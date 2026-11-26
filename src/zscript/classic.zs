// The joined maps lab (PLAN.md, "The joined maps lab"; tools/classic.py builds
// the level): Doom II's Entryway (MAP01) and Dead Simple (MAP07) made one level,
// CLASSIC, at build time from the player's own doom2.wad, with a room of Ajar's
// own; the level is in build/ajar-classic.pk3 only. Nothing of id's is here:
// only coordinates of the joined level (Entryway as it is, Dead Simple moved
// by (6144, 0)) and ids given by classic.py.
//   MAP=CLASSIC ./run.sh                       (by hand)
//   MAP=CLASSIC MODE=n tools/smoke.sh          (the tests below)
//
// Every sector of a piece carries user_piece (1 Entryway, 2 Dead Simple, 3 and
// 4 the further pieces of CLASSIC4; 0 Ajar's room) and user_music (its map's
// music), and user_doom (a sector of id's map).
// Frames: 101 Entryway's first room (north wall, west of the steps), 102 by
// Entryway's exit (the big room's north wall), 103 Dead Simple (the yard's
// north wall), 104 the Ajar room (west wall). Far sides: 201 RED (Dead Simple's
// yard, east wall, facing the start), 202 BLUE (the Ajar room's north wall),
// 203 GREEN (CLASSIC4 only: in MAP22's piece, far out). 4001: Entryway's exit
// door (line 166 of MAP01), made a frame that stays a Doom door (doomlab.zs's
// gate, made at build time). RED and BLUE lean in Entryway's first room.
//
// Tests (ClassicTest): 1 doors walked both ways, the gate, the music; 2 each
// piece as itself (a door, a lift, switches, items, monsters waking) and tags
// not crossing; 3 views (screenshots); 4 shots and a monster through RED; 5
// Dead Simple's 666 and 667; 6 (CLASSIC4) the far pieces: walking, shots, a
// door across 25000 units, views; 7 load time.

class AjarClassic : EventHandler
{
	string playing;          // the music of the piece the player is in (user_music), "" before the first tic
	int musicChanges;

	static AjarClassic Get() { return AjarClassic(EventHandler.Find("AjarClassic")); }
	static int PieceAt(Vector2 p) { return level.PointInSector(p).GetUDMFInt('user_piece'); }

	override void WorldLoaded(WorldEvent e)
	{
		// GZDoom gives every sector of a Doom-format map SECF_FLOORDROP (things on a
		// floor that drops fast stay on it); a UDMF sector cannot say so
		int doom = 0;
		for (int i = 0; i < level.sectors.Size(); i++)
		{
			Sector s = level.sectors[i];
			if (s.GetUDMFInt('user_doom')) { s.Flags |= Sector.SECF_FLOORDROP; doom++; }
		}
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info loaded %s at %d ms: lines %d sectors %d (of id's maps %d) vertices %d things %d; secrets %d monsters %d items %d",
				level.mapname, MSTime(), level.lines.Size(), level.sectors.Size(), doom, level.vertexes.Size(), ThingCount(),
				level.total_secrets, level.total_monsters, level.total_items);
	}

	// MODE=7 (the load times): every tic's time is printed (WorldTick), the last before a load being when that
	// load began (WorldUnloaded is not called for a level's own handler on a "map" from the console)

	static int ThingCount()
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		while (it.Next()) n++;
		return n;
	}

	// music by piece: the music of the map whose piece the player stands in (the Ajar room has none of its own)
	override void WorldTick()
	{
		if (CVar.GetCVar("ajar_autotest").GetInt() == 7) Console.Printf("AJARTEST info %s tic %d at %d ms", level.mapname, level.maptime, MSTime());
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		string m = mo.CurSector.GetUDMFString('user_music');
		if (m == "" || m == playing) return;
		if (playing != "") musicChanges++;
		playing = m;
		S_ChangeMusic(m);
	}
}

class ClassicTest : EventHandler
{
	const DX = 6144;                 // Dead Simple's offset
	const WALKKEY = 0x1900;
	int tic, cur, tt;
	int checks, fails;
	AjarHandler h;
	AjarClassic c;
	AjarDoor red, blue, green;

	bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0 && level.mapname.Left(7) ~== "CLASSIC"; }

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
	void Info(string s) { Console.Printf("AJARTEST info %s", s); }

	int PieceOf(Actor a) { return a.CurSector.GetUDMFInt('user_piece'); }
	bool InRoom(Actor a) { return a.pos.x > -256 && a.pos.x < 256 && a.pos.y > 3200 && a.pos.y < 3584; }
	string Where(Actor a) { return String.Format("(%.1f,%.1f,%.1f) angle %.1f piece %d sector %d", a.pos.x, a.pos.y, a.pos.z, a.angle, PieceOf(a), a.CurSector.Index()); }
	bool Facing(Actor a, double ang) { return abs(Actor.DeltaAngle(a.angle, ang)) < 1; }
	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }
	string Music() { return String.Format("music %s, changes %d", c.playing, c.musicChanges); }

	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, FloorAt((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		walking = false;
		Keys();
	}

	// --- the player's controls: keys "held" for this tic, as thentest.zs does ------------------------
	int fwd;
	uint btn;
	Vector2 walkGoal;
	bool walking;
	void Keys(int f = 0, uint b = 0) { fwd = f; btn = b; }
	void WalkTo(double x, double y) { walkGoal = (x, y); walking = true; }
	void Drive(Actor mo)
	{
		let pp = PlayerPawn(mo);
		if (!pp) return;
		if (walking)
		{
			Vector2 d = walkGoal - mo.pos.xy;
			if (d.Length() < 6) { walking = false; Keys(); }
			else { mo.angle = VectorAngle(d.x, d.y); fwd = WALKKEY; }
		}
		if (!(fwd || btn)) return;
		pp.player.cmd.forwardmove = fwd;
		pp.player.cmd.buttons = btn;
		pp.HandleMovement();
	}
	// a real USE: the engine's own CheckUse, looking where the player looks
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}
	void HangIn(AjarDoor d, int id, Actor mo)
	{
		if (d.frame) h.carried = h.Unhang(d.frame);
		h.carried = d;
		d.carried = true;
		d.Hide();
		h.UseFrame(h.FindFrame(id), mo);
	}
	double AimThrough(Actor mo, int src, int dst, Vector2 p)
	{
		Vector2 img = AjarSight.ImageThrough(h.FindLine(src), h.FindLine(dst), p);
		return VectorAngle(img.x - mo.pos.x, img.y - mo.pos.y);
	}

	// every sector's floor and ceiling, to see what moved
	Array<double> floor0, ceil0;
	void Heights()
	{
		floor0.Clear(); ceil0.Clear();
		for (int i = 0; i < level.sectors.Size(); i++)
		{
			Sector s = level.sectors[i];
			floor0.Push(s.floorplane.ZatPoint(s.centerspot));
			ceil0.Push(s.ceilingplane.ZatPoint(s.centerspot));
		}
	}
	// how many sectors of each piece movedIn since Heights(): "piece 1: n, piece 2: m"
	int movedIn[5];
	string Moved()
	{
		for (int k = 0; k < 5; k++) movedIn[k] = 0;
		for (int i = 0; i < level.sectors.Size(); i++)
		{
			Sector s = level.sectors[i];
			if (abs(s.floorplane.ZatPoint(s.centerspot) - floor0[i]) > 0.5 || abs(s.ceilingplane.ZatPoint(s.centerspot) - ceil0[i]) > 0.5)
				movedIn[clamp(s.GetUDMFInt('user_piece'), 0, 4)]++;
		}
		return String.Format("sectors moved: Ajar's %d, piece 1 %d, piece 2 %d, piece 3 %d, piece 4 %d", movedIn[0], movedIn[1], movedIn[2], movedIn[3], movedIn[4]);
	}
	Sector Tagged(int tag)
	{
		let it = level.CreateSectorTagIterator(tag);
		int i = it.Next();
		if (i < 0) return null;
		return level.sectors[i];
	}
	double CZ(Sector s) { return s.ceilingplane.ZatPoint(s.centerspot); }
	double FZ(Sector s) { return s.floorplane.ZatPoint(s.centerspot); }

	override void WorldTick()
	{
		if (!Testing()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (tic == 1)
		{
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			c = AjarClassic.Get();
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.args[1] == 1) red = d;
				else if (d.args[1] == 2) blue = d;
				else if (d.args[1] == 3) green = d;
			}
			mo.player.cheats |= CF_GODMODE;
			if (mode != 2 && mode != 4 && mode != 6) mo.player.cheats |= CF_NOTARGET;
			// the views and the shots want no fight of id's in the way
			if (mode == 3 || mode == 4 || mode == 6 || mode == 8)
			{
				let ti = ThinkerIterator.Create("Actor");
				Actor a;
				while (a = Actor(ti.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
			}
			Info(String.Format("red %d blue %d green %d; start %s; frames 101 %d 102 %d 103 %d 104 %d gate 4001 %d; %s", red != null, blue != null, green != null,
				Where(mo), h.FindFrame(101) != null, h.FindFrame(102) != null, h.FindFrame(103) != null, h.FindFrame(104) != null, h.FindFrame(4001) != null, Music()));
		}
		cur = 2;
		if (mode == 1) Doors(mo);
		else if (mode == 2) Pieces(mo);
		else if (mode == 3) Views(mo);
		else if (mode == 4) Shots(mo);
		else if (mode == 5) Bosses(mo);
		else if (mode == 6) Far(mo);
		else if (mode == 8) FarViews(mo);
		Drive(mo);
		if (mode != 3 && mode != 7 && mode != 8 && tic == cur + 2) Console.Printf("AJARTEST classicDone=1 checks=%d failed=%d", checks, fails);
	}

	override void WorldLinePreActivated(WorldEvent e)
	{
		if (Testing() && e.ActivatedLine) Info(String.Format("tic %d: line %d (special %d, id %d) activated by %s, type %d", tic, e.ActivatedLine.Index(),
			e.ActivatedLine.special, e.ActivatedLine.GetID(0), e.Thing ? e.Thing.GetClassName() : 'none', e.ActivationType));
	}

	// === MODE=1: the doors, walked both ways; the gate; the music =====================================
	void Doors(Actor mo)
	{
		if (At()) { Check("musicEntrywayAtStart", c.playing == "D_RUNNIN", Music()); red.Used(mo); Check("tookRed", h.carried == red, h.said); }
		// RED hung in frame 101 (Entryway's first room) by a real USE
		if (At()) Pose(mo, -288, 1230, 90);
		if (At()) PressUse(mo);
		if (At()) Check("redHungInEntryway", red.frame && red.frame.args[0] == 101 && !h.carried, h.said);
		// walk north into it: out of RED's far side in Dead Simple's yard, going west
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29)
		{
			Keys();
			Check("walkedIntoDeadSimple", PieceOf(mo) == 2 && mo.pos.x < 6592 && abs(mo.pos.y + 208) < 4, Where(mo));
			Check("arrivedFacingWest", Facing(mo, 180), Where(mo));
		}
		if (Seg(3) && tt == 2) Check("musicDeadSimple", c.playing == "D_SHAWN", Music());
		// and back: east into the far side, out of frame 101 going south
		if (At()) { mo.angle = 0; Keys(WALKKEY); }
		if (Seg(40) && tt == 39)
		{
			Keys();
			Check("walkedBackToEntryway", PieceOf(mo) == 1 && mo.pos.y < 1280 && abs(mo.pos.x + 288) < 4, Where(mo));
			Check("arrivedFacingSouth", Facing(mo, 270), Where(mo));
		}
		if (Seg(3) && tt == 2) Check("musicEntrywayAgain", c.playing == "D_RUNNIN", Music());
		// BLUE into frame 103 in Dead Simple: the Ajar room; and back
		if (At()) { blue.Used(mo); Check("tookBlue", h.carried == blue, h.said); }
		if (At()) Pose(mo, 6304, 730, 90);
		if (At()) { Check("standingInDeadSimple", PieceOf(mo) == 2, Where(mo)); PressUse(mo); }
		if (At()) Check("blueHungInDeadSimple", blue.frame && blue.frame.args[0] == 103 && !h.carried, h.said);
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29) { Keys(); Check("deadSimpleToAjarRoom", InRoom(mo) && Facing(mo, 270), Where(mo)); }
		if (At()) { mo.angle = 90; Keys(WALKKEY); }
		if (Seg(40) && tt == 39) { Keys(); Check("ajarRoomBackToDeadSimple", PieceOf(mo) == 2 && mo.pos.y < 768 && abs(mo.pos.x - 6304) < 4 && Facing(mo, 270), Where(mo)); }
		// BLUE taken down in Dead Simple and hung by Entryway's exit (frame 102): the Ajar room again
		if (At()) Pose(mo, 6304, 730, 90);
		if (At()) PressUse(mo);
		if (At()) Check("tookBlueInDeadSimple", h.carried == blue && !blue.frame, h.said);
		if (At()) Pose(mo, 864, 920, 90);
		if (At()) { Check("standingByTheExit", PieceOf(mo) == 1, Where(mo)); PressUse(mo); }
		if (At()) Check("blueHungByTheExit", blue.frame && blue.frame.args[0] == 102, h.said);
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29) { Keys(); Check("exitToAjarRoom", InRoom(mo), Where(mo)); }
		if (At()) { mo.angle = 90; Keys(WALKKEY); }
		if (Seg(40) && tt == 39) { Keys(); Check("ajarRoomBackToEntryway", PieceOf(mo) == 1 && mo.pos.y < 960 && abs(mo.pos.x - 864) < 4, Where(mo)); }
		// RED out of frame 101, into the gate: Entryway's own exit door (line 166)
		if (At()) Pose(mo, -288, 1230, 90);
		if (At()) PressUse(mo);
		if (At()) Check("tookRedDown", h.carried == red, h.said);
		if (At()) Pose(mo, 992, 1000, 90);
		if (At())
		{
			Line g = h.FindLine(4001);
			Info(String.Format("gate line %d: special %d portal %d, door sector %d ceiling %.1f; standing %s", g ? g.Index() : -1, g ? g.special : -1,
				g ? g.isLinePortal() : -1, g && g.backsector ? g.backsector.Index() : -1, g && g.backsector ? CZ(g.backsector) : 0, Where(mo)));
			PressUse(mo);
		}
		if (At()) Check("redHungInTheExitDoor", red.frame && red.frame.args[0] == 4001 && !h.carried, h.said);
		if (Seg(40) && tt == 39)
		{
			Line g = h.FindLine(4001);
			Check("exitDoorHeldOpen", g && g.backsector && CZ(g.backsector) - FZ(g.backsector) > 64, String.Format("door %.1f..%.1f", FZ(g.backsector), CZ(g.backsector)));
		}
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29) { Keys(); Check("exitDoorToDeadSimple", PieceOf(mo) == 2 && mo.pos.x < 6592 && Facing(mo, 180), Where(mo)); }
		if (At()) { mo.angle = 0; Keys(WALKKEY); }
		if (Seg(40) && tt == 39) { Keys(); Check("deadSimpleBackThroughTheExitDoor", PieceOf(mo) == 1 && mo.pos.y < 1048 && abs(mo.pos.x - 992) < 4 && Facing(mo, 270), Where(mo)); }
		// taken out again, the exit door is Entryway's door: USE opens it, and it leads into the exit room
		// a real USE straight at the hung gate reaches no line (the trace goes on through the portal); one at the
		// leaf standing open beside it takes the door, as on any frame
		if (At()) Pose(mo, 992, 1000, 90);
		if (At()) PressUse(mo);
		if (At()) Check("useStraightAtTheHungGateDoesNothing", h.carried == null && red.frame != null, h.said);
		if (At()) { Pose(mo, 992, 1000, 90); mo.angle = VectorAngle(red.pos.x - mo.pos.x, red.pos.y - mo.pos.y); Info(String.Format("the leaf at (%.1f,%.1f)", red.pos.x, red.pos.y)); }
		if (At()) PressUse(mo);
		if (At()) { Check("redTakenFromTheExitDoorByItsLeaf", h.carried == red && !red.frame, h.said); mo.angle = 90; }
		if (Seg(60) && tt == 59) { Line g = h.FindLine(4001); Check("exitDoorShutAgain", CZ(g.backsector) - FZ(g.backsector) < 1, String.Format("door %.1f..%.1f", FZ(g.backsector), CZ(g.backsector))); }
		// (with a door in the hands USE on it would hang that door: RED is put down first)
		if (At()) { h.DropDoor(red, mo); h.carried = null; red.SetOrigin((-176, 1100, FloorAt((-176, 1100))), false); PressUse(mo); }
		if (Seg(50) && tt == 49) { Line g = h.FindLine(4001); Check("exitDoorOpensByUse", CZ(g.backsector) - FZ(g.backsector) > 64, String.Format("door %.1f..%.1f", FZ(g.backsector), CZ(g.backsector))); }
		if (At())
		{
			Line g = h.FindLine(4001), r = h.FindLine(201);
			Info(String.Format("gate portal %d dest %d, RED's far side portal %d dest %d; frame 4001 door %d; carried %s", g.isLinePortal(), g.getPortalDestination() ? g.getPortalDestination().Index() : -1,
				r.isLinePortal(), r.getPortalDestination() ? r.getPortalDestination().Index() : -1, h.FindFrame(4001).door != null, h.carried ? h.carried.Label() : "-"));
			Keys(WALKKEY);
		}
		if (Seg(20) && tt == 19) { Keys(); Check("intoTheExitRoom", PieceOf(mo) == 1 && mo.pos.y > 1056 && mo.pos.y < 1250, Where(mo)); }
	}

	// === MODE=2: each piece as itself; tags =========================================================
	Inventory item;
	int itemCount;
	Inventory PickupNear(Vector2 p, int piece)
	{
		Inventory best;
		double bd = 1e9;
		let it = ThinkerIterator.Create("Inventory");
		Inventory i;
		while (i = Inventory(it.Next()))
		{
			// (what the player always takes: not health, which a player at full health leaves)
			if (i.owner || PieceOf(i) != piece || !(i is "Ammo" || i is "Weapon" || i is "BasicArmorBonus" || i is "HealthBonus" || i is "BasicArmorPickup")) continue;
			double d = (i.pos.xy - p).Length();
			if (d < bd) { bd = d; best = i; }
		}
		return best;
	}
	// a spot 64 from the item in the same sector, at its floor
	Vector2 Approach(Actor i)
	{
		for (int a = 0; a < 360; a += 45)
		{
			Vector2 p = i.pos.xy + Actor.AngleToVector(a, 64);
			if (level.PointInSector(p) == i.CurSector) return p;
		}
		return i.pos.xy + (64, 0);
	}
	int Awake(int piece, Actor mo)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			if (a.bIsMonster && a.health > 0 && PieceOf(a) == piece && a.target == mo && (a.pos.xy - a.SpawnPoint.xy).Length() > 32) n++;
		return n;
	}
	int Heard(int piece)
	{
		int n = 0;
		for (int i = 0; i < level.sectors.Size(); i++)
			if (level.sectors[i].SoundTarget && level.sectors[i].GetUDMFInt('user_piece') == piece) n++;
		return n;
	}
	int Targeting(int piece)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && PieceOf(a) == piece && a.target) n++;
		return n;
	}
	int Monsters(int piece)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && PieceOf(a) == piece) n++;
		return n;
	}
	// id's monsters stand dormant (they do nothing) until the waking test, so that nothing of theirs moves a door
	void Dormant(bool on)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster) continue;
			if (on) { a.Deactivate(null); continue; }
			// woken with nothing in mind: what they heard while the player went about the switches is forgotten
			a.Activate(null);
			a.target = null;
			a.LastHeard = null;
			a.SetState(a.SpawnState);
		}
	}
	void Pieces(Actor mo)
	{
		if (At()) Dormant(true);
		// Entryway: its east door (line 170) by USE
		if (At()) { Pose(mo, 1120, 608, 0); Heights(); }
		if (At()) PressUse(mo);
		if (Seg(40) && tt == 39) { string mv = Moved(); Check("entrywayDoorOpensByUse", movedIn[1] >= 1 && movedIn[2] == 0, mv); }
		// its lift (line 126, tag 5)
		if (At()) { Pose(mo, 216, 664, 180); Heights(); }
		if (At()) PressUse(mo);
		if (Seg(30) && tt == 29) { string mv = Moved(); Sector s = Tagged(10005); Check("entrywayLiftGoesDown", s && FZ(s) < 140 && movedIn[2] == 0, String.Format("lift floor %.1f; %s", s ? FZ(s) : 0, mv)); }
		// its switch of tag 3 (line 84): Entryway's sectors tagged 10003 move, none of Dead Simple's (tagged 20003)
		if (At()) { Pose(mo, 160, 2400, 180); Heights(); }
		if (At()) PressUse(mo);
		if (Seg(120) && tt == 119)
		{
			string mv = Moved();
			Sector e = Tagged(10003), d = Tagged(20003);
			Check("entrywayTag3Moves", e && FZ(e) < 112, String.Format("Entryway's tagged %.1f, Dead Simple's %.1f; %s", e ? FZ(e) : 0, d ? FZ(d) : 0, mv));
			Check("tagsDoNotCrossEntrywayToDeadSimple", movedIn[2] == 0 && movedIn[0] == 0, mv);
		}
		// Dead Simple's switch of tag 3 (line 131): the other way (once Entryway's door and lift, used above, are still)
		if (Seg(150) && tt == 149) { Heights(); }
		if (Seg(35) && tt == 34) { string mv = Moved(); Info("Entryway at rest: " .. mv); }
		if (At()) { Pose(mo, DX - 256 + 32, 490, 90); Heights(); }
		if (At()) PressUse(mo);
		if (Seg(120) && tt == 119)
		{
			string mv = Moved();
			Sector d = Tagged(20003);
			Check("deadSimpleTag3Moves", movedIn[2] >= 1, String.Format("Dead Simple's tagged %.1f; %s", d ? FZ(d) : 0, mv));
			Check("tagsDoNotCrossDeadSimpleToEntryway", movedIn[1] == 0 && movedIn[0] == 0, mv);
		}
		// Dead Simple's start switch (line 162, tag 1): its start room opens
		if (At()) { Pose(mo, DX + 56, -224, 180); Heights(); }
		if (At()) PressUse(mo);
		if (Seg(120) && tt == 119) { string mv = Moved(); Sector s = Tagged(20001); Check("deadSimpleStartSwitch", s && FZ(s) < 100 && movedIn[1] == 0, String.Format("floor %.1f; %s", s ? FZ(s) : 0, mv)); }
		// (the doors and the lift used above have closed and come back up by now)
		// an item in each, picked up by walking over it
		for (int k = 1; k <= 2; k++)
		{
			if (At())
			{
				let i = PickupNear(k == 1 ? (-96, 1000) : (DX - 600, -208), k);
				item = i;
				if (i)
				{
					Vector2 p = Approach(i);
					Pose(mo, p.x, p.y, 0);
					WalkTo(i.pos.x, i.pos.y);
					Info(String.Format("item %s at (%.0f,%.0f) piece %d; walking from (%.0f,%.0f)", i.GetClassName(), i.pos.x, i.pos.y, k, p.x, p.y));
				}
			}
			if (Seg(40) && tt == 39) { Check(k == 1 ? "entrywayItemPickedUp" : "deadSimpleItemPickedUp", item == null || item.owner != null || item.bInvisible, item ? String.Format("%s held by %s", item.GetClassName(), item.owner ? "" .. item.owner.GetClassName() : "nobody") : "gone"); walking = false; Keys(); }
		}
		// monsters wake to noise and come, in their own piece only: Entryway first (Dead Simple's must sleep on)
		if (At()) Pose(mo, -96, 1000, 90);          // (out of Dead Simple's sight before they wake)
		if (At())
		{
			Info(String.Format("sectors with a sound target before: Entryway %d, Dead Simple %d", Heard(1), Heard(2)));
			for (int i = 0; i < level.sectors.Size(); i++) level.sectors[i].SoundTarget = null;
			Dormant(false);
		}
		for (int k = 1; k <= 2; k++)
		{
			if (At())
			{
				if (k == 1) Pose(mo, -96, 1000, 90); else Pose(mo, DX + 300, -208, 180);
				mo.A_AlertMonsters();
				Info(String.Format("piece %d: monsters %d alive, %s", k, Monsters(k), Where(mo)));
			}
			if (Seg(2) && tt == 1) Info(String.Format("sectors with a sound target after the noise in piece %d: Entryway %d, Dead Simple %d; Dead Simple's monsters with a target %d",
				k, Heard(1), Heard(2), Targeting(2)));
			if (Seg(140) && tt == 139)
			{
				Check(k == 1 ? "entrywayMonstersWakeAndWalk" : "deadSimpleMonstersWakeAndWalk", Awake(k, mo) > 0, String.Format("awake and moved %d of %d", Awake(k, mo), Monsters(k)));
				if (k == 1)
				{
					let it = ThinkerIterator.Create("Actor");
					Actor a;
					while (a = Actor(it.Next()))
						if (a.bIsMonster && a.health > 0 && PieceOf(a) == 2 && a.target)
							Info(String.Format("Dead Simple's %s at (%.0f,%.0f) from (%.0f,%.0f) has a target: %s at (%.0f,%.0f) piece %d; sees it %d", a.GetClassName(), a.pos.x, a.pos.y,
								a.SpawnPoint.x, a.SpawnPoint.y, a.target.GetClassName(), a.target.pos.x, a.target.pos.y, PieceOf(a.target), a.CheckSight(a.target)));
				}
				if (k == 1) Check("deadSimpleSleepsThrough", Targeting(2) == 0, String.Format("Dead Simple's monsters with a target: %d of %d", Targeting(2), Monsters(2)));
			}
		}
	}

	// === MODE=3: views (tools/smoke_CLASSIC_3.cfg: a screenshot at 50 + 70 n) =============================
	void View(Actor mo, int n, double x, double y, double ang, string what)
	{
		if (tic == 20 + 70 * n) { Pose(mo, x, y, ang); Info(String.Format("view %d: %s; %s", n + 1, what, Where(mo))); }
	}
	void Views(Actor mo)
	{
		if (tic == 10) { HangIn(red, 101, mo); HangIn(blue, 102, mo); }
		View(mo, 0, -288, 1060, 90, "Entryway's first room, RED hung in frame 101: Dead Simple's yard through it");
		View(mo, 1, DX + 160, -208, 0, "Dead Simple's yard, RED's far side: Entryway's first room through it");
		View(mo, 2, 864, 760, 90, "Entryway's big room, BLUE hung in frame 102 by the exit: the Ajar room");
		View(mo, 3, 0, 3300, 90, "the Ajar room, BLUE's far side: Entryway's big room through it");
		if (tic == 20 + 70 * 4) { HangIn(red, 4001, mo); }
		View(mo, 4, 992, 930, 90, "Entryway's exit door, RED hung in it (the gate): Dead Simple's yard");
		View(mo, 5, DX + 160, -208, 0, "Dead Simple's yard: RED's far side, the exit door's corridor through it");
		if (tic == 20 + 70 * 6) { HangIn(blue, 103, mo); }
		View(mo, 6, DX + 160, 600, 90, "Dead Simple's yard, BLUE hung in frame 103: the Ajar room");
		View(mo, 7, -96, 820, 90, "Entryway's first room from the start");
		if (tic == 20 + 70 * 8) { red.Used(mo); h.carried = null; red.SetOrigin((-176, 1100, FloorAt((-176, 1100))), false); }
		View(mo, 8, -288, 1060, 90, "frame 101 empty again");
	}

	// === MODE=4: shots and a monster through RED ======================================================
	Actor target, imp, rocket;
	Vector3 rocketLast;
	bool impSeen;
	int targetWas;
	void Shots(Actor mo)
	{
		if (At()) HangIn(red, 101, mo);
		// a zombie in Dead Simple's yard, 256 west of RED's far side; the player in Entryway shoots through the frame
		if (At())
		{
			target = Actor.Spawn("ZombieMan", (DX + 448 - 256, -208, FloorAt((DX + 448 - 256, -208))));
			target.speed = 0;           // (it stands still; a dormant monster would take no damage)
			targetWas = target.health;
			Pose(mo, -288, 1100, 90);
		}
		if (At()) { double a = AimThrough(mo, 101, 201, target.pos.xy); mo.angle = a; mo.LineAttack(a, 4096, 0, 10, 'Hitscan', "BulletPuff"); }
		if (At()) Check("hitscanEntrywayToDeadSimple", target.health < targetWas, String.Format("health %d of %d", target.health, targetWas));
		// a rocket the same way
		if (At()) { targetWas = target.health; rocket = mo.SpawnPlayerMissile("Rocket", AimThrough(mo, 101, 201, target.pos.xy)); }
		if (Seg(40))
		{
			if (rocket) rocketLast = rocket.pos;
			if (tt == 39) Check("rocketEntrywayToDeadSimple", target.health < targetWas || !target || target.health <= 0, String.Format("rocket last at (%.0f,%.0f), piece %d; zombie health %d", rocketLast.x, rocketLast.y, AjarClassic.PieceAt(rocketLast.xy), target ? target.health : -1));
		}
		// and back: a zombie in Entryway's first room, shot from Dead Simple's yard through RED's far side
		if (At())
		{
			target = Actor.Spawn("ZombieMan", (-288, 1000, FloorAt((-288, 1000))));
			target.speed = 0;           // (it stands still; a dormant monster would take no damage)
			targetWas = target.health;
			Pose(mo, DX + 300, -208, 0);
		}
		if (At()) { double a = AimThrough(mo, 201, 101, target.pos.xy); mo.angle = a; mo.LineAttack(a, 4096, 0, 10, 'Hitscan', "BulletPuff"); }
		if (At()) Check("hitscanDeadSimpleToEntryway", target.health < targetWas, String.Format("health %d of %d", target.health, targetWas));
		if (At()) target.Destroy();
		// an imp in Entryway after the player, who walks through RED: it follows (AjarSense)
		if (At())
		{
			Pose(mo, -288, 1230, 90);
			imp = Actor.Spawn("DoomImp", (-288, 1040, FloorAt((-288, 1040))));
			imp.angle = 90;
			imp.target = mo;
			imp.SetState(imp.SeeState);
			mo.player.cheats &= ~CF_NOTARGET;
		}
		if (At()) Keys(WALKKEY);
		if (Seg(20) && tt == 19) { Keys(); WalkTo(DX + 200, -208); Check("playerInDeadSimple", PieceOf(mo) == 2, Where(mo)); }
		if (Seg(350))
		{
			if (!impSeen && imp && PieceOf(imp) == 2) { impSeen = true; Info(String.Format("the imp came through after %d tics: %s", tt, Where(imp))); }
			if (tt == 349) Check("impFollowsThroughRed", impSeen, imp ? Where(imp) : "gone");
		}
	}

	// === MODE=5: Dead Simple's 666 and 667 ==========================================================
	void KillAll(string cls, Actor mo, int piece = 0)
	{
		let it = ThinkerIterator.Create(cls);
		Actor a;
		int n = 0, left = 0;
		while (a = Actor(it.Next()))
		{
			if (a.health <= 0) continue;
			if (piece && PieceOf(a) != piece) { left++; continue; }
			a.DamageMobj(mo, mo, a.health + 1000, 'None', DMG_FORCED);
			n++;
		}
		Info(String.Format("killed %d %s%s, %d alive elsewhere", n, cls, piece ? String.Format(" in piece %d", piece) : "", left));
	}
	int Down666()
	{
		let it = level.CreateSectorTagIterator(666);
		int i, down;
		while ((i = it.Next()) >= 0) if (FZ(level.sectors[i]) < floor0[i] - 8) down++;
		return down;
	}
	int can666;
	void Bosses(Actor mo)
	{
		if (At())
		{
			Pose(mo, DX + 300, -208, 180);
			Heights();
			// a tag 666 sector already at its lowest neighbour's floor has nowhere to go, in Doom as here
			let it = level.CreateSectorTagIterator(666);
			int i;
			can666 = 0;
			while ((i = it.Next()) >= 0)
			{
				double low;
				Vertex v;
				[low, v] = level.sectors[i].FindLowestFloorSurrounding();
				if (FZ(level.sectors[i]) > low + 0.5) can666++;
				Info(String.Format("tag 666: sector %d floor %.1f, lowest around %.1f", i, FZ(level.sectors[i]), low));
			}
		}
		// in CLASSIC4 a mancubus elsewhere (Nirvana's own three are cut away with its north, so one is put in its
		// start room): Dead Simple's are killed first, alone, and the walls wait for that one too
		bool four = level.mapname ~== "CLASSIC4";
		if (four && At())
		{
			let f = Actor.Spawn("Fatso", (NX + 4480, 3600, FloorAt((NX + 4480, 3600))));
			f.speed = 0;
			Info(String.Format("a mancubus put in Nirvana: piece %d", PieceOf(f)));
			KillAll("Fatso", mo, 2);
		}
		if (four && Seg(300) && tt == 299)
			Check("deadSimpleWallsWaitForAMancubusElsewhere", Down666() == 0, String.Format("%d tag 666 sectors lowered with only Dead Simple's mancubi dead", Down666()));
		if (At()) KillAll("Fatso", mo);
		if (Seg(300) && tt == 299)
		{
			Moved();
			let it = level.CreateSectorTagIterator(666);
			int i, n, down;
			while ((i = it.Next()) >= 0) { n++; if (FZ(level.sectors[i]) < floor0[i] - 8) down++; }
			Check("mancubiDeadWallsDown", n > 0 && down == can666, String.Format("%d of %d tag 666 sectors lowered, %d could; %s", down, n, can666, Moved()));
			Heights();
		}
		if (At()) KillAll("Arachnotron", mo);
		if (Seg(300) && tt == 299)
		{
			let it = level.CreateSectorTagIterator(667);
			int i, n, up;
			while ((i = it.Next()) >= 0) { n++; if (FZ(level.sectors[i]) > floor0[i] + 8) up++; }
			Check("arachnotronsDeadStairUp", n > 0 && up == n, String.Format("%d of %d tag 667 sectors raised; %s", up, n, Moved()));
		}
	}

	// === MODE=6: CLASSIC4's far pieces ============================================================
	// === MODE=6 (CLASSIC4): the far pieces, MAP21 at 16384 and MAP22 at (24576, 16384) =================
	// Where they are is read off their frames (105 in MAP21's start room, 203 GREEN's far side in MAP22's), so
	// that the same test runs on a package with MAP22 put elsewhere (AJAR_CLASSIC_FAR22, past 32767).
	Vector2 Mouth(int id) { Line l = h.FindLine(id); return (l.v1.p + l.v2.p) / 2; }
	Vector2 Inward(int id) { Line l = h.FindLine(id); Vector2 d = l.v2.p - l.v1.p; return (d.y, -d.x).Unit(); }
	Vector2 Off(int id, double k) { return Mouth(id) + Inward(id) * k; }
	double InAngle(int id) { Vector2 n = Inward(id); return VectorAngle(n.x, n.y); }
	void PoseAt(Actor mo, int id, double k, bool outward) { Vector2 p = Off(id, k); Pose(mo, p.x, p.y, outward ? InAngle(id) : InAngle(id) + 180); }
	Vector3 from;
	double walked22, walkedDS;
	Actor shotAt, imp22;
	void Zombie(Vector2 p) { shotAt = Actor.Spawn("ZombieMan", (p.x, p.y, FloorAt(p))); shotAt.speed = 0; targetWas = shotAt.health; }
	void Far(Actor mo)
	{
		if (At()) { Vector2 g = Mouth(203), r = Mouth(105); Info(String.Format("GREEN's far side 203 at (%.0f,%.0f), frame 105 at (%.0f,%.0f); %s", g.x, g.y, r.x, r.y, Where(mo))); }
		// GREEN hung in frame 101 (Entryway's first room): out of 203 in The Catacombs' start room, going north
		if (At()) { green.Used(mo); Check("tookGreen", h.carried == green, h.said); }
		if (At()) Pose(mo, -288, 1230, 90);
		if (At()) PressUse(mo);
		if (At()) Check("greenHungInEntryway", green.frame && green.frame.args[0] == 101 && !h.carried, h.said);
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29) { Keys(); Check("walkedIntoTheCatacombs", PieceOf(mo) == 4 && Facing(mo, InAngle(203)), Where(mo)); }
		if (Seg(3) && tt == 2) Check("musicCatacombs", c.playing == "D_THE_DA", Music());
		// walking at these coordinates: 20 tics from standing, as far as in Dead Simple's yard near (6400, -208)
		if (At()) { PoseAt(mo, 203, 40, true); from = mo.pos; Keys(WALKKEY); }
		if (Seg(20) && tt == 19) { Keys(); walked22 = (mo.pos.xy - from.xy).Length(); }
		if (At()) { Pose(mo, 6400, -208, 180); from = mo.pos; Keys(WALKKEY); }
		if (Seg(20) && tt == 19)
		{
			Keys();
			walkedDS = (mo.pos.xy - from.xy).Length();
			Check("walksAsFarInTheCatacombs", walked22 > 64 && abs(walked22 - walkedDS) < 0.001, String.Format("%.4f in 20 tics there, %.4f in Dead Simple", walked22, walkedDS));
		}
		// and back through GREEN's far side
		if (At()) PoseAt(mo, 203, 60, false);
		if (At()) Keys(WALKKEY);
		if (Seg(40) && tt == 39) { Keys(); Check("catacombsBackToEntryway", PieceOf(mo) == 1 && mo.pos.y < 1280 && abs(mo.pos.x + 288) < 4 && Facing(mo, 270), Where(mo)); }
		// a hitscan from Entryway through GREEN at a zombie in The Catacombs; then one across its start room, 240
		// long (the room is 150 deep and 300 wide, from x -696 to -392 of MAP22, a lift in its north wall)
		if (At()) { Zombie(Off(203, 100)); Pose(mo, -288, 1100, 90); }
		if (At()) { double a = AimThrough(mo, 101, 203, shotAt.pos.xy); mo.angle = a; mo.LineAttack(a, 4096, 0, 10, 'Hitscan', "BulletPuff"); }
		if (At()) { Check("hitscanEntrywayToCatacombs", shotAt.health < targetWas, String.Format("health %d of %d", shotAt.health, targetWas)); shotAt.Destroy(); }
		if (At()) { Vector2 m = Mouth(203); Zombie(m + (126, 112)); Pose(mo, m.x - 114, m.y + 112, 0); }
		if (At())
		{
			FLineTraceData d;
			mo.LineTrace(mo.angle, 4096, 0, TRF_THRUHITSCAN, mo.height / 2, data: d);
			Info(String.Format("trace from %s: hit type %d at (%.1f,%.1f,%.1f) actor %s line %d sector %d; the zombie at (%.1f,%.1f,%.1f) sector %d piece %d, height %.0f, solid %d shootable %d",
				Where(mo), d.HitType, d.HitLocation.x, d.HitLocation.y, d.HitLocation.z, d.HitActor ? "" .. d.HitActor.GetClassName() : "-", d.HitLine ? d.HitLine.Index() : -1,
				d.HitSector ? d.HitSector.Index() : -1, shotAt.pos.x, shotAt.pos.y, shotAt.pos.z, shotAt.CurSector.Index(), PieceOf(shotAt), shotAt.height, shotAt.bSolid, shotAt.bShootable));
			mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff");
		}
		if (At()) { Check("hitscanInsideTheCatacombs", shotAt.health < targetWas, String.Format("health %d of %d", shotAt.health, targetWas)); targetWas = shotAt.health; }
		if (At()) rocket = mo.SpawnPlayerMissile("Rocket", mo.angle);
		if (Seg(30) && tt == 29) { Check("rocketInsideTheCatacombs", !shotAt || shotAt.health < targetWas, String.Format("shotAt health %d", shotAt ? shotAt.health : -1)); if (shotAt) shotAt.Destroy(); }
		// a monster there walks: an imp 400 in, after the player
		if (At())
		{
			mo.player.cheats &= ~CF_NOTARGET;
			Vector2 p = Off(203, 400);
			imp22 = Actor.Spawn("DoomImp", (p.x, p.y, FloorAt(p)));
			imp22.target = mo;
			imp22.SetState(imp22.SeeState);
			from = imp22.pos;
		}
		if (Seg(70) && tt == 69) { Check("impWalksInTheCatacombs", imp22 && (imp22.pos.xy - from.xy).Length() > 64 && PieceOf(imp22) == 4, String.Format("moved %.1f", imp22 ? (imp22.pos.xy - from.xy).Length() : -1)); if (imp22) imp22.Destroy(); }
		// RED hung in frame 105 (Nirvana' start room): out of RED's far side in Dead Simple; and back
		if (At()) { green.Used(mo); h.carried = null; green.SetOrigin((-96, 1150, FloorAt((-96, 1150))), false); red.Used(mo); Check("tookRed", h.carried == red, h.said); }
		if (At()) PoseAt(mo, 105, 60, false);
		if (At()) { Check("standingInNirvana", PieceOf(mo) == 3, Where(mo)); PressUse(mo); }
		if (At()) Check("redHungInNirvana", red.frame && red.frame.args[0] == 105 && !h.carried, h.said);
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29) { Keys(); Check("nirvanaToDeadSimple", PieceOf(mo) == 2 && mo.pos.x < 6592 && Facing(mo, 180), Where(mo)); }
		if (At()) { mo.angle = 0; Keys(WALKKEY); }
		if (Seg(40) && tt == 39) { Keys(); Check("deadSimpleBackToNirvana", PieceOf(mo) == 3 && Facing(mo, InAngle(105)), Where(mo)); }
		if (Seg(3) && tt == 2) Check("musicNirvana", c.playing == "D_SHAWN", Music());

		// Nirvana changed in code at build time (classic.py, nirvana()): edits by index, then cut down to TRIM21
		if (At())
		{
			Sector room = level.PointInSector((NX + 4480, 3200)), square = level.PointInSector((NX + 4224, 3456));
			string fl = TexMan.GetName(room.GetTexture(Sector.floor));
			Check("editStartRoomLightAndFloor", room.lightlevel == 208 && fl ~== "FLOOR1_6", String.Format("light %d, floor %s", room.lightlevel, fl));
			Check("editSquareHigher", abs(FZ(square) - 40) < 0.01, String.Format("floor %.1f (id's 16)", FZ(square)));
			Line east = LineAt((NX + 4608, 3840), (NX + 4608, 3072));
			string tx = east ? TexMan.GetName(east.sidedef[0].GetTexture(Side.mid)) : "-";
			Check("editEastWall", east && tx ~== "MARBFACE" && east.special == 112, String.Format("line %d: %s, special %d", east ? east.Index() : -1, tx, east ? east.special : -1));
			squareLight = square.lightlevel;
			if (east) east.Activate(mo, 0, SPAC_Use);
		}
		if (Seg(5) && tt == 4)
		{
			Sector square = level.PointInSector((NX + 4224, 3456));
			Check("editLineSpecialDarkensSquare", square.lightlevel == 64, String.Format("light %d, was %d", square.lightlevel, squareLight));
			Check("editThings", Near("SuperShotgun", (NX + 4224, 3520)) == 0 && Near("Medikit", (NX + 4224, 3200)) == 1 && Near("BlueArmor", (NX + 4480, 3200)) == 1,
				String.Format("super shotguns on the square %d, medikits at the frame %d, blue armours %d", Near("SuperShotgun", (NX + 4224, 3520)), Near("Medikit", (NX + 4224, 3200)), Near("BlueArmor", (NX + 4480, 3200))));
			int cut = 0, bad = 0, outside = 0, things = 0;
			for (int i = 0; i < level.lines.Size(); i++)
			{
				Line l = level.lines[i];
				if (l.frontsector.GetUDMFInt('user_piece') != 3) continue;
				if (l.GetUDMFInt('user_cut')) { cut++; if (l.backsector || !l.sidedef[0].GetTexture(Side.mid).IsValid()) bad++; }
				for (int k = 0; k < 2; k++)
				{
					Vector2 v = k ? l.v2.p : l.v1.p;
					if (v.x < NX + 3000 || v.x > NX + 4700 || v.y < 3000 || v.y > 3870) outside++;
				}
			}
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
				if (a.pos.x > NX + 1184 && a.pos.x < NX + 4672 && a.pos.y > 3008 && a.pos.y < 6016 && !(a.pos.x >= NX + 3000 && a.pos.y <= 3870)) things++;
			Check("trimWallsOneSided", cut > 0 && bad == 0, String.Format("%d lines made walls, %d of them not one-sided with a texture", cut, bad));
			Check("trimNothingOutsideTheBox", outside == 0 && things == 0, String.Format("line ends outside %d, things in the rest of Nirvana %d", outside, things));
		}
		// the wall the cut made (Nirvana's line 144, at x 3072 of its own) stops the player
		if (At()) Pose(mo, NX + 3112, 3456, 180);
		if (At()) Keys(WALKKEY);
		if (Seg(30) && tt == 29) { Keys(); Check("trimWallStops", mo.pos.x > NX + 3072 && PieceOf(mo) == 3, Where(mo)); }
	}
	const NX = 16384;                // Nirvana's offset
	int squareLight;
	Line LineAt(Vector2 a, Vector2 b)
	{
		for (int i = 0; i < level.lines.Size(); i++)
			if ((level.lines[i].v1.p - a).Length() < 0.01 && (level.lines[i].v2.p - b).Length() < 0.01) return level.lines[i];
		return null;
	}
	int Near(class<Actor> cls, Vector2 p)
	{
		int n = 0;
		let it = ThinkerIterator.Create(cls);
		Actor a;
		while (a = Actor(it.Next())) if ((a.pos.xy - p).Length() < 1) n++;
		return n;
	}

	// === MODE=8 (CLASSIC4): views of the far pieces, and the automap there =============================
	void FarViews(Actor mo)
	{
		if (tic == 10) { HangIn(green, 101, mo); HangIn(red, 105, mo); }
		Vector2 g = Off(203, 140), r = Off(105, 150);
		View(mo, 0, -288, 1060, 90, "Entryway's first room, GREEN hung in frame 101: The Catacombs' start room through it");
		View(mo, 1, g.x, g.y, InAngle(203) + 180, "The Catacombs (MAP22) at its offset: GREEN's far side, Entryway's first room through it");
		View(mo, 2, r.x, r.y, InAngle(105) + 180, "Nirvana (MAP21) start room: RED hung in frame 105, Dead Simple's yard through it");
		View(mo, 3, DX + 160, -208, 0, "Dead Simple's yard: RED's far side, Nirvana's start room through it");
		View(mo, 4, g.x, g.y, InAngle(203) + 180, "the automap in The Catacombs (togglemap in the cfg)");
		View(mo, 5, NX + 4300, 3200, 0, "Nirvana's start room as changed in code: lighter, red floor, MARBFACE east wall, the blue armour added, the middle square 24 higher (left)");
		View(mo, 6, NX + 3400, 3456, 180, "Nirvana cut down: the wall made of line 144 where the long rooms were cut through");
	}
}
