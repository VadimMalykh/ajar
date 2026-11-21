// MAP32's look, "Deep Field" (PLAN.md, "Look: MAP32"; the map's dressing in
// tools/works32.py, the pictures in tools/gfx_works.py). Only a level that has
// AjarWorksRoom things in it (MAP32 built with AJAR_WORKS unset or 1) wakes
// this; in any other it does nothing.
//
// What it does, and all it does: it works the look's lights and the textures
// that change, and it reads the game for four things only (Vadim,
// 2026-11-21: "Lights answer the game: time door wave, press, calm when won,
// plate line"). It never changes the game.
//  * The state of each room. A room is DONE when the time handler has it in
//    `won` (a fight won; a room of goes left by a way that is not a time
//    door: EndGoes): its lit lines turn plain white and steady (the W00
//    variants), nothing moves there, its light is up by DONE_UP. Rooms 3 and 4
//    are CALM while their fight is on (the handler's fight is theirs and its
//    phase is not IDLE): the steady variants (S00), no breathing, running,
//    sweep or stutter. Otherwise FULL: the high lines breathe and the dashes
//    run (the M and L variants, animated by ANIMDEFS), the steady lights
//    breathe with them, lights travel along the floor's conduits, a sweep of
//    pale light crosses the room now and then, a stretch of the high line
//    stutters with a light that flickers with it.
//  * The time door wave: the player (never an earlier self) steps out of a
//    box into its room (the handler's Where goes from a box of fight k to its
//    hall, alive): a wave of pale light runs from that door through the room
//    along its long axis, once.
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
// stands down completely: from that tic it sets no light, texture or sprite
// and moves nothing (the room's light is the paradox's then; what it lit
// stays as it was, the textures' own ANIMDEFS frames run on).
// Its own random numbers (Random[AjarWorks]): the game's are never drawn on.
// The lights are carriers (+INVISIBLE, +NOBLOCKMAP, +NOINTERACTION): nothing
// can touch them and the recorders never see them. No moving or coloured light
// shines within QUIET of a frame, a leaf, a plate, a lamp or a lever: it fades
// out before (Guard).

// A light of the look, placed by the map: args[0] its kind (STEADY, ORANGE,
// TRAVEL, STUTTER), args[1] its room (0: a corridor), args[2] its radius,
// args[3], args[4] for TRAVEL where it goes (dx, dy), for STUTTER args[3] the
// id of its line.
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
	Vector3 home;
	override void PostBeginPlay() { Super.PostBeginPlay(); home = pos; }
}

// A rectangle of a room, placed by the map: args[0] the room, args[1], args[2]
// its half width and height, args[3] its long axis (0 x, 1 y), args[4] 1: a
// sweep crosses it.
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

class AjarWorksSweep play
{
	int room, t, len;
	double x1, y1, x2, y2;          // its path: from the middle of the line at (x1, y1) to (x2, y2)
	double across;                  // how far apart the lights are, across the path
	Array<AjarWorksGlow> glow;
}

class AjarWorks : EventHandler
{
	const FULL = 0;
	const CALM = 1;
	const DONE = 2;
	const STEADY = 1;
	const ORANGE = 2;
	const TRAVEL = 3;
	const STUTTER = 4;
	const TAG = 4100;
	const DONE_UP = 24;
	const PRESS_DIM = 48;
	const FLARE_TICS = 20;
	const QUIET = 192;
	const FADE = 96;
	const BREATH = 112;             // tics: as the textures' breath (gfx_works: FRAMES x TICS)
	const SWEEP_LEN = 105;
	const WAVE_LEN = 70;
	const TRAVEL_LEN = 280;
	const ROOMS = 6;

	bool on;
	AjarTimeHandler th;
	Array<AjarWorksRoom> rects;
	Array<AjarWorksSpot> spots;
	int roomState[ROOMS];
	int nextSweep[ROOMS];
	Array<AjarWorksSweep> sweeps;
	// the sides and sectors whose textures follow the state
	Array<int> sdLine, sdSide, sdPart, sdRoom, sdStut;
	Array<string> sdFam;
	Array<int> scSec, scPlane, scRoom;
	Array<string> scFam;
	// the sectors whose light follows the state, and the press
	Array<int> ltSec, ltBase, ltRoom, ltPress;
	AjarPress press;
	AjarWorksGlow flare;
	Array<double> qx, qy;           // where the puzzle's frames, plates, lamps and levers are
	Array<AjarWorksLine> plateLines;
	int prevK, prevB;
	// stutters: by room, the tic of the next flicker and the flicker's tics left
	int stutAt[ROOMS], stutLeft[ROOMS];
	bool stutDark[ROOMS];
	int waves;                      // how many waves have run (tests)

	static AjarWorks Get() { return AjarWorks(EventHandler.Find("AjarWorks")); }

	override void WorldLoaded(WorldEvent e)
	{
		let it = ThinkerIterator.Create("AjarWorksRoom");
		AjarWorksRoom r;
		while (r = AjarWorksRoom(it.Next())) rects.Push(r);
		on = rects.Size() > 0;
		if (!on) return;
		th = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let si = ThinkerIterator.Create("AjarWorksSpot");
		AjarWorksSpot s;
		while (s = AjarWorksSpot(si.Next())) { spots.Push(s); s.home = s.pos; }
		for (int i = 0; i < level.lines.Size(); i++)
		{
			Line l = level.lines[i];
			for (int sd = 0; sd < 2; sd++)
			{
				Side d = l.sidedef[sd];
				if (!d) continue;
				for (int part = 0; part < 3; part++)
				{
					string fam;
					bool ok;
					[fam, ok] = Family(TexMan.GetName(d.GetTexture(part)));
					if (!ok) continue;
					sdLine.Push(i); sdSide.Push(sd); sdPart.Push(part); sdFam.Push(fam); sdStut.Push(0);
					sdRoom.Push(RoomAt(d.sector.centerspot));
				}
			}
		}
		for (int i = 0; i < level.sectors.Size(); i++)
		{
			Sector sec = level.sectors[i];
			for (int plane = 0; plane < 2; plane++)
			{
				string fam;
				bool ok;
				[fam, ok] = Family(TexMan.GetName(sec.GetTexture(plane)));
				if (!ok) continue;
				scSec.Push(i); scPlane.Push(plane); scFam.Push(fam); scRoom.Push(RoomAt(sec.centerspot));
			}
		}
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
			let li = level.CreateLineIdIterator(4300 + k);
			while ((i = li.Next()) >= 0)
				for (int n = 0; n < sdLine.Size(); n++) if (sdLine[n] == i) sdStut[n] = k;
		}
		let pi = ThinkerIterator.Create("AjarPress");
		press = AjarPress(pi.Next());
		static const string QUIETS[] = { "AjarFrame", "AjarPlate", "AjarTogether", "AjarShutLamp", "AjarPressLamp",
			"AjarKeyLamp", "AjarPressSwitch", "AjarKeyLever" };
		for (int q = 0; q < QUIETS.Size(); q++)
		{
			let qi = ThinkerIterator.Create(QUIETS[q]);
			Actor a;
			while (a = Actor(qi.Next())) { qx.Push(a.pos.x); qy.Push(a.pos.y); }
		}
		for (int k = 0; k < ROOMS; k++)
		{
			roomState[k] = -1;
			nextSweep[k] = 350 + Random[AjarWorks](0, 700);
			stutAt[k] = 200 + Random[AjarWorks](0, 500);
		}
	}

	// A texture of a family that follows the state: AJZ, two letters, the variant, two digits.
	static string, bool Family(string n)
	{
		if (n.Length() != 8 || n.Left(3) != "AJZ") return "", false;
		string v = n.Mid(5, 1);
		if (v != "M" && v != "L" && v != "S") return "", false;
		return n.Left(6), true;
	}

	int RoomAt(Vector2 p)
	{
		for (int i = 0; i < rects.Size(); i++)
		{
			let r = rects[i];
			if (abs(p.x - r.pos.x) <= r.args[1] && abs(p.y - r.pos.y) <= r.args[2]) return r.args[0];
		}
		return 0;
	}

	int StateOf(int k)
	{
		if (!k || !th) return FULL;
		if (th.won.Find(k) < th.won.Size()) return DONE;
		if ((k == 3 || k == 4) && th.fight == k && th.phase != AjarTimeHandler.IDLE) return CALM;
		return FULL;
	}

	// The name a side's or a sector's texture of family `fam` (with its variant letter) has in state st.
	static string Shown(string fam, int st, bool dark = false)
	{
		string v = fam.Mid(5, 1);
		if (st == DONE) return fam.Left(5) .. "W00";
		if (st == CALM) return fam.Left(5) .. "S00";
		if (dark && v != "S") return fam.Left(5) .. "D00";
		return fam .. "00";
	}

	void SetSide(int i, string name)
	{
		TextureID tex = TexMan.CheckForTexture(name, TexMan.Type_Any);
		if (!tex.IsValid()) return;
		Side d = level.lines[sdLine[i]].sidedef[sdSide[i]];
		if (d.GetTexture(sdPart[i]) != tex) d.SetTexture(sdPart[i], tex);
	}

	void Apply(int k)
	{
		int st = roomState[k];
		for (int i = 0; i < sdLine.Size(); i++)
			if (sdRoom[i] == k) SetSide(i, Shown(sdFam[i], st, st == FULL && stutDark[k] && sdStut[i] == k));
		for (int i = 0; i < scSec.Size(); i++)
		{
			if (scRoom[i] != k) continue;
			TextureID tex = TexMan.CheckForTexture(Shown(scFam[i], st), TexMan.Type_Any);
			if (tex.IsValid()) level.sectors[scSec[i]].SetTexture(scPlane[i], tex);
		}
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

	// Do all of room k's sides that follow the state show variant v (tests)?
	bool SidesShow(int k, string v)
	{
		int n = 0;
		for (int i = 0; i < sdLine.Size(); i++)
		{
			if (sdRoom[i] != k) continue;
			string nm = TexMan.GetName(level.lines[sdLine[i]].sidedef[sdSide[i]].GetTexture(sdPart[i]));
			if (nm.Mid(5, 1) != v) return false;
			n++;
		}
		return n > 0;
	}

	int Traces(AjarPlate p)
	{
		for (int i = 0; i < plateLines.Size(); i++) if (plateLines[i].plate == p) return plateLines[i].dash.Size();
		return 0;
	}

	// --- moving lights fade out near the puzzle --------------------------------------------
	Array<double> dx, dy;           // where the leaves are now

	// 1 away from the puzzle, falling to 0 where a light of radius `reach` would touch it (or nearer than QUIET)
	double Guard(Vector2 p, double reach = 0)
	{
		double d = 1e9;
		for (int i = 0; i < qx.Size(); i++) d = min(d, ((qx[i], qy[i]) - p).Length());
		for (int i = 0; i < dx.Size(); i++) d = min(d, ((dx[i], dy[i]) - p).Length());
		return clamp((d - max(QUIET, reach)) / FADE, 0., 1.);
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
		dx.Clear(); dy.Clear();
		let di = ThinkerIterator.Create("AjarDoor");
		Actor d;
		while (d = Actor(di.Next())) if (!d.bInvisible) { dx.Push(d.pos.x); dy.Push(d.pos.y); }
		for (int k = 1; k < ROOMS; k++)
		{
			int st = StateOf(k);
			if (st == roomState[k]) continue;
			roomState[k] = st;
			stutDark[k] = false;
			Apply(k);
			if (st != FULL) EndSweeps(k, true);
		}
		if (roomState[0] != FULL) { roomState[0] = FULL; Apply(0); }
		for (int i = 0; i < ltSec.Size(); i++)
		{
			int want = Want(i);
			if (level.sectors[ltSec[i]].lightlevel != want) level.sectors[ltSec[i]].SetLightLevel(want);
		}
		Actor mo = players[consoleplayer].mo;
		int here = mo ? RoomAt(mo.pos.xy) : 0;
		ShowSpots(here);
		ShowFlare();
		Wave(mo);
		RunSweeps(here);
		Stutters(here);
		ShowPlateLines();
	}

	void ShowSpots(int here)
	{
		double breath = 0.5 - 0.5 * cos(360. * (level.maptime % BREATH) / BREATH);
		for (int i = 0; i < spots.Size(); i++)
		{
			let s = spots[i];
			if (!s) continue;
			int k = s.args[1], st = roomState[k];
			int kind = s.args[0];
			if (kind == ORANGE) { s.Shine(Color(255, 138, 48), 0.45, s.args[2]); continue; }
			if (kind == STEADY)
			{
				if (st == DONE) s.Shine(Color(200, 204, 210), 0.42, s.args[2]);
				else if (st == CALM) s.Shine(Color(159, 216, 255), 0.42, s.args[2]);
				else if (k == here || !s.lit) s.Shine(Color(159, 216, 255), 0.42 + 0.16 * breath, s.args[2]);
				continue;
			}
			if (kind == TRAVEL)
			{
				if (st != FULL) { s.Shine(0, 0, 0); continue; }
				int t = (level.maptime + i * 97) % TRAVEL_LEN;
				double u = t / double(TRAVEL_LEN);
				Vector2 p = s.home.xy + (s.args[3], s.args[4]) * u;
				s.SetOrigin((p, FloorAt(p) + 20), true);
				s.Shine(Color(159, 216, 255), 0.75 * sin(180. * u) * Guard(p, s.args[2]), s.args[2]);
				continue;
			}
			if (kind == STUTTER)
			{
				if (st != FULL) { s.Shine(0, 0, 0); continue; }
				s.Shine(Color(159, 216, 255), stutDark[k] ? 0.03 : 0.30, s.args[2]);
			}
		}
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

	// --- sweeps and waves ---------------------------------------------------------------
	void StartSweep(int k, AjarWorksRoom r, int len, Vector2 from, int dir)
	{
		EndSweeps(k, false);
		let sw = new("AjarWorksSweep");
		sw.room = k; sw.len = len; sw.t = 0;
		int axis = r.args[3];
		double hw = r.args[1], hh = r.args[2];
		double across = axis ? 2 * hw : 2 * hh;
		int n = clamp(int(across / 256), 2, 4);
		sw.across = across / n;
		if (axis)
		{
			sw.x1 = sw.x2 = r.pos.x;
			sw.y1 = from.y; sw.y2 = dir > 0 ? r.pos.y + hh + 128 : r.pos.y - hh - 128;
		}
		else
		{
			sw.y1 = sw.y2 = r.pos.y;
			sw.x1 = from.x; sw.x2 = dir > 0 ? r.pos.x + hw + 128 : r.pos.x - hw - 128;
		}
		for (int i = 0; i < n; i++)
		{
			let g = AjarWorksGlow(Actor.Spawn("AjarWorksGlow", (sw.x1, sw.y1, 0)));
			sw.glow.Push(g);
		}
		sweeps.Push(sw);
	}

	void EndSweeps(int k, bool andWaves)
	{
		for (int i = sweeps.Size() - 1; i >= 0; i--)
		{
			if (sweeps[i].room != k || (!andWaves && sweeps[i].len == WAVE_LEN)) continue;
			for (int j = 0; j < sweeps[i].glow.Size(); j++) if (sweeps[i].glow[j]) sweeps[i].glow[j].Destroy();
			sweeps.Delete(i);
		}
	}

	void RunSweeps(int here)
	{
		// a new one, now and then, in the room the player is in (in no step with any other)
		if (here && roomState[here] == FULL && level.maptime >= nextSweep[here])
		{
			nextSweep[here] = level.maptime + Random[AjarWorks](700, 1050);
			Array<AjarWorksRoom> can;
			for (int i = 0; i < rects.Size(); i++) if (rects[i].args[0] == here && rects[i].args[4]) can.Push(rects[i]);
			bool busy = false;
			for (int i = 0; i < sweeps.Size(); i++) if (sweeps[i].room == here) busy = true;
			if (can.Size() && !busy)
			{
				let r = can[Random[AjarWorks](0, can.Size() - 1)];
				int dir = Random[AjarWorks](0, 1) ? 1 : -1;
				Vector2 from = r.args[3] ? (r.pos.x, r.pos.y - dir * (r.args[2] + 128)) : (r.pos.x - dir * (r.args[1] + 128), r.pos.y);
				StartSweep(here, r, SWEEP_LEN, from, dir);
			}
		}
		for (int i = sweeps.Size() - 1; i >= 0; i--)
		{
			let sw = sweeps[i];
			double u = sw.t / double(sw.len);
			Vector2 c = (sw.x1 + (sw.x2 - sw.x1) * u, sw.y1 + (sw.y2 - sw.y1) * u);
			bool alongY = sw.x1 == sw.x2;
			int n = sw.glow.Size();
			double env = sin(180. * u);
			for (int j = 0; j < n; j++)
			{
				let g = sw.glow[j];
				if (!g) continue;
				double off = (j - (n - 1) / 2.) * sw.across;
				Vector2 p = alongY ? (c.x + off, c.y) : (c.x, c.y + off);
				g.SetOrigin((p, FloorAt(p) + 112), true);
				g.Shine(Color(150, 166, 182), 0.62 * env * Guard(p, 352), 352);
			}
			if (++sw.t > sw.len)
			{
				for (int j = 0; j < n; j++) if (sw.glow[j]) sw.glow[j].Destroy();
				sweeps.Delete(i);
			}
		}
	}

	// the player out of a box into its room: a wave from the door they came out of
	void Wave(Actor mo)
	{
		if (!mo || !th) return;
		int k, b;
		[k, b] = th.Where(mo.pos.xy);
		if (prevB > 0 && b == 0 && k == prevK && mo.health > 0 && k > 0 && k < ROOMS && roomState[k] != DONE)
		{
			// the rectangle of the room it is in (a sweep's), or the nearest
			AjarWorksRoom best = null;
			double bd = 1e9;
			for (int i = 0; i < rects.Size(); i++)
			{
				let r = rects[i];
				if (r.args[0] != k || !r.args[4]) continue;
				double dx = max(0, abs(mo.pos.x - r.pos.x) - r.args[1]), dy = max(0, abs(mo.pos.y - r.pos.y) - r.args[2]);
				double dd = dx * dx + dy * dy;
				if (dd < bd) { bd = dd; best = r; }
			}
			if (best)
			{
				// away from the door, toward the room's farther end along its long axis
				int axis = best.args[3];
				double at = axis ? mo.pos.y : mo.pos.x, mid = axis ? best.pos.y : best.pos.x;
				double half = axis ? best.args[2] : best.args[1];
				int dir = abs(mid + half - at) > abs(at - (mid - half)) ? 1 : -1;
				StartSweep(k, best, WAVE_LEN, mo.pos.xy, dir);
				waves++;
			}
		}
		prevK = k; prevB = b;
	}

	// --- the stutter: a stretch of the high line fails for a moment ----------------------------
	void Stutters(int here)
	{
		for (int k = 1; k < ROOMS; k++)
		{
			if (roomState[k] != FULL) continue;
			if (stutLeft[k] > 0)
			{
				stutLeft[k]--;
				bool dark = stutLeft[k] > 0 && Random[AjarWorks](0, 2) > 0;
				if (dark != stutDark[k]) { stutDark[k] = dark; ApplyStutter(k); }
				continue;
			}
			if (level.maptime >= stutAt[k])
			{
				stutLeft[k] = Random[AjarWorks](10, 28);
				stutAt[k] = level.maptime + Random[AjarWorks](150, 600);
			}
		}
	}

	void ApplyStutter(int k)
	{
		for (int i = 0; i < sdLine.Size(); i++)
			if (sdRoom[i] == k && sdStut[i] == k) SetSide(i, Shown(sdFam[i], roomState[k], stutDark[k]));
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
