// The third goes lab (PLAN.md, "The third goes lab"; the test map SHUT,
// tools/map_shut.py; MAP=SHUT MODE=3 and 4 tools/smoke.sh). Five pieces:
//
// THE SHUTTER. AjarShutter thing: args[0] the sector tag of the shutter
// (every sector with that tag: a wall opening, ajartime.shutter), args[1]
// how high it opens over its floor (0: 96). It points (its angle) to the
// side it is worked from. A plate on the floor names it: an AjarPlate with
// args[1] the shutter's tag (args[0] 0, or a frame too). The shutter is
// OPEN only while such a plate is pressed (the player or an earlier self on
// it, as for a sprung frame); otherwise shut: its ceiling at its floor,
// and nothing passes, no walker, shot or sight. It opens and shuts in TICS
// tics, heard (the fast door's sounds), moved by this script tic by tic
// (Sector.MoveCeiling, no mover left behind). Shutting, it puts the player
// clear of it on the side it is worked from, and anything else in its way
// (an earlier self, a monster) it waits for: it never crushes. Every go of
// a fight or a room of goes begins with every shutter shut and every
// shutter's plate up (ShuttersShut).
//
// AN EARLIER SELF'S SHOTS, in a fight of goes (zone args[4] 3) while it is
// a fight: what an AjarGhost fires hurts a monster on the demo and wakes it
// as the player's own shot does (AjarRail, time.zs), and its kills are the
// player's kills (a monster on the demo it wakes dead is killed by the
// player, as Wake does; any other death counts to the player as the engine
// counts every monster death in single play). MAP31's open fights (args[4]
// 1) are as they were.
//
// KILLED IN A ROOM OF GOES (and in a fight of goes after its win): the
// player cannot die there (bBuddha). At the last moment they are in box 1
// with RESCUE_HEALTH, at the start of a new go, as through a time door; the
// go that ended is kept and played as any other (its earlier self is gone
// where it fell). A red flash, their shape gone to light where they fell,
// and a short message (GoesKilled).
//
// SEVERAL ROOMS IN ONE LEVEL: each room of goes or fight has its own fight
// number, box 1 and plate that forgets. Leaving one for good (by a way that
// is not a time door) ends it (EndGoes, or the win); walking into the next
// begins it (Begin), which takes stock of the doors afresh (DoorBegin) and
// begins its own logs, takes and ghosts.
//
// FIGURES. AjarFigure thing, for a still model of a puzzle solved behind
// glass: args[0] what (1 the player standing, 2 a body: args[1] a Doom
// editor number, its last death picture; 3 a plate, pressed; 4 a door of
// colour args[1] as it stands hung; 5 that door leaning), args[2] its size
// in percent (0: 100). No behaviour: not solid, not shootable, never
// counted, no weight on a plate, and not recorded, replayed or snapped by
// the go machinery (Counts, RecordFx, Snap leave it out).

class AjarShutter : Actor
{
	const TICS = 12;            // tics to open, and to shut
	const TALL = 96;
	bool known, want;
	Array<int> secs;
	Array<double> bottom;
	double x1, y1, x2, y2;      // round the opening

	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	void Know()
	{
		if (known) return;
		known = true;
		x1 = y1 = 1e9; x2 = y2 = -1e9;
		let it = level.CreateSectorTagIterator(args[0]);
		int i;
		while ((i = it.Next()) >= 0)
		{
			Sector s = level.sectors[i];
			secs.Push(i); bottom.Push(s.CenterFloor());
			for (int j = 0; j < s.lines.Size(); j++)
			{
				for (int v = 0; v < 2; v++)
				{
					Vector2 p = v ? s.lines[j].v2.p : s.lines[j].v1.p;
					x1 = min(x1, p.x); y1 = min(y1, p.y); x2 = max(x2, p.x); y2 = max(y2, p.y);
				}
			}
		}
	}

	double High() { return args[1] ? args[1] : TALL; }
	// how far open: 0 shut, 1 open
	double Opened()
	{
		Know();
		if (!secs.Size()) return 0;
		return (level.sectors[secs[0]].CenterCeiling() - bottom[0]) / High();
	}
	bool IsShut() { return Opened() < 0.001; }
	bool IsOpen() { return Opened() > 0.999; }

	bool Pressed()
	{
		let it = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(it.Next())) if (p.args[1] == args[0] && p.pressed) return true;
		return false;
	}

	// The player is not left in it: a step clear on the side it is worked from.
	void Clear()
	{
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		double r = mo.radius;
		if (mo.pos.x + r <= x1 || mo.pos.x - r >= x2 || mo.pos.y + r <= y1 || mo.pos.y - r >= y2) return;
		Vector2 d = AngleToVector(angle), p = mo.pos.xy;
		if (abs(d.x) > abs(d.y)) p.x = d.x > 0 ? x2 + r + 1 : x1 - r - 1;
		else p.y = d.y > 0 ? y2 + r + 1 : y1 - r - 1;
		mo.SetOrigin((p, mo.pos.z), true);
	}

	// One tic of its way, open or shut. Something in the way: it waits.
	void Move(double step)
	{
		for (int i = 0; i < secs.Size(); i++)
		{
			Sector s = level.sectors[secs[i]];
			double now = s.CenterCeiling(), to = want ? bottom[i] + High() : bottom[i];
			if (now == to) continue;
			if (!want) Clear();
			s.MoveCeiling(min(step, abs(to - now)), to, -1, to > now ? 1 : -1, false);
		}
	}

	override void Tick()
	{
		Super.Tick();
		Know();
		bool w = Pressed();
		if (w != want)
		{
			want = w;
			A_StartSound(w ? "doors/dr2_open" : "doors/dr2_clos", CHAN_BODY);
		}
		Move(High() / TICS);
	}

	// At once shut (a go begins).
	void ShutNow()
	{
		Know();
		want = false;
		Move(High());
	}
}

class AjarFigure : Actor
{
	Default { +NOINTERACTION +NOBLOCKMAP +NOGRAVITY +DONTSPLASH +NOTELEPORT }
	States
	{
	Spawn:
		PLAY A -1;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		if (args[2]) scale = (args[2], args[2]) / 100.;
		switch (args[0])
		{
		case 1:         // the player, standing, in their colours
			if (players[consoleplayer].mo) translation = players[consoleplayer].mo.translation;
			break;
		case 2:         // a body: the last picture of its death
		{
			class<Actor> cls = AjarHandler.AmbushClass(args[1]);
			if (!cls) { bInvisible = true; break; }
			let d = GetDefaultByType(cls);
			State st = d.FindState("Death"), last = null;
			for (int n = 0; st && n < 60; n++)
			{
				if (st.sprite != GetSpriteIndex("TNT1")) last = st;
				if (st.tics == -1) break;
				st = st.NextState;
			}
			if (!last) { bInvisible = true; break; }
			sprite = last.sprite;
			frame = last.Frame;
			scale.x *= d.scale.x; scale.y *= d.scale.y;
			translation = d.translation;
			break;
		}
		case 3:         // a plate, pressed
			bFlatSprite = true;
			sprite = GetSpriteIndex("AJPL");
			frame = 1;
			bBright = true;
			break;
		case 4:         // a door, hung (standing open) or leaning (tilted against what is behind it)
		case 5:
		{
			static const name spr[] = { 'AJD1', 'AJD1', 'AJD2', 'AJD3', 'AJD4', 'AJD5', 'AJD6', 'AJD7', 'AJD8', 'AJD9' };
			int c = clamp(args[1], 1, 9);
			bWallSprite = true;
			sprite = GetSpriteIndex(spr[c]);
			frame = 0;
			if (args[0] == 5) { bRollSprite = true; roll = 10; }
			A_AttachLight('glow', DynamicLight.PointLight, AjarDoor.glow[c], int(80 * scale.x), int(80 * scale.x), 0, (0, 0, 56 * scale.y));
			break;
		}
		}
	}

	override void Tick() {}     // still: nothing moves it, nothing runs
}

extend class AjarTimeHandler
{
	// --- the shutter ----------------------------------------------------------------
	// A go begins: every shutter shut, and the plates of shutters up (whoever
	// stands on one presses it again at once).
	void ShuttersShut()
	{
		let pi = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(pi.Next()))
		{
			if (!p.args[1] || !p.pressed) continue;
			p.pressed = false;
			p.SetStateLabel("Spawn");
		}
		let it = ThinkerIterator.Create("AjarShutter");
		AjarShutter s;
		while (s = AjarShutter(it.Next())) s.ShutNow();
	}

	AjarShutter FindShutter(int tag)
	{
		let it = ThinkerIterator.Create("AjarShutter");
		AjarShutter s;
		while (s = AjarShutter(it.Next())) if (s.args[0] == tag) return s;
		return null;
	}

	// --- killed in a room of goes -----------------------------------------------------
	// Into box 1 at the start of a new go, as through a time door (NextGo).
	bool GoesKilled(PlayerPawn mo)
	{
		Line l = Doors().FindLine(BoxLine(fight, 1));
		if (!l) return false;
		Actor c = Actor.Spawn("AjarSnatch", mo.pos);
		if (c) { c.angle = mo.angle; c.translation = mo.translation; c.sprite = mo.sprite; c.frame = mo.frame; c.vel.z = 1; }
		Actor.Spawn("TeleportFog", mo.pos, ALLOW_REPLACE);
		Vector2 p = (l.v1.p + l.v2.p) / 2 + (l.delta.y, -l.delta.x).Unit() * 40;
		mo.SetOrigin((p, l.frontsector.floorplane.ZAtPoint(p)), false);
		mo.angle = VectorAngle(l.delta.y, -l.delta.x);
		mo.vel = (0, 0, 0);
		mo.health = mo.player.health = RESCUE_HEALTH;
		NextGo(mo, true);
		// they stand where they were put for a second (keys still held must not walk them out)
		stand = STAND_TICS;
		mo.player.cheats |= CF_FROZEN;
		return true;
	}

	// --- the tests (map SHUT) ------------------------------------------------------------
	const SHUT_TAG = 3520;
	const SHUT_PRESS = 3510;
	int shutStep, shutT, shutOff, shutKills, shutKilled, shutShots;
	Array<Actor> shutOnDemo, penShots, penOut;

	int Figures(bool bad)       // AjarFigures (bad: those that are solid, shot, counted or alive)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarFigure");
		Actor a;
		while (a = Actor(it.Next()))
			if (!bad || a.bSolid || a.bShootable || a.bCountKill || a.bCountItem || a.bIsMonster || !a.bNoBlockmap || a.bInvisible) n++;
		return n;
	}

	int AllGhosts()
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarGhost");
		while (it.Next()) n++;
		return n;
	}

	// A rocket from the player at a point (as aimed by hand: the test's aim is exact).
	void ShootAt(PlayerPawn mo, Vector3 at)
	{
		Actor r, r2;
		[r, r2] = mo.SpawnPlayerMissile("Rocket", noautoaim: true);
		mo.TakeInventory("RocketAmmo", 1);
		if (!r) return;
		Vector3 d = at - r.pos;
		r.vel = d.Unit() * r.Speed;
		r.angle = VectorAngle(d.x, d.y);
	}
	// where the rockets go: low on the pen's back wall, across it
	Vector3 PenSpot(int n)
	{
		static const int xs[] = { 1092, 1010, 1174, 1050, 1134, 980, 1204 };
		return (xs[n % 7], 1215, 6);
	}

	// monsters of the fight that were on the demo and are hurt (or dead), and those dead
	int, int DemoHurt()
	{
		int hurt = 0, dead = 0;
		for (int i = 0; demo && i < demo.roles.Size(); i++)
		{
			AjarRole r = demo.roles[i];
			Actor a = r.actor;
			if (!a || !a.bIsMonster) continue;
			let rail = AjarRail(a.FindInventory("AjarRail"));
			if (rail) { if (rail.dmg > 0 && !r.dead) hurt++; continue; }
			if (r.mode != 2 || r.dead) continue;        // (one that was dead on the demo)
			if (a.health <= 0) { dead++; hurt++; }
			else if (a.health < a.SpawnHealth()) hurt++;
		}
		return hurt, dead;
	}

	bool InPit(Actor mo) { return mo.pos.x > 384 && mo.pos.y > 384 && mo.pos.x < 640 && mo.pos.y < 640 && mo.pos.z < -32; }

	// MODE=3: room A (the pit, the two time doors, the `only` frame), on into
	// room B (the shutter alone; go 1 on the plate and killed; go 2 shooting
	// through when the earlier self opens it).
	void ShutScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor red = Door32(1);
		AjarFrame f1 = h.FindFrame(101);
		Line l1 = h.FindLine(101);
		AjarPlate p1 = h.PlateFor(f1);
		AjarShutter sh = FindShutter(SHUT_TAG);
		AjarPlate sp = null;
		let pit = ThinkerIterator.Create("AjarPlate");
		AjarPlate pp;
		while (pp = AjarPlate(pit.Next())) if (pp.args[1] == SHUT_TAG) sp = pp;
		int g = takes.Size(), o = ot, k, b;
		[k, b] = Where(mo.pos.xy);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d goes=%d open=%d mixed=%d at=%d go=%d ot=%d selves=%d carried=%s open=%.2f plate=%d demo=%d awake=%d step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, goes, open, mixed, at, g, o, AllGhosts(), h.carried ? h.carried.Label() : "-",
			sh ? sh.Opened() : -1, sp && sp.pressed, Rails(true), Rails(false), shutStep);
		// (not a check: how many of the pen's monsters' missiles were fired, and how many came out past the shutter)
		if (fight == 2 && open)
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor m;
			while (m = Actor(mi.Next()))
			{
				if (!m.bMissile || !m.target || !m.target.bIsMonster) continue;
				if (penShots.Find(m) == penShots.Size()) penShots.Push(m);
				if (m.pos.y < 1090 && penOut.Find(m) == penOut.Size()) penOut.Push(m);
			}
			if (t % 35 == 0) Console.Printf("AJARTEST info penFired=%d penOut=%d", penShots.Size(), penOut.Size());
		}
		if (t == 3) Check("caseIsThere", Figures(false) == 4 && !Figures(true) && goes && fight == 1);

		// --- room A, go 1: into the pit, out by its time door ---
		if (shutStep == 0 && goes && g == 1)
		{
			if (o == 5) Go(mo, 500, 340, 0, 90);
			if (o > 5 && o < 16) Walk(mo, (0, 8));
			if (o == 30) Go(mo, 600, 512, -64, 0);
			if (o > 30 && o < 50) Walk(mo, (8, 0));
		}
		if (shutStep == 0 && goes && g == 2)
		{
			if (o == 2)
			{
				AjarTake t0 = takes[0];
				int n = t0.x.Size();
				bool fell = false;
				for (int i = 0; i < n; i++) if (t0.z[i] < -48 && t0.x[i] > 384 && t0.y[i] > 384) fell = true;
				Check("fromThePitToTheBox", at == 1 && b == 1 && fell && n > 30 && t0.z[n - 1] < -48);
			}
			// out by the box's door: into the room by time door 1
			if (o == 3) Go(mo, -240, 128, 0, 0);
			if (o > 3 && o <= 12) Walk(mo, (8, 0));
			if (o == 16) Check("outByDoorOne", at == 0 && b == 0 && mo.pos.x > -20 && mo.pos.x < 200 && abs(mo.pos.y - 128) < 40 && mo.pos.z == 0);
			// RED into the frame that takes it only; it is shut; on its plate
			if (o == 18) { Go(mo, 300, 520, 0, 90); red.Used(mo); }
			if (o == 20) { Go(mo, 160, 590, 0, 90); f1.Activate(mo); }
			if (o == 22) Check("onlyFrameHangsIt", red.frame == f1 && f1.args[4] == 1 && !red.nailer && !h.wayOutBuilt && red.bInvisible
				&& (l1.flags & Line.ML_BLOCKING) && !h.carried);
			if (o == 24) Go(mo, 160, 300, 0, 90);
			if (o == 28) Check("opensWithItsPlate", p1.pressed && !(l1.flags & Line.ML_BLOCKING) && !red.bInvisible);
			if (o == 220) Go(mo, 40, 128, 0, 180);
			if (o > 220 && o < 245) Walk(mo, (-8, 0));
		}
		// go 3: the second self hangs RED and holds it; through it, into room B's lobby
		if (shutStep == 0 && goes && g == 3)
		{
			if (o == 3) Go(mo, -240, 128, 0, 0);
			if (o > 3 && o <= 12) Walk(mo, (8, 0));
			if (o == 40) Check("heldByMyEarlierSelf", AllGhosts() >= 1 && red.frame == f1 && p1.pressed && !(l1.flags & Line.ML_BLOCKING));
			if (o == 42) Go(mo, 160, 600, 0, 90);
			if (o > 42 && o < 60) Walk(mo, (0, 8));
		}
		if (shutStep == 0 && !goes && t > 60)
		{
			shutStep = 1;
			shutT = t;
			Check("through", k == 2 && mo.pos.x > 780 && mo.pos.x < 860 && mo.pos.y > 570 && won.Find(1) < won.Size()
				&& (h.FindLine(HallLine(1, 1)).flags & Line.ML_BLOCKING) && (h.FindLine(HallLine(1, 2)).flags & Line.ML_BLOCKING));
		}
		if (shutStep == 1 && fight == 2 && open && phase == LIVE && ot == 2)
		{
			bool held = false;
			for (int i = 0; i < dHold.Size(); i++) if (dHold[i] >= 0) held = true;
			int touched = 0;
			for (int i = 0; i < dTouched.Size(); i++) touched += dTouched[i];
			Console.Printf("AJARTEST info fight=%d phase=%d open=%d mixed=%d goes=%d takes=%d logs=%d entries=%d ghosts=%d held=%d touched=%d left=%d",
				fight, phase, open, mixed, goes, takes.Size(), logs.Size(), logs.Size() ? logs[0].tic.Size() : -1, AllGhosts(), held, touched, Left());
			Check("secondRoomBegins", fight == 2 && phase == LIVE && open && mixed && !goes && !AllGhosts() && takes.Size() == 1
				&& logs.Size() == 1 && !logs[0].tic.Size() && !logs[0].pTic.Size() && !held && !touched && Left() == 6
				&& !(h.FindLine(HallLine(2, 1)).flags & Line.ML_BLOCKING) && (h.FindLine(HallLine(1, 1)).flags & Line.ML_BLOCKING)
				&& !red.carried && red.frame == f1 && (l1.flags & Line.ML_BLOCKING));
			shutStep = 2;
		}
		// --- room B, go 1: the shutter alone, then on its plate from 100 to 500, then "killed" ---
		if (shutStep == 2 && open && g == 1)
		{
			if (o == 3) { Go(mo, FIRE_X, FIRE_Y, 0, 90); mo.GiveInventory("RocketLauncher", 1); mo.GiveInventory("RocketAmmo", 50); }
			if (o == 5)
			{
				Check("shutWithoutThePlate", sh.IsShut() && !sp.pressed);
				FLineTraceData ld;
				mo.LineTrace(90, 1300, 0, 0, 32, data: ld);
				Console.Printf("AJARTEST info trace=%d at=(%d,%d,%d) line=%d", ld.HitType, ld.HitLocation.x, ld.HitLocation.y, ld.HitLocation.z, ld.HitLine ? ld.HitLine.Index() : -1);
				Check("noShotThrough", ld.HitType == TRACE_HitWall && ld.HitLocation.y <= 1101 && ld.HitLocation.y > 1090);
			}
			if (o == 10) Go(mo, 1364, 1040, 0, 180);
			if (o == 26) Check("opensWithThePlate", sp.pressed && sh.IsOpen());
			if (o == 30) Go(mo, 1364, 940, 0, 180);
			if (o == 46) Check("shutsAgain", !sp.pressed && sh.IsShut());
			if (o == 100) Go(mo, 1364, 1040, 0, 180);
			if (o == 500) Go(mo, 1364, 940, 0, 180);
			if (o == 505) { mo.health = mo.player.health = 1; shutStep = 3; }
		}
		if (shutStep == 3 && g == 2 && o == 2)
		{
			Check("killedIntoTheBox", open && phase == LIVE && at == 1 && b == 1 && mo.health == RESCUE_HEALTH && demo != null);
			Check("shutAtTheStart", sh.IsShut() && !sp.pressed && Rails(true) > 0);
			// the tic the earlier self steps off the plate
			AjarTake t0 = takes[0];
			for (int i = 101; i < t0.x.Size() && !shutOff; i++)
				if ((t0.x[i] - sp.pos.x, t0.y[i] - sp.pos.y).Length() > AjarPlate.REACH) shutOff = i;
			Console.Printf("AJARTEST info off=%d len=%d", shutOff, t0.x.Size());
			shutStep = 4;
		}
		// --- go 2: at the firing spot; when the earlier self opens it, fire ---
		if (shutStep == 4 && open && g == 2)
		{
			if (o == 3) Go(mo, FIRE_X, FIRE_Y, 0, 90);
			// three rockets: enough to hurt, not to win (the fight must last past the earlier self's step off)
			if (o >= 116 && o <= 160 && o % 12 == 8 && sh.IsOpen() && shutShots < 3) { ShootAt(mo, PenSpot(shutShots)); shutShots++; }
			if (o == 200)
			{
				int hurt, dead;
				[hurt, dead] = DemoHurt();
				Console.Printf("AJARTEST info hurt=%d dead=%d onDemo=%d awake=%d", hurt, dead, Rails(true), Rails(false));
				Check("hurtThroughTheShutter", hurt > 0);
			}
			if (shutOff && o == shutOff - 2) Check("openWhileMyEarlierSelfStands", sh.IsOpen() && sp.pressed && AllGhosts() >= 1);
			// standing in the opening when it shuts: put clear of it, on the range's side
			if (shutOff && o == shutOff - 4) Go(mo, 1092, 1108, 0, 90);
			if (shutOff && o == shutOff + MOVE_CHECK)
			{
				Check("shutsWhenMyEarlierSelfLeaves", sh.IsShut() && !sp.pressed);
				Check("putClearOfIt", mo.pos.y < 1100 - mo.radius && mo.pos.y > 1000 && mo.health > 0 && mo.TestMobjLocation());
				shutStep = 5;
			}
		}
	}
	const FIRE_X = 1092;
	const FIRE_Y = 80;
	const MOVE_CHECK = 15;      // AjarShutter.TICS and a little

	// MODE=4: in room B from the start. Go 1 fires at the shut shutter and is
	// "killed"; in go 2 the player holds it open and the earlier self's
	// rockets fly into the pen; the rest killed, won; after the win the
	// press puts the player in box 1.
	void ShotScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		let h = Doors();
		AjarShutter sh = FindShutter(SHUT_TAG);
		AjarPress pr = FindPress(SHUT_PRESS);
		AjarPressSwitch sw = null;
		let si = ThinkerIterator.Create("AjarPressSwitch");
		AjarPressSwitch s;
		while (s = AjarPressSwitch(si.Next())) if (s.args[0] == SHUT_PRESS) sw = s;
		int g = takes.Size(), o = ot, k, b;
		[k, b] = Where(mo.pos.xy);
		bool crush = shutStep == 3 && goes && g == 1 && o >= 45;
		if (crush) mo.player.cheats &= ~CF_GODMODE;
		else mo.player.cheats |= CF_GODMODE;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d goes=%d open=%d mixed=%d at=%d go=%d ot=%d selves=%d open=%.2f demo=%d awake=%d kills=%d/%d health=%d press=%d/%.2f step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, goes, open, mixed, at, g, o, AllGhosts(), sh ? sh.Opened() : -1,
			Rails(true), Rails(false), mo.player.killcount, level.killed_monsters, mo.health, pr ? pr.phase : -1, pr ? pr.Lowered() : -1, shutStep);
		if (t == 1) Go(mo, 820, 720, 0, 0);         // into room B's lobby: room A is left at once
		if (shutStep == 0 && open && fight == 2 && g == 1)
		{
			if (o == 3) { Go(mo, FIRE_X, FIRE_Y, 0, 90); mo.GiveInventory("RocketLauncher", 1); mo.GiveInventory("RocketAmmo", 50); }
			if (o >= 100 && o <= 400 && o % 20 == 0) ShootAt(mo, PenSpot(o / 20));
			if (o == 440)
			{
				int hurt = 0;
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next())) if (a.bIsMonster && (a.health <= 0 || a.health < a.SpawnHealth())) hurt++;
				Check("rocketsStopped", sh.IsShut() && !hurt && Left() == 6);
			}
			if (o == 445) { mo.health = mo.player.health = 1; shutStep = 1; }
		}
		if (shutStep == 1 && g == 2 && o == 2)
		{
			Check("intoTheBox", open && at == 1 && b == 1 && mo.health == RESCUE_HEALTH && demo && Rails(true) == 6 && takes[0].evTic.Size() >= 10);
			shutStep = 2;
		}
		// --- go 2: on the plate from tic 90; the earlier self's rockets fly into the pen ---
		if (shutStep == 2 && open && g == 2)
		{
			if (o == 3) Go(mo, 1364, 940, 0, 90);
			if (o == 90)
			{
				Go(mo, 1364, 1040, 0, 180);
				shutKills = mo.player.killcount; shutKilled = level.killed_monsters;
			}
			// as soon as some are dead (they may all be, soon after), or at 420
			if (!shutT && o >= 120 && (level.killed_monsters > shutKilled || o >= 420))
			{
				shutT = o;
				int hurt, dead;
				[hurt, dead] = DemoHurt();
				int mine = mo.player.killcount - shutKills, all = level.killed_monsters - shutKilled;
				Console.Printf("AJARTEST info hurt=%d dead=%d mine=%d all=%d onDemo=%d awake=%d", hurt, dead, mine, all, Rails(true), Rails(false));
				Check("myEarlierSelfHurtsThem", hurt > 0);
				Check("killsAreMine", all > 0 && mine == all && dead > 0);
			}
			if (o > 475 && o % 5 == 0) KillAll(mo);
		}
		if (shutStep == 2 && goes)
		{
			Check("won", won.Find(2) < won.Size() && goesWon && !open && !mixed && !Left() && takes.Size() == 1 && fight == 2);
			shutStep = 3;
		}
		// --- after the win: the lever, and under the press ---
		if (shutStep == 3 && goes && g == 1)
		{
			if (o == 40) Check("steelOpens", SteelUp(2));
			if (o == 45) { Go(mo, 940, 584, 0, 180); sw.Used(mo); }
			if (o == 47) Go(mo, 1092, 584, 0, 90);
		}
		if (shutStep == 3 && goes && g == 2 && o == 2)
		{
			Console.Printf("AJARTEST info health=%d at=%d b=%d under=%d press=%d", mo.health, at, b, pr.Under(mo), pr.phase);
			Check("pressPutsMeInTheBox", mo.health == RESCUE_HEALTH && at == 1 && b == 1 && k == 2 && !pr.Under(mo) && goes && takes.Size() == 2
				&& mo.player.playerstate == PST_LIVE);
			shutStep = 4;
		}
	}
}
