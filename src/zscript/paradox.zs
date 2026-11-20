// The paradox (PLAN.md, "The paradox: touching an earlier self ends the
// universe"; the test MAP=PLATE MODE=5 tools/smoke.sh).
//
// In a room of goes proper (an AjarZone of a hall with args[4] 2: MAP32's
// rooms 1, 2 and 5, the labs PLATE, TWOKEY and SHUT's room of goes; not an
// open fight, not a fight of goes, not even one that has been won and become
// a room of goes: ParadoxHere) the player who touches one of their earlier
// selves (an AjarGhost) has made a time paradox, and this universe is over:
//  * touching is the bodies overlapping: the two boxes (radius 16 each) and
//    their heights. Nothing is shown or heard before it;
//  * a copy counts only while its go is still running (its record is not
//    over) and it stands in the hall; nothing counts while the player is in
//    the box. Every go begins with the player inside their copies (they all
//    start in the box at the same tic), so a copy cannot be touched until
//    the player has once been clear of it in this go (parted, kept per copy
//    and cleared at the start of every go and by begin anew: GoTake). One
//    who walks a copy's path with it and never parts from it is safe;
//  * the player is dead at once, really (through god mode, buddha, armour and
//    powers: the damage is forced), and nothing of the room of goes runs any
//    more (no rescue into the box, no going on as a copy, no beginning anew):
//    the engine begins the level again as after any death. The touched copy
//    is gone; the others stand where they were;
//  * what is seen and heard: a white flash over the whole screen, a loud
//    blast, the screen shaking, and explosions that spread from the point of
//    touch through the room's zones in PARADOX_SPREAD tics and go on all over
//    it for as long again, fewer and fewer; the message
//    "PARADOX" (in red, readable on the white), said again so that it stays
//    longer than the others.
// The tests read paradox and paradoxes; under ajar_autotest a line
// "AJARTEST info paradox ..." gives the tic, the copy and the place.

// One of the explosions: the rocket's, as the Icon of Sin's death has them.
class AjarParadoxBlast : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH RenderStyle "Add"; Alpha 0.95; }
	States
	{
	Spawn:
		MISL B 6 Bright;
		MISL C 5 Bright;
		MISL D 4 Bright;
		Stop;
	}
}

extend class AjarTimeHandler
{
	bool paradox;               // this universe is over
	int paradoxes;              // how many times (tests: once)
	int paradoxTic;             // level.maptime of the touch
	int paradoxCopy;            // the go of the copy that was touched (from 1)
	int paradoxSaid;            // how often the message has been said
	Vector3 paradoxAt;          // where
	double paradoxReach;        // how far the explosions go: to the farthest corner of the room's zones
	Array<bool> parted;         // parted[i]: the player has been clear of the copy of takes[i] in this go

	const PARADOX_SPREAD = 35; // tics the explosions take to fill the room
	const PARADOX_FLASH = 50;   // tics the white takes to fade
	const PARADOX_AGAIN = 90;   // the message is said again after so many tics...
	const PARADOX_SAYS = 3;     // ... until it has been said so often

	// Where the rule holds. Fights of goes and open fights may come later: here alone.
	bool ParadoxHere()
	{
		return goes && !goesWon && goesFights.Find(fight) < goesFights.Size();
	}

	static bool Touching(Actor a, Actor b)
	{
		double r = a.radius + b.radius;
		return abs(a.pos.x - b.pos.x) < r && abs(a.pos.y - b.pos.y) < r
			&& a.pos.z < b.pos.z + b.height && b.pos.z < a.pos.z + a.height;
	}

	// Every tic of a room of goes, after the earlier selves are where they are (GoesTick).
	void ParadoxWatch(PlayerPawn mo)
	{
		if (paradox || !ParadoxHere() || mo.health <= 0) return;
		int k, b;
		[k, b] = Where(mo.pos.xy);
		bool inHall = k == fight && b == 0;
		for (int i = 0; i < takes.Size() - 1 && i < ghosts.Size(); i++)
		{
			while (parted.Size() <= i) parted.Push(false);
			AjarGhost g = ghosts[i];
			if (!g || ot >= takes[i].x.Size()) continue;
			if (!Touching(mo, g)) { parted[i] = true; continue; }
			if (!parted[i] || !inHall) continue;
			int gk, gb;
			[gk, gb] = Where(g.pos.xy);
			if (gk != fight || gb != 0) continue;
			EndUniverse(mo, i);
			return;
		}
	}

	void EndUniverse(PlayerPawn mo, int i)
	{
		AjarGhost g = ghosts[i];
		paradox = true;
		paradoxes++;
		paradoxTic = level.maptime;
		paradoxCopy = i + 1;
		paradoxAt = ((mo.pos.xy + g.pos.xy) / 2, max(mo.pos.z, g.pos.z));
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info paradox t=%d go=%d ot=%d copy=%d at=(%d,%d,%d) me=(%d,%d,%d)", level.maptime, takes.Size(), ot, i + 1,
				g.pos.x, g.pos.y, g.pos.z, mo.pos.x, mo.pos.y, mo.pos.z);
		paradoxReach = 0;
		for (int z = 0; z < zf.Size(); z++)
		{
			if (zf[z] != fight) continue;
			for (int c = 0; c < 4; c++)
			{
				Vector2 corner = (zx[z] + ((c & 1) != 0 ? zw[z] : -zw[z]), zy[z] + ((c & 2) != 0 ? zh[z] : -zh[z]));
				paradoxReach = max(paradoxReach, (corner - paradoxAt.xy).Length());
			}
		}
		// the copy is gone in it
		g.Destroy();
		ghosts[i] = null;
		for (int n = 0; n < 4; n++) ParadoxBlast(paradoxAt.xy + (frandom[AjarParadox](-24, 24), frandom[AjarParadox](-24, 24)), 1.6);
		// the player is dead: nothing spares them
		mo.player.cheats &= ~(CF_GODMODE | CF_GODMODE2 | CF_BUDDHA | CF_BUDDHA2 | CF_FROZEN | CF_TOTALLYFROZEN);
		mo.bBuddha = false;
		mo.bInvulnerable = false;
		mo.bNoDamage = false;
		stand = 0;
		mo.DamageMobj(null, null, Actor.TELEFRAG_DAMAGE, 'Paradox', DMG_FORCED | DMG_NO_ARMOR | DMG_THRUSTLESS);
		mo.player.damagecount = 0;          // (the white, not the red of a hit)
		mo.player.bonuscount = 0;
		mo.vel = (0, 0, 0);
		mo.A_SetBlend("white", 1.0, PARADOX_FLASH);
		mo.A_QuakeEx(6, 6, 4, 50, 0, 4096, "", QF_SCALEDOWN);
		mo.A_StartSound("weapons/bfgx", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		mo.A_StartSound("weapons/rocklx", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		mo.A_StartSound("world/barrelx", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE);
		ParadoxSay();
	}

	void ParadoxSay()
	{
		paradoxSaid++;
		Say("\cgPARADOX\n\n\cgYou touched your earlier self.\n\cgThis universe is over.");
	}

	// An explosion at p, on the floor or a little above it, if p is in the room.
	void ParadoxBlast(Vector2 p, double size = 1)
	{
		int k, b;
		[k, b] = Where(p);
		if (k != fight) return;
		Sector sec = level.PointInSector(p);
		double fl = sec.floorplane.ZAtPoint(p), ce = sec.ceilingplane.ZAtPoint(p);
		if (ce - fl < 32 || !level.IsPointInLevel((p, fl + 1))) return;
		let a = Actor.Spawn("AjarParadoxBlast", (p, fl + frandom[AjarParadox](4, min(64, ce - fl - 24))));
		if (!a) return;
		a.scale *= size * frandom[AjarParadox](0.8, 1.4);
		a.vel.z = frandom[AjarParadox](0, 1.5);
		a.tics -= random[AjarParadox](0, 3);
	}

	// A place in one of the room's zones no farther than r from the touch (a few tries).
	bool, Vector2 ParadoxInRoom(double r)
	{
		Array<int> mine;
		for (int z = 0; z < zf.Size(); z++) if (zf[z] == fight) mine.Push(z);
		if (!mine.Size()) return false, (0, 0);
		for (int i = 0; i < 6; i++)
		{
			int z = mine[random[AjarParadox](0, mine.Size() - 1)];
			Vector2 p = (zx[z] + frandom[AjarParadox](-zw[z], zw[z]), zy[z] + frandom[AjarParadox](-zh[z], zh[z]));
			if ((p - paradoxAt.xy).Length() <= r) return true, p;
		}
		return false, (0, 0);
	}

	// Every tic once the universe is over: the explosions spread, and the
	// message is said again. Nothing else of the room runs.
	void ParadoxTick(PlayerPawn mo)
	{
		int t = level.maptime - paradoxTic;
		if (t > 0 && t <= 2 * PARADOX_SPREAD)
		{
			// the front, while it spreads; and behind it, all over what it has reached, until 2 * PARADOX_SPREAD
			double r = paradoxReach * min(t, PARADOX_SPREAD) / PARADOX_SPREAD;
			int n = t <= PARADOX_SPREAD ? clamp(int(r / 64), 3, 10) : 0;
			for (int j = 0; j < n; j++)
				ParadoxBlast(paradoxAt.xy + Actor.AngleToVector(frandom[AjarParadox](0, 360), r + frandom[AjarParadox](-32, 32)));
			int m = int(clamp(r / 96, 2, 8) * min(1., 2. - double(t) / PARADOX_SPREAD) + 0.5);
			for (int j = 0; j < m; j++)
			{
				bool ok;
				Vector2 p;
				[ok, p] = ParadoxInRoom(r);
				if (ok) ParadoxBlast(p);
			}
			if (t % 4 == 0)
				mo.A_StartSound("weapons/rocklx", CHAN_AUTO, CHANF_DEFAULT, 0.9 - 0.6 * t / (2 * PARADOX_SPREAD), ATTN_NONE);
		}
		if (t > 0 && t % PARADOX_AGAIN == 0 && paradoxSaid < PARADOX_SAYS) ParadoxSay();
	}
}
