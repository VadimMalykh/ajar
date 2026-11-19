// MAP16 "Watch Your Step" (tools/map_institute6.py): the walkthrough for
// MAP=MAP16 tools/smoke.sh. The head's leaf is part of the building and
// shut; the player's leaf hung at the foot, and the stair goes round; taken
// down, it is cut, and made again; RED and GREEN for the keys; VIOLET up by
// the stair to the brass frame behind locks 1 and 2.
extend class AjarHandler
{
	void WatchYourStepScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame head = FindFrame(110), foot = FindFrame(104);
		if (t == 10) Check("headIsShutAndFixed", head.door && head.door.Shut() && head.door.nailer == head.door);
		if (t == 12) { Pose(mo, -200, 160, 384, 180); head.Activate(mo); Check("headIsNotTaken", !carried && head.door != null); }
		if (t == 20)
		{
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next())) if (d.IsPair() && !d.frame) d.Used(mo);
		}
		if (t == 21) Check("tookLeaf", carried && carried.IsPair());
		// hung at the foot: the way up is down
		if (t == 24) { Pose(mo, -200, -128, 0, 180); foot.Activate(mo); Check("stairJoined", !carried && foot.door && foot.door.args[0] == 110 && head.door.args[0] == 104); }
		Forward(mo, t, 26, 14);
		if (t == 45) Check("upByTheStair", mo.pos.z == 384 && InBox(mo, -256, 64, 64, 256));
		// taken down, both ends are shut; and made again
		if (t == 46) { Pose(mo, -200, -128, 0, 180); foot.Activate(mo); Check("stairCut", carried && carried.IsPair() && head.door.Shut() && !foot.door); }
		if (t == 48) { foot.Activate(mo); Check("stairJoinedAgain", !carried && head.door.args[0] == 104); }
		// RED in the stores' frame: the strongroom, key 1
		if (t == 50) { Take(mo, 1); Pose(mo, -1340, -608, 0, 180); FindFrame(105).Activate(mo); Check("redHung", !carried && FindFrame(105).door != null); }
		Forward(mo, t, 52, 12);
		if (t == 70) Check("inStrongroom", InBox(mo, 1600, -640, 1984, -256));
		if (t == 71) Pose(mo, 1900, -300, 0, 0);
		Forward(mo, t, 71, 6);
		if (t == 80) Check("key1", Has(mo, 1));
		// GREEN in the labs' frame: the cold store, key 2
		if (t == 82) { Take(mo, 3); Pose(mo, 1000, 80, 256, 0); FindFrame(102).Activate(mo); Check("greenHung", !carried && FindFrame(102).door != null); }
		Forward(mo, t, 84, 12);
		if (t == 102) Check("inColdStore", InBox(mo, 1600, 200, 1984, 584));
		if (t == 103) Pose(mo, 1900, 540, 0, 0);
		Forward(mo, t, 103, 6);
		if (t == 112) Check("key2", Has(mo, 2));
		// VIOLET from the stores, up by the stair
		if (t == 114) { Take(mo, 5); Pose(mo, -200, -128, 0, 180); }
		Forward(mo, t, 114, 14);
		if (t == 135) Check("violetUpByTheStair", mo.pos.z == 384 && carried && carried.args[1] == 5);
		if (t == 136) { Pose(mo, -200, 880, 384, 90); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 180) Check("locksOpen", RoomOpen(301));
		if (t == 182) { Pose(mo, -80, 1136, 384, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 184, 70);
	}

	// MAP16's tour: MAP=MAP16 MODE=2 tools/smoke.sh (run it with EXTRA=-nomonsters).
	void WatchYourStepViews()
	{
		static const double v[] = {
			-96, 400, 384, 270, 0,      // the start: the reading room, the well beyond
			-96, 200, 384, 200, 0,      // the head: its leaf, shut, and the player's
			-30, 100, 384, 225, 40,     // from the head down on the foot
			160, 200, 256, 270, 20,     // the second landing, the first below
			200, -160, 128, 180, 25,    // the first landing, the foot below
			-160, -200, 0, 90, -35,     // the foot: up the cliff to the head
			-120, -128, 0, 180, 0,      // the foot's frame
			-160, -300, 0, 250, 0,      // the boiler room
			-760, -528, 0, 200, 0,      // the stores
			-496, -760, 0, 270, 0,      // the cubby: the doorway up
			-300, 600, 384, 90, 0,      // the reading room: the locked door
			400, 96, 256, 0, 0,         // the labs
			96, -400, 128, 290, 0       // the canteen
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP16's company, where it lives: MAP=MAP16 MODE=3 tools/smoke.sh. Doom's
	// monsters are taken out. The leaf hung at the foot and the player beside
	// it: the level's own thief, from the boiler room, has it out of the frame.
	// Then a nailer at the foot, as the ambush brings it: it nails the leaf,
	// and a second thief leaves it alone.
	AjarDoor stairLeaf;
	bool stairWasCut, stairNailed, stairCutAgain;

	void WatchYourStepCompany(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame foot = FindFrame(104);
		if (t == 1)
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster && !(a is "AjarEnemy")) { a.ClearCounters(); a.Destroy(); }
			let ti = ThinkerIterator.Create("AjarThief");
			thief = AjarThief(ti.Next());
		}
		if (t == 20)
		{
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next())) if (d.IsPair() && !d.frame) { stairLeaf = d; d.Used(mo); }
		}
		if (t == 24) { Pose(mo, -200, -128, 0, 180); foot.Activate(mo); Check("stairJoined", stairLeaf.frame == foot && stairLeaf.args[0] == 110); }
		if (t == 26) Pose(mo, -120, -20, 0, 250);
		if (t > 26 && t % 35 == 0 && thief)
			Console.Printf("AJARTEST thief pos=(%d,%d) loot=%s foot=%s nailed=%d", thief.pos.x, thief.pos.y,
				thief.loot ? thief.loot.Label() : "-", foot.door ? foot.door.Label() : "-", stairLeaf.nailer != null);
		if (t > 26 && t < 900 && stairLeaf.frame != foot) stairWasCut = true;
		if (t == 900)
		{
			Check("thiefCutsTheStair", stairWasCut);
			Check("thiefStaysDownHere", thief && thief.pos.z == 0 && thief.pos.x < -64 && thief.pos.y < 64);
			// the leaf back at the foot, and the nailer where the ambush puts it
			if (thief.loot) { DropDoor(thief.loot, thief); thief.loot = null; }
			thief.Destroy();
			if (stairLeaf.frame) Unhang(stairLeaf.frame);
			if (foot.door) { AjarDoor o = Unhang(foot); o.SetOrigin((-680, -300, 0), false); DropDoor(o, o); }
			Hang(stairLeaf, foot);
			nailer = Actor.Spawn("AjarNailer", (-190, 20, 0));
		}
		if (t > 900 && t % 35 == 0)
			Console.Printf("AJARTEST nailed=%d foot=%s", stairLeaf.nailer != null, foot.door ? foot.door.Label() : "-");
		if (t > 900 && !stairNailed && stairLeaf.nailer == nailer)
		{
			stairNailed = true;
			Check("nailerNailsTheLeaf", stairLeaf.frame == foot);
			thief = AjarThief(Actor.Spawn("AjarThief", (-400, -400, 0)));
			thief.args[1] = 1;
		}
		if (t == 1300 && !stairNailed) Check("nailerNailsTheLeaf", false);
		if (stairNailed && stairLeaf.frame != foot) stairCutAgain = true;
		if (t == 1900) Check("nailedLeafIsLeftAlone", stairNailed && !stairCutAgain && stairLeaf.args[0] == 110);
	}
}
