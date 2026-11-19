// Sight lines (MAP13; the test map OPT, tools/map_optics.py).
//
// What a hung door lets through besides the player.
//  * AjarTarget thing (ajarmap.target): something on a wall that is shot.
//    args[0] = the sector tag of the steel door it opens (Door_Open),
//    args[1] = 0 if any shot of the player's sets it off, 1 if only the
//    emitter's beam does (a sensor). The engine carries a bullet through a
//    hung door, so the player may stand anywhere a door shows it.
//  * AjarEmitter thing (ajarmap.emitter): a fixed lamp that fires an
//    AjarBeam along its angle when activated (its button's line calls
//    Thing_Activate). A beam is a missile, and a missile keeps its line
//    through a door: where it comes out is the player's choice of frame.
//  * AjarWatch thing (ajarmap.watch): the middle of a room that is some
//    door's far side. args[0], args[1] = half the room's size along x and y,
//    args[2] = the far side's line id. Doom's monsters neither see nor aim
//    through a door (the engine's sight stops at one), so this does it for
//    those in such a room: while that door hangs, they fire through it at
//    the player standing before its frame, or, where its frame faces the
//    frame of another watched room's door, at what is in that room.
//    A monster fires its own attack at an AjarAim, a thing put where the
//    victim would be if the door were a hole in the wall.

class AjarBeam : Actor
{
	Default
	{
		Radius 6;
		Height 8;
		Speed 25;
		Damage 10;
		Projectile;
		RenderStyle "Add";
		DamageType "Beam";
		SeeSound "weapons/plasmaf";
		DeathSound "weapons/plasmax";
	}
	States
	{
	Spawn:
		PLSS AB 3 Bright;
		Loop;
	Death:
		PLSE A 3 Bright A_Glance();
		PLSE BCDE 3 Bright;
		Stop;
	}

	Vector3 flew;      // its velocity while it last moved: gone by the time it has struck

	override void Tick()
	{
		if (vel.xy.Length() > 1) flew = vel;
		Super.Tick();
	}

	// A beam that strikes a mirror (a Line_Mirror wall) goes on from it as
	// light does. The engine does not do this for any shot.
	void A_Glance()
	{
		Line l = BlockingLine;
		if (!l || l.special != 182 /* Line_Mirror */) return;
		Vector2 e = l.delta.Unit();
		Vector2 n = (e.y, -e.x);                   // into the room
		Vector2 v = flew.xy - 2 * (flew.xy dot n) * n;
		// from the very point of the glass its middle was flying at: a beam is
		// 12 wide, and what struck was its edge
		Vector2 d = flew.xy.Unit(), w = l.v1.p - pos.xy, at = pos.xy;
		double det = d.x * e.y - d.y * e.x;
		if (abs(det) > 0.001) at += d * ((w.x * e.y - w.y * e.x) / det);
		let b = AjarBeam(Spawn("AjarBeam", (at + v.Unit() * 14, pos.z)));
		b.target = target;
		b.angle = VectorAngle(v.x, v.y);
		b.vel = (v.x, v.y, flew.z);
		b.A_StartSound(b.SeeSound, CHAN_VOICE);
	}
}

class AjarEmitter : Actor
{
	int ready;
	Default
	{
		+NOBLOCKMAP +NOGRAVITY
	}
	States
	{
	Spawn:
		AJEM A -1;       // a lamp on a stand (gfx_institute2.emitter_lamp): its lens is where the beam starts
		Stop;
	}

	override void Activate(Actor activator)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (level.maptime < ready)
		{
			if (h && activator) h.Say("The emitter is charging.");
			return;
		}
		ready = level.maptime + 52;
		Fire();
	}

	AjarBeam Fire()
	{
		let b = AjarBeam(Spawn("AjarBeam", pos + (cos(angle) * 20, sin(angle) * 20, 40)));
		b.target = self;
		b.angle = angle;
		b.Vel3DFromAngle(b.speed, angle, 0);
		b.A_StartSound(b.SeeSound, CHAN_VOICE);
		return b;
	}
}

class AjarTarget : Actor
{
	bool done;
	int told;
	Default
	{
		Radius 10;
		Height 20;
		Health 1000000;
		Mass 1000000;
		+SHOOTABLE +NOBLOOD +NOGRAVITY +DONTTHRUST +NEVERTARGET
	}
	States
	{
	Spawn:
		AJTG A -1;
		Stop;
	Lit:
		AJTG B -1 Bright;
		Stop;
	Sensor:
		AJTG C -1;
		Stop;
	SensorLit:
		AJTG D -1 Bright;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		if (args[1]) SetStateLabel("Sensor");
		bOnlyVisibleInMirrors = args[2] != 0;      // ajarmap.target(unseen=True), until it is set off
	}

	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		if (done) return 0;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		bool beam = inflictor is "AjarBeam", player = source && source.player;
		if (args[1] ? beam : player)
		{
			if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST target %d set off t=%d by=%s of=%s mod=%s", args[0], level.maptime, inflictor ? inflictor.GetClassName() : 'none', source ? source.GetClassName() : 'none', mod);
			Trigger(h);
		}
		else if (args[1] && player && h && level.maptime > told)
		{
			told = level.maptime + 105;
			h.Say("The sensor takes no notice of that.\nIt is waiting for the beam.");
		}
		return 0;
	}

	void Trigger(AjarHandler h)
	{
		done = true;
		bOnlyVisibleInMirrors = false;
		if (args[1]) SetStateLabel("SensorLit");
		else SetStateLabel("Lit");
		A_StartSound("switches/normbutn", CHAN_AUTO, 0, 1, ATTN_NONE);
		level.ExecuteSpecial(11 /* Door_Open */, null, null, false, args[0], 32);
		if (h && args[1]) h.Say("The beam is on the sensor.\nSteel doors open.");
		else if (h) h.Say("Hit. A steel door opens.");
	}
}

class AjarWatch : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
	bool Holds(Actor a) { return abs(a.pos.x - pos.x) < args[0] && abs(a.pos.y - pos.y) < args[1]; }
}

// Where a monster aims when it fires through a door, and what the checks
// of sight stand on. Nobody can shoot it, so whoever fired at it stops.
class AjarAim : Actor
{
	Default
	{
		Radius 4;
		Height 8;
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A 105;
		Stop;
	Post:
		TNT1 A 280;
		Stop;
	Stay:
		TNT1 A -1;
		Stop;
	}
}

extend class AjarHandler
{
	int opticsKnown;              // 0: not looked yet; 1: the level has no watched room; 2: it has
	Array<AjarWatch> watches;
	AjarAim eyeSpot, markSpot;
	int aimFail;                  // why the last AimThrough said no (for the tests)
	int volleys;                  // how many times a monster has fired through a door (for the tests)

	// A point in the space before the portal line `a`, as it lies in the
	// space before `b` once a is joined to b (the engine's own rule: turned
	// half round, a's first end on b's second).
	Vector3 PortalMap(Line a, Line b, Vector3 p)
	{
		Vector2 ea = a.delta.Unit(), eb = b.delta.Unit();
		Vector2 na = (ea.y, -ea.x), nb = (eb.y, -eb.x);
		Vector2 r = p.xy - a.v1.p;
		Vector2 q = b.v1.p + eb * (b.delta.Length() - (r dot ea)) - nb * (r dot na);
		double dz = b.frontsector.floorplane.ZatPoint(b.v1.p) - a.frontsector.floorplane.ZatPoint(a.v1.p);
		return (q.x, q.y, p.z + dz);
	}

	// Where the straight way from p to q crosses the opening of line l,
	// keeping `margin` from its jambs.
	bool, Vector2 CrossOpening(Vector2 p, Vector2 q, Line l, double margin = 10)
	{
		Vector2 d = q - p, e = l.delta, w = l.v1.p - p;
		double det = d.x * e.y - d.y * e.x;
		if (abs(det) < 0.001) return false, (0, 0);
		double t = (w.x * e.y - w.y * e.x) / det;          // along p-q
		double u = (w.x * d.y - w.y * d.x) / det;          // along the line
		double m = margin / e.Length();
		if (t <= 0 || t >= 1 || u < m || u > 1 - m) return false, (0, 0);
		return true, p + d * t;
	}

	void PutSpot(AjarAim s, Vector2 at)
	{
		s.SetOrigin((at.x, at.y, 0), false);
		s.SetZ(s.floorz + 32);
	}

	// Can `s` hit `v` by the doors ins[i] -> outs[i], taken in turn? If so,
	// also where s has to aim: v's place as the first door shows it.
	bool, Vector3 AimThrough(Actor s, Actor v, Array<Line> ins, Array<Line> outs)
	{
		int n = ins.Size();
		if (!eyeSpot) { eyeSpot = AjarAim(Actor.Spawn("AjarAim")); eyeSpot.SetStateLabel("Stay"); }
		if (!markSpot) { markSpot = AjarAim(Actor.Spawn("AjarAim")); markSpot.SetStateLabel("Stay"); }
		Array<double> tx, ty, tz;
		tx.Resize(n + 1); ty.Resize(n + 1); tz.Resize(n + 1);
		tx[n] = v.pos.x; ty[n] = v.pos.y; tz[n] = v.pos.z;
		for (int i = n - 1; i >= 0; i--)
		{
			Vector3 back = PortalMap(outs[i], ins[i], (tx[i + 1], ty[i + 1], tz[i + 1]));
			tx[i] = back.x; ty[i] = back.y; tz[i] = back.z;
		}
		Vector2 from = s.pos.xy;
		Actor eye = s;
		for (int i = 0; i < n; i++)
		{
			Vector2 to = (tx[i], ty[i]);
			bool ok; Vector2 c;
			[ok, c] = CrossOpening(from, to, ins[i]);
			if (!ok) { aimFail = 10 + i; return false, (0, 0, 0); }
			Vector2 dir = (to - from).Unit();
			PutSpot(markSpot, c - dir * 20);
			if (!eye.CheckSight(markSpot, SF_IGNOREVISIBILITY)) { aimFail = 20 + i; return false, (0, 0, 0); }
			Vector3 c3 = PortalMap(ins[i], outs[i], (c.x, c.y, 0));
			Vector2 next = (tx[i + 1], ty[i + 1]);
			from = c3.xy + (next - c3.xy).Unit() * 20;
			PutSpot(eyeSpot, from);
			eye = eyeSpot;
		}
		if (!eye.CheckSight(v)) { aimFail = 30; return false, (0, 0, 0); }
		aimFail = 0;
		return true, (tx[0], ty[0], tz[0]);
	}

	// The frame line the door with this far side hangs in, or null.
	Line HungIn(int farLine)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
			if (d.args[0] == farLine && d.frame && !d.IsPair()) return FindLine(d.frame.args[0]);
		return null;
	}

	bool FiresThroughDoors(Actor a)
	{
		if (!a.bIsMonster || a.health <= 0 || !a.MissileState) return false;
		if (a is "Revenant" || a is "Archvile" || a is "PainElemental" || a is "LostSoul") return false;   // a homing missile turns back for its mark; the others have nothing that flies straight
		return !a.InStateSequence(a.CurState, a.MissileState) && !a.InStateSequence(a.CurState, a.ResolveState("Pain"));
	}

	void FireAt(Actor a, Vector3 at)
	{
		let aim = Actor.Spawn("AjarAim", at);
		a.target = aim;
		a.goal = null;
		a.SetState(a.MissileState);
		volleys++;
	}

	// A monster sees through a door only from where the door, and what is
	// beyond it, are in one line: it walks to such a place. `seen` is the
	// thing to line up with, as the door `far` shows it.
	void TakePost(Actor a, AjarWatch w, Line far, Vector2 seen)
	{
		Vector2 c = far.v1.p + far.delta / 2;
		Vector2 dir = (c - seen).Unit();
		double near = 0, reach = 0;               // the stretch of that line that is well inside the room
		for (double d = 16; d < 2048; d += 16)
		{
			Vector2 q = c + dir * d;
			bool inside = abs(q.x - w.pos.x) < w.args[0] - 40 && abs(q.y - w.pos.y) < w.args[1] - 40;
			if (inside && !near) near = d;
			if (inside) reach = d;
			else if (near) break;
		}
		if (!near) return;
		Vector2 at = c + dir * frandom[AjarOptics](near, reach);
		let post = Actor.Spawn("AjarAim", (at.x, at.y, a.pos.z));
		post.SetStateLabel("Post");
		a.goal = post;
		a.target = post;
		if (!a.InStateSequence(a.CurState, a.SeeState)) a.SetState(a.SeeState);
	}

	// Does the player stand where the door hung in `fl` shows them?
	bool BeforeFrame(Actor mo, Line fl, Line far)
	{
		if (!mo || mo.health <= 0) return false;
		Vector2 c = fl.v1.p + fl.delta / 2;
		if ((mo.pos.xy - c).Length() > 1200) return false;
		Vector3 seen = PortalMap(fl, far, mo.pos);
		Vector2 fc = far.v1.p + far.delta / 2, e = far.delta.Unit();
		Vector2 r = seen.xy - fc;
		// within the widest angle the opening gives, and nothing in the way on the player's side
		if (abs(r dot e) > 32 + 2 * abs(r.x * e.y - r.y * e.x)) return false;
		if (!eyeSpot) return true;
		PutSpot(eyeSpot, c + (mo.pos.xy - c).Unit() * 24);
		return eyeSpot.CheckSight(mo);
	}

	void OpticsTick(Actor mo)
	{
		if (!opticsKnown)
		{
			opticsKnown = 1;
			let wi = ThinkerIterator.Create("AjarWatch");
			AjarWatch w;
			while (w = AjarWatch(wi.Next())) { watches.Push(w); opticsKnown = 2; }
		}
		if (opticsKnown < 2 || level.maptime % 8) return;
		Array<Line> ins, outs;
		for (int i = 0; i < watches.Size(); i++)
		{
			AjarWatch w = watches[i];
			Line far = FindLine(w.args[2]), fl = HungIn(w.args[2]);
			if (!far || !fl) continue;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (!w.Holds(a) || !FiresThroughDoors(a) || random[AjarOptics](0, 255) > 40) continue;
				bool ok, lineUp; Vector3 at;
				Vector2 seen;
				if (BeforeFrame(mo, fl, far)) { lineUp = true; Vector3 pv = PortalMap(fl, far, mo.pos); seen = pv.xy; }
				ins.Clear(); outs.Clear();
				ins.Push(far); outs.Push(fl);
				aimFail = -1;
				if (mo && mo.health > 0 && lineUp) [ok, at] = AimThrough(a, mo, ins, outs);
				int failP = aimFail;
				aimFail = -1;
				if (ok) { FireAt(a, at); continue; }
				// another watched room, whose door's frame this one faces
				for (int k = 0; k < watches.Size() && !ok; k++)
				{
					AjarWatch o = watches[k];
					Line far2 = FindLine(o.args[2]), fl2 = HungIn(o.args[2]);
					if (o == w || !far2 || !fl2) continue;
					// the other frame's middle, as this door shows it: in line with this door, or the two do not face
					Vector3 mv = PortalMap(fl, far, (fl2.v1.p.x + fl2.delta.x / 2, fl2.v1.p.y + fl2.delta.y / 2, 0));
					Vector2 mid = mv.xy;
					if (abs((mid - far.v1.p - far.delta / 2) dot far.delta.Unit()) > 24) continue;
					if (!lineUp) { lineUp = true; seen = mid; }
					ins.Clear(); outs.Clear();
					ins.Push(far); outs.Push(fl);
					ins.Push(fl2); outs.Push(far2);
					let vi = ThinkerIterator.Create("Actor");
					Actor v;
					int tries = 0;
					while (!ok && tries < 6 && (v = Actor(vi.Next())))
					{
						if (!v.bIsMonster || v.health <= 0 || !o.Holds(v)) continue;
						tries++;
						[ok, at] = AimThrough(a, v, ins, outs);
					}
				}
				if (ok) FireAt(a, at);
				else if (lineUp && !a.goal) TakePost(a, w, far, seen);
			}
		}
	}

	// --- MAP=OPT MODE=1..3 tools/smoke.sh ---------------------------------
	Actor OptOne(class<Actor> cls)
	{
		let it = ThinkerIterator.Create(cls);
		return Actor(it.Next());
	}

	void OptReport(int t, Actor baron, Actor fatso, Actor mo)
	{
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d volleys=%d baron=%d fatso=%d player=%d", t, volleys, baron ? baron.health : 0, fatso ? fatso.health : 0, mo.health);
	}

	void OpticsScript(Actor mo, int t, int mode)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		Actor baron = OptOne("BaronOfHell"), fatso = OptOne("Fatso");
		AjarTarget shot, sensor;
		let ti = ThinkerIterator.Create("AjarTarget");
		AjarTarget x;
		while (x = AjarTarget(ti.Next())) { if (x.args[1]) sensor = x; else shot = x; }
		let em = AjarEmitter(OptOne("AjarEmitter"));
		OptReport(t, baron, fatso, mo);
		if (mode == 1)
		{
			// the beam: RED in the frame that faces nothing, then in the one that faces a leaf
			mo.player.cheats |= CF_GODMODE;
			if (t == 20) { Take(mo, 1); Pose(mo, 320, 470, 0, 90); FindFrame(103).Activate(mo); Check("redHung", !carried && FindFrame(103).door != null); }
			if (t == 22) { a.Used(mo); Pose(mo, 580, 256, 0, 0); FindFrame(102).Activate(mo); }
			if (t == 24) { b.Used(mo); Pose(mo, 60, -240, 0, 180); FindFrame(104).Activate(mo); Check("pairJoined", !carried && !a.Shut() && !b.Shut()); }
			if (t == 26) { Pose(mo, 100, 100, 0, 90); em.Activate(mo); }
			if (t == 160) Check("beamIntoTheWallDoesNothing", !sensor.done);
			if (t == 162) { Take(mo, 1); Pose(mo, 60, 256, 0, 180); FindFrame(101).Activate(mo); Check("redFacesTheLeaf", !carried && FindFrame(101).door != null); }
			if (t == 164) { Pose(mo, 100, 100, 0, 90); em.Activate(mo); }
			if (t > 164 && t < 300 && t % 6 == 0)
			{
				Actor beam = OptOne("AjarBeam");
				if (beam) Console.Printf("AJARTEST beam t=%d at (%.0f,%.0f,%.0f)", t, beam.pos.x, beam.pos.y, beam.pos.z);
			}
			if (t == 300) Check("beamOnSensorThroughTwoDoors", sensor.done);
			if (t == 301) Check("sensorOpensItsDoor", FindLine(302).backsector.CenterCeiling() > 40 || FindLine(302).frontsector.CenterCeiling() > 40);
		}
		if (mode == 2)
		{
			// a bullet through GREEN, and what the baron in there does about it
			if (t == 20) { Take(mo, 3); Pose(mo, 60, 256, 0, 180); FindFrame(101).Activate(mo); Check("greenHung", !carried && FindFrame(101).door != null); }
			if (t == 22) Pose(mo, 300, 256, 0, 180);
			if (t == 24) Check("targetNotYetShot", !shot.done);
			if (t == 25) mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff");
			if (t == 27) Check("bulletThroughDoorHitsTarget", shot.done);
			if (t == 28) Check("targetOpensItsDoor", FindLine(301).backsector.CenterCeiling() > 40 || FindLine(301).frontsector.CenterCeiling() > 40);
			if (t == 400) Check("baronFiredThroughDoor", volleys > 0);
			if (t == 400) Check("andHitThePlayer", mo.health < 100);
			if (t == 400) Check("sensorIgnoresBullets", !sensor.done);
		}
		if (mode == 3)
		{
			// GREEN and BLUE in the two frames that face each other, the player out of the way
			mo.player.cheats |= CF_GODMODE;
			if (t == 20) { Take(mo, 3); Pose(mo, 60, 256, 0, 180); FindFrame(101).Activate(mo); }
			if (t == 22) { Take(mo, 2); Pose(mo, 580, 256, 0, 0); FindFrame(102).Activate(mo); Check("bothHung", !carried && FindFrame(101).door && FindFrame(102).door); }
			if (t == 24) Pose(mo, 60, -100, 0, 90);
			if (t == 700) Check("theyFired", volleys > 1);
			if (t == 700) Check("baronHurt", baron == null || baron.health < 1000);
			if (t == 700) Check("fatsoHurt", fatso == null || fatso.health < 600);
		}
	}
}
