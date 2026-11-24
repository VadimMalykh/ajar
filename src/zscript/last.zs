// THE LAST HALL of a map played in goes (third.zs's head has the contract:
// AjarThirdLast, AjarThirdGuard, the stands' tags; PLAN.md, "MAP33: the last
// fight together, as decided" and "The last fight lab"; the lab is map LAST,
// tools/map_last.py, its tests lasttest.zs, MAP=LAST MODE=1..4 tools/smoke.sh).
//
// Every go fights the same last fight anew, and the earlier selves fight in
// it with the player, really: what they fired in their own goes from the
// alarm on, they fire again, and what they shoot turns on them. Nothing of
// the last hall is recorded or played by puppets. All of it is only on a map
// with an AjarThirdLast: on any other (THIRD) none of this runs.
//
// Four ways the selves help each other besides (third.zs's rules 9 to 12;
// PLAN.md, "The last fight lab: four ways the selves help each other"; each
// only with its things or argument, so MAP33 today has none of them):
// waves by plates (each go a different fight: AjarThirdGuard args[1]), one
// share for three (AjarThirdShare), the stagger (an earlier self hit hard
// holds its fire: AjarThirdLast args[4]), the levers on the stands (the
// hall's machines, steam and a breaker: AjarThirdLever, AjarThirdVent).

class AjarThirdLast : AjarThirdMark {}
class AjarThirdGuard : AjarThirdMark {}
class AjarThirdShare : AjarThirdMark {}

// What a go's record has of the last hall besides where the player was and
// what they fired: the tic they took the share (+ 1; 0: not taken), the
// levers they worked (lever number, tic).
extend class AjarThirdTake
{
	int shareAt;
	Array<int> leverN, leverTic;
}

class AjarThirdVent : AjarThirdMark {}

// A lever on a stand's wall (the last hall's machines; AjarTimeHandler.LastLeverUsed):
// USE works it. Its pictures (gfx_time.py): A ready, B spent, C not yet.
class AjarThirdLever : Actor
{
	Default { Radius 12; Height 24; +NOGRAVITY +WALLSPRITE +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJLV C -1;
		Stop;
	ValveReady:
		AJLV A -1 Bright;
		Stop;
	ValveSpent:
		AJLV B -1;
		Stop;
	ValveWait:
		AJLV C -1;
		Stop;
	BreakerReady:
		AJBK A -1 Bright;
		Stop;
	BreakerSpent:
		AJBK B -1;
		Stop;
	BreakerWait:
		AJBK C -1;
		Stop;
	}

	// 0 not yet (before the alarm, or an earlier self's), 1 ready, 2 spent
	int shown;
	void Show(int st)
	{
		shown = st;
		if (args[1] == 2)
		{
			if (st == 1) SetStateLabel("BreakerReady");
			else if (st == 2) SetStateLabel("BreakerSpent");
			else SetStateLabel("BreakerWait");
		}
		else if (st == 1) SetStateLabel("ValveReady");
		else if (st == 2) SetStateLabel("ValveSpent");
		else SetStateLabel("ValveWait");
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		Show(0);
	}

	override bool Used(Actor user)
	{
		let h = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let mo = PlayerPawn(user);
		if (!h || !mo || !mo.player || !h.lastMark) return false;
		h.LastLeverUsed(mo, self);
		return true;
	}
}

// Steam over the floor: a puff of the IWAD's bullet smoke, rising, pale.
class AjarSteam : Actor
{
	Default { +NOINTERACTION +NOBLOCKMAP +NOGRAVITY RenderStyle "Translucent"; Alpha 0.75; Scale 2.4; }
	States
	{
	Spawn:
		PUFF BCD 5;
	Fade:
		PUFF D 2 A_FadeOut(0.06);
		Loop;
	}
}

// A spark at a stunned monster: the IWAD's plasma burst, small.
class AjarSpark : Actor
{
	Default { +NOINTERACTION +NOBLOCKMAP +NOGRAVITY RenderStyle "Add"; Alpha 0.9; Scale 0.35; }
	States
	{
	Spawn:
		PLSE ABCDE 2 Bright;
		Stop;
	}
}

// A copy of the share, at a share thing: pale and not to be taken, or real
// (SPECIAL: the player who touches it takes the item, AjarTimeHandler.LastShareTaken).
class AjarShareCopy : Actor
{
	Default { Radius 20; Height 45; }
	States
	{
	Spawn:
		PINV ABCD 6 Bright;
		Loop;
	Mega:
		MEGA ABCD 6 Bright;
		Loop;
	}

	override void Touch(Actor toucher)
	{
		let h = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let mo = PlayerPawn(toucher);
		if (h && mo && mo.player && mo.health > 0 && bSpecial) h.LastShareTaken(mo, self);
	}
}

// An earlier self at a last hall: an AjarGhost (shootable from the alarm on,
// never harmed) that counts what hits it (the tests) and sums the damage
// that hits it from the alarm on (not its own nor another self's or a
// player's): AjarThirdLast args[4] of it staggers it (LastStagger).
class AjarLastSelf : AjarGhost
{
	int hits;
	int dmgSum;                 // falls by 1 a tic; held at 0 while it is staggered
	int staggerFrom, staggerTo; // staggered from .. to (this go's tics; staggerTo <= ot: not)
	int staggers;               // how often in this go
	int fired, skipped;         // of its record's fire events: fired again, and skipped while staggered

	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		if (bShootable)
		{
			hits++;
			if (source != self && !(source is "AjarGhost") && !(source && source.player)) dmgSum += max(0, damage);
		}
		return Super.DamageMobj(inflictor, source, damage, mod, flags, angle);
	}
}

extend class AjarTimeHandler
{
	static int StandTag(int k) { return 3360 + k; }

	AjarThirdLast lastMark;
	Array<AjarThirdGuard> guards;
	Array<Actor> guardIs;       // guardIs[i]: guard i's monster in this go (none before the alarm)
	AjarShutter lastGate;       // the alarm's shutter (args[3])
	int alarmTic;               // the tic of this go the alarm rang (-1: not yet)
	int alarmAt;                // the tic it rings in this go, from the first self's record (-1: go 1, not known)
	// the waves (AjarThirdGuard args[1]): the highest of the map's guards (1: no waves), the tic of
	// this go wave w came (waveTic[w], -1: not yet), and when wave k (1 < k < parts) is to come in
	// this go by the record of the self that pressed plate k (waveAt[k], -1: not by a record)
	int waves;
	Array<int> waveTic, waveAt;
	int staggerLines;           // the stagger's lines said in this go (the tests: one a self staggered)
	// the share (AjarThirdShare): its places, the copies shown there in this go, the earlier self that
	// takes it in this go and when (-1: none), the tic it was taken or went in this go (-1: not yet)
	Array<AjarThirdShare> shares;
	Array<Actor> shareCopies;
	int shareSelf, shareTic, shareGone;
	// the levers (AjarThirdLever): the tic each worked in this go and until when it works (-1: not),
	// the earlier self whose record works it in this go and when (-1: none); the vents
	Array<AjarThirdLever> levers;
	Array<int> lvUsed, lvUntil, lvSelf, lvSelfTic;
	Array<AjarThirdVent> vents;
	// the breaker's stun: until when, the monsters held and whether they were DONTTHRUST, the hall's
	// sectors and their light
	int stunUntil;
	Array<Actor> stunned;
	Array<int> stunThrust;
	Array<int> hallSecs, hallLight, secLastHall;
	bool hallDimmed;
	int steamToPlayer, steamToMonster;      // damage the steam did (the tests)
	Array<int> guardSteam;                  // ... to each guard's monster
	int plateSum;               // the tics the player has stood on their plate in this go, that count
	bool standSaved;            // the save at the stand is made in this go
	int lastClip, lastShell;    // what the player carried a tic ago (what was fired: time.zs's RecordTake)
	Array<Actor> lastShots;     // the player's missiles already written down
	// who hurt each guard's monster last (its killer, once dead) and how: for the kill counters and the tests
	Array<Actor> guardHitBy;
	Array<int> guardSelfDmg;    // damage done to it by earlier selves
	transient double lastMs;    // what LastTick took this tic, in ms (the tests measure it)

	// --- the map ------------------------------------------------------------------
	// ThirdLoaded: has the map a last hall?
	void LastLoaded()
	{
		lastMark = AjarThirdLast(ThinkerIterator.Create("AjarThirdLast").Next());
		if (!lastMark) return;
		let it = ThinkerIterator.Create("AjarThirdGuard");
		AjarThirdGuard g;
		while (g = AjarThirdGuard(it.Next())) { guards.Push(g); guardIs.Push(null); guardHitBy.Push(null); guardSelfDmg.Push(0); }
		waves = 1;
		for (int i = 0; i < guards.Size(); i++) waves = max(waves, GuardWave(i));
		let si = ThinkerIterator.Create("AjarThirdShare");
		AjarThirdShare sh;
		while (sh = AjarThirdShare(si.Next())) shares.Push(sh);
		let lvi = ThinkerIterator.Create("AjarThirdLever");
		AjarThirdLever lv;
		while (lv = AjarThirdLever(lvi.Next())) { levers.Push(lv); lvUsed.Push(-1); lvUntil.Push(-1); lvSelf.Push(-1); lvSelfTic.Push(-1); }
		let vi = ThinkerIterator.Create("AjarThirdVent");
		AjarThirdVent vt;
		while (vt = AjarThirdVent(vi.Next())) vents.Push(vt);
		for (int i = 0; i < guards.Size(); i++) guardSteam.Push(0);
		for (int i = 0; i < level.sectors.Size(); i++) secLastHall.Push(0);
		let hi = level.CreateSectorTagIterator(lastMark.args[0]);
		int hs;
		while ((hs = hi.Next()) >= 0) { hallSecs.Push(hs); hallLight.Push(level.sectors[hs].lightlevel); secLastHall[hs] = 1; }
		lastGate = lastMark.args[3] ? FindShutter(lastMark.args[3]) : null;
		alarmTic = -1;
		alarmAt = -1;
	}

	int GuardWave(int i) { return max(1, guards[i].args[1]); }

	int LastNeed() { return 35 * (tgo == 1 ? (lastMark.args[1] ? lastMark.args[1] : 30) : (lastMark.args[2] ? lastMark.args[2] : 15)); }

	// Is p in the last hall or on a stand?
	bool InLast(Vector2 p)
	{
		if (SecTagged(p, lastMark.args[0])) return true;
		for (int k = 1; k <= parts; k++) if (SecTagged(p, StandTag(k))) return true;
		return false;
	}

	// --- a go begins: the hall as at the start ----------------------------------------
	void LastBegin(PlayerPawn mo)
	{
		if (!lastMark) return;
		LastClear(mo);
		alarmTic = -1;
		plateSum = 0;
		standSaved = false;
		lastShots.Clear();
		for (int i = 0; i < takes.Size(); i++) takes[i].next = 0;
		if (lastGate) { lastGate.keyed = 0; lastGate.ShutNow(); }
		// the alarm rings when the first self first steps onto plate 1 (a pale stretch presses nothing)
		alarmAt = -1;
		if (tgo >= 2 && plates.Size() && plates[0])
		{
			AjarTake t = takes[0];
			for (int j = 0; j < t.x.Size() && alarmAt < 0; j++) if (OnAt(plates[0], t, j) && !PaleAt(t, j)) alarmAt = j;
		}
		// wave k (1 < k < parts) comes in a later go than k at the first tic, from the alarm on, its self
		// k stands on plate k (as the alarm: a pale stretch presses nothing)
		waveTic.Clear(); waveAt.Clear();
		for (int w = 0; w <= parts; w++) { waveTic.Push(-1); waveAt.Push(-1); }
		for (int k = 2; k < parts && k <= plates.Size() && alarmAt >= 0; k++)
		{
			if (tgo <= k || !plates[k - 1] || k > takes.Size() - 1) continue;
			AjarTake t = takes[k - 1];
			for (int j = alarmAt; j < t.x.Size() && waveAt[k] < 0; j++) if (OnAt(plates[k - 1], t, j) && !PaleAt(t, j)) waveAt[k] = j;
		}
		LastShareBegin();
		LastLeverBegin();
		staggerLines = 0;
	}

	// What an earlier go left in the hall goes: the guards' monsters wherever
	// they went, and in the hall and on the stands every monster, body,
	// missile and dropped thing; the missiles the guards or the selves fired,
	// wherever they are. The kill counters lose what goes.
	void LastClear(PlayerPawn mo)
	{
		Array<Actor> gone;
		for (int i = 0; i < guardIs.Size(); i++) if (guardIs[i]) gone.Push(guardIs[i]);
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.player || a is "AjarGhost" || gone.Find(a) < gone.Size()) continue;
			let inv = Inventory(a);
			bool loose = a.bIsMonster || a.bMissile || a.bCorpse || (inv && !inv.owner && inv.bDropped);
			if (!loose) continue;
			bool fired = a.bMissile && a.target && (a.target is "AjarGhost" || guardIs.Find(a.target) < guardIs.Size());
			if (fired || InLast(a.pos.xy)) gone.Push(a);
		}
		for (int i = 0; i < gone.Size(); i++)
		{
			a = gone[i];
			if (!a) continue;
			if (a.bIsMonster && a.health > 0) a.ClearCounters();
			else if (a.bIsMonster && a.bCountKill)
			{
				// dead in an earlier go: it was counted, killed; and the player's kill (in single play the
				// engine gives the player every monster's death, whoever killed it; in a game of several, theirs)
				level.total_monsters--;
				level.killed_monsters--;
				int g = guardIs.Find(a);
				if (mo.player && mo.player.killcount > 0 && (!multiplayer || (g < guardIs.Size() && guardHitBy[g] == mo))) mo.player.killcount--;
			}
			a.Destroy();
		}
		for (int i = 0; i < guardIs.Size(); i++) { guardIs[i] = null; guardHitBy[i] = null; guardSelfDmg[i] = 0; }
	}

	// --- the tic -------------------------------------------------------------------
	// ThirdTick, after the earlier selves are where they are (ThirdSelves).
	void LastTick(PlayerPawn mo)
	{
		if (!lastMark || paradox) return;
		double t0 = MSTimeF();
		LastRecordFire(mo);         // (from the tic after the alarm)
		if (alarmTic < 0 && LastRings(mo)) LastAlarm(mo);
		LastWaves(mo);
		LastShareTick();
		LastMachines(mo);
		LastSelvesFight();
		LastStandSave(mo);
		LastPlates(mo);
		lastMs = MSTimeF() - t0;
	}

	// Plate 1 is first pressed in this go: in go 1 by the player (this tic's
	// record on it), later by the first self at the tic its record has.
	bool LastRings(PlayerPawn mo)
	{
		if (!plates.Size() || !plates[0]) return false;
		if (tgo == 1) return mo.health > 0 && OnAt(plates[0], takes[takes.Size() - 1], ot);
		return alarmAt >= 0 && ot >= alarmAt;
	}

	void LastAlarm(PlayerPawn mo)
	{
		alarmTic = ot;
		LastWave(mo, 1);
		if (lastGate) lastGate.keyed = HELD_OPEN;
		FireFrom(mo);               // what the player fires is recorded from now
		mo.A_StartSound("brain/sight", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		int need = LastNeed() / 35;
		string s;
		if (tgo == 1) s = String.Format("The alarm. Hold the plate: %d seconds in all.", need);
		else if (tgo < parts) s = String.Format("The alarm. Hold plate %d while your earlier selves hold theirs:\n%d seconds in all.", tgo, need);
		else s = "The alarm. The exit door is open while every plate is held:\nget across to it.";
		LastSay(s .. LastShareAlarm());
		for (int i = 0; i < levers.Size(); i++) levers[i].Show(lvSelf[i] < 0 ? 1 : 0);
	}

	// What the last hall says: a line said in the same tic as another (wave 2 with the alarm, a lever
	// with a wave) goes under it, not over it.
	string lastSaid;
	int lastSaidTic, lastSaidGo;
	void LastSay(string s)
	{
		if (lastSaidTic == ot && lastSaidGo == tgo && lastSaid != "") s = lastSaid .. "\n" .. s;
		lastSaid = s;
		lastSaidTic = ot;
		lastSaidGo = tgo;
		Say(s);
	}

	// --- the share: one item for every self -------------------------------------------
	static string Nth(int i)
	{
		static const string nth[] = { "first", "second", "third", "fourth", "fifth" };
		return nth[clamp(i, 0, 4)];
	}
	string ShareName() { return shares.Size() && shares[0].args[0] == 1 ? "megasphere" : "sphere"; }

	// A go begins: a pale copy at each share thing, not to be taken; the earlier self that takes it
	// in this go (the first in the records to have taken it: only one can have).
	void LastShareBegin()
	{
		for (int i = 0; i < shareCopies.Size(); i++) if (shareCopies[i]) shareCopies[i].Destroy();
		shareCopies.Clear();
		shareSelf = shareTic = shareGone = -1;
		if (!shares.Size()) return;
		for (int i = 0; i < takes.Size() - 1; i++)
		{
			let t = AjarThirdTake(takes[i]);
			if (t && t.shareAt > 0 && (shareTic < 0 || t.shareAt - 1 < shareTic)) { shareTic = t.shareAt - 1; shareSelf = i; }
		}
		for (int i = 0; i < shares.Size(); i++)
		{
			Actor c = Actor.Spawn("AjarShareCopy", shares[i].pos);
			if (!c) continue;
			if (shares[0].args[0] == 1) c.SetStateLabel("Mega");
			c.bSpecial = false;
			c.A_SetRenderStyle(0.4, STYLE_Translucent);
			shareCopies.Push(c);
		}
	}

	// The alarm: the copies become real, unless an earlier self takes it in this go (said).
	string LastShareAlarm()
	{
		if (!shareCopies.Size()) return "";
		if (shareSelf >= 0)
			return String.Format("\nThe %s is your %s self's: it takes it at %s.", ShareName(), Nth(shareSelf), ThirdClock(shareTic));
		for (int i = 0; i < shareCopies.Size(); i++)
		{
			Actor c = shareCopies[i];
			if (!c) continue;
			c.bSpecial = true;
			c.A_SetRenderStyle(1.0, STYLE_Normal);
			c.A_StartSound("misc/spawn", CHAN_AUTO);
		}
		return "";
	}

	// Every copy goes, each in an item's flash.
	void ShareGo()
	{
		shareGone = ot;
		for (int i = 0; i < shareCopies.Size(); i++)
		{
			Actor c = shareCopies[i];
			if (!c) continue;
			Actor.Spawn("ItemFog", c.pos, ALLOW_REPLACE);
			c.Destroy();
		}
		shareCopies.Clear();
	}

	// The earlier self that takes it does, at its record's tic (it is never in a pale stretch: the
	// player took it, they were not winding).
	void LastShareTick()
	{
		if (shareSelf < 0 || shareGone >= 0 || alarmTic < 0 || ot < shareTic) return;
		if (shareSelf < ghosts.Size() && ghosts[shareSelf]) ghosts[shareSelf].A_StartSound("misc/p_pkup", CHAN_AUTO);
		ShareGo();
	}

	// The player touches a real copy: they take the item (as if it were the item itself), the copies go,
	// the record has the tic.
	void LastShareTaken(PlayerPawn mo, Actor copy)
	{
		if (shareSelf >= 0 || shareGone >= 0 || alarmTic < 0) return;
		class<Inventory> cls = shares[0].args[0] == 1 ? "Megasphere" : "InvulnerabilitySphere";
		let it = Inventory(Actor.Spawn(cls, copy.pos));
		if (it)
		{
			it.Touch(mo);
			if (it && !it.bDestroyed && !it.owner) it.Destroy();
		}
		let t = AjarThirdTake(takes[takes.Size() - 1]);
		if (t) t.shareAt = ot + 1;
		ShareGo();
	}

	// Wave w's guards come (wave 1: the alarm's): each in a teleport fog,
	// awake, its first target the nearest it sees. How many came.
	int LastWave(PlayerPawn mo, int w)
	{
		waveTic[w] = ot;
		int n = 0;
		for (int i = 0; i < guards.Size(); i++)
		{
			AjarThirdGuard gd = guards[i];
			if (GuardWave(i) != w) continue;
			class<Actor> cls = AjarHandler.AmbushClass(gd.args[0]);
			if (!cls) continue;
			Actor m = Actor.Spawn(cls, gd.pos, ALLOW_REPLACE);
			if (!m) continue;
			m.angle = gd.angle;
			m.bAmbush = false;
			Actor.Spawn("TeleportFog", m.pos, ALLOW_REPLACE);
			Actor t = LastFirstTarget(m, mo);
			if (t)
			{
				m.target = t;
				m.SetState(m.SeeState);
			}
			guardIs[i] = m;
			guardHitBy[i] = null;
			guardSelfDmg[i] = 0;
			guardSteam[i] = 0;
			n++;
		}
		return n;
	}

	// The later waves (a map whose guards have them), from the alarm on: wave
	// k (1 < k < parts) the first time plate k is pressed (in go k by the
	// player, as the alarm in go 1; later by self k at its record's tic); the
	// last wave in the last go, the first time the player stands in the hall.
	void LastWaves(PlayerPawn mo)
	{
		if (waves < 2 || alarmTic < 0) return;
		for (int k = 2; k <= min(waves, parts); k++)
		{
			if (waveTic[k] >= 0) continue;
			bool now;
			if (k < parts)
				now = k <= plates.Size() && plates[k - 1] && ((tgo == k && mo.health > 0 && OnAt(plates[k - 1], takes[takes.Size() - 1], ot))
					|| (tgo > k && waveAt[k] >= 0 && ot >= waveAt[k]));
			else
				now = tgo == parts && mo.health > 0 && SecTagged(mo.pos.xy, lastMark.args[0]);
			if (!now || !LastWave(mo, k)) continue;
			mo.A_StartSound("brain/spit", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
			if (k < parts) LastSay(String.Format("Plate %d is held: more of them come.", k));
			else LastSay("They have seen you on the floor: more of them come.");
		}
	}

	// A monster's first target: the nearest of the player and the earlier
	// selves that it sees (the player if it sees none).
	Actor LastFirstTarget(Actor m, PlayerPawn mo)
	{
		Actor best = null;
		double bd = 1e12;
		if (mo.health > 0 && m.CheckSight(mo)) { best = mo; bd = m.Distance3D(mo); }
		for (int i = 0; i < ghosts.Size() && i < takes.Size() - 1; i++)
		{
			AjarGhost g = ghosts[i];
			if (!g || PaleAt(takes[i], ot) || !m.CheckSight(g)) continue;
			double d = m.Distance3D(g);
			if (d < bd) { bd = d; best = g; }
		}
		if (!best && mo.health > 0) best = mo;
		return best;
	}

	// What the player fires is followed from now (the alarm; a common place's group coming): what they
	// carry, and the missiles they have in flight already (not theirs to write down).
	void FireFrom(PlayerPawn mo)
	{
		lastClip = mo.CountInv("Clip");
		lastShell = mo.CountInv("Shell");
		lastShots.Clear();
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bMissile && a.target == mo) lastShots.Push(a);
	}

	bool AlarmOn() { return lastMark && alarmTic >= 0; }

	// time.zs's RecordTake, the part of it that writes down what was fired: bullets, shells, the player's missiles.
	// From the alarm; and in a common place (common.zs) from its group's coming, written while the player is in it.
	void LastRecordFire(PlayerPawn mo)
	{
		bool alarm = AlarmOn();
		if (!alarm && !CommonFollows()) return;
		bool write = alarm || CommonWrites(mo);
		AjarTake t = takes[takes.Size() - 1];
		int clip = mo.CountInv("Clip"), shell = mo.CountInv("Shell");
		if (write)
		{
			for (int i = clip; i < lastClip; i++) Fired(t, 1, null, mo.pos, (0, 0, 0));
			if (shell < lastShell) Fired(t, lastShell - shell >= 2 ? 3 : 2, null, mo.pos, (0, 0, 0));
		}
		lastClip = clip; lastShell = shell;
		for (int i = lastShots.Size() - 1; i >= 0; i--) if (!lastShots[i]) lastShots.Delete(i);
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bMissile || a.target != mo || lastShots.Find(a) < lastShots.Size()) continue;
			lastShots.Push(a);
			if (write) Fired(t, 0, a.GetClass(), a.pos, a.vel);
		}
	}

	// From the alarm the earlier selves can be shot (and are never harmed), and
	// fire again what they fired then, really (as time.zs's PlayGhosts); so do
	// they in a common place's fight (common.zs, CommonThere), aimed again there.
	// The one consumer of the records' fire: each tic every event whose tic has
	// come is fired (the self in the common place's fight now, or the alarm on
	// and the event written from it) or dropped, never fired late.
	void LastSelvesFight()
	{
		bool alarm = AlarmOn();
		for (int i = 0; i < takes.Size() - 1 && i < ghosts.Size(); i++)
		{
			AjarGhost g = ghosts[i];
			if (!g) continue;
			AjarTake t = takes[i];
			bool pale = PaleAt(t, ot);
			bool yard = CommonThere(i);
			g.bShootable = (alarm || yard) && !pale;
			let ls = AjarLastSelf(g);
			bool held = alarm && g.bShootable && ls && LastStagger(ls, i);
			for (; t.next < t.evTic.Size() && t.evTic[t.next] <= ot; t.next++)
			{
				int e = t.next;
				if (pale || t.evTic[e] < ot || !(yard || (alarm && t.evTic[e] >= alarmTic))) continue;     // dropped
				if (held) { ls.skipped++; continue; }
				LastFire(g, t, e, yard);
				if (ls) ls.fired++;
			}
		}
	}

	// A self hit hard is STAGGERED (AjarThirdLast args[4] n, 0: never): once the damage summed from the
	// alarm (falling by 1 a tic) reaches n, for STAGGER_TICS it fires nothing of its record (skipped, not
	// fired later), flickers between pale with the player's pain picture and as it is, and says so with
	// the player's pain sound; the sum is 0 again. It stands and presses its plate as its record has it.
	// True while it is.
	const STAGGER_TICS = 105;
	bool LastStagger(AjarLastSelf ls, int i)
	{
		int n = lastMark.args[4];
		if (n <= 0) return false;
		if (ls.staggerTo <= ot && ls.dmgSum >= n)
		{
			ls.staggerFrom = ot;
			ls.staggerTo = ot + STAGGER_TICS;
			ls.staggers++;
			ls.A_StartSound("player/male/pain100_1", CHAN_VOICE);
			if (ls.staggers == 1 && ++staggerLines)
				LastSay(String.Format("Your %s self is hit hard: it holds its fire for three seconds.\nKeep them off it.", Nth(i)));
		}
		if (ls.staggerTo <= ot)
		{
			if (ls.dmgSum > 0) ls.dmgSum--;
			return false;
		}
		ls.dmgSum = 0;
		if ((ot - ls.staggerFrom) / 4 % 2 == 0)
		{
			ls.A_SetRenderStyle(PALE_ALPHA, STYLE_Translucent);
			ls.frame = 6;               // PLAY G: the player's pain picture
		}
		return true;
	}

	// `again`: in a common place's fight, aimed again (common.zs).
	void LastFire(AjarGhost g, AjarTake t, int e, bool again = false)
	{
		int kind = t.evKind[e];
		if (kind == 0)
		{
			if (!t.evCls[e]) return;
			Actor m = Actor.Spawn(t.evCls[e], (t.ex[e], t.ey[e], t.ez[e]));
			if (!m) return;
			m.target = g;
			m.vel = (t.evx[e], t.evy[e], t.evz[e]);
			if (again) CommonAimMissile(g, m);      // common.zs: to a monster of the place near its way
			m.angle = VectorAngle(m.vel.x, m.vel.y);
			m.A_StartSound(m.SeeSound, CHAN_VOICE);
			return;
		}
		// a hitscan aims as the player's did (autoaim): at a monster along its angle, else as it looked;
		// `again`: first at a monster of the common place near its angle (common.zs)
		double ang = g.angle, pitch;
		if (!again || !CommonAimHitscan(g, ang, pitch))
		{
			FTranslatedLineTarget lt;
			pitch = g.AimLineAttack(g.angle, 8192, lt);
			if (!lt.linetarget || !lt.linetarget.bIsMonster) pitch = g.pitch;
		}
		int n = kind == 1 ? 1 : kind == 2 ? 7 : 20;
		double sh = kind == 1 ? 2.8 : kind == 2 ? 5.6 : 11.2, sv = kind == 3 ? 7.1 : 0;
		for (int j = 0; j < n; j++)
			g.LineAttack(ang + frandom[AjarGhost](-sh, sh), 8192, pitch + frandom[AjarGhost](-sv, sv),
				5 * random[AjarGhost](1, 3), 'Hitscan', "BulletPuff");
		g.A_StartSound(kind == 1 ? "weapons/chngun" : kind == 2 ? "weapons/shotgf" : "weapons/sshotf", CHAN_WEAPON);
		if (again) CommonFired(g);
	}

	// The first time in a go the player comes onto their stand: a save, so
	// that a death in the last fight costs the fight, not the part.
	void LastStandSave(PlayerPawn mo)
	{
		if (standSaved || mo.health <= 0 || !SecTagged(mo.pos.xy, StandTag(tgo))) return;
		standSaved = true;
		LevelLocals.MakeAutoSave();
	}

	// The player's plate is held: the sum, and this go's time door at it.
	void LastPlates(PlayerPawn mo)
	{
		if (alarmTic < 0 || tgo >= parts || tgo > plates.Size() || !plates[tgo - 1]) return;
		if (plates[tgo - 1].mine && mo.health > 0 && PlatesHeld(tgo - 1)) plateSum++;
		if (tdOpen || plateSum < LastNeed()) return;
		tdOpen = true;
		Doors().Link(TimeDoorId(tgo), BoxDoorId(tgo + 1), TIME_TEX);
		mo.A_StartSound("doors/dr1_open", CHAN_AUTO);
		Say("The door with a clock on it is open:\nthrough it is the start again, and your next part.");
	}

	// Who hurt a guard's monster (the last to hurt a dead one killed it).
	// (map32.zs's WorldThingDamaged calls it)
	void LastDamaged(WorldEvent e)
	{
		if (!lastMark || !e.Thing) return;
		bool steam = e.DamageType == 'AjarSteam';
		if (steam && e.Thing.player) steamToPlayer += e.Damage;
		else if (steam) steamToMonster += e.Damage;
		int i = guardIs.Find(e.Thing);
		if (i == guardIs.Size()) return;
		if (steam) guardSteam[i] += e.Damage;
		guardHitBy[i] = e.DamageSource;
		if (e.DamageSource is "AjarGhost") guardSelfDmg[i] += e.Damage;
	}

	// --- the levers: the hall's machines --------------------------------------------------
	static string LeverName(AjarThirdLever lv) { return lv.args[1] == 2 ? "breaker" : "steam valve"; }

	// A go begins: no machine runs, every lever not yet; which earlier self works each in this go
	// (the first in the records: only one can have).
	void LastLeverBegin()
	{
		LastStunEnd();
		stunUntil = -1;
		steamToPlayer = steamToMonster = 0;
		for (int i = 0; i < levers.Size(); i++)
		{
			lvUsed[i] = lvUntil[i] = lvSelf[i] = lvSelfTic[i] = -1;
			for (int s = 0; s < takes.Size() - 1; s++)
			{
				let t = AjarThirdTake(takes[s]);
				if (!t) continue;
				for (int e = 0; e < t.leverN.Size(); e++)
					if (t.leverN[e] == levers[i].args[0] && (lvSelfTic[i] < 0 || t.leverTic[e] < lvSelfTic[i])) { lvSelfTic[i] = t.leverTic[e]; lvSelf[i] = s; }
			}
			levers[i].Show(0);
		}
	}

	// USE on a lever: once a go, from the alarm on, not one an earlier self works in this go.
	void LastLeverUsed(PlayerPawn mo, AjarThirdLever lv)
	{
		int i = levers.Find(lv);
		if (i == levers.Size() || paradox) return;
		string what = LeverName(lv);
		string no = "";
		if (alarmTic < 0) no = String.Format("The %s does nothing yet: the hall's machines wake with the alarm.", what);
		else if (lvUsed[i] >= 0) no = String.Format("The %s is spent in this go.", what);
		else if (lvSelf[i] >= 0)
			no = String.Format("The %s is your %s self's: it %s it at %s.", what, Nth(lvSelf[i]), lv.args[1] == 2 ? "throws" : "opens", ThirdClock(lvSelfTic[i]));
		if (no != "")
		{
			mo.A_StartSound("*usefail", CHAN_VOICE);
			LastSay(no);
			return;
		}
		let t = AjarThirdTake(takes[takes.Size() - 1]);
		if (t) { t.leverN.Push(lv.args[0]); t.leverTic.Push(ot); }
		LeverGo(i, mo, -1);
	}

	// Lever i works now, by the player (who < 0) or by earlier self `who`'s record.
	void LeverGo(int i, PlayerPawn mo, int who)
	{
		AjarThirdLever lv = levers[i];
		bool breaker = lv.args[1] == 2;
		int secs = lv.args[3] ? lv.args[3] : breaker ? 5 : 6;
		lvUsed[i] = ot;
		lvUntil[i] = ot + 35 * secs;
		lv.Show(2);
		lv.A_StartSound("switches/exitbutn", CHAN_AUTO);
		string by = who < 0 ? "" : String.Format("Your %s self %s the %s. ", Nth(who), breaker ? "throws" : "opens", LeverName(lv));
		if (breaker)
		{
			stunUntil = max(stunUntil, lvUntil[i]);
			mo.A_StartSound("weapons/plasmax", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
			LastSay(String.Format("%sThe breaker is thrown:\neverything in the hall stands stunned for %d seconds.", by, secs));
		}
		else
		{
			for (int k = 0; k < vents.Size(); k++)
				if (vents[k].args[0] == lv.args[2] && k % 4 == 0) vents[k].A_StartSound("vile/firestrt", CHAN_AUTO);
			LastSay(String.Format("%sSteam blows over the marked floor:\n%d seconds.", by, secs));
		}
	}

	// Each tic from the alarm: an earlier self's lever works at its record's tic (not in a pale
	// stretch: as the alarm), and what runs runs.
	void LastMachines(PlayerPawn mo)
	{
		if (!levers.Size()) return;
		for (int i = 0; i < levers.Size(); i++)
			if (lvSelf[i] >= 0 && lvUsed[i] < 0 && alarmTic >= 0 && ot >= lvSelfTic[i] && !PaleAt(takes[lvSelf[i]], lvSelfTic[i]))
				LeverGo(i, mo, lvSelf[i]);
		for (int i = 0; i < levers.Size(); i++)
			if (levers[i].args[1] != 2 && lvUsed[i] >= 0 && ot < lvUntil[i]) LastSteam(i);
		if (stunUntil > ot) LastStun();
		else if (stunned.Size() || hallDimmed) LastStunEnd();
	}

	static double VentReach(AjarThirdVent v) { return v.args[1] ? v.args[1] : 96; }

	// STEAM: over the floor round lever i's vents (args[2]: the vents of that number), within each
	// one's reach and at its floor's height: puffs and a hiss, and every 4 tics 6 damage to whatever
	// lives there, monster or player, but the earlier selves.
	void LastSteam(int i)
	{
		int grp = levers[i].args[2];
		Array<AjarThirdVent> vs;
		for (int k = 0; k < vents.Size(); k++) if (vents[k] && vents[k].args[0] == grp) vs.Push(vents[k]);
		if (!vs.Size()) return;
		int o = ot - lvUsed[i];
		for (int k = 0; k < 4; k++)
		{
			AjarThirdVent v = vs[random[AjarLast](0, vs.Size() - 1)];
			double r = VentReach(v) * sqrt(frandom[AjarLast](0, 1)), a = frandom[AjarLast](0, 360);
			Actor p = Actor.Spawn("AjarSteam", (v.pos.xy + (cos(a), sin(a)) * r, v.pos.z + frandom[AjarLast](0, 12)));
			if (p) p.vel = (frandom[AjarLast](-0.4, 0.4), frandom[AjarLast](-0.4, 0.4), frandom[AjarLast](1.2, 2.6));
		}
		if (o % 35 == 17) vs[random[AjarLast](0, vs.Size() - 1)].A_StartSound("vile/firestrt", CHAN_AUTO);
		if (o % 4) return;
		Array<Actor> hit;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.health <= 0 || !(a.bIsMonster || a.player) || a is "AjarGhost") continue;
			for (int k = 0; k < vs.Size(); k++)
				if (abs(a.pos.z - vs[k].pos.z) <= 8 && (a.pos.xy - vs[k].pos.xy).Length() <= VentReach(vs[k])) { hit.Push(a); break; }
		}
		for (int k = 0; k < hit.Size(); k++) if (hit[k]) hit[k].DamageMobj(null, null, 6, 'AjarSteam');
	}

	// THE BREAKER: every living monster in the hall stands as it is (its state held, tics -1, not
	// moved, not thrust), and can be hurt and killed; sparks at it, the hall's light flickers.
	void LastStun()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || !secLastHall[a.CurSector.Index()]) continue;
			if (stunned.Find(a) == stunned.Size()) { stunned.Push(a); stunThrust.Push(a.bDontThrust); a.bDontThrust = true; }
			a.tics = -1;
			a.vel.xy = (0, 0);
			if (a.bNoGravity) a.vel.z = 0;
			if (random[AjarLast](0, 4) == 0)
			{
				double r = a.radius;
				Actor.Spawn("AjarSpark", a.pos + (frandom[AjarLast](-r, r), frandom[AjarLast](-r, r), frandom[AjarLast](0, a.height)));
				if (random[AjarLast](0, 9) == 0) a.A_StartSound("weapons/plasmaf", CHAN_AUTO, CHANF_DEFAULT, 0.6);
			}
		}
		if (ot % 3 == 0)
		{
			int d = random[AjarLast](0, 2) == 0 ? -56 : random[AjarLast](-8, 24);
			for (int k = 0; k < hallSecs.Size(); k++) level.sectors[hallSecs[k]].SetLightLevel(clamp(hallLight[k] + d, 0, 255));
			hallDimmed = true;
		}
	}

	// The stun is over: every monster held goes on from where it stood; the light is as it was.
	void LastStunEnd()
	{
		for (int k = 0; k < stunned.Size(); k++)
		{
			Actor a = stunned[k];
			if (!a) continue;
			a.bDontThrust = stunThrust[k];
			if (a.health > 0 && a.tics == -1) a.tics = 1;
		}
		stunned.Clear();
		stunThrust.Clear();
		if (hallDimmed) for (int k = 0; k < hallSecs.Size(); k++) level.sectors[hallSecs[k]].SetLightLevel(hallLight[k]);
		hallDimmed = false;
	}

	// --- winding on: not in the fight ---------------------------------------------------
	// ThirdWind: true when it is refused (the alarm is on, or the clock would wind into the fight).
	bool LastNoWind()
	{
		if (!lastMark) return false;
		if (alarmTic >= 0) { Say("The alarm is on: the clock does not wind on in the fight."); return true; }
		int next = -1;
		for (int s = 0; s < plFrom.Size(); s++)
			if (plFrom[s] - WIND_LEAD > ot && (next < 0 || plFrom[s] < next)) next = plFrom[s];
		if (next < 0 || alarmAt < 0 || next - WIND_LEAD < alarmAt) return false;
		Say(String.Format("The alarm rings at %s: the clock does not wind on into the fight.", ThirdClock(alarmAt)));
		return true;
	}

	// --- the timetable -------------------------------------------------------------
	// ThirdSchedule, on a map with a last hall: one line an earlier self (its
	// first step on its plate and the seconds it stood there, that counted),
	// and in the last go the first and last moment the exit door is open.
	void LastSchedule()
	{
		if (!lastMark) return;
		static const int colours[] = { Font.CR_YELLOW, Font.CR_GREEN, Font.CR_RED };
		int n = takes.Size() - 1;
		for (int i = 0; i < n && i < plates.Size(); i++)
		{
			int first = -1, sum = 0;
			for (int s = 0; s < plFrom.Size(); s++)
			{
				if (plSelf[s] != i) continue;
				if (first < 0 || plFrom[s] < first) first = plFrom[s];
				for (int j = plFrom[s]; j < plTo[s]; j++) if (SelvesOn(j, i)) sum++;
			}
			if (first < 0) continue;
			tLine.Push(String.Format("%d steps on plate %d  %s%s; stands %d s in all", i + 1, i + 1, ThirdClock(first),
				i == 0 ? ": the alarm" : "", sum / 35));
			tColor.Push(colours[min(i, 2)]);
			// (a map with waves: when it fires, the fight being another in each go)
			AjarTake t = takes[i];
			int ne = t.evTic.Size();
			if (waves > 1 && ne)
			{
				tLine.Push(String.Format("%d fires from %s to %s (%d shots)", i + 1, ThirdClock(t.evTic[0]), ThirdClock(t.evTic[ne - 1]), ne));
				tColor.Push(colours[min(i, 2)]);
			}
			if (shareSelf == i)
			{
				tLine.Push(String.Format("%d takes the %s  %s", i + 1, ShareName(), ThirdClock(shareTic)));
				tColor.Push(colours[min(i, 2)]);
			}
			for (int l = 0; l < levers.Size(); l++)
			{
				if (lvSelf[l] != i) continue;
				tLine.Push(String.Format("%d %s the %s  %s", i + 1, levers[l].args[1] == 2 ? "throws" : "opens", LeverName(levers[l]), ThirdClock(lvSelfTic[l])));
				tColor.Push(colours[min(i, 2)]);
			}
		}
		if (tgo == parts && n && heldFrom.Size())
		{
			tLine.Push(String.Format("the exit door open first at %s, the last time until %s",
				ThirdClock(heldFrom[0] + 1), ThirdClock(heldTo[heldFrom.Size() - 1] + openTics)));
			tColor.Push(Font.CR_WHITE);
		}
	}

	// Are earlier selves 0 .. upTo - 1 all on their plates at tic j (by the spans)?
	bool SelvesOn(int j, int upTo)
	{
		for (int e = 0; e < upTo; e++)
		{
			bool on = false;
			for (int s = 0; !on && s < plFrom.Size(); s++) on = plSelf[s] == e && j >= plFrom[s] && j < plTo[s];
			if (!on) return false;
		}
		return true;
	}

	// --- the HUD: the sum under the clock while it runs --------------------------------
	ui void LastOverlay(RenderEvent e)
	{
		if (!lastMark || alarmTic < 0 || tdOpen || tgo >= parts) return;
		static const int colours[] = { Font.CR_YELLOW, Font.CR_GREEN, Font.CR_RED };
		int need = 35 * (tgo == 1 ? (lastMark.args[1] ? lastMark.args[1] : 30) : (lastMark.args[2] ? lastMark.args[2] : 15));
		string s = String.Format("plate %d: %d of %d", tgo, plateSum / 35, need / 35);
		int y = 30 + BigFont.GetHeight() + 10 * tLine.Size();
		Screen.DrawText(BigFont, colours[min(tgo - 1, 2)], 320 - BigFont.StringWidth(s) / 2, y, s, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
	}
}
