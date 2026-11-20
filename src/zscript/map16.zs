// MAP16 "Watch Your Step" (tools/map_institute6.py), rebuilt 2026-11-20:
// the weighbridge, and the smoke tests.

// The weighbridge: the plate in front of the head, in the lobby. args[0]: the
// tag of the plate's sector; args[1]: the tag of the test hall's shutter;
// args[2]: the tag of the lobby's sectors; args[3]: the tid of the MapSpot
// at the foot where a baron appears; args[4]: the seconds before another.
// When the player first comes into the lobby a baron appears at the foot,
// and whenever that one dies another comes; each is announced (its sight
// sound heard everywhere, and a message). It weighs everything alive that
// stands on the plate, the player and monsters, by their Mass (something
// flying over it weighs nothing): a total of HEAVY or more (a baron, a hell
// knight, a mancubus; never the player alone, who is 100) opens the shutter
// for good. The dial beside it (AjarWeighDial) shows the total.
class AjarWeighbridge : Actor
{
	const HEAVY = 1000;
	Array<int> plate, lobby;
	Actor baron;
	bool called, isOpen, quiet;  // quiet: no more barons (the smoke walkthrough)
	int wait, said, barons, announced;
	int weight;                  // the total on the plate, as of the last look (every 3 tics)
	Actor heaviest;              // the heaviest thing on it then
	Actor openedBy;              // the heaviest thing on it when it opened

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		let it = level.CreateSectorTagIterator(args[0]);
		int i;
		while ((i = it.Next()) >= 0) plate.Push(i);
		it = level.CreateSectorTagIterator(args[2]);
		while ((i = it.Next()) >= 0) lobby.Push(i);
	}

	bool OnPlate(Actor a) { return a && plate.Find(a.CurSector.Index()) < plate.Size(); }
	bool InLobby(Actor a) { return a && (OnPlate(a) || lobby.Find(a.CurSector.Index()) < lobby.Size()); }

	void Say(string msg)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(msg);
	}

	// The total weight of what is alive and stands on the plate.
	void Weigh()
	{
		weight = 0;
		heaviest = null;
		Array<Actor> seen;
		let bi = BlockThingsIterator.CreateFromPos(pos.x, pos.y, pos.z, 128, 128, false);
		while (bi.Next())
		{
			Actor a = bi.thing;
			if (!a || a.health <= 0 || !(a.bIsMonster || a.player) || !OnPlate(a)) continue;
			if (a.pos.z > a.floorz + 4 || seen.Find(a) < seen.Size()) continue;
			seen.Push(a);
			weight += a.Mass;
			if (!heaviest || a.Mass > heaviest.Mass) heaviest = a;
		}
	}

	override void Tick()
	{
		if (level.maptime % 3) return;
		Weigh();
		if (isOpen) return;
		if (weight >= HEAVY) { OpenShutter(heaviest); return; }
		let p = players[consoleplayer].mo;
		if (p && p.health > 0 && OnPlate(p) && level.maptime - said > 175)
		{
			said = level.maptime;
			int tenths = weight * 10 / HEAVY;
			Say("The weighbridge does not stir under you.\nThe dial beside it reads "
				.. (tenths == 1 ? "a tenth" : String.Format("%d tenths", tenths)) .. " of what it was built to weigh.");
		}
		if (!called)
		{
			if (p && InLobby(p)) { called = true; Call(); }
		}
		else if (!quiet && (!baron || baron.health <= 0))
		{
			if (!wait) wait = args[4] * 35;
			else if ((wait -= 3) <= 0) { wait = 0; Call(); }
		}
	}

	void Call()
	{
		let it = level.CreateActorIterator(args[3]);
		Actor spot = it.Next();
		if (!spot || quiet) return;
		Actor b = Spawn("BaronOfHell", spot.pos, ALLOW_REPLACE);
		if (!b) return;
		if (!b.TestMobjLocation()) { b.ClearCounters(); b.Destroy(); return; }
		b.angle = spot.angle;
		Spawn("TeleportFog", spot.pos, ALLOW_REPLACE);
		if (barons++) b.ClearCounters();             // only the first is in the level's tally
		baron = b;
		// heard wherever the player is, and said
		b.A_StartSound(b.SeeSound, CHAN_VOICE, CHANF_DEFAULT, 1, ATTN_NONE);
		Say(barons == 1 ? "Far below, something heavy has come in\nat the foot of the building."
			: "Another, as heavy, has come in\nat the foot of the building.");
		said = level.maptime;                         // (the plate's message waits)
		announced++;
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST baronCalled=%d", barons);
	}

	void OpenShutter(Actor by)
	{
		isOpen = true;
		openedBy = by;
		level.ExecuteSpecial(11 /* Door_Open */, null, null, false, args[1], 16);
		Say("The weighbridge takes the weight. Behind the lobby\nthe test hall's shutter rolls up, for good.");
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST weighbridgeBy=%s weight=%d", by ? by.GetClassName() : 'None', weight);
	}
}

// The dial beside the weighbridge, on the wall (a wall sprite, facing its
// angle): it reads the total weight on the plate in tenths of what the
// weighbridge was built to weigh, to its red mark (10) and one past it (11).
// The needle moves a step every STEP tics toward what it should read; at or
// past the mark the lamp on it is green.
class AjarWeighDial : Actor
{
	const STEP = 4;
	AjarWeighbridge w;
	int needle;

	Default { Radius 8; Height 16; Scale 1.25; +NOGRAVITY +WALLSPRITE +NOBLOCKMAP +DONTTHRUST +NOTELEPORT +BRIGHT }
	States
	{
	Spawn:
		AJWG A -1 Bright;
		Stop;
	Needles:                    // only so that these are loaded
		AJWG ABCDEFGHIJKL -1;
		Stop;
	}

	int Reads() { return w ? clamp(w.weight * 10 / w.HEAVY, 0, 11) : 0; }     // where the needle should be
	bool Green() { return needle >= 10; }

	override void Tick()
	{
		Super.Tick();
		if (!w) w = AjarWeighbridge(ThinkerIterator.Create("AjarWeighbridge").Next());
		if (level.maptime % STEP == 0)
		{
			int to = Reads();
			if (needle < to) needle++;
			else if (needle > to) needle--;
		}
		frame = needle;
	}
}

extend class AjarHandler
{
	bool porterSaid;           // the first porter killed (AjarThief.A_PorterGone)

	bool TagOpen(int tag)
	{
		let it = level.CreateSectorTagIterator(tag);
		int i = it.Next();
		return i >= 0 && level.sectors[i].CenterCeiling() > level.sectors[i].CenterFloor() + 40;
	}

	AjarWeighbridge Weighbridge() { return AjarWeighbridge(ThinkerIterator.Create("AjarWeighbridge").Next()); }

	// the player's leaf: the TEAL one that is not the head
	AjarDoor StairLeaf()
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.IsPair() && d.nailer != d) return d;
		return null;
	}

	// The walkthrough: MAP=MAP16 tools/smoke.sh. Doom's monsters are gone (as
	// in every walkthrough), and so is the porter: what it does is done here
	// by the script with the thief's own calls, and a baron is put on the
	// weighbridge by hand. MODE=3 has them do it themselves. The order is the
	// solver's: a first trip down with empty hands (GREEN, RED, the lever),
	// up by the hole and the cubby to the lobby and its bolt; the leaf down,
	// hung at the foot, up through it, and a baron onto the weighbridge; down
	// again, and the porter has the leaf to the den; up by the cubby, through
	// the head into the den; VIOLET through it to the lobby, the test hall,
	// the brass frame.
	void WatchYourStepScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame head = FindFrame(110), foot = FindFrame(104), den = FindFrame(105);
		AjarDoor leaf = StairLeaf();
		let w = Weighbridge();
		bool violet = carried && carried.args[1] == 5;
		if (t == 10)
		{
			Check("headIsShutAndFixed", head.door && head.door.Shut() && head.door.nailer == head.door);
			Check("allShut", !TagOpen(614) && !TagOpen(615) && !TagOpen(617));
		}
		// the first trip, empty-handed: down to the labs
		if (t == 12) Pose(mo, 256, -1690, 384, 90);
		Forward(mo, t, 12, 40);
		if (t == 60) Check("dropToTheLabs", mo.pos.z == 256 && InBox(mo, 144, -1440, 912, -1136));
		// GREEN in the south wall: out south, in north
		if (t == 62) Take(mo, 3);
		if (t == 63) { Pose(mo, 528, -1410, 256, 270); FindFrame(102).Activate(mo); Check("greenHung", !carried && FindFrame(102).door != null); }
		if (t == 65) Pose(mo, 528, -1420, 256, 270);
		Forward(mo, t, 65, 12);
		if (t == 85) Check("outSouthInNorth", mo.pos.z == 256 && InBox(mo, 144, -1104, 912, -800));
		if (t == 86) Pose(mo, 816, -860, 256, 90);
		Forward(mo, t, 86, 25);
		if (t == 125) Check("dropToTheCanteen", mo.pos.z == 128 && InBox(mo, 144, -704, 912, -208));
		// RED in the canteen's frame: the gallery over it
		if (t == 126) Take(mo, 1);
		if (t == 127) { Pose(mo, 180, -608, 128, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
		if (t == 129) Pose(mo, 170, -608, 128, 180);
		Forward(mo, t, 129, 12);
		if (t == 150) Check("upToTheGallery", mo.pos.z == 256 && InBox(mo, 144, -208, 912, -80));
		if (t == 151) { Pose(mo, 736, -110, 256, 90); FindLine(320).Activate(mo, 0, SPAC_Use); }
		if (t == 152) { Pose(mo, 170, -144, 256, 180); FindLine(321).Activate(mo, 0, SPAC_Use); }
		if (t == 200)
		{
			Check("leverOpensTheWayDown", TagOpen(614));
			Line l = FindLine(321);
			Check("panelOpens", min(l.frontsector.CenterCeiling() - l.frontsector.CenterFloor(),
				l.backsector.CenterCeiling() - l.backsector.CenterFloor()) > 64);
		}
		if (t == 201) Pose(mo, 170, -144, 256, 180);
		Forward(mo, t, 201, 10);
		if (t == 215) Check("secretFound", level.found_secrets > 0);
		// down to the base, and up again by the hole and the cubby
		if (t == 216) Pose(mo, 200, -448, 128, 180);
		Forward(mo, t, 216, 30);
		if (t == 260) Check("dropToTheBase", mo.pos.z == 0 && InBox(mo, -1024, -768, 64, -192));
		if (t == 261) Pose(mo, -990, -496, 0, 180);
		Forward(mo, t, 261, 12);
		if (t == 280) Pose(mo, -1200, -496, 0, 180);
		Forward(mo, t, 280, 10);
		if (t == 300)
		{
			Check("cubbyToTheLobby", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856));
			Check("baronAtTheFoot", w.baron && w.baron.pos.z == 0);
			w.quiet = true;
			if (w.baron) { w.baron.ClearCounters(); w.baron.Destroy(); }
		}
		if (t == 301) { Pose(mo, 800, -2176, 384, 180); FindLine(315).Activate(mo, 0, SPAC_Use); }
		if (t == 350) Check("lobbyDoorOpen", TagOpen(615));
		if (t == 351) Pose(mo, 800, -2176, 384, 180);
		Forward(mo, t, 351, 12);
		if (t == 370) { Check("intoTheReadingRoom", InBox(mo, 0, -2560, 768, -1664)); leaf.Used(mo); Check("tookLeaf", carried == leaf); }
		// the second trip, with the leaf: the drops are open
		if (t == 372) Pose(mo, 256, -1690, 384, 90);
		Forward(mo, t, 372, 40);
		if (t == 421) Pose(mo, 528, -1420, 256, 270);
		Forward(mo, t, 421, 12);
		if (t == 440) Check("throughGreenWithTheLeaf", mo.pos.z == 256 && InBox(mo, 144, -1104, 912, -800) && carried == leaf);
		if (t == 441) Pose(mo, 816, -860, 256, 90);
		Forward(mo, t, 441, 25);
		if (t == 480) Pose(mo, 200, -448, 128, 180);
		Forward(mo, t, 480, 30);
		if (t == 525) Check("leafAtTheBase", mo.pos.z == 0 && carried == leaf);
		// hung at the foot: the way up is down
		if (t == 526) { Pose(mo, -576, -736, 0, 270); foot.Activate(mo); Check("stairJoined", !carried && foot.door == leaf && leaf.args[0] == 110 && head.door.args[0] == 104); }
		if (t == 528) Pose(mo, -576, -740, 0, 270);
		Forward(mo, t, 528, 10);
		if (t == 545) Check("upByTheStair", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856));
		if (t == 546) Pose(mo, 900, -2000, 384, 0);
		if (t == 560) Check("playerAloneDoesNotOpen", !w.isOpen && !TagOpen(617));
		// a baron on the weighbridge (MODE=3 has one follow you there)
		if (t == 561) baron = Actor.Spawn("BaronOfHell", (1100, -2048, 384));
		if (t == 575) { Check("heavyOnThePlateOpens", w.isOpen); if (baron) { baron.ClearCounters(); baron.Destroy(); } }
		if (t == 630) Check("testHallOpen", TagOpen(617));
		// down by the stair; the porter takes the leaf to the den
		if (t == 631) Pose(mo, 1130, -2048, 384, 0);
		Forward(mo, t, 631, 10);
		if (t == 650) Check("downByTheStair", mo.pos.z == 0 && InBox(mo, -1024, -768, -128, -192));
		if (t == 651)
		{
			AjarDoor d = ThiefUsesFrame(foot, null, mo);
			ThiefUsesFrame(den, d, mo);
			Check("headOpensIntoTheDen", den.door == leaf && head.door.args[0] == 105);
		}
		if (t == 653) Pose(mo, -990, -496, 0, 180);
		Forward(mo, t, 653, 12);
		if (t == 670) Pose(mo, -1200, -496, 0, 180);
		Forward(mo, t, 670, 10);
		if (t == 690) Check("upByTheCubbyAgain", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856));
		if (t == 691) Pose(mo, 1130, -2048, 384, 0);
		Forward(mo, t, 691, 10);
		if (t == 710) Check("throughTheHeadIntoTheDen", mo.pos.z == 40 && InBox(mo, -768, -192, -384, 96));
		if (t == 711) { Take(mo, 5); Check("violetTaken", carried && carried.args[1] == 5); }
		if (t == 715) Pose(mo, -576, 40, 40, 90);
		Forward(mo, t, 715, 10);
		if (t == 735) Check("violetUpToTheLobby", violet && InBox(mo, 784, -2240, 1168, -1856));
		if (t == 736) Pose(mo, 976, -1900, 384, 90);
		Forward(mo, t, 736, 20);
		if (t == 765) Check("intoTheTestHall", violet && InBox(mo, 784, -1840, 1232, -1456));
		if (t == 766) { Pose(mo, 1600, -1648, 384, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 768, 70);
	}

	// MAP16's tour: MAP=MAP16 MODE=2 tools/smoke.sh (run it with EXTRA=-nomonsters).
	void WatchYourStepViews()
	{
		static const double v[] = {
			384, -2500, 384, 90, 0,     // the start: the reading room, its stacks
			700, -1950, 384, 0, 0,      // through the glass: the lobby, the head, the weighbridge
			256, -1640, 384, 90, 35,    // the stair head: the drop to the labs
			300, -1400, 256, 60, 0,     // the labs' south half, GREEN
			528, -1300, 256, 90, 0,     // across the trench to the north half, GREEN's far side
			528, -850, 256, 270, 0,     // the north half: the trench, the south wall's frame
			464, -650, 128, 90, -12,    // the canteen: the gallery over it
			464, -150, 256, 270, 20,    // the gallery, down on the canteen
			300, -140, 256, 180, 0,     // the gallery's west wall: the panel
			1000, -500, 128, 0, 0,      // the kitchen
			-576, -600, 0, 270, 0,      // the boiler room: the foot
			-576, -330, 0, 90, 0,       // the den through its bars, the staff stair
			-576, 0, 40, 270, 0,        // in the den
			-1100, -496, 0, 180, 0,     // the cubby: the doorway up
			850, -2048, 384, 0, 0,      // the lobby: the head, the weighbridge
			1080, -2060, 384, 30, 0,    // on the plate: the dial beside the head
			740, -1920, 384, 0, 0,      // through the glass from the reading room: the dial
			660, -1760, 384, 90, -8,    // the glass case: a baron on the plate, the dial at the mark
			1000, -1800, 384, 90, 0,    // the test hall
			1360, -1648, 384, 0, 0      // the night room
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP16's company, where it lives: MAP=MAP16 MODE=3 tools/smoke.sh. Doom's
	// monsters are taken out (the barons the weighbridge calls are not). One
	// One phase after another, each when the last is done:
	//  1 the leaf at the foot, the player in the porter's sight: it carries
	//    the leaf to the den's frame, and stays in the base.
	//  2 RED at the foot, the player in sight: the porter leaves it alone.
	//  3 the leaf at the foot again, the player away upstairs: a nailer nails it.
	//  4 the player in sight again: the porter leaves the nailed leaf alone.
	//  5 the nailer killed: the nails fall out.
	//  6 up through the leaf: the player alone on the plate does not open the
	//    shutter, and the dial comes to rest at a tenth; a baron comes to the
	//    foot, announced. Down again in its sight and up once more: it
	//    follows through the leaf, out of the head onto the weighbridge, and
	//    the shutter opens. The baron is held there while the needle swings
	//    up: at or past the mark, the lamp green.
	// And at the start: the glass case's three figures are there.
	//  7 the porter killed: another comes out of the den 30 seconds later.
	int m16phase, phaseAt, heldAt;
	Vector3 held;
	bool porterAway;

	// The glass case's figures (bad: those solid, shot, counted, alive or not
	// shown), and a baron standing among them: plate, baron, dial.
	int CaseFigures(bool bad)
	{
		int n = 0, baron = 0;
		let it = ThinkerIterator.Create("AjarFigure");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.args[0] == 12 && a.sprite == Actor.GetSpriteIndex("BOSS")) baron++;
			if (a.args[0] == 13 && a.sprite == Actor.GetSpriteIndex("AJWG") && a.frame == 10) baron++;
			if (!bad || a.bSolid || a.bShootable || a.bCountKill || a.bCountItem || a.bIsMonster || !a.bNoBlockmap || a.bInvisible) n++;
		}
		return bad || baron == 2 ? n : -1;
	}
	AjarThief firstPorter;

	// (each phase starts on the tic after the last one ends: the callers return)
	void NextStep(int n, int t) { m16phase = n; phaseAt = t; Console.Printf("AJARTEST phase=%d t=%d", n, t); }

	void WatchYourStepCompany(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame foot = FindFrame(104), den = FindFrame(105), head = FindFrame(110);
		AjarDoor leaf = StairLeaf(), red = DoorOf(1);
		let w = Weighbridge();
		let dial = AjarWeighDial(ThinkerIterator.Create("AjarWeighDial").Next());
		if (t == 3) Check("caseIsThere", CaseFigures(false) == 3 && !CaseFigures(true));
		if (t == 1)
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster && !(a is "AjarEnemy")) { a.ClearCounters(); a.Destroy(); }
			thief = AjarThief(ThinkerIterator.Create("AjarThief").Next());
			firstPorter = thief;
		}
		int s = t - phaseAt;
		if (t > 20 && t % 35 == 0)
			Console.Printf("AJARTEST t=%d phase=%d porter=%s loot=%s foot=%s den=%s nailed=%d baron=%s", t, m16phase,
				thief ? String.Format("(%d,%d,%d)", thief.pos.x, thief.pos.y, thief.pos.z) : "-",
				thief && thief.loot ? thief.loot.Label() : "-", foot.door ? foot.door.Label() : "-",
				den.door ? den.door.Label() : "-", leaf.nailer != null,
				w.baron ? String.Format("(%d,%d,%d)", w.baron.pos.x, w.baron.pos.y, w.baron.pos.z) : "-");
		if (thief && thief.health > 0 && (thief.pos.z > 41 || !InBox(thief, -1024, -768, -128, 96))) porterAway = true;

		if (t == 20)
		{
			leaf.Used(mo);
			Pose(mo, -576, -736, 0, 270);
			foot.Activate(mo);
			Check("stairJoined", foot.door == leaf && head.door.args[0] == 104);
			Pose(mo, -576, -500, 0, 90);
			NextStep(1, t);
			return;
		}
		if (m16phase == 1 && (den.door == leaf || s > 900))
		{
			Check("porterCarriesTheLeafToTheDen", den.door == leaf && head.door.args[0] == 105);
			Check("porterStaysInTheBase", !porterAway);
			// RED, from the canteen, at the foot
			red.Used(mo);
			Pose(mo, -576, -736, 0, 270);
			foot.Activate(mo);
			Pose(mo, -576, -500, 0, 90);
			NextStep(2, t);
			return;
		}
		if (m16phase == 2 && s == 300)
		{
			Check("porterLeavesOtherDoors", foot.door == red && thief && !thief.loot);
			Unhang(foot);                                   // RED back to the canteen
			red.carried = false;
			red.SetOrigin((820, -650, 128), false);
			red.Show();
			if (carried == leaf) { Pose(mo, -576, -736, 0, 270); foot.Activate(mo); }   // phase 1 failed
			else Hang(Unhang(den), foot);                   // the leaf from the den to the foot again
			Pose(mo, 384, -2400, 384, 90);                  // upstairs, out of its sight
			nailer = Actor.Spawn("AjarNailer", (-640, -700, 0));
			NextStep(3, t);
			return;
		}
		if (m16phase == 3 && (leaf.nailer || s > 700))
		{
			Check("nailerNailsTheLeafAtTheFoot", leaf.nailer == nailer && foot.door == leaf);
			Pose(mo, -576, -500, 0, 90);
			NextStep(4, t);
			return;
		}
		if (m16phase == 4 && s == 300)
		{
			Check("porterLeavesTheNailedLeaf", foot.door == leaf && leaf.nailer && thief && !thief.loot);
			nailer.DamageMobj(null, null, 1000, 'None');
			NextStep(5, t);
			return;
		}
		if (m16phase == 5 && s == 30)
		{
			Check("nailsFallWhenTheNailerDies", nailer.health <= 0 && !leaf.nailer && foot.door == leaf);
			Pose(mo, -576, -740, 0, 270);
			NextStep(6, t);
			return;
		}
		if (m16phase == 6)
		{
			Forward(mo, t, phaseAt, 10);                    // up through the leaf, alone
			if (s == 12) Pose(mo, 1100, -2048, 384, 180);   // standing still on the plate
			if (s == 30)
			{
				Check("playerAloneDoesNotOpen", mo.pos.z == 384 && !w.isOpen && !TagOpen(617));
				Check("dialReadsATenth", w.OnPlate(mo) && w.weight == 100 && dial && dial.needle == 1 && !dial.Green());
			}
			if (s == 40)
			{
				Check("aBaronComesToTheFoot", w.baron && w.baron.pos.z == 0);
				Check("theBaronIsAnnounced", w.barons == 1 && w.announced == 1);
				Check("dialRestsAtATenth", dial && dial.needle == 1 && !w.isOpen && !TagOpen(617));
			}
			if (s == 41) Pose(mo, 1130, -2048, 384, 0);     // down again, into its sight
			Forward(mo, t, phaseAt + 41, 10);
			if (s == 100) Pose(mo, -576, -740, 0, 270);     // and up once more, with it behind
			Forward(mo, t, phaseAt + 100, 30);
			if (!heldAt && (w.isOpen || s > 900))
			{
				Check("baronFollowsOntoTheWeighbridge", w.isOpen && w.openedBy is "BaronOfHell");
				heldAt = t;
				if (w.isOpen && w.baron) held = w.baron.pos;
			}
			// the baron held where it opened it, on the plate, while the needle swings up
			if (heldAt && w.baron && w.baron.health > 0 && held != (0, 0, 0)) { w.baron.SetOrigin(held, false); w.baron.vel = (0, 0, 0); }
			if (heldAt && t == heldAt + 70)
			{
				Check("dialAtTheMark", w.isOpen && w.weight >= w.HEAVY && dial && dial.needle >= 10 && dial.Green()
					&& TagOpen(617));
				Console.Printf("AJARTEST weight=%d needle=%d", w.weight, dial ? dial.needle : -1);
				thief.DamageMobj(null, null, 1000, 'None');
				NextStep(7, t);
				return;
			}
		}
		if (m16phase == 7 && s == 20) Check("porterKilled", firstPorter.health <= 0);
		if (m16phase == 7 && s == 1150)
		{
			AjarThief next = null;
			let ti = ThinkerIterator.Create("AjarThief");
			AjarThief th;
			while (th = AjarThief(ti.Next())) if (th != firstPorter && th.health > 0) next = th;
			if (next) Console.Printf("AJARTEST nextPorter=(%d,%d,%d)", next.pos.x, next.pos.y, next.pos.z);
			Check("anotherPorterComes", next != null && next.args[2] == 105 && InBox(next, -768, -112, -384, 96));
			if (next) thief = next;
			NextStep(8, t);
			return;
		}
	}
}
