// The one-sided doorway lab (map ONESIDE, tools/map_oneside.py; PLAN.md, "The
// one-sided doorway lab"). MAP=ONESIDE MODE=n tools/smoke.sh: 1 walking,
// 2 views (screenshots), 3 shots, 4 monsters, 5 sound and things on the line.
// Lines: 401 the turn-round's odd face (B's side), 402 C's opening; 411 the
// longer way back's odd face (Q's side), 412 its plain mouth, 413 and 414 the
// ends of X; 421 the booth's face, 422 R's opening; 431 the one-way sight's
// odd face (MR's side), 432 E's opening.

// Something to shoot at that stays where it is put and keeps count.
class OneSideDummy : Actor
{
	int hits;
	string by;
	Default
	{
		Radius 16;
		Height 56;
		Health 100000;
		Mass 100000;
		+SHOOTABLE +SOLID +NOBLOOD +DONTTHRUST +NOGRAVITY +NODAMAGETHRUST
	}
	States
	{
	Spawn:
		POSS A -1;
		Stop;
	}

	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		hits++;
		by = inflictor ? inflictor.GetClassName() .. "" : "none";
		return 0;
	}
}

// One actor's crossings: where it was and how it moved the tic before each
// jump (a portal moves it far in one tic), and where and how after.
class OneSideWatch play
{
	Actor who;
	string name;
	Vector3 lastPos, lastVel;
	double lastAngle;
	Vector2 setVel;          // the velocity the script gave it this tic (zero: none)
	double ratio;            // speed after a plain tic over the speed given
	Array<double> fromX, fromY, setX, setY, toX, toY, velX, velY, angBefore, angAfter, ratioBefore;
	Array<int> tics;

	int Jumps() { return tics.Size(); }
}

class OneSideTest : EventHandler
{
	const WALK = 8.33;       // Doom's walking speed, units a tic (about)
	const RUN = 16.67;       // and running
	int tic;
	Array<OneSideWatch> watches;
	Array<Actor> made;       // what a test spawned, to clear away after it
	int playerHurt, ballsSeen;
	Array<Actor> balls;
	Array<double> ballEndX, ballEndY;
	Array<double> ballX, ballY;
	Array<bool> ballDone;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "ONESIDE"; }

	Line FindLine(int id)
	{
		let it = level.CreateLineIdIterator(id);
		int i = it.Next();
		if (i < 0) return null;
		return level.lines[i];
	}

	// The engine maps a point p crossing src to dst.v2 + R(p - src.v1), R a
	// turn by (angle of dst - angle of src + 180) (as AjarSight.ImageThrough).
	static double Turn(Line src, Line dst)
	{
		return VectorAngle(dst.delta.x, dst.delta.y) - VectorAngle(src.delta.x, src.delta.y) + 180;
	}
	static Vector2 Through(Line src, Line dst, Vector2 p)
	{
		return dst.v2.p + Actor.RotateVector(p - src.v1.p, Turn(src, dst));
	}

	OneSideWatch Watch(Actor a, string name)
	{
		let w = new("OneSideWatch");
		w.who = a;
		w.name = name;
		w.lastPos = a.pos;
		w.lastVel = a.vel;
		w.lastAngle = a.angle;
		w.ratio = -1;
		watches.Push(w);
		return w;
	}

	OneSideWatch WatchOf(Actor a)
	{
		for (int i = 0; i < watches.Size(); i++) if (watches[i].who == a) return watches[i];
		return Watch(a, a.GetClassName());
	}

	void WatchTick()
	{
		for (int i = 0; i < watches.Size(); i++)
		{
			let w = watches[i];
			if (!w.who) continue;
			Actor a = w.who;
			if ((a.pos.xy - w.lastPos.xy).Length() > 64)
			{
				w.tics.Push(tic);
				w.fromX.Push(w.lastPos.x); w.fromY.Push(w.lastPos.y);
				w.setX.Push(w.setVel.x); w.setY.Push(w.setVel.y);
				w.toX.Push(a.pos.x); w.toY.Push(a.pos.y);
				w.velX.Push(a.vel.x); w.velY.Push(a.vel.y);
				w.angBefore.Push(w.lastAngle); w.angAfter.Push(a.angle);
				w.ratioBefore.Push(w.ratio);
			}
			else if (w.setVel.Length() > 0) w.ratio = a.vel.xy.Length() / w.setVel.Length();
			w.lastPos = a.pos;
			w.lastVel = a.vel;
			w.lastAngle = a.angle;
			w.setVel = (0, 0);
		}
	}

	void Pose(Actor mo, double x, double y, double ang)
	{
		mo.SetOrigin((x, y, 0), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
		let w = WatchOf(mo);
		w.lastPos = mo.pos;
		w.lastAngle = ang;
		w.setVel = (0, 0);
		w.ratio = -1;
	}

	// Move a thing the way it faces (back: the other way) at `speed`, from
	// tic `from` for `tics` tics. A portal turns it, so this goes on beyond it.
	void Go(Actor a, int t, int from, int tics, double speed, bool back = false)
	{
		if (!a) return;
		if (t >= from && t < from + tics)
		{
			Vector2 v = Actor.AngleToVector(a.angle + (back ? 180 : 0), speed);
			a.vel.xy = v;
			WatchOf(a).setVel = v;
		}
		if (t == from + tics) a.vel.xy = (0, 0);
	}

	void Check(string what, bool ok, Actor mo = null)
	{
		if (mo) Console.Printf("AJARTEST %s=%d pos=(%.2f,%.2f,%.2f) angle=%.2f", what, ok, mo.pos.x, mo.pos.y, mo.pos.z, Actor.Normalize180(mo.angle));
		else Console.Printf("AJARTEST %s=%d", what, ok);
	}

	// The crossing number k of `w` was by line src to line dst as the engine
	// says it should be: the place (where the tic's move would have ended,
	// carried through), the facing, the direction of motion and the speed.
	bool CrossedRight(OneSideWatch w, int k, int src, int dst, string what)
	{
		Line s = FindLine(src), d = FindLine(dst);
		if (k >= w.Jumps() || !s || !d)
		{
			Console.Printf("AJARTEST info %s: no crossing %d (%d in all)", what, k, w.Jumps());
			return false;
		}
		double rot = Turn(s, d);
		Vector2 set = (w.setX[k], w.setY[k]);
		Vector2 want = Through(s, d, (w.fromX[k], w.fromY[k]) + set);
		Vector2 got = (w.toX[k], w.toY[k]);
		double posErr = (got - want).Length();
		double angErr = Actor.DeltaAngle(w.angAfter[k], w.angBefore[k] + rot);
		Vector2 vel = (w.velX[k], w.velY[k]);
		double dirErr = set.Length() > 0 ? Actor.DeltaAngle(VectorAngle(vel.x, vel.y), VectorAngle(set.x, set.y) + rot) : 0;
		double r = set.Length() > 0 ? vel.Length() / set.Length() : 0;
		Console.Printf("AJARTEST info %s: t=%d from (%.2f,%.2f) moving (%.2f,%.2f) facing %.1f -> (%.2f,%.2f) moving (%.2f,%.2f) facing %.1f; "
			.. "turn %.1f; place off by %.3f, facing by %.3f, motion by %.3f; speed kept %.4f (a plain tic %.4f)",
			what, w.tics[k], w.fromX[k], w.fromY[k], set.x, set.y, Actor.Normalize180(w.angBefore[k]), got.x, got.y, vel.x, vel.y,
			Actor.Normalize180(w.angAfter[k]), Actor.Normalize180(rot), posErr, angErr, dirErr, r, w.ratioBefore[k]);
		return posErr < 1 && abs(angErr) < 0.5 && abs(dirErr) < 0.5 && (w.ratioBefore[k] < 0 || abs(r - w.ratioBefore[k]) < 0.02);
	}

	bool InBox(Actor a, double x1, double y1, double x2, double y2)
	{
		return a && a.pos.x > x1 && a.pos.x < x2 && a.pos.y > y1 && a.pos.y < y2;
	}
	bool InA(Actor a) { return InBox(a, 0, 32, 384, 352); }
	bool InB(Actor a) { return InBox(a, 0, 368, 384, 688); }
	bool InC(Actor a) { return InBox(a, 0, 1200, 384, 1536); }
	bool InC2(Actor a) { return InBox(a, -16, 2000, 384, 2320); }
	bool InR(Actor a) { return InBox(a, 1700, 2384, 2468, 3168); }
	bool InHall(Actor a) { return InBox(a, 1700, 32, 2340, 300); }
	bool InBooth(Actor a) { return InBox(a, 1956, 316, 2084, 444); }
	bool InMR(Actor a) { return InBox(a, 2600, 368, 2984, 816); }
	bool InE(Actor a) { return InBox(a, 2600, 1400, 2984, 1736); }
	bool InPL(Actor a) { return InBox(a, 2600, 32, 2984, 352); }

	Actor Make(class<Actor> what, double x, double y, double ang = 0, double z = 0)
	{
		Actor a = Actor.Spawn(what, (x, y, z));
		a.angle = ang;
		made.Push(a);
		return a;
	}

	void ClearMade()
	{
		for (int i = 0; i < made.Size(); i++) if (made[i]) made[i].Destroy();
		made.Clear();
		for (int i = 0; i < level.sectors.Size(); i++) level.sectors[i].SoundTarget = null;
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		if (e.Thing && e.Thing is "DoomImpBall" && Testing())
		{
			balls.Push(e.Thing);
			ballX.Push(e.Thing.pos.x); ballY.Push(e.Thing.pos.y); ballDone.Push(false);
			ballsSeen++;
			Actor by = e.Thing.target;
			Console.Printf("AJARTEST info ball t=%d at (%.1f,%.1f) moving (%.1f,%.1f) thrown by %s at (%.1f,%.1f)", tic, e.Thing.pos.x, e.Thing.pos.y,
				e.Thing.vel.x, e.Thing.vel.y, by ? by.GetClassName() .. "" : "none", by ? by.pos.x : 0, by ? by.pos.y : 0);
		}
	}

	override void WorldThingDamaged(WorldEvent e)
	{
		if (e.Thing && e.Thing.player && Testing())
		{
			playerHurt++;
			Console.Printf("AJARTEST info player hurt t=%d by %s via %s, %d", tic,
				e.DamageSource ? e.DamageSource.GetClassName() .. "" : "none",
				e.Inflictor ? e.Inflictor.GetClassName() .. "" : "none", e.Damage);
		}
	}

	// where each imp's fireball was last seen before it burst
	void BallTick()
	{
		for (int i = 0; i < balls.Size(); i++)
		{
			if (ballDone[i]) continue;
			if (balls[i] && !balls[i].InStateSequence(balls[i].CurState, balls[i].ResolveState("Death"))) { ballX[i] = balls[i].pos.x; ballY[i] = balls[i].pos.y; }
			else { ballEndX.Push(ballX[i]); ballEndY.Push(ballY[i]); ballDone[i] = true; Console.Printf("AJARTEST info ball %d burst t=%d at (%.1f,%.1f)", i, tic, ballX[i], ballY[i]); }
		}
	}

	override void WorldTick()
	{
		tic++;
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		int t = tic;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (t == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			let it = ThinkerIterator.Create("Actor");      // the map's own monsters are for play by hand
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
			Watch(mo, "player");
		}
		WatchTick();
		BallTick();
		if (mode == 1) Walking(mo, t);
		else if (mode == 2) Views(mo, t);
		else if (mode == 3) Shots(mo, t);
		else if (mode == 4) Monsters(mo, t);
		else if (mode == 5) SoundAndThings(mo, t);
	}

	// --- MODE=1: walking ------------------------------------------------------
	int eastIn, eastOut, westIn, westOut;

	void Walking(Actor mo, int t)
	{
		let w = WatchOf(mo);
		// A to B, the plain face: walking, running, at a slant
		if (t == 10) Pose(mo, 192, 200, 90);
		Go(mo, t, 10, 30, WALK);
		if (t == 45) Check("plainAToB_walk", InB(mo) && w.Jumps() == 0 && mo.angle == 90, mo);
		if (t == 50) Pose(mo, 192, 150, 90);
		Go(mo, t, 50, 20, RUN);
		if (t == 75) Check("plainAToB_run", InB(mo) && w.Jumps() == 0, mo);
		if (t == 80) Pose(mo, 75, 150, 60);
		Go(mo, t, 80, 35, WALK);
		if (t == 120) Check("plainAToB_slant", InB(mo) && w.Jumps() == 0 && mo.angle == 60, mo);
		// B to C, the odd face
		if (t == 130) Pose(mo, 192, 520, 270);
		Go(mo, t, 130, 30, WALK);
		if (t == 165) Check("walkBToC", InC(mo) && w.Jumps() == 1 && CrossedRight(w, 0, 401, 402, "walkBToC"), mo);
		if (t == 170) Pose(mo, 192, 560, 270);
		Go(mo, t, 170, 20, RUN);
		if (t == 195) Check("runBToC", InC(mo) && w.Jumps() == 2 && CrossedRight(w, 1, 401, 402, "runBToC"), mo);
		if (t == 200) Pose(mo, 280, 520, 240);
		Go(mo, t, 200, 30, WALK);
		if (t == 235) Check("slantBToC", InC(mo) && w.Jumps() == 3 && CrossedRight(w, 2, 401, 402, "slantBToC"), mo);
		if (t == 240) Pose(mo, 192, 520, 90);
		Go(mo, t, 240, 30, WALK, true);
		if (t == 275) Check("backBToC", InC(mo) && w.Jumps() == 4 && CrossedRight(w, 3, 401, 402, "backBToC") && mo.angle == 90, mo);
		if (t == 280) Pose(mo, 81, 560, 300);
		Go(mo, t, 280, 20, RUN);
		if (t == 305) Check("runSlantBToC", InC(mo) && w.Jumps() == 5 && CrossedRight(w, 4, 401, 402, "runSlantBToC"), mo);
		// C back through its opening: out of the doorway into B
		if (t == 310) Pose(mo, 192, 1400, 90);
		Go(mo, t, 310, 30, WALK);
		if (t == 345) Check("walkCToB", InB(mo) && w.Jumps() == 6 && CrossedRight(w, 5, 402, 401, "walkCToB"), mo);
		if (t == 350) Pose(mo, 192, 1400, 90);
		Go(mo, t, 350, 20, RUN);
		if (t == 375) Check("runCToB", InB(mo) && w.Jumps() == 7 && CrossedRight(w, 6, 402, 401, "runCToB"), mo);
		// the turn-round: A into B, turn, back the same way
		if (t == 380) Pose(mo, 192, 250, 90);
		Go(mo, t, 380, 25, WALK);
		if (t == 410) { Check("turnRound_inB", InB(mo) && w.Jumps() == 7, mo); mo.angle = 270; }
		Go(mo, t, 410, 30, WALK);
		if (t == 445) Check("turnRound_inC", InC(mo) && w.Jumps() == 8 && CrossedRight(w, 7, 401, 402, "turnRound"), mo);

		// the longer way back: 8 a tic, P to Q and Q to P
		if (t == 450) { Pose(mo, 896, 176, 0); eastIn = eastOut = westIn = westOut = 0; }
		Go(mo, t, 450, 50, 8);
		if (t > 450 && t <= 500)
		{
			if (!eastIn && mo.pos.x >= 960) eastIn = t;
			if (!eastOut && mo.pos.x >= 1216) eastOut = t;
		}
		if (t == 505)
		{
			Console.Printf("AJARTEST info longWayEast: x 960 to 1216 in %d tics at 8 a tic", eastOut - eastIn);
			Check("longWayEast", w.Jumps() == 8 && abs(eastOut - eastIn - 32) <= 1 && mo.pos.x > 1216, mo);
		}
		if (t == 510) Pose(mo, 1296, 176, 180);
		Go(mo, t, 510, 160, 8);
		if (t > 510 && t <= 670)
		{
			if (!westIn && (w.Jumps() >= 9 || mo.pos.x <= 1216)) westIn = t;    // at the odd face or past it
			if (westIn && !westOut && mo.pos.y < 300 && mo.pos.x <= 960) westOut = t;
		}
		if (t == 675)
		{
			Console.Printf("AJARTEST info longWayWest: x 1216 to 960 in %d tics at 8 a tic (two crossings)", westOut - westIn);
			Check("longWayWest", w.Jumps() == 10 && abs(westOut - westIn - 128) <= 1 && InBox(mo, 800, 96, 960, 256)
				&& CrossedRight(w, 8, 411, 413, "longWayWest_intoX") && CrossedRight(w, 9, 414, 412, "longWayWest_outOfX"), mo);
		}

		// bigger inside: the hall into R, R out to the hall, round the booth, into it from the back
		if (t == 680) Pose(mo, 2020, 150, 90);
		Go(mo, t, 680, 30, WALK);
		if (t == 715) Check("hallIntoR", InR(mo) && w.Jumps() == 11 && CrossedRight(w, 10, 421, 422, "hallIntoR"), mo);
		if (t == 720) Pose(mo, 2084, 2600, 270);
		Go(mo, t, 720, 30, WALK);
		if (t == 755) Check("rOutToHall", InHall(mo) && w.Jumps() == 12 && CrossedRight(w, 11, 422, 421, "rOutToHall"), mo);
		if (t == 760) Pose(mo, 1910, 250, 90);
		Go(mo, t, 760, 30, 8);
		if (t == 795) { Check("roundTheBooth_west", w.Jumps() == 12 && mo.pos.y > 480 && abs(mo.pos.x - 1910) < 0.01, mo); mo.angle = 0; }
		Go(mo, t, 795, 30, 8);
		if (t == 830) Check("roundTheBooth_north", w.Jumps() == 12 && mo.pos.x > 2120 && mo.pos.y > 480, mo);
		if (t == 835) Pose(mo, 2020, 560, 270);
		Go(mo, t, 835, 20, 8);
		if (t == 860) Check("intoTheBoothFromBehind", InBooth(mo) && w.Jumps() == 12, mo);
		Go(mo, t, 860, 25, 8);
		if (t == 890) Check("boothFrontPlainFromInside", InHall(mo) && w.Jumps() == 12, mo);

		// on the line: standing exactly on the odd face, and astride it
		if (t == 900) Pose(mo, 192, 368, 270);
		if (t == 935) Check("standOnTheLine", w.Jumps() == 12 && mo.pos.y == 368, mo);
		Go(mo, t, 935, 10, 1);
		if (t == 950) Check("offTheLineSouthToC", InC(mo) && w.Jumps() == 13, mo);
		if (t == 955) Pose(mo, 192, 368, 90);
		Go(mo, t, 955, 10, 1);
		if (t == 970) Check("offTheLineNorthStaysInB", InB(mo) && w.Jumps() == 13, mo);
		if (t == 975) Pose(mo, 192, 360, 90);       // in the opening, its box 8 over the odd face
		if (t == 1010) Check("astridePlainSideStill", w.Jumps() == 13 && mo.pos.y == 360, mo);
		Go(mo, t, 1010, 10, WALK);
		if (t == 1025) Check("astridePlainSideOnIntoB", InB(mo) && w.Jumps() == 13, mo);
		if (t == 1030) Pose(mo, 192, 376, 270);     // in B, its box 8 over the odd face
		if (t == 1065) Check("astrideOddSideStill", w.Jumps() == 13 && mo.pos.y == 376, mo);
		Go(mo, t, 1065, 10, WALK);
		if (t == 1080) Check("astrideOddSideOnIntoC", InC(mo) && w.Jumps() == 14 && CrossedRight(w, 13, 401, 402, "astrideOddSide"), mo);

		// a turned far side: the odd face pointed (Line_SetPortalTarget, as a hung
		// door does it) at C2's opening, in C2's west wall; then back to C
		if (t == 1085) { level.ExecuteSpecial(107 /* Line_SetPortalTarget */, null, null, false, 401, 403); Pose(mo, 192, 520, 270); }
		Go(mo, t, 1086, 30, WALK);
		if (t == 1120) Check("turnedBToC2", InC2(mo) && w.Jumps() == 15 && CrossedRight(w, 14, 401, 403, "turnedBToC2") && mo.angle == 0, mo);
		if (t == 1125) Pose(mo, 81, 560, 300);
		Go(mo, t, 1125, 20, RUN);
		if (t == 1150) Check("turnedRunSlantBToC2", InC2(mo) && w.Jumps() == 16 && CrossedRight(w, 15, 401, 403, "turnedRunSlantBToC2"), mo);
		if (t == 1155) Pose(mo, 200, 2160, 180);
		Go(mo, t, 1155, 30, WALK);
		if (t == 1190) Check("turnedC2ToB", InB(mo) && w.Jumps() == 17 && CrossedRight(w, 16, 403, 401, "turnedC2ToB") && mo.angle == 90, mo);
		if (t == 1195) { level.ExecuteSpecial(107, null, null, false, 401, 402); Pose(mo, 192, 520, 270); }
		Go(mo, t, 1196, 30, WALK);
		if (t == 1230) Check("pointedBackBToC", InC(mo) && w.Jumps() == 18 && CrossedRight(w, 17, 401, 402, "pointedBackBToC"), mo);
		if (t == 1235) Console.Printf("AJARTEST walkingDone=1");
	}

	// --- MODE=2: views (tools/smoke_ONESIDE_2.cfg shoots every 40 tics) ------
	void Views(Actor mo, int t)
	{
		static const double views[] = {
			192, 150, 90, 0,        // 0 A: the doorway, B beyond
			330, 200, 120, 0,       // 1 A at a slant
			192, 336, 90, 0,        // 2 A close to the mouth
			192, 560, 270, 0,       // 3 B looking back: C
			320, 520, 225, 0,       // 4 B at a slant
			192, 390, 270, 0,       // 5 B close to the odd face
			192, 368, 270, 0,       // 6 exactly on the odd face, looking south
			192, 368, 90, 0,        // 7 exactly on it, looking north into B
			192, 360, 270, 0,       // 8 in the opening, looking south into A
			192, 1350, 90, 0,       // 9 C: its opening, B beyond
			192, 1510, 90, 0,       // 10 C close
			320, 1330, 120, 0,      // 11 C at a slant
			1300, 176, 180, 0,      // 12 Q looking back west: the long X
			1000, 176, 0, 0,        // 13 the corridor east: Q plain
			880, 1832, 180, 0,      // 14 X's west end: out of the doorway, west to P
			2020, 150, 90, 0,       // 15 the hall: the booth's face, R in it
			1830, 190, 40, 0,       // 16 the booth from the hall at a slant
			2084, 2620, 270, 0,     // 17 R: its way out, the hall
			2020, 580, 270, 0,      // 18 the booth's back: small, the hall through its front
			2792, 150, 90, 0,       // 19 PL: MR and its monsters
			2792, 600, 270, 0,      // 20 MR looking south: E
			2700, 560, 250, 0,      // 21 MR at a slant
			192, 368.5, 270, 0,     // 22 half a unit off the odd face, in B, looking at it
			192, 369, 270, 0,       // 23 one unit off
			192, 370, 270, 0,       // 24 two
			192, 372, 270, 0,       // 25 four
			205, 380, 250, 0,       // 26 twelve off, at a slant
			192, 368, 300, 0,       // 27 exactly on it, at a slant
			192, 520, 270, 0        // 28 the automap (the cfg opens it), from B
		};
		if (t == 2)
		{
			for (int i = 0; i < 3; i++) Make("DoomImp", 2680 + 112 * i, 640, 270);
			Make("OneSideDummy", 100, 1300);      // something in C, A and B to tell them by
			Make("OneSideDummy", 100, 120);
			Make("Column", 300, 600);
			mo.GiveInventoryType("Allmap");
		}
		int i = t / 40;
		if (i >= views.Size() / 4) return;
		Pose(mo, views[i * 4], views[i * 4 + 1], views[i * 4 + 2]);
		mo.pitch = views[i * 4 + 3];
		if (t % 40 == 0) Console.Printf("AJARTEST view=%d at (%.0f,%.0f) facing %.0f", i, views[i * 4], views[i * 4 + 1], views[i * 4 + 2]);
	}

	// --- MODE=3: shots --------------------------------------------------------
	// dummies: 0 A, 1 B, 2 C, 3 C on the slant, 4 E, 5 PL, 6 MR, 7 R, 8 the booth
	Array<OneSideDummy> dummies;
	Actor missile;
	Vector3 missileLast;

	void Dummy(double x, double y) { dummies.Push(OneSideDummy(Make("OneSideDummy", x, y))); }

	void Zero()
	{
		for (int i = 0; i < dummies.Size(); i++) if (dummies[i]) { dummies[i].hits = 0; dummies[i].by = ""; }
	}

	string Hit()
	{
		static const string names[] = { "A", "B", "C", "Cslant", "E", "PL", "MR", "R", "booth" };
		string s = "";
		for (int i = 0; i < dummies.Size(); i++)
			if (dummies[i] && dummies[i].hits) s = s .. names[i] .. "(" .. dummies[i].hits .. " by " .. dummies[i].by .. ") ";
		return s == "" ? "nothing" : s;
	}

	void Bullet(Actor mo, string what)
	{
		Zero();
		Actor puff;
		int dmg;
		[puff, dmg] = mo.LineAttack(mo.angle, 4096, 0, 5, 'Hitscan', "BulletPuff");
		Console.Printf("AJARTEST info %s: fired from (%.1f,%.1f) facing %.1f, hit %s, puff %s", what, mo.pos.x, mo.pos.y, mo.angle, Hit(),
			puff ? String.Format("(%.1f,%.1f,%.1f)", puff.pos.x, puff.pos.y, puff.pos.z) : "none");
	}

	void Fire(Actor mo, class<Actor> what)
	{
		Zero();
		Vector2 at = mo.pos.xy + Actor.AngleToVector(mo.angle, 20);
		missile = Actor.Spawn(what, (at, 32));
		missile.target = mo;
		missile.angle = mo.angle;
		missile.vel = (Actor.AngleToVector(mo.angle, missile.speed), 0);
		missileLast = missile.pos;
	}

	void MissileTick()
	{
		if (missile && !missile.InStateSequence(missile.CurState, missile.ResolveState("Death"))) missileLast = missile.pos;
	}

	Actor thrower;

	void ShotCase(Actor mo, int t, int at, double x, double y, double ang, int kind, string what, int want)
	{
		if (t == at) Pose(mo, kind == 3 ? 330 : x, kind == 3 ? 650 : y, ang);
		if (t == at + 2)
		{
			if (kind == 0) Bullet(mo, what);
			else if (kind == 3)
			{
				// an imp's own throw (P_SpawnMissile), at the dummy in A, straight south
				thrower = Make("DoomImp", x, y, ang);
				Zero();
				missile = thrower.SpawnMissile(dummies[0], "DoomImpBall");
				Console.Printf("AJARTEST info %s: the imp at (%.1f,%.1f), its fireball put at (%.1f,%.1f)", what, x, y, missile.pos.x, missile.pos.y);
			}
			else if (kind == 4)
			{
				Zero();
				missile = mo.SpawnPlayerMissile("Rocket", ang);
				Console.Printf("AJARTEST info %s: the player at (%.1f,%.1f), the rocket put at (%.1f,%.1f)", what, x, y, missile.pos.x, missile.pos.y);
			}
			else Fire(mo, kind == 1 ? "Rocket" : "DoomImpBall");
		}
		if (t == at + 85)
		{
			if (kind) Console.Printf("AJARTEST info %s: %s fired from (%.1f,%.1f) facing %.1f, hit %s, burst at (%.1f,%.1f,%.1f)", what,
				kind == 1 || kind == 4 ? "a rocket" : "an imp's fireball", x, y, ang, Hit(), missileLast.x, missileLast.y, missileLast.z);
			int others = 0;
			for (int i = 0; i < dummies.Size(); i++) if (dummies[i] && i != want) others += dummies[i].hits;
			Check(what, dummies[want] && dummies[want].hits > 0 && others == 0, mo);
			if (thrower) thrower.Destroy();
		}
	}

	void Shots(Actor mo, int t)
	{
		if (t == 2)
		{
			Dummy(192, 100); Dummy(192, 600); Dummy(192, 1300);
			// a shot fired from (280, 520) at 240 crosses the odd face at x 192.2 and goes on into C
			Vector2 slant = (192.2, 1536) + Actor.AngleToVector(240, 340);
			Dummy(slant.x, slant.y);
			Dummy(2792, 1500); Dummy(2792, 100); Dummy(2792, 600);
			Dummy(2084, 2700); Dummy(2020, 400);
		}
		MissileTick();
		static const double cases[] = {
			// x, y, facing, kind (0 hitscan, 1 rocket, 2 imp's fireball), which dummy should be hit
			192, 520, 270, 0, 2,        // B to C
			192, 250, 90, 0, 1,         // A to B
			192, 1450, 90, 0, 1,        // C to B
			280, 520, 240, 0, 3,        // B to C at a slant
			192, 520, 270, 1, 2,
			192, 520, 270, 2, 2,
			192, 250, 90, 1, 1,
			192, 250, 90, 2, 1,
			192, 1450, 90, 1, 1,
			192, 1450, 90, 2, 1,
			280, 520, 240, 1, 3,
			2792, 150, 90, 0, 6,        // PL into MR, the plain face
			2792, 560, 270, 0, 4,       // MR to E, the odd face (the player stands in for a monster)
			2792, 560, 270, 2, 4,
			2020, 150, 90, 0, 7,        // the hall into R
			2020, 150, 90, 1, 7,
			// thrown by the engine's own spawning (a missile is put half a step ahead), from close to the odd face
			192, 400, 270, 3, 2,       // an imp 32 from it
			192, 372, 270, 3, 0,       // an imp 4 from it: the ball is put beyond the line without crossing it
			192, 400, 270, 4, 2,       // the player 32 from it, a rocket
			192, 372, 270, 4, 0,       // the player 4 from it: the same
			192, 372, 270, 0, 2        // a hitscan from 4: a trace, not put ahead
		};
		static const string names[] = {
			"hitscanBToC", "hitscanAToB", "hitscanCToB", "hitscanSlantBToC", "rocketBToC", "impBallBToC", "rocketAToB", "impBallAToB",
			"rocketCToB", "impBallCToB", "rocketSlantBToC", "hitscanPLToMR", "hitscanMRToE", "impBallMRToE", "hitscanHallToR", "rocketHallToR",
			"impThrowsFrom32", "impThrowsFrom4_intoA", "playerRocketFrom32", "playerRocketFrom4_intoA", "hitscanFrom4" };
		for (int i = 0; i < 21; i++)
			ShotCase(mo, t, 10 + 90 * i, cases[i * 5], cases[i * 5 + 1], cases[i * 5 + 2], int(cases[i * 5 + 3]), names[i], int(cases[i * 5 + 4]));
		if (t == 10 + 90 * 21) Console.Printf("AJARTEST shotsDone=1");
	}

	// --- MODE=4: monsters -----------------------------------------------------
	Array<Actor> imps;

	void PlaceImps(Array<double> at)
	{
		imps.Clear();
		for (int i = 0; i + 2 < at.Size(); i += 3) imps.Push(Make("DoomImp", at[i], at[i + 1], at[i + 2]));
	}

	int Woken()
	{
		int n = 0;
		for (int i = 0; i < imps.Size(); i++) if (imps[i] && imps[i].target == players[consoleplayer].mo) n++;
		return n;
	}

	int Seeing()
	{
		int n = 0;
		for (int i = 0; i < imps.Size(); i++) if (imps[i] && imps[i].CheckSight(players[consoleplayer].mo)) n++;
		return n;
	}

	string Where(Actor a)
	{
		if (!a) return "gone";
		string room = InA(a) ? "A" : InB(a) ? "B" : InC(a) ? "C" : InMR(a) ? "MR" : InE(a) ? "E" : InPL(a) ? "PL" : "elsewhere";
		return String.Format("%s (%.0f,%.0f)", room, a.pos.x, a.pos.y);
	}

	// one sight case: imps placed, the player placed, after 70 tics how many
	// woke for the player and how many have the engine's sight of the player
	void SightCase(Actor mo, int t, int at, Array<double> where, double px, double py, double pang, string what, int want)
	{
		if (t == at)
		{
			ClearMade();
			mo.player.cheats &= ~CF_NOTARGET;
			Pose(mo, px, py, pang);
			PlaceImps(where);
		}
		if (t == at + 70)
		{
			int woke = Woken(), seen = Seeing();
			Console.Printf("AJARTEST info %s: %d imps, %d woke for the player, %d have sight of the player", what, imps.Size(), woke, seen);
			Check(what, woke == want && seen == want, mo);
		}
	}

	Actor walker, chaser;
	int ballsBefore, hurtBefore;

	void Monsters(Actor mo, int t)
	{
		Array<double> one, three;
		// imps asleep facing the doorway, the player in front of them as the view goes
		one.Clear(); one.Push(192); one.Push(560); one.Push(270);
		SightCase(mo, t, 10, one, 192, 1350, 90, "impInBSeesPlayerInC", 0);
		SightCase(mo, t, 90, one, 192, 250, 90, "impInBSeesPlayerInA", 1);
		one.Clear(); one.Push(192); one.Push(150); one.Push(90);
		SightCase(mo, t, 170, one, 192, 560, 270, "impInASeesPlayerInB", 1);
		one.Clear(); one.Push(192); one.Push(1350); one.Push(90);
		SightCase(mo, t, 250, one, 192, 560, 270, "impInCSeesPlayerInB", 0);
		// bay 5: three imps in MR, the player in PL before the doorway
		three.Clear();
		for (int i = 0; i < 3; i++) { three.Push(2744 + 48 * i); three.Push(640); three.Push(270); }
		Line odd = FindLine(431);
		SightCase(mo, t, 330, three, 2792, 100, 90, "oneWaySight_blind", 0);
		if (t == 410) odd.flags &= ~Line.ML_BLOCKSIGHT;
		SightCase(mo, t, 410, three, 2792, 100, 90, "oneWaySight_withoutBlocksight", 3);
		// ... and so they fight: the player stays (buddha), what do their fireballs do?
		if (t == 480) { mo.player.cheats &= ~CF_GODMODE; mo.player.cheats |= CF_BUDDHA; ballsBefore = ballsSeen; hurtBefore = playerHurt; ballEndX.Clear(); ballEndY.Clear(); }
		if (t == 700)
		{
			int inE = 0, inPL = 0, elsewhere = 0;
			for (int i = 0; i < ballEndX.Size(); i++)
			{
				Vector2 p = (ballEndX[i], ballEndY[i]);
				if (p.x > 2600 && p.x < 2984 && p.y > 1400 && p.y < 1736) inE++;
				else if (p.x > 2600 && p.x < 2984 && p.y > 32 && p.y < 352) inPL++;
				else elsewhere++;
			}
			string at = "";
			for (int i = 0; i < ballEndX.Size(); i++) at = at .. String.Format(" (%.0f,%.0f)", ballEndX[i], ballEndY[i]);
			Console.Printf("AJARTEST info oneWaySight_fight: in 220 tics %d fireballs; burst in E %d, in PL %d, elsewhere %d (at%s); player hurt %d times; imps at %s, %s, %s",
				ballsSeen - ballsBefore, inE, inPL, elsewhere, at, playerHurt - hurtBefore, Where(imps[0]), Where(imps[1]), Where(imps[2]));
			Check("oneWaySight_theyWalkIntoE", (InE(imps[0]) || InE(imps[1]) || InE(imps[2])) && !InPL(imps[0]) && !InPL(imps[1]) && !InPL(imps[2]), mo);
			mo.player.cheats &= ~CF_BUDDHA; mo.player.cheats |= CF_GODMODE;
			mo.health = 100;
			mo.player.health = 100;
		}
		// with blocksight again: the player shoots one; where does it go?
		if (t == 705)
		{
			odd.flags |= Line.ML_BLOCKSIGHT;
			ClearMade();
			Pose(mo, 2792, 100, 90);
			PlaceImps(three);
			ballsBefore = ballsSeen;
			ballEndX.Clear(); ballEndY.Clear();
		}
		if (t == 710) mo.LineAttack(mo.angle, 4096, 0, 5, 'Hitscan', "BulletPuff");    // at the middle imp, 540 ahead
		if (t == 1010)
		{
			Actor shot = imps[1];
			Console.Printf("AJARTEST info oneWaySight_shotImp: health %d, woke %d, fireballs %d, imps at %s, %s, %s", shot ? shot.health : -1, Woken(), ballsSeen - ballsBefore,
				Where(imps[0]), Where(imps[1]), Where(imps[2]));
			Check("oneWaySight_shotImpGoesIntoE", shot && shot.health < 60 && InE(shot) && InMR(imps[0]) && InMR(imps[2]), mo);
		}

		// walking through each face, as the player does (moved by its speed each tic)
		if (t == 1015) { ClearMade(); mo.player.cheats |= CF_NOTARGET; walker = Make("DoomImp", 192, 520, 270); Watch(walker, "imp"); }
		Go(walker, t, 1016, 30, WALK);
		if (t == 1050) Check("impWalksBToC", InC(walker) && WatchOf(walker).Jumps() == 1 && CrossedRight(WatchOf(walker), 0, 401, 402, "impWalksBToC"), walker);
		if (t == 1055) { walker.SetOrigin((192, 1400, 0), false); walker.angle = 90; WatchOf(walker).lastPos = walker.pos; WatchOf(walker).lastAngle = 90; }
		Go(walker, t, 1056, 30, WALK);
		if (t == 1090) Check("impWalksCToB", InB(walker) && WatchOf(walker).Jumps() == 2 && CrossedRight(WatchOf(walker), 1, 402, 401, "impWalksCToB"), walker);
		if (t == 1095) { walker.SetOrigin((192, 200, 0), false); walker.angle = 90; WatchOf(walker).lastPos = walker.pos; WatchOf(walker).lastAngle = 90; }
		Go(walker, t, 1096, 30, WALK);
		if (t == 1130) Check("impWalksAToB", InB(walker) && WatchOf(walker).Jumps() == 2, walker);
		if (t == 1135) { walker.SetOrigin((2020, 150, 0), false); walker.angle = 90; WatchOf(walker).lastPos = walker.pos; WatchOf(walker).lastAngle = 90; }
		Go(walker, t, 1136, 30, WALK);
		if (t == 1170) Check("impWalksHallToR", InR(walker) && WatchOf(walker).Jumps() == 3 && CrossedRight(WatchOf(walker), 2, 421, 422, "impWalksHallToR"), walker);

		// a monster asleep astride the odd face, and exactly on it
		if (t == 1175) { ClearMade(); walker = Make("DoomImp", 192, 376, 270); Watch(walker, "imp astride"); }
		if (t == 1215) Check("impAstrideStaysInB", walker && walker.pos.y == 376 && WatchOf(walker).Jumps() == 0, walker);
		if (t == 1220) { ClearMade(); walker = Make("DoomImp", 192, 368, 270); Watch(walker, "imp on the line"); }
		if (t == 1260) Check("impOnTheLineStays", walker && walker.pos.y == 368 && WatchOf(walker).Jumps() == 0, walker);

		// left to itself: an imp in B that knows of the player in A, just beyond the plain face
		if (t == 1265)
		{
			ClearMade();
			mo.player.cheats &= ~CF_NOTARGET;
			mo.player.cheats &= ~CF_GODMODE; mo.player.cheats |= CF_BUDDHA;
			Pose(mo, 192, 250, 270);
			chaser = Make("DoomImp", 192, 560, 270);
			Watch(chaser, "chaser");
			chaser.target = mo;
			chaser.SetState(chaser.SeeState);
			ballsBefore = ballsSeen; hurtBefore = playerHurt;
			ballEndX.Clear(); ballEndY.Clear();
		}
		if (t == 1565)
		{
			int inC = 0;
			for (int i = 0; i < ballEndX.Size(); i++) if (ballEndX[i] > 0 && ballEndX[i] < 384 && ballEndY[i] > 1200 && ballEndY[i] < 1536) inC++;
			Console.Printf("AJARTEST info chaseFromB: after 300 tics the imp is in %s, crossed %d times; %d fireballs, %d burst in C; player hurt %d times",
				Where(chaser), chaser ? WatchOf(chaser).Jumps() : -1, ballsSeen - ballsBefore, inC, playerHurt - hurtBefore);
			Check("chaseFromB_endsInC", chaser && InC(chaser), mo);
			mo.player.cheats &= ~CF_BUDDHA; mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			Console.Printf("AJARTEST monstersDone=1");
		}
	}

	// --- MODE=5: sound, and things on the line ---------------------------------
	Actor corpse, clip, clip2;

	void SoundCase(Actor mo, int t, int at, double px, double py, Array<double> where, string what, int want)
	{
		if (t == at)
		{
			ClearMade();
			mo.player.cheats &= ~CF_NOTARGET;
			Pose(mo, px, py, 0);
			PlaceImps(where);
		}
		if (t == at + 5) mo.SoundAlert(mo);       // what a shot does (P_NoiseAlert)
		if (t == at + 40)
		{
			int heard = 0;
			for (int i = 0; i < imps.Size(); i++) if (imps[i] && imps[i].CurSector.SoundTarget == mo) heard++;
			int woke = Woken(), seen = Seeing();
			Console.Printf("AJARTEST info %s: %d imps, %d in a sector the sound reached, %d woke, %d have sight of the player", what, imps.Size(), heard, woke, seen);
			Check(what, heard == want && woke == want && seen == 0, mo);
		}
	}

	void SoundAndThings(Actor mo, int t)
	{
		Array<double> a;
		// imps where they do not have sight of the player, facing away
		a.Clear(); a.Push(360); a.Push(60); a.Push(0);
		SoundCase(mo, t, 10, 300, 600, a, "shotInBWakesA", 1);
		a.Clear(); a.Push(40); a.Push(1230); a.Push(180);
		SoundCase(mo, t, 60, 300, 600, a, "shotInBWakesC", 1);
		a.Clear(); a.Push(40); a.Push(400); a.Push(180);
		SoundCase(mo, t, 110, 300, 1300, a, "shotInCWakesB", 1);
		SoundCase(mo, t, 160, 300, 100, a, "shotInAWakesB", 1);
		a.Clear(); a.Push(2640); a.Push(780); a.Push(180);
		SoundCase(mo, t, 210, 2950, 60, a, "shotInPLWakesMR", 1);
		a.Clear(); a.Push(2640); a.Push(1430); a.Push(180);
		SoundCase(mo, t, 260, 2950, 60, a, "shotInPLWakesE", 1);
		if (t == 305) { ClearMade(); mo.player.cheats |= CF_NOTARGET; Pose(mo, 300, 100, 90); }

		// a corpse on the odd face, then pushed through it
		if (t == 310) { corpse = Make("DoomImp", 192, 372, 270); corpse.DamageMobj(null, null, 1000, 'None'); Watch(corpse, "corpse"); }
		if (t == 380) Check("corpseAstrideStays", corpse && corpse.health <= 0 && abs(corpse.pos.y - 372) < 0.01 && WatchOf(corpse).Jumps() == 0, corpse);
		Go(corpse, t, 381, 12, 6);              // pushed south, the way it faces
		if (t == 450) Check("corpsePushedIntoC", InC(corpse) && WatchOf(corpse).Jumps() == 1 && CrossedRight(WatchOf(corpse), 0, 401, 402, "corpsePushed"), corpse);
		// a dropped thing tossed through each face
		if (t == 455) { clip = Make("Clip", 192, 430, 270, 24); clip.vel = (0, -6, 3); Watch(clip, "clip B"); }
		if (t == 520) Check("itemTossedBToC", InC(clip) && WatchOf(clip).Jumps() == 1, clip);
		if (t == 525) { clip2 = Make("Clip", 192, 300, 90, 24); clip2.vel = (0, 6, 3); Watch(clip2, "clip A"); }
		if (t == 590) Check("itemTossedAToB", InB(clip2) && WatchOf(clip2).Jumps() == 0, clip2);
		// and one lying across the line, picked up from B
		if (t == 595) { clip = Make("Clip", 192, 369, 0); Watch(clip, "clip on line"); Pose(mo, 192, 470, 270); }
		Go(mo, t, 600, 9, WALK);
		if (t == 615) Check("itemAstrideLinePickedUpFromB", !clip && InB(mo), mo);
		// sound from the plain side into the odd face's far room, and a sealed room as the control
		a.Clear(); a.Push(40); a.Push(1230); a.Push(180);
		SoundCase(mo, t, 625, 300, 100, a, "shotInAWakesC", 1);
		a.Clear(); a.Push(3364); a.Push(1464); a.Push(180);
		SoundCase(mo, t, 675, 300, 600, a, "shotInBWakesSealedRoom", 0);
		if (t == 720) { ClearMade(); mo.player.cheats |= CF_NOTARGET; Console.Printf("AJARTEST soundAndThingsDone=1"); }
	}
}
