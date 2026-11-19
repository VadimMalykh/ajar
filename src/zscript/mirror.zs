// Mirrors (the test map MIR, tools/map_mirror.py), for MAP15.
// MAP=MIR MODE=n tools/smoke.sh: 1 shots at a mirror and the door only a
// mirror shows, 2 a monster only a mirror shows, 3 the lodger and a Pair.

// An imp that is drawn only in mirrors. Everything else about it is an imp.
class AjarUnseenImp : DoomImp
{
	Default
	{
		+ONLYVISIBLEINMIRRORS
	}
}

// ajarmap.unseen: args[0], args[1] = half the box's size along x and y.
class AjarUnseen : Actor
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

extend class AjarHandler
{
	// Monsters that only a mirror shows (ajarmap.unseen): those that stand in
	// the marker's box when the level begins, while they are alive and in
	// that box. One that walks out of the room with the mirrors is seen like
	// any other, and unseen again if it goes back.
	Array<Actor> unseenOnes;
	Array<Actor> unseenMarks;

	void UnseenInit()
	{
		let marks = ThinkerIterator.Create("AjarUnseen");
		Actor u;
		while (u = Actor(marks.Next()))
		{
			let mi = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(mi.Next()))
				if (a.bIsMonster && abs(a.pos.x - u.pos.x) < u.args[0] && abs(a.pos.y - u.pos.y) < u.args[1])
				{
					a.bOnlyVisibleInMirrors = true;
					unseenOnes.Push(a);
					unseenMarks.Push(u);
				}
		}
	}

	bool unseenTold;

	void UnseenTick()
	{
		if (level.maptime % 4) return;
		// the first time the player stands in such a room with any of them alive
		let mo = players[consoleplayer].mo;
		for (int i = 0; mo && !unseenTold && i < unseenOnes.Size(); i++)
		{
			Actor a = unseenOnes[i], u = unseenMarks[i];
			if (a && u && a.health > 0 && abs(mo.pos.x - u.pos.x) < u.args[0] && abs(mo.pos.y - u.pos.y) < u.args[1])
			{
				unseenTold = true;
				Say("This room is not as empty as it looks.\nThe glass shows who is here.");
			}
		}
		for (int i = 0; i < unseenOnes.Size(); i++)
		{
			Actor a = unseenOnes[i], u = unseenMarks[i];
			if (!a || !u) continue;
			a.bOnlyVisibleInMirrors = a.health > 0 && abs(a.pos.x - u.pos.x) < u.args[0] && abs(a.pos.y - u.pos.y) < u.args[1];
		}
	}

	override void WorldThingDied(WorldEvent e)
	{
		if (e.Thing) e.Thing.bOnlyVisibleInMirrors = false;
	}

	Actor glassBall;
	bool ballCameBack, lodgerOut, lodgerBack, outAlone, outJoined;
	int impWas, phase, phaseTic;

	void GlassShot(string name, int t) { Console.Printf("AJARTEST shot %s t=%d", name, t); }

	void GlassScript(Actor mo, int t, int mode)
	{
		if (mode == 1)
		{
			mo.player.cheats |= CF_GODMODE;
			let sensor = AjarTarget(OptOne("AjarTarget"));
			let em = AjarEmitter(OptOne("AjarEmitter"));
			AjarDoor d = DoorOf(3);
			// a bullet along the line the beam will take
			if (t == 20) Pose(mo, 200, 157.9, 0, 153);
			if (t == 22) mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff");
			if (t == 24) Check("bulletComesBackOffMirror", sensor.told != 0);
			// one of Doom's missiles
			if (t == 26)
			{
				Pose(mo, 320, 600, 0, 225);
				glassBall = Actor.Spawn("PlasmaBall", (382, 65, 40));
				glassBall.target = em;
				glassBall.Vel3DFromAngle(25, 153, 0);
			}
			if (glassBall && glassBall.vel.x > 1) ballCameBack = true;
			if (t == 80) Check("plasmaComesBackOffMirror", ballCameBack);
			// the beam
			if (t == 82) { em.Activate(mo); GlassShot("beam_toMirror", t); }
			if (t > 82 && t < 140 && t % 4 == 0)
			{
				Actor beam = OptOne("AjarBeam");
				if (beam) Console.Printf("AJARTEST beam t=%d at (%.0f,%.0f,%.0f)", t, beam.pos.x, beam.pos.y, beam.pos.z);
			}
			if (t == 150) Check("beamOffMirrorOnSensor", sensor.done);
			// the door only the mirror shows
			if (t == 152) { Check("doorUnseen", d && d.bOnlyVisibleInMirrors && !d.bInvisible); Pose(mo, 320, 420, 0, 0); GlassShot("door_direct", t); }
			if (t == 230) { Pose(mo, 330, 300, 0, 180); GlassShot("door_inMirror", t); }
			if (t == 310) { Pose(mo, 470, 420, 0, 0); d.Used(mo); Check("doorTakenByFeel", carried == d); }
			if (t == 312) { Pose(mo, 320, 590, 0, 90); FindFrame(101).Activate(mo); Check("doorHung", !carried && FindFrame(101).door == d); }
			if (t == 314) { Check("onceTakenItIsSeen", !d.bOnlyVisibleInMirrors); Pose(mo, 320, 400, 0, 90); GlassShot("door_hung", t); }
			Forward(mo, t, 390, 40);
			if (t == 435) Check("throughItToItsFarSide", mo.pos.y > 1000 && mo.pos.x < 256);
		}
		if (mode == 2)
		{
			let imp = OptOne("AjarUnseenImp");
			if (t == 20) { Pose(mo, 2300, 192, 0, 180); GlassShot("imp_inMirror", t); Check("impUnseen", imp && imp.bOnlyVisibleInMirrors); }
			if (t == 21) Check("impBlocks", !mo.CheckPosition(imp.pos.xy));
			if (t == 60) { impWas = imp.health; mo.angle = mo.AngleTo(imp); mo.LineAttack(mo.angle, 4096, 0, 10, 'Hitscan', "BulletPuff"); }
			if (t == 62) Check("bulletHitsUnseenImp", imp.health < impWas);
			if (t == 64) { mo.angle = 180; }
			if (t % 35 == 0 && imp) Console.Printf("AJARTEST imp at (%.0f,%.0f) health=%d player=%d", imp.pos.x, imp.pos.y, imp.health, mo.health);
			if (t == 500) Check("unseenImpHurtsPlayer", mo.health < 100);
		}
		if (mode == 3)
		{
			AjarDoor a = LabLeaf(8, 0), b = LabLeaf(8, 1);
			if (t == 40) { Pose(mo, 4256, 192, 0, 90); lodger = AjarLodger(Actor.Spawn("AjarLodger", (4256, 300, 0))); }
			if (!lodger) return;
			if (t % 35 == 0) Console.Printf("AJARTEST lodger pos=(%d,%d) inside=%d phase=%d player=%d", lodger.pos.x, lodger.pos.y, lodger.inside, phase, mo.health);
			if (phase) mo.player.cheats |= CF_GODMODE;
			if (!lodger.inside) lodgerOut = true;
			if (phase == 0 && lodgerOut && lodger.inside)
			{
				// it has been out and gone back: one leaf alone in 111, BLUE in 112
				Check("lodgerComesOutOfEmptyFrame", true);
				a.Used(mo); FindFrame(111).Activate(mo);
				Take(mo, 2); FindFrame(112).Activate(mo);
				Check("leafHungAloneIsShut", a.Shut() && !carried);
				phase = 1; phaseTic = t;
			}
			if (t == 1500 && phase == 0) Check("lodgerComesOutOfEmptyFrame", false);
			if (phase == 1 && !lodger.inside) outAlone = true;
			if (phase == 1 && t == phaseTic + 500)
			{
				Check("leafHungAlonePlugsItsFrame", !outAlone);
				// the twin in place of BLUE: the Pair joined, 111 onto 112
				b.Used(mo); FindFrame(112).Activate(mo);
				Check("pairJoined", !a.Shut() && !b.Shut() && FindFrame(112).door == b);
				Pose(mo, 4256, 192, 0, 0); GlassShot("pair_joined", t);
				phase = 2; phaseTic = t;
			}
			if (phase == 2 && !lodger.inside) outJoined = true;
			if (phase == 2 && t == phaseTic + 500) Check("joinedPairPlugsBothFrames", !outJoined);
		}
	}
}
