// The sprung frame and the room of goes (PLAN.md, "The plate lab";
// the test map PLATE, tools/map_plate.py; MAP=PLATE MODE=3 and 4 tools/smoke.sh).
//
// A sprung frame is a frame that a plate on the floor names (AjarPlate,
// args[0] the frame's id; or args[1] the tag of a shutter, shut.zs). A door hung in it is a door only while the plate
// is pressed: while the player or an earlier self (AjarGhost) stands on it.
// Otherwise it is shut, as a Pair's leaf hung alone is: its face on the
// frame's line and on its far side, and nothing passes it from either side,
// no walker, shot or sight. It is heard opening and shutting. Whoever stands
// in the doorway when it shuts is put a step clear, on the side they are on.
//
// A room of goes (an AjarZone of a hall with args[4] 2, time.zs) is the open
// fight's way of having earlier selves, with no fight in it. It has one box
// (box 1) behind its time door. Through the time door the player is in the
// box at the start of a new go, with the box's door open onto the hall; as
// often as they like. Every earlier go is there as an AjarGhost that walks
// where the player walked then, and does again what they did to doors:
//  * at the start of every go, every door that has been touched is put as it
//    was when the room was first entered (a door in the player's hands then
//    counts as leaning at the time door);
//  * each go writes down what the player did to doors (took, hung, took
//    down, left leaning), at the go's tic, with how the door was found;
//  * an earlier self does each of those again at its tic, for real, if the
//    door is just then as it found it then: leaning in that place, hanging
//    in that frame, or in that self's own hands; and, to hang it, the frame
//    is empty. If not, that and every later thing it did to that door in
//    this go is not done (it mimes it);
//  * a door in an earlier self's hands is hidden, as in the player's; when
//    its go is over (it went out by the time door then, and it is gone now)
//    what it holds is left leaning where it went;
//  * the player must not touch an earlier self (their bodies overlapping) in
//    the hall, once they have been clear of it in this go: that is a time
//    paradox, the player is dead for real and the level begins again
//    (paradox.zs; so too in a fight that has become a room of goes, and in
//    an open fight).
// The room is over when the player is out of its zones by a way that is not
// a time door: its time doors shut, the earlier selves are gone (what they
// hold is left where they stood), and it does not begin again. A plate on a
// wall of the box (AjarAnew) forgets every go: no earlier selves, the doors
// as at the first entry, and the go that is on is the first.
//
// An open fight can also become a room of goes when it is won (zone args[4]
// 3): goes.zs. Its first entry is then the moment of the win.

class AjarPlate : Actor
{
	bool pressed;
	AjarFrame fr;
	// args[2] n: the first time the player steps on it, it says
	// AjarTimeHandler.PlateText(n) (shut.zs). steps: how often the player
	// stepped on it; told: how often it said so (tests)
	int steps, told;
	bool mine;
	double homeZ;               // its height: a press coming down over it pushes it down, and it goes back
	bool homed;
	const REACH = 28;           // how near its middle someone must stand
	const FEET = 4;             // and how near the floor

	Default { Radius 28; Height 2; +FLATSPRITE +NOBLOCKMAP +NOGRAVITY +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJPL A -1;
		Stop;
	Down:
		AJPL B -1 Bright;
		Stop;
	}

	bool On(Actor a)
	{
		return a && a.health > 0 && (a.pos.xy - pos.xy).Length() <= REACH && abs(a.pos.z - pos.z) <= FEET;
	}

	override void Tick()
	{
		Super.Tick();
		if (!homed) { homed = true; homeZ = pos.z; }
		else if (pos.z != homeZ) SetZ(homeZ);
		bool now = On(players[consoleplayer].mo);
		if (now && !mine)
		{
			steps++;
			if (args[2] && !told)
			{
				told++;
				let dh = AjarHandler(EventHandler.Find("AjarHandler"));
				if (dh) dh.Say(AjarTimeHandler.PlateText(args[2]));
			}
		}
		mine = now;
		if (!now)
		{
			let it = ThinkerIterator.Create("AjarGhost");
			Actor g;
			while (!now && (g = Actor(it.Next()))) now = On(g);
		}
		if (now == pressed) return;
		pressed = now;
		if (now) SetStateLabel("Down");
		else SetStateLabel("Spawn");
		A_StartSound("switches/normbutn", CHAN_BODY, 0, 0.5);
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h) return;
		if (!fr) fr = h.FindFrame(args[0]);
		if (fr) h.Spring(fr, true);
	}
}

// A plate on a wall of a room of goes' box: USE forgets every go.
class AjarAnew : Actor
{
	Default { Radius 12; Height 24; +NOGRAVITY +WALLSPRITE +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJAN A -1 Bright;
		Stop;
	}

	override bool Used(Actor user)
	{
		let h = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let mo = PlayerPawn(user);
		if (!h || !mo || !mo.player) return false;
		h.Anew(mo);
		return true;
	}
}

// What the player did to doors in one go at a room of goes: for each
// change, its tic, the door (its index in AjarTimeHandler.dDoor), how it
// was found and what it was made.
class AjarGoLog play
{
	Array<int> tic, door, car, fCar;
	Array<AjarFrame> frm, fFrm;
	Array<double> x, y, z, a, fx, fy;
	int next;                   // the next of them to be done again
	Array<int> broken;          // doors it no longer does anything to, in this go
	// and the presses it set off (goes.zs): at tic pTic, the press with sector tag pTag
	Array<int> pTic, pTag;
	int pNext;
	// and the key levers it pulled (keys.zs): at tic kTic, lever number kNum of the shutter of tag kTag
	Array<int> kTic, kTag, kNum;
	int kNext;
}

extend class AjarHandler
{
	// what nothing passes while a sprung frame's door is shut
	const SPRUNG = Line.ML_BLOCKING | Line.ML_BLOCKEVERYTHING | Line.ML_BLOCKPROJECTILE | Line.ML_BLOCKHITSCAN | Line.ML_BLOCKSIGHT;
	const CLEAR = 26;

	AjarPlate PlateFor(AjarFrame f)
	{
		if (!f) return null;
		let it = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(it.Next())) if (p.args[0] == f.args[0]) return p;
		return null;
	}

	// The door in a sprung frame is opened or shut as its plate is (Hang,
	// and the plate when it is pressed or let go). `felt`: it is heard.
	void Spring(AjarFrame f, bool felt = false)
	{
		AjarPlate p = PlateFor(f);
		if (!p || !f.door) return;
		AjarDoor d = f.door;
		bool open = p.pressed && d.args[0];
		Line a = FindLine(f.args[0]), b = FindLine(d.args[0]);
		if (open)
		{
			Link(f.args[0], d.args[0], d.IsPair() ? d.BackTex() : FRAME_TEX);
			Link(d.args[0], f.args[0], d.BackTex());
			if (a) a.flags &= ~SPRUNG;
			if (b) b.flags &= ~SPRUNG;
			d.Show();
		}
		else
		{
			Link(f.args[0], 0, d.BackTex());
			Link(d.args[0], 0, d.BackTex());
			if (a) a.flags |= SPRUNG;
			if (b) b.flags |= SPRUNG;
			d.Hide();
			StandClear(a);
			StandClear(b);
		}
		if (felt) f.A_StartSound(open ? "doors/dr2_open" : "doors/dr2_clos", CHAN_AUTO);
	}

	// A door taken out of a sprung frame: its lines are as any empty frame's
	// and any unhung door's (Link makes them solid walls).
	void Unspring(AjarFrame f, AjarDoor d)
	{
		if (!PlateFor(f)) return;
		int more = Line.ML_BLOCKPROJECTILE | Line.ML_BLOCKHITSCAN | Line.ML_BLOCKSIGHT;
		Line a = FindLine(f.args[0]), b = FindLine(d.args[0]);
		if (a) a.flags &= ~more;
		if (b) b.flags &= ~more;
	}

	// A line that has just become solid: the player is not left in it, but a
	// step clear of it on the side they are on (their middle is never past
	// a portal line: crossing it, they are on the far side).
	void StandClear(Line l)
	{
		let mo = players[consoleplayer].mo;
		if (!l || !mo) return;
		Vector2 dir = l.delta.Unit(), n = (dir.y, -dir.x);
		Vector2 rel = mo.pos.xy - l.v1.p;
		double along = rel dot dir, d = rel dot n;
		if (along < -mo.radius || along > l.delta.Length() + mo.radius || abs(d) >= CLEAR) return;
		mo.SetOrigin((mo.pos.xy + n * ((d < 0 ? -CLEAR : CLEAR) - d), mo.pos.z), true);
	}
}

extend class AjarTimeHandler
{
	Array<int> goesFights;
	bool goes;                  // the fight that is on is a room of goes
	bool goesWon;               // and it was a fight until it was won (goes.zs): its first entry is the win
	Array<AjarGoLog> logs;      // logs[i]: what was done to doors in takes[i]
	Array<int> dHold;           // dHold[i]: the earlier self (its take) door i is in the hands of, or -1

	// The hall's time doors lead into the box, and the box's door back out
	// by time door 1; or (on false) all are shut.
	void GoesDoors(bool on)
	{
		let h = Doors();
		for (int j = 1; h.FindLine(HallLine(fight, j)); j++) h.Link(HallLine(fight, j), on ? BoxLine(fight, 1) : 0, TIME_TEX);
		h.Link(BoxLine(fight, 1), on ? HallLine(fight, 1) : 0, TIME_TEX);
	}

	void GoTake(Actor mo)
	{
		takes.Push(new("AjarTake"));
		logs.Push(new("AjarGoLog"));
		ot = 0;
		hadClip = mo.CountInv("Clip"); hadShell = mo.CountInv("Shell");
		shots.Clear();
		parted.Clear();             // paradox.zs: every go begins inside the copies
	}

	// `atWin`: a fight that has just been won becomes a room of goes (goes.zs).
	void BeginGoes(int k, bool atWin = false)
	{
		let mo = players[consoleplayer].mo;
		fight = k;
		goes = true;
		goesWon = atWin;
		open = false;
		demo = rec = null;
		takes.Clear(); logs.Clear();
		DropGhosts();
		trips = 0;
		at = 0;
		main = null;
		boxes.Clear();
		phase = LIVE;
		DoorBegin();
		LeanHeld(k);
		if (!atWin) ShuttersShut();         // (at the win, as the press, it is as it is)
		GoTake(mo);
		GoesDoors(true);
		if (atWin) Say("The fight is won, and its clock door stays: through it you are here again,\nas it is now, and every go of yours from now on with you.");
		else Say("A door with a clock on it: through it you are here again,\nas you first came in, and every earlier go of yours with you.");
	}

	// A door in the player's hands as they first come in is, as at the first
	// entry, leaning at the time door. (And no earlier self holds anything.)
	void LeanHeld(int k)
	{
		Line l = Doors().FindLine(HallLine(k, 1));
		dHold.Clear();
		for (int i = 0; i < dDoor.Size(); i++)
		{
			dHold.Push(-1);
			if (!d0Car[i] || !l) continue;
			Vector2 p = (l.v1.p + l.v2.p) / 2 + (l.delta.y, -l.delta.x).Unit() * 40;
			d0Car[i] = 0; d0Frame[i] = null;
			d0x[i] = p.x; d0y[i] = p.y; d0z[i] = l.frontsector.floorplane.ZAtPoint(p); d0a[i] = VectorAngle(l.delta.y, -l.delta.x);
		}
	}

	void GoesTick(PlayerPawn mo)
	{
		// killed: into box 1, at the start of a new go (shut.zs)
		if (stand && --stand == 0) mo.player.cheats &= ~CF_FROZEN;
		mo.bBuddha = true;
		if (mo.health <= 1) GoesKilled(mo);
		int k, b;
		[k, b] = Where(mo.pos.xy);
		if (k != fight || b < 0) { mo.bBuddha = false; EndGoes(); return; }       // out by a way that is not a time door
		if (at == 0 && b > 0) NextGo(mo);
		else if (at > 0 && b == 0) at = 0;
		GoWatch(ot);
		RecordTake(mo);
		PlayGhosts(mo);
		ParadoxWatch(mo);           // paradox.zs: touching an earlier self ends the universe
		if (paradox) return;
		GhostDoors();
		GhostPresses();
		ot++;
	}

	// What the player has done to doors since they were last looked at is
	// written down as done at tic t of this go, with how each was found.
	// (What earlier selves do is not: DoorSet knows it at once.) A door taken
	// in the same tic as another is hung (a swap) comes first.
	void GoWatch(int t)
	{
		AjarGoLog lg = logs[logs.Size() - 1];
		for (int i = 0; i < dDoor.Size(); i++)
		{
			AjarDoor d = dDoor[i];
			if (!d) continue;
			bool leans = !d.frame && !d.carried;
			if (d.frame == dFrame[i] && d.carried == dCar[i]
				&& (!leans || (d.pos.x == dx[i] && d.pos.y == dy[i] && d.pos.z == dz[i] && d.angle == da[i]))) continue;
			int n = lg.tic.Size();
			if (d.carried) while (n > 0 && lg.tic[n - 1] == t && !lg.car[n - 1]) n--;
			lg.tic.Insert(n, t); lg.door.Insert(n, i); lg.car.Insert(n, d.carried); lg.frm.Insert(n, d.frame);
			lg.x.Insert(n, d.pos.x); lg.y.Insert(n, d.pos.y); lg.z.Insert(n, d.pos.z); lg.a.Insert(n, d.angle);
			lg.fCar.Insert(n, dCar[i]); lg.fFrm.Insert(n, dFrame[i]); lg.fx.Insert(n, dx[i]); lg.fy.Insert(n, dy[i]);
			DoorKnow(i);
			dTouched[i] = 1;
		}
	}

	// Every earlier self does what it did to doors at this tic, if it can.
	void GhostDoors()
	{
		let h = Doors();
		for (int i = 0; i < takes.Size() - 1 && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			AjarGhost g = i < ghosts.Size() ? ghosts[i] : null;
			for (; lg.next < lg.tic.Size() && lg.tic[lg.next] <= ot; lg.next++)
			{
				int e = lg.next, di = lg.door[e];
				AjarDoor d = dDoor[di];
				if (!d || lg.broken.Find(di) < lg.broken.Size()) continue;
				bool found;
				if (lg.fCar[e]) found = d.carried && h.carried != d && dHold[di] == i;
				else if (lg.fFrm[e]) found = d.frame == lg.fFrm[e] && !d.carried;
				else found = !d.frame && !d.carried && (d.pos.xy - (lg.fx[e], lg.fy[e])).Length() < 8;
				AjarFrame f = lg.frm[e];
				if (!found || (f && f.door && f.door != d)) { lg.broken.Push(di); continue; }
				DoorSet(di, f, lg.car[e], (lg.x[e], lg.y[e], lg.z[e]), lg.a[e]);
				dHold[di] = lg.car[e] ? i : -1;
				if (g && (f || lg.car[e])) g.A_StartSound(f ? "doors/dr1_open" : "doors/dr1_clos", CHAN_AUTO);
			}
			// its go is over: what it holds is left leaning where it went
			AjarTake t = takes[i];
			int n = t.x.Size();
			if (ot == n && n > 0) for (int di = 0; di < dDoor.Size(); di++)
			{
				if (dHold[di] != i) continue;
				DoorSet(di, null, false, (t.x[n - 1], t.y[n - 1], t.z[n - 1]), t.ang[n - 1]);
				dHold[di] = -1;
			}
		}
	}

	// Every door that has been touched as it was when the room was first entered.
	void FirstDoors()
	{
		for (int i = 0; i < dDoor.Size(); i++)
			if (dTouched[i]) DoorSet(i, d0Frame[i], d0Car[i], (d0x[i], d0y[i], d0z[i]), d0a[i]);
		for (int i = 0; i < dHold.Size(); i++) dHold[i] = -1;
	}

	// Through the time door: the box, at the start of a new go. (`killed`:
	// the player was put there, shut.zs.)
	void NextGo(PlayerPawn mo, bool killed = false)
	{
		GoWatch(ot);                // (the last of what was done)
		let h = Doors();
		AjarDoor had = h.carried;
		DropGhosts();
		FirstDoors();
		for (int i = 0; i < logs.Size(); i++) { logs[i].next = 0; logs[i].pNext = 0; logs[i].kNext = 0; logs[i].broken.Clear(); }
		for (int i = 0; i < takes.Size(); i++) takes[i].next = 0;
		PressesUp();
		ShuttersShut();
		GoTake(mo);
		at = 1;
		mo.A_SetBlend(killed ? "ff2010" : "white", 1.0, 40);
		mo.A_StartSound("misc/teleport", CHAN_AUTO);
		string door = had ? "\nThe " .. had.Label() .. " door does not come through: it is where it was." : "";
		string first = goesWon ? "as when the fight was won" : "as when you first came in";
		if (killed) Say(String.Format("You were killed. Go %d: it is %s,\nand you are here again.", takes.Size(), first) .. door);
		else Say(String.Format("Go %d. It is %s,\nand your earlier selves do again what they did.", takes.Size(), first) .. door);
	}

	// What the earlier selves hold is left leaning where they stand.
	void LeaveHeld()
	{
		for (int i = 0; i < dHold.Size(); i++)
		{
			int gi = dHold[i];
			if (gi < 0) continue;
			Actor g = gi < ghosts.Size() ? ghosts[gi] : null;
			if (g) DoorSet(i, null, false, g.pos, g.angle);
			dHold[i] = -1;
		}
	}

	void EndGoes()
	{
		LeaveHeld();
		GoesDoors(false);
		DropGhosts();
		takes.Clear(); logs.Clear();
		if (won.Find(fight) == won.Size()) won.Push(fight);      // (a fight that became a room of goes is won already)
		goes = false;
		phase = IDLE;
		at = 0;
	}

	// AjarAnew: every go is forgotten, and this one is the first.
	void Anew(PlayerPawn mo)
	{
		if (!goes)
		{
			Say("Nothing to forget here.");
			return;
		}
		DropGhosts();
		FirstDoors();
		PressesUp();
		ShuttersShut();
		takes.Clear(); logs.Clear();
		GoTake(mo);
		mo.A_SetBlend("a0d0ff", 0.8, 30);
		mo.A_StartSound("misc/teleport", CHAN_AUTO);
		Say(goesWon ? "Every go since the win is forgotten. Nobody else is here,\nand the doors are as when the fight was won."
			: "Every go is forgotten. Nobody else is here,\nand the doors are as when you first came in.");
	}

	int GhostsHere()
	{
		int n = 0;
		for (int i = 0; i < ghosts.Size(); i++) if (ghosts[i]) n++;
		return n;
	}

	// The clock at the top: this go's tic over the longest earlier go's length.
	ui bool GoesClock()
	{
		if (takes.Size() < 2) return false;
		int len = 0;
		for (int i = 0; i < takes.Size() - 1; i++) len = max(len, takes[i].x.Size());
		if (ot >= len) return true;
		string o = String.Format("%d:%02d / %d:%02d", ot / 35 / 60, ot / 35 % 60, len / 35 / 60, len / 35 % 60);
		Screen.DrawText(BigFont, Font.CR_WHITE, 320 - BigFont.StringWidth(o) / 2, 12, o, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
		TableBar(len);              // table.zs: what the earlier selves will do
		return true;
	}

	// --- the tests (map PLATE) ------------------------------------------------
	int plateEnd, plateStep;
	bool plateOk;

	void Walk(Actor mo, Vector2 v) { mo.vel.xy = v; }

	// MODE=3: the sprung frame alone; three goes, the far room's frame too, and out.
	void PlateScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor red = Door32(1), blue = Door32(2);
		AjarFrame f1 = h.FindFrame(101), f2 = h.FindFrame(102);
		Line l1 = h.FindLine(101), l2 = h.FindLine(102);
		AjarPlate p1 = h.PlateFor(f1), p2 = h.PlateFor(f2);
		int g = goes ? takes.Size() : 0, o = ot;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) goes=%d go=%d ot=%d at=%d selves=%d carried=%s p1=%d p2=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, goes, g, o, at, GhostsHere(), h.carried ? h.carried.Label() : "-", p1 && p1.pressed, p2 && p2.pressed);
		if (t == 3) Check("begun", goes && phase == LIVE && g == 1 && p1 && p2 && red && blue && f1 && f2);

		// --- 1: alone, the first go ---
		if (g == 1)
		{
			if (o == 10) { Go(mo, 400, 430, 0, 270); red.Used(mo); }
			if (o == 14) { Go(mo, 256, 490, 0, 90); f1.Activate(mo); }
			if (o == 16) Check("hungShut", red.frame == f1 && red.bInvisible && (l1.flags & Line.ML_BLOCKEVERYTHING) && (l1.flags & Line.ML_BLOCKSIGHT));
			if (o > 16 && o <= 40) Walk(mo, (0, 8));
			if (o == 42)
			{
				Check("shutWithoutThePlate", mo.pos.y < 528 && mo.pos.y > 400 && red.frame == f1);
				FLineTraceData ld;
				mo.LineTrace(90, 300, 0, 0, 32, data: ld);
				Check("noShotThrough", ld.HitType == TRACE_HitWall && ld.HitLine == l1);
			}
			if (o == 45) Go(mo, 256, 200, 0, 90);
			if (o == 48) Check("opensWithThePlate", p1.pressed && !(l1.flags & Line.ML_BLOCKING) && !(l1.flags & Line.ML_BLOCKSIGHT) && !red.bInvisible);
			if (o == 55) Go(mo, 256, 300, 0, 90);
			if (o == 58) Check("shutsAgain", !p1.pressed && (l1.flags & Line.ML_BLOCKING) && red.bInvisible && red.frame == f1);
			if (o == 60) Go(mo, 256, 200, 0, 90);
			// --- 2: on the plate six seconds, then out by the time door ---
			if (o == 272) Go(mo, 40, 256, 0, 180);
			if (o > 272 && o < 300) Walk(mo, (-8, 0));
		}
		// --- 3: the second go: the earlier self hangs RED and holds it open ---
		if (g == 2)
		{
			if (o == 2)
			{
				Line bl = h.FindLine(BoxLine(1, 1)), hl = h.FindLine(HallLine(1, 1));
				int k, b;
				[k, b] = Where(mo.pos.xy);
				Check("inTheBoxAndOpenAtOnce", at == 1 && b == 1 && !(bl.flags & Line.ML_BLOCKING) && !(hl.flags & Line.ML_BLOCKING));
				Check("doorsAsAtTheStart", !red.frame && !red.carried && !red.bInvisible && Near(red, 400, 400) && !f1.door && !h.carried && GhostsHere() == 1);
			}
			if (o == 3) Go(mo, -240, 256, 0, 0);
			if (o > 3 && o <= 12) Walk(mo, (8, 0));
			if (o == 14) Check("outOfTheBox", at == 0 && mo.pos.x > -20 && mo.pos.x < 200);
			if (o == 20) Check("myEarlierSelfHangsIt", red.frame == f1 && !h.carried && red.bInvisible && (l1.flags & Line.ML_BLOCKING));
			// in the doorway when the earlier self steps off the plate
			if (o == 49) Go(mo, 256, 522, 0, 90);
			if (o == 50) Check("heldOpen", p1.pressed && !(l1.flags & Line.ML_BLOCKING));
			if (o == 60) Check("clearOfTheDoorway", (l1.flags & Line.ML_BLOCKING) && mo.pos.y < 504 && mo.pos.y > 400 && mo.TestMobjLocation());
			if (o == 65) Check("myEarlierSelfHoldsIt", p1.pressed && red.frame == f1 && !(l1.flags & Line.ML_BLOCKING) && !red.bInvisible);
			if (o == 66) Go(mo, 256, 470, 0, 90);
			if (o > 66 && o <= 80) Walk(mo, (0, 8));
			if (o == 82) Check("through", mo.pos.y > 690 && mo.pos.y < 1216);
			// --- 4: BLUE in the far room's frame, held by this self on its plate ---
			if (o == 84) { Go(mo, 256, 1070, 0, 90); blue.Used(mo); }
			if (o == 86) { Go(mo, 490, 960, 0, 0); f2.Activate(mo); }
			if (o == 88) Check("secondShut", blue.frame == f2 && (l2.flags & Line.ML_BLOCKING));
			if (o == 90) Go(mo, 160, 960, 0, 0);
			if (o == 93) Check("secondOpens", p2.pressed && !(l2.flags & Line.ML_BLOCKING));
			// back through RED while the first self still holds it, and out
			if (o == 150) Go(mo, 256, 740, 0, 270);
			if (o > 150 && o <= 166) Walk(mo, (0, -8));
			if (o == 168) Check("backThroughRed", mo.pos.y < 528 && mo.pos.y > 300 && at == 0 && !p2.pressed);
			if (o == 170) Go(mo, 40, 256, 0, 180);
			if (o > 170 && o < 200) Walk(mo, (-8, 0));
		}
		// the third go: the first self holds RED, the second BLUE; through both
		if (g == 3)
		{
			if (o == 3) Go(mo, -240, 256, 0, 0);
			if (o > 3 && o <= 12) Walk(mo, (8, 0));
			if (o == 20) Check("twoSelves", GhostsHere() == 2 && red.frame == f1);
			// (through RED and BLUE after the second self: it walks through RED at 66, and on the
			// path behind it this self would touch it, paradox.zs)
			if (o == 95) Check("mySecondSelfHoldsIt", blue.frame == f2 && p2.pressed && !(l2.flags & Line.ML_BLOCKING));
			if (o == 96) Go(mo, 256, 470, 0, 90);
			if (o > 96 && o <= 110) Walk(mo, (0, 8));
			if (o == 112) Check("throughAgain", mo.pos.y > 690);
			if (o == 120) Go(mo, 470, 960, 0, 0);
			if (o > 120 && o <= 135) Walk(mo, (8, 0));
		}
		if (!goes && t > 50 && !plateEnd)
		{
			plateEnd = t;
			Line hl = h.FindLine(HallLine(1, 1));
			Check("throughBoth", mo.pos.x > 690 && phase == IDLE && won.Find(1) < won.Size() && !GhostsHere() && !takes.Size());
			Check("timeDoorShut", (hl.flags & Line.ML_BLOCKING) && (h.FindLine(BoxLine(1, 1)).flags & Line.ML_BLOCKING));
		}
		if (plateEnd && t == plateEnd + 2) Go(mo, 860, 960, 0, 0);
		if (plateEnd && t > plateEnd + 2 && t < plateEnd + 20) Walk(mo, (8, 0));
	}

	// MODE=4: the conflict rule, six goes, and beginning anew.
	void GoesScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor red = Door32(1);
		AjarFrame f1 = h.FindFrame(101);
		int g = goes ? takes.Size() : 0, o = ot;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) goes=%d go=%d ot=%d at=%d selves=%d carried=%s step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, goes, g, o, at, GhostsHere(), h.carried ? h.carried.Label() : "-", plateStep);
		if (t == 0) plateOk = true;
		// --- 5: go 1 hangs RED; in go 2 the player has taken it first ---
		if (plateStep == 0 && g == 1)
		{
			if (o == 10) { Go(mo, 400, 430, 0, 270); red.Used(mo); }
			if (o == 14) { Go(mo, 256, 490, 0, 90); f1.Activate(mo); }
			if (o == 16) Check("hung", red.frame == f1);
			if (o == 20) Go(mo, 40, 256, 0, 180);
			if (o > 20 && o < 45) Walk(mo, (-8, 0));
		}
		if (plateStep == 0 && g == 2)
		{
			if (o == 3) { Go(mo, 400, 430, 0, 270); red.Used(mo); }
			if (o == 5) Check("tookFirst", h.carried == red);
			if (o == 6) Go(mo, 150, 380, 0, 180);      // out of the first self's way to RED (paradox.zs)
			if (o == 20)
			{
				AjarGhost e = ghosts.Size() ? ghosts[0] : null;
				Check("mimedNotDone", h.carried == red && !red.frame && !f1.door && red.bInvisible && e && Near(e, 256, 490, 4)
					&& logs[0].broken.Size() == 1);
			}
		}
		// --- 6: on through the one box, to the sixth go ---
		if (plateStep == 0 && g >= 2)
		{
			if (o == 2)
			{
				int k, b;
				[k, b] = Where(mo.pos.xy);
				plateOk = plateOk && at == 1 && b == 1 && !(h.FindLine(BoxLine(1, 1)).flags & Line.ML_BLOCKING) && GhostsHere() == g - 1;
			}
			if (g == 6 && o == 3)
			{
				Check("sixGoes", plateOk && GhostsHere() == 5 && takes.Size() == 6 && logs.Size() == 6);
				// --- 7: begin anew ---
				Go(mo, -370, 256, 0, 180);
				AjarAnew w = AjarAnew(ThinkerIterator.Create("AjarAnew").Next());
				if (w) w.Used(mo);
				plateStep = 1;
			}
			// each go out by the time door 10 tics after the one before: on its heels, it would touch it (paradox.zs)
			else if (o == 12 + 10 * g) Go(mo, 40, 256, 0, 180);
			else if (o > 12 + 10 * g && o < 35 + 10 * g) Walk(mo, (-8, 0));
		}
		if (plateStep == 1 && g == 1)
		{
			if (o == 3) Check("forgotten", !GhostsHere() && takes.Size() == 1 && !red.frame && !red.carried && !red.bInvisible && Near(red, 400, 400)
				&& !h.carried && !f1.door && at == 1);
			if (o == 5) Go(mo, 40, 256, 0, 180);
			if (o > 5 && o < 30) Walk(mo, (-8, 0));
		}
		if (plateStep == 1 && g == 2 && o == 3) { Check("oneSelfAfter", GhostsHere() == 1); plateStep = 2; }
	}

	// MODE=5: the paradox (paradox.zs). Three goes that start together, then
	// begin anew; four goes: in the box, after a copy's time, beside one, and
	// the touch, which ends it all.
	int pdxStep, pdxTouch, pdxOt;
	bool pdxAtTouch;
	Vector3 pdxFell;
	const PDX_HX = 300;
	const PDX_HY = 150;

	bool InHall(Actor a)
	{
		int k, b;
		[k, b] = Where(a.pos.xy);
		return k == fight && b == 0;
	}

	bool InBox(Actor a)
	{
		int k, b;
		[k, b] = Where(a.pos.xy);
		return k == fight && b > 0;
	}

	void ParadoxScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		int g = goes ? takes.Size() : 0, o = ot;
		if (t % 35 == 0 || (g && o < 2)) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) goes=%d go=%d ot=%d at=%d selves=%d step=%d paradox=%d health=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, goes, g, o, at, GhostsHere(), pdxStep, paradoxes, mo.health);
		if (paradox)
		{
			if (!pdxTouch)
			{
				pdxTouch = t;
				pdxFell = mo.pos;
				pdxOt = o;
				pdxAtTouch = pdxStep == 3 && paradoxes == 1 && paradoxCopy == 3 && mo.health <= 0 && (mo.player.cheats & CF_GODMODE)
					&& ghosts.Size() > 2 && !ghosts[2] && paradoxSaid == 0 && takes.Size() == 4;     // (said at the blast, PDX_HOLD)
				Console.Printf("AJARTEST info touched at t=%d o=%d: now=%d health=%d", t, o, pdxAtTouch, mo.health);
			}
			if (t == pdxTouch + 70)
			{
				Check("touchIsParadox", pdxAtTouch && paradoxes == 1 && mo.health <= 0 && mo.player.health <= 0 && InHall(mo) && at == 0
					&& (mo.pos.xy - pdxFell.xy).Length() < 64 && goes && takes.Size() == 4 && ot == pdxOt && paradoxSaid >= 1);
			}
			// the wave has taken every copy and monster; then the dark (paradox.zs)
			if (t == pdxTouch + PDX_HOLD + 60) Check("allGoneToLight", ParadoxAllGone() && paradoxes == 1 && mo.health <= 0);
			if (t == pdxTouch + PDX_HOLD + 180) Check("theDark", ParadoxDark() && paradoxes == 1 && mo.health <= 0 && InHall(mo) && ot == pdxOt);
			return;
		}
		// --- before begin anew: go 2 and go 3 walk one path from one start ---
		if (pdxStep == 0)
		{
			if (g == 1)
			{
				if (o == 3) Go(mo, 40, 256, 0, 180);
				if (o > 3 && o < 30) Walk(mo, (-8, 0));
			}
			if (g == 2 || g == 3)
			{
				if (o == 1) Go(mo, -300, 256, 0, 0);
				if (o > 1 && o <= 45) Walk(mo, (8, 0));
				if (g == 3 && o == 40)
					Check("startTogetherIsSafe", !paradoxes && mo.health > 0 && ghosts.Size() > 1 && ghosts[1] && Touching(mo, ghosts[1])
						&& InHall(mo) && InHall(ghosts[1]) && mo.pos.x > 60);
			}
			if (g == 2)
			{
				if (o == 50) Go(mo, 40, 256, 0, 180);
				if (o > 50 && o < 75) Walk(mo, (-8, 0));
			}
			if (g == 3 && o == 46)
			{
				Go(mo, -370, 256, 0, 180);
				AjarAnew w = AjarAnew(ThinkerIterator.Create("AjarAnew").Next());
				if (w) w.Used(mo);
				pdxStep = 1;
			}
			return;
		}
		// --- after it: go 1 is short; go 2 stays where it came in ---
		if (pdxStep == 1 && g == 1)
		{
			if (o == 3) Go(mo, 40, 256, 0, 180);
			if (o > 3 && o < 30) Walk(mo, (-8, 0));
		}
		if (pdxStep == 1 && g == 2)
		{
			if (o == 1) Go(mo, -300, 256, 0, 0);
			if (o == 61) Go(mo, 40, 256, 0, 180);
			if (o > 61 && o < 85) Walk(mo, (-8, 0));
		}
		// go 3: in the box, out of the copy of go 2 and into it again; where it ended; beside where go 4 will be
		if (pdxStep == 1 && g == 3)
		{
			AjarTake two = takes[1];
			AjarGhost e = ghosts.Size() > 1 ? ghosts[1] : null;
			if (o == 1) Go(mo, -300, 304, 0, 0);
			if (o == 6) Go(mo, -300, 256, 0, 0);
			if (o == 8) Check("inTheBoxIsSafe", !paradoxes && mo.health > 0 && e && Touching(mo, e) && InBox(mo) && InBox(e)
				&& parted.Size() > 1 && parted[1]);
			if (o == 10) Go(mo, -370, 200, 0, 0);
			int n = two.x.Size();
			if (o == 90) Go(mo, two.x[n - 1], two.y[n - 1], two.z[n - 1], 0);
			if (o == 92) Check("afterItsTimeIsSafe", !paradoxes && mo.health > 0 && !e && n < 90 && InHall(mo));
			if (o == 100) Go(mo, PDX_HX, PDX_HY, 0, 90);
			if (o == 200) Go(mo, 40, 256, 0, 180);
			if (o > 200 && o < 225) Walk(mo, (-8, 0));
		}
		if (pdxStep == 1 && g == 4) pdxStep = 2;
		// go 4: beside the copy of go 3 (34 apart), armour and invulnerability on; then into it
		if (pdxStep == 2 && g == 4)
		{
			AjarGhost e = ghosts.Size() > 2 ? ghosts[2] : null;
			if (o == 3) Go(mo, PDX_HX + 34, PDX_HY, 0, 180);
			if (o == 120) { mo.GiveInventory("BlueArmor", 1); mo.GiveInventory("PowerInvulnerable", 1); }
			if (o == 125)
			{
				Check("nearIsSafe", !paradoxes && mo.health > 0 && e && !Touching(mo, e) && abs(mo.pos.x - e.pos.x) < 35 && abs(mo.pos.y - e.pos.y) < 1
					&& InHall(mo) && InHall(e) && parted.Size() > 2 && parted[2]);
				pdxStep = 3;
			}
		}
		if (pdxStep == 3)
		{
			if (o > 125 && o < 200) Walk(mo, (-4, 0));
			if (o == 200) Check("touchIsParadox", false);
		}
	}
}
