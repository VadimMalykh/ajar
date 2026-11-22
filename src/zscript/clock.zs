// The clock lab (map CLOCK, tools/map_clock.py; PLAN.md, "The clock lab").
//
// MAP18's metronome: a pulse fired along a gallery laps it for ever through
// a hung Pair (the endless corridor), and strikes a contact every lap; a
// gate stays up while the last beat is recent enough.
//  * AjarPulseEmitter thing (20110): args[0] the pulse's speed in units a
//    tic (0: 20), args[1] 0 for a pulse that passes through everything
//    (AjarPulse, +THRUACTORS), 1 for a ripper that hurts what it passes
//    (AjarRipPulse). Thing_Activate on it (a button) fires one pulse along
//    its angle, 40 above its floor. One pulse to an emitter: firing again
//    calls the running one back (it bursts where it is) and fires anew.
//  * AjarContact thing (20111): what a line across the gallery sets off
//    (Thing_Activate on the contact's tid, `missilecross`: only projectiles
//    set it off, a pulse in either direction). Only pulses count. args[0]
//    the gate's sector tag, args[1] the hold time in tics (0: 70), args[2]
//    the lamp's sector tag (0: none). It makes the level's AjarMetronome.
//  * AjarMetronome thinker: the tics of the last two beats, the period
//    between them, and the gate: every tic the gate goes up (8 units a tic,
//    to 4 below the lowest ceiling beside it) while the last beat is no
//    older than the hold time, and down otherwise. It never crushes: a gate
//    coming down onto something stops there until it is free.
//
// MAP18's delay lanes (tools/map_clockdept.py; PLAN.md, "MAP18: the clock
// department"): the pulse is the stopwatch for a run.
//  * An emitter with args[2] a lane (1, 2, 3) is a lane's: firing it calls
//    back every pulse of any lane still alive (one pulse in the hall at a
//    time), and the new pulse belongs to that lane.
//  * AjarLaneContact thing (20130): args[0] its lane. Only a pulse of that
//    lane counts on it: each pass is a lap; at the last the pulse burns out.
//  * AjarDelayShutter thing (20131): args[0] the shutter's sector tag,
//    args[1] the first of the lamps' tags (one a lap: lamp k lit while more
//    than k laps are left), args[2] the laps a pulse lives for. The shutter
//    goes up (8 units a tic, to 4 below the lowest ceiling beside it, never
//    crushing) while a lane's pulse lives, and down when it does not. Every
//    lap ticks, wherever the player is, with a word on the screen.

class AjarPulse : Actor
{
	AjarPulseEmitter from;
	int beats;                  // contacts it has set off
	bool recalled;              // called back by its emitter's next shot
	int lane, laps;             // MAP18: its lane (0: none), the passes of that lane's contact
	bool burnt;                 // ... it lived its laps out

	Default
	{
		Radius 6;
		Height 8;
		Speed 20;
		Damage 0;
		Projectile;
		+THRUACTORS
		+NODAMAGETHRUST
		+DONTSPLASH
		RenderStyle "Add";
	}
	States
	{
	Spawn:
		PLSS AB 3 Bright;
		Loop;
	Death:
		PLSE A 3 Bright Gone();
		PLSE BCDE 3 Bright;
		Stop;
	}

	void Gone()
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.ClockGone(self);
	}
}

// The ripper: it passes through what can be hurt and hurts it, 3 each tic
// it is in it (the engine's ripper hits a thing once a tic).
class AjarRipPulse : AjarPulse
{
	Default
	{
		Damage 1;
		-THRUACTORS
		+RIPPER
	}

	override int DoSpecialDamage(Actor victim, int damage, Name damagetype)
	{
		return 3;
	}
}

class AjarPulseEmitter : Actor
{
	AjarPulse pulse;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY
	}
	States
	{
	Spawn:
		AJEM A -1;              // the optics lab's lamp on a stand (a placeholder)
		Stop;
	}

	override void Activate(Actor activator)
	{
		Fire();
	}

	AjarPulse Fire()
	{
		if (pulse && pulse.bMissile)
		{
			pulse.recalled = true;
			pulse.ExplodeMissile();
		}
		if (args[2])                                    // a lane's: every lane's pulse is called back
		{
			let it = ThinkerIterator.Create("AjarPulse");
			AjarPulse p;
			while (p = AjarPulse(it.Next()))
			{
				if (p.lane && p.bMissile)
				{
					p.recalled = true;
					p.ExplodeMissile();
				}
			}
		}
		double speed = args[0] ? args[0] : 20;
		pulse = AjarPulse(Spawn(args[1] ? "AjarRipPulse" : "AjarPulse", pos + (AngleToVector(angle, 20), 40)));
		pulse.from = self;
		pulse.angle = angle;
		pulse.speed = speed;
		pulse.Vel3DFromAngle(speed, angle, 0);
		pulse.A_StartSound("weapons/plasmaf", CHAN_VOICE);
		if (args[2])
		{
			pulse.lane = args[2];
			let d = AjarDelayShutter.Find();
			if (d) d.Fired(pulse);
		}
		return pulse;
	}
}

class AjarContact : Actor
{
	AjarMetronome metronome;
	int others;                 // set off by something that is no pulse (and not counted)

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
		metronome = AjarMetronome.Make(args[0], args[1] ? args[1] : 70, args[2]);
	}

	override void Activate(Actor activator)
	{
		let p = AjarPulse(activator);
		if (!p)
		{
			others++;
			if (CVar.GetCVar("ajar_autotest").GetInt())
				Console.Printf("AJARTEST info the contact was set off by %s", activator ? activator.GetClassName() : 'nothing');
			return;
		}
		p.beats++;
		metronome.Beat();
	}
}

class AjarMetronome : Thinker
{
	const GATE_SPEED = 8;
	const FLASH = 6;
	int hold;
	int lastBeat, prevBeat;     // level.maptime of the last two beats (-1: none yet)
	int beats, period;
	bool want;                  // the gate is wanted up (as of this tic)
	Sector gate, lamp;
	double gateTop, gateBottom;
	int lampLight, lampTill;

	static AjarMetronome Make(int gateTag, int hold, int lampTag)
	{
		let m = new("AjarMetronome");
		m.hold = hold;
		m.lastBeat = m.prevBeat = -1;
		let it = level.CreateSectorTagIterator(gateTag);
		int i = it.Next();
		if (i >= 0)
		{
			m.gate = level.sectors[i];
			m.gateBottom = m.gate.CenterFloor();
			m.gateTop = m.gate.FindLowestCeilingSurrounding() - 4;
		}
		it = level.CreateSectorTagIterator(lampTag);
		i = lampTag ? it.Next() : -1;
		if (i >= 0)
		{
			m.lamp = level.sectors[i];
			m.lampLight = m.lamp.lightlevel;
		}
		return m;
	}

	void Beat()
	{
		prevBeat = lastBeat;
		lastBeat = level.maptime;
		beats++;
		period = prevBeat >= 0 ? lastBeat - prevBeat : 0;
		if (lamp)
		{
			lamp.SetLightLevel(255);
			lampTill = level.maptime + FLASH;
		}
	}

	override void Tick()
	{
		want = lastBeat >= 0 && level.maptime - lastBeat <= hold;
		if (gate)
		{
			double c = gate.CenterCeiling();
			if (want && c < gateTop) gate.MoveCeiling(GATE_SPEED, gateTop, -1, 1, false);
			else if (!want && c > gateBottom) gate.MoveCeiling(GATE_SPEED, gateBottom, -1, -1, false);
		}
		if (lamp && lampTill && level.maptime >= lampTill)
		{
			lamp.SetLightLevel(lampLight);
			lampTill = 0;
		}
	}

	bool GateUp() { return gate && gate.CenterCeiling() >= gateTop - 0.01; }
	bool GateDown() { return gate && gate.CenterCeiling() <= gateBottom + 0.01; }
}

class AjarLaneContact : Actor
{
	int others;                 // set off by what is not this lane's pulse

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

	override void Activate(Actor activator)
	{
		let p = AjarPulse(activator);
		if (!p || p.lane != args[0] || !p.bMissile)
		{
			others++;
			return;
		}
		p.laps++;
		let d = AjarDelayShutter.Find();
		if (d) d.Lap(p);
	}
}

class AjarDelayShutter : Actor
{
	const SPEED = 8;
	const LIT = 255;
	AjarPulse pulse;            // the lane's pulse last fired
	bool wasLive;
	Sector shutter;
	double top, bottom;
	Array<int> lamps;           // the lamps: every sector tagged args[1] + k (sector numbers)
	Array<int> lampOf;          // ... and which k
	int dark;
	// what the tests read: when the last pulse was fired and went, how, and its laps' tics
	int firedAt, goneAt, gone;  // gone: 0 alive, 1 burnt out, 2 burst, 3 called back
	int upAt, downAt;           // the tics the shutter was last full up and last back down
	Array<int> lapAt;

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

	static AjarDelayShutter Find()
	{
		return AjarDelayShutter(ThinkerIterator.Create("AjarDelayShutter").Next());
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		let it = level.CreateSectorTagIterator(args[0]);
		int i = it.Next();
		if (i >= 0)
		{
			shutter = level.sectors[i];
			bottom = shutter.CenterFloor();
			top = shutter.FindLowestCeilingSurrounding() - 4;
		}
		for (int k = 0; k < args[2]; k++)
		{
			it = level.CreateSectorTagIterator(args[1] + k);
			while ((i = it.Next()) >= 0)
			{
				lamps.Push(i);
				lampOf.Push(k);
				dark = level.sectors[i].lightlevel;
			}
		}
		upAt = downAt = -1;
	}

	double PulseSpeed()
	{
		let it = ThinkerIterator.Create("AjarPulseEmitter");
		Actor e;
		while (e = Actor(it.Next())) if (e.args[2]) return e.args[0] ? e.args[0] : 20;
		return 20;
	}

	bool Live() { return pulse && pulse.bMissile; }
	int Left() { return Live() ? args[2] - pulse.laps : 0; }
	bool Up() { return shutter && shutter.CenterCeiling() >= top - 0.01; }
	bool Down() { return shutter && shutter.CenterCeiling() <= bottom + 0.01; }

	void Fired(AjarPulse p)
	{
		pulse = p;
		firedAt = level.maptime;
		goneAt = -1;
		gone = 0;
		lapAt.Clear();
	}

	void Lap(AjarPulse p)
	{
		lapAt.Push(level.maptime);
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.delayFirstLap = true;
		int left = args[2] - p.laps;
		let mo = players[consoleplayer].mo;
		if (mo) mo.A_StartSound("switches/normbutn", CHAN_AUTO, CHANF_DEFAULT, 1.0, ATTN_NONE);
		if (left <= 0)
		{
			p.burnt = true;
			p.ExplodeMissile();
		}
		if (h) h.Say(left > 0 ? String.Format("Tick. %d to go.", left) : "Tick. The pulse has burnt out.");
	}

	override void Tick()
	{
		Super.Tick();
		bool live = Live();
		if (wasLive && !live)
		{
			goneAt = level.maptime;
			gone = !pulse ? 2 : pulse.burnt ? 1 : pulse.recalled ? 3 : 2;
			if (gone == 2)
			{
				let h = AjarHandler(EventHandler.Find("AjarHandler"));
				if (h) h.Say("The pulse burst on the end of its lane.");
			}
		}
		wasLive = live;
		if (shutter)
		{
			double c = shutter.CenterCeiling();
			if (live && c < top)
			{
				shutter.MoveCeiling(SPEED, top, -1, 1, false);
				if (Up()) upAt = level.maptime;
			}
			else if (!live && c > bottom)
			{
				shutter.MoveCeiling(SPEED, bottom, -1, -1, false);
				if (Down()) downAt = level.maptime;
			}
		}
		int left = Left();
		for (int i = 0; i < lamps.Size(); i++)
		{
			int want = lampOf[i] < left ? LIT : dark;
			Sector s = level.sectors[lamps[i]];
			if (s.lightlevel != want) s.SetLightLevel(want);
		}
	}
}

// --- the checks: MAP=CLOCK MODE=1..7 tools/smoke.sh -----------------------
// A pulse is watched as it passes a mark (x 1900, in every loop of the
// gallery, going east): the tic it passed, to a fraction of a tic, where it
// was across the lane and in height, and how many beats it struck since.
class AjarClockWatch : Object
{
	AjarPulse p;
	string name;
	double expect;              // a lap as the loop's length over the speed, in tics
	double wrap;                // how far back the east frame's portal puts it (2064 less where it comes out)
	int marks, beatsAt, beatMiss;
	double lastAt, lo, hi, sum;
	double yLo, yHi, zLo, zHi, vLo, vHi;
	double prevX;
	bool prevSet;
}

extend class AjarHandler
{
	const CLOCK_MARK = 1900;
	AjarClockWatch clockW;
	bool delayFirstLap;         // MAP18: a lane's pulse has made a lap (the ambushes of cause 50)
	int clockRun, clockRunFrom, clockPhase, clockT1, clockT2, clockT3, clockCase, clockN;
	int clockDeaths, clockDeathTic, clockDeathLine;
	Vector3 clockDeathPos;
	double clockX;
	AjarPulse clockP;
	Array<int> clockPeriods;

	AjarMetronome ClockMetronome()
	{
		return AjarMetronome(ThinkerIterator.Create("AjarMetronome").Next());
	}

	AjarPulseEmitter ClockEmitter(int lane)
	{
		let it = level.CreateActorIterator(lane == 2 ? 1102 : 1101, "AjarPulseEmitter");
		return AjarPulseEmitter(it.Next());
	}

	void ClockGone(AjarPulse p)
	{
		if (p.recalled) return;
		clockDeaths++;
		clockDeathTic = testTic;
		clockDeathPos = p.pos;
		Line l = p.BlockingLine;
		clockDeathLine = l && l.CountIDs() ? l.GetID(0) : l ? 0 : -1;
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info t=%d a pulse burst at (%.2f,%.2f,%.2f) on line %d (%s), in the level %d, after %d beats",
				testTic, p.pos.x, p.pos.y, p.pos.z, clockDeathLine, l ? "a wall" : "no line", level.IsPointInLevel(p.pos), p.beats);
	}

	int ClockAlive()
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarPulse");
		AjarPulse p;
		while (p = AjarPulse(it.Next())) if (p.bMissile) n++;
		return n;
	}

	void ClockKill()
	{
		let it = ThinkerIterator.Create("AjarPulse");
		AjarPulse p;
		while (p = AjarPulse(it.Next())) p.Destroy();
	}

	// Every door down and back where it leant.
	void ClockClear(Actor mo)
	{
		for (int f = 111; f <= 116; f++)
		{
			let fr = FindFrame(f);
			if (fr && fr.door) BeltTake(mo, f);
		}
	}

	// The three loops, hung by the handler as the player would (BeltHang,
	// belt.zs): 512 is 115 and 116 (lane B), 1024 is 113 and 114 (lane A),
	// 2048 is 111 and 114 with the other Pair in the pier (112, 113).
	void ClockLoop(Actor mo, int n)
	{
		ClockClear(mo);
		AjarDoor ta = LabLeaf(8, 0), tb = LabLeaf(8, 1), oa = LabLeaf(9, 0), ob = LabLeaf(9, 1);
		if (n == 512) { BeltHang(mo, ta, 115); BeltHang(mo, tb, 116); }
		else if (n == 1024) { BeltHang(mo, ta, 113); BeltHang(mo, tb, 114); }
		else { BeltHang(mo, oa, 112); BeltHang(mo, ob, 113); BeltHang(mo, ta, 111); BeltHang(mo, tb, 114); }
	}

	// The way a pulse flies in a lap, portal line to portal line: 2064 - 1520,
	// 2064 - 1008, and (896 + 16) + (2064 - 1008) through the pier.
	static double ClockPath(int n) { return n == 512 ? 544 : n == 1024 ? 1056 : 1968; }

	// The emitter's button, pressed (its speed and kind set first).
	AjarPulse ClockFire(Actor mo, int lane, int speed, int variant = 0)
	{
		let e = ClockEmitter(lane);
		e.args[0] = speed;
		e.args[1] = variant;
		FindLine(lane == 2 ? 1102 : 1101).Activate(mo, 0, SPAC_Use);
		return e.pulse;
	}

	AjarClockWatch ClockWatch(AjarPulse p, string name, double expect, double wrap = 1056)
	{
		let w = new("AjarClockWatch");
		w.p = p;
		w.name = name;
		w.expect = expect;
		w.wrap = wrap;
		clockW = w;
		return w;
	}

	void ClockStartRun(Actor mo, int t, int loop, int speed, string name, int variant = 0)
	{
		ClockKill();
		ClockLoop(mo, loop);
		Pose(mo, 400, 300, 0, 0);
		ClockWatch(ClockFire(mo, loop == 512 ? 2 : 1, speed, variant), name, ClockPath(loop) / speed, loop == 512 ? 544 : loop == 1024 ? 1056 : 2080);
		clockRunFrom = t;
	}

	bool ClockRunDone(int t, int laps)
	{
		let w = clockW;
		return w && (w.marks > laps || !w.p || !w.p.bMissile || t - clockRunFrom > (laps + 3) * w.expect + 70);
	}

	void ClockWatchTick(int t)
	{
		let w = clockW;
		if (!w || !w.p || !w.p.bMissile) return;
		let p = w.p;
		double x = p.pos.x;
		// how far it went since the last tic, through the east frame if it went
		// back (a fast pulse goes through it and past the mark in one tic)
		double d = x - w.prevX, to = CLOCK_MARK - w.prevX;
		if (d < 0) { d += w.wrap; if (to < 0) to += w.wrap; }
		if (w.prevSet && p.vel.x > 0 && to > 0 && to <= d && d < 2 * p.vel.x + 1)
		{
			double at = t - 1 + to / d;
			double v = p.vel.Length();
			if (w.marks > 0)
			{
				double took = at - w.lastAt;
				w.lo = w.marks == 1 ? took : min(w.lo, took);
				w.hi = w.marks == 1 ? took : max(w.hi, took);
				w.sum += took;
				if (p.beats - w.beatsAt != 1) w.beatMiss++;
			}
			if (w.marks == 0) { w.yLo = w.yHi = p.pos.y; w.zLo = w.zHi = p.pos.z; w.vLo = w.vHi = v; }
			w.yLo = min(w.yLo, p.pos.y); w.yHi = max(w.yHi, p.pos.y);
			w.zLo = min(w.zLo, p.pos.z); w.zHi = max(w.zHi, p.pos.z);
			w.vLo = min(w.vLo, v); w.vHi = max(w.vHi, v);
			w.marks++;
			w.lastAt = at;
			w.beatsAt = p.beats;
		}
		w.prevX = x;
		w.prevSet = true;
	}

	void ClockReport(AjarClockWatch w, int want)
	{
		int laps = max(w.marks - 1, 0);
		Console.Printf("AJARTEST info %s: %d laps, a lap %.4f to %.4f tics (mean %.4f; the length over the speed %.4f); at the mark y %.4f..%.4f, z %.4f..%.4f, speed %.4f..%.4f; %d beats, %d laps with other than one beat; alive %d",
			w.name, laps, w.lo, w.hi, laps ? w.sum / laps : 0., w.expect, w.yLo, w.yHi, w.zLo, w.zHi, w.vLo, w.vHi,
			w.p ? w.p.beats : -1, w.beatMiss, w.p && w.p.bMissile);
		Check(w.name .. "_laps", laps >= want && w.p && w.p.bMissile);
		Check(w.name .. "_lapIsLengthOverSpeed", laps > 0 && abs(w.lo - w.expect) < 0.05 && abs(w.hi - w.expect) < 0.05);
		Check(w.name .. "_noDrift", laps > 0 && w.yHi - w.yLo < 0.001 && w.zHi - w.zLo < 0.001 && w.vHi - w.vLo < 0.001);
		Check(w.name .. "_beatEveryLap", laps > 0 && w.beatMiss == 0);
	}

	bool ClockEastIn(AjarPulse p, double x1, double x2)
	{
		return p && p.bMissile && p.vel.x > 0 && p.pos.x > x1 && p.pos.x < x2 && abs(p.pos.y - 64) < 1;
	}

	// --- the gate, every tic --------------------------------------------
	// From the first tic it is fully up after a segment begins: how often the
	// metronome let it down, any tic it moved against what the metronome
	// wanted, and the spans fully up, fully down and not wanted.
	bool gateOn;
	int gateFrom, gateTics, gateWrong, gateDrops, gateUpFor, gateDownFor, gateOffFor;
	double gatePrev;
	bool gateWas;
	Array<int> gateUps, gateDowns, gateOffs;

	void ClockGateReset()
	{
		gateOn = false;
		gateFrom = level.maptime;
		gateTics = gateWrong = gateDrops = gateUpFor = gateDownFor = gateOffFor = 0;
		gateUps.Clear(); gateDowns.Clear(); gateOffs.Clear();
	}

	void ClockGateTick()
	{
		let mt = ClockMetronome();
		if (!mt || !mt.gate) return;
		double c = mt.gate.CenterCeiling();
		if (!gateOn)
		{
			if (mt.lastBeat < gateFrom || !mt.GateUp()) return;
			gateOn = true;
			gatePrev = c;
			gateWas = mt.want;
		}
		gateTics++;
		if ((mt.want && c < gatePrev - 0.001) || (!mt.want && c > gatePrev + 0.001)) gateWrong++;
		if (gateWas && !mt.want) gateDrops++;
		if (mt.GateUp()) gateUpFor++; else if (gateUpFor) { gateUps.Push(gateUpFor); gateUpFor = 0; }
		if (mt.GateDown()) gateDownFor++; else if (gateDownFor) { gateDowns.Push(gateDownFor); gateDownFor = 0; }
		if (!mt.want) gateOffFor++; else if (gateOffFor) { gateOffs.Push(gateOffFor); gateOffFor = 0; }
		gatePrev = c;
		gateWas = mt.want;
	}

	static string ClockList(Array<int> a, int now)
	{
		string s = "";
		for (int i = 0; i < a.Size(); i++) s = s .. (i ? "," : "") .. a[i];
		if (now) s = s .. (s == "" ? "" : ",") .. "(" .. now .. " so far)";
		return s == "" ? "none" : s;
	}

	// --- MODE=1 and 2: 20 laps at each distance, at speed 20 and 10 ---------
	void ClockLaps(Actor mo, int t, int speed)
	{
		static const int loops[] = { 1024, 512, 2048 };
		if (t == 5) { clockRun = 0; ClockStartRun(mo, t, loops[0], speed, String.Format("loop%d_speed%d", loops[0], speed)); }
		if (clockRun < 3 && t > 5 && ClockRunDone(t, 20))
		{
			ClockReport(clockW, 20);
			if (++clockRun < 3) ClockStartRun(mo, t, loops[clockRun], speed, String.Format("loop%d_speed%d", loops[clockRun], speed));
		}
	}

	// --- MODE=3: faster pulses, a pulse through RED, the lever pulled twice ---
	void ClockOdd(Actor mo, int t)
	{
		static const int speeds[] = { 40, 60, 100, 200 };
		if (t == 5) { clockRun = 0; ClockStartRun(mo, t, 512, speeds[0], "loop512_speed40"); }
		if (clockRun < 4 && t > 5 && ClockRunDone(t, 20))
		{
			ClockReport(clockW, 20);
			if (++clockRun < 4) ClockStartRun(mo, t, 512, speeds[clockRun], String.Format("loop512_speed%d", speeds[clockRun]));
			else
			{
				// RED in 114: the pulse comes out of RED's far side, at the range's west end
				ClockKill();
				ClockClear(mo);
				BeltHang(mo, DoorOf(1), 114);
				clockDeaths = 0;
				clockP = ClockFire(mo, 1, 20);
				clockW = null;
				clockPhase = 1;
				clockT2 = 0;
			}
		}
		let p = clockP;
		if (clockPhase == 1)
		{
			if (!clockT2 && p && p.bMissile && p.pos.y < -100)
			{
				clockT2 = t;
				clockX = p.pos.x;
				Console.Printf("AJARTEST info t=%d through RED: out at (%.3f,%.3f,%.3f), vel (%.4f,%.4f,%.4f), angle %.2f", t, p.pos.x, p.pos.y, p.pos.z, p.vel.x, p.vel.y, p.vel.z, p.angle);
				Check("outOfRedsFarSide", p.pos.x > -16 && p.pos.x < 8 && abs(p.pos.y + 192) < 0.001 && abs(p.pos.z - 40) < 0.001);
				Check("keepsItsDirection", abs(p.vel.x - 20) < 0.001 && abs(p.vel.y) < 0.001 && abs(p.vel.z) < 0.001);
			}
			if (clockT2 && t == clockT2 + 10 && p && p.bMissile)
			{
				Console.Printf("AJARTEST info 10 tics on: (%.3f,%.3f,%.3f)", p.pos.x, p.pos.y, p.pos.z);
				Check("straightOnInTheRange", abs(p.pos.x - clockX - 200) < 0.001 && abs(p.pos.y + 192) < 0.001 && abs(p.pos.z - 40) < 0.001);
			}
			if (clockDeaths)
			{
				Check("burstsAtTheRangesEnd", clockDeathPos.x > 1000 && clockDeathPos.x < 1024 && abs(clockDeathPos.y + 192) < 0.001);
				// the lever pulled twice, 10 tics apart, on the 1024 loop
				ClockStartRun(mo, t, 1024, 20, "pulledTwice");
				clockT1 = t;
				clockPhase = 2;
			}
		}
		else if (clockPhase == 2 && t == clockT1 + 10)
		{
			AjarPulse first = clockW.p;
			let second = ClockFire(mo, 1, 20);
			Console.Printf("AJARTEST info the lever pulled again at t=%d: the first pulse (at x %.1f) %s; pulses flying: %d", t,
				first.pos.x, first.recalled ? "is called back" : "flies on", ClockAlive());
			Check("secondPullCallsTheFirstBack", first.recalled && ClockAlive() == 1 && second != first && second.bMissile);
			ClockWatch(second, "pulledTwice", ClockPath(1024) / 20);
			clockPhase = 3;
		}
		else if (clockPhase == 3 && clockW.marks > 5)
		{
			ClockReport(clockW, 5);
			Check("onePulseFlying", ClockAlive() == 1);
			// a rocket across the contact, beside the lanes: no beat
			let mt = ClockMetronome();
			clockN = mt.beats - clockW.p.beats;
			let r = Actor.Spawn("Rocket", (1700, 320, 40));
			r.angle = 0;
			r.Vel3DFromAngle(20, 0, 0);
			clockT1 = t;
			clockPhase = 4;
		}
		else if (clockPhase == 4 && t == clockT1 + 30)
		{
			let mt = ClockMetronome();
			let c = AjarContact(level.CreateActorIterator(1110, "AjarContact").Next());
			Check("aRocketIsNoBeat", c.others == 1 && mt.beats - clockW.p.beats == clockN);
			clockPhase = 5;
		}
	}

	// --- MODE=4: the gate held by the beat ----------------------------------
	void ClockGate(Actor mo, int t)
	{
		static const int loops[] = { 512, 1024, 2048, 2048 };
		static const int holds[] = { 70, 70, 70, 100 };
		static const int lens[] = { 400, 500, 1100, 500 };
		let mt = ClockMetronome();
		if (t == 5) clockRun = -1;
		if (clockRun >= 4) return;
		if (clockRun >= 0 && t - clockRunFrom < lens[clockRun]) return;
		if (clockRun >= 0)
		{
			string name = String.Format("gate%d_hold%d", loops[clockRun], holds[clockRun]);
			int laps = max(clockW.marks - 1, 0);
			Console.Printf("AJARTEST info %s: watched %d tics from the gate's first full rise, %d laps (%.2f tics a lap); let down %d times; %d tics moving against the metronome; fully up spans %s; fully down spans %s; spans not wanted %s; last period %d",
				name, gateTics, laps, laps ? clockW.sum / laps : 0., gateDrops, gateWrong,
				ClockList(gateUps, gateUpFor), ClockList(gateDowns, gateDownFor), ClockList(gateOffs, gateOffFor), mt.period);
			clockW.name = name;
			ClockReport(clockW, lens[clockRun] / int(clockW.expect + 1) - 2);
			Check(name .. "_neverMovesAgainstTheBeat", gateTics > 0 && gateWrong == 0);
			bool held = clockW.expect <= holds[clockRun];
			if (held) Check(name .. "_staysUp", gateTics > 0 && gateDrops == 0 && gateDowns.Size() == 0 && !gateDownFor && gateUps.Size() == 0 && gateUpFor == gateTics);
			else Check(name .. "_downAndUpEachLap", gateDrops >= laps - 1 && gateDowns.Size() >= laps - 2 && gateUps.Size() >= laps - 2);
		}
		if (++clockRun >= 4) return;
		mt.hold = holds[clockRun];
		ClockStartRun(mo, t, loops[clockRun], 20, "gate");
		ClockGateReset();
	}

	// --- MODE=5: a leaf taken while the pulse flies; the doorway ------------
	void ClockTaken(Actor mo, int t)
	{
		let mt = ClockMetronome();
		AjarDoor ta = LabLeaf(8, 0);
		AjarPulse p = clockW ? clockW.p : null;
		if (t == 5) { clockPhase = 0; ClockStartRun(mo, t, 1024, 20, "taken"); }
		if (t <= 5) return;
		switch (clockPhase)
		{
		case 0:     // three beats, then the leaf behind the pulse is taken
			if (p.beats >= 3 && ClockEastIn(p, 1100, 1700))
			{
				clockDeaths = 0;
				Console.Printf("AJARTEST info t=%d the pulse at x %.1f flying east, the gate up %d; the leaf in 113 is taken: 114's is a shut door now", t, p.pos.x, mt.GateUp());
				BeltTake(mo, 113);
				clockPhase = 1;
				clockT1 = 0;
			}
			break;
		case 1:     // it bursts on 114's shut leaf; the gate falls when the hold is over
			if (clockDeaths && !clockT1)
			{
				clockT1 = level.maptime;
				Check("burstsOnTheShutLeaf", clockDeathLine == 114 && clockDeathPos.x > 2040 && clockDeathPos.x < 2064 && level.IsPointInLevel(clockDeathPos));
				Console.Printf("AJARTEST info last beat at %d, burst at %d (level tics), hold %d", mt.lastBeat, clockT1, mt.hold);
			}
			if (clockT1 && level.maptime == mt.lastBeat + mt.hold) Check("gateUpUntilTheHoldIsOver", mt.GateUp() && mt.want);
			if (clockT1 && level.maptime == mt.lastBeat + mt.hold + 1) Console.Printf("AJARTEST info a tic later: wanted %d", mt.want);
			if (clockT1 && level.maptime == mt.lastBeat + mt.hold + 20)
			{
				Check("gateDownAfterTheHold", mt.GateDown() && !mt.want && mt.lastBeat < clockT1);
				clockDeaths = 0;
				ClockWatch(ClockFire(mo, 1, 20), "refired", ClockPath(1024) / 20);
				clockPhase = 2;
			}
			break;
		case 2:     // fired again with the loop still broken: it bursts there too
			if (clockDeaths)
			{
				Check("refiredBurstsOnTheShutLeaf", clockDeathLine == 114 && clockDeathPos.x > 2040 && clockDeathPos.x < 2064);
				BeltHang(mo, ta, 113);
				ClockWatch(ClockFire(mo, 1, 20), "rehung", ClockPath(1024) / 20);
				clockPhase = 3;
			}
			break;
		case 3:     // the leaf hung again: it laps, the beat and the gate come back
			if (p.beats >= 5 && ClockEastIn(p, 1100, 1700))
			{
				Console.Printf("AJARTEST info rehung: period %d, gate up %d", mt.period, mt.GateUp());
				Check("recovers", (mt.period == 52 || mt.period == 53) && mt.GateUp() && clockW.beatMiss == 0);
				clockDeaths = 0;
				BeltTake(mo, 114);
				Console.Printf("AJARTEST info t=%d the pulse at x %.1f flying east; the leaf in 114 is taken: an empty frame there", t, p.pos.x);
				clockPhase = 4;
			}
			break;
		case 4:
			if (clockDeaths)
			{
				Check("burstsOnTheEmptyFrame", clockDeathLine == 114 && clockDeathPos.x > 2040 && clockDeathPos.x < 2064);
				ClockStartRun(mo, t, 2048, 20, "nearer");
				clockPeriods.Clear();
				clockN = 0;
				clockPhase = 5;
			}
			break;
		case 5:     // the 2048 loop; after two beats, one move: the TEAL leaf from 111 to 113 (its ORANGE leaf comes off)
			if (mt.beats != clockN) { clockN = mt.beats; clockPeriods.Push(mt.period); }
			if (p.beats >= 3 && ClockEastIn(p, 1100, 1780))
			{
				Console.Printf("AJARTEST info t=%d the pulse at x %.1f flying east; the TEAL leaf in 111 is hung in 113 instead", t, p.pos.x);
				BeltHang(mo, ta, 113);
				Check("oneMove", FindFrame(113).door == ta && !FindFrame(111).door && ta.args[0] == 114);
				clockT1 = p.beats;
				clockPhase = 6;
			}
			break;
		case 6:
			if (mt.beats != clockN) { clockN = mt.beats; clockPeriods.Push(mt.period); }
			if (p.beats >= clockT1 + 4)
			{
				Console.Printf("AJARTEST info the periods, beat by beat: %s", ClockList(clockPeriods, 0));
				Check("nearerBeatsFaster", p.bMissile && (mt.period == 52 || mt.period == 53) && clockW.beatMiss == 0);
				clockPhase = 7;
				clockCase = 0;
			}
			break;
		case 7:     // the worst tics: the pulse put in a doorway and the leaf taken at once
		{
			static const double at[] = { 2050, 2061, 2063.9, 1011 };
			static const int frame[] = { 114, 114, 114, 113 };
			static const string what[] = { "middleInTheRecess", "boxOverTheLine", "middleAtTheLine", "justOutOfTheFarFrame" };
			if (clockCase >= 4) { clockPhase = 9; break; }
			if (!ClockEastIn(p, 1300, 1700)) break;
			clockDeaths = 0;
			p.SetOrigin((at[clockCase], p.pos.y, p.pos.z), false);
			BeltTake(mo, frame[clockCase]);
			Console.Printf("AJARTEST info t=%d case %s: the pulse put at x %.2f (its box %.2f..%.2f; 114's line at 2064, 113's at 1008), the leaf in %d taken",
				t, what[clockCase], p.pos.x, p.pos.x - p.radius, p.pos.x + p.radius, frame[clockCase]);
			clockT1 = t;
			clockP = p;
			clockPhase = 8;
			break;
		}
		case 8:
		{
			static const string what[] = { "middleInTheRecess", "boxOverTheLine", "middleAtTheLine", "justOutOfTheFarFrame" };
			p = clockP;
			if (t <= clockT1 + 3 || t % 10 == 0)
				Console.Printf("AJARTEST info t+%d: pulse %s at (%.2f,%.2f,%.2f)", t - clockT1, p && p.bMissile ? "flying" : "gone", p ? p.pos.x : 0., p ? p.pos.y : 0., p ? p.pos.z : 0.);
			if (t < clockT1 + 80) break;
			bool ok = clockDeaths == 1 && level.IsPointInLevel(clockDeathPos) && (!p || !p.bMissile) && ClockAlive() == 0;
			Check(what[clockCase] .. "_burstsInTheLevel", ok);
			Console.Printf("AJARTEST info %s: %d bursts, the last at (%.2f,%.2f) on line %d", what[clockCase], clockDeaths, clockDeathPos.x, clockDeathPos.y, clockDeathLine);
			clockCase++;
			ClockStartRun(mo, t, 1024, 20, "again");
			clockPhase = 7;
			break;
		}
		case 9:
			Check("allAccountedFor", ClockAlive() == 1 && clockW.p.bMissile);
			clockPhase = 10;
			break;
		}
	}

	// --- MODE=6: in the way: the player, a zombie, an imp, a demon and a
	// leaning door on lane A of the 1024 loop; the plain pulse, then the ripper
	Actor clockWho[4];
	int clockHp[4];
	void ClockWhoReport(string when)
	{
		static const string names[] = { "player", "zombie", "imp", "demon" };
		string s = "";
		for (int i = 0; i < 4; i++)
		{
			Actor a = clockWho[i];
			s = s .. String.Format("%s %d at (%.0f,%.0f)%s; ", names[i], a ? a.health : -1, a ? a.pos.x : 0., a ? a.pos.y : 0., a && a.health <= 0 ? " dead" : "");
		}
		Console.Printf("AJARTEST info %s: %s", when, s);
	}

	void ClockInTheWay(Actor mo, int t)
	{
		static const class<Actor> kinds[] = { "ZombieMan", "DoomImp", "Demon" };
		if (t == 5)
		{
			ClockLoop(mo, 1024);
			Pose(mo, 1200, 64, 0, 90);
			clockWho[0] = mo;
			for (int i = 0; i < 3; i++)
			{
				clockWho[i + 1] = Actor.Spawn(kinds[i], (1300 + 100 * i, 64, 0));
				clockWho[i + 1].angle = 90;
			}
			AjarDoor oa = LabLeaf(9, 0);
			oa.SetOrigin((1600, 64, 0), false);
			oa.angle = 90;
			for (int i = 0; i < 4; i++) clockHp[i] = clockWho[i].health;
			ClockWatch(ClockFire(mo, 1, 20, 0), "inTheWay_plain", ClockPath(1024) / 20);
			clockRunFrom = t;
			clockN = 0;
			clockPhase = 0;
			ClockWhoReport("before");
		}
		if (t <= 5) return;
		if (clockW.marks != clockN)
		{
			clockN = clockW.marks;
			ClockWhoReport(String.Format("%s mark %d", clockW.name, clockN));
		}
		if (clockPhase == 0 && clockW.marks > 10)
		{
			ClockReport(clockW, 10);
			bool same = true;
			for (int i = 0; i < 4; i++) if (clockWho[i].health != clockHp[i]) same = false;
			Check("plainHurtsNobody", same);
			// the ripper: the player can be hurt now (1000 health to count it)
			mo.player.cheats &= ~CF_GODMODE;
			mo.health = 1000;
			mo.player.health = 1000;
			for (int i = 0; i < 4; i++) clockHp[i] = clockWho[i].health;
			ClockWatch(ClockFire(mo, 1, 20, 1), "inTheWay_ripper", ClockPath(1024) / 20);
			clockN = 0;
			clockRunFrom = t;
			clockPhase = 1;
		}
		if (clockPhase == 1 && (clockW.marks > 10 || t - clockRunFrom > 1000))
		{
			ClockReport(clockW, 10);
			ClockWhoReport("after the ripper");
			Check("ripperHurtsThePlayer", mo.health < 1000);
			mo.player.cheats |= CF_GODMODE;
			clockPhase = 2;
		}
	}

	// --- MODE=7: the relay lever (ajarmap.lever and .shutter, MAP08's) ----
	int relayState, relayFrom, relayTopAt, relayDownAt, relayShutAt, relayPass, relayCycle, relayBounce;
	double relayPrev;

	Sector ClockShutter()
	{
		let it = level.CreateSectorTagIterator(SHUTTER_TAG);
		int i = it.Next();
		if (i < 0) return null;
		return level.sectors[i];
	}

	void ClockRelay(Actor mo, int t)
	{
		Sector s = ClockShutter();
		double c = s.CenterCeiling() - s.CenterFloor();
		// what the shutter does, tic by tic: 0 shut, 1 going up, 2 up, 3 coming down
		int now = c <= 0 ? 0 : c > relayPrev ? 1 : c < relayPrev ? 3 : 2;
		if (t > 1 && now != relayState)
		{
			static const string doing[] = { "shut", "going up", "up", "coming down" };
			Console.Printf("AJARTEST info t=%d the shutter %s (%.1f high), the count on the screen %d (%d.%d)", t, doing[now], c, shutterLeft,
				shutterLeft / 35, (shutterLeft % 35) * 10 / 35);
			if (now == 1 && relayState == 0) { relayCycle++; relayFrom = t; relayPass = 0; }
			if (now == 1 && relayState != 0) relayBounce++;      // (it stops a tic on what it met, then goes up)
			if (now == 2) relayTopAt = t;
			if (now == 3) relayDownAt = t;
			if (now == 0)
			{
				relayShutAt = t;
				Console.Printf("AJARTEST info cycle %d: up %d tics from the pull's first rise to shut, at the top %d tics, passable (56 high or more) %d tics",
					relayCycle, t - relayFrom, relayDownAt - relayTopAt, relayPass);
			}
			relayState = now;
		}
		if (c >= 56) relayPass++;
		relayPrev = c;

		if (t == 5) { mo.player.cheats &= ~CF_GODMODE; Pose(mo, 632, 470, 0, 90); }
		if (t == 10) { clockT1 = t; FindLine(320).Activate(mo, 0, SPAC_Use); }
		if (t == 12) Check("pullSendsItUp", relayState == 1 && shutterLeft > 0);
		// pulled again while it is up
		if (t == 110)
		{
			clockN = shutterLeft;
			Console.Printf("AJARTEST info t=%d pulled again while it is up: the count %d", t, shutterLeft);
			FindLine(320).Activate(mo, 0, SPAC_Use);
		}
		if (t == 111) Console.Printf("AJARTEST info a tic later the count is %d", shutterLeft);
		if (relayCycle == 1 && relayState == 0 && relayShutAt && !clockT2)
		{
			clockT2 = t;
			Check("upForFiveSeconds", relayDownAt - relayTopAt >= 174 && relayDownAt - relayTopAt <= 176);
			Check("secondPullChangedNothing", relayBounce == 0);
		}
		// pulled after it fell; then, as it comes down, the player put under it
		if (clockT2 && t == clockT2 + 20) FindLine(320).Activate(mo, 0, SPAC_Use);
		if (relayCycle == 2 && relayState == 3 && c < 90 && c > 60 && !clockT3)
		{
			clockT3 = t;
			clockN = mo.health;
			Pose(mo, 1632, 392, 0, 90);
			Console.Printf("AJARTEST info t=%d the player put under the shutter as it comes down (%.1f high)", t, c);
		}
		if (clockT3 && t > clockT3 && t <= clockT3 + 30 && t % 3 == 0)
			Console.Printf("AJARTEST info t=%d player at (%.1f,%.1f,%.1f) health %d, shutter %.1f high", t, mo.pos.x, mo.pos.y, mo.pos.z, mo.health, c);
		if (clockT3 && t == clockT3 + 30)
		{
			Check("notCrushed", mo.health == clockN && mo.pos.z == 0 && relayBounce == 1);
			Pose(mo, 1632, 470, 0, 90);         // on into the night room
			Check("notStuck", abs(mo.pos.y - 470) < 1);
		}
		if (clockT3 && relayCycle == 2 && relayState == 0 && relayShutAt > clockT3 && clockPhase == 0)
		{
			clockPhase = 1;
			Check("shutsAgainAfterTheBounce", c <= 0);
			Check("countGone", shutterLeft < 0);
			mo.player.cheats |= CF_GODMODE;
		}
	}

	void ClockScript(Actor mo, int t, int mode)
	{
		if (t == 1) mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		ClockWatchTick(t);
		ClockGateTick();
		if (mode == 1) ClockLaps(mo, t, 20);
		else if (mode == 2) ClockLaps(mo, t, 10);
		else if (mode == 3) ClockOdd(mo, t);
		else if (mode == 4) ClockGate(mo, t);
		else if (mode == 5) ClockTaken(mo, t);
		else if (mode == 6) ClockInTheWay(mo, t);
		else if (mode == 7) ClockRelay(mo, t);
	}
}
