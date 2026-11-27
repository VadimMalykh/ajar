// MAP23's decor (tools/dogs23.py places them, tools/gfx_dogs<n>.py paints them): sprites in one of three looks,
// args[0] the look (1 Vivarium, 2 Menagerie, 3 The Kennels), args[1] 1 THEN, 0 NOW. Frame A, C, E THEN and B, D,
// F NOW in looks 1, 2, 3. Not solid, not shot, no tid, counted for nothing: the level plays as without them.
class AjarDogsDecor : Actor
{
	Default
	{
		Radius 8;
		Height 16;
		+NOBLOCKMAP
		+DONTSPLASH
		+NOTAUTOAIMED
		+NOINTERACTION
	}
	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		frame = (clamp(args[0], 1, 3) - 1) * 2 + (args[1] ? 0 : 1);
	}
}

class AjarDogsBowl : AjarDogsDecor          // a feed bowl on the pen's side of a hatch
{
	Default { Height 8; }
	States { Spawn: AJVB A -1; Stop; }
}

class AjarDogsBucket : AjarDogsDecor        // a bucket with a brush, in a passage near its hatch
{
	Default { Height 24; }
	States { Spawn: AJVK A -1; Stop; }
}

class AjarDogsStore : AjarDogsDecor         // a store in a passage's dead corner
{
	Default { Height 40; }
	States { Spawn: AJVS A -1; Stop; }
}
