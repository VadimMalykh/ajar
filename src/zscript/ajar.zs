// Ajar prototype: frames, doors, and the handler that rewires portals.
//
// Map contract (see tools/make_map.py):
//  * AjarFrame thing: args[0] = id of the frame's portal line. Its tid is the
//    same number; the frame's mouth line calls Thing_Activate on it.
//  * AjarDoor thing:  args[0] = id of the door's far-side portal line,
//    args[1] = colour (1..5), args[2] = id of the frame it starts in (0 = leaning).

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
		if (h) h.UseFrame(self, activator);
	}
}

class AjarDoor : Actor
{
	AjarFrame frame;   // where it hangs, or null
	bool carried;
	Actor nailer;      // who nailed it to its frame, or null

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
	Nailed:            // only so that these sprites are loaded
		AJN1 A -1;
		AJN2 A -1;
		AJN3 A -1;
		AJN4 A -1;
		AJN5 A -1;
		Stop;
	}

	static const Color glow[] = { 0, 0xFF5040, 0x4070FF, 0x40E060, 0xFFC830, 0xB060FF };
	static const string names[] = { "", "RED", "BLUE", "GREEN", "YELLOW", "VIOLET" };

	int Colour() { return clamp(args[1], 1, 5); }
	string BackTex() { return String.Format("AJDR%d", Colour()); }
	string Label() { return names[Colour()]; }

	void Show()
	{
		static const name spr[] = { 'AJD1', 'AJD1', 'AJD2', 'AJD3', 'AJD4', 'AJD5' };
		static const name nailedSpr[] = { 'AJN1', 'AJN1', 'AJN2', 'AJN3', 'AJN4', 'AJN5' };
		int c = Colour();
		sprite = GetSpriteIndex(nailer ? nailedSpr[c] : spr[c]);
		bInvisible = false;
		A_AttachLight('glow', DynamicLight.PointLight, glow[c], 80, 80, 0, (0, 0, 56));
	}

	void Hide()
	{
		bInvisible = true;
		A_RemoveLight('glow');
	}

	override bool Used(Actor user)
	{
		if (carried) return false;
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h) return false;
		if (frame) h.UseFrame(frame, user);
		else h.TakeLeaning(self, user);
		return true;
	}
}

class AjarHandler : EventHandler
{
	const FRAME_TEX = "AJFRAME";
	AjarDoor carried;
	int testTic;

	// --- portal plumbing -------------------------------------------------
	void Link(int fromLine, int toLine, string blankTex)
	{
		level.ExecuteSpecial(107 /* Line_SetPortalTarget */, null, null, false, fromLine, toLine);
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
	}

	Line FindLine(int id)
	{
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
	void Hang(AjarDoor d, AjarFrame f)
	{
		Link(f.args[0], d.args[0], FRAME_TEX);
		Link(d.args[0], f.args[0], d.BackTex());
		d.frame = f;
		d.carried = false;
		f.door = d;

		// stand the leaf open at the hinge side of the frame
		Line l = FindLine(f.args[0]);
		if (l)
		{
			Vector2 dir = l.delta.Unit();
			Vector2 n = (dir.y, -dir.x);                  // into the room
			Vector2 u = n * cos(25) - dir * sin(25);       // leaf swung open 115 degrees
			Vector2 hinge = l.v1.p + n * 16;
			d.SetOrigin((hinge + u * 32, f.pos.z), false);
			d.angle = VectorAngle(u.x, u.y) + 90;
		}
		d.Show();
	}

	AjarDoor Unhang(AjarFrame f)
	{
		AjarDoor d = f.door;
		Link(f.args[0], 0, FRAME_TEX);
		Link(d.args[0], 0, d.BackTex());
		f.door = null;
		d.frame = null;
		d.carried = true;
		d.Hide();
		return d;
	}

	// The thief's door work, the same three moves the player has. Returns the
	// door it carries afterwards.
	AjarDoor ThiefUsesFrame(AjarFrame f, AjarDoor carrying, Actor thief)
	{
		AjarDoor old = f.door ? Unhang(f) : null;
		if (carrying) Hang(carrying, f);
		thief.A_StartSound(carrying ? "doors/dr1_open" : "doors/dr1_clos", CHAN_AUTO);
		if (carrying && old) Say("A thief swaps the " .. old.Label() .. " door for the " .. carrying.Label() .. " one!");
		else if (carrying) Say("A thief hangs the " .. carrying.Label() .. " door!");
		else if (old) Say("A thief has taken the " .. old.Label() .. " door!");
		return old;
	}

	void ThiefPicksUp(AjarDoor d, Actor thief)
	{
		d.carried = true;
		d.Hide();
		thief.A_StartSound("doors/dr1_clos", CHAN_AUTO);
		Say("A thief picks up the " .. d.Label() .. " door!");
	}

	// A carried door is put down where `at` stands, to be picked up again.
	void DropDoor(AjarDoor d, Actor at)
	{
		d.carried = false;
		d.SetOrigin(at.pos, false);
		d.angle = at.angle;
		d.Show();
	}

	void Say(string msg)
	{
		Console.MidPrint(smallfont, msg);
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

	void UseFrame(AjarFrame f, Actor user)
	{
		if (f.door && f.door.nailer)
		{
			Say("The " .. f.door.Label() .. " door is nailed to its frame.\nSomeone with a hammer did that.");
			return;
		}
		if (f.door && !carried)
		{
			carried = Unhang(f);
			user.A_StartSound("doors/dr1_clos", CHAN_AUTO);
			Say("You unhinge the " .. carried.Label() .. " door.");
		}
		else if (!f.door && carried)
		{
			Hang(carried, f);
			user.A_StartSound("doors/dr1_open", CHAN_AUTO);
			Say("The " .. carried.Label() .. " door opens where it always opens.");
			carried = null;
		}
		else if (f.door && carried)
		{
			AjarDoor old = Unhang(f);
			Hang(carried, f);
			user.A_StartSound("doors/dr1_open", CHAN_AUTO);
			Say("You swap the " .. old.Label() .. " door for the " .. carried.Label() .. " one.");
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
		user.A_StartSound("doors/dr1_clos", CHAN_AUTO);
		Say("You pick up the " .. d.Label() .. " door.");
	}

	// --- events ----------------------------------------------------------
	override void WorldLoaded(WorldEvent e)
	{
		if (e.IsSaveGame) return;

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

		// The test box's own monsters would walk into the scripted smoke tests.
		if (level.mapname ~== "TEST" && CVar.GetCVar("ajar_autotest").GetInt())
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

		let di = ThinkerIterator.Create("AjarDoor");
		AjarDoor d;
		while (d = AjarDoor(di.Next()))
		{
			Link(d.args[0], 0, d.BackTex());
			f = null;
			if (d.args[2]) f = FindFrame(d.args[2]);
			if (f) Hang(d, f);
			else d.Show();
		}
	}

	override void PlayerSpawned(PlayerEvent e)
	{
		let mo = players[e.PlayerNumber].mo;
		if (!mo) return;
		Say("USE a door to take it with you.\nUSE an empty frame to hang it there.\nA door always opens onto its own far side.");
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		// ordinary monsters learn about doors (see AjarSense)
		let t = e.thing;
		if (t && t.bIsMonster && t.SeeState && !(t is "AjarEnemy")) t.GiveInventoryType("AjarSense");
	}

	// --- headless smoke tests (ajar_autotest 1 or 2, see tools/smoke.sh) ----
	override void WorldUnloaded(WorldEvent e)
	{
		if (CVar.GetCVar("ajar_autotest").GetInt()) Check("levelExited", true);
	}

	override void WorldTick()
	{
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (!mode) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		int t = testTic++;
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) carried=%s", t, mo.pos.x, mo.pos.y, mo.pos.z, carried ? carried.Label() : "-");
		if (level.mapname ~== "TEST") TestLevelScript(mo, t, mode);
		else if (level.mapname ~== "MAP01") BorrowedRoomsScript(mo, t);
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
		// face the exit switch; the real USE press comes from tools/smoke_MAP01_1.cfg
		if (t == 695) Pose(mo, 3290, 128, 0, 0);
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

	void TestLevelScript(Actor mo, int t, int mode)
	{
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
		Ammo a1, a2;
		[a1, a2] = GetCurrentAmmo();
		if (a1) DrawString(big, FormatNumber(a1.Amount, 3), (76, -24), DI_SCREEN_LEFT_BOTTOM, Font.CR_GOLD);
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h || !h.carried) return;
		DrawImage(String.Format("AJDR%d", h.carried.args[1]), (-8, 28),
			DI_SCREEN_RIGHT_BOTTOM | DI_ITEM_RIGHT_BOTTOM, 1.0, (-1, -1), (1.5, 1.5));
	}
}
