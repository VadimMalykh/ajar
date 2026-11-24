// The tests of the last fight lab (map LAST, tools/map_last.py; last.zs and
// third.zs; PLAN.md, "The last fight lab"). MAP=LAST MODE=n tools/smoke.sh, n:
//  1  the whole thing: go 1 alone at the alarm, go 2 with the first self
//     firing again, go 3 with both, across the floor and out. God mode; the
//     player's shots are the script's (LineAttack, SpawnPlayerMissile) with
//     the ammunition they spend taken, so that the record sees them. In go 3
//     the player does not fire: what the two earlier selves kill is counted
//     (the log's "kills" lines). EXTRA="+set save_dir /out/saves" keeps the saves.
//  2  the stand's save: killed on stand 2 after the alarm in go 2, USE, the
//     save made at the stand is loaded (before the alarm), the go plays on
//     to its time door.
//  3  winding on before the alarm (go 2 and go 3) and refused after it; go
//     3 stays on its stand: too late, the paradox.
//  4  the views: mode 1 with views held for smoke_LAST_4.cfg's screenshots.
// Kills by script, where a check needs one, are said in the log.

extend class AjarTimeHandler
{
	// the scripted clock (ot of each go)
	const L_ALARM = 600;        // go 1 steps onto plate 1
	const L_OFF = 300;          // ... steps off it at the alarm + this,
	const L_ON = 400;           // ... and on again
	const L_LEAVE1 = 1800;      // go 1 leaves plate 1 at the alarm + this (mode 1, 3 and 4)
	const L_PLATE2 = 540;       // go 2 steps onto plate 2 (before the alarm)
	const L_HOLD2 = 300;        // go 2 does not fire until the alarm + this
	const L_LEAVE2 = 1700;      // go 2 leaves plate 2 at the alarm + this
	const L_CROSS = 1600;       // go 3 crosses from the alarm + this
	const L_DIE = 100;          // mode 2: killed on stand 2 at the alarm + this

	int ltGo, ltStep, ltMark, ltHold, ltDone, ltAlarm1, ltDied;
	double ltHoldA, ltHoldP;
	Vector2 ltHoldAt;
	int ltSumOff, ltSumOn, ltNoMove;
	Vector2 ltWas;
	bool ltTurned, ltAlarmChecked, ltDoorChecked, ltWound;
	Array<Actor> ltFirst;       // each guard's first target
	Array<int> ltCounted;       // guards whose death is counted (by index)
	// kills by kind (0 mancubus, 1 revenant, 2 cacodemon, 3 demon, 4 hell knight) and killer (0 the player, 1 self 1, 2 self 2, 3 other)
	int ltKills[60];             // [20 * (go - 1) + 4 * kind + killer]
	int ltExitBad, ltExitSeen;
	double ltMsSum, ltMsMax, ltTicSum, ltTicMax, ltLastMs;
	int ltMsN;
	double ltWall;

	static const double LROUTES[] = {
		/* 0: S, the supplies, C1, stand 1 */   610, 1380,  750, 1380,  750, 1420,  610, 1420,  900, 1160,  960, 1152,  1340, 1152,  1400, 1185,  1560, 1190,  -1, -1,
		/* 20: onto plate 1 */                 1600, 1088,  -1, -1,
		/* 24: off it */                       1680, 1088,  -1, -1,
		/* 28: through time door 1 */          1632, 1150,  1632, 1300,  -1, -1,
		/* 34: box 2, R2, C2, stand 2 */        700, 990,  700, 880,  620, 735,  740, 735,  740, 775,  620, 775,  784, 690,  784, 560,  870, 560,  880, 420,  -1, -1,
		/* 56: onto plate 2 */                  960, 512,  -1, -1,
		/* 60: through time door 2 */           870, 416,  760, 416,  -1, -1,
		/* 66: box 3, R3, C3, stand 3 */        480, 1240,  480, 1150,  430, 990,  540, 990,  540, 1024,  430, 1024,  480, 940,  480, -128,  1100, -128,  1200, -128,  1344, -60,  -1, -1,
		/* 90: across the floor, out */        1344, -20,  1344, 40,  1344, 130,  1344, 400,  1560, 420,  1600, 620,  1850, 650,  2040, 704,  2100, 704,  2230, 704,  -1, -1,
		/* 112: to stand 3's wind plate */      1500, -160,  -1, -1,
		/* 116: to stand 2's wind plate */      870, 420,  870, 670,  900, 672,  -1, -1,
		/* 124: from it onto plate 2 */          870, 670,  870, 512,  960, 512,  -1, -1
	};

	bool WalkL(PlayerPawn mo, int n)
	{
		if (wpRoute != n) { wpRoute = n; wpIx = 0; }
		int i = n + 2 * wpIx;
		if (LROUTES[i] < 0 && LROUTES[i + 1] < 0) { mo.vel.xy = (0, 0); return true; }
		if (Toward(mo, (LROUTES[i], LROUTES[i + 1]))) wpIx++;
		return false;
	}

	// --- what is in the hall -----------------------------------------------------------
	int LastLiving()
	{
		int n = 0;
		for (int i = 0; i < guardIs.Size(); i++) if (guardIs[i] && guardIs[i].health > 0) n++;
		return n;
	}

	// monsters, bodies, missiles, drops in the hall or on the stands, or guards anywhere
	int LastLoose()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.player || a is "AjarGhost") continue;
			let inv = Inventory(a);
			if (!(a.bIsMonster || a.bMissile || a.bCorpse || (inv && !inv.owner && inv.bDropped))) continue;
			if (a.bIsMonster || InLast(a.pos.xy)) n++;
		}
		return n;
	}

	static int KindOf(Actor a)
	{
		if (a is "Fatso") return 0;
		if (a is "Revenant") return 1;
		if (a is "Cacodemon") return 2;
		if (a is "Demon") return 3;
		return 4;
	}

	// Every guard dead since the last look: counted by its killer.
	void CountKills(PlayerPawn mo)
	{
		while (ltCounted.Size() < guardIs.Size()) ltCounted.Push(0);
		for (int i = 0; i < guardIs.Size(); i++)
		{
			Actor a = guardIs[i];
			if (!a || a.health > 0 || ltCounted[i]) continue;
			ltCounted[i] = 1;
			Actor by = guardHitBy[i];
			int k = 3;
			if (by == mo) k = 0;
			else for (int s = 0; s < ghosts.Size() && s < 2; s++) if (ghosts[s] && by == ghosts[s]) k = s + 1;
			ltKills[20 * (min(tgo, 3) - 1) + 4 * KindOf(a) + k]++;
		}
	}

	void PrintKills(int go)
	{
		static const string kinds[] = { "mancubus", "revenant", "cacodemon", "demon", "hell knight" };
		static const int many[] = { 2, 2, 2, 4, 2 };
		for (int k = 0; k < 5; k++)
			Console.Printf("AJARTEST info kills go=%d %s (of %d): the player %d, self 1 %d, self 2 %d, other %d", go, kinds[k], many[k],
				ltKills[20 * (go - 1) + 4 * k + 0], ltKills[20 * (go - 1) + 4 * k + 1], ltKills[20 * (go - 1) + 4 * k + 2], ltKills[20 * (go - 1) + 4 * k + 3]);
	}

	// --- the player's fire (the script's) ------------------------------------------
	Actor LastAim(PlayerPawn mo)
	{
		Actor best = null;
		double bd = 1e12;
		for (int i = 0; i < guardIs.Size(); i++)
		{
			Actor a = guardIs[i];
			if (!a || a.health <= 0 || !mo.CheckSight(a)) continue;
			double d = a.Distance3D(mo);
			if (d < bd) { bd = d; best = a; }
		}
		return best;
	}

	// at the nearest guard it sees: a bullet each 4 tics, a rocket each 35 at a big one
	void FireL(PlayerPawn mo, int o)
	{
		Actor a = LastAim(mo);
		if (!a) return;
		Face(mo, a);
		if (o % 4 == 0 && mo.CountInv("Clip") > 0)
		{
			mo.TakeInventory("Clip", 1);
			mo.LineAttack(mo.angle, 4096, mo.pitch, 5 * random[AjarGhost](1, 3), 'Hitscan', "BulletPuff");
			mo.A_StartSound("weapons/chngun", CHAN_WEAPON);
		}
		if (o % 35 == 17 && mo.CountInv("RocketAmmo") > 0 && !(a is "Demon") && a.Distance2D(mo) > 256)
		{
			mo.TakeInventory("RocketAmmo", 1);
			mo.SpawnPlayerMissile("Rocket");
		}
	}

	// --- a view held for a screenshot (the cfg shoots in its middle) -------------------
	void ShotL(PlayerPawn mo, string what, Vector2 at, double ang, double pitch)
	{
		Look(mo, at, ang, pitch);
		Console.Printf("AJARTEST info view %s t=%d ot=%d go=%d", what, thirdT, ot, tgo);
		ltHold = 120;
		ltHoldA = ang; ltHoldP = pitch; ltHoldAt = at;
	}

	// --- the dispatch ------------------------------------------------------------------
	void LastTests(PlayerPawn mo, int mode)
	{
		if (level.totaltime > level.maptime + 10)
		{
			if (ltDone < 2) { ltDone = 2; Console.Printf("AJARTEST info the level began again (out by the exit)"); }
			return;
		}
		int t = thirdT++;
		double now = MSTimeF();
		if (ltWall > 0 && tgo == 3 && alarmTic >= 0 && ot < alarmTic + L_LEAVE2)
		{
			double d = now - ltWall;
			ltTicSum += d; ltTicMax = max(ltTicMax, d);
			ltMsSum += lastMs; ltMsMax = max(ltMsMax, lastMs); ltMsN++;
		}
		ltWall = now;
		mo.player.cheats |= CF_GODMODE;
		if (paradox) mo.player.cheats &= ~CF_GODMODE;
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) go=%d ot=%d step=%d alarm=%d living=%d sum=%d td=%d exit=%d/%d p1=%d p2=%d selves=%d health=%d loads=%d kills=%d/%d",
				t, mo.pos.x, mo.pos.y, mo.pos.z, tgo, ot, ltStep, alarmTic, LastLiving(), plateSum, tdOpen, exitDoor && exitDoor.IsOpen(), exitUntil,
				plates.Size() > 0 && plates[0].pressed, plates.Size() > 1 && plates[1].pressed, Selves3(), mo.health, thirdLoads,
				level.killed_monsters, level.total_monsters);
		if (!paradox && tgo) CountKills(mo);
		if (ltHold > 0 && !paradox)
		{
			ltHold--;
			mo.vel = (0, 0, 0);
			if ((mo.pos.xy - ltHoldAt).Length() > 1) mo.SetOrigin((ltHoldAt, mo.pos.z), true);
			mo.angle = ltHoldA;
			mo.pitch = ltHoldP;
			if (!ltHold) mo.pitch = 0;
			return;
		}
		if (mode == 1 || mode == 4) Last1(mo, mode == 4);
		else if (mode == 2) Last2(mo, t);
		else if (mode == 3) Last3(mo, t);
	}

	bool NewGoL()
	{
		if (ltGo == tgo) return false;
		if (ltGo) PrintKills(ltGo);
		ltGo = tgo;
		ltStep = 0;
		ltSumOff = ltSumOn = -1;
		ltTurned = ltAlarmChecked = ltDoorChecked = false;
		ltFirst.Clear();
		ltCounted.Clear();
		NewRoute();
		return true;
	}

	// --- the checks of every go at the alarm ------------------------------------------
	void AlarmChecks(PlayerPawn mo)
	{
		int o = ot;
		if (alarmTic < 0)
		{
			// none before the plate
			if (o == 2 || o % 100 == 50) Check(String.Format("hallEmptyBefore%d", tgo), LastLoose() == 0 && LastLiving() == 0);
			if (o == 2 && lastGate) Check(String.Format("gateShut%d", tgo), lastGate.IsShut());
			return;
		}
		if (!ltAlarmChecked && o == alarmTic + 1)
		{
			ltAlarmChecked = true;
			int awake = 0, aimed = 0;
			for (int i = 0; i < guardIs.Size(); i++)
			{
				Actor a = guardIs[i];
				ltFirst.Push(a ? a.target : null);
				if (!a || a.health <= 0) continue;
				if (!a.bAmbush && (a.target || a.InStateSequence(a.CurState, a.SeeState))) awake++;
				if (a.target) aimed++;
			}
			string who = "";
			for (int i = 0; i < guardIs.Size(); i++)
				if (guardIs[i] && guardIs[i].target) who = who .. (guardIs[i].target.player ? "P" : guardIs[i].target is "AjarGhost" ? "S" : "?");
			Console.Printf("AJARTEST info alarm go=%d at %d (from the record %d): guards %d, awake %d, with a target %d (%s)", tgo, alarmTic, alarmAt,
				LastLiving(), awake, aimed, who);
			Check(String.Format("alarmGuards%d", tgo), LastLiving() == guards.Size() && guards.Size() == 12 && awake == 12 && aimed == 12);
			if (tgo == 1) ltAlarm1 = alarmTic;
			else Check(String.Format("alarmAtFirstSelf%d", tgo), alarmTic == alarmAt && alarmTic == ltAlarm1 && SelfAsRecord(0) && plates[0].pressed);
		}
		if (o == alarmTic + 20 && lastGate) Check(String.Format("gateOpen%d", tgo), lastGate.IsOpen());
		// a monster turns on an earlier self that shot it
		for (int i = 0; i < guardIs.Size() && i < ltFirst.Size() && !ltTurned; i++)
		{
			Actor a = guardIs[i];
			if (a && a.health > 0 && a.target is "AjarGhost" && ltFirst[i] != a.target && guardSelfDmg[i] > 0) ltTurned = true;
		}
	}

	// --- mode 1 (and 4: with views) ------------------------------------------------------
	void Last1(PlayerPawn mo, bool views)
	{
		NewGoL();
		AlarmChecks(mo);
		if (tgo == 1) Go1L(mo, views, L_LEAVE1);
		else if (tgo == 2) Go2L(mo, views, true);
		else if (tgo == 3) Go3L(mo, views, false);
	}

	// stays at p (a hit pushes the player: back to it)
	void StayAt(PlayerPawn mo, Vector2 p)
	{
		if ((mo.pos.xy - p).Length() > 2) Toward(mo, p);
		else mo.vel.xy = (0, 0);
	}

	// Do shots pass stand 1's railing both ways? Before the alarm, an imp (frozen, 1 health) on
	// the floor far out: a hitscan trace each way, a rocket each way. Then it is taken away.
	Actor ltZ, ltRIn, ltROut;
	bool ltInHit;
	void RailTest(PlayerPawn mo, int s)
	{
		if (s == 0)
		{
			Look(mo, (1560, 1060), 270);
			ltZ = Actor.Spawn("DoomImp", (1560, 150, -96));       // (straight south: clear of the blocks and pedestals)
			ltZ.tics = -1;
			ltZ.angle = 90;
			ltZ.health = 1;
			return;
		}
		if (!ltZ) return;
		if (s == 1)
		{
			FLineTraceData d;
			Face(mo, ltZ);
			mo.LineTrace(mo.angle, 4096, mo.pitch, 0, mo.player.viewheight, data: d);
			bool outHit = d.HitType == TRACE_HitActor && d.HitActor == ltZ;
			Vector2 v = mo.pos.xy - ltZ.pos.xy;
			double pitch = -atan2(mo.pos.z + 41 - (ltZ.pos.z + 32), v.Length());
			ltZ.LineTrace(VectorAngle(v.x, v.y), 4096, pitch, 0, 32, data: d);
			bool inHit = d.HitType == TRACE_HitActor && d.HitActor == mo;
			Console.Printf("AJARTEST info the railing, hitscans: out %d, in %d", outHit, inHit);
			Check("hitscansPassRailing", outHit && inHit);
			ltRIn = ltZ.SpawnMissile(mo, "Rocket");
			ltROut = mo.SpawnPlayerMissile("Rocket");
			ltInHit = false;
			return;
		}
		if (ltRIn && !ltRIn.bMissile && !ltInHit)
		{
			ltInHit = (ltRIn.pos.xy - mo.pos.xy).Length() < 64;
			Console.Printf("AJARTEST info the railing: the rocket from the floor burst %d from the player", (ltRIn.pos.xy - mo.pos.xy).Length());
			ltRIn = null;
		}
		if (s == 45)
		{
			Console.Printf("AJARTEST info the railing: the imp's health after the player's rocket %d", ltZ.health);
			Check("missilesPassRailing", ltInHit && ltZ.health <= 0);
			if (ltZ.health > 0) ltZ.ClearCounters();
			else { level.killed_monsters--; level.total_monsters--; if (mo.player.killcount > 0) mo.player.killcount--; }
			ltZ.Destroy();
			Look(mo, (1560, 1190), 270);
		}
	}

	void Go1L(PlayerPawn mo, bool views, int leave, bool wind = false)
	{
		int o = ot;
		if (ltStep == 0 && WalkL(mo, 0)) { ltStep = 1; ltMark = o; }
		if (ltStep == 1)
		{
			if (o == ltMark + 2) Check("standSaveOne", standSaved);
			if (o >= 300 && o <= 345) { RailTest(mo, o - 300); return; }
			if (views && o == 400) { ShotL(mo, "stand 1 before the alarm (go 1)", (1560, 1150), 250, 12); return; }
			if (o >= L_ALARM - 40 && WalkL(mo, 20)) { ltStep = 2; }
		}
		if (ltStep == 2)
		{
			if (alarmTic < 0) return;
			int a = o - alarmTic;
			// on, off at L_OFF, on again at L_ON: the sum counts only on the plate and does not fall
			if (a > L_OFF && a < L_ON) StayAt(mo, (1680, 1088));
			else StayAt(mo, (1600, 1088));
			FireL(mo, o);
			if (a == L_OFF + 10) ltSumOff = plateSum;
			if (a == L_ON - 1) Check("sumOnlyOnPlate", ltSumOff > 0 && plateSum == ltSumOff && !plates[0].mine && !tdOpen);
			if (a == L_ON + 60) Check("sumDoesNotFall", plateSum > ltSumOff && plateSum <= ltSumOff + 60);
			if (!ltDoorChecked && tdOpen)
			{
				ltDoorChecked = true;
				Console.Printf("AJARTEST info time door 1 open at %d (the alarm + %d): sum %d of %d", o, a, plateSum, LastNeed());
				Check("doorOneAtSum", plateSum == LastNeed() && a >= LastNeed() + (L_ON - L_OFF) - 10);
			}
			if (!tdOpen && plateSum == LastNeed() - 1) Check("doorOneShutBefore", !tdOpen);
			if (views && a == 600) { ShotL(mo, "stand 1 in the fight (go 1)", mo.pos.xy, 270, 14); return; }
			if (a == leave)
			{
				AjarTake t = takes[0];
				int bullets = 0, missiles = 0, early = 0;
				for (int e = 0; e < t.evTic.Size(); e++) { if (t.evKind[e] == 1) bullets++; if (t.evKind[e] == 0) missiles++; if (t.evTic[e] <= alarmTic) early++; }
				Console.Printf("AJARTEST info go 1 fired: %d bullets, %d missiles, %d before the alarm", bullets, missiles, early);
				Check("shotsInTake", bullets > 50 && missiles > 0 && !early);
				ltStep = 3;
				NewRoute();
				mo.pitch = 0;
			}
		}
		if (ltStep == 3) WalkL(mo, 28);
	}

	// go 2: `checks` the first self's fire (mode 1)
	int ltDoorAt;
	void Go2L(PlayerPawn mo, bool views, bool checks, bool wind = false, bool die = false, bool quick = false)
	{
		int o = ot;
		if (o == 1)
		{
			Check("hallEmptyAgain", LastLoose() == 0 && LastLiving() == 0 && (!lastGate || lastGate.IsShut()) && takes.Size() == 2);
			Console.Printf("AJARTEST info go 2 begins: monsters %d killed %d, the player's kills %d", level.total_monsters, level.killed_monsters, mo.player.killcount);
			Check("countersRight", level.total_monsters == 0 && level.killed_monsters == 0 && mo.player.killcount == 0);
		}
		if (ltStep == 0 && WalkL(mo, 34)) { ltStep = 1; ltMark = o; }
		if (ltStep == 1)
		{
			if (o == ltMark + 2) Check("standSaveTwo", standSaved && alarmTic < 0);
			if (wind && !ltWound && o == ltMark + 3) { ltStep = 10; NewRoute(); return; }
			if (views && o == 400) { ShotL(mo, "stand 2 before the alarm (go 2)", (880, 450), 10, 14); return; }
			if (o >= L_PLATE2 && WalkL(mo, 56)) ltStep = 2;
		}
		// mode 3: wind on, before the alarm
		if (ltStep == 10)
		{
			if (!WalkL(mo, 116)) return;
			AjarThirdWind wp = null;
			let it = ThinkerIterator.Create("AjarThirdWind");
			AjarThirdWind q;
			while (q = AjarThirdWind(it.Next())) if (q.pos.y > 0) wp = q;
			int from = ot;
			Look(mo, mo.pos.xy, 90);
			TestWind(mo, wp);
			ltWound = true;
			Console.Printf("AJARTEST info go 2 wound from %d to %d (the alarm at %d)", from, ot + 1, alarmAt);
			Check("windBeforeAlarmTwo", ot + 1 == alarmAt - WIND_LEAD && alarmTic < 0 && LastLiving() == 0);
			ltStep = 11;
			NewRoute();
			return;
		}
		if (ltStep == 11 && WalkL(mo, 124)) ltStep = 2;
		if (ltStep == 2)
		{
			if (alarmTic < 0) return;
			int a = o - alarmTic;
			int off = L_OFF, on = L_ON;
			if (checks)
			{
				if (a == off) Check("sumWhilePlateOneOn", plateSum >= off - 2 && plates[1].mine);
				if (a == off + 10) ltSumOff = plateSum;
				if (a == on - 1) Check("sumOnlyWithPlateOne", plateSum == ltSumOff && plates[1].mine && !plates[0].pressed);
				if (a == L_HOLD2)
				{
					// the player has not fired: what the first self did
					int dmg = 0;
					for (int i = 0; i < guardSelfDmg.Size(); i++) dmg += guardSelfDmg[i];
					let g = AjarLastSelf(ghosts[0]);
					Console.Printf("AJARTEST info go 2, %d tics after the alarm: the first self did %d damage, was hit %d times, its health %d; it fired %d of %d",
						a, dmg, g ? g.hits : -1, g ? g.health : -1, takes[0].next, takes[0].evTic.Size());
					Check("selfFiresAgain", dmg > 0 && takes[0].next > 0);
					Check("turnsOnSelf", ltTurned);
					Check("selfHitUnharmed", g && g.hits > 0 && g.health == g.SpawnHealth() && g.bShootable);
				}
			}
			if (die && a == L_DIE && !ltDied)
			{
				ltDied = thirdT;
				mo.player.cheats &= ~CF_GODMODE;
				mo.DamageMobj(null, null, 10000, 'None', DMG_FORCED);
				Check("killedOnStandTwo", mo.health <= 0 && SecTagged(mo.pos.xy, StandTag(2)));
				return;
			}
			if (die && ltDied) return;
			if (wind && a == 10)
			{
				AjarThirdWind wp = null;
				let it = ThinkerIterator.Create("AjarThirdWind");
				AjarThirdWind q;
				while (q = AjarThirdWind(it.Next())) if (q.pos.y > 0) wp = q;
				int was = ot, len = takes[takes.Size() - 1].x.Size();
				TestWind(mo, wp);
				Check("windRefusedTwo", ot == was && takes[takes.Size() - 1].x.Size() == len && alarmTic >= 0);
			}
			StayAt(mo, (960, 512));
			if (a >= L_HOLD2) FireL(mo, o);
			if (!ltDoorChecked && tdOpen)
			{
				ltDoorChecked = true;
				ltDoorAt = o;
				Console.Printf("AJARTEST info time door 2 open at %d (the alarm + %d): sum %d of %d", o, a, plateSum, LastNeed());
				Check("doorTwoAtSum", plateSum == LastNeed() && (!checks || a >= LastNeed() + (on - off) - 10));
			}
			if (!tdOpen && plateSum == LastNeed() - 1) Check("doorTwoShutBefore", !tdOpen);
			if (views && a == 700) { ShotL(mo, "stand 2 in the fight (go 2)", mo.pos.xy, 0, 12); return; }
			if (tdOpen && (a == L_LEAVE2 || (quick && o == ltDoorAt + 50))) { ltStep = 3; NewRoute(); mo.pitch = 0; }
		}
		if (ltStep == 3) WalkL(mo, 60);
	}

	// go 3: `late` stays on stand 3
	void Go3L(PlayerPawn mo, bool views, bool late, bool wind = false)
	{
		int o = ot;
		if (o == 1) Check("hallEmptyThree", LastLoose() == 0 && LastLiving() == 0 && takes.Size() == 3 && level.total_monsters == 0);
		if (o == 2)
		{
			for (int i = 0; i < tLine.Size(); i++) Console.Printf("AJARTEST info timetable: %s", tLine[i]);
			Check("timetableLines", tLine.Size() == 3);
		}
		// the exit door as the timetable has it (sampled; not within 15 tics of a change)
		if (o % 35 == 3 && exitDoor)
		{
			bool want = false, near = false;
			for (int s = 0; s < heldFrom.Size(); s++)
			{
				int a = heldFrom[s] + 1, b = heldTo[s] + openTics;
				if (o >= a && o < b) want = true;
				if (abs(o - a) < 15 || abs(o - b) < 15) near = true;
			}
			if (!near)
			{
				ltExitSeen++;
				if (want != exitDoor.IsOpen() || !want != exitDoor.IsShut()) { ltExitBad++; Console.Printf("AJARTEST info exit door at %d: wanted %d, open %d", o, want, exitDoor.IsOpen()); }
			}
		}
		if (alarmTic >= 0 && o == alarmTic + 600)
		{
			Console.Printf("AJARTEST info go 3 at the alarm + 600: self 1 fired %d of %d, self 2 %d of %d", takes[0].next, takes[0].evTic.Size(), takes[1].next, takes[1].evTic.Size());
			Check("twoSelvesFiring", takes[0].next > 0 && takes[1].next > 0 && Selves3() == 2);
		}
		if (alarmTic < 0 && o == alarmAt - 1 && lastGate) Check("gateShutBeforeAlarm", lastGate.IsShut());
		if (ltStep == 0 && WalkL(mo, 66)) { ltStep = 1; ltMark = o; }
		if (ltStep == 1)
		{
			if (o == ltMark + 2) Check("standSaveThree", standSaved);
			if (wind && !ltWound && o == ltMark + 3) { ltStep = 10; NewRoute(); return; }
			if (views && o == 400) { ShotL(mo, "stand 3 before the alarm (go 3)", (1344, -60), 60, 14); return; }
			if (alarmTic >= 0 && views && o == alarmTic + 600) { ShotL(mo, "stand 3 in the fight (go 3)", (1344, -60), 70, 10); return; }
			if (wind && alarmTic >= 0 && o == alarmTic + 10 && !ltDoorChecked)
			{
				ltDoorChecked = true;
				AjarThirdWind wp = null;
				let it = ThinkerIterator.Create("AjarThirdWind");
				AjarThirdWind q;
				while (q = AjarThirdWind(it.Next())) if (q.pos.y < 0) wp = q;
				int was = ot, len = takes[takes.Size() - 1].x.Size();
				TestWind(mo, wp);
				Check("windRefusedThree", ot == was && takes[takes.Size() - 1].x.Size() == len);
			}
			if (late) return;
			if (alarmTic >= 0 && o >= alarmTic + L_CROSS && exitDoor.IsOpen()) { ltStep = 2; NewRoute(); ltWas = mo.pos.xy; ltNoMove = 0; }
		}
		if (ltStep == 10)
		{
			if (!WalkL(mo, 112)) return;
			AjarThirdWind wp = null;
			let it = ThinkerIterator.Create("AjarThirdWind");
			AjarThirdWind q;
			while (q = AjarThirdWind(it.Next())) if (q.pos.y < 0) wp = q;
			int next = -1;
			for (int s = 0; s < plFrom.Size(); s++) if (plFrom[s] - WIND_LEAD > ot + 1 && (next < 0 || plFrom[s] < next)) next = plFrom[s];
			int from = ot;
			Look(mo, mo.pos.xy, 0);
			TestWind(mo, wp);
			ltWound = true;
			Console.Printf("AJARTEST info go 3 wound from %d to %d (the next step %d, the alarm at %d)", from, ot + 1, next, alarmAt);
			Check("windBeforeAlarmThree", next >= 0 && ot + 1 == next - WIND_LEAD && ot + 1 < alarmAt && alarmTic < 0);
			ltStep = 1;
			NewRoute();
			mo.SetOrigin((1344, -60, mo.pos.z), true);
			return;
		}
		if (ltStep == 2)
		{
			if (views && ltHold == 0 && !ltWound && SecTagged(mo.pos.xy, lastMark.args[0]) && mo.pos.x > 1550)
			{
				ltWound = true;     // (here: the crossing's view is taken)
				ShotL(mo, "the crossing (go 3)", mo.pos.xy, 30, 4);
				return;
			}
			// something stands in the way: it is killed by script (said)
			if ((mo.pos.xy - ltWas).Length() < 1) ltNoMove++; else ltNoMove = 0;
			ltWas = mo.pos.xy;
			if (ltNoMove > 15)
			{
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(it.Next()))
					if (a.bIsMonster && a.health > 0 && a.Distance2D(mo) < 96)
					{
						Console.Printf("AJARTEST info a %s stood in the way at (%d,%d): killed by script", a.GetClassName(), a.pos.x, a.pos.y);
						a.DamageMobj(null, null, 10000, 'None');
					}
				ltNoMove = 0;
			}
			if (WalkL(mo, 90)) ltStep = 3;
		}
		if (ltStep >= 2 && Through(mo) && ltDone < 1)
		{
			ltDone = 1;
			Console.Printf("AJARTEST info through the exit door at %d (the exit door open until %d)", o, exitUntil);
			Check("throughTheExitDoor", tgo == 3 && !paradox);
			Console.Printf("AJARTEST info the exit door: %d samples, %d not as the timetable", ltExitSeen, ltExitBad);
			Check("exitAsTimetable", ltExitSeen > 20 && !ltExitBad);
			if (ltMsN)
				Console.Printf("AJARTEST info the fight's tics in go 3 (two selves firing): %d tics, last.zs %.3f ms mean, %.2f worst; wall clock between tics %.1f ms mean, %.1f worst",
					ltMsN, ltMsSum / ltMsN, ltMsMax, ltTicSum / ltMsN, ltTicMax);
			PrintKills(3);
		}
	}

	// --- mode 2: the stand's save ---------------------------------------------------------
	void Last2(PlayerPawn mo, int t)
	{
		if (thirdLoads)
		{
			// loaded: the save made at stand 2 (the alarm not yet rung in it)
			if (ltDied >= 0)
			{
				ltDied = -1;
				Console.Printf("AJARTEST info loaded: go=%d ot=%d alarm=%d len1=%d", tgo, ot, alarmTic, takes[0].x.Size());
				Check("loadedStandSave", tgo == 2 && alarmTic < 0 && ot < alarmAt && SecTagged(mo.pos.xy, StandTag(2)) && mo.health > 0
					&& LastLiving() == 0 && LastLoose() == 0 && standSaved && takes.Size() == 2);
				ltStep = 1;
				NewRoute();
			}
			if (tgo == 2) { AlarmChecks(mo); Go2L(mo, false, false, quick: true); }
			if (tgo == 3 && ltGo != 3)
			{
				ltGo = 3;
				Check("goThreeAfterLoad", tdOpen == false && takes.Size() == 3 && takes[1].x.Size() > alarmAt);
			}
			return;
		}
		NewGoL();
		AlarmChecks(mo);
		if (tgo == 1) Go1L(mo, false, LastNeed() + 400);
		else if (tgo == 2) Go2L(mo, false, false, die: true);
		// (USE: smoke_LAST_2.cfg presses it, +use)
	}

	// --- mode 3: winding, and too late ---------------------------------------------------
	void Last3(PlayerPawn mo, int t)
	{
		if (paradox)
		{
			if (!ltDied)
			{
				ltDied = t;
				Check("lateInGoThree", tgo == 3 && paradoxCopy == 0 && paradoxWhy.IndexOf("shut for the last time") >= 0
					&& exitDoor.IsShut() && exitUntil <= ot && ot - 1 > heldLast && exitOpened && SecTagged(mo.pos.xy, StandTag(3)));
			}
			return;
		}
		if (NewGoL()) ltWound = false;
		AlarmChecks(mo);
		if (tgo == 1) Go1L(mo, false, L_LEAVE1);
		else if (tgo == 2) Go2L(mo, false, false, wind: true);
		else if (tgo == 3) Go3L(mo, false, true, wind: true);
	}
}
