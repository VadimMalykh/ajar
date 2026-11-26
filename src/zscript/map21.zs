// MAP21 "In the Long Run" (tools/map_longrun.py; PLAN.md, "MAP21 "In the Long
// Run""): the level's own script, and its checks (LongRunTest, below).
// THEN is NOW + (0, 8192). Frames NOW / THEN: 101/121 the machine (the clocked
// door's alone at both times), 103/123 the corridor's first stretch (NOW the
// clocked door's alone), 105/125 the cellar's landing, 108/128 the goods bay,
// 106/126 optics, 110/130 the lobby. Causes (then.zs): 11 the valve (0 shut,
// 1 open; found open), 12 the belt (0 standing, found; 1 running), 13 the beam
// (0 off, 1 A, 2 B, 3 C; found at C).

// The desk the machine is run from (thing 20187, one, NOW; its panel's line
// does Thing_Activate on it at both times). NOW it is smashed. THEN, with keys 1
// and 2 and the clocked door in the machine's frame (101, or 121: either time),
// the machine starts: the hall THEN brightens, a sound, and the brass shutter
// in the north wall opens for good onto the night room.
class AjarLongRunDesk : Actor
{
	const SHUTTER = 2101;
	const LIGHT_TAG = 2102;
	bool started;
	int startedAt;
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	override void Activate(Actor activator)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		let w = AjarThen.Find();
		if (!h || !w || !activator) return;
		if (!w.InThen(activator.pos.xy))
		{
			h.Say("The desk is smashed.\nNothing on it works now.");
			return;
		}
		if (started)
		{
			h.Say("The machine is running.");
			return;
		}
		bool k1 = h.Has(activator, 1), k2 = h.Has(activator, 2);
		if (!k1 || !k2)
		{
			h.Say(!k1 && !k2 ? "Two keys turn here: 1 and 2." : !k1 ? "Key 1 is missing." : "Key 2 is missing.");
			A_StartSound("*usefail", CHAN_AUTO);
			return;
		}
		AjarFrame f = h.FindFrame(101);
		if (!(f && f.door && f.door.IsClocked()))
		{
			h.Say("You turn the keys.\nThe frame is empty.");
			A_StartSound("*usefail", CHAN_AUTO);
			return;
		}
		Start(activator);
	}

	void Start(Actor who)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		started = true;
		startedAt = level.maptime;
		if (h) h.Say("You turn the keys.\nThe machine starts on the door it was found with.");
		let si = level.CreateSectorTagIterator(LIGHT_TAG);
		int s;
		while ((s = si.Next()) >= 0) level.sectors[s].SetLightLevel(240);
		S_StartSound("weapons/bfgf", CHAN_AUTO, CHANF_UI, 1, ATTN_NONE);
		level.ExecuteSpecial(11, who, null, false, SHUTTER, 16);             // Door_Open: the brass shutter, for good
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info the machine starts at t=%d", level.maptime);
	}

	static AjarLongRunDesk Get() { return AjarLongRunDesk(ThinkerIterator.Create("AjarLongRunDesk").Next()); }
}

// The first time each long cause is changed, one line says it the long way.
class AjarLongRun : EventHandler
{
	const VALVE = 11; const BELT = 12; const BEAM = 13;
	bool told[3];

	static string LineFor(int tid, int s)
	{
		if (tid == VALVE) return s == 0 ? "The valve was never opened." : "The valve has stood open for forty years.";
		if (tid == BELT) return s == 1 ? "The belt has run for forty years." : "The belt has never run.";
		if (s == 0) return "The beam was never switched on.";
		return String.Format("The beam has been on wall %s for forty years.", s == 1 ? "A" : s == 2 ? "B" : "C");
	}

	override void WorldTick()
	{
		if (!(level.mapname ~== "MAP21")) return;
		let th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		for (int i = 0; i < 3; i++)
		{
			if (told[i]) continue;
			let c = th.FindCause(VALVE + i);
			if (!c || !c.timesSet) continue;
			told[i] = true;
			if (h) h.Say(LineFor(c.tid, c.setting));
		}
	}
}

// The checks: MAP=MAP21 MODE=n tools/smoke.sh.
//   1 the way through, walked: every stage on foot, through the doors, by USE
//     (nothing posed, nothing ridden by script), with the checks on the way
//   2 the three causes set by shots from NOW through the clocked door (posed)
//   3 views (tools/smoke_MAP21_3.cfg shoots every 70 tics)
class LongRunTest : EventHandler
{
	const OFF = 8192;
	const LX = 2560;
	const WALKKEY = 0x1900;
	const VALVE = 11; const BELT = 12; const BEAM = 13;
	const BASIN = 2110;
	const PIT = -200;
	int tic, checks, fails;
	int step, cur, stepTic;
	bool entered;
	AjarHandler h;
	AjarThenHandler th;
	AjarDoor clocked, shadow, red, blue;
	AjarLongRunDesk desk;
	int viewN;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP21"; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	// --- the steps: each `if (S()) {...}` is one, done in turn; Next() moves on --------------------------
	bool S() { return cur++ == step; }
	void Next() { step++; entered = false; }
	bool First() { if (!entered) { entered = true; stepTic = tic; return true; } return false; }
	int Age() { return tic - stepTic; }

	bool InThen(Actor mo) { return th.when.InThen(mo.pos.xy); }
	string Where(Actor mo) { return String.Format("(%.1f,%.1f,%.1f) angle %.1f %s", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, InThen(mo) ? "THEN" : "NOW"); }
	AjarFrame F(int id) { return h.FindFrame(id); }
	Sector SectorAt(double x, double y) { return level.PointInSector((x, y)); }
	double FZ(double x, double y) { Sector s = SectorAt(x, y); return s.floorplane.ZatPoint(s.centerspot); }
	double CZ(double x, double y) { Sector s = SectorAt(x, y); return s.ceilingplane.ZatPoint(s.centerspot); }
	bool Open(double x, double y) { return CZ(x, y) > FZ(x, y) + 56; }
	AjarThenCause Cause(int tid) { return th.FindCause(tid); }
	double Water() { let wh = AjarWaterHandler.Get(); let b = wh ? wh.BasinOfTag(BASIN) : null; return b ? b.w : -9999; }
	bool Said(string part) { return h.said.IndexOf(part) >= 0; }
	int Ambushers(int cause)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == cause) n++;
		return n;
	}
	AjarPressureDoor PDoor() { return AjarPressureDoor(ThinkerIterator.Create("AjarPressureDoor").Next()); }

	// --- the player's controls, as thentest.zs ---------------------------------------------------
	int fwd;
	Vector2 walkGoal;
	bool walking;
	double pushAngle;
	bool pushing;
	double best;
	int bestAt;
	Vector2 last;
	bool jumped;
	int afterJump;

	void Keys(int f = 0) { fwd = f; }
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp) return;
		if (walking)
		{
			// toward the goal; back on the keys in time to stop on it (Doom's friction leaves 9.6 tics' worth of
			// speed to slide), and done once there and still
			Vector2 d = walkGoal - mo.pos.xy;
			double l = d.Length(), v = mo.vel.xy.Length();
			if (l < 8 && v < 1.5) { walking = false; Keys(); }
			else
			{
				if (l > 2) mo.angle = VectorAngle(d.x, d.y);
				double along = l > 0.01 ? (mo.vel.xy dot d) / l : 0;
				fwd = l < along * 10 + 4 ? (along > 0.5 ? -WALKKEY : 0) : WALKKEY;
			}
		}
		else if (pushing) { mo.angle = pushAngle; fwd = WALKKEY; }
		if (!fwd && !walking) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.buttons = 0;
		pp.HandleMovement();
	}
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}
	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, level.PointInSector((x, y)).floorplane.ZatPoint((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = pushing = false;
		Keys();
	}

	// Walk to x, y (a real walk: the engine's own movement, keys "held"); stuck: a failed check, and on.
	void Go(Actor mo, double x, double y)
	{
		if (First())
		{
			walkGoal = (x, y); walking = true; pushing = false;
			best = 1e9; bestAt = tic;
		}
		double d = (walkGoal - mo.pos.xy).Length();
		if (d < best - 4) { best = d; bestAt = tic; }
		if (!walking) { Next(); return; }
		if (tic - bestAt > 105)
		{
			Check(String.Format("walkTo_%d_%d", x, y), false, Where(mo));
			walking = false; Keys(); Next();
		}
	}
	// Walk on facing `ang` for n tics.
	void Push(Actor mo, double ang, int n)
	{
		if (First()) { pushAngle = ang; pushing = true; walking = false; }
		if (Age() >= n) { pushing = false; Keys(); Next(); }
	}
	// Walk on facing `ang` through a hung door (until the player is carried elsewhere), and 14 tics out of it.
	void Through(Actor mo, double ang)
	{
		if (First()) { pushAngle = ang; pushing = true; walking = false; last = mo.pos.xy; jumped = false; afterJump = 0; }
		if (!jumped && (mo.pos.xy - last).Length() > 100) { jumped = true; pushAngle = mo.angle; }
		last = mo.pos.xy;
		if (jumped && ++afterJump >= 14) { pushing = false; Keys(); Next(); return; }
		if (Age() > 140) { Check("walkThrough", false, Where(mo)); pushing = false; Keys(); Next(); }
	}
	void Use(Actor mo, double ang) { mo.angle = ang; mo.pitch = 0; PressUse(mo); Next(); }
	void Wait(int n) { First(); if (Age() >= n) Next(); }

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
			desk = AjarLongRunDesk.Get();
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.IsShadow()) shadow = d;
				else if (d.IsClocked()) clocked = d;
				else if (d.args[1] == 1) red = d;
				else if (d.args[1] == 2) blue = d;
			}
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			let mi = ThinkerIterator.Create("Actor");          // (mode 1's are gone already: ajar.zs)
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster) a.Destroy();
			Info(String.Format("causes %d, cause sectors %d, emitters %d, belts %d, targets %d; clocked %d shadow %d red %d blue %d desk %d",
				th.causes.Size(), th.secIdx.Size(), th.emitters.Size(), th.belts.Size(), th.targets.Size(),
				clocked != null, shadow != null, red != null, blue != null, desk != null));
		}
		cur = 0;
		if (mode == 1) Walk(mo);
		else if (mode == 2) Shots(mo);
		else if (mode == 3) Views(mo);
		Drive(mo);
		if (tic % 70 == 0 && mode != 3) Info(String.Format("t=%d step %d %s carried %s", tic, step, Where(mo), h.carried ? h.carried.Label() : "-"));
	}

	void Done() { Console.Printf("AJARTEST longRunDone=1 checks=%d failed=%d", checks, fails); Next(); }

	// === MODE=1: the way through, on foot ==============================================================
	void Walk(Actor mo)
	{
		if (S()) { Wait(2); }
		if (S())
		{
			Check("clockedFoundIn101", F(101).door == clocked && F(121).door == shadow && clocked.frame == F(101), h.said);
			Check("valveFoundOpen", Cause(VALVE).setting == 1 && abs(Water() - (-72)) < 1, String.Format("water %.1f", Water()));
			Check("beltFoundStanding", Cause(BELT).setting == 0 && abs(FZ(2000, 1150) + 112) < 1);
			Check("beamFoundAtC", Cause(BEAM).setting == 3 && CZ(1672, 2576) > 50 && CZ(1144, 2576) < -39);
			Check("nowMusicAtStart", th.musicThen == 0);
			Next();
		}
		// the hall is sealed NOW: its one door is bolted on the vestibule's side
		if (S()) Go(mo, 300, 80);
		if (S()) Go(mo, 700, 80);
		if (S()) Go(mo, 990, 384);
		if (S()) Use(mo, 0);
		if (S()) Push(mo, 0, 35);
		if (S()) { Check("hallSealedNow", !Open(1032, 384) && mo.pos.x < 1024, Where(mo)); Next(); }
		// the desk NOW is smashed
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 512, 222);
		if (S()) Use(mo, 270);
		if (S()) { Check("deskSmashedNow", Said("smashed"), h.said); Next(); }
		// through the clocked door into the hall THEN
		if (S()) Go(mo, 512, 280);
		if (S()) Through(mo, 90);
		if (S()) { Check("walkedIntoHallThen", InThen(mo) && mo.pos.y < OFF + 320 && abs(Actor.DeltaAngle(mo.angle, 270)) < 2, Where(mo)); Next(); }
		if (S()) Wait(3);
		if (S()) { Check("thenMusicThen", th.musicThen == 1); Next(); }
		if (S()) Go(mo, 512, OFF + 222);
		if (S()) Use(mo, 270);
		if (S()) { Check("deskWantsKeys", Said("keys") && !desk.started, h.said); Next(); }
		// take it THEN: both frames empty
		if (S()) Go(mo, 512, OFF + 290);
		if (S()) Use(mo, 90);
		if (S()) { Check("tookClockedThen", h.carried == clocked && !F(101).door && !F(121).door, h.said); Next(); }
		// to the vestibule THEN; the turnstile lets no door through
		if (S()) Go(mo, 512, OFF + 232);
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 700, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 472);
		if (S()) Push(mo, 0, 35);
		if (S()) { Check("noDoorPastTurnstile", mo.pos.x < 1296 && h.carried == clocked, Where(mo) .. " " .. h.said); Next(); }
		// out over the goods edge into the pocket, door in hand; not back up
		if (S()) Go(mo, 1250, OFF + 320);
		if (S()) Push(mo, 0, 30);
		if (S()) { Check("downTheGoodsEdge", mo.pos.x > 1316 && abs(mo.pos.z + 40) < 1 && h.carried == clocked, Where(mo)); Next(); }
		if (S()) Push(mo, 180, 40);
		if (S()) { Check("goodsEdgeOneWay", mo.pos.x > 1312, Where(mo)); Next(); }
		// hang it in 123 (THEN, any door): its shadow in 103 NOW
		if (S()) Go(mo, 1470, OFF + 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("hungIn123", F(123).door == clocked && F(103).door == shadow && !h.carried, h.said); Next(); }
		if (S()) Through(mo, 0);
		if (S()) { Check("outOf103Now", !InThen(mo) && mo.pos.x > 1312 && mo.pos.x < 1504, Where(mo)); Next(); }
		if (S()) Go(mo, 1470, 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClockedNow", h.carried == clocked && !F(103).door && !F(123).door, h.said); Next(); }

		// --- the cellar: hang it in 105, shut the valve THEN, the pit drains, the store, key 2 ------------
		if (S()) Go(mo, 1408, 520);
		if (S()) Go(mo, 1408, 1472);
		if (S()) Go(mo, 1340, 1472);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1180, 1472);
		if (S()) Go(mo, 1200, 1280);
		if (S()) Use(mo, 0);
		if (S()) { Check("hungIn105", F(105).door == clocked && F(125).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 0);
		if (S()) { Check("inCellarThen", InThen(mo) && mo.pos.x < 1232 && mo.pos.x > 1056, Where(mo)); Next(); }
		if (S()) Go(mo, 1152, OFF + 1570);
		if (S()) Use(mo, 90);
		if (S()) Wait(3);
		if (S())
		{
			Check("valveShutThen", Cause(VALVE).setting == 0, String.Format("setting %d", Cause(VALVE).setting));
			Check("valveLine", h.said == "The valve was never opened.", h.said);
			Next();
		}
		if (S()) Go(mo, 1200, OFF + 1280);
		if (S()) Through(mo, 0);
		if (S()) Wait(80);
		if (S()) { Check("dryPit", !InThen(mo) && Water() <= PIT + 1, String.Format("water %.1f %s", Water(), Where(mo))); Next(); }
		if (S()) Go(mo, 1200, 1280);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClockedFrom105", h.carried == clocked, h.said); Next(); }
		if (S()) Go(mo, 1080, 1136);
		if (S()) Go(mo, 816, 1136);
		if (S()) { Check("downThePitStair", abs(mo.pos.z - PIT) < 2, Where(mo)); Next(); }
		if (S()) Go(mo, 800, 1540);
		if (S()) Go(mo, 672, 1560);
		if (S()) Use(mo, 90);
		if (S()) Wait(40);
		if (S()) { let pd = PDoor(); Check("storeOpens", pd && pd.IsOpen(), h.said); Next(); }
		if (S()) Go(mo, 672, 1700);
		if (S()) { Check("key2", h.Has(mo, 2), Where(mo)); Next(); }
		if (S()) Go(mo, 672, 1560);
		if (S()) Go(mo, 800, 1540);
		if (S()) Go(mo, 860, 1136);
		if (S()) Go(mo, 1080, 1136);
		if (S()) { Check("upThePitStair", abs(mo.pos.z + 40) < 2, Where(mo)); Next(); }
		if (S()) Go(mo, 1180, 1472);
		if (S()) Go(mo, 1215, 1472);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1472);

		// --- the goods bay: hang it in 108, start the belt THEN, up the heap, RED ------------------------
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1480, 1312);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1600, 1312);
		if (S()) Go(mo, 1712, 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("hungIn108", F(108).door == clocked && F(128).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("inBayThen", InThen(mo) && mo.pos.x > 1568, Where(mo)); Next(); }
		if (S()) Go(mo, 1728, OFF + 1300);
		if (S()) Go(mo, 1664, OFF + 1128);
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S())
		{
			Check("beltRunsThen", Cause(BELT).setting == 1);
			Check("beltLine", h.said == "The belt has run for forty years.", h.said);
			Next();
		}
		if (S()) Go(mo, 1728, OFF + 1300);
		if (S()) Go(mo, 1712, OFF + 1500);
		if (S()) Through(mo, 90);
		if (S()) Wait(80);
		if (S()) { Check("heapUp", abs(FZ(1872, 1150) + 16) < 1 && abs(FZ(1936, 1150) - 8) < 1 && abs(FZ(2000, 1150) - 32) < 1 && !InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 1800, 1260);
		if (S()) Go(mo, 1872, 1150);
		if (S()) Go(mo, 1936, 1150);
		if (S()) Go(mo, 2000, 1150);
		if (S()) Go(mo, 2096, 1150);
		if (S()) { Check("galleryOnFoot", abs(mo.pos.z - 56) < 1, Where(mo)); Next(); }
		if (S()) Go(mo, 2096, 1440);
		if (S()) Use(mo, 90);
		if (S()) { Check("tookRed", h.carried == red, h.said); Next(); }
		if (S()) Go(mo, 1990, 1450);
		if (S()) Go(mo, 1600, 1312);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1312);
		// 103 takes the clocked door only, NOW
		if (S()) Go(mo, 1408, 520);
		if (S()) Go(mo, 1470, 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("plainRefusedAt103", h.carried == red && !F(103).door && h.said == "This frame takes only the clocked door.", h.said); Next(); }

		// --- RED hung in 105: the lobby THEN, key 1 and its ambush -----------------------------------
		if (S()) Go(mo, 1408, 1472);
		if (S()) Go(mo, 1340, 1472);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1180, 1472);
		if (S()) Go(mo, 1200, 1280);
		if (S()) Use(mo, 0);
		if (S()) { Check("redHungIn105", F(105).door == red, h.said); Next(); }
		if (S()) Through(mo, 0);
		if (S()) { Check("intoLobbyThen", InThen(mo) && mo.pos.x > LX && mo.pos.x < LX + 1024, Where(mo)); Next(); }
		if (S()) Go(mo, LX + 330, OFF + 320);
		if (S()) Go(mo, LX + 330, OFF + 470);
		if (S()) Go(mo, LX + 512, OFF + 470);
		if (S()) { Check("key1", h.Has(mo, 1), Where(mo)); Next(); }
		if (S()) Wait(250);
		if (S()) { Check("key1Ambush", Ambushers(1) == 0, String.Format("%d still to come", Ambushers(1))); Next(); }
		if (S()) Go(mo, LX + 330, OFF + 470);
		if (S()) Go(mo, LX + 330, OFF + 320);
		if (S()) Go(mo, LX + 40, OFF + 320);
		if (S()) Through(mo, 180);
		if (S()) { Check("backFromLobby", !InThen(mo) && mo.pos.x < 1232 && mo.pos.x > 1056, Where(mo)); Next(); }

		// --- the clocked door from 108 to 106: optics, the beam to A, BLUE ------------------------------
		if (S()) Go(mo, 1215, 1472);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1472);
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1480, 1312);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1600, 1312);
		if (S()) Go(mo, 1712, 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("tookClockedFrom108", h.carried == clocked, h.said); Next(); }
		if (S()) Go(mo, 1600, 1312);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1408, 2228);
		if (S()) Use(mo, 90);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2380);
		if (S()) Go(mo, 1568, 2360);
		if (S()) Use(mo, 270);
		if (S()) { Check("hungIn106", F(106).door == clocked && F(126).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 270);
		if (S()) { Check("inOpticsThen", InThen(mo) && mo.pos.y > OFF + 2320, Where(mo)); Next(); }
		if (S()) Go(mo, 1248, OFF + 2350);
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S()) { Check("beamLine", h.said == "The beam was never switched on.", h.said); Next(); }
		if (S()) Wait(10);
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S()) { Check("beamAThen", Cause(BEAM).setting == 1, String.Format("setting %d", Cause(BEAM).setting)); Next(); }
		if (S()) Go(mo, 1568, OFF + 2360);
		if (S()) Through(mo, 270);
		if (S()) Wait(160);
		if (S()) { Check("holeAAlone", CZ(1144, 2576) > 50 && CZ(1408, 2840) < -39 && CZ(1672, 2576) < -39 && !InThen(mo),
			String.Format("A %.0f B %.0f C %.0f", CZ(1144, 2576), CZ(1408, 2840), CZ(1672, 2576))); Next(); }
		if (S()) Go(mo, 1200, 2576);
		if (S()) Go(mo, 1090, 2576);
		if (S()) Use(mo, 180);
		if (S()) { Check("tookBlue", h.carried == blue, h.said); Next(); }

		// --- BLUE hung in 108: the vestibule NOW; the bolts drawn; the hall wakes -----------------------
		if (S()) Go(mo, 1200, 2576);
		if (S()) Go(mo, 1408, 2345);
		if (S()) Use(mo, 270);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2200);
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1480, 1312);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1600, 1312);
		if (S()) Go(mo, 1712, 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("blueHungIn108", F(108).door == blue, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) Go(mo, 1168, 300);
		if (S()) Wait(40);
		if (S()) { Check("boltsDrawn", Open(1032, 384) && Open(1304, 304) && mo.pos.x > 1040 && mo.pos.x < 1296, Where(mo)); Next(); }
		if (S()) Wait(300);
		if (S()) { Check("hallWakes", Ambushers(62) == 0, String.Format("%d still to come", Ambushers(62))); Next(); }
		// the clocked door from 106
		if (S()) Go(mo, 1250, 304);
		if (S()) Go(mo, 1340, 304);
		if (S()) Go(mo, 1408, 400);
		if (S()) Go(mo, 1408, 2228);
		if (S()) Use(mo, 90);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2380);
		if (S()) Go(mo, 1568, 2360);
		if (S()) Use(mo, 270);
		if (S()) { Check("tookClockedFrom106", h.carried == clocked, h.said); Next(); }

		// --- the desk with both keys and no door in the machine: into the pocket by 103, up the turnstile --
		if (S()) Go(mo, 1408, 2345);
		if (S()) Use(mo, 270);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2200);
		if (S()) Go(mo, 1408, 520);
		if (S()) Go(mo, 1470, 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("clockedIn103", F(103).door == clocked, h.said); Next(); }
		if (S()) Through(mo, 0);
		if (S()) { Check("inPocketThen", InThen(mo) && mo.pos.x > 1312, Where(mo)); Next(); }
		if (S()) Go(mo, 1340, OFF + 472);
		if (S()) Push(mo, 180, 30);
		if (S()) { Check("upTheTurnstile", mo.pos.x < 1296 && InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 1250, OFF + 384);
		if (S()) Go(mo, 1060, OFF + 384);
		if (S()) Go(mo, 700, OFF + 384);
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 512, OFF + 222);
		if (S()) Use(mo, 270);
		if (S()) { Check("deskRefusesWithoutDoor", Said("The frame is empty.") && !desk.started, h.said); Next(); }
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 700, OFF + 384);
		if (S()) Go(mo, 1060, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 320);
		if (S()) Push(mo, 0, 30);
		if (S()) Go(mo, 1470, OFF + 480);
		if (S()) Through(mo, 0);
		if (S()) Go(mo, 1470, 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClockedLast", h.carried == clocked, h.said); Next(); }

		// --- into the hall NOW by the vestibule; the clocked door into 101; the desk; out ---------------------
		if (S()) Go(mo, 1408, 304);
		if (S()) Go(mo, 1250, 304);
		if (S()) Go(mo, 1100, 384);
		if (S()) Go(mo, 960, 384);
		if (S()) { Check("hallNowFromVestibule", mo.pos.x < 1024 && !InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 512, 232);                                                  // between the machine's wings
		if (S()) Go(mo, 512, 280);
		if (S()) Use(mo, 90);
		if (S()) { Check("clockedBackIn101", F(101).door == clocked && F(121).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) Go(mo, 512, OFF + 222);
		if (S()) Use(mo, 270);
		if (S()) Wait(5);
		if (S()) { Check("machineStarts", desk.started, h.said); Next(); }
		if (S()) Wait(100);
		if (S()) { Check("shutterOpen", Open(512, OFF + 776), String.Format("shutter %.0f", CZ(512, OFF + 776))); Next(); }
		if (S()) Done();
		if (S()) Go(mo, 700, OFF + 600);
		if (S()) Go(mo, 512, OFF + 700);
		if (S()) Go(mo, 512, OFF + 860);
		if (S()) Go(mo, 600, OFF + 912);
		if (S()) Go(mo, 720, OFF + 912);
	}

	override void WorldUnloaded(WorldEvent e)
	{
		if (!Testing() || CVar.GetCVar("ajar_autotest").GetInt() != 1) return;
		Console.Printf("AJARTEST outByTheWayOut=%d  (step %d, %s)", desk && desk.started && th && players[consoleplayer].mo && th.when.InThen(players[consoleplayer].mo.pos.xy), step, e.NextMap);
	}

	// === MODE=2: the causes set by shots from NOW through the clocked door (posed) ===========================
	double AimThrough(Actor mo, int src, int dst, Vector2 p)
	{
		Vector2 img = AjarSight.ImageThrough(h.FindLine(src), h.FindLine(dst), p);
		return VectorAngle(img.x - mo.pos.x, img.y - mo.pos.y);
	}
	void Shoot(Actor mo, double ang)
	{
		mo.angle = ang; mo.pitch = 0;
		FTranslatedLineTarget t;
		let puff = mo.LineAttack(ang, 4096, 0, 10, 'Hitscan', "BulletPuff", LAF_NORANDOMPUFFZ, t);
		Info(String.Format("shot at %.1f: puff %s, hit %s", ang, puff ? String.Format("(%.0f,%.0f,%.0f)", puff.pos.x, puff.pos.y, puff.pos.z) : "none",
			t.linetarget ? t.linetarget.GetClassName() : 'none'));
	}

	void Shots(Actor mo)
	{
		if (S()) Wait(2);
		if (S()) { Pose(mo, 512, 280, 90); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("tookClocked", h.carried == clocked, h.said); Next(); }
		// the valve, from the landing through 105
		if (S()) { Pose(mo, 1200, 1280, 0); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("hungIn105", F(105).door == clocked, h.said); Next(); }
		if (S()) { Shoot(mo, AimThrough(mo, 105, 125, (588, OFF + 1376))); Next(); }
		if (S()) Wait(3);
		if (S()) { Check("valveShotShut", Cause(VALVE).setting == 0, String.Format("setting %d", Cause(VALVE).setting)); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("shotPitDry", Water() <= PIT + 1, String.Format("water %.1f", Water())); Next(); }
		if (S()) Wait(40);
		if (S()) { Shoot(mo, AimThrough(mo, 105, 125, (588, OFF + 1376))); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("valveShotOpenAgain", Cause(VALVE).setting == 1 && abs(Water() + 72) < 1, String.Format("water %.1f", Water())); Next(); }
		if (S()) Wait(200);
		if (S()) { Check("fullAgainAmbush", Ambushers(63) == 0, String.Format("%d still to come", Ambushers(63))); Next(); }
		if (S()) { Pose(mo, 1200, 1280, 0); PressUse(mo); Next(); }
		if (S()) Wait(20);
		// the belt, from the bay through 108
		if (S()) { Pose(mo, 1712, 1500, 90); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("hungIn108", F(108).door == clocked, h.said); Next(); }
		if (S()) { Shoot(mo, AimThrough(mo, 108, 128, (1760, OFF + 1100))); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("beltShotRunning", Cause(BELT).setting == 1 && abs(FZ(2000, 1150) - 32) < 1, String.Format("setting %d step3 %.1f", Cause(BELT).setting, FZ(2000, 1150))); Next(); }
		if (S()) { Pose(mo, 1712, 1500, 90); PressUse(mo); Next(); }
		if (S()) Wait(20);
		// the beam, from optics through 106: A
		if (S()) { Pose(mo, 1568, 2360, 270); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("hungIn106", F(106).door == clocked, h.said); Next(); }
		// A lies far to the side: from the middle of the mouth the line grazes 126's jamb; a step west of it
		if (S()) { Pose(mo, 1527, 2360, 270); Next(); }
		if (S()) { Shoot(mo, AimThrough(mo, 106, 126, (1280, OFF + 2820))); Next(); }
		if (S()) Wait(160);
		if (S()) { Check("beamShotA", Cause(BEAM).setting == 1 && CZ(1144, 2576) > 50 && CZ(1672, 2576) < -39 && CZ(1408, 2840) < -39,
			String.Format("setting %d A %.0f B %.0f C %.0f", Cause(BEAM).setting, CZ(1144, 2576), CZ(1408, 2840), CZ(1672, 2576))); Next(); }
		if (S()) Wait(40);
		if (S()) { Pose(mo, 1568, 2360, 270); Next(); }
		if (S()) { Shoot(mo, AimThrough(mo, 106, 126, (1504, OFF + 2820))); Next(); }
		if (S()) Wait(160);
		if (S()) { Check("beamShotB", Cause(BEAM).setting == 2 && CZ(1408, 2840) > 50 && CZ(1144, 2576) < -39, String.Format("setting %d", Cause(BEAM).setting)); Next(); }
		if (S()) Done();
	}

	// === MODE=3: views (a screenshot every 70 tics: tools/smoke_MAP21_3.cfg) ===========================
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void SetNow(int tid, int s) { let c = Cause(tid); th.SetCause(c, s, null); th.Snap(c); }
	void Views(Actor mo)
	{
		if (S()) { mo.bInvisible = true; Wait(15); }
		if (S()) { View(mo, "the start NOW: the machine and its desk; through 101 the hall THEN, its desk and its clock", 512, 40, 90); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the same spot THEN: through 121 the hall NOW", 512, OFF + 40, 90); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "hall NOW from the north-east: the machine, Doom's stone, the benches' footprints", 980, 740, 215, 8); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "hall THEN from the north-east: the brass shutter, the benches", 980, OFF + 740, 215, 8); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "vestibule NOW: bolted both ways, BLUE's far side", 1060, 530, 315); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "vestibule THEN: the porter's desk, the goods edge, the turnstile", 1060, OFF + 530, 315); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the corridor NOW from its south end", 1408, 176, 90); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the pocket THEN: the night grille, NO DOORS BEYOND THIS POINT, frame 123", 1480, OFF + 610, 200); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the cellar NOW, the valve open (found): the pit full", 1220, 1580, 220, 15); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the cellar THEN: the pit dry, the tanks, the target on the ledge", 1220, OFF + 1580, 220, 15); Next(); }
		if (S()) Wait(69);
		if (S()) { SetNow(VALVE, 0); View(mo, "the cellar NOW, the valve shut: the pit dry, the store's pressure door", 1220, 1580, 220, 15); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the goods bay NOW, the belt standing (found): the hatch stair, the gallery", 1590, 1520, 330); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the goods bay THEN: the belt, the racks", 1590, OFF + 1520, 330); Next(); }
		if (S()) Wait(69);
		if (S()) { SetNow(BELT, 1); View(mo, "the goods bay NOW, the belt running: the heap up to the gallery", 1590, 1520, 330); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "optics NOW, the beam at C (found): hole C open", 1180, 2340, 40); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "optics THEN: the emitter at C, the targets", 1180, OFF + 2340, 40); Next(); }
		if (S()) Wait(69);
		if (S()) { SetNow(BEAM, 1); View(mo, "optics NOW, the beam at A: hole A open, C shut", 1640, 2340, 145); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the lobby THEN: RED's far side, the desk, the clock", LX + 990, OFF + 600, 215); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the lobby NOW (the secret): dust, the megasphere", LX + 990, 600, 215); Next(); }
		if (S()) Wait(69);
		if (S()) { desk.Start(mo); View(mo, "the hall THEN, the machine running: the shutter opening", 760, OFF + 520, 120); Next(); }
		if (S()) Wait(69);
		if (S()) { View(mo, "the hall THEN, the machine running: the shutter open, the night room", 512, OFF + 600, 90); Next(); }
		if (S()) Wait(69);
	}
}
