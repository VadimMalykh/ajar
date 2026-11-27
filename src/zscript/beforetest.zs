// The three times lab's checks (map BEFORE, tools/map_before.py; then.zs;
// PLAN.md, "The three times lab"). MAP=BEFORE MODE=n tools/smoke.sh.
// THEN is NOW + (0, 4096), BEFORE NOW + (0, 8192). Frames (NOW / THEN /
// BEFORE): hall 101/121/141 and 102/122/142 (north wall), 103/123 (east
// wall, no BEFORE); strongroom 104/124/144 and 105/125/145 (north wall);
// string line 106/126/146 (north wall); hoist 107/127/147, drip 108/128/148,
// company 109/129/149 (west walls). RED's far side 201 / 221 / 241 (the
// corridor's south wall; BEFORE a pier). Causes: 11 the string line and 12
// the hoist (BEFORE), 13 the drip (THEN). Bays: hall x 0, strongroom 640,
// string 1280, hoist 1920, drip 2560, company 3200.
//   1 the doors; 2 the causes; 3 company; 4 views (tools/smoke_BEFORE_4.cfg
//   shoots at about 50 + 70 n).
// The old door lab (PLAN.md, "The old door lab"; then.zs, a door left hanging): bays
// 7 the door left on the site x 3840 (frame 110/130/150, BLUE in 150 from the
// start), 8 the water x 4480 (frame 111/131/151 in the tank, tag 42; BLUE's far
// side 202/222/242 in the dry room, tag 43; the valve THEN, cause 14).
//   5 the rule; 6 water through an old door.

class BeforeTest : EventHandler
{
	const OFF = 4096;
	const STRONG_X = 640; const STRING_X = 1280; const HOIST_X = 1920; const DRIP_X = 2560; const PEN_X = 3200;
	const OLD_X = 3840; const WATER_X = 4480;
	const WALKKEY = 0x1900;
	int tic, cur, tt;
	int checks, fails;
	AjarHandler h;
	AjarThenHandler th;
	AjarDoor clocked, shadow, ten, tenShadow, red, blue;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "BEFORE"; }

	bool Seg(int n)
	{
		bool now = tic >= cur && tic < cur + n;
		if (now) tt = tic - cur;
		cur += n;
		return now;
	}
	bool At() { return Seg(1); }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }
	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = false;
		Keys();
	}
	int TimeOf(Actor a) { return th.when.TimeOf(a.pos.xy); }
	static const string timeNames[] = { "NOW", "THEN", "BEFORE" };
	string Where(Actor mo) { return String.Format("(%.1f,%.1f,%.1f) angle %.1f %s", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, timeNames[TimeOf(mo)]); }
	bool Facing(Actor mo, double ang) { return abs(Actor.DeltaAngle(mo.angle, ang)) < 1; }
	AjarFrame F(int id) { return h.FindFrame(id); }
	Sector SectorAt(double x, double y) { return level.PointInSector((x, y)); }
	double FZ(double x, double y) { Sector s = SectorAt(x, y); return s.floorplane.ZatPoint(s.centerspot); }
	double CZ(double x, double y) { Sector s = SectorAt(x, y); return s.ceilingplane.ZatPoint(s.centerspot); }
	AjarThenCause Cause(int tid) { return th.FindCause(tid); }
	bool Said(string part) { return h.said.IndexOf(part) >= 0; }
	string Carried() { return h.carried ? h.carried.Label() : "-"; }
	// a portal line open (it leads somewhere), or shut and showing RED's shut door
	bool Open(int id) { Line l = h.FindLine(id); return l && !(l.flags & Line.ML_BLOCKING); }
	bool ShutRed(int id) { Line l = h.FindLine(id); return l && (l.flags & Line.ML_BLOCKING) && TexMan.GetName(l.sidedef[0].GetTexture(Side.mid)) ~== "AJDR1"; }
	string Fars()
	{
		string s = String.Format("red args[0] %d ownFar %d;", red.args[0], red.ownFar);
		for (int id = 201; id <= 241; id += 20) s = s .. String.Format(" %d %s", id, Open(id) ? "open" : ShutRed(id) ? "shut" : "?");
		return s;
	}
	// only RED's far side at time t is open (and, where old doors are on, its far sides at the later times, by the old
	// RED left in the same frame then: the old door lab)
	bool RedAt(int t)
	{
		for (int k = 0; k < 3; k++)
		{
			bool on = k == t || (k < t && th.when.OldDoors());
			if (on != Open(201 + 20 * k) || (!on && !ShutRed(201 + 20 * k))) return false;
		}
		return red.args[0] == 201 + 20 * t;
	}
	// out of RED's far side at time t, facing out of it
	bool InCorridor(Actor mo, int t) { double y = mo.pos.y - t * OFF; return TimeOf(mo) == t && y > -176 && y < -60 && abs(mo.pos.x - 192) < 6 && Facing(mo, 90); }
	string DoorsSaid()
	{
		string s = "";
		for (int i = 0; i < 5; i++)
		{
			AjarDoor d = i == 0 ? clocked : i == 1 ? shadow : i == 2 ? ten : i == 3 ? tenShadow : red;
			s = s .. String.Format("%s%s in %d; ", d.Label(), d.IsShadow() ? "(shadow)" : "", d.frame ? d.frame.args[0] : 0);
		}
		return s .. "carried " .. Carried() .. "; " .. h.said;
	}

	// --- the player's controls, as thentest.zs ---------------------------------------------------------------
	int fwd;
	uint btn;
	Vector2 walkGoal;
	bool walking;
	void Keys(int f = 0, uint b = 0) { fwd = f; btn = b; }
	void WalkTo(double x, double y) { walkGoal = (x, y); walking = true; }
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp) return;
		if (walking)
		{
			Vector2 d = walkGoal - mo.pos.xy;
			if (d.Length() < 6) { walking = false; Keys(); }
			else { mo.angle = VectorAngle(d.x, d.y); fwd = WALKKEY; }
		}
		if (!(fwd || btn)) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.buttons = btn;
		pp.HandleMovement();
	}
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}
	void Shoot(Actor mo, double ang)
	{
		mo.angle = ang;
		mo.pitch = 0;
		mo.LineAttack(ang, 4096, 0, 10, 'Hitscan', "BulletPuff");
	}
	double AimThrough(Actor mo, int src, int dst, Vector2 p)
	{
		Vector2 img = AjarSight.ImageThrough(h.FindLine(src), h.FindLine(dst), p);
		return VectorAngle(img.x - mo.pos.x, img.y - mo.pos.y);
	}
	// by script: a door out of its frame into the hands, or into a frame (its other leaf with it)
	void ScriptUnhang(AjarDoor d) { if (d.frame) h.carried = h.Unhang(d.frame); }
	void ScriptHang(AjarDoor d, int id)
	{
		ScriptUnhang(d);
		if (h.carried == d) h.carried = null;
		h.Hang(d, F(id));
	}

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		tic++;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (tic == 1)
		{
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.args[1] == AjarDoor.CLOCKED) { if (d.IsShadow()) shadow = d; else clocked = d; }
				else if (d.args[1] == AjarDoor.TENYEAR) { if (d.IsShadow()) tenShadow = d; else ten = d; }
				else if (d.args[1] == 1) red = d;
				else if (d.args[1] == 2) blue = d;
			}
			mo.player.cheats |= CF_GODMODE;
			if (mode != 3) mo.player.cheats |= CF_NOTARGET;
			Info(String.Format("times %d; causes %d, cause sectors %d, targets %d; clocked %d shadow %d ten-year %d shadow %d red %d blue %d; old doors %d",
				th.when.Times(), th.causes.Size(), th.secIdx.Size(), th.targets.Size(),
				clocked != null, shadow != null, ten != null, tenShadow != null, red != null, blue != null, th.when.OldDoors()));
		}
		cur = 2;
		if (mode == 1) Doors(mo);
		else if (mode == 2) Causes(mo);
		else if (mode == 3) Company(mo);
		else if (mode == 4) Views(mo);
		else if (mode == 5) Rule(mo);
		else if (mode == 6) Water(mo);
		Drive(mo);
		if (mode != 4 && tic == cur + 2) Console.Printf("AJARTEST beforeDone=1 checks=%d failed=%d", checks, fails);
	}

	// walk 24 tics from a frame's mouth into it (the player stands 18 in front of it, facing it)
	void Through(Actor mo, double x, double y, double ang)
	{
		Pose(mo, x, y, ang);
		Keys(WALKKEY);
	}

	// === MODE=1: the doors ===========================================================================
	void Doors(Actor mo)
	{
		if (At())
		{
			Check("threeTimes", th.when.Times() == 3 && TimeOf(mo) == AjarThen.T_NOW, Where(mo));
			Check("allDoorsThere", clocked && shadow && ten && tenShadow && red && !ten.frame && TimeOf(ten) == AjarThen.T_THEN);
			Check("nowMusicAtStart", th.musicThen == 0);
			Check("redFarSidesShutAtStart", ShutRed(201) && ShutRed(221) && ShutRed(241), Fars());
		}
		// the clocked door NOW into 101 by a real USE, and through into THEN
		if (At()) { Pose(mo, 100, 140, 270); clocked.Used(mo); }
		if (At()) { Pose(mo, 128, 470, 90); PressUse(mo); }
		if (At()) Check("clockedHungNow", clocked.frame == F(101) && shadow.frame == F(121) && clocked.args[0] == 121 && shadow.args[0] == 101, DoorsSaid());
		if (At()) Through(mo, 128, 452, 90);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("walkedIntoThen", TimeOf(mo) == AjarThen.T_THEN && mo.pos.y > OFF + 380 && mo.pos.y < OFF + 512 && Facing(mo, 270), Where(mo));
			Check("thenMusic", th.musicThen == 1);
		}
		// the ten-year door, leaning THEN: its own look, and its words
		if (At()) { Pose(mo, 400, OFF + 150, 270); ten.Used(mo); }
		if (At())
			Check("tookTenYear", h.carried == ten && ten.bInvisible && Said("The ten-year door.") && ten.sprite == Actor.GetSpriteIndex('AJDY')
				&& ten.Label() == "TEN-YEAR", DoorsSaid());
		// carried through the clocked door into NOW: NOW is no time of its clock
		if (At()) Through(mo, 128, OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("tenYearCarriedIntoNow", TimeOf(mo) == AjarThen.T_NOW && h.carried == ten, Where(mo)); }
		if (At()) { Pose(mo, 384, 470, 90); PressUse(mo); }
		if (At()) Check("tenYearRefusesNow", h.carried == ten && !F(102).door && Said("ten-year door's clock does not reach this time"), DoorsSaid());
		if (At()) Through(mo, 128, 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("tenYearBackIntoThen", TimeOf(mo) == AjarThen.T_THEN && h.carried == ten, Where(mo)); }
		// 123 has no BEFORE: no other time for the ten-year door
		if (At()) { Pose(mo, 470, OFF + 256, 0); PressUse(mo); }
		if (At()) Check("tenYearRefusesTwinless", h.carried == ten && !F(123).door && Said("This frame has no other time.\nThe ten-year door"), DoorsSaid());
		// into 122 THEN: its other leaf BEFORE in 142, linked both ways
		if (At()) { Pose(mo, 384, OFF + 470, 90); PressUse(mo); }
		if (At())
		{
			Check("tenYearHungThen", ten.frame == F(122) && tenShadow.frame == F(142) && ten.args[0] == 142 && tenShadow.args[0] == 122
				&& !tenShadow.bInvisible && tenShadow.sprite == Actor.GetSpriteIndex('AJDY') && Said("ten years before"), DoorsSaid());
			Check("handsEmpty", h.carried == null);
		}
		if (Seg(2) && tt == 1) Check("chainLinked", th.Linked() && th.LinkedAt(AjarThen.T_THEN) && th.wasLinked && th.wasLinkedBefore);
		if (At()) Through(mo, 384, OFF + 452, 90);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("walkedIntoBefore", TimeOf(mo) == AjarThen.T_BEFORE && mo.pos.y > 2 * OFF + 380 && mo.pos.y < 2 * OFF + 512 && abs(mo.pos.x - 384) < 4
				&& Facing(mo, 270), Where(mo));
			Check("beforeMusic", th.musicThen == AjarThen.T_BEFORE, String.Format("changes %d", th.musicChanges));
		}
		if (At()) Through(mo, 384, 2 * OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("backIntoThenFromBefore", TimeOf(mo) == AjarThen.T_THEN && Facing(mo, 270), Where(mo)); }
		// the clocked door taken THEN and carried through the ten-year door: BEFORE is no time of its clock
		if (At()) { Pose(mo, 128, OFF + 470, 90); PressUse(mo); }
		if (At()) Check("tookClockedThen", h.carried == clocked && !F(101).door && !F(121).door && Said("Now and then, the frame is empty."), DoorsSaid());
		if (At()) Through(mo, 384, OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("clockedCarriedIntoBefore", TimeOf(mo) == AjarThen.T_BEFORE && h.carried == clocked, Where(mo)); }
		if (At()) { Pose(mo, 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("clockedRefusesBefore", h.carried == clocked && !F(141).door && Said("clocked door's clock does not reach this time"), DoorsSaid());
		if (At()) Through(mo, 384, 2 * OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("clockedBackIntoThen", TimeOf(mo) == AjarThen.T_THEN && h.carried == clocked, Where(mo)); }
		// hung THEN in 121: its other leaf NOW in 101
		if (At()) { Pose(mo, 128, OFF + 470, 90); PressUse(mo); }
		if (At()) Check("clockedHungFromThen", clocked.frame == F(121) && shadow.frame == F(101), DoorsSaid());
		// the chain: NOW to THEN to BEFORE on foot, and back
		if (At()) Through(mo, 128, 452, 90);
		if (Seg(24) && tt == 23) { Keys(); WalkTo(384, OFF + 440); }
		if (Seg(70) && tt == 69) Through(mo, 384, OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("chainNowThenBefore", TimeOf(mo) == AjarThen.T_BEFORE, Where(mo)); }
		if (At()) Through(mo, 384, 2 * OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); WalkTo(128, OFF + 440); }
		if (Seg(70) && tt == 69) Through(mo, 128, OFF + 452, 90);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("chainBeforeThenNow", TimeOf(mo) == AjarThen.T_NOW && mo.pos.y > 380 && mo.pos.y < 512, Where(mo));
			Check("nowMusicAgain", th.musicThen == 0);
		}

		// RED at all three times: its far side at the time of the frame it hangs in
		if (At()) { Pose(mo, 200, 140, 270); red.Used(mo); }
		if (At()) { Pose(mo, 384, 470, 90); PressUse(mo); }
		if (At()) Check("redNowOpensNow", red.frame == F(102) && RedAt(0), Fars());
		if (At()) Through(mo, 384, 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("redNowLeadsNow", InCorridor(mo, 0), Where(mo)); }
		if (At()) { Pose(mo, 384, 470, 90); PressUse(mo); }                        // RED down, carried into THEN
		if (At()) Through(mo, 128, 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Pose(mo, 470, OFF + 256, 0); PressUse(mo); }
		if (At()) Check("redThenOpensThen", red.frame == F(123) && RedAt(1), Fars());
		if (At()) Through(mo, 452, OFF + 256, 0);
		if (Seg(24) && tt == 23) { Keys(); Check("redThenLeadsThen", InCorridor(mo, 1), Where(mo)); }
		if (At()) { Pose(mo, 470, OFF + 256, 0); PressUse(mo); }                    // RED down, carried into BEFORE
		if (At()) Through(mo, 384, OFF + 452, 90);
		// (in 145, the strongroom's second frame: 141 is kept free for the refusal below)
		if (Seg(24) && tt == 23) { Keys(); Pose(mo, STRONG_X + 384, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("redBeforeOpensBefore", red.frame == F(145) && RedAt(2), Fars() .. "; " .. Where(mo));
		if (At()) Through(mo, STRONG_X + 384, 2 * OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("redBeforeLeadsBefore", InCorridor(mo, 2), Where(mo)); }
		if (At()) Through(mo, 192, 2 * OFF - 120, 270);
		if (Seg(30) && tt == 29)
		{
			Keys();
			Check("redBackToItsFrameBefore", TimeOf(mo) == AjarThen.T_BEFORE && abs(mo.pos.x - STRONG_X - 384) < 6 && mo.pos.y > 2 * OFF + 380 && Facing(mo, 270), Where(mo));
		}
		// the ten-year door, taken BEFORE, refused where its twin THEN holds another door (141; 121 the clocked door)
		if (At()) { Pose(mo, 384, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("tookTenYearBefore", h.carried == ten && !F(122).door && !F(142).door && Said("Then and before, the frame is empty."), DoorsSaid());
		if (At()) { Pose(mo, 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("tenYearRefusedTwinHolds", h.carried == ten && !F(141).door && F(121).door == clocked && Said("At the other time a door hangs in this frame.\nThe ten-year door"), DoorsSaid());

		// the strongroom: the ten-year door in its free frame BEFORE (144) opens into it THEN (124)
		if (At()) { Pose(mo, 768, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("tenYearIn144", ten.frame == F(144) && tenShadow.frame == F(124), DoorsSaid());
		if (At()) Through(mo, 768, 2 * OFF + 452, 90);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("intoStrongroomThen", TimeOf(mo) == AjarThen.T_THEN && mo.pos.x > STRONG_X && mo.pos.x < STRONG_X + 512 && mo.pos.y > OFF && mo.pos.y < OFF + 512, Where(mo));
			WalkTo(STRONG_X + 256, OFF + 256);
		}
		if (Seg(60) && tt == 59) Check("soulSphereThen", mo.health > 100, String.Format("health %d", mo.health));
		// ... and on to NOW by the clocked door in 125 (105 NOW). In play the clocked door cannot be brought in
		// here (PLAN.md, "The three times lab": the solver's strongroom NOW); the script puts it in hand.
		if (At())
		{
			// (RED, left BEFORE in 145, is an old door THEN in 125: the script takes it down first, the old door lab)
			if (th.when.OldDoors() && red.frame) { ScriptUnhang(red); PutBack(red); Info("RED taken out of 145 by the script: its old self THEN filled 125"); }
			ScriptUnhang(clocked);
			Info("the clocked door taken out of 121 and put in hand by the script, in the strongroom THEN");
			Pose(mo, STRONG_X + 384, OFF + 470, 90);
			PressUse(mo);
		}
		if (At()) Check("clockedIn125", clocked.frame == F(125) && shadow.frame == F(105), DoorsSaid());
		if (At()) Through(mo, STRONG_X + 384, OFF + 452, 90);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("strongroomNowFromIt", TimeOf(mo) == AjarThen.T_NOW && mo.pos.x > STRONG_X && mo.pos.x < STRONG_X + 512 && mo.pos.y > 0 && mo.pos.y < 512, Where(mo));
			Check("chainThroughStrongroom", th.Linked() && th.LinkedAt(AjarThen.T_THEN));
		}
		if (At()) Through(mo, STRONG_X + 384, 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Through(mo, STRONG_X + 128, OFF + 452, 90); }
		if (Seg(24) && tt == 23) { Keys(); Check("strongroomBackToBefore", TimeOf(mo) == AjarThen.T_BEFORE, Where(mo)); }
	}

	// === MODE=2: the causes ===========================================================================
	int fullAt;
	void Causes(Actor mo)
	{
		let sc = Cause(11), hc = Cause(12), dc = Cause(13);
		let b = th.wh.BasinOfTag(41);
		double ax = STRING_X + 168, bx = STRING_X + 344, lx = HOIST_X + 256;
		if (At())
		{
			Check("stringAtStart", sc.setting == 0 && CZ(ax, 256) == 0 && CZ(ax, OFF + 256) == 0 && CZ(bx, 256) == 256 && CZ(bx, OFF + 256) == 256,
				String.Format("A %.0f/%.0f B %.0f/%.0f", CZ(ax, 256), CZ(ax, OFF + 256), CZ(bx, 256), CZ(bx, OFF + 256)));
			Check("hoistDownAtStart", hc.setting == 0 && FZ(lx, 448) == 0 && FZ(lx, OFF + 448) == 0 && FZ(lx, 2 * OFF + 448) == 0,
				String.Format("%.0f %.0f %.0f", FZ(lx, 448), FZ(lx, OFF + 448), FZ(lx, 2 * OFF + 448)));
			Check("dryAtStart", b && !b.Wet() && dc.setting == 0);
		}
		// the string line's lever: dead NOW and THEN (where the wall stands since), live BEFORE
		if (At()) { Pose(mo, STRING_X + 304, 32, 270); PressUse(mo); }
		if (At()) { Pose(mo, STRING_X + 304, OFF + 32, 270); PressUse(mo); }
		if (Seg(10) && tt == 9) Check("stringLeverDeadNowAndThen", sc.setting == 0);
		if (At()) { Pose(mo, STRING_X + 304, 2 * OFF + 32, 270); PressUse(mo); }
		if (Seg(150))
		{
			if (tt == 0) Check("stringLeverBefore", sc.setting == 1);
			if (tt == 149)
			{
				Check("partitionBBuiltThenAndNow", CZ(bx, 256) == 0 && CZ(bx, OFF + 256) == 0, String.Format("B %.0f/%.0f", CZ(bx, 256), CZ(bx, OFF + 256)));
				Check("partitionANeverBuilt", CZ(ax, 256) == 256 && CZ(ax, OFF + 256) == 256, String.Format("A %.0f/%.0f", CZ(ax, 256), CZ(ax, OFF + 256)));
				Check("beforeHasNoWall", CZ(ax, 2 * OFF + 256) == 256 && CZ(bx, 2 * OFF + 256) == 256);
			}
		}
		// NOW: into the west strip (the rocket launcher); the east one is walled off
		if (At()) { Pose(mo, STRING_X + 256, 256, 180); WalkTo(STRING_X + 80, 256); }
		if (Seg(70) && tt == 69) Check("westStripNow", mo.pos.x < STRING_X + 160 && mo.FindInventory("RocketLauncher") != null, Where(mo));
		if (At()) { Pose(mo, STRING_X + 256, 256, 0); Keys(WALKKEY); }
		if (Seg(50) && tt == 49) { Keys(); Check("eastStripWalledNow", mo.pos.x < STRING_X + 336, Where(mo)); }
		// shot from THEN through the ten-year door in 126: target A BEFORE
		if (At()) ScriptHang(ten, 126);
		if (At())
		{
			Check("tenYearIn126", ten.frame == F(126) && tenShadow.frame == F(146));
			Pose(mo, STRING_X + 256, OFF + 400, 90);
			Shoot(mo, AimThrough(mo, 126, 146, (ax, 2 * OFF + 12)));
		}
		if (Seg(150))
		{
			if (tt == 1) Check("shotFromThenThroughTenYearSetsA", sc.setting == 0, Where(mo));
			if (tt == 149) Check("partitionABuiltAgain", CZ(ax, 256) == 0 && CZ(ax, OFF + 256) == 0 && CZ(bx, 256) == 256 && CZ(bx, OFF + 256) == 256);
		}
		// nothing crushed: NOW the player stands where B would be built; the lever BEFORE sets B
		if (At()) { Pose(mo, bx, 256, 0); sc.Activate(null); }
		if (Seg(150) && tt == 149)
		{
			Check("partitionBWaitsForPlayer", sc.setting == 1 && CZ(bx, 256) > 200 && mo.health > 0 && abs(mo.pos.x - bx) < 1, String.Format("B %.0f/%.0f ", CZ(bx, 256), CZ(bx, OFF + 256)) .. Where(mo));
			Check("partitionAWaitsForB", CZ(ax, 256) == 0 && CZ(ax, OFF + 256) == 0);
		}
		if (At()) Pose(mo, STRING_X + 256, 256, 0);
		if (Seg(150) && tt == 149) Check("thenBBuiltAndAOpen", CZ(bx, 256) == 0 && CZ(bx, OFF + 256) == 0 && CZ(ax, 256) == 256 && CZ(ax, OFF + 256) == 256);

		// the hoist: its lever BEFORE; the landing THEN and NOW
		if (At()) { Pose(mo, HOIST_X + 480, 2 * OFF + 96, 0); PressUse(mo); }
		if (Seg(90))
		{
			if (tt == 0) Check("hoistLeverBefore", hc.setting == 1);
			if (tt == 89) Check("landingAtAllThreeTimes", FZ(lx, 448) == 128 && FZ(lx, OFF + 448) == 128 && FZ(lx, 2 * OFF + 448) == 128,
				String.Format("%.0f %.0f %.0f", FZ(lx, 448), FZ(lx, OFF + 448), FZ(lx, 2 * OFF + 448)));
		}
		if (At()) { Pose(mo, HOIST_X + 96, 448, 0); WalkTo(HOIST_X + 448, 448); }
		if (Seg(90) && tt == 89) Check("onTheLedgeNow", mo.pos.x > HOIST_X + 320 && abs(mo.pos.z - 128) < 0.5 && mo.health >= 200, Where(mo) .. String.Format(" health %d", mo.health));
		if (At()) { Pose(mo, HOIST_X + 96, OFF + 448, 0); WalkTo(HOIST_X + 448, OFF + 448); }
		if (Seg(90) && tt == 89) Check("onTheLedgeThen", mo.pos.x > HOIST_X + 320 && abs(mo.pos.z - 128) < 0.5 && TimeOf(mo) == AjarThen.T_THEN, Where(mo));
		// down, by a shot from THEN through the ten-year door in 127
		if (At()) ScriptHang(ten, 127);
		if (At())
		{
			Check("tenYearIn127", ten.frame == F(127) && tenShadow.frame == F(147));
			Pose(mo, HOIST_X + 96, OFF + 192, 180);
			Shoot(mo, AimThrough(mo, 127, 147, (HOIST_X + 500, 2 * OFF + 48)));
		}
		if (Seg(90))
		{
			if (tt == 1) Check("shotFromThenSetsHoistDown", hc.setting == 0, Where(mo));
			if (tt == 89) Check("noLandingNowOrThen", FZ(lx, 448) == 0 && FZ(lx, OFF + 448) == 0 && FZ(lx, 2 * OFF + 448) == 0);
		}
		// BEFORE, the platform rides the player up
		if (At()) { Pose(mo, lx, 2 * OFF + 448, 0); hc.Activate(null); }
		if (Seg(90) && tt == 89) Check("platformRidesUpBefore", abs(mo.pos.z - 128) < 0.5 && mo.health > 0, Where(mo));

		// beside them, a cause THEN that moves NOW only: the drip
		if (At()) { Pose(mo, DRIP_X + 470, 320, 0); PressUse(mo); }
		if (Seg(10) && tt == 9) Check("dripLeverDeadNow", dc.setting == 0);
		if (At()) { Pose(mo, DRIP_X + 470, OFF + 320, 0); PressUse(mo); fullAt = -1; }
		if (Seg(140))
		{
			if (tt == 0) Check("dripLeverThen", dc.setting == 1);
			if (fullAt < 0 && b.w >= 95.5) fullAt = tt;
			if (tt == 139)
			{
				Check("tankFullNow", fullAt >= 0 && abs(b.w - 96) < 0.01, String.Format("%d tics, w %.2f", fullAt, b.w));
				Check("thenStaysDry", mo.waterlevel == 0 && TimeOf(mo) == AjarThen.T_THEN);
				// both spans at once: the causes BEFORE stand as they were set, THEN's moved NOW alone
				Check("bothSpans", sc.setting == 1 && hc.setting == 1 && CZ(bx, OFF + 256) == 0 && FZ(lx, OFF + 448) == 128 && b.Wet());
			}
		}
		if (At()) Pose(mo, DRIP_X + 256, 2 * OFF + 256, 0);
		if (Seg(3) && tt == 2) Check("beforeHasNoTank", mo.waterlevel == 0 && TimeOf(mo) == AjarThen.T_BEFORE);
	}

	// === MODE=3: company =============================================================================
	Actor impThen, impBefore;
	int StandIns(Actor a, int at = -1)
	{
		int n = 0;
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && c.of == a && !c.Leaving() && (at < 0 || c.at == at)) n++;
		}
		return n;
	}
	int DeadOnes(Actor a, int at = -1)
	{
		int n = 0;
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && c.who == a && !c.of && (at < 0 || c.at == at)) n++;
		}
		return n;
	}
	AjarThenCorpse CorpseOf(Actor a, int at)
	{
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && c.who == a && c.at == at && !c.Leaving()) return c;
		}
		return null;
	}
	string Bones()
	{
		string s = String.Format("links %d %d;", th.wasLinked, th.wasLinkedBefore);
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c) s = s .. String.Format(" [%s at %s (%.0f,%.0f)%s%s]", c.who == impThen ? "impThen" : c.who == impBefore ? "impBefore" : "other",
				timeNames[c.at], c.pos.x, c.pos.y, c.of ? " stand-in" : " dead", c.Leaving() ? " leaving" : "");
		}
		return s;
	}
	// the company bay at time t
	Vector2 Bay(double x, double y, int t) { return (PEN_X + x, t * OFF + y); }

	void Company(Actor mo)
	{
		if (At())
		{
			Pose(mo, PEN_X + 256, 2 * OFF + 100, 90);
			impThen = Actor.Spawn("DoomImp", (Bay(200, 300, 1), 0));
			impBefore = Actor.Spawn("DoomImp", (Bay(400, 300, 2), 0));
			impThen.bDormant = impBefore.bDormant = true;
			ScriptHang(clocked, 101);
			ScriptHang(ten, 122);
		}
		if (Seg(5) && tt == 4) Check("allJoinedNoStandIns", th.wasLinked && th.wasLinkedBefore && StandIns(impThen) == 0 && StandIns(impBefore) == 0, Bones());
		// THEN and BEFORE apart (NOW and THEN joined): the one BEFORE shows THEN and NOW; the one THEN nowhere
		if (At()) ScriptUnhang(ten);
		if (Seg(5) && tt == 4)
			Check("thenBeforeApart", StandIns(impBefore, 1) == 1 && StandIns(impBefore, 0) == 1 && StandIns(impThen) == 0
				&& CorpseOf(impBefore, 1) && (CorpseOf(impBefore, 1).pos.xy - Bay(400, 300, 1)).Length() < 1
				&& CorpseOf(impBefore, 0) && (CorpseOf(impBefore, 0).pos.xy - Bay(400, 300, 0)).Length() < 1, Bones());
		// all joined again: they go
		if (At()) { h.carried = null; h.Hang(ten, F(122)); }
		if (Seg(40) && tt == 39) Check("joinedAgainTheyGo", StandIns(impBefore) == 0 && StandIns(impThen) == 0, Bones());
		// NOW and THEN apart (THEN and BEFORE joined): the one THEN shows NOW, the one BEFORE NOW only
		if (At()) ScriptUnhang(clocked);
		if (Seg(5) && tt == 4)
			Check("nowThenApart", StandIns(impThen, 0) == 1 && StandIns(impBefore, 0) == 1 && StandIns(impBefore, 1) == 0, Bones());
		// all apart: the one BEFORE THEN and NOW, the one THEN NOW, none twice
		if (At()) { h.carried = null; ScriptUnhang(ten); }
		if (Seg(5) && tt == 4)
			Check("allApart", StandIns(impThen, 0) == 1 && StandIns(impBefore, 0) == 1 && StandIns(impBefore, 1) == 1 && StandIns(impThen, 1) == 0, Bones());
		// killed BEFORE: its stand-ins THEN and NOW are its old corpses for good
		if (At()) { h.carried = null; impBefore.bDormant = false; impBefore.DamageMobj(null, mo, 10000, 'None'); }
		if (Seg(5) && tt == 4)
			Check("killedBeforeCorpsesThenAndNow", impBefore.health <= 0 && DeadOnes(impBefore, 1) == 1 && DeadOnes(impBefore, 0) == 1 && StandIns(impBefore) == 0, Bones());
		if (At()) { ScriptHang(clocked, 101); ScriptHang(ten, 122); h.carried = null; }
		if (Seg(40) && tt == 39)
			Check("deadOnesStayJoined", DeadOnes(impBefore, 1) == 1 && DeadOnes(impBefore, 0) == 1 && StandIns(impThen) == 0, Bones());
		// killed THEN (all joined): its old corpse NOW only
		if (At()) { impThen.bDormant = false; impThen.DamageMobj(null, mo, 10000, 'None'); }
		if (Seg(5) && tt == 4) Check("killedThenCorpseNowOnly", DeadOnes(impThen, 0) == 1 && DeadOnes(impThen) == 1, Bones());
		if (At()) { ScriptUnhang(clocked); h.carried = null; ScriptUnhang(ten); h.carried = null; }
		if (Seg(40) && tt == 39) Check("deadOnesStayApart", DeadOnes(impBefore) == 2 && DeadOnes(impThen) == 1 && StandIns(impThen) == 0 && StandIns(impBefore) == 0, Bones());
		Follow(mo);
	}

	// Following through a clocked door (thentest.zs's MODE=7, doorcaco.zs): one monster at a time is set on the
	// player in the company bay, who walks through the door to the other time and on into the bay there. The
	// ten-year door in 129 / 149: THEN to BEFORE and BEFORE to THEN; the clocked door in 109 / 129 beside it.
	static const string followKinds[] = { "DoomImp", "Demon" };
	int fTrial, fStart, fOut, fOutAt, fFlips, fInMouth, fLongest, fWas;
	bool fBegun;
	Actor fDog;
	bool InBay(Actor a, int t) { double y = a.pos.y - t * OFF; return TimeOf(a) == t && a.pos.x > PEN_X + a.radius + 8 && a.pos.x < PEN_X + 512 && y > 0 && y < 512; }
	bool InMouth(Actor a) { double y = a.pos.y - TimeOf(a) * OFF; return a.pos.x < PEN_X + a.radius + 2 && a.pos.x > PEN_X - 64 && y > 224 - 32 && y < 288 + 32; }
	void Follow(Actor mo)
	{
		if (tic < cur) return;
		int n = followKinds.Size();
		if (!fBegun)
		{
			fBegun = true;
			mo.player.cheats &= ~CF_NOTARGET;
			ScriptHang(ten, 129);
			h.carried = null;
			Check("tenYearIn129", ten.frame == F(129) && tenShadow.frame == F(149), DoorsSaid());
			fStart = tic + 3;
		}
		if (fTrial > 2 * n) { cur = tic + 100; if (fTrial == 2 * n + 1) { fTrial++; cur = tic - 2; } return; }
		cur = tic + 100;
		// trials 0..n-1 THEN to BEFORE, n..2n-1 BEFORE to THEN (the ten-year door); 2n NOW to THEN (the clocked door)
		bool clockedTrial = fTrial == 2 * n;
		int from = clockedTrial ? 0 : fTrial < n ? 1 : 2, to = clockedTrial ? 1 : fTrial < n ? 2 : 1;
		string kind = clockedTrial ? "DoomImp" : followKinds[fTrial % n];
		int st = tic - fStart;
		if (st < 0) return;
		if (st == 0)
		{
			if (clockedTrial) { ScriptUnhang(ten); h.carried = null; ScriptHang(clocked, 109); h.carried = null; Info("the clocked door hung in 109 / 129 for the last trial; the ten-year door taken out"); }
			Pose(mo, PEN_X + 40, from * OFF + 256, 180);
			fDog = Actor.Spawn(kind, (PEN_X + 380, from * OFF + 120, 0));
			fDog.angle = 180;
			fDog.target = mo;
			fDog.SetState(fDog.SeeState);
			fOut = fOutAt = fFlips = fInMouth = fLongest = 0;
			fWas = from;
		}
		if (st == 20) Keys(WALKKEY);
		if (st == 50) { Keys(); WalkTo(PEN_X + 420, to * OFF + 420); }
		if (st > 0 && fDog)
		{
			if (TimeOf(fDog) != fWas) { fFlips++; fWas = TimeOf(fDog); }
			if (InMouth(fDog)) { fInMouth++; fLongest = max(fLongest, fInMouth); } else fInMouth = 0;
			if (InBay(fDog, to)) { if (!fOutAt) fOutAt = st; fOut++; } else fOut = 0;
			if (st % 15 == 0) Info(String.Format("follow %d t+%d %s", fTrial, st, AjarDoorTrace.Of(fDog)));
		}
		if (st == 1050 || (fOut >= 70 && st > 60) || (st > 0 && (!fDog || fDog.health <= 0)))
		{
			string name = String.Format("%s%sTo%s", kind, timeNames[from], timeNames[to]);
			Check(name .. (clockedTrial ? "_throughClocked" : "_throughTenYear"), fDog && fDog.health > 0 && fOut >= 70 && fFlips == 1 && fLongest < 105,
				String.Format("out of the far recess at t+%d, %d crossings, longest in an opening %d tics; %s", fOutAt, fFlips, fLongest, AjarDoorTrace.Of(fDog)));
			if (fDog) { fDog.ClearCounters(); fDog.Destroy(); }
			walking = false;
			Keys();
			fTrial++;
			fStart = tic + 1;
			if (fTrial == 2 * n + 1) fStart = tic + 1000000;
		}
	}

	// === MODE=4: views for a person to judge (smoke_BEFORE_4.cfg: a shot at about 50 + 70 n) ========
	int viewN;
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void Set(AjarThenCause c, int s) { th.SetCause(c, s, null); th.Snap(c); }
	void Views(Actor mo)
	{
		let sc = Cause(11), hc = Cause(12), dc = Cause(13);
		if (Seg(15)) {}
		if (At()) mo.bInvisible = true;
		if (At()) View(mo, "hall NOW (from the south-west): the clocked door and RED leaning", 40, 40, 45);
		if (Seg(69)) {}
		if (At()) View(mo, "hall THEN (from the south-west)", 40, OFF + 40, 45);
		if (Seg(69)) {}
		if (At()) View(mo, "the ten-year door leaning THEN", 400, OFF + 200, 270, 10);
		if (Seg(69)) {}
		if (At()) View(mo, "hall BEFORE: the yard, frames 141 and 142 in their piers", 256, 2 * OFF + 160, 90);
		if (Seg(69)) {}
		if (At()) { ScriptHang(clocked, 101); h.carried = null; View(mo, "hall NOW through 101 into THEN (the clocked door)", 128, 250, 90); }
		if (Seg(69)) {}
		if (At()) { ScriptHang(ten, 122); h.carried = null; View(mo, "hall THEN through 122 into BEFORE (the ten-year door)", 384, OFF + 250, 90); }
		if (Seg(69)) {}
		if (At()) View(mo, "BEFORE: the ten-year door hung in 142, and through it THEN", 384, 2 * OFF + 300, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "strongroom THEN, inside (from the south-west)", STRONG_X + 40, OFF + 40, 45);
		if (Seg(69)) {}
		if (At()) View(mo, "strongroom NOW, inside (from the south-west)", STRONG_X + 40, 40, 45);
		if (Seg(69)) {}
		if (At()) { ScriptHang(ten, 144); h.carried = null; View(mo, "BEFORE: the strongroom's site, the ten-year door in 144 and 145 free", STRONG_X + 256, 2 * OFF + 200, 90); }
		if (Seg(69)) {}
		if (At()) View(mo, "strongroom THEN through 124 into BEFORE", STRONG_X + 128, OFF + 300, 90);
		if (Seg(69)) {}
		if (At()) { Set(sc, 0); View(mo, "string NOW, line A: the west strip walled off", STRING_X + 256, 40, 120); }
		if (Seg(69)) {}
		if (At()) { Set(sc, 1); View(mo, "string NOW, line B: the east strip walled off", STRING_X + 256, 40, 60); }
		if (Seg(69)) {}
		if (At()) View(mo, "string THEN, line B", STRING_X + 256, OFF + 40, 60);
		if (Seg(69)) {}
		if (At()) View(mo, "string BEFORE: the lever on its pier and the two targets (B lit)", STRING_X + 256, 2 * OFF + 160, 270);
		if (Seg(69)) {}
		if (At()) { ScriptHang(ten, 126); h.carried = null; View(mo, "string THEN through 126 into BEFORE: the lever and targets", STRING_X + 256, OFF + 400, 90); }
		if (Seg(69)) {}
		if (At()) { Set(hc, 0); View(mo, "hoist NOW, platform down: no landing between gallery and ledge", HOIST_X + 256, 120, 90, -10); }
		if (Seg(69)) {}
		if (At()) { Set(hc, 1); View(mo, "hoist NOW, platform up: the landing", HOIST_X + 256, 120, 90, -10); }
		if (Seg(69)) {}
		if (At()) View(mo, "hoist THEN, platform up: the landing", HOIST_X + 256, OFF + 120, 90, -10);
		if (Seg(69)) {}
		if (At()) View(mo, "hoist BEFORE, the platform up", HOIST_X + 60, 2 * OFF + 200, 40);
		if (Seg(69)) {}
		if (At()) { Set(hc, 0); View(mo, "hoist BEFORE, the platform down", HOIST_X + 60, 2 * OFF + 200, 40); }
		if (Seg(69)) {}
		if (At()) { ScriptHang(ten, 127); h.carried = null; View(mo, "hoist THEN through 127 into BEFORE: the lever and targets", HOIST_X + 96, OFF + 192, 180); }
		if (Seg(69)) {}
		if (At()) { Set(dc, 1); View(mo, "drip NOW, valve open THEN: full", DRIP_X + 60, 100, 45); }
		if (Seg(69)) {}
		if (At()) View(mo, "drip THEN: dry", DRIP_X + 60, OFF + 100, 45);
		if (Seg(69)) {}
		if (At())
		{
			let imp = Actor.Spawn("DoomImp", (PEN_X + 256, 2 * OFF + 200, 0));
			imp.DamageMobj(null, null, 1000, 'None');
			View(mo, "company THEN: the old corpse of an imp killed BEFORE", PEN_X + 256, OFF + 60, 90, 20);
		}
		if (Seg(69)) {}
		if (At()) View(mo, "company NOW: the same imp's old corpse", PEN_X + 256, 60, 90, 20);
		if (Seg(69)) {}
		if (At()) View(mo, "company BEFORE: the imp as it fell", PEN_X + 256, 2 * OFF + 60, 90, 20);
		if (Seg(69)) {}
		if (At()) View(mo, "the yard BEFORE, from its west end", -150, 2 * OFF + 120, 5);
		if (Seg(69)) {}
		if (At()) Console.Printf("AJARTEST beforeViews=%d", viewN);
	}

	// === the old door lab: helpers =====================================================================
	// the old door in frame id: of door d, so many years old, open onto its far side `far` at that time, in its look
	bool OldOf(int id, AjarDoor d, int years, int far)
	{
		AjarFrame f = F(id);
		AjarDoor o = f ? f.door : null;
		if (!o || !o.IsOld() || o.oldOf != d || o.oldYears != years || o.args[0] != far || !Open(far) || !Open(id)) return false;
		string spr = String.Format("%s%d", years > 10 ? "AJQ" : "AJO", d.Colour());
		return o.sprite == Actor.GetSpriteIndex(spr) && !o.bInvisible && o.Label() == d.Label()
			&& FarFace(far) == String.Format("AJTF%d%s", d.Colour(), years > 10 ? "Q" : "O");
	}
	// the flat of the recess of far side id: the colour's surround, aged with an old door open onto it
	string FarFace(int id)
	{
		Line l = h.FindLine(id);
		for (int k = 0; l && k < 2; k++)
		{
			Sector s = k ? l.backsector : l.frontsector;
			string n = s ? TexMan.GetName(s.GetTexture(Sector.floor)) : "";
			if (n.Left(4) ~== "AJTF") return n;
		}
		return "-";
	}
	int OldCount()
	{
		int n = 0;
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.IsOld()) n++;
		return n;
	}
	string Olds()
	{
		string s = "old doors:";
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
			if (d.IsOld()) s = s .. String.Format(" %s in %d (%d years, onto %d)", d.Label(), d.frame ? d.frame.args[0] : 0, d.oldYears, d.args[0]);
		s = s .. String.Format("; red in %d, blue in %d; carried %s", red.frame ? red.frame.args[0] : 0, blue.frame ? blue.frame.args[0] : 0, Carried());
		return s;
	}
	// a door put back leaning where the map put it, out of the hands (belt.zs's BeltPutBack)
	void PutBack(AjarDoor d)
	{
		if (d.frame) ScriptUnhang(d);
		d.carried = false;
		d.SetOrigin(d.SpawnPoint, false);
		d.angle = 90;
		d.Show();
		if (h.carried == d) h.carried = null;
	}
	// a door in the hands, by script (what was in them put back)
	void InHand(AjarDoor d)
	{
		if (h.carried && h.carried != d) PutBack(h.carried);
		if (d.frame) ScriptUnhang(d);
		d.carried = true;
		d.Hide();
		h.carried = d;
	}
	bool InBox(Actor a, int t, double x1, double y1, double x2, double y2)
	{
		double y = a.pos.y - t * OFF;
		return TimeOf(a) == t && a.pos.x > x1 && a.pos.x < x2 && y > y1 && y < y2;
	}
	bool InStrongroom(Actor a, int t) { return InBox(a, t, STRONG_X, 0, STRONG_X + 512, 512); }

	// === MODE=5: the rule ===============================================================================
	void Rule(Actor mo)
	{
		// BLUE hangs BEFORE from the first tic, so its old selves THEN and NOW do too
		if (At()) Check("blueHangsBeforeFromTheStart", blue.frame == F(150) && OldOf(130, blue, 10, 222) && OldOf(110, blue, 50, 202) && Open(242) && OldCount() == 2, Olds());
		// RED hung BEFORE in 141: an old RED THEN in 121 (ten years) and NOW in 101 (fifty), each onto RED's far side then
		if (At()) { Pose(mo, 200, 140, 270); red.Used(mo); }
		if (At()) { Pose(mo, 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("redHungBeforeSeenThenAndNow", red.frame == F(141) && OldOf(121, red, 10, 221) && OldOf(101, red, 50, 201) && Open(241) && !h.carried && OldCount() == 4, Olds() .. "; " .. Fars());
		if (At()) Through(mo, 128, 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("throughOldRedNow", InCorridor(mo, 0), Where(mo)); }
		if (At()) Through(mo, 128, OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("throughOldRedThen", InCorridor(mo, 1), Where(mo)); }
		if (At()) Through(mo, 192, OFF - 120, 270);
		if (Seg(30) && tt == 29)
		{
			Keys();
			Check("backThroughOldRedThen", TimeOf(mo) == AjarThen.T_THEN && abs(mo.pos.x - 128) < 6 && mo.pos.y > OFF + 380 && mo.pos.y < OFF + 512 && Facing(mo, 270), Where(mo));
		}
		// rusted to its frame: USE with empty hands, NOW and THEN
		if (At()) { h.said = ""; Pose(mo, 128, 470, 90); PressUse(mo); }
		if (At()) Check("rustedNow", Said("Rusted to its frame.") && !h.carried && OldOf(101, red, 50, 201), h.said);
		if (At()) { h.said = ""; Pose(mo, 128, OFF + 470, 90); PressUse(mo); }
		if (At()) Check("rustedThen", Said("Rusted to its frame.") && !h.carried && OldOf(121, red, 10, 221), h.said);
		// BLUE taken down BEFORE: its old selves are gone at once
		if (At()) { Pose(mo, OLD_X + 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("blueDownItsOldSelvesGone", h.carried == blue && !F(130).door && !F(110).door && !Open(202) && !Open(222) && !Open(242) && OldCount() == 2, Olds());
		// ... and USE with a door in hand: rusted, nothing swapped
		if (At()) { h.said = ""; Pose(mo, 128, 470, 90); PressUse(mo); }
		if (At()) Check("rustedWithADoorInHand", Said("Rusted to its frame.") && h.carried == blue && OldOf(101, red, 50, 201), h.said);
		if (At()) Check("thiefAndNailerLeaveIt", F(101).door.Stuck() && F(121).door.Stuck() && !red.Stuck());
		// the swap BEFORE: BLUE for RED in 141, the old doors with it
		if (At()) { Pose(mo, 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("swapMovesTheOldDoors", blue.frame == F(141) && h.carried == red && OldOf(121, blue, 10, 222) && OldOf(101, blue, 50, 202) && OldCount() == 2 && !Open(201) && !Open(221), Olds() .. "; " .. Fars());
		if (At()) PressUse(mo);
		if (At()) Check("swappedBack", red.frame == F(141) && h.carried == blue && OldOf(121, red, 10, 221) && OldOf(101, red, 50, 201) && OldCount() == 2, Olds());

		// rule 4: no colour door into a frame while a later time has a door in it. A colour door: RED NOW in 102
		if (At()) { ScriptHang(red, 102); h.carried = blue; }
		if (At()) { h.said = ""; Pose(mo, 384, OFF + 470, 90); PressUse(mo); }
		if (At()) Check("refusedColourDoorLater", h.carried == blue && !F(122).door && Said("A door hangs in this frame at a later time.\nThe BLUE door will not hang in it.") && OldCount() == 0, h.said .. "; " .. Olds());
		if (At()) { h.said = ""; Pose(mo, 384, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("refusedColourDoorTwoTimesLater", h.carried == blue && !F(142).door && Said("A door hangs in this frame at a later time."), h.said);
		// a clocked leaf: the clocked door hung NOW in 101 has its leaf THEN in 121; BLUE into 141 BEFORE
		if (At()) { ScriptHang(clocked, 101); h.carried = blue; h.said = ""; Pose(mo, 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("refusedClockedLeafLater", h.carried == blue && !F(141).door && shadow.frame == F(121) && Said("A door hangs in this frame at a later time."), h.said .. "; " .. DoorsSaid());
		// an old door: RED hung THEN in 121 (by script), its old self NOW in 101 keeps BLUE out of 141 first
		if (At()) { ScriptUnhang(clocked); PutBack(clocked); ScriptHang(red, 121); h.carried = blue; }
		if (At()) { h.said = ""; Pose(mo, 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("refusedOldDoorLater", h.carried == blue && !F(141).door && h.OldBlocker(blue, F(141)) == F(101) && OldOf(101, red, 40, 201) && Said("A door hangs in this frame at a later time."), h.said .. "; " .. Olds());
		// RED hung THEN in play in 123, which has no BEFORE: an old RED NOW in 103 only, forty years old
		if (At()) { PutBack(blue); ScriptUnhang(red); }
		if (At()) Check("redDownFrom121OldGone", h.carried == red && OldCount() == 0 && !F(101).door, Olds());
		if (At()) { Pose(mo, 470, OFF + 256, 0); PressUse(mo); }
		if (At()) Check("redHungThenSeenNowOnly", red.frame == F(123) && OldOf(103, red, 40, 201) && OldCount() == 1 && Open(221) && !Open(241), Olds() .. "; " .. Fars());
		if (At()) Through(mo, 452, 256, 0);
		if (Seg(24) && tt == 23) { Keys(); Check("throughOldRedNowIn103", InCorridor(mo, 0), Where(mo)); }
		// the clocked door's own refusal covers an old door in its twin: THEN at 123, RED's old self NOW in 103
		if (At()) { InHand(clocked); h.said = ""; Pose(mo, 470, OFF + 256, 0); PressUse(mo); }
		if (At()) Check("clockedRefusedOldDoorInTwin", h.carried == clocked && red.frame == F(123) && OldOf(103, red, 40, 201) && Said("At the other time a door hangs in this frame.\nThe clocked door"), h.said);
		// taken down at its own time: never there later, at once
		if (At()) { PutBack(clocked); Pose(mo, 470, OFF + 256, 0); PressUse(mo); }
		if (At()) Check("takenDownNeverThereLater", h.carried == red && !F(103).door && !F(123).door && OldCount() == 0 && !Open(201) && ShutRed(201)
			&& FarFace(201) == "AJTF1" && FarFace(221) == "AJTF1", Olds() .. "; " .. Fars() .. "; " .. FarFace(201));

		// the strongroom NOW in play: RED left BEFORE in its free frame 144 is an old door into it THEN (124) and NOW (104)
		if (At()) { InHand(red); Pose(mo, STRONG_X + 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("redLeftIn144", red.frame == F(144) && OldOf(124, red, 10, 221) && OldOf(104, red, 50, 201) && !h.carried, Olds());
		if (At()) Through(mo, 192, -120, 270);
		if (Seg(30) && tt == 29) { Keys(); Check("strongroomNowInPlay", InStrongroom(mo, 0), Where(mo)); WalkTo(STRONG_X + 256, 256); }
		if (Seg(60) && tt == 59) Check("megasphereNow", mo.health >= 200, String.Format("health %d", mo.health));
		// ... and the clocked door carried into the strongroom THEN through RED's far side THEN, hung in 125, on to NOW
		if (At()) { InHand(clocked); Through(mo, 192, OFF - 120, 270); }
		if (Seg(30) && tt == 29) { Keys(); Check("clockedCarriedIntoStrongroomThen", InStrongroom(mo, 1) && h.carried == clocked, Where(mo)); }
		if (At()) { Pose(mo, STRONG_X + 384, OFF + 470, 90); PressUse(mo); }
		if (At()) Check("clockedHungIn125", clocked.frame == F(125) && shadow.frame == F(105), DoorsSaid());
		if (At()) Through(mo, STRONG_X + 384, OFF + 452, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("strongroomNowByTheClockedDoor", InStrongroom(mo, 0), Where(mo)); }
		FollowOld(mo);
	}

	// A monster NOW follows the player through an old door (after the rest: it takes as long as it takes, as
	// Follow's trials). BLUE back in 150 BEFORE, through old BLUE NOW in 110 from bay 7 into the dry room of bay 8
	// (BLUE's far side 202), the bay's own imp behind.
	Actor oImp;
	int oDone, oStart, oSeen, oIn, oCrossed;
	void FollowOld(Actor mo)
	{
		if (tic < cur) return;
		if (oDone) { cur = tic + 100; if (oDone == 1) { oDone = 2; cur = tic - 2; } return; }
		cur = tic + 100;
		if (!oStart)
		{
			oStart = tic;
			h.carried = null;
			ScriptHang(blue, 150);
			let it = ThinkerIterator.Create("DoomImp");
			Actor a;
			while (a = Actor(it.Next())) if (InBox(a, 0, OLD_X, 0, OLD_X + 512, 512)) oImp = a;
			Check("theImpNow", oImp != null && OldOf(110, blue, 50, 202), Olds());
			mo.player.cheats &= ~CF_NOTARGET;
			Pose(mo, OLD_X + 128, 300, 90);
			if (oImp) { oImp.bAmbush = false; oImp.target = mo; oImp.SetState(oImp.SeeState); }
		}
		int st = tic - oStart;
		if (st == 20) Through(mo, OLD_X + 128, 494, 90);         // into 110, out of 202 in the dry room
		if (st == 44) { Keys(); WalkTo(WATER_X + 400, 120); }
		bool dry = oImp && InBox(oImp, 0, WATER_X + 288, 0, WATER_X + 512, 512);
		if (oImp && InBox(oImp, 0, OLD_X, 0, OLD_X + 512, 512)) oSeen = 1;
		if (dry && oSeen == 1) { oCrossed++; oSeen = 2; }
		if (dry) oIn++; else oIn = 0;
		if (oImp && st % 30 == 0) Info(String.Format("follow t+%d imp %s; player %s", st, AjarDoorTrace.Of(oImp), Where(mo)));
		if ((oIn >= 70 && st > 60) || st >= 1050 || !oImp || oImp.health <= 0)
		{
			Check("impNowThroughOldBlue", oImp && oImp.health > 0 && oIn >= 70 && oCrossed == 1 && InBox(mo, 0, WATER_X + 288, 0, WATER_X + 512, 512),
				String.Format("t+%d, in the dry room %d tics; %s", st, oIn, oImp ? AjarDoorTrace.Of(oImp) : "no imp"));
			if (oImp) { oImp.ClearCounters(); oImp.Destroy(); }
			walking = false;
			Keys();
			mo.player.cheats |= CF_NOTARGET;
			oDone = 1;
		}
	}

	// === MODE=6: water through an old door ===============================================================
	int dryAt;
	void Water(Actor mo)
	{
		let tank = th.wh.BasinOfTag(42), dry = th.wh.BasinOfTag(43);
		let vc = Cause(14);
		if (At()) Check("waterDryAtStart", tank && dry && !tank.Wet() && !dry.Wet() && vc.setting == 0);
		// BLUE taken BEFORE from 150 and hung BEFORE in 151: old BLUE NOW in 111 (in the tank), onto 202 (in the dry room)
		if (At()) { Pose(mo, OLD_X + 128, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) { Pose(mo, WATER_X + 112, 2 * OFF + 470, 90); PressUse(mo); }
		if (At()) Check("blueIn151", blue.frame == F(151) && OldOf(131, blue, 10, 222) && OldOf(111, blue, 50, 202), Olds());
		// the valve THEN, on the tank's west wall: the tank NOW fills, and the dry room through old BLUE
		if (At()) { Pose(mo, WATER_X + 32, OFF + 320, 180); PressUse(mo); fullAt = -1; dryAt = -1; }
		if (Seg(700))
		{
			if (tt == 0) Check("valveOpenThen", vc.setting == 1);
			if (fullAt < 0 && tank.w >= 95.5) fullAt = tt;
			if (dryAt < 0 && dry.w >= 95.5) dryAt = tt;
			if (tt % 70 == 0) Info(String.Format("t+%d tank %.2f, dry room %.2f", tt, tank.w, dry.w));
			if (tt == 699)
				Check("waterStandsInBoth", fullAt >= 0 && dryAt >= 0 && abs(tank.w - 96) < 0.01 && abs(dry.w - tank.w) < 0.5,
					String.Format("tank full in %d tics, the dry room in %d; %.2f / %.2f", fullAt, dryAt, tank.w, dry.w));
		}
		if (At()) Pose(mo, WATER_X + 400, 200, 90);
		if (Seg(3) && tt == 2) Check("dryRoomNowUnderWater", mo.waterlevel >= 2 && TimeOf(mo) == AjarThen.T_NOW, String.Format("waterlevel %d", mo.waterlevel));
		if (At()) Pose(mo, WATER_X + 400, OFF + 200, 90);
		if (Seg(3) && tt == 2) Check("dryRoomThenDry", mo.waterlevel == 0 && TimeOf(mo) == AjarThen.T_THEN);
		// BLUE taken down BEFORE: the old door is gone, and with it the link; what came through stays (water.zs moves
		// water through a hung door and keeps no history)
		if (At()) { Pose(mo, WATER_X + 112, 2 * OFF + 470, 90); PressUse(mo); }
		if (Seg(70) && tt == 69)
			Check("oldDoorGoneTheWaterStays", !F(111).door && h.carried == blue && abs(dry.w - 96) < 0.5 && abs(tank.w - 96) < 0.01,
				String.Format("tank %.2f, dry room %.2f", tank.w, dry.w));
	}
}
