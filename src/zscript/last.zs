// THE LAST HALL of a map played in goes (third.zs's head has the contract:
// AjarThirdLast, AjarThirdGuard, the stands' tags; PLAN.md, "MAP33: the last
// fight together, as decided" and "The last fight lab"; the lab is map LAST,
// tools/map_last.py, its tests lasttest.zs, MAP=LAST MODE=1..4 tools/smoke.sh).
//
// Every go fights the same last fight anew, and the earlier selves fight in
// it with the player, really: what they fired in their own goes from the
// alarm on, they fire again, and what they shoot turns on them. Nothing of
// the last hall is recorded or played by puppets. All of it is only on a map
// with an AjarThirdLast: on any other (THIRD, MAP33 today) none of this runs.

class AjarThirdLast : AjarThirdMark {}
class AjarThirdGuard : AjarThirdMark {}

// An earlier self at a last hall: an AjarGhost (shootable from the alarm on,
// never harmed) that counts what hits it (the tests).
class AjarLastSelf : AjarGhost
{
	int hits;

	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		if (bShootable) hits++;
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
		// what the player fires is recorded from now
		lastClip = mo.CountInv("Clip");
		lastShell = mo.CountInv("Shell");
		lastShots.Clear();
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bMissile && a.target == mo) lastShots.Push(a);
		mo.A_StartSound("brain/sight", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		int need = LastNeed() / 35;
		if (tgo == 1) Say(String.Format("The alarm. Hold the plate: %d seconds in all.", need));
		else if (tgo < parts) Say(String.Format("The alarm. Hold plate %d while your earlier selves hold theirs:\n%d seconds in all.", tgo, need));
		else Say("The alarm. The exit door is open while every plate is held:\nget across to it.");
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
			if (k < parts) Say(String.Format("Plate %d is held: more of them come.", k));
			else Say("They have seen you on the floor: more of them come.");
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

	// time.zs's RecordTake, the part of it that writes down what was fired: bullets, shells, the player's missiles.
	void LastRecordFire(PlayerPawn mo)
	{
		if (alarmTic < 0) return;
		AjarTake t = takes[takes.Size() - 1];
		int clip = mo.CountInv("Clip"), shell = mo.CountInv("Shell");
		for (int i = clip; i < lastClip; i++) Fired(t, 1, null, mo.pos, (0, 0, 0));
		if (shell < lastShell) Fired(t, lastShell - shell >= 2 ? 3 : 2, null, mo.pos, (0, 0, 0));
		lastClip = clip; lastShell = shell;
		for (int i = lastShots.Size() - 1; i >= 0; i--) if (!lastShots[i]) lastShots.Delete(i);
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bMissile || a.target != mo || lastShots.Find(a) < lastShots.Size()) continue;
			lastShots.Push(a);
			Fired(t, 0, a.GetClass(), a.pos, a.vel);
		}
	}

	// From the alarm the earlier selves can be shot (and are never harmed), and
	// fire again what they fired then, really (as time.zs's PlayGhosts).
	void LastSelvesFight()
	{
		for (int i = 0; i < takes.Size() - 1 && i < ghosts.Size(); i++)
		{
			AjarGhost g = ghosts[i];
			if (!g) continue;
			AjarTake t = takes[i];
			bool pale = PaleAt(t, ot);
			g.bShootable = alarmTic >= 0 && !pale;
			if (!g.bShootable) continue;
			for (; t.next < t.evTic.Size() && t.evTic[t.next] <= ot; t.next++) LastFire(g, t, t.next);
		}
	}

	void LastFire(AjarGhost g, AjarTake t, int e)
	{
		int kind = t.evKind[e];
		if (kind == 0)
		{
			if (!t.evCls[e]) return;
			Actor m = Actor.Spawn(t.evCls[e], (t.ex[e], t.ey[e], t.ez[e]));
			if (!m) return;
			m.target = g;
			m.vel = (t.evx[e], t.evy[e], t.evz[e]);
			m.angle = VectorAngle(m.vel.x, m.vel.y);
			m.A_StartSound(m.SeeSound, CHAN_VOICE);
			return;
		}
		// a hitscan aims as the player's did (autoaim): at a monster along its angle, else as it looked
		FTranslatedLineTarget lt;
		double pitch = g.AimLineAttack(g.angle, 8192, lt);
		if (!lt.linetarget || !lt.linetarget.bIsMonster) pitch = g.pitch;
		int n = kind == 1 ? 1 : kind == 2 ? 7 : 20;
		double sh = kind == 1 ? 2.8 : kind == 2 ? 5.6 : 11.2, sv = kind == 3 ? 7.1 : 0;
		for (int j = 0; j < n; j++)
			g.LineAttack(g.angle + frandom[AjarGhost](-sh, sh), 8192, pitch + frandom[AjarGhost](-sv, sv),
				5 * random[AjarGhost](1, 3), 'Hitscan', "BulletPuff");
		g.A_StartSound(kind == 1 ? "weapons/chngun" : kind == 2 ? "weapons/shotgf" : "weapons/sshotf", CHAN_WEAPON);
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
		int i = guardIs.Find(e.Thing);
		if (i == guardIs.Size()) return;
		guardHitBy[i] = e.DamageSource;
		if (e.DamageSource is "AjarGhost") guardSelfDmg[i] += e.Damage;
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
