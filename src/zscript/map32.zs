// MAP32 "Double Shift" (tools/map_secret2.py): what it adds to stepping out
// of a fight, and its walk-through (MAP=MAP32 MODE=3 tools/smoke.sh); winding
// a fight that is watched (MODE=4).

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

	// --- winding a fight that is watched (MODE=4) ---------------------------------
	// Shop 1, its first go made long: the leaf is carried about for ten
	// seconds before it is hung, so that winding on from the wing goes past
	// the moment the earlier self hangs it.
	AjarWind Plate32(bool on)
	{
		let it = ThinkerIterator.Create("AjarWind");
		AjarWind w;
		while (w = AjarWind(it.Next()))
		{
			int k, b;
			[k, b] = Where(w.pos.xy);
			if (k == fight && b == at && (w.args[0] != 0) == on) return w;
		}
		return null;
	}
	int testHp, testArm, testLen;

	void Wind32Script(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		let h = Doors();
		if (t == 0) { testA = Leaf32(true); testB = Leaf32(false); }
		AjarDoor a = testA, b = testB;
		AjarFrame fa = h.FindFrame(111), fb = h.FindFrame(112);
		Line la = h.FindLine(111), lb = h.FindLine(112);
		Quiet(mo);
		AjarTrack self = boxes.Size() ? boxes[boxes.Size() - 1] : null;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d at=%d trips=%d rt=%d len=%d self=%d hp=%d arm=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, at, trips, rt, main ? main.first.Size() : 0, self ? self.first.Size() : -1,
			mo.health, mo.CountInv("BasicArmor"));

		if (t == 1)
		{
			int n = 0;
			let it = ThinkerIterator.Create("AjarWind");
			while (it.Next()) n++;
			Check("plates", n == 18);
		}
		// the first go: the leaf taken at once, hung ten seconds later, out
		if (t == 10) Go(mo, 300, -120, 64, 270);
		if (t == 12) { Check("begun", phase == LIVE && fight == 1); a.Used(mo); mo.GiveInventoryType("GreenArmor"); }
		if (t == 400) { Go(mo, 192, -170, 64, 270); fa.Activate(mo); }
		if (t == 402) Check("leafHung", a.frame == fa && a.Shut());
		if (t == 480) Go(mo, 960, 640, 0, 0);
		if (t > 480 && t < 510) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 512) { Check("out", phase == REPLAY && at == 1 && main.first.Size() > 450); testLen = main.first.Size(); }
		// in the wing: the twin hung; the earlier self still has the leaf in hand
		if (t == 514) { Go(mo, -340, 450, 64, 90); b.Used(mo); }
		if (t == 518) { Go(mo, -370, 352, 64, 180); fb.Activate(mo); }
		if (t == 520) Check("twinHung", b.frame == fb && !a.frame && a.carried);
		// on: to two seconds before the handover; the leaf hangs, the Pair is joined and held
		if (t == 522)
		{
			Go(mo, -60, 256, 64, 0);
			testHp = mo.health; testArm = mo.CountInv("BasicArmor");
			let w = Plate32(true);
			Check("platesInTheWing", w && Plate32(false));
			if (w) w.Used(mo);
			Check("woundOn", rt == testLen - 70 && self.first.Size() == rt && Selves() == 1);
			Check("leafHangsAgain", a.frame == fa && b.frame == fb && a.args[0] == 112 && b.args[0] == 111
				&& (la.flags & Line.ML_BLOCKEVERYTHING) && (lb.flags & Line.ML_BLOCKEVERYTHING));
			Check("itCosts", mo.health == testHp - 10 && mo.CountInv("BasicArmor") == testArm - 5);
			Console.Printf("AJARTEST rt=%d len=%d self=%d selves=%d hp=%d arm=%d", rt, testLen, self.first.Size(), Selves(), mo.health, mo.CountInv("BasicArmor"));
		}
		if (t == 530)
		{
			int was = rt;
			Plate32(true).Used(mo);
			Check("noFurtherOn", rt == was && mo.health == testHp - 10 && mo.CountInv("BasicArmor") == testArm - 5);
		}
		// back: to the start; the leaf leans where it did then, the twin still hangs
		if (t == 540)
		{
			Go(mo, -60, 448, 64, 0);
			Plate32(false).Used(mo);
			Check("woundBack", rt == 0 && self.first.Size() == 0 && !self.slot.Size());
			Check("leafAsAtTheStart", !a.frame && !a.carried && Near(a, 300, -150) && !a.bInvisible);
			Check("myTwinStillHangs", b.frame == fb && h.carried != b);
			Check("itCostsAgain", mo.health == testHp - 20 && mo.CountInv("BasicArmor") == testArm - 10);
			Plate32(false).Used(mo);
			Check("noFurtherBack", rt == 0 && mo.health == testHp - 20);
		}
		if (t == 545)
		{
			Check("myselfThroughTheGlass", Selves() == 1 && self.first.Size() == rt && rt == 5);
			Console.Printf("AJARTEST rt=%d self=%d selves=%d", rt, self.first.Size(), Selves());
		}
		if (t == 550)
		{
			int was = rt;
			mo.health = mo.player.health = 10;
			Plate32(false).Used(mo);
			Check("notWithoutTheHealth", rt == was && mo.health == 10);
			mo.health = mo.player.health = 100;
		}
		// it plays on from the start: the earlier self takes the leaf and hangs it again
		if (t > 550 && testStep == 0 && phase == REPLAY && rt == testLen - 40)
		{
			Check("joinedAgain", a.frame == fa && b.frame == fb && a.args[0] == 112 && (lb.flags & Line.ML_BLOCKEVERYTHING));
			testStep = 1;
		}
		// the handover: open, and through to the gallery
		if (t > 550 && testStep == 1 && phase == LIVE)
		{
			Check("open", at == 1 && a.args[0] == 112 && !(lb.flags & Line.ML_BLOCKING) && t >= 540 + testLen);
			Go(mo, -370, 352, 64, 180);
			testStep = 2;
			testN = t;
		}
		if (testStep == 2 && t < testN + 22) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (testStep == 2 && t == testN + 26) { Check("onTheGallery", mo.pos.y < 0 && mo.pos.y > -192 && mo.pos.x > 100 && at == 0); testStep = 3; }
	}
}
