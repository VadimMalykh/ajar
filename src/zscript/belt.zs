// The belt lab (map BELT, tools/map_belt.py; PLAN.md, "The belt lab").
//
// A belt is a scrolling floor that carries what stands on it
// (ajarmap.belt: Scroll_Floor, the texture and things). Where a belt ends
// at a frame, what it carries goes through whatever door hangs there and
// comes out of that door's far side; the belt there carries it on.
//  * AjarCrate thing (20094): what MAP17 will send. Solid, not shootable,
//    not pushed by walking into it, heavy; carried like anything on the
//    floor. It keeps the stamps of the rooms it came into, in order.
//  * AjarStation thing (20095): args[0] a colour number. A crate whose
//    middle comes into the station's sector is stamped with that number
//    (once each time it comes in; where it starts is no coming in).
//    "AJARTEST stamps=..." on the console when a crate's stamps change.

class AjarCrate : Actor
{
	Array<int> stamps;
	Sector was;

	Default
	{
		Radius 16;
		Height 32;
		Mass 1000;
		MaxStepHeight 4;        // a belt's curb (16) holds it
		+SOLID +NOBLOOD +DONTTHRUST +NOTAUTOAIMED
	}
	States
	{
	Spawn:
		AMMO A -1;              // Doom's box of bullets, for now
		Stop;
	}

	string StampList()
	{
		string s = "";
		for (int i = 0; i < stamps.Size(); i++) s = s .. (i ? "," : "") .. stamps[i];
		return s;
	}

	override void Tick()
	{
		Super.Tick();
		if (bDestroyed) return;
		if (!was) { was = CurSector; return; }
		if (CurSector == was) return;
		was = CurSector;
		let it = ThinkerIterator.Create("AjarStation");
		AjarStation s;
		while (s = AjarStation(it.Next()))
		{
			if (s.home != CurSector) continue;
			stamps.Push(s.args[0]);
			Console.Printf("AJARTEST stamps=%s t=%d crate at (%.0f,%.0f)", StampList(), level.maptime, pos.x, pos.y);
		}
	}
}

class AjarStation : Actor
{
	Sector home;

	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE +NOSECTOR    // (in no sector's list of things: a belt does not carry it off)
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		home = level.PointInSector(pos.xy);
	}
}

// A door is taken (or a sprung frame shuts, a Pair parts...) while a crate
// is in the doorway, its box over the portal line and its middle not yet
// across: the engine leaves it there, in a wall it cannot move out of
// either way, until a door is hung again (PLAN.md, "The belt lab", E). So
// whenever a portal line becomes solid (AjarHandler.Link), a crate over it
// is put a step clear on the side its middle is on, as plate.zs's
// StandClear does with the player; a crate right behind it is moved along
// with it. Only crates: the player, monsters and barrels are left as the
// engine leaves them.
extend class AjarHandler
{
	bool beltRaw;               // the lab's look at what the engine does without this

	void CratesClear(Line l)
	{
		if (beltRaw) return;
		Vector2 dir = l.delta.Unit(), n = (dir.y, -dir.x);
		let it = ThinkerIterator.Create("AjarCrate");
		AjarCrate c;
		while (c = AjarCrate(it.Next()))
		{
			Vector2 rel = c.pos.xy - l.v1.p;
			double along = rel dot dir, d = rel dot n, reach = c.radius * (abs(n.x) + abs(n.y));
			if (along < -c.radius || along > l.delta.Length() + c.radius || abs(d) >= reach) continue;
			ShoveCrate(c, n * ((d < 0 ? -1 : 1) * (reach + 1) - d), 0);
		}
	}

	void ShoveCrate(AjarCrate c, Vector2 by, int depth)
	{
		c.SetOrigin((c.pos.xy + by, c.pos.z), true);
		if (depth > 8) return;
		Vector2 u = by.Unit();
		let it = ThinkerIterator.Create("AjarCrate");
		AjarCrate o;
		while (o = AjarCrate(it.Next()))
		{
			if (o == c || abs(o.pos.z - c.pos.z) >= c.height) continue;
			Vector2 gap = o.pos.xy - c.pos.xy;
			double r = o.radius + c.radius, ahead = gap dot u;
			if (abs(gap.x) >= r || abs(gap.y) >= r || ahead <= 0) continue;
			ShoveCrate(o, u * (r - ahead), depth + 1);
		}
	}
}

// --- the checks: MAP=BELT MODE=1..6 tools/smoke.sh ----------------------
// What rides is watched by a BeltWatch: when it first gets past given
// marks, and where it is.
class AjarBeltWatch : Object
{
	Actor a;
	string name;
	int from;                   // the tic it was put down
	int at96, at608;            // the tics it got past x 96 and x 608 on H's belt (512 apart)
	int crossed;                // the tic it first came out in another room than it started in
	double maxX;
	Vector3 was;
}

extend class AjarHandler
{
	Array<AjarBeltWatch> belts;
	AjarCrate beltCrate, beltCrate2;
	Actor beltSubject;
	int beltT1, beltT2, beltT3, beltLaps;
	double beltLapAt, beltLapMin, beltLapMax;
	Array<double> beltLapTook;
	double beltLo, beltHi, beltYLo, beltYHi, beltVLo, beltVHi;
	bool beltFlag;

	AjarBeltWatch BeltWatch(Actor a, string name, int t)
	{
		let w = new("AjarBeltWatch");
		w.a = a; w.name = name; w.from = t; w.maxX = a.pos.x; w.was = a.pos;
		belts.Push(w);
		return w;
	}

	AjarBeltWatch Watched(Actor a)
	{
		for (int i = 0; i < belts.Size(); i++) if (belts[i].a == a) return belts[i];
		return null;
	}

	void BeltWatchTick(int t)
	{
		for (int i = 0; i < belts.Size(); i++)
		{
			let w = belts[i];
			if (!w.a) continue;
			Vector3 p = w.a.pos;
			if (!w.at96 && p.x >= 96 && p.x < 700) w.at96 = t;
			if (!w.at608 && p.x >= 608 && p.x < 700) w.at608 = t;
			if (!w.crossed && (p.xy - w.was.xy).Length() > 64)
			{
				w.crossed = t;
				Console.Printf("AJARTEST info %s through a door at t=%d: (%.1f,%.1f) to (%.1f,%.1f), vel (%.2f,%.2f), angle %.0f",
					w.name, t, w.was.x, w.was.y, p.x, p.y, w.a.vel.x, w.a.vel.y, w.a.angle);
			}
			w.maxX = max(w.maxX, p.x);
			if ((t - w.from) % 10 == 0)
				Console.Printf("AJARTEST info t=%d %s (%.1f,%.1f,%.1f) vel (%.2f,%.2f) health %d", t, w.name, p.x, p.y, p.z, w.a.vel.x, w.a.vel.y, w.a.health);
			w.was = p;
		}
	}

	void BeltPace(AjarBeltWatch w)
	{
		if (w.at96 && w.at608) Console.Printf("AJARTEST info pace %s: 512 units of H's belt in %d tics (%.2f a tic)", w.name, w.at608 - w.at96, 512. / (w.at608 - w.at96));
		else Console.Printf("AJARTEST info pace %s: did not ride H's belt from 96 to 608", w.name);
	}

	// A door taken, or hung, by script as the player's USE would.
	void BeltPutBack(AjarDoor d)
	{
		d.carried = false;
		d.SetOrigin(d.SpawnPoint, false);
		d.angle = 90;
		d.Show();
		if (carried == d) carried = null;
	}

	void BeltHang(Actor mo, AjarDoor d, int frame)
	{
		if (carried && carried != d) BeltPutBack(carried);
		if (d.frame && d.frame.args[0] == frame) return;
		if (d.frame) UseFrame(d.frame, mo);
		else if (!carried) TakeLeaning(d, mo);
		UseFrame(FindFrame(frame), mo);
		if (carried) BeltPutBack(carried);
	}

	void BeltTake(Actor mo, int frame)
	{
		if (carried) BeltPutBack(carried);
		AjarFrame f = FindFrame(frame);
		if (f.door) UseFrame(f, mo);
		if (carried) BeltPutBack(carried);
	}

	Actor BeltSpawn(class<Actor> cls, double x, double y, int t, string name)
	{
		let a = Actor.Spawn(cls, (x, y, 0));
		a.angle = 0;
		BeltWatch(a, name, t);
		return a;
	}

	void BeltDrop(Actor a)
	{
		if (!a) return;
		let w = Watched(a);
		if (w) w.a = null;
		a.ClearCounters();
		a.Destroy();
	}

	bool InP(Actor a) { return a && a.pos.x > 784 && a.pos.x < 1456 && a.pos.y > 0 && a.pos.y < 384; }
	bool InK(Actor a) { return a && a.pos.x > 1600 && a.pos.x < 2256 && a.pos.y > 0 && a.pos.y < 464; }
	bool InS(Actor a) { return a && a.pos.x > 2384 && a.pos.x < 2848 && a.pos.y > 0 && a.pos.y < 384; }
	bool OnBelt(Actor a) { return a && abs(a.pos.y - 192) < 16; }

	void BeltScript(Actor mo, int t, int mode)
	{
		if (t == 1)
		{
			mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
			let it = ThinkerIterator.Create("AjarCrate");     // the map's own crate is for play by hand
			Actor c;
			while (c = Actor(it.Next())) c.Destroy();
		}
		BeltWatchTick(t);
		if (mode == 1) BeltPlain(mo, t);
		else if (mode == 2) BeltTurned(mo, t);
		else if (mode == 3) BeltOrder(mo, t);
		else if (mode == 4) BeltEmpty(mo, t);
		else if (mode == 5) BeltRing(mo, t);
		else if (mode == 6) BeltInTheWay(mo, t);
	}

	// MODE=1, A: RED in 101. A crate, a barrel, a sleeping imp and the
	// player standing still, each put on H's belt in turn.
	void BeltPlain(Actor mo, int t)
	{
		static const class<Actor> kinds[] = { "AjarCrate", "ExplosiveBarrel", "DoomImp", "" };
		static const string names[] = { "crate", "barrel", "imp", "player" };
		if (t == 5) { BeltHang(mo, DoorOf(1), 101); Pose(mo, 560, 72, 0, 90); Check("redHung", FindFrame(101).door == DoorOf(1)); }
		int i = (t - 10) / 250, k = (t - 10) % 250;
		if (t < 10 || i > 3) return;
		if (k == 0 && i < 3) beltSubject = BeltSpawn(kinds[i], 64, 192, t, names[i]);
		if (k == 0 && i == 3) { Pose(mo, 64, 192, 0, 90); beltSubject = mo; BeltWatch(mo, "player", t); }
		Actor a = beltSubject;
		if (k == 240 && a)
		{
			let w = Watched(a);
			BeltPace(w);
			Console.Printf("AJARTEST info %s ended at (%.1f,%.1f,%.1f) health %d, furthest x %.1f", names[i], a.pos.x, a.pos.y, a.pos.z, a.health, w.maxX);
			Check(names[i] .. "ThroughRed", w.crossed && w.maxX > 800 && a.pos.x > 784);
			Check(names[i] .. "OnPBelt", InP(a) && OnBelt(a) && a.pos.x > 900);
			if (i == 0) Check("crateUnderHatch", a.pos.x > 1130);
			else Check(names[i] .. "HeldAtHatch", a.pos.x < 1104 && a.pos.x > 1060);
			w.a = null;
			if (i < 3) BeltDrop(a); else Pose(mo, 560, 72, 0, 90);
			beltSubject = null;
		}
	}

	// MODE=2, B and C: GREEN in 102 (P to K, turned), then a TEAL leaf in
	// 103 and its twin in 104 (K to S by a Pair, out of a frame).
	void BeltTurned(Actor mo, int t)
	{
		AjarDoor ta = LabLeaf(8, 0), tb = LabLeaf(8, 1);
		if (t == 5) { BeltHang(mo, DoorOf(3), 102); Pose(mo, 1700, 72, 0, 90); }
		if (t == 10) beltCrate = AjarCrate(BeltSpawn("AjarCrate", 1200, 192, t, "crate"));
		// after the crate, the player standing still takes the same way: P, K's corner, the Pair, the scale
		if (t == 380) { Pose(mo, 1200, 192, 0, 0); BeltWatch(mo, "player", t); }
		if (t == 700)
		{
			Console.Printf("AJARTEST info player ended at (%.1f,%.1f) angle %.0f", mo.pos.x, mo.pos.y, mo.angle);
			Check("playerRodeToScale", InS(mo) && mo.pos.x > 2528 && mo.pos.x < 2688);
		}
		AjarCrate c = beltCrate;
		if (!c) return;
		let w = Watched(c);
		if (w && w.crossed == t - 1)
		{
			Console.Printf("AJARTEST info into K: (%.1f,%.1f) vel (%.2f,%.2f)", c.pos.x, c.pos.y, c.vel.x, c.vel.y);
			Check("outAlongKBelt", InK(c) && c.vel.y < -3 && abs(c.vel.x) < 0.5 && abs(c.pos.x - 1792) < 1);
		}
		if (t > 10 && t < 200 && InK(c) && c.pos.y < 224 && !beltT1) { beltT1 = t; Console.Printf("AJARTEST info at the corner t=%d (%.1f,%.1f) vel (%.2f,%.2f)", t, c.pos.x, c.pos.y, c.vel.x, c.vel.y); }
		if (t > 10 && t < 200 && InK(c) && c.pos.x > 1900 && !beltT2) { beltT2 = t; Console.Printf("AJARTEST info round the corner t=%d (%.1f,%.1f) vel (%.2f,%.2f)", t, c.pos.x, c.pos.y, c.vel.x, c.vel.y); }
		if (t == 200)
		{
			Check("roundTheCorner", beltT2 > 0 && InK(c) && OnBelt(c));
			Check("waitsAt103", abs(c.pos.x - 2240) < 2 && OnBelt(c) && c.vel.Length() < 0.01);
			BeltHang(mo, ta, 103);
			BeltHang(mo, tb, 104);
			Check("pairHung", ta.args[0] == 104 && tb.args[0] == 103);
			beltT1 = 0;
		}
		if (t > 200 && InS(c) && !beltT1) { beltT1 = t; Console.Printf("AJARTEST info into S t=%d (%.1f,%.1f) vel (%.2f,%.2f)", t, c.pos.x, c.pos.y, c.vel.x, c.vel.y); }
		if (t == 330) { beltLo = c.pos.x; beltYLo = c.pos.y; }
		if (t == 365)
		{
			Console.Printf("AJARTEST info on the scale: (%.2f,%.2f) vel (%.3f,%.3f), at t=330 (%.2f,%.2f)", c.pos.x, c.pos.y, c.vel.x, c.vel.y, beltLo, beltYLo);
			Check("outOfFrame104", beltT1 > 0);
			Check("restsOnScale", c.pos.x > 2528 && c.pos.x < 2688 && OnBelt(c) && c.pos.x == beltLo && c.pos.y == beltYLo && c.vel.Length() == 0);
		}
		if (t == 370) BeltDrop(c);
	}

	// MODE=3, D: H, P, K with RED in 101 and GREEN in 102; then H, K, P with
	// GREEN in 101 and RED in 103.
	void BeltOrder(Actor mo, int t)
	{
		if (t == 5) { BeltHang(mo, DoorOf(1), 101); BeltHang(mo, DoorOf(3), 102); Pose(mo, 560, 72, 0, 90); }
		if (t == 10) beltCrate = AjarCrate(BeltSpawn("AjarCrate", 64, 192, t, "crate"));
		if (t == 400)
		{
			Console.Printf("AJARTEST info first crate: stamps %s at (%.1f,%.1f)", beltCrate.StampList(), beltCrate.pos.x, beltCrate.pos.y);
			Check("stampsPThenK", beltCrate.StampList() == "1,3" && abs(beltCrate.pos.x - 2240) < 2);
			BeltDrop(beltCrate);
			BeltTake(mo, 101);
			BeltTake(mo, 102);
			BeltHang(mo, DoorOf(3), 101);
			BeltHang(mo, DoorOf(1), 103);
			Check("swapped", FindFrame(101).door == DoorOf(3) && FindFrame(103).door == DoorOf(1) && !FindFrame(102).door);
		}
		if (t == 405) beltCrate = AjarCrate(BeltSpawn("AjarCrate", 64, 192, t, "crate2"));
		if (t == 800)
		{
			Console.Printf("AJARTEST info second crate: stamps %s at (%.1f,%.1f)", beltCrate.StampList(), beltCrate.pos.x, beltCrate.pos.y);
			Check("stampsKThenP", beltCrate.StampList() == "3,1" && abs(beltCrate.pos.x - 1440) < 2);
		}
	}

	// MODE=4, E: an empty frame, a queue, a door taken from under a crate.
	void BeltEmpty(Actor mo, int t)
	{
		if (t == 5) Pose(mo, 560, 72, 0, 90);
		if (t == 10) beltCrate = AjarCrate(BeltSpawn("AjarCrate", 64, 192, t, "crateA"));
		AjarCrate a = beltCrate, b = beltCrate2;
		if (t == 120) { beltLo = beltHi = a.pos.x; beltYLo = beltYHi = a.pos.y; }
		if (t > 120 && t <= 230)
		{
			beltLo = min(beltLo, a.pos.x); beltHi = max(beltHi, a.pos.x);
			beltYLo = min(beltYLo, a.pos.y); beltYHi = max(beltYHi, a.pos.y);
		}
		if (t == 230)
		{
			Console.Printf("AJARTEST info crateA waiting: x %.3f..%.3f, y %.3f..%.3f, vel (%.3f,%.3f), health %d", beltLo, beltHi, beltYLo, beltYHi, a.vel.x, a.vel.y, a.health);
			Check("waitsAtEmptyFrame", abs(a.pos.x - 640) < 2 && OnBelt(a));
			Check("noJitter", beltHi - beltLo < 0.01 && beltYHi - beltYLo < 0.01);
			Check("noDamage", a.health == a.SpawnHealth());
			Check("notInTheWall", a.pos.x + a.radius <= 656);
		}
		if (t == 130) beltCrate2 = AjarCrate(BeltSpawn("AjarCrate", 64, 192, t, "crateB"));
		if (t == 230)
		{
			Console.Printf("AJARTEST info crateB at (%.2f,%.2f) vel (%.3f,%.3f)", b.pos.x, b.pos.y, b.vel.x, b.vel.y);
			Check("secondQueues", abs(b.pos.x - (a.pos.x - 32)) < 2 && OnBelt(b));
		}
		if (t == 235) { BeltHang(mo, DoorOf(1), 101); Pose(mo, 560, 72, 0, 90); }
		if (t == 400)
		{
			let wa = Watched(a), wb = Watched(b);
			Console.Printf("AJARTEST info through after RED was hung (t=235): crateA at t=%d, crateB at t=%d; now (%.1f,%.1f) and (%.1f,%.1f)", wa.crossed, wb.crossed, a.pos.x, a.pos.y, b.pos.x, b.pos.y);
			Check("bothThroughInTurn", wa.crossed && wb.crossed && wa.crossed < wb.crossed && InP(a) && InP(b));
			Check("queueAt102", abs(a.pos.x - 1440) < 2 && abs(b.pos.x - 1408) < 2);
			BeltDrop(a); BeltDrop(b);
			beltRaw = true;            // first what the engine does by itself
			beltCrate = AjarCrate(BeltSpawn("AjarCrate", 400, 192, t, "crateC"));
			beltCrate2 = null;
			beltT1 = beltT2 = 0;
		}
		if (t <= 400 || !beltCrate) return;
		// The door taken while a crate is in the frame's doorway (its box over
		// the portal line, its middle not yet across), then while one is in the
		// far side's doorway (just come out in P). Twice: by the engine alone
		// (beltRaw), then with CratesClear, and a second crate right behind.
		a = beltCrate; b = beltCrate2;
		string pass = beltRaw ? "raw" : "clear";
		if (!beltT1 && a.pos.x + a.radius > 656 && a.pos.x < 656)
		{
			beltT1 = t;
			beltLo = a.pos.x;
			Console.Printf("AJARTEST info %s: crateC in the frame's doorway at t=%d x %.2f%s: RED is taken", pass, t, a.pos.x, b ? String.Format(", crateD at %.2f", b.pos.x) : "");
			BeltTake(mo, 101);
			beltHi = a.pos.x;
			Console.Printf("AJARTEST info %s: right after, crateC at %.2f%s", pass, a.pos.x, b ? String.Format(", crateD at %.2f", b.pos.x) : "");
			if (beltRaw) Check("rawLeftInTheLine", beltHi == beltLo);
			else Check("steppedClearOfFrame", a.pos.x + a.radius < 656 && b.pos.x <= a.pos.x - 32 + 0.01 && OnBelt(a) && OnBelt(b));
		}
		if (beltT1 && t > beltT1 && t <= beltT1 + 35 && (t - beltT1) % 5 == 0)
			Console.Printf("AJARTEST info %s: t+%d crateC (%.2f,%.2f) vel (%.2f,%.2f)%s", pass, t - beltT1, a.pos.x, a.pos.y, a.vel.x, a.vel.y, b ? String.Format(", crateD %.2f", b.pos.x) : "");
		if (beltT1 && t == beltT1 + 35)
		{
			if (beltRaw) Check("rawStuckInFrameDoorway", a.pos.x == beltLo && a.pos.x + a.radius > 656);
			else Check("waitsAfterTaken", abs(a.pos.x - 640) < 0.1 && abs(b.pos.x - (a.pos.x - 32)) < 1 && a.vel.Length() < 0.01 && b.vel.Length() < 0.01);
			BeltHang(mo, DoorOf(1), 101);
		}
		// (with the step clear: the two now queue touching; RED hung, both set
		// off together, and RED taken again as the first is in the doorway
		// with the second right behind it)
		if (!beltRaw && beltT1 && t > beltT1 + 35 && !beltT3 && a.pos.x + a.radius > 656 && a.pos.x < 656)
		{
			beltT3 = t;
			Console.Printf("AJARTEST info clear: the queue in the frame's doorway at t=%d, crateC at %.2f, crateD at %.2f: RED is taken", t, a.pos.x, b.pos.x);
			BeltTake(mo, 101);
			Console.Printf("AJARTEST info clear: right after, crateC at %.2f, crateD at %.2f", a.pos.x, b.pos.x);
			Check("queueSteppedClear", a.pos.x + a.radius < 656 && b.pos.x <= a.pos.x - 32 + 0.01 && OnBelt(a) && OnBelt(b));
		}
		if (beltT3 && t == beltT3 + 10) BeltHang(mo, DoorOf(1), 101);
		if (beltT1 && t > beltT1 + 35 && (beltRaw || (beltT3 && t > beltT3 + 10)) && !beltT2 && InP(a) && a.pos.x - a.radius < 784)
		{
			beltT2 = t;
			beltLo = a.pos.x;
			Console.Printf("AJARTEST info %s: crateC in RED's far doorway at t=%d x %.2f%s: RED is taken", pass, t, a.pos.x, b ? String.Format(", crateD at %.2f", b.pos.x) : "");
			BeltTake(mo, 101);
			Console.Printf("AJARTEST info %s: right after, crateC at %.2f", pass, a.pos.x);
			if (!beltRaw) Check("steppedClearOfFarSide", a.pos.x - a.radius > 784 && InP(a));
		}
		if (beltT2 && t > beltT2 && t <= beltT2 + 35 && (t - beltT2) % 5 == 0)
			Console.Printf("AJARTEST info %s: t+%d crateC (%.2f,%.2f) vel (%.2f,%.2f)%s", pass, t - beltT2, a.pos.x, a.pos.y, a.vel.x, a.vel.y, b ? String.Format(", crateD %.2f", b.pos.x) : "");
		if (beltT2 && t == beltT2 + 35)
		{
			if (beltRaw) Check("rawStuckInFarDoorway", a.pos.x == beltLo && a.pos.x - a.radius < 784);
			else Check("goesOnAndSecondWaits", a.pos.x > 1000 && abs(b.pos.x - 640) < 0.1);
			Check("noneLost", level.IsPointInLevel(a.pos) && (!b || level.IsPointInLevel(b.pos)));
			BeltDrop(a); BeltDrop(b);
			beltT1 = beltT2 = beltT3 = 0;
			if (beltRaw)
			{
				beltRaw = false;
				BeltHang(mo, DoorOf(1), 101);
				beltCrate = AjarCrate(BeltSpawn("AjarCrate", 400, 192, t, "crateC"));
				beltCrate2 = AjarCrate(BeltSpawn("AjarCrate", 368, 192, t, "crateD"));
			}
			else beltCrate = null;
		}
	}

	// MODE=5, F: the ring, RED in 101, GREEN in 102, BLUE in 103.
	void BeltRing(Actor mo, int t)
	{
		if (t == 5)
		{
			BeltHang(mo, DoorOf(1), 101); BeltHang(mo, DoorOf(3), 102); BeltHang(mo, DoorOf(2), 103);
			Pose(mo, 560, 72, 0, 90);
		}
		if (t == 10) { beltCrate = AjarCrate(BeltSpawn("AjarCrate", 64, 192, t, "crate")); beltLo = 64; }
		if (t == 6) BeltKeep();
		AjarCrate c = beltCrate;
		if (!c) return;
		// a lap: past x 320 on H's belt (the tic it got there, to a fraction)
		if (beltLo < 320 && c.pos.x >= 320 && c.pos.x < 640)
		{
			double at = t - 1 + (320 - beltLo) / (c.pos.x - beltLo);
			if (beltLapAt > 0)
			{
				double took = at - beltLapAt;
				beltLaps++;
				beltLapTook.Push(took);
				beltLapMin = beltLaps == 1 ? took : min(beltLapMin, took);
				beltLapMax = beltLaps == 1 ? took : max(beltLapMax, took);
				if (beltLaps == 1) { beltYLo = beltYHi = c.pos.y; beltVLo = beltVHi = c.vel.x; }
				beltYLo = min(beltYLo, c.pos.y); beltYHi = max(beltYHi, c.pos.y);
				beltVLo = min(beltVLo, c.vel.x); beltVHi = max(beltVHi, c.vel.x);
			}
			Console.Printf("AJARTEST info lap %d at t=%.2f took %.2f, y %.3f, vel (%.3f,%.3f), stamps %s", beltLaps, at, beltLapAt > 0 ? at - beltLapAt : 0., c.pos.y, c.vel.x, c.vel.y, c.StampList());
			beltLapAt = at;
		}
		beltLo = c.pos.x;
		if (t == 1900)
		{
			Console.Printf("AJARTEST info %d laps, %.2f to %.2f tics, y %.3f..%.3f, speed %.3f..%.3f (from the first lap's end on)", beltLaps, beltLapMin, beltLapMax, beltYLo, beltYHi, beltVLo, beltVHi);
			Check("fiveLaps", beltLaps >= 5);
			// a lap is not to the tic the same (the corner in K: below), but
			// within 2% of each other, and the later ones no slower
			double early = 0, late = 0;
			int half = beltLapTook.Size() / 2;
			for (int i = 0; i < half * 2; i++) { if (i < half) early += beltLapTook[i]; else late += beltLapTook[i]; }
			if (half) Console.Printf("AJARTEST info laps %d to %d took %.2f on average, laps %d to %d %.2f", 1, half, early / half, half + 1, half * 2, late / half);
			Check("lapsSteady", beltLapMax - beltLapMin < 5.4);
			Check("notSlowing", half > 0 && late / half - early / half < 1);
			Check("noDrift", beltYHi - beltYLo < 0.1 && beltVHi - beltVLo < 0.01);
			Check("framesAndDoorsStayPut", BeltKept());
		}
	}

	// Frames, doors and stations stand on the belts' sectors too, without
	// gravity: a belt must not carry them off.
	Array<Actor> keptA;
	Array<double> keptX, keptY;
	void BeltKeep()
	{
		for (int pass = 0; pass < 3; pass++)
		{
			let it = ThinkerIterator.Create(pass == 0 ? "AjarFrame" : pass == 1 ? "AjarDoor" : "AjarStation");
			Actor a;
			while (a = Actor(it.Next())) { keptA.Push(a); keptX.Push(a.pos.x); keptY.Push(a.pos.y); }
		}
	}
	bool BeltKept()
	{
		bool ok = keptA.Size() > 0;
		for (int i = 0; i < keptA.Size(); i++)
			if (keptA[i].pos.x != keptX[i] || keptA[i].pos.y != keptY[i])
			{
				ok = false;
				Console.Printf("AJARTEST info %s moved from (%.1f,%.1f) to (%.1f,%.1f)", keptA[i].GetClassName(), keptX[i], keptY[i], keptA[i].pos.x, keptA[i].pos.y);
			}
		return ok;
	}

	// MODE=6, G: in the way. The player on the belt before a crate; then an
	// awake imp on the belt. Reported, not judged.
	Actor beltImp;
	void BeltInTheWay(Actor mo, int t)
	{
		if (t == 5) { BeltHang(mo, DoorOf(1), 101); Pose(mo, 200, 192, 0, 0); BeltWatch(mo, "player", t); }
		if (t == 6) beltCrate = AjarCrate(BeltSpawn("AjarCrate", 64, 192, t, "crate"));
		AjarCrate c = beltCrate;
		if (t == 200)
		{
			Console.Printf("AJARTEST info player at (%.1f,%.1f), crate at (%.1f,%.1f)", mo.pos.x, mo.pos.y, c.pos.x, c.pos.y);
			Check("playerAndCrateReported", true);
			Pose(mo, 1300, 300, 0, 180);      // out of the way, in P beyond the hatch
		}
		if (t == 300)
		{
			Console.Printf("AJARTEST info with the player gone: crate at (%.1f,%.1f)", c.pos.x, c.pos.y);
			Check("crateGoesOnWhenClear", c.pos.x > 1130);
			BeltDrop(c);
			mo.player.cheats &= ~CF_NOTARGET;
			Pose(mo, 560, 320, 0, 180);       // in H, north of the belt
			beltImp = BeltSpawn("DoomImp", 100, 192, t, "imp");
			beltImp.target = mo;
			beltImp.SetState(beltImp.SeeState);
		}
		if (t == 600)
		{
			Console.Printf("AJARTEST info imp after 300 tics at (%.1f,%.1f,%.1f) health %d, in level %d", beltImp.pos.x, beltImp.pos.y, beltImp.pos.z, beltImp.health, level.IsPointInLevel(beltImp.pos));
			Check("impReported", true);
			// the player in P beyond the hatch: does it ride through RED to them?
			Pose(mo, 1300, 300, 0, 180);
			beltImp.SetOrigin((100, 192, 0), false);
			beltImp.target = mo;
		}
		if (t == 1000)
		{
			Console.Printf("AJARTEST info imp after 400 more tics at (%.1f,%.1f,%.1f) health %d, in level %d", beltImp.pos.x, beltImp.pos.y, beltImp.pos.z, beltImp.health, level.IsPointInLevel(beltImp.pos));
			Check("impReported2", true);
		}
	}
}
