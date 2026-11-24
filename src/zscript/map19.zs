// MAP19 "On Paper" (tools/map_paper.py): the level's own words, its
// registers' names, and the smoke tests. The pass, its double, the registers
// and the desks are the pass lab's (pass.zs); the way out is MAP09's chain
// (ajar.zs, ChainTick). Both handlers are named in MAP19's MAPINFO only.
//
// MAP=MAP19 MODE=1..4 tools/smoke.sh (PaperTest, below):
//   1  the whole level by the answers meant, in the order of the stages, and
//      out by VIOLET and PINK in the brass frames
//   2  what must not work: RED in 102, GREEN in 103, 4 and 6 laps for 5, 2
//      laps for 6, walking over a plate without stopping; GREEN in 102 kept on
//      upstairs (registers 3 and 4 not signed by it); the balcony's door shut
//      before register 4 and open after
//   3  the building's own: the covered way, the porter's lodge, the boat
//      store and the island, the gazebo, the desks, the courts' ways in and
//      out, the drop from the balcony, the two secrets
//   4  views (tools/smoke_MAP19_4.cfg takes a screenshot of each)
// The player is god-moded and unseen, and every placed monster is gone; the
// ambushes stay, and each one that comes is counted and taken away at once
// (the autotest's rule, ajar.zs).
// The places come from the MapSpots map_paper.py puts (TEST_SPOTS there).

class AjarPaper : EventHandler
{
	int partedAt;               // the tic the pass first parted from the player (0: not yet)
	bool introSaid;

	// The registers, by number: their names (map_paper.py gives them the same; the build checks it) ...
	static string RegisterName(int n)
	{
		static const string names[] = { "a register", "the duty room", "the stack", "the side room", "the hall with no stair",
			"down the bricked-up gallery", "down the bricked-up stair", "the boathouse", "the porter's lodge", "the island" };
		return names[clamp(n, 0, 9)];
	}

	// ... and what signing each one opens
	static string Opened(int n)
	{
		static const string what[] = { "Its door is unbolted.", "The barrier to the covered way is up.", "The stair hall is unbolted.",
			"The basement is unbolted.", "The garden and the balcony are unbolted.", "The east strongroom is unbolted.",
			"The tower's strongroom is unbolted.", "The kiosk is unbolted.", "The lodge is unbolted.", "The footbridge is up." };
		return what[clamp(n, 0, 9)];
	}

	void Say(string msg)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(msg);
	}

	override void WorldTick()
	{
		// after the game's own word on doors (AjarHandler.PlayerSpawned) has been read
		if (!introSaid && level.maptime >= 105)
		{
			introSaid = true;
			Say("Your pass is issued. It counts your steps\nand knows nothing about doors.");
		}
		let dbl = AjarPassDouble.Get();
		if (!partedAt && dbl && dbl.crossings > 0 && !dbl.IsIdentity())
		{
			partedAt = level.maptime;
			Say("The pass took that door for a hole in the wall.\nOn paper you are where the white figure stands.");
		}
	}
}

class PaperTest : EventHandler
{
	const RUN = 16.67;
	const WALK = 8.33;
	const PROG = 3000;          // + n: where the player stands for register n's answer meant
	const FRONT = 3000;         // + frame number: 32 in front of the frame, turned into it
	const FARS = 3200;          // + colour: 32 in front of that far side
	const DESKS = 1970;         // + k: the pass desks (AjarPassDesk's tid)
	int tic, checks, fails;
	int pc, k, opT, lastPc;
	bool stepped, finished;
	AjarHandler h;
	AjarPaper paper;
	AjarPassDouble dbl;
	int seenCross;
	int ambushAt[64];           // the ambushers of each cause at the start

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP19"; }

	// --- the running order: one op at a time, each as long as it takes ---------------
	bool Op() { bool me = k == pc && !stepped; k++; return me; }
	void Next() { pc++; stepped = true; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info t=%d %s", tic, s); }

	string TStr() { return String.Format("T(turn %.3f, shift %.4f %.4f, height %.4f)", dbl.tAng, dbl.tOff.x, dbl.tOff.y, dbl.tDz); }
	string PStr(Vector3 p) { return String.Format("(%.3f,%.3f,%.3f)", p.x, p.y, p.z); }
	bool TIs(double a, double x, double y, double z)
	{
		return abs(Actor.DeltaAngle(dbl.tAng, a)) < 1e-9 && abs(dbl.tOff.x - x) < 0.001 && abs(dbl.tOff.y - y) < 0.001 && abs(dbl.tDz - z) < 0.001;
	}
	bool OnT(Actor mo)
	{
		return (dbl.pos - dbl.Apply(mo.pos)).Length() < 1e-6 && abs(Actor.DeltaAngle(dbl.angle, mo.angle + dbl.tAng)) < 1e-6;
	}
	bool Inside(Vector3 p, double x1, double y1, double x2, double y2) { return p.x > x1 && p.x < x2 && p.y > y1 && p.y < y2; }

	Actor Spot(int tid) { return level.CreateActorIterator(tid).Next(); }
	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }

	void PoseF(Actor mo, double x, double y, double ang)
	{
		mo.SetOrigin((x, y, FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
		dbl.Posed(mo);
	}
	bool PoseAt(Actor mo, int tid)
	{
		Actor s = Spot(tid);
		if (!s) { Check(String.Format("spot%d", tid), false, "no such MapSpot"); return true; }
		PoseF(mo, s.pos.x, s.pos.y, s.angle);
		return true;
	}

	AjarPassRegister Reg(int n)
	{
		let it = ThinkerIterator.Create("AjarPassRegister");
		AjarPassRegister r;
		while (r = AjarPassRegister(it.Next())) if (r.args[3] == n) return r;
		return null;
	}

	// --- ops (each returns true when it is over) ------------------------------------
	// Into the frame or far side in front of MapSpot tid (0: from where the player
	// is, as he faces), running, until `want` crossings and `extra` tics more.
	int c0, crossAt, unexp0;
	bool Through(Actor mo, string name, int tid, int want = 1, int extra = 4, int limit = 90)
	{
		if (opT == 0)
		{
			if (tid) PoseAt(mo, tid);
			c0 = dbl.crossings;
			unexp0 = dbl.unexplained;
			crossAt = -1;
		}
		int n = dbl.crossings - c0;
		if (n >= want && crossAt < 0) crossAt = opT;
		if ((crossAt >= 0 && opT - crossAt >= extra) || opT >= limit)
		{
			mo.vel.xy = (0, 0);
			Check(name, n == want && dbl.unexplained == unexp0 && OnT(mo), String.Format("crossed %d in %d tics; %s; player %s, double %s",
				n, crossAt, TStr(), PStr(mo.pos), PStr(dbl.pos)));
			return true;
		}
		mo.vel.xy = Actor.AngleToVector(mo.angle, RUN);
		return false;
	}

	// On foot in a straight line to x, y (no crossing on the way).
	bool WalkTo(Actor mo, string name, double x, double y, int limit = 300, double speed = RUN)
	{
		if (opT == 0) c0 = dbl.crossings;
		Vector2 d = (x, y) - mo.pos.xy;
		double len = d.Length();
		if (len < 0.01 || opT >= limit)
		{
			mo.vel.xy = (0, 0);
			Check(name, len < 0.01 && dbl.crossings == c0, String.Format("player %s after %d tics, crossings %d", PStr(mo.pos), opT, dbl.crossings - c0));
			return true;
		}
		mo.vel.xy = len <= speed ? d : d / len * speed;
		return false;
	}

	// Pose at MapSpot tid (0: stay) and go forward n tics.
	bool Forward(Actor mo, int tid, int n, double speed = RUN)
	{
		if (opT == 0 && tid) PoseAt(mo, tid);
		if (opT >= n) { mo.vel.xy = (0, 0); return true; }
		mo.vel.xy = Actor.AngleToVector(mo.angle, speed);
		return false;
	}

	bool Stand(Actor mo, int n) { mo.vel.xy = (0, 0); return opT >= n; }

	bool WaitSigned(string name, int n, int limit = 70)
	{
		let r = Reg(n);
		if (!r) { Check(name, false, "no register"); return true; }
		if (!r.signed && opT < limit) return false;
		string want = String.Format("Signed in: %s.\n%s", AjarPaper.RegisterName(n), AjarPaper.Opened(n));
		Check(name, r.signed && h.said == want && r.frame == 2, String.Format("signed %d tics into the wait; said \"%s\"; the double %s, the plate (%.0f,%.0f,%.0f)",
			opT, h.said, PStr(dbl.pos), r.pos.x, r.pos.y, r.plateZ));
		return true;
	}

	bool NotSigned(string name, int n)
	{
		let r = Reg(n);
		double d = r ? (dbl.pos.xy - r.pos.xy).Length() : -1;
		Check(name, r && !r.signed, String.Format("the double %s, %.0f from the plate's middle (%.0f,%.0f,%.0f); player %s; %s",
			PStr(dbl.pos), d, r.pos.x, r.pos.y, r.plateZ, PStr(Players[consoleplayer].mo.pos), TStr()));
		return true;
	}

	// Every sector with `tag` open (more than 56 between floor and ceiling); `want` of them.
	bool DoorUp(string name, int tag, int want, int limit = 70)
	{
		int n = 0, up = 0;
		let it = level.CreateSectorTagIterator(tag);
		int i;
		while ((i = it.Next()) >= 0)
		{
			n++;
			Sector s = level.sectors[i];
			if (s.ceilingplane.ZatPoint(s.centerspot) - s.floorplane.ZatPoint(s.centerspot) > 56) up++;
		}
		if (up < n && opT < limit) return false;
		Check(name, n == want && up == n, String.Format("%d of %d sectors with tag %d open, %d tics", up, n, tag, opT));
		return true;
	}

	bool DeskAt(Actor mo, string name, int k)
	{
		if (opT == 0)
		{
			Actor d = Spot(DESKS + k);
			if (!d) { Check(name, false, "no desk"); return true; }
			Info(String.Format("onto desk %d, %s", k, TStr()));
			PoseF(mo, d.pos.x, d.pos.y, mo.angle);
			return false;
		}
		if (opT < 3) return false;
		Check(name, dbl.IsIdentity() && dbl.pos == mo.pos, String.Format("%s; said \"%s\"", TStr(), h.said));
		return true;
	}

	bool TakeDoor(Actor mo, AjarDoor d)
	{
		if (h.carried && h.carried != d) h.BeltPutBack(h.carried);
		if (h.carried == d) return true;
		if (d.frame) h.UseFrame(d.frame, mo);
		else h.TakeLeaning(d, mo);
		return true;
	}

	bool HangIn(Actor mo, string name, int frame)
	{
		AjarDoor d = h.carried;
		AjarFrame f = h.FindFrame(frame);
		if (!d || !f) { Check(name, false, "nothing carried, or no frame"); return true; }
		h.UseFrame(f, mo);
		Check(name, f.door == d, String.Format("said \"%s\"", h.said));
		if (h.carried) h.BeltPutBack(h.carried);        // a door swapped out goes back where it leant
		return true;
	}

	// Laps: forward until `want` crossings, then on foot to x, y; T is then (a, ex, ey, ez).
	int lapPhase;
	bool Laps(Actor mo, string name, int want, double x, double y, double a, double ex, double ey, double ez, int limit = 700)
	{
		if (opT == 0) { c0 = dbl.crossings; unexp0 = dbl.unexplained; lapPhase = 0; }
		int n = dbl.crossings - c0;
		if (lapPhase == 0)
		{
			if (n >= want) lapPhase = 1;
			else mo.vel.xy = Actor.AngleToVector(mo.angle, RUN);
		}
		if (lapPhase == 1)
		{
			Vector2 d = (x, y) - mo.pos.xy;
			double len = d.Length();
			if (len < 0.01) lapPhase = 2;
			else mo.vel.xy = len <= RUN ? d : d / len * RUN;
		}
		if (lapPhase == 2 || opT >= limit)
		{
			mo.vel.xy = (0, 0);
			Check(name, lapPhase == 2 && n == want && TIs(a, ex, ey, ez) && OnT(mo) && dbl.unexplained == unexp0,
				String.Format("%d crossings in %d tics; %s; player %s, double %s", n, opT, TStr(), PStr(mo.pos), PStr(dbl.pos)));
			return true;
		}
		return false;
	}

	void ClearOut()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
	}

	int AmbushLeft(int cause)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == cause) n++;
		return n;
	}

	// Company: the ambushes of these causes have come (each has at least one that does not wait to be seen).
	void Company(string causes, string watched)
	{
		Array<String> cs;
		causes.Split(cs, " ");
		for (int i = 0; i < cs.Size(); i++)
		{
			int c = cs[i].ToInt();
			int came = ambushAt[c] - AmbushLeft(c);
			Check(String.Format("company%d", c), ambushAt[c] > 0 && came > 0, String.Format("%d of %d came", came, ambushAt[c]));
		}
		watched.Split(cs, " ");
		for (int i = 0; i < cs.Size(); i++)
		{
			int c = cs[i].ToInt();
			Info(String.Format("company %d (they wait to see the player): %d of %d came", c, ambushAt[c] - AmbushLeft(c), ambushAt[c]));
		}
	}

	void Summary()
	{
		if (finished) return;
		finished = true;
		Console.Printf("AJARTEST info unexplained jumps %d, two crossings in a tic %d, crossings %d", dbl.unexplained, dbl.twoInOne, dbl.crossings);
		Console.Printf("AJARTEST paperDone=1 checks=%d failed=%d", checks, fails);
	}

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			lastPc = -1;                // so that the first op starts at its tic 0
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			paper = AjarPaper(EventHandler.Find("AjarPaper"));
			ClearOut();
			for (int c = 0; c < 64; c++) ambushAt[c] = AmbushLeft(c);
		}
		if (!dbl) dbl = AjarPassDouble.Get();
		if (!dbl || tic < 3) return;
		if (dbl.crossings != seenCross)
		{
			seenCross = dbl.crossings;
			Info(String.Format("cross n=%d from line %d; %s; player %s, double %s", dbl.crossings, dbl.lastSrc ? dbl.lastSrc.Index() : -1,
				TStr(), PStr(mo.pos), PStr(dbl.pos)));
		}
		if (pc != lastPc) { lastPc = pc; opT = 0; }
		else opT++;
		k = 0;
		stepped = false;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode == 1) Whole(mo);
		else if (mode == 2) Refused(mo);
		else if (mode == 3) Building(mo);
		else if (mode == 4) Views(mo);
		if (mode != 4 && pc >= k) Summary();
	}

	// --- MODE=1: the whole level by the answers meant ------------------------------------
	void Whole(Actor mo)
	{
		AjarDoor red = h.DoorOf(1), blue = h.DoorOf(2), green = h.DoorOf(3), yellow = h.DoorOf(4), violet = h.DoorOf(5), pink = h.DoorOf(6);
		if (Op())
		{
			Check("startsOnThePlayer", dbl.IsIdentity() && dbl.pos == mo.pos, PStr(mo.pos));
			Check("wordsAtStart", h.said.IndexOf("USE a door") == 0 || h.said.IndexOf("Your pass is issued") == 0, h.said);
			Next();
		}
		// the gatehouse: RED in 101, the double into the duty room
		if (Op() && TakeDoor(mo, red)) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && PoseAt(mo, FRONT + 101)) Next();
		if (Op() && HangIn(mo, "redHungIn101", 101)) Next();
		if (Op() && Through(mo, "red101_cross", FRONT + 101, 1)) Next();
		if (Op())
		{
			Check("wordsAtTheParting", paper.partedAt > 0 && h.said.IndexOf("hole in the wall") > 0, h.said);
			Next();
		}
		if (Op() && WalkTo(mo, "reg1_walkToTheAnswer", 1104, 1408)) Next();
		if (Op() && WaitSigned("reg1_signedByRED", 1)) Next();
		if (Op() && DoorUp("reg1_barrierAndDutyRoomOpen", 1901, 2)) Next();
		// the block: GREEN taken down from 112 by its far side in the archive, out of the east yard, hung in 102
		if (Op() && DeskAt(mo, "desk2_resets", 2)) Next();
		if (Op() && Through(mo, "greenFarSide_intoTheEastYard", FARS + 3, 1)) Next();
		if (Op())
		{
			Check("inTheEastYard", Inside(mo.pos, 6912, 2752, 7872, 3712) && mo.pos.z == 0, PStr(mo.pos));
			TakeDoor(mo, green);
			Check("greenTakenDownFrom112", h.carried == green && !h.FindFrame(112).door, h.said);
			Next();
		}
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && Forward(mo, 3402, 12)) Next();
		if (Op() && Stand(mo, 10)) Next();
		if (Op()) { Check("outOfTheEastYardWithGreen", Inside(mo.pos, 3776, 3456, 6848, 3648) && mo.pos.z == 0 && h.carried == green, PStr(mo.pos)); Next(); }
		if (Op() && DeskAt(mo, "desk3_resets", 3)) Next();
		if (Op() && PoseAt(mo, FRONT + 102)) Next();
		if (Op() && HangIn(mo, "greenHungIn102", 102)) Next();
		if (Op() && Through(mo, "green102_cross", FRONT + 102, 1)) Next();
		if (Op() && WalkTo(mo, "reg2_walkToTheAnswer", 2592, 2912)) Next();
		if (Op() && WaitSigned("reg2_signedByGREEN", 2)) Next();
		if (Op() && DoorUp("reg2_stairHallOpen", 1902, 1)) Next();
		// up the grand stair on foot, past BLUE's pier and off the way's axis (2026-11-24: the way was two
		// slots 32 wide, which nobody but a test set down in the middle of one could pass)
		if (Op()) { PoseF(mo, 1756, 3760, 90); Next(); }
		if (Op() && WalkTo(mo, "stairHall_upTheGrandStairOnFoot", 1756, 4544)) Next();
		if (Op()) { Check("stairHall_onTheTopLandingOnFoot", abs(mo.pos.z - 256) < 0.001, PStr(mo.pos)); Next(); }
		if (Op()) { PoseF(mo, 1796, 4544, 270); Next(); }
		if (Op() && WalkTo(mo, "stairHall_downTheGrandStairOnFoot", 1796, 3760)) Next();
		if (Op()) { Check("stairHall_backInTheHallOnFoot", abs(mo.pos.z) < 0.001, PStr(mo.pos)); Next(); }
		// into the drawing office on foot from the upper corridor, off the way in's axis (x 3328), round the
		// counter by the gap between it and the west bench (x 3136..3200, walked at 3172, off its axis) and to
		// the front of 122 (2026-11-24: the counter stood 32 from the north wall, straight across the way in,
		// and nobody got in). The room's monsters are gone (ClearOut, as everywhere in the test); its ambushes
		// wait for TEAL, not taken yet here, and stand nowhere (NOBLOCKMAP); the TEAL leaves on its floor are
		// not solid. So nothing but the walls and the furniture is in the way, as for a player who has cleared it.
		if (Op()) { PoseF(mo, 3304, 4736, 270); Next(); }
		if (Op() && WalkTo(mo, "drawing_inFromTheCorridorOnFoot", 3304, 4424)) Next();
		if (Op() && WalkTo(mo, "drawing_alongTheCounterOnFoot", 3172, 4424)) Next();
		if (Op() && WalkTo(mo, "drawing_betweenCounterAndBenchOnFoot", 3172, 4192)) Next();
		if (Op() && WalkTo(mo, "drawing_toTheFrontOf122OnFoot", 3296, 4128)) Next();
		if (Op()) { Check("drawing_inTheRoomBefore122", abs(mo.pos.z - 256) < 0.001 && Inside(mo.pos, 2944, 4096, 3712, 4512), PStr(mo.pos)); Next(); }
		// the upper floor: RED in 103, the double into the side room
		if (Op() && DeskAt(mo, "desk2_resetsAgain", 2)) Next();
		if (Op() && TakeDoor(mo, red)) Next();
		if (Op() && PoseAt(mo, FRONT + 103)) Next();
		if (Op() && HangIn(mo, "redHungIn103", 103)) Next();
		if (Op() && Through(mo, "red103_cross", FRONT + 103, 1)) Next();
		if (Op() && WalkTo(mo, "reg3_walkToTheAnswer", 1216, 1968)) Next();
		if (Op() && WaitSigned("reg3_signedByRED", 3)) Next();
		if (Op() && DoorUp("reg3_basementOpen", 1903, 1)) Next();
		// the basement: BLUE in 104, and up the grand stair
		if (Op() && DeskAt(mo, "desk3_resetsAgain", 3)) Next();
		if (Op() && TakeDoor(mo, blue)) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && PoseAt(mo, FRONT + 104)) Next();
		if (Op() && HangIn(mo, "blueHungIn104", 104)) Next();
		if (Op() && Through(mo, "blue104_cross", FRONT + 104, 1)) Next();
		if (Op() && WalkTo(mo, "reg4_upTheGrandStair", 1888, 4512)) Next();
		if (Op()) { Check("reg4_onTheTopLanding", abs(mo.pos.z - 256) < 0.001 && abs(dbl.pos.z - 256) < 0.001, String.Format("player %s, double %s", PStr(mo.pos), PStr(dbl.pos))); Next(); }
		if (Op() && WaitSigned("reg4_signedByBLUE", 4)) Next();
		if (Op() && DoorUp("reg4_gardenNoSizeAndBalconyOpen", 1904, 3)) Next();        // the garden's, the hall with no size's, the balcony's
		// register 5: a TEAL leaf in 105 and 106, five laps east
		if (Op() && TakeDoor(mo, h.LabLeaf(8, 0))) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && HangIn(mo, "tealHungIn105", 105)) Next();
		if (Op() && TakeDoor(mo, h.LabLeaf(8, 1))) Next();
		if (Op() && HangIn(mo, "tealHungIn106", 106)) Next();
		if (Op() && DeskAt(mo, "desk3_resetsBeforeTheLaps", 3)) Next();
		if (Op()) { PoseF(mo, 3328, 3296, 0); Next(); }
		if (Op() && Laps(mo, "reg5_fiveLapsEast", 5, 3328, 3296, 0, 2720, 0, 0)) Next();
		if (Op() && WaitSigned("reg5_signedByFiveLaps", 5)) Next();
		if (Op() && DoorUp("reg5_eastStrongroomOpen", 1905, 1)) Next();
		// out of the link hall on foot by its side door, back in, and out again at a walk (2026-11-23: its
		// lintel came down with its two steps, and Vadim, in the hall with both leaves hung, could not get out)
		if (Op() && WalkTo(mo, "linkHall_outByTheSideDoor", 3328, 3488, 100)) Next();
		if (Op() && Stand(mo, 8)) Next();
		if (Op()) { Check("linkHall_downInTheVestibule", mo.pos.z == 0, PStr(mo.pos)); Next(); }
		if (Op() && WalkTo(mo, "linkHall_backInByTheSideDoor", 3328, 3296, 100)) Next();
		if (Op()) { Check("linkHall_upInTheHall", mo.pos.z == 64, PStr(mo.pos)); Next(); }
		if (Op() && WalkTo(mo, "linkHall_outAtAWalk", 3312.5, 3488, 200, 3)) Next();
		if (Op() && Stand(mo, 8)) Next();
		if (Op()) { Check("linkHall_downAgain", mo.pos.z == 0, PStr(mo.pos)); Next(); }
		// register 7: GREEN taken down from 102, through the balcony's door (register 4's, open since) and over the
		// balcony into the pond court, hung in 113
		if (Op() && DeskAt(mo, "desk3_resetsThirdTime", 3)) Next();
		if (Op() && TakeDoor(mo, green)) Next();
		if (Op() && Forward(mo, 3406, 18)) Next();
		if (Op() && Stand(mo, 30)) Next();
		if (Op()) { Check("throughTheBalconyDoorIntoThePondCourtWithGreen", Inside(mo.pos, 4928, 3712, 6848, 5568) && mo.pos.z == 0 && h.carried == green, PStr(mo.pos)); Next(); }
		if (Op() && PoseAt(mo, FRONT + 113)) Next();
		if (Op() && HangIn(mo, "greenHungIn113", 113)) Next();
		if (Op() && Through(mo, "green113_cross", FRONT + 113, 1)) Next();
		if (Op() && WalkTo(mo, "reg7_walkToTheAnswer", 2592, 2912)) Next();
		if (Op() && WaitSigned("reg7_signedByGREEN", 7)) Next();
		if (Op() && DoorUp("reg7_kioskOpen", 1907, 1)) Next();
		// register 6: YELLOW from the kiosk into 113; both ORANGE leaves through it into the tower yard
		if (Op() && TakeDoor(mo, yellow)) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && PoseAt(mo, FRONT + 113)) Next();
		if (Op() && HangIn(mo, "yellowHungIn113", 113)) Next();
		if (Op() && TakeDoor(mo, h.LabLeaf(9, 0))) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && Through(mo, "orange1_throughYellow", FRONT + 113, 1)) Next();
		if (Op()) { Check("inTheTowerYardWithOrange", Inside(mo.pos, 5760, 64, 7168, 1728) && h.carried == h.LabLeaf(9, 0), PStr(mo.pos)); Next(); }
		if (Op() && PoseAt(mo, FRONT + 107)) Next();
		if (Op() && HangIn(mo, "orangeHungIn107", 107)) Next();
		if (Op() && Through(mo, "backThroughYellow", FARS + 4, 1)) Next();
		if (Op() && TakeDoor(mo, h.LabLeaf(9, 1))) Next();
		if (Op() && Through(mo, "orange2_throughYellow", FRONT + 113, 1)) Next();
		if (Op() && PoseAt(mo, FRONT + 108)) Next();
		if (Op() && HangIn(mo, "orangeHungIn108", 108)) Next();
		// out of the tower yard by its turnstile, the pass stamped in the garden, in again by the squeeze
		if (Op() && Forward(mo, 3404, 12)) Next();
		if (Op() && Stand(mo, 10)) Next();
		if (Op()) { Check("outOfTheTowerYard", Inside(mo.pos, 1536, 64, 5696, 2176), PStr(mo.pos)); Next(); }
		if (Op() && DeskAt(mo, "desk4_resets", 4)) Next();
		if (Op() && Forward(mo, 3403, 12)) Next();
		if (Op()) { Check("inTheTowerYardBySqueeze", Inside(mo.pos, 5760, 64, 7168, 1728), PStr(mo.pos)); Next(); }
		if (Op()) { PoseF(mo, 6368, 512, 90); Next(); }
		if (Op() && Laps(mo, "reg6_threeLapsDown", 3, 6368, 896, 0, 0, 1632, -384)) Next();
		if (Op() && WaitSigned("reg6_signedByThreeLaps", 6)) Next();
		if (Op() && DoorUp("reg6_towerStrongroomOpen", 1906, 1)) Next();
		// the way out: VIOLET and PINK in the brass frames
		if (Op() && TakeDoor(mo, violet)) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && HangIn(mo, "violetHungIn190", 190)) Next();
		if (Op() && TakeDoor(mo, pink)) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && HangIn(mo, "pinkHungIn191", 191)) Next();
		if (Op() && Stand(mo, 240)) Next();
		if (Op())
		{
			Company("11 12 13 14 15 16 18 19 51 55 56 57", "52 53 54");
			Check("allSeven", Reg(1).signed && Reg(2).signed && Reg(3).signed && Reg(4).signed && Reg(5).signed && Reg(6).signed && Reg(7).signed);
			Summary();
			Next();
		}
		if (Op() && PoseAt(mo, FRONT + 190)) Next();
		if (Op())
		{
			mo.vel.xy = Actor.AngleToVector(mo.angle, RUN);
			if (opT > 120) { Check("outByTheNightRoom", false, PStr(mo.pos)); Next(); }
		}
	}

	// --- MODE=2: what must not work ----------------------------------------------------
	void Refused(Actor mo)
	{
		AjarDoor red = h.DoorOf(1), green = h.DoorOf(3);
		// RED in 102: the forecourt runs out before the stack does
		if (Op() && TakeDoor(mo, red)) Next();
		if (Op() && PoseAt(mo, FRONT + 102)) Next();
		if (Op() && HangIn(mo, "redHungIn102", 102)) Next();
		if (Op() && Through(mo, "red102_cross", FRONT + 102, 1)) Next();
		if (Op() && WalkTo(mo, "red102_acrossTheForecourt", 864, 1408)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg2_notByRED_forecourt", 2)) Next();
		if (Op() && WalkTo(mo, "red102_ontoTheDais", 736, 1408)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg2_notByRED_dais", 2)) Next();
		// GREEN in 103: the reading corridor has no room to the right
		if (Op() && DeskAt(mo, "desk1_resets", 1)) Next();
		if (Op() && TakeDoor(mo, green)) Next();
		if (Op() && PoseAt(mo, FRONT + 103)) Next();
		if (Op() && HangIn(mo, "greenHungIn103", 103)) Next();
		if (Op() && Through(mo, "green103_cross", FRONT + 103, 1)) Next();
		if (Op() && WalkTo(mo, "green103_eastAlongTheCorridor", 1888, 2860)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg3_notByGREEN_near", 3)) Next();
		if (Op() && WalkTo(mo, "green103_further", 2400, 2860)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg3_notByGREEN_far", 3)) Next();
		// 4 and 6 laps of the link hall
		if (Op() && TakeDoor(mo, h.LabLeaf(8, 0))) Next();
		if (Op() && HangIn(mo, "tealHungIn105", 105)) Next();
		if (Op() && TakeDoor(mo, h.LabLeaf(8, 1))) Next();
		if (Op() && HangIn(mo, "tealHungIn106", 106)) Next();
		if (Op() && DeskAt(mo, "desk3_resets", 3)) Next();
		if (Op()) { PoseF(mo, 3328, 3296, 0); Next(); }
		if (Op() && Laps(mo, "fourLaps", 4, 3328, 3296, 0, 2176, 0, 0)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg5_notByFourLaps", 5)) Next();
		if (Op() && DeskAt(mo, "desk3_resetsAgain", 3)) Next();
		if (Op()) { PoseF(mo, 3328, 3296, 0); Next(); }
		// (on the way to six, the fifth lap carries the double over the plate at a run: not signed either)
		if (Op() && Laps(mo, "sixLaps", 6, 3328, 3296, 0, 3264, 0, 0)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg5_notBySixLaps_norByPassingOverAtFive", 5)) Next();
		// 2 laps of the water tower's flight
		if (Op() && TakeDoor(mo, h.LabLeaf(9, 0))) Next();
		if (Op() && HangIn(mo, "orangeHungIn107", 107)) Next();
		if (Op() && TakeDoor(mo, h.LabLeaf(9, 1))) Next();
		if (Op() && HangIn(mo, "orangeHungIn108", 108)) Next();
		if (Op() && DeskAt(mo, "desk4_resets", 4)) Next();
		if (Op()) { PoseF(mo, 6368, 512, 90); Next(); }
		if (Op() && Laps(mo, "twoLapsDown", 2, 6368, 896, 0, 0, 1088, -256)) Next();
		if (Op() && Stand(mo, 45)) Next();
		if (Op() && NotSigned("reg6_notByTwoLaps", 6)) Next();
		// over register 1's plate without stopping, then stopped on it
		if (Op() && DeskAt(mo, "desk2_resets", 2)) Next();
		if (Op() && TakeDoor(mo, red)) Next();
		if (Op() && HangIn(mo, "redHungIn101", 101)) Next();
		if (Op() && Through(mo, "red101_cross", FRONT + 101, 1)) Next();
		if (Op() && WalkTo(mo, "red101_overThePlateAtARun", 880, 1408)) Next();
		if (Op() && NotSigned("reg1_passingOverSignsNothing", 1)) Next();
		if (Op() && WalkTo(mo, "red101_backToTheAnswer", 1104, 1408)) Next();
		if (Op() && WaitSigned("reg1_stoppedOnItSigns", 1)) Next();
		if (Op())
		{
			Check("noneOfTheRestSigned", !Reg(2).signed && !Reg(3).signed && !Reg(5).signed && !Reg(6).signed);
			Next();
		}
		// GREEN in 102 kept on upstairs (2026-11-24: Vadim, the stack signed, stood beyond the grand stair's head and
		// register 4 signed itself; the stack now stands 112 up, and GREEN in 102 carries that): the stack signed, the
		// player stands 2 s at each patch where it used to put the double on register 3's or 4's plate
		if (Op() && DeskAt(mo, "desk2_resetsForTheLeaks", 2)) Next();
		if (Op() && TakeDoor(mo, green)) Next();
		if (Op() && PoseAt(mo, FRONT + 102)) Next();
		if (Op() && HangIn(mo, "greenHungIn102", 102)) Next();
		if (Op() && Through(mo, "green102_cross", FRONT + 102, 1)) Next();
		if (Op() && WalkTo(mo, "green102_toTheStackAnswer", 2592, 2912)) Next();
		if (Op() && WaitSigned("reg2_signedByGREEN", 2)) Next();
		if (Op()) { PoseF(mo, 2112, 4736, 0); Next(); }
		if (Op() && Stand(mo, 70)) Next();
		if (Op() && NotSigned("reg4_notByGREEN102_upperCorridor", 4)) Next();
		if (Op() && NotSigned("reg3_notByGREEN102_upperCorridor", 3)) Next();
		if (Op()) { PoseF(mo, 4560, 5200, 90); Next(); }
		if (Op() && Stand(mo, 70)) Next();
		if (Op() && NotSigned("reg3_notByGREEN102_upperStore", 3)) Next();
		if (Op() && NotSigned("reg4_notByGREEN102_upperStore", 4)) Next();
		if (Op()) { PoseF(mo, 4560, 4704, 0); Next(); }
		if (Op() && Stand(mo, 70)) Next();
		if (Op() && NotSigned("reg3_notByGREEN102_corridorBySideRoom", 3)) Next();
		if (Op() && NotSigned("reg4_notByGREEN102_corridorBySideRoom", 4)) Next();
		// ... and the other way, as the third patch was found: the pass stamped, in by GREEN's far side, out of 102
		if (Op() && DeskAt(mo, "desk3_resetsBeforeTheOtherWay", 3)) Next();
		if (Op() && Through(mo, "greenFarSide_into102", FARS + 3, 1)) Next();
		if (Op()) { Check("green102_outOnTheDais", abs(mo.pos.z - 112) < 0.001 && TIs(0, 0, 224, -112), String.Format("player %s, %s", PStr(mo.pos), TStr())); Next(); }
		if (Op()) { PoseF(mo, 4560, 4704, 0); Next(); }
		if (Op() && Stand(mo, 70)) Next();
		if (Op() && NotSigned("reg3_notByGREEN102_backways_corridorBySideRoom", 3)) Next();
		if (Op() && NotSigned("reg4_notByGREEN102_backways_corridorBySideRoom", 4)) Next();
		// the balcony's door (register 4's): shut before register 4 is signed, a walk at it stops in the corridor ...
		if (Op() && Forward(mo, 3406, 18)) Next();
		if (Op() && Stand(mo, 10)) Next();
		if (Op())
		{
			Check("balconyDoor_shutBeforeRegister4", !Reg(4).signed && Inside(mo.pos, 4700, 4640, 4864, 4832) && abs(mo.pos.z - 256) < 0.001, PStr(mo.pos));
			Next();
		}
		// ... and open after: register 4 by its answer (BLUE in 104, up the grand stair), then the walk drops into the court
		if (Op() && DeskAt(mo, "desk3_resetsForRegister4", 3)) Next();
		if (Op() && TakeDoor(mo, h.DoorOf(2))) Next();
		if (Op() && Stand(mo, 6)) Next();
		if (Op() && PoseAt(mo, FRONT + 104)) Next();
		if (Op() && HangIn(mo, "blueHungIn104", 104)) Next();
		if (Op() && Through(mo, "blue104_cross", FRONT + 104, 1)) Next();
		if (Op() && WalkTo(mo, "reg4_upTheGrandStair", 1888, 4512)) Next();
		if (Op() && WaitSigned("reg4_signedByBLUE", 4)) Next();
		if (Op() && DoorUp("reg4_gardenNoSizeAndBalconyOpen", 1904, 3)) Next();
		if (Op() && Forward(mo, 3406, 18)) Next();
		if (Op() && Stand(mo, 30)) Next();
		if (Op()) { Check("balconyDoor_openAfterRegister4", Inside(mo.pos, 4928, 3712, 6848, 5568) && mo.pos.z == 0, PStr(mo.pos)); Next(); }
	}

	// --- MODE=3: the building's own ---------------------------------------------------------
	int goTics, comeTics;
	void Building(Actor mo)
	{
		AjarDoor red = h.DoorOf(1);
		// the covered way: going north it is the stretch, 768 more; the double goes up the real one
		if (Op() && Through(mo, "coveredWay_north", 3301, 2, 1, 150))
		{
			goTics = opT;
			Next();
		}
		if (Op())
		{
			Check("coveredWay_theDoubleAheadInTheLobby", Inside(dbl.pos, 640, 2560, 1408, 3200) && dbl.pos.y - mo.pos.y > 700 && TIs(0, 0, 784, 0),
				String.Format("player %s, double %s, %s", PStr(mo.pos), PStr(dbl.pos), TStr()));
			Next();
		}
		if (Op() && WalkTo(mo, "coveredWay_toTheLodgeAnswer", 992, 2288)) Next();
		if (Op() && WaitSigned("reg8_lodgeSigned", 8)) Next();
		if (Op() && DoorUp("reg8_lodgeOpen", 1908, 1)) Next();
		if (Op() && WalkTo(mo, "coveredWay_south", 992, 2192)) { comeTics = opT; Next(); }
		if (Op())
		{
			Check("coveredWay_longerGoingThanComing", goTics > comeTics + 40, String.Format("north %d tics (from y 2192 into the lobby's end of it), south %d tics (y 2288 to 2192)", goTics, comeTics));
			Next();
		}
		if (Op() && DeskAt(mo, "desk2_putsItBack", 2)) Next();
		// the porter's lodge: in by its door, onto its plate (a secret)
		if (Op()) { PoseF(mo, 992, 3184, 270); Next(); }
		if (Op() && WalkTo(mo, "lodge_walkIn", 992, 3072)) Next();
		if (Op() && Stand(mo, 3)) Next();
		if (Op()) { Check("lodge_secretFound", level.found_secrets == 1, String.Format("%d of %d", level.found_secrets, level.total_secrets)); Next(); }
		// the boat store, bigger inside: the double walks out of the little one's back wall onto the island
		if (Op() && Through(mo, "boatStore_intoTheBigStore", 3305, 1)) Next();
		if (Op()) { Check("boatStore_inTheBigStore", Inside(mo.pos, 4032, 2240, 5056, 2496), PStr(mo.pos)); Next(); }
		if (Op() && WalkTo(mo, "boatStore_toItsFarEnd", 5008, 2368)) Next();
		if (Op()) { Check("boatStore_theDoubleOnTheIsland", Inside(dbl.pos, 5824, 4736, 6144, 5056) && abs(dbl.pos.z) < 0.001, PStr(dbl.pos)); Next(); }
		if (Op() && WaitSigned("reg9_islandSigned", 9)) Next();
		if (Op())
		{
			let it = level.CreateSectorTagIterator(1909);
			int i = it.Next();
			let li = level.CreateLineIdIterator(1909);
			int j = li.Next();
			if (i < 0 || j < 0) { Check("footbridgeUp", false, "no footbridge or no railing"); Next(); return; }
			Sector s = level.sectors[i];
			Line l = level.lines[j];
			double fz = s.floorplane.ZatPoint(s.centerspot);
			if (fz < 0 && opT < 70) return;
			bool open = !(l.flags & Line.ML_BLOCKING);
			Check("footbridgeUp", fz == 0 && open, String.Format("its floor %.1f after %d tics; the railing %s", fz, opT, open ? "gone" : "still there"));
			Next();
		}
		if (Op() && Through(mo, "boatStore_backOut", 3307, 1)) Next();
		if (Op()) { Check("boatStore_backOutUndoesIt", dbl.IsIdentity() && Inside(mo.pos, 4928, 3712, 6848, 5568), String.Format("%s, player %s", TStr(), PStr(mo.pos))); Next(); }
		if (Op()) { PoseF(mo, 5984, 4180, 90); Next(); }
		if (Op() && WalkTo(mo, "footbridge_ontoTheIsland", 5984, 4896)) Next();
		if (Op() && Stand(mo, 3)) Next();
		if (Op())
		{
			Check("island_reachedOnFoot", Inside(mo.pos, 5824, 4736, 6144, 5056) && mo.pos.z == 0 && level.found_secrets == 2,
				String.Format("player %s, secrets %d of %d", PStr(mo.pos), level.found_secrets, level.total_secrets));
			Next();
		}
		// the gazebo: each wall of the hall with no size is one of its faces, and back
		for (int n = 1; n <= 4; n++)
		{
			if (Op() && Through(mo, String.Format("gazebo%d_outOfTheHallWithNoSize", n), 3310 + n, 1)) Next();
			if (Op())
			{
				Check(String.Format("gazebo%d_inTheGarden", n), mo.pos.z == 0 && (mo.pos.xy - (4320, 1056)).Length() < 220 && Inside(mo.pos, 1536, 64, 5696, 2176), PStr(mo.pos));
				Next();
			}
			if (Op() && Through(mo, String.Format("gazebo%d_intoItsFace", n), 3320 + n, 1)) Next();
			if (Op()) { Check(String.Format("gazebo%d_inTheHallWithNoSize", n), mo.pos.z == 256 && Inside(mo.pos, 2432, 4160, 2816, 4544), PStr(mo.pos)); Next(); }
		}
		// the pass desks
		if (Op() && DeskAt(mo, "desk4_resetsAfterTheGazebo", 4)) Next();
		for (int n = 1; n <= 3; n++)
		{
			if (Op()) { dbl.tOff = (96, 0); Info("T set by the script, to try the desk"); Next(); }
			if (Op() && DeskAt(mo, String.Format("desk%d_resets", n), n)) Next();
		}
		// the courts: in by the squeeze with empty hands, not with a door; out by the turnstile with one, not back
		if (Op() && Forward(mo, 3401, 12)) Next();
		if (Op()) { Check("eastYard_inBySqueezeEmptyHanded", Inside(mo.pos, 6912, 2752, 7872, 3712), PStr(mo.pos)); Next(); }
		if (Op() && TakeDoor(mo, red)) Next();
		if (Op() && Forward(mo, 3401, 12)) Next();
		if (Op()) { Check("eastYard_notBySqueezeWithADoor", Inside(mo.pos, 3776, 3456, 6860, 3648), PStr(mo.pos)); Next(); }
		if (Op() && Forward(mo, 3402, 12)) Next();
		if (Op() && Stand(mo, 10)) Next();
		if (Op()) { Check("eastYard_outByTurnstileWithADoor", Inside(mo.pos, 3776, 3456, 6848, 3648) && mo.pos.z == 0 && h.carried == red, PStr(mo.pos)); Next(); }
		if (Op() && Forward(mo, 3407, 12)) Next();
		if (Op()) { Check("eastYard_notBackByTurnstile", Inside(mo.pos, 3776, 3456, 6850, 3648), PStr(mo.pos)); Next(); }
		if (Op()) { h.BeltPutBack(red); Next(); }
		if (Op() && Forward(mo, 3403, 12)) Next();
		if (Op()) { Check("towerYard_inBySqueezeEmptyHanded", Inside(mo.pos, 5760, 64, 7168, 1728), PStr(mo.pos)); Next(); }
		if (Op() && TakeDoor(mo, red)) Next();
		if (Op() && Forward(mo, 3403, 12)) Next();
		if (Op()) { Check("towerYard_notBySqueezeWithADoor", Inside(mo.pos, 1536, 64, 5708, 2176), PStr(mo.pos)); Next(); }
		if (Op() && Forward(mo, 3404, 12)) Next();
		if (Op() && Stand(mo, 10)) Next();
		if (Op()) { Check("towerYard_outByTurnstileWithADoor", Inside(mo.pos, 1536, 64, 5696, 2176) && mo.pos.z == 0 && h.carried == red, PStr(mo.pos)); Next(); }
		if (Op() && Forward(mo, 3408, 12)) Next();
		if (Op()) { Check("towerYard_notBackByTurnstile", Inside(mo.pos, 1536, 64, 5698, 2176), PStr(mo.pos)); Next(); }
		// the balcony's door is register 4's (2026-11-24), not signed in this run: opened by the script
		if (Op()) { level.ExecuteSpecial(11 /* Door_Open */, null, null, false, 1904, 64); Next(); }
		if (Op() && DoorUp("balconyDoor_openedByTheScript", 1904, 3)) Next();
		if (Op() && Forward(mo, 3406, 18)) Next();
		if (Op() && Stand(mo, 30)) Next();
		if (Op()) { Check("pondCourt_inByTheDropWithADoor", Inside(mo.pos, 4928, 3712, 6848, 5568) && mo.pos.z == 0 && h.carried == red, PStr(mo.pos)); Next(); }
		if (Op() && Forward(mo, 3405, 12)) Next();
		if (Op() && Stand(mo, 10)) Next();
		if (Op()) { Check("pondCourt_outByTurnstileWithADoor", Inside(mo.pos, 3776, 3456, 6848, 3648) && mo.pos.z == 0 && h.carried == red, PStr(mo.pos)); Next(); }
		if (Op())
		{
			Check("bothSecrets", level.found_secrets == 2 && level.total_secrets == 2, String.Format("%d of %d", level.found_secrets, level.total_secrets));
			Next();
		}
	}

	// --- MODE=4: views (tools/smoke_MAP19_4.cfg shoots at 78 + 80 n) ---------------------------
	int vc0;
	void Stride(Actor mo, int st, int at, int n)
	{
		if (st > at && st <= at + n) mo.vel.xy = Actor.AngleToVector(mo.angle, RUN);
		if (st == at + n + 1) mo.vel.xy = (0, 0);
	}
	// from MapSpot tid, forward until `want` crossings and `more` tics
	void ViewCross(Actor mo, int st, int at, int tid, int want, int more = 3)
	{
		if (st == at) { PoseAt(mo, tid); vc0 = dbl.crossings; crossAt = -1; }
		if (st <= at || st >= 70 || crossAt == -2) return;
		if (dbl.crossings - vc0 >= want && crossAt < 0) crossAt = st;
		if (crossAt >= 0 && st - crossAt >= more) { mo.vel.xy = (0, 0); crossAt = -2; return; }
		mo.vel.xy = Actor.AngleToVector(mo.angle, RUN);
	}
	void Look(Actor mo, int st, double x, double y, double ang, double pitch = 0)
	{
		if (st >= 70) { PoseF(mo, x, y, ang); mo.pitch = pitch; }
	}
	void Hang(Actor mo, AjarDoor d, int frame)
	{
		if (d.frame && d.frame.args[0] == frame) return;
		TakeDoor(mo, d);
		h.UseFrame(h.FindFrame(frame), mo);
		if (h.carried) h.BeltPutBack(h.carried);
	}

	void Views(Actor mo)
	{
		int i = (tic - 3) / 80, st = (tic - 3) % 80;
		if (tic == 3) mo.GiveInventoryType("Allmap");
		if (st == 0) { dbl.Reset(); dbl.Posed(mo); Console.Printf("AJARTEST view=%d t=%d", i, tic); }
		if (st == 79) Info(String.Format("view %d: player %s, double %s, %s", i, PStr(mo.pos), PStr(dbl.pos), TStr()));
		switch (i)
		{
		case 0:     // the start: the pass hall, its west brass frame (the street doors behind)
			Look(mo, st, 1200, 300, 158);
			break;
		case 1:     // ... and its east brass frame
			Look(mo, st, 600, 300, 22);
			break;
		case 2:     // the forecourt, RED by 101: the duty room's glass, the double inside on the plate
			if (st == 1) Hang(mo, h.DoorOf(1), 101);
			ViewCross(mo, st, 2, FRONT + 101, 1);
			Look(mo, st, 1104, 1408, 185);
			break;
		case 3:     // just out of the covered way: the double ahead, at the porter's lodge
			ViewCross(mo, st, 2, 3301, 2);
			Look(mo, st, 992, 2288, 90);
			break;
		case 4:     // the reading corridor, GREEN by 102: the stack and the double behind glass, 112 up (looking up)
			if (st == 1) Hang(mo, h.DoorOf(3), 102);
			ViewCross(mo, st, 2, FRONT + 102, 1);
			Look(mo, st, 2400, 2970, 300, -14);
			break;
		case 5:     // the link hall after two laps: the double down the sealed gallery, through the glass
			if (st == 1) { Hang(mo, h.LabLeaf(8, 0), 105); Hang(mo, h.LabLeaf(8, 1), 106); }
			if (st == 2) { PoseF(mo, 3328, 3296, 0); vc0 = dbl.crossings; }
			if (st > 2 && st < 70 && dbl.crossings - vc0 < 2) mo.vel.xy = (RUN, 0);
			else if (st > 2 && st < 70) mo.vel.xy = (0, 0);
			Look(mo, st, 3540, 3230, 0);
			break;
		case 6:     // the grand stair, BLUE by 104: the double climbs the air beside it
			if (st == 1) Hang(mo, h.DoorOf(2), 104);
			ViewCross(mo, st, 2, FRONT + 104, 1);
			Look(mo, st, 1840, 4200, 20);
			break;
		case 7:     // the water tower after one lap, at the foot looking at 107 and the glass: what the player sees
			if (st == 1) { Hang(mo, h.LabLeaf(9, 0), 107); Hang(mo, h.LabLeaf(9, 1), 108); }
			if (st == 2) { PoseF(mo, 6368, 512, 90); vc0 = dbl.crossings; }
			if (st > 2 && st < 70 && dbl.crossings - vc0 < 1) mo.vel.xy = (0, RUN);
			else if (st > 2 && st < 70) mo.vel.xy = (0, 0);
			Look(mo, st, 6368, 900, 90, 10);
			break;
		case 8:     // ... and from the head, down the flight in line with the glass beside 107
			if (st == 2) { PoseF(mo, 6368, 512, 90); vc0 = dbl.crossings; }
			if (st > 2 && st < 70 && dbl.crossings - vc0 < 1) mo.vel.xy = (0, RUN);
			else if (st > 2 && st < 70) mo.vel.xy = (0, 0);
			Look(mo, st, 6296, 500, 90, 8);
			break;
		case 9:     // the pond court from the balcony
			Look(mo, st, 5000, 4736, 0, 12);
			break;
		case 10:    // the garden: the avenue between its two arches
			Look(mo, st, 2752, 640, 90);
			break;
		case 11:    // the garden: the gazebo
			Look(mo, st, 4320, 700, 90);
			break;
		case 12:    // the east yard, GREEN hung in 112
			Look(mo, st, 7000, 2850, 40);
			break;
		case 13:    // the tower yard: the water tower and its strongroom
			Look(mo, st, 5900, 300, 30);
			break;
		case 14:    // the upper floor's corridor
			Look(mo, st, 1700, 4736, 0);
			break;
		case 15:    // the basement: the long cellar
			Look(mo, st, 800, 5250, 0);
			break;
		case 16:    // the upper corridor's east end: the balcony's door (register 4's) and its plaque
			Look(mo, st, 4560, 4704, 20);
			break;
		case 17:    // the automap (the cfg opens it), after RED by 101: the double's mark
			if (st == 1) Hang(mo, h.DoorOf(1), 101);
			ViewCross(mo, st, 2, FRONT + 101, 1);
			Look(mo, st, 1104, 1408, 185);
			break;
		}
		if (tic == 3 + 80 * 18) Console.Printf("AJARTEST viewsDone=1");
	}
}
