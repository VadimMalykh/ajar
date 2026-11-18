// The engine tests for levels 11 to 20 (map ENG, tools/map_eng.py).
// MAP=ENG MODE=n tools/smoke.sh: 1 the lift, 2 the loop, 3 the inside-out
// room, 4 mirrors, 5 slanted walls. Played by hand the buttons work too.

// A button on a wall: 1 sends the lift to its other floor, 2 sends an imp's
// fireball round the loop.
class EngButton : Actor
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
		let h = EngTest(EventHandler.Find("EngTest"));
		if (!h) return;
		if (args[0] == 1) h.Lift();
		else h.Fire("DoomImpBall", 10);
	}
}

// Something only a mirror shows.
class EngGhost : Actor
{
	Default
	{
		Radius 16;
		Height 56;
		+NOGRAVITY +NOBLOCKMAP +BRIGHT +ONLYVISIBLEINMIRRORS
	}
	States
	{
	Spawn:
		HEAD A -1;
		Stop;
	}
}

class EngTest : EventHandler
{
	const LIFT_TAG = 1;
	const SHUTTER_TAG = 2;
	int tic;
	Actor ball;
	double ballX;
	int laps, crossings, lastLap, openTics, ballTics;

	Sector Tagged(int tag)
	{
		let it = level.CreateSectorTagIterator(tag);
		int i = it.Next();
		if (i < 0) return null;
		return level.sectors[i];
	}

	double CarFloor()
	{
		Sector s = Tagged(LIFT_TAG);
		return s.floorplane.ZatPoint(s.centerspot);
	}

	void Lift()
	{
		double z = CarFloor();
		if (z == 0) level.ExecuteSpecial(96 /* FloorAndCeiling_RaiseByValue */, null, null, false, LIFT_TAG, 16, 192);
		else if (z == 192) level.ExecuteSpecial(95 /* FloorAndCeiling_LowerByValue */, null, null, false, LIFT_TAG, 16, 192);
	}

	void Fire(class<Actor> what, double speed)
	{
		if (ball) ball.Destroy();
		ball = Actor.Spawn(what, (1100, 128, 32));
		ball.angle = 0;
		ball.vel = (speed, 0, 0);
		ballX = ball.pos.x;
		laps = crossings = openTics = ballTics = 0;
		lastLap = tic;
	}

	override void WorldLineActivated(WorldEvent e)
	{
		if (e.ActivationType != SPAC_PCross) return;
		crossings++;
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST crossed t=%d by=%s", tic, e.Thing ? e.Thing.GetClassName() : 'none');
	}

	void Link(int a, int b)
	{
		level.ExecuteSpecial(107 /* Line_SetPortalTarget */, null, null, false, a, b);
		level.ExecuteSpecial(107, null, null, false, b, a);
	}

	void Pose(Actor mo, double x, double y, double z, double ang, string shot = "")
	{
		mo.SetOrigin((x, y, z), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
		if (shot != "") Console.Printf("AJARTEST shot %s t=%d", shot, tic);
	}

	// walk the way you face (a portal turns you, so this goes on beyond it)
	void Walk(Actor mo, int t, int from, int tics)
	{
		if (t > from && t <= from + tics) mo.vel.xy = Actor.AngleToVector(mo.angle, 10);
		if (t == from + tics + 1) mo.vel = (0, 0, 0);
	}

	void Check(string what, bool ok, Actor mo)
	{
		Console.Printf("AJARTEST %s=%d pos=(%.1f,%.1f,%.1f) angle=%.1f", what, ok, mo.pos.x, mo.pos.y, mo.pos.z, Actor.Normalize180(mo.angle));
	}

	override void WorldTick()
	{
		tic++;
		if (ball)
		{
			ballTics++;
			if (ball.pos.x < ballX - 100)
			{
				laps++;
				if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST lap %d t=%d took=%d z=%.1f y=%.1f", laps, tic, tic - lastLap, ball.pos.z, ball.pos.y);
				lastLap = tic;
			}
			ballX = ball.pos.x;
			Sector sh = Tagged(SHUTTER_TAG);
			if (sh.ceilingplane.ZatPoint(sh.centerspot) > 48) openTics++;
		}
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		let mo = players[consoleplayer].mo;
		if (!mode || !mo || !(level.mapname ~== "ENG")) return;
		int t = tic;
		if (mode == 1) LiftScript(mo, t);
		else if (mode == 2) LoopScript(mo, t);
		else if (mode == 3) InsideOutScript(mo, t);
		else if (mode == 4) MirrorScript(mo, t);
		else if (mode == 5) SlantScript(mo, t);
	}

	bool InCar(Actor mo) { return mo.pos.x > 256 && mo.pos.x < 384 && mo.pos.y > 96 && mo.pos.y < 224; }
	bool InHall(Actor mo) { return mo.pos.x > 0 && mo.pos.x < 256 && mo.pos.y > 32 && mo.pos.y < 288; }

	// 1: a portal in a lift car, its other end in the hall
	void LiftScript(Actor mo, int t)
	{
		if (t == 20) Pose(mo, 100, 160, 0, 180);
		Walk(mo, t, 20, 25);                    // hall -> car, the car down
		if (t == 50) Check("carDown_hallToCar", InCar(mo) && mo.pos.z == 0, mo);
		if (t == 55) Pose(mo, 320, 130, 0, 90, "fromCarDown");
		if (t == 160) Lift();                   // ride up, looking at the door
		if (t == 165) Console.Printf("AJARTEST shot ridingUp t=%d", t);
		if (t > 160 && t < 262 && t % 16 == 0) Console.Printf("AJARTEST ride t=%d car=%.1f player=%.1f", t, CarFloor(), mo.pos.z);
		if (t == 270) Check("rodeUp", InCar(mo) && mo.pos.z == 192 && CarFloor() == 192, mo);
		if (t == 275) Console.Printf("AJARTEST shot fromCarUp t=%d", t);
		Walk(mo, t, 380, 25);                   // car -> hall, the car up
		if (t == 410) Check("carUp_carToHall", InHall(mo) && mo.pos.z == 0, mo);
		if (t == 415) Pose(mo, 100, 160, 0, 180, "fromHallCarUp");
		Walk(mo, t, 520, 25);                   // hall -> car, the car up
		if (t == 550) Check("carUp_hallToCar", InCar(mo) && mo.pos.z == 192, mo);
		// go in while the car is on its way down
		if (t == 555) { Pose(mo, 100, 160, 0, 180, "carComingDown"); Lift(); }
		Walk(mo, t, 590, 25);
		if (t > 595 && t < 612) Console.Printf("AJARTEST mid t=%d car=%.1f player=(%.1f,%.1f,%.1f)", t, CarFloor(), mo.pos.x, mo.pos.y, mo.pos.z);
		if (t == 670) Check("midRide_landedWithCar", InCar(mo) && mo.pos.z == 0 && CarFloor() == 0, mo);
		// the same after the link is cut and made again, as a carried door does it
		if (t == 675) { Pose(mo, 100, 160, 0, 180); Lift(); }
		if (t == 780) { level.ExecuteSpecial(107, null, null, false, 301, 0); level.ExecuteSpecial(107, null, null, false, 302, 0); }
		if (t == 782) Link(301, 302);
		if (t == 785) Console.Printf("AJARTEST shot relinked t=%d car=%.1f", t, CarFloor());
		Walk(mo, t, 860, 25);
		if (t == 890) Check("relinked_hallToCar", InCar(mo) && mo.pos.z == 192, mo);
		// a fireball thrown from the hall into the car that is up
		if (t == 895)
		{
			Pose(mo, 200, 60, 0, 135, "ballIntoCar");
			ball = Actor.Spawn("DoomImpBall", (150, 160, 32));
			ball.angle = 180;
			ball.vel = (-10, 0, 0);
		}
		if (t > 905 && t < 925 && t % 3 == 0 && ball) Console.Printf("AJARTEST ball t=%d pos=(%.1f,%.1f,%.1f)", t, ball.pos.x, ball.pos.y, ball.pos.z);
	}

	// 2: a missile going round a corridor that opens onto itself
	void LoopScript(Actor mo, int t)
	{
		if (t == 20) Pose(mo, 1040, 60, 0, 25, "loop");
		if (t == 30) Fire("DoomImpBall", 10);
		if (t > 30 && t % 35 == 0)
		{
			Sector sh = Tagged(SHUTTER_TAG);
			Console.Printf("AJARTEST t=%d ball=%d laps=%d crossings=%d shutter=%.0f", t, ball != null, laps, crossings, sh.ceilingplane.ZatPoint(sh.centerspot));
		}
		if (t == 590) Console.Printf("AJARTEST impBall alive=%d laps=%d crossings=%d shutterOpen=%d/%d tics health=%d", ball != null, laps, crossings, openTics, ballTics, mo.health);
		if (t == 600) Fire("PlasmaBall", 25);
		if (t == 880) Console.Printf("AJARTEST plasma alive=%d laps=%d crossings=%d shutterOpen=%d/%d tics", ball != null, laps, crossings, openTics, ballTics);
		if (t == 890) Fire("Rocket", 20);
		if (t == 1170) Console.Printf("AJARTEST rocket alive=%d laps=%d crossings=%d shutterOpen=%d/%d tics", ball != null, laps, crossings, openTics, ballTics);
	}

	// 3: four frames in a hall's four walls, each out of the same face of a booth
	void InsideOutScript(Actor mo, int t)
	{
		static const string names[] = { "east", "north", "west", "south" };
		for (int i = 0; i < 4; i++)
		{
			int at = 20 + i * 150;
			if (t == at) Pose(mo, 2192, 224, 0, i * 90, "hall_" .. names[i]);
			Walk(mo, t, at + 105, 30);
			Vector2 d = Actor.AngleToVector(i * 90, 1);
			// 300 walked, less the 208 from the hall's middle to its portal line; out of the booth's line, 80 from its middle
			Vector2 want = (2500, 3000) + d * (80 + 300 - 208);
			if (t == at + 140) Check("out_" .. names[i], (mo.pos.xy - want).Length() < 12 && abs(Actor.DeltaAngle(mo.angle, i * 90)) < 1, mo);
		}
		if (t == 620) Pose(mo, 2192, 224, 0, 45, "hall_corner");
		if (t == 725) Pose(mo, 2040, 70, 0, 45, "hall_fromCorner");
		if (t == 830) Pose(mo, 2500, 3400, 0, 270, "square_boothNorthFace");
		if (t == 935) Pose(mo, 2850, 3350, 0, 225, "square_boothCorner");
		if (t == 1040) Pose(mo, 2500, 3180, 0, 270, "square_close");
	}

	// 4: mirrors with portals in view, and things only a mirror shows
	void MirrorScript(Actor mo, int t)
	{
		if (t == 20) Pose(mo, 4250, 192, 0, 180, "mirror_west");
		if (t == 125) Pose(mo, 4300, 110, 0, 160, "mirror_slant");
		if (t == 230) Pose(mo, 4250, 90, 0, 130, "ghost_direct");
		if (t == 335) Pose(mo, 4060, 192, 0, 0, "portal_toSideRoom");
		if (t == 440) Pose(mo, 4200, 192, 0, 0, "portal_closer");
		Walk(mo, t, 545, 30);
		if (t == 580) Check("intoSideRoom", mo.pos.x > 4000 && mo.pos.x < 4320 && mo.pos.y > 2000, mo);
		if (t == 585) Pose(mo, 4100, 2128, 0, 0, "side_mirror");
		if (t == 690) Pose(mo, 4060, 2060, 0, 40, "side_ghost_direct");
		if (t == 795) Pose(mo, 4280, 2128, 0, 180, "side_backToPortal");
		// at the door's mouth, looking through it straight at the side room's ghost (17 degrees to the left)
		if (t == 900) Pose(mo, 4380, 192, 0, 17, "ghost_throughPortal");
	}

	// 5: door recesses on slanting walls
	void SlantScript(Actor mo, int t)
	{
		Vector2 hex = (5000, 240);
		if (t == 20) Pose(mo, hex.x, hex.y, 0, 90, "hex_north");
		if (t == 125) Pose(mo, hex.x, hex.y, 0, 30, "hex_30");
		if (t == 230) Pose(mo, hex.x, hex.y, 0, 0, "hex_corner");
		if (t == 335) Pose(mo, hex.x, hex.y, 0, 30);
		Walk(mo, t, 335, 25);
		// 250 walked; the wall's line is 182.277 from the middle and so is the one it leads to
		Vector2 want = hex + Actor.AngleToVector(30, 250 - 2 * 182.277);
		if (t == 365) Check("hex_straightOn", (mo.pos.xy - want).Length() < 12 && abs(Actor.DeltaAngle(mo.angle, 30)) < 1, mo);
		// each wall onto its neighbour: 361-362, 363-364, 365-366
		if (t == 370) { Link(361, 362); Link(363, 364); Link(365, 366); Pose(mo, hex.x, hex.y, 0, 30, "hex_turned_30"); }
		if (t == 475) Pose(mo, hex.x, hex.y, 0, 90, "hex_turned_north");
		if (t == 580) Pose(mo, hex.x, hex.y, 0, 30);
		Walk(mo, t, 580, 25);
		if (t == 610) Check("hex_turned", abs(mo.pos.x - hex.x) < 12 && mo.pos.y > hex.y && mo.pos.y < hex.y + 166 && abs(Actor.DeltaAngle(mo.angle, 270)) < 1, mo);

		Vector2 tri = (5600, 180);
		if (t == 615) Pose(mo, tri.x, tri.y - 30, 0, 90, "tri_top");
		if (t == 720) Pose(mo, tri.x, tri.y + 60, 0, 330, "tri_rightCorner");
		if (t == 825) Pose(mo, tri.x - 60, tri.y - 40, 0, 0, "tri_along");
		if (t == 930) Pose(mo, tri.x + 96, 150, 0, 270);
		Walk(mo, t, 930, 14);
		if (t == 950) Check("tri_roundCorner", mo.pos.y > 88 && mo.pos.x > tri.x && abs(Actor.DeltaAngle(mo.angle, 210)) < 1, mo);
	}
}
