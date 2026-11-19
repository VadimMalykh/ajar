// MAP15 "On Reflection" (tools/map_institute5.py): the walkthrough for
// MAP=MAP15 tools/smoke.sh: the target only the glass shows, RED in 103 and
// a leaf in 101, its twin in the darkroom, the emitter (sensor B); PINK, the
// door only the glass shows, and its far side; BLUE and through it to the
// periscope room, the twin in 104, the emitter (sensor C); keys 1 and 2,
// VIOLET and the night room.
extend class AjarHandler
{
	AjarTarget TargetTagged(int tag)
	{
		let ti = ThinkerIterator.Create("AjarTarget");
		AjarTarget x;
		while (x = AjarTarget(ti.Next())) if (x.args[0] == tag) return x;
		return null;
	}

	void OnReflectionScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1), pink = DoorOf(6);
		AjarTarget shot = TargetTagged(1), sensorB = TargetTagged(2), sensorC = TargetTagged(3);
		bool violet = carried && carried.args[1] == 5;
		// the target on the hall's north wall, which only the mirror shows
		if (t == 10) Check("allShut", !RoomOpen(311) && !RoomOpen(312) && !RoomOpen(313));
		if (t == 12) Check("targetUnseen", shot.bOnlyVisibleInMirrors);
		if (t == 20) Pose(mo, 240, 560, 0, 90);
		if (t == 24) mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff");
		if (t == 26) Check("targetInTheGlassShot", shot.done && !shot.bOnlyVisibleInMirrors);
		if (t == 60) Check("galleryOpen", RoomOpen(311));
		if (t == 64) Pose(mo, 128, 600, 0, 90);
		Forward(mo, t, 64, 34);
		if (t == 100) Check("inGallery", InBox(mo, -448, 816, 704, 1264));
		// RED in 103, a leaf in 101, its twin in the darkroom, the emitter
		if (t == 102) { Take(mo, 1); Pose(mo, 384, 590, 0, 90); FindFrame(103).Activate(mo); Check("redHung", !carried && FindFrame(103).door != null); }
		if (t == 106) { a.Used(mo); Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); }
		if (t == 110) { b.Used(mo); Pose(mo, -650, 128, 0, 180); FindFrame(106).Activate(mo); Check("pairJoined", !carried && !a.Shut() && !b.Shut()); }
		if (t == 112) { Press(721, mo); Pose(mo, 600, 60, 0, 90); }
		if (t > 112 && t < 330 && t % 10 == 0)
		{
			Actor beam = OptOne("AjarBeam");
			if (beam) Console.Printf("AJARTEST beam t=%d at (%.0f,%.0f,%.0f)", t, beam.pos.x, beam.pos.y, beam.pos.z);
		}
		if (t == 330) Check("beamOnSensorB", sensorB.done && !sensorC.done);
		if (t == 360) Check("firstCellOpen", RoomOpen(312) && !RoomOpen(313));
		// the door only the glass shows, and where it leads
		if (t == 362) { Check("pinkUnseen", pink.bOnlyVisibleInMirrors && !pink.bInvisible); Pose(mo, 600, 900, 0, 270); pink.Used(mo); Check("pinkTakenByFeel", carried == pink); }
		if (t == 364) { Pose(mo, 320, 870, 0, 270); FindFrame(105).Activate(mo); Check("pinkHung", !carried && FindFrame(105).door == pink); }
		Forward(mo, t, 364, 20);
		if (t == 390) Check("inTheSecretRoom", InBox(mo, 1536, 900, 1792, 1156));
		// key 1 and BLUE out of the first cell; through BLUE to the periscope room
		if (t == 392) Pose(mo, -340, 1790, 0, 270);
		Forward(mo, t, 392, 7);
		if (t == 402) Check("key1", Has(mo, 1));
		if (t == 404) { Take(mo, 2); Pose(mo, 708, 320, 0, 0); FindFrame(102).Activate(mo); Check("blueHung", !carried && FindFrame(102).door != null); }
		if (t == 406) Pose(mo, 650, 320, 0, 0);
		Forward(mo, t, 406, 24);
		if (t == 434) Check("inThePeriscopeRoom", InBox(mo, 1536, 0, 2176, 640));
		// the twin out of the darkroom and into 104
		if (t == 436) { Pose(mo, -650, 128, 0, 180); FindFrame(106).Activate(mo); Check("twinTakenDown", carried == b); }
		if (t == 438) { Pose(mo, 1590, 576, 0, 180); FindFrame(104).Activate(mo); Check("twinIn104", !carried && !a.Shut() && !b.Shut()); }
		if (t == 440) { Press(721, mo); Pose(mo, 1800, 200, 0, 90); }
		if (t > 440 && t < 700 && t % 10 == 0)
		{
			Actor beam = OptOne("AjarBeam");
			if (beam) Console.Printf("AJARTEST beam t=%d at (%.0f,%.0f,%.0f)", t, beam.pos.x, beam.pos.y, beam.pos.z);
		}
		if (t == 700) Check("beamOnSensorC", sensorC.done);
		if (t == 730) Check("secondCellOpen", RoomOpen(313));
		// key 2, VIOLET
		if (t == 732) Pose(mo, 840, 1790, 0, 270);
		Forward(mo, t, 732, 7);
		if (t == 742) Check("key2", Has(mo, 2));
		if (t == 744) { Take(mo, 5); Check("tookViolet", carried && carried.args[1] == 5); }
		// the door with locks 1 and 2, and the night room
		if (t == 746) { Pose(mo, 730, 128, 0, 0); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 786) Check("locks1And2Open", RoomOpen(301));
		Forward(mo, t, 786, 16);
		if (t == 804) Check("pastTheLocks", mo.pos.x > 784 && violet);
		if (t == 807) { Pose(mo, 1066, -64, 0, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 814, 12);
	}

	// MAP15's tour of what is its own: MAP=MAP15 MODE=2 tools/smoke.sh.
	void OnReflectionViews()
	{
		static const double v[] = {
			120, 560, 0, 315, 0,    // the hall: the mirror aslant, and in it the target on the north wall
			60, 320, 0, 0, 0,    // the hall from frame 101: the mirror shows frame 103
			128, 870, 0, 80, 0,    // the gallery: nobody, and the glass full of them
			600, 1000, 0, 90, 0,    // the gallery: PINK behind you, in the glass
			600, 1100, 0, 270, 0,    // the gallery: where PINK is, seen directly
			1600, 320, 0, 0, 0,    // the periscope room: its two mirrors
			1700, 576, 0, 0, 0,    // the periscope room: the way the beam goes
			1600, 1028, 0, 0, 0    // the secret room: the secret way out
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}
}
