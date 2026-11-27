// MAP18 "Time and Motion" (tools/map_clockdept.py): the smoke tests.
// The level's own workings are the clock lab's (clock.zs): the lanes'
// emitters, AjarLaneContact and AjarDelayShutter.
//
// MAP=MAP18 MODE=1..6 tools/smoke.sh:
//   1  the winning run: TEAL in the long lane, the doors on the track the
//      generator found best, BLUE taken at the lever and the lever pulled,
//      then the measured way (MapSpots 1861 on) walked at 16.7 a tic with
//      BLUE in hand; through the shutter, BLUE hung in the brass frame 190
//      (the empty frame no way out before), and out
//   2  both Pairs joining the two longest lanes, and the way on foot
//      (MapSpots 1901 on, the lift ridden) at 16.7 a tic, BLUE in hand, the
//      way out built as in 1
//   3  the failures: nothing hung; the long lane alone on foot; a leaf taken
//      while the pulse laps; a second pull; a run made without BLUE: nobody
//      is shut in the night room, the shutter comes down behind him; BLUE
//      hung elsewhere is a way in for empty hands; USE pressed (for real) at
//      its far side from the night room does not take it down (reach.zs; it did: PLAN.md); the brass frame
//      takes no other door
//   4  each lane's laps, and the two longest joined: the lap's tics, the
//      laps counted, the lamps, how long the shutter is up
//   5  the paradoxes walked
//   6  views (tools/smoke_MAP18_6.cfg takes a screenshot of each)
//   7  the one-sided doorways: each face walked, where it lands; the longer
//      way east against the way west; the way back from the cloakroom to
//      the start; a monster woken beside each face kept off it by its fence
//   8  views of the one-sided doorways (tools/smoke_MAP18_8.cfg)
// The player is god-moded and unseen, and every monster is gone.

extend class AjarHandler
{
	const TAM_RUN = 16.7;
	const TAM_LEVER = 1840;
	const TAM_WAY_A = 1860;
	const TAM_WAY_B = 1900;
	const TAM_HOME = 190;           // the night room's brass frame (ajarmap.HOME): BLUE's only
	const TAM_BLUE = 2;
	int tamStep, tamAt;
	int tamI, tamThrough, tamT0, tamArrive, tamCase, tamSeen;
	double tamAng, tamLastX, tamLastY, tamLastZ, tamRideZ;
	bool tamRiding, tamRideSent, tamJumped, tamFlag;
	double tamJumpX, tamJumpY, tamJumpZ;

	void TamNext(int t) { tamStep++; tamAt = t; }
	int TamIn(int t) { return t - tamAt; }
	bool TamWait(int t, string what, bool ok, int limit)
	{
		if (!ok && TamIn(t) < limit) return false;
		Check(what, ok);
		if (!ok) Console.Printf("AJARTEST info %s: gave up after %d tics", what, TamIn(t));
		TamNext(t);
		return true;
	}

	AjarDelayShutter Delay() { return AjarDelayShutter.Find(); }
	Actor TamSpot(int tid) { return level.CreateActorIterator(tid).Next(); }

	void TamPose(Actor mo, double x, double y, double ang)
	{
		Sector s = level.PointInSector((x, y));
		Pose(mo, x, y, s.floorplane.ZatPoint((x, y)), ang);
		mo.vel = (0, 0, 0);
		mo.pitch = 0;
		tamLastX = x;
		tamLastY = y;
		tamLastZ = mo.pos.z;
	}

	// A lane's lever, used as the player would (from in front of it).
	void TamPull(Actor mo, int lane)
	{
		TamPose(mo, 96, lane == 1 ? 1440 : lane == 2 ? 1664 : 1888, 180);
		Line l = FindLine(TAM_LEVER + lane);
		if (l) l.Activate(mo, 0, SPAC_Use);
	}

	// Every monster gone, and every ambush but those of the first lap (cause 50) when `keepLap`.
	void TamClearOut(bool keepLap = false)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
		it = ThinkerIterator.Create("AjarAmbush");
		while (a = Actor(it.Next())) if (!keepLap || a.args[0] != 50) a.Destroy();
	}

	// Every door down and back where it leant.
	void TamTakeAll(Actor mo)
	{
		let it = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(it.Next())) if (f.door) BeltTake(mo, f.args[0]);
	}

	double TamOpen() { let d = Delay(); return d && d.shutter ? d.shutter.CenterCeiling() - d.shutter.CenterFloor() : 0; }

	int TamLampsLit()
	{
		int n = 0;
		for (int k = 0; k < 8; k++)
		{
			let it = level.CreateSectorTagIterator(1830 + k);
			int i;
			while ((i = it.Next()) >= 0) if (level.sectors[i].lightlevel == 255) n++;
		}
		return n;
	}

	// A jump of more than 128 in one tic: the player went through a portal.
	void TamWatchJump(Actor mo, int t)
	{
		double d = (mo.pos.xy - (tamLastX, tamLastY)).Length();
		if (d > 128)
		{
			tamJumped = true;
			tamJumpX = mo.pos.x;
			tamJumpY = mo.pos.y;
			tamJumpZ = mo.pos.z;
			Console.Printf("AJARTEST info t=%d through a portal: (%.0f,%.0f,%.0f) to (%.0f,%.0f,%.0f)", t, tamLastX, tamLastY, tamLastZ, mo.pos.x, mo.pos.y, mo.pos.z);
		}
		tamLastX = mo.pos.x;
		tamLastY = mo.pos.y;
		tamLastZ = mo.pos.z;
	}

	// The way of MapSpots first + 1, first + 2, ... at `speed` a tic, as the
	// generator measured it: true when it is past the last spot.
	bool TamRun(Actor mo, int t, int first, double speed)
	{
		Actor s = TamSpot(first + 1 + tamI);
		if (!s) { mo.vel.xy = (0, 0); return true; }
		Vector2 at = mo.pos.xy;
		bool jump = (at - (tamLastX, tamLastY)).Length() > 128;
		tamLastX = at.x;
		tamLastY = at.y;
		if (tamThrough > 0)
		{
			if (jump)
			{
				Console.Printf("AJARTEST info t=%d through a door to (%.0f,%.0f,%.0f)", t, at.x, at.y, mo.pos.z);
				tamThrough = 0;
				tamI++;
			}
			else if (--tamThrough == 0)
			{
				Check("throughTheDoorAtSpot" .. (first + 1 + tamI), false);
				tamI++;
			}
			else mo.vel.xy = Actor.AngleToVector(tamAng, speed);
			return false;
		}
		if (tamRiding)
		{
			mo.vel.xy = (0, 0);
			if (!tamRideSent) { LiftSend(LIFT_TAG, int(tamRideZ)); tamRideSent = true; }
			else if (!LiftMoving() && LiftAt() == tamRideZ)
			{
				Console.Printf("AJARTEST info t=%d rode the car to %.0f", t, tamRideZ);
				tamRiding = false;
				tamI++;
			}
			return false;
		}
		Vector2 d = s.pos.xy - at;
		double len = d.Length();
		if (s.args[0] == 2)
		{
			tamRiding = true;
			tamRideSent = false;
			tamRideZ = s.args[1] - 512;
			mo.vel.xy = d;
			return false;
		}
		if (len <= speed + 0.5)
		{
			mo.vel.xy = d;
			if (s.args[0] == 1) { tamThrough = 12; tamAng = s.args[1]; }
			else tamI++;
		}
		else mo.vel.xy = d / len * speed;
		return false;
	}

	void TamStartRun(int t)
	{
		tamI = 0;
		tamThrough = 0;
		tamRiding = false;
		tamT0 = t;
		tamArrive = 0;
	}

	// While a run goes on: the tic the player is in the shutter's doorway.
	void TamWatchShutter(Actor mo, int t, bool want)
	{
		if (tamArrive || mo.pos.y < 2596 || mo.pos.x < 7744 || mo.pos.x > 7808 || mo.pos.z > -200) return;
		tamArrive = t;
		let d = Delay();
		int life = d.Live() ? 0 : d.goneAt - d.firedAt;
		Console.Printf("AJARTEST info the way took %d tics (lever pulled at %d); the pulse fired at %d is %s, %d laps; the shutter open %.0f",
			t - tamT0, tamT0, d.firedAt, d.Live() ? "alive" : "gone", d.pulse ? d.pulse.laps : -1, TamOpen());
		if (want) Check("theShutterIsUpWhenThere", d.Live() && TamOpen() >= 56);
	}

	// The night room (map_clockdept.py, NIGHT): BLUE's far side in its west end, the brass frame in its east end.
	bool TamInNight(Actor mo) { return InBox(mo, 7616, 2608, 7936, 2864) && mo.pos.z < -200; }

	// TEAL in the long lane and the doors of way A as the generator found them (MapSpot 1860: ORANGE's two
	// frames, RED's, GREEN's; 1859: RED's car's floor + 512), and the car sent there.
	void TamHangWayA(Actor mo)
	{
		Actor doors = TamSpot(TAM_WAY_A), car = TamSpot(TAM_WAY_A - 1);
		BeltHang(mo, LabLeaf(8, 0), 101);
		BeltHang(mo, LabLeaf(8, 1), 102);
		if (doors.args[0]) { BeltHang(mo, LabLeaf(9, 0), doors.args[0]); BeltHang(mo, LabLeaf(9, 1), doors.args[1]); }
		if (doors.args[2]) BeltHang(mo, DoorOf(1), doors.args[2]);
		if (doors.args[3]) BeltHang(mo, DoorOf(3), doors.args[3]);
		Console.Printf("AJARTEST info the track: ORANGE %d %d, RED %d (the car at %d), GREEN %d (BLUE is no door of the track)",
			doors.args[0], doors.args[1], doors.args[2], car.args[0] - 512, doors.args[3]);
		if (doors.args[2]) LiftSend(LIFT_TAG, car.args[0] - 512);
	}
	bool TamCarWaits()
	{
		Actor doors = TamSpot(TAM_WAY_A), car = TamSpot(TAM_WAY_A - 1);
		return !LiftMoving() && LiftAt() == (doors.args[2] ? car.args[0] - 512 : LiftAt());
	}

	// At the lever: BLUE taken (from wherever it leans) and carried from here on.
	void TamTakeBlue(Actor mo)
	{
		if (carried) BeltPutBack(carried);
		TakeLeaning(DoorOf(TAM_BLUE), mo);
		Check("blueInHandAtTheLever", carried == DoorOf(TAM_BLUE));
	}

	// The end of a run made with BLUE in hand (MODE=1 and 2), from before the brass frame: the frame empty is
	// no way out (walked into, nothing ends); BLUE hung in it makes the room the way out, and walking on into
	// its east end ends the level.
	void TamBuildTheWayOut(Actor mo, int t)
	{
		int k = TamIn(t);
		AjarFrame f = FindFrame(TAM_HOME);
		if (k == 1) Check("noWayOutYet", !wayOutBuilt && carried == DoorOf(TAM_BLUE) && TamInNight(mo) && !f.door);
		if (k <= 24) mo.vel.xy = (TAM_RUN, 0);           // into the empty frame: its back is a wall
		else if (k == 30)
		{
			Check("theEmptyFrameIsNoWayOut", !wayOutBuilt && InBox(mo, 7616, 2608, 7952, 2864) && carried == DoorOf(TAM_BLUE));
			TamPose(mo, 7872, 2736, 0);
			f.Activate(mo);
			Check("wayOutBuilt", wayOutBuilt && !carried && f.door == DoorOf(TAM_BLUE));
		}
		else if (k > 30) mo.vel.xy = (TAM_RUN, 0);
		if (k > 90) { Check("outByTheNightRoom", false); TamNext(t); }
	}

	void TimeAndMotionScript(Actor mo, int t, int mode)
	{
		if (t == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			tamAt = 1;
			TamClearOut(mode == 4);         // MODE=4: the first lap's ambushes come (and go at once: the autotest's rule)
			let d = Delay();
			Check("theShutterIsThere", d && d.shutter && d.lamps.Size() == 2 * d.args[2]);
			Check("theShutterIsDown", d && d.Down() && !d.Live());
		}
		if (t < 2) return;
		if (mode == 1) TamWinningRun(mo, t);
		else if (mode == 2) TamOnFoot(mo, t);
		else if (mode == 3) TamFailures(mo, t);
		else if (mode == 4) TamLaps(mo, t);
		else if (mode == 5) TamParadoxes(mo, t);
		else if (mode == 6) TamViews(mo, t);
		else if (mode == 7) TamOneSided(mo, t);
		else if (mode == 8) TamOneSidedViews(mo, t);
	}

	// MODE=1: TEAL in the long lane, the rest as the generator's best track.
	void TamWinningRun(Actor mo, int t)
	{
		switch (tamStep)
		{
		case 0:
			TamHangWayA(mo);
			Check("tealInTheLongLane", LabLeaf(8, 0).frame == FindFrame(101) && LabLeaf(8, 1).frame == FindFrame(102));
			TamNext(t);
			break;
		case 1:
			TamWait(t, "theCarWaits", TamCarWaits(), 400);
			break;
		case 2:
			TamTakeBlue(mo);
			TamPull(mo, 1);
			Check("theLeverFiresTheLongLane", Delay().Live() && Delay().pulse.lane == 1);
			TamStartRun(t);
			TamNext(t);
			break;
		case 3:
			TamWatchShutter(mo, t, true);
			if (TamRun(mo, t, TAM_WAY_A, TAM_RUN) || TamIn(t) > 1500)
			{
				Check("theWayIsWalked", tamArrive > 0);
				TamNext(t);
			}
			break;
		case 4:
			TamBuildTheWayOut(mo, t);
			break;
		}
	}

	// MODE=2: TEAL in 102 and 103, ORANGE in 104 and 101: one loop of both lanes; the way on foot.
	void TamOnFoot(Actor mo, int t)
	{
		let d = Delay();
		switch (tamStep)
		{
		case 0:
			BeltHang(mo, LabLeaf(8, 0), 102);
			BeltHang(mo, LabLeaf(8, 1), 103);
			BeltHang(mo, LabLeaf(9, 0), 104);
			BeltHang(mo, LabLeaf(9, 1), 101);
			Check("bothPairsJoinTheLanes", LabLeaf(9, 1).frame == FindFrame(101) && LabLeaf(8, 1).frame == FindFrame(103));
			Check("theCarIsOnTheGround", LiftAt() == 0);
			TamNext(t);
			break;
		case 1:
			TamTakeBlue(mo);
			TamPull(mo, 1);
			TamStartRun(t);
			TamNext(t);
			break;
		case 2:
			TamWatchShutter(mo, t, true);
			if (TamRun(mo, t, TAM_WAY_B, TAM_RUN) || TamIn(t) > 1500)
			{
				Check("theWayIsWalked", tamArrive > 0);
				if (d.lapAt.Size() >= 2)
				{
					int lap = d.lapAt[1] - d.lapAt[0];
					Console.Printf("AJARTEST info the joined loop: a lap %d tics (%.1f by its length)", lap, 3136.0 / d.PulseSpeed());
					Check("theJoinedLapIsBothLanes", abs(lap - 3136.0 / d.PulseSpeed()) <= 1.5);
				}
				TamNext(t);
			}
			break;
		case 3:
			TamBuildTheWayOut(mo, t);
			break;
		}
	}

	// A USE press as the player makes one (the key down, then up): the engine's own use trace, not a script call.
	void TamPressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
		pp.CheckUse();
	}

	// MODE=3, with BLUE hung in 128 and the player in the night room, empty-handed: USE pressed facing west at
	// BLUE's far side (its mouth at x 7616, y 2704..2768; the portal 16 behind it, at x 7600), one press a tic,
	// from x 7604, 7616, 7632, 7648, 7664 (4 to 64 from the portal), y 2720, 2736, 2752 (either jamb, the
	// middle), facing 165, 180, 195. Each press logged; a door taken is hung back in 128 and the presses go on.
	int tamFarTaken;
	bool TamFarSideUse(Actor mo, int t)
	{
		static const double xs[] = { 7604, 7616, 7632, 7648, 7664 };
		static const double ys[] = { 2720, 2736, 2752 };
		static const double angs[] = { 165, 180, 195 };
		int k = TamIn(t);
		if (k == 1) tamFarTaken = 0;
		int i = k - 1;
		if (i < 45)
		{
			TamPose(mo, xs[i / 9], ys[(i / 3) % 3], angs[i % 3]);
			TamPressUse(mo);
			bool hung = FindFrame(128).door == DoorOf(TAM_BLUE);
			Console.Printf("AJARTEST info far side USE %d at (%.0f,%.0f,%.0f) facing %.0f: carried %s, 128 %s, in the night room %d",
				i + 1, mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, carried ? carried.Label() : "-", hung ? "BLUE" : FindFrame(128).door ? "another" : "empty", TamInNight(mo));
			if (carried || !hung)
			{
				tamFarTaken++;
				Console.Printf("AJARTEST info far side USE %d TOOK %s down from 128", i + 1, carried ? carried.Label() : "?");
				if (carried == DoorOf(TAM_BLUE)) { BeltHang(mo, DoorOf(TAM_BLUE), 128); }
				if (carried) BeltPutBack(carried);
			}
			return false;
		}
		Check("blueIsNotTakenFromItsFarSide", tamFarTaken == 0 && FindFrame(128).door == DoorOf(TAM_BLUE) && !carried && TamInNight(mo));
		return true;
	}

	// MODE=3: what fails.
	void TamFailures(Actor mo, int t)
	{
		let d = Delay();
		switch (tamStep)
		{
		case 0:     // nothing hung: the pulse bursts on the lane's end
			TamPull(mo, 1);
			TamNext(t);
			break;
		case 1:
			if (TamWait(t, "nothingHungItBursts", d.gone == 2, 200))
				Console.Printf("AJARTEST info nothing hung: the pulse lived %d tics, the shutter opened to %.0f", d.goneAt - d.firedAt, d.shutter.CenterCeiling() - d.bottom);
			break;
		case 2:
			if (TamWait(t, "andTheShutterComesDown", d.Down(), 100))
				Console.Printf("AJARTEST info down again %d tics after it burst", d.downAt - d.goneAt);
			break;
		case 3:     // the long lane alone, on foot: the shutter is down before the player is there
			BeltHang(mo, LabLeaf(8, 0), 101);
			BeltHang(mo, LabLeaf(8, 1), 102);
			TamPull(mo, 1);
			TamStartRun(t);
			TamNext(t);
			break;
		case 4:
			TamWatchShutter(mo, t, false);
			TamRun(mo, t, TAM_WAY_B, TAM_RUN);
			if (d.gone && !tamFlag)
			{
				tamFlag = true;
				tamCase = t;
				Console.Printf("AJARTEST info the long lane alone: the pulse burnt out after %d tics, %d laps; the player %d tics into the way, at (%.0f,%.0f,%.0f)",
					d.goneAt - d.firedAt, d.lapAt.Size(), t - tamT0, mo.pos.x, mo.pos.y, mo.pos.z);
				Check("theLongLaneAloneBurnsOut", d.gone == 1 && d.lapAt.Size() == d.args[2]);
			}
			if (tamFlag && t - tamCase > 200)
			{
				Check("theLongLaneAloneIsNotEnough", !tamArrive && mo.pos.y < 2592);
				Console.Printf("AJARTEST info the player waits at (%.0f,%.0f,%.0f), the shutter down", mo.pos.x, mo.pos.y, mo.pos.z);
				TamNext(t);
			}
			break;
		case 5:     // a leaf taken while the pulse laps: it bursts where the leaf was
			mo.vel.xy = (0, 0);
			TamPull(mo, 1);
			TamNext(t);
			break;
		case 6:
			if (d.lapAt.Size() >= 1)
			{
				BeltTake(mo, 102);
				Check("theLeafIsTaken", !FindFrame(102).door);
				TamNext(t);
			}
			else if (TamIn(t) > 200) { Check("aLapBeforeTheLeafIsTaken", false); TamNext(t); }
			break;
		case 7:
			if (TamWait(t, "takenLeafItBursts", d.gone == 2, 150))
			{
				Check("afterOneLap", d.pulse && d.pulse.laps == 1);
				BeltHang(mo, LabLeaf(8, 1), 102);
			}
			break;
		case 8:
			TamWait(t, "theShutterDownAgain", d.Down(), 100);
			break;
		case 9:     // a second pull: the first pulse is called back, one pulse in the hall
			TamPull(mo, 1);
			tamFlag = false;
			TamNext(t);
			break;
		case 10:
			if (TamIn(t) == 60)
			{
				let old = d.pulse;
				TamPull(mo, 1);
				Check("theFirstIsCalledBack", old && old.recalled && !old.bMissile);
				Check("oneInTheHall", ClockAlive() == 1 && d.pulse != old && d.pulse.laps == 0);
				Check("theShutterHeld", d.Live() && d.Up());
			}
			if (TamIn(t) == 100)
			{
				let old = d.pulse;
				TamPull(mo, 2);                 // the middle lane, with nothing in it
				Check("anotherLaneCallsItBack", old.recalled && ClockAlive() == 1 && d.pulse.lane == 2);
				TamNext(t);
			}
			break;
		case 11:
			TamWait(t, "theMiddleLaneAloneBursts", d.gone == 2, 100);
			break;
		case 12:    // a run made without BLUE (way A, the pulse alive on arrival): nobody is shut in the night room
			TamTakeAll(mo);
			TamHangWayA(mo);
			TamNext(t);
			break;
		case 13:
			TamWait(t, "readyForARunWithoutBlue", TamCarWaits() && d.Down(), 400);
			break;
		case 14:
			TamPull(mo, 1);
			TamStartRun(t);
			TamNext(t);
			break;
		case 15:
			TamWatchShutter(mo, t, false);
			if (TamRun(mo, t, TAM_WAY_A, TAM_RUN) || TamIn(t) > 1500)
			{
				Check("inTheNightRoomWithoutBlue", tamArrive > 0 && TamInNight(mo) && !carried && !wayOutBuilt && d.Live());
				TamNext(t);
			}
			break;
		case 16:
			mo.vel.xy = (0, 0);
			if (TamWait(t, "theRunWithoutBlueBurnsOut", d.gone == 1, 600))
				Console.Printf("AJARTEST info the pulse burnt out with the player in the night room, %d tics after the pull", d.goneAt - d.firedAt);
			break;
		case 17:
			if (TamIn(t) == 40)
			{
				Console.Printf("AJARTEST info 40 tics after the pulse went: the player at (%.0f,%.0f,%.0f), the shutter open %.0f", mo.pos.x, mo.pos.y, mo.pos.z, TamOpen());
				Check("nobodyIsShutIn", !d.Live() && d.Up() && d.occupied && TamInNight(mo));
				TamNext(t);
			}
			break;
		case 18:    // out by the shutter, south into the boiler room
			if (TamWalk(mo, t, 7776, 2680, 270, 20)) { Check("outByTheShutter", !tamJumped && mo.pos.y < 2560 && mo.pos.z < -200); TamNext(t); }
			break;
		case 19:
			if (TamWait(t, "theShutterComesDownBehind", d.Down() && !d.occupied && mo.pos.y < 2592, 100))
				Console.Printf("AJARTEST info down again %d tics after the walk out ended (the shutter %d tics down)", TamIn(t), level.maptime - d.downAt);
			break;
		case 20:    // BLUE hung elsewhere (128, the north corridor) is a way into the night room for empty hands
			if (TamIn(t) == 1) { TamTakeAll(mo); BeltHang(mo, DoorOf(TAM_BLUE), 128); }
			if (TamWalk(mo, t, 2272, 2200, 90, 20))
			{
				Console.Printf("AJARTEST info through BLUE in 128: at (%.0f,%.0f,%.0f) facing %.0f", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle);
				Check("blueHungIsAWayIn", tamJumped && TamInNight(mo) && !carried && !wayOutBuilt);
				TamNext(t);
			}
			break;
		case 21:
			TamWait(t, "theShutterGoesUpForWhoeverIsIn", d.Up() && !d.Live() && d.occupied, 60);
			break;
		case 22:    // BLUE must not be taken down from its far side: real USE presses at it from the night room (it is: PLAN.md)
			if (TamFarSideUse(mo, t)) TamNext(t);
			break;
		case 23:    // the brass frame takes no door but BLUE: GREEN stays in hand
			if (carried) BeltPutBack(carried);
			TakeLeaning(DoorOf(3), mo);
			TamPose(mo, 7872, 2736, 0);
			FindFrame(TAM_HOME).Activate(mo);
			Check("theBrassFrameTakesBlueOnly", carried == DoorOf(3) && !FindFrame(TAM_HOME).door && !wayOutBuilt);
			TamNext(t);
			break;
		case 24:    // ... and GREEN is carried out by the shutter
			if (TamWalk(mo, t, 7776, 2680, 270, 20)) { Check("outByTheShutterWithGreen", !tamJumped && mo.pos.y < 2560 && carried == DoorOf(3)); TamNext(t); }
			break;
		case 25:
			if (TamWait(t, "theShutterComesDownBehindAgain", d.Down() && !d.occupied, 100) && carried) BeltPutBack(carried);
			break;
		}
	}

	// MODE=4: each lane, then the two longest joined.
	void TamLaps(Actor mo, int t)
	{
		static const int lanes[] = { 1, 2, 3, 1 };
		static const double lens[] = { 2080, 1056, 544, 3136 };
		static const string names[] = { "long", "middle", "short", "joined" };
		let d = Delay();
		int c = tamStep / 2;
		if (c >= 4) return;
		if (tamStep % 2 == 0)
		{
			TamTakeAll(mo);
			if (c == 0) { BeltHang(mo, LabLeaf(8, 0), 101); BeltHang(mo, LabLeaf(8, 1), 102); }
			if (c == 1) { BeltHang(mo, LabLeaf(8, 0), 103); BeltHang(mo, LabLeaf(8, 1), 104); }
			if (c == 2) { BeltHang(mo, LabLeaf(8, 0), 105); BeltHang(mo, LabLeaf(8, 1), 106); }
			if (c == 3) { BeltHang(mo, LabLeaf(8, 0), 102); BeltHang(mo, LabLeaf(8, 1), 103); BeltHang(mo, LabLeaf(9, 0), 104); BeltHang(mo, LabLeaf(9, 1), 101); }
			TamPull(mo, lanes[c]);
			tamSeen = 0;
			tamFlag = true;
			TamNext(t);
			return;
		}
		if (TamIn(t) % 35 == 1)
			Console.Printf("AJARTEST info t=%d live=%d gone=%d laps=%d open=%.0f pulse=%s at (%.0f,%.0f,%.0f) alive=%d", t, d.Live(), d.gone, d.lapAt.Size(), TamOpen(),
				d.pulse ? "yes" : "no", d.pulse ? d.pulse.pos.x : 0., d.pulse ? d.pulse.pos.y : 0., d.pulse ? d.pulse.pos.z : 0., ClockAlive());
		// the lamps: as many lit as laps are left, two tics after each lap
		if (d.lapAt.Size() > tamSeen && t >= d.lapAt[d.lapAt.Size() - 1] + 2)
		{
			tamSeen = d.lapAt.Size();
			int left = d.args[2] - tamSeen;
			if (TamLampsLit() != 2 * left) tamFlag = false;
		}
		if (d.gone && d.Down())
		{
			double want = lens[c] / d.PulseSpeed();
			string laps = "";
			bool even = true;
			for (int i = 1; i < d.lapAt.Size(); i++)
			{
				int lap = d.lapAt[i] - d.lapAt[i - 1];
				laps.AppendFormat("%s%d", i > 1 ? "," : "", lap);
				if (abs(lap - want) > 1.5) even = false;
			}
			Console.Printf("AJARTEST info the %s lane: laps at %s tics (%.1f by its length), %d counted, first after %d; it lived %d tics; the shutter up %d tics after the pull, down %d after it went",
				names[c], laps, want, d.lapAt.Size(), d.lapAt.Size() ? d.lapAt[0] - d.firedAt : -1, d.goneAt - d.firedAt, d.upAt - d.firedAt, d.downAt - d.goneAt);
			Check(names[c] .. "LapsEven", even && d.lapAt.Size() > 1);
			Check(names[c] .. "LapsCounted", d.lapAt.Size() == d.args[2] && d.gone == 1);
			Check(names[c] .. "LampsCountDown", tamFlag && TamLampsLit() == 0);
			if (c == 0)
			{
				int n50 = 0;
				let it = ThinkerIterator.Create("AjarAmbush");
				Actor a;
				while (a = Actor(it.Next())) if (a.args[0] == 50) n50++;
				Check("theFirstLapsAmbushesCame", delayFirstLap && n50 == 0);
			}
			TamNext(t);
		}
		else if (TamIn(t) > 1200) { Check(names[c] .. "Ends", false); TamNext(t); }
	}

	// A walk at 10 a tic: posed on its first tic, then on at its angle.
	bool TamWalk(Actor mo, int t, double x, double y, double ang, int tics)
	{
		int k = TamIn(t);
		if (k == 1) { TamPose(mo, x, y, ang); tamJumped = false; return false; }
		TamWatchJump(mo, t);
		if (k <= tics + 1) mo.vel.xy = (cos(mo.angle), sin(mo.angle)) * 10;
		else mo.vel.xy = (0, 0);
		return k == tics + 4;
	}

	// MODE=5: the paradoxes, each walked.
	void TamParadoxes(Actor mo, int t)
	{
		switch (tamStep)
		{
		case 0:     // the endless corridor: TEAL in the long lane
			if (TamIn(t) == 1) { BeltHang(mo, LabLeaf(8, 0), 101); BeltHang(mo, LabLeaf(8, 1), 102); }
			if (TamWalk(mo, t, 2420, 1440, 0, 30)) { Check("laneEastComesInWest", tamJumped && mo.pos.x < 1000); TamNext(t); }
			break;
		case 1:
			if (TamWalk(mo, t, 560, 1440, 180, 30)) { Check("laneWestComesInEast", tamJumped && mo.pos.x > 2000); TamNext(t); }
			break;
		case 2:     // the endless stair: TEAL in 107 (the foot) and 108 (the head)
			if (TamIn(t) == 1) { TamTakeAll(mo); BeltHang(mo, LabLeaf(8, 0), 107); BeltHang(mo, LabLeaf(8, 1), 108); }
			if (TamWalk(mo, t, 544, 3080, 270, 80)) { Check("downTheStairComesInAtTheHead", tamJumped && tamJumpY > 3000 && tamJumpZ > 250); TamNext(t); }
			break;
		case 3:
			if (TamWalk(mo, t, 544, 2420, 90, 80)) { Check("upTheStairComesInAtTheFoot", tamJumped && tamJumpY < 2500 && tamJumpZ < 5); TamNext(t); }
			break;
		case 4:     // the moving room: RED in 128 (the north corridor), the car at each floor
		case 7:
		case 10:
			if (TamIn(t) == 1)
			{
				TamTakeAll(mo);
				BeltHang(mo, DoorOf(1), 128);
				TamPose(mo, 2272, 2200, 90);
				LiftSend(LIFT_TAG, tamStep == 4 ? -256 : tamStep == 7 ? 0 : 256);
			}
			if (TamIn(t) > 130 && !LiftMoving()) TamNext(t);
			break;
		case 5:
		case 8:
		case 11:
			if (TamWalk(mo, t, 2272, 2200, 90, 20))
			{
				Check("intoTheCarAt" .. (LiftAt() < 0 ? "Basement" : LiftAt() > 0 ? "Upper" : "Ground"), tamJumped && InBox(mo, 6720, 1920, 6912, 2112) && abs(mo.pos.z - LiftAt()) < 2);
				TamNext(t);
			}
			break;
		case 6:
		case 9:
		case 12:
			if (TamWalk(mo, t, 6816, 2040, 270, 20))
			{
				Check("outOfTheCarAt" .. (LiftAt() < 0 ? "Basement" : LiftAt() > 0 ? "Upper" : "Ground"), tamJumped && InBox(mo, 448, 2112, 2944, 2288));
				TamNext(t);
			}
			break;
		case 13:    // round the pillar: TEAL in the stub's two faces
			if (TamIn(t) == 1) { TamTakeAll(mo); BeltHang(mo, LabLeaf(8, 0), 112); BeltHang(mo, LabLeaf(8, 1), 113); }
			if (TamWalk(mo, t, 5860, 1792, 0, 15)) { Check("eastThroughTheStub", tamJumped && mo.pos.x > 6096); TamNext(t); }
			break;
		case 14:
			if (TamWalk(mo, t, 6170, 1792, 180, 15)) { Check("westThroughTheStub", tamJumped && mo.pos.x < 5936); TamNext(t); }
			break;
		case 15:    // ... and the north wall to the west wall
			if (TamIn(t) == 1) { TamTakeAll(mo); BeltHang(mo, LabLeaf(8, 0), 109); BeltHang(mo, LabLeaf(8, 1), 111); }
			if (TamWalk(mo, t, 6016, 2660, 90, 15)) { Check("northComesInWest", tamJumped && mo.pos.x < 5700 && mo.pos.y < 2100); TamNext(t); }
			break;
		case 16:    // the six-sided hall: its north-east wall is its south-west wall
			if (TamWalk(mo, t, 5952, 3616, 30, 40)) { Check("northEastComesInSouthWest", tamJumped && tamJumpX < 5800 && (mo.pos.xy - (5952, 3616)).Length() < 280); TamNext(t); }
			break;
		case 17:
			if (TamWalk(mo, t, 5952, 3616, 210, 40)) { Check("southWestComesInNorthEast", tamJumped && tamJumpX > 6100 && (mo.pos.xy - (5952, 3616)).Length() < 280); TamNext(t); }
			break;
		case 18:    // the room that is its own neighbour
			if (TamWalk(mo, t, 6848, 3584, 90, 30)) { Check("northComesInSouth", tamJumped && tamJumpY < 3450 && InBox(mo, 6656, 3392, 7040, 3776)); TamNext(t); }
			break;
		case 19:
			if (TamWalk(mo, t, 6848, 3584, 270, 30)) { Check("southComesInNorth", tamJumped && tamJumpY > 3700 && InBox(mo, 6656, 3392, 7040, 3776)); TamNext(t); }
			break;
		case 20:    // the inside-out booth: each wall of the hall with no size is a face of the tower, outwards
		case 21:
		case 22:
		case 23:
		{
			static const double angs[] = { 90, 0, 270, 180 };
			int n = tamStep - 20;
			if (TamWalk(mo, t, 1728, 2800, angs[n], 30))
			{
				bool inCourt = InBox(mo, 3008, 1344, 4992, 2944) && !InBox(mo, 3880, 2024, 4120, 2264);
				Vector2 dir = Actor.AngleToVector(angs[n], 1);
				bool away = (mo.pos.xy - (4000, 2144)) dot dir > 100;
				Check("hallWall" .. (n + 1) .. "IsTheTowersFace", tamJumped && inCourt && away);
				TamNext(t);
			}
			break;
		}
		case 24:    // ... and back in from the court
			if (TamWalk(mo, t, 4000, 2340, 270, 30)) { Check("intoTheTowerIsIntoTheHall", tamJumped && InBox(mo, 1536, 2608, 1920, 2992) && mo.pos.z > 250); TamNext(t); }
			break;
		}
	}

	// MODE=6: views of every area and paradox.
	void TamViews(Actor mo, int t)
	{
		static const double views[] = {
			4000, 416, 90, 0,       // 0 the start: the entrance hall
			4450, 1200, 225, 0,     // 1 the entrance hall from the north-east
			3300, 980, 200, 0,      // 2 the cloakroom
			2860, 384, 180, 0,      // 3 the yard from the porch
			1900, 300, 150, 0,      // 4 the yard and the porter's hut
			320, 1480, 180, 0,      // 5 the regulator room: the levers and the lamps
			2420, 1320, 150, 0,     // 6 the delay hall from the south-east
			2420, 1440, 180, 0,     // 7 down the long lane: the endless corridor (TEAL in 101, 102)
			560, 1760, 180, 0,      // 8 the glass onto the regulator room
			2860, 2200, 180, 0,     // 9 the north corridor
			544, 2420, 90, -10,     // 10 the stair from the foot
			544, 3100, 270, 10,     // 11 the stair from the head: the endless stair (ORANGE in 107, 108)
			760, 3136, 0, 0,        // 12 the spine
			1728, 2680, 90, 0,      // 13 the hall with no size, looking north: the court
			1728, 2900, 0, 0,       // 14 ... looking east
			4000, 1420, 90, 0,      // 15 the court and the clock tower
			3700, 2144, 0, 0,       // 16 the tower's west face
			5560, 2560, 315, 0,     // 17 the rotunda
			5860, 1792, 0, 0,       // 18 the stub's west face (GREEN: the basement stores)
			6640, 2016, 0, 0,       // 19 the lift's car (RED's far side)
			5120, 400, 45, 0,       // 20 the canteen
			6450, 700, 0, 0,        // 21 the kitchen
			7120, 1400, 0, -10,     // 22 the kitchen's steps down
			7100, 500, 0, 0,        // 23 the stores
			7480, 1300, 60, 0,      // 24 the cellar
			7250, 2250, 30, 0,      // 25 the boiler room and the shutter
			7700, 2680, 0, 0,       // 26 the night room: the brass frame, BLUE's only, empty
			5700, 3616, 0, 0,       // 27 the six-sided hall
			6848, 3450, 90, 0,      // 28 the room that is its own neighbour
			7600, 3400, 90, 0,      // 29 the regulator store (ORANGE)
			1000, 3300, 90, 0,      // 30 an office
			3100, 3300, 60, 0,      // 31 the archive
			4200, 3300, 45, 0,      // 32 the timekeepers
			1000, 2720, 30, 0,      // 33 the drawing office
			2100, 2720, 30, 0       // 34 the workshop
		};
		if (t == 2)
		{
			BeltHang(mo, LabLeaf(8, 0), 101); BeltHang(mo, LabLeaf(8, 1), 102);
			BeltHang(mo, LabLeaf(9, 0), 107); BeltHang(mo, LabLeaf(9, 1), 108);
			BeltHang(mo, DoorOf(3), 112);
			BeltHang(mo, DoorOf(1), 128);
		}
		int i = t / 40;
		if (i >= views.Size() / 4) return;
		TamPose(mo, views[i * 4], views[i * 4 + 1], views[i * 4 + 2]);
		mo.pitch = views[i * 4 + 3];
		if (t % 40 == 0) Console.Printf("AJARTEST view=%d at (%.0f,%.0f)", i, views[i * 4], views[i * 4 + 1]);
	}

	// --- the one-sided doorways (map_clockdept.py: ONESIDE sites 1 to 3) -----------------------------
	const ODD1 = 1871; const MOUTH1 = 1872; const X_IN = 1873; const X_OUT = 1874;
	const ODD2 = 1875; const ARCH_GATE = 1876; const MOUTH2 = 1877;
	const ODD3 = 1878; const OFFICE_GATE = 1879; const MOUTH3 = 1880;
	const FENCE = 48;
	Vector2 tamFrom, tamSet, tamPreFrom, tamPreSet, tamLand;
	double tamPrevAng, tamPreAng, tamLandAng, tamLandZ, tamMinDist;
	int tamJumps, tamEast, tamWest;
	Actor tamImp;

	// A walk at 10 a tic, as TamWalk, that keeps the first crossing: where
	// the player was and how he was moving the tic before, where he landed.
	bool TamGo(Actor mo, int t, double x, double y, double ang, int tics)
	{
		int k = TamIn(t);
		if (k == 1)
		{
			TamPose(mo, x, y, ang);
			tamFrom = mo.pos.xy;
			tamPrevAng = ang;
			tamSet = (0, 0);
			tamJumps = 0;
			return false;
		}
		if ((mo.pos.xy - tamFrom).Length() > 64)
		{
			if (!tamJumps)
			{
				tamPreFrom = tamFrom; tamPreSet = tamSet; tamPreAng = tamPrevAng;
				tamLand = mo.pos.xy; tamLandAng = mo.angle; tamLandZ = mo.pos.z;
			}
			tamJumps++;
		}
		tamFrom = mo.pos.xy;
		tamPrevAng = mo.angle;
		tamSet = (0, 0);
		if (k <= tics + 1) { tamSet = (cos(mo.angle), sin(mo.angle)) * 10; mo.vel.xy = tamSet; }
		else mo.vel.xy = (0, 0);
		return k == tics + 4;
	}

	// The first crossing went from the portal `src` to `dst` as the engine
	// carries a thing (oneside.zs, OneSideTest.Through): the place where the
	// tic's move would have ended, carried through, and the facing turned.
	bool TamLanded(int src, int dst, string what)
	{
		Line s = FindLine(src), d = FindLine(dst);
		if (!tamJumps || !s || !d) { Console.Printf("AJARTEST info %s: no crossing", what); return false; }
		double rot = OneSideTest.Turn(s, d);
		Vector2 want = OneSideTest.Through(s, d, tamPreFrom + tamPreSet);
		double off = (tamLand - want).Length(), angOff = Actor.DeltaAngle(tamLandAng, tamPreAng + rot);
		Console.Printf("AJARTEST info %s: from (%.1f,%.1f) facing %.0f to (%.1f,%.1f,%.1f) facing %.0f; turn %.0f; place off by %.3f, facing by %.3f; %d jumps",
			what, tamPreFrom.x, tamPreFrom.y, Actor.Normalize180(tamPreAng), tamLand.x, tamLand.y, tamLandZ, Actor.Normalize180(tamLandAng),
			Actor.Normalize180(rot), off, angOff, tamJumps);
		return tamJumps == 1 && off < 1 && abs(angOff) < 0.5;
	}

	double TamToLine(Vector2 p, int id)
	{
		Line l = FindLine(id);
		Vector2 a = l.v1.p, d = l.delta;
		double u = clamp(((p - a) dot d) / (d dot d), 0, 1);
		return (p - (a + d * u)).Length();
	}

	// A monster woken beside a face with the player beyond it: in `tics` it
	// comes no nearer to the face than its fence lets it, and crosses nothing.
	// `push`: an angle the imp is also driven at (8 a tic) all the while, where its own way to the player
	// would not take it to the face.
	bool TamFenceCase(Actor mo, int t, double ix, double iy, double px, double py, double pz, int face, double keep, string what, double push = -1)
	{
		int k = TamIn(t);
		if (k == 1)
		{
			mo.player.cheats &= ~CF_NOTARGET;
			Pose(mo, px, py, pz, 0);
			tamImp = Actor.Spawn("DoomImp", (ix, iy, level.PointInSector((ix, iy)).floorplane.ZatPoint((ix, iy))));
			tamImp.angle = tamImp.AngleTo(mo);
			tamImp.target = mo;
			tamImp.movedir = 8;     // no way it was going: Doom's chase would not turn it round towards the player at first
			tamImp.SetState(tamImp.SeeState);
			tamFrom = tamImp.pos.xy;
			tamJumps = 0;
			tamMinDist = TamToLine(tamImp.pos.xy, face);
			return false;
		}
		if (!tamImp) { Check(what, false); return true; }
		if ((tamImp.pos.xy - tamFrom).Length() > 64) tamJumps++;
		tamFrom = tamImp.pos.xy;
		if (push >= 0 && k < 150) tamImp.vel.xy = Actor.AngleToVector(push, 8);
		tamMinDist = min(tamMinDist, TamToLine(tamImp.pos.xy, face));
		if (k < 160) return false;
		Console.Printf("AJARTEST info %s: the imp from (%.0f,%.0f) is at (%.0f,%.0f), came %.1f near the face (kept off %.0f), %d jumps, its target %s",
			what, ix, iy, tamImp.pos.x, tamImp.pos.y, tamMinDist, keep, tamJumps, tamImp.target == mo ? "the player" : "other");
		Check(what, tamJumps == 0 && tamMinDist >= keep - 0.5 && tamImp.target == mo);
		tamImp.Destroy();
		mo.player.cheats |= CF_NOTARGET;
		return true;
	}

	void TamOneSided(Actor mo, int t)
	{
		switch (tamStep)
		{
		// site 1, the longer way east
		case 0:
			if (TamGo(mo, t, 5120, 2208, 0, 20)) { Check("eastIntoTheStretch", TamLanded(ODD1, X_IN, "eastIntoTheStretch") && InBox(mo, 5008, 2384, 5104, 2672)); TamNext(t); }
			break;
		case 1:
			if (TamGo(mo, t, 5056, 2440, 270, 15)) { Check("stretchBackOutWest", TamLanded(X_IN, ODD1, "stretchBackOutWest") && InBox(mo, 4992, 2112, 5200, 2304)); TamNext(t); }
			break;
		case 2:
			if (TamGo(mo, t, 5376, 2660, 90, 15)) { Check("stretchOutOfTheMouthEast", TamLanded(X_OUT, MOUTH1, "stretchOutOfTheMouthEast") && InBox(mo, 5216, 2112, 5440, 2304)); TamNext(t); }
			break;
		case 3:
			if (TamGo(mo, t, 5300, 2208, 180, 20)) { Check("westPlain", tamJumps == 0 && InBox(mo, 4992, 2112, 5200, 2304)); TamNext(t); }
			break;
		case 4:     // the longer way east, at 10 a tic by the generator's way (MapSpots 2001 on), then back west (2041 on)
			if (TamIn(t) == 1) { TamPose(mo, 5080, 2208, 0); TamStartRun(t); }
			else if (TamRun(mo, t, 2000, 10) || TamIn(t) > 400) { tamEast = t - tamT0; Check("theLongWayEastIsWalked", InBox(mo, 5300, 2112, 5440, 2304)); TamNext(t); }
			break;
		case 5:
			if (TamIn(t) == 1) { TamPose(mo, 5340, 2208, 180); TamStartRun(t); }
			else if (TamRun(mo, t, 2040, 10) || TamIn(t) > 400)
			{
				tamWest = t - tamT0;
				Console.Printf("AJARTEST info the longer way east: %d tics at 10 a tic, back west %d (x 5080 to 5340)", tamEast, tamWest);
				Check("theWayEastIsLonger", InBox(mo, 4992, 2112, 5120, 2304) && tamEast < 400 && tamEast * 10 > 1000 && tamWest * 10 < 320);
				TamNext(t);
			}
			break;
		// site 2, the hut bigger inside
		case 6:
			if (TamGo(mo, t, 1472, 800, 270, 15)) { Check("hutDoorIntoTheArchive", TamLanded(ODD2, ARCH_GATE, "hutDoorIntoTheArchive") && InBox(mo, 256, -1088, 1280, -320)); TamNext(t); }
			break;
		case 7:
			if (TamGo(mo, t, 768, -420, 90, 15)) { Check("archiveDoorOutOfTheHut", TamLanded(ARCH_GATE, ODD2, "archiveDoorOutOfTheHut") && InBox(mo, 1392, 704, 1552, 1000)); TamNext(t); }
			break;
		case 8:
			if (TamGo(mo, t, 1472, 600, 90, 15)) { Check("hutFrontPlainFromInside", tamJumps == 0 && InBox(mo, 1392, 704, 1552, 900)); TamNext(t); }
			break;
		case 9:
			if (TamGo(mo, t, 1472, 380, 90, 12)) { Check("intoTheHutFromBehind", tamJumps == 0 && InBox(mo, 1360, 464, 1584, 688)); TamNext(t); }
			break;
		case 10:    // round the hut: up its west side, then along its front past the door
			if (TamGo(mo, t, 1310, 420, 90, 36)) { Check("roundTheHut_west", tamJumps == 0 && mo.pos.y > 760); TamNext(t); }
			break;
		case 11:
			if (TamGo(mo, t, 1310, 770, 0, 34)) { Check("roundTheHut_front", tamJumps == 0 && mo.pos.x > 1620 && mo.pos.y > 760); TamNext(t); }
			break;
		// site 3, the turn-round
		case 12:
			if (TamGo(mo, t, 3560, 736, 180, 20)) { Check("hallIntoTheCloakroomPlain", tamJumps == 0 && InBox(mo, 3008, 512, 3392, 1024)); TamNext(t); }
			break;
		case 13:
			if (TamGo(mo, t, 3300, 736, 0, 15)) { Check("cloakroomDoorIntoTheOffice", TamLanded(ODD3, OFFICE_GATE, "cloakroomDoorIntoTheOffice") && InBox(mo, 2432, 3264, 2880, 3968) && abs(mo.pos.z - 256) < 1); TamNext(t); }
			break;
		case 14:
			if (TamGo(mo, t, 2752, 3880, 90, 15)) { Check("officeGateIntoTheCloakroom", TamLanded(OFFICE_GATE, ODD3, "officeGateIntoTheCloakroom") && InBox(mo, 3008, 512, 3392, 1024) && abs(mo.pos.z) < 1); TamNext(t); }
			break;
		case 15:    // the way back from the cloakroom to the start on foot, at 16.7 (MapSpots 2061 on)
			if (TamIn(t) == 1) { TamPose(mo, 3384, 736, 180); TamStartRun(t); }
			else if (TamRun(mo, t, 2060, TAM_RUN) || TamIn(t) > 600)
			{
				Console.Printf("AJARTEST info the cloakroom back to the start on foot: %d tics, at (%.0f,%.0f,%.0f)", t - tamT0, mo.pos.x, mo.pos.y, mo.pos.z);
				Check("cloakroomBackToTheHallOnFoot", InBox(mo, 3456, 256, 4544, 1280) && abs(mo.pos.z) < 1 && TamIn(t) <= 600);
				TamNext(t);
			}
			break;
		// the fences: an imp woken beside each face, the player beyond it
		case 16: if (TamFenceCase(mo, t, 5060, 2208, 5340, 2208, 0, ODD1, FENCE + 20, "fence1_oddSide")) TamNext(t); break;
		case 17: if (TamFenceCase(mo, t, 5360, 2208, 5060, 2208, 0, ODD1, FENCE + 20, "fence1_plainSide")) TamNext(t); break;
		case 18: if (TamFenceCase(mo, t, 1472, 900, 1472, 600, 0, ODD2, FENCE + 20, "fence2_yard")) TamNext(t); break;
		case 19: if (TamFenceCase(mo, t, 1472, 560, 1472, 900, 0, ODD2, FENCE + 20, "fence2_insideTheHut")) TamNext(t); break;
		case 20: if (TamFenceCase(mo, t, 768, -520, 1472, 900, 0, ARCH_GATE, FENCE + 20, "fence2_archiveDoor", 90)) TamNext(t); break;
		case 21: if (TamFenceCase(mo, t, 3250, 736, 3600, 736, 0, ODD3, FENCE + 20, "fence3_cloakroom")) TamNext(t); break;
		case 22: if (TamFenceCase(mo, t, 3560, 736, 3200, 736, 0, ODD3, 64 + 20, "fence3_hall")) TamNext(t); break;
		case 23: if (TamFenceCase(mo, t, 2752, 3820, 3200, 736, 0, OFFICE_GATE, FENCE + 20, "fence3_officeGate", 90)) TamNext(t); break;
		case 24:
			Console.Printf("AJARTEST oneSidedDone=1");
			TamNext(t);
			break;
		}
	}

	// MODE=8: the one-sided doorways seen (tools/smoke_MAP18_8.cfg)
	void TamOneSidedViews(Actor mo, int t)
	{
		static const double views[] = {
			5040, 2208, 0, 0,       // 0 the longer way: from the court's side, the odd face (the stretch in it) and its signs
			5130, 2140, 15, 0,      // 1 ... close, at a slant
			5420, 2208, 180, 0,     // 2 ... from the rotunda's side: a plain doorway, no sign
			5056, 2420, 90, 0,      // 3 in the stretch, from its way in
			5376, 2560, 90, 0,      // 4 the stretch's way out (the rotunda's side of the corridor in it)
			1472, 920, 270, 0,      // 5 the porter's hut from the yard: its door (the archive in it) and the signs
			1260, 960, 300, 0,      // 6 ... at a slant
			1472, 250, 90, 0,       // 7 the hut from behind: in by the back, its door plain from inside
			1472, 600, 90, 0,       // 8 inside the hut: the yard through its door
			768, -420, 270, 0,      // 9 the archive, from inside its door
			300, -1040, 40, 0,      // 10 the archive from its far corner
			768, -720, 90, 0,       // 11 the archive's door: the yard in it
			3720, 736, 180, 0,      // 12 the cloakroom's doorway from the entrance hall: plain, no sign
			3150, 736, 0, 0,        // 13 the doorway from inside the cloakroom: the office in it, and the signs
			3120, 920, 340, 0,      // 14 ... at a slant
			2752, 3640, 90, 0,      // 15 the office's gate: the cloakroom in it
			2540, 3700, 45, 0,      // 16 the office and its gate at a slant
			3250, 736, 0, 0         // 17 the doorway from inside the cloakroom, nearer
		};
		int i = t / 40;
		if (i >= views.Size() / 4) return;
		TamPose(mo, views[i * 4], views[i * 4 + 1], views[i * 4 + 2]);
		mo.pitch = views[i * 4 + 3];
		if (t % 40 == 0) Console.Printf("AJARTEST view=%d at (%.0f,%.0f)", i, views[i * 4], views[i * 4 + 1]);
	}
}
