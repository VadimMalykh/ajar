// Key levers (PLAN.md, "MAP32 room 4: two keys under fire"; MAP=MAP32 MODE=3,
// 5 and 8 tools/smoke.sh).
//
// AjarKeyLever thing (20056, ajartime.key_lever), on a wall: args[0] the sector
// tag of the AjarShutter it works, args[1] how many seconds the shutter stays
// open (0: 30), args[2] its number in its set (1, 2, ...). Every AjarKeyLever
// with the same args[0] is one SET. It looks and sounds like the press's
// switch (AJPS).
//  * USE (the player) pulls it if it is up and the shutter is not keyed open:
//    it shows down and is LIVE for JOIN tics (AjarHandler.TOGETHER_TICS, 70:
//    two seconds). The pull is written in the go's log (AjarGoLog.kTic, kTag,
//    kNum, apart from the press's pTic and pTag) in a room of goes and a fight
//    of goes, and an earlier self pulls that lever again at its tic if it is up
//    then (GhostKeys, called by GhostPresses).
//  * When every lever of the set is live at the same tic, the shutter is KEYED:
//    held open (AjarShutter.keyed, Held()) for the set's seconds from that tic,
//    with AjarTogether's joined sound; the levers stay down until the time is
//    up, then the shutter shuts by its usual rules (the player put clear on the
//    side it is worked from) and the levers come up, ready again. In the last
//    three seconds the press's warning beep, once a second.
//  * A live lever whose JOIN tics run out without the others comes up, with
//    AjarTogether's "too late" sound.
//  * Every go begins with every key lever up and every keyed shutter at rest
//    (KeysUp, called by ShuttersShut: Begin, Retake, Resume, NextGo, Anew, a
//    fight begun anew, BeginGoes). A fight of goes wound to a tic begins there
//    with them as the earlier selves' pulls before then left them (KeysAt,
//    from MixWound in goes.zs). After a fight's win the levers work the
//    same, in the room of goes it has become.
//  * Three messages, each once a level: the player's first pull that finds no
//    other lever of its set live; the first time a lever the player pulled runs
//    out; the first time a shutter is keyed while an earlier self is about.
// AjarKeyLamp thing (20057, ajartime.key_lamp), an AjarLamp beside a lever:
// args[0] the shutter's tag, args[1] the lever's number. Green while the
// shutter is keyed open; while another lever of the set is live, amber and
// green by turns every 6 tics with a click each half second ("now"); else
// amber while an earlier self's pull of another lever of the set comes within
// SOON (the timetable, table.zs); else red.
// The timetable (table.zs) has the earlier selves' key pulls (gold ticks on the
// bar), KeyPullIn(tag, n), and for a shutter worked by keys the holds that the
// earlier selves' own pulls make between them (HoldIn and the bar's green row).

class AjarKeyLever : Actor
{
	const JOIN = AjarHandler.TOGETHER_TICS;
	int pulledAt;               // level.maptime of the pull that made it live (-1: not live)
	bool held;                  // down while its shutter is keyed
	bool byPlayer;              // the live pull was the player's
	AjarShutter sh;

	Default { Radius 12; Height 24; +NOGRAVITY +WALLSPRITE +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJPS A -1 Bright;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		pulledAt = -1;
	}

	int Tics() { return 35 * (args[1] > 0 ? args[1] : 30); }
	int Number() { return args[2]; }
	AjarShutter Shutter()
	{
		if (!sh)
		{
			let it = ThinkerIterator.Create("AjarShutter");
			AjarShutter s;
			while (s = AjarShutter(it.Next())) if (s.args[0] == args[0]) sh = s;
		}
		return sh;
	}
	bool Live() { return !held && pulledAt >= 0 && level.maptime - pulledAt <= JOIN; }
	bool Up() { return !held && pulledAt < 0; }
	bool Keyed() { let s = Shutter(); return s && s.keyed > 0; }

	// At once up (a go begins).
	void Reset()
	{
		pulledAt = -1;
		held = false;
		byPlayer = false;
		frame = 0;
	}

	override bool Used(Actor user)
	{
		let mo = PlayerPawn(user);
		if (!mo || !mo.player) return false;
		if (!Up() || Keyed()) return true;          // down: nothing to pull
		let th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		if (th) th.KeyPull(self, false);
		return true;
	}

	override void Tick()
	{
		Super.Tick();
		if (held && !Keyed()) { held = false; pulledAt = -1; byPlayer = false; }      // the time is up: up again
		if (!held && pulledAt >= 0 && level.maptime - pulledAt > JOIN)
		{
			// alone: too late
			pulledAt = -1;
			A_StartSound("plats/pt1_stop", CHAN_VOICE);
			let th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
			if (byPlayer && th) th.KeySay(2);
			byPlayer = false;
		}
		frame = held || pulledAt >= 0 ? 1 : 0;
	}
}

// A lamp beside key lever args[1] of the shutter args[0].
class AjarKeyLamp : AjarLamp
{
	AjarShutter sh;

	override int Shows()
	{
		quiet = false;
		if (!sh)
		{
			let it = ThinkerIterator.Create("AjarShutter");
			AjarShutter s;
			while (s = AjarShutter(it.Next())) if (s.args[0] == args[0]) sh = s;
		}
		if (sh && sh.keyed > 0) return GREEN;
		let th = Th();
		if (!th) return RED;
		AjarKeyLever other = th.OtherLive(args[0], args[1]);
		if (other)
		{
			// now: amber and green by turns, a click each half second
			int age = level.maptime - other.pulledAt;
			quiet = true;
			if (age % 18 == 0) A_StartSound("switches/normbutn", CHAN_BODY, 0, 0.6);
			return (age / 6) % 2 ? GREEN : AMBER;
		}
		int soon = th.KeyPullIn(args[0], args[1]);
		return soon >= 0 && soon <= AjarTimeHandler.SOON ? AMBER : RED;
	}
}

extend class AjarTimeHandler
{
	int keySaid;                // the key levers' messages said in this level (bits 1, 2, 4)

	AjarKeyLever FindKeyLever(int tag, int n)
	{
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next())) if (k.args[0] == tag && k.args[2] == n) return k;
		return null;
	}

	// A live lever of the set `tag` other than number n (none: null).
	AjarKeyLever OtherLive(int tag, int n)
	{
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next())) if (k.args[0] == tag && k.args[2] != n && k.Live()) return k;
		return null;
	}

	// How many levers the set `tag` has (0: the shutter is not worked by keys).
	int KeyCount(int tag)
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next())) if (k.args[0] == tag) n++;
		return n;
	}

	void KeySay(int bit)
	{
		if (keySaid & bit) return;
		keySaid |= bit;
		if (bit == 1) Say("Two levers, one in each wing. Pulled within two seconds of each other\nthey open the shutter for half a minute.");
		else if (bit == 2) Say("Too late: the other lever was not pulled.");
		else if (bit == 4) Say("The shutter is open for half a minute.\nWhat an earlier self fired at it shut, it fires again now.");
	}

	// Lever k is pulled (by the player, or an earlier self).
	void KeyPull(AjarKeyLever k, bool ghost)
	{
		int tag = k.args[0];
		k.A_StartSound("switches/normbutn", CHAN_BODY);
		bool alone = !OtherLive(tag, k.args[2]);
		k.pulledAt = level.maptime;
		k.byPlayer = !ghost;
		k.frame = 1;
		if (!ghost)
		{
			KeyLog(k);
			if (alone) KeySay(1);
		}
		// every lever of the set live at once: the shutter is keyed
		Array<AjarKeyLever> set;
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever o;
		while (o = AjarKeyLever(it.Next()))
		{
			if (o.args[0] != tag) continue;
			if (!o.Live()) return;
			set.Push(o);
		}
		AjarShutter s = k.Shutter();
		if (!s) return;
		s.Key(k.Tics());
		for (int i = 0; i < set.Size(); i++) { set[i].held = true; set[i].byPlayer = false; }
		k.A_StartSound("misc/p_pkup", CHAN_AUTO);
		if (AllGhosts() > 0) KeySay(4);
	}

	// The player has pulled a lever: written down in this go's log.
	void KeyLog(AjarKeyLever k)
	{
		if (!(goes || mixed) || phase != LIVE || !logs.Size()) return;
		AjarGoLog lg = logs[logs.Size() - 1];
		lg.kTic.Push(ot); lg.kTag.Push(k.args[0]); lg.kNum.Push(k.args[2]);
	}

	// Every earlier self pulls the levers it pulled, at its tic, if they are up (GhostPresses calls it).
	void GhostKeys()
	{
		for (int i = 0; i < takes.Size() - 1 && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			for (; lg.kNext < lg.kTic.Size() && lg.kTic[lg.kNext] <= ot; lg.kNext++)
			{
				AjarKeyLever k = FindKeyLever(lg.kTag[lg.kNext], lg.kNum[lg.kNext]);
				if (k && k.Up() && !k.Keyed()) KeyPull(k, true);
			}
		}
	}

	// A go begins: every key lever up, no shutter keyed (ShuttersShut calls it).
	void KeysUp()
	{
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next())) k.Reset();
		let si = ThinkerIterator.Create("AjarShutter");
		AjarShutter s;
		while (s = AjarShutter(si.Next())) s.keyed = 0;
	}

	// A fight of goes wound to tic `to` (MixWound, goes.zs; after ShuttersShut): the levers and shutters
	// as the earlier selves' pulls before then left them. Their pulls in the order of their tics, by the
	// rules GhostKeys and the levers keep: a pull is done if the lever is up and its shutter not keyed;
	// a lever pulled is down until JOIN has run out (it comes up in the tic after), or while the shutter
	// it keyed is keyed; every lever of a set live at once keys it for the set's time. At `to`: a shutter
	// keyed then for what is left of its time, its levers down; a lever live then for what is left of
	// JOIN. Unheard. (WorldTick at `to` is the level's next tic.)
	void KeysAt(int to)
	{
		Array<AjarKeyLever> lev;
		Array<int> live, held;      // of each lever: the tic of its pull that is down (-1: none); down while keyed
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next())) { lev.Push(k); live.Push(-1); held.Push(0); }
		if (!lev.Size()) return;
		Array<int> tags, keyedAt;   // of each set: the tic it was keyed (-1: not)
		for (int q = 0; q < lev.Size(); q++) if (tags.Find(lev[q].args[0]) == tags.Size()) { tags.Push(lev[q].args[0]); keyedAt.Push(-1); }
		// the pulls before `to`, in the order of their tics (the same tic: by the order of the takes)
		Array<int> pt, pq;
		for (int i = 0; i < takes.Size() - 1 && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			for (int e = 0; e < lg.kTic.Size() && lg.kTic[e] < to; e++)
			{
				int q = 0;
				while (q < lev.Size() && (lev[q].args[0] != lg.kTag[e] || lev[q].args[2] != lg.kNum[e])) q++;
				if (q == lev.Size()) continue;
				int j = 0;
				while (j < pt.Size() && pt[j] <= lg.kTic[e]) j++;
				pt.Insert(j, lg.kTic[e]); pq.Insert(j, q);
			}
		}
		for (int e = 0; e <= pt.Size(); e++)
		{
			int t = e < pt.Size() ? pt[e] : to;
			// a set whose time is up: its levers up
			for (int s = 0; s < tags.Size(); s++)
			{
				if (keyedAt[s] < 0 || t - keyedAt[s] < KeyTics(tags[s])) continue;
				keyedAt[s] = -1;
				for (int r = 0; r < lev.Size(); r++) if (lev[r].args[0] == tags[s]) { held[r] = 0; live[r] = -1; }
			}
			// a lever whose JOIN has run out: up
			for (int r = 0; r < lev.Size(); r++) if (!held[r] && live[r] >= 0 && t - live[r] > AjarKeyLever.JOIN + 1) live[r] = -1;
			if (e == pt.Size()) break;
			int q = pq[e], s = tags.Find(lev[q].args[0]);
			if (held[q] || live[q] >= 0 || keyedAt[s] >= 0) continue;
			live[q] = t;
			bool all = true;
			for (int r = 0; r < lev.Size(); r++)
				if (lev[r].args[0] == tags[s] && (held[r] || live[r] < 0 || t - live[r] > AjarKeyLever.JOIN)) all = false;
			if (!all) continue;
			keyedAt[s] = t;
			for (int r = 0; r < lev.Size(); r++) if (lev[r].args[0] == tags[s]) held[r] = 1;
		}
		// as it is at `to`
		for (int s = 0; s < tags.Size(); s++)
		{
			if (keyedAt[s] < 0) continue;
			AjarShutter sh = FindShutter(tags[s]);
			// (its Tick counts it down once before then)
			if (sh) sh.keyed = KeyTics(tags[s]) - (to - keyedAt[s]) + 1;
		}
		for (int r = 0; r < lev.Size(); r++)
		{
			if (live[r] < 0) continue;
			lev[r].pulledAt = level.maptime + 1 - (to - live[r]);
			lev[r].held = held[r] != 0;
			lev[r].byPlayer = false;
			lev[r].frame = 1;
		}
	}

	// The time a set of key levers keys its shutter for.
	int KeyTics(int tag)
	{
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next())) if (k.args[0] == tag) return k.Tics();
		return 0;
	}

	// Tics until an earlier self's next pull of a lever of the set `tag` other than number n (-1: none).
	int KeyPullIn(int tag, int n)
	{
		let tb = Table();
		if (!tb.on) return -1;
		int best = -1;
		for (int i = 0; i < tb.kTic.Size(); i++)
			if (tb.kTag[i] == tag && tb.kNum[i] != n && tb.kTic[i] >= ot && (best < 0 || tb.kTic[i] - ot < best)) best = tb.kTic[i] - ot;
		return best;
	}

	// The timetable (table.zs): the spans in which the earlier selves' own key pulls (of the first n
	// takes), as logged, have every lever of the set `tag` live at once, each from that tic for the set's
	// time: khSelf (the self whose pull keyed it), khFrom, khTo (the tic after the last).
	Array<int> khSelf, khFrom, khTo;
	void KeyHolds(int tag, int n)
	{
		khSelf.Clear(); khFrom.Clear(); khTo.Clear();
		Array<int> nums, from;
		int dur = 0;
		let it = ThinkerIterator.Create("AjarKeyLever");
		AjarKeyLever k;
		while (k = AjarKeyLever(it.Next()))
		{
			if (k.args[0] != tag) continue;
			dur = k.Tics();
			if (nums.Find(k.args[2]) == nums.Size()) { nums.Push(k.args[2]); from.Push(-1); }
		}
		if (!nums.Size()) return;
		// the pulls, in the order of their tics
		Array<int> pt, pn, ps;
		for (int i = 0; i < n && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			for (int e = 0; e < lg.kTic.Size(); e++)
			{
				if (lg.kTag[e] != tag) continue;
				int j = 0;
				while (j < pt.Size() && pt[j] <= lg.kTic[e]) j++;
				pt.Insert(j, lg.kTic[e]); pn.Insert(j, lg.kNum[e]); ps.Insert(j, i);
			}
		}
		int till = -1;
		for (int e = 0; e < pt.Size(); e++)
		{
			int t = pt[e];
			if (t < till) continue;                // the levers are down while it is keyed
			if (till >= 0) { for (int z = 0; z < from.Size(); z++) from[z] = -1; till = -1; }
			int q = nums.Find(pn[e]);
			if (q == nums.Size()) continue;
			if (from[q] >= 0 && t - from[q] <= AjarKeyLever.JOIN) continue;     // live already
			from[q] = t;
			bool all = true;
			for (int r = 0; r < from.Size(); r++) if (from[r] < 0 || t - from[r] > AjarKeyLever.JOIN) all = false;
			if (!all) continue;
			khSelf.Push(ps[e]); khFrom.Push(t); khTo.Push(t + dur);
			till = t + dur;
		}
	}
}
