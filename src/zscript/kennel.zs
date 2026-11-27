// The kennel lab (map KENNEL: tools/map_kennel.py; PLAN.md, "The kennel lab").
// The tests: kenneltest.zs. What bones do NOW, for MAP23 "Sleeping Dogs":
//
// Bones are then.zs's old corpses (AjarThenCorpse): of a monster dead THEN (for
// good), or standing in for one alive THEN while the times are apart. Each
// keeps its monster's Mass and radius. Whatever weighs them counts one from the
// tic it is spawned to the tic it is gone (a stand-in fading in or out too).
//
//   * AjarKennelScales (20193, NOW): weighs the bones lying in the sectors
//     tagged args[0] (a pen) and shows the sum on its readout (four digit
//     plates, a wall sprite each, along the wall it faces out of: amber under
//     args[1], green at or over it). With args[2], the sector of that tag is
//     its shutter: open (ceiling args[3] over its floor) while the weight is at
//     or over args[1], shut otherwise, moving over MOVE_TICS, and it does not
//     come down on anything standing under it.
//   * AjarKennel (the map's event handler): the bones of a monster of Mass
//     BIG or more are a step, AjarKennelStep: solid, STEP_H high, the
//     monster's own radius, an actor the player steps onto (+ACTLIKEBRIDGE)
//     as onto a stair, and up from it. It is not solid while anything solid
//     overlaps it (bones appearing under the player or a monster): it becomes
//     solid once they are clear. It goes when its bones are gone; whoever
//     stands on it drops.

class AjarKennelDigit : Actor
{
	Default { Radius 4; Height 24; +NOGRAVITY +WALLSPRITE +NOBLOCKMAP +DONTTHRUST +NOTELEPORT +BRIGHT +NOINTERACTION }
	States
	{
	Spawn:
		AJKD K -1 Bright;
		Stop;
	Digits:                     // only so that these are loaded
		AJKD ABCDEFGHIJKLMNOPQRSTU -1;
		Stop;
	}
}

class AjarKennelScales : Actor
{
	const MOVE_TICS = 64;
	const PLACES = 4;
	Array<int> secs;
	Array<AjarKennelDigit> digits;
	int weight;
	int shownWeight;
	Sector shutter;
	double shutFloor;
	double bx1, by1, bx2, by2;
	int openedAt, shutAt;      // (the tests) the tic it last stood fully open, fully shut
	bool held;                 // (the tests) its closing is waiting for what stands under it

	Default { +NOBLOCKMAP +NOGRAVITY +NOINTERACTION +INVISIBLE }
	States { Spawn: TNT1 A -1; Stop; }

	int Threshold() { return args[1]; }
	bool Holds() { return weight >= Threshold(); }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		let si = level.CreateSectorTagIterator(args[0]);
		int s;
		while ((s = si.Next()) >= 0) secs.Push(s);
		Vector2 along = (cos(angle + 90), sin(angle + 90));       // left to right, for one facing the wall
		for (int i = 0; i < PLACES; i++)
		{
			let d = AjarKennelDigit(Spawn("AjarKennelDigit", pos + (along * (16 * i - 24), 0)));
			if (d) { d.angle = angle; digits.Push(d); }
		}
		if (args[2])
		{
			let ti = level.CreateSectorTagIterator(args[2]);
			int k = ti.Next();
			if (k >= 0)
			{
				shutter = level.sectors[k];
				shutFloor = shutter.floorplane.ZAtPoint(shutter.centerspot);
				bx1 = by1 = 1e9; bx2 = by2 = -1e9;
				for (int j = 0; j < shutter.lines.Size(); j++)
				{
					Line l = shutter.lines[j];
					bx1 = min(bx1, min(l.v1.p.x, l.v2.p.x)); by1 = min(by1, min(l.v1.p.y, l.v2.p.y));
					bx2 = max(bx2, max(l.v1.p.x, l.v2.p.x)); by2 = max(by2, max(l.v1.p.y, l.v2.p.y));
				}
			}
		}
		openedAt = shutAt = -1;
		Show();
	}

	bool InPen(Vector2 p)
	{
		int i = level.PointInSector(p).Index();
		return secs.Find(i) != secs.Size();
	}

	int Weigh()
	{
		let th = AjarThenHandler.Get();
		if (!th) return 0;
		int w = 0;
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (c && !c.bDestroyed && InPen(c.pos.xy)) w += c.weight;
		}
		return w;
	}

	void Show()
	{
		int w = clamp(weight, 0, 9999);
		int base = Holds() ? 11 : 0;
		for (int i = 0; i < digits.Size(); i++)
		{
			int p = 1;
			for (int k = i; k < PLACES - 1; k++) p *= 10;
			int dgt = (w / p) % 10;
			bool lead = w < p && i < PLACES - 1;           // no leading noughts
			digits[i].frame = lead ? 10 : base + dgt;
		}
		shownWeight = weight;
	}

	bool Occupied()
	{
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!(a.player || a.bSolid || a.bShootable) || a.bNoBlockmap) continue;
			if (a.pos.x + a.radius <= bx1 || a.pos.x - a.radius >= bx2) continue;
			if (a.pos.y + a.radius <= by1 || a.pos.y - a.radius >= by2) continue;
			return true;
		}
		return false;
	}

	double CeilZ() { return shutter.ceilingplane.ZAtPoint(shutter.centerspot); }

	// every tic, from AjarKennel.WorldTick: after then.zs's handler has made or ended bones this tic
	void Weighing()
	{
		weight = Weigh();
		if (weight != shownWeight || level.maptime < 2) Show();
		if (!shutter) return;
		double want = shutFloor + (Holds() ? args[3] : 0), now = CeilZ();
		double speed = max(args[3], 1) / double(MOVE_TICS);
		held = false;
		if (want > now + 0.01) shutter.MoveCeiling(speed, shutter.ceilingplane.PointToDist(shutter.centerspot, want), -1, 1, false);
		else if (want < now - 0.01)
		{
			if (Occupied()) held = true;
			else shutter.MoveCeiling(speed, shutter.ceilingplane.PointToDist(shutter.centerspot, want), -1, -1, false);
		}
		now = CeilZ();
		if (abs(now - (shutFloor + args[3])) < 0.01) { if (openedAt < 0 || shutAt > openedAt) openedAt = level.maptime; }
		else if (abs(now - shutFloor) < 0.01) { if (shutAt < 0 || openedAt > shutAt) shutAt = level.maptime; }
	}

	bool IsOpen() { return shutter && abs(CeilZ() - (shutFloor + args[3])) < 0.01; }
	bool IsShut() { return shutter && abs(CeilZ() - shutFloor) < 0.01; }

	static AjarKennelScales OfTag(int tag)
	{
		let it = ThinkerIterator.Create("AjarKennelScales");
		AjarKennelScales s;
		while (s = AjarKennelScales(it.Next())) if (s.args[0] == tag) return s;
		return null;
	}
}

class AjarKennelStep : Actor
{
	AjarThenCorpse bones;
	int solidAt;               // (the tests) the tic it became solid; -1 not yet
	Default
	{
		Radius 20;
		Height 24;
		Mass 100000;
		+ACTLIKEBRIDGE +DONTTHRUST +NOBLOOD +NOTAUTOAIMED +NOTELEPORT +DONTSPLASH +CANPASS
	}
	States { Spawn: TNT1 A -1; Stop; }

	override void BeginPlay() { Super.BeginPlay(); solidAt = -1; }

	// Is anything solid (or the player) where it stands?
	bool Overlapped()
	{
		let it = BlockThingsIterator.Create(self, radius + 64);
		while (it.Next())
		{
			let a = it.thing;
			if (!a || a == self || !(a.player || a.bSolid) || a is "AjarKennelStep") continue;
			if (abs(a.pos.x - pos.x) >= a.radius + radius || abs(a.pos.y - pos.y) >= a.radius + radius) continue;
			if (a.pos.z >= pos.z + height || a.pos.z + a.height <= pos.z) continue;
			return true;
		}
		return false;
	}

	override void Tick()
	{
		Super.Tick();
		if (!bones || bones.bDestroyed) { Destroy(); return; }
		if (!bSolid && !Overlapped()) { bSolid = true; solidAt = level.maptime; }
	}
}

class AjarKennel : EventHandler
{
	const BIG = 1000;          // bones of this Mass or more are a step
	const STEP_H = 24;
	Array<AjarKennelStep> steps;

	static AjarKennel Get() { return AjarKennel(EventHandler.Find("AjarKennel")); }

	AjarKennelStep StepOf(AjarThenCorpse c)
	{
		for (int i = 0; i < steps.Size(); i++) if (steps[i] && steps[i].bones == c) return steps[i];
		return null;
	}

	override void WorldTick()
	{
		let th = AjarThenHandler.Get();
		if (!th || !th.ready) return;
		let si = ThinkerIterator.Create("AjarKennelScales");
		AjarKennelScales sc;
		while (sc = AjarKennelScales(si.Next())) sc.Weighing();
		for (int i = steps.Size() - 1; i >= 0; i--) if (!steps[i] || steps[i].bDestroyed) steps.Delete(i);
		for (int i = 0; i < th.corpses.Size(); i++)
		{
			let c = th.corpses[i];
			if (!c || c.bDestroyed || c.weight < BIG || StepOf(c)) continue;
			let s = AjarKennelStep(Actor.Spawn("AjarKennelStep", c.pos));
			if (!s) continue;
			s.bSolid = false;
			s.A_SetSize(c.bodyRadius, STEP_H);
			s.bones = c;
			steps.Push(s);
			if (CVar.GetCVar("ajar_autotest").GetInt())
				Console.Printf("AJARTEST info a step at (%.0f,%.0f) radius %.0f for the bones of a %s", c.pos.x, c.pos.y, c.bodyRadius, c.who ? c.who.GetClassName() : 'nothing');
		}
	}
}
