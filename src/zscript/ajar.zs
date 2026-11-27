// Ajar prototype: frames, doors, and the handler that rewires portals.
//
// Map contract (see tools/make_map.py):
//  * AjarFrame thing: args[0] = id of the frame's portal line. Its tid is the
//    same number; the frame's mouth line calls Thing_Activate on it.
//  * AjarDoor thing:  args[0] = id of the door's far-side portal line,
//    args[1] = colour (1..6), args[2] = id of the frame it starts in (0 = leaning),
//    args[3] = 1 for a fixed doorway: no leaf, no colour, and it stays in that
//    frame for the whole level (ajarmap.doorway).
//    Colour 7 is a Stray door (ajarmap.stray): it has no far side of its own.
//    Hung, it opens onto one of the level's stray places (lines 270..289)
//    or the far side of a coloured door that hangs nowhere just then,
//    stays open for 2 to 5 seconds (StrayTics) and is then gone.
//  * AjarFrame args[4]: 1 if no door but that of args[1] hangs in it; 2 if
//    none but those of args[1] and args[2] (the third frame of a longer
//    chain, ajarmap.way_longer: it is not a way out by itself).
//    3 if none but a leaf of the Pair whose colour is args[1] (MAP12).
//    4 if any door but the one whose colour is args[1] (MAP11's archive).
//    5 if no door but that of args[1] hangs in it, and it is a frame like
//    any other, no way out (MAP32's).
//  * AjarFrame args[1]: the far-side line id of the door that turns this
//    frame into the way out (ajarmap.way_home); lines 590 are its mouths.
//    Frame 193 is the same for a secret way out (MAP15), and lines 591 its
//    mouths: they become Exit_Secret, and the plain way out is not touched.
//    With args[3] the frame is one end of a chain (ajarmap.brass_pair):
//    args[3] is the other brass frame, args[1] and args[2] the far-side
//    lines of the two doors that belong in the pair, either way round. Their
//    far sides are the two ends of the room an AjarLine thing stands in
//    (ajarmap.way_through); with both hung, walking into that room and out
//    of it again ends the level. Until then both can be taken down again.
//    AjarLine args[2], args[3]: a third frame and a third door's far side,
//    for a longer loop and a secret way out (ajarmap.way_longer; LoopLen).
//  * A Pair (ajarmap.pair): two AjarDoor things with the same args[4] (the
//    pair's number) and the same colour, 8 or 9. A leaf has no far side of
//    its own: args[0] is 0 until both hang, and then it is the line of the
//    frame the twin hangs in (set in Hang, cleared in Unhang), so that
//    whatever asks where a hung door leads is told the truth. One leaf hung
//    alone is a shut door: its own face on the frame's line. A frame with an
//    AjarTogether thing (goes.zs) joins a Pair only if its two leaves were
//    hung within two seconds of each other.
//  * The clocked door (colour 10, then.zs; the lab THEN): a Pair whose second
//    leaf (args[3] 3, a shadow nobody sees leaning) always hangs in the twin of
//    the frame the door hangs in: the same frame at the other time. Hung, the
//    two frames lead to each other; taken from either, both are empty and the
//    one door is in the player's hands.
//  * A colour door on a map with two times (then.zs, FarAt): its far side is
//    built at both times, line id args[0] NOW and args[0] + 20 THEN, and it
//    opens on the copy at the time of the frame it hangs in; while it hangs,
//    args[0] is that copy's line (ownFar keeps NOW's). It joins places,
//    never times.
//  * Lines 700 + a frame's id and 801..806 are the lamps of a route board
//    (ajarmap.route_board; BoardTick).
//  * USE works a door or a frame from its own side only: a real press that
//    reaches it through an opening (any line portal) does nothing (reach.zs).

class AjarFrame : Actor
{
	AjarDoor door;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void Activate(Actor activator)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h && !h.HandsDoNotReach(activator, null, self)) h.UseFrame(self, activator);     // not through an opening (reach.zs)
	}
}

// A monster that is not there yet (ajarmap.ambush, AjarHandler.AmbushTick).
class AjarAmbush : Actor
{
	bool armed;
	int wait;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

// The middle of the room a chain of doors runs through (ajarmap.way_through):
// args[0] and args[1] are half its length along x and y.
class AjarLine : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

class AjarDoor : Actor
{
	AjarFrame frame;   // where it hangs, or null
	bool carried;
	Actor nailer;      // who nailed it to its frame, or null (itself: a fixed doorway)
	int strayTics;     // a Stray door that is open: how long it has left
	int hungAt;        // a Pair's leaf: the level's tic it was last hung (goes.zs, two keys at once)
	int joinEnds;      // joined for a time only (goes.zs): the level's tic it shuts again (0: for good)
	int joinTics;      // and how long that time is
	int ownFar;        // a colour door on a map with two times: its own far side's line id (NOW's copy); args[0] is the copy at its frame's time while it hangs (then.zs, FarAt)

	Default
	{
		Radius 20;
		Height 96;
		+NOGRAVITY +WALLSPRITE
	}
	States
	{
	Spawn:
		AJD1 A -1;
		Stop;
	Colour2:
		AJD2 A -1;
		Stop;
	Colour3:
		AJD3 A -1;
		Stop;
	Colour4:
		AJD4 A -1;
		Stop;
	Colour5:
		AJD5 A -1;
		Stop;
	Colour6:
		AJD6 A -1;
		Stop;
	Colour7:
		AJD7 A -1;
		Stop;
	Colour8:
		AJD8 A -1;
		Stop;
	Colour9:
		AJD9 A -1;
		Stop;
	Colour10:          // the clocked door (then.zs)
		AJDT A -1;
		Stop;
	Nailed:            // only so that these sprites are loaded
		AJN1 A -1;
		AJN2 A -1;
		AJN3 A -1;
		AJN4 A -1;
		AJN5 A -1;
		AJN6 A -1;
		AJN7 A -1;
		AJN8 A -1;
		AJN9 A -1;
		AJNT A -1;
		Stop;
	}

	static const Color glow[] = { 0, 0xFF5040, 0x4070FF, 0x40E060, 0xFFC830, 0xB060FF, 0xFF70B0, 0xFFFFFF, 0x30D0C0, 0xFF8A30, 0xFFF0D0 };
	static const string names[] = { "", "RED", "BLUE", "GREEN", "YELLOW", "VIOLET", "PINK", "STRAY", "TEAL", "ORANGE", "CLOCKED" };
	const STRAY = 7;
	const CLOCKED = 10;
	const SHADOW = 3;      // args[3] of the clocked door's other leaf

	int Colour() { return clamp(args[1], 1, 10); }
	bool IsClocked() { return args[1] == CLOCKED; }
	bool IsShadow() { return IsClocked() && args[3] == SHADOW; }
	bool IsStray() { return args[1] == STRAY; }
	bool IsPair() { return args[4] != 0; }
	// The other leaf of a Pair.
	AjarDoor Twin()
	{
		if (!IsPair()) return null;
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor o;
		while (o = AjarDoor(it.Next())) if (o != self && o.args[4] == args[4]) return o;
		return null;
	}
	// A Pair leaf that hangs while its twin does not: a shut door, flat in its frame.
	bool Shut() { return IsPair() && frame && !args[0]; }
	// Nobody can take it out of its frame: nailed, a fixed doorway, or a Stray door once open.
	bool Stuck() { return nailer || (IsStray() && frame); }
	string BackTex() { return String.Format("AJDR%d", Colour()); }
	string Label() { return names[Colour()]; }

	void Show()
	{
		static const name spr[] = { 'AJD1', 'AJD1', 'AJD2', 'AJD3', 'AJD4', 'AJD5', 'AJD6', 'AJD7', 'AJD8', 'AJD9', 'AJDT' };
		static const name nailedSpr[] = { 'AJN1', 'AJN1', 'AJN2', 'AJN3', 'AJN4', 'AJN5', 'AJN6', 'AJN7', 'AJN8', 'AJN9', 'AJNT' };
		if (nailer == self || Shut()) { Hide(); return; }      // a fixed doorway has no leaf; a shut one is drawn on its line
		if (IsShadow() && !frame) { Hide(); return; }          // the clocked door's other leaf is only ever seen hung
		int c = Colour();
		sprite = GetSpriteIndex(nailer ? nailedSpr[c] : spr[c]);
		bInvisible = false;
		bOnlyVisibleInMirrors = args[3] == 2;      // ajarmap.door(unseen=True), until it is first taken
		if (bOnlyVisibleInMirrors) A_RemoveLight('glow');
		else A_AttachLight('glow', DynamicLight.PointLight, glow[c], 80, 80, 0, (0, 0, 56));
	}

	void Hide()
	{
		bInvisible = true;
		A_RemoveLight('glow');
	}

	override bool Used(Actor user)
	{
		if (carried) return false;
		if (IsShadow() && !frame) return false;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h) return false;
		if (h.UseGoesOn(self, user)) return false;     // aimed past it at a switch: the press goes on to that (leaf.zs)
		if (h.HandsDoNotReach(user, self, null)) return false;     // a real press through an opening: hands do not reach (reach.zs)
		if (frame) h.UseFrame(frame, user);
		else h.TakeLeaning(self, user);
		return true;
	}
}

class AjarHandler : EventHandler
{
	const FRAME_TEX = "AJFRAME";
	const SQUEEZE_ID = 500;       // line id of every squeeze (ajarmap.squeeze)
	const STRAY_ID = 270;         // 270..289: the places a Stray door may open onto (ajarmap.stray_place)
	const STRAY_PLACES = 20;
	const STRAY_TICS = 175;       // the longest a Stray door stays open: see StrayTics()
	const HOME_MOUTH = 590;       // both mouths of a way out the player builds (ajarmap.way_home)
	const SECRET_HOME = 193;      // the brass frame of a secret way out the player builds (ajarmap.SECRET_HOME)
	const SECRET_MOUTH = 591;     // and both its mouths
	AjarDoor carried;
	int testTic;

	// --- portal plumbing -------------------------------------------------
	void Link(int fromLine, int toLine, string blankTex)
	{
		if (!fromLine) return;        // a Pair leaf whose twin hangs nowhere has no far side
		level.ExecuteSpecial(107 /* Line_SetPortalTarget */, null, null, false, fromLine, toLine);
		// A Doom door that stays a Doom door with a portal on its face (the Doom door lab, doomlab.zs): only
		// its portal is switched, and with none it is the plain Doom door.
		if (AjarDoomLab.Gate(fromLine)) return;
		// With no target the line is a blank wall again: make it solid.
		Line l = FindLine(fromLine);
		if (!l) return;
		int solid = Line.ML_BLOCKING | Line.ML_BLOCKEVERYTHING | Line.ML_SOUNDBLOCK;
		if (toLine) l.flags &= ~solid;
		else l.flags |= solid;
		// The blank-wall texture would be drawn over the portal view, so it
		// is only present while the line leads nowhere.
		TextureID tex;
		if (toLine) tex.SetNull();
		else tex = TexMan.CheckForTexture(blankTex, TexMan.Type_Any);
		l.sidedef[0].SetTexture(Side.mid, tex);
		if (!toLine) CratesClear(l);      // a crate in the doorway is not left in the wall (belt.zs)
	}

	Line FindLine(int id)
	{
		if (!id) return null;
		let it = level.CreateLineIdIterator(id);
		int i = it.Next();
		if (i < 0) return null;
		return level.lines[i];
	}

	AjarFrame FindFrame(int id)
	{
		let it = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(it.Next()))
			if (f.args[0] == id) return f;
		return null;
	}

	// --- door state changes ----------------------------------------------
	// --- the Stray door ----------------------------------------------------
	// Which place a Stray door opens onto is drawn from the level's pool,
	// without repeats until every place has come up (so no streaks, and a
	// secret place does come up in the end). 0: the level has none free.
	Array<int> strayLeft;
	// How long this hanging stays open: 2 to 5 seconds, drawn afresh each
	// time, the short ones likelier (2 s 35%, 3 s 35%, 4 s 20%, 5 s 10%).
	// (The smoke tests always get the longest.)
	int StrayTics()
	{
		if (CVar.GetCVar("ajar_autotest").GetInt()) return STRAY_TICS;
		int r = random[AjarStray](0, 99);
		return 35 * (r < 35 ? 2 : r < 70 ? 3 : r < 90 ? 4 : 5);
	}

	// Where a Stray door may open: the level's own stray places, and the far
	// side of every coloured door. (In that order, and the far sides by
	// number: the smoke tests take the pool in order.)
	void StrayPool(out Array<int> ids)
	{
		ids.Clear();
		Actor line = ChainRoom();
		for (int id = STRAY_ID; id < STRAY_ID + STRAY_PLACES; id++) if (FindLine(id)) ids.Push(id);
		int places = ids.Size();
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			if (d.IsStray() || d.IsPair() || !FindLine(d.args[0]) || ids.Find(d.args[0]) < ids.Size()) continue;
			// not the room of a longer chain's third door (Vadim, 2026-11-18): a
			// door comes there only through that door, hung somewhere, so one
			// hung in its frame can always be fetched again, and the frame
			// takes any door
			if (line && d.args[0] == line.args[3]) continue;
			int at = places;
			while (at < ids.Size() && ids[at] < d.args[0]) at++;
			ids.Insert(at, d.args[0]);
		}
	}

	// Is some door open onto this place right now? A coloured door that
	// hangs anywhere is open onto its far side; so is a Stray door onto the
	// place it drew.
	bool StrayUsed(int id)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor o;
		while (o = AjarDoor(di.Next())) if (o.frame && o.args[0] == id) return true;
		return false;
	}

	// What a place shows while nothing is open onto it: the shut door of its
	// colour if it is a coloured door's far side, a shut Stray door if not.
	string PlaceTex(int id)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor o;
		while (o = AjarDoor(di.Next())) if (!o.IsStray() && o.args[0] == id) return o.BackTex();
		return "AJDR7";
	}

	int DrawStray()
	{
		Array<int> free;
		for (int pass = 0; pass < 2 && !free.Size(); pass++)
		{
			if (pass || !strayLeft.Size()) StrayPool(strayLeft);
			for (int i = 0; i < strayLeft.Size(); i++) if (!StrayUsed(strayLeft[i])) free.Push(strayLeft[i]);
		}
		if (!free.Size()) return 0;
		// (the smoke tests take the pool in order)
		int id = free[CVar.GetCVar("ajar_autotest").GetInt() ? 0 : random[AjarStray](0, free.Size() - 1)];
		strayLeft.Delete(strayLeft.Find(id));
		return id;
	}

	// Is there a place left for one more Stray door to open onto?
	bool StrayRoom()
	{
		Array<int> ids;
		StrayPool(ids);
		for (int i = 0; i < ids.Size(); i++) if (!StrayUsed(ids[i])) return true;
		return false;
	}

	// The least time any open Stray door has left, or -1; `held`: a nailer
	// has nailed it open, and it stays until the nails fall out.
	int, bool StrayTime()
	{
		int best = -1;
		bool held = false;
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			if (!d.IsStray() || !d.frame) continue;
			if (best < 0 || d.strayTics < best) { best = d.strayTics; held = d.nailer != null; }
		}
		return best, held;
	}

	// Whatever stands in an opening when it shuts is cut in two, the player
	// included. (A thing goes through when its centre crosses the line, so
	// nothing is ever half-way: this is whoever overlaps the line.)
	void Telefrag(Line l)
	{
		if (!l) return;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bShootable || a.health <= 0) continue;
			Vector2 w = a.pos.xy - l.v1.p;
			double u = clamp((w dot l.delta) / (l.delta dot l.delta), 0, 1);
			if ((w - l.delta * u).Length() >= a.radius) continue;
			double fz = l.frontsector.floorplane.ZAtPoint(a.pos.xy);
			if (a.pos.z > fz + 96 || a.pos.z + a.height < fz) continue;
			a.DamageMobj(null, null, 1000000, 'Telefrag');
		}
	}

	void StrayTick()
	{
		Array<AjarDoor> over;
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			if (!d.IsStray() || !d.frame) continue;
			if (d.nailer) continue;                    // nailed open
			if (d.strayTics > 0 && d.strayTics % 35 == 0) d.A_StartSound("misc/chat2", CHAN_AUTO);
			if (--d.strayTics <= 0) over.Push(d);
		}
		for (int i = 0; i < over.Size(); i++) StrayShut(over[i]);
	}

	// An open Stray door shuts and is gone, with whatever stands in it.
	void StrayShut(AjarDoor d)
	{
		AjarFrame f = d.frame;
		Telefrag(FindLine(f.args[0]));
		Telefrag(FindLine(d.args[0]));
		Link(f.args[0], 0, FRAME_TEX);
		Link(d.args[0], 0, PlaceTex(d.args[0]));
		f.door = null;
		d.A_StartSound("doors/dr1_clos", CHAN_AUTO);
		Say("The STRAY door is gone.");
		d.Destroy();
	}

	// --- a shutter on a timer (ajarmap.shutter) -----------------------------
	// A lever sends it up (Door_Raise on sector tag 600) and it comes down by
	// itself. This only keeps the time for the HUD and says what happened.
	const SHUTTER_TAG = 600;
	int shutterLeft;       // tics until it starts down again; -1: it is shut
	int shutterWait;       // how long the last pull (or push from inside) holds it up
	override void WorldLineActivated(WorldEvent e)
	{
		Line l = e.ActivatedLine;
		if (l && l.special == 12 && l.args[0] == SHUTTER_TAG) shutterWait = l.args[2];
	}

	// A lever or a bell that opens something out of sight (Door_Open on a
	// wall with nothing behind it): say so, or nothing seems to happen.
	override void WorldLinePreActivated(WorldEvent e)
	{
		Line l = e.ActivatedLine;
		if (!l || l.special != 11 || l.backsector) return;
		if (e.ActivationType == SPAC_Impact) Say("The bell rings.\nSomewhere close a bolt is drawn.");
		else if (e.ActivationType == SPAC_Use) Say("You pull the lever.\nSomewhere in the building a bolt is drawn.");
	}

	// --- ambushes (ajarmap.ambush) ------------------------------------------
	// An AjarAmbush thing is a monster that is not there yet. args[0] is what
	// brings it: 1..4, taking that room key; 11..16, taking the door of that
	// colour (less 10) for the first time; 21.., the target or sensor with that
	// tag (less 20) set off; 41.., MAP17's checkers; 50, MAP18's first lap;
	// 51..59, MAP19's register with that number (less 50) signed (pass.zs);
	// 60 and 61, MAP20's basin first at or over, at or under a height (args[4]: water.zs).
	// 62, MAP21's bolted sector tag args[4] first open; 63, a long cause (tid args[4] / 16) first set to the
	// setting args[4] % 16 (then.zs). 64, MAP22's turn: the two times first joined (then.zs, JoinedDue); one
	// with args[4] 1..4 carries that room key (map22.zs, AjarKeyBearer). 65, keys 1 and 2 both in hand.
	// args[3], if set: it holds back until the player is
	// within that distance of it and in sight of it. args[1]
	// is the monster's Doom editor number. It comes in a flash where the thing stands, a moment
	// after, facing the way the thing faces, and knows where the player is.
	// If something stands in its place it waits until the place is free.
	static class<Actor> AmbushClass(int n)
	{
		switch (n)
		{
		case 3004: return "ZombieMan";
		case 9: return "ShotgunGuy";
		case 3001: return "DoomImp";
		case 3002: return "Demon";
		case 58: return "Spectre";
		case 65: return "ChaingunGuy";
		case 69: return "HellKnight";
		case 3003: return "BaronOfHell";
		case 66: return "Revenant";
		case 3006: return "LostSoul";
		case 3005: return "Cacodemon";
		case 67: return "Fatso";
		case 68: return "Arachnotron";
		case 71: return "PainElemental";
		case 64: return "Archvile";
		case 20004: return "AjarNailer";       // MAP16: it comes to the foot of the stair
		case 16: return "Cyberdemon";
		case 7: return "SpiderMastermind";      // MAP33: a post of the turbine hall (third.zs)
		}
		return null;
	}

	// AjarAmbush cause 62 (MAP21): some sector with this tag has its ceiling over its floor.
	static bool SectorOpen(int tag)
	{
		let si = level.CreateSectorTagIterator(tag);
		int s;
		while ((s = si.Next()) >= 0)
		{
			Sector sec = level.sectors[s];
			if (sec.ceilingplane.ZAtPoint(sec.centerspot) > sec.floorplane.ZAtPoint(sec.centerspot) + 56) return true;
		}
		return false;
	}

	int ambushHid[50], ambushShown[50];      // by cause: ambushers that came unseen (UnseenJoin), and seen

	void AmbushTick(PlayerPawn mo)
	{
		if (level.maptime % 5) return;
		let it = ThinkerIterator.Create("AjarAmbush");
		AjarAmbush a;
		while (a = AjarAmbush(it.Next()))
		{
			int g = a.args[0];
			if (!a.armed)
			{
				if (g == 60 || g == 61)                         // MAP20: a basin first at or over / under a height (water.zs)
				{
					if (!AjarWaterHandler.WaterDue(g, a.args[4])) continue;
				}
				else if (g == 62)                               // MAP21: a sector tagged args[4] first stands open (a bolted door's bolts drawn)
				{
					if (!SectorOpen(a.args[4])) continue;
				}
				else if (g == 63)                               // MAP21: a long cause first set to a setting, and arrived (then.zs)
				{
					if (!AjarThenHandler.CauseDue(a.args[4])) continue;
				}
				else if (g == 64)                               // MAP22: the turn, the two times first joined (then.zs)
				{
					if (!AjarThenHandler.JoinedDue()) continue;
				}
				else if (g == 65)                               // MAP22: keys 1 and 2 both in hand
				{
					if (!Has(mo, 1) || !Has(mo, 2)) continue;
				}
				else if (g == 50)                               // MAP18: the first lap a pulse has made (clock.zs)
				{
					if (!delayFirstLap) continue;
				}
				else if (g > 50 && g < 60)                      // MAP19: register g - 50 is signed (pass.zs)
				{
					if (!AjarPassRegister.IsSigned(g - 50)) continue;
				}
				else if (g > 40)                                // MAP17: the order that opens tag g - 40 is filled
				{
					if (!CheckerOpened(g - 40)) continue;
				}
				else if (g > 20)
				{
					let tg = TargetTagged(g - 20);
					if (!tg || !tg.done) continue;
				}
				else if (g >= 1 && g <= 4 ? !Has(mo, g) : !(carried && carried.Colour() == g - 10)) continue;
				if (a.args[3] && (a.Distance2D(mo) > a.args[3] || !a.CheckSight(mo))) continue;
				a.armed = true;
				a.wait = 20 + 5 * random(0, 5) + 35 * a.args[2];    // args[2]: seconds a later wave holds back
			}
			if (a.wait > 0) { a.wait -= 5; continue; }
			class<Actor> cls = AmbushClass(a.args[1]);
			if (!cls) { a.Destroy(); continue; }
			a.SetZ(a.floorz);                                   // one in a lift car comes where the car is now
			Actor m = Actor.Spawn(cls, a.pos, ALLOW_REPLACE);
			if (!m) continue;
			if (!m.TestMobjLocation()) { m.ClearCounters(); m.Destroy(); continue; }
			m.angle = a.angle;
			Actor.Spawn("TeleportFog", a.pos, ALLOW_REPLACE);
			bool hid = UnseenJoin(m);                           // come into a room only the glass shows
			if (g >= 0 && g < 50) { if (hid) ambushHid[g]++; else ambushShown[g]++; }
			bool bears = g == 64 && a.args[4] >= 1 && a.args[4] <= 4;      // MAP22: it carries a room key (map22.zs)
			if (bears) AjarKeyBearer.Bear(m, a.args[4]);
			if (CVar.GetCVar("ajar_autotest").GetInt() && bears)
			{
				// the tests kill it themselves, to see the key given
				Console.Printf("AJARTEST ambusher=%s cause=%d unseen=%d bears=%d", m.GetClassName(), g, hid, a.args[4]);
			}
			else if (CVar.GetCVar("ajar_autotest").GetInt())
			{
				// a scripted walkthrough: it came, which is all the test wants
				// to know, and it must not stand in the walker's way
				Console.Printf("AJARTEST ambusher=%s cause=%d unseen=%d", m.GetClassName(), g, hid);
				m.ClearCounters();
				m.Destroy();
			}
			else
			{
				m.target = mo;
				if (m.SeeState) m.SetState(m.SeeState);
				m.A_StartSound(m.SeeSound, CHAN_VOICE);
			}
			a.Destroy();
		}
	}

	void ShutterTick()
	{
		let it = level.CreateSectorTagIterator(SHUTTER_TAG);
		int i = it.Next();
		if (i < 0) { shutterLeft = -1; return; }
		Sector s = level.sectors[i];
		if (s.CenterCeiling() <= s.CenterFloor()) { shutterLeft = -1; return; }
		if (shutterLeft >= 0) { if (shutterLeft > 0) shutterLeft--; return; }
		if (!shutterWait) shutterWait = 280;
		shutterLeft = shutterWait + 12;        // and the time it takes to go up
		if (shutterWait > 70)
			Say(String.Format("Across the loading dock a shutter goes up.\nIt comes down again in %d seconds.", shutterWait / 35));
	}

	// --- a way out the player builds ---------------------------------------
	// The door whose far side is in the night room, hung in the frame that
	// faces it: the room opens onto itself. The door stays there for good,
	// as the doorway of every earlier level's way out, and walking into
	// either end ends the level.
	//
	// The same in the brass frame SECRET_HOME (MAP15, 2026-11-19) is a secret
	// way out: its mouths end the level by Exit_Secret, and the plain way out
	// (wayOutBuilt, HOME_MOUTH) is left as it was.
	bool wayOutBuilt, secretOutBuilt;
	void ComeHome(AjarDoor d, AjarFrame f)
	{
		d.nailer = d;
		bool secret = f.args[0] == SECRET_HOME;
		if (secret) secretOutBuilt = true;
		else wayOutBuilt = true;
		let it = level.CreateLineIdIterator(secret ? SECRET_MOUTH : HOME_MOUTH);
		int i;
		while ((i = it.Next()) >= 0)
		{
			Line l = level.lines[i];
			l.special = secret ? 244 /* Exit_Secret */ : 243 /* Exit_Normal */;
			l.args[0] = 0;
			l.activation = SPAC_Cross;
		}
	}

	// The way out as a chain (Vadim, 2026-11-16): two brass frames in one
	// place, and two doors whose far sides are the two ends of another room
	// (the line, where an AjarLine thing stands). With both hung, either way
	// round, the two open onto each other without end.
	//
	// Nothing is fixed by that (Vadim, 2026-11-17): a brass frame is a frame
	// like any other, and either door can be taken down again. Only when the
	// player walks onto the line through the closed loop do its doors stay,
	// and leaving the line again by one of its two doors ends the level
	// (ChainTick). Leaving it by its way out on foot (the drop) ends nothing
	// (Vadim, 2026-11-17), and frees its doors again (2026-11-18).
	//
	// The longer loop (MAP10): the AjarLine's args[2] is a third frame, in a
	// room that has the far side args[3] of a third door. That door and one of
	// the two in the brass frames, the other of the two in the third frame: a
	// loop of three rooms. Closing it is a secret, and leaving the line by it
	// is the secret way out.
	//
	// One of the two brass frames may be in a lift car (Vadim, 2026-11-19;
	// MAP14), across a landing from the other. Then they face each other
	// only while the car stands at that floor, and only then is the loop
	// closed (BrassLevel): with the car anywhere else the two doors are a way
	// between the car and that floor, by the line, and nothing more.
	bool chainBuilt, onTheLine, longFound;
	bool chainHung;        // the loop's doors hang in its frames, level or not
	Vector2 lineAt;        // where on the line the player last was, from its middle
	int chainLen;          // 0, or how many rooms the closed loop has: 2 or 3

	AjarFrame BrassFrame()
	{
		let it = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(it.Next())) if (f.args[3]) return f;
		return null;
	}

	// Do the two brass frames face each other? Those of one room always do.
	// With one of them in a lift car: while the car stands level with the other.
	bool BrassLevel(AjarFrame f, AjarFrame o)
	{
		if (liftKnown < 2) return true;
		int n = liftSectors.Size();
		if (liftSectors.Find(f.CurSector.Index()) == n && liftSectors.Find(o.CurSector.Index()) == n) return true;
		// (by their floors: the engine pushes a frame in a car under the ceiling
		// its recess had when the level began, each tic, until LiftTick puts it back)
		return !LiftMoving() && abs(f.CurSector.floorplane.ZatPoint(f.pos.xy) - o.CurSector.floorplane.ZatPoint(o.pos.xy)) < 1;
	}

	int LoopLen(Actor room)
	{
		chainHung = false;
		AjarFrame f = BrassFrame();
		AjarFrame o = f ? FindFrame(f.args[3]) : null;
		if (!o || !f.door || !o.door || f.door.IsStray() || o.door.IsStray()) return 0;
		int a = f.args[1], b = f.args[2], x = f.door.args[0], y = o.door.args[0];
		if ((x == a && y == b) || (x == b && y == a))
		{
			chainHung = true;
			return BrassLevel(f, o) ? 2 : 0;
		}
		int c = room.args[3];
		AjarFrame t = room.args[2] ? FindFrame(room.args[2]) : null;
		if (!t || !t.door || t.door.IsStray() || (x != c && y != c)) return 0;
		int other = x == c ? y : x, z = t.door.args[0];
		return (other == a && z == b) || (other == b && z == a) ? 3 : 0;
	}

	Actor ChainRoom()
	{
		let it = ThinkerIterator.Create("AjarLine");
		return Actor(it.Next());
	}

	// Is the loop closed, and which? Called when a door is hung (so that what
	// is said about it is right) and every tic.
	void ChainUpdate()
	{
		Actor room = ChainRoom();
		if (!room || onTheLine) return;
		bool hung = chainHung;
		int was = chainLen;
		chainLen = LoopLen(room);
		chainBuilt = wayOutBuilt = chainLen > 0;
		let mo = players[consoleplayer].mo;
		// the doors hung already, and now the car has come level (or gone)
		if (hung && chainHung && !was && chainLen == 2)
			Say("The lift stops level with the other brass frame.\nThe way out runs through it.");
		else if (hung && chainHung && was == 2 && !chainLen)
			Say("The lift has left: the brass frames no longer face each other.");
		if (chainLen == 3 && !longFound && mo)
		{
			longFound = true;
			mo.GiveSecret(false, true);
			if (CVar.GetCVar("ajar_autotest").GetInt())
				Console.Printf("AJARTEST longLoop secrets=%d/%d", level.found_secrets, level.total_secrets);
		}
	}

	// Is d one of the doors of the loop that is closed now?
	bool InChain(AjarDoor d)
	{
		Actor room = ChainRoom();
		if (!room || !chainLen || !d || !d.frame) return false;
		return d.frame.args[3] || (chainLen == 3 && d.frame.args[0] == room.args[2]);
	}

	void ChainTick(Actor mo)
	{
		Actor room = ChainRoom();
		if (!room) return;
		ChainUpdate();
		if (!chainLen) return;
		Vector2 d = mo.pos.xy - room.pos.xy;
		// the mouths are 16 deep: 24 past a wall is through a door, or out by the drop
		bool gone = abs(d.x) > room.args[0] + 24 || abs(d.y) > room.args[1] + 24;
		if (onTheLine && !gone) lineAt = d;
		if (abs(d.x) < room.args[0] && abs(d.y) < room.args[1])
		{
			if (onTheLine) return;
			// on the line, through the loop: now its doors stay
			onTheLine = true;
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor o;
			while (o = AjarDoor(di.Next())) if (InChain(o)) { o.nailer = o; o.Show(); }
		}
		else if (onTheLine && gone)
		{
			onTheLine = false;
			// The doors are in the middle of its two ends, 64 wide; the way out on
			// foot is in a side wall. Left from anywhere but a door's mouth: not
			// by the line, and nothing ends
			if (abs(lineAt.y) >= 64)
			{
				// ... and its doors are doors again (Vadim, 2026-11-18): the plain
				// loop can be taken apart and the longer one built
				let di = ThinkerIterator.Create("AjarDoor");
				AjarDoor o;
				while (o = AjarDoor(di.Next())) if (o.nailer == o && InChain(o)) o.nailer = null;
				if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST leftTheLine=onFoot");
				return;
			}
			if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST wayOut=%s", chainLen == 3 ? "secret" : "plain");
			level.ExecuteSpecial(chainLen == 3 ? 244 /* Exit_Secret */ : 243 /* Exit_Normal */, mo, null, false, 0);
		}
	}

	// --- the route board of a bus stop (ajarmap.route_board) ------------------
	// A lamp is a piece of wall with a line id: 600 + a frame's id (it shows
	// the colour of the door that hangs in that frame, white for a Stray one)
	// or 800 + a colour (lit while that door hangs anywhere: its far side is a
	// door of the bus). Its texture is AJR, the door's number, the colour.
	void Lamp(int id, int c)
	{
		let it = level.CreateLineIdIterator(id);
		int i;
		while ((i = it.Next()) >= 0)
		{
			Side sd = level.lines[i].sidedef[0];
			string n = TexMan.GetName(sd.GetTexture(Side.mid));
			if (n.Length() != 5 || n.Left(3) != "AJR") continue;
			// (the clocked door's lamp is AJRnC; a colour with no lamp drawn shows as a line that runs, 7)
			string want = c == AjarDoor.CLOCKED ? n.Left(4) .. "C" : String.Format("%s%d", n.Left(4), c);
			TextureID tex = TexMan.CheckForTexture(want, TexMan.Type_Any);
			if (!tex.IsValid()) { want = n.Left(4) .. "7"; tex = TexMan.CheckForTexture(want, TexMan.Type_Any); }
			if (want != n && tex.IsValid()) sd.SetTexture(Side.mid, tex);
		}
	}

	void BoardTick()
	{
		if (level.maptime % 8) return;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next())) Lamp(600 + f.args[0], f.door && f.door.args[1] ? f.door.Colour() : 0);
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.args[1] >= 1 && d.args[1] <= 6) Lamp(800 + d.args[1], d.frame ? d.args[1] : 0);
	}

	void Hang(AjarDoor d, AjarFrame f)
	{
		if (d.IsClocked() && !d.IsShadow()) ClockedHang(d, f);     // its other leaf into the same frame at the other time (then.zs)
		if (d.IsStray()) { d.args[0] = DrawStray(); d.strayTics = StrayTics(); }
		else
		{
			d.args[0] = FarAt(d, f);       // a colour door on a map with two times: its far side at f's time (then.zs)
			// a Stray door open onto this door's far side gives way to it
			let si = ThinkerIterator.Create("AjarDoor");
			AjarDoor o;
			while (o = AjarDoor(si.Next())) if (o.IsStray() && o.frame && o.args[0] == d.args[0]) { StrayShut(o); break; }
			// (a sprung frame made with `only` takes its door and is no way out: shut.zs)
			if (!f.args[3] && f.args[4] != 2 && f.args[4] != 5 && f.args[1] && f.args[1] == d.args[0] && !PlateFor(f)) ComeHome(d, f);
		}
		// A Pair leaf leads to the frame its twin hangs in, if it hangs; and
		// then the twin leads here.
		AjarDoor tw = d.Twin();
		if (d.IsPair())
		{
			// (two frames that are hung "together" join only leaves hung close in time: goes.zs)
			d.hungAt = level.maptime - hangBack;        // (hangBack: a fight of goes wound, goes.zs)
			d.args[0] = tw && tw.frame && InTime(d, f, tw) ? tw.frame.args[0] : 0;
			d.joinEnds = d.joinTics = 0;
			if (d.args[0])
			{
				tw.args[0] = f.args[0];
				JoinFor(d, tw, 35 * JoinSeconds(f.args[0], tw.frame.args[0]));      // (goes.zs: a Pair joined for a time)
			}
		}
		Link(f.args[0], d.args[0], d.IsPair() ? d.BackTex() : FRAME_TEX);
		Link(d.args[0], f.args[0], d.BackTex());
		d.frame = f;
		d.carried = false;
		f.door = d;
		if (tw && tw.frame) tw.Show();

		// stand the leaf open at a jamb of the frame, clear of the walls round it (leaf.zs)
		PoseLeaf(d, f);
		d.Show();
		ChainUpdate();
		Spring(f);          // a sprung frame's door is shut unless its plate is pressed (plate.zs)
	}

	AjarDoor Unhang(AjarFrame f)
	{
		AjarDoor d = f.door;
		Unspring(f, d);
		Link(f.args[0], 0, FRAME_TEX);
		Link(d.args[0], 0, d.BackTex());       // a Pair: the twin's frame, which shows a shut door now
		f.door = null;
		d.frame = null;
		d.carried = true;
		d.Hide();
		if (d.ownFar) d.args[0] = d.ownFar;        // carried, a colour door is its own far side again (then.zs, FarAt)
		if (d.IsPair())
		{
			AjarDoor tw = d.Twin();
			d.args[0] = 0;
			d.joinEnds = d.joinTics = 0;
			if (tw) { tw.args[0] = 0; tw.joinEnds = tw.joinTics = 0; if (tw.frame) tw.Show(); }
		}
		ChainUpdate();
		if (d.IsClocked()) d = ClockedUnhang(d);       // both leaves come down; the one door is the one taken (then.zs)
		return d;
	}

	// The thief's door work, the same three moves the player has. Returns the
	// door it carries afterwards.
	AjarDoor ThiefUsesFrame(AjarFrame f, AjarDoor carrying, Actor thief)
	{
		AjarDoor old = f.door ? Unhang(f) : null;
		if (carrying) Hang(carrying, f);
		if (carrying && old) PlaySwap(thief);
		else if (carrying) PlaySet(thief);
		else PlayTake(thief);
		if (carrying && old) Say("A thief swaps the " .. old.Label() .. " door for the " .. carrying.Label() .. " one!");
		else if (carrying) Say("A thief hangs the " .. carrying.Label() .. " door!");
		else if (old) Say("A thief has taken the " .. old.Label() .. " door!");
		return old;
	}

	void ThiefPicksUp(AjarDoor d, Actor thief)
	{
		d.carried = true;
		d.Hide();
		PlayTake(thief);
		Say("A thief picks up the " .. d.Label() .. " door!");
	}

	// --- the sounds of taking and hanging a door ---------------------------
	// Every door taken out of a frame or off the floor (take) and every door
	// hung in a frame (set) plays through these: the player's, the thief's,
	// and an earlier self's in a room of goes (plate.zs, GhostDoors).
	// The game's sounds, chosen by Vadim by ear in the sound lab on
	// 2026-11-23: the take is the game's own "field drops" (tools/sfx.py,
	// ajar/take -> sounds/ajtake.wav), the set Doom's lift stopping
	// (plats/pt1_stop) played at pitch 0.7. Every level has these: an empty
	// takeSound / setSound. Only the sound lab (soundlab.zs, map SOUND) puts
	// another name there to compare, with its pitch (takePitch / setPitch: 2
	// an octave up, 0.5 an octave down; 1 the sound's own).
	const TAKE_SOUND = "ajar/take";
	const TAKE_PITCH = 1.0;
	const SET_SOUND = "plats/pt1_stop";
	const SET_PITCH = 0.7;
	string takeSound, setSound;
	double takePitch, setPitch;
	int swapSetTics;            // a swap's set sound is still to come in this many tics
	Actor swapBy;

	clearscope string TakeName() { return takeSound != "" ? takeSound : TAKE_SOUND; }
	clearscope string SetName() { return setSound != "" ? setSound : SET_SOUND; }
	clearscope double UsedTakePitch() { return takeSound != "" ? takePitch : TAKE_PITCH; }
	clearscope double UsedSetPitch() { return setSound != "" ? setPitch : SET_PITCH; }
	// A_StartSound's pitch: 0 is the sound's own
	static double PitchArg(double p) { return p > 0 && p != 1 ? p : 0; }

	void PlayTake(Actor who) { if (who) who.A_StartSound(TakeName(), CHAN_AUTO, 0, 1.0, ATTN_NORM, PitchArg(UsedTakePitch())); }
	void PlaySet(Actor who) { if (who) who.A_StartSound(SetName(), CHAN_AUTO, 0, 1.0, ATTN_NORM, PitchArg(UsedSetPitch())); }

	// A swap: the door comes off (take), and a moment later the other goes
	// on (set).
	void PlaySwap(Actor who)
	{
		PlayTake(who);
		swapBy = who;
		swapSetTics = 9;
	}

	void SwapTick()
	{
		if (swapSetTics <= 0 || --swapSetTics > 0) return;
		PlaySet(swapBy);
		swapBy = null;
	}

	// A carried door is put down where `at` stands, to be picked up again.
	void DropDoor(AjarDoor d, Actor at)
	{
		d.carried = false;
		d.SetOrigin(at.pos, false);
		d.angle = at.angle;
		d.Show();
	}

	string said;                // what was said last (the smoke tests read it)
	void Say(string msg)
	{
		said = msg;
		Console.MidPrint(smallfont, msg);
	}

	// the first time a lodger knocks in a level
	bool lodgerHeard;
	void LodgerKnocks()
	{
		if (lodgerHeard) return;
		lodgerHeard = true;
		Say("Something knocks from inside an empty frame.\nA door hung there would shut it in.");
	}

	// A nailer fixes a hung door to its frame; when it dies its nails fall out.
	void Nail(AjarDoor d, Actor by)
	{
		d.nailer = by;
		d.Show();
		Say("The " .. d.Label() .. " door is nailed to its frame!");
	}

	void Unnail(Actor by)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		int n = 0;
		while (d = AjarDoor(di.Next()))
		{
			if (d.nailer != by) continue;
			d.nailer = null;
			if (!d.carried) d.Show();
			n++;
		}
		if (n) Say("The nails fall out.");
	}

	// What hanging the carried door in f has to say.
	void SayHung(AjarDoor d, AjarDoor old)
	{
		if (d.IsClocked())
			Say((old ? "You swap the " .. old.Label() .. " door for the clocked one.\n" : "") ..
				"The clocked door opens onto this very frame,\nforty years before (or after).");
		else if (d.IsPair() && d.args[0] && pairSaidAt == level.maptime + 1)
			return;             // (the first join for a time has said so: goes.zs, JoinFor)
		else if (d.IsPair() && d.args[0])
			Say("Both leaves of the " .. d.Label() .. " pair hang:\neach frame opens onto the other.");
		else if (d.IsPair() && Late(d))
			Say(LateText(d));
		else if (d.IsPair() && d.frame && Together(d.frame))
			Say("One leaf of the " .. d.Label() .. " pair, in a frame marked with a clock:\nits twin must be hung within two seconds, or it stays shut.");
		else if (d.IsPair())
			Say("One leaf of the " .. d.Label() .. " pair. It stays shut\nuntil its twin hangs in a frame somewhere.");
		else if (d.IsStray())
			Say((old ? "You swap the " .. old.Label() .. " door for the STRAY one.\n" : "") ..
				"The STRAY door opens onto somewhere. It will not stay.");
		else if (chainLen == 3 && InChain(d))
			Say("Three doors, three frames: the long way round.\nA secret way out runs through it!");
		else if (chainLen == 2 && InChain(d))
			Say("Two doors, two frames, one room at the other end of both.\nThe way out runs through it.");
		else if (chainHung && d.frame && d.frame.args[3])
			Say("Two doors, two brass frames, but they do not face each other:\nthe lift is at another floor.");
		else if (d.nailer == d && d.frame && d.frame.args[0] == SECRET_HOME)
			Say("The " .. d.Label() .. " door opens onto the room it hangs in.\nThat is a secret way out!");
		else if (d.nailer == d)
			Say("The " .. d.Label() .. " door opens onto the room it hangs in.\nThat is the way out.");
		else if (old) Say("You swap the " .. (old.IsClocked() ? "clocked" : old.Label()) .. " door for the " .. d.Label() .. " one.");
		else Say("The " .. d.Label() .. " door opens where it always opens.");
	}

	void UseFrame(AjarFrame f, Actor user)
	{
		if (f.door && f.door.IsStray() && !f.door.nailer)
		{
			Say("The STRAY door is already on its way.\nNobody takes it down now.");
			return;
		}
		if (carried && carried.IsStray() && !StrayRoom())
		{
			Say("The STRAY door has nowhere to open onto here.");
			return;
		}
		if (f.door && f.door.nailer)
		{
			bool secret = f.args[0] == SECRET_HOME;
			if (f.door.nailer == f.door && secret && secretOutBuilt) Say("This is a secret way out now.");
			else if (f.door.nailer == f.door) Say(wayOutBuilt && f.args[1] && !secret ? "This is the way out now." : "This doorway is part of the building.\nIt is not yours to take.");
			else Say("The " .. f.door.Label() .. " door is nailed to its frame.\nSomeone with a hammer did that.");
			return;
		}
		if (ClockedRefuses(f)) return;        // a frame with no other time; one that is the clocked door's at either time (then.zs)
		Actor line = ChainRoom();
		if (carried && f.args[4] == 2 && line && carried.args[0] == line.args[3])
		{
			// the third door of a longer chain, in its own room's frame: the
			// room would open onto itself, and once left by its way out on
			// foot nothing would open onto it again
			Say("The " .. carried.Label() .. " door opens onto this very room.\nHung here it would lead nowhere.");
			return;
		}
		if (carried && f.args[4] == 3 && !(carried.IsPair() && carried.args[1] == f.args[1]))
		{
			// MAP12's booth: a frame for a leaf of one Pair (args[1] its colour)
			Say("This frame takes a " .. (f.args[1] == 8 ? "TEAL" : "ORANGE") .. " leaf\nand no other door.");
			return;
		}
		if (carried && f.args[4] == 4 && !carried.IsPair() && carried.args[1] == f.args[1])
		{
			// MAP11's archive: a frame that one door is kept out of; MAP17's night room, whose
			// brass frame does not take the door whose far side faces it (ajarmap.way_home(barred=))
			if (f.args[0] == 190) Say("The way out will not open onto itself here.\nIt has to come round the line.");
			else Say("This frame is barred to the " .. carried.Label() .. " door.\nAny other will hang in it.");
			return;
		}
		if (carried && (f.args[4] == 1 || f.args[4] == 5) && FarAt(carried, f) != f.args[1])     // (its far side at f's time: then.zs)
		{
			if (PlateFor(f) || f.args[4] == 5 || f.args[3])
			{
				// a sprung frame that takes one door (shut.zs), a plain one (MAP32), a brass one of a chain
				string which = "one";
				let di = ThinkerIterator.Create("AjarDoor");
				AjarDoor o;
				while (o = AjarDoor(di.Next())) if (!o.IsPair() && o.args[0] == f.args[1]) which = "the " .. o.Label();
				Say("This frame takes " .. which .. " door\nand no other.");
			}
			else Say("The brass frame takes one door only:\nthe one that opens onto this room.");
			return;
		}
		if (f.door && !carried)
		{
			carried = Unhang(f);
			PlayTake(user);
			if (carried.IsClocked()) Say("You take down the clocked door.\nNow and then, the frame is empty.");
			else if (carried.IsPair()) Say("You unhinge a leaf of the " .. carried.Label() .. " pair.");
			else Say("You unhinge the " .. carried.Label() .. " door.");
		}
		else if (!f.door && carried)
		{
			Hang(carried, f);
			PlaySet(user);
			SayHung(carried, null);
			carried = null;
		}
		else if (f.door && carried)
		{
			AjarDoor old = Unhang(f);
			Hang(carried, f);
			PlaySwap(user);
			SayHung(carried, old);
			carried = old;
		}
		else
		{
			Say("An empty frame. It wants a door.");
		}
	}

	void TakeLeaning(AjarDoor d, Actor user)
	{
		if (carried)
		{
			Say("You can only carry one door.");
			return;
		}
		d.carried = true;
		d.Hide();
		carried = d;
		PlayTake(user);
		if (d.args[3] == 2) { d.args[3] = 0; Say("Your hands find the " .. d.Label() .. " door\nthat only the glass showed."); }
		else if (d.IsStray()) Say("A STRAY door: it has forgotten where it belongs.\nHang it and it opens onto somewhere, once, for a few seconds.");
		else if (d.IsClocked()) Say("The clocked door. Hung in a frame, it opens\nonto the same frame at the other time.");
		else if (d.IsPair()) Say("A leaf of the " .. d.Label() .. " pair: it opens onto its twin,\nwherever that hangs.");
		else Say("You pick up the " .. d.Label() .. " door.");
	}


	// --- events ----------------------------------------------------------
	override void WorldLoaded(WorldEvent e)
	{
		if (e.IsSaveGame) return;
		shutterLeft = -1;
		// the longer loop of a chain (see LoopLen) is one of the level's secrets
		Actor line = ChainRoom();
		if (line && line.args[2]) level.total_secrets++;

		// "+set ajar_only N" leaves one kind of Ajar's own monsters in a map.
		int only = CVar.GetCVar("ajar_only").GetInt();
		if (only)
		{
			static const string kinds[] = { "", "AjarThief", "AjarNailer", "AjarLodger" };
			let ei = ThinkerIterator.Create("AjarEnemy");
			Actor a;
			while (a = Actor(ei.Next()))
				if (a.GetClassName() != kinds[clamp(only, 0, 3)]) a.Destroy();
		}

		// Monsters would walk into the scripted smoke tests. (In a real level
		// mode 2 is a tour of it as it is played, so it keeps them.)
		int autotest = CVar.GetCVar("ajar_autotest").GetInt();
		// (MAP33's tests play its fights in every mode: map33.zs; the kennel lab's and MAP23's tests clear what they do not use)
		if (autotest && !(!(level.mapname ~== "TEST") && autotest >= 2) && !(level.mapname ~== "MAP33") && !(level.mapname ~== "KENNEL") && !(level.mapname ~== "MAP23"))
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next()))
				if (a.bIsMonster) a.Destroy();
		}

		// Every portal line is authored with a valid dummy target so the
		// engine creates it; start from "all frames empty".
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next())) Link(f.args[0], 0, FRAME_TEX);
		for (int id = STRAY_ID; id < STRAY_ID + STRAY_PLACES; id++) Link(id, 0, "AJDR7");

		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			// the clocked door's other leaf: hung with it (Hang), never by itself
			if (d.IsShadow()) { if (!d.frame) { d.carried = true; d.Hide(); } continue; }
			Link(d.args[0], 0, d.BackTex());
			Link(ThenFar(d), 0, d.BackTex());      // its far side's copy THEN, on a map with two times (then.zs)
			f = null;
			if (d.args[2]) f = FindFrame(d.args[2]);
			if (f && d.args[3]) d.nailer = d;
			if (f) Hang(d, f);
			else d.Show();
		}

		UnseenInit();

		// a thief may start with a door on its back (its args[0]: the colour)
		let ti = ThinkerIterator.Create("AjarThief");
		AjarThief th;
		while (th = AjarThief(ti.Next()))
		{
			d = th.args[0] && th.health > 0 ? DoorOf(th.args[0]) : null;
			if (!d || d.frame) continue;
			d.carried = true;
			d.Hide();
			th.loot = d;
		}
	}

	// A squeeze is a hole too small for a door: its line stops the player
	// while they carry one. (Monsters it always stops, by its own flag.)
	int squeezeSaid;
	void Squeeze(Actor mo)
	{
		let it = level.CreateLineIdIterator(SQUEEZE_ID);
		int i;
		while ((i = it.Next()) >= 0)
		{
			Line l = level.lines[i];
			if (!carried) { l.flags &= ~Line.ML_BLOCK_PLAYERS; continue; }
			l.flags |= Line.ML_BLOCK_PLAYERS;
			if (mo.BlockingLine != l || level.time - squeezeSaid < 105) continue;
			if ((mo.pos.xy - (l.v1.p + l.v2.p) / 2).Length() > 56) continue;
			squeezeSaid = level.time;
			Say("The " .. carried.Label() .. " door will not go through here.\nYou would have to leave it behind.");
		}
	}

	override void PlayerSpawned(PlayerEvent e)
	{
		let mo = players[e.PlayerNumber].mo;
		if (!mo || gamestate == GS_TITLELEVEL) return;      // the title's cell (title.zs) says nothing
		// a level with no door to carry (MAP31) says what it has instead
		if (ThinkerIterator.Create("AjarDoor").Next()) Say("USE a door to take it with you.\nUSE an empty frame to hang it there.\nA door always opens onto its own far side.");
		else if (ThinkerIterator.Create("AjarZone").Next()) Say("Three halls, three fights.\nA door with a clock on it leads out of a fight: to before it began.");
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		// ordinary monsters learn about doors (see AjarSense)
		let t = e.thing;
		if (t && t.bIsMonster && t.SeeState && !(t is "AjarEnemy")) t.GiveInventoryType("AjarSense");
		// anything fired may come back through a door at whoever fired it
		if (t && t.bMissile)
		{
			let w = new("AjarShotWatch");
			w.shot = t;
		}
	}

	// --- headless smoke tests (ajar_autotest 1 or 2, see tools/smoke.sh) ----
	override void WorldUnloaded(WorldEvent e)
	{
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode) Check("levelExited", true);
		if (mode == 3 && level.mapname ~== "MAP15") Check("outBySecretWayOut", e.NextMap ~== "MAP32");
		// MAP32's walk-through ends with the level: MAP16 after it is not tested (its own mode 3 is another test)
		if (mode == 3 && level.mapname ~== "MAP32") CVar.FindCVar("ajar_autotest").SetInt(0);
		// MAP17's, MAP18's and MAP19's tests end with the level: the next map must not take the test up
		if (level.mapname ~== "MAP17" || level.mapname ~== "MAP18" || level.mapname ~== "MAP19" || level.mapname ~== "MAP20" || level.mapname ~== "MAP21" || level.mapname ~== "MAP22" || level.mapname ~== "MAP23") CVar.FindCVar("ajar_autotest").SetInt(0);
	}

	// --- shooting yourself through a door ---------------------------------
	// The engine never lets a shot hit whoever fired it, so a player who can
	// see their own back through a door could not shoot it. Bullets: when
	// the player's gun uses ammo, the same shot is traced again here, and if
	// it went through a door and then through the player, it hurts them.
	// Projectiles: see AjarShotWatch.
	Weapon lastWeapon;
	int lastAmmo;

	// Would a bullet fired by mo at this angle and pitch come back through a
	// door and hit mo? Also returns where.
	bool, Vector3 SelfShot(PlayerPawn mo, double ang, double pitch)
	{
		FLineTraceData d;
		double oz = mo.height * 0.5 - mo.floorclip + mo.AttackZOffset * mo.player.crouchFactor;
		mo.LineTrace(ang, 8192, pitch, 0, oz, 0, 0, d);
		if (d.NumPortals == 0) return false, (0, 0, 0);
		// Walk back from where the shot ended towards the door it came out of.
		Vector3 back = -d.HitDir;
		double len2 = back.xy dot back.xy;
		if (len2 < 0.0001) return false, (0, 0, 0);
		double s = ((mo.pos.xy - d.HitLocation.xy) dot back.xy) / len2;     // nearest to the player
		if (s <= 0) return false, (0, 0, 0);
		// ...but no further back than that door.
		double exit = 1e9;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			if (!f.door) continue;
			for (int k = 0; k < 2; k++)
			{
				Line l = FindLine(k ? f.door.args[0] : f.args[0]);
				if (!l) continue;
				Vector2 ao = l.v1.p - d.HitLocation.xy;
				double det = back.x * l.delta.y - back.y * l.delta.x;
				if (abs(det) < 0.0001) continue;
				double sl = (ao.x * l.delta.y - ao.y * l.delta.x) / det;
				double u = (ao.x * back.y - ao.y * back.x) / det;
				if (sl > 0 && u >= 0 && u <= 1 && sl < exit) exit = sl;
			}
		}
		if (s >= exit) return false, (0, 0, 0);
		Vector3 at = d.HitLocation + back * s;
		if ((at.xy - mo.pos.xy).Length() > mo.radius) return false, (0, 0, 0);
		if (at.z < mo.pos.z || at.z > mo.pos.z + mo.height) return false, (0, 0, 0);
		return true, at;
	}

	void SelfShots()
	{
		let mo = players[consoleplayer].mo;
		if (!mo || mo.health <= 0) return;
		let w = mo.player.ReadyWeapon;
		int ammo = (w && w.Ammo1) ? w.Ammo1.amount : 0;
		bool fired = w && w == lastWeapon && ammo < lastAmmo;
		lastWeapon = w;
		lastAmmo = ammo;
		if (!fired) return;

		// Doom's bullet weapons: pellets, spread sideways and up/down.
		int pellets = 0;
		double sh = 0, sv = 0;
		if (w is "SuperShotgun") { pellets = 20; sh = 11.2; sv = 7.1; }
		else if (w is "Shotgun") { pellets = 7; sh = 5.6; }
		else if (w is "Pistol" || w is "Chaingun") { pellets = 1; sh = mo.player.refire ? 5.6 : 0; }
		if (!pellets) return;

		double pitch = mo.BulletSlope();
		int damage = 0;
		for (int i = 0; i < pellets; i++)
		{
			bool hit;
			Vector3 at;
			[hit, at] = SelfShot(mo, mo.angle + sh * Random2[AjarSelf]() / 255., pitch + sv * Random2[AjarSelf]() / 255.);
			if (!hit) continue;
			damage += 5 * random[AjarSelf](1, 3);
			Actor.Spawn("Blood", at, ALLOW_REPLACE);
		}
		if (damage) mo.DamageMobj(null, mo, damage, 'Hitscan');
	}

	// When the player goes through a door, the monsters that were after them
	// and can see that door go after them through it (AjarSense.Follow). A
	// step far longer than a walk is a door: the one that was nearest.
	Vector3 playerWas;
	bool playerWasSet;
	void Followers(Actor mo)
	{
		Vector3 was = playerWas;
		bool moved = playerWasSet && (mo.pos.xy - was.xy).Length() > 96;
		playerWas = mo.pos;
		playerWasSet = true;
		if (!moved) return;
		Line through;
		double best = 48;
		let fi = ThinkerIterator.Create("AjarFrame");
		AjarFrame f;
		while (f = AjarFrame(fi.Next()))
		{
			if (!f.door) continue;
			for (int k = 0; k < 2; k++)
			{
				Line l = FindLine(k ? f.door.args[0] : f.args[0]);
				if (!l) continue;
				// distance from where the player was to the opening
				Vector2 w = was.xy - l.v1.p;
				double u = clamp((w dot l.delta) / (l.delta dot l.delta), 0, 1);
				double d = (w - l.delta * u).Length();
				if (d < best) { best = d; through = l; }
			}
		}
		if (!through) return;
		let si = ThinkerIterator.Create("AjarSense");
		AjarSense s;
		while (s = AjarSense(si.Next())) s.Follow(through, mo);
	}

	override void WorldTick()
	{
		SwapTick();
		SelfShots();
		StrayTick();
		ShutterTick();
		let mo = players[consoleplayer].mo;
		if (mo) ChainTick(mo);
		BoardTick();
		if (mo && mo.health > 0) AmbushTick(mo);
		if (mo) Squeeze(mo);
		if (mo && mo.health > 0) Followers(mo);
		LiftTick();
		OpticsTick(mo);
		UnseenTick();
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (!mode || !mo) return;
		int t = testTic++;
		if (t % 35 == 0)       // (MAP32's played demonstration, mode 20, is watched: not on the screen)
			Console.PrintfEx(mode == 20 ? PRINT_HIGH | PRINT_NONOTIFY : PRINT_HIGH, "AJARTEST t=%d pos=(%d,%d,%d) carried=%s", t, mo.pos.x, mo.pos.y, mo.pos.z, carried ? carried.Label() : "-");
		if (level.mapname ~== "ENG") return;       // the engine tests have their own handler (engtest.zs)
		if (AjarDoomLab.Lab()) return;             // and the Doom door lab, in Doom II's own MAP22 (doomlab.zs)
		if (level.mapname ~== "ONESIDE") return;   // so has the one-sided doorway lab (oneside.zs)
		if (level.mapname ~== "PASS") return;      // and the pass lab (passtest.zs)
		if (level.mapname ~== "MAP19") return;     // and MAP19 (map19.zs, PaperTest)
		if (level.mapname ~== "MAP20") return;     // and MAP20 (map20.zs, HighWaterTest)
		if (level.mapname ~== "SOUND") return;     // and the sound lab (soundlab.zs)
		if (level.mapname ~== "WATER") return;     // and the water lab (watertest.zs)
		if (level.mapname ~== "LEFT") return;      // and the left-handed room lab (lefthand.zs)
		if (level.mapname ~== "MAP33") return;     // and MAP33 (map33.zs, from third.zs's tic)
		if (level.mapname ~== "LAST") return;      // and the last fight lab (lasttest.zs, from third.zs's tic)
		if (level.mapname ~== "YARD") return;      // and the yard lab (yardtest.zs, from third.zs's tic)
		if (level.mapname ~== "THEN") return;      // and the then and now lab (thentest.zs)
		if (level.mapname.Left(7) ~== "CLASSIC") return;     // and the joined maps lab (classic.zs)
		if (level.mapname ~== "MAP21") return;     // and MAP21 (map21.zs, LongRunTest)
		if (level.mapname ~== "MAP22") return;     // and MAP22 (map22.zs, DayReturnTest)
		if (level.mapname ~== "KENNEL") return;    // and the kennel lab (kenneltest.zs)
		if (level.mapname ~== "MAP23") return;     // and MAP23 (map23.zs, SleepingDogsTest)
		if (level.mapname ~== "LAB" && mode == 2) LabThiefScript(mo, t);
		else if (level.mapname ~== "LAB" && mode == 3) LabNailerScript(mo, t);
		else if (level.mapname ~== "LAB" && mode == 4) LabReachScript(mo, t);      // the reach survey (reachtest.zs)
		else if (level.mapname ~== "LAB") LabScript(mo, t);
		else if (level.mapname ~== "OPT") OpticsScript(mo, t, mode);
		else if (level.mapname ~== "MIR") GlassScript(mo, t, mode);
		else if (level.mapname ~== "LIFT" && mode == 2) LiftCompanyScript(mo, t);
		else if (level.mapname ~== "LIFT") LiftScript(mo, t);
		else if (level.mapname ~== "BELT") BeltScript(mo, t, mode);
		else if (level.mapname ~== "CLOCK") ClockScript(mo, t, mode);       // the clock lab (clock.zs)
		else if (level.mapname ~== "MAP11" && mode == 1) ByAppointmentScript(mo, t);
		else if (level.mapname ~== "MAP12" && mode == 1) GoingUpScript(mo, t);
		else if (level.mapname ~== "MAP12" && mode == 2) StoreHoleScript(mo, t);
		else if (level.mapname ~== "MAP13" && mode == 1) SightUnseenScript(mo, t);
		else if (level.mapname ~== "MAP14" && mode == 1) OnTheLevelScript(mo, t);
		else if (level.mapname ~== "MAP15" && mode == 1) OnReflectionScript(mo, t);
		else if (level.mapname ~== "MAP15" && mode == 3) OnReflectionSecret(mo, t);
		else if (level.mapname ~== "MAP16" && mode == 1) WatchYourStepScript(mo, t);
		else if (level.mapname ~== "MAP16" && mode == 3) WatchYourStepCompany(mo, t);
		else if (level.mapname ~== "TEST") TestLevelScript(mo, t, mode);
		else if (level.mapname ~== "MAP04" && mode == 3) DisposalScript(mo, t);
		else if (level.mapname ~== "MAP04" && mode != 2) PartyWallScript(mo, t);
		else if (level.mapname ~== "MAP09" && mode == 3) ChainScript(mo, t);
		else if (level.mapname ~== "MAP10" && mode == 3) LongWayScript(mo, t);
		else if (level.mapname ~== "MAP17") MadeToOrderScript(mo, t, mode);
		else if (level.mapname ~== "MAP18") TimeAndMotionScript(mo, t, mode);     // map18.zs
		else if (level.mapname ~== "MAP32") return;        // its views are map32.zs's (Views32)
		else if (!(level.mapname ~== "MAP01") && mode == 2) Tour(mo, t);
		else if (level.mapname ~== "MAP02" && mode == 3) LodgerPortrait(mo, t);
		else if (level.mapname ~== "MAP05" && mode == 3) LostPropertyStrays(mo, t);
		else if (level.mapname ~== "MAP05") LostPropertyScript(mo, t);
		else if (level.mapname ~== "MAP06") AfterHoursScript(mo, t);
		else if (level.mapname ~== "MAP07") SmallHoursScript(mo, t);
		else if (level.mapname ~== "MAP08") ClosingTimeScript(mo, t);
		else if (level.mapname ~== "MAP09") PuttingThroughScript(mo, t);
		else if (level.mapname ~== "MAP02") NoVacancyScript(mo, t);
		else if (level.mapname ~== "MAP03") StageDoorScript(mo, t);
		else if (level.mapname ~== "MAP01" && mode == 2) BorrowedRoomsTour(mo, t);
		else if (level.mapname ~== "MAP01" && mode == 3) BorrowedRoomsShoot(mo, t);
		else if (level.mapname ~== "MAP01" && mode == 4) BorrowedRoomsSelf(PlayerPawn(mo), t);
		else if (level.mapname ~== "MAP01" && mode == 5) BorrowedRoomsPit(PlayerPawn(mo), t);
		else if (level.mapname ~== "MAP01") BorrowedRoomsScript(mo, t);
	}

	// MAP02: the shortest solution as printed by tools/build.py. Keys are
	// picked up by walking over them and locked doors are tried with USE.
	bool Has(Actor mo, int key) { return mo.FindInventory(String.Format("AjarKey%d", key)) != null; }
	bool RoomOpen(int lineId) { Line l = FindLine(lineId); return l && l.backsector.CenterCeiling() > l.backsector.CenterFloor() + 40; }

	// MODE=3 on MAP02: the lodger posed in the kitchen for the look board
	// (tools/lodger_shots.sh). Five poses of 60 tics: in the frame, stepping
	// out, walking, striking, dead. ajar_lodger_look 0 photographs the lodger
	// as it is (9: the same, turned aside). The rest are the looks that lost.
	// 1..6, the second round: the shadow of one of Doom's monsters (1
	// revenant, 2 arch-vile, 3 zombie, 4 imp, 5 revenant seen through, 6
	// revenant shimmering). 7 is the smoke figure, drawn four times as fine,
	// and 8 a first-round look (build with AJAR_LODGER=7, or 1..6 for 8).
	AjarLodger sitter;

	void LodgerPortrait(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		Pose(mo, -1664, 650, 0, 90);
		if (t == 5)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (a is "AjarLodger") sitter = AjarLodger(a);
				else if (a.bIsMonster && a.Distance2D(mo) < 600) a.Destroy();
			}
		}
		if (!sitter || t < 240 || t % 60) return;     // after the level's opening message
		static const double ys[] = { 846, 818, 772, 744, 762 };
		static const int frames[] = {
			5, 6, 0, 3, 4,          // AJLG: F G A D E
			0, 1, 2, 7, 16,         // SKEL: walking, the punch, the bones
			0, 1, 2, 13, 25,        // VILE: walking, arms up, dead
			0, 1, 2, 5, 11,         // POSS
			0, 1, 2, 6, 12          // TROO
		};
		static const string sprites[] = { "SKEL", "SKEL", "VILE", "POSS", "TROO", "SKEL", "SKEL", "AJLG", "AJLG", "SKEL" };
		int look = clamp(CVar.GetCVar("ajar_lodger_look").GetInt(), 0, 9);
		int set = look >= 7 && look <= 8 ? 0 : look >= 5 || !look ? 1 : look;
		bool real = look == 0 || look == 9;
		int i = t / 60 - 4;
		if (i > 4) return;
		sitter.inside = false;
		sitter.noEyes = !real;
		sitter.bInvisible = false;
		sitter.SetStateLabel("Prowl");                   // takes a step and turns to the player
		sitter.SetOrigin((-1664, ys[i], 0), false);
		sitter.angle = look == 9 ? 345 : 270;
		sitter.sprite = Actor.GetSpriteIndex(sprites[look]);
		sitter.frame = frames[set * 5 + i];
		sitter.tics = -1;
		if (real) sitter.alpha = i == 0 ? 0.2 : i == 1 ? 0.4 : AjarLodger.SHADE;
		else if (look >= 1 && look <= 6)
		{
			double a = i == 0 ? 0.5 : i == 1 ? 0.8 : 1.0;
			if (look == 5) a *= 0.6;
			sitter.A_SetRenderStyle(a, look == 6 ? STYLE_Fuzzy : a < 1 ? STYLE_TranslucentStencil : STYLE_Stencil);
			sitter.SetShade(0x0A090E);
		}
		else
		{
			if (look == 7) sitter.scale = (0.25, 0.25);
			sitter.A_SetRenderStyle(1.0, STYLE_Translucent);
		}
		if (i < 2) sitter.A_AttachLight('knock', DynamicLight.PointLight, 0xD8FFD0, 64, 64, 0, (0, 0, 48));
		else sitter.A_RemoveLight('knock');
	}

	void NoVacancyScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		// the three locked rooms refuse to open without their keys
		if (t == 20) for (int id = 301; id <= 303; id++) FindLine(id).Activate(mo, 0, SPAC_Use);
		if (t == 34) Check("lockedWithoutKeys", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303));
		// room 104's RED into the lobby frame, and through it upstairs
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 256, 80, 0, 270); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("upstairs", mo.pos.z == 144 && mo.pos.x > 512);
		// room 204's YELLOW into the upstairs frame, through to the attic
		if (t == 85) { Take(mo, 4); FindFrame(102).Activate(mo); Pose(mo, 1024, 230, 144, 270); }
		Forward(mo, t, 90, 25);
		if (t == 125) Check("inAttic", mo.pos.z == 304 && mo.pos.x > 1792);
		// key 1, then off the edge into the upstairs hall
		if (t == 130) Pose(mo, 2100, 180, 304, 270);
		Forward(mo, t, 135, 12);
		if (t == 155) Check("haveKey1", Has(mo, 1));
		if (t == 160) Pose(mo, 1830, 224, 304, 180);
		Forward(mo, t, 165, 15);
		if (t == 215) Check("droppedUpstairs", mo.pos.z == 144 && mo.pos.x < 1792);
		// key 4 in the bathroom of 201, then down the missing stairs into the lobby
		if (t == 220) Pose(mo, 1040, 420, 144, 90);
		Forward(mo, t, 225, 12);
		if (t == 245) Check("haveKey4", Has(mo, 4));
		if (t == 250) Pose(mo, 560, 224, 144, 180);
		Forward(mo, t, 255, 15);
		if (t == 300) Check("inLobby", mo.pos.z == 0 && mo.pos.x < 512);
		// keys 1 and 4 open rooms 106 and 105, but 203 still wants keys 2 and 3
		if (t == 305) { Pose(mo, -1120, 200, 0, 270); for (int id = 301; id <= 303; id++) FindLine(id).Activate(mo, 0, SPAC_Use); }
		if (t == 345) Check("rooms105And106Open", RoomOpen(301) && RoomOpen(303) && !RoomOpen(302));
		// key 3 lies in the bath of suite 105
		if (t == 350) Pose(mo, -1328, 450, 0, 90);
		Forward(mo, t, 355, 12);
		if (t == 380) Check("haveKey3", Has(mo, 3));
		t -= 40;                                    // the rest is timed as before that detour
		// BLUE into the kitchen frame, through to the cellar, key 2, and back
		if (t == 350) { Take(mo, 2); FindFrame(105).Activate(mo); Pose(mo, -1664, 770, 0, 90); }
		Forward(mo, t, 360, 25);
		if (t == 400) Check("inCellar", mo.pos.x > 4200 && mo.pos.x < 4520);
		if (t == 405) Pose(mo, 4360, 60, 0, 0);
		Forward(mo, t, 410, 12);
		if (t == 430) Check("haveKey2", Has(mo, 2));
		if (t == 435) Pose(mo, 4300, 160, 0, 180);
		Forward(mo, t, 440, 25);
		if (t == 475) Check("backInKitchen", mo.pos.x < -1408 && mo.pos.y > 528);
		// upstairs again through RED; keys 2 and 3 open room 203: GREEN
		if (t == 480) Pose(mo, 256, 80, 0, 270);
		Forward(mo, t, 485, 25);
		if (t == 520) Check("upstairsAgain", mo.pos.z == 144 && mo.pos.x > 512);
		if (t == 525) { Pose(mo, 1344, 240, 144, 90); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 565) Check("room203Opens", RoomOpen(302));
		if (t == 570) { Take(mo, 3); Pose(mo, 560, 224, 144, 180); }
		Forward(mo, t, 580, 15);
		if (t == 625) Check("inLobbyWithGreen", mo.pos.z == 0 && mo.pos.x < 512 && have == "GREEN");
		// the only empty frame left is in the cellar: GREEN goes there
		if (t == 630) Pose(mo, -1664, 770, 0, 90);
		Forward(mo, t, 635, 25);
		if (t == 670) Check("inCellarWithGreen", mo.pos.x > 4200 && mo.pos.x < 4520 && have == "GREEN");
		if (t == 675) { FindFrame(104).Activate(mo); Pose(mo, 4440, 160, 0, 0); }
		Forward(mo, t, 680, 25);
		if (t == 715) Check("onTerraceEmptyHanded", mo.pos.z == 128 && mo.pos.x > 3000 && mo.pos.x < 3256 && have == "-");
		// off the terrace into the garden, through the stone doorway to the balcony
		if (t == 720) Pose(mo, 3200, 224, 128, 0);
		Forward(mo, t, 725, 15);
		if (t == 775) Check("inGarden", mo.pos.z == 0 && mo.pos.x > 3256);
		if (t == 780) Pose(mo, 3830, 224, 0, 0);
		Forward(mo, t, 785, 20);
		if (t == 820) Check("onBalcony", mo.pos.z == 112 && mo.pos.y > 448 && mo.pos.x < 512);
		// the doorway is not a door to take; VIOLET is, and goes down through the gap in the rail
		if (t == 822) { FindFrame(151).Activate(mo); Check("doorwayStays", !carried && FindFrame(151).door); }
		if (t == 825) { Take(mo, 5); Pose(mo, 256, 500, 112, 270); }
		Forward(mo, t, 835, 15);
		if (t == 880) Check("inLobbyWithViolet", mo.pos.z == 0 && mo.pos.y < 448 && have == "VIOLET");
		// swap RED for VIOLET in the lobby frame and leave
		if (t == 885) { FindFrame(101).Activate(mo); Pose(mo, 256, 80, 0, 270); }
		Forward(mo, t, 890, 25);
		if (t == 925) Check("inExitRoom", mo.pos.x > 4900);
		// the way out is walked into
		if (t == 930) Pose(mo, 5290, 128, 0, 0);
		Forward(mo, t, 960, 10);
	}

	// MAP03: a solution of the same length as the one tools/build.py prints.
	// Bolts are drawn by walking over their lines, as a player would.
	bool Sunk(int lineId) { Line l = FindLine(lineId); return l && l.frontsector.CenterFloor() < 0 && l.backsector.CenterFloor() < 0; }

	void StageDoorScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		// office and star's room are locked; stairs, grate and booth are bolted
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 34) Check("lockedAndBolted", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303) && !RoomOpen(305) && !Sunk(304));
		// the bar's BLUE into the foyer frame: the dress circle
		if (t == 35) { Take(mo, 2); FindFrame(101).Activate(mo); Pose(mo, -224, 1104, 0, 270); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("onCircle", mo.pos.z == 128 && mo.pos.y < 1088 && mo.pos.x > 320);
		if (t == 85) Pose(mo, 990, 980, 128, 90);
		Forward(mo, t, 90, 12);
		if (t == 110) Check("haveKey2AndStairsOpen", Has(mo, 2) && RoomOpen(303));
		// over the rail into the stalls
		if (t == 115) Pose(mo, 664, 930, 128, 270);
		Forward(mo, t, 120, 15);
		if (t == 170) Check("inStalls", mo.pos.z == 0 && mo.pos.y < 896);
		// the cloakroom's VIOLET into the stalls frame: under the stage
		if (t == 175) { Take(mo, 5); FindFrame(104).Activate(mo); Pose(mo, 256, 820, 0, 90); }
		Forward(mo, t, 180, 25);
		if (t == 220) Check("underTheStage", mo.pos.z == -64 && mo.pos.x > 1168 && mo.pos.x < 1424);
		// GREEN into the frame down here: the flies. The grate has sunk
		if (t == 225) { Take(mo, 3); FindFrame(102).Activate(mo); Pose(mo, 1232, 800, -64, 90); }
		Forward(mo, t, 230, 25);
		if (t == 270) Check("onFliesAndGrateSunk", mo.pos.z == 288 && mo.pos.y < 0 && Sunk(304));
		// along the bridge, down into the gods, and through YELLOW's far side
		if (t == 275) Pose(mo, -200, 60, 288, 90);
		Forward(mo, t, 280, 15);
		if (t == 320) Check("inTheGods", mo.pos.z == 224 && mo.pos.x < 0 && mo.pos.y > 128);
		if (t == 325) Pose(mo, -224, 700, 224, 90);
		Forward(mo, t, 330, 25);
		if (t == 370) Check("inBooth", mo.pos.x < -464 && mo.pos.x > -720 && mo.pos.z == 224);
		if (t == 375) Pose(mo, -560, 460, 224, 90);
		Forward(mo, t, 380, 12);
		if (t == 400) Check("haveKey3AndBoothOpen", Has(mo, 3) && RoomOpen(305));
		// over the gods' rail, through the sunk grate and up to the flies again
		if (t == 405) Pose(mo, -100, 448, 224, 0);
		Forward(mo, t, 410, 15);
		if (t == 455) Check("inStallsAgain", mo.pos.z == 0 && mo.pos.x > 0);
		if (t == 460) Pose(mo, 1100, 768, -48, 0);
		Forward(mo, t, 465, 15);
		if (t == 485) Check("throughTheGrate", mo.pos.z == -64 && mo.pos.x > 1168);
		if (t == 490) Pose(mo, 1232, 800, -64, 90);
		Forward(mo, t, 495, 25);
		if (t == 530) Check("onFliesAgain", mo.pos.z == 288 && mo.pos.y < 0);
		// this time down onto the stage: keys 2 and 3 open the star's room
		if (t == 535) Pose(mo, 1472, -60, 288, 90);
		Forward(mo, t, 540, 15);
		if (t == 585) Check("onStage", mo.pos.z == 64 && mo.pos.y > 0);
		if (t == 590) FindLine(302).Activate(mo, 0, SPAC_Use);
		if (t == 630) Check("starsRoomOpens", RoomOpen(302) && !RoomOpen(301));
		// RED with empty hands, into the room under the stage, and out
		if (t == 635) { Take(mo, 1); Pose(mo, 1300, 600, 64, 90); }
		Forward(mo, t, 640, 15);
		if (t == 685) Check("underWithRed", mo.pos.z == -64 && have == "RED");
		if (t == 690) { FindFrame(102).Activate(mo); Pose(mo, 1232, 800, -64, 90); }
		Forward(mo, t, 695, 25);
		if (t == 735) Check("inExitRoom", mo.pos.x > 4900);
		// the way out is walked into
		if (t == 740) Pose(mo, 5290, 128, 0, 0);
		Forward(mo, t, 775, 10);
	}

	// MAP04: a solution of the same length as the one tools/build.py prints
	// (the thief is gone, so BLUE leans where it stood). Keys are walked over,
	// drops are walked off, squeezes are walked through.
	void PartyWallScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 34) Check("lockedAndBolted", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303));
		// BLUE into the passage frame: the balcony, key 1 and GREEN
		if (t == 35) { Take(mo, 2); FindFrame(101).Activate(mo); Pose(mo, 720, -160, 0, 180); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("onBalcony", mo.pos.z == 160 && mo.pos.x < 0);
		if (t == 85) Pose(mo, -200, 300, 160, 90);
		Forward(mo, t, 90, 12);
		if (t == 110) Check("haveKey1", Has(mo, 1));
		// through the gap in the rail with GREEN
		if (t == 112) { Take(mo, 3); Pose(mo, -80, 384, 160, 0); }
		Forward(mo, t, 115, 15);
		if (t == 170) Check("inYardWithGreen", mo.pos.z == 0 && mo.pos.x > 0 && have == "GREEN");
		// GREEN into the north frame: the roof, key 2
		if (t == 175) { FindFrame(102).Activate(mo); Pose(mo, 128, 1072, 0, 90); }
		Forward(mo, t, 180, 25);
		if (t == 220) Check("onRoof", mo.pos.z == 320 && mo.pos.y > 1152);
		if (t == 225) Pose(mo, 1200, 1480, 320, 0);
		Forward(mo, t, 230, 12);
		if (t == 250) Check("haveKey2", Has(mo, 2));
		// into the light well, with empty hands: key 4
		if (t == 255) Pose(mo, 600, 1500, 320, 0);
		Forward(mo, t, 260, 15);
		if (t == 310) Check("inWell", mo.pos.z == -128 && mo.pos.x > 640 && mo.pos.x < 896);
		if (t == 315) Pose(mo, 660, 1400, -128, 0);
		Forward(mo, t, 320, 12);
		if (t == 340) Check("haveKey4", Has(mo, 4));
		// out by the coal hole; that draws the cellar door's bolt
		if (t == 345) Pose(mo, 824, 1500, -128, 90);
		Forward(mo, t, 350, 25);
		if (t == 388) Check("inCellarAndBoltDrawn", mo.pos.y > 1616 && RoomOpen(303));
		// YELLOW does not go back through the hole
		if (t == 390) { Take(mo, 4); Pose(mo, 824, 1680, -128, 270); }
		Forward(mo, t, 395, 25);
		if (t == 430) Check("squeezeRefusesADoor", mo.pos.y > 1536 && have == "YELLOW");
		// up the cellar stairs and out of the door that was bolted
		if (t == 432) Pose(mo, 1472, 1500, -112, 270);
		Forward(mo, t, 433, 45);
		if (t == 482) Check("upTheCellarStairs", mo.pos.z == 0 && mo.pos.y < 1184);
		t -= 50;                                    // the rest is timed as before that walk
		// YELLOW into the frame by the office: the loft
		if (t == 435) { FindFrame(104).Activate(mo); Pose(mo, 1456, 480, 0, 0); }
		Forward(mo, t, 440, 25);
		if (t == 480) Check("inLoft", mo.pos.z == 192 && mo.pos.x > 1536 && mo.pos.y > 544);
		// keys 1 and 2 open the suite: VIOLET, and off the loft with it
		if (t == 485) FindLine(302).Activate(mo, 0, SPAC_Use);
		if (t == 525) Check("suiteOpens", RoomOpen(302) && !RoomOpen(301));
		if (t == 530) { Take(mo, 5); Pose(mo, 1600, 832, 192, 180); }
		Forward(mo, t, 535, 15);
		if (t == 585) Check("inYardWithViolet", mo.pos.z == 0 && mo.pos.x < 1536 && have == "VIOLET");
		// every frame in the yard is taken: over the roof and down the well with it
		if (t == 590) Pose(mo, 128, 1072, 0, 90);
		Forward(mo, t, 595, 25);
		if (t == 635) Check("onRoofWithViolet", mo.pos.z == 320 && have == "VIOLET");
		if (t == 640) Pose(mo, 600, 1500, 320, 0);
		Forward(mo, t, 645, 15);
		if (t == 695) Check("inWellWithViolet", mo.pos.z == -128 && have == "VIOLET");
		// VIOLET into the well's frame: the kennel, key 3
		if (t == 700) { FindFrame(103).Activate(mo); Pose(mo, 688, 1456, -128, 90); }
		Forward(mo, t, 705, 25);
		if (t == 745) Check("inKennel", mo.pos.x < 240 && mo.pos.y > 1616 && mo.pos.z == -64 && have == "-");
		if (t == 750) Pose(mo, -80, 1720, -64, 270);
		Forward(mo, t, 755, 10);
		if (t == 775) Check("haveKey3", Has(mo, 3));
		// out by the hatch, a drop into the cellar
		if (t == 780) Pose(mo, 180, 1672, -64, 0);
		Forward(mo, t, 785, 15);
		if (t == 815) Check("outByTheHatch", mo.pos.z == -128 && mo.pos.x > 256);
		// keys 3 and 4 open the office; through the hole into the strongroom
		if (t == 820) FindLine(301).Activate(mo, 0, SPAC_Use);
		if (t == 860) Check("officeOpens", RoomOpen(301));
		if (t == 865) Pose(mo, 1900, 240, 0, 0);
		Forward(mo, t, 870, 25);
		if (t == 905) Check("inStrongroom", mo.pos.x > 1984 && mo.pos.x < 2240);
		// RED into the frame in here, and out
		if (t == 910) { Take(mo, 1); FindFrame(105).Activate(mo); Pose(mo, 2160, 240, 0, 0); }
		Forward(mo, t, 915, 25);
		if (t == 955) Check("inExitRoom", mo.pos.x > 4900);
		// the way out is walked into
		if (t == 960) Pose(mo, 5290, 128, 0, 0);
		Forward(mo, t, 975, 10);
	}

	// MAP05: a solution of the same length as the one tools/build.py prints.
	// No Stray door is used; the nailer is gone with the other monsters.
	void LostPropertyScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 34) Check("lockedAndBolted", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303) && !RoomOpen(304) && !RoomOpen(305) && !RoomOpen(307));
		// the waiting room's RED into the vestibule frame: the bridge
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 384, 80, 0, 270); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("onBridge", mo.pos.z == 160 && mo.pos.x > 2048 && mo.pos.x < 2240);
		// the signal box: key 1, the lever, GREEN
		if (t == 85) Pose(mo, 2400, 1120, 160, 0);
		Forward(mo, t, 90, 12);
		if (t == 110) Check("haveKey1", Has(mo, 1));
		if (t == 112) { FindLine(306).Activate(mo, 0, SPAC_Use); Take(mo, 3); }
		if (t == 150) Check("leverOpensLampRoom", RoomOpen(307));
		// off the bridge into the yard with it; walking west draws the gate's bolt
		if (t == 152) Pose(mo, 2100, 1920, 160, 180);
		Forward(mo, t, 155, 15);
		if (t == 205) Check("inYardWithGreen", mo.pos.z == 0 && mo.pos.x < 2048 && mo.pos.y > 1680 && have == "GREEN");
		if (t == 210) Pose(mo, 1100, 1760, 0, 180);
		Forward(mo, t, 215, 20);
		if (t == 260) Check("gateUnbolted", RoomOpen(305));
		if (t == 262) Pose(mo, 256, 1720, 0, 270);
		Forward(mo, t, 265, 25);
		if (t == 295) Check("throughTheGate", mo.pos.y < 1600 && mo.pos.x < 512);
		// GREEN into platform 1's frame: the gallery, key 2, and over the rail
		if (t == 300) { FindFrame(102).Activate(mo); Pose(mo, 896, 330, 0, 270); }
		Forward(mo, t, 305, 25);
		if (t == 340) Check("onGallery", mo.pos.z == 192 && mo.pos.x < 0);
		if (t == 345) Pose(mo, -128, 380, 192, 270);
		Forward(mo, t, 350, 12);
		if (t == 370) Check("haveKey2", Has(mo, 2));
		if (t == 375) Pose(mo, -60, 464, 192, 0);
		Forward(mo, t, 380, 15);
		if (t == 430) Check("inConcourse", mo.pos.z == 0 && mo.pos.x > 0);
		// keys 1 and 2 open the lost property office: key 3
		if (t == 435) { Pose(mo, 1088, 330, 0, 270); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 475) Check("lostPropertyOpens", RoomOpen(301) && !RoomOpen(302));
		if (t == 480) Pose(mo, 1060, 200, 0, 180);
		Forward(mo, t, 485, 10);
		if (t == 505) Check("haveKey3", Has(mo, 3));
		// through the turnstile, with empty hands
		if (t == 510) Pose(mo, 440, 1152, 0, 0);
		Forward(mo, t, 515, 20);
		if (t == 545) Check("throughTheTurnstile", mo.pos.x > 528 && mo.pos.y > 1024 && mo.pos.y < 1280);
		// BLUE into platform 2's frame: the parcels office, key 4, and out by its own door
		if (t == 550) { Take(mo, 2); FindFrame(104).Activate(mo); Pose(mo, 1120, 1200, 0, 90); }
		Forward(mo, t, 555, 25);
		if (t == 590) Check("inParcels", mo.pos.x > 752 && mo.pos.x < 1056 && mo.pos.y > 1296);
		if (t == 595) Pose(mo, 900, 1470, 0, 180);
		Forward(mo, t, 600, 15);
		if (t == 620) Check("haveKey4", Has(mo, 4));
		if (t == 625) Pose(mo, 912, 1450, 0, 270);
		Forward(mo, t, 630, 10);
		if (t == 675) Check("parcelsDoorUnbolted", RoomOpen(303));
		if (t == 680) Pose(mo, 912, 1340, 0, 270);
		Forward(mo, t, 685, 20);
		if (t == 710) Check("onPlatform2", mo.pos.z == 0 && mo.pos.y < 1280 && mo.pos.y > 1024);
		// keys 3 and 4 open the station master's office: VIOLET
		if (t == 715) { Pose(mo, 448, 2060, 0, 90); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 755) Check("masterOpens", RoomOpen(302));
		// which does not go through the turnstile
		if (t == 760) { Take(mo, 5); Pose(mo, 440, 1152, 0, 0); }
		Forward(mo, t, 765, 20);
		if (t == 795) Check("turnstileRefusesADoor", mo.pos.x < 512 && have == "VIOLET");
		// so: over the bridge, along the train's roof, down onto platform 2
		if (t == 800) Pose(mo, 384, 80, 0, 270);
		Forward(mo, t, 805, 25);
		if (t == 835) Check("onBridgeWithViolet", mo.pos.z == 160 && have == "VIOLET");
		if (t == 840) Pose(mo, 2100, 912, 160, 180);
		Forward(mo, t, 845, 15);
		if (t == 870) Check("onTheTrain", mo.pos.z == 112 && mo.pos.x < 2048);
		if (t == 875) Pose(mo, 1500, 960, 112, 90);
		Forward(mo, t, 880, 15);
		if (t == 915) Check("onPlatform2WithViolet", mo.pos.z == 0 && mo.pos.y > 1024 && have == "VIOLET");
		// VIOLET for BLUE in the frame here: the night room, whose bolt you draw
		if (t == 920) { FindFrame(104).Activate(mo); Pose(mo, 1120, 1200, 0, 90); }
		Forward(mo, t, 925, 25);
		if (t == 960) Check("inNightRoom", mo.pos.x > 1280 && mo.pos.x < 1600 && mo.pos.y > 1296 && mo.pos.y < 1552 && have == "BLUE");
		if (t == 965) Pose(mo, 1440, 1420, 0, 270);
		Forward(mo, t, 970, 6);
		if (t == 1015) Check("nightDoorUnbolted", RoomOpen(304) && !wayOutBuilt);
		if (t == 1020) Pose(mo, 1440, 1360, 0, 270);
		Forward(mo, t, 1025, 20);
		if (t == 1050) Check("outOntoPlatform2", mo.pos.y < 1280 && mo.pos.y > 1024);
		// BLUE back for VIOLET, in by the door, and VIOLET into the night room's frame
		if (t == 1055) { FindFrame(104).Activate(mo); Pose(mo, 1440, 1200, 0, 90); }
		Forward(mo, t, 1060, 25);
		if (t == 1090) Check("inNightRoomWithViolet", mo.pos.y > 1296 && mo.pos.x > 1280 && mo.pos.x < 1600 && have == "VIOLET");
		if (t == 1095) { FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		// the way out is walked into
		if (t == 1100) Pose(mo, 1400, 1424, 0, 0);
		Forward(mo, t, 1130, 30);
	}

	// MAP06: a solution of the same length as the one tools/build.py prints.
	// No Stray door is used.
	void AfterHoursScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); FindLine(303).Activate(mo, 0, SPAC_Use); FindLine(306).Activate(mo, 0, SPAC_Use); }
		if (t == 34) Check("lockedAndBolted", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303) && !RoomOpen(304) && !RoomOpen(305) && !RoomOpen(306) && !RoomOpen(307));
		// the cloakroom's RED into the lobby's frame: the upper gallery, key 1, and off it into the great hall
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 448, 80, 0, 270); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("onUpperGallery", mo.pos.z == 160 && mo.pos.x > -256 && mo.pos.x < -64);
		if (t == 85) Pose(mo, -160, 2100, 160, 90);
		Forward(mo, t, 90, 15);
		if (t == 110) Check("haveKey1", Has(mo, 1));
		if (t == 115) Pose(mo, -160, 1250, 160, 270);
		Forward(mo, t, 120, 20);
		if (t == 160) Check("droppedIntoGreatHall", mo.pos.z == 0 && mo.pos.y < 1152);
		// the cafe's GREEN into the great hall's frame: the cellar, key 2, and up its stairs
		if (t == 165) { Take(mo, 3); FindFrame(102).Activate(mo); Pose(mo, 576, 1070, 0, 90); }
		Forward(mo, t, 170, 25);
		if (t == 210) Check("inCellar", mo.pos.z == -128 && mo.pos.y < -64);
		if (t == 215) Pose(mo, 1700, -400, -128, 0);
		Forward(mo, t, 220, 15);
		if (t == 240) Check("haveKey2", Has(mo, 2));
		if (t == 245) Pose(mo, 1264, -120, -128, 90);
		Forward(mo, t, 250, 15);
		if (t == 295) Check("cellarDoorUnbolted", RoomOpen(305));
		if (t == 300) Pose(mo, 1264, 100, -128, 90);
		Forward(mo, t, 305, 55);
		if (t == 370) Check("upInCafe", mo.pos.z == 0 && mo.pos.y > 480 && mo.pos.x > 912);
		// key 1 opens the west wing: YELLOW into its frame, the roof, key 3, and off it into the court
		if (t == 375) { Pose(mo, -180, 992, 0, 180); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 415) Check("westWingOpens", RoomOpen(301) && !RoomOpen(303));
		if (t == 420) { Take(mo, 4); FindFrame(103).Activate(mo); Pose(mo, -1120, 1248, 0, 180); }
		Forward(mo, t, 425, 25);
		if (t == 465) Check("onRoof", mo.pos.z == 224 && mo.pos.x > 704 && mo.pos.x < 896);
		if (t == 470) Pose(mo, 800, 2100, 224, 90);
		Forward(mo, t, 475, 15);
		if (t == 495) Check("haveKey3", Has(mo, 3));
		if (t == 500) Pose(mo, 800, 1632, 224, 180);
		Forward(mo, t, 505, 20);
		if (t == 545) Check("inCourt", mo.pos.z == -72 && mo.pos.x < 704);
		// up the steps and past the gatepost onto the terrace, with empty hands; and off it again
		if (t == 550) Pose(mo, 680, 1700, -72, 90);
		Forward(mo, t, 555, 40);
		if (t == 605) Check("upTheStepsToTheTerrace", mo.pos.z == 0 && mo.pos.y > 1984);
		if (t == 610) Pose(mo, 320, 2030, 0, 270);
		Forward(mo, t, 615, 15);
		if (t == 650) Check("backInCourt", mo.pos.z == -72 && mo.pos.y < 1984);
		// key 2 opens the east wing, keys 2 and 3 the archive
		if (t == 655) { Pose(mo, 1136, 900, 0, 90); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 695) Check("eastWingOpens", RoomOpen(302));
		if (t == 700) { Pose(mo, 1200, 1800, 0, 90); FindLine(306).Activate(mo, 0, SPAC_Use); }
		if (t == 740) Check("archiveOpens", RoomOpen(306));
		// VIOLET into the cellar's frame: the mezzanine, key 4, and off it
		if (t == 745) { Take(mo, 5); FindFrame(104).Activate(mo); Pose(mo, 1300, -136, -128, 180); }
		Forward(mo, t, 750, 25);
		if (t == 790) Check("onMezzanine", mo.pos.z == 192 && mo.pos.x < -256);
		if (t == 795) Pose(mo, -384, 600, 192, 270);
		Forward(mo, t, 800, 15);
		if (t == 820) Check("haveKey4", Has(mo, 4));
		if (t == 825) Pose(mo, -360, 752, 192, 0);
		Forward(mo, t, 830, 20);
		if (t == 870) Check("inGreatHall", mo.pos.z <= 16 && mo.pos.x > -256);    // perhaps on a bench
		// keys 3 and 4 open the office: its lever, and the hole into the strongroom
		if (t == 875) { Pose(mo, -624, 1560, 0, 90); FindLine(303).Activate(mo, 0, SPAC_Use); }
		if (t == 915) Check("officeOpens", RoomOpen(303));
		if (t == 920) { Pose(mo, -680, 1840, 0, 180); FindLine(308).Activate(mo, 0, SPAC_Use); }
		if (t == 960) Check("leverOpensGrotto", RoomOpen(307));
		if (t == 965) Pose(mo, -536, 1840, 0, 90);
		Forward(mo, t, 970, 20);
		if (t == 1000) Check("inStrongroom", mo.pos.y > 1920 && mo.pos.y < 2176 && mo.pos.x < -352);
		// BLUE into the strongroom's frame: the night room, whose bolt you draw
		if (t == 1005) { Take(mo, 2); FindFrame(105).Activate(mo); Pose(mo, -536, 2100, 0, 90); }
		Forward(mo, t, 1010, 25);
		if (t == 1050) Check("inNightRoom", mo.pos.x > 160 && mo.pos.x < 480 && mo.pos.y > 2256 && mo.pos.y < 2512 && have == "-");
		if (t == 1055) Pose(mo, 320, 2380, 0, 270);
		Forward(mo, t, 1060, 6);
		if (t == 1105) Check("nightDoorUnbolted", RoomOpen(304) && !wayOutBuilt);
		// back through it, and out by the hole
		if (t == 1110) Pose(mo, 260, 2384, 0, 180);
		Forward(mo, t, 1115, 25);
		if (t == 1150) Check("backInStrongroom", mo.pos.y > 1920 && mo.pos.y < 2176 && mo.pos.x < -352);
		if (t == 1155) Pose(mo, -536, 1990, 0, 270);
		Forward(mo, t, 1160, 20);
		if (t == 1190) Check("outByTheHole", mo.pos.y < 1904 && mo.pos.x < -352);
		// YELLOW down again: it goes neither through the hole nor past the gatepost
		if (t == 1195) { Take(mo, 4); Pose(mo, -536, 1840, 0, 90); }
		Forward(mo, t, 1200, 20);
		if (t == 1230) Check("holeRefusesADoor", mo.pos.y < 1904 && have == "YELLOW");
		if (t == 1235) Pose(mo, 680, 1700, -72, 90);
		Forward(mo, t, 1240, 40);
		if (t == 1290) Check("gatepostRefusesADoor", mo.pos.y < 1984 && have == "YELLOW");
		// so: through RED, off the upper gallery onto the terrace, into the night room by its door
		if (t == 1295) Pose(mo, 448, 80, 0, 270);
		Forward(mo, t, 1300, 25);
		if (t == 1335) Check("onUpperGalleryWithYellow", mo.pos.z == 160 && have == "YELLOW");
		if (t == 1340) Pose(mo, -160, 2112, 160, 0);
		Forward(mo, t, 1345, 20);
		if (t == 1385) Check("onTerraceWithYellow", mo.pos.z == 0 && mo.pos.y > 1984 && mo.pos.y < 2240 && have == "YELLOW");
		if (t == 1390) Pose(mo, 320, 2180, 0, 90);
		Forward(mo, t, 1395, 20);
		if (t == 1425) Check("inNightRoomWithYellow", mo.pos.y > 2256 && mo.pos.x > 160 && mo.pos.x < 480 && have == "YELLOW");
		// through BLUE's far side into the strongroom, and YELLOW for BLUE in its frame
		if (t == 1430) Pose(mo, 260, 2384, 0, 180);
		Forward(mo, t, 1435, 25);
		if (t == 1470) Check("inStrongroomWithYellow", mo.pos.y > 1920 && mo.pos.y < 2176 && mo.pos.x < -352 && have == "YELLOW");
		if (t == 1475) FindFrame(105).Activate(mo);
		if (t == 1478) Check("swappedForBlue", have == "BLUE");
		// out through YELLOW onto the roof, off it onto the terrace, and BLUE into the night room's frame
		if (t == 1480) Pose(mo, -536, 2100, 0, 90);
		Forward(mo, t, 1485, 25);
		if (t == 1520) Check("onRoofWithBlue", mo.pos.z == 224 && have == "BLUE");
		if (t == 1525) Pose(mo, 800, 2112, 224, 180);
		Forward(mo, t, 1530, 20);
		if (t == 1570) Check("onTerraceWithBlue", mo.pos.z == 0 && mo.pos.y > 1984 && mo.pos.y < 2240 && have == "BLUE");
		if (t == 1575) Pose(mo, 320, 2180, 0, 90);
		Forward(mo, t, 1580, 20);
		if (t == 1610) Check("inNightRoomWithBlue", mo.pos.y > 2256 && mo.pos.x > 160 && mo.pos.x < 480 && have == "BLUE");
		if (t == 1615) { FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		// the way out is walked into
		if (t == 1620) Pose(mo, 280, 2384, 0, 0);
		Forward(mo, t, 1650, 30);
	}

	// MAP07: a solution of the same length as the one tools/build.py prints.
	// No Stray door is used.
	void SmallHoursScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); FindLine(303).Activate(mo, 0, SPAC_Use); }
		if (t == 34) Check("lockedAndBolted", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303) && !RoomOpen(304) && !RoomOpen(305) && !RoomOpen(307) && !RoomOpen(311));
		// RED into the frame by the gate: three steps on, inside it, and the gate's bolt is drawn
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 192, -400, 0, 90); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("throughRedPastTheGate", mo.pos.x > -128 && mo.pos.x < 128 && mo.pos.y > -256 && mo.pos.y < 0);
		if (t == 115) Check("gateUnbolted", RoomOpen(311));
		// GREEN into the hall's frame: the stacks, key 1, and off them into the library
		if (t == 120) { Take(mo, 3); FindFrame(105).Activate(mo); Pose(mo, 180, 592, 0, 0); }
		Forward(mo, t, 125, 25);
		if (t == 165) Check("onStacks", mo.pos.z == 160 && mo.pos.x < -800 && mo.pos.x > -992 && mo.pos.y > 528);
		if (t == 170) Pose(mo, -896, 800, 160, 90);
		Forward(mo, t, 175, 12);
		if (t == 195) Check("haveKey1", Has(mo, 1));
		if (t == 200) Pose(mo, -840, 720, 160, 0);
		Forward(mo, t, 205, 20);
		if (t == 240) Check("droppedIntoLibrary", mo.pos.z <= 32 && mo.pos.x > -800 && mo.pos.x < -272);    // perhaps on a table
		// key 1 opens the west wing, off the lane: key 4 in the clock room
		if (t == 245) { Pose(mo, -1120, 832, 0, 180); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 285) Check("westWingOpens", RoomOpen(301));
		if (t == 290) Pose(mo, -1600, 340, 0, 270);
		Forward(mo, t, 295, 12);
		if (t == 315) Check("haveKey4", Has(mo, 4));
		// over the stile onto the hillside, up the steps past the gatepost onto the roof, and into the gallery
		if (t == 320) Pose(mo, -1050, 1824, 0, 0);
		Forward(mo, t, 325, 22);
		if (t == 360) Check("overTheStile", mo.pos.z == 0 && mo.pos.x > -992 && mo.pos.y > 1696 && mo.pos.y < 2000);
		if (t == 365) Pose(mo, -440, 1990, 0, 270);
		Forward(mo, t, 370, 42);
		if (t == 425) Check("upTheStepsToTheRoof", mo.pos.z == 160 && mo.pos.y < 1696);
		if (t == 430) { Pose(mo, -440, 1280, 160, 0); FindLine(306).Activate(mo, 0, SPAC_Use); }
		Forward(mo, t, 470, 20);
		if (t == 500) Check("onGallery", mo.pos.z == 160 && mo.pos.x > -384 && mo.pos.x < -256);
		if (t == 505) Pose(mo, 320, 1190, 160, 270);
		Forward(mo, t, 510, 12);
		if (t == 530) Check("haveKey2", Has(mo, 2));
		if (t == 535) Pose(mo, 300, 1376, 160, 180);
		Forward(mo, t, 540, 14);
		if (t == 570) Check("droppedIntoDome", mo.pos.z == 0 && mo.pos.x > -256 && mo.pos.x < 256);
		// key 2 opens the east wing: key 3 in the cellar
		if (t == 575) { Pose(mo, 200, 720, 0, 0); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 615) Check("eastWingOpens", RoomOpen(302));
		if (t == 620) Pose(mo, 1340, 1730, -128, 270);
		Forward(mo, t, 625, 12);
		if (t == 645) Check("haveKey3", Has(mo, 3));
		// VIOLET into the hillside's frame: across the ravine. Keys 3 and 4 open the transit house; its lever
		if (t == 650) { Take(mo, 5); FindFrame(104).Activate(mo); Pose(mo, 120, 2336, 0, 180); }
		Forward(mo, t, 655, 25);
		if (t == 695) Check("onKnoll", mo.pos.z == 0 && mo.pos.y > 2592 && mo.pos.y < 2944 && have == "-");
		if (t == 700) { Pose(mo, -256, 2900, 0, 90); FindLine(303).Activate(mo, 0, SPAC_Use); }
		if (t == 740) Check("transitHouseOpens", RoomOpen(303));
		if (t == 745) { Pose(mo, -400, 3120, 0, 180); FindLine(308).Activate(mo, 0, SPAC_Use); }
		if (t == 785) Check("leverOpensCave", RoomOpen(307));
		// BLUE down off the knoll, up the ravine's steps, and no further: the stile refuses it
		if (t == 790) { Take(mo, 2); Pose(mo, 0, 2640, 0, 270); }
		Forward(mo, t, 795, 20);
		if (t == 830) Check("inRavineWithBlue", mo.pos.z == -128 && have == "BLUE");
		if (t == 835) Pose(mo, -720, 2432, -128, 180);
		Forward(mo, t, 840, 36);
		if (t == 885) Check("upTheRavineSteps", mo.pos.z == 0 && mo.pos.x < -940);
		if (t == 886) Pose(mo, -960, 2432, 0, 270);
		Forward(mo, t, 890, 10);
		if (t == 910) Check("onHillsideWithBlue", mo.pos.z == 0 && mo.pos.y < 2400 && have == "BLUE");
		if (t == 915) Pose(mo, -940, 1824, 0, 180);
		Forward(mo, t, 920, 20);
		if (t == 950) Check("stileRefusesADoor", mo.pos.x > -992 && have == "BLUE");
		// BLUE for VIOLET in the hillside's frame, and through it: the night room, whose bolt you draw
		if (t == 955) { Pose(mo, 120, 2336, 0, 180); FindFrame(104).Activate(mo); }
		if (t == 958) Check("swappedForViolet", have == "VIOLET");
		Forward(mo, t, 960, 25);
		if (t == 1000) Check("inNightRoomWithViolet", mo.pos.z == 160 && mo.pos.x > -160 && mo.pos.x < 160 && mo.pos.y > 1712 && mo.pos.y < 1968 && have == "VIOLET");
		if (t == 1005) Pose(mo, 0, 1800, 160, 270);
		Forward(mo, t, 1010, 10);
		if (t == 1055) Check("nightDoorUnbolted", RoomOpen(304) && !wayOutBuilt);
		// the ready-made pair in its west wall turns you round
		if (t == 1060) Pose(mo, -100, 1776, 160, 180);
		Forward(mo, t, 1065, 14);
		if (t == 1090) Check("turnedRound", mo.pos.x > -160 && mo.pos.x < 160 && mo.pos.y > 1860 && mo.pos.y < 1950 && abs(Actor.DeltaAngle(mo.angle, 0)) < 1 && !wayOutBuilt);
		// out onto the gallery, down into the dome, and VIOLET into the frame there
		if (t == 1095) Pose(mo, 0, 1740, 160, 270);
		Forward(mo, t, 1100, 12);
		if (t == 1125) Check("outOntoGallery", mo.pos.z == 160 && mo.pos.y < 1696 && have == "VIOLET");
		if (t == 1128) Pose(mo, -300, 1376, 160, 0);
		Forward(mo, t, 1130, 14);
		if (t == 1163) Check("downInDome", mo.pos.z == 0);
		if (t == 1165) FindFrame(103).Activate(mo);
		if (t == 1168) Check("violetHungInDome", have == "-");
		// YELLOW through it: over the knoll and the ravine to the hillside, and YELLOW for BLUE
		if (t == 1170) Take(mo, 4);
		if (t == 1175) Pose(mo, 320, 1000, 0, 270);
		Forward(mo, t, 1180, 25);
		if (t == 1215) Check("onKnollWithYellow", mo.pos.z == 0 && mo.pos.y > 2592 && mo.pos.y < 2944 && have == "YELLOW");
		if (t == 1220) Pose(mo, 0, 2640, 0, 270);
		Forward(mo, t, 1225, 20);
		if (t == 1255) Pose(mo, -720, 2432, -128, 180);
		Forward(mo, t, 1260, 36);
		if (t == 1305) Pose(mo, -960, 2432, 0, 270);
		Forward(mo, t, 1310, 10);
		if (t == 1330) Check("onHillsideWithYellow", mo.pos.z == 0 && mo.pos.y < 2400 && have == "YELLOW");
		if (t == 1335) { Pose(mo, 120, 2336, 0, 180); FindFrame(104).Activate(mo); }
		if (t == 1338) Check("swappedForBlue", have == "BLUE");
		// through YELLOW onto the gallery, into the night room, and BLUE beside its own far side
		Forward(mo, t, 1340, 25);
		if (t == 1380) Check("onGalleryWithBlue", mo.pos.z == 160 && mo.pos.y < 1696 && mo.pos.x > 256 && have == "BLUE");
		if (t == 1385) Pose(mo, 0, 1660, 160, 90);
		Forward(mo, t, 1390, 12);
		if (t == 1415) Check("inNightRoomWithBlue", mo.pos.y > 1712 && mo.pos.x > -160 && mo.pos.x < 160 && have == "BLUE");
		if (t == 1420) { FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		// the way out is walked into
		if (t == 1425) Pose(mo, -100, 1776, 160, 180);
		Forward(mo, t, 1455, 30);
	}

	// MAP08: a solution of the same length as the one tools/build.py prints.
	// No Stray door is used. The last part is the dash: from the lever to the
	// frame's half of the night room on foot, with no help from the script.
	void ClosingTimeScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); FindLine(303).Activate(mo, 0, SPAC_Use); }
		if (t == 34) Check("lockedBoltedAndShut", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303) && !RoomOpen(305) && !RoomOpen(306) && !RoomOpen(310) && shutterLeft < 0);
		// RED into the lobby's frame: the gallery over the atrium, key 1, and down through the gap
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 180, -96, 0, 0); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("onGallery", mo.pos.z == 160 && mo.pos.x > -512 && mo.pos.x < -384 && mo.pos.y > 144);
		if (t == 85) Pose(mo, -448, 200, 160, 90);
		Forward(mo, t, 90, 10);
		if (t == 110) Check("haveKey1", Has(mo, 1));
		if (t == 115) Pose(mo, -440, 432, 160, 0);
		Forward(mo, t, 120, 16);
		if (t == 150) Check("droppedIntoAtrium", mo.pos.z == 0 && mo.pos.x > -384);
		// key 1 opens the west wing: GREEN into the furniture department's frame, the roof, key 2
		if (t == 155) { Pose(mo, -470, 80, 0, 180); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 195) Check("westWingOpens", RoomOpen(301));
		if (t == 200) { Take(mo, 3); FindFrame(102).Activate(mo); Pose(mo, -1216, -360, 0, 270); }
		Forward(mo, t, 205, 25);
		if (t == 245) Check("onRoof", mo.pos.z == 320 && mo.pos.y > 416 && mo.pos.y < 1040 && have == "-");
		if (t == 250) Pose(mo, -1340, 540, 320, 270);
		Forward(mo, t, 255, 12);
		if (t == 275) Check("haveKey2", Has(mo, 2));
		// off the roof by the hole, onto the gallery, and down
		if (t == 280) Pose(mo, -580, 944, 320, 0);
		Forward(mo, t, 285, 14);
		if (t == 314) Check("fromRoofOntoGallery", mo.pos.z == 160 && mo.pos.x > -512 && mo.pos.x < -384);
		if (t == 315) Pose(mo, -440, 432, 160, 0);
		Forward(mo, t, 320, 16);
		// key 2 opens the east wing: key 3 among the linen, YELLOW among the carpets
		if (t == 350) { Pose(mo, 470, 80, 0, 0); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 390) Check("eastWingOpens", RoomOpen(302));
		if (t == 395) Pose(mo, 944, 760, 0, 90);
		Forward(mo, t, 400, 10);
		if (t == 420) Check("haveKey3", Has(mo, 3));
		if (t == 425) Take(mo, 4);
		// YELLOW through RED, along the gallery and down the hole into the showroom
		if (t == 430) Pose(mo, 180, -96, 0, 0);
		Forward(mo, t, 435, 25);
		if (t == 470) Check("onGalleryWithYellow", mo.pos.z == 160 && mo.pos.x < -384 && have == "YELLOW");
		if (t == 475) Pose(mo, -448, 980, 160, 90);
		Forward(mo, t, 480, 16);
		if (t == 514) Check("inShowroomWithYellow", mo.pos.z == 0 && mo.pos.y > 1056 && mo.pos.y < 1440 && have == "YELLOW");
		// it does not leave by the turnstile
		if (t == 515) Pose(mo, -288, 1100, 0, 270);
		Forward(mo, t, 520, 12);
		if (t == 545) Check("turnstileRefusesADoor", mo.pos.y > 1056 && have == "YELLOW");
		if (t == 550) FindFrame(107).Activate(mo);
		if (t == 553) Check("yellowHungInShowroom", have == "-");
		// up the stairs, past the gatepost, into the office: key 4, and the lever
		if (t == 555) Pose(mo, -190, 1080, 0, 0);
		Forward(mo, t, 560, 45);
		if (t == 610) Check("upTheStairsToTheOffice", mo.pos.z == 160 && mo.pos.x > 128);
		if (t == 615) Pose(mo, 336, 1180, 160, 270);
		Forward(mo, t, 620, 12);
		if (t == 640) Check("haveKey4", Has(mo, 4));
		if (t == 645) FindLine(309).Activate(mo, 0, SPAC_Use);
		if (t == 665) Check("leverSendsShutterUp", RoomOpen(310) && shutterLeft > 200 && shutterLeft < 280);
		// off the balcony, through the hatch into the dock: VIOLET, which the hatch refuses
		if (t == 670) Pose(mo, 180, 1312, 160, 180);
		Forward(mo, t, 675, 14);
		if (t == 704) Check("offTheBalcony", mo.pos.z == 0 && mo.pos.x < 128);
		if (t == 705) Pose(mo, -416, 1400, 0, 90);
		Forward(mo, t, 710, 22);
		if (t == 740) Check("throughTheHatch", mo.pos.z == 0 && mo.pos.y > 1520 && mo.pos.y < 1840);
		if (t == 745) Take(mo, 5);
		if (t == 750) Pose(mo, -416, 1560, 0, 270);
		Forward(mo, t, 755, 10);
		if (t == 775) Check("hatchRefusesADoor", mo.pos.y > 1440 && have == "VIOLET");
		// down the chute into the stockroom, up its stairs, through the door into the passage
		if (t == 780) Pose(mo, 340, 1776, 0, 0);
		Forward(mo, t, 785, 14);
		if (t == 815) Check("downTheChute", mo.pos.z == -128 && mo.pos.x > 400 && have == "VIOLET");
		if (t == 820) Pose(mo, 1088, 1560, -128, 270);
		Forward(mo, t, 825, 40);
		if (t == 870) Check("upTheStockroomStairs", mo.pos.z == 0 && mo.pos.y < 1264 && mo.pos.y > 1120);
		if (t == 872) FindLine(307).Activate(mo, 0, SPAC_Use);
		Forward(mo, t, 905, 22);
		if (t == 935) Check("inGoodsPassage", mo.pos.y < 1104 && mo.pos.y > 896);
		if (t == 960) Check("shutterCameDown", !RoomOpen(310) && shutterLeft < 0);
		// VIOLET through RED and down the hole, into the showroom's other frame; through it, the dock
		if (t == 965) Pose(mo, 180, -96, 0, 0);
		Forward(mo, t, 970, 25);
		if (t == 1010) Pose(mo, -448, 980, 160, 90);
		Forward(mo, t, 1015, 16);
		if (t == 1049) Check("inShowroomWithViolet", mo.pos.z == 0 && mo.pos.y > 1056 && mo.pos.y < 1440 && have == "VIOLET");
		if (t == 1050) FindFrame(106).Activate(mo);
		if (t == 1055) Pose(mo, -32, 1380, 0, 90);
		Forward(mo, t, 1060, 25);
		if (t == 1095) Check("throughVioletToDock", have == "-" && mo.pos.y > 1520 && mo.pos.y < 1840 && mo.pos.x > -320 && mo.pos.x < -192);
		// back by the hatch and the turnstile, with empty hands
		if (t == 1100) Pose(mo, -416, 1560, 0, 270);
		Forward(mo, t, 1105, 22);
		if (t == 1135) Check("backThroughTheHatch", mo.pos.y < 1440);
		if (t == 1140) Pose(mo, -288, 1100, 0, 270);
		Forward(mo, t, 1145, 14);
		if (t == 1170) Check("throughTheTurnstile", mo.pos.y < 1040);
		// keys 3 and 4 open the cash office: its lever opens the shop window; BLUE
		if (t == 1175) { Pose(mo, -200, -272, 0, 180); FindLine(303).Activate(mo, 0, SPAC_Use); }
		if (t == 1215) Check("cashOfficeOpens", RoomOpen(303));
		if (t == 1220) { Pose(mo, -540, -272, 0, 180); FindLine(308).Activate(mo, 0, SPAC_Use); }
		if (t == 1260) Check("leverOpensShopWindow", RoomOpen(305));
		if (t == 1265) Take(mo, 2);
		// BLUE through RED, down the hole, and through YELLOW into the office
		if (t == 1270) Pose(mo, 180, -96, 0, 0);
		Forward(mo, t, 1275, 25);
		if (t == 1310) Pose(mo, -448, 980, 160, 90);
		Forward(mo, t, 1315, 16);
		if (t == 1349) Check("inShowroomWithBlue", mo.pos.z == 0 && mo.pos.y > 1056 && mo.pos.y < 1440 && have == "BLUE");
		if (t == 1350) Pose(mo, -160, 1380, 0, 90);
		Forward(mo, t, 1355, 25);
		if (t == 1390) Check("inOfficeWithBlue", mo.pos.z == 160 && mo.pos.x > 128 && mo.pos.y < 1440 && have == "BLUE");
		// the dash. To the lever; then nothing but walking: off the balcony,
		// through VIOLET, across the dock, under the shutter
		if (t == 1393) Pose(mo, 340, 1312, 160, 0);
		if (t == 1395) { FindLine(309).Activate(mo, 0, SPAC_Use); dashFrom = t; mo.angle = 180; }
		Forward(mo, t, 1396, 46);                                   // 368 west: off the balcony, to x = -28
		if (t == 1444) { mo.vel.xy = (0, 0); mo.angle = 90; }
		Forward(mo, t, 1445, 82);                                   // north: the frame, the dock, the shutter
		if (t > 1445 && !dashTook && mo.pos.y > 1936) dashTook = t - dashFrom;
		if (t == 1535) Check("underTheShutterWithBlue", dashTook > 0 && dashTook < 280 && mo.pos.y > 1936 && mo.pos.x > -320 && mo.pos.x < -160 && have == "BLUE");
		if (t == 1536) Console.Printf("AJARTEST dashTics=%d", dashTook);
		// nothing stands across the room: BLUE is carried the length of it
		if (t == 1540) Pose(mo, -290, 1976, 0, 180);
		Forward(mo, t, 1545, 10);
		if (t == 1565) Check("acrossTheRoomWithBlue", mo.pos.x < -320 && have == "BLUE");
		if (t == 1570) { FindFrame(190).Activate(mo); Check("wayOutBuilt", wayOutBuilt && !carried); }
		// the way out is walked into
		if (t == 1575) Pose(mo, -220, 2064, 0, 0);
		Forward(mo, t, 1580, 30);
	}
	int dashFrom, dashTook;

	// MAP09: the shortest solution as printed by tools/build.py, with the
	// places that refuse a door tried on the way.
	void PuttingThroughScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		string have = carried ? carried.Label() : "-";
		bool inTrunk = mo.pos.z == 0 && mo.pos.x > 336 && mo.pos.x < 848 && mo.pos.y > 304 && mo.pos.y < 560;
		bool onBalcony = mo.pos.z == 160 && mo.pos.x > -768 && mo.pos.x < -512 && mo.pos.y > -288 && mo.pos.y < -32;
		bool onGallery = mo.pos.z == 160 && mo.pos.x > -768 && mo.pos.x < 384 && mo.pos.y > 96 && mo.pos.y < 224;
		bool onRoof = mo.pos.z == 320 && mo.pos.x > -1344 && mo.pos.x < -528 && mo.pos.y > 240 && mo.pos.y < 928;
		bool inTest = mo.pos.z == 0 && mo.pos.x > 1200 && mo.pos.x < 1520 && mo.pos.y > -560 && mo.pos.y < -304;
		bool onLine = mo.pos.z == 96 && mo.pos.x > 760 && mo.pos.x < 1080 && mo.pos.y > -560 && mo.pos.y < -304;
		if (t == 20) { FindLine(301).Activate(mo, 0, SPAC_Use); FindLine(302).Activate(mo, 0, SPAC_Use); FindLine(303).Activate(mo, 0, SPAC_Use); }
		// the thief has YELLOW: it is caught first, so that the door lies where it fell.
		if (t == 22)
		{
			let ti = ThinkerIterator.Create("AjarThief");
			Actor th = Actor(ti.Next());
			if (th) th.DamageMobj(null, null, 10000, 'None');
		}
		if (t == 34) Check("lockedAndBolted", !RoomOpen(301) && !RoomOpen(302) && !RoomOpen(303) && !RoomOpen(305) && !RoomOpen(306));
		// the start is in the forecourt. RED into the call office's frame: the roof,
		// key 1 in its far corner, and down the hole onto the gallery
		if (t == 30) Check("startsInForecourt", mo.pos.z == 0 && mo.pos.y < -576 && have == "-");
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 300, -432, 0, 0); }
		Forward(mo, t, 40, 25);
		if (t == 80) Check("onRoof", onRoof && have == "-");
		if (t == 85) Pose(mo, -1290, 410, 320, 270);
		Forward(mo, t, 90, 12);
		if (t == 110) Check("haveKey1", Has(mo, 1));
		if (t == 115) Pose(mo, -608, 330, 320, 270);
		Forward(mo, t, 120, 14);
		if (t == 153) Check("fromRoofOntoGallery", mo.pos.z < 320 && mo.pos.y > 96 && mo.pos.y < 224);
		if (t == 185) Pose(mo, -224, 130, 160, 270);
		Forward(mo, t, 190, 9);
		if (t == 200) mo.vel.xy = (0, 0);                              // straight down, not onto a switchboard
		if (t == 222) Check("droppedIntoSwitchroom", mo.pos.z == 0 && mo.pos.y < 96);
		// the west wing is open; key 1 opens the cloakroom: key 2
		if (t == 225) { Pose(mo, -1320, -96, 0, 180); FindLine(301).Activate(mo, 0, SPAC_Use); }
		if (t == 265) Check("cloakroomOpens", RoomOpen(301));
		if (t == 270) Pose(mo, -1640, -190, 0, 270);
		Forward(mo, t, 275, 10);
		if (t == 295) Check("haveKey2", Has(mo, 2));
		// key 3 is in the far corner of the battery room
		if (t == 300) Pose(mo, 1428, 790, -128, 90);
		Forward(mo, t, 305, 12);
		if (t == 330) Check("haveKey3", Has(mo, 3));
		// keys 2 and 3 open the east wing: YELLOW, where the thief dropped it
		if (t == 340) { Pose(mo, 730, -168, 0, 0); FindLine(302).Activate(mo, 0, SPAC_Use); }
		if (t == 380) Check("eastWingOpens", RoomOpen(302));
		if (t == 385) Take(mo, 4);
		if (t == 388) Check("yellowFromTheThief", have == "YELLOW");
		// YELLOW through RED, down the hole, along the gallery into the cable loft, and down into the trunk room
		if (t == 390) Pose(mo, 300, -432, 0, 0);
		Forward(mo, t, 395, 25);
		if (t == 430) Check("onRoofWithYellow", onRoof && have == "YELLOW");
		if (t == 435) Pose(mo, -608, 330, 320, 270);
		Forward(mo, t, 440, 14);
		if (t == 470) Pose(mo, 224, 190, 160, 90);
		Forward(mo, t, 475, 52);
		if (t == 535) Check("inCableLoft", mo.pos.z == 160 && mo.pos.y > 576);
		if (t == 540) Pose(mo, 592, 620, 160, 270);
		Forward(mo, t, 545, 20);
		if (t == 580) Check("inTrunkRoomWithYellow", inTrunk && have == "YELLOW");
		// it does not leave by the hatch
		if (t == 585) Pose(mo, 448, 400, 0, 270);
		Forward(mo, t, 590, 25);
		if (t == 620) Check("hatchRefusesADoor", mo.pos.y > 224 && have == "YELLOW");
		// the lever at the trunk positions: the kiosk
		if (t == 623) FindLine(307).Activate(mo, 0, SPAC_Use);
		if (t == 625) { Pose(mo, 500, 432, 0, 180); FindFrame(190).Activate(mo); }
		if (t == 628) Check("yellowInABrassFrame", have == "-" && !wayOutBuilt);
		// through it: the monitor's balcony, key 4, and down through the gap
		Forward(mo, t, 630, 25);
		if (t == 663) Check("leverOpensKiosk", RoomOpen(305));
		if (t == 665) Check("onBalcony", onBalcony);
		if (t == 670) Pose(mo, -560, -200, 160, 270);
		Forward(mo, t, 675, 8);
		if (t == 695) Check("haveKey4", Has(mo, 4));
		if (t == 700) Pose(mo, -560, -160, 160, 0);
		Forward(mo, t, 705, 11);
		if (t == 717) mo.vel.xy = (0, 0);
		if (t == 737) Check("offTheBalcony", mo.pos.z == 0 && mo.pos.x > -512);
		// the test room, by its hatch: VIOLET, which the hatch refuses; into the test room's frame
		if (t == 740) Pose(mo, 1280, -240, 0, 270);
		Forward(mo, t, 745, 16);
		if (t == 775) Check("inTestRoom", inTest);
		if (t == 780) Take(mo, 5);
		if (t == 785) Pose(mo, 1280, -360, 0, 90);
		Forward(mo, t, 790, 14);
		if (t == 815) Check("testHatchRefusesADoor", mo.pos.y < -288 && have == "VIOLET");
		if (t == 820) FindFrame(104).Activate(mo);
		if (t == 823) Check("violetHungInTestRoom", have == "-");
		if (t == 825) Pose(mo, 1280, -360, 0, 90);
		Forward(mo, t, 830, 18);
		if (t == 860) Check("outByTheHatch", mo.pos.y > -288);
		// key 4 opens the manager's office: BLUE
		if (t == 865) { Pose(mo, -340, -432, 0, 180); FindLine(303).Activate(mo, 0, SPAC_Use); }
		if (t == 905) Check("officeOpens", RoomOpen(303));
		if (t == 910) Take(mo, 2);
		// BLUE through RED and down into the trunk room, swapped for YELLOW
		if (t == 915) Pose(mo, 300, -432, 0, 0);
		Forward(mo, t, 920, 25);
		if (t == 955) Pose(mo, -608, 330, 320, 270);
		Forward(mo, t, 960, 14);
		if (t == 990) Pose(mo, 224, 190, 160, 90);
		Forward(mo, t, 995, 52);
		if (t == 1055) Pose(mo, 592, 620, 160, 270);
		Forward(mo, t, 1060, 20);
		if (t == 1095) Check("inTrunkRoomWithBlue", inTrunk && have == "BLUE");
		if (t == 1100) { Pose(mo, 500, 432, 0, 180); FindFrame(190).Activate(mo); }
		if (t == 1103) Check("blueSwappedForYellow", have == "YELLOW" && !wayOutBuilt);
		// along the line with YELLOW: in by BLUE, out by VIOLET, into the test room
		Forward(mo, t, 1105, 25);
		if (t == 1140) Check("onTheLineWithYellow", onLine && have == "YELLOW");
		Forward(mo, t, 1145, 45);
		if (t == 1200) Check("alongTheLineIntoTestRoom", inTest && have == "YELLOW");
		if (t == 1205) { Pose(mo, 1360, -480, 0, 270); FindFrame(104).Activate(mo); }
		if (t == 1208) Check("violetSwappedOut", have == "VIOLET");
		// VIOLET leaves through YELLOW: the balcony, and down
		Forward(mo, t, 1210, 16);
		if (t == 1240) Check("onBalconyWithViolet", onBalcony && have == "VIOLET");
		if (t == 1245) Pose(mo, -560, -160, 160, 0);
		Forward(mo, t, 1250, 11);
		if (t == 1262) mo.vel.xy = (0, 0);
		// VIOLET through RED and down into the trunk room, into the other brass frame
		if (t == 1285) Pose(mo, 300, -432, 0, 0);
		Forward(mo, t, 1290, 25);
		if (t == 1325) Pose(mo, -608, 330, 320, 270);
		Forward(mo, t, 1330, 14);
		if (t == 1360) Pose(mo, 224, 190, 160, 90);
		Forward(mo, t, 1365, 52);
		if (t == 1425) Pose(mo, 592, 620, 160, 270);
		Forward(mo, t, 1430, 20);
		if (t == 1465) Check("inTrunkRoomWithViolet", inTrunk && have == "VIOLET");
		if (t == 1470) { FindFrame(191).Activate(mo); Check("chainBuilt", wayOutBuilt && chainBuilt && !carried); }
		// the way out is walked: through VIOLET onto the line, along it, and out by BLUE
		if (t == 1475) Pose(mo, 592, 432, 0, 0);
		if (t == 1530) Check("stillHere", inTrunk && !onTheLine);
		Forward(mo, t, 1535, 90);
		if (t == 1585) Check("walkedOntoTheLine", onLine && onTheLine);
	}

	// MAP09 mode 3: the chain by itself. One of the two doors in a brass
	// frame is a door like any other; both, and they stay; nothing ends
	// until the player has been onto the line and left it again by a door.
	void ChainScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		string have = carried ? carried.Label() : "-";
		bool onLine = mo.pos.z == 96 && mo.pos.x > 760 && mo.pos.x < 1080 && mo.pos.y > -560 && mo.pos.y < -304;
		if (t == 5)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) a.Destroy();
		}
		if (t == 35) { Take(mo, 5); Pose(mo, 440, 432, 0, 180); }
		if (t == 40) { FindFrame(190).Activate(mo); Check("oneDoorIsOnlyADoor", have == "VIOLET" && !carried && !wayOutBuilt); }
		if (t == 45) { FindFrame(190).Activate(mo); Check("itCanBeTakenAgain", carried && carried.Label() == "VIOLET"); }
		if (t == 50) FindFrame(190).Activate(mo);
		// through it onto the line, and out by the hole: nothing ends
		Forward(mo, t, 55, 20);
		if (t == 85) Check("ontoTheLine", onLine && !onTheLine);
		if (t == 90) Pose(mo, 920, -500, 96, 270);
		Forward(mo, t, 95, 14);
		if (t == 125) Check("outByTheHole", mo.pos.z == 0 && mo.pos.y < -576);
		if (t == 130) { Take(mo, 2); Pose(mo, 700, 432, 0, 0); }
		if (t == 135) { FindFrame(191).Activate(mo); Check("chainBuilt", wayOutBuilt && chainBuilt && !carried); }
		if (t == 136) { FindFrame(191).Activate(mo); Check("stillOnlyADoor", carried && carried.Label() == "BLUE" && !chainBuilt); }
		if (t == 137) { FindFrame(191).Activate(mo); Check("chainBuiltAgain", chainBuilt && !carried); }
		if (t == 140) Pose(mo, 592, 432, 0, 0);          // shot: east down the chain
		if (t == 200) Pose(mo, 692, 432, 0, 180);        // shot: west
		if (t == 260) Check("nothingEndsInTheTrunkRoom", !onTheLine);
		if (t == 261) Pose(mo, 592, 432, 0, 0);
		Forward(mo, t, 265, 44);                         // through BLUE: onto the line at its west end, and along it
		if (t == 310) mo.vel.xy = (0, 0);
		if (t == 315) Check("walkedOntoTheLine", onLine && onTheLine);
		if (t == 316) Check("nowTheyStay", FindFrame(190).door.nailer && FindFrame(191).door.nailer);
		// out by the hole: the doors stay, and nothing ends
		if (t == 330) Pose(mo, 920, -500, 96, 270);
		Forward(mo, t, 335, 14);
		if (t == 365) Check("theHoleEndsNothing", mo.pos.z == 0 && mo.pos.y < -576 && !onTheLine && chainBuilt);
		if (t == 366) Check("itsDoorsAreDoorsAgain", !FindFrame(190).door.nailer && !FindFrame(191).door.nailer);
		// round again, along the line and out by VIOLET's end: that ends it
		if (t == 370) Pose(mo, 592, 432, 0, 0);
		Forward(mo, t, 375, 44);
		if (t == 420) mo.vel.xy = (0, 0);
		if (t == 425) Check("backOnTheLine", onLine && onTheLine);
		Forward(mo, t, 430, 60);
	}

	// MAP10 mode 3: the two ways out. BLUE in door 6 of the bus and VIOLET in
	// the shelter: the plain loop, and either can be taken down again. Then
	// PINK in door 2, VIOLET carried through it into PINK's room and hung
	// there, PINK brought round to the shelter: the loop of three, a secret.
	// Onto the line through BLUE and out at its far end: the secret way out.
	void LongWayScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		string have = carried ? carried.Label() : "-";
		bool onLine = mo.pos.z == 64 && mo.pos.x > 304 && mo.pos.x < 624 && mo.pos.y > -560 && mo.pos.y < -304;
		bool inPink = mo.pos.z == 144 && mo.pos.x > 96 && mo.pos.x < 416 && mo.pos.y > 1072 && mo.pos.y < 1328;
		if (t == 5)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) a.Destroy();
			Check("oneSecretMoreThanSectors", level.total_secrets == 4);
		}
		if (t == 35) { Take(mo, 2); FindFrame(190).Activate(mo); Check("oneDoorIsOnlyADoor", !carried && !chainLen); }
		if (t == 40) { Take(mo, 5); FindFrame(191).Activate(mo); Check("plainLoop", !carried && chainLen == 2 && !longFound); }
		if (t == 45) Pose(mo, 320, -150, 0, 90);         // shot: into door 6, down the chain
		if (t == 100) { FindFrame(191).Activate(mo); Check("stillOnlyADoor", have == "-" && carried && carried.Label() == "VIOLET" && !chainLen); }
		if (t == 105) { Pose(mo, -100, -300, 0, 90); DropDoor(carried, mo); carried = null; }
		if (t == 107) { Take(mo, 6); FindFrame(101).Activate(mo); Check("pinkInDoorTwo", !carried && FindFrame(101).door); }
		if (t == 110) { Take(mo, 5); Pose(mo, -192, -40, 0, 90); }
		Forward(mo, t, 112, 16);                         // through PINK, with VIOLET
		if (t == 135) { mo.vel.xy = (0, 0); Check("inPinksRoomWithViolet", inPink && have == "VIOLET"); }
		if (t == 136) Check("pinksRoomIsASecret", level.found_secrets == 1);
		if (t == 140) { FindFrame(192).Activate(mo); Check("violetInPinksRoom", !carried && !chainLen); }
		// the frame takes any door: RED for VIOLET, and back
		if (t == 141) { Take(mo, 1); FindFrame(192).Activate(mo); Check("anyDoorInPinksRoom", carried && carried.Label() == "VIOLET" && FindFrame(192).door.Label() == "RED"); }
		if (t == 142) { FindFrame(192).Activate(mo); Check("violetBackInPinksRoom", carried && carried.Label() == "RED" && !chainLen); }
		if (t == 143) { DropDoor(carried, mo); carried = null; }
		if (t == 145) Pose(mo, 200, 1200, 144, 180);
		Forward(mo, t, 146, 20);                         // back out through PINK
		if (t == 175) { mo.vel.xy = (0, 0); Check("backAtTheStop", mo.pos.z == 0 && mo.pos.y < 0 && mo.pos.y > -640); }
		if (t == 180) { FindFrame(101).Activate(mo); FindFrame(191).Activate(mo); }
		if (t == 182) Check("longLoop", !carried && chainLen == 3 && longFound && level.found_secrets == 2);
		if (t == 185) Pose(mo, 320, -150, 0, 90);        // shot: into door 6, the long way round
		if (t == 240) Pose(mo, 320, -60, 0, 270);        // shot: into the shelter
		if (t == 300) { Check("nothingEndsAtTheStop", !onTheLine); Pose(mo, 320, -60, 0, 90); }
		Forward(mo, t, 302, 20);                         // through BLUE: onto the line
		if (t == 330) { mo.vel.xy = (0, 0); Check("walkedOntoTheLine", onLine && onTheLine); }
		if (t == 331) Check("nowTheyStay", FindFrame(190).door.nailer && FindFrame(191).door.nailer && FindFrame(192).door.nailer);
		Forward(mo, t, 335, 60);                         // and out at its far end: wayOut=secret
	}

	// MAP31's tour (see PartyWallViews): the cinema's foyer, its three halls
	// from the floor and from their boxes, a lobby, the closet.
	void SecretOneViews()
	{
		static const double v[] = {
			384, -700, 32, 90, 0,          // the foyer from the street doors: the way in, HALL 1
			420, -592, 32, 180, 0,         // the box office
			470, -540, 32, 70, 0,          // posters on the north wall
			300, -400, 32, 315, 0,         // the bench, posters on the east wall
			384, -420, 32, 270, 0,         // the street doors
			384, -300, 32, 90, 0,          // the way into hall 1
			384, -30, 32, 90, 0,           // hall 1 from the step down
			384, 800, 0, 270, -8,          // hall 1: back at the way in, the screen over it
			-22, 128, 0, 180, 0,           // a time door, close up
			300, 480, 0, 180, -8,          // hall 1: the west box's glass, a tall block
			384, 500, 0, 90, -6,           // hall 1's north wall: time door, glass, steel door
			-232, 516, 64, 0, 12,           // from hall 1's west box, through the glass
			-232, 558, 64, 200, 0,          // in that box: its door
			732, 1006, 0, 50, 0,            // the lobby behind hall 1's steel door: HALL 2
			3520, -290, 32, 90, 0,         // the way into hall 2
			3520, -30, 32, 90, 0,          // hall 2 from the step down
			4188, 1116, 0, 222, -6,         // hall 2 from its far corner
			3556, 1300, 64, 270, 12,        // from hall 2's north box
			2554, 680, 64, 315, 0,         // in hall 2's west box: the cupboard, the glass
			6656, -30, 32, 90, 0,          // the great hall from the step down
			7660, 772, 64, 180, 12,        // from its east box: the arrow on a block
			5880, 150, 0, 45, -6,          // the great hall from its floor
			6656, 1300, 0, 270, -8,         // the great hall: the screen
			6132, -30, 0, 215, 0,          // the secret closet
			7390, 1518, 0, 50, 0,          // the last lobby: the way out
			2560, 608, 64, 0, 0,           // hall 2's west box: the plates that wind the fight, beside the glass
			3520, 300, 0, 270, 0           // and in hall 2, either side of the way in
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP10's tour (see PartyWallViews).
	void AllChangeViews1()
	{
		static const double v[] = {
			-64, -592, 0, 90, 0,           // from the start: the square, the bus
			-64, -300, 0, 90, 0,           // the bus, nearer
			-360, -160, 0, 20, 0,          // along the bus from its west end
			200, -200, 0, 135, 0,          // and from the shelter's corner
			320, -180, 0, 90, 0,           // from the shelter: door 6, the brass frame
			320, -40, 0, 270, 0,           // from door 6: the shelter's brass frame
			300, -128, 0, 0, 0,            // the route board
			-620, 72, 0, 0, 0,             // the bus from in front
			430, -70, 0, 250, -25,         // over the shelter: the hole, the line
			-288, -560, 0, 270, 0,         // the kiosk behind its bars
			-250, -368, 0, 180, 0,         // the museum's door: one lock
			-7850, 800, 0, 200, 0,         // the hotel's far hall
			-6144, 40, 0, 90, 0,           // line 1: the hotel, where MAP02 began
			620, 420, 0, 215, 0,           // round the back of the bus, from the lane's corner
			-6420, 290, 0, 180, 0,         // its corridor
			-6740, 320, 0, 45, 0,          // a room: RED
			3584, 40, 0, 110, 0,           // line 5: the station, where MAP05 began
			3350, 500, 0, 90, 0,           // the concourse
			3520, 1250, 0, 0, 0,           // the far platform: YELLOW
			3520, 290, 0, 20, 0,           // the near platform, the tracks
			320, -432, 64, 0, 0            // the line
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void AllChangeViews2()
	{
		static const double v[] = {
			-224, -3400, 0, 60, 0,         // the theatre: the foyer from RED's far side
			256, -3530, 0, 20, 0,          // the stage door: a ledge, a pit, the line to the other stop
			40, -3700, 0, 315, 0,          // the house
			1100, -4030, -48, 170, 0,      // from the stage
			300, -3080, 0, 20, 0,          // the rooms behind the foyer: GREEN
			-560, -368, 0, 180, 0,         // the museum's hall
			0, 2920, 0, 90, 0,             // the other stop: the 20
			-1220, -400, -128, 180, 0,     // the cellar: its frame
			-1560, -150, -128, 300, 0,     // the cellar: VIOLET, the stairs
			-760, 360, 0, 200, 0,          // the gallery
			-1068, 370, 0, 90, 0,          // PINK's store through its bars
			-1020, 620, 0, 200, 0,         // PINK's store
			0, 620, 48, 90, 0,             // the depot from YELLOW's far side
			0, 420, 0, 270, 0,             // the bus from behind: doors 7 and 8
			-600, 3560, 0, 330, 0,         // the 20 from behind
			250, 852, 48, 90, -30,         // the hole from PINK's room
			120, 1200, 144, 0, 0,          // PINK's room: its brass frame
			400, 1112, 144, 160, 0,        // PINK's room: PINK's far side
			1856, 1020, 0, 90, 0,          // line 8: the observatory's library
			1856, 1440, 0, 90, 20,         // the dome from its ledge: BLUE, the frame
			1700, 1500, -96, 30, -10       // down in the dome
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP09's tour (see PartyWallViews).
	void PuttingThroughViews1()
	{
		static const double v[] = {
			0, -768, 0, 90, 0,             // from the start: the forecourt, the front door
			600, -780, 0, 45, -20,         // the hole high in the wall: the line
			-300, -720, 0, 180, 0,         // the kiosk behind its bars
			0, -520, 0, 90, 0,             // the call office
			-100, -432, 0, 180, 0,         // RED leaning, the manager's two locks
			250, -432, 0, 0, 0,            // the call office's frame
			-450, -432, 0, 180, 0,         // the manager's office: BLUE
			0, -250, 0, 90, -8,            // the switchroom from the way in
			0, -100, 0, 180, -8,           // west down the hall: the balcony
			0, -100, 0, 0, -8,             // east down the hall
			-200, -100, 0, 90, -15,        // the supervisor's gallery, GREEN's far side
			480, -160, 0, 270, 0,          // the switchroom's frame
			448, 100, 0, 90, 0,            // the hatch to the trunk room
			-700, 160, 160, 0, 0,          // on the gallery
			0, 160, 160, 270, 15,          // from the gallery, the boards
			-640, -160, 160, 0, 5,         // on the balcony
			224, 300, 160, 90, 0,          // the way into the cable loft
			300, 690, 160, 0, 0,           // the cable loft
			592, 640, 160, 270, 25,        // the hole down into the trunk room
			650, 432, 0, 180, 0            // the trunk room: the west brass frame
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void PuttingThroughViews2()
	{
		static const double v[] = {
			530, 432, 0, 0, 0,             // the east brass frame
			400, 520, 0, 320, 0,           // the trunk room across: the hatch, the chute
			900, 520, -128, 0, 0,          // the battery room
			1440, 520, -128, 270, -15,     // its stairs
			820, 150, 0, 0, 0,             // the cable passage
			1104, 280, 0, 90, 0,           // the generator room
			-880, 32, 0, 180, 0,           // the canteen
			-1400, -96, 0, 180, 0,         // the cloakroom
			-1136, 140, 0, 120, 0,         // the rest room: GREEN, the frame
			-928, 860, 320, 270, 0,        // the roof, from RED's far side
			-700, 600, 320, 135, 0,        // RED's far side
			-608, 340, 320, 270, 20,       // the hole onto the gallery
			820, -168, 0, 0, 0,            // the apparatus room
			1200, -130, 0, 180, 0,         // down the racks
			1400, -168, 0, 0, 0,           // the relay room
			1280, -330, 0, 250, 0,         // the test room: its frame
			1400, -400, 0, 150, 0,         // VIOLET, the hatch
			-1736, -200, 0, 250, 0,        // the stationery store: PINK, a frame
			-1726, -32, 0, 180, 0,         // the strongroom: PINK's far side
			920, -432, 96, 180, 0,         // the line: BLUE's far side
			920, -432, 96, 0, 0,           // VIOLET's
			920, -360, 96, 270, 15         // the hole over the forecourt
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void PuttingThroughViews3()
	{
		static const double v[] = {
			-416, -110, 0, 75, -18,        // from the hall: the gallery, GREEN's far side
			250, 620, 160, 12, 0,          // the cable loft, past its drums
			-200, -200, 0, 180, -12,       // from the hall: the balcony, YELLOW's far side
			40, -400, 0, 335, 0,           // the call boxes
			330, -810, 0, 115, -10,        // the front and its windows
			1136, 600, -128, 90, 0         // the battery room: the cells, the frame
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP08's tour, in three parts (see PartyWallViews).
	void ClosingTimeViews1()
	{
		static const double v[] = {
			0, -640, 0, 90, 0,             // from the start: the arcade, the front door
			300, -600, 0, 60, 0,           // the shop window, behind glass
			-560, -592, 0, 180, 0,         // the kiosk behind its bars
			0, -400, 0, 90, 0,             // the lobby
			100, -96, 0, 0, 0,             // the lobby's frame
			-100, -380, 0, 180, 0,         // RED, leaning
			-100, -272, 0, 180, 0,         // the cash office's door: two locks
			100, -368, 0, 0, 0,            // the shop window's door, bolted
			448, -400, 0, 90, 0,           // in the shop window
			-400, -272, 0, 180, 0,         // the cash office: its lever, BLUE
			0, 40, 0, 90, -15,             // the atrium: the fountain, the lantern
			-200, 80, 0, 180, 0,           // the west wing's door: one lock
			200, 80, 0, 0, 0,              // the east wing's: one lock
			200, 500, 0, 180, -20,         // the gallery, RED's far side, from below
			200, 944, 0, 0, 0,             // the goods passage's door
			-288, 900, 0, 90, 0,           // the turnstile into the showroom
			-448, 600, 160, 180, 0,        // on the gallery: RED's far side
			-448, 300, 160, 270, 0,        // along the gallery: key 1
			-420, 432, 160, 0, 25,         // the gap in the rail: the atrium
			-448, 900, 160, 90, 0          // the hole into the showroom; the hole from the roof
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void ClosingTimeViews2()
	{
		static const double v[] = {
			-448, 1100, 0, 0, 0,           // the showroom: doors on show, the stairs, the balcony
			-300, 1150, 0, 250, 0,         // the turnstile, from inside
			-448, 1150, 0, 110, -30,       // the hole from the gallery, from below
			-96, 1300, 0, 90, 0,           // the showroom's two frames
			-100, 1300, 0, 0, -20,         // the balcony: the gap in its rail
			64, 1300, 0, 90, 0,            // the window on the dock
			-416, 1300, 0, 90, 0,          // the hatch to the dock
			-190, 1088, 0, 0, -10,         // the stairs up to the office
			80, 1080, 160, 0, 0,           // the gatepost at their head
			256, 1150, 160, 90, 0,         // the office: YELLOW's far side, the window
			256, 1280, 160, 0, 0,          // the lever
			336, 1380, 160, 90, 10,        // from the office window: the dock, the shutter
			200, 1312, 160, 180, 20,       // from the balcony: the gap, the frames
			-256, 1680, 0, 270, 0,         // the dock: VIOLET's far side
			-256, 1620, 0, 90, 0,          // the shutter
			-416, 1700, 0, 90, 0,          // the wall beside the shutter
			200, 1700, 0, 0, 0,            // VIOLET, and the chute
			100, 1560, 0, 180, 0,          // the dock, from its east end
			-400, 2064, 0, 0, 0,           // the night room, and the frame at its far end
			-340, 2064, 0, 180, 0,         // BLUE's far side
			-240, 2064, 0, 0, 0,           // the frame's half: the brass frame
			-240, 2100, 0, 270, 0,         // the shutter from inside
			-260, 2000, 0, 180, 0          // the room from its south wall
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void ClosingTimeViews3()
	{
		static const double v[] = {
			460, 1776, -128, 0, 0,         // the stockroom, from under the chute
			768, 1800, -128, 90, 0,        // the stockroom's frame
			1088, 1700, -128, 270, 0,      // the stairs up
			1100, 1744, -128, 0, 0,        // the hole into the alcove
			1088, 1200, 0, 270, 0,         // the door into the passage
			1100, 1000, 0, 180, 0,         // the goods passage
			768, 960, 0, 90, 0,            // the boiler room's door, bolted
			768, 1150, 0, 90, 0,           // the boiler room
			-600, 80, 0, 180, 0,           // the west wing: toys
			-1040, 176, 0, 180, 0,         // haberdashery
			-1216, 100, 0, 270, 0,         // the door to the furniture
			-1216, -100, 0, 270, 0,        // furniture: the frame
			-1300, -200, 0, 135, 0,        // GREEN
			-992, 900, 320, 90, 0,         // the roof: GREEN's far side
			-700, 600, 320, 180, 0,        // across the roof: key 2
			-600, 944, 320, 0, 15,         // the hole down onto the gallery
			600, 80, 0, 0, 0,              // the east wing: china
			752, 400, 0, 90, 0,            // linen: key 3
			1040, 176, 0, 0, 0,            // carpets: YELLOW
			1088, 100, 0, 270, 0,          // the hole into the lamp store
			1096, -60, 0, 270, 0,          // the lamp store: PINK and its frame
			1120, -120, 0, 0, 0,           // through its bars, the strongroom
			1328, -30, 0, 270, 0           // the strongroom: PINK's far side
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void ClosingTimeViews4()
	{
		static const double v[] = {
			520, -576, 0, 0, 0,            // the arcade's gate, the street beyond
			-400, -600, 0, 20, -30,        // its roof of iron and glass
			-300, 300, 0, 45, -40,         // the atrium's lantern
			-1100, 700, 320, 135, 0,       // the roof's edge: the town
			-1380, 700, 320, 180, 20,      // over the parapet
			-700, 100, 0, 50, 0,           // toys: the rocking horse
			1200, 120, 0, 50, 0,           // carpets, rolled
			-900, 176, 0, 180, 0,          // toys: the door to the haberdashery
			40, -200, 0, 300, 0            // the enquiry desk and its till
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP07's tour, in three parts (see PartyWallViews).
	void SmallHoursViews1()
	{
		static const double v[] = {
			0, -768, 0, 90, 0,             // from the start: the road, the gate
			192, -420, 0, 90, 0,           // the frame by the gate, RED leaning
			96, -380, 0, 110, 0,           // through the bars: RED's far side
			0, -200, 0, 160, 0,            // inside the gate: RED's far side
			0, 40, 0, 90, 0,               // the forecourt
			-300, 256, 0, 180, 0,          // the arch to the yard
			0, 560, 0, 90, 0,              // the hall: the dome's door
			100, 592, 0, 0, 0,             // the hall's frame
			100, 740, 0, 20, 0,            // GREEN, and the east wing's door: one lock
			-100, 720, 0, 180, 0,          // the library's door
			-300, 720, 0, 180, -15,        // the library, the stacks over it
			-560, 740, 0, 225, 0,          // the frame under the stacks
			-720, 700, 0, 215, -30,        // GREEN's far side, from below
			-896, 640, 160, 270, 0,        // on the stacks: GREEN's far side
			-880, 720, 160, 0, 25,         // from the stacks, the library
			-896, 700, 160, 90, 0,         // along the stacks: key 1
			0, 960, 0, 90, -15,            // the dome: the telescope, the gallery
			160, 1000, 0, 300, 0,          // the frame under the gallery
			200, 1200, 0, 60, -25,         // YELLOW's far side, from below
			-320, 1100, 160, 90, 0         // along the west gallery
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void SmallHoursViews2()
	{
		static const double v[] = {
			-300, 1280, 160, 180, 0,       // the gallery: the door to the roof
			-300, 1500, 160, 315, 25,      // from the gallery, the dome floor
			0, 1600, 160, 90, 0,           // the night room's door, bolted
			200, 1620, 160, 45, 0,         // YELLOW's far side
			320, 1300, 160, 270, 0,        // the east gallery: key 2
			-20, 1840, 160, 180, 0,        // the night room: the ready-made pair
			20, 1840, 160, 0, 0,           // the night room: BLUE's far side and the frame
			-500, 1280, 160, 180, 0,       // the roof
			-900, 960, 160, 45, 0,         // across the roof
			-672, 1640, 160, 90, 25,       // the gap in the roof's rail: the hillside
			-440, 1640, 160, 90, 20,       // the gatepost at the head of the steps
			-600, 1900, 0, 0, -10,         // the steps up to the roof
			-900, 1824, 0, 180, 0,         // the stile
			-800, 300, 0, 0, 0,            // the west yard
			-1008, 200, 0, 270, 0,         // the boiler house's door, bolted
			-1008, 20, 0, 270, 0,          // the boiler house
			-1088, 500, 0, 90, 0,          // the lane
			-1050, 832, 0, 180, 0,         // the west wing's door: one lock
			-1088, 1700, 0, 135, 0,        // the shed behind its bars
			-1060, 1824, 0, 0, 0           // the stile, from the lane
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void SmallHoursViews3()
	{
		static const double v[] = {
			-200, 2100, 0, 45, 0,          // the hillside: the tower stump
			200, 2336, 0, 180, 0,          // the hillside's frame
			200, 2300, 0, 80, 0,           // VIOLET's far side, across the ravine
			300, 2100, 0, 270, 0,          // VIOLET
			-500, 2380, 0, 200, 20,        // the ravine's steps
			-400, 2500, -128, 150, 0,      // the ravine: the cave's door
			-784, 2640, -128, 90, 0,       // the cave
			192, 2700, 0, 90, 0,           // the knoll: VIOLET's far side
			-256, 2700, 0, 90, 0,          // the transit house's door: two locks
			0, 2650, 0, 270, 10,           // from the knoll, the hillside's frame
			-256, 3000, 0, 60, 0,          // the transit house
			-200, 3120, 0, 180, 0,         // its lever, and BLUE
			-1250, 832, 0, 180, 0,         // the west wing: the workshop
			-1408, 1100, 0, 90, 0,         // the instrument room: YELLOW, the hole
			-1408, 560, 0, 270, 0,         // the clock room: key 4
			-1536, 1480, 0, 90, 0,         // the lens store: PINK and its frame
			-1500, 1560, 0, 0, 0,          // through its bars, the armoury
			-1296, 1480, 0, 90, 0,         // the armoury: PINK's far side
			400, 720, 0, 0, 0,             // the east wing: the lecture room
			830, 700, 0, 0, -10,           // the planetarium
			1024, 1020, 0, 90, 0,          // the orrery, the steps down
			1024, 1700, -128, 45, 0,       // the cellar: the cistern
			1300, 1824, -128, 0, 0,        // the hole into the alcove
			0, 1010, 0, 90, -30,           // the telescope, from under it
			300, 1312, 160, 180, -20,      // the telescope, from the gallery
			-200, 1100, 0, 47, -35,        // the telescope and the dome's roof
			-100, 1100, 0, 320, 0,         // the frame's bay
			-620, 1300, 160, 0, -10,       // the dome from the roof
			890, 640, 0, 45, -20,          // the planetarium's dome and projector
			1024, 940, 0, 270, 0,          // the planetarium from the orrery's door
			1024, 1230, 0, 270, 0,         // the orrery
			60, 800, 0, 20, 0,             // the hall's globe
			500, 2200, 0, 0, 0,            // the hill's east edge
			-700, 2200, 0, 180, 0,         // the hill's west edge
			100, 2760, 0, 0, 0,            // the knoll's east edge
			600, 2500, -128, 45, -20,      // the ravine's far corner
			-700, 1640, 160, 60, 0,        // the hill from the roof
			-700, 2330, 0, 143, -12,       // the wood's end west of the hill (no wall of firs alone in the sky)
			-300, 2330, 0, 127, -12        // the wood's end west of the knoll, across the ravine
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP05 mode 3: the level's four Stray doors, one after another, each
	// hung in the vestibule frame and walked through. (In a test the pool
	// is taken in order: the lamp room, the shed, the kiosk, and then RED's
	// far side on the bridge.) Each must be gone again afterwards.
	void LostPropertyStrays(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		if (t == 1)                                 // nobody standing in the openings
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster) a.Destroy();
		}
		int c = (t - 35) / 240, u = (t - 35) % 240;
		if (t < 35 || c > 3) return;
		AjarFrame f = FindFrame(101);
		if (u == 0) { Take(mo, 7); f.Activate(mo); Pose(mo, 384, 80, 0, 270); }
		Forward(mo, u, 5, 25);
		if (u == 40)
		{
			// the lamp room, the shed, the kiosk, and then RED's far side on the bridge
			bool there = c == 0 ? mo.pos.x > 1696 && mo.pos.x < 1920 && mo.pos.y < 240
				: c == 1 ? mo.pos.x > 1024 && mo.pos.x < 1728 && mo.pos.y > 1680 && mo.pos.y < 2192
				: c == 2 ? mo.pos.x > 528 && mo.pos.x < 656 && mo.pos.y > 1312 && mo.pos.y < 1568
				: mo.pos.z == 160 && mo.pos.x > 2000;
			Console.Printf("AJARTEST stray %d: at (%d,%d,%d)", c, mo.pos.x, mo.pos.y, mo.pos.z);
			Check(String.Format("stray%dOpensOntoItsPlace", c), there);
		}
		if (u == 200) Check(String.Format("stray%dGone", c), !f.door && !carried);
	}

	// MAP04 mode 3: sending something somewhere worse. VIOLET hangs in the
	// frame by the office; the player stands in the kennel, in view through
	// it. A baron in the yard follows them in, the player leaves by the
	// hatch and takes the door down: the baron stays in the kennel.
	Actor baron;
	void DisposalScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		if (t == 1)
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next())) if (a.bIsMonster) a.Destroy();
		}
		if (t == 35) { Take(mo, 5); FindFrame(104).Activate(mo); Pose(mo, -40, 1776, -64, 180); }
		if (t == 40) { baron = Actor.Spawn("BaronOfHell", (1300, 480, 0)); baron.angle = 90; }
		if (!baron) return;
		if (t > 40 && t % 35 == 0)
			Console.Printf("AJARTEST baron pos=(%d,%d,%d) player=(%d,%d)", baron.pos.x, baron.pos.y, baron.pos.z, mo.pos.x, mo.pos.y);
		bool caged = baron.pos.x < 240 && baron.pos.y > 1616 && baron.pos.z == -64;
		if (t == 300) Check("baronFollowsIntoKennel", caged);
		// out by the hatch (the baron cannot follow), and take the door down
		if (t == 305) Pose(mo, 180, 1672, -64, 0);
		Forward(mo, t, 310, 15);
		if (t == 340) Check("playerOutByHatch", mo.pos.z == -128 && mo.pos.x > 256);
		if (t == 345) { Pose(mo, 1456, 480, 0, 0); FindFrame(104).Activate(mo); }
		if (t == 350) Check("doorTakenDown", carried && carried.Label() == "VIOLET");
		// stand at the bars: it sees the player, and still cannot get out
		if (t == 355) Pose(mo, 300, 1840, -128, 180);
		if (t == 560) Check("baronStaysCaged", caged && baron.health > 0);
	}

	// MAP04's tour (in a function of its own: one function does not hold
	// three such tables).
	void PartyWallViews()
	{
		static const double houses[] = {
			768, -200, 0, 90, 0,        // from the start: the yard, the thief
			768, 80, 0, 180, 0,         // the gate passage, its frame
			768, 300, 0, 90, -20,       // the yard: the roof beyond
			900, 560, 0, 180, -12,      // the balcony
			700, 560, 0, 0, -12,        // the loft, the frame, the office door
			1300, 240, 0, 0, 0,         // the office door: two locks
			1300, 1000, 0, 60, 0,       // the cellar door, bolted
			500, 900, 0, 150, 0,        // the north frame
			700, 700, 0, 315, -25,      // the hole high in the south wall
			200, 112, 0, 180, 0,        // the wash house door
			-100, 112, 0, 225, 0,       // the wash house: the hole to the pantry
			-280, -40, 0, 250, 0,       // the pantry: PINK
			-60, 600, 160, 180, 0,      // on the balcony: BLUE's far side
			-128, 500, 160, 90, 0,      // the balcony: GREEN
			400, 1300, 320, 0, 0,       // on the roof
			620, 1440, 320, 0, 50,      // down the light well
			1132, 1170, 320, 270, 0,    // from the roof's edge: the target
			680, 1380, -128, 60, 0,     // in the well: the frame, the coal hole
			300, 1780, -128, 0, 0,      // the cellar
			1200, 1780, -128, 60, 0,    // the cellar: YELLOW
			320, 1840, -128, 180, -10,  // the bars of the kennel
			150, 1780, -64, 180, 0,     // in the kennel
			1472, 1560, -128, 270, -20, // the cellar stairs
			1560, 820, 192, 0, 0,       // the loft
			1800, 832, 192, 0, 0,       // the suite's door: two locks
			1960, 832, 192, 0, 0,       // the suite: VIOLET
			1620, 240, 0, 0, 0,         // the office: the landlords
			2010, 240, 0, 0, 0,         // the strongroom: RED, its frame
			1344, -40, 0, 270, 0,       // the closet
			4040, 192, 0, 0, 0,         // the store
			5030, 128, 0, 0, 0          // the way out
		};
		for (int k = 0; k < houses.Size(); k++) tourViews.Push(houses[k]);
	}

	// MAP05's tour, in two halves (see PartyWallViews).
	void LostPropertyViews1()
	{
		static const double v[] = {
			256, 64, 0, 90, 0,          // from the start
			120, 64, 0, 180, 0,         // a Stray door by the start
			384, 100, 0, 270, 0,        // the vestibule's frame
			256, 400, 0, 90, -10,       // the concourse
			400, 800, 0, 180, -20,      // the gallery
			300, 1432, 0, 0, 0,         // the kiosk behind its bars
			256, 1450, 0, 90, 0,        // the yard gate, bolted
			400, 1152, 0, 0, 0,         // the turnstile, BLUE beyond it
			480, 380, 0, 0, 0,          // platform 1
			500, 700, 0, 0, -5,         // the tracks, the train
			688, 330, 0, 270, 0,        // the waiting room's door
			690, 200, 0, 270, 0,        // the waiting room: RED
			896, 360, 0, 270, 0,        // platform 1's frame
			1088, 340, 0, 270, 0,       // the lost property office: two locks
			1020, 200, 0, 0, 0,         // in it: Stray doors
			1300, 80, 0, 0, 0,          // the hole to the lockers
			1450, 128, 0, 0, 0,         // the lockers: PINK
			4040, 192, 0, 0, 0,         // the store
			1808, 330, 0, 270, 0,       // the lamp room's door
			1808, 200, 0, 270, 0,       // the lamp room
			1950, 360, 0, 45, -20,      // the bridge from platform 1
			1952, 420, 0, 90, 20,       // the steps down to the tracks
			2100, 576, 160, 0, 0,       // on the bridge: RED's far side
			2144, 300, 160, 90, 0,      // along the bridge
			2100, 400, 160, 180, 15   // over platform 1
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void LostPropertyViews2()
	{
		static const double v[] = {
			2100, 912, 160, 180, 10,    // the train's roof
			2120, 1024, 160, 0, 0,      // the signal box's door
			2300, 1024, 160, 0, 0,      // the signal box: the lever
			2300, 1024, 160, 330, 0,    // the signal box: GREEN
			1900, 912, 112, 180, 0,     // on the roof
			1900, 1150, 0, 180, 0,      // platform 2
			1120, 1100, 0, 90, 0,       // its frame
			1440, 1100, 0, 90, 0,       // the night room's door, bolted
			912, 1100, 0, 90, 0,        // the parcels office's door, bolted
			900, 1340, 0, 90, 0,        // the parcels office
			1320, 1424, 0, 0, 0,        // the night room: the frame
			1560, 1424, 0, 180, 0,      // the night room: VIOLET's far side
			-128, 400, 192, 90, 0,      // the gallery
			-40, 800, 192, 0, 20,       // from it, the concourse
			-128, 1250, 192, 90, 0,     // the nook
			256, 1760, 0, 20, 0,        // the yard
			600, 1936, 0, 0, 0,         // the engine shed
			1100, 1936, 0, 0, 0,        // in the shed
			1376, 2040, 0, 90, 0,       // YELLOW in the shed's frame
			1900, 1900, 0, 90, -20,     // the loft from below
			1900, 2300, 160, 270, 15,   // from the loft
			1960, 2320, 160, 180, 0,    // the loft: YELLOW's far side
			448, 2060, 0, 90, 0,        // the station master's door: two locks
			448, 2260, 0, 90, 0,        // the station master's office
			592, 1340, 0, 90, 0
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// MAP06's tour, in three parts (see PartyWallViews).
	void AfterHoursViews1()
	{
		static const double v[] = {
			320, 64, 0, 90, 0,          // from the start
			448, 100, 0, 270, 0,        // the lobby's frame
			540, 280, 0, 45, 0,         // a Stray door in the lobby
			320, 420, 0, 90, -8,        // the great hall
			320, 700, 0, 180, -15,      // the mezzanine
			320, 800, 0, 135, -15,      // the upper gallery over the hall
			576, 1000, 0, 90, 0,        // the great hall's frame, the head of the steps
			-100, 992, 0, 180, 0,       // the west wing's door: one lock
			760, 672, 0, 0, 0,          // the cafe's door
			100, 192, 0, 180, 0,        // the cloakroom's door
			-150, 250, 0, 270, 0,       // the cloakroom: RED
			700, 100, 0, 45, 0,         // the gift shop
			900, 256, 0, 0, 0,          // the hole to the stockroom
			1048, 120, 0, 90, 0,        // the stockroom: PINK
			4040, 192, 0, 0, 0,         // the store
			960, 720, 0, 0, 0,          // the cafe: GREEN
			1136, 860, 0, 90, 0,        // the east wing's door: one lock
			1264, 520, 0, 270, 25,      // the steps down to the cellar
			1264, 100, -128, 90, 0,     // the cellar's door, bolted on this side
			1536, -100, -128, 270, 0,   // the cellar: GREEN's far side
			1500, -136, -128, 180, 0    // the cellar's frame
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void AfterHoursViews2()
	{
		static const double v[] = {
			1700, -256, -128, 0, 0,     // the boiler room's door
			1900, -256, -128, 0, 0,     // the boiler room
			320, 1120, 0, 90, 15,       // the steps down to the court
			320, 1400, -72, 90, -10,    // the court, the terrace beyond
			500, 1500, -72, 180, -25,   // the upper gallery from the court
			100, 1500, -72, 0, -30,     // the roof from the court
			96, 1450, -72, 270, 0,      // the grotto's door
			560, 1450, -72, 270, 0,     // the shed behind its bars
			672, 1700, -72, 90, -10,    // the steps to the terrace, the gatepost
			320, 2040, 0, 90, 0,        // the terrace: the night room's door, bolted
			600, 2100, 0, 180, 0,       // along the terrace
			-100, 1632, 160, 180, 0,    // on the upper gallery: RED's far side
			-160, 1300, 160, 90, 0,     // along it
			-160, 1300, 160, 270, 20,   // from it, the great hall
			-120, 1856, 160, 0, 25,     // from it, the court
			-120, 2112, 160, 0, 25,     // from it, the terrace
			800, 1500, 224, 90, 0,      // along the roof
			760, 1760, 224, 0, 0,       // the roof: YELLOW's far side
			760, 1632, 224, 180, 25,    // from it, the court
			800, 2180, 224, 90, 0       // the nook
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	void AfterHoursViews3()
	{
		static const double v[] = {
			-300, 640, 192, 180, 0,     // the mezzanine: VIOLET's far side
			-300, 640, 192, 0, 20,      // from it, the great hall
			-500, 900, 0, 45, 0,        // the west wing: the first room
			-540, 1300, 0, 90, 0,       // the second, and the office's door: two locks
			-800, 1400, 0, 180, 0,      // the third: the frame
			-1000, 1000, 0, 180, 0,     // the fourth: YELLOW
			-536, 1650, 0, 90, 0,       // the office: the desk, the hole behind it
			-600, 1840, 0, 150, 0,      // the office's lever
			-536, 1960, 0, 90, 0,       // the strongroom: the frame
			-600, 2050, 0, 0, 0,        // the strongroom: BLUE
			1100, 1100, 0, 45, 0,       // the east wing: the first room
			1200, 1500, 0, 90, 0,       // the second, and the archive's door: two locks
			1500, 1600, 0, 0, 0,        // the third: VIOLET
			1660, 1340, 0, 270, 0,      // the fourth
			1200, 1900, 0, 90, 0,       // the archive: Stray doors
			280, 2384, 0, 0, 0,         // the night room: the frame
			400, 2384, 0, 180, 0        // the night room: BLUE's far side
		};
		for (int k = 0; k < v.Size(); k++) tourViews.Push(v[k]);
	}

	// Mode 2 in MAP02 and MAP03: a tour, as BorrowedRoomsTour. Each view is
	// x, y, z, angle, pitch.
	Array<double> tourViews;
	void Tour(Actor mo, int t)
	{
		if (!tourViews.Size())
		{
			static const double hotel[] = {
				256, 96, 0, 90, -12,        // lobby: the balcony, VIOLET, the gap in the rail
				330, 280, 0, 140, 0,        // lobby: the reception desk
				200, 300, 0, 325, 0,        // lobby: the front doors
				380, 100, 0, 180, 0,        // lobby: the sofa, the mouth of the hall
				-100, 224, 0, 180, 0,       // the hall
				-224, 328, 0, 90, 0,        // room 101: bed, windows
				-432, 420, 0, 90, 15,       // its bathroom
				-224, 120, 0, 270, 0,       // room 102
				-672, 110, 0, 270, 0,       // room 104: RED
				-1120, 250, 0, 270, 0,      // room 106's door: one lock
				-1120, 330, 0, 90, 0,       // suite 105: sitting room
				-1120, 600, 0, 90, 0,       // suite 105: bedroom
				-1328, 440, 0, 90, 15,      // suite 105: the bath, key 3
				-1500, 224, 0, 180, 0,      // dining room
				-1664, 600, 0, 90, 0,       // kitchen: the frame
				540, 224, 144, 0, 0,        // upstairs hall
				832, 330, 144, 90, 0,       // room 201
				1040, 420, 144, 90, 15,     // its bathroom: key 4
				1344, 190, 144, 90, 0,      // room 203's door: two locks
				1300, 600, 144, 45, 0,      // suite 203: GREEN in the bedroom
				1820, 224, 304, 0, 0,       // attic: key 1
				4240, 160, 0, 0, 0,         // cellar: the frame, key 2
				3060, 224, 128, 0, 12,      // terrace, down into the garden
				300, 520, 112, 270, 20,     // balcony: the gap in the rail
				5030, 128, 0, 0, 0          // the way out
			};
			static const double theatre[] = {
				-200, 1352, 0, 0, 0,        // foyer from the start
				0, 1500, 0, 200, 0,         // foyer: box office, cloakroom door, frame
				-256, 1560, 0, 90, 0,       // office door: one lock
				-256, 1730, 0, 90, 0,       // office: PINK hanging, the store beyond
				-700, 1228, 0, 180, 0,      // cloakroom: VIOLET
				300, 1520, 0, 0, 0,         // bar: BLUE, the bolted stairs door
				128, 940, 0, 300, -5,       // stalls from the way in
				40, 448, 0, 0, -8,          // down the aisle to the stage
				900, 448, 0, 180, -20,      // back of the house: the gods
				900, 300, 0, 60, -20,       // the dress circle
				1100, 600, -48, 20, 0,      // the pit: the grate
				680, 1000, 128, 0, 5,       // on the circle
				384, 1100, 128, 90, 30,     // down its stairs
				-420, 448, 224, 0, 12,      // from the gods
				-300, 600, 224, 105, 0,     // gods: YELLOW's far side, open
				-200, 448, 224, 180, 0,     // gods: the booth's door and window
				-500, 448, 224, 180, 0,     // in the booth
				1700, -96, 288, 180, 10,    // flies and the bridge
				1472, -40, 288, 90, 35,     // from the flies, down onto the stage
				1700, 300, 64, 150, 15,     // on the stage: the room under it
				1296, 860, -64, 270, 0,     // under the stage: GREEN
				1200, 1024, 64, 0, 0,       // backstage corridor
				1920, 1024, 64, 90, 0,      // the star's door: two locks
				1920, 1130, 64, 90, 0,      // the star's room: RED
				2140, 1024, 64, 0, 0,       // green room
				4040, 192, 0, 0, 0,         // property store
				5030, 128, 0, 0, 0          // the way out
			};
			if (level.mapname ~== "MAP04") PartyWallViews();
			else if (level.mapname ~== "MAP05") { LostPropertyViews1(); LostPropertyViews2(); }
			else if (level.mapname ~== "MAP06") { AfterHoursViews1(); AfterHoursViews2(); AfterHoursViews3(); }
			else if (level.mapname ~== "MAP07") { SmallHoursViews1(); SmallHoursViews2(); SmallHoursViews3(); }
			else if (level.mapname ~== "MAP08") { ClosingTimeViews1(); ClosingTimeViews2(); ClosingTimeViews3(); ClosingTimeViews4(); }
			else if (level.mapname ~== "MAP09") { PuttingThroughViews1(); PuttingThroughViews2(); PuttingThroughViews3(); }
			else if (level.mapname ~== "MAP10") { AllChangeViews1(); AllChangeViews2(); }
			else if (level.mapname ~== "MAP31") SecretOneViews();
			else if (level.mapname ~== "MAP11") ByAppointmentViews();
			else if (level.mapname ~== "MAP13") SightUnseenViews();
			else if (level.mapname ~== "MAP14") OnTheLevelViews();
			else if (level.mapname ~== "MAP15") OnReflectionViews();
			else if (level.mapname ~== "MAP16") WatchYourStepViews();
			else if (level.mapname ~== "MAP02") for (int k = 0; k < hotel.Size(); k++) tourViews.Push(hotel[k]);
			else for (int k = 0; k < theatre.Size(); k++) tourViews.Push(theatre[k]);
		}
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		int i = t / 40;
		if (i >= tourViews.Size() / 5) return;
		Pose(mo, tourViews[i * 5], tourViews[i * 5 + 1], tourViews[i * 5 + 2], tourViews[i * 5 + 3]);
		mo.pitch = tourViews[i * 5 + 4];
		if (t % 40 == 0)
		{
			int n = 0;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0) n++;
			Console.Printf("AJARTEST view=%d monsters=%d secrets=%d", i, n, level.total_secrets);
		}
	}

	// MAP01 mode 3: shooting through the level's own doors.
	void BorrowedRoomsShoot(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); }
		if (t == 40) ShootProbe(mo, "cellToHall", 128, -1340, 0, 90, 300, 320, 0);
		if (t == 50) ShootProbe(mo, "hallToCell", 300, 320, 0, 180, 128, -1400, 0);
		if (t == 60) ShootProbe(mo, "pitToLedge", 896, 500, -192, 90, 1100, 320, 0);
		if (t == 70) ShootProbe(mo, "ledgeToPit", 1100, 320, 0, 0, 896, 400, -192);
		if (t == 80) { shootee.Destroy(); Pose(mo, 128, -1340, 0, 90); }
		if (t > 80) { mo.angle = 90; mo.pitch = 0; }
	}

	// MAP01 mode 4: do the level's monsters come through a door, and can you
	// shoot yourself? First RED hangs in the cell and the player waits there
	// for the hall's zombies. Then RED goes into the hall frame, so the frame
	// shows the hall from RED's far side, and every spot in the hall is tried
	// at every angle.
	double waitX, waitY;
	void BorrowedRoomsSelf(PlayerPawn mo, int t)
	{
		if (t < 605) mo.player.cheats |= CF_GODMODE;
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 128, -1420, 0, 90); }
		if (t == 36)
		{
			// from how much of the cell does some monster notice you through the door?
			int spots = 0, seenSpots = 0;
			for (double x = 24; x < 256; x += 16) for (double y = -1476; y < -1250; y += 16)
			{
				Pose(mo, x, y, 0, 90);
				spots++;
				bool seen = false;
				let it = ThinkerIterator.Create("Actor");
				Actor a;
				while (!seen && (a = Actor(it.Next())))
					if (a.bIsMonster && a.health > 0) seen = AjarSight.DoorImage(a, mo);
				if (seen) { seenSpots++; if (y < -1380) { waitX = x; waitY = y; } }
			}
			Console.Printf("AJARTEST cellSpots=%d noticedFrom=%d waitAt=(%d,%d)", spots, seenSpots, waitX, waitY);
			Pose(mo, waitX, waitY, 0, 90);
		}
		if (t > 35 && t < 600) { mo.angle = 90; mo.pitch = 0; }
		if (t >= 35 && t <= 600 && t % 70 == 0)
		{
			int awake = 0, inCell = 0;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (!a.bIsMonster || a.health <= 0) continue;
				if (a.target) awake++;
				if (a.pos.y < -1200) inCell++;
				if (a.target) Console.Printf("AJARTEST   %s at (%d,%d)", a.GetClassName(), a.pos.x, a.pos.y);
			}
			Console.Printf("AJARTEST t=%d awake=%d inCell=%d", t, awake, inCell);
			if (t == 560) Check("monsterComesIntoCell", inCell > 0);
		}
		if (t == 605)
		{
			// the rest is about your own bullets: no monsters, no god mode
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) a.Destroy();
			mo.player.cheats &= ~CF_GODMODE;
			mo.health = mo.player.health = 100;
			Take(mo, 1); Pose(mo, 384, 60, 0, 270); FindFrame(102).Activate(mo);
		}
		if (t == 610)
		{
			int spots = 0, hits = 0;
			for (double x = 32; x < 768; x += 32) for (double y = 32; y < 640; y += 32)
			{
				Pose(mo, x, y, 0, 0);
				bool any = false;
				for (double a = 0; a < 360; a += 0.5)
				{
					if (!SelfShot(mo, a, 0)) continue;
					if (!hits) { waitX = x; waitY = y; selfAng = a + 1; }
					hits++;
					any = true;
				}
				if (any) spots++;
			}
			Console.Printf("AJARTEST selfSpots=%d selfAngles=%d first=(%d,%d,%.1f)", spots, hits, waitX, waitY, selfAng);
			Check("canAimAtSelfInHall", hits > 0);
		}
		// the pistol is fired by tools/smoke_MAP01_4.cfg
		if (t >= 610 && t < 720) { Pose(mo, waitX, waitY, 0, selfAng); mo.pitch = 0; }
		if (t == 715) Check("pistolHitsSelfInHall", mo.health < 100);
	}

	// MAP01 mode 2: stand in each room in turn, unseen and unhurt, so that
	// tools/smoke_MAP01_2.cfg can photograph monsters and decoration.
	void BorrowedRoomsTour(Actor mo, int t)
	{
		static const double views[] = {
			128, -1470, 0, 90, 0,       // cell: the frame
			230, -1270, 0, 225, 0,      // cell: back from the frame corner
			40, 320, 0, 0, 0,           // hall from the RED far side
			720, 600, 0, 215, 0,        // hall: niches, frame, torches
			384, 600, 0, 270, 0,        // hall: the south wall square on
			288, 170, 0, 270, 0,        // hall: a picture and a niche, close
			384, 60, 0, 90, -15,        // hall, looking up at the gallery
			740, 320, 0, 0, 30,         // down into the pit, ledge beyond
			1000, 150, -192, 100, -6,   // in the pit: YELLOW hanging
			896, 560, -192, 270, -25,   // in the pit, looking up and out
			1060, 40, 0, 65, 0,         // ledge
			1100, 320, 0, 180, 5,       // ledge: back across the pit to hall and gallery
			40, 736, 160, 0, 0,         // gallery
			740, 736, 160, 180, 0,      // gallery from the far end
			384, 680, 160, 90, 0,       // gallery: BLUE's far side, pictures
			384, 700, 160, 270, 25,     // gallery: down into the hall
			2030, 160, 0, 0, 0,         // vault
			2290, 290, 0, 215, 0,       // vault: back to GREEN's far side
			3030, 128, 0, 0, 0,         // way out
			3290, 30, 0, 160, 0,        // way out: back to VIOLET's far side
			3200, 128, 0, 0, 0,         // way out: the door, close
			3210, 40, 0, 40, 0          // way out: the door from one side
		};
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		int i = t / 40;
		if (i >= views.Size() / 5) return;
		Pose(mo, views[i * 5], views[i * 5 + 1], views[i * 5 + 2], views[i * 5 + 3]);
		mo.pitch = views[i * 5 + 4];
		if (t % 40 == 0)
		{
			int n = 0;
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0) n++;
			Console.Printf("AJARTEST view=%d monsters=%d secrets=%d", i, n, level.total_secrets);
		}
	}

	void Pose(Actor mo, double x, double y, double z, double ang)
	{
		mo.SetOrigin((x, y, z), false);
		mo.angle = ang;
		mo.vel = (0, 0, 0);
	}

	// Portals turn the player, so "forward" keeps working on the far side.
	void Forward(Actor mo, int t, int from, int tics)
	{
		if (t > from && t <= from + tics) mo.vel.xy = (cos(mo.angle), sin(mo.angle)) * 8;
	}

	void Take(Actor mo, int colour)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.args[1] == colour) d.Used(mo);
	}

	void Check(string what, bool ok)
	{
		Console.Printf("AJARTEST %s=%d", what, ok);
	}

	// The shortest solution of MAP01 as printed by tools/build.py.
	void BorrowedRoomsScript(Actor mo, int t)
	{
		string have = carried ? carried.Label() : "-";
		// cell: take RED, hang it, walk through into the hall
		if (t == 35) { Take(mo, 1); FindFrame(101).Activate(mo); Pose(mo, 128, -1340, 0, 90); }
		Forward(mo, t, 40, 35);
		if (t == 80) Check("inHall", mo.pos.x > 0 && mo.pos.x < 768 && mo.pos.y > 0 && mo.pos.y < 640);
		// step off the edge into the pit
		if (t == 105) Pose(mo, 700, 320, 0, 0);
		Forward(mo, t, 110, 15);
		if (t == 170) Check("inPit", mo.pos.z == -192);
		// through YELLOW up to the ledge, take BLUE, drop back in
		if (t == 175) Pose(mo, 896, 560, -192, 90);
		Forward(mo, t, 180, 25);
		if (t == 210) Check("onLedge", mo.pos.x > 1024 && mo.pos.z == 0);
		if (t == 245) { Take(mo, 2); Pose(mo, 1080, 320, 0, 180); }
		Forward(mo, t, 250, 15);
		if (t == 310) Check("inPitWithBlue", mo.pos.z == -192 && have == "BLUE");
		// swap YELLOW for BLUE, through to the gallery
		if (t == 315) { Pose(mo, 896, 560, -192, 90); FindFrame(103).Activate(mo); }
		Forward(mo, t, 350, 25);
		if (t == 380) Check("onGalleryWithYellow", mo.pos.z == 160 && mo.pos.y > 640 && have == "YELLOW");
		// hang YELLOW up here, take GREEN, drop into the hall
		if (t == 385) { FindFrame(104).Activate(mo); Take(mo, 3); Pose(mo, 384, 700, 160, 270); }
		Forward(mo, t, 420, 15);
		if (t == 480) Check("inHallWithGreen", mo.pos.z == 0 && mo.pos.y < 640 && have == "GREEN");
		// hang GREEN in the hall frame, fetch VIOLET from the vault
		if (t == 485) { FindFrame(102).Activate(mo); Pose(mo, 384, 100, 0, 270); }
		Forward(mo, t, 520, 25);
		if (t == 550) Check("inVault", mo.pos.x > 1900 && mo.pos.x < 2400);
		if (t == 555) { Take(mo, 5); Pose(mo, 2100, 160, 0, 180); }
		Forward(mo, t, 590, 25);
		if (t == 620) Check("backInHallWithViolet", mo.pos.x < 768 && mo.pos.y < 640 && have == "VIOLET");
		// swap GREEN for VIOLET and leave
		if (t == 625) { FindFrame(102).Activate(mo); Pose(mo, 384, 100, 0, 270); }
		Forward(mo, t, 660, 25);
		if (t == 690) Check("inExitRoom", mo.pos.x > 2900);
		// the way out is walked into
		if (t == 695) Pose(mo, 3290, 128, 0, 0);
		Forward(mo, t, 725, 10);
	}

	// MODE=3: things other than the player through a hung door (M3 proof).
	// RED hangs in frame 101 from the start; its far side is the red room.
	Actor probe, shot;
	bool shotPassed;

	void ThingsScript(Actor mo, int t)
	{
		// a projectile fired at the door from the hall
		if (t == 40)
		{
			shot = Actor.Spawn("AjarProbeShot", (160, 300, 32));
			shot.target = mo;
			shot.angle = 90;
			shot.vel = (0, 10, 0);
		}
		if (shot && shot.pos.y > 1500) shotPassed = true;
		if (t == 105) Check("projectileThrough", shotPassed);
		// a monster-like actor pushed at the door
		if (t == 110) probe = Actor.Spawn("AjarProbe", (160, 400, 0));
		if (probe && t > 110 && t < 180) probe.vel.xy = (0, 8);
		if (t == 185 && probe)
		{
			Console.Printf("AJARTEST probe pos=(%d,%d,%d)", probe.pos.x, probe.pos.y, probe.pos.z);
			Check("actorThrough", probe.pos.y > 1500);
		}
		// a hitscan from the hall at the probe standing on the far side
		if (t == 190) Pose(mo, 160, 400, 0, 90);
		if (t == 195) mo.LineAttack(90, 4096, 0, 10, 'Hitscan', "AjarProbePuff");
		if (t == 200 && probe) Check("hitscanThrough", probe.health < probe.SpawnHealth());
	}

	// MODE=8: the player's own pistol, fired by real key presses from
	// tools/smoke_TEST_8.cfg, at a zombie standing beyond the hung RED door.
	Actor shootee;

	void ShootScript(Actor mo, int t)
	{
		if (t == 1) mo.player.cheats |= CF_NOTARGET | CF_GODMODE;
		if (t == 40)
		{
			Pose(mo, 160, 400, 0, 90);
			shootee = Actor.Spawn("ZombieMan", (192, 2200, 0));
			shootee.angle = 0;
		}
		if (t > 40 && t < 200) { mo.angle = 90; mo.pitch = 0; }
		if (t >= 40 && t % 20 == 0 && t <= 200)
		{
			FTranslatedLineTarget lt;
			mo.AimLineAttack(90, 4096, lt);
			Console.Printf("AJARTEST shoot t=%d zombieHealth=%d aim=%s ammo=%d", t, shootee ? shootee.health : -1,
				lt.linetarget ? lt.linetarget.GetClassName() : 'none', mo.CountInv("Clip"));
		}
		if (t == 200) Check("pistolThroughDoor", !shootee || shootee.health < 20);
		// the same by script from other places: back through the far side,
		// at a slant, and through the pit frame (different floor heights)
		if (t == 210) ShootProbe(mo, "reverse", 192, 2200, 0, 270, 160, 300, 0);
		if (t == 220) ShootProbe(mo, "slant", 100, 300, 0, VectorAngle(60, 228), 249, 2200, 0);
		if (t == 230) ShootProbe(mo, "slantNear", 100, 470, 0, VectorAngle(60, 58), 300, 2100, 0);
		if (t == 240) ShootProbe(mo, "pitToGreen", 752, 400, -128, 90, 2200, 2128, 0);
		if (t == 250) ShootProbe(mo, "greenToPit", 2200, 2128, 0, 180, 752, 300, -128);
	}

	void ShootProbe(Actor mo, string what, double x, double y, double z, double ang, double tx, double ty, double tz)
	{
		if (shootee) shootee.Destroy();
		Pose(mo, x, y, z, ang);
		mo.pitch = 0;
		shootee = Actor.Spawn("AjarProbe", (tx, ty, tz));
		FTranslatedLineTarget lt;
		mo.AimLineAttack(ang, 4096, lt);
		mo.LineAttack(ang, 4096, 0, 10, 'Hitscan', "AjarProbePuff");
		Console.Printf("AJARTEST %s=%d autoaim=%d", what, shootee.health < 1000, lt.linetarget == shootee);
	}

	// MODE=9: shooting yourself. BLUE hangs in the ledge frame; its far side
	// is in the ledge's north wall, so from in front of the frame you can
	// see yourself at a slant. Key presses come from tools/smoke_TEST_9.cfg:
	// pistol at yourself, pistol at a blank wall, plasma at yourself.
	double selfAng;
	int selfHealth;

	void SelfShotScript(PlayerPawn mo, int t)
	{
		if (t == 35) { Take(mo, 2); FindFrame(105).Activate(mo); Pose(mo, 1070, 256, 0, 0); mo.pitch = 0; }
		if (t == 40)
		{
			selfAng = 1000;
			for (double a = -45; a <= 45 && selfAng == 1000; a += 0.5)
				if (SelfShot(mo, a, 0)) selfAng = a + 1.5;       // a little inside the edge
			Console.Printf("AJARTEST selfAng=%d", selfAng);
			Check("canAimAtSelf", selfAng != 1000);
		}
		if ((t > 40 && t <= 125) || t >= 195) { mo.angle = selfAng; mo.pitch = 0; }
		if (t == 125) { Check("pistolHitsSelf", mo.health < 100); selfHealth = mo.health; }
		if (t > 125 && t < 195) { mo.angle = 180; mo.pitch = 0; }
		if (t == 192) Check("noSelfHitAtAWall", mo.health == selfHealth);
		if (t == 195)
		{
			mo.health = mo.player.health = 500;
			mo.GiveInventory("PlasmaRifle", 1);
			mo.GiveInventory("Cell", 40);
			mo.player.PendingWeapon = Weapon(mo.FindInventory("PlasmaRifle"));
		}
		if (t == 290) Check("plasmaHitsSelf", mo.health < 500);
	}

	// MAP01 mode 5: the demon in the pit. YELLOW hangs in the pit from the
	// start and leads to the ledge. The player stands on the ledge, in plain
	// view of the pit but out of its reach: the demon has to come by the door.
	Actor pinky;
	void BorrowedRoomsPit(PlayerPawn mo, int t)
	{
		if (t < 600) mo.player.cheats |= CF_GODMODE;
		if (t == 35)
		{
			Pose(mo, 1100, 320, 0, 180);
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			Array<Actor> others;
			while (a = Actor(it.Next()))
			{
				if (a is "Demon") pinky = a;
				else if (a.bIsMonster) others.Push(a);
			}
			for (int k = 0; k < others.Size(); k++) others[k].Destroy();     // nobody else in the way
		}
		if (t > 35 && t < 600) { mo.angle = 180; mo.vel = (0, 0, 0); }
		if (t > 35 && t % 35 == 0 && pinky)
		{
			bool seen; Vector2 img; Line src;
			[seen, img, src] = AjarSight.DoorImage(pinky, mo);
			String tg = "none";
			if (pinky.target) tg = pinky.target.GetClassName();
			Console.Printf("AJARTEST pinky pos=(%d,%d,%d) sight=%d door=%d target=%s", pinky.pos.x, pinky.pos.y, pinky.pos.z,
				pinky.CheckSight(mo), seen, tg);
		}
		if (t == 560) Check("demonComesByTheDoor", pinky && pinky.pos.z == 0 && pinky.pos.x > 1024);
	}

	// MODE=4: an ordinary Doom monster in the hall notices a player standing
	// beyond the hung RED door and walks through it after them.
	Actor zombie;

	void FollowScript(Actor mo, int t)
	{
		if (t == 40) { Pose(mo, 192, 2300, 0, 270); zombie = Actor.Spawn("ZombieMan", (160, 200, 0)); zombie.angle = 0; }
		if (t == 80) Check("monsterWakesThroughDoor", zombie.target != null);
		if (t > 40 && t % 35 == 0 && zombie)
			Console.Printf("AJARTEST zombie pos=(%d,%d,%d) health=%d", zombie.pos.x, zombie.pos.y, zombie.pos.z, mo.health);
		if (t == 400) Check("monsterFollowsThroughDoor", zombie.pos.y > 1900);
		if (t == 400) Check("monsterTargetsPlayerAgain", zombie.target == mo);
	}

	// MODE=5: the thief, from where it stands in the test box, with its
	// random choices switched off. It takes the hung RED door (not GREEN down
	// in the pit, which it cannot walk to) and hangs it in another frame; a
	// second one takes a door, is killed, drops it, and the player picks it
	// up; a third walks through a hung door and back.
	AjarThief thief;
	int killTic;
	bool tookRed, hungElsewhere, wentThrough, cameBack;
	AjarDoor lootAtDeath;

	AjarDoor DoorOf(int colour)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.args[1] == colour) return d;
		return null;
	}

	void ThiefScript(Actor mo, int t)
	{
		AjarDoor red = DoorOf(1);
		if (t == 40) { Pose(mo, 96, 256, 0, 0); thief = AjarThief(Actor.Spawn("AjarThief", (560, 150, 0))); thief.testMode = 1; }
		if (t > 40 && t % 35 == 0 && thief)
			Console.Printf("AJARTEST thief pos=(%d,%d,%d) loot=%s red=%d", thief.pos.x, thief.pos.y, thief.pos.z,
				thief.loot ? thief.loot.Label() : "-", red.frame ? red.frame.args[0] : 0);
		if (t < 700 && thief && thief.loot == red && !FindFrame(101).door) tookRed = true;
		if (t == 700) Check("thiefTakesDoor", tookRed);
		if (t < 700 && red.frame && red.frame.args[0] != 101) hungElsewhere = true;
		if (t == 700) Check("thiefHangsItElsewhere", hungElsewhere);
		// A second thief (the first may have wandered off through the door it
		// hung): once it has a door on its back, kill it.
		if (t == 705)
		{
			thief.Destroy();
			thief = AjarThief(Actor.Spawn("AjarThief", (560, 150, 0))); thief.testMode = 1;
		}
		if (t > 705 && !killTic && thief.loot)
		{
			Check("thiefTakesAgain", true);
			killTic = t;
			lootAtDeath = thief.loot;
			thief.DamageMobj(null, null, 1000, 'None');
		}
		if (killTic && t == killTic + 20)
		{
			Check("thiefDropsDoor", !lootAtDeath.carried && !lootAtDeath.bInvisible && lootAtDeath.Distance2D(thief) < 8);
			lootAtDeath.Used(mo);
		}
		if (killTic && t == killTic + 25) Check("playerRecoversDoor", carried == lootAtDeath);
		// A third thief that only wants to walk through doors: the player
		// hangs the door back, it goes through to the red room and returns.
		if (killTic && t == killTic + 26)
		{
			// (an earlier thief may have hung BLUE somewhere on its own; put it
			// down again so that RED is the only way through)
			AjarDoor blue = DoorOf(2);
			if (blue.frame) { Unhang(blue.frame); DropDoor(blue, blue); }
			FindFrame(101).Activate(mo);
		}
		if (killTic && t == killTic + 30)
		{
			thief = AjarThief(Actor.Spawn("AjarThief", (300, 300, 0)));
			thief.testMode = 2;
		}
		if (killTic && t > killTic + 30 && thief)
		{
			if (t % 10 == 0)
				Console.Printf("AJARTEST walker t=%d pos=(%d,%d) job=%d crossing=%d lined=%d steps=%d spot=(%d,%d)", t, thief.pos.x, thief.pos.y,
					thief.jobLine != null, thief.crossing, thief.lined, thief.steps, thief.spot ? thief.spot.pos.x : 0, thief.spot ? thief.spot.pos.y : 0);
			if (thief.pos.y > 1900) wentThrough = true;
			if (wentThrough && thief.pos.y < 600 && thief.pos.x < 640) cameBack = true;
		}
		if (killTic && t == killTic + 600)
		{
			Check("thiefWalksThroughDoor", wentThrough);
			Check("thiefComesBackThroughIt", cameBack);
		}
	}

	// MODE=6: the nailer nails the hung RED door; the player cannot take it
	// until the nailer is dead.
	Actor nailer;

	void NailerScript(Actor mo, int t)
	{
		AjarDoor red = DoorOf(1);
		if (t == 40) { Pose(mo, 96, 256, 0, 0); nailer = Actor.Spawn("AjarNailer", (400, 300, 0)); }
		if (t > 40 && t % 35 == 0 && nailer)
			Console.Printf("AJARTEST nailer pos=(%d,%d) nailed=%d health=%d", nailer.pos.x, nailer.pos.y, red.nailer != null, mo.health);
		if (t == 300) Check("nailerNailsDoor", red.nailer == nailer);
		if (t == 300) Pose(mo, 160, 360, 0, 90);      // look at the nailed door for the screenshot
		if (t == 305) FindFrame(101).Activate(mo);
		if (t == 306) Check("nailedDoorCannotBeTaken", !carried && red.frame && red.frame.args[0] == 101);
		if (t == 310) nailer.DamageMobj(null, null, 1000, 'None');
		if (t == 330) Check("nailsFallOutWhenItDies", !red.nailer);
		if (t == 331) FindFrame(101).Activate(mo);
		if (t == 332) Check("doorCanBeTakenAgain", carried == red);
	}

	// MODE=7: the lodger. It starts inside, comes out of an empty hall frame,
	// goes back in; with every hall frame plugged it stays in; with one freed
	// it comes out again.
	AjarLodger lodger;
	bool cameOut, wasHit, wentBack, cameOutPlugged, cameOutAgain;
	int plugTic;

	void LodgerScript(Actor mo, int t)
	{
		if (t == 40) { Pose(mo, 96, 256, 0, 0); lodger = AjarLodger(Actor.Spawn("AjarLodger", (300, 100, 0))); }
		if (!lodger) return;
		if (t == 45) Check("lodgerStartsInside", lodger.bInvisible && !lodger.bShootable);
		if (t % 35 == 0)
			Console.Printf("AJARTEST lodger pos=(%d,%d) inside=%d health=%d dist=%d melee=%d sight=%d", lodger.pos.x, lodger.pos.y, lodger.inside, mo.health, lodger.Distance2D(mo), lodger.CheckMeleeRange(), lodger.CheckSight(mo));
		if (cameOut && !wentBack && mo.health < 100) wasHit = true;
		if (wentBack) mo.health = mo.player.health = 100;      // from here on the player only watches
		bool atHallFrame = lodger.pos.x > 380 && lodger.pos.x < 520 && (lodger.pos.y > 440 || lodger.pos.y < 72);
		if (!lodger.inside && !cameOut && atHallFrame) cameOut = true;
		if (cameOut && lodger.inside && !wentBack)
		{
			wentBack = true;
			plugTic = t;
			Check("lodgerComesOutOfEmptyFrame", true);
			Check("lodgerGoesBackIn", true);
			Check("lodgerHitsPlayer", wasHit);
			// plug both empty hall frames with GREEN and BLUE (101 holds RED)
			Take(mo, 3); FindFrame(102).Activate(mo);
			Take(mo, 2); FindFrame(103).Activate(mo);
		}
		if (t == 900 && !wentBack) { Check("lodgerComesOutOfEmptyFrame", cameOut); Check("lodgerGoesBackIn", false); }
		if (!plugTic) return;
		if (t < plugTic + 400 && !lodger.inside) cameOutPlugged = true;
		if (t == plugTic + 400)
		{
			Check("pluggedFramesKeepItIn", !cameOutPlugged);
			FindFrame(103).Activate(mo);         // take BLUE down again
		}
		if (t > plugTic + 400 && !lodger.inside) cameOutAgain = true;
		if (t == plugTic + 800) Check("freedFrameLetsItOut", cameOutAgain);
	}

	// MODE=10: three of Doom's monsters, awake in the hall and none of them
	// in front of the RED door, when the player leaves through it and steps
	// out of view. All three have to follow, and none may attack its lure.
	Actor crowd[3];
	int lureAttacks;

	void CrowdScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		if (t == 40)
		{
			Pose(mo, 96, 256, 0, 0);
			crowd[0] = Actor.Spawn("DoomImp", (400, 300, 0));
			crowd[1] = Actor.Spawn("Demon", (300, 120, 0));
			crowd[2] = Actor.Spawn("ZombieMan", (520, 400, 0));
			for (int i = 0; i < 3; i++) crowd[i].angle = 180;
		}
		if (t < 40) return;
		if (t == 75) Pose(mo, 160, 470, 0, 90);
		Forward(mo, t, 76, 12);
		if (t == 100) mo.angle = 135;
		Forward(mo, t, 100, 25);
		int through = 0;
		for (int i = 0; i < 3; i++)
		{
			Actor a = crowd[i];
			if (!a) continue;
			if (a.pos.y > 1900) through++;
			if (a.target is "AjarLure" && (a.InStateSequence(a.CurState, a.MeleeState) || a.InStateSequence(a.CurState, a.MissileState)))
				lureAttacks++;
			if (t % 35 == 0)
				Console.Printf("AJARTEST   %s at (%d,%d) target=%s", a.GetClassName(), a.pos.x, a.pos.y, a.target ? a.target.GetClassName() : 'none');
		}
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d through=%d lureAttacks=%d", t, through, lureAttacks);
		if (t == 700)
		{
			Check("crowdFollowsThroughDoor", through == 3);
			Check("nobodyAttacksItsLure", lureAttacks == 0);
		}
	}

	// MODE=11: the Stray door. Hung in the hall it opens onto the first place
	// of the pool (the green room); the player goes through; a probe is left
	// standing in the opening; when the time is up the door is gone, the
	// frame is empty, the place is a wall again and the probe is dead.
	void StrayScript(Actor mo, int t)
	{
		AjarFrame f = FindFrame(102);
		if (t == 35) { Take(mo, 7); f.Activate(mo); }
		if (t == 36) Check("strayOpensOntoAPlace", f.door && f.door.IsStray() && f.door.args[0] == STRAY_ID && StrayTime() > 0);
		if (t == 37) { f.Activate(mo); Check("openStrayCannotBeTaken", !carried && f.door); }
		if (t == 40) Pose(mo, 448, 400, 0, 90);
		Forward(mo, t, 45, 25);
		if (t == 80) Check("throughStray", mo.pos.x > 2000 && mo.pos.x < 2320 && mo.pos.y > 2000 && mo.pos.y < 2260);
		if (t == 100) probe = Actor.Spawn("AjarProbe", (448, 520, 0));
		if (t == 205) Check("stillOpenBeforeTime", f.door != null && probe && probe.health > 0);
		if (t == 215)
		{
			Check("strayGone", !f.door && !DoorOf(7));
			Check("placeShutAgain", (FindLine(STRAY_ID).flags & Line.ML_BLOCKING) && (FindLine(102).flags & Line.ML_BLOCKING));
			Check("telefragged", !probe || probe.health <= 0);
		}
	}

	// MODE=12: building the way out. With YELLOW in hand in the night room,
	// walking into the empty frame does nothing; hung there, YELLOW opens
	// onto the room it hangs in, cannot be taken again, and walking into it
	// ends the level.
	void HomeScript(Actor mo, int t)
	{
		AjarFrame f = FindFrame(190);
		if (t == 35) { Take(mo, 4); Pose(mo, 3200, 2128, 0, 0); }
		Forward(mo, t, 40, 25);
		if (t == 70) Check("noWayOutYet", mo.pos.x > 3300 && !wayOutBuilt && carried);
		if (t == 75) { f.Activate(mo); Check("wayOutBuilt", wayOutBuilt && f.door && f.door.nailer == f.door && !carried); }
		if (t == 76) { f.Activate(mo); Check("itStays", f.door && !carried); }
		if (t == 80) Pose(mo, 3100, 2128, 0, 0);
		Forward(mo, t, 130, 40);
	}

	// MODE=13: the way out that turns you round (ajarmap.way_round). The
	// fixed pair in the west wall brings you back into the room; VIOLET hung
	// beside its own far side makes all four openings ways out.
	void RoundScript(Actor mo, int t)
	{
		AjarFrame f = FindFrame(191);
		if (t == 35) Pose(mo, 4200, 2064, 0, 180);         // shot 1: the fixed pair, nothing built
		Forward(mo, t, 70, 30);
		if (t == 105) Check("turnedRound", mo.pos.x > 4000 && mo.pos.x < 4320 && mo.pos.y > 2160 && abs(Actor.DeltaAngle(mo.angle, 0)) < 1 && !wayOutBuilt);
		if (t == 110) { Take(mo, 5); Pose(mo, 4290, 2192, 0, 0); }
		if (t == 115) { f.Activate(mo); Check("wayOutBuilt", wayOutBuilt && f.door && !carried); }
		if (t == 120) Pose(mo, 4200, 2064, 0, 180);        // shot 2: west, built
		if (t == 180) Pose(mo, 4120, 2064, 0, 0);          // shot 3: east, built
		if (t == 240) Pose(mo, 4250, 2100, 0, 170);        // shot 4: off the axis
		Forward(mo, t, 300, 40);
	}

	// The lab (map LAB, tools/map_lab.py; MAP=LAB tools/smoke.sh): the Pair
	// door. Frames 111 west and 112 east face each other, 113 is round the
	// corner from 112, 114 and 115 are side by side, 116 is on the gallery.
	AjarDoor LabLeaf(int colour, int n)
	{
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next())) if (d.args[1] == colour && !n--) return d;
		return null;
	}

	void LabScript(Actor mo, int t)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		AjarFrame w = FindFrame(111), e = FindFrame(112), c = FindFrame(113), s1 = FindFrame(114), s2 = FindFrame(115), g = FindFrame(116);
		// 1: one leaf alone is shut; both hung, the endless corridor
		if (t == 20) { Pose(mo, 120, 128, 0, 180); a.Used(mo); }
		if (t == 22) { w.Activate(mo); Check("aloneShut", a.frame == w && a.Shut() && a.bInvisible && !carried && (FindLine(111).flags & Line.ML_BLOCKING)); }
		if (t == 30) Pose(mo, 200, 128, 0, 180);                       // shot: the shut leaf
		if (t == 145) { b.Used(mo); Check("tookTwin", carried == b); }
		if (t == 147) Check("stillShut", TexMan.GetName(FindLine(111).sidedef[0].GetTexture(Side.mid)) ~== "AJDR8");
		if (t == 150) { Pose(mo, 700, 128, 0, 0); e.Activate(mo); Check("linked", a.args[0] == 112 && b.args[0] == 111 && !a.bInvisible && !b.bInvisible && !(FindLine(111).flags & Line.ML_BLOCKING)); }
		if (t == 155) Pose(mo, 384, 128, 0, 0);                        // shot: the corridor
		if (t == 215) { Pose(mo, 500, 128, 0, 0); }
		if (t > 215 && t < 265) mo.vel.xy = Actor.AngleToVector(mo.angle, 10);
		if (t == 265) { Check("wentRound", mo.pos.x < 500 && mo.pos.x > 0 && abs(mo.pos.y - 128) < 8); mo.vel.xy = (0, 0); }
		// 2: the corner: take the west leaf to 113
		if (t == 270) { Pose(mo, 120, 128, 0, 180); w.Activate(mo); Check("cut", carried == a && b.Shut() && b.bInvisible && (FindLine(112).flags & Line.ML_BLOCKING)); }
		if (t == 275) { Pose(mo, 640, 80, 0, 270); c.Activate(mo); Check("corner", a.args[0] == 112 && b.args[0] == 113); }
		if (t == 280) Pose(mo, 500, 200, 0, 315);                      // shot: the pinwheel
		if (t == 340) Pose(mo, 640, 120, 0, 270);
		if (t > 340 && t < 380) mo.vel.xy = Actor.AngleToVector(mo.angle, 10);
		if (t == 380) { Check("turned", mo.pos.x > 300 && mo.pos.x < 784 && mo.pos.y > 96 && mo.pos.y < 160 && abs(Actor.DeltaAngle(mo.angle, 180)) < 1); mo.vel.xy = (0, 0); }
		// 3: side by side: the U-turn
		if (t == 385) { Pose(mo, 700, 128, 0, 0); e.Activate(mo); Pose(mo, 192, 80, 0, 270); s1.Activate(mo); }
		if (t == 390) { Pose(mo, 640, 80, 0, 270); c.Activate(mo); Pose(mo, 320, 80, 0, 270); s2.Activate(mo); Check("sideBySide", a.frame && b.frame && a.args[0] && b.args[0] && !carried); }
		if (t == 395) Pose(mo, 256, 260, 0, 270);                      // shot: the two mouths
		if (t == 455) Pose(mo, 192, 120, 0, 270);
		if (t > 455 && t < 495) mo.vel.xy = Actor.AngleToVector(mo.angle, 10);
		if (t == 495) { Check("uTurn", abs(mo.pos.x - 320) < 8 && mo.pos.y > 0 && abs(Actor.DeltaAngle(mo.angle, 90)) < 1); mo.vel.xy = (0, 0); }
		// 4: the gallery: up by RED, a leaf hung there, down, and the hall is joined to it
		if (t == 500) { Pose(mo, 192, 80, 0, 270); s1.Activate(mo); Pose(mo, 128, 600, 128, 90); g.Activate(mo); Check("leafUp", !carried && g.door && g.door.args[0] == 115); }
		if (t == 506) { Pose(mo, 320, 80, 0, 270); s2.Activate(mo); Pose(mo, 120, 128, 0, 180); w.Activate(mo); Check("joined", w.door && g.door && w.door.args[0] == 116 && g.door.args[0] == 111); }
		if (t == 510) Pose(mo, 300, 128, 0, 180);                      // shot: the gallery through the west frame
		if (t == 570) Pose(mo, 120, 128, 0, 180);
		if (t > 570 && t < 596) mo.vel.xy = Actor.AngleToVector(mo.angle, 10);
		if (t == 600) { Check("onGallery", mo.pos.y > 512 && mo.pos.z > 100 && abs(mo.pos.x - 128) < 8); mo.vel.xy = (0, 0); }
		if (t == 605) Pose(mo, 400, 560, 128, 200);                    // shot: the gallery, looking back at 116
	}

	// The lab, MODE=2 and 3: company with a Pair (before MAP16). What must
	// hold whatever anyone does: both leaves hung, each leads to the other's
	// frame and both frames are open; otherwise neither leads anywhere and a
	// leaf that hangs is a wall.
	bool PairOk(AjarDoor a, AjarDoor b)
	{
		if (a.frame && b.frame)
			return a.args[0] == b.frame.args[0] && b.args[0] == a.frame.args[0]
				&& !(FindLine(a.args[0]).flags & Line.ML_BLOCKING) && !(FindLine(b.args[0]).flags & Line.ML_BLOCKING);
		if (a.args[0] || b.args[0]) return false;
		if (a.frame && !(FindLine(a.frame.args[0]).flags & Line.ML_BLOCKING)) return false;
		if (b.frame && !(FindLine(b.frame.args[0]).flags & Line.ML_BLOCKING)) return false;
		return true;
	}

	void LabPut(AjarDoor d, double x, double y)
	{
		if (d.frame) Unhang(d.frame);
		d.carried = false;
		d.SetOrigin((x, y, 0), false);
		d.Show();
	}

	// MODE=2: a thief takes a hung leaf while it is watched (the link is cut
	// at both ends) and hangs it in another frame (the link is made again
	// from there); a leaf hung alone is no way through for it; a Pair, both
	// hung, is, and it comes out at the twin.
	bool leafTaken, leafMoved, pairBroken, shutWay, throughPair;

	void LabThiefScript(Actor mo, int t)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1), red = DoorOf(1);
		AjarFrame w = FindFrame(111), e = FindFrame(112), g = FindFrame(116);
		if (!PairOk(a, b) && !pairBroken) { pairBroken = true; Console.Printf("AJARTEST pair broken at t=%d", t); }
		if (t > 40 && t % 35 == 0 && thief)
			Console.Printf("AJARTEST thief pos=(%d,%d,%d) loot=%s a=%d>%d b=%d>%d", thief.pos.x, thief.pos.y, thief.pos.z,
				thief.loot ? thief.loot.Label() : "-", a.frame ? a.frame.args[0] : 0, a.args[0], b.frame ? b.frame.args[0] : 0, b.args[0]);
		if (t == 20) { Pose(mo, 120, 128, 0, 180); a.Used(mo); w.Activate(mo); }
		if (t == 25) { b.Used(mo); Pose(mo, 700, 128, 0, 0); e.Activate(mo); Check("linked", a.args[0] == 112 && b.args[0] == 111); }
		if (t == 40) { Pose(mo, 384, 300, 0, 0); thief = AjarThief(Actor.Spawn("AjarThief", (680, 128, 0))); thief.testMode = 1; }
		if (t > 40 && t < 700 && thief && thief.loot == b && a.Shut()
			&& (FindLine(111).flags & Line.ML_BLOCKING) && (FindLine(112).flags & Line.ML_BLOCKING)) leafTaken = true;
		if (t > 40 && t < 700 && leafTaken && b.frame && b.frame != e) leafMoved = true;
		if (t == 700)
		{
			Check("thiefTakesLeafAndCutsTheLink", leafTaken);
			Check("thiefHangsLeafElsewhere", leafMoved);
			Check("pairHeldTogether", !pairBroken);
			thief.Destroy();
		}
		// a leaf hung alone: nothing to walk through
		if (t == 705) { LabPut(a, 300, 440); LabPut(b, 440, 440); LabPut(red, 620, 440); }
		if (t == 710) { Pose(mo, 120, 128, 0, 180); a.Used(mo); w.Activate(mo); Check("aloneShut", a.Shut()); }
		if (t == 715) { Pose(mo, 384, 300, 0, 0); thief = AjarThief(Actor.Spawn("AjarThief", (300, 128, 0))); thief.testMode = 2; }
		if (t > 715 && t < 820 && thief && thief.jobLine) shutWay = true;
		if (t == 820) { Check("shutLeafIsNoWay", !shutWay); thief.Destroy(); }
		// both hung, one in the hall and one on the gallery: it goes up by them
		if (t == 825) { LabPut(a, 300, 440); LabPut(b, 440, 440); LabPut(red, 620, 440); }
		if (t == 830) { Pose(mo, 120, 128, 0, 180); a.Used(mo); w.Activate(mo); b.Used(mo); Pose(mo, 128, 600, 128, 90); g.Activate(mo); }
		if (t == 835) { Check("joined", a.args[0] == 116 && b.args[0] == 111); Pose(mo, 384, 300, 0, 180); thief = AjarThief(Actor.Spawn("AjarThief", (300, 128, 0))); thief.testMode = 2; }
		if (t > 835 && thief && thief.pos.z > 100) throughPair = true;
		if (t == 1130) { Check("thiefWalksThroughPair", throughPair); Check("pairHeldTogetherToTheEnd", !pairBroken); }
	}

	// MODE=3: a nailer nails a hung leaf. It cannot be taken; its twin can,
	// and the nailed leaf is then a shut door that stays nailed; the twin
	// hung elsewhere, the nailed leaf leads there.
	void LabNailerScript(Actor mo, int t)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
		AjarFrame w = FindFrame(111), e = FindFrame(112), c = FindFrame(113);
		if (!PairOk(a, b) && !pairBroken) { pairBroken = true; Console.Printf("AJARTEST pair broken at t=%d", t); }
		if (t == 20) { Pose(mo, 120, 128, 0, 180); a.Used(mo); w.Activate(mo); }
		if (t == 25) { b.Used(mo); Pose(mo, 700, 128, 0, 0); e.Activate(mo); Check("linked", a.args[0] == 112 && b.args[0] == 111); }
		if (t == 40) { Pose(mo, 384, 300, 0, 0); nailer = Actor.Spawn("AjarNailer", (600, 128, 0)); }
		if (t > 40 && t % 35 == 0 && nailer)
			Console.Printf("AJARTEST nailer pos=(%d,%d) a=%d b=%d", nailer.pos.x, nailer.pos.y, a.nailer != null, b.nailer != null);
		if (t > 40 && !killTic && b.nailer == nailer) { killTic = t; Check("nailerNailsLeaf", true); }
		if (killTic && t == killTic + 2) { Pose(mo, 700, 128, 0, 0); e.Activate(mo); Check("nailedLeafCannotBeTaken", !carried && b.frame == e); }
		if (killTic && t == killTic + 4) { Pose(mo, 120, 128, 0, 180); w.Activate(mo); Check("itsTwinCanBe", carried == a && b.Shut() && b.nailer == nailer); }
		if (killTic && t == killTic + 6) { Pose(mo, 640, 80, 0, 270); c.Activate(mo); Check("nailedLeafLeadsToTheNewFrame", a.args[0] == 112 && b.args[0] == 113 && !(FindLine(112).flags & Line.ML_BLOCKING)); }
		if (killTic && t == killTic + 10) Pose(mo, 500, 128, 0, 0);          // shot: the nailed leaf, open onto 113
		if (killTic && t == killTic + 80) nailer.DamageMobj(null, null, 1000, 'None');
		if (killTic && t == killTic + 100) { Check("nailsFallOut", !b.nailer && !a.nailer); Pose(mo, 700, 128, 0, 0); e.Activate(mo); }
		if (killTic && t == killTic + 102) { Check("leafTakenAgain", carried == b && a.Shut()); Check("pairHeldTogether", !pairBroken); }
		if (t == 600 && !killTic) Check("nailerNailsLeaf", false);
	}

	void TestLevelScript(Actor mo, int t, int mode)
	{
		if (mode == 13) { RoundScript(mo, t); return; }
		if (mode == 12) { HomeScript(mo, t); return; }
		if (mode == 11) { StrayScript(mo, t); return; }
		if (mode == 10) { CrowdScript(mo, t); return; }
		if (mode == 9) { SelfShotScript(PlayerPawn(mo), t); return; }
		if (mode == 8) { ShootScript(mo, t); return; }
		if (mode == 7) { LodgerScript(mo, t); return; }
		if (mode == 6) { NailerScript(mo, t); return; }
		if (mode == 5) { ThiefScript(mo, t); return; }
		if (mode == 4) { FollowScript(mo, t); return; }
		if (mode == 3) { ThingsScript(mo, t); return; }
		if (mode == 2)
		{
			// real USE key presses come from tools/smoke2.cfg; just pose the player
			if (t == 35) { mo.SetOrigin((70, 2192, 0), false); mo.angle = 180; }   // facing the leaning blue door
			if (t == 120) { mo.SetOrigin((448, 470, 0), false); mo.angle = 90; }   // facing empty frame 102
			return;
		}
		// 1: walk north through the red door (frame 101 at x=160)
		if (t == 35) { mo.SetOrigin((160, 400, 0), false); mo.angle = 90; }
		if (t > 70 && t < 140) mo.vel.xy = (0, 8);
		if (t == 140) Console.Printf("AJARTEST throughRed=%d", mo.pos.y > 1500);
		// 2: pick up blue (leaning), walk back out through the red far side
		if (t == 175) { let di = ThinkerIterator.Create("AjarDoor"); AjarDoor d; while (d = AjarDoor(di.Next())) if (!d.frame && !d.carried) d.Used(mo); }
		if (t == 180) { mo.SetOrigin((192, 2100, 0), false); mo.angle = 270; }
		if (t > 185 && t < 260) mo.vel.xy = (0, -8);
		if (t == 260) Console.Printf("AJARTEST backInHall=%d", mo.pos.y < 600);
		// 3: hang blue in frame 102, look at it, walk through to the ledge
		if (t == 265) { mo.SetOrigin((448, 300, 0), false); mo.angle = 90; mo.vel.xy = (0, 0); FindFrame(102).Activate(mo); }
		if (t > 350 && t < 420) mo.vel.xy = (0, 8);
		if (t == 420) Console.Printf("AJARTEST onLedge=%d", mo.pos.x > 900);
		// 4: swap test and the pit door (z offset)
		if (t == 425) { FindFrame(104).Activate(mo); FindFrame(105).Activate(mo); mo.SetOrigin((1000, 256, 0), false); mo.angle = 0; mo.vel.xy = (0, 0); }
		if (t > 500 && t < 570) mo.vel.xy = (8, 0);
		if (t == 570) Console.Printf("AJARTEST inExitRoom=%d", mo.pos.x > 1900);
	}
}

// Follows one projectile. A projectile never collides with whoever fired it;
// once it has been through a door (seen as a jump far longer than its own
// step) that no longer holds, and it hits its sender like anything else.
class AjarShotWatch : Thinker
{
	Actor shot;
	Vector3 last;
	bool started, crossed;

	override void Tick()
	{
		if (!shot || !shot.bMissile || !shot.target) { Destroy(); return; }
		let who = shot.target;
		if (started && !crossed && (shot.pos.xy - last.xy).Length() > shot.vel.xy.Length() * 1.5 + 48) crossed = true;
		last = shot.pos;
		started = true;
		if (!crossed || who.health <= 0) return;
		if (shot.Distance2D(who) >= shot.radius + who.radius) return;
		if (shot.pos.z >= who.pos.z + who.height || shot.pos.z + shot.height <= who.pos.z) return;
		who.DamageMobj(shot, who, shot.GetMissileDamage(7, 1), shot.DamageType);
		shot.ExplodeMissile(null, who);
		Destroy();
	}
}

// Test-only actors for the MODE=3 smoke test (invisible stand-ins).
class AjarProbe : Actor
{
	Default
	{
		Radius 16;
		Height 56;
		Health 1000;
		Mass 100;
		+SOLID +SHOOTABLE +ISMONSTER +NOBLOOD
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

class AjarProbeShot : Actor
{
	Default
	{
		Projectile;
		Radius 6;
		Height 8;
		Speed 10;
		Damage 1;
	}
	States
	{
	Spawn:
		TNT1 A 1;
		Loop;
	Death:
		TNT1 A 1;
		Stop;
	}
}

class AjarProbePuff : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY
	}
	States
	{
	Spawn:
		TNT1 A 1;
		Stop;
	}
}

// No Doom status bar: only the door you are carrying, held at your side.
// Room keys: numbered, brass, and not Doom's coloured cards, so that a key
// is never mistaken for a door colour. The locks are in src/lockdefs.txt;
// like Doom's keys they are taken away at the end of the level.
class AjarKey : Key
{
	Default
	{
		Radius 20;
		Height 16;
		+NOTDMATCH
	}
}

class AjarKey1 : AjarKey
{
	Default { Inventory.PickupMessage "Room key 1."; Inventory.Icon "AJKI1"; }
	States { Spawn: AJK1 A -1; Stop; }
}

class AjarKey2 : AjarKey
{
	Default { Inventory.PickupMessage "Room key 2."; Inventory.Icon "AJKI2"; }
	States { Spawn: AJK2 A -1; Stop; }
}

class AjarKey3 : AjarKey
{
	Default { Inventory.PickupMessage "Room key 3."; Inventory.Icon "AJKI3"; }
	States { Spawn: AJK3 A -1; Stop; }
}

class AjarKey4 : AjarKey
{
	Default { Inventory.PickupMessage "Room key 4."; Inventory.Icon "AJKI4"; }
	States { Spawn: AJK4 A -1; Stop; }
}

// What stands in MAP07's rooms to be looked at (tools/gfx_things.py): the
// telescope on its pier, the planetarium's projector, an orrery, a globe.
// Nothing touches them: what blocks the way is the pier or plinth under them.
class AjarExhibit : Actor
{
	Default
	{
		Radius 16;
		Height 16;
		YScale 0.8333;       // see TALL in gfx_things.py
		+NOBLOCKMAP
	}
}

class AjarTelescope : AjarExhibit
{
	States { Spawn: AJTE A -1; Stop; }
}

class AjarProjector : AjarExhibit
{
	States { Spawn: AJPJ A -1; Stop; }
}

class AjarOrrery : AjarExhibit
{
	States { Spawn: AJOY A -1; Stop; }
}

class AjarGlobe : AjarExhibit
{
	States { Spawn: AJGB A -1; Stop; }
}

// And in MAP08's: what a department store has standing about.
class AjarMannequin : AjarExhibit
{
	States { Spawn: AJMQ A -1; Stop; }
}

class AjarGentleman : AjarExhibit
{
	States { Spawn: AJMG A -1; Stop; }
}

class AjarRockingHorse : AjarExhibit
{
	States { Spawn: AJRH A -1; Stop; }
}

class AjarTill : AjarExhibit
{
	States { Spawn: AJTL A -1; Stop; }
}

class AjarCarpets : AjarExhibit
{
	States { Spawn: AJCR A -1; Stop; }
}

class AjarStatusBar : BaseStatusBar
{
	HUDFont big;

	override void Init()
	{
		Super.Init();
		SetSize(0, 320, 200);
		big = HUDFont.Create("BIGFONT");
	}

	override void Draw(int state, double TicFrac)
	{
		Super.Draw(state, TicFrac);
		BeginHUD();
		// health bottom left, ammo of the weapon in hand next to it
		DrawString(big, FormatNumber(CPlayer.health, 3), (12, -24), DI_SCREEN_LEFT_BOTTOM, Font.CR_RED);
		// armour over it, when there is any: green, or blue for the better kind
		let arm = BasicArmor(CPlayer.mo.FindInventory("BasicArmor"));
		if (arm && arm.Amount > 0) DrawString(big, FormatNumber(arm.Amount, 3), (12, -44), DI_SCREEN_LEFT_BOTTOM,
			arm.SavePercent > 0.4 ? Font.CR_BLUE : Font.CR_GREEN);
		Ammo a1, a2;
		[a1, a2] = GetCurrentAmmo();
		if (a1) DrawString(big, FormatNumber(a1.Amount, 3), (76, -24), DI_SCREEN_LEFT_BOTTOM, Font.CR_GOLD);
		// room keys held, top right
		int kx = -8;
		for (int k = 4; k >= 1; k--)
		{
			if (!CPlayer.mo.FindInventory(String.Format("AjarKey%d", k))) continue;
			DrawImage(String.Format("AJKI%d", k), (kx, 8), DI_SCREEN_RIGHT_TOP | DI_ITEM_RIGHT_TOP, 1.0, (-1, -1), (2, 2));
			kx -= 62;
		}
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h) return;
		// an open Stray door: how long it has left, always
		int left = -1;
		bool held = false;
		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor sd;
		while (sd = AjarDoor(di.Next()))
		{
			if (sd.args[1] != 7 || !sd.frame) continue;
			if (left < 0 || sd.strayTics < left) { left = sd.strayTics; held = sd.nailer != null; }
		}
		if (left >= 0)
		{
			DrawImage("AJDR7", (-12, 8), DI_SCREEN_CENTER_TOP | DI_ITEM_RIGHT_TOP, 1.0, (-1, -1), (0.5, 0.5));
			if (held) DrawString(big, "NAILED", (0, 20), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_LEFT, Font.CR_GOLD);
			else DrawString(big, String.Format("%d.%d", left / 35, (left % 35) * 10 / 35), (0, 20), DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_LEFT,
				left < 70 ? Font.CR_RED : Font.CR_WHITE);
		}
		// a shutter that is up: how long before it comes down, always
		if (h.shutterLeft >= 0)
		{
			DrawImage("AJLEVR", (-12, 60), DI_SCREEN_CENTER_TOP | DI_ITEM_RIGHT_TOP, 1.0, (-1, -1), (0.3, 0.3));
			DrawString(big, String.Format("%d.%d", h.shutterLeft / 35, (h.shutterLeft % 35) * 10 / 35), (0, 68),
				DI_SCREEN_CENTER_TOP | DI_TEXT_ALIGN_LEFT, h.shutterLeft < 70 ? Font.CR_RED : Font.CR_WHITE);
		}
		if (!h.carried) return;
		// (the clocked door by its sprite: AJDR10 is the time door's, gfx_time.py, which shares its number)
		DrawImage(h.carried.args[1] == AjarDoor.CLOCKED ? "AJDTA0" : String.Format("AJDR%d", h.carried.args[1]), (-8, 28),
			DI_SCREEN_RIGHT_BOTTOM | DI_ITEM_RIGHT_BOTTOM, 1.0, (-1, -1), (1.5, 1.5));
	}
}
