// MAP11 "By Appointment" (tools/map_institute1.py): the walkthrough for
// MAP=MAP11 tools/smoke.sh, by the Pair as tools/build.py prints it with
// RED kept out of the archive: a leaf in the lobby, its twin up by RED and
// down into the archive, VIOLET out through the two of them.
extend class AjarHandler
{
	void ByAppointmentScript(Actor mo, int t)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		if (t == 20) { Take(mo, 1); Pose(mo, 60, 256, 0, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
		if (t == 24) { a.Used(mo); Pose(mo, 700, 256, 0, 0); FindFrame(102).Activate(mo); Check("leafAloneShut", a.frame == FindFrame(102) && a.Shut()); }
		if (t == 28) { b.Used(mo); Check("tookTwin", carried == b); Pose(mo, 100, 256, 0, 180); }
		Forward(mo, t, 30, 22);
		if (t == 60) Check("onGalleryWithLeaf", mo.pos.z == 128 && mo.pos.x > 512 && mo.pos.x < 704 && carried == b);
		if (t == 65) Pose(mo, 608, 1060, 128, 90);
		Forward(mo, t, 65, 18);
		if (t == 110) Check("keyAndIntoArchive", Has(mo, 1) && mo.pos.z == 0 && mo.pos.y > 1152 && carried == b);
		if (t == 115) { Pose(mo, 860, 1312, 0, 0); FindFrame(106).Activate(mo); Check("archiveJoinedToLobby", !carried && a.args[0] == 106 && b.args[0] == 102); }
		if (t == 120) { Take(mo, 5); Check("tookViolet", carried && carried.args[1] == 5); Pose(mo, 800, 1312, 0, 0); }
		Forward(mo, t, 122, 24);
		if (t == 155) Check("inLobbyWithViolet", mo.pos.y < 512 && mo.pos.x < 768 && carried && carried.args[1] == 5);
		// the hole would not have it
		if (t == 160) Check("holeShutToADoor", (FindLine(SQUEEZE_ID).flags & Line.ML_BLOCK_PLAYERS) != 0);
		if (t == 165) { Pose(mo, 300, 960, 0, 180); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 200) Check("lockOpensWithKey1", RoomOpen(301));
		Forward(mo, t, 200, 14);
		if (t == 225) Check("inVestibule", mo.pos.x < 240 && mo.pos.y > 896);
		if (t == 230) { Pose(mo, 90, 768, 0, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 240, 12);
	}
}
