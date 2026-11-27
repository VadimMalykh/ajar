// The kennel lab's checks and measurements (map KENNEL, tools/map_kennel.py;
// kennel.zs, then.zs; PLAN.md, "The kennel lab"). MAP=KENNEL MODE=n tools/smoke.sh.
// THEN is NOW + (0, -4096). The run x 0..768, y 0..256; pens north of it,
// y 272..528, middles x 120, 376, 632 (pen 2 a stall: x 336..416, y 336..528,
// its gate y 320..336, ledges at 48 x 272..336 and 416..480, a megasphere on
// the west one and a soul sphere on the east one); the passage y 544..672 and its east leg
// x 784..896; the turnstile x 768..784, y 96..160. Frame 101 NOW / 121 THEN in
// the run's west wall. Gate causes 21..23 (THEN), the opening between pens 2
// and 3 cause 24.
//   1 the scales; 2 the step; 3 the hatch as bait, and the turnstile;
//   4 raised from the dead; 5 two pens set on each other (measured only);
//   6 views (tools/smoke_KENNEL_6.cfg shoots every 70 tics); 7 a probe of
//   monsters following through the clocked door (measured only).

class KennelTest : EventHandler
{
	const OFF = -4096;
	const WALKKEY = 0x1900;
	const PASS_Y = 562;        // the player at a hatch, in the passage
	int tic, sn, step, st;
	bool moved, finished;
	int checks, fails;
	AjarHandler h;
	AjarThenHandler th;
	AjarKennel kh;
	AjarDoor clocked, shadow;
	Array<AjarKennelScales> scales;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "KENNEL"; }

	// --- steps: each runs until it calls Next() ---------------------------------------------------
	bool S() { return sn++ == step && !moved; }
	void Next() { step++; st = -1; moved = true; }
	void JumpTo(int s) { step = s; st = -1; moved = true; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	// --- the place ----------------------------------------------------------------------------------
	static int Mid(int n) { return n == 0 ? 120 : n == 1 ? 376 : 632; }
	static int PenX1(int n) { return n == 0 ? 0 : n == 1 ? 336 : 512; }
	static int PenX2(int n) { return n == 1 ? 416 : PenX1(n) + 240; }
	static int PenY1(int n) { return n == 1 ? 336 : 272; }           // the pen's mouth (pen 2, the stall: behind its gate)
	static double MouthY(int n) { return 528; }                      // the hatch's mouth on the pen's side
	static double GateY(int n) { return n == 1 ? 328 : 264; }
	bool InThen(Actor a) { return th.when.InThen(a.pos.xy); }
	double NowY(Actor a) { return InThen(a) ? a.pos.y - OFF : a.pos.y; }
	bool InPen(Actor a, int n)
	{
		double y = NowY(a);
		return a.pos.x > PenX1(n) && a.pos.x < PenX2(n) && y > PenY1(n) + a.radius - 1 && y < 528;
	}
	double FromMouth(Actor a, int n) { return (a.pos.xy - (Mid(n), MouthY(n) + (InThen(a) ? OFF : 0))).Length(); }
	string Where(Actor a) { return a ? String.Format("(%.1f,%.1f,%.1f) %s", a.pos.x, NowY(a), a.pos.z, InThen(a) ? "THEN" : "NOW") : "(gone)"; }
	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }
	double CZ(double x, double y) { Sector s = level.PointInSector((x, y)); return s.ceilingplane.ZatPoint(s.centerspot); }
	double GateZ(int n) { return CZ(Mid(n), GateY(n) + OFF); }
	AjarFrame F(int id) { return h.FindFrame(id); }
	AjarThenCause Gate(int n) { return th.FindCause(21 + n); }

	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = false;
		Keys();
	}

	// --- the player's controls (as thentest.zs) ------------------------------------------------------
	int fwd;
	uint btn;
	Vector2 walkGoal;
	bool walking;
	void Keys(int f = 0, uint b = 0) { fwd = f; btn = b; }
	void WalkTo(double x, double y) { walkGoal = (x, y); walking = true; }
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp) return;
		if (walking)
		{
			Vector2 d = walkGoal - mo.pos.xy;
			if (d.Length() < 6) { walking = false; Keys(); mo.vel.xy = (0, 0); }       // stopped dead at the goal (a player would slide on)
			else { mo.angle = VectorAngle(d.x, d.y); fwd = WALKKEY; }
		}
		if (!(fwd || btn)) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.buttons = btn;
		pp.HandleMovement();
	}
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}
	// one step: walk to x, y (NOW's coordinates; then: at THEN), until there or `limit` tics
	void Walk(Actor mo, double x, double y, bool then = false, int limit = 400)
	{
		if (!S()) return;
		if (then) y += OFF;
		if (st == 0) WalkTo(x, y);
		if (!walking || st >= limit)
		{
			if (walking) Info(String.Format("walk to (%.0f,%.0f) stopped at %s after %d tics", x, y, Where(mo), st));
			walking = false;
			Keys();
			Next();
		}
	}
	// one step: stand still for n tics
	void Wait(int n) { if (S() && st >= n - 1) Next(); }
	// one step: through the clocked door in the run's west wall, from either time
	void ThroughDoor(Actor mo, bool fromThen)
	{
		if (!S()) return;
		if (st == 0) { Pose(mo, 40, 128 + (fromThen ? OFF : 0), 180); Keys(WALKKEY); }
		if (st == 23) { Keys(); Next(); }
	}
	void Shoot(Actor mo, Actor at, int damage = 10)
	{
		Vector2 d = at.pos.xy - mo.pos.xy;
		mo.angle = VectorAngle(d.x, d.y);
		mo.pitch = 0;
		mo.LineAttack(mo.angle, 4096, 0, damage, 'Hitscan', "BulletPuff");
	}

	// --- monsters ---------------------------------------------------------------------------------
	Actor SpawnAt(class<Actor> cls, double x, double y, bool then, double ang = 90)
	{
		if (then) y += OFF;
		let a = Actor.Spawn(cls, (x, y, FloorAt((x, y))));
		if (a) { a.angle = ang; a.bAmbush = false; }
		return a;
	}
	// put a monster in the run THEN, after the player, with no door in its head (AjarSense forgets its door)
	void Bring(Actor a, Actor mo, double x, double y)
	{
		a.SetOrigin((x, y + OFF, FloorAt((x, y + OFF))), false);
		a.ClearInterpolation();
		let sense = AjarSense(a.FindInventory("AjarSense"));
		if (sense) { sense.via = null; sense.Unmute(); if (sense.lure) sense.lure.Destroy(); }
		a.target = mo;
		a.movedir = 0;
		a.movecount = 0;
	}
	void Wake(Actor a, Actor mo) { if (!a) return; a.bAmbush = false; a.target = mo; a.movecount = 0; a.SetState(a.SeeState); }
	void ClearNowMonsters(Actor keep = null)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		Array<Actor> gone;
		while (a = Actor(it.Next())) if (a.bIsMonster && a != keep) gone.Push(a);
		for (int i = 0; i < gone.Size(); i++) gone[i].Destroy();
	}
	Actor ItemNear(class<Actor> cls, double x, double y)
	{
		let it = ThinkerIterator.Create(cls);
		Actor a;
		while (a = Actor(it.Next())) if ((a.pos.xy - (x, y)).Length() < 32) return a;
		return null;
	}
	Actor FirstNow(class<Actor> cls)
	{
		let it = ThinkerIterator.Create(cls);
		Actor a;
		while (a = Actor(it.Next())) if (a.GetClass() == cls && !InThen(a) && a.health > 0) return a;
		return null;
	}
	void SetGate(int cause, int n)
	{
		let c = th.FindCause(cause);
		if (!c) return;
		th.SetCause(c, n, null);
		th.Snap(c);
	}

	// --- bones ------------------------------------------------------------------------------------
	AjarThenCorpse BonesOf(Actor a, bool forGood)
	{
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && c.who == a && (c.of == null) == forGood) return c;
		}
		return null;
	}
	int CountBones(Actor a)
	{
		int n = 0;
		for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && !th.corpses[i].bDestroyed && th.corpses[i].who == a) n++;
		return n;
	}
	int StandIns()
	{
		int n = 0;
		for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && !th.corpses[i].bDestroyed && th.corpses[i].of) n++;
		return n;
	}
	string Readout(AjarKennelScales s)
	{
		string r = "";
		for (int i = 0; i < s.digits.Size(); i++)
		{
			int f = s.digits[i].frame;
			r = r .. (f == 10 ? " " : String.Format("%d", f % 11));
		}
		return r .. (s.digits.Size() && s.digits[s.digits.Size() - 1].frame >= 11 ? " green" : " amber");
	}
	bool Reads(AjarKennelScales s, int w)
	{
		string want = String.Format("%4d", w) .. (w >= s.Threshold() ? " green" : " amber");
		return s.weight == w && Readout(s) == want;
	}
	string ScaleInfo(AjarKennelScales s)
	{
		return String.Format("weight %d, reads '%s', shutter %.1f%s", s.weight, Readout(s), s.shutter ? s.CeilZ() : -1, s.held ? " (held)" : "");
	}
	AjarKennelStep StepOf(AjarThenCorpse c) { return kh && c ? kh.StepOf(c) : null; }
	void HangNow() { if (h.carried == clocked) h.carried = null; else if (clocked.frame) return; h.Hang(clocked, F(101)); }
	void UnhangNow() { if (clocked.frame) h.carried = h.Unhang(clocked.frame); }

	// --- damage, counted for the measurements ---------------------------------------------------------
	Actor watch, other;
	int onPlayerMissile, onPlayerMelee, onWatchByPlayer, watchByOther, otherByWatch, watchDmgByOther, otherDmgByWatch;
	override void WorldThingDamaged(WorldEvent e)
	{
		if (!Testing() || !e.thing) return;
		if (e.thing.player && watch && e.damageSource == watch)
		{
			if (e.inflictor == watch) onPlayerMelee++;
			else onPlayerMissile++;
		}
		if (watch && e.thing == watch && e.damageSource && e.damageSource.player) onWatchByPlayer++;
		if (watch && other && e.thing == watch && e.damageSource == other) { watchByOther++; watchDmgByOther += e.damage; }
		if (watch && other && e.thing == other && e.damageSource == watch) { otherByWatch++; otherDmgByWatch += e.damage; }
	}
	void ResetCounts() { onPlayerMissile = onPlayerMelee = onWatchByPlayer = watchByOther = otherByWatch = watchDmgByOther = otherDmgByWatch = 0; }

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		tic++;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (tic == 1)
		{
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			kh = AjarKennel.Get();
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.IsShadow()) shadow = d;
				else if (d.IsClocked()) clocked = d;
			}
			for (int n = 0; n < 3; n++) scales.Push(AjarKennelScales.OfTag(81 + n));
			mo.player.cheats |= CF_GODMODE;
			Info(String.Format("causes %d, cause sectors %d; clocked %d shadow %d; scales %d %d %d; shift (%.0f,%.0f)",
				th.causes.Size(), th.secIdx.Size(), clocked != null, shadow != null, scales[0] != null, scales[1] != null, scales[2] != null,
				th.when.args[0], th.when.args[1]));
		}
		moved = false;
		sn = 0;
		if (tic > 2 && !finished)
		{
			if (mode == 1) ScalesMode(mo);
			else if (mode == 2) StepMode(mo);
			else if (mode == 3) Hatch(mo);
			else if (mode == 4) Raised(mo);
			else if (mode == 5) SetOn(mo);
			else if (mode == 6) Views(mo);
			else if (mode == 7) FollowProbe(mo);
			if (S())
			{
				finished = true;
				if (mode == 6) Console.Printf("AJARTEST kennelViews=1");
				else Console.Printf("AJARTEST kennelDone=1 checks=%d failed=%d", checks, fails);
			}
		}
		Drive(mo);
		st++;
	}

	// === MODE=1 and 2: lead a monster into THEN, pen it, take the door down ===========================
	Actor dog;
	bool followed;
	int penN, mark, enteredAt;
	Vector2 dogThen;
	AjarThenCorpse bones;
	Actor sphere;
	int unhungAt;

	// The common first part: wake `dog` NOW, hang the clocked door in 101, lead it into THEN, through the
	// turnstile to pen n's hatch; it comes into the pen; the lever shuts the gate; back to NOW; the door
	// taken down there (by a real USE). `steer`: once it is in, the player stands that far west of the
	// hatch for a while.
	void LeadAndPen(Actor mo, int n, double steer = 0)
	{
		int mid = Mid(n);
		if (S())
		{
			Check("dogThere", dog != null, dog ? dog.GetClassName() .. " " .. Where(dog) : "none");
			for (int k = 0; k < 3; k++) if (k != n) SetGate(21 + k, 0);
			Check("onlyItsGateOpen", Gate(n).setting == 1 && GateZ(n) > 100 && GateZ((n + 1) % 3) < 1 && GateZ((n + 2) % 3) < 1,
				String.Format("gates %.0f %.0f %.0f", GateZ(0), GateZ(1), GateZ(2)));
			clocked.Used(mo);
			Pose(mo, 40, 128, 180);
			Next();
		}
		if (S()) { PressUse(mo); Next(); }
		if (S()) { Check("hungIn101", clocked.frame == F(101) && shadow.frame == F(121), h.said); Wake(dog, mo); Next(); }
		// wait for it to come near, then through the door
		if (S())
		{
			double d = (dog.pos.xy - mo.pos.xy).Length();
			if (d < 200 || st >= 400) { Info(String.Format("%s came within %.0f after %d tics", dog.GetClassName(), d, st)); Next(); }
		}
		ThroughDoor(mo, false);
		if (S()) { Check("playerThen", InThen(mo), Where(mo)); Next(); }
		Walk(mo, 300, 128, true);
		// it is through when it stands THEN clear of the frame's recess (x 48 on) for 35 tics
		if (S())
		{
			if (st == 0) mark = 0;
			if (st % 10 == 0 && st < 200) Info(String.Format("following t+%d: %s", st, Where(dog)));
			mark = InThen(dog) && dog.pos.x > 48 ? mark + 1 : 0;
			if (mark >= 35 || st >= 400)
			{
				bool came = mark >= 35;
				Info(String.Format("%s %s into the run THEN through the clocked door by itself (%d tics); at %s", dog.GetClassName(), came ? "came" : "did NOT come", st, Where(dog)));
				followed = came;
				if (!came) { Bring(dog, mo, 200, 128); Info("brought into the run THEN by the script"); }
				Next();
			}
		}
		Walk(mo, 740, 128, true);
		Walk(mo, 840, 128, true);
		if (S()) { Check("throughTurnstileThen", mo.pos.x > 790 && InThen(mo), Where(mo)); Next(); }
		Walk(mo, 840, 608, true);
		Walk(mo, mid, 608, true);
		Walk(mo, mid, PASS_Y, true);
		// at the hatch: it comes into the pen
		if (S())
		{
			if (st == 0) { mo.angle = 270; enteredAt = -1; mark = tic; }
			if (enteredAt < 0 && InPen(dog, n)) enteredAt = st;
			if (st % 70 == 0) Info(String.Format("t+%d %s %s", st, dog.GetClassName(), Where(dog)));
			if ((enteredAt >= 0 && st >= enteredAt + 105) || st >= 1050)
			{
				// a measure, not a promise (MODE=3 counts it): one that has not come in is put in by the script
				bool came = InPen(dog, n);
				Info(String.Format("%s %s pen %d by itself: in after %d tics; at %s, %.0f from the hatch", dog.GetClassName(), came ? "came into" : "did NOT come into", n + 1, enteredAt, Where(dog), FromMouth(dog, n)));
				if (!came)
				{
					Bring(dog, mo, Mid(n), 440);
					Info("put into the pen by the script");
				}
				Check("itIsInThePen", InPen(dog, n), Where(dog));
				Next();
			}
		}
		if (steer)
		{
			Walk(mo, mid - steer, PASS_Y, true);
			if (S()) { mo.angle = 270; if (st >= 140) { Info("after steering: " .. Where(dog)); Next(); } }
		}
		// the lever, by a real USE
		if (S()) { Pose(mo, mid + 80, PASS_Y + OFF, 270); PressUse(mo); Next(); }
		if (S())
		{
			if (st == 0) Check("leverShutsGate", Gate(n).setting == 0, h.said);
			if (st == 99) { Check("gateShutBehindIt", GateZ(n) < 1 && InPen(dog, n), String.Format("gate %.1f; ", GateZ(n)) .. Where(dog)); Next(); }
		}
		// back: through the turnstile, the run, the door; NOW
		Walk(mo, 840, 608, true);
		Walk(mo, 840, 128, true);
		Walk(mo, 60, 128, true, 500);
		ThroughDoor(mo, true);
		if (S()) { Check("backNow", !InThen(mo) && InPen(dog, n), Where(mo) .. "; it: " .. Where(dog)); Next(); }
	}

	void ScalesMode(Actor mo)
	{
		let s = scales[0];
		if (S())
		{
			dog = FirstNow("Demon");
			ClearNowMonsters(dog);
			Check("scalesZeroAndShutAtStart", Reads(s, 0) && s.IsShut(), ScaleInfo(s));
			sphere = ItemNear("Soulsphere", 120, 720);
			Next();
		}
		LeadAndPen(mo, 0);
		// the door down NOW: the demon's stand-in fades in in pen 1, the scales read 400, the shutter opens
		if (S())
		{
			if (st == 0) { Pose(mo, 24, 128, 180); PressUse(mo); unhungAt = tic; }
			if (st == 1)
			{
				Check("doorDownNow", h.carried == clocked && !clocked.frame, h.said);
				bones = BonesOf(dog, false);
				Check("standInInPen1", bones && InPen(bones, 0) && bones.Translation != 0 && !bones.bSolid,
					bones ? Where(bones) .. " for " .. Where(dog) : String.Format("%d corpses", th.corpses.Size()));
				Check("fadesInFromNothing", bones && bones.alpha < 0.1 && bones.fading == 1, bones ? String.Format("alpha %.2f", bones.alpha) : "");
				Check("countedFromSpawn", Reads(s, 400), ScaleInfo(s));
			}
			if (st == 18) Check("halfIn", bones && bones.alpha > 0.4 && bones.alpha < 0.6, bones ? String.Format("alpha %.2f", bones.alpha) : "gone");
			if (st == 36) Check("fadedInIn35", bones && bones.alpha >= 1 && bones.fading == 0, bones ? String.Format("alpha %.2f", bones.alpha) : "gone");
			if (st == 69) Check("shutterOpenIn64", s.IsOpen() && s.openedAt - unhungAt <= 66, String.Format("open at +%d; ", s.openedAt - unhungAt) .. ScaleInfo(s));
			if (st == 69) Next();
		}
		// NOW to the soul sphere: through the turnstile, the passage, the shutter
		Walk(mo, 740, 128);
		Walk(mo, 840, 128);
		if (S()) { Check("throughTurnstileNow", mo.pos.x > 790 && !InThen(mo), Where(mo)); Next(); }
		Walk(mo, 840, 608);
		Walk(mo, 120, 608);
		Walk(mo, 120, 724);
		if (S()) { Check("soulSphereTaken", !sphere && mo.health > 100, String.Format("health %d; ", mo.health) .. Where(mo)); Next(); }
		// standing under the shutter, the door hung again (by the script: the frame is far): the bones fade out,
		// the scales read 0, the shutter waits for the player
		if (S()) { Pose(mo, 120, 680, 270); Next(); }
		if (S())
		{
			if (st == 0) { HangNow(); unhungAt = tic; Check("hungAgain", clocked.frame == F(101), h.said); }
			if (st == 1) Check("stillCountedFading", bones && bones.fading == -1 && Reads(s, 400), (bones ? String.Format("alpha %.2f; ", bones.alpha) : "gone; ") .. ScaleInfo(s));
			if (st == 18) Check("halfOut", bones && bones.alpha > 0.4 && bones.alpha < 0.6, bones ? String.Format("alpha %.2f", bones.alpha) : "gone");
			if (st == 37) Check("fadedOutIn35", !bones && BonesOf(dog, false) == null && Reads(s, 0), ScaleInfo(s));
			if (st == 120) { Check("shutterWaitsForPlayer", s.IsOpen() && s.held, ScaleInfo(s) .. "; " .. Where(mo)); Next(); }
		}
		Walk(mo, 120, 620);
		if (S() && st >= 80) { Check("shutterShutsWhenClear", s.IsShut() && Reads(s, 0), ScaleInfo(s)); Next(); }
		// through to THEN, to pen 1's hatch: kill the demon through it
		ThroughDoor(mo, false);
		if (S()) { Pose(mo, 120, PASS_Y + OFF, 270); ResetCounts(); watch = dog; Next(); }
		if (S())
		{
			if (st % 12 == 0 && dog.health > 0) Shoot(mo, dog, 25);
			if (dog.health <= 0 || st >= 400)
			{
				Check("killedThroughHatch", dog.health <= 0 && InPen(dog, 0), String.Format("%d hits from the player; ", onWatchByPlayer) .. Where(dog));
				Next();
			}
		}
		if (S())
		{
			if (st == 3)
			{
				bones = BonesOf(dog, true);
				Check("corpseForGood", bones && InPen(bones, 0) && BonesOf(dog, false) == null && bones.alpha >= 1, bones ? Where(bones) : "none");
				Check("reads400DoorHung", clocked.frame != null && Reads(s, 400), ScaleInfo(s));
			}
			if (st == 80) { Check("shutterOpenAgain", s.IsOpen(), ScaleInfo(s)); Next(); }
		}
		// the door down THEN: still 400, for good
		if (S()) { Pose(mo, 40, 128 + OFF, 180); PressUse(mo); Next(); }
		if (S() && st >= 40)
		{
			Check("reads400DoorDown", h.carried == clocked && !clocked.frame && Reads(s, 400) && StandIns() == 0 && BonesOf(dog, true) == bones, ScaleInfo(s) .. "; " .. h.said);
			Next();
		}
	}

	// === MODE=2: the step =========================================================================
	Vector2 bp;
	AjarKennelStep stepA;
	Actor imp, prize;
	double zMax;
	Array<double> climbX, climbY;
	Array<int> climbSide;
	Array<string> climbTag;
	int climb;
	void AddClimb(string tag, double x, double y, int side) { climbTag.Push(tag); climbX.Push(x); climbY.Push(y); climbSide.Push(side); }
	static double LedgeX(int side) { return side == 0 ? 304 : 448; }       // the middle of the stall's west, east ledge
	void StepMode(Actor mo)
	{
		let s = scales[1];
		if (S())
		{
			dog = FirstNow("HellKnight");
			ClearNowMonsters(dog);
			Next();
		}
		LeadAndPen(mo, 1);
		// NOW, the door still hung: the knight THEN goes after the player's place, which for it is north (the end wall)
		if (S())
		{
			if (st == 0) mo.angle = 180;
			if (st % 35 == 0) Info(String.Format("waiting NOW t+%d: the knight THEN %s", st, Where(dog)));
			if ((NowY(dog) > 420 && st >= 70) || st >= 500) { Info(String.Format("the knight THEN deep in the stall after %d tics: %s", st, Where(dog))); Next(); }
		}
		if (S())
		{
			if (st == 0) { Pose(mo, 24, 128, 180); PressUse(mo); dogThen = dog.pos.xy; }
			if (st == 2)
			{
				bones = BonesOf(dog, false);
				stepA = StepOf(bones);
				if (bones) bp = bones.pos.xy;
				Check("doorDownNowKnight", h.carried == clocked && !clocked.frame, h.said);
				Check("knightBonesInPen2", bones && InPen(bones, 1) && bones.weight == 1000, bones ? Where(bones) .. String.Format(" weight %d, %.0f from the hatch's mouth", bones.weight, FromMouth(bones, 1)) : "none");
				Check("aStep", stepA && stepA.radius == dog.radius && stepA.height == 24 && stepA.bSolid,
					stepA ? String.Format("radius %.0f height %.0f solid %d", stepA.radius, stepA.height, stepA.bSolid) : "none");
				Check("pen2Reads1000", Reads(s, 1000), ScaleInfo(s));
			}
			if (st == 2) Next();
		}
		// NOW: from bones in each of these places the player gets up onto them, onto a ledge, and takes what is
		// there: where the lead left them, then (moved by the script) against the west side, against the east
		// side, on the middle line (to either ledge), and at the end wall in front of the hatch (to either ledge)
		if (S())
		{
			climbX.Clear(); climbY.Clear(); climbSide.Clear(); climbTag.Clear();
			AddClimb("_lead", bp.x, bp.y, bp.x < Mid(1) ? 0 : 1);
			AddClimb("_west", 360, 440, 0);
			AddClimb("_east", 392, 440, 1);
			AddClimb("_midW", 376, 440, 0);
			AddClimb("_midE", 376, 440, 1);
			AddClimb("_endW", 376, 504, 0);
			AddClimb("_endE", 376, 504, 1);
			climb = 0;
			Next();
		}
		int top = sn;
		if (S())
		{
			if (st == 0)
			{
				Vector2 at = (climbX[climb], climbY[climb]);
				Pose(mo, at.x, at.y - 72, 90);
				if (climb > 0)
				{
					bones.SetOrigin((at, FloorAt(at)), false);
					stepA.SetOrigin((at, FloorAt(at)), false);
				}
				mo.health = 100; mo.player.health = 100;
				if (!ItemNear("Megasphere", LedgeX(0), 464)) Actor.Spawn("Megasphere", (LedgeX(0), 464, 48));
				if (!ItemNear("Soulsphere", LedgeX(1), 464)) Actor.Spawn("Soulsphere", (LedgeX(1), 464, 48));
				prize = ItemNear(climbSide[climb] == 0 ? "Megasphere" : "Soulsphere", LedgeX(climbSide[climb]), 464);
			}
			if (st == 2) Next();
		}
		if (S())
		{
			Vector2 at = (climbX[climb], climbY[climb]);
			if (st == 0) WalkTo(at.x, at.y);
			if (!walking || st >= 120)
			{
				walking = false; Keys();
				Check("onBones" .. climbTag[climb], abs(mo.pos.z - 24) < 0.5 && (mo.pos.xy - at).Length() < 12 && stepA && stepA.bSolid,
					Where(mo) .. String.Format(" bones at (%.0f,%.0f)", bones.pos.x, bones.pos.y));
				Next();
			}
		}
		Wait(10);
		if (S())
		{
			if (st == 0) WalkTo(LedgeX(climbSide[climb]), climbY[climb]);
			if (!walking || st >= 120)
			{
				walking = false; Keys();
				Check("ontoLedge" .. climbTag[climb], abs(mo.pos.z - 48) < 0.5, Where(mo) .. String.Format(" from bones at (%.0f,%.0f)", bones.pos.x, bones.pos.y));
				Next();
			}
		}
		if (S())
		{
			if (st == 0) WalkTo(LedgeX(climbSide[climb]), 464);
			if (!walking || st >= 120)
			{
				walking = false; Keys();
				Check("took" .. climbTag[climb], !prize && mo.health > 100, String.Format("health %d; ", mo.health) .. Where(mo));
				climb++;
				if (climb < climbX.Size()) JumpTo(top); else Next();
			}
		}
		// the bones back on the middle line; the player comes down onto them from the east ledge
		if (S()) { bp = (376, 440); bones.SetOrigin((bp, 0), false); stepA.SetOrigin((bp, 0), false); Next(); }
		// back down onto the bones; the door hung: they fade out from under the player, who drops
		if (S())
		{
			if (st == 0) { WalkTo(bp.x, bp.y); mark = -1; }
			if (!walking && mark < 0) mark = st;
			if ((mark >= 0 && st >= mark + 15) || st >= 135) { walking = false; Keys(); Check("downOntoBones", abs(mo.pos.z - 24) < 0.5, Where(mo)); Next(); }
		}
		if (S())
		{
			if (st == 0) { HangNow(); mark = mo.health; }
			if (st == 20) Check("stillOnFadingBones", abs(mo.pos.z - 24) < 0.5 && stepA && bones && bones.fading == -1, Where(mo));
			if (st == 60)
			{
				Check("droppedWhenGone", !stepA && !bones && abs(mo.pos.z) < 0.5 && mo.health == mark, Where(mo) .. String.Format(" health %d", mo.health));
				Next();
			}
		}
		Walk(mo, bp.x, bp.y - 80);
		if (S()) { Check("walksOffFree", (mo.pos.xy - (bp.x, bp.y - 80)).Length() < 12, Where(mo)); Next(); }
		// an imp's bones in the same place are no step
		if (S())
		{
			Vector2 at = dog.pos.xy;
			dog.Destroy();
			imp = Actor.Spawn("DoomImp", (at, FloorAt(at)));
			UnhangNow();
			Next();
		}
		if (S())
		{
			if (st == 2)
			{
				bones = BonesOf(imp, false);
				Check("impBonesThere", bones && InPen(bones, 1) && bones.weight == 100, bones ? Where(bones) : "none");
				Check("impBonesNoStep", !StepOf(bones) && kh.steps.Size() == 0, String.Format("%d steps", kh.steps.Size()));
				if (bones) bp = bones.pos.xy;
				WalkTo(bp.x, bp.y + 12);
				zMax = 0;
			}
			if (st > 2)
			{
				zMax = max(zMax, mo.pos.z);
				if (!walking || st >= 120)
				{
					walking = false; Keys();
					Check("walkedThroughImpBones", (mo.pos.xy - (bp.x, bp.y + 12)).Length() < 12 && zMax < 0.5, Where(mo) .. String.Format(" highest z %.1f", zMax));
					Next();
				}
			}
		}
		// a knight's bones appearing under the player: not solid until the player is clear, never pushed or trapped
		if (S())
		{
			HangNow();
			Vector2 at = imp.pos.xy;
			imp.Destroy();
			dog = Actor.Spawn("HellKnight", (at, FloorAt(at)));
			Next();
		}
		Wait(40);
		if (S())
		{
			if (st == 0) { Pose(mo, dog.pos.x, NowY(dog), 270); UnhangNow(); zMax = 0; }
			if (st == 2)
			{
				bones = BonesOf(dog, false);
				stepA = StepOf(bones);
				Check("bonesUnderPlayerNotSolid", stepA && !stepA.bSolid && abs(mo.pos.z) < 0.5, (stepA ? String.Format("step solid %d; ", stepA.bSolid) : "no step; ") .. Where(mo));
				WalkTo(mo.pos.x, mo.pos.y - 80);
			}
			if (st > 2)
			{
				zMax = max(zMax, mo.pos.z);
				if (!walking || st >= 60)
				{
					walking = false; Keys();
					Check("notTrapped", st < 40 && zMax < 0.5, String.Format("%d tics, highest z %.1f; ", st, zMax) .. Where(mo));
					Next();
				}
			}
		}
		if (S() && st >= 5) { Check("solidOnceClear", stepA && stepA.bSolid && stepA.solidAt > 0, stepA ? String.Format("solid at %d", stepA.solidAt) : "none"); Next(); }
	}

	// === MODE=3: the hatch as bait; shots through it; the turnstile =====================================
	int trial;
	Array<int> trialKind, trialPen;
	Array<double> trialX, trialY;
	Array<int> resTime, resIn;
	Array<double> resDist, resDx;
	static class<Actor> Kind(int k) { return k == 0 ? "Demon" : k == 1 ? "HellKnight" : k == 2 ? "BaronOfHell" : "DoomImp"; }
	int maxStart, shotsFired, shotsHit;
	double maxX;

	void AddTrial(int kind, int pen, double x, double y) { trialKind.Push(kind); trialPen.Push(pen); trialX.Push(x); trialY.Push(y); }

	void Hatch(Actor mo)
	{
		if (S())
		{
			ClearNowMonsters();
			mo.player.cheats &= ~CF_GODMODE;
			mo.health = 100000; mo.player.health = 100000;
			static const double SX[] = { 680, 680, 400, 60, 560 };
			static const double SY[] = { 64, 192, 128, 200, 96 };
			for (int i = 0; i < 5; i++) AddTrial(0, 0, SX[i], SY[i]);
			for (int i = 0; i < 5; i++) AddTrial(1, 1, SX[i], SY[i]);
			for (int i = 0; i < 5; i++) AddTrial(2, 1, SX[i], SY[i]);
			trial = 0;
			Next();
		}
		// one trial: the monster awake in the run THEN, only that pen's gate open, the player at its hatch
		int top = sn;
		if (S())
		{
			int n = trialPen[trial];
			for (int k = 0; k < 3; k++) SetGate(21 + k, k == n ? 1 : 0);
			Pose(mo, Mid(n), PASS_Y + OFF, 270);
			dog = SpawnAt(Kind(trialKind[trial]), trialX[trial], trialY[trial], true, 0);
			Wake(dog, mo);
			enteredAt = -1;
			Next();
		}
		if (S())
		{
			int n = trialPen[trial];
			if (enteredAt < 0 && InPen(dog, n)) enteredAt = st;
			bool done = (enteredAt >= 0 && st >= enteredAt + 140) || st >= 700;
			if (done)
			{
				bool inside = InPen(dog, n);
				resIn.Push(inside ? 1 : 0); resTime.Push(enteredAt); resDist.Push(FromMouth(dog, n)); resDx.Push(dog.pos.x - Mid(n));
				Info(String.Format("trial %d: a %s from (%.0f,%.0f) to pen %d: %s after %d tics; 5 s later at %s, %.0f from the hatch's mouth, %.0f off its middle",
					trial + 1, dog.GetClassName(), trialX[trial], trialY[trial], n + 1, inside ? "in" : "NOT in", enteredAt, Where(dog), FromMouth(dog, n), dog.pos.x - Mid(n)));
				bool last = trial == trialKind.Size() - 1 || trialKind[trial + 1] != trialKind[trial];
				if (!last) { dog.Destroy(); trial++; JumpTo(top); }
				else Next();
			}
		}
		// the last of a kind: the lever shuts the gate behind it; the player leaves; it stays penned
		if (S())
		{
			int n = trialPen[trial];
			if (st == 0)
			{
				// the penning is checked, not the luring (the trials above measure that): one not in is put in
				if (!InPen(dog, n)) { Bring(dog, mo, Mid(n), 440); Info(String.Format("the last %s not in pen %d: put in by the script", dog.GetClassName(), n + 1)); }
				Pose(mo, Mid(n) + 80, PASS_Y + OFF, 270);
				PressUse(mo);
			}
			if (st == 80) { Check("gateShuts_" .. dog.GetClassName(), GateZ(n) < 1 && InPen(dog, n), String.Format("gate %.1f; ", GateZ(n)) .. Where(dog)); Pose(mo, 840, 300 + OFF, 90); }
			if (st > 80 && st % 175 == 0) Info(String.Format("penned t+%d: %s", st - 80, Where(dog)));
			if (st == 80 + 525)
			{
				Check("staysPenned_" .. dog.GetClassName(), InPen(dog, n) && GateZ(n) < 1, Where(dog));
				dog.Destroy();
				trial++;
				if (trial < trialKind.Size()) JumpTo(top);
				else Next();
			}
		}
		// the summary per kind
		if (S())
		{
			for (int k = 0; k < 3; k++)
			{
				int came = 0, n = 0;
				double tmin = 1e9, tmax = -1, dmin = 1e9, dmax = -1, tsum = 0;
				string dxs = "";
				for (int i = 0; i < resIn.Size(); i++)
				{
					if (trialKind[i] != k) continue;
					n++;
					if (resIn[i]) { came++; tmin = min(tmin, resTime[i]); tmax = max(tmax, resTime[i]); tsum += resTime[i]; dmin = min(dmin, resDist[i]); dmax = max(dmax, resDist[i]); }
					dxs = dxs .. String.Format(" %.0f", resDx[i]);
				}
				Info(String.Format("%s: %d of %d came into the pen; in after %.0f to %.0f tics (mean %.0f); ended %.0f to %.0f from the hatch's mouth; off its middle:%s",
					Kind(k).GetClassName(), came, n, tmin, tmax, came ? tsum / came : 0, dmin, dmax, dxs));
				// a measure, not a check: Doom's chase is random, and pen 2's stall (an opening 80 wide for a
				// monster 48 wide) lets in about two in three (PLAN.md, "The kennel lab"); the counts are above
			}
			Next();
		}
		// shots and bites through the hatch (pen 1's): each kind penned there, the player at the hatch's mouth
		if (S())
		{
			if (st == 0)
			{
				for (int k = 0; k < 3; k++) SetGate(21 + k, 0);
				trial = 0;
			}
			Next();
		}
		int shots = sn;
		if (S())
		{
			if (st == 0)
			{
				Pose(mo, 120, 562 + OFF, 270);
				dog = SpawnAt(Kind(trial), 120, 470, true, 90);
				Wake(dog, mo);
				ResetCounts();
				watch = dog;
				maxX = 1e9;
				shotsFired = shotsHit = 0;
			}
			maxX = min(maxX, (dog.pos.xy - mo.pos.xy).Length());
			// the player's shots through the hatch, at it, whenever it stands lined up with the hatch (5 at most)
			if (st % 7 == 0 && shotsFired < 5 && abs(dog.pos.x - 120) < 16 && dog.health > 0)
			{
				int before = onWatchByPlayer;
				Shoot(mo, dog, 1);
				shotsFired++;
				shotsHit += onWatchByPlayer - before;
			}
			if (st == 349)
			{
				Info(String.Format("through the hatch, %s penned at it, the player at its mouth: %d missiles and %d melee hits on the player in 10 s; came within %.0f of the player",
					dog.GetClassName(), onPlayerMissile, onPlayerMelee, maxX));
				if (trial == 0) Info(String.Format("demon: %d bites through the hatch in 10 s, within %.0f", onPlayerMelee, maxX));
				if (trial == 1) Check("knightFireballsPass", onPlayerMissile > 0, String.Format("%d", onPlayerMissile));
				if (trial == 3) Info(String.Format("imp: %d fireballs through", onPlayerMissile));
				Info(String.Format("the player's shots at a %s through the hatch, fired while it stood lined up with it: %d of %d hit", dog.GetClassName(), shotsHit, shotsFired));
				if (trial == 1) Check("playerShotsPassHatch", shotsFired > 0 && shotsHit == shotsFired, String.Format("%d of %d", shotsHit, shotsFired));
				dog.Destroy();
				trial++;
				if (trial < 4) JumpTo(shots);
				else Next();
			}
		}
		// the turnstile: the player passes both ways, empty-handed and with the clocked door
		if (S()) { Pose(mo, 650, 128 + OFF, 0); Next(); }
		Walk(mo, 700, 128, true);
		Walk(mo, 850, 128, true);
		if (S()) { Check("turnstileEastEmpty", mo.pos.x > 800 && !h.carried, Where(mo)); Next(); }
		Walk(mo, 700, 128, true);
		if (S()) { Check("turnstileWestEmpty", mo.pos.x < 740, Where(mo)); clocked.Used(mo); Next(); }
		Walk(mo, 850, 128, true);
		if (S()) { Check("turnstileEastWithDoor", mo.pos.x > 800 && h.carried == clocked, Where(mo)); Next(); }
		Walk(mo, 700, 128, true);
		if (S()) { Check("turnstileWestWithDoor", mo.pos.x < 740 && h.carried == clocked, Where(mo)); trial = 0; Next(); }
		// no monster passes in 20 s, the player in plain sight beyond it
		int tst = sn;
		if (S())
		{
			if (st == 0)
			{
				Pose(mo, 850, 128 + OFF, 180);
				static const double TY[] = { 128, 100, 160, 128 };
				dog = SpawnAt(Kind(trial), 640, TY[trial], true, 0);
				Wake(dog, mo);
				maxX = -1;
			}
			maxX = max(maxX, dog.pos.x);
			if (st % 175 == 0) Info(String.Format("turnstile t+%d: %s", st, Where(dog)));
			if (st == 700)
			{
				Check("turnstileStops_" .. dog.GetClassName(), maxX < 768 && dog.pos.x < 768, String.Format("furthest east x %.1f (the line at 768); ", maxX) .. Where(dog));
				dog.Destroy();
				trial++;
				if (trial < 4) JumpTo(tst);
				else Next();
			}
		}
	}

	// === MODE=4: raised from the dead; an arch-vile NOW and old bones ==============================
	Actor vile, ctrl, baron;
	AjarThenCorpse oldImp, oldBaron;
	int revivedAt;
	void Raise(Actor a)
	{
		a.ChangeTid(901);
		level.ExecuteSpecial(17, null, null, false, 901);       // Thing_Raise
		a.ChangeTid(0);
	}
	void Raised(Actor mo)
	{
		if (S())
		{
			ClearNowMonsters();
			mo.player.cheats |= CF_NOTARGET;
			Pose(mo, 100, 128, 0);
			imp = SpawnAt("DoomImp", 632, 400, true, 270);
			Next();
		}
		Wait(10);
		if (S())
		{
			if (st == 0) { Check("timesApart", !th.Linked() && !clocked.frame); imp.DamageMobj(null, null, 1000, 'None'); }
			if (st == 2)
			{
				bones = BonesOf(imp, true);
				Check("killedThenForGood", imp.health <= 0 && bones && bones.alpha >= 1, bones ? Where(bones) : "none");
			}
			if (st == 70) Next();
		}
		if (S())
		{
			if (st == 0) { revivedAt = th.revived; Raise(imp); }
			if (st == 2)
			{
				Check("revivedEventFires", th.revived == revivedAt + 1 && imp.health > 0, String.Format("%d revived, imp health %d", th.revived - revivedAt, imp.health));
				Check("noLongerForGood", BonesOf(imp, true) == null);
				let si = BonesOf(imp, false);
				Check("bonesStandInWhileApart", si && si == bones && CountBones(imp) == 1 && si.alpha >= 1, si ? Where(si) : "none");
			}
			if (st == 70) Next();
		}
		// joined: the stand-in fades out; apart: a stand-in again where it stands
		if (S())
		{
			if (st == 0) HangNow();
			if (st == 40) { Check("joinedNoBones", CountBones(imp) == 0, String.Format("%d", CountBones(imp))); UnhangNow(); }
			if (st == 42) { let si = BonesOf(imp, false); Check("apartStandInAgain", si && CountBones(imp) == 1, si ? Where(si) : "none"); }
			if (st == 80) Next();
		}
		// killed again THEN, then raised while the times are joined: its bones fade
		if (S())
		{
			if (st == 0) imp.DamageMobj(null, null, 1000, 'None');
			if (st == 40) Check("killedAgainForGood", BonesOf(imp, true) != null && CountBones(imp) == 1, String.Format("%d bones", CountBones(imp)));
			if (st == 41) HangNow();
			if (st == 110) { revivedAt = th.revived; Raise(imp); }
			if (st == 112)
			{
				let c = BonesOf(imp, true);
				Check("raisedJoinedFades", th.revived == revivedAt + 1 && imp.health > 0 && (!c || c.Leaving()), String.Format("%d bones", CountBones(imp)));
			}
			if (st == 150) Check("raisedJoinedGone", CountBones(imp) == 0, String.Format("%d bones", CountBones(imp)));
			if (st == 151) UnhangNow();
			if (st == 153) { Check("thenApartStandsIn", BonesOf(imp, false) != null && CountBones(imp) == 1); imp.Destroy(); }
			if (st == 160) Next();
		}
		// an arch-vile NOW among old bones (an imp's, a baron's: for good) and one real corpse NOW
		if (S())
		{
			if (st == 0)
			{
				HangNow();
				let a = SpawnAt("DoomImp", 260, 128, true);
				a.DamageMobj(null, null, 1000, 'None');
				baron = SpawnAt("BaronOfHell", 260, 64, true);
				baron.DamageMobj(null, null, 10000, 'None');
				oldImp = BonesOf(a, true);
				oldBaron = BonesOf(baron, true);
				ctrl = SpawnAt("DoomImp", 420, 128, false);
				ctrl.DamageMobj(null, null, 1000, 'None');
				mo.player.cheats &= ~CF_NOTARGET;
				Pose(mo, 700, 128, 180);
			}
			if (st == 70)
			{
				Check("oldBonesNow", oldImp && oldBaron && !InThen(oldImp) && !InThen(oldBaron), (oldImp ? Where(oldImp) : "no imp's") .. "; " .. (oldBaron ? Where(oldBaron) : "no baron's"));
				vile = SpawnAt("Archvile", 140, 128, false, 0);
				Wake(vile, mo);
				revivedAt = th.revived;
				mark = 0;
			}
			if (st > 70)
			{
				if (st % 70 == 0) Info(String.Format("arch-vile t+%d: %s, the control imp %s", st - 70, Where(vile), ctrl ? Where(ctrl) : "raised"));
				if (ctrl && ctrl.health > 0) { mark = st - 70; Info(String.Format("the arch-vile raised the real corpse NOW after %d tics", mark)); ctrl.Destroy(); ctrl = null; }
			}
			if (st == 70 + 700)
			{
				bool stay = oldImp && !oldImp.bDestroyed && oldBaron && !oldBaron.bDestroyed && oldImp.of == null && oldBaron.of == null;
				Check("archvileRaisesNoOldBones", stay && CountNear(oldImp.pos.xy) == 0 && CountNear(oldBaron.pos.xy) == 0,
					String.Format("old bones there %d; monsters NOW within 24 of them: %d, %d", stay, stay ? CountNear(oldImp.pos.xy) : -1, stay ? CountNear(oldBaron.pos.xy) : -1));
				Info(mark ? String.Format("control: the real corpse NOW was raised after %d tics", mark) : "control: the real corpse NOW was not raised in 20 s");
				Next();
			}
		}
	}
	int CountNear(Vector2 p)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && !InThen(a) && a != vile && (a.pos.xy - p).Length() < 24) n++;
		return n;
	}

	// === MODE=5: two pens set on each other (measured, not checked) ===================================
	Actor knight;
	int run;
	void SetOn(Actor mo)
	{
		if (S())
		{
			ClearNowMonsters();
			mo.player.cheats &= ~CF_GODMODE;
			run = 0;
			Next();
		}
		int top = sn;
		if (S())
		{
			if (st == 0)
			{
				mo.health = 100000; mo.player.health = 100000;
				SetGate(21, 0); SetGate(22, 0); SetGate(23, 0); SetGate(24, 1);
				static const double KX[] = { 376, 360, 392, 376, 368 };
				static const double IX[] = { 632, 580, 680, 560, 700 };
				knight = SpawnAt("HellKnight", KX[run], 400, true, 90);
				imp = SpawnAt("DoomImp", IX[run], 360 + 20 * run, true, 180);
				Pose(mo, 376, PASS_Y + OFF, 270);
				Wake(knight, mo);
				Wake(imp, mo);
				ResetCounts();
				watch = knight;
				other = imp;
			}
			if (st % 175 == 0) Info(String.Format("set on t+%d: knight %s hp %d target %s; imp %s hp %d target %s", st, Where(knight), knight.health,
				knight.target ? knight.target.GetClassName() : 'none', Where(imp), imp.health, imp.target ? imp.target.GetClassName() : 'none'));
			if (st == 1050 || (knight.health <= 0 && imp.health <= 0))
			{
				Console.Printf("AJARTEST setOn run=%d knightHitByImp=%d (%d damage) impHitByKnight=%d (%d damage) knightHp=%d impHp=%d knightTarget=%s impTarget=%s",
					run + 1, watchByOther, watchDmgByOther, otherByWatch, otherDmgByWatch, knight.health, imp.health,
					knight.target ? knight.target.GetClassName() : 'none', imp.target ? imp.target.GetClassName() : 'none');
				knight.Destroy(); imp.Destroy();
				watch = other = null;
				run++;
				if (run < 5) JumpTo(top);
				else Next();
			}
		}
	}

	// === MODE=7: how a monster follows through the clocked door (a probe: an imp, a knight, a demon) ======
	void FollowProbe(Actor mo)
	{
		if (S())
		{
			ClearNowMonsters();
			trial = 0;
			clocked.Used(mo);
			Pose(mo, 40, 128, 180);
			PressUse(mo);
			Next();
		}
		int top = sn;
		if (S())
		{
			if (st == 0)
			{
				Pose(mo, 60, 128, 180);
				dog = SpawnAt(Kind(trial == 0 ? 3 : trial == 1 ? 1 : 0), 300, 128, false, 180);
				Wake(dog, mo);
			}
			if (st == 20) { Pose(mo, 40, 128, 180); Keys(WALKKEY); }
			if (st == 43) { Keys(); WalkTo(400, 128 + OFF); }
			let sense = AjarSense(dog.FindInventory("AjarSense"));
			if (st >= 20 && st < 400 && st % 6 == 0)
				Info(String.Format("probe %s t+%d: %s angle %.0f movedir %d target %s at (%.0f,%.0f) via %s; player %s",
					dog.GetClassName(), st, Where(dog), dog.angle, dog.movedir, dog.target ? dog.target.GetClassName() : 'none',
					dog.target ? dog.target.pos.x : 0, dog.target ? dog.target.pos.y : 0,
					sense && sense.via ? String.Format("(%.0f,%.0f)-(%.0f,%.0f)", sense.via.v1.p.x, sense.via.v1.p.y, sense.via.v2.p.x, sense.via.v2.p.y) : "none",
					Where(mo)));
			if (st == 400)
			{
				Info(String.Format("probe %s: %s", dog.GetClassName(), InThen(dog) && dog.pos.x > 48 ? "came through" : "did not come through"));
				dog.Destroy();
				walking = false; Keys();
				ThroughDoorNow(mo);
				trial++;
				if (trial < 3) JumpTo(top); else Next();
			}
		}
	}
	void ThroughDoorNow(Actor mo) { Pose(mo, 60, 128, 180); }

	// === MODE=6: views for a person to judge (smoke_KENNEL_6.cfg: a shot every 70 tics) ===============
	int viewN;
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0, double z = -1)
	{
		Pose(mo, x, y, ang, pitch);
		if (z >= 0) mo.SetOrigin((x, y, z), false);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void Views(Actor mo)
	{
		if (S()) { mo.bInvisible = true; mo.player.cheats |= CF_NOTARGET; if (st >= 14) Next(); }
		if (S()) { if (st == 0) View(mo, "the run NOW from the west: the clocked door, the monsters asleep", 60, 40, 15); if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "the run THEN from the west: lit, the gates", 60, 40 + OFF, 15); if (st == 69) Next(); }
		if (S()) { if (st == 0) { SetGate(22, 0); View(mo, "THEN: pen 2's gate shut, pens 1 and 3 open", 376, 120 + OFF, 110); } if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "NOW: the pens from the run, the gates gone", 376, 120, 110); if (st == 69) Next(); }
		if (S())
		{
			if (st == 0)
			{
				dog = SpawnAt("Demon", 120, 470, true, 270);
				View(mo, "THEN: pen 1's hatch from the passage, a demon behind it", 120, 650 + OFF, 270);
			}
			if (st == 69) Next();
		}
		if (S()) { if (st == 0) View(mo, "THEN: pen 1's hatch from inside the pen", 120, 330 + OFF, 90); if (st == 69) Next(); }
		if (S())
		{
			if (st == 0) HangNow();
			if (st == 2) UnhangNow();
			if (st == 40) View(mo, "NOW: the demon's bones in pen 1, from the run", 120, 120, 90, 8);
			if (st == 109) Next();
		}
		if (S()) { if (st == 0) View(mo, "NOW: the same bones through the hatch, from the passage", 120, 600, 270, 10); if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "NOW: pen 1's readout (400, green) beside its hatch", 60, 620, 260, 5); if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "NOW: pen 1's shutter open, the soul sphere", 120, 600, 90); if (st == 69) Next(); }
		if (S())
		{
			if (st == 0)
			{
				knight = SpawnAt("HellKnight", 376, 440, true, 90);
				HangNow();
			}
			if (st == 2) UnhangNow();
			if (st == 40) View(mo, "NOW: a knight's bones in the stall, between its ledges", 376, 290, 90, 5);
			if (st == 109) Next();
		}
		if (S()) { if (st == 0) View(mo, "NOW: from on top of the bones, the west ledge and the megasphere", 376, 440, 150, 10, 24); if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "NOW: pen 2's readout (1000)", 330, 620, 260, 5); if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "NOW: the turnstile from the run", 640, 128, 0); if (st == 69) Next(); }
		if (S()) { if (st == 0) View(mo, "THEN: the turnstile from the passage's east leg", 850, 300 + OFF, 250); if (st == 69) Next(); }
		if (S()) { if (st == 0) { SetGate(24, 1); View(mo, "THEN: the opening into pen 3 over the stall's east ledge", 360, 368 + OFF, 0); } if (st == 69) Next(); }
	}
}
