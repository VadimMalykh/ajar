// The pass lab's checks (map PASS, tools/map_pass.py; pass.zs; PLAN.md, "The
// pass lab"). MAP=PASS MODE=n tools/smoke.sh: 1 tracking, 2 registers,
// 3 the pumps, 4 the rest, 5 views (screenshots).
// Lines: frames 101..108; far sides 201 RED, 202 BLUE, 203 GREEN; the gate
// pair 701 (GA's north wall) and 702 (GB's east wall); the one-sided
// doorway's odd face 711 (B's side) and C's opening 712.
//
// What each portal does to T (the map's numbers, by the engine's rule
// dst.v2 + R(p - src.v1); T after one crossing from the identity, as
// (turn, shift x, shift y, height)):
//   101 -> RED        0,  -224,   352,    0      RED -> 101    0,  224, -352, 0
//   102 -> RED        0,   736,   352,    0      102 -> GREEN  0, -572,  352, 0
//   103 -> GREEN    270,  2544,  1788,    0      (a quarter turn: x' = y + 2544, y' = 1788 - x)
//   104 -> GREEN      0,  1928,   352,    0      104 -> BLUE   0, -522,  352, 0
//   106 -> 105        0,   800,     0,    0      105 -> 106    0, -800,    0, 0
//   107 -> 108        0,     0,   544, -128      108 -> 107    0,    0, -544, 128
//   701 -> 702      270,  7400,  9144,    0
//   711 -> 712        0,     0, -1200,    0      712 -> 711    0,    0, 1200, 0
//   GREEN by 103, then RED by 101: 270, 2896, 2012, 0

class PassDummy : Actor
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

class PassTest : EventHandler
{
	const WALK = 8.33;
	const RUN = 16.67;
	int tic, cur, tt;
	int checks, fails;
	AjarHandler h;
	AjarPassDouble dbl;
	AjarDoor red, green, blue;
	int seenCross;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "PASS"; }

	// --- the running order: each step is a stretch of tics ---------------------
	bool Seg(int n)
	{
		bool now = tic >= cur && tic < cur + n;
		if (now) tt = tic - cur;
		cur += n;
		return now;
	}
	bool At() { return Seg(1); }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}

	string TStr() { return String.Format("T(turn %.3f, shift %.4f %.4f, height %.4f)", dbl.tAng, dbl.tOff.x, dbl.tOff.y, dbl.tDz); }
	string PStr(Vector3 p) { return String.Format("(%.3f,%.3f,%.3f)", p.x, p.y, p.z); }

	bool TIs(double a, double x, double y, double z)
	{
		return abs(Actor.DeltaAngle(dbl.tAng, a)) < 1e-9 && abs(dbl.tOff.x - x) < 0.001 && abs(dbl.tOff.y - y) < 0.001 && abs(dbl.tDz - z) < 0.001;
	}
	bool TExactly(double a, double x, double y, double z) { return dbl.tAng == a && dbl.tOff.x == x && dbl.tOff.y == y && dbl.tDz == z; }

	// the double stands at T(player), facing as the player turned by T
	bool OnT(Actor mo)
	{
		return (dbl.pos - dbl.Apply(mo.pos)).Length() < 1e-6 && abs(Actor.DeltaAngle(dbl.angle, mo.angle + dbl.tAng)) < 1e-6;
	}

	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }

	void PoseF(Actor mo, double x, double y, double ang)
	{
		mo.SetOrigin((x, y, FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
		dbl.Posed(mo);
	}

	// every scripted step: on the tic of a crossing the double makes exactly the tic's move, turned by T
	Vector2 strideMove, strideDbl;
	int strideTic, strideCross, crossTics;
	double crossTicErr;
	void Stride(Actor mo, double speed, double off = 0)
	{
		mo.vel.xy = Actor.AngleToVector(mo.angle + off, speed);
		strideMove = AjarPassDouble.Rot(mo.vel.xy, dbl.tAng);
		strideDbl = dbl.pos.xy;
		strideTic = tic;
		strideCross = dbl.crossings;
	}
	void StrideCheck()
	{
		if (strideTic != tic - 1 || dbl.crossings == strideCross) return;
		double e = (dbl.pos.xy - (strideDbl + strideMove)).Length();
		crossTics++;
		crossTicErr = max(crossTicErr, e);
		if (e > 0.001) Console.Printf("AJARTEST info the double off its step at a crossing by %.6f (t=%d)", e, tic);
	}

	AjarDoor Leaf(int colour, int n)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.args[1] == colour && !n--) return d;
		return null;
	}

	void HangIn(AjarDoor d, int frameId)
	{
		AjarFrame f = h.FindFrame(frameId);
		if (!d || !f) { Console.Printf("AJARTEST info no door or no frame %d", frameId); return; }
		if (f.door == d) return;
		if (d.frame) h.Unhang(d.frame);
		if (f.door) h.Unhang(f);
		h.Hang(d, f);
	}

	AjarPassRegister Reg(int n)
	{
		let it = ThinkerIterator.Create("AjarPassRegister");
		AjarPassRegister r;
		while (r = AjarPassRegister(it.Next())) if (r.args[3] == n) return r;
		return null;
	}

	double DoorGap(int tag)
	{
		let it = level.CreateSectorTagIterator(tag);
		int i = it.Next();
		if (i < 0) return -1;
		Sector s = level.sectors[i];
		return s.ceilingplane.ZatPoint(s.centerspot) - s.floorplane.ZatPoint(s.centerspot);
	}

	// --- one walk: pose (or stay: x < -99999), walk n tics, and check -------------
	Vector3 cDbl;
	Vector2 cMove;
	int cCross;
	double cA, cDz;
	Vector2 cOff;

	void Walkthrough(Actor mo, string name, bool reset, double x, double y, double ang, double off, double speed, int n, int want,
		double ea = 0, double ex = 0, double ey = 0, double edz = 0, bool blocked = false)
	{
		if (At())
		{
			if (reset) dbl.Reset();
			if (x > -99999) PoseF(mo, x, y, ang);
			else { mo.angle = ang; mo.vel = (0, 0, 0); }
			cCross = dbl.crossings;
			cDbl = dbl.Apply(mo.pos);
			cMove = AjarPassDouble.Rot(Actor.AngleToVector(ang + off, speed) * n, dbl.tAng);
			cA = dbl.tAng; cOff = dbl.tOff; cDz = dbl.tDz;
		}
		if (Seg(n)) Stride(mo, speed, off);
		if (At())
		{
			mo.vel = (0, 0, 0);
			int crossed = dbl.crossings - cCross;
			bool tOk = want ? TIs(ea, ex, ey, edz) : (dbl.tAng == cA && dbl.tOff == cOff && dbl.tDz == cDz);
			Vector2 straight = cDbl.xy + cMove;
			double off2 = (dbl.pos.xy - straight).Length();
			Check(name, crossed == want && tOk && (blocked || off2 < 0.001) && OnT(mo),
				String.Format("crossed %d; %s; player %s, double %s, the straight walk ends at (%.3f,%.3f): off by %.6f; on T(player) %d",
				crossed, TStr(), PStr(mo.pos), PStr(dbl.pos), straight.x, straight.y, off2, OnT(mo)));
		}
	}

	// a stretch of standing still
	void Still(int n) { Seg(n); }

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			red = h.DoorOf(1); blue = h.DoorOf(2); green = h.DoorOf(3);
		}
		if (!dbl) dbl = AjarPassDouble.Get();
		if (!dbl) return;
		if (dbl.crossings != seenCross)
		{
			seenCross = dbl.crossings;
			Console.Printf("AJARTEST info cross n=%d t=%d from line %d; %s; player %s, double %s (floor under it %.3f)", dbl.crossings, tic,
				dbl.lastSrc ? dbl.lastSrc.Index() : -1, TStr(), PStr(mo.pos), PStr(dbl.pos), FloorAt(dbl.pos.xy));
		}
		StrideCheck();
		cur = 2;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode == 1) Tracking(mo);
		else if (mode == 2) Registers(mo);
		else if (mode == 3) Pumps(mo);
		else if (mode == 4) Rest(mo);
		else if (mode == 5) Views(mo);
		if (mode != 5 && tic == cur + 2)
			Console.Printf("AJARTEST passDone=1 checks=%d failed=%d", checks, fails);
	}

	// --- MODE=1: tracking --------------------------------------------------------
	void Tracking(Actor mo)
	{
		if (At())
		{
			Console.Printf("AJARTEST info portals in the map: %d", level.LinePortals.Size());
			// the double is ticked after the player: where it stands is this tic's
			Check("startsOnThePlayer", dbl.IsIdentity() && dbl.pos == mo.pos, String.Format("player %s, double %s", PStr(mo.pos), PStr(dbl.pos)));
			HangIn(red, 101);
		}
		// bay 1: RED in 101, every way through
		Walkthrough(mo, "red101_walk", true, 96, 200, 90, 0, WALK, 30, 1, 0, -224, 352, 0);
		Walkthrough(mo, "red101_run", true, 96, 150, 90, 0, RUN, 18, 1, 0, -224, 352, 0);
		Walkthrough(mo, "red101_strafe", true, 96, 200, 0, 90, WALK, 30, 1, 0, -224, 352, 0);
		Walkthrough(mo, "red101_back", true, 96, 200, 270, 180, WALK, 30, 1, 0, -224, 352, 0);
		Walkthrough(mo, "red101_slant30", true, 17.48, 200, 60, 0, WALK, 30, 1, 0, -224, 352, 0, true);   // (slides on the far recess's side: see crossingTicsExact)
		Walkthrough(mo, "red101_runSlant30", true, 174.52, 200, 120, 0, RUN, 16, 1, 0, -224, 352, 0);
		// ... and back through the same door: exactly nothing
		Walkthrough(mo, "red_backThroughSame", false, 320, 100, 270, 0, WALK, 30, 1, 0, 0, 0, 0);
		if (At()) Check("red_backThroughSame_exact", dbl.IsIdentity() && dbl.pos == mo.pos, TStr());
		// out by the door, on on foot: the offset stays
		Walkthrough(mo, "red101_again", true, 96, 200, 90, 0, WALK, 30, 1, 0, -224, 352, 0);
		Walkthrough(mo, "red_onOnFoot", false, -100000, 0, 90, 0, WALK, 18, 0);
		Walkthrough(mo, "red_onOnFootTurned", false, -100000, 0, 200, 0, WALK, 20, 0);
		// bay 2: GREEN and RED in 102
		if (At()) HangIn(green, 102);
		Walkthrough(mo, "green102_walk", true, 1056, 200, 90, 0, WALK, 30, 1, 0, -572, 352, 0);
		if (At()) HangIn(red, 102);
		Walkthrough(mo, "red102_walk", true, 1056, 200, 90, 0, WALK, 30, 1, 0, 736, 352, 0);

		// bay 3: GREEN in 103, a quarter turn
		if (At()) HangIn(green, 103);
		Walkthrough(mo, "green103_walk", true, 2400, 160, 0, 0, WALK, 30, 1, 270, 2544, 1788, 0);
		Walkthrough(mo, "green103_run", true, 2350, 160, 0, 0, RUN, 18, 1, 270, 2544, 1788, 0);
		Walkthrough(mo, "green103_strafe", true, 2400, 160, 90, -90, WALK, 30, 1, 270, 2544, 1788, 0);
		Walkthrough(mo, "green103_back", true, 2400, 160, 180, 180, WALK, 30, 1, 270, 2544, 1788, 0);
		Walkthrough(mo, "green103_slant30", true, 2400, 86.1, 30, 0, WALK, 30, 1, 270, 2544, 1788, 0, true);
		// then moves: the double's are the player's turned (a strafe right, a turn left and a walk)
		Walkthrough(mo, "green103_thenOn", true, 2400, 160, 0, 0, WALK, 30, 1, 270, 2544, 1788, 0);
		Walkthrough(mo, "turned_strafeRight", false, -100000, 0, 90, -90, 8, 8, 0);
		Walkthrough(mo, "turned_turnLeftWalk", false, -100000, 0, 180, 0, 8, 8, 0);
		Walkthrough(mo, "turned_backUp", false, -100000, 0, 270, 180, 8, 8, 0);
		// two different doors in a row: GREEN by 103, then RED by 101
		if (At()) HangIn(red, 101);
		Walkthrough(mo, "twoDoors_first", true, 2400, 160, 0, 0, WALK, 30, 1, 270, 2544, 1788, 0);
		Walkthrough(mo, "twoDoors_second", false, 96, 200, 90, 0, WALK, 30, 1, 270, 2896, 2012, 0);

		// bay 5: the TEAL leaves in 105 and 106
		if (At()) { HangIn(Leaf(8, 0), 105); HangIn(Leaf(8, 1), 106); }
		Walkthrough(mo, "teal106_east", true, 5250, 128, 0, 0, WALK, 30, 1, 0, 800, 0, 0);
		Walkthrough(mo, "teal_backThroughSame", false, -100000, 0, 180, 0, WALK, 20, 1, 0, 0, 0, 0);
		if (At()) Check("teal_backThroughSame_exact", dbl.IsIdentity() && dbl.pos == mo.pos, TStr());
		Walkthrough(mo, "teal105_west", true, 4800, 128, 180, 0, WALK, 30, 1, 0, -800, 0, 0);
		Walkthrough(mo, "teal_twoInFewTics_in", true, 5370, 128, 0, 0, WALK, 3, 1, 0, 800, 0, 0);
		Walkthrough(mo, "teal_twoInFewTics_out", false, -100000, 0, 180, 0, WALK, 3, 1, 0, 0, 0, 0);

		// bay 6: the ORANGE leaves in 107 and 108 (heights)
		if (At()) { HangIn(Leaf(9, 0), 107); HangIn(Leaf(9, 1), 108); }
		Walkthrough(mo, "orange107_downTheStair", true, 8096, 64, 90, 0, WALK, 70, 1, 0, 0, 544, -128);
		Walkthrough(mo, "orange_backThroughSame", false, -100000, 0, 270, 0, WALK, 20, 1, 0, 0, 0, 0);
		if (At()) Check("orange_backThroughSame_exact", dbl.IsIdentity() && dbl.pos == mo.pos, TStr());
		Walkthrough(mo, "orange108_upTheStair", true, 8096, 470, 270, 0, WALK, 75, 1, 0, 0, -544, 128);
		Walkthrough(mo, "orange107_run", true, 8096, 64, 90, 0, RUN, 36, 1, 0, 0, 544, -128);

		// bay 7: the building's own
		Walkthrough(mo, "gate701_walk", true, 8728, 128, 90, 0, WALK, 30, 1, 270, 7400, 9144, 0);
		Walkthrough(mo, "gate_backThroughSame", false, -100000, 0, 0, 0, WALK, 20, 1, 0, 0, 0, 0);
		Walkthrough(mo, "oneside_plainAToB", true, 9128, 128, 90, 0, WALK, 30, 0);
		Walkthrough(mo, "oneside_oddBToC", true, 9128, 400, 270, 0, WALK, 30, 1, 0, 0, -1200, 0);
		if (At()) Check("oneside_oddBToC_doubleInA", dbl.pos.x > 9000 && dbl.pos.x < 9256 && dbl.pos.y > 0 && dbl.pos.y < 256, PStr(dbl.pos));
		Walkthrough(mo, "oneside_CBackToB", true, 9128, 1300, 90, 0, WALK, 30, 1, 0, 0, 1200, 0);

		// on the line, and astride it: no false crossing
		if (At()) HangIn(red, 101);
		Walkthrough(mo, "onTheLine_still", true, 96, 336, 90, 0, 0, 35, 0);
		Walkthrough(mo, "onTheLine_stepOffBeyond", false, -100000, 0, 90, 0, 1, 10, 1, 0, -224, 352, 0);
		Walkthrough(mo, "onTheLine_stepOffBack", true, 96, 336, 270, 0, 1, 10, 0);
		Walkthrough(mo, "astride_still", true, 96, 330, 90, 0, 0, 35, 0);
		Walkthrough(mo, "astride_walkOn", false, -100000, 0, 90, 0, WALK, 10, 1, 0, -224, 352, 0);
		Walkthrough(mo, "astrideFarSide_still", true, 320, -10, 270, 0, 0, 35, 0);
		Walkthrough(mo, "astrideFarSide_walkOn", false, -100000, 0, 270, 0, WALK, 10, 1, 0, 224, -352, 0);
		if (At())
		{
			Console.Printf("AJARTEST info unexplained jumps %d, two crossings in a tic %d", dbl.unexplained, dbl.twoInOne);
			Check("crossingTicsExact", crossTics > 30 && crossTicErr < 0.001 && dbl.unexplained == 0,
				String.Format("%d crossings in a scripted step: on each the double moved the step's own move, off by %.6f at most", crossTics, crossTicErr));
		}
	}

	// --- MODE=2: registers -------------------------------------------------------
	void Registers(Actor mo)
	{
		if (At()) HangIn(red, 101);
		// over the plate without stopping
		Walkthrough(mo, "reg1_passOver_walk", true, 96, 200, 90, 0, 8, 52, 1, 0, -224, 352, 0);
		Still(40);
		if (At()) Check("reg1_passOverSignsNothing", !Reg(1).signed, PStr(dbl.pos));
		// RED: the double 96 in from the duty room's wall
		Walkthrough(mo, "reg1_walk", true, 96, 200, 90, 0, 8, 37, 1, 0, -224, 352, 0);
		Still(40);
		if (At())
		{
			let r = Reg(1);
			Check("reg1_signedByRED", r.signed && h.said == "Signed in: the duty room.\nIts door is unbolted.",
				String.Format("signed at %d, the double %s, said \"%s\"", r.signedAt, PStr(dbl.pos), h.said));
			Check("reg1_lampGreen", r.frame == 2);
		}
		Still(40);
		if (At()) Check("reg1_doorOpen", DoorGap(11) > 56, String.Format("the steel door's gap %.1f", DoorGap(11)));
		if (At()) { h.Unhang(h.FindFrame(101)); dbl.Reset(); dbl.Posed(mo); }
		Still(20);
		if (At()) Check("reg1_staysSignedDoorDown", Reg(1).signed && DoorGap(11) > 56 && !h.FindFrame(101).door);

		// bay 2: RED's far side is too short, GREEN's long enough
		if (At()) HangIn(red, 102);
		Walkthrough(mo, "reg2_RED_walk", true, 1056, 200, 90, 0, 8, 100, 1, 0, 736, 352, 0, true);
		Still(40);
		if (At()) Check("reg2_notByRED", !Reg(2).signed, String.Format("the double got to %s", PStr(dbl.pos)));
		if (At()) HangIn(green, 102);
		Walkthrough(mo, "reg2_GREEN_walk", true, 1056, 200, 90, 0, 8, 105, 1, 0, -572, 352, 0);
		Still(40);
		if (At()) Check("reg2_signedByGREEN", Reg(2).signed, String.Format("the double %s, player %s", PStr(dbl.pos), PStr(mo.pos)));

		// bay 3: straight on is beside it; a step to the left puts it on
		if (At()) HangIn(green, 103);
		Walkthrough(mo, "reg3_walk", true, 2400, 160, 0, 0, 8, 66, 1, 270, 2544, 1788, 0);
		Still(40);
		if (At()) Check("reg3_notStraightOn", !Reg(3).signed, PStr(dbl.pos));
		Walkthrough(mo, "reg3_stepLeft", false, -100000, 0, 90, 90, 8, 12, 0);
		Still(40);
		if (At()) Check("reg3_signedByGREENTurned", Reg(3).signed, String.Format("the double %s, player %s", PStr(dbl.pos), PStr(mo.pos)));

		// bay 4: GREEN's far side is flat (under the mezzanine: the wrong height); BLUE's climbs the stair
		if (At()) HangIn(green, 104);
		Walkthrough(mo, "reg4_GREEN_walk", true, 3556, 200, 90, 0, 7, 100, 1, 0, 1928, 352, 0);
		Still(40);
		if (At()) Check("reg4_wrongHeightSignsNothing", !Reg(4).signed, String.Format("the double %s, the plate's floor %.0f", PStr(dbl.pos), Reg(4).plateZ));
		if (At()) HangIn(blue, 104);
		Walkthrough(mo, "reg4_BLUE_walk", true, 3556, 200, 90, 0, 7, 100, 1, 0, -522, 352, 0);
		Still(40);
		if (At()) Check("reg4_signedByBLUE", Reg(4).signed && abs(dbl.pos.z - 128) < 0.001, String.Format("the double %s, player %s", PStr(dbl.pos), PStr(mo.pos)));
		Still(60);
		if (At())
		{
			Check("registers_doorsOpen", DoorGap(12) > 56 && DoorGap(13) > 56 && DoorGap(14) > 56,
				String.Format("gaps %.0f %.0f %.0f", DoorGap(12), DoorGap(13), DoorGap(14)));
			Check("registers_5and6NotSigned", !Reg(5).signed && !Reg(6).signed);
		}
	}

	// --- MODE=3: the pumps ---------------------------------------------------------
	int pStart, pCross, pStopped, pBad, pCompared, pSignedAt;
	double pMaxErr;

	void PumpLog(string what)
	{
		Console.Printf("AJARTEST info %s lap %d t=%d: %s; player %s, double %s, floor under the double %.3f", what, dbl.crossings - pCross,
			tic - pStart, TStr(), PStr(mo_pos), PStr(dbl.pos), FloorAt(dbl.pos.xy));
	}
	Vector3 mo_pos;
	int pLaps;

	void Pumps(Actor mo)
	{
		mo_pos = mo.pos;
		// bay 5: run east round the corridor until the double is on register 5
		if (At())
		{
			HangIn(Leaf(8, 0), 105); HangIn(Leaf(8, 1), 106);
			dbl.Reset(); PoseF(mo, 4932, 128, 0);
			pStart = tic; pCross = dbl.crossings; pStopped = 0; pLaps = 0; pBad = 0; pCompared = 0;
		}
		if (Seg(400))
		{
			int laps = dbl.crossings - pCross;
			if (laps != pLaps)
			{
				pLaps = laps;
				PumpLog("bay5");
				if (dbl.tOff.x != 800 * laps || dbl.tOff.y != 0) pBad++;
			}
			// the double in the sealed corridor walks on its floor
			if (laps >= 1 && dbl.pos.x > 5448 && dbl.pos.x < 7848)
			{
				pCompared++;
				if (dbl.pos.y < 0 || dbl.pos.y > 256 || abs(dbl.pos.z - FloorAt(dbl.pos.xy)) > 0.001) pBad++;
			}
			if (!pStopped && laps == 3 && mo.pos.x + 2400 >= 7360) pStopped = tic;
			if (pStopped) mo.vel = (0, 0, 0);
			else Stride(mo, RUN);
			if (Reg(5).signed && !pSignedAt) pSignedAt = tic;
		}
		if (At())
		{
			Check("bay5_lapsAre800", pBad == 0 && pLaps == 3, String.Format("%d laps, %d tics in the sealed corridor compared", pLaps, pCompared));
			Check("bay5_signed", Reg(5).signed, String.Format("stopped after %d tics, signed after %d tics (%.2f s) at a run; the double %s",
				pStopped - pStart, pSignedAt - pStart, (pSignedAt - pStart) / 35.0, PStr(dbl.pos)));
			Check("bay5_doorOpen", DoorGap(15) > 0, String.Format("%.0f", DoorGap(15)));
		}
		// twenty laps of bay 5 at a run
		if (At()) { dbl.Reset(); PoseF(mo, 4700, 128, 0); pStart = tic; pCross = dbl.crossings; pStopped = 0; }
		if (Seg(1100))
		{
			if (!pStopped && dbl.crossings - pCross == 20) pStopped = tic;
			if (pStopped) mo.vel = (0, 0, 0);
			else Stride(mo, RUN);
		}
		if (At()) Check("bay5_twentyLaps", dbl.crossings - pCross == 20 && TExactly(0, 16000, 0, 0) && OnT(mo),
			String.Format("%d laps in %d tics; %s", dbl.crossings - pCross, pStopped - pStart, TStr()));

		// bay 6: down the stair until the double is on register 6
		if (At())
		{
			HangIn(Leaf(9, 0), 107); HangIn(Leaf(9, 1), 108);
			dbl.Reset(); PoseF(mo, 8096, 64, 90);
			pStart = tic; pCross = dbl.crossings; pStopped = 0; pLaps = 0; pBad = 0; pCompared = 0; pSignedAt = 0; pMaxErr = 0;
		}
		if (Seg(400))
		{
			int laps = dbl.crossings - pCross;
			if (laps != pLaps)
			{
				pLaps = laps;
				PumpLog("bay6");
				if (dbl.tOff.x != 0 || dbl.tOff.y != 544 * laps || dbl.tDz != -128 * laps) pBad++;
			}
			// on the sealed stair, the double is as high over its floor as the player over his
			if (laps >= 1 && dbl.pos.y > 592 && dbl.pos.y < 2200)
			{
				pCompared++;
				double e = abs((dbl.pos.z - FloorAt(dbl.pos.xy)) - (mo.pos.z - FloorAt(mo.pos.xy)));
				pMaxErr = max(pMaxErr, e);
				if (e > 0.001 || dbl.pos.x < 7936 || dbl.pos.x > 8256) pBad++;
			}
			if (!pStopped && laps == 3 && mo.pos.y >= 448) pStopped = tic;
			if (pStopped) mo.vel = (0, 0, 0);
			else Stride(mo, RUN);
			if (Reg(6).signed && !pSignedAt) pSignedAt = tic;
		}
		if (At())
		{
			Check("bay6_lapsAre544Down128", pBad == 0 && pLaps == 3, String.Format("%d laps, %d tics on the sealed stair compared, the most off %.6f", pLaps, pCompared, pMaxErr));
			Check("bay6_signed", Reg(6).signed, String.Format("stopped after %d tics, signed after %d tics (%.2f s) at a run; the double %s",
				pStopped - pStart, pSignedAt - pStart, (pSignedAt - pStart) / 35.0, PStr(dbl.pos)));
			Check("bay6_doorOpen", DoorGap(16) > 0, String.Format("%.0f", DoorGap(16)));
		}
		// twenty laps of bay 6 at a run
		if (At()) { dbl.Reset(); PoseF(mo, 8096, 64, 90); pStart = tic; pCross = dbl.crossings; pStopped = 0; }
		if (Seg(800))
		{
			if (!pStopped && dbl.crossings - pCross == 20) pStopped = tic;
			if (pStopped) mo.vel = (0, 0, 0);
			else Stride(mo, RUN);
		}
		if (At()) Check("bay6_twentyLaps", dbl.crossings - pCross == 20 && TExactly(0, 0, 10880, -2560) && OnT(mo),
			String.Format("%d laps in %d tics; %s", dbl.crossings - pCross, pStopped - pStart, TStr()));
	}

	// --- MODE=4: the rest ----------------------------------------------------------
	Array<Actor> made;
	PassDummy target, shooter;
	Actor rocket, imp;
	Vector3 rocketLast, before;
	int unexplainedBefore;

	Actor Make(class<Actor> what, Vector3 at, double ang = 0)
	{
		Actor a = Actor.Spawn(what, at);
		a.angle = ang;
		made.Push(a);
		return a;
	}

	void Rest(Actor mo)
	{
		// the pass desks
		if (At()) HangIn(red, 101);
		Walkthrough(mo, "desk_walk", true, 96, 200, 90, 0, WALK, 30, 1, 0, -224, 352, 0);
		if (At()) { h.said = ""; PoseF(mo, 160, -256, 0); }
		Still(3);
		if (At()) Check("desk1Resets", dbl.IsIdentity() && dbl.pos == mo.pos && h.said == "Your pass is stamped: it is where you are.", String.Format("said \"%s\"", h.said));
		if (At()) { h.said = ""; PoseF(mo, 100, -256, 0); }
		if (At()) PoseF(mo, 160, -256, 0);
		Still(3);
		if (At()) Check("desk1SaysNothingTwice", dbl.IsIdentity() && h.said == "", String.Format("said \"%s\"", h.said));
		Walkthrough(mo, "desk2_walk", true, 96, 200, 90, 0, WALK, 30, 1, 0, -224, 352, 0);
		if (At()) PoseF(mo, 9472, -256, 0);
		Still(3);
		if (At()) Check("desk2Resets", dbl.IsIdentity() && dbl.pos == mo.pos);

		// a ride in the lift after BLUE: the double rides with the player
		if (At()) HangIn(blue, 104);
		Walkthrough(mo, "lift_walk", true, 3556, 200, 90, 0, WALK, 30, 1, 0, -522, 352, 0);
		if (At()) { PoseF(mo, 4270, 256, 90); before = dbl.pos; h.LiftSend(700, 128); }
		if (Seg(60) && tt == 16)
			Console.Printf("AJARTEST info mid-ride: player z %.3f, double z %.3f (behind by %.3f)", mo.pos.z, dbl.pos.z, mo.pos.z + dbl.tDz - dbl.pos.z);
		if (At()) Check("liftRideMovesTheDouble", abs(mo.pos.z - 128) < 0.001 && abs(dbl.pos.z - before.z - 128) < 0.001 && TIs(0, -522, 352, 0) && OnT(mo),
			String.Format("the double from %s to %s; player %s", PStr(before), PStr(dbl.pos), PStr(mo.pos)));
		if (At()) h.LiftSend(700, 0);
		Still(50);

		// shots through the double, a monster that faces it: GREEN by 102 puts it in the stack
		if (At()) HangIn(green, 102);
		Walkthrough(mo, "shots_walk", true, 1056, 200, 90, 0, 8, 50, 1, 0, -572, 352, 0);
		if (At())
		{
			before = dbl.pos;
			target = PassDummy(Make("PassDummy", (1056, 450, 0)));
			shooter = PassDummy(Make("PassDummy", (1056, 1000, 0), 270));
			Actor puff;
			int dmg;
			[puff, dmg] = shooter.LineAttack(270, 2048, 0, 5, 'Hitscan', "BulletPuff");
			Check("hitscanThroughTheDouble", target.hits == 1 && (dbl.pos - before).Length() == 0 && dbl.health > 0,
				String.Format("the double at %s; the dummy beyond it hit %d times; puff %s", PStr(dbl.pos), target.hits, puff ? PStr(puff.pos) : "none"));
			target.hits = 0;
			rocket = Actor.Spawn("Rocket", (1056, 960, 24));
			rocket.target = shooter;
			rocket.angle = 270;
			rocket.vel = (0, -rocket.speed, 0);
		}
		if (Seg(50) && rocket && !rocket.InStateSequence(rocket.CurState, rocket.ResolveState("Death"))) rocketLast = rocket.pos;
		if (At()) Check("rocketThroughTheDouble", target.hits >= 1 && (dbl.pos - before).Length() == 0,
			String.Format("the double at %s; the dummy beyond it hit %d times by %s; the rocket burst at %s", PStr(dbl.pos), target.hits, target.by, PStr(rocketLast)));
		if (At())
		{
			mo.player.cheats &= ~CF_NOTARGET;
			imp = Make("DoomImp", (1056, 1000, 0), 270);        // 400 from the double, facing it; the player in GREEN's corridor
			if (shooter) shooter.Destroy();
			if (target) target.Destroy();
		}
		Still(70);
		if (At())
		{
			Check("monsterFacingTheDoubleSleeps", imp && !imp.target && !imp.CheckSight(mo),
				String.Format("imp target %s, imp sees the player %d, the double %s", imp && imp.target ? imp.target.GetClassName() .. "" : "none", imp ? imp.CheckSight(mo) : -1, PStr(dbl.pos)));
			if (imp) imp.Destroy();
			mo.player.cheats |= CF_NOTARGET;
		}
		// paper: nothing to bump into
		Walkthrough(mo, "walkThroughTheDouble", true, 300, 100, 0, 0, WALK, 20, 0);
		if (At()) Check("paperFlags", !dbl.bSolid && !dbl.bShootable && dbl.bNoBlockmap && dbl.bNoInteraction && dbl.bNeverTarget);
		// a door taken down while the double is away: nothing
		if (At()) HangIn(red, 101);
		Walkthrough(mo, "doorDown_walk", true, 96, 200, 90, 0, WALK, 30, 1, 0, -224, 352, 0);
		if (At()) { before = dbl.pos; h.Unhang(h.FindFrame(101)); }
		Still(5);
		if (At()) Check("doorTakenDownChangesNothing", TIs(0, -224, 352, 0) && dbl.pos == before && OnT(mo), TStr());
		// an ordinary teleport is not a crossing: T is kept, the double jumps with the player
		if (At()) { before = dbl.pos; unexplainedBefore = dbl.unexplained; cCross = dbl.crossings; mo.Teleport((1000, 100, 0), 90, 0); }
		Still(3);
		if (At()) Check("teleportKeepsT", TIs(0, -224, 352, 0) && OnT(mo) && dbl.crossings == cCross,
			String.Format("the double from %s to %s (by the teleport's own move); unexplained jumps +%d", PStr(before), PStr(dbl.pos), dbl.unexplained - unexplainedBefore));
		// a scripted pose through Posed: also kept; Reset: back on the player
		if (At()) { PoseF(mo, 2200, 100, 0); Check("poseKeepsT", TIs(0, -224, 352, 0) && OnT(mo)); dbl.Reset(); dbl.Posed(mo); Check("resetPutsItOnThePlayer", dbl.pos == mo.pos); }
		// the lines on the screen
		if (At()) { HangIn(red, 101); }
		Walkthrough(mo, "lines_walk", true, 96, 200, 90, 0, 8, 37, 1, 0, -224, 352, 0);
		if (At())
		{
			let ph = AjarPassHandler(EventHandler.Find("AjarPassHandler"));
			string a = ph.PassLine(), b = ph.RegisterLine();
			Check("linesOnTheRegister", a == "PASS  352 ahead  224 left  level" && b == "REGISTER 1: 0 ahead of it, 0 left, level", String.Format("\"%s\" \"%s\"", a, b));
			mo.angle = 0;
		}
		Still(2);
		if (At())
		{
			let ph = AjarPassHandler(EventHandler.Find("AjarPassHandler"));
			string a = ph.PassLine(), b = ph.RegisterLine();
			Check("linesTurned", a == "PASS  224 behind  352 left  level" && b == "REGISTER 1: 0 ahead of it, 0 left, level", String.Format("\"%s\" \"%s\"", a, b));
			dbl.Reset(); dbl.Posed(mo);
			Check("noLinesOnThePlayer", ph.PassLine() == "", ph.PassLine());
		}
		if (At()) { HangIn(blue, 104); dbl.Reset(); PoseF(mo, 3556, 200, 90); }
		Walkthrough(mo, "lines4_walk", true, -100000, 0, 90, 0, 8, 20, 1, 0, -522, 352, 0);
		if (At())
		{
			let ph = AjarPassHandler(EventHandler.Find("AjarPassHandler"));
			string a = ph.PassLine(), b = ph.RegisterLine();
			Check("linesRegisterUp", b.IndexOf("REGISTER 4: ") == 0 && b.IndexOf("128 up") > 0, String.Format("\"%s\" \"%s\"", a, b));
		}
		// with the player's own controls: tools/smoke_PASS_4.cfg holds +forward from about 10 tics into each of
		// the two stretches below for 50 tics (the second with +speed: running)
		if (At()) { HangIn(red, 101); dbl.Reset(); PoseF(mo, 96, 150, 90); cCross = dbl.crossings; Console.Printf("AJARTEST info controls from t=%d", tic); }
		Still(100);
		if (At()) Check("red101_byControls", dbl.crossings - cCross == 1 && TIs(0, -224, 352, 0) && OnT(mo), String.Format("%s; player %s, double %s", TStr(), PStr(mo.pos), PStr(dbl.pos)));
		if (At()) { dbl.Reset(); PoseF(mo, 96, 150, 90); cCross = dbl.crossings; Console.Printf("AJARTEST info running controls from t=%d", tic); }
		Still(100);
		if (At()) Check("red101_byControlsRunning", dbl.crossings - cCross == 1 && TIs(0, -224, 352, 0) && OnT(mo), String.Format("%s; player %s, double %s", TStr(), PStr(mo.pos), PStr(dbl.pos)));
	}

	// --- MODE=5: views (tools/smoke_PASS_5.cfg shoots at 34 + 40 n) ----------------
	void CrossAt(Actor mo, int st, int at, double x, double y, double ang, int n = 5)
	{
		if (st == at) PoseF(mo, x, y, ang);
		if (st > at && st <= at + n) Stride(mo, WALK);
		if (st == at + n + 1) mo.vel = (0, 0, 0);
	}

	void Look(Actor mo, int st, double x, double y, double ang, double pitch = 0)
	{
		if (st >= 28) { PoseF(mo, x, y, ang); mo.pitch = pitch; }
	}

	void Views(Actor mo)
	{
		int i = (tic - 2) / 40, st = (tic - 2) % 40;
		if (tic == 2) mo.GiveInventoryType("Allmap");
		if (st == 0) { dbl.Reset(); dbl.Posed(mo); Console.Printf("AJARTEST view=%d t=%d", i, tic); }
		if (st == 39) Console.Printf("AJARTEST info view %d: player %s, double %s, %s", i, PStr(mo.pos), PStr(dbl.pos), TStr());
		switch (i)
		{
		case 0:     // bay 1: out of RED's far side, the glass; the double in the duty room
			if (st == 1) HangIn(red, 101);
			CrossAt(mo, st, 2, 96, 300, 90, 8);
			Look(mo, st, 320, 144, 90);
			break;
		case 1:     // the same, turned to it
			CrossAt(mo, st, 2, 96, 300, 90, 8);
			Look(mo, st, 320, 144, 118);
			break;
		case 2:     // the same, closer to the glass
			CrossAt(mo, st, 2, 96, 300, 90, 8);
			Look(mo, st, 330, 280, 125, -5);
			break;
		case 3:     // bay 5: one lap; down the sealed corridor through the glass
			if (st == 1) { HangIn(Leaf(8, 0), 105); HangIn(Leaf(8, 1), 106); }
			CrossAt(mo, st, 2, 5360, 128, 0);
			Look(mo, st, 5330, 208, 0);
			break;
		case 4:     // two laps
			CrossAt(mo, st, 2, 5360, 128, 0);
			CrossAt(mo, st, 10, 5360, 128, 0);
			Look(mo, st, 5330, 208, 0);
			break;
		case 5:     // bay 6: one lap; down the sealed stair through the glass
			if (st == 1) { HangIn(Leaf(9, 0), 107); HangIn(Leaf(9, 1), 108); }
			CrossAt(mo, st, 2, 8096, 500, 90);
			Look(mo, st, 8192, 470, 90, 20);
			break;
		case 6:     // two laps
			CrossAt(mo, st, 2, 8096, 500, 90);
			CrossAt(mo, st, 10, 8096, 500, 90);
			Look(mo, st, 8192, 470, 90, 20);
			break;
		case 7:     // through a hung door: at the foot, into 107; beyond it the stair from its head, and the double on the player
			Look(mo, st, 8096, 450, 90, 0);
			break;
		case 8:     // bay 3, after GREEN by 103: the double is out of sight; the line and the picture
			if (st == 1) HangIn(green, 103);
			CrossAt(mo, st, 2, 2500, 160, 0);
			Look(mo, st, 1628, 384, 90);
			break;
		case 9:     // bay 4, after BLUE by 104: on the landing; the double on the mezzanine
			if (st == 1) HangIn(blue, 104);
			CrossAt(mo, st, 2, 3556, 310, 90);
			Look(mo, st, 4078, 548, 90);
			break;
		case 10:    // the automap (the cfg opens it), after RED by 101
			if (st == 1) HangIn(red, 101);
			CrossAt(mo, st, 2, 96, 300, 90, 8);
			Look(mo, st, 320, 144, 90);
			break;
		case 11:    // the double inside a wall (RED by 101, the player at the far side's mouth)
			CrossAt(mo, st, 2, 96, 300, 90, 8);
			Look(mo, st, 320, 40, 90);
			break;
		case 12:    // the double in the void: four laps of bay 6
			CrossAt(mo, st, 2, 8096, 500, 90);
			CrossAt(mo, st, 8, 8096, 500, 90);
			CrossAt(mo, st, 14, 8096, 500, 90);
			CrossAt(mo, st, 20, 8096, 500, 90);
			Look(mo, st, 8192, 470, 90, 20);
			break;
		case 13:    // bay 7: out of the one-sided doorway's odd face into C; the double in A
			CrossAt(mo, st, 2, 9128, 300, 270);
			Look(mo, st, 9128, 1300, 270);
			break;
		case 14:    // bay 1 again with the picture turned off (the cfg sets ajar_pass_inset 0)
			if (st == 1) HangIn(red, 101);
			CrossAt(mo, st, 2, 96, 300, 90, 8);
			Look(mo, st, 320, 144, 118);
			break;
		}
		if (tic == 2 + 40 * 15) Console.Printf("AJARTEST viewsDone=1");
	}
}
