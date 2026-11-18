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
//    that many monsters are left, args[3] the monster's Doom editor number.
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
}

// What was seen in one place over one stretch of time, from the fight's
// first tic. Only changes are kept: a record says how one thing (its slot)
// looked from that tic on, or that it was gone (sf < 0).
class AjarTrack play
{
	int box;                    // 0: the hall, and each box from the moment its door opened
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
		if (players[consoleplayer].mo) players[consoleplayer].cheats &= ~CF_TOTALLYFROZEN;
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
			if (d && mo) mo.A_StartSound("switches/normbutn", CHAN_AUTO, 0, phase == REPLAY ? 0.5 : 1.0);
		}
	}

	// --- the open fight ---------------------------------------------------------
	// A fight whose box is open from the start (MAP31's second hall). A trip
	// does not show the fight again: it begins it again. The hall is cleared,
	// the show runs, the same monsters come; the box's door is open at once
	// onto the door the player left by, and every earlier go at the fight is
	// there as an AjarGhost that walks where the player walked and fires
	// what they fired, for as long as that go lasted. So the past is changed:
	// the player fights beside themselves, and the fight goes on from where
	// they are when the ghosts are gone. Nothing is recorded but the player.
	const GHOST_RUN = 16;       // an earlier self's speed on its way out
	Array<int> openFights;
	bool open;                  // the fight that is on is one
	int ot;                     // its tic, from the start of this go
	Array<AjarTake> takes;      // every go at it, the last being this one
	Array<AjarGhost> ghosts;    // ghosts[i]: of takes[i], while it lasts
	Array<Actor> shots;         // the player's missiles that are already written down
	int hadClip, hadShell;

	void RecordTake(PlayerPawn mo)
	{
		AjarTake t = takes[takes.Size() - 1];
		t.x.Push(mo.pos.x); t.y.Push(mo.pos.y); t.z.Push(mo.pos.z); t.ang.Push(mo.angle); t.pit.Push(mo.pitch);
		t.sf.Push((int(mo.sprite) << 8) | (mo.frame & 127));
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
			if (k == fight && b == 0) gone.Push(a);
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
	}

	void NewTake(Actor mo)
	{
		takes.Push(new("AjarTake"));
		ot = 0;
		hadClip = mo.CountInv("Clip"); hadShell = mo.CountInv("Shell");
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
		ClearHall();
		NewTake(mo);
		HallDoors(0);
		h.Link(BoxLine(fight, at), used, TIME_TEX);
		h.Link(used, BoxLine(fight, at), TIME_TEX);
		mo.A_SetBlend(rescued ? "ff2010" : "white", 1.0, 40);
		if (!rescued) mo.A_StartSound("misc/teleport", CHAN_AUTO);
		string last = trips == BoxCount(fight) ? "\nThe last box: after this the doors stay shut, and death is death." : "";
		Say((rescued ? "You were killed. " : "") .. "It is before the fight, and this door is open:\ngo back in and fight beside yourself." .. last);
		rescued = false;
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

	override void WorldThingDied(WorldEvent e)
	{
		Actor t = e.thing;
		if (!t || !t.bIsMonster || phase != LIVE || t.SpawnHealth() < BIG) return;
		int k, b;
		[k, b] = Where(t.pos.xy);
		if (k != fight || b != 0) return;
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
		HouseLights(1, 0);
		level.ExecuteSpecial(40 /* Ceiling_LowerByValue */, null, null, false, REEL_TAG, 16, 224);
		cam = AjarCam(Actor.Spawn("AjarCam", mo.pos + (0, 0, 40)));
		cam.angle = mo.angle + 180;
		TexMan.SetCameraToTexture(cam, "AJREEL", 55);
		if (!clips.Size()) clips.Copy(kills);
		caption = clips.Size() ? "" : "Not once were you killed in a hall.";
	}

	// The camera: near where they fell, on them, from where they can be seen.
	void Aim(AjarClip c)
	{
		static const int tryAt[] = { 0, 40, -40, 80, -80, 130, -130, 180 };
		let mark = Actor.Spawn("AjarCam", c.at + (0, 0, 32));
		for (int i = 0; i < 8; i++)
		{
			Vector2 p = c.at.xy + Actor.AngleToVector(c.ang + tryAt[i], c.big ? 230 : 120);
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
				caption = c.big ? String.Format("HALL %d   -   %s", c.fight, c.what) : String.Format("HALL %d   -   %d of %d", c.fight, reelClip + 1, clips.Size());
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
		if (a is "AjarEcho" || a is "AjarZone" || a is "AjarCue" || a.bInvisible) return false;
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
		for (int r = tr.first[i]; r < to; r++)
		{
			int s = tr.slot[r];
			int k = puppetSlot.Find(s);
			if (tr.sf[r] < 0)
			{
				if (k < puppets.Size()) DropPuppet(k);
				continue;
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
		if (open) NewTake(players[consoleplayer].mo);
		trips = 0;
		at = 0;
		main = new("AjarTrack");
		boxes.Clear();
		slotCls.Clear();
		phase = LIVE;
		HallDoors(1);
		if (!(said & 1)) Say("A door with a clock on it leads out of the fight,\nand back into it where you left.");
		said |= 1;
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

	// The next wave, if it is due. Returns whether any is still to come.
	bool Cues(Actor mo, int left)
	{
		int wave = 0;
		let it = ThinkerIterator.Create("AjarCue");
		AjarCue c;
		while (c = AjarCue(it.Next())) if (c.args[0] == fight && !c.special1 && (!wave || c.args[1] < wave)) wave = c.args[1];
		if (!wave) return false;
		it = ThinkerIterator.Create("AjarCue");
		while (c = AjarCue(it.Next()))
		{
			if (c.args[0] != fight || c.special1 || c.args[1] != wave || left > c.args[2]) continue;
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

	bool Rescue(PlayerPawn mo)
	{
		if (over)
		{
			mo.bBuddha = true;
			mo.vel = (0, 0, 0);
			if (--over == 0)
			{
				// The level is left, on their feet: not frozen, in full health;
				// and if what comes next is this level again, as they first came.
				mo.player.cheats &= ~CF_TOTALLYFROZEN;
				mo.bBuddha = false;
				string next = level.nextmap != "" ? level.nextmap : level.mapname;
				level.ChangeLevel(next, 0, CHANGELEVEL_RESETHEALTH | (next ~== level.mapname ? CHANGELEVEL_RESETINVENTORY : 0));
			}
			return false;
		}
		bool can = phase != IDLE && (at > 0 || phase == LIVE);
		mo.bBuddha = can;
		if (!can || mo.health > 1) return false;
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
		return true;
	}

	// Out of a spare box and in its hall: its door shuts behind the player.
	void SpareTick(Actor mo, int k, int b)
	{
		if (!spareOut || k != spareOut / 10 || b != 0) return;
		let h = Doors();
		h.Link(BoxLine(spareOut / 10, spareOut % 10), 0, TIME_TEX);
		StepClear(mo, HallLine(k, 1));
		h.Link(HallLine(k, 1), 0, TIME_TEX);
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
		if (phase == IDLE)
		{
			// a big monster's death that won the fight is still being kept
			if (dueTic.Size()) { Snap(mo); KeepKills(); }
			SpareTick(mo, k, b);
			if (comeBack && k == fight && b == 0) Resume(mo);
			else if (!comeBack && k && b == 0 && won.Find(k) == won.Size() && mo.health > 0) Begin(k);
		}
		else if (phase == LIVE)
		{
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
				if (open) { RecordTake(PlayerPawn(mo)); PlayGhosts(mo); ot++; }
				else Record(main);
				// a hall with a show is empty until the count is over
				int go = HasShow(fight) ? SHOW_GO : 0;
				if (ft == go || (ft > go && level.maptime % 5 == 0))
				{
					int left = Left();
					if (!Cues(mo, left) && !left && at == 0) Win();
				}
			}
		}
		if (phase == REPLAY)
		{
			Show(fight, rt, mo);
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
		if (mode == 3 && level.mapname ~== "MAP31") SecretScript(PlayerPawn(mo));
		if (mode == 5 && level.mapname ~== "MAP31") OverScript(PlayerPawn(mo));
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
	// each hall in turn: in while it is empty and lit, the count, out by the
	// west door, the same beginning and the fight watched from box 1, back
	// in, and the fight won.
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
			if (v == 10) Check("theReelBegins", reel == 1 && clips.Size() == 2 && mo.bInvisible && ShowLight(1, false));
			if (v == 150)
			{
				let si = level.CreateSectorTagIterator(REEL_TAG);
				Sector sec = level.sectors[si.Next()];
				Check("theScreenIsDown", sec.CenterCeiling() == 32 && reel == 2 && cam && puppets.Size() > 3);
				int ck, cb;
				[ck, cb] = Where(cam.pos.xy);
				Check("aDeathInHall2", ck == 2 && clips[0].fight == 2 && clips[1].fight == 3);
			}
			if (v == 420) Check("goneToLightOnScreen", reel == 2 && reelClip == 0 && fallen && !fallen.bInvisible && fallen.alpha < 1);
			if (v == 440 || v == 460) { reelTic = 100000; }      // the rest, quickly
			if (v == 470) Check("theEnd", reel == 3);
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
		if (u == 60 && k) mo.GiveInventoryType(k == 1 ? "AjarKey1" : "AjarKey2");
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
			if (u == 82 + 230) Check("theyComeAgain", Left() > 5 && ghosts.Size() == 1 && ghosts[0]);
		}
		else
		{
			if (u == 80) Go(mo, x + 40, 128, 0, 180);
			if (u > 80 && u < 100) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		}
		if (u == 105)
		{
			Check("out" .. n, phase == (k == 1 ? LIVE : REPLAY) && at == 1 && mo.pos.z > 60);
			Console.Printf("AJARTEST followers=%d", pending.Size());
			Go(mo, x - 40, cy, 64, 0);          // at the glass
		}
		if (k == 2)                         // in the great hall: killed in the first box while watching
		{
			if (u == 110) mo.health = mo.player.health = 1;
			if (u == 112) Check("killedInABox", phase == REPLAY && at == 2 && trips == 2 && rt < 5 && mo.health == RESCUE_HEALTH && mo.pos.y > hh[k]);
		}
		if (u == 150)
		{
			let it = ThinkerIterator.Create("AjarLocker");
			AjarLocker l;
			while (l = AjarLocker(it.Next())) if (mo.Distance2D(l) < 200)
			{
				l.Used(mo);
				Check("cupboard" .. n, l.frame == 1);
			}
		}
		if (u < 240 + D) return;
		u -= D;
		if (u == 240)
		{
			Check("handedOver" .. n, phase == LIVE && at == (k == 2 ? 2 : 1) && !puppets.Size());
			if (k == 2) Go(mo, cx, hh[k] + 196, 64, 90);        // the north box
			else Go(mo, x - 200, cy, 64, 180);
		}
		if (u > 240 && u < 260) mo.vel.xy = Actor.AngleToVector(mo.angle, 8);
		if (k == 1 && u == 262) Check("itWentToADoor", ghosts.Size() == 1 && !ghosts[0]);
		if (u == 265) Check("backIn" .. n, at == 0 && mo.pos.x > x && mo.pos.z < 30);     // it may stand on a row of seats
		if (u == 266) Go(mo, cx, 40, 0, 90);        // out of the way of what comes in later
		if (k == 2)     // the great hall: no box of its own left, killed: into a box hall 1 did not use, and the fight begins again
		{
			if (u == 266) { trips = BoxCount(fight); HallDoors(0); mo.health = mo.player.health = 1; }
			if (u == 268) { let ci = ThinkerIterator.Create("AjarSnatch"); Actor c = Actor(ci.Next()); Check("goneToLight", c && abs(c.pos.x - cx) < 2 && abs(c.pos.y - 40) < 2 && c.alpha < 1); }
			if (u == 268) Check("killedIntoASpareBox", phase == IDLE && comeBack && spare.Size() == 3 && spareOut == 12 && !Left()
				&& mo.pos.x < 1200 && mo.pos.y > hh[0] && mo.health == RESCUE_HEALTH);
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
