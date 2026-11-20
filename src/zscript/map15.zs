// MAP15 "On Reflection" (tools/map_institute5.py): the walkthrough for
// MAP=MAP15 tools/smoke.sh: the target only the glass shows, RED in 103 and
// a leaf in 101, its twin in the darkroom, the emitter (sensor B), RED's
// ambush unseen in the gallery and the leaf's seen in the hall; PINK, the
// door only the glass shows, and its far side; BLUE and through it to the
// periscope room, the twin in 104, the emitter (sensor C); keys 1 and 2,
// VIOLET and the night room.
// MAP=MAP15 MODE=3 tools/smoke.sh: the secret way out. RED in 103, PINK in
// 101, the emitter: the beam goes into PINK and out of its far side onto
// sensor D, which opens the steel door north of the periscope room. BLUE in
// 102, PINK down and carried through BLUE and that door, hung in the brass
// frame: the secret way out, the plain one untouched; out by it to MAP32.
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
		// (each carried for a few tics, long enough to set off its ambush: AmbushTick looks every 5)
		if (t == 102) { Take(mo, 1); Pose(mo, 384, 590, 0, 90); }
		if (t == 108) { FindFrame(103).Activate(mo); Check("redHung", !carried && FindFrame(103).door != null); }
		if (t == 109) { a.Used(mo); Pose(mo, 60, 320, 0, 180); }
		if (t == 115) FindFrame(101).Activate(mo);
		if (t == 116) { b.Used(mo); Pose(mo, -650, 128, 0, 180); FindFrame(106).Activate(mo); Check("pairJoined", !carried && !a.Shut() && !b.Shut()); }
		if (t == 118) { Press(721, mo); Pose(mo, 600, 60, 0, 90); }
		if (t > 118 && t < 330 && t % 10 == 0)
		{
			Actor beam = OptOne("AjarBeam");
			if (beam) Console.Printf("AJARTEST beam t=%d at (%.0f,%.0f,%.0f)", t, beam.pos.x, beam.pos.y, beam.pos.z);
		}
		if (t == 330) Check("beamOnSensorB", sensorB.done && !sensorC.done);
		if (t == 360) Check("firstCellOpen", RoomOpen(312) && !RoomOpen(313) && !RoomOpen(314));
		// RED's ambush came into the gallery: unseen; the leaf's into the hall: seen
		if (t == 361) Check("redAmbushUnseen", ambushHid[11] > 0 && !ambushShown[11]);
		if (t == 361) Check("leafAmbushSeen", ambushShown[18] > 0 && !ambushHid[18]);
		// the door only the glass shows, and where it leads
		if (t == 362) { Check("pinkUnseen", pink.bOnlyVisibleInMirrors && !pink.bInvisible); Pose(mo, 600, 900, 0, 270); pink.Used(mo); Check("pinkTakenByFeel", carried == pink); }
		if (t == 364) { Pose(mo, 320, 870, 0, 270); FindFrame(105).Activate(mo); Check("pinkHung", !carried && FindFrame(105).door == pink); }
		Forward(mo, t, 364, 20);
		if (t == 390) Check("inTheSecretRoom", InBox(mo, 1536, 900, 1856, 1156));
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
		// sensor C's ambushes come when the walker is back in the room: the
		// periscope room's (it stands there) seen, the gallery's unseen
		if (t == 731) Check("lateAmbushWaits", !ambushHid[23]);
		if (t == 790) Check("periAmbushSeen", ambushShown[23] > 0 && !ambushHid[23]);
		if (t == 791) Pose(mo, 128, 900, 0, 90);
		if (t == 850) Check("galleryAmbushUnseen", ambushHid[23] > 0);
		int u = t - 120;
		// key 2, VIOLET
		if (u == 732) Pose(mo, 840, 1790, 0, 270);
		Forward(mo, u, 732, 7);
		if (u == 742) Check("key2", Has(mo, 2));
		if (u == 744) { Take(mo, 5); Check("tookViolet", carried && carried.args[1] == 5); }
		// the door with locks 1 and 2, and the night room
		if (u == 746) { Pose(mo, 730, 128, 0, 0); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (u == 786) Check("locks1And2Open", RoomOpen(301));
		Forward(mo, u, 786, 16);
		if (u == 804) Check("pastTheLocks", mo.pos.x > 784 && violet);
		if (u == 807) { Pose(mo, 1066, -64, 0, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried && !secretOutBuilt); }
		Forward(mo, u, 814, 12);
	}

	// MAP=MAP15 MODE=3 tools/smoke.sh: the secret way out (see the top).
	void OnReflectionSecret(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarDoor pink = DoorOf(6);
		AjarTarget sensorB = TargetTagged(2), sensorC = TargetTagged(3), sensorD = TargetTagged(4);
		if (t == 10) Check("secretShut", !RoomOpen(314) && sensorD && sensorD.args[1] && !sensorD.done);
		// RED in 103, PINK in 101, the emitter
		if (t == 12) { Take(mo, 1); Pose(mo, 384, 590, 0, 90); FindFrame(103).Activate(mo); Check("redHung", !carried && FindFrame(103).door != null); }
		if (t == 14) { Take(mo, 6); Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); Check("pinkIn101", !carried && FindFrame(101).door == pink); }
		if (t == 15)
		{
			// the lab and the hall are fought through first: nothing stands in the beam's way
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
				if (a.bIsMonster && a.health > 0 && (InBox(a, -448, 1440, 1216, 1696) || InBox(a, 0, 0, 768, 640))) a.DamageMobj(null, null, a.health, 'None');
		}
		if (t == 16) { Press(721, mo); Pose(mo, 600, 60, 0, 90); }
		if (t > 16 && t < 250 && t % 10 == 0)
		{
			Actor beam = OptOne("AjarBeam");
			if (beam) Console.Printf("AJARTEST beam t=%d at (%.0f,%.0f,%.0f)", t, beam.pos.x, beam.pos.y, beam.pos.z);
		}
		if (t == 250) Check("beamOnSensorD", sensorD.done && !sensorB.done && !sensorC.done);
		if (t == 280) Check("secretDoorOpen", RoomOpen(314) && !RoomOpen(312) && !RoomOpen(313));
		// BLUE in 102, PINK down, and through BLUE with it
		if (t == 282) { Take(mo, 2); Pose(mo, 708, 320, 0, 0); FindFrame(102).Activate(mo); Check("blueHung", !carried && FindFrame(102).door != null); }
		if (t == 284) { Pose(mo, 60, 320, 0, 180); FindFrame(101).Activate(mo); Check("pinkTakenDown", carried == pink); }
		if (t == 286) Pose(mo, 650, 320, 0, 0);
		Forward(mo, t, 286, 24);
		if (t == 314) Check("inThePeriscopeRoomWithPink", InBox(mo, 1536, 0, 2176, 640) && carried == pink);
		// north through the steel door, on foot, into the secret room
		if (t == 316) Pose(mo, 1696, 600, 0, 90);
		Forward(mo, t, 316, 45);
		if (t == 366) Check("inTheSecretRoomOnFoot", InBox(mo, 1536, 900, 1856, 1156) && carried == pink);
		// PINK in the brass frame: the secret way out, and the plain one as it was
		if (t == 368) { Pose(mo, 1800, 1028, 0, 0); FindFrame(193).Activate(mo); }
		if (t == 369) Check("secretWayOutBuilt", secretOutBuilt && !carried && pink.nailer == pink && FindFrame(193).door == pink);
		if (t == 369) Check("plainWayOutUntouched", !wayOutBuilt && !FindFrame(190).door && FindLine(590).special == 0 && FindLine(591).special == 244);
		Forward(mo, t, 370, 12);                    // and out: the level ends (outBySecretWayOut)
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
			1696, 420, 0, 90, 0,    // the periscope room: the steel door north, to the secret room
			1600, 1028, 0, 0, 0    // the secret room: the brass frame for PINK, sensor D in its recess
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}
}
