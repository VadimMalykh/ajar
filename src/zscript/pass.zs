// The pass and its double (MAP19's outline, "MAP19 'On Paper'"; the lab is
// map PASS, tools/map_pass.py; PLAN.md, "The pass lab").
//
// The player has a pass. A white double stands where the pass says the
// player is: at T(player), T a rigid transform (a turn about the vertical,
// a shift, a change of height). T starts as the identity and changes only
// when the player crosses a line portal: if the portal carries points by M
// (the engine's rule: dst.v2 + R(p - src.v1), heights by the portal's
// alignment), T becomes T o M^-1, so the double goes on as if the portal
// line were a hole in the wall. T is made from the two lines' numbers only,
// never from measured positions, so nothing drifts.
//
// A map with a pass has AjarPassHandler among its MAPINFO EventHandlers and
// at least one pass desk; nothing here runs on any other map.
//  * AjarPassDesk (20132): args[0], args[1] half its box along x and y. The
//    player standing on it (in the box, feet within 32 of its floor) has T
//    set back to the identity.
//  * AjarPassRegister (20133): args[0], args[1] half its plate's box,
//    args[2] the sector tag of the door it opens, args[3] its number (its
//    name: AjarPassRegister.Name). Signed for good once the double has stood
//    in the box, feet within 32 of the plate's floor, for 35 tics running.
//
// Scripted moves of the player that are not portals (SetOrigin, Teleport)
// are not crossings: T is kept and the double moves with the player. A
// script that poses the player calls AjarPassDouble.Posed (keep T) and, to
// put the double back on the player, Reset.

class AjarPassDouble : Actor
{
	// T(p) = R(tAng) p.xy + tOff, p.z + tDz
	double tAng;
	Vector2 tOff;
	double tDz;
	Vector3 last;               // the player's place when the double last looked
	bool started;
	int crossings;              // portal crossings counted, in all
	int unexplained;            // jumps no portal explains (teleports, scripted moves without Posed)
	int lastCrossAt;            // level.maptime of the last crossing
	Line lastSrc, lastDst;      // ... its portal line and where that leads
	int twoInOne;               // tics with two crossings in them
	MapMarker mark;
	AjarPassPlacer placer;

	Default
	{
		Radius 16;
		Height 56;
		CameraHeight 41;
		RenderStyle "Stencil";
		StencilColor "FFFFFF";
		Alpha 0.9;
		+NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH +NOTELEPORT +NEVERTARGET +NOTONAUTOMAP
	}
	States
	{
	Spawn:
		PLAY A -1 Bright;
		Stop;
	}

	// --- the transform ---------------------------------------------------
	// cos and sin of a turn, exact for quarter turns (so that laps add up exactly)
	clearscope static double, double CosSin(double a)
	{
		a = a % 360;
		if (a < 0) a += 360;
		double q = a / 90;
		double n = floor(q + 0.5);
		if (abs(q - n) < 1e-9)
		{
			int k = int(n) % 4;
			if (k == 0) return 1, 0;
			if (k == 1) return 0, 1;
			if (k == 2) return -1, 0;
			return 0, -1;
		}
		return cos(a), sin(a);
	}

	clearscope static Vector2 Rot(Vector2 v, double a)
	{
		double c, s;
		[c, s] = CosSin(a);
		return (c * v.x - s * v.y, s * v.x + c * v.y);
	}

	clearscope static double Norm(double a)
	{
		double q = a / 90;
		double n = floor(q + 0.5);
		if (abs(q - n) < 1e-9) a = n * 90;
		a = a % 360;
		if (a < 0) a += 360;
		return a;
	}

	clearscope Vector3 Apply(Vector3 p) { return (Rot(p.xy, tAng) + tOff, p.z + tDz); }

	clearscope bool IsIdentity() { return tAng == 0 && tOff == (0, 0) && tDz == 0; }

	void Reset()
	{
		tAng = 0;
		tOff = (0, 0);
		tDz = 0;
	}

	// The engine's own numbers for a portal: its turn, and the change of height it gives.
	static double Turn(int i) { return level.LinePortals[i].mAngleDiff; }

	static double Lift(int i)
	{
		Line src = level.LinePortals[i].mOrigin, dst = level.LinePortals[i].mDestination;
		int align = level.LinePortals[i].mAlign;
		if (align == LinePortal.PORG_FLOOR)
			return dst.frontsector.floorplane.ZatPoint(dst.v2.p) - src.frontsector.floorplane.ZatPoint(src.v1.p);
		if (align == LinePortal.PORG_CEILING)
			return dst.frontsector.ceilingplane.ZatPoint(dst.v2.p) - src.frontsector.ceilingplane.ZatPoint(src.v1.p);
		return 0;
	}

	// M^-1 of portal i: where a point beyond its destination came from
	static Vector2 Back(int i, Vector2 q)
	{
		Line src = level.LinePortals[i].mOrigin, dst = level.LinePortals[i].mDestination;
		return src.v1.p + Rot(q - dst.v2.p, -Turn(i));
	}
	static Vector2 Forth(int i, Vector2 p)
	{
		Line src = level.LinePortals[i].mOrigin, dst = level.LinePortals[i].mDestination;
		return dst.v2.p + Rot(p - src.v1.p, Turn(i));
	}

	// T becomes T o M^-1: R(a) (s + R(-f) (p - d)) + o = R(a - f) p + R(a) (s - R(-f) d) + o
	void Compose(int i)
	{
		Line src = level.LinePortals[i].mOrigin, dst = level.LinePortals[i].mDestination;
		double f = Turn(i);
		tOff = Rot(src.v1.p - Rot(dst.v2.p, -f), tAng) + tOff;
		tAng = Norm(tAng - f);
		tDz -= Lift(i);
		crossings++;
		lastCrossAt = level.maptime;
		lastSrc = src;
		lastDst = dst;
	}

	// --- noticing a crossing -------------------------------------------------
	static bool Passable(int i)
	{
		if (!level.LinePortals[i].mOrigin || !level.LinePortals[i].mDestination) return false;
		if (!(level.LinePortals[i].mFlags & LinePortal.PORTF_PASSABLE)) return false;
		int type = level.LinePortals[i].mType;
		return type == LinePortal.PORTT_TELEPORT || type == LinePortal.PORTT_INTERACTIVE;
	}

	// The straight move a -> b goes through line l from its front (the engine's
	// rule: the centre from side 0, on the line included, to side 1), between its ends.
	static bool Crosses(Vector2 a, Vector2 b, Line l)
	{
		if (level.PointOnLineSide(a, l) != 0 || level.PointOnLineSide(b, l) != 1) return false;
		Vector2 r = b - a, d = l.delta, v = l.v1.p;
		double den = d.x * r.y - d.y * r.x;
		if (den == 0) return false;
		double u = ((a.x - v.x) * r.y - (a.y - v.y) * r.x) / den;
		return u > -0.05 && u < 1.05;
	}

	const REACH = 128;          // the longest move a tic (running is 16.67, a fall or a push more)

	// One crossing from p0 that ended at p1 (or that p1 was carried on from):
	// the portal i such that p0 -> M_i^-1(p1) goes through i's line from its front.
	int One(Vector2 p0, Vector2 p1)
	{
		int best = -1;
		double bestD = REACH;
		for (int i = 0; i < level.LinePortals.Size(); i++)
		{
			if (!Passable(i)) continue;
			Vector2 q = Back(i, p1);
			double d = (q - p0).Length();
			if (d < bestD && Crosses(p0, q, level.LinePortals[i].mOrigin)) { best = i; bestD = d; }
		}
		return best;
	}

	// Two crossings in one tic, j then i: returns j * 65536 + i, or -1.
	int Two(Vector2 p0, Vector2 p1)
	{
		for (int i = 0; i < level.LinePortals.Size(); i++)
		{
			if (!Passable(i)) continue;
			Line li = level.LinePortals[i].mOrigin;
			Vector2 r = Back(i, p1);
			if (level.PointOnLineSide(r, li) != 1) continue;
			for (int j = 0; j < level.LinePortals.Size(); j++)
			{
				if (!Passable(j)) continue;
				Line lj = level.LinePortals[j].mOrigin;
				Vector2 q = Back(j, r);
				if ((q - p0).Length() >= REACH || !Crosses(p0, q, lj)) continue;
				// where the move came out of j's far end, and went on to r: through i
				Vector2 dl = lj.delta, rr = q - p0;
				double den = dl.x * rr.y - dl.y * rr.x;
				double t = ((lj.v1.p.x - p0.x) * dl.y - (lj.v1.p.y - p0.y) * dl.x) / -den;
				Vector2 c = Forth(j, p0 + rr * t);
				if (Crosses(c, r, li)) return j * 65536 + i;
			}
		}
		return -1;
	}

	void Track(Actor mo)
	{
		Vector3 p1 = mo.pos;
		// A portal clears the mover's interpolation where it lands (and so does
		// SetOrigin, a teleport): a tic with no jump in it leaves Prev where
		// the double last saw the player. Only then is anything looked for.
		if (mo.Prev.xy != last.xy)
		{
			int i = One(last.xy, mo.Prev.xy);
			if (i < 0) i = One(last.xy, p1.xy);
			if (i >= 0) Compose(i);
			else
			{
				int two = Two(last.xy, mo.Prev.xy);
				if (two < 0) two = Two(last.xy, p1.xy);
				if (two >= 0) { Compose(two / 65536); Compose(two % 65536); twoInOne++; }
				else unexplained++;
			}
		}
		last = p1;
	}

	// --- the shape ---------------------------------------------------------
	void Place(Actor mo)
	{
		SetOrigin(Apply(mo.pos), true);
		angle = mo.angle + tAng;
		pitch = mo.pitch;
		// the player's own frame: standing, walking, firing
		sprite = mo.sprite;
		frame = mo.frame;
		bInvisible = mo.health <= 0;
		if (!mark)
		{
			mark = MapMarker(Spawn("MapMarker", pos));
			if (mark) { mark.args[2] = 0; mark.scale = (0.5, 0.5); }
		}
		if (mark) mark.SetOrigin(pos, false);
	}

	override void Tick()
	{
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		if (!started) { last = mo.pos; started = true; }
		Track(mo);
		Place(mo);
		if (!placer) placer = AjarPassPlacer.Make(self);
	}

	// A script has moved the player itself: not a crossing; T is kept.
	void Posed(Actor mo)
	{
		last = mo.pos;
		Place(mo);
	}

	// The handler's double, if the map has a pass.
	static AjarPassDouble Get()
	{
		let h = AjarPassHandler(EventHandler.Find("AjarPassHandler"));
		return h ? h.dbl : null;
	}

	// The offset from the player in the player's own terms: ahead, left, up.
	clearscope Vector3 FromPlayer(Actor mo)
	{
		Vector3 d = pos - mo.pos;
		Vector2 f = AngleToVector(mo.angle);
		return (d.x * f.x + d.y * f.y, -d.x * f.y + d.y * f.x, d.z);
	}
}

// Crossings are looked for in the double's own tick, between the player's and the
// sector movers' (so a portal's heights are read as they were when the player
// crossed); this puts the double where the player is once lifts have moved too,
// so that it does not ride a tic behind.
class AjarPassPlacer : Thinker
{
	AjarPassDouble dbl;

	static AjarPassPlacer Make(AjarPassDouble d)
	{
		let p = new("AjarPassPlacer");
		p.dbl = d;
		p.ChangeStatNum(STAT_ACTORMOVER);
		return p;
	}

	override void Tick()
	{
		let mo = players[consoleplayer].mo;
		if (!dbl) { Destroy(); return; }
		if (mo) dbl.SetOrigin(dbl.Apply(mo.pos), true);
	}
}

// A pass desk: a plate in the floor that stamps the pass.
class AjarPassDesk : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void Tick()
	{
		let mo = players[consoleplayer].mo;
		let dbl = AjarPassDouble.Get();
		if (!mo || !dbl || mo.health <= 0) return;
		if (abs(mo.pos.x - pos.x) > args[0] || abs(mo.pos.y - pos.y) > args[1]) return;
		if (abs(mo.pos.z - floorz) > 32 || dbl.IsIdentity()) return;
		dbl.Reset();
		dbl.Place(mo);
		mo.A_StartSound("misc/i_pkup", CHAN_AUTO);
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say("Your pass is stamped: it is where you are.");
		else Console.MidPrint(smallfont, "Your pass is stamped: it is where you are.");
	}
}

// A register: a plate in a sealed room, and its lamp (red, green when signed).
class AjarPassRegister : Actor
{
	int held;                   // tics the double has stood on it, running
	bool signed;
	int signedAt;
	double plateZ;

	Default
	{
		Radius 6;
		Height 24;
		+NOBLOCKMAP +NOGRAVITY
	}
	States
	{
	Spawn:
		AJQL B -1 Bright;
		Stop;
	Signed:
		AJQL C -1 Bright;
		Stop;
	}

	// what each register is called, by its number (args[3]); a level adds its own
	static string Name(int n)
	{
		if (level.mapname ~== "PASS")
		{
			static const string names[] = { "a room", "the duty room", "the stack", "the side office", "the mezzanine",
				"the far end of the corridor", "the foot of the stair" };
			return names[clamp(n, 0, 6)];
		}
		return String.Format("register %d", n);
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		plateZ = floorz;
		SetZ(plateZ + 48);          // the lamp stands on the desk, above the plate
		A_AttachLight('lamp', DynamicLight.PointLight, 0xFF3020, 48, 48, 0, (0, 0, 8));
	}

	bool OnIt(Actor a)
	{
		return a && abs(a.pos.x - pos.x) <= args[0] && abs(a.pos.y - pos.y) <= args[1] && abs(a.pos.z - plateZ) <= 32;
	}

	override void Tick()
	{
		if (signed) return;
		let dbl = AjarPassDouble.Get();
		if (OnIt(dbl)) held++;
		else held = 0;
		if (held >= 35) Sign();
	}

	void Sign()
	{
		signed = true;
		signedAt = level.maptime;
		SetStateLabel("Signed");
		A_RemoveLight('lamp');
		A_AttachLight('lamp', DynamicLight.PointLight, 0x40FF60, 48, 48, 0, (0, 0, 8));
		if (args[2]) level.ExecuteSpecial(11 /* Door_Open */, null, null, false, args[2], 16);
		A_StartSound("switches/exitbutn", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		string msg = String.Format("Signed in: %s.\nIts door is unbolted.", Name(args[3]));
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(msg);
		else Console.MidPrint(smallfont, msg);
	}
}

// Keeps the double (one, made at the start), draws the line on the screen and
// the small picture of what the double sees.
class AjarPassHandler : EventHandler
{
	AjarPassDouble dbl;
	bool looked, hasPass, camSet;
	Array<AjarPassRegister> registers;

	override void WorldTick()
	{
		if (!looked)
		{
			looked = true;
			hasPass = ThinkerIterator.Create("AjarPassDesk").Next() != null;
			let it = ThinkerIterator.Create("AjarPassRegister");
			AjarPassRegister r;
			while (r = AjarPassRegister(it.Next())) registers.Push(r);
		}
		if (!hasPass) return;
		let mo = players[consoleplayer].mo;
		if (!dbl && mo)
		{
			dbl = AjarPassDouble(Actor.Spawn("AjarPassDouble", mo.pos));
			dbl.Posed(mo);
		}
		if (dbl && !camSet)
		{
			camSet = true;
			TexMan.SetCameraToTexture(dbl, "AJPASSC", 90);
		}
	}

	// the nearest unsigned register within 1500 of the double
	clearscope AjarPassRegister Nearest()
	{
		AjarPassRegister best;
		double bestD = 1500;
		for (int i = 0; i < registers.Size(); i++)
		{
			let r = registers[i];
			if (!r || r.signed) continue;
			double d = (dbl.pos - (r.pos.xy, r.plateZ)).Length();
			if (d < bestD) { best = r; bestD = d; }
		}
		return best;
	}

	clearscope static string Along(double v, string pos, string neg)
	{
		int n = int(abs(v) + 0.5);
		return n == 0 ? String.Format("0 %s", pos) : String.Format("%d %s", n, v > 0 ? pos : neg);
	}

	// "PASS  640 ahead  128 left  256 down" (empty: the double is on the player)
	clearscope string PassLine()
	{
		let mo = players[consoleplayer].mo;
		if (!dbl || !mo) return "";
		Vector3 o = dbl.FromPlayer(mo);
		if (o.Length() <= 16) return "";
		string h = abs(o.z) < 0.5 ? "level" : Along(o.z, "up", "down");
		return String.Format("PASS  %s  %s  %s", Along(o.x, "ahead", "behind"), Along(o.y, "left", "right"), h);
	}

	// "REGISTER 2: 96 ahead of it, 0 left, level", in the double's own terms
	clearscope string RegisterLine()
	{
		if (!dbl) return "";
		let r = Nearest();
		if (!r) return "";
		Vector2 d = r.pos.xy - dbl.pos.xy;
		Vector2 f = Actor.AngleToVector(dbl.angle);
		double ahead = d.x * f.x + d.y * f.y, left = -d.x * f.y + d.y * f.x;
		double up = r.plateZ - dbl.pos.z;
		string h = abs(up) <= 32 ? "level" : Along(up, "up", "down");
		return String.Format("REGISTER %d: %s, %s, %s", r.args[3], Along(ahead, "ahead of it", "behind it"), Along(left, "left", "right"), h);
	}

	override void RenderOverlay(RenderEvent e)
	{
		if (!dbl || automapactive) return;
		string a = PassLine();
		if (a == "") return;
		string b = RegisterLine();
		Screen.DrawText(SmallFont, Font.CR_WHITE, 240 - SmallFont.StringWidth(a) / 2, 6, a, DTA_VirtualWidth, 480, DTA_VirtualHeight, 300);
		if (b != "") Screen.DrawText(SmallFont, Font.CR_GOLD, 240 - SmallFont.StringWidth(b) / 2, 18, b, DTA_VirtualWidth, 480, DTA_VirtualHeight, 300);
		// what the double sees, a fifth of the screen wide, top right
		if (!CVar.GetCVar("ajar_pass_inset", players[consoleplayer]).GetBool()) return;
		TextureID tex = TexMan.CheckForTexture("AJPASSC", TexMan.Type_Any);
		if (!tex.IsValid()) return;
		int w = Screen.GetWidth() / 5, hgt = w * 10 / 16;
		int x = Screen.GetWidth() - w - 8, y = 8;
		Screen.Clear(x - 2, y - 2, x + w + 2, y + hgt + 2, 0xFFFFFF);
		Screen.DrawTexture(tex, false, x, y, DTA_DestWidth, w, DTA_DestHeight, hgt);
	}
}
