// The tests of the yard lab (map YARD, tools/map_yard.py; common.zs, third.zs;
// PLAN.md, "The yard lab: a common place on three levels"). MAP=YARD MODE=n
// tools/smoke.sh, n:
//  1  the whole thing in three goes, the selves NOT meeting in the yard: go 1
//     comes onto its ledge late, go 2 onto the floor early, go 3 onto its
//     ledge in between; each group at its go's step, its way shut until it
//     is dead; the earlier groups again at their tics with their selves
//     firing, and dead at their ends; the place cleared and the counters right
//     at each go's start; the timetable; out by the exit.
//  2  the selves MEETING: go 3 comes onto its ledge while the first self
//     fights on its own across the yard; whom group 1 goes for; the aiming
//     again (a direct check in go 1: a replayed hitscan 10 degrees off a
//     monster hits it, 30 degrees off it does not turn; and how many of the
//     selves' replayed shots hit).
//  3  mode 2 with views held for smoke_YARD_3.cfg's screenshots.
// God mode; the player's shots are the script's (LineAttack, SpawnPlayerMissile)
// with the ammunition they spend taken, so that the record sees them as a
// real weapon's. EXTRA="+set save_dir /out/saves" keeps the saves.

// A monster that stands still and lasts (the aiming's direct check)
class AjarYardDummy : DoomImp
{
	Default { Health 1000; +NOPAIN }
}

extend class AjarTimeHandler
{
	// the scripted clock (ot of each go): mode 1, and modes 2 and 3
	const Y1_STEP = 2400;       // go 1 steps onto its ledge (mode 1: late)
	const Y1_LEAVE = 3700;      // go 1 leaves plate 1
	const Y2_LEAVE = 3600;      // go 2 leaves plate 2 (its time door open)
	const Y1_STEP_M = 1500;     // modes 2, 3: go 1 steps onto its ledge,
	const Y1_HOLD_M = 300;      // ... does not fire until its group's coming + this,
	const Y1_LEAVE_M = 3000;    // ... leaves plate 1
	const Y2_LEAVE_M = 2900;    // ... go 2 leaves plate 2
	const Y3_AFTER_M = 60;      // ... go 3 steps onto its ledge the first self's coming + this

	int ytGo, ytStep, ytHold, ytDone, ytMark;
	double ytHoldA, ytHoldP;
	Vector2 ytHoldAt;
	int ytNoGroupBad, ytNoGroupSeen, ytWayBad, ytWaySeen, ytTgtP, ytTgtS, ytMet;
	bool ytCame, ytDoneSeen, ytAgain1, ytAgain2, ytOver1, ytOver2, ytAimed, ytTopped;
	int ytFiredAt[3];           // a self's fired count at its group's coming in this go
	int ytWayBad2;              // the earlier parts' ways not as they were
	Array<int> ytCounted;       // cmMon's deaths counted (by index)
	// kills: [25 * (go - 1) + 5 * (part - 1) + killer], killer 0 the player, 1 self 1, 2 self 2, 3 at its end, 4 other
	int ytKills[75];
	double ytMsSum, ytMsMax, ytTicSum, ytTicMax, ytWall;
	int ytMsN;

	static const double YROUTES[] = {
		/* 0: go 1: S, its supplies, C1, to the ledge's door */     630, 1380,  710, 1380,  710, 1420,  630, 1420,  900, 1440,  2224, 1440,  2224, 1380,  -1, -1,
		/* 16: onto the ledge */                                    2224, 1300,  2100, 1280,  -1, -1,
		/* 22: way 1, E1, plate 1 */                                2240, 1280,  2400, 1280,  2688, 1280,  -1, -1,
		/* 30: through time door 1 */                               2760, 1280,  2900, 1280,  -1, -1,
		/* 36: go 2: box 2, R2's supplies, C2, down onto the floor */ 700, 990,  700, 880,  630, 735,  740, 735,  740, 775,  630, 775,  800, 736,  1270, 704,  1560, 704,  -1, -1,
		/* 56: way 2, up, E2, plate 2 */                            2200, 256,  2400, 256,  2768, 256,  -1, -1,
		/* 64: through time door 2 */                               2850, 256,  2960, 256,  -1, -1,
		/* 70: go 3: box 3, R3's supplies, C3, to the stairs */     480, 1240,  480, 1150,  430, 990,  540, 990,  540, 1028,  430, 1028,  480, 940,  480, -320,  2224, -320,  2224, -270,  -1, -1,
		/* 92: onto the ledge */                                    2224, -100,  2100, -64,  -1, -1,
		/* 98: way 3, E3 */                                         2240, -64,  2400, -64,  2650, -120,  -1, -1,
		/* 106: out by the exit */                                  2700, -240,  2900, -240,  3000, -240,  -1, -1
	};

	bool WalkY(PlayerPawn mo, int n)
	{
		if (wpRoute != n) { wpRoute = n; wpIx = 0; }
		int i = n + 2 * wpIx;
		if (YROUTES[i] < 0 && YROUTES[i + 1] < 0) { mo.vel.xy = (0, 0); return true; }
		if (Toward(mo, (YROUTES[i], YROUTES[i + 1]))) wpIx++;
		return false;
	}

	void StayY(PlayerPawn mo, Vector2 p)
	{
		if ((mo.pos.xy - p).Length() > 2) Toward(mo, p);
		else mo.vel.xy = (0, 0);
	}

	// --- what is in the yard ----------------------------------------------------------------
	int GroupLiving(int k)
	{
		int n = 0;
		for (int i = 0; i < cmMon.Size(); i++) if (cmMon[i] && cmMon[i].health > 0 && (!k || cmPart[i] == k)) n++;
		return n;
	}
	int GroupIn(int k)
	{
		int n = 0;
		for (int i = 0; i < cmMon.Size(); i++) if (cmMon[i] && cmPart[i] == k) n++;
		return n;
	}
	int ComersOf(int k)
	{
		int n = 0;
		for (int i = 0; i < comers.Size(); i++) if (comers[i].args[1] == k) n++;
		return n;
	}
	// monsters, bodies, missiles, drops in the yard, or the groups' anywhere
	int YardLoose()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.player || a is "AjarGhost") continue;
			let inv = Inventory(a);
			if (!(a.bIsMonster || a.bMissile || a.bCorpse || (inv && !inv.owner && inv.bDropped))) continue;
			if (InCommon(a.pos.xy) || cmMon.Find(a) < cmMon.Size()) n++;
		}
		return n;
	}
	int YardBodies()
	{
		int n = 0;
		let it = ThinkerIterator.Create("AjarFigure");
		Actor a;
		while (a = Actor(it.Next())) if (a.args[0] == 2) n++;
		return n;
	}
	AjarShutter WayOf(int k)
	{
		for (int i = 0; i < cmWays.Size(); i++) if (cmWays[i].args[0] == k) return FindShutter(cmWays[i].args[1]);
		return null;
	}
	bool HasLine(string s)
	{
		for (int i = 0; i < tLine.Size(); i++) if (tLine[i] == s) return true;
		return false;
	}
	string YardLine(int k) { return String.Format("%d is in the yard  %s to %s", k, ThirdClock(cmCome[k]), ThirdClock(cmLeave[k])); }
	string SaidY() { let h = Doors(); return h ? h.said : ""; }

	// the record's fire events in [from, to)
	static int EventsIn(AjarTake t, int from, int to)
	{
		int n = 0;
		for (int e = 0; e < t.evTic.Size(); e++) if (t.evTic[e] >= from && t.evTic[e] < to) n++;
		return n;
	}

	// Every group monster dead since the last look: counted by its killer.
	void CountKillsY(PlayerPawn mo)
	{
		while (ytCounted.Size() < cmMon.Size()) ytCounted.Push(0);
		for (int i = 0; i < cmMon.Size(); i++)
		{
			Actor a = cmMon[i];
			if (!a || a.health > 0 || ytCounted[i]) continue;
			ytCounted[i] = 1;
			int k = cmPart[i];
			Actor by = cmHitBy[i];
			int who = 4;
			if (by == mo) who = 0;
			else if (by && by is "AjarGhost") { for (int s = 0; s < ghosts.Size() && s < 2; s++) if (by == ghosts[s]) who = s + 1; }
			else if (k < tgo && cmDone[k] >= 0 && ot >= cmDone[k]) who = 3;
			if (k >= 1 && k <= 3) ytKills[25 * (min(tgo, 3) - 1) + 5 * (k - 1) + who]++;
		}
	}

	void PrintKillsY(int go)
	{
		for (int k = 1; k <= 3; k++)
		{
			int b = 25 * (go - 1) + 5 * (k - 1);
			int all = ytKills[b] + ytKills[b + 1] + ytKills[b + 2] + ytKills[b + 3] + ytKills[b + 4];
			if (all) Console.Printf("AJARTEST info kills go=%d group %d: the player %d, self 1 %d, self 2 %d, at its end %d, other %d", go, k,
				ytKills[b], ytKills[b + 1], ytKills[b + 2], ytKills[b + 3], ytKills[b + 4]);
		}
	}

	// --- the player's fire (the script's) ------------------------------------------
	Actor YardAim(PlayerPawn mo)
	{
		Actor best = null;
		double bd = 1e12;
		for (int i = 0; i < cmMon.Size(); i++)
		{
			Actor a = cmMon[i];
			if (!a || a.health <= 0 || !mo.CheckSight(a)) continue;
			double d = a.Distance3D(mo);
			if (d < bd) { bd = d; best = a; }
		}
		return best;
	}

	// at the nearest group monster it sees: a bullet each 4 tics, a rocket each 17 at one not close
	void FireY(PlayerPawn mo, int o)
	{
		if (o % 4 == 2 && (mo.CountInv("Clip") < 40 || mo.CountInv("RocketAmmo") < 5))
		{
			// (the script's own top-up, between shots: the record sees only what is spent)
			if (!ytTopped) Console.Printf("AJARTEST info go %d: the script tops up its ammunition at %d", tgo, o);
			ytTopped = true;
			mo.GiveInventory("Clip", 100);
			mo.GiveInventory("RocketAmmo", 10);
		}
		Actor a = YardAim(mo);
		if (!a) return;
		Face(mo, a);
		if (o % 4 == 0 && mo.CountInv("Clip") > 0)
		{
			mo.TakeInventory("Clip", 1);
			mo.LineAttack(mo.angle, 4096, mo.pitch, 5 * random[AjarGhost](1, 3), 'Hitscan', "BulletPuff");
			mo.A_StartSound("weapons/chngun", CHAN_WEAPON);
		}
		if (o % 17 == 9 && mo.CountInv("RocketAmmo") > 0 && a.Distance3D(mo) > 192 && !(a is "LostSoul"))
		{
			mo.TakeInventory("RocketAmmo", 1);
			mo.SpawnPlayerMissile("Rocket");
		}
	}

	// --- a view held for a screenshot (the cfg shoots in its middle) ---------------------
	void ShotY(PlayerPawn mo, string what, Vector2 at, double ang, double pitch)
	{
		Look(mo, at, ang, pitch);
		Console.Printf("AJARTEST info view %s t=%d ot=%d go=%d", what, thirdT, ot, tgo);
		ytHold = 120;
		ytHoldA = ang; ytHoldP = pitch; ytHoldAt = at;
	}

	// --- the dispatch ------------------------------------------------------------------
	void YardTests(PlayerPawn mo, int mode)
	{
		if (level.totaltime > level.maptime + 10)
		{
			if (ytDone < 2) { ytDone = 2; Console.Printf("AJARTEST info the level began again (out by the exit)"); }
			return;
		}
		int t = thirdT++;
		double now = MSTimeF();
		if (ytWall > 0 && tgo == 3 && !paradox)
		{
			double d = now - ytWall;
			ytTicSum += d; ytTicMax = max(ytTicMax, d);
			ytMsSum += commonMs; ytMsMax = max(ytMsMax, commonMs); ytMsN++;
		}
		ytWall = now;
		mo.player.cheats |= CF_GODMODE;
		if (paradox) { mo.player.cheats &= ~CF_GODMODE; return; }
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) go=%d ot=%d step=%d come=%d/%d/%d done=%d/%d/%d living=%d/%d/%d selves=%d td=%d exit=%d p1=%d p2=%d kills=%d/%d",
				t, mo.pos.x, mo.pos.y, mo.pos.z, tgo, ot, ytStep, cmCome[1], cmCome[2], cmCome[3], cmDone[1], cmDone[2], cmDone[3],
				GroupLiving(1), GroupLiving(2), GroupLiving(3), Selves3(), tdOpen, exitDoor && exitDoor.IsOpen(),
				plates.Size() > 0 && plates[0].pressed, plates.Size() > 1 && plates[1].pressed, level.killed_monsters, level.total_monsters);
		if (tgo) CountKillsY(mo);
		bool meet = mode >= 2;
		NewGoY(mo, meet);
		GoChecks(mo, meet);
		if (meet && tgo == 1 && ot >= 4 && !ytAimed) AimTest(mo);
		if (ytHold > 0)
		{
			ytHold--;
			mo.vel = (0, 0, 0);
			if ((mo.pos.xy - ytHoldAt).Length() > 1) mo.SetOrigin((ytHoldAt, mo.pos.z), true);
			mo.angle = ytHoldA;
			mo.pitch = ytHoldP;
			if (!ytHold) mo.pitch = 0;
			return;
		}
		bool views = mode == 3;
		if (tgo == 1) Go1Y(mo, meet, views);
		else if (tgo == 2) Go2Y(mo, meet, views);
		else if (tgo == 3) Go3Y(mo, meet, views);
	}

	void NewGoY(PlayerPawn mo, bool meet)
	{
		if (ytGo == tgo) return;
		if (ytGo) PrintKillsY(ytGo);
		ytGo = tgo;
		ytStep = 0;
		ytCame = ytDoneSeen = ytAgain1 = ytAgain2 = ytOver1 = ytOver2 = ytTopped = false;
		ytNoGroupBad = ytNoGroupSeen = ytWayBad = ytWaySeen = ytWayBad2 = 0;
		ytCounted.Clear();
		NewRoute();
	}

	// --- the checks of every go ---------------------------------------------------------
	void GoChecks(PlayerPawn mo, bool meet)
	{
		int o = ot;
		int k = tgo;
		// the go's start: the place as at the start, the counters right, the bodies, the ways, the timetable
		if (o == 2)
		{
			int bodies = YardBodies();
			Console.Printf("AJARTEST info go %d begins: loose in the yard %d, groups' monsters %d, bodies %d, monsters %d killed %d, the player's kills %d",
				k, YardLoose(), cmMon.Size(), bodies, level.total_monsters, level.killed_monsters, mo.player.killcount);
			Check(String.Format("yardAsAtStart%d", k), YardLoose() == 0 && !cmMon.Size() && cmCome[k] < 0 && cmDone[k] < 0);
			Check(String.Format("countersRight%d", k), level.total_monsters == 0 && level.killed_monsters == 0 && mo.player.killcount == 0);
			// the seen fallen: part 2's eight walkers lie on the floor in go 1, nothing from go 2 on
			Check(String.Format("bodies%d", k), bodies == (k < 2 ? 8 : 0));
			// the ways: open before their go, shut in it, in a later go shut until its group's end then
			bool ways = true;
			for (int w = 1; w <= 3; w++)
			{
				AjarShutter s = WayOf(w);
				bool want = w > k;
				if (!s || (want ? !s.IsOpen() : !s.IsShut())) ways = false;
			}
			Check(String.Format("waysAtStart%d", k), ways);
			for (int i = 0; i < tLine.Size(); i++) Console.Printf("AJARTEST info timetable go %d: %s", k, tLine[i]);
			bool tt = true;
			for (int j = 1; j < k; j++) tt = tt && cmLeave[j] > cmCome[j] && HasLine(YardLine(j));
			int want = k - 1;
			int has = 0;
			for (int i = 0; i < tLine.Size(); i++) if (tLine[i].IndexOf(" is in the yard ") >= 0) has++;
			Check(String.Format("timetable%d", k), tt && has == want);
		}
		if (o < 2) return;
		// before the player's step: nothing of this go's group (nothing of the earlier ones before their tics)
		if (cmCome[k] < 0)
		{
			ytNoGroupSeen++;
			if (GroupIn(k)) ytNoGroupBad++;
		}
		for (int j = 1; j < k; j++) if (o < cmCome[j] && GroupIn(j)) ytNoGroupBad++;
		// the player's step: the group comes
		if (!ytCame && cmCome[k] >= 0)
		{
			ytCame = true;
			int awake = 0, aimed = 0, onP = 0, onS = 0;
			for (int i = 0; i < cmMon.Size(); i++)
			{
				Actor a = cmMon[i];
				if (!a || cmPart[i] != k || a.health <= 0) continue;
				if (!a.bAmbush && (a.target || a.InStateSequence(a.CurState, a.SeeState))) awake++;
				if (a.target) aimed++;
				if (a.target == mo) onP++;
				else if (a.target is "AjarGhost") onS++;
			}
			bool selfThere = false;
			for (int i = 0; i < k - 1; i++) selfThere = selfThere || CommonThere(i);
			Console.Printf("AJARTEST info go %d: on level %d first at %d: group %d came, %d of %d, awake %d, with a target %d (the player %d, a self %d); before it %d tics looked at, %d bad; a self in the yard %d",
				k, k, o, k, GroupLiving(k), ComersOf(k), awake, aimed, onP, onS, ytNoGroupSeen, ytNoGroupBad, selfThere);
			Check(String.Format("comesAtStep%d", k), cmCome[k] == o && CmAt(mo.pos.xy) == k && GroupLiving(k) == ComersOf(k) && ComersOf(k) > 0
				&& awake == ComersOf(k) && aimed == ComersOf(k) && (selfThere || onP == ComersOf(k)) && ytNoGroupSeen > 100 && !ytNoGroupBad
				&& SaidY().IndexOf("They come for you") >= 0);
		}
		// this go's way: shut until its group is dead, then open for good
		AjarShutter way = WayOf(k);
		if (way && o > 2)
		{
			ytWaySeen++;
			if (cmDone[k] < 0 && (way.keyed || !way.IsShut())) ytWayBad++;
			if (cmDone[k] >= 0 && o >= cmDone[k] + 70 && !way.IsOpen()) ytWayBad++;
		}
		if (!ytDoneSeen && cmDone[k] >= 0)
		{
			ytDoneSeen = true;
			int all = 0, died = 0;
			for (int i = 0; i < cmMon.Size(); i++) if (cmPart[i] == k) { all++; if (cmDied[i]) died++; }
			Console.Printf("AJARTEST info go %d: group %d all dead at %d (came at %d: %d tics); members followed %d (lost souls %d), died %d; way %d shut until then: %d tics looked at, %d bad",
				k, k, o, cmCome[k], o - cmCome[k], all, all - ComersOf(k), died, k, ytWaySeen, ytWayBad);
			Check(String.Format("doneTic%d", k), cmDone[k] == o && !GroupLiving(k) && !CommonLives(k) && !ytWayBad && way && way.keyed == HELD_OPEN
				&& SaidY().IndexOf("your way on from the yard is open") >= 0);
			// what the player fired there is in the take (from the coming, while in the yard)
			AjarTake tk = takes[takes.Size() - 1];
			int bullets = 0, missiles = 0, early = 0, outside = 0;
			for (int e = 0; e < tk.evTic.Size(); e++)
			{
				if (tk.evKind[e] == 1) bullets++;
				if (tk.evKind[e] == 0) missiles++;
				if (tk.evTic[e] < cmCome[k]) early++;
				int j = tk.evTic[e];
				if (j < tk.x.Size() && CmAt((tk.x[j], tk.y[j])) < 0) outside++;
			}
			Console.Printf("AJARTEST info go %d fired in the yard: %d bullets, %d missiles; %d before the coming, %d out of the yard", k, bullets, missiles, early, outside);
			Check(String.Format("shotsInTake%d", k), bullets > 20 && missiles > 0 && !early && !outside);
		}
		if (way && cmDone[k] >= 0 && o == cmDone[k] + 70)
			Check(String.Format("wayOpen%d", k), way.IsOpen() && ytWayBad == 0);
		// the earlier groups, again
		for (int j = 1; j < k; j++) AgainChecks(mo, j, meet);
		// mode 2, go 3: the meeting
		if (meet && k == 3 && CommonThere(0) && CmAt(mo.pos.xy) == 3)
		{
			ytMet++;
			for (int i = 0; i < cmMon.Size(); i++)
			{
				Actor a = cmMon[i];
				if (!a || cmPart[i] != 1 || a.health <= 0) continue;
				if (a.target == mo) ytTgtP++;
				else if (a.target == ghosts[0]) ytTgtS++;
			}
		}
		if (!meet && k == 3 && cmCome[3] >= 0 && cmDone[3] < 0 && (CommonThere(0) || CommonThere(1))) ytMet++;
	}

	// Group j (an earlier part's) in this go: comes at its self's tic, its self shootable and firing
	// there, never harmed; what is left of it dies at its end; its way as it was.
	void AgainChecks(PlayerPawn mo, int j, bool meet)
	{
		int o = ot, k = tgo, i = j - 1;
		if (cmCome[j] < 0 || i >= ghosts.Size()) return;
		let g = AjarLastSelf(ghosts[i]);
		AjarTake t = takes[i];
		if (o == cmCome[j] - 1)
			Check(String.Format("selfNotYet%d_%d", k, j), g && !g.bShootable && !GroupIn(j) && !CommonThere(i));
		if (o == cmCome[j])
		{
			int aimed = 0, onS = 0;
			for (int m = 0; m < cmMon.Size(); m++)
			{
				Actor a = cmMon[m];
				if (!a || cmPart[m] != j || a.health <= 0) continue;
				if (a.target) aimed++;
				if (a.target == g) onS++;
			}
			Console.Printf("AJARTEST info go %d: group %d again at %d (its self's step): %d of %d, with a target %d (on the self %d); said: %s",
				k, j, o, GroupLiving(j), ComersOf(j), aimed, onS, SaidY());
			Check(String.Format("groupAgain%d_%d", k, j), cmAgain[j] && GroupLiving(j) == ComersOf(j) && aimed == ComersOf(j) && g && g.bShootable
				&& CommonThere(i) && SelfAsRecord(i) && CmAt(g.pos.xy) == j && SaidY().IndexOf("its fight there comes again") >= 0);
			ytFiredAt[i] = g ? g.fired : 0;
		}
		// the self's fight: its shots fired again (all of them: it is there from the group's tic to its leaving)
		if (o == cmDone[j] && g)
		{
			int want = EventsIn(t, cmCome[j], cmDone[j] + 1);
			Console.Printf("AJARTEST info go %d: self %d at its group's end (%d): fired %d of its record's %d shots since %d; aimed again %d, of them hit %d; was hit %d times, health %d; left alive %d",
				k, j, o, g.fired - ytFiredAt[i], want, cmCome[j], cmShots[i], cmShotsHit[i], g.hits, g.health, GroupLiving(j));
			Check(String.Format("selfFires%d_%d", k, j), g.fired - ytFiredAt[i] == want && want > 0 && cmShots[i] == want && g.health == g.SpawnHealth());
		}
		if (o == cmDone[j] + 1)
		{
			Console.Printf("AJARTEST info go %d: group %d's end at %d: %d died then; alive now %d; said: %s", k, j, cmDone[j], cmOverKilled[j], GroupLiving(j), SaidY());
			Check(String.Format("groupOver%d_%d", k, j), cmOver[j] && !GroupLiving(j));
		}
		// its way: shut until its end, then open
		AjarShutter way = WayOf(j);
		if (way && o > 2 && o < cmDone[j] && (way.keyed || !way.IsShut())) ytWayBad2++;
		if (way && o == cmDone[j] + 70) Check(String.Format("wayAsItWas%d_%d", k, j), way.IsOpen() && way.keyed == HELD_OPEN && !ytWayBad2);
		// the self leaves the yard: no longer there, no longer shootable
		if (o == cmLeave[j] + 1 && g)
			Check(String.Format("selfLeaves%d_%d", k, j), !g.bShootable && !CommonThere(i) && CmAt((t.x[o - 1], t.y[o - 1])) < 0);
	}

	// --- the aiming again: a direct check (mode 2, go 1, before any group) ----------------
	void AimTest(PlayerPawn mo)
	{
		ytAimed = true;
		Vector3 at = (1920, 1280, 0);
		let g = AjarGhost(Actor.Spawn("AjarGhost", at));
		let d = Actor.Spawn("AjarYardDummy", (1920, 980, -128));
		d.ClearCounters();
		d.tics = -1;
		d.angle = 90;
		let t = new("AjarThirdTake");
		t.x.Push(at.x);
		Fired(t, 1, null, at, (0, 0, 0));
		// 10 degrees off: turned to it, hit
		g.angle = 270 + 10;
		g.pitch = 0;
		Actor a10 = CommonAim(g, g.pos, g.angle);
		int hp = d.health;
		for (int n = 0; n < 5; n++) LastFire(g, t, 0, true);
		int hit10 = hp - d.health;
		// 30 degrees off: not turned, missed
		g.angle = 270 + 30;
		Actor a30 = CommonAim(g, g.pos, g.angle);
		hp = d.health;
		for (int n = 0; n < 5; n++) LastFire(g, t, 0, true);
		int hit30 = hp - d.health;
		Console.Printf("AJARTEST info the aiming again: 10 degrees off, turned to it %d, five shots took %d; 30 degrees off, turned %d, five shots took %d",
			a10 == d, hit10, a30 != null, hit30);
		Check("aimAgainTen", a10 == d && hit10 > 0);
		Check("aimAgainNotThirty", a30 == null && hit30 == 0);
		d.Destroy();
		g.Destroy();
	}

	// --- go 1: S, the north ledge (late in mode 1), plate 1 --------------------------------
	void Go1Y(PlayerPawn mo, bool meet, bool views)
	{
		int o = ot;
		int step = meet ? Y1_STEP_M : Y1_STEP, leave = meet ? Y1_LEAVE_M : Y1_LEAVE;
		if (ytStep == 0 && WalkY(mo, 0)) ytStep = 1;
		if (ytStep == 1)
		{
			if (views && o == step - 200) { ShotY(mo, "go 1 before its step: the bodies on the floor", (2224, 1372), 235, 22); return; }
			if (o >= step) { ytStep = 2; NewRoute(); }
			else return;
		}
		if (ytStep == 2)
		{
			if (!WalkY(mo, 16)) { if (cmCome[1] >= 0) FireY(mo, o); return; }
			ytStep = 3;
		}
		if (ytStep == 3)
		{
			StayY(mo, (2100, 1280));
			if (views && cmCome[1] >= 0 && o == cmCome[1] + 60) { ShotY(mo, "go 1 on the north ledge: its group over the yard", (2100, 1280), 235, 12); return; }
			if (!meet || o >= cmCome[1] + Y1_HOLD_M) FireY(mo, o);
			if (cmDone[1] >= 0 && o >= cmDone[1] + 40 && WayOf(1).IsOpen()) { ytStep = 4; NewRoute(); mo.pitch = 0; }
			return;
		}
		if (ytStep == 4)
		{
			if (WalkY(mo, 22) && o >= leave) { ytStep = 5; NewRoute(); }
			return;
		}
		if (ytStep == 5) WalkY(mo, 30);
	}

	// --- go 2: box 2, the floor (early), plate 2 -----------------------------------------
	void Go2Y(PlayerPawn mo, bool meet, bool views)
	{
		int o = ot;
		int leave = meet ? Y2_LEAVE_M : Y2_LEAVE;
		if (ytStep == 0)
		{
			if (!WalkY(mo, 36)) { if (cmCome[2] >= 0) FireY(mo, o); return; }
			ytStep = 1;
		}
		if (ytStep == 1)
		{
			StayY(mo, (1600, 704));
			if (views && cmCome[2] >= 0 && o == cmCome[2] + 60) { ShotY(mo, "go 2 on the floor: its group", (1600, 704), 10, -4); return; }
			FireY(mo, o);
			if (cmDone[2] >= 0 && o >= cmDone[2] + 40 && WayOf(2).IsOpen()) { ytStep = 2; NewRoute(); mo.pitch = 0; }
			return;
		}
		if (ytStep == 2)
		{
			if (WalkY(mo, 56) && tdOpen && o >= leave) { ytStep = 3; NewRoute(); }
			return;
		}
		if (ytStep == 3) WalkY(mo, 64);
	}

	// --- go 3: box 3, the south ledge (in between in mode 1; meeting the first self in mode 2), out ----
	void Go3Y(PlayerPawn mo, bool meet, bool views)
	{
		int o = ot;
		if (o == 3)
			Console.Printf("AJARTEST info go 3: self 1 in the yard %d to %d, self 2 %d to %d", cmCome[1], cmLeave[1], cmCome[2], cmLeave[2]);
		if (ytStep == 0)
		{
			// (mode 1: walk so as to come after the second self has left the yard; mode 2: wait at the stairs)
			if (!meet && o < cmLeave[2] - 380 && wpIx >= 6) { StayY(mo, (480, 940)); return; }
			if (WalkY(mo, 70)) ytStep = 1;
			return;
		}
		if (ytStep == 1)
		{
			if (meet && o < cmCome[1] + Y3_AFTER_M - 20) return;
			if (!WalkY(mo, 92)) { if (cmCome[3] >= 0) FireY(mo, o); return; }
			ytStep = 2;
		}
		if (ytStep == 2)
		{
			StayY(mo, (2100, -64));
			if (views && cmCome[3] >= 0 && o == cmCome[3] + 60)
			{
				ShotY(mo, "go 3 on the south ledge: a shared fight, the first self across the yard", (2100, -64), 100, -6);
				return;
			}
			FireY(mo, o);
			if (cmDone[3] >= 0 && o >= cmDone[3] + 40 && WayOf(3).IsOpen()) { ytStep = 3; NewRoute(); mo.pitch = 0; }
			return;
		}
		if (ytStep == 3)
		{
			if (!WalkY(mo, 98)) return;
			if (o % 35 == 0) Console.Printf("AJARTEST info go 3 waits in E3 for the exit door (%d)", o);
			if (exitDoor && exitDoor.IsOpen()) { ytStep = 4; NewRoute(); Report(meet); }
			return;
		}
		if (ytStep == 4) WalkY(mo, 106);
	}

	// Go 3, at the exit door: what the selves did, the meeting, the cost.
	void Report(bool meet)
	{
		PrintKillsY(3);
		Console.Printf("AJARTEST info go 3: the selves' shots aimed again in the yard: self 1 %d of %d hit, self 2 %d of %d", cmShotsHit[0], cmShots[0], cmShotsHit[1], cmShots[1]);
		Console.Printf("AJARTEST info go 3 cost: common.zs %.4f ms a tic on average, %.3f at worst (%d tics); the wall clock between tics %.1f ms on average, %.1f at worst",
			ytMsN ? ytMsSum / ytMsN : 0., ytMsMax, ytMsN, ytMsN ? ytTicSum / ytMsN : 0., ytTicMax);
		if (meet)
		{
			Console.Printf("AJARTEST info go 3: the player on its ledge while the first self is in the yard %d tics; group 1 on the player %d monster-tics, on the first self %d",
				ytMet, ytTgtP, ytTgtS);
			Check("selvesMeet", ytMet > 100 && ytTgtP > 0 && ytTgtS > 0);
			Check("aimedShotsHit", cmShotsHit[0] > 0 && cmShots[0] > 0);
		}
		else
		{
			Console.Printf("AJARTEST info go 3: group 3's fight with a self in the yard %d tics", ytMet);
			Check("selvesApart", !ytMet && cmCome[3] >= cmLeave[2] && cmDone[3] < cmCome[1]);
		}
	}
}
