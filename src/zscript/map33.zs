// The tests of MAP33 "Third Person" (tools/map_station.py; the engine third.zs;
// PLAN.md, "MAP33 "Third Person": the first playable version").
// MAP=MAP33 MODE=n tools/smoke.sh, n:
//  1  the whole level, scripted: three goes, out by the exit door. God mode,
//     and the script kills: in a window hall one monster at a time, the
//     nearest, shot at for six tics and then killed; elsewhere whatever of the
//     go's part comes in sight (or within 320) on the way, one each 4 tics.
//     Checks the gate, the doors, the future seen, the halls played in step,
//     the plates and the exit; go 3 through the cooling pond and the cooling
//     tower (window hall 5: its exit shut while anything lives in it); the wind
//     plate told of once in go 2 and not in go 1; measures the halls' cost and
//     the records' sizes.
//  2  go 2 too slow (it stays in box 2): the gantry paradox when the first
//     self comes onto it; then USE (smoke_MAP33_2.cfg): go 2's start loaded.
//  3  as 1, with views: two dozen places where a player would stand, each held
//     70 tics and named in the log; smoke_MAP33_3.cfg shoots in the middle of
//     each (its waits are the views' tics t + 35, from a run's log: a change to
//     the script before a view moves them, and runs differ by up to about 25
//     tics). (LevelLocals.MakeScreenShot made no file.)
// The parts are told apart by the sectors' user_part (map_station.py).

extend class AjarTimeHandler
{
	// the map's numbers (map_station.py)
	const M33_GATE = 3351;
	const M33_GSHUT = 3352;
	const M33_STEEL = 3353;
	const M33_GANTRY_TAG = 3346;
	const M33_TSHUT = 3357;     // the cooling tower's exit (window hall 5's win opens it)
	const M33_TF = -64;         // the tower's floor
	// the script's clock: go 1 waits at the foot of the gantry until M33_GANTRY
	// (go 2 has won R by then), holds plate 1 until M33_LEAVE1, go 2 plate 2
	// until M33_LEAVE2 (go 3 is through the exit door by then)
	const M33_GANTRY = 2100;
	const M33_LEAVE1 = 3000;
	const M33_LEAVE2 = 2900;

	int m3T, m3Step, m3Go, m3Mark, m3From, m3AimAt, m3Killed;
	int m3Route, m3Ix, m3Prog;
	double m3BestD;
	Actor m3Aim;
	bool m3Done, m3Shots, m3GateBad, m3GateSeen, m3Through, m3ExitSeen, m3DoorSeen;
	bool m3TowerBad, m3TowerSeen, m3WindBad, m3WindLogged;
	int m3Pdx, m3RFrom, m3RTo, m3PlateAt;
	Array<bool> m3PostSeen;
	// a view: held m3Hold tics, then back to where the script was
	int m3Hold, m3Views, m3Once;
	double m3BackX, m3BackY, m3BackZ, m3BackA, m3VX, m3VY, m3VZ, m3VA, m3VP;
	// measures: by group, the halls' ms a tic and the whole tic's (wall clock between tics)
	Array<double> m3HSum, m3HWorst, m3FSum, m3FWorst;
	Array<int> m3N;
	double m3Last;

	// --- the route ------------------------------------------------------------------
	// Routes as pairs of x, y; each ends at the first -1, -1 (routes are numbered in order).
	static const double M33R[] = {
		/* 0 S to the coal yard's mouth */        384, 2660,  600, 2900,  640, 3040,  512, 3150,  512, 3500,  512, 3790,  -1, -1,
		/* 1 across the yard, the gate */          900, 3790,  1860, 3790,  1860, 4416,  2000, 4416,  2110, 4416,  2110, 4100,  -1, -1,
		/* 2 to BLUE */                            2110, 4000,  3000, 3900,  3330, 3880,  -1, -1,
		/* 3 to frame 101 */                       3000, 4100,  2288, 4120,  2288, 4170,  -1, -1,
		/* 4 the catwalk, the pump room, the stack court, the foot of the gantry */
		                                          2272, 4930,  3560, 4900,  3650, 4896,  3650, 4672,  4600, 4672,  4880, 4672,  5000, 4600,  5230, 4450,  5240, 4000,  5200, 3800,  4992, 3700,  4992, 3450,  -1, -1,
		/* 5 onto the gantry */                    4992, 3330,  5100, 3330,  6000, 3330,  -1, -1,
		/* 6 along it to E1, plate 1 */            7000, 3330,  7240, 3330,  7500, 3330,  7808, 3328,  -1, -1,
		/* 7 through time door 1 */                8000, 3328,  8150, 3328,  -1, -1,
		/* 8 box 2, the gallery, the workshop */   576, 2430,  700, 2430,  960, 2430,  960, 3600,  3776, 3600,  3776, 3160,  2816, 3160,  2816, 3000,  -1, -1,
		/* 9 to VIOLET */                          3700, 3000,  3700, 2280,  -1, -1,
		/* 10 to frame 102 */                      3700, 2920,  2750, 2920,  2750, 2784,  -1, -1,
		/* 11 the armoury: the plasma rifle */     2560, 2368,  2420, 2368,  -1, -1,
		/* 12 the pump hall, the stores, the mezzanine, down into R */
		                                          2760, 2880,  3800, 2880,  3870, 2880,  4000, 2880,  4352, 2880,  4352, 2600,  4352, 2520,  4700, 2520,  4700, 2368,  4800, 2368,  4960, 2368,  5150, 2400,  -1, -1,
		/* 13 the steel door, E2, plate 2 */       5150, 2848,  6900, 2848,  7000, 2880,  7100, 2880,  7350, 2880,  7600, 2880,  7808, 2880,  -1, -1,
		/* 14 through time door 2 */               8000, 2880,  8150, 2880,  -1, -1,
		/* 15 box 3, the cable tunnel, PINK */     192, 2400,  192, 2280,  192, 2050,  1270, 2050,  1350, 2040,  1400, 1880,  -1, -1,
		/* 16 to frame 103 */                      1450, 1720,  2560, 1720,  2600, 1560,  2760, 1440,  -1, -1,
		/* 17 the relay room's south door, the steps, the pond */
		                                          3100, 1920,  3488, 1920,  3488, 1810,  3488, 1740,  3488, 1680,  -1, -1,
		/* 18 through the water to the outfall */  3700, 1520,  4000, 1400,  4300, 1040,  4400, 1024,  4470, 1024,  -1, -1,
		/* 19 the drop into the tower */           4560, 1024,  4640, 1024,  -1, -1,
		/* 20 the tower's exit, the passage, the steps down, the duct */
		                                          4700, 1150,  4850, 1300,  4830, 1480,  4800, 1580,  4800, 1700,  4800, 1920,  4950, 1920,  5070, 1920,  5700, 1950,  -1, -1,
		/* 21 along the duct, up to E3 */          7000, 1950,  7550, 1920,  7550, 2270,  7550, 2400,  -1, -1,
		/* 22 through the exit door */             7900, 2528,  8040, 2528,  8150, 2528,  8250, 2528,  -1, -1
	};

	int RouteBase(int n)
	{
		int i = 0;
		for (int k = 0; k < n; k++)
		{
			while (M33R[i] >= 0 || M33R[i + 1] >= 0) i += 2;
			i += 2;
		}
		return i;
	}

	// Walks route n; true once at its end. A walk that gets no nearer for three seconds is said in the log.
	bool Walk33(PlayerPawn mo, int n, double speed = 16)
	{
		if (m3Route != n) { m3Route = n; m3Ix = 0; m3Prog = ot; m3BestD = 1e9; }
		int i = RouteBase(n) + 2 * m3Ix;
		if (M33R[i] < 0 && M33R[i + 1] < 0) { mo.vel.xy = (0, 0); return true; }
		Vector2 p = (M33R[i], M33R[i + 1]);
		double d = (p - mo.pos.xy).Length();
		if (d < m3BestD - 1) { m3BestD = d; m3Prog = ot; }
		else if (ot - m3Prog == 105)
			Console.Printf("AJARTEST info stuck: route %d point %d at (%d,%d,%d), to (%d,%d); go %d ot %d",
				n, m3Ix, mo.pos.x, mo.pos.y, mo.pos.z, p.x, p.y, tgo, ot);
		if (Toward(mo, p, speed)) { m3Ix++; m3BestD = 1e9; m3Prog = ot; }
		return false;
	}

	int PartAt(Vector2 p)
	{
		return level.GetUDMFInt(LevelLocals.UDMF_Sector, level.PointInSector(p).Index(), "user_part");
	}

	// Whatever of this go's part, not in a window hall, comes in sight or within 320: one killed each 4 tics.
	void Clear33(PlayerPawn mo)
	{
		if (ot % 4) return;
		let it = ThinkerIterator.Create("Actor");
		Actor a, best;
		double bd = 1400;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || a.bInvisible || HallAt(a.pos.xy) >= 0 || PartAt(a.pos.xy) != tgo) continue;
			double d = a.Distance2D(mo);
			if (d < bd && (d < 320 || mo.CheckSight(a))) { bd = d; best = a; }
		}
		if (!best) return;
		mo.A_StartSound("weapons/sshotf", CHAN_WEAPON);
		best.DamageMobj(mo, mo, 10000, 'None');
		m3Killed++;
	}

	// A window hall's fight: the nearest monster in it faced, shot at for six tics, then killed; what
	// it holds noted every 60 tics (`snap`: the later goes check it is played so). True once none lives.
	bool Fight33(PlayerPawn mo, int h, bool snap)
	{
		int o = ot;
		if (snap && (o - m3From) % 60 == 30) Snap3(h);
		if (!m3Aim || m3Aim.health <= 0 || m3Aim.bInvisible)
		{
			m3Aim = LiveIn(mo, h);
			m3AimAt = o;
			if (!m3Aim) { mo.pitch = 0; return !HallLives(h); }     // (not while a pain elemental is dying: its lost souls are to come)
		}
		Face(mo, m3Aim);
		mo.vel.xy = (0, 0);
		if ((o - m3AimAt) % 3 == 0) { mo.LineAttack(mo.angle, 4096, mo.pitch, 10, 'Hitscan', "BulletPuff"); mo.A_StartSound("weapons/chngun", CHAN_WEAPON); }
		if (o - m3AimAt >= 6) { m3Aim.DamageMobj(mo, mo, 10000, 'None'); m3Killed++; }
		return false;
	}

	// A view for a screenshot (mode 3): the player put at (x, y), turned, held 70 tics (the world goes
	// on; the cfg shoots at the 35th); then back where the script had it.
	void View33(PlayerPawn mo, string what, double x, double y, double ang, double pitch = 0)
	{
		if (!m3Shots) return;
		m3Views++;
		Console.Printf("AJARTEST info view %d: %s (go %d, ot %d, t %d)", m3Views, what, tgo, ot, m3T);
		m3BackX = mo.pos.x; m3BackY = mo.pos.y; m3BackZ = mo.pos.z; m3BackA = mo.angle;
		m3VX = x; m3VY = y; m3VZ = level.PointInSector((x, y)).floorplane.ZAtPoint((x, y)); m3VA = ang; m3VP = pitch;
		m3Hold = 70;
		HoldView33(mo);
	}

	// Kept at the view, whatever pushed or turned it (a shot's thrust, the rest of the script's tic)
	void HoldView33(PlayerPawn mo)
	{
		if (mo.pos != (m3VX, m3VY, m3VZ)) mo.SetOrigin((m3VX, m3VY, m3VZ), false);
		mo.vel = (0, 0, 0);
		mo.angle = m3VA;
		mo.pitch = m3VP;
	}

	// true the first time it is asked for view k (k < 31)
	bool Once33(int k)
	{
		if (m3Once & (1 << k)) return false;
		m3Once |= 1 << k;
		return true;
	}

	bool Hold33(PlayerPawn mo)
	{
		if (m3Hold <= 0) return false;
		m3Hold--;
		HoldView33(mo);
		if (!m3Hold)
		{
			mo.SetOrigin((m3BackX, m3BackY, m3BackZ), false);
			mo.angle = m3BackA;
			mo.pitch = 0;
		}
		return true;
	}

	// --- measures ---------------------------------------------------------------------
	// groups: 0..2 go 1..3 whole; 3 the yard's fight (go 1, recording); 4 R's fight (go 2: R and the
	// workshop recorded, the yard and the boiler house played); 5 go 3 while R is played
	void Measure33(int g, double hall, double frame)
	{
		while (m3N.Size() <= g) { m3N.Push(0); m3HSum.Push(0); m3HWorst.Push(0); m3FSum.Push(0); m3FWorst.Push(0); }
		m3N[g]++;
		m3HSum[g] += hall; m3HWorst[g] = max(m3HWorst[g], hall);
		m3FSum[g] += frame; m3FWorst[g] = max(m3FWorst[g], frame);
	}

	void Report33(int g, string what)
	{
		if (g >= m3N.Size() || !m3N[g]) return;
		Console.Printf("AJARTEST info measure %s: halls %.3f ms a tic (worst %.3f); the whole tic %.2f ms (worst %.2f); over %d tics",
			what, m3HSum[g] / m3N[g], m3HWorst[g], m3FSum[g] / m3N[g], m3FWorst[g], m3N[g]);
	}

	static int TakeBytes(AjarTake t) { return t.x.Size() * (5 * 8 + 4) + t.evTic.Size() * 32; }
	static int TrackBytes(AjarTrack t) { return t ? t.first.Size() * 4 + t.slot.Size() * (2 * 4 + 4 * 8) : 0; }

	void Sizes33(string when)
	{
		for (int i = 0; i < takes.Size(); i++)
			Console.Printf("AJARTEST info size %s: go %d's record %d tics, %d bytes", when, i + 1, takes[i].x.Size(), TakeBytes(takes[i]));
		for (int h = 0; h < halls.Size(); h++)
			if (hTrack[h])
				Console.Printf("AJARTEST info size %s: hall %d's track %d tics, %d records, %d bytes", when, halls[h].args[0],
					hTrack[h].first.Size(), hTrack[h].slot.Size(), TrackBytes(hTrack[h]));
		Console.Printf("AJARTEST info size %s: %d classes in the slots", when, slotCls.Size());
	}

	// --- the checks every tic -----------------------------------------------------------
	static const string HALL33[] = { "", "yard", "workshop", "r", "boiler", "tower" };

	// A window hall of an earlier part, at a tic its own go noted it: the same, as puppets; its real things unseen.
	void SnapChecks33()
	{
		if (paradox || !tgo) return;
		for (int h = 0; h < halls.Size(); h++)
		{
			if (halls[h].args[1] >= tgo) continue;
			for (int s = 0; s < snT.Size(); s++)
				if (snH[s] == h && snT[s] == ot)
				{
					string n = HALL33[clamp(halls[h].args[0], 0, 5)];
					Check(n .. "AsItWas", SameAsSnap(h));
					Check(n .. "RealUnseen", HallThings(h, true) == 0);
					break;
				}
		}
	}

	// A door an earlier self hung: hung again at the tic it did.
	void HungAgain33()
	{
		for (int i = 0; i + 1 < tgo && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			for (int e = 0; e < lg.tic.Size(); e++)
			{
				if (!lg.frm[e] || lg.tic[e] != ot) continue;
				AjarDoor d = null;
				let it = ThinkerIterator.Create("AjarDoor");
				AjarDoor q;
				while (q = AjarDoor(it.Next())) if (q.frame == lg.frm[e]) d = q;
				Check(String.Format("hungAgain%d", lg.frm[e].args[0]), d && !d.carried && SelfAsRecord(i));
				Console.Printf("AJARTEST info %s hung again in frame %d at %d of go %d", d ? d.Label() : "nothing", lg.frm[e].args[0], ot, tgo);
			}
		}
	}

	int Bodies33()
	{
		int n = 0;
		for (int i = 0; i < postIs.Size(); i++) if (postIs[i] is "AjarFigure") n++;
		return n;
	}

	int WantBodies33()
	{
		int n = 0;
		for (int i = 0; i < posts.Size(); i++) if (LeavesBody(AjarHandler.AmbushClass(posts[i].args[1]))) n++;
		return n;
	}

	bool PostsIdle33()
	{
		for (int i = 0; i < postIs.Size(); i++)
		{
			Actor m = postIs[i];
			if (!m || !m.bIsMonster || m.health <= 0 || m.target || !m.bAmbush) return false;
		}
		return postIs.Size() > 0;
	}

	// --- the tic ---------------------------------------------------------------------------
	void Map33Tests(PlayerPawn mo, int mode)
	{
		if (level.totaltime > level.maptime + 10)
		{
			// the exit ends the level and it begins again (next = MAP33): the test is over
			if (!m3Done) { m3Done = true; Check("levelEnded", true); Console.Printf("AJARTEST info the level began again (out by the exit)"); }
			return;
		}
		int t = m3T++;
		double now = MSTimeF();
		double frame = m3Last > 0 ? now - m3Last : 0;
		m3Last = now;
		mo.player.cheats |= CF_GODMODE;
		if (paradox) mo.player.cheats &= ~CF_GODMODE;
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) go=%d ot=%d step=%d selves=%d puppets=%d frozen=%d won=%d,%d,%d,%d td=%d exit=%d p1=%d p2=%d killed=%d health=%d loads=%d",
				t, mo.pos.x, mo.pos.y, mo.pos.z, tgo, ot, m3Step, Selves3(), puppets.Size(), tfz.Size(),
				wonTic.Size() > 0 ? wonTic[0] : -9, wonTic.Size() > 1 ? wonTic[1] : -9, wonTic.Size() > 2 ? wonTic[2] : -9, wonTic.Size() > 3 ? wonTic[3] : -9,
				tdOpen, exitDoor && exitDoor.IsOpen(), plates.Size() > 0 && plates[0].pressed, plates.Size() > 1 && plates[1].pressed, m3Killed, mo.health, thirdLoads);
		if (mode == 2) { Map33Paradox(mo, t); return; }
		m3Shots = mode == 3;
		if (paradox) { if (!m3Pdx) { m3Pdx = t; Check("noParadox", false); Console.Printf("AJARTEST info paradox: %s", paradoxWhy); } return; }
		// measures (not while a view is held)
		if (m3Hold <= 0 && t > 0 && tgo >= 1)
		{
			Measure33(tgo - 1, hallMs, frame);
			if (tgo == 1 && m3Step == 1) Measure33(3, hallMs, frame);
			if (tgo == 2 && m3Step == 7) Measure33(4, hallMs, frame);
			int r = HallIx(3);
			if (tgo == 3 && r >= 0 && hTrack[r] && ot < hTrack[r].first.Size()) Measure33(5, hallMs, frame);
		}
		if (m3Go != tgo)
		{
			if (m3Go == 1) { Report33(0, "go 1"); Report33(3, "the coal yard's fight (go 1: the yard and the boiler house recorded)"); }
			if (m3Go == 2) { Report33(1, "go 2"); Report33(4, "R's fight (go 2: R and the workshop recorded, the yard and the boiler house played)"); }
			if (tgo >= 2) Sizes33(String.Format("at go %d's start", tgo));
			m3Go = tgo;
			m3Step = 0;
			m3Route = -1;
			m3Aim = null;
			Console.Printf("AJARTEST info go %d: god mode; the script kills (hall fights: shot at six tics, then killed; elsewhere what comes in sight)", tgo);
		}
		SnapChecks33();
		HungAgain33();
		if (tgo == 1) Checks33One(mo);
		else if (tgo == 2) Checks33Two(mo);
		else if (tgo == 3) Checks33Three(mo);
		if (Hold33(mo)) return;
		if (tgo == 1) Go33One(mo);
		else if (tgo == 2) Go33Two(mo, false);
		else if (tgo == 3) Go33Three(mo);
	}

	// --- go 1 ------------------------------------------------------------------------------
	void Checks33One(PlayerPawn mo)
	{
		int o = ot;
		int yard = HallIx(1), r = HallIx(3);
		if (o == 2)
		{
			Check("goOneBegun", tgo == 1 && parts == 3 && plates.Size() == 2 && halls.Size() == 5 && exitDoor && !Selves3());
			Console.Printf("AJARTEST info posts %d, bodies %d (of %d that leave one), monsters in the level %d", posts.Size(), Bodies33(), WantBodies33(), level.total_monsters);
			// the future seen: a body at each post that leaves one, nothing alive in R, its shutters open
			Check("bodiesInR", posts.Size() >= 14 && Bodies33() == WantBodies33() && !HallLives(r) && Open3(M33_GSHUT) && Open3(M33_STEEL));
			Check("gateShutAtTheStart", Shut3(M33_GATE) && HallLives(yard));
			Check("towerOpenBeforeItsGo", Open3(M33_TSHUT) && halls.Size() == 5);
		}
		if (windSays) m3WindBad = true;         // (the wind plate is not told of in go 1)
		// the gate: shut while anything lives in the yard
		if (o > 2 && wonTic[yard] < 0)
		{
			m3GateSeen = true;
			if (!Shut3(M33_GATE) || !HallLives(yard)) m3GateBad = true;
		}
		// the bodies, from the gantry: each in sight from some place on it
		if (SecTagged(mo.pos.xy, M33_GANTRY_TAG))
		{
			while (m3PostSeen.Size() < postIs.Size()) m3PostSeen.Push(false);
			for (int i = 0; i < postIs.Size(); i++) if (postIs[i] is "AjarFigure" && mo.CheckSight(postIs[i], SF_IGNOREVISIBILITY)) m3PostSeen[i] = true;
		}
	}

	void Go33One(PlayerPawn mo)
	{
		int o = ot;
		int yard = HallIx(1), boil = HallIx(4), r = HallIx(3);
		let h = Doors();
		AjarDoor blue = Door32(2);
		if (m3Step == 0)
		{
			if (Once33(1)) View33(mo, "S, the gatehouse: the start", 384, 2600, 90, 4);
			else if (Once33(2)) View33(mo, "S: the case of three on its west wall", 260, 2912, 180, 4);
			else if (Walk33(mo, 0))
			{
				m3Step = 1; m3From = o;
				View33(mo, "the coal yard from its mouth: the fight to come", 512, 3780, 50, 2);
			}
			if (m3Step == 0) Clear33(mo);
		}
		if (m3Step == 1 && Fight33(mo, yard, true)) { m3Step = 2; m3Mark = o; Console.Printf("AJARTEST info the yard's fight: %d to %d", m3From, o); }
		if (m3Step == 2)
		{
			if (wonTic[yard] < 0 || o < wonTic[yard] + 40) return;
			Check("gateShutUntilTheYardIsClear", m3GateSeen && !m3GateBad);
			Check("gateOpensWhenClear", Open3(M33_GATE) && !HallLives(yard));
			m3Step = 3;
			View33(mo, "the coal yard after its fight: the heaps, the bowed bunker wall, the west bank", 1800, 3800, 160, 2);
		}
		if (m3Step == 3 && Walk33(mo, 1))
		{
			m3Step = 4; m3From = o;
			View33(mo, "the boiler house: the boilers, the catwalk", 2120, 3760, 45, -4);
		}
		if (m3Step == 4 && Fight33(mo, boil, true)) { m3Step = 5; Console.Printf("AJARTEST info the boiler house's fight: %d to %d", m3From, o); }
		if (m3Step == 5 && Walk33(mo, 2)) { blue.Used(mo); Check("blueTaken", h.carried == blue); m3Step = 6; }
		if (m3Step == 6 && Walk33(mo, 3))
		{
			h.FindFrame(101).Activate(mo);
			Check("blueHung", blue.frame == h.FindFrame(101) && !h.carried);
			m3Step = 7; m3Mark = o;
		}
		if (m3Step == 7)
		{
			if (o == m3Mark + 1) View33(mo, "BLUE hung in the first boiler's face", 2288, 3950, 90, 6);
			Toward(mo, (2288, 4320), 8);
			if (mo.pos.y > 4800)
			{
				Console.Printf("AJARTEST info through BLUE: at (%d,%d,%d), floor %d, part %d, boiler house tag %d", mo.pos.x, mo.pos.y, mo.pos.z,
					mo.floorz, PartAt(mo.pos.xy), SecTagged(mo.pos.xy, 3344));
				Check("catwalkReached", mo.floorz == 128 && PartAt(mo.pos.xy) == 1);
				m3Step = 8;
				View33(mo, "the catwalk, back west to BLUE's far side", 3400, 4900, 180, 2);
			}
		}
		if (m3Step == 8)
		{
			Clear33(mo);
			if (Walk33(mo, 4)) m3Step = 9;
			if (m3Route == 4 && m3Ix == 3 && Once33(3)) View33(mo, "the pump room", 3660, 4920, 315, 2);
			if (m3Route == 4 && m3Ix == 7 && Once33(4)) View33(mo, "the stack court: the chimney's foot", 4950, 4650, 315, -6);
			if (m3Route == 4 && m3Ix == 10 && Once33(11)) View33(mo, "the stack court from the south: the imps' ledge round the north-east", 5300, 3800, 45, -4);
		}
		if (m3Step == 9)
		{
			Clear33(mo);
			if (o == M33_GANTRY - 1) Console.Printf("AJARTEST info go 1 at the foot of the gantry, waiting: R won in go 2 at %d", -1);
			if (o >= M33_GANTRY) m3Step = 10;
		}
		if (m3Step == 10 && Walk33(mo, 5)) { m3Step = 11; m3Mark = o; }
		if (m3Step == 11)
		{
			if (o == m3Mark + 1) Look(mo, mo.pos.xy, 270, 24);
			if (o == m3Mark + 6)
			{
				Check("gantryOverBodies", SecTagged(mo.pos.xy, M33_GANTRY_TAG) && mo.pos.z == 0 && !HallLives(r) && Bodies33() == WantBodies33()
					&& Open3(M33_GSHUT));
				View33(mo, "R from the gantry (go 1): the bodies at the posts", 5600, 3330, 300, 22);
			}
			if (o >= m3Mark + 8 && Walk33(mo, 6))
			{
				int seen = 0, want = 0;
				for (int i = 0; i < postIs.Size(); i++)
					if (postIs[i] is "AjarFigure") { want++; if (i < m3PostSeen.Size() && m3PostSeen[i]) seen++; }
				Console.Printf("AJARTEST info bodies seen from the gantry: %d of %d", seen, want);
				Check("everyBodySeenFromTheGantry", want > 0 && seen == want);
				m3Step = 12; m3Mark = o;
			}
		}
		if (m3Step == 12)
		{
			if (o == m3Mark + 2) Check("plateOneOpensTimeDoorOne", plates[0].mine && tdOpen);
			if (o == m3Mark + 4) View33(mo, "E1: plate 1, and E2 through the glass", 7520, 3420, 300, 0);
			if (o >= M33_LEAVE1) { m3Step = 13; Console.Printf("AJARTEST info go 1 on plate 1 from %d to %d", m3Mark, o); }
		}
		if (m3Step == 13) Walk33(mo, 7);
	}

	// --- go 2 ------------------------------------------------------------------------------
	void Checks33Two(PlayerPawn mo)
	{
		int o = ot;
		int yard = HallIx(1), boil = HallIx(4), r = HallIx(3);
		if (o == 0) Check("boxTwo", tgo == 2 && BoxOf(mo) == 2 && takes.Size() == 2);
		if (o == 0) Check("noWindLineInGoOne", !m3WindBad);
		if (windSays && !m3WindLogged)
		{
			m3WindLogged = true;
			int who;
			int next = ThirdWindNext(who);
			Console.Printf("AJARTEST info the wind plate told of at %d of go 2 (the player at (%d,%d)); the next step onto a plate at %d: \"%s\"",
				windSaid, mo.pos.x, mo.pos.y, next, Doors().said);
			Check("windLineSaidInGoTwo", windSays == 1 && windSaid == o && next - o > 350 && Doors().said.IndexOf("winds the clock on") >= 0);
		}
		if (o == 1)
		{
			Check("rAliveAndIdle", PostsLiving() == posts.Size() && PostsIdle33() && !Bodies33() && Shut3(M33_GSHUT) && Shut3(M33_STEEL) && !tdOpen);
			Check("firstSelf", Selves3() == 1 && SelfAsRecord(0));
			Check("yardHidden", HallThings(yard, true) == 0 && HallThings(yard, false) > 0 && HallPuppets(yard) > 0);
			Check("blueAsAtTheStart", !Door32(2).frame && !Door32(2).carried);
		}
		// the gate as the yard was won in go 1
		if (wonTic[yard] > 0 && o == wonTic[yard] - 1) Check("gateShutBeforeTheYardWasWon", Shut3(M33_GATE));
		if (wonTic[yard] >= 0 && o == wonTic[yard] + 40) Check("gateOpenAsTheYardWasWon", Open3(M33_GATE));
		if (r >= 0 && wonTic[r] >= 0 && o == wonTic[r] + 20)
		{
			Check("rWonOpensTheSteelDoorAndTheGantry", Open3(M33_STEEL) && Open3(M33_GSHUT) && !HallLives(r));
			Console.Printf("AJARTEST info R won at %d of go 2; the first self comes onto the gantry at %d", wonTic[r], watchTic.Size() ? watchTic[0] : -1);
			Check("rWonBeforeTheFirstSelfComes", watchTic.Size() == 1 && watchTic[0] > wonTic[r]);
		}
		if (tdOpen && !m3DoorSeen)
		{
			m3DoorSeen = true;
			Check("doorOpensWithBoth", exitOpened && plates[0].pressed && !plates[0].mine && plates[1].mine);
		}
	}

	void Go33Two(PlayerPawn mo, bool slow)
	{
		int o = ot;
		int work = HallIx(2), r = HallIx(3);
		let h = Doors();
		AjarDoor violet = Door32(5);
		if (slow) { mo.vel.xy = (0, 0); return; }
		if (m3Step == 0)
		{
			if (o >= 20 && Once33(5)) View33(mo, "box 2: S through the glass, the first self setting off", 576, 2420, 90, 0);
			if (o > 26)
			{
				Clear33(mo);
				if (Walk33(mo, 8)) { m3Step = 1; m3From = o; View33(mo, "the workshop from its door: the fight to come", 2816, 3040, 300, 0); }
				if (m3Route == 8 && m3Ix == 4 && Once33(6)) View33(mo, "the gallery: the coal yard's fight through the glass (played)", 1150, 3560, 60, 0);
			}
		}
		if (m3Step == 1 && Fight33(mo, work, true)) { m3Step = 2; Console.Printf("AJARTEST info the workshop's fight: %d to %d", m3From, o); }
		if (m3Step == 2 && Walk33(mo, 9)) { violet.Used(mo); Check("violetTaken", h.carried == violet); m3Step = 3; }
		if (m3Step == 3 && Walk33(mo, 10))
		{
			h.FindFrame(102).Activate(mo);
			Check("violetHung", violet.frame == h.FindFrame(102) && !h.carried);
			m3Step = 4;
		}
		if (m3Step == 4)
		{
			Toward(mo, (2560, 2784), 8);
			if (mo.pos.x < 2500) { Check("armouryReached", mo.pos.y > 2240 && mo.pos.y < 2496 && PartAt(mo.pos.xy) == 2); m3Step = 5; View33(mo, "the armoury, through VIOLET", 2400, 2300, 20, 0); }
		}
		if (m3Step == 5 && Walk33(mo, 11)) { m3Step = 6; Check("plasmaRifle", mo.CountInv("PlasmaRifle") > 0); }
		if (m3Step == 6)
		{
			Toward(mo, (2300, 2368), 8);
			if (mo.pos.x > 2600) { m3Step = 7; m3Route = -1; }
		}
		if (m3Step == 7)
		{
			Clear33(mo);
			if (m3Route == 12 && m3Ix == 4 && Once33(7)) View33(mo, "the pump hall", 3990, 2880, 0, 0);
			if (m3Route == 12 && m3Ix == 8 && Once33(8)) View33(mo, "the stores, the clerk's nook in the far corner", 4700, 2200, 182, 0);
			if (Walk33(mo, 12)) { m3Step = 8; m3RFrom = o; m3From = o; View33(mo, "R from its floor (go 2): every post's monster, idle", 5120, 2380, 40, 6); }
		}
		if (m3Step == 8)
		{
			if (mo.pos.z > -124) return;
			if (Fight33(mo, r, true)) { m3Step = 9; m3RTo = o; Console.Printf("AJARTEST info R's fight: %d to %d", m3RFrom, o); }
		}
		if (m3Step == 9)
		{
			if (wonTic[r] < 0 || o < wonTic[r] + 20) return;
			if (Walk33(mo, 13)) { m3Step = 10; m3PlateAt = o; }
		}
		if (m3Step == 10)
		{
			if (o == m3PlateAt + 4) View33(mo, "E2: the first self on plate 1, through the glass", 7700, 2960, 80, 0);
			if (o >= M33_LEAVE2 && tdOpen)
			{
				m3Step = 11;
				Console.Printf("AJARTEST info go 2 on plate 2 from %d to %d", m3PlateAt, o);
				Check("windLineSaidOnceInGoTwo", windSays == 1);
			}
		}
		if (m3Step == 11) Walk33(mo, 14);
	}

	// --- go 3 ------------------------------------------------------------------------------
	void Checks33Three(PlayerPawn mo)
	{
		int o = ot;
		int work = HallIx(2), r = HallIx(3), yard = HallIx(1);
		if (o == 0) Check("boxThree", tgo == 3 && BoxOf(mo) == 3 && takes.Size() == 3);
		if (o == 2)
		{
			Check("twoSelves", Selves3() == 2 && SelfAsRecord(0) && SelfAsRecord(1));
			Check("rPlayedFromItsStart", HallPuppets(r) >= posts.Size() && HallThings(r, true) == 0 && Shut3(M33_STEEL) && Shut3(M33_GSHUT));
			Check("workshopPlayed", HallPuppets(work) > 0 && HallThings(work, true) == 0);
			Check("pinkAsAtTheStart", !Door32(6).frame);
		}
		if (wonTic[r] > 0 && o == wonTic[r] - 1) Check("shuttersShutBeforeRWasWon", Shut3(M33_STEEL) && Shut3(M33_GSHUT));
		if (wonTic[r] >= 0 && o == wonTic[r] + 13) Check("shuttersOpenAsRWasWon", Open3(M33_STEEL) && Open3(M33_GSHUT));
		if (wonTic[yard] >= 0 && o == wonTic[yard] + 40) Check("gateOpenAsTheYardWasWon3", Open3(M33_GATE));
		// the tower's exit: shut while anything lives in the tower
		int tower = HallIx(5);
		if (o == 2) Check("towerShutAtGoThree", tower >= 0 && Shut3(M33_TSHUT) && HallLives(tower) && hTrack[tower]);
		if (o > 2 && tower >= 0 && wonTic[tower] < 0)
		{
			m3TowerSeen = true;
			if (!Shut3(M33_TSHUT) || !HallLives(tower)) m3TowerBad = true;
		}
		if (exitOpened && !m3ExitSeen)
		{
			m3ExitSeen = true;
			Check("exitOpenedByTheTwoEarlierSelves", plates[0].pressed && plates[1].pressed && !plates[0].mine && !plates[1].mine);
			Console.Printf("AJARTEST info the exit door opens at %d of go 3; the player at (%d,%d)", o, mo.pos.x, mo.pos.y);
		}
		if (Through(mo) && !m3Through)
		{
			m3Through = true;
			Check("throughTheExitDoor", tgo == 3 && !paradox);
			Sizes33("at the exit");
			Report33(2, "go 3");
			Report33(5, "go 3 while R is played (every hall played: the yard, the boiler house, the workshop, R; none recorded)");
		}
	}

	void Go33Three(PlayerPawn mo)
	{
		int o = ot;
		let h = Doors();
		AjarDoor pink = Door32(6);
		if (m3Step == 0)
		{
			if (o >= 6 && Once33(9)) View33(mo, "box 3: S through the glass, two selves", 192, 2510, 90, 0);
			Clear33(mo);
			if (m3Route == 15 && m3Ix == 3 && Once33(10)) View33(mo, "the cable tunnel", 300, 2048, 0, 0);
			if (Walk33(mo, 15)) { pink.Used(mo); Check("pinkTaken", h.carried == pink); m3Step = 1; View33(mo, "the switchyard", 1330, 2060, 330, -4); }
		}
		if (m3Step == 1)
		{
			Clear33(mo);
			if (Walk33(mo, 16))
			{
				h.FindFrame(103).Activate(mo);
				Check("pinkHung", pink.frame == h.FindFrame(103) && !h.carried);
				m3Step = 2;
				View33(mo, "the switchyard from PINK's frame: the gravel banks along the north", 2700, 1440, 150, 2);
			}
		}
		if (m3Step == 2)
		{
			Toward(mo, (2900, 1440), 8);
			if (mo.pos.x > 2930 && mo.pos.y > 1792)
			{
				Check("relayRoomReached", PartAt(mo.pos.xy) == 3);
				m3Step = 3;
				View33(mo, "the relay room: the workshop through its window (played)", 3260, 1980, 90, 0);
			}
		}
		if (m3Step == 3)
		{
			Clear33(mo);
			if (Walk33(mo, 17)) { m3Step = 4; View33(mo, "the cooling pond from the foot of the steps", 3488, 1690, 290, -2); }
		}
		if (m3Step == 4)
		{
			// through the water: the pond's fight, killed as it comes in sight
			Clear33(mo);
			if (Walk33(mo, 18))
			{
				m3Step = 5;
				Check("outfallReached", PartAt(mo.pos.xy) == 3 && mo.floorz == -8);
				View33(mo, "the outfall: the cooling tower from the channel, before the drop", 4500, 1024, 0, -8);
			}
		}
		if (m3Step == 5)
		{
			Clear33(mo);
			Walk33(mo, 19);
			if (mo.pos.x > 4560 && mo.pos.z <= M33_TF + 1)
			{
				int tower = HallIx(5);
				Check("droppedIntoTheTower", mo.floorz == M33_TF && HallAt(mo.pos.xy) == tower && Shut3(M33_TSHUT) && HallLives(tower));
				m3Step = 6; m3From = o; m3Route = -1;
				View33(mo, "the cooling tower from its floor: the cyberdemon on the basin, the ring ledge", 4620, 1024, 0, 6);
			}
		}
		if (m3Step == 6 && Fight33(mo, HallIx(5), false)) { m3Step = 7; Console.Printf("AJARTEST info the tower's fight: %d to %d", m3From, o); }
		if (m3Step == 7)
		{
			int tower = HallIx(5);
			if (wonTic[tower] < 0 || o < wonTic[tower] + 40) return;
			Check("towerShutUntilItIsClear", m3TowerSeen && !m3TowerBad);
			Check("towerOpensWhenClear", Open3(M33_TSHUT) && !HallLives(tower));
			Console.Printf("AJARTEST info the tower won at %d of go 3", wonTic[tower]);
			m3Step = 8;
		}
		if (m3Step == 8)
		{
			Clear33(mo);
			if (Walk33(mo, 20))
			{
				Check("throughTheTowerIntoTheDuct", PartAt(mo.pos.xy) == 3 && mo.floorz == -128);
				m3Step = 9;
			}
		}
		if (m3Step == 9)
		{
			// in the duct, at go 2's fight in R (or after it)
			Clear33(mo);
			if (o >= (m3RFrom + m3RTo) / 2)
			{
				View33(mo, "the duct: go 2's fight in R through the glass (go 3)", 5700, 1950, 90, 0);
				m3Step = 10;
			}
		}
		if (m3Step == 10)
		{
			Clear33(mo);
			if (Walk33(mo, 21)) { m3Step = 11; m3Mark = o; }
		}
		if (m3Step == 11)
		{
			if (exitDoor.IsOpen() && o > m3Mark + 4)
			{
				View33(mo, "E3: the exit door open; E2 and E1 through the glass", 7520, 2380, 60, 0);
				m3Step = 12;
			}
		}
		if (m3Step == 12) Walk33(mo, 22);
	}

	// --- mode 2: go 2 too slow ------------------------------------------------------------
	void Map33Paradox(PlayerPawn mo, int t)
	{
		if (thirdLoads)
		{
			// loaded: the save of go 2's start (made before the paradox, so m3Pdx is 0 in it)
			if (m3Pdx >= 0)
			{
				m3Pdx = -1;
				Check("loadedGoTwoStart", tgo == 2 && ot < 5 && !paradox && mo.health > 0 && takes.Size() == 2 && takes[0].x.Size() > M33_LEAVE1
					&& PostsLiving() == posts.Size() && Shut3(M33_GSHUT) && !Bodies33());
				m3Mark = ot;
			}
			if (ot == m3Mark + 30) Check("loadedPlays", Selves3() == 1 && SelfAsRecord(0) && HallPuppets(HallIx(1)) > 0 && HallThings(HallIx(1), true) == 0);
			return;
		}
		if (paradox)
		{
			if (!m3Pdx)
			{
				m3Pdx = t;
				Console.Printf("AJARTEST info paradox at t %d, ot %d: %s", t, ot, paradoxWhy);
				Check("gantryParadox", tgo == 2 && paradoxCopy == 1 && mo.health <= 0 && paradoxWhy.IndexOf("gantry") >= 0 && ot == watchTic[0]
					&& wonTic[HallIx(3)] < 0 && PostsLiving() > 0);
			}
			if (t == m3Pdx + 200) Check("theDarkAfter", ParadoxDark());
			// (USE: smoke_MAP33_2.cfg presses it, +use)
			return;
		}
		if (m3Go != tgo) { m3Go = tgo; m3Step = 0; m3Route = -1; m3Aim = null; }
		if (tgo == 1) { Checks33One(mo); Go33One(mo); }
		else if (tgo == 2) Go33Two(mo, true);
	}
}
