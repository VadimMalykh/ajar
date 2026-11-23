// The water lab's checks (map WATER, tools/map_water.py; water.zs; PLAN.md,
// "The water lab"). MAP=WATER MODE=n tools/smoke.sh.
// Frames: 101 hall A floor (west), 102 A's gallery (128), 103 A floor (east),
// 104 B (TEAL), 105 B (BLUE), 106 C (192, TEAL), 107 L's foot, 108 U's head
// (192), 109 L (BLUE), 110 the cell K. Far sides: 202 BLUE (in R), 203 GREEN
// (in O). Basin tags: 21 A, 22 R, 23 O, 24 B, 25 C, 26 U, 27 L, 28 K.

// a target that counts what hits it and does not move
class WaterDummy : Actor
{
	int hits;
	string by;
	Default
	{
		Radius 16;
		Height 56;
		Health 100000;
		Mass 100000;
		+SHOOTABLE +SOLID +NOBLOOD +DONTTHRUST +NOGRAVITY +NODAMAGETHRUST
	}
	States
	{
	Spawn:
		POSS A -1;
		Stop;
	}
	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		hits++;
		by = by .. (inflictor ? inflictor.GetClassName() .. " " : "none ");
		return 0;
	}
}

class WaterTest : EventHandler
{
	const TA = 21; const TR = 22; const TO = 23; const TB = 24; const TC = 25; const TU = 26; const TL = 27; const TK = 28;
	int tic, cur, tt;
	int checks, fails;
	AjarHandler h;
	AjarWaterHandler wh;
	AjarDoor blue, green;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "WATER"; }

	bool Seg(int n)
	{
		bool now = tic >= cur && tic < cur + n;
		if (now) tt = tic - cur;
		cur += n;
		return now;
	}
	bool At() { return Seg(1); }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	AjarBasin B(int tag) { return wh.BasinOfTag(tag); }
	double W(int tag) { return B(tag).w; }
	double D(int tag) { return B(tag).Depth(); }

	AjarDoor Leaf(int colour, int n)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.args[1] == colour && !n--) return d;
		return null;
	}

	void HangIn(AjarDoor d, int frameId)
	{
		AjarFrame f = h.FindFrame(frameId);
		if (!d || !f) { Info(String.Format("no door or no frame %d", frameId)); return; }
		if (f.door == d) return;
		if (d.frame) h.Unhang(d.frame);
		if (f.door) h.Unhang(f);
		h.Hang(d, f);
	}
	void Down(int frameId)
	{
		AjarFrame f = h.FindFrame(frameId);
		if (f && f.door) h.Unhang(f);
	}
	void AllDown()
	{
		for (int i = 0; i < wh.frames.Size(); i++) if (wh.frames[i].door) h.Unhang(wh.frames[i]);
	}
	void SetW(int tag, double depth)
	{
		let b = B(tag);
		b.w = depth < 0 ? b.floorZ : b.floorZ + depth;
	}

	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }

	void Pose(Actor mo, double x, double y, double ang, double z = -1e9, double pitch = 0)
	{
		mo.SetOrigin((x, y, z > -1e8 ? z : FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
	}

	string Levels()
	{
		return String.Format("A %.2f R %.2f O %.2f B %.2f C %.2f U %.2f L %.2f K %.2f",
			W(TA), W(TR), W(TO), W(TB), W(TC), W(TU), W(TL), W(TK));
	}

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		if (!wh) wh = AjarWaterHandler.Get();
		if (!wh || !wh.ready) return;
		tic++;
		if (tic == 1)
		{
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			blue = h.DoorOf(2); green = h.DoorOf(3);
			Info(String.Format("basins %d, weirs %d, frames %d; %s", wh.basins.Size(), wh.weirs.Size(), wh.frames.Size(), Levels()));
		}
		cur = 2;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode == 1) SeeIt(mo);
		else if (mode == 2) Pipe(mo);
		else if (mode == 3) Circle(mo);
		else if (mode == 4) Swimmer(PlayerPawn(mo));
		else if (mode == 5) Shots(mo);
		else if (mode == 6) Company(mo);
		else if (mode == 7) Views(mo);
		else if (mode == 8) Rafting(mo);
		Drive(mo);
		if (mode != 7 && tic == cur + 2)
			Console.Printf("AJARTEST waterDone=1 checks=%d failed=%d", checks, fails);
	}

	// --- the player's controls (the test "holds" keys) ----------------------------------------------
	int fwd, side, up;
	uint btn;
	void Keys(int f = 0, int sd = 0, int u = 0, uint b = 0) { fwd = f; side = sd; up = u; btn = b; }
	// The engine has moved the player for this tic before any handler runs (P_PlayerThink comes
	// before WorldTick), with no keys down in a headless run. With keys "held", this puts them into
	// the player's command and runs the engine's own movement and use for the tic once more
	// (PlayerPawn.HandleMovement: MovePlayer, CheckJump, CheckMoveUpDown; CheckUse).
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp || !(fwd || side || up || btn)) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.sidemove = side;
		pp.player.cmd.upmove = up;
		pp.player.cmd.buttons = btn;
		pp.HandleMovement();
		if (btn & BT_USE) pp.CheckUse();
	}
	const WALKKEY = 0x1900;
	const RUNKEY = 0x3200;

	// --- a stretch in which basin `tag` goes to `expect` (absolute), checked at its end -----------
	int reachAt;
	void Approach(int tag, double expect, int n, string name, double tol = 0.5)
	{
		if (Seg(n))
		{
			if (tt == 0) reachAt = -1;
			if (reachAt < 0 && abs(W(tag) - expect) < 1) reachAt = tt;
			if (tt % 70 == 0) Info(String.Format("%s t+%.0fs: %s", name, tt / 35., Levels()));
		}
		if (At()) Check(name, abs(W(tag) - expect) < tol, String.Format("expected %.2f, measured %.3f (%.3f over the floor); within 1 of it after %.1f s",
			expect, W(tag), W(tag) - B(tag).floorZ, reachAt < 0 ? -1 : reachAt / 35.));
	}
	// the flow through the door hung in frame `frameId` this tic (0: no link), signed from its frame's side
	double LinkFlow(int frameId)
	{
		for (int i = 0; i < wh.linkFrame.Size(); i++) if (wh.linkFrame[i] == frameId) return wh.linkQ[i];
		return 0;
	}
	Sector SectorAt(double x, double y) { return level.PointInSector((x, y)); }
	double Gap(Sector s) { return s.ceilingplane.ZatPoint(s.centerspot) - s.floorplane.ZatPoint(s.centerspot); }

	// --- MODE=1: see it (bay 1): the depth by the frame's height, the drain ----------------------
	void SeeIt(Actor mo)
	{
		if (At()) { mo.player.cheats |= CF_GODMODE; Pose(mo, -840, -256, 0); AllDown(); SetW(TA, -1); HangIn(blue, 101); }
		Approach(TA, 96, 700, "blue101_aPoolOfTheHead");
		if (At()) HangIn(blue, 102);
		Approach(TA, 224, 1050, "blue102_galleryPlusTheHead");
		if (At()) HangIn(green, 103);
		Approach(TA, 96, 700, "blue102_green103_fedAndDrained");
		if (At()) HangIn(blue, 101);
		Approach(TA, 96. / 9, 700, "blue101_green103_theDrainHoldsItNearItsSill");
		if (At()) Down(101);
		Approach(TA, 0, 350, "green103_drainsToItsSill");
		if (At()) { Down(103); HangIn(blue, 102); }
		Approach(TA, 224, 1050, "blue102_again");
		if (At()) { Down(102); HangIn(green, 102); }
		Approach(TA, 128, 700, "green102_drainsToTheGallery");
		if (At()) HangIn(green, 101);
		Approach(TA, 0, 350, "green101_drainsToTheFloor");
		// a door whose far side is in no basin, and a frame in no basin: no link
		// the bulkhead, from the corridor: shut while A holds water, opens when it is dry
		Sector bh = SectorAt(256, -8);
		if (At()) { AllDown(); SetW(TA, 40); B(TA).held = true; Pose(mo, 256, -60, 90); h.said = ""; }
		if (Seg(3)) { if (tt == 1) Keys(0, 0, 0, BT_USE); else Keys(); }
		Seg(35);
		if (At()) Check("bulkhead_shutWhileWet", Gap(bh) < 1 && h.said.IndexOf("Water stands") >= 0, String.Format("gap %.1f; said \"%s\"", Gap(bh), h.said));
		if (At()) { SetW(TA, -1); }
		if (Seg(3)) { if (tt == 1) Keys(0, 0, 0, BT_USE); else Keys(); }
		Seg(35);
		if (At()) { Check("bulkhead_opensWhenDry", Gap(bh) > 48, String.Format("gap %.1f", Gap(bh))); B(TA).held = false; }
	}

	// --- MODE=2: the pipe (bay 2): a Pair lifts water ---------------------------------------------
	double v0, wb0, wc0;
	double Vol(int tag) { return B(tag).Volume(); }
	void Pipe(Actor mo)
	{
		if (At()) { mo.player.cheats |= CF_GODMODE; AllDown(); HangIn(blue, 105); HangIn(Leaf(8, 0), 104); HangIn(Leaf(8, 1), 106); }
		if (Seg(2100) && tt % 70 == 0) Info(String.Format("pipe t+%.0fs: %s; flow by 105 %.0f, by the pair %.0f", tt / 35., Levels(), LinkFlow(105), LinkFlow(104)));
		if (At())
		{
			Check("pipe_B_theHead", abs(W(TB) - 96) < 0.5, String.Format("expected 96, measured %.3f", W(TB)));
			Check("pipe_C_192higher", abs(W(TC) - 288) < 0.5 && abs(W(TC) - W(TB) - 192) < 0.5, String.Format("expected 288 (192 over B), measured %.3f (%.3f over B)", W(TC), W(TC) - W(TB)));
		}
		if (At()) { Down(105); wb0 = W(TB); wc0 = W(TC); }
		Seg(175);
		if (At()) Check("pipe_withoutTheReservoir_stays", abs(W(TB) - wb0) < 0.05 && abs(W(TC) - wc0) < 0.05,
			String.Format("B %.3f to %.3f, C %.3f to %.3f in 5 s; flow by the pair %.3f a tic", wb0, W(TB), wc0, W(TC), LinkFlow(104)));
		if (At()) HangIn(green, 105);
		if (Seg(1050) && tt % 70 == 0) Info(String.Format("pipe drain t+%.0fs: %s; flow by 105 %.0f, by the pair %.0f", tt / 35., Levels(), LinkFlow(105), LinkFlow(104)));
		if (At())
		{
			Check("pipe_drain_B", W(TB) < 0.5, String.Format("expected 0, measured %.3f", W(TB)));
			Check("pipe_drain_C_toItsSill", W(TC) < 192.5, String.Format("expected 192 (its sill), measured %.3f", W(TC)));
		}
		// B filled alone, then the pair: the water shares itself out to equal heads
		if (At()) { AllDown(); SetW(TB, -1); SetW(TC, -1); HangIn(blue, 105); }
		Seg(700);
		if (At()) { Down(105); v0 = Vol(TB) + Vol(TC); HangIn(Leaf(8, 0), 104); HangIn(Leaf(8, 1), 106); }
		Seg(5);
		if (At()) Check("pipe_flowSigned_BtoC", LinkFlow(104) > 0, String.Format("flow by the pair, from 104's side (B) %.1f a tic", LinkFlow(104)));
		if (Seg(1050) && tt % 70 == 0) Info(String.Format("pipe share t+%.0fs: %s; flow by the pair %.0f", tt / 35., Levels(), LinkFlow(104)));
		if (At())
		{
			double v1 = Vol(TB) + Vol(TC);
			Check("pipe_share_equalHeads", abs(W(TB) - 48) < 0.5 && abs(W(TC) - 240) < 0.5, String.Format("expected B 48, C 240; measured B %.3f, C %.3f", W(TB), W(TC)));
			Check("pipe_share_noWaterLost", abs(v1 - v0) < 1e-6 * v0, String.Format("volume before %.3f, after %.3f", v0, v1));
		}
	}

	// --- MODE=3: the circle (bay 3) -------------------------------------------------------------------
	int startedAt, stoppedAt, shutAt;
	double overAtDown;
	double lamp;
	void Circle(Actor mo)
	{
		AjarWeir wr = wh.weirs[0];
		Sector lampS = SectorAt(3072, -256), shut = SectorAt(3072, -328);
		if (At()) { mo.player.cheats |= CF_GODMODE; AllDown(); SetW(TL, -1); SetW(TU, -1); HangIn(blue, 109); }
		Seg(700);
		if (At())
		{
			Check("circle_LFilledToTheHead", abs(W(TL) - 96) < 0.5, String.Format("%.3f", W(TL)));
			Down(109);
			v0 = Vol(TL) + Vol(TU);
			HangIn(Leaf(9, 0), 107); HangIn(Leaf(9, 1), 108);
			startedAt = -1;
		}
		if (Seg(1400))
		{
			if (startedAt < 0 && wr.turning) startedAt = tt;
			if (tt % 70 == 0) Info(String.Format("circle t+%.0fs: L %.3f U %.3f; by the pair %.0f (L to U), over the weir %.0f; wheel %s, lamp %d, shutter %.1f",
				tt / 35., W(TL), W(TU), LinkFlow(107), wr.flow, wr.turning ? "turning" : "still", lampS.lightlevel, Gap(shut)));
		}
		if (At())
		{
			// steady: K (hL - hU) = K_WEIR (hU - 32) and hL + hU = H (the water there is, as a depth over one of the two equal areas)
			double H = v0 / B(TL).area, k = wh.K, k2 = wh.K_WEIR;
			double hU = (k * H + k2 * 32) / (2 * k + k2), hL = H - hU;
			Check("circle_U", abs(W(TU) - (192 + hU)) < 0.3, String.Format("expected %.3f (%.3f over the crest), measured %.3f", 192 + hU, hU - 32, W(TU)));
			Check("circle_L", abs(W(TL) - hL) < 0.3, String.Format("expected %.3f, measured %.3f", hL, W(TL)));
			double q = wh.K_WEIR * (hU - 32);
			Check("circle_goesRound", abs(wr.flow - q) < 0.02 * q && abs(LinkFlow(107) - wr.flow) < 0.02 * q,
				String.Format("expected %.0f a tic round; over the weir %.1f, up the pair (L to U) %.1f", q, wr.flow, LinkFlow(107)));
			Check("circle_noWaterLost", abs(Vol(TL) + Vol(TU) - v0) < 1e-6 * v0, String.Format("volume %.3f, at the start %.3f", Vol(TL) + Vol(TU), v0));
			Check("circle_wheelTurns", wr.turning && startedAt >= WaterTest.WHEELMIN && lampS.lightlevel == 255 && Gap(shut) > 95,
				String.Format("turning from %.1f s after the pair was hung; lamp %d; shutter open %.1f", startedAt / 35., lampS.lightlevel, Gap(shut)));
			Down(108);
			overAtDown = W(TU) - 224;
			stoppedAt = shutAt = -1;
		}
		if (Seg(1050))
		{
			if (stoppedAt < 0 && !wr.turning) stoppedAt = tt;
			if (shutAt < 0 && Gap(shut) < 0.5) shutAt = tt;
			if (tt % 70 == 0) Info(String.Format("circle stopping t+%.0fs: L %.3f U %.3f; over the weir %.0f (%.3f over the crest); wheel %s, lamp %d, shutter %.1f",
				tt / 35., W(TL), W(TU), wr.flow, wr.over, wr.turning ? "turning" : "still", lampS.lightlevel, Gap(shut)));
		}
		if (At())
		{
			// the spill falls as e^(-t K_WEIR / area): under 2 over the crest after ln(10.67 / 2) * 128 tics
			double expect = log(overAtDown / 2) * B(TU).area / wh.K_WEIR;
			Check("circle_wheelStops", stoppedAt >= 0 && abs(stoppedAt - expect) < 5 && lampS.lightlevel != 255,
				String.Format("stopped %.1f s after the leaf was taken down (expected %.1f s); lamp %d", stoppedAt / 35., expect / 35., lampS.lightlevel));
			Check("circle_shutterShuts", shutAt >= 0 && shutAt > stoppedAt + wh.SHUT_AFTER - 2,
				String.Format("shut %.1f s after the leaf was taken down, %.1f s after the wheel stopped", shutAt / 35., (shutAt - stoppedAt) / 35.));
			double hl = v0 / B(TL).area - 32;
			Check("circle_settles", abs(W(TU) - 224) < 0.2 && abs(W(TL) - hl) < 0.2 && abs(Vol(TL) + Vol(TU) - v0) < 1e-6 * v0,
				String.Format("U %.3f (crest 224), L %.3f (expected %.3f: what is left over)", W(TU), W(TL), hl));
		}
	}
	const WHEELMIN = 105;

	// --- MODE=4: the player in it (C) ---------------------------------------------------------------
	Vector3 p0;
	int phase;
	double best;
	void Swimmer(PlayerPawn mo)
	{
		if (At()) { mo.player.cheats |= CF_GODMODE; AllDown(); B(TA).held = true; Info(String.Format("air supply %d tics, player height %.0f, view height %.0f, speed %.2f", level.airsupply, mo.height, mo.player.viewheight, mo.speed)); }
		// waterlevel by depth: the engine's 1 is the feet, 2 the middle (28), 3 the eyes (41)
		static const int depths[] = { 8, 24, 30, 40, 44, 60 };
		static const int want[] = { 1, 1, 2, 2, 3, 3 };
		for (int i = 0; i < 6; i++)
		{
			if (At()) { SetW(TA, depths[i]); Pose(mo, 256, 200, 0); }
			Seg(4);
			if (At()) Check(String.Format("waterlevel_depth%d", depths[i]), mo.waterlevel == want[i], String.Format("waterlevel %d (expected %d)", mo.waterlevel, want[i]));
		}
		// walking: dry, wading (24), swimming level (192 deep, mid-water): 35 tics of the walk key
		static const int wd[] = { -1, 24, 192 };
		static const string wn[] = { "dry", "wading24", "swimming" };
		for (int i = 0; i < 3; i++)
		{
			if (At()) { SetW(TA, wd[i]); Pose(mo, 80, 200, 0, i == 2 ? 100 : -1e9); p0 = mo.pos; }
			if (Seg(35)) Keys(WALKKEY);
			if (At()) { Keys(); Info(String.Format("walk key 35 tics %s: %.1f along, %.1f up; waterlevel %d", wn[i], mo.pos.x - p0.x, mo.pos.z - p0.z, mo.waterlevel)); }
		}
		// mid-water with no keys: sinks or floats?
		if (At()) { SetW(TA, 192); Pose(mo, 256, 200, 0, 100); p0 = mo.pos; }
		Seg(70);
		if (At()) Check("swim_noKeys_sinks", mo.pos.z < p0.z - 4, String.Format("in 2 s from z 100: z %.1f, vel z %.2f, waterlevel %d", mo.pos.z, mo.vel.z, mo.waterlevel));
		// up: the jump key (the level is nojump), the look up and forward, the fly-up key
		if (At()) { Pose(mo, 256, 200, 0); p0 = mo.pos; }
		if (Seg(35)) Keys(0, 0, 0, BT_JUMP);
		if (At()) { Keys(); Check("swim_upByTheJumpKey", mo.pos.z > p0.z + 60, String.Format("35 tics from the floor: z %.1f (vel z %.2f)", mo.pos.z, mo.vel.z)); }
		if (At()) { Pose(mo, 120, 200, 0, -1e9, -45); p0 = mo.pos; }
		if (Seg(35)) { Keys(WALKKEY); mo.pitch = -45; }
		if (At()) { Keys(); Check("swim_upByLookingUp", mo.pos.z > p0.z + 30, String.Format("35 tics of the walk key looking 45 up: z %.1f, %.1f along", mo.pos.z, mo.pos.x - p0.x)); mo.pitch = 0; }
		if (At()) { Pose(mo, 256, 200, 0); p0 = mo.pos; }
		if (Seg(35)) Keys(0, 0, 256);
		if (At()) { Keys(); Info(String.Format("fly-up key (upmove 256) 35 tics: z %.1f", mo.pos.z)); }
		// rising water: BLUE in 102 fills A to 224; the player stands by the ledge with no keys
		if (At()) { B(TA).held = false; SetW(TA, -1); HangIn(blue, 102); Pose(mo, 420, 256, 0); best = 0; }
		if (Seg(1050)) { best = max(best, mo.pos.z); if (tt % 105 == 0) Info(String.Format("rising t+%.0fs: water %.1f, player z %.1f, waterlevel %d", tt / 35., W(TA), mo.pos.z, mo.waterlevel)); }
		if (At()) Check("risingWater_doesNotLiftThePlayer", best < 8, String.Format("water %.1f; the player rose at most to z %.1f", W(TA), best));
		// climbing out onto the ledge (208) from the surface: jump and walk keys, the water some way under the ledge
		static const int below[] = { 8, 24, 40, 56 };
		for (int i = 0; i < 4; i++)
		{
			if (At()) { AllDown(); SetW(TA, 208 - below[i]); B(TA).held = true; Pose(mo, 420, 256, 0, 208 - below[i] - 40); }
			if (Seg(105)) Keys(WALKKEY, 0, 0, BT_JUMP);
			if (At()) { Keys(); Info(String.Format("climb out, the water %d under the ledge: x %.1f z %.1f (on the ledge: %d)", below[i], mo.pos.x, mo.pos.z, mo.pos.x > 452 && mo.pos.z > 207)); }
			if (i == 0 && At()) Check("climbOut_8underTheLedge", mo.pos.x > 452 && mo.pos.z > 207, String.Format("x %.1f z %.1f", mo.pos.x, mo.pos.z));
		}
		if (At()) { SetW(TA, 200); Pose(mo, 420, 256, 0, 160, -30); }
		if (Seg(105)) { Keys(WALKKEY); mo.pitch = -30; }
		if (At()) { Keys(); mo.pitch = 0; Info(String.Format("climb out by looking up and walking, the water 8 under the ledge: x %.1f z %.1f (on the ledge: %d)", mo.pos.x, mo.pos.z, mo.pos.x > 452 && mo.pos.z > 207)); }
		// through BLUE under water, both ways (A and R at 96)
		if (At()) { AllDown(); SetW(TA, 96); HangIn(blue, 101); Pose(mo, 120, 64, 180, 20); p0 = mo.pos; }
		if (Seg(50)) Keys(WALKKEY);
		if (At())
		{
			Keys();
			Check("swim_throughBlue_intoR", wh.BasinAt(mo.pos.xy) == B(TR) && mo.waterlevel == 3,
				String.Format("from (120,64,20): at (%.1f,%.1f,%.1f), angle %.0f, waterlevel %d", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, mo.waterlevel));
			mo.angle += 180;
		}
		if (Seg(50)) Keys(WALKKEY);
		if (At())
		{
			Keys();
			Check("swim_throughBlue_backToA", wh.BasinAt(mo.pos.xy) == B(TA) && mo.waterlevel == 3,
				String.Format("at (%.1f,%.1f,%.1f), angle %.0f, waterlevel %d", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, mo.waterlevel));
		}
		// USE under water, with the use key: take BLUE out of 101 and hang it again
		if (At()) { SetW(TA, 96); B(TA).held = true; HangIn(blue, 101); Pose(mo, 40, 64, 180, 10); }
		if (Seg(3)) { if (tt == 1) Keys(0, 0, 0, BT_USE); else Keys(); }
		if (At()) Check("useUnderWater_takes", h.carried == blue && mo.waterlevel == 3, String.Format("carried %s, waterlevel %d", h.carried ? h.carried.Label() : "nothing", mo.waterlevel));
		if (Seg(3)) { if (tt == 1) Keys(0, 0, 0, BT_USE); else Keys(); }
		if (At()) Check("useUnderWater_hangs", !h.carried && h.FindFrame(101).door == blue && mo.waterlevel == 3, String.Format("carried %s, 101 holds %s", h.carried ? h.carried.Label() : "nothing", h.FindFrame(101).door ? h.FindFrame(101).door.Label() : "nothing"));
		// air and drowning (the engine's own, not changed): under water without god mode
		if (At()) { B(TA).held = true; SetW(TA, 192); Pose(mo, 256, 200, 0); mo.player.cheats &= ~CF_GODMODE; mo.A_SetHealth(100); phase = 0; best = 0; Info(String.Format("under: air finished in %d tics", mo.player.air_finished - level.maptime)); }
		if (Seg(1000))
		{
			mo.vel.z = 0;
			if (mo.health < 100 - best) { phase++; Info(String.Format("drowning: hurt %d at %.1f s under (health %d)", int(100 - best - mo.health), tt / 35., mo.health)); best = 100 - mo.health; }
		}
		if (At()) { Check("drowning_engineDefault", phase > 0, String.Format("%d hurts in %.1f s under water, health %d", phase, 1000 / 35., mo.health)); mo.player.cheats |= CF_GODMODE; mo.A_SetHealth(100); }
		// the real keys: tools/smoke_WATER_4.cfg holds +jump for 35 tics, then presses +use; the script waits for each
		if (At()) { SetW(TA, 192); B(TA).held = true; Pose(mo, 256, 200, 0); phase = 0; Info("waiting for the real jump key"); }
		if (Seg(700))
		{
			bool jump = (mo.player.original_cmd.buttons & BT_JUMP) != 0, use = (mo.player.original_cmd.buttons & BT_USE) != 0;
			if (phase == 0 && !jump) Pose(mo, 256, 200, 0);
			else if (phase == 0) { phase = 1; reachAt = tt; p0 = mo.pos; }
			else if (phase == 1 && tt == reachAt + 35)
			{
				Check("realKey_jumpSwimsUp", mo.pos.z > p0.z + 60, String.Format("the jump key held 35 tics from the floor under water: z %.1f (level nojump)", mo.pos.z));
				SetW(TA, 96); HangIn(blue, 101); phase = 2;
			}
			if (phase == 2 && !use) Pose(mo, 40, 64, 180, 10);
			else if (phase == 2) { phase = 3; reachAt = tt; }
			else if (phase == 3 && tt == reachAt + 5)
			{
				Check("realKey_useTakesUnderWater", h.carried == blue && mo.waterlevel == 3, String.Format("carried %s, waterlevel %d", h.carried ? h.carried.Label() : "nothing", mo.waterlevel));
				phase = 4;
			}
		}
		if (At()) { if (phase < 4) Check("realKeys_came", false, String.Format("phase %d", phase)); B(TA).held = false; }
	}

	// --- MODE=5: shots across, into, out of and under the water, and through a door under it (D) ----------
	WaterDummy dummy;
	int hb, hf, hr;
	Actor flying;
	double aimPit;
	Vector3 flyingWas;
	string flyingState;
	void Follow()
	{
		if (flying && flying.health > -9999)
		{
			string st = flying.InStateSequence(flying.CurState, flying.FindState("Death")) ? "exploding" : "flying";
			if (st != flyingState) Info(String.Format("%s %s at (%.1f,%.1f,%.1f) waterlevel %d", flying.GetClassName(), st, flying.pos.x, flying.pos.y, flying.pos.z, flying.waterlevel));
			flyingState = st;
			flyingWas = flying.pos;
		}
		else if (flyingState != "") { Info(String.Format("missile gone after (%.1f,%.1f,%.1f)", flyingWas.x, flyingWas.y, flyingWas.z)); flyingState = ""; }
	}
	void Fire(Actor mo, string what, Vector3 at, double ang, double pit)
	{
		double oz = mo.height * 0.5 - mo.floorclip + PlayerPawn(mo).AttackZOffset;
		Vector3 from = mo.pos + (0, 0, oz);
		if (what == "bullet") { mo.LineAttack(ang, 4096, pit, 10, 'Hitscan', "BulletPuff"); return; }
		let m = Actor.Spawn(what, from, ALLOW_REPLACE);
		flying = m;
		m.target = mo;
		m.angle = ang;
		m.pitch = pit;
		m.Vel3DFromAngle(m.speed, ang, pit);
	}
	void Shot(Actor mo, string name, Vector3 pos, double ang, double pit, Vector3 dpos, int air)
	{
		if (At())
		{
			AllDown(); SetW(TA, air ? -1 : 96); B(TA).held = true; HangIn(blue, 101);
			Pose(mo, pos.x, pos.y, ang, pos.z);
			if (dummy) dummy.Destroy();
			dummy = WaterDummy(Actor.Spawn("WaterDummy", dpos));
			if (ang > 999)          // aim at the dummy's middle
			{
				double oz = mo.height * 0.5 - mo.floorclip + PlayerPawn(mo).AttackZOffset;
				Vector3 d = dpos + (0, 0, 28) - (mo.pos + (0, 0, oz));
				ang = VectorAngle(d.x, d.y);
				pit = -atan2(d.z, d.xy.Length());
			}
			mo.angle = ang;
			aimPit = pit;
			Fire(mo, "bullet", pos, ang, pit);
		}
		Seg(5);
		if (At()) { hb = dummy.hits; Fire(mo, "DoomImpBall", pos, mo.angle, aimPit); }
		if (Seg(120)) Pose(mo, pos.x, pos.y, mo.angle, pos.z);
		if (At()) { hf = dummy.hits - hb; Fire(mo, "Rocket", pos, mo.angle, aimPit); }
		if (Seg(80)) Pose(mo, pos.x, pos.y, mo.angle, pos.z);
		if (At())
		{
			hr = dummy.hits - hb - hf;
			Check(name, hb > 0 && hf > 0 && hr > 0, String.Format("bullet %d, fireball %d, rocket %d (by: %s); dummy waterlevel %d", hb, hf, hr, dummy.by, dummy.waterlevel));
		}
	}
	void Shots(Actor mo)
	{
		if (At()) mo.player.cheats |= CF_GODMODE;
		mo.bNoGravity = true;
		Follow();
		Shot(mo, "shot_acrossTheSurface", (150, 450, 128), 1000, 0, (400, 100, 136), 0);
		Shot(mo, "shot_intoTheWater", (150, 450, 128), 1000, 0, (300, 150, 10), 0);
		Shot(mo, "shot_outOfTheWater", (300, 100, 0), 1000, 0, (300, 470, 150), 0);
		Shot(mo, "shot_underWater", (100, 300, 0), 1000, 0, (400, 300, 10), 0);
		Shot(mo, "shot_throughBlueUnderWater", (200, 64, 0), 180, 0, (-700, 0, 0), 0);
		Shot(mo, "shot_fromDryThroughBlueIntoWater", (200, 64, 0), 180, 0, (-700, 0, 0), 1);
		if (At()) { mo.bNoGravity = false; B(TA).held = false; }
	}

	// --- MODE=6: company (D, E): monsters in a cell that floods -------------------------------------
	Array<Actor> mons;
	Array<int> diedAt;
	Actor pushed;
	void Company(Actor mo)
	{
		if (At())
		{
			mo.player.cheats |= CF_GODMODE;
			Pose(mo, 3460, -170, 90);
			AllDown();
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0) { mons.Push(a); diedAt.Push(-1); a.target = mo; a.SetState(a.SeeState); }
			Info(String.Format("monsters in the cell: %d, woken and after the player; the drowning rule %s", mons.Size(), wh.bDrown ? "on" : "off"));
			HangIn(blue, 110);
		}
		if (Seg(1050))
		{
			for (int i = 0; i < mons.Size(); i++) if (diedAt[i] < 0 && (!mons[i] || mons[i].health <= 0)) diedAt[i] = tt;
			if (tt % 70 == 0)
			{
				string s = String.Format("company t+%.0fs: K %.1f deep;", tt / 35., D(TK));
				for (int i = 0; i < mons.Size(); i++) if (mons[i])
					s = s .. String.Format(" %s (%.0f,%.0f,%.0f) wl %d hp %d under %d %s;", mons[i].GetClassName(), mons[i].pos.x, mons[i].pos.y, mons[i].pos.z,
						mons[i].waterlevel, mons[i].health, wh.UnderFor(mons[i]), wh.BasinAt(mons[i].pos.xy) == B(TR) ? "IN R" : "");
				Info(s);
			}
		}
		if (At())
		{
			int walkersDead = 0, walkers = 0, flyersAlive = 0, flyers = 0;
			string s = "";
			for (int i = 0; i < mons.Size(); i++)
			{
				let a = mons[i];
				bool flyer = a && (a.bFloat || a.bNoGravity);
				if (flyer) { flyers++; if (a.health > 0) flyersAlive++; }
				else { walkers++; if (!a || a.health <= 0) walkersDead++; }
				s = s .. String.Format("%s %s%s; ", a ? a.GetClassName() .. "" : "gone", diedAt[i] >= 0 ? String.Format("dead after %.1f s", diedAt[i] / 35.) : "alive",
					a && wh.BasinAt(a.pos.xy) == B(TR) ? " (in R)" : "");
			}
			Check("drowning_walkersDrown", walkers > 0 && walkersDead == walkers, s);
			Check("drowning_flyersDoNot", flyers > 0 && flyersAlive == flyers, String.Format("%d of %d flying monsters alive", flyersAlive, flyers));
		}
		// a monster pushed through BLUE under water (K into R); the rule off: it lives, on: it drowns
		if (At())
		{
			wh.bDrown = false;
			pushed = Actor.Spawn("DoomImp", (3400, 192, 0));
			pushed.angle = 180;
			pushed.bNoTarget = true;
		}
		if (Seg(40)) { pushed.vel.xy = (-6, 0); }
		if (At()) Check("monster_throughBlueUnderWater", wh.BasinAt(pushed.pos.xy) == B(TR),
			String.Format("imp at (%.1f,%.1f,%.1f), waterlevel %d", pushed.pos.x, pushed.pos.y, pushed.pos.z, pushed.waterlevel));
		Seg(280);
		if (At()) { Check("drowning_ruleOff_lives", pushed.health > 0, String.Format("health %d after 8 s, waterlevel %d", pushed.health, pushed.waterlevel)); wh.bDrown = true; }
		Seg(315);
		if (At()) Check("drowning_ruleOn_drowns", pushed.health <= 0, String.Format("health %d 9 s after the rule was turned on", pushed.health));
		if (At()) HangIn(green, 110);
		Approach(TK, 0, 700, "company_drainedByGreen");
	}

	// --- MODE=8: a raft (F) -------------------------------------------------------------------------
	AjarRaft raft;
	Vector3 r0;
	int ridden;
	void Rafting(Actor mo)
	{
		if (!raft) raft = AjarRaft(ThinkerIterator.Create("AjarRaft").Next());
		if (At()) { mo.player.cheats |= CF_GODMODE; AllDown(); SetW(TA, -1); raft.SetOrigin((150, 64, 0), false); HangIn(blue, 101); HangIn(green, 103); }
		Seg(140);
		if (At())
		{
			Check("raft_floats", raft.afloat && abs(raft.pos.z + raft.height / 2 - W(TA)) < 0.01,
				String.Format("water %.2f, raft from %.2f to %.2f", W(TA), raft.pos.z, raft.pos.z + raft.height));
			r0 = raft.pos;
			Pose(mo, raft.pos.x, raft.pos.y, 0, raft.pos.z + raft.height);
			raft.riders = 0;
		}
		if (Seg(1050) && tt % 70 == 0) Info(String.Format("raft t+%.0fs: at (%.1f,%.1f,%.1f) %s, current (%.2f,%.2f); player (%.1f,%.1f,%.1f); in %s",
			tt / 35., raft.pos.x, raft.pos.y, raft.pos.z, raft.afloat ? "afloat" : "aground", raft.current.x, raft.current.y, mo.pos.x, mo.pos.y, mo.pos.z,
			wh.BasinAt(raft.pos.xy) == B(TO) ? "O" : wh.BasinAt(raft.pos.xy) == B(TA) ? "A" : "?"));
		if (At())
		{
			Check("raft_carriedOutByTheOutfallDoor", wh.BasinAt(raft.pos.xy) == B(TO),
				String.Format("from (%.0f,%.0f) to (%.1f,%.1f,%.1f); %d tics with the player on it", r0.x, r0.y, raft.pos.x, raft.pos.y, raft.pos.z, raft.riders));
			Check("raft_thePlayerRode", raft.riders > 30 && wh.BasinAt(mo.pos.xy) == B(TO) && abs(mo.pos.z - (raft.pos.z + raft.height)) < 1,
				String.Format("player at (%.1f,%.1f,%.1f), on the raft (top %.1f) on the far side", mo.pos.x, mo.pos.y, mo.pos.z, raft.pos.z + raft.height));
		}
		// deep: BLUE on the gallery, GREEN at the floor (96 deep): carried to the wall over GREEN's lintel
		if (At()) { AllDown(); SetW(TA, 96); HangIn(blue, 102); HangIn(green, 103); raft.SetOrigin((150, 64, 92), false); Pose(mo, 100, 400, 0, 128); }
		if (Seg(700) && tt % 70 == 0) Info(String.Format("raft deep t+%.0fs: at (%.1f,%.1f,%.1f) %s; water %.2f", tt / 35., raft.pos.x, raft.pos.y, raft.pos.z, raft.afloat ? "afloat" : "aground", W(TA)));
		if (At()) Check("raft_deep_heldByTheWallOverTheDoor", raft.afloat && wh.BasinAt(raft.pos.xy) == B(TA) && raft.pos.x > 470,
			String.Format("at (%.1f,%.1f,%.1f); the lintel of 103 at 96", raft.pos.x, raft.pos.y, raft.pos.z));
	}

	// --- MODE=7: views (tools/smoke_WATER_7.cfg shoots at about 50 + 70 n) ---------------------------
	// Each view is 70 tics: st 0 sets the scene, the player is posed from st 2 on and hovers (no
	// gravity). A scene "in passing" lets the water run for `run` tics and then holds both basins
	// where they are, so that the shot, whenever it falls, shows that moment.
	void Look(Actor mo, int st, double x, double y, double z, double ang, double pitch = 0)
	{
		if (st >= 2) Pose(mo, x, y, ang, z, pitch);
	}
	void Scene(int st, int run, int t1, int t2 = 0)
	{
		if (st == 0) { for (int i = 0; i < wh.basins.Size(); i++) wh.basins[i].held = false; }
		if (st == run) { B(t1).held = true; if (t2) B(t2).held = true; }
	}

	void Views(Actor mo)
	{
		int i = (tic - 2) / 70, st = (tic - 2) % 70;
		mo.bNoGravity = true;
		mo.player.cheats |= CF_GODMODE;
		if (st == 0) Console.Printf("AJARTEST view=%d t=%d", i, tic);
		if (st == 40) Info(String.Format("view %d: player (%.1f,%.1f,%.1f) eye %.1f waterlevel %d; %s", i, mo.pos.x, mo.pos.y, mo.pos.z,
			mo.pos.z + mo.player.viewheight, mo.waterlevel, Levels()));
		switch (i)
		{
		case 0:     // dry side into a room with water: A held dry, BLUE in 101, R beyond (96 over the sill)
			if (st == 0) { AllDown(); SetW(TA, -1); HangIn(blue, 101); }
			Scene(st, 0, TA);
			Look(mo, st, 140, 64, 0, 180, 5);
			break;
		case 1:     // the same, at the door
			Scene(st, 0, TA);
			Look(mo, st, 50, 40, 0, 170, 15);
			break;
		case 2:     // both sides 48 over the sill: B and C by the TEAL pair (C 192 higher), from B
			if (st == 0) { AllDown(); SetW(TB, 48); SetW(TC, 48); HangIn(Leaf(8, 0), 104); HangIn(Leaf(8, 1), 106); }
			Look(mo, st, 1056, 400, 50, 90, 20);
			break;
		case 3:     // the same from C
			Look(mo, st, 1756, 400, 242, 90, 20);
			break;
		case 4:     // depths differ: B 80 and C 16 over their sills, the pair hung, held after 20 tics; from B
			if (st == 0) { AllDown(); SetW(TB, 80); SetW(TC, 16); HangIn(Leaf(8, 0), 104); HangIn(Leaf(8, 1), 106); }
			Scene(st, 20, TB, TC);
			Look(mo, st, 1090, 420, 50, 100, 20);
			break;
		case 5:     // the same moment from C
			if (st == 0) { AllDown(); SetW(TB, 80); SetW(TC, 16); HangIn(Leaf(8, 0), 104); HangIn(Leaf(8, 1), 106); }
			Scene(st, 20, TB, TC);
			Look(mo, st, 1790, 420, 242, 100, 20);
			break;
		case 6:     // under water: A at 96 by BLUE in 101, the eye at 51, into 101
			if (st == 0) { AllDown(); SetW(TA, 96); HangIn(blue, 101); }
			Look(mo, st, 140, 64, 10, 180, 0);
			break;
		case 7:     // under water at the door
			Look(mo, st, 50, 40, 10, 170, 5);
			break;
		case 8:     // under water, looking up at the surface
			Look(mo, st, 250, 200, 10, 180, -60);
			break;
		case 9:     // two real heights: BLUE in 102 on the gallery (128 up), A 52 over the gallery, R 96 over its sill
			if (st == 0) { AllDown(); SetW(TA, 180); HangIn(blue, 102); }
			Scene(st, 0, TA);
			Look(mo, st, 192, 420, 160, 90, 20);
			break;
		case 10:    // the reservoir through the corridor's glass
			if (st == 0) AllDown();
			Look(mo, st, -700, -250, 0, 90, 0);
			break;
		case 11:    // the circle running: L's foot and U's head joined by the ORANGE pair; the chute and its wheel from L
			if (st == 0) { AllDown(); SetW(TL, 64); SetW(TU, 32); HangIn(Leaf(9, 0), 107); HangIn(Leaf(9, 1), 108); }
			Look(mo, st, 2556, 300, 100, 90, 15);
			break;
		case 12:    // the cell flooded by BLUE in 110, through the armoured glass
			if (st == 0) { AllDown(); SetW(TK, 96); HangIn(blue, 110); }
			Look(mo, st, 3460, -170, 0, 90, 0);
			break;
		case 13:    // a dry room's frame onto the outfall: GREEN in 103, A dry
			if (st == 0) { AllDown(); SetW(TA, -1); HangIn(green, 103); }
			Look(mo, st, 380, 64, 0, 0, 5);
			break;
		}
		if (tic == 2 + 70 * 14) Console.Printf("AJARTEST viewsDone=1");
	}
}
