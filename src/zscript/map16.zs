// MAP16 "Watch Your Step" (tools/map_institute6.py), rebuilt 2026-11-20:
// the weighbridge, and the smoke tests.

// The weighbridge: the plate in front of the head, in the lobby. args[0]: the
// tag of the plate's sector; args[1]: the tag of the test hall's shutter;
// args[2]: the tag of the lobby's sectors; args[3]: the tid of the MapSpot
// on the canteen's gallery where its baron stands; args[4]: the seconds
// before another.
//
// It weighs everything that stands or lies on the plate (by where its middle
// is): the player (100) and live monsters by their Mass (something flying
// more than 4 over it weighs nothing), and the bodies of dead monsters by
// theirs. The shutter follows the total: while it is HEAVY or more the
// shutter goes up, and when it falls below it comes down again, moved here
// tic by tic (Sector.MoveCeiling, no mover left behind) at a door's speed.
// Coming down it never crushes: while anything stands (or lies) in the
// doorway it waits. A body of HEAVY or more on the plate (a dead baron)
// settles it: the shutter stays up for good, and no more barons come. The
// dial beside it (AjarWeighDial) shows the total.
//
// Its baron stands on the canteen's gallery from the start (on every skill,
// unannounced); 20 seconds after each one dies another comes there, its
// sight sound heard everywhere and a message, until it is settled. Its barons
// are dogged (AjarSense.dogged): seeing the player on the canteen floor
// below does not make them give up a door they are making for, so one
// follows the player down through RED, and through whatever hangs in a frame
// after.
class AjarWeighbridge : Actor
{
	const HEAVY = 1000;
	const SPEED = 2;             // the shutter's way a tic (Door_Open at speed 16)
	const AGAIN = 350;           // its "up" and "down" words, no more often than this
	Array<int> plate, lobby, shutter;
	Array<double> bottom, top;
	double dx1, dy1, dx2, dy2;   // the shutter's doorway
	Actor baron;
	bool called, quiet;          // quiet: no more barons (the smoke walkthrough)
	bool up;                     // the shutter wants to be up (the total at the mark, or settled)
	bool settled;                // a body of HEAVY or more lies on it: up for good
	bool baronDown;              // its last baron is dead (or gone): another is due
	int wait, said, barons, announced, upSaid, downSaid, lostSaid, ups, downs;
	int weight;                  // the total on the plate, as of the last look (every 3 tics)
	int deadWeight;              // ...of which the dead
	Actor heaviest;              // the heaviest thing on it then
	Actor openedBy;              // the heaviest thing on it when the shutter first went up

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
		it = level.CreateSectorTagIterator(args[1]);
		dx1 = dy1 = 1e9;
		dx2 = dy2 = -1e9;
		while ((i = it.Next()) >= 0)
		{
			Sector s = level.sectors[i];
			shutter.Push(i);
			bottom.Push(s.CenterFloor());
			double low;
			Vertex v;
			[low, v] = s.FindLowestCeilingSurrounding();
			top.Push(low - 4);
			for (int k = 0; k < s.lines.Size(); k++)
			{
				Line l = s.lines[k];
				dx1 = min(dx1, min(l.v1.p.x, l.v2.p.x)); dx2 = max(dx2, max(l.v1.p.x, l.v2.p.x));
				dy1 = min(dy1, min(l.v1.p.y, l.v2.p.y)); dy2 = max(dy2, max(l.v1.p.y, l.v2.p.y));
			}
		}
	}

	bool OnPlate(Actor a) { return a && plate.Find(a.CurSector.Index()) < plate.Size(); }
	bool InLobby(Actor a) { return a && (OnPlate(a) || lobby.Find(a.CurSector.Index()) < lobby.Size()); }
	bool Dead(Actor a) { return a && !a.player && a.health <= 0 && (a.bIsMonster || a.bCorpse); }
	bool IsUp() { return shutter.Size() && level.sectors[shutter[0]].CenterCeiling() >= top[0]; }
	bool IsDown() { return shutter.Size() && level.sectors[shutter[0]].CenterCeiling() <= bottom[0]; }

	void Say(string msg)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(msg);
	}

	// The total weight of what stands or lies on the plate.
	void Weigh()
	{
		weight = deadWeight = 0;
		heaviest = null;
		Array<Actor> seen;
		let bi = BlockThingsIterator.CreateFromPos(pos.x, pos.y, pos.z, 128, 128, false);
		while (bi.Next())
		{
			Actor a = bi.thing;
			if (!a || !OnPlate(a) || seen.Find(a) < seen.Size()) continue;
			bool dead = Dead(a);
			if (!dead && (a.health <= 0 || !(a.bIsMonster || a.player))) continue;
			if (a.pos.z > a.floorz + 4) continue;
			seen.Push(a);
			weight += a.Mass;
			if (dead) deadWeight += a.Mass;
			if (!heaviest || a.Mass > heaviest.Mass) heaviest = a;
		}
	}

	// Anything standing or lying in the shutter's doorway?
	bool InDoorway()
	{
		let bi = BlockThingsIterator.CreateFromPos((dx1 + dx2) / 2, (dy1 + dy2) / 2, bottom.Size() ? bottom[0] : 0,
			128, max(dx2 - dx1, dy2 - dy1), false);
		while (bi.Next())
		{
			Actor a = bi.thing;
			if (!a || !(a.player || a.bIsMonster || a.bSolid || a.bCorpse)) continue;
			double r = a.radius;
			if (a.pos.x + r <= dx1 || a.pos.x - r >= dx2 || a.pos.y + r <= dy1 || a.pos.y - r >= dy2) continue;
			return true;
		}
		return false;
	}

	// One tic of the shutter's way, up or down. Down, it waits while the doorway is not clear.
	void MoveShutter()
	{
		if (!up && InDoorway()) return;
		for (int i = 0; i < shutter.Size(); i++)
		{
			Sector s = level.sectors[shutter[i]];
			double now = s.CenterCeiling(), to = up ? top[i] : bottom[i];
			if (now == to) continue;
			s.MoveCeiling(min(SPEED, abs(to - now)), to, -1, to > now ? 1 : -1, false);
		}
	}

	void ShutterSound(bool rising)
	{
		if (!shutter.Size()) return;
		Sector s = level.sectors[shutter[0]];
		s.StartSoundSequence(2 /* the ceiling's channel */, rising ? "DoorOpenNormal" : "DoorCloseNormal", 0);
	}

	override void Tick()
	{
		MoveShutter();
		if (level.maptime % 3) return;
		if (!called) { called = true; Call(); }      // the first baron: there from the start, not announced
		Weigh();
		bool test = CVar.GetCVar("ajar_autotest").GetInt() != 0;
		if (!settled && deadWeight >= HEAVY)
		{
			settled = true;
			quiet = true;
			if (!up) { up = true; ShutterSound(true); }
			if (!openedBy) openedBy = heaviest;
			Say("Dead weight. The weighbridge holds it,\nand the test hall's shutter stays up.");
			said = level.maptime;
			if (test) Console.Printf("AJARTEST weighbridgeSettled weight=%d dead=%d", weight, deadWeight);
		}
		if (!settled)
		{
			bool w = weight >= HEAVY;
			if (w != up)
			{
				up = w;
				ShutterSound(w);
				if (w)
				{
					ups++;
					if (!openedBy) openedBy = heaviest;
					if (!upSaid || level.maptime - upSaid >= AGAIN)
					{
						upSaid = said = level.maptime;
						Say("The weighbridge takes the weight, and the test hall's\nshutter rolls up.");
					}
					if (test) Console.Printf("AJARTEST weighbridgeBy=%s weight=%d dead=%d", heaviest ? heaviest.GetClassName() : 'None', weight, deadWeight);
				}
				else
				{
					downs++;
					if (!downSaid || level.maptime - downSaid >= AGAIN)
					{
						downSaid = said = level.maptime;
						Say("The weight is off the weighbridge.\nThe shutter comes down again.");
					}
					if (test) Console.Printf("AJARTEST weighbridgeDown weight=%d", weight);
				}
			}
		}
		let p = players[consoleplayer].mo;
		if (!up && p && p.health > 0 && OnPlate(p) && level.maptime - said > 175)
		{
			said = level.maptime;
			int tenths = weight * 10 / HEAVY;
			Say("The weighbridge does not stir under you.\nThe dial beside it reads "
				.. (tenths == 1 ? "a tenth" : String.Format("%d tenths", tenths)) .. " of what it was built to weigh.");
		}

		// its baron: dogged while it lives; dead, another after a while
		if (baron && baron.health > 0)
		{
			let sense = AjarSense(baron.FindInventory("AjarSense"));
			if (sense) sense.dogged = true;
		}
		else if (!baronDown)
		{
			baronDown = true;
			if (baron && !OnPlate(baron) && !settled && lostSaid < 2)
			{
				lostSaid++;
				said = level.maptime;
				Say("It lies where nothing weighs it.");
			}
			wait = args[4] * 35;
			if (test) Console.Printf("AJARTEST baronDied onPlate=%d", baron && OnPlate(baron));
		}
		else if (!quiet && !settled && (wait -= 3) <= 0) Call();
	}

	// A baron onto the gallery. Its spot taken: tried again on the next look.
	void Call()
	{
		let it = level.CreateActorIterator(args[3]);
		Actor spot = it.Next();
		if (!spot || quiet || settled) return;
		Actor b = Spawn("BaronOfHell", spot.pos, ALLOW_REPLACE);
		if (!b) return;
		if (!b.TestMobjLocation()) { b.ClearCounters(); b.Destroy(); return; }
		b.angle = spot.angle;
		if (barons++) b.ClearCounters();             // only the first is in the level's tally
		baron = b;
		baronDown = false;
		let sense = AjarSense(b.FindInventory("AjarSense"));
		if (sense) sense.dogged = true;
		if (barons > 1)
		{
			// heard wherever the player is, and said
			Spawn("TeleportFog", spot.pos, ALLOW_REPLACE);
			b.A_StartSound(b.SeeSound, CHAN_VOICE, CHANF_DEFAULT, 1, ATTN_NONE);
			Say("Another, as heavy, has come onto the gallery\nover the canteen.");
			said = level.maptime;                     // (the plate's message waits)
			announced++;
		}
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST baronCalled=%d", barons);
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
	// by the script with the thief's own calls. The weighbridge's baron, which
	// it puts on the gallery, is taken away, and a baron is put on the
	// weighbridge by hand; MODE=3 has the real one walk there. The order is
	// the solver's (its detour on the first trip, the baron down through RED
	// and killed, left out: there is no baron here): a first trip down with
	// empty hands (GREEN, RED, the lever, the panel), up by the hole and the
	// cubby to the lobby and its bolt; the leaf down to the canteen, up
	// through RED to the gallery and down through it again, RED swapped out
	// of the canteen's frame for the leaf, through the leaf to the lobby: a
	// baron on the plate raises the shutter, off it the shutter comes down,
	// dead on it the shutter stays up. Back through the leaf, RED swapped in
	// again, the leaf down to the foot; the porter has it to the den; up by
	// the cubby, through the head into the den; VIOLET through it to the
	// lobby, the test hall, the brass frame.
	Actor handBaron;
	Vector3 handAt;
	void WatchYourStepScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame head = FindFrame(110), foot = FindFrame(104), den = FindFrame(105), canteen = FindFrame(101);
		AjarDoor leaf = StairLeaf(), red = DoorOf(1);
		let w = Weighbridge();
		bool violet = carried && carried.args[1] == 5;
		if (t == 10)
		{
			Check("headIsShutAndFixed", head.door && head.door.Shut() && head.door.nailer == head.door);
			Check("allShut", !TagOpen(614) && !TagOpen(615) && !TagOpen(617));
			Check("baronOnTheGallery", w.baron && w.baron.health > 0 && w.baron.pos.z == 256 && InBox(w.baron, 144, -208, 912, -80));
			w.quiet = true;
			if (w.baron) { w.baron.ClearCounters(); w.baron.Destroy(); }
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
		if (t == 127) { Pose(mo, 180, -608, 128, 180); canteen.Activate(mo); Check("redHung", !carried && canteen.door != null); }
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
		if (t == 300) Check("cubbyToTheLobby", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856));
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
		// up through RED with the leaf, and down through it again (where the baron would follow)
		if (t == 480) { Check("leafInTheCanteen", mo.pos.z == 128 && InBox(mo, 144, -704, 912, -208) && carried == leaf); Pose(mo, 170, -608, 128, 180); }
		Forward(mo, t, 480, 12);
		if (t == 510) Check("upThroughRedWithTheLeaf", mo.pos.z == 256 && InBox(mo, 144, -208, 912, -80) && carried == leaf);
		if (t == 511) Pose(mo, 528, -110, 256, 90);
		Forward(mo, t, 511, 12);
		if (t == 540) Check("downThroughRedAgain", mo.pos.z == 128 && InBox(mo, 144, -704, 912, -208));
		// RED out of the canteen's frame, the leaf in: the canteen opens onto the lobby
		if (t == 541)
		{
			Pose(mo, 180, -608, 128, 180);
			canteen.Activate(mo);
			Check("redSwappedForTheLeaf", carried == red && canteen.door == leaf && head.door.args[0] == 101);
		}
		if (t == 543) Pose(mo, 170, -608, 128, 180);
		Forward(mo, t, 543, 12);
		if (t == 570) { Check("throughTheLeafToTheLobby", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856) && carried == red); Pose(mo, 900, -2000, 384, 0); }
		// the weighbridge: a baron on it by hand, held where the script puts it
		if (t == 580)
		{
			Check("playerAloneDoesNotOpen", !w.up && !TagOpen(617));
			handAt = (1104, -2048, 384);
			handBaron = Actor.Spawn("BaronOfHell", handAt);
		}
		if (handBaron && handBaron.health > 0) { handBaron.SetOrigin(handAt, false); handBaron.vel = (0, 0, 0); }
		if (t == 590) Check("liveBaronRaisesTheShutter", w.up && w.weight >= w.HEAVY && w.deadWeight == 0);
		if (t == 640) Check("shutterGoingUp", TagOpen(617));
		if (t == 720) { Check("shutterUp", w.IsUp()); handAt = (860, -2190, 384); }
		if (t == 730) Check("offThePlateItComesDown", !w.up && w.weight < w.HEAVY);
		if (t == 870) { Check("shutterDownAgain", w.IsDown() && !TagOpen(617)); handAt = (1104, -2048, 384); }
		if (t == 880 && handBaron) handBaron.DamageMobj(null, null, 10000, 'None');
		if (t == 920) Check("deadBaronSettles", w.settled && w.deadWeight >= w.HEAVY && w.up);
		if (t == 1060) Check("deadBaronHoldsTheShutterUp", w.IsUp() && TagOpen(617) && w.barons == 1);
		// back through the leaf, RED in again, the leaf down to the foot
		if (t == 1061) Pose(mo, 1130, -2048, 384, 0);
		Forward(mo, t, 1061, 10);
		if (t == 1080) Check("backToTheCanteen", mo.pos.z == 128 && InBox(mo, 144, -704, 912, -208) && carried == red);
		if (t == 1081)
		{
			Pose(mo, 180, -608, 128, 180);
			canteen.Activate(mo);
			Check("leafSwappedForRed", carried == leaf && canteen.door == red);
		}
		if (t == 1083) Pose(mo, 200, -448, 128, 180);
		Forward(mo, t, 1083, 30);
		if (t == 1130) Check("leafAtTheBase", mo.pos.z == 0 && carried == leaf);
		if (t == 1131) { Pose(mo, -576, -736, 0, 270); foot.Activate(mo); Check("stairJoined", !carried && foot.door == leaf && leaf.args[0] == 110 && head.door.args[0] == 104); }
		// the porter takes the leaf to the den
		if (t == 1133)
		{
			AjarDoor d = ThiefUsesFrame(foot, null, mo);
			ThiefUsesFrame(den, d, mo);
			Check("headOpensIntoTheDen", den.door == leaf && head.door.args[0] == 105);
		}
		if (t == 1135) Pose(mo, -990, -496, 0, 180);
		Forward(mo, t, 1135, 12);
		if (t == 1155) Pose(mo, -1200, -496, 0, 180);
		Forward(mo, t, 1155, 10);
		if (t == 1175) Check("upByTheCubbyAgain", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856));
		if (t == 1176) Pose(mo, 1130, -2048, 384, 0);
		Forward(mo, t, 1176, 10);
		if (t == 1195) Check("throughTheHeadIntoTheDen", mo.pos.z == 40 && InBox(mo, -768, -192, -384, 96));
		if (t == 1196) { Take(mo, 5); Check("violetTaken", carried && carried.args[1] == 5); }
		if (t == 1200) Pose(mo, -576, 40, 40, 90);
		Forward(mo, t, 1200, 10);
		if (t == 1220) Check("violetUpToTheLobby", violet && InBox(mo, 784, -2240, 1168, -1856));
		if (t == 1221) Pose(mo, 976, -1900, 384, 90);
		Forward(mo, t, 1221, 20);
		if (t == 1250) Check("intoTheTestHall", violet && InBox(mo, 784, -1840, 1232, -1456));
		if (t == 1251) { Pose(mo, 1600, -1648, 384, 0); FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		Forward(mo, t, 1253, 70);
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
			620, -520, 128, 60, -22,    // the gallery from the canteen floor: the baron at its east end
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
			660, -1760, 384, 90, -8,    // the glass case: a baron lying dead on the plate, the dial at the mark
			1000, -1800, 384, 90, 0,    // the test hall
			1360, -1648, 384, 0, 0      // the night room
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP16's company, where it lives: MAP=MAP16 MODE=3 tools/smoke.sh. Doom's
	// monsters are taken out (the weighbridge's barons are not). One phase
	// after another, each when the last is done:
	//  1 the leaf at the foot, the player in the porter's sight: it carries
	//    the leaf to the den's frame, and stays in the base.
	//  2 GREEN at the foot, the player in sight: the porter leaves it alone.
	//    (Not RED: RED's far side is on the gallery, and the baron would come.)
	//  3 the leaf at the foot again, the player away upstairs: a nailer nails it.
	//  4 the player in sight again: the porter leaves the nailed leaf alone.
	//  5 the nailer killed: the nails fall out.
	//  6 up through the leaf: the player alone on the plate does not open the
	//    shutter, and the dial comes to rest at a tenth.
	//  7 the player on the canteen floor, in the baron's sight, RED not hung:
	//    it stays on the gallery. Then RED is hung in the canteen's frame and
	//    the leaf taken down from the foot.
	//  8 up through RED to the gallery with the leaf, and down through it
	//    again: the baron comes after the player through RED.
	//  9 RED swapped out of the canteen's frame for the leaf, through the leaf
	//    to the lobby: the baron follows and comes out of the head onto the
	//    plate.
	// 10 it is held there while the needle swings up: the dial at the mark,
	//    the shutter going up. The first time it is let go, walks off the
	//    plate, the shutter comes down, and it is killed off the plate; the
	//    second time it is killed on it.
	// 11 the first killed off the plate: "It lies where nothing weighs it",
	//    and the porter killed too; another baron on the gallery after the
	//    wait, announced.
	// 12 back through the leaf to the canteen, the leaf swapped for RED: 8
	//    to 10 again.
	// 13 the second killed on the plate: dead weight, settled, the shutter
	//    up and still up later, no more barons; and another porter in the den.
	// And at the start: the glass case's three figures, and the baron on the gallery.
	int m16phase, phaseAt, heldAt, offAt, swapAt, round;
	Vector3 held;
	bool porterAway;

	// The glass case's figures (bad: those solid, shot, counted, alive or not
	// shown), and among them a baron's body and the dial at the mark.
	int CaseFigures(bool bad)
	{
		int n = 0, baron = 0;
		let it = ThinkerIterator.Create("AjarFigure");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.args[0] == 2 && a.sprite == Actor.GetSpriteIndex("BOSS")) baron++;
			if (a.args[0] == 13 && a.sprite == Actor.GetSpriteIndex("AJWG") && a.frame == 10) baron++;
			if (!bad || a.bSolid || a.bShootable || a.bCountKill || a.bCountItem || a.bIsMonster || !a.bNoBlockmap || a.bInvisible) n++;
		}
		return bad || baron == 2 ? n : -1;
	}
	AjarThief firstPorter;

	// (each phase starts on the tic after the last one ends: the callers return)
	void NextStep(int n, int t) { m16phase = n; phaseAt = t; Console.Printf("AJARTEST phase=%d t=%d", n, t); }

	bool OnGallery(Actor a) { return a && a.health > 0 && a.pos.z == 256 && InBox(a, 144, -208, 912, -80); }
	bool InCanteen(Actor a) { return a && a.pos.z == 128 && InBox(a, 144, -704, 912, -208); }

	int LiveBarons()
	{
		int n = 0;
		let it = ThinkerIterator.Create("BaronOfHell");
		Actor a;
		while (a = Actor(it.Next())) if (a.health > 0) n++;
		return n;
	}

	void WatchYourStepCompany(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		AjarFrame foot = FindFrame(104), den = FindFrame(105), head = FindFrame(110), canteen = FindFrame(101);
		AjarDoor leaf = StairLeaf(), red = DoorOf(1), green = DoorOf(3);
		let w = Weighbridge();
		let dial = AjarWeighDial(ThinkerIterator.Create("AjarWeighDial").Next());
		if (t == 3)
		{
			Check("caseIsThere", CaseFigures(false) == 3 && !CaseFigures(true));
			Check("baronOnTheGalleryAtTheStart", OnGallery(w.baron) && w.barons == 1 && w.announced == 0);
		}
		if (t == 1)
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster && !(a is "AjarEnemy") && a != w.baron) { a.ClearCounters(); a.Destroy(); }
			thief = AjarThief(ThinkerIterator.Create("AjarThief").Next());
			firstPorter = thief;
		}
		int s = t - phaseAt;
		if (t > 20 && t % 35 == 0)
			Console.Printf("AJARTEST t=%d phase=%d porter=%s loot=%s foot=%s den=%s nailed=%d baron=%s weight=%d dead=%d shutter=%d", t, m16phase,
				thief ? String.Format("(%d,%d,%d)", thief.pos.x, thief.pos.y, thief.pos.z) : "-",
				thief && thief.loot ? thief.loot.Label() : "-", foot.door ? foot.door.Label() : "-",
				den.door ? den.door.Label() : "-", leaf.nailer != null,
				w.baron ? String.Format("(%d,%d,%d)%s", w.baron.pos.x, w.baron.pos.y, w.baron.pos.z, w.baron.health > 0 ? "" : " dead") : "-",
				w.weight, w.deadWeight, int(level.sectors[w.shutter[0]].CenterCeiling() - level.sectors[w.shutter[0]].CenterFloor()));
		if (t > 20 && t % 35 == 0 && w.baron)
		{
			let sn = AjarSense(w.baron.FindInventory("AjarSense"));
			Console.Printf("AJARTEST sense via=%d straight=%d dogged=%d target=%s state=%s", sn && sn.via ? sn.via.Index() : -1,
				sn && sn.viaStraight, sn && sn.dogged, w.baron.target ? w.baron.target.GetClassName() : 'None',
				w.baron.InStateSequence(w.baron.CurState, w.baron.SeeState) ? "see" : w.baron.InStateSequence(w.baron.CurState, w.baron.SpawnState) ? "spawn" : "other");
		}
		if (m16phase < 11 && thief && thief.health > 0 && (thief.pos.z > 41 || !InBox(thief, -1024, -768, -128, 96))) porterAway = true;

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
			// GREEN, from the labs, at the foot
			green.Used(mo);
			Pose(mo, -576, -736, 0, 270);
			foot.Activate(mo);
			Pose(mo, -576, -500, 0, 90);
			NextStep(2, t);
			return;
		}
		if (m16phase == 2 && s == 300)
		{
			Check("porterLeavesOtherDoors", foot.door == green && thief && !thief.loot);
			Unhang(foot);                                   // GREEN back to the labs
			green.carried = false;
			green.SetOrigin((700, -1400, 256), false);
			green.Show();
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
				Check("playerAloneDoesNotOpen", mo.pos.z == 384 && !w.up && !TagOpen(617));
				Check("dialReadsATenth", w.OnPlate(mo) && w.weight == 100 && dial && dial.needle == 1 && !dial.Green());
			}
			if (s == 40)
			{
				Check("dialRestsAtATenth", dial && dial.needle == 1 && !w.up && !TagOpen(617));
				Pose(mo, 464, -450, 128, 90);               // the canteen floor, under the gallery's eyes
				NextStep(7, t);
				return;
			}
		}
		if (m16phase == 7 && s == 300)
		{
			Check("baronStaysUpWithoutRed", OnGallery(w.baron) && w.baron.target == mo);
			// RED hung in the canteen's frame, the leaf down from the foot (out of the porter's sight)
			Pose(mo, 180, -608, 128, 180);
			red.Used(mo);
			canteen.Activate(mo);
			carried = Unhang(foot);
			Check("redHungLeafCarried", canteen.door == red && carried == leaf);
			round = 1;
			NextStep(8, t);
			return;
		}
		if (m16phase == 8)
		{
			if (s == 1) Pose(mo, 170, -608, 128, 180);
			Forward(mo, t, phaseAt + 1, 12);                // up through RED
			if (s == 30) Check("upThroughRedWithTheLeaf", mo.pos.z == 256 && InBox(mo, 144, -208, 912, -80) && carried == leaf);
			if (s >= 30 && s < 400 && !offAt && !heldAt && w.baron && w.baron.target == mo) heldAt = s;
			if (!offAt && ((heldAt && s == heldAt + 35) || s == 400))   // seen by it a second: down through RED again
			{
				heldAt = 0;
				Pose(mo, 528, -110, 256, 90);
				offAt = s;
			}
			if (offAt) Forward(mo, t, phaseAt + offAt, 12);
			if (offAt && s == offAt + 20)
			{
				Check("downThroughRed", InCanteen(mo));
				Pose(mo, 420, -660, 128, 180);              // out of the way of the frame, where it comes out
			}
			if (offAt && s > offAt + 20 && (InCanteen(w.baron) || s > offAt + 900))
			{
				Check("baronComesThroughRed", InCanteen(w.baron) && w.baron.health > 0);
				offAt = 0;
				NextStep(9, t);
				return;
			}
		}
		if (m16phase == 9)
		{
			// RED out, the leaf in; through it to the lobby, and off to its west side
			// (once it has come away from the frame after the player)
			if (!swapAt && (!w.baron || w.baron.pos.x > 300 || s > 300))
			{
				swapAt = s;
				Pose(mo, 180, -608, 128, 180);
				canteen.Activate(mo);
				Check("redSwappedForTheLeaf", carried == red && canteen.door == leaf && head.door.args[0] == 101);
			}
			if (swapAt) Forward(mo, t, phaseAt + swapAt, 20);
			if (swapAt && s == swapAt + 35)
			{
				Check("throughTheLeafToTheLobby", mo.pos.z == 384 && InBox(mo, 784, -2240, 1168, -1856));
				Pose(mo, 880, -2200, 384, 0);
			}
			if (swapAt && s > swapAt + 35 && (w.OnPlate(w.baron) || s > swapAt + 935))
			{
				Check("baronOutOfTheHeadOntoThePlate", w.baron && w.baron.health > 0 && w.OnPlate(w.baron) && w.baron.pos.z == 384);
				held = w.baron ? w.baron.pos : (0, 0, 0);
				swapAt = 0;
				NextStep(10, t);
				return;
			}
		}
		if (m16phase == 10)
		{
			// held where it stepped onto the plate while the needle swings up
			if (s < 70 && w.baron && w.baron.health > 0) { w.baron.SetOrigin(held, false); w.baron.vel = (0, 0, 0); }
			if (s == 70)
			{
				Check("dialAtTheMark", w.up && w.weight >= w.HEAVY && dial && dial.needle >= 10 && dial.Green() && TagOpen(617));
				Console.Printf("AJARTEST weight=%d needle=%d by=%s", w.weight, dial ? dial.needle : -1, w.openedBy ? w.openedBy.GetClassName() : 'None');
				if (round == 2)
				{
					w.baron.DamageMobj(null, null, 10000, 'None');      // killed on the plate
					NextStep(13, t);
					return;
				}
			}
			if (s > 70 && !offAt && w.baron && !w.OnPlate(w.baron)) offAt = s;
			if (offAt && s == offAt + 170)
			{
				Check("shutterDownAfterItLeft", !w.up && w.IsDown() && !TagOpen(617));
				Check("baronOffThePlate", w.baron.health > 0 && !w.OnPlate(w.baron));
				w.baron.DamageMobj(null, null, 10000, 'None');          // killed off the plate
				offAt = 0;
				NextStep(11, t);
				return;
			}
			if (s == 1500) { Check("baronWalksOffThePlate", false); NextStep(11, t); return; }
		}
		if (m16phase == 11)
		{
			if (s == 10)
			{
				Check("itLiesWhereNothingWeighsIt", w.lostSaid == 1 && !w.settled && !w.up);
				thief.DamageMobj(null, null, 1000, 'None');
			}
			if (s == 30) Check("porterKilled", firstPorter.health <= 0);
			if (s == 600) Check("noBaronBeforeTheWait", w.barons == 1 && !LiveBarons());
			if (s == 20 * 35 + 60)
			{
				Check("anotherOnTheGalleryAnnounced", w.barons == 2 && w.announced == 1 && OnGallery(w.baron));
				NextStep(12, t);
				return;
			}
		}
		if (m16phase == 12)
		{
			// back through the leaf from the lobby, carrying RED; the leaf swapped for RED in the canteen
			if (s == 1) Pose(mo, 1130, -2048, 384, 0);
			Forward(mo, t, phaseAt + 1, 10);
			if (s == 30)
			{
				Check("backToTheCanteen", InCanteen(mo) && carried == red);
				Pose(mo, 180, -608, 128, 180);
				canteen.Activate(mo);
				Check("leafSwappedForRed", carried == leaf && canteen.door == red);
				round = 2;
				NextStep(8, t);
				return;
			}
		}
		if (m16phase == 13)
		{
			if (s == 30) Check("deadWeightSettles", w.settled && w.deadWeight >= w.HEAVY && w.up);
			if (s == 300) Check("shutterStaysUp", w.IsUp() && TagOpen(617));
			if (s == 900)
			{
				Check("shutterStillUp", w.IsUp() && TagOpen(617) && w.settled);
				Check("noMoreBarons", w.barons == 2 && !LiveBarons());
				AjarThief next = null;
				let ti = ThinkerIterator.Create("AjarThief");
				AjarThief th;
				while (th = AjarThief(ti.Next())) if (th != firstPorter && th.health > 0) next = th;
				if (next) Console.Printf("AJARTEST nextPorter=(%d,%d,%d)", next.pos.x, next.pos.y, next.pos.z);
				Check("anotherPorterComes", next != null && next.args[2] == 105 && InBox(next, -768, -112, -384, 96));
				NextStep(14, t);
				return;
			}
		}
	}
}
