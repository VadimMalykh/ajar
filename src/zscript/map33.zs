// The tests of MAP33 "Third Person" (tools/map_station.py; the engine third.zs
// and last.zs; PLAN.md, "MAP33 "Third Person": the first playable version" and
// "MAP33: the last fight in the level, and doors at the fight halls").
// MAP=MAP33 MODE=n tools/smoke.sh, n:
//  1  the whole level, scripted: three goes, out by the exit door. God mode,
//     and the script kills: in a window hall one monster at a time, the
//     nearest, shot at for six tics and then killed; elsewhere whatever of the
//     go's part comes in sight (or within 320) on the way, one each 4 tics.
//     Checks the lobbies (the coal yard's, the boiler house's, the workshop's:
//     shut behind the player, open into the hall, both open at the win, the
//     ways on shut until it; no monster of the hall out of it; in later goes
//     the same at the same tics), the gate, the doors, the future seen, the
//     halls played in step, the cooling tower; the last hall as lasttest.zs
//     checks LAST: the alarm at plate 1, the guards there and awake, the sums
//     (30 and 15 seconds), the time doors, the earlier selves firing again
//     really, the hall empty at each go's start, stand 3's gate, the exit
//     door's spans, the crossing, the level's end. In the last hall the
//     player's shots are the script's (lasttest.zs's FireL: bullets and
//     rockets with the ammunition they spend taken, so that the record sees
//     them); in go 3 the player does not fire. The wind plate told of once in
//     go 2 and not in go 1; measures the halls' cost and the records' sizes.
//     The gallery (AjarThirdFallen, part 2's corridor seen from part 1): in go
//     1 a body at each fallen thing and nothing living in it (at the start and
//     in the coal yard); at go 2's start each one's monster alive in its place
//     and no body; at go 3's start nothing spawned again.
//  2  go 2 too slow (it stays in box 2): the gantry paradox when the first
//     self comes onto it; then USE (smoke_MAP33_2.cfg): go 2's start loaded.
//  3  as 1, with views: places where a player would stand, each held 70 tics
//     and named in the log; smoke_MAP33_3.cfg shoots in the middle of each
//     (its waits are the views' tics t + 35, from a run's log: a change to the
//     script before a view moves them, and runs differ by some tics).
//  4  the stand's save: killed on stand 2 after the alarm in go 2, USE
//     (smoke_MAP33_4.cfg), the save made at the stand is loaded (before the
//     alarm), the go plays on to its time door and go 3 begins.
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
	// (go 2 has won R by then); in the last hall go 1 holds plate 1 until the
	// alarm + M33_HOLD1, go 2 plate 2 until the alarm + M33_HOLD2 (go 3 is
	// through the exit door by then); go 2 does not fire until the alarm +
	// M33_QUIET; go 3 crosses from the alarm + M33_CROSS
	const M33_GANTRY = 2100;
	const M33_HOLD1 = 1800;
	const M33_HOLD2 = 1700;
	const M33_QUIET = 300;
	const M33_CROSS = 600;
	const M33_DIE = 100;        // mode 4: killed on stand 2 at the alarm + this

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
	// the lobbies: the script's step in one, and what was seen in the hall's go (by lock index)
	int m3LStep, m3LMark;
	Array<bool> m3LockBad, m3LockSeen, m3WaysBad, m3OutBad, m3LockDone;
	Array<Actor> m3Mon;
	Array<int> m3MonLock;
	// the last hall
	bool m3Gave, m3Quick, m3Crossed;
	int m3Alarm, m3Died, m3NoMove, m3ExitBad, m3ExitSeen2;
	Vector2 m3Was;
	int m3KillBy[24];           // [8 * (go - 1) + 4 * (walks or flies) + killer]: 0 the player, 1 self 1, 2 self 2, 3 other
	Array<int> m3Counted;
	// the gallery (AjarThirdFallen): checked from the coal yard; the monsters at go 2's start, and whether each was in it
	bool m3GalYard;
	Array<Actor> m3GoTwoMon;
	Array<bool> m3GoTwoIn;

	// --- the route ------------------------------------------------------------------
	// Routes as pairs of x, y; each ends at the first -1, -1 (routes are numbered in order).
	static const double M33R[] = {
		/* 0 S to before the coal yard's lobby */  384, 2660,  600, 2900,  640, 3040,  512, 3150,  512, 3480,  -1, -1,
		/* 1 across the yard, to the gate */       900, 3790,  1860, 3790,  1860, 4416,  1890, 4416,  -1, -1,
		/* 2 to BLUE */                            2110, 4000,  3000, 3900,  3330, 3880,  -1, -1,
		/* 3 to frame 101 */                       3000, 4100,  2288, 4120,  2288, 4170,  -1, -1,
		/* 4 the catwalk, the pump room, the stack court, the foot of the gantry */
		                                          2272, 4930,  3560, 4900,  3650, 4896,  3650, 4672,  4600, 4672,  4880, 4672,  5000, 4600,  5230, 4450,  5240, 4000,  5200, 3800,  4992, 3700,  4992, 3450,  -1, -1,
		/* 5 onto the gantry */                    4992, 3330,  5100, 3330,  6000, 3330,  -1, -1,
		/* 6 along it, north and east to stand 1, plate 1 */
		                                          7000, 3330,  7240, 3330,  7360, 3330,  7360, 3520,  8150, 3520,  8240, 3552,  8448, 3552,  8448, 3456,  -1, -1,
		/* 7 through time door 1 */                8480, 3520,  8480, 3660,  -1, -1,
		/* 8 box 2, the gallery, before the workshop's lobby */
		                                          576, 2430,  700, 2430,  960, 2430,  960, 3600,  3776, 3600,  3776, 3160,  3000, 3160,  -1, -1,
		/* 9 to VIOLET */                          3700, 3000,  3700, 2280,  -1, -1,
		/* 10 to frame 102 */                      3700, 2920,  2750, 2920,  2750, 2784,  -1, -1,
		/* 11 the armoury: the plasma rifle */     2560, 2368,  2420, 2368,  -1, -1,
		/* 12 the pump hall, the stores, the mezzanine, down into R */
		                                          2760, 2880,  3800, 2880,  3870, 2880,  4000, 2880,  4352, 2880,  4352, 2600,  4352, 2520,  4700, 2520,  4700, 2368,  4800, 2368,  4960, 2368,  5150, 2400,  -1, -1,
		/* 13 the steel door, the passage, stand 2, plate 2 */
		                                          5150, 2848,  6900, 2848,  7000, 2880,  7100, 2880,  7350, 2880,  7600, 2880,  7744, 2880,  -1, -1,
		/* 14 through time door 2 */               7700, 3008,  7560, 3008,  -1, -1,
		/* 15 box 3, the cable tunnel, PINK */     192, 2400,  192, 2280,  192, 2050,  1270, 2050,  1350, 2040,  1400, 1880,  -1, -1,
		/* 16 to frame 103 */                      1450, 1720,  2560, 1720,  2600, 1560,  2760, 1440,  -1, -1,
		/* 17 the relay room's south door, the steps, the pond */
		                                          3100, 1920,  3488, 1920,  3488, 1810,  3488, 1740,  3488, 1680,  -1, -1,
		/* 18 through the water to the outfall */  3700, 1520,  4000, 1400,  4300, 1040,  4400, 1024,  4470, 1024,  -1, -1,
		/* 19 the drop into the tower */           4560, 1024,  4640, 1024,  -1, -1,
		/* 20 the tower's exit, the passage, the steps down, the duct */
		                                          4700, 1150,  4850, 1300,  4830, 1480,  4800, 1580,  4800, 1700,  4800, 1920,  4950, 1920,  5070, 1920,  5700, 1950,  -1, -1,
		/* 21 along the duct, up, the corridor to stand 3 */
		                                          7000, 1950,  7550, 1920,  7550, 2288,  8150, 2288,  8384, 2300,  -1, -1,
		/* 22 the crossing (map_station.py's CROSSING): the gate, the steps, the floor, the exit door */
		                                          8384, 2330,  8384, 2500,  8400, 2560,  8400, 2688,  8600, 2688,  8640, 2730,  8640, 2916,  8930, 2916,  8990, 2880,  9140, 2880,  -1, -1,
		/* 23 into the boiler house, to its fight */  2110, 4416,  2110, 4100,  -1, -1
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

	// Whatever of this go's part, not in a window hall nor the last hall, comes in sight or within 320: one killed each 4 tics.
	void Clear33(PlayerPawn mo)
	{
		if (ot % 4) return;
		let it = ThinkerIterator.Create("Actor");
		Actor a, best;
		double bd = 1400;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || a.bInvisible || HallAt(a.pos.xy) >= 0 || PartAt(a.pos.xy) != tgo) continue;
			if (guardIs.Find(a) < guardIs.Size() || (lastMark && InLast(a.pos.xy))) continue;
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

	// --- the gallery: part 2's corridor, seen from part 1 as go 2 leaves it (third.zs, AjarThirdFallen) ---
	static bool InGallery33(Vector2 p) { return p.x >= 896 && p.x <= 3840 && p.y >= 3520 && p.y <= 3696; }

	// The monsters in the gallery's box (`living`: only those alive).
	int GalleryMonsters33(bool living)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && (!living || a.health > 0) && InGallery33(a.pos.xy)) n++;
		return n;
	}

	// The fallen things with a body (an AjarFigure) lying within 8 of them.
	int FallenFigures33()
	{
		int n = 0;
		for (int i = 0; i < fallenAt.Size(); i++)
		{
			let it = ThinkerIterator.Create("AjarFigure");
			Actor f;
			bool got = false;
			while (!got && (f = Actor(it.Next()))) got = (f.pos.xy - fallenAt[i].pos.xy).Length() < 8;
			if (got) n++;
		}
		return n;
	}

	int FallenWant33()
	{
		int n = 0;
		for (int i = 0; i < fallenAt.Size(); i++) if (LeavesBody(AjarHandler.AmbushClass(fallenAt[i].args[1]))) n++;
		return n;
	}

	// The fallen things whose monster stands at them alive, of the right class.
	int FallenAlive33()
	{
		int n = 0;
		for (int i = 0; i < fallenAt.Size(); i++)
		{
			Actor a = fallenIs[i];
			class<Actor> c = Actor.GetReplacement(AjarHandler.AmbushClass(fallenAt[i].args[1]));
			if (a && a.bIsMonster && a.health > 0 && a.GetClass() == c && (a.pos.xy - fallenAt[i].pos.xy).Length() < 1 && !a.target) n++;
		}
		return n;
	}

	// go 1: a body at each fallen thing (every one of the gallery's leaves one), nothing living in the gallery
	void GalleryGoOne33(string when)
	{
		int figs = FallenFigures33(), want = FallenWant33(), living = GalleryMonsters33(true);
		Console.Printf("AJARTEST info the gallery %s (go 1): %d fallen things, %d leave a body, %d bodies there; %d monsters living in it",
			when, fallenAt.Size(), want, figs, living);
		Check("galleryDead" .. when, fallenAt.Size() >= 13 && want == fallenAt.Size() && figs == want && !living);
	}

	// --- the lobbies (third.zs, AjarThirdLock) -----------------------------------------------
	int LockIx(int hallNumber)
	{
		for (int i = 0; i < locks.Size(); i++) if (locks[i].args[0] == hallNumber) return i;
		return -1;
	}

	string LockName(int k) { return HALL33[clamp(locks[k].args[0], 0, 5)]; }

	// Every tic: in a lobby's hall's go, its shutters as at the start until it locks, the ways on shut
	// until the win, no monster of the hall out of it; checked 40 tics after the win. In a later go, the
	// shutters at the tics its go had them.
	void LockChecks33()
	{
		if (paradox || !tgo) return;
		while (m3LockBad.Size() < locks.Size()) { m3LockBad.Push(false); m3LockSeen.Push(false); m3WaysBad.Push(false); m3OutBad.Push(false); m3LockDone.Push(false); }
		int o = ot;
		for (int k = 0; k < locks.Size(); k++)
		{
			AjarThirdLock lk = locks[k];
			int h = HallIx(lk.args[0]);
			if (h < 0) continue;
			int part = halls[h].args[1];
			string n = LockName(k);
			if (part == tgo)
			{
				if (o == 1)
				{
					let it = ThinkerIterator.Create("Actor");
					Actor a;
					while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && HallAt(a.pos.xy) == h) { m3Mon.Push(a); m3MonLock.Push(k); }
				}
				if (o > 1 && lockTic[k] < 0) { m3LockSeen[k] = true; if (!Open3(lk.args[1]) || !Shut3(lk.args[2])) m3LockBad[k] = true; }
				if (o > 1 && wonTic[h] < 0)
					for (int w = 0; w < winners.Size(); w++) if (HallIx(winners[w].args[0]) == h && !Shut3(winners[w].args[1])) m3WaysBad[k] = true;
				for (int i = 0; i < m3Mon.Size(); i++)
				{
					Actor a = m3Mon[i];
					if (m3MonLock[i] != k || !a || a.health <= 0 || HallAt(a.pos.xy) == h) continue;
					if (!m3OutBad[k]) Console.Printf("AJARTEST info a %s of the %s out of it at (%d,%d), tic %d", a.GetClassName(), n, a.pos.x, a.pos.y, o);
					m3OutBad[k] = true;
				}
				if (wonTic[h] >= 0 && o == wonTic[h] + 40 && !m3LockDone[k])
				{
					m3LockDone[k] = true;
					int many = 0;
					for (int i = 0; i < m3Mon.Size(); i++) if (m3MonLock[i] == k) many++;
					bool ways = true;
					for (int w = 0; w < winners.Size(); w++) if (HallIx(winners[w].args[0]) == h && !Open3(winners[w].args[1])) ways = false;
					Console.Printf("AJARTEST info the %s: locked at %d, its inner shutter open at %d, won at %d; %d monsters of it followed", n, lockTic[k], lockOpen[k], wonTic[h], many);
					Check(n .. "LobbyAsAtStartUntilLocked", m3LockSeen[k] && !m3LockBad[k]);
					Check(n .. "WaysOnShutUntilWon", !m3WaysBad[k]);
					Check(n .. "NoMonsterOutOfIt", many > 0 && !m3OutBad[k]);
					Check(n .. "LobbyOpenAtTheWin", Open3(lk.args[1]) && Open3(lk.args[2]) && ways && lockTic[k] >= 0 && lockOpen[k] > lockTic[k]);
				}
			}
			else if (part < tgo)
			{
				int lt = lockTic[k], lo = lockOpen[k], w = wonTic[h];
				if (lt > 0 && o == lt - 1) Check(String.Format("%sOuterOpenUntilItsTic%d", n, tgo), Open3(lk.args[1]) && Shut3(lk.args[2]));
				if (lt >= 0 && o == lt + 20 && (w < 0 || o < w)) Check(String.Format("%sOuterShutAtItsTic%d", n, tgo), Shut3(lk.args[1]));
				if (lo > 0 && o == lo - 1) Check(String.Format("%sInnerShutUntilItsTic%d", n, tgo), Shut3(lk.args[2]));
				if (lo >= 0 && o == lo + 20) Check(String.Format("%sInnerOpenAtItsTic%d", n, tgo), Open3(lk.args[2]));
				if (w >= 0 && o == w + 20)
				{
					bool ways = true;
					for (int x = 0; x < winners.Size(); x++) if (HallIx(winners[x].args[0]) == h && !Open3(winners[x].args[1])) ways = false;
					Check(String.Format("%sOpenAsWon%d", n, tgo), Open3(lk.args[1]) && Open3(lk.args[2]) && ways);
				}
				if (w > 0 && o == w - 1)
				{
					bool shut = true;
					for (int x = 0; x < winners.Size(); x++) if (HallIx(winners[x].args[0]) == h && !Shut3(winners[x].args[1])) shut = false;
					Check(String.Format("%sWaysShutUntilWon%d", n, tgo), shut);
				}
			}
		}
	}

	// The script through a lobby: to `before` (outside it; the shutters as at the start), into it at
	// `inside` (the outer shuts behind, the inner opens), then to `into` in the hall. True once there.
	bool Lobby33(PlayerPawn mo, int hallNumber, Vector2 before, Vector2 inside, double ang, Vector2 into, string what)
	{
		int k = LockIx(hallNumber);
		if (k < 0) { Check("lobbyFound", false); return true; }
		AjarThirdLock lk = locks[k];
		string n = LockName(k);
		if (m3LStep == 0)
		{
			if (!Toward(mo, before, 16)) return false;
			Check(n .. "LobbyBefore", Open3(lk.args[1]) && Shut3(lk.args[2]) && lockTic[k] < 0);
			m3LStep = 1; m3LMark = ot;
			View33(mo, what .. "'s lobby from outside: the outer shutter open, the inner one shut", before.x, before.y, ang, 0);
			return false;
		}
		if (m3LStep == 1)
		{
			if (!Toward(mo, inside, 8)) return false;
			m3LStep = 2;
		}
		if (m3LStep == 2)
		{
			mo.vel.xy = (0, 0);
			if (!Open3(lk.args[2]) && ot - m3LMark < 300) return false;
			Console.Printf("AJARTEST info the %s's lobby: set off into it at %d, locked at %d, the inner shutter open at %d (fully at %d)", n, m3LMark, lockTic[k], lockOpen[k], ot);
			Check(n .. "LobbyLocked", Shut3(lk.args[1]) && Open3(lk.args[2]) && lockTic[k] > m3LMark && lockOpen[k] > lockTic[k] && SecTagged(mo.pos.xy, lk.args[3]));
			m3LStep = 3;
			View33(mo, what .. "'s lobby from inside: the outer shutter shut behind, the hall through the inner one", inside.x, inside.y, ang, 0);
			return false;
		}
		if (!Toward(mo, into, 16))
		{
			// a monster of the hall come to the doorway stands in the way: killed by script (said; seen in a MODE=3 run)
			if ((mo.pos.xy - m3Was).Length() < 1) m3NoMove++; else m3NoMove = 0;
			m3Was = mo.pos.xy;
			if (m3NoMove > 15)
			{
				KillNear33(mo);
				m3NoMove = 0;
			}
			return false;
		}
		m3LStep = 0;
		return true;
	}

	void KillNear33(PlayerPawn mo)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			if (a.bIsMonster && a.health > 0 && a.Distance2D(mo) < 96)
			{
				Console.Printf("AJARTEST info a %s stood in the way at (%d,%d): killed by script", a.GetClassName(), a.pos.x, a.pos.y);
				a.DamageMobj(null, null, 10000, 'None');
				m3Killed++;
			}
	}

	// --- the last hall ---------------------------------------------------------------------
	static bool Stands33(Actor a) { return a is "Arachnotron" || a is "Fatso" || a is "Revenant" || a is "ChaingunGuy"; }

	// Every guard dead since the last look: counted by its killer, and whether it stood.
	void Kills33(PlayerPawn mo)
	{
		while (m3Counted.Size() < guardIs.Size()) m3Counted.Push(0);
		for (int i = 0; i < guardIs.Size(); i++)
		{
			Actor a = guardIs[i];
			if (!a || a.health > 0 || m3Counted[i]) continue;
			m3Counted[i] = 1;
			Actor by = guardHitBy[i];
			int k = 3;
			if (by == mo) k = 0;
			else for (int s = 0; s < ghosts.Size() && s < 2; s++) if (ghosts[s] && by == ghosts[s]) k = s + 1;
			m3KillBy[8 * (clamp(tgo, 1, 3) - 1) + (Stands33(a) ? 0 : 4) + k]++;
		}
	}

	void PrintKills33(int go)
	{
		int st = 0, mv = 0;
		for (int i = 0; i < guards.Size(); i++)
		{
			class<Actor> c = AjarHandler.AmbushClass(guards[i].args[0]);
			if (c && (c is "Arachnotron" || c is "Fatso" || c is "Revenant" || c is "ChaingunGuy")) st++; else mv++;
		}
		int b = 8 * (go - 1);
		Console.Printf("AJARTEST info kills go=%d standing (of %d): the player %d, self 1 %d, self 2 %d, other %d; walking or flying (of %d): the player %d, self 1 %d, self 2 %d, other %d",
			go, st, m3KillBy[b], m3KillBy[b + 1], m3KillBy[b + 2], m3KillBy[b + 3], mv, m3KillBy[b + 4], m3KillBy[b + 5], m3KillBy[b + 6], m3KillBy[b + 7]);
	}

	// The script's ammunition for the last fight, once a go (said): what the stand's supplies would give and more.
	void Arm33(PlayerPawn mo)
	{
		if (m3Gave) return;
		m3Gave = true;
		Console.Printf("AJARTEST info go %d on its stand with %d bullets, %d rockets; the script gives 200 bullets and 50 rockets more (FireL's)", tgo, mo.CountInv("Clip"), mo.CountInv("RocketAmmo"));
		mo.GiveInventory("Backpack", 1);
		mo.GiveInventory("Clip", 200);
		mo.GiveInventory("RocketAmmo", 50);
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
		if (mode == 4 && m3Died > 0 && !thirdLoads) mo.player.cheats &= ~CF_GODMODE;
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) go=%d ot=%d step=%d selves=%d puppets=%d frozen=%d won=%d,%d,%d,%d td=%d exit=%d p1=%d p2=%d killed=%d health=%d loads=%d alarm=%d living=%d sum=%d",
				t, mo.pos.x, mo.pos.y, mo.pos.z, tgo, ot, m3Step, Selves3(), puppets.Size(), tfz.Size(),
				wonTic.Size() > 0 ? wonTic[0] : -9, wonTic.Size() > 1 ? wonTic[1] : -9, wonTic.Size() > 2 ? wonTic[2] : -9, wonTic.Size() > 3 ? wonTic[3] : -9,
				tdOpen, exitDoor && exitDoor.IsOpen(), plates.Size() > 0 && plates[0].pressed, plates.Size() > 1 && plates[1].pressed, m3Killed, mo.health, thirdLoads,
				alarmTic, LastLiving(), plateSum);
		if (mode == 2) { Map33Paradox(mo, t); return; }
		if (mode == 4) { Map33StandSave(mo, t); return; }
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
		NewGo33(mo);
		SnapChecks33();
		HungAgain33();
		LockChecks33();
		AlarmChecks(mo);            // lasttest.zs: the last hall at each go's start and at the alarm
		Kills33(mo);
		if (tgo == 1) Checks33One(mo);
		else if (tgo == 2) Checks33Two(mo);
		else if (tgo == 3) Checks33Three(mo);
		if (Hold33(mo)) return;
		if (tgo == 1) Go33One(mo);
		else if (tgo == 2) Go33Two(mo, false);
		else if (tgo == 3) Go33Three(mo);
	}

	void NewGo33(PlayerPawn mo)
	{
		if (m3Go == tgo) return;
		if (m3Go == 1) { Report33(0, "go 1"); Report33(3, "the coal yard's fight (go 1: the yard and the boiler house recorded)"); }
		if (m3Go == 2) { Report33(1, "go 2"); Report33(4, "R's fight (go 2: R and the workshop recorded, the yard and the boiler house played)"); }
		if (m3Go >= 1) PrintKills33(m3Go);
		if (tgo >= 2) Sizes33(String.Format("at go %d's start", tgo));
		m3Go = tgo;
		m3Step = 0;
		m3LStep = 0;
		m3Route = -1;
		m3Aim = null;
		m3Gave = false;
		m3Counted.Clear();
		ltTurned = ltAlarmChecked = ltDoorChecked = false;
		ltFirst.Clear();
		Console.Printf("AJARTEST info go %d: god mode; the script kills (hall fights: shot at six tics, then killed; elsewhere what comes in sight)", tgo);
	}

	// --- go 1 ------------------------------------------------------------------------------
	void Checks33One(PlayerPawn mo)
	{
		int o = ot;
		int yard = HallIx(1), r = HallIx(3);
		if (o == 2)
		{
			Check("goOneBegun", tgo == 1 && parts == 3 && plates.Size() == 2 && halls.Size() == 5 && exitDoor && !Selves3() && locks.Size() == 3 && lastMark);
			Console.Printf("AJARTEST info posts %d, bodies %d (of %d that leave one), monsters in the level %d, guards %d", posts.Size(), Bodies33(), WantBodies33(), level.total_monsters, guards.Size());
			// the future seen: a body at each post that leaves one, nothing alive in R, its shutters open
			Check("bodiesInR", posts.Size() >= 14 && Bodies33() == WantBodies33() && !HallLives(r) && Open3(M33_GSHUT) && Open3(M33_STEEL));
			Check("gateShutAtTheStart", Shut3(M33_GATE) && HallLives(yard));
			Check("towerOpenBeforeItsGo", Open3(M33_TSHUT) && halls.Size() == 5);
			// the lobbies at the start: the outer shutters open, the inner shut; the workshop's (go 2) and its way on as before its go
			bool lobbies = true;
			for (int k = 0; k < locks.Size(); k++) if (!Open3(locks[k].args[1]) || !Shut3(locks[k].args[2])) lobbies = false;
			Check("lobbiesAtTheStart", lobbies && locks.Size() == 3);
			Check("workshopWayOnOpenBeforeItsGo", Open3(3382) && Shut3(3380) && Shut3(3381));
			GalleryGoOne33("AtTheStart");
		}
		// the gallery again, from the coal yard (the script in it: its fight begins)
		if (!m3GalYard && m3Step >= 1 && HallAt(mo.pos.xy) == yard) { m3GalYard = true; GalleryGoOne33("FromTheYard"); }
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
			else if (Walk33(mo, 0)) m3Step = 20;
			if (m3Step == 0) Clear33(mo);
		}
		if (m3Step == 20)
		{
			Clear33(mo);
			if (Lobby33(mo, 1, (512, 3480), (512, 3640), 90, (512, 3790), "the coal yard"))
			{
				m3Step = 1; m3From = o;
				View33(mo, "the coal yard from its mouth: the fight to come", 512, 3780, 50, 2);
			}
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
		if (m3Step == 3 && m3Shots && m3Hold <= 0 && Once33(14))
			View33(mo, "the gallery through the coal yard's east window (go 1): its monsters dead, as go 2 leaves them", 1500, 3740, 345, 4);
		else if (m3Step == 3 && Walk33(mo, 1)) m3Step = 21;
		if (m3Step == 21 && Lobby33(mo, 4, (1890, 4416), (2008, 4416), 0, (2110, 4416), "the boiler house")) m3Step = 22;
		if (m3Step == 22 && Walk33(mo, 23))
		{
			m3Step = 4; m3From = o;
			View33(mo, "the boiler house: the boilers, the catwalk", 2120, 3760, 45, -4);
		}
		if (m3Step == 4 && Fight33(mo, boil, true))
		{
			m3Step = 5;
			Console.Printf("AJARTEST info the boiler house's fight: %d to %d", m3From, o);
			View33(mo, "the gallery through the boiler house's window (go 1): its monsters dead, as go 2 leaves them", 2150, 3740, 345, 4);
		}
		if (m3Step == 5)
		{
			if (wonTic[boil] < 0) return;
			if (Walk33(mo, 2)) { blue.Used(mo); Check("blueTaken", h.carried == blue); m3Step = 6; }
		}
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
			if (Walk33(mo, 4)) { m3Step = 9; m3Mark = o; }
			if (m3Route == 4 && m3Ix == 3 && Once33(3)) View33(mo, "the pump room", 3660, 4920, 315, 2);
			if (m3Route == 4 && m3Ix == 7 && Once33(4)) View33(mo, "the stack court: the chimney's foot", 4950, 4650, 315, -6);
			if (m3Route == 4 && m3Ix == 10 && Once33(11)) View33(mo, "the stack court from the south: the imps' ledge round the north-east", 5300, 3800, 45, -4);
		}
		if (m3Step == 9)
		{
			Clear33(mo);
			int waitTo = M33_GANTRY + (m3Shots ? 400 : 0);     // (mode 3: go 2 is held up by its views)
			if (o == waitTo - 1) Console.Printf("AJARTEST info go 1 at the foot of the gantry from %d, waiting until %d", m3Mark, waitTo);
			if (o >= waitTo) m3Step = 10;
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
			if (o >= m3Mark + 8)
			{
				if (m3Route == 6 && m3Ix == 5 && Once33(12)) View33(mo, "the corridor to stand 1: its supplies", 7400, 3520, 0, 0);
				if (Walk33(mo, 6))
				{
					int seen = 0, want = 0;
					for (int i = 0; i < postIs.Size(); i++)
						if (postIs[i] is "AjarFigure") { want++; if (i < m3PostSeen.Size() && m3PostSeen[i]) seen++; }
					Console.Printf("AJARTEST info bodies seen from the gantry: %d of %d", seen, want);
					Check("everyBodySeenFromTheGantry", want > 0 && seen == want);
					m3Step = 12; m3Mark = o;
				}
			}
		}
		if (m3Step == 12) Last33One(mo);
		if (m3Step == 13) Walk33(mo, 7);
	}

	// go 1 on stand 1: the alarm at plate 1, held under fire until the alarm + M33_HOLD1 (m3Quick: the door + 50)
	void Last33One(PlayerPawn mo)
	{
		int o = ot;
		if (o == m3Mark + 2) Check("standSaveOne", standSaved && SecTagged(mo.pos.xy, StandTag(1)));       // (the alarm rings as the plate is come to)
		Arm33(mo);
		StayAt(mo, (8448, 3456));
		if (alarmTic < 0)
		{
			if (o == m3Mark + 30) Check("alarmAtPlateOne", false);
			return;
		}
		int a = o - alarmTic;
		if (a == 1) Check("alarmAtPlateOne", alarmTic <= m3Mark + 3 && plates[0].mine && lastGate && LastLiving() == guards.Size());
		FireL(mo, o);
		if (!ltDoorChecked && tdOpen)
		{
			ltDoorChecked = true;
			m3PlateAt = o;
			Console.Printf("AJARTEST info time door 1 open at %d (the alarm + %d): sum %d of %d", o, a, plateSum, LastNeed());
			Check("doorOneAtSum", plateSum == LastNeed() && LastNeed() == 35 * 30 && a >= LastNeed() - 1);
		}
		if (!tdOpen && plateSum == LastNeed() - 1) Check("doorOneShutBefore", !tdOpen);
		if (a == 600) View33(mo, "stand 1 in the fight (go 1): plate 1 held, the hall below", 8448, 3456, 250, 16);
		if (a == M33_HOLD1 || (m3Quick && tdOpen && o == m3PlateAt + 50))
		{
			AjarTake t = takes[0];
			int bullets = 0, missiles = 0, early = 0;
			for (int e = 0; e < t.evTic.Size(); e++) { if (t.evKind[e] == 1) bullets++; if (t.evKind[e] == 0) missiles++; if (t.evTic[e] <= alarmTic) early++; }
			Console.Printf("AJARTEST info go 1 fired: %d bullets, %d missiles, %d before the alarm; leaves plate 1 at %d", bullets, missiles, early, o);
			Check("shotsInTake", bullets > 50 && !early && tdOpen);      // (rockets: only at what is not a demon, 256 or more off: few)
			m3Step = 13;
			mo.pitch = 0;
		}
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
			Check("hallEmptyAgain", LastLoose() == 0 && LastLiving() == 0 && lastGate && lastGate.IsShut() && takes.Size() == 2);
			// the gallery: each fallen thing's monster alive at it, no body left; noted for go 3
			int alive = FallenAlive33(), figs = FallenFigures33(), living = GalleryMonsters33(true);
			Console.Printf("AJARTEST info the gallery at go 2's start: %d fallen things, %d monsters alive at them, %d bodies there; %d monsters living in it",
				fallenAt.Size(), alive, figs, living);
			Check("galleryAliveGoTwo", fallenAt.Size() >= 13 && alive == fallenAt.Size() && !figs && living == fallenAt.Size());
			m3GoTwoMon.Clear(); m3GoTwoIn.Clear();
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) { m3GoTwoMon.Push(a); m3GoTwoIn.Push(InGallery33(a.pos.xy)); }
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
				if (Walk33(mo, 8)) { m3Step = 20; m3NoMove = 0; }
				if (m3Route == 8 && m3Ix == 4 && Once33(6)) View33(mo, "the gallery: the coal yard's fight through the glass (played)", 1150, 3560, 60, 0);
				else if (m3Step == 0 && m3Route == 8)
				{
					// a monster of the gallery (alive from this go's start: AjarThirdFallen) in the way: killed by script (said)
					if ((mo.pos.xy - m3Was).Length() < 1) m3NoMove++; else m3NoMove = 0;
					m3Was = mo.pos.xy;
					if (m3NoMove > 15) { KillNear33(mo); m3NoMove = 0; }
				}
			}
		}
		if (m3Step == 20)
		{
			Clear33(mo);
			if (Lobby33(mo, 2, (3000, 3160), (2848, 3160), 180, (2816, 3000), "the workshop"))
			{
				m3Step = 1; m3From = o;
				View33(mo, "the workshop from its door: the fight to come", 2816, 3040, 300, 0);
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
			if (wonTic[work] < 0) return;
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
			if (Walk33(mo, 13)) { m3Step = 10; m3Mark = o; }
		}
		if (m3Step == 10) Last33Two(mo);
		if (m3Step == 11) Walk33(mo, 14);
	}

	// go 2 on stand 2: plate 2 held from before the alarm; not firing until the alarm + M33_QUIET (what the first
	// self does), then firing; leaves at the alarm + M33_HOLD2 (m3Quick: the door + 50). `die`: killed at the alarm + M33_DIE.
	void Last33Two(PlayerPawn mo, bool die = false)
	{
		int o = ot;
		if (o == m3Mark + 2) Check("standSaveTwo", standSaved && SecTagged(mo.pos.xy, StandTag(2)) && alarmTic < 0);
		if (o == m3Mark + 4) View33(mo, "stand 2 before the alarm (go 2): plate 2, stand 1 across the hall", 7744, 2880, 20, 8);
		Arm33(mo);
		if (die && m3Died) return;
		StayAt(mo, (7744, 2880));
		if (alarmTic < 0) return;
		int a = o - alarmTic;
		if (a == 10) Check("sumWhilePlateOneOn", plateSum >= 9 && plates[1].mine && plates[0].pressed);
		if (a == M33_QUIET)
		{
			int dmg = 0;
			for (int i = 0; i < guardSelfDmg.Size(); i++) dmg += guardSelfDmg[i];
			let g = AjarLastSelf(ghosts[0]);
			Console.Printf("AJARTEST info go 2, %d tics after the alarm: the first self did %d damage, was hit %d times, its health %d; it fired %d of %d",
				a, dmg, g ? g.hits : -1, g ? g.health : -1, takes[0].next, takes[0].evTic.Size());
			Check("selfFiresAgain", dmg > 0 && takes[0].next > 0);
			Check("turnsOnSelf", ltTurned);
			Check("selfHitUnharmed", g && g.hits > 0 && g.health == g.SpawnHealth() && g.bShootable);
		}
		if (die && a == M33_DIE)
		{
			m3Died = m3T;
			mo.player.cheats &= ~CF_GODMODE;
			mo.DamageMobj(null, null, 10000, 'None', DMG_FORCED);
			Check("killedOnStandTwo", mo.health <= 0 && SecTagged(mo.pos.xy, StandTag(2)));
			return;
		}
		if (a >= M33_QUIET) FireL(mo, o);
		if (!ltDoorChecked && tdOpen)
		{
			ltDoorChecked = true;
			m3PlateAt = o;
			Console.Printf("AJARTEST info time door 2 open at %d (the alarm + %d): sum %d of %d", o, a, plateSum, LastNeed());
			Check("doorTwoAtSum", plateSum == LastNeed() && LastNeed() == 35 * 15 && a >= LastNeed() - 1);
			Check("doorTwoWithBothPlates", exitOpened && plates[0].pressed && !plates[0].mine && plates[1].mine);
		}
		if (!tdOpen && plateSum == LastNeed() - 1) Check("doorTwoShutBefore", !tdOpen);
		if (a == 700) View33(mo, "stand 2 in the fight (go 2): the first self on stand 1 firing again", 7744, 2880, 25, 10);
		if (tdOpen && (a == M33_HOLD2 || (m3Quick && o == m3PlateAt + 50)))
		{
			Console.Printf("AJARTEST info go 2 on plate 2 from %d to %d", m3Mark, o);
			Check("windLineSaidOnceInGoTwo", windSays == 1);
			m3Step = 11;
			mo.pitch = 0;
		}
	}

	// --- go 3 ------------------------------------------------------------------------------
	void Checks33Three(PlayerPawn mo)
	{
		int o = ot;
		int work = HallIx(2), r = HallIx(3), yard = HallIx(1);
		if (o == 0) Check("boxThree", tgo == 3 && BoxOf(mo) == 3 && takes.Size() == 3);
		if (o == 1) Check("hallEmptyThree", LastLoose() == 0 && LastLiving() == 0 && takes.Size() == 3 && lastGate && lastGate.IsShut());
		if (o == 2)
		{
			Check("twoSelves", Selves3() == 2 && SelfAsRecord(0) && SelfAsRecord(1));
			Check("rPlayedFromItsStart", HallPuppets(r) >= posts.Size() && HallThings(r, true) == 0 && Shut3(M33_STEEL) && Shut3(M33_GSHUT));
			Check("workshopPlayed", HallPuppets(work) > 0 && HallThings(work, true) == 0);
			Check("pinkAsAtTheStart", !Door32(6).frame);
			for (int i = 0; i < tLine.Size(); i++) Console.Printf("AJARTEST info timetable: %s", tLine[i]);
			Check("timetableLines", tLine.Size() == 3);
			// the gallery: nothing spawned again (a monster that came into it from elsewhere in go 2 is told apart)
			int n = 0, living = 0, came = 0, fresh = 0;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (!a.bIsMonster || !InGallery33(a.pos.xy)) continue;
				n++;
				if (a.health > 0) living++;
				int k = m3GoTwoMon.Find(a);
				if (k == m3GoTwoMon.Size()) fresh++;
				else if (!m3GoTwoIn[k]) came++;
			}
			int figs = FallenFigures33();
			Console.Printf("AJARTEST info the gallery at go 3's start: %d monsters in it (%d living), %d came in from elsewhere in go 2, %d new since go 2's start; %d fallen things, %d bodies there",
				n, living, came, fresh, fallenAt.Size(), figs);
			Check("galleryNotSpawnedAgain", m3GoTwoMon.Size() > 0 && !fresh && n - came <= fallenAt.Size() && !figs);
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
		// the exit door as the timetable has it (sampled; not within 15 tics of a change)
		if (o % 35 == 3 && exitDoor && !m3Through)
		{
			bool want = false, near = false;
			for (int s = 0; s < heldFrom.Size(); s++)
			{
				int a = heldFrom[s] + 1, b = heldTo[s] + openTics;
				if (o >= a && o < b) want = true;
				if (abs(o - a) < 15 || abs(o - b) < 15) near = true;
			}
			if (!near)
			{
				m3ExitSeen2++;
				if (want != exitDoor.IsOpen() || !want != exitDoor.IsShut()) { m3ExitBad++; Console.Printf("AJARTEST info exit door at %d: wanted %d, open %d", o, want, exitDoor.IsOpen()); }
			}
		}
		if (alarmTic >= 0 && o == alarmTic + M33_QUIET + 100)
		{
			Console.Printf("AJARTEST info go 3 at the alarm + 400 (self 2 fires from + 300): self 1 fired %d of %d, self 2 %d of %d", takes[0].next, takes[0].evTic.Size(), takes[1].next, takes[1].evTic.Size());
			Check("twoSelvesFiring", takes[0].next > 0 && takes[1].next > 0 && Selves3() == 2);
		}
		if (alarmTic < 0 && alarmAt > 0 && o == alarmAt - 1) Check("gateShutBeforeAlarm", lastGate && lastGate.IsShut());
		if (exitOpened && !m3ExitSeen)
		{
			m3ExitSeen = true;
			Check("exitOpenedByTheTwoEarlierSelves", plates[0].pressed && plates[1].pressed && !plates[0].mine && !plates[1].mine);
			Console.Printf("AJARTEST info the exit door opens at %d of go 3; the player at (%d,%d)", o, mo.pos.x, mo.pos.y);
		}
		if (Through(mo) && !m3Through)
		{
			m3Through = true;
			Console.Printf("AJARTEST info through the exit door at %d (the exit door open until %d)", o, exitUntil);
			Check("throughTheExitDoor", tgo == 3 && !paradox && m3Crossed);
			Console.Printf("AJARTEST info the exit door: %d samples, %d not as the timetable", m3ExitSeen2, m3ExitBad);
			Check("exitAsTimetable", m3ExitSeen2 > 20 && !m3ExitBad);
			PrintKills33(3);
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
			// on stand 3, not firing, until the alarm + M33_CROSS with the exit door open
			if (o == m3Mark + 2) Check("standSaveThree", standSaved && SecTagged(mo.pos.xy, StandTag(3)) && alarmTic < 0);
			if (o == m3Mark + 4) View33(mo, "stand 3 before the alarm (go 3): the gate shut, the hall empty", 8384, 2300, 60, 10);
			StayAt(mo, (8384, 2300));
			if (alarmTic >= 0 && o == alarmTic + 300) View33(mo, "stand 3 in the fight (go 3): both earlier selves firing again", 8384, 2300, 70, 10);
			if (alarmTic >= 0 && o >= alarmTic + M33_CROSS && exitDoor.IsOpen())
			{
				Check("exitOpenAtTheCrossing", exitDoor.IsOpen() && lastGate.IsOpen() && plates[0].pressed && plates[1].pressed);
				m3Step = 12; m3Was = mo.pos.xy; m3NoMove = 0;
				Console.Printf("AJARTEST info go 3 crosses at %d (the alarm + %d), guards living %d", o, o - alarmTic, LastLiving());
			}
		}
		if (m3Step == 12)
		{
			if (!m3Crossed && SecTagged(mo.pos.xy, lastMark.args[0]) && mo.pos.y > 2500) m3Crossed = true;
			if (m3Crossed && mo.pos.x > 8620 && Once33(13)) { View33(mo, "the crossing (go 3): the exit door ahead", mo.pos.x, mo.pos.y, 20, 4); return; }
			// something stands in the way: it is killed by script (said)
			if ((mo.pos.xy - m3Was).Length() < 1) m3NoMove++; else m3NoMove = 0;
			m3Was = mo.pos.xy;
			if (m3NoMove > 15)
			{
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next()))
					if (a.bIsMonster && a.health > 0 && a.Distance2D(mo) < 96)
					{
						Console.Printf("AJARTEST info a %s stood in the way at (%d,%d): killed by script", a.GetClassName(), a.pos.x, a.pos.y);
						a.DamageMobj(null, null, 10000, 'None');
					}
				m3NoMove = 0;
			}
			if (Walk33(mo, 22, 12)) m3Step = 13;
		}
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
				Check("loadedGoTwoStart", tgo == 2 && ot < 5 && !paradox && mo.health > 0 && takes.Size() == 2 && takes[0].x.Size() > alarmAt
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
		m3Quick = true;
		NewGo33(mo);
		LockChecks33();
		if (tgo == 1) { Checks33One(mo); Go33One(mo); }
		else if (tgo == 2) Go33Two(mo, true);
	}

	// --- mode 4: the stand's save -------------------------------------------------------------
	void Map33StandSave(PlayerPawn mo, int t)
	{
		if (paradox) { if (!m3Pdx) { m3Pdx = t; Check("noParadox", false); Console.Printf("AJARTEST info paradox: %s", paradoxWhy); } return; }
		m3Quick = true;
		if (thirdLoads)
		{
			// loaded: the save made at stand 2 (the alarm not yet rung in it; m3Died is 0 in it)
			if (m3Died >= 0)
			{
				m3Died = -1;
				Console.Printf("AJARTEST info loaded: go=%d ot=%d alarm=%d (rings at %d) len1=%d", tgo, ot, alarmTic, alarmAt, takes[0].x.Size());
				Check("loadedStandSave", tgo == 2 && alarmTic < 0 && ot < alarmAt && SecTagged(mo.pos.xy, StandTag(2)) && mo.health > 0
					&& LastLiving() == 0 && LastLoose() == 0 && standSaved && takes.Size() == 2);
			}
			if (tgo == 2)
			{
				AlarmChecks(mo);
				if (Hold33(mo)) return;
				Go33Two(mo, false);
			}
			if (tgo == 3 && m3Go != 3)
			{
				m3Go = 3;
				Check("goThreeAfterLoad", !tdOpen && takes.Size() == 3 && takes[1].x.Size() > alarmAt && takes[1].evTic.Size() > 0);
			}
			return;
		}
		NewGo33(mo);
		LockChecks33();
		AlarmChecks(mo);
		if (tgo == 1) { Checks33One(mo); Go33One(mo); }
		else if (tgo == 2)
		{
			if (m3Step == 10) { Last33Two(mo, true); return; }
			Go33Two(mo, false);
		}
		// (USE: smoke_MAP33_4.cfg presses it, +use)
	}
}
