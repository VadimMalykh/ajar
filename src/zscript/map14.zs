// MAP14 "On the Level" (tools/map_institute4.py): the walkthrough for
// MAP=MAP14 tools/smoke.sh (run it with EXTRA=-nomonsters): RED in the
// canteen's frame and the car sent to the top, key 1, the car sent to the
// first floor and the gap down to it, GREEN in the brass frame there for key
// 2, VIOLET out of the safe room into the car's brass frame, BLUE out of the
// cashier's office swapped in for GREEN: the loop, closed while the car
// stands at the first floor and open while it is anywhere else.
extend class AjarHandler
{
	bool InStaffLift(Actor mo) { return InBox(mo, -96, -128, 96, 128); }
	bool InAccounts(Actor mo) { return (mo.pos.z == 192 || mo.pos.z == 232) && InBox(mo, -896, -96, -128, 608); }

	void OnTheLevelScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame inCar = FindFrame(190), onFirst = FindFrame(191);
		// RED in the canteen's frame, the car sent to the top, and through RED
		if (t == 10) Check("noLoopYet", !chainLen && !chainHung);
		if (t == 20) { Take(mo, 1); Pose(mo, -400, -544, 0, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
		if (t == 22) { Press(712, mo); Check("canteenSendsCarToTop", LiftMoving()); }
		Forward(mo, t, 24, 12);
		if (t == 130) Check("inCarAtTop", InStaffLift(mo) && mo.pos.z == 384 && LiftAt() == 384);
		if (t == 132) Pose(mo, 0, 100, 384, 90);
		Forward(mo, t, 132, 30);
		if (t == 165) Check("onTop", mo.pos.z == 384 && mo.pos.y > 160);
		if (t == 166) Pose(mo, 820, 860, 384, 0);
		Forward(mo, t, 166, 6);
		if (t == 175) Check("key1", Has(mo, 1));
		// the top's button sends the car to the first floor; down the gap after it
		if (t == 176) { Press(713, mo); Check("topSendsCarToFirst", LiftMoving()); }
		if (t == 178) Pose(mo, -80, 464, 384, 180);
		Forward(mo, t, 178, 9);
		if (t == 235) Check("downTheGapToFirst", InAccounts(mo) && LiftAt() == 192);
		// GREEN in the brass frame: a frame like any other. Key 2
		if (t == 236) { Take(mo, 3); Pose(mo, -850, 0, 192, 180); onFirst.Activate(mo); Check("greenInBrassFrame", !carried && onFirst.door != null && !chainLen); }
		Forward(mo, t, 238, 12);
		if (t == 254) Check("inColdStore", InBox(mo, -1600, -640, -1216, -256));
		if (t == 255) Pose(mo, -1530, -300, 0, 180);
		Forward(mo, t, 255, 6);
		if (t == 265) Check("key2", Has(mo, 2));
		if (t == 267) Pose(mo, -1280, -448, 0, 0);
		Forward(mo, t, 267, 12);
		if (t == 283) Check("backOnFirst", InAccounts(mo));
		// down the gap to the canteen, the car to the top, through RED, the safe room
		if (t == 284) Pose(mo, -336, -60, 192, 270);
		Forward(mo, t, 284, 24);
		if (t == 330) { Check("downTheGapToCanteen", mo.pos.z == 0 && InBox(mo, -448, -896, 448, -160)); Press(712, mo); }
		if (t == 331) Pose(mo, -400, -544, 0, 180);
		Forward(mo, t, 332, 12);
		if (t == 400) Check("inCarAtTopAgain", InStaffLift(mo) && mo.pos.z == 384 && LiftAt() == 384);
		if (t == 402) { Pose(mo, 400, 890, 384, 90); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 442) Check("lock2Open", RoomOpen(301));
		Forward(mo, t, 442, 14);
		if (t == 460) Take(mo, 5);
		if (t == 461) Check("tookViolet", carried && carried.args[1] == 5 && mo.pos.y > 944);
		// VIOLET in the car's brass frame; the car to the first floor again
		if (t == 462) { Pose(mo, 48, 0, 384, 0); inCar.Activate(mo); Check("violetInCar", !carried && inCar.door != null && !chainLen && !chainHung); }
		if (t == 464) { Pose(mo, 0, 220, 384, 90); Press(713, mo); }
		if (t == 466) Pose(mo, -80, 464, 384, 180);
		Forward(mo, t, 466, 9);
		if (t == 520) Check("onFirstAgain", InAccounts(mo) && LiftAt() == 192);
		// the cashier's office: BLUE, swapped in for GREEN. The loop is closed
		if (t == 522) { Pose(mo, -512, 570, 192, 90); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 562) Check("lock1Open", RoomOpen(302));
		Forward(mo, t, 562, 14);
		if (t == 580) { Take(mo, 2); Check("tookBlue", carried && carried.args[1] == 2 && mo.pos.y > 624); }
		if (t == 582) { Pose(mo, -850, 0, 192, 180); onFirst.Activate(mo); Check("loopClosed", chainLen == 2 && wayOutBuilt && carried && carried.args[1] == 3); }
		// the car sent away (as from the canteen): the same doors, and only a way to the car
		if (t == 584) LiftSend(700, 384);
		if (t == 590) Check("movingCarOpensLoop", !chainLen && chainHung);
		if (t == 640) Check("carAwayLoopOpen", !chainLen && chainHung && LiftAt() == 384);
		Forward(mo, t, 640, 12);
		if (t == 656) Check("onTheLineByADoorOnly", !onTheLine && InBox(mo, 1280, -640, 1600, -384));
		Forward(mo, t, 656, 40);
		if (t == 700) Check("byTheLineIntoTheCar", InStaffLift(mo) && mo.pos.z == 384);
		// the car back at the first floor (as from the top): closed again, and out by it
		if (t == 702) LiftSend(700, 192);
		if (t == 760) Check("levelAgain", chainLen == 2 && LiftAt() == 192 && InStaffLift(mo));
		if (t == 762) Pose(mo, 48, 0, 192, 0);
		Forward(mo, t, 762, 70);
	}

	// MAP14's tour: MAP=MAP14 MODE=2 tools/smoke.sh (run it with EXTRA=-nomonsters).
	void OnTheLevelViews()
	{
		static const double v[] = {
			0, -840, 0, 90, 0,    // the canteen from the start
			-272, -500, 0, 270, 15,    // a table
			250, -320, 0, 0, 0,    // the kitchen's hatch, the menu
			656, -340, 0, 270, 8,    // the kitchen: the range, pans
			-180, 0, 192, 180, 0,    // accounts from the landing: the brass frame across the room
			-640, 330, 192, 270, 20,    // a desk
			-520, 330, 192, 115, 0,    // the plan
			-256, 330, 192, 90, 0,    // filing cabinets
			-512, 700, 192, 90, 0,    // the cashier's window
			0, 260, 384, 60, 0,    // the director's floor
			400, 380, 384, 90, 15,    // the director's desk
			544, 760, 384, 90, 0,    // where the portrait hung
			256, 760, 384, 90, 0,    // the bookcase
			400, 1020, 384, 90, 0,    // the safe
			48, 0, 0, 180, 0    // in the car: the torn-out panel, the landing
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}
}
