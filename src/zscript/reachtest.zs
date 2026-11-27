// MAP=LAB MODE=4 tools/smoke.sh: the reach survey (reach.zs; PLAN.md, "Hands do not reach through an opening
// (built 2026-11-27)"). Real presses of USE (cmd.buttons = BT_USE, the engine's own CheckUse, then let go) over a
// grid of places and aims at eight arrangements of the lab's doors, each press logged ("AJARREACH ..."): what it
// did to the doors, if anything, and whether that was direct (a door or frame of the player's own room) or through
// an opening (one beyond it). After a press that did something the arrangement is set up again. Every press is
// made twice, first with the rule off (reachOff: the game as it was until 2026-11-27), then with it on, and the
// two are compared press for press. The arrangements (the lab's frames, and 118 and 119 in its sealed annex):
//   1 redFromItsFrame      RED hung in 112, empty hands, from the hall before 112: direct
//   2 redFromItsFarSide    the same from the gallery at RED's far side (its mouth y 704, the portal at 720):
//                          RED reached through its own opening
//   3 tealFromItsFrame     TEAL's leaves in 114 (the hall) and 116 (the gallery), from before 114: the leaf of
//                          114 direct, its twin in 116 through the Pair
//   4 tealFromTheGallery   the same from before 116: 116 direct, 114 through
//   5 leaningInTheHall     an ORANGE leaf leaning in the middle of the hall, from all round it: direct
//   6 leaningBeyond        RED in 112 and an ORANGE leaf leaning in the gallery just before RED's far side, from
//                          the hall before 112 and in its recess: RED direct, the leaf through
//   7 emptyFrame           RED in hand, 113 empty, from before it: direct
//   8 emptyFrameBeyond     RED in hand, TEAL in 114 and in 118 (the annex), 119 empty 32 across from 118, from
//                          before 114: 114 direct (a swap), 118 and 119 through
// Then a script's call of Used and Activate (no key down) through an opening: answered as before.
extend class AjarHandler
{
	const RS_PHASES = 8;
	const RS_PER_TIC = 40;
	static const string RS_NAMES[] = { "", "redFromItsFrame", "redFromItsFarSide", "tealFromItsFrame", "tealFromTheGallery",
		"leaningInTheHall", "leaningBeyond", "emptyFrame", "emptyFrameBeyond" };
	// what is in the player's own room: an act on anything else is through an opening
	static const string RS_OWN[] = { "", " F112 ", " F116 ", " F111 F112 F113 F114 F115 F117 ", " F116 ",
		" L-O1 F111 F112 F113 F114 F115 F117 ", " F111 F112 F113 F114 F115 F117 ", " F111 F112 F113 F114 F115 F117 ",
		" F111 F112 F113 F114 F115 F117 " };
	static const string RS_DOOR[] = { "RED", "T1", "T2", "O1", "O2" };
	Array<double> rsX, rsY, rsA;
	Array<int> rsP;
	Array<string> rsBefore;        // what each press did with the rule off ("" nothing; "T " in front: through)
	Array<AjarDoor> rsDoors;       // RED, TEAL's two leaves, ORANGE's two
	Array<int> rsN, rsDB, rsDA, rsTB, rsTA, rsChanged;
	int rsI, rsPass, rsArranged;
	bool rsSaid;
	int rsKnown;                   // the far-side places like MAP18's three that acted before (a bit each of y 716, 704, 688)

	double RsFloor(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }

	void RsPose(Actor mo, double x, double y, double ang)
	{
		mo.SetOrigin((x, y, RsFloor((x, y))), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
	}

	void RsPress(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
		pp.CheckUse();
	}

	// where door k is in arrangement p: a frame's id, -1 in hand, 1 leaning at the arrangement's place, 0 put
	// aside (leaning by the hall's north wall, out of every grid's reach)
	int RsWhere(int p, int k)
	{
		switch (p)
		{
		case 1: case 2: return k == 0 ? 112 : 0;
		case 3: case 4: return k == 1 ? 114 : k == 2 ? 116 : 0;
		case 5: return k == 3 ? 1 : 0;
		case 6: return k == 0 ? 112 : k == 4 ? 1 : 0;
		case 7: return k == 0 ? -1 : 0;
		case 8: return k == 0 ? -1 : k == 1 ? 114 : k == 2 ? 118 : 0;
		}
		return 0;
	}

	void RsArrange(int p)
	{
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next())) if (f.door) Unhang(f);
		carried = null;
		for (int k = 0; k < rsDoors.Size(); k++)
		{
			AjarDoor d = rsDoors[k];
			int w = RsWhere(p, k);
			if (w >= 100) { Hang(d, FindFrame(w)); continue; }
			if (w < 0) { d.carried = true; d.Hide(); carried = d; continue; }
			Vector3 s = (40 + 60 * k, 470, 270);
			if (w == 1 && p == 5) s = (384, 300, 270);
			else if (w == 1) s = (512, 688, 270);
			d.carried = false;
			d.SetOrigin((s.x, s.y, RsFloor(s.xy)), false);
			d.angle = s.z;
			d.Show();
		}
	}

	string RsState(AjarDoor d)
	{
		if (d.frame) return String.Format("f%d", d.frame.args[0]);
		if (carried == d) return "h";
		if (d.carried) return "c";
		return String.Format("l%.0f,%.0f", d.pos.x, d.pos.y);
	}

	// the places and aims of arrangement p: every x of xs with every y of ys, facing base + each of offs
	// (base 999: facing (384, 300), the leaning door of 5); places outside the map left out
	void RsGrid(int p, string xs, string ys, double base, string offs)
	{
		Array<string> ax, ay, ao;
		xs.Split(ax, " ");
		ys.Split(ay, " ");
		offs.Split(ao, " ");
		for (int i = 0; i < ax.Size(); i++)
			for (int j = 0; j < ay.Size(); j++)
			{
				double x = ax[i].ToDouble(), y = ay[j].ToDouble();
				if (!level.IsPointInLevel((x, y, RsFloor((x, y)) + 8))) continue;
				for (int k = 0; k < ao.Size(); k++)
				{
					double a = base == 999 ? VectorAngle(384 - x, 300 - y) : base;
					rsP.Push(p);
					rsX.Push(x);
					rsY.Push(y);
					rsA.Push(Actor.Normalize180(a + ao[k].ToDouble()));
				}
			}
	}

	void RsSetUp()
	{
		rsDoors.Clear();
		rsDoors.Push(DoorOf(1));
		rsDoors.Push(LabLeaf(8, 0));
		rsDoors.Push(LabLeaf(8, 1));
		rsDoors.Push(LabLeaf(9, 0));
		rsDoors.Push(LabLeaf(9, 1));
		string wide = "-60 -45 -30 -20 -15 -10 0 10 15 20 30 45 60";
		RsGrid(1, "704 716 728 740 752 762 770 778", "72 84 96 104 112 120 128 136 144 152 160 172 184", 0, wide);
		RsGrid(2, "472 480 488 496 504 512 520 528 536 544 552", "716 712 704 696 688 680 672 660 648", 90, wide);
		RsGrid(3, "148 160 168 176 184 192 200 208 216 224 236", "-12 -6 0 8 16 24 36 48 64", 270, wide);
		RsGrid(4, "84 96 104 112 120 128 136 144 152 160 172", "716 712 704 696 688 680 672 660 648", 90, wide);
		RsGrid(5, "320 336 352 364 376 384 392 404 416 432 448", "236 252 268 280 292 300 308 320 332 348 364", 999, "-40 -20 -10 0 10 20 40");
		RsGrid(6, "752 760 766 772 778 782", "96 104 112 120 128 136 144 152 160", 0, "-45 -30 -20 -10 0 10 20 30 45");
		RsGrid(7, "592 600 608 616 624 632 640 648 656 664 672 680 688", "-12 -6 0 8 16 24 36 48 60", 270, "-60 -45 -30 -20 -10 0 10 20 30 45 60");
		RsGrid(8, "148 160 168 176 184 192 200 208 216 224 236", "-12 -6 0 8 16 24 36 48 64", 270, wide);
		for (int p = 0; p <= RS_PHASES; p++) { rsN.Push(0); rsDB.Push(0); rsDA.Push(0); rsTB.Push(0); rsTA.Push(0); rsChanged.Push(0); }
		Console.Printf("AJARTEST info reach survey: %d presses a pass", rsP.Size());
	}

	// one press: what it did ("" nothing; "T " in front when through an opening)
	string RsOne(Actor mo, int i)
	{
		int p = rsP[i];
		if (rsArranged != p) { RsArrange(p); rsArranged = p; }
		RsPose(mo, rsX[i], rsY[i], rsA[i]);
		Array<string> st;
		for (int k = 0; k < rsDoors.Size(); k++) st.Push(RsState(rsDoors[k]));
		RsPress(mo);
		string act = "";
		bool through = false;
		for (int k = 0; k < rsDoors.Size(); k++)
		{
			string now = RsState(rsDoors[k]);
			if (now == st[k]) continue;
			act = act .. (act != "" ? ", " : "") .. RS_DOOR[k] .. " " .. st[k] .. ">" .. now;
			for (int e = 0; e < 2; e++)
			{
				string s = e ? now : st[k];
				string obj = s.Left(1) == "f" ? "F" .. s.Mid(1) : s.Left(1) == "l" ? "L-" .. RS_DOOR[k] : "";
				if (obj != "" && RS_OWN[p].IndexOf(" " .. obj .. " ") < 0) through = true;
			}
		}
		if (act != "") { RsArrange(p); rsArranged = p; }
		return act == "" ? "" : (through ? "T " : "D ") .. act;
	}

	void LabReachScript(Actor mo, int t)
	{
		if (t == 10) { RsSetUp(); rsPass = 0; rsI = 0; reachOff = true; rsArranged = 0; }
		if (t < 12 || rsPass > 1) return;
		for (int n = 0; n < RS_PER_TIC; n++)
		{
			if (rsI >= rsP.Size())
			{
				if (rsPass == 0) { rsPass = 1; rsI = 0; reachOff = false; rsArranged = 0; continue; }
				rsPass = 2;
				RsReport(mo);
				return;
			}
			int i = rsI++, p = rsP[i];
			string act = RsOne(mo, i);
			Console.Printf("AJARREACH %s P%d #%d (%.0f,%.0f) %.0f: %s", rsPass ? "after" : "before", p, i, rsX[i], rsY[i], rsA[i], act == "" ? "-" : act);
			if (rsPass == 0)
			{
				rsBefore.Push(act);
				rsN[p]++;
				if (act.Left(1) == "D") rsDB[p]++;
				if (act.Left(1) == "T") rsTB[p]++;
				// MAP18's three: at a jamb (16 in from it), 4 from the portal, at the mouth, 16 into the room, aimed 15 off
				if (p == 2 && act.Left(1) == "T" && (rsX[i] == 496 || rsX[i] == 528) && abs(abs(rsA[i] - 90) - 15) < 0.1)
					rsKnown |= rsY[i] == 716 ? 1 : rsY[i] == 704 ? 2 : rsY[i] == 688 ? 4 : 0;
				continue;
			}
			string was = rsBefore[i];
			if (act.Left(1) == "D") rsDA[p]++;
			if (act.Left(1) == "T") rsTA[p]++;
			if (was.Left(1) == "D" ? act != was : act != "") rsChanged[p]++;
			if (was.Left(1) == "T" && act == "" && said == "Your hands do not reach through a doorway.\nStep through first.") rsSaid = true;
		}
	}

	void RsReport(Actor mo)
	{
		int changed = 0, ownBefore = 1;
		for (int p = 1; p <= RS_PHASES; p++)
		{
			Console.Printf("AJARTEST info reach %d %s: %d presses; direct acted before %d, after %d; through acted before %d, after %d; changed %d",
				p, RS_NAMES[p], rsN[p], rsDB[p], rsDA[p], rsTB[p], rsTA[p], rsChanged[p]);
			changed += rsChanged[p];
			if ((p == 1 || p == 3 || p == 4 || p == 5 || p == 6 || p == 7 || p == 8) && !rsDB[p]) ownBefore = 0;
		}
		Console.Printf("AJARTEST info reach: the far-side places like MAP18's that acted before: %d of 3", (rsKnown & 1) + ((rsKnown >> 1) & 1) + ((rsKnown >> 2) & 1));
		Check("theHoleWasThereBefore", rsTB[2] > 0 && rsTB[3] + rsTB[4] > 0 && rsTB[6] > 0 && rsTB[8] > 0 && rsKnown == 7);
		Check("theDoorIsNotTakenFromItsFarSide", rsTA[2] == 0);
		Check("theTwinIsNotTakenThroughThePair", rsTA[3] + rsTA[4] == 0);
		Check("aLeaningDoorIsNotTakenThroughADoorway", rsTA[6] == 0);
		Check("noDoorIsHungThroughADoorway", rsTA[8] == 0);
		Check("fromItsOwnSideEverythingWorks", changed == 0 && ownBefore);
		Check("theHandsSaySo", rsSaid);
		// a script's call (no key down) through an opening is answered as before: RED taken from its far side,
		// RED hung in 119 from the hall through 114 and 118
		RsArrange(2);
		RsPose(mo, 512, 704, 90);
		rsDoors[0].Used(mo);
		bool taken = carried == rsDoors[0] && !rsDoors[0].frame;
		RsArrange(8);
		RsPose(mo, 192, -8, 270);
		FindFrame(119).Activate(mo);
		Check("scriptsAreAnsweredAsBefore", taken && FindFrame(119).door == rsDoors[0] && !carried);
	}
}
