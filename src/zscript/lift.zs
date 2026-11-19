// The lift (ajarmap.lift_button; the test map LIFT, tools/map_lift.py).
//
// A lift car is every sector with one tag: the car itself and the door
// recesses in its walls. Floor and ceiling move together, so a frame or a
// far side in the car rides with it, and a door that opens onto the car
// opens onto whichever floor the car is at.
//  * AjarLiftButton thing: args[0] = the car's sector tag, args[1] = the
//    floor height the button sends it to. Its line calls Thing_Activate.
// Whatever stands in an opening of the car when it is sent holds it there
// (the engine's doing: it does not fit under the lintel); the car goes on
// when the opening is clear.

class AjarLiftButton : Actor
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

	override void Activate(Actor activator)
	{
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (h) h.LiftSend(args[0], args[1], activator);
	}
}

extend class AjarHandler
{
	const LIFT_TAG = 700;
	const LIFT_SPEED = 32;        // 4 units a tic
	int liftKnown;                // 0: not looked yet; 1: the level has none; 2: it has
	Array<int> liftSectors;       // every sector that rides

	Sector LiftCar(int tag)
	{
		let it = level.CreateSectorTagIterator(tag);
		int i = it.Next();
		if (i < 0) return null;
		return level.sectors[i];
	}

	double LiftAt(int tag = LIFT_TAG)
	{
		Sector s = LiftCar(tag);
		return s ? s.floorplane.ZatPoint(s.centerspot) : 0;
	}

	bool LiftMoving(int tag = LIFT_TAG)
	{
		Sector s = LiftCar(tag);
		return s && (s.floordata || s.ceilingdata);
	}

	bool LiftSend(int tag, int z, Actor by = null)
	{
		Sector s = LiftCar(tag);
		if (!s) return false;
		if (LiftMoving(tag))
		{
			if (by) Say("The lift is on its way.");
			return false;
		}
		double d = z - LiftAt(tag);
		if (d == 0)
		{
			if (by) Say("The lift is here.");
			return false;
		}
		level.ExecuteSpecial(d > 0 ? 96 /* FloorAndCeiling_RaiseByValue */ : 95 /* ...LowerByValue */, null, null, false, tag, LIFT_SPEED, int(abs(d)));
		if (by) by.A_StartSound("plats/pt1_strt", CHAN_AUTO);
		return true;
	}

	// Frames and doors neither fall nor are lifted (no gravity, and a frame
	// is in no blockmap): those in a car are kept on its floor.
	void LiftTick()
	{
		if (!liftKnown)
		{
			liftKnown = 1;
			let bi = ThinkerIterator.Create("AjarLiftButton");
			Actor b;
			while (b = Actor(bi.Next()))
			{
				let it = level.CreateSectorTagIterator(b.args[0]);
				int i;
				while ((i = it.Next()) >= 0) if (liftSectors.Find(i) == liftSectors.Size()) liftSectors.Push(i);
				liftKnown = 2;
			}
		}
		if (liftKnown < 2) return;
		for (int pass = 0; pass < 2; pass++)
		{
			let it = ThinkerIterator.Create(pass ? "AjarDoor" : "AjarFrame");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (liftSectors.Find(a.CurSector.Index()) == liftSectors.Size()) continue;
				let d = AjarDoor(a);
				if (d && d.carried) continue;
				double fz = a.CurSector.floorplane.ZatPoint(a.pos.xy);
				if (a.pos.z != fz) a.SetZ(fz);
			}
		}
	}

	// --- MAP=LIFT MODE=1 tools/smoke.sh: the doors --------------------------
	bool InCar(Actor a) { return a.pos.x > 640 && a.pos.x < 832 && a.pos.y > 96 && a.pos.y < 288; }

	void LiftScript(Actor mo, int t)
	{
		AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1), o1 = LabLeaf(9, 0), o2 = LabLeaf(9, 1);
		AjarFrame inCar = FindFrame(110);
		if (t > 20 && t % 20 == 0) Console.Printf("AJARTEST t=%d car=%.0f moving=%d frame110=%.0f orange=%.0f,%.0f", t, LiftAt(), LiftMoving(), inCar.pos.z, o1.pos.z, o2.pos.z);
		// RED's far side is in the car: hung in the hall it opens onto the car on the ground...
		if (t == 20) { Take(mo, 1); Pose(mo, 60, 192, 0, 180); FindFrame(101).Activate(mo); Check("redHung", !carried && FindFrame(101).door != null); }
		Forward(mo, t, 22, 22);
		if (t == 50) Check("throughRedIntoCarOnGround", InCar(mo) && mo.pos.z == 0);
		// ...the car rides to the top with the player and both leaning leaves in it...
		if (t == 55) { Pose(mo, 736, 192, 0, 0); Check("sent", LiftSend(LIFT_TAG, 384) && !LiftSend(LIFT_TAG, 0)); }
		if (t == 160) Check("rodeToTop", InCar(mo) && mo.pos.z == 384 && LiftAt() == 384 && !LiftMoving());
		if (t == 160) Check("leaningLeavesRode", o1.pos.z == 384 && o2.pos.z == 384);
		if (t == 160) Check("frameRode", inCar.pos.z == 384);
		Forward(mo, t, 162, 20);
		if (t == 190) Check("outOntoTheTop", mo.pos.z == 384 && mo.pos.x > 864);
		// ...and from the hall RED now opens onto the top
		if (t == 195) Pose(mo, 60, 192, 0, 180);
		Forward(mo, t, 197, 22);
		if (t == 225) Check("throughRedIntoCarAtTop", InCar(mo) && mo.pos.z == 384);
		if (t == 230) { Pose(mo, 736, 192, 384, 0); LiftSend(LIFT_TAG, 0); }
		if (t == 335) Check("rodeDown", InCar(mo) && mo.pos.z == 0 && o1.pos.z == 0 && inCar.pos.z == 0);
		// a leaf in the car's frame, and the car to the first floor
		if (t == 340) { a.Used(mo); Pose(mo, 688, 150, 0, 270); inCar.Activate(mo); Check("leafHungInCar", a.frame == inCar && a.Shut() && !carried); }
		if (t == 345) LiftSend(LIFT_TAG, 192);
		if (t == 400) Check("hungLeafRode", inCar.pos.z == 192 && a.pos.z == 192 && mo.pos.z == 192);
		if (t == 405) Pose(mo, 736, 192, 192, 90);
		Forward(mo, t, 405, 20);
		if (t == 430) Check("outOntoFirst", mo.pos.z == 192 && mo.pos.y > 320);
		// its twin on the first floor: the two are joined
		if (t == 432) { b.Used(mo); Pose(mo, 736, 580, 192, 90); FindFrame(104).Activate(mo); Check("pairJoined", !carried && a.args[0] == 104 && b.args[0] == 110 && !a.bInvisible); }
		// the car goes down, and the first floor's frame leads down with it
		if (t == 435) LiftSend(LIFT_TAG, 0);
		if (t == 490) Check("openLeafRode", a.pos.z == 0 && LiftAt() == 0);
		Forward(mo, t, 492, 16);
		if (t == 515) Check("firstToCarOnGround", InCar(mo) && mo.pos.z == 0);
		if (t == 520) Pose(mo, 688, 150, 0, 270);
		Forward(mo, t, 520, 14);
		if (t == 540) Check("carToFirst", mo.pos.z == 192 && mo.pos.y > 320);
		// taken down and hung again in the car at the top
		if (t == 545) LiftSend(LIFT_TAG, 384);
		if (t == 650)
		{
			Pose(mo, 688, 150, 384, 270);
			inCar.Activate(mo);
			bool took = carried == a;
			inCar.Activate(mo);
			Check("rehungAtTop", took && !carried && a.frame == inCar && a.pos.z == 384 && a.args[0] == 104);
		}
		// through it from the first floor while the car is on its way down
		if (t == 655) { Pose(mo, 736, 580, 192, 90); LiftSend(LIFT_TAG, 0); }
		Forward(mo, t, 670, 16);
		if (t > 675 && t < 700 && t % 4 == 0) Console.Printf("AJARTEST mid t=%d car=%.0f player=(%.0f,%.0f,%.0f)", t, LiftAt(), mo.pos.x, mo.pos.y, mo.pos.z);
		if (t == 770) Check("intoCarMidRide", InCar(mo) && mo.pos.z == 0 && LiftAt() == 0);
	}

	// --- MAP=LIFT MODE=2 tools/smoke.sh: company ----------------------------
	Actor liftGuest;

	Actor SpawnGuest(class<Actor> cls, double x, double y, double z, double ang, Actor after)
	{
		if (liftGuest) { liftGuest.ClearCounters(); liftGuest.Destroy(); }
		liftGuest = Actor.Spawn(cls, (x, y, z));
		liftGuest.angle = ang;
		if (after)
		{
			liftGuest.target = after;
			liftGuest.SetState(liftGuest.SeeState);
		}
		return liftGuest;
	}

	void LiftCompanyScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		Actor g = liftGuest;
		if (t > 20 && t % 35 == 0)
			Console.Printf("AJARTEST t=%d car=%.0f moving=%d guest=%s (%.0f,%.0f,%.0f) health=%d", t, LiftAt(), LiftMoving(),
				g ? g.GetClassName() : 'none', g ? g.pos.x : 0, g ? g.pos.y : 0, g ? g.pos.z : 0, g ? g.health : 0);
		// 1: a monster in the car rides with it
		if (t == 20) { Take(mo, 1); Pose(mo, 60, 192, 0, 180); FindFrame(101).Activate(mo); Pose(mo, 300, 60, 0, 90); }
		if (t == 22) { SpawnGuest("ZombieMan", 736, 192, 0, 180, null); LiftSend(LIFT_TAG, 384); }
		if (t == 125) Check("monsterRides", g && InCar(g) && g.pos.z == 384 && LiftAt() == 384);
		// 2: a demon in the hall, the player in the car at the top, RED between them
		if (t == 130) { Pose(mo, 784, 230, 384, 270); SpawnGuest("Demon", 300, 192, 0, 180, mo); }
		if (t == 480) Check("demonUpThroughRed", g && g.health > 0 && g.pos.z == 384);
		// 3: the other way: a demon in the car at the top, the player in the hall
		if (t == 485) { Pose(mo, 200, 192, 0, 180); SpawnGuest("Demon", 736, 220, 384, 270, mo); }
		if (t == 835) Check("demonDownThroughRed", g && g.health > 0 && g.pos.z == 0);
		// 4: the player standing in the car's opening at the top when it is sent
		if (t == 840) { Pose(mo, 836, 192, 384, 0); LiftSend(LIFT_TAG, 0); }
		if (t == 900) { Check("playerInTheWayHoldsCar", LiftAt() > 300); Console.Printf("AJARTEST held car=%.0f moving=%d health=%d", LiftAt(), LiftMoving(), mo.health); }
		if (t == 905) Pose(mo, 300, 60, 0, 90);
		if (t == 1010) Check("carGoesOnWhenClear", LiftAt() == 0 && !LiftMoving());
		// 5: a body lying there holds nothing
		if (t == 1015) LiftSend(LIFT_TAG, 384);
		if (t == 1115) { SpawnGuest("Demon", 836, 192, 384, 0, null); liftGuest.DamageMobj(null, null, 10000, 'None'); }
		if (t == 1150) LiftSend(LIFT_TAG, 0);
		if (t == 1255) Check("carGoesOnOverABody", LiftAt() == 0 && !LiftMoving() && g.pos.z == 384);
	}
}
