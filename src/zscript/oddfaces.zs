// A missile thrown across a one-sided doorway's odd face from its front
// (PLAN.md, "MAP18: the one-sided doorways"). The engine puts a new missile
// half a step ahead of its shooter by setting it there, not by moving it, so
// one thrown from closer than that to a line portal is put beyond the line
// without crossing it, and flies on into the plain room behind the face
// instead of out of the gate (ONESIDE MODE=3, impThrowsFrom4_intoA). This
// carries such a missile through, as if it had crossed: a missile whose way
// from its shooter to where it was put crosses an odd face from the front is
// moved, at the next tic (after its first step, which the engine makes in the
// tic it is thrown), to where the portal would have put it, turned as it
// would have turned. (The spawning event sees it already put, but before its
// speed is certain, so it is not moved there.)
//
// An odd face is a two-sided line portal (ajarmap.oneside); the doors' and
// the gates' portals are on one-sided lines and are not touched.
class AjarOddFaces : EventHandler
{
	bool off;                    // tests: the engine's own way (ONESIDE MODE=3's first cases)
	Array<Line> faces;
	Array<Actor> fresh;
	Array<double> freshX, freshY, fromX, fromY;
	int carried;                 // how many it has carried, for tests

	override void WorldLoaded(WorldEvent e)
	{
		for (int i = 0; i < level.lines.Size(); i++)
		{
			Line l = level.lines[i];
			if (l.backsector && l.isLinePortal()) faces.Push(l);
		}
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		if (off || !faces.Size() || !e.thing || !e.thing.bMissile || !e.thing.target) return;
		fresh.Push(e.thing);
		fromX.Push(e.thing.target.pos.x);
		fromY.Push(e.thing.target.pos.y);
		freshX.Push(e.thing.pos.x);
		freshY.Push(e.thing.pos.y);
	}

	override void WorldTick()
	{
		for (int i = 0; i < fresh.Size(); i++)
			if (fresh[i] && !off) Carry(fresh[i], (fromX[i], fromY[i]), (freshX[i], freshY[i]));
		fresh.Clear(); freshX.Clear(); freshY.Clear(); fromX.Clear(); fromY.Clear();
	}

	// from: the shooter, put: where the missile was put; it is carried from where it is now
	void Carry(Actor mo, Vector2 from, Vector2 put)
	{
		if ((put - from).Length() > 128) return;         // put far from its shooter: not this
		for (int i = 0; i < faces.Size(); i++)
		{
			Line l = faces[i];
			Line dst = l.getPortalDestination();
			if (!dst) continue;
			if (!Crosses(l, from, put)) continue;
			double turn = VectorAngle(dst.delta.x, dst.delta.y) - VectorAngle(l.delta.x, l.delta.y) + 180;
			Vector2 p = dst.v2.p + Actor.RotateVector(mo.pos.xy - l.v1.p, turn);
			// aligned on the floor: what comes out stands as high over the far floor as it went in over this one
			double dz = dst.frontsector.floorplane.ZatPoint(dst.v1.p) - l.frontsector.floorplane.ZatPoint(l.v1.p);
			mo.SetOrigin((p, mo.pos.z + dz), false);
			mo.ClearInterpolation();
			mo.angle += turn;
			mo.vel.xy = Actor.RotateVector(mo.vel.xy, turn);
			carried++;
			return;
		}
	}

	// from on the front side of l (or on it), to on its back side, and the way between goes over the line itself
	static bool Crosses(Line l, Vector2 from, Vector2 to)
	{
		Vector2 d = l.delta;
		double sf = d.x * (from.y - l.v1.p.y) - d.y * (from.x - l.v1.p.x);    // < 0: the front (right) side
		double st = d.x * (to.y - l.v1.p.y) - d.y * (to.x - l.v1.p.x);
		if (sf > 0 || st <= 0) return false;
		Vector2 m = to - from;
		double a = m.x * (l.v1.p.y - from.y) - m.y * (l.v1.p.x - from.x);
		double b = m.x * (l.v2.p.y - from.y) - m.y * (l.v2.p.x - from.x);
		return a * b <= 0;
	}
}
