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
		let it = ThinkerIterator.Create("AjarZone");
		Actor a;
		while (a = Actor(it.Next()))
		{
			zf.Push(a.args[0]); zb.Push(a.args[1]);
			zx.Push(a.pos.x); zy.Push(a.pos.y); zw.Push(a.args[2]); zh.Push(a.args[3]);
		}
		let h = Doors();
		for (int k = 1; k < 10; k++)
		{
			for (int j = 1; h.FindLine(HallLine(k, j)); j++) h.Link(HallLine(k, j), 0, TIME_TEX);
			for (int n = 1; h.FindLine(BoxLine(k, n)); n++) h.Link(BoxLine(k, n), 0, TIME_TEX);
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

	void Show(AjarTrack tr, int i)
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
		while (c = AjarCue(it.Next())) if (c.args[0] == fight && (!wave || c.args[1] < wave)) wave = c.args[1];
		if (!wave) return false;
		it = ThinkerIterator.Create("AjarCue");
		while (c = AjarCue(it.Next()))
		{
			if (c.args[0] != fight || c.args[1] != wave || left > c.args[2]) continue;
			class<Actor> cls = AjarHandler.AmbushClass(c.args[3]);
			if (c.args[3] == 64) cls = "Archvile";
			if (c.args[3] == 16) cls = "Cyberdemon";
			if (!cls) { c.Destroy(); continue; }
			Actor m = Actor.Spawn(cls, c.pos, ALLOW_REPLACE);
			if (!m) continue;
			if (!m.TestMobjLocation()) { m.ClearCounters(); m.Destroy(); continue; }
			m.angle = c.angle;
			Actor.Spawn("TeleportFog", c.pos, ALLOW_REPLACE);
			m.target = mo;
			if (m.SeeState) m.SetState(m.SeeState);
			m.A_StartSound(m.SeeSound, CHAN_VOICE);
			c.Destroy();
		}
		return true;
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
		while (pending.Size() < 2 && (a = Actor(it.Next())))
		{
			if (!a.bIsMonster || a.health <= 0 || a.target != mo || a.radius > 31 || a.height > 96 || a.bFloat) continue;
			if ((a.pos.xy - mid).Length() > FOLLOW_NEAR || !Counts(a, 0)) continue;
			pending.Push(a); pendingTics.Push(a.tics);
		}
		Freeze(mo);
		for (int i = 0; i < pending.Size(); i++) { pending[i].tics = -1; pending[i].bInvisible = true; }
		trips++;
		at = trips;
		HallDoors(0);
		let tr = new("AjarTrack");
		tr.box = trips;
		boxes.Push(tr);
		rt = 0;
		phase = REPLAY;
		if (!(said & 2)) Say("It is before the fight. Through the glass: yourself.\nThis door opens when the fight is where you left it.");
		else if (trips == BoxCount(fight)) Say("The last box. After this the doors stay shut.");
		said |= 2;
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
		HallDoors(trips + 1);
	}

	void Win()
	{
		won.Push(fight);
		HallDoors(0);
		phase = IDLE;
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
		int k, b;
		[k, b] = Where(mo.pos.xy);
		if (phase == IDLE)
		{
			if (k && b == 0 && won.Find(k) == won.Size() && mo.health > 0) Begin(k);
		}
		else if (phase == LIVE)
		{
			if (mo.health > 0 && k == fight)
			{
				if (at == 0 && b == trips + 1) Leave(mo);
				else if (at > 0 && b == 0) Back();
			}
			if (phase == LIVE)
			{
				Record(main);
				if (level.maptime % 5 == 0)
				{
					int left = Left();
					if (!Cues(mo, left) && !left && at == 0) Win();
				}
			}
		}
		if (phase == REPLAY)
		{
			Show(main, rt);
			for (int n = 0; n < boxes.Size() - 1; n++)
			{
				if (rt < boxes[n].first.Size()) Show(boxes[n], rt);
				else if (rt == boxes[n].first.Size()) DropPuppets(n + 1);
			}
			Hold();
			Arrive();
			Record(boxes[boxes.Size() - 1]);
			if (++rt >= main.first.Size()) EndReplay();
		}
		playerWas = mo.pos;
		if (CVar.GetCVar("ajar_autotest").GetInt() && level.mapname ~== "TIME") TimeScript(PlayerPawn(mo));
	}

	// How far the fight that is being watched has got, and when the door opens.
	override void RenderOverlay(RenderEvent e)
	{
		if (phase != REPLAY || !main) return;
		int now = rt / 35, end = main.first.Size() / 35;
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
		if (t == 827) Check("backIn2", at == 0 && mo.pos.y < 100 && mo.pos.z < 8);
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
}
