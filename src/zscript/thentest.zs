// The then and now lab's checks (map THEN, tools/map_then.py; then.zs;
// PLAN.md, "The then and now lab"). MAP=THEN MODE=n tools/smoke.sh.
// THEN is NOW + (0, 4096). Frames (NOW / THEN): hall W 101/121, M 102/122,
// E 103/123 (north walls), belt 104/124, company 105/125, drip 106/126 (west
// walls), beam 107/127 (north wall); 131 THEN only (W's west wall). RED's far
// side 201 NOW, 221 THEN (the corridor's south wall: a colour door joins
// places, never times). Causes: 11 the belt, 12 the drip, 13 the beam. Bays:
// hall x 0, belt 896, drip 1536, beam 2176, company 2880.
//   1 the door and the way round; 2 the drip; 3 the belt; 4 the beam;
//   5 company; 6 views (tools/smoke_THEN_6.cfg shoots at about 50 + 70 n).

class ThenTest : EventHandler
{
	const OFF = 4096;
	const BELT_X = 896; const DRIP_X = 1536; const BEAM_X = 2176; const PEN_X = 2880;
	const WALKKEY = 0x1900;
	int tic, cur, tt;
	int checks, fails;
	AjarHandler h;
	AjarThenHandler th;
	AjarDoor clocked, shadow, red;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "THEN"; }

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
	bool InThen(Actor mo) { return th.when.InThen(mo.pos.xy); }
	string Where(Actor mo) { return String.Format("(%.1f,%.1f,%.1f) angle %.1f %s", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, InThen(mo) ? "THEN" : "NOW"); }
	bool Facing(Actor mo, double ang) { return abs(Actor.DeltaAngle(mo.angle, ang)) < 1; }
	string Carried() { return h.carried ? h.carried.Label() .. (h.carried == clocked ? "" : h.carried.IsShadow() ? "(shadow!)" : "") : "-"; }
	AjarFrame F(int id) { return h.FindFrame(id); }
	Sector SectorAt(double x, double y) { return level.PointInSector((x, y)); }
	double FZ(double x, double y) { Sector s = SectorAt(x, y); return s.floorplane.ZatPoint(s.centerspot); }
	double CZ(double x, double y) { Sector s = SectorAt(x, y); return s.ceilingplane.ZatPoint(s.centerspot); }
	AjarThenCause Cause(int tid) { return th.FindCause(tid); }
	string Around(Actor mo)
	{
		string r = "";
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a != mo && (a.pos.xy - mo.pos.xy).Length() < 80) r = r .. String.Format(" [%s (%.0f,%.0f,%.0f) r%.0f h%.0f solid %d]", a.GetClassName(), a.pos.x, a.pos.y, a.pos.z, a.radius, a.height, a.bSolid);
		return r;
	}
	bool Near(double a, double b) { return abs(a - b) < 0.05; }
	// a portal line open (it leads somewhere), or shut and showing RED's shut door
	bool Open(int id) { Line l = h.FindLine(id); return l && !(l.flags & Line.ML_BLOCKING); }
	bool ShutRed(int id) { Line l = h.FindLine(id); return l && (l.flags & Line.ML_BLOCKING) && TexMan.GetName(l.sidedef[0].GetTexture(Side.mid)) ~== "AJDR1"; }
	string Fars() { return String.Format("red args[0] %d ownFar %d; 201 %s, 221 %s", red.args[0], red.ownFar, Open(201) ? "open" : ShutRed(201) ? "shut" : "?", Open(221) ? "open" : ShutRed(221) ? "shut" : "?"); }
	bool InCorridor(Actor mo, bool then) { double y = mo.pos.y - (then ? OFF : 0); return InThen(mo) == then && y > -176 && y < -60 && abs(mo.pos.x - 192) < 6 && Facing(mo, 90); }
	string Steps()
	{
		string s = "steps";
		for (int x = 232; x < 520; x += 48) s = s .. String.Format(" %.3f", FZ(BELT_X + x, 384));
		return s;
	}

	// --- the player's controls: keys "held" for this tic, as watertest.zs does ----------------------
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
	// a real USE: the engine's own CheckUse, looking where the player looks
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}
	// a hitscan of the player's, along where the player looks (the engine's own, through portals)
	void Shoot(Actor mo, double ang)
	{
		mo.angle = ang;
		mo.pitch = 0;
		mo.LineAttack(ang, 4096, 0, 10, 'Hitscan', "BulletPuff");
	}
	// aim at a point beyond the frame line `src` that leads to `dst`
	double AimThrough(Actor mo, int src, int dst, Vector2 p)
	{
		Vector2 img = AjarSight.ImageThrough(h.FindLine(src), h.FindLine(dst), p);
		return VectorAngle(img.x - mo.pos.x, img.y - mo.pos.y);
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
				if (d.IsShadow()) shadow = d;
				else if (d.IsClocked()) clocked = d;
				else if (d.args[1] == 1) red = d;
			}
			mo.player.cheats |= CF_GODMODE;
			if (mode != 5) mo.player.cheats |= CF_NOTARGET;
			Info(String.Format("causes %d, cause sectors %d, emitters %d, belts %d, targets %d, hidden %d; clocked %d shadow %d red %d",
				th.causes.Size(), th.secIdx.Size(), th.emitters.Size(), th.belts.Size(), th.targets.Size(), th.hiddenItems.Size(),
				clocked != null, shadow != null, red != null));
		}
		cur = 2;
		if (mode == 1) Door(mo);
		else if (mode == 2) Drip(mo);
		else if (mode == 3) Belt(mo);
		else if (mode == 4) Beam(mo);
		else if (mode == 5) Company(mo);
		else if (mode == 6) Views(mo);
		Drive(mo);
		if (mode != 6 && tic == cur + 2) Console.Printf("AJARTEST thenDone=1 checks=%d failed=%d", checks, fails);
	}

	// === MODE=1: the clocked door, the twinless frame, RED across, the way round =====================
	void Door(Actor mo)
	{
		// NOW the rubble holds: from W east along y 256
		if (At()) { Check("nowMusicAtStart", th.musicThen == 0, String.Format("changes %d", th.musicChanges)); Pose(mo, 128, 256, 0); Keys(WALKKEY); }
		if (Seg(50) && tt == 49) { Keys(); Check("rubbleHoldsNow", mo.pos.x < 256 && mo.pos.x > 200, Where(mo)); }
		// take the clocked door; hang it in 101 by a real USE
		if (At()) { clocked.Used(mo); Check("tookClocked", h.carried == clocked, h.said); }
		if (At()) Pose(mo, 128, 470, 90);
		if (At()) PressUse(mo);
		if (At())
		{
			let f = F(101), t = F(121);
			Check("hungNow", clocked.frame == f && f.door == clocked, h.said);
			Check("twinShowsIt", shadow.frame == t && t.door == shadow && !shadow.bInvisible && shadow.sprite == Actor.GetSpriteIndex('AJDT'),
				String.Format("shadow at (%.0f,%.0f) invisible %d", shadow.pos.x, shadow.pos.y, shadow.bInvisible));
			Check("linkedBothWays", clocked.args[0] == 121 && shadow.args[0] == 101);
			Check("handsEmpty", h.carried == null);
		}
		// walk through: out of the same wall THEN, facing into the room
		if (At()) Keys(WALKKEY);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("walkedIntoThen", InThen(mo) && mo.pos.y < OFF + 512 && mo.pos.y > OFF + 380 && abs(mo.pos.x - 128) < 4, Where(mo));
			Check("arrivedFacingIn", Facing(mo, 270), Where(mo));
			Check("thenMusicThen", th.musicThen == 1, String.Format("changes %d", th.musicChanges));
		}
		// a door carried to either frame of the hung clocked door is swapped for it (2026-11-26): both leaves come
		// down, the carried door hangs in that one frame, at that time, and the clocked door is in hand
		if (At()) { Pose(mo, 200, 96, 270); red.Used(mo); }
		if (At()) { Pose(mo, 128, OFF + 470, 90); PressUse(mo); }
		if (At()) Check("swapInForClockedThen", h.carried == clocked && F(121).door == red && !F(101).door && !clocked.frame && !shadow.frame
			&& red.args[0] == 221 && Open(221) && ShutRed(201) && h.said == "You swap the clocked door for the RED one.", Fars() .. "; " .. h.said);
		if (At()) { Pose(mo, 128, OFF + 452, 90); Keys(WALKKEY); }
		if (Seg(24) && tt == 23) { Keys(); Check("swappedRedThenLeadsThen", InCorridor(mo, true), Where(mo)); }
		if (At()) { Pose(mo, 128, OFF + 470, 90); PressUse(mo); }                    // the clocked door back for RED
		if (At()) Check("clockedSwappedBackThen", h.carried == red && F(121).door && F(121).door.IsClocked() && F(101).door && F(101).door.IsClocked() && ShutRed(201) && ShutRed(221), h.said);
		if (At()) { Pose(mo, 128, 470, 90); PressUse(mo); }
		if (At()) Check("swapInForClockedNow", h.carried == clocked && F(101).door == red && !F(121).door && red.args[0] == 201 && Open(201) && ShutRed(221), Fars() .. "; " .. h.said);
		if (At()) { Pose(mo, 128, 452, 90); Keys(WALKKEY); }
		if (Seg(24) && tt == 23) { Keys(); Check("swappedRedNowLeadsNow", InCorridor(mo, false), Where(mo)); }
		if (At()) { Pose(mo, 128, 470, 90); PressUse(mo); }                          // the clocked door back in 101
		if (At()) Check("clockedSwappedBackNow", h.carried == red && clocked.frame && shadow.frame && F(101).door && F(121).door, h.said);
		if (At()) { h.DropDoor(red, mo); h.carried = null; red.SetOrigin((200, 96, 0), false); red.angle = 90; Pose(mo, 128, OFF + 470, 90); }
		// take it THEN: both frames empty, the door in hand THEN
		if (At()) PressUse(mo);
		if (At())
		{
			Check("tookItThen", h.carried == clocked && !F(101).door && !F(121).door && !clocked.frame && !shadow.frame && shadow.bInvisible, h.said);
			Check("framesShutAgain", h.FindLine(101).flags & Line.ML_BLOCKING && h.FindLine(121).flags & Line.ML_BLOCKING);
		}
		// the frame with no twin refuses it
		if (At()) { Pose(mo, 60, OFF + 256, 180); PressUse(mo); }
		if (At()) Check("twinlessRefuses", h.carried == clocked && !F(131).door, h.said);
		// the way round THEN: W to M (whole THEN), and the gate holds
		if (At()) WalkTo(400, OFF + 256);
		if (Seg(90) && tt == 89) Check("thenWholeWtoM", mo.pos.x > 380 && InThen(mo), Where(mo));
		if (At()) Keys(WALKKEY);              // (facing east, at the gate's gap)
		if (Seg(40) && tt == 39) { Keys(); Check("gateHoldsThen", mo.pos.x < 512 && mo.pos.x > 470, Where(mo)); }
		// hang it in 122 (M, THEN), walk through: NOW in M
		if (At()) WalkTo(400, OFF + 470);
		if (Seg(60) && tt == 59) { mo.angle = 90; PressUse(mo); }
		if (At()) Check("hungThen", clocked.frame == F(122) && shadow.frame == F(102) && !clocked.bInvisible && !shadow.bInvisible, h.said);
		if (At()) Keys(WALKKEY);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("walkedIntoNow", !InThen(mo) && mo.pos.x > 288 && mo.pos.x < 512 && mo.pos.y > 380, Where(mo));
			Check("arrivedFacingInNow", Facing(mo, 270), Where(mo));
		}
		// NOW from M to E through the gap: the far end, two hangings
		if (At()) WalkTo(470, 256);
		if (Seg(60)) {}
		if (At()) WalkTo(640, 256);
		if (Seg(60) && tt == 59) Check("reachedFarEnd", !InThen(mo) && mo.pos.x > 560, Where(mo) .. String.Format(" health %d", mo.health));

		// RED, carried through the clocked door and hung THEN, opens onto its far side THEN (2026-11-26: a
		// colour door joins places, never times)
		if (At()) { Check("redFarSidesShutAtStart", red.args[0] == 201 && ShutRed(201) && ShutRed(221), Fars()); Pose(mo, 200, 96, 270); red.Used(mo); }
		if (At()) Pose(mo, 400, 440, 90);
		if (At()) Keys(WALKKEY);
		if (Seg(24) && tt == 23) { Keys(); Check("carriedRedIntoThen", InThen(mo) && h.carried == red, Where(mo)); }
		if (At()) WalkTo(60, OFF + 256);
		if (Seg(100) && tt == 99) { Info("walked to " .. Where(mo)); Pose(mo, 60, OFF + 256, 180); PressUse(mo); }
		if (At()) Check("redHungThen", red.frame == F(131), h.said);
		if (At()) Check("redThenOpensThenNowShut", red.args[0] == 221 && Open(221) && ShutRed(201), Fars());
		if (At()) Keys(WALKKEY);
		if (Seg(24) && tt == 23)
		{
			Keys();
			Check("redLeadsThen", InCorridor(mo, true), Where(mo));
		}
		if (At()) { mo.angle = 270; Keys(WALKKEY); }
		if (Seg(30) && tt == 29)
		{
			Keys();
			Check("redBackToThen", InThen(mo) && mo.pos.x > 0 && mo.pos.x < 140 && abs(mo.pos.y - (OFF + 256)) < 6 && Facing(mo, 0), Where(mo));
		}
		// the clocked door does not hang where its twin holds another door: RED in 102 THEN... (122 holds it; use 101/121)
		if (At()) { Pose(mo, 60, OFF + 256, 180); PressUse(mo); }                 // RED down from 131
		if (At()) { Pose(mo, 128, 470, 90); PressUse(mo); }                       // RED into 101 NOW
		if (At()) { Pose(mo, 400, OFF + 470, 90); PressUse(mo); }                 // the clocked door down from 122
		if (At()) { Pose(mo, 128, OFF + 470, 90); PressUse(mo); }                 // ... and tried in 121
		if (At()) Check("refusedWhereTwinHoldsAnother", h.carried == clocked && red.frame == F(101) && !F(121).door, h.said);
		// the music lever (NOW, W's west wall): off, then THEN keeps NOW's music; on again
		if (At()) { Pose(mo, 30, 416, 180); PressUse(mo); }
		if (At()) { Check("musicLeverOff", th.musicOff, h.said); Pose(mo, 128, OFF + 256, 0); }
		if (Seg(3) && tt == 2) Check("offKeepsNowMusic", th.musicThen == 0 && InThen(mo));
		if (At()) { Pose(mo, 30, 416, 180); PressUse(mo); }
		if (At()) { Check("musicLeverOn", !th.musicOff, h.said); Pose(mo, 128, OFF + 256, 0); }
		if (Seg(3) && tt == 2) Check("onFollowsAgain", th.musicThen == 1, String.Format("changes %d", th.musicChanges));

		// --- a colour door joins places, never times (2026-11-26). RED hangs in 101 NOW, the clocked door
		// is in hand. RED NOW: its far side NOW open, THEN shut; through it into the corridor NOW
		if (At()) Check("redNowOpensNowThenShut", red.frame == F(101) && red.args[0] == 201 && Open(201) && ShutRed(221), Fars());
		if (At()) { Pose(mo, 128, 452, 90); Keys(WALKKEY); }
		if (Seg(24) && tt == 23) { Keys(); Check("redNowLeadsNow", InCorridor(mo, false), Where(mo)); }
		// the clocked door swapped in for RED in 101: RED in hand, both its far sides shut
		if (At()) { Pose(mo, 128, 470, 90); PressUse(mo); }
		if (At()) Check("redDownBothShut", h.carried == red && clocked.frame == F(101) && shadow.frame == F(121) && red.args[0] == 201 && ShutRed(201) && ShutRed(221), Fars() .. "; " .. h.said);
		// carried through the clocked door into THEN and hung in 131 (no twin: a frame at its own time)
		if (At()) { Pose(mo, 128, 452, 90); Keys(WALKKEY); }
		if (Seg(24) && tt == 23) { Keys(); Check("redCarriedIntoThenAgain", InThen(mo) && h.carried == red, Where(mo)); }
		if (At()) { Pose(mo, 60, OFF + 256, 180); PressUse(mo); }
		if (At()) Check("redInTwinlessFrameOpensThen", red.frame == F(131) && red.args[0] == 221 && Open(221) && ShutRed(201), Fars());
		// the clocked door taken down THEN: RED hung THEN joins nothing across the times
		if (At()) { Pose(mo, 128, OFF + 470, 90); PressUse(mo); }
		if (Seg(3) && tt == 2)
			Check("redThenIsNoLink", h.carried == clocked && !clocked.frame && red.frame == F(131) && !th.Linked() && !th.wasLinked, Fars());
		// RED taken down THEN (the clocked door put down first) and hung NOW again: NOW
		if (At()) { h.DropDoor(clocked, mo); h.carried = null; Pose(mo, 60, OFF + 256, 180); PressUse(mo); }
		if (At()) Check("redDownThenIsItsOwn", h.carried == red && !red.frame && red.args[0] == 201 && red.ownFar == 201 && ShutRed(201) && ShutRed(221), Fars());
		if (At()) { Pose(mo, 128, 470, 90); PressUse(mo); }
		if (At()) Check("redNowAgainOpensNow", red.frame == F(101) && red.args[0] == 201 && Open(201) && ShutRed(221), Fars());
		if (At()) { Pose(mo, 128, 452, 90); Keys(WALKKEY); }
		if (Seg(24) && tt == 23) { Keys(); Check("redNowAgainLeadsNow", InCorridor(mo, false), Where(mo)); }
	}

	// === MODE=2: the drip ============================================================================
	int fullAt, dryAt;
	double floatZ;
	void Drip(Actor mo)
	{
		let c = Cause(12);
		let b = th.wh.BasinOfTag(41);
		if (At()) { Check("tankDryAtStart", b && !b.Wet() && c.setting == 0, String.Format("w %.2f", b ? b.w : -1)); }
		// NOW's dead lever does nothing
		if (At()) { Pose(mo, DRIP_X + 470, 320, 0); PressUse(mo); }
		if (Seg(10) && tt == 9) Check("deadLeverNow", c.setting == 0 && !b.Wet());
		// THEN: open the valve by its lever
		if (At()) { Pose(mo, DRIP_X + 470, OFF + 320, 0); PressUse(mo); fullAt = -1; }
		if (Seg(140))
		{
			if (tt == 0) Check("valveOpen", c.setting == 1);
			if (fullAt < 0 && b.w >= 95.5) fullAt = tt;
			if (tt % 35 == 0) Info(String.Format("drip t+%d: water %.1f", tt, b.w));
			if (tt == 139)
			{
				Check("fullWithin80", fullAt >= 0 && fullAt <= 80, String.Format("%d tics", fullAt));
				Check("standsAt96", abs(b.w - 96) < 0.01, String.Format("w %.2f", b.w));
				Check("thenTankDry", mo.waterlevel == 0 && InThen(mo));
			}
		}
		// the player in the tank: floats up, gets onto the ledge
		if (At()) Pose(mo, DRIP_X + 256, 400, 90);
		if (Seg(100))
		{
			if (tt == 1) Check("underWater", mo.waterlevel == 3, String.Format("waterlevel %d", mo.waterlevel));
			if (tt == 99) { floatZ = mo.pos.z; Check("floatedUp", mo.pos.z > 40 && mo.waterlevel < 3, Where(mo) .. String.Format(" waterlevel %d", mo.waterlevel)); }
		}
		if (At()) { mo.angle = 90; Keys(WALKKEY, BT_JUMP); }
		if (Seg(70) && tt == 69)
		{
			Keys();
			Check("onLedge", mo.pos.y > 448 && abs(mo.pos.z - 112) < 1, Where(mo));
		}
		if (At()) WalkTo(DRIP_X + 256, 480);
		if (Seg(40) && tt == 39) Check("armourFromLedge", mo.CountInv("BlueArmor") > 0 || (BasicArmor(mo.FindInventory("BasicArmor")) && BasicArmor(mo.FindInventory("BasicArmor")).Amount >= 200));
		// shut it by shooting its target THEN: dry
		if (At()) { Pose(mo, DRIP_X + 300, OFF + 256, 0); Shoot(mo, 0); dryAt = -1; }
		if (Seg(120))
		{
			if (tt == 1) Check("targetShutsValve", c.setting == 0);
			if (dryAt < 0 && !b.Wet()) dryAt = tt;
			if (tt == 119) Check("dryWithin80", dryAt >= 0 && dryAt <= 80, String.Format("%d tics, w %.2f", dryAt, b.w));
		}
	}

	// === MODE=3: the belt and the heap ===============================================================
	Actor crate, pitItem;
	double crateX;
	void Belt(Actor mo)
	{
		let c = Cause(11);
		if (At())
		{
			pitItem = th.hiddenItems.Size() ? th.hiddenItems[0] : null;
			Check("heapFlatAtStart", c.setting == 0 && Near(FZ(BELT_X + 376, 384), 0) && Near(FZ(BELT_X + 280, 384), -48) && Near(FZ(BELT_X + 232, 384), -24), Steps());
			Check("pitItemThere", pitItem && !pitItem.bInvisible && pitItem.bSpecial);
			crate = Actor.Spawn("AjarCrate", (BELT_X + 100, OFF + 384, 0));
			crateX = crate.pos.x;
		}
		if (Seg(35) && tt == 34) Check("beltStandsThen", abs(crate.pos.x - crateX) < 1, String.Format("crate x %.1f", crate.pos.x));
		// the clocked door in 104 (NOW)
		if (At()) { clocked.Used(mo); Pose(mo, BELT_X + 60, 384, 180); PressUse(mo); }
		if (At()) Check("hungIn104", clocked.frame == F(104) && shadow.frame == F(124), h.said);
		// standing where the heap's third step rises, shoot the belt's target THEN through the door
		if (At()) { Pose(mo, BELT_X + 376, 384, 180); Shoot(mo, 180); crateX = crate.pos.x; }
		if (Seg(90))
		{
			if (tt == 1) Check("shotThroughDoorRunsBelt", c.setting == 1, Where(mo));
			if (tt == 30) Info(String.Format("rising: z %.1f", mo.pos.z));
			if (tt == 89)
			{
				Check("riddenUpUnhurt", abs(mo.pos.z - 72) < 0.5 && mo.health == 100 && Near(FZ(BELT_X + 376, 384), 72), Where(mo) .. " " .. Steps() .. String.Format(" health %d", mo.health));
				Check("pitCovered", Near(FZ(BELT_X + 280, 384), 24) && pitItem && pitItem.bInvisible && !pitItem.bSpecial);
				Check("beltRunsThen", crate.pos.x - crateX > 200, String.Format("crate moved %.1f", crate.pos.x - crateX));
				Check("raisedLooksCrate", TexMan.GetName(SectorAt(BELT_X + 376, 384).GetTexture(Sector.floor)) == "AJDSTOF");
			}
		}
		// climb the heap to the ledge: the megasphere
		if (At()) { Pose(mo, BELT_X + 150, 384, 0); WalkTo(BELT_X + 480, 384); }
		if (Seg(120))
		{
			if (tt % 10 == 0) Info(String.Format("climb %d: %s vel (%.2f,%.2f) floorz %.2f", tt, Where(mo), mo.vel.x, mo.vel.y, mo.floorz));
			if (tt == 119) Check("climbedToLedge", abs(mo.pos.z - 120) < 0.5 && mo.health == 200, Where(mo) .. String.Format(" health %d ", mo.health) .. Steps());
		}
		// the lever THEN stops it: the heap was never there, the pit is open
		if (At()) { Pose(mo, BELT_X + 470, OFF + 256, 0); PressUse(mo); }
		if (Seg(90) && tt == 89)
		{
			Check("leverStopsBelt", c.setting == 0);
			Check("heapGone", Near(FZ(BELT_X + 376, 384), 0) && Near(FZ(BELT_X + 424, 384), 0) && Near(FZ(BELT_X + 280, 384), -48), Steps());
			Check("pitItemBack", pitItem && !pitItem.bInvisible && pitItem.bSpecial);
			Check("flatLooksFloor", TexMan.GetName(SectorAt(BELT_X + 376, 384).GetTexture(Sector.floor)) != "AJDSTOF");
		}
		// into the pit for the berserk pack, and out
		if (At()) { Pose(mo, BELT_X + 150, 384, 0); Keys(WALKKEY); }       // east until the pit's far wall stops the player
		if (Seg(50) && tt == 49) { Keys(); Check("pitItemTaken", Near(mo.pos.z, -48) && mo.FindInventory("PowerStrength") != null, Where(mo) .. (pitItem ? String.Format(" item %s (%.0f,%.0f,%.1f) special %d invisible %d", pitItem.GetClassName(), pitItem.pos.x, pitItem.pos.y, pitItem.pos.z, pitItem.bSpecial, pitItem.bInvisible) : " item gone")); }
		// standing in the pit as the heap comes: lifted to the step, not crushed
		if (At()) th.SetCause(c, 1, null);
		if (Seg(90) && tt == 89) Check("pitLiftsPlayer", abs(mo.pos.z - 24) < 0.5 && mo.health > 0, Where(mo));
		if (At()) WalkTo(BELT_X + 150, 384);
		if (Seg(50) && tt == 49) Check("offTheHeap", Near(mo.pos.z, 0), Where(mo));
	}

	// === MODE=4: the beam and its holes ==============================================================
	void Beam(Actor mo)
	{
		let c = Cause(13);
		let em = th.emitters.Size() ? th.emitters[0] : null;
		double ax = BEAM_X - 8, bx = BEAM_X + 520;
		if (At()) Check("bothShutAtStart", CZ(ax, 256) == 0 && CZ(bx, 256) == 0 && em && em.dots.Size() == 0);
		// THEN: shoot A's target
		if (At()) { Pose(mo, BEAM_X + 320, OFF + 200, 270); Shoot(mo, 270); }
		if (Seg(90) && tt == 89)
		{
			Check("targetSetsA", c.setting == 1);
			Check("aOpensOnly", CZ(ax, 256) == 96 && CZ(bx, 256) == 0, String.Format("A %.0f B %.0f", CZ(ax, 256), CZ(bx, 256)));
			Check("beamShownThen", em.dots.Size() > 5 && Facing(em, 180), String.Format("%d dots", em.dots.Size()));
		}
		// NOW: through hole A into its closet, then stand in the hole
		if (At()) { Pose(mo, BEAM_X + 100, 256, 180); WalkTo(BEAM_X - 64, 256); }
		if (Seg(60) && tt == 59) Check("throughHoleA", mo.pos.x < BEAM_X - 16 && mo.FindInventory("RocketLauncher") != null, Where(mo));
		if (At()) Pose(mo, BEAM_X - 8, 256, 0);                                 // standing in the hole
		// the lever THEN steps it on to B while the player stands in A
		if (Seg(20) && tt == 19) { Info("in hole A: " .. Where(mo)); Cause(13).Activate(null); }
		if (Seg(150) && tt == 149)
		{
			Check("leverStepsToB", c.setting == 2);
			Check("holeWaitsForPlayer", CZ(ax, 256) == 96 && mo.pos.x > BEAM_X - 16 && mo.pos.x < BEAM_X, String.Format("A %.0f; ", CZ(ax, 256)) .. Where(mo));
			Check("oneAtATime", CZ(bx, 256) == 0, String.Format("B %.0f", CZ(bx, 256)));
			Check("beamAtB", Facing(em, 0));
		}
		if (At()) Pose(mo, BEAM_X + 256, 128, 0);
		if (Seg(160) && tt == 159)
		{
			Check("aShutWhenClear", CZ(ax, 256) == 0);
			Check("thenBOpens", CZ(bx, 256) == 96);
		}
		if (At()) WalkTo(BEAM_X + 576, 256);
		if (Seg(80) && tt == 79) Check("throughHoleB", mo.FindInventory("PlasmaRifle") != null, Where(mo));
		// off, from NOW through the clocked door in 107: the off target THEN
		if (At()) { Pose(mo, BEAM_X + 384, 470, 90); clocked.Used(mo); PressUse(mo); }
		if (At()) { Check("hungIn107", clocked.frame == F(107), h.said); }
		if (At()) { Pose(mo, BEAM_X + 384, 400, 90); Shoot(mo, AimThrough(mo, 107, 127, (BEAM_X + 384, OFF + 12))); }
		if (Seg(160) && tt == 159)
		{
			Check("offFromNowThroughDoor", c.setting == 0);
			Check("bothShut", CZ(ax, 256) == 0 && CZ(bx, 256) == 0 && em.dots.Size() == 0);
		}
	}

	// === MODE=5: company ============================================================================
	Array<Actor> pen;
	AjarThenCorpse old;
	Actor killed;
	Vector2 killedAt;
	void Company(Actor mo)
	{
		if (At())
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) pen.Push(a);
			Check("penHasThree", pen.Size() == 3, String.Format("%d", pen.Size()));
			clocked.Used(mo);
			Pose(mo, PEN_X + 60, 256, 180);
			PressUse(mo);
		}
		if (At()) Check("hungIn105", clocked.frame == F(105), h.said);
		// the gate's lever, by a real USE
		if (At()) Pose(mo, PEN_X + 128, 470, 90);
		if (At()) PressUse(mo);
		if (Seg(70) && tt == 69)
		{
			Check("gateOpen", CZ(PEN_X + 256, 520) > 64);
			for (int i = 0; i < pen.Size(); i++) { pen[i].target = mo; pen[i].SetState(pen[i].SeeState); }
			Pose(mo, PEN_X + 256, 380, 90);
		}
		// wait at the gate for them to come out, then step back to the frame and go through into THEN
		if (Seg(210) && tt % 35 == 0) Info(MonsterPlaces());
		if (At()) Pose(mo, PEN_X + 40, 256, 180);
		if (At()) Keys(WALKKEY);
		if (Seg(40) && tt == 39) { Keys(); Check("playerThen", InThen(mo), Where(mo)); }
		if (At()) WalkTo(PEN_X + 400, OFF + 100);
		if (Seg(500))
		{
			if (tt % 70 == 0) Info(MonsterPlaces());
			if (tt == 499) Check("monsterFollowsToThen", Count(true) >= 1, MonsterPlaces());
		}
		// one killed THEN: its old corpse NOW at the same spot
		if (At())
		{
			for (int i = 0; i < pen.Size() && !killed; i++) if (pen[i].health > 0 && th.when.InThen(pen[i].pos.xy)) killed = pen[i];
			if (killed) { killedAt = killed.pos.xy; killed.DamageMobj(null, mo, 10000, 'None'); }
		}
		if (Seg(5) && tt == 4)
		{
			old = FindCorpse(killedAt - (0, OFF), null);
			Check("oldCorpseNow", old != null && !old.bSolid && old.sprite == killed.sprite && old.Translation != 0,
				killed ? String.Format("%s killed at (%.0f,%.0f); %d corpses", killed.GetClassName(), killedAt.x, killedAt.y, th.corpses.Size()) : "none killed");
			Check("killedIsDeadThen", killed && killed.health <= 0 && th.when.InThen(killed.pos.xy));
		}
		// make sure one lives THEN (one that did not follow is brought through)
		if (At())
		{
			if (Count(true) == 0)
				for (int i = 0; i < pen.Size(); i++)
					if (pen[i].health > 0) { pen[i].SetOrigin((PEN_X + 300, OFF + 300, 0), false); Info("one brought THEN by the script"); break; }
			Pose(mo, PEN_X + 60, OFF + 256, 180);
		}
		// the door taken down THEN: nothing joins the times; the living THEN show NOW as old corpses
		if (At()) PressUse(mo);
		if (Seg(3) && tt == 2)
		{
			Check("doorDownThen", h.carried == clocked && !F(125).door, h.said);
			bool all = Count(true) > 0;
			for (int i = 0; i < pen.Size(); i++)
				if (pen[i].health > 0 && th.when.InThen(pen[i].pos.xy) && !FindCorpse(pen[i].pos.xy - (0, OFF), pen[i], 48)) all = false;
			Check("aliveThenShowsNow", all, String.Format("%d alive then, %d corpses", Count(true), th.corpses.Size()));
			Check("stillAliveThen", Count(true) > 0);
			Check("deadOneStays", FindCorpse(killedAt - (0, OFF), null) != null);
		}
		// hung again: the stand-ins go, the dead one's stays
		if (At()) PressUse(mo);
		if (Seg(3) && tt == 2)
		{
			int standIns = 0;
			for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && th.corpses[i].of) standIns++;
			Check("hungAgain", clocked.frame == F(125), h.said);
			Check("standInsGo", standIns == 0, String.Format("%d left", standIns));
			Check("deadOneStillStays", FindCorpse(killedAt - (0, OFF), null) != null);
		}
		// the clocked door down again, and RED hung THEN in its frame: a colour door joins no times
		// (2026-11-26), so the living THEN still show NOW as old corpses
		if (At()) { Pose(mo, PEN_X + 60, OFF + 256, 180); PressUse(mo); }
		if (At()) { h.DropDoor(clocked, mo); h.carried = null; clocked.SetOrigin((PEN_X + 256, OFF + 100, 0), false); red.Used(mo); Pose(mo, PEN_X + 60, OFF + 256, 180); PressUse(mo); }
		if (Seg(3) && tt == 2)
		{
			int standIns = 0;
			for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && th.corpses[i].of) standIns++;
			Check("redHungThenNoCompany", red.frame == F(125) && red.args[0] == 221 && !clocked.frame && !th.Linked(),
				String.Format("red in %d, args[0] %d", red.frame ? red.frame.args[0] : 0, red.args[0]));
			Check("standInsStayWithRedThen", standIns > 0 && standIns == Count(true), String.Format("%d stand-ins, %d alive then", standIns, Count(true)));
		}
	}
	int Count(bool inThen)
	{
		int n = 0;
		for (int i = 0; i < pen.Size(); i++) if (pen[i] && pen[i].health > 0 && th.when.InThen(pen[i].pos.xy) == inThen) n++;
		return n;
	}
	string MonsterPlaces()
	{
		string s = "";
		for (int i = 0; i < pen.Size(); i++)
			if (pen[i]) s = s .. String.Format("%s (%.0f,%.0f) %s hp %d; ", pen[i].GetClassName(), pen[i].pos.x, pen[i].pos.y, th.when.InThen(pen[i].pos.xy) ? "THEN" : "NOW", pen[i].health);
		return s;
	}
	AjarThenCorpse FindCorpse(Vector2 p, Actor of, double near = 1)
	{
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && c.of == of && (c.pos.xy - p).Length() < near) return c;
		}
		return null;
	}

	// === MODE=6: views for a person to judge (smoke_THEN_6.cfg: a shot at about 50 + 70 n) ==========
	int viewN;
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void Views(Actor mo)
	{
		let bc = Cause(11), dc = Cause(12), ec = Cause(13);
		if (Seg(15)) {}
		if (At()) { mo.player.mo.bInvisible = true; clocked.Used(mo); Pose(mo, 128, 470, 90); PressUse(mo); }
		// 0, 1: the hall through the clocked door, NOW into THEN and THEN into NOW
		if (At()) View(mo, "hall NOW, through 101 into THEN", 128, 250, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "hall THEN, through 121 into NOW", 128, OFF + 250, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "hall NOW: W, the rubble, the clocked door in 101 (from the south-west)", 40, 40, 45);
		if (Seg(69)) {}
		if (At()) View(mo, "hall THEN: W and M whole, the gate to E (from the south-west)", 40, OFF + 40, 30);
		if (Seg(69)) {}
		// the belt bay: heap down / up NOW, belt standing / running THEN
		if (At()) { Unhang(); View(mo, "belt NOW, standing: no heap, the pit open", BELT_X + 60, 200, 30); }
		if (Seg(69)) {}
		if (At()) View(mo, "belt THEN, standing", BELT_X + 60, OFF + 200, 30);
		if (Seg(69)) {}
		if (At()) { th.SetCause(bc, 1, null); th.Snap(bc); View(mo, "belt NOW, running: the heap", BELT_X + 60, 200, 30); }
		if (Seg(69)) {}
		if (At()) View(mo, "belt THEN, running", BELT_X + 60, OFF + 200, 30);
		if (Seg(69)) {}
		if (At()) { HangIn(104); View(mo, "belt NOW through 104: THEN's belt and its target, from the heap", BELT_X + 376, 384, 180); }
		if (Seg(69)) {}
		// the drip
		if (At()) { Unhang(); View(mo, "drip NOW, valve shut: dry", DRIP_X + 60, 100, 45); }
		if (Seg(69)) {}
		if (At()) { th.SetCause(dc, 1, null); th.Snap(dc); View(mo, "drip NOW, valve open: full", DRIP_X + 60, 100, 45); }
		if (Seg(69)) {}
		if (At()) View(mo, "drip THEN, valve open: dry", DRIP_X + 60, OFF + 100, 45);
		if (Seg(69)) {}
		if (At()) { HangIn(106); View(mo, "drip NOW through 106 into THEN, from the water", DRIP_X + 120, 256, 180); }
		if (Seg(69)) {}
		// the beam: off, A, B at both times
		for (int s = 0; s < 3; s++)
		{
			if (At()) { Unhang(); th.SetCause(ec, s, null); th.Snap(ec); View(mo, String.Format("beam NOW, setting %d: the %s wall", s, s == 2 ? "east" : "west"), BEAM_X + 256, 256, s == 2 ? 0 : 180); }
			if (Seg(69)) {}
			if (At()) View(mo, String.Format("beam THEN, setting %d", s), BEAM_X + 256, OFF + 60, 90);
			if (Seg(69)) {}
		}
		if (At()) { HangIn(107); View(mo, "beam NOW through 107 into THEN: the lever and the three targets", BEAM_X + 384, 300, 90); }
		if (Seg(69)) {}
		// company: an old corpse NOW
		if (At())
		{
			Unhang();
			let imp = Actor.Spawn("DoomImp", (PEN_X + 256, OFF + 200, 0));
			imp.DamageMobj(null, null, 1000, 'None');
			View(mo, "company NOW: an imp's old corpse (it died THEN)", PEN_X + 256, 60, 90, 20);
		}
		if (Seg(69)) {}
		if (At()) View(mo, "company THEN: the imp's corpse as it fell", PEN_X + 256, OFF + 60, 90, 20);
		if (Seg(69)) {}
		if (At()) Console.Printf("AJARTEST thenViews=1");
	}
	void Unhang() { if (clocked.frame) { h.carried = h.Unhang(clocked.frame); } }
	void HangIn(int id)
	{
		Unhang();
		let f = F(id);
		if (f) { h.Hang(clocked, f); h.carried = null; }
	}
}
