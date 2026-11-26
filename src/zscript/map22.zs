// MAP22 "Day Return" (tools/map_dayreturn.py; PLAN.md, "MAP22 "Day Return""): the level's own script, and its
// checks (DayReturnTest, below). THEN is NOW + (0, 12288). Frames NOW / THEN: 101/121 door 2 of the bus (RED
// hangs in 121 at the start), 102/122 door 7, 104/124 door 4 (the clocked door's alone at both times), 123 door 6
// THEN (brass, any colour door, no twin), 190 HOME in the night room THEN (BLUE's alone). Far sides NOW / THEN:
// RED 201/221 the theatre's foyer, BLUE 202/222 the night room, GREEN 203/223 door 3 (there is no GREEN),
// YELLOW 204/224 the depot. Fixed doorways: 1 the hotel and 2 the station (THEN), 3 and 4 door 8 from the pit
// under the stage door (NOW, THEN).

// The turn: the first time the clocked door hangs in a twinned frame (AjarThenHandler.joinedAt, then.zs). Once:
// the line on the screen; the music THEN from the quiet piece to the fight's; the square's company NOW (tid
// SQUARE_TID) woken and set on the player. What it brings THEN comes by ambush (cause 64, ajar.zs), each when the
// player is next there; two of those carry keys (AjarKeyBearer). Taking the clocked door down undoes nothing.
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
//   2 the turn by itself (posed): the clocked door hung in 124, the line, the music, the square's company woken, the
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
			Check("noKeys", !h.Has(mo, 1) && !h.Has(mo, 2));
			Check("peaceMusicThen", th.musicThen == 1 && th.ThenMusic() == "AJM_EMY4", th.ThenMusic());
			Check("notTurned", !DR().turned && th.joinedAt < 0);
			Next();
		}
		// the shelter's brass door THEN: locked, no keys
		if (S()) Go(mo, -64, OFF - 30);
		if (S()) Go(mo, 320, OFF - 30);
		if (S()) Go(mo, 320, OFF - 180);
		if (S()) Use(mo, 270);
		if (S()) Wait(30);
		if (S()) { Check("brassDoorLocked", CZ(320, OFF - 216) <= FZ(320, OFF - 216) + 1, String.Format("ceiling %.0f", CZ(320, OFF - 216))); Next(); }
		// line 5: the station; YELLOW from its far platform
		if (S()) Go(mo, 320, OFF - 30);
		if (S()) Go(mo, 192, OFF - 30);
		if (S()) Through(mo, 90);
		if (S()) { Check("line5ToStation", InThen(mo) && mo.pos.x > SX && mo.pos.x < SX + 2100, Where(mo)); Next(); }
		if (S()) Put(mo, SX + 1640, OFF + 1250, 0);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookYellow", h.carried == yellow, h.said); Next(); }
		if (S()) Put(mo, SX + 384, OFF + 70, 270);
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromStation", InThen(mo) && abs(mo.pos.x - 192) < 40 && mo.pos.y < OFF && mo.pos.y > OFF - 64, Where(mo)); Next(); }
		// YELLOW in door 7 THEN (122): the depot THEN, the clocked door
		ToBack(mo, OFF);
		if (S()) Go(mo, 192, OFF + 200);
		if (S()) Use(mo, 270);
		if (S()) { Check("yellowIn122", F(122).door == yellow && yellow.args[0] == 224 && !F(102).door, h.said); Next(); }
		if (S()) Through(mo, 270);
		if (S()) { Check("yellowToDepotThen", InThen(mo) && mo.pos.y > OFF + 544 && mo.pos.y < OFF + 700 && abs(mo.pos.z - 48) < 1, Where(mo)); Next(); }
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
		// swap YELLOW for the clocked door in 122: the turn
		if (S()) Go(mo, 192, OFF + 200);
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S())
		{
			Check("clockedIn122", F(122).door == clocked && F(102).door == shadow && h.carried == yellow, h.said);
			Check("theTurn", DR().turned && Said("forty years on"), h.said);
			Check("fightMusicThen", th.ThenMusic() == "AJM_EMY5" && th.musicThen == 1, th.ThenMusic());
			Next();
		}
		if (S()) Through(mo, 270);
		if (S()) { Check("throughClockedToNow", !InThen(mo) && mo.pos.y > 144 && mo.pos.y < 448, Where(mo)); Next(); }
		if (S()) Wait(3);
		if (S()) { Check("nowMusicNow", th.musicThen == 0); Next(); }
		if (S()) Go(mo, 192, 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("backThen", InThen(mo) && mo.pos.y > OFF + 144, Where(mo)); Next(); }
		// key 2: RED, where it hangs, to the theatre THEN; its bearer by the stage
		ToFront(mo, OFF);
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
		// RED down, YELLOW up in 121; RED through the clocked door and onto the old bus: the theatre NOW
		if (S()) Go(mo, -192, OFF - 24);
		if (S()) Use(mo, 90);
		if (S()) { Check("yellowFor121", F(121).door == yellow && h.carried == red && red.args[0] == 201, h.said); Next(); }
		if (S()) Go(mo, 470, OFF - 24);
		ToBack(mo, OFF);
		if (S()) Go(mo, 192, OFF + 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("redCarriedToNow", !InThen(mo) && h.carried == red, Where(mo)); Next(); }
		ToFront(mo, 0);
		if (S()) Go(mo, -192, -24);
		if (S()) Use(mo, 90);
		if (S()) { Check("redIn101", F(101).door == red && red.args[0] == 201 && F(121).door == yellow, String.Format("RED leads to %d; ", red.args[0]) .. h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("redToTheatreNow", !InThen(mo) && mo.pos.y > TY + 1000 && mo.pos.y < TY + 1700, Where(mo)); Next(); }
		if (S()) Put(mo, 540, TY + 1450, 0);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookBlue", h.carried == blue, h.said); Next(); }
		if (S()) Put(mo, -224, TY + 1024 + 48, 270);
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromTheatreNow", !InThen(mo) && mo.pos.y < 0 && h.carried == blue, Where(mo)); Next(); }
		// BLUE through the clocked door, THEN; line 1: the hotel, key 1's baron
		if (S()) Go(mo, 470, -24);
		ToBack(mo, 0);
		if (S()) Go(mo, 192, 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("blueCarriedToThen", InThen(mo) && h.carried == blue, Where(mo)); Next(); }
		ToFront(mo, OFF);
		if (S()) Go(mo, -320, OFF - 24);
		if (S()) Through(mo, 90);
		if (S()) { Check("line1ToHotel", InThen(mo) && mo.pos.x < HX + 600 && mo.pos.x > HX - 2000, Where(mo)); Next(); }
		if (S()) KillBearer(mo, 1, 350);
		if (S()) Wait(5);
		if (S()) { Check("key1FromItsBearer", h.Has(mo, 1) && Said("It carried key 1."), h.said); Next(); }
		if (S()) Put(mo, HX + 256, OFF + 60, 270);
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromHotel", InThen(mo) && abs(mo.pos.x + 320) < 40 && mo.pos.y < OFF, Where(mo)); Next(); }
		// the shelter's brass door: keys 1 and 2; the stair; BLUE in HOME
		if (S()) Go(mo, 320, OFF - 30);
		if (S()) Go(mo, 320, OFF - 180);
		if (S()) Use(mo, 270);
		if (S()) Wait(40);
		if (S()) { Check("brassDoorOpens", CZ(320, OFF - 216) > FZ(320, OFF - 216) + 60, String.Format("ceiling %.0f", CZ(320, OFF - 216))); Next(); }
		if (S()) Go(mo, 320, OFF - 296);
		if (S()) Go(mo, 400, OFF - 330);
		if (S()) { Check("upTheStair", abs(mo.pos.z - 64) < 1 && InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 590, OFF - 432);
		if (S()) Use(mo, 0);
		if (S()) { Check("blueIn190", F(190).door == blue && blue.args[0] == 222 && h.wayOutBuilt, String.Format("BLUE leads to %d; ", blue.args[0]) .. h.said); Next(); }
		if (S()) Done();
		if (S()) Push(mo, 0, 60);
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
		if (S()) Put(mo, 64, OFF - 28, 90);
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
		// taken down and hung again elsewhere: no second turn
		if (S()) Put(mo, 64, OFF - 28, 90);
		if (S()) Use(mo, 90);
		if (S()) { Check("clockedTakenDown", h.carried == clocked && !F(124).door && !F(104).door, h.said); Next(); }
		if (S()) { h.said = ""; Next(); }
		if (S()) Put(mo, 192, OFF + 200, 270);
		if (S()) Use(mo, 270);
		if (S()) Wait(5);
		if (S()) { Check("noSecondTurn", F(122).door == clocked && !Said("forty years on") && DR().turnedAt < tic - 100, h.said); Next(); }
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
		V(mo, "NOW the shelter: stone in the brass frame, the hole over it", 320, -40, 270, -10);
		V(mo, "THEN the bus's back: doors 7 and 8, the lane, the depot's gate", 620, OFF + 420, 200);
		V(mo, "NOW the bus's back", 620, 420, 200);
		V(mo, "THEN the bus's front", -620, OFF + 72, 0);
		V(mo, "THEN the depot from YELLOW's far side: the new buses", 0, OFF + 620, 90, -4);
		V(mo, "THEN the fitters' corner: the clocked door under its plate", 40, OFF + 900, 15, -6);
		V(mo, "NOW the depot: the old buses, the cache in the far corner", 300, 700, 135, -4);
		V(mo, "NOW the cache", -448, 940, 90);
		V(mo, "THEN the night room: BLUE's far side, HOME", 600, OFF - 432, 180);
		V(mo, "THEN the stair from the night room", 400, OFF - 360, 90, 8);
		V(mo, "NOW the night room: BLUE's far side, stone where HOME is", 340, -432, 0);
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
		if (S()) { Info("views done"); Next(); }
	}
}
