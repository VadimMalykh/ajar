// MODE=14 of the TEST map (MAP=TEST MODE=14 tools/smoke.sh): a cacodemon at
// floor height, a second one floating well above the RED door's opening and
// a demon, all set on the player, who stands still in the red room beyond
// RED. Each must come all the way through and out of the far recess into the
// red room; none may stay in either opening.
extend class AjarHandler
{
	Actor cacoTest[3];
	int cacoThrough[3];        // tic it was first in the red room, out of the recess
	int cacoInMouth[3];        // tics it has spent in an opening (either recess)
	int cacoLongest[3];        // ...the longest stay in one go

	bool InRedRoom(Actor a) { return a.pos.x > 0 && a.pos.x < 384 && a.pos.y > 2000 + a.radius && a.pos.y < 2384; }
	// in RED's recess or stub (the hall side) or in its far side's (the red room side)
	bool InRedMouth(Actor a)
	{
		bool hallSide = a.pos.y > 512 - a.radius && a.pos.y < 576 && a.pos.x > 96 && a.pos.x < 224;
		bool farSide = a.pos.y > 1936 && a.pos.y < 2000 + a.radius && a.pos.x > 128 && a.pos.x < 256;
		return hallSide || farSide;
	}

	void CacoScript(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE;
		if (t == 40)
		{
			Pose(mo, 192, 2250, 0, 270);
			cacoTest[0] = Actor.Spawn("Cacodemon", (180, 250, 0));
			cacoTest[1] = Actor.Spawn("Cacodemon", (420, 200, 120));
			cacoTest[2] = Actor.Spawn("Demon", (520, 330, 0));
			for (int i = 0; i < 3; i++)
			{
				cacoTest[i].angle = 90;
				cacoTest[i].target = mo;
				cacoTest[i].SetState(cacoTest[i].SeeState);
			}
		}
		if (t <= 40) return;
		for (int i = 0; i < 3; i++)
		{
			Actor a = cacoTest[i];
			if (!a) continue;
			if (!cacoThrough[i] && InRedRoom(a)) cacoThrough[i] = t;
			if (InRedMouth(a)) { cacoInMouth[i]++; cacoLongest[i] = max(cacoLongest[i], cacoInMouth[i]); }
			else cacoInMouth[i] = 0;
			if (t % 17 == 0)
			{
				let s = AjarSense(a.FindInventory("AjarSense"));
				Console.Printf("AJARTEST   %d %s at (%.1f,%.1f,%.1f) floor %.0f ceil %.0f target=%s via=%d mouth=%d dir=%d",
					i, a.GetClassName(), a.pos.x, a.pos.y, a.pos.z, a.floorz, a.ceilingz,
					a.target ? a.target.GetClassName() : 'none', s && s.via ? s.via.Index() : -1, cacoInMouth[i], a.movedir);
			}
		}
		if (t == 1400)
		{
			Check("cacoThroughDoor", cacoThrough[0] > 0);
			Check("cacoLeftTheOpening", cacoTest[0] && InRedRoom(cacoTest[0]) && cacoLongest[0] < 105);
			Check("floatingCacoThroughDoor", cacoThrough[1] > 0);
			Check("floatingCacoLeftTheOpening", cacoTest[1] && InRedRoom(cacoTest[1]) && cacoLongest[1] < 105);
			Check("demonThroughDoor", cacoThrough[2] > 0);
			Check("demonLeftTheOpening", cacoTest[2] && InRedRoom(cacoTest[2]) && cacoLongest[2] < 105);
			Console.Printf("AJARTEST info through at t=%d %d %d, longest in an opening %d %d %d tics",
				cacoThrough[0], cacoThrough[1], cacoThrough[2], cacoLongest[0], cacoLongest[1], cacoLongest[2]);
		}
	}
}
