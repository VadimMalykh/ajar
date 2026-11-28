// MAP03 "Stage Door" (tools/map_hinges3.py): YELLOW in the lighting booth is an old door from the start
// (ajarmap.door(old=40); AjarHandler.WorldLoaded makes it AjarDoor.OLD; PLAN.md, "MAP03: YELLOW in the booth is an
// old door"). MAP=MAP03 MODE=3 tools/smoke.sh (tools/smoke_MAP03_3.cfg): what hangs in frame 105 at the first
// tics, two views for the look (tics 110 to 390: inside the booth facing it, the gods facing its far side 204),
// USE at it with empty hands and with a door in hand, and the walk from the gods into the booth and back.
extend class AjarHandler
{
	int oyChecks, oyFails;
	AjarDoor oyYellow, oyGreen;

	void OYCheck(string what, bool ok, string info = "")
	{
		oyChecks++;
		if (!ok) oyFails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}

	bool OYOpen(int id) { Line l = FindLine(id); return l && !(l.flags & Line.ML_BLOCKING); }

	// the textures of the far side's recess (both sectors of its line): its flats and its walls, as one line
	string OYFace(int id)
	{
		string s = "";
		Line l = FindLine(id);
		for (int k = 0; l && k < 2; k++)
		{
			Sector sec = k ? l.backsector : l.frontsector;
			if (!sec) continue;
			s = s .. " " .. TexMan.GetName(sec.GetTexture(Sector.floor)) .. " " .. TexMan.GetName(sec.GetTexture(Sector.ceiling));
			for (int i = 0; i < sec.lines.Size(); i++)
				for (int sd = 0; sd < 2; sd++)
				{
					Side side = sec.lines[i].sidedef[sd];
					if (!side) continue;
					for (int part = Side.top; part <= Side.bottom; part++)
					{
						string n = TexMan.GetName(side.GetTexture(part));
						if (n.Left(4) ~== "AJTR") s = s .. " " .. n;
					}
				}
		}
		return s;
	}

	// YELLOW's far side in the gods, aged forty years: every bit of the yellow surround is AJTR4Q / AJTF4Q
	bool OYAged(int id)
	{
		string s = OYFace(id) .. " ";
		return s.IndexOf(" AJTF4Q ") >= 0 && s.IndexOf(" AJTR4Q ") >= 0 && s.IndexOf(" AJTF4 ") < 0 && s.IndexOf(" AJTR4 ") < 0
			&& s.IndexOf(" AJTF4O ") < 0 && s.IndexOf(" AJTR4O ") < 0;
	}

	string OYState()
	{
		AjarFrame f = FindFrame(105);
		AjarDoor o = f ? f.door : null;
		if (!o) return "105 empty; carried " .. (carried ? carried.Label() : "-") .. "; " .. said;
		return String.Format("105: %s old %d years %d oldOf %d stuck %d onto %d (open %d/%d) shown %d AJQ4 %d; carried %s; said \"%s\"",
			o.Label(), o.IsOld(), o.oldYears, o.oldOf != null, o.Stuck(), o.args[0], OYOpen(105), OYOpen(o.args[0]),
			!o.bInvisible, o.sprite == Actor.GetSpriteIndex('AJQ4'), carried ? carried.Label() : "-", said);
	}

	void OYPress(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
	}

	void StageDoorOld(Actor mo, int t)
	{
		mo.player.cheats |= CF_GODMODE | CF_NOTARGET;
		if (t == 1)
		{
			let it = ThinkerIterator.Create("Actor");
			Actor a;
			while (a = Actor(it.Next())) if (a.bIsMonster) a.Destroy();       // nobody in the way of the walk or the views
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next()))
			{
				if (d.frame && d.frame.args[0] == 105) oyYellow = d;
				if (d.args[1] == 3) oyGreen = d;
			}
		}
		AjarFrame f = FindFrame(105);
		// --- at the first tics: YELLOW in 105 is an old door, forty years, open onto the gods
		if (t == 2)
		{
			int old = 0;
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next())) if (d.IsOld()) old++;
			OYCheck("oneTimeMap", AjarThen.Find() == null);
			OYCheck("yellowOldInBooth", oyYellow && f.door == oyYellow && oyYellow.IsOld() && oyYellow.Colour() == 4 && oyYellow.Label() == "YELLOW"
				&& oyYellow.oldYears == 40 && oyYellow.oldOf == null && oyYellow.args[3] == 0 && !oyYellow.nailer && old == 1, OYState());
			OYCheck("yellowStuck", oyYellow && oyYellow.Stuck());
			OYCheck("yellowOpenOntoGods", oyYellow && oyYellow.args[0] == 204 && OYOpen(105) && OYOpen(204), OYState());
			OYCheck("yellowLooksForty", oyYellow && !oyYellow.bInvisible && oyYellow.sprite == Actor.GetSpriteIndex('AJQ4'), OYState());
			OYCheck("godsSurroundAged", OYAged(204), OYFace(204));
			OYCheck("otherFarSidesNotAged", OYFace(201).IndexOf("Q") < 0 && OYFace(202).IndexOf("Q") < 0 && OYFace(203).IndexOf("Q") < 0
				&& OYFace(205).IndexOf("Q") < 0 && OYFace(206).IndexOf("Q") < 0, OYFace(202) .. " /" .. OYFace(206));
		}
		// --- the two views (tools/smoke_MAP03_3.cfg shoots at about 180 and 320)
		if (t == 110) { mo.bInvisible = true; Pose(mo, -540, 448, 224, 180); Console.Printf("AJARTEST info view 0: inside the booth, facing old YELLOW in 105"); }
		if (t == 250) { Pose(mo, -224, 600, 224, 90); Console.Printf("AJARTEST info view 1: the gods, facing YELLOW's far side 204"); }
		if (t > 110 && t < 390) mo.pitch = 0;
		// --- USE at 105 with empty hands: rusted to its frame
		if (t == 400) { mo.bInvisible = false; said = ""; Pose(mo, -680, 448, 224, 180); }
		if (t == 401) OYPress(mo);
		if (t == 403) OYCheck("rustedEmptyHanded", said == "Rusted to its frame." && !carried && f.door == oyYellow && oyYellow.IsOld() && OYOpen(204), OYState());
		// --- and with GREEN in hand: no swap, GREEN still in hand
		if (t == 405)
		{
			said = "";
			oyGreen.carried = true;
			oyGreen.Hide();
			carried = oyGreen;
			Pose(mo, -680, 448, 224, 180);
		}
		if (t == 406) OYPress(mo);
		if (t == 408)
			OYCheck("rustedWithADoorInHand", said == "Rusted to its frame." && carried == oyGreen && !oyGreen.frame && f.door == oyYellow && oyYellow.IsOld()
				&& OYOpen(204) && oyYellow.args[0] == 204, OYState());
		if (t == 409)
		{
			oyGreen.carried = false;
			oyGreen.SetOrigin(oyGreen.SpawnPoint, false);
			oyGreen.Show();
			carried = null;
		}
		// --- from the gods through YELLOW's far side into the booth
		if (t == 410) Pose(mo, -224, 700, 224, 90);
		Forward(mo, t, 410, 25);
		if (t == 450) OYCheck("walkedIntoBooth", mo.pos.x > -720 && mo.pos.x < -464 && mo.pos.y > 320 && mo.pos.y < 576 && mo.pos.z == 224,
			String.Format("(%.1f,%.1f,%.1f)", mo.pos.x, mo.pos.y, mo.pos.z));
		// --- and back out through YELLOW into the gods
		if (t == 455) Pose(mo, -660, 448, 224, 180);
		Forward(mo, t, 455, 25);
		if (t == 495)
		{
			OYCheck("walkedBackIntoGods", mo.pos.x > -448 && mo.pos.x < 0 && mo.pos.y > 128 && mo.pos.y < 768 && mo.pos.z == 224,
				String.Format("(%.1f,%.1f,%.1f)", mo.pos.x, mo.pos.y, mo.pos.z));
			OYCheck("yellowStillHangs", f.door == oyYellow && oyYellow.frame == f && oyYellow.IsOld() && !carried, OYState());
		}
		if (t == 500) Console.Printf("AJARTEST oldYellowDone=1 checks=%d failed=%d", oyChecks, oyFails);
	}
}
