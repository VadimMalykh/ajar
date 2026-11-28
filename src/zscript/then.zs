// Then and now (the lab THEN: tools/map_then.py, tools/ajarthen.py; PLAN.md,
// "The then and now lab"). The tests: thentest.zs.
//
// A place built twice: NOW, and THEN forty years before, the same plan shifted
// by a fixed offset (AjarThen, thing 20180: args[0], args[1] the shift from NOW
// to THEN; it stands in NOW). "The same spot at the other time" is a point
// plus or minus the shift; a point is THEN if it lies past half the shift.
//
// The clocked door (AjarDoor colour 10; ajar.zs's Hang, Unhang, UseFrame call
// the AjarHandler functions below): a Pair whose second leaf is its shadow
// (args[3] 3, never seen leaning). Hung in frame F, its shadow hangs in F's
// twin (the frame at F's spot plus or minus the shift), and the two frames
// lead to each other both ways (the Pair's own links). Taken from either
// frame, both leaves come down and the player holds the door; so too when a
// carried door is swapped in at either frame (it hangs in that one frame).
// A frame with no twin, or whose twin holds another door, does not take it.
//
// Long causes: an AjarThenCause (20181) is a fixture THEN with 2 or 3
// settings, stepped on by USE on its lever (Thing_Activate on its tid) or set
// by shooting an AjarThenTarget (20182). A setting puts NOW in a state, at
// once, one way (nothing NOW changes a cause):
//   * the NOW sectors tagged args[1] go to their heights for the setting (UDMF
//     user_f<n> floors and user_c<n> ceilings, n the setting; user_floors and
//     user_ceils say which are given) over MOVE_TICS. One with user_hold does
//     not bring its ceiling down while anything stands in it, and the cause's
//     openings wait until its closings are done (one hole at a time). One with
//     user_raised shows that flat while its floor stands over its setting 0
//   * the basin tagged args[2] (water.zs) stands args[3] over its floor in
//     setting 1 and over, dry in 0, reached over MOVE_TICS
//   * things with tid HIDDEN_TID + its tid (what lies in a pit a heap covers) are
//     there only in setting 0, once its sectors are back
// THEN shows it: AjarThenEmitter (20183) a beam along args[1] (setting 1) or
// args[2] (setting 2); AjarThenBelt (20184) runs its belt (sector tag args[1],
// args[2] - 128 and args[3] - 128 units a tic along x and y) in setting 1.
//
// A colour door joins places, never times (Vadim, 2026-11-26): its far side is
// built at both times (ajarthen.Times.far: line id n NOW, n + THEN_ID THEN),
// and hung in a frame it opens on the copy at that frame's time; the copy at
// the other time stays shut. Hang sets args[0] to that copy (FarAt), so all
// that asks where a hung door leads (sight, shots, monsters following) is told
// the truth; Unhang gives it back its own (ownFar, NOW's). A frame with no
// twin is a frame at its own time like any other.
//
// Company: a monster that dies THEN leaves its old corpse at the same spot NOW
// (its last death frame, pale, not solid). A monster alive THEN while no door
// joins the two times (the clocked door hung; a colour door never does) is
// shown NOW as that corpse, where it stood when the last link came down; when
// a link is made again the corpse goes. Such a stand-in fades in and out over
// AjarThenCorpse.FADE tics; one of a monster dead THEN is there at once, and
// so are the stand-ins made at the level's first tic (MAP23: the times are
// apart from the start). When a monster that has a stand-in dies THEN, the
// stand-in becomes its corpse, moved to where it died (never two for one). A
// monster raised THEN (WorldThingRevived) loses its bones for good: they stand
// in for it while the times are apart, and fade while they are joined. Each
// corpse keeps the Mass and radius of its monster (kennel.zs weighs them and
// makes a big one's a step).
//
// Music by time: the level's piece for THEN while the player is THEN (THEN_MUSIC,
// MAP21's, unless the level names its own: SetThenMusic, MAP22's map22.zs), the
// level's own (mapinfo) NOW; the lever (AjarThenMusic, 20185) turns the switching
// off and on again.
//
// The times joined: `joinedAt` is the level's tic at which some door first
// joined the two times (Linked: the clocked door hung), -1 until then. MAP22's
// turn (map22.zs; AjarAmbush cause 64, ajar.zs: JoinedDue).
//
// Three times (the three times lab BEFORE: tools/map_before.py, beforetest.zs;
// PLAN.md, "The three times lab"). With args[2] 3 the AjarThen thing names a
// third time, BEFORE, ten years before THEN, at twice the shift (TimeOf: NOW 0,
// THEN 1, BEFORE 2). A frame or far side BEFORE has the line id of NOW's + 2 x
// THEN_ID, and a colour door hung BEFORE opens on its far side BEFORE. The
// ten-year door (AjarDoor colour 11) is a second clocked door: it joins a
// frame THEN to the same frame BEFORE as the clocked door joins NOW and THEN,
// and neither hangs at a time its clock does not reach (ClockReaches). Both
// hung, NOW, THEN and BEFORE are a chain. A cause BEFORE moves every sector
// with its tag, which is THEN's and NOW's (and BEFORE's own, to show it).
// Company: a monster alive at an earlier time shows at each later time as its
// old corpse while no chain of hung clocked doors joins the two (Joined); one
// killed BEFORE leaves a corpse THEN and NOW. BEFORE has its own music
// (BEFORE_MUSIC). With two times all of this is as before.
//
// A door left hanging (the old door lab, the same map; PLAN.md, "The old door lab"). With args[3] 1 the AjarThen
// thing switches on the rule (ajarthen.Times(old=True)); every other map is as before. A colour door (RED .. PINK)
// hung in frame F at time t has, at each later time u (nearer NOW) at which a frame stands at F's spot (FrameAt), an
// old door hanging in that frame: an AjarDoor with args[1] OLD, made by Hang (OldHang) the moment the door goes in,
// also at the first tic for a door that hangs from the start, and unmade by Unhang when the door comes down at t
// (OldUnhang). It is a hung door to everything that asks (it is the frame's door, args[0] its far side at u: sight,
// shots, monsters, water, belts), opens on the door's far side at u, and is rusted to its frame: USE at it says so
// (UseFrame), and a thief or a nailer leaves it (Stuck). A colour door does not go into a frame while a frame at
// its spot at a later time holds any door but those that go with the one swapped out (OldRefuses); the clocked
// doors leave none, and their own refusals cover an old door in their twin. Its look (AjarDoor.Show): ten years old
// THEN (dulled, AJO1..6), forty or fifty NOW (flaking, rust from the hinges, AJQ1..6; tools/gfx_olddoor.py), and
// the surround of the far side it opens onto ages with it (AgeFar).
// A long cause may follow a frame instead of a lever (AjarThenFrameCause, 20208): its setting is what hangs in that
// frame at its time.

class AjarThen : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	const THEN_ID = 20;        // a THEN copy's line id: NOW's + THEN_ID (frames and far sides; ajarthen.THEN_ID); BEFORE's + 2 x THEN_ID
	const T_NOW = 0;          // the times (T_: a ZScript name is not told from Now by its case)
	const T_THEN = 1;
	const T_BEFORE = 2;       // the third time (the three times lab): ten years before THEN, at twice the shift

	Vector2 Off() { return (args[0], args[1]); }
	// a door left hanging is an old door at every later time (args[3] 1: ajarthen.Times(old=True))
	bool OldDoors() { return args[3] == 1; }
	// 2, or 3 with args[2] 3 (ajarthen.Times(before=True))
	int Times() { return args[2] >= 3 ? 3 : 2; }
	// which time p is at: NOW 0, THEN 1 (past half the shift), BEFORE 2 (past one and a half, three times only)
	int TimeOf(Vector2 p)
	{
		Vector2 o = Off();
		double l2 = o dot o;
		if (l2 <= 0) return T_NOW;
		double t = ((p - pos.xy) dot o) / l2;
		return Times() == 3 && t > 1.5 ? T_BEFORE : t > 0.5 ? T_THEN : T_NOW;
	}
	bool InThen(Vector2 p) { return TimeOf(p) == T_THEN; }
	// the same spot at time t
	Vector2 At(Vector2 p, int t) { return p + Off() * (t - TimeOf(p)); }
	// the same spot at the other time (NOW and THEN)
	Vector2 Other(Vector2 p) { return InThen(p) ? p - Off() : p + Off(); }
	// the same spot NOW
	Vector2 Now(Vector2 p) { return At(p, T_NOW); }

	static AjarThen Find() { return AjarThen(ThinkerIterator.Create("AjarThen").Next()); }
}

class AjarThenCause : Actor
{
	int setting;
	int changedAt;
	bool arrived;              // its sectors and basin stand where the setting puts them
	int timesSet;              // changes made to it (MAP21: its first change is said on the screen)
	int reached;               // the settings a change has set it to, a bit each (AjarAmbush cause 63)
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	virtual int Settings() { return clamp(args[0], 2, 4); }      // (4: MAP21's beam, off and three walls)
	override void Activate(Actor activator)
	{
		let th = AjarThenHandler.Get();
		if (th) th.SetCause(self, (setting + 1) % Settings(), activator);
	}
}

// A long cause that follows a frame (thing 20208; the old door lab, PLAN.md "The old door lab", 7 and 8): its
// setting is not a lever's but what hangs in frame args[0] at that frame's time, kept so each tic (FollowFrames):
// 0 while it is empty, 1 while a colour door (an old one too) hangs in it. With args[4] a cause's tid * 16 + a
// colour (the belt's heap): 0 while that cause stands in its setting 0; else 1 while the frame is empty, 2 while the
// door of that colour (or an old self of it) hangs there, and 0 with any other door in it (what went through went
// where nothing was built for it). Otherwise as AjarThenCause: args[1] the sectors it moves, args[2] a basin and
// args[3] its depth. It has no lever.
class AjarThenFrameCause : AjarThenCause
{
	AjarFrame f;
	override int Settings() { return args[4] ? 3 : 2; }
	override void Activate(Actor activator) {}
	int Want()
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!f && h) f = h.FindFrame(args[0]);
		AjarDoor d = f ? f.door : null;
		bool colour = d && (AjarHandler.Placed(d) || d.IsOld());
		if (!args[4]) return colour ? 1 : 0;
		let th = AjarThenHandler.Get();
		let gate = th ? th.FindCause(args[4] / 16) : null;
		if (!gate || gate.setting == 0) return 0;
		if (!d) return 1;
		return colour && d.Colour() == args[4] % 16 ? 2 : 0;
	}
}

// Shot by the player (from either time, through a hung door too): sets its
// cause to args[1] - 1, or steps it on (args[1] 0). One shot is one hit: hits
// closer together than QUIET tics (a shotgun's pellets, a chaingun held down)
// count once.
class AjarThenTarget : Actor
{
	const QUIET = 35;
	int lastHit;
	AjarThenCause cause;
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
	}
	override void BeginPlay() { Super.BeginPlay(); lastHit = -1000; }
	override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
	{
		if (!source || !source.player) return 0;
		bool quiet = level.maptime - lastHit < QUIET;
		lastHit = level.maptime;
		if (quiet) return 0;
		let th = AjarThenHandler.Get();
		if (!th || !cause) return 0;
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info target of cause %d hit at t=%d", cause.tid, level.maptime);
		A_StartSound("switches/normbutn", CHAN_AUTO);
		th.SetCause(cause, args[1] ? args[1] - 1 : (cause.setting + 1) % cause.Settings(), source);
		return 0;
	}
	void Light(bool on) { if (on) SetStateLabel("Lit"); else SetStateLabel("Spawn"); }
}

class AjarThenEmitter : Actor
{
	Array<Actor> dots;
	Default { +NOBLOCKMAP +NOGRAVITY }
	States { Spawn: AJEM A -1; Stop; }

	void ShowBeam(int s)
	{
		for (int i = 0; i < dots.Size(); i++) if (dots[i]) dots[i].Destroy();
		dots.Clear();
		if (s < 1 || s > 3) return;
		angle = args[s];
		FLineTraceData d;
		LineTrace(angle, 4096, 0, TRF_THRUACTORS, 40, 0, 0, d);
		Vector2 dir = (cos(angle), sin(angle));
		for (double r = 20; r < d.Distance - 6; r += 12)
			dots.Push(Spawn("AjarThenDot", pos + (dir * r, 40)));
		let spot = Spawn("AjarThenSpot", pos + (dir * (d.Distance - 3), 40));     // where it strikes the wall
		dots.Push(spot);
	}
}

class AjarThenDot : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION RenderStyle "Add"; Alpha 0.9; }
	States { Spawn: PLSS A -1 Bright; Stop; }
}

class AjarThenSpot : AjarThenDot
{
	Default { Scale 1.4; }
	States { Spawn: PLSE A 4 Bright; PLSE B 4 Bright; Loop; }
}

class AjarThenBelt : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
	// Scroll_Floor as an action special (tag, x * 32, y * 32, 2: the texture and what stands on it); 0, 0 stops it
	void Run(bool on)
	{
		int dx = args[2] - 128, dy = args[3] - 128;
		level.ExecuteSpecial(223, null, null, false, args[1], on ? dx * 32 : 0, on ? dy * 32 : 0, 2);
	}
}

class AjarThenMusic : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
	override void Activate(Actor activator)
	{
		let th = AjarThenHandler.Get();
		if (!th) return;
		th.musicOff = !th.musicOff;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(th.musicOff ? "The music no longer follows the time." : "The music follows the time again.");
	}
}

// A door then that is locked for the night (MAP21's room doors, then: Thing_Activate on its tid from the
// door's face). Says so.
class AjarThenLocked : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
	override void Activate(Actor activator)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say("Locked for the night.");
		A_StartSound("*usefail", CHAN_AUTO);
	}
}

// A monster dead forty years: its own last death frame, pale, not solid.
// A stand-in (of != null) fades in over FADE tics when the times come apart and
// out over FADE when they are joined, then is gone; one of a monster dead THEN
// is there at once. Whatever counts or weighs bones (kennel.zs) counts one from
// its spawning to its destruction, fading or not.
class AjarThenCorpse : Actor
{
	const FADE = 35;
	Actor of;                  // the monster it stands for while that one is alive THEN (null: it died THEN)
	Actor who;                 // the monster it is the bones of, alive or dead
	int at;                    // the time it lies at (AjarThen.T_NOW; THEN for a monster BEFORE)
	int weight;                // that monster's Mass
	double bodyRadius;         // ... and radius
	int fading;                // 1 fading in, -1 fading out, 0 neither
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH }
	States
	{
	Spawn:
		TNT1 A 0;
	Keep:
		#### # -1;
		Stop;
	}
	bool Leaving() { return fading < 0; }
	void FadeIn()
	{
		if (fading == 0) alpha = 0;
		fading = 1;
		A_SetRenderStyle(alpha, STYLE_Translucent);
	}
	void FadeOut()
	{
		fading = -1;
		A_SetRenderStyle(alpha, STYLE_Translucent);
	}
	override void Tick()
	{
		Super.Tick();
		if (fading > 0)
		{
			alpha = min(1., alpha + 1. / FADE);
			if (alpha >= 1) { fading = 0; A_SetRenderStyle(1, STYLE_Normal); }
		}
		else if (fading < 0)
		{
			alpha -= 1. / FADE;
			if (alpha <= 0.001)
			{
				let th = AjarThenHandler.Get();
				if (th) th.Forget(self);
				Destroy();
			}
		}
	}
}

class AjarThenHandler : EventHandler
{
	const MOVE_TICS = 64;      // a long cause changes NOW over this long (a power of two: whole heights move in exact steps, and what rides them stays exactly on them)
	const HIDDEN_TID = 1000;       // tid HIDDEN + a cause's tid: there only in its setting 0 (ajarthen.HIDDEN)
	const THEN_MUSIC = "AJM_AFTR";
	const BEFORE_MUSIC = "AJM_EMY3";       // BEFORE's piece (the three times lab): the waltz on a music box, which no level plays

	AjarThen when;
	AjarHandler h;
	AjarWaterHandler wh;
	bool ready;
	Array<AjarThenCause> causes;
	// the NOW sectors of every cause
	Array<int> secIdx;
	Array<AjarThenCause> secCause;
	Array<double> secFSpeed, secCSpeed;
	Array<double> bx1, by1, bx2, by2;
	Array<string> secFlat;          // its own floor flat (shown at its setting-0 height)
	Array<AjarThenEmitter> emitters;
	Array<AjarThenBelt> belts;
	Array<AjarThenTarget> targets;
	Array<Actor> hiddenItems;
	Array<AjarThenCause> hiddenOf;
	// company
	bool wasLinked;            // NOW and THEN joined at the last change
	bool wasLinkedBefore;      // THEN and BEFORE joined (three times)
	Array<AjarThenCorpse> corpses;
	// music
	bool musicOff;
	int musicThen;
	string nowMusic;
	string thenPiece;          // the level's piece for THEN ("": THEN_MUSIC)
	int musicChanges;          // (the tests)
	int joinedAt;              // the tic the two times were first joined; -1: not yet
	bool atStart;              // the first tic's company: stand-ins made then are there at once

	static AjarThenHandler Get() { return AjarThenHandler(EventHandler.Find("AjarThenHandler")); }

	AjarThenCause FindCause(int tid)
	{
		for (int i = 0; i < causes.Size(); i++) if (causes[i].tid == tid) return causes[i];
		return null;
	}

	void Setup()
	{
		ready = true;
		when = AjarThen.Find();
		h = AjarHandler(EventHandler.Find("AjarHandler"));
		wh = AjarWaterHandler.Get();
		nowMusic = level.Music;
		musicThen = -1;
		joinedAt = -1;
		wasLinked = true;          // as if a link had just come down: whatever lives THEN at the start shows NOW
		wasLinkedBefore = when && when.Times() == 3;       // (and BEFORE THEN and NOW)
		atStart = true;            // ... and is there at once, not fading in (MAP23: bones from the first tic)
		let ci = ThinkerIterator.Create("AjarThenCause");
		AjarThenCause c;
		while (c = AjarThenCause(ci.Next()))
		{
			causes.Push(c);
			c.setting = clamp(c.args[4], 0, c.Settings() - 1);
			if (c is "AjarThenFrameCause") c.setting = AjarThenFrameCause(c).Want();     // what hangs in its frame from the start
			if (c.args[1])
			{
				let si = level.CreateSectorTagIterator(c.args[1]);
				int s;
				while ((s = si.Next()) >= 0)
				{
					Sector sec = level.sectors[s];
					secIdx.Push(s); secCause.Push(c); secFSpeed.Push(1); secCSpeed.Push(1);
					secFlat.Push(TexMan.GetName(sec.GetTexture(Sector.floor)));
					double x1 = 1e9, y1 = 1e9, x2 = -1e9, y2 = -1e9;
					for (int k = 0; k < sec.lines.Size(); k++)
					{
						Line l = sec.lines[k];
						x1 = min(x1, min(l.v1.p.x, l.v2.p.x)); y1 = min(y1, min(l.v1.p.y, l.v2.p.y));
						x2 = max(x2, max(l.v1.p.x, l.v2.p.x)); y2 = max(y2, max(l.v1.p.y, l.v2.p.y));
					}
					bx1.Push(x1); by1.Push(y1); bx2.Push(x2); by2.Push(y2);
				}
			}
			if (c.args[2] && wh)
			{
				let b = wh.BasinOfTag(c.args[2]);
				if (b) b.held = true;      // its level is the cause's, never a flow's
			}
			let ai = level.CreateActorIterator(HIDDEN_TID + c.tid);
			Actor a;
			while (a = ai.Next()) { hiddenItems.Push(a); hiddenOf.Push(c); }
		}
		let ti = ThinkerIterator.Create("AjarThenTarget");
		AjarThenTarget tg;
		while (tg = AjarThenTarget(ti.Next())) { tg.cause = FindCause(tg.args[0]); targets.Push(tg); }
		let ei = ThinkerIterator.Create("AjarThenEmitter");
		AjarThenEmitter em;
		while (em = AjarThenEmitter(ei.Next())) emitters.Push(em);
		let bi = ThinkerIterator.Create("AjarThenBelt");
		AjarThenBelt bt;
		while (bt = AjarThenBelt(bi.Next())) belts.Push(bt);
		for (int i = 0; i < causes.Size(); i++) { Snap(causes[i]); ShowThen(causes[i]); }
	}

	// --- a sector's heights by setting ------------------------------------------------------------
	static int UserF(Sector s, int n) { return n == 0 ? s.GetUDMFInt('user_f0') : n == 1 ? s.GetUDMFInt('user_f1') : n == 2 ? s.GetUDMFInt('user_f2') : s.GetUDMFInt('user_f3'); }
	static int UserC(Sector s, int n) { return n == 0 ? s.GetUDMFInt('user_c0') : n == 1 ? s.GetUDMFInt('user_c1') : n == 2 ? s.GetUDMFInt('user_c2') : s.GetUDMFInt('user_c3'); }
	static double FloorZ(Sector s) { return s.floorplane.ZAtPoint(s.centerspot); }
	static double CeilZ(Sector s) { return s.ceilingplane.ZAtPoint(s.centerspot); }

	double WaterWant(AjarThenCause c, AjarBasin b) { return c.setting >= 1 ? b.floorZ + c.args[3] : b.floorZ; }

	// --- a cause set: NOW follows at once (over MOVE_TICS) ------------------------------------------
	int changes;               // (the tests)
	void SetCause(AjarThenCause c, int n, Actor who)
	{
		n = clamp(n, 0, c.Settings() - 1);
		if (n == c.setting) return;
		c.setting = n;
		c.changedAt = level.maptime;
		c.arrived = false;
		c.timesSet++;
		c.reached |= 1 << n;
		changes++;
		for (int i = 0; i < secIdx.Size(); i++)
		{
			if (secCause[i] != c) continue;
			Sector s = level.sectors[secIdx[i]];
			if (s.GetUDMFInt('user_floors')) secFSpeed[i] = max(abs(UserF(s, n) - FloorZ(s)) / MOVE_TICS, 0.25);
			if (s.GetUDMFInt('user_ceils')) secCSpeed[i] = max(abs(UserC(s, n) - CeilZ(s)) / MOVE_TICS, 0.25);
		}
		ShowThen(c);
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info cause %d set to %d at t=%d", c.tid, n, level.maptime);
	}

	// A cause that follows a frame is set to what hangs there now (AjarThenFrameCause).
	void FollowFrames()
	{
		for (int i = 0; i < causes.Size(); i++)
		{
			let fc = AjarThenFrameCause(causes[i]);
			if (fc) SetCause(fc, fc.Want(), null);
		}
	}

	// at once (the start; the tests' views)
	void Snap(AjarThenCause c)
	{
		for (int i = 0; i < secIdx.Size(); i++)
		{
			if (secCause[i] != c) continue;
			Sector s = level.sectors[secIdx[i]];
			if (s.GetUDMFInt('user_floors'))
			{
				double want = UserF(s, c.setting), now = FloorZ(s);
				if (abs(want - now) > 0.01) s.MoveFloor(abs(want - now) + 1, s.floorplane.PointToDist(s.centerspot, want), -1, want > now ? 1 : -1, false);
			}
			if (s.GetUDMFInt('user_ceils'))
			{
				double want = UserC(s, c.setting), now = CeilZ(s);
				if (abs(want - now) > 0.01) s.MoveCeiling(abs(want - now) + 1, s.ceilingplane.PointToDist(s.centerspot, want), -1, want > now ? 1 : -1, false);
			}
			Flat(i, c);
		}
		if (c.args[2] && wh)
		{
			let b = wh.BasinOfTag(c.args[2]);
			if (b) b.w = WaterWant(c, b);
		}
		c.arrived = true;
	}

	// The sector's floor shows its raised flat while it stands over its setting 0.
	void Flat(int i, AjarThenCause c)
	{
		Sector s = level.sectors[secIdx[i]];
		string raised = s.GetUDMFString('user_raised');
		if (raised == "" || !s.GetUDMFInt('user_floors')) return;
		string want = FloorZ(s) > UserF(s, 0) + 0.5 ? raised : secFlat[i];
		if (!(TexMan.GetName(s.GetTexture(Sector.floor)) ~== want)) s.SetTexture(Sector.floor, TexMan.CheckForTexture(want, TexMan.Type_Any));
	}

	// Does anything stand in sector i's box (a hole that is to shut)?
	bool Occupied(int i)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!(a.player || a.bSolid || a.bShootable) || a.bNoBlockmap || a is "AjarThenTarget") continue;
			if (a.pos.x + a.radius <= bx1[i] || a.pos.x - a.radius >= bx2[i]) continue;
			if (a.pos.y + a.radius <= by1[i] || a.pos.y - a.radius >= by2[i]) continue;
			return true;
		}
		return false;
	}

	void MoveCause(AjarThenCause c)
	{
		bool closing = false, moving = false;
		for (int i = 0; i < secIdx.Size(); i++)
		{
			if (secCause[i] != c) continue;
			Sector s = level.sectors[secIdx[i]];
			if (s.GetUDMFInt('user_floors'))
			{
				double want = UserF(s, c.setting), now = FloorZ(s);
				if (abs(want - now) > 0.01) { moving = true; s.MoveFloor(secFSpeed[i], s.floorplane.PointToDist(s.centerspot, want), -1, want > now ? 1 : -1, false); }
				Flat(i, c);
			}
			if (s.GetUDMFInt('user_ceils'))
			{
				double want = UserC(s, c.setting), now = CeilZ(s);
				if (want < now - 0.01)
				{
					closing = moving = true;       // until it is shut, the cause's openings wait
					if (s.GetUDMFInt('user_hold') && Occupied(i)) continue;
					s.MoveCeiling(secCSpeed[i], s.ceilingplane.PointToDist(s.centerspot, want), -1, -1, false);
				}
			}
		}
		for (int i = 0; i < secIdx.Size(); i++)
		{
			if (secCause[i] != c) continue;
			Sector s = level.sectors[secIdx[i]];
			if (!s.GetUDMFInt('user_ceils')) continue;
			double want = UserC(s, c.setting), now = CeilZ(s);
			if (want <= now + 0.01) continue;
			moving = true;
			if (closing && s.GetUDMFInt('user_hold')) continue;
			s.MoveCeiling(secCSpeed[i], s.ceilingplane.PointToDist(s.centerspot, want), -1, 1, false);
		}
		if (c.args[2] && wh)
		{
			let b = wh.BasinOfTag(c.args[2]);
			if (b)
			{
				double want = WaterWant(c, b), step = max(c.args[3], 1) / double(MOVE_TICS);
				if (abs(b.w - want) > 0.001) { moving = true; b.w = b.w < want ? min(b.w + step, want) : max(b.w - step, want); }
			}
		}
		c.arrived = !moving;
	}

	void ShowThen(AjarThenCause c)
	{
		for (int i = 0; i < emitters.Size(); i++) if (emitters[i] && emitters[i].args[0] == c.tid) emitters[i].ShowBeam(c.setting);
		for (int i = 0; i < belts.Size(); i++) if (belts[i] && belts[i].args[0] == c.tid) belts[i].Run(c.setting == 1);
		for (int i = 0; i < targets.Size(); i++)
		{
			let tg = targets[i];
			if (tg && tg.cause == c) tg.Light(tg.args[1] ? c.setting == tg.args[1] - 1 : c.setting != 0);
		}
	}

	void ShowHidden()
	{
		for (int i = 0; i < hiddenItems.Size(); i++)
		{
			let a = hiddenItems[i];
			if (!a || a.bDestroyed) continue;
			bool there = hiddenOf[i].setting == 0 && hiddenOf[i].arrived;
			a.bInvisible = !there;
			a.bSpecial = there;
		}
	}

	// AjarAmbush cause 63 (ajarthen.ambush): arg is a cause's tid * 16 + a setting. Due once a change has set
	// that cause to that setting and NOW stands where the setting puts it (MAP21: the cellar when it first
	// stands full again).
	static bool CauseDue(int arg)
	{
		let th = Get();
		if (!th || !th.ready) return false;
		let c = th.FindCause(arg / 16);
		int s = arg % 16;
		return c && (c.reached & (1 << s)) && c.setting == s && c.arrived;
	}

	// --- company -------------------------------------------------------------------------------------
	// Is some door hung that joins the two times NOW and THEN? (A colour door never does: AjarHandler.FarAt.)
	bool Linked() { return LinkedAt(AjarThen.T_NOW); }

	// ... that joins time k to time k + 1: NOW and THEN (the clocked door), THEN and BEFORE (the ten-year door)
	bool LinkedAt(int k)
	{
		if (!h || !when) return false;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			if (!f.door || !f.door.args[0] || AjarHandler.Placed(f.door)) continue;
			Line a = h.FindLine(f.args[0]), b = h.FindLine(f.door.args[0]);
			if (!a || !b) continue;
			int ta = when.TimeOf(a.v1.p), tb = when.TimeOf(b.v1.p);
			if (min(ta, tb) == k && max(ta, tb) == k + 1) return true;
		}
		return false;
	}

	// Are times u and t joined by a chain of hung clocked doors, as the links stood at the last change?
	bool Joined(int u, int t)
	{
		for (int k = min(u, t); k < max(u, t); k++) if (!(k == AjarThen.T_NOW ? wasLinked : wasLinkedBefore)) return false;
		return true;
	}

	// a's old corpse at the time `at` (NOW unless said), where a stands; `of` a: a stand-in for a while it lives
	AjarThenCorpse OldCorpse(Actor a, Actor of, int at = AjarThen.T_NOW)
	{
		State s = a.FindState("Death");
		for (int k = 0; s && s.Tics != -1 && k < 64; k++) s = s.NextState;
		if (!s) return null;
		Vector2 p = when.At(a.pos.xy, at);
		double z = level.PointInSector(p).floorplane.ZAtPoint(p);
		let c = AjarThenCorpse(Actor.Spawn("AjarThenCorpse", (p, z)));
		if (!c) return null;
		c.sprite = s.sprite;
		c.frame = s.Frame;
		c.angle = a.angle;
		c.scale = a.scale;
		c.of = of;
		c.who = a;
		c.at = at;
		c.weight = a.Mass;
		c.bodyRadius = a.radius;
		c.A_SetTranslation('AjarDust');
		if (of && !atStart) c.FadeIn();
		corpses.Push(c);
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info old corpse of a %s at (%.0f,%.0f) for %s%s", a.GetClassName(), p.x, p.y,
				of ? "one alive then" : "one dead then", at ? " (THEN)" : "");
		return c;
	}

	// Each time two times come apart (a link down), every monster alive at an earlier time than another and no
	// longer joined to it shows there as its old corpse; each time some are joined (a link up), the stand-ins of
	// the monsters now joined to their corpse's time go. With two times: NOW and THEN, the clocked door.
	void Company()
	{
		bool l0 = Linked(), l1 = when.Times() == 3 && LinkedAt(AjarThen.T_THEN);
		if ((l0 || l1) && joinedAt < 0) joinedAt = level.maptime;
		if (l0 == wasLinked && l1 == wasLinkedBefore) return;
		bool up = (l0 && !wasLinked) || (l1 && !wasLinkedBefore);
		bool down = (!l0 && wasLinked) || (!l1 && wasLinkedBefore);
		wasLinked = l0;
		wasLinkedBefore = l1;
		if (up)
		{
			for (int i = 0; i < corpses.Size(); i++)
			{
				let c = corpses[i];
				if (!c || !c.of) continue;
				int t = when.TimeOf(c.of.pos.xy);
				if (t <= c.at || Joined(c.at, t)) c.FadeOut();
			}
		}
		if (!down) return;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int t = when.TimeOf(a.pos.xy);
			for (int u = AjarThen.T_NOW; u < t; u++)
				if (!Joined(u, t) && !StandsIn(a, u) && !Returns(a, u)) OldCorpse(a, a, u);
		}
	}

	// a has a stand-in at time u that is not fading out (three times: a pair of times came apart while another
	// pair stayed apart)
	bool StandsIn(Actor a, int u)
	{
		for (int i = 0; i < corpses.Size(); i++)
		{
			let c = corpses[i];
			if (c && c.of == a && c.at == u && !c.Leaving()) return true;
		}
		return false;
	}

	// The times come apart again while a's stand-in is still fading out from where a still stands: it
	// fades in again from there rather than a second one beside it.
	bool Returns(Actor a, int u = AjarThen.T_NOW)
	{
		Vector2 p = when.At(a.pos.xy, u);
		for (int i = 0; i < corpses.Size(); i++)
		{
			let c = corpses[i];
			if (c && c.of == a && c.at == u && c.Leaving() && (c.pos.xy - p).Length() < 1) { c.FadeIn(); return true; }
		}
		return false;
	}

	// a stand-in that has faded out is gone from the list
	void Forget(AjarThenCorpse c) { for (int i = corpses.Size() - 1; i >= 0; i--) if (corpses[i] == c) corpses.Delete(i); }

	// Killed THEN: its old corpse NOW, for good, where it died. If its stand-in is there (the times apart, or
	// joined while it is still fading out), that becomes the corpse: moved to where it died, whole at once, so
	// that whatever weighs bones never counts two for one (MAP23; the kennel lab faded one out and made another).
	// Killed BEFORE: so too THEN and NOW, a corpse at each.
	override void WorldThingDied(WorldEvent e)
	{
		let a = e.thing;
		if (!ready || !when || !a || !a.bIsMonster) return;
		int t = when.TimeOf(a.pos.xy);
		for (int u = AjarThen.T_NOW; u < t; u++) DiedAt(a, u);
	}

	void DiedAt(Actor a, int u)
	{
		AjarThenCorpse kept = null;
		for (int i = 0; i < corpses.Size(); i++)
		{
			let c = corpses[i];
			if (!c || c.of != a || c.at != u) continue;
			if (!kept) kept = c;
			else c.FadeOut();
		}
		if (!kept) { OldCorpse(a, null, u); return; }
		Vector2 p = when.At(a.pos.xy, u);
		kept.SetOrigin((p, level.PointInSector(p).floorplane.ZAtPoint(p)), false);
		kept.angle = a.angle;
		kept.of = null;
		kept.fading = 0;
		kept.A_SetRenderStyle(1, STYLE_Normal);
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info old corpse of a %s at (%.0f,%.0f) for one dead then (its stand-in, kept)%s", a.GetClassName(), p.x, p.y,
				u ? " (THEN)" : "");
	}

	// Raised THEN (an arch-vile; Thing_Raise): it is not dead after all, so its bones NOW are not for good.
	// While the times are apart they stand in for it from where it lies (it gets up there); while joined
	// they fade out. (Raised BEFORE: its bones THEN and NOW, each by whether its time and BEFORE are joined.)
	int revived;               // (the tests)
	override void WorldThingRevived(WorldEvent e)
	{
		let a = e.thing;
		if (!ready || !when || !a || !a.bIsMonster || when.TimeOf(a.pos.xy) == AjarThen.T_NOW) return;
		int t = when.TimeOf(a.pos.xy);
		revived++;
		for (int i = 0; i < corpses.Size(); i++)
		{
			let c = corpses[i];
			if (!c || c.of || c.who != a) continue;
			bool joined = Joined(c.at, t);
			if (joined) c.FadeOut();
			else c.of = a;
			if (CVar.GetCVar("ajar_autotest").GetInt())
				Console.Printf("AJARTEST info old corpse of a %s raised then: %s", a.GetClassName(), joined ? "fades out" : "stands in for it");
		}
	}

	// --- music by time ---------------------------------------------------------------------------
	void Music(Actor mo)
	{
		int th = musicOff ? AjarThen.T_NOW : when.TimeOf(mo.pos.xy);
		if (th == musicThen) return;
		musicThen = th;
		S_ChangeMusic(th == AjarThen.T_BEFORE ? BEFORE_MUSIC : th ? ThenMusic() : nowMusic);
		musicChanges++;
	}

	string ThenMusic() { return thenPiece != "" ? thenPiece : THEN_MUSIC; }

	// A level names its own piece for THEN (MAP22: map22.zs, in peace and after the turn); played at once if
	// the player is THEN.
	void SetThenMusic(string piece)
	{
		thenPiece = piece;
		if (musicThen == 1) musicThen = -1;
	}

	// AjarAmbush cause 64 (ajar.zs): the two times have been joined
	static bool JoinedDue()
	{
		let th = Get();
		return th && th.ready && th.joinedAt >= 0;
	}

	override void WorldTick()
	{
		if (!ready) Setup();
		if (!when) return;
		FollowFrames();
		for (int i = 0; i < causes.Size(); i++) MoveCause(causes[i]);
		ShowHidden();
		Company();
		atStart = false;
		let mo = players[consoleplayer].mo;
		if (mo) Music(mo);
	}
}

extend class AjarHandler
{
	// A colour door (RED .. PINK): a far side of its own, a place.
	static bool Placed(AjarDoor d) { return d && d.args[1] >= 1 && d.args[1] <= 6 && !d.IsPair(); }

	// Where the colour door d opens hung in frame f: its far side at f's time. Its own line id (ownFar) is
	// the copy NOW, + THEN_ID the copy THEN, + 2 x THEN_ID the copy BEFORE. A map with one time, any other
	// door, or a far side built in one copy only (Copy.far, against the rule): args[0] as it is.
	int FarAt(AjarDoor d, AjarFrame f)
	{
		if (!Placed(d) || !f || !d.args[0]) return d.args[0];
		let w = AjarThen.Find();
		if (!w) return d.args[0];
		if (!d.ownFar) d.ownFar = d.args[0];
		int t = w.TimeOf(f.pos.xy);
		return t != AjarThen.T_NOW && FarCopy(d, t) ? FarCopy(d, t) : d.ownFar;
	}

	// The copy THEN of a colour door's far side, or 0 (a map with one time; none built).
	int ThenFar(AjarDoor d) { return FarCopy(d, AjarThen.T_THEN); }

	// The copy at time t (THEN, BEFORE) of a colour door's far side, or 0 (none built at that time).
	int FarCopy(AjarDoor d, int t)
	{
		let w = AjarThen.Find();
		if (!Placed(d) || !d.args[0] || !w || t == AjarThen.T_NOW) return 0;
		int id = (d.ownFar ? d.ownFar : d.args[0]) + AjarThen.THEN_ID * t;
		Line l = FindLine(id);
		return l && w.TimeOf(l.v1.p) == t ? id : 0;
	}

	// The frame at the same spot at the other time (NOW and THEN), if there is one.
	AjarFrame TwinFrame(AjarFrame f)
	{
		let w = AjarThen.Find();
		if (!w || !f || w.TimeOf(f.pos.xy) == AjarThen.T_BEFORE) return null;
		return FrameAt(f, AjarThen.T_THEN - w.TimeOf(f.pos.xy));
	}

	// The frame at f's spot at time t, if there is one.
	AjarFrame FrameAt(AjarFrame f, int t)
	{
		let w = AjarThen.Find();
		if (!w || !f) return null;
		Vector2 at = w.At(f.pos.xy, t);
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame o;
		while (o = AjarFrame(fi.Next())) if (o != f && (o.pos.xy - at).Length() < 1) return o;
		return null;
	}

	// Does the clocked door d reach f's time? (The clocked door NOW and THEN, the ten-year door THEN and BEFORE.)
	bool ClockReaches(AjarDoor d, AjarFrame f)
	{
		let w = AjarThen.Find();
		int t = w ? w.TimeOf(f.pos.xy) : AjarThen.T_NOW;
		return t == d.SpanFrom() || t == d.SpanFrom() + 1;
	}

	// The frame d's other leaf hangs in when d hangs in f: f's spot at the other time of d's span.
	AjarFrame ClockedTwin(AjarDoor d, AjarFrame f)
	{
		let w = AjarThen.Find();
		if (!w || !f || !ClockReaches(d, f)) return null;
		return FrameAt(f, w.TimeOf(f.pos.xy) == d.SpanFrom() ? d.SpanFrom() + 1 : d.SpanFrom());
	}

	// Hang: the clocked door d is going into f; its shadow goes into f's twin first.
	void ClockedHang(AjarDoor d, AjarFrame f)
	{
		AjarDoor s = d.Twin();
		AjarFrame t = ClockedTwin(d, f);
		if (s && t && !t.door && !s.frame) Hang(s, t);
	}

	// Unhang: one leaf of the clocked door has come down; so does the other,
	// and the door taken is the door itself, whichever frame it was taken from.
	AjarDoor ClockedUnhang(AjarDoor d)
	{
		AjarDoor tw = d.Twin();
		if (tw && tw.frame) Unhang(tw.frame);
		AjarDoor door = d.IsShadow() && tw ? tw : d;
		AjarDoor shadow = door.Twin();
		if (shadow) { shadow.carried = true; shadow.Hide(); }
		return door;
	}

	// UseFrame: what the clocked door does not do; and a frame that takes it only (args[4] 6: MAP21's
	// machine frame, at both times, and its corridor's first frame, now) takes no other door. The same for
	// the ten-year door, between THEN and BEFORE; and neither hangs at a time its clock does not reach.
	bool ClockedRefuses(AjarFrame f)
	{
		if (carried && !carried.IsClocked() && f.args[4] == 6)
		{
			Say("This frame takes only the clocked door.");
			return true;
		}
		if (carried && carried.IsClocked())
		{
			string name = carried.ClockName();
			if (!ClockReaches(carried, f))
			{
				Say("The " .. name .. " door's clock does not reach this time.\nIt will not hang in this frame.");
				return true;
			}
			AjarFrame t = ClockedTwin(carried, f);
			if (!t)
			{
				Say("This frame has no other time.\nThe " .. name .. " door will not hang in it.");
				return true;
			}
			// (all that fills the twin is the old self of the colour door swapped out of f: it comes down with that
			// door, as rule 4 has it for colour doors. PLAN.md, "The old door rule, mended", 2026-11-28)
			if (t.door && !(f.door && t.door.IsOld() && t.door.oldOf == f.door))
			{
				Say("At the other time a door hangs in this frame.\nThe " .. name .. " door cannot open onto it.");
				return true;
			}
			return false;
		}
		// (a door carried to a frame the clocked door hangs in is swapped for it, as for any hung door: both its
		// leaves come down, the carried door hangs in this frame alone, and the clocked door is in hand. Vadim's
		// game rule since MAP02, 2026-11-26: no door is ever put down, so a refusal here left full hands nothing)
		return false;
	}

	// --- a door left hanging (the old door lab) -----------------------------------------------------------
	// Hang: the colour door d has just gone into f at time t. At each later time u whose frame at f's spot is free
	// an old door hangs in that frame, opening on d's far side at u: ten years old THEN (d hung BEFORE), forty NOW (d
	// hung THEN), fifty NOW (d hung BEFORE).
	void OldHang(AjarDoor d, AjarFrame f)
	{
		let w = AjarThen.Find();
		if (!w || !w.OldDoors() || !Placed(d) || !f) return;
		int t = w.TimeOf(f.pos.xy);
		for (int u = AjarThen.T_NOW; u < t; u++)
		{
			AjarFrame g = FrameAt(f, u);
			if (!g || g.door) continue;           // (OldRefuses keeps it free; a door the map hangs there from the start stays)
			let o = AjarDoor(Actor.Spawn("AjarDoor", g.pos));
			if (!o) continue;
			o.args[1] = AjarDoor.OLD;
			o.oldOf = d;
			o.oldColour = d.Colour();
			o.oldYears = (t == AjarThen.T_BEFORE ? 10 : 0) + (u == AjarThen.T_NOW ? 40 : 0);
			o.args[0] = u == AjarThen.T_NOW ? (d.ownFar ? d.ownFar : d.args[0]) : FarCopy(d, u);     // 0: none built then, shut
			Hang(o, g);
			AgeFar(o.args[0], o.oldColour, o.oldYears > 10 ? "Q" : "O");
			if (CVar.GetCVar("ajar_autotest").GetInt())
				Console.Printf("AJARTEST info old %s door in %d, %d years, open onto %d", o.Label(), g.args[0], o.oldYears, o.args[0]);
		}
	}

	// Unhang: the colour door d has come down; it was never there later.
	void OldUnhang(AjarDoor d)
	{
		if (!d || !Placed(d)) return;
		Array<AjarDoor> old;
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor o;
		while (o = AjarDoor(di.Next())) if (o.IsOld() && o.oldOf == d) old.Push(o);
		for (int i = 0; i < old.Size(); i++)
		{
			if (old[i].frame) Unhang(old[i].frame);
			AgeFar(old[i].args[0], old[i].oldColour, "");
			old[i].Destroy();
		}
	}

	// The far side's face ages with the old door that opens onto it: the colour's surround of its recess, AJTRn and
	// AJTFn, is AJTRnO / AJTFnO ten years on, AJTRnQ / AJTFnQ forty or fifty (age ""; tools/gfx_olddoor.py).
	void AgeFar(int id, int colour, string age)
	{
		Line l = id ? FindLine(id) : null;
		if (!l) return;
		string wall = String.Format("AJTR%d", colour), flat = String.Format("AJTF%d", colour);
		TextureID wallTex = TexMan.CheckForTexture(wall .. age, TexMan.Type_Any);
		TextureID flatTex = TexMan.CheckForTexture(flat .. age, TexMan.Type_Any);
		for (int k = 0; k < 2; k++)
		{
			Sector s = k ? l.backsector : l.frontsector;
			if (!s) continue;
			for (int p = 0; p < 2; p++)
			{
				int at = p ? Sector.ceiling : Sector.floor;
				if (Aged(TexMan.GetName(s.GetTexture(at)), flat)) s.SetTexture(at, flatTex);
			}
			for (int i = 0; i < s.lines.Size(); i++)
				for (int sd = 0; sd < 2; sd++)
				{
					Side side = s.lines[i].sidedef[sd];
					if (!side) continue;
					for (int part = Side.top; part <= Side.bottom; part++)
						if (Aged(TexMan.GetName(side.GetTexture(part)), wall)) side.SetTexture(part, wallTex);
				}
		}
	}
	static bool Aged(string n, string base) { return n ~== base || n ~== base .. "O" || n ~== base .. "Q"; }

	// The frame at f's spot at a later time that keeps the colour door d out of f, or null: one that holds a door
	// (a clocked leaf, a colour door, an old door) other than what goes with the door swapped out of f (its old
	// selves, a clocked door's other leaf).
	AjarFrame OldBlocker(AjarDoor d, AjarFrame f)
	{
		let w = AjarThen.Find();
		if (!w || !w.OldDoors() || !Placed(d) || !f) return null;
		AjarDoor gone = f.door;
		int t = w.TimeOf(f.pos.xy);
		for (int u = AjarThen.T_NOW; u < t; u++)
		{
			AjarFrame g = FrameAt(f, u);
			if (!g || !g.door) continue;
			AjarDoor o = g.door;
			if (gone && (o == gone || (o.IsOld() && o.oldOf == gone) || (gone.IsClocked() && o == gone.Twin()))) continue;
			return g;
		}
		return null;
	}

	// UseFrame: the carried colour door does not go into f while a later time has a door in the same frame.
	bool OldRefuses(AjarFrame f)
	{
		if (!carried || !OldBlocker(carried, f)) return false;
		Say("A door hangs in this frame at a later time.\nThe " .. carried.Label() .. " door will not hang in it.");
		return true;
	}
}
