// Hands do not reach through an opening (PLAN.md, "Hands do not reach through an opening (built 2026-11-27)").
//
// The engine's use trace (P_UseTraverse) follows line portals: a press of USE at a hung door's far side, aimed
// at the opening, came out at the door's frame and took the door down from there (the leaf, standing open at a
// jamb, was the first thing it met), so a door could be had in the place it opens onto without being carried
// there. The rule: a real press by the player does nothing to a door (leaning or hung) and nothing to a frame
// (empty or filled) that it reaches through a line portal: a hung door's opening, a Pair's, a fixed doorway, a
// one-sided doorway. From the same side everything is as it was.
//
// Asked only at the engine's two ways in, AjarDoor.Used and AjarFrame.Activate (a frame's mouth line calls
// Thing_Activate on it; the Doom door lab's gates call Activate from WorldLinePreActivated), and only of a real
// press (RealPress). UseFrame, Hang, Unhang and TakeLeaning, which scripts, the thief and the tests call, are not
// touched, and neither is a script's call of Used or Activate.
//
// How a press through an opening is told from a direct one: in plain space, no portal followed. The press is
// direct when the line from where the player stands along where they face (flat, UseRange long: the engine's own
// use trace, up to its first portal) meets the target before it crosses any line portal: a door's box (its
// radius, as the engine's trace meets it), or a frame's mouth (a line whose Thing_Activate is the frame) or the
// frame's own line. Up to the first portal the engine's trace and this line are one and the same, so a press the
// engine brought to the target without a portal is always direct here; a press it brought through a portal
// crossed that portal first, and is told so, wherever the far side lies in plain space (also right behind its
// own frame). What it cannot tell: a target that stands on the aim in plain space before any portal and yet was
// reached by the engine only through one (the engine missing a corner of the box this counts, then coming round
// to the same thing through a portal): there the player stands at the target anyway, and the press is let be.
extend class AjarHandler
{
	// The breadth of the rule, one switch: 1 ("all"), every door and every frame (a leaning door is not picked up
	// and nothing is hung in an empty frame through an opening either); 0 ("hung only"), only a hung door or a
	// filled frame (taking a leaning door or hanging in an empty frame through an opening stays allowed).
	const REACH_ALL = 1;
	bool reachOff;          // the reach survey's "before" (MAP=LAB MODE=4, reachtest.zs): no such rule, as until 2026-11-27
	int reachSaid;          // the tic (+ 1) the refusal was last said

	// A press of USE at the keyboard. The engine calls the use trace (and from it Used, and a mouth's
	// Thing_Activate) only from PlayerPawn.CheckUse, and that only while BT_USE is down in the tic's command and
	// usedown has just been set (CheckUse: if (cmd.buttons & BT_USE) { if (!usedown) { usedown = true; ...
	// P_UseLines } }). A script or a test calling Used or Activate has no key down (the tests' real presses set
	// cmd.buttons for the one CheckUse and clear it after).
	static bool RealPress(Actor user)
	{
		let pp = PlayerPawn(user);
		return pp && pp.player && pp.player.mo == pp && (pp.player.cmd.buttons & BT_USE) && pp.player.usedown;
	}

	// AjarDoor.Used (d) and AjarFrame.Activate (f): true when the press is to be refused, a real press that came
	// to d or f through an opening. Says so, at most once every 3 seconds.
	bool HandsDoNotReach(Actor user, AjarDoor d, AjarFrame f)
	{
		if (reachOff || !RealPress(user)) return false;
		bool hung = d ? d.frame != null : f.door != null;
		if (REACH_ALL == 0 && !hung) return false;
		if (d ? ReachesDoor(user, d) : ReachesFrame(user, f)) return false;
		if (!reachSaid || level.time + 1 - reachSaid >= 105)
		{
			reachSaid = level.time + 1;
			Say("Your hands do not reach through a doorway.\nStep through first.");
		}
		return true;
	}

	// The press meets d's box along the aim before any line portal.
	bool ReachesDoor(Actor user, AjarDoor d)
	{
		Vector2 from = user.pos.xy, dir = Actor.AngleToVector(user.angle);
		double range = PlayerPawn(user).UseRange + 1;
		double at = BoxEntry(from, dir, range, d.pos.xy, d.radius);
		if (at < 0) return false;
		Array<int> none;
		return at < FirstPortal(user, from, dir, range, none);
	}

	// The press meets one of f's mouths (a line whose special is Thing_Activate on f) or f's own line along the
	// aim, within range, before any other line portal.
	bool ReachesFrame(Actor user, AjarFrame f)
	{
		Vector2 from = user.pos.xy, dir = Actor.AngleToVector(user.angle);
		double range = PlayerPawn(user).UseRange + 1;
		Array<int> own;
		let li = level.CreateLineIdIterator(f.args[0]);
		int i;
		while ((i = li.Next()) >= 0) own.Push(i);
		double at = -1;
		let it = BlockLinesIterator.CreateFromPos((from + dir * range / 2, user.pos.z), user.height, range / 2 + 1);
		while (it.Next())
		{
			Line w = it.CurLine;
			bool mine = (w.special == 130 && f.tid && w.args[0] == f.tid) || own.Find(w.Index()) < own.Size();
			if (!mine) continue;
			if (own.Find(w.Index()) == own.Size()) own.Push(w.Index());
			double t = AjarLeafRoom.RayHit(from, dir, w.v1.p, w.v2.p);
			if (t >= 0 && t <= range && (at < 0 || t < at)) at = t;
		}
		return at >= 0 && at < FirstPortal(user, from, dir, range, own);
	}

	// How far along the aim the first line portal is (not one of `skip`), or past the range: none.
	double FirstPortal(Actor user, Vector2 from, Vector2 dir, double range, Array<int> skip)
	{
		double first = range + 1;
		let it = BlockLinesIterator.CreateFromPos((from + dir * range / 2, user.pos.z), user.height, range / 2 + 1);
		while (it.Next())
		{
			Line w = it.CurLine;
			if (!w.isLinePortal() || skip.Find(w.Index()) < skip.Size()) continue;
			double t = AjarLeafRoom.RayHit(from, dir, w.v1.p, w.v2.p);
			if (t >= 0 && t < first) first = t;
		}
		return first;
	}

	// Where the ray from p (unit dir), `len` long, enters the square box of half-width r round c (0 if p is in
	// it), or -1: it does not.
	static double BoxEntry(Vector2 p, Vector2 dir, double len, Vector2 c, double r)
	{
		double t0 = 0, t1 = len;
		for (int i = 0; i < 2; i++)
		{
			double o = i ? p.y : p.x, dd = i ? dir.y : dir.x, lo = (i ? c.y : c.x) - r, hi = (i ? c.y : c.x) + r;
			if (abs(dd) < 1e-12) { if (o < lo || o > hi) return -1; continue; }
			double a = (lo - o) / dd, b = (hi - o) / dd;
			if (a > b) { double s = a; a = b; b = s; }
			t0 = max(t0, a);
			t1 = min(t1, b);
			if (t0 > t1) return -1;
		}
		return t0;
	}
}
