// MAP32's look (PLAN.md, "Look: MAP32"; the map's dressing in
// tools/works32.py, the pictures in tools/gfx_works.py). Only a level that has
// AjarWorksRoom things in it (MAP32 built with AJAR_WORKS unset or 1) wakes
// this; in any other it does nothing.
//
// Since 2026-11-22 (Vadim: "on walls only, something more still like orange
// glow, not white on black") the level's house light is one still orange wall
// lamp, a picture with its glow painted on (gfx_works.py): nothing of it is
// worked here, and nothing of the look moves or changes texture. What is left
// here: the pens' and the way out's dull orange lights (steady), and three
// answers to the game (it never changes the game):
//  * A room done: when the time handler has it in `won` (a fight won; a room
//    of goes left by a way that is not a time door: EndGoes) its sectors'
//    light is up by DONE_UP.
//  * The press (room 3, AjarPress's phase, so an earlier self's pull too):
//    while it warns and comes down the hall's and the chamber's light sinks
//    by PRESS_DIM; at the moment it is down they go to full light and a white
//    light flashes in the chamber, falling back over FLARE_TICS tics.
//  * The plate line: while anyone stands on a plate (AjarPlate.pressed) a line
//    of white dashes lies on the floor from the plate to what it works, with
//    brightness running along it toward that (AjarWorksTrace: visible, so
//    the time handler's recorders skip it by name).
// Every sector light the look sets is worked out each tic from the state, so
// none is ever left changed (a go that ends, a hall cleared, begun anew).
// Once the universe is over (the time handler's `paradox`, paradox.zs) it
// stands down completely: from that tic it sets no light and moves nothing
// (the room's light is the paradox's then; what it lit stays as it was).
// The lights are carriers (+INVISIBLE, +NOBLOCKMAP, +NOINTERACTION): nothing
// can touch them and the recorders never see them.

// A light of the look, placed by the map: args[0] its kind (ORANGE), args[1]
// its room, args[2] its radius, args[3] its strength in hundredths.
class AjarWorksGlow : Actor
{
	int shownKey, shownRad;
	bool lit;
	Default { +NOBLOCKMAP +NOINTERACTION +INVISIBLE +NOGRAVITY +NOTELEPORT +DONTSPLASH +NOSECTOR }
	States { Spawn: TNT1 A -1; Stop; }

	void Shine(Color c, double f, int rad)
	{
		f = clamp(f, 0., 1.);
		int r = int(c.r * f), g = int(c.g * f), b = int(c.b * f);
		if (f < 0.02 || rad <= 0 || r + g + b < 6)
		{
			if (lit) { A_RemoveLight('works'); lit = false; }
			return;
		}
		int key = (r << 16) | (g << 8) | b;
		if (lit && key == shownKey && rad == shownRad) return;
		lit = true; shownKey = key; shownRad = rad;
		A_AttachLight('works', DynamicLight.PointLight, Color(r, g, b), rad, 0, DynamicLight.LF_ATTENUATE);
	}
}

class AjarWorksSpot : AjarWorksGlow
{
}

// A rectangle of a room, placed by the map: args[0] the room, args[1], args[2]
// its half width and height. Its being there is what wakes the look.
class AjarWorksRoom : Actor
{
	Default { +NOBLOCKMAP +NOINTERACTION +INVISIBLE +NOGRAVITY +NOSECTOR }
	States { Spawn: TNT1 A -1; Stop; }
}

// A dash of the plate line: white, laid flat on the floor, added to what is under it.
class AjarWorksTrace : Actor
{
	Default { +NOBLOCKMAP +NOINTERACTION +NOGRAVITY +FLATSPRITE +BRIGHT +DONTSPLASH RenderStyle "Add"; Alpha 0; }
	States { Spawn: AJZT A -1 Bright; Stop; }
}

class AjarWorksLine play
{
	AjarPlate plate;
	Array<AjarWorksTrace> dash;
}

class AjarWorks : EventHandler
{
	const FULL = 0;
	const DONE = 2;
	const ORANGE = 2;
	const TAG = 4100;
	const DONE_UP = 24;
	const PRESS_DIM = 48;
	const FLARE_TICS = 20;
	const ROOMS = 6;

	bool on;
	AjarTimeHandler th;
	Array<AjarWorksSpot> spots;
	int roomState[ROOMS];
	// the sectors whose light follows the state, and the press
	Array<int> ltSec, ltBase, ltRoom, ltPress;
	AjarPress press;
	AjarWorksGlow flare;
	Array<AjarWorksLine> plateLines;

	static AjarWorks Get() { return AjarWorks(EventHandler.Find("AjarWorks")); }

	override void WorldLoaded(WorldEvent e)
	{
		let it = ThinkerIterator.Create("AjarWorksRoom");
		on = it.Next() != null;
		if (!on) return;
		th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let si = ThinkerIterator.Create("AjarWorksSpot");
		AjarWorksSpot s;
		while (s = AjarWorksSpot(si.Next())) spots.Push(s);
		Array<int> pressed;
		let pt = level.CreateSectorTagIterator(TAG + 31);
		int j;
		while ((j = pt.Next()) >= 0) pressed.Push(j);
		for (int k = 1; k < ROOMS; k++)
		{
			let ti = level.CreateSectorTagIterator(TAG + 10 * k);
			int i;
			while ((i = ti.Next()) >= 0)
			{
				ltSec.Push(i); ltBase.Push(level.sectors[i].lightlevel); ltRoom.Push(k);
				ltPress.Push(pressed.Find(i) < pressed.Size());
			}
		}
		let pi = ThinkerIterator.Create("AjarPress");
		press = AjarPress(pi.Next());
		for (int k = 0; k < ROOMS; k++) roomState[k] = -1;
	}

	int StateOf(int k)
	{
		if (!k || !th) return FULL;
		if (th.won.Find(k) < th.won.Size()) return DONE;
		return FULL;
	}

	// --- light levels -------------------------------------------------------------------
	// What the press does to the light now: added to the level (or, for the flare, a share of the way to full).
	double, double PressLight()
	{
		if (!press) return 0, 0;
		if (press.phase == 1) return -PRESS_DIM * min(1., press.t / 8.), 0;
		if (press.phase == 2) return -PRESS_DIM, 0;
		if (press.phase == 3 && press.t < FLARE_TICS) return 0, 1 - press.t / double(FLARE_TICS);
		return 0, 0;
	}

	int Want(int i)
	{
		double l = ltBase[i] + (roomState[ltRoom[i]] == DONE ? DONE_UP : 0);
		if (ltPress[i])
		{
			double dim, fl;
			[dim, fl] = PressLight();
			l += dim;
			l += (255 - l) * fl;
		}
		return clamp(int(l), 0, 255);
	}

	// How many of the look's sectors are not at the light their room's state says (tests).
	int Wrong()
	{
		int n = 0;
		for (int i = 0; i < ltSec.Size(); i++) if (level.sectors[ltSec[i]].lightlevel != Want(i)) n++;
		return n;
	}

	// How many of the sectors the press's light follows are not at their room's own level (tests: 0 but in a stroke).
	int PressLit()
	{
		int n = 0;
		for (int i = 0; i < ltSec.Size(); i++)
			if (ltPress[i] && level.sectors[ltSec[i]].lightlevel != ltBase[i] + (roomState[ltRoom[i]] == DONE ? DONE_UP : 0)) n++;
		return n;
	}

	int Traces(AjarPlate p)
	{
		for (int i = 0; i < plateLines.Size(); i++) if (plateLines[i].plate == p) return plateLines[i].dash.Size();
		return 0;
	}

	static double FloorAt(Vector2 p)
	{
		Sector s = level.PointInSector(p);
		return s.floorplane.ZAtPoint(p);
	}

	// --- the tic --------------------------------------------------------------------------
	override void WorldTick()
	{
		if (!on) return;
		if (!th) th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		if (th && th.paradox) return;       // the universe is over (paradox.zs): the look stands down
		for (int k = 1; k < ROOMS; k++) roomState[k] = StateOf(k);
		for (int i = 0; i < ltSec.Size(); i++)
		{
			int want = Want(i);
			if (level.sectors[ltSec[i]].lightlevel != want) level.sectors[ltSec[i]].SetLightLevel(want);
		}
		for (int i = 0; i < spots.Size(); i++)
		{
			let s = spots[i];
			if (s && s.args[0] == ORANGE) s.Shine(Color(255, 138, 48), (s.args[3] ? s.args[3] : 45) / 100., s.args[2]);
		}
		ShowFlare();
		ShowPlateLines();
	}

	// the flash in the chamber at the moment the press is down
	void ShowFlare()
	{
		double dim, fl;
		[dim, fl] = PressLight();
		if (fl <= 0)
		{
			if (flare) { flare.Destroy(); flare = null; }
			return;
		}
		if (!flare)
		{
			Vector2 c = (5768, 1040);
			flare = AjarWorksGlow(Actor.Spawn("AjarWorksGlow", (c, FloorAt(c) + 96)));
		}
		flare.Shine(Color(255, 255, 255), fl, 640);
	}

	// --- the plate line ---------------------------------------------------------------------
	void ShowPlateLines()
	{
		let it = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(it.Next()))
		{
			int at = -1;
			for (int i = 0; i < plateLines.Size(); i++) if (plateLines[i].plate == p) at = i;
			if (!p.pressed)
			{
				if (at >= 0)
				{
					for (int j = 0; j < plateLines[at].dash.Size(); j++) if (plateLines[at].dash[j]) plateLines[at].dash[j].Destroy();
					plateLines.Delete(at);
				}
				continue;
			}
			if (at < 0)
			{
				Vector2 to;
				bool found;
				[to, found] = PlateTarget(p);
				if (!found) continue;
				let pl = new("AjarWorksLine");
				pl.plate = p;
				Vector2 d = to - p.pos.xy;
				double len = d.Length();
				Vector2 u = d / max(len, 1);
				double ang = atan2(u.y, u.x);
				for (double s = 40; s < len; s += 64)
				{
					Vector2 q = p.pos.xy + u * s;
					let tr = AjarWorksTrace(Actor.Spawn("AjarWorksTrace", (q, FloorAt(q) + 1)));
					if (!tr) continue;
					tr.angle = ang;
					pl.dash.Push(tr);
				}
				plateLines.Push(pl);
				at = plateLines.Size() - 1;
			}
			// brightness running along it toward what the plate works
			let pl = plateLines[at];
			for (int j = 0; j < pl.dash.Size(); j++)
			{
				if (!pl.dash[j]) continue;
				double w = (j * 64 - level.maptime * 9) % 320;
				if (w < 0) w += 320;
				double pulse = max(0., cos(w * 360. / 320.)) ** 4;
				pl.dash[j].alpha = 0.22 + 0.6 * pulse;
			}
		}
	}

	// What a plate works: its sprung frame (args[0], the frame's id) or its shutter (args[1], a tag).
	Vector2, bool PlateTarget(AjarPlate p)
	{
		if (p.args[0])
		{
			let h = AjarHandler(EventHandler.Find("AjarHandler"));
			AjarFrame f = h ? h.FindFrame(p.args[0]) : null;
			if (f) return f.pos.xy, true;
		}
		if (p.args[1])
		{
			let it = ThinkerIterator.Create("AjarShutter");
			Actor s;
			while (s = Actor(it.Next())) if (s.args[0] == p.args[1]) return s.pos.xy, true;
		}
		return (0, 0), false;
	}
}
