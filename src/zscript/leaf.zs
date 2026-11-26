// A hung door's leaf and the walls round its frame; USE at a switch beside a door (PLAN.md, "Doors: the open leaf
// keeps clear of walls; USE at a lever works the lever; the clocked door is look 3 (2026-11-26)").
//
// The leaf. A door hung in a frame stands open at a jamb: hinged 16 out from the frame line (on the room's wall, at
// the mouth of the recess), 64 long, a wall sprite. Until 2026-11-26 every leaf was hinged at the jamb of the frame
// line's first end and swung open 115 degrees, whatever stood beside the frame; in MAP21's machine (a wall 16 from
// each jamb) the leaf went into the wall. Now, when a door is hung (Hang, PoseLeaf), its leaf is checked against the
// walls round the frame (AjarLeafRoom.Clear): one-sided lines, and two-sided lines whose opening is lower than the
// leaf or whose floor is higher than its foot (whatever the leaf would be drawn through; things, furniture, are not
// walls). Then:
//   - posed as it always was, if that is clear by 2 everywhere (so no frame where it was right looks different);
//   - else hinged on the other jamb, mirrored, if that is clear;
//   - else opened less, to the widest angle at which it is clear at either jamb (the first jamb's on a tie; to about
//     a thousandth of a degree): in MAP21's machine 102.64, a little past square;
//   - and if no angle is clear at either jamb (MAP33's frame 101, whose recess is 16 below the floor in front of it),
//     as it always was.
// The clocked door and its shadow, hung in the same frame at both times, are posed alike, by the tighter of the two.
// tools/leafcheck.py does the same reckoning over the built maps and lists the frames that are not as they were.
//
// USE. The engine's use trace (P_UseTraverse) meets a door's box (radius 20, standing out from the frame) before
// the wall piece beside the frame, and calls the door's Used; a door whose Used returns false lets the trace go
// on to whatever comes next along it (a line with a use special: a lever, a switch, a desk's panel). So a door takes
// a USE only when the aim is at it (UseGoesOn): when the first thing along the aim (from the player, flat, along
// where they face, as the engine's trace) is a switch of its own, before the door's leaf as it stands and before its
// frame's opening, the press goes on to the switch. Aimed at the door, at its frame, or at a plain wall with the
// door in reach, the door is used as before. A door leaning by a switch is the same (its leaf: its face).

class AjarLeafRoom : Object play
{
	const LEN = 64.0;          // the leaf's width
	const OPEN = 115.0;        // how far a leaf always stood open, in degrees from shut
	const GAP = 2.0;           // how far it keeps off a wall
	const DEPTH = 16.0;        // the hinge: this far out from the frame line, on the recess's mouth (ajarmap.DEPTH)
	const TALL = 96.0;         // the leaf's height
	Line l;                    // the frame line
	double z;                  // the leaf's foot
	Array<int> walls;          // the lines round the frame that the leaf must keep off (level.lines indices)

	static AjarLeafRoom Of(AjarFrame f)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		Line l = h ? h.FindLine(f.args[0]) : null;
		if (!l) return null;
		let r = new("AjarLeafRoom");
		r.l = l;
		r.z = f.pos.z;
		Vector2 mid = l.v1.p + l.delta / 2;
		double reach = l.delta.Length() / 2 + DEPTH + LEN + 2 * GAP;
		let it = BlockLinesIterator.CreateFromPos((mid, r.z), TALL, reach);
		while (it.Next())
		{
			Line w = it.CurLine;
			int i = w.Index();
			if (r.walls.Find(i) < r.walls.Size()) continue;
			if (SegDist(mid, w.v1.p, w.v2.p) < reach && r.Solid(w, mid)) r.walls.Push(i);
		}
		return r;
	}

	// A wall to the leaf: one-sided, or an opening lower than the leaf or a floor higher than its foot.
	bool Solid(Line w, Vector2 near)
	{
		if (!w.frontsector || !w.backsector) return true;
		Vector2 p = Closest(near, w.v1.p, w.v2.p);
		double top = min(w.frontsector.ceilingplane.ZatPoint(p), w.backsector.ceilingplane.ZatPoint(p));
		double bottom = max(w.frontsector.floorplane.ZatPoint(p), w.backsector.floorplane.ZatPoint(p));
		return top < z + TALL - 1 || bottom > z + 1;
	}

	// The leaf hinged at the frame line's first end (or, mirrored, its second) and `ang` degrees open from shut: its
	// hinge, and the way it runs from there.
	Vector2 Hinge(bool mirrored)
	{
		Vector2 dir = l.delta.Unit();
		return (mirrored ? l.v2.p : l.v1.p) + (dir.y, -dir.x) * DEPTH;
	}
	Vector2 Way(bool mirrored, double ang)
	{
		Vector2 dir = l.delta.Unit();
		Vector2 n = (dir.y, -dir.x);                       // into the room
		if (!mirrored && ang == OPEN) return n * cos(25) - dir * sin(25);      // to the bit as it always stood
		Vector2 shut = mirrored ? -dir : dir;
		return shut * cos(ang) + n * sin(ang);
	}

	// The leaf so posed keeps GAP off every wall, and stands on open floor all along.
	bool Clear(bool mirrored, double ang)
	{
		Vector2 h = Hinge(mirrored), u = Way(mirrored, ang);
		Vector2 e = h + u * LEN;
		for (int k = 0; k < walls.Size(); k++)
		{
			Line w = level.lines[walls[k]];
			Vector2 a = w.v1.p, b = w.v2.p;
			if (SegDist(h, a, b) < 1)
			{
				// a wall at the hinge (the room's wall beside the frame, the recess's side): the leaf's end and
				// the wall's other end count; which side of it the leaf is on, the floor below tells
				if (SegDist(e, a, b) < GAP) return false;
				if ((a - h).Length() >= 1 && SegDist(a, h, e) < GAP) return false;
				if ((b - h).Length() >= 1 && SegDist(b, h, e) < GAP) return false;
				continue;
			}
			if (Crosses(h, e, a, b)) return false;
			if (SegDist(e, a, b) < GAP || SegDist(a, h, e) < GAP || SegDist(b, h, e) < GAP) return false;
		}
		// every 4 along the leaf from 2 out: in the map, on a floor no higher than its foot, under a ceiling no lower
		// than its top
		for (int k = 0; k < 17; k++)
		{
			Vector2 p = h + u * min(2.0 + 4 * k, LEN);
			if (!level.IsPointInLevel((p, z + TALL / 2))) return false;
			Sector s = level.PointInSector(p);
			if (s.floorplane.ZatPoint(p) > z + 1 || s.ceilingplane.ZatPoint(p) < z + TALL - 1) return false;
		}
		return true;
	}

	// Clear here and, with g, there too (the clocked door's two frames).
	static bool ClearBoth(AjarLeafRoom r, AjarLeafRoom g, bool mirrored, double ang)
	{
		return r.Clear(mirrored, ang) && (!g || g.Clear(mirrored, ang));
	}

	// The widest opening below OPEN that is clear (in whole degrees down, then halved twelve times between the
	// first clear one and the blocked one above it), or -1: none down to 1 degree.
	static double Widest(AjarLeafRoom r, AjarLeafRoom g, bool mirrored)
	{
		double a = OPEN - 1;
		while (a >= 1 && !ClearBoth(r, g, mirrored, a)) a--;
		if (a < 1) return -1;
		double lo = a, hi = a + 1;
		for (int i = 0; i < 12; i++)
		{
			double mid = (lo + hi) / 2;
			if (ClearBoth(r, g, mirrored, mid)) lo = mid;
			else hi = mid;
		}
		return lo;
	}

	// How the leaf stands in r (and, with g, in g too, alike): as it always stood, mirrored, or opened less.
	static void Choose(AjarLeafRoom r, AjarLeafRoom g, out bool mirrored, out double ang)
	{
		mirrored = false;
		ang = OPEN;
		if (ClearBoth(r, g, false, OPEN)) return;
		if (ClearBoth(r, g, true, OPEN)) { mirrored = true; return; }
		double first = Widest(r, g, false), second = Widest(r, g, true);
		if (first < 0 && second < 0) return;           // nothing is clear: as it always stood
		if (second > first + 0.001) { mirrored = true; ang = second; }      // (a tie, to rounding: the first jamb)
		else ang = first;
	}

	// --- plane geometry --------------------------------------------------------------------------------------
	static Vector2 Closest(Vector2 p, Vector2 a, Vector2 b)
	{
		Vector2 d = b - a;
		double n = d dot d;
		double t = n > 0 ? clamp(((p - a) dot d) / n, 0, 1) : 0;
		return a + d * t;
	}
	static double SegDist(Vector2 p, Vector2 a, Vector2 b) { return (p - Closest(p, a, b)).Length(); }
	static double Perp(Vector2 a, Vector2 b) { return a.x * b.y - a.y * b.x; }
	// p-q and a-b meet (touching counts)
	static bool Crosses(Vector2 p, Vector2 q, Vector2 a, Vector2 b)
	{
		Vector2 r = q - p, s = b - a;
		double den = Perp(r, s);
		if (abs(den) < 1e-12) return false;
		double t = Perp(a - p, s) / den, u = Perp(a - p, r) / den;
		return t >= -1e-9 && t <= 1 + 1e-9 && u >= -1e-9 && u <= 1 + 1e-9;
	}
	// how far along the ray from p (unit dir) it meets a-b, or -1
	static double RayHit(Vector2 p, Vector2 dir, Vector2 a, Vector2 b)
	{
		Vector2 s = b - a;
		double den = Perp(dir, s);
		if (abs(den) < 1e-12) return -1;
		double t = Perp(a - p, s) / den, u = Perp(a - p, dir) / den;
		return t >= 0 && u >= 0 && u <= 1 ? t : -1;
	}
}

extend class AjarHandler
{
	// Hang: d's leaf stands open in f (and the clocked door's two leaves alike in their two frames).
	void PoseLeaf(AjarDoor d, AjarFrame f)
	{
		let r = AjarLeafRoom.Of(f);
		if (!r) return;
		AjarDoor tw = d.IsClocked() ? d.Twin() : null;
		AjarFrame tf = tw && tw.frame && tw.frame != f ? tw.frame : null;
		let g = tf ? AjarLeafRoom.Of(tf) : null;
		bool mirrored;
		double ang;
		AjarLeafRoom.Choose(r, g, mirrored, ang);
		SetLeaf(d, r, mirrored, ang);
		if (g) SetLeaf(tw, g, mirrored, ang);
	}

	void SetLeaf(AjarDoor d, AjarLeafRoom r, bool mirrored, double ang)
	{
		Vector2 hinge = r.Hinge(mirrored), u = r.Way(mirrored, ang);
		d.SetOrigin((hinge + u * AjarLeafRoom.LEN / 2, r.z), false);
		d.angle = VectorAngle(u.x, u.y) + 90;
	}

	// AjarDoor.Used: true when the USE that met d's box is aimed past the door at a switch, and so goes on to it.
	// Only a press whose aim passes through d's box, as the engine's use trace that called Used does, is looked at:
	// a script that calls Used to take a door from where the player happens to stand is answered as before.
	const USE_LOOK = 128.0;     // how far along the aim lines are looked at (the use trace itself reaches 64)
	bool UseGoesOn(AjarDoor d, Actor user)
	{
		if (!user) return false;
		Vector2 from = user.pos.xy;
		Vector2 dir = Actor.AngleToVector(user.angle);
		let pp = PlayerPawn(user);
		double range = pp ? pp.UseRange : 64;
		if (!RayMeetsBox(from, dir, range + 1, d.pos.xy, d.radius)) return false;
		// the leaf as it stands (hung: as posed; leaning: its face)
		Vector2 side = Actor.AngleToVector(d.angle - 90) * AjarLeafRoom.LEN / 2;
		double door = AjarLeafRoom.RayHit(from, dir, d.pos.xy - side, d.pos.xy + side);
		if (door < 0) door = USE_LOOK;
		Line fl = d.frame ? FindLine(d.frame.args[0]) : null;
		// the lines along the aim, nearest first
		Array<int> hit;
		Array<double> at;
		let it = BlockLinesIterator.CreateFromPos((from + dir * USE_LOOK / 2, user.pos.z), user.height, USE_LOOK / 2 + 1);
		while (it.Next())
		{
			Line w = it.CurLine;
			double t = AjarLeafRoom.RayHit(from, dir, w.v1.p, w.v2.p);
			if (t < 0 || t >= door || hit.Find(w.Index()) < hit.Size()) continue;
			int k = 0;
			while (k < at.Size() && at[k] <= t) k++;
			hit.Insert(k, w.Index());
			at.Insert(k, t);
		}
		for (int k = 0; k < hit.Size(); k++)
		{
			Line w = level.lines[hit[k]];
			if (w == fl || (d.frame && w.special == 130 && w.args[0] == d.frame.args[0])) return false;   // the frame: the door's
			bool front = AjarLeafRoom.Perp(w.delta, from - w.v1.p) <= 0;      // (P_PointOnLineSide)
			if (w.special && (w.activation & (SPAC_Use | SPAC_UseThrough | SPAC_UseBack)) && (front || (w.activation & SPAC_UseBack)))
				return true;                                // a switch first
			if (w.flags & (Line.ML_BLOCKEVERYTHING | Line.ML_BLOCKUSE) || !w.frontsector || !w.backsector) return false;
			Vector2 p = from + dir * at[k];
			double top = min(w.frontsector.ceilingplane.ZatPoint(p), w.backsector.ceilingplane.ZatPoint(p));
			double bottom = max(w.frontsector.floorplane.ZatPoint(p), w.backsector.floorplane.ZatPoint(p));
			if (top <= bottom) return false;                // a wall: the door's, as before
		}
		return false;                                       // the leaf, or nothing: the door's
	}

	// The ray from p (unit dir), `len` long, passes through the square box of half-width r round c.
	static bool RayMeetsBox(Vector2 p, Vector2 dir, double len, Vector2 c, double r)
	{
		double t0 = 0, t1 = len;
		for (int i = 0; i < 2; i++)
		{
			double o = i ? p.y : p.x, dd = i ? dir.y : dir.x, lo = (i ? c.y : c.x) - r, hi = (i ? c.y : c.x) + r;
			if (abs(dd) < 1e-12) { if (o < lo || o > hi) return false; continue; }
			double a = (lo - o) / dd, b = (hi - o) / dd;
			if (a > b) { double s = a; a = b; b = s; }
			t0 = max(t0, a);
			t1 = min(t1, b);
			if (t0 > t1) return false;
		}
		return true;
	}
}
