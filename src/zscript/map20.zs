// MAP20 "High Water" (tools/map_highwater.py; the water: water.zs): the tests.
// MAP=MAP20 MODE=n tools/smoke.sh "$PWD/build/smoke20_n" (PLAN.md, the MAP20 write-up)
//   MODE=1 (EXTRA=-nomonsters) the whole level by the answers meant, stage by stage, each
//          level at rest read against the generator's measure (its MapSpots 3101..: args[0]
//          the level x 100), to the wheel turning, the sluice open and the way out
//   MODE=2 the player in the water: floating up when idle, out onto the ledge, a dive to 113
//          with GREEN, a swim through the TEAL pipe, the lock as written, a pressure door
//          refusing, opening dry and shutting itself (on no one), the float gate
//   MODE=3 "nothing can be lost": K at 96 with BLUE taken down and the player inside; C refilled
//          with the player on the boiler house's side; the lower yard with K full; the gates
//   MODE=4 a tour of fixed views (tools/smoke_MAP20_4.cfg shoots at 78 + 80 n)
//   MODE=5 the fights' causes: each water ambush once and when it should; the cells; drowning
//   MODE=6 (EXTRA=-nomonsters) the secret way out: BLUE in 142, the swim to the fourth pane and through
//          it into the left-handed bath, its water at the bath's level every tic, the way back, a mirror
//          pane is a wall, shots through the opening and at a mirror, the bath drained behind the player,
//          the copy's door, the secret, the Exit_Secret line (PLAN.md, "MAP20: the secret way out, built")
//   MODE=7 views of the pane wall for tools/highwater_compare.py (tools/smoke_MAP20_7.cfg shoots at
//          78 + 80 n), as built and with AJAR_SBMIRROR=1 (the fourth pane a mirror); the notch views
class HighWaterTest : EventHandler
{
	const TP = 21; const TC = 22; const TT = 23; const TK = 24; const TL = 25; const TU = 26; const TSB = 27;
	const PD_P = 41; const PD_E2 = 42; const PD_CA = 43; const PD_CB = 44; const PD_T = 45; const PD_K = 46;
	const GD_TAG = 61; const GW_TAG = 62; const LEDGE_TAG = 63; const YARD_TAG = 64; const SLUICE = 65;
	const FRONT = 1000;         // + frame number: before the frame, facing it (map_highwater.test_spot)
	const EXPECT = 3100;        // + n: the measure's levels at rest (map_highwater.EXPECT)
	const E_P102 = 1; const E_C112 = 2; const E_C113 = 3; const E_PIPE = 4; const E_K131 = 5; const E_K133 = 6;
	const E_L109 = 7; const E_CIRCLE = 8; const E_P101 = 9; const E_T121 = 10; const E_PIPE_NOBLUE = 11;
	const E_SB142 = 12; const E_SB141 = 13;
	const TSBL = 30;            // the left-handed bath (a FOLLOW basin: the swimming bath's level)
	const PANE4 = 1440; const PANE4_FAR = 1441;     // the fourth pane's portal line, and its image in the copy
	const CX = -1664; const CY = -2048;                 // a point (x, y) of the bath is (CX - x, y + CY) in the copy
	const GLASS = -848;
	const WALKKEY = 0x1900;
	const RUNKEY = 0x3200;
	const RUN = 16.7;

	int tic, checks, fails;
	int pc, k, opT, lastPc;
	bool stepped, finished;
	AjarHandler h;
	AjarWaterHandler wh;
	int fwd, side, up, btn;     // keys "held" this tic (Drive)
	Array<int> ambKey, ambAt;   // the water ambushes: cause * 65536 + args[4], and how many there were at the start

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP20"; }

	bool Op() { bool me = k == pc && !stepped; k++; return me; }
	void Next() { pc++; stepped = true; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info t=%d %s", tic, s); }
	string PStr(Vector3 p) { return String.Format("(%.1f,%.1f,%.1f)", p.x, p.y, p.z); }

	Actor Spot(int tid) { return level.CreateActorIterator(tid).Next(); }
	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }
	AjarBasin B(int tag) { return wh.BasinOfTag(tag); }
	double W(int tag) { let b = B(tag); return b ? b.w : -9999; }
	double Measured(int n) { let s = Spot(EXPECT + n); return s ? s.args[0] / 100. : -9999; }
	string Levels()
	{
		return String.Format("P %.2f C %.2f T %.2f K %.2f L %.2f U %.2f SB %.2f", W(TP), W(TC), W(TT), W(TK), W(TL), W(TU), W(TSB));
	}

	void PoseF(Actor mo, double x, double y, double ang, double z = -1e9)
	{
		mo.SetOrigin((x, y, z > -1e8 ? z : FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
	}
	bool PoseAt(Actor mo, int tid, double z = -1e9)
	{
		Actor s = Spot(tid);
		if (!s) { Check(String.Format("spot%d", tid), false, "no such MapSpot"); return true; }
		PoseF(mo, s.pos.x, s.pos.y, s.angle, z);
		return true;
	}
	bool Stand(Actor mo, int n) { mo.vel.xy = (0, 0); return opT >= n; }

	// keys held: the engine's own movement for the tic once more (as watertest.zs)
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp || !(fwd || side || up || btn)) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.sidemove = side;
		pp.player.cmd.upmove = up;
		pp.player.cmd.buttons = btn;
		pp.HandleMovement();
		wh.keysUntil = level.maptime + 1;
	}
	void Keys(int f = 0, int b = 0) { fwd = f; btn = b; }
	string Carrying() { return h.carried ? h.carried.Label() : "-"; }

	// --- doors ------------------------------------------------------------------------------
	AjarDoor Blue() { return h.DoorOf(2); }
	AjarDoor Green() { return h.DoorOf(3); }
	AjarDoor Leaf(int n) { return h.LabLeaf(8, n); }
	bool TakeDoor(Actor mo, AjarDoor d)
	{
		if (h.carried && h.carried != d) h.BeltPutBack(h.carried);
		if (h.carried == d) return true;
		if (d.frame) h.UseFrame(d.frame, mo);
		else h.TakeLeaning(d, mo);
		return true;
	}
	// hang d in the frame (a door already there comes down and goes back where it leant)
	bool Hang(Actor mo, string name, AjarDoor d, int frame)
	{
		TakeDoor(mo, d);
		AjarFrame f = h.FindFrame(frame);
		if (!h.carried || !f) { Check(name, false, "nothing carried, or no frame"); return true; }
		h.UseFrame(f, mo);
		Check(name, f.door == d, String.Format("said \"%s\"", h.said));
		if (h.carried) h.BeltPutBack(h.carried);
		return true;
	}
	// take a door down (and put it back where it leant, unless `keep`)
	bool TakeDown(Actor mo, string name, AjarDoor d, bool keep = false)
	{
		TakeDoor(mo, d);
		bool ok = h.carried == d && !d.frame;
		if (!keep && h.carried) h.BeltPutBack(h.carried);
		Check(name, ok, Levels());
		return true;
	}

	// --- water at rest -------------------------------------------------------------------------
	double lastW;
	int steadyT, nearAt;
	// waits until basin `tag` is at rest (or `limit` tics), then checks it against `expect`
	bool Rest(string name, int tag, double expect, int limit = 2100, double tol = 0.5)
	{
		double w = W(tag);
		if (opT == 0) { steadyT = 0; nearAt = -1; lastW = w; }
		if (nearAt < 0 && abs(w - expect) < 1) nearAt = opT;
		steadyT = abs(w - lastW) < 0.0005 ? steadyT + 1 : 0;
		lastW = w;
		if (opT % 175 == 0) Info(String.Format("%s t+%.0fs: %s", name, opT / 35., Levels()));
		if ((steadyT < 35 || opT < 40) && opT < limit) return false;
		Check(name, abs(w - expect) < tol, String.Format("the measure %.2f, here %.3f; within 1 of it after %.1f s, at rest after %.1f s",
			expect, w, nearAt < 0 ? -1 : nearAt / 35., (opT - steadyT) / 35.));
		return true;
	}

	// --- pressure doors, gates ----------------------------------------------------------------
	AjarPressureDoor PD(int tag)
	{
		for (int i = 0; i < wh.pdoors.Size(); i++) if (wh.pdoors[i].args[0] == tag) return wh.pdoors[i];
		return null;
	}
	Sector SectorOf(int tag)
	{
		int i = level.CreateSectorTagIterator(tag).Next();
		if (i < 0) return null;
		return level.sectors[i];
	}
	double Opening(int tag)
	{
		let s = SectorOf(tag);
		return s ? s.ceilingplane.ZatPoint(s.centerspot) - s.floorplane.ZatPoint(s.centerspot) : -1;
	}
	// USE, by the player, on the first line of sector `tag` that has a special
	bool UseLineOf(Actor mo, int tag)
	{
		let s = SectorOf(tag);
		if (!s) return false;
		for (int i = 0; i < s.lines.Size(); i++)
			if (s.lines[i].special) { s.lines[i].Activate(mo, 0, SPAC_Use); return true; }
		return false;
	}
	bool UsePD(Actor mo, string name, int tag, bool expectOpen)
	{
		let pd = PD(tag);
		if (!pd) { Check(name, false, "no such pressure door"); return true; }
		int ref = pd.refused;
		h.said = "";
		UseLineOf(mo, tag);
		bool opened = pd.open;
		Check(name, opened == expectOpen && (expectOpen || pd.refused > ref),
			String.Format("open %d, refused %d; water at its sill %.1f / %.1f; said \"%s\"", opened, pd.refused - ref, pd.WaterAt(0), pd.WaterAt(1), h.said));
		return true;
	}
	bool DoorState(string name, int tag, bool wantOpen, int limit = 105)
	{
		double o = Opening(tag);
		bool ok = wantOpen ? o >= 56 : o <= 0.01;
		if (!ok && opT < limit) return false;
		Check(name, ok, String.Format("opening %.1f after %d tics", o, opT));
		let pd = PD(tag);
		if (pd && !ok) Info(String.Format("%s: open %d, held %d, auto %d, waited %d tics, top %.1f, sill %.1f", name, pd.open, pd.held, pd.autoDone, pd.shutWaits, pd.Top(), pd.sill));
		return true;
	}

	// --- ambushes ---------------------------------------------------------------------------------
	int AmbushLeft(int cause, int arg = -1)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == cause && (arg < 0 || a.args[4] == arg)) n++;
		return n;
	}
	static int Key(int tag, int height) { return tag * 1024 + height + 512; }
	int At(int cause, int arg) { int i = ambKey.Find(cause * 65536 + arg); return i < ambKey.Size() ? ambAt[i] : 0; }

	void ClearOut()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
	}

	void Summary()
	{
		if (finished) return;
		finished = true;
		Console.Printf("AJARTEST highWaterDone=1 checks=%d failed=%d", checks, fails);
	}

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		if (!wh) wh = AjarWaterHandler.Get();
		if (!wh || !wh.ready) return;
		tic++;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (tic == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			lastPc = -1;
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			if (mode != 5) ClearOut();
			let it = ThinkerIterator.Create("AjarAmbush");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (a.args[0] != 60 && a.args[0] != 61) continue;
				int key = a.args[0] * 65536 + a.args[4];
				int i = ambKey.Find(key);
				if (i == ambKey.Size()) { ambKey.Push(key); ambAt.Push(0); }
				ambAt[i]++;
			}
		}
		if (tic < 3) return;
		if (pc != lastPc) { lastPc = pc; opT = 0; }
		else opT++;
		k = 0;
		stepped = false;
		fwd = side = up = btn = 0;
		if (mode == 1) Whole(mo);
		else if (mode == 2) Swimmer(mo);
		else if (mode == 3) Lost(mo);
		else if (mode == 4) Views(mo);
		else if (mode == 5) Fights(mo);
		else if (mode == 6) Secret(mo);
		else if (mode == 7) PaneViews(mo);
		Drive(mo);
		if (mode != 4 && mode != 7 && pc >= k) Summary();
	}

	// the exit lines crossed (MODE=6: the level ends by the secret way, not the plain one)
	Vector3 lastPos;
	bool testing6;
	override void WorldUnloaded(WorldEvent e)
	{
		if (!testing6) return;
		// the Exit_Secret line is at y 792 of the bath in the copy; the plain way out is far east (x 6048)
		bool bySecret = InCopy(lastPos.xy) && lastPos.y > 792 + CY - 24;
		Check("exitBySecretWayOut", bySecret && e.NextMap ~== level.NextSecretMap,
			String.Format("last seen at %s; next map %s (secretnext %s, next %s)", PStr(lastPos), e.NextMap, level.NextSecretMap, level.NextMap));
		Check("copyKeptAtTheBathsLevelEveryTic", maxDev < 1e-9, String.Format("the most it was off: %.9f", maxDev));
		Check("secretFound", level.found_secrets == 1 && level.total_secrets == 1, String.Format("%d of %d", level.found_secrets, level.total_secrets));
		finished = false;
		Summary();
	}

	// --- MODE=1: the whole level by the answers meant ------------------------------------------
	void Whole(Actor mo)
	{
		AjarDoor blue = Blue(), green = Green(), tealA = Leaf(0), tealB = Leaf(1);
		if (Op())
		{
			Check("rate", wh.kFlow == 1000 && wh.freeFall == 6 && wh.bFloat && wh.bOverflow && wh.wheelTics == 192,
				String.Format("K %.0f, FREE %.0f, float %d, overflow %d, wheel %d tics", wh.kFlow, wh.freeFall, wh.bFloat, wh.bOverflow, wh.wheelTics));
			Check("asFound", W(TP) == 0 && W(TC) == 96 && W(TT) == 0 && W(TK) == 0 && W(TL) == -96 && W(TU) == 128 && W(TSB) == -160, Levels());
			Check("measureCarried", Measured(E_P102) > 200, String.Format("P with BLUE in 102: %.2f", Measured(E_P102)));
			Next();
		}
		// 1. the baths: P's door opens dry; BLUE in 101: 96, the ledge not reached; in 102: 224
		if (Op() && UsePD(mo, "plungeDoorOpensDry", PD_P, true)) Next();
		if (Op() && DoorState("plungeDoorOpen", PD_P, true)) Next();
		if (Op() && PoseAt(mo, FRONT + 101)) Next();
		if (Op() && Hang(mo, "blueIn101", blue, 101)) Next();
		if (Op() && Rest("P_blue101", TP, Measured(E_P101))) Next();
		if (Op())
		{
			Check("ledgeNotReachedAt96", W(TP) < 232 - 24, Levels());
			Next();
		}
		if (Op() && DoorState("plungeDoorShutItself", PD_P, false)) Next();
		if (Op() && PoseAt(mo, FRONT + 102)) Next();
		if (Op() && Hang(mo, "blueIn102", blue, 102)) Next();
		if (Op() && Rest("P_blue102", TP, Measured(E_P102))) Next();
		if (Op())
		{
			Check("ledgeReached", W(TP) >= 232 - 24, Levels());
			Next();
		}
		// out by the ledge door; the first steps beyond draw the gallery's bolt
		if (Op() && PoseAt(mo, 2011)) Next();
		if (Op())
		{
			UseLineOf(mo, LEDGE_TAG);
			Next();
		}
		if (Op() && DoorState("ledgeDoorOpens", LEDGE_TAG, true)) Next();
		if (Op())
		{
			PoseF(mo, 1150, 224, 0);
			Next();
		}
		if (Op()) { Keys(WALKKEY); if (opT >= 25) Next(); }
		if (Op() && DoorState("galleryBoltDrawn", GD_TAG, true)) Next();
		// 2. the pump house and the cooling hall: GREEN in 111, 112, 113
		if (Op() && PoseAt(mo, FRONT + 111)) Next();
		if (Op() && Hang(mo, "greenIn111", green, 111)) Next();
		if (Op() && Stand(mo, 140)) Next();
		if (Op())
		{
			Check("C_green111_nothing", abs(W(TC) - 96) < 0.01, Levels());
			Next();
		}
		if (Op() && PoseAt(mo, FRONT + 112)) Next();
		if (Op() && Hang(mo, "greenIn112", green, 112)) Next();
		if (Op() && Rest("C_green112", TC, Measured(E_C112))) Next();
		if (Op())
		{
			Check("E2heldAt0", PD(PD_E2).held && PD(PD_CA).held, String.Format("water at E2's sill %.1f", PD(PD_E2).WaterAt(0)));
			Next();
		}
		if (Op() && PoseAt(mo, FRONT + 113)) Next();
		if (Op() && Hang(mo, "greenIn113", green, 113)) Next();
		if (Op() && Rest("C_green113", TC, Measured(E_C113))) Next();
		if (Op() && DoorState("cellAOpensItself", PD_CA, true)) Next();
		if (Op() && DoorState("cellBOpensItself", PD_CB, true)) Next();
		if (Op() && UsePD(mo, "E2opensDry", PD_E2, true)) Next();
		if (Op() && DoorState("E2open", PD_E2, true)) Next();
		// the gangway's bolt, from the boiler house's side
		if (Op())
		{
			PoseF(mo, 3400, 416, 180);
			UseLineOf(mo, GW_TAG);
			Next();
		}
		if (Op() && DoorState("gangwayBoltDrawn", GW_TAG, true)) Next();
		// 3. the pipe: a leaf in 113, its twin in 121, BLUE in 111: C at its brim, T at 228, the float
		if (Op() && TakeDown(mo, "greenOutOf113", green)) Next();
		if (Op() && UsePD(mo, "manholeOpensDry", PD_T, true)) Next();
		if (Op() && Hang(mo, "tealIn113", tealA, 113)) Next();
		if (Op() && PoseAt(mo, FRONT + 121)) Next();
		if (Op() && Hang(mo, "tealIn121", tealB, 121)) Next();
		if (Op())
		{
			PoseF(mo, 4000, 200, 0);
			Next();
		}
		if (Op() && Hang(mo, "blueIn111", blue, 111)) Next();
		if (Op() && Rest("T_pipe", TT, Measured(E_PIPE))) Next();
		if (Op())
		{
			Check("C_atItsBrim", abs(W(TC) - 100) < 0.5, Levels());
			Check("E2shutItself", PD(PD_E2).held && Opening(PD_E2) <= 0.01, String.Format("opening %.1f", Opening(PD_E2)));
			Check("manholeShutItself", Opening(PD_T) <= 0.01, String.Format("opening %.1f", Opening(PD_T)));
			Next();
		}
		if (Op() && DoorState("yardGateRaised", YARD_TAG, true, 140)) Next();
		// 4. the yards: BLUE in 109 fills L; a leaf to 135 (alone: its twin still leans); BLUE in 131, then 133
		if (Op() && TakeDown(mo, "blueOutOf111", blue)) Next();
		if (Op() && TakeDown(mo, "leafOutOf121", tealB)) Next();
		if (Op() && TakeDown(mo, "leafOutOf113", tealA)) Next();
		if (Op() && PoseAt(mo, FRONT + 109)) Next();
		if (Op() && Hang(mo, "blueIn109", blue, 109)) Next();
		if (Op() && Rest("L_blue109", TL, Measured(E_L109))) Next();
		if (Op() && TakeDown(mo, "blueOutOf109", blue)) Next();
		if (Op() && Stand(mo, 70)) Next();
		if (Op())
		{
			Check("L_staysFull", abs(W(TL) - Measured(E_L109)) < 0.5, Levels());
			Next();
		}
		if (Op() && PoseAt(mo, 2015)) Next();
		if (Op() && UsePD(mo, "lockDoorOpensDry", PD_K, true)) Next();
		if (Op() && DoorState("lockDoorOpen", PD_K, true)) Next();
		if (Op() && PoseAt(mo, FRONT + 135)) Next();
		if (Op() && Hang(mo, "leafIn135_lockDry", tealB, 135)) Next();
		if (Op() && PoseAt(mo, FRONT + 131)) Next();
		if (Op() && Hang(mo, "blueIn131", blue, 131)) Next();
		if (Op() && Rest("K_blue131", TK, Measured(E_K131))) Next();
		if (Op())
		{
			Check("lockDoorShutItself", Opening(PD_K) <= 0.01, String.Format("opening %.1f", Opening(PD_K)));
			Check("shelfInReach", W(TK) >= 88 - 24, Levels());
			Check("sillNotInReach", W(TK) < 192 - 24, Levels());
			Next();
		}
		if (Op() && PoseAt(mo, FRONT + 133)) Next();
		if (Op() && Hang(mo, "blueIn133", blue, 133)) Next();
		if (Op() && Rest("K_blue133", TK, Measured(E_K133))) Next();
		if (Op())
		{
			Check("sillInReach", W(TK) >= 192 - 24, Levels());
			Check("ambushAtTheSillDue", AjarWaterHandler.WaterDue(60, Key(TK, 150)), Levels());
			Next();
		}
		// 5. the circle: the leaf out of 135 (a dive), into 108, its twin into 107: the water goes round, the wheel turns
		if (Op() && TakeDown(mo, "leafOutOf135", tealB)) Next();
		if (Op() && PoseAt(mo, FRONT + 108)) Next();
		if (Op() && Hang(mo, "leafIn108_alone", tealB, 108)) Next();
		if (Op() && PoseAt(mo, FRONT + 107)) Next();
		if (Op() && Hang(mo, "leafIn107_circle", tealA, 107)) Next();
		if (Op())
		{
			let wr = wh.weirs[0];
			if (!wr.turning && opT < 700) return;
			Check("wheelTurns", wr.turning, String.Format("after %.1f s (the measure 6.1 s from the hanging); spill %.0f a tic; %s", opT / 35., wr.flow, Levels()));
			Next();
		}
		if (Op() && Rest("U_circle", TU, Measured(E_CIRCLE), 700)) Next();
		if (Op() && DoorState("sluiceOpen", SLUICE, true, 140)) Next();
		if (Op())
		{
			let wr = wh.weirs[0];
			Check("wheelStillTurning", wr.turning, String.Format("spill %.0f a tic", wr.flow));
			PoseF(mo, 5150, 1312, 0);
			Next();
		}
		if (Op())
		{
			if (opT == 0) Summary();
			mo.vel.xy = (RUN, 0);
			if (opT >= 120) { Check("levelExitedInTime", false, PStr(mo.pos)); Next(); }
		}
	}

	// --- MODE=2: the player in the water ----------------------------------------------------------
	double z0;
	void Swimmer(Actor mo)
	{
		AjarDoor blue = Blue(), green = Green(), tealA = Leaf(0), tealB = Leaf(1);
		// floating idle while P fills to 224, and out onto the ledge
		if (Op() && PoseAt(mo, FRONT + 101)) Next();
		if (Op() && Hang(mo, "blueIn102", blue, 102)) Next();
		if (Op())
		{
			mo.vel.xy = (0, 0);
			if (opT % 175 == 0) Info(String.Format("floating: P %.1f, player %s, waterlevel %d", W(TP), PStr(mo.pos), mo.waterlevel));
			if (W(TP) < Measured(E_P102) - 0.5 && opT < 1400) return;
			Check("floatsUpAsPFills", mo.waterlevel < 3 && mo.pos.z > W(TP) - 56,
				String.Format("P %.1f, player %s, waterlevel %d, floated %d tics", W(TP), PStr(mo.pos), mo.waterlevel, wh.floatTics));
			Check("toldToSwimUp", wh.saidSwim);
			Next();
		}
		// the float's speed: from P's floor, under 224, idle
		if (Op())
		{
			PoseF(mo, 800, 200, 0, 0);
			Next();
		}
		if (Op())
		{
			if (opT == 10) z0 = mo.pos.z;
			if (opT < 45) return;
			Check("floatSpeed", mo.pos.z - z0 > 45 && mo.pos.z - z0 < 80, String.Format("%.1f units in a second (64 asked)", mo.pos.z - z0));
			Next();
		}
		if (Op())
		{
			if (mo.waterlevel >= 3 && opT < 350) return;
			Check("headOut", mo.waterlevel < 3, String.Format("after %d tics more, player %s", opT, PStr(mo.pos)));
			Next();
		}
		// out over the coaming onto the ledge: walk, and the jump key
		if (Op())
		{
			PoseF(mo, 990, 224, 0, mo.pos.z);
			Next();
		}
		if (Op())
		{
			Keys(WALKKEY, BT_JUMP);
			if (!(mo.pos.x > 1080 && abs(mo.pos.z - 216) < 1) && opT < 140) return;
			Keys();
			Check("outOnTheLedge", mo.pos.x > 1056 && abs(mo.pos.z - 216) < 1, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		// a dive to 113, 224 under C's water, with GREEN, and GREEN hung there
		if (Op())
		{
			TakeDoor(mo, green);
			PoseF(mo, 2784, 160, 270, 96 - 40);
			mo.pitch = 80;
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (mo.pos.z > -120 && opT < 350) return;
			Keys();
			Check("diveTo113", mo.pos.z <= -120, String.Format("down to %.1f in %.1f s, carrying %s, air left %.1f s",
				mo.pos.z, opT / 35., Carrying(), (mo.player.air_finished - level.maptime) / 35.));
			Next();
		}
		if (Op())
		{
			mo.pitch = 0;
			h.UseFrame(h.FindFrame(113), mo);
			Check("greenHungIn113UnderWater", green.frame && green.frame.args[0] == 113, String.Format("said \"%s\"", h.said));
			Next();
		}
		if (Op() && Rest("C_green113_dived", TC, Measured(E_C113))) Next();
		// the TEAL pipe: a leaf in 113, its twin in 121, BLUE in 111; then swim from C through 113 into T
		if (Op() && TakeDown(mo, "greenOutOf113", green)) Next();
		if (Op() && Hang(mo, "tealIn113", tealA, 113)) Next();
		if (Op() && Hang(mo, "tealIn121", tealB, 121)) Next();
		if (Op() && Hang(mo, "blueIn111", blue, 111)) Next();
		if (Op() && Rest("T_pipe", TT, Measured(E_PIPE))) Next();
		if (Op())
		{
			PoseF(mo, 2784, 80, 270, -128);
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			bool inT = mo.pos.x > 4096 && mo.pos.x < 4352 && mo.pos.y > 512 && mo.pos.y < 768;
			if (!inT && opT < 105) return;
			Keys();
			Check("swamThroughThePipe", inT, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		// the float gate: T stood at 216 or over for 2 s
		if (Op())
		{
			let fg = wh.floats[0];
			Check("floatTripped", fg.tripped, String.Format("at %d", fg.trippedAt));
			Next();
		}
		if (Op() && DoorState("yardGateUp", YARD_TAG, true, 140)) Next();
		// the lock as written: the leaf in 135 with the lock dry, BLUE in 131, the shelf, BLUE in 133
		if (Op() && TakeDown(mo, "leafOutOf121", tealB)) Next();
		if (Op() && TakeDown(mo, "leafOutOf113", tealA)) Next();
		if (Op() && TakeDown(mo, "blueOutOf111", blue)) Next();
		if (Op() && Hang(mo, "leafIn135_lockDry", tealB, 135)) Next();
		if (Op() && PoseAt(mo, FRONT + 131)) Next();
		if (Op() && Hang(mo, "blueIn131", blue, 131)) Next();
		if (Op() && Rest("K_blue131", TK, Measured(E_K131))) Next();
		if (Op())
		{
			Check("floatedInK", mo.waterlevel < 3 && mo.pos.z > W(TK) - 56, String.Format("player %s, K %.1f", PStr(mo.pos), W(TK)));
			Next();
		}
		if (Op())        // swim to the shelf (east, at 88: 8 under the water)
		{
			mo.angle = atan2(2176 - mo.pos.y, 4192 - mo.pos.x);
			Keys(WALKKEY, BT_JUMP);
			if (!(mo.pos.x > 4170 && mo.pos.y > 2120 && abs(mo.pos.z - 88) < 2) && opT < 280) return;
			Keys();
			Check("onTheShelf", mo.pos.x > 4160 && mo.pos.y > 2112 && abs(mo.pos.z - 88) < 2, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		if (Op() && Hang(mo, "blueIn133", blue, 133)) Next();
		if (Op() && Rest("K_blue133", TK, Measured(E_K133))) Next();
		if (Op())        // out over the sill with empty hands
		{
			mo.angle = atan2(2290 - mo.pos.y, 4032 - mo.pos.x);
			Keys(WALKKEY, BT_JUMP);
			if (!(mo.pos.y > 2240 && mo.pos.z >= 191) && opT < 280) return;
			Keys();
			Check("outOverTheSill", mo.pos.y > 2240 && mo.pos.z >= 191, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		if (Op())        // dive for the leaf in 135 (at the floor, 184 under)
		{
			PoseF(mo, 4150, 2016, 0, W(TK) - 40);
			mo.pitch = 80;
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (mo.pos.z > 8 && opT < 280) return;
			Keys();
			mo.pitch = 0;
			h.UseFrame(h.FindFrame(135), mo);
			Check("leafTakenFrom135", h.carried == tealB, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		if (Op())        // and out with it over the sill
		{
			mo.angle = atan2(2290 - mo.pos.y, 4032 - mo.pos.x);
			Keys(WALKKEY, BT_JUMP);
			if (!(mo.pos.y > 2240 && mo.pos.z >= 191) && opT < 420) return;
			Keys();
			Check("outWithTheLeaf", mo.pos.y > 2240 && mo.pos.z >= 191 && h.carried == tealB, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			if (h.carried) h.BeltPutBack(h.carried);
			Next();
		}
		// a pressure door: it refuses while water holds it, opens dry, and shuts itself on no one
		if (Op() && PoseAt(mo, 2015)) Next();
		if (Op() && UsePD(mo, "lockDoorRefuses", PD_K, false)) Next();
		if (Op())
		{
			Check("refusalSaysWhy", h.said.IndexOf("water holds") >= 0, h.said);
			Next();
		}
		if (Op() && TakeDown(mo, "blueOutOf133", blue)) Next();
		if (Op() && Hang(mo, "greenIn131", green, 131)) Next();
		if (Op() && Rest("K_green131", TK, 0)) Next();
		if (Op() && UsePD(mo, "lockDoorOpensDry", PD_K, true)) Next();
		if (Op() && DoorState("lockDoorOpen", PD_K, true)) Next();
		if (Op())        // stand in the doorway, and let the water come
		{
			PoseF(mo, 4000, 1888, 90);
			Next();
		}
		if (Op() && Hang(mo, "blueIn131_again", blue, 131)) Next();
		if (Op())
		{
			mo.vel.xy = (0, 0);
			if (opT < 210) return;
			let pd = PD(PD_K);
			Check("waitsOnTheOneInTheDoorway", pd.held && Opening(PD_K) >= 56 && pd.shutWaits > 0 && mo.health > 0,
				String.Format("held %d, opening %.1f, waited %d tics, health %d; K %.1f", pd.held, Opening(PD_K), pd.shutWaits, mo.health, W(TK)));
			PoseF(mo, 4000, 1780, 270);
			Next();
		}
		if (Op() && DoorState("shutsOnceHeIsOut", PD_K, false, 140)) Next();
	}

	// --- MODE=3: nothing can be lost ---------------------------------------------------------------
	void Lost(Actor mo)
	{
		AjarDoor blue = Blue(), green = Green(), tealA = Leaf(0), tealB = Leaf(1);
		// K at 96 with BLUE taken down and the player inside: out through the squeeze and up the stair
		if (Op() && PoseAt(mo, FRONT + 131)) Next();
		if (Op() && Hang(mo, "blueIn131", blue, 131)) Next();
		if (Op() && Rest("K_blue131", TK, Measured(E_K131))) Next();
		if (Op() && TakeDown(mo, "blueTakenDown", blue, true)) Next();
		if (Op() && UsePD(mo, "lockDoorHeld", PD_K, false)) Next();
		if (Op())        // with a door: the squeeze will not let it through
		{
			PoseF(mo, 3930, 2120, 180, 0);
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (opT < 70) return;
			Keys();
			Check("squeezeStopsTheDoor", mo.pos.x > 3888, String.Format("player %s carrying %s", PStr(mo.pos), Carrying()));
			if (h.carried) h.BeltPutBack(h.carried);
			PoseF(mo, 3930, 2120, 180, 0);
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (mo.pos.x > 3866 && opT < 140) return;
			mo.angle = 90;
			if (!(mo.pos.y > 2250 && mo.pos.z >= 191) && opT < 560) return;
			Keys();
			Check("outOfKEmptyHanded", mo.pos.y > 2240 && mo.pos.z >= 191, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		// C refilled with the player on the boiler house's side: back by the gangway
		if (Op() && Hang(mo, "greenIn113", green, 113)) Next();
		if (Op() && Rest("C_drained", TC, Measured(E_C113))) Next();
		if (Op() && UsePD(mo, "E2opens", PD_E2, true)) Next();
		if (Op() && TakeDown(mo, "greenOutOf113", green)) Next();
		if (Op() && Hang(mo, "blueIn111", blue, 111)) Next();
		if (Op() && Rest("C_refilled", TC, 100)) Next();
		if (Op())
		{
			Check("E2heldByTheWater", PD(PD_E2).held && Opening(PD_E2) <= 0.01, String.Format("opening %.1f", Opening(PD_E2)));
			PoseF(mo, 3420, 416, 180);
			UseLineOf(mo, GW_TAG);
			Next();
		}
		if (Op() && DoorState("gangwayOpens", GW_TAG, true)) Next();
		if (Op())
		{
			Keys(RUNKEY);
			if (!(mo.pos.x < 3320 && mo.pos.z >= 103) && opT < 210) return;
			Keys();
			Check("backToTheWalkway", mo.pos.x < 3328 && mo.pos.z >= 103, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		// the lower yard with K full: up by the squeeze stair empty handed, not with a door; down by the terrace
		if (Op() && TakeDown(mo, "blueOutOf111", blue)) Next();
		if (Op() && Hang(mo, "blueIn133", blue, 133)) Next();
		if (Op() && Rest("K_full", TK, Measured(E_K133))) Next();
		if (Op())
		{
			PoseF(mo, 3672, 1800, 90);
			UsePD(mo, "lockDoorHeldFromTheYard", PD_K, false);
			TakeDoor(mo, green);
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (opT < 70) return;
			Keys();
			Check("squeezeStairNotWithADoor", mo.pos.y < 1860, String.Format("player %s carrying %s", PStr(mo.pos), Carrying()));
			if (h.carried) h.BeltPutBack(h.carried);
			PoseF(mo, 3672, 1800, 90);
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (!(mo.pos.y > 2300 && mo.pos.z >= 191) && opT < 280) return;
			Keys();
			Check("upTheSqueezeStair", mo.pos.y > 2300 && mo.pos.z >= 191, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			Next();
		}
		if (Op())
		{
			TakeDoor(mo, green);
			PoseF(mo, 3776, 2200, 270);
			Next();
		}
		if (Op())
		{
			Keys(RUNKEY);
			if (!(mo.pos.y < 1850 && mo.pos.z < 1) && opT < 140) return;
			Keys();
			Check("downTheTerraceWithADoor", mo.pos.y < 1856 && mo.pos.z < 1 && h.carried == green, String.Format("player %s after %d tics", PStr(mo.pos), opT));
			if (h.carried) h.BeltPutBack(h.carried);
			Next();
		}
		// the gates stay open: the ledge door, the gallery's and the gangway's bolts, the yard gate
		if (Op())
		{
			PoseAt(mo, 2011);
			UseLineOf(mo, LEDGE_TAG);
			PoseF(mo, 1150, 224, 0);
			Next();
		}
		if (Op()) { Keys(WALKKEY); if (opT >= 25) Next(); }
		if (Op() && Hang(mo, "tealIn113", tealA, 113)) Next();
		if (Op() && Hang(mo, "tealIn121", tealB, 121)) Next();
		if (Op() && TakeDown(mo, "blueOutOf133", blue)) Next();
		if (Op() && Hang(mo, "blueIn111", blue, 111)) Next();
		if (Op() && Rest("T_pipe", TT, Measured(E_PIPE))) Next();
		if (Op() && DoorState("yardGateUp", YARD_TAG, true, 140)) Next();
		if (Op() && Hang(mo, "greenIn121", green, 121)) Next();
		if (Op() && TakeDown(mo, "blueOutOf111_again", blue)) Next();
		if (Op() && Stand(mo, 700)) Next();
		if (Op())
		{
			Check("gatesStayOpen", Opening(LEDGE_TAG) >= 56 && Opening(GD_TAG) >= 56 && Opening(GW_TAG) >= 56 && Opening(YARD_TAG) >= 100,
				String.Format("ledge %.0f, gallery %.0f, gangway %.0f, yard %.0f; T %.1f", Opening(LEDGE_TAG), Opening(GD_TAG), Opening(GW_TAG), Opening(YARD_TAG), W(TT)));
			Next();
		}
	}

	// --- MODE=4: views (tools/smoke_MAP20_4.cfg shoots at 78 + 80 n) -----------------------------
	void Set(int tag, double w) { let b = B(tag); if (b) { b.w = w; b.held = true; } }
	void Free(int tag) { let b = B(tag); if (b) b.held = false; }
	void Look(Actor mo, int st, double x, double y, double ang, double pitch = 0, double z = -1e9)
	{
		if (st >= 60) { PoseF(mo, x, y, ang, z); mo.pitch = pitch; }
	}
	void HangQuiet(Actor mo, AjarDoor d, int frame)
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
		if (st == 0) Console.Printf("AJARTEST view=%d t=%d", i, tic);
		if (st == 79) Info(String.Format("view %d: player %s; %s", i, PStr(mo.pos), Levels()));
		switch (i)
		{
		case 0:     // the changing room: the start, the plunge hall's pressure door ahead (its lamps)
			Look(mo, st, 224, 192, 20);
			break;
		case 1:     // the plunge hall from the gallery's corner, dry: BLUE by the plunge, 101 and the ledge
			Look(mo, st, 520, 470, 330, 18);
			break;
		case 2:     // ... with BLUE in 102: P at 224, the ledge 8 under (from the landing at 240)
			if (st == 1) { HangQuiet(mo, Blue(), 102); Set(TP, 224); }
			Look(mo, st, 832, 480, 300, 25);
			break;
		case 3:     // ... under water: the gallery stair going on down, the gauge
			Look(mo, st, 760, 200, 240, 10, 60);
			break;
		case 4:     // the ledge and the pump corridor's door, from the water
			Look(mo, st, 960, 224, 0, -5, 190);
			break;
		case 5:     // the swimming bath, dry: the pit, the shallow end, the five panes
			Look(mo, st, -150, 300, 180, 10);
			break;
		case 6:     // ... with BLUE in 142: the water at the poolside
			if (st == 1) { Set(TSB, 0); }
			Look(mo, st, -150, 300, 180, 10);
			break;
		case 7:     // the cooling hall full, as found, from the walkway
			Look(mo, st, 2336, 736, 315, 20);
			break;
		case 8:     // ... drained by GREEN in 113: the floor, E2, the cells open
			if (st == 1) { Set(TC, -128); }
			Look(mo, st, 2336, 736, 315, 20);
			break;
		case 9:     // the floor at E2 and the cells, their lamps
			Look(mo, st, 2976, 220, 270, 0);
			break;
		case 10:    // the pipe: under C's water before 113, T through it
			if (st == 1) { HangQuiet(mo, Leaf(0), 113); HangQuiet(mo, Leaf(1), 121); Set(TC, 100); Set(TT, 228); }
			Look(mo, st, 2784, 96, 270, 0, -128);
			break;
		case 11:    // the boiler house: T's gauge glass and float mark, T at 228
			Look(mo, st, 3880, 616, 0, -10);
			break;
		case 12:    // T from the catwalk
			Look(mo, st, 4200, 448, 90, 30);
			break;
		case 13:    // the lower yard from the yard gate
			Look(mo, st, 3648, 920, 20, -5);
			break;
		case 14:    // the lock from its sill, dry: 131, 135, the shelf and 133
			Look(mo, st, 4032, 2280, 270, 25);
			break;
		case 15:    // ... at 96 (BLUE in 131)
			if (st == 1) { Set(TK, 96); }
			Look(mo, st, 4032, 2280, 270, 25);
			break;
		case 16:    // ... at 184 (BLUE in 133): 8 under the sill
			if (st == 1) { Set(TK, 184); }
			Look(mo, st, 4032, 2280, 270, 25);
			break;
		case 17:    // the wheel house: L from its east end, the spillway coming down into it; dry
			Look(mo, st, 5060, 1950, 150, 5, 12);
			break;
		case 18:    // ... the circle running (L full, the leaves in 107 and 108)
			if (st == 1) { Free(TC); Free(TT); HangQuiet(mo, Leaf(0), 107); HangQuiet(mo, Leaf(1), 108); Set(TL, -4); }
			if (st == 2) Free(TL);
			Look(mo, st, 5060, 1950, 150, 5, 12);
			break;
		case 19:    // the sluice and the wheel's lamp from the lower yard, the wheel turning
			Look(mo, st, 4900, 1312, 0, 0);
			break;
		case 20:    // through the sluice: the tunnel and the machine hall
			Look(mo, st, 5240, 1312, 0, 0);
			break;
		}
	}

	// --- MODE=5: the fights' causes --------------------------------------------------------------
	bool Due(string name, int cause, int tag, int height, bool expect)
	{
		int arg = Key(tag, height);
		int at = At(cause, arg), left = AmbushLeft(cause, arg);
		Check(name, expect ? at > 0 && left == 0 : at > 0 && left == at,
			String.Format("%d of %d came; %s", at - left, at, Levels()));
		return true;
	}
	bool Coming(string name, int cause, int tag, int height, int limit = 350)
	{
		int arg = Key(tag, height);
		int at = At(cause, arg), left = AmbushLeft(cause, arg);
		if (left > 0 && opT < limit) return false;
		Check(name, at > 0 && left == 0, String.Format("%d of %d came within %.1f s; %s", at - left, at, opT / 35., Levels()));
		return true;
	}
	Array<Actor> walkers;
	void Fights(Actor mo)
	{
		AjarDoor blue = Blue(), green = Green();
		if (Op())
		{
			Info(String.Format("water ambush groups %d", ambKey.Size()));
			PoseF(mo, 224, 192, 90);
			Next();
		}
		// P: not before it stands over 200; then the cacodemons
		if (Op() && Hang(mo, "blueIn101", blue, 101)) Next();
		if (Op() && Rest("P_blue101", TP, Measured(E_P101))) Next();
		if (Op() && Due("P_notAt96", 60, TP, 200, false)) Next();
		if (Op() && Hang(mo, "blueIn102", blue, 102)) Next();
		if (Op())
		{
			int arg = Key(TP, 200);
			bool early = AmbushLeft(60, arg) < At(60, arg);
			if (W(TP) < 200 && !early && opT < 1400) return;
			Check("P_noneBefore200", !early || W(TP) >= 200, Levels());
			Next();
		}
		if (Op() && Coming("P_cacosOver200", 60, TP, 200)) Next();
		// C: the walkway's second lot when it is first dry; the cells open
		if (Op() && Due("C_notWhileFull", 61, TC, -120, false)) Next();
		if (Op() && Hang(mo, "greenIn113", green, 113)) Next();
		if (Op() && Coming("C_impsWhenDry", 61, TC, -120, 700)) Next();
		if (Op() && DoorState("cellAOpen", PD_CA, true, 350)) Next();
		if (Op() && DoorState("cellBOpen", PD_CB, true, 350)) Next();
		// flooding C drowns what walks on its floor: the cells' company put out on the floor, and C flooded
		if (Op())
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			int n = 0;
			while (a = Actor(it.Next()))
			{
				if (!a.bIsMonster || a.health <= 0 || a.pos.y > -32 || a.pos.y < -420 || a.pos.x < 3000 || a.pos.x > 3440) continue;
				a.SetOrigin((2600 + 64 * (n % 8), 300 + 64 * (n / 8), -128), false);
				walkers.Push(a);
				n++;
			}
			Info(String.Format("%d from the cells on C's floor", n));
			Next();
		}
		if (Op() && TakeDown(mo, "greenOutOf113", green)) Next();
		if (Op() && Hang(mo, "blueIn111", blue, 111)) Next();
		if (Op())
		{
			int pinkies = 0, pinkiesDead = 0, hurt = 0;
			for (int i = 0; i < walkers.Size(); i++)
			{
				let a = walkers[i];
				if (!a) continue;
				if (a is "Demon") { pinkies++; if (a.health <= 0) pinkiesDead++; }
				if (a.health < a.SpawnHealth()) hurt++;
			}
			if (opT < 35 * 20) return;
			Check("floodingDrowns", walkers.Size() > 0 && pinkies > 0 && pinkiesDead == pinkies && hurt > 0,
				String.Format("%d walkers, pinkies %d dead of %d, %d hurt; C %.1f", walkers.Size(), pinkiesDead, pinkies, hurt, W(TC)));
			Next();
		}
		// T: company when the float trips
		if (Op() && Due("T_notYet", 60, TT, 216, false)) Next();
		if (Op() && Hang(mo, "tealIn113", Leaf(0), 113)) Next();
		if (Op() && Hang(mo, "tealIn121", Leaf(1), 121)) Next();
		if (Op() && Coming("T_companyAt216", 60, TT, 216, 900)) Next();
		// K: lost souls and cacodemons when it first stands over 150
		if (Op() && Due("K_notYet", 60, TK, 150, false)) Next();
		if (Op() && Hang(mo, "blueIn131", blue, 131)) Next();
		if (Op() && Rest("K_blue131", TK, Measured(E_K131))) Next();
		if (Op() && Due("K_notAt96", 60, TK, 150, false)) Next();
		if (Op() && Hang(mo, "blueIn133", blue, 133)) Next();
		if (Op() && Coming("K_soulsOver150", 60, TK, 150, 700)) Next();
		// each once: every water ambusher has come, and no more are left to come again
		if (Op())
		{
			int total = 0, left = 0;
			for (int i = 0; i < ambKey.Size(); i++) { total += ambAt[i]; left += AmbushLeft(ambKey[i] >> 16, ambKey[i] & 0xFFFF); }
			Check("eachWaterAmbushOnce", left == 0 && total > 0, String.Format("%d ambushers, %d left", total, left));
			Next();
		}
	}

	// --- MODE=6: the secret way out -------------------------------------------------------------
	Vector2 Copy(double x, double y) { return (CX - x, y + CY); }
	bool InCopy(Vector2 p) { return p.y < -1000; }
	AjarLeftHanded Marker()
	{
		let it = ThinkerIterator.Create("AjarLeftHanded");
		return AjarLeftHanded(it.Next());
	}
	// walks (keys held) towards (x, y); true once within r
	bool Toward(Actor mo, Vector2 to, int key = WALKKEY, int b = 0, double r = 12)
	{
		Vector2 d = to - mo.pos.xy;
		if (d.Length() < r) return true;
		mo.angle = VectorAngle(d.x, d.y);
		Keys(key, b);
		return false;
	}
	double maxDev;              // the most the copy's water was off the bath's, any tic
	Vector3 prev;
	bool crossed;
	int crossT;
	LeftHandDummy dummyIn, dummyBehind;
	Actor shot;
	Vector3 shotLast;
	bool shotGone;
	int wp;

	// over the sill of the pane before the player and through it: `dir` 180 into the copy, 0 back out;
	// the landing is checked against the portal's shift (32, -2048) and the walk goes on `after` tics
	bool Through(Actor mo, string name, double dir, int after = 35)
	{
		Line a = h.FindLine(PANE4), b = h.FindLine(PANE4_FAR);
		bool into = dir == 180;
		if (opT == 0) { crossed = false; prev = mo.pos; }
		mo.angle = dir;
		if (!crossed)
		{
			if (InCopy(mo.pos.xy) == into && (mo.pos.xy - prev.xy).Length() > 200)
			{
				crossed = true;
				crossT = opT;
				Vector2 shift = into ? (32, -2048) : (-32, 2048);
				double e = (mo.pos.xy - (prev.xy + shift)).Length();
				Check(name, e < 24 && abs(Actor.DeltaAngle(mo.angle, dir)) < 0.001,
					String.Format("before %s, after %s facing %.1f: the shift says %s, off by %.2f (a tic's walk); turn %.3f; water %.1f",
					PStr(prev), PStr(mo.pos), mo.angle, PStr((prev.xy + shift, prev.z)), e, LeftHandTest.Turn(into ? a : b, into ? b : a), W(TSB)));
			}
			else
			{
				prev = mo.pos;
				Keys(WALKKEY, BT_JUMP);
				if (opT < 350) return false;
				Check(name, false, String.Format("not through after %d tics: player %s, water %.1f", opT, PStr(mo.pos), W(TSB)));
				return true;
			}
		}
		Keys(WALKKEY);
		return opT - crossT >= after;
	}

	bool Shoot(Actor mo, string name, class<Actor> type, double y, LeftHandDummy want, LeftHandDummy notWant, double xMin, double xMax)
	{
		if (opT == 0)
		{
			PoseF(mo, -300, y, 180);
			if (want) want.hits = 0;
			if (notWant) notWant.hits = 0;
			shot = mo.SpawnPlayerMissile(type, 180, nofreeaim: true, noautoaim: true);
			shotGone = false;
			shotLast = shot ? shot.pos : (0, 0, 0);
		}
		if (shot && shot.bMissile) shotLast = shot.pos;
		else shotGone = true;
		if (opT < 70) return false;
		bool ok = shotGone && shotLast.x >= xMin && shotLast.x <= xMax;
		if (want) ok = ok && want.hits > 0;
		if (notWant) ok = ok && notWant.hits == 0;
		Check(name, ok, String.Format("%s last flying at %s; the dummy in the copy hit %d%s", type.GetClassName(), PStr(shotLast),
			want ? want.hits : notWant.hits, want ? "" : " (none wanted)"));
		if (shot) shot.Destroy();
		return true;
	}

	bool Hitscan(Actor mo, string name, double y, LeftHandDummy want, LeftHandDummy notWant)
	{
		PoseF(mo, -300, y, 180);
		if (want) want.hits = 0;
		if (notWant) notWant.hits = 0;
		Actor puff;
		int dmg;
		[puff, dmg] = mo.LineAttack(180, 4096, 0, 10, 'Hitscan', "BulletPuff", LAF_NORANDOMPUFFZ);
		bool ok = want ? want.hits == 1 : notWant.hits == 0 && puff && puff.pos.x > GLASS - 1 && !InCopy(puff.pos.xy);
		Check(name, ok, String.Format("dummy hit %d; puff %s", want ? want.hits : notWant.hits, puff ? PStr(puff.pos) : "none"));
		return true;
	}

	// a path of the bath's points (walked in the copy, where each is (CX - x, y + CY))
	static const double PATHX[] = { -740, -560, -480, -300, -300, -448 };
	static const double PATHY[] = { 450, 450, 450, 450, 600, 600 };

	void Secret(Actor mo)
	{
		testing6 = true;
		lastPos = mo.pos;
		AjarDoor blue = Blue(), green = Green();
		let cb = B(TSBL), sb = B(TSB);
		if (cb && sb) maxDev = max(maxDev, abs(cb.w - sb.w));
		if (Op())
		{
			Line a = h.FindLine(PANE4), b = h.FindLine(PANE4_FAR);
			Vector2 p = (0, 0);
			if (a && b) p = LeftHandTest.Through(a, b, (GLASS, 352));
			Check("openingIsAShift", a && b && abs(Actor.DeltaAngle(LeftHandTest.Turn(a, b), 0)) < 1e-9 && (p - (GLASS + 32, 352 - 2048)).Length() < 1e-6,
				a && b ? String.Format("turn %.6f; (-848, 352) goes to (%.3f, %.3f)", LeftHandTest.Turn(a, b), p.x, p.y) : "no lines");
			let mk = Marker();
			int hidden = 0;
			if (mk) for (int i = 0; i < level.lines.Size(); i++)
				if (mk.Inside(level.lines[i].v1.p) && mk.Inside(level.lines[i].v2.p) && level.lines[i].flags & Line.ML_DONTDRAW) hidden++;
			Check("copyOffTheMap", mk && mk.args[2] && !mk.revealed && hidden > 50, String.Format("%d lines of the copy not drawn", hidden));
			Check("copyFollowsTheBath", cb && cb.follow == sb && cb.w == sb.w && cb.floorZ == sb.floorZ,
				cb ? String.Format("copy %.2f (floor %.1f), bath %.2f (floor %.1f)", cb.w, cb.floorZ, sb.w, sb.floorZ) : "no copy basin");
			Check("oneSecret", level.total_secrets == 1, String.Format("%d", level.total_secrets));
			int frames = 0;
			let fi = ThinkerIterator.Create("AjarFrame");
			AjarFrame f;
			while (f = AjarFrame(fi.Next())) if (InCopy(f.pos.xy)) frames++;
			Check("noFramesInTheCopy", frames == 0 && h.FindFrame(141) && h.FindFrame(142), String.Format("%d", frames));
			Next();
		}
		// BLUE in 142: the bath at 0, the copy with it
		if (Op() && PoseAt(mo, FRONT + 142)) Next();
		if (Op() && Hang(mo, "blueIn142", blue, 142)) Next();
		if (Op() && Rest("SB_blue142", TSB, Measured(E_SB142))) Next();
		if (Op())
		{
			Check("copyAt0", abs(W(TSBL) - W(TSB)) < 1e-6 && abs(W(TSB)) < 0.5, Levels() .. String.Format(" copy %.3f", W(TSBL)));
			Next();
		}
		// the swim from the shallow end to the fourth pane, over its sill and through: into the copy's water
		if (Op())
		{
			if (!Toward(mo, (-780, 352), WALKKEY, BT_JUMP, 16) && opT < 700) return;
			Check("swumToTheFourthPane", (mo.pos.xy - (-780, 352)).Length() < 24, String.Format("player %s waterlevel %d after %d tics", PStr(mo.pos), mo.waterlevel, opT));
			Next();
		}
		if (Op() && Through(mo, "throughTheOpening", 180)) Next();
		if (Op())
		{
			let mk = Marker();
			Check("inTheCopysWater", InCopy(mo.pos.xy) && mo.pos.x < CX + 832 && mo.waterlevel >= 1 && abs(W(TSBL) - W(TSB)) < 1e-6,
				String.Format("player %s waterlevel %d; copy %.2f, bath %.2f", PStr(mo.pos), mo.waterlevel, W(TSBL), W(TSB)));
			Check("copyOnTheMapOnceEntered", mk && mk.revealed);
			Next();
		}
		// and back: the copy's fourth pane, from its water, into the bath
		if (Op())
		{
			if (!Toward(mo, Copy(-780, 352), WALKKEY, BT_JUMP, 16) && opT < 350) return;
			Check("swumToTheCopysFourthPane", (mo.pos.xy - Copy(-780, 352)).Length() < 24, PStr(mo.pos));
			Next();
		}
		if (Op() && Through(mo, "backThroughTheOpening", 0)) Next();
		if (Op())
		{
			Check("backInTheBathsWater", !InCopy(mo.pos.xy) && mo.pos.x > GLASS && mo.waterlevel >= 1, String.Format("player %s waterlevel %d", PStr(mo.pos), mo.waterlevel));
			Next();
		}
		// a mirror pane is a wall: swimming at the third goes nowhere
		if (Op())
		{
			if (!Toward(mo, (-780, 256), WALKKEY, BT_JUMP, 16) && opT < 350) return;
			Next();
		}
		if (Op())
		{
			mo.angle = 180;
			Keys(WALKKEY, BT_JUMP);
			if (opT < 105) return;
			Keys();
			Check("mirrorPaneIsAWall", !InCopy(mo.pos.xy) && mo.pos.x > -832 && mo.pos.x < -790, String.Format("player %s after 3 s", PStr(mo.pos)));
			Next();
		}
		// shots: through the opening they fly on into the copy; at a mirror they stop
		if (Op())
		{
			Vector2 p = Copy(-700, 352), q = Copy(-700, 256);
			dummyIn = LeftHandDummy(Actor.Spawn("LeftHandDummy", (p, 0)));
			dummyBehind = LeftHandDummy(Actor.Spawn("LeftHandDummy", (q, 0)));
			Next();
		}
		if (Op() && Shoot(mo, "rocketThroughTheOpening", "Rocket", 352, dummyIn, null, CX + 700 - 40, CX + 848)) Next();
		if (Op() && Shoot(mo, "plasmaThroughTheOpening", "PlasmaBall", 352, dummyIn, null, CX + 700 - 40, CX + 848)) Next();
		if (Op() && Shoot(mo, "rocketAtAMirrorStops", "Rocket", 256, null, dummyBehind, GLASS - 1, -800)) Next();
		if (Op() && Hitscan(mo, "hitscanThroughTheOpening", 352, dummyIn, null)) Next();
		if (Op() && Hitscan(mo, "hitscanAtAMirrorStops", 256, null, dummyBehind)) Next();
		if (Op())
		{
			dummyIn.Destroy();
			dummyBehind.Destroy();
			PoseF(mo, -760, 352, 180, -40);
			Next();
		}
		// in again, and the bath's level changed behind the player: BLUE moved to 141 (both at -64), then
		// GREEN (both dry); he cannot come back through the glass, and the copy's steps take him to its door
		if (Op() && Through(mo, "inAgain", 180, 20)) Next();
		if (Op() && Hang(mo, "blueIn141_behindHim", blue, 141)) Next();
		if (Op())
		{
			mo.vel.xy = (0, 0);
			if (Rest("SB_blue141", TSB, Measured(E_SB141))) Next();
		}
		if (Op())
		{
			Check("copyAtMinus64", abs(W(TSBL) - W(TSB)) < 1e-6 && abs(W(TSB) + 64) < 0.5, String.Format("copy %.3f, bath %.3f", W(TSBL), W(TSB)));
			Next();
		}
		if (Op())
		{
			if (!Toward(mo, Copy(-780, 352), WALKKEY, BT_JUMP, 16) && opT < 350) return;
			Next();
		}
		if (Op())
		{
			mo.angle = 0;
			Keys(WALKKEY, BT_JUMP);
			if (opT < 140) return;
			Keys();
			Check("noWayBackAtMinus64", InCopy(mo.pos.xy), String.Format("player %s (the sill 64 over the water)", PStr(mo.pos)));
			Next();
		}
		if (Op() && Hang(mo, "greenIn141_drains", green, 141)) Next();
		if (Op())
		{
			mo.vel.xy = (0, 0);
			if (Rest("SB_green141", TSB, -160)) Next();
		}
		if (Op())
		{
			Check("copyDry", abs(W(TSBL) - W(TSB)) < 1e-6 && !B(TSBL).Wet() && !B(TSB).Wet(), String.Format("copy %.3f, bath %.3f", W(TSBL), W(TSB)));
			Next();
		}
		if (Op())
		{
			mo.angle = 0;
			Keys(WALKKEY, BT_JUMP);
			if (opT < 105) return;
			Keys();
			Check("noWayBackDry", InCopy(mo.pos.xy), String.Format("player %s", PStr(mo.pos)));
			wp = 0;
			Next();
		}
		if (Op())        // up the copy's steps to its door: the pit's steps, the shallow end, the stair, the poolside
		{
			if (wp < 6 && Toward(mo, Copy(PATHX[wp], PATHY[wp]), WALKKEY, 0, 12)) wp++;
			if (wp < 6 && opT < 1400) return;
			Keys();
			Check("toTheCopysDoorDry", wp == 6 && abs(mo.pos.z) < 1, String.Format("player %s after %.1f s, at point %d of 6", PStr(mo.pos), opT / 35., wp));
			Next();
		}
		if (Op())
		{
			mo.angle = 90;
			Line door = null;
			for (int i = 0; i < level.lines.Size(); i++)
			{
				Line l = level.lines[i];
				if (l.special == 12 && InCopy(l.v1.p) && l.v1.p.y == 648 + CY && l.v2.p.y == 648 + CY) door = l;
			}
			bool used = door && door.Activate(mo, 0, SPAC_Use);
			Check("copysDoorOpens", used, door ? String.Format("(%.0f,%.0f)-(%.0f,%.0f)", door.v1.p.x, door.v1.p.y, door.v2.p.x, door.v2.p.y) : "no door");
			Next();
		}
		if (Op() && Stand(mo, 40)) Next();
		if (Op())
		{
			mo.angle = 90;
			Keys(WALKKEY);
			if (opT < 280) return;
			Check("exitLineNotReached", false, String.Format("still here: %s; secrets %d", PStr(mo.pos), level.found_secrets));
			Next();
		}
	}

	// --- MODE=7: the pane wall seen (tools/smoke_MAP20_7.cfg shoots at 78 + 80 n; tools/highwater_compare.py)
	// views 0..8: three places on the poolside (straight on from the east, from the north walk, from the south
	// end) x the bath dry, at -64, at 0, the player hidden; 9..11: the three at 0 with the player drawn;
	// 12..16: the player before each pane in turn (in line with it), at 0; 17: along the wall, the copy's door in
	// the fourth pane; 18: from the north walk with BLUE hung in 142; 19..21: the notch (P at 48 at its
	// pressure door, K at 48 at its door, C at -64 at E2 and the cells); 22: from the copy, back at the opening;
	// 23..31: views 0..8 again. From view 9 on (but the notch's) the water's surface is a still flat
	// (AJLBFLOR, the lab's floor with an F in its corner) in both baths, since the engine animates FWATER1 by
	// the clock and no two runs catch it at the same frame: what differs is then the opening's alone. The
	// camera is put from st 20 on, the water set at st 1.
	void Still(bool on)
	{
		TextureID t = TexMan.CheckForTexture(on ? "AJLBFLOR" : "FWATER1", TexMan.Type_Any);
		for (int i = 0; i < wh.basins.Size(); i++)
		{
			let b = wh.basins[i];
			if (b.Tag() == TSB || b.Tag() == TSBL) b.ctl.SetTexture(Sector.ceiling, t);
		}
	}
	void PoseV(Actor mo, int st, double x, double y, double ang, double pitch = 0, double z = -1e9)
	{
		if (st >= 20) { PoseF(mo, x, y, ang, z); mo.pitch = pitch; }
	}
	static const double VX[] = { -200, -560, -300 };
	static const double VY[] = { 300, 600, 40 };
	static const double VA[] = { 180, 218, 150 };
	void PaneViews(Actor mo)
	{
		int i = (tic - 3) / 80, st = (tic - 3) % 80;
		if (st == 0) Console.Printf("AJARTEST view=%d t=%d", i, tic);
		if (st == 79) Info(String.Format("view %d: player %s facing %.1f hidden %d; %s copy %.1f", i, PStr(mo.pos), mo.angle, mo.bInvisible, Levels(), W(TSBL)));
		int j = i >= 23 ? i - 23 : i;
		if (st == 1)
		{
			mo.bInvisible = i < 9 || i == 17 || i == 18 || i >= 23;
			Still(i >= 9 && i != 19 && i != 20 && i != 21);
			if (j < 9) Set(TSB, j % 3 == 0 ? -160 : j % 3 == 1 ? -64 : 0);
			else if (i < 19) Set(TSB, 0);
			if (i == 18) HangQuiet(mo, Blue(), 142);
			if (i == 19) { Set(TP, 48); TakeDoor(mo, Blue()); if (h.carried) h.BeltPutBack(h.carried); }    // BLUE back out of 142
			if (i == 20) Set(TK, 48);
			if (i == 21) Set(TC, -64);
			if (i == 22) Set(TSB, 0);
		}
		if (i >= 23) { int c = j / 3; PoseV(mo, st, VX[c], VY[c], VA[c], 8); }
		else if (i < 12) { int c = i < 9 ? i / 3 : i - 9; PoseV(mo, st, VX[c], VY[c], VA[c], 8); }
		else if (i < 17) PoseV(mo, st, -330, 64 + 96 * (i - 12), 180, 0);
		else if (i == 17) PoseV(mo, st, -700, 220, 143, 0, 0);
		else if (i == 18) PoseV(mo, st, VX[1], VY[1], VA[1], 8);
		else if (i == 19) PoseV(mo, st, 640, 64, 180, 20, 70);
		else if (i == 20) PoseV(mo, st, 4000, 2010, 270, 20, 80);
		else if (i == 21) PoseV(mo, st, 3040, 220, 270, 20, -40);
		else if (i == 22) PoseV(mo, st, CX + 700, 352 + CY, 0, 0, 0);
	}
}
