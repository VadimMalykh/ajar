// Ajar's own monster (the thief) and what Doom's monsters need to know about doors.

// Where a point on the far side of a hung door appears when looked at
// through it, and the other way round (a door works both ways).
struct AjarSight play
{
	// The engine maps a point p crossing `src` to dst.v2 + R(p - src.v1), with
	// R a turn by (angle of dst - angle of src + 180). This is the inverse:
	// where `p`, standing beyond `dst`, is seen from the room `src` is in.
	static Vector2 ImageThrough(Line src, Line dst, Vector2 p)
	{
		double a = VectorAngle(dst.delta.x, dst.delta.y) - VectorAngle(src.delta.x, src.delta.y) + 180;
		return src.v1.p + Actor.RotateVector(p - dst.v2.p, -a);
	}

	// Does the straight walk from a to b go through the opening of line l?
	// `at` is how far along a..b (0..1) it crosses.
	static bool Crosses(Line l, Vector2 a, Vector2 b, double margin, out double at)
	{
		Vector2 d = l.delta;
		Vector2 r = b - a;
		double den = r.x * d.y - r.y * d.x;
		if (abs(den) < 0.001) return false;
		Vector2 w = l.v1.p - a;
		at = (w.x * d.y - w.y * d.x) / den;            // along a..b
		double u = (w.x * r.y - w.y * r.x) / den;      // along the line
		double m = margin / d.Length();
		return at > 0 && at < 1 && u > m && u < 1 - m;
	}

	// Is the way from `who` to the opening of `src`, heading for `img`, clear of walls?
	static bool ClearTo(Actor who, Line src, Vector2 img, double margin, out double ang)
	{
		double at;
		if (!Crosses(src, who.pos.xy, img, margin, at)) return false;
		Vector2 d = img - who.pos.xy;
		ang = VectorAngle(d.x, d.y);
		FLineTraceData data;
		who.LineTrace(ang, d.Length() * at - 1, 0, TRF_THRUACTORS, who.height / 2, 0, 0, data);
		return data.HitType == TRACE_HitNone;
	}

	// Where `target` appears to `who` through a hung door, if some door shows
	// it, and the line of that door on who's side. The engine's own sight
	// check does not look through these doors, so the way is checked on each
	// side of the door separately. This is sight only: the line may pass the
	// very edge of the opening, where `who` could not walk.
	static bool, Vector2, Line DoorImage(Actor who, Actor target)
	{
		Vector2 img;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor door;
		while (h && (door = AjarDoor(it.Next())))
		{
			if (!door.frame) continue;
			Line a = h.FindLine(door.frame.args[0]);
			Line b = h.FindLine(door.args[0]);
			if (!a || !b) continue;
			for (int i = 0; i < 2; i++)
			{
				Line src = i ? b : a;
				Line dst = i ? a : b;
				double ang, back;
				img = ImageThrough(src, dst, target.pos.xy);
				if (ClearTo(who, src, img, 2, ang)
					&& ClearTo(target, dst, ImageThrough(dst, src, who.pos.xy), 0, back))
					return true, img, src;
			}
		}
		return false, img, null;
	}
}

// Common base, so maps and tests can find every enemy.
class AjarEnemy : Actor
{
	Default
	{
		Monster;
		+NOBLOOD +DONTTHRUST +LOOKALLAROUND
	}
}

// What the monsters that work on doors share: finding the handler, judging
// whether a place can be walked to, and a marker to walk at.
class AjarWorker : AjarEnemy
{
	const REACH = 36;          // how far in front of an opening it stands
	Actor spot;                // marker to look at and walk to

	AjarHandler Handler() { return AjarHandler(EventHandler.Find("AjarHandler")); }

	bool SeesPlayer()
	{
		let p = players[consoleplayer].mo;
		return p && p.health > 0 && CheckSight(p);
	}

	// A point `dist` in front of a door opening (behind it if negative).
	// Openings always face their room: the front of the line is the room side.
	Vector2 Front(Line l, double dist)
	{
		Vector2 n = (l.delta.y, -l.delta.x);
		return (l.v1.p + l.v2.p) / 2 + n.Unit() * dist;
	}

	// Puts the marker there if this monster can see the place and walk to it
	// in a straight line: no step on the way higher than it can climb and no
	// drop it would not come back up (it cannot plan a way down into a pit,
	// across one, or round by stairs).
	bool CanReach(Vector2 at)
	{
		if (!spot) spot = Spawn("AjarLure", pos);
		Vector2 d = at - pos.xy;
		double len = d.Length();
		double z = pos.z;
		for (double done = 16; done < len + 16; done += 16)
		{
			Vector2 p = pos.xy + d * (min(done, len) / max(len, 1.));
			double pz = level.PointInSector(p).floorplane.ZAtPoint(p);
			if (abs(pz - z) > 24) return false;
			z = pz;
		}
		// nor through a squeeze, which no monster passes
		let si = level.CreateLineIdIterator(AjarHandler.SQUEEZE_ID);
		int li;
		double along;
		while ((li = si.Next()) >= 0)
			if (AjarSight.Crosses(level.lines[li], pos.xy, at, 0, along)) return false;
		spot.SetOrigin((at, z), false);
		return CheckSight(spot);
	}

	// One step towards the marker.
	void StepToSpot()
	{
		target = spot;
		A_Chase(null, null);
		// do not commit to one direction for long: it runs past things
		if (movecount > 2) movecount = 2;
	}

	override void OnDestroy()
	{
		if (spot) spot.Destroy();
		Super.OnDestroy();
	}
}

// Thief: the one monster of Ajar's own. It does what you do. It takes a door
// off its hinges or picks up one left leaning, carries it to another frame
// and hangs it there, swapping if that frame is taken; now and then it just
// walks through a hung door and carries on from the other side. It picks
// among the jobs open to it at random and keeps going until it is killed.
// Whatever it was carrying falls where it dies.
//
// Thing arguments: args[0] is the colour of a door it starts with on its
// back (put that door thing where the thief stands); args[1] = 1 keeps it
// from walking through doors, so it stays in the part of the level it is in.
//
// It only goes for things it can see and walk to. Taking a hung door down
// (or swapping it out) it does only while it can see you: that is the one
// job that can close a way behind someone's back. Picking up a leaning
// door, hanging one in an empty frame and walking through doors it does
// unwatched.
class AjarThief : AjarWorker
{
	const PATIENCE = 150;      // walk steps before it gives a job up
	const REST = 30;           // steps it keeps away from you after a job
	const FORGET = 350;        // tics before it will touch the same frame again
	AjarDoor loot;             // the door on its back
	AjarFrame jobFrame;        // a frame to work at, or
	AjarDoor jobDoor;          // a leaning door to pick up, or
	Line jobLine;              // an opening to walk through,
	AjarDoor jobLineDoor;      // which is open while this door hangs
	bool crossing, lined;
	AjarFrame lastFrame;       // where it worked last (left alone for a while)
	Actor avoid;               // a job it gave up on
	int lastTime, lastThrough;
	int steps;
	int testMode;              // smoke tests: 1 = nearest job, never through; 2 = always through

	Default
	{
		Radius 16;
		Height 52;
		Health 40;
		Speed 16;
		Mass 80;
		PainChance 0;
		SeeSound "skeleton/sight";
		DeathSound "skeleton/death";
		-DONTTHRUST
	}
	States
	{
	Spawn:
		AJTH A 8 A_ThiefLook();
		Loop;
	Walk:
		AJTH AABB 2 A_ThiefWalk();
		Loop;
	WalkLoot:
		AJTH EEFF 2 A_ThiefWalk();
		Loop;
	Work:
		AJTH C 35 A_ThiefFace();
		AJTH C 0 A_ThiefAct();
		Goto Spawn;
	Rest:
		AJTH AABB 2 A_ThiefRest();
		Loop;
	RestLoot:
		AJTH EEFF 2 A_ThiefRest();
		Loop;
	Death:
		AJTH D 6 A_Scream();
		AJTH D 0 A_ThiefDrop();
		AJTH D 0 A_NoBlocking();
		AJTH D -1;
		Stop;
	}

	void GoWalk()
	{
		steps = 0;
		target = spot;
		if (loot) SetStateLabel("WalkLoot"); else SetStateLabel("Walk");
	}

	void GoRest()
	{
		steps = 0;
		if (loot) SetStateLabel("RestLoot"); else SetStateLabel("Rest");
	}

	void GoIdle()
	{
		jobFrame = null;
		jobDoor = null;
		jobLine = null;
		jobLineDoor = null;
		crossing = false;
		target = null;
		SetStateLabel("Spawn");
	}

	void A_ThiefLook()
	{
		if (loot) frame = 4;
		let h = Handler();
		if (!h) return;
		if (lastFrame && level.time - lastTime > FORGET) lastFrame = null;
		bool seen = SeesPlayer();

		Array<AjarFrame> frames;      // frames to work at
		Array<AjarDoor> leaning;      // doors to pick up
		Array<Line> ways;             // openings to walk through
		Array<AjarDoor> wayDoors;

		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			if (f == lastFrame || f == avoid || (f.door && f.door.Stuck())) continue;
			// with a door: hang it, or swap; without: take the one that hangs there.
			// Anything that takes a hung door down needs the player watching.
			bool job = loot ? (!f.door || seen) : (f.door && seen);
			Line l = h.FindLine(f.args[0]);
			if (job && l && CanReach(Front(l, REACH))) frames.Push(f);
		}
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			if (d.carried || d.IsStray()) continue;      // a Stray door is nothing to a thief
			if (!d.frame)
			{
				if (!loot && d != avoid && CanReach(d.pos.xy)) leaning.Push(d);
				continue;
			}
			// a hung door can be walked through from either end
			for (int i = 0; i < 2; i++)
			{
				Line l = h.FindLine(i ? d.args[0] : d.frame.args[0]);
				if (l && CanReach(Front(l, REACH))) { ways.Push(l); wayDoors.Push(d); }
			}
		}

		int work = frames.Size() + leaning.Size();
		bool through;
		if (testMode == 1 || args[1]) through = false;       // args[1]: it stays where it is
		else if (testMode == 2) through = ways.Size() > 0;
		else through = ways.Size() > 0 && level.time - lastThrough > (work ? 250 : 100)
			&& (!work || random[AjarThief](0, 99) < 35);
		if (!through && !work) return;

		if (through)
		{
			int i = random[AjarThief](0, ways.Size() - 1);
			jobLine = ways[i];
			jobLineDoor = wayDoors[i];
			crossing = false;
			CanReach(Front(jobLine, REACH));                  // leaves the marker there
		}
		else
		{
			int pick = random[AjarThief](0, work - 1);
			if (testMode == 1)
			{
				// the nearest job, so the test is repeatable
				double best = 1e9;
				for (int i = 0; i < work; i++)
				{
					Actor a = i < frames.Size() ? Actor(frames[i]) : Actor(leaning[i - frames.Size()]);
					if (Distance2D(a) < best) { best = Distance2D(a); pick = i; }
				}
			}
			if (pick < frames.Size())
			{
				jobFrame = frames[pick];
				CanReach(Front(h.FindLine(jobFrame.args[0]), REACH));
			}
			else
			{
				jobDoor = leaning[pick - frames.Size()];
				CanReach(jobDoor.pos.xy);
			}
		}
		A_StartSound(SeeSound, CHAN_VOICE);
		GoWalk();
	}

	bool JobStillThere()
	{
		if (jobLine) return jobLineDoor && jobLineDoor.frame;
		if (jobDoor) return !jobDoor.frame && !jobDoor.carried;
		return jobFrame && (loot || jobFrame.door);
	}

	void A_ThiefWalk()
	{
		if (!JobStillThere() || ++steps > PATIENCE)
		{
			if (steps > PATIENCE)
			{
				if (jobLine) lastThrough = level.time;
				else avoid = jobFrame ? Actor(jobFrame) : Actor(jobDoor);
			}
			GoIdle();
			return;
		}
		if (jobLine && !crossing && Distance2D(spot) < 40)
		{
			crossing = true;
			lined = false;
		}
		if (crossing)
		{
			// Doom's chasing overshoots a doorway, so the last steps are walked
			// straight: first to the point in front of the opening, then in.
			Vector2 d = Front(jobLine, lined ? -24 : REACH) - pos.xy;
			if (!lined && d.Length() < 6)
			{
				lined = true;
				d = Front(jobLine, -24) - pos.xy;
			}
			else if (lined && d.Length() > 150)
			{
				// suddenly far from the opening: it has come out at the other end
				vel.xy = (0, 0);
				lastThrough = level.time;
				GoIdle();
				return;
			}
			angle = VectorAngle(d.x, d.y);
			vel.xy = d.Unit() * min(8., d.Length() / 2);
			return;
		}
		if (!jobLine && Distance2D(spot) < 40) { SetStateLabel("Work"); return; }
		StepToSpot();
	}

	void A_ThiefFace()
	{
		if (jobFrame) angle = AngleTo(jobFrame);
		else if (jobDoor) angle = AngleTo(jobDoor);
		A_StartSound("misc/chat2", CHAN_BODY);
	}

	void A_ThiefAct()
	{
		let h = Handler();
		target = null;
		bool ok = h && JobStillThere() && Distance2D(spot) <= 64;
		// taking a hung door down needs the player watching
		if (ok && jobFrame && jobFrame.door && (!SeesPlayer() || jobFrame.door.Stuck())) ok = false;
		if (!ok) { GoIdle(); return; }
		if (jobDoor)
		{
			loot = jobDoor;
			h.ThiefPicksUp(loot, self);
		}
		else
		{
			loot = h.ThiefUsesFrame(jobFrame, loot, self);
			lastFrame = jobFrame;
			lastTime = level.time;
		}
		jobDoor = null;
		jobFrame = null;
		avoid = null;
		bFrightened = true;
		GoRest();
	}

	// keep away from the player for a moment before the next job
	void A_ThiefRest()
	{
		let p = players[consoleplayer].mo;
		if (++steps > REST || !p)
		{
			bFrightened = false;
			GoIdle();
			return;
		}
		target = p;
		A_Chase(null, null);
		// A_Chase may have sent it back to idle
		if (InStateSequence(CurState, SpawnState))
		{
			if (loot) SetStateLabel("RestLoot"); else SetStateLabel("Rest");
		}
	}

	// One that stays where it is (args[1]) must not stray through a hung door
	// while running about either: a step that long was a door, so it is undone.
	Vector3 stayAt;
	override void Tick()
	{
		Super.Tick();
		if (!args[1] || health <= 0) return;
		if (stayAt != (0, 0, 0) && (pos.xy - stayAt.xy).Length() > 96)
		{
			SetOrigin(stayAt, false);
			vel.xy = (0, 0);
			angle += 180;
		}
		stayAt = pos;
	}

	void A_ThiefDrop()
	{
		let h = Handler();
		if (h && loot) h.DropDoor(loot, self);
		loot = null;
	}

	override void OnDestroy()
	{
		A_ThiefDrop();
		Super.OnDestroy();
	}
}

// Nailer: the thief's opposite. It walks to a hung door and nails it to its
// frame. A nailed door still opens onto its far side, but nobody can take it
// down or swap it, neither you nor a thief, until the nailer is dead; then
// the nails fall out of every door it nailed. With no door left to nail it
// comes for you with the hammer.
class AjarNailer : AjarWorker
{
	const PATIENCE = 120;
	AjarDoor job;
	int steps;

	Default
	{
		Radius 18;
		Height 56;
		Health 80;
		Speed 9;
		Mass 200;
		PainChance 60;
		MeleeRange 52;
		SeeSound "skeleton/sight";
		PainSound "skeleton/pain";
		DeathSound "skeleton/death";
	}
	States
	{
	Spawn:
		AJNL A 8 A_NailerLook();
		Loop;
	Walk:
		AJNL AABB 3 A_NailerWalk();
		Loop;
	Work:
		AJNL C 9 A_NailerFace();
		AJNL D 8 A_StartSound("skeleton/melee", CHAN_WEAPON);
		AJNL C 9;
		AJNL D 8 A_StartSound("skeleton/melee", CHAN_WEAPON);
		AJNL D 0 A_NailerNail();
		Goto Spawn;
	Hunt:
		AJNL AABB 3 A_NailerHunt();
		Loop;
	Melee:
		AJNL C 7 A_FaceTarget();
		AJNL D 7 A_CustomMeleeAttack(4 * random[AjarNailer](2, 5), "skeleton/melee", "skeleton/swing");
		Goto Hunt;
	Pain:
		AJNL A 4 A_Pain();
		Goto Spawn;
	Death:
		AJNL E 6 A_Scream();
		AJNL E 0 A_NailerDone();
		AJNL E 0 A_NoBlocking();
		AJNL E -1;
		Stop;
	}

	bool JobStillThere() { return job && job.frame && !job.nailer; }

	// the nearest hung door without nails that it can walk to
	AjarDoor FindJob()
	{
		let h = Handler();
		if (!h) return null;
		AjarDoor best;
		double bestDist = 1e9;
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			if (!d.frame || d.nailer) continue;
			Line l = h.FindLine(d.frame.args[0]);
			double dist = Distance2D(d.frame);
			if (l && dist < bestDist && CanReach(Front(l, REACH))) { best = d; bestDist = dist; }
		}
		if (best) CanReach(Front(h.FindLine(best.frame.args[0]), REACH));   // leaves the marker there
		return best;
	}

	void A_NailerLook()
	{
		job = FindJob();
		if (job)
		{
			steps = 0;
			A_StartSound(SeeSound, CHAN_VOICE);
			SetStateLabel("Walk");
		}
		else if (SeesPlayer())
		{
			steps = 0;
			target = players[consoleplayer].mo;
			SetStateLabel("Hunt");
		}
	}

	void A_NailerWalk()
	{
		if (!JobStillThere() || ++steps > PATIENCE) { job = null; target = null; SetStateLabel("Spawn"); return; }
		if (Distance2D(spot) < 40) { SetStateLabel("Work"); return; }
		StepToSpot();
	}

	void A_NailerFace()
	{
		if (job && job.frame) angle = AngleTo(job.frame);
	}

	void A_NailerNail()
	{
		let h = Handler();
		if (h && JobStillThere() && Distance2D(spot) <= 64) h.Nail(job, self);
		job = null;
		target = null;
	}

	// after the player, but a door to nail comes first
	void A_NailerHunt()
	{
		let p = players[consoleplayer].mo;
		if (!p || p.health <= 0 || (++steps % 12 == 0 && FindJob())) { target = null; SetStateLabel("Spawn"); return; }
		target = p;
		A_Chase("Melee", null);
	}

	void A_NailerDone()
	{
		let h = Handler();
		if (h) h.Unnail(self);
	}

	override void OnDestroy()
	{
		A_NailerDone();
		Super.OnDestroy();
	}
}

// Lodger: it lives in the empty frames and uses them as its own doors. While
// it is inside it cannot be seen or hurt. It comes out of an empty frame that
// has a view of you (the frame glows and knocks first), goes for you, and
// after a while or when hurt walks back into the nearest empty frame.
// A frame with a door in it is shut to the lodger: hang a door to plug it.
class AjarLodger : AjarWorker
{
	const OUT_STEPS = 110;     // hunting steps before it wants back in
	const PATIENCE = 100;
	AjarFrame hole;            // the frame it is coming out of or going back to
	int wait;                  // tics until it next tries to come out
	int steps;
	int hurtAt;                // health at which it turns back
	bool inside;
	bool awake;                // args[0]: sleeps until the player is this close to where it was placed

	Default
	{
		Radius 14;
		Height 60;
		Health 60;
		Speed 15;
		Mass 100;
		PainChance 255;
		MeleeRange 48;
		SeeSound "wolfss/sight";
		PainSound "skeleton/pain";
		DeathSound "skeleton/death";
	}
	States
	{
	Spawn:
		TNT1 A 5 A_LodgerWait();
		Loop;
	Knock:
		TNT1 A 12 A_LodgerKnock();
		TNT1 A 12 A_LodgerKnock();
		TNT1 A 12 A_LodgerKnock();
		TNT1 A 0 A_LodgerEmerge();
		Goto Spawn;
	Prowl:
		AJLG AABB 2 A_LodgerHunt();
		Loop;
	Melee:
		AJLG C 6 A_FaceTarget();
		AJLG D 6 A_CustomMeleeAttack(2 * random[AjarLodger](2, 5), "skeleton/melee", "skeleton/swing");
		AJLG A 8;
		Goto Prowl;
	Back:
		AJLG AABB 2 A_LodgerBack();
		Loop;
	Pain:
		AJLG A 3 A_Pain();
		Goto Prowl;
	Death:
		AJLG E 6 A_Scream();
		AJLG E 0 A_NoBlocking();
		AJLG E -1;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		GoInside(70);
	}

	void GoInside(int tics)
	{
		inside = true;
		wait = tics;
		hole = null;
		target = null;
		bInvisible = true;
		bSolid = false;
		bShootable = false;
		A_RemoveLight('knock');
	}

	Vector2 FrontOf(AjarFrame f)
	{
		Line l = Handler().FindLine(f.args[0]);
		return l ? Front(l, REACH) : f.pos.xy;
	}

	// inside: wait, then pick an empty frame the player can see
	void A_LodgerWait()
	{
		if (!inside) { SetStateLabel("Prowl"); return; }
		wait -= 5;
		let p = players[consoleplayer].mo;
		if (wait > 0 || !Handler() || !p || p.health <= 0) return;
		if (args[0] && !awake)
		{
			if ((p.pos.xy - SpawnPoint.xy).Length() > args[0]) return;
			awake = true;
		}
		if (!spot) spot = Spawn("AjarLure", pos);

		Array<AjarFrame> holes;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			if (f.door) continue;
			Vector2 at = FrontOf(f);
			double d = (at - p.pos.xy).Length();
			if (d < 96 || d > 1024) continue;
			spot.SetOrigin((at, f.pos.z), false);
			if (p.CheckSight(spot)) holes.Push(f);
		}
		if (!holes.Size()) { wait = 35; return; }
		hole = holes[random[AjarLodger](0, holes.Size() - 1)];
		SetOrigin((FrontOf(hole), hole.pos.z), false);
		angle = AngleTo(p);
		SetStateLabel("Knock");
	}

	void A_LodgerKnock()
	{
		A_StartSound("misc/chat2", CHAN_BODY, 0, 1.0, ATTN_NORM);
		if (Handler()) Handler().LodgerKnocks();
		A_AttachLight('knock', DynamicLight.PulseLight, 0xD8FFD0, 24, 72, 0, (0, 0, 48), 0.4);
	}

	void A_LodgerEmerge()
	{
		A_RemoveLight('knock');
		// plugged while it was knocking, or somebody is standing in the way
		if (!hole || hole.door || !TestMobjLocation()) { GoInside(70); return; }
		inside = false;
		bInvisible = false;
		bSolid = true;
		bShootable = true;
		steps = 0;
		hurtAt = health - 20;
		target = players[consoleplayer].mo;
		A_StartSound(SeeSound, CHAN_VOICE);
		SetStateLabel("Prowl");
	}

	// the nearest empty frame it can walk to
	AjarFrame WayBack()
	{
		AjarFrame best;
		double bestDist = 1e9;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			double d = Distance2D(f);
			if (!f.door && d < bestDist && CanReach(FrontOf(f))) { best = f; bestDist = d; }
		}
		if (best) CanReach(FrontOf(best));       // leaves the marker there
		return best;
	}

	void A_LodgerHunt()
	{
		let p = players[consoleplayer].mo;
		if (++steps > OUT_STEPS || health <= hurtAt)
		{
			hole = WayBack();
			if (hole) { steps = 0; SetStateLabel("Back"); return; }
			// every frame in reach is plugged: it is shut out, and stays out
			steps = OUT_STEPS - 10;
			hurtAt = -1000;
		}
		if (p) target = p;
		A_Chase("Melee", null);
	}

	void A_LodgerBack()
	{
		if (!hole || hole.door || ++steps > PATIENCE)
		{
			steps = 0;
			hurtAt = health - 20;
			SetStateLabel("Prowl");
			return;
		}
		if (Distance2D(spot) < 40)
		{
			A_StartSound("misc/chat2", CHAN_BODY);
			GoInside(random[AjarLodger](60, 130));
			SetStateLabel("Spawn");
			return;
		}
		StepToSpot();
	}
}

// --- ordinary Doom monsters and doors ------------------------------------
// Doom's monsters neither see nor chase through a hung door. Every one of
// them carries an AjarSense. While its monster has no straight view of the
// player but can see them through a door, the monster is given a lure to
// chase instead: an unseen marker standing where the player appears to be,
// beyond the door. Walking at it takes the monster through the door, where
// it sees the real player and goes back to normal.
class AjarLure : Actor
{
	Default
	{
		Health 1000;
		// Not +INVISIBLE: monsters refuse to chase invisible targets. It has no sprite.
		+NOBLOCKMAP +NOGRAVITY +SHOOTABLE +NODAMAGE +NOTARGET
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

class AjarSense : Inventory
{
	Actor lure;
	Line via;           // the door it is making for
	int viaUntil;       // ...and until when, if it does not see you through it again
	Vector2 viaImg;     // where you appeared through it
	bool viaStraight;   // it can walk straight at that, through the opening
	Vector3 lastPos;
	bool muted;         // it is after its lure, and must not attack it
	double ownRange;    // its melee range, kept while muted

	// An opening is 64 wide and as high as a door.
	bool Fits() { return owner.radius <= 31 && owner.height <= 96; }

	// The player has just left through the door at `l`. A monster that was
	// after them and can see that door goes the same way.
	void Follow(Line l, Actor p)
	{
		if (!owner || owner.health <= 0 || !Fits()) return;
		if (owner.target != p && !(lure && owner.target == lure)) return;
		if (!lure) lure = Spawn("AjarLure", owner.pos);
		Vector2 n = (l.delta.y, -l.delta.x).Unit();
		Vector2 at = (l.v1.p + l.v2.p) / 2 + n * 24;
		lure.SetOrigin((at, l.frontsector.floorplane.ZAtPoint(at)), false);
		if (!owner.CheckSight(lure)) return;
		via = l;
		viaUntil = level.time + 1050;
		viaStraight = false;
	}

	override void DoEffect()
	{
		Super.DoEffect();
		if (!owner || owner.health <= 0) return;
		let p = players[consoleplayer].mo;
		if (p && p.health > 0 && (level.time + owner.SpawnTime) % 4 == 0) Look(p);
		if (lure && owner.target == lure && via) Steer();
		else Unmute();
	}

	// Four times a second: is there a door to make for?
	void Look(Actor p)
	{
		bool luring = lure && owner.target == lure;
		// Leave it alone while it is busy with anything else (another monster).
		if (!luring && owner.target && owner.target != p) return;

		// A jump since the last look means it has gone through a door.
		bool jumped = via && (owner.pos.xy - lastPos.xy).Length() > 96;
		lastPos = owner.pos;

		if (jumped || !Fits() || owner.CheckSight(p)) via = null;
		else
		{
			bool seen;
			Vector2 img;
			Line src;
			[seen, img, src] = AjarSight.DoorImage(owner, p);
			// Having seen you through a door it keeps making for that door for
			// a while: the view through an opening is lost after a step or two.
			if (seen)
			{
				double ang;
				via = src;
				viaUntil = level.time + 1050;
				viaImg = img;
				viaStraight = AjarSight.ClearTo(owner, src, img, owner.radius, ang);
			}
			else
			{
				viaStraight = false;
				if (level.time > viaUntil) via = null;
			}
		}
		if (!via)
		{
			if (luring) owner.target = p;
			return;
		}
		if (!lure) lure = Spawn("AjarLure", owner.pos);
		bool idle = !owner.target;
		owner.target = lure;
		Steer();
		if (idle && owner.SeeState)
		{
			// wake it as if it had seen the player (it needs its target first)
			owner.A_StartSound(owner.SeeSound, CHAN_VOICE);
			owner.SetState(owner.SeeState);
		}
	}

	// Every tic while it is making for a door: where its lure stands, and
	// the last steps into the opening.
	void Steer()
	{
		// The lure is only something to walk at. Doom's monsters attack what
		// they chase: bite it when they reach it, shoot it when they see it.
		// That showed as a monster busy with a spot beside the door.
		if (!muted)
		{
			muted = true;
			ownRange = owner.meleerange;
		}
		owner.meleerange = -10000;      // never in reach
		owner.reactiontime = 4;         // never ready to shoot
		owner.bJustHit = false;         // nor shooting back at once
		if (owner.SeeState && ((owner.MeleeState && owner.InStateSequence(owner.CurState, owner.MeleeState))
			|| (owner.MissileState && owner.InStateSequence(owner.CurState, owner.MissileState))))
			owner.SetState(owner.SeeState);

		// With a straight walk through the opening the lure stands where you
		// appear. Otherwise (a slant, or the view is lost) it first stands
		// square in front of the door, and goes beyond it once the monster is
		// about in line. Doom's chase walks in eight directions and in whole
		// steps, so it never lines up exactly: in front of the opening the
		// monster is slid sideways onto the middle line, which a demon, 60
		// wide in a 64 opening, needs to within 2 units.
		Vector2 to = viaImg;
		if (!viaStraight)
		{
			Vector2 mid = (via.v1.p + via.v2.p) / 2;
			Vector2 along = via.delta.Unit();
			Vector2 n = (along.y, -along.x);
			Vector2 off = owner.pos.xy - mid;
			if (off dot n < 0) n = -n;
			double side = off dot along;
			double ahead = off dot n;
			bool lined = abs(side) < 16 && ahead < 128;
			to = lined ? mid - n * 40 : mid + n * (owner.radius + 28);
			if (ahead < 128 && abs(side) < 24 && abs(side) > 0.25)
				owner.TryMove(owner.pos.xy - along * clamp(side, -2, 2), 1);
		}
		lure.SetOrigin((to, owner.pos.z), false);
	}

	void Unmute()
	{
		if (!muted) return;
		muted = false;
		owner.meleerange = ownRange;
		owner.reactiontime = 0;
	}

	override void OnDestroy()
	{
		if (lure) lure.Destroy();
		Super.OnDestroy();
	}
}
