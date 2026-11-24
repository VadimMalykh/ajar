// A COMMON PLACE of a map played in goes (third.zs's head has the contract
// and the rules: AjarThirdCommon, AjarThirdComer, AjarThirdWay, the levels'
// tags 3390 + k; PLAN.md, "MAP33: the yard in the middle, on three levels,
// as decided" and "The yard lab: a common place on three levels"; the lab is
// map YARD, tools/map_yard.py, its tests yardtest.zs, MAP=YARD MODE=1..3
// tools/smoke.sh).
//
// One place (a yard) that every part goes through, each on its own level,
// with railings that stop players only: shots, sight and flyers pass between
// the levels. Each part has its group of monsters there; in its go the group
// comes when the player first stands on its level, and the part's way on
// opens when the group is dead. In every later go the group comes again at
// that tic, really, while the earlier self is there: it can be shot (never
// harmed), it fires again what it fired there (aimed again at what moves),
// and at the tic its go had the group dead, what is left of it dies. All of
// it only on a map with an AjarThirdCommon: on any other nothing here runs.

class AjarThirdCommon : AjarThirdMark {}
class AjarThirdComer : AjarThirdMark {}
class AjarThirdWay : AjarThirdMark {}

extend class AjarTimeHandler
{
	static int LevelTag(int k) { return 3390 + k; }
	const AIM_AGAIN = 15;       // a self's shot in the place turns to a monster within this many degrees of its way

	AjarThirdCommon commonMark;
	Array<AjarThirdComer> comers;
	Array<Actor> comerBody;     // comerBody[i]: the body lying at seen-fallen comer i in this go (an AjarFigure), or none
	Array<AjarThirdWay> cmWays;
	Array<int> secCm;           // by sector index: -1 not in the place, 0 the place's own tag, k part k's level
	// by part k (index k, 1 .. parts): the tic of go k at which its group came and was all dead (-1: not;
	// kept for the later goes), the tic in this go self k is no longer in the place (its record's last tic
	// there + 1), whether its group has come in this go, whether its end has come in this go (a later go)
	Array<int> cmCome, cmDone, cmLeave, cmAgain, cmOver;
	// the groups' monsters in this go, wherever they went: the monster, its part, who hurt it last, whether
	// it counts as a kill and has died (one that leaves no body is gone before the next go's start, its kill
	// still counted: so the kill counters are put right by these, not by what is left)
	Array<Actor> cmMon, cmHitBy;
	Array<int> cmPart, cmKill, cmDied;
	Array<int> cmOverKilled;    // [k]: how many of group k died at its end in this go (the tests)
	// what the selves' shots did in the place (the tests, PLAN.md's figures): by self, the events fired
	// again in it and those that hit a monster; the missiles still to be counted, by self (-1: counted)
	Array<int> cmShots, cmShotsHit;
	Array<Actor> cmMissile;
	Array<int> cmMissileOf;
	Actor cmFiring;             // the self whose hitscan is being fired again now
	bool cmFireHit;             // ... and it hit a monster
	transient double commonMs;  // what CommonTick took this tic, in ms (the tests measure it)

	// --- the map ------------------------------------------------------------------
	// ThirdLoaded: has the map a common place?
	void CommonLoaded()
	{
		commonMark = AjarThirdCommon(ThinkerIterator.Create("AjarThirdCommon").Next());
		if (!commonMark) return;
		let ci = ThinkerIterator.Create("AjarThirdComer");
		AjarThirdComer c;
		while (c = AjarThirdComer(ci.Next())) { comers.Push(c); comerBody.Push(null); }
		let wi = ThinkerIterator.Create("AjarThirdWay");
		AjarThirdWay w;
		while (w = AjarThirdWay(wi.Next())) cmWays.Push(w);
		for (int i = 0; i < level.sectors.Size(); i++) secCm.Push(-1);
		for (int k = 0; k <= parts; k++)
		{
			let it = level.CreateSectorTagIterator(k ? LevelTag(k) : commonMark.args[0]);
			int s;
			while ((s = it.Next()) >= 0) secCm[s] = k;
		}
		for (int k = 0; k <= parts; k++)
		{
			cmCome.Push(-1); cmDone.Push(-1); cmLeave.Push(-1); cmAgain.Push(0); cmOver.Push(0); cmOverKilled.Push(0);
			cmShots.Push(0); cmShotsHit.Push(0);
		}
	}

	// Where p is: -1 not in the place, 0 in it on no level, k on part k's level.
	int CmAt(Vector2 p) { return secCm[level.PointInSector(p).Index()]; }
	bool InCommon(Vector2 p) { return commonMark && CmAt(p) >= 0; }

	// Is earlier self i (part i + 1) in the place's fight now: from its group's tic to its leaving the
	// place by its record, not in a pale stretch?
	bool CommonThere(int i)
	{
		int k = i + 1;
		if (!commonMark || k >= tgo || k > parts || i >= ghosts.Size() || !ghosts[i]) return false;
		return cmCome[k] >= 0 && ot >= cmCome[k] && ot < cmLeave[k] && !PaleAt(takes[i], ot);
	}

	// Has go tgo's group come (what the player fires is followed from then), and is the player in the place
	// now (what they fire is written in the take)?
	bool CommonFollows() { return commonMark && tgo <= parts && cmCome[tgo] >= 0; }
	bool CommonWrites(PlayerPawn mo) { return CommonFollows() && mo.health > 0 && CmAt(mo.pos.xy) >= 0; }

	// --- a go begins: the place as at the start -------------------------------------------
	void CommonBegin(PlayerPawn mo)
	{
		if (!commonMark) return;
		CommonClear(mo);
		if (tgo <= parts) { cmCome[tgo] = -1; cmDone[tgo] = -1; }
		for (int k = 0; k <= parts; k++) { cmAgain[k] = 0; cmOver[k] = 0; cmOverKilled[k] = 0; cmShots[k] = 0; cmShotsHit[k] = 0; }
		cmMissile.Clear(); cmMissileOf.Clear();
		cmFiring = null;
		for (int i = 0; i < takes.Size(); i++) takes[i].next = 0;
		// when each earlier self leaves the place: its record's last tic in it, from its group's coming, + 1
		for (int k = 1; k < tgo && k <= parts; k++)
		{
			cmLeave[k] = -1;
			if (cmCome[k] < 0) continue;
			AjarTake t = takes[k - 1];
			for (int j = cmCome[k]; j < t.x.Size(); j++) if (CmAt((t.x[j], t.y[j])) >= 0) cmLeave[k] = j + 1;
		}
		// the seen fallen: a body at each in the goes before its part's
		for (int i = 0; i < comers.Size(); i++)
		{
			AjarThirdComer c = comers[i];
			bool lie = tgo < c.args[1] && c.args[2] && LeavesBody(AjarHandler.AmbushClass(c.args[0]));
			if (lie && !comerBody[i])
			{
				Actor f = Actor.Spawn("AjarFigure", (c.pos.xy, level.PointInSector(c.pos.xy).floorplane.ZAtPoint(c.pos.xy)));
				if (!f) continue;
				f.args[0] = 2; f.args[1] = c.args[0];
				f.angle = c.angle;
				comerBody[i] = f;
			}
			else if (!lie && comerBody[i]) { comerBody[i].Destroy(); comerBody[i] = null; }
		}
		CommonWays(true);
	}

	// What an earlier go left of the groups goes: their monsters wherever they went, and in the place every
	// monster, body, missile and dropped thing; the missiles the groups or the selves fired, wherever they
	// are. The kill counters lose what goes (as LastClear), and the groups' dead that are gone already.
	void CommonClear(PlayerPawn mo)
	{
		for (int i = 0; i < cmMon.Size(); i++)
		{
			Actor m = cmMon[i];
			if (m && m.health <= 0) cmDied[i] = 1;
			if (cmDied[i] && cmKill[i])
			{
				// dead in an earlier go: counted, killed; and the player's kill (in single play the engine gives
				// the player every monster's death, whoever killed it; in a game of several, theirs)
				level.total_monsters--;
				level.killed_monsters--;
				if (mo.player && mo.player.killcount > 0 && (!multiplayer || cmHitBy[i] == mo)) mo.player.killcount--;
			}
			else if (m && !cmDied[i]) m.ClearCounters();
			if (m) m.Destroy();
		}
		cmMon.Clear(); cmPart.Clear(); cmHitBy.Clear(); cmKill.Clear(); cmDied.Clear();
		Array<Actor> gone;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.player || a is "AjarGhost") continue;
			let inv = Inventory(a);
			bool loose = a.bIsMonster || a.bMissile || a.bCorpse || (inv && !inv.owner && inv.bDropped);
			if (!loose) continue;
			// (the groups' missiles: their monsters are gone, so a missile without a target was theirs or a self's)
			bool fired = a.bMissile && (!a.target || a.target is "AjarGhost");
			if (fired || InCommon(a.pos.xy)) gone.Push(a);
		}
		for (int i = 0; i < gone.Size(); i++)
		{
			a = gone[i];
			if (!a) continue;
			if (a.bIsMonster && a.health > 0) a.ClearCounters();
			else if (a.bIsMonster && a.bCountKill)
			{
				level.total_monsters--;
				level.killed_monsters--;
				if (mo.player && mo.player.killcount > 0 && !multiplayer) mo.player.killcount--;
			}
			a.Destroy();
		}
	}

	// --- the tic -------------------------------------------------------------------
	// ThirdTick, after the earlier selves are where they are (ThirdSelves), before the last hall's.
	void CommonTick(PlayerPawn mo)
	{
		if (!commonMark || paradox || !tgo) return;
		double t0 = MSTimeF();
		// this go's group: the first time the player stands on its level
		if (tgo <= parts && cmCome[tgo] < 0 && mo.health > 0 && CmAt(mo.pos.xy) == tgo)
		{
			cmCome[tgo] = ot;
			CommonCome(mo, tgo, false);
			FireFrom(mo);           // last.zs: what the player fires is followed from now
		}
		// an earlier group comes again at its tic, and what is left of it dies at its end
		for (int k = 1; k < tgo && k <= parts; k++)
		{
			if (cmCome[k] >= 0 && !cmAgain[k] && ot >= cmCome[k]) CommonCome(mo, k, true);
			if (cmAgain[k] && cmDone[k] >= 0 && ot >= cmDone[k]) CommonOver(k);
		}
		// this go's group is dead: its way on opens (CommonWays)
		if (tgo <= parts && cmCome[tgo] >= 0 && cmDone[tgo] < 0 && !CommonLives(tgo))
		{
			cmDone[tgo] = ot;
			if (CommonHas(tgo)) LastSay("Nothing of them lives: your way on from the yard is open.");
		}
		for (int i = cmMissile.Size() - 1; i >= 0; i--) if (!cmMissile[i]) { cmMissile.Delete(i); cmMissileOf.Delete(i); }
		if (!lastMark) { LastRecordFire(mo); LastSelvesFight(); }       // (with a last hall, LastTick does both)
		commonMs = MSTimeF() - t0;
	}

	bool CommonHas(int k)
	{
		for (int i = 0; i < comers.Size(); i++) if (comers[i].args[1] == k) return true;
		return false;
	}

	// Group k comes (again: in a later go, at self k's tic): each of its monsters in a teleport fog, awake,
	// its first target the nearest it sees of the player and the earlier selves in the place.
	void CommonCome(PlayerPawn mo, int k, bool again)
	{
		cmAgain[k] = 1;
		int n = 0;
		for (int i = 0; i < comers.Size(); i++)
		{
			AjarThirdComer c = comers[i];
			if (c.args[1] != k) continue;
			if (comerBody[i]) { comerBody[i].Destroy(); comerBody[i] = null; }
			class<Actor> cls = AjarHandler.AmbushClass(c.args[0]);
			if (!cls) continue;
			Actor m = Actor.Spawn(cls, c.pos, ALLOW_REPLACE);
			if (!m) continue;
			m.angle = c.angle;
			m.bAmbush = false;
			Actor.Spawn("TeleportFog", m.pos, ALLOW_REPLACE);
			Actor t = CommonFirstTarget(m, mo);
			if (t)
			{
				m.target = t;
				m.SetState(m.SeeState);
			}
			cmMon.Push(m); cmPart.Push(k); cmHitBy.Push(null); cmKill.Push(m.bCountKill); cmDied.Push(0);
			n++;
		}
		if (!n) return;
		mo.A_StartSound("brain/spit", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		if (!again) LastSay("They come for you over the yard.\nYour way on opens once every one of them is dead.");
		else LastSay(String.Format("Your %s self is in the yard: its fight there comes again.", Nth(k - 1)));
	}

	// A monster's first target: the nearest it sees of the player and the earlier selves in the place (the
	// player if it sees none).
	Actor CommonFirstTarget(Actor m, PlayerPawn mo)
	{
		Actor best = null;
		double bd = 1e12;
		if (mo.health > 0 && m.CheckSight(mo)) { best = mo; bd = m.Distance3D(mo); }
		for (int i = 0; i < ghosts.Size() && i < takes.Size() - 1; i++)
		{
			if (!CommonThere(i) || !m.CheckSight(ghosts[i])) continue;
			double d = m.Distance3D(ghosts[i]);
			if (d < bd) { bd = d; best = ghosts[i]; }
		}
		if (!best && mo.health > 0) best = mo;
		return best;
	}

	// Does anything of group k live? A pain elemental that is dying still does (its lost souls are to come;
	// it leaves no body, so it is gone when it is done), and its lost souls are of its group.
	bool CommonLives(int k)
	{
		for (int i = 0; i < cmMon.Size(); i++)
		{
			Actor a = cmMon[i];
			if (a && cmPart[i] == k && (a.health > 0 || a is "PainElemental")) return true;
		}
		return false;
	}

	// The end of an earlier go's fight here (the tic its group was all dead in its go): whatever of it still
	// lives dies, its death played (a pain elemental's 'Massacre' throws no lost souls; one thrown since
	// dies the tic after).
	void CommonOver(int k)
	{
		int n = 0;
		for (int i = 0; i < cmMon.Size(); i++)
		{
			Actor a = cmMon[i];
			if (!a || cmPart[i] != k || a.health <= 0) continue;
			a.DamageMobj(null, null, a.health, 'Massacre', DMG_FORCED | DMG_NO_ARMOR | DMG_THRUSTLESS);
			n++;
		}
		cmOverKilled[k] += n;
		if (cmOver[k]) return;
		cmOver[k] = 1;
		if (n) LastSay(String.Format("Your %s self's fight in the yard is over: what was left of it falls.", Nth(k - 1)));
	}

	// A lost soul is of the group of the pain elemental that threw it: it comes out at the elemental's
	// middle and is put a step away (A_PainShootSkull), so it is the group's elemental nearest it.
	override void WorldThingSpawned(WorldEvent e)
	{
		if (!commonMark || !e.Thing || !(e.Thing is "LostSoul") || cmMon.Find(e.Thing) < cmMon.Size()) return;
		int best = -1;
		double bd = 160;
		for (int i = 0; i < cmMon.Size(); i++)
		{
			Actor p = cmMon[i];
			if (!p || !(p is "PainElemental")) continue;
			double d = (e.Thing.pos.xy - p.pos.xy).Length();
			if (d < bd) { bd = d; best = i; }
		}
		if (best < 0) return;
		cmMon.Push(e.Thing); cmPart.Push(cmPart[best]); cmHitBy.Push(null); cmKill.Push(e.Thing.bCountKill); cmDied.Push(0);
	}

	// --- the ways on -----------------------------------------------------------------
	// (ThirdShutters) Part k's way: open in the goes before k; in go k shut until its group is dead; in a
	// later go as it was then. `now`: at once.
	void CommonWays(bool now)
	{
		if (!commonMark) return;
		for (int i = 0; i < cmWays.Size(); i++)
		{
			int k = cmWays[i].args[0];
			AjarShutter s = FindShutter(cmWays[i].args[1]);
			if (!s || k < 1 || k > parts) continue;
			bool want = tgo < k || (tgo == k && cmDone[k] >= 0) || (tgo > k && cmDone[k] >= 0 && ot >= cmDone[k]);
			HoldShutter(s, want, now);
		}
	}

	// --- the selves' shots, aimed again ----------------------------------------------
	// The nearest living monster of the place within AIM_AGAIN degrees (horizontally) of `ang` from `at`,
	// that `from` sees (none: null).
	Actor CommonAim(Actor from, Vector3 at, double ang)
	{
		Actor best = null;
		double bd = 1e12;
		let it = ThinkerIterator.Create("Actor", Thinker.STAT_DEFAULT);
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || !a.bShootable || a.player || a is "AjarGhost" || !InCommon(a.pos.xy)) continue;
			Vector2 d = a.pos.xy - at.xy;
			if (abs(Actor.DeltaAngle(ang, VectorAngle(d.x, d.y))) > AIM_AGAIN) continue;
			double l = (a.pos + (0, 0, a.height / 2) - at).Length();
			if (l >= bd || !from.CheckSight(a)) continue;
			bd = l;
			best = a;
		}
		return best;
	}

	// (LastFire) A self's hitscan in the place: turned to such a monster, its pitch to the monster's middle
	// (from where a monster's hitscan leaves it: 8 over its middle). False: none, as recorded.
	bool CommonAimHitscan(AjarGhost g, out double ang, out double pitch)
	{
		cmFiring = g;
		cmFireHit = false;
		Actor a = CommonAim(g, g.pos, g.angle);
		if (!a) return false;
		Vector2 d = a.pos.xy - g.pos.xy;
		ang = VectorAngle(d.x, d.y);
		double dz = a.pos.z + a.height / 2 - (g.pos.z + g.height / 2 + 8);
		pitch = -atan2(dz, max(1., d.Length()));
		return true;
	}

	// (LastFire, after a hitscan fired again in the place) the measure: did it hit a monster?
	void CommonFired(AjarGhost g)
	{
		int i = ghosts.Find(g);
		cmFiring = null;
		if (i >= ghosts.Size() || i >= cmShots.Size()) return;
		cmShots[i]++;
		if (cmFireHit) cmShotsHit[i]++;
	}

	// (LastFire) A self's missile in the place: sent at the same speed to such a monster near its way.
	void CommonAimMissile(AjarGhost g, Actor m)
	{
		Actor a = CommonAim(m, m.pos, VectorAngle(m.vel.x, m.vel.y));
		if (a) m.vel = (a.pos + (0, 0, a.height / 2) - m.pos).Unit() * m.vel.Length();
		int i = ghosts.Find(g);
		if (i >= ghosts.Size() || i >= cmShots.Size()) return;
		cmShots[i]++;
		cmMissile.Push(m); cmMissileOf.Push(i);
	}

	// Who hurt a group's monster (the last to hurt a dead one killed it), and the selves' hits.
	// (map32.zs's WorldThingDamaged calls it)
	void CommonDamaged(WorldEvent e)
	{
		if (!commonMark || !e.Thing) return;
		int i = cmMon.Find(e.Thing);
		if (i < cmMon.Size())
		{
			cmHitBy[i] = e.DamageSource;
			if (e.Thing.health <= 0) cmDied[i] = 1;
		}
		if (!e.Thing.bIsMonster || e.Thing.player || e.Thing is "AjarGhost") return;
		if (cmFiring && e.DamageSource == cmFiring) cmFireHit = true;
		if (!e.Inflictor) return;
		int s = cmMissile.Find(e.Inflictor);
		if (s < cmMissile.Size() && cmMissileOf[s] >= 0) { cmShotsHit[cmMissileOf[s]]++; cmMissileOf[s] = -1; }
	}

	// --- the timetable -------------------------------------------------------------
	// ThirdSchedule: when each earlier self is in the place.
	void CommonSchedule()
	{
		if (!commonMark) return;
		static const int colours[] = { Font.CR_YELLOW, Font.CR_GREEN, Font.CR_RED };
		for (int k = 1; k < tgo && k <= parts; k++)
		{
			if (cmCome[k] < 0 || cmLeave[k] < 0) continue;
			tLine.Push(String.Format("%d is in the yard  %s to %s", k, ThirdClock(cmCome[k]), ThirdClock(cmLeave[k])));
			tColor.Push(colours[min(k - 1, 2)]);
		}
	}
}
