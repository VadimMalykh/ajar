// MAP32 "Double Shift", rebuilt (tools/map_secret2.py; PLAN.md, "MAP32
// rebuilt"): five rooms in a row, each needing earlier selves. Nothing new in
// the engine is needed for it but a plain frame that takes one door (ajar.zs,
// AjarFrame args[4] 5) and a lamp among the figures (shut.zs). Its tests:
//   MAP=MAP32 MODE=3 tools/smoke.sh   the whole level solved, room by room
//   MAP=MAP32 MODE=4 tools/smoke.sh   the dead ends: out of the pit, out of
//                                     the lock; a door of room 1 refused
//   MAP=MAP32 MODE=2 tools/smoke.sh   views, for screenshots
// The coordinates are the generator's.

extend class AjarTimeHandler
{
	const PRESS32 = 3530;       // room 3's press (map_secret2.PRESS3)
	const SHUT32 = 3540;        // room 4's shutter (map_secret2.SHUT4)
	const SHUT33 = 3535;        // room 3's booth's shutter (map_secret2.SHUT3)
	const F32 = -96;            // the floor of the pit, of room 4
	const G32 = -192;           // of room 5
	const TA32 = 200;           // when the first self hangs leaf a in room 2
	int dsStep, dsT, dsT2, dsUsed, dsBefore, dsShots, dsOut0;
	int dsOnFrom;               // walking on, ahead, until the fight that is on is another than this
	int dsPlateO, dsStuckT;     // room 3: the tic go 1 stood on the cell's plate; the booth seen shut again
	double dsStuckY;
	int dsCell, dsNearO, dsNearH, dsMinH, dsInCell;     // room 3, go 1 in the cell (without godmode)
	Array<Actor> dsPenShots, dsPenOut;
	AjarDoor leafA32, leafB32;
	Actor dsGhost;              // MODE=2: a self on room 3's plate, for the view of the booth open

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

	// Room 3's cell (map_secret2.CELL3) and its glass (GLASS3, on the chamber's north wall).
	bool InCell32(Actor a) { return a.pos.x > 5672 && a.pos.x < 5928 && a.pos.y > 1296 && a.pos.y < 1392; }
	int MonstersBy32(double near, bool inCell)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			if (inCell) { if (InCell32(a)) n++; continue; }
			double dx = max(5736 - a.pos.x, 0, a.pos.x - 5928), dy = max(1280 - a.pos.y, 0, a.pos.y - 1296);
			if (dx * dx + dy * dy <= near * near) n++;
		}
		return n;
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
		if (dsCell) mo.player.cheats &= ~CF_GODMODE;     // room 3's bait in the cell: hurt as anyone (safeInTheCell3)
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
		AjarPlate sp3 = FloorPlate32(0, SHUT33);
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
				&& p1 && p51 && p52 && sp && pr && sh && sw && sh3 && sp3 && red.frame == home && !h.chainLen);
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
			Check("begun3", phase == LIVE && open && mixed && Left() >= 17 && PressUp(pr) && sh3.IsShut() && !sp3.pressed);
			Check("noLeak3", Fresh(3));
		}
		// go 1: the monsters do not fight each other; alone, the booth is shut and
		// the lever out of reach; then the bait walks through the mouth and the
		// squeeze into the cell and onto its plate, stands there (without
		// godmode) until twelve are under the press or 700 tics, and at least
		// 150 tics after the first monster came within 200 of the glass, and
		// leaves by the cell's time door
		if (dsStep == 3 && open && g == 1)
		{
			if (o == 6) Check("noInfighting3", NoInfighting(3));
			if (o == 8) Go(mo, 5768, 20, 0, 270);
			if (o == 10)
			{
				FLineTraceData ld;
				mo.LineTrace(270, 200, 0, 0, 40, data: ld);
				Console.Printf("AJARTEST info booth: hit=%d at y=%.1f lever=%.1f away", ld.HitType, ld.HitLocation.y, mo.Distance2D(sw));
				Check("boothShutAlone3", sh3.IsShut() && !sp3.pressed && ld.HitType == TRACE_HitWall && ld.HitLocation.y > -17
					&& ld.HitLocation.y < 1 && mo.Distance2D(sw) > 64 + mo.radius && PressUp(pr));
			}
			if (o == 12) Go(mo, 5696, 740, 0, 90);
			if (o > 12 && !dsPlateO)
			{
				if (mo.pos.y < 1336 && o < 300) Walk(mo, (0, 10));
				else if (mo.pos.x < 5870 && o < 300) Walk(mo, (10, 0));
				else
				{
					Console.Printf("AJARTEST info on the plate o=%d from (%d,%d) through the squeeze=%d", o, mo.pos.x, mo.pos.y, InCell32(mo));
					Go(mo, 5880, 1344, 0, 270);
					dsPlateO = o;
					dsCell = 1;
					dsMinH = dsNearH = mo.health;
				}
			}
			if (dsCell && !dsT2)
			{
				int near = MonstersBy32(200, false);
				if (!dsNearO && near) { dsNearO = o; dsNearH = mo.health; Console.Printf("AJARTEST info near the glass o=%d health=%d", o, mo.health); }
				dsMinH = min(dsMinH, mo.health);
				dsInCell += MonstersBy32(0, true);
				if ((dsNearO && o >= dsNearO + 150 && (UnderPress(pr) >= 12 || o >= 700)) || o >= 900)
				{
					dsT2 = o;
					dsCell = 0;
					Console.Printf("AJARTEST info under=%d o=%d near=%d health=%d min=%d inCell=%d", UnderPress(pr), o, near, mo.health, dsMinH, dsInCell);
					Check("safeInTheCell3", dsNearO && o - dsNearO >= 150 && dsMinH >= dsNearH && mo.health == dsNearH && !dsInCell);
				}
			}
			if (dsT2 && o == dsT2 + 2) Go(mo, 5904, 1344, 0, 0);
			if (dsT2 && o > dsT2 + 2 && o < dsT2 + 20) Walk(mo, (8, 0));
		}
		// go 2: the booth stands open while the earlier self holds the plate; in,
		// the lever when the monsters, played as they went, are under the press;
		// put out into the hall when the shutter shuts
		if (dsStep == 3 && open && g == 2)
		{
			if (o == 2) Check("outByTheCellDoor3", at == 1 && bx == 1 && demo != null && !takes[0].died && takes[0].door == HallLine(3, 3));
			if (o == 3) Go(mo, 5768, 40, 0, 270);
			if (o == dsPlateO + 20) Check("boothOpenForMyEarlierSelf3", sh3.IsOpen() && sp3.pressed && AllGhosts() >= 1 && !sp3.On(mo));
			if (o > dsPlateO + 20 && !dsUsed && mo.pos.y > -64) Walk(mo, (0, -8));
			else if (o > dsPlateO + 20 && !dsUsed && mo.pos.x < 5820) Walk(mo, (8, 0));
			if (!dsUsed && o > dsPlateO + 30 && mo.pos.y < -40 && mo.Distance2D(sw) < 64 && Demoing()
				&& (UnderPress(pr, 1) >= 10 || o >= demo.len - AjarPress.WARN - AjarPress.DOWN - 10))
			{
				Console.Printf("AJARTEST info under=%d onDemo=%d len=%d lever=%.1f away", UnderPress(pr, 1), Rails(true), demo.len, mo.Distance2D(sw));
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
			// the earlier self leaves the plate: the shutter shuts, the player is put out and walks on
			if (dsUsed && !dsStuckT && o > dsUsed && sh3.IsShut())
			{
				dsStuckT = o;
				dsStuckY = mo.pos.y;
				Console.Printf("AJARTEST info shut again o=%d at (%d,%d)", o, mo.pos.x, mo.pos.y);
			}
			if (dsStuckT && o > dsStuckT && o < dsStuckT + 8) Walk(mo, (0, 8));
			if (dsStuckT && o == dsStuckT + 10)
				Check("notStuckInTheBooth3", dsStuckY > 0 && mo.pos.y > dsStuckY + 16 && k == 3 && bx == 0 && !sp3.pressed);
			if (dsStuckT && o > dsStuckT + 10 && o > down + 62 && o % 5 == 0) KillAll(mo);
		}
		if (dsStep == 3 && goes && fight == 3)
		{
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
	// for room 3's booth open a self (a bare AjarGhost) stands on the cell's plate.
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
			5768, 760, 0, 90, 0,            // the chamber from the mouth: the cell's glass, the plate behind it, the squeeze
			5696, 1180, 0, 80, 0,           // the cell from just outside the squeeze
			5700, 1320, 0, 5, -5,           // inside the cell: the plate and the time door
			5856, 160, 0, 270, -5,          // the booth shut: the lever through the slit
			5768, 220, 0, 270, 0,           // the booth, open: a self on the cell's plate
			7000, 176, -96, 0, 0,           // room 4 as entered: the range, the case on its far wall
			7580, 150, -96, 15, -10,        // room 4's case, close (south of the pillar before it)
			7456, 120, -96, 90, 0,          // the firing spot: the shutter
			8100, 452, -192, 0, 0,          // room 5 as entered: S, F1 and the case
			8410, 576, -192, 0, -10,        // room 5's case, close
			9856, 172, -192, 90, 0,         // E from PINK's far side, wide: the brass frames face each other
			10040, 384, -192, 180, 0,       // BLUE hung: into RED's frame, the way without end
			9672, 384, -192, 0, 0           // and the other way, into BLUE's
		};
		int WIDE = 20, OPEN3 = 14;
		int i = t / 40;
		if (t == OPEN3 * 40 - 15) dsGhost = Actor.Spawn("AjarGhost", (5880, 1344, 0));
		if (t == OPEN3 * 40 + 39 && dsGhost) { dsGhost.Destroy(); dsGhost = null; }
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
