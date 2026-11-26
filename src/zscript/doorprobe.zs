// The door probe: every frame's leaf, and USE at every switch beside a frame, in one map after another (PLAN.md,
// "Doors: the open leaf keeps clear of walls; USE at a lever works the lever"). Off unless ajar_doorprobe is set:
//   CFG=doorprobe.cfg MAP=MAP01 MODE=0 EXTRA="+set ajar_doorprobe 7" tools/smoke.sh build/probe
// ajar_doorprobe is a sum: 1 the leaves, 2 the switches, 4 on to the next map of LIST when done (else it stays).
// It runs with ajar_autotest 0 (no level's test script), the player a god, the monsters gone.
//
// 1, the leaves: for each frame by id, the leaf of the door hung in it, as the engine posed it: the door it starts
// with, or one of the level's hung there by the probe (Hang, as the game does; then the doors are put back as they
// were). A line "AJARTEST pose <map> frame <id> <door> start|probe pos=(x,y,z) angle=a" each, to compare two builds.
// 2, the switches: each line the player USEs that has a special and is not a frame's mouth, within 96 of a frame's
// mouth, with a door hung in that frame (the one there, or the probe's), real USE presses (the engine's CheckUse):
//   fromSwitch  standing 40 out from the switch's middle, facing it: the press reaches the switch, the door stays
//   fromFrame   standing in front of the frame, turned to the switch (from no more than 48 off): the same
//               (both: unless the open leaf lies between the player and the switch; then the press is the door's)
//   atLeaf      from in front of the frame, aimed at the leaf's middle: the door comes down into the hands
//   atFrame     aimed at the empty frame's middle: the door is hung again
//   byLeaning   the door put down leaning beside the switch, edge on, its box across the aim: the switch, the door
//               left leaning
//   atLeaning   aimed at that door's face: it is picked up
// A switch is not worked: its activation is seen (WorldLinePreActivated) and stopped, so nothing in the level
// moves. A frame's mouth is let through (it is Ajar's own: the frame takes or hangs a door).
// 8, views (alone): the map's views of VIEW_* below, one each 70 tics from tic 20, a door hung in the frame first if
// it has none (tools/doorprobe_views.cfg shoots twice a view: the later one is the view).
class AjarDoorProbe : EventHandler
{
	static const string LIST[] = { "MAP01", "MAP02", "MAP03", "MAP04", "MAP05", "MAP06", "MAP07", "MAP08", "MAP09",
		"MAP10", "MAP11", "MAP12", "MAP13", "MAP14", "MAP15", "MAP16", "MAP17", "MAP18", "MAP19", "MAP20", "MAP21",
		"MAP31", "MAP32", "MAP33" };
	const NEAR = 96.0;
	// the views (8): map, frame, where the player stands, which way they look
	// (MAP21 125, 128, 126: the three levers THEN with the frame beside each, from 100 out)
	static const string VIEW_MAP[] = { "MAP21", "MAP21", "MAP21", "MAP21", "MAP21", "MAP21", "MAP21", "MAP04", "MAP04", "MAP07", "MAP17", "MAP17", "MAP33" };
	static const int VIEW_FRAME[] = { 101, 101, 121, 121, 125, 128, 126, 103, 103, 103, 101, 101, 101 };
	static const double VIEW_X[] = { 520, 400, 520, 400, 1132, 1904, 1600, 688, 780, 230, 552, 560, 2288 };
	static const double VIEW_Y[] = { 230, 200, 8422, 8392, 9512, 9628, 10612, 1420, 1450, 1010, 256, 340, 4130 };
	static const double VIEW_A[] = { 115, 50, 115, 50, 0, 90, 270, 90, 135, 320, 0, 330, 90 };
	int tic, checks, fails, pairs;
	AjarHandler h;
	Array<int> pf, ps;           // the pairs: a frame's id, a switch's line index
	int k, step, wait;
	bool pressing;
	Array<int> fired;            // the lines whose activation the press reached
	AjarDoor door;               // the door hung in the pair's frame
	AjarDoor before;             // what the hands held before the press
	bool done;

	int Mode() { return CVar.GetCVar("ajar_doorprobe").GetInt(); }

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d  %s%s%s", what, ok, level.mapname, info != "" ? " " : "", info);
	}

	override void WorldLinePreActivated(WorldEvent e)
	{
		if (!pressing || !Mode()) return;
		Line l = e.ActivatedLine;
		fired.Push(l.Index());
		if (!IsMouth(l)) e.ShouldActivate = false;
	}

	bool IsMouth(Line l)
	{
		if (l.special != 130) return false;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next())) if (f.args[0] == l.args[0]) return true;
		return false;
	}

	// the frame's mouth: its line moved 16 into the room
	Vector2 MouthN(AjarFrame f) { Vector2 dir = h.FindLine(f.args[0]).delta.Unit(); return (dir.y, -dir.x); }
	Vector2 MouthA(AjarFrame f) { return h.FindLine(f.args[0]).v1.p + MouthN(f) * 16; }
	Vector2 MouthB(AjarFrame f) { return h.FindLine(f.args[0]).v2.p + MouthN(f) * 16; }

	// (its own plane geometry: the probe also goes into a build of main, to compare)
	static double SegDist(Vector2 p, Vector2 a, Vector2 b)
	{
		Vector2 d = b - a;
		double n = d dot d;
		double t = n > 0 ? clamp(((p - a) dot d) / n, 0, 1) : 0;
		return (p - (a + d * t)).Length();
	}
	static double Perp(Vector2 a, Vector2 b) { return a.x * b.y - a.y * b.x; }
	static double SegSeg(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
	{
		Vector2 r = b - a, s = d - c;
		double den = Perp(r, s);
		if (abs(den) > 1e-12)
		{
			double t = Perp(c - a, s) / den, u = Perp(c - a, r) / den;
			if (t >= 0 && t <= 1 && u >= 0 && u <= 1) return 0;
		}
		return min(min(SegDist(a, c, d), SegDist(b, c, d)), min(SegDist(c, a, b), SegDist(d, a, b)));
	}

	// --- doors put back as they were ------------------------------------------------------------------------
	Array<AjarDoor> dd;
	Array<AjarFrame> dFrame;
	Array<double> dx, dy, dz, da;
	void Remember()
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			if (d.IsShadow()) continue;
			dd.Push(d); dFrame.Push(d.frame); dx.Push(d.pos.x); dy.Push(d.pos.y); dz.Push(d.pos.z); da.Push(d.angle);
		}
	}
	void PutBack()
	{
		h.carried = null;
		for (int i = 0; i < dd.Size(); i++)
		{
			AjarDoor d = dd[i];
			if (d.frame == dFrame[i] && !d.carried) continue;
			if (d.frame) h.Unhang(d.frame);
			if (dFrame[i]) { if (dFrame[i].door) h.Unhang(dFrame[i]); h.Hang(d, dFrame[i]); }
			else { d.carried = false; d.SetOrigin((dx[i], dy[i], dz[i]), false); d.angle = da[i]; d.Show(); }
		}
	}
	// a door for frame f: a colour one (1..6) that is no way out there and is nobody's start in a frame, else any
	// colour one, else none
	AjarDoor DoorFor(AjarFrame f)
	{
		AjarDoor any = null;
		for (int i = 0; i < dd.Size(); i++)
		{
			AjarDoor d = dd[i];
			if (d.args[1] < 1 || d.args[1] > 6 || d.IsPair() || d.nailer) continue;
			if (f.args[1] && f.args[1] == h.FarAt(d, f)) continue;
			if (!dFrame[i]) return d;
			if (!any) any = d;
		}
		return any;
	}
	void HangIn(AjarDoor d, AjarFrame f)
	{
		if (d.frame == f) return;
		if (d.frame) h.Unhang(d.frame);
		if (f.door) h.Unhang(f);
		if (h.carried == d) h.carried = null;
		h.Hang(d, f);
	}

	// --- 1: the leaves ---------------------------------------------------------------------------------------
	void Leaves()
	{
		Array<AjarFrame> fs;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			int at = 0;
			while (at < fs.Size() && fs[at].args[0] < f.args[0]) at++;
			fs.Insert(at, f);
		}
		for (int i = 0; i < fs.Size(); i++)
		{
			f = fs[i];
			if (!h.FindLine(f.args[0])) continue;
			AjarDoor d = f.door;
			string how = "start";
			if (!d)
			{
				d = DoorFor(f);
				if (!d) { Console.Printf("AJARTEST pose %s frame %d none", level.mapname, f.args[0]); continue; }
				HangIn(d, f);
				how = "probe";
			}
			Console.Printf("AJARTEST pose %s frame %d %s %s pos=(%.4f,%.4f,%.4f) angle=%.4f", level.mapname, f.args[0],
				d.IsShadow() ? "SHADOW" : d.Label(), how, d.pos.x, d.pos.y, d.pos.z, d.angle);
		}
		PutBack();
	}

	// --- 2: the switches -------------------------------------------------------------------------------------
	void FindPairs()
	{
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			if (!h.FindLine(f.args[0])) continue;
			Vector2 a = MouthA(f), b = MouthB(f), n = MouthN(f);
			for (int i = 0; i < level.lines.Size(); i++)
			{
				Line w = level.lines[i];
				if (!w.special || !(w.activation & (SPAC_Use | SPAC_UseThrough | SPAC_UseBack)) || IsMouth(w)) continue;
				if (SegSeg(w.v1.p, w.v2.p, a, b) > NEAR) continue;
				int at = 0;
				while (at < pf.Size() && (pf[at] < f.args[0] || (pf[at] == f.args[0] && ps[at] < i))) at++;
				pf.Insert(at, f.args[0]);
				ps.Insert(at, i);
			}
		}
		for (int i = 0; i < pf.Size(); i++)
		{
			Line w = level.lines[ps[i]];
			Console.Printf("AJARTEST info switch %s line %d special %d(%d) at (%.0f,%.0f) by frame %d", level.mapname, ps[i],
				w.special, w.args[0], (w.v1.p.x + w.v2.p.x) / 2, (w.v1.p.y + w.v2.p.y) / 2, pf[i]);
		}
	}

	// stand at p facing q; false: the player does not fit there
	bool Stand(Actor mo, Vector2 p, Vector2 q)
	{
		Sector s = level.PointInSector(p);
		mo.SetOrigin((p, s.floorplane.ZatPoint(p)), false);
		mo.angle = VectorAngle(q.x - p.x, q.y - p.y);
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		return mo.TestMobjLocation() && s.ceilingplane.ZatPoint(p) - s.floorplane.ZatPoint(p) >= mo.height;
	}
	void Press(Actor mo)
	{
		let pp = PlayerPawn(mo);
		fired.Clear();
		before = h.carried;
		pressing = true;
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
		pp.CheckUse();
		pressing = false;
	}
	bool Reached(int i) { return fired.Find(i) < fired.Size(); }
	// the door's leaf as it stands lies across p-q (the leaf in front of the switch: the press is the door's)
	bool LeafBetween(AjarDoor d, Vector2 p, Vector2 q)
	{
		Vector2 s = Actor.AngleToVector(d.angle - 90) * 32, a = d.pos.xy - s, b = d.pos.xy + s;
		Vector2 r = q - p, t = b - a;
		double den = Perp(r, t);
		if (abs(den) < 1e-12) return false;
		double u = Perp(a - p, t) / den, v = Perp(a - p, r) / den;
		return u >= 0 && u <= 1 && v >= 0 && v <= 1;
	}
	// the press as the rule has it: the switch, the door left; or, with the leaf between, the door taken
	bool AsRuled(bool behind, int sw, AjarFrame f)
	{
		return behind ? h.carried == door && !Reached(sw) : Reached(sw) && f.door == door && h.carried == before;
	}
	string Said() { string s = h.said; s.Replace("\n", " / "); return s; }

	Vector2 SwitchMid(Line w) { return w.v1.p + w.delta / 2; }
	Vector2 SwitchOut(Line w) { Vector2 d = w.delta.Unit(); return (d.y, -d.x); }

	// From in front of the frame toward the switch: the frame's middle 40 out, brought to 48 off the switch.
	Vector2 FrontOfFrame(AjarFrame f, Vector2 to)
	{
		Vector2 a = MouthA(f), b = MouthB(f), n = MouthN(f);
		Vector2 p = (a + b) / 2 + n * 40;
		double l = (to - p).Length();
		if (l > 48) p = to + (p - to) / l * 48;
		return p;
	}

	void Pair(Actor mo)
	{
		AjarFrame f = h.FindFrame(pf[k]);
		Line w = level.lines[ps[k]];
		Vector2 m = SwitchMid(w), o = SwitchOut(w);
		string what = String.Format("line %d by frame %d", ps[k], pf[k]);
		if (step == 0)
		{
			door = f.door;
			if (!door || door.IsShadow()) { door = DoorFor(f); if (door) HangIn(door, f); }
			if (!door) { Console.Printf("AJARTEST info %s %s: no door to hang", level.mapname, what); step = 99; return; }
			Console.Printf("AJARTEST info %s %s: the %s door hung, leaf at (%.1f,%.1f) angle %.1f", level.mapname, what,
				door.Label(), door.pos.x, door.pos.y, door.angle);
			step++;
			return;
		}
		if (step == 1)
		{
			static const double outs[] = { 40, 48, 32, 56 };
			bool ok = false;
			for (int i = 0; i < 4 && !ok; i++) ok = Stand(mo, m + o * outs[i], m);
			if (!ok) { Console.Printf("AJARTEST info %s %s: no room in front of the switch", level.mapname, what); step = 3; return; }
			bool behind = LeafBetween(door, mo.pos.xy, m);
			Press(mo);
			Check("fromSwitch", AsRuled(behind, ps[k], f),
				String.Format("%s from (%.0f,%.0f)%s: switch %s, door %s; %s", what, mo.pos.x, mo.pos.y, behind ? ", the leaf between" : "", Reached(ps[k]) ? "reached" : "NOT reached",
				f.door == door ? "hung" : h.carried == door ? "TAKEN" : "?", Said()));
			if (h.carried == door) { h.carried = null; HangIn(door, f); }
			step++;
			return;
		}
		if (step == 2)
		{
			Vector2 p = FrontOfFrame(f, m);
			if (!Stand(mo, p, m)) { Console.Printf("AJARTEST info %s %s: no room in front of the frame", level.mapname, what); step++; return; }
			bool behind = LeafBetween(door, mo.pos.xy, m);
			Press(mo);
			Check("fromFrame", AsRuled(behind, ps[k], f),
				String.Format("%s from (%.0f,%.0f) angle %.0f%s: switch %s, door %s; %s", what, mo.pos.x, mo.pos.y, mo.angle, behind ? ", the leaf between" : "",
				Reached(ps[k]) ? "reached" : "NOT reached", f.door == door ? "hung" : h.carried == door ? "TAKEN" : "?", Said()));
			if (h.carried == door) { h.carried = null; HangIn(door, f); }
			step++;
			return;
		}
		if (step == 3)
		{
			if (door.Stuck()) { step = 99; return; }
			Vector2 p = FrontOfFrame(f, door.pos.xy);
			Stand(mo, p, door.pos.xy);
			Press(mo);
			Check("atLeaf", h.carried == door && !f.door, String.Format("%s from (%.0f,%.0f): %s", what, mo.pos.x, mo.pos.y, Said()));
			step++;
			return;
		}
		if (step == 4)
		{
			if (h.carried != door) { step = 99; return; }
			Vector2 a = MouthA(f), b = MouthB(f), n = MouthN(f);
			Stand(mo, (a + b) / 2 + n * 40, (a + b) / 2);
			Press(mo);
			Check("atFrame", f.door == door && !h.carried, String.Format("%s: %s", what, Said()));
			step++;
			return;
		}
		if (step == 5)
		{
			// the door leaning beside the switch, edge on to the wall, 28 out and 18 along: its box across the aim
			if (f.door == door) h.Unhang(f);
			h.carried = null;
			door.carried = false;
			Vector2 t = w.delta.Unit();
			Vector2 c = m + o * 28 + t * 18;
			door.SetOrigin((c, level.PointInSector(c).floorplane.ZatPoint(c)), false);
			door.angle = VectorAngle(o.x, o.y) + 90;
			door.Show();
			bool ok = Stand(mo, m + o * 40, m);
			Press(mo);
			Check("byLeaning", Reached(ps[k]) && !door.carried && h.carried == before,
				String.Format("%s: switch %s, door %s; %s", what, Reached(ps[k]) ? "reached" : "NOT reached", door.carried ? "PICKED UP" : "leaning", Said()));
			step++;
			return;
		}
		if (step == 6)
		{
			if (door.carried) { step++; return; }
			Stand(mo, m + o * 40, door.pos.xy);
			Press(mo);
			Check("atLeaning", h.carried == door, String.Format("%s: %s", what, Said()));
			step++;
			return;
		}
		if (step == 7)
		{
			if (h.carried == door) h.carried = null;
			HangIn(door, f);
			step = 99;
		}
	}

	void Views(Actor mo)
	{
		if (tic < 20 || (tic - 20) % 70) return;
		int n = (tic - 20) / 70, i;
		for (i = 0; i < VIEW_MAP.Size(); i++) if (VIEW_MAP[i] ~== level.mapname) { if (n == 0) break; n--; }
		if (i == VIEW_MAP.Size()) { Console.Printf("AJARTEST viewsDone=1"); done = true; return; }
		AjarFrame f = h.FindFrame(VIEW_FRAME[i]);
		AjarDoor d = f ? f.door : null;
		if (f && !d) { d = DoorFor(f); if (d) HangIn(d, f); }
		Vector2 p = (VIEW_X[i], VIEW_Y[i]);
		Stand(mo, p, p + Actor.AngleToVector(VIEW_A[i]));
		mo.bInvisible = true;
		Console.MidPrint(smallfont, " ");
		Console.Printf("AJARTEST info view %d %s frame %d from (%.0f,%.0f) angle %.0f: %s door, leaf at (%.1f,%.1f) angle %.2f", (tic - 20) / 70,
			level.mapname, VIEW_FRAME[i], p.x, p.y, VIEW_A[i], d ? d.Label() : "no", d ? d.pos.x : 0.0, d ? d.pos.y : 0.0, d ? d.angle : 0.0);
	}

	override void WorldTick()
	{
		int mode = Mode();
		if (!mode || done) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 1)
		{
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster) a.Destroy();
			Remember();
			return;
		}
		if (mode & 8) { Views(mo); return; }
		if (tic == 3 && (mode & 1)) Leaves();
		if (tic == 4 && (mode & 2)) FindPairs();
		if (tic >= 6 && (mode & 2) && k < pf.Size() && tic % 3 == 0)
		{
			Pair(mo);
			if (step == 99) { k++; step = 0; }
			return;
		}
		if (tic < 6 || ((mode & 2) && k < pf.Size())) return;
		done = true;
		PutBack();
		Console.Printf("AJARTEST probeDone=1 %s pairs=%d checks=%d failed=%d", level.mapname, pf.Size(), checks, fails);
		if (!(mode & 4)) return;
		for (int i = 0; i < LIST.Size() - 1; i++)
			if (level.mapname ~== LIST[i]) { level.ChangeLevel(LIST[i + 1], 0, CHANGELEVEL_NOINTERMISSION | CHANGELEVEL_RESETINVENTORY | CHANGELEVEL_RESETHEALTH | CHANGELEVEL_NOMONSTERS); return; }
		Console.Printf("AJARTEST probeAllDone=1");
	}
}
