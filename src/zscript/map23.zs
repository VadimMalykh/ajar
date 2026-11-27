// MAP23 "Sleeping Dogs" (tools/map_sleepingdogs.py; PLAN.md, "MAP23 "Sleeping Dogs": the first version, as decided"
// and "... the first playable version"): the level's own script, and its checks (SleepingDogsTest, below). THEN is
// NOW + (0, -8192). Bones, their scales and steps: then.zs and kennel.zs.
//
// AjarStockGate (20194, THEN): a run's Doom gate, a pad of Doom's stone at the far end of the run. args[0]: the tag
// of the run's sectors (its pen's or stall's too: UDMF moreids); args[1]: the DoomEdNum of its kind (3002 demon, 69
// hell knight, 16 cyberdemon); args[2]: the tid it gives what it brings; args[3]: a keep tag (the crush): while a
// dead one of its kind lies in a sector of that tag it brings none. When no monster of its kind is alive in the run
// (one led off out of it counts as gone) and WAIT tics have passed since the last one was, and nothing solid stands
// on the pad, one arrives there with teleport fog and its sound; it counts for no kill total (a specimen), and while
// the times are apart its bones show NOW at once, as every specimen's do. The first time: "There is always another."
class AjarStockGate : Actor
{
	const WAIT = 175;          // five seconds
	Array<int> secs, keep;
	class<Actor> kind;
	int lastHere;
	int brought;               // (the tests)
	double px1, py1, px2, py2; // the pad

	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	static class<Actor> KindOf(int ednum)
	{
		if (ednum == 3002) return "Demon";
		if (ednum == 69) return "HellKnight";
		if (ednum == 16) return "Cyberdemon";
		return null;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		kind = KindOf(args[1]);
		let si = level.CreateSectorTagIterator(args[0]);
		int s;
		while ((s = si.Next()) >= 0) secs.Push(s);
		if (args[3])
		{
			let ki = level.CreateSectorTagIterator(args[3]);
			while ((s = ki.Next()) >= 0) keep.Push(s);
		}
		Sector pad = level.PointInSector(pos.xy);
		px1 = py1 = 1e9; px2 = py2 = -1e9;
		for (int j = 0; j < pad.lines.Size(); j++)
		{
			Line l = pad.lines[j];
			px1 = min(px1, min(l.v1.p.x, l.v2.p.x)); py1 = min(py1, min(l.v1.p.y, l.v2.p.y));
			px2 = max(px2, max(l.v1.p.x, l.v2.p.x)); py2 = max(py2, max(l.v1.p.y, l.v2.p.y));
		}
		lastHere = level.maptime;
	}

	bool InRun(Vector2 p) { return secs.Find(level.PointInSector(p).Index()) != secs.Size(); }

	// a dead one of its kind lies in the keep (the crush): the big one is where it was wanted
	bool Kept()
	{
		if (!args[3]) return false;
		let it = ThinkerIterator.Create(kind);
		Actor a;
		while (a = Actor(it.Next()))
			if (a.GetClass() == kind && a.health <= 0 && keep.Find(level.PointInSector(a.pos.xy).Index()) != keep.Size()) return true;
		return false;
	}

	int Alive()
	{
		int n = 0;
		let it = ThinkerIterator.Create(kind);
		Actor a;
		while (a = Actor(it.Next())) if (a.GetClass() == kind && a.health > 0 && InRun(a.pos.xy)) n++;
		return n;
	}

	bool PadClear(double r)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!(a.player || a.bSolid) || a.bNoBlockmap || a == self) continue;
			if (a.pos.x + a.radius <= px1 - r || a.pos.x - a.radius >= px2 + r) continue;
			if (a.pos.y + a.radius <= py1 - r || a.pos.y - a.radius >= py2 + r) continue;
			return false;
		}
		return true;
	}

	override void Tick()
	{
		Super.Tick();
		if (!kind || level.maptime % 5) return;
		if (Alive()) { lastHere = level.maptime; return; }
		if (level.maptime - lastHere < WAIT || Kept() || !PadClear(0)) return;
		let a = Actor.Spawn(kind, pos);
		if (!a) return;
		if (!a.TestMobjLocation()) { a.ClearCounters(); a.Destroy(); return; }
		a.angle = angle;
		a.ChangeTid(args[2]);
		a.ClearCounters();
		if (kind == "Cyberdemon") a.bAmbush = true;         // the big one wakes by sight (AjarSleepingDogs wakes it too)
		Actor.Spawn("TeleportFog", pos);
		lastHere = level.maptime;
		brought++;
		let th = AjarThenHandler.Get();
		if (th && th.ready && !th.wasLinked) th.OldCorpse(a, a);   // the times apart: its bones NOW at once
		let sd = AjarSleepingDogs.Get();
		if (sd) sd.Another();
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info a Doom gate brought a %s at (%.0f,%.0f), t=%d (%d so far)", a.GetClassName(), pos.x, pos.y, level.maptime, brought);
	}
}

// The level's own: the specimens count for no kill total; the big one wakes when the player is in its keeper's
// passage THEN; the three lines, each once.
class AjarSleepingDogs : EventHandler
{
	const KEN_DOGS = 2311;
	const STALL_DOGS = 2312;
	const BIG_ONE = 2313;
	const GUARDS = 2314;
	const OFF = -8192;
	bool saidLain, saidNotDead, saidAnother;
	int woke;                  // (the tests) the big one woken by the passage

	static AjarSleepingDogs Get() { return AjarSleepingDogs(EventHandler.Find("AjarSleepingDogs")); }
	static bool Here() { return level.mapname ~== "MAP23"; }
	static bool Specimen(Actor a) { return a && (a.tid == KEN_DOGS || a.tid == STALL_DOGS || a.tid == BIG_ONE || a.tid == GUARDS); }

	void Say(string s)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(s);
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info said at t=%d: %s", level.maptime, s);
	}

	void Another()
	{
		if (saidAnother) return;
		saidAnother = true;
		Say("There is always another.");
	}

	override void WorldLoaded(WorldEvent e)
	{
		if (!Here() || e.IsSaveGame) return;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && Specimen(a)) a.ClearCounters();
	}

	override void WorldTick()
	{
		if (!Here()) return;
		let th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		if (!saidNotDead && th.wasLinked)
		{
			for (int i = 0; i < th.corpses.Size(); i++)
			{
				let c = th.corpses[i];
				if (c && c.of && c.of.health > 0) { saidNotDead = true; Say("Not dead yet."); break; }
			}
		}
		if (!saidLain && !th.wasLinked)
		{
			let si = ThinkerIterator.Create("AjarKennelScales");
			AjarKennelScales s;
			while (s = AjarKennelScales(si.Next())) if (s.Holds()) { saidLain = true; Say("It has lain there for forty years."); break; }
		}
		let mo = players[consoleplayer].mo;
		if (!mo || !th.when.InThen(mo.pos.xy)) return;
		double y = mo.pos.y - OFF;
		if (mo.pos.x < 560 || mo.pos.x > 1072 || y < -1456 || y > -1312) return;
		let it = level.CreateActorIterator(BIG_ONE);
		Actor a;
		while (a = it.Next())
		{
			if (a.health <= 0 || a.target == mo) continue;
			a.bAmbush = false;
			a.target = mo;
			a.movedir = 8;          // DI_NODIR: its next A_Chase picks a direction toward him (else it starts east)
			a.movecount = 0;
			if (a.SeeState) a.SetState(a.SeeState);
			woke++;
			if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info the big one woken by the passage at t=%d", level.maptime);
		}
	}
}

// The checks: MAP=MAP23 MODE=n tools/smoke.sh.
//   1 the way through (tools/puzzle23.py's shortest), to the way out: walked and by USE; ordinary company removed,
//     the specimens and the guards real; a lure that does not work in its time is finished by the script (logged)
//   2 the rules, posed: bones at the first tic; "Not dead yet."; three demons in pen 1 open both shutters; one killed
//     there through the hatch holds the scales with the door hung; a Doom gate restocks; the big one killed outside
//     the crush: another, its bones a step; killed in the crush: none
//   3 measurements (nothing has to pass): knight into the stall, the big one into the crush (and its rockets at the
//     hatch and behind the pier), a specimen left with its gate open and the player NOW, the guards led through
//   4 views (tools/smoke_MAP23_4.cfg shoots every 70 tics; two a view)
//   5 the look board's tour (tools/board23_shots.sh; a camera of its own, THEN and NOW from the same spot)
class SleepingDogsTest : EventHandler
{
	const OFF = -8192;
	const WALKKEY = 0x1900;
	const KEN_DOGS = 2311;
	const STALL_DOGS = 2312;
	const BIG_ONE = 2313;
	const GUARDS = 2314;
	const LEVER_X = 840;       // THEN: where the player pulls the crush's lever (facing 60), the gate in sight through the glass
	const LEVER_Y = -1336;
	int tic, checks, fails;
	int step, cur, stepTic;
	bool entered;
	AjarHandler h;
	AjarThenHandler th;
	AjarKennel kh;
	AjarSleepingDogs sd;
	AjarDoor clocked, shadow, red;
	AjarKennelScales sc1, sc2;
	int viewN;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP23"; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	bool S() { return cur++ == step; }
	void Next() { step++; entered = false; }
	bool First() { if (!entered) { entered = true; stepTic = tic; return true; } return false; }
	int Age() { return tic - stepTic; }

	bool InThen(Actor a) { return th.when.InThen(a.pos.xy); }
	double NowY(Actor a) { return InThen(a) ? a.pos.y - OFF : a.pos.y; }
	string Where(Actor a) { return a ? String.Format("(%.1f,%.1f,%.1f) %s", a.pos.x, NowY(a), a.pos.z, InThen(a) ? "THEN" : "NOW") : "(gone)"; }
	AjarFrame F(int id) { return h.FindFrame(id); }
	double FZ(double x, double y) { Sector s = level.PointInSector((x, y)); return s.floorplane.ZatPoint((x, y)); }
	double CZ(double x, double y) { Sector s = level.PointInSector((x, y)); return s.ceilingplane.ZatPoint(s.centerspot); }
	bool Said(string part) { return h.said.IndexOf(part) >= 0; }
	bool Inside(Actor a, double x1, double y1, double x2, double y2, bool then)
	{
		if (!a || InThen(a) != then) return false;
		double y = NowY(a);
		return a.pos.x > x1 + a.radius - 1 && a.pos.x < x2 - a.radius + 1 && y > y1 + a.radius - 1 && y < y2 - a.radius + 1;
	}
	bool InPen1(Actor a) { return Inside(a, -880, 688, -640, 944, true); }
	bool InStall(Actor a) { return Inside(a, 1240, 304, 1320, 496, true); }
	bool InCrush(Actor a) { return Inside(a, 720, -1296, 848, -1040, true); }
	bool InIsoPen(Actor a) { return Inside(a, 784, 1280, 1024, 1472, true); }
	double Gate(double x, double y) { return CZ(x, y + OFF); }        // a gate's ceiling THEN (0: shut)

	// --- the player's controls, as map22.zs ------------------------------------------------------
	int fwd;
	Vector2 walkGoal;
	bool walking;
	double pushAngle;
	bool pushing;
	double best;
	int bestAt;
	Vector2 last;
	bool jumped;
	int afterJump;

	void Keys(int f = 0) { fwd = f; }
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp) return;
		if (walking)
		{
			Vector2 d = walkGoal - mo.pos.xy;
			double l = d.Length(), v = mo.vel.xy.Length();
			if (l < 8 && v < 1.5) { walking = false; Keys(); }
			else
			{
				if (l > 2) mo.angle = VectorAngle(d.x, d.y);
				double along = l > 0.01 ? (mo.vel.xy dot d) / l : 0;
				fwd = l < along * 10 + 4 ? (along > 0.5 ? -WALKKEY : 0) : WALKKEY;
			}
		}
		else if (pushing) { mo.angle = pushAngle; fwd = WALKKEY; }
		if (!fwd && !walking) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.buttons = 0;
		pp.HandleMovement();
	}
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}
	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, FZ(x, y)), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = pushing = false;
		Keys();
	}
	void Put(Actor mo, double x, double y, double ang) { Pose(mo, x, y, ang); Next(); }
	// walk to x, y (NOW's coordinates; `then`: at THEN)
	void Go(Actor mo, double x, double y, bool then = false)
	{
		if (then) y += OFF;
		if (First())
		{
			walkGoal = (x, y); walking = true; pushing = false;
			best = 1e9; bestAt = tic;
		}
		double d = (walkGoal - mo.pos.xy).Length();
		if (d < best - 4) { best = d; bestAt = tic; }
		if (!walking) { Next(); return; }
		if (tic - bestAt > 105)
		{
			Check(String.Format("walkTo_%d_%d", x, then ? y - OFF : y), false, Where(mo));
			walking = false; Keys(); Next();
		}
	}
	void GoT(Actor mo, double x, double y) { Go(mo, x, y, true); }
	void Push(Actor mo, double ang, int n)
	{
		if (First()) { pushAngle = ang; pushing = true; walking = false; }
		if (Age() >= n) { pushing = false; Keys(); Next(); }
	}
	void Through(Actor mo, double ang)
	{
		if (First()) { pushAngle = ang; pushing = true; walking = false; last = mo.pos.xy; jumped = false; afterJump = 0; }
		if (!jumped && (mo.pos.xy - last).Length() > 100) { jumped = true; pushAngle = mo.angle; }
		last = mo.pos.xy;
		if (jumped && ++afterJump >= 14) { pushing = false; Keys(); Next(); return; }
		if (Age() > 140) { Check("walkThrough", false, Where(mo)); pushing = false; Keys(); Next(); }
	}
	void Use(Actor mo, double ang) { mo.angle = ang; mo.pitch = 0; PressUse(mo); Next(); }
	void Wait(int n) { First(); if (Age() >= n) Next(); }

	// --- monsters ---------------------------------------------------------------------------------
	// set on the player with no stale direction: DI_NODIR (8) makes its next A_Chase pick one toward him (a woken
	// monster's movedir is 0, east, and it walked that way first: the caco-through-doors session's warning)
	void Wake(Actor a, Actor mo) { if (!a || a.health <= 0) return; a.bAmbush = false; a.target = mo; a.movedir = 8; a.movecount = 0; if (a.SeeState) a.SetState(a.SeeState); }
	// put a monster at x, y (NOW's coordinates; `then`), after the player, with no door in its head
	void Bring(Actor a, Actor mo, double x, double y, bool then = true)
	{
		if (!a) return;
		if (then) y += OFF;
		a.SetOrigin((x, y, FZ(x, y)), false);
		a.ClearInterpolation();
		a.vel = (0, 0, 0);
		let sense = AjarSense(a.FindInventory("AjarSense"));
		if (sense) { sense.via = null; sense.Unmute(); if (sense.lure) sense.lure.Destroy(); }
		a.target = mo;
		a.movedir = 8;
		a.movecount = 0;
	}
	void Kill(Actor a, Actor by) { if (a && a.health > 0) a.DamageMobj(by, by, a.health + 1000, 'None', DMG_FORCED); }
	void Of(int tid, Array<Actor> found, bool alive = true)
	{
		found.Clear();
		let it = level.CreateActorIterator(tid);
		Actor a;
		while (a = it.Next()) if (a.bIsMonster && (!alive || a.health > 0)) found.Push(a);
	}
	Actor OneOf(int tid, class<Actor> cls = null)
	{
		let it = level.CreateActorIterator(tid);
		Actor a;
		while (a = it.Next()) if (a.bIsMonster && a.health > 0 && (!cls || a.GetClass() == cls)) return a;
		return null;
	}
	int CountAlive(int tid) { Array<Actor> l; Of(tid, l); return l.Size(); }
	// ordinary company out of the way (every tic of MODE 1 and 4: the ambushes too); the specimens and guards kept
	void ClearOrdinary()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		Array<Actor> gone;
		while (a = Actor(it.Next())) if (a.bIsMonster && !AjarSleepingDogs.Specimen(a)) gone.Push(a);
		for (int i = 0; i < gone.Size(); i++) { gone[i].Destroy(); cleared++; }
	}
	int cleared;

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
	int StandIns()
	{
		int n = 0;
		for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && !th.corpses[i].bDestroyed && th.corpses[i].of) n++;
		return n;
	}
	AjarKennelStep StepOf(AjarThenCorpse c) { return kh && c ? kh.StepOf(c) : null; }
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
	string ScaleInfo(AjarKennelScales s) { return String.Format("weight %d, reads '%s', shutter %.1f%s", s.weight, Readout(s), s.shutter ? s.CeilZ() : -1, s.held ? " (held)" : ""); }
	void SetGate(int cause, int n)
	{
		let c = th.FindCause(cause);
		if (!c) return;
		th.SetCause(c, n, null);
		th.Snap(c);
	}

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
			sd = AjarSleepingDogs.Get();
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.IsShadow()) shadow = d;
				else if (d.IsClocked()) clocked = d;
				else if (d.args[1] == 1) red = d;
			}
			sc1 = AjarKennelScales.OfTag(81);
			let si = ThinkerIterator.Create("AjarKennelScales");
			AjarKennelScales s;
			while (s = AjarKennelScales(si.Next())) if (s.args[1] == 1000) sc2 = s;
			if (mode != 3) mo.player.cheats |= CF_GODMODE;
			if (mode == 4 || mode == 5) mo.player.cheats |= CF_NOTARGET;
			Info(String.Format("clocked %d shadow %d red %d; scales %d %d; monsters to kill %d", clocked != null, shadow != null, red != null, sc1 != null, sc2 != null, level.total_monsters));
		}
		if (mode == 1 || mode == 4 || mode == 5) ClearOrdinary();
		cur = 0;
		if (mode == 1) Walk(mo);
		else if (mode == 2) Rules(mo);
		else if (mode == 3) Measure(mo);
		else if (mode == 4) Views(mo);
		else if (mode == 5) { Tour(mo); return; }
		Drive(mo);
		if (tic % 140 == 0 && mode != 4) Info(String.Format("t=%d step %d %s carried %s", tic, step, Where(mo), h.carried ? h.carried.Label() : "-"));
	}

	void Done() { Console.Printf("AJARTEST sleepingDogsDone=1 checks=%d failed=%d", checks, fails); Next(); }

	// === MODE=1: the way through ===================================================================
	// a lure: the player stands where he is; `who` (tid) come until `inside` holds for one or the time is up;
	// then the script puts the first that did not in (logged). Returns through `lured` how many came by themselves.
	int lured, luredAt;
	bool LureInto(Actor mo, int tid, int which, int limit, double bx, double by)
	{
		First();
		Array<Actor> l;
		Of(tid, l);
		for (int i = 0; i < l.Size(); i++)
		{
			bool inside = which == 1 ? InPen1(l[i]) : which == 2 ? InStall(l[i]) : which == 3 ? InCrush(l[i]) && NowY(l[i]) < -1150 : InIsoPen(l[i]);
			if (inside)
			{
				lured = 1; luredAt = Age();
				Info(String.Format("a %s came in by itself after %d tics, at %s", l[i].GetClassName(), Age(), Where(l[i])));
				return true;
			}
		}
		if (Age() % 70 == 0) for (int i = 0; i < l.Size(); i++) Info(String.Format("t+%d %s %s", Age(), l[i].GetClassName(), Where(l[i])));
		if (Age() >= limit)
		{
			lured = 0;
			if (l.Size())
			{
				Bring(l[0], mo, bx, by);
				Info(String.Format("no %s came in within %d tics: one put in by the script", l[0].GetClassName(), limit));
			}
			return true;
		}
		return false;
	}
	int brought1, came1;
	void Woken(Actor mo, int tid, int wait)
	{
		First();
		Array<Actor> l;
		Of(tid, l);
		int awake = 0;
		for (int i = 0; i < l.Size(); i++) if (l[i].target == mo) awake++;
		if (awake && Age() >= 20) { Info(String.Format("%d of %d (tid %d) awake by themselves after %d tics", awake, l.Size(), tid, Age())); Next(); return; }
		if (Age() >= wait)
		{
			for (int i = 0; i < l.Size(); i++) Wake(l[i], mo);
			Info(String.Format("none of %d (tid %d) woke in %d tics: woken by the script", l.Size(), tid, wait));
			Next();
		}
	}
	int guardsCame, guardsBrought, guardsPenned, guardsLoose;

	void Walk(Actor mo)
	{
		if (S()) Wait(2);
		if (S())
		{
			Check("startsNowInTheYard", !InThen(mo) && mo.pos.x > 0 && mo.pos.x < 640 && mo.pos.y < 512, Where(mo));
			Check("bonesAtTheStart", StandIns() == 6, String.Format("%d stand-ins", StandIns()));
			Check("clockedLeansInTheShelter", clocked && !clocked.frame && !InThen(clocked) && clocked.pos.x < 192 && clocked.pos.y > 128 && clocked.pos.y < 320);
			Check("redLeansInTheGuardRoom", red && !red.frame && red.pos.x > 784 && red.pos.y > 1280 && red.pos.y < 1472, red ? Where(red) : "none");
			int counted = 0;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && AjarSleepingDogs.Specimen(a) && a.bCountKill) counted++;
			Check("specimensNotCounted", counted == 0, String.Format("%d counted; the level's kill total %d", counted, level.total_monsters));
			Next();
		}
		// the clocked door, the house's door, the hall, the antechamber
		if (S()) Go(mo, 176, 224);
		if (S()) Use(mo, 180);
		if (S()) { Check("tookClocked", h.carried == clocked, h.said); Next(); }
		if (S()) Go(mo, 320, 470);
		if (S()) Use(mo, 90);
		if (S()) Wait(35);
		if (S()) Go(mo, 320, 660);
		if (S()) { Check("intoTheHall", mo.pos.y > 592 && !InThen(mo), Where(mo)); Next(); }
		// --- the guards: the clocked door in 104; they are led THEN and penned; the door down
		if (S()) Go(mo, 128, 1150);
		if (S()) Go(mo, 128, 1320);
		if (S()) Go(mo, 40, 1376);
		if (S()) Use(mo, 180);
		if (S()) { Check("clockedIn104", F(104).door == clocked && F(124).door == shadow, h.said); Next(); }
		if (S()) Wait(2);
		if (S()) { Check("notDeadYet", Said("Not dead yet."), h.said); Next(); }
		if (S()) { mo.angle = 0; Woken(mo, GUARDS, 140); }
		if (S()) Wait(50);
		if (S()) Through(mo, 180);
		if (S()) { Check("guardsWingThen", InThen(mo) && mo.pos.x < 400 && NowY(mo) > 1280 && NowY(mo) < 1472, Where(mo)); Next(); }
		if (S()) GoT(mo, 208, 1440);
		if (S())
		{
			First();
			mo.angle = 180;
			Array<Actor> l;
			Of(GUARDS, l);
			int n = 0;
			for (int i = 0; i < l.Size(); i++) if (InThen(l[i])) n++;
			if (n == l.Size() || Age() >= 350)
			{
				guardsCame = n;
				for (int i = 0; i < l.Size(); i++) if (!InThen(l[i])) { Bring(l[i], mo, 400 + 100 * guardsBrought, 1340 + 40 * (guardsBrought % 2)); guardsBrought++; }
				Info(String.Format("guards: %d of %d followed through the clocked door by themselves in %d tics; %d brought by the script", n, l.Size(), Age(), guardsBrought));
				Next();
			}
		}
		if (S()) GoT(mo, 208, 1540);
		if (S()) GoT(mo, 904, 1540);
		if (S()) GoT(mo, 904, 1515);
		if (S())
		{
			First();
			mo.angle = 270;
			Array<Actor> l;
			Of(GUARDS, l);
			int n = 0;
			for (int i = 0; i < l.Size(); i++) if (InIsoPen(l[i])) n++;
			if (Age() % 70 == 0) for (int i = 0; i < l.Size(); i++) Info(String.Format("t+%d %s %s", Age(), l[i].GetClassName(), Where(l[i])));
			if (n == l.Size() || Age() >= 700)
			{
				guardsPenned = n;
				int put = 0;
				for (int i = 0; i < l.Size(); i++) if (!InIsoPen(l[i])) { Bring(l[i], mo, 860 + 60 * put, 1330 + 30 * (put % 2)); put++; }
				Info(String.Format("guards: %d of %d came into the pen by themselves in %d tics; %d put in by the script", n, l.Size(), Age(), put));
				Next();
			}
		}
		if (S()) Wait(20);
		if (S()) GoT(mo, 984, 1530);
		if (S()) Use(mo, 270);
		if (S()) Wait(100);
		if (S()) { Check("guardsShutIn", Gate(776, 1376) < 1, String.Format("gate %.1f", Gate(776, 1376))); Next(); }
		if (S()) GoT(mo, 904, 1540);
		if (S()) GoT(mo, 208, 1540);
		if (S()) GoT(mo, 208, 1440);
		if (S()) GoT(mo, 60, 1376);
		if (S()) Through(mo, 180);
		if (S()) { Check("backNowAntechamber", !InThen(mo) && mo.pos.x < 256 && mo.pos.y > 1280, Where(mo)); Next(); }
		if (S()) Go(mo, 40, 1376);
		if (S()) Use(mo, 180);
		if (S()) Wait(2);
		if (S())
		{
			int bones = 0;
			for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && th.corpses[i].who && th.corpses[i].who.tid == GUARDS) bones++;
			Check("clockedDownFrom104", h.carried == clocked && !F(104).door, h.said);
			Check("guardsAreBonesNow", bones == 3 && CountAlive(GUARDS) == 3, String.Format("%d bones", bones));
			Next();
		}
		// --- the stalls: the clocked door in 103; a knight into the stall; the door down; up its bones: key 2
		if (S()) Go(mo, 128, 1320);
		if (S()) Go(mo, 128, 1150);
		if (S()) Go(mo, 700, 1088);
		if (S()) Go(mo, 1120, 1088);
		if (S()) Go(mo, 1300, 1376);
		if (S()) Go(mo, 1480, 1376);
		if (S()) Go(mo, 1480, 192);
		if (S()) Go(mo, 1184, 200);
		if (S()) Use(mo, 270);
		if (S()) { Check("clockedIn103", F(103).door == clocked && F(123).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 270);
		if (S()) { Check("stallsPassageThen", InThen(mo) && NowY(mo) > 160 && NowY(mo) < 288, Where(mo)); Next(); }
		if (S()) GoT(mo, 1480, 224);
		if (S()) GoT(mo, 1480, 1376);
		if (S()) GoT(mo, 1360, 1376);
		if (S()) { mo.angle = 180; Woken(mo, STALL_DOGS, 105); }
		if (S()) GoT(mo, 1480, 1376);
		if (S()) GoT(mo, 1480, 240);
		if (S()) GoT(mo, 1280, 250);
		if (S()) { mo.angle = 90; if (LureInto(mo, STALL_DOGS, 2, 1050, 1280, 420)) { came1 += lured; Next(); } }
		if (S()) Wait(35);
		if (S()) GoT(mo, 1360, 250);
		if (S()) Use(mo, 90);
		if (S()) Wait(100);
		if (S())
		{
			Check("stallGateShut", Gate(1280, 504) < 1, String.Format("gate %.1f", Gate(1280, 504)));
			Array<Actor> l;
			Of(STALL_DOGS, l);
			int n = 0;
			for (int i = 0; i < l.Size(); i++) if (InStall(l[i])) n++;
			Info(String.Format("knights in the stall when its gate came down: %d", n));
			if (!n && l.Size()) { Bring(l[0], mo, 1280, 420); l[0].target = null; Info("one put into the stall by the script"); }
			Next();
		}
		if (S()) GoT(mo, 1184, 200);
		if (S()) Through(mo, 270);
		if (S()) { Check("backNowStallsPassage", !InThen(mo) && mo.pos.y > 160 && mo.pos.y < 224, Where(mo)); Next(); }
		if (S()) Go(mo, 1184, 200);
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S()) { Check("clockedDownFrom103", h.carried == clocked && !F(103).door, h.said); Next(); }
		if (S()) Go(mo, 1480, 192);
		if (S()) Go(mo, 1480, 1376);
		if (S()) Go(mo, 1300, 1376);
		if (S()) Go(mo, 1280, 700);
		if (S()) Go(mo, 1280, 560);
		if (S()) { knight = StallBones(); Check("knightsBonesInTheStall", knight != null, knight ? String.Format("(%.0f,%.0f)", knight.pos.x, knight.pos.y) : "none"); Next(); }
		if (S()) { if (knight) Go(mo, knight.pos.x, knight.pos.y); else Next(); }
		if (S()) { Check("onTheKnightsBones", abs(mo.pos.z - 24) < 1, Where(mo)); Next(); }
		if (S()) { if (knight) Go(mo, knight.pos.x < 1280 ? 1216 : 1344, knight.pos.y); else Next(); }
		if (S()) { Check("upOnTheLedge", abs(mo.pos.z - 48) < 1, Where(mo)); Next(); }
		if (S()) { if (knight) Go(mo, knight.pos.x < 1280 ? 1208 : 1352, 272); else Next(); }
		if (S()) Go(mo, 1280, 272);
		if (S()) { Check("key2FromTheLedge", h.Has(mo, 2), Where(mo)); Next(); }
		if (S()) Go(mo, 1280, 420);
		if (S()) Go(mo, 1280, 600);
		// --- the kennels: the clocked door in 102, left hung; a demon into pen 1
		if (S()) Go(mo, 1280, 1088);
		if (S()) Go(mo, 700, 1088);
		if (S()) Go(mo, 40, 632);
		if (S()) Go(mo, -368, 620);
		if (S()) Go(mo, -368, 584);
		if (S()) Use(mo, 270);
		if (S()) { Check("clockedIn102", F(102).door == clocked && F(122).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 270);
		if (S()) { Check("kennelsPassageThen", InThen(mo) && NowY(mo) > 544 && NowY(mo) < 672, Where(mo)); Next(); }
		if (S()) GoT(mo, -368, 610);
		if (S()) GoT(mo, -984, 610);
		if (S()) GoT(mo, -984, 1088);
		if (S()) GoT(mo, -890, 1088);
		if (S()) { mo.angle = 0; Woken(mo, KEN_DOGS, 105); }
		if (S()) GoT(mo, -984, 1088);
		if (S()) GoT(mo, -984, 610);
		if (S()) GoT(mo, -760, 640);
		if (S()) { mo.angle = 90; if (LureInto(mo, KEN_DOGS, 1, 1050, -760, 820)) { came1 += lured; Next(); } }
		if (S()) Wait(35);
		if (S()) GoT(mo, -680, 640);
		if (S()) Use(mo, 90);
		if (S()) Wait(100);
		if (S())
		{
			Check("pen1GateShut", Gate(-760, 952) < 1, String.Format("gate %.1f", Gate(-760, 952)));
			Array<Actor> l;
			Of(KEN_DOGS, l);
			int n = 0;
			for (int i = 0; i < l.Size(); i++) if (InPen1(l[i])) n++;
			Info(String.Format("demons in pen 1 when its gate came down: %d", n));
			if (!n && l.Size()) { Bring(l[0], mo, -760, 820); l[0].target = null; Info("one put into pen 1 by the script"); }
			Next();
		}
		if (S()) GoT(mo, -368, 600);
		if (S()) Through(mo, 270);
		if (S()) { Check("backNowKennels", !InThen(mo) && mo.pos.y > 544 && mo.pos.y < 672, Where(mo)); Next(); }
		if (S()) Wait(70);
		if (S()) { Check("scalesEmptyWhileJoined", sc1.weight == 0, ScaleInfo(sc1)); Next(); }
		// --- RED, from the guard room (its guards are bones in the pen's place); the clocked door stays in 102
		if (S()) Go(mo, 40, 632);
		if (S()) Go(mo, 128, 1150);
		if (S()) Go(mo, 128, 1320);
		if (S()) Go(mo, 200, 1376);
		if (S()) Go(mo, 600, 1376);
		if (S()) Go(mo, 920, 1376);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookRed", h.carried == red, h.said); Next(); }
		if (S()) Go(mo, 600, 1376);
		if (S()) Go(mo, 200, 1376);
		if (S()) Go(mo, 128, 1320);
		if (S()) Go(mo, 128, 1150);
		if (S()) Go(mo, 40, 632);
		if (S()) Go(mo, -368, 620);
		if (S()) Go(mo, -368, 584);
		// RED for the clocked door in 102: the times apart, the demon's bones in pen 1, S1 open: key 1
		if (S()) Use(mo, 270);
		if (S()) { Check("redSwappedInto102", F(102).door == red && h.carried == clocked && !F(122).door, h.said); Next(); }
		if (S()) Wait(80);
		if (S())
		{
			Check("demonsBonesOnTheScales", sc1.weight >= 400 && Reads(sc1, sc1.weight), ScaleInfo(sc1));
			Check("s1Open", sc1.IsOpen(), ScaleInfo(sc1));
			Check("lainForty", Said("forty years"), h.said);
			Info(String.Format("pen 1 weighs %d; the second shutter %s", sc1.weight, sc2 && sc2.IsOpen() ? "open" : "shut"));
			Next();
		}
		if (S()) Go(mo, -760, 600);
		if (S()) Go(mo, -760, 520);
		if (S()) Go(mo, -760, 476);
		if (S()) { Check("key1FromTheCloset", h.Has(mo, 1), Where(mo)); Next(); }
		if (S()) Go(mo, -760, 600);
		if (S()) Go(mo, -368, 600);
		if (S()) Go(mo, -368, 584);
		// RED to the big run's passage; the clocked door in 105; the big one into the crush
		if (S()) Through(mo, 270);
		if (S()) { Check("redToBigRunsPassage", !InThen(mo) && mo.pos.x > 560 && mo.pos.x < 1072 && mo.pos.y > -1456 && mo.pos.y < -1360, Where(mo)); Next(); }
		if (S()) Go(mo, 600, -1408);
		if (S()) Use(mo, 180);
		if (S()) { Check("clockedIn105", F(105).door == clocked && F(125).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 180);
		if (S()) { Check("bigRunsPassageThen", InThen(mo) && NowY(mo) > -1456 && NowY(mo) < -1312, Where(mo)); Next(); }
		// at the lever beside the glass: it comes by scent; the gate pulled without moving
		if (S()) GoT(mo, LEVER_X, LEVER_Y);
		if (S()) { mo.angle = 60; if (LureInto(mo, BIG_ONE, 3, 1050, 784, -1170)) { came1 += lured; Next(); } }
		if (S()) Use(mo, 60);
		if (S()) Wait(100);
		if (S())
		{
			let a = OneOf(BIG_ONE);
			Check("crushGateShut", Gate(784, -1032) < 1, String.Format("gate %.1f", Gate(784, -1032)));
			Info(String.Format("the big one %s the crush when its gate came down: %s", InCrush(a) ? "was in" : "had backed out of", Where(a)));
			if (!InCrush(a)) { Bring(a, mo, 784, -1170); a.target = null; Info("put into the crush by the script"); }
			Next();
		}
		if (S()) GoT(mo, 600, -1408);
		if (S()) Through(mo, 180);
		if (S()) { Check("backNowBigRunsPassage", !InThen(mo) && mo.pos.y > -1456 && mo.pos.y < -1360, Where(mo)); Next(); }
		if (S()) Go(mo, 600, -1408);
		if (S()) Use(mo, 180);
		if (S()) Wait(3);
		if (S()) { Check("clockedDownFrom105", h.carried == clocked && !F(105).door, h.said); Next(); }
		// out by RED; the hall, the yard, the big run; up the big one's bones, the brass door, out
		if (S()) Go(mo, 896, -1420);
		if (S()) Through(mo, 270);
		if (S()) { Check("redBackToKennels", !InThen(mo) && mo.pos.y > 544 && mo.pos.y < 672, Where(mo)); Next(); }
		if (S()) Go(mo, -368, 620);
		if (S()) Go(mo, 40, 632);
		if (S()) Go(mo, 320, 640);
		if (S()) Use(mo, 270);
		if (S()) Wait(35);
		if (S()) Go(mo, 320, 420);
		if (S()) Go(mo, 600, 440);
		if (S()) Go(mo, 720, 440);
		if (S()) Go(mo, 784, -800);
		if (S()) Go(mo, 784, -1000);
		if (S()) { big = CrushBones(); Check("bigOnesBonesInTheCrush", big != null, big ? String.Format("(%.0f,%.0f), step %d", big.pos.x, big.pos.y, StepOf(big) != null) : "none"); Next(); }
		if (S()) { if (big) Go(mo, big.pos.x, big.pos.y); else Next(); }
		if (S()) { Check("onTheBigOnesBones", abs(mo.pos.z - 24) < 1, Where(mo)); Next(); }
		// to the nearer side (the arithmetic: one side is always in reach), round the end to the east ledge
		if (S()) { if (big) Go(mo, big.pos.x < 784 ? 688 : 880, big.pos.y); else Next(); }
		if (S()) { Check("upOnTheCrushsLedge", abs(mo.pos.z - 48) < 1, Where(mo)); Next(); }
		if (S()) { if (big && big.pos.x < 784) Go(mo, 688, -1320); else Next(); }
		if (S()) { if (big && big.pos.x < 784) Go(mo, 880, -1320); else Next(); }
		if (S()) Go(mo, 880, -1104);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) { Check("brassDoorOpens", CZ(920, -1104) > 48 + 64, String.Format("ceiling %.0f", CZ(920, -1104))); Next(); }
		if (S()) Go(mo, 1000, -1104);
		if (S()) Go(mo, 1072, -1104);
		if (S())
		{
			Info(String.Format("lures that worked by themselves: %d of 3 (knight, demon, big one); guards: %d of 3 followed, %d penned by themselves; ordinary company cleared %d",
				came1, guardsCame, guardsPenned, cleared));
			Done();
		}
		if (S()) Push(mo, 270, 200);
	}
	AjarThenCorpse knight, big;
	AjarThenCorpse StallBones()
	{
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && c.who is "HellKnight" && c.pos.x > 1240 && c.pos.x < 1320 && c.pos.y > 304 && c.pos.y < 496) return c;
		}
		return null;
	}
	AjarThenCorpse CrushBones()
	{
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && c.who is "Cyberdemon" && c.pos.x > 720 && c.pos.x < 848 && c.pos.y > -1296 && c.pos.y < -1040) return c;
		}
		return null;
	}

	// === MODE=2: the rules, posed =====================================================================
	Array<Actor> dogs;
	Actor cyber, cyber2;
	AjarThenCorpse cyberBones;
	void HangIn(int id) { if (h.carried == clocked) h.carried = null; else if (clocked.frame) return; h.Hang(clocked, F(id)); }
	void TakeDown() { if (clocked.frame) h.carried = h.Unhang(clocked.frame); }
	void Rules(Actor mo)
	{
		if (S()) Wait(1);
		if (S())
		{
			Check("bonesAtTheFirstTic", StandIns() == 6, String.Format("%d stand-ins", StandIns()));
			bool whole = true;
			for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && (th.corpses[i].fading || th.corpses[i].alpha < 1)) whole = false;
			Check("bonesThereAtOnce", whole);
			cyber = OneOf(BIG_ONE);
			let b = BonesOf(cyber, false);
			let st = StepOf(b);
			Check("bigOnesBonesAStep", b && st && st.bSolid && abs(b.pos.x - 784) < 1 && abs(b.pos.y - 96) < 1, b ? String.Format("(%.0f,%.0f) step %d solid %d", b.pos.x, b.pos.y, st != null, st && st.bSolid) : "none");
			Check("scalesEmpty", sc1 && sc1.weight == 0 && sc1.IsShut() && sc2 && sc2.IsShut(), sc1 ? ScaleInfo(sc1) : "none");
			int counted = 0;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && AjarSleepingDogs.Specimen(a) && a.bCountKill) counted++;
			Check("specimensCountForNoKill", counted == 0, String.Format("%d counted", counted));
			Check("nothingSaidYet", !Said("Not dead") && !Said("forty years") && !Said("always another"), h.said);
			Next();
		}
		if (S()) Put(mo, 320, 800, 90);
		if (S()) { HangIn(102); Next(); }
		if (S()) Wait(2);
		if (S())
		{
			Check("notDeadYet", Said("Not dead yet."), h.said);
			int leaving = 0;
			for (int i = 0; i < th.corpses.Size(); i++) if (th.corpses[i] && th.corpses[i].Leaving()) leaving++;
			Check("standInsFadeWhenJoined", leaving == 6, String.Format("%d fading out", leaving));
			Next();
		}
		// three demons in pen 1, shut in; the door down: 1200, both shutters
		if (S())
		{
			Of(KEN_DOGS, dogs);
			Check("threeDemons", dogs.Size() == 3);
			for (int i = 0; i < dogs.Size(); i++) { Bring(dogs[i], null, -820 + 60 * i, 780 + 50 * (i % 2)); dogs[i].target = null; }
			SetGate(21, 0);
			Next();
		}
		if (S()) Wait(40);
		if (S()) { int n = 0; for (int i = 0; i < dogs.Size(); i++) if (InPen1(dogs[i])) n++; Check("threeInPen1", n == 3, String.Format("%d", n)); TakeDown(); Next(); }
		if (S()) Wait(80);
		if (S())
		{
			Check("threeDemonsWeigh1200", Reads(sc1, 1200) && Reads(sc2, 1200), ScaleInfo(sc1) .. "; " .. ScaleInfo(sc2));
			Check("s1Open", sc1.IsOpen(), ScaleInfo(sc1));
			Check("secondShutterOpenAt1000", sc2.IsOpen(), ScaleInfo(sc2));
			Check("lainForty", Said("It has lain there for forty years."), h.said);
			Next();
		}
		// the door hung again: no bones; one killed in the pen through the hatch: its bones hold the scales
		if (S()) { HangIn(102); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("joinedThePenWeighsNothing", sc1.weight == 0, ScaleInfo(sc1)); Next(); }
		if (S()) Put(mo, -760, 640 + OFF, 90);
		if (S())
		{
			let d = dogs[1];
			Vector2 v = d.pos.xy - mo.pos.xy;
			mo.angle = VectorAngle(v.x, v.y);
			double dz = d.pos.z + d.height / 2 - (mo.pos.z + PlayerPawn(mo).AttackZOffset + mo.height / 2);
			mo.pitch = -atan2(dz, v.Length());
			for (int k = 0; k < 20 && d.health > 0; k++) mo.LineAttack(mo.angle, 4096, mo.pitch, 100, 'Hitscan', "BulletPuff");
			Check("killedThroughTheHatch", d.health <= 0, String.Format("health %d at %s", d.health, Where(d)));
			Kill(d, mo);
			Next();
		}
		if (S()) Wait(80);
		if (S())
		{
			let b = BonesOf(dogs[1], true);
			Check("itsBonesForGoodInPen1", b && b.pos.x > -880 && b.pos.x < -640 && b.pos.y > 688 && b.pos.y < 944 && StandIns() == 0, b ? String.Format("(%.0f,%.0f); %d stand-ins", b.pos.x, b.pos.y, StandIns()) : "none");
			Check("holdsTheScalesWithTheDoorHung", clocked.frame == F(102) && Reads(sc1, 400) && sc1.IsOpen(), ScaleInfo(sc1));
			Check("secondShutterShutAgain", sc2.IsShut() || sc2.held, ScaleInfo(sc2));
			Next();
		}
		// the other two killed: the run's Doom gate brings another
		if (S()) { Kill(dogs[0], mo); Kill(dogs[2], mo); Next(); }
		if (S())
		{
			First();
			let a = OneOf(KEN_DOGS);
			if (a || Age() > 300)
			{
				Check("aDoomGateRestocks", a && InThen(a) && a.pos.x > -144 && a.pos.x < -80 && NowY(a) > 1056 && NowY(a) < 1120 && !a.bCountKill, String.Format("after %d tics: %s", Age(), Where(a)));
				Check("alwaysAnother", Said("There is always another."), h.said);
				Next();
			}
		}
		// the big one killed where it stands: another comes; its bones in the run stay a step
		if (S()) { cyber = OneOf(BIG_ONE); Kill(cyber, mo); Next(); }
		if (S()) Wait(3);
		if (S())
		{
			cyberBones = BonesOf(cyber, true);
			let st = StepOf(cyberBones);
			Check("bigOnesBonesForGood", cyberBones && abs(cyberBones.pos.y - 96) < 2 && st != null, cyberBones ? String.Format("(%.0f,%.0f)", cyberBones.pos.x, cyberBones.pos.y) : "none");
			Next();
		}
		if (S())
		{
			First();
			cyber2 = OneOf(BIG_ONE);
			if (cyber2 || Age() > 300)
			{
				Check("anotherBigOne", cyber2 && InThen(cyber2) && NowY(cyber2) > 416 && !cyber2.bCountKill, String.Format("after %d tics: %s", Age(), Where(cyber2)));
				Next();
			}
		}
		if (S()) Wait(20);
		if (S()) { let st = StepOf(cyberBones); Check("itsBonesStayAStep", st && st.bSolid, st ? String.Format("solid %d", st.bSolid) : "none"); Next(); }
		if (S()) { TakeDown(); Next(); }
		if (S()) Wait(3);
		if (S()) { let b = BonesOf(cyber2, false); Check("theNewOnesBonesNow", b && StepOf(b) && b.pos.y > 416, b ? String.Format("(%.0f,%.0f)", b.pos.x, b.pos.y) : "none"); Next(); }
		// killed in the crush: none comes
		if (S()) { Bring(cyber2, null, 784, -1168); cyber2.target = null; Next(); }
		if (S()) Wait(5);
		if (S()) { Check("secondInTheCrush", InCrush(cyber2), Where(cyber2)); Pose(mo, LEVER_X, LEVER_Y + OFF, 60); Next(); }
		if (S())
		{
			Check("glassBlocksSightBothWays", !cyber2.CheckSight(mo) && !mo.CheckSight(cyber2), String.Format("it sees him %d, he it %d", cyber2.CheckSight(mo), mo.CheckSight(cyber2)));
			// a shot of his from the lever: the glass takes it
			int h0 = cyber2.health;
			Vector2 v = cyber2.pos.xy - mo.pos.xy;
			mo.angle = VectorAngle(v.x, v.y);
			mo.LineAttack(mo.angle, 4096, 0, 100, 'Hitscan', "BulletPuff");
			Check("glassStopsShots", cyber2.health == h0, String.Format("health %d of %d", cyber2.health, h0));
			Kill(cyber2, mo);
			Next();
		}
		if (S()) Wait(300);
		if (S())
		{
			let b = BonesOf(cyber2, true);
			Check("noneAfterTheCrush", !OneOf(BIG_ONE), Where(OneOf(BIG_ONE)));
			Check("crushBonesAStep", b && StepOf(b) && b.pos.y < -1040, b ? String.Format("(%.0f,%.0f)", b.pos.x, b.pos.y) : "none");
			Done();
		}
	}

	// === MODE=3: measurements ==========================================================================
	int trial, entered3, sumTics, dmgHatch, dmgPier, left3, shut3, seen3, sightTics;
	Actor sub;
	string results;
	void Setup3(Actor mo)
	{
		let it = ThinkerIterator.Create("AjarStockGate");
		Array<Actor> g;
		Actor a;
		while (a = Actor(it.Next())) g.Push(a);
		for (int i = 0; i < g.Size(); i++) g[i].Destroy();
		ClearOrdinary();
		Info(String.Format("MODE 3: the Doom gates taken away (%d), ordinary company cleared", g.Size()));
	}
	void Heal(Actor mo) { mo.health = 100000; mo.player.health = 100000; }
	int Hurt(Actor mo) { return 100000 - mo.health; }
	void Clear(class<Actor> cls) { Array<Actor> l; let it = ThinkerIterator.Create(cls); Actor a; while (a = Actor(it.Next())) if (a.GetClass() == cls) l.Push(a); for (int i = 0; i < l.Size(); i++) l[i].Destroy(); }
	Actor Spawn3(class<Actor> cls, double x, double y, bool then, int tid)
	{
		if (then) y += OFF;
		let a = Actor.Spawn(cls, (x, y, FZ(x, y)));
		if (a) { a.ChangeTid(tid); a.ClearCounters(); a.bAmbush = false; }
		return a;
	}

	void Measure(Actor mo)
	{
		if (S()) { Setup3(mo); Next(); }
		// A: a knight in the run, the player at the stall's hatch: does it come into the stall, how fast; then the
		// player steps to the lever and pulls it: is it shut in?
		if (S()) { trial = entered3 = sumTics = shut3 = 0; Next(); }
		if (S())
		{
			if (First())
			{
				Clear("HellKnight");
				SetGate(22, 1);
				Pose(mo, 1280, 250 + OFF, 90);
				Heal(mo);
				sub = Spawn3("HellKnight", 1184 + (trial * 37) % 192, 900 + (trial * 113) % 560, true, STALL_DOGS);
				Wake(sub, mo);
			}
			bool inside = InStall(sub);
			if (inside || Age() >= 525)
			{
				if (inside) { entered3++; sumTics += Age(); }
				Info(String.Format("knight trial %d: %s after %d tics; at %s; the player hurt %d", trial, inside ? "in the stall" : "NOT in", Age(), Where(sub), Hurt(mo)));
				Next();
			}
		}
		if (S()) GoT(mo, 1360, 250);
		if (S()) Use(mo, 90);
		if (S())
		{
			First();
			if (Age() >= 100)
			{
				bool shut = Gate(1280, 504) < 1 && InStall(sub);
				if (shut) shut3++;
				Info(String.Format("knight trial %d: the lever pulled; %s; it at %s", trial, shut ? "shut in" : "NOT shut in", Where(sub)));
				if (++trial < 10) { step -= 3; entered = false; } else Next();
			}
		}
		if (S()) { results = String.Format("knight into the stall: %d of 10, %d tics on average; shut in by the lever after: %d of 10", entered3, entered3 ? sumTics / entered3 : 0, shut3); Info(results); Next(); }
		// B: the big one in its run, a fresh one (asleep, as a Doom gate brings it); the player stands at the lever
		// beside the crush's glass THEN and does not move: the level's handler wakes it by scent; does it come into
		// the crush, how fast, does it ever see him (CheckSight, either way through the glass), is he hurt; the
		// lever pulled from where he stands: is it shut in?
		if (S()) { trial = entered3 = sumTics = dmgHatch = shut3 = seen3 = 0; Next(); }
		if (S())
		{
			if (First())
			{
				Clear("Cyberdemon");
				SetGate(24, 1);
				Pose(mo, LEVER_X, LEVER_Y + OFF, 60);
				Heal(mo);
				sub = Spawn3("Cyberdemon", 700 + (trial * 41) % 168, -500 + (trial * 157) % 900, true, BIG_ONE);
				sub.bAmbush = true;
				sub.angle = 90 + (trial * 67) % 180;
				sightTics = 0;
			}
			if (sub.CheckSight(mo) || mo.CheckSight(sub)) sightTics++;
			bool inside = InCrush(sub) && NowY(sub) < -1150;
			if (inside || Age() >= 700)
			{
				if (inside) { entered3++; sumTics += Age(); }
				Info(String.Format("big one trial %d: %s after %d tics; at %s; target %s", trial, inside ? "deep in the crush" : "NOT in", Age(), Where(sub), sub.target == mo ? "the player" : "none"));
				mo.angle = 60; mo.pitch = 0;
				PressUse(mo);
				Next();
			}
		}
		if (S())
		{
			First();
			if (sub.CheckSight(mo) || mo.CheckSight(sub)) sightTics++;
			if (Age() >= 100)
			{
				bool shut = Gate(784, -1032) < 1 && InCrush(sub);
				if (shut) shut3++;
				if (sightTics) seen3++;
				dmgHatch += Hurt(mo);
				Info(String.Format("big one trial %d: the lever pulled from where he stood: %s; it at %s; sight %d tics; the player hurt %d, at %s",
					trial, shut ? "shut in" : "NOT shut in", Where(sub), sightTics, Hurt(mo), Where(mo)));
				if (++trial < 10) { step -= 1; entered = false; } else Next();
			}
		}
		if (S()) { Info(String.Format("big one by scent into the crush: %d of 10, %d tics on average; shut in from the lever: %d of 10; trials with any sight: %d; the player hurt %d in all", entered3, entered3 ? sumTics / entered3 : 0, shut3, seen3, dmgHatch)); Next(); }
		// C: left with its gate open, the player NOW: does it leave the pen's end of the run?
		if (S()) { trial = left3 = 0; Next(); }
		if (S())
		{
			if (First())
			{
				Clear("HellKnight"); Clear("Cyberdemon");
				bool big3 = trial >= 10;
				SetGate(22, 1); SetGate(24, 1);
				if (big3) { sub = Spawn3("Cyberdemon", 784, -1170, true, BIG_ONE); Pose(mo, 700, -1408, 0); }
				else { sub = Spawn3("HellKnight", 1270 + (trial % 3) * 10, 380 + (trial % 4) * 25, true, STALL_DOGS); Pose(mo, 1300, 192, 0); }
				Heal(mo);
				Wake(sub, mo);
				leftAt = -1;
			}
			bool big3 = trial >= 10;
			bool gone = big3 ? NowY(sub) > -896 : NowY(sub) > 640;
			if (gone && leftAt < 0) leftAt = Age();
			if (Age() >= 350)
			{
				if (leftAt >= 0) left3++;
				Info(String.Format("%s trial %d, gate open, the player NOW: %s; at %s after 350 tics", big3 ? "big one" : "knight", trial, leftAt >= 0 ? String.Format("left the end of its run after %d tics", leftAt) : "stayed at the end of its run", Where(sub)));
				trial++;
				if (trial == 10) { Info(String.Format("knights that left: %d of 10", left3)); left3 = 0; }
				if (trial < 15) entered = false; else { Info(String.Format("big ones that left: %d of 5", left3)); Next(); }
			}
		}
		// D: a real lead of the guards through the clocked door in 104
		if (S()) { Clear("HellKnight"); Clear("Cyberdemon"); trial = guardsCame = 0; HangIn(104); Next(); }
		if (S())
		{
			if (First())
			{
				Clear("BaronOfHell"); Clear("Archvile");
				Pose(mo, 60, 1376, 0);
				Heal(mo);
				g3.Clear();
				g3.Push(Spawn3("BaronOfHell", 600, 1328, false, GUARDS));
				g3.Push(Spawn3("BaronOfHell", 600, 1424, false, GUARDS));
				g3.Push(Spawn3("Archvile", 760, 1376, false, GUARDS));
				for (int i = 0; i < 3; i++) { g3[i].angle = 180; Wake(g3[i], mo); }
			}
			if (Age() == 50) { pushAngle = 180; pushing = true; last = mo.pos.xy; }
			if (pushing && (mo.pos.xy - last).Length() > 100) { pushing = false; Keys(); Pose(mo, 208, 1440 + OFF, 180); crossedAt = Age(); }
			if (pushing) last = mo.pos.xy;
			if (First3()) { came3[0] = came3[1] = came3[2] = -1; }
			for (int i = 0; i < 3; i++) if (came3[i] < 0 && g3[i] && InThen(g3[i])) came3[i] = Age();
			if (Age() >= 50 + 525)
			{
				pushing = false; Keys();
				int n = 0;
				for (int i = 0; i < 3; i++) if (g3[i] && g3[i].health > 0 && InThen(g3[i])) n++;
				guardsCame += n;
				Info(String.Format("guards trial %d: %d of 3 followed through the clocked door in 525 tics (the player through at +%d, then posed at the turnstile's mouth; %s); first THEN at +%d +%d +%d",
					trial, n, crossedAt, Where(mo), came3[0], came3[1], came3[2]));
				if (++trial < 10) entered = false; else Next();
			}
		}
		if (S()) { Info(String.Format("guards that followed: %d of 30 in 10 trials", guardsCame)); Done(); }
	}
	int leftAt, crossedAt;
	Array<Actor> g3;
	int came3[3];
	int g3trial;
	bool First3() { if (g3trial != trial + 1) { g3trial = trial + 1; return true; } return false; }

	// === MODE=4: views, 140 tics each (a screenshot every 70 tics: tools/smoke_MAP23_4.cfg; two a view) ============
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void V(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		if (S()) { View(mo, what, x, y, ang, pitch); Next(); }
		if (S()) Wait(139);
	}
	void Views(Actor mo)
	{
		if (S()) { mo.bInvisible = true; Wait(15); }
		V(mo, "NOW from the start: the yard, the glass, the big one's bones beyond", 320, 32, 10);
		V(mo, "THEN from the start: the yard by day, the big one alive beyond the glass", 320, 32 + OFF, 10);
		V(mo, "NOW the shelter, the clocked door", 330, 224, 180);
		V(mo, "NOW the house's front: its door, frame 101", 420, 280, 90);
		V(mo, "NOW the hall from its door", 320, 620, 90);
		V(mo, "NOW the kennels' run from the hall: pens on the south side", -40, 1120, 200);
		V(mo, "THEN the kennels' run from the turnstile: the demons, the Doom gate", -880, 1088 + OFF, 0);
		V(mo, "THEN pen 1 through its hatch, the lever", -760, 600 + OFF, 80);
		V(mo, "NOW the kennels' passage: frame 102, the readout, S1", -560, 610, 190);
		V(mo, "NOW the stalls' run from its north end: the knights' bones, the funnel", 1280, 1500, 270);
		V(mo, "THEN the stalls' run from the turnstile: the knights", 1400, 1376 + OFF, 210);
		V(mo, "THEN the stall through its hatch", 1280, 230 + OFF, 90);
		V(mo, "NOW the stall from the funnel: the ledges, key 2, the soul sphere", 1280, 620, 270, 10);
		V(mo, "NOW the guard room from the antechamber: RED beyond", 100, 1376, 0);
		V(mo, "THEN the isolation run from frame 124", 40, 1376 + OFF, 0);
		V(mo, "THEN the passage over the isolation pen", 600, 1550 + OFF, 0);
		V(mo, "NOW the big run from the gateway: the big one's bones", 680, 440, 280);
		V(mo, "THEN the big run from its Doom gate: the big one", 784, 400 + OFF, 270);
		V(mo, "NOW the crush from the funnel: the ledges, the brass door", 784, -900, 270, 10);
		V(mo, "NOW the brass door from the big run's floor, at the funnel", 700, -880, 313, 4);
		V(mo, "THEN the crush through its glass, from the lever", LEVER_X, LEVER_Y + OFF, 95, -4);
		V(mo, "THEN the passage from frame 125: the glass, the lever, RED's far side", 600, -1408 + OFF, 20);
		V(mo, "NOW the big run's passage: RED's far side, frame 105", 1040, -1400, 190);
		V(mo, "THEN the secret behind the shelter", 40, 224 + OFF, 180);
		V(mo, "NOW the night room", 1072, -1220, 90);
		if (S()) { Info("views done"); Console.Printf("AJARTEST sleepingDogsViews=1"); Next(); }
	}

	// === MODE=5: the tour of the look board (tools/dogs23.py; tools/board23_shots.sh, whose header numbers the
	// shots) ============================================================================================================
	// A camera of its own (AjarTourCam23) at each view for 70 tics from tic 20 (tools/smoke_MAP23_5.cfg shoots every
	// 35: two a shot, the later kept). The player stays at the start, not drawn, no target; NOW's ordinary company is
	// cleared (ClearOrdinary), the specimens THEN and their bones NOW kept. A view is x, y (NOW's), angle, pitch,
	// when: 0 THEN and then NOW from the same spot (THEN is y + OFF), 1 THEN only, 2 NOW only.
	static const double TOUR[] = {
		600, -200, 110, 0, 0,      // yard: the front, the door, the shelter
		120, 40, 15, 0, 0,         // yard: the glass, the gateway
		300, 224, 180, 0, 0,       // yard: the shelter straight on
		60, 640, 45, 0, 2,         // hall
		700, 1180, 225, 0, 2,      // hall
		-60, 1088, 180, 0, 0,      // runs: the kennels' run
		1280, 1500, 270, 0, 0,     // runs: the stalls' run to its funnel
		784, 520, 270, 0, 0,       // runs: the big run
		40, 1376, 0, 0, 0,         // runs: the isolation run THEN, the antechamber NOW
		-760, 1100, 270, 0, 0,     // pens: into pen 1
		-420, 1180, 250, 0, 0,     // pens: the gates of pens 2 and 3
		1280, 600, 270, 0, 0,      // pens: the stall
		784, -900, 270, 0, 0,      // pens: the crush
		700, 1376, 0, 0, 0,        // pens: the isolation pen THEN, the guard room's end NOW
		-60, 608, 180, 0, 0,       // passages: the kennels' passage
		-700, 600, 90, 0, 0,       // passages: pen 1's hatch, lever and readout
		1500, 200, 180, 0, 0,      // passages: the stalls' passage
		1040, -1400, 180, 0, 0,    // passages: the big run's passage
		40, 1552, 0, 0, 1,         // passages: the isolation passage (THEN)
		352, 224, 180, -10, 0,     // plates 1: LINE 6, THE INSTITUTE
		320, 352, 90, -16, 0,      // plates 2: ANIMAL HOUSE
		144, 352, 90, -12, 0,      // plates 2: the plan (yard)
		496, 752, 270, -12, 2,     // plates 2: the plan (hall)
		-608, 668, 270, -10, 0,    // plates 4: the rules (kennels' passage)
		1376, 218, 270, -14, 0,    // plates 4: the rules (stalls' passage)
		480, 1492, 90, -10, 1,     // plates 4: the rules (isolation passage)
		736, -1364, 270, -12, 0,   // plates 4: the rules (big run's passage)
		-928, 668, 270, -10, 0,    // plates 5: the weigh record
		480, 32, 0, -24, 0,        // plates 6: DO NOT TAP ON THE GLASS
		-1030, 1088, 0, -8, 0,     // plates 6: KEEPERS ONLY (kennels)
		1530, 1376, 180, -8, 0,    // plates 6: KEEPERS ONLY (stalls)
		208, 1610, 270, -8, 1,     // plates 6: KEEPERS ONLY (isolation)
		-480, 1056, 90, -12, 0,    // plates 7: the kennels' name board
		1248, 1024, 0, -12, 0,     // plates 7: the stalls' name board
		480, 1440, 270, -12, 0,    // plates 7: the isolation run's name board
		752, 288, 0, -12, 0,       // plates 7: the big run's name board
		-488, 860, 270, 8, 0,      // things: a bowl at pen 2's hatch, from inside the pen
		-760, 610, 180, 4, 0       // things: a bucket and a store in the kennels' passage
	};
	AjarTourCam23 tourCam;

	void Tour(Actor mo)
	{
		if (tic == 2) mo.A_SetRenderStyle(1.0, STYLE_None);
		if (tic < 20 || (tic - 20) % 70) return;
		int i = (tic - 20) / 70, k = 0;
		for (int v = 0; v * 5 < TOUR.Size(); v++)
		{
			int when = int(TOUR[v * 5 + 4]);
			int times = when == 0 ? 2 : 1;
			for (int t = 0; t < times; t++)
			{
				k++;
				if (k - 1 != i) continue;
				bool early = when == 1 || (when == 0 && t == 0);
				double x = TOUR[v * 5], y = TOUR[v * 5 + 1] + (early ? OFF : 0);
				if (!tourCam) tourCam = AjarTourCam23(Actor.Spawn("AjarTourCam23", (x, y, 0)));
				tourCam.SetOrigin((x, y, FZ(x, y) + 41), false);
				tourCam.angle = TOUR[v * 5 + 2];
				tourCam.pitch = TOUR[v * 5 + 3];
				tourCam.ClearInterpolation();
				mo.player.camera = tourCam;
				Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "AJARTEST view=%d place=%d %s (%d,%d) %d", i, v, early ? "THEN" : "NOW", x, y - (early ? OFF : 0), TOUR[v * 5 + 2]);
				return;
			}
		}
		if (i == k) Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "AJARTEST tour over: %d views", k);
	}
}

class AjarTourCam23 : Actor        // the tour's eye (MODE=5): holds still where it is put
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +INVISIBLE +DONTSPLASH CameraHeight 0; Height 2; Radius 1; }
	States { Spawn: TNT1 A -1; Stop; }
}
