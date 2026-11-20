// MAP32 "Double Shift", rebuilt (tools/map_secret2.py; PLAN.md, "MAP32
// rebuilt"): five rooms in a row, each needing earlier selves. Nothing new in
// the engine is needed for it but a plain frame that takes one door (ajar.zs,
// AjarFrame args[4] 5) and a lamp among the figures (shut.zs). Its tests:
//   MAP=MAP32 MODE=3 tools/smoke.sh   the whole level solved, room by room
//   MAP=MAP32 MODE=4 tools/smoke.sh   the dead ends: out of the pit, out of
//                                     the lock; a door of room 1 refused
//   MAP=MAP32 MODE=2 tools/smoke.sh   views, for screenshots
//   MAP=MAP32 MODE=7 tools/smoke.sh   room 3's plates, screen, cage, sentries and the timetable
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
	Array<Actor> dsPenShots, dsPenOut;
	AjarDoor leafA32, leafB32;
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
		AjarPlate p1 = FloorPlate32(101, 0), p51 = FloorPlate32(141, 0), p52 = FloorPlate32(142, 0), sp = FloorPlate32(0, SHUT32);
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
			Check("begun1", goes && fight == 1 && g == 1 && Figures(false) == 41 && !Figures(true));
			Check("allThere", violet && yellow && green && pink && blue && red && a && b && f1 && fa && fb && fw && g1 && g2 && home && home2
				&& p1 && p51 && p52 && sp && pr && sh && sw && sh3 && Lamp33() && red.frame == home && !h.chainLen);
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
		// the solution: go 1 hangs a at TA32 and goes out by door 1; go 2 hangs b in time,
		// and brings YELLOW up through the Pair
		if (dsStep == 2 && goes && fight == 2 && g == 1)
		{
			if (o == 2) Check("forgotten2", !a.frame && !b.frame && !a.carried && !b.carried && !AllGhosts() && !yellow.frame);
			if (o == 5) { Go(mo, 2100, 230, 0, 90); a.Used(mo); }
			if (o == 7) Go(mo, 2040, 160, 0, 180);
			if (o == TA32) fa.Activate(mo);
			if (o == TA32 + 4) Go(mo, 2480, 280, 0, 90);
			if (o > TA32 + 4 && o < TA32 + 25) Walk(mo, (0, 8));
		}
		if (dsStep == 2 && goes && fight == 2 && g == 2)
		{
			if (o == 3) { Go(mo, 3560, 530, F32, 90); b.Used(mo); }
			if (o == 5) Go(mo, 3696, 600, F32, 90);
			if (o == TA32 + 8) fb.Activate(mo);
			if (o == TA32 + 10)
				Check("joined2", a.frame == fa && b.frame == fb && a.args[0] == 132 && b.args[0] == 131 && AllGhosts() == 1
					&& !(la.flags & Line.ML_BLOCKING) && !(lb.flags & Line.ML_BLOCKING));
			if (o == TA32 + 12) { Go(mo, 3700, -120, F32, 270); yellow.Used(mo); }
			if (o == TA32 + 14) Go(mo, 3696, 600, F32, 90);
			if (o > TA32 + 14 && o < TA32 + 34) Ahead(mo);
			if (o == TA32 + 36)
				Check("yellowUp2", k == 2 && mo.pos.x < 2400 && mo.pos.z > -1 && h.carried == yellow && a.frame == fa && b.frame == fb);
			if (o == TA32 + 38) { Go(mo, 2632, 40, 0, 270); fw.Activate(mo); }
			if (o == TA32 + 40) Check("hungInW2", yellow.frame == fw && !h.carried && !yellow.nailer && !h.wayOutBuilt);
			if (o == TA32 + 42) { Go(mo, 2632, 40, 0, 270); dsOnFrom = 2; }
		}
		// === 3: the press ===
		if (dsStep == 2 && fight == 3)
		{
			Check("on2", k == 3 && won.Find(2) < won.Size() && (h.FindLine(HallLine(2, 1)).flags & Line.ML_BLOCKING)
				&& (h.FindLine(HallLine(2, 2)).flags & Line.ML_BLOCKING) && yellow.frame == fw);
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
			dsStep = 4;
			dsT = t;
		}
		if (dsStep == 4 && t == dsT + 40) { Check("steel3", SteelUp(3)); Go(mo, 6500, 160, 0, 0); dsOnFrom = 3; }
		// === 4: the range ===
		if (dsStep == 4 && fight == 4 && open)
		{
			dsStep = 5;
			dsT = t;
			dsT2 = 0;
		}
		if (dsStep == 5 && t == dsT + 6)
		{
			Console.Printf("AJARTEST info left=%d", Left());
			Check("begun4", phase == LIVE && open && mixed && Left() >= 9 && sh.IsShut());
			Check("noLeak4", Fresh(4));
		}
		if (dsStep == 5 && open && fight == 4)
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor m;
			while (m = Actor(mi.Next()))
			{
				if (!m.bMissile || !m.target || !m.target.bIsMonster) continue;
				if (dsPenShots.Find(m) == dsPenShots.Size()) dsPenShots.Push(m);
				if (m.pos.y < 1390 && dsPenOut.Find(m) == dsPenOut.Size()) dsPenOut.Push(m);
			}
		}
		if (dsStep == 5 && open && g == 1)
		{
			if (o == 3) { Go(mo, 7456, 120, F32, 90); mo.GiveInventory("RocketLauncher", 1); mo.GiveInventory("RocketAmmo", 50); }
			if (o == 5)
			{
				FLineTraceData ld;
				mo.LineTrace(90, 1400, 0, 0, 32, data: ld);
				Check("shutWithoutThePlate4", sh.IsShut() && !sp.pressed && ld.HitType == TRACE_HitWall && ld.HitLocation.y <= 1401 && ld.HitLocation.y > 1390);
			}
			if (o == 10) Go(mo, 7840, 1300, F32, 180);
			if (o == 30) Check("opensWithThePlate4", sp.pressed && sh.IsOpen());
			if (o == 500) { Go(mo, 7840, 1150, F32, 180); mo.health = mo.player.health = 1; }
		}
		if (dsStep == 5 && open && g == 2)
		{
			if (o == 2) Check("killedIntoTheBox4", at == 1 && bx == 1 && mo.health == RESCUE_HEALTH && demo != null && sh.IsShut());
			if (o == 3) { Go(mo, 7456, 120, F32, 90); dsOut0 = dsPenOut.Size(); }
			if (o == 40) Check("heldByMyEarlierSelf4", sh.IsOpen() && sp.pressed && AllGhosts() >= 1 && !sp.On(mo));
			if (o >= 60 && o <= 280 && o % 20 == 0 && sh.IsOpen()) { ShootPen(mo, dsShots * 3); dsShots++; }
			if (o == 290)
			{
				int hurt, dead;
				[hurt, dead] = DemoHurt();
				Console.Printf("AJARTEST info hurt=%d dead=%d shots=%d fired=%d out=%d onDemo=%d awake=%d", hurt, dead, dsShots, dsPenShots.Size(),
					dsPenOut.Size() - dsOut0, Rails(true), Rails(false));
				Check("hurtThroughTheShutter4", hurt > 0);
				Check("theyFireBack4", dsPenOut.Size() > dsOut0);
			}
			if (o > 300 && o % 5 == 0) KillAll(mo);
		}
		if (dsStep == 5 && goes && fight == 4)
		{
			Check("won4", won.Find(4) < won.Size() && !open && !mixed && !Left() && goesWon);
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
			if (o == 5) Go(mo, 8530, 416, G32, 0);
			if (o > 5 && o < 20) Ahead(mo);
			if (o == 80)
			{
				Check("twoEarlierSelves5", AllGhosts() == 2 && p51.pressed && p52.pressed && pink.frame == g2 && green.frame == g1 && h.carried == blue);
				Go(mo, 9218, 416, G32, 0);
			}
			if (o > 80 && o < 95) Ahead(mo);
			if (o == 97) Check("through5b", k == 5 && mo.pos.x > 9600 && mo.pos.x < 10112 && mo.pos.y > 160 && mo.pos.y < 608 && h.carried == blue);
			if (o == 99) { Go(mo, 10080, 384, G32, 0); home2.Activate(mo); }
			if (o == 101) Check("chainClosed5", h.chainLen == 2 && blue.frame == home2 && red.frame == home && !h.carried);
			if (o == 103) Go(mo, 9640, 384, G32, 180);
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
			if (o == 3) Go(mo, 8232, 240, G32, 90);
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
			5768, 250, 0, 90, 0,            // the mouth of the press from the hall
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
			7000, 176, -96, 0, 0,           // room 4 as entered: the range, the case on its far wall
			7580, 150, -96, 15, -10,        // room 4's case, close (south of the pillar before it)
			7456, 120, -96, 90, 0,          // the firing spot: the shutter
			8100, 452, -192, 0, 0,          // room 5 as entered: S, F1 and the case
			8410, 576, -192, 0, -10,        // room 5's case, close
			9856, 172, -192, 90, 0,         // E from PINK's far side, wide: the brass frames face each other
			10040, 384, -192, 180, 0,       // BLUE hung: into RED's frame, the way without end
			9672, 384, -192, 0, 0           // and the other way, into BLUE's
		};
		int WIDE = 27, OPEN3 = 12, SHUT3V = 19;
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
// Go 2 goes up the wing, into the cage while the first self holds it, pulls
// the lever at TT_PULL, out by the window and door 2. Go 3 watches the press
// lamps from box 2, and begins the fight anew.
extend class AjarTimeHandler
{
	const TT_SCR = 160;
	const TT_SCR_OFF = 340;
	const TT_CAGE = 370;
	const TT_CAGE_OFF = 520;
	const TT_OUT1 = 700;
	const TT_PULL = 560;
	int ttStep, ttT, ttOutO, ttLandO, ttUpO, ttPull;
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
			}
			if (o == TT_SCR_OFF) Go(mo, 5768, 1120, 0, 270);
			if (o == TT_SCR_OFF + AjarShutter.TICS + 4)
			{
				int n, demo, after, see;
				[n, demo, after, see] = Pen33(mo, ttMark);
				Console.Printf("AJARTEST info screen up: guards=%d see=%d stopped=%d", n, see, TraceStopped33());
				Check("screenUpAgain3", scr.IsOpen() && !sp.pressed && LampsShow(SCREEN3, AjarLamp.RED) && see > 0 && !TraceStopped33());
			}
			if (o == TT_CAGE) Go(mo, 5096, 1184, 0, 90);
			if (o == TT_CAGE + 90) Check("cageOpensWithItsPlate3", cage.IsOpen() && cp.pressed && LampsShow(CAGE3, AjarLamp.GREEN));
			if (o == TT_CAGE_OFF) Go(mo, 5096, 1080, 0, 0);
			if (o == TT_CAGE_OFF + AjarShutter.TICS + 4) Check("cageShutsAgain3", cage.IsShut() && !cp.pressed && LampsShow(CAGE3, AjarLamp.RED));
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
			if (o == TT_CAGE + AjarShutter.TICS + 5) Go(mo, 5860, -120, 96, 0);
			if (o > TT_CAGE + AjarShutter.TICS + 5 && o <= TT_CAGE + AjarShutter.TICS + 15) Walk(mo, (8, 0));
			if (o > TT_CAGE + AjarShutter.TICS + 15 && o <= TT_CAGE + AjarShutter.TICS + 20) Walk(mo, (0, 8));
			if (o == TT_CAGE + AjarShutter.TICS + 26)
			{
				Console.Printf("AJARTEST info in the cage at (%d,%d,%d) health=%d", mo.pos.x, mo.pos.y, mo.pos.z, mo.health);
				Check("megasphere3", mo.health == 200 && !MegaThere33() && mo.pos.x > 5896);
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
			if (ttMark) ttMark.Destroy();
			ttStep = 4;
		}
	}
}
