// MAP22 "Day Return" (tools/map_dayreturn.py; PLAN.md, "MAP22 "Day Return"" and "MAP22 bigger"): the level's own
// script, and its checks (DayReturnTest, below). THEN is NOW + (0, 12288). Frames NOW / THEN, every one of a bus
// twinned and taking any door: 101/121 door 2 of the 10 (RED hangs in 121 at the start), 102/122 door 7, 104/124
// door 4; 106/126 door 3 of the 20, at the other stop; 123 door 6 THEN (brass, any colour door, no twin); 190 HOME
// in the night room THEN (BLUE's alone), 105/125 the night room's south wall (the clocked door's alone; 125 east
// of the gate THEN). The gate THEN: a bolted door (sector tag 2202, its bolt side line 311) across the night room,
// opened by crossing the line north of frame 125. Far sides NOW / THEN: RED 201/221 the theatre's foyer, BLUE
// 202/222 the night room, GREEN 203/223 door 3 (there is no GREEN), YELLOW 204/224 the depot. Fixed doorways:
// 1 the hotel and 2 the station (THEN); door 8 of the 10 to door 1 of the 20, 3 NOW and 4 THEN; the pit under the
// stage door to door 2 of the 20, 5 and 6; door 4 of the 20 to the observatory's library, 7 and 8. Locked doors:
// the museum's on the square (key 1; mouth line 301 NOW, 321 THEN), the dome's (key 2; 302, 322), the shelter's
// brass door THEN (keys 3 and 4; 310). Key 3 lies on the dome's floor NOW.

// The turn: the first time the clocked door hangs in a twinned frame (AjarThenHandler.joinedAt, then.zs). Once:
// the line on the screen; the music THEN from the quiet piece to the fight's; the square's company NOW (tid
// SQUARE_TID) woken and set on the player. What it brings THEN comes by ambush (cause 64, ajar.zs), each when the
// player is next there; three of those carry keys 1, 2 and 4 (AjarKeyBearer). Taking the clocked door down undoes nothing.
class AjarDayReturn : EventHandler
{
	const SQUARE_TID = 2201;
	const PEACE = "AJM_EMY4";
	const FIGHT = "AJM_EMY5";
	bool turned;
	int turnedAt;
	int woken;                 // the square's company woken at the turn (the tests)

	static AjarDayReturn Get() { return AjarDayReturn(EventHandler.Find("AjarDayReturn")); }
	static bool Here() { return level.mapname ~== "MAP22"; }

	override void WorldLoaded(WorldEvent e)
	{
		if (!Here() || e.IsSaveGame) return;
		let th = AjarThenHandler.Get();
		if (th) th.thenPiece = PEACE;
	}

	override void WorldTick()
	{
		if (!Here() || turned) return;
		let th = AjarThenHandler.Get();
		if (!th || !th.ready || th.joinedAt < 0) return;
		turned = true;
		turnedAt = level.maptime;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say("The line runs to the same stop, forty years on.\nSomething is coming the other way.");
		th.SetThenMusic(FIGHT);
		let mo = players[consoleplayer].mo;
		let it = level.CreateActorIterator(SQUARE_TID);
		Actor a;
		while (a = it.Next())
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			woken++;
			a.bAmbush = false;
			if (!mo) continue;
			a.target = mo;
			if (a.SeeState) a.SetState(a.SeeState);
		}
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info the turn at t=%d: %d of the square's company woken", level.maptime, woken);
	}
}

// A room key carried by a monster (an ambusher of the turn with args[4]: AjarHandler.AmbushTick): it shows over
// the bearer's head, the game's own key, and when the bearer dies (or is gone by any way) the key is the player's
// at once, wherever the body falls: no key can drop out of reach.
class AjarKeyBearer : Actor
{
	Actor bearer;
	int key;
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +FORCEXYBILLBOARD }
	States
	{
	Spawn:
		AJK1 A -1 Bright;
		Stop;
	Key2:
		AJK2 A -1 Bright;
		Stop;
	Key3:
		AJK3 A -1 Bright;
		Stop;
	Key4:
		AJK4 A -1 Bright;
		Stop;
	}

	static AjarKeyBearer Bear(Actor m, int key)
	{
		let k = AjarKeyBearer(Actor.Spawn("AjarKeyBearer", m.pos + (0, 0, m.height + 10)));
		if (!k) return null;
		k.bearer = m;
		k.key = key;
		if (key == 2) k.SetStateLabel("Key2");
		else if (key == 3) k.SetStateLabel("Key3");
		else if (key == 4) k.SetStateLabel("Key4");
		return k;
	}

	override void Tick()
	{
		Super.Tick();
		if (bearer && bearer.health > 0)
		{
			SetOrigin(bearer.pos + (0, 0, bearer.height + 10), true);
			return;
		}
		let mo = players[consoleplayer].mo;
		if (mo)
		{
			mo.GiveInventory(String.Format("AjarKey%d", key), 1);
			mo.A_StartSound("misc/k_pkup", CHAN_ITEM);
		}
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(String.Format("It carried key %d.", key));
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info key %d given at t=%d", key, level.maptime);
		Destroy();
	}
}

// The checks: MAP=MAP22 MODE=n tools/smoke.sh.
//   1 the solver's way through (tools/puzzle22.py), to the way out: through every door and doorway on foot and by
//     USE (hanging, taking, swapping, the brass door's lock), the walks inside a place posed (the excerpts are
//     walkable by construction: ajarmap.excerpt); the bearers killed by the script; checks on the way
//   2 the turn by itself (posed): the clocked door hung in 124 (an ordinary frame), the line, the music, the square's company woken, the
//     stop's two waves; taken down and hung again in 122: no second turn
//   3 views (tools/smoke_MAP22_3.cfg shoots every 70 tics; two a view)
class DayReturnTest : EventHandler
{
	const OFF = 12288;
	const TY = -4480;
	const HX = -6400;
	const SX = 3200;
	const WALKKEY = 0x1900;
	int tic, checks, fails;
	int step, cur, stepTic;
	bool entered;
	AjarHandler h;
	AjarThenHandler th;
	AjarDoor clocked, shadow, red, blue, yellow;
	int viewN;
	const GATE_X = 504;        // the middle of the gate's wall (map_dayreturn.py, GATE_X + 8), on the runner at y -432
	const GATE_TAG = 2202;
	bool GateOpen() { return CZ(GATE_X, OFF - 432) > FZ(GATE_X, OFF - 432) + 56; }
	bool GateShut() { return CZ(GATE_X, OFF - 432) <= FZ(GATE_X, OFF - 432) + 1; }
	bool InNightRoom(Actor mo) { double y = mo.pos.y - (InThen(mo) ? OFF : 0); return mo.pos.x > 304 && mo.pos.x < 624 && y > -560 && y < -304 && abs(mo.pos.z - 64) < 1; }

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP22"; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

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
	bool Said(string part) { return h.said.IndexOf(part) >= 0; }
	AjarDayReturn DR() { return AjarDayReturn.Get(); }
	int Left(int cause, int near = -1)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == cause && (near < 0 || (a.args[3] != 0) == (near != 0))) n++;
		return n;
	}
	AjarKeyBearer Bearer(int key)
	{
		let it = ThinkerIterator.Create("AjarKeyBearer");
		AjarKeyBearer b;
		while (b = AjarKeyBearer(it.Next())) if (b.key == key) return b;
		return null;
	}
	int MonstersThen()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && th.when.InThen(a.pos.xy)) n++;
		return n;
	}
	int ItemsThen()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Inventory");
		Inventory a;
		while (a = Inventory(it.Next())) if (!a.owner && th.when.InThen(a.pos.xy)) n++;
		return n;
	}

	// --- the player's controls, as map21.zs ------------------------------------------------------
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
	void Put(Actor mo, double x, double y, double ang) { Pose(mo, x, y, ang); Next(); }
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
	void Push(Actor mo, double ang, int n)
	{
		if (First()) { pushAngle = ang; pushing = true; walking = false; }
		if (Age() >= n) { pushing = false; Keys(); Next(); }
	}
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
	// Wait until key's bearer has come (at most n tics), then kill it, as the player would
	void KillBearer(Actor mo, int key, int n)
	{
		First();
		let b = Bearer(key);
		if (b && b.bearer)
		{
			Info(String.Format("key %d's bearer: a %s at (%.0f,%.0f) after %d tics", key, b.bearer.GetClassName(), b.bearer.pos.x, b.bearer.pos.y, Age()));
			b.bearer.DamageMobj(mo, mo, b.bearer.health + 1000, 'None');
			Next();
			return;
		}
		if (Age() > n) { Check(String.Format("bearerOfKey%dCame", key), false, Where(mo)); Next(); }
	}
	// the way round the bus, THEN (dy = OFF) or NOW (0): from in front of its south face to behind it, by its east end
	// (the walks of MODE 1 that cross the square are walked, not posed)

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
				else if (d.args[1] == 2) blue = d;
				else if (d.args[1] == 4) yellow = d;
			}
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			Check("nobodyThenInPeace", MonstersThen() == 0, String.Format("%d alive then", MonstersThen()));
			Info(String.Format("pick-ups lying then at the start: %d", ItemsThen()));
			if (mode != 2)
			{
				let mi = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(mi.Next())) if (a.bIsMonster) a.Destroy();
			}
		}
		cur = 0;
		if (mode == 1) Walk(mo);
		else if (mode == 2) TheTurn(mo);
		else if (mode == 3) Views(mo);
		Drive(mo);
		if (tic % 70 == 0 && mode != 3) Info(String.Format("t=%d step %d %s carried %s", tic, step, Where(mo), h.carried ? h.carried.Label() : "-"));
	}

	void Done() { Console.Printf("AJARTEST dayReturnDone=1 checks=%d failed=%d", checks, fails); Next(); }

	// round the bus's east end, from its south face's pavement to the lane behind it (or back): at time dy
	void ToBack(Actor mo, int dy)
	{
		if (S()) Go(mo, 470, -24 + dy);
		if (S()) Go(mo, 470, 220 + dy);
	}
	void ToFront(Actor mo, int dy)
	{
		if (S()) Go(mo, 470, 220 + dy);
		if (S()) Go(mo, 470, -24 + dy);
	}

	// === MODE=1: the way through ===================================================================
	// The solver's way (tools/puzzle22.py), in one of its orders, with a look at every new thing on it: the peace
	// first (the museum, the brass door and the dome locked; door 8 to the other stop and its door 4 to the library);
	// YELLOW in the 20's frame 126 for the depot; the clocked door into 124 (the turn); key 2; the dome then with key
	// 2, out by its stair carrying nothing; RED to the theatre now, BLUE, out by the pit to the other stop; BLUE in
	// 104 for the night room now, the gate as before; key 1, the brass door shut with keys 1 and 2; the museum now
	// with key 1; key 3 in the dome now, out by its stair carrying BLUE; key 4 from the museum's mancubus then; the
	// brass door with keys 3 and 4, the last fight; HOME
	bool DoorOpen(double x, double y) { return CZ(x, y) > FZ(x, y) + 56; }
	bool DoorShut(double x, double y) { return CZ(x, y) <= FZ(x, y) + 1; }
	const BY = 3168;            // the 20's south face (map_dayreturn.py)
	const MUSEUM_X = -520;      // the middle of the museum's door, its mouth on the square at x -512, y -400..-336
	const DOME_Y = 1392;        // the middle of the dome's door, x 1824..1888
	string Shut(double x, double y) { return String.Format("ceiling %.0f over %.0f", CZ(x, y), FZ(x, y)); }
	bool InLibrary(Actor mo, bool then) { double y = mo.pos.y - (then ? OFF : 0); return InThen(mo) == then && mo.pos.x > 1600 && mo.pos.x < 2112 && y > 1000 && y < 1384 && abs(mo.pos.z) < 1; }
	bool AtStop2(Actor mo, bool then) { double y = mo.pos.y - (then ? OFF : 0); return InThen(mo) == then && abs(mo.pos.x) < 640 && y > BY - 288 && y < BY + 432; }
	bool InHall(Actor mo, bool then) { double y = mo.pos.y - (then ? OFF : 0); return InThen(mo) == then && mo.pos.x > -1168 && mo.pos.x < -528 && y > -640 && y < -128; }

	void Walk(Actor mo)
	{
		if (S()) { Wait(2); }
		if (S())
		{
			Check("startsThen", InThen(mo), Where(mo));
			Check("redHungIn121", red && F(121).door == red && red.args[0] == 221 && !F(101).door, red ? String.Format("RED leads to %d", red.args[0]) : "no RED");
			Check("clockedLeansInDepotThen", clocked && !clocked.frame && !clocked.carried && InThen(clocked) && clocked.pos.y > OFF + 544 && clocked.pos.y < OFF + 992);
			Check("yellowLeansOnPlatformThen", yellow && !yellow.frame && InThen(yellow) && yellow.pos.x > SX);
			Check("blueLeansInTheatreNow", blue && !blue.frame && !InThen(blue) && blue.pos.y < 0);
			Check("noKeys", !h.Has(mo, 1) && !h.Has(mo, 2) && !h.Has(mo, 3) && !h.Has(mo, 4));
			Check("peaceMusicThen", th.musicThen == 1 && th.ThenMusic() == "AJM_EMY4", th.ThenMusic());
			Check("notTurned", !DR().turned && th.joinedAt < 0);
			Check("gatesCompanyWaits", Left(62) > 0, String.Format("%d", Left(62)));
			Check("frame104Ordinary", F(104) && F(124) && F(104).args[4] == 0 && F(124).args[4] == 0, F(104) ? String.Format("only %d / %d", F(104).args[4], F(124).args[4]) : "no 104");
			Check("frames106And126", F(106) && F(126) && !F(106).door && !F(126).door);
			Check("key3LiesInTheDomeNow", Key3Lying());
			Next();
		}
		// the gate THEN, from its west side (posed: the way there needs keys 3 and 4): bolted, USE does nothing
		if (S()) { Check("gateShutAtStart", GateShut(), String.Format("ceiling %.0f", CZ(GATE_X, OFF - 432))); Next(); }
		if (S()) Put(mo, 470, OFF - 432, 0);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) { Check("gateBoltedFromTheWest", GateShut(), String.Format("ceiling %.0f", CZ(GATE_X, OFF - 432))); Next(); }
		if (S()) Put(mo, -64, OFF - 592, 90);
		// the museum THEN: locked, no key 1
		if (S()) Go(mo, -400, OFF - 368);
		if (S()) Go(mo, -470, OFF - 368);
		if (S()) Use(mo, 180);
		if (S()) Wait(30);
		if (S()) { Check("museumLockedThen", DoorShut(MUSEUM_X, OFF - 368), Shut(MUSEUM_X, OFF - 368)); Next(); }
		// the shelter's brass door THEN: locked, no keys
		if (S()) Go(mo, -420, OFF - 250);
		if (S()) Go(mo, 100, OFF - 200);
		if (S()) Go(mo, 320, OFF - 180);
		if (S()) Use(mo, 270);
		if (S()) Wait(30);
		if (S()) { Check("brassDoorLocked", DoorShut(320, OFF - 216), Shut(320, OFF - 216)); Next(); }
		// in peace: door 8 of the 10 to the other stop, its door 4 to the library, the dome locked; back by door 1
		if (S()) Go(mo, 320, OFF - 30);
		ToBack(mo, OFF);
		if (S()) Go(mo, -192, OFF + 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("door8ToTheOtherStopThen", AtStop2(mo, true) && abs(mo.pos.x + 320) < 40 && mo.pos.y < OFF + BY, Where(mo)); Next(); }
		ToBack(mo, OFF + BY);
		if (S()) Go(mo, 64, OFF + BY + 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("door4OfThe20ToTheLibraryThen", InLibrary(mo, true), Where(mo)); Next(); }
		if (S()) Go(mo, 1856, OFF + 1360);
		if (S()) Use(mo, 90);
		if (S()) Wait(30);
		if (S()) { Check("domeLockedThenWithoutKey2", DoorShut(1856, OFF + DOME_Y), Shut(1856, OFF + DOME_Y)); Next(); }
		if (S()) Go(mo, 1856, OFF + 1030);
		if (S()) Through(mo, 270);
		if (S()) { Check("backByDoor4ToTheOtherStopThen", AtStop2(mo, true) && abs(mo.pos.x - 64) < 40 && mo.pos.y > OFF + BY + 144, Where(mo)); Next(); }
		ToFront(mo, OFF + BY);
		if (S()) Go(mo, -320, OFF + BY - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("door1OfThe20BackToTheLaneThen", InThen(mo) && abs(mo.pos.x + 192) < 40 && mo.pos.y > OFF + 144 && mo.pos.y < OFF + 448, Where(mo)); Next(); }
		// line 5: the station; YELLOW from its far platform
		ToFront(mo, OFF);
		if (S()) Go(mo, 192, OFF - 30);
		if (S()) Through(mo, 90);
		if (S()) { Check("line5ToStation", InThen(mo) && mo.pos.x > SX && mo.pos.x < SX + 2100, Where(mo)); Next(); }
		if (S()) Put(mo, SX + 1640, OFF + 1250, 0);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookYellow", h.carried == yellow, h.said); Next(); }
		if (S()) Put(mo, SX + 384, OFF + 70, 270);
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromStation", InThen(mo) && abs(mo.pos.x - 192) < 40 && mo.pos.y < OFF && mo.pos.y > OFF - 64, Where(mo)); Next(); }
		// YELLOW in the 20's door 3 THEN (126): the depot THEN, the clocked door
		ToBack(mo, OFF);
		if (S()) Go(mo, -192, OFF + 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("yellowCarriedToTheOtherStop", AtStop2(mo, true) && h.carried == yellow, Where(mo)); Next(); }
		if (S()) Go(mo, 192, OFF + BY - 24);
		if (S()) Use(mo, 90);
		if (S()) { Check("yellowIn126", F(126).door == yellow && yellow.args[0] == 224 && !F(106).door && !h.carried, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("yellowFrom126ToDepotThen", InThen(mo) && mo.pos.y > OFF + 544 && mo.pos.y < OFF + 700 && abs(mo.pos.z - 48) < 1, Where(mo)); Next(); }
		if (S()) Go(mo, 96, OFF + 700);
		if (S()) Go(mo, 96, OFF + 960);
		if (S()) Go(mo, 200, OFF + 960);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClocked", h.carried == clocked, h.said); Next(); }
		if (S()) { Check("stillPeace", !DR().turned && MonstersThen() == 0); Next(); }
		// out by the gate: a step down, never in
		if (S()) Go(mo, 96, OFF + 960);
		if (S()) Go(mo, 96, OFF + 700);
		if (S()) Go(mo, 464, OFF + 640);
		if (S()) Go(mo, 464, OFF + 420);
		if (S()) Wait(15);
		if (S()) { Check("downTheGate", abs(mo.pos.z) < 1 && mo.pos.y < OFF + 448, Where(mo)); Next(); }
		if (S()) Push(mo, 90, 40);
		if (S()) { Check("gateOneWay", mo.pos.y < OFF + 450, Where(mo)); Next(); }
		// the clocked door into door 4 THEN (124), an ordinary frame: the turn
		ToFront(mo, OFF);
		if (S()) Go(mo, 64, OFF - 24);
		if (S()) Use(mo, 90);
		if (S()) Wait(3);
		if (S())
		{
			Check("clockedIn124", F(124).door == clocked && F(104).door == shadow && !h.carried, h.said);
			Check("theTurn", DR().turned && Said("forty years on"), h.said);
			Check("fightMusicThen", th.ThenMusic() == "AJM_EMY5" && th.musicThen == 1, th.ThenMusic());
			Next();
		}
		if (S()) Through(mo, 90);
		if (S()) { Check("throughClockedToNow", !InThen(mo) && abs(mo.pos.x - 64) < 40 && mo.pos.y < 0 && mo.pos.y > -300, Where(mo)); Next(); }
		if (S()) Wait(3);
		if (S()) { Check("nowMusicNow", th.musicThen == 0); Next(); }
		// now, without keys (posed: the walks are later): the museum and the dome locked
		if (S()) Put(mo, -470, -368, 180);
		if (S()) Use(mo, 180);
		if (S()) Wait(30);
		if (S()) { Check("museumLockedNow", DoorShut(MUSEUM_X, -368), Shut(MUSEUM_X, -368)); Next(); }
		if (S()) Put(mo, 1856, 1360, 90);
		if (S()) Use(mo, 90);
		if (S()) Wait(30);
		if (S()) { Check("domeLockedNowWithoutKey2", DoorShut(1856, DOME_Y), Shut(1856, DOME_Y)); Next(); }
		if (S()) Put(mo, 64, -60, 90);
		if (S()) Go(mo, 64, -24);
		if (S()) Through(mo, 90);
		if (S()) { Check("backThen", InThen(mo) && mo.pos.y < OFF && abs(mo.pos.x - 64) < 40, Where(mo)); Next(); }
		// key 2: RED, where it hangs, to the theatre THEN; its bearer by the stage
		if (S()) Go(mo, -192, OFF - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("redToTheatreThen", InThen(mo) && mo.pos.y > OFF + TY + 1000 && mo.pos.y < OFF + TY + 1700, Where(mo)); Next(); }
		if (S()) Put(mo, 950, OFF + TY + 680, 330);
		if (S()) KillBearer(mo, 2, 350);
		if (S()) Wait(5);
		if (S()) { Check("key2FromItsBearer", h.Has(mo, 2) && Said("It carried key 2."), h.said); Next(); }
		if (S()) Put(mo, -224, OFF + TY + 1024 + 48, 270);
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromTheatreThen", InThen(mo) && abs(mo.pos.x + 192) < 40 && mo.pos.y < OFF, Where(mo)); Next(); }
		// the dome THEN with key 2, carrying nothing: door 8, the 20's door 4, the library, the dome; out by its stair
		if (S()) Go(mo, 470, OFF - 24);
		ToBack(mo, OFF);
		if (S()) Go(mo, -192, OFF + 200);
		if (S()) Through(mo, 270);
		ToBack(mo, OFF + BY);
		if (S()) Go(mo, 64, OFF + BY + 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("libraryThenAgain", InLibrary(mo, true) && !h.carried, Where(mo)); Next(); }
		if (S()) Go(mo, 1856, OFF + 1360);
		if (S()) Use(mo, 90);
		if (S()) Wait(30);
		if (S()) { Check("domeOpensThenWithKey2", DoorOpen(1856, OFF + DOME_Y), Shut(1856, OFF + DOME_Y)); Next(); }
		if (S()) Go(mo, 1856, OFF + 1440);
		if (S()) Go(mo, 1856, OFF + 1500);
		if (S()) Wait(10);
		if (S()) { Check("downIntoTheDomeThen", InThen(mo) && abs(mo.pos.z + 96) < 1, Where(mo)); Next(); }
		if (S()) Go(mo, 1720, OFF + 1500);
		if (S()) Go(mo, 1700, OFF + 1736);
		if (S()) Wait(35 * 3);              // (a cacodemon behind the pier comes when the player is round it)
		if (S()) { Check("theDomeThensCompanyCame", ObsThenLeft() == 0, String.Format("%d still to come", ObsThenLeft())); Next(); }
		if (S()) Go(mo, 1440, OFF + 1732);
		if (S()) Go(mo, 1440, OFF + 1352);
		if (S()) Go(mo, 1640, OFF + 1352);
		if (S()) { Check("outOfTheDomeThenByTheStairCarryingNothing", InLibrary(mo, true) && !h.carried, Where(mo)); Next(); }
		if (S()) Go(mo, 1856, OFF + 1100);
		if (S()) Go(mo, 1856, OFF + 1030);
		if (S()) Through(mo, 270);
		ToFront(mo, OFF + BY);
		if (S()) Go(mo, -320, OFF + BY - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("backToTheLaneThen", InThen(mo) && mo.pos.y > OFF + 144 && mo.pos.y < OFF + 448, Where(mo)); Next(); }
		// RED down from 121, carried through the clocked door (124) and hung in 101: the theatre NOW, BLUE
		ToFront(mo, OFF);
		if (S()) Go(mo, -192, OFF - 24);
		if (S()) Use(mo, 90);
		if (S()) { Check("redDownFrom121", h.carried == red && !F(121).door, h.said); Next(); }
		if (S()) Go(mo, 64, OFF - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("redCarriedToNow", !InThen(mo) && h.carried == red, Where(mo)); Next(); }
		if (S()) Go(mo, -192, -24);
		if (S()) Use(mo, 90);
		if (S()) { Check("redIn101", F(101).door == red && red.args[0] == 201 && !F(121).door, String.Format("RED leads to %d; ", red.args[0]) .. h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("redToTheatreNow", !InThen(mo) && mo.pos.y > TY + 1000 && mo.pos.y < TY + 1700, Where(mo)); Next(); }
		if (S()) Put(mo, 540, TY + 1450, 0);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookBlue", h.carried == blue, h.said); Next(); }
		// out by the stage door's ledge (posed on it) and the pit: the other stop NOW; back by the 20's door 1
		if (S()) Put(mo, 256, TY + 960, 0);
		if (S()) Go(mo, 420, TY + 960);
		if (S()) { Check("downIntoThePitNow", !InThen(mo) && abs(mo.pos.z + 48) < 1 && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, 570, TY + 960);
		if (S()) Through(mo, 0);
		if (S()) { Check("thePitToTheOtherStopNow", AtStop2(mo, false) && abs(mo.pos.x + 64) < 40 && mo.pos.y < BY && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, -320, BY - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("door1OfThe20BackToTheLaneNow", !InThen(mo) && abs(mo.pos.x + 192) < 40 && mo.pos.y > 144 && mo.pos.y < 448, Where(mo)); Next(); }
		// BLUE swapped for the clocked door in 104: the night room NOW, whole; the hole shut
		ToFront(mo, 0);
		if (S()) Go(mo, 64, -24);
		if (S()) Use(mo, 90);
		if (S()) { Check("blueIn104", F(104).door == blue && blue.args[0] == 202 && !F(124).door && h.carried == clocked, String.Format("BLUE leads to %d; ", blue.args[0]) .. h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("blueToNightRoomNow", !InThen(mo) && InNightRoom(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 416, -330);
		if (S()) Go(mo, 416, -260);
		if (S()) Push(mo, 90, 40);
		if (S()) { Check("noWayDownTheHoleNow", !InThen(mo) && abs(mo.pos.z - 64) < 1 && mo.pos.y > -304 && mo.pos.y < -240, Where(mo)); Next(); }
		// the clocked door in 105: the far side of the gate, THEN; the bolt drawn; the gate's company
		if (S()) Go(mo, 416, -330);
		if (S()) Go(mo, 552, -528);
		if (S()) { h.said = ""; Next(); }
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S())
		{
			Check("clockedIn105", h.carried == null && F(105).door && F(125).door && (F(105).door == clocked || F(125).door == clocked), h.said);
			Check("noSecondTurnAt105", DR().turned && !Said("forty years on") && th.ThenMusic() == "AJM_EMY5", h.said);
			Check("gateShutBefore", GateShut() && Left(62) > 0, String.Format("ceiling %.0f, %d of its company to come", CZ(GATE_X, OFF - 432), Left(62)));
			Next();
		}
		if (S()) Through(mo, 270);
		if (S()) Wait(50);
		if (S())
		{
			Check("throughClockedToTheGatesEastThen", InThen(mo) && InNightRoom(mo) && mo.pos.x > GATE_X + 8, Where(mo));
			Check("boltDrawnOnArriving", GateOpen(), String.Format("ceiling %.0f", CZ(GATE_X, OFF - 432)));
			Next();
		}
		if (S()) Wait(35 * 4);
		if (S()) { Check("gatesCompanyCame", Left(62) == 0, String.Format("%d still to come", Left(62))); Next(); }
		// the clocked door back to the bus: through it to NOW, down from 105, through BLUE, swapped for BLUE in 104
		if (S()) Go(mo, 552, OFF - 500);
		if (S()) Through(mo, 270);
		if (S()) { Check("backToNightRoomNow", !InThen(mo) && InNightRoom(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 552, -528);
		if (S()) Use(mo, 270);
		if (S()) { Check("clockedDownFrom105", h.carried == clocked && !F(105).door && !F(125).door, h.said); Next(); }
		if (S()) Go(mo, 340, -432);
		if (S()) Through(mo, 180);
		if (S()) { Check("throughBlueToTheSquareNow", !InThen(mo) && abs(mo.pos.x - 64) < 40 && mo.pos.y < 0 && mo.pos.y > -300, Where(mo)); Next(); }
		if (S()) Go(mo, 64, -24);
		if (S()) Use(mo, 90);
		if (S()) { Check("clockedBackIn104", h.carried == blue && F(104).door && F(124).door && (F(104).door == clocked || F(124).door == clocked), h.said); Next(); }
		// BLUE through the clocked door, THEN; line 1: the hotel, key 1's baron
		if (S()) Through(mo, 90);
		if (S()) { Check("blueCarriedToThen", InThen(mo) && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, -320, OFF - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("line1ToHotel", InThen(mo) && mo.pos.x < HX + 600 && mo.pos.x > HX - 2000, Where(mo)); Next(); }
		if (S()) KillBearer(mo, 1, 350);
		if (S()) Wait(5);
		if (S()) { Check("key1FromItsBearer", h.Has(mo, 1) && Said("It carried key 1."), h.said); Next(); }
		if (S()) Put(mo, HX + 256, OFF + 60, 270);
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromHotel", InThen(mo) && abs(mo.pos.x + 320) < 40 && mo.pos.y < OFF, Where(mo)); Next(); }
		// the brass door with keys 1 and 2 only: shut; the last fight waits for keys 3 and 4
		if (S()) Go(mo, -320, OFF - 200);
		if (S()) Go(mo, 100, OFF - 200);
		if (S()) Go(mo, 320, OFF - 180);
		if (S()) Use(mo, 270);
		if (S()) Wait(40);
		if (S())
		{
			Check("brassDoorShutWithKeys1And2", h.Has(mo, 1) && h.Has(mo, 2) && !h.Has(mo, 3) && DoorShut(320, OFF - 216), Shut(320, OFF - 216));
			Check("lastFightWaitsForKeys3And4", Left(65) > 0, String.Format("%d to come", Left(65)));
			Next();
		}
		// now through the clocked door (104), BLUE carried: the museum NOW opens with key 1
		if (S()) Go(mo, 320, OFF - 30);
		if (S()) Go(mo, 64, OFF - 30);
		if (S()) Through(mo, 90);
		if (S()) { Check("blueCarriedToNowAgain", !InThen(mo) && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, -400, -368);
		if (S()) Go(mo, -470, -368);
		if (S()) Use(mo, 180);
		if (S()) Wait(30);
		if (S()) { Check("museumOpensNowWithKey1", DoorOpen(MUSEUM_X, -368), Shut(MUSEUM_X, -368)); Next(); }
		if (S()) Go(mo, -580, -368);
		if (S()) { Check("intoTheMuseumNow", InHall(mo, false), Where(mo)); Next(); }
		if (S()) Go(mo, -470, -368);
		// door 8 NOW, the other stop, the 20's door 4, the library: the dome with key 2, key 3, out by the stair with BLUE
		if (S()) Go(mo, -420, -250);
		if (S()) Go(mo, -420, -60);
		if (S()) Go(mo, -520, 0);
		if (S()) Go(mo, -520, 220);
		if (S()) Go(mo, -192, 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("door8ToTheOtherStopNow", AtStop2(mo, false) && abs(mo.pos.x + 320) < 40 && mo.pos.y < BY && h.carried == blue, Where(mo)); Next(); }
		ToBack(mo, BY);
		if (S()) Go(mo, 64, BY + 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("door4OfThe20ToTheLibraryNow", InLibrary(mo, false), Where(mo)); Next(); }
		if (S()) Go(mo, 1856, 1360);
		if (S()) Use(mo, 90);
		if (S()) Wait(30);
		if (S()) { Check("domeOpensNowWithKey2", DoorOpen(1856, DOME_Y), Shut(1856, DOME_Y)); Next(); }
		if (S()) Go(mo, 1856, 1440);
		if (S()) Go(mo, 1856, 1500);
		if (S()) Wait(10);
		if (S()) { Check("downIntoTheDomeNow", !InThen(mo) && abs(mo.pos.z + 96) < 1 && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, 1990, 1500);
		if (S()) Go(mo, 1990, 1736);
		if (S()) Wait(5);
		if (S()) { Check("key3TakenInTheDomeNow", h.Has(mo, 3) && !Key3Lying() && h.carried == blue, Where(mo)); Next(); }
		if (S()) Wait(35 * 4);
		if (S()) { Check("theDomesAmbushCame", Left(3) == 0, String.Format("%d still to come", Left(3))); Next(); }
		if (S()) Go(mo, 1700, 1736);
		if (S()) Go(mo, 1440, 1732);
		if (S()) Go(mo, 1440, 1352);
		if (S()) Go(mo, 1640, 1352);
		if (S()) { Check("outOfTheDomeNowByTheStairCarryingBlue", InLibrary(mo, false) && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, 1856, 1100);
		if (S()) Go(mo, 1856, 1030);
		if (S()) Through(mo, 270);
		ToFront(mo, BY);
		if (S()) Go(mo, -320, BY - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("backToTheLaneNow", !InThen(mo) && mo.pos.y > 144 && mo.pos.y < 448 && h.carried == blue, Where(mo)); Next(); }
		// THEN through the clocked door: the museum THEN with key 1, key 4's mancubus; down the hole, up the cellar's
		// stair with BLUE, out
		ToFront(mo, 0);
		if (S()) Go(mo, 64, -24);
		if (S()) Through(mo, 90);
		if (S()) { Check("blueAndKey3ToThen", InThen(mo) && h.carried == blue && h.Has(mo, 3), Where(mo)); Next(); }
		if (S()) Go(mo, -400, OFF - 368);
		if (S()) Go(mo, -470, OFF - 368);
		if (S()) Use(mo, 180);
		if (S()) Wait(30);
		if (S()) { Check("museumOpensThenWithKey1", DoorOpen(MUSEUM_X, OFF - 368), Shut(MUSEUM_X, OFF - 368)); Next(); }
		if (S()) Go(mo, -570, OFF - 368);
		if (S()) KillBearer(mo, 4, 350);
		if (S()) Wait(5);
		if (S()) { Check("key4FromTheMancubus", h.Has(mo, 4) && Said("It carried key 4."), h.said); Next(); }
		if (S()) Go(mo, -700, OFF - 300);
		if (S()) Go(mo, -1120, OFF - 300);
		if (S()) Go(mo, -1120, OFF - 400);
		if (S()) Go(mo, -1220, OFF - 400);
		if (S()) Wait(10);
		if (S()) { Check("downTheHoleIntoTheCellarThen", InThen(mo) && abs(mo.pos.z + 128) < 1 && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, -1300, OFF - 480);
		if (S()) Go(mo, -1528, OFF - 480);
		if (S()) Go(mo, -1528, OFF - 140);
		if (S()) Go(mo, -1528, OFF + 176);
		if (S()) Go(mo, -1440, OFF + 176);
		if (S()) { Check("upTheCellarsStairCarryingBlue", InThen(mo) && abs(mo.pos.z) < 1 && mo.pos.x > -1480 && mo.pos.x < -720 && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, -1440, OFF - 40);
		if (S()) Go(mo, -868, OFF - 40);
		if (S()) Go(mo, -868, OFF - 200);
		if (S()) Go(mo, -570, OFF - 368);
		if (S()) Use(mo, 0);
		if (S()) Wait(30);
		if (S()) { Check("museumOpensFromInsideWithKey1", DoorOpen(MUSEUM_X, OFF - 368), Shut(MUSEUM_X, OFF - 368)); Next(); }
		if (S()) Go(mo, -470, OFF - 368);
		if (S()) { Check("outOfTheMuseumThen", InThen(mo) && mo.pos.x > -512 && h.carried == blue, Where(mo)); Next(); }
		// the brass door: keys 3 and 4; the last fight; the stair; the gate; BLUE in HOME
		if (S()) Go(mo, -420, OFF - 250);
		if (S()) Go(mo, 100, OFF - 200);
		if (S()) Go(mo, 320, OFF - 180);
		if (S()) Use(mo, 270);
		if (S()) Wait(40);
		if (S())
		{
			Check("brassDoorOpensWithKeys3And4", DoorOpen(320, OFF - 216), Shut(320, OFF - 216));
			Check("lastFightCameWithKeys3And4", Left(65) == 0, String.Format("%d still to come", Left(65)));
			Next();
		}
		if (S()) Go(mo, 320, OFF - 296);
		if (S()) Go(mo, 400, OFF - 330);
		if (S()) { Check("upTheStair", abs(mo.pos.z - 64) < 1 && InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 460, OFF - 432);
		if (S()) Go(mo, 590, OFF - 432);
		if (S()) { Check("throughTheGate", InThen(mo) && InNightRoom(mo) && mo.pos.x > GATE_X + 8, Where(mo)); Next(); }
		if (S()) Use(mo, 0);
		if (S()) { Check("blueIn190", F(190).door == blue && blue.args[0] == 222 && h.wayOutBuilt, String.Format("BLUE leads to %d; ", blue.args[0]) .. h.said); Next(); }
		if (S()) Done();
		if (S()) Push(mo, 0, 60);
	}
	// key 3 still lying on the dome's floor now
	bool Key3Lying()
	{
		let it = ThinkerIterator.Create("AjarKey3");
		Inventory k;
		while (k = Inventory(it.Next())) if (!k.owner) return true;
		return false;
	}
	// the turn's company of the observatory then still to come (ambushers of cause 64 in its box)
	int ObsThenLeft()
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next()))
			if (a.args[0] == 64 && a.pos.x > 1600 && a.pos.x < 2112 && a.pos.y > OFF + 1000 && a.pos.y < OFF + 1784) n++;
		return n;
	}

	override void WorldUnloaded(WorldEvent e)
	{
		if (!Testing() || CVar.GetCVar("ajar_autotest").GetInt() != 1) return;
		Console.Printf("AJARTEST outByTheWayOut=%d  (step %d, %s)", h && h.wayOutBuilt, step, e.NextMap);
	}

	// === MODE=2: the turn by itself (posed) ========================================================
	int wavesAt;
	void TheTurn(Actor mo)
	{
		if (S()) Wait(2);
		if (S())
		{
			Check("noAmbushersYet", Left(64) > 0 && Left(65) > 0, String.Format("%d of the turn, %d of the keys", Left(64), Left(65)));
			Check("squareCompanyStands", Standing() > 0, String.Format("%d", Standing()));
			Next();
		}
		if (S()) Put(mo, 200, OFF + 960, 0);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClocked", h.carried == clocked, h.said); Next(); }
		if (S()) Put(mo, 64, OFF - 120, 90);
		if (S()) Go(mo, 64, OFF - 28);
		if (S()) Use(mo, 90);
		if (S()) Wait(3);
		if (S())
		{
			Check("clockedIn124", F(124).door == clocked && F(104).door == shadow, h.said);
			Check("theTurn", DR().turned && Said("forty years on"), h.said);
			Check("fightMusicThen", th.ThenMusic() == "AJM_EMY5");
			Check("squareCompanyWoken", DR().woken > 0 && DR().woken == Hunting(mo), String.Format("woken %d, hunting %d", DR().woken, Hunting(mo)));
			wavesAt = tic;
			Next();
		}
		if (S()) Wait(35 * 8);
		if (S()) { Check("theStopsFirstWave", Wave(3) == 0, String.Format("%d of it to come", Wave(3))); Check("theSecondWaveWaits", Wave(30) > 0, String.Format("%d", Wave(30))); Next(); }
		if (S()) Wait(35 * 26);
		if (S()) { Check("theStopsSecondWave", Wave(30) == 0, String.Format("%d of it to come", Wave(30))); Check("theDistrictsWait", Left(64, 1) > 0, String.Format("%d near", Left(64, 1))); Next(); }
		// taken down and hung again elsewhere: no second turn. The square's company, woken and hunting, has come
		// through door 4 by now and may stand in the walk to it (the walk failed in two runs of three): it is
		// removed first, its part of the test done
		if (S()) { Info(String.Format("%d of the square's company removed", RemoveSquareCompany())); Next(); }
		if (S()) Put(mo, 64, OFF - 120, 90);
		if (S()) Go(mo, 64, OFF - 28);
		if (S()) Use(mo, 90);
		if (S()) { Check("clockedTakenDown", h.carried == clocked && !F(124).door && !F(104).door, h.said); Next(); }
		if (S()) { h.said = ""; Next(); }
		if (S()) Put(mo, 192, OFF + 300, 270);
		if (S()) Go(mo, 192, OFF + 200);
		if (S()) Use(mo, 270);
		if (S()) Wait(5);
		if (S()) { Check("noSecondTurn", F(122).door == clocked && !Said("forty years on") && DR().turnedAt < level.maptime - 100, h.said); Next(); }
		if (S()) Done();
	}
	int Standing()
	{
		int n = 0;
		let it = level.CreateActorIterator(AjarDayReturn.SQUARE_TID);
		Actor a;
		while (a = it.Next()) if (a.bIsMonster && a.health > 0) n++;
		return n;
	}
	int RemoveSquareCompany()
	{
		Array<Actor> all;
		let it = level.CreateActorIterator(AjarDayReturn.SQUARE_TID);
		Actor a;
		while (a = it.Next()) if (a.bIsMonster) all.Push(a);
		for (int i = 0; i < all.Size(); i++) { all[i].ClearCounters(); all[i].Destroy(); }
		return all.Size();
	}
	int Hunting(Actor mo)
	{
		int n = 0;
		let it = level.CreateActorIterator(AjarDayReturn.SQUARE_TID);
		Actor a;
		while (a = it.Next()) if (a.bIsMonster && a.health > 0 && a.target == mo) n++;
		return n;
	}
	// the stop's waves still to come (ambushers of the turn with no `near`, holding back `after` seconds)
	int Wave(int after)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == 64 && !a.args[3] && a.args[2] == after) n++;
		return n;
	}

	// === MODE=3: views, 140 tics each (a screenshot every 70 tics: tools/smoke_MAP22_3.cfg; two a view) ============
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void V(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		if (S()) { View(mo, what, x, y, ang, pitch); Next(); }
		if (S()) Wait(139);
	}
	void Views(Actor mo)
	{
		if (S()) { mo.bInvisible = true; Wait(15); }
		V(mo, "THEN from the start: the square by day, the new bus, the day sky", -64, OFF - 592, 90, -6);
		V(mo, "NOW from the start: MAP10's square at night, the old bus", -64, -592, 90, -6);
		V(mo, "THEN the bus nearer: plates 1 to 6, RED in door 2", -64, OFF - 300, 90);
		V(mo, "NOW the bus nearer: stone in 1 and 5, frame 101, the plate of 4 lost", -64, -300, 90);
		V(mo, "THEN along the bus from its west end", -360, OFF - 160, 20);
		V(mo, "THEN door 6 (frame 123, brass) from the shelter", 320, OFF - 180, 90);
		V(mo, "NOW door 6: brass, stone in it", 320, -180, 90);
		V(mo, "THEN the shelter: the brass door, LINE 6, the timetable", 320, OFF - 40, 270, 4);
		V(mo, "NOW the shelter: stone in the brass frame; no hole over it now", 320, -40, 270, -10);
		V(mo, "THEN the bus's back: doors 7 and 8, the lane, the depot's gate", 620, OFF + 420, 200);
		V(mo, "NOW the bus's back", 620, 420, 200);
		V(mo, "THEN the bus's front", -620, OFF + 72, 0);
		V(mo, "THEN the depot from YELLOW's far side: the new buses", 0, OFF + 620, 90, -4);
		V(mo, "THEN the fitters' corner: the clocked door under the fitters' tag", 40, OFF + 900, 15, -6);
		V(mo, "THEN the fitters' tag close: FOUND IN THE YARD. NOT OURS.", 100, OFF + 930, 20, -4);
		V(mo, "NOW the depot: the old buses, the cache in the far corner", 300, 700, 135, -4);
		V(mo, "NOW the cache", -448, 940, 90);
		V(mo, "THEN the night room's east part from HOME: the gate's bolt side, the bars", 600, OFF - 432, 180);
		V(mo, "THEN the east part: HOME, frame 125, the gate's bolt side", 540, OFF - 340, 293);
		V(mo, "THEN the gate from the west part: the bolted door, frame 125 through the south bars", 340, OFF - 432, 0);
		V(mo, "THEN at the north bars, from the west part: HOME", 476, OFF - 330, 325);
		V(mo, "THEN at the south bars, from the west part: frame 125", 470, OFF - 470, 312);
		V(mo, "THEN the stair from the night room", 400, OFF - 360, 90, 8);
		V(mo, "NOW the night room from BLUE's far side: the wall's two stubs, stone where HOME is", 340, -432, 0);
		V(mo, "NOW the east end: frame 105 by the south stub, stone where HOME is", 540, -340, 293);
		V(mo, "NOW the night room from the east: the stubs, BLUE's far side", 610, -432, 180);
		V(mo, "NOW the passage north of the night room: Doom's stone where the hole was", 416, -330, 90);
		V(mo, "THEN the hotel's lobby, by day", -6144, OFF + 40, 90);
		V(mo, "THEN the hotel's corridor", -6440, OFF + 224, 180);
		V(mo, "THEN the station's concourse", 3350, OFF + 500, 90);
		V(mo, "THEN the far platform: YELLOW", 3520, OFF + 1250, 0);
		V(mo, "THEN the near platform, the tracks, the sky", 3520, OFF + 290, 20, -10);
		V(mo, "THEN the theatre's foyer from RED's far side", -224, OFF + TY + 1080, 60);
		V(mo, "NOW the theatre's foyer from RED's far side", -224, TY + 1080, 60);
		V(mo, "THEN the house", 40, OFF + TY + 780, 315);
		V(mo, "NOW the house", 40, TY + 780, 315);
		V(mo, "THEN the stage door: the ledge, the pit, door 8's doorway", 256, OFF + TY + 940, 0, 10);
		V(mo, "NOW the rooms behind the foyer: BLUE", 300, TY + 1400, 20);
		V(mo, "NOW the kiosk behind its bars", -288, -560, 270);
		V(mo, "NOW the lane from its corner", 620, 420, 215);
		// MAP22 bigger: the other stop, the observatory, the museum, door 4, the timetable
		V(mo, "THEN door 4 of the bus: an ordinary frame, its blank plate", 64, OFF - 200, 90);
		V(mo, "NOW door 4 of the bus: frame 104, the plate lost", 64, -200, 90);
		V(mo, "THEN the timetable in the shelter: line 4 a dash", 480, OFF - 140, 270);
		V(mo, "THEN the shelter's brass door: locks 3 and 4", 320, OFF - 120, 270);
		V(mo, "THEN the other stop: the new 20 (livery F), doors 1 to 3", 0, OFF + 2930, 90, -4);
		V(mo, "NOW the other stop: the old 20, frame 106 in door 3", 0, 2930, 90, -4);
		V(mo, "THEN the 20's back: door 4, the observatory", 64, OFF + 3560, 270, -4);
		V(mo, "NOW the 20's back", 64, 3560, 270, -4);
		V(mo, "THEN the 20's front from the west", -620, OFF + 3240, 0);
		V(mo, "THEN the library from door 4 of the 20", 1856, OFF + 1040, 90);
		V(mo, "NOW the library", 1856, 1040, 90);
		V(mo, "THEN the dome's door from the library: the plate 2", 1856, OFF + 1250, 90);
		V(mo, "NOW the dome from the ledge: the pier, the telescope", 1856, 1440, 90, 12);
		V(mo, "THEN the dome from the ledge", 1856, OFF + 1440, 90, 12);
		V(mo, "NOW the dome's floor: key 3, the stair out", 1900, 1700, 0, 4);
		V(mo, "NOW the stair out of the dome, from its foot", 1700, 1732, 180, -8);
		V(mo, "NOW the top of the dome's stair: a plain opening", 1440, 1560, 90);
		V(mo, "THEN the museum's door on the square: the plate 1", -380, OFF - 368, 180);
		V(mo, "NOW the museum's door on the square", -380, -368, 180);
		V(mo, "THEN the great hall from its door", -580, OFF - 368, 180, -8);
		V(mo, "NOW the great hall from its door", -580, -368, 180, -8);
		V(mo, "THEN the hall's way down to the cellar", -1000, OFF - 400, 180);
		V(mo, "THEN the gallery", -760, OFF + 150, 180);
		V(mo, "NOW the gallery: PINK's store behind its bars", -1068, 300, 90);
		V(mo, "THEN the gallery's north wall: shut", -1068, OFF + 300, 90);
		V(mo, "THEN the cellar from the bay", -1220, OFF - 400, 180);
		V(mo, "NOW the cellar's stair", -1528, -300, 90, -10);
		V(mo, "NOW the top of the cellar's stair: a plain opening to the gallery", -1528, 120, 90);
		V(mo, "THEN the gallery from the cellar's stair", -1528, OFF + 176, 0);
		if (S()) { Info("views done"); Next(); }
	}
}
