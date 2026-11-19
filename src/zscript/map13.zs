// MAP13 "Sight Unseen" (tools/map_institute3.py): the walkthrough for
// MAP=MAP13 tools/smoke.sh (run it with EXTRA=-nomonsters): GREEN in the
// hall and the target shot through it, RED in 101 and a leaf in 102 that
// faces it, its twin in the darkroom, the emitter, key 1 by RED, key 2 and
// VIOLET from the cells, and the night room.
extend class AjarHandler
{
	AjarTarget SightTarget(bool sensor)
	{
		let ti = ThinkerIterator.Create("AjarTarget");
		AjarTarget x;
		while (x = AjarTarget(ti.Next())) if ((x.args[1] != 0) == sensor) return x;
		return null;
	}

	void SightUnseenScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		AjarTarget shot = SightTarget(false), sensor = SightTarget(true);
		bool violet = carried && carried.args[1] == 5, green = carried && carried.args[1] == 3;
		// GREEN in the hall, and the target at the far end of its cell
		if (t == 10) Check("rangeShut", !RoomOpen(311) && !RoomOpen(312) && !RoomOpen(313));
		if (t == 20) { Take(mo, 3); Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); Check("greenHung", !carried && FindFrame(101).door != null); }
		if (t == 22) Pose(mo, 300, 320, 0, 180);
		if (t == 24) mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff");
		if (t == 26) Check("targetShotThroughGreen", shot.done);
		if (t == 60) Check("rangeOpen", RoomOpen(311) && !RoomOpen(312));
		// GREEN's far side has a rail before it: nobody walks through
		Forward(mo, t, 60, 40);
		if (t == 102) Check("noWayThroughGreen", !InBox(mo, -384, 1088, 88, 1408));
		// the range; RED swapped in for GREEN, which goes in the frame that faces a wall
		if (t == 104) Pose(mo, 128, 600, 0, 90);
		Forward(mo, t, 104, 34);
		if (t == 140) { Check("inRange", InBox(mo, -448, 816, 1216, 1072)); Take(mo, 1); }
		if (t == 142) { Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); Check("redSwappedIn", carried && carried.args[1] == 3 && FindFrame(101).door.args[1] == 1); }
		if (t == 144) { Pose(mo, 384, 590, 0, 90); FindFrame(103).Activate(mo); Check("greenPutAside", !carried); }
		// the darkroom's frame takes a leaf only; the beam with no leaf in its way does nothing
		if (t == 146) { Take(mo, 2); Pose(mo, -650, 128, 0, 180); FindFrame(104).Activate(mo); Check("darkroomFrameTakesALeafOnly", carried && carried.args[1] == 2 && FindFrame(104).door == null); }
		if (t == 148) { Pose(mo, -288, 870, 0, 270); FindFrame(105).Activate(mo); Check("bluePutAside", !carried); }
		if (t == 150) { Press(721, mo); Pose(mo, 384, 100, 0, 90); }
		if (t == 290) Check("beamIntoTheWallDoesNothing", !sensor.done);
		// a leaf in 102, its twin in the darkroom, and the emitter again
		if (t == 292) { a.Used(mo); Pose(mo, 708, 320, 0, 0); FindFrame(102).Activate(mo); }
		if (t == 294) { b.Used(mo); Pose(mo, -650, 128, 0, 180); FindFrame(104).Activate(mo); Check("pairJoined", !carried && !a.Shut() && !b.Shut()); }
		if (t == 296) { Press(721, mo); Pose(mo, -400, 60, 0, 90); }
		if (t == 460) Check("beamOnSensor", sensor.done);
		if (t == 490) Check("cellsOpen", RoomOpen(312) && RoomOpen(313));
		// key 1, beyond the pit, by RED; down into the pit and up its steps
		if (t == 492) Pose(mo, 300, 320, 0, 180);
		Forward(mo, t, 492, 40);
		if (t == 535) Check("beyondThePit", InBox(mo, 992, 816, 1216, 1072) && mo.pos.z == 0);
		if (t == 536) Pose(mo, 1170, 880, 0, 270);
		Forward(mo, t, 536, 6);
		if (t == 545) Check("key1", Has(mo, 1));
		if (t == 546) Pose(mo, 1100, 1030, 0, 180);
		Forward(mo, t, 546, 80);
		if (t == 630) Check("outOfThePit", mo.pos.z == 0 && InBox(mo, -448, 816, 544, 1072));
		// GREEN's cell: key 2
		if (t == 632) Pose(mo, -128, 1040, 0, 90);
		Forward(mo, t, 632, 16);
		if (t == 650) Check("inGreensCell", InBox(mo, -384, 1088, 128, 1408));
		if (t == 652) Pose(mo, -340, 1160, 0, 270);
		Forward(mo, t, 652, 6);
		if (t == 660) Check("key2", Has(mo, 2));
		// BLUE's cell: the lens store is shut, and VIOLET in it is not to be had
		if (t == 662) Pose(mo, 480, 1040, 0, 90);
		Forward(mo, t, 662, 16);
		if (t == 680) Check("inBluesCell", InBox(mo, 384, 1088, 896, 1408));
		if (t == 681) Pose(mo, 640, 1300, 0, 90);
		Forward(mo, t, 681, 16);
		if (t == 698) Check("lensStoreShut", !RoomOpen(314) && mo.pos.y < 1408);
		// BLUE where the leaf hung: the beam comes out in BLUE's cell, onto its sensor
		if (t == 700) { Take(mo, 2); Pose(mo, 708, 320, 0, 0); FindFrame(102).Activate(mo); Check("blueSwappedIn", carried && carried.args[1] == 8 && FindFrame(102).door.args[1] == 2); }
		if (t == 702) { Pose(mo, -288, 870, 0, 270); FindFrame(105).Activate(mo); Check("leafPutAside", !carried); }
		if (t == 704) { Press(721, mo); Pose(mo, -400, 60, 0, 90); }
		if (t == 900) Check("lensStoreOpen", RoomOpen(314));
		if (t == 902) Pose(mo, 640, 1300, 0, 90);
		Forward(mo, t, 902, 24);
		if (t == 928) { Check("inLensStore", InBox(mo, 384, 1424, 896, 1744)); Take(mo, 5); }
		if (t == 930) Check("tookViolet", violet);
		// the door with locks 1 and 2: beyond it a steel door, shut
		if (t == 932) { Pose(mo, 730, 128, 0, 0); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 972) Check("locks1And2Open", RoomOpen(301));
		Forward(mo, t, 972, 16);
		if (t == 990) Check("pastTheLocks", mo.pos.x > 784 && violet);
		if (t == 991) Pose(mo, 944, 150, 0, 270);
		Forward(mo, t, 991, 16);
		if (t == 1008) Check("nightRoomShut", !RoomOpen(315) && mo.pos.y > 64);
		// VIOLET hung in the hall, the target beside the brass frame shot through it, and VIOLET down again
		if (t == 1010) { Pose(mo, 384, 590, 0, 90); FindFrame(103).Activate(mo); Check("violetHung", carried && carried.args[1] == 3 && FindFrame(103).door.args[1] == 5); }
		if (t == 1012) Pose(mo, 386, 500, 0, 97.5);
		if (t == 1014) mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff");
		if (t == 1050) Check("nightRoomOpen", RoomOpen(315));
		if (t == 1052) { Pose(mo, 384, 590, 0, 90); FindFrame(103).Activate(mo); Check("violetDownAgain", carried && carried.args[1] == 5); }
		if (t == 1054) Pose(mo, 944, 150, 0, 270);
		Forward(mo, t, 1054, 20);
		if (t == 1076) Check("inNightRoom", InBox(mo, 784, -192, 1104, 64) && violet);
		if (t == 1078) { Pose(mo, 1066, -64, 0, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 1084, 12);
	}

	// MAP13's tour of what is its own: MAP=MAP13 MODE=2 tools/smoke.sh (run it with EXTRA=-nomonsters).
	void SightUnseenViews()
	{
		static const double v[] = {
			512, 200, 0, 270, 0,    // the hall: the chart of the beam
			224, 340, 0, 90, 15,    // the hall: an optical bench
			-384, 110, 0, 90, 0,    // the darkroom: the safelight, prints on a line
			-250, 944, 0, 180, 0,    // the range: the emitter's lamp, its button, the desk
			300, 1010, 0, 270, 0,    // the range's marks
			-32, 1010, 0, 270, 15,    // the range: a bench
			800, 1616, 0, 0, 0    // the lens store: racks of lenses
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}
}
