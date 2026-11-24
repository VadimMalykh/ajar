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
// The handler is named in the MAPINFO of map WATER and of MAP20 ("High
// Water", tools/map_highwater.py); on a map with no basin it does nothing.
//
// A level may set its own rate and rules (AjarWaterRate, thing 20143; the
// lab has none and keeps the constants below): K and FREE, the weir's K (the
// level's K) and the wheel's time; FLOAT, the player floats up when idle
// under water; OVERFLOW, a basin at its brim spills what more comes in (to
// the outfall: it is gone), so that no door's or weir's flow is held back by
// a full basin. MAP20 also has pressure doors (AjarPressureDoor), a float
// that raises a gate (AjarFloatGate), ambushes brought by water (AjarAmbush
// causes 60 and 61, WaterDue) and the water's sounds (tools/sfx.py).
//
// A FOLLOW basin (kind 3, args[4] the tag of the basin it follows) has no
// links and no water of its own: its surface is put where the other's is,
// every tic, after the flows (MAP20's left-handed bath, behind the opening
// in the swimming bath's panes: PLAN.md, "MAP20: the secret way out").
//
// In a level (a map with an AjarWaterRate: MAP20; not the lab) the handler also puts a buoy (AjarBuoy)
// in every NORMAL basin that no FOLLOW basin follows (so none in MAP20's swimming bath, where nothing may
// move by itself, and none in the reservoir or the outfall), at the basin thing's own spot: it rides the
// surface, a third of it under, and rests on the floor when the basin is dry. Scenery only. A weir's
// fountain: the sectors tagged FOUNTAIN + the weir's chute tag (MAP20's lower yard) are dry at rest and
// show water, with a jet in their middle (AjarFountainJet), while the weir's wheel counts as turning.
// The wheel is drawn 128 across (AJWH); the lab shows it at half that, a level as large as its chute lets
// it be, up to WHEEL_MAX (PLAN.md, "MAP20: buoys, the fountain, a bigger wheel").

class AjarBasin : Actor
{
	// args: the basins' sector tag, plan area, brim, kind (0 normal, 1 reservoir, 2 outfall, 3 follow), depth
	// (follow: the tag of the basin it follows)
	const DRY = 32;            // a dry basin's surface is put this far under its floor
	double w;                  // the water surface, absolute
	double floorZ;             // the basin's lowest floor
	double area, brim;
	Sector ctl;                // the 3D floor's control sector: its ceiling is the surface
	double shown;              // where the surface was put last
	double inflow;             // this tic's net volume in (tests, HUD)
	AjarBasin follow;          // FOLLOW: the basin whose level it keeps

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
	bool Follows() { return args[3] == 3; }
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
	Array<int> fountain;       // the fountain's sectors (tag FOUNTAIN + the chute's tag), by index
	Array<string> fountainDry; // ... and their own floors
	Vector3 fountainAt;        // the middle of the fountain, on its floor
	AjarFountainJet jet;       // there while the wheel turns

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +NOINTERACTION +WALLSPRITE +ROLLSPRITE +ROLLCENTER
		Radius 32;
		Height 64;
		RenderStyle "Normal";
		Scale 0.5;             // the sprite is 128 across: the lab's wheel stays 64 (a level's: AjarWaterHandler.WheelSize)
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

// A buoy (a level's: put by the handler, never by the map): a red-and-white ball at its basin thing's
// spot, standing on the surface with DRAFT of it under while there is that much water there, on the
// floor otherwise. Scenery: not solid, not shootable, not in the blockmap, counts as nothing.
class AjarBuoy : Actor
{
	const DRAFT = 8;           // a third of its 24 under water
	AjarBasin basin;
	double floorAt;            // the floor at its spot
	double phase;              // its rocking, so that no two rock together

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +NOINTERACTION +ROLLSPRITE +ROLLCENTER +DONTSPLASH
		Radius 12;
		Height 24;
		RenderStyle "Normal";
	}
	States
	{
	Spawn:
		AJBY A -1;
		Stop;
	}

	bool Afloat() { return basin && basin.Wet() && basin.w - DRAFT > floorAt; }
	double Want() { return Afloat() ? basin.w - DRAFT : floorAt; }

	void Ride()
	{
		SetOrigin((pos.xy, Want()), true);
		roll = Afloat() ? 4 * sin(level.maptime * 3.1 + phase) : 0;
	}
}

// A fountain's jet (the handler's, while its weir's wheel turns): a sprite about 96 high, spray falling
// back into the bowl as particles, and the sound of running water. Nothing solid.
class AjarFountainJet : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH
		Radius 16;
		Height 96;
		RenderStyle "Translucent";
		Alpha 0.9;
	}
	States
	{
	Spawn:
		AJFJ ABCD 3;
		Loop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		A_StartSound("ajar/water", CHAN_BODY, CHANF_LOOPING, 0.8, ATTN_NORM);
	}

	override void Tick()
	{
		Super.Tick();
		for (int i = 0; i < 4; i++)
		{
			double a = frandom(0, 360), v = frandom(1.2, 2.6);
			A_SpawnParticle(0xE0F0F8, 0, 30, frandom(2, 4), 0, 0, 0, frandom(78, 90), v * cos(a), v * sin(a),
				frandom(0.2, 1.6), 0, 0, -0.25, 0.8, 0.02);
		}
	}

	override void OnDestroy()
	{
		A_StopSound(CHAN_BODY);
		Super.OnDestroy();
	}
}

// A level's own rate of flow and rules (args: K, FREE, flags 1 FLOAT 2 OVERFLOW, wheel tics; 0: the lab's).
class AjarWaterRate : Actor
{
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
}

// A door that water holds (ajarwater.pressure_door; args: the door's sector tag, the basin tags on its
// two sides (0: dry ground), its lamps' sector tag, flags: 1 it opens by itself when the basin args[1]
// is first dry). It opens by USE only while the water at its sill is under HOLD on both sides, and
// shuts itself (never on anyone) when the water comes to HOLD. Its lamps are red while water holds it.
class AjarPressureDoor : Actor
{
	const HOLD = 16;
	const SPEED = 4;
	const UP = 88;             // how far it opens
	Sector door;
	Array<int> lamps;
	Array<int> uses;           // its two door lines, by index
	AjarBasin side[2];
	double sill;
	bool open;                 // wanted open
	bool autoDone;
	bool held;
	int shutWaits;             // tics it has waited to shut on someone (the tests)
	int refused;               // USEs refused (the tests)

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

	double Top() { return door.ceilingplane.ZatPoint(door.centerspot); }
	bool IsOpen() { return Top() > sill + 56; }
	bool IsShut() { return Top() <= sill + 0.01; }
	double WaterAt(int i) { return side[i] ? max(side[i].w - sill, 0) : 0; }
}

// A float in a basin (args: the basin's tag, the mark, the gate's sector tag, seconds): once the water
// has stood at the mark or over for that long, it raises the gate for good.
class AjarFloatGate : Actor
{
	AjarBasin b;
	int over;
	bool tripped;
	int trippedAt;
	Array<int> gate;

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
	const FLOAT_UP = 64. / 35; // the player rises this much a tic when he floats (FLOAT)
	const SOUND_SLOT = 7;      // the channel a frame's running water and a wheel's turning play on
	const FOUNTAIN = 7000;     // a weir's fountain: the sectors tagged FOUNTAIN + its chute's tag (ajarwater.FOUNTAIN)
	const WHEEL_MAX = 160;     // a level's wheel is drawn this wide, or as wide as its chute lets it be, less WHEEL_ROOM
	const WHEEL_ROOM = 6;
	const WHEEL_PX = 127;      // the sprite's paddles' tips, from one to the other (AJWH, 128 px)

	// the level's rate and rules: the constants above, unless an AjarWaterRate says otherwise
	double kFlow, freeFall, kWeir, wheelFlow;
	int wheelTics;
	bool bFloat, bOverflow;
	bool bLevel;               // a level's (an AjarWaterRate is there): buoys, a fountain, the wheel as large as fits
	Array<AjarBuoy> buoys;
	Array<AjarPressureDoor> pdoors;
	Array<AjarFloatGate> floats;
	Array<int> lastWater;      // by player: his waterlevel last tic (the splash)
	bool saidSwim;
	int floatTics;             // tics the player has been floated up (the tests)
	int keysUntil;             // a test's script holds keys down until this tic: he is not idle (map20.zs)
	Array<int> dueKeys;        // WaterDue's causes once met: cause * 65536 + args[4]
	Array<AjarFrame> linkF;    // this tic's links: the frame whose door made it (its sound)

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
		kFlow = K; freeFall = FREE; kWeir = K_WEIR; wheelFlow = WHEEL_FLOW; wheelTics = WHEEL_TICS;
		let ri = ThinkerIterator.Create("AjarWaterRate");
		let rate = AjarWaterRate(ri.Next());
		bLevel = rate != null;
		if (rate)
		{
			if (rate.args[0]) { kFlow = rate.args[0]; kWeir = kFlow; wheelFlow = 2 * kWeir; }
			if (rate.args[1]) freeFall = rate.args[1];
			bFloat = rate.args[2] & 1;
			bOverflow = rate.args[2] & 2;
			if (rate.args[3]) wheelTics = rate.args[3];
		}
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
			else if (b.Follows()) b.w = b.floorZ;
			else b.w = clamp(b.floorZ + b.args[4], b.floorZ, b.brim);
			b.shown = 1e9;
			Show(b);
			let li = level.CreateLineIdIterator(BULKHEAD + b.Tag());
			int l;
			while ((l = li.Next()) >= 0) { bulkheads.Push(l); bulkheadTag.Push(b.Tag()); }
		}
		any = basins.Size() > 0;
		for (int i = 0; i < basins.Size(); i++) if (basins[i].Follows()) basins[i].follow = BasinOfTag(basins[i].args[4]);
		Follow();
		for (int i = 0; i < basins.Size(); i++) Show(basins[i]);
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
			if (bLevel) WheelSize(wr);
			SetupFountain(wr);
			weirs.Push(wr);
		}
		if (bLevel) PutBuoys();
		let pi = ThinkerIterator.Create("AjarPressureDoor");
		AjarPressureDoor pd;
		while (pd = AjarPressureDoor(pi.Next())) SetupPressureDoor(pd);
		let gi = ThinkerIterator.Create("AjarFloatGate");
		AjarFloatGate fg;
		while (fg = AjarFloatGate(gi.Next()))
		{
			fg.b = BasinOfTag(fg.args[0]);
			let si = level.CreateSectorTagIterator(fg.args[2]);
			int s;
			while ((s = si.Next()) >= 0) fg.gate.Push(s);
			floats.Push(fg);
		}
	}

	void SetupPressureDoor(AjarPressureDoor pd)
	{
		let si = level.CreateSectorTagIterator(pd.args[0]);
		int s = si.Next();
		if (s < 0) { Console.Printf("AjarPressureDoor: no sector %d", pd.args[0]); return; }
		pd.door = level.sectors[s];
		pd.sill = pd.door.floorplane.ZatPoint(pd.door.centerspot);
		for (int i = 0; i < pd.door.lines.Size(); i++)
			if (pd.door.lines[i].special == 11) pd.uses.Push(pd.door.lines[i].Index());
		let li = level.CreateSectorTagIterator(pd.args[3]);
		while ((s = li.Next()) >= 0) pd.lamps.Push(s);
		pd.side[0] = BasinOfTag(pd.args[1]);
		pd.side[1] = BasinOfTag(pd.args[2]);
		pdoors.Push(pd);
	}

	// A level's wheel: WHEEL_MAX across, or less if its chute (across the wheel's plane) is narrower.
	// The paddles reach every way as it turns, so the chute's width bounds it whatever its height.
	void WheelSize(AjarWeir wr)
	{
		Vector2 along = (cos(wr.angle + 90), sin(wr.angle + 90));
		double lo = 1e9, hi = -1e9;
		for (int i = 0; i < wr.chute.Size(); i++)
		{
			Sector sec = level.sectors[wr.chute[i]];
			for (int j = 0; j < sec.lines.Size(); j++)
			{
				Line l = sec.lines[j];
				for (int e = 0; e < 2; e++)
				{
					double d = ((e ? l.v2.p : l.v1.p) - wr.pos.xy) dot along;
					lo = min(lo, d); hi = max(hi, d);
				}
			}
		}
		double room = wr.chute.Size() ? 2 * min(-lo, hi) - WHEEL_ROOM : WHEEL_MAX;
		double across = clamp(room, 32, WHEEL_MAX);
		wr.scale = (across / WHEEL_PX, across / WHEEL_PX);
	}

	// A weir's fountain: its sectors, their dry floors, its middle
	void SetupFountain(AjarWeir wr)
	{
		let fi = level.CreateSectorTagIterator(FOUNTAIN + wr.args[3]);
		int s;
		Vector2 lo = (1e9, 1e9), hi = (-1e9, -1e9);
		while ((s = fi.Next()) >= 0)
		{
			Sector sec = level.sectors[s];
			wr.fountain.Push(s);
			wr.fountainDry.Push(TexMan.GetName(sec.GetTexture(Sector.floor)));
			for (int j = 0; j < sec.lines.Size(); j++)
			{
				Line l = sec.lines[j];
				for (int e = 0; e < 2; e++)
				{
					Vector2 p = e ? l.v2.p : l.v1.p;
					lo = (min(lo.x, p.x), min(lo.y, p.y));
					hi = (max(hi.x, p.x), max(hi.y, p.y));
				}
			}
		}
		if (!wr.fountain.Size()) return;
		Vector2 mid = (lo + hi) / 2;
		wr.fountainAt = (mid, level.PointInSector(mid).floorplane.ZatPoint(mid));
	}

	// the fountain plays while the wheel turns: water on its floor, the jet in its middle
	void PlayFountain(AjarWeir wr)
	{
		if (!wr.fountain.Size()) return;
		TextureID wet = TexMan.CheckForTexture("FWATER1", TexMan.Type_Any);
		for (int i = 0; i < wr.fountain.Size(); i++)
			level.sectors[wr.fountain[i]].SetTexture(Sector.floor, wr.turning ? wet : TexMan.CheckForTexture(wr.fountainDry[i], TexMan.Type_Any));
		if (wr.turning && !wr.jet) wr.jet = AjarFountainJet(Actor.Spawn("AjarFountainJet", wr.fountainAt));
		else if (!wr.turning && wr.jet) { wr.jet.Destroy(); wr.jet = null; }
	}

	// a buoy in every NORMAL basin that no FOLLOW basin follows, at the basin thing's spot
	void PutBuoys()
	{
		for (int i = 0; i < basins.Size(); i++)
		{
			let b = basins[i];
			if (b.args[3] != 0) continue;
			bool followed = false;
			for (int j = 0; j < basins.Size(); j++) if (basins[j].Follows() && basins[j].follow == b) followed = true;
			if (followed) continue;
			let by = AjarBuoy(Actor.Spawn("AjarBuoy", (b.pos.xy, 0)));
			by.basin = b;
			by.floorAt = level.PointInSector(b.pos.xy).floorplane.ZatPoint(b.pos.xy);
			by.phase = 97 * buoys.Size();
			by.SetOrigin((b.pos.xy, by.Want()), false);
			buoys.Push(by);
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
		double q = (hb <= 0 ? kFlow * freeFall : kFlow) * (ha - max(hb, 0));
		double ia = a.Fixed() ? 0 : 1 / a.area, ib = b.Fixed() ? 0 : 1 / b.area;
		if (ia + ib > 0) q = min(q, (ha - hb) / (ia + ib));     // never past level
		if (!a.Fixed()) q = min(q, ha * a.area);                // a never under its sill by this door
		if (!b.Fixed() && !bOverflow) q = min(q, (b.brim - b.w) * b.area);    // b never over its brim (OVERFLOW: it spills)
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

	// FOLLOW basins: at the level of the basin each follows (after this tic's flows)
	void Follow()
	{
		for (int i = 0; i < basins.Size(); i++)
		{
			let b = basins[i];
			if (b.Follows() && b.follow) b.w = b.follow.w;
		}
	}

	void Links()
	{
		linkA.Clear(); linkB.Clear(); linkSA.Clear(); linkSB.Clear(); linkQ.Clear(); linkFrame.Clear(); linkLA.Clear(); linkLB.Clear();
		linkF.Clear();
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
			linkF.Push(f);
		}
	}

	void Spills()
	{
		for (int i = 0; i < weirs.Size(); i++)
		{
			let wr = weirs[i];
			if (!wr.up || !wr.low) continue;
			wr.over = wr.up.w - wr.Crest();
			double q = wr.over > 0 ? kWeir * wr.over : 0;
			if (!wr.up.Fixed()) q = min(q, max(wr.over, 0) * wr.up.area);
			if (!wr.low.Fixed() && !bOverflow) q = min(q, (wr.low.brim - wr.low.w) * wr.low.area);
			wr.flow = max(q, 0);
		}
	}

	void Wheel(AjarWeir wr)
	{
		wr.spin = min(wr.flow / 1024., 12);                     // degrees a tic: a quarter of a unit over the crest is 0.5
		if (wr.flow > wheelFlow) wr.overTics++;
		else wr.overTics = 0;
		bool was = wr.turning;
		wr.turning = wr.overTics >= wheelTics;
		if (wr.spin > 0.05 && !wr.IsActorPlayingSound(SOUND_SLOT))
			wr.A_StartSound("ajar/wheel", SOUND_SLOT, CHANF_LOOPING, 0.2, ATTN_NORM);
		if (wr.spin > 0.05) wr.A_SoundVolume(SOUND_SLOT, clamp(wr.spin / 6, 0.2, 1));
		else if (wr.IsActorPlayingSound(SOUND_SLOT)) wr.A_StopSound(SOUND_SLOT);
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
		PlayFountain(wr);
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
		Follow();
		for (int i = 0; i < weirs.Size(); i++) Wheel(weirs[i]);
		for (int i = 0; i < basins.Size(); i++) Show(basins[i]);
		for (int i = 0; i < buoys.Size(); i++) if (buoys[i]) buoys[i].Ride();
		Drowning();
		Rafts();
		Running();
		for (int i = 0; i < pdoors.Size(); i++) PressureDoor(pdoors[i]);
		for (int i = 0; i < floats.Size(); i++) FloatGate(floats[i]);
		Players();
	}

	// --- MAP20: the sounds of water ----------------------------------------------------------
	// Water running at a door that passes any, louder the more goes; quiet at the others.
	void Running()
	{
		for (int i = 0; i < frames.Size(); i++)
		{
			let f = frames[i];
			if (!f) continue;
			int j = linkF.Find(f);
			double q = j < linkF.Size() ? abs(linkQ[j]) : 0;
			if (q > 32)
			{
				double v = clamp(sqrt(q / (kFlow * 64)), 0.15, 1);
				if (!f.IsActorPlayingSound(SOUND_SLOT)) f.A_StartSound("ajar/water", SOUND_SLOT, CHANF_LOOPING, v, ATTN_NORM);
				else f.A_SoundVolume(SOUND_SLOT, v);
			}
			else if (f.IsActorPlayingSound(SOUND_SLOT)) f.A_StopSound(SOUND_SLOT);
		}
	}

	// --- MAP20: the player in the water: a splash going in and out; FLOAT -------------------------
	static bool Idle(PlayerInfo p)
	{
		let c = p.cmd;
		return !c.forwardmove && !c.sidemove && !c.upmove && !(c.buttons & (BT_JUMP | BT_CROUCH));
	}

	void Players()
	{
		lastWater.Resize(MAXPLAYERS);
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo) continue;
			let mo = players[i].mo;
			int wl = mo.waterlevel;
			if ((wl > 0) != (lastWater[i] > 0) && level.maptime > 2)
				mo.A_StartSound("ajar/splash", CHAN_BODY, CHANF_OVERLAP, wl > 0 ? 1 : 0.6);
			lastWater[i] = wl;
			if (!bFloat || wl < 3 || mo.health <= 0) continue;
			if (!saidSwim && h) { h.Say("Swim up: look up and walk, or the jump key."); saidSwim = true; }
			if (!Idle(players[i]) || level.maptime <= keysUntil) continue;
			mo.vel.z = max(mo.vel.z, FLOAT_UP);
			floatTics++;
		}
	}

	// --- MAP20: pressure doors ------------------------------------------------------------------
	bool Held(AjarPressureDoor pd) { return pd.WaterAt(0) >= AjarPressureDoor.HOLD || pd.WaterAt(1) >= AjarPressureDoor.HOLD; }

	void PressureDoor(AjarPressureDoor pd)
	{
		if (!pd.door) return;
		bool was = pd.held;
		pd.held = Held(pd);
		for (int i = 0; i < pd.lamps.Size(); i++)
		{
			Sector l = level.sectors[pd.lamps[i]];
			l.SetColor(pd.held ? Color(255, 255, 64, 48) : Color(255, 200, 255, 200), 0);
			l.SetLightLevel(pd.held ? 176 : 224);
		}
		// a cell in a tank's floor opens by itself the first time the tank is dry
		if (pd.args[4] & 1 && !pd.autoDone && pd.side[0] && !pd.side[0].Wet() && !pd.held)
		{
			pd.autoDone = true;
			if (!pd.open) { pd.open = true; pd.A_StartSound("doors/dr2_open", CHAN_BODY); }
		}
		// the water comes: it shuts itself
		if (pd.held && !was && pd.open) { pd.open = false; pd.A_StartSound("doors/dr2_clos", CHAN_BODY); }
		double top = pd.Top();
		double want = pd.open ? pd.sill + AjarPressureDoor.UP : pd.sill;
		if (abs(top - want) < 0.01) return;
		if (want < top && Someone(pd)) { pd.shutWaits++; return; }       // never on anyone: it waits
		int r = pd.door.MoveCeiling(AjarPressureDoor.SPEED, want, -1, want > top ? 1 : -1, false);
		if (r == Sector.MOVE_CRUSHED) pd.shutWaits++;
	}

	// anyone (solid) standing in the door's way
	bool Someone(AjarPressureDoor pd)
	{
		let it = BlockThingsIterator.Create(pd, 96);
		while (it.Next())
		{
			let a = it.thing;
			if (!a || !a.bSolid || a.health <= 0 && !a.player) continue;
			if (a.pos.z >= pd.Top() || a.pos.z + a.height <= pd.sill) continue;
			if (level.PointInSector(a.pos.xy) == pd.door) return true;
			// the door's own box: its four corners
			Vector2 lo = (1e9, 1e9), hi = (-1e9, -1e9);
			for (int i = 0; i < pd.door.lines.Size(); i++)
			{
				Line l = pd.door.lines[i];
				for (int e = 0; e < 2; e++)
				{
					Vector2 p = e ? l.v2.p : l.v1.p;
					lo = (min(lo.x, p.x), min(lo.y, p.y));
					hi = (max(hi.x, p.x), max(hi.y, p.y));
				}
			}
			if (a.pos.x + a.radius > lo.x && a.pos.x - a.radius < hi.x && a.pos.y + a.radius > lo.y && a.pos.y - a.radius < hi.y)
				return true;
		}
		return false;
	}

	AjarPressureDoor PressureDoorOfLine(Line l)
	{
		if (!l) return null;
		for (int i = 0; i < pdoors.Size(); i++) if (pdoors[i].uses.Find(l.Index()) < pdoors[i].uses.Size()) return pdoors[i];
		return null;
	}

	// the player's USE (or a test's): true if it opens
	bool UsePressureDoor(AjarPressureDoor pd)
	{
		if (Held(pd))
		{
			pd.refused++;
			if (h) h.Say("The water holds this door shut.\nIt opens when the water at its sill is gone.");
			pd.A_StartSound("plats/pt1_stop", CHAN_BODY);
			return false;
		}
		if (!pd.open) { pd.open = true; pd.A_StartSound("doors/dr1_open", CHAN_BODY); }
		return true;
	}

	// --- MAP20: the float that raises the yard gate -------------------------------------------------
	void FloatGate(AjarFloatGate fg)
	{
		if (!fg.b) return;
		if (!fg.tripped)
		{
			fg.over = fg.b.w >= fg.args[1] ? fg.over + 1 : 0;
			if (fg.over >= fg.args[3] * TICRATE)
			{
				fg.tripped = true;
				fg.trippedAt = level.maptime;
				if (h) h.Say("The float in the feed tank has risen:\nthe yard gate goes up.");
				fg.A_StartSound("doors/dr2_open", CHAN_BODY, 0, 1, ATTN_NONE);
			}
			return;
		}
		for (int i = 0; i < fg.gate.Size(); i++)
		{
			Sector g = level.sectors[fg.gate[i]];
			double fz = g.floorplane.ZatPoint(g.centerspot), cz = g.ceilingplane.ZatPoint(g.centerspot);
			if (cz < fz + 112 - 0.01) g.MoveCeiling(2, fz + 112, -1, 1, false);
		}
	}

	// --- MAP20: ambushes brought by water (AjarAmbush causes 60 and 61; ajarwater.water_ambush) ------
	// arg: the basin's tag * 1024 + the height + 512. Once met, met for good (a basin *first* at it).
	static bool WaterDue(int cause, int arg)
	{
		let wh = Get();
		if (!wh || !wh.ready) return false;
		int key = cause * 65536 + arg;
		if (wh.dueKeys.Find(key) < wh.dueKeys.Size()) return true;
		let b = wh.BasinOfTag(arg / 1024);
		if (!b) return false;
		double z = arg % 1024 - 512;
		bool met = cause == 60 ? b.w >= z : b.w <= z;
		if (met) wh.dueKeys.Push(key);
		return met;
	}

	// A bulkhead will not open from the dry side while water stands behind it.
	override void WorldLinePreActivated(WorldEvent e)
	{
		if (!any || !e.ActivatedLine) return;
		let pd = PressureDoorOfLine(e.ActivatedLine);
		if (pd)
		{
			e.ShouldActivate = false;                        // the handler moves it (PressureDoor)
			if (e.Thing && e.Thing.player) UsePressureDoor(pd);
			return;
		}
		int i = bulkheads.Find(e.ActivatedLine.Index());
		if (i == bulkheads.Size()) return;
		let b = BasinOfTag(bulkheadTag[i]);
		if (!b || !b.Wet()) return;
		e.ShouldActivate = false;
		if (h) h.Say("Water stands behind this bulkhead.\nIt will not open from the dry side.");
	}
}
