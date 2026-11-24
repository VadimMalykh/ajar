// The whole map in three goes (PLAN.md, "MAP33, the third secret level"
// and "The three goes lab"; the lab is map THIRD, tools/map_third.py, its
// helpers tools/ajarthird.py; the tests are in thirdtest.zs, MAP=THIRD
// MODE=3..9 tools/smoke.sh).
//
// The map is played several times (goes), each go in its own part. Go k
// plays part k. Going through time door k (at the end of part k), the player
// is in box k + 1, the start of part k + 1, with the clock at 0 again: the
// whole map is as it was at the start, every earlier go is played again in
// step with the clock, and the player goes on as the next self. Health,
// armour, weapons and ammunition go with them (it is the same player); a
// door in their hands does not (it is where it was at the start: the
// existing rule, plate.zs's NextGo).
//
// Map contract (tools/ajarthird.py makes all of it):
//  * AjarThird thing (20160), one: the map is played in goes. args[0] the
//    sector tag of the exit door (an AjarShutter, ajartime.shutter), args[1]
//    the sector tag of the room behind it (the player there is through it),
//    args[2] the seconds it stays open after the plates (0: 10).
//    And an AjarZone of fight FIGHT (9), box 0, over the whole map: what the
//    paradox's end takes in (paradox.zs works by zones).
//  * Line id 3310 + k: time door k (a portal recess, ajarmap.recess).
//    Line id 3320 + k: box k's door, where time door k - 1 comes out. Sector
//    tag 3330 + k: box k (its room and its door's recess). The number of
//    parts is the last box's number.
//  * AjarPlate (plate.zs) with args[3] n: plate n, at the end of part n
//    (args[0..2] 0). It is pressed by the player or any earlier self on it.
//  * AjarThirdHall thing (20161): a WINDOW HALL. args[0] its number h,
//    args[1] the part whose go fights there, args[2] its sector tag (every
//    sector of the hall: a sector has one tag, so its pits, pedestals and
//    walkways carry it), args[3] a second tag that also counts (0 none).
//  * AjarThirdPost thing (20162): a monster of hall args[0]'s fight, Doom
//    editor number args[1], facing the thing's angle: THE FUTURE SEEN.
//  * AjarThirdWatch thing (20163): the earlier self of go args[2] must not
//    come into a sector with tag args[0] while hall args[1]'s fight is not
//    won (a paradox).
//  * AjarThirdWin thing (20164): the AjarShutter with tag args[1] is opened
//    by hall args[0]'s win.
//  * AjarThirdWind thing (20165): a plate on a wall; USE winds the clock on.
//  * The line said at the start of go k may be the map's own: the string
//    <MAPNAME>_GO<k> of the LANGUAGE lump (src/language.txt), said in place
//    of the first lines of the engine's (ThirdWords).
//  * AjarThirdLast thing (20166), at most one: THE LAST HALL (last.zs; the
//    lab is map LAST, tools/map_last.py). args[0] the sector tag of the hall
//    (its floor, pits, pedestals, bays: where its monsters are), args[1] the
//    seconds plate 1 must be held (0: 30), args[2] the seconds a later plate
//    must be held while the earlier ones are (0: 15), args[3] the tag of an
//    AjarShutter the alarm opens (the last stand's gate; 0 none).
//    AjarThirdGuard thing (20167): a monster of the last hall, Doom editor
//    number args[0] (AjarHandler.AmbushClass), at the thing's place (a flyer
//    at its height) and angle. Sector tag 3360 + k: stand k, where go k
//    stands at the last hall (its plate, its time door), open to the hall
//    behind a railing nobody crosses (ajarthird.railing).
//
// The rules:
//  * ONE CLOCK (ot, AjarTimeHandler's) for the whole map, 0 at the start of
//    each go, on the HUD: "this go / the longest earlier go" while an earlier
//    go is still playing, then this go's alone; under it what the earlier
//    selves will do (the timetable, ThirdSchedule).
//  * EARLIER SELVES: every earlier go is an AjarGhost that is where the
//    player was at that tic of it, in its part's colour (TRNSLATE: AjarSelf1
//    yellow, AjarSelf2 green, AjarSelf3 red), until its go's end, then gone.
//    It does not fire (Claude's choice: its shots are seen in a window hall,
//    as part of the hall's record) and nothing hits it. Standing on an
//    AjarPlate it presses it (plate.zs). What it did to doors it does again
//    at its tic (goes.zs: GoWatch, GhostDoors, FirstDoors), if it can.
//    Touching one is the paradox (as in a room of goes; the parts are not
//    joined, so it cannot happen in THIRD).
//  * WINDOW HALLS: the go of the hall's part is recorded there, tic by tic
//    from its start, as time.zs records a hall (AjarTrack: monsters living
//    and dead, missiles, puffs, blood, what lies about; not players, not
//    earlier selves, not the level's own Ajar things). In every later go,
//    from its start, the record is played by puppets (AjarEcho) in step with
//    the clock, and the hall's real things are held still and unseen
//    (ThirdFreezeHall); when the record is over the puppets go and the hall is
//    as it was left. Nothing of the go that is on can reach a window hall of
//    an earlier part (the parts are not joined), so nothing it does there
//    needs to be put right.
//  * THE FUTURE SEEN (posts): before the go of the post's hall, a body lies
//    at each post (an AjarFigure of the monster's last death picture; one
//    that leaves no body shows nothing), and the shutters the hall's win
//    opens (AjarThirdWin) stand open. At the start of that go the bodies
//    go, the monsters stand at their posts alive and idle (AMBUSH: they wake
//    when they see the player), and those shutters are shut. When every
//    post's monster is dead and no monster lives in the hall, it is won and
//    they open. In a later go they are shut until the tic it was won then.
//    A hall with no posts and a shutter its win opens (MAP33's coal yard and
//    its gate) is won when no monster lives in it.
//    A watch whose earlier self comes into its sectors while the hall is not
//    won ends the universe.
//  * THE END: the exit door is open while every plate is pressed and
//    args[2] seconds more (keyed, shut.zs: it beeps its last three seconds).
//    Time door k opens, in go k, once the player stands on plate k while
//    plates 1 .. k-1 are pressed (go 1: once they stand on plate 1; go 2:
//    the moment the exit door opens). Too late: in go k (2 <= k < parts),
//    once the earlier selves will never again hold plates 1 .. k-1 all at
//    once and time door k has not opened; in the last go, once the exit
//    door has shut and will not open again and the player is not through.
//  * A SAVE at the start of each go (LevelLocals.MakeAutoSave).
//  * WINDING ON (AjarThirdWind): to two seconds before the next moment an
//    earlier self steps on its plate (none: a message). The player's record
//    over the stretch is them standing there, pale (AjarThirdTake.paleFrom,
//    paleTo: seen through, presses nothing, not touched); what the earlier
//    selves did to doors meanwhile is done; window halls are put as they are
//    then; the shutters, the exit door and the plates as the records have
//    them. No price (the lab).
//  * THE LAST HALL (only with an AjarThirdLast; last.zs has it in full):
//    every go fights it anew and the earlier selves fight in it really.
//    1. It is empty until plate 1 is first pressed in a go (go 1: by the
//       player; later: by the first self at its record's tic): the alarm.
//       Each guard's monster comes in a teleport fog, awake, its first
//       target the nearest it sees of the player and the earlier selves; the
//       gate (args[3]) opens for the go; a sound and a line.
//    2. At each go's start the hall is as at the start: what an earlier go
//       left (monsters, bodies, missiles, drops) goes, the kill counters lose
//       it, the gate is shut. Nothing of it is recorded or played by puppets.
//    3. From the alarm a go's record has what the player fired (bullets,
//       shells, their missiles: time.zs's RecordTake), and in later goes the
//       earlier self fires it again, really, from the alarm; it can be shot
//       then (what it shoots turns on it) and is never harmed. Before the
//       alarm it is as above.
//    4. Time door 1 opens once the player has stood on plate 1 args[1]
//       seconds in all since the alarm; time door k (1 < k < parts) once on
//       plate k args[2] seconds in all while plates 1 .. k-1 are pressed. The
//       HUD shows the sum. The exit door and too late as above.
//    5. The first time in a go the player comes onto their stand: a save.
//    6. No winding on once the alarm is on in the go, nor into it.
//    7. The timetable: one line an earlier self (its first step on its plate,
//       the seconds it stood there that counted), and in the last go the
//       first and the last moment the exit door is open.
//    8. Paradoxes as above; an earlier self cannot die.

class AjarThirdMark : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
}
class AjarThird : AjarThirdMark {}
class AjarThirdHall : AjarThirdMark {}
class AjarThirdPost : AjarThirdMark {}
class AjarThirdWatch : AjarThirdMark {}
class AjarThirdWin : AjarThirdMark {}

// A plate on a wall: USE winds the clock on (AjarTimeHandler.ThirdWind).
class AjarThirdWind : AjarWind
{
	// its own picture (gfx_time.py): two arrowheads on to a plate with a self on it
	States
	{
	Spawn:
		AJW3 A -1 Bright;
		Stop;
	On:
		AJW3 B -1 Bright;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		SetStateLabel("On");
	}

	override bool Used(Actor user)
	{
		let h = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let mo = PlayerPawn(user);
		if (!h || !mo || !mo.player || !h.third) return false;
		h.ThirdWind(mo);
		return true;
	}
}

// One go's record, with the stretches it wound over (pale, not lived).
class AjarThirdTake : AjarTake
{
	Array<int> paleFrom, paleTo;

	bool Pale(int t)
	{
		for (int i = 0; i < paleFrom.Size(); i++) if (t >= paleFrom[i] && t < paleTo[i]) return true;
		return false;
	}
}

extend class AjarTimeHandler
{
	const FIGHT_THIRD = 9;      // the AjarZone over the whole map (ajarthird.FIGHT)
	const WIND_LEAD = 70;       // winding on stops two seconds before a step onto a plate
	const HELD_OPEN = 1000000;  // a shutter kept open (AjarShutter.keyed)
	static int TimeDoorId(int k) { return 3310 + k; }
	static int BoxDoorId(int k) { return 3320 + k; }
	static int BoxTag(int k) { return 3330 + k; }

	bool third;                 // this map is played in goes (AjarThird)
	int tgo;                     // the go that is on, from 1 (0: not begun)
	int parts;
	int thirdLoads;             // times a saved game was loaded into this level (tests)
	transient bool thirdSeen;   // (not in a save: false on the first tic after a load)
	transient double hallMs;    // what the window halls (ThirdHalls) took this tic, in ms (MAP33's tests measure it)
	AjarThird thirdMark;
	AjarShutter exitDoor;
	int openTics;               // the exit door stays open so long after the plates
	int exitUntil;              // ... until this tic of the go
	bool exitOpened;            // it has opened in this go
	bool tdOpen;                // this go's time door has opened
	Array<AjarPlate> plates;    // plates[n - 1]: plate n

	// window halls
	Array<AjarThirdHall> halls;
	Array<AjarTrack> hTrack;    // hTrack[i]: hall i's record (from its part's go on)
	Array<int> wonTic;          // the tic of its part's go at which hall i was won (-1: not)
	Array<int> secHall;         // by sector index: the hall it is in, + 1 (0: none)
	// what is held still and unseen while a hall is played
	Array<Actor> tfz, tfzTarget;
	Array<int> tfzHall, tfzTics, tfzFlags;
	Array<double> tfzx, tfzy, tfzz, tfzvx, tfzvy, tfzvz;

	// the future seen
	Array<AjarThirdPost> posts;
	Array<Actor> postIs;        // what stands for it now: a body (AjarFigure), the monster, or none
	Array<AjarThirdWatch> watches;
	Array<int> watchTic;        // the tic of this go at which the watched self comes into it (-1: never)
	Array<AjarThirdWin> winners;

	// the schedule: what the earlier selves will do in this go (ThirdSchedule)
	Array<int> plFrom, plTo, plSelf;    // the spans an earlier self stands on its plate
	int heldLast;               // the last tic at which plates 1..go-1 are all held by earlier selves
	Array<int> heldFrom, heldTo;        // the spans they are
	Array<string> tLine;        // the timetable's lines, and their colours (Font.CR_*)
	Array<int> tColor;

	// --- the map ------------------------------------------------------------------
	// WorldLoaded (time.zs), a new level: is it played in goes?
	void ThirdLoaded()
	{
		thirdMark = AjarThird(ThinkerIterator.Create("AjarThird").Next());
		if (!thirdMark) return;
		third = true;
		fight = FIGHT_THIRD;
		openTics = 35 * (thirdMark.args[2] ? thirdMark.args[2] : 10);
		exitDoor = FindShutter(thirdMark.args[0]);
		for (parts = 1; level.CreateSectorTagIterator(BoxTag(parts + 1)).Next() >= 0; parts++) {}
		let pi = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(pi.Next()))
		{
			int n = p.args[3];
			if (n < 1) continue;
			while (plates.Size() < n) plates.Push(null);
			plates[n - 1] = p;
		}
		for (int i = 0; i < level.sectors.Size(); i++) secHall.Push(0);
		let hi = ThinkerIterator.Create("AjarThirdHall");
		AjarThirdHall hl;
		while (hl = AjarThirdHall(hi.Next()))
		{
			halls.Push(hl); hTrack.Push(null); wonTic.Push(-1);
			for (int t = 2; t <= 3; t++)
			{
				if (!hl.args[t]) continue;
				let it = level.CreateSectorTagIterator(hl.args[t]);
				int s;
				while ((s = it.Next()) >= 0) secHall[s] = halls.Size();
			}
		}
		let ri = ThinkerIterator.Create("AjarThirdPost");
		AjarThirdPost ps;
		while (ps = AjarThirdPost(ri.Next())) { posts.Push(ps); postIs.Push(null); }
		let wi = ThinkerIterator.Create("AjarThirdWatch");
		AjarThirdWatch w;
		while (w = AjarThirdWatch(wi.Next())) { watches.Push(w); watchTic.Push(-1); }
		let ni = ThinkerIterator.Create("AjarThirdWin");
		AjarThirdWin wn;
		while (wn = AjarThirdWin(ni.Next())) winners.Push(wn);
		let h = Doors();
		for (int k = 1; k <= parts; k++) { h.Link(TimeDoorId(k), 0, TIME_TEX); h.Link(BoxDoorId(k), 0, TIME_TEX); }
		LastLoaded();               // last.zs: a last hall?
	}

	clearscope static string ThirdClock(int t) { return String.Format("%d:%02d", t / 35 / 60, t / 35 % 60); }

	// The hall (index) of hall number n, or -1.
	int HallIx(int n)
	{
		for (int i = 0; i < halls.Size(); i++) if (halls[i].args[0] == n) return i;
		return -1;
	}

	int HallAt(Vector2 p) { return secHall[level.PointInSector(p).Index()] - 1; }

	bool SecTagged(Vector2 p, int tag)
	{
		if (!tag) return false;
		let it = level.CreateSectorTagIterator(tag);
		int s, at = level.PointInSector(p).Index();
		while ((s = it.Next()) >= 0) if (s == at) return true;
		return false;
	}

	// Which box the player is in (0: none).
	int BoxOf(Actor mo)
	{
		for (int k = 2; k <= parts; k++) if (SecTagged(mo.pos.xy, BoxTag(k))) return k;
		return 0;
	}

	// --- the tic ------------------------------------------------------------------
	void ThirdTick(PlayerPawn mo)
	{
		if (!thirdSeen) { thirdSeen = true; if (tgo) thirdLoads++; }
		if (paradox) { ParadoxTick(mo); ThirdTests(mo); return; }
		if (!tgo) ThirdBegin(mo);
		if (tgo < parts && mo.health > 0 && BoxOf(mo) == tgo + 1) ThirdNextGo(mo);
		GoWatch(ot);                // goes.zs: what the player did to doors, in this go's log
		ThirdRecordSelf(mo);
		ThirdSelves();
		GhostDoors();               // goes.zs: the earlier selves do again what they did to doors
		LastTick(mo);               // last.zs: the last hall's fight
		ThirdTouch(mo);
		if (!paradox)
		{
			double t0 = MSTimeF();
			ThirdHalls();
			hallMs = MSTimeF() - t0;
			ThirdHold();
			ThirdFuture(mo);
		}
		if (!paradox)
		{
			ThirdShutters(false);
			ThirdEnd(mo);
		}
		ThirdTests(mo);
		if (!paradox) ot++;
	}

	// The first go begins (the level's first tic).
	void ThirdBegin(PlayerPawn mo)
	{
		tgo = 1;
		ot = 0;
		DoorBegin();                // timedoor.zs: every door as it is at the start
		dHold.Clear();
		for (int i = 0; i < dDoor.Size(); i++) dHold.Push(-1);
		takes.Clear(); logs.Clear(); ghosts.Clear(); parted.Clear();
		takes.Push(new("AjarThirdTake")); logs.Push(new("AjarGoLog"));
		slotCls.Clear();
		ThirdHallsBegin();
		ThirdPosts();
		ThirdShutters(true);
		ThirdExitShut();
		LastBegin(mo);              // last.zs
		ThirdSchedule();
		Say(ThirdWords(1, String.Format("Go 1 of %d. Your part ends at plate 1; a door with a clock\non it leads to before, into the start of the next part.", parts)));
		LevelLocals.MakeAutoSave();
	}

	// Through time door `go`: box go + 1, the start of the next go.
	void ThirdNextGo(PlayerPawn mo)
	{
		GoWatch(ot);                // (the last of what was done)
		let h = Doors();
		AjarDoor had = h.carried;
		// the halls as they are, before they are played again
		DropAllHallPuppets();
		for (int i = 0; i < halls.Size(); i++) ThirdUnfreeze(i);
		DropGhosts();
		FirstDoors();               // plate.zs: every door touched is as it was at the start
		for (int i = 0; i < logs.Size(); i++) { logs[i].next = 0; logs[i].pNext = 0; logs[i].kNext = 0; logs[i].broken.Clear(); }
		takes.Push(new("AjarThirdTake")); logs.Push(new("AjarGoLog"));
		parted.Clear();
		tgo++;
		ot = 0;
		ThirdHallsBegin();
		ThirdPosts();
		ThirdShutters(true);
		ThirdExitShut();
		LastBegin(mo);              // last.zs
		ThirdSchedule();
		ThirdClearDoor(mo);
		mo.A_SetBlend("white", 1.0, 40);
		mo.A_StartSound("misc/teleport", CHAN_AUTO);
		string door = had ? "\nThe " .. had.Label() .. " door does not come through: it is where it was." : "";
		string last = tgo == parts ? "\nThe way out is the door in the last room: open while every plate\nis stood on, and ten seconds more." : "";
		Say(ThirdWords(tgo, String.Format("Go %d of %d. It is the start again: through the glass your earlier\nself sets off. This room's only way out is your own part.", tgo, parts)) .. last .. door);
		LevelLocals.MakeAutoSave();
	}

	// What is said at the start of go k: the map's own words if its LANGUAGE has
	// <MAPNAME>_GO<k> (MAP33: where the player is and what the go is for), else `plain`.
	static string ThirdWords(int k, string plain)
	{
		string key = String.Format("%s_GO%d", level.mapname.MakeUpper(), k);
		string s = StringTable.Localize("$" .. key);
		return s == key || s == "" ? plain : s;
	}

	// The player comes out of the box's door a few units past its line, which
	// leads nowhere and is solid: they would be stuck in it. A step on, clear of it.
	void ThirdClearDoor(PlayerPawn mo)
	{
		let it = level.CreateLineIdIterator(BoxDoorId(tgo));
		int li = it.Next();
		if (li < 0) return;
		Line l = level.lines[li];
		Vector2 mid = l.v1.p + l.delta / 2, n = (l.delta.y, -l.delta.x).Unit();
		double d = (mo.pos.xy - mid) dot n;
		if (d < 0) { n = -n; d = -d; }
		if (d > mo.radius) return;
		mo.SetOrigin((mo.pos.xy + n * (mo.radius + 1 - d), mo.pos.z), false);
	}

	void ThirdExitShut()
	{
		exitUntil = 0;
		exitOpened = false;
		tdOpen = false;
		if (exitDoor) { exitDoor.keyed = 0; exitDoor.ShutNow(); }
		let h = Doors();
		for (int k = 1; k <= parts; k++) h.Link(TimeDoorId(k), 0, TIME_TEX);
	}

	// --- earlier selves ---------------------------------------------------------------
	void ThirdRecordSelf(PlayerPawn mo)
	{
		AjarTake t = takes[takes.Size() - 1];
		t.x.Push(mo.pos.x); t.y.Push(mo.pos.y); t.z.Push(mo.pos.z); t.ang.Push(mo.angle); t.pit.Push(mo.pitch);
		t.sf.Push((int(mo.sprite) << 8) | (mo.frame & 127));
	}

	static bool PaleAt(AjarTake t, int j)
	{
		let tt = AjarThirdTake(t);
		return tt && tt.Pale(j);
	}

	void ThirdSelves()
	{
		static const string colours[] = { "AjarSelf1", "AjarSelf2", "AjarSelf3" };
		for (int i = 0; i < takes.Size() - 1; i++)
		{
			while (ghosts.Size() <= i) ghosts.Push(null);
			AjarTake t = takes[i];
			AjarGhost g = ghosts[i];
			if (ot >= t.x.Size())
			{
				// its go is over: it went through its time door
				if (g) g.Destroy();
				ghosts[i] = null;
				continue;
			}
			Vector3 p = (t.x[ot], t.y[ot], t.z[ot]);
			if (!g)
			{
				g = AjarGhost(Actor.Spawn(lastMark ? "AjarLastSelf" : "AjarGhost", p));     // (last.zs)
				g.bShootable = false;
				g.A_SetTranslation(colours[min(i, 2)]);
				ghosts[i] = g;
			}
			g.SetOrigin(p, true);
			g.angle = t.ang[ot];
			g.pitch = t.pit[ot];
			g.sprite = t.sf[ot] >> 8;
			g.frame = t.sf[ot] & 127;
			// a stretch it wound over: pale, and nobody (no plate) feels it
			bool pale = PaleAt(t, ot);
			g.A_SetRenderStyle(pale ? PALE_ALPHA : 1.0, pale ? STYLE_Translucent : STYLE_Normal);
			g.health = pale ? 0 : g.SpawnHealth();
		}
	}

	// Touching an earlier self (paradox.zs's rule; not to be had in THIRD, whose parts are apart).
	void ThirdTouch(PlayerPawn mo)
	{
		if (mo.health <= 0) return;
		for (int i = 0; i < takes.Size() - 1 && i < ghosts.Size(); i++)
		{
			while (parted.Size() <= i) parted.Push(false);
			AjarGhost g = ghosts[i];
			if (!g || ot >= takes[i].x.Size()) continue;
			if (PaleAt(takes[i], ot)) { parted[i] = false; continue; }
			if (!Touching(mo, g)) { parted[i] = true; continue; }
			if (!parted[i]) continue;
			EndUniverse(mo, i);
			return;
		}
	}

	// --- window halls ------------------------------------------------------------------
	// A go begins: the hall of its part is recorded from now; the halls of
	// earlier parts are played from their records' start, their real things
	// held still and unseen until then.
	void ThirdHallsBegin()
	{
		for (int i = 0; i < halls.Size(); i++)
		{
			int part = halls[i].args[1];
			if (part == tgo)
			{
				hTrack[i] = new("AjarTrack");
				hTrack[i].box = 100 + i;
				wonTic[i] = -1;
			}
			else if (part < tgo && hTrack[i]) ThirdFreezeHall(i);
		}
	}

	// What a window hall records and, while it is played, holds unseen.
	bool ThirdCounts(Actor a)
	{
		if (!a || a.player || a is "AjarGhost" || a is "AjarEcho" || a.bInvisible) return false;
		let inv = Inventory(a);
		if (inv) return !inv.owner;
		if (a.bIsMonster || a.bMissile || a.bCorpse) return true;
		if (!a.bNoBlockmap) return false;
		String n = a.GetClassName();
		return !(n.Left(4) ~== "Ajar");      // the level's own things: plates, doors, figures, zones, the paradox's
	}

	void ThirdHalls()
	{
		bool rec = false;
		for (int i = 0; i < halls.Size(); i++)
		{
			AjarTrack tr = hTrack[i];
			if (!tr) continue;
			int part = halls[i].args[1];
			if (part == tgo) { rec = true; continue; }
			if (part > tgo) continue;
			int n = tr.first.Size();
			if (ot < n) PlayBack(tr, ot);           // time.zs
			else if (ot == n) { DropPuppets(tr.box); ThirdUnfreeze(i); }
		}
		if (rec) RecordHalls();
	}

	// time.zs's Record, for every hall that is being recorded, in one pass.
	void RecordHalls()
	{
		for (int i = 0; i < halls.Size(); i++)
		{
			AjarTrack tr = hTrack[i];
			if (!tr || halls[i].args[1] != tgo) continue;
			tr.first.Push(tr.slot.Size());
			for (int j = 0; j < tr.live.Size(); j++) tr.liveSeen[j] = 0;
		}
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			int hi = HallAt(a.pos.xy);
			if (hi < 0 || halls[hi].args[1] != tgo || !hTrack[hi] || !ThirdCounts(a)) continue;
			AjarTrack tr = hTrack[hi];
			int f = (int(a.sprite) << 8) | (a.frame & 127) | ((a.bBright || (a.CurState && a.CurState.bFullbright)) ? 128 : 0);
			int i = tr.live.Find(a);
			if (i == tr.live.Size())
			{
				slotCls.Push(a.GetClass());
				tr.live.Push(a); tr.liveSlot.Push(slotCls.Size() - 1); tr.liveSf.Push(-1); tr.liveSeen.Push(1);
				tr.lx.Push(0); tr.ly.Push(0); tr.lz.Push(0); tr.la.Push(0);
			}
			tr.liveSeen[i] = 1;
			if (tr.liveSf[i] == f && tr.lx[i] == a.pos.x && tr.ly[i] == a.pos.y && tr.lz[i] == a.pos.z && tr.la[i] == a.angle) continue;
			tr.liveSf[i] = f; tr.lx[i] = a.pos.x; tr.ly[i] = a.pos.y; tr.lz[i] = a.pos.z; tr.la[i] = a.angle;
			tr.Put(tr.liveSlot[i], f, a.pos, a.angle);
		}
		for (int h = 0; h < halls.Size(); h++)
		{
			AjarTrack tr = hTrack[h];
			if (!tr || halls[h].args[1] != tgo) continue;
			for (int i = tr.live.Size() - 1; i >= 0; i--)
			{
				if (tr.liveSeen[i]) continue;
				tr.Put(tr.liveSlot[i], -1, (0, 0, 0), 0);
				tr.live.Delete(i); tr.liveSlot.Delete(i); tr.liveSf.Delete(i); tr.liveSeen.Delete(i);
				tr.lx.Delete(i); tr.ly.Delete(i); tr.lz.Delete(i); tr.la.Delete(i);
			}
		}
	}

	// The puppets of a played hall as its record has them at tic `to`, from `from` (winding).
	void HallPuppetsAt(AjarTrack tr, int from, int to)
	{
		int s = tr.first.Size();
		int a = from < s ? tr.first[from] : tr.slot.Size();
		int b = to < s ? tr.first[to] : tr.slot.Size();
		Array<int> last;
		for (int i = 0; i < slotCls.Size(); i++) last.Push(-1);
		for (int r = a; r < b; r++) last[tr.slot[r]] = r;
		for (int i = 0; i < last.Size(); i++) if (last[i] >= 0) Puppet(tr, last[i]);
	}

	void DropAllHallPuppets()
	{
		for (int i = 0; i < halls.Size(); i++) DropPuppets(100 + i);
	}

	void ThirdFreezeHall(int h)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (HallAt(a.pos.xy) != h || !ThirdCounts(a) || tfz.Find(a) < tfz.Size()) continue;
			tfz.Push(a); tfzHall.Push(h); tfzTarget.Push(a.target); tfzTics.Push(a.tics);
			tfzFlags.Push((a.bSkullFly ? 1 : 0) | (a.bShootable ? 2 : 0) | (a.bSolid ? 4 : 0));
			tfzx.Push(a.pos.x); tfzy.Push(a.pos.y); tfzz.Push(a.pos.z);
			tfzvx.Push(a.vel.x); tfzvy.Push(a.vel.y); tfzvz.Push(a.vel.z);
			a.tics = -1;
			a.bSkullFly = false;
			a.bShootable = false;
			a.bSolid = false;
			a.bInvisible = true;
		}
		ThirdHold();
	}

	// Held: no state runs (tics -1), and nothing moves it.
	void ThirdHold()
	{
		for (int i = 0; i < tfz.Size(); i++)
		{
			Actor a = tfz[i];
			if (!a) continue;
			a.vel = (0, 0, 0);
			a.target = null;
			if (a.pos.x != tfzx[i] || a.pos.y != tfzy[i] || a.pos.z != tfzz[i]) a.SetOrigin((tfzx[i], tfzy[i], tfzz[i]), false);
		}
	}

	void ThirdUnfreeze(int h)
	{
		for (int i = tfz.Size() - 1; i >= 0; i--)
		{
			if (tfzHall[i] != h) continue;
			Actor a = tfz[i];
			if (a)
			{
				a.SetOrigin((tfzx[i], tfzy[i], tfzz[i]), false);
				a.bInvisible = false;
				a.tics = tfzTics[i];
				a.vel = (tfzvx[i], tfzvy[i], tfzvz[i]);
				a.target = tfzTarget[i];
				a.bSkullFly = (tfzFlags[i] & 1) != 0;
				a.bShootable = (tfzFlags[i] & 2) != 0;
				a.bSolid = (tfzFlags[i] & 4) != 0;
			}
			tfz.Delete(i); tfzHall.Delete(i); tfzTarget.Delete(i); tfzTics.Delete(i); tfzFlags.Delete(i);
			tfzx.Delete(i); tfzy.Delete(i); tfzz.Delete(i); tfzvx.Delete(i); tfzvy.Delete(i); tfzvz.Delete(i);
		}
	}

	// --- the future seen --------------------------------------------------------------
	// Does a monster of this class leave a body (its death ends in a picture that stays)?
	static bool LeavesBody(class<Actor> cls)
	{
		if (!cls) return false;
		State st = GetDefaultByType(cls).FindState("Death");
		for (int n = 0; st && n < 60; n++)
		{
			if (st.tics == -1) return st.sprite != Actor.GetSpriteIndex("TNT1");
			st = st.NextState;
		}
		return false;
	}

	// A go begins: what stands at each post.
	void ThirdPosts()
	{
		for (int i = 0; i < posts.Size(); i++)
		{
			AjarThirdPost p = posts[i];
			int hi = HallIx(p.args[0]);
			int part = hi >= 0 ? halls[hi].args[1] : 0;
			class<Actor> cls = AjarHandler.AmbushClass(p.args[1]);
			if (tgo < part)
			{
				// its body, as it will lie
				if (postIs[i] || !LeavesBody(cls)) continue;
				Actor f = Actor.Spawn("AjarFigure", p.pos);
				if (!f) continue;
				f.args[0] = 2; f.args[1] = p.args[1];
				f.angle = p.angle;
				postIs[i] = f;
			}
			else if (tgo == part)
			{
				if (postIs[i] && postIs[i] is "AjarFigure") postIs[i].Destroy();
				postIs[i] = null;
				if (!cls) continue;
				Vector3 at = (p.pos.xy, level.PointInSector(p.pos.xy).floorplane.ZAtPoint(p.pos.xy));
				Actor m = Actor.Spawn(cls, at, ALLOW_REPLACE);
				if (!m) continue;
				m.angle = p.angle;
				m.bAmbush = true;           // idle at its post: it wakes when it sees the player
				m.target = null;
				postIs[i] = m;
			}
			else postIs[i] = null;          // its hall's record shows it now
		}
	}

	// The hall of the go that is on: is it won?
	void ThirdFuture(PlayerPawn mo)
	{
		for (int i = 0; i < halls.Size(); i++)
		{
			if (halls[i].args[1] != tgo || wonTic[i] >= 0) continue;
			bool any = false, alive = false;
			for (int p = 0; p < posts.Size(); p++)
			{
				if (HallIx(posts[p].args[0]) != i) continue;
				any = true;
				Actor m = postIs[p];
				if (m && m.bIsMonster && m.health > 0) alive = true;
			}
			if ((!any && !HasWinner(i)) || alive || HallLives(i)) continue;
			wonTic[i] = ot;
			Say(any ? "The hall is won: the shutters it held shut open." : "Nothing lives here any more: the way on opens.");
		}
		// a watched self comes into its place while the hall is not won
		for (int w = 0; w < watches.Size(); w++)
		{
			AjarThirdWatch wt = watches[w];
			int hi = HallIx(wt.args[1]), s = wt.args[2] - 1;
			if (hi < 0 || halls[hi].args[1] != tgo || wonTic[hi] >= 0 || s < 0 || s >= takes.Size() - 1) continue;
			if (watchTic[w] < 0 || ot < watchTic[w] || s >= ghosts.Size() || !ghosts[s]) continue;
			EndUniverse(mo, s, String.Format("Your earlier self came onto the gantry at %s,\nand then everything in the hall below was dead. Here it is not.",
				ThirdClock(watchTic[w])), true);
			return;
		}
	}

	// Does a shutter open on hall h's win (an AjarThirdWin names it)?
	bool HasWinner(int h)
	{
		for (int i = 0; i < winners.Size(); i++) if (HallIx(winners[i].args[0]) == h) return true;
		return false;
	}

	bool HallLives(int h)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && HallAt(a.pos.xy) == h) return true;
		return false;
	}

	// The shutters a hall's win opens: open before its go, shut in it until
	// the win, and in a later go as they were then. `now`: at once.
	void ThirdShutters(bool now)
	{
		for (int i = 0; i < winners.Size(); i++)
		{
			int hi = HallIx(winners[i].args[0]);
			AjarShutter s = FindShutter(winners[i].args[1]);
			if (hi < 0 || !s) continue;
			int part = halls[hi].args[1];
			bool want = tgo < part || (tgo == part && wonTic[hi] >= 0) || (tgo > part && wonTic[hi] >= 0 && ot >= wonTic[hi]);
			s.keyed = want ? HELD_OPEN : 0;
			if (!now) continue;
			s.Know();
			if (want) { s.want = true; s.Move(s.High()); }
			else s.ShutNow();
		}
	}

	// --- the end -------------------------------------------------------------------
	bool Through(Actor mo) { return thirdMark && SecTagged(mo.pos.xy, thirdMark.args[1]); }

	bool PlatesHeld(int upTo)
	{
		for (int n = 1; n <= upTo; n++) if (n > plates.Size() || !plates[n - 1] || !plates[n - 1].pressed) return false;
		return true;
	}

	void ThirdEnd(PlayerPawn mo)
	{
		// the exit door: open while every plate is pressed, and openTics more
		if (PlatesHeld(parts - 1))
		{
			exitOpened = true;
			exitUntil = ot + openTics;
		}
		if (exitDoor) exitDoor.keyed = max(0, exitUntil - ot);
		// this go's time door: once the player stands on its plate while the earlier ones are pressed
		// (a map with a last hall: by the sum, last.zs's LastPlates)
		if (!lastMark && tgo < parts && !tdOpen && tgo <= plates.Size() && plates[tgo - 1] && plates[tgo - 1].mine && PlatesHeld(tgo - 1))
		{
			tdOpen = true;
			Doors().Link(TimeDoorId(tgo), BoxDoorId(tgo + 1), TIME_TEX);
			mo.A_StartSound("doors/dr1_open", CHAN_AUTO);
			Say("The door with a clock on it is open:\nthrough it is the start again, and your next part.");
		}
		// too late
		if (tgo >= 2 && tgo < parts && !tdOpen && ot - 1 > heldLast)
		{
			EndUniverse(mo, -1, String.Format("Your earlier self left its plate for the last time at %s,\nand the door never opened in this go.",
				ThirdClock(heldLast + 1)));
			return;
		}
		if (tgo == parts && tgo >= 2 && ot - 1 > heldLast && exitUntil <= ot && exitDoor && exitDoor.IsShut() && !Through(mo))
			EndUniverse(mo, -1, "The exit door has shut for the last time,\nand you are not through it.");
	}

	// --- the schedule: what the earlier selves will do in this go ----------------------
	void ThirdSchedule()
	{
		static const int colours[] = { Font.CR_YELLOW, Font.CR_GREEN, Font.CR_RED };
		plFrom.Clear(); plTo.Clear(); plSelf.Clear(); heldFrom.Clear(); heldTo.Clear(); tLine.Clear(); tColor.Clear();
		int n = takes.Size() - 1;           // earlier selves
		// each one's plate spans
		for (int i = 0; i < n && i < plates.Size(); i++)
		{
			AjarTake t = takes[i];
			AjarPlate p = plates[i];
			if (!p) continue;
			int start = -1;
			for (int j = 0; j <= t.x.Size(); j++)
			{
				bool on = j < t.x.Size() && OnAt(p, t, j) && !PaleAt(t, j);
				if (on && start < 0) start = j;
				else if (!on && start >= 0) { plFrom.Push(start); plTo.Push(j); plSelf.Push(i); start = -1; }
			}
		}
		// the tics at which plates 1..n are all held by them
		heldLast = n ? -1 : 0x7FFFFFFF;
		if (n)
		{
			int len = 0x7FFFFFFF;
			for (int i = 0; i < n; i++) len = min(len, takes[i].x.Size());
			int start = -1;
			for (int j = 0; j <= len; j++)
			{
				bool all = j < len;
				for (int i = 0; all && i < n; i++)
				{
					bool on = false;
					for (int s = 0; !on && s < plFrom.Size(); s++) on = plSelf[s] == i && j >= plFrom[s] && j < plTo[s];
					all = on;
				}
				if (all) heldLast = j;
				if (all && start < 0) start = j;
				else if (!all && start >= 0) { heldFrom.Push(start); heldTo.Push(j); start = -1; }
			}
		}
		// the watched places: when the watched self comes into one
		for (int w = 0; w < watches.Size(); w++)
		{
			watchTic[w] = -1;
			int s = watches[w].args[2] - 1;
			if (s < 0 || s >= n) continue;
			AjarTake t = takes[s];
			for (int j = 0; j < t.x.Size() && watchTic[w] < 0; j++)
				if (SecTagged((t.x[j], t.y[j]), watches[w].args[0])) watchTic[w] = j;
			int hi = HallIx(watches[w].args[1]);
			if (watchTic[w] >= 0 && hi >= 0 && halls[hi].args[1] == tgo)
			{
				tLine.Push(String.Format("%d comes onto the gantry  %s  (the hall below must be won)", s + 1, ThirdClock(watchTic[w])));
				tColor.Push(colours[min(s, 2)]);
			}
		}
		for (int s = 0; s < plFrom.Size() && !lastMark; s++)        // (a last hall has its own lines: LastSchedule)
		{
			tLine.Push(String.Format("%d on plate %d  %s - %s", plSelf[s] + 1, plSelf[s] + 1, ThirdClock(plFrom[s]), ThirdClock(plTo[s])));
			tColor.Push(colours[min(plSelf[s], 2)]);
		}
		if (tgo == parts && n && !lastMark)
			for (int s = 0; s < heldFrom.Size(); s++)
			{
				tLine.Push(String.Format("the exit door open  %s - %s", ThirdClock(heldFrom[s] + 1), ThirdClock(heldTo[s] + openTics)));
				tColor.Push(Font.CR_WHITE);
			}
		LastSchedule();             // last.zs
	}

	// --- winding on ------------------------------------------------------------------
	void ThirdWind(PlayerPawn mo)
	{
		if (paradox || tgo < 2) { Say("Nothing is playing: there is nothing to wind on to."); return; }
		if (LastNoWind()) return;   // last.zs: not in the last fight
		int next = -1, who = -1;
		for (int s = 0; s < plFrom.Size(); s++)
			if (plFrom[s] - WIND_LEAD > ot && (next < 0 || plFrom[s] < next)) { next = plFrom[s]; who = plSelf[s]; }
		if (next < 0) { Say("No earlier self steps onto its plate after this:\nthere is nothing to wind on to."); return; }
		ThirdWindTo(mo, next - WIND_LEAD);
		mo.A_SetBlend("white", 0.5, 14);
		mo.A_StartSound("switches/normbutn", CHAN_AUTO);
		Say(String.Format("The clock goes on to %s: two seconds before\nyour earlier self %d steps onto plate %d.", ThirdClock(ot), who + 1, who + 1));
	}

	// The clock goes on to `to` at once. (Also the tests' way to sample a long go.)
	void ThirdWindTo(PlayerPawn mo, int to)
	{
		int from = ot;
		if (to <= from) return;
		// the player's own record over the stretch: standing here, pale
		let t = AjarThirdTake(takes[takes.Size() - 1]);
		int sf = (int(mo.sprite) << 8) | (mo.frame & 127);
		while (t.x.Size() < to)
		{
			t.x.Push(mo.pos.x); t.y.Push(mo.pos.y); t.z.Push(mo.pos.z); t.ang.Push(mo.angle); t.pit.Push(mo.pitch); t.sf.Push(sf);
		}
		t.paleFrom.Push(from); t.paleTo.Push(to);
		// what the earlier selves did to doors meanwhile, in its order
		for (int j = from; j < to; j++) { ot = j; GhostDoors(); }
		ot = to;
		// window halls: a played one is as its record has it then; the one recorded did not change
		for (int i = 0; i < halls.Size(); i++)
		{
			AjarTrack tr = hTrack[i];
			if (!tr) continue;
			int part = halls[i].args[1];
			if (part == tgo) { while (tr.first.Size() < to) tr.first.Push(tr.slot.Size()); continue; }
			if (part > tgo) continue;
			int n = tr.first.Size();
			if (from >= n) continue;
			if (to < n) HallPuppetsAt(tr, from, to);
			else { DropPuppets(tr.box); ThirdUnfreeze(i); }
		}
		// the shutters, and the exit door as the earlier selves' plates have it then
		ThirdShutters(true);
		if (tgo == parts)
		{
			// (in an earlier go the exit door needs the player's own plate: nothing opened it meanwhile)
			int last = -1;
			for (int s = 0; s < heldFrom.Size(); s++) if (heldFrom[s] < to) last = min(heldTo[s], to) - 1;
			exitUntil = last >= 0 ? last + 1 + openTics : 0;
		}
		if (exitDoor)
		{
			exitDoor.keyed = max(0, exitUntil - to);
			exitDoor.Know();
			if (exitUntil > to) { exitDoor.want = true; exitDoor.Move(exitDoor.High()); }
			else exitDoor.ShutNow();
		}
		ThirdSelves();
	}

	// --- the HUD: the clock and the timetable ------------------------------------------
	ui void ThirdOverlay(RenderEvent e)
	{
		if (!tgo) return;
		int len = 0;
		for (int i = 0; i < takes.Size() - 1; i++) len = max(len, takes[i].x.Size());
		string c = ThirdClock(ot);
		if (ot < len) c = c .. " / " .. ThirdClock(len);
		Screen.DrawText(BigFont, Font.CR_WHITE, 320 - BigFont.StringWidth(c) / 2, 12, c, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
		string g = String.Format("go %d of %d", tgo, parts);
		Screen.DrawText(SmallFont, Font.CR_GRAY, 320 - SmallFont.StringWidth(g) / 2, 14 + BigFont.GetHeight(), g, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
		for (int i = 0; i < tLine.Size(); i++)
			Screen.DrawText(SmallFont, tColor[i], 320 - SmallFont.StringWidth(tLine[i]) / 2, 26 + BigFont.GetHeight() + 10 * i, tLine[i],
				DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
		LastOverlay(e);             // last.zs: a plate's sum
	}
}
