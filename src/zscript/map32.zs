// MAP32 "Double Shift", rebuilt (tools/map_secret2.py; PLAN.md, "MAP32
// rebuilt"): five rooms in a row, each needing earlier selves. Nothing new in
// the engine is needed for it but a plain frame that takes one door (ajar.zs,
// AjarFrame args[4] 5) and a lamp among the figures (shut.zs); room 4 since
// has key levers and idle guards (keys.zs, time.zs; PLAN.md, "MAP32 room 4:
// two keys under fire"). Its tests:
//   MAP=MAP32 MODE=3 tools/smoke.sh   the whole level solved, room by room
//   MAP=MAP32 MODE=4 tools/smoke.sh   the dead ends: out of the pit, out of
//                                     the lock; a door of room 1 refused
//   MAP=MAP32 MODE=2 tools/smoke.sh   views, for screenshots
//   MAP=MAP32 MODE=7 tools/smoke.sh   room 3's plates, screen, cage, sentries and the timetable
//   MAP=MAP32 MODE=8 tools/smoke.sh   room 4's key levers over four goes, and the timetable
//   MAP=MAP32 MODE=9 tools/smoke.sh   room 3: an earlier self's shots wake nobody
//   MAP=MAP32 MODE=10 tools/smoke.sh  winding the fights of goes, rooms 3 and 4
// The coordinates are the generator's.

extend class AjarTimeHandler
{
	const PRESS32 = 3530;       // room 3's press (map_secret2.PRESS3)
	const SHUT32 = 3540;        // room 4's shutter (map_secret2.SHUT4)
	const SHUT33 = 3535;        // room 3's wing's shutter (map_secret2.SHUT3)
	const SCREEN3 = 3536;       // room 3's screen before the guards (map_secret2.SCREEN3)
	const CAGE3 = 3537;         // room 3's cage (map_secret2.CAGE3)
	const F32 = -96;            // the floor of the pit, of room 4
	const G32 = -192;           // of room 5
	const TA32 = 200;           // when the first self hangs leaf a in room 2
	int dsStep, dsT, dsT2, dsUsed, dsBefore, dsShots, dsOut0;
	int dsOnFrom;               // walking on, ahead, until the fight that is on is another than this
	// room 3: go 1 in the chamber from dsBaitO, twelve under the press at dsTwelveO, out at dsLeaveO; go 2
	// out of the box at dsOutO, at the lever at dsLeverO, how many under the press when it was pulled
	int dsBaitO, dsTwelveO, dsLeaveO, dsOutO, dsLeverO, dsUnderAtPull, dsBackY;
	Array<Actor> dsSeen;        // room 3's monsters as first seen, and whether in the pen (a guard)
	Array<int> dsGuard;
	int dsGuards, dsGuardOut, dsHallInWing, dsLaterGuards;
	// room 4: go 1 pulls the west lever at K4P; the east one is pulled 30 later in go 2
	const K4P = 200;
	double dsOpenMax;
	bool dsLive4, dsAmber4, dsSawA4, dsSawG4;
	int dsKeyO;
	int penHitsMe, penHitsGhost;    // hits on a monster in room 4's pen by the player, by an earlier self
	int penFell;                    // pen monsters on the demo that the earlier selves' hits killed (AjarTimeHandler.Fell: the player's kill)
	AjarDoor leafA32, leafB32;
	const PAIR32 = 105;         // room 2's Pair stays joined three seconds (map_secret2.PAIR2)
	const YX32 = 3600;          // where YELLOW leans in room 2's pit, and where it is taken from (map_secret2.YELLOW_AT)
	const YY32 = -810;
	bool dsAmber2;
	// the clock lamps of room 2's frames A (131) and B (132): both showing frame f
	bool PairLamps32(int f)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarTogether");
		Actor l;
		while (l = Actor(it.Next())) if (l.args[0] == 131 || l.args[0] == 132) { if (l.frame != f) return false; n++; }
		return n == 2;
	}
	Actor dsGhost;              // MODE=2: a self in room 3's chamber, for the view of the shutter open

	void Ahead(Actor mo) { mo.vel.xy = Actor.AngleToVector(mo.angle, 8); }

	// the plate that forgets, of the box the player is in
	AjarAnew Anew32(Actor mo)
	{
		let it = ThinkerIterator.Create("AjarAnew");
		AjarAnew w, best = null;
		while (w = AjarAnew(it.Next())) if (!best || mo.Distance2D(w) < mo.Distance2D(best)) best = w;
		return best;
	}

	AjarPlate FloorPlate32(int frame, int shutter)
	{
		let it = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(it.Next())) if (p.args[0] == frame && p.args[1] == shutter) return p;
		return null;
	}

	bool InPen32(Actor a) { return a.pos.x > 7072 && a.pos.x < 7840 && a.pos.y > 1416 && a.pos.y < 1736; }
	// room 4's wings (map_secret2: WINGS4): 1 west, 2 east, 0 either
	bool InWing4(Actor a, int side)
	{
		if (a.pos.y < 720 || a.pos.y > 1380) return false;
		bool w = a.pos.x > 6896 && a.pos.x < 7184, e = a.pos.x > 7728 && a.pos.x < 8016;
		return side == 1 ? w : side == 2 ? e : w || e;
	}
	// the living monsters in the wings: how many, how many idle at their posts (real, no target, in their
	// Spawn state, deaf), how many on the demo
	int, int, int Guards4(int side)
	{
		int n = 0, idle = 0, demo = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || !InWing4(a, side)) continue;
			n++;
			if (OnDemo(a)) demo++;
			else if (!a.target && a.bAmbush && a.InStateSequence(a.CurState, a.SpawnState)) idle++;
		}
		return n, idle, demo;
	}
	// the living monsters in the pen, and how many of them are after the player
	int, int PenAfter4(Actor mo)
	{
		int n = 0, after = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && InPen32(a)) { n++; if (a.target == mo) after++; }
		return n, after;
	}
	AjarKeyLamp KeyLamp4(int n)
	{
		let it = ThinkerIterator.Create("AjarKeyLamp");
		AjarKeyLamp l;
		while (l = AjarKeyLamp(it.Next())) if (l.args[0] == SHUT32 && l.args[1] == n) return l;
		return null;
	}
	// (the tests: who hurt what in room 4's pen)
	override void WorldThingDamaged(WorldEvent e)
	{
		Actor a = e.Thing, s = e.DamageSource;
		GsDamaged(a, s, e.Damage);      // MODE=9
		LastDamaged(e);                 // last.zs: who hurt a last hall's guard
		CommonDamaged(e);               // common.zs: who hurt a common place's monster, and the selves' hits there
		if (!a || !s || !a.bIsMonster || e.Damage <= 0 || !InPen32(a)) return;
		if (s is "AjarGhost") penHitsGhost++;
		else if (s.player && (e.DamageFlags & DMG_FORCED)) penFell++;      // (Fell: not a shot of mine)
		else if (s.player) penHitsMe++;
	}

	// A rocket fired level at the n-th living monster in room 4's pen, from the west.
	void ShootPen(PlayerPawn mo, int n)
	{
		Array<Actor> pen;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || !InPen32(a)) continue;
			int i = 0;
			while (i < pen.Size() && pen[i].pos.x < a.pos.x) i++;
			pen.Insert(i, a);
		}
		if (pen.Size()) { Actor t = pen[n % pen.Size()]; mo.angle = VectorAngle(t.pos.x - mo.pos.x, t.pos.y - mo.pos.y); }
		mo.pitch = 0;
		mo.SpawnPlayerMissile("Rocket", noautoaim: true);
		mo.TakeInventory("RocketAmmo", 1);
	}

	// Two living monsters of fight k, awake and of two kinds, each hurt by the
	// other: neither turns on the other (a calm fight, time.zs). The control:
	// one with the flag taken off for a moment does.
	bool NoInfighting(int k)
	{
		Actor a = null, b = null;
		int n = 0, calm = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor m;
		while (m = Actor(it.Next()))
		{
			if (!m.bIsMonster || m.health <= 0 || OnDemo(m)) continue;
			int mk, mb;
			[mk, mb] = Where(m.pos.xy);
			if (mk != k) continue;
			n++;
			if (m.bNoInfighting) calm++;
			if (!a) a = m;
			else if (!b && m.GetClass() != a.GetClass()) b = m;
		}
		if (!a || !b) return false;
		a.DamageMobj(b, b, 1, 'None');
		b.DamageMobj(a, a, 1, 'None');
		bool apart = a.target != b && b.target != a;
		Actor was = a.target;
		int th = a.threshold;
		a.bNoInfighting = false;
		a.threshold = 0;
		a.DamageMobj(b, b, 1, 'None');
		bool would = a.target == b;
		a.bNoInfighting = true;
		a.target = was;
		a.threshold = th;
		Console.Printf("AJARTEST info infighting: %d of %d calm, %s and %s apart=%d, without the flag it would=%d",
			calm, n, a.GetClassName(), b.GetClassName(), apart, would);
		return n >= 2 && calm == n && apart && would;
	}

	// Room 3's wing (map_secret2: LANDING3 .. UPPER3, the shutter and the window in the hall's south wall)
	// and the pen in it (PEN3); the lamp beside the shutter
	bool InPen33(Actor a) { return a.pos.x > 5464 && a.pos.x < 5880 && a.pos.y > -432 && a.pos.y < -176; }
	bool InWing33(Actor a) { return a.pos.x > 5112 && a.pos.x < 5976 && a.pos.y > -432 && a.pos.y < 0; }     // (the cage too)
	AjarShutLamp Lamp33()
	{
		let it = ThinkerIterator.Create("AjarShutLamp");
		AjarShutLamp l;
		while (l = AjarShutLamp(it.Next())) if (l.args[0] == SHUT33) return l;
		return null;
	}
	int PenGuards33()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && InPen33(a)) n++;
		return n;
	}
	bool Red33() { let l = Lamp33(); return l && l.frame == 3; }
	bool Green33() { let l = Lamp33(); return l && l.frame == 2; }

	// Every tic of room 3: each monster of the fight as first seen (a guard if in the pen then); a guard
	// out of the pen, or another monster in the wing, is counted
	void Watch33()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != 3 || b != 0) continue;
			int i = dsSeen.Find(a);
			if (i == dsSeen.Size())
			{
				dsSeen.Push(a);
				dsGuard.Push(InPen33(a) ? 1 : 0);
				if (InPen33(a))
				{
					dsGuards++;
					if (a is "Revenant" || a is "Fatso" || a is "Archvile") dsLaterGuards++;
				}
				continue;
			}
			if (dsGuard[i] && !InPen33(a)) dsGuardOut++;
			if (!dsGuard[i] && InWing33(a)) dsHallInWing++;
		}
	}

	// Nothing of the room before is left: one go, no earlier selves, nothing written down.
	bool Fresh(int k)
	{
		return fight == k && takes.Size() == 1 && logs.Size() == 1 && !logs[0].tic.Size() && !logs[0].pTic.Size()
			&& !AllGhosts() && won.Find(k - 1) < won.Size()
			&& (Doors().FindLine(HallLine(k - 1, 1)).flags & Line.ML_BLOCKING);
	}

	void Leaves32()
	{
		if (leafA32) return;
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next())) if (d.IsPair()) { if (d.pos.x < 2800) leafA32 = d; else leafB32 = d; }
	}

	// MODE=3: the level solved, room by room.
	void DoubleShiftScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		Leaves32();
		AjarDoor violet = Door32(5), yellow = Door32(4), green = Door32(3), pink = Door32(6), blue = Door32(2), red = Door32(1);
		AjarDoor a = leafA32, b = leafB32;
		AjarFrame f1 = h.FindFrame(101), fa = h.FindFrame(131), fb = h.FindFrame(132), fw = h.FindFrame(133);
		AjarFrame g1 = h.FindFrame(141), g2 = h.FindFrame(142), home = h.FindFrame(190), home2 = h.FindFrame(191);
		Line l1 = h.FindLine(101), la = h.FindLine(131), lb = h.FindLine(132), lg1 = h.FindLine(141), lg2 = h.FindLine(142);
		AjarPlate p1 = FloorPlate32(101, 0), p51 = FloorPlate32(141, 0), p52 = FloorPlate32(142, 0);
		AjarKeyLever kw = FindKeyLever(SHUT32, 1), ke = FindKeyLever(SHUT32, 2);
		AjarPress pr = FindPress(PRESS32);
		AjarShutter sh = FindShutter(SHUT32), sh3 = FindShutter(SHUT33);
		AjarPressSwitch sw = null;
		let si = ThinkerIterator.Create("AjarPressSwitch");
		AjarPressSwitch s;
		while (s = AjarPressSwitch(si.Next())) if (s.args[0] == PRESS32) sw = s;
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d goes=%d open=%d mixed=%d at=%d go=%d ot=%d selves=%d carried=%s left=%d kills=%d step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, goes, open, mixed, at, g, o, AllGhosts(), h.carried ? h.carried.Label() : "-",
			phase ? Left() : -1, level.killed_monsters, dsStep);
		if (t == 3)
		{
			Check("begun1", goes && fight == 1 && g == 1 && Figures(false) == 49 && !Figures(true));
			Check("allThere", violet && yellow && green && pink && blue && red && a && b && f1 && fa && fb && fw && g1 && g2 && home && home2
				&& p1 && p51 && p52 && kw && ke && KeyLamp4(1) && KeyLamp4(2) && pr && sh && sw && sh3 && Lamp33() && red.frame == home && !h.chainLen);
		}

		// on to the next room (a room left is over at once: no go, no tic of its own)
		if (dsOnFrom && fight == dsOnFrom) Ahead(mo);
		else dsOnFrom = 0;

		// === 1: VIOLET hung and held by the plate; through, in the next go ===
		if (dsStep == 0 && goes && fight == 1 && g == 1)
		{
			if (o == 5) { Go(mo, 560, 460, 0, 270); violet.Used(mo); }
			if (o == 7) { Go(mo, 192, 480, 0, 90); f1.Activate(mo); }
			if (o == 9) Check("shutAlone1", violet.frame == f1 && (l1.flags & Line.ML_BLOCKING) && !violet.nailer && !h.wayOutBuilt);
			if (o == 10) Go(mo, 192, 160, 0, 90);
			if (o == 14) Check("opensWithThePlate1", p1.pressed && !(l1.flags & Line.ML_BLOCKING));
			if (o == 300) Go(mo, 40, 128, 0, 180);
			if (o > 300 && o < 325) Walk(mo, (-8, 0));
		}
		if (dsStep == 0 && goes && fight == 1 && g == 2)
		{
			if (o == 3) Go(mo, -240, 128, 0, 0);
			if (o > 3 && o <= 12) Walk(mo, (8, 0));
			if (o == 30) Check("heldByMyEarlierSelf1", AllGhosts() == 1 && violet.frame == f1 && p1.pressed && !(l1.flags & Line.ML_BLOCKING) && !p1.On(mo));
			if (o == 32) Go(mo, 192, 470, 0, 90);
			if (o > 32) Ahead(mo);
		}
		// === 2: two keys ===
		if (dsStep == 0 && goes && fight == 2)
		{
			Check("through1", k == 2 && mo.pos.x > 2100 && mo.pos.x < 2300 && mo.pos.y < 120 && won.Find(1) < won.Size() && (l1.flags & Line.ML_BLOCKING)
				&& (h.FindLine(HallLine(1, 1)).flags & Line.ML_BLOCKING));
			Check("noLeak2", Fresh(2));
			Check("noParadox1", !paradoxes && !paradox);      // paradox.zs: no self touched an earlier one
			dsStep = 1;
		}
		// go 1: A, then B 83 tics later: too late; out by the pit's own time door
		if (dsStep == 1 && goes && g == 1)
		{
			if (o == 5) { Go(mo, 2100, 230, 0, 90); a.Used(mo); }
			if (o == 7) { Go(mo, 2040, 160, 0, 180); fa.Activate(mo); }
			if (o == 9) Check("itTicks2", a.frame == fa && a.Shut() && h.TickingAge() >= 0);
			if (o == 60) { Go(mo, 3560, 530, F32, 90); b.Used(mo); }
			if (o == 90) { Go(mo, 3696, 600, F32, 90); fb.Activate(mo); }
			if (o == 92) Check("tooLateAlone2", a.frame == fa && b.frame == fb && a.Shut() && b.Shut() && h.Late(b)
				&& (la.flags & Line.ML_BLOCKING) && (lb.flags & Line.ML_BLOCKING));
			if (o == 95) Go(mo, 3760, -96, F32, 0);
			if (o > 95 && o < 115) Walk(mo, (8, 0));
		}
		// in the box: begin anew
		if (dsStep == 1 && goes && g == 2 && o == 3)
		{
			Check("pitDoorToTheBox2", at == 1 && bx == 1 && k == 2);
			Go(mo, 2480, 640, 0, 90);
			AjarAnew w = Anew32(mo);
			if (w) w.Used(mo);
			dsStep = 2;
			return;
		}
		// the solution, three selves: go 1 hangs a at TA32 and goes out by door 1; go 2 hangs b in time (the
		// Pair is joined for three seconds), fetches YELLOW from the far end of the pit, finds the Pair shut
		// again and goes out by the pit's time door; go 3 takes YELLOW before the second self would, waits at
		// B, walks through when the two earlier selves have joined it, and hangs YELLOW in W
		if (dsStep == 2 && goes && fight == 2 && g == 1)
		{
			if (o == 2) Check("forgotten2", !a.frame && !b.frame && !a.carried && !b.carried && !AllGhosts() && !yellow.frame);
			if (o == 5) { Go(mo, 2100, 230, 0, 90); a.Used(mo); }
			if (o == 7) Go(mo, 2040, 160, 0, 180);
			if (o == TA32) fa.Activate(mo);
			if (o == TA32 + 4) Go(mo, 2480, 280, 0, 90);
			if (o > TA32 + 4 && o < TA32 + 25) Walk(mo, (0, 8));
		}
		int join2 = TA32 + 8, shut2 = join2 + PAIR32;
		if (dsStep == 2 && goes && fight == 2 && g == 2)
		{
			if (o == 3) { Go(mo, 3560, 530, F32, 90); b.Used(mo); }
			if (o == 5) Go(mo, 3696, 600, F32, 90);
			if (o == join2) fb.Activate(mo);
			if (o == join2 + 2)
				Check("joined2", a.frame == fa && b.frame == fb && a.args[0] == 132 && b.args[0] == 131 && AllGhosts() == 1
					&& !(la.flags & Line.ML_BLOCKING) && !(lb.flags & Line.ML_BLOCKING) && a.joinEnds == level.maptime - 2 + PAIR32);
			if (o == join2 + 4) { Go(mo, YX32, YY32, F32, 270); yellow.Used(mo); }
			// back at B just before it shuts, standing in its mouth (10 from the line)
			if (o == shut2 - 6)
			{
				Vector2 dir = lb.delta.Unit(), n = (dir.y, -dir.x), mid = (lb.v1.p + lb.v2.p) / 2;
				Go(mo, mid.x + n.x * 10, mid.y + n.y * 10, F32, 90);
			}
			if (o == shut2 - 2)
				Check("stillJoined2", a.args[0] == 132 && b.args[0] == 131 && !(la.flags & Line.ML_BLOCKING) && !(lb.flags & Line.ML_BLOCKING)
					&& PairLamps32(2) && h.carried == yellow);
			if (o == shut2 + 2)
			{
				Vector2 dir = lb.delta.Unit(), n = (dir.y, -dir.x);
				double off = (mo.pos.xy - lb.v1.p) dot n;
				Console.Printf("AJARTEST info shut again: the player %.1f from B's line, at (%d,%d,%d)", off, mo.pos.x, mo.pos.y, mo.pos.z);
				Check("shutAgain2", a.frame == fa && b.frame == fb && a.Shut() && b.Shut() && h.Late(a) && h.Late(b) && !a.joinEnds && !b.joinEnds
					&& (la.flags & Line.ML_BLOCKING) && (lb.flags & Line.ML_BLOCKING) && PairLamps32(3) && h.pairSaid == 3);
				Check("putClear2", off >= AjarHandler.CLEAR - 0.5 && k == 2 && mo.pos.z < -90);
			}
			// self 2, back with YELLOW, walks into B: shut
			if (o > shut2 + 4 && o < shut2 + 24) Ahead(mo);
			if (o == shut2 + 26) Check("backTooLate2", k == 2 && mo.pos.z < -90 && mo.pos.x > 3280 && h.carried == yellow && a.Shut() && b.Shut());
			if (o == shut2 + 28) Go(mo, 3760, -96, F32, 0);
			if (o > shut2 + 28 && o < shut2 + 48) Walk(mo, (8, 0));
		}
		if (dsStep == 2 && goes && fight == 2 && g == 3)
		{
			int yi = dDoor.Find(yellow);
			if (o == 2)
			{
				// the timetable: the Pair's row, one span of the second self from its hanging, three seconds long
				let tb = Table();
				int rows = 0, row = -1;
				for (int i = 0; i < tb.rPair.Size(); i++) if (tb.rPair[i]) { rows++; row = i; }
				int n = 0;
				bool ok = tb.on && rows == 1 && tb.jFrom.Size() == 1 && abs(tb.jFrom[0] - join2) <= 1 && tb.jTo[0] - tb.jFrom[0] == PAIR32
					&& (tb.jFa[0] == 132 && tb.jFb[0] == 131);
				for (int i = 0; i < tb.sRow.Size(); i++) if (tb.sRow[i] == row) { n++; ok = ok && tb.sSelf[i] == 1 && tb.sFrom[i] == tb.jFrom[0] && tb.sTo[i] == tb.jTo[0]; }
				Console.Printf("AJARTEST info timetable: on=%d pairRows=%d spans=%d from=%d to=%d", tb.on, rows, tb.jFrom.Size(),
					tb.jFrom.Size() ? tb.jFrom[0] : -1, tb.jTo.Size() ? tb.jTo[0] : -1);
				Check("pairOnTheTimetable2", ok && n == 1 && !yellow.frame && !yellow.carried && Near(yellow, YX32, YY32 - 30, 8));
				dsAmber2 = true;
			}
			if (o == 5) { Go(mo, YX32, YY32, F32, 270); yellow.Used(mo); }
			// waits 40 behind B's mouth, where the second self stands to hang b until join2 + 4 (paradox.zs)
			if (o == 7) Go(mo, 3696, 560, F32, 90);
			// the lamps: not lit 140 tics before the earlier selves join it, amber 40 before, green when joined
			if (o == join2 - 140) dsAmber2 = dsAmber2 && PairLamps32(0) && abs(PairJoinIn(131) - 140) <= 1;
			if (o == TA32 - 40) dsAmber2 = dsAmber2 && PairLamps32(AjarTogether.AMBER);
			if (o == join2 + 2)
			{
				Check("pairLampsAmber2", dsAmber2 && PairLamps32(2) && PairJoinIn(132) == 0);
				Check("joinedByMyEarlierSelves2", a.frame == fa && b.frame == fb && a.args[0] == 132 && b.args[0] == 131 && AllGhosts() == 2
					&& !(la.flags & Line.ML_BLOCKING) && !(lb.flags & Line.ML_BLOCKING) && h.carried == yellow && a.joinTics == PAIR32);
			}
			// the second self's pick-up of YELLOW (at join2 + 4) finds it in my hands: it mimes it, and from then on
			// does nothing to YELLOW
			if (o == join2 + 6)
				Check("lostPickUp2", h.carried == yellow && yellow.carried && logs[1].broken.Find(yi) < logs[1].broken.Size()
					&& dHold[yi] == -1 && a.args[0] == 132);
			if (o > join2 + 6 && o < join2 + 26) Ahead(mo);
			if (o == join2 + 28)
				Check("yellowUp2", k == 2 && mo.pos.x < 2400 && mo.pos.z > -1 && h.carried == yellow && a.frame == fa && b.frame == fb && o < shut2);
			if (o == join2 + 30) { Go(mo, 2632, 40, 0, 270); fw.Activate(mo); }
			if (o == join2 + 32) Check("hungInW2", yellow.frame == fw && !h.carried && !yellow.nailer && !h.wayOutBuilt);
			if (o == join2 + 34) { Go(mo, 2632, 40, 0, 270); dsOnFrom = 2; }
		}
		// === 3: the press ===
		if (dsStep == 2 && fight == 3)
		{
			Check("on2", k == 3 && won.Find(2) < won.Size() && (h.FindLine(HallLine(2, 1)).flags & Line.ML_BLOCKING)
				&& (h.FindLine(HallLine(2, 2)).flags & Line.ML_BLOCKING) && yellow.frame == fw);
			Check("noParadox2", !paradoxes && !paradox);
			dsStep = 3;
			dsT = t;
		}
		if (dsStep == 3 && t == dsT + 6)
		{
			Console.Printf("AJARTEST info left=%d", Left());
			Check("begun3", phase == LIVE && open && mixed && Left() >= 17 && PressUp(pr) && sh3.IsShut() && Red33());
			Check("noLeak3", Fresh(3));
		}
		if (dsStep == 3 && open && fight == 3) Watch33();
		// go 1: the monsters do not fight each other; alone in the hall, the shutter is shut and its lamp
		// red; it opens when the player stands under the press (a message, the lamp green) and shuts when
		// they step out. Then the bait in the chamber, by door 3, until twelve are under the press (or
		// 900 tics), and out by door 3
		if (dsStep == 3 && open && g == 1)
		{
			if (o == 6) Check("noInfighting3", NoInfighting(3));
			if (o == 8) Go(mo, 5192, 40, 0, 270);
			if (o == 10)
			{
				FLineTraceData ld;
				mo.LineTrace(270, 200, 0, 0, 40, data: ld);
				Console.Printf("AJARTEST info shutter: hit=%d at y=%.1f lever=%.1f away", ld.HitType, ld.HitLocation.y, mo.Distance2D(sw));
				Check("shutAlone3", sh3.IsShut() && Red33() && ld.HitType == TRACE_HitWall && ld.HitLocation.y > -1
					&& ld.HitLocation.y < 1 && PressUp(pr) && !sh3.told);
			}
			if (o == 12) Go(mo, 5768, 784, 0, 90);
			if (o == 12 + AjarShutter.TICS + 4)
				Check("opensUnderThePress3", pr.Under(mo) && sh3.IsOpen() && Green33() && sh3.told && sh3.PlayerIn());
			if (o == 30) Go(mo, 5768, 700, 0, 270);
			if (o == 30 + AjarShutter.TICS + 4) Check("shutsWhenIStepOut3", !pr.Under(mo) && sh3.IsShut() && Red33());
			if (o == 48) { Go(mo, 6500, 1040, 0, 180); dsBaitO = o; }
			if (dsBaitO && !dsLeaveO)
			{
				if (!dsTwelveO && UnderPress(pr) >= 12)
				{
					dsTwelveO = o;
					Console.Printf("AJARTEST info twelve under the press at o=%d (%d after the bait came in)", o, o - dsBaitO);
				}
				if ((dsTwelveO && o >= dsTwelveO + 35) || o >= 900)
				{
					dsLeaveO = o;
					if (!dsTwelveO) dsTwelveO = o - 35;
					Console.Printf("AJARTEST info the bait leaves o=%d under=%d", o, UnderPress(pr));
					Go(mo, 6510, 1040, 0, 0);
					mo.health = mo.player.health = 80;      // (out with more than RESCUE_HEALTH: it is kept)
				}
				else if ((mo.pos.xy - (6500, 1040)).Length() > 8) Go(mo, 6500, 1040, 0, 180);
			}
			if (dsLeaveO && o > dsLeaveO) Walk(mo, (8, 0));
		}
		// go 2: out of the box by door 1, not into the chamber; before the shutter, open while the
		// earlier self is under the press; in, up the stairs past the guards, the lever when the monsters,
		// played as they went, are under the press; the shutter shuts with the player in the wing when the
		// earlier self is gone; out by the window, and no way back
		if (dsStep == 3 && open && g == 2)
		{
			int len = takes[0].x.Size();
			if (o == 2) Check("outByDoorThree3", at == 1 && bx == 1 && demo != null && !takes[0].died && takes[0].door == HallLine(3, 3)
				&& used == HallLine(3, 1));
			if (o == 2) Check("outWithMoreKeepsIt3", mo.health == 80);
			if (o == 3) Go(mo, 4810, 560, 64, 180);
			if (o > 3 && !dsOutO)
			{
				if (at == 1) Ahead(mo);      // (through the portal it faces the hall)
				else dsOutO = o;
			}
			if (dsOutO && o == dsOutO + 3)
			{
				Console.Printf("AJARTEST info out of the box at (%d,%d) o=%d", mo.pos.x, mo.pos.y, o);
				Check("outByDoorOne3", at == 0 && k == 3 && bx == 0 && mo.pos.x > 5000 && mo.pos.x < 5150 && mo.pos.y > 650 && mo.pos.y < 768
					&& !pr.Under(mo));
				Go(mo, 5192, 40, 0, 270);
			}
			if (dsOutO && o == max(dsOutO + 6, dsBaitO + 20))
				Check("openForMyEarlierSelf3", sh3.IsOpen() && Green33() && AllGhosts() >= 1 && sh3.GhostIn() && !sh3.PlayerIn());
			// through the shutter, onto the landing, up the stairs (along the north wall), to the lever
			if (dsOutO && o > max(dsOutO + 6, dsBaitO + 20) && !dsLeverO)
			{
				if (mo.pos.y > -56 && mo.pos.x < 5300) Walk(mo, (0, -8));
				else if (mo.pos.x < 5600) Walk(mo, (8, 0));
				else
				{
					dsLeverO = o;
					Console.Printf("AJARTEST info at the lever o=%d z=%d guards=%d in the pen", o, mo.pos.z, PenGuards33());
					Check("upTheStairs3", mo.pos.z == 96 && k == 3 && bx == 0 && InWing33(mo));
					Check("guardsInThePen3", PenGuards33() >= 1 && !dsGuardOut);
					Go(mo, 5856, -50, 96, 90);
				}
			}
			if (!dsUsed && dsLeverO && o > dsLeverO && Demoing() && (UnderPress(pr, 1) >= 10 || o >= dsTwelveO))
			{
				dsUnderAtPull = UnderPress(pr, 1);
				Console.Printf("AJARTEST info pulled o=%d under=%d onDemo=%d len=%d lever=%.1f away", o, dsUnderAtPull, Rails(true), demo.len, mo.Distance2D(sw));
				dsBefore = mo.player.killcount;
				mo.vel = (0, 0, 0);
				sw.Used(mo);
				dsUsed = o;
			}
			int down = dsUsed + AjarPress.WARN + AjarPress.DOWN;
			if (dsUsed && o == down + 5)
			{
				int n = 0;
				for (int i = 0; i < pr.victimDemo.Size(); i++) n += pr.victimDemo[i];
				Console.Printf("AJARTEST info victims=%d onDemo=%d killed=%d mine=%d", pr.victims.Size(), n, pr.kills, mo.player.killcount - dsBefore);
				// (the player's count may rise by one more in those tics: a death the demo plays, as in the PRESS lab)
				Check("pressKills3", n > 0 && pr.kills == pr.victims.Size() && mo.player.killcount - dsBefore >= pr.victims.Size() && !pr.byGhost);
				let wk = AjarWorks.Get();      // the look (works.zs): the flare, every sector as the press says
				if (wk && wk.on) Check("worksPressFlare3", wk.flare != null && wk.PressLit() > 0);     // (the flare falls each tic: Wrong waits for the end)
			}
			if (dsUsed && o == down + AjarPress.HOLD + AjarPress.RISE + 5)
			{
				let wk = AjarWorks.Get();      // the stroke over: every sector back where its state says
				if (wk && wk.on) Check("worksPressBack3", pr.phase == 0 && !wk.flare && wk.Wrong() == 0 && wk.PressLit() == 0);
			}
			// the earlier self's time is over: the shutter shuts with the player in the wing
			if (dsUsed && o == len + AjarShutter.TICS + 4)
			{
				Console.Printf("AJARTEST info the earlier self gone o=%d (len %d), at (%d,%d,%d)", o, len, mo.pos.x, mo.pos.y, mo.pos.z);
				Check("shutBehindMe3", sh3.IsShut() && Red33() && !AllGhosts() && InWing33(mo) && mo.pos.z == 96);
			}
			// out by the window: a drop into the hall; no way back up, nor through the shutter
			int w = len + AjarShutter.TICS + 6;
			if (dsUsed && o == w) Go(mo, 5768, -40, 96, 90);
			if (dsUsed && o > w && o < w + 12) Walk(mo, (0, 8));
			if (dsUsed && o == w + 26)
			{
				Check("outByTheWindow3", k == 3 && bx == 0 && mo.pos.y > 0 && mo.pos.z < 1 && !InWing33(mo));
				Go(mo, 5768, 24, 0, 270);
			}
			if (dsUsed && o > w + 26 && o < w + 38) Walk(mo, (0, -8));
			if (dsUsed && o == w + 40) { dsBackY = int(mo.pos.y); Go(mo, 5192, 40, 0, 270); }
			if (dsUsed && o > w + 40 && o < w + 52) Walk(mo, (0, -8));
			if (dsUsed && o == w + 54)
			{
				Console.Printf("AJARTEST info back: window y=%d shutter y=%d", dsBackY, mo.pos.y);
				Check("noWayBack3", dsBackY > 0 && mo.pos.y > 0 && sh3.IsShut() && !InWing33(mo));
			}
			if (dsUsed && o > w + 56 && o > down + 62 && o % 5 == 0) KillAll(mo);
		}
		if (dsStep == 3 && goes && fight == 3)
		{
			Console.Printf("AJARTEST info guards=%d (later waves' %d) out of the pen=%d hall monsters in the wing=%d twelveAt=%d underAtPull=%d",
				dsGuards, dsLaterGuards, dsGuardOut, dsHallInWing, dsTwelveO - dsBaitO, dsUnderAtPull);
			Check("guardsStayed3", dsGuards >= 4 && !dsGuardOut);
			Check("laterGuards3", dsLaterGuards >= 1);
			Check("noneInTheWing3", !dsHallInWing);
			Check("won3", won.Find(3) < won.Size() && !open && !mixed && !Left() && goesWon);
			Check("noParadox3", !paradoxes && !paradox);      // paradox.zs: no self touched an earlier one in the fight
			dsStep = 4;
			dsT = t;
		}
		if (dsStep == 4 && t == dsT + 40)
		{
			let wk = AjarWorks.Get();          // the look: room 3 done, its light up
			if (wk && wk.on) Check("worksDone3", wk.StateOf(3) == AjarWorks.DONE && wk.Wrong() == 0 && wk.PressLit() == 0);
		}
		if (dsStep == 4 && t == dsT + 40) { Check("steel3", SteelUp(3)); Go(mo, 6500, 160, 0, 0); dsOnFrom = 3; }
		// === 4: the range: two keys under fire ===
		if (dsStep == 4 && fight == 4 && open)
		{
			dsStep = 5;
			dsT = t;
			dsT2 = 0;
		}
		if (dsStep == 5 && t == dsT + 6)
		{
			Console.Printf("AJARTEST info left=%d", Left());
			Check("begun4", phase == LIVE && open && mixed && Left() >= 9 && sh.IsShut() && kw && ke && !sh.keyed);
			Check("noLeak4", Fresh(4));
		}
		// go 1: the guards of both wings idle at their posts, the pen's after the player; into the west
		// wing, its lever pulled alone at K4P (nothing opens); rockets at the shut shutter; out by door 1
		if (dsStep == 5 && open && g == 1)
		{
			if (o == 3) { Go(mo, 7456, 120, F32, 90); mo.GiveInventory("RocketLauncher", 1); mo.GiveInventory("RocketAmmo", 50); }
			if (o == 6)
			{
				int n, idle, pen, after;
				[n, idle] = Guards4(0);
				[pen, after] = PenAfter4(mo);
				Console.Printf("AJARTEST info guards=%d idle=%d pen=%d after me=%d", n, idle, pen, after);
				Check("guardsIdle4", n >= 6 && idle == n && pen > 0 && after == pen);
			}
			if (o == 10) Go(mo, 7150, 780, F32, 90);
			if (o == 12) Go(mo, 7040, 1340, F32, 90);
			if (o > 12 && o < K4P) mo.vel.xy = (0, 0);
			if (o == K4P) { kw.Used(mo); dsOpenMax = 0; }
			if (o > K4P && o <= K4P + 75) dsOpenMax = max(dsOpenMax, sh.Opened());
			if (o == K4P + 2) dsLive4 = kw.Live() && kw.frame == 1 && (keySaid & 1) && !(keySaid & 2) && !sh.keyed;
			if (o == K4P + AjarKeyLever.JOIN - 2) dsLive4 = dsLive4 && kw.Live();
			if (o == K4P + 75)
			{
				Console.Printf("AJARTEST info alone: live=%d up=%d said=%d opened=%.2f", dsLive4, kw.Up(), keySaid, dsOpenMax);
				Check("shutAlone4", dsLive4 && kw.Up() && kw.frame == 0 && ke.Up() && dsOpenMax == 0 && sh.IsShut() && (keySaid & 3) == 3 && !(keySaid & 4));
			}
			if (o == K4P + 80) Go(mo, 7456, 120, F32, 90);
			if (o >= K4P + 90 && o <= K4P + 290 && o % 20 == 0) { ShootPen(mo, dsShots); dsShots++; }
			if (o == K4P + 340)
			{
				int hurt = 0, n = 0;
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next())) if (a.bIsMonster && InPen32(a)) { n++; if (a.health < a.SpawnHealth()) hurt++; }
				Console.Printf("AJARTEST info rockets at the shut shutter: %d, pen=%d hurt=%d hits=%d/%d", dsShots, n, hurt, penHitsMe, penHitsGhost);
				Check("rocketsStopped4", sh.IsShut() && dsShots >= 8 && n >= 9 && !hurt && !penHitsMe);
			}
			if (o == K4P + 345) Go(mo, 7240, 432, F32, 180);
			if (o > K4P + 345) Walk(mo, (-8, 0));
		}
		// go 2: before the east wing its guards are on the demo; stepping in wakes them, idle; at the east
		// lever its lamp turns amber before the earlier self's pull and blinks once the west lever is live;
		// pulled within two seconds: keyed open. The earlier self's rockets fly into the pen, then mine;
		// shut again half a minute later. Then the rest are killed by the script
		if (dsStep == 5 && open && g == 2)
		{
			AjarKeyLamp lamp = KeyLamp4(2);
			if (o == 2) { Console.Printf("AJARTEST info go 2: at=%d box=%d demo=%d shut=%d", at, bx, demo != null, sh.IsShut()); penHitsMe = penHitsGhost = penFell = 0; }
			if (o == 3) Go(mo, 7680, 784, F32, 0);
			if (o == 4)
			{
				int n, idle, demo;
				[n, idle, demo] = Guards4(2);
				Console.Printf("AJARTEST info east wing before: guards=%d on the demo=%d", n, demo);
				Check("guardsOnTheDemo4", n > 0 && demo == n);
			}
			if (o == 6) Go(mo, 7720, 784, F32, 0);
			if (o == 16)
			{
				int n, idle, demo;
				[n, idle, demo] = Guards4(2);
				Console.Printf("AJARTEST info east wing after stepping in: guards=%d idle=%d on the demo=%d", n, idle, demo);
				Check("guardsWake4", n > 0 && !demo && idle == n);
			}
			if (o == 20) Go(mo, 7872, 1340, F32, 90);
			if (o > 20 && o < K4P + 30) mo.vel.xy = (0, 0);
			if (o == K4P - AjarTimeHandler.SOON - 20) dsAmber4 = lamp && lamp.frame == AjarLamp.RED;
			if (o == K4P - 40) dsAmber4 = dsAmber4 && lamp.frame == AjarLamp.AMBER;
			if (o > K4P + 1 && o < K4P + 26 && lamp) { if (lamp.frame == AjarLamp.AMBER) dsSawA4 = true; if (lamp.frame == AjarLamp.GREEN) dsSawG4 = true; }
			if (o == K4P + 28)
			{
				Console.Printf("AJARTEST info east lamp: red then amber=%d, by turns amber=%d green=%d, west live=%d", dsAmber4, dsSawA4, dsSawG4, kw.Live());
				Check("keyLampAmber4", dsAmber4 && dsSawA4 && dsSawG4 && kw.Live());
			}
			if (o == K4P + 30) { ke.Used(mo); dsKeyO = o; }
			if (o == K4P + 30 + AjarShutter.TICS + 4)
			{
				Console.Printf("AJARTEST info keyed=%d open=%.2f lamps=%d/%d said=%d", sh.keyed, sh.Opened(), KeyLamp4(1).frame, lamp.frame, keySaid);
				Check("keyedByTwo4", sh.IsOpen() && sh.keyed > 0 && kw.held && ke.held && KeyLamp4(1).frame == AjarLamp.GREEN
					&& lamp.frame == AjarLamp.GREEN && LampsShow(SHUT32, AjarLamp.GREEN) && (keySaid & 4) && AllGhosts() >= 1);
			}
			// the pen monsters the earlier self's rockets hurt (a hit the demo has not: the shutter was shut in
			// go 1) are still on the demo, and none is after me (PLAN.md, "Fights of goes: an earlier self's
			// shots wake nobody")
			if (o == K4P + 300)
			{
				int n = 0, onDemo = 0, hurt = 0, after = 0;
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next()))
				{
					if (!a.bIsMonster || a.health <= 0 || !InPen32(a)) continue;
					n++;
					let rail = AjarRail(a.FindInventory("AjarRail"));
					if (rail) { onDemo++; if (rail.ghostDmg > 0) hurt++; }
					if (a.target == mo) after++;
				}
				Console.Printf("AJARTEST info pen at o=%d: alive=%d on the demo=%d hurt by the earlier self=%d after me=%d hits=%d/%d demo=%d len=%d",
					o, n, onDemo, hurt, after, penHitsGhost, penHitsMe, Demoing(), demo ? demo.len : -1);
				Check("hurtButOnTheDemo4", Demoing() && penHitsGhost > 0 && !penHitsMe && hurt > 0 && onDemo == n && !after);
			}
			if (o == K4P + 375)
			{
				Console.Printf("AJARTEST info before I fire: hits by the earlier self=%d, mine=%d, killed on the demo by them=%d", penHitsGhost, penHitsMe, penFell);
				Check("myEarlierSelfHurtsThem4", penHitsGhost > 0 && !penHitsMe);
				// what they counted killed one on the demo, the player's kill, before it woke (Fell)
				Check("killedOnTheDemo4", penFell > 0);
				Go(mo, 7456, 120, F32, 90);
			}
			if (o >= K4P + 380 && o <= K4P + 500 && o % 20 == 0 && sh.IsOpen()) ShootPen(mo, o / 20);
			if (o == K4P + 600)
			{
				Console.Printf("AJARTEST info my hits=%d", penHitsMe);
				Check("hurtThroughTheShutter4", penHitsMe > 0);
			}
			if (dsKeyO && o == dsKeyO + 30 * 35 - 2) Check("openStill4", sh.IsOpen() && kw.held && ke.held);
			if (dsKeyO && o == dsKeyO + 30 * 35 + AjarShutter.TICS + 4)
			{
				Console.Printf("AJARTEST info half a minute: keyed=%d opened=%.2f up=%d/%d", sh.keyed, sh.Opened(), kw.Up(), ke.Up());
				Check("shutsAfterHalfAMinute4", sh.IsShut() && !sh.keyed && kw.Up() && ke.Up() && kw.frame == 0 && ke.frame == 0);
			}
			if (dsKeyO && o > dsKeyO + 30 * 35 + 20 && o % 5 == 0) KillAll(mo);
		}
		if (dsStep == 5 && goes && fight == 4)
		{
			Check("won4", won.Find(4) < won.Size() && !open && !mixed && !Left() && goesWon);
			Check("noParadox4", !paradoxes && !paradox);
			dsStep = 6;
			dsT = t;
		}
		if (dsStep == 6 && t == dsT + 40) { Check("steel4", SteelUp(4)); Go(mo, 7680, 452, F32, 0); dsOnFrom = 4; }
		// === 5: the airlock and the way out ===
		if (dsStep == 6 && fight == 5 && goes)
		{
			Check("begun5", goes && mo.pos.x > 8048 && !g1.door && !g2.door && red.frame == home && !home2.door);
			Check("noLeak5", Fresh(5));
			dsStep = 7;
		}
		// go 1: GREEN in F1, on its plate a good while, out by door 1
		if (dsStep == 7 && goes && g == 1)
		{
			if (o == 5) { Go(mo, 8480, 340, G32, 270); green.Used(mo); }
			if (o == 7) { Go(mo, 8530, 416, G32, 0); g1.Activate(mo); }
			if (o == 9) Check("onlyItsPlate5", green.frame == g1 && (lg1.flags & Line.ML_BLOCKING));
			if (o == 11) Go(mo, 8180, 580, G32, 0);
			if (o == 300) Go(mo, 8232, 200, G32, 270);
			if (o > 300 && o < 325) Walk(mo, (0, -8));
		}
		// go 2: through F1 while the first self holds it, PINK in F2, on P2, out by L's time door
		if (dsStep == 7 && goes && g == 2)
		{
			if (o == 3) Go(mo, 8296, -90, G32, 90);
			if (o > 3 && o <= 15) Walk(mo, (0, 8));
			if (o == 22) Check("outByDoorOne5", at == 0 && bx == 0 && k == 5 && mo.pos.x < 8560 && mo.pos.y > 160);
			if (o == 25) Go(mo, 8530, 416, G32, 0);
			if (o > 25 && o < 40) Ahead(mo);
			if (o == 42) Check("through5a", k == 5 && mo.pos.x > 8800 && mo.pos.x < 9248 && p51.pressed && AllGhosts() == 1);
			if (o == 44) { Go(mo, 9150, 310, G32, 270); pink.Used(mo); }
			if (o == 46) { Go(mo, 9218, 416, G32, 0); g2.Activate(mo); }
			if (o == 50) Go(mo, 8930, 580, G32, 0);
			if (o == 300) Go(mo, 9032, 200, G32, 270);
			if (o > 300 && o < 325) Walk(mo, (0, -8));
		}
		// go 3: BLUE, through both while the two earlier selves hold them, BLUE opposite RED, the chain
		if (dsStep == 7 && goes && g == 3)
		{
			if (o == 3) { Go(mo, 8300, 600, G32, 90); blue.Used(mo); }
			// through F1 once the first self has hung GREEN in it (it stands in its mouth till 11), and out of
			// the way of the second self, which comes through F1 on this path at 25 (paradox.zs)
			if (o == 12) Go(mo, 8530, 416, G32, 0);
			if (o > 12 && o < 27) Ahead(mo);
			if (o == 28) Go(mo, 9100, 520, G32, 0);
			if (o == 80)
			{
				Check("twoEarlierSelves5", AllGhosts() == 2 && p51.pressed && p52.pressed && pink.frame == g2 && green.frame == g1 && h.carried == blue);
				Go(mo, 9218, 416, G32, 0);
			}
			if (o > 80 && o < 95) Ahead(mo);
			if (o == 97) Check("through5b", k == 5 && mo.pos.x > 9600 && mo.pos.x < 10112 && mo.pos.y > 160 && mo.pos.y < 608 && h.carried == blue);
			if (o == 99) { Go(mo, 10080, 384, G32, 0); home2.Activate(mo); }
			if (o == 101) Check("chainClosed5", h.chainLen == 2 && blue.frame == home2 && red.frame == home && !h.carried);
			if (o == 103) { Go(mo, 9640, 384, G32, 180); Check("noParadox5", !paradoxes && !paradox); }
			if (o > 103) Ahead(mo);
		}
	}

	// MODE=4: the dead ends. A door of room 1 is refused in room 2; a player in the
	// pit with nothing joined leaves by the pit's time door; one shut in room 5's
	// lock by its own.
	void DeadEndScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		Leaves32();
		AjarDoor violet = Door32(5), green = Door32(3), a = leafA32, b = leafB32;
		AjarFrame fa = h.FindFrame(131), fb = h.FindFrame(132), fw = h.FindFrame(133), g1 = h.FindFrame(141);
		Line lg1 = h.FindLine(141);
		AjarPlate p51 = FloorPlate32(141, 0);
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d goes=%d at=%d go=%d ot=%d selves=%d carried=%s step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, goes, at, g, o, AllGhosts(), h.carried ? h.carried.Label() : "-", dsStep);
		// VIOLET from room 1, carried into room 2: no frame there takes it
		if (t == 1) { Go(mo, 560, 460, 0, 270); violet.Used(mo); }
		if (t == 3) Go(mo, 2300, 160, 0, 90);
		if (t == 6) { Go(mo, 2632, 40, 0, 270); fw.Activate(mo); }
		if (t == 7) { Go(mo, 2040, 160, 0, 180); fa.Activate(mo); }
		if (t == 8) { Go(mo, 3696, 600, F32, 90); fb.Activate(mo); }
		if (t == 9)
		{
			Check("onlyItsOwnDoor", fight == 2 && goes && h.carried == violet && !fw.door && !fa.door && !fb.door && !violet.frame);
			h.carried = null;
			h.DropDoor(violet, mo);
		}
		// into the pit, nothing joined: out by its own time door, into the box, and up by door 1
		if (t == 12) Go(mo, 3500, 0, F32, 0);
		if (t == 14) Check("inThePit", k == 2 && bx == 0 && mo.pos.z < -90 && !a.frame && !b.frame);
		if (t == 16) Go(mo, 3760, -96, F32, 0);
		if (t > 16 && t < 34) Walk(mo, (8, 0));
		if (dsStep == 0 && t > 16 && at == 1)
		{
			Check("pitDoorToTheBox", bx == 1 && g == 2);
			Go(mo, 2480, 520, 0, 270);
			dsStep = 1;
			dsT = t;
		}
		if (dsStep == 1 && t > dsT && t < dsT + 14) Walk(mo, (0, -8));
		if (dsStep == 1 && t == dsT + 18)
		{
			Check("outOfThePit", at == 0 && k == 2 && bx == 0 && mo.pos.z > -1 && mo.pos.y > 200 && mo.pos.y < 320 && mo.pos.x > 2400 && mo.pos.x < 2560);
			Go(mo, 8100, 452, G32, 0);           // room 2 is left; room 5 begins
			dsStep = 2;
		}
		// room 5: go 1 holds F1 till 150; go 2 is in L when it shuts, and leaves by L's time door
		if (dsStep == 2 && goes && fight == 5 && g == 1)
		{
			if (o == 5) { Go(mo, 8480, 340, G32, 270); green.Used(mo); }
			if (o == 7) { Go(mo, 8530, 416, G32, 0); g1.Activate(mo); }
			if (o == 11) Go(mo, 8180, 580, G32, 0);
			if (o == 150) Go(mo, 8232, 200, G32, 270);
			if (o > 150 && o < 175) Walk(mo, (0, -8));
		}
		if (dsStep == 2 && goes && fight == 5 && g == 2)
		{
			// (it waits off the way from door 1, where the third self comes in: paradox.zs)
			if (o == 3) Go(mo, 8400, 240, G32, 90);
			if (o == 20) Go(mo, 8530, 416, G32, 0);
			if (o > 20 && o < 35) Ahead(mo);
			if (o == 180) Check("shutInTheLock", k == 5 && mo.pos.x > 8800 && mo.pos.x < 9248 && (lg1.flags & Line.ML_BLOCKING) && !p51.pressed);
			if (o == 182) Go(mo, 9032, 200, G32, 270);
			if (o > 182 && o < 205) Walk(mo, (0, -8));
		}
		if (dsStep == 2 && goes && fight == 5 && g == 3 && o == 2)
		{
			Check("lockDoorToTheBox", at == 1 && bx == 1);
			Go(mo, 8296, -90, G32, 90);
			dsStep = 3;
			dsT = t;
		}
		if (dsStep == 3 && t > dsT && t < dsT + 14) Walk(mo, (0, 8));
		if (dsStep == 3 && t == dsT + 18)
			Check("outOfTheLock", at == 0 && k == 5 && bx == 0 && mo.pos.x > 8048 && mo.pos.x < 8560 && mo.pos.y > 160 && takes.Size() == 3);
	}

	// MODE=2: views of the level, one every 40 tics (tools/smoke_MAP32_2.cfg
	// takes a screenshot of each). Before the last two, BLUE is hung opposite RED;
	// for room 3's shutter open a self (a bare AjarGhost) stands in the chamber.
	void Views32(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		static const double v[] = {
			320, -150, 0, 90, 0,            // room 1 from the start: the sprung frame, the case
			150, 60, 0, 57, 0,              // room 1's case across the room (where Vadim stood)
			480, 362, 0, 90, -10,           // room 1's case, close, straight on
			2192, 40, 0, 90, 0,             // room 2 as entered: the case in the gallery's wall
			2176, 170, 0, 90, -10,          // room 2's case, close
			2300, 200, 0, 0, 0,             // the gallery to the pit
			3500, 0, -96, 70, 0,            // the pit: B and its lamp
			4872, 170, 0, 90, -10,          // room 3's lobby: the case, close
			4800, 150, 0, 8, 0,             // room 3's hall from the lobby, as the player comes in
			5768, 250, 0, 90, 0,            // the press from the hall: its open front (since 2026-11-21) under the lintel
			5768, 784, 0, 20, 0,            // the chamber from the mouth: its east slab, time door 3
			5330, 120, 0, 228, 0,           // the wing's shutter shut, its lamp red
			5330, 120, 0, 228, 0,           // and open: a self in the chamber
			5130, -56, 0, 0, -8,            // the landing: the stairs up along the north wall
			5480, -100, 96, 0, 0,           // the upper room: the lever at the end, the window, the pen's bars
			5768, -40, 96, 90, 0,           // through the window, between the hall's slabs, to the mouth
			5768, 1110, 0, 90, 25,          // the chamber: the screen's plate at the back
			5200, 1090, 0, 138, 25,         // the cage's plate in the north-west corner
			5672, -40, 96, 270, -5,         // the screen open, from the upper room: the bars, the pen
			5672, -40, 96, 270, -5,         // and shut: a self on its plate
			5800, -72, 96, 0, 0,            // the cage through its glass: the megasphere, its shutter and lamp
			5170, -40, 0, 316, 0,           // the landing as the player comes in: the screen's repeater lamp
			6920, 100, -96, 50, 0,          // room 4 as entered: the range from the lobby, the case on its far wall
			7150, 760, -96, 125, 0,         // the west wing just in from its doorway: the first baffle
			6950, 1225, -96, 40, 0,         // the west lever with its lamp, the window beside it
			7168, 1295, -96, 0, 0,          // through the west window, across the range, to the east one
			7456, 1000, -96, 90, 0,         // the shutter with its lamps
			7580, 150, -96, 15, -10,        // room 4's case, close (south of the pillar before it)
			8100, 452, -192, 0, 0,          // room 5 as entered: S, F1 and the case
			8410, 576, -192, 0, -10,        // room 5's case, close
			9856, 172, -192, 90, 0,         // E from PINK's far side, wide: the brass frames face each other
			10040, 384, -192, 180, 0,       // BLUE hung: into RED's frame, the way without end
			9672, 384, -192, 0, 0,          // and the other way, into BLUE's
			// the look (works.zs; PLAN.md, "Look: MAP32"): what it puts on each room, its orange wall lamps
			180, 128, 0, 180, 0,            // room 1: its time door, the lamp over it; a wall lamp beside
			192, 330, 0, 90, 0,             // a frame with its leaf, its pale surround
			-300, 128, 0, 0, 0,             // from the box, through its glass: the room's time door and its lamp
			320, 300, 0, 270, 0,            // TEST BAY 1 over the nook
			2480, 120, 0, 90, 0,            // room 2: its time door with its lamp, TEST BAY 2
			2200, 160, 0, 180, 0,           // frame A with its lamp
			2480, 560, 0, 270, 0,           // from the box, through its glass
			5200, 720, 0, 180, 0,           // room 3: time door 1, its lamp
			5768, 880, 0, 90, 15,           // the chamber's back wall: the scale, a wall lamp, load cell A
			5064, 250, 0, 270, 0,           // CABIN OPENS UNDER LOAD by the wing's shutter
			4880, 520, 0, 0, 0,             // from box 1, through its glass
			6600, 160, 0, 0, 0,             // the corridor to room 4: a wall lamp each side
			7400, 432, -96, 180, 0,         // room 4: time door 1, its lamp
			7120, 120, -96, 90, 0,          // TEST BAY 4 in the lobby
			7288, -150, -96, 90, 0,         // from box 1, through its glass
			8160, 330, -192, 90, 0,         // room 5: TEST BAY 5, a wall lamp beside it
			8232, 400, -192, 270, 0,        // its time door with its lamp
			9856, 250, -192, 90, 0,         // the way out: the hatch, lit orange all round
			8296, -150, -192, 90, 0,        // from the box, through its glass
			8300, 400, -192, 0, 0,          // F1 with its leaf
			5250, 1000, 0, 130, 25,         // the plate line: a self on the cage's plate
			5768, 400, 0, 90, 0,            // the press down: the flare
			320, -150, 0, 90, 0             // room 1 done: its light up
		};
		int WIDE = 30, OPEN3 = 12, SHUT3V = 19, LINE3 = 53, FLARE3 = 54, DONE1 = 55;
		if (t == LINE3 * 40 - 25) dsGhost = Actor.Spawn("AjarGhost", (5096, 1184, 0));        // on the cage's plate
		if (t == LINE3 * 40 + 39 && dsGhost) { dsGhost.Destroy(); dsGhost = null; }
		if (t == FLARE3 * 40 - 15)
		{
			let it = ThinkerIterator.Create("AjarPressSwitch");
			let sw = Actor(it.Next());
			if (sw) sw.Used(mo);
		}
		if (t == DONE1 * 40 - 30 && won.Find(1) == won.Size()) won.Push(1);
		if (t == DONE1 * 40 + 20)
		{
			let wk = AjarWorks.Get();
			if (wk && wk.on) Check("worksTourDone1", wk.StateOf(1) == AjarWorks.DONE && wk.Wrong() == 0);
		}
		int i = t / 40;
		if (t == OPEN3 * 40 - 15) dsGhost = Actor.Spawn("AjarGhost", (5768, 1000, 0));
		if (t == OPEN3 * 40 + 39 && dsGhost) { dsGhost.Destroy(); dsGhost = null; }
		if (t == SHUT3V * 40 - 25) dsGhost = Actor.Spawn("AjarGhost", (5768, 1216, 0));       // on the screen's plate
		if (t == SHUT3V * 40 + 39 && dsGhost) { dsGhost.Destroy(); dsGhost = null; }
		if (i >= v.Size() / 5) return;
		Go(mo, v[i * 5], v[i * 5 + 1], v[i * 5 + 2], v[i * 5 + 3]);
		mo.pitch = v[i * 5 + 4];
		mo.player.SetFOV(i == WIDE ? 130 : 90);      // wide, for both brass frames at once
		Quiet(mo);
		if (t == (WIDE + 1) * 40 - 5)
		{
			let h = Doors();
			AjarDoor blue = Door32(2);
			blue.Used(mo);
			h.FindFrame(191).Activate(mo);
			Console.Printf("AJARTEST info chain=%d", h.chainLen);
		}
	}
}

// MODE=7 (tools/smoke_MAP32_7.cfg): room 3's plates in the chamber, the screen,
// the cage, the sentries and the timetable (PLAN.md, "MAP32 room 3: plates in
// the fight, and the timetable"). Room 3 is entered at its lobby by the script
// (as MODE=5), godmode. Go 1 is the bait: the screen's plate from TT_SCR to
// TT_SCR_OFF, the cage's from TT_CAGE to TT_CAGE_OFF, out by door 3 at TT_OUT1.
// Go 2 goes up the wing, into the cage while the first self holds it (taking
// the megasphere, the backpack, the rockets and the cells), pulls the lever at
// TT_PULL, out by the window and door 2. Go 3 finds all six in the cage again
// (EachGoBack), watches the press lamps from box 2, and begins the fight anew
// (the backpack is gone, the six lie there once each). Then (after every check
// above) go 1 takes them and goes out by door 3, and go 2 finds them again and
// takes them too.
extend class AjarTimeHandler
{
	const TT_SCR = 160;
	const TT_SCR_OFF = 340;
	const TT_CAGE = 370;
	const TT_CAGE_OFF = 520;
	const TT_OUT1 = 700;
	const TT_PULL = 560;
	int ttStep, ttT, ttOutO, ttLandO, ttUpO, ttPull;
	int ttItems, ttFound;       // the level's item total and found count once the megasphere is taken
	int ttRockets, ttCells;     // the player's rockets and cells before the cage's five are taken (or after)
	bool ttSupLay;              // go 2: the five lay there as the player stepped in
	// go 1 as it went, live: the first tic of each hold, and the tic after its last (wing shutter, screen, cage)
	int ttFrom[3], ttTo[3];
	bool ttAmber, ttNoneSee;
	Actor ttMark;

	AjarShutLamp ShutLamp33(int tag, int n)       // the n-th lamp of a shutter
	{
		let it = ThinkerIterator.Create("AjarShutLamp");
		AjarShutLamp l;
		while (l = AjarShutLamp(it.Next())) if (l.args[0] == tag && n-- == 0) return l;
		return null;
	}

	// every lamp of the shutter `tag` (or of the press, `press`) shows frame f
	bool LampsShow(int tag, int f, bool press = false)
	{
		int n = 0;
		let it = ThinkerIterator.Create(press ? "AjarPressLamp" : "AjarShutLamp");
		Actor l;
		while (l = Actor(it.Next()))
		{
			if (l.args[0] != tag) continue;
			if (l.frame != f) return false;
			n++;
		}
		return n > 0;
	}

	// the living monsters in the pen: how many, how many on the demo, how many awake and after the player,
	// how many have sight of `who` (none: not asked)
	int, int, int, int Pen33(Actor mo, Actor who = null)
	{
		int n = 0, demo = 0, after = 0, see = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || !InPen33(a)) continue;
			n++;
			if (OnDemo(a)) demo++;
			else if (a.target == mo) after++;
			if (who && a.CheckSight(who, SF_IGNOREVISIBILITY)) see++;
		}
		return n, demo, after, see;
	}

	// a level trace north from every guard in the pen, at 40 over its feet: stopped by the screen?
	bool TraceStopped33()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || !InPen33(a)) continue;
			FLineTraceData ld;
			a.LineTrace(90, 400, 0, TRF_THRUACTORS, 40, data: ld);       // (past the other guards: the wall is what is asked)
			Console.Printf("AJARTEST info trace from (%d,%d,%d) angle %d: hit=%d at (%.1f,%.1f,%.1f)", a.pos.x, a.pos.y, a.pos.z, a.angle, ld.HitType,
				ld.HitLocation.x, ld.HitLocation.y, ld.HitLocation.z);
			if (ld.HitType != TRACE_HitWall || ld.HitLocation.y < -177 || ld.HitLocation.y > -159) return false;
			n++;
		}
		return n > 0;
	}

	// the megasphere in the cage, lying where it lay (map_secret2.MEGA3)
	bool MegaThere33()
	{
		let it = ThinkerIterator.Create("Megasphere");
		Inventory a;
		while (a = Inventory(it.Next())) if (!a.owner && abs(a.pos.x - 5940) < 1 && abs(a.pos.y + 72) < 1) return true;
		return false;
	}

	// ... how many lie there (one: no double), and of them how many count as an item to be found
	int, int MegasThere33()
	{
		int n = 0, counted = 0;
		let it = ThinkerIterator.Create("Megasphere");
		Inventory a;
		while (a = Inventory(it.Next()))
		{
			if (a.owner || !a.bSpecial || abs(a.pos.x - 5940) >= 1 || abs(a.pos.y + 72) >= 1) continue;
			n++;
			if (a.bCountItem) counted++;
		}
		return n, counted;
	}

	// the backpack, the two boxes of rockets and the two cell packs beside it (map_secret2.SUPPLIES3): of
	// their five spots, how many have one of its kind lying there; how many of those three kinds lie anywhere
	// (five and five: one each where it lay, no double, none elsewhere); and how many count as an item
	int, int, int SuppliesThere33()
	{
		static const int sx[] = { 5944, 5920, 5960, 5920, 5956 };
		static const int sy[] = { -108, -136, -136, -112, -76 };
		int placed = 0, n = 0, counted = 0;
		let it = ThinkerIterator.Create("Inventory");
		Inventory a;
		while (a = Inventory(it.Next()))
		{
			if (a.owner || !a.bSpecial || !(a is "AjarBackpackEachGo" || a is "AjarRocketBoxEachGo" || a is "AjarCellPackEachGo"))
				continue;
			n++;
			if (a.bCountItem) counted++;
			for (int i = 0; i < 5; i++)
			{
				Name cls = i == 0 ? 'AjarBackpackEachGo' : i < 3 ? 'AjarRocketBoxEachGo' : 'AjarCellPackEachGo';
				if (a.GetClassName() == cls && abs(a.pos.x - sx[i]) < 1 && abs(a.pos.y - sy[i]) < 1) { placed++; break; }
			}
		}
		return placed, n, counted;
	}

	// the five as at the first entry: one each where it lay, nothing else, none counted
	bool SuppliesLie33()
	{
		int placed, n, counted;
		[placed, n, counted] = SuppliesThere33();
		Console.Printf("AJARTEST info cage supplies: placed=%d lying=%d counted=%d", placed, n, counted);
		return placed == 5 && n == 5 && !counted;
	}

	// none of the five lies anywhere, and the player has one backpack and may carry 100 rockets and 600 cells
	bool SuppliesTaken33(Actor mo)
	{
		int placed, n, counted;
		[placed, n, counted] = SuppliesThere33();
		Console.Printf("AJARTEST info cage supplies taken: lying=%d backpacks=%d rockets=%d/%d cells=%d/%d", n, Backpacks(mo),
			mo.CountInv("RocketAmmo"), MaxOf(mo, "RocketAmmo"), mo.CountInv("Cell"), MaxOf(mo, "Cell"));
		return !n && Backpacks(mo) == 1 && MaxOf(mo, "RocketAmmo") == 100 && MaxOf(mo, "Cell") == 600;
	}

	void TableScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		AjarShutter sh3 = FindShutter(SHUT33), scr = FindShutter(SCREEN3), cage = FindShutter(CAGE3);
		AjarPlate sp = FloorPlate32(0, SCREEN3), cp = FloorPlate32(0, CAGE3);
		AjarPress pr = FindPress(PRESS32);
		AjarPressSwitch sw = null;
		let si = ThinkerIterator.Create("AjarPressSwitch");
		AjarPressSwitch s;
		while (s = AjarPressSwitch(si.Next())) if (s.args[0] == PRESS32) sw = s;
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		let tb = Table();
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d open=%d at=%d go=%d ot=%d selves=%d screen=%.2f cage=%.2f lamps=%d/%d/%d press=%d rows=%d spans=%d pulls=%d step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, open, at, g, o, AllGhosts(), scr ? scr.Opened() : -1, cage ? cage.Opened() : -1,
			ShutLamp33(SCREEN3, 0) ? ShutLamp33(SCREEN3, 0).frame : -1, ShutLamp33(CAGE3, 0) ? ShutLamp33(CAGE3, 0).frame : -1,
			ShutLamp33(SHUT33, 0) ? ShutLamp33(SHUT33, 0).frame : -1, pr ? pr.phase : -1, tb.rTag.Size(), tb.sRow.Size(), tb.pTic.Size(), ttStep);
		if (t == 2) Go(mo, 4872, 100, 0, 90);           // into room 3's lobby: the rooms before are left, and over
		if (fight != 3) return;

		// === go 1: the bait works the room ===
		if (ttStep == 0 && open && g == 1)
		{
			if (o == 4)
			{
				Check("atRest3", scr.IsOpen() && cage.IsShut() && LampsShow(SCREEN3, AjarLamp.RED) && LampsShow(CAGE3, AjarLamp.RED)
					&& LampsShow(PRESS32, AjarLamp.GREEN, true) && !tb.on && tb.Empty() && sp && cp && !sp.pressed && !cp.pressed);
				ttMark = Actor.Spawn("AjarCam", (5672, -88, 126));      // a point in the upper room, for sight
				for (int i = 0; i < 3; i++) { ttFrom[i] = -1; ttTo[i] = -1; }
			}
			if (o == TT_SCR) Go(mo, 5768, 1216, 0, 90);
			if (o == TT_SCR + 90)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo, ttMark);
				bool stopped = TraceStopped33();
				Console.Printf("AJARTEST info screen down: guards=%d see=%d stopped=%d", n, see, stopped);
				Check("screenDownWithItsPlate3", scr.IsShut() && sp.pressed && n > 0 && !see && stopped && LampsShow(SCREEN3, AjarLamp.GREEN));
				let wk = AjarWorks.Get();      // the look: the plate line lies from the plate to the screen
				if (wk && wk.on) Check("worksPlateLine3", sp.pressed && wk.Traces(sp) > 0);
			}
			if (o == TT_SCR_OFF) Go(mo, 5768, 1120, 0, 270);
			if (o == TT_SCR_OFF + AjarShutter.TICS + 4)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo, ttMark);
				Console.Printf("AJARTEST info screen up: guards=%d see=%d stopped=%d", n, see, TraceStopped33());
				Check("screenUpAgain3", scr.IsOpen() && !sp.pressed && LampsShow(SCREEN3, AjarLamp.RED) && see > 0 && !TraceStopped33());
				let wk = AjarWorks.Get();      // ... and is gone with it
				if (wk && wk.on) Check("worksPlateLineGone3", !sp.pressed && wk.Traces(sp) == 0);
			}
			if (o == TT_CAGE) Go(mo, 5096, 1184, 0, 90);
			if (o == TT_CAGE + 90) Check("cageOpensWithItsPlate3", cage.IsOpen() && cp.pressed && LampsShow(CAGE3, AjarLamp.GREEN));
			if (o == TT_CAGE_OFF) Go(mo, 5096, 1080, 0, 0);
			if (o == TT_CAGE_OFF + AjarShutter.TICS + 4)
			{
				Check("cageShutsAgain3", cage.IsShut() && !cp.pressed && LampsShow(CAGE3, AjarLamp.RED));
				// what lies in the cage is clear of the shutter: none of it lost as it shut
				Check("suppliesStayAsItShuts3", SuppliesLie33() && MegaThere33());
			}
			if (o == TT_OUT1) Go(mo, 6500, 1040, 0, 0);
			if (o > TT_OUT1) Walk(mo, (8, 0));
			// the holds as they go (the take writes this tic's place at index o)
			for (int i = 0; i < 3; i++)
			{
				bool on = i == 0 ? sh3.PlayerIn() : i == 1 ? sp.On(mo) : cp.On(mo);
				if (on && ttFrom[i] < 0) ttFrom[i] = o;
				if (!on && ttFrom[i] >= 0 && ttTo[i] < 0) ttTo[i] = o;
			}
		}
		if (ttStep == 0 && open && g == 2) { ttStep = 1; ttT = t; }

		// === go 2: the wing ===
		if (ttStep == 1 && open && g == 2)
		{
			int len = takes[0].x.Size();
			if (o == 2)
			{
				for (int i = 0; i < 3; i++) if (ttFrom[i] >= 0 && ttTo[i] < 0) ttTo[i] = len;
				static const int tags[] = { SHUT33, SCREEN3, CAGE3 };
				bool ok = tb.on && tb.rTag.Size() == 3 && tb.sRow.Size() == 3 && !tb.pTic.Size();
				for (int r = 0; ok && r < 3; r++)
				{
					int j = tb.sRow.Find(r);
					ok = tb.rTag[r] == tags[r] && j < tb.sRow.Size() && tb.sSelf[j] == 0
						&& abs(tb.sFrom[j] - ttFrom[r]) <= 2 && abs(tb.sTo[j] - ttTo[r]) <= 2;
					Console.Printf("AJARTEST info row %d tag=%d table %d..%d, go 1 %d..%d", r, tb.rTag[r], j < tb.sRow.Size() ? tb.sFrom[j] : -1,
						j < tb.sRow.Size() ? tb.sTo[j] : -1, ttFrom[r], ttTo[r]);
				}
				Check("timetable3", ok);
				ttAmber = true;
			}
			// the lamps: red more than SOON before the earlier self steps on, amber within it, green once worked
			if (o == ttFrom[1] - SOON - 20) ttAmber = ttAmber && LampsShow(SCREEN3, AjarLamp.RED);
			if (o == ttFrom[1] - 40) ttAmber = ttAmber && LampsShow(SCREEN3, AjarLamp.AMBER);
			if (o == ttFrom[1] + AjarShutter.TICS + 6) ttAmber = ttAmber && LampsShow(SCREEN3, AjarLamp.GREEN);
			if (o == ttFrom[2] - SOON - 20) ttAmber = ttAmber && LampsShow(CAGE3, AjarLamp.RED);
			if (o == ttFrom[2] - 40) ttAmber = ttAmber && LampsShow(CAGE3, AjarLamp.AMBER);
			if (o == ttFrom[2] + AjarShutter.TICS + 6)
			{
				ttAmber = ttAmber && LampsShow(CAGE3, AjarLamp.GREEN);
				Check("amberBefore3", ttAmber);
			}
			// out of box 1 by door 1, before the shutter: the guards are on the demo
			if (o == 3) Go(mo, 4810, 560, 64, 180);
			if (o > 3 && !ttOutO)
			{
				if (at == 1) Ahead(mo);
				else ttOutO = o;
			}
			if (ttOutO && o == ttOutO + 3) Go(mo, 5192, 40, 0, 270);
			if (ttOutO && o == ttOutO + 4)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo);
				Console.Printf("AJARTEST info before the wing: guards=%d on the demo=%d", n, demo);
				Check("guardsOnTheDemo3", n > 0 && demo == n);
			}
			// through the shutter once the earlier self holds it open, onto the landing, up the stairs
			if (ttOutO && o > ttOutO + 4 && !ttUpO && sh3.IsOpen() && o > TT_SCR + AjarShutter.TICS)
			{
				if (mo.pos.y > -56 && mo.pos.x < 5300) Walk(mo, (0, -8));
				else if (mo.pos.x < 5600) Walk(mo, (8, 0));
				else { ttUpO = o; mo.vel = (0, 0, 0); Console.Printf("AJARTEST info up at o=%d z=%d", o, mo.pos.z); }
			}
			if (!ttLandO && mo.pos.y < -16 && mo.pos.x < 5272 && mo.pos.x > 5112) ttLandO = o;
			if (ttLandO && o == ttLandO + 10)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo);
				Console.Printf("AJARTEST info on the landing at o=%d: guards=%d on the demo=%d after me=%d", ttLandO, n, demo, after);
				Check("guardsWakeAsIStepIn3", n > 0 && !demo && after == n);
			}
			// the screen held by the earlier self: no guard sees me in the upper room; let go: one does
			if (o == TT_SCR_OFF - 30)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo, mo);
				Console.Printf("AJARTEST info screen held: guards=%d see=%d at (%d,%d,%d)", n, see, mo.pos.x, mo.pos.y, mo.pos.z);
				ttNoneSee = ttUpO && scr.IsShut() && sp.pressed && !sp.On(mo) && n > 0 && !see && mo.pos.z == 96 && mo.pos.y > -160 && mo.pos.y < -16;
			}
			if (o == TT_SCR_OFF + AjarShutter.TICS + 12)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo, mo);
				Console.Printf("AJARTEST info screen let go: guards=%d see=%d", n, see);
				Check("screenHeldByMyEarlierSelf3", ttNoneSee && scr.IsOpen() && see > 0);
			}
			// the cage, held open by the earlier self: in, the megasphere, put out when it steps off
			if (o == TT_CAGE + AjarShutter.TICS + 4)
				Check("cageHeldByMyEarlierSelf3", cage.IsOpen() && cp.pressed && !cp.On(mo) && AllGhosts() >= 1);
			if (o == TT_CAGE + AjarShutter.TICS + 5)
			{
				ttSupLay = SuppliesLie33();
				ttRockets = mo.CountInv("RocketAmmo"); ttCells = mo.CountInv("Cell");
				ttItems = level.total_items; ttFound = level.found_items;
				Go(mo, 5860, -120, 96, 0);
			}
			if (o > TT_CAGE + AjarShutter.TICS + 5 && o <= TT_CAGE + AjarShutter.TICS + 15) Walk(mo, (8, 0));
			if (o > TT_CAGE + AjarShutter.TICS + 15 && o <= TT_CAGE + AjarShutter.TICS + 20) Walk(mo, (0, 8));
			if (o == TT_CAGE + AjarShutter.TICS + 26)
			{
				Console.Printf("AJARTEST info in the cage at (%d,%d,%d) health=%d", mo.pos.x, mo.pos.y, mo.pos.z, mo.health);
				Check("megasphere3", mo.health == 200 && !MegaThere33() && mo.pos.x > 5896);
				// the backpack, the rockets and the cells beside it, walked over on the way: the limits doubled,
				// 5 + 5 rockets and 100 + 100 cells, and the backpack's 1 and 20 (none of them counted: one item
				// found in the cage, the megasphere)
				Console.Printf("AJARTEST info go 2 took rockets %d -> %d, cells %d -> %d, items %d/%d (before %d/%d)", ttRockets, mo.CountInv("RocketAmmo"),
					ttCells, mo.CountInv("Cell"), level.found_items, level.total_items, ttFound, ttItems);
				Check("suppliesTaken3", ttSupLay && SuppliesTaken33(mo) && mo.CountInv("RocketAmmo") == ttRockets + 11
					&& mo.CountInv("Cell") == ttCells + 220 && level.found_items == ttFound + 1 && level.total_items == ttItems);
				ttItems = level.total_items; ttFound = level.found_items;
				ttRockets = mo.CountInv("RocketAmmo"); ttCells = mo.CountInv("Cell");
			}
			if (o == TT_CAGE_OFF + AjarShutter.TICS + 4)
			{
				Console.Printf("AJARTEST info put out at (%d,%d,%d)", mo.pos.x, mo.pos.y, mo.pos.z);
				Check("putOutOfTheCage3", mo.pos.x < 5880 - 15 && mo.pos.x > 5464 && mo.pos.y > -160 && mo.pos.y < -16 && mo.pos.z == 96
					&& cage.IsShut() && !cp.pressed && mo.TestMobjLocation());
			}
			// the lever at TT_PULL; out by the window, and by the hall's time door 2
			if (o == TT_PULL - 15) Go(mo, 5856, -50, 96, 90);
			if (o == TT_PULL)
			{
				Console.Printf("AJARTEST info pulled o=%d ready=%d", o, pr.Ready());
				mo.vel = (0, 0, 0);
				sw.Used(mo);
				ttPull = o;
			}
			if (o == TT_PULL + 5) Go(mo, 5768, -40, 96, 90);
			if (o > TT_PULL + 5 && o < TT_PULL + 18) Walk(mo, (0, 8));
			if (o == TT_PULL + 30) Go(mo, 6500, 720, 0, 0);
			if (o > TT_PULL + 30) Walk(mo, (8, 0));
		}
		if (ttStep == 1 && open && g == 3) { ttStep = 2; ttT = t; Console.Printf("AJARTEST info go 3 begins at t=%d", t); }

		// === go 3: the pull on the timetable, the press lamps; then begin anew ===
		if (ttStep == 2 && open && g == 3)
		{
			if (o == 2)
			{
				int n = tb.pTic.Size();
				Console.Printf("AJARTEST info pulls=%d first=%d (tag %d, self %d) P=%d at=%d", n, n ? tb.pTic[0] : -1, n ? tb.pTag[0] : -1, n ? tb.pSelf[0] : -1, ttPull, at);
				Check("pullOnTheTimetable3", tb.on && n == 1 && tb.pTic[0] == ttPull && tb.pTag[0] == PRESS32 && tb.pSelf[0] == 1);
				ttAmber = true;
				// the megasphere taken in go 2 lies in the cage again, once, not counted again
				int megas, counted;
				[megas, counted] = MegasThere33();
				Console.Printf("AJARTEST info go 3: megaspheres=%d counted=%d items=%d/%d (taken in go 2: %d/%d)", megas, counted,
					level.found_items, level.total_items, ttFound, ttItems);
				Check("megasphereBackNextGo3", MegaThere33() && megas == 1 && !counted && level.total_items == ttItems
					&& level.found_items == ttFound && level.found_items <= level.total_items);
				// and the five beside it, one each, not counted; the player keeps what go 2 took of them (one
				// backpack, the limits doubled, the rockets and cells)
				Check("suppliesBackNextGo3", SuppliesLie33() && Backpacks(mo) == 1 && MaxOf(mo, "RocketAmmo") == 100 && MaxOf(mo, "Cell") == 600
					&& mo.CountInv("RocketAmmo") == ttRockets && mo.CountInv("Cell") == ttCells);
			}
			if (o == 3) Go(mo, 6600, 560, 64, 180);         // in box 2, looking into the hall
			// the guards alive now are on the demo, though the second self is in the wing
			if (o == 300)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo);
				Actor g2 = ghosts.Size() > 1 ? ghosts[1] : null;
				Console.Printf("AJARTEST info go 3: guards=%d on the demo=%d, the second self at (%d,%d)", n, demo, g2 ? g2.pos.x : 0, g2 ? g2.pos.y : 0);
				Check("guardsOnTheDemoAgain3", g2 && InWing33(g2) && at > 0 && n > 0 && demo == n);
			}
			if (o == ttPull - SOON - 20) ttAmber = ttAmber && LampsShow(PRESS32, AjarLamp.GREEN, true);
			if (o == ttPull - 30) ttAmber = ttAmber && LampsShow(PRESS32, AjarLamp.AMBER, true);
			if (o == ttPull + 25)
			{
				Console.Printf("AJARTEST info press phase=%d byGhost=%d", pr.phase, pr.byGhost);
				Check("pressLampAmber3", ttAmber && LampsShow(PRESS32, AjarLamp.RED, true) && pr.phase && pr.byGhost);
			}
			if (o == ttPull + 40)
			{
				AjarFightAnew pl = FightAnewOf(3);
				Vector2 front = pl.pos.xy + Actor.AngleToVector(pl.angle, 40);
				Go(mo, front.x, front.y, 0, pl.angle + 180);
				pl.Used(mo);
				ttStep = 3;
				ttT = t;
			}
		}
		if (ttStep == 3 && t == ttT + 1)
		{
			let tn = Table();
			Check("restAnew3", scr.IsOpen() && cage.IsShut() && MegaThere33() && !tn.on && tn.Empty() && takes.Size() == 1 && open);
			// (the megasphere put back for go 3 lay there: it is the one, counted as at the first entry)
			int megas, counted;
			[megas, counted] = MegasThere33();
			Console.Printf("AJARTEST info anew: megaspheres=%d counted=%d items=%d/%d, at the first entry %d/%d", megas, counted,
				level.found_items, level.total_items, first.levelFound, first.levelItems);
			Check("megasphereCountedAnew3", megas == 1 && counted == 1 && level.total_items == first.levelItems && level.found_items == first.levelFound);
			// the five beside it, one each where it lay; the player's backpack gone (none at the first entry), the
			// limits, rockets and cells as then
			Console.Printf("AJARTEST info anew: backpacks=%d/%d rockets=%d/%d of %d/%d cells=%d/%d of %d/%d", Backpacks(mo), BackpacksFirst(),
				mo.CountInv("RocketAmmo"), MaxOf(mo, "RocketAmmo"), CountFirst("RocketAmmo"), MaxFirst("RocketAmmo"),
				mo.CountInv("Cell"), MaxOf(mo, "Cell"), CountFirst("Cell"), MaxFirst("Cell"));
			Check("suppliesAnew3", SuppliesLie33() && Backpacks(mo) == BackpacksFirst() && MaxOf(mo, "RocketAmmo") == MaxFirst("RocketAmmo")
				&& MaxOf(mo, "Cell") == MaxFirst("Cell") && mo.CountInv("RocketAmmo") == CountFirst("RocketAmmo") && mo.CountInv("Cell") == CountFirst("Cell"));
		}
		// each plate's message is said once a level: on both again
		if (ttStep == 3 && t == ttT + 3) Go(mo, 5768, 1216, 0, 90);
		if (ttStep == 3 && t == ttT + 6) Go(mo, 5768, 1120, 0, 90);
		if (ttStep == 3 && t == ttT + 8) Go(mo, 5096, 1184, 0, 90);
		if (ttStep == 3 && t == ttT + 11) Go(mo, 5096, 1080, 0, 90);
		if (ttStep == 3 && t == ttT + 13)
		{
			Console.Printf("AJARTEST info screen plate steps=%d told=%d, cage plate steps=%d told=%d", sp.steps, sp.told, cp.steps, cp.told);
			Check("saidOnce3", sp.steps >= 2 && sp.told == 1 && cp.steps >= 2 && cp.told == 1);
			Check("noParadox7", !paradoxes && !paradox);      // paradox.zs: no self touched an earlier one
			if (ttMark) ttMark.Destroy();
			ttStep = 4;
		}

		// === begun anew: the megasphere in every go (PLAN.md, "MAP32 room 3: the megasphere lies there
		// again in every go"). Go 1 takes it (counted, as at the first entry), stepping into the cage from
		// behind its shut shutter, and goes out by door 3; go 2 finds it there again, not counted again,
		// leaves box 1 at once (go 1's self comes in by door 3), and takes it too ===
		if (ttStep == 4 && open && g == 1)
		{
			if (o == 20)
			{
				ttItems = level.total_items; ttFound = level.found_items;
				ttRockets = mo.CountInv("RocketAmmo"); ttCells = mo.CountInv("Cell");
				mo.health = mo.player.health = 100;
				Go(mo, 5940, -120, 96, 90);
			}
			if (o > 20 && o <= 26) Walk(mo, (0, 8));
			if (o == 30)
			{
				Console.Printf("AJARTEST info anew, go 1: health=%d items=%d/%d (before %d/%d)", mo.health, level.found_items, level.total_items, ttFound, ttItems);
				Check("megasphereAfterAnew3", mo.health == 200 && !MegaThere33() && level.found_items == ttFound + 1 && level.total_items == ttItems);
				// the five beside it too: the backpack taken again doubles the limits again
				Console.Printf("AJARTEST info anew, go 1 took rockets %d -> %d, cells %d -> %d", ttRockets, mo.CountInv("RocketAmmo"), ttCells, mo.CountInv("Cell"));
				Check("suppliesAfterAnew3", SuppliesTaken33(mo) && mo.CountInv("RocketAmmo") == ttRockets + 11 && mo.CountInv("Cell") == ttCells + 220);
			}
			if (o == 32) Go(mo, 6500, 1040, 0, 0);
			if (o > 32) Walk(mo, (8, 0));
		}
		if (ttStep == 4 && open && g == 2) { ttStep = 5; Console.Printf("AJARTEST info anew, go 2 begins at t=%d", t); }
		if (ttStep == 5 && open && g == 2)
		{
			if (o == 2)
			{
				int megas, counted;
				[megas, counted] = MegasThere33();
				Console.Printf("AJARTEST info anew, go 2: megaspheres=%d counted=%d items=%d/%d at=%d", megas, counted, level.found_items, level.total_items, at);
				Check("megasphereEveryGo3", MegaThere33() && megas == 1 && !counted && level.total_items == ttItems && level.found_items == ttFound + 1);
				// the five too, one each, not counted; the backpack go 1 took is still the player's
				Check("suppliesEveryGo3", SuppliesLie33() && Backpacks(mo) == 1 && MaxOf(mo, "RocketAmmo") == 100 && MaxOf(mo, "Cell") == 600);
			}
			if (o == 3) Go(mo, 5100, 200, 0, 90);
			if (o == 60)
			{
				ttRockets = mo.CountInv("RocketAmmo"); ttCells = mo.CountInv("Cell");
				mo.health = mo.player.health = 100;
				Go(mo, 5940, -120, 96, 90);
			}
			if (o > 60 && o <= 66) Walk(mo, (0, 8));
			if (o == 70)
			{
				Console.Printf("AJARTEST info anew, go 2: health=%d items=%d/%d", mo.health, level.found_items, level.total_items);
				Check("megasphereTakenAgain3", mo.health == 200 && !MegaThere33() && level.found_items == ttFound + 1
					&& level.total_items == ttItems && level.found_items <= level.total_items);
				// the five again (go 1's self, which walked over them first, picked nothing up): a second backpack
				// gives its ammunition only, the limits stay doubled, one backpack
				Console.Printf("AJARTEST info anew, go 2 took rockets %d -> %d, cells %d -> %d", ttRockets, mo.CountInv("RocketAmmo"), ttCells, mo.CountInv("Cell"));
				Check("suppliesTakenAgain3", SuppliesTaken33(mo) && mo.CountInv("RocketAmmo") == ttRockets + 11 && mo.CountInv("Cell") == ttCells + 220);
				Check("noParadoxEachGo3", !paradoxes && !paradox);
				ttStep = 6;
			}
		}
	}
}

// MODE=8 (tools/smoke_MAP32_8.cfg): room 4's key levers over four goes (PLAN.md,
// "MAP32 room 4: two keys under fire"). Room 4 is entered at its lobby by the
// script, godmode. Go 1 pulls the west lever at KS_P and leaves by door 1; go
// 2 pulls the east lever 100 tics late (nothing opens); go 3 pulls it 30 after
// KS_P (keyed: the second self's late pull finds it down); in go 4 the earlier
// selves open the shutter by themselves, on the timetable, its lamps amber
// before. The cfg takes a screenshot in go 4 with the bar under the clock.
extend class AjarTimeHandler
{
	const KS_P = 200;           // go 1 pulls the west lever
	const KS_STAY3 = 330;       // go 3 leaves this long after its start (go 4's clock and bar are up as long)
	int ksKeyO, ksK31;
	double ksOpenMax;
	bool ksAmber;

	void KeyScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		AjarShutter sh = FindShutter(SHUT32);
		AjarKeyLever kw = FindKeyLever(SHUT32, 1), ke = FindKeyLever(SHUT32, 2);
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		let tb = Table();
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d open=%d at=%d go=%d ot=%d selves=%d shutter=%.2f keyed=%d levers=%d/%d rows=%d spans=%d keys=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, open, at, g, o, AllGhosts(), sh ? sh.Opened() : -1, sh ? sh.keyed : -1,
			kw ? kw.frame : -1, ke ? ke.frame : -1, tb.rTag.Size(), tb.sRow.Size(), tb.kTic.Size());
		if (t == 2) Go(mo, 6950, 176, F32, 0);         // into room 4's lobby: the rooms before are left, and over
		if (fight != 4 || !open) return;
		// go 1: the west lever at KS_P; out by door 1
		if (g == 1)
		{
			if (o == 5) Go(mo, 7040, 1340, F32, 90);
			if (o > 5 && o < KS_P) mo.vel.xy = (0, 0);
			if (o == KS_P) kw.Used(mo);
			if (o == KS_P + 10) Go(mo, 7240, 432, F32, 180);
			if (o > KS_P + 10) Walk(mo, (-8, 0));
		}
		// go 2: the east lever, 100 tics after the first self's west one: too late
		if (g == 2)
		{
			if (o == 2) ksOpenMax = 0;
			if (o > 2) ksOpenMax = max(ksOpenMax, sh.Opened());
			if (o == 3) Go(mo, 7872, 1340, F32, 90);
			if (o > 3 && o < KS_P + 100) mo.vel.xy = (0, 0);
			if (o == KS_P + 100) ke.Used(mo);
			if (o == KS_P + 100 + AjarKeyLever.JOIN + 5)
			{
				Console.Printf("AJARTEST info too late: opened=%.2f keyed=%d up=%d/%d", ksOpenMax, sh.keyed, kw.Up(), ke.Up());
				Check("tooLateTogether4", ksOpenMax == 0 && !sh.keyed && sh.IsShut() && kw.Up() && ke.Up());
			}
			if (o == KS_P + 180) Go(mo, 7240, 432, F32, 180);
			if (o > KS_P + 180) Walk(mo, (-8, 0));
		}
		// go 3: the east lever within JOIN of the first self's: keyed; the second self's late pull finds it down
		if (g == 3)
		{
			// (40 west of where the second self stands at the lever till KS_P + 180, and still within
			// reach of it: on that spot it would touch it, paradox.zs)
			if (o == 3) Go(mo, 7832, 1340, F32, 90);
			if (o > 3 && o < KS_P + 30) mo.vel.xy = (0, 0);
			if (o == KS_P + 30) { ke.Used(mo); ksKeyO = o; }
			if (o == KS_P + 32) ksK31 = sh.keyed;
			if (o == KS_P + 110)
			{
				Console.Printf("AJARTEST info in time: keyed=%d (%d at +32) open=%.2f held=%d/%d", sh.keyed, ksK31, sh.Opened(), kw.held, ke.held);
				Check("inTimeWithMyFirstSelf4", sh.IsOpen() && ksK31 > 1000 && abs(sh.keyed - (ksK31 - 78)) <= 1 && ke.held && kw.held);
			}
			if (o == KS_STAY3) Go(mo, 7240, 432, F32, 180);
			if (o > KS_STAY3) Walk(mo, (-8, 0));
		}
		// go 4: the earlier selves open it between them, the player nowhere near a lever
		if (g == 4)
		{
			int keyAt = KS_P + 30;
			if (o == 2)
			{
				int r = tb.rTag.Find(SHUT32), spans = 0;
				bool span = false;
				for (int i = 0; i < tb.sRow.Size(); i++)
				{
					if (tb.sRow[i] != r) continue;
					spans++;
					span = abs(tb.sFrom[i] - keyAt) <= 2 && tb.sTo[i] - tb.sFrom[i] == 30 * 35 && tb.sSelf[i] == 2;
					Console.Printf("AJARTEST info span %d..%d of self %d", tb.sFrom[i], tb.sTo[i], tb.sSelf[i]);
				}
				bool pulls = tb.kTic.Size() == 3;
				for (int i = 0; i < tb.kTic.Size(); i++)
				{
					Console.Printf("AJARTEST info key pull at %d, lever %d, self %d", tb.kTic[i], tb.kNum[i], tb.kSelf[i]);
					int want = tb.kSelf[i] == 0 ? KS_P : tb.kSelf[i] == 1 ? KS_P + 100 : KS_P + 30;
					if (abs(tb.kTic[i] - want) > 1 || tb.kNum[i] != (tb.kSelf[i] ? 2 : 1) || tb.kTag[i] != SHUT32) pulls = false;
				}
				Check("shutterOnTheTimetable4", tb.on && r < tb.rTag.Size() && spans == 1 && span && pulls);
				ksAmber = true;
			}
			if (o == 3) Go(mo, 7456, 900, F32, 90);     // in the range, facing the shutter, far from both levers
			if (o > 3) mo.vel.xy = (0, 0);
			if (o == keyAt - AjarTimeHandler.SOON - 20) ksAmber = ksAmber && LampsShow(SHUT32, AjarLamp.RED);
			if (o == keyAt - 40) ksAmber = ksAmber && LampsShow(SHUT32, AjarLamp.AMBER);
			if (o == keyAt + AjarShutter.TICS + 4)
			{
				Console.Printf("AJARTEST info go 4: open=%.2f keyed=%d held=%d/%d away %d/%d", sh.Opened(), sh.keyed, kw.held, ke.held, mo.Distance2D(kw), mo.Distance2D(ke));
				Check("openedByMyEarlierSelves4", sh.IsOpen() && sh.keyed > 0 && kw.held && ke.held && mo.Distance2D(kw) > 500 && mo.Distance2D(ke) > 500
					&& AllGhosts() >= 2);
				Check("amberBeforeItOpens4", ksAmber && LampsShow(SHUT32, AjarLamp.GREEN));
				Check("noParadox8", !paradoxes && !paradox);      // paradox.zs
			}
			if (o == keyAt + 60) Console.Printf("AJARTEST info go 4 at o=%d is t=%d (the screenshot is due)", o, t);
		}
	}
}

// MODE=9 (tools/smoke_MAP32_9.cfg): an earlier self's shots wake nobody
// (PLAN.md, "Fights of goes: an earlier self's shots wake nobody"). Room 3 is
// entered at its lobby by the script (as MODE=5 and 7), godmode. Go 1 is the
// bait in the chamber by door 3, as in MODE=3, and it shoots: rockets at the
// weakest monster in sight until one it hurt is dead, then plasma twice each
// at two big monsters; out by door 3.
// Go 2 stays in box 1 and touches nothing: the earlier self's shots fly
// again and hit again, and no monster wakes before the demo's end; the one it
// killed dies when it died, once; at the demo's end those it hurt wake with
// the health the record had (less what was counted of hits the demo has not:
// the replay is not exact, a shot that missed then can hit now).
extend class AjarTimeHandler
{
	const GS_FIRE = 150;        // go 1 fires from this tic on, every GS_EVERY
	const GS_EVERY = 8;
	int gsStep, gsShots, gsBigShots, gsDoneO, gsLeaveO, gsLen, gsKills0;
	Actor gsBig1, gsBig2;
	// go 1: the roles the player hurt, the tic of the first hit, the tic it died (-1: alive)
	Array<AjarRole> gsHurt;
	Array<int> gsHurtO, gsKilledO;
	// go 2, of each: deaths, the tic of the last and its mode then, the most dmg counted on its rail,
	// its health on the tic it was seen awake (-1: not yet), whether it woke before the demo's end
	Array<int> gsDeaths2, gsDiedO2, gsDiedMode2, gsDmg2, gsWokeHp2, gsEarly2;
	int gsAwakeMax, gsAfterMax;
	Array<int> gsNewOff;        // go 2: of each hit of the earlier self that was counted, the record's nearest fall from it

	bool GsOn() { return CVar.GetCVar("ajar_autotest").GetInt() == 9 && level.mapname ~== "MAP32" && open && fight == 3; }

	// (from WorldThingDamaged) go 1: who the player hurt
	void GsDamaged(Actor a, Actor s, int dmg)
	{
		// go 2: a hit of the earlier self that was counted (the demo has not got it): how far the record's
		// nearest fall of that monster's health is (it must be beyond REPLAY_TICS)
		if (a && s is "AjarGhost" && a.bIsMonster && dmg > 0 && GsOn() && takes.Size() == 2 && demo && OnDemo(a))
		{
			for (int k = 0; k < demo.roles.Size(); k++)
			{
				AjarRole q = demo.roles[k];
				if (q.actor != a) continue;
				int i = ot - q.born, best = 99999;
				for (int j = 1; j < q.hp.Size(); j++) if (q.sf[j] >= 0 && q.sf[j - 1] >= 0 && q.hp[j] < q.hp[j - 1] && abs(j - i) < abs(best)) best = j - i;
				gsNewOff.Push(best);
				Console.Printf("AJARTEST info go 2: a hit the demo has not, on %s at %d (%d): its record's nearest fall %+d tics away", a.GetClassName(), ot, dmg, best);
			}
		}
		if (!a || !s || !s.player || !a.bIsMonster || dmg <= 0 || takes.Size() != 1 || !rec || !GsOn()) return;
		AjarRole r = RoleOf(a);
		if (!r || gsHurt.Find(r) < gsHurt.Size()) return;
		gsHurt.Push(r); gsHurtO.Push(ot); gsKilledO.Push(-1);
		gsDeaths2.Push(0); gsDiedO2.Push(-1); gsDiedMode2.Push(-1); gsDmg2.Push(0); gsWokeHp2.Push(-1); gsEarly2.Push(0);
	}

	// (from WorldThingDied) go 1: when the ones the player hurt died; go 2: their deaths, and when
	void GsDied(Actor a)
	{
		if (!a || !a.bIsMonster || !GsOn()) return;
		if (takes.Size() == 1)
		{
			AjarRole r = rec ? RoleOf(a) : null;
			int i = r ? gsHurt.Find(r) : gsHurt.Size();
			if (i < gsHurt.Size() && gsKilledO[i] < 0) gsKilledO[i] = ot;
			return;
		}
		if (takes.Size() != 2) return;
		for (int i = 0; i < gsHurt.Size(); i++)
		{
			if (gsHurt[i].actor != a) continue;
			gsDeaths2[i]++; gsDiedO2[i] = ot; gsDiedMode2[i] = gsHurt[i].mode;
		}
	}

	// a living monster awake in sight, not `but`: the weakest (the nearest of those), or the nearest of 300 health or more
	Actor GsTarget(Actor mo, bool weakest, Actor but = null)
	{
		Actor best = null;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || a == but || OnDemo(a)) continue;
			if (!weakest && a.health < 300) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != 3 || b != 0 || !mo.CheckSight(a)) continue;
			if (!best || (weakest && a.health < best.health)
				|| ((!weakest || a.health == best.health) && mo.Distance2D(a) < mo.Distance2D(best))) best = a;
		}
		return best;
	}

	void GsFire(PlayerPawn mo, Actor t, class<Actor> cls)
	{
		mo.angle = VectorAngle(t.pos.x - mo.pos.x, t.pos.y - mo.pos.y);
		mo.pitch = 0;
		if (mo.SpawnPlayerMissile(cls)) gsShots++;        // (aimed up or down at it by autoaim; none if it burst at once)
	}

	void GhostShotScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d open=%d mixed=%d at=%d go=%d ot=%d len=%d selves=%d onDemo=%d awake=%d left=%d shots=%d hurt=%d replays=%d new=%d step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, open, mixed, at, g, o, demo ? demo.len : -1, AllGhosts(), Rails(true), Rails(false),
			phase ? Left() : -1, gsShots, gsHurt.Size(), ghostReplays, ghostNew, gsStep);
		if (t == 2) Go(mo, 4872, 100, 0, 90);           // into room 3's lobby: the rooms before are left, and over
		if (fight != 3 || !open) return;

		// === go 1: the bait by door 3, and it shoots ===
		if (gsStep == 0 && g == 1)
		{
			if (o == 4)
			{
				Console.Printf("AJARTEST info left=%d", Left());
				Check("begun9", phase == LIVE && open && mixed && Left() >= 17);
			}
			if (o == 8) Go(mo, 6500, 1040, 0, 180);
			if (o > 8 && !gsLeaveO && (mo.pos.xy - (6500, 1040)).Length() > 8) Go(mo, 6500, 1040, 0, mo.angle);
			if (o >= GS_FIRE && !gsDoneO && o % GS_EVERY == 0)
			{
				int dead = 0;
				for (int i = 0; i < gsKilledO.Size(); i++) if (gsKilledO[i] >= 0) dead++;
				Actor tg = null;
				if (!dead && gsShots < 40) tg = GsTarget(mo, true);
				else if (dead && gsBigShots < 4)
				{
					if (gsBigShots < 2 && (!gsBig1 || gsBig1.health <= 0 || !mo.CheckSight(gsBig1))) gsBig1 = GsTarget(mo, false);
					if (gsBigShots >= 2 && (!gsBig2 || gsBig2.health <= 0 || !mo.CheckSight(gsBig2))) gsBig2 = GsTarget(mo, false, gsBig1);
					tg = gsBigShots < 2 ? gsBig1 : gsBig2;
					if (tg) gsBigShots++;
				}
				else gsDoneO = o;
				if (tg) GsFire(mo, tg, dead ? "PlasmaBall" : "Rocket");
				if (!gsDoneO && o >= 900) gsDoneO = o;
			}
			// out by door 3, three seconds after the last shot (its deaths are written down)
			if (gsDoneO && !gsLeaveO && o >= gsDoneO + 105)
			{
				int dead = 0, alive = 0;
				for (int i = 0; i < gsHurt.Size(); i++)
				{
					Actor a = gsHurt[i].src;
					if (gsKilledO[i] >= 0) dead++;
					else if (a && a.health > 0) alive++;
					Console.Printf("AJARTEST info go 1 hurt: %s first hit at %d, died at %d, health %d of %d", gsHurt[i].cls.GetClassName(), gsHurtO[i],
						gsKilledO[i], a ? a.health : -1, a ? a.SpawnHealth() : -1);
				}
				Console.Printf("AJARTEST info the bait leaves o=%d shots=%d written down=%d hurt=%d dead=%d alive=%d", o, gsShots,
					takes[0].evTic.Size(), gsHurt.Size(), dead, alive);
				Check("baitShoots3", dead >= 1 && alive >= 1 && takes[0].evTic.Size() >= gsShots);
				gsLeaveO = o;
				Go(mo, 6510, 1040, 0, 0);
				// out with less than RESCUE_HEALTH: in the box it has that, as if killed (time.zs). (God mode
				// stays on: it keeps damage off, not health up, and a hit now would make this a death.)
				mo.health = mo.player.health = 20;
			}
			if (gsLeaveO && o > gsLeaveO) Walk(mo, (8, 0));
		}
		if (gsStep == 0 && g == 2)
		{
			gsStep = 1;
			gsLen = demo ? demo.len : 0;
			gsKills0 = mo.player.killcount;
			ghostReplays = 0;
			ghostNew = 0;
		}

		// === go 2: in box 1, still; the earlier self shoots again ===
		if (gsStep == 1 && g == 2)
		{
			mo.vel = (0, 0, 0);
			if (o == 2) Check("inTheBox9", at == 1 && bx == 1 && demo != null && !takes[0].died && takes[0].door == HallLine(3, 3));
			if (o == 2) Check("outWithLittleAsIfKilled3", mo.health == RESCUE_HEALTH);
			if (o >= 2 && o <= gsLen - 1)
			{
				// nothing of the hall awake, nothing after me, while the demo plays
				int awake = 0, after = 0;
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next()))
				{
					if (!a.bIsMonster || a.health <= 0) continue;
					int ak, ab;
					[ak, ab] = Where(a.pos.xy);
					if (ak != 3 || ab != 0) continue;
					if (!OnDemo(a)) awake++;
					if (a.target == mo) after++;
				}
				gsAwakeMax = max(gsAwakeMax, awake);
				gsAfterMax = max(gsAfterMax, after);
			}
			for (int i = 0; i < gsHurt.Size(); i++)
			{
				AjarRole r = gsHurt[i];
				Actor a = r.actor;
				if (!a) continue;
				let rail = AjarRail(a.FindInventory("AjarRail"));
				if (rail) gsDmg2[i] = max(gsDmg2[i], rail.dmg);
				if (r.mode == 2 && a.health > 0 && gsWokeHp2[i] < 0)
				{
					gsWokeHp2[i] = a.health;
					if (o <= gsLen - 1) gsEarly2[i] = 1;
				}
			}
			if (o == gsLen + 45)
			{
				bool none = gsAwakeMax == 0 && gsAfterMax == 0 && ghostReplays > 0, once = true, when = true;
				int hurtAlive = 0, below = 0, dead = 0;
				for (int i = 0; i < gsHurt.Size(); i++)
				{
					AjarRole r = gsHurt[i];
					int last = r.hp.Size() ? r.hp[r.hp.Size() - 1] : -1;
					Console.Printf("AJARTEST info go 2: %s hit at %d died at %d (now %d, %d times, mode %d) dmg=%d woke with %d of the record's %d (spawn %d) early=%d",
						r.cls.GetClassName(), gsHurtO[i], gsKilledO[i], gsDiedO2[i], gsDeaths2[i], gsDiedMode2[i], gsDmg2[i], gsWokeHp2[i], last,
						GetDefaultByType(r.cls).health, gsEarly2[i]);
					if (gsEarly2[i]) none = false;
					if (gsKilledO[i] >= 0)
					{
						dead++;
						if (gsDeaths2[i] != 1 || abs(gsDiedO2[i] - gsKilledO[i]) > 1 || gsDiedMode2[i] != 1) when = false;
						continue;
					}
					// (what was counted on it can only be hits the demo has not: it wakes with the record's health less that;
					// if that was all of it, it fell on the demo)
					if (gsDeaths2[i]) { if (gsDeaths2[i] != 1 || gsDmg2[i] <= 0 || gsDiedMode2[i] != 2) once = false; continue; }
					hurtAlive++;
					if (gsWokeHp2[i] != last - gsDmg2[i]) once = false;
					if (last < GetDefaultByType(r.cls).health) below++;
				}
				// a hit the demo had (a fall within REPLAY_TICS) was never counted
				for (int i = 0; i < gsNewOff.Size(); i++) if (abs(gsNewOff[i]) <= REPLAY_TICS) once = false;
				Console.Printf("AJARTEST info awake while the demo played=%d after me=%d replays=%d new=%d kills in go 2=%d len=%d",
					gsAwakeMax, gsAfterMax, ghostReplays, ghostNew, mo.player.killcount - gsKills0, gsLen);
				Check("myEarlierSelfsShotsWakeNone3", none);
				Check("hurtOnceNotTwice3", once && hurtAlive > 0 && below > 0);
				Check("diedWhenItDied3", when && dead > 0);
				Check("noParadox9", !paradoxes && !paradox);      // paradox.zs
				gsStep = 2;
			}
		}
	}
}

// MODE=10 (tools/smoke_MAP32_10.cfg): winding the fights of goes (PLAN.md,
// "MAP32: winding the fights of goes"). The plates: eight in each of rooms 3
// and 4, back on the left, on on the right. Room 3, entered at its lobby by the
// script, godmode. Go 1: nothing to wind yet; it waits in the lobby, stands on
// the screen's plate from WF_S0 to WF_S1 and on the cage's from WF_C0 to
// WF_C1, pulls the press at WF_P and goes out by door 2. Go 2, from box 1:
// wound on to WF_W1 + half a minute (the screen held at once by the first
// self, the monsters and it where the record has them, the price paid); the
// first self lets go of the screen and steps on the cage's plate at its tic;
// the megasphere taken; wound back while the first self's press comes down
// (the press up, the megasphere not put back); refused at 10 health; into the
// hall and on from there while nothing is awake, to two seconds before the
// end, and no further; not once something is awake; on the screen's plate,
// out by door 2. Go 3: the second self stands where it wound from up to then,
// and then does what was done. Room 4: go 1 pulls both key levers; go 2 winds
// on past the pulls (keyed at once, for what is left), back before them (up),
// and they are pulled at their tics. Then room 4 is won, and its plates say
// nothing plays.
extend class AjarTimeHandler
{
	const WF_W1 = 30;           // go 2 winds on from here
	const WF_S0 = 950;          // go 1 on the screen's plate
	const WF_S1 = 1120;
	const WF_C0 = 1130;         // on the cage's plate
	const WF_C1 = 1190;
	const WF_P = 1205;          // pulls the press
	const WF_OUT = 1210;        // out by door 2
	const WK_W = 200;           // room 4, go 1: the west lever
	const WK_E = 230;           // the east one
	const WK_OUT = 1200;
	int wfStep, wfT1, wfT3, wfLen2, wfH, wfA, wfPhase, wfT;
	Vector3 wfSpot;
	Array<Actor> wfSeen;        // (the awake ones already told of)
	bool wfOk;

	// the plate that winds (`on`) in box b of room k (0: its hall)
	AjarWind Wind32(int k, int b, bool on)
	{
		let it = ThinkerIterator.Create("AjarWind");
		AjarWind w;
		while (w = AjarWind(it.Next()))
		{
			int wk, wb;
			[wk, wb] = Where(w.pos.xy);
			if (wk == k && wb == b && (w.args[0] != 0) == on) return w;
		}
		return null;
	}

	// rooms 3 and 4: one back and one on in each box and the hall, eight in each; back on the left of one
	// who faces the wall they are on
	bool Plates32()
	{
		int n3 = 0, n4 = 0;
		let it = ThinkerIterator.Create("AjarWind");
		AjarWind w;
		while (w = AjarWind(it.Next()))
		{
			int wk, wb;
			[wk, wb] = Where(w.pos.xy);
			if (wk == 3) n3++;
			if (wk == 4) n4++;
		}
		bool ok = n3 == 8 && n4 == 8;
		for (int k = 3; k <= 4; k++)
		{
			for (int b = 0; b <= 3; b++)
			{
				AjarWind back = Wind32(k, b, false), on = Wind32(k, b, true);
				if (!back || !on) { ok = false; continue; }
				double left = (back.pos.xy - on.pos.xy) dot Actor.AngleToVector(back.angle + 270);
				Console.Printf("AJARTEST info room %d box %d: back (%d,%d) on (%d,%d) facing %d, back to the left by %d", k, b,
					back.pos.x, back.pos.y, on.pos.x, on.pos.y, back.angle, left);
				if (left <= 0 || back.angle != on.angle) ok = false;
			}
		}
		return ok;
	}

	int Armour(Actor mo) { let a = mo.FindInventory("BasicArmor"); return a ? a.Amount : 0; }

	// earlier self i stands where its record puts it at tic o
	bool SelfAt(int i, int o)
	{
		if (i >= takes.Size() - 1 || i >= ghosts.Size() || !ghosts[i] || o >= takes[i].x.Size()) return false;
		return ghosts[i].pos.x == takes[i].x[o] && ghosts[i].pos.y == takes[i].y[o];
	}

	void Wind32FightScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		AjarShutter sh3 = FindShutter(SHUT33), scr = FindShutter(SCREEN3), cage = FindShutter(CAGE3), sh4 = FindShutter(SHUT32);
		AjarPlate sp = FloorPlate32(0, SCREEN3), cp = FloorPlate32(0, CAGE3);
		AjarPress pr = FindPress(PRESS32);
		AjarKeyLever kw = FindKeyLever(SHUT32, 1), ke = FindKeyLever(SHUT32, 2);
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d open=%d mixed=%d at=%d go=%d ot=%d len=%d selves=%d onDemo=%d awake=%d health=%d screen=%.2f cage=%.2f wing=%.2f press=%d shutter4=%.2f keyed=%d step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, open, mixed, at, g, o, demo ? demo.len : -1, AllGhosts(), Rails(true), Rails(false), mo.health,
			scr ? scr.Opened() : -1, cage ? cage.Opened() : -1, sh3 ? sh3.Opened() : -1, pr ? pr.phase : -1, sh4 ? sh4.Opened() : -1, sh4 ? sh4.keyed : -1, wfStep);
		if (t == 2) Go(mo, 4872, 100, 0, 90);           // into room 3's lobby: the rooms before are left, and over
		// (any monster of room 3's hall that is real while the demo plays, told once: what, where, and its
		// role on the demo if it has one; only the one go 2 hurts is expected)
		if (open && Demoing() && fight == 3 && demo)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (!a.bIsMonster || a.health <= 0 || OnDemo(a) || wfSeen.Find(a) < wfSeen.Size()) continue;
				int ak, ab;
				[ak, ab] = Where(a.pos.xy);
				if (ak != fight || ab != 0) continue;
				wfSeen.Push(a);
				string why = "no role";
				for (int i = 0; i < demo.roles.Size(); i++)
				{
					AjarRole r = demo.roles[i];
					if (r.actor != a && r.src != a) continue;
					why = String.Format("role %d born=%d size=%d lag=%d mode=%d dead=%d hidden=%d wakeDue=%d cue=%d", i, r.born, r.x.Size(), r.lag, r.mode, r.dead, r.hidden,
						r.wakeDue, r.cue ? 1 : 0);
				}
				Console.Printf("AJARTEST info woke at ot=%d: %s at (%d,%d) health %d: %s", ot, a.GetClassName(), a.pos.x, a.pos.y, a.health, why);
			}
		}

		// === room 3, go 1: the plates; nothing to wind; the screen, the cage, the press; out by door 2 ===
		if (wfStep == 0 && fight == 3 && open && g == 1)
		{
			if (o == 4) Check("plates10", Plates32());
			if (o == 5)
			{
				int h = mo.health;
				Wind32(3, 0, false).Used(mo);
				Check("nothingToWindYet10", ot == o && mo.health == h && takes.Size() == 1);
			}
			if (o > 5 && o < WF_S0) mo.vel.xy = (0, 0);
			// on the plates (put back on each tic: a monster that comes under the player lifts them off)
			if (o >= WF_S0 && o < WF_S1) Go(mo, 5768, 1216, 0, 90);
			if (o == WF_S0 + AjarShutter.TICS + 4) Check("screenByMe10", scr.IsShut() && sp.pressed && sh3.IsOpen());
			if (o == WF_S1) Go(mo, 5768, 1120, 0, 270);
			if (o >= WF_C0 && o < WF_C1) Go(mo, 5096, 1184, 0, 90);
			if (o == WF_C1) Go(mo, 5096, 1080, 0, 0);
			if (o == WF_P - 10) Go(mo, 5856, -50, 96, 90);
			if (o == WF_P)
			{
				AjarPressSwitch sw = null;
				let si = ThinkerIterator.Create("AjarPressSwitch");
				AjarPressSwitch s;
				while (s = AjarPressSwitch(si.Next())) if (s.args[0] == PRESS32) sw = s;
				sw.Used(mo);
				Console.Printf("AJARTEST info go 1 pulled the press at %d: phase=%d", o, pr.phase);
			}
			if (o == WF_OUT) Go(mo, 6500, 720, 0, 0);
			if (o > WF_OUT) Walk(mo, (8, 0));
		}
		if (wfStep == 0 && fight == 3 && open && g == 2) wfStep = 1;

		// === go 2: from box 1 ===
		if (wfStep == 1 && fight == 3 && open && g == 2)
		{
			if (o == 2)
			{
				Check("inBox1_10", at == 1 && bx == 1 && demo != null);
				mo.health = mo.player.health = 100;
				mo.GiveInventoryType("GreenArmor");
			}
			if (o == 3) Go(mo, 4900, 560, 64, 0);
			if (o > 3) mo.vel.xy = (0, 0);
			// on, half a minute: the first self on the screen's plate at once
			if (o == WF_W1)
			{
				wfH = mo.health; wfA = Armour(mo);
				Wind32(3, 1, true).Used(mo);
				wfT1 = ot;
				Console.Printf("AJARTEST info wound on from %d to %d: health %d armour %d (were %d, %d) screen=%.2f wing=%.2f selves=%d",
					o, ot, mo.health, Armour(mo), wfH, wfA, scr.Opened(), sh3.Opened(), AllGhosts());
				Check("woundOn10", wfT1 == WF_W1 + WIND_TICS && takes.Size() == 2 && takes[1].x.Size() == wfT1 && wound && !parted.Size());
				Check("itCosts10", mo.health == wfH - WIND_HEALTH && Armour(mo) == wfA - WIND_ARMOUR);
				Check("screenHeldAtOnce10", scr.IsShut() && sp.pressed && !sp.On(mo) && sh3.IsOpen() && cage.IsShut() && !cp.pressed
					&& pr.Ready() && SelfAt(0, wfT1));
			}
			if (wfT1 && ot == wfT1 + 1 && o == ot)
			{
				Console.Printf("AJARTEST info at %d: on the demo %d, awake %d, the first self at (%d,%d)", wfT1, Rails(true), Rails(false),
					ghosts.Size() && ghosts[0] ? ghosts[0].pos.x : 0, ghosts.Size() && ghosts[0] ? ghosts[0].pos.y : 0);
				Check("asTheRecordHasItAtT10", AsTheyWent() && Rails(true) > 0 && !Awake() && SelfAt(0, wfT1));
			}
			// after T, at their tics: the first self lets go of the screen, steps on the cage's plate
			if (wfT1 && o == WF_S1 + AjarShutter.TICS + 4) Check("screenLetGoAtItsTic10", scr.IsOpen() && !sp.pressed);
			if (wfT1 && o == WF_C0 + AjarShutter.TICS + 4) Check("cageAtItsTic10", cage.IsOpen() && cp.pressed && !cp.On(mo));
			// the megasphere, taken (from here)
			if (wfT1 && o == WF_C0 + 20)
			{
				let it = ThinkerIterator.Create("Megasphere");
				Inventory a, mega = null;
				while (a = Inventory(it.Next())) if (!a.owner && abs(a.pos.x - 5940) < 1 && abs(a.pos.y + 72) < 1) mega = a;
				if (mega) mega.Touch(mo);
			}
			if (wfT1 && o == WF_C0 + 22)
			{
				int megas, counted;
				[megas, counted] = MegasThere33();
				Check("megasphereTaken10", mo.health == 200 && !MegaThere33() && !megas);
			}
			// back, while the first self's press comes down
			if (wfT1 && o == WF_P + 30)
			{
				wfH = mo.health; wfA = Armour(mo); wfPhase = pr.phase;
				Wind32(3, 1, false).Used(mo);
				Console.Printf("AJARTEST info wound back from %d to %d: press phase %d, now %d lowered %.2f; health %d armour %d (were %d, %d)",
					o, ot, wfPhase, pr.phase, pr.Lowered(), mo.health, Armour(mo), wfH, wfA);
				Check("woundBack10", ot == min(o, demo.len) - WIND_TICS && takes[1].x.Size() == ot && mo.health == wfH - WIND_HEALTH && Armour(mo) == wfA - WIND_ARMOUR);
				Check("pressUpAtOnce10", wfPhase > 0 && pr.Ready() && pr.Lowered() < 0.01);
				Check("asItWasThen10", scr.IsOpen() && !sp.pressed && cage.IsShut() && !cp.pressed && sh3.IsShut() && SelfAt(0, ot));
				int megas, counted;
				[megas, counted] = MegasThere33();
				Check("megasphereNotPutBack10", !MegaThere33() && !megas && wfH == 200);
				wfStep = 2;
				wfT = ot;
			}
		}
		if (wfStep == 2 && fight == 3 && open && g == 2)
		{
			if (o == wfT + 1) Check("monstersAsThen10", AsTheyWent() && Rails(true) > 0 && !Rails(false) && SelfAt(0, wfT));
			if (o == wfT + 5)
			{
				mo.health = mo.player.health = 10;
				Wind32(3, 1, false).Used(mo);
				Check("notWithoutTheHealth10", ot == o && mo.health == 10);
				mo.health = mo.player.health = 100;
			}
			if (o == wfT + 10) Go(mo, 5040, 60, 0, 180);      // into the hall, by its plates
			// on from the hall, while nothing is awake: to two seconds before the end, and no further
			// (before wave 2 is due: a monster of it that did not come in the last go comes now, real)
			if (o == wfT + 14)
			{
				Console.Printf("AJARTEST info in the hall: at=%d awake=%d demoing=%d", at, Awake(), Demoing());
				wfSpot = mo.pos;
				Wind32(3, 0, true).Used(mo);
				wfT3 = ot;
				Console.Printf("AJARTEST info on from %d to %d (the demo is %d long); cage=%.2f", o, ot, demo.len, cage.Opened());
				Check("fromTheHall10", at == 0 && mo.health == 90 && SelfAt(0, wfT3));
				Check("onToTwoSecondsBeforeItsEnd10", wfT3 == demo.len - 70 && o + WIND_TICS > wfT3);
				Check("cageHeldAtOnce10", wfT3 > WF_C0 && wfT3 < WF_C1 && cage.IsOpen() && cp.pressed && SelfAt(0, wfT3));
				Wind32(3, 0, true).Used(mo);
				Check("noFurther10", ot == wfT3 && mo.health == 90);
				wfStep = 4;
			}
		}
		if (wfStep == 4 && fight == 3 && open && g == 2)
		{
			if (o > wfT3 && o < wfT3 + 20) mo.vel.xy = (0, 0);
			if (o == wfT3 + 5) Hurt(mo, 1, 20);
			if (o == wfT3 + 10)
			{
				Wind32(3, 0, false).Used(mo);
				Check("notFromTheHallOnceAwake10", ot == o && Awake() && mo.health == 90);
			}
			// what is done after: on the screen's plate (the first self is on the cage's), out by door 2
			if (o >= wfT3 + 20 && o < wfT3 + 40) Go(mo, 5768, 1216, 0, 90);
			if (o == wfT3 + 50) Go(mo, 6500, 720, 0, 0);
			if (o > wfT3 + 50) Walk(mo, (8, 0));
		}
		if (wfStep == 4 && fight == 3 && open && g == 3) { wfStep = 5; wfLen2 = takes[1].x.Size(); }

		// === go 3: the wound go's self ===
		if (wfStep == 5 && fight == 3 && open && g == 3)
		{
			if (o == 2)
			{
				bool still = takes[1].x.Size() > wfT3 + 50;
				for (int i = 0; still && i < wfT3; i++) still = takes[1].x[i] == wfSpot.x && takes[1].y[i] == wfSpot.y && takes[1].z[i] == wfSpot.z;
				Console.Printf("AJARTEST info go 3: the second self's record %d long, wound at %d, the demo %d long", wfLen2, wfT3, demo ? demo.len : -1);
				Check("theWoundGoIsAGo10", still && at == 2 && demo && abs(demo.len - wfLen2) <= 2);
			}
			if (o == wfT3 - 20) Check("standingStillUpToT10", SelfAt(1, o - 1) && ghosts[1].pos.xy == wfSpot.xy && AsTheyWent());
			if (o == wfT3 + 36) Check("thenWhatWasDone10", SelfAt(1, o - 1) && sp.On(ghosts[1]) && sp.pressed && scr.IsShut());
			if (o == wfT3 + 45)
			{
				Check("noParadox10", !paradoxes && !paradox);
				Go(mo, 6950, 176, F32, 0);         // on to room 4's lobby: room 3 is left
				wfStep = 6;
			}
		}

		// === room 4, go 1: both key levers; out by door 1 ===
		if (wfStep == 6 && fight == 4 && open && g == 1)
		{
			if (o == 5) Go(mo, 7040, 1340, F32, 90);
			if (o > 5) mo.vel.xy = (0, 0);
			if (o == WK_W) kw.Used(mo);
			if (o == WK_W + 5) Go(mo, 7872, 1340, F32, 90);
			if (o == WK_E) ke.Used(mo);
			if (o == WK_E + 3) Check("keyedInGo1_10", sh4.keyed > 0 && kw.held && ke.held);
			if (o == WK_OUT) Go(mo, 7240, 432, F32, 180);
			if (o > WK_OUT) Walk(mo, (-8, 0));
		}
		if (wfStep == 6 && fight == 4 && open && g == 2) { wfStep = 7; wfT = 0; }
		if (wfStep == 7 && fight == 4 && open && g == 2)
		{
			if (o == 3) Go(mo, 7288, -112, F32 + 64, 90);
			if (o > 3) mo.vel.xy = (0, 0);
			if (o == WF_W1)
			{
				wfH = mo.health;
				Wind32(4, 1, true).Used(mo);
				int kt = logs[0].kTic.Size() == 2 ? logs[0].kTic[1] : -1, left = kw.Tics() - (ot - kt);
				Console.Printf("AJARTEST info room 4 wound on to %d: keyed=%d (the pull that keyed it at %d: %d left) open=%.2f held=%d/%d",
					ot, sh4.keyed, kt, left, sh4.Opened(), kw.held, ke.held);
				Check("keyedAtOnce10", ot == WF_W1 + WIND_TICS && kt > 0 && abs(sh4.keyed - left) <= 2 && sh4.IsOpen() && kw.held && ke.held
					&& mo.health == wfH - WIND_HEALTH);
				wfT = ot;
			}
			if (wfT && o == wfT + 1) Check("stillKeyed10", sh4.IsOpen() && sh4.keyed > 0 && kw.held && ke.held && SelfAt(0, o - 1));
			if (wfT && o == wfT + 10)
			{
				Wind32(4, 1, false).Used(mo);
				Console.Printf("AJARTEST info room 4 wound back to %d: keyed=%d open=%.2f up=%d/%d", ot, sh4.keyed, sh4.Opened(), kw.Up(), ke.Up());
				Check("notYetPulled10", ot == wfT + 10 - WIND_TICS && kw.Up() && ke.Up() && !sh4.keyed && sh4.IsShut());
				wfStep = 8;
			}
		}
		if (wfStep == 8 && fight == 4 && open && g == 2)
		{
			if (o == WK_W + 1) Check("liveAtItsTic10", kw.Live() && ke.Up() && !sh4.keyed);
			if (o == WK_E + 2)
			{
				Check("keyedAtItsTic10", sh4.keyed > 0 && kw.held && ke.held);
				Check("noParadoxRoom4_10", !paradoxes && !paradox);
				Go(mo, 7456, 900, F32, 90);        // into the range: win it
			}
			if (o > WK_E + 2 && o % 5 == 0) KillAll(mo);
		}
		if (wfStep == 8 && fight == 4 && goes) { wfStep = 9; wfT = t; }
		// === won: the plates say nothing plays ===
		if (wfStep == 9 && t == wfT + 5)
		{
			int h = mo.health, n = takes.Size();
			Wind32(4, 0, true).Used(mo);
			Wind32(4, 1, false).Used(mo);
			Check("nothingPlaysOnceWon10", won.Find(4) < won.Size() && !open && mo.health == h && takes.Size() == n);
			wfStep = 10;
		}
	}
}
