// MAP17 "Made to Order" (tools/map_dispatch.py): the goods dispatch. The
// hopper, the checkers and their lamps, and the smoke tests. The crate and
// the stations that stamp it are the belt lab's (belt.zs).

// The hopper (20096): it issues a crate onto the belt it stands on, one on
// the line at a time: the first at once, the next AGAIN tics after the last
// is gone. It takes a crate back (gone in a puff) when it has stood still
// for STILL tics: not moved on along the line (east: all belts run east) by
// more than ON (pressed against someone it creeps a unit or two), at an
// empty frame or held behind someone; or when it has not moved on by FAR in
// STILL + LATE tics: rocking in a doorway that sends it back against a belt
// (each time through it gains or loses a little, so ON is not enough); when it has more than MOST stamps (a ring);
// or when it is off the line (args[0], args[1]: the tags of the line's
// sectors). That is all a reject is.
// It issues none while the player or a monster stands under the chute or in
// the store's mouth behind it (GUARD: the box from BACK behind the hopper to
// AHEAD before it, SIDE either side of the belt's middle): the wait starts
// again once they are gone. (The store behind the hopper is reached by
// walking up the belt against it, MAP17's third secret.)
class AjarHopper : Actor
{
	const STILL = 350;
	const AGAIN = 70;
	const MOST = 6;
	const ON = 8;
	const FAR = 64;
	const LATE = 35;
	const BACK = 64;
	const AHEAD = 64;
	const SIDE = 48;
	AjarCrate crate;
	Array<int> line;
	int wait, issued, takenBack, issuedAt, takenAt, markTic, farTic;
	int heldAt, holds;
	Vector2 takenFrom;          // where the last was taken back
	int crateCame;              // the tic the crate last came into another sector          // the last tic someone in the way held the next crate back, and how many tics in all
	double progress, mark, farMark;
	Vector2 last;
	string why;                 // why the last was taken back
	string stampsTaken;         // ... and its stamps
	bool paused;                // (the smoke tests: no more crates)

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE +NOSECTOR
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		for (int k = 0; k < 2; k++)
		{
			if (!args[k]) continue;
			let it = level.CreateSectorTagIterator(args[k]);
			int i;
			while ((i = it.Next()) >= 0) line.Push(i);
		}
	}

	bool OnLine(Actor a) { return a && line.Find(a.CurSector.Index()) < line.Size(); }
	static bool Testing() { return CVar.GetCVar("ajar_autotest").GetInt() != 0; }

	override void Tick()
	{
		if (crate && crate.bDestroyed) crate = null;
		if (!crate)
		{
			if (paused) return;
			if (InTheWay()) { wait = AGAIN; heldAt = level.maptime; holds++; return; }
			if (wait > 0) { wait--; return; }
			Issue();
			return;
		}
		Vector2 step = crate.pos.xy - last;
		last = crate.pos.xy;
		if (step.Length() < 64) progress += step.x;          // (a step through a door is no way along)
		if (progress > mark + ON) { mark = progress; markTic = level.maptime; }
		if (progress > farMark + FAR) { farMark = progress; farTic = level.maptime; }
		string w = "";
		if (crate.stamps.Size() > MOST) w = "stamps";
		else if (!OnLine(crate)) w = "off";
		else if (level.maptime - markTic >= STILL) w = "still";
		else if (level.maptime - farTic >= STILL + LATE) w = "rocking";
		if (w != "") TakeBack(w);
	}

	// the player or a living monster under the chute or in the store's mouth
	bool InTheWay()
	{
		let it = BlockThingsIterator.CreateFromPos(pos.x, pos.y, pos.z, 64, BACK + AHEAD, false);
		while (it.Next())
		{
			Actor a = it.thing;
			if (!a || !(a.player || a.bIsMonster) || a.health <= 0) continue;
			if (a.pos.x + a.radius > pos.x - BACK && a.pos.x - a.radius < pos.x + AHEAD && abs(a.pos.y - pos.y) < SIDE + a.radius)
				return true;
		}
		return false;
	}

	// its crate came into another sector (AjarCrate.Tick): off the line, it goes now
	void Arrived()
	{
		crateCame = level.maptime;
		if (crate && !crate.bDestroyed && !OnLine(crate)) TakeBack("off");
	}

	void Issue()
	{
		Sector s = level.PointInSector(pos.xy);
		Vector3 at = (pos.xy, s.floorplane.ZatPoint(pos.xy));
		let c = AjarCrate(Spawn("AjarCrate", at, ALLOW_REPLACE));
		if (!c) return;
		if (!c.TestMobjLocation()) { c.Destroy(); return; }      // someone stands under the hopper: next tic
		crate = c;
		issued++;
		issuedAt = level.maptime;
		last = c.pos.xy;
		progress = mark = farMark = 0;
		markTic = farTic = level.maptime;
		if (Testing()) Console.Printf("AJARTEST crateIssued n=%d t=%d", issued, level.maptime);
	}

	void TakeBack(string w)
	{
		why = w;
		takenFrom = crate.pos.xy;
		stampsTaken = crate.StampList();
		takenBack++;
		takenAt = level.maptime;
		Spawn("ItemFog", crate.pos, ALLOW_REPLACE);
		crate.A_StartSound("misc/spawn", CHAN_AUTO, CHANF_DEFAULT, 0.6);
		if (Testing())
			Console.Printf("AJARTEST crateTakenBack why=%s stamps=%s at (%.1f,%.1f) t=%d issued t=%d", w, stampsTaken,
				crate.pos.x, crate.pos.y, level.maptime, issuedAt);
		crate.Destroy();
		crate = null;
		wait = AGAIN;
	}
}

// A checker (20097): a stretch of belt or a scale (the sector it stands in)
// that reads the stamps of a crate coming onto it (AjarCrate.Tick). args[0]:
// the order it wants, as digits (13 is RED then GREEN), and args[1] the tag
// it opens (Door_Open) when a crate comes stamped exactly so; args[2] and
// args[3] a second order and what that opens (the bay's hidden one), or 0;
// args[4] which it is (1 the press's checker, 2 the kiln's scale, 3 the
// bay's), plus ten times the tag a crate with no stamps at all opens (the
// bay's blank one; none if 0). Filled, an order stays filled; a checker
// whose orders are filled says nothing more. Until then a crate that matches
// none is refused: its lamp (AjarCheckLamp) flashes red, a clunk, and a line
// saying what it wanted and what came, or, once only hidden orders are left,
// that it has no order for that. It does not stop the crate: refusing is all
// it does.
class AjarChecker : Actor
{
	Sector home;
	bool filled, filled2, filled3;
	int refusedAt, filledAt, filledAt2, filledAt3, reads, refusals;
	string lastRead, lastSaid;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE +NOSECTOR
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		home = level.PointInSector(pos.xy);
	}

	static string Colour(int c) { return c == 1 ? "RED" : c == 2 ? "BLUE" : c == 3 ? "GREEN" : String.Format("%d", c); }

	static string Wanted(int code)
	{
		string s = "";
		for (; code > 0; code /= 10) s = Colour(code % 10) .. (s.Length() ? ", " .. s : "");
		return s;
	}

	static string Came(AjarCrate c)
	{
		if (!c.stamps.Size()) return "unstamped";
		string s = "";
		for (int i = 0; i < c.stamps.Size(); i++) s = s .. (i ? ", " : "") .. Colour(c.stamps[i]);
		return s;
	}

	// the stamps as the digits of an order; -1 if they cannot be one
	static int Code(AjarCrate c)
	{
		if (c.stamps.Size() > 6) return -1;
		int code = 0;
		for (int i = 0; i < c.stamps.Size(); i++)
		{
			if (c.stamps[i] < 1 || c.stamps[i] > 9) return -1;
			code = code * 10 + c.stamps[i];
		}
		return code;
	}

	int Which() { return args[4] % 10; }
	int BlankTag() { return args[4] / 10; }
	string Name() { return Which() == 1 ? "The press's checker" : Which() == 2 ? "The kiln's scale" : "The bay's scale"; }
	bool Done() { return filled && (!args[2] || filled2) && (!BlankTag() || filled3); }

	void Say(string msg)
	{
		lastSaid = msg;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.Say(msg);
	}

	void Open(int tag) { if (tag) level.ExecuteSpecial(11 /* Door_Open */, null, null, false, tag, Which() == 3 ? 16 : 32); }

	void Read(AjarCrate c)
	{
		if (Done()) return;
		reads++;
		lastRead = c.StampList();
		int code = Code(c);
		string result;
		if (!filled && code == args[0])
		{
			filled = true;
			filledAt = level.maptime;
			Open(args[1]);
			c.A_StartSound("switches/exitbutn", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
			static const string opens[] = { "", "The steel door from the hall slides open.", "The steel door to the dispatch wing slides open.",
				"The shutter beyond it rolls up: the way out." };
			Say(String.Format("%s passes the crate: %s, as ordered.\n%s", Name(), Wanted(args[0]), opens[clamp(Which(), 0, 3)]));
			result = "filled";
		}
		else if (args[2] && !filled2 && code == args[2])
		{
			filled2 = true;
			filledAt2 = level.maptime;
			Open(args[3]);
			c.A_StartSound("misc/secret", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
			Say(String.Format("%s passes the crate: %s.\nNobody ordered that here, but a panel south of the shutter slides open.", Name(), Wanted(args[2])));
			result = "filled2";
		}
		else if (BlankTag() && !filled3 && !c.stamps.Size())
		{
			filled3 = true;
			filledAt3 = level.maptime;
			Open(BlankTag());
			c.A_StartSound("misc/secret", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
			Say(String.Format("%s passes the crate: unstamped.\nNobody ordered a blank one, but a panel north of the shutter slides open.", Name()));
			result = "filled3";
		}
		else
		{
			refusedAt = level.maptime;
			refusals++;
			c.A_StartSound("plats/pt1_stop", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NORM);
			if (!filled) Say(String.Format("%s wants %s. This one came %s.", Name(), Wanted(args[0]), Came(c)));
			else if (!c.stamps.Size()) Say(String.Format("%s has no order for an unstamped crate.", Name()));
			else Say(String.Format("%s has no order for a crate stamped %s.", Name(), Came(c)));
			result = "refused";
		}
		if (AjarHopper.Testing())
			Console.Printf("AJARTEST checker=%d read=%s result=%s t=%d", Which(), lastRead.Length() ? lastRead : "-", result, level.maptime);
	}
}

// A checker's lamp (20098), on its notice board: args[0] the checker's thing
// id. Dark; flashing red for four seconds after a refusal; green once its
// order (the first, for the bay) is filled.
class AjarCheckLamp : Actor
{
	AjarChecker c;
	int shown;

	Default
	{
		Radius 6;
		Height 24;
		+NOBLOCKMAP +DONTTHRUST +NOTELEPORT
	}
	States
	{
	Spawn:
		AJQL A -1;
		Stop;
	Lit:                        // only so that these are loaded
		AJQL BC -1 Bright;
		Stop;
	}

	override void Tick()
	{
		Super.Tick();
		if (!c)
		{
			let it = level.CreateActorIterator(args[0], "AjarChecker");
			c = AjarChecker(it.Next());
		}
		int f = 0;
		if (c && c.filled) f = 2;
		else if (c && c.refusedAt && level.maptime - c.refusedAt < 140 && (level.maptime - c.refusedAt) % 16 < 10) f = 1;
		frame = f;
		bBright = f > 0;
		if (f != shown)
		{
			shown = f;
			if (f) A_AttachLight('lamp', DynamicLight.PointLight, f == 2 ? 0x40FF60 : 0xFF3020, 56, 56, 0, (0, 0, 12));
			else A_RemoveLight('lamp');
		}
	}
}

// The way out (20099), a thing in the middle of the night room: args[0] and
// args[1] half the room's size along x and y (with its two doors' recesses),
// args[2] the brass frame's line id, args[3] the colour of the door whose far
// side is in the room (VIOLET). The brass frame does not take that door
// (ajarmap.way_home(barred=)); the way out has to come round the line.
// For the player a station is a room from its door's far side to its outlet
// frame: the kiln (GREEN, outlet 103) and labelling (BLUE, outlet 104); the
// press is none (its cell is a dead end). The ring is closed when the brass
// frame holds the door of a station whose outlet holds VIOLET, or holds the
// other station's door, whose outlet holds VIOLET. Each time it becomes
// closed it says so. While it is closed, the player coming into the night
// room through either of its doors (out of the brass frame, or out of
// VIOLET's far side: a step through a portal, not a walk) ends the level;
// by the corridor ends nothing, and leaving ends nothing. Nothing is
// nailed: a door of the ring taken down opens it again.
class AjarRing : Actor
{
	const CAUSE = 9;            // ambush cause 40 + CAUSE: the ring closed for the first time
	bool closed, wasIn, exited;
	int closings, closedAt, openedAt;
	Vector2 last;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE +NOSECTOR
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	// the outlet of the station a door opens onto, for the player; 0 if none
	static int Outlet(AjarDoor d)
	{
		if (!d || d.IsPair()) return 0;
		return d.args[1] == 3 ? 103 : d.args[1] == 2 ? 104 : 0;
	}

	bool Closes(AjarHandler h)
	{
		AjarFrame brass = h.FindFrame(args[2]);
		AjarDoor d = brass ? brass.door : null;
		for (int i = 0; i < 2; i++)
		{
			int o = Outlet(d);
			if (!o) return false;
			AjarFrame f = h.FindFrame(o);
			d = f ? f.door : null;
			if (d && !d.IsPair() && d.args[1] == args[3]) return true;
		}
		return false;
	}

	bool InRoom(Vector2 p) { return abs(p.x - pos.x) < args[0] && abs(p.y - pos.y) < args[1]; }

	override void Tick()
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h || exited) return;
		bool now = Closes(h);
		if (now != closed)
		{
			closed = now;
			if (now)
			{
				closings++;
				closedAt = level.maptime;
				h.Say("The line runs round through the way out.\nGo round.");
			}
			else openedAt = level.maptime;
			if (AjarHopper.Testing()) Console.Printf("AJARTEST ring%s n=%d t=%d", now ? "Closed" : "Opened", closings, level.maptime);
		}
		Actor mo = players[consoleplayer].mo;
		if (!mo) return;
		bool inside = InRoom(mo.pos.xy);
		if (closed && inside && !wasIn && (mo.pos.xy - last).Length() > 64 && mo.health > 0)
		{
			exited = true;
			if (AjarHopper.Testing())
				Console.Printf("AJARTEST ringOut by=%s at (%.0f,%.0f) t=%d", mo.pos.x > pos.x ? "brass" : "violet", mo.pos.x, mo.pos.y, level.maptime);
			level.ExecuteSpecial(243 /* Exit_Normal */, mo, null, false, 0);
		}
		last = mo.pos.xy;
		wasIn = inside;
	}
}

extend class AjarHandler
{
	// ajarmap.ambush's cause 40 + a tag: the order whose checker opens that tag
	// is filled; 40 + AjarRing.CAUSE: the way out's ring has been closed
	bool CheckerOpened(int tag)
	{
		if (tag == AjarRing.CAUSE)
		{
			let r = AjarRing(ThinkerIterator.Create("AjarRing").Next());
			return r && r.closings > 0;
		}
		let it = ThinkerIterator.Create("AjarChecker");
		AjarChecker k;
		while (k = AjarChecker(it.Next()))
			if ((k.filled && k.args[1] == tag) || (k.filled2 && k.args[3] == tag) || (k.filled3 && k.BlankTag() == tag)) return true;
		return false;
	}

	AjarHopper Hopper() { return AjarHopper(ThinkerIterator.Create("AjarHopper").Next()); }

	AjarChecker Checker(int which)
	{
		let it = ThinkerIterator.Create("AjarChecker");
		AjarChecker k;
		while (k = AjarChecker(it.Next())) if (k.Which() == which) return k;
		return null;
	}

	AjarRing Ring() { return AjarRing(ThinkerIterator.Create("AjarRing").Next()); }

	// --- the smoke tests: MAP=MAP17 MODE=1..5 tools/smoke.sh ---------------------
	// The scripts go in steps: each waits for what it needs (a crate to come
	// somewhere, a door to open) and then goes on. The player is god-moded
	// and unseen; Doom's monsters are gone (mode 1 by the walkthrough's rule,
	// the others by the script).
	int mtoStep, mtoAt;          // the step, and the tic it began
	int mtoFails;
	AjarCrate mtoCrate;
	Actor mtoBlock;
	double mtoX, mtoY;
	int mtoT1, mtoT2, mtoN;
	string mtoS;
	bool mtoFlag, mtoFlag2;

	void MtoNext(int t) { mtoStep++; mtoAt = t; }
	int MtoIn(int t) { return t - mtoAt; }
	// a step that waits for `ok`, at most `limit` tics: true when it goes on
	bool MtoWait(int t, string what, bool ok, int limit)
	{
		if (!ok && MtoIn(t) < limit) return false;
		Check(what, ok);
		if (!ok) Console.Printf("AJARTEST info %s: gave up after %d tics", what, MtoIn(t));
		MtoNext(t);
		return true;
	}

	// where the player (or anything) is
	bool InHall(Actor a) { return InBox(a, 0, 0, 640, 512); }
	bool InPressHall(Actor a) { return InBox(a, 768, 0, 1600, 512) && !InCell(a); }
	bool InCell(Actor a) { return InBox(a, 768, 160, 992, 352); }
	bool InKiln(Actor a) { return InBox(a, 768, -448, 1600, -64); }
	bool InLabel(Actor a) { return InBox(a, 768, 576, 1600, 960); }
	bool InWing(Actor a) { return InBox(a, 1728, -448, 2176, 960); }
	bool InBay(Actor a) { return InBox(a, 1728, 0, 2176, 128); }
	bool InNight(Actor a) { return InBox(a, 2352, 128, 2704, 384); }
	bool InStore(Actor a) { return InBox(a, -208, 160, -16, 352); }
	bool InCloset2(Actor a) { return InBox(a, 2192, 128, 2288, 320); }

	// what a lamp of the dispatcher's boards (line id) shows now
	string LampTex(int id) { Line l = FindLine(id); return l ? TexMan.GetName(l.sidedef[0].GetTexture(Side.mid)) : ""; }
	int AmbushersCame(int cause) { return ambushShown[cause] + ambushHid[cause]; }
	const RING_SAID = "The line runs round through the way out.\nGo round.";

	// a walk: posed at x, y facing ang (on a step's first tic), then forward
	// for `tics`; true a few tics after
	bool MtoWalk(Actor mo, int t, double x, double y, double ang, int tics)
	{
		int k = MtoIn(t);
		if (k == 1) Pose(mo, x, y, 0, ang);
		if (k > 1 && k <= tics + 1) mo.vel.xy = (cos(mo.angle), sin(mo.angle)) * 8;
		return k == tics + 5;
	}

	AjarDoor Leaf(int n) { return LabLeaf(8, n); }

	void TakeDoor(Actor mo, AjarDoor d) { if (!carried) d.Used(mo); }

	// Every monster and ambush gone (the modes other than the walk-through).
	void MtoClearOut()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster) { a.ClearCounters(); a.Destroy(); }
		it = ThinkerIterator.Create("AjarAmbush");
		while (a = Actor(it.Next())) a.Destroy();
	}

	void MadeToOrderScript(Actor mo, int t, int mode)
	{
		if (t == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			if (mode != 1) MtoClearOut();
			if (mode != 5) Check("theFirstCrateIsIssued", Hopper() && Hopper().issued == 1 && Hopper().crate != null);
		}
		if (mode == 1) MtoWalkthrough(mo, t);
		else if (mode == 2) MtoSecret(mo, t);
		else if (mode == 3) MtoRules(mo, t);
		else if (mode == 4) MtoWalkOut(mo, t);
		else if (mode == 5) MtoViews(mo, t);
	}

	// MODE=1: the level by the solver's solution (tools/build.py prints it),
	// with real crates: each order is filled by a crate the hopper issued.
	void MtoWalkthrough(Actor mo, int t)
	{
		AjarChecker press = Checker(1), kiln = Checker(2), bay = Checker(3);
		AjarHopper h = Hopper();
		AjarDoor red = DoorOf(1), green = DoorOf(3), blue = DoorOf(2), la = Leaf(0), lb = Leaf(1);
		// watch for a crate in the bay that came by the Pair, with its stamps
		if (h.crate && InBay(h.crate) && !mtoFlag && h.crate.stamps.Size() == 3)
		{
			mtoFlag = true;
			Console.Printf("AJARTEST info a crate in the bay at t=%d, (%.1f,%.1f), stamps %s", t, h.crate.pos.x, h.crate.pos.y, h.crate.StampList());
		}
		switch (mtoStep)
		{
		case 0:     // pick up RED, hang RED in 101
			if (MtoIn(t) == 5) { Pose(mo, 600, 180, 0, 0); TakeDoor(mo, red); FindFrame(101).Activate(mo); }
			if (MtoIn(t) == 6) { Check("redIn101", red.frame == FindFrame(101) && !carried); MtoNext(t); }
			break;
		case 1:     // a crate comes to the press stamped RED: steel door A opens
			if (MtoWait(t, "order1Filled", press.filled, 1200))
			{
				Check("order1ReadRed", press.lastRead == "1");
				Console.Printf("AJARTEST info order 1 filled at t=%d", t);
			}
			break;
		case 2:
			if (MtoWait(t, "doorAOpens", TagOpen(1), 140)) Check("doorBStillShut", !TagOpen(2));
			break;
		case 3:     // walk to the press hall by door A
			if (MtoWalk(mo, t, 600, 432, 0, 30)) { Check("throughDoorA", InPressHall(mo)); MtoNext(t); }
			break;
		case 4:     // pick up GREEN, hang GREEN in 102
			if (MtoIn(t) == 1) { TakeDoor(mo, green); Pose(mo, 1560, 180, 0, 0); FindFrame(102).Activate(mo); }
			if (MtoIn(t) == 2) { Check("greenIn102", green.frame == FindFrame(102) && !carried); MtoNext(t); }
			break;
		case 5:     // a crate onto the kiln's scale stamped RED, GREEN: steel door B opens
			if (MtoWait(t, "order2Filled", kiln.filled, 1600))
			{
				Check("order2ReadRedGreen", kiln.lastRead == "1,3");
				Console.Printf("AJARTEST info order 2 filled at t=%d", t);
			}
			break;
		case 6:
			MtoWait(t, "doorBOpens", TagOpen(2), 140);
			break;
		case 7:     // walk to the wing by door B
			if (MtoWalk(mo, t, 1560, 432, 0, 30)) { Check("throughDoorB", InWing(mo)); MtoNext(t); }
			break;
		case 8:     // pick up BLUE, back to the press hall, through GREEN to the kiln
			if (MtoIn(t) == 1) { Pose(mo, 1780, 650, 0, 180); TakeDoor(mo, blue); Check("tookBlue", carried == blue); MtoNext(t); }
			break;
		case 9:
			if (MtoWalk(mo, t, 1760, 432, 180, 30)) { Check("backToThePressHall", InPressHall(mo)); MtoNext(t); }
			break;
		case 10:
			if (MtoWalk(mo, t, 1540, 256, 0, 20)) { Check("throughGreenToTheKiln", InKiln(mo) && carried == blue); MtoNext(t); }
			break;
		case 11:    // hang BLUE in 103 (round the tunnel, by the scale), back through GREEN against the belt
			if (MtoIn(t) == 1) { Pose(mo, 1560, -180, 0, 0); FindFrame(103).Activate(mo); Check("blueIn103", blue.frame == FindFrame(103) && !carried); MtoNext(t); }
			break;
		case 12:
			if (MtoWalk(mo, t, 820, -256, 180, 25)) { Check("outOfTheKilnByGreen", InPressHall(mo)); MtoNext(t); }
			break;
		case 13:    // a TEAL leaf from the wing
			if (MtoWalk(mo, t, 1560, 432, 0, 30)) { Pose(mo, 1780, 760, 0, 180); TakeDoor(mo, la); Check("tookALeaf", carried == la); MtoNext(t); }
			break;
		case 14:    // back, and swap GREEN for the leaf in 102
			if (MtoWalk(mo, t, 1760, 432, 180, 30))
			{
				Pose(mo, 1560, 180, 0, 0);
				FindFrame(102).Activate(mo);
				Check("leafSwappedIntoFor102", la.frame == FindFrame(102) && carried == green);
				MtoNext(t);
			}
			break;
		case 15:    // to the hall by door A, and swap RED for GREEN in 101
			if (MtoWalk(mo, t, 800, 432, 180, 30))
			{
				Check("backInTheHall", InHall(mo));
				Pose(mo, 600, 180, 0, 0);
				FindFrame(101).Activate(mo);
				Check("greenSwappedForRedIn101", green.frame == FindFrame(101) && carried == red);
				MtoNext(t);
			}
			break;
		case 16:    // through GREEN to the kiln, through BLUE to labelling, with RED
			if (MtoWalk(mo, t, 560, 256, 0, 20)) { Check("throughGreenWithRed", InKiln(mo) && carried == red); MtoNext(t); }
			break;
		case 17:
			if (MtoWalk(mo, t, 1540, -256, 0, 20)) { Check("throughBlueToLabelling", InLabel(mo) && carried == red); MtoNext(t); }
			break;
		case 18:    // hang RED in 104; back through BLUE to the kiln and GREEN to the hall, against the belts
			if (MtoIn(t) == 1) { Pose(mo, 1560, 840, 0, 0); FindFrame(104).Activate(mo); Check("redIn104", red.frame == FindFrame(104) && !carried); MtoNext(t); }
			break;
		case 19:
			if (MtoWalk(mo, t, 820, 768, 180, 25)) { Check("backThroughBlueToTheKiln", InKiln(mo)); MtoNext(t); }
			break;
		case 20:
			if (MtoWalk(mo, t, 820, -256, 180, 25)) { Check("backThroughGreenToTheHall", InHall(mo)); MtoNext(t); }
			break;
		case 21:    // to the wing by both steel doors, the other leaf into 105
			if (MtoWalk(mo, t, 600, 432, 0, 30)) { Check("hallToPressHall", InPressHall(mo)); MtoNext(t); }
			break;
		case 22:
			if (MtoWalk(mo, t, 1560, 432, 0, 30))
			{
				Check("pressHallToWing", InWing(mo));
				Pose(mo, 1780, 870, 0, 180);
				TakeDoor(mo, lb);
				Pose(mo, 1760, 160, 0, 180);
				FindFrame(105).Activate(mo);
				Check("leafIn105", lb.frame == FindFrame(105) && !carried && la.args[0] == 105 && lb.args[0] == 102);
				MtoNext(t);
			}
			break;
		case 23:    // the bay's order is filled: the shutter rolls up (the player watching the scale)
			if (MtoIn(t) == 1) Pose(mo, 1840, 230, 0, 280);
			if (MtoWait(t, "order3Filled", bay.filled, 2000))
			{
				Check("order3ReadGreenBlueRed", bay.lastRead == "3,2,1");
				Check("thePairCarriedItIntoTheBay", mtoFlag);
				Check("thePanelStaysShut", !bay.filled2 && !TagOpen(4));
				Console.Printf("AJARTEST info order 3 filled at t=%d", t);
			}
			break;
		case 24:
			MtoWait(t, "shutterUp", TagOpen(3), 200);
			break;
		case 25:    // out by the shutter, to the night room
			if (MtoWalk(mo, t, 2120, 64, 0, 20)) { Check("throughTheShutter", mo.pos.x > 2192); MtoNext(t); }
			break;
		case 26:
			if (MtoWalk(mo, t, 2528, 64, 90, 12)) { Check("intoTheNightRoom", InNight(mo)); MtoNext(t); }
			break;
		default:
			MtoWayOut(mo, t);
			break;
		}
	}

	// MODE=1 from the night room on: the way out round the line. First what
	// is refused or closes nothing, by script hands (BeltHang) where walking
	// adds nothing; then the solver's route, walked: VIOLET into 103 from the
	// kiln, GREEN into the brass frame; the corridor in; a door of the ring
	// taken down and in by a door; closed again, and round it.
	void MtoWayOut(Actor mo, int t)
	{
		AjarRing ring = Ring();
		AjarFrame brass = FindFrame(190);
		AjarDoor red = DoorOf(1), green = DoorOf(3), blue = DoorOf(2), violet = DoorOf(5), la = Leaf(0), lb = Leaf(1);
		switch (mtoStep)
		{
		case 27:    // VIOLET, leaning in the night room
			if (MtoIn(t) == 1)
			{
				Pose(mo, 2528, 320, 0, 90);
				TakeDoor(mo, violet);
				Check("tookViolet", carried == violet && !ring.closed);
				MtoNext(t);
			}
			break;
		case 28:    // VIOLET tried in the brass frame: refused
			if (MtoIn(t) == 1)
			{
				Pose(mo, 2660, 256, 0, 0);
				brass.Activate(mo);
				Console.Printf("AJARTEST info the brass frame said: %s", said);
				Check("violetRefusedInBrass", !brass.door && carried == violet &&
					said == "The way out will not open onto itself here.\nIt has to come round the line.");
				MtoNext(t);
			}
			break;
		case 29:    // RED in the brass frame and VIOLET in 102: no ring
			if (MtoIn(t) == 1)
			{
				BeltHang(mo, violet, 102);
				BeltHang(mo, red, 190);
				Pose(mo, 2600, 256, 0, 0);
			}
			if (MtoIn(t) == 12)
			{
				Check("redInBrassVioletIn102", brass.door == red && FindFrame(102).door == violet && !carried);
				Console.Printf("AJARTEST info the boards: 102 %s, the brass frame %s", LampTex(702), LampTex(790));
				Check("boardsShowVioletAndBrass", LampTex(702) == "AJRP5" && LampTex(790) == "AJRX1");
				Check("redAndVioletIn102CloseNothing", !ring.closed && ring.closings == 0);
				MtoNext(t);
			}
			break;
		case 30:    // through RED from the brass frame into the press's cell, and back against its belt
			if (MtoWalk(mo, t, 2600, 256, 0, 25)) { Check("throughRedFromBrassToTheCell", InCell(mo)); MtoNext(t); }
			break;
		case 31:
			if (MtoWalk(mo, t, 850, 256, 180, 40)) { Check("backInByTheBrassFrameNothingEnds", InNight(mo) && !ring.exited); MtoNext(t); }
			break;
		case 32:    // all back as the solver has it, VIOLET in hand
			if (MtoIn(t) == 1)
			{
				BeltTake(mo, 190);
				BeltHang(mo, red, 104);
				BeltHang(mo, la, 102);
				Pose(mo, 2528, 320, 0, 90);
				TakeDoor(mo, violet);
				Check("asTheSolverHasIt", green.frame == FindFrame(101) && la.frame == FindFrame(102) && blue.frame == FindFrame(103) &&
					red.frame == FindFrame(104) && lb.frame == FindFrame(105) && !brass.door && carried == violet);
				MtoNext(t);
			}
			break;
		case 33:    // by the corridor to the wing, the press hall, the hall
			if (MtoWalk(mo, t, 2528, 200, 270, 20)) MtoNext(t);
			break;
		case 34:
			if (MtoWalk(mo, t, 2400, 64, 180, 40)) { Check("backToTheWing", InWing(mo)); MtoNext(t); }
			break;
		case 35:
			if (MtoWalk(mo, t, 1760, 432, 180, 30)) MtoNext(t);
			break;
		case 36:
			if (MtoWalk(mo, t, 800, 432, 180, 30)) { Check("backToTheHall", InHall(mo) && carried == violet); MtoNext(t); }
			break;
		case 37:    // through GREEN to the kiln; swap BLUE for VIOLET in 103
			if (MtoWalk(mo, t, 560, 256, 0, 20)) { Check("throughGreenWithViolet", InKiln(mo) && carried == violet); MtoNext(t); }
			break;
		case 38:
			if (MtoIn(t) == 1)
			{
				Pose(mo, 1560, -180, 0, 0);
				FindFrame(103).Activate(mo);
				Check("violetIn103", violet.frame == FindFrame(103) && carried == blue && !ring.closed);
				MtoNext(t);
			}
			break;
		case 39:    // out through GREEN against the belt; swap GREEN for BLUE in 101
			if (MtoWalk(mo, t, 820, -256, 180, 25)) { Check("outOfTheKilnByGreen2", InHall(mo)); MtoNext(t); }
			break;
		case 40:
			if (MtoIn(t) == 1)
			{
				Pose(mo, 600, 180, 0, 0);
				FindFrame(101).Activate(mo);
				Check("blueSwappedForGreenIn101", blue.frame == FindFrame(101) && carried == green);
				MtoNext(t);
			}
			break;
		case 41:    // to the night room with GREEN
			if (MtoWalk(mo, t, 600, 432, 0, 30)) MtoNext(t);
			break;
		case 42:
			if (MtoWalk(mo, t, 1560, 432, 0, 30)) MtoNext(t);
			break;
		case 43:
			if (MtoWalk(mo, t, 2120, 64, 0, 40)) MtoNext(t);
			break;
		case 44:
			if (MtoWalk(mo, t, 2528, 64, 90, 12)) { Check("intoTheNightRoomWithGreen", InNight(mo) && carried == green); MtoNext(t); }
			break;
		case 45:    // GREEN into the brass frame: the ring is closed (GREEN, the kiln, 103 VIOLET)
			if (MtoIn(t) == 1) { Pose(mo, 2660, 256, 0, 0); brass.Activate(mo); }
			if (MtoIn(t) == 4)
			{
				Console.Printf("AJARTEST info said: %s", said);
				Check("ringClosed", brass.door == green && ring.closed && ring.closings == 1 && said == RING_SAID);
				MtoNext(t);
			}
			break;
		case 46:    // out to the corridor and in again by it: nothing ends
			if (MtoWalk(mo, t, 2528, 200, 270, 15)) { Check("outToTheCorridor", !InNight(mo) && mo.pos.y < 128); MtoNext(t); }
			break;
		case 47:
			if (MtoWalk(mo, t, 2528, 80, 90, 15)) { Check("inByTheCorridorEndsNothing", InNight(mo) && !ring.exited); MtoNext(t); }
			break;
		case 48:    // GREEN taken down: the ring is open
			if (MtoIn(t) == 1) { Pose(mo, 2660, 256, 0, 0); brass.Activate(mo); }
			if (MtoIn(t) == 4) { Check("ringOpened", !ring.closed && carried == green && ring.openedAt > ring.closedAt); MtoNext(t); }
			break;
		case 49:    // into VIOLET's far side: the kiln at 103; back through 103: in by a door, and nothing ends
			if (MtoWalk(mo, t, 2440, 256, 180, 15)) { Check("throughVioletToTheKiln", InKiln(mo)); MtoNext(t); }
			break;
		case 50:
			if (MtoWalk(mo, t, 1540, -256, 0, 20)) { Check("inByVioletOpenEndsNothing", InNight(mo) && !ring.exited); MtoNext(t); }
			break;
		case 51:    // closed again
			if (MtoIn(t) == 1) { Pose(mo, 2660, 256, 0, 0); brass.Activate(mo); }
			if (MtoIn(t) == 4)
			{
				Check("closedAgain", brass.door == green && ring.closed && ring.closings == 2 && !carried);
				Console.Printf("AJARTEST info ambushers: VIOLET taken %d, the ring closed %d", AmbushersCame(15), AmbushersCame(49));
				Check("violetsCompanyCame", AmbushersCame(15) == 3);
				Check("theRingsCompanyCame", AmbushersCame(49) == 6);
				MtoNext(t);
			}
			break;
		case 52:    // round it: into the brass frame, GREEN's far side in the kiln...
			if (MtoWalk(mo, t, 2600, 256, 0, 20)) { Check("throughGreenFromBrassToTheKiln", InKiln(mo) && mo.pos.x < 1000); MtoNext(t); }
			break;
		case 53:    // ... round the tunnel, and out through VIOLET in 103: in by a door, the ring closed
			if (MtoWalk(mo, t, 900, -140, 0, 60)) MtoNext(t);
			break;
		case 54:
			if (MtoWalk(mo, t, 1540, -256, 0, 30)) { Check("stillHere", false); MtoNext(t); }
			break;
		}
	}

	// MODE=2: the hidden order from a fresh start, as the solver finds it
	// (orders 1 and 2 first, for the steel doors).
	void MtoSecret(Actor mo, int t)
	{
		AjarChecker press = Checker(1), kiln = Checker(2), bay = Checker(3);
		AjarDoor red = DoorOf(1), green = DoorOf(3), blue = DoorOf(2), la = Leaf(0), lb = Leaf(1);
		MtoNoneInTheStore(t);
		if (t < 800) { MtoStore(mo, t); return; }
		switch (mtoStep)
		{
		case 0:
			if (t == 800) { Pose(mo, 600, 180, 0, 0); TakeDoor(mo, red); FindFrame(101).Activate(mo); MtoNext(t); }
			break;
		case 1:
			MtoWait(t, "order1FilledDoorAOpen", press.filled && TagOpen(1), 1300);
			break;
		case 2:
			if (MtoWalk(mo, t, 600, 432, 0, 30)) { TakeDoor(mo, green); Pose(mo, 1560, 180, 0, 0); FindFrame(102).Activate(mo); MtoNext(t); }
			break;
		case 3:
			MtoWait(t, "order2FilledDoorBOpen", kiln.filled && TagOpen(2), 1700);
			break;
		case 4:     // BLUE from the wing, to the hall: swap RED for BLUE in 101
			if (MtoWalk(mo, t, 1560, 432, 0, 40)) { Pose(mo, 1780, 650, 0, 180); TakeDoor(mo, blue); MtoNext(t); }
			break;
		case 5:
			if (MtoWalk(mo, t, 1760, 432, 180, 30)) MtoNext(t);
			break;
		case 6:
			if (MtoWalk(mo, t, 800, 432, 180, 30))
			{
				Pose(mo, 600, 180, 0, 0);
				FindFrame(101).Activate(mo);
				Check("blueSwappedForRedIn101", blue.frame == FindFrame(101) && carried == red);
				MtoNext(t);
			}
			break;
		case 7:     // through BLUE to labelling, RED in 104, back through BLUE to the hall
			if (MtoWalk(mo, t, 560, 256, 0, 20)) { Check("throughBlueToLabelling", InLabel(mo)); Pose(mo, 1560, 840, 0, 0); FindFrame(104).Activate(mo); MtoNext(t); }
			break;
		case 8:
			if (MtoWalk(mo, t, 820, 768, 180, 25)) { Check("backThroughBlueToTheHall", InHall(mo)); MtoNext(t); }
			break;
		case 9:     // a leaf: from the wing, through GREEN into the kiln, into 103
			if (MtoWalk(mo, t, 600, 432, 0, 30)) MtoNext(t);
			break;
		case 10:
			if (MtoWalk(mo, t, 1560, 432, 0, 30)) { Pose(mo, 1780, 760, 0, 180); TakeDoor(mo, la); MtoNext(t); }
			break;
		case 11:
			if (MtoWalk(mo, t, 1760, 432, 180, 30)) MtoNext(t);
			break;
		case 12:
			if (MtoWalk(mo, t, 1540, 256, 0, 20)) { Check("throughGreenToTheKiln", InKiln(mo)); Pose(mo, 1560, -180, 0, 0); FindFrame(103).Activate(mo); MtoNext(t); }
			break;
		case 13:
			if (MtoWalk(mo, t, 820, -256, 180, 25)) { Check("outOfTheKilnByGreen", InPressHall(mo)); MtoNext(t); }
			break;
		case 14:    // the other leaf into 105
			if (MtoWalk(mo, t, 1560, 432, 0, 30))
			{
				Pose(mo, 1780, 870, 0, 180);
				TakeDoor(mo, lb);
				Pose(mo, 1760, 160, 0, 180);
				FindFrame(105).Activate(mo);
				Check("leavesIn103And105", la.frame == FindFrame(103) && lb.frame == FindFrame(105) && la.args[0] == 105);
				MtoNext(t);
			}
			break;
		case 15:    // the hidden order: the panel opens; the shutter does not
			if (MtoWait(t, "hiddenOrderFilled", bay.filled2, 2000))
			{
				Check("hiddenReadBlueRedGreen", bay.lastRead == "2,1,3");
				Check("theShutterStaysShut", !bay.filled && !TagOpen(3));
			}
			break;
		case 16:
			MtoWait(t, "panelOpens", TagOpen(4), 200);
			break;
		case 17:
			if (MtoWalk(mo, t, 2120, -96, 0, 20)) MtoNext(t);
			break;
		case 18:
			MtoWait(t, "secretFound", level.found_secrets == 2 && level.total_secrets == 3, 60);     // (the store, then this)
			break;
		case 19:    // and the bay answers what comes next as it should: the main order is still open
			if (MtoWait(t, "theBayStillAnswers", bay.refusals > 0 && bay.lastSaid.IndexOf("wants GREEN, BLUE, RED") >= 0, 1600))
				Console.Printf("AJARTEST info the bay said: %s", bay.lastSaid);
			break;
		case 20:    // the blank crate: a leaf in 101 (from 103), its twin still in 105; the player in the bay
			if (MtoIn(t) == 1)
			{
				BeltTake(mo, 103);
				BeltHang(mo, la, 101);
				Pose(mo, 1840, 230, 0, 280);
				Check("leavesIn101And105", la.frame == FindFrame(101) && lb.frame == FindFrame(105) && la.args[0] == 105);
				MtoNext(t);
			}
			break;
		case 21:
			if (MtoWait(t, "blankOrderFilled", bay.filled3, 1500))
			{
				Console.Printf("AJARTEST info the bay said: %s", bay.lastSaid);
				Check("blankReadUnstamped", bay.lastRead == "" && bay.lastSaid.IndexOf("panel north of the shutter") >= 0);
				Check("theShutterStaysShut2", !bay.filled && !TagOpen(3));
			}
			break;
		case 22:
			MtoWait(t, "panel2Opens", TagOpen(5), 200);
			break;
		case 23:    // into the closet behind it
			if (MtoWalk(mo, t, 2120, 224, 0, 20)) MtoNext(t);
			break;
		case 24:
			MtoWait(t, "secondSecretFound", InCloset2(mo) && level.found_secrets == 3, 60);
			break;
		case 25:    // all three; and the bay, with only its main order left, still asks for it
			if (MtoIn(t) == 1)
			{
				Console.Printf("AJARTEST info secrets %d of %d", level.found_secrets, level.total_secrets);
				Check("secretsThreeOfThree", level.found_secrets == 3 && level.total_secrets == 3);
				mtoN = bay.refusals;
			}
			if (MtoIn(t) > 1 && MtoWait(t, "theBayAsksForItsOrder", bay.refusals > mtoN && bay.lastSaid.IndexOf("wants GREEN, BLUE, RED") >= 0, 1600))
			{
				Console.Printf("AJARTEST info the bay said: %s", bay.lastSaid);
				Check("noCrateEverInTheStore", mtoFails == 0);
			}
			break;
		}
	}

	// no crate ever comes into the store behind the hopper (MODE=2 and 3)
	void MtoNoneInTheStore(int t)
	{
		let it = ThinkerIterator.Create("AjarCrate");
		Actor c;
		while (c = Actor(it.Next()))
			if (c.pos.x < 0) { mtoFails++; Console.Printf("AJARTEST info a crate behind the hopper at (%.1f,%.1f) t=%d", c.pos.x, c.pos.y, t); }
	}

	// MODE=2, before the orders: the store behind the hopper, by the player's
	// own walking up the belt against it (tools/smoke_MAP17_2.cfg holds
	// +forward down from about t=60, cl_run 0); then the hopper's guard: no
	// crate while the player, or a monster, is under the chute, and the wait
	// starts again once they are gone.
	void MtoStore(Actor mo, int t)
	{
		AjarHopper h = Hopper();
		if (t == 2) { h.paused = true; if (h.crate) h.crate.Destroy(); }
		// on the hall's belt facing the chute, held there until the key is down
		if (t >= 20 && !walkFrom)
		{
			if (mo.player.cmd.forwardmove > 0) { walkFrom = t; Console.Printf("AJARTEST info the key is down at t=%d", t); }
			else Pose(mo, 300, 256, 0, 180);
		}
		if (walkFrom && !mtoT1 && mo.pos.x < 96) { mtoT1 = t; Console.Printf("AJARTEST info under the chute at t=%d: 204 against the belt in %d tics (%.2f a tic)", t, t - walkFrom, 204. / (t - walkFrom)); }
		if (walkFrom && !mtoT2 && InStore(mo))
		{
			mtoT2 = t;
			Console.Printf("AJARTEST info in the store at t=%d (%.1f,%.1f), secrets %d", t, mo.pos.x, mo.pos.y, level.found_secrets);
		}
		if (t == 280)
		{
			Check("walkedUpTheBeltIntoTheStore", mtoT1 > 0 && mtoT2 > 0 && InStore(mo));
			Check("theStoreIsASecret", level.found_secrets == 1);
			Check("noCrateWhileWalking", h.issued == 1);
			h.paused = false;                     // no crate on the line; and the player under the chute
		}
		if (t >= 280 && t < 420) Pose(mo, 64, 256, 0, 180);
		if (t == 419) { Check("noCrateWithThePlayerUnderTheChute", h.issued == 1 && !h.crate && h.holds >= 135); mtoN = h.holds; }
		if (t == 420) { Pose(mo, 300, 120, 0, 90); mtoX = level.maptime; }
		if (t == 420 + 75)
		{
			Console.Printf("AJARTEST info the player gone at %d, the next issued %d tics later", int(mtoX), h.issuedAt - int(mtoX));
			Check("issuedTwoSecondsAfterThePlayerWent", h.issued == 2 && h.issuedAt - mtoX >= 70 && h.issuedAt - mtoX <= 72);
			h.TakeBack("script");
			mtoBlock = Actor.Spawn("ZombieMan", (64, 256, 0));
			mtoBlock.angle = 0;
		}
		if (t > 495 && t < 640 && mtoBlock) mtoBlock.SetOrigin((64, 256, 0), false);
		if (t == 639) Check("noCrateWithAMonsterUnderTheChute", h.issued == 2 && !h.crate);
		if (t == 640) { mtoBlock.ClearCounters(); mtoBlock.Destroy(); mtoX = level.maptime; }
		if (t == 640 + 75)
		{
			Console.Printf("AJARTEST info the zombie gone at %d, the next issued %d tics later", int(mtoX), h.issuedAt - int(mtoX));
			Check("issuedTwoSecondsAfterTheMonsterWent", h.issued == 3 && h.issuedAt - mtoX >= 70 && h.issuedAt - mtoX <= 72);
		}
	}

	// MODE=3: the rules. Doors by hand (BeltHang, BeltTake: belt.zs).
	// mtoRest: when the hopper's crate came to rest (below); mtoPasses: its jumps through doors
	int mtoRest, mtoPasses;
	Vector2 mtoLastPos, mtoRestPos;
	AjarCrate mtoLastCrate;
	bool mtoHung;
	void MtoRules(Actor mo, int t)
	{
		AjarChecker press = Checker(1), kiln = Checker(2), bay = Checker(3);
		AjarHopper h = Hopper();
		AjarDoor red = DoorOf(1), green = DoorOf(3), blue = DoorOf(2), la = Leaf(0), lb = Leaf(1);
		AjarCrate c = h.crate;
		if (c && !level.IsPointInLevel(c.pos)) { mtoFails++; Console.Printf("AJARTEST info a crate outside the map at t=%d", t); }
		// mtoRest: the last tic the crate was 8 or more from where it was then (it creeps a unit or two when pressed)
		if (c != mtoLastCrate) { mtoLastCrate = c; mtoRest = t; if (c) { mtoLastPos = c.pos.xy; mtoRestPos = c.pos.xy; } }
		else if (c)
		{
			if ((c.pos.xy - mtoLastPos).Length() > 500) mtoPasses++;     // through a door
			mtoLastPos = c.pos.xy;
			if ((c.pos.xy - mtoRestPos).Length() >= 8) { mtoRest = t; mtoRestPos = c.pos.xy; }
		}
		bool still = c && t - mtoRest > 10;
		MtoNoneInTheStore(t);
		switch (mtoStep)
		{
		case 0:     // GREEN in 101: the crate goes to the kiln stamped GREEN only
			if (MtoIn(t) == 4) { BeltHang(mo, green, 101); Pose(mo, 300, 100, 0, 90); MtoNext(t); }
			break;
		case 1:
			if (MtoWait(t, "kilnRefusesGreen", kiln.refusals > 0, 900))
			{
				Console.Printf("AJARTEST info the kiln's scale said: %s", kiln.lastSaid);
				Check("refusalSaysWhatCame", kiln.lastSaid == "The kiln's scale wants RED, GREEN. This one came GREEN.");
				Check("refusedNotFilled", !kiln.filled && !TagOpen(2));
				mtoN = h.takenBack;
				mtoT1 = 0;
			}
			break;
		case 2:     // it comes to rest at 103, empty; ten seconds still, and it is taken back
			if (still) mtoT1 = mtoRest;
			if (MtoWait(t, "takenBackAt103", h.takenBack > mtoN, 800))
			{
				Console.Printf("AJARTEST info came to rest at (%.1f,%.1f) at t=%d, taken back at t=%d (why %s): %d tics", mtoLastPos.x, mtoLastPos.y, mtoT1, h.takenAt, h.why, h.takenAt - mtoT1);
				Check("takenBackAfterTenSeconds", h.why == "still" && h.stampsTaken == "3" && mtoT1 && abs(h.takenAt - mtoT1 - 350) <= 3);
			}
			break;
		case 3:
			if (MtoWait(t, "nextIssued", h.issuedAt > h.takenAt, 100))
			{
				Check("nextTwoSecondsAfter", h.issuedAt - h.takenAt == 70 || h.issuedAt - h.takenAt == 71);
				mtoHung = false;
			}
			break;
		case 4:     // the next comes to rest at 103 too; BLUE hung there 100 tics later: it goes on, stamps kept
			if (still && t == mtoRest + 100 && !mtoHung)
			{
				mtoHung = true;
				mtoN = h.takenBack;
				BeltHang(mo, blue, 103);
				Pose(mo, 300, 100, 0, 90);
				Console.Printf("AJARTEST info BLUE hung in 103 at t=%d, the crate waiting at (%.1f,%.1f) since t=%d", t, c.pos.x, c.pos.y, mtoRest);
			}
			if (MtoWait(t, "waitingCrateGoesOn", mtoHung && c && InLabel(c) && c.stamps.Size() == 2, 1200))
			{
				Check("keptItsStamps", c.StampList() == "3,2" && h.takenBack == mtoN);
				Console.Printf("AJARTEST info in labelling at t=%d with %s", t, c.StampList());
			}
			break;
		case 5:     // RED in 101; the player rides into the cell and is held at the press
			if (MtoIn(t) == 1)
			{
				BeltTake(mo, 101); BeltTake(mo, 103);
				BeltHang(mo, red, 101);
				if (c) { h.TakeBack("script"); }
				Pose(mo, 400, 256, 0, 0);
			}
			if (MtoIn(t) == 150) { Check("playerHeldAtThePress", InCell(mo) && mo.pos.x > 960); mtoN = h.takenBack; mtoT1 = 0; MtoNext(t); }
			break;
		case 6:     // a crate comes up behind the player and stops; ten seconds, and it is taken back
			if (still && InCell(c) && !mtoT1)
			{
				mtoT1 = mtoRest;
				double gap = mo.pos.x - c.pos.x - mo.radius - c.radius;
				Console.Printf("AJARTEST info a crate stopped behind the player at t=%d: crate x %.1f, player x %.1f, between them %.1f", t, c.pos.x, mo.pos.x, gap);
				Check("crateStopsBehindThePlayer", gap > -1 && gap < 3);
			}
			if (MtoWait(t, "takenBackBehindThePlayer", h.takenBack > mtoN, 900))
				Check("afterTenSecondsStill", h.why == "still" && mtoT1 && abs(h.takenAt - mtoT1 - 350) <= 3);
			break;
		case 7:     // the player steps off onto the cell's floor: the next goes on through the press to its checker
			if (MtoIn(t) == 1) { Pose(mo, 900, 190, 0, 90); mtoN = h.takenBack; mtoT1 = 0; }
			if (MtoWait(t, "nextGoesThroughThePress", press.filled, 700))
				Check("throughOnceThePlayerIsGone", h.takenBack == mtoN && press.lastRead == "1");
			break;
		case 8:     // a zombie stands at the press: the same
			if (MtoIn(t) == 1)
			{
				if (c) h.TakeBack("script");
				mtoBlock = Actor.Spawn("ZombieMan", (970, 256, 0));
				mtoBlock.angle = 0;
				Pose(mo, 300, 100, 0, 90);
				mtoN = h.takenBack;
				mtoT1 = 0;
			}
			if (still && InCell(c) && !mtoT1 && MtoIn(t) > 1)
			{
				mtoT1 = mtoRest;
				double gap = mtoBlock.pos.x - c.pos.x - mtoBlock.radius - c.radius;
				Console.Printf("AJARTEST info a crate stopped behind the zombie at t=%d: crate x %.1f, zombie x %.1f, between them %.1f", t, c.pos.x, mtoBlock.pos.x, gap);
				Check("crateStopsBehindAMonster", gap > -1 && gap < 3);
			}
			if (MtoIn(t) > 1 && MtoWait(t, "takenBackBehindAMonster", h.takenBack > mtoN, 1200))
			{
				Check("afterTenSecondsStillToo", h.why == "still" && mtoT1 && abs(h.takenAt - mtoT1 - 350) <= 3);
				Check("monsterLeftWhereItWas", mtoBlock && mtoBlock.health > 0 && InCell(mtoBlock));
				mtoBlock.ClearCounters();
				mtoBlock.Destroy();
			}
			break;
		case 9:     // a TEAL leaf in 101, its twin in 102: through 101, out of 102 against the belt, back in...
			if (MtoIn(t) == 1)
			{
				BeltTake(mo, 101);
				BeltHang(mo, la, 101);
				BeltHang(mo, lb, 102);
				Check("leavesIn101And102", la.args[0] == 102 && lb.args[0] == 101);
				if (c) h.TakeBack("script");
				mtoN = h.takenBack;
				mtoPasses = 0;
			}
			if (c && MtoIn(t) > 1 && t % 35 == 0) Console.Printf("AJARTEST info t=%d the crate at (%.2f,%.2f) vel (%.2f,%.2f), %d passes", t, c.pos.x, c.pos.y, c.vel.x, c.vel.y, mtoPasses);
			if (MtoIn(t) > 1 && MtoWait(t, "rockingCrateTakenBack", h.takenBack > mtoN, 1200))
			{
				Console.Printf("AJARTEST info taken back at t=%d (why %s) at (%.1f,%.1f) after %d passes through the doors", h.takenAt, h.why, mtoLastPos.x, mtoLastPos.y, mtoPasses);
				Check("takenBackAsRocking", h.why == "rocking" && mtoPasses >= 2);
			}
			break;
		case 10:
			if (MtoWait(t, "nextIssuedAfterTheRocking", h.issuedAt > h.takenAt, 100))
			{
				BeltTake(mo, 101); BeltTake(mo, 102);
				BeltHang(mo, red, 101); BeltHang(mo, green, 102);
				mtoN = h.takenBack;
				mtoFlag = false;
			}
			break;
		case 11:    // a ring: once a crate is in the kiln, BLUE into 103 and RED from 101 into 104
			if (c && InKiln(c) && !mtoFlag)
			{
				mtoFlag = true;
				BeltTake(mo, 101);
				BeltHang(mo, blue, 103);
				BeltHang(mo, red, 104);
				Console.Printf("AJARTEST info the ring closed at t=%d with the crate in the kiln, stamps %s", t, c.StampList());
			}
			if (MtoWait(t, "ringTakenBack", h.takenBack > mtoN, 3000))
			{
				Console.Printf("AJARTEST info taken back at t=%d (why %s) with %s", h.takenAt, h.why, h.stampsTaken);
				Check("sevenStampsAreTooMany", h.why == "stamps" && h.stampsTaken == "1,3,2,1,3,2,1");
				BeltTake(mo, 104); BeltTake(mo, 103); BeltTake(mo, 102);
				BeltHang(mo, green, 101);
				mtoFlag2 = false;
			}
			break;
		case 12:    // off the line: a crate put down on the hall's floor
			if (c && c.pos.x > 300 && !mtoFlag2) { mtoFlag2 = true; mtoN = h.takenBack; mtoT2 = t; c.SetOrigin((c.pos.x, 120, 0), true); }
			if (mtoFlag2 && (h.takenBack > mtoN || t - mtoT2 > 30))
			{
				Check("offTheLineTakenBack", h.takenBack > mtoN);
				Console.Printf("AJARTEST info put down at t=%d, taken back at t=%d (why %s)", mtoT2, h.takenAt, h.why);
				Check("whyOff", h.why == "off" && h.takenAt - mtoT2 <= 2);
				MtoNext(t);
			}
			else if (MtoIn(t) > 400) { Check("offTheLineTakenBack", false); MtoNext(t); }
			break;
		case 13:
			if (MtoWait(t, "theHopperGoesOn", h.issuedAt > h.takenAt && h.crate != null, 100))
				Check("noneLost", mtoFails == 0);
			break;
		case 14:    // VIOLET in 101: a crate goes through it into the night room, off the line: taken back at once
		case 15:    // a leaf in 101, its twin in the night room's brass frame: the same
		{
			if (MtoIn(t) == 1)
			{
				BeltTake(mo, 101);
				if (mtoStep == 14) BeltHang(mo, DoorOf(5), 101);
				else { BeltHang(mo, la, 101); BeltHang(mo, lb, 190); }
				if (c) h.TakeBack("script");
				mtoN = h.takenBack;
				Pose(mo, 300, 100, 0, 90);
			}
			string by = mtoStep == 14 ? "Violet" : "ALeaf";
			if (MtoIn(t) > 1 && MtoWait(t, "crateThrough" .. by .. "TakenBack", h.takenBack > mtoN, 400))
			{
				Console.Printf("AJARTEST info taken back (why %s) at (%.1f,%.1f) t=%d, came there t=%d", h.why, h.takenFrom.x, h.takenFrom.y, h.takenAt, h.crateCame);
				Check("offInTheNightRoomThrough" .. by, h.why == "off" && h.takenFrom.x > 2352 && h.takenFrom.x < 2704 && h.takenFrom.y > 128 && h.takenFrom.y < 384);
				Check("takenBackTheTicItCameThrough" .. by, h.takenAt == h.crateCame);
			}
			break;
		}
		case 16:    // all as it was, GREEN in 101
			if (MtoIn(t) == 1)
			{
				BeltTake(mo, 101); BeltTake(mo, 190);
				BeltHang(mo, green, 101);
				Check("noRingOfThat", Ring().closings == 0);
			}
			MtoWait(t, "theHopperGoesOnAgain", h.crate != null && h.issuedAt > h.takenAt, 120);
			break;
		case 17:    // and nothing has been left anywhere: one crate, the hopper's
			if (MtoIn(t) == 1)
			{
				int n = 0;
				let it = ThinkerIterator.Create("AjarCrate");
				while (it.Next()) n++;
				Check("oneCrateInTheLevel", n == 1);
				Console.Printf("AJARTEST info %d crates issued, %d taken back", h.issued, h.takenBack);
				MtoNext(t);
			}
			break;
		}
	}

	// MODE=4: in by a door and out again against the belt, walking, by each
	// of the three far sides (RED: the press's cell, GREEN: the kiln, BLUE:
	// labelling). The walking is the player's own: tools/smoke_MAP17_4.cfg
	// holds +forward down (cl_run 0) in each "walk" window; the script only
	// places the player and turns them round. No crates (the hopper stops).
	int walkFrom, walkOut;
	double walkSpeed;
	void MtoWalkOut(Actor mo, int t)
	{
		AjarHopper h = Hopper();
		if (t == 2) { h.paused = true; if (h.crate) h.crate.Destroy(); }
		// on the floor first: how fast does the player walk (no belt)?
		if (t == 60) Pose(mo, 40, 100, 0, 0);
		if (t > 60 && t < 300 && !walkFrom && mo.vel.Length() > 0.5) { walkFrom = t; Console.Printf("AJARTEST info the key is down at t=%d", t); }
		if (walkFrom && t == walkFrom + 20) mtoX = mo.pos.x;     // (at full speed by then; the wall is some 500 off)
		if (walkFrom && t == walkFrom + 50)
		{
			walkSpeed = (mo.pos.x - mtoX) / 30;
			Console.Printf("AJARTEST info walking on the floor: %.2f a tic (vel %.2f)", walkSpeed, mo.vel.Length());
			Check("walkingNotRunning", walkSpeed > 7.5 && walkSpeed < 9);
		}
		static const int colours[] = { 1, 3, 2 };
		static const string rooms[] = { "Cell", "Kiln", "Labelling" };
		int k = (t - 400) / 700, at = (t - 400) % 700;
		if (t < 400 || k > 2) return;
		AjarDoor d = DoorOf(colours[k]);
		bool inRoom = k == 0 ? InCell(mo) : k == 1 ? InKiln(mo) : InLabel(mo);
		if (at == 0)
		{
			BeltTake(mo, 101);
			BeltHang(mo, d, 101);
			Pose(mo, 520, 256, 0, 0);         // standing on the hall's belt: it carries them in
			walkOut = 0;
			mtoFlag = false;
		}
		if (at == 290)
		{
			Console.Printf("AJARTEST info %s: carried in and held at (%.1f,%.1f)", rooms[k], mo.pos.x, mo.pos.y);
			Check("riddenInto" .. rooms[k], inRoom);
			mo.angle = 180;                   // turned round; the key goes down at about 310
			mtoX = mo.pos.x;
		}
		if (at > 290 && at < 680 && inRoom && !mtoFlag && mo.vel.x < -0.5) { mtoFlag = true; mtoT1 = t; mtoX = mo.pos.x; }
		if (at > 290 && mtoFlag && !walkOut && InHall(mo))
		{
			walkOut = t;
			Console.Printf("AJARTEST info %s: walked out into the hall at t=%d, %d tics after starting from x %.1f: %.2f a tic against the belt",
				rooms[k], t, t - mtoT1, mtoX, (mtoX - 768) / (t - mtoT1));
		}
		if (at == 690) Check("walkedOutOf" .. rooms[k], walkOut > 0);
	}

	// MODE=5: views for screenshots (tools/smoke_MAP17_5.cfg shoots every 40
	// tics): the doors hung as for the way out, crates with stamps put down
	// before the camera, the notes, the board, the glass.
	void MtoViews(Actor mo, int t)
	{
		static const double views[] = {
			400, 300, 0, 90, 0,         // 0 the hall's board (GREEN in 101)
			300, 120, 0, 10, 0,         // 1 the hopper's belt and 101, a crate on it
			560, 100, 0, 18, 0,         // 2 through the window: the press's checker, its board and lamp
			1216, 150, 0, 90, -5,       // 3 the press's note, from the south
			900, 300, 0, 180, 0,        // 4 in the cell: the secret's note by RED's far side
			880, 440, 0, 270, 0,        // 5 the cell through its glass, from the north
			1440, 200, 0, 270, 8,       // 6 through the window into the kiln: its scale and note
			900, -380, 0, 0, 0,         // 7 the kiln's tunnel
			900, 660, 0, 15, 0,         // 8 labelling's gantry
			1800, 200, 0, 300, 5,       // 9 the bay: the scale, the shutter and its note, the lamp
			1980, 740, 0, 0, 0,         // 10 the wing's board
			1770, -270, 0, 0, 5,        // 11 crates before the camera: no stamps; R; R,G; G,B,R; B,R,G; five
			1780, -370, 0, 180, 0,      // 12 through the window into the kiln
			1780, 896, 0, 180, 0,       // 13 through the window into labelling
			1250, 100, 0, 180, 0,       // 14 the press hall: the cell, the press and its belt
			2080, 64, 0, 0, 0,          // 15 the bay's note, close
			2528, 140, 0, 90, 0,        // 16 the night room from the way in: VIOLET against the north wall
			2420, 256, 0, 0, 0,         // 17 the brass frame down the room
			2600, 256, 0, 180, 0,       // 18 VIOLET's far side
			1960, -96, 0, 0, 0,         // 19 the panel south of the shutter, its stub
			1960, 224, 0, 0, 0,         // 20 the panel north of the shutter, its stub
			1110, 330, 0, 180, 0,       // 21 the cell's torn note, from the press hall through the glass
			880, 440, 0, 235, 0,        // 22 ... and from north of the cell
			280, 160, 0, 180, 0,        // 23 the blank crate's torn note in the hall
			260, 320, 0, 194, 5,        // 24 the store's mouth, from the hall
			-24, 256, 0, 180, 0,        // 25 in the store
			400, 300, 0, 90, 0,         // 26 the hall's board: VIOLET in 102, GREEN in the brass frame
			1280, 300, 0, 90, 0,        // 27 the press hall's board
			1980, 704, 0, 0, 0          // 28 the wing's board
		};
		if (t == 2)
		{
			AjarHopper h = Hopper();
			BeltHang(mo, DoorOf(3), 101); BeltHang(mo, DoorOf(2), 103); BeltHang(mo, DoorOf(1), 104);
			BeltHang(mo, Leaf(0), 102); BeltHang(mo, Leaf(1), 105);
			static const int stamps[] = { 0, 1, 13, 321, 213, 32132 };
			for (int i = 0; i < 6; i++)
			{
				let c = AjarCrate(Actor.Spawn("AjarCrate", (1900, -380 + 44 * i, 0)));
				Array<int> digits;
				for (int code = stamps[i]; code > 0; code /= 10) digits.Insert(0, code % 10);
				for (int k = 0; k < digits.Size(); k++) c.stamps.Push(digits[k]);
				c.Bands();
			}
		}
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		if (t == 26 * 40 - 20) { BeltHang(mo, DoorOf(5), 102); BeltHang(mo, DoorOf(3), 190); }
		int i = t / 40;
		if (i >= views.Size() / 5) return;
		Pose(mo, views[i * 5], views[i * 5 + 1], views[i * 5 + 2], views[i * 5 + 3]);
		mo.pitch = views[i * 5 + 4];
		if (t % 40 == 0)
		{
			AjarHopper h = Hopper();
			Console.Printf("AJARTEST view=%d crate=%s", i, h.crate ? String.Format("(%.0f,%.0f) %s", h.crate.pos.x, h.crate.pos.y, h.crate.StampList()) : "-");
		}
	}
}
