// Stepping out of a fight (PLAN.md, "Step out of the fight"; tools/ajartime.py).
//
// A fight has a hall, and boxes that look into the hall through glass. The
// hall has time doors. Going through one, the player is in the next box,
// before the fight began: through the glass the fight is seen from its start,
// their earlier self in it. When it reaches the moment they left, the box's
// door opens onto the door they left by, and the fight goes on from there.
//
// Nothing is rewound. While the player watches, the hall's real monsters,
// shots and things stand still and unseen where they were, and puppets
// (AjarEcho) play what was recorded; at the end the puppets stand exactly
// where the real ones do and are taken away. So the past cannot be changed,
// and nothing has to be put back.
//
// Map contract:
//  * AjarZone thing: args[0] fight, args[1] 0 for the hall (and the way into
//    it) or the number of a box, args[2] and args[3] half its size along x
//    and y. A place may have several. A box is looked for before a hall, so
//    a hall's zone may be drawn generously.
//  * Lines 3000 + 100 * fight + j: the hall's time doors, j from 1.
//    Lines 3050 + 100 * fight + n: the door of box n. All are portal lines
//    as a door's far side is (ajarmap.recess).
//  * Sector tag 3090 + 100 * fight: opened (Door_Open) when the fight is won.
//  * AjarCue thing: a monster that comes into the fight later. args[0] fight,
//    args[1] its wave (from 1), args[2] the wave comes when no more than
//    that many monsters are left, or 25 seconds after the wave before it
//    was due (Cues), args[3] the monster's Doom editor number.
//
//  * Sector tag and line id 3080 + 100 * fight: the hall's sectors and its
//    screen (the upper texture of that line, a name whose fifth letter is a
//    digit: 0 blank, 3, 2, 1 the count). A hall that has them has a show:
//    see "the show" below. Such a hall should start empty, its first
//    monsters being AjarCues of wave 1 that come at 0 left.
//
//  * An AjarZone of the hall with args[4] set makes the fight an OPEN one:
//    see "the open fight" below. Its first monsters must all be AjarCues.
//
//  * AjarLocker thing: a cupboard. args[0] the room key that opens it,
//    args[1] and args[2] the Doom editor numbers of what is in it.
//
// Whatever was right behind the player at a time door comes out with them
// (FOLLOW_NEAR, two at most): it is in the box, and gone from the fight.
//
// In a fight's zones everything that changes must be a thing: a lift or a
// door that moved would not be played back.

class AjarZone : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
}

class AjarCue : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
}

// A cupboard that a room key opens (a thing, so that it is played back).
class AjarLocker : Actor
{
	Default { Radius 20; Height 56; +SOLID }
	States
	{
	Spawn:
		AJLK A -1;
		Stop;
	Open:
		AJLK B -1;
		Stop;
	}

	static class<Actor> What(int n)
	{
		switch (n)
		{
		case 2003: return "RocketLauncher";
		case 2046: return "RocketBox";
		case 2004: return "PlasmaRifle";
		case 17: return "CellPack";
		case 2006: return "BFG9000";
		case 2002: return "Chaingun";
		case 82: return "SuperShotgun";
		case 2013: return "Soulsphere";
		case 2019: return "BlueArmor";
		}
		return null;
	}

	override bool Used(Actor user)
	{
		if (frame) return false;
		if (!user.FindInventory(String.Format("AjarKey%d", args[0])))
		{
			Console.MidPrint(smallfont, String.Format("The cupboard is locked.\nRoom key %d opens it.", args[0]));
			return true;
		}
		SetStateLabel("Open");
		A_StartSound("doors/dr1_open", CHAN_AUTO);
		Vector2 side = AngleToVector(angle + 90, 18);
		for (int i = 1; i <= 2; i++)
		{
			class<Actor> cls = What(args[i]);
			if (cls) Spawn(cls, (pos.xy + AngleToVector(angle, 44) + side * (i == 1 ? -1 : 1), pos.z), ALLOW_REPLACE);
		}
		return true;
	}
}

// A plate on a wall of a box beside its glass, and of an open fight's hall
// beside the way in: USE winds the fight that is played or watched half a
// minute back (args[0] 0) or on (1). See AjarTimeHandler.Wind.
class AjarWind : Actor
{
	Default { Radius 12; Height 24; +NOGRAVITY +WALLSPRITE +DONTTHRUST +NOTELEPORT }
	States
	{
	Spawn:
		AJWD A -1 Bright;
		Stop;
	On:
		AJWD B -1 Bright;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		if (args[0]) SetStateLabel("On");
	}

	override bool Used(Actor user)
	{
		let h = AjarTimeHandler(EventHandler.Find("AjarTimeHandler"));
		let mo = PlayerPawn(user);
		if (!h || !mo || !mo.player) return false;
		h.Wind(mo, args[0] ? 1 : -1);
		return true;
	}
}

// What is seen of something as it was: a picture and nothing more.
class AjarEcho : Actor
{
	Default { +NOINTERACTION +NOBLOCKMAP +NOGRAVITY }
	States { Spawn: TNT1 A -1; Stop; }
}

// The player is never killed in a fight: at the last moment they are taken
// out of it, to before it began. What is seen of that where they stood: their
// own shape gone to light, rising and fading, in a teleport's flash. A thing
// of the hall like any other, so a replay shows it at that moment.
class AjarSnatch : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY RenderStyle "Add"; }
	States
	{
	Spawn:
		TNT1 A 0;
	Fade:
		#### # 1 Bright A_FadeOut(0.03);
		Loop;
	}
}

// The reel's camera.
class AjarCam : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }
}

// One tic of a hall, for the reel: everything in it.
class AjarStill play
{
	Array<class<Actor> > cls;
	Array<double> x, y, z, ang;
	Array<int> sf;
	int me;                     // which of them is the player (-1: none)
}

// The last seconds before the player was killed in a hall.
class AjarClip play
{
	int fight;
	Vector3 at;
	double ang;
	Array<AjarStill> stills;
	// not the player's death but a big monster's: how big, and what
	int big;
	string what;
	// ... or the last monster of its hall to be killed, whatever its size
	bool last;
}

// An earlier self in an open fight: it goes where the player went and its
// shots are real. It cannot be hurt, but what it shoots turns on it.
class AjarGhost : Actor
{
	Default { Radius 16; Height 56; +SHOOTABLE +NODAMAGE +NOBLOOD +NOGRAVITY +DONTTHRUST +NOTELEPORT }
	States { Spawn: PLAY A -1; Stop; }
}

// What the player did in one go at an open fight, tic by tic from its start.
class AjarTake play
{
	Array<double> x, y, z, ang, pit;
	Array<int> sf;
	// what was fired: kind 0 a missile (cls, from e, at speed v), 1 a bullet, 2 a shotgun's shot, 3 a super shotgun's
	Array<int> evTic, evKind;
	Array<class<Actor> > evCls;
	Array<double> ex, ey, ez, evx, evy, evz;
	int next;                   // the next of them to be fired again
	bool died;                  // it ended with the player killed, not at a time door
	int door;                   // the hall's door it ended by (its line)
	// what they carried (ammunition and armour): each kind's amount now, and
	// every change of it (at tic carTic, kind carKind had carAmt; pct: an armour's)
	Array<class<Inventory> > kinds;
	Array<int> kindAmt;
	Array<int> carTic, carKind, carAmt;
	Array<double> carPct;
}

// A monster in one go at an open fight: where it was, how it looked and its
// health, tic by tic from the tic it came (sf < 0: it was out of the hall).
class AjarRole play
{
	class<Actor> cls;
	int born;
	AjarCue cue;                // the cue it came by, if any
	AjarRole maker;             // a lost soul's pain elemental
	Array<double> x, y, z, ang;
	Array<int> sf, hp;
	// while it is recorded
	Actor src;
	AjarRole twin;              // of a role being played: its record so far in the go being recorded, when time was wound
	bool seen;
	int lag;                    // tics it has lain dead and still, not written down (it is as it was last)
	// while it is played: mode 0 not yet come, 1 on the demo, 2 no longer
	Actor actor;
	int mode;
	bool dead, wakeDue, hidden;
	int waited;                 // tics it has been due to wake and did not stand free
}

// One go at an open fight, as it went: its monsters, and what they shot.
class AjarDemo play
{
	Array<AjarRole> roles;
	int len;
	Array<int> evTic;
	Array<class<Actor> > evCls;
	Array<AjarRole> evBy;
	Array<double> ex, ey, ez, evx, evy, evz;
	int next;
	AjarTrack fx;               // what was seen besides: flames, puffs, blood, fog
}

// Carried by a monster that is on the demo. Only the player hurts it, and
// that wakes it; its real health is what the demo says (hp) less that (dmg).
class AjarRail : Inventory
{
	int hp, dmg;
	bool hit;
	Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE }
	override void ModifyDamage(int damage, Name damageType, out int newdamage, bool passive, Actor inflictor, Actor source, int flags)
	{
		if (!passive) return;
		if (source && source.player) { dmg += damage; hit = true; newdamage = damage; }
		else newdamage = 0;
	}
}

// What was seen in one place over one stretch of time, from the fight's
// first tic. Only changes are kept: a record says how one thing (its slot)
// looked from that tic on, or that it was gone (sf < 0).
class AjarTrack play
{
	int box;                    // 0: the hall, and each box from the moment its door opened
	bool fx;                    // an open fight's: only what is seen besides its monsters and shots
	Array<int> first;           // first[i]: the first record of tic i
	Array<int> slot, sf;        // sf: sprite * 256 + 128 if bright + frame
	Array<double> x, y, z, ang;
	// what is being recorded
	Array<Actor> live;
	Array<int> liveSlot, liveSf, liveSeen;
	Array<double> lx, ly, lz, la;

	void Put(int s, int f, Vector3 p, double a)
	{
		slot.Push(s); sf.Push(f); x.Push(p.x); y.Push(p.y); z.Push(p.z); ang.Push(a);
	}
}

class AjarTimeHandler : EventHandler
{
	const IDLE = 0;
	const LIVE = 1;
	const REPLAY = 2;
	const TIME_TEX = "AJDR10";

	// the level's zones
	Array<int> zf, zb;
	Array<double> zx, zy, zw, zh;

	int fight;                  // the fight that is on, or the last one
	Array<int> won;             // the fights that are over
	int phase;
	int trips;                  // how many times the player has stepped out of this fight
	int at;                     // where the player is: 0 the hall, n box n
	int used;                   // the hall's door they left by last (its line)
	int rt;                     // REPLAY: the tic of the fight that is being shown
	AjarTrack main;
	Array<AjarTrack> boxes;     // boxes[n - 1]: box n while its door was shut
	Array<class<Actor> > slotCls;
	Array<AjarEcho> puppets;
	Array<int> puppetSlot, puppetTrack;
	Vector3 playerWas;

	// what stands still while the player watches
	Array<Actor> fz, fzTarget;
	Array<int> fzTics, fzFlags;
	Array<double> fzx, fzy, fzz, fzvx, fzvy, fzvz;

	static int HallLine(int k, int j) { return 3000 + 100 * k + j; }
	static int BoxLine(int k, int n) { return 3050 + 100 * k + n; }

	AjarHandler Doors() { return AjarHandler(EventHandler.Find("AjarHandler")); }
	void Say(string s) { let h = Doors(); if (h) h.Say(s); }

	// what came out of the fight behind the player, and is not in the box yet
	Array<Actor> pending;
	Array<int> pendingTics;
	const FOLLOW_NEAR = 150;
	int said;                   // which hints have been given

	// --- places ---------------------------------------------------------------
	// Which fight's zone a point is in, and which box of it (0: the hall; -1: none).
	int, int Where(Vector2 p)
	{
		int k = 0, b = -1;
		for (int i = 0; i < zf.Size(); i++)
		{
			if (abs(p.x - zx[i]) > zw[i] || abs(p.y - zy[i]) > zh[i]) continue;
			if (b < 0 || zb[i] > b) { k = zf[i]; b = zb[i]; }
		}
		return k, b;
	}

	int BoxCount(int k)
	{
		int n = 0;
		for (int i = 0; i < zf.Size(); i++) if (zf[i] == k && zb[i] > n) n = zb[i];
		return n;
	}

	// The hall's doors all open onto box n, one way; with n 0, or no such
	// box, they are shut.
	void HallDoors(int n)
	{
		let h = Doors();
		if (n > BoxCount(fight)) n = 0;
		for (int j = 1; h.FindLine(HallLine(fight, j)); j++)
			h.Link(HallLine(fight, j), n ? BoxLine(fight, n) : 0, TIME_TEX);
	}

	override void WorldLoaded(WorldEvent e)
	{
		if (e.IsSaveGame) return;
		// never begun frozen (a level left by "the show is over" was, once)
		if (players[consoleplayer].mo) players[consoleplayer].cheats &= ~(CF_TOTALLYFROZEN | CF_FROZEN);
		let it = ThinkerIterator.Create("AjarZone");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.args[4]) openFights.Push(a.args[0]);
			zf.Push(a.args[0]); zb.Push(a.args[1]);
			zx.Push(a.pos.x); zy.Push(a.pos.y); zw.Push(a.args[2]); zh.Push(a.args[3]);
		}
		let h = Doors();
		for (int k = 1; k < 10; k++)
		{
			for (int j = 1; h.FindLine(HallLine(k, j)); j++) h.Link(HallLine(k, j), 0, TIME_TEX);
			for (int n = 1; h.FindLine(BoxLine(k, n)); n++) h.Link(BoxLine(k, n), 0, TIME_TEX);
		}
		FindShows();
	}

	// --- the show ---------------------------------------------------------------
	// What tells the player, in a box, that this is the fight from its start
	// again: every fight in a hall with a show begins the same way, and it is
	// the first thing seen through the glass. The house lights are up and the
	// hall is empty; the lights go down; the screen counts 3, 2, 1, a tick to
	// each; at nought the hall flashes and the first monsters come in.
	// Lights and screen are not things, so they are not recorded: they are
	// set from the fight's tic, the one being lived or the one being shown.
	const SHOW_DIM = 50;        // the lights begin to go down
	const SHOW_COUNT = 70;      // "3"; "2" and "1" follow, SHOW_STEP apart
	const SHOW_STEP = 35;
	const SHOW_GO = 175;        // the monsters come
	const SHOW_UP = 232;        // the house lights
	Array<int> showSec, showFight, showDown;    // the halls' sectors, and their light when the lights are down
	int showDigit;              // what the screen of the fight that is on shows

	static int ShowTag(int k) { return 3080 + 100 * k; }

	bool HasShow(int k) { return showFight.Find(k) < showFight.Size(); }

	// The tic of the fight: the one being lived, or the one being shown.
	int FightTic() { return phase == REPLAY ? rt : open ? ot : main ? main.first.Size() : 0; }

	void FindShows()
	{
		for (int k = 1; k < 10; k++)
		{
			let it = level.CreateSectorTagIterator(ShowTag(k));
			int i;
			while ((i = it.Next()) >= 0)
			{
				showSec.Push(i); showFight.Push(k); showDown.Push(level.sectors[i].lightlevel);
			}
			HouseLights(k, 1);
		}
	}

	// up: 0 the lights are down, 1 they are up; over: a flash.
	void HouseLights(int k, double up, double over = 0)
	{
		for (int i = 0; i < showSec.Size(); i++)
		{
			if (showFight[i] != k) continue;
			double l = showDown[i] + (SHOW_UP - showDown[i]) * up;
			level.sectors[showSec[i]].SetLightLevel(int(l + (255 - l) * over));
		}
	}

	void SetScreen(int k, int digit)
	{
		let it = level.CreateLineIdIterator(ShowTag(k));
		int i;
		while ((i = it.Next()) >= 0)
		{
			for (int s = 0; s < 2; s++)
			{
				Side sd = level.lines[i].sidedef[s];
				if (!sd) continue;
				string n = TexMan.GetName(sd.GetTexture(Side.top));
				if (n.Length() < 6) continue;
				TextureID tex = TexMan.CheckForTexture(String.Format("%s%d%s", n.Left(4), digit, n.Mid(5)), TexMan.Type_Any);
				if (tex.IsValid()) sd.SetTexture(Side.top, tex);
			}
		}
	}

	// The hall as it is at tic t of its fight.
	void Show(int k, int t, Actor mo)
	{
		if (!HasShow(k)) return;
		if (t > SHOW_GO + 8) return;            // nothing changes after that
		double up = t < SHOW_DIM ? 1 : t < SHOW_DIM + 20 ? 1 - (t - SHOW_DIM) / 20. : 0;
		double over = t >= SHOW_GO && t < SHOW_GO + 8 ? 1 - (t - SHOW_GO) / 8. : 0;
		HouseLights(k, up, over);
		int d = t < SHOW_COUNT || t >= SHOW_GO ? 0 : 3 - min(2, (t - SHOW_COUNT) / SHOW_STEP);
		if (d != showDigit || t == 0)
		{
			showDigit = d;
			SetScreen(k, d);
			// heard in the box too, through the glass
			if (d && mo) mo.A_StartSound("switches/exitbutn", CHAN_AUTO, 0, phase == REPLAY ? 0.5 : 1.0);
		}
	}

	// --- the open fight ---------------------------------------------------------
	// A fight whose box is open from the start (MAP31's second and third
	// halls). A trip begins the fight again, and it is played as it went the
	// last time: the hall is cleared, the show runs, and
	//  * every earlier go of the player is there as an AjarGhost that walks
	//    where they walked and fires what they fired, really;
	//  * every monster of the last go is there again, a real monster ON THE
	//    DEMO (AjarRail): put each tic where it was then, looking as it did,
	//    dying (and being raised) when it did; what it shot then flies again,
	//    really. Flames, puffs and blood of then are shown (AjarEcho).
	// The box's door is open at once, and the player steps in when they
	// choose. Nothing of the demo knows them: a monster stays on the demo until
	//  * the player hurts it: it wakes (only the player can hurt it), real
	//    from where it stands, with the health it had, and after the player;
	//  * the player walks into it: it wakes;
	//  * the demo is over, at the tic the last go ended: all wake.
	// A monster on the demo is not solid (it walks through what stands in its
	// way), so it wakes once it stands free; after a second, anyway.
	// A wave that came in the last go comes when it came then; one that did
	// not comes by the usual rule (few enough left).
	// Each go is recorded whole, demo monsters and all, and is the next
	// go's demo. So the past is changed, from the moment the player steps in.
	const GHOST_RUN = 16;       // an earlier self's speed on its way out
	Array<int> openFights;
	bool open;                  // the fight that is on is one
	int ot;                     // its tic, from the start of this go
	Array<AjarTake> takes;      // every go at it, the last being this one
	Array<AjarGhost> ghosts;    // ghosts[i]: of takes[i], while it lasts
	Array<Actor> shots;         // the player's missiles that are already written down
	int hadClip, hadShell;
	const RAIL_HEALTH = 1000000;
	const WAKE_WAIT = 35;
	AjarDemo demo, rec;         // the last go, being played; this go, being recorded
	Array<Actor> mshots;        // the monsters' missiles that are already written down
	Array<Actor> bornA;         // what came by a cue in this go,
	Array<AjarCue> bornC;       // and the cue

	bool Demoing() { return demo && ot < demo.len; }
	bool OnDemo(Actor a) { return a.FindInventory("AjarRail") != null; }

	AjarRole RoleOf(Actor a)
	{
		for (int i = 0; i < rec.roles.Size(); i++) if (rec.roles[i].src == a) return rec.roles[i];
		return null;
	}

	void RecordDemo()
	{
		for (int i = 0; i < rec.roles.Size(); i++) rec.roles[i].seen = false;
		for (int i = mshots.Size() - 1; i >= 0; i--) if (!mshots[i]) mshots.Delete(i);
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster && !(a.bMissile && a.target && a.target.bIsMonster)) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight || b != 0) continue;
			if (a.bMissile)
			{
				if (mshots.Find(a) < mshots.Size()) continue;
				mshots.Push(a);
				rec.evTic.Push(ot); rec.evCls.Push(a.GetClass()); rec.evBy.Push(RoleOf(a.target));
				rec.ex.Push(a.pos.x); rec.ey.Push(a.pos.y); rec.ez.Push(a.pos.z);
				rec.evx.Push(a.vel.x); rec.evy.Push(a.vel.y); rec.evz.Push(a.vel.z);
				continue;
			}
			AjarRole r = RoleOf(a);
			if (!r)
			{
				r = new("AjarRole");
				r.cls = a.GetClass();
				r.born = ot;
				r.src = a;
				int c = bornA.Find(a);
				if (c < bornA.Size()) r.cue = bornC[c];
				else if (a is "LostSoul")
				{
					// whose it is: the pain elemental beside it
					double best = 160;
					for (int i = 0; i < rec.roles.Size(); i++)
					{
						Actor m = rec.roles[i].src;
						if (!m || !(m is "PainElemental") || m.Distance2D(a) >= best) continue;
						best = m.Distance2D(a);
						r.maker = rec.roles[i];
					}
				}
				rec.roles.Push(r);
			}
			r.seen = true;
			let rail = AjarRail(a.FindInventory("AjarRail"));
			int n = r.x.Size();
			if (n)
			{
				// a body lying still: nothing to write
				if (a.health <= 0 && a.tics == -1 && r.hp[n - 1] <= 0 && r.sf[n - 1] >= 0 && r.x[n - 1] == a.pos.x && r.y[n - 1] == a.pos.y
					&& r.z[n - 1] == a.pos.z && (r.sf[n - 1] >> 8) == int(a.sprite) && (r.sf[n - 1] & 127) == (a.frame & 127)) { r.lag++; continue; }
				for (; r.lag > 0; r.lag--)
				{
					r.x.Push(r.x[n - 1]); r.y.Push(r.y[n - 1]); r.z.Push(r.z[n - 1]); r.ang.Push(r.ang[n - 1]);
					r.sf.Push(r.sf[n - 1]); r.hp.Push(r.hp[n - 1]);
				}
			}
			r.x.Push(a.pos.x); r.y.Push(a.pos.y); r.z.Push(a.pos.z); r.ang.Push(a.angle);
			r.sf.Push((int(a.sprite) << 8) | (a.frame & 127) | ((a.bBright || (!rail && a.CurState && a.CurState.bFullbright)) ? 128 : 0));
			r.hp.Push(rail ? rail.hp : max(0, a.health));
		}
		for (int i = 0; i < rec.roles.Size(); i++)
		{
			AjarRole r = rec.roles[i];
			if (r.seen || !r.src) continue;      // (gone for good: its record ends here)
			r.x.Push(0); r.y.Push(0); r.z.Push(0); r.ang.Push(0); r.sf.Push(-1); r.hp.Push(1);
		}
	}

	// What is seen in the hall besides: things of no substance. A puppet that
	// shows one of the last go is written down as what it shows.
	void RecordFx(AjarTrack tr)
	{
		tr.first.Push(tr.slot.Size());
		for (int i = 0; i < tr.live.Size(); i++) tr.liveSeen[i] = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.bInvisible) continue;
			class<Actor> cls = a.GetClass();
			if (a is "AjarEcho")
			{
				int pi = puppets.Find(AjarEcho(a));
				if (pi == puppets.Size()) continue;
				cls = slotCls[puppetSlot[pi]];
			}
			else if (!a.bNoBlockmap || a.bIsMonster || a.bMissile || a.player || a is "AjarZone" || a is "AjarCue" || a is "AjarCam"
				|| a is "Inventory" || GetDefaultByType(cls).bMissile) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight || b != 0) continue;
			int f = (int(a.sprite) << 8) | (a.frame & 127) | ((a.bBright || (a.CurState && a.CurState.bFullbright)) ? 128 : 0);
			int i = tr.live.Find(a);
			if (i == tr.live.Size())
			{
				slotCls.Push(cls);
				tr.live.Push(a); tr.liveSlot.Push(slotCls.Size() - 1); tr.liveSf.Push(-1); tr.liveSeen.Push(1);
				tr.lx.Push(0); tr.ly.Push(0); tr.lz.Push(0); tr.la.Push(0);
			}
			tr.liveSeen[i] = 1;
			if (tr.liveSf[i] == f && tr.lx[i] == a.pos.x && tr.ly[i] == a.pos.y && tr.lz[i] == a.pos.z && tr.la[i] == a.angle) continue;
			tr.liveSf[i] = f; tr.lx[i] = a.pos.x; tr.ly[i] = a.pos.y; tr.lz[i] = a.pos.z; tr.la[i] = a.angle;
			tr.Put(tr.liveSlot[i], f, a.pos, a.angle);
		}
		for (int i = tr.live.Size() - 1; i >= 0; i--)
		{
			if (tr.liveSeen[i]) continue;
			tr.Put(tr.liveSlot[i], -1, (0, 0, 0), 0);
			tr.live.Delete(i); tr.liveSlot.Delete(i); tr.liveSf.Delete(i); tr.liveSeen.Delete(i);
			tr.lx.Delete(i); tr.ly.Delete(i); tr.lz.Delete(i); tr.la.Delete(i);
		}
	}

	// This go is over: it is the next one's demo.
	void EndGo()
	{
		if (!rec) return;
		rec.len = ot;
		demo = rec;
		rec = null;
	}

	// The monster is real again, where it stands, if it stands free.
	bool Wake(AjarRole r, AjarRail rail, Actor mo)
	{
		Actor a = r.actor;
		let d = GetDefaultByType(a.GetClass());
		a.bSolid = d.bSolid;
		if (!a.TestMobjLocation())
		{
			// Something stands in it. It waits a second for that to move on;
			// then it steps aside, or wakes where it is (it must not be left
			// for good where it cannot be hurt).
			if (++r.waited < WAKE_WAIT) { a.bSolid = false; return false; }
			Vector3 was = a.pos;
			bool ok = false;
			for (int i = 0; i < 16 && !ok; i++)
			{
				Vector2 p = was.xy + Actor.AngleToVector(i * 45, (a.radius + 8) * (1 + i / 8));
				if (!level.IsPointInLevel((p, was.z))) continue;
				a.SetOrigin((p, was.z), false);
				ok = a.TestMobjLocation();
			}
			if (!ok) a.SetOrigin(was, false);
		}
		int hp = rail.hp - rail.dmg;
		a.RemoveInventory(rail);
		rail.Destroy();
		r.mode = 2;
		a.bBright = d.bBright;
		a.health = max(1, hp);
		a.target = mo;
		a.SetState(a.SeeState ? a.SeeState : a.SpawnState);
		if (hp <= 0) a.DamageMobj(mo, mo, RAIL_HEALTH, 'None');
		return true;
	}

	void Release(AjarRole r, AjarRail rail)
	{
		if (rail) { r.actor.RemoveInventory(rail); rail.Destroy(); }
		r.mode = 2;
	}

	// The state of its death that has the picture a body shows (its state has
	// not run on the demo, only its picture was set), or none.
	State PictureState(Actor a)
	{
		static const statelabel from[] = { "Death", "XDeath" };
		for (int j = -1; j < 2; j++)
		{
			State st = j < 0 ? a.CurState : a.FindState(from[j]);
			for (int n = 0; st && n < 60; n++)
			{
				if (st.sprite == a.sprite && st.Frame == (a.frame & 127)) return st;
				if (st.tics == -1) break;
				st = st.NextState;
			}
		}
		return null;
	}

	// A body the demo has let go of. The go that is played may have ended
	// while it was still falling: it falls on from the picture it shows.
	void FallOn(Actor a)
	{
		State st = PictureState(a);
		if (st) a.SetState(st, true);
	}

	// The monster on the demo is as its record says at tic i of it. `quiet`:
	// time was wound, and a death that is in the past is not heard.
	void Pose(AjarRole r, Actor a, AjarRail rail, int i, bool quiet)
	{
		int f = r.sf[i];
		if (f < 0)      // it was out of the hall then
		{
			if (!r.hidden) { r.hidden = true; a.bInvisible = true; a.bShootable = false; }
			return;
		}
		if (r.hidden) { r.hidden = false; a.bInvisible = false; a.bShootable = !r.dead; }
		int hp = r.hp[i];
		if (hp <= 0 && !r.dead)
		{
			r.dead = true;
			a.health = 0;
			a.Die(null, null);
			a.A_NoBlocking();
			if (!quiet) a.A_StartSound(a.DeathSound, CHAN_VOICE);
		}
		else if (hp > 0 && r.dead)
		{
			r.dead = false;
			a.Revive();
			a.bSolid = false;
		}
		rail.hp = r.dead ? 0 : hp;
		if (!r.dead) a.health = RAIL_HEALTH;
		a.SetOrigin((r.x[i], r.y[i], r.z[i]), true);
		a.angle = r.ang[i];
		a.sprite = f >> 8;
		a.frame = f & 127;
		a.bBright = (f & 128) != 0;
		a.tics = -1;
	}

	void PlayDemo(Actor mo)
	{
		if (!demo) return;
		bool ended = ot >= demo.len;
		if (demo.fx)
		{
			if (ot < demo.fx.first.Size()) PlayBack(demo.fx, ot);
			else if (ot == demo.fx.first.Size()) DropPuppets(-1);
		}
		for (int ri = 0; ri < demo.roles.Size(); ri++)
		{
			AjarRole r = demo.roles[ri];
			if (r.mode == 2) continue;
			int i = ot - r.born;
			if (r.mode == 0)
			{
				if (i != 0 && !(wound && i > 0)) { if (ended) r.mode = 2; continue; }
				int n0 = r.x.Size(), j = 0;
				if (i > 0)
				{
					// time was wound into the middle of its record: it is there as it was then
					if (!n0 || r.sf[0] < 0) { r.mode = 2; continue; }
					j = i;
					if (i >= n0)
					{
						// its record is over: a body that lay still from then on, or it was gone
						if (r.lag <= 0 || (i >= n0 + r.lag && r.born + n0 + r.lag < demo.len)) { r.mode = 2; continue; }
						j = n0 - 1;
					}
					while (j > 0 && r.sf[j] < 0) j--;       // out of the hall then: where it was last seen
				}
				// not if its cue has brought it already, or its pain elemental is awake
				else if ((r.cue && r.cue.special1) || (r.maker && r.maker.mode != 1) || r.sf[0] < 0) { r.mode = 2; continue; }
				Actor n = Actor.Spawn(r.cls, (r.x[j], r.y[j], r.z[j]));
				if (!n) { r.mode = 2; continue; }
				n.GiveInventoryType("AjarRail");
				n.bSolid = false;
				if (r.cue)
				{
					r.cue.special1 = 1;
					bornA.Push(n); bornC.Push(r.cue);
					if (i == 0)
					{
						Actor.Spawn("TeleportFog", n.pos, ALLOW_REPLACE);
						n.A_StartSound(n.SeeSound, CHAN_VOICE);
					}
				}
				r.actor = n;
				r.mode = 1;
				r.dead = r.hidden = false;
				r.wakeDue = false;
				if (i > 0 && r.twin) r.twin.src = n;        // its record goes on from here
				if (i > 0)
				{
					// as it was when last seen (dead, if it was: one that is out of the hall now stays so)
					Pose(r, n, AjarRail(n.FindInventory("AjarRail")), j, true);
					n.vel = (0, 0, 0);
					n.target = null;
					n.tics = -1;
					if (i >= n0) continue;
				}
			}
			Actor a = r.actor;
			let rail = a ? AjarRail(a.FindInventory("AjarRail")) : null;
			if (!rail) { r.mode = 2; continue; }
			// a body that something has really raised is real
			if (r.dead && a.health > 0) { a.bSolid = GetDefaultByType(a.GetClass()).bSolid; Release(r, rail); continue; }
			if (rail.hit) r.wakeDue = true;
			// the player walks into it: it wakes (once they are out of it)
			if (!r.dead && !r.hidden && !r.wakeDue && at == 0 && a.Distance2D(mo) < a.radius + mo.radius
				&& mo.pos.z < a.pos.z + a.height && a.pos.z < mo.pos.z + mo.height) r.wakeDue = true;
			bool has = i < r.x.Size();
			if (!has)
			{
				// a body that lay still from then on. (Not what was gone before the
				// go ended, a lost soul that burst: its last picture hung in the air.)
				if (r.lag > 0 && !ended && (i < r.x.Size() + r.lag || r.born + r.x.Size() + r.lag >= demo.len)) continue;
				if (r.born + r.x.Size() + r.lag < demo.len)     // it was gone then (a lost soul that burst)
				{
					if (!r.dead) a.ClearCounters();
					a.Destroy();
					r.mode = 2;
					continue;
				}
				if (r.dead) { Release(r, rail); FallOn(a); continue; }       // the demo is over: a body
				if (r.hidden) { r.hidden = false; a.bInvisible = false; a.bShootable = true; }
				r.wakeDue = true;
			}
			if (r.wakeDue && !r.dead && !r.hidden && Wake(r, rail, mo)) continue;
			a.vel = (0, 0, 0);
			a.target = null;
			a.tics = -1;
			if (!has) continue;
			Pose(r, a, rail, i, wound);
		}
		wound = false;
		// what they shot then flies again
		for (; demo.next < demo.evTic.Size() && demo.evTic[demo.next] <= ot; demo.next++)
		{
			int e = demo.next;
			AjarRole by = demo.evBy[e];
			if (!by || by.mode != 1 || by.dead || by.hidden || !by.actor || !demo.evCls[e]) continue;
			Actor m = Actor.Spawn(demo.evCls[e], (demo.ex[e], demo.ey[e], demo.ez[e]));
			if (!m) continue;
			m.target = by.actor;
			m.vel = (demo.evx[e], demo.evy[e], demo.evz[e]);
			m.angle = VectorAngle(m.vel.x, m.vel.y);
			m.A_StartSound(m.SeeSound, CHAN_VOICE);
		}
	}

	void RecordTake(PlayerPawn mo)
	{
		AjarTake t = takes[takes.Size() - 1];
		t.x.Push(mo.pos.x); t.y.Push(mo.pos.y); t.z.Push(mo.pos.z); t.ang.Push(mo.angle); t.pit.Push(mo.pitch);
		t.sf.Push((int(mo.sprite) << 8) | (mo.frame & 127));
		for (Inventory it = mo.Inv; it; it = it.Inv)
		{
			if (!(it is "Ammo") && !(it is "BasicArmor")) continue;
			int ki = t.kinds.Find(it.GetClass());
			if (ki == t.kinds.Size()) { t.kinds.Push(it.GetClass()); t.kindAmt.Push(-1); }
			if (t.kindAmt[ki] == it.Amount) continue;
			t.kindAmt[ki] = it.Amount;
			let arm = BasicArmor(it);
			t.carTic.Push(t.x.Size() - 1); t.carKind.Push(ki); t.carAmt.Push(it.Amount); t.carPct.Push(arm ? arm.SavePercent : 0);
		}
		int clip = mo.CountInv("Clip"), shell = mo.CountInv("Shell");
		for (int i = clip; i < hadClip; i++) Fired(t, 1, null, mo.pos, (0, 0, 0));
		if (shell < hadShell) Fired(t, hadShell - shell >= 2 ? 3 : 2, null, mo.pos, (0, 0, 0));
		hadClip = clip; hadShell = shell;
		for (int i = shots.Size() - 1; i >= 0; i--) if (!shots[i]) shots.Delete(i);
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bMissile || a.target != mo || shots.Find(a) < shots.Size()) continue;
			shots.Push(a);
			Fired(t, 0, a.GetClass(), a.pos, a.vel);
		}
	}

	void Fired(AjarTake t, int kind, class<Actor> cls, Vector3 p, Vector3 v)
	{
		t.evTic.Push(t.x.Size() - 1); t.evKind.Push(kind); t.evCls.Push(cls);
		t.ex.Push(p.x); t.ey.Push(p.y); t.ez.Push(p.z); t.evx.Push(v.x); t.evy.Push(v.y); t.evz.Push(v.z);
	}

	void DropGhosts()
	{
		for (int i = 0; i < ghosts.Size(); i++) if (ghosts[i]) ghosts[i].Destroy();
		ghosts.Clear();
	}

	void PlayGhosts(Actor mo)
	{
		for (int i = 0; i < takes.Size() - 1; i++)
		{
			AjarTake t = takes[i];
			while (ghosts.Size() <= i) ghosts.Push(null);
			if (ot >= t.x.Size())
			{
				// Its time is up, whatever has become of the fight: it is gone, as
				// the player went then. If they were killed then, and what killed
				// them is dead this time, it is taken out all the same (to its
				// box, as it were): there is never more than one of the player
				// left in a fight.
				AjarGhost e = ghosts[i];
				if (!e) continue;
				Line l = t.died ? Doors().FindLine(t.door) : null;
				Vector2 to = l ? (l.v1.p + l.v2.p) / 2 - e.pos.xy : (0, 0);
				if (to.Length() < GHOST_RUN) { e.Destroy(); continue; }
				// it runs to that door, straight, and goes in
				Vector2 p = e.pos.xy + to.Unit() * GHOST_RUN;
				Sector sec = level.PointInSector(p);
				double z = sec.floorplane.ZAtPoint(p);
				if (z >= sec.ceilingplane.ZAtPoint(p)) z = e.pos.z;      // through a pillar, as it must
				e.SetOrigin((p, z), true);
				e.angle = VectorAngle(to.x, to.y);
				e.sprite = Actor.GetSpriteIndex("PLAY");
				e.frame = (ot / 4) % 4;
				continue;
			}
			Vector3 p = (t.x[ot], t.y[ot], t.z[ot]);
			AjarGhost g = ghosts[i];
			if (!g)
			{
				g = AjarGhost(Actor.Spawn("AjarGhost", p));
				g.translation = mo.translation;
				ghosts[i] = g;
			}
			g.SetOrigin(p, true);
			g.angle = t.ang[ot];
			g.pitch = t.pit[ot];
			g.sprite = t.sf[ot] >> 8;
			g.frame = t.sf[ot] & 127;
			for (; t.next < t.evTic.Size() && t.evTic[t.next] <= ot; t.next++)
			{
				int e = t.next, kind = t.evKind[e];
				if (kind == 0)
				{
					if (!t.evCls[e]) continue;
					Actor m = Actor.Spawn(t.evCls[e], (t.ex[e], t.ey[e], t.ez[e]));
					if (!m) continue;
					m.target = g;
					m.vel = (t.evx[e], t.evy[e], t.evz[e]);
					m.angle = VectorAngle(m.vel.x, m.vel.y);
					m.A_StartSound(m.SeeSound, CHAN_VOICE);
					continue;
				}
				int n = kind == 1 ? 1 : kind == 2 ? 7 : 20;
				double sh = kind == 1 ? 2.8 : kind == 2 ? 5.6 : 11.2, sv = kind == 3 ? 7.1 : 0;
				for (int j = 0; j < n; j++)
					g.LineAttack(g.angle + frandom[AjarGhost](-sh, sh), 8192, g.pitch + frandom[AjarGhost](-sv, sv),
						5 * random[AjarGhost](1, 3), 'Hitscan', "BulletPuff");
				g.A_StartSound(kind == 1 ? "weapons/pistol" : kind == 2 ? "weapons/shotgf" : "weapons/sshotf", CHAN_WEAPON);
			}
		}
	}

	// The hall as it was before the fight: nothing in it but what lay there.
	void ClearHall()
	{
		Array<Actor> gone;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a is "AjarGhost" || a.player) continue;
			let inv = Inventory(a);
			if (!(a.bIsMonster || a.bMissile || a.bCorpse || (inv && !inv.owner && inv.bDropped))) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			// (an open fight's monster that is in a box goes too: it comes again)
			if (k == fight && (b == 0 || (open && b > 0 && a.bIsMonster))) gone.Push(a);
		}
		for (int i = 0; i < gone.Size(); i++)
		{
			if (gone[i].bIsMonster && gone[i].health > 0) gone[i].ClearCounters();
			gone[i].Destroy();
		}
		let ci = ThinkerIterator.Create("AjarCue");
		AjarCue c;
		while (c = AjarCue(ci.Next())) if (c.args[0] == fight) c.special1 = 0;
		DropGhosts();
		for (int i = 0; i < takes.Size(); i++) takes[i].next = 0;
		shots.Clear();
		DropPuppets(-1);
		if (demo)
		{
			demo.next = 0;
			for (int i = 0; i < demo.roles.Size(); i++)
			{
				AjarRole r = demo.roles[i];
				r.actor = null; r.src = null; r.mode = 0; r.waited = 0;
				r.dead = r.wakeDue = r.hidden = false;
			}
		}
	}

	void NewTake(Actor mo)
	{
		takes.Push(new("AjarTake"));
		ot = 0;
		hadClip = mo.CountInv("Clip"); hadShell = mo.CountInv("Shell");
		rec = new("AjarDemo");
		rec.fx = new("AjarTrack");
		rec.fx.fx = true;
		mshots.Clear(); bornA.Clear(); bornC.Clear();

	}

	// The player has gone out of an open fight (or been killed in it): it
	// begins again, and they are in the next box with its door open.
	void Retake(Actor mo)
	{
		let h = Doors();
		double best = 1e9;
		for (int j = 1; h.FindLine(HallLine(fight, j)); j++)
		{
			Line l = h.FindLine(HallLine(fight, j));
			double d = (playerWas.xy - (l.v1.p + l.v2.p) / 2).Length();
			if (d < best) { best = d; used = HallLine(fight, j); }
		}
		takes[takes.Size() - 1].died = rescued;
		takes[takes.Size() - 1].door = used;
		trips++;
		at = trips;
		StepClear(mo, BoxLine(fight, trips));
		EndGo();
		ClearHall();
		NewTake(mo);
		HallDoors(0);
		h.Link(BoxLine(fight, at), used, TIME_TEX);
		h.Link(used, BoxLine(fight, at), TIME_TEX);
		mo.A_SetBlend(rescued ? "ff2010" : "white", 1.0, 40);
		if (!rescued) mo.A_StartSound("misc/teleport", CHAN_AUTO);
		string last = trips == BoxCount(fight) ? "\nThe last box: after this the doors stay shut, and death is death." : "";
		Say((rescued ? "You were killed. " : "") .. "It is before the fight, and it plays as it went.\nThis door is open: step in when you choose." .. last);
		rescued = false;
	}

	// --- winding ---------------------------------------------------------------------
	// A plate on the wall (AjarWind) winds a fight half a minute back or on.
	// Each winding costs 10 health and 5 armour, and is not to be had with 10
	// health or less. On, it goes no further than two seconds before the end
	// of what there is to play or watch.
	//  * An open fight that is being played: in its boxes, and in its hall
	//    beside the way in (for when the player comes back to it on foot, from
	//    a box left over from an earlier fight). The go begins over, at that
	//    moment of the last one: the hall is cleared and everything in it is
	//    as it was then; this go's record up to then is the last go's, with
	//    the player standing where they stand. From the hall it winds only
	//    while the fight is still as it went (nothing is awake); from a box,
	//    always.
	//  * A fight that is being watched from a box (MAP32): from that box. What
	//    is seen through the glass and the doors are as they were at that
	//    moment of the fight (WindWatched); the player is not wound, and what
	//    they have done in this trip stays done. The real fight stands still
	//    as before, and the box's door still opens when the fight is where it
	//    was left.
	const WIND_TICS = 30 * 35;
	const WIND_HEALTH = 10;
	const WIND_ARMOUR = 5;
	bool wound;                 // time was wound: PlayDemo brings the monsters in as they were at this tic

	bool Awake()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || OnDemo(a)) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k == fight && b == 0) return true;
		}
		return false;
	}

	void Wind(PlayerPawn mo, int dir)
	{
		int k, b;
		[k, b] = Where(mo.pos.xy);
		if (phase == REPLAY && main && at > 0 && k == fight && b == at) { WindWatch(mo, dir); return; }
		if (!open || phase != LIVE || k != fight) { Say("Nothing is playing."); return; }
		if (!demo) { Say("This is the fight's first time:\nthere is nothing to wind yet."); return; }
		if (at == 0 && (!Demoing() || Awake())) { Say("The fight is yours now.\nIt winds from a box."); return; }
		int now = min(ot, demo.len);
		int to = clamp(now + dir * WIND_TICS, 0, max(0, demo.len - 70));
		if (dir > 0 && to <= now) { Say("It ends here: there is no more of it to wind on to."); return; }
		if (!WindPay(mo)) return;
		WindTo(mo, to);
		WindFelt(mo);
	}

	// it costs (Vadim): 10 health, and 5 armour of what there is
	bool WindPay(PlayerPawn mo)
	{
		if (mo.health <= WIND_HEALTH) { Say("Winding takes it out of you:\nyou have not the health for it."); return false; }
		mo.health = mo.player.health = mo.health - WIND_HEALTH;
		let arm = mo.FindInventory("BasicArmor");
		if (arm) arm.Amount = max(0, arm.Amount - WIND_ARMOUR);
		return true;
	}

	void WindFelt(PlayerPawn mo)
	{
		mo.A_SetBlend("white", 0.5, 14);
		mo.A_StartSound("switches/normbutn", CHAN_AUTO);
	}

	// A fight that is watched, from its box.
	void WindWatch(PlayerPawn mo, int dir)
	{
		int to = clamp(rt + dir * WIND_TICS, 0, max(0, main.first.Size() - 70));
		if (dir > 0 && to <= rt) { Say("It ends here: there is no more of it to wind on to."); return; }
		if (dir < 0 && rt < 70) {      // the first two seconds: nothing worth the price
		 Say("It begins here: there is no more of it to wind back to."); return; }
		if (!WindPay(mo)) return;
		WindWatched(mo, to);
		WindFelt(mo);
	}

	// The fight that is watched goes to tic `to` at once: the next tic shown
	// is `to`, as if it had played (on) or played again from its start
	// (back) up to there. Only what is shown and the doors move: the hall's
	// real things stand still, and what has come out after the player into
	// the box, or is still to come, is where it is.
	void WindWatched(PlayerPawn mo, int to)
	{
		AjarTrack self = boxes[boxes.Size() - 1];
		if (to < rt)
		{
			DropPuppets(-1);
			PuppetsAt(0, to);
			// what the player did in this box after then was not done: their
			// track is cut there, and the next Record writes down afresh
			// whatever is in the box (and as gone what was there then and is not now)
			int r = to < self.first.Size() ? self.first[to] : self.slot.Size();
			Array<int> seen;
			for (int i = 0; i < slotCls.Size(); i++) seen.Push(0);
			for (int i = 0; i < r; i++) seen[self.slot[i]] = self.sf[i] >= 0 ? 1 : 0;
			self.first.Resize(to);
			self.slot.Resize(r); self.sf.Resize(r); self.x.Resize(r); self.y.Resize(r); self.z.Resize(r); self.ang.Resize(r);
			for (int i = 0; i < self.live.Size(); i++) { self.liveSf[i] = -2; seen[self.liveSlot[i]] = 0; }
			for (int s = 0; s < seen.Size(); s++)
			{
				if (!seen[s]) continue;
				self.live.Push(null); self.liveSlot.Push(s); self.liveSf.Push(-2); self.liveSeen.Push(0);
				self.lx.Push(0); self.ly.Push(0); self.lz.Push(0); self.la.Push(0);
			}
		}
		else
		{
			PuppetsAt(rt, to);
			// nothing in the box moved meanwhile
			while (self.first.Size() < to) self.first.Push(self.slot.Size());
		}
		DoorWind(to);
		// the hall's lights and screen: Show changes nothing after the count
		Show(fight, min(to, SHOW_GO + 8), null);
		Hold();
		rt = to;
	}

	// What tics from..to - 1 of the fight that is watched show: each slot as
	// its last record says, and the earlier selves' tracks that have ended
	// gone (as WorldTick plays them, tic by tic).
	void PuppetsAt(int from, int to)
	{
		Array<int> last;
		for (int n = -1; n < boxes.Size() - 1; n++)
		{
			AjarTrack tr = n < 0 ? main : boxes[n];
			int s = tr.first.Size();
			if (n >= 0 && s < to) { if (s >= from) DropPuppets(n + 1); continue; }
			int a = from < s ? tr.first[from] : tr.slot.Size();
			int b = to < s ? tr.first[to] : tr.slot.Size();
			last.Clear();
			for (int i = 0; i < slotCls.Size(); i++) last.Push(-1);
			for (int r = a; r < b; r++) last[tr.slot[r]] = r;
			for (int i = 0; i < last.Size(); i++) if (last[i] >= 0) Puppet(tr, last[i]);
		}
	}

	void WindTo(PlayerPawn mo, int to)
	{
		ClearHall();
		recent.Clear();
		takes.Pop();
		NewTake(mo);
		// this go so far: the player has stood here
		AjarTake t = takes[takes.Size() - 1];
		int sf = (int(mo.sprite) << 8) | (mo.frame & 127);
		for (int i = 0; i < to; i++)
		{
			t.x.Push(mo.pos.x); t.y.Push(mo.pos.y); t.z.Push(mo.pos.z); t.ang.Push(mo.angle); t.pit.Push(mo.pitch); t.sf.Push(sf);
		}
		// what the earlier selves fired before then is not fired again
		for (int i = 0; i < takes.Size() - 1; i++)
			for (takes[i].next = 0; takes[i].next < takes[i].evTic.Size() && takes[i].evTic[takes[i].next] < to; takes[i].next++) {}
		// the monsters' records up to then
		for (int i = 0; i < demo.roles.Size(); i++) demo.roles[i].twin = null;
		for (int i = 0; i < demo.roles.Size(); i++)
		{
			AjarRole r = demo.roles[i];
			if (r.born >= to) continue;
			let c = new("AjarRole");
			c.cls = r.cls; c.born = r.born; c.cue = r.cue;
			c.maker = r.maker ? r.maker.twin : null;
			int n = min(r.x.Size(), to - r.born);
			c.x.Copy(r.x); c.y.Copy(r.y); c.z.Copy(r.z); c.ang.Copy(r.ang); c.sf.Copy(r.sf); c.hp.Copy(r.hp);
			c.x.Resize(n); c.y.Resize(n); c.z.Resize(n); c.ang.Resize(n); c.sf.Resize(n); c.hp.Resize(n);
			c.lag = n == r.x.Size() ? min(r.lag, to - r.born - n) : 0;
			r.twin = c;
			rec.roles.Push(c);
		}
		// and what they shot
		int ne = 0;
		while (ne < demo.evTic.Size() && demo.evTic[ne] < to) ne++;
		rec.evTic.Copy(demo.evTic); rec.evCls.Copy(demo.evCls);
		rec.ex.Copy(demo.ex); rec.ey.Copy(demo.ey); rec.ez.Copy(demo.ez);
		rec.evx.Copy(demo.evx); rec.evy.Copy(demo.evy); rec.evz.Copy(demo.evz);
		rec.evTic.Resize(ne); rec.evCls.Resize(ne);
		rec.ex.Resize(ne); rec.ey.Resize(ne); rec.ez.Resize(ne);
		rec.evx.Resize(ne); rec.evy.Resize(ne); rec.evz.Resize(ne);
		for (int e = 0; e < ne; e++) rec.evBy.Push(demo.evBy[e] ? demo.evBy[e].twin : null);
		demo.next = ne;
		// what was seen besides: the track up to then; what it shows at that
		// moment is seen (and ends there in this go's track: RecordFx writes
		// it down again, as what is seen now)
		AjarTrack fx = demo.fx, nfx = rec.fx;
		int tf = fx ? min(to, fx.first.Size()) : 0;
		int nr = !fx ? 0 : tf < fx.first.Size() ? fx.first[tf] : fx.slot.Size();
		if (fx)
		{
			nfx.first.Copy(fx.first); nfx.first.Resize(tf);
			nfx.slot.Copy(fx.slot); nfx.sf.Copy(fx.sf); nfx.x.Copy(fx.x); nfx.y.Copy(fx.y); nfx.z.Copy(fx.z); nfx.ang.Copy(fx.ang);
			nfx.slot.Resize(nr); nfx.sf.Resize(nr); nfx.x.Resize(nr); nfx.y.Resize(nr); nfx.z.Resize(nr); nfx.ang.Resize(nr);
			Array<int> last;
			for (int i = 0; i < slotCls.Size(); i++) last.Push(-1);
			for (int r = 0; r < nr; r++) last[fx.slot[r]] = fx.sf[r] < 0 ? -1 : r;
			for (int s = 0; s < last.Size(); s++)
			{
				if (last[s] < 0) continue;
				if (tf) nfx.Put(s, -1, (0, 0, 0), 0);
				if (to < fx.first.Size()) Puppet(fx, last[s]);
			}
		}
		while (nfx.first.Size() < to) nfx.first.Push(nfx.slot.Size());
		ot = to;
		wound = true;
	}

	// --- the reel -----------------------------------------------------------------
	// When every fight is won the last way out leads back to the first hall,
	// to a seat. The lights go down, a big screen comes down before the way
	// in, and on it is every time the player was killed in a hall: its last
	// two seconds, close, at a third of the speed, and their going to light. Then the
	// level ends. (USE: the next one.)
	// How: while a fight is lived the last REEL_LEN tics of its hall are kept
	// (stills: every thing's place and picture). A death keeps a copy. For
	// the reel each is played with puppets in the hall where it happened,
	// now empty, before a camera whose view is the screen's texture (AJREEL,
	// animdefs.txt). The player is unseen meanwhile, so that a clip of the
	// hall they sit in does not have them in it.
	const REEL_LEN = 70;
	const REEL_SLOW = 3;
	const REEL_FALL = 12;       // tics to a frame of the fall (7 frames)
	const REEL_TAG = 3070;
	Array<AjarStill> recent;
	Array<AjarClip> clips;
	int reel;                   // 0 not yet, 1 the screen comes down, 2 clips, 3 the end, 4 over
	int reelTic, reelClip;
	bool reelUse;
	AjarCam cam;
	AjarEcho fallen;
	string caption;

	void Snap(Actor mo)
	{
		let st = new("AjarStill");
		st.me = -1;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a is "AjarEcho" || a is "AjarZone" || a is "AjarCue" || a is "AjarCam" || a.bInvisible) continue;
			let inv = Inventory(a);
			if (inv && inv.owner) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight || b != 0) continue;
			if (a == mo) st.me = st.cls.Size();
			st.cls.Push(a.GetClass());
			st.x.Push(a.pos.x); st.y.Push(a.pos.y); st.z.Push(a.pos.z); st.ang.Push(a.angle);
			st.sf.Push((int(a.sprite) << 8) | (a.frame & 127) | ((a.bBright || (a.CurState && a.CurState.bFullbright)) ? 128 : 0));
		}
		recent.Push(st);
		if (recent.Size() > REEL_LEN) recent.Delete(0);
	}

	// If the player was never killed in a hall, the reel has the deaths of
	// the three biggest monsters instead (600 health and up: arch-viles,
	// mancubi, barons, cyberdemons), kept a little after each died so that
	// its fall is in it.
	const BIG = 600;
	const BIG_AFTER = 45;
	Array<AjarClip> kills, dueKills;
	Array<int> dueTic;
	// And after those, for every hall, the death of the monster killed last
	// in it (Vadim, 2026-11-19): each death in a lived fight is a candidate,
	// kept BIG_AFTER tics later unless another has died by then; a hall's
	// later one replaces its earlier one.
	Array<AjarClip> lastKills;
	AjarClip dueLast;
	int dueLastTic;

	override void WorldThingDied(WorldEvent e)
	{
		Actor t = e.thing;
		if (!t || !t.bIsMonster || phase != LIVE) return;
		int k, b;
		[k, b] = Where(t.pos.xy);
		if (k != fight || b != 0) return;
		let l = new("AjarClip");
		l.fight = fight;
		l.at = t.pos;
		l.ang = t.angle;
		l.big = max(1, t.SpawnHealth());
		l.what = t.GetTag();
		l.last = true;
		dueLast = l; dueLastTic = level.maptime + BIG_AFTER;
		if (t.SpawnHealth() < BIG) return;
		let c = new("AjarClip");
		c.fight = fight;
		c.at = t.pos;
		c.ang = t.angle;
		c.big = t.SpawnHealth();
		c.what = t.GetTag();
		dueKills.Push(c); dueTic.Push(level.maptime + BIG_AFTER);
	}

	void KeepKills()
	{
		if (dueLast && dueLastTic <= level.maptime)
		{
			if (recent.Size())
			{
				dueLast.stills.Copy(recent);
				for (int i = lastKills.Size() - 1; i >= 0; i--) if (lastKills[i].fight == dueLast.fight) lastKills.Delete(i);
				int at = 0;
				while (at < lastKills.Size() && lastKills[at].fight < dueLast.fight) at++;
				lastKills.Insert(at, dueLast);
			}
			dueLast = null;
		}
		while (dueTic.Size() && dueTic[0] <= level.maptime)
		{
			AjarClip c = dueKills[0];
			dueKills.Delete(0); dueTic.Delete(0);
			if (!recent.Size()) continue;
			c.stills.Copy(recent);
			kills.Push(c);
			if (kills.Size() <= 3) continue;
			int least = 0;
			for (int i = 1; i < kills.Size(); i++) if (kills[i].big < kills[least].big) least = i;
			kills.Delete(least);
		}
	}

	void KeepClip(Actor mo)
	{
		if (!recent.Size()) return;
		let c = new("AjarClip");
		c.fight = fight;
		c.at = mo.pos;
		c.ang = mo.angle;
		c.stills.Copy(recent);
		clips.Push(c);
		recent.Clear();
	}

	int Fights()
	{
		int n = 0;
		for (int i = 0; i < zf.Size(); i++) if (zf[i] > n) n = zf[i];
		return n;
	}

	void StartReel(PlayerPawn mo)
	{
		reel = 1;
		reelTic = 0;
		mo.player.cheats |= CF_TOTALLYFROZEN;
		mo.bInvisible = true;
		mo.vel = (0, 0, 0);
		mo.pitch = -8;
		// nothing lies between the seat and the screen (nor in a clip of this
		// hall): the bodies of its fight and what they dropped are unseen
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			let inv = Inventory(a);
			if (!(a.bCorpse || (a.bIsMonster && a.health <= 0) || (inv && !inv.owner))) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k == 1 && b == 0) a.bInvisible = true;
		}
		HouseLights(1, 0);
		level.ExecuteSpecial(40 /* Ceiling_LowerByValue */, null, null, false, REEL_TAG, 16, 224);
		cam = AjarCam(Actor.Spawn("AjarCam", mo.pos + (0, 0, 40)));
		cam.angle = mo.angle + 180;
		TexMan.SetCameraToTexture(cam, "AJREEL", 55);
		if (!clips.Size()) clips.Copy(kills);
		caption = clips.Size() ? "" : "Not once were you killed in a hall.";
		// the last scene of each hall: the monster killed last in it (not
		// twice, where that death is among the big ones already)
		for (int i = 0; i < lastKills.Size(); i++)
		{
			bool there = false;
			for (int j = 0; j < clips.Size(); j++) if (clips[j].big && clips[j].fight == lastKills[i].fight && clips[j].at == lastKills[i].at) there = true;
			if (!there) clips.Push(lastKills[i]);
		}
	}

	// The camera: near where they fell, on them, from where they can be seen.
	void Aim(AjarClip c)
	{
		static const int tryAt[] = { 0, 40, -40, 80, -80, 130, -130, 180 };
		let mark = Actor.Spawn("AjarCam", c.at + (0, 0, 32));
		for (int i = 0; i < 8; i++)
		{
			Vector2 p = c.at.xy + Actor.AngleToVector(c.ang + tryAt[i], c.big >= 300 ? 230 : 120);
			Sector sec = level.PointInSector(p);
			if (!level.IsPointInLevel((p, c.at.z + 44)) || sec.ceilingplane.ZAtPoint(p) - sec.floorplane.ZAtPoint(p) < 64) continue;
			cam.SetOrigin((p, max(c.at.z, sec.floorplane.ZAtPoint(p)) + 44), false);
			cam.angle = VectorAngle(c.at.x - p.x, c.at.y - p.y);
			cam.pitch = 6;
			if (cam.CheckSight(mark)) break;
		}
		mark.Destroy();
	}

	void Stage(AjarStill st, bool withMe)
	{
		int n = st.cls.Size();
		while (puppets.Size() < n)
		{
			puppets.Push(AjarEcho(Actor.Spawn("AjarEcho", (st.x[0], st.y[0], st.z[0]))));
			puppetSlot.Push(0); puppetTrack.Push(0);
		}
		for (int i = 0; i < puppets.Size(); i++)
		{
			AjarEcho e = puppets[i];
			if (!e) continue;
			if (i >= n || (i == st.me && !withMe)) { e.bInvisible = true; continue; }
			let d = GetDefaultByType(st.cls[i]);
			e.bInvisible = false;
			e.SetOrigin((st.x[i], st.y[i], st.z[i]), false);
			e.scale = d.scale;
			e.A_SetRenderStyle(d.alpha, d.GetRenderStyle());
			e.translation = d.translation;
			e.angle = st.ang[i];
			e.sprite = st.sf[i] >> 8;
			e.frame = st.sf[i] & 127;
			e.bBright = (st.sf[i] & 128) != 0;
		}
	}

	void ReelTick(PlayerPawn mo)
	{
		mo.vel = (0, 0, 0);
		bool use = (mo.player.original_cmd.buttons & BT_USE) != 0;
		bool skip = use && !reelUse;
		reelUse = use;
		int t = reelTic++;
		if (reel == 1)
		{
			if (t < 130) return;
			reel = clips.Size() ? 2 : 3;
			reelTic = 0; reelClip = 0;
			return;
		}
		if (reel == 2)
		{
			AjarClip c = clips[reelClip];
			int n = c.stills.Size(), shown = t / REEL_SLOW, fall = t - n * REEL_SLOW;
			if (t == 0)
			{
				Aim(c);
				caption = c.last ? String.Format("HALL %d   -   the last to fall: %s", c.fight, c.what) : c.big ? String.Format("HALL %d   -   %s", c.fight, c.what) : String.Format("HALL %d   -   %d of %d", c.fight, reelClip + 1, clips.Size());
			}
			if (shown < n) Stage(c.stills[shown], true);
			else if (c.big) fall += 7 * REEL_FALL;     // its fall is in the clip: only the pause
			else
			{
				// taken out: everything else as it was at the last, and the
				// player's shape gone to light, rising and fading
				AjarStill last = c.stills[n - 1];
				Stage(last, false);
				if (!fallen) fallen = AjarEcho(Actor.Spawn("AjarEcho", c.at));
				double gone = min(1., fall / (7. * REEL_FALL));
				fallen.SetOrigin(c.at + (0, 0, 24 * gone), false);
				fallen.angle = c.ang;
				fallen.sprite = last.me >= 0 ? last.sf[last.me] >> 8 : Actor.GetSpriteIndex("PLAY");
				fallen.frame = last.me >= 0 ? last.sf[last.me] & 127 : 0;
				fallen.bBright = true;
				fallen.A_SetRenderStyle(1 - gone, STYLE_Add);
				fallen.scale = (1 + 0.3 * gone, 1 + 0.3 * gone);
				fallen.bInvisible = false;
			}
			if (skip || fall > 7 * REEL_FALL + 35)
			{
				if (fallen) fallen.bInvisible = true;
				for (int i = 0; i < puppets.Size(); i++) if (puppets[i]) puppets[i].bInvisible = true;
				reelTic = 0;
				if (++reelClip >= clips.Size()) reel = 3;
			}
			return;
		}
		if (reel == 3)
		{
			if (t == 0)
			{
				if (clips.Size()) caption = "THE END";
				mo.A_SetBlend("black", 1.0, 200);
			}
			if (t < 105 && !skip) return;
			reel = 4;
			DropPuppets(-1);
			if (fallen) fallen.Destroy();
			if (cam) cam.Destroy();
			mo.player.cheats &= ~CF_TOTALLYFROZEN;
			mo.bInvisible = false;
			level.ExitLevel(0, false);
		}
	}

	// --- recording ------------------------------------------------------------
	// Is this thing part of what is recorded just now? `box` 0: the hall and
	// every box whose door has opened; else that box alone.
	bool Counts(Actor a, int box)
	{
		if (a is "AjarEcho" || a is "AjarZone" || a is "AjarCue" || a is "AjarDoor" || a.bInvisible) return false;      // a door: timedoor.zs
		let inv = Inventory(a);
		if (inv && inv.owner) return false;
		int k, b;
		[k, b] = Where(a.pos.xy);
		if (k != fight || b < 0) return false;
		if (box) return b == box;
		return b == 0 || b < trips || (b == trips && phase == LIVE);
	}

	void Record(AjarTrack tr)
	{
		tr.first.Push(tr.slot.Size());
		for (int i = 0; i < tr.live.Size(); i++) tr.liveSeen[i] = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!Counts(a, tr.box)) continue;
			int f = (int(a.sprite) << 8) | (a.frame & 127) | ((a.bBright || (a.CurState && a.CurState.bFullbright)) ? 128 : 0);
			int i = tr.live.Find(a);
			if (i == tr.live.Size())
			{
				slotCls.Push(a.GetClass());
				tr.live.Push(a); tr.liveSlot.Push(slotCls.Size() - 1); tr.liveSf.Push(-1); tr.liveSeen.Push(1);
				tr.lx.Push(0); tr.ly.Push(0); tr.lz.Push(0); tr.la.Push(0);
			}
			tr.liveSeen[i] = 1;
			if (tr.liveSf[i] == f && tr.lx[i] == a.pos.x && tr.ly[i] == a.pos.y && tr.lz[i] == a.pos.z && tr.la[i] == a.angle) continue;
			tr.liveSf[i] = f; tr.lx[i] = a.pos.x; tr.ly[i] = a.pos.y; tr.lz[i] = a.pos.z; tr.la[i] = a.angle;
			tr.Put(tr.liveSlot[i], f, a.pos, a.angle);
		}
		for (int i = tr.live.Size() - 1; i >= 0; i--)
		{
			if (tr.liveSeen[i]) continue;
			tr.Put(tr.liveSlot[i], -1, (0, 0, 0), 0);
			tr.live.Delete(i); tr.liveSlot.Delete(i); tr.liveSf.Delete(i); tr.liveSeen.Delete(i);
			tr.lx.Delete(i); tr.ly.Delete(i); tr.lz.Delete(i); tr.la.Delete(i);
		}
	}

	// --- playing back ---------------------------------------------------------
	void DropPuppet(int i)
	{
		if (puppets[i]) puppets[i].Destroy();
		puppets.Delete(i); puppetSlot.Delete(i); puppetTrack.Delete(i);
	}

	void DropPuppets(int track)     // -1: all
	{
		for (int i = puppets.Size() - 1; i >= 0; i--) if (track < 0 || puppetTrack[i] == track) DropPuppet(i);
	}

	void PlayBack(AjarTrack tr, int i)
	{
		int to = i + 1 < tr.first.Size() ? tr.first[i + 1] : tr.slot.Size();
		for (int r = tr.first[i]; r < to; r++) Puppet(tr, r);
	}

	// What record r of the track says is seen.
	void Puppet(AjarTrack tr, int r)
	{
		{
			int s = tr.slot[r];
			int k = puppetSlot.Find(s);
			if (tr.sf[r] < 0)
			{
				if (k < puppets.Size()) DropPuppet(k);
				return;
			}
			Vector3 p = (tr.x[r], tr.y[r], tr.z[r]);
			AjarEcho e;
			if (k < puppets.Size()) { e = puppets[k]; e.SetOrigin(p, true); }
			else
			{
				e = AjarEcho(Actor.Spawn("AjarEcho", p));
				let d = GetDefaultByType(slotCls[s]);
				e.scale = d.scale;
				e.A_SetRenderStyle(d.alpha, d.GetRenderStyle());
				e.translation = d.translation;
				puppets.Push(e); puppetSlot.Push(s); puppetTrack.Push(tr.box);
			}
			e.angle = tr.ang[r];
			e.sprite = tr.sf[r] >> 8;
			e.frame = tr.sf[r] & 127;
			e.bBright = (tr.sf[r] & 128) != 0;
		}
	}

	// --- standing still -------------------------------------------------------
	void Freeze(Actor mo)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a == mo || !Counts(a, 0) || pending.Find(a) < pending.Size()) continue;
			fz.Push(a); fzTarget.Push(a.target); fzTics.Push(a.tics); fzFlags.Push(a.bSkullFly ? 1 : 0);
			fzx.Push(a.pos.x); fzy.Push(a.pos.y); fzz.Push(a.pos.z);
			fzvx.Push(a.vel.x); fzvy.Push(a.vel.y); fzvz.Push(a.vel.z);
			a.tics = -1;
			a.bSkullFly = false;
			a.bInvisible = true;
		}
		Hold();
	}

	// A thing with no state to run still falls, floats and is pushed.
	void Hold()
	{
		for (int i = 0; i < fz.Size(); i++)
		{
			Actor a = fz[i];
			if (!a) continue;
			a.vel = (0, 0, 0);
			a.target = null;
			if (a.pos.x != fzx[i] || a.pos.y != fzy[i] || a.pos.z != fzz[i]) a.SetOrigin((fzx[i], fzy[i], fzz[i]), false);
		}
	}

	void Unfreeze()
	{
		Hold();
		for (int i = 0; i < fz.Size(); i++)
		{
			Actor a = fz[i];
			if (!a) continue;
			a.bInvisible = false;
			a.tics = fzTics[i];
			a.vel = (fzvx[i], fzvy[i], fzvz[i]);
			a.target = fzTarget[i];
			if (fzFlags[i] & 1) a.bSkullFly = true;
		}
		fz.Clear(); fzTarget.Clear(); fzTics.Clear(); fzFlags.Clear();
		fzx.Clear(); fzy.Clear(); fzz.Clear(); fzvx.Clear(); fzvy.Clear(); fzvz.Clear();
	}

	// --- the fight ------------------------------------------------------------
	void Begin(int k)
	{
		fight = k;
		recent.Clear();
		dueKills.Clear(); dueTic.Clear();
		open = openFights.Find(k) < openFights.Size();
		takes.Clear();
		DropGhosts();
		demo = null;
		slotCls.Clear();
		if (open) NewTake(players[consoleplayer].mo);
		trips = 0;
		at = 0;
		main = new("AjarTrack");
		boxes.Clear();
		phase = LIVE;
		DoorBegin();
		HallDoors(1);
		if (!(said & 1)) Say("A door with a clock on it leads out of the fight,\nand back into it where you left.");
		said |= 1;
	}

	// A monster that came into a box after the player, and is still alive
	// there when the player is back in the hall, is shut in where nothing can
	// reach it, and the fight could not be won. It comes out into the hall by
	// the time door farthest from the player (when there is room there).
	void BackToTheHall(Actor mo)
	{
		let h = Doors();
		Vector2 mid;
		double far = -1;
		for (int j = 1; h.FindLine(HallLine(fight, j)); j++)
		{
			Line l = h.FindLine(HallLine(fight, j));
			Vector2 c = (l.v1.p + l.v2.p) / 2;
			double d = (mo.pos.xy - c).Length();
			if (d > far) { far = d; mid = c; }
		}
		if (far < 0) return;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight || b <= 0) continue;
			Vector3 was = a.pos;
			bool ok = false;
			for (int i = 0; i < 24 && !ok; i++)
			{
				Vector2 p = mid + Actor.AngleToVector(i * 45, 64 + a.radius + 48 * (i / 8));
				[k, b] = Where(p);
				if (k != fight || b != 0 || !level.IsPointInLevel((p, 0))) continue;
				Sector sec = level.PointInSector(p);
				// in the hall itself, not a door's recess or the way in
				if (sec.ceilingplane.ZAtPoint(p) - sec.floorplane.ZAtPoint(p) < 160) continue;
				a.SetOrigin((p, sec.floorplane.ZAtPoint(p)), false);
				ok = a.TestMobjLocation();
			}
			if (!ok) { a.SetOrigin(was, false); continue; }
			a.vel = (0, 0, 0);
			a.target = mo;
			Actor.Spawn("TeleportFog", a.pos, ALLOW_REPLACE);
		}
	}

	// An open fight, and who its monsters are after. While the player is in
	// a box they are not in the fight yet: the monsters are after their
	// earlier selves (each after the nearest), not at the glass after them,
	// so that the player can wait and watch. When no earlier self is left,
	// or the player is in the hall, a monster that is after no one is after
	// the player; one that is on an earlier self stays on it until that self
	// is gone or something else hurts it.
	void Hunt(Actor mo)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight || b != 0 || OnDemo(a)) continue;
			if (a.target && (a.target != mo || at == 0)) continue;
			Actor to = null;
			if (at > 0)
				for (int i = 0; i < ghosts.Size(); i++)
					if (ghosts[i] && (!to || a.Distance2D(ghosts[i]) < a.Distance2D(to))) to = ghosts[i];
			if (!to) to = mo;
			if (a.target == to) continue;
			a.target = to;
			a.lastheard = null;
			if (a.InStateSequence(a.CurState, a.SpawnState) && a.SeeState) a.SetState(a.SeeState);
		}
	}

	int Left()      // monsters of this fight still alive, wherever in it they are
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k == fight && b >= 0) n++;
		}
		return n;
	}

	// Is this cue's monster still to come in the demo that is playing?
	bool WillCome(AjarCue c)
	{
		if (!open || !Demoing()) return false;
		for (int i = 0; i < demo.roles.Size(); i++) if (demo.roles[i].cue == c && demo.roles[i].mode == 0) return true;
		return false;
	}

	// The next wave, if it is due. Returns whether any is still to come.
	// A wave is due when no more than its number of monsters are left, or
	// when its time has come: WAVE_TICS after the first for the second, twice
	// that for the third, whoever has or has not been shot by then (Vadim,
	// 2026-11-19: the fights are for setting them on each other, and a wave
	// must not wait for the player's kills). `since` is the fight's tic less
	// the tic its first monsters came.
	const WAVE_TICS = 25 * 35;
	bool Cues(Actor mo, int left, int since)
	{
		int wave = 0;
		let it = ThinkerIterator.Create("AjarCue");
		AjarCue c;
		while (c = AjarCue(it.Next())) if (c.args[0] == fight && !c.special1 && (!wave || c.args[1] < wave)) wave = c.args[1];
		if (!wave) return false;
		it = ThinkerIterator.Create("AjarCue");
		while (c = AjarCue(it.Next()))
		{
			if (c.args[0] != fight || c.special1 || c.args[1] != wave) continue;
			if (left > c.args[2] && since < WAVE_TICS * (wave - 1)) continue;
			if (WillCome(c)) continue;      // as it came the last time, and when
			class<Actor> cls = AjarHandler.AmbushClass(c.args[3]);
			if (c.args[3] == 64) cls = "Archvile";
			if (c.args[3] == 16) cls = "Cyberdemon";
			if (!cls) { c.special1 = 1; continue; }
			Actor m = Actor.Spawn(cls, c.pos, ALLOW_REPLACE);
			if (!m) continue;
			// someone stands there: it comes when there is room (the wave is not over until it has)
			if (!m.TestMobjLocation()) { m.ClearCounters(); m.Destroy(); continue; }
			m.angle = c.angle;
			Actor.Spawn("TeleportFog", c.pos, ALLOW_REPLACE);
			m.target = mo;
			bornA.Push(m); bornC.Push(c);
			if (m.SeeState) m.SetState(m.SeeState);
			m.A_StartSound(m.SeeSound, CHAN_VOICE);
			c.special1 = 1;         // spent (not destroyed: an open fight begins again)
		}
		return true;
	}

	// Killed while a box is still unused, in the hall or in a box: the player
	// is not dead but in the next box, before the fight. From the hall it is
	// as if they had gone out at that moment by the nearest time door; from
	// a box, what they were watching is dropped and they watch again from
	// the start, to come back in by the door they first left by. While that
	// can happen the player cannot die (bBuddha: health stops at 1). With no
	// box left, death is death.
	const RESCUE_HEALTH = 50;
	const REWIND = 35;          // tics the clock takes to run back
	bool rescued;               // the trip that is on began with a death
	const STAND_TICS = 35;
	int stand;                  // tics the player still cannot walk, just killed into a box

	// Boxes that were not used in a fight that is won are kept (fight * 10 +
	// box). Killed in a later fight with none of its own boxes left, the
	// player is in the oldest of them: that fight is long over, so its door
	// is open at once onto its hall, and the way to the fight they fell in
	// is the way they came. That fight is cleared, and begins again when they
	// walk into its hall (an open fight with their earlier selves in it).
	// With no box of any kind left, the show is over: the level ends.
	Array<int> spare;
	int spareOut;               // the spare box the player is on the way out of
	bool comeBack;                // the fight begins again when the player comes back to its hall
	int over;                   // tics until the level ends, once nothing is left

	// Killed in an open fight's hall while an earlier self is still fighting:
	// the player goes on as that self, from where it stands (the one with the
	// most time left). No box is spent; the rest of what that self did is
	// dropped, so in a later go it is there only up to this moment. What that
	// self carried at this moment is the player's: of each kind of ammunition,
	// and of armour, they have its amount where it is more than their own
	// (never less: what a box gave since is not lost).
	void Carry(PlayerPawn mo, AjarTake t)
	{
		Array<int> amt;
		Array<double> pct;
		for (int i = 0; i < t.kinds.Size(); i++) { amt.Push(0); pct.Push(0); }
		for (int e = 0; e < t.carTic.Size() && t.carTic[e] <= ot; e++) { amt[t.carKind[e]] = t.carAmt[e]; pct[t.carKind[e]] = t.carPct[e]; }
		for (int i = 0; i < t.kinds.Size(); i++)
		{
			if (amt[i] <= mo.CountInv(t.kinds[i])) continue;
			Inventory it = mo.FindInventory(t.kinds[i]);
			if (!it) { mo.GiveInventory(t.kinds[i], 1); it = mo.FindInventory(t.kinds[i]); }
			if (!it) continue;
			it.Amount = amt[i];
			let arm = BasicArmor(it);
			if (arm && pct[i] > 0) arm.SavePercent = pct[i];
		}
		hadClip = mo.CountInv("Clip"); hadShell = mo.CountInv("Shell");      // (not shots)
	}

	bool GoOnAs(PlayerPawn mo)
	{
		if (!open || phase != LIVE || at != 0) return false;
		int best = -1;
		for (int i = 0; i < takes.Size() - 1 && i < ghosts.Size(); i++)
		{
			if (!ghosts[i] || ot >= takes[i].x.Size()) continue;
			// not one that is still in its box: that box is shut now
			int gk, gb;
			[gk, gb] = Where(ghosts[i].pos.xy);
			if (gk != fight || gb != 0) continue;
			if (best < 0 || takes[i].x.Size() > takes[best].x.Size()) best = i;
		}
		if (best < 0) return false;
		AjarTake t = takes[best];
		AjarGhost g = ghosts[best];
		KeepClip(mo);
		Actor c = Actor.Spawn("AjarSnatch", mo.pos);
		if (c) { c.angle = mo.angle; c.translation = mo.translation; c.sprite = mo.sprite; c.frame = mo.frame; c.vel.z = 1; }
		Actor.Spawn("TeleportFog", mo.pos, ALLOW_REPLACE);
		Vector3 p = g.pos;
		mo.angle = g.angle;
		mo.pitch = g.pitch;
		g.Destroy();
		Carry(mo, t);
		t.x.Resize(ot);             // PlayGhosts goes by its length
		t.died = false;
		mo.SetOrigin(p, false);
		mo.vel = (0, 0, 0);
		mo.health = mo.player.health = RESCUE_HEALTH;
		mo.A_SetBlend("ff2010", 1.0, 40);
		mo.A_StartSound("misc/teleport", CHAN_AUTO);
		Say("You were killed. You go on as your earlier self,\nfrom where it stood, with what it carried.");
		return true;
	}

	bool Rescue(PlayerPawn mo)
	{
		if (stand && --stand == 0) mo.player.cheats &= ~CF_FROZEN;
		if (over)
		{
			mo.bBuddha = true;
			mo.vel = (0, 0, 0);
			if (--over == 0)
			{
				// The level begins again (whatever its way out leads to), on
				// their feet: not frozen, in full health, and as they first came.
				mo.player.cheats &= ~CF_TOTALLYFROZEN;
				mo.bBuddha = false;
				level.ChangeLevel(level.mapname, 0, CHANGELEVEL_RESETHEALTH | CHANGELEVEL_RESETINVENTORY);
			}
			return false;
		}
		bool can = phase != IDLE && (at > 0 || phase == LIVE);
		mo.bBuddha = can;
		if (!can || mo.health > 1) return false;
		if (GoOnAs(mo)) return true;
		let h = Doors();
		bool own = trips < BoxCount(fight);
		if (!own && !spare.Size())
		{
			// the last of them: the level ends
			over = 70;
			mo.player.cheats |= CF_TOTALLYFROZEN;
			mo.A_SetBlend("black", 1.0, 200);
			mo.A_StartSound("*death", CHAN_VOICE);
			Say("No box is left.\nThe show is over.");
			return false;
		}
		int sk = own ? fight : spare[0] / 10, sn = own ? trips + 1 : spare[0] % 10;
		Line l = h.FindLine(BoxLine(sk, sn));
		if (!l) return false;
		playerWas = mo.pos;                 // Leave() takes the door nearest to it
		// Taken out of the hall, their shape is left there for a moment, in light. Not in an open fight
		// that begins again at once: its hall is put back to before the fight
		// (there the earlier self runs for a door instead).
		if (at == 0) KeepClip(mo);
		bool body = at == 0 && !(open && own);
		Vector3 fell = mo.pos;
		double faced = mo.angle;
		if (at > 0)
		{
			if (phase == REPLAY)            // the fight is as it was left: nothing has been handed over
			{
				while (pending.Size())
				{
					if (pending[0]) { pending[0].bInvisible = false; pending[0].tics = pendingTics[0]; }
					pending.Delete(0); pendingTics.Delete(0);
				}
				DropPuppets(-1);
				Unfreeze();
				phase = LIVE;
			}
			h.Link(BoxLine(fight, at), 0, TIME_TEX);
			Line was = h.FindLine(used);
			if (was)
			{
				h.Link(used, 0, TIME_TEX);
				playerWas = ((was.v1.p + was.v2.p) / 2, 0);
			}
			at = 0;
		}
		if (!own)
		{
			// the fight is put back to before it began, to begin when they return
			if (open)
			{
				AjarTake t = takes[takes.Size() - 1];
				t.died = true;
				double best = 1e9;
				for (int j = 1; h.FindLine(HallLine(fight, j)); j++)
				{
					Line d = h.FindLine(HallLine(fight, j));
					double far = (playerWas.xy - (d.v1.p + d.v2.p) / 2).Length();
					if (far < best) { best = far; t.door = HallLine(fight, j); }
				}
				EndGo();
			}
			ClearHall();
			HallDoors(0);
			HouseLights(fight, 1);
			SetScreen(fight, 0);
			showDigit = 0;
			phase = IDLE;
			comeBack = true;
			spare.Delete(0);
			spareOut = sk * 10 + sn;
			h.Link(BoxLine(sk, sn), HallLine(sk, 1), TIME_TEX);
			h.Link(HallLine(sk, 1), BoxLine(sk, sn), TIME_TEX);
			mo.A_SetBlend("ff2010", 1.0, 40);
			Say("You were killed. This box was left over from an earlier fight,\nand its door is open. The fight begins again when you are back.");
		}
		if (body)
		{
			Actor c = Actor.Spawn("AjarSnatch", fell);
			if (c) { c.angle = faced; c.translation = mo.translation; c.sprite = mo.sprite; c.frame = mo.frame; c.vel.z = 1; }
			Actor.Spawn("TeleportFog", fell, ALLOW_REPLACE);
		}
		Vector2 p = (l.v1.p + l.v2.p) / 2 + (l.delta.y, -l.delta.x).Unit() * 40;
		mo.SetOrigin((p, l.frontsector.floorplane.ZAtPoint(p)), false);
		mo.angle = VectorAngle(l.delta.y, -l.delta.x);
		mo.vel = (0, 0, 0);
		mo.health = mo.player.health = RESCUE_HEALTH;
		mo.bBuddha = false;
		mo.A_StartSound("misc/teleport", CHAN_AUTO);
		rescued = own;
		// they stand where they were put for a second (they can look about):
		// keys still held from the fight must not walk them out of the box
		stand = STAND_TICS;
		mo.player.cheats |= CF_FROZEN;
		return true;
	}

	// A spare box's door stays open while the player is in the box or in its
	// hall (they can go back in for what lies there); it shuts once they have
	// left that hall.
	void SpareTick(Actor mo, int k, int b)
	{
		if (!spareOut || k == spareOut / 10) return;
		let h = Doors();
		h.Link(BoxLine(spareOut / 10, spareOut % 10), 0, TIME_TEX);
		h.Link(HallLine(spareOut / 10, 1), 0, TIME_TEX);
		spareOut = 0;
	}

	// Back in the hall of a fight that was put back: it begins again.
	void Resume(Actor mo)
	{
		comeBack = false;
		phase = LIVE;
		at = 0;
		if (open) NewTake(mo);
		else
		{
			main = new("AjarTrack");
			slotCls.Clear();
		}
		HallDoors(trips + 1);
	}

	// The door the player has just come out of shuts behind them, and a shut
	// door is a solid line: one that overlaps it cannot move at all. So they
	// are put a step clear of it, on the side they are on.
	const CLEAR = 26;
	void StepClear(Actor mo, int id)
	{
		Line l = Doors().FindLine(id);
		if (!l) return;
		Vector2 n = (l.delta.y, -l.delta.x).Unit();
		double d = (mo.pos.xy - (l.v1.p + l.v2.p) / 2) dot n;
		if (abs(d) >= CLEAR) return;
		Vector2 p = mo.pos.xy + n * ((d < 0 ? -CLEAR : CLEAR) - d);
		mo.SetOrigin((p, mo.pos.z), true);
	}

	// The player has gone through one of the hall's doors.
	void Leave(Actor mo)
	{
		let h = Doors();
		double best = 1e9;
		for (int j = 1; h.FindLine(HallLine(fight, j)); j++)
		{
			Line l = h.FindLine(HallLine(fight, j));
			double d = (playerWas.xy - (l.v1.p + l.v2.p) / 2).Length();
			if (d < best) { best = d; used = HallLine(fight, j); }
		}
		// what is on the player's heels comes too
		Line door = h.FindLine(used);
		Vector2 mid = (door.v1.p + door.v2.p) / 2;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (!rescued && pending.Size() < 2 && (a = Actor(it.Next())))
		{
			if (!a.bIsMonster || a.health <= 0 || a.target != mo || a.radius > 31 || a.height > 96 || a.bFloat) continue;
			if ((a.pos.xy - mid).Length() > FOLLOW_NEAR || !Counts(a, 0)) continue;
			pending.Push(a); pendingTics.Push(a.tics);
		}
		DoorLeave(mo);
		Freeze(mo);
		for (int i = 0; i < pending.Size(); i++) { pending[i].tics = -1; pending[i].bInvisible = true; }
		trips++;
		at = trips;
		StepClear(mo, BoxLine(fight, trips));
		HallDoors(0);
		let tr = new("AjarTrack");
		tr.box = trips;
		boxes.Push(tr);
		rt = 0;
		phase = REPLAY;
		// it is felt: a flash (red if it was a death), a sound, and for a
		// second the clock at the top runs back to nought (RenderOverlay)
		mo.A_SetBlend(rescued ? "ff2010" : "white", 1.0, 40);
		if (!rescued) mo.A_StartSound("misc/teleport", CHAN_AUTO);
		string last = trips == BoxCount(fight) ? "\nThe last box: after this the doors stay shut, and death is death." : "";
		if (rescued) Say("You were killed. It is before the fight again:\nthis door opens when the fight is where you left it." .. last);
		else if (!(said & 2)) Say("It is before the fight. Through the glass: yourself.\nThis door opens when the fight is where you left it.");
		else if (last != "") Say("The last box. After this the doors stay shut.");
		if (!rescued) said |= 2;
		rescued = false;
	}

	// One of them steps out of the box's door, once there is room.
	void Arrive()
	{
		if (!pending.Size() || rt % 12) return;
		Actor a = pending[0];
		if (a)
		{
			Line l = Doors().FindLine(BoxLine(fight, at));
			Vector2 p = (l.v1.p + l.v2.p) / 2 + (l.delta.y, -l.delta.x).Unit() * 40;
			Vector3 was = a.pos;
			a.SetOrigin((p, l.frontsector.floorplane.ZAtPoint(p)), false);
			if (!a.TestMobjLocation()) { a.SetOrigin(was, false); return; }
			a.angle = VectorAngle(l.delta.y, -l.delta.x);
			a.vel = (0, 0, 0);
			a.bInvisible = false;
			a.tics = pendingTics[0] > 0 ? pendingTics[0] : 1;
		}
		pending.Delete(0); pendingTics.Delete(0);
	}

	void EndReplay()
	{
		while (pending.Size())      // no room in the box: it stayed in the fight after all
		{
			if (pending[0]) { pending[0].bInvisible = false; pending[0].tics = pendingTics[0]; }
			pending.Delete(0); pendingTics.Delete(0);
		}
		DropPuppets(-1);
		Unfreeze();
		DoorEnd();
		phase = LIVE;
		let h = Doors();
		h.Link(BoxLine(fight, at), used, TIME_TEX);
		h.Link(used, BoxLine(fight, at), TIME_TEX);
		players[consoleplayer].mo.A_StartSound("doors/dr1_open", CHAN_AUTO);
	}

	// The player has come back into the hall.
	void Back()
	{
		let h = Doors();
		h.Link(BoxLine(fight, at), 0, TIME_TEX);
		at = 0;
		StepClear(players[consoleplayer].mo, used);
		HallDoors(trips + 1);
		players[consoleplayer].mo.A_SetBlend("white", 0.6, 18);
	}

	void Win()
	{
		won.Push(fight);
		for (int n = trips + 1; n <= BoxCount(fight); n++) spare.Push(fight * 10 + n);     // the boxes not used are kept
		HallDoors(0);
		phase = IDLE;
		DropGhosts();
		takes.Clear();
		DropPuppets(-1);
		demo = rec = null;
		open = false;
		HouseLights(fight, 1);
		main = null;
		boxes.Clear();
		slotCls.Clear();
		level.ExecuteSpecial(11 /* Door_Open */, null, null, false, 3090 + 100 * fight, 32);
	}

	override void WorldTick()
	{
		if (!zf.Size()) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		if (reel && reel < 4) { ReelTick(PlayerPawn(mo)); Tests(mo); return; }
		Rescue(PlayerPawn(mo));
		int k, b;
		[k, b] = Where(mo.pos.xy);
		if (!reel && phase == IDLE && !comeBack && k == 1 && b == 0 && won.Size() >= Fights() && Fights() > 1
			&& level.CreateSectorTagIterator(REEL_TAG).Next() >= 0)
		{
			StartReel(PlayerPawn(mo));
			Tests(mo);
			return;
		}
		if (phase == LIVE && k && k != fight && b == 0 && won.Find(k) == won.Size()) Quit();     // map32.zs
		SpareTick(mo, k, b);
		if (phase == IDLE)
		{
			// a big monster's death that won the fight is still being kept
			if (dueTic.Size() || dueLast) { Snap(mo); KeepKills(); }
			if (comeBack && k == fight && b == 0) Resume(mo);
			else if (!comeBack && k && b == 0 && won.Find(k) == won.Size() && mo.health > 0) Begin(k);
		}
		else if (phase == LIVE)
		{
			DoorWatch(FightTic());
			if (mo.health > 0 && k == fight)
			{
				if (at == 0 && b == trips + 1) { if (open) Retake(mo); else Leave(mo); }
				else if (at > 0 && b == 0) Back();
			}
			if (phase == LIVE)
			{
				int ft = FightTic();
				Show(fight, ft, mo);
				if (at == 0) Snap(mo);
				KeepKills();
				if (open) { RecordTake(PlayerPawn(mo)); PlayGhosts(mo); PlayDemo(mo); RecordDemo(); RecordFx(rec.fx); ot++; }
				else Record(main);
				// a hall with a show is empty until the count is over
				int go = HasShow(fight) ? SHOW_GO : 0;
				if (ft == go || (ft > go && level.maptime % 5 == 0))
				{
					if (at == 0) BackToTheHall(mo);
					int left = Left();
					if (!Cues(mo, left, ft - go) && !left && at == 0) Win();
					if (open && phase == LIVE) Hunt(mo);
				}
			}
		}
		if (phase == REPLAY)
		{
			Show(fight, rt, mo);
			DoorPlay(rt);
			PlayBack(main, rt);
			for (int n = 0; n < boxes.Size() - 1; n++)
			{
				if (rt < boxes[n].first.Size()) PlayBack(boxes[n], rt);
				else if (rt == boxes[n].first.Size()) DropPuppets(n + 1);
			}
			Hold();
			Arrive();
			Record(boxes[boxes.Size() - 1]);
			if (++rt >= main.first.Size()) EndReplay();
		}
		playerWas = mo.pos;
		Tests(mo);
	}

	void Tests(Actor mo)
	{
		int mode = CVar.GetCVar("ajar_autotest").GetInt();
		if (mode == 4 && level.mapname ~== "TIME") FollowScript(PlayerPawn(mo));
		else if (mode && level.mapname ~== "TIME") TimeScript(PlayerPawn(mo));
		if (mode == 3 && level.mapname ~== "TDOOR") DoorScript(PlayerPawn(mo));
		if (mode == 4 && level.mapname ~== "TDOOR") ChainScript(PlayerPawn(mo));
		if (mode == 5 && level.mapname ~== "TDOOR") HandScript(PlayerPawn(mo));
		if (mode == 3 && level.mapname ~== "MAP32") Map32Script(PlayerPawn(mo));
		if (mode == 4 && level.mapname ~== "MAP32") Wind32Script(PlayerPawn(mo));
		if (mode == 3 && level.mapname ~== "MAP31") SecretScript(PlayerPawn(mo));
		if (mode == 5 && level.mapname ~== "MAP31") OverScript(PlayerPawn(mo));
		if (mode == 6 && level.mapname ~== "MAP31") ThirdGoScript(PlayerPawn(mo));
		if (mode == 7 && level.mapname ~== "MAP31") WindScript(PlayerPawn(mo));
	}

	// How far the fight that is being watched has got, and when the door opens.
	override void RenderOverlay(RenderEvent e)
	{
		if (reel && reel < 4)
		{
			if (caption != "") Screen.DrawText(BigFont, Font.CR_GOLD, 320 - BigFont.StringWidth(caption) / 2, 360, caption, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
			if (reel == 2) Screen.DrawText(SmallFont, Font.CR_GRAY, 320 - SmallFont.StringWidth("USE: the next") / 2, 384, "USE: the next", DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
			return;
		}
		if (open && phase == LIVE && takes.Size() > 1)
		{
			int len = takes[takes.Size() - 2].x.Size();
			if (ot >= len) return;
			string o = String.Format("%d:%02d / %d:%02d", ot / 35 / 60, ot / 35 % 60, len / 35 / 60, len / 35 % 60);
			Screen.DrawText(BigFont, Font.CR_WHITE, 320 - BigFont.StringWidth(o) / 2, 12, o, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
			return;
		}
		if (phase != REPLAY || !main) return;
		int now = rt / 35, end = main.first.Size() / 35;
		if (rt < REWIND)
		{
			// just through the door: the clock runs back, large, in the middle
			int back = int(end * (1 - double(rt) / REWIND) + 0.99);
			string r = String.Format("<<  %d:%02d", back / 60, back % 60);
			Screen.DrawText(BigFont, Font.CR_GOLD, 160 - BigFont.StringWidth(r) / 2, 40, r, DTA_VirtualWidth, 320, DTA_VirtualHeight, 200);
			return;
		}
		string s = String.Format("%d:%02d / %d:%02d", now / 60, now % 60, end / 60, end % 60);
		Screen.DrawText(BigFont, Font.CR_WHITE, 320 - BigFont.StringWidth(s) / 2, 12, s, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
	}

	// --- the test box (map TIME, tools/map_time.py; MAP=TIME MODE=3 tools/smoke.sh) ---
	int testTic;
	int Selves()
	{
		int n = 0;
		for (int i = 0; i < puppets.Size(); i++) if (slotCls[puppetSlot[i]] is "PlayerPawn") n++;
		return n;
	}
	void Check(string what, bool ok) { Console.Printf("AJARTEST %s=%d", what, ok); }
	void Go(Actor mo, double x, double y, double z, double ang) { mo.SetOrigin((x, y, z), false); mo.angle = ang; mo.vel = (0, 0, 0); mo.pitch = 0; }

	void TimeScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d at=%d trips=%d rt=%d len=%d recs=%d puppets=%d frozen=%d left=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, at, trips, rt, main ? main.first.Size() : 0, main ? main.slot.Size() : 0, puppets.Size(), fz.Size(), Left());
		// the first take: into the hall, a few shots, three seconds of it
		if (t == 10) Check("idle", phase == IDLE);
		if (t > 10 && t < 40) mo.vel.xy = (0, 8);
		if (t == 45) { Check("begun", phase == LIVE && fight == 1); Go(mo, 384, 200, 0, 90); }
		if (t > 45 && t < 150 && t % 20 == 0) mo.player.cmd.buttons |= BT_ATTACK;
		// out by the east door
		if (t == 150) Go(mo, 700, 320, 0, 0);
		if (t > 150 && t < 175) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 176)
		{
			Check("out", phase == REPLAY && at == 1 && used == 3101 && fz.Size() > 0);
			Go(mo, -44, 320, 64, 0);
		}
		if (t == 200) Check("watching", puppets.Size() > 0 && Selves() == 1);
		// held still: nothing of the real fight may move while it is watched
		if (t == 201) { double sum; for (int i = 0; i < fz.Size(); i++) if (fz[i]) sum += fz[i].pos.x + fz[i].pos.y; testSum = sum; }
		if (t == 250) { double sum; for (int i = 0; i < fz.Size(); i++) if (fz[i]) sum += fz[i].pos.x + fz[i].pos.y; Check("held", phase == REPLAY && sum == testSum); }
		// the door opens when the fight is where it was left: back in by it
		if (t == 345) { Check("handedOver", phase == LIVE && at == 1 && !puppets.Size() && !fz.Size()); Go(mo, -128, 380, 64, 90); }
		if (t > 345 && t < 370) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 372) { Check("backIn", at == 0 && mo.pos.x > 600 && mo.pos.z < 8); Go(mo, 384, 200, 0, 90); }
		// a second take, and out by the south door: two earlier selves to watch
		if (t == 440) Go(mo, 128, 80, 0, 270);
		if (t > 440 && t < 465) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 466) { Check("outAgain", phase == REPLAY && at == 2 && used == 3102); Go(mo, 384, 684, 64, 270); }
		if (t == 520) Check("twoSelves", Selves() == 2);
		if (t == 700) Check("oneSelf", Selves() == 1);
		if (t == 800) { Check("handedOver2", phase == LIVE && at == 2); Go(mo, 470, 752, 64, 0); }
		if (t > 800 && t < 825) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 827) Check("backIn2", at == 0 && mo.pos.y < 300 && mo.pos.z < 8);
		// no box left: the doors are shut; and the fight is won
		if (t == 830) Check("shut", (Doors().FindLine(3101).flags & Line.ML_BLOCKING) != 0);
		if (t == 840 || t == 870)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0) a.DamageMobj(mo, mo, 10000, 'None');
		}
		if (t == 900) Check("won", phase == IDLE && won.Size() == 1);
	}
	double testSum;

	// MAP=TIME MODE=4: the demon is on the player's heels at the east door,
	// and comes out into the box with them.
	Actor testDemon;
	void FollowScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		if (t > 10 && t < 40) mo.vel.xy = (0, 8);
		if (t == 45)
		{
			Go(mo, 700, 320, 0, 0);
			let it = ThinkerIterator.Create("Demon");
			testDemon = Actor(it.Next());
			testDemon.SetOrigin((640, 320, 0), false);
			testDemon.target = mo;
		}
		if (t > 45 && t < 70) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 71) { Check("followed", phase == REPLAY && pending.Size() == 1 && pending[0] == testDemon); Go(mo, -44, 320, 64, 0); }
		if (t == 110)
		{
			int k, b;
			[k, b] = Where(testDemon.pos.xy);
			Check("inTheBox", !pending.Size() && b == 1 && !testDemon.bInvisible && testDemon.tics != -1 && fz.Find(testDemon) == fz.Size());
		}
		if (t == 170)
		{
			int k, b;
			[k, b] = Where(testDemon.pos.xy);
			Check("stayedOut", phase == LIVE && b == 1 && testDemon.health > 0);
			Go(mo, -128, 380, 64, 90);          // back in by the box's door, leaving it there
		}
		if (t > 170 && t < 195) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (t == 205)
		{
			int k, b;
			[k, b] = Where(testDemon.pos.xy);
			Check("notShutInTheBox", at == 0 && b == 0 && testDemon.pos.z < 8 && testDemon.Distance2D(mo) > 200);
		}
	}

	// MAP=MAP31 MODE=5 TIMEOUT=60: killed in hall 1 with no box left: the
	// level ends and begins again, the player on their feet and as they first
	// came. (The handler is new in the new level: it tells by the health.)
	void OverScript(PlayerPawn mo)
	{
		int t = testTic++;
		if (level.totaltime > level.maptime + 10)       // the level again
		{
			if (t == 30) Check("beganAgain", phase == IDLE && !over && mo.health == 100 && !mo.FindInventory("BFG9000")
				&& !(mo.player.cheats & CF_TOTALLYFROZEN) && mo.pos.y < -500);
			if (t == 31) Go(mo, 384, -500, 32, 90);
			if (t > 31 && t < 40) mo.vel.xy = (0, 8);
			if (t == 45) Check("andCanWalk", mo.pos.y > -470);
			return;
		}
		if (t == 2) Go(mo, 384, -60, 32, 90);
		if (t == 10) { Go(mo, 384, 60, 0, 90); mo.GiveInventoryType("BFG9000"); }
		if (t == 20 && phase == LIVE) { trips = BoxCount(fight); mo.health = mo.player.health = 1; }
		if (t == 24) Check("theShowIsOver", over > 0 && (mo.player.cheats & CF_TOTALLYFROZEN));
	}

	// MAP31 (tools/map_secret1.py; MAP=MAP31 MODE=3 TIMEOUT=250 tools/smoke.sh):
	// MAP31 MODE=6: hall 2 three times over. The third go's demo is a go that
	// had demo monsters in it itself; when it is over every monster left must
	// be awake.
	int Stopped(bool say)       // monsters of the fight alive whose state does not run
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health <= 0 || a.tics != -1) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight) continue;
			n++;
			if (!say) continue;
			string why = "no role";
			for (int i = 0; demo && i < demo.roles.Size(); i++)
			{
				AjarRole r = demo.roles[i];
				if (r.actor != a) continue;
				why = String.Format("role %d mode=%d born=%d size=%d lag=%d dead=%d hidden=%d wakeDue=%d waited=%d lasthp=%d", i, r.mode, r.born, r.x.Size(), r.lag,
					r.dead, r.hidden, r.wakeDue, r.waited, r.hp.Size() ? r.hp[r.hp.Size() - 1] : -1);
			}
			Console.Printf("AJARTEST stopped %s onDemo=%d health=%d box=%d ot=%d len=%d: %s", a.GetClassName(), OnDemo(a), a.health, b, ot, demo ? demo.len : -1, why);
		}
		return n;
	}
	int MidFall()       // bodies in the fight that stopped in the middle of falling
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!a.bIsMonster || a.health > 0 || a.tics != -1 || !a.CurState) continue;
			State st = PictureState(a);
			if (!st || st.tics == -1) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight) continue;
			n++;
			Console.Printf("AJARTEST midFall %s frame=%d onDemo=%d", a.GetClassName(), a.frame, OnDemo(a));
		}
		return n;
	}
	void Hurt(Actor mo, int n, int dmg)
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (n > 0 && (a = Actor(it.Next())))
		{
			if (!a.bIsMonster || a.health <= 0) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k != fight || b != 0) continue;
			a.DamageMobj(mo, mo, dmg, 'None');
			n--;
		}
	}
	int goStart;
	// Winding (MAP=MAP31 MODE=7 tools/smoke.sh): hall 2. A first go; in the
	// second, from the box, time is wound back and then on, and the hall is
	// each time as it was at that moment; the third go plays the second whole,
	// its wound stretches as they were; and the plates wind by half a minute.
	int seenA, seenB, seenC;
	void WindScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		double cx = 2752 + 768;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d phase=%d at=%d trips=%d ot=%d len=%d takes=%d onDemo=%d awake=%d",
			t, phase, at, trips, ot, demo ? demo.len : -1, takes.Size(), Rails(true), Rails(false));
		if (t == 1)
		{
			int n = 0;
			let it = ThinkerIterator.Create("AjarWind");
			while (it.Next()) n++;
			Check("plates", n == 16);
			Go(mo, cx, 60, 0, 90);
		}
		if (t == 5) { Wind(mo, -1); Check("nothingToWindYet", ot > 2 && takes.Size() == 1); }
		if (t == 260) Hurt(mo, 30, 100000);
		if (t == 300) Hurt(mo, 6, 20);
		if (t == 340) Hurt(mo, 16, 100000);
		if (t == 520) mo.health = mo.player.health = 1;
		if (t == 524) Check("go2", open && at == 1 && takes.Size() == 2);
		if (takes.Size() == 2 && (testStep < 10 || testStep == 21))
		{
			if (ot == 200 && testStep == 0) { seenA = Rails(true); testStep = 1; }
			if (ot == 302 && testStep == 1) { seenB = Rails(true) * 1000 + RailsDead(); testStep = 2; }
			if (ot == 422 && testStep == 2) { seenC = Rails(true) * 1000 + RailsDead(); testStep = 21; }
			if (ot == 430 && testStep == 21) { WindTo(mo, 300); testStep = 3; }
			else if (ot == 302 && testStep == 3)
			{
				Check("woundBack", Rails(true) * 1000 + RailsDead() == seenB && !Rails(false) && takes.Size() == 2
					&& takes[1].x.Size() == ot && rec.fx.first.Size() == ot);
				Console.Printf("AJARTEST seenB=%d now=%d", seenB, Rails(true) * 1000 + RailsDead());
				testStep = 4;
			}
			if (ot == 310 && testStep == 4) { WindTo(mo, 420); testStep = 5; }
			else if (ot == 422 && testStep == 5)
			{
				Check("woundOn", Rails(true) * 1000 + RailsDead() == seenC && takes[1].x.Size() == ot);
				Console.Printf("AJARTEST seenC=%d now=%d", seenC, Rails(true) * 1000 + RailsDead());
				testStep = 6;
			}
			// into the hall: something is hurt awake, and it does not wind from there
			if (ot == 440 && testStep == 6) { Back(); Go(mo, cx, 300, 0, 90); testStep = 7; }
			if (ot == 450 && testStep == 7) { Hurt(mo, 3, 20); testStep = 8; }
			if (ot == 470 && testStep == 8) { int was = ot; Wind(mo, -1); Check("notFromTheHallOnceAwake", ot == was && Rails(false) > 0); testStep = 9; }
			if (ot == 530 && testStep == 9) { mo.health = mo.player.health = 1; testStep = 10; }
		}
		if (takes.Size() == 3)
		{
			if (ot == 4 && testStep == 10) { Check("go3", at == 2 && demo && demo.len >= 525 && demo.len <= 535); testStep = 11; }
			if (ot == 200 && testStep == 11) { Check("itsStartIsThere", Rails(true) == seenA); testStep = 12; }
			if (ot == 302 && testStep == 12)
			{
				Check("theWoundStretchIsThere", Rails(true) * 1000 + RailsDead() == seenB);
				Console.Printf("AJARTEST seenB=%d now=%d", seenB, Rails(true) * 1000 + RailsDead());
				testStep = 13;
			}
			// the plates: half a minute back is the start; half a minute on is two seconds before its end
			if (ot == 320 && testStep == 13) { mo.GiveInventoryType("GreenArmor"); seenA = mo.health; Wind(mo, -1); testStep = 14; }
			else if (ot == 2 && testStep == 14)
			{
				Check("backToTheStart", !Rails(true) && takes.Size() == 3);
				Check("itCosts", mo.health == seenA - 10 && mo.CountInv("BasicArmor") == 95);
				testStep = 15;
			}
			if (ot == 30 && testStep == 15) { Wind(mo, 1); testStep = 16; }
			else if (testStep == 16) { Check("onToItsEnd", ot >= demo.len - 70 && ot <= demo.len - 66 && Rails(true) > 5); testStep = 17; }
			else if (testStep == 17 && ot == demo.len - 40) { int was = ot; Wind(mo, 1); Check("noFurther", ot == was && mo.health == seenA - 20); testStep = 18; }
			else if (testStep == 18 && ot == demo.len - 30)
			{
				int was = ot;
				mo.health = mo.player.health = 10;
				Wind(mo, -1);
				Check("notWithoutTheHealth", ot == was && mo.health == 10);
				mo.health = mo.player.health = 50;
				testStep = 19;
			}
			if (testStep == 19 && ot == demo.len + 60) { Check("awakeAtItsEnd", !Rails(true) && Rails(false) > 5); testStep = 20; }
		}
	}
	int testStep;
	int RailsDead()
	{
		int n = 0;
		for (int i = 0; demo && i < demo.roles.Size(); i++) if (demo.roles[i].mode == 1 && demo.roles[i].dead) n++;
		return n;
	}

	void ThirdGoScript(PlayerPawn mo)
	{
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		double cx = 2752 + 768;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d phase=%d at=%d trips=%d ot=%d len=%d takes=%d onDemo=%d awake=%d stopped=%d",
			t, phase, at, trips, ot, demo ? demo.len : -1, takes.Size(), Rails(true), Rails(false), Stopped(false));
		if (t == 1) Go(mo, cx, 60, 0, 90);
		// the first go: enough are killed for both later waves to come, then the player is
		if (t == 260) Hurt(mo, 30, 100000);
		if (t == 300) Hurt(mo, 6, 20);
		if (t == 340) Hurt(mo, 16, 100000);
		if (t == 520) mo.health = mo.player.health = 1;
		if (t == 524) { Check("go2", open && at == 1 && takes.Size() == 2); goStart = t - ot; }
		// the second: into the hall while the first plays; more killed; on past its end
		int u = t - goStart;
		if (takes.Size() == 2)
		{
			if (u == 250) { Back(); Go(mo, cx, 300, 0, 90); }
			if (u == 300) Hurt(mo, 10, 100000);
			if (u == 640) Check("awakeAfterGo1", !Demoing() && !Rails(true) && Stopped(true) == 0);
			if (u == 715) Hurt(mo, 4, 100000);         // these are still falling when the go ends
			if (u == 720) mo.health = mo.player.health = 1;
		}
		if (takes.Size() == 3)
		{
			if (ot == 4) Check("go3", at == 2 && demo && demo.len > 500);
			// into the hall, and killed there: on as an earlier self
			if (ot == 300) { Back(); Go(mo, cx, 300, 0, 90); }
			// (with nothing left: the earlier self has its bullets and shells still, and no armour to give)
			if (ot == 340) { mo.TakeInventory("Clip", 1000); mo.TakeInventory("Shell", 1000); mo.GiveInventory("Cell", 7); mo.GiveInventoryType("GreenArmor"); }
			if (ot == 350) mo.health = mo.player.health = 1;
			if (ot == 354) Check("onAsAnEarlierSelf", at == 0 && trips == 2 && takes.Size() == 3);
			if (ot == 354) Check("withWhatItCarried", mo.CountInv("Clip") >= 50 && mo.CountInv("Cell") == 7 && mo.CountInv("BasicArmor") == 100);
			if (ot == 400) Check("onTheDemo3", Demoing() && Rails(true) > 5);
			if (ot == demo.len + 60) Check("awakeAfterGo2", !Demoing() && !Rails(true) && Rails(false) > 5 && Stopped(true) == 0);
			if (ot == demo.len + 200) Check("stillAwake", Stopped(true) == 0);
			if (ot == demo.len + 100) Check("noneStoppedInItsFall", MidFall() == 0);
		}
	}

	// each hall in turn: in while it is empty and lit, the count, out by the
	// west door (hall 2: by being killed), into box 1, back in, and the fight
	// won. Hall 1 is watched again from the box, and the player is killed
	// there while watching; halls 2 and 3 are open fights, begun again.
	int testN;
	Actor testRail, testBump;
	int Rails(bool on)      // monsters of the fight alive, on the demo or awake
	{
		int n = 0;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && OnDemo(a) == on) n++;
		return n;
	}
	bool ShowLight(int k, bool up)       // is the hall's light as it should be?
	{
		for (int i = 0; i < showSec.Size(); i++)
			if (showFight[i] == k && level.sectors[showSec[i]].lightlevel != (up ? SHOW_UP : showDown[i])) return false;
		return HasShow(k);
	}
	void SecretScript(PlayerPawn mo)
	{
		static const int hx[] = { -192, 2752, 5696 };
		static const int hw[] = { 1152, 1536, 1920 };
		static const int hh[] = { 960, 1216, 1472 };
		if (level.totaltime > level.maptime + 10) return;       // the level again, after the reel
		int t = testTic++;
		mo.player.cheats |= CF_GODMODE;
		if (t % 35 == 0) Console.Printf("AJARTEST t=%d pos=(%d,%d,%d) phase=%d fight=%d at=%d trips=%d rt=%d len=%d recs=%d puppets=%d frozen=%d left=%d digit=%d",
			t, mo.pos.x, mo.pos.y, mo.pos.z, phase, fight, at, trips, rt, main ? main.first.Size() : 0, main ? main.slot.Size() : 0, puppets.Size(), fz.Size(), Left(), showDigit);
		int D = 180;                      // the show, and a little
		int k = t / (540 + 2 * D), u = t % (540 + 2 * D);
		if (k > 2)
		{
			int v = t - 3 * (540 + 2 * D);
			if (v == 0) Check("secrets", level.total_secrets == 1);
			// the reel: by the last way out to the seat in hall 1; two deaths in halls were kept
			if (v == 6) Go(mo, 384, 420, 0, 270);
			if (v == 10) Check("bigDeathsKept", kills.Size() == 3 && kills[0].big >= BIG && kills[0].stills.Size() > 10 && kills[0].what != "");
			if (v == 10) Console.Printf("AJARTEST lastKills=%d clips=%d", lastKills.Size(), clips.Size());
			if (v == 10) Check("theReelBegins", reel == 1 && clips.Size() == 3 + lastKills.Size() && mo.bInvisible && ShowLight(1, false));
			if (v == 10) Check("aLastKillForEveryHall", lastKills.Size() == Fights() && lastKills[0].fight == 1 && lastKills[0].stills.Size() > 10 && clips[clips.Size() - 1].last);
			if (v == 150)
			{
				let si = level.CreateSectorTagIterator(REEL_TAG);
				Sector sec = level.sectors[si.Next()];
				Check("theScreenIsDown", sec.CenterCeiling() == 32 && reel == 2 && cam && puppets.Size() > 3);
				int ck, cb;
				[ck, cb] = Where(cam.pos.xy);
				Check("aDeathInHall2", ck == 2 && clips[0].fight == 2 && clips[1].fight == 3 && clips[2].fight == 3);
			}
			if (v == 420) Check("goneToLightOnScreen", reel == 2 && reelClip == 0 && fallen && !fallen.bInvisible && fallen.alpha < 1);
			if (v >= 440 && v <= 490 && v % 10 == 0 && reel == 2) { reelTic = 100000; }      // the rest, quickly
			if (v == 485) Check("lastScenesOnScreen", reel == 2 && clips[reelClip].last && caption.IndexOf("the last to fall") > 0);
			if (v == 500) Check("theEnd", reel == 3);
			return;
		}
		double x = hx[k], cx = x + hw[k] / 2, cy = hh[k] / 2;
		string n = String.Format("%d", k + 1);
		if (u == 1) Go(mo, cx, -60, 32, 90);
		if (u == 5) Check("begun" .. n, phase == LIVE && fight == k + 1);
		if (u == 10) Go(mo, cx, 60, 0, 90);
		if (u == 30) Check("emptyAndLit" .. n, !Left() && ShowLight(k + 1, true) && showDigit == 0);
		if (u == 100) Check("count" .. n, !Left() && ShowLight(k + 1, false) && showDigit == 3);
		if (u == 200) Check("theyCome" .. n, Left() > 5 && showDigit == 0);
		// and the same again from the box
		if (phase == REPLAY && rt == 30) Check("againEmptyAndLit" .. n, Selves() == 1 && puppets.Size() < 8 && ShowLight(k + 1, true));
		if (phase == REPLAY && rt == SHOW_COUNT + SHOW_STEP + 5) Check("againCount" .. n, ShowLight(k + 1, false) && showDigit == 2);
		if (phase == REPLAY && rt == SHOW_GO + 20) Check("watching" .. n, Selves() == 1 && puppets.Size() > 5 && showDigit == 0);
		// shots for the ghost to fire again: a rocket, and a bullet gone from the clip
		if (k == 1 && u == 200) mo.SpawnPlayerMissile("Rocket");
		if (k == 1 && u == 210) mo.TakeInventory("Clip", 1);
		if (u < 80 + D) return;
		u -= D;
		if (k == 1)                         // the second hall is left by being killed, in its middle
		{
			if (u == 80) { Go(mo, cx, cy, 0, 90); mo.health = mo.player.health = 1; }
			if (u == 82) Check("killedIntoTheBox", open && phase == LIVE && at == 1 && mo.health == RESCUE_HEALTH && used == HallLine(2, 3));
			// the open fight: it has begun again, empty, with the earlier self in it, whose shots were kept
			if (u == 84) Check("begunAgain", ot < 6 && !Left() && takes.Size() == 2 && takes[0].evTic.Size() == 2 && takes[0].died);
			if (u == 100) Check("besideMyself", ghosts.Size() == 1 && ghosts[0] && ghosts[0].pos.z < 40 && ShowLight(2, true));
			if (u == 82 + 215) Check("itFiresAgain", takes[0].next == 2);
			if (u == 82 + 225)
			{
				// in the box: the last go as it went. Every monster is on the demo, where it was then
				AjarRole r = demo.roles[0];
				Check("theyPlayAsTheyWent", at == 1 && Demoing() && Rails(true) > 5 && !Rails(false) && r.actor
					&& r.actor.pos.x == r.x[ot - 1 - r.born] && r.actor.pos.y == r.y[ot - 1 - r.born]);
			}
			if (u == 82 + 300) Check("allAwakeAtItsEnd", !Demoing() && !Rails(true) && Rails(false) > 5 && !puppets.Size());
			if (u == 82 + 230) Check("theyComeAgain", Left() > 5 && ghosts.Size() == 1 && ghosts[0]);
		}
		else
		{
			if (u == 80) Go(mo, x + 40, 128, 0, 180);
			if (u > 80 && u < 100) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		}
		if (u == 105)
		{
			Check("out" .. n, phase == (k ? LIVE : REPLAY) && at == 1 && mo.pos.z > 60);
			Console.Printf("AJARTEST followers=%d", pending.Size());
			Go(mo, x - 40, cy, 64, 0);          // at the glass
		}
		if (k == 0)                         // in the small hall: killed in the first box while watching
		{
			if (u == 110) mo.health = mo.player.health = 1;
			// the armour in the box they are now in is real, and is taken
			if (u == 113) Go(mo, cx, hh[k] + 156, 64, 0);       // (a thing is taken by walking onto it)
			if (u > 113 && u < 120) mo.vel.xy = (8, 0);
			if (u == 122) Check("armourInTheBox", phase == REPLAY && mo.CountInv("BasicArmor") == 100);
			if (u == 112) Check("killedInABox", phase == REPLAY && at == 2 && trips == 2 && rt < 5 && mo.health == RESCUE_HEALTH && mo.pos.y > hh[k]);
		}
		if (k == 2)                         // the great hall is an open fight too, left here by a door
		{
			if (u == 107) Check("begunAgain3", open && ot < 30 && !Left() && takes.Size() == 2 && !takes[0].died && takes[0].door == HallLine(3, 1));
			// killed in the hall while the earlier self is still there: on as it, and no box spent
			// (the walk teleports: it says itself that the player is in the hall, and puts them back in the box after)
			if (u == 130) { at = 0; Go(mo, cx, 300, 0, 90); mo.health = mo.player.health = 1; }
			if (u == 132) Check("onAsMyEarlierSelf", at == 0 && trips == 1 && phase == LIVE && mo.health == RESCUE_HEALTH && ghosts.Size() == 1 && !ghosts[0]
				&& takes.Size() == 2 && takes[0].x.Size() < 60 && abs(mo.pos.x - takes[0].x[takes[0].x.Size() - 1]) < 20 && (mo.pos.xy - (cx, 300)).Length() > 50);
			if (u == 133) { at = 1; Go(mo, x - 40, cy, 64, 0); }
			// into the hall while the last go is still playing: nothing wakes for that
			if (u == 299) testN = Rails(true);
			if (u == 300) { Back(); Go(mo, cx, 300, 0, 90); }
			if (u == 304) Check("noneWakesAsIStepIn", testN > 5 && !Rails(false) && Rails(true) == testN);
			if (u == 305)
			{
				for (int i = 0; i < demo.roles.Size() && !testRail; i++)
					if (demo.roles[i].mode == 1 && !demo.roles[i].dead && !demo.roles[i].wakeDue) testRail = demo.roles[i].actor;
				if (testRail) testRail.DamageMobj(mo, mo, 5, 'None');
			}
			// walking into one wakes it
			if (u == 310)
			{
				for (int i = 0; i < demo.roles.Size() && !testBump; i++)
					if (demo.roles[i].mode == 1 && !demo.roles[i].dead && !demo.roles[i].wakeDue) testBump = demo.roles[i].actor;
				if (testBump) Go(mo, testBump.pos.x, testBump.pos.y, testBump.pos.z, 90);
			}
			if (u == 312) Go(mo, cx, 300, 0, 90);
			if (u == 350) Check("wokenByATouch", testBump && !OnDemo(testBump) && testBump.tics != -1 && testBump.health > 0 && Rails(true) <= testN - 2);
			if (u == 345) Check("wokenByAShot", testRail && !OnDemo(testRail) && testRail.tics != -1 && testRail.health > 0
				&& testRail.health <= testRail.SpawnHealth() - 5);
			if (u == 410) Check("allAwakeAtItsEnd3", !Demoing() && !Rails(true) && Rails(false) > 3);
			if (u == 125) Check("besideMyself3", ghosts.Size() == 1 && ghosts[0] && ghosts[0].pos.z < 40 && ShowLight(3, true));
		}
		if (u < 240 + D) return;
		u -= D;
		if (u == 240)
		{
			if (k != 2) Check("handedOver" .. n, phase == LIVE && at == (k == 0 ? 2 : 1) && !puppets.Size());
			if (k == 0) Go(mo, cx, hh[k] + 196, 64, 90);        // the north box
			else if (k == 1) Go(mo, x - 200, cy, 64, 180);
		}
		if (k != 2 && u > 240 && u < 260) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (k == 1 && u == 262) Check("itWentToADoor", ghosts.Size() == 1 && !ghosts[0]);
		if (k == 2 && u == 262) Check("itLeftWhenIDid", ghosts.Size() == 1 && !ghosts[0]);
		if (u == 265) Check("backIn" .. n, at == 0 && mo.pos.x > x && mo.pos.z < 30);     // it may stand on a row of seats
		if (u == 266) Go(mo, cx, 40, 0, 90);        // out of the way of what comes in later
		if (k == 2)     // the great hall: no box of its own left, killed: into a box hall 1 did not use, and the fight begins again
		{
			if (u == 266) { trips = BoxCount(fight); HallDoors(0); mo.health = mo.player.health = 1; }
			if (u == 268) { let ci = ThinkerIterator.Create("AjarSnatch"); Actor c = Actor(ci.Next()); Check("goneToLight", c && abs(c.pos.x - cx) < 2 && abs(c.pos.y - 40) < 2 && c.alpha < 1); }
			if (u == 268) Check("killedIntoASpareBox", phase == IDLE && comeBack && spare.Size() == 2 && spareOut == 13 && !Left()
				&& mo.pos.x > 960 && mo.pos.x < 1300 && mo.pos.y < hh[0] && mo.health == RESCUE_HEALTH);
			if (u == 269) Go(mo, cx, 40, 0, 90);
			if (u == 275) Check("begunOver", phase == LIVE && !comeBack && FightTic() < 12 && !Left() && ShowLight(3, true));
		}
		if (u >= 270 && u <= 536 && (u % 20 == 10 || (u > 440 && u % 4 == 0)))
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster && a.health > 0 && a.Distance2D(mo) < 2000) a.DamageMobj(mo, mo, 100000, 'None');
		}
		if (u == 538)
		{
			let si = level.CreateSectorTagIterator(3190 + 100 * k);
			int i = si.Next();
			Check("won" .. n, phase == IDLE && won.Size() == k + 1 && i >= 0 && level.sectors[i].CenterCeiling() > level.sectors[i].CenterFloor() + 60);
		}
	}
}
