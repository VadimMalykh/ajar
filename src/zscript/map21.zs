// MAP21 "In the Long Run" (tools/map_longrun.py; PLAN.md, "MAP21 "In the Long
// Run""): the level's own script, and its checks (LongRunTest, below).
// THEN is NOW + (0, 8192). Frames NOW / THEN: 101/121 the machine (the clocked
// door's alone at both times), 103/123 the corridor's first stretch (NOW the
// clocked door's alone), 104/124 its south end (any door), 105/125 the cellar's
// landing, 108/128 the goods bay, 106/126 optics, 110/130 the lobby; 190 the
// brass frame HOME in the night room THEN (GREEN only, no twin). A colour door
// hung leads to its far side at the frame's time: RED the lobby (both times),
// BLUE the vestibule NOW / the pass office THEN, GREEN the night room. Causes (then.zs): 11 the valve (0 shut,
// 1 open; found open), 12 the belt (0 standing, found; 1 running), 13 the beam
// (0 off, 1 A, 2 B, 3 C; found at C).

// The desk the machine is run from (thing 20187, one, NOW; its panel's line
// does Thing_Activate on it at both times). NOW it is smashed. THEN, with keys 1
// and 2, the keys are turned and stay turned (`started`). The machine runs while
// the keys are turned and the clocked door hangs in its frame (101, or 121:
// either time): the hall THEN brightens, a sound, and the brass shutter in the
// north wall goes up onto the night room. Take the clocked door out of the
// machine and it stops: the hall dims and the shutter comes down, but never
// on anything that stands in it (it waits). Hang it back and it runs again
// (PLAN.md, "MAP21: colour doors by time, the pass office, and the way out
// built"; the graph's walk hallT <-> nightT, keys 12, the clocked door in 101).
class AjarLongRunDesk : Actor
{
	const SHUTTER = 2101;
	const LIGHT_TAG = 2102;
	const OPEN_H = 128;        // the shutter up: its ceiling over its floor (the night room is 160 high)
	const SPEED = 4;           // units a tic, either way
	const DIM = 176; const BRIGHT = 240;
	bool started;              // the keys are turned (for good)
	bool running;              // ... and the clocked door is in the machine
	int startedAt, runs, stops;
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	override void Activate(Actor activator)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		let w = AjarThen.Find();
		if (!h || !w || !activator) return;
		if (!w.InThen(activator.pos.xy))
		{
			h.Say("The desk is smashed.\nNothing on it works now.");
			return;
		}
		if (started)
		{
			h.Say(running ? "The machine is running." : "The keys are turned. The machine waits\nfor the clocked door in its frame.");
			return;
		}
		bool k1 = h.Has(activator, 1), k2 = h.Has(activator, 2);
		if (!k1 || !k2)
		{
			h.Say(!k1 && !k2 ? "Two keys turn here: 1 and 2." : !k1 ? "Key 1 is missing." : "Key 2 is missing.");
			A_StartSound("*usefail", CHAN_AUTO);
			return;
		}
		started = true;
		startedAt = level.maptime;
		if (InMachine())
		{
			Run(true);
			h.Say("You turn the keys.\nThe machine starts on the door it was found with.");
		}
		else
		{
			h.Say("You turn the keys. The frame is empty:\nthe machine waits for the clocked door.");
			A_StartSound("*usefail", CHAN_AUTO);
		}
	}

	static bool InMachine()
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		AjarFrame f = h ? h.FindFrame(101) : null;
		return f && f.door && f.door.IsClocked();
	}

	void Run(bool on)
	{
		running = on;
		if (on) runs++; else stops++;
		let si = level.CreateSectorTagIterator(LIGHT_TAG);
		int s;
		while ((s = si.Next()) >= 0) level.sectors[s].SetLightLevel(on ? BRIGHT : DIM);
		S_StartSound(on ? "weapons/bfgf" : "plats/pt1_stop", CHAN_AUTO, CHANF_UI, 1, ATTN_NONE);
		S_StartSound(on ? "doors/dr1_open" : "doors/dr1_clos", CHAN_AUTO, CHANF_UI, 0.6, ATTN_NONE);      // the shutter
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info the machine %s at t=%d", on ? "runs" : "stops", level.maptime);
	}

	// Does anything stand in the shutter's doorway?
	bool Occupied(Sector s)
	{
		double x1 = 1e9, y1 = 1e9, x2 = -1e9, y2 = -1e9;
		for (int k = 0; k < s.lines.Size(); k++)
		{
			Line l = s.lines[k];
			x1 = min(x1, min(l.v1.p.x, l.v2.p.x)); y1 = min(y1, min(l.v1.p.y, l.v2.p.y));
			x2 = max(x2, max(l.v1.p.x, l.v2.p.x)); y2 = max(y2, max(l.v1.p.y, l.v2.p.y));
		}
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!(a.player || a.bSolid || a.bShootable) || a.bNoBlockmap) continue;
			if (a.pos.x + a.radius <= x1 || a.pos.x - a.radius >= x2 || a.pos.y + a.radius <= y1 || a.pos.y - a.radius >= y2) continue;
			return true;
		}
		return false;
	}

	int waited;                // (the tests) tics the shutter has waited for something in its way
	override void Tick()
	{
		Super.Tick();
		if (!started) return;
		bool want = InMachine();
		if (want != running)
		{
			Run(want);
			let h = AjarHandler(EventHandler.Find("AjarHandler"));
			if (h) h.Say(h.said .. (want ? "\nThe machine runs again: the brass shutter goes up." : "\nThe machine stops: the brass shutter comes down."));
		}
		let si = level.CreateSectorTagIterator(SHUTTER);
		int i;
		while ((i = si.Next()) >= 0)
		{
			Sector s = level.sectors[i];
			double fz = s.floorplane.ZAtPoint(s.centerspot), cz = s.ceilingplane.ZAtPoint(s.centerspot);
			double goal = fz + (running ? OPEN_H : 0);
			if (abs(cz - goal) < 0.01) continue;
			if (goal < cz && Occupied(s)) { waited++; continue; }
			s.MoveCeiling(SPEED, s.ceilingplane.PointToDist(s.centerspot, goal), -1, goal > cz ? 1 : -1, false);
		}
	}

	static AjarLongRunDesk Get() { return AjarLongRunDesk(ThinkerIterator.Create("AjarLongRunDesk").Next()); }
}

// The first time each long cause is changed, one line says it the long way.
class AjarLongRun : EventHandler
{
	const VALVE = 11; const BELT = 12; const BEAM = 13;
	bool told[3];

	static string LineFor(int tid, int s)
	{
		if (tid == VALVE) return s == 0 ? "The valve was never opened." : "The valve has stood open for forty years.";
		if (tid == BELT) return s == 1 ? "The belt has run for forty years." : "The belt has never run.";
		if (s == 0) return "The beam was never switched on.";
		return String.Format("The beam has been on wall %s for forty years.", s == 1 ? "A" : s == 2 ? "B" : "C");
	}

	override void WorldTick()
	{
		if (!(level.mapname ~== "MAP21")) return;
		let th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		for (int i = 0; i < 3; i++)
		{
			if (told[i]) continue;
			let c = th.FindCause(VALVE + i);
			if (!c || !c.timesSet) continue;
			told[i] = true;
			if (h) h.Say(LineFor(c.tid, c.setting));
		}
	}
}

// === The causes made readable (PLAN.md, "MAP21: the causes made readable") ==========================
// THEN the device does the thing, small; NOW its wreck is at the same spot and the result where it was
// putting it. Things placed by tools/map_longrun.py (sections 4 to 6).

// A crate of the goods-in (AjarGoodsIn): THEN, on the belt.
class AjarGoodsCrate : AjarCrate
{
	AjarOldCrate twin;         // NOW: the same crate in dust, while the belt never ran
	int cameOut;               // the tic it came out of the flap into the bay (0: it stood there at the start)
	int fell;                  // the tic it went over the hatch's edge
}

// NOW: a crate that stood on the belt forty years ago and still does, grey-brown with dust. Solid, 32 high.
class AjarOldCrate : Actor
{
	Default { Radius 16; Height 32; Mass 1000; +SOLID +NOBLOOD +DONTTHRUST +NOTAUTOAIMED }
	States { Spawn: AJB0 A -1; Stop; }
	override void PostBeginPlay() { Super.PostBeginPlay(); A_SetTranslation('AjarDustCrate'); }
}

// The goods-in (thing 20188, THEN, in the dark alcove behind the bay's flap; args: the belt's cause, the
// crates standing on the belt at the start, their spacing along it, how far the flap's wall is east of it).
// THEN the crates stand on the belt as found; while it runs they ride east and drop into the hatch, where
// each is gone with a thud, and a new one comes out of the flap each time the last is `spacing` clear of
// it; the belt hums. NOW, while the belt stands (it never ran), each crate standing on it in the bay THEN
// stands on it NOW at the same spot, in dust (AjarOldCrate; it waits while something stands there NOW);
// while it runs there are none (they are in the heap).
class AjarGoodsIn : Actor
{
	const DROP = 24;           // a crate this far under the belt has gone over the hatch's edge
	const MOST = 8;
	AjarThenCause cause;
	AjarThen when;
	Array<AjarGoodsCrate> crates;
	AjarGoodsCrate last;
	int made, gone;            // (the tests) crates come out of the flap, crates gone into the hatch
	Array<int> rides;          // (the tests) tics from the flap to the hatch's edge, a crate each
	bool hum;

	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	double FlapX() { return pos.x + args[3]; }
	static AjarGoodsIn Get() { return AjarGoodsIn(ThinkerIterator.Create("AjarGoodsIn").Next()); }

	AjarGoodsCrate Make(double x)
	{
		let c = AjarGoodsCrate(Spawn("AjarGoodsCrate", (x, pos.y, pos.z)));
		if (c) { crates.Push(c); last = c; }
		return c;
	}

	// Is the crate's place NOW free of anything solid?
	bool Clear(Vector3 p)
	{
		let it = BlockThingsIterator.CreateFromPos(p.x, p.y, p.z, 32, 16, false);
		while (it.Next())
		{
			let a = it.thing;
			if (!a.bSolid || a is "AjarOldCrate") continue;
			if (abs(a.pos.x - p.x) < a.radius + 16 && abs(a.pos.y - p.y) < a.radius + 16 && a.pos.z < p.z + 32 && a.pos.z + a.height > p.z) return false;
		}
		return true;
	}

	override void Tick()
	{
		Super.Tick();
		if (!cause)
		{
			let th = AjarThenHandler.Get();
			if (!th || !th.ready) return;
			cause = th.FindCause(args[0]);
			when = th.when;
			if (!cause || !when) { cause = null; return; }
			for (int k = 1; k <= args[1]; k++) Make(pos.x + args[2] * k);
		}
		bool running = cause.setting == 1;
		if (running != hum)
		{
			hum = running;
			if (hum) A_StartSound("plats/pt1_mid", CHAN_BODY, CHANF_LOOPING, 0.45, ATTN_NORM, 0.6);
			else A_StopSound(CHAN_BODY);
		}
		if (running && crates.Size() < MOST && (!last || last.bDestroyed || last.pos.x - pos.x >= args[2]))
		{
			let c = Make(pos.x);
			if (c) { c.cameOut = -1; made++; }
		}
		bool autotest = CVar.GetCVar("ajar_autotest").GetInt() != 0;
		for (int i = crates.Size() - 1; i >= 0; i--)
		{
			let c = crates[i];
			if (!c || c.bDestroyed) { crates.Delete(i); continue; }
			if (c.cameOut == -1 && c.pos.x >= FlapX()) c.cameOut = max(level.maptime, 1);
			bool over = c.pos.z < pos.z - DROP;
			if (over && !c.fell)
			{
				c.fell = level.maptime;
				if (c.cameOut > 0) rides.Push(c.fell - c.cameOut);
				if (autotest) Console.Printf("AJARTEST info a crate over the hatch's edge at t=%d (%d tics from the flap)", level.maptime, c.cameOut > 0 ? c.fell - c.cameOut : -1);
			}
			if (over && c.pos.z <= c.floorz + 0.5)
			{
				c.A_StartSound("plats/pt1_stop", CHAN_AUTO, 0, 1, ATTN_NORM, 0.7);       // a thud, and it is gone
				if (c.twin) c.twin.Destroy();
				c.Destroy();
				crates.Delete(i);
				gone++;
				continue;
			}
			// NOW: on the belt in the bay, while it stands
			bool want = cause.setting == 0 && !over && c.pos.x - c.radius >= FlapX() && abs(c.pos.z - pos.z) < 1;
			if (want)
			{
				Vector3 p = (when.Now(c.pos.xy), c.pos.z);
				if (!c.twin) { if (Clear(p)) c.twin = AjarOldCrate(Spawn("AjarOldCrate", p)); }
				else if ((c.twin.pos.xy - p.xy).Length() > 0.01) c.twin.SetOrigin(p, true);
			}
			else if (c.twin) { c.twin.Destroy(); c.twin = null; }
		}
	}

	// (the tests) the crates THEN standing on the belt in the bay; and NOW's
	int OnBelt()
	{
		int n = 0;
		for (int i = 0; i < crates.Size(); i++)
			if (crates[i] && !crates[i].bDestroyed && crates[i].pos.x - 16 >= FlapX() && abs(crates[i].pos.z - pos.z) < 1) n++;
		return n;
	}
}

// NOW: the heap's rumble while the cause's sectors move (thing 20192; args: the cause).
class AjarRumble : Actor
{
	AjarThenCause cause;
	bool on;
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
	override void Tick()
	{
		Super.Tick();
		if (!cause)
		{
			let th = AjarThenHandler.Get();
			if (!th || !th.ready) return;
			cause = th.FindCause(args[0]);
			if (!cause) return;
		}
		bool moving = !cause.arrived;
		if (moving == on) return;
		on = moving;
		if (on) A_StartSound("plats/pt1_mid", CHAN_BODY, CHANF_LOOPING, 1, ATTN_NORM, 0.5);
		else { A_StopSound(CHAN_BODY); A_StartSound("plats/pt1_stop", CHAN_AUTO, 0, 1, ATTN_NORM, 0.6); }
	}
}

// A thin stream of water from a pipe's mouth (thing 20191, at both times; args: the cause, the setting it
// falls in, the mouth's height over the floor here, and NOW the tag of the basin whose water it falls onto,
// THEN 0: it falls to the floor and leaves a wet patch, a step out from the wall the thing faces away from).
// Shown and hidden by the cause's setting at once; it trickles while shown.
class AjarStream : Actor
{
	AjarThenCause cause;
	AjarBasin basin;
	Actor patch;
	double floorAt;
	bool flowing;
	Default { +NOBLOCKMAP +NOGRAVITY +DONTSPLASH RenderStyle "Translucent"; Alpha 0.9; XScale 2; }
	States { Spawn: AJXS ABCD 3 Bright; Loop; }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		floorAt = pos.z;
		bInvisible = true;
	}
	double Mouth() { return floorAt + args[2]; }
	double Bottom() { return basin && basin.w > floorAt ? basin.w : floorAt; }
	bool Shown() { return flowing; }

	override void Tick()
	{
		Super.Tick();
		if (!cause)
		{
			let th = AjarThenHandler.Get();
			if (!th || !th.ready) return;
			cause = th.FindCause(args[0]);
			if (!cause) return;
			if (args[3])
			{
				let wh = AjarWaterHandler.Get();
				if (wh) basin = wh.BasinOfTag(args[3]);
			}
			else
			{
				patch = Spawn("AjarStreamPatch", (pos.xy + (cos(angle), sin(angle)) * 12, floorAt + 0.3));
				if (patch) patch.bInvisible = true;
			}
		}
		bool on = cause.setting == args[1];
		if (on)
		{
			double b = Bottom();
			if (abs(pos.z - b) > 0.01) SetZ(b);
			scale.y = max(Mouth() - b, 1) / 64.;
		}
		bInvisible = !on;
		if (patch) patch.bInvisible = !on;
		if (on == flowing) return;
		flowing = on;
		if (on) A_StartSound("ajar/water", CHAN_BODY, CHANF_LOOPING, 0.3, ATTN_NORM);
		else A_StopSound(CHAN_BODY);
	}
}

class AjarStreamPatch : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +FLATSPRITE +NOINTERACTION RenderStyle "Translucent"; Alpha 0.85; }
	States { Spawn: AJXP A -1; Stop; }
}

// NOW: the emitter's wreck on its inlay (thing 20189), where THEN's stands. Not solid, as THEN's is not.
class AjarEmitterWreck : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY }
	// the apparatus's wreck of the emitter (tools/gfx_longrun.py, AJUE D, E, F) in the look args[0] (1 to 3)
	States { Spawn: AJUE D -1; Stop; }
	override void PostBeginPlay() { Super.PostBeginPlay(); frame = 3 + clamp(args[0], 1, 3) - 1; }
}

// The checks: MAP=MAP21 MODE=n tools/smoke.sh.
//   1 the way through, walked: every stage on foot, through the doors, by USE
//     (nothing posed, nothing ridden by script), with the checks on the way
//   2 the three causes set by shots from NOW through the clocked door (posed)
//   3 views (tools/smoke_MAP21_3.cfg shoots every 70 tics)
//   5 the wall over every frame and far side, THEN and NOW (tools/smoke_MAP21_5.cfg shoots every 35 tics)
//   9 doors beside walls and levers (leaf.zs): the clocked door's leaf in the machine keeps off its wings, at both
//     times alike; real USE presses at each cause's lever with a door hung beside it (RED, the clocked door hung
//     THEN, the clocked door hung NOW and its shadow THEN) from in front of the lever, of its end nearer the frame
//     and of the frame: the leaf (hung on the jamb away from the lever) is not between, the lever moves and the
//     door stays; aimed at the leaf the door comes down, aimed at the empty frame it is hung; NOW
//     the same levers are dead (said what a press does);
//     the desk's panel at both times with the clocked door in the machine (posed; tools/smoke_MAP21_9.cfg)
class LongRunTest : EventHandler
{
	const OFF = 8192;
	const LX = 2560;
	const WALKKEY = 0x1900;
	const VALVE = 11; const BELT = 12; const BEAM = 13;
	const BASIN = 2110;
	const PIT = -200;
	int tic, checks, fails;
	int step, cur, stepTic;
	bool entered;
	AjarHandler h;
	AjarThenHandler th;
	AjarDoor clocked, shadow, red, blue, green;
	AjarLongRunDesk desk;
	int viewN;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "MAP21"; }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	// --- the steps: each `if (S()) {...}` is one, done in turn; Next() moves on --------------------------
	bool S() { return cur++ == step; }
	void Next() { step++; entered = false; }
	bool First() { if (!entered) { entered = true; stepTic = tic; return true; } return false; }
	int Age() { return tic - stepTic; }

	bool InThen(Actor mo) { return th.when.InThen(mo.pos.xy); }
	string Where(Actor mo) { return String.Format("(%.1f,%.1f,%.1f) angle %.1f %s", mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, InThen(mo) ? "THEN" : "NOW"); }
	AjarFrame F(int id) { return h.FindFrame(id); }
	Sector SectorAt(double x, double y) { return level.PointInSector((x, y)); }
	double FZ(double x, double y) { Sector s = SectorAt(x, y); return s.floorplane.ZatPoint(s.centerspot); }
	double CZ(double x, double y) { Sector s = SectorAt(x, y); return s.ceilingplane.ZatPoint(s.centerspot); }
	bool Open(double x, double y) { return CZ(x, y) > FZ(x, y) + 56; }
	AjarThenCause Cause(int tid) { return th.FindCause(tid); }
	double Water() { let wh = AjarWaterHandler.Get(); let b = wh ? wh.BasinOfTag(BASIN) : null; return b ? b.w : -9999; }
	bool Said(string part) { return h.said.IndexOf(part) >= 0; }
	int Ambushers(int cause)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == cause) n++;
		return n;
	}
	AjarPressureDoor PDoor() { return AjarPressureDoor(ThinkerIterator.Create("AjarPressureDoor").Next()); }

	// --- the player's controls, as thentest.zs ---------------------------------------------------
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
			// toward the goal; back on the keys in time to stop on it (Doom's friction leaves 9.6 tics' worth of
			// speed to slide), and done once there and still
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
		mo.SetOrigin((x, y, level.PointInSector((x, y)).floorplane.ZatPoint((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = pushing = false;
		Keys();
	}

	// Walk to x, y (a real walk: the engine's own movement, keys "held"); stuck: a failed check, and on.
	void Go(Actor mo, double x, double y)
	{
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
			Check(String.Format("walkTo_%d_%d", x, y), false, Where(mo));
			walking = false; Keys(); Next();
		}
	}
	// Walk on facing `ang` for n tics.
	void Push(Actor mo, double ang, int n)
	{
		if (First()) { pushAngle = ang; pushing = true; walking = false; }
		if (Age() >= n) { pushing = false; Keys(); Next(); }
	}
	// Walk on facing `ang` through a hung door (until the player is carried elsewhere), and 14 tics out of it.
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
			desk = AjarLongRunDesk.Get();
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.IsShadow()) shadow = d;
				else if (d.IsClocked()) clocked = d;
				else if (d.args[1] == 1) red = d;
				else if (d.args[1] == 2) blue = d;
				else if (d.args[1] == 3) green = d;
			}
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			let mi = ThinkerIterator.Create("Actor");          // (mode 1's are gone already: ajar.zs)
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster) a.Destroy();
			Info(String.Format("causes %d, cause sectors %d, emitters %d, belts %d, targets %d; clocked %d shadow %d red %d blue %d desk %d",
				th.causes.Size(), th.secIdx.Size(), th.emitters.Size(), th.belts.Size(), th.targets.Size(),
				clocked != null, shadow != null, red != null, blue != null, desk != null));
		}
		cur = 0;
		if (mode == 1) Walk(mo);
		else if (mode == 2) Shots(mo);
		else if (mode == 3) Views(mo);
		else if (mode == 4) Causes(mo);
		else if (mode == 5) FrameViews(mo);
		else if (mode == 9) Doors(mo);
		Drive(mo);
		if (tic % 70 == 0 && mode != 3) Info(String.Format("t=%d step %d %s carried %s", tic, step, Where(mo), h.carried ? h.carried.Label() : "-"));
	}

	void Done() { Console.Printf("AJARTEST longRunDone=1 checks=%d failed=%d", checks, fails); Next(); }

	// === MODE=1: the way through, on foot ==============================================================
	void Walk(Actor mo)
	{
		if (S()) { Wait(2); }
		if (S())
		{
			Check("clockedFoundIn101", F(101).door == clocked && F(121).door == shadow && clocked.frame == F(101), h.said);
			Check("valveFoundOpen", Cause(VALVE).setting == 1 && abs(Water() - (-72)) < 1, String.Format("water %.1f", Water()));
			Check("beltFoundStanding", Cause(BELT).setting == 0 && abs(FZ(2000, 1150) + 112) < 1);
			Check("beamFoundAtC", Cause(BEAM).setting == 3 && CZ(1672, 2576) > 50 && CZ(1144, 2576) < -39);
			Check("nowMusicAtStart", th.musicThen == 0);
			Check("shutterShutAtStart", !desk.started && !desk.running && Shutter() < 1, String.Format("shutter %.0f", Shutter()));
			Check("greenLeansInBayCellar", green && !green.frame && !green.carried && FZ(green.pos.x, green.pos.y) < -100, green ? String.Format("(%.0f,%.0f)", green.pos.x, green.pos.y) : "no GREEN");
			Next();
		}
		// the hall is sealed NOW: its one door is bolted on the vestibule's side
		if (S()) Go(mo, 300, 80);
		if (S()) Go(mo, 700, 80);
		if (S()) Go(mo, 990, 384);
		if (S()) Use(mo, 0);
		if (S()) Push(mo, 0, 35);
		if (S()) { Check("hallSealedNow", !Open(1032, 384) && mo.pos.x < 1024, Where(mo)); Next(); }
		// the desk NOW is smashed
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 512, 222);
		if (S()) Use(mo, 270);
		if (S()) { Check("deskSmashedNow", Said("smashed"), h.said); Next(); }
		// through the clocked door into the hall THEN
		if (S()) Go(mo, 512, 280);
		if (S()) Through(mo, 90);
		if (S()) { Check("walkedIntoHallThen", InThen(mo) && mo.pos.y < OFF + 320 && abs(Actor.DeltaAngle(mo.angle, 270)) < 2, Where(mo)); Next(); }
		if (S()) Wait(3);
		if (S()) { Check("thenMusicThen", th.musicThen == 1); Next(); }
		if (S()) Go(mo, 512, OFF + 222);
		if (S()) Use(mo, 270);
		if (S()) { Check("deskWantsKeys", Said("keys") && !desk.started, h.said); Next(); }
		// take it THEN: both frames empty
		if (S()) Go(mo, 512, OFF + 290);
		if (S()) Use(mo, 90);
		if (S()) { Check("tookClockedThen", h.carried == clocked && !F(101).door && !F(121).door, h.said); Next(); }
		// to the vestibule THEN; the turnstile lets no door through
		if (S()) Go(mo, 512, OFF + 232);
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 700, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 472);
		if (S()) Push(mo, 0, 35);
		if (S()) { Check("noDoorPastTurnstile", mo.pos.x < 1296 && h.carried == clocked, Where(mo) .. " " .. h.said); Next(); }
		// out over the goods edge into the pocket, door in hand; not back up
		if (S()) Go(mo, 1250, OFF + 320);
		if (S()) Push(mo, 0, 30);
		if (S()) { Check("downTheGoodsEdge", mo.pos.x > 1316 && abs(mo.pos.z + 40) < 1 && h.carried == clocked, Where(mo)); Next(); }
		if (S()) Push(mo, 180, 40);
		if (S()) { Check("goodsEdgeOneWay", mo.pos.x > 1312, Where(mo)); Next(); }
		// hang it in 123 (THEN, any door): its shadow in 103 NOW
		if (S()) Go(mo, 1470, OFF + 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("hungIn123", F(123).door == clocked && F(103).door == shadow && !h.carried, h.said); Next(); }
		if (S()) Through(mo, 0);
		if (S()) { Check("outOf103Now", !InThen(mo) && mo.pos.x > 1312 && mo.pos.x < 1504, Where(mo)); Next(); }
		if (S()) Go(mo, 1470, 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClockedNow", h.carried == clocked && !F(103).door && !F(123).door, h.said); Next(); }

		// --- the cellar: hang it in 105, shut the valve THEN, the pit drains, the store, key 2 ------------
		if (S()) Go(mo, 1408, 520);
		if (S()) Go(mo, 1408, 1472);
		if (S()) Go(mo, 1340, 1472);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1180, 1472);
		if (S()) Go(mo, 1200, 1280);
		if (S()) Use(mo, 0);
		if (S()) { Check("hungIn105", F(105).door == clocked && F(125).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 0);
		if (S()) { Check("inCellarThen", InThen(mo) && mo.pos.x < 1232 && mo.pos.x > 1056, Where(mo)); Next(); }
		if (S()) Go(mo, 1200, OFF + 1360);                                         // the lever, beside 125
		if (S()) Use(mo, 0);
		if (S()) Wait(3);
		if (S())
		{
			Check("valveShutThen", Cause(VALVE).setting == 0, String.Format("setting %d", Cause(VALVE).setting));
			Check("valveLine", h.said == "The valve was never opened.", h.said);
			Next();
		}
		if (S()) Go(mo, 1200, OFF + 1280);
		if (S()) Through(mo, 0);
		if (S()) Wait(80);
		if (S()) { Check("dryPit", !InThen(mo) && Water() <= PIT + 1, String.Format("water %.1f %s", Water(), Where(mo))); Next(); }
		if (S()) Go(mo, 1200, 1280);
		if (S()) Use(mo, 0);
		if (S()) { Check("tookClockedFrom105", h.carried == clocked, h.said); Next(); }
		if (S()) Go(mo, 1080, 1136);
		if (S()) Go(mo, 816, 1136);
		if (S()) { Check("downThePitStair", abs(mo.pos.z - PIT) < 2, Where(mo)); Next(); }
		if (S()) Go(mo, 800, 1540);
		if (S()) Go(mo, 672, 1560);
		if (S()) Use(mo, 90);
		if (S()) Wait(40);
		if (S()) { let pd = PDoor(); Check("storeOpens", pd && pd.IsOpen(), h.said); Next(); }
		if (S()) Go(mo, 672, 1700);
		if (S()) { Check("key2", h.Has(mo, 2), Where(mo)); Next(); }
		if (S()) Go(mo, 672, 1560);
		if (S()) Go(mo, 800, 1540);
		if (S()) Go(mo, 860, 1136);
		if (S()) Go(mo, 1080, 1136);
		if (S()) { Check("upThePitStair", abs(mo.pos.z + 40) < 2, Where(mo)); Next(); }
		if (S()) Go(mo, 1180, 1472);
		if (S()) Go(mo, 1215, 1472);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1472);

		// --- the goods bay: hang it in 108, start the belt THEN, up the heap, RED ------------------------
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1480, 1312);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1600, 1312);
		if (S()) Go(mo, 1936, 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("hungIn108", F(108).door == clocked && F(128).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("inBayThen", InThen(mo) && mo.pos.x > 1568, Where(mo)); Next(); }
		if (S()) Go(mo, 1872, OFF + 1500);                                         // the lever, beside 128
		if (S()) Use(mo, 90);
		if (S()) Wait(3);
		if (S())
		{
			Check("beltRunsThen", Cause(BELT).setting == 1);
			Check("beltLine", h.said == "The belt has run for forty years.", h.said);
			Next();
		}
		if (S()) Go(mo, 1936, OFF + 1500);
		if (S()) Through(mo, 90);
		if (S()) Wait(80);
		if (S()) { Check("heapUp", abs(FZ(1872, 1150) + 16) < 1 && abs(FZ(1936, 1150) - 8) < 1 && abs(FZ(2000, 1150) - 32) < 1 && !InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 1800, 1260);
		if (S()) Go(mo, 1872, 1150);
		if (S()) Go(mo, 1936, 1150);
		if (S()) Go(mo, 2000, 1150);
		if (S()) Go(mo, 2096, 1150);
		if (S()) { Check("galleryOnFoot", abs(mo.pos.z - 56) < 1, Where(mo)); Next(); }
		if (S()) Go(mo, 2096, 1440);
		if (S()) Use(mo, 90);
		if (S()) { Check("tookRed", h.carried == red, h.said); Next(); }
		// down off the gallery to 108; through the clocked door with RED; the belt stopped by its lever THEN
		if (S()) Go(mo, 1990, 1450);
		if (S()) Go(mo, 1936, 1500);
		if (S()) Through(mo, 90);
		if (S()) { Check("redIntoBayThen", InThen(mo) && h.carried == red, Where(mo)); Next(); }
		if (S()) Go(mo, 1872, OFF + 1500);
		if (S()) Use(mo, 90);
		if (S()) Wait(3);
		if (S()) { Check("beltStoppedThen", Cause(BELT).setting == 0, String.Format("setting %d", Cause(BELT).setting)); Next(); }
		// RED swapped in for the clocked door in 128 (THEN): it opens on its far side THEN, the lobby THEN
		if (S()) Go(mo, 1936, OFF + 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("redSwappedInAt128", h.carried == clocked && F(128).door == red && !F(108).door && red.args[0] == 221
			&& h.said == "You swap the clocked door for the RED one.", String.Format("RED leads to %d; ", red.args[0]) .. h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("intoLobbyThen", InThen(mo) && mo.pos.x > LX && mo.pos.x < LX + 1024, Where(mo)); Next(); }
		if (S()) Go(mo, LX + 330, OFF + 320);
		if (S()) Go(mo, LX + 330, OFF + 470);
		if (S()) Go(mo, LX + 512, OFF + 470);
		if (S()) { Check("key1", h.Has(mo, 1), Where(mo)); Next(); }
		if (S()) Wait(250);
		if (S()) { Check("key1Ambush", Ambushers(1) == 0, String.Format("%d still to come", Ambushers(1))); Next(); }
		if (S()) Go(mo, LX + 330, OFF + 470);
		if (S()) Go(mo, LX + 330, OFF + 320);
		if (S()) Go(mo, LX + 40, OFF + 320);
		if (S()) Through(mo, 180);
		if (S()) { Check("backFromLobbyThen", InThen(mo) && mo.pos.x > 1568 && mo.pos.x < 2160 && mo.pos.y < OFF + 1536, Where(mo)); Next(); }
		// the clocked door swapped back in for RED: through it NOW, and RED swapped in for it in 108: the lobby NOW
		if (S()) Go(mo, 1936, OFF + 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("clockedSwappedInAt128", h.carried == red && F(128).door && F(128).door.IsClocked() && F(108).door && F(108).door.IsClocked() && red.args[0] == 201, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) Wait(60);
		if (S()) { Check("heapDown", !InThen(mo) && abs(FZ(2000, 1150) + 112) < 1 && abs(FZ(1872, 1150) + 64) < 1, Where(mo)); Next(); }
		if (S()) Go(mo, 1936, 1500);
		if (S()) Use(mo, 90);
		if (S()) { Check("redSwappedInAt108", h.carried == clocked && F(108).door == red && !F(128).door && red.args[0] == 201, h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) { Check("redNowLeadsToLobbyNow", !InThen(mo) && mo.pos.x > LX && mo.pos.x < LX + 1024, Where(mo)); Next(); }
		if (S()) Go(mo, LX + 40, 320);
		if (S()) Through(mo, 180);
		if (S()) { Check("backFromLobbyNow", !InThen(mo) && mo.pos.x > 1568 && mo.pos.x < 2160, Where(mo)); Next(); }

		// --- the clocked door to 106: optics, the beam to A, BLUE --------------------------------------
		if (S()) Go(mo, 1600, 1312);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1408, 2228);
		if (S()) Use(mo, 90);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2380);
		if (S()) Go(mo, 1568, 2360);
		if (S()) Use(mo, 270);
		if (S()) { Check("hungIn106", F(106).door == clocked && F(126).door == shadow, h.said); Next(); }
		if (S()) Through(mo, 270);
		if (S()) { Check("inOpticsThen", InThen(mo) && mo.pos.y > OFF + 2320, Where(mo)); Next(); }
		if (S()) Go(mo, 1632, OFF + 2352);                                         // the lever, beside 126
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S()) { Check("beamLine", h.said == "The beam was never switched on.", h.said); Next(); }
		if (S()) Wait(10);
		if (S()) Use(mo, 270);
		if (S()) Wait(3);
		if (S()) { Check("beamAThen", Cause(BEAM).setting == 1, String.Format("setting %d", Cause(BEAM).setting)); Next(); }
		if (S()) Go(mo, 1568, OFF + 2360);
		if (S()) Through(mo, 270);
		if (S()) Wait(160);
		if (S()) { Check("holeAAlone", CZ(1144, 2576) > 50 && CZ(1408, 2840) < -39 && CZ(1672, 2576) < -39 && !InThen(mo),
			String.Format("A %.0f B %.0f C %.0f", CZ(1144, 2576), CZ(1408, 2840), CZ(1672, 2576))); Next(); }
		if (S()) Go(mo, 1200, 2576);
		if (S()) Go(mo, 1090, 2576);
		if (S()) Use(mo, 180);
		if (S()) { Check("tookBlue", h.carried == blue, h.said); Next(); }

		// --- BLUE swapped in for the clocked door in 106: the vestibule NOW; the bolts drawn; the hall wakes ---
		if (S()) Go(mo, 1200, 2576);
		if (S()) Go(mo, 1568, 2360);
		if (S()) Use(mo, 270);
		if (S()) { Check("blueSwappedInAt106", h.carried == clocked && F(106).door == blue && !F(126).door && blue.args[0] == 202, h.said); Next(); }
		if (S()) Through(mo, 270);
		if (S()) Go(mo, 1168, 300);
		if (S()) Wait(40);
		if (S()) { Check("boltsDrawn", Open(1032, 384) && Open(1304, 304) && mo.pos.x > 1040 && mo.pos.x < 1296 && !InThen(mo), Where(mo)); Next(); }
		if (S()) Wait(300);
		if (S()) { Check("hallWakes", Ambushers(62) == 0, String.Format("%d still to come", Ambushers(62))); Next(); }
		// the clocked door back into the machine (the keys not turned yet: it stands)
		if (S()) Go(mo, 1100, 384);
		if (S()) Go(mo, 960, 384);
		if (S()) { Check("hallNowFromVestibule", mo.pos.x < 1024 && !InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 512, 232);                                                  // between the machine's wings
		if (S()) Go(mo, 512, 280);
		if (S()) Use(mo, 90);
		if (S()) { Check("clockedBackIn101", F(101).door == clocked && F(121).door == shadow && !desk.running && Shutter() < 1, h.said); Next(); }

		// --- BLUE hung THEN leads to the pass office THEN (the booth; the secret); the keys turned; the shutter --
		if (S()) Go(mo, 512, 232);
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 960, 384);
		if (S()) Go(mo, 1100, 384);
		if (S()) Go(mo, 1250, 304);
		if (S()) Go(mo, 1408, 304);
		if (S()) Go(mo, 1408, 2228);
		if (S()) Use(mo, 90);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2380);
		if (S()) Go(mo, 1568, 2360);
		if (S()) Use(mo, 270);
		if (S()) { Check("tookBlueFrom106", h.carried == blue && blue.args[0] == 202, h.said); Next(); }
		if (S()) Go(mo, 1408, 2345);
		if (S()) Use(mo, 270);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 2200);
		if (S()) Go(mo, 1408, 304);
		if (S()) Go(mo, 1250, 304);
		if (S()) Go(mo, 1100, 384);
		if (S()) Go(mo, 960, 384);
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 512, 232);
		if (S()) Go(mo, 512, 280);
		if (S()) Through(mo, 90);
		if (S()) { Check("blueIntoHallThen", InThen(mo) && h.carried == blue, Where(mo)); Next(); }
		if (S()) Go(mo, 512, OFF + 222);
		if (S()) Use(mo, 270);
		if (S()) Wait(5);
		if (S()) { Check("machineStarts", desk.started && desk.running, h.said); Next(); }
		if (S()) Wait(60);
		if (S()) { Check("shutterOpen", Shutter() > 100 && Open(512, OFF + 776), String.Format("shutter %.0f", Shutter())); Next(); }
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 700, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 384);
		if (S()) Go(mo, 1250, OFF + 320);
		if (S()) Push(mo, 0, 30);
		if (S()) Go(mo, 1470, OFF + 480);
		if (S()) Use(mo, 0);
		if (S()) { Check("blueHungIn123", F(123).door == blue && blue.args[0] == 222 && !F(103).door, String.Format("BLUE leads to %d; ", blue.args[0]) .. h.said); Next(); }
		if (S()) { secretsWere = level.found_secrets; Next(); }
		if (S()) Through(mo, 0);
		if (S()) Wait(10);
		if (S())
		{
			Check("blueThenLeadsToTheBooth", InThen(mo) && mo.pos.x > 1112 && mo.pos.x < 1224 && mo.pos.y > OFF + 224 && mo.pos.y < OFF + 280, Where(mo));
			Check("megasphereIsTheSecret", level.found_secrets == secretsWere + 1 && mo.health >= 200, String.Format("secrets %d -> %d of %d, health %d", secretsWere, level.found_secrets, level.total_secrets, mo.health));
			Next();
		}
		if (S()) Through(mo, 270);
		if (S()) { Check("backFromTheBooth", InThen(mo) && mo.pos.x > 1312 && mo.pos.x < 1504 && mo.pos.y < OFF + 640, Where(mo)); Next(); }
		// BLUE stays in 123; up the turnstile, empty-handed
		if (S()) Go(mo, 1340, OFF + 472);
		if (S()) Push(mo, 180, 30);
		if (S()) { Check("upTheTurnstile", mo.pos.x < 1296 && InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 1250, OFF + 384);
		if (S()) Go(mo, 700, OFF + 384);
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 512, OFF + 232);
		if (S()) Go(mo, 512, OFF + 290);
		// the clocked door out of the machine: it stops, the shutter comes down; back: it runs, the shutter goes up
		if (S()) Use(mo, 90);
		if (S()) Wait(60);
		if (S()) { Check("clockedOutShutterShuts", h.carried == clocked && !desk.running && Shutter() < 1, String.Format("shutter %.0f; ", Shutter()) .. h.said); Next(); }
		if (S()) Use(mo, 90);
		if (S()) Wait(60);
		if (S()) { Check("clockedBackShutterOpens", F(121).door == clocked && desk.running && Shutter() > 100, String.Format("shutter %.0f; ", Shutter()) .. h.said); Next(); }

		// --- GREEN from the bay cellar (the belt standing); its ambush in the bay ----------------------------
		if (S()) Through(mo, 90);
		if (S()) { Check("backInHallNow", !InThen(mo), Where(mo)); Next(); }
		if (S()) Go(mo, 512, 232);
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 960, 384);
		if (S()) Go(mo, 1100, 384);
		if (S()) Go(mo, 1250, 304);
		if (S()) Go(mo, 1408, 304);
		if (S()) Go(mo, 1408, 1312);
		if (S()) Go(mo, 1480, 1312);
		if (S()) Use(mo, 0);
		if (S()) Wait(40);
		if (S()) Go(mo, 1600, 1312);
		if (S()) Go(mo, 1872, 1260);
		if (S()) Go(mo, 1872, 1150);
		if (S()) Go(mo, 1936, 1150);
		if (S()) Go(mo, 2000, 1150);
		if (S()) Go(mo, 2000, 1050);
		if (S()) { Check("downTheHatchStair", abs(mo.pos.z + 112) < 1, Where(mo)); Next(); }
		if (S()) { Check("greenAmbushWaitsInBay", Ambushers(13) == 4 && InBay(13) == 4, String.Format("%d to come, %d of them in the bay", Ambushers(13), InBay(13))); Next(); }
		if (S()) Go(mo, 1975, 952);
		if (S()) Use(mo, 180);
		if (S()) { Check("tookGreen", h.carried == green, h.said); Next(); }
		if (S()) Wait(210);
		if (S()) { Check("greenAmbushCame", Ambushers(13) == 0, String.Format("%d still to come", Ambushers(13))); Next(); }
		if (S()) Go(mo, 2000, 1050);
		if (S()) Go(mo, 2000, 1150);
		if (S()) Go(mo, 1936, 1150);
		if (S()) Go(mo, 1872, 1150);
		if (S()) Go(mo, 1872, 1260);
		if (S()) { Check("upTheHatchStair", abs(mo.pos.z + 40) < 1, Where(mo)); Next(); }
		if (S()) Go(mo, 1600, 1312);
		if (S()) Use(mo, 180);
		if (S()) Wait(40);
		if (S()) Go(mo, 1408, 1312);
		// GREEN hung NOW (in 104, the corridor's south end): the night room NOW, dead; and back
		if (S()) Go(mo, 1408, 260);
		if (S()) Go(mo, 1376, 200);
		if (S()) Use(mo, 270);
		if (S()) { Check("greenHungIn104", F(104).door == green && green.args[0] == 203 && !F(124).door, h.said); Next(); }
		if (S()) { Check("deadNightRoomBonuses", Bonuses() == 4, String.Format("%d", Bonuses())); Next(); }
		if (S()) Through(mo, 270);
		if (S()) { Check("greenNowLeadsToDeadNightRoom", !InThen(mo) && mo.pos.x > 352 && mo.pos.x < 672 && mo.pos.y > 784 && mo.pos.y < 1040, Where(mo)); Next(); }
		if (S()) Go(mo, 640, 912);
		if (S()) { Check("deadNightRoomBonusesTaken", Bonuses() == 0, String.Format("%d left", Bonuses())); Next(); }
		if (S()) Go(mo, 400, 912);
		if (S()) Through(mo, 180);
		if (S()) { Check("backFromDeadNightRoom", !InThen(mo) && mo.pos.x > 1312 && mo.pos.x < 1504 && mo.pos.y < 400, Where(mo)); Next(); }
		if (S()) Go(mo, 1376, 200);
		if (S()) Use(mo, 270);
		if (S()) { Check("tookGreenFrom104", h.carried == green && green.args[0] == 203, h.said); Next(); }

		// --- GREEN to the hall THEN, through the shutter into the night room; GREEN in 190; out ---------------
		if (S()) Go(mo, 1408, 304);
		if (S()) Go(mo, 1250, 304);
		if (S()) Go(mo, 1100, 384);
		if (S()) Go(mo, 960, 384);
		if (S()) Go(mo, 700, 232);
		if (S()) Go(mo, 512, 232);
		if (S()) Go(mo, 512, 280);
		if (S()) Use(mo, 90);                                                       // 101 takes only the clocked door
		if (S()) { Check("plainRefusedAt101", h.carried == green && F(101).door && h.said == "This frame takes only the clocked door.", h.said); Next(); }
		if (S()) Through(mo, 90);
		if (S()) Go(mo, 700, OFF + 232);
		if (S()) Go(mo, 700, OFF + 600);
		if (S()) Go(mo, 512, OFF + 700);
		if (S()) Go(mo, 512, OFF + 860);
		if (S()) { Check("throughTheShutter", InThen(mo) && mo.pos.y > OFF + 784 && h.carried == green, Where(mo)); Next(); }
		if (S()) Go(mo, 630, OFF + 912);
		if (S()) Use(mo, 0);
		if (S()) { Check("greenHungIn190", F(190).door == green && green.args[0] == 223 && h.wayOutBuilt, String.Format("GREEN leads to %d; ", green.args[0]) .. h.said); Next(); }
		if (S()) Done();
		// out: into the brass frame's mouth (WorldUnloaded says it)
		if (S()) Push(mo, 0, 60);
	}
	int secretsWere;
	double Shutter() { return CZ(512, OFF + 776) - FZ(512, OFF + 776); }
	// the ambush of `cause` still to come that stands in the goods bay (NOW)
	int InBay(int cause)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarAmbush");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == cause && a.pos.x > 1568 && a.pos.x < 2160 && a.pos.y > 1088 && a.pos.y < 1536) n++;
		return n;
	}
	// the armour bonuses left in the dead night room NOW
	int Bonuses()
	{
		int n = 0;
		let it = ThinkerIterator.Create("ArmorBonus");
		Actor a;
		while (a = Actor(it.Next())) if (a.pos.x > 352 && a.pos.x < 672 && a.pos.y > 784 && a.pos.y < 1040) n++;
		return n;
	}

	override void WorldUnloaded(WorldEvent e)
	{
		if (!Testing() || CVar.GetCVar("ajar_autotest").GetInt() != 1) return;
		Console.Printf("AJARTEST outByTheWayOut=%d  (step %d, %s)", h && h.wayOutBuilt && desk && desk.running && th && players[consoleplayer].mo && th.when.InThen(players[consoleplayer].mo.pos.xy), step, e.NextMap);
	}

	// === MODE=2: the causes set by shots from NOW through the clocked door (posed) ===========================
	double AimThrough(Actor mo, int src, int dst, Vector2 p)
	{
		Vector2 img = AjarSight.ImageThrough(h.FindLine(src), h.FindLine(dst), p);
		return VectorAngle(img.x - mo.pos.x, img.y - mo.pos.y);
	}
	void Shoot(Actor mo, double ang, double pitch = 0)
	{
		mo.angle = ang; mo.pitch = pitch;
		FTranslatedLineTarget t;
		let puff = mo.LineAttack(ang, 4096, pitch, 10, 'Hitscan', "BulletPuff", LAF_NORANDOMPUFFZ, t);
		Info(String.Format("shot from (%.0f,%.0f) at %.1f pitch %.1f: puff %s, hit %s", mo.pos.x, mo.pos.y, ang, pitch,
			puff ? String.Format("(%.0f,%.0f,%.0f)", puff.pos.x, puff.pos.y, puff.pos.z) : "none", t.linetarget ? t.linetarget.GetClassName() : 'none'));
	}
	// A shot through the hung door src (its far side dst) at the point p (THEN), z its height: aimed as a player
	// aims, angle and pitch, from where the player stands.
	void ShootAt(Actor mo, int src, int dst, Vector3 p)
	{
		Vector2 img = AjarSight.ImageThrough(h.FindLine(src), h.FindLine(dst), p.xy);
		double dist = (img - mo.pos.xy).Length();
		double sz = mo.pos.z + mo.height * 0.5 - mo.floorclip + PlayerPawn(mo).AttackZOffset * mo.player.crouchfactor;
		Shoot(mo, VectorAngle(img.x - mo.pos.x, img.y - mo.pos.y), -atan2(p.z - sz, dist));
	}
	string Holes() { return String.Format("A %.0f B %.0f C %.0f", CZ(1144, 2576), CZ(1408, 2840), CZ(1672, 2576)); }
	bool HoleOpen(int n) { return n == 1 ? CZ(1144, 2576) > 50 : n == 2 ? CZ(1408, 2840) > 50 : CZ(1672, 2576) > 50; }
	bool HoleShut(int n) { return n == 1 ? CZ(1144, 2576) < -39 : n == 2 ? CZ(1408, 2840) < -39 : CZ(1672, 2576) < -39; }
	bool OnlyHole(int n) { for (int k = 1; k <= 3; k++) if (k == n ? !HoleOpen(k) : !HoleShut(k)) return false; return true; }

	void Shots(Actor mo)
	{
		if (S()) Wait(2);
		if (S()) { Pose(mo, 512, 280, 90); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("tookClocked", h.carried == clocked, h.said); Next(); }
		// the valve, from the landing through 105: the target on the ledge, across the pit
		if (S()) { Pose(mo, 1200, 1280, 0); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("hungIn105", F(105).door == clocked, h.said); Next(); }
		if (S()) { ShootAt(mo, 105, 125, (588, OFF + 1376, -2)); Next(); }
		if (S()) Wait(3);
		if (S()) { Check("valveShotShut", Cause(VALVE).setting == 0, String.Format("setting %d", Cause(VALVE).setting)); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("shotPitDry", Water() <= PIT + 1, String.Format("water %.1f", Water())); Next(); }
		if (S()) Wait(40);
		if (S()) { ShootAt(mo, 105, 125, (588, OFF + 1376, -2)); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("valveShotOpenAgain", Cause(VALVE).setting == 1 && abs(Water() + 72) < 1, String.Format("water %.1f", Water())); Next(); }
		if (S()) Wait(200);
		if (S()) { Check("fullAgainAmbush", Ambushers(63) == 0, String.Format("%d still to come", Ambushers(63))); Next(); }
		if (S()) { Pose(mo, 1200, 1280, 0); PressUse(mo); Next(); }
		if (S()) Wait(20);
		// the belt, from the bay through 108, which looks straight at the hatch: the target over it
		if (S()) { Pose(mo, 1936, 1500, 90); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("hungIn108", F(108).door == clocked, h.said); Next(); }
		if (S()) { ShootAt(mo, 108, 128, (1936, OFF + 1100, 16)); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("beltShotRunning", Cause(BELT).setting == 1 && abs(FZ(2000, 1150) - 32) < 1, String.Format("setting %d step3 %.1f", Cause(BELT).setting, FZ(2000, 1150))); Next(); }
		if (S()) { ShootAt(mo, 108, 128, (1936, OFF + 1100, 16)); Next(); }
		if (S()) Wait(80);
		if (S()) { Check("beltShotStanding", Cause(BELT).setting == 0 && abs(FZ(2000, 1150) + 112) < 1, String.Format("setting %d step3 %.1f", Cause(BELT).setting, FZ(2000, 1150))); Next(); }
		if (S()) { Pose(mo, 1936, 1500, 90); PressUse(mo); Next(); }
		if (S()) Wait(20);
		// the beam, from optics through 106, which looks straight at the plan board: each of its four targets from
		// one place, the middle of 106's mouth, a step out of it
		if (S()) { Pose(mo, 1568, 2360, 270); PressUse(mo); Next(); }
		if (S()) Wait(20);
		if (S()) { Check("hungIn106", F(106).door == clocked, h.said); Next(); }
		if (S()) { ShootAt(mo, 106, 126, (1504, OFF + 2820, 72)); Next(); }
		if (S()) Wait(160);
		if (S()) { Check("beamShotA", Cause(BEAM).setting == 1 && OnlyHole(1), String.Format("setting %d %s", Cause(BEAM).setting, Holes())); Next(); }
		if (S()) { ShootAt(mo, 106, 126, (1580, OFF + 2820, 136)); Next(); }
		if (S()) Wait(160);
		if (S()) { Check("beamShotB", Cause(BEAM).setting == 2 && OnlyHole(2), String.Format("setting %d %s", Cause(BEAM).setting, Holes())); Next(); }
		if (S()) { ShootAt(mo, 106, 126, (1556, OFF + 2820, 72)); Next(); }
		if (S()) Wait(160);
		if (S()) { Check("beamShotOff", Cause(BEAM).setting == 0 && HoleShut(1) && HoleShut(2) && HoleShut(3), String.Format("setting %d %s", Cause(BEAM).setting, Holes())); Next(); }
		if (S()) { ShootAt(mo, 106, 126, (1632, OFF + 2820, 72)); Next(); }
		if (S()) Wait(160);
		if (S()) { Check("beamShotC", Cause(BEAM).setting == 3 && OnlyHole(3), String.Format("setting %d %s", Cause(BEAM).setting, Holes())); Next(); }
		if (S()) Done();
	}

	// === MODE=3: views, 140 tics each (a screenshot every 70 tics: tools/smoke_MAP21_3.cfg; two a view) ===========
	void View(Actor mo, string what, double x, double y, double ang, double pitch = 0)
	{
		Pose(mo, x, y, ang, pitch);
		Info(String.Format("view %d: %s", viewN++, what));
	}
	void SetNow(int tid, int s) { let c = Cause(tid); th.SetCause(c, s, null); th.Snap(c); }
	// the clocked door taken from where it hangs and hung in frame n (the player posed in front of each, NOW),
	// a step each: then a view; 139 tics in all, as any view
	void Hang(Actor mo, double x, double y, double ang) { Pose(mo, x, y, ang); PressUse(mo); Next(); }
	void Views(Actor mo)
	{
		if (S()) { mo.bInvisible = true; Wait(15); }
		if (S()) { View(mo, "the start NOW: the machine and its desk; through 101 the hall THEN, its desk and its clock", 512, 40, 90); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the same spot THEN: through 121 the hall NOW", 512, OFF + 40, 90); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "hall NOW from the north-east: the machine, Doom's stone, the benches' footprints", 980, 740, 215, 8); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "hall THEN from the north-east: the brass shutter, the benches", 980, OFF + 740, 215, 8); Next(); }
		if (S()) Wait(139);
		// --- the machine's faces (PLAN.md, "MAP21: the machine's faces"), THEN and NOW from the same spot
		if (S()) { View(mo, "the machine THEN from the north (as Vadim's screenshot): the works, the port, MACHINE 7", 512, OFF + 744, 270, -8); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine NOW from the north: the same, dead", 512, 744, 270, -8); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine THEN from the north-west: the north and west faces, their corner", 200, OFF + 660, 311, -4); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine NOW from the north-west", 200, 660, 311, -4); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine THEN from the east: the power side, the wing's corner", 980, OFF + 340, 180, -4); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine NOW from the east", 980, 340, 180, -4); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine THEN from the south at 300: the front, the towers, the alcove, 121", 512, OFF + 24, 90, -8); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the machine NOW from the south at 300: the front, 101", 512, 24, 90, -8); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "THEN in the alcove before 121, looking up: the piece over the frame, the inner faces", 512, OFF + 240, 90, -45); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "NOW in the alcove before 101, looking up", 512, 240, 90, -45); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "vestibule NOW: bolted both ways, BLUE's far side", 1060, 530, 315); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "vestibule THEN: the porter's desk, the goods edge, the turnstile", 1060, OFF + 530, 315); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the corridor NOW from its south end", 1408, 176, 90); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the pocket THEN: the night grille, NO DOORS BEYOND THIS POINT, frame 123", 1480, OFF + 610, 200); Next(); }
		if (S()) Wait(139);
		// --- the pocket is the corridor (PLAN.md, "MAP21: the pocket is the corridor"): the two times one place
		if (S()) { View(mo, "the pocket THEN looking north: through the night grille the corridor at night, its night lamps, its doors shut", 1408, OFF + 420, 90); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the same spot NOW: the grille's wreck (stubs in the walls and at the ceiling, bars on the floor), the corridor", 1408, 420, 90); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the pocket THEN facing west from 123: the turnstile, the clock", 1460, OFF + 470, 180); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the same spot NOW: the turnstile's wreck in its choked opening, the clock", 1460, 470, 180); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "frame 123 THEN from in front, empty: the wall over it", 1376, OFF + 480, 0, -14); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "frame 103 NOW from in front, empty: the wall over it", 1376, 480, 0, -14); Next(); }
		if (S()) Wait(139);
		if (S()) Hang(mo, 512, 280, 90);                    // the clocked door from 101 ...
		if (S()) Wait(8);
		if (S()) Hang(mo, 1470, 480, 0);                    // ... into 103 (its shadow in 123)
		if (S()) Wait(8);
		if (S()) { Info(String.Format("the clocked door in 103: %d", F(103).door == clocked));
			View(mo, "the pocket THEN through the clocked door in 123 (as Vadim's screenshot): the corridor NOW, the clock and the turnstile's wreck", 1390, OFF + 380, 32); Next(); }
		if (S()) Wait(119);
		if (S()) { View(mo, "the corridor NOW through the clocked door in 103: the pocket THEN, the goods edge", 1390, 380, 32); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the pocket THEN straight at the clocked door in 123: opposite 103 NOW the turnstile's wreck, the clock's wall", 1390, OFF + 480, 0); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the corridor NOW straight at the clocked door in 103: opposite 123 THEN the turnstile, the clock's wall", 1390, 480, 0); Next(); }
		if (S()) Wait(139);
		if (S()) Hang(mo, 1470, 480, 0);                    // the clocked door back into 101
		if (S()) Wait(8);
		if (S()) Hang(mo, 512, 280, 90);
		if (S()) Wait(8);
		if (S()) { Info(String.Format("the clocked door in 101: %d", F(101).door == clocked));
			View(mo, "the start NOW again, the clocked door back in 101", 512, 40, 90); Next(); }
		if (S()) Wait(119);
		// --- the cellar: the valve (found open)
		if (S()) { View(mo, "the cellar NOW, the valve open (found): the pit full, the stream from the pipe onto the water, the dead lever VALVE", 1076, 1540, 212, 16); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the cellar THEN, the valve open: the stream from the pipe to the pit's floor, its wet patch, the tanks, the target on the ledge", 1076, OFF + 1540, 212, 16); Next(); }
		if (S()) Wait(139);
		if (S()) { SetNow(VALVE, 0); View(mo, "the cellar NOW, the valve shut: the pit dry, the pipe dry, the store's pressure door", 1076, 1540, 212, 16); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the cellar THEN, the valve shut: no stream", 1076, OFF + 1540, 212, 16); Next(); }
		if (S()) Wait(139);
		if (S()) { SetNow(VALVE, 1); Hang(mo, 512, 280, 90); }
		if (S()) Wait(8);
		if (S()) Hang(mo, 1200, 1280, 0);
		if (S()) Wait(8);
		if (S()) { Info(String.Format("the clocked door in 105: %d", F(105).door == clocked));
			View(mo, "the cellar THEN by the lever, the valve open: through 125 the cellar NOW, the stream onto the water", 1130, OFF + 1300, 352); Next(); }
		if (S()) Wait(119);
		if (S()) { View(mo, "the cellar NOW in front of 105 (where its target is shot from): through it the cellar THEN, the ledge's target, the stream", 1190, 1280, 0); Next(); }
		if (S()) Wait(139);
		// --- the goods bay: the belt (found standing)
		if (S()) { View(mo, "the goods bay NOW, the belt standing (found): the dead belt, its crates in dust, the hatch stair, the gallery", 1640, 1320, 300, 12); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the goods bay THEN, the belt standing: four crates on it, the flap, the railed hatch, the target over it", 1640, OFF + 1320, 300, 12); Next(); }
		if (S()) Wait(139);
		if (S()) { SetNow(BELT, 1); View(mo, "the goods bay THEN, the belt running: crates ride into the hatch, new ones out of the flap", 1640, OFF + 1320, 300, 12); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the goods bay NOW, the belt running: the heap up to the gallery, no crates on the belt", 1640, 1320, 300, 12); Next(); }
		if (S()) Wait(139);
		if (S()) Hang(mo, 1200, 1280, 0);
		if (S()) Wait(8);
		if (S()) Hang(mo, 1936, 1500, 90);
		if (S()) Wait(8);
		if (S()) { Info(String.Format("the clocked door in 108: %d", F(108).door == clocked));
			View(mo, "the goods bay THEN by the lever, the belt running: through 128 the bay NOW, the heap", 1904, OFF + 1430, 70); Next(); }
		if (S()) Wait(119);
		if (S()) { SetNow(BELT, 0); View(mo, "the goods bay NOW in front of 108, the belt standing: through it THEN, the hatch and its target, the crates", 1936, 1440, 90, 4); Next(); }
		if (S()) Wait(139);
		// --- optics: the beam (found at C)
		if (S()) { View(mo, "optics NOW, the beam at C (found): hole C open under its plate, the plates A and B, the emitter's wreck, the board faded", 1180, 2340, 40); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "optics THEN, the beam at C: the emitter, the beam to C under its plate, the plan board and its targets", 1180, OFF + 2340, 40); Next(); }
		if (S()) Wait(139);
		if (S()) { SetNow(BEAM, 1); View(mo, "optics NOW, the beam at A: hole A open, C shut", 1640, 2340, 145); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "optics THEN, the beam at A", 1640, OFF + 2340, 145); Next(); }
		if (S()) Wait(139);
		if (S()) { SetNow(BEAM, 3); Hang(mo, 1936, 1500, 90); }
		if (S()) Wait(8);
		if (S()) Hang(mo, 1568, 2360, 270);
		if (S()) Wait(8);
		if (S()) { Info(String.Format("the clocked door in 106: %d", F(106).door == clocked));
			View(mo, "optics THEN by the lever, the beam at C: through 126 optics NOW, hole C", 1600, OFF + 2420, 240); Next(); }
		if (S()) Wait(119);
		if (S()) { View(mo, "optics NOW in front of 106 (where the targets are shot from): through it THEN, the plan board and its four targets", 1568, 2380, 270, -6); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the lobby THEN: RED's far side, the desk, the clock", LX + 990, OFF + 600, 215); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the lobby NOW: dust, RED's far side as THEN, the blue armour (no secret now)", LX + 990, 600, 215); Next(); }
		if (S()) Wait(139);
		// --- the pass office: THEN a booth against the vestibule's south wall, BLUE's far side in it; NOW its footprint
		if (S()) { View(mo, "the vestibule NOW: the booth's footprint, BLUE's far side", 1168, 420, 270, 6); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the vestibule THEN: the pass office, PASSES, the megasphere behind the glass", 1168, OFF + 420, 270, 6); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "inside the booth THEN: out through the glass to the vestibule", 1130, OFF + 236, 60); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "inside the booth THEN: BLUE's far side", 1214, OFF + 246, 200); Next(); }
		if (S()) Wait(139);
		// --- the second pocket frame, 104 NOW and 124 THEN, at the corridor's south end
		if (S()) { View(mo, "the corridor's south end NOW: frame 104", 1376, 320, 270); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the pocket's south end THEN: frame 124", 1376, OFF + 320, 270); Next(); }
		if (S()) Wait(139);
		// --- GREEN, and the night room's two times
		if (S()) { View(mo, "the bay cellar NOW: GREEN leaning on the west wall, the super shotgun", 2080, 990, 190); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the night room NOW, dead: GREEN's far side, the armour bonuses on the runner", 660, 912, 180); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the night room NOW, dead: stone where the brass frame is THEN", 380, 912, 0); Next(); }
		if (S()) Wait(139);
		if (S()) { View(mo, "the night room THEN: the brass frame HOME, the candelabra", 380, OFF + 912, 0); Next(); }
		if (S()) Wait(139);
		// --- the machine: the clocked door back in 101, the keys turned: it runs, the shutter opens; taken out: shut
		if (S()) Hang(mo, 1568, 2360, 270);
		if (S()) Wait(8);
		if (S()) Hang(mo, 512, 280, 90);
		if (S()) Wait(8);
		if (S()) { desk.started = true; Info(String.Format("the clocked door in 101: %d", F(101).door == clocked));
			View(mo, "the hall THEN, the machine running: the shutter opening", 760, OFF + 520, 120); Next(); }
		if (S()) Wait(119);
		if (S()) { View(mo, "the hall THEN, the machine running: the shutter open, the night room", 512, OFF + 600, 90); Next(); }
		if (S()) Wait(139);
		if (S()) Hang(mo, 512, 280, 90);
		if (S()) Wait(8);
		if (S()) { Info(String.Format("running %d", desk.running)); View(mo, "the hall THEN, the clocked door taken: the machine stopped, the shutter shut", 512, OFF + 600, 90); Next(); }
		if (S()) Wait(129);
	}

	// === MODE=5: the wall over every frame and far side, from in front, THEN and NOW (PLAN.md, "MAP21: the pocket
	// is the corridor"; tools/smoke_MAP21_5.cfg shoots every 35 tics, two a view, the later one kept) ===========
	static const double FV[] = {
		// x, y (NOW's), angle, pitch
		512, 200, 90, -14,              //  0 101 / 121, in the machine
		1376, 480, 0, -14,              //  1 103 / 123, the corridor's (the pocket's) east wall
		1376, 330, 270, -14,            //  2 104 / 124, its south end
		1090, 1280, 0, -14,             //  3 105 / 125, the landing's east wall
		1568, 2470, 270, -14,           //  4 106 / 126, optics' south wall
		1936, 1400, 90, -14,            //  5 108 / 128, the goods bay's north wall
		LX + 880, 320, 0, -14,          //  6 110 / 130, the lobby's east wall
		LX + 150, 320, 180, -14,        //  7 RED's far side, the lobby's west wall
		1168, 400, 270, -14,            //  8 BLUE's far side, the vestibule's south wall (THEN in the pass office)
		1214, 246, 200, -14,            //  9 ... THEN from inside the pass office
		520, 912, 180, -10,             // 10 GREEN's far side, the night room's west end
		500, 912, 0, -10,               // 11 the brass frame HOME (190) THEN, its east end (NOW stone)
		1260, 304, 0, -14,              // 12 the vestibule's bolted door NOW, the goods edge and NO DOORS THEN
		1440, 1310, 0, -14,             // 13 GOODS' door from the corridor (THEN beyond the grille)
		1380, 1472, 180, -14,           // 14 CELLAR's door from the corridor
		1408, 2120, 90, -14,            // 15 OPTICS' door at the corridor's north end
		860, 384, 0, -14,               // 16 the hall's doorway to the vestibule
		LX + 150, 160, 180, -14         // 17 the lobby's way to the cloakroom
	};
	void FrameViews(Actor mo)
	{
		if (tic == 10) mo.bInvisible = true;
		if (tic < 20 || (tic - 20) % 70) return;
		int i = (tic - 20) / 70, k = i / 2;
		if (k * 4 >= FV.Size()) { if (k * 4 == FV.Size() && !(i % 2)) Console.Printf("AJARTEST frameViewsDone=1"); return; }
		Pose(mo, FV[k * 4], FV[k * 4 + 1] + (i % 2 ? 0 : OFF), FV[k * 4 + 2], FV[k * 4 + 3]);
		Info(String.Format("frame view %d (%s): row %d", i, i % 2 ? "NOW" : "THEN", k));
	}

	// === MODE=4: the causes shown (posed): the crates, the streams, the levers beside their frames =========
	int OldCrates()
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarOldCrate");
		Actor a;
		while (a = Actor(it.Next())) n++;
		return n;
	}
	// every crate standing on the belt THEN has its dusty twin NOW at the same spot, solid, and there are no others
	bool TwinsRight(AjarGoodsIn gi, out string info)
	{
		int twins = 0;
		bool ok = true;
		for (int i = 0; i < gi.crates.Size(); i++)
		{
			let c = gi.crates[i];
			if (!c || c.bDestroyed || c.pos.x - 16 < gi.FlapX() || abs(c.pos.z - gi.pos.z) >= 1) continue;
			twins++;
			Vector2 want = (c.pos.x, c.pos.y - OFF);
			if (!c.twin || (c.twin.pos.xy - want).Length() > 0.5 || !c.twin.bSolid) ok = false;
			info = info .. String.Format(" (%.0f,%.0f)%s", want.x, want.y, c.twin ? String.Format("=(%.0f,%.0f)", c.twin.pos.x, c.twin.pos.y) : "-");
		}
		return ok && twins == OldCrates();
	}
	AjarStream Stream(bool then)
	{
		let it = ThinkerIterator.Create("AjarStream");
		AjarStream s;
		while (s = AjarStream(it.Next())) if (th.when.InThen(s.pos.xy) == then) return s;
		return null;
	}
	Array<double> xs;
	Array<AjarGoodsCrate> seen;
	void Remember(AjarGoodsIn gi)
	{
		xs.Clear(); seen.Clear();
		for (int i = 0; i < gi.crates.Size(); i++) if (gi.crates[i]) { seen.Push(gi.crates[i]); xs.Push(gi.crates[i].pos.x); }
	}
	// how far the crates remembered have moved since, the least or the most (those gone over the edge left out)
	double Moved(bool least)
	{
		double r = least ? 1e9 : 0;
		for (int i = 0; i < seen.Size(); i++)
		{
			if (!seen[i] || seen[i].bDestroyed || seen[i].fell) continue;
			double d = abs(seen[i].pos.x - xs[i]);
			r = least ? min(r, d) : max(r, d);
		}
		return r;
	}
	// USE on a cause's lever from the spot 32 out from the wall where the lever and its frame meet
	void UseBeside(Actor mo, double x, double y, Vector2 lever)
	{
		Pose(mo, x, y, VectorAngle(lever.x - x, lever.y - y));
		PressUse(mo);
	}
	AjarGoodsIn gi;
	int was;
	void Causes(Actor mo)
	{
		if (S()) Wait(3);
		if (S())
		{
			gi = AjarGoodsIn.Get();
			string info = "";
			Check("fourCratesStandOnTheBelt", gi && gi.crates.Size() == 4 && gi.OnBelt() == 4 && Cause(BELT).setting == 0, gi ? String.Format("%d crates, %d on the belt", gi.crates.Size(), gi.OnBelt()) : "no goods-in");
			bool twins = gi && TwinsRight(gi, info);
			Check("dustyCratesNowWhereThenStand", twins && OldCrates() == 4, String.Format("%d old crates:%s", OldCrates(), info));
			let sn = Stream(false), st = Stream(true);
			Check("streamsShownValveOpen", sn && st && sn.Shown() && st.Shown() && !sn.bInvisible && !st.bInvisible && st.patch && !st.patch.bInvisible,
				sn && st ? String.Format("now %d then %d", sn.Shown(), st.Shown()) : "no streams");
			Check("streamFallsOntoTheWaterNow", sn && abs(sn.pos.z - Water()) < 1 && abs(sn.pos.z + sn.scale.y * 64 - (-16)) < 1, sn ? String.Format("from %.1f to %.1f, water %.1f", sn.pos.z + sn.scale.y * 64, sn.pos.z, Water()) : "");
			Check("streamFallsToTheFloorThen", st && abs(st.pos.z - PIT) < 1 && abs(st.pos.z + st.scale.y * 64 - (-16)) < 1, st ? String.Format("from %.1f to %.1f", st.pos.z + st.scale.y * 64, st.pos.z) : "");
			Next();
		}
		// the valve's lever, beside 125: shut, and both streams stop at once; open again, both run
		if (S()) { UseBeside(mo, 1200, OFF + 1320, (1232, OFF + 1360)); Next(); }
		if (S()) Wait(1);
		if (S())
		{
			Check("valveLeverBesideItsFrame", Cause(VALVE).setting == 0, String.Format("setting %d", Cause(VALVE).setting));
			Check("streamsStopAtOnce", !Stream(false).Shown() && !Stream(true).Shown() && Stream(false).bInvisible && Stream(true).bInvisible && Stream(true).patch.bInvisible);
			Next();
		}
		if (S()) { UseBeside(mo, 1200, OFF + 1320, (1232, OFF + 1360)); Next(); }
		if (S()) Wait(1);
		if (S()) { Check("streamsRunAgain", Cause(VALVE).setting == 1 && Stream(false).Shown() && Stream(true).Shown()); Next(); }
		// the belt's lever, beside 128: it runs; the crates ride, the dusty ones are gone at once
		if (S()) { Remember(gi); UseBeside(mo, 1904, OFF + 1504, (1872, OFF + 1536)); Next(); }
		if (S()) Wait(1);
		if (S())
		{
			Check("beltLeverBesideItsFrame", Cause(BELT).setting == 1, String.Format("setting %d", Cause(BELT).setting));
			Check("noDustyCratesWhileItRuns", OldCrates() == 0, String.Format("%d", OldCrates()));
			Next();
		}
		if (S()) Wait(35);
		if (S()) { Check("cratesRide", Moved(true) > 20, String.Format("the least moved %.1f", Moved(true))); Next(); }
		if (S()) Wait(300);
		if (S())
		{
			string rides = "";
			bool fair = gi.rides.Size() > 0;
			for (int i = 0; i < gi.rides.Size(); i++) { rides = rides .. " " .. gi.rides[i]; if (gi.rides[i] < 105 || gi.rides[i] > 175) fair = false; }
			Check("cratesGoneIntoTheHatch", gi.gone >= 3, String.Format("%d gone", gi.gone));
			Check("newCratesComeOutOfTheFlap", gi.made >= 3, String.Format("%d made", gi.made));
			Check("aboutFourOnTheBelt", gi.OnBelt() >= 3 && gi.OnBelt() <= 5, String.Format("%d on the belt", gi.OnBelt()));
			Check("flapToHatchIn3To5s", fair, "tics:" .. rides);
			Check("noDustyCratesStill", OldCrates() == 0);
			Next();
		}
		// stopped: they stand where they are, THEN and (in dust) NOW
		if (S()) { UseBeside(mo, 1904, OFF + 1504, (1872, OFF + 1536)); Next(); }
		if (S()) Wait(60);                                                          // (what rides slides a little: Doom's friction)
		if (S()) { Check("beltStopped", Cause(BELT).setting == 0); Remember(gi); was = gi.made; Next(); }
		if (S()) Wait(70);
		if (S())
		{
			string info = "";
			Check("cratesStand", Moved(false) < 0.5 && gi.made == was, String.Format("the most moved %.2f, %d made", Moved(false), gi.made - was));
			Check("dustyCratesNowWhereThenStopped", TwinsRight(gi, info) && OldCrates() == gi.OnBelt() && OldCrates() >= 3, String.Format("%d old, %d on the belt:%s", OldCrates(), gi.OnBelt(), info));
			Next();
		}
		// the beam's lever, beside 126: C to off
		if (S()) { UseBeside(mo, 1600, OFF + 2352, (1632, OFF + 2320)); Next(); }
		if (S()) Wait(1);
		if (S()) { Check("beamLeverBesideItsFrame", Cause(BEAM).setting == 0, String.Format("setting %d", Cause(BEAM).setting)); Next(); }
		if (S()) Done();
	}

	// === MODE=9: doors beside walls and levers =========================================================
	// The three causes' levers THEN (NOW the same pictures are dead: no special), each beside its frame: the
	// lever's middle, which way it faces, its frame THEN, the cause.
	static const double LEVER_X[] = { 1232, 1872, 1632 };
	static const double LEVER_Y[] = { 9552, 9728, 10512 };
	static const double LEVER_OX[] = { -1, 0, 0 };
	static const double LEVER_OY[] = { 0, -1, 1 };
	static const int LEVER_FRAME[] = { 125, 128, 126 };
	static const int LEVER_CAUSE[] = { 11, 12, 13 };
	static const string LEVER_NAME[] = { "valve", "belt", "beam" };
	int leverWas;

	// the frame's mouth (its line 16 into the room): the middle, and which way the room is
	Vector2 MouthN(AjarFrame f) { Vector2 dir = h.FindLine(f.args[0]).delta.Unit(); return (dir.y, -dir.x); }
	Vector2 MouthMid(AjarFrame f) { Line l = h.FindLine(f.args[0]); return l.v1.p + l.delta / 2 + MouthN(f) * 16; }
	Vector2 FrontOf(AjarFrame f) { return MouthMid(f) + MouthN(f) * 40; }
	void Aim(Actor mo, Vector2 p, Vector2 at) { Pose(mo, p.x, p.y, VectorAngle(at.x - p.x, at.y - p.y)); }
	// the door d hung in f (by script), both of a lever's frames emptied first
	void HangIn(AjarDoor d, AjarFrame f)
	{
		AjarFrame tf = h.TwinFrame(f);
		if (d.frame) h.Unhang(d.frame);
		if (f.door) h.Unhang(f);
		if (tf && tf.door) h.Unhang(tf);
		h.carried = null;
		h.Hang(d, f);
	}
	// the two ends of a hung leaf
	Vector2 End(AjarDoor d, int sign) { return d.pos.xy + Actor.AngleToVector(d.angle - 90) * 32 * sign; }
	string LeafAt(AjarDoor d) { Vector2 a = End(d, -1), b = End(d, 1); return String.Format("leaf (%.1f,%.1f)-(%.1f,%.1f) angle %.2f", a.x, a.y, b.x, b.y, d.angle); }

	void Doors(Actor mo)
	{
		if (tic < 3 || tic % 3) return;
		int i = tic / 3 - 1;
		if (i == 0) { MachineLeaf(); return; }
		i--;
		if (i < 54) { LeverStep(mo, i / 18, (i / 6) % 3, i % 6); return; }
		i -= 54;
		if (i < 9) { DeadLever(mo, i / 3, i % 3); return; }
		i -= 9;
		if (i < 3) { DeskPanel(mo, i); return; }
		if (i == 3) Done();
	}

	// the clocked door as found, in the machine (101) and its shadow THEN (121): between the wings, whose faces are
	// x 464 and 560 (from the frame's wall at y 320 down to 256), by 2 at least; both leaves alike
	void MachineLeaf()
	{
		Vector2 a = End(clocked, -1), b = End(clocked, 1), c = End(shadow, -1), d = End(shadow, 1);
		Check("clockedLeafKeepsOffTheWings", clocked.frame == F(101) && min(a.x, b.x) >= 466 - 0.001 && max(a.x, b.x) <= 558 + 0.001, LeafAt(clocked));
		Check("shadowLeafKeepsOffTheWings", shadow.frame == F(121) && min(c.x, d.x) >= 466 - 0.001 && max(c.x, d.x) <= 558 + 0.001, LeafAt(shadow));
		Check("bothLeavesAlike", (shadow.pos - clocked.pos - (0, OFF, 0)).Length() < 0.001 && abs(Actor.DeltaAngle(shadow.angle, clocked.angle)) < 0.001,
			LeafAt(clocked) .. "; " .. LeafAt(shadow));
		// how far open: from shut (along the frame line, from the hinge to the other jamb) to the leaf
		Vector2 hinge = abs(a.y - 320) < abs(b.y - 320) ? a : b, far = hinge == a ? b : a;
		double shut = hinge.x < 512 ? 0 : 180;
		Info(String.Format("the machine's leaf: hinge (%.2f,%.2f), far end (%.2f,%.2f), open %.2f degrees", hinge.x, hinge.y, far.x, far.y,
			abs(Actor.DeltaAngle(shut, VectorAngle(far.x - hinge.x, far.y - hinge.y)))));
	}

	// lever L; which: 0 RED hung THEN, 1 the clocked door hung THEN, 2 the clocked door hung NOW (its shadow THEN).
	// Steps: 0 hang it; 1 fromLever, 40 out from the lever's middle, facing it; 2 fromLeverEnd, 40 out from the
	// lever's end by the frame, turned to its middle; 3 fromFrame, 40 out from the frame's middle, turned to the
	// lever's middle; 4 atLeaf, from there aimed at the leaf's middle; 5 atFrame, aimed at the empty frame's middle.
	// Where the aim to the lever passes through the leaf as it stands (the leaf swings out over the lever's side of
	// the frame), the door is in front of the lever and the press is the door's; else it is the lever's and the
	// door stays.
	bool LeafBetween(AjarDoor d, Vector2 p, Vector2 q) { return AjarLeafRoom.Crosses(p, q, End(d, -1), End(d, 1)); }
	void LeverStep(Actor mo, int L, int which, int step)
	{
		AjarFrame ft = F(LEVER_FRAME[L]), fn = F(LEVER_FRAME[L] - 20);
		AjarDoor hand = which == 0 ? red : clocked;              // the door taken down and hung
		AjarDoor seen = which == 2 ? shadow : hand;              // the door in the frame THEN
		Vector2 lever = (LEVER_X[L], LEVER_Y[L]), o = (LEVER_OX[L], LEVER_OY[L]);
		string what = String.Format("%s_%s", LEVER_NAME[L], which == 0 ? "red" : which == 1 ? "clockedThen" : "clockedNow");
		let c = Cause(LEVER_CAUSE[L]);
		if (step == 0 || ft.door != seen) HangIn(hand, which == 2 ? fn : ft);
		if (step == 0)
		{
			Info(String.Format("%s: %s hung, %s", what, hand.Label(), LeafAt(seen)));
			return;
		}
		if (step <= 3)
		{
			// the lever's end by the frame: the one nearer the frame's mouth
			Vector2 along = (o.y, -o.x), e1 = lever + along * 32, e2 = lever - along * 32;
			Vector2 near = (e1 - MouthMid(ft)).Length() < (e2 - MouthMid(ft)).Length() ? e1 : e2;
			// from the frame: 24 out from its mouth's middle, aimed at the lever 8 in from its end by the frame (its
			// middle is 89 from 40 out, past the use range of 64, door or no door)
			Vector2 p = step == 1 ? lever + o * 40 : step == 2 ? near + o * 40 : MouthMid(ft) + MouthN(ft) * 24;
			Vector2 at = step == 3 ? near + (lever - near).Unit() * 8 : lever;
			Aim(mo, p, at);
			bool behind = LeafBetween(seen, p, at);
			leverWas = c.setting;
			PressUse(mo);
			bool moved = c.setting == (leverWas + 1) % c.Settings(), stays = ft.door == seen && !h.carried;
			Check(String.Format("%s_%s", step == 1 ? "fromLever" : step == 2 ? "fromLeverEnd" : "fromFrame", what),
				!behind && moved && stays,
				String.Format("%s: the leaf %s; setting %d to %d; frame THEN %s; hands %s; %s", Where(mo),
				behind ? "BETWEEN" : "not between", leverWas, c.setting,
				ft.door ? ft.door.Label() .. (ft.door.IsShadow() ? "(shadow)" : "") : "empty", h.carried ? h.carried.Label() : "-", h.said));
			return;
		}
		if (step == 4)
		{
			Aim(mo, FrontOf(ft), seen.pos.xy);
			PressUse(mo);
			Check("atLeaf_" .. what, h.carried == hand && !ft.door && !fn.door, String.Format("%s: %s", Where(mo), h.said));
			return;
		}
		if (h.carried != hand) { if (ft.door) h.Unhang(ft); h.carried = hand; }
		Aim(mo, FrontOf(ft), MouthMid(ft));
		PressUse(mo);
		Check("atFrame_" .. what, ft.door == hand && !h.carried, String.Format("%s: %s", Where(mo), h.said));
	}

	// NOW: RED hung in the lever's frame NOW, beside the dead lever (the same picture, no special)
	void DeadLever(Actor mo, int L, int step)
	{
		AjarFrame fn = F(LEVER_FRAME[L] - 20);
		Vector2 lever = (LEVER_X[L], LEVER_Y[L] - OFF), o = (LEVER_OX[L], LEVER_OY[L]);
		if (step == 0) { HangIn(red, fn); return; }
		if (step == 1) Aim(mo, FrontOf(fn), lever);
		else Aim(mo, lever + o * 40, lever);
		h.said = "";
		PressUse(mo);
		Info(String.Format("dead lever NOW, %s, %s: %s", LEVER_NAME[L], step == 1 ? "from the frame" : "from the lever",
			fn.door == red ? "RED stays hung" : h.carried == red ? "RED taken down" : "?"));
		if (h.carried == red) { h.carried = null; h.Hang(red, fn); }
	}

	// the desk's panel (y 176, facing the machine), the clocked door back in the machine
	void DeskPanel(Actor mo, int step)
	{
		if (step == 0) { HangIn(clocked, F(101)); return; }
		bool then = step == 1;
		Aim(mo, (512, (then ? OFF : 0) + 224), (512, (then ? OFF : 0) + 176));
		h.said = "";
		PressUse(mo);
		Check(then ? "deskPanelThen" : "deskPanelNow", (then ? h.said.IndexOf("key") >= 0 || h.said.IndexOf("Key") >= 0 : h.said.IndexOf("smashed") >= 0)
			&& F(101).door == clocked && F(121).door == shadow && !h.carried, String.Format("%s: %s", Where(mo), h.said));
	}
}
