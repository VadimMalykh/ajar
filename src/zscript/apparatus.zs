// MAP21's apparatus (tools/gfx_longrun.py draws it, tools/map_longrun.py places it): pieces that stand THEN,
// sprites in one of three looks, args[0]: 1 Lamps and Reels, 2 Copper and Porcelain, 3 Glass and Mercury (frame
// A, B, C). args[1] 1: solid (a piece flush against a wall where nobody walks); otherwise nothing stops at it.
class AjarApparatus : Actor
{
	Default
	{
		Radius 16;
		Height 56;
		+DONTSPLASH
		+NOTAUTOAIMED
	}
	virtual int FirstFrame() { return clamp(args[0], 1, 3) - 1; }
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		frame = FirstFrame();
		bSolid = args[1] != 0;
		if (bSolid) A_SetSize(20, Height);
	}
}

class AjarApparatusTrolley : AjarApparatus     // S1, 40x56: a scope; a meter set; a vacuum pump
{
	Default { Height 56; }
	States { Spawn: AJUA A -1; Stop; }
}

class AjarApparatusTall : AjarApparatus        // S2, 40x96: a tape drive; a coil on insulators; a tube on a stand
{
	Default { Height 96; }
	States { Spawn: AJUB A -1; Stop; }
}

class AjarApparatusSmall : AjarApparatus       // S3, on a desk: a desk radio; a telephone; a glass of tea
{
	Default { Height 20; }
	States { Spawn: AJUC A -1; Stop; }
}

// EM, 40x72: the beam's emitter THEN, standing where then.zs's AjarThenEmitter is (whose own sprite it hides:
// the beam is still that one's). args[2]: the beam's cause (its tid): lit (A, B, C) in settings 1 to 3, dark
// (G, H, I) in 0, OFF. args[1] 1: its wreck (D, E, F); NOW map21.zs's AjarEmitterWreck shows those.
class AjarApparatusEmitter : AjarApparatus
{
	AjarThenCause cause;
	Default { Height 72; }
	States { Spawn: AJUE A -1; Stop; }
	override int FirstFrame()
	{
		int look = clamp(args[0], 1, 3) - 1;
		if (args[1]) return look + 3;
		return (cause && cause.setting == 0) ? look + 6 : look;
	}
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		bSolid = false;
		A_SetSize(16, Height);
		if (args[2])
		{
			let it = level.CreateActorIterator(args[2], "AjarThenCause");
			cause = AjarThenCause(it.Next());
		}
		let ei = ThinkerIterator.Create("AjarThenEmitter");
		Actor em;
		while (em = Actor(ei.Next()))
			if ((em.pos.xy - pos.xy).Length() < 8) em.bInvisible = true;
		frame = FirstFrame();
	}
	override void Tick()
	{
		Super.Tick();
		if (!bDestroyed) frame = FirstFrame();
	}
}

// MAP=MAP21 MODE=7 tools/smoke.sh: the apparatus's views, for its look board (tools/board21_shots.sh): each
// place twice, THEN and then NOW from the same spot (view 2k THEN, 2k+1 NOW), 70 tics each, a screenshot every
// 35 (tools/smoke_MAP21_7.cfg: two a view, the later one kept). Posed, monsters gone (LongRunTest does that).
class LongRunLookViews : EventHandler
{
	const OFF = 8192;
	int tic;
	static const double V[] = {
		// x, y (NOW's), angle, pitch; what it is for (the board's rows: tools/board21_shots.sh, design/map21-board.html)
		512, 40, 90, 0,          //  0 the start: the desk, its radio, the machine, the consoles, the banks far off
		300, 576, 180, 0,        //  1 the hall's west bank of cabinets (NOW its ghost), the trolley
		724, 576, 0, 0,          //  2 the hall's east bank, its end panel
		330, 192, 180, 6,        //  3 the hall's west console, the ducts
		512, 520, 90, -6,        //  4 the hall's north wall: the schematic, the two tall pieces, the shutter
		860, 330, 0, 0,          //  5 the doorway: the notice and the calendar
		1150, 380, 90, -4,       //  6 the vestibule: the pass and key board, the porter's desk and what is on it
		1146, 408, 0, 0,         //  7 the vestibule's notice by the turnstile, from 150
		1360, 300, 10, 0,        //  8 the pocket: the wall newspaper, the trolley
		1080, 1250, 200, 10,     //  9 the cellar from the landing: the pump and its tank under the valve's pipe
		1180, 1350, 110, 0,      // 10 the cellar's north side: the tanks, the console and the pipe run on the landing
		1070, 1376, 180, 0,      // 11 the cellar's ledge across the pit: the valve's gauges
		1728, 1250, 90, 0,       // 12 the goods bay's racks
		1720, 1330, 215, 10,     // 13 the goods bay's belt from the flap, its motor
		1930, 1420, 140, 0,      // 14 the goods bay's console by the lever BELT
		1600, 2600, 180, 4,      // 15 optics: the benches, the tall pieces, the emitter from behind
		1408, 2440, 90, 0,       // 16 optics: the emitter on its inlay (NOW its wreck)
		1568, 2380, 90, -6       // 17 optics from in front of 106: the plan board, the plates A, B, C
	};

	override void WorldTick()
	{
		if (CVar.GetCVar("ajar_autotest").GetInt() != 7 || !(level.mapname ~== "MAP21")) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 10) mo.bInvisible = true;
		if (tic < 20 || (tic - 20) % 70) return;
		int i = (tic - 20) / 70, k = i / 2;
		if (k * 4 >= V.Size()) { if (k * 4 == V.Size() && !(i % 2)) Console.Printf("AJARTEST lookViewsDone=1"); return; }
		double x = V[k * 4], y = V[k * 4 + 1] + (i % 2 ? 0 : OFF);
		mo.SetOrigin((x, y, level.PointInSector((x, y)).floorplane.ZatPoint((x, y))), false);
		mo.angle = V[k * 4 + 2];
		mo.pitch = V[k * 4 + 3];
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		Console.Printf("AJARTEST info look view %d (%s) at %.0f %.0f", i, i % 2 ? "now" : "then", x, y);
	}
}
