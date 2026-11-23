// Water through doors (map WATER, tools/map_water.py; the pieces a map puts:
// tools/ajarwater.py; PLAN.md, "The water lab"). The tests: watertest.zs.
//
// The rule: water stands level on both sides of a hung door, measured from
// the door's sill. A room that can hold water is a basin (AjarBasin): a group
// of sectors with one tag and one water surface at the absolute height w,
// dry while w is at its floor. The surface is a swimmable 3D floor
// (Sector_Set3DFloor type 2) whose control sector's ceiling the handler
// moves each tic (Sector.MoveCeiling). Two kinds of basin keep their level:
// the RESERVOIR (always `depth` over its floor) and the OUTFALL (always dry).
//
// Each tic, every hung door links the basin of its frame with that of its
// far side (a Pair's two leaves, the basins of their two frames): with the
// heads hA = wA - sA and hB = wB - sB over the two sills, a volume
// q = K (hA - hB) goes from A to B (K FREE times that when B is dry at its
// sill: the water falls out freely); never so much that the heads cross,
// that A goes below its sill or B over its brim. All of a tic's flows are
// reckoned from the same levels and made together (the order of the doors
// does not matter). A weir (AjarWeir) is a
// fixed one-way overflow from basin U into basin L over a crest c:
// q = K_WEIR (wU - c). Its paddle wheel turns with the flow; once the flow
// has stayed over WHEEL_FLOW for 3 seconds the wheel counts as turning: its
// lamp is lit and its shutter held open, until the flow falls under it again
// (the shutter shuts SHUT_AFTER later).
//
// The drowning rule (bDrown, on in the lab): a walking monster whose head
// has been under water (the engine's waterlevel 3) for 3 seconds takes
// DROWN_DAMAGE each second until it is dead. Flying monsters are not hurt.
//
// The handler is named in map WATER's MAPINFO only; on a map with no basin
// it does nothing.

class AjarBasin : Actor
{
	// args: the basins' sector tag, plan area, brim, kind (0 normal, 1 reservoir, 2 outfall), depth
	const DRY = 32;            // a dry basin's surface is put this far under its floor
	double w;                  // the water surface, absolute
	double floorZ;             // the basin's lowest floor
	double area, brim;
	Sector ctl;                // the 3D floor's control sector: its ceiling is the surface
	double shown;              // where the surface was put last
	double inflow;             // this tic's net volume in (tests, HUD)

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE +NOINTERACTION
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	bool held;                 // kept where it is for a while (the tests' views)

	int Tag() { return args[0]; }
	bool Fixed() { return args[3] != 0 || held; }
	bool Reservoir() { return args[3] == 1; }
	double Depth() { return max(w - floorZ, 0); }
	bool Wet() { return w > floorZ + 0.5; }
	double Volume() { return Depth() * area; }
}

// A fixed overflow, drawn as its paddle wheel (args: upper basin's tag, lower
// basin's tag, crest height, chute's sector tag, lamp tag * 65536 + shutter tag).
class AjarWeir : Actor
{
	AjarBasin up, low;
	double flow;               // this tic's spill, upper to lower (volume a tic; never negative over a weir)
	double over;               // how far the upper surface stands over the crest
	int overTics;              // tics the flow has stayed over WHEEL_FLOW
	bool turning;
	int stoppedAt;             // the level's tic the wheel stopped turning (-1: never turned)
	double spin;               // the wheel's turn, degrees a tic
	Array<int> chute;          // the chute's sectors, by index
	Array<string> chuteDry;    // ... and their own floors
	double scroll;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +NOINTERACTION +WALLSPRITE +ROLLSPRITE +ROLLCENTER
		Radius 32;
		Height 64;
		RenderStyle "Normal";
	}
	States
	{
	Spawn:
		AJWH A -1;
		Stop;
	}

	double Crest() { return args[2]; }
	int LampTag() { return args[4] >> 16; }
	int ShutterTag() { return args[4] & 0xFFFF; }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		angle = 90;                         // the wheel faces up and down the chute (seen from the pool below)
		SetZ(Crest() - 56);
		stoppedAt = -1;
	}

	override void Tick()
	{
		Super.Tick();
		roll += spin;
	}
}

// A raft (thing 20142): floats with its middle at the surface while the water
// under it is half its height deep or more, is carried towards the door the
// most water leaves its basin by, and can be stood on (things stand on it).
class AjarRaft : Actor
{
	const MAXSPEED = 2.;       // units a tic
	const DRIFT = 0.25;        // its speed, per unit of (outflow / (64 x depth))
	bool afloat;
	Vector2 current;
	int riders;                // tics someone stood on it (the tests)
	Default
	{
		Radius 24;
		Height 8;
		Mass 400;
		+SOLID +ACTLIKEBRIDGE +FLATSPRITE +NOBLOOD +DONTTHRUST +NOTAUTOAIMED +CANPASS
		Scale 1.5;
	}
	States
	{
	Spawn:
		AJB0 A -1;
		Stop;
	}
}

class AjarWaterHandler : EventHandler
{
	const K = 2048.;           // volume a tic, per unit of head difference, through a hung door
	const FREE = 8.;           // ... this many times that into a basin dry at its sill (or the outfall)
	const K_WEIR = 2048.;      // a weir's, per unit over its crest
	const WHEEL_FLOW = 4096.;  // the flow a wheel needs to count as turning (2 units over the crest)
	const WHEEL_TICS = 105;    // ... for this long
	const SHUT_AFTER = 105;    // a shutter shuts this long after its wheel stopped
	const SHUTTER_UP = 96;     // how far a shutter goes up
	const DROWN_AFTER = 105;
	const DROWN_DAMAGE = 20;
	const BULKHEAD = 9000;     // the dry side of a bulkhead into basin tag t: line id BULKHEAD + t (ajarwater.bulkhead)
	const CTL = 6000;          // basin tag t's control sector: tag CTL + t

	bool ready, any;
	bool bDrown;               // the drowning rule (PLAN.md, "The water lab", E)
	Array<AjarBasin> basins;
	Array<int> basinOf;        // a sector's index -> 1 + its basin's index (0: in none)
	Array<AjarWeir> weirs;
	Array<AjarFrame> frames;
	Array<int> bulkheads;      // lines, by index
	Array<int> bulkheadTag;
	AjarHandler h;
	// this tic's links (the tests read them): the two basins, their sills, the flow A -> B
	Array<AjarBasin> linkA, linkB;
	Array<double> linkSA, linkSB, linkQ;
	Array<int> linkFrame;      // the frame's line id of the door that made it
	Array<int> linkLA, linkLB; // the two portal lines, by index
	// the drowning rule's count, by monster
	Array<Actor> under;
	Array<int> underTics;

	static AjarWaterHandler Get() { return AjarWaterHandler(EventHandler.Find("AjarWaterHandler")); }

	AjarBasin BasinOfTag(int tag)
	{
		for (int i = 0; i < basins.Size(); i++) if (basins[i].Tag() == tag) return basins[i];
		return null;
	}

	AjarBasin BasinOfSector(Sector s)
	{
		if (!s) return null;
		int i = basinOf[s.Index()];
		return i ? basins[i - 1] : null;
	}

	AjarBasin BasinAtLine(Line l)
	{
		if (!l) return null;
		let b = BasinOfSector(l.frontsector);
		return b ? b : BasinOfSector(l.backsector);
	}

	AjarBasin BasinAt(Vector2 p) { return BasinOfSector(level.PointInSector(p)); }

	static double Sill(Line l)
	{
		Vector2 mid = (l.v1.p + l.v2.p) / 2;
		return l.frontsector.floorplane.ZatPoint(mid);
	}

	void Setup()
	{
		ready = true;
		bDrown = true;
		h = AjarHandler(EventHandler.Find("AjarHandler"));
		basinOf.Resize(level.sectors.Size());
		for (int i = 0; i < basinOf.Size(); i++) basinOf[i] = 0;
		let it = ThinkerIterator.Create("AjarBasin");
		AjarBasin b;
		while (b = AjarBasin(it.Next()))
		{
			let ci = level.CreateSectorTagIterator(CTL + b.Tag());
			int c = ci.Next();
			if (c < 0) { Console.Printf("AjarBasin %d: no control sector %d", b.Tag(), CTL + b.Tag()); continue; }
			b.ctl = level.sectors[c];
			basins.Push(b);
			b.floorZ = 1e9;
			let si = level.CreateSectorTagIterator(b.Tag());
			int s;
			while ((s = si.Next()) >= 0)
			{
				basinOf[s] = basins.Size();
				b.floorZ = min(b.floorZ, level.sectors[s].floorplane.ZatPoint(level.sectors[s].centerspot));
			}
			b.area = b.args[1];
			b.brim = b.args[2];
			if (b.args[3] == 2) b.w = b.floorZ - AjarBasin.DRY;
			else b.w = clamp(b.floorZ + b.args[4], b.floorZ, b.brim);
			b.shown = 1e9;
			Show(b);
			let li = level.CreateLineIdIterator(BULKHEAD + b.Tag());
			int l;
			while ((l = li.Next()) >= 0) { bulkheads.Push(l); bulkheadTag.Push(b.Tag()); }
		}
		any = basins.Size() > 0;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next())) frames.Push(f);
		let wi = ThinkerIterator.Create("AjarWeir");
		AjarWeir wr;
		while (wr = AjarWeir(wi.Next()))
		{
			wr.up = BasinOfTag(wr.args[0]);
			wr.low = BasinOfTag(wr.args[1]);
			let ci = level.CreateSectorTagIterator(wr.args[3]);
			int s;
			while ((s = ci.Next()) >= 0) { wr.chute.Push(s); wr.chuteDry.Push(TexMan.GetName(level.sectors[s].GetTexture(Sector.floor))); }
			weirs.Push(wr);
		}
	}

	// --- the water -------------------------------------------------------------------------
	// The flow between a (sill sa) and b (sill sb) by the rule, from this tic's levels: a -> b.
	// Every flow of a tic is reckoned from the same levels and then all are made at once, so
	// that what comes out does not depend on the order of the doors.
	double Flow(AjarBasin a, double sa, AjarBasin b, double sb)
	{
		double sign = 1;
		double ha = a.w - sa, hb = b.w - sb;
		if (ha < hb)
		{
			AjarBasin t = a; a = b; b = t;
			double s = sa; sa = sb; sb = s;
			s = ha; ha = hb; hb = s;
			sign = -1;
		}
		if (ha <= 0) return 0;                          // nothing over the higher sill
		double q = (hb <= 0 ? K * FREE : K) * (ha - max(hb, 0));
		double ia = a.Fixed() ? 0 : 1 / a.area, ib = b.Fixed() ? 0 : 1 / b.area;
		if (ia + ib > 0) q = min(q, (ha - hb) / (ia + ib));     // never past level
		if (!a.Fixed()) q = min(q, ha * a.area);                // a never under its sill by this door
		if (!b.Fixed()) q = min(q, (b.brim - b.w) * b.area);    // b never over its brim
		q = max(q, 0);
		return q * sign;
	}

	// q from a to b (negative: b to a)
	void Move(AjarBasin a, AjarBasin b, double q)
	{
		if (!a.Fixed()) a.w = clamp(a.w - q / a.area, a.floorZ, a.brim);
		if (!b.Fixed()) b.w = clamp(b.w + q / b.area, b.floorZ, b.brim);
		a.inflow -= q;
		b.inflow += q;
	}

	void Apply()
	{
		for (int i = 0; i < linkQ.Size(); i++) Move(linkA[i], linkB[i], linkQ[i]);
		for (int i = 0; i < weirs.Size(); i++) if (weirs[i].up && weirs[i].low) Move(weirs[i].up, weirs[i].low, weirs[i].flow);
	}

	void Links()
	{
		linkA.Clear(); linkB.Clear(); linkSA.Clear(); linkSB.Clear(); linkQ.Clear(); linkFrame.Clear(); linkLA.Clear(); linkLB.Clear();
		for (int i = 0; i < frames.Size(); i++)
		{
			let f = frames[i];
			if (!f || !f.door) continue;
			let d = f.door;
			int far = d.args[0];
			if (!far) continue;                                  // a Pair's leaf hung alone: a shut door
			if (d.IsPair() && f.args[0] > far) continue;         // a Pair: once, from the leaf in the lower-numbered frame
			Line la = h.FindLine(f.args[0]), lb = h.FindLine(far);
			AjarBasin a = BasinAtLine(la), b = BasinAtLine(lb);
			if (!a || !b || a == b) continue;
			double sa = Sill(la), sb = Sill(lb);
			double q = Flow(a, sa, b, sb);
			linkA.Push(a); linkB.Push(b); linkSA.Push(sa); linkSB.Push(sb); linkQ.Push(q); linkFrame.Push(f.args[0]);
			linkLA.Push(la.Index()); linkLB.Push(lb.Index());
		}
	}

	void Spills()
	{
		for (int i = 0; i < weirs.Size(); i++)
		{
			let wr = weirs[i];
			if (!wr.up || !wr.low) continue;
			wr.over = wr.up.w - wr.Crest();
			double q = wr.over > 0 ? K_WEIR * wr.over : 0;
			if (!wr.up.Fixed()) q = min(q, max(wr.over, 0) * wr.up.area);
			if (!wr.low.Fixed()) q = min(q, (wr.low.brim - wr.low.w) * wr.low.area);
			wr.flow = max(q, 0);
		}
	}

	void Wheel(AjarWeir wr)
	{
		wr.spin = min(wr.flow / 1024., 12);                     // degrees a tic: a quarter of a unit over the crest is 0.5
		if (wr.flow > WHEEL_FLOW) wr.overTics++;
		else wr.overTics = 0;
		bool was = wr.turning;
		wr.turning = wr.overTics >= WHEEL_TICS;
		if (was && !wr.turning) wr.stoppedAt = level.maptime;
		// the lamp
		let li = level.CreateSectorTagIterator(wr.LampTag());
		int s;
		while ((s = li.Next()) >= 0) level.sectors[s].SetLightLevel(wr.turning ? 255 : 96);
		if (wr.turning && !was) wr.A_AttachLight('wheel', DynamicLight.PointLight, 0xFFE070, 160, 160);
		if (was && !wr.turning) wr.A_RemoveLight('wheel');
		// the shutter: up while it turns, down SHUT_AFTER after it stopped
		bool open = wr.turning || (wr.stoppedAt >= 0 && level.maptime - wr.stoppedAt < SHUT_AFTER);
		let si = level.CreateSectorTagIterator(wr.ShutterTag());
		while ((s = si.Next()) >= 0)
		{
			Sector sec = level.sectors[s];
			double fz = sec.floorplane.ZatPoint(sec.centerspot), cz = sec.ceilingplane.ZatPoint(sec.centerspot);
			double want = open ? fz + SHUTTER_UP : fz;
			if (abs(cz - want) > 0.01) sec.MoveCeiling(4, want, -1, want > cz ? 1 : -1, false);
		}
		// the chute: wet and running while water goes down it
		wr.scroll += min(wr.flow / 2048., 8);
		TextureID wet = TexMan.CheckForTexture("FWATER1", TexMan.Type_Any);
		for (int i = 0; i < wr.chute.Size(); i++)
		{
			Sector sec = level.sectors[wr.chute[i]];
			sec.SetTexture(Sector.floor, wr.flow > 256 ? wet : TexMan.CheckForTexture(wr.chuteDry[i], TexMan.Type_Any));
			sec.SetYOffset(Sector.floor, wr.scroll);
		}
	}

	// the surface where the basin's water is (under its floor when dry)
	void Show(AjarBasin b)
	{
		double z = b.Wet() ? b.w : b.floorZ - AjarBasin.DRY;
		if (abs(z - b.shown) < 0.001) return;
		double now = b.ctl.ceilingplane.ZatPoint(b.ctl.centerspot);
		if (abs(z - now) > 0.001) b.ctl.MoveCeiling(abs(z - now) + 1, z, -1, z > now ? 1 : -1, false);
		b.shown = z;
	}

	// --- drowning (a rule to try) ----------------------------------------------------------
	void Drowning()
	{
		if (!bDrown) return;
		for (int i = under.Size() - 1; i >= 0; i--)
			if (!under[i] || under[i].health <= 0) { under.Delete(i); underTics.Delete(i); }
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || a.bNoGravity || a.bFloat) continue;
			int i = under.Find(a);
			if (a.waterlevel < 3)
			{
				if (i < under.Size()) underTics[i] = 0;
				continue;
			}
			if (i == under.Size()) { under.Push(a); underTics.Push(0); }
			int t = ++underTics[i];
			if (t >= DROWN_AFTER && (t - DROWN_AFTER) % 35 == 0) a.DamageMobj(null, null, DROWN_DAMAGE, 'Drowning');
		}
	}

	// --- rafts: on the surface, carried towards the door the water leaves by ----------------------
	void Rafts()
	{
		let it = ThinkerIterator.Create("AjarRaft");
		AjarRaft r;
		while (r = AjarRaft(it.Next())) Raft(r);
	}

	void Raft(AjarRaft r)
	{
		let b = BasinAt(r.pos.xy);
		Vector3 was = r.pos;
		r.afloat = b && b.Wet() && b.w - r.floorz >= r.height / 2;
		r.bNoGravity = r.afloat;
		r.current = (0, 0);
		if (!r.afloat) return;
		r.SetZ(b.w - r.height / 2);
		r.vel.z = 0;
		// the strongest outflow of this basin pulls it towards its door, the faster the more water goes
		double best = 0;
		for (int i = 0; i < linkQ.Size(); i++)
		{
			double leaving = linkA[i] == b ? linkQ[i] : linkB[i] == b ? -linkQ[i] : 0;
			if (leaving <= best) continue;
			best = leaving;
			Line l = level.lines[linkA[i] == b ? linkLA[i] : linkLB[i]];
			Vector2 to = (l.v1.p + l.v2.p) / 2 - r.pos.xy;
			// near the door: straight through it (out of the line's front, into the portal)
			if (to.Length() < r.radius + 16) to = (-l.delta.y, l.delta.x);
			r.current = to.Unit() * min(AjarRaft.MAXSPEED, leaving / (64 * max(b.Depth(), 8)) * AjarRaft.DRIFT);
		}
		r.vel.xy = r.current;
		// whoever stands on it goes with it
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			let mo = players[i].mo;
			if (!playeringame[i] || !mo) continue;
			if (abs(mo.pos.z - (r.pos.z + r.height)) > 2 || (mo.pos.xy - r.pos.xy).Length() > r.radius + mo.radius) continue;
			mo.vel.xy = r.current;
			r.riders++;
		}
	}

	int UnderFor(Actor a)
	{
		int i = under.Find(a);
		return i < under.Size() ? underTics[i] : 0;
	}

	// --- events ----------------------------------------------------------------------------
	override void WorldTick()
	{
		if (!ready) Setup();
		if (!any) return;
		for (int i = 0; i < basins.Size(); i++) basins[i].inflow = 0;
		Links();
		Spills();
		Apply();
		for (int i = 0; i < weirs.Size(); i++) Wheel(weirs[i]);
		for (int i = 0; i < basins.Size(); i++) Show(basins[i]);
		Drowning();
		Rafts();
	}

	// A bulkhead will not open from the dry side while water stands behind it.
	override void WorldLinePreActivated(WorldEvent e)
	{
		if (!any || !e.ActivatedLine) return;
		int i = bulkheads.Find(e.ActivatedLine.Index());
		if (i == bulkheads.Size()) return;
		let b = BasinOfTag(bulkheadTag[i]);
		if (!b || !b.Wet()) return;
		e.ShouldActivate = false;
		if (h) h.Say("Water stands behind this bulkhead.\nIt will not open from the dry side.");
	}
}
