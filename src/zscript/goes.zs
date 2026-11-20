// The second goes lab (PLAN.md, "The second goes lab"; the test maps PRESS
// and TWOKEY, tools/map_press.py and tools/map_twokey.py; MAP=PRESS MODE=3
// and 4, MAP=TWOKEY MODE=3 tools/smoke.sh). Three pieces:
//
// A FIGHT THAT BECOMES A ROOM OF GOES (an AjarZone of a hall with args[4] 3,
// time.zs). Until it is won it is an open fight (time.zs, "the open fight":
// its boxes, ghosts whose shots are real, the last go's monsters on the
// demo, the rescue at death, winding), and besides, as in a room of goes
// (plate.zs):
//  * at the start of each go every door that has been touched is as at the
//    first entry, and each go writes down what the player did to doors and
//    presses; every earlier self does that again at its tic, by the same
//    rules (the conflict rule: if the door is not as it found it, that and
//    the rest of what it did to that door in this go is mimed);
//  * an earlier self on a plate (AjarPlate) presses it;
//  * an earlier self's shots hurt the monsters on the demo but never wake
//    one: only the present player does (hurting it, walking into it,
//    tripping its sentries), or the demo's end. A hit the demo already has
//    does nothing (the demo carries it); one it has not is counted, and
//    kills the monster, the player's kill, when it reaches its health
//    (AjarRail and Fell in time.zs, shut.zs's header).
// When it is won the steel door opens as for any fight (sector tag 3090 +
// 100 * fight), and from that moment the hall is a room of goes: its time
// doors lead into box 1 and it back by time door 1, any number of times; a
// go begins at the win, and the hall as it is then (bodies, doors and what
// else lies there) is the new first entry; the ghosts and the demo of the
// fight are gone and no monster comes again; only goes made after the win
// are played. Begin anew (AjarAnew) forgets the goes since the win. The
// room is over for good when the player leaves its zones by a way that is
// not a time door, as any room of goes.
//
// THE PRESS. AjarPress thing: args[0] the sector tag of its area (every
// sector with that tag). AjarPressSwitch thing, on a wall: args[0] the same
// tag; USE sets the press off, if it is up. A warning (WARN tics), then the
// ceiling of the area comes down to its floor (DOWN tics), stays (HOLD),
// and goes up again (RISE); then it can be set off again. It is moved by
// this script tic by tic (Sector.MoveCeiling, no mover is left behind).
// Everything living under it at the bottom and while it is down is killed:
// awake monsters and monsters on the demo alike, as by the player (the kill
// is theirs, and a monster on the demo dies really and is not put back),
// and the player (rescued into a box by the fight's rule, or dead). An
// earlier self under it is not hurt; bodies lying there stay as they lie
// (they are not ground). Each go begins with every press up and ready, and
// an earlier self's USE of a switch is done again at its tic (if the press
// is up then; if not, it is mimed). Key levers (keys.zs) are logged and
// pulled again by earlier selves the same way (GhostKeys, called from
// GhostPresses), each go beginning with them up (KeysUp in ShuttersShut).
//
// TWO KEYS AT ONCE. AjarTogether thing beside a frame (args[0] the frame's
// id): a lamp on the wall. A Pair whose leaves hang in two frames one of
// which (or both) has one joins only if the two were hung within
// TOGETHER_TICS of each other; otherwise both stay shut, as a leaf hung
// alone is. Taking a leaf down and hanging it again is a new hanging. Earlier
// selves' hangings count as the player's. While a leaf hangs alone in such a
// frame and its time is not up, the lamps blink and the leaf's ticks every
// half second; joined in time, a clear sound and the lamps are green; too
// late, a dull sound, a short message and the lamps are red.
//
// A PAIR JOINED FOR A TIME (MAP32's room 2; PLAN.md, "MAP32 room 2: the Pair
// shuts again"). AjarTogether args[1] n: the Pair stays joined n seconds after
// its second leaf is hung (0, as before: for good; if the lamps of the two
// frames differ, the smaller of those not 0). AjarDoor.joinEnds is the tic it
// shuts. While it is joined the lamps are green and beep (the key levers'
// beep) at every whole second left that is less than the whole time; at the
// end both leaves stay hanging but are no longer joined, exactly as two leaves
// hung too late (Late): shut, red lamps, the "too late" sound. To join it again
// both are taken down and hung together again. Whoever stands in either mouth
// then is put a step clear, on the side they are on (StandClear, as a sprung
// frame does; an earlier self is put where its record says each tic anyway).
// Two messages, once a level each: the first such join (said even when earlier
// selves made it) and the first time one shuts again. The timetable (table.zs)
// has a row for such a Pair with the spans in which the earlier selves'
// hangings have it joined, and the lamps of its frames are amber while one is
// about to begin (within SOON).

class AjarPress : Actor
{
	const WARN = 18;            // the warning, before it moves
	const DOWN = 16;            // coming down, about half a second
	const HOLD = 35;            // down, a second
	const RISE = 70;            // going up, two seconds
	int phase, t;               // 0 up and ready, 1 the warning, 2 coming down, 3 down, 4 going up
	bool byGhost;               // set off by an earlier self (tests)
	bool known;
	Array<int> secs;
	Array<double> top, bottom;
	double x1, y1, x2, y2;      // round the area, for the bodies in it
	// what it killed the last time it came down (tests)
	Array<Actor> victims;
	Array<int> victimDemo;
	int kills;                  // how much the level's kill count rose by them

	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	void Know()
	{
		if (known) return;
		known = true;
		x1 = y1 = 1e9; x2 = y2 = -1e9;
		let it = level.CreateSectorTagIterator(args[0]);
		int i;
		while ((i = it.Next()) >= 0)
		{
			Sector s = level.sectors[i];
			secs.Push(i); top.Push(s.CenterCeiling()); bottom.Push(s.CenterFloor());
			for (int j = 0; j < s.lines.Size(); j++)
			{
				for (int v = 0; v < 2; v++)
				{
					Vector2 p = v ? s.lines[j].v2.p : s.lines[j].v1.p;
					x1 = min(x1, p.x); y1 = min(y1, p.y); x2 = max(x2, p.x); y2 = max(y2, p.y);
				}
			}
		}
	}

	bool Ready() { return phase == 0; }
	bool Under(Actor a)
	{
		Know();
		return secs.Find(level.PointInSector(a.pos.xy).Index()) < secs.Size();
	}
	// how far down it is: 0 up, 1 at the floor
	double Lowered()
	{
		Know();
		if (!secs.Size() || top[0] == bottom[0]) return 0;
		return (top[0] - level.sectors[secs[0]].CenterCeiling()) / (top[0] - bottom[0]);
	}

	bool Start(bool ghost)
	{
		if (phase) return false;
		phase = 1;
		t = 0;
		byGhost = ghost;
		A_StartSound("switches/exitbutn", CHAN_VOICE);
		return true;
	}

	// Every ceiling of the area a share of the way down (0 up, 1 at the floor).
	void SetTo(double share)
	{
		Know();
		// the bodies lying there are not ground to pulp by it (the engine would)
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			if (a.bCorpse && a.pos.x > x1 - 64 && a.pos.x < x2 + 64 && a.pos.y > y1 - 64 && a.pos.y < y2 + 64) a.bDontGib = true;
		for (int i = 0; i < secs.Size(); i++)
		{
			Sector s = level.sectors[secs[i]];
			double want = top[i] + (bottom[i] - top[i]) * share, now = s.CenterCeiling();
			if (want == now) continue;
			// crush 0: what is in the way is squeezed, not hurt, and does not stop it
			s.MoveCeiling(abs(want - now), want, 0, want < now ? -1 : 1, false);
		}
	}

	// At once up and ready (a go begins).
	void Up()
	{
		phase = 0;
		t = 0;
		SetTo(0);
	}

	override void Tick()
	{
		Super.Tick();
		if (!phase) return;
		t++;
		if (phase == 1)
		{
			if (t < WARN) return;
			phase = 2; t = 0;
			A_StartSound("plats/pt1_strt", CHAN_BODY);
		}
		else if (phase == 2)
		{
			SetTo(min(1., t / double(DOWN)));
			if (t < DOWN) return;
			phase = 3; t = 0;
			A_StartSound("doors/dr2_clos", CHAN_BODY);
			victims.Clear(); victimDemo.Clear();
			kills = 0;
			Squash();
		}
		else if (phase == 3)
		{
			SetTo(1);
			Squash();
			if (t < HOLD) return;
			phase = 4; t = 0;
			A_StartSound("plats/pt1_strt", CHAN_BODY);
		}
		else if (phase == 4)
		{
			SetTo(1 - min(1., t / double(RISE)));
			if (t < RISE) return;
			phase = 0; t = 0;
			A_StartSound("plats/pt1_stop", CHAN_BODY);
		}
	}

	// Everything living under it dies, by the player's hand (an earlier self
	// is not hurt).
	void Squash()
	{
		let th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		Actor me = players[consoleplayer].mo;
		int before = level.killed_monsters;
		Array<Actor> hit;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			if (a.health > 0 && (a.bIsMonster || a.player) && !(a is "AjarGhost") && Under(a)) hit.Push(a);
		for (int i = 0; i < hit.Size(); i++)
		{
			a = hit[i];
			if (!a || a.health <= 0) continue;
			if (a.player) { a.DamageMobj(self, null, 100000, 'Crush', DMG_THRUSTLESS); continue; }
			bool demo = th && th.OnDemo(a);
			victims.Push(a); victimDemo.Push(demo);
			if (demo) th.Squashed(a, me, self);
			else a.DamageMobj(self, me, 100000, 'Crush', DMG_FORCED | DMG_THRUSTLESS);
		}
		kills += level.killed_monsters - before;
	}
}

// A switch on a wall: USE sets off the press whose tag is its args[0].
class AjarPressSwitch : Actor
{
	Default { Radius 12; Height 24; +NOGRAVITY +WALLSPRITE +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJPS A -1 Bright;
		Stop;
	Busy:
		AJPS B -1 Bright;
		Stop;
	}

	AjarPress Press()
	{
		let it = ThinkerIterator.Create("AjarPress");
		AjarPress p;
		while (p = AjarPress(it.Next())) if (p.args[0] == args[0]) return p;
		return null;
	}

	override bool Used(Actor user)
	{
		let mo = PlayerPawn(user);
		if (!mo || !mo.player) return false;
		AjarPress p = Press();
		if (!p) return false;
		A_StartSound("switches/normbutn", CHAN_BODY);
		if (!p.Start(false))
		{
			let h = AjarHandler(EventHandler.Find("AjarHandler"));
			if (h) h.Say("The press is not up yet.");
			return true;
		}
		let th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		if (th) th.PressLog(p);
		return true;
	}

	override void Tick()
	{
		Super.Tick();
		AjarPress p = Press();
		frame = p && !p.Ready() ? 1 : 0;
	}
}

// A lamp on the wall beside a frame (args[0] its id): a Pair joins there only
// if its leaves are hung together (args[1] n: and stays joined n seconds only).
class AjarTogether : Actor
{
	AjarFrame fr;
	int told;                   // the hanging (hungAt + 1) whose time ran out, told already

	Default { Radius 8; Height 16; +NOGRAVITY +WALLSPRITE +NOBLOCKMAP +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJTW A -1;
		Stop;
	Lamps:                      // only so that these are loaded: B lit, C joined, D too late, E amber (soon)
		AJTW BCDE -1;
		Stop;
	}

	const AMBER = 4;

	override void Tick()
	{
		Super.Tick();
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h) return;
		if (!fr) fr = h.FindFrame(args[0]);
		if (!fr) return;
		int show = 0;
		AjarDoor d = fr.door;
		if (d && d.IsPair())
		{
			AjarDoor tw = d.Twin();
			bool alone = !tw || !tw.frame;
			int age = level.maptime - d.hungAt;
			if (d.args[0] && d.joinEnds)
			{
				// joined for a time: a beep at each whole second left, and shut at the end
				int left = d.joinEnds - level.maptime;
				if (left <= 0) h.Unjoin(d);
				else if (left < d.joinTics && left % 35 == 0) A_StartSound("switches/exitbutn", CHAN_VOICE);
			}
			if (d.args[0]) show = 2;
			else if (alone && age < AjarHandler.TOGETHER_TICS)
			{
				show = (age / 9) % 2 ? 0 : 1;
				if (age % 18 == 0) A_StartSound("switches/normbutn", CHAN_BODY, 0, 0.6);
			}
			else
			{
				show = 3;
				if (alone && told != d.hungAt + 1)
				{
					told = d.hungAt + 1;
					A_StartSound("plats/pt1_stop", CHAN_VOICE);
					h.Say("Too late: the twin of the " .. d.Label() .. " leaf was not hung\nwithin two seconds of it. It stays shut.");
				}
			}
		}
		else
		{
			// a leaf hung in another such frame is waiting for its twin: blink with it
			int age = h.TickingAge();
			if (age >= 0) show = (age / 9) % 2 ? 0 : 1;
		}
		// not joined, nothing ticking: amber while the earlier selves' hangings are about to join it (table.zs)
		if (show == 0 && h.TickingAge() < 0 || show == 3)
		{
			let th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
			int soon = th ? th.PairJoinIn(args[0]) : -1;
			if (soon >= 0 && soon <= AjarTimeHandler.SOON)
			{
				if (frame != AMBER) A_StartSound("switches/normbutn", CHAN_BODY, 0, 0.35);
				show = AMBER;
			}
		}
		frame = show;
		bBright = show > 0;
	}
}

extend class AjarHandler
{
	const TOGETHER_TICS = 70;

	bool Together(AjarFrame f)
	{
		if (!f) return false;
		let it = ThinkerIterator.Create("AjarTogether");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == f.args[0]) return true;
		return false;
	}

	// Hang: may leaf d, just hung in f, join its twin (which hangs)?
	bool InTime(AjarDoor d, AjarFrame f, AjarDoor tw)
	{
		if (!Together(f) && !Together(tw.frame)) return true;
		bool ok = abs(d.hungAt - tw.hungAt) <= TOGETHER_TICS;
		f.A_StartSound(ok ? "misc/p_pkup" : "plats/pt1_stop", CHAN_AUTO);
		if (!ok) Say(LateText(d));
		return ok;
	}

	// Both leaves hang and are not joined, because they were not hung together.
	bool Late(AjarDoor d)
	{
		AjarDoor tw = d.Twin();
		return d.frame && tw && tw.frame && !d.args[0] && (Together(d.frame) || Together(tw.frame));
	}

	string LateText(AjarDoor d)
	{
		return "Too late: the two " .. d.Label() .. " leaves were not hung\nwithin two seconds of each other. Both stay shut.";
	}

	// --- a Pair joined for a time ---------------------------------------------------
	int pairSaid;               // its messages said in this level (bits 1: the first join for a time, 2: the first shut)
	int pairSaidAt;             // the tic (+ 1) the first was said (SayHung says nothing over it)

	// How many seconds a Pair hung in frames fa and fb stays joined (0: for good): the
	// smallest of their lamps' args[1] that is not 0.
	int JoinSeconds(int fa, int fb)
	{
		int best = 0;
		let it = ThinkerIterator.Create("AjarTogether");
		Actor a;
		while (a = Actor(it.Next()))
			if ((a.args[0] == fa || a.args[0] == fb) && a.args[1] > 0 && (!best || a.args[1] < best)) best = a.args[1];
		return best;
	}

	// Hang: leaf d has just joined its twin tw; for `tics` (0: for good).
	void JoinFor(AjarDoor d, AjarDoor tw, int tics)
	{
		d.joinTics = tw.joinTics = tics;
		d.joinEnds = tw.joinEnds = tics ? level.maptime + tics : 0;
		if (!tics || (pairSaid & 1)) return;
		pairSaid |= 1;
		pairSaidAt = level.maptime + 1;
		Say(String.Format("Both leaves of the %s pair hang: each frame opens onto the other,\nbut only for %d seconds. Then both shut again.", d.Label(), tics / 35));
	}

	// The time of a joined Pair is up: both leaves hang on, shut, as two hung too late.
	void Unjoin(AjarDoor d)
	{
		AjarDoor tw = d.Twin();
		Array<AjarDoor> both;
		both.Push(d);
		if (tw) both.Push(tw);
		for (int i = 0; i < both.Size(); i++)
		{
			AjarDoor o = both[i];
			o.args[0] = 0;
			o.joinEnds = o.joinTics = 0;
		}
		for (int i = 0; i < both.Size(); i++)
		{
			AjarDoor o = both[i];
			if (!o.frame) continue;
			Link(o.frame.args[0], 0, o.BackTex());
			o.Show();           // (hidden: a shut leaf is drawn on its line)
			StandClear(FindLine(o.frame.args[0]));
			o.frame.A_StartSound("plats/pt1_stop", CHAN_AUTO);
			Spring(o.frame);
		}
		ChainUpdate();
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info the %s pair shuts again at %d", d.Label(), level.maptime);
		if (pairSaid & 2) return;
		pairSaid |= 2;
		Say("The " .. d.Label() .. " pair has shut again. To join it, both leaves\nmust be taken down and hung together again.");
	}

	// How long ago a leaf that waits for its twin in such a frame was hung (-1: none waits).
	int TickingAge()
	{
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next()))
		{
			if (!d.IsPair() || !d.frame || d.args[0] || !Together(d.frame)) continue;
			AjarDoor tw = d.Twin();
			int age = level.maptime - d.hungAt;
			if ((!tw || !tw.frame) && age < TOGETHER_TICS) return age;
		}
		return -1;
	}
}

extend class AjarTimeHandler
{
	Array<int> mixFights;
	bool mixed;                 // the fight that is on is an open fight that becomes a room of goes

	// --- the fight that becomes a room of goes ---------------------------------
	void MixBegin(int k)
	{
		mixed = open && mixFights.Find(k) < mixFights.Size();
		if (!mixed) return;
		logs.Clear();
		logs.Push(new("AjarGoLog"));
		LeanHeld(k);
	}

	// A go begins (Retake, Resume): the doors as at the first entry, and a new log.
	void MixRetake(Actor mo)
	{
		FirstDoors();
		for (int i = 0; i < logs.Size(); i++) { logs[i].next = 0; logs[i].pNext = 0; logs[i].kNext = 0; logs[i].broken.Clear(); }
		logs.Push(new("AjarGoLog"));
	}

	// The player goes on as earlier self `best` (GoOnAs): what it did from now
	// on is not done, and what it holds is left leaning where it stands.
	void MixGoOnAs(int best, Actor g)
	{
		if (best < logs.Size())
		{
			AjarGoLog lg = logs[best];
			int n = 0;
			while (n < lg.tic.Size() && lg.tic[n] < ot) n++;
			lg.tic.Resize(n); lg.door.Resize(n); lg.car.Resize(n); lg.fCar.Resize(n); lg.frm.Resize(n); lg.fFrm.Resize(n);
			lg.x.Resize(n); lg.y.Resize(n); lg.z.Resize(n); lg.a.Resize(n); lg.fx.Resize(n); lg.fy.Resize(n);
			lg.next = min(lg.next, n);
			n = 0;
			while (n < lg.pTic.Size() && lg.pTic[n] < ot) n++;
			lg.pTic.Resize(n); lg.pTag.Resize(n);
			lg.pNext = min(lg.pNext, n);
			n = 0;
			while (n < lg.kTic.Size() && lg.kTic[n] < ot) n++;
			lg.kTic.Resize(n); lg.kTag.Resize(n); lg.kNum.Resize(n);
			lg.kNext = min(lg.kNext, n);
		}
		for (int i = 0; i < dHold.Size(); i++)
		{
			if (dHold[i] != best) continue;
			if (g) DoorSet(i, null, false, g.pos, g.angle);
			dHold[i] = -1;
		}
	}

	// Time was wound (WindTo): this go is begun over at `ot`. The doors are as
	// at the first entry with what the earlier selves did up to then done at
	// once; what the player did in this go so far is forgotten.
	void MixWound(Actor mo)
	{
		logs.Pop();
		FirstDoors();
		PressesUp();
		for (int i = 0; i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			lg.next = 0; lg.broken.Clear();
			for (lg.pNext = 0; lg.pNext < lg.pTic.Size() && lg.pTic[lg.pNext] < ot; lg.pNext++) {}
			for (lg.kNext = 0; lg.kNext < lg.kTic.Size() && lg.kTic[lg.kNext] < ot; lg.kNext++) {}
		}
		logs.Push(new("AjarGoLog"));
		GhostDoors();
	}

	// The fight is won (Win): the hall is a room of goes from now on.
	void WonGoes()
	{
		mixed = false;
		let mo = players[consoleplayer].mo;
		if (mo) mo.bBuddha = false;         // (a room of goes puts the player in its box instead: GoesTick, shut.zs)
		BeginGoes(fight, true);
	}

	// --- the press ----------------------------------------------------------------
	AjarPress FindPress(int tag)
	{
		let it = ThinkerIterator.Create("AjarPress");
		AjarPress p;
		while (p = AjarPress(it.Next())) if (p.args[0] == tag) return p;
		return null;
	}

	void PressesUp()
	{
		let it = ThinkerIterator.Create("AjarPress");
		AjarPress p;
		while (p = AjarPress(it.Next())) p.Up();
	}

	// The player has set a press off: written down in this go's log.
	void PressLog(AjarPress p)
	{
		if (!(goes || mixed) || phase != LIVE || !logs.Size()) return;
		AjarGoLog lg = logs[logs.Size() - 1];
		lg.pTic.Push(ot); lg.pTag.Push(p.args[0]);
	}

	// Every earlier self sets off the presses it set off, at its tic, if they are up.
	void GhostPresses()
	{
		for (int i = 0; i < takes.Size() - 1 && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			for (; lg.pNext < lg.pTic.Size() && lg.pTic[lg.pNext] <= ot; lg.pNext++)
			{
				int tag = lg.pTag[lg.pNext];
				AjarPress p = FindPress(tag);
				if (!p || !p.Start(true)) continue;
				let it = ThinkerIterator.Create("AjarPressSwitch");
				Actor s;
				while (s = Actor(it.Next())) if (s.args[0] == tag) s.A_StartSound("switches/normbutn", CHAN_BODY);
			}
		}
		GhostKeys();                // keys.zs: and the key levers they pulled
	}

	// A monster on the demo under a press: it dies really, by the player's
	// hand, and the demo lets it go.
	void Squashed(Actor a, Actor mo, Actor by)
	{
		let rail = AjarRail(a.FindInventory("AjarRail"));
		AjarRole r = null;
		for (int i = 0; demo && i < demo.roles.Size() && !r; i++) if (demo.roles[i].actor == a && demo.roles[i].mode == 1) r = demo.roles[i];
		if (r) Release(r, rail);
		else if (rail) { a.RemoveInventory(rail); rail.Destroy(); }
		let d = GetDefaultByType(a.GetClass());
		a.bSolid = d.bSolid;
		a.bBright = d.bBright;
		a.bShootable = true;
		a.health = 1;
		a.DamageMobj(by, mo, 100000, 'Crush', DMG_FORCED | DMG_THRUSTLESS);
	}

	// --- the tests (maps PRESS and TWOKEY) ------------------------------------------
	const PRESS_TAG = 3500;
	int pressStep, pressUsed, pressBefore, pressT;
	Array<Actor> bodies;
	Array<double> bodyX, bodyY;
	double redX, redY;
	AjarDoor pressRed;

	AjarPressSwitch FirstSwitch()
	{
		let it = ThinkerIterator.Create("AjarPressSwitch");
		return AjarPressSwitch(it.Next());
	}

	// monsters of the fight alive under the press (on the demo: `demo` 1, awake 0, either -1)
	int UnderPress(AjarPress p, int onDemo = -1)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			if (a.bIsMonster && a.health > 0 && p.Under(a) && (onDemo < 0 || OnDemo(a) == (onDemo > 0))) n++;
		return n;
	}

	bool PressUp(AjarPress p) { return p.Ready() && p.Lowered() < 0.01; }

	// every monster on the demo stands where its record says (as theyPlayAsTheyWent in MAP31)
	bool AsTheyWent()
	{
		if (!demo) return false;
		int n = 0;
		for (int i = 0; i < demo.roles.Size(); i++)
		{
			AjarRole r = demo.roles[i];
			if (r.mode != 1 || !r.actor || r.dead || r.hidden) continue;
			int j = ot - 1 - r.born;
			if (j < 0 || j >= r.x.Size()) continue;
			if (r.actor.pos.x != r.x[j] || r.actor.pos.y != r.y[j]) return false;
			n++;
		}
		return n > 0;
	}

	void KillAll(Actor mo)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k == fight) a.DamageMobj(mo, mo, 100000, 'None', DMG_THRUSTLESS);
		}
	}

	// MODE=3: the press in a fight, the win, and the room of goes after it.
	void PressScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;       // the level again, after its exit
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarPress p = FindPress(PRESS_TAG);
		AjarPressSwitch sw = FirstSwitch();
		AjarDoor red = Door32(1);
		AjarFrame f1 = h.FindFrame(101);
		AjarPlate pl = h.PlateFor(f1);
		Line l1 = h.FindLine(101);
		int g = takes.Size(), o = ot;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d) phase=%d open=%d mixed=%d goes=%d at=%d trips=%d go=%d ot=%d len=%d onDemo=%d awake=%d under=%d press=%d/%.2f kills=%d step=%d",
			t, mo.pos.x, mo.pos.y, phase, open, mixed, goes, at, trips, g, o, demo ? demo.len : -1, Rails(true), Rails(false),
			p ? UnderPress(p) : -1, p ? p.phase : -1, p ? p.Lowered() : -1, level.killed_monsters, pressStep);
		if (t == 1) Go(mo, 512, 40, 0, 90);
		if (t == 4) Check("begun", phase == LIVE && open && mixed && fight == 1 && p && sw && red && f1 && pl && PressUp(p));
		// --- 1: go 1, in the middle of the press until they are close, and "killed" there ---
		if (pressStep == 0 && open && g == 1)
		{
			if (o == 10) Go(mo, 512, 660, 0, 270);
			if (o > 10 && !pressT && (UnderPress(p) >= 5 || o >= 500)) pressT = o;
			if (pressT && o == pressT + 40) { mo.health = mo.player.health = 1; pressStep = 1; }
		}
		if (pressStep == 1 && g == 2 && o == 2)
		{
			Check("killedIntoTheBox", open && phase == LIVE && at == 1 && mo.health == RESCUE_HEALTH && demo && ghosts.Size() <= 1);
			pressStep = 2;
		}
		// --- 2: go 2, at the switch; they go where they went, and the press comes down on them ---
		if (pressStep == 2 && g == 2)
		{
			if (o == 3) Go(mo, 320, 48, 0, 270);
			if (!pressUsed && o > 30 && Demoing() && (UnderPress(p, 1) >= max(3, Rails(true) / 2) || o >= demo.len - AjarPress.WARN - AjarPress.DOWN - 10))
			{
				Console.Printf("AJARTEST info under=%d onDemo=%d len=%d", UnderPress(p, 1), Rails(true), demo.len);
				Check("theyGoWhereTheyWent", at == 0 && AsTheyWent() && UnderPress(p, 1) >= 3 && !Rails(false));
				pressBefore = mo.player.killcount;
				sw.Used(mo);
				pressUsed = o;
			}
			int down = pressUsed + AjarPress.WARN + AjarPress.DOWN;
			if (pressUsed && o == down + 3)
				Check("pressCameDown", p.phase == 3 && p.Lowered() > 0.9 && !p.byGhost);
			if (pressUsed && o == down + 5)
			{
				int n = 0;
				for (int i = 0; i < p.victimDemo.Size(); i++) n += p.victimDemo[i];
				Console.Printf("AJARTEST info victims=%d onDemo=%d killed=%d mine=%d", p.victims.Size(), n, p.kills, mo.player.killcount - pressBefore);
				// the level's kill count rose by as many as it killed, and every one is the player's
				Check("killsAreMine", p.victims.Size() > 0 && p.kills == p.victims.Size() && mo.player.killcount - pressBefore == p.victims.Size());
			}
			if (pressUsed && o == down + 60)
			{
				int n = 0;
				bool ok = true;
				for (int i = 0; i < p.victims.Size(); i++)
				{
					Actor a = p.victims[i];
					if (!p.victimDemo[i]) continue;
					n++;
					if (!a || a.health > 0 || OnDemo(a)) ok = false;
					for (int r = 0; demo && r < demo.roles.Size(); r++) if (demo.roles[r].actor == a && demo.roles[r].mode != 2) ok = false;
				}
				Check("killedOnTheDemo", n > 0 && ok);
			}
			// the rest by hand
			if (pressUsed && o > down + 62 && o < down + 120 && o % 5 == 0) KillAll(mo);
		}
		// --- 3: won; the clock door stays; a go after the win ---
		if (pressStep == 2 && goes)
		{
			pressStep = 3;
			Check("won", won.Find(1) < won.Size() && !open && !mixed && !Left() && !Rails(true) && takes.Size() == 1 && !GhostsHere());
		}
		if (pressStep == 3 && goes && g == 1)
		{
			if (o == 2)
			{
				Line hl = h.FindLine(HallLine(1, 1)), hl2 = h.FindLine(HallLine(1, 2)), bl = h.FindLine(BoxLine(1, 1));
				Check("clockDoorStays", !(hl.flags & Line.ML_BLOCKING) && !(hl2.flags & Line.ML_BLOCKING) && !(bl.flags & Line.ML_BLOCKING)
					&& (h.FindLine(BoxLine(1, 2)).flags & Line.ML_BLOCKING));
			}
			if (o == 40)
			{
				// the bodies, and the door, as they lie (the last of them have stopped sliding)
				bodies.Clear(); bodyX.Clear(); bodyY.Clear();
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next())) if (a.bIsMonster && a.health <= 0) { bodies.Push(a); bodyX.Push(a.pos.x); bodyY.Push(a.pos.y); }
				redX = red.pos.x; redY = red.pos.y;
				Console.Printf("AJARTEST info bodies=%d red=(%d,%d) steel=%d", bodies.Size(), redX, redY, SteelUp(1));
				Check("steelOpens", SteelUp(1));
			}
			if (o == 45) { Go(mo, 930, 150, 0, 0); red.Used(mo); }
			if (o == 47) { Go(mo, 990, 256, 0, 0); f1.Activate(mo); }
			if (o == 49) Go(mo, 700, 256, 0, 0);
			if (o == 260) Go(mo, 40, 128, 0, 180);
			if (o > 260 && o < 290) Walk(mo, (-8, 0));
		}
		if (pressStep == 3 && goes && g == 2)
		{
			if (o == 2)
			{
				bool lie = bodies.Size() > 3;
				for (int i = 0; i < bodies.Size(); i++)
					if (!bodies[i] || bodies[i].health > 0 || bodies[i].pos.x != bodyX[i] || bodies[i].pos.y != bodyY[i]) lie = false;
				int k, b;
				[k, b] = Where(mo.pos.xy);
				Console.Printf("AJARTEST info lie=%d red=(%d,%d) frame=%d press=%d", lie, red.pos.x, red.pos.y, red.frame != null, PressUp(p));
				Check("afterTheWin", at == 1 && b == 1 && !(h.FindLine(BoxLine(1, 1)).flags & Line.ML_BLOCKING) && !Left() && !Rails(true) && !Rails(false)
					&& lie && !red.frame && !red.carried && !red.bInvisible && Near(red, redX, redY) && !f1.door && PressUp(p) && takes.Size() == 2);
			}
			if (o == 3) Go(mo, 900, 256, 0, 0);
			if (o == 70) Check("myEarlierSelfHoldsIt", red.frame == f1 && pl.pressed && !(l1.flags & Line.ML_BLOCKING) && GhostsHere() == 1);
			if (o == 71) Go(mo, 980, 256, 0, 0);
			if (o > 71 && o < 90) Walk(mo, (8, 0));
		}
		if (pressStep == 3 && !goes && phase == IDLE)
		{
			pressStep = 4;
			pressT = t;
			Check("through", mo.pos.x > 1200 && won.Find(1) < won.Size());
		}
		if (pressStep == 4 && t > pressT && t < pressT + 60) Walk(mo, (8, 0));
	}

	// MODE=4: an earlier self's USE of the switch is done again; each go
	// begins with the press up; the player under it is killed into a box.
	void PressGoScript(PlayerPawn mo)
	{
		int t = testTic++;
		AjarPress p = FindPress(PRESS_TAG);
		AjarPressSwitch sw = FirstSwitch();
		int g = takes.Size(), o = ot;
		int u = pressUsed ? pressUsed : 200, down = u + AjarPress.WARN + AjarPress.DOWN;
		if (open && g == 2 && o >= u - 50 && o < down + 5) mo.player.cheats &= ~CF_GODMODE;
		else mo.player.cheats |= CF_GODMODE;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d) phase=%d open=%d at=%d go=%d ot=%d press=%d/%.2f ghost=%d under=%d",
			t, mo.pos.x, mo.pos.y, phase, open, at, g, o, p ? p.phase : -1, p ? p.Lowered() : -1, p && p.byGhost, p ? UnderPress(p) : -1);
		if (t == 1) Go(mo, 320, 48, 0, 270);
		if (!open) return;
		if (g == 1)
		{
			// at about tic 200, when nothing is under it
			if (!pressUsed && o >= 200 && (!UnderPress(p) || o >= 300)) { Console.Printf("AJARTEST info under=%d", UnderPress(p)); sw.Used(mo); pressUsed = o; }
			if (pressUsed && o == down + 3) Check("cameDownOnNothing", p.phase == 3 && !p.byGhost && !p.victims.Size());
			if (pressUsed && o == u + 45) mo.health = mo.player.health = 1;
		}
		if (g == 2)
		{
			if (o == 2) Check("upAtTheStart", PressUp(p) && at == 1);
			if (o == 3) Go(mo, 640, 48, 0, 270);
			// under the press when the earlier self sets it off
			if (o == u - 50) Go(mo, 512, 640, 0, 270);
			if (o == down - 3) Check("myEarlierSelfPressesIt", p.phase == 2 && p.byGhost && p.Lowered() > 0.5 && at == 0);
			// killed by it while that self is still in the hall: on as that self (the open fight's rule)
			if (o == down + 4) Check("killedByThePress", at == 0 && trips == 1 && mo.health == RESCUE_HEALTH && !p.Under(mo)
				&& Near(mo, takes[0].x[takes[0].x.Size() - 1], takes[0].y[takes[0].x.Size() - 1], 24) && takes[0].x.Size() <= down + 1);
			if (o == u + 50) mo.health = mo.player.health = 1;
		}
		if (g == 3 && o == 2)
			Check("upAtTheStartAgain", PressUp(p) && at == 2 && logs.Size() == 3 && logs[0].pTic.Size() == 1 && !logs[1].pTic.Size());
	}

	// MODE=3 on TWOKEY: two frames that join a Pair only if both leaves are hung within two seconds.
	int keyStep;
	AjarDoor KeyLeaf(bool west)      // the leaf that leans by frame A (west), or by frame B
	{
		for (int i = 0; i < dDoor.Size(); i++) if (dDoor[i] && dDoor[i].IsPair() && (d0x[i] < 600) == west) return dDoor[i];
		return null;
	}
	void TwoKeyScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor a = KeyLeaf(true), b = KeyLeaf(false);
		AjarFrame fa = h.FindFrame(131), fb = h.FindFrame(132);
		Line la = h.FindLine(131), lb = h.FindLine(132);
		int g = goes ? takes.Size() : 0, o = ot;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d) goes=%d go=%d ot=%d at=%d selves=%d carried=%s a=%d/%d b=%d/%d step=%d",
			t, mo.pos.x, mo.pos.y, goes, g, o, at, GhostsHere(), h.carried ? h.carried.Label() : "-",
			a && a.frame ? a.frame.args[0] : 0, a ? a.args[0] : -1, b && b.frame ? b.frame.args[0] : 0, b ? b.args[0] : -1, keyStep);
		if (t == 3)
		{
			int n = 0;
			let it = ThinkerIterator.Create("AjarTogether");
			while (it.Next()) n++;
			Check("begun", goes && phase == LIVE && g == 1 && a && b && fa && fb && n == 2 && h.Together(fa) && h.Together(fb));
		}
		// --- alone: A, a run, B: too late; B taken down, and out ---
		if (keyStep == 0 && g == 1)
		{
			if (o == 5) { Go(mo, 100, 230, 0, 90); a.Used(mo); }
			if (o == 7) { Go(mo, 40, 160, 0, 180); fa.Activate(mo); }
			if (o == 9) Check("itTicks", a.frame == fa && a.Shut() && h.TickingAge() >= 0 && h.TickingAge() < 10);
			if (o == 100) { Go(mo, 1100, 970, 0, 90); b.Used(mo); }
			if (o == 102) { Go(mo, 992, 1040, 0, 90); fb.Activate(mo); }
			if (o == 104) Check("tooLateAlone", a.frame == fa && b.frame == fb && a.Shut() && b.Shut() && h.Late(b)
				&& (la.flags & Line.ML_BLOCKING) && (lb.flags & Line.ML_BLOCKING));
			if (o == 106) fb.Activate(mo);
			if (o == 108) Check("tookDown", h.carried == b && !fb.door && a.Shut());
			if (o == 110) Go(mo, 480, 40, 0, 270);
			if (o > 110 && o < 135) Walk(mo, (0, -8));
		}
		// begin anew, then: A at 300 in go 1, B at 310 in go 2 (step 1); A at 300, B at 400 (step 2)
		if (g >= 2 && o == 3 && (keyStep == 0 || (keyStep == 1 && g == 3)))
		{
			Go(mo, 580, -224, 0, 0);
			AjarAnew w = AjarAnew(ThinkerIterator.Create("AjarAnew").Next());
			if (w) w.Used(mo);
			keyStep++;
			return;
		}
		if (keyStep >= 1 && g == 1)
		{
			if (o == 2 && keyStep == 1) Check("forgotten", !a.frame && !b.frame && !a.carried && !b.carried && !h.carried && !GhostsHere());
			if (o == 5) { Go(mo, 100, 230, 0, 90); a.Used(mo); }
			if (o == 7) Go(mo, 40, 160, 0, 180);
			if (o == 300) fa.Activate(mo);
			if (o == 330) Go(mo, 480, 40, 0, 270);
			if (o > 330 && o < 355) Walk(mo, (0, -8));
		}
		if (keyStep >= 1 && g == 2)
		{
			int when = keyStep == 1 ? 310 : 400;
			if (o == 3) { Go(mo, 1100, 970, 0, 90); b.Used(mo); }
			if (o == 5) Go(mo, 992, 1040, 0, 90);
			if (o == when) fb.Activate(mo);
			if (o == when + 2 && keyStep == 1)
				Check("joinedWithMyself", a.frame == fa && b.frame == fb && a.args[0] == 132 && b.args[0] == 131 && GhostsHere() == 1
					&& !(la.flags & Line.ML_BLOCKING) && !(lb.flags & Line.ML_BLOCKING));
			if (o == when + 2 && keyStep == 2)
				Check("tooLateTogether", a.frame == fa && b.frame == fb && a.Shut() && b.Shut() && h.Late(b) && (lb.flags & Line.ML_BLOCKING));
			if (keyStep == 1)
			{
				if (o == when + 4) Go(mo, 992, 1030, 0, 90);
				if (o > when + 4 && o < when + 20) Walk(mo, (0, 8));
				if (o == when + 22) Check("throughThePair", mo.pos.x < 300 && mo.pos.y > 100 && mo.pos.y < 260);
				if (o == when + 30) Go(mo, 480, 40, 0, 270);
				if (o > when + 30 && o < when + 55) Walk(mo, (0, -8));
			}
		}
	}
}
