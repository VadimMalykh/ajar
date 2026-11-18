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
		if (t == 20) { Take(mo, 1); Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
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
}
