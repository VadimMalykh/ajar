// MAP32 "Double Shift" (tools/map_secret2.py): what it adds to stepping out
// of a fight, and its walk-through (MAP=MAP32 MODE=3 tools/smoke.sh).

extend class AjarTimeHandler
{
	// A fight can be left unwon here (its wing leads on): it is over when the
	// player stands in the hall of another. Its time doors are shut.
	void Quit()
	{
		let h = Doors();
		if (at) { h.Link(BoxLine(fight, at), 0, TIME_TEX); if (used) h.Link(used, 0, TIME_TEX); }
		HallDoors(0);
		DropPuppets(-1);
		Unfreeze();
		pending.Clear(); pendingTics.Clear();
		phase = IDLE;
		at = 0;
		open = false;
		main = null;
		boxes.Clear();
		slotCls.Clear();
	}

	AjarDoor Leaf32(bool east)
	{
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next())) if (d.IsPair() && (d.pos.x > 0) == east) return d;
		return null;
	}
	AjarDoor testA, testB;

	// Is fight k's steel door up?
	bool SteelUp(int k)
	{
		let it = level.CreateSectorTagIterator(3090 + 100 * k);
		int i = it.Next();
		return i >= 0 && level.sectors[i].ceilingplane.ZatPoint(level.sectors[i].centerspot) > level.sectors[i].floorplane.ZatPoint(level.sectors[i].centerspot) + 56;
	}

	AjarDoor Door32(int colour)
	{
		let it = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(it.Next())) if (!d.IsPair() && d.args[1] == colour) return d;
		return null;
	}

	// The test's monsters stand still and are not hurt; `kill`: those of fight k die.
	void Quiet(Actor mo, int kill = 0)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (kill && k == kill) { a.bDormant = false; a.DamageMobj(mo, mo, 100000, 'None'); }
			else a.bDormant = true;
		}
	}

	void Map32Script(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		if (t == 0) { testA = Leaf32(true); testB = Leaf32(false); }
		AjarDoor a = testA, b = testB, yellow = Door32(4), red = Door32(1), blue = Door32(2);
		AjarFrame fa = h.FindFrame(111), fb = h.FindFrame(112), fy = h.FindFrame(113), f1 = h.FindFrame(190), f2 = h.FindFrame(191);
		Line la = h.FindLine(111), lb = h.FindLine(112);
		Quiet(mo, t >= 365 && t <= 610 && t % 35 == 15 ? 2 : 0);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d fight=%d at=%d trips=%d rt=%d len=%d left=%d chain=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, fight, at, trips, rt, main ? main.first.Size() : 0, phase ? Left() : 0, h.chainLen);

		// --- 1: the leaf on the gallery, down, out; the twin in the wing ---
		if (t == 10) Go(mo, 300, -120, 64, 270);
		if (t == 12) { Check("begun1", phase == LIVE && fight == 1); a.Used(mo); }
		if (t == 16) { Go(mo, 192, -170, 64, 270); fa.Activate(mo); }
		if (t == 18) Check("leafHung", a.frame == fa && a.Shut());
		// YELLOW is not for this frame
		if (t == 20) { Go(mo, 80, -120, 64, 270); yellow.Used(mo); }
		if (t == 22) { Go(mo, 192, -170, 64, 270); fa.Activate(mo); }
		if (t == 24) { Check("tealOnly", h.carried == yellow && a.frame == fa); h.carried = null; h.DropDoor(yellow, mo); }
		if (t == 120) Go(mo, 960, 640, 0, 0);
		if (t > 120 && t < 150) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 152) Check("out1", phase == REPLAY && at == 1 && mo.pos.x < -16 && !h.carried);
		if (t == 154) { Go(mo, -340, 450, 64, 90); b.Used(mo); }
		if (t == 158) { Go(mo, -370, 352, 64, 180); fb.Activate(mo); }
		if (t == 170) Check("joinedAndHeld", a.frame == fa && b.frame == fb && a.args[0] == 112 && (la.flags & Line.ML_BLOCKEVERYTHING) && (lb.flags & Line.ML_BLOCKEVERYTHING));
		if (t == 262) { Check("open1", phase == LIVE && !(lb.flags & Line.ML_BLOCKING)); Go(mo, -370, 352, 64, 180); }
		if (t > 262 && t < 285) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 288) Check("onTheGallery", mo.pos.y < 0 && mo.pos.y > -192 && mo.pos.x > 100 && at == 0);
		// YELLOW through the Pair into the wing, into its frame, and on
		if (t == 290) { Go(mo, 192, -150, 64, 270); yellow.Used(mo); }
		if (t > 290 && t < 316) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 318) Check("yellowInTheWing", mo.pos.x < -16 && h.carried == yellow);
		if (t == 320) { Go(mo, -176, 200, 64, 270); fy.Activate(mo); }
		if (t > 320 && t < 348) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 352) Check("inShop2", mo.pos.x > 3000 && yellow.frame == fy);

		// --- 2: the fight is won, the steel door, the doorway ---
		if (t == 357) Go(mo, 3712, -100, 64, 90);
		if (t == 360) Check("begun2", phase == LIVE && fight == 2 && (h.FindLine(HallLine(1, 1)).flags & Line.ML_BLOCKING));
		if (t == 362) Go(mo, 3712, 300, 0, 90);
		if (t == 640) Check("won2", won.Find(2) < won.Size() && phase == IDLE);
		if (t == 700) { Check("steelOpen", SteelUp(2)); Go(mo, 4292, 128, 0, 0); }       // in the pit, before the steel door
		if (t > 700 && t < 738) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 739) Check("inShop3", mo.pos.x > 6000);

		// --- 3: RED on the gallery, down, out; BLUE in the wing; the line ---
		if (t == 740) Go(mo, 6444, -120, 64, 270);
		if (t == 742) { Check("begun3", phase == LIVE && fight == 3); red.Used(mo); }
		if (t == 746) { Go(mo, 6336, -170, 64, 270); f1.Activate(mo); }
		if (t == 748) Check("redHung", red.frame == f1 && !h.chainLen);
		if (t == 850) Go(mo, 7360, 896, 0, 0);
		if (t > 850 && t < 880) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 882) Check("out3", phase == REPLAY && at == 1 && fight == 3);
		if (t == 884) { Go(mo, 5804, 450, 64, 90); blue.Used(mo); }
		if (t == 888) { Go(mo, 5774, 352, 64, 180); f2.Activate(mo); }
		if (t == 900) Check("loopHeld", red.frame == f1 && blue.frame == f2 && h.chainLen == 2 && (h.FindLine(191).flags & Line.ML_BLOCKEVERYTHING));
		if (t == 1000) { Check("open3", phase == LIVE && h.chainLen == 2 && !(h.FindLine(191).flags & Line.ML_BLOCKING)); Go(mo, 5774, 352, 64, 180); }
		if (t > 1000) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
	}
}
