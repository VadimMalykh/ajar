// The Doom door lab (PLAN.md, "The Doom door lab"): Doom II's own MAP22 (The
// Catacombs), loaded from the player's doom2.wad, a few of its doors turned
// into portals while the map loads. Nothing of the map is in the package:
// AjarDoomLabPost changes the lines named below as the engine loads the map,
// and only when the map is id's (its checksum) and `+set ajar_doomlab 1` asks
// for it; without both, every class here does nothing.
//   MAP=MAP22 EXTRA="+set ajar_doomlab 1" ./run.sh        (by hand: the carried doors)
//   MAP=MAP22 MODE=n EXTRA="+set ajar_doomlab 1" tools/smoke.sh
// MODE 1 walking, the doors' own motion, heights, widths, a monster; 2 views
// (screenshots); 3 shots; 4 a link moved and cut; 5 carried doors in Doom
// doorways, and a Doom door taken off its hinges; 6 views of 5.
//
// The doors used (line numbers of doom2.wad's MAP22; a face is the line of a
// door that faces one room, the door's own sector behind it):
//   A  line 314: door sector 56's north face, the 64 wide way south out of the
//      hall 52 (floor 48), by its little lobby 54. Door_Raise, fast.
//   B  line 333: door sector 120's south face, the 64 wide secret door in the
//      north wall of the start room 109 (floor -240). Door_Open, fast.
//   C  line 155: door sector 8's south face, 64 wide, north wall of the big
//      room 2 (floor 72); its north face, line 156, opens onto the closet 5
//      (a teleporter's) beyond it.
//   W  line 250: door sector 58's west face, the 128 wide red door in the east
//      wall of the hall 52 (floor 48), as wide again as A at A's height.
// Line ids given here: 4001..4049 a door that stays a Doom door with a portal
// on its face (a "gate": the empty frame is the plain Doom door, see
// AjarHandler.Link); 4050..4099 a Doom door that Ajar's rules take over (the
// one taken off its hinges: an empty frame is solid, as Ajar's are).

// A Doom door line's own special, kept while Line_SetPortal stands in for it
// at load: args = (line index, special, arg 1, arg 2, arg 3). Its arg 0, the
// tag, is 0 for Doom's doors worked from the line (the line's back sector).
// Its own id: the face's id (4001..).
class AjarDoomNote : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE +NOINTERACTION
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

class AjarDoomLabPost : LevelPostProcessor
{
	const NOTE_T = 20190;
	const FRAME_T = 20001;
	const DOOR_T = 20002;

	// line becomes a portal (type 1, aligned to the floor) to the line with
	// id target; its own special is kept in a note
	void Face(int line, int id, int target)
	{
		Line l = level.lines[line];
		Vector2 mid = (l.v1.p + l.v2.p) / 2;
		uint n = AddThing(NOTE_T, (mid, 0));
		SetThingID(n, id);
		SetThingArgument(n, 0, line);
		SetThingArgument(n, 1, l.special);
		SetThingArgument(n, 2, l.args[1]);
		SetThingArgument(n, 3, l.args[2]);
		SetThingArgument(n, 4, l.args[3]);
		Console.Printf("AJARTEST info face line %d id %d: its own special %d (%d,%d,%d,%d,%d) activation %d flags %x", line, id, l.special,
			l.args[0], l.args[1], l.args[2], l.args[3], l.args[4], l.activation, l.flags);
		AddLineID(line, id);
		SetLineSpecial(line, 156 /* Line_SetPortal */, target, id, 1 /* teleport */, 1 /* aligned to the floor */);
	}

	// an AjarFrame 8 in front of the line (as ajarmap.recess puts it), its tid and args[0] the line's id
	void Frame(int line, int id)
	{
		Line l = level.lines[line];
		Vector2 dir = l.delta.Unit();
		Vector2 p = (l.v1.p + l.v2.p) / 2 + (dir.y, -dir.x) * 8;
		uint n = AddThing(FRAME_T, (p, 0));
		SetThingID(n, id);
		SetThingArgument(n, 0, id);
	}

	void Door(Vector2 p, int far, int colour, int frame)
	{
		uint n = AddThing(DOOR_T, (p, 0));
		SetThingArgument(n, 0, far);
		SetThingArgument(n, 1, colour);
		SetThingArgument(n, 2, frame);
	}

	protected void Apply(Name checksum, String mapname)
	{
		if (!CVar.GetCVar("ajar_doomlab").GetInt()) return;
		Console.Printf("AJARTEST info load map=%s checksum=%s lines=%d sectors=%d things=%d", mapname, "" .. checksum,
			level.lines.Size(), level.sectors.Size(), GetThingCount());
		if (!(mapname ~== "MAP22") || !(("" .. checksum) ~== AjarDoomLab.ID_MAP22)) return;
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode >= 1 && mode <= 4)
		{
			// the bare links: A and B joined, C and W portals too (switched off at load, see AjarDoomLab.WorldLoaded)
			Face(314, 4001, 4002);
			Face(333, 4002, 4001);
			Face(155, 4003, 4001);
			Face(250, 4004, 4001);
			return;
		}
		// the carried doors (by hand, and MODE 5 and 6): A a frame that stays a Doom door; B the far side of
		// Ajar's RED door, leaning in the hall 52; door 8 taken over as Ajar's YELLOW door, hung at the start
		// in its own south face (frame 4051), its far side its north face (4052), the closet it opened onto
		Face(314, 4001, 4002);
		Face(333, 4002, 4001);
		Face(155, 4051, 4052);
		Face(156, 4052, 4051);
		Frame(314, 4001);
		Frame(155, 4051);
		Door((-60, -150), 4002, 1, 0);
		Door((-32, 880), 4052, 4, 4051);
	}
}

// One actor's crossings, as OneSideWatch, with heights.
class AjarDoomWatch play
{
	Actor who;
	Vector3 lastPos, lastVel;
	double lastAngle;
	Vector2 setVel;
	Array<double> fromX, fromY, fromZ, setX, setY, toX, toY, toZ, velX, velY, angBefore, angAfter;
	Array<int> tics;

	int Jumps() { return tics.Size(); }
}

class AjarDoomLab : EventHandler
{
	const WALK = 8.33;
	const RUN = 16.67;
	const GATE_FIRST = 4001;
	const GATE_LAST = 4049;
	const FACE_LAST = 4099;
	// Doom II's MAP22 as doom2.wad has it: MD5 of THINGS, LINEDEFS, SIDEDEFS
	// and SECTORS (the engine's own map checksum, as in its compatibility list)
	const ID_MAP22 = "4AA9B3CE449FB614497756E96509F096";
	bool on;                     // this is id's MAP22 and the lab changed it as it loaded
	int tic;

	// --- the rules of a Doom door with a portal on its face -------------------

	// Doom's doors that keep their own motion while a portal is on them: Ajar's
	// Link only switches their portal (ajar.zs, AjarHandler.Link)
	static bool Gate(int id)
	{
		return id >= GATE_FIRST && id <= GATE_LAST && (Lab() || Joined());
	}

	// the joined maps lab (classic.zs): its Doom doors are made gates at build time, by tools/classic.py
	static bool Joined() { return level.mapname.Left(7) ~== "CLASSIC"; }

	// the lab is on: asked for, and this is id's MAP22 (then, and only then, the post-processor changed it)
	static bool Lab()
	{
		return CVar.GetCVar("ajar_doomlab").GetInt() && level.mapname ~== "MAP22" && level.GetChecksum() ~== ID_MAP22;
	}

	static bool Face(int id) { return id >= GATE_FIRST && id <= FACE_LAST; }

	Line FindLine(int id)
	{
		let it = level.CreateLineIdIterator(id);
		int i = it.Next();
		if (i < 0) return null;
		return level.lines[i];
	}

	AjarFrame FindFrame(int id)
	{
		let it = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(it.Next())) if (f.args[0] == id) return f;
		return null;
	}

	AjarDoor DoorOf(int colour)
	{
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next())) if (d.args[1] == colour) return d;
		return null;
	}

	AjarHandler Ajar() { return AjarHandler(EventHandler.Find("AjarHandler")); }

	// how far a Doom door opens: to 4 under the lowest ceiling round it
	static double OpenTop(Sector s)
	{
		double low;
		Vertex v;
		[low, v] = s.FindLowestCeilingSurrounding();
		return low - 4;
	}

	static double Opening(Sector s)
	{
		return s.ceilingplane.ZAtPoint(s.centerspot) - s.floorplane.ZAtPoint(s.centerspot);
	}

	Array<Line> kept;            // the faces, by their notes
	Array<int> keptSpecial, keptA1, keptA2, keptA3;
	TextureID frameUpper;        // door 8's south face, its own upper texture (the door)

	override void WorldLoaded(WorldEvent e)
	{
		if (!(Lab() || Joined()) || e.IsSaveGame) return;
		let it = ThinkerIterator.Create("AjarDoomNote");
		AjarDoomNote n;
		while (n = AjarDoomNote(it.Next()))
		{
			on = true;
			Line l = level.lines[n.args[0]];
			Line d = l.getPortalDestination();
			Console.Printf("AJARTEST info line %d (id %d) after load: special %d (%d,%d,%d,%d) portal %d visual %d dest %d type %d flags %d align %d",
				n.args[0], n.tid, l.special, l.args[0], l.args[1], l.args[2], l.args[3], l.isLinePortal(), l.isVisualPortal(), d ? d.Index() : -1,
				l.getPortalType(), l.getPortalFlags(), l.getPortalAlignment());
			kept.Push(l);
			keptSpecial.Push(n.args[1]); keptA1.Push(n.args[2]); keptA2.Push(n.args[3]); keptA3.Push(n.args[4]);
			// Line_SetPortal has done its work: the Doom door gets its own special back. The door taken over
			// by Ajar's rules gets a frame's instead (Thing_Activate on its frame), its far face none.
			if (n.tid == 4051) l.special = 130;
			else if (n.tid == 4052) l.special = 0;
			else l.special = n.args[1];
			l.args[0] = n.tid == 4051 ? 4051 : 0;
			l.args[1] = n.tid >= 4050 ? 0 : n.args[2];
			l.args[2] = n.tid >= 4050 ? 0 : n.args[3];
			l.args[3] = n.tid >= 4050 ? 0 : n.args[4];
			l.args[4] = 0;
			if (n.tid == 4051) { l.flags |= Line.ML_REPEAT_SPECIAL; frameUpper = l.sidedef[0].GetTexture(Side.top); }
		}
		if (!on) return;
		// the bare links: C and W wait, switched off (a portal with no far side is a plain line)
		if (FindLine(4003)) level.ExecuteSpecial(107 /* Line_SetPortalTarget */, null, null, false, 4003, 0);
		if (FindLine(4004)) level.ExecuteSpecial(107, null, null, false, 4004, 0);
	}

	// While an Ajar door hangs in a Doom doorway, or a Doom doorway is its far
	// side, that doorway's door sector stands open (as Ajar's hung doors do):
	// its own motion (a DR door's wait and close) gives way. When no door
	// hangs there any more, it shuts.
	Array<Sector> held;
	Array<Line> heldBy;

	void HoldLine(int id, out Array<Sector> now, out Array<Line> by)
	{
		if (!Face(id)) return;
		Line l = FindLine(id);
		if (!l || !l.backsector) return;
		for (int i = 0; i < now.Size(); i++) if (now[i] == l.backsector) return;
		now.Push(l.backsector);
		by.Push(l);
	}

	void HoldTick()
	{
		Array<Sector> now;
		Array<Line> by;
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next()))
		{
			if (!d.frame) continue;
			HoldLine(d.frame.args[0], now, by);
			HoldLine(d.args[0], now, by);
		}
		for (int i = 0; i < now.Size(); i++)
		{
			Sector s = now[i];
			if (s.ceilingdata) s.ceilingdata.Destroy();
			double top = OpenTop(s);
			if (s.ceilingplane.ZAtPoint(s.centerspot) < top - 0.01) s.MoveCeiling(16, top, -1, 1, false);
		}
		for (int i = 0; i < held.Size(); i++)
		{
			bool still = false;
			for (int j = 0; j < now.Size(); j++) if (now[j] == held[i]) still = true;
			if (!still) level.ExecuteSpecial(10 /* Door_Close */, null, heldBy[i], false, 0, 64);
		}
		held.Move(now);
		heldBy.Move(by);
		// the door taken over: its empty frame shows Ajar's empty frame, not the door that is gone
		AjarFrame f = FindFrame(4051);
		Line fl = FindLine(4051);
		if (f && fl)
		{
			TextureID t = f.door ? frameUpper : TexMan.CheckForTexture(AjarHandler.FRAME_TEX, TexMan.Type_Any);
			if (TexMan.GetName(fl.sidedef[0].GetTexture(Side.top)) != TexMan.GetName(t)) fl.sidedef[0].SetTexture(Side.top, t);
		}
	}

	// USE on a Doom doorway that is a frame: with a door in the hands, or a
	// door hanging there, it is Ajar's (hang, take, swap); otherwise the Doom
	// door opens as Doom's.
	override void WorldLinePreActivated(WorldEvent e)
	{
		if (!on || e.ActivationType != SPAC_Use || !e.Thing || !e.Thing.player) return;
		let it = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(it.Next()))
		{
			if (!Gate(f.args[0]) || FindLine(f.args[0]) != e.ActivatedLine) continue;
			let h = Ajar();
			if (!h || (!h.carried && !f.door)) return;
			e.ShouldActivate = false;
			f.Activate(e.Thing);
			return;
		}
	}

	override void WorldTick()
	{
		if (!on) return;
		tic++;
		HoldTick();
		if (!Lab()) return;           // (the joined maps lab has the hold rule only; its tests are classic.zs's)
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		let mo = players[consoleplayer].mo;
		if (!mode || !mo) return;
		int t = tic;
		if (t == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			let ti = ThinkerIterator.Create("Actor");      // id's monsters are left for play by hand
			Actor a;
			while (a = Actor(ti.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
			Watch(mo);
		}
		WatchTick();
		MissileTick();
		if (mode == 1) { DoorLogTick(t); Walking(mo, t); }
		else if (mode == 2) Views(mo, t);
		else if (mode == 3) Shots(mo, t);
		else if (mode == 4) Moved(mo, t);
		else if (mode == 5) Carried(mo, t);
		else if (mode == 6) CarriedViews(mo, t);
	}

	// --- the tests' means -------------------------------------------------------
	Array<AjarDoomWatch> watches;
	Array<Actor> made;
	int mark;                    // the player's crossings so far, when a case began

	AjarDoomWatch Watch(Actor a)
	{
		let w = new("AjarDoomWatch");
		w.who = a;
		w.lastPos = a.pos;
		w.lastVel = a.vel;
		w.lastAngle = a.angle;
		watches.Push(w);
		return w;
	}

	AjarDoomWatch WatchOf(Actor a)
	{
		for (int i = 0; i < watches.Size(); i++) if (watches[i].who == a) return watches[i];
		return Watch(a);
	}

	// a crossing: the thing went further in one tic than its speed takes it
	// (a portal moves it in the same tic; a door's two faces are only 16 apart)
	void WatchTick()
	{
		for (int i = 0; i < watches.Size(); i++)
		{
			let w = watches[i];
			if (!w.who) continue;
			Actor a = w.who;
			Vector2 used = w.setVel.Length() > 0 ? w.setVel : w.lastVel.xy;
			if ((a.pos.xy - w.lastPos.xy).Length() > used.Length() + 8)
			{
				w.tics.Push(tic);
				w.fromX.Push(w.lastPos.x); w.fromY.Push(w.lastPos.y); w.fromZ.Push(w.lastPos.z);
				w.setX.Push(used.x); w.setY.Push(used.y);
				w.toX.Push(a.pos.x); w.toY.Push(a.pos.y); w.toZ.Push(a.pos.z);
				w.velX.Push(a.vel.x); w.velY.Push(a.vel.y);
				w.angBefore.Push(w.lastAngle); w.angAfter.Push(a.angle);
				if (stopOnJump.Find(a) != stopOnJump.Size()) a.vel = (0, 0, 0);
			}
			w.lastPos = a.pos;
			w.lastVel = a.vel;
			w.lastAngle = a.angle;
			w.setVel = (0, 0);
		}
	}

	double FloorAt(double x, double y)
	{
		Sector s = level.PointInSector((x, y));
		return s.floorplane.ZAtPoint((x, y));
	}

	void Pose(Actor mo, double x, double y, double ang)
	{
		mo.SetOrigin((x, y, FloorAt(x, y)), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
		let w = WatchOf(mo);
		w.lastPos = mo.pos;
		w.lastVel = mo.vel;
		w.lastAngle = ang;
		w.setVel = (0, 0);
		mark = WatchOf(players[consoleplayer].mo).Jumps();
	}

	// move a thing the way it faces from tic `from` for `tics` tics; `halt`: it stands still once it has crossed
	Array<Actor> stopOnJump;
	void Go(Actor a, int t, int from, int tics, double speed, bool halt = true)
	{
		if (!a) return;
		let w = WatchOf(a);
		if (t == from) { stopOnJump.Clear(); if (halt) stopOnJump.Push(a); }
		if (t >= from && t < from + tics)
		{
			if (halt && t > from && w.Jumps() && w.tics[w.Jumps() - 1] > from) return;     // crossed: stays where it came out
			Vector2 v = Actor.AngleToVector(a.angle, speed);
			a.vel.xy = v;
			w.setVel = v;
		}
		if (t == from + tics) a.vel.xy = (0, 0);
	}

	void Check(string what, bool ok, Actor mo = null)
	{
		if (mo) Console.Printf("AJARTEST %s=%d pos=(%.2f,%.2f,%.2f) angle=%.2f sector=%d", what, ok, mo.pos.x, mo.pos.y, mo.pos.z,
			Actor.Normalize180(mo.angle), mo.CurSector.Index());
		else Console.Printf("AJARTEST %s=%d", what, ok);
	}

	// crossing k of w was by line src (id) to line dst (id) as the engine's rule says: the place (the tic's
	// move carried through: dst.v2 + R(p - src.v1)), the height (aligned on the floors), the facing, the motion
	bool CrossedRight(AjarDoomWatch w, int k, int src, int dst, string what)
	{
		Line s = FindLine(src), d = FindLine(dst);
		if (k >= w.Jumps() || !s || !d)
		{
			Console.Printf("AJARTEST info %s: no crossing %d (%d in all)", what, k, w.Jumps());
			return false;
		}
		double rot = OneSideTest.Turn(s, d);
		Vector2 set = (w.setX[k], w.setY[k]);
		Vector2 want = OneSideTest.Through(s, d, (w.fromX[k], w.fromY[k]) + set);
		double wantZ = w.fromZ[k] - s.frontsector.floorplane.ZAtPoint(s.v1.p) + d.frontsector.floorplane.ZAtPoint(d.v2.p);
		Vector2 got = (w.toX[k], w.toY[k]);
		double posErr = (got - want).Length();
		double zErr = w.toZ[k] - wantZ;
		double angErr = Actor.DeltaAngle(w.angAfter[k], w.angBefore[k] + rot);
		Vector2 vel = (w.velX[k], w.velY[k]);
		double dirErr = set.Length() > 0 && vel.Length() > 0 ? Actor.DeltaAngle(VectorAngle(vel.x, vel.y), VectorAngle(set.x, set.y) + rot) : 0;
		Console.Printf("AJARTEST info %s: t=%d from (%.2f,%.2f,%.2f) moving (%.2f,%.2f) facing %.1f -> (%.2f,%.2f,%.2f) moving (%.2f,%.2f) facing %.1f; "
			.. "turn %.1f; place off by %.3f, height by %.3f, facing by %.3f, motion by %.3f", what, w.tics[k], w.fromX[k], w.fromY[k], w.fromZ[k],
			set.x, set.y, Actor.Normalize180(w.angBefore[k]), got.x, got.y, w.toZ[k], vel.x, vel.y, Actor.Normalize180(w.angAfter[k]),
			Actor.Normalize180(rot), posErr, zErr, angErr, dirErr);
		return posErr < 1 && abs(zErr) < 0.01 && abs(angErr) < 0.5 && abs(dirErr) < 0.5;
	}

	// the player crossed once since the case began, by src to dst, as the rule says
	bool OnceThrough(Actor mo, int src, int dst, string what)
	{
		let w = WatchOf(mo);
		return w.Jumps() == mark + 1 && CrossedRight(w, mark, src, dst, what);
	}

	bool NoCrossing(Actor mo) { return WatchOf(mo).Jumps() == mark; }

	bool InSec(Actor a, int s1, int s2 = -1, int s3 = -1)
	{
		if (!a) return false;
		int s = a.CurSector.Index();
		return s == s1 || s == s2 || s == s3;
	}

	Sector Sec(int i) { return level.sectors[i]; }
	double Open(int i) { return Opening(level.sectors[i]); }
	Line Ln(int i) { return level.lines[i]; }

	void Use(Actor mo, int line) { bool ok = level.lines[line].Activate(mo, 0, SPAC_Use); Console.Printf("AJARTEST info USE line %d: %d", line, ok); }
	void Link(int from, int to) { level.ExecuteSpecial(107, null, null, false, from, to); }
	void DoorOpen(int tag) { level.ExecuteSpecial(11 /* Door_Open */, null, null, false, tag, 64); }
	void DoorClose(int tag) { level.ExecuteSpecial(10 /* Door_Close */, null, null, false, tag, 64); }
	// a door sector put open or shut at once, whatever its own motion was (the tests' setting, not the game's)
	void SetOpen(int i, double h)
	{
		Sector s = level.sectors[i];
		if (s.ceilingdata) s.ceilingdata.Destroy();
		double f = s.floorplane.ZAtPoint(s.centerspot), c = s.ceilingplane.ZAtPoint(s.centerspot);
		s.MoveCeiling(4096, f + h, -1, f + h > c ? 1 : -1, false);
	}
	void ForceOpen(int i) { SetOpen(i, OpenTop(level.sectors[i]) - level.sectors[i].floorplane.ZAtPoint(level.sectors[i].centerspot)); }
	void ForceShut(int i) { SetOpen(i, 0); }
	void DoorOpenAt(int line) { level.ExecuteSpecial(11, null, level.lines[line], false, 0, 64); }

	Actor Make(class<Actor> what, double x, double y, double ang = 0)
	{
		Actor a = Actor.Spawn(what, (x, y, FloorAt(x, y)));
		a.angle = ang;
		made.Push(a);
		return a;
	}

	void ClearMade()
	{
		for (int i = 0; i < made.Size(); i++) if (made[i]) made[i].Destroy();
		made.Clear();
	}

	// --- MODE=1: walking, the doors' own motion, heights, widths, a monster ----
	Actor walker;
	string doorLog;
	double doorWas;
	int doorWay;

	// what door 56 does by itself, as it happens (its wait after Door_Raise)
	void DoorLogTick(int t)
	{
		double now = Open(56);
		int way = now > doorWas + 0.01 ? 1 : now < doorWas - 0.01 ? -1 : 0;
		if (way != doorWay) doorLog = doorLog .. String.Format("t=%d %s at %.0f; ", t, way > 0 ? "rising" : way < 0 ? "falling" : "still", now);
		doorWas = now;
		doorWay = way;
	}

	void Walking(Actor mo, int t)
	{
		if (t == 2)
		{
			Line a = FindLine(4001), b = FindLine(4002), c = FindLine(4003), w = FindLine(4004);
			Check("portalsMadeAtLoad", a && b && c && w && a.Index() == 314 && b.Index() == 333 && a.isLinePortal() && b.isLinePortal()
				&& a.getPortalDestination() == b && b.getPortalDestination() == a && a.getPortalType() == 1 && a.getPortalAlignment() == 1
				&& !c.isLinePortal() && !w.isLinePortal());
			Check("doorSpecialsBack", a.special == 12 && a.args[0] == 0 && a.args[1] == 64 && a.args[2] == 150 && (a.activation & SPAC_Use) != 0
				&& b.special == 11 && b.args[0] == 0 && b.args[1] == 64);
			// the hidden names: what a map name loads here
			string m1 = LevelInfo.MapChecksum("MAP01"), m7 = LevelInfo.MapChecksum("MAP07"), m21 = LevelInfo.MapChecksum("MAP21");
			Console.Printf("AJARTEST info MAP01 here: %s (id's 3C9902E376CCA1E9C3BE8763BDC21DF5), MAP07: %s (id's 291F24417FB3DD411339AE82EF9B3597), "
				.. "MAP21: %s (id's EBDAC00E9D25D884B2C8F4B1F0390539), MAP22: %s", m1, m7, m21, level.GetChecksum());
			Check("map22IsIds", level.GetChecksum() ~== "4AA9B3CE449FB614497756E96509F096");
			Check("map01IsAjarsNotIds", !(m1 ~== "3C9902E376CCA1E9C3BE8763BDC21DF5"));
			Check("map07IsAjarsNotIds", !(m7 ~== "291F24417FB3DD411339AE82EF9B3597"));
			Check("map21IsIds", m21 ~== "EBDAC00E9D25D884B2C8F4B1F0390539");
		}
		// the Doom door shut: its face is a wall, portal or not
		if (t == 10) Pose(mo, -160, -200, 270);
		Go(mo, t, 10, 25, WALK);
		if (t == 40) Check("shutDoorBlocks", NoCrossing(mo) && InSec(mo, 54) && mo.pos.y > -266 && Open(56) < 1, mo);
		// USE opens it as ever: its own special, Door_Raise (speed 64: 8 a tic)
		if (t == 42) Use(mo, 314);
		if (t == 55) Check("useOpensTheDoor", Open(56) > 64 && Ln(314).special == 12, mo);
		// A open, B shut: the far door is asked too (the engine checks the room the box would have beyond the far face)
		if (t == 56) Pose(mo, -160, -200, 270);
		Go(mo, t, 56, 25, WALK);
		if (t == 84) Check("farDoorShutBlocksAToB", NoCrossing(mo) && InSec(mo, 54) && mo.pos.y > -270 && Open(120) < 1, mo);
		// B's door, from the start room: shut, a wall; USE opens it (Door_Open, for good)
		if (t == 86) Pose(mo, -736, 60, 90);
		Go(mo, t, 86, 15, WALK);
		if (t == 104) Check("shutFarDoorIsAWall", NoCrossing(mo) && mo.pos.y > 120 && mo.pos.y < 129, mo);
		if (t == 105) Use(mo, 333);
		// half open, 40 of the player's 56: still no way through; 64: through
		if (t == 109) Console.Printf("AJARTEST info door 120 open %.1f at t=109", Open(120));
		if (t == 110) { ForceShut(120); SetOpen(120, 40); Pose(mo, -160, -200, 270); }
		Go(mo, t, 110, 25, WALK);
		if (t == 138) Check("farDoorOpen40Blocks", NoCrossing(mo) && InSec(mo, 54), mo);
		if (t == 140) { SetOpen(120, 64); Pose(mo, -160, -200, 270); }
		Go(mo, t, 140, 25, WALK);
		if (t == 168) Check("farDoorOpen64Passes", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "farDoorOpen64Passes"), mo);
		// both put open for good from here (A's own wait would shut it at t=202: logged at the end)
		if (t == 170) { ForceOpen(120); ForceOpen(56); }
		// through it: A (floor 48) to B (floor -240), both open
		if (t == 172) Pose(mo, -160, -200, 270);
		Go(mo, t, 172, 25, WALK);
		if (t == 200) Check("walkAToB", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "walkAToB"), mo);
		if (t == 202) Pose(mo, -160, -180, 270);
		Go(mo, t, 202, 15, RUN);
		if (t == 220) Check("runAToB", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "runAToB"), mo);
		if (t == 222) Pose(mo, -150, -200, 260);
		Go(mo, t, 222, 25, WALK);
		if (t == 250) Check("slantAToB", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "slantAToB"), mo);
		// back: B (floor -240) up to A (floor 48)
		if (t == 252) Pose(mo, -736, 0, 90);
		Go(mo, t, 252, 25, WALK);
		if (t == 280) Check("walkBToA", InSec(mo, 54, 52) && OnceThrough(mo, 4002, 4001, "walkBToA"), mo);
		if (t == 282) Pose(mo, -736, -20, 90);
		Go(mo, t, 282, 15, RUN);
		if (t == 300) Check("runBToA", InSec(mo, 54, 52) && OnceThrough(mo, 4002, 4001, "runBToA"), mo);
		// A shut again (forced; Doom's own wait is logged): B to A is a wall too, as A to B was with B shut
		if (t == 302) { Pose(mo, -160, -200, 270); ForceShut(56); }       // (not with the player in its way: it would not come down)
		if (t == 304) Pose(mo, -160, -200, 270);
		Go(mo, t, 304, 25, WALK);
		if (t == 332) Check("shutAgainBlocks", NoCrossing(mo) && InSec(mo, 54), mo);
		if (t == 334) Pose(mo, -736, 0, 90);
		Go(mo, t, 334, 25, WALK);
		if (t == 362) Check("farDoorShutBlocksBToA", NoCrossing(mo) && mo.pos.y < 144, mo);
		// through A's door from behind (its other face, line 317): a plain door
		if (t == 364) { Pose(mo, -160, -310, 90); Use(mo, 317); }
		Go(mo, t, 375, 25, WALK);
		if (t == 403) Check("plainFromBehind", InSec(mo, 52, 54) && NoCrossing(mo) && Open(56) > 56, mo);
		// an imp walked through, both ways
		if (t == 405) { ForceOpen(56); walker = Make("DoomImp", -160, -200, 270); Watch(walker); }
		Go(walker, t, 406, 25, WALK);
		if (t == 434) Check("impWalksAToB", InSec(walker, 109, 119) && WatchOf(walker).Jumps() == 1 && CrossedRight(WatchOf(walker), 0, 4001, 4002, "impWalksAToB"), walker);
		if (t == 436) { walker.SetOrigin((-736, 0, FloorAt(-736, 0)), false); walker.angle = 90; WatchOf(walker).lastPos = walker.pos; WatchOf(walker).lastAngle = 90; }
		Go(walker, t, 437, 25, WALK);
		if (t == 466) Check("impWalksBToA", InSec(walker, 54, 52) && WatchOf(walker).Jumps() == 2 && CrossedRight(WatchOf(walker), 1, 4002, 4001, "impWalksBToA"), walker);
		if (t == 468) ClearMade();

		// widths: A (64) joined to W (128), both doors open
		if (t == 470) { Link(4001, 4004); Link(4004, 4001); Link(4002, 0); ForceOpen(56); ForceOpen(58); }
		// W's north half (the end the rule pins to A's far end) lands on A
		if (t == 472) Pose(mo, 40, -160, 0);
		Go(mo, t, 472, 20, WALK);
		if (t == 496) Check("wideNorthHalfToA", InSec(mo, 54) && OnceThrough(mo, 4004, 4001, "wideNorthHalfToA"), mo);
		// W's south half lands beyond A's end, where the map has no room
		if (t == 498) Pose(mo, 40, -224, 0);
		Go(mo, t, 498, 20, WALK);
		if (t == 522)
		{
			Sector s = level.PointInSector(mo.pos.xy);
			Console.Printf("AJARTEST info wideSouthHalf: at (%.1f,%.1f,%.1f), its sector %d (floor %.0f, ceiling %.0f); A runs x -192 to -128",
				mo.pos.x, mo.pos.y, mo.pos.z, s.Index(), s.floorplane.ZAtPoint(mo.pos.xy), s.ceilingplane.ZAtPoint(mo.pos.xy));
			Check("wideSouthHalfLandsBeyondA", OnceThrough(mo, 4004, 4001, "wideSouthHalf") && mo.pos.x > -128 + 16, mo);
		}
		// ... and can it walk on from there? (each way in turn)
		// it stands south of the hall's wall (y -256), outside every room: the engine's map puts it in the hall 52
		if (t == 523) Check("wideSouthHalfInTheVoid", InSec(mo, 52) && mo.pos.y < -256 - 16, mo);
		if (t == 524) mo.angle = 90;
		Go(mo, t, 524, 10, WALK, false);
		if (t == 535) { Console.Printf("AJARTEST info wideSouthHalf: walked north 10 tics: at (%.1f,%.1f)", mo.pos.x, mo.pos.y); mo.angle = 270; }
		Go(mo, t, 535, 10, WALK, false);
		if (t == 546) { Console.Printf("AJARTEST info wideSouthHalf: walked south 10 tics: at (%.1f,%.1f)", mo.pos.x, mo.pos.y); mo.angle = 0; }
		Go(mo, t, 546, 10, WALK, false);
		if (t == 557) { Console.Printf("AJARTEST info wideSouthHalf: walked east 10 tics: at (%.1f,%.1f)", mo.pos.x, mo.pos.y); mo.angle = 180; }
		Go(mo, t, 557, 10, WALK, false);
		if (t == 568) Console.Printf("AJARTEST info wideSouthHalf: walked west 10 tics: at (%.1f,%.1f), sector %d", mo.pos.x, mo.pos.y, mo.CurSector.Index());
		// A to W: lands in W's south half (the rule pins A's near end to W's far end)
		if (t == 570) Pose(mo, -160, -200, 270);
		Go(mo, t, 570, 25, WALK);
		if (t == 598) Check("narrowToWideSouthHalf", InSec(mo, 52) && OnceThrough(mo, 4001, 4004, "narrowToWide") && mo.pos.y < -192, mo);
		if (t == 600) Console.Printf("AJARTEST info door 56: Doom's own motion seen in this run: %s", doorLog);
		if (t == 602) Console.Printf("AJARTEST walkingDone=1");
	}

	// --- MODE=2: views (tools/smoke_MAP22_2.cfg shoots every 40 tics) --------
	void Views(Actor mo, int t)
	{
		static const double views[] = {
			-160, -200, 270,      // 0 the hall 52, A shut: the Doom door
			-160, -200, 270,      // 1 A open: the start room through it
			-160, -262, 270,      // 2 close, in the lobby 54
			-60, -150, 235,       // 3 at a slant from the hall
			-736, -60, 90,        // 4 the start room, B shut
			-736, -60, 90,        // 5 B open: the lobby and the hall
			-736, 120, 90,        // 6 close
			-40, -192, 0,         // 7 W (128) joined to A (64): from the hall
			-160, -262, 270,      // 8 A joined to W, from the lobby: the hall from W
			-160, -200, 270,      // 9 A joined to C: the big room 2
			-32, 820, 90,         // 10 the big room: C, the lobby and hall
			-160, -200, 270       // 11 A opening slowly: the view grows with the door
		};
		int i = t / 40;
		if (i >= views.Size() / 3) return;
		if (t == 40) DoorOpen(13);
		if (t == 200) DoorOpen(14);
		if (t == 280) { Link(4001, 4004); Link(4004, 4001); Link(4002, 0); DoorOpen(9); }
		if (t == 360) { Link(4001, 4003); Link(4003, 4001); Link(4004, 0); DoorOpenAt(155); }
		if (t == 440) ForceShut(56);
		if (t == 446) level.ExecuteSpecial(11, null, null, false, 13, 16);   // 2 a tic
		Pose(mo, views[i * 3], views[i * 3 + 1], views[i * 3 + 2]);
		if (t % 40 == 0) Console.Printf("AJARTEST view=%d at (%.0f,%.0f) facing %.0f", i, views[i * 3], views[i * 3 + 1], views[i * 3 + 2]);
		if (t % 40 == 20) Console.Printf("AJARTEST info view %d: door 56 open %.1f, door 120 %.1f, door 58 %.1f, door 8 %.1f", i, Open(56), Open(120), Open(58), Open(8));
	}

	// --- MODE=3: shots ---------------------------------------------------------
	// dummies: 0 the start room, beyond B; 1 behind A's door (the room 62); 2 the hall 52, beyond A;
	// 3 the secret room 85, behind B's door
	Array<OneSideDummy> dummies;
	Actor missile;
	Vector3 missileLast;

	void Zero() { for (int i = 0; i < dummies.Size(); i++) if (dummies[i]) { dummies[i].hits = 0; dummies[i].by = ""; } }

	string Hit()
	{
		static const string names[] = { "startRoom", "behindA", "hall", "behindB" };
		string s = "";
		for (int i = 0; i < dummies.Size(); i++)
			if (dummies[i] && dummies[i].hits) s = s .. names[i] .. "(" .. dummies[i].hits .. " by " .. dummies[i].by .. ") ";
		return s == "" ? "nothing" : s;
	}

	void MissileTick()
	{
		if (missile && !missile.InStateSequence(missile.CurState, missile.ResolveState("Death"))) missileLast = missile.pos;
	}

	Actor puff;
	double puffY;

	void ShotCase(Actor mo, int t, int at, double x, double y, double ang, int kind, string what, int want)
	{
		if (t == at) Pose(mo, x, y, ang);
		if (t == at + 2)
		{
			Zero();
			puff = null;
			if (kind == 0)
			{
				int dmg;
				[puff, dmg] = mo.LineAttack(mo.angle, 4096, 0, 5, 'Hitscan', "BulletPuff");
				puffY = puff ? puff.pos.y : 99999;
				Console.Printf("AJARTEST info %s: fired from (%.1f,%.1f,%.1f) facing %.1f, hit %s, puff %s", what, mo.pos.x, mo.pos.y, mo.pos.z, mo.angle, Hit(),
					puff ? String.Format("(%.1f,%.1f,%.1f)", puff.pos.x, puff.pos.y, puff.pos.z) : "none");
			}
			else if (kind == 3) missile = mo.SpawnPlayerMissile("Rocket", ang);
			else
			{
				Vector2 p = mo.pos.xy + Actor.AngleToVector(mo.angle, 20);
				missile = Actor.Spawn(kind == 1 ? "Rocket" : "DoomImpBall", (p, mo.pos.z + 32));
				missile.target = mo;
				missile.angle = mo.angle;
				missile.vel = (Actor.AngleToVector(mo.angle, missile.speed), 0);
			}
			if (missile) missileLast = missile.pos;
		}
		if (t == at + 80)
		{
			if (kind) Console.Printf("AJARTEST info %s: %s from (%.1f,%.1f) facing %.1f, hit %s, burst at (%.1f,%.1f,%.1f)", what,
				kind == 2 ? "an imp's fireball" : "a rocket", x, y, ang, Hit(), missileLast.x, missileLast.y, missileLast.z);
			int others = 0;
			for (int i = 0; i < dummies.Size(); i++) if (dummies[i] && i != want) others += dummies[i].hits;
			if (want >= 0) Check(what, dummies[want] && dummies[want].hits > 0 && others == 0, mo);
			// none wanted: the shot stops on the shut door
			else if (kind == 0) Check(what, others == 0 && abs(puffY + 280) < 8, mo);
			else Check(what, others == 0 && abs(missileLast.y + 280) < 24, mo);
		}
	}

	void Shots(Actor mo, int t)
	{
		if (t == 2)
		{
			dummies.Push(OneSideDummy(Make("OneSideDummy", -736, -60)));
			dummies.Push(OneSideDummy(Make("OneSideDummy", -160, -332)));
			dummies.Push(OneSideDummy(Make("OneSideDummy", -160, -120)));
			dummies.Push(OneSideDummy(Make("OneSideDummy", -736, 230)));
			ForceOpen(56); ForceOpen(120);
		}
		static const double cases[] = {
			// x, y, facing, kind (0 hitscan, 1 rocket, 2 imp's fireball, 3 the player's own rocket), which dummy
			-160, -200, 270, 0, 0,     // A to B: down 288
			-736, 0, 90, 0, 2,         // B to A: up 288
			-160, -200, 270, 1, 0,
			-160, -200, 270, 2, 0,
			-736, 0, 90, 1, 2,
			-736, 0, 90, 2, 2,
			-160, -268, 270, 3, 0,     // the player's rocket from 12 off A's face (put 10 ahead of him: AjarOddFaces carries it)
			-160, -200, 270, 0, -1,    // A shut (at t=636): the bullet stops on the door
			-160, -200, 270, 1, -1     // and the rocket
		};
		static const string names[] = { "hitscanAToB", "hitscanBToA", "rocketAToB", "impBallAToB", "rocketBToA", "impBallBToA",
			"playerRocketCloseToA", "hitscanAShut", "rocketAShut" };
		if (t == 636) { Pose(mo, -160, -200, 270); ForceShut(56); }
		for (int i = 0; i < 9; i++)
			ShotCase(mo, t, 10 + 90 * i, cases[i * 5], cases[i * 5 + 1], cases[i * 5 + 2], int(cases[i * 5 + 3]), names[i], int(cases[i * 5 + 4]));
		if (t == 10 + 90 * 9) Console.Printf("AJARTEST shotsDone=1");
	}

	// --- MODE=4: the link moved, A-B to A-C, and cut (as Hang and Unhang do it)
	void Moved(Actor mo, int t)
	{
		if (t == 2) { ForceOpen(56); ForceOpen(120); ForceOpen(8); }
		if (t == 10) Pose(mo, -160, -200, 270);
		Go(mo, t, 10, 25, WALK);
		if (t == 38) Check("joinedAToB", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "joinedAToB"), mo);
		// moved: A to C (the big room 2, floor 72) and back, B cut
		if (t == 40) { Link(4001, 4003); Link(4003, 4001); Link(4002, 0); }
		if (t == 42) Pose(mo, -160, -200, 270);
		Go(mo, t, 42, 25, WALK);
		if (t == 70) Check("movedAToC", InSec(mo, 2) && OnceThrough(mo, 4001, 4003, "movedAToC"), mo);
		if (t == 72) Pose(mo, -32, 820, 90);
		Go(mo, t, 72, 25, WALK);
		if (t == 100) Check("movedCToA", InSec(mo, 54) && OnceThrough(mo, 4003, 4001, "movedCToA"), mo);
		// B cut: its door is a plain door into the secret room 85
		if (t == 102) Pose(mo, -736, 0, 90);
		Go(mo, t, 102, 30, WALK, false);
		if (t == 135) Check("cutBIsPlain", NoCrossing(mo) && mo.pos.y > 176, mo);
		// A cut too (and C): A's door is a plain door into the room 55 behind it
		if (t == 137) { Link(4001, 0); Link(4003, 0); Pose(mo, -160, -200, 270); }
		Go(mo, t, 137, 16, WALK, false);
		if (t == 156) Check("cutAIsPlain", NoCrossing(mo) && InSec(mo, 55, 62, 56), mo);
		if (t == 158) Pose(mo, -32, 860, 90);
		Go(mo, t, 158, 8, WALK, false);
		if (t == 172) Check("cutCIsPlain", NoCrossing(mo) && InSec(mo, 5, 8), mo);
		// joined again, A-B, as at first
		if (t == 174) { Link(4001, 4002); Link(4002, 4001); Pose(mo, -160, -200, 270); }
		Go(mo, t, 174, 25, WALK);
		if (t == 202) Check("joinedAgainAToB", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "joinedAgainAToB"), mo);
		if (t == 204) Console.Printf("AJARTEST movedDone=1");
	}

	// --- MODE=5: carried doors in Doom doorways ---------------------------------
	void Carried(Actor mo, int t)
	{
		let h = Ajar();
		AjarDoor red = DoorOf(1), yellow = DoorOf(4);
		AjarFrame fa = FindFrame(4001), f8 = FindFrame(4051);
		if (t == 2)
		{
			Check("framesAtLoad", fa && f8 && red && yellow && !red.frame && !red.carried && f8.door == yellow && !fa.door
				&& Ln(155).isLinePortal() && Ln(156).isLinePortal() && Ln(155).getPortalDestination() == Ln(156)
				&& !Ln(314).isLinePortal() && !Ln(333).isLinePortal() && Ln(314).special == 12 && Ln(155).special == 130 && Ln(156).special == 0);
		}
		// door 8, taken over: hung in its own doorway at the start, it stands open and leads where it always led
		if (t == 20) Check("ownDoorStandsOpen", Open(8) > 56, mo);
		if (t == 22) Pose(mo, -32, 850, 90);
		Go(mo, t, 22, 20, WALK);
		if (t == 45) Check("ownDoorLeadsOn", InSec(mo, 5) && OnceThrough(mo, 4051, 4052, "ownDoorLeadsOn"), mo);
		// unhinged: USE on its doorway from the big room takes it; the doorway is an empty frame, the door shuts
		if (t == 47) { Pose(mo, -32, 880, 90); Use(mo, 155); }
		if (t == 62)
			Check("doomDoorTaken", h.carried == yellow && !f8.door && !Ln(155).isLinePortal() && !Ln(156).isLinePortal() && Open(8) < 1
				&& TexMan.GetName(Ln(155).sidedef[0].GetTexture(Side.top)) ~== AjarHandler.FRAME_TEX, mo);
		if (t == 64) Pose(mo, -32, 860, 90);
		Go(mo, t, 64, 15, WALK);
		if (t == 82) Check("emptyFrameBlocks", NoCrossing(mo) && InSec(mo, 2), mo);
		// from the closet its far face does not open (no special now)
		if (t == 84) { Pose(mo, -32, 944, 270); Use(mo, 156); }
		if (t == 95) Check("farFaceStaysShut", Open(8) < 1, mo);
		// hung in A (a Doom door kept as one): both doorways stand open
		if (t == 97) { Pose(mo, -160, -262, 270); Use(mo, 314); }
		if (t == 115) Check("hungInDoomDoorway", fa.door == yellow && !h.carried && Ln(314).isLinePortal() && Ln(314).getPortalDestination() == Ln(156)
			&& Ln(156).getPortalDestination() == Ln(314) && Open(56) > 56 && Open(8) > 56, mo);
		// through it: out of the closet's face, into the closet it opened onto
		if (t == 117) Pose(mo, -160, -200, 270);
		Go(mo, t, 117, 25, WALK);
		if (t == 145) Check("intoTheRoomItOpenedOnto", InSec(mo, 5) && OnceThrough(mo, 4001, 4052, "intoTheRoomItOpenedOnto"), mo);
		if (t == 147) Pose(mo, -32, 944, 270);
		Go(mo, t, 147, 25, WALK);
		// ... but not back: door 8 is 16 deep, and its other face, the empty frame, is solid (Ajar's rule):
		// the box of whoever walks into the closet's face reaches it before the middle crosses
		if (t == 175) Check("backOutBlockedByTheEmptyFrame", NoCrossing(mo) && InSec(mo, 5) && mo.pos.y < 944, mo);
		// the same with the empty frame left open (not solid): back out it is
		if (t == 177) { Ln(155).flags &= ~(Line.ML_BLOCKING | Line.ML_BLOCKEVERYTHING | Line.ML_SOUNDBLOCK); Pose(mo, -32, 944, 270); }
		Go(mo, t, 177, 25, WALK);
		if (t == 205) Check("backOutWithTheEmptyFrameOpen", InSec(mo, 54) && OnceThrough(mo, 4052, 4001, "backOutWithTheEmptyFrameOpen"), mo);
		// ... and then the empty frame is a plain hole from the big room into the closet (its far face acts for its front only)
		if (t == 207) Pose(mo, -32, 860, 90);
		Go(mo, t, 207, 10, WALK, false);
		if (t == 225) Check("theOpenEmptyFrameIsAPlainHole", NoCrossing(mo) && InSec(mo, 5, 8), mo);
		if (t == 227) Ln(155).flags |= Line.ML_BLOCKING | Line.ML_BLOCKEVERYTHING | Line.ML_SOUNDBLOCK;
		// the empty frame, solid again, its door sector open: Ajar's empty frame drawn in it
		if (t == 229) Pose(mo, -32, 860, 90);
		Go(mo, t, 229, 15, WALK);
		if (t == 247) Check("emptyFrameSolidWhileOpen", NoCrossing(mo) && InSec(mo, 2) && Open(8) > 56, mo);
		// A's other face used (Door_Raise on a held door): it stays open past Doom's wait
		if (t == 249) { Pose(mo, -160, -312, 90); Use(mo, 317); }
		if (t == 400) Check("heldPastDoomsWait", Open(56) > 56 && Open(8) > 56, mo);
		// taken out of A: both doors shut, A a plain Doom door again
		if (t == 402) { Pose(mo, -160, -262, 270); Use(mo, 314); }
		if (t == 420) Check("takenFromDoomDoorway", h.carried == yellow && !fa.door && !Ln(314).isLinePortal() && Open(56) < 1 && Open(8) < 1, mo);
		// back in its own doorway
		if (t == 422) { Pose(mo, -32, 880, 90); Use(mo, 155); }
		if (t == 440) Check("backInItsOwnDoorway", f8.door == yellow && !h.carried && Open(8) > 56
			&& TexMan.GetName(Ln(155).sidedef[0].GetTexture(Side.top)) == TexMan.GetName(frameUpper), mo);
		if (t == 442) Pose(mo, -32, 850, 90);
		Go(mo, t, 442, 20, WALK);
		if (t == 465) Check("leadsOnAgain", InSec(mo, 5) && OnceThrough(mo, 4051, 4052, "leadsOnAgain"), mo);
		// A empty, nothing carried: USE opens the Doom door, and it is plain
		if (t == 467) { Pose(mo, -160, -262, 270); Use(mo, 314); }
		if (t == 470) Pose(mo, -160, -200, 270);
		Go(mo, t, 470, 25, WALK, false);
		if (t == 498) Check("emptyDoomFrameIsItsDoor", NoCrossing(mo) && mo.pos.y < -296 && !fa.door, mo);
		// Ajar's RED door, its far side B: picked up, hung in A
		if (t == 500) { Pose(mo, -60, -180, 270); red.Used(mo); }
		if (t == 502) Check("tookRed", h.carried == red, mo);
		if (t == 504) { Pose(mo, -160, -262, 270); Use(mo, 314); }
		if (t == 520) Check("redHungInA", fa.door == red && !h.carried && Ln(314).getPortalDestination() == Ln(333)
			&& Ln(333).getPortalDestination() == Ln(314) && Open(56) > 56 && Open(120) > 56, mo);
		if (t == 522) Pose(mo, -160, -200, 270);
		Go(mo, t, 522, 25, WALK);
		if (t == 550) Check("throughRedAToB", InSec(mo, 109, 119) && OnceThrough(mo, 4001, 4002, "throughRedAToB"), mo);
		if (t == 552) Pose(mo, -736, 0, 90);
		Go(mo, t, 552, 25, WALK);
		if (t == 580) Check("throughRedBToA", InSec(mo, 54) && OnceThrough(mo, 4002, 4001, "throughRedBToA"), mo);
		if (t == 582) { Pose(mo, -160, -262, 270); Use(mo, 314); }
		if (t == 600) Check("redTakenDown", h.carried == red && !fa.door && !Ln(314).isLinePortal() && !Ln(333).isLinePortal() && Open(56) < 1 && Open(120) < 1, mo);
		if (t == 602) Console.Printf("AJARTEST carriedDone=1");
	}

	// --- MODE=6: views of the carried doors (tools/smoke_MAP22_6.cfg) ---------
	void CarriedViews(Actor mo, int t)
	{
		static const double views[] = {
			-32, 820, 90,         // 0 the big room: door 8, hung in its own doorway, stands open onto the closet
			-32, 820, 90,         // 1 taken: an empty frame
			-32, 950, 270,        // 2 the closet: door 8's far face, shut
			-160, -200, 270,      // 3 YELLOW hung in A: the closet through it
			-32, 820, 90,         // 4 the big room: the empty frame while door 8 stands open
			-32, 950, 270,        // 5 the closet: the lobby and the hall through door 8's far face
			-160, -200, 270,      // 6 RED hung in A: the start room through it
			-736, -60, 90,        // 7 the start room: the lobby and hall through B
			-60, -150, 235        // 8 the hall at a slant: RED's leaf by A
		};
		let h = Ajar();
		int i = t / 40;
		if (i >= views.Size() / 3) return;
		if (t == 40) { Pose(mo, -32, 880, 90); Use(mo, 155); }
		if (t == 120) { Pose(mo, -160, -262, 270); Use(mo, 314); }
		if (t == 240)
		{
			Pose(mo, -160, -262, 270); Use(mo, 314);           // YELLOW out of A
			Pose(mo, -32, 880, 90); Use(mo, 155);              // back in its own doorway
			Pose(mo, -60, -180, 270); DoorOf(1).Used(mo);      // RED
			Pose(mo, -160, -262, 270); Use(mo, 314);           // into A
		}
		Pose(mo, views[i * 3], views[i * 3 + 1], views[i * 3 + 2]);
		if (t % 40 == 0) Console.Printf("AJARTEST view=%d at (%.0f,%.0f) facing %.0f", i, views[i * 3], views[i * 3 + 1], views[i * 3 + 2]);
		if (t % 40 == 20) Console.Printf("AJARTEST info view %d: carried %s, door 56 open %.1f, door 120 %.1f, door 8 %.1f", i,
			h.carried ? h.carried.Label() : "-", Open(56), Open(120), Open(8));
	}
}
