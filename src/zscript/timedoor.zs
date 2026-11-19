// Doors in a fight that is stepped out of (PLAN.md, "MAP32"; the test map
// TDOOR, tools/map_timedoor.py; MAP=TDOOR MODE=3 tools/smoke.sh).
//
// A door is not played back by a puppet: what was done to it is done again.
// Every change to a door while a fight is on is written down with the
// fight's tic (the one lived, or the one being watched from a box). When the
// player steps out, the doors are put as they were at the fight's first tic,
// and as the replay goes each change is made again for real: the door hangs,
// its far side opens. So an earlier self is a second pair of hands.
//
//  * A door is not taken through a time door: it is left leaning at it.
//  * While a fight is watched, a hung door that joins its hall to anywhere
//    is seen through but lets nothing pass (the past cannot be changed);
//    it opens when the fight is where it was left.

extend class AjarTimeHandler
{
	// the level's doors: as they were at the fight's first tic, and as last seen
	Array<AjarDoor> dDoor;
	Array<AjarFrame> d0Frame, dFrame;
	Array<int> d0Car, dCar, dTouched;
	Array<double> d0x, d0y, d0z, d0a, dx, dy, dz, da;
	// what was done to them, in the order of the fight's tics
	Array<int> deTic, deDoor, deCar;
	Array<AjarFrame> deFrame;
	Array<double> dex, dey, dez, dea;
	int dNext;                  // REPLAY: the next of them to be done again

	const HELD = Line.ML_BLOCKING | Line.ML_BLOCKEVERYTHING | Line.ML_BLOCKPROJECTILE | Line.ML_BLOCKHITSCAN | Line.ML_BLOCKSIGHT;

	void DoorKnow(int i)
	{
		AjarDoor d = dDoor[i];
		dFrame[i] = d.frame; dCar[i] = d.carried;
		dx[i] = d.pos.x; dy[i] = d.pos.y; dz[i] = d.pos.z; da[i] = d.angle;
	}

	// The fight begins: how every door is now.
	void DoorBegin()
	{
		dDoor.Clear(); d0Frame.Clear(); dFrame.Clear(); d0Car.Clear(); dCar.Clear(); dTouched.Clear();
		d0x.Clear(); d0y.Clear(); d0z.Clear(); d0a.Clear(); dx.Clear(); dy.Clear(); dz.Clear(); da.Clear();
		deTic.Clear(); deDoor.Clear(); deCar.Clear(); deFrame.Clear(); dex.Clear(); dey.Clear(); dez.Clear(); dea.Clear();
		dNext = 0;
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next()))
		{
			dDoor.Push(d); d0Frame.Push(d.frame); d0Car.Push(d.carried); dTouched.Push(0);
			d0x.Push(d.pos.x); d0y.Push(d.pos.y); d0z.Push(d.pos.z); d0a.Push(d.angle);
			dFrame.Push(null); dCar.Push(0); dx.Push(0); dy.Push(0); dz.Push(0); da.Push(0);
			DoorKnow(dDoor.Size() - 1);
		}
	}

	// What has been done to a door since it was last looked at is written
	// down as done at tic t.
	void DoorWatch(int t)
	{
		for (int i = 0; i < dDoor.Size(); i++)
		{
			AjarDoor d = dDoor[i];
			if (!d) continue;
			bool leans = !d.frame && !d.carried;
			if (d.frame == dFrame[i] && d.carried == dCar[i]
				&& (!leans || (d.pos.x == dx[i] && d.pos.y == dy[i] && d.pos.z == dz[i] && d.angle == da[i]))) continue;
			DoorKnow(i);
			dTouched[i] = 1;
			int at = deTic.Size();
			while (at > 0 && deTic[at - 1] > t) at--;
			deTic.Insert(at, t); deDoor.Insert(at, i); deCar.Insert(at, d.carried); deFrame.Insert(at, d.frame);
			dex.Insert(at, d.pos.x); dey.Insert(at, d.pos.y); dez.Insert(at, d.pos.z); dea.Insert(at, d.angle);
		}
	}

	// Door i is made to hang in f, or to be in someone's hands, or to lean at p.
	void DoorSet(int i, AjarFrame f, bool car, Vector3 p, double ang)
	{
		AjarDoor d = dDoor[i];
		if (!d) return;
		let h = Doors();
		if (d.frame && d.frame != f) h.Unhang(d.frame);
		if (f)
		{
			if (d.frame != f)
			{
				if (f.door) h.DropDoor(h.Unhang(f), f);
				if (h.carried == d) h.carried = null;
				h.Hang(d, f);
			}
		}
		else if (car)
		{
			if (h.carried != d) { d.carried = true; d.Hide(); }
		}
		else
		{
			if (h.carried == d) h.carried = null;
			d.carried = false;
			d.SetOrigin(p, false);
			d.angle = ang;
			d.Show();
		}
		DoorKnow(i);
	}

	// The player has stepped out: a door in their hands stays behind, and
	// every door is as it was when the fight began.
	void DoorLeave(Actor mo)
	{
		let h = Doors();
		if (h.carried)
		{
			AjarDoor d = h.carried;
			h.carried = null;
			d.carried = false;
			d.SetOrigin(playerWas, false);
			d.angle = mo.angle;
			d.Show();
			Say("The " .. d.Label() .. " door does not go through a door with a clock on it.\nIt is left leaning there.");
		}
		DoorWatch(FightTic());
		for (int i = 0; i < dDoor.Size(); i++)
			if (dTouched[i]) DoorSet(i, d0Frame[i], d0Car[i], (d0x[i], d0y[i], d0z[i]), d0a[i]);
		dNext = 0;
	}

	// REPLAY: what the player in the box has just done is written down, and
	// what was done at this tic of the fight is done again.
	void DoorPlay(int t)
	{
		DoorWatch(t);
		for (; dNext < deTic.Size() && deTic[dNext] <= t; dNext++)
			DoorSet(deDoor[dNext], deFrame[dNext], deCar[dNext], (dex[dNext], dey[dNext], dez[dNext]), dea[dNext]);
		DoorHold(true);
	}

	// The fight is where it was left: so are the doors (what was done in the
	// very tic of leaving, a door left at the time door, is done now).
	void DoorEnd()
	{
		DoorPlay(int.max);
		DoorHold(false);
	}

	// A hung door with one end in the hall of the fight: nothing passes it
	// while the fight is watched.
	void DoorHold(bool on)
	{
		let h = Doors();
		// a closed loop (the way out as a chain) is held whole if any of it is
		bool loop;
		for (int pass = 0; pass < 2; pass++)
		{
			let it = ThinkerIterator.Create("AjarFrame");
			AjarFrame f;
			while (f = AjarFrame(it.Next()))
			{
				if (!f.door || !f.door.args[0]) continue;
				Line a = h.FindLine(f.args[0]), b = h.FindLine(f.door.args[0]);
				if (!a || !b) continue;
				int k1, b1, k2, b2;
				[k1, b1] = Where(f.pos.xy);
				[k2, b2] = Where((b.v1.p + b.v2.p) / 2);
				bool inHall = (k1 == fight && b1 == 0) || (k2 == fight && b2 == 0);
				if (!pass) { if (inHall && h.InChain(f.door)) loop = true; continue; }
				if (!inHall && !(loop && h.InChain(f.door))) continue;
				if (on) { a.flags |= HELD; b.flags |= HELD; }
				else { a.flags &= ~HELD; b.flags &= ~HELD; }
			}
		}
	}

	// --- the test (map TDOOR, mode 3) -------------------------------------------
	AjarDoor TestLeaf(bool inHall)
	{
		for (int i = 0; i < dDoor.Size(); i++) if (dDoor[i] && dDoor[i].IsPair() && (d0x[i] > 0) == inHall) return dDoor[i];
		return null;
	}
	bool Near(Actor a, double x, double y, double r = 1) { return (a.pos.xy - (x, y)).Length() <= r; }

	void DoorScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor a = TestLeaf(true), b = TestLeaf(false);
		AjarFrame fa = h.FindFrame(121), fb = h.FindFrame(122);
		Line la = h.FindLine(121), lb = h.FindLine(122);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d at=%d trips=%d rt=%d len=%d events=%d next=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, at, trips, rt, main ? main.first.Size() : 0, deTic.Size(), dNext);
		if (t > 10 && t < 40) mo.vel.xy = (0, 8);
		if (t == 45) Check("begun", phase == LIVE && a && b && fa && fb);
		// the first go: the hall's leaf is hung alone, and out by the east door
		if (t == 50) { Go(mo, 600, 470, 0, 90); a.Used(mo); }
		if (t == 52) Check("took", h.carried == a);
		if (t == 60) { Go(mo, 640, 600, 0, 90); fa.Activate(mo); }
		if (t == 62) Check("hungAlone", a.frame == fa && a.Shut() && !h.carried);
		if (t == 150) Go(mo, 700, 320, 0, 0);
		if (t > 150 && t < 175) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 176)
		{
			Check("out", phase == REPLAY && at == 1);
			Check("putBack", !a.frame && !a.carried && !a.bInvisible && Near(a, 600, 500) && !fa.door);
			Go(mo, -44, 320, 64, 0);
		}
		// in the box, the twin is hung before the earlier self has hung its own
		if (t == 180) { Go(mo, -200, 350, 64, 90); b.Used(mo); }
		if (t == 184) { Go(mo, -128, 270, 64, 270); fb.Activate(mo); }
		if (t == 186) Check("twinAlone", b.frame == fb && b.Shut() && !a.frame && !h.carried);
		if (t == 203) Check("takenAgain", a.carried && a.bInvisible && !h.carried);
		if (t == 215)
		{
			Check("hungAgain", a.frame == fa && a.args[0] == 122 && b.args[0] == 121);
			Check("held", (la.flags & Line.ML_BLOCKEVERYTHING) && (lb.flags & Line.ML_BLOCKEVERYTHING));
			Go(mo, -128, 270, 64, 270);
		}
		if (t > 215 && t < 240) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 242) { Check("notThrough", mo.pos.x < 0 && phase == REPLAY); Go(mo, -44, 320, 64, 0); }
		// the fight is where it was left: the Pair is open, and is the way back
		if (t == 330)
		{
			Check("handedOver", phase == LIVE && at == 1);
			Check("open", !(la.flags & Line.ML_BLOCKING) && !(lb.flags & Line.ML_BLOCKING) && a.args[0] == 122);
			Go(mo, -128, 270, 64, 270);
		}
		if (t > 330 && t < 355) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 360) Check("through", mo.pos.x > 500 && mo.pos.z < 8 && at == 0);
		// the second go: the hall's leaf is taken down and carried at the south door
		if (t == 365) { Go(mo, 640, 600, 0, 90); fa.Activate(mo); }
		if (t == 367) Check("tookDown", h.carried == a && b.Shut());
		if (t == 370) Go(mo, 128, 80, 0, 270);
		if (t > 370 && t < 395) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 397)
		{
			Check("outAgain", phase == REPLAY && at == 2);
			Check("leftBehind", !h.carried);
			Check("putBack2", !a.frame && !a.carried && Near(a, 600, 500) && !b.frame && !b.carried && Near(b, -200, 380) && !fa.door && !fb.door);
			Go(mo, 384, 684, 64, 270);
		}
		// both earlier selves hang their leaves again, the one in the box too
		if (t == 450) Check("bothAgain", a.args[0] == 122 && b.args[0] == 121 && Selves() == 2 && (la.flags & Line.ML_BLOCKEVERYTHING));
		if (t == 800)
		{
			Check("handedOver2", phase == LIVE && at == 2);
			Check("asLeft", !a.frame && !a.carried && !a.bInvisible && Near(a, 128, 40, 100) && b.frame == fb && b.Shut());
		}
	}

	// --- MODE=4: the chain, a door hung by each of two selves ------------------
	AjarDoor TestDoor(int colour)
	{
		for (int i = 0; i < dDoor.Size(); i++) if (dDoor[i] && !dDoor[i].IsPair() && dDoor[i].args[1] == colour) return dDoor[i];
		return null;
	}

	void ChainScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor red = TestDoor(1), blue = TestDoor(2);
		AjarFrame f1 = h.FindFrame(190), f2 = h.FindFrame(191);
		Line l1 = h.FindLine(190), l2 = h.FindLine(191);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d at=%d rt=%d len=%d events=%d chain=%d line=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, at, rt, main ? main.first.Size() : 0, deTic.Size(), h.chainLen, h.onTheLine);
		if (t > 10 && t < 40) mo.vel.xy = (0, 8);
		// the first go: RED into the hall's brass frame
		if (t == 50) { Go(mo, 500, 470, 0, 90); red.Used(mo); }
		if (t == 60) { Go(mo, 592, 40, 0, 270); f1.Activate(mo); }
		if (t == 62) Check("redHung", red.frame == f1 && !h.chainLen && !(l1.flags & Line.ML_BLOCKING));
		if (t == 150) Go(mo, 700, 320, 0, 0);
		if (t > 150 && t < 175) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 176) { Check("out", phase == REPLAY && at == 1 && !red.frame && !f1.door); Go(mo, -44, 320, 64, 0); }
		// in the box: BLUE into its brass frame, before the earlier self has hung RED
		if (t == 180) { Go(mo, -40, 370, 64, 90); blue.Used(mo); }
		if (t == 184) { Go(mo, -200, 320, 64, 180); f2.Activate(mo); }
		if (t == 186) Check("blueHung", blue.frame == f2 && !h.chainLen && !(l2.flags & Line.ML_BLOCKING));
		if (t == 215)
		{
			Check("loopInReplay", red.frame == f1 && h.chainLen == 2);
			Check("loopHeld", (l1.flags & Line.ML_BLOCKEVERYTHING) && (l2.flags & Line.ML_BLOCKEVERYTHING));
			Go(mo, -200, 320, 64, 180);
		}
		if (t > 215 && t < 240) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 242) { Check("notThrough", mo.pos.x < 0 && mo.pos.x > -300 && !h.onTheLine); Go(mo, -44, 320, 64, 0); }
		// the fight is where it was left: through BLUE onto the line, and out of it by RED
		if (t == 330)
		{
			Check("handedOver", phase == LIVE && h.chainLen == 2 && !(l1.flags & Line.ML_BLOCKING) && !(l2.flags & Line.ML_BLOCKING));
			Go(mo, -200, 320, 64, 180);
		}
		if (t > 330) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 350) Check("onTheLine", h.onTheLine && mo.pos.x > 1900);
	}

	// --- MODE=5: a fight handed across -----------------------------------------
	void HandScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		AjarDoor blue = TestDoor(2);
		AjarFrame f2 = h.FindFrame(191);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d at=%d rt=%d left=%d pending=%d demon=(%d,%d,%d)",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, at, rt, Left(), pending.Size(),
			testDemon ? testDemon.pos.x : 0, testDemon ? testDemon.pos.y : 0, testDemon ? testDemon.pos.z : 0);
		if (t > 10 && t < 40) mo.vel.xy = (0, 8);
		// a demon on the player's heels at the east door
		if (t == 45)
		{
			Go(mo, 700, 320, 0, 0);
			testDemon = Actor.Spawn("Demon", (640, 320, 0));
			testDemon.GiveInventoryType("AjarSense");
			testDemon.target = mo;
		}
		if (t == 46) Check("inTheFight", Left() == 2);
		if (t > 45 && t < 70) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 71)
		{
			// (it is in the box at once if there is room at its door)
			int k, b;
			[k, b] = Where(testDemon.pos.xy);
			Check("followed", phase == REPLAY && (pending.Find(testDemon) < pending.Size() || b == 1) && fz.Find(testDemon) == fz.Size());
			Go(mo, -44, 320, 64, 0);
		}
		// BLUE in the box's frame: it opens onto the night room
		if (t == 75) { Go(mo, -40, 370, 64, 90); blue.Used(mo); }
		if (t == 80) { Go(mo, -200, 320, 64, 180); f2.Activate(mo); }
		if (t == 140)
		{
			int k, b;
			[k, b] = Where(testDemon.pos.xy);
			Check("inTheBox", !pending.Size() && b == 1 && !testDemon.bInvisible);
			Go(mo, -200, 320, 64, 180);
		}
		// through it, the demon after: then back (the test teleports) and BLUE is taken down
		if (t > 140 && t < 170) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 171) Check("ledOut", mo.pos.x > 1900);
		if (t > 171 && t < 195) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 400)
		{
			Check("delivered", testDemon.health > 0 && testDemon.pos.x > 1900);
			Go(mo, -200, 320, 64, 180);
			f2.Activate(mo);
		}
		if (t == 402) Check("shutAway", h.carried == blue && testDemon.pos.x > 1900 && (h.FindLine(191).flags & Line.ML_BLOCKING));
		if (t == 410) Check("outOfTheFight", phase == LIVE && Left() == 1);
	}
}
