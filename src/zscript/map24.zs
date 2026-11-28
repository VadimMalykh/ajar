// MAP24 "Left Hanging" (tools/map_lefthanging.py; PLAN.md, "MAP24 "Left Hanging": the first version, as decided"
// and "... the first playable version"): the level's own script, and its checks (LeftHangingTest, below). Three
// times: THEN is NOW + (0, 8192), BEFORE NOW + (0, 16384). The old door rule is on (then.zs, a door left hanging).
// Frames (NOW / THEN / BEFORE): A the test room 101 / 121 / 141 (BEFORE free in yard A), B the lobby 105 / 125,
// C the hall's bay 102 / 122 / 142, D the strongroom 104 / 124 / 144, E the wet bay 103 / 123 / 143. GREEN's far
// side 203 / 223 / 243 (the sump, the store, the cellar). Causes: 11 the test room's mouth (follows 141), 12 the
// hoist (BEFORE), 13 the valve (THEN). Basins NOW: 2410 the cistern, 2411 the sump, 2412..2415 the outfalls
// before 101, 105, 102, 104.
//
// AjarLeftHanging: what is said. The test room's mouth first shut: "The test room was never built."; open again by
// a change (a colour door hung back BEFORE in 141): "It was found after all."

class AjarLeftHanging : EventHandler
{
	const MOUTH = 11;
	bool saidGone, saidFound;

	static bool Here() { return level.mapname ~== "MAP24"; }

	void Say(string s)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(s);
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info said at t=%d: %s", level.maptime, s);
	}

	override void WorldTick()
	{
		if (!Here()) return;
		let th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		let c = th.FindCause(MOUTH);
		if (!c) return;
		if (!saidGone && c.setting == 0) { saidGone = true; Say("The test room was never built."); }
		if (saidGone && !saidFound && AjarThenHandler.CauseDue(MOUTH * 16 + 1)) { saidFound = true; Say("It was found after all."); }
	}
}

// The checks: MAP=MAP24 MODE=n tools/smoke.sh.
//   1 the way through (tools/puzzle24.py's shortest, 12 door actions), to the way out: door actions by USE, the
//     frames walked through, the landing and the stair walked, the swim to the ledge; ordinary company removed
//     (the ambushes are seen to come: ajar.zs takes each away as it comes)
//   2 the level's rules, posed: the old GREEN from the first tic; rusted; the mouth following 141 (waiting for the
//     player); the swaps at 122 and 123; the old door's refusals; the sump filling through old GREEN in 103 and
//     draining through old GREEN in the lobby's outfall room; key 2 not reachable dry; the hoist and the levers;
//     the megasphere by the ten-year door in 144
//   3 views (tools/smoke_MAP24_3.cfg: a shot at 70 n)
class LeftHangingTest : EventHandler
{
	const OFF = 8192;
	const WALKKEY = 0x1900;
	const RUNKEY = 0x3200;
	const MOUTH = 11; const HOIST = 12; const VALVE = 13;
	const CISTERN = 2410; const SUMP = 2411;
	const BOTTOM = -128;
	int tic, cur, tt;
	int checks, fails, cleared;
	AjarHandler h;
	AjarThenHandler th;
	AjarDoor clocked, shadow, ten, tenShadow, green;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP24"; }

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
	void Pose(Actor mo, double x, double y, double ang, double pitch = 0, double z = -1e9)
	{
		mo.SetOrigin((x, y, z > -1e8 ? z : FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = false;
		Keys();
	}
	int TimeOf(Actor a) { return th.when.TimeOf(a.pos.xy); }
	static const string timeNames[] = { "NOW", "THEN", "BEFORE" };
	string Where(Actor mo) { return String.Format("(%.1f,%.1f,%.1f) angle %.1f %s", mo.pos.x, mo.pos.y - TimeOf(mo) * OFF, mo.pos.z, mo.angle, timeNames[TimeOf(mo)]); }
	bool Facing(Actor mo, double ang) { return abs(Actor.DeltaAngle(mo.angle, ang)) < 1; }
	AjarFrame F(int id) { return h.FindFrame(id); }
	double FZ(double x, double y) { Sector s = level.PointInSector((x, y)); return s.floorplane.ZatPoint(s.centerspot); }
	double CZ(double x, double y) { Sector s = level.PointInSector((x, y)); return s.ceilingplane.ZatPoint(s.centerspot); }
	AjarThenCause Cause(int tid) { return th.FindCause(tid); }
	AjarBasin Basin(int tag) { return th.wh ? th.wh.BasinOfTag(tag) : null; }
	bool Said(string part) { return h.said.IndexOf(part) >= 0; }
	string Carried() { return h.carried ? h.carried.Label() : "-"; }
	bool Open(int id) { Line l = h.FindLine(id); return l && !(l.flags & Line.ML_BLOCKING); }
	bool Has(Actor mo, int k) { return mo.FindInventory(String.Format("AjarKey%d", k)) != null; }
	bool InBox(Actor a, int t, double x1, double y1, double x2, double y2)
	{
		double y = a.pos.y - t * OFF;
		return TimeOf(a) == t && a.pos.x > x1 && a.pos.x < x2 && y > y1 && y < y2;
	}
	bool InSump(Actor a) { return InBox(a, 0, 1024, 448, 1600, 1024); }
	bool InStrong(Actor a, int t) { return InBox(a, t, 1536, -512, 2048, -16); }
	bool InHallOrLobby(Actor a, int t) { return InBox(a, t, 0, 0, 2048, 512); }
	string MouthInfo() { return String.Format("mouth: cause %d; ceiling NOW %.0f THEN %.0f", Cause(MOUTH).setting, CZ(320, 520), CZ(320, OFF + 520)); }
	string Water()
	{
		let c = Basin(CISTERN), s = Basin(SUMP);
		return String.Format("cistern %.2f, sump %.2f (valve %d)", c ? c.w : -999, s ? s.w : -999, Cause(VALVE).setting);
	}
	string DoorsSaid()
	{
		string s = "";
		for (int i = 0; i < 5; i++)
		{
			AjarDoor d = i == 0 ? clocked : i == 1 ? shadow : i == 2 ? ten : i == 3 ? tenShadow : green;
			s = s .. String.Format("%s%s in %d; ", d.Label(), d.IsShadow() ? "(shadow)" : "", d.frame ? d.frame.args[0] : 0);
		}
		return s .. "carried " .. Carried() .. "; " .. Olds() .. "; said: " .. h.said;
	}
	// the old door in frame id: GREEN's, so many years old, open onto its far side `far` at that time
	bool OldOf(int id, int years, int far)
	{
		AjarFrame f = F(id);
		AjarDoor o = f ? f.door : null;
		if (!o || !o.IsOld() || o.oldOf != green || o.oldYears != years || o.args[0] != far || !Open(far) || !Open(id)) return false;
		string spr = String.Format("%s%d", years > 10 ? "AJQ" : "AJO", green.Colour());
		return o.sprite == Actor.GetSpriteIndex(spr) && !o.bInvisible;
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
		string s = "old:";
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
			if (d.IsOld()) s = s .. String.Format(" %s in %d (%d years, onto %d)", d.Label(), d.frame ? d.frame.args[0] : 0, d.oldYears, d.args[0]);
		return s;
	}
	// ambushers still to come, of cause g (63: and args[4] arg)
	int ToCome(int g, int arg = -1)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == g && (arg < 0 || a.args[4] == arg)) n++;
		return n;
	}
	// the upper texture of the line a-b (either side)
	string UpperAt(double x1, double y1, double x2, double y2)
	{
		for (int i = 0; i < level.lines.Size(); i++)
		{
			Line l = level.lines[i];
			bool here = (l.v1.p == (x1, y1) && l.v2.p == (x2, y2)) || (l.v1.p == (x2, y2) && l.v2.p == (x1, y1));
			if (!here) continue;
			for (int k = 0; k < 2; k++)
			{
				if (!l.sidedef[k]) continue;
				string n = TexMan.GetName(l.sidedef[k].GetTexture(Side.top));
				if (n != "" && n != "-") return n;
			}
		}
		return "-";
	}

	// --- the player's controls, as beforetest.zs ------------------------------------------------------------------
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
	// 60 in front of a frame's mouth, facing it: walk 24 tics through it
	void Through(Actor mo, double x, double y, double ang) { Pose(mo, x, y, ang); Keys(WALKKEY); }
	void Use(Actor mo, double x, double y, double ang) { h.said = ""; Pose(mo, x, y, ang); PressUse(mo); }
	// by script: a door out of its frame into the hands, or into a frame (its other leaf with it)
	void ScriptUnhang(AjarDoor d) { if (d.frame) h.carried = h.Unhang(d.frame); }
	void ScriptHang(AjarDoor d, int id)
	{
		ScriptUnhang(d);
		if (h.carried == d) h.carried = null;
		h.Hang(d, F(id));
	}
	void PutBack(AjarDoor d)
	{
		if (d.frame) ScriptUnhang(d);
		d.carried = false;
		d.SetOrigin(d.SpawnPoint, false);
		d.Show();
		if (h.carried == d) h.carried = null;
	}
	void InHand(AjarDoor d)
	{
		if (h.carried && h.carried != d) PutBack(h.carried);
		if (d.frame) ScriptUnhang(d);
		d.carried = true;
		d.Hide();
		h.carried = d;
	}
	void Set(int tid, int s) { let c = Cause(tid); th.SetCause(c, s, null); th.Snap(c); }
	void ClearOrdinary()
	{
		Array<Actor> l;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && !(a is "PlayerPawn") && a.health > 0) l.Push(a);
		for (int i = 0; i < l.Size(); i++) { l[i].ClearCounters(); l[i].Destroy(); cleared++; }
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
				else if (d.args[1] == 3) green = d;
			}
			mo.player.cheats |= CF_GODMODE;
			if (mode != 3) mo.player.cheats |= CF_NOTARGET;
			Info(String.Format("times %d, old doors %d; causes %d, cause sectors %d; clocked %d shadow %d ten-year %d shadow %d green %d; basins %d %d",
				th.when.Times(), th.when.OldDoors(), th.causes.Size(), th.secIdx.Size(),
				clocked != null, shadow != null, ten != null, tenShadow != null, green != null, Basin(CISTERN) != null, Basin(SUMP) != null));
		}
		if (mode != 3 ? tic % 35 == 1 : tic == 1) ClearOrdinary();          // (the views: the places, not their company)
		cur = 2;
		if (mode == 1) Way(mo);
		else if (mode == 2) Rules(mo);
		else if (mode == 3) Views(mo);
		Drive(mo);
	}
	void Done() { Console.Printf("AJARTEST leftHangingDone=1 checks=%d failed=%d", checks, fails); }

	// === MODE=1: the way through =====================================================================================
	int fullAt, key1At, key2At;
	void Way(Actor mo)
	{
		let sump = Basin(SUMP), cistern = Basin(CISTERN);
		if (At())
		{
			Check("threeTimesOldDoors", th.when.Times() == 3 && th.when.OldDoors() && TimeOf(mo) == AjarThen.T_NOW, Where(mo));
			Check("doorsAtTheStart", green.frame == F(141) && ten.frame == F(122) && tenShadow.frame == F(142) && !clocked.frame && OldOf(121, 10, 223) && OldOf(101, 50, 203), DoorsSaid());
			Check("mouthOpenAtTheStart", Cause(MOUTH).setting == 1 && CZ(320, 520) == 128 && CZ(320, OFF + 520) == 128, MouthInfo());
			Check("dryAtTheStart", sump && cistern && !sump.Wet() && !cistern.Wet(), Water());
		}
		// 1, 2: the clocked door taken in the lobby and hung in 105; through into THEN
		if (At()) { Pose(mo, 100, 170, 270); clocked.Used(mo); }
		if (At()) Check("tookTheClockedDoor", h.carried == clocked, DoorsSaid());
		if (At()) Use(mo, 42, 256, 180);
		if (At()) Check("clockedIn105", clocked.frame == F(105) && shadow.frame == F(125), DoorsSaid());
		if (At()) Through(mo, 60, 256, 180);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheLobbyThen", InHallOrLobby(mo, 1) && Facing(mo, 0), Where(mo)); }
		if (At()) Check("theNoticeOverOldGreen", UpperAt(288, OFF + 912, 352, OFF + 912) ~== "AJLHN0" && OldOf(121, 10, 223), UpperAt(288, OFF + 912, 352, OFF + 912));
		// through the ten-year door on its rig into yard A
		if (At()) Through(mo, 832, OFF + 516, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("intoYardA", InBox(mo, 2, -192, -384, 1024, 1216), Where(mo)); }
		// 3: GREEN out of 141: the test room is gone, THEN and NOW
		if (At()) Use(mo, 320, 2 * OFF + 870, 90);
		if (At()) Check("tookGreen", h.carried == green && OldCount() == 0 && Cause(MOUTH).setting == 0, DoorsSaid());
		if (Seg(100) && tt == 99) Check("testRoomGone", CZ(320, 520) == 0 && CZ(320, OFF + 520) == 0 && Said("The test room was never built."), MouthInfo());
		if (At()) Through(mo, 832, 2 * OFF + 516, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("backIntoTheHallThen", InHallOrLobby(mo, 1) || InBox(mo, 1, 704, 384, 960, 576), Where(mo)); }
		// 4, 5, 6: GREEN swapped into 122 for the ten-year door, that hung in 123, GREEN fetched from 122
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Check("swapGreenFor122", green.frame == F(122) && h.carried == ten && OldOf(102, 40, 203), DoorsSaid());
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (At()) Check("tenYearIn123", ten.frame == F(123) && tenShadow.frame == F(143), DoorsSaid());
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Check("greenFrom122", h.carried == green && !F(122).door && OldCount() == 0, DoorsSaid());
		if (At()) Through(mo, 1792, OFF + 708, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("intoYardB", InBox(mo, 2, 1600, -704, 2624, 1216) && abs(mo.pos.z) < 1, Where(mo)); }
		// 7: GREEN in 144: old GREEN in 124 and 104
		if (At()) Use(mo, 1792, 2 * OFF - 470, 270);
		if (At()) Check("greenIn144", green.frame == F(144) && OldOf(124, 10, 223) && OldOf(104, 50, 203) && !h.carried, DoorsSaid());
		if (At()) Through(mo, 1792, 2 * OFF + 708, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("backIntoThePumpBayThen", InBox(mo, 1, 1664, 384, 1920, 768) && abs(mo.pos.z + 120) < 1, Where(mo)); }
		if (At()) Through(mo, 60, OFF + 256, 180);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheLobbyNow", InHallOrLobby(mo, 0), Where(mo)); }
		// NOW: down the sump's stair, through GREEN's far side and old GREEN in 104 into the strongroom: key 1
		if (At()) { Pose(mo, 1056, 420, 90); WalkTo(1056, 760); }
		if (Seg(70) && tt == 69) Check("downTheSumpsStair", InSump(mo) && abs(mo.pos.z - BOTTOM) < 1, Where(mo));
		if (At()) Through(mo, 1184, 964, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheStrongroomNow", InStrong(mo, 0) && Facing(mo, 90), Where(mo)); WalkTo(1792, -300); }
		if (Seg(50) && tt == 49) { Check("key1", Has(mo, 1), Where(mo)); key1At = tic; }
		if (At()) Through(mo, 1792, -452, 270);
		if (Seg(24) && tt == 23) { Keys(); Check("backIntoTheSump", InSump(mo) && abs(mo.pos.z - BOTTOM) < 1 && Facing(mo, 270), Where(mo)); }
		// 8: back to yard B (the clocked door in 105), the hoist's lever, GREEN taken from 144
		if (At()) Through(mo, 60, 256, 180);
		if (Seg(24) && tt == 23) Keys();
		if (At()) Through(mo, 1792, OFF + 708, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("intoYardBAgain", InBox(mo, 2, 1600, -704, 2624, 1216), Where(mo)); }
		if (At()) Use(mo, 2054, 2 * OFF + 448, 0);
		if (Seg(90) && tt == 89) Check("hoistUp", Cause(HOIST).setting == 1 && FZ(2240, 448) == 128 && FZ(2240, OFF + 448) == 128 && FZ(2240, 2 * OFF + 448) == 128,
			String.Format("%.0f %.0f %.0f", FZ(2240, 448), FZ(2240, OFF + 448), FZ(2240, 2 * OFF + 448)));
		if (At()) Check("ambushAtKey1", ToCome(1) == 0, String.Format("%d to come, %d tics after key 1", ToCome(1), tic - key1At));
		if (At()) Use(mo, 1792, 2 * OFF - 470, 270);
		if (At()) Check("greenFrom144", h.carried == green && OldCount() == 0, DoorsSaid());
		if (At()) Through(mo, 1792, 2 * OFF + 708, 90);
		if (Seg(24) && tt == 23) Keys();
		// THEN: across the landing to the gallery, the valve
		if (At()) { Pose(mo, 2112, OFF + 448, 0); WalkTo(2400, OFF + 448); }
		if (Seg(80) && tt == 79) Check("acrossTheLandingThen", InBox(mo, 1, 2304, 384, 2560, 704) && abs(mo.pos.z - 128) < 1, Where(mo));
		if (At()) Use(mo, 2530, OFF + 608, 0);
		if (At()) { Check("valveOpen", Cause(VALVE).setting == 1, Water()); fullAt = -1; }
		// 9: GREEN swapped into 123 for the ten-year door: old GREEN NOW in 103, in the full cistern; the sump fills
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (At()) Check("swapGreenFor123", green.frame == F(123) && h.carried == ten && OldOf(103, 40, 203), DoorsSaid());
		if (At()) Through(mo, 60, OFF + 256, 180);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheLobbyNowWithTheTenYearDoor", InHallOrLobby(mo, 0) && h.carried == ten, Where(mo)); Pose(mo, 1184, 420, 90); }
		if (Seg(1050))
		{
			if (fullAt < 0 && sump.w >= BOTTOM + 95.5) fullAt = tt;
			if (tt % 140 == 0) Info(String.Format("t+%d %s", tt, Water()));
			if (tt == 1049) Check("sumpFull", abs(cistern.w - (-120 + 96)) < 0.01 && abs(sump.w - (BOTTOM + 96)) < 0.6,
				String.Format("full in %d tics; %s", fullAt, Water()));
		}
		// the swim: from the water before the ledge, the walk and jump keys
		if (At()) Pose(mo, 1400, 944, 0, 0, sump.w - 40);
		if (Seg(105)) Keys(WALKKEY, BT_JUMP);
		if (At()) { Keys(); Check("swamOntoTheLedge", mo.pos.x > 1440 && abs(mo.pos.z - (BOTTOM + 112)) < 1, Where(mo)); WalkTo(1500, 950); }
		if (Seg(40) && tt == 39) { Check("key2", Has(mo, 2), Where(mo)); key2At = tic; }
		if (Seg(200) && tt == 199) Check("ambushAtKey2", ToCome(2) == 0, String.Format("%d to come", ToCome(2)));
		// 10, 11: the ten-year door back in 122, GREEN taken from 123: the sump keeps its water
		if (At()) Through(mo, 60, 256, 180);
		if (Seg(24) && tt == 23) Keys();
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Check("tenYearBackIn122", ten.frame == F(122) && tenShadow.frame == F(142) && !h.carried, DoorsSaid());
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (Seg(70) && tt == 69) Check("greenFrom123TheSumpStaysFull", h.carried == green && OldCount() == 0 && abs(sump.w - (BOTTOM + 96)) < 0.6, DoorsSaid() .. "; " .. Water());
		// 12: through the ten-year door to yard A, GREEN back in 141: the test room is found
		if (At()) Through(mo, 832, OFF + 516, 90);
		if (Seg(24) && tt == 23) Keys();
		if (At()) Use(mo, 320, 2 * OFF + 870, 90);
		if (At()) Check("greenBackIn141", green.frame == F(141) && OldOf(121, 10, 223) && OldOf(101, 50, 203) && Cause(MOUTH).setting == 1, DoorsSaid());
		if (At()) Through(mo, 832, 2 * OFF + 516, 90);
		if (Seg(24) && tt == 23) Keys();
		if (At()) Through(mo, 60, OFF + 256, 180);
		if (Seg(24) && tt == 23) { Keys(); Pose(mo, 320, 300, 90); }
		if (Seg(250) && tt == 249)
		{
			Check("testRoomFound", CZ(320, 520) == 128 && CZ(320, OFF + 520) == 128 && Said("It was found after all."), MouthInfo());
			Check("lastFightCame", ToCome(63, MOUTH * 16 + 1) == 0, String.Format("%d to come", ToCome(63, MOUTH * 16 + 1)));
			Check("sumpDrainsThroughOldGreenIn101", sump.w < BOTTOM + 90, Water());
		}
		// the test room, the brass door (keys 1 and 2), the night room, out
		if (At()) WalkTo(320, 800);
		if (Seg(90) && tt == 89) Check("intoTheTestRoom", InBox(mo, 0, 128, 528, 512, 912), Where(mo));
		if (At()) Use(mo, 464, 870, 90);
		if (Seg(40) && tt == 39) Check("brassDoorOpens", CZ(464, 920) > 64, String.Format("ceiling %.0f", CZ(464, 920)));
		if (At()) WalkTo(464, 1120);
		if (Seg(60) && tt == 59)
		{
			Check("inTheNightRoom", InBox(mo, 0, 304, 992, 624, 1248), Where(mo));
			Info(String.Format("ordinary company cleared %d; %s", cleared, Water()));
			Done();
		}
		if (At()) WalkTo(700, 1120);
	}

	// === MODE=2: the rules ===========================================================================================
	int drainAt;
	void Rules(Actor mo)
	{
		let sump = Basin(SUMP), cistern = Basin(CISTERN);
		// GREEN hangs BEFORE from the first tic, so its old selves THEN and NOW do too
		if (At())
		{
			Check("oldGreenFromTheFirstTic", green.frame == F(141) && OldOf(121, 10, 223) && OldOf(101, 50, 203) && Open(243) && OldCount() == 2, DoorsSaid());
			Check("causesAtTheStart", Cause(MOUTH).setting == 1 && Cause(HOIST).setting == 0 && Cause(VALVE).setting == 0 && FZ(2240, 448) == 16 && FZ(2240, OFF + 448) == 16 && FZ(2240, 2 * OFF + 448) == 16,
				MouthInfo() .. String.Format("; landing %.0f %.0f %.0f", FZ(2240, 448), FZ(2240, OFF + 448), FZ(2240, 2 * OFF + 448)));
		}
		// rusted, NOW and THEN
		if (At()) Use(mo, 320, 870, 90);
		if (At()) Check("rustedNow", Said("Rusted to its frame.") && !h.carried, h.said);
		if (At()) Use(mo, 320, OFF + 870, 90);
		if (At()) Check("rustedThen", Said("Rusted to its frame.") && !h.carried, h.said);
		// through old GREEN: NOW into the sump's bottom (101 at 0, 203 at -128), THEN into the store
		if (At()) Through(mo, 320, 852, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("throughOldGreenNowIntoTheSump", InSump(mo) && abs(mo.pos.z - BOTTOM) < 1 && Facing(mo, 270), Where(mo)); }
		if (At()) Through(mo, 320, OFF + 852, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("throughOldGreenThenIntoTheStore", InBox(mo, 1, 1024, 400, 1600, 1024) && abs(mo.pos.z) < 1, Where(mo)); }
		if (At()) Through(mo, 1184, OFF + 964, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("backFromTheStore", InBox(mo, 1, 128, 528, 512, 912), Where(mo)); }
		// the mouth: GREEN taken from 141 (by script) while the player stands NOW in the mouth: THEN it shuts, NOW it waits
		if (At()) { Pose(mo, 320, 520, 90); InHand(green); }
		if (Seg(100) && tt == 99)
			Check("mouthWaitsForThePlayer", Cause(MOUTH).setting == 0 && CZ(320, 520) == 128 && CZ(320, OFF + 520) == 0 && mo.health > 0 && Said("The test room was never built."), MouthInfo());
		if (At()) Pose(mo, 320, 300, 90);
		if (Seg(100) && tt == 99) Check("mouthShutAtBothTimes", CZ(320, 520) == 0 && CZ(320, OFF + 520) == 0, MouthInfo());
		if (At()) WalkTo(320, 700);
		if (Seg(40) && tt == 39) { walking = false; Keys(); Check("noWayIntoTheTestRoom", mo.pos.y < 512, Where(mo)); }
		// the ten-year door's leaf in 141 is no colour door: still shut
		if (At()) ScriptHang(ten, 121);
		if (Seg(60) && tt == 59) Check("tenYearLeafIn141KeepsItShut", tenShadow.frame == F(141) && Cause(MOUTH).setting == 0 && CZ(320, 520) == 0, MouthInfo());
		if (At()) { ScriptHang(ten, 122); h.carried = green; }
		// GREEN hung back in 141 in play: open again, at both times
		if (At()) Use(mo, 320, 2 * OFF + 870, 90);
		if (Seg(100))
		{
			if (tt == 0) Check("greenBackIn141", green.frame == F(141) && OldOf(121, 10, 223) && OldOf(101, 50, 203) && Cause(MOUTH).setting == 1, DoorsSaid());
			if (tt == 99) Check("mouthOpenAgain", CZ(320, 520) == 128 && CZ(320, OFF + 520) == 128 && Said("It was found after all."), MouthInfo());
		}
		// the swaps: at 122 (GREEN for the ten-year door and back), at 123
		if (At()) Use(mo, 320, 2 * OFF + 870, 90);
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Check("swapAt122", green.frame == F(122) && h.carried == ten && !tenShadow.frame && OldOf(102, 40, 203) && !F(142).door && OldCount() == 1, DoorsSaid());
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Check("swapBackAt122", ten.frame == F(122) && tenShadow.frame == F(142) && h.carried == green && OldCount() == 0, DoorsSaid());
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (At()) Check("tenYearInto123", ten.frame == F(123) && tenShadow.frame == F(143) && green.frame == F(122), DoorsSaid());
		if (At()) Use(mo, 832, OFF + 534, 90);
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (At()) Check("swapAt123", green.frame == F(123) && h.carried == ten && OldOf(103, 40, 203) && !F(143).door, DoorsSaid());
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (At()) Check("swapBackAt123", ten.frame == F(123) && tenShadow.frame == F(143) && h.carried == green && OldCount() == 0, DoorsSaid());
		// the old door rule's refusal: GREEN BEFORE into 142 while the clocked door's leaf hangs THEN in 122
		if (At()) { ScriptHang(ten, 123); ScriptHang(clocked, 102); h.carried = green; }
		if (At()) Use(mo, 832, 2 * OFF + 534, 90);
		if (At()) Check("refusedALaterDoorIn122", h.carried == green && !F(142).door && shadow.frame == F(122) && Said("A door hangs in this frame at a later time."), DoorsSaid());
		// the clocked door refused at 123 THEN while old GREEN hangs in its twin 103 (GREEN THEN in 123), rusted at 103 NOW
		if (At()) { PutBack(clocked); ScriptHang(ten, 122); ScriptHang(green, 123); InHand(clocked); }
		if (At()) Use(mo, 1792, OFF + 726, 90);
		if (At()) Check("clockedRefusedOldGreenInItsTwin", h.carried == clocked && green.frame == F(123) && OldOf(103, 40, 203) && Said("At the other time a door hangs in this frame."), DoorsSaid());
		if (At()) Use(mo, 1792, 726, 90);
		if (At()) Check("rustedInTheCistern", h.carried == clocked && OldOf(103, 40, 203) && Said("Rusted to its frame."), DoorsSaid());
		// the bars: the hall NOW does not lead into the cistern (walked at, and run at)
		if (At()) { PutBack(clocked); Pose(mo, 1792, 300, 90); WalkTo(1792, 640); }
		if (Seg(60) && tt == 59) { walking = false; Keys(); Check("barsHallNotIntoTheCistern", mo.pos.y < 384 && TimeOf(mo) == AjarThen.T_NOW, Where(mo)); }
		if (At()) { Pose(mo, 1700, 200, 60); Keys(RUNKEY, BT_JUMP); }
		if (Seg(50) && tt == 49) { Keys(); Check("barsRunAndJump", mo.pos.y < 384, Where(mo)); }
		if (At()) Pose(mo, 1792, OFF + 300, 90);
		if (At()) WalkTo(1792, OFF + 640);
		if (Seg(70) && tt == 69) { walking = false; Keys(); Check("pumpBayOpenThen", InBox(mo, 1, 1664, 384, 1920, 768) && mo.pos.z < -100, Where(mo)); }
		// the cistern entered and left through old GREEN in 103 (GREEN THEN in 123): from the sump's bottom, and back
		if (At()) Through(mo, 1184, 964, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheCisternThroughOldGreen", InBox(mo, 0, 1664, 384, 1920, 768) && abs(mo.pos.z + 120) < 1 && Facing(mo, 270), Where(mo)); }
		if (At()) Through(mo, 1792, 708, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("outOfTheCisternIntoTheSump", InSump(mo) && abs(mo.pos.z - BOTTOM) < 1, Where(mo)); }
		// ... and through the clocked door hung THEN in 123 (its leaf NOW in 103)
		if (At()) { ScriptUnhang(green); PutBack(green); ScriptHang(clocked, 123); h.carried = null; }
		if (At()) Through(mo, 1792, OFF + 708, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheCisternByTheClockedDoor", InBox(mo, 0, 1664, 384, 1920, 768) && shadow.frame == F(103), Where(mo) .. "; " .. DoorsSaid()); }
		if (At()) Through(mo, 1792, 708, 90);
		if (Seg(24) && tt == 23) { Keys(); Check("outOfTheCisternByTheClockedDoor", InBox(mo, 1, 1664, 384, 1920, 768), Where(mo)); }
		if (At()) { PutBack(clocked); ScriptHang(green, 123); h.carried = null; }
		// the water: the valve open (by script); the cistern full; through old GREEN in 103 the sump fills
		if (At()) { PutBack(clocked); Set(VALVE, 1); fullAt = -1; Pose(mo, 1184, 420, 90); }
		if (Seg(1050))
		{
			if (fullAt < 0 && sump.w >= BOTTOM + 95.5) fullAt = tt;
			if (tt % 140 == 0) Info(String.Format("t+%d %s", tt, Water()));
			if (tt == 1049) Check("sumpFillsThroughOldGreenIn103", abs(cistern.w + 24) < 0.01 && abs(sump.w - (BOTTOM + 96)) < 0.6 && Cause(VALVE).setting == 1,
				String.Format("full in %d tics; %s", fullAt, Water()));
		}
		if (At()) Pose(mo, 1300, 700, 90);
		if (Seg(3) && tt == 2) Check("sumpUnderWaterNow", mo.waterlevel >= 2, String.Format("waterlevel %d", mo.waterlevel));
		if (At()) Pose(mo, 1300, OFF + 700, 90);
		if (Seg(3) && tt == 2) Check("storeDryThen", mo.waterlevel == 0 && TimeOf(mo) == AjarThen.T_THEN);
		if (At()) Pose(mo, 1792, OFF + 640, 90);
		if (Seg(3) && tt == 2) Check("pumpBayDryThen", mo.waterlevel == 0 && TimeOf(mo) == AjarThen.T_THEN);
		// GREEN taken from 123: the sump keeps its water (water.zs keeps no history)
		if (At()) ScriptUnhang(green);
		if (Seg(70) && tt == 69) Check("theSumpKeepsItsWater", OldCount() == 0 && abs(sump.w - (BOTTOM + 96)) < 0.6, Water());
		// the clocked door in 123 with the cistern full NOW: what the pump bay THEN sees (measured, nothing to pass)
		if (At()) { PutBack(green); ScriptHang(clocked, 123); Pose(mo, 1792, OFF + 640, 90); }
		if (Seg(35) && tt == 34) Info(String.Format("the clocked door in 123/103, the cistern full: THEN at the pump bay waterlevel %d; %s", mo.waterlevel, Water()));
		if (At()) Pose(mo, 1792, OFF + 718, 90);
		if (Seg(30)) Keys(WALKKEY);
		if (At()) { Keys(); Info(String.Format("walked from THEN through the clocked door in 123 into the full cistern: %s, waterlevel %d", Where(mo), mo.waterlevel)); }
		if (At()) Check("cisternStaysFull", abs(cistern.w + 24) < 0.01, Water());
		// drained: GREEN hung THEN in 125 (by script), old GREEN NOW in 105, the lobby's outfall room
		if (At()) { PutBack(clocked); ScriptHang(green, 125); drainAt = -1; }
		if (Seg(1050))
		{
			if (drainAt < 0 && !sump.Wet()) drainAt = tt;
			if (tt % 140 == 0) Info(String.Format("t+%d %s", tt, Water()));
			if (tt == 1049) Check("sumpDrainsThroughOldGreenIn105", OldOf(105, 40, 203) && !sump.Wet() && abs(cistern.w + 24) < 0.01, String.Format("dry in %d tics; %s", drainAt, Water()));
		}
		if (At()) Pose(mo, 32, 256, 180);
		if (Seg(3) && tt == 2) Check("theLobbyStaysDry", mo.waterlevel == 0, String.Format("waterlevel %d", mo.waterlevel));
		// key 2 not reachable dry: off the landing at a run; from the stair's foot at a run; along the bottom to the ledge
		if (At()) { ScriptUnhang(green); PutBack(green); sump.w = BOTTOM - 32; Pose(mo, 1520, 420, 90); Keys(RUNKEY); }
		if (Seg(70) && tt == 69) { Keys(); Check("offTheLandingIntoThePit", !Has(mo, 2) && mo.pos.z < BOTTOM + 1 && mo.pos.y < 870, Where(mo)); }
		if (At()) { Pose(mo, 1056, 690, VectorAngle(1500 - 1056, 940 - 690)); Keys(RUNKEY); }
		if (Seg(70) && tt == 69) { Keys(); Check("fromTheStairsFoot", !Has(mo, 2) && mo.pos.z < BOTTOM + 1, Where(mo)); }
		if (At()) { Pose(mo, 1520, 420, 90); Keys(RUNKEY, BT_JUMP); }
		if (Seg(70) && tt == 69) { Keys(); Check("runningJumpFromTheLanding", !Has(mo, 2) && mo.pos.z < BOTTOM + 1, Where(mo)); }
		if (At()) { Pose(mo, 1056, 456, VectorAngle(1500 - 1056, 940 - 456)); Keys(RUNKEY, BT_JUMP); }
		if (Seg(70) && tt == 69) { Keys(); Check("runningJumpFromTheStairsTop", !Has(mo, 2) && mo.pos.z < BOTTOM + 1, Where(mo)); }
		if (At()) { Pose(mo, 1056, 690, VectorAngle(1500 - 1056, 940 - 690)); Keys(RUNKEY, BT_JUMP); }
		if (Seg(70) && tt == 69) { Keys(); Check("runningJumpFromTheStairsFoot", !Has(mo, 2) && mo.pos.z < BOTTOM + 1, Where(mo)); }
		if (At()) { Pose(mo, 1500, 820, 90); WalkTo(1500, 950); }
		if (Seg(50) && tt == 49) { walking = false; Keys(); Check("notUpTheLedgeDry", !Has(mo, 2) && mo.pos.z < BOTTOM + 1 && mo.pos.y < 864, Where(mo)); }
		// the hoist: down, the landing a drop; its lever BEFORE (dead THEN and NOW); up, the landing at all times
		if (At()) { Pose(mo, 2112, 448, 0); WalkTo(2400, 448); }
		if (Seg(80) && tt == 79) { walking = false; Keys(); Check("noLandingWhileDown", mo.pos.x < 2310 && mo.pos.z < 17, Where(mo)); }
		if (At()) Use(mo, 2054, 2 * OFF + 448, 0);
		if (Seg(90))
		{
			if (tt == 0) Check("hoistLeverBefore", Cause(HOIST).setting == 1);
			if (tt == 89) Check("landingAtAllThreeTimes", FZ(2240, 448) == 128 && FZ(2240, OFF + 448) == 128 && FZ(2240, 2 * OFF + 448) == 128,
				String.Format("%.0f %.0f %.0f", FZ(2240, 448), FZ(2240, OFF + 448), FZ(2240, 2 * OFF + 448)));
		}
		if (At()) { Pose(mo, 2112, 448, 0); WalkTo(2400, 448); }
		if (Seg(80) && tt == 79) Check("acrossTheLandingNow", InBox(mo, 0, 2304, 384, 2560, 704) && abs(mo.pos.z - 128) < 1 && mo.FindInventory("RocketLauncher") == null, Where(mo));
		if (At()) WalkTo(2496, 640);
		if (Seg(50) && tt == 49) Check("rocketLauncherNow", mo.FindInventory("RocketLauncher") != null, Where(mo));
		if (At()) { Set(VALVE, 0); Use(mo, 2530, 608, 0); }
		if (Seg(10) && tt == 9) Check("valveLeverDeadNow", Cause(VALVE).setting == 0);
		// the megasphere: the ten-year door in 144 BEFORE (its leaf THEN in 124)
		if (At()) { ScriptHang(ten, 144); h.carried = null; }
		if (At()) Check("tenYearIn144", ten.frame == F(144) && tenShadow.frame == F(124), DoorsSaid());
		if (At()) Through(mo, 1792, 2 * OFF - 452, 270);
		if (Seg(24) && tt == 23) { Keys(); Check("intoTheStrongroomThen", InStrong(mo, 1), Where(mo)); WalkTo(1792, OFF - 300); }
		if (Seg(50) && tt == 49) Check("megasphereThen", mo.health >= 200, String.Format("health %d", mo.health));
		if (At()) Done();
	}

	// === MODE=3: views for a person to judge (smoke_MAP24_3.cfg: a shot at 70 n) ===================================
	int viewN;
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void Views(Actor mo)
	{
		let sump = Basin(SUMP);
		if (Seg(15)) {}
		if (At()) { mo.bInvisible = true; mo.player.cheats |= CF_NOTARGET; }
		if (At()) View(mo, "the start NOW: through the test room's mouth, old GREEN in 101 under its lamp", 320, 96, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "the test room NOW: old GREEN in 101, fifty years, the grate before it; the brass door right", 320, 640, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "the test room NOW: the brass door (keys 1 and 2)", 380, 720, 60);
		if (Seg(69)) {}
		if (At()) View(mo, "the start THEN: through the mouth, old GREEN in 121", 320, OFF + 96, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "the test room THEN: old GREEN in 121, ten years, under ON TEST. DO NOT REMOVE.", 320, OFF + 600, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "the hall NOW from the lobby", 600, 200, 0);
		if (Seg(69)) {}
		if (At()) View(mo, "the hall THEN from the lobby", 600, OFF + 200, 0);
		if (Seg(69)) {}
		if (At()) View(mo, "bay C THEN: the ten-year door on its rig in 122", 832, OFF + 320, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "yard A BEFORE: GREEN new in 141, pier 142 (the ten-year door's other leaf)", 100, 2 * OFF + 500, 30);
		if (Seg(69)) {}
		if (At()) View(mo, "yard B BEFORE from 143: the hoist's gantry and deck (down), its lever on its post", 1792, 2 * OFF + 700, 330);
		if (Seg(69)) {}
		if (At()) { Set(HOIST, 1); View(mo, "yard B BEFORE: the deck up (the lever pulled)", 1880, 2 * OFF + 300, 20); }
		if (Seg(69)) {}
		if (At()) View(mo, "the hoist bay NOW: the same deck, a landing", 2100, 250, 60, -5);
		if (Seg(69)) {}
		if (At()) View(mo, "the cistern NOW, dry, from the hall: the bars, frame 103", 1792, 300, 90, 8);
		if (Seg(69)) {}
		if (At()) View(mo, "the sump NOW, dry, from the landing: the stair, the ledge with key 2", 1150, 420, 55, 15);
		if (Seg(69)) {}
		if (At()) { ScriptHang(green, 123); h.carried = null; Set(VALVE, 1); if (sump) sump.w = BOTTOM + 96; View(mo, "the sump NOW full (old GREEN in 103, the valve open): from the landing", 1150, 420, 55, 15); }
		if (Seg(69)) {}
		if (At()) View(mo, "the cistern NOW full, from the hall: old GREEN in 103 under water, through the bars", 1792, 300, 90, 8);
		if (Seg(69)) {}
		if (At()) View(mo, "the pump bay THEN, dry: GREEN in 123", 1792, OFF + 420, 90, 10);
		if (Seg(69)) {}
		if (At()) { ScriptUnhang(green); PutBack(green); ScriptHang(clocked, 123); h.carried = null; View(mo, "the pump bay THEN: the clocked door in 123, the cistern full NOW (left for the second version)", 1792, OFF + 600, 90); }
		if (Seg(69)) {}
		if (At()) View(mo, "the store THEN (GREEN's far side 223)", 1300, OFF + 600, 90);
		if (Seg(69)) {}
		if (At()) { PutBack(clocked); ScriptHang(green, 144); h.carried = null; if (sump) sump.w = BOTTOM - 32; View(mo, "the strongroom NOW: old GREEN in 104, key 1", 1792, -150, 270); }
		if (Seg(69)) {}
		if (At()) View(mo, "the gallery THEN: the valve's lever", 2340, OFF + 600, 0);
		if (Seg(69)) {}
		if (At()) { ShutMouth(); View(mo, "the lobby NOW with no colour door in 141: the test room never built", 320, 300, 90); }
		if (Seg(69)) {}
		if (At()) View(mo, "the cellar BEFORE (GREEN's far side 243)", 1300, 2 * OFF + 760, 90);
		if (Seg(69)) {}
		if (At()) View(mo, "the night room NOW", 340, 1120, 0);
		if (Seg(69)) {}
		if (At()) Console.Printf("AJARTEST leftHangingViews=%d", viewN);
	}
	// (the mouth shut at once, for the view)
	void ShutMouth() { if (green.frame == F(141)) ScriptUnhang(green); th.FollowFrames(); th.Snap(Cause(MOUTH)); }
}
