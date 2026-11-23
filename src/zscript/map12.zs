// MAP12 "Going Up" (tools/map_institute2.py): the walkthrough for
// MAP=MAP12 tools/smoke.sh (run it with EXTRA=-nomonsters): RED in the hall's
// frame and the car sent up, the leaf in the car's frame, the booth's top
// button, key 1, key 2 by GREEN, VIOLET out of the store by RED, and from
// the car by the booth to the top and the night room.
extend class AjarHandler
{
	void Press(int tid, Actor mo)
	{
		let it = level.CreateActorIterator(tid);
		Actor b = it.Next();
		if (b) b.Activate(mo);
	}

	bool InLift(Actor mo) { return InBox(mo, -96, -96, 96, 96); }
	bool InBooth(Actor mo) { return mo.pos.z == 192 && InBox(mo, -1216, 160, -1040, 352); }

	// MODE 2: the store's hole and steps, on foot with empty hands: out of the
	// store and up, and from the top down and in (2026-11-23: mapcheck's LINTEL
	// said the hole's ceiling shut both; the walkthrough never walked them).
	void StoreHoleScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		if (t == 10) Pose(mo, 584, -400, -64, 90);
		Forward(mo, t, 10, 40);
		if (t == 60) { Console.Printf("AJARTEST info out: player (%.1f, %.1f, %.1f)", mo.pos.x, mo.pos.y, mo.pos.z); Check("outOfTheStoreByTheHole", mo.pos.z == 0 && mo.pos.y > -208); }
		if (t == 62) Pose(mo, 584, -176, 0, 270);
		Forward(mo, t, 62, 40);
		if (t == 112) { Console.Printf("AJARTEST info in: player (%.1f, %.1f, %.1f)", mo.pos.x, mo.pos.y, mo.pos.z); Check("intoTheStoreByTheHole", mo.pos.z == -64 && mo.pos.y < -288); }
	}

	void GoingUpScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		AjarFrame booth = FindFrame(106), inCar = FindFrame(110);
		AjarDoor hung = booth.door == a ? a : b, free = hung == a ? b : a;
		bool violet = carried && carried.args[1] == 5, red = carried && carried.args[1] == 1;
		if (t == 10) Check("leafHangsInBooth", booth.door && booth.door.IsPair() && booth.door.Shut());
		// RED in the hall's frame, the car sent to the first floor, and through RED
		if (t == 20) { Take(mo, 1); Pose(mo, -400, -480, 0, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
		if (t == 22) { Press(712, mo); Check("hallSendsCarUp", LiftMoving()); }
		Forward(mo, t, 24, 12);
		if (t == 80) Check("inCarOnFirst", InLift(mo) && mo.pos.z == 192 && LiftAt() == 192);
		// the leaf in the car's frame: the booth opens onto the car
		if (t == 82) { free.Used(mo); Pose(mo, 48, -48, 192, 0); inCar.Activate(mo); Check("leafInCar", !carried && free.frame == inCar && free.args[0] == 106 && !hung.Shut()); }
		Forward(mo, t, 86, 12);
		if (t == 100) Check("inBooth", InBooth(mo));
		if (t == 102) { Press(717, mo); Check("boothSendsCarToTop", LiftMoving()); }
		if (t == 104) Pose(mo, -1150, 256, 192, 180);
		Forward(mo, t, 104, 14);
		if (t == 160) Check("inCarAtTop", InLift(mo) && mo.pos.z == 384 && LiftAt() == 384);
		if (t == 160) Pose(mo, 0, 60, 384, 90);
		Forward(mo, t, 160, 30);
		if (t == 195) Check("onTop", mo.pos.z == 384 && mo.pos.y > 128);
		if (t == 196) Pose(mo, 720, 864, 384, 0);
		Forward(mo, t, 196, 6);
		if (t == 205) Check("key1", Has(mo, 1));
		// down by the booth to the first floor, for GREEN
		if (t == 207) Pose(mo, 0, 200, 384, 270);
		Forward(mo, t, 207, 22);
		if (t == 232) Pose(mo, 48, -48, 384, 0);
		Forward(mo, t, 232, 12);
		if (t == 246) { Check("inBoothAgain", InBooth(mo)); Press(716, mo); }
		if (t == 248) Pose(mo, -1150, 256, 192, 180);
		Forward(mo, t, 248, 14);
		if (t == 300) { Check("carBackOnFirst", InLift(mo) && mo.pos.z == 192 && !LiftMoving()); Take(mo, 3); }
		// from the car by RED's far side to the hall, GREEN in hand
		if (t == 302) Pose(mo, 48, 48, 192, 0);
		Forward(mo, t, 302, 12);
		if (t == 316) Check("inHallWithGreen", mo.pos.z == 0 && InBox(mo, -448, -832, 448, -128) && carried && carried.args[1] == 3);
		if (t == 318) { Pose(mo, -400, -480, 0, 180); FindFrame(101).Activate(mo); }
		if (t == 319) Check("swappedRedForGreen", red && FindFrame(101).door.args[1] == 3);
		Forward(mo, t, 320, 12);
		if (t == 334) Check("inBatteryRoom", InBox(mo, -1600, -640, -1216, -256));
		if (t == 335) Pose(mo, -1530, -300, 0, 180);
		Forward(mo, t, 335, 6);
		if (t == 345) Check("key2", Has(mo, 2) && red);
		if (t == 347) Pose(mo, -1280, -448, 0, 0);
		Forward(mo, t, 347, 12);
		// the store: lock 1, the drop, RED in a frame down there, VIOLET
		if (t == 363) { Check("backInHall", InBox(mo, -448, -832, 448, -128)); Pose(mo, 400, -480, 0, 0); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 400) Check("lock1Open", RoomOpen(302));
		Forward(mo, t, 400, 22);
		if (t == 430) Check("downInStoreWithRed", mo.pos.z == -64 && red);
		if (t == 432) { Pose(mo, 848, -608, -64, 0); FindFrame(107).Activate(mo); Check("redHungInStore", !carried && FindFrame(107).door != null); }
		if (t == 434) Take(mo, 5);
		if (t == 435) Check("tookViolet", violet);
		Forward(mo, t, 436, 12);
		if (t == 450) Check("fromStoreIntoCar", InLift(mo) && mo.pos.z == 192 && violet);
		// by the leaf to the booth; its frame takes no VIOLET; the top button; back
		if (t == 452) Pose(mo, 48, -48, 192, 0);
		Forward(mo, t, 452, 12);
		if (t == 466) { booth.Activate(mo); Check("boothFrameTakesALeafOnly", InBooth(mo) && violet && booth.door == hung); Press(717, mo); }
		if (t == 468) Pose(mo, -1150, 256, 192, 180);
		Forward(mo, t, 468, 14);
		if (t == 525) Check("atTopWithViolet", InLift(mo) && mo.pos.z == 384 && violet);
		if (t == 526) Pose(mo, 400, 860, 384, 90);
		if (t == 527) FindLine(301).Activate(mo, 0, SPAC_Use);
		if (t == 570) Check("locks1And2Open", RoomOpen(301));
		Forward(mo, t, 570, 14);
		if (t == 590) { Pose(mo, 520, 1120, 384, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 596, 12);
	}
}
