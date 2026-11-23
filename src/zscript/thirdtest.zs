// The tests of the three goes lab (map THIRD, tools/map_third.py; third.zs;
// PLAN.md, "The three goes lab"). MAP=THIRD MODE=n tools/smoke.sh, n:
//  3  the whole solution: three goes, out by the exit door; the window
//     halls (W1 played to go 2, R to go 3: puppets where the monsters were,
//     the real ones unseen until the record's end); screenshots.
//  4  go 2 too slow in R: the paradox when the first self comes onto the
//     gantry; then USE: the engine loads the save of go 2's start.
//  5  go 2 not on plate 2 in time: the paradox.
//  6  go 3 too late at the exit door: the paradox.
//  7  winding on, in E2 (go 2) and in E3 (go 3); the pale stretch; out.
//  8  a long go: go 1 of 21000 tics, sampled to its end from go 2.
//  9  the save at the start of a go: killed in go 2, USE, the save loaded.
// Monsters stay in the map from mode 2 up (ajar.zs), so the modes start at 3.

extend class AjarTimeHandler
{
	int thirdT;                 // tics of the test (in this level)
	int t3Step;                 // where the script is, in the go that is on
	int t3Mark;                 // a tic of the go it noted
	int wpRoute, wpIx;          // the route being walked, and the next point of it
	int ttFightFrom;
	Actor ttAim;
	bool ttDone;
	int ttWindFrom, ttWindTo, ttWind2From, ttWind2To;
	// what a hall held at a tic of the go that recorded it: hall, tic, class, place, picture
	Array<int> snH, snT, snSf;
	Array<class<Actor> > snCls;
	Array<double> snX, snY, snZ;
	// carried across a level start: health and ammunition at time door 1 (checked at box 2)
	int ttHealth, ttClip, t3Rockets;

	// --- moving the scripted player -----------------------------------------------------
	bool Toward(PlayerPawn mo, Vector2 p, double speed = 8)
	{
		Vector2 d = p - mo.pos.xy;
		double l = d.Length();
		if (l < 1) { mo.vel.xy = (0, 0); return true; }
		mo.angle = VectorAngle(d.x, d.y);
		if (l <= speed) { mo.vel.xy = d; return true; }
		mo.vel.xy = d / l * speed;
		return false;
	}

	// The routes, as pairs of x, y; route n ends at the first -1.
	static const double ROUTES[] = {
		/* 0: S, the chaingun, to RED */            110, 525,  150, 520,  300, 720,  -1, -1,
		/* 8: into W1 */                            360, 608,  450, 608,  560, 608,  -1, -1,
		/* 16: to the frame */                      736, 780,  -1, -1,
		/* 20: to the gantry */                     900, 736,  1000, 736,  1300, 736,  -1, -1,
		/* 28: along it to E1, plate 1 */           1780, 736,  1860, 736,  1960, 700,  2048, 640,  -1, -1,
		/* 38: through time door 1 */               2140, 640,  2240, 640,  -1, -1,
		/* 44: box 2, C2, over the edge */          296, 352,  408, 304,  600, 296,  700, 296,  1000, 296,  1070, 296,  -1, -1,
		/* 58: R, the steel door, E2, plate 2 */    1700, 352,  1790, 352,  1900, 352,  2000, 352,  2112, 320,  -1, -1,
		/* 70: through time door 2 */               2150, 448,  2240, 448,  -1, -1,
		/* 76: box 3, south, the duct */            72, 352,  72, -96,  1000, -96,  1100, -64,  1400, -64,  -1, -1,
		/* 88: to E3, by the exit door */           1900, -64,  2050, -64,  2120, 64,  -1, -1,
		/* 96: through the exit door, out */        2250, 64,  2360, 64,  -1, -1,
		/* 102: round W1 (the long tgo) */           600, 450,  900, 450,  900, 760,  600, 760,  -1, -1
	};

	// Walks route n (its first index); true once at its end.
	bool Walk3(PlayerPawn mo, int n)
	{
		if (wpRoute != n) { wpRoute = n; wpIx = 0; }
		int i = n + 2 * wpIx;
		if (ROUTES[i] < 0 && ROUTES[i + 1] < 0) { mo.vel.xy = (0, 0); return true; }
		if (Toward(mo, (ROUTES[i], ROUTES[i + 1]))) wpIx++;
		return false;
	}

	void NewRoute() { wpRoute = -1; wpIx = 0; }

	// A test winds in the middle of a tic whose record is made: as if at the
	// start of the next one, as a USE in play is (the thinkers run after
	// WorldTick). The rest of this tic sees ot one short of where it went.
	void TestWind(PlayerPawn mo, AjarThirdWind wp, int to = -1)
	{
		ot++;
		if (to >= 0) ThirdWindTo(mo, to);
		else if (wp) wp.Used(mo);
		ot--;
	}

	void Look(PlayerPawn mo, Vector2 at, double ang, double pitch = 0)
	{
		mo.SetOrigin((at, mo.pos.z), true);
		mo.vel = (0, 0, 0);
		mo.angle = ang;
		mo.pitch = pitch;
	}

	void Face(PlayerPawn mo, Actor a)
	{
		Vector2 d = a.pos.xy - mo.pos.xy;
		mo.angle = VectorAngle(d.x, d.y);
		double dz = a.pos.z + a.height / 2 - (mo.pos.z + 41);
		mo.pitch = -atan2(dz, max(1., d.Length()));
	}

	// the nearest monster alive in hall h
	Actor LiveIn(PlayerPawn mo, int h)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a, best;
		double bd = 1e9;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || a.bInvisible || HallAt(a.pos.xy) != h) continue;
			double d = a.Distance2D(mo);
			if (d < bd) { bd = d; best = a; }
		}
		return best;
	}

	int Count3(string cls)
	{
		int n = 0;
		let it = ThinkerIterator.Create(cls);
		while (it.Next()) n++;
		return n;
	}

	// the real things of hall h that a window hall hides (monsters, bodies, what lies about), seen or not
	int HallThings(int h, bool seen)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (HallAt(a.pos.xy) != h || a.player || a is "AjarGhost" || a is "AjarEcho") continue;
			let inv = Inventory(a);
			if (!(a.bIsMonster || a.bCorpse || (inv && !inv.owner))) continue;
			if (a.bInvisible != seen) n++;
		}
		return n;
	}

	int HallPuppets(int h)
	{
		int n = 0;
		for (int i = 0; i < puppetTrack.Size(); i++) if (puppetTrack[i] == 100 + h && puppets[i]) n++;
		return n;
	}

	// Notes what hall h holds now (in the go that records it).
	void Snap3(int h)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		int n = 0;
		while (a = Actor(it.Next()))
		{
			if (HallAt(a.pos.xy) != h || !ThirdCounts(a)) continue;
			snH.Push(h); snT.Push(ot); snCls.Push(a.GetClass());
			snX.Push(a.pos.x); snY.Push(a.pos.y); snZ.Push(a.pos.z);
			snSf.Push((int(a.sprite) << 8) | (a.frame & 127));
			n++;
		}
		Console.Printf("AJARTEST info snap hall=%d tic=%d things=%d", h + 1, ot, n);
	}

	// In a later go at the same tic: is each of them a puppet, where it was and as it looked, and nothing more?
	bool SameAsSnap(int h)
	{
		int want = 0, found = 0;
		for (int s = 0; s < snT.Size(); s++)
		{
			if (snH[s] != h || snT[s] != ot) continue;
			want++;
			for (int i = 0; i < puppets.Size(); i++)
			{
				AjarEcho e = puppets[i];
				if (!e || puppetTrack[i] != 100 + h || slotCls[puppetSlot[i]] != snCls[s]) continue;
				if (abs(e.pos.x - snX[s]) > 0.01 || abs(e.pos.y - snY[s]) > 0.01 || abs(e.pos.z - snZ[s]) > 0.01) continue;
				if (((int(e.sprite) << 8) | (e.frame & 127)) != snSf[s]) continue;
				found++;
				break;
			}
		}
		int have = HallPuppets(h);
		Console.Printf("AJARTEST info hall %d at %d: noted %d, found %d, puppets %d", h + 1, ot, want, found, have);
		return want > 0 && found == want && have == want;
	}

	// The puppets of a played hall against its record, worked out afresh: each slot as its last record up to now says.
	bool PuppetsAsRecord(int h)
	{
		AjarTrack tr = hTrack[h];
		if (!tr) return false;
		int to = min(ot + 1, tr.first.Size());
		int b = to < tr.first.Size() ? tr.first[to] : tr.slot.Size();
		Array<int> last;
		for (int i = 0; i < slotCls.Size(); i++) last.Push(-1);
		for (int r = 0; r < b; r++) last[tr.slot[r]] = tr.sf[r] < 0 ? -1 : r;
		int want = 0, ok = 0;
		for (int s = 0; s < last.Size(); s++)
		{
			int r = last[s];
			if (r < 0) continue;
			want++;
			int k = puppetSlot.Find(s);
			if (k == puppetSlot.Size() || !puppets[k]) continue;
			AjarEcho e = puppets[k];
			if (e.pos.x == tr.x[r] && e.pos.y == tr.y[r] && e.pos.z == tr.z[r] && e.sprite == (tr.sf[r] >> 8) && e.frame == (tr.sf[r] & 127)) ok++;
		}
		Console.Printf("AJARTEST info hall %d as recorded at %d: %d of %d, puppets %d", h + 1, ot, ok, want, HallPuppets(h));
		return ok == want && HallPuppets(h) == want;
	}

	bool SelfAsRecord(int i)
	{
		if (i >= ghosts.Size() || !ghosts[i]) return false;
		AjarTake t = takes[i];
		AjarGhost g = ghosts[i];
		return ot < t.x.Size() && g.pos.x == t.x[ot] && g.pos.y == t.y[ot] && g.pos.z == t.z[ot] && g.sprite == (t.sf[ot] >> 8);
	}

	int Selves3()
	{
		int n = 0;
		for (int i = 0; i < ghosts.Size(); i++) if (ghosts[i]) n++;
		return n;
	}

	bool Shut3(int tag) { let s = FindShutter(tag); return s && s.IsShut(); }
	bool Open3(int tag) { let s = FindShutter(tag); return s && s.IsOpen(); }

	int PostsLiving()
	{
		int n = 0;
		for (int i = 0; i < postIs.Size(); i++) if (postIs[i] && postIs[i].bIsMonster && postIs[i].health > 0) n++;
		return n;
	}

	// A window hall in a later go, at a tic its own go noted what it held:
	// the same, as puppets, and its real things unseen (every mode, every go).
	void SnapChecks()
	{
		if (paradox || !tgo) return;
		for (int h = 0; h < halls.Size(); h++)
		{
			if (halls[h].args[1] >= tgo) continue;
			for (int s = 0; s < snT.Size(); s++)
				if (snH[s] == h && snT[s] == ot)
				{
					Check(h == HallIx(1) ? "w1AsItWas" : "rAsItWas", SameAsSnap(h));
					Check(h == HallIx(1) ? "w1RealUnseen" : "rRealUnseen", HallThings(h, true) == 0);
					break;
				}
		}
	}

	// --- the scripts -------------------------------------------------------------------
	// A view for a screenshot: held still 120 tics (the world goes on), its
	// tic printed; smoke_THIRD_3.cfg shoots in the middle of each.
	int ttHold;
	double ttHoldA, ttHoldP;
	void Shot3(PlayerPawn mo, string what)
	{
		Console.Printf("AJARTEST info view %s t=%d ot=%d go=%d", what, thirdT, ot, tgo);
		ttHold = 120;
		ttHoldA = mo.angle;
		ttHoldP = mo.pitch;
	}

	void ThirdTests(PlayerPawn mo)
	{
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (!mode || !(level.mapname ~== "THIRD")) return;
		SnapChecks();
		if (ttHold > 0 && !paradox)
		{
			ttHold--;
			thirdT++;
			mo.vel = (0, 0, 0);
			mo.angle = ttHoldA;
			mo.pitch = ttHoldP;
			if (!ttHold) mo.pitch = 0;
			return;
		}
		if (level.totaltime > level.maptime + 10)
		{
			// the exit ends the level and it begins again: the test is over
			if (!ttDone) { ttDone = true; Console.Printf("AJARTEST info the level began again (out by the exit)"); }
			return;
		}
		int t = thirdT++;
		mo.player.cheats |= CF_GODMODE;
		if (paradox) mo.player.cheats &= ~CF_GODMODE;
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) go=%d ot=%d step=%d selves=%d puppets=%d frozen=%d won=%d td=%d exit=%d/%d p1=%d p2=%d health=%d loads=%d",
				t, mo.pos.x, mo.pos.y, mo.pos.z, tgo, ot, t3Step, Selves3(), puppets.Size(), tfz.Size(), wonTic.Size() > 1 ? wonTic[1] : -9,
				tdOpen, exitDoor && exitDoor.IsOpen(), exitUntil, plates.Size() > 0 && plates[0].pressed, plates.Size() > 1 && plates[1].pressed,
				mo.health, thirdLoads);
		if (mode == 3) Third3(mo, t);
		else if (mode == 4) Third4(mo, t);
		else if (mode == 5) Third5(mo, t);
		else if (mode == 6) Third6(mo, t);
		else if (mode == 7) Third7(mo, t);
		else if (mode == 8) Third8(mo, t);
		else if (mode == 9) Third9(mo, t);
	}

	// A new go: the script's place in it begins again.
	int ttGo;
	bool NewGo3()
	{
		if (ttGo == tgo) return false;
		ttGo = tgo;
		t3Step = 0;
		NewRoute();
		return true;
	}

	// --- go 1, as in the solution (`shots`: screenshots; `longGo`: it lasts 21000 tics) ----
	void Go1(PlayerPawn mo, bool shots, bool longGo = false)
	{
		int o = ot;
		let h = Doors();
		AjarDoor red = Door32(1);
		AjarFrame f1 = h.FindFrame(101);
		int r = HallIx(2), w = HallIx(1);
		if (o == 2)
		{
			Check("goOneBegun", tgo == 1 && parts == 3 && plates.Size() == 2 && halls.Size() == 2 && posts.Size() == 4 && exitDoor && !Selves3());
			// the future seen: bodies at the posts that leave one, no monster alive in R, the shutters open
			int bodies = 0;
			for (int i = 0; i < postIs.Size(); i++) if (postIs[i] is "AjarFigure") bodies++;
			Check("bodiesInR", bodies == 3 && !HallLives(r) && Open3(3304) && Open3(3305) && Shut3(3306));
		}
		if (t3Step == 0 && Walk3(mo, 0)) { red.Used(mo); t3Step = 1; }
		if (t3Step == 1 && Walk3(mo, 8)) { t3Step = 2; ttFightFrom = o; }
		if (t3Step == 2)
		{
			// the fight in W1: the nearest at the chaingun, then whatever is left is killed
			Actor a = LiveIn(mo, w);
			// what W1 holds at four moments of the fight (the window hall's test, in go 2), before this tic's shot
			if ((o - ttFightFrom) % 90 == 30 && o - ttFightFrom < 400) Snap3(w);
			// (buttons set in WorldTick do not reach the player's think: the shots are the script's)
			if (a) { Face(mo, a); if (o % 4 == 0) { mo.LineAttack(mo.angle, 2048, mo.pitch, 12, 'Hitscan', "BulletPuff"); mo.A_StartSound("weapons/chngun", CHAN_WEAPON); } }
			if (o - ttFightFrom == 400)
			{
				let it = ThinkerIterator.Create("Actor");
				Actor m;
				while (m = Actor(it.Next())) if (m.bIsMonster && m.health > 0 && HallAt(m.pos.xy) == w) m.DamageMobj(mo, mo, 10000, 'None');
			}
			if (o - ttFightFrom == 440) { Check("w1Fought", !LiveIn(mo, w) && hTrack[w] && hTrack[w].slot.Size() > 100); t3Step = 3; mo.pitch = 0; }
		}
		if (t3Step == 3 && Walk3(mo, 16)) { f1.Activate(mo); t3Step = 4; }
		if (t3Step == 4)
		{
			if (o == t3Mark + 1) {}
			Check("redHung", red.frame == f1 && !h.carried);
			t3Step = longGo ? 20 : 5;
			t3Mark = o;
		}
		// the long go: round W1 until 20720
		if (t3Step == 20)
		{
			if (Walk3(mo, 102)) NewRoute();
			if (o >= 20720) { NewRoute(); t3Step = 5; }
		}
		if (t3Step == 5 && Walk3(mo, 20)) { t3Step = 6; t3Mark = o; }
		if (t3Step == 6)
		{
			// on the gantry: the bodies below
			if (o == t3Mark + 1) Look(mo, (1300, 736), 300, 28);
			if (o == t3Mark + 10)
			{
				Check("gantryOverBodies", SecTagged(mo.pos.xy, 3303) && mo.pos.z == 0 && !HallLives(r) && Count3("AjarFigure") == 3);
				t3Step = 61;
			}
		}
		// (mode 3 holds each view at a fixed tic of its go, so that the cfg's screenshots find them)
		if (t3Step == 61 && (!shots || o >= V_GANTRY))
		{
			if (shots) Shot3(mo, "gantry over the bodies (go 1)");
			else mo.pitch = 0;
			t3Step = 7;
		}
		if (t3Step == 7 && Walk3(mo, 28)) { t3Step = 8; t3Mark = o; }
		if (t3Step == 8)
		{
			if (o == t3Mark + 2) Check("plateOneOpensTimeDoorOne", plates[0].mine && tdOpen && !exitOpened);
			if (shots || ttFixed ? o == V_LEAVE1 : o == t3Mark + 100) { t3Step = 9; ttHealth = mo.health; ttClip = mo.CountInv("Clip"); t3Rockets = mo.CountInv("RocketAmmo"); }
		}
		if (t3Step == 9) Walk3(mo, 38);
	}

	// --- go 2: `slow` stays in box 2; `offPlate` keeps off plate 2; `wind` winds on in E2 ----
	void Go2(PlayerPawn mo, bool shots, bool slow = false, bool offPlate = false, bool wind = false)
	{
		int o = ot;
		int r = HallIx(2), w = HallIx(1);
		if (o == 0)
		{
			Check("boxTwo", tgo == 2 && BoxOf(mo) == 2 && takes.Size() == 2 && mo.health == ttHealth && mo.CountInv("Clip") == ttClip);
			Check("rAlive", PostsLiving() == 4 && !Count3("AjarFigure") && Shut3(3304) && Shut3(3305) && !tdOpen);
		}
		if (o == 1)
		{
			let red = Door32(1);
			Check("doorsAsAtTheStart", !red.frame && !red.carried && (red.pos.xy - (300, 760)).Length() < 1);
			Check("firstSelf", Selves3() == 1 && SelfAsRecord(0));
			Check("w1Hidden", HallThings(w, true) == 0 && HallThings(w, false) > 0 && HallPuppets(w) > 0);
			Actor m = postIs[0];
			Check("rIdle", m && !m.target && m.bAmbush);
		}
		if (shots && o == 20) { Look(mo, (296, 410), 90); Shot3(mo, "box 2 through the glass onto S (go 2)"); }
		// rule 4: the first self hangs RED again, at the tic it did (seen from part 2 through box 2's glass: its far side in S)
		{
			AjarFrame f1 = Doors().FindFrame(101);
			AjarGoLog lg = logs[0];
			for (int e = 0; e < lg.tic.Size(); e++)
				if (lg.frm[e] == f1 && o == lg.tic[e])
				{
					let red = Door32(1);
					Check("redHungAgain", red.frame == f1 && !red.carried && SelfAsRecord(0));
					Console.Printf("AJARTEST info RED hung again at %d of go %d", o, tgo);
				}
		}
		if (slow) return;
		if (t3Step == 0 && o > 26 && Walk3(mo, 44)) { t3Step = 1; t3Mark = o; }
		if (t3Step == 1)
		{
			// in R: when down, at each in turn: rockets, then whatever is left of it is killed
			if (mo.pos.z > FLOOR_R3 + 4) return;
			if (o % 60 == 0) Snap3(r);              // the fight under way (go 3 sees it played), before this tic's shot
			Actor a = null;
			for (int i = 0; i < postIs.Size() && !a; i++) if (postIs[i] && postIs[i].health > 0) a = postIs[i];
			if (!a) a = LiveIn(mo, r);
			if (!a) { t3Step = 2; NewRoute(); return; }
			if (a != ttAim) { ttAim = a; ttFightFrom = o; }
			Face(mo, a);
			if (o - ttFightFrom < 25 && (o - ttFightFrom) % 12 == 0) mo.SpawnPlayerMissile("Rocket");
			if (o - ttFightFrom == 30) a.DamageMobj(mo, mo, 10000, 'None');
		}
		if (t3Step == 2)
		{
			if (wonTic[r] < 0) return;
			if (o == wonTic[r] + 20) Check("rWon", Open3(3304) && Open3(3305) && !HallLives(r));
			if (o < wonTic[r] + 20) return;
			mo.pitch = 0;
			if (offPlate) { if (Walk3(mo, 58)) t3Step = 3; Toward(mo, (2000, 352)); return; }
			if (Walk3(mo, 58)) { t3Step = 3; t3Mark = o; }
		}
		if (t3Step == 3)
		{
			if (offPlate) { Toward(mo, (2000, 352)); return; }
			if (wind && !ttWindFrom && o > t3Mark + 3)
			{
				// on plate 2: wind on to two seconds before the first self steps onto plate 1
				ttWindFrom = o + 1;
				AjarThirdWind wp = AjarThirdWind(ThinkerIterator.Create("AjarThirdWind").Next());
				Look(mo, mo.pos.xy, 0);
				TestWind(mo, wp);
				ttWindTo = ot + 1;
				int s1 = -1;
				for (int s = 0; s < plFrom.Size(); s++) if (plSelf[s] == 0 && plFrom[s] > ttWindFrom + 70 && s1 < 0) s1 = plFrom[s];
				Check("windToBeforePlateOne", ttWindTo == s1 - 70 && plates[1].mine);
				return;
			}
			if (wind && ttWindFrom && o == ttWindTo + 1)
			{
				Check("windSelf", SelfAsRecord(0));
				Check("windHall", PuppetsAsRecord(w) || (ot >= hTrack[w].first.Size() && !HallPuppets(w)));
				AjarThirdTake mine = AjarThirdTake(takes[1]);
				Check("windPale", mine.Pale(ttWindFrom) && mine.Pale(ttWindTo - 1) && !mine.Pale(ttWindTo) && mine.x.Size() == ot + 1);
			}
			if (tdOpen && !ttMark2) { ttMark2 = o; Check("doorOpensWithBoth", exitOpened && plates[0].pressed && plates[1].mine); }
			if (ttMark2 && o == (shots ? max(ttMark2 + 20, V_E1) : ttMark2 + 20))
			{
				Check("exitOpenInGoTwo", Open3(3306) && plates[0].pressed);
				// E1 through the glass: the first self on plate 1
				if (shots) { Look(mo, mo.pos.xy, 110, -2); Shot3(mo, "E2: the first self on plate 1 (go 2)"); }
				t3Step = 4;
			}
		}
		if (t3Step == 4)
		{
			// E3 through the glass: the exit door open
			if (shots && o == max(ttMark2 + 20, V_E1) + 122) { Look(mo, (2040, 292), 302, -1); Shot3(mo, "E2: the exit door open, beyond E3's glass (go 2)"); }
			if (o > (shots ? max(ttMark2 + 20, V_E1) + 244 : ttMark2 + 22)) Walk3(mo, 70);
		}
	}
	int ttMark2;
	bool ttFixed;               // go 1 leaves plate 1 at V_LEAVE1 (the cfg's USE is timed by it)
	const V_GANTRY = 950;       // mode 3's views: the gantry in go 1,
	const V_LEAVE1 = 1300;      // go 1 leaves plate 1,
	const V_E1 = 1200;          // E2's look at plate 1 in go 2 (and 122 tics on, at E3),
	const V_DUCT = 240;         // the duct in go 3
	const FLOOR_R3 = -96;

	// --- go 3: `late` waits in box 3; `wind` winds on in E3 ----
	int ttLen2;
	void Go3(PlayerPawn mo, bool shots, bool late = false, bool wind = false)
	{
		int o = ot;
		int r = HallIx(2), w = HallIx(1);
		if (o == 0) { ttLen2 = takes[1].x.Size(); Check("boxThree", tgo == 3 && BoxOf(mo) == 3 && takes.Size() == 3); }
		if (o == 2)
		{
			Check("twoSelves", Selves3() == 2 && SelfAsRecord(0) && SelfAsRecord(1));
			Check("rPlayedFromItsStart", HallPuppets(r) >= 4 && HallThings(r, true) == 0 && Shut3(3304) && Shut3(3305));
			Check("w1PlayedAgain", HallPuppets(w) > 0 && HallThings(w, true) == 0);
		}
		if (o == 40)
		{
			int standing = 0;
			for (int i = 0; i < puppets.Size(); i++)
				if (puppets[i] && puppetTrack[i] == 100 + r && slotCls[puppetSlot[i]] && GetDefaultByType(slotCls[puppetSlot[i]]).bIsMonster) standing++;
			Check("rBefore", standing == 4 && HallThings(r, true) == 0);
		}
		if (wonTic[r] >= 0 && o == wonTic[r] + 13) Check("shuttersAsGoTwoWon", Open3(3304) && Open3(3305));
		if (wonTic[r] > 0 && o == wonTic[r] - 1) Check("shuttersShutBeforeWin", Shut3(3304) && Shut3(3305));
		if (o == ttLen2 + 2) Check("rAfter", !HallPuppets(r) && HallThings(r, true) >= 3 && HallThings(r, false) == 0);
		if (o == takes[0].x.Size() + 2) Check("w1AsLeft", !HallPuppets(w) && HallThings(w, true) >= 8 && HallThings(w, false) == 0);
		if (wind && ttWindFrom && ttWindFrom < ttWindTo && o == ttWindFrom + 10)
		{
			// the second self's stretch wound over: pale, not on plate 2's count
			AjarGhost g = ghosts.Size() > 1 ? ghosts[1] : null;
			Check("paleSelf", g && g.GetRenderStyle() == STYLE_Translucent && g.health <= 0 && !plates[1].pressed);
		}
		if (wind && ttWindFrom && o == ttWindTo + 5)
		{
			AjarGhost g = ghosts.Size() > 1 ? ghosts[1] : null;
			Check("notPaleAfter", g && g.GetRenderStyle() == STYLE_Normal && g.health > 0 && plates[1].pressed);
		}
		if (late) return;
		if (t3Step == 0 && Walk3(mo, 76)) { t3Step = 1; t3Mark = o; }
		if (t3Step == 1)
		{
			// in the duct, looking into R
			if (o == t3Mark + 1) Look(mo, (1400, -64), 90, 6);
			if (o >= t3Mark + 2 && (!shots || o >= V_DUCT))
			{
				// the fight, through the glass
				Console.Printf("AJARTEST info duct at %d, R won at %d in go 2", o, wonTic[r]);
				if (shots) Shot3(mo, "the duct: go 2's fight in R (go 3)");
				else mo.pitch = 0;
				t3Step = 2;
			}
		}
		if (t3Step == 2 && Walk3(mo, 88)) { t3Step = 3; t3Mark = o; }
		if (t3Step == 3)
		{
			if (wind && !ttWind2From && o == t3Mark + 2)
			{
				ttWind2From = o + 1;
				AjarThirdWind wp = null;
				let it = ThinkerIterator.Create("AjarThirdWind");
				AjarThirdWind q;
				while (q = AjarThirdWind(it.Next())) if (q.pos.y < 256) wp = q;
				int next = -1;
				for (int s = 0; s < plFrom.Size(); s++) if (plFrom[s] - 70 > ttWind2From && (next < 0 || plFrom[s] < next)) next = plFrom[s];
				Look(mo, (2120, 180), 0);
				TestWind(mo, wp);
				ttWind2To = ot + 1;
				Check("windInE3To", next >= 0 && ttWind2To == next - 70);
				Look(mo, (2120, 64), 0);
			}
			if (wind && ttWind2To && o == ttWind2To)
			{
				Check("windInE3Selves", SelfAsRecord(0) && SelfAsRecord(1));
				Check("windHallR", PuppetsAsRecord(r) || (ot >= hTrack[r].first.Size() && !HallPuppets(r)));
			}
			// through, once the door is open and R's record is over
			if (exitDoor.IsOpen() && o > max(ttLen2, takes[0].x.Size()) + 3)
			{
				if (wind)
				{
					// no earlier self steps onto its plate after this: the message, and the clock as it was
					AjarThirdWind wp = null;
					let it = ThinkerIterator.Create("AjarThirdWind");
					AjarThirdWind q;
					while (q = AjarThirdWind(it.Next())) if (q.pos.y < 256) wp = q;
					int was = ot, len = takes[takes.Size() - 1].x.Size();
					TestWind(mo, wp);
					Check("windNoneLeft", ot == was && takes[takes.Size() - 1].x.Size() == len);
				}
				t3Step = 4;
			}
		}
		if (t3Step == 4 && Walk3(mo, 96)) t3Step = 5;
		if (t3Step >= 4 && Through(mo) && !ttDone)
		{
			ttDone = true;
			Check("throughTheExitDoor", Open3(3306) && tgo == 3 && !paradox);
		}
	}

	// --- the modes ---------------------------------------------------------------------
	void Third3(PlayerPawn mo, int t)
	{
		NewGo3();
		if (tgo == 1) Go1(mo, true);
		else if (tgo == 2) Go2(mo, true);
		else if (tgo == 3) Go3(mo, true);
	}

	// go 2 stays in box 2: the first self comes onto the gantry with R alive. Then USE.
	int ttPdx;
	void Third4(PlayerPawn mo, int t)
	{
		ttFixed = true;
		if (thirdLoads)
		{
			// loaded: the save of go 2's start (made before the paradox, so ttPdx is 0 in it)
			if (ttPdx >= 0)
			{
				ttPdx = -1;
				Check("loadedGoTwoStart", tgo == 2 && ot < 5 && !paradox && mo.health > 0 && takes.Size() == 2 && takes[0].x.Size() > 300
					&& PostsLiving() == 4 && Shut3(3304) && !Count3("AjarFigure"));
				t3Mark = ot;
			}
			if (ot == t3Mark + 30) Check("loadedPlays", Selves3() == 1 && SelfAsRecord(0) && HallPuppets(HallIx(1)) > 0 && HallThings(HallIx(1), true) == 0);
			return;
		}
		NewGo3();
		if (paradox)
		{
			if (!ttPdx)
			{
				ttPdx = t;
				Check("gantryParadox", tgo == 2 && paradoxCopy == 1 && mo.health <= 0 && paradoxWhy.IndexOf("gantry") >= 0 && ot == watchTic[0]
					&& wonTic[HallIx(2)] < 0 && PostsLiving() > 0);
			}
			if (t == ttPdx + 200) Check("theDarkAfter", ParadoxDark());
			// (USE: smoke_THIRD_4.cfg presses it, +use, at t 2500)
			return;
		}
		if (tgo == 1) Go1(mo, false);
		else if (tgo == 2) Go2(mo, false, slow: true);
	}

	// go 2 keeps off plate 2: the paradox when the first self leaves plate 1 for the last time
	void Third5(PlayerPawn mo, int t)
	{
		NewGo3();
		if (paradox)
		{
			if (!ttPdx)
			{
				ttPdx = t;
				Check("lateInGoTwo", tgo == 2 && paradoxCopy == 0 && mo.health <= 0 && paradoxWhy.IndexOf("never opened") >= 0 && ot == heldLast + 2
					&& !tdOpen && wonTic[HallIx(2)] >= 0);
			}
			return;
		}
		if (tgo == 1) Go1(mo, false);
		else if (tgo == 2) Go2(mo, false, offPlate: true);
	}

	// go 3 waits in box 3: the paradox when the exit door has shut for the last time
	void Third6(PlayerPawn mo, int t)
	{
		NewGo3();
		if (paradox)
		{
			if (!ttPdx)
			{
				ttPdx = t;
				Check("lateInGoThree", tgo == 3 && paradoxCopy == 0 && mo.health <= 0 && paradoxWhy.IndexOf("shut for the last time") >= 0
					&& exitDoor.IsShut() && exitUntil <= ot && ot - 1 > heldLast && exitOpened);
			}
			return;
		}
		if (tgo == 1) Go1(mo, false);
		else if (tgo == 2) Go2(mo, false);
		else if (tgo == 3) Go3(mo, false, late: true);
	}

	// winding on: in E2 (go 2), then in E3 (go 3)
	void Third7(PlayerPawn mo, int t)
	{
		NewGo3();
		if (tgo == 1) Go1(mo, false);
		else if (tgo == 2) Go2(mo, false, wind: true);
		else if (tgo == 3) Go3(mo, false, wind: true);
	}

	// a long go: go 1 of 21000 tics; from go 2 it is sampled to its end by winding the clock on
	static const int SAMPLES[] = { 3000, 6000, 9000, 12000, 15000, 18000, 20000, 20500 };
	int ttSample;
	void Third8(PlayerPawn mo, int t)
	{
		NewGo3();
		if (paradox)
		{
			if (!ttPdx)
			{
				ttPdx = t;
				Check("longLateParadox", tgo == 2 && paradoxCopy == 0 && takes[0].x.Size() > 20000);
				Console.Printf("AJARTEST info long paradox: echoes=%d held=%d", pdxEchoTake.Size(), pdxHeld.Size());
			}
			return;
		}
		if (tgo == 1) { Go1(mo, false, longGo: true); return; }
		if (tgo != 2) return;
		int o = ot;
		int w = HallIx(1), r = HallIx(2);
		if (o == 1)
		{
			AjarTake t1 = takes[0];
			AjarTrack tw = hTrack[w];
			int n = t1.x.Size();
			int takeBytes = n * (5 * 8 + 4), trackBytes = tw.first.Size() * 4 + tw.slot.Size() * (2 * 4 + 4 * 8);
			Console.Printf("AJARTEST info long record: go1 tics=%d, self record %d bytes; W1 track tics=%d records=%d slots=%d, %d bytes; door log %d",
				n, takeBytes, tw.first.Size(), tw.slot.Size(), slotCls.Size(), trackBytes, logs[0].tic.Size());
			Check("longGoRecorded", n > 20000 && tw.first.Size() == n);
			double t0 = MSTimeF();
			ThirdSchedule();
			Console.Printf("AJARTEST info long: the schedule over 21000 tics took %.1f ms", MSTimeF() - t0);
			// R is won at once, so that the first self may cross the gantry
			for (int i = 0; i < postIs.Size(); i++) if (postIs[i] && postIs[i].health > 0) postIs[i].DamageMobj(mo, mo, 10000, 'None');
		}
		if (o > 1 && o < 40 && o % 5 == 0)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor m;
			while (m = Actor(it.Next())) if (m.bIsMonster && m.health > 0 && HallAt(m.pos.xy) == r) m.DamageMobj(mo, mo, 10000, 'None');
		}
		if (o == 40) Check("longRWon", wonTic[r] >= 0);
		if (o >= 40 && ttSample < SAMPLES.Size() && (t3Step == 0 || o == t3Mark + 10))
		{
			if (t3Step == 1 || t3Step == 0)
			{
				double t0 = MSTimeF();
				TestWind(mo, null, SAMPLES[ttSample]);
				Console.Printf("AJARTEST info long: to %d in %.1f ms", SAMPLES[ttSample], MSTimeF() - t0);
				t3Step = 2;
				t3Mark = ot;
				return;
			}
		}
		if (t3Step == 2 && o == t3Mark + 1)
		{
			bool ok = SelfAsRecord(0) && (PuppetsAsRecord(w) || (ot >= hTrack[w].first.Size() && !HallPuppets(w)));
			Check(String.Format("longSample%d", SAMPLES[ttSample]), ok);
			ttSample++;
			t3Step = 1;
			t3Mark = o - 9;
		}
	}

	// the save: killed in go 2, USE; the engine loads the save of go 2's start.
	// (Whether the earlier go came back whole: the length of its record is
	// printed before the death and after the load; the shell compares them.)
	int ttDied;
	void Third9(PlayerPawn mo, int t)
	{
		ttFixed = true;
		if (thirdLoads)
		{
			int w = HallIx(1);
			if (ttDied >= 0)
			{
				ttDied = -1;
				int len1 = takes.Size() > 0 ? takes[0].x.Size() : -1;
				Console.Printf("AJARTEST info loaded: go=%d ot=%d len1=%d w1tics=%d w1records=%d slots=%d logs=%d",
					tgo, ot, len1, hTrack[w] ? hTrack[w].first.Size() : -1, hTrack[w] ? hTrack[w].slot.Size() : -1, slotCls.Size(), logs.Size());
				Check("loadedTheGoTwoSave", tgo == 2 && ot < 5 && mo.health > 0 && takes.Size() == 2 && !paradox);
				t3Mark = ot;
			}
			if (ot == t3Mark + 20) Check("loadedSelfPlays", Selves3() == 1 && SelfAsRecord(0));
			if (ot == t3Mark + 21) Check("loadedHallPlays", PuppetsAsRecord(w) && HallThings(w, true) == 0 && PostsLiving() == 4);
			// (the earlier go played on as before: SnapChecks, W1 against what go 1 noted; the notes came back with the save)
			return;
		}
		NewGo3();
		if (tgo == 1) { Go1(mo, false); return; }
		if (tgo != 2) return;
		int w = HallIx(1);
		if (ot == 0)
			Console.Printf("AJARTEST info before: go=%d ot=%d len1=%d w1tics=%d w1records=%d slots=%d logs=%d",
				tgo, ot, takes[0].x.Size(), hTrack[w].first.Size(), hTrack[w].slot.Size(), slotCls.Size(), logs.Size());
		if (ot == 120 && !ttDied)
		{
			mo.player.cheats &= ~CF_GODMODE;
			mo.DamageMobj(null, null, 10000, 'None', DMG_FORCED);
			ttDied = t;
			Check("killedInGoTwo", mo.health <= 0);
		}
		// (USE: smoke_THIRD_9.cfg presses it, +use, at t 1500: go 1 is 1300 long, the death at 120 of go 2)
	}
}
