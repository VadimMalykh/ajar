// Begin anew in a fight (PLAN.md, "Begin anew in a fight"; MAP32 rooms 3
// and 4; MAP=MAP32 MODE=5 tools/smoke.sh).
//
// AjarFightAnew thing: a big bright plate on a wall of an open fight's hall
// (in its zone, by the way in). While the fight is on and not won, USE puts
// it back as it was when the player first came in: every monster of it as at
// the start (the living and the bodies gone, every wave's cues ready, wave 1
// comes again), every pick-up of its zones (hall, lobby, boxes) back where it
// lay, the player's health, armour, weapons and ammunition as they were then,
// and the player where they stood then, facing as then, standing still; all
// its boxes unused, every take, log, earlier self and demo forgotten, the
// doors as at the first entry, the presses up, the key levers up and the
// shutters shut (none keyed: keys.zs). The
// level's kill and item counts are as they were then too. Nothing gained in
// the fight survives it.
// In a fight that has such a plate, death after its last box does the same
// (Rescue), instead of the show being over (or a spare box of an earlier
// fight being used).
// Once the fight is won, the plate is the room of goes' (plate.zs, Anew):
// every go since the win is forgotten. A fight is never un-won.
//
// What the first entry was is kept when the fight begins (Begin, KeepFirst):
// AjarFirstEntry.

class AjarFightAnew : Actor
{
	Default { Radius 24; Height 56; +NOGRAVITY +WALLSPRITE +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJAF A 18 Bright;
		AJAF B 18 Bright;
		Loop;
	}

	override bool Used(Actor user)
	{
		let h = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let mo = PlayerPawn(user);
		if (!h || !mo || !mo.player) return false;
		h.UseFightAnew(mo, self);
		return true;
	}
}

// An open fight as the player first came into it.
class AjarFirstEntry play
{
	int fight;
	// the player
	Vector3 pos;
	double angle, pitch;
	int health;
	class<Weapon> ready;
	Array<class<Inventory> > invCls;
	Array<int> invAmt, invMax;
	int armAmt, armMax, armAbsorb, armMaxAbsorb, armFull, armBonus, armActual;
	double armPct;
	Name armType;
	// the level's counts
	int kills, items, levelKilled, levelMonsters, levelFound, levelItems;
	// what lay in the fight's zones to be picked up
	Array<Inventory> pick;
	Array<class<Inventory> > pickCls;
	Array<double> px, py, pz, pa;
}

extend class AjarTimeHandler
{
	AjarFirstEntry first;

	// Something a player picks up (and not a door, a key of the house or the like).
	static bool Pickup(Actor a)
	{
		return a is "Health" || a is "Ammo" || a is "Weapon" || a is "Armor" || a is "PowerupGiver" || a is "BackpackItem"
			|| a is "HealthPickup" || a is "Megasphere";
	}

	// Does fight k have a plate that begins it anew (in its hall's zone)?
	bool HasFightAnew(int k)
	{
		let it = ThinkerIterator.Create("AjarFightAnew");
		Actor a;
		while (a = Actor(it.Next()))
		{
			int pk, pb;
			[pk, pb] = Where(a.pos.xy);
			if (pk == k && pb == 0) return true;
		}
		return false;
	}

	// The fight begins (Begin): how it is.
	void KeepFirst(int k)
	{
		if (first && first.fight == k) return;      // begun anew (FightAnew): the first entry stays the first
		first = null;
		let mo = players[consoleplayer].mo;
		if (!open || !mo || !mo.player) return;
		let f = new("AjarFirstEntry");
		f.fight = k;
		f.pos = mo.pos; f.angle = mo.angle; f.pitch = mo.pitch;
		f.health = mo.health;
		f.ready = mo.player.ReadyWeapon ? mo.player.ReadyWeapon.GetClass() : null;
		for (Inventory it = mo.Inv; it; it = it.Inv)
		{
			let arm = BasicArmor(it);
			if (arm)
			{
				f.armAmt = arm.Amount; f.armMax = arm.MaxAmount; f.armAbsorb = arm.AbsorbCount; f.armMaxAbsorb = arm.MaxAbsorb;
				f.armFull = arm.MaxFullAbsorb; f.armBonus = arm.BonusCount; f.armActual = arm.ActualSaveAmount;
				f.armPct = arm.SavePercent; f.armType = arm.ArmorType;
				continue;
			}
			if (!(it is "Weapon" || it is "Ammo" || it is "Powerup")) continue;
			f.invCls.Push(it.GetClass()); f.invAmt.Push(it.Amount); f.invMax.Push(it.MaxAmount);
		}
		f.kills = mo.player.killcount; f.items = mo.player.itemcount;
		f.levelKilled = level.killed_monsters; f.levelMonsters = level.total_monsters;
		f.levelFound = level.found_items; f.levelItems = level.total_items;
		let it = ThinkerIterator.Create("Inventory");
		Inventory a;
		while (a = Inventory(it.Next()))
		{
			if (a.owner || !a.bSpecial || !Pickup(a)) continue;
			int ak, ab;
			[ak, ab] = Where(a.pos.xy);
			if (ak != k || ab < 0) continue;
			f.pick.Push(a); f.pickCls.Push(a.GetClass());
			f.px.Push(a.pos.x); f.py.Push(a.pos.y); f.pz.Push(a.pos.z); f.pa.Push(a.angle);
		}
		first = f;
	}

	// The plate is used.
	void UseFightAnew(PlayerPawn mo, Actor plate)
	{
		int k, b;
		[k, b] = Where(plate.pos.xy);
		if (goes && fight == k) { Anew(mo); return; }       // won: a room of goes now (plate.zs)
		if (open && phase == LIVE && fight == k && first && first.fight == k)
		{
			FightAnew(mo, false);
			return;
		}
		if (won.Find(k) < won.Size()) Say("The fight is won. There is nothing to begin anew.");
		else Say("Nothing to begin anew here.");
	}

	// Everything of fight `fight` as at the first entry (`killed`: by a death after its last box, Rescue).
	void FightAnew(PlayerPawn mo, bool killed)
	{
		let h = Doors();
		int k = fight;
		// out of whatever box they are in (an open fight is not watched; but to be sure)
		while (pending.Size())
		{
			if (pending[0]) { pending[0].bInvisible = false; pending[0].tics = pendingTics[0]; }
			pending.Delete(0); pendingTics.Delete(0);
		}
		DropPuppets(-1);
		Unfreeze();
		for (int n = 1; h.FindLine(BoxLine(k, n)); n++) h.Link(BoxLine(k, n), 0, TIME_TEX);
		HallDoors(0);
		at = 0;
		// the doors as at the first entry (a door in the player's hands is put back too)
		FirstDoors();
		// every monster, body, shot and thing dropped of the fight gone, the cues ready
		ClearHall();
		ClearBoxes(k);
		PressesUp();
		ShuttersShut();
		PickupsBack(k);
		PlayerBack(mo);
		// the counts as then (wave 1 is counted again when it comes)
		mo.player.killcount = first.kills; mo.player.itemcount = first.items;
		level.killed_monsters = first.levelKilled; level.total_monsters = first.levelMonsters;
		level.found_items = first.levelFound; level.total_items = first.levelItems;
		// what the reel would keep of this fight did not happen
		for (int i = kills.Size() - 1; i >= 0; i--) if (kills[i].fight == k) kills.Delete(i);
		for (int i = clips.Size() - 1; i >= 0; i--) if (clips[i].fight == k) clips.Delete(i);
		for (int i = lastKills.Size() - 1; i >= 0; i--) if (lastKills[i].fight == k) lastKills.Delete(i);
		dueKills.Clear(); dueTic.Clear(); dueLast = null;
		over = 0; stand = 0; rescued = false; wound = false; comeBack = false;
		mo.player.cheats &= ~(CF_FROZEN | CF_TOTALLYFROZEN);
		// and it begins: no takes, no earlier selves, no demo, every box unused
		Begin(k);
		mo.A_SetBlend(killed ? "ff2010" : "a0d0ff", 1.0, 40);
		mo.A_StartSound("misc/teleport", CHAN_AUTO);
		if (killed) Say("You were killed, and no box is left.\nThe fight begins anew: it is as when you first came in.");
		else Say("The fight begins anew: it is as when you first came in.\nAll its boxes are unused.");
	}

	// What ClearHall leaves in the boxes: bodies, shots, things dropped.
	void ClearBoxes(int k)
	{
		Array<Actor> gone;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a is "AjarGhost" || a.player) continue;
			let inv = Inventory(a);
			if (!(a.bIsMonster || a.bMissile || a.bCorpse || (inv && !inv.owner && inv.bDropped))) continue;
			int ak, ab;
			[ak, ab] = Where(a.pos.xy);
			if (ak == k && ab >= 0) gone.Push(a);
		}
		for (int i = 0; i < gone.Size(); i++)
		{
			if (gone[i].bIsMonster && gone[i].health > 0) gone[i].ClearCounters();
			gone[i].Destroy();
		}
	}

	// Every pick-up of the fight's zones where it lay at the first entry; nothing else.
	void PickupsBack(int k)
	{
		let it = ThinkerIterator.Create("Inventory");
		Inventory a;
		Array<Inventory> extra;
		while (a = Inventory(it.Next()))
		{
			if (a.owner || !Pickup(a) || first.pick.Find(a) < first.pick.Size()) continue;
			int ak, ab;
			[ak, ab] = Where(a.pos.xy);
			if (ak == k && ab >= 0) extra.Push(a);
		}
		for (int i = 0; i < extra.Size(); i++) extra[i].Destroy();
		for (int i = 0; i < first.pick.Size(); i++)
		{
			Inventory p = first.pick[i];
			Vector3 at = (first.px[i], first.py[i], first.pz[i]);
			if (p && !p.owner && p.bSpecial)
			{
				if ((p.pos - at).Length() > 0) p.SetOrigin(at, false);
				p.vel = (0, 0, 0);
				continue;
			}
			p = Inventory(Actor.Spawn(first.pickCls[i], at));
			if (!p) continue;
			p.angle = first.pa[i];
			p.vel = (0, 0, 0);
			first.pick[i] = p;
		}
	}

	// The player as at the first entry.
	void PlayerBack(PlayerPawn mo)
	{
		// weapons, ammunition and powers they had then and have not now
		for (int i = 0; i < first.invCls.Size(); i++)
			if (!mo.FindInventory(first.invCls[i])) mo.GiveInventoryType(first.invCls[i]);
		// and what they have now and had not then
		Array<Inventory> extra;
		for (Inventory it = mo.Inv; it; it = it.Inv)
		{
			if (!(it is "Weapon" || it is "Powerup")) continue;
			if (first.invCls.Find(it.GetClass()) == first.invCls.Size()) extra.Push(it);
		}
		for (int i = 0; i < extra.Size(); i++) extra[i].Destroy();
		// how much of each
		for (Inventory it = mo.Inv; it; it = it.Inv)
		{
			if (it is "Ammo")
			{
				int j = first.invCls.Find(it.GetClass());
				it.Amount = j < first.invCls.Size() ? first.invAmt[j] : 0;
				it.MaxAmount = j < first.invCls.Size() ? first.invMax[j] : GetDefaultByType(it.GetClass()).MaxAmount;
			}
			let arm = BasicArmor(it);
			if (arm)
			{
				arm.Amount = first.armAmt; arm.MaxAmount = first.armMax; arm.AbsorbCount = first.armAbsorb;
				arm.MaxAbsorb = first.armMaxAbsorb; arm.MaxFullAbsorb = first.armFull; arm.BonusCount = first.armBonus;
				arm.ActualSaveAmount = first.armActual; arm.SavePercent = first.armPct; arm.ArmorType = first.armType;
			}
		}
		if (first.ready)
		{
			let w = Weapon(mo.FindInventory(first.ready));
			if (w && w != mo.player.ReadyWeapon) mo.player.PendingWeapon = w;
		}
		mo.health = mo.player.health = first.health;
		mo.bBuddha = false;
		mo.SetOrigin(first.pos, false);
		mo.angle = first.angle;
		mo.pitch = first.pitch;
		mo.vel = (0, 0, 0);
		mo.player.vel = (0, 0);
		mo.player.poisoncount = 0;
	}

	// The last box's message, in a fight that begins anew or not.
	string LastBoxText()
	{
		if (HasFightAnew(fight)) return "\nThe last box. After this the doors stay shut; the plate by the way in begins the fight anew.";
		return "\nThe last box: after this the doors stay shut, and death is death.";
	}

	// --- the tests: MAP=MAP32 MODE=5 TIMEOUT=300 tools/smoke.sh -----------------
	// Rooms 3 and 4, each entered at its lobby (the rooms before are left at
	// once, so each begins as at the first entry). In each: go 1 picks up
	// what is in the lobby (room 3) and kills two monsters, and is killed into
	// box 1; go 2 picks up box 1's three things and uses the plate: all is as
	// at the first entry. Then every box is used and the player killed after
	// the last: it begins anew again (not the level). Then the fight is won,
	// as before: the steel door opens. Room 3's go 2 stands under the press
	// first, and the wing's shutter is shut again (shutterShutAnew3). Room 4's
	// go 1 pulls the west lever, takes what lies by it and fires at the shut
	// shutter; its go 2 asks every key lever up (the first self's was live), the
	// shutter shut and the wing's pick-ups back (asAtTheFirstEntry4).
	int faStep, faT, faRoom, faTotal, faLeft, faPicks, faDeaths;
	bool faShut3;               // room 3: the wing's shutter was opening, the player under the press, when the plate was used
	bool faMega;                // room 3: go 1 took the megasphere
	bool faLive4;               // room 4: the first self's west lever was live when the plate was used
	AjarFightAnew faPlate;

	AjarFightAnew FightAnewOf(int k)
	{
		let it = ThinkerIterator.Create("AjarFightAnew");
		AjarFightAnew a;
		while (a = AjarFightAnew(it.Next()))
		{
			int pk, pb;
			[pk, pb] = Where(a.pos.xy);
			if (pk == k) return a;
		}
		return null;
	}

	// ownerless pick-ups in fight k's zones (`placed`: of them, those that lie where one lay at the first entry)
	int, int PicksIn(int k)
	{
		int n = 0, placed = 0;
		let it = ThinkerIterator.Create("Inventory");
		Inventory a;
		while (a = Inventory(it.Next()))
		{
			if (a.owner || !a.bSpecial || !Pickup(a)) continue;
			int ak, ab;
			[ak, ab] = Where(a.pos.xy);
			if (ak != k || ab < 0) continue;
			n++;
			for (int i = 0; first && i < first.pickCls.Size(); i++)
				if (a.GetClass() == first.pickCls[i] && a.pos.x == first.px[i] && a.pos.y == first.py[i]) { placed++; break; }
		}
		return n, placed;
	}

	int BodiesIn(int k)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health > 0) continue;
			int ak, ab;
			[ak, ab] = Where(a.pos.xy);
			if (ak == k && ab >= 0) n++;
		}
		return n;
	}

	// Two living monsters of the fight, awake, killed by the player.
	void KillTwo(Actor mo)
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		Array<Actor> them;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || OnDemo(a)) continue;
			int ak, ab;
			[ak, ab] = Where(a.pos.xy);
			if (ak == fight && them.Size() < 2) them.Push(a);
		}
		for (int i = 0; i < them.Size(); i++) them[i].DamageMobj(mo, mo, 100000, 'None', DMG_THRUSTLESS);
	}

	// As at the first entry? (the monsters are checked once wave 1 is in: AsAtFirstMonsters)
	bool AsAtFirst(PlayerPawn mo, int k)
	{
		let h = Doors();
		bool doors = !(h.FindLine(HallLine(k, 1)).flags & Line.ML_BLOCKING);
		for (int n = 1; h.FindLine(BoxLine(k, n)); n++) if (!(h.FindLine(BoxLine(k, n)).flags & Line.ML_BLOCKING)) doors = false;
		int picks, placed;
		[picks, placed] = PicksIn(k);
		let arm = BasicArmor(mo.FindInventory("BasicArmor"));
		bool inv = mo.CountInv("RocketAmmo") == CountFirst("RocketAmmo") && mo.CountInv("Cell") == CountFirst("Cell")
			&& mo.CountInv("Clip") == CountFirst("Clip") && (mo.FindInventory("PlasmaRifle") != null) == (CountFirst("PlasmaRifle") > 0)
			&& (mo.FindInventory("RocketLauncher") != null) == (CountFirst("RocketLauncher") > 0) && (!arm || arm.Amount == first.armAmt);
		Console.Printf("AJARTEST info anew%d fight=%d phase=%d open=%d mixed=%d takes=%d trips=%d at=%d ghosts=%d demo=%d doors=%d picks=%d/%d of %d inv=%d health=%d/%d pos=(%d,%d,%d)/(%d,%d,%d) ang=%d/%d kills=%d/%d level=%d/%d bodies=%d over=%d",
			k, fight, phase, open, mixed, takes.Size(), trips, at, AllGhosts(), demo != null, doors, picks, placed, first.pick.Size(), inv,
			mo.health, first.health, mo.pos.x, mo.pos.y, mo.pos.z, first.pos.x, first.pos.y, first.pos.z, mo.angle, first.angle,
			mo.player.killcount, first.kills, level.killed_monsters, first.levelKilled, BodiesIn(k), over);
		return fight == k && phase == LIVE && open && mixed && !goes && takes.Size() == 1 && trips == 0 && at == 0 && !AllGhosts() && !demo
			&& doors && picks == first.pick.Size() && placed == picks && inv && mo.health == first.health
			&& Near(mo, first.pos.x, first.pos.y) && abs(mo.pos.z - first.pos.z) < 1 && mo.angle == first.angle && mo.vel.Length() < 1
			&& mo.player.killcount == first.kills && level.killed_monsters == first.levelKilled && !BodiesIn(k) && !over;
	}

	int CountFirst(class<Inventory> cls)
	{
		int j = first.invCls.Find(cls);
		return j < first.invCls.Size() ? first.invAmt[j] : 0;
	}

	void FightAnewScript(PlayerPawn mo)
	{
		if (level.totaltime > level.maptime + 10) return;       // the level again: it must not be
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		int g = takes.Size(), o = ot, k, bx;
		[k, bx] = Where(mo.pos.xy);
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) fight=%d phase=%d goes=%d open=%d at=%d go=%d trips=%d ot=%d selves=%d left=%d kills=%d/%d health=%d room=%d step=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, fight, phase, goes, open, at, g, trips, o, AllGhosts(), phase ? Left() : -1,
			level.killed_monsters, level.total_monsters, mo.health, faRoom, faStep);
		// room 3, then room 4: into its lobby, facing on (the room before is left, and over)
		if (t == 2) { faRoom = 3; Go(mo, 4872, 100, 0, 90); }
		if (faStep == 99 && t == faT + 40) { faRoom = 4; faStep = 0; Go(mo, 6950, 176, -96, 0); }
		int R = faRoom;
		if (!R) return;
		bool r3 = R == 3;
		double bz = r3 ? 64 : -32;          // box 1's floor
		// --- begun: the first entry is kept ---
		if (faStep == 0 && fight == R && open && phase == LIVE && g == 1 && o == 3)
		{
			faPlate = FightAnewOf(R);
			int picks, placed;
			[picks, placed] = PicksIn(R);
			faTotal = level.total_monsters; faLeft = Left();
			Console.Printf("AJARTEST info room=%d picks=%d placed=%d left=%d total=%d", R, picks, placed, faLeft, faTotal);
			Check(String.Format("firstKept%d", R), first && first.fight == R && faPlate && picks >= (r3 ? 17 : 9) && placed == picks
				&& Near(mo, first.pos.x, first.pos.y) && faLeft > 0);
			faPicks = picks;
			faStep = 1;
		}
		// go 1: what lies in the lobby (room 3: the plasma rifle, the rockets), two monsters killed, and killed into box 1
		if (faStep == 1 && g == 1)
		{
			if (r3 && o == 5) Go(mo, 4800, 160, 0, 90);
			if (r3 && o > 5 && o < 10) Walk(mo, (0, 8));
			if (r3 && o == 11) Go(mo, 4860, 220, 0, 90);
			if (r3 && o > 11 && o < 16) Walk(mo, (0, 8));
			// (room 3: and the megasphere in the cage, stepped into from behind its shut shutter)
			if (r3 && o == 16) Go(mo, 5940, -120, 96, 90);
			if (r3 && o > 16 && o < 20) Walk(mo, (0, 8));
			if (!r3 && o == 5) { mo.GiveInventory("RocketLauncher", 1); mo.GiveInventory("RocketAmmo", 20); }
			if (r3 && o == 20) KillTwo(mo);
			if (r3 && o == 29) faMega = !MegaThere33() && mo.health >= 200;
			if (r3 && o == 30) mo.health = mo.player.health = 1;
			// (room 4: the west lever pulled, what lies by it taken, rockets fired at the shut shutter)
			if (!r3 && o == 6) Go(mo, 7040, 1340, -96, 90);
			if (!r3 && o == 8) { AjarKeyLever kw = FindKeyLever(SHUT32, 1); if (kw) kw.Used(mo); }
			if (!r3 && o == 10) Go(mo, 6930, 1250, -96, 0);
			if (!r3 && o > 10 && o <= 30) Walk(mo, (8, 0));
			if (!r3 && o == 32) Go(mo, 7456, 120, -96, 90);
			if (!r3 && (o == 34 || o == 40)) ShootPen(mo, o);
			if (!r3 && o == 44) KillTwo(mo);
			if (!r3 && o == 50) mo.health = mo.player.health = 1;
		}
		// go 2: box 1's armour, medikit and the next; then the plate
		if (faStep == 1 && g == 2)
		{
			double x0 = r3 ? 4810 : 7240, y0 = r3 ? 600 : -150, dy = r3 ? 8 : -8;
			if (o == 2) Check(String.Format("killedIntoTheBox%dx", R), at == 1 && bx == 1 && BodiesIn(R) == 0);
			if (o == 3) mo.health = mo.player.health = 40;
			for (int i = 0; i < 3; i++)
			{
				if (o == 5 + 8 * i) Go(mo, x0 + 40 * i, y0, bz, 90);
				if (o > 5 + 8 * i && o < 10 + 8 * i) Walk(mo, (0, dy));
			}
			if (o == 32)
			{
				int picks, placed;
				[picks, placed] = PicksIn(R);
				Console.Printf("AJARTEST info room=%d picks=%d health=%d armour=%d", R, picks, mo.health, mo.CountInv("BasicArmor"));
				Check(String.Format("pickedUp%d", R), picks <= faPicks - (r3 ? 5 : 3) && mo.CountInv("BasicArmor") > 0);
			}
			// out into the hall, two more killed, and to the plate
			if (o == 34) { Go(mo, r3 ? 5100 : 7300, r3 ? 200 : 100, r3 ? 0 : -96, 90); }
			// (room 3: under the press, in its mouth, so that the wing's shutter is opening)
			if (r3 && o == 35) Go(mo, 5768, 784, 0, 90);
			if (o == 40) KillTwo(mo);
			// (room 4: the first self's west lever is live, pulled again, when the plate is used)
			if (!r3 && o == 43) { AjarKeyLever kw = FindKeyLever(SHUT32, 1); faLive4 = kw && kw.Live(); }
			if (o == 44)
			{
				if (r3)
				{
					AjarShutter sh3 = FindShutter(SHUT33);
					faShut3 = sh3 && sh3.Opened() > 0.3 && sh3.PlayerIn();
					Console.Printf("AJARTEST info shutter opened=%.2f under=%d", sh3 ? sh3.Opened() : -1, sh3 && sh3.PlayerIn());
				}
				Check(String.Format("plateThere%d", R), faPlate != null);
				Vector2 front = faPlate.pos.xy + Actor.AngleToVector(faPlate.angle, 40);
				Go(mo, front.x, front.y, r3 ? 0 : -96, faPlate.angle + 180);
				faPlate.Used(mo);
				faStep = 2;
				faT = t;
			}
		}
		if (faStep == 2 && t == faT + 1)
		{
			bool rest = true;
			if (r3)
			{
				// room 3: the screen open, the cage shut, the megasphere (taken in go 1) back
				AjarShutter scr = FindShutter(SCREEN3), cage = FindShutter(CAGE3);
				rest = scr.IsOpen() && cage.IsShut() && MegaThere33();
				Console.Printf("AJARTEST info room 3 at rest: screen=%.2f cage=%.2f megasphere=%d took=%d", scr.Opened(), cage.Opened(), MegaThere33(), faMega);
			}
			else
			{
				// room 4: every key lever up (the first self's was live), the shutter shut and not keyed
				AjarShutter sh = FindShutter(SHUT32);
				AjarKeyLever kw = FindKeyLever(SHUT32, 1), ke = FindKeyLever(SHUT32, 2);
				rest = faLive4 && kw && ke && kw.Up() && ke.Up() && sh.IsShut() && !sh.keyed;
				Console.Printf("AJARTEST info room 4 at rest: was live=%d up=%d/%d shutter=%.2f keyed=%d", faLive4, kw && kw.Up(), ke && ke.Up(), sh.Opened(), sh.keyed);
			}
			Check(String.Format("asAtTheFirstEntry%d", R), AsAtFirst(mo, R) && rest && (!r3 || faMega));
			if (r3)
			{
				AjarShutter sh3 = FindShutter(SHUT33);
				Check("shutterShutAnew3", faShut3 && sh3.IsShut() && !sh3.PlayerIn());
			}
		}
		if (faStep == 2 && t == faT + 4)
		{
			Console.Printf("AJARTEST info room=%d left=%d/%d total=%d/%d", R, Left(), faLeft, level.total_monsters, faTotal);
			Check(String.Format("monstersAsAtFirst%d", R), Left() == faLeft && level.total_monsters == faTotal && !BodiesIn(R) && takes.Size() == 1);
			faStep = 3;
			faDeaths = 0;
		}
		// every box, then killed after the last (out in the hall): it begins anew again
		if (faStep == 3 && open && fight == R && trips == BoxCount(R) && o == 10 * (g + 1) - 4)
			Go(mo, r3 ? 5100 : 7300, r3 ? 200 : 100, r3 ? 0 : -96, 90);
		if (faStep == 3 && open && fight == R && o == 10 * (g + 1))
		{
			if (trips < BoxCount(R))
			{
				if (trips == g - 1) { mo.health = mo.player.health = 1; faDeaths++; }
			}
			else
			{
				Check(String.Format("everyBoxUsed%d", R), faDeaths == BoxCount(R) && g == BoxCount(R) + 1 && at == 0 && bx == 0);
				mo.health = mo.player.health = 1;
				faStep = 4;
				faT = t;
			}
		}
		if (faStep == 4 && t == faT + 2)
		{
			Check(String.Format("killedAfterTheLastBox%d", R), AsAtFirst(mo, R) && level.mapname ~== "MAP32");
			faStep = 5;
		}
		// and it can be won as before
		if (faStep == 5 && open && fight == R && o > 10 && o % 5 == 0) KillAll(mo);
		if (faStep == 5 && goes && fight == R)
		{
			Check(String.Format("wonAfterAnew%d", R), won.Find(R) < won.Size() && !open && !Left() && goesWon);
			faStep = 6;
			faT = t;
		}
		if (faStep == 6 && t == faT + 40)
		{
			Check(String.Format("steelAfterAnew%d", R), SteelUp(R));
			// the plate in a won fight forgets the goes since the win, as in a room of goes
			faPlate.Used(mo);
			Check(String.Format("wonStaysWon%d", R), goes && won.Find(R) < won.Size() && takes.Size() == 1);
			faStep = R == 3 ? 99 : 100;
			faT = t;
		}
	}

	// MODE=6: the two plates as the player sees them coming in (smoke_MAP32_6.cfg takes a screenshot of each).
	void AnewViews32(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		static const double v[] = {
			4872, 90, 0, 90, 0,             // room 3: off the ledge into the lobby
			4872, 120, 0, 150, 0,           // and turned to its west wall
			6900, 176, -96, 0, 0,           // room 4: down from the corridor
			6900, 176, -96, 50, 0,          // and turned to the lobby's north wall
			4830, 192, 0, 180, 0,           // room 3's plate, close
			6960, 250, -96, 90, 0           // room 4's plate, close
		};
		int i = t / 40;
		if (i >= v.Size() / 5) return;
		Go(mo, v[i * 5], v[i * 5 + 1], v[i * 5 + 2], v[i * 5 + 3]);
		mo.pitch = v[i * 5 + 4];
		Quiet(mo);
	}
}
