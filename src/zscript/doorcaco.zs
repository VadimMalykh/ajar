// MODE=14 of the TEST map (MAP=TEST MODE=14 tools/smoke.sh): a cacodemon at
// floor height, a second one floating well above the RED door's opening and
// a demon, all set on the player, who stands still in the red room beyond
// RED. Each must come all the way through and out of the far recess into the
// red room; none may stay in either opening. Then a cacodemon while the
// player stands just beyond RED's far opening, and after he steps back.
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
		// Then the user's case: the player waits just beyond the door, where a
		// monster coming through would stand. A cacodemon must keep out of the
		// opening while he is there, and come through once he steps back.
		if (t == 1410)
		{
			for (int i = 0; i < 3; i++) if (cacoTest[i]) { cacoTest[i].ClearCounters(); cacoTest[i].Destroy(); }
			Pose(mo, 192, 2030, 0, 270);
			cacoTest[0] = Actor.Spawn("Cacodemon", (170, 380, 0));
			cacoTest[0].target = mo;
			cacoTest[0].SetState(cacoTest[0].SeeState);
			cacoThrough[0] = cacoInMouth[0] = cacoLongest[0] = 0;
		}
		if (t <= 40) return;
		for (int i = 0; i < 3; i++)
		{
			Actor a = cacoTest[i];
			if (!a) continue;
			if (!cacoThrough[i] && InRedRoom(a)) cacoThrough[i] = t;
			if (InRedMouth(a)) { cacoInMouth[i]++; cacoLongest[i] = max(cacoLongest[i], cacoInMouth[i]); }
			else cacoInMouth[i] = 0;
			if (t % 15 == 0) Console.Printf("AJARTEST info t=%d %d mouth %d %s", t, i, cacoInMouth[i], AjarDoorTrace.Of(a));
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
		if (t == 2100)
		{
			Check("cacoKeepsOutWhileBlocked", cacoTest[0] && !cacoThrough[0] && cacoLongest[0] < 105);
			Console.Printf("AJARTEST info blocked: longest in an opening %d tics; %s", cacoLongest[0], AjarDoorTrace.Of(cacoTest[0]));
			cacoLongest[0] = 0;
			Pose(mo, 192, 2250, 0, 270);
		}
		if (t == 2800)
		{
			Check("cacoComesOnceFree", cacoThrough[0] > 0 && cacoTest[0] && InRedRoom(cacoTest[0]) && cacoLongest[0] < 105);
			Console.Printf("AJARTEST info freed: through at t=%d, longest in an opening %d tics; %s", cacoThrough[0], cacoLongest[0], AjarDoorTrace.Of(cacoTest[0]));
		}
	}
}

// A monster's state, for the logs of these tests.
struct AjarDoorTrace play
{
	static string Of(Actor a)
	{
		if (!a) return "gone";
		let s = AjarSense(a.FindInventory("AjarSense"));
		bool steered = s && s.lure && a.target == s.lure && s.via;
		return String.Format("%s (%.1f,%.1f,%.1f) fl %.0f ce %.0f ang %.0f dir %d cnt %d vel (%.1f,%.1f,%.1f) hp %d tgt %s%s via %s img (%.0f,%.0f) str %d",
			a.GetClassName(), a.pos.x, a.pos.y, a.pos.z, a.floorz, a.ceilingz, a.angle, a.movedir, a.movecount,
			a.vel.x, a.vel.y, a.vel.z, a.health,
			a.target ? a.target.GetClassName() : 'none',
			a.target ? String.Format(" at (%.0f,%.0f,%.0f)", a.target.pos.x, a.target.pos.y, a.target.pos.z) : "",
			s && s.via ? String.Format("%d", s.via.Index()) : "-", s ? s.viaImg.x : 0, s ? s.viaImg.y : 0, s && s.viaStraight);
	}
}

// MODE=7 of the THEN lab (MAP=THEN MODE=7 tools/smoke.sh): following through
// the clocked door. It hangs in 105 (NOW) / 125 (THEN), the company bay's west
// wall. One monster at a time, of every kind that fits an opening, is set on
// the player in the bay, who walks through the door to the other time and on
// into the bay there; first NOW to THEN, then THEN to NOW. Each must come
// through and out of the far recess into the bay, without going back and
// forth between the times and without staying in an opening.
extend class ThenTest
{
	static const string followKinds[] = { "DoomImp", "HellKnight", "Demon", "Cacodemon", "Cacodemon", "BaronOfHell", "Archvile" };
	int fTrial, fStart, fOut, fOutAt, fFlips, fInMouth, fLongest;
	bool fWasThen, fGoing;
	Actor fDog;

	// in the bay at its own time `then`, out of the recess and clear of the mouth
	bool InBay(Actor a, bool then) { double y = a.pos.y - (then ? OFF : 0); return InThen(a) == then && a.pos.x > PEN_X + a.radius + 8 && a.pos.x < PEN_X + 512 && y > 0 && y < 512; }
	// in the clocked door's opening (recess or mouth) at either time
	bool InMouth(Actor a) { double y = a.pos.y - (InThen(a) ? OFF : 0); return a.pos.x < PEN_X + a.radius + 2 && a.pos.x > PEN_X - 64 && y > 224 - 32 && y < 288 + 32; }

	void ClockedFollow(Actor mo)
	{
		mo.player.cheats &= ~CF_NOTARGET;
		if (tic == 2)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			Array<Actor> gone;
			while (a = Actor(it.Next())) if (a.bIsMonster) gone.Push(a);
			for (int i = 0; i < gone.Size(); i++) { gone[i].ClearCounters(); gone[i].Destroy(); }
			HangIn(105);
			Check("clockedIn105", clocked.frame == F(105) && shadow.frame == F(125), h.said);
			fTrial = 0;
			fStart = 5;
		}
		if (tic < 5) { cur = tic; return; }
		int n = followKinds.Size();
		if (fTrial >= 2 * n) { if (!fGoing) { fGoing = true; cur = tic - 2; } return; }
		cur = tic;
		bool fromThen = fTrial >= n;               // the monster and the player start THEN
		string kind = followKinds[fTrial % n];
		bool floating = fTrial % n == 4;
		double ya = fromThen ? OFF : 0, yb = fromThen ? 0 : OFF;
		int st = tic - fStart;
		if (st == 0)
		{
			Pose(mo, PEN_X + 40, ya + 256, 180);
			fDog = Actor.Spawn(kind, (PEN_X + 380, ya + 120, floating ? 150 : FloorAt((PEN_X + 380, ya + 120))));
			fDog.angle = 180;
			fDog.target = mo;
			fDog.SetState(fDog.SeeState);
			fOut = fOutAt = fFlips = fInMouth = fLongest = 0;
			fWasThen = fromThen;
		}
		if (st == 20) Keys(WALKKEY);
		if (st == 50) { Keys(); WalkTo(PEN_X + 420, yb + 420); }
		if (st > 0 && fDog)
		{
			bool nowThen = InThen(fDog);
			if (nowThen != fWasThen) { fFlips++; fWasThen = nowThen; }
			if (InMouth(fDog)) { fInMouth++; fLongest = max(fLongest, fInMouth); } else fInMouth = 0;
			if (InBay(fDog, !fromThen)) { if (!fOutAt) fOutAt = st; fOut++; } else fOut = 0;
			if (st % 15 == 0) Info(String.Format("follow %d t+%d %s", fTrial, st, AjarDoorTrace.Of(fDog)));
		}
		if (st == 1050 || (fOut >= 70 && st > 60) || (st > 0 && (!fDog || fDog.health <= 0)))
		{
			string name = String.Format("%s%s%s", floating ? "floating" : "", kind, fromThen ? "ThenToNow" : "NowToThen");
			Check(name .. "_through", fDog && fDog.health > 0 && fOut >= 70 && fFlips == 1 && fLongest < 105,
				String.Format("out of the far recess at t+%d (the player through at about t+25), %d crossings, longest in an opening %d tics; %s",
					fOutAt, fFlips, fLongest, AjarDoorTrace.Of(fDog)));
			if (fDog) { fDog.ClearCounters(); fDog.Destroy(); }
			walking = false; Keys();
			fTrial++;
			fStart = tic + 1;
		}
	}
}
