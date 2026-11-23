// The left-handed copy (PLAN.md, "The left-handed room lab"; tools/lefthand.py
// builds a room a second time reflected, tools/map_lefthand.py is the lab).
//
// AjarLeftHanded (20150) is what the game needs of it at run time: it stands in
// the middle of a reflected copy, args[0] and args[1] the half width and half
// height of its box, and at the start of the level it flips the sprite of
// every actor standing in that box (SPRITEFLIP: the picture is drawn mirrored
// and the rotation shown is mirrored too, as in a mirror). args[2] = 1 keeps
// the copy off the automap until a player stands in it (every line in the box
// is ML_DONTDRAW until then).
class AjarLeftHanded : Actor
{
	bool revealed;
	int flippedCount;

	Default
	{
		+NOBLOCKMAP +NOSECTOR +NOGRAVITY +NOINTERACTION +DONTSPLASH +NOTELEPORT
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	bool Inside(Vector2 p) { return abs(p.x - pos.x) <= args[0] && abs(p.y - pos.y) <= args[1]; }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			if (a != self && !a.player && Inside(a.pos.xy)) { a.bSpriteFlip = true; flippedCount++; }
		if (args[2]) Hide(true);
	}

	void Hide(bool hide)
	{
		for (int i = 0; i < level.lines.Size(); i++)
		{
			Line l = level.lines[i];
			if (!Inside(l.v1.p) || !Inside(l.v2.p)) continue;
			if (hide) l.flags |= Line.ML_DONTDRAW;
			else l.flags &= ~Line.ML_DONTDRAW;
		}
	}

	override void Tick()
	{
		if (!args[2] || revealed) return;
		for (int i = 0; i < MAXPLAYERS; i++)
			if (playeringame[i] && players[i].mo && Inside(players[i].mo.pos.xy))
			{
				revealed = true;
				Hide(false);
				return;
			}
	}
}

// A statue of the marine, turned as it was placed: a thing with eight
// rotations and a clear left and right (the gun in his right hand).
class AjarLeftHandStatue : Actor
{
	Default
	{
		Radius 16;
		Height 56;
		+SOLID
	}
	States
	{
	Spawn:
		PLAY A -1;
		Stop;
	}
}

// Something to shoot at that stays where it is put and keeps count.
class LeftHandDummy : Actor
{
	int hits;
	string by;
	Default
	{
		Radius 16;
		Height 56;
		Health 100000;
		Mass 100000;
		+SHOOTABLE +SOLID +NOBLOOD +DONTTHRUST +NOGRAVITY +NODAMAGETHRUST
	}
	States
	{
	Spawn:
		POSS A -1;
		Stop;
	}
	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		hits++;
		by = inflictor ? inflictor.GetClassName() .. "" : "none";
		return 0;
	}
}

// The tests: MAP=LEFT MODE=n tools/smoke.sh (n = 1..5; see PLAN.md).
// Bays (x of the room's corner): A 0 (the opening, line 501 onto its copy's 502),
// B 1024 (the fourth pane a mirror), C 2048 (as A with a south mirror: 511, 512),
// D 3072 (as B with it), V 4096 (frame 101 among frame-sized mirrors, frame 102 in
// the east wall, GREEN's far side in the copy). Each copy is its room reflected:
// a point (x, y) of a pane room is (x, 2880 - y) in its copy.
class LeftHandTest : EventHandler
{
	const WALK = 8.33;
	const RUN = 16.67;
	const MIRRORED = 2880;      // y in the copy = MIRRORED - y in the room
	const SHIFT = 2096;         // the opening's portal: a pure shift north (bays A and C)
	const VSHIFT = 2080;        // bay V's frame 101 onto GREEN's far side
	int tic, cur, tt;
	int checks, fails;
	AjarHandler h;
	Array<Actor> made;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname ~== "LEFT"; }

	bool Seg(int n)
	{
		bool now = tic >= cur && tic < cur + n;
		if (now) tt = tic - cur;
		cur += n;
		return now;
	}
	bool At() { return Seg(1); }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}

	string PStr(Vector3 p) { return String.Format("(%.3f,%.3f,%.3f)", p.x, p.y, p.z); }
	string P2(Vector2 p) { return String.Format("(%.3f,%.3f)", p.x, p.y); }
	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }

	Line FindLine(int id)
	{
		let it = level.CreateLineIdIterator(id);
		int i = it.Next();
		if (i < 0) return null;
		return level.lines[i];
	}

	// the engine's rule for a line portal: p crossing src comes out at dst.v2 + R(p - src.v1)
	static double Turn(Line src, Line dst)
	{
		return VectorAngle(dst.delta.x, dst.delta.y) - VectorAngle(src.delta.x, src.delta.y) + 180;
	}
	static Vector2 Through(Line src, Line dst, Vector2 p)
	{
		return dst.v2.p + Actor.RotateVector(p - src.v1.p, Turn(src, dst));
	}

	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
	}

	void Clear()
	{
		for (int i = 0; i < made.Size(); i++) if (made[i]) made[i].Destroy();
		made.Clear();
	}

	Actor Make(class<Actor> type, double x, double y, double z, double ang, bool flip = false)
	{
		let a = Actor.Spawn(type, (x, y, FloorAt((x, y)) + z));
		if (!a) return null;
		a.angle = ang;
		a.bSpriteFlip = flip;
		made.Push(a);
		return a;
	}

	// a monster that stays as it stands (no thinking, its first picture)
	Actor Frozen(class<Actor> type, double x, double y, double ang, bool flip = false)
	{
		let a = Make(type, x, y, 0, ang, flip);
		if (a) a.tics = -1;
		return a;
	}

	// a missile held in the air where it is put
	Actor Held(class<Actor> type, double x, double y, double z, double ang, bool flip = false)
	{
		let a = Make(type, x, y, z, ang, flip);
		if (a) { a.vel = (0, 0, 0); a.bNoGravity = true; a.tics = -1; }
		return a;
	}

	AjarLeftHanded MarkerAt(Vector2 p)
	{
		let it = ThinkerIterator.Create("AjarLeftHanded");
		AjarLeftHanded m;
		while (m = AjarLeftHanded(it.Next())) if (m.Inside(p)) return m;
		return null;
	}

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 1)
		{
			mo.player.cheats |= CF_GODMODE;
			h = AjarHandler(EventHandler.Find("AjarHandler"));
		}
		cur = 2;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode == 1) Walks(mo);
		else if (mode == 2) Panes(mo);
		else if (mode == 3) Tells(mo);
		else if (mode == 4) Carried(mo);
		else if (mode == 5) CarriedViews(mo);
		if ((mode == 1 || mode == 4) && tic == cur + 2)
			Console.Printf("AJARTEST leftDone=1 checks=%d failed=%d", checks, fails);
	}

	override void WorldUnloaded(WorldEvent e)
	{
		if (!Testing()) return;
		Check("exitBySecretWayOut", e.NextMap ~== "MIR", "next map " .. e.NextMap);
		Console.Printf("AJARTEST leftDone=1 checks=%d failed=%d", checks, fails);
		CVar.FindCVar("ajar_autotest").SetInt(0);       // MIR after it must not take the test up
	}

	Vector3 wPrev;
	Vector2 wVel;
	Line wSrc, wDst;

	// the landing itself, checked on the tic after the crossing: the place by the
	// engine's rule, the facing turned by the portal (none for the opening)
	Vector2 lStart;
	int lCross;
	bool lDone;
	void Through1(Actor mo, string name, double x, double y, double ang, double off, double speed, int n, int srcId, int dstId,
		Vector2 copyOf = (0, 0), double copyAng = -1)
	{
		if (At())
		{
			Pose(mo, x, y, ang);
			lCross = 0;
			lDone = false;
			wSrc = FindLine(srcId);
			wDst = FindLine(dstId);
			wPrev = mo.pos;
		}
		if (Seg(n))
		{
			if (!lDone && tt > 0 && (mo.pos.xy - wPrev.xy).Length() > 200)
			{
				lDone = true;
				lCross = tic;
				Vector2 want = Through(wSrc, wDst, wPrev.xy + wVel);
				double turn = Turn(wSrc, wDst);
				double dA = Actor.DeltaAngle(mo.angle, ang + turn);
				double e = (mo.pos.xy - want).Length();
				string extra = "";
				if (copyAng >= 0)
				{
					// where the copy stands for: the room's point reflected (x, 2880 - y), the facing mirrored
					Vector2 mirr = (mo.pos.x - copyOf.x, MIRRORED - (mo.pos.y - copyOf.y));
					extra = String.Format("; in the copy at the mirror image of the room's %s (the mirrored facing would be %.1f)", P2(mirr), copyAng);
				}
				Check(name, e < 0.001 && abs(dA) < 0.001,
					String.Format("before %s moving %s, after %s facing %.3f; the engine's rule says %s, off by %.6f; turn %.3f%s",
					PStr(wPrev), P2(wVel), PStr(mo.pos), mo.angle, P2(want), e, turn, extra));
			}
			wPrev = mo.pos;
			mo.vel.xy = wVel = Actor.AngleToVector(ang + off, speed);
		}
		if (At())
		{
			mo.vel = (0, 0, 0);
			if (!lDone) Check(name, false, String.Format("no crossing; player %s", PStr(mo.pos)));
		}
	}

	// --- MODE=1: walking in and back, shots, the way out ------------------------------
	LeftHandDummy dIn, dGlass;
	Actor shot;
	Vector3 shotLast;
	bool shotGone;
	int puffHits;
	Line exitDoor;

	void FollowShot()
	{
		if (!shot) { shotGone = true; return; }
		if (shot.bMissile) shotLast = shot.pos;
		else shotGone = true;
	}

	void Shoot(Actor mo, string name, class<Actor> type, double x, double y, double ang, LeftHandDummy want, LeftHandDummy notWant, int n,
		double endYMin, double endYMax)
	{
		if (At())
		{
			Pose(mo, x, y, ang);
			if (want) want.hits = 0;
			if (notWant) notWant.hits = 0;
			shot = mo.SpawnPlayerMissile(type, ang, nofreeaim: true, noautoaim: true);
			shotGone = false;
			shotLast = shot ? shot.pos : (0, 0, 0);
		}
		if (Seg(n)) FollowShot();
		if (At())
		{
			bool ok = shotGone && shotLast.y >= endYMin && shotLast.y <= endYMax;
			if (want) ok = ok && want.hits > 0;
			if (notWant) ok = ok && notWant.hits == 0;
			Check(name, ok, String.Format("%s last flying at %s; dummy hit %d (%s)%s", type.GetClassName(), PStr(shotLast),
				want ? want.hits : -1, want ? want.by : "", notWant ? String.Format("; the other dummy %d", notWant.hits) : ""));
			if (shot) shot.Destroy();
		}
	}

	void Walks(Actor mo)
	{
		if (At())
		{
			Line a = FindLine(501), b = FindLine(502);
			Console.Printf("AJARTEST info portals in the map: %d; 501 %s-%s, 502 %s-%s", level.LinePortals.Size(),
				P2(a.v1.p), P2(a.v2.p), P2(b.v1.p), P2(b.v2.p));
			Check("openingIsAShift", abs(Actor.DeltaAngle(Turn(a, b), 0)) < 1e-9 && (Through(a, b, (352, 392)) - (352, 392 + SHIFT)).Length() < 1e-6,
				String.Format("turn %.6f, (352, 392) goes to %s", Turn(a, b), P2(Through(a, b, (352, 392)))));
			let mk = MarkerAt((256, 2700));
			Check("copyMarkerFlipped", mk != null && mk.flippedCount == 3, String.Format("%d things flipped in A's copy", mk ? mk.flippedCount : -1));
			// the copies' things: at the mirrored place, the angle mirrored, flipped
			int good = 0;
			let it = ThinkerIterator.Create("AjarLeftHandStatue");
			AjarLeftHandStatue s;
			while (s = AjarLeftHandStatue(it.Next()))
				if (s.pos.y > 2000 && s.pos.x < 512 && s.pos.xy == (128, MIRRORED - 200) && s.angle == 330 && s.bSpriteFlip) good++;
			Check("statueMirrored", good == 1, "the statue in A's copy at (128, 2680) facing 330, flipped");
		}
		// into the opening and out again
		Through1(mo, "walkIn", 352, 320, 90, 0, WALK, 16, 501, 502, (0, 0), 270);
		Through1(mo, "runIn", 352, 280, 90, 0, RUN, 12, 501, 502, (0, 0), 270);
		Through1(mo, "slantIn", 330, 330, 75, 0, WALK, 16, 501, 502, (0, 0), 285);
		Through1(mo, "backingIn", 352, 330, 270, 180, WALK, 16, 501, 502, (0, 0), 90);
		if (At()) Check("standsInTheCopy", mo.pos.y > MIRRORED - 384 && mo.pos.y < MIRRORED, PStr(mo.pos));
		Through1(mo, "walkBack", 352, MIRRORED - 330, 270, 0, WALK, 16, 502, 501);
		Through1(mo, "runBack", 352, MIRRORED - 280, 270, 0, RUN, 12, 502, 501);
		if (At()) Check("standsInA", mo.pos.y > 0 && mo.pos.y < 384 && mo.pos.x > 0 && mo.pos.x < 512, PStr(mo.pos));
		// a mirror pane is a wall: walking at pane 3 goes nowhere
		if (At()) { Pose(mo, 256, 330, 90); wPrev = mo.pos; }
		if (Seg(16)) mo.vel.xy = Actor.AngleToVector(90, WALK);
		if (At())
		{
			mo.vel = (0, 0, 0);
			Check("mirrorPaneIsAWall", mo.pos.y < 392 && mo.pos.y > 360, PStr(mo.pos));
		}
		// shots: through the opening they fly on into the copy; a mirror stops them
		if (At())
		{
			dIn = LeftHandDummy(Make("LeftHandDummy", 352, MIRRORED - 120, 0, 270));
			dGlass = LeftHandDummy(Make("LeftHandDummy", 256, MIRRORED - 120, 0, 270));
		}
		Shoot(mo, "rocketThroughOpening", "Rocket", 352, 150, 90, dIn, null, 70, MIRRORED - 200, MIRRORED);
		Shoot(mo, "plasmaThroughOpening", "PlasmaBall", 352, 150, 90, dIn, null, 70, MIRRORED - 200, MIRRORED);
		Shoot(mo, "rocketAtMirrorStops", "Rocket", 256, 150, 90, null, dGlass, 70, 300, 392);
		if (At()) dIn.hits = 0;
		if (At())
		{
			Pose(mo, 352, 150, 90);
			Actor puff;
			int dmg;
			[puff, dmg] = mo.LineAttack(90, 4096, 0, 10, 'Hitscan', "BulletPuff", LAF_NORANDOMPUFFZ);
			Check("hitscanThroughOpening", dIn.hits == 1,String.Format("dummy hit %d; puff %s", dIn.hits, puff ? PStr(puff.pos) : "none"));
		}
		if (At())
		{
			Pose(mo, 256, 150, 90);
			Actor puff;
			int dmg;
			[puff, dmg] = mo.LineAttack(90, 4096, 0, 10, 'Hitscan', "BulletPuff", LAF_NORANDOMPUFFZ);
			Check("hitscanAtMirrorStops", dGlass.hits == 0 && puff && puff.pos.y < 400, String.Format("dummy behind the glass hit %d; puff %s", dGlass.hits, puff ? PStr(puff.pos) : "none"));
		}
		// the way out: in by the opening, to the copy's door, open it, through it
		Through1(mo, "inForTheWayOut", 352, 320, 90, 0, WALK, 16, 501, 502, (0, 0), 270);
		if (At())
		{
			Pose(mo, 40, MIRRORED - 328, 180);
			for (int i = 0; i < level.lines.Size(); i++)
			{
				Line l = level.lines[i];
				if (l.special == 12 && l.v1.p.x == 0 && l.v2.p.x == 0 && min(l.v1.p.y, l.v2.p.y) == MIRRORED - 360) exitDoor = l;
			}
			bool used = exitDoor && exitDoor.Activate(mo, 0, SPAC_Use);
			Check("copysDoorOpens", used, exitDoor ? P2(exitDoor.v1.p) .. "-" .. P2(exitDoor.v2.p) : "no door");
		}
		Seg(40);
		if (Seg(40)) mo.vel.xy = Actor.AngleToVector(180, WALK);
		if (At()) Check("exitLineNotReached", false, "still here: " .. PStr(mo.pos));
	}

	// --- MODE=2: question 1, the pane wall as built and with the opening a mirror -----
	// Cameras in the room (from its corner): straight on, from the west and the
	// east at a slant, from the far (south-west) corner, and before the fourth
	// pane (where the player's own reflection would be in it).
	static const double CAMX[] = { 256, 96, 464, 32, 352 };
	static const double CAMY[] = { 48, 64, 160, 32, 140 };
	static const double CAMA[] = { 90, 50, 135, 55, 95 };

	void Look(Actor mo, int st, double x, double y, double ang, double pitch = 0)
	{
		if (st >= 1) Pose(mo, x, y, ang, pitch);
	}

	// views start at tic 82: the level's opening words are off the screen by then (the cfgs wait 116 for the first)
	const VIEWS = 82;

	void Panes(Actor mo)
	{
		if (tic < VIEWS) return;
		int i = (tic - VIEWS) / 40, st = (tic - VIEWS) % 40;
		// views 0..19: camera c = i / 4, then A seen, B seen, A hidden, B hidden
		// (hidden: the player is not drawn, in the mirrors either); 20, 21: A and B turned to the south wall
		if (st == 0) Console.Printf("AJARTEST view=%d t=%d", i, tic);
		if (i < 20)
		{
			int c = i / 4, k = i % 4;
			double ox = (k % 2) ? 1024 : 0;
			mo.bInvisible = k >= 2;
			Look(mo, st, ox + CAMX[c], CAMY[c], CAMA[c]);
			if (st == 39) Console.Printf("AJARTEST info view %d: camera %d in %s, player %s, %s", i, c, (k % 2) ? "B" : "A",
				k >= 2 ? "hidden" : "seen", PStr(mo.pos));
		}
		else if (i < 22)
		{
			mo.bInvisible = false;
			Look(mo, st, (i == 21 ? 1024 : 0) + 256, 300, 270);
		}
		if (tic == VIEWS + 40 * 22) Console.Printf("AJARTEST viewsDone=1");
	}

	// --- MODE=3: the tells, the depth, walking in, a monster in the copy, the automap ---
	void Tells(Actor mo)
	{
		if (tic < VIEWS) return;
		int i = (tic - VIEWS) / 40, st = (tic - VIEWS) % 40;
		if (st == 0) { Clear(); mo.bInvisible = false; Console.Printf("AJARTEST view=%d t=%d", i, tic); }
		if (st == 39) Console.Printf("AJARTEST info view %d: player %s facing %.1f", i, PStr(mo.pos), mo.angle);
		double ox = (i % 2) ? 1024 : 0;
		switch (i)
		{
		case 0: case 1:     // A, then B, from before the fourth pane: two imps behind the player, seen only in the
			                // glass: one where the fourth pane shows it, one in the third
			if (st == 1) { Frozen("DoomImp", ox + 400, 40, 90); Frozen("DoomImp", ox + 180, 40, 90); }
			Look(mo, st, ox + 352, 64, 90);
			break;
		case 2: case 3:     // the same, shots held in flight behind the player: a rocket where the fourth pane shows it, a plasma ball in the third
			if (st == 1)
			{
				Held("Rocket", ox + 400, 40, 30, 90);
				Held("PlasmaBall", ox + 200, 40, 30, 90);
			}
			Look(mo, st, ox + 352, 64, 90);
			break;
		case 4:             // walked in: from the copy, back at the opening (A, without the player)
			Look(mo, st, 352, MIRRORED - 120, 270);
			break;
		case 5:             // the copy's other panes from in it: mirrors (the player in them)
			Look(mo, st, 200, MIRRORED - 120, 250);
			break;
		case 6:             // the one thing not as it was: the copy's door
			Look(mo, st, 300, MIRRORED - 240, 196);
			break;
		case 7:             // a monster in the copy, seen from A: a figure in the glass, nobody in the room
			if (st == 1) Frozen("DoomImp", 352, MIRRORED - 200, 90, true);
			Look(mo, st, 256, 48, 90);
			break;
		case 8: case 9:     // depth: C (the opening and a south mirror) and D (its control), straight on
			Look(mo, st, (i == 8 ? 2048 : 3072) + 256, 48, 90);
			break;
		case 10: case 11:   // the same from the east at a slant
			Look(mo, st, (i == 10 ? 2048 : 3072) + 464, 160, 135);
			break;
		case 12: case 13:   // C and D: into the south mirror, the pane wall behind the player
			Look(mo, st, (i == 12 ? 2048 : 3072) + 400, 330, 270);
			break;
		case 14: case 15:   // C and D: in the panes, close and turned a little: the glass in the glass
			Look(mo, st, (i == 14 ? 2048 : 3072) + 352, 200, 80);
			break;
		// the automap follows the player and zooms out no further than the map's width: for the rooms and
		// their copies (y 0..2896) to be on it at once, the player is put between them (in no room: y 1400)
		case 16:            // the automap (the cfg opens it, zoomed out), after views 0..15: A's copy is drawn, C's is not
			Look(mo, st, 2400, 1400, 90);
			break;
		case 17:            // the same with the computer map
			if (st == 1) mo.GiveInventoryType("Allmap");
			Look(mo, st, 2400, 1400, 90);
			break;
		case 18:            // C's copy after standing in it: drawn
			if (st <= 4) Pose(mo, 2048 + 256, MIRRORED - 200, 90);
			else Look(mo, st, 2400, 1400, 90);
			break;
		}
		if (tic == VIEWS + 40 * 19) Console.Printf("AJARTEST viewsDone=1");
	}

	// --- MODE=4: the carried door; monsters' sight and sound through the opening -------
	AjarDoor green;
	Actor imp;
	void HangIn(AjarDoor d, int frameId)
	{
		AjarFrame f = h.FindFrame(frameId);
		if (!d || !f) { Console.Printf("AJARTEST info no door or no frame %d", frameId); return; }
		if (f.door == d) return;
		if (d.frame) h.Unhang(d.frame);
		if (f.door) h.Unhang(f);
		h.Hang(d, f);
	}

	void Carried(Actor mo)
	{
		if (At())
		{
			green = h.DoorOf(3);
			HangIn(green, 101);
			Line a = FindLine(101), b = FindLine(203);
			Check("frameIsAShift", a && b && abs(Actor.DeltaAngle(Turn(a, b), 0)) < 1e-9 && (Through(a, b, (4096 + 352, 400)) - (4096 + 352, 400 + VSHIFT)).Length() < 1e-6,
				a && b ? String.Format("turn %.6f; 101 %s-%s, 203 %s-%s", Turn(a, b), P2(a.v1.p), P2(a.v2.p), P2(b.v1.p), P2(b.v2.p)) : "no lines");
		}
		Through1(mo, "greenIn101_walkIn", 4096 + 352, 320, 90, 0, WALK, 18, 101, 203, (4096, 0), 270);
		Through1(mo, "greenIn101_walkBack", 4096 + 352, MIRRORED - 320, 270, 0, WALK, 18, 203, 101);
		if (At()) HangIn(green, 102);
		Through1(mo, "greenIn102_walkIn_turned", 4096 + 440, 192, 0, 0, WALK, 18, 102, 203);
		if (At()) Console.Printf("AJARTEST info by 102: in the copy at %s facing %.3f", PStr(mo.pos), mo.angle);
		if (At()) HangIn(green, 101);
		// sight and sound through the opening (A): what the engine does with a fixed portal of this kind
		if (At())
		{
			Pose(mo, 352, 200, 90);
			imp = Make("DoomImp", 352, MIRRORED - 250, 0, 270);      // in the copy, facing the opening, the player in plain view through it
		}
		Seg(30);
		if (At())
		{
			Check("impInCopyDoesNotSeePlayerInA", imp.target == null && !imp.CheckSight(mo),
				String.Format("woke %d, sight %d", imp.target != null, imp.CheckSight(mo)));
			imp.Destroy();
			Pose(mo, 352, MIRRORED - 250, 270);
			imp = Make("DoomImp", 352, 200, 0, 90);                  // in A facing the opening, the player in the copy through it
		}
		Seg(30);
		if (At())
		{
			Check("impInADoesNotSeePlayerInCopy", imp.target == null && !imp.CheckSight(mo),
				String.Format("woke %d, sight %d", imp.target != null, imp.CheckSight(mo)));
			imp.Destroy();
			Pose(mo, 352, 200, 270);                                 // the player in A, back to the glass
			imp = Make("DoomImp", 352, MIRRORED - 250, 0, 90);       // in the copy, its back to the opening
		}
		if (At()) mo.SoundAlert(mo);
		Seg(20);
		if (At())
		{
			Check("shotInAWakesImpInCopy", imp.target == mo, String.Format("woke %d (sound only: it faces away, and has no sight)", imp.target == mo));
			imp.Destroy();
		}
	}

	// --- MODE=5: the carried door seen ------------------------------------------------
	void CarriedViews(Actor mo)
	{
		if (tic == 2) green = h.DoorOf(3);
		if (tic < VIEWS) return;
		int i = (tic - VIEWS) / 40, st = (tic - VIEWS) % 40;
		if (st == 0) Console.Printf("AJARTEST view=%d t=%d", i, tic);
		if (st == 39) Console.Printf("AJARTEST info view %d: player %s facing %.1f", i, PStr(mo.pos), mo.angle);
		double ox = 4096;
		switch (i)
		{
		case 0:             // the frame empty among the mirrors
			Look(mo, st, ox + 256, 48, 90);
			break;
		case 1:             // GREEN hung in it, straight on
			if (st == 1) HangIn(green, 101);
			Look(mo, st, ox + 256, 48, 90);
			break;
		case 2:             // from the west at a slant
			Look(mo, st, ox + 64, 160, 45);
			break;
		case 3:             // close
			Look(mo, st, ox + 330, 250, 80);
			break;
		case 4:             // from the copy, back through it
			Look(mo, st, ox + 352, MIRRORED - 120, 270);
			break;
		case 5:             // GREEN in 102 (the east wall): the copy turned
			if (st == 1) HangIn(green, 102);
			Look(mo, st, ox + 300, 192, 0);
			break;
		}
		if (tic == VIEWS + 40 * 6) Console.Printf("AJARTEST viewsDone=1");
	}
}
