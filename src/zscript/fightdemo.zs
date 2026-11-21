// MAP32 room 3 played by itself (PLAN.md, "MAP32 room 3: the fight as fought,
// a demonstration"). ajar_autotest 20 on MAP32: `DEMO=3 ./run.sh` to watch it,
// `MAP=MAP32 MODE=20 tools/smoke.sh` (tools/smoke_MAP32_20.cfg) as a test.
//
// A bot plays the fight honestly. At tic 2 it is put into room 3's lobby with
// what a fresh start of the level gives (as the test modes 5, 7 and 9 do);
// after that nothing is given, set or done for it that a player could not do:
//  * it moves by the thrust a running player's keys give (MovePlayer's
//    numbers: 1.5625 a tic on a plain floor, so 16.7 at most, with the
//    engine's friction), in any direction, and only on the ground; the view
//    bobs as it does for a player (PlayerPawn.Bob, PlayRunning);
//  * it turns at most FD_TURN degrees a tic, and looks up and down at most
//    FD_PITCH;
//  * it shoots with the real weapons: it picks one (PendingWeapon, so it is
//    lowered and raised as for a player), fires when the weapon is ready
//    (FireWeapon, as CheckWeaponFire does for the fire button), and holds
//    the button for the next shot the way A_ReFire would see it held (it
//    fires again on the tic the weapon reaches its A_ReFire state, the last
//    of its Fire sequence). Ammunition, rate of fire, the picture: the
//    engine's;
//  * it picks things up by walking over them; it pulls the press's lever by
//    the lever's own Used(), only standing within use range facing it, as
//    the engine's use line does for a thing;
//  * it reads the fight as a player sees it: where the monsters are and
//    what they are, how many stand under the press, whether the press is
//    up, the lamps, the clock.
// No god mode, no SetOrigin, no GiveInventory, no damage or missile of its
// own making. Checked: `honest` (never god mode, buddha cheat or
// invulnerability; the fight's own rescue sets bBuddha, which is the
// fight's rule, not a cheat).
//
// The plan for room 3 is in FdRoom3 (below the core); the captions say what
// each self does (FdSay, drawn by FdOverlay from time.zs's RenderOverlay).

extend class AjarTimeHandler
{
	const FD_THRUST = 1.5625;       // a running player's keys, a tic (MovePlayer: 50 * movefactor)
	const FD_RUN = 16.6;            // and the speed that comes to with the friction
	const FD_TURN = 20;
	const FD_PITCH = 8;
	const FD_R = 16;                // the player's radius

	int fdT;                        // tics since the demonstration began
	bool fdBad;                     // god mode or the like seen on
	string fdCap1, fdCap2;          // the caption
	int fdCapT;

	bool FdOn() { return CVar.GetCVar("ajar_autotest").GetInt() == 20 && level.mapname ~== "MAP32"; }
	void FdLog(string s) { Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "AJARTEST info [%d] %s", fdT, s); }
	void FdCheck(string what, bool ok) { Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "AJARTEST %s=%d", what, ok); }
	void FdSay(string a, string b = "")
	{
		if (a == fdCap1 && b == fdCap2) return;
		fdCap1 = a; fdCap2 = b; fdCapT = fdT;
		FdLog("caption: " .. a .. (b != "" ? " / " .. b : ""));
	}

	// (from RenderOverlay, time.zs) the caption at the bottom of the screen
	ui void FdOverlay(RenderEvent e)
	{
		if (fdCap1 == "" || !(level.mapname ~== "MAP32")) return;
		int y = fdCap2 != "" ? 352 : 364;
		Screen.Dim("black", 0.55, 0, int(Screen.GetHeight() * (y - 6) / 400.), Screen.GetWidth(), Screen.GetHeight());
		Screen.DrawText(SmallFont, Font.CR_GOLD, 320 - SmallFont.StringWidth(fdCap1) / 2, y, fdCap1, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
		if (fdCap2 != "")
			Screen.DrawText(SmallFont, Font.CR_WHITE, 320 - SmallFont.StringWidth(fdCap2) / 2, y + 14, fdCap2, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
	}

	// ======== the body ===========================================================
	// What it wants this tic, set by the plan; FdBody does it as a player would.
	Vector2 fdGoal;                 // where it walks (fdWalk), through fdPath
	bool fdWalk;
	double fdNear;                  // how near is there
	bool fdDirect;                  // straight there (no path: a door, the wing)
	bool fdAvoid;                   // keep off monsters (on the demo: a touch wakes them)
	Actor fdAim;                    // what it shoots at (fdShoot), or faces
	bool fdShoot;
	double fdFaceAng;               // with nothing to aim at: the way it faces
	bool fdFace;
	bool fdDodge;                   // step aside from shots
	Array<double> fdPx, fdPy;       // the path
	int fdPathT;
	Vector2 fdPathGoal;
	int fdStuck;
	Vector2 fdLastPos;

	// the walls and slabs of room 3's hall and chamber, as rectangles (x1, y1, x2, y2)
	static const double FD_SOLID[] = {
		5160, 160, 5352, 224,   6184, 160, 6376, 224,   5480, 320, 5672, 384,   5864, 320, 6056, 384,     // the hall's slabs
		5320, 1008, 5448, 1072,   6088, 1008, 6216, 1072,                                                 // the chamber's
		4700, 768, 5128, 800,   6408, 768, 6600, 800,                                                     // the wall's two stubs, either side of the mouth
		4600, 320, 5000, 768,   4600, -200, 5000, 64 };                                                   // the lobby's walls
	const FD_PAD = 30;

	bool FdCuts(Vector2 p, Vector2 q, double x1, double y1, double x2, double y2)
	{
		double t0 = 0, t1 = 1;
		for (int k = 0; k < 2; k++)
		{
			double d = k ? q.y - p.y : q.x - p.x, lo = k ? y1 : x1, hi = k ? y2 : x2, s = k ? p.y : p.x;
			if (abs(d) < 1e-9) { if (s <= lo || s >= hi) return false; continue; }
			double a = (lo - s) / d, b = (hi - s) / d;
			t0 = max(t0, min(a, b)); t1 = min(t1, max(a, b));
		}
		return t0 < t1;
	}
	bool FdClear(Vector2 p, Vector2 q, double pad)
	{
		for (int i = 0; i < FD_SOLID.Size(); i += 4)
			if (FdCuts(p, q, FD_SOLID[i] - pad, FD_SOLID[i + 1] - pad, FD_SOLID[i + 2] + pad, FD_SOLID[i + 3] + pad)) return false;
		return true;
	}
	// is p where one can stand in room 3 (hall, mouth, chamber, lobby)?
	bool FdRoomy(Vector2 p)
	{
		double m = FD_R + 2;
		if (p.x > 5000 + m && p.x < 6536 - m && p.y > m && p.y < 768 - m) return true;
		if (p.x > 5000 + m && p.x < 6536 - m && p.y > 800 + m && p.y < 1280 - m) return true;
		if (p.x > 5128 + m && p.x < 6408 - m && p.y > 700 && p.y < 860) return true;
		if (p.x > 4744 + m && p.x < 5010 && p.y > 64 + m && p.y < 320 - m) return true;
		return false;
	}

	// The way from p to q round the slabs and through the mouth: the corners of the padded rectangles.
	void FdPlan(Vector2 p, Vector2 q)
	{
		fdPx.Clear(); fdPy.Clear();
		if (FdClear(p, q, 6)) { fdPx.Push(q.x); fdPy.Push(q.y); return; }
		Array<double> nx, ny, dist;
		Array<int> from, done;
		nx.Push(p.x); ny.Push(p.y);
		nx.Push(q.x); ny.Push(q.y);
		double c = FD_PAD + 2;
		for (int i = 0; i < FD_SOLID.Size(); i += 4)
		{
			for (int k = 0; k < 4; k++)
			{
				Vector2 v = ((k & 1) ? FD_SOLID[i + 2] + c : FD_SOLID[i] - c, (k & 2) ? FD_SOLID[i + 3] + c : FD_SOLID[i + 1] - c);
				if (FdRoomy(v)) { nx.Push(v.x); ny.Push(v.y); }
			}
		}
		int n = nx.Size();
		for (int i = 0; i < n; i++) { dist.Push(i ? 1e9 : 0); from.Push(-1); done.Push(0); }
		for (;;)
		{
			int u = -1;
			for (int i = 0; i < n; i++) if (!done[i] && (u < 0 || dist[i] < dist[u])) u = i;
			if (u < 0 || dist[u] >= 1e9 || u == 1) break;
			done[u] = 1;
			for (int i = 0; i < n; i++)
			{
				if (done[i]) continue;
				Vector2 a = (nx[u], ny[u]), b = (nx[i], ny[i]);
				double d = dist[u] + (b - a).Length();
				if (d >= dist[i] || !FdClear(a, b, u ? FD_PAD - 4 : 6)) continue;        // (from where it stands: it may be near a wall)
				dist[i] = d; from[i] = u;
			}
		}
		if (from[1] < 0) { fdPx.Push(q.x); fdPy.Push(q.y); return; }       // no way found: straight
		Array<int> rev;
		for (int i = 1; i > 0; i = from[i]) rev.Push(i);
		for (int i = rev.Size() - 1; i >= 0; i--) { fdPx.Push(nx[rev[i]]); fdPy.Push(ny[rev[i]]); }
	}

	void FdGoTo(Vector2 p, double near = 12, bool direct = false)
	{
		if (!fdWalk || (p - fdGoal).Length() > 1 || direct != fdDirect) fdPathT = -999;
		fdGoal = p; fdWalk = true; fdNear = near; fdDirect = direct;
	}
	void FdStop() { fdWalk = false; }
	bool FdThere(PlayerPawn mo, Vector2 p, double near = 16) { return (mo.pos.xy - p).Length() <= near; }

	// The direction to walk in, about `dir`, that keeps clear of the monsters near it: of 24, the one
	// that gets on best a few tics ahead less what passes close to a monster (none near: dir).
	Vector2 fdWeaveDir;
	Vector2 FdWeave(PlayerPawn mo, Vector2 dir)
	{
		Vector2 here = mo.pos.xy;
		Array<Actor> near;
		for (int i = 0; i < fdMon.Size(); i++)
		{
			Actor a = fdMon[i];
			if (a && a.health > 0 && (a.pos.xy - here).Length() < 160 + a.radius && abs(a.pos.z - mo.pos.z) < 64) near.Push(a);
		}
		for (int i = 0; i < fdSelves.Size(); i++)
		{
			Actor a = fdSelves[i];
			if (a && (a.pos.xy - here).Length() < 160 + a.radius && abs(a.pos.z - mo.pos.z) < 64) near.Push(a);
		}
		if (!near.Size()) { fdWeaveDir = dir; return dir; }
		double best = -1e9;
		Vector2 bestDir = dir;
		for (int i = 0; i < 32; i++)
		{
			Vector2 d = Actor.AngleToVector(i * 11.25, 1);
			Vector2 p = here + d * 64;
			if (!FdRoomy(p) || !FdClear(here, p, FD_R + 2)) continue;
			double score = (d dot dir) * 100 + (d dot fdWeaveDir > 0.85 ? 12 : 0);
			for (int j = 0; j < near.Size(); j++)
			{
				Actor a = near[j];
				Vector2 r = a.pos.xy - here;
				double s = clamp(r dot d, 0, 64);
				double c = (r - d * s).Length() - a.radius - FD_R;
				// close is bad, touching worse; a monster on the demo must not be touched at all, nor an
				// earlier self (paradox.zs): as much
				if (c < 32) score -= (32 - c) * (c < 4 ? 12 : 2) * (a is "AjarGhost" || OnDemo(a) ? 3 : 1);
			}
			if (score > best) { best = score; bestDir = d; }
		}
		fdWeaveDir = bestDir;
		return bestDir;
	}

	// the monsters and others' shots near it, this tic; and the earlier selves it must not touch
	// (paradox.zs: their record still running, in the hall)
	Array<Actor> fdMon, fdShots, fdSelves;
	Array<int> fdSelfGo;            // fdSelves[i] is the copy of takes[fdSelfGo[i]]
	void FdLook(PlayerPawn mo)
	{
		fdMon.Clear(); fdShots.Clear(); fdSelves.Clear(); fdSelfGo.Clear();
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.bIsMonster && a.health > 0) { fdMon.Push(a); continue; }
			if (a.bMissile && a.target != mo && (a.pos.xy - mo.pos.xy).Length() < 900 && a.vel.xy.Length() > 0.5) fdShots.Push(a);
		}
		for (int i = 0; i < takes.Size() - 1 && i < ghosts.Size(); i++)
		{
			AjarGhost g = ghosts[i];
			if (!g || ot >= takes[i].x.Size()) continue;
			int k, b;
			[k, b] = Where(g.pos.xy);
			if (k == fight && b == 0) { fdSelves.Push(g); fdSelfGo.Push(i); }
		}
	}

	// One tic of a player's hands.
	void FdBody(PlayerPawn mo)
	{
		if (mo.health <= 0) return;
		bool frozen = (mo.player.cheats & (CF_FROZEN | CF_TOTALLYFROZEN)) != 0;
		// --- where to go
		Vector2 want = (0, 0);
		if (fdWalk && !frozen)
		{
			Vector2 to = fdGoal;
			if (!fdDirect)
			{
				if (fdPathT < fdT - 10 || (fdPathGoal - fdGoal).Length() > 1) { FdPlan(mo.pos.xy, fdGoal); fdPathT = fdT; fdPathGoal = fdGoal; }
				while (fdPx.Size() > 1 && (mo.pos.xy - (fdPx[0], fdPy[0])).Length() < 28) { fdPx.Delete(0); fdPy.Delete(0); }
				if (fdPx.Size()) to = (fdPx[0], fdPy[0]);
			}
			Vector2 d = to - mo.pos.xy;
			double len = d.Length();
			bool last = fdDirect || fdPx.Size() <= 1;
			if (len > (last ? fdNear : 4))
			{
				// as fast as it can and still stop there (braking is the keys the other way)
				double sp = last ? min(FD_RUN, 0.26 * (len - fdNear * 0.5) + 1) : FD_RUN;
				want = d / len * sp;
				// among monsters: the way round them that gets on best (a human weaves)
				if (!fdDirect && sp > 6) want = FdWeave(mo, d / len) * sp;
			}
		}
		// --- keep off monsters (on the demo a touch wakes them; awake, they claw)
		Vector2 push = (0, 0);
		if (!frozen && (fdAvoid || fdWalk))
		{
			for (int i = 0; i < fdMon.Size(); i++)
			{
				Actor a = fdMon[i];
				if (!a || a.health <= 0) continue;
				Vector2 d = mo.pos.xy - a.pos.xy;
				double len = d.Length(), keep = a.radius + FD_R + (fdAvoid ? 40 : 24);
				if (len >= keep || len < 0.1) continue;
				if (abs(a.pos.z - mo.pos.z) > 64) continue;
				push += d / len * (keep - len) / keep * FD_RUN * 1.5;
			}
		}
		// and off its earlier selves (paradox.zs: a touch ends the universe), as off a monster on the
		// demo, whether it walks or stands: one may walk into it. Where each will be in the next few
		// tics is known (it was this player): off the nearest of those places
		if (!frozen)
		{
			for (int i = 0; i < fdSelves.Size(); i++)
			{
				Actor a = fdSelves[i];
				if (!a) continue;
				Vector2 at = a.pos.xy;
				AjarTake tk = takes[fdSelfGo[i]];
				for (int j = ot; j < tk.x.Size() && j <= ot + 6; j++)
					if (((tk.x[j], tk.y[j]) - mo.pos.xy).Length() < (at - mo.pos.xy).Length()) at = (tk.x[j], tk.y[j]);
				Vector2 d = mo.pos.xy - at;
				double len = d.Length(), keep = a.radius + FD_R + 40;
				if (len >= keep || abs(a.pos.z - mo.pos.z) > 64) continue;
				if (len < 0.1) { d = (1, 0); len = 0.1; }
				push += d.Unit() * (keep - len) / keep * FD_RUN * 1.5;
			}
		}
		// --- step aside from what is flying at it
		Vector2 dodge = (0, 0);
		if (!frozen && fdDodge)
		{
			for (int i = 0; i < fdShots.Size(); i++)
			{
				Actor s = fdShots[i];
				if (!s) continue;
				Vector2 p = s.pos.xy - mo.pos.xy, v = s.vel.xy - mo.vel.xy;
				double vv = v dot v;
				if (vv < 1) continue;
				double t = -(p dot v) / vv;
				if (t < 0 || t > 30) continue;
				Vector2 c = p + v * t;
				double miss = c.Length(), r = s.radius + FD_R + 14;
				if (miss > r) continue;
				if (s.pos.z > mo.pos.z + mo.height + 8 || s.pos.z + s.height < mo.pos.z - 8) continue;
				Vector2 side = miss > 1 ? -c / miss : (-v.y, v.x).Unit();
				dodge += side * (r - miss) / r * FD_RUN * 2;
			}
		}
		Vector2 total = want + push + dodge;
		if (total.Length() > FD_RUN) total = total.Unit() * FD_RUN;
		bool moving = fdWalk || push.Length() > 0 || dodge.Length() > 0;
		bool onground = mo.pos.z <= mo.floorz + 0.1 || mo.bOnMobj;
		if (moving && onground && !frozen)
		{
			// the keys: thrust toward the velocity it wants, no more than a player's
			double friction, movefactor;
			[friction, movefactor] = mo.GetFriction();
			double thrust = 50 * mo.Speed * movefactor;
			Vector2 dv = total - mo.vel.xy;
			if (dv.Length() > 0.3)
			{
				Vector2 th = dv.Length() > thrust ? dv.Unit() * thrust : dv;
				mo.vel.xy += th;
				double bobfactor = friction < Actor.ORIG_FRICTION ? movefactor : Actor.ORIG_FRICTION_FACTOR;
				mo.Bob(VectorAngle(th.x, th.y), 50 * th.Length() / thrust * bobfactor, true);
				mo.PlayRunning();
			}
		}
		// stuck against something: a sidestep
		if (fdWalk && moving && (mo.pos.xy - fdLastPos).Length() < 0.5 && total.Length() > 4) fdStuck++;
		else fdStuck = 0;
		fdLastPos = mo.pos.xy;
		if (fdStuck > 20) { fdStuck = 0; fdPathT = -999; }
		// --- where to look
		double wantAng = mo.angle, wantPitch = 0;
		if (fdAim && fdAim.health > 0)
		{
			Vector3 at = fdAim.pos + (0, 0, fdAim.height * 0.5);
			Vector2 lead = fdAim.vel.xy * min(12, (at.xy - mo.pos.xy).Length() / 25.) * 0.5;
			at.xy += lead;
			Vector2 d = at.xy - mo.pos.xy;
			wantAng = VectorAngle(d.x, d.y);
			double eye = mo.pos.z + mo.height * 0.5 + mo.AttackZOffset;
			wantPitch = -atan2(at.z - eye, max(1, d.Length()));
		}
		else if (fdFace) wantAng = fdFaceAng;
		else if (fdWalk && total.Length() > 2) wantAng = VectorAngle(total.x, total.y);
		mo.angle += clamp(Actor.deltaangle(mo.angle, wantAng), -FD_TURN, FD_TURN);
		mo.pitch += clamp(wantPitch - mo.pitch, -FD_PITCH, FD_PITCH);
		// --- the trigger
		FdTrigger(mo);
	}

	// ======== the hands: weapons ===================================================
	int fdWeapT;                    // when it last chose a weapon
	int fdShotsFired;

	Weapon FdHas(PlayerPawn mo, class<Weapon> cls)
	{
		let w = Weapon(mo.FindInventory(cls));
		return w && w.CheckAmmo(Weapon.PrimaryFire, false) ? w : null;
	}
	void FdWield(PlayerPawn mo, Weapon w)
	{
		if (!w) return;
		let p = mo.player;
		if (p.ReadyWeapon == w || p.PendingWeapon == w) return;
		p.PendingWeapon = w;
		fdWeapT = fdT;
	}
	// the state of the weapon's Fire sequence that goes back to Ready: where A_ReFire is
	State FdRefire(Weapon w)
	{
		State st = w.GetAtkState(false), ready = w.GetReadyState();
		for (int n = 0; st && n < 40; n++)
		{
			if (st.NextState == ready) return st;
			st = st.NextState;
		}
		return null;
	}
	void FdTrigger(PlayerPawn mo)
	{
		let p = mo.player;
		let w = p.ReadyWeapon;
		if (!w || !fdShoot || !fdAim || fdAim.health <= 0 || p.PendingWeapon != WP_NOCHANGE) { p.attackdown = false; return; }
		// on target?
		Vector2 d = fdAim.pos.xy - mo.pos.xy;
		double dist = d.Length();
		double tol = max(3., atan2(fdAim.radius * 0.8, max(dist, 1)));
		Vector2 lead = fdAim.vel.xy * min(12, dist / 25.) * 0.5;
		Vector2 dl = d + lead;
		if (abs(Actor.deltaangle(mo.angle, VectorAngle(dl.x, dl.y))) > tol) return;
		// a rocket into a wall or a monster right before it is a rocket in the face
		if (w is "RocketLauncher")
		{
			FLineTraceData ld;
			mo.LineTrace(mo.angle, 200, mo.pitch, 0, mo.height * 0.5 + mo.AttackZOffset, data: ld);
			if (ld.HitType != TRACE_HitNone && ld.Distance < 160) return;
		}
		let psp = p.GetPSprite(PSP_WEAPON);
		if (!psp) return;
		bool ready = (p.WeaponState & WF_WEAPONREADY) && w.InStateSequence(psp.CurState, w.GetReadyState());
		State rf = FdRefire(w);
		bool refire = rf && psp.CurState == rf && psp.Tics == rf.Tics;
		if (!ready && !refire) return;
		if (refire) p.refire++;
		p.attackdown = true;
		mo.FireWeapon(null);
		fdShotsFired++;
	}

	// ======== the eyes: what to shoot =================================================
	// A living monster of this fight that it sees and that is awake (one on the demo is left
	// alone: it goes where it went, and a shot would wake it), the most pressing.
	Actor FdTarget(PlayerPawn mo, double range = 2000, bool demoToo = false)
	{
		Actor best = null;
		double bestScore = 1e9;
		for (int i = 0; i < fdMon.Size(); i++)
		{
			Actor a = fdMon[i];
			if (!a || a.health <= 0) continue;
			if (!demoToo && OnDemo(a)) continue;
			double dist = mo.Distance2D(a);
			if (dist > range) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != 3 || b != 0) continue;
			if (!mo.CheckSight(a, SF_IGNOREVISIBILITY)) continue;
			double score = dist;
			if (a is "Archvile") score *= 0.2;
			else if (dist < 160) score *= 0.3;            // in its face
			else if (a is "Revenant" || a is "Cyberdemon") score *= 0.7;
			// keep on the one it has (no dithering)
			if (a == fdAim) score *= 0.75;
			// and one it need not turn far for
			score *= 1 + abs(Actor.deltaangle(mo.angle, mo.AngleTo(a))) / 360.;
			if (score < bestScore) { bestScore = score; best = a; }
		}
		return best;
	}
	// how many awake monsters stand within `cone` degrees of the line to a, out to `range`
	int FdCrowd(PlayerPawn mo, Actor a, double cone, double range)
	{
		if (!a) return 0;
		int n = 0;
		double ang = mo.AngleTo(a);
		for (int i = 0; i < fdMon.Size(); i++)
		{
			Actor m = fdMon[i];
			if (!m || m.health <= 0 || OnDemo(m) || mo.Distance2D(m) > range) continue;
			if (abs(Actor.deltaangle(ang, mo.AngleTo(m))) <= cone) n++;
		}
		return n;
	}
	// the weapon for the target: the BFG into a crowd or at a big one, rockets at range, else plasma
	void FdChoose(PlayerPawn mo, Actor a)
	{
		if (!a) return;
		if (fdT - fdWeapT < 35 && mo.player.PendingWeapon == WP_NOCHANGE && mo.player.ReadyWeapon
			&& mo.player.ReadyWeapon.CheckAmmo(Weapon.PrimaryFire, false)) return;
		double dist = mo.Distance2D(a);
		Weapon bfg = FdHas(mo, "BFG9000"), rl = FdHas(mo, "RocketLauncher"), pl = FdHas(mo, "PlasmaRifle");
		Weapon w = null;
		if (bfg && (FdCrowd(mo, a, 25, 1000) >= 5 || a is "Cyberdemon")) w = bfg;
		else if (rl && dist > 260 && a.SpawnHealth() >= 400) w = rl;
		else if (pl) w = pl;
		else if (rl && dist > 260) w = rl;
		else if (bfg) w = bfg;
		if (!w) w = FdHas(mo, "Chaingun");
		if (!w) w = FdHas(mo, "Shotgun");
		if (!w) w = FdHas(mo, "Pistol");
		FdWield(mo, w);
	}

	// ======== picking up ===============================================================
	// The nearest thing lying in the box (x1, y1, x2, y2) that it would take now (health only
	// when hurt, armour only when it has less), or none.
	Inventory FdPickup(PlayerPawn mo, double x1, double y1, double x2, double y2)
	{
		Inventory best = null;
		let it = ThinkerIterator.Create("Inventory");
		Inventory i;
		while (i = Inventory(it.Next()))
		{
			if (i.owner || i.bInvisible || i.pos.x < x1 || i.pos.x > x2 || i.pos.y < y1 || i.pos.y > y2) continue;
			if (abs(i.pos.z - mo.pos.z) > 24) continue;
			if (i is "Health" && mo.health >= 100) continue;
			if (i is "BasicArmorPickup" && mo.CountInv("BasicArmor") >= BasicArmorPickup(i).SaveAmount) continue;
			if (i is "Ammo")
			{
				let am = Ammo(mo.FindInventory(i.GetClass()));
				if (am && am.Amount >= am.MaxAmount) continue;
			}
			if (!best || mo.Distance2D(i) < mo.Distance2D(best)) best = i;
		}
		return best;
	}

	// ======== the lever ================================================================
	// USE on the press's lever: only within use range, facing it (the engine's use line).
	bool FdPull(PlayerPawn mo, AjarPressSwitch sw)
	{
		if (!sw) return false;
		Vector2 d = sw.pos.xy - mo.pos.xy;
		if (d.Length() > mo.UseRange || abs(Actor.deltaangle(mo.angle, VectorAngle(d.x, d.y))) > 30) return false;
		return sw.Used(mo);
	}
	AjarPressSwitch FdLever()
	{
		let it = ThinkerIterator.Create("AjarPressSwitch");
		AjarPressSwitch s;
		while (s = AjarPressSwitch(it.Next())) if (s.args[0] == PRESS32) return s;
		return null;
	}

	// ======== room 3 =====================================================================
	const FD_SCREEN_X = 5768;       // the screen's plate (map_secret2.SCREEN_PLATE3)
	const FD_SCREEN_Y = 1216;
	const FD_CAGE_X = 5096;         // the cage's plate
	const FD_CAGE_Y = 1184;
	const FD_LEVER_X = 5850;        // where one stands at the lever (it is at 5856, -18)
	const FD_LEVER_Y = -42;
	const FD_LEAVE_HP = 40;         // the bait goes when it is down to this

	int fdGoSeen, fdAnew, fdPhase, fdPhaseT, fdPhaseO;
	int fdGoStart;                  // fdT at the start of this go
	int fdBaitIn, fdBaitOut, fdBaitHp, fdLeverAt, fdPulls, fdWon, fdWonGo;
	int fdUnderMax;
	int fdCycleT, fdCycleLow, fdCyclePull0;   // this time through the four goes
	Array<int> fdPullO, fdPullUnder, fdPullKills, fdPullT, fdPullG;
	int fdPullKill0, fdPullPending;
	int fdRole;                     // from a box: 1 the lever, 2 the bait
	int fdUnderNow, fdLeftNow;      // this tic: under the press, left (for the log when the go ends)
	Name fdBy;                      // what last hurt the player (for the log)
	bool fdThenBait;                // the lever's self is the bait next (not in the last box)
	const FD_BAIT_LEAD = 150;       // it leaves the lever this long before the earlier self's time is over
	bool fdEast;

	void FdTo(int p, int o)
	{
		if (p == fdPhase) return;
		FdLog(String.Format("go %d phase %d -> %d at o=%d health=%d armour=%d cells=%d rockets=%d left=%d", takes.Size(), fdPhase, p, o,
			players[consoleplayer].mo.health, players[consoleplayer].mo.CountInv("BasicArmor"), players[consoleplayer].mo.CountInv("Cell"),
			players[consoleplayer].mo.CountInv("RocketAmmo"), Left()));
		fdPhase = p; fdPhaseT = fdT; fdPhaseO = o;
	}

	void FightDemo(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;      // the level again
		int t = fdT++;
		if (mo.player.cheats & (CF_GODMODE | CF_GODMODE2 | CF_BUDDHA | CF_BUDDHA2 | CF_NOCLIP | CF_NOCLIP2) || mo.bInvulnerable
			|| mo.FindInventory("PowerInvulnerable")) fdBad = true;
		if (t == 2) { Go(mo, 4872, 100, 0, 90); fdCycleLow = 1000; }   // into room 3's lobby: the rooms before are left, and over
		if (t < 3) return;
		if (fdWon)
		{
			if (t == fdWon + 70) FdReport(mo);
			fdWalk = fdShoot = false;
			FdBody(mo);
			return;
		}
		if (fight != 3) return;
		if (won.Find(3) < won.Size())
		{
			fdWon = t; fdWonGo = fdGoSeen;
			FdLog(String.Format("room 3 won at t=%d in go %d (anew %d) health=%d", t, fdGoSeen, fdAnew, mo.health));
			FdSay("Room 3 is won. The steel door is open.", "");
			return;
		}
		if (!open) return;
		int g = takes.Size(), o = ot;
		if (g != fdGoSeen)
		{
			if (g < fdGoSeen)
			{
				fdAnew++;
				FdCycle(mo, t);
				FdLog(String.Format("the fight began anew (%d)", fdAnew));
			}
			else if (g > 1)
			{
				AjarTake last = takes[g - 2];
				FdLog(String.Format("go %d ended at its tic %d: %s by door %d (last hurt by %s, %d under the press then, %d left); now go %d, health=%d",
					g - 1, last.x.Size(), last.died ? "killed" : "out", last.door - HallLine(3, 0), fdBy, fdUnderNow, fdLeftNow, g, mo.health));
				fdBy = 'None';
			}
			fdGoSeen = g;
			fdGoStart = t;
			fdPhase = -1;
			FdTo(0, o);
			fdPx.Clear(); fdPy.Clear();
			fdWalk = fdShoot = fdFace = false;
			fdAim = null;
			fdPullPending = 0;
		}
		FdLook(mo);
		if (mo.player.attacker && mo.player.attacker != mo && mo.player.damagecount) fdBy = mo.player.attacker.GetClassName();
		if (o > 10) fdCycleLow = min(fdCycleLow, Left());
		AjarPress prs = FindPress(PRESS32);
		if (prs && o > 10) { fdUnderNow = UnderPress(prs, -1); fdLeftNow = Left(); }      // (the monsters are back a few tics into a go)
		FdRoom3(mo, g, o);
		// what the last pull killed, two seconds on (the press's victims; -1: the go was over before)
		int np = fdPullT.Size();
		if (np > fdPullKills.Size() && fdT == fdPullT[np - 1] + 70)
		{
			AjarPress pp = FindPress(PRESS32);
			int v = pp && takes.Size() == fdPullG[np - 1] ? pp.victims.Size() : -1;
			fdPullKills.Push(v);
			FdLog(String.Format("pull %d killed %d", np, v));
		}
		FdBody(mo);
		if (t % 35 == 0)
		{
			AjarPress pr = FindPress(PRESS32);
			FdLog(String.Format("go=%d o=%d phase=%d pos=(%d,%d,%d) hp=%d ar=%d cells=%d rk=%d wpn=%s left=%d under=%d/%d demo=%d aim=%s shots=%d",
				g, o, fdPhase, mo.pos.x, mo.pos.y, mo.pos.z, mo.health, mo.CountInv("BasicArmor"), mo.CountInv("Cell"), mo.CountInv("RocketAmmo"),
				mo.player.ReadyWeapon ? mo.player.ReadyWeapon.GetClassName() : 'none', Left(), pr ? UnderPress(pr, 1) : -1, pr ? UnderPress(pr, 0) : -1,
				demo ? demo.len : -1, fdAim ? fdAim.GetClassName() : 'none', fdShotsFired));
		}
	}

	// fight with what is in reach, while doing whatever else
	void FdFight(PlayerPawn mo, double range = 2000)
	{
		Actor a = FdTarget(mo, range);
		fdAim = a;
		fdShoot = a != null;
		if (a) FdChoose(mo, a);
	}

	// how many monsters are near the line from p to q (within w)
	int FdNearLine(Vector2 p, Vector2 q, double w)
	{
		int n = 0;
		Vector2 d = q - p;
		double l = d.Length();
		if (l < 1) return 0;
		Vector2 u = d / l;
		for (int i = 0; i < fdMon.Size(); i++)
		{
			Actor a = fdMon[i];
			if (!a || a.health <= 0) continue;
			Vector2 r = a.pos.xy - p;
			double s = clamp(r dot u, 0, l);
			if ((r - u * s).Length() < w + a.radius) n++;
		}
		return n;
	}

	// ---- the plan ----------------------------------------------------------------
	// Phases. The bait: 10 arms (the lobby), 11 to the chamber, 13 holding out on the screen's plate,
	// 14 out by a time door, 15 holding the lobby (the variant: thin them there and fall).
	// From a box: 20 in the box; the lever: 21 to the shutter, 22 up the stairs, 24 at the lever, 26 after
	// the demo, in the wing; the bait from a box: 31 to the chamber past them on the demo, 32 waiting on
	// the plate till the demo is over, then 13. 90 no plan.
	// The plan played is 10 (the open front, 2026-11-21): go 1 takes all the lobby's guns and goes north
	// along the west wall to the screen's plate at the back, shooting only what is close; a bait from a
	// box; the lever's self pulls when 16 are on the demo under the press (+set fd_early N) or at the
	// last moment, then is the next bait. The others, tried on the old mouth (PLAN.md has their
	// numbers): +set fd_plan N. 0, 1, 4: other runs for the chamber; 2, 3, 5, 6, 9: go 1 holds the lobby
	// (3, 4 the bait on the cage's plate, 5 and 8 by door 3, else the screen's plate; 3 and up
	// shoot only arch-viles and what is close while the bait; 7 and up: the lever's self is the next bait).
	int FdPlanKnob() { CVar c = CVar.FindCVar("fd_plan"); return c ? c.GetInt() : 10; }

	// was earlier self i under the press at any tic (from, to: its first and last such tic)?
	int, int FdUnderSpan(int i)
	{
		AjarTake t = takes[i];
		int a = -1, z = -1;
		for (int j = 0; j < t.x.Size(); j++)
		{
			bool under = t.y[j] > 768 && t.x[j] > 5000 && t.x[j] < 6536 && (t.y[j] > 800 || (t.x[j] > 5128 && t.x[j] < 6408));
			if (!under) continue;
			if (a < 0) a = j;
			z = j;
		}
		return a, z;
	}

	// where the bait waits: plan 3 hides on the cage's plate (out of sight of the hall), else the screen's
	Vector2 FdBaitSpot(int plan) { return plan == 5 || plan == 8 ? (6480, 1040) : plan == 3 || plan == 4 ? (FD_CAGE_X, FD_CAGE_Y)
		: plan == 11 ? (5384, 1190) : (FD_SCREEN_X, FD_SCREEN_Y); }
	// where it walks to wait there: the spot, or 88 beside it while an earlier self whose time is not
	// up still stands on it (paradox.zs: the bait before held that spot; touching it ends the universe)
	Vector2 FdWaitSpot(int plan)
	{
		Vector2 s = FdBaitSpot(plan);
		if (!FdBusy(s, 35)) return s;
		// beside it, in the chamber, where no earlier self will be for the next two seconds
		double side = s.x < 6000 ? 1 : -1;
		static const double off[] = { 96, 0,  160, 0,  96, -128,  160, -128,  224, 0,  224, -128,  288, -64 };
		for (int i = 0; i < off.Size(); i += 2)
		{
			Vector2 p = s + (off[i] * side, off[i + 1]);
			if (FdRoomy(p) && FdClear(s, p, FD_R) && !FdBusy(p, 70)) return p;
		}
		return s + (288 * side, -64);
	}
	// where the lever's self stands: at the lever, or while an earlier self is there or will be in the
	// next second, back along the landing where none will be for the next two (paradox.zs)
	Vector2 FdLeverSpot()
	{
		Vector2 s = (FD_LEVER_X, FD_LEVER_Y);
		if (!FdBusy(s, 35)) return s;
		for (int i = 1; i <= 6; i++)
		{
			Vector2 p = (FD_LEVER_X - 80 * i, -48);
			if (!FdBusy(p, 70)) return p;
		}
		return (FD_LEVER_X - 480, -48);
	}
	// will an earlier self be within 72 of p in the next `ahead` tics? (What it did is known: it
	// was this player. A self that comes out of a box's door comes out where this one will.)
	bool FdBusy(Vector2 p, int ahead)
	{
		for (int i = 0; i < takes.Size() - 1; i++)
		{
			AjarTake tk = takes[i];
			for (int j = ot; j < tk.x.Size() && j <= ot + ahead; j++)
				if (((tk.x[j], tk.y[j]) - p).Length() < 72) return true;
		}
		return false;
	}
	int FdEarly(int plan) { CVar c = CVar.FindCVar("fd_early"); return c ? c.GetInt() : plan >= 10 ? 16 : 8; }
	bool FdRush(int plan) { return plan == 0 || plan == 1 || plan == 4 || plan == 7 || plan == 8 || plan >= 10; }

	// the bait fights only what is on it (close by) and the arch-viles: what comes in is for the press
	void FdBaitFight(PlayerPawn mo, int plan)
	{
		if (plan < 3) { FdFight(mo, 1500); return; }
		Actor a = FdTarget(mo, 1500);
		if (a && !(a is "Archvile") && mo.Distance2D(a) > 230 + a.radius) a = FdTarget(mo, 230);
		fdAim = a;
		fdShoot = a != null;
		if (a) FdChoose(mo, a);
	}

	void FdRoom3(PlayerPawn mo, int g, int o)
	{
		AjarPress pr = FindPress(PRESS32);
		AjarShutter sh = FindShutter(SHUT33);
		let sw = FdLever();
		int plan = FdPlanKnob();
		int k, b;
		[k, b] = Where(mo.pos.xy);
		fdDodge = true;
		fdAvoid = demo && Demoing();
		if (fdPhase == 0)
		{
			if (at == 0) FdTo(10, o);
			else
			{
				// the self before this one: was it under the press? Then this one is at the lever
				int a, z;
				[a, z] = FdUnderSpan(g - 2);
				FdLog(String.Format("the self before was under the press from %d to %d (its go lasted %d)", a, z, takes[g - 2].x.Size()));
				fdRole = a >= 0 && z - a > 70 ? 1 : 2;
				fdThenBait = fdRole == 1 && at < BoxCount(3) && plan >= 7;
				FdTo(20, o);
			}
		}
		// --- go 1 (and a fight begun anew): the bait, from the lobby ---
		if (fdPhase == 10)
		{
			FdSay(String.Format("Go %d, the bait: take the guns and run for the chamber under the press.", g));
			Inventory i = FdPickup(mo, 4744, 64, 5000, 320);
			if (plan == 1 || plan == 4 || plan == 7 || plan == 8)
			{
				// only the plasma rifle and the BFG on the way out
				i = null;
				let it = ThinkerIterator.Create("Inventory");
				Inventory c;
				while (c = Inventory(it.Next()))
					if (!c.owner && (c is "PlasmaRifle" || c is "BFG9000" || (c is "CellPack" && plan >= 7)) && c.pos.x < 5000 && c.pos.y > 64 && c.pos.y < 320
						&& (!i || mo.Distance2D(c) < mo.Distance2D(i))) i = c;
			}
			if (i && o < 120) FdGoTo(i.pos.xy, 4, true);
			else FdTo(FdRush(plan) ? 11 : 15, o);
			FdFight(mo, 700);
		}
		if (fdPhase == 15)
		{
			FdSay("Thin them out from the lobby, as long as you live.");
			FdGoTo((4800, 190), 8, true);
			FdFight(mo, 1500);
		}
		if (fdPhase == 11)
		{
			// (the open front, plan 10 on: north along the west wall, and no shot on the way: a shot wakes them)
			if (plan >= 10 && mo.pos.y < 660 && mo.pos.x < 5400) FdGoTo((5056, 700), 40);
			else FdGoTo(FdBaitSpot(plan), 10);
			if (plan >= 10) FdFight(mo, 260);
			else FdFight(mo, 1200);
			if (pr.Under(mo) && !fdBaitIn) { fdBaitIn = o; FdLog(String.Format("the bait is under the press at o=%d health=%d", o, mo.health)); }
			if (FdThere(mo, FdBaitSpot(plan), 20)) FdTo(13, o);
		}
		if (fdPhase == 13)
		{
			FdSay("Stay alive in here. Everything that follows you in is under the press.",
				"Standing on this plate lowers a screen before the guards, for the next you.");
			FdGoTo(FdWaitSpot(plan), 6);
			FdBaitFight(mo, plan);
			fdUnderMax = max(fdUnderMax, UnderPress(pr, -1));
			if (o % 35 == 0) FdLog(String.Format("holding: %d under the press (%d on the demo), health %d", UnderPress(pr, -1), UnderPress(pr, 1), mo.health));
			if (mo.health <= (plan >= 10 ? 15 : FD_LEAVE_HP)) FdTo(14, o);      // (plan 10: leaving gives no less than dying)
		}
		if (fdPhase == 14)
		{
			FdSay("Out by the chamber's time door before they get you.");
			// the side with fewer of them on the way
			Vector2 here = mo.pos.xy;
			int e = FdNearLine(here, (6500, 1040), 64), w = FdNearLine(here, (5036, 1040), 64);
			if (fdPhaseO == o) { fdEast = e <= w; FdLog(String.Format("out: east %d west %d -> %s", e, w, fdEast ? "door 3" : "door 4")); }
			Vector2 door = fdEast ? (6500, 1040) : (5036, 1040);
			if ((mo.pos.xy - door).Length() < 40 || ((fdEast ? mo.pos.x > 6400 : mo.pos.x < 5140) && abs(mo.pos.y - 1040) < 20))
				FdGoTo(fdEast ? (6600, 1040) : (4940, 1040), 0, true);
			else FdGoTo(door, 8);
			FdFight(mo, 600);
		}
		// --- a go that starts in a box ---
		if (fdPhase == 20)
		{
			if (fdRole == 1) FdSay(String.Format("Go %d, the lever: they go where they went, after the earlier you.", g), "Do not touch them.");
			else FdSay(String.Format("Go %d, the bait: they go where they went. Walk past them, do not touch them,", g), "and wait in the chamber under the press.");
			fdShoot = false; fdAim = null;
			Inventory i = at == 1 ? FdPickup(mo, 4776, 464, 4984, 656) : at == 2 ? FdPickup(mo, 6552, 464, 6760, 656)
				: at == 3 ? FdPickup(mo, 6100, -216, 6356, -16) : null;
			int len = demo ? demo.len : 0;
			if (i && (o < len - 70 || (fdRole == 2 && o < len + 30))) FdGoTo(i.pos.xy, 4, true);
			else if (at > 0)
			{
				Line l = Doors().FindLine(BoxLine(3, at));
				Vector2 m = (l.v1.p + l.v2.p) / 2, n = (l.delta.y, -l.delta.x).Unit();
				// the lever: wait for the shutter (open while the earlier self is under the press), but not
				// for the demo's end in here (they would come in after me)
				bool go = fdRole == 2 || sh.IsOpen() || (sh.Held() && o > 20) || o > len - 70;
				// (not while an earlier self comes out where this one will, or stands there: the same
				// box door's way out, by the same rule at the same tic; paradox.zs)
				Line ul = Doors().FindLine(used);
				if (go && ul && FdBusy((ul.v1.p + ul.v2.p) / 2, 30)) go = false;
				if (go) FdGoTo(m - n * 60, 0, true);
				else { FdGoTo(m + n * 50, 6, true); fdFace = true; fdFaceAng = VectorAngle(-n.x, -n.y); }
			}
			if (at == 0) FdTo(fdRole == 1 ? 21 : 31, o);
		}
		if (fdPhase == 21)
		{
			FdSay("The shutter is open while the earlier you is under the press.", "Do not touch them.");
			if (mo.pos.y > 64 || abs(mo.pos.x - 5192) > 40) FdGoTo((5192, 40), 10);
			else FdGoTo((5192, -60), 6, true);
			if (mo.pos.y < -20) FdTo(22, o);
			if (!sh.Held() && !sh.IsOpen() && mo.pos.y > 30 && FdThere(mo, (5192, 40), 30) && !Demoing()) { fdRole = 2; FdTo(31, o); }
			if (o % 35 == 0) FdLog(String.Format("to the shutter: open %.2f held %d", sh.Opened(), sh.Held()));
		}
		if (fdPhase == 22)
		{
			FdSay("Up the stairs to the lever. The guards wake as you come in.");
			if (mo.pos.x < 5280) FdGoTo((5300, -56), 0, true);
			else FdGoTo(FdLeverSpot(), 6, true);
			Actor gd = FdTarget(mo, 900);
			fdAim = gd; fdShoot = gd && mo.pos.x > 5350;
			if (gd) FdChoose(mo, gd);
			if (FdThere(mo, (FD_LEVER_X, FD_LEVER_Y), 12)) { FdTo(24, o); fdLeverAt = o; FdLog(String.Format("at the lever at o=%d health=%d", o, mo.health)); }
		}
		if (fdPhase == 24 || fdPhase == 26)
		{
			FdGoTo(FdLeverSpot(), 6, true);
			// shoot the guards when they are seen; face the lever otherwise
			Actor gd = FdTarget(mo, 1500);
			int under = UnderPress(pr, 1);
			int len = demo ? demo.len : 0;
			bool up = PressUp(pr);
			bool last = Demoing() && o >= len - 40 && o <= len - 28;
			// (plan 10: the earlier self's time may be nearly over when the lever is reached: pull late, as
			// long as some are under; they wake only when it is over, and the press is down 34 after the pull)
			if (plan >= 10) last = Demoing() && o >= len - 24 && o <= len - 4;
			bool early = Demoing() && under >= FdEarly(plan) && o + 34 + 139 + 34 <= len;
			if (fdThenBait && plan >= 10)
			{
				// the open front: the pull at the last moment, when the most are under, then down into the
				// chamber once the press is up again (phase 25 waits in the hall till then)
				if (o >= len - 2 && fdPhase == 24 && !fdPullPending) { FdTo(25, o); return; }
			}
			else if (fdThenBait)
			{
				// it will be the bait next: the last pull early enough that the press is up when it walks in
				int go = len - FD_BAIT_LEAD;
				last = Demoing() && o >= go - 100 && o <= go - 80;
				early = Demoing() && under >= FdEarly(plan) && o + 139 <= go - 100;
				if (o >= go && fdPhase == 24) { FdTo(25, o); return; }
			}
			bool after = !Demoing() && UnderPress(pr, 0) >= 3;
			if (up && (last || early || after) && !fdPullPending) fdPullPending = o;
			if (fdPullPending)
			{
				fdAim = null; fdShoot = false; fdFace = true; fdFaceAng = 90;
				if (FdPull(mo, sw))
				{
					fdPulls++;
					while (fdPullKills.Size() < fdPullO.Size()) fdPullKills.Push(-1);
						fdPullO.Push(o); fdPullUnder.Push(under); fdPullT.Push(fdT); fdPullG.Push(takes.Size());
					FdLog(String.Format("pull %d at o=%d (demo %d): %d on the demo under the press, %d awake", fdPulls, o, len, under, UnderPress(pr, 0)));
					fdPullPending = 0;
				}
				if (fdPullPending && o > fdPullPending + 20) fdPullPending = 0;
			}
			else
			{
				fdAim = gd; fdShoot = gd != null;
				if (gd) FdChoose(mo, gd);
				else { fdFace = true; fdFaceAng = 90; }
			}
			if (Demoing()) FdSay("Pull when the chamber is full.", "The press is ready again four seconds after a pull.");
			else { FdSay("The earlier you is gone, and they are awake.", "The hall's monsters cannot climb in here."); FdTo(26, o); }
		}
		// --- the lever's self is the bait next: out by the window and into the chamber while they are on the demo ---
		if (fdPhase == 25)
		{
			FdSay("Now you are the bait: out by the window and into the chamber,", "while they still go where they went.");
			fdShoot = false; fdAim = null;
			fdAvoid = true;
			Vector2 spot = FdBaitSpot(plan);
			bool safe = PressUp(pr) && (PullIn(PRESS32) < 0 || PullIn(PRESS32) > 140);
			if (mo.pos.y < 0) FdGoTo((5768, mo.pos.y < -24 && abs(mo.pos.x - 5768) > 24 ? -40 : 60), 4, true);
			else if (!safe && mo.pos.y < 760) FdGoTo((5768, 640), 24);
			else FdGoTo(FdWaitSpot(plan), 10);
			if (!Demoing()) FdFight(mo, 1200);
			if (pr.Under(mo) && o % 35 == 0) FdLog(String.Format("the next bait under the press at o=%d health=%d", o, mo.health));
			if (FdThere(mo, spot, 20)) FdTo(Demoing() ? 32 : 13, o);
		}
		// --- the bait from a box: past them on the demo into the chamber, and wait there ---
		if (fdPhase == 31)
		{
			FdSay("Past them while they go where they went: do not touch them.", "Into the chamber, and wait there to be found.");
			FdGoTo(FdWaitSpot(plan), 10);
			fdAvoid = true;
			if (Demoing()) { fdShoot = false; fdAim = null; }
			else FdFight(mo, 1200);
			if (pr.Under(mo) && !fdBaitIn) { fdBaitIn = o; FdLog(String.Format("the bait is under the press at o=%d health=%d", o, mo.health)); }
			if (FdThere(mo, FdBaitSpot(plan), 20)) FdTo(Demoing() ? 32 : 13, o);
		}
		if (fdPhase == 32)
		{
			FdSay("Wait. When the earlier you is gone they wake, and come in after you.", "A shot now would wake one.");
			FdGoTo(FdWaitSpot(plan), 6);
			fdShoot = false; fdAim = null;
			if (!Demoing()) FdTo(13, o);
		}
		if (fdPhase == 90 && fdPhaseO == o) FdLog("no plan for this state");
	}

	// all four goes spent and the fight is as it was at first: what this time through did, and the
	// smoke test's checks after the first (it is not won: see PLAN.md, "the fight as fought")
	void FdCycle(PlayerPawn mo, int t)
	{
		int kills = 0;
		for (int i = fdCyclePull0; i < fdPullKills.Size(); i++) kills += max(fdPullKills[i], 0);
		FdLog(String.Format("time through %d: %d goes in %d s, %d pulls killing %d, at fewest %d left",
			fdAnew, fdGoSeen, (t - fdCycleT) / 35, fdPulls - fdCyclePull0, kills, fdCycleLow));
		if (fdAnew == 1)
		{
			FdCheck("honest", !fdBad);
			FdCheck("goes4", fdGoSeen == BoxCount(3) + 1);
			FdCheck("pulled", fdPulls > 0);
			FdCheck("won3", won.Find(3) < won.Size());
		}
		fdCycleT = t; fdCycleLow = 1000; fdCyclePull0 = fdPulls;
	}

	void FdReport(PlayerPawn mo)
	{
		FdLog(String.Format("bait in at %d out at %d; at the lever at %d; pulls %d; under max %d", fdBaitIn, fdBaitOut, fdLeverAt, fdPulls, fdUnderMax));
		for (int i = 0; i < fdPullO.Size(); i++)
			FdLog(String.Format("pull %d at %d: %d under, killed %d", i + 1, fdPullO[i], fdPullUnder[i], i < fdPullKills.Size() ? fdPullKills[i] : -1));
		FdCheck("honest", !fdBad);
		FdCheck("won3", won.Find(3) < won.Size() && !open && !mixed && !Left());
		FdCheck("steel3", SteelUp(3));
		FdLog(String.Format("won in go %d after %d begun anew, t=%d (%d s)", fdWonGo, fdAnew, fdWon, fdWon / 35));
	}
}
