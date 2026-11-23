// The paradox (PLAN.md, "The paradox: touching an earlier self ends the
// universe", "The paradox in fights", "The paradox: a bigger end" and "The
// paradox: a self that wound time is pale"; the tests MAP=PLATE MODE=5,
// MAP=PRESS MODE=4 and MODE=5, MAP=MAP31 MODE=8 tools/smoke.sh).
//
// Wherever an earlier self (an AjarGhost) walks (ParadoxHere): in any room
// of goes (an AjarZone of a hall with args[4] 2: MAP32's rooms 1, 2 and 5,
// the labs PLATE, TWOKEY and SHUT's room of goes; and a fight of goes that
// has been won and become a room of goes), and in any open fight while it is
// live (args[4] 1, MAP31's; args[4] 3, the fights of goes: MAP32's rooms 3
// and 4, SHUT's room B, PRESS), the player who touches one of their earlier
// selves has made a time paradox, and this universe is over. (A closed
// fight watched from a box has no earlier selves.)
//  * touching is the bodies overlapping: the two boxes (radius 16 each) and
//    their heights. Nothing is shown or heard before it;
//  * a copy counts only while its go is still running (its record is not
//    over: one whose time is up, or that was killed then and now runs to its
//    door, does not) and it stands in the hall; nothing counts while the
//    player is in a box. In a room of goes every go begins with the player
//    inside their copies (they all start in the box at the same tic), so a
//    copy cannot be touched until the player has once been clear of it in
//    this go (parted, kept per copy). It is cleared whenever a go begins
//    (GoTake in a room; NewTake in a fight: Retake, Resume, Begin, begin
//    anew, winding) and when the player goes on as an earlier self (GoOnAs:
//    whoever overlaps the spot they are put on is safe until they part).
//    One who walks a copy's path with it and never parts from it is safe;
//  * a copy that began its go by winding time (a wind plate; AjarTake.wound)
//    does not count through the stretch it wound over: it stands pale at the
//    plate, so that the next self can use the plate too. It is "not parted
//    from" all that while, so one who stands in it at the tic it wound to is
//    safe until they part;
//  * the player is dead at once, really (through god mode, buddha, armour and
//    powers: the damage is forced), and nothing of the room or the fight runs
//    any more (no rescue into a box, no going on as a copy, no beginning
//    anew, no spare box, no "the show is over"; trips, boxes and takes stay
//    as they were): the engine begins the level again when USE is pressed,
//    as after any death. The touched copy is gone.
// What is seen and heard (tics from the touch; every number is a constant
// below):
//  * 0 to PDX_HOLD, the held breath. Everything in the room stands dead
//    still: monsters awake or on the demo, their missiles, the copies (held
//    by hand each tic, ParadoxHold: no state of theirs runs, nothing moves;
//    the level is not frozen, so USE still begins it again). Where the two
//    met stand two white shapes of the player, flickering (the body is not
//    seen; the touched copy is gone). Along the record of every take of the
//    room, every PDX_ECHO_EVERY tics, a pale shape of the player appears
//    where that self was (only in the hall, at most PDX_ECHOES, thinned
//    evenly; over the first PDX_ECHO_IN tics), and all of them fall into
//    the point of touch, slowly and then fast, arriving at PDX_HOLD. A short
//    white flash (PDX_PRE_FLASH, gone in PDX_PRE_TICS) and the BFG's charge,
//    a little low, heard everywhere. The view is taken at once by a camera
//    at the player's eye (AjarParadoxCam), which holds still (so the view
//    does not drop as a dead player's does).
//  * PDX_HOLD, the blast: full white over the screen, fading over
//    PDX_WHITE tics; the BFG's, the rocket's and the barrel's blasts, and
//    PDX_ECHO_SOUND tics later the same at half pitch; a hard shake
//    (PDX_SHAKE, PDX_SHAKE_TICS, falling off); the two shapes flare into one
//    ball of light and are gone; the camera pulls back and up over PDX_CAM
//    tics, turning to look at the point of touch, to a place inside the
//    room's zones, under the ceiling, with a clear line to the touch: back
//    on the player's side if it can, else turned away from it (the farthest
//    back of ten ways), no higher above the touch than it is back from it
//    (where it cannot pull back it only rises). The white and the black are
//    drawn in RenderOverlay (a player's blend is not seen through another
//    camera), and so is the message (a midprint would be under them).
//  * PDX_HOLD to PDX_HOLD + PDX_WAVE, the wave: a ring of light runs out
//    over the floor to the farthest corner of the room's zones
//    (AjarParadoxRing, the sprite AJPR from tools/gfx_time.py). What it
//    reaches goes to light, its own shape white, rising and fading
//    (AjarParadoxGone, as AjarSnatch), and is gone: monsters living and dead,
//    the copies, missiles, things lying about; not the room's fixtures
//    (doors, frames, plates, lamps, levers, the look's things). Explosions
//    in three waves: with the ring, again PDX_WAVE2 tics behind it, and
//    columns of two or three, one above another, all over what the ring has
//    passed, until PDX_BOOM_END: the rocket's and the barrel's. A rocket's
//    blast is heard every 4 tics, fading.
//  * The dark: for PDX_FLICKER tics after the blast the light of each of the
//    room's sectors flickers between PDX_DIM and full; then, behind the
//    ring, it sinks to PDX_LOW over PDX_SINK tics. MAP32's look (works.zs)
//    stands down. From PDX_BLACK_AT after the blast the screen goes black
//    over PDX_BLACK tics and stays black.
//  * The message "PARADOX" (in red) with two lines, said at the blast and
//    again PARADOX_AGAIN tics later (each stays PDX_SAY_TICS, then fades);
//    once the screen is black, once more with "Press USE to begin again.",
//    which stays.
// Only the paradox's own random numbers (AjarParadox). What it spawns is
// capped (PDX_ECHOES, PDX_GONE_MAX, PDX_BOOM_PER_TIC).
// The tests read paradox, paradoxes, paradoxSaid, ParadoxAllGone and
// ParadoxDark; under ajar_autotest a line "AJARTEST info paradox ..." gives
// the tic, the copy and the place, and "AJARTEST info pdx n" each tic n after
// the touch (to place the screenshots).

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

// ... and the barrel's.
class AjarParadoxBarrel : AjarParadoxBlast
{
	States
	{
	Spawn:
		BEXP C 5 Bright;
		BEXP D 5 Bright;
		BEXP E 6 Bright;
		Stop;
	}
}

// A white shape of the player or of a thing: its sprite is set when it is
// spawned (the two that met, the pale ones of every moment).
class AjarParadoxShape : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH +NOTELEPORT RenderStyle "AddStencil"; StencilColor "FFFFFF"; Alpha 1; }
	States { Spawn: TNT1 A -1 Bright; Stop; }
}

// What the ring reaches goes to light: its own shape, white, rising and fading.
class AjarParadoxGone : AjarParadoxShape
{
	States
	{
	Spawn:
		TNT1 A 0;
	Fade:
		#### # 1 Bright A_FadeOut(0.03);
		Loop;
	}
}

// The ring of light on the floor (flat; its scale is set each tic).
class AjarParadoxRing : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH +FLATSPRITE RenderStyle "Add"; Alpha 1; }
	States { Spawn: AJPR A -1 Bright; Stop; }
}

// The ball the two white shapes flare into.
class AjarParadoxBall : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +DONTSPLASH RenderStyle "Add"; Alpha 1; }
	States { Spawn: AJPB A -1 Bright; Stop; }
}

// The view, once the universe is over: at the player's eye, then back and up.
class AjarParadoxCam : Actor
{
	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +INVISIBLE +DONTSPLASH CameraHeight 0; Height 2; Radius 1; }
	States { Spawn: TNT1 A -1; Stop; }
}

extend class AjarTimeHandler
{
	bool paradox;               // this universe is over
	int paradoxes;              // how many times (tests: once)
	int paradoxTic;             // level.maptime of the touch
	int paradoxCopy;            // the go of the copy that was touched (from 1)
	int paradoxSaid;            // how often the message has been said
	Vector3 paradoxAt;          // where
	double paradoxReach;        // how far the ring goes: to the farthest corner of the room's zones
	Array<bool> parted;         // parted[i]: the player has been clear of the copy of takes[i] in this go

	// --- the sequence (tics from the touch) ---
	const PDX_HOLD = 18;            // the held breath; then the blast
	const PDX_PRE_FLASH = 0.6;      // the flash at the touch...
	const PDX_PRE_TICS = 8;         // ... gone in so many tics
	const PDX_ECHO_EVERY = 8;       // a pale shape every so many tics of each take's record
	const PDX_ECHOES = 250;         // at most so many (thinned evenly)
	const PDX_ECHO_IN = 6;          // they appear over the first so many tics
	const PDX_ECHO_ALPHA = 0.5;     // (pale on a lit wall is all but unseen: additive)
	const PDX_ECHO_NEAR = 160;      // within 48 + this of the camera they fade, to nothing at 48 (they fall
	                                // into the point in front of the eye: 250 there make the screen white)
	const PDX_SELF_LO = 0.15;       // the two white shapes flicker between these (additive on a lit wall)
	const PDX_SELF_HI = 0.4;
	const PDX_WHITE = 60;           // the blast's white fades over so many tics
	const PDX_ECHO_SOUND = 5;       // the deep echo of the blast, so many tics after it
	const PDX_SHAKE = 12;           // the shake's strength (twice the old)...
	const PDX_SHAKE_TICS = 90;      // ... and length, falling off
	const PDX_BALL_TICS = 10;       // the ball of light flares and is gone
	const PDX_BALL_SIZE = 3.0;      // its last scale
	const PDX_CAM = 40;             // the camera pulls back over so many tics...
	const PDX_CAM_BACK = 384;       // ... at most so far from the point of touch...
	const PDX_CAM_UP = 176;         // ... and so high above it
	const PDX_WAVE = 45;            // the ring runs to the room's farthest corner in so many tics
	const PDX_RING_PX = 112;        // the ring's radius in its sprite (AJPR)
	const PDX_WAVE2 = 20;           // the second wave of explosions, so many tics behind the ring
	const PDX_BOOM_END = 110;       // the last explosions, so many tics after the blast
	const PDX_BOOM_PER_TIC = 22;    // at most so many explosions a tic
	const PDX_GONE_MAX = 160;       // at most so many shapes going to light at once (the rest just go)
	const PDX_FLICKER = 30;         // the room's light flickers for so many tics after the blast...
	const PDX_DIM = 40;             // ... between this and full
	const PDX_SINK = 40;            // then sinks behind the ring over so many tics...
	const PDX_LOW = 16;             // ... to this
	const PDX_BLACK_AT = 120;       // the screen goes black from so many tics after the blast...
	const PDX_BLACK = 50;           // ... over so many
	const PARADOX_AGAIN = 90;       // the message is said again after so many tics

	// --- what the sequence holds ---
	Array<Actor> pdxHeld;           // the room's things held still, and where
	Array<double> pdxHx, pdxHy, pdxHz;
	Array<Actor> pdxEcho;           // the pale shapes, where each starts and from which tic it falls
	Array<double> pdxEx, pdxEy, pdxEz;
	Array<int> pdxEt;
	Array<int> pdxEchoTake, pdxEchoTic;     // (before they are spawned: which take, which tic of it)
	Actor pdxMe, pdxIt;             // the two white shapes
	AjarParadoxBall pdxBall;
	AjarParadoxRing pdxRing;
	AjarParadoxCam pdxCam;
	Vector3 pdxEye, pdxCamTo;
	double pdxEyeAng, pdxEyePitch;
	Array<int> pdxSec, pdxSecLight; // the room's sectors, their light before
	Array<double> pdxSecDist;       // and how far each one's middle is from the touch
	double pdxFloor;                // the floor under the touch
	int pdxBooms[16];               // explosions spawned in each of the last 16 tics
	int pdxGoneTic[64];             // shapes going to light spawned in each recent tic

	// Where the rule holds: wherever an earlier self walks. Any room of goes
	// (`goes`: a room of goes proper, and a fight of goes that has been won
	// and become one, goesWon), and any open fight while it is live (MAP31's
	// open fights, and the fights of goes before they are won: MAP32's rooms
	// 3 and 4, SHUT's room B, PRESS). Not a closed fight watched from a box:
	// it has no earlier selves.
	bool ParadoxHere()
	{
		return goes || (open && phase == LIVE);
	}

	static bool Touching(Actor a, Actor b)
	{
		double r = a.radius + b.radius;
		return abs(a.pos.x - b.pos.x) < r && abs(a.pos.y - b.pos.y) < r
			&& a.pos.z < b.pos.z + b.height && b.pos.z < a.pos.z + a.height;
	}

	// Every tic of a room of goes (GoesTick) and of a live open fight (WorldTick),
	// after the earlier selves are where they are (PlayGhosts).
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
			// it wound time and is not there yet (pale: GhostLook, time.zs); and
			// whoever stands in it when it is, is safe until they part
			if (ot < takes[i].wound) { parted[i] = false; continue; }
			if (!Touching(mo, g)) { parted[i] = true; continue; }
			if (!parted[i] || !inHall) continue;
			int gk, gb;
			[gk, gb] = Where(g.pos.xy);
			if (gk != fight || gb != 0) continue;
			EndUniverse(mo, i);
			return;
		}
	}

	// `why` (third.zs): what is said instead of "You touched your earlier
	// self." (a line break in it makes two lines). `apart`: the copy is not
	// touched but far off (a self that came where it could not have); the
	// end is where it is, and the player only dies. i < 0: no copy at all
	// (coming too late): the end is where the player is.
	string paradoxWhy;
	void EndUniverse(PlayerPawn mo, int i, string why = "", bool apart = false)
	{
		AjarGhost g = i >= 0 && i < ghosts.Size() ? ghosts[i] : null;
		paradox = true;
		paradoxes++;
		paradoxTic = level.maptime;
		paradoxCopy = i + 1;
		paradoxWhy = why;
		paradoxAt = !g ? mo.pos : apart ? g.pos : ((mo.pos.xy + g.pos.xy) / 2, max(mo.pos.z, g.pos.z));
		Vector3 gp = g ? g.pos : mo.pos;
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info paradox t=%d go=%d ot=%d copy=%d at=(%d,%d,%d) me=(%d,%d,%d)", level.maptime, takes.Size(), ot, i + 1,
				gp.x, gp.y, gp.z, mo.pos.x, mo.pos.y, mo.pos.z);
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
		pdxFloor = level.PointInSector(paradoxAt.xy).floorplane.ZAtPoint(paradoxAt.xy);
		// the two that met: white shapes of them where they stood (before the body falls)
		pdxMe = g && apart ? null : ParadoxShape(mo, mo.pos, mo.angle);
		pdxIt = g ? ParadoxShape(g, g.pos, g.angle) : null;
		// the view: a camera at the player's eye, which holds still until the blast
		pdxEye = (mo.pos.xy, mo.player.viewz);
		pdxEyeAng = mo.angle;
		pdxEyePitch = mo.pitch;
		pdxCam = AjarParadoxCam(Actor.Spawn("AjarParadoxCam", pdxEye));
		if (pdxCam)
		{
			pdxCam.angle = pdxEyeAng;
			pdxCam.pitch = pdxEyePitch;
			pdxCamTo = ParadoxCamTo(mo);
			mo.player.camera = pdxCam;
		}
		// the copy is gone in it
		if (g) { g.Destroy(); ghosts[i] = null; }
		// the player is dead: nothing spares them
		mo.player.cheats &= ~(CF_GODMODE | CF_GODMODE2 | CF_BUDDHA | CF_BUDDHA2 | CF_FROZEN | CF_TOTALLYFROZEN);
		mo.bBuddha = false;
		mo.bInvulnerable = false;
		mo.bNoDamage = false;
		stand = 0;
		mo.DamageMobj(null, null, Actor.TELEFRAG_DAMAGE, 'Paradox', DMG_FORCED | DMG_NO_ARMOR | DMG_THRUSTLESS);
		mo.player.damagecount = 0;          // (no red of a hit: the white is drawn, RenderOverlay)
		mo.player.bonuscount = 0;
		mo.vel = (0, 0, 0);
		mo.bInvisible = pdxMe != null;      // (its white shape stands there)
		mo.A_StartSound("weapons/bfgf", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE, 0.8);
		Say("");                            // (a hint on the screen goes)
		// the room stands still; every moment of the player's in it, at once
		ParadoxHold(true);
		ParadoxEchoesPlan();
		ParadoxRoomSectors();
		if (CVar.GetCVar("ajar_autotest").GetInt())
			Console.Printf("AJARTEST info paradox held=%d echoes=%d sectors=%d reach=%d cam=(%d,%d,%d)", pdxHeld.Size(), pdxEchoTake.Size(),
				pdxSec.Size(), paradoxReach, pdxCamTo.x, pdxCamTo.y, pdxCamTo.z);
	}

	AjarParadoxShape ParadoxShape(Actor of, Vector3 at, double ang)
	{
		let s = AjarParadoxShape(Actor.Spawn("AjarParadoxShape", at));
		if (!s) return null;
		s.sprite = of.sprite;
		s.frame = of.frame;
		s.angle = ang;
		s.scale = of.scale;
		s.translation = of.translation;
		return s;
	}

	// Is a thing one of the room's that are held and go to light: a monster
	// (living or not), a copy, a missile, a body, a thing lying about. (Not
	// the room's fixtures: doors, frames, plates, lamps, levers, the look's
	// things; not the player, not the paradox's own.)
	bool ParadoxTakes(Actor a)
	{
		if (!a || a.player || a is "AjarParadoxShape" || a is "AjarParadoxBlast" || a is "AjarParadoxRing"
			|| a is "AjarParadoxBall" || a is "AjarParadoxCam") return false;
		bool what = a.bIsMonster || a is "AjarGhost" || a.bMissile || a.bCorpse
			|| (a is "Inventory" && !Inventory(a).owner);
		if (!what) return false;
		int k, b;
		[k, b] = Where(a.pos.xy);
		return k == fight;
	}

	// Hold the room still: every tic, each of its things where it was, not
	// moving, its state not running (tics -1). New ones (a missile fired at the
	// touch) are taken in while `look`. The level itself is not frozen.
	void ParadoxHold(bool look)
	{
		if (look)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next()))
			{
				if (!ParadoxTakes(a) || pdxHeld.Find(a) < pdxHeld.Size()) continue;
				pdxHeld.Push(a); pdxHx.Push(a.pos.x); pdxHy.Push(a.pos.y); pdxHz.Push(a.pos.z);
			}
		}
		for (int i = 0; i < pdxHeld.Size(); i++)
		{
			Actor a = pdxHeld[i];
			if (!a) continue;
			a.vel = (0, 0, 0);
			a.tics = -1;
			if (a.pos.x != pdxHx[i] || a.pos.y != pdxHy[i] || a.pos.z != pdxHz[i]) a.SetOrigin((pdxHx[i], pdxHy[i], pdxHz[i]), false);
		}
	}

	// Every PDX_ECHO_EVERY tics of every take's record, where it was in the
	// hall: at most PDX_ECHOES of them, thinned evenly.
	void ParadoxEchoesPlan()
	{
		Array<int> tk, tt;
		for (int i = 0; i < takes.Size(); i++)
		{
			AjarTake t = takes[i];
			for (int j = 0; j < t.x.Size(); j += PDX_ECHO_EVERY)
			{
				int k, b;
				[k, b] = Where((t.x[j], t.y[j]));
				if (k != fight || b != 0) continue;
				tk.Push(i); tt.Push(j);
			}
		}
		int n = tk.Size(), m = min(n, PDX_ECHOES);
		for (int e = 0; e < m; e++)
		{
			int s = n > m ? e * n / m : e;
			pdxEchoTake.Push(tk[s]); pdxEchoTic.Push(tt[s]);
		}
	}

	void ParadoxEchoes(int t)
	{
		int m = pdxEchoTake.Size();
		// they appear over the first PDX_ECHO_IN tics
		if (t >= 1 && t <= PDX_ECHO_IN)
		{
			int from = m * (t - 1) / PDX_ECHO_IN, to = m * t / PDX_ECHO_IN;
			for (int e = from; e < to; e++)
			{
				AjarTake tk = takes[pdxEchoTake[e]];
				int j = pdxEchoTic[e];
				Vector3 p = (tk.x[j], tk.y[j], tk.z[j]);
				let s = AjarParadoxShape(Actor.Spawn("AjarParadoxShape", p));
				if (!s) continue;
				s.sprite = Actor.GetSpriteIndex("PLAY");
				s.frame = (j / PDX_ECHO_EVERY) % 4;
				s.angle = tk.ang[j];
				s.alpha = PDX_ECHO_ALPHA;
				pdxEcho.Push(s); pdxEx.Push(p.x); pdxEy.Push(p.y); pdxEz.Push(p.z); pdxEt.Push(t);
			}
		}
		// ... and fall into the point of touch, slowly and then fast, arriving at PDX_HOLD
		for (int e = 0; e < pdxEcho.Size(); e++)
		{
			Actor s = pdxEcho[e];
			if (!s) continue;
			if (t >= PDX_HOLD) { s.Destroy(); continue; }
			double f = double(t - pdxEt[e]) / (PDX_HOLD - pdxEt[e]);
			f = f * f * f;
			Vector3 from = (pdxEx[e], pdxEy[e], pdxEz[e]);
			s.SetOrigin(from + (paradoxAt - from) * f, true);
			double near = clamp(((s.pos + (0, 0, 28) - pdxEye).Length() - 48) / PDX_ECHO_NEAR, 0., 1.);
			s.alpha = (PDX_ECHO_ALPHA * frandom[AjarParadox](0.8, 1.2) + 0.25 * f) * near * near;
		}
		if (t >= PDX_HOLD) pdxEcho.Clear();
	}

	// The camera's end: back from the point of touch on the player's side and
	// up, as far as it can be inside the room's zones, under the ceiling, with
	// a clear line to the touch; where it cannot pull back it only rises.
	Vector3 ParadoxCamTo(PlayerPawn mo)
	{
		Vector2 d = pdxEye.xy - paradoxAt.xy;
		if (d.Length() < 1) d = -Actor.AngleToVector(mo.angle);
		double side = VectorAngle(d.x, d.y);
		Vector3 aim = (paradoxAt.xy, paradoxAt.z + 32), best = pdxEye;
		double bestScore = -1;
		// the player's side first, then turning away from it both ways: the farthest back wins
		static const double turn[] = { 0, 30, -30, 60, -60, 90, -90, 135, -135, 180 };
		for (int i = 0; i < turn.Size(); i++)
		{
			Vector2 dir = Actor.AngleToVector(side + turn[i]);
			for (double back = PDX_CAM_BACK; back >= 0; back -= 32)
			{
				Vector2 p = back < 1 ? pdxEye.xy : paradoxAt.xy + dir * back;
				int k, b;
				[k, b] = Where(p);
				if (k != fight) continue;
				Sector sec = level.PointInSector(p);
				double fl = sec.floorplane.ZAtPoint(p), ce = sec.ceilingplane.ZAtPoint(p);
				bool found = false;
				// not higher than it is back (the touch seen from no steeper than about 45 degrees)
				for (double up = min(PDX_CAM_UP, back + 48); up >= 0; up -= 16)
				{
					double z = min(paradoxAt.z + up, ce - 16);
					if (z < fl + 24 || (z < pdxEye.z - 1 && up > 0)) continue;
					if (!ParadoxClear((p, z), aim) || !ParadoxClear(pdxEye, (p, z))) continue;
					double score = back + 0.3 * (z - paradoxAt.z) - 0.1 * abs(turn[i]);
					if (score > bestScore) { bestScore = score; best = (p, z); }
					found = true;
					break;
				}
				if (found) break;
			}
		}
		return best;
	}

	// a clear line from p to q: every 16 units of it in the level, between a floor and a ceiling
	bool ParadoxClear(Vector3 p, Vector3 q)
	{
		double len = (q - p).Length();
		int n = max(1, int(len / 16));
		for (int i = 0; i <= n; i++)
			if (!level.IsPointInLevel(p + (q - p) * i / n)) return false;
		return true;
	}

	void ParadoxCamera(int t)
	{
		if (!pdxCam) return;
		let pl = players[consoleplayer];
		if (pl.mo && pl.camera != pdxCam && pl.health <= 0) pl.camera = pdxCam;
		if (t < PDX_HOLD) return;
		double f = min(1., double(t - PDX_HOLD) / PDX_CAM);
		double e = 1 - (1 - f) * (1 - f);
		Vector3 p = pdxEye + (pdxCamTo - pdxEye) * e;
		pdxCam.SetOrigin(p, true);
		Vector3 d = (paradoxAt.xy, paradoxAt.z + 32) - p;
		double ang = VectorAngle(d.x, d.y), pit = atan2(-d.z, max(1., d.xy.Length()));
		pdxCam.angle = pdxEyeAng + Actor.DeltaAngle(pdxEyeAng, ang) * e;
		pdxCam.pitch = pdxEyePitch + (pit - pdxEyePitch) * e;
	}

	// The room's sectors (their middles in its zones), their light, how far from the touch.
	void ParadoxRoomSectors()
	{
		for (int i = 0; i < level.sectors.Size(); i++)
		{
			Sector s = level.sectors[i];
			int k, b;
			[k, b] = Where(s.centerspot);
			if (k != fight) continue;
			pdxSec.Push(i); pdxSecLight.Push(s.lightlevel); pdxSecDist.Push((s.centerspot - paradoxAt.xy).Length());
		}
	}

	void ParadoxLights(int t)
	{
		int d = t - PDX_HOLD;
		if (d < 0) return;
		for (int i = 0; i < pdxSec.Size(); i++)
		{
			int want;
			if (d <= PDX_FLICKER) want = random[AjarParadox](PDX_DIM, 255);
			else
			{
				double reach = paradoxReach > 0 ? PDX_WAVE * min(1., pdxSecDist[i] / paradoxReach) : 0;
				double from = max(double(PDX_FLICKER), reach);
				double f = clamp((d - from) / PDX_SINK, 0., 1.);
				want = int(pdxSecLight[i] + (PDX_LOW - pdxSecLight[i]) * f + 0.5);
			}
			Sector s = level.sectors[pdxSec[i]];
			if (s.lightlevel != want) s.SetLightLevel(want);
		}
	}

	// How far the ring has run d tics after the blast.
	double ParadoxRingAt(int d)
	{
		if (d < 0) return 0;
		return paradoxReach * min(1., double(d) / PDX_WAVE);
	}

	void ParadoxWave(int t)
	{
		int d = t - PDX_HOLD;
		if (d < 0) return;
		if (d > PDX_WAVE + 12) { if (pdxRing) pdxRing.Destroy(); return; }
		double r = ParadoxRingAt(d);
		if (!pdxRing && d <= PDX_WAVE) pdxRing = AjarParadoxRing(Actor.Spawn("AjarParadoxRing", (paradoxAt.xy, pdxFloor + 1)));
		if (pdxRing)
		{
			double sc = max(0.05, r / PDX_RING_PX);
			pdxRing.scale = (sc, sc);
			pdxRing.alpha = d <= PDX_WAVE ? 1. : 1. - (d - PDX_WAVE) / 12.;
		}
		// what it reaches goes to light (at its end, all that is left)
		pdxGoneTic[d & 63] = 0;
		for (int i = 0; i < pdxHeld.Size(); i++)
		{
			Actor a = pdxHeld[i];
			if (!a) continue;
			if (d < PDX_WAVE && (a.pos.xy - paradoxAt.xy).Length() > r) continue;
			ParadoxGo(a, d);
			pdxHeld[i] = null;
		}
	}

	void ParadoxGo(Actor a, int d)
	{
		int live = 0;
		for (int i = 0; i < 34 && i <= d; i++) live += pdxGoneTic[(d - i) & 63];
		if (live < PDX_GONE_MAX && !a.bInvisible && a.sprite != Actor.GetSpriteIndex("TNT1"))
		{
			let s = AjarParadoxGone(Actor.Spawn("AjarParadoxGone", a.pos));
			if (s)
			{
				s.sprite = a.sprite; s.frame = a.frame; s.angle = a.angle; s.scale = a.scale; s.translation = a.translation;
				s.alpha = 0.95;
				s.vel.z = 1;
				pdxGoneTic[d & 63]++;
			}
		}
		for (int i = 0; i < ghosts.Size(); i++) if (ghosts[i] == a) ghosts[i] = null;
		a.Destroy();
	}

	// An explosion at p, at height z (or on the floor or a little above it), if p is in the room.
	bool ParadoxBlast(Vector2 p, double size, double z, int d)
	{
		if (pdxBooms[d & 15] >= PDX_BOOM_PER_TIC) return false;
		int k, b;
		[k, b] = Where(p);
		if (k != fight) return false;
		Sector sec = level.PointInSector(p);
		double fl = sec.floorplane.ZAtPoint(p), ce = sec.ceilingplane.ZAtPoint(p);
		if (ce - fl < 32 || !level.IsPointInLevel((p, fl + 1))) return false;
		if (z < fl) z = fl + frandom[AjarParadox](4, min(64, ce - fl - 24));
		if (z > ce - 24) return false;
		let a = Actor.Spawn(random[AjarParadox](0, 2) ? "AjarParadoxBlast" : "AjarParadoxBarrel", (p, z));
		if (!a) return false;
		pdxBooms[d & 15]++;
		a.scale *= size * frandom[AjarParadox](0.8, 1.4);
		a.vel.z = frandom[AjarParadox](0, 1.5);
		a.tics -= random[AjarParadox](0, 3);
		return true;
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

	void ParadoxBooms(int t, PlayerPawn mo)
	{
		int d = t - PDX_HOLD;
		if (d < 0 || d > PDX_BOOM_END) return;
		pdxBooms[d & 15] = 0;
		// with the ring, and again PDX_WAVE2 tics behind it
		for (int w = 0; w < 2; w++)
		{
			int dw = d - w * PDX_WAVE2;
			if (dw < 0 || dw > PDX_WAVE) continue;
			double r = ParadoxRingAt(dw);
			int n = clamp(int(r / 64), 3, w ? 7 : 10);
			for (int j = 0; j < n; j++)
				ParadoxBlast(paradoxAt.xy + Actor.AngleToVector(frandom[AjarParadox](0, 360), r + frandom[AjarParadox](-32, 32)),
					w ? frandom[AjarParadox](1.2, 2.4) : frandom[AjarParadox](1.5, 3.0), -32768, d);
		}
		// columns of two or three, one above another, all over what the ring has passed
		double passed = ParadoxRingAt(d);
		int cols = int(3 * (1 - double(d) / PDX_BOOM_END) + 0.7);
		for (int c = 0; c < cols; c++)
		{
			bool ok;
			Vector2 p;
			[ok, p] = ParadoxInRoom(passed);
			if (!ok) continue;
			double fl = level.PointInSector(p).floorplane.ZAtPoint(p);
			int h = random[AjarParadox](2, 3);
			for (int i = 0; i < h; i++)
				if (!ParadoxBlast(p + (frandom[AjarParadox](-8, 8), frandom[AjarParadox](-8, 8)), frandom[AjarParadox](1.2, 2.2), fl + 16 + 56 * i, d)) break;
		}
		if (d % 4 == 0)
			mo.A_StartSound("weapons/rocklx", CHAN_AUTO, CHANF_DEFAULT, max(0.1, 0.9 - 0.8 * d / PDX_BOOM_END), ATTN_NONE);
	}

	// The blast's sounds, everywhere (pitch 0: as they are).
	void ParadoxBang(PlayerPawn mo, double pitch)
	{
		mo.A_StartSound("weapons/bfgx", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE, pitch);
		mo.A_StartSound("weapons/rocklx", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE, pitch);
		mo.A_StartSound("world/barrelx", CHAN_AUTO, CHANF_DEFAULT, 1, ATTN_NONE, pitch);
	}

	// The two white shapes flicker; at the blast they flare into one ball of light and are gone.
	void ParadoxSelves(int t)
	{
		if (t < PDX_HOLD)
		{
			// (faint: the copy's stands a step from the eye, and at more it is a white wall before it)
			if (pdxMe) pdxMe.alpha = frandom[AjarParadox](PDX_SELF_LO, PDX_SELF_HI);
			if (pdxIt) pdxIt.alpha = frandom[AjarParadox](PDX_SELF_LO, PDX_SELF_HI);
			return;
		}
		if (t == PDX_HOLD)
		{
			if (pdxMe) pdxMe.Destroy();
			if (pdxIt) pdxIt.Destroy();
			pdxBall = AjarParadoxBall(Actor.Spawn("AjarParadoxBall", (paradoxAt.xy, paradoxAt.z + 28)));
		}
		if (!pdxBall) return;
		double f = double(t - PDX_HOLD) / PDX_BALL_TICS;
		if (f >= 1) { pdxBall.Destroy(); return; }
		double sc = 0.6 + (PDX_BALL_SIZE - 0.6) * sqrt(f);
		pdxBall.scale = (sc, sc);
		pdxBall.alpha = 1 - f * f;
	}

	// The message is drawn in RenderOverlay (a midprint would be under the
	// white and the black): it stays PDX_SAY_TICS and fades over PDX_SAY_FADE;
	// the last one, on the black, stays.
	int pdxSaidTic;
	bool pdxSaidLast;
	const PDX_SAY_TICS = 105;
	const PDX_SAY_FADE = 35;

	void ParadoxSay(bool last = false)
	{
		paradoxSaid++;
		pdxSaidTic = level.maptime;
		pdxSaidLast = last;
		if (CVar.GetCVar("ajar_autotest").GetInt()) Console.Printf("AJARTEST info paradox said %d%s", paradoxSaid, last ? " (press USE)" : "");
	}

	ui void ParadoxText(RenderEvent e)
	{
		if (!paradoxSaid) return;
		double s = level.maptime - 1 - pdxSaidTic + e.FracTic;
		double a = pdxSaidLast ? min(1., s / 8) : clamp(1 - (s - PDX_SAY_TICS) / PDX_SAY_FADE, 0., 1.);
		if (a <= 0) return;
		Array<string> lines;
		lines.Push("PARADOX");
		lines.Push("");
		if (paradoxWhy == "") lines.Push("You touched your earlier self.");
		else
		{
			Array<string> why;
			paradoxWhy.Split(why, "\n");
			for (int i = 0; i < why.Size(); i++) lines.Push(why[i]);
		}
		lines.Push("This universe is over.");
		if (pdxSaidLast) { lines.Push(""); lines.Push("Press USE to begin again."); }
		int n = lines.Size();
		double y = 150;
		for (int i = 0; i < n; i++)
		{
			Font f = i == 0 ? BigFont : SmallFont;
			string l = lines[i];
			if (l != "") Screen.DrawText(f, Font.CR_RED, 320 - f.StringWidth(l) / 2, y, l,
				DTA_VirtualWidth, 640, DTA_VirtualHeight, 400, DTA_Alpha, a);
			y += i == 0 ? 22 : 12;
		}
	}

	// Every tic once the universe is over. Nothing else of the room or the fight runs.
	void ParadoxTick(PlayerPawn mo)
	{
		int t = level.maptime - paradoxTic;
		bool test = CVar.GetCVar("ajar_autotest").GetInt() != 0;
		if (test && t <= PDX_HOLD + 200) Console.Printf("AJARTEST info pdx %d", t);
		ParadoxHold(t <= PDX_HOLD);
		ParadoxEchoes(t);
		ParadoxSelves(t);
		ParadoxCamera(t);
		if (t == PDX_HOLD)
		{
			ParadoxBang(mo, 0);
			mo.A_QuakeEx(PDX_SHAKE, PDX_SHAKE, PDX_SHAKE * 2 / 3, PDX_SHAKE_TICS, 0, 8192, "", QF_SCALEDOWN);
			ParadoxSay();
		}
		if (t == PDX_HOLD + PDX_ECHO_SOUND) ParadoxBang(mo, 0.5);
		ParadoxWave(t);
		ParadoxBooms(t, mo);
		ParadoxLights(t);
		if (t == PDX_HOLD + PARADOX_AGAIN) ParadoxSay();
		if (t == PDX_HOLD + PDX_BLACK_AT + PDX_BLACK) ParadoxSay(true);
		if (test && t == PDX_HOLD + 180) Console.Printf("AJARTEST info paradox allGone=%d dark=%d sectors=%d cam=(%d,%d,%d)",
			ParadoxAllGone(), ParadoxDark(), pdxSec.Size(), pdxCamTo.x, pdxCamTo.y, pdxCamTo.z);
	}

	// --- drawn (RenderOverlay): the white of the touch and of the blast, then the black ---
	clearscope double ParadoxWhite(double t)
	{
		if (t < 0) return 0;
		if (t < PDX_PRE_TICS) return PDX_PRE_FLASH * (1 - t / PDX_PRE_TICS);
		if (t >= PDX_HOLD && t < PDX_HOLD + PDX_WHITE) { double f = 1 - (t - PDX_HOLD) / PDX_WHITE; return f * f; }
		return 0;
	}

	clearscope double ParadoxBlack(double t)
	{
		return clamp((t - PDX_HOLD - PDX_BLACK_AT) / PDX_BLACK, 0., 1.);
	}

	ui void ParadoxOverlay(RenderEvent e)
	{
		if (!paradox) return;
		double t = level.maptime - 1 - paradoxTic + e.FracTic;     // (the tic last run: maptime is already on)
		int w = Screen.GetWidth(), h = Screen.GetHeight();
		double b = ParadoxBlack(t), wh = ParadoxWhite(t);
		if (b > 0) Screen.Dim("black", b, 0, 0, w, h);
		if (wh > 0) Screen.Dim("white", wh, 0, 0, w, h);
		ParadoxText(e);
	}

	// --- for the tests ---
	// no living monster and no copy left in the room
	bool ParadoxAllGone()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!(a is "AjarGhost") && !(a.bIsMonster && a.health > 0)) continue;
			int k, b;
			[k, b] = Where(a.pos.xy);
			if (k == fight) return false;
		}
		return true;
	}

	// the screen black and the room's sectors at their low light
	bool ParadoxDark()
	{
		if (ParadoxBlack(level.maptime - paradoxTic) < 1) return false;
		for (int i = 0; i < pdxSec.Size(); i++) if (level.sectors[pdxSec[i]].lightlevel != PDX_LOW) return false;
		return pdxSec.Size() > 0;
	}
}
