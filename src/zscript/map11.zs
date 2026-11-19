// MAP11 "By Appointment" (tools/map_institute1.py): the walkthrough for
// MAP=MAP11 tools/smoke.sh, by the Pair: RED and GREEN hung in the lobby, a
// leaf in the corridor, its twin up by RED and down into the archive, VIOLET
// out through the two of them, key 2 by GREEN, and into the night room.
extend class AjarHandler
{
	bool InBox(Actor mo, double x1, double y1, double x2, double y2) { return mo.pos.x > x1 && mo.pos.x < x2 && mo.pos.y > y1 && mo.pos.y < y2; }

	void ByAppointmentScript(Actor mo, int t)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		bool violet = carried && carried.args[1] == 5;
		// the archive's frames are barred to RED
		if (t == 10) { Take(mo, 1); Pose(mo, 1320, 1532, 0, 0); FindFrame(106).Activate(mo); Check("archiveBarredToRed", carried && carried.args[1] == 1 && FindFrame(106).door == null); }
		if (t == 20) { Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
		if (t == 23) { Take(mo, 3); Pose(mo, 960, 320, 0, 0); FindFrame(102).Activate(mo); Check("greenHung", !carried && FindFrame(102).door != null); }
		if (t == 26) { a.Used(mo); Pose(mo, 440, 736, 0, 180); FindFrame(103).Activate(mo); Check("leafAloneShut", a.frame == FindFrame(103) && a.Shut()); }
		if (t == 30) { b.Used(mo); Check("tookTwin", carried == b); Pose(mo, 100, 320, 0, 180); }
		Forward(mo, t, 34, 22);
		if (t == 62) Check("onGalleryWithLeaf", mo.pos.z == 128 && InBox(mo, 656, 1120, 1360, 1312) && carried == b);
		if (t == 66) Pose(mo, 700, 1240, 128, 90);
		Forward(mo, t, 66, 16);
		if (t == 105) Check("key1AndIntoArchive", Has(mo, 1) && mo.pos.z == 0 && InBox(mo, 656, 1312, 1360, 1760) && carried == b);
		if (t == 110) { Pose(mo, 1320, 1532, 0, 0); FindFrame(106).Activate(mo); Check("archiveJoinedToCorridor", !carried && a.args[0] == 106 && b.args[0] == 103); }
		if (t == 115) { Take(mo, 5); Pose(mo, 1260, 1532, 0, 0); }
		if (t == 116) Check("tookViolet", violet);
		Forward(mo, t, 117, 24);
		if (t == 150) Check("inCorridorWithViolet", InBox(mo, 384, 640, 640, 1664) && violet);
		// neither hole would have it
		if (t == 155) Check("holesShutToADoor", (FindLine(SQUEEZE_ID).flags & Line.ML_BLOCK_PLAYERS) != 0);
		// the pump room by GREEN, door in hand, and back the same way
		if (t == 160) Pose(mo, 900, 320, 0, 0);
		Forward(mo, t, 162, 22);
		if (t == 190) Check("inPumpRoom", mo.pos.z == 32 && InBox(mo, -256, 1296, 368, 1664) && violet);
		if (t == 192) Pose(mo, -216, 1590, 32, 90);
		Forward(mo, t, 192, 7);
		if (t == 205) Check("key2", Has(mo, 2));
		if (t == 207) Pose(mo, -200, 1488, 32, 180);
		Forward(mo, t, 208, 20);
		if (t == 235) Check("backInLobbyWithViolet", InBox(mo, 0, 0, 1024, 640) && violet);
		if (t == 240) { Pose(mo, 512, 1630, 0, 90); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 280) Check("locks1And2Open", RoomOpen(301));
		Forward(mo, t, 280, 14);
		if (t == 300) Check("inExperimentHall", InBox(mo, -128, 1680, 624, 2320));
		if (t == 305) { Pose(mo, 370, 2528, 0, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 312, 12);
	}

	// MAP11's tour (see PartyWallViews): MAP=MAP11 MODE=2, for the look board
	// (tools/board11_shots.sh).
	void ByAppointmentViews()
	{
		static const double v[] = {
			512, 60, 0, 90, 0,             // the lobby from the start: the desk, the corridor beyond
			512, 300, 0, 270, 0,           // the street doors
			100, 300, 0, 75, -8,           // the lobby's long wall
			600, 300, 0, 180, 0,           // west: a frame, a TEAL leaf, the cloakroom's way in
			420, 300, 0, 0, 0,             // east: the frame facing it, the other leaf
			900, 300, 0, 101, -8,          // the clock, the notice
			640, 250, 0, 60, 0,            // the desk from the side, a pillar
			-50, 160, 0, 180, 0,           // the cloakroom: the counter, coats
			512, 600, 0, 90, 0,            // the corridor
			610, 880, 0, 172, 0,           // its west wall: a frame, the way into the lab
			410, 832, 0, 0, 0,             // its east wall: the way into the canteen
			512, 1400, 0, 90, 0,           // its far end: the door with two locks, the hatch, the hole
			600, 1472, 0, 180, 0,          // the pump room's hatch
			420, 1524, 0, 0, 0,            // the hole into the archive
			340, 1024, 0, 180, 0,          // the lab from its way in
			0, 1000, 0, 90, 0,             // the lab: the blackboard
			-200, 1150, 0, 320, 0,         // the lab from its far corner: benches, cabinets
			690, 832, 0, 0, -6,            // the canteen from its way in: tables, the balcony
			1000, 760, 0, 90, -12,         // the gallery's front
			960, 1000, 0, 270, 0,          // the canteen's south wall: the menu
			700, 1216, 128, 0, 0,          // on the gallery: RED's far side at its end
			1000, 1290, 128, 270, 18,      // from the gallery, down into the canteen
			1312, 1060, 128, 270, 8,       // along the balcony to its south end
			1000, 1150, 128, 90, 22,       // from the gallery, down into the archive
			700, 1390, 0, 0, 0,            // the archive: along the stacks' ends
			912, 1420, 0, 90, 0,           // between two stacks
			1104, 1730, 0, 15, 0,          // the archive: VIOLET, a frame
			900, 1730, 0, 170, 0,          // its north wall: the card index, a frame
			330, 1480, 32, 180, 0,         // the pump room from its hatch: tanks, GREEN's far side
			256, 1540, 32, 90, 0,          // the pump room: gauges
			-200, 1340, 32, 330, 0,        // the pump room from its far corner
			512, 1730, 0, 125, 0,          // the experiment hall from its door
			248, 1790, 0, 90, 0,           // the machine
			80, 1792, 0, 180, 0,           // the desk it was run from
			248, 2130, 0, 90, 0,           // the way to the night room, the platforms
			500, 2100, 0, 215, 0,          // the hall from its far side: the door
			248, 2360, 0, 90, 0            // the way to the night room
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}
}
