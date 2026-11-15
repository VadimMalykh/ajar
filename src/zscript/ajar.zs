// Ajar prototype: frames, doors, and the handler that rewires portals.
//
// Map contract (see tools/make_map.py):
//  * AjarFrame thing: args[0] = id of the frame's portal line. Its tid is the
//    same number; the frame's mouth line calls Thing_Activate on it.
//  * AjarDoor thing:  args[0] = id of the door's far-side portal line,
//    args[1] = colour (1..6), args[2] = id of the frame it starts in (0 = leaning),
//    args[3] = 1 for a fixed doorway: no leaf, no colour, and it stays in that
//    frame for the whole level (ajarmap.doorway).

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
	Actor nailer;      // who nailed it to its frame, or null (itself: a fixed doorway)

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
	Nailed:            // only so that these sprites are loaded
		AJN1 A -1;
		AJN2 A -1;
		AJN3 A -1;
		AJN4 A -1;
		AJN5 A -1;
		AJN6 A -1;
		Stop;
	}

	static const Color glow[] = { 0, 0xFF5040, 0x4070FF, 0x40E060, 0xFFC830, 0xB060FF, 0xFF70B0 };
	static const string names[] = { "", "RED", "BLUE", "GREEN", "YELLOW", "VIOLET", "PINK" };

	int Colour() { return clamp(args[1], 1, 6); }
	string BackTex() { return String.Format("AJDR%d", Colour()); }
	string Label() { return names[Colour()]; }

	void Show()
	{
		static const name spr[] = { 'AJD1', 'AJD1', 'AJD2', 'AJD3', 'AJD4', 'AJD5', 'AJD6' };
		static const name nailedSpr[] = { 'AJN1', 'AJN1', 'AJN2', 'AJN3', 'AJN4', 'AJN5', 'AJN6' };
		if (nailer == self) { Hide(); return; }      // a fixed doorway has no leaf
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
	const SQUEEZE_ID = 500;       // line id of every squeeze (ajarmap.squeeze)
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

	void UseFrame(AjarFrame f, Actor user)
	{
		if (f.door && f.door.nailer)
		{
			if (f.door.nailer == f.door) Say("This doorway is part of the building.\nIt is not yours to take.");
			else Say("The " .. f.door.Label() .. " door is nailed to its frame.\nSomeone with a hammer did that.");
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

		// Monsters would walk into the scripted smoke tests. (In a real level
		// mode 2 is a tour of it as it is played, so it keeps them.)
		int autotest = CVar.GetCVar("ajar_autotest").GetInt();
		if (autotest && !(!(level.mapname ~== "TEST") && autotest >= 2))
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
			if (f && d.args[3]) d.nailer = d;
			if (f) Hang(d, f);
			else d.Show();
		}

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
		if (!mo) return;
		Say("USE a door to take it with you.\nUSE an empty frame to hang it there.\nA door always opens onto its own far side.");
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
		if (CVar.GetCVar("ajar_autotest").GetInt()) Check("levelExited", true);
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

	override void WorldTick()
	{
		SelfShots();
		let mo = players[consoleplayer].mo;
		if (mo) Squeeze(mo);
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (!mode || !mo) return;
		int t = testTic++;
		if (t % 35 == 0)
			Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) carried=%s", t, mo.pos.x, mo.pos.y, mo.pos.z, carried ? carried.Label() : "-");
		if (level.mapname ~== "TEST") TestLevelScript(mo, t, mode);
		else if (level.mapname ~== "MAP04" && mode == 3) DisposalScript(mo, t);
		else if (level.mapname ~== "MAP04" && mode != 2) PartyWallScript(mo, t);
		else if (!(level.mapname ~== "MAP01") && mode == 2) Tour(mo, t);
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
		if (t == 925) Check("inStreet", mo.pos.x > 4900);
		// face the exit switch; the real USE press comes from tools/smoke_MAP02_1.cfg
		if (t == 930) Pose(mo, 5418, 96, 0, 0);
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
		if (t == 735) Check("inAlley", mo.pos.x > 4900);
		// face the exit switch; the real USE press comes from tools/smoke_MAP03_1.cfg
		if (t == 740) Pose(mo, 5418, 96, 0, 0);
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
		if (t == 955) Check("inStreet", mo.pos.x > 4900);
		// face the exit switch; the real USE press comes from tools/smoke_MAP04_1.cfg
		if (t == 960) Pose(mo, 5418, 96, 0, 0);
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
			5040, 96, 0, 0, 0           // the street
		};
		for (int k = 0; k < houses.Size(); k++) tourViews.Push(houses[k]);
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
				5040, 96, 0, 0, 0           // street
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
				5040, 96, 0, 0, 0           // alley
			};
			if (level.mapname ~== "MAP04") PartyWallViews();
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
		// face the exit switch; the real USE press comes from tools/smoke_MAP01_1.cfg
		if (t == 695) Pose(mo, 3290, 128, 0, 0);
		Forward(mo, t, 725, 10);                    // a way out that is walked into (AJAR_EXIT=2)
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

	void TestLevelScript(Actor mo, int t, int mode)
	{
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
		// room keys held, top right
		int kx = -8;
		for (int k = 4; k >= 1; k--)
		{
			if (!CPlayer.mo.FindInventory(String.Format("AjarKey%d", k))) continue;
			DrawImage(String.Format("AJKI%d", k), (kx, 8), DI_SCREEN_RIGHT_TOP | DI_ITEM_RIGHT_TOP, 1.0, (-1, -1), (2, 2));
			kx -= 62;
		}
		let h = AjarHandler(EventHandler.Find("AjarHandler"));
		if (!h || !h.carried) return;
		DrawImage(String.Format("AJDR%d", h.carried.args[1]), (-8, 28),
			DI_SCREEN_RIGHT_BOTTOM | DI_ITEM_RIGHT_BOTTOM, 1.0, (-1, -1), (1.5, 1.5));
	}
}
