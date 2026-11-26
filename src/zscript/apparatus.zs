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

class AjarApparatusEmitter : AjarApparatus     // EM, 40x72: the beam's emitter; args[1] 1: its wreck, now (D, E, F)
{
	Default { Height 72; }
	States { Spawn: AJUE A -1; Stop; }
	override int FirstFrame() { return clamp(args[0], 1, 3) - 1 + (args[1] ? 3 : 0); }
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		bSolid = false;
		A_SetSize(16, Height);
	}
}

// MAP=MAP21 MODE=7 tools/smoke.sh: the apparatus's views, for its look board (a screenshot every 35 tics,
// tools/smoke_MAP21_7.cfg: two a view, the later one kept). Posed, monsters gone (LongRunTest does that).
class LongRunLookViews : EventHandler
{
	const OFF = 8192;
	int tic, n;
	static const double V[] = {
		// x, y, angle, pitch; THEN is y + OFF (the hall, the vestibule, the pocket; then each again NOW)
		512, 40 + OFF, 90, 0,          // the start THEN: the desk, its radio, the machine
		300, 200 + OFF, 140, 0,        // the hall's west side THEN: the bank, the console, the duct, the trolley
		760, 300 + OFF, 40, 0,         // the hall's east side THEN: the bank, the tall piece, the duct
		860, 330 + OFF, 0, 0,          // the doorway THEN: the notice and the calendar, 150 from the notice
		700, 250 + OFF, 90, -8,        // the north wall THEN: the schematic, the shutter
		980, 60 + OFF, 135, 0,         // the hall from the south-east THEN: the console, the banks
		760, 560 + OFF, 40, 0,         // the hall's north-east corner THEN: a tall piece by the bank's end
		280, 560 + OFF, 140, 0,        // the hall's north-west corner THEN: the other, the trolley
		1060, 300 + OFF, 50, 0,        // the vestibule THEN: the board, the desk, the notice
		1140, 400 + OFF, 0, 0,         // the vestibule THEN: the notice by the turnstile
		1330, 300 + OFF, 0, 0,         // the pocket THEN: the wall newspaper, frame 123
		1400, 600 + OFF, 270, 0,       // the pocket THEN: the trolley in its corner
		512, 40, 90, 0,                // the start NOW
		300, 200, 140, 0,              // the hall's west side NOW: the bank's ghost, the duct open
		760, 300, 40, 0,               // the hall's east side NOW
		860, 330, 0, 0,                // the doorway NOW: the notice's ghost, the calendar yellowed
		1060, 300, 50, 0,              // the vestibule NOW: the board's ghost
		1140, 400, 0, 0,               // the vestibule NOW: the notice's ghost
		1330, 300, 0, 0,               // the corridor NOW: the newspaper's ghost
		1400, 600, 270, 0              // the corridor NOW, looking south
	};

	override void WorldTick()
	{
		if (CVar.GetCVar("ajar_autotest").GetInt() != 7 || !(level.mapname ~== "MAP21")) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 10) mo.bInvisible = true;
		if (tic < 20 || (tic - 20) % 70) return;
		int i = (tic - 20) / 70;
		if (i * 4 >= V.Size()) { if (i * 4 == V.Size()) Console.Printf("AJARTEST lookViewsDone=1"); return; }
		double x = V[i * 4], y = V[i * 4 + 1];
		mo.SetOrigin((x, y, level.PointInSector((x, y)).floorplane.ZatPoint((x, y))), false);
		mo.angle = V[i * 4 + 2];
		mo.pitch = V[i * 4 + 3];
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
		Console.Printf("AJARTEST info look view %d at %.0f %.0f", i, x, y);
	}
}
