// The sound lab (map SOUND, tools/map_soundlab.py): door sounds and music to
// judge by ear. MAP=SOUND ./run.sh
//
// Four switches on the east wall, each a line that activates an
// AjarSoundButton (args[0]: 1 TAKE, 2 SET, 3 MUSIC +, 4 MUSIC -):
//   TAKE, SET    step the sound of taking (or hanging) a door on: the
//                game's, 1, 2, ... n, the game's ..., the candidates listed in
//                ajsounds.txt (tools/sfx.py: kind|logical name|its name[|pitch]:
//                the name is the game's own, ajar/take1, or one of Doom's,
//                misc/w_pkup; the pitch 1 if not given; Doom's old door the
//                first), play it and say which it is, counting the game's as
//                the first ("1 of 8: the game's: field drops"). The game's is
//                what every level plays (AjarHandler's TAKE_SOUND ... SET_PITCH
//                in ajar.zs, an empty takeSound / setSound); ajsounds.txt's
//                gametake and gameset lines only name it for the lab. Every
//                door action then uses the one chosen (AjarHandler.PlayTake /
//                PlaySet / PlaySwap).
//   MUSIC +, -   step through silence and the tracks listed in ajmusic.txt
//                (tools/music_trial.py, from trial/music/: LUMP|Title|what it
//                is for), start the chosen one from its beginning and say
//                what it is. A build with none says where they go.
// Nothing about the candidates is written here: both lists are read at load.
// What is chosen is always on screen, top right. The level begins with
// the game's sounds and silence.
//
// MAP=SOUND MODE=1 tools/smoke.sh: the walkthrough at the end of this file.

class AjarSoundButton : Actor
{
	Default
	{
		+NOBLOCKMAP +NOGRAVITY +INVISIBLE
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}

	override void Activate(Actor activator)
	{
		let lab = AjarSoundLab(EventHandler.Find("AjarSoundLab"));
		if (lab) lab.Press(args[0], activator);
	}
}

class AjarSoundLab : EventHandler
{
	int take, setv;             // 0 the game's, 1.. the candidates of ajsounds.txt
	string gameTake, gameSet;   // ajsounds.txt's gametake and gameset: logical name, what it is, pitch
	string gameTakeName, gameSetName;
	double gameTakePitch, gameSetPitch;
	int track;                  // 0 silence, 1.. the tracks of ajmusic.txt
	Array<string> takes, takeNames, sets, setNames;     // logical sound names and what each is
	Array<double> takePitches, setPitches;
	Array<string> lumps, titles, whats;
	bool changed;               // what S_ChangeMusic said the last time

	clearscope static string NoMusic() { return "No music in this build: candidates go in trial/music/, then build again"; }

	// a lump's lines, split at |, of `fields` fields or more: all in one array, `fields` to a line
	static void ReadList(string name, int fields, out Array<string> res)
	{
		res.Clear();
		int lump = Wads.CheckNumForFullName(name);
		if (lump < 0) return;
		string text = Wads.ReadLump(lump);
		Array<string> lines;
		text.Split(lines, "\n", TOK_SKIPEMPTY);
		for (int i = 0; i < lines.Size(); i++)
		{
			string l = lines[i];
			l.Replace("\r", "");
			Array<string> f;
			l.Split(f, "|");
			if (f.Size() < fields) continue;
			for (int k = 0; k < fields; k++) res.Push(f[k]);
		}
	}

	// ajsounds.txt: kind|logical name|its name[|pitch], each line as 4 fields
	static void ReadSounds(out Array<string> res)
	{
		res.Clear();
		int lump = Wads.CheckNumForFullName("ajsounds.txt");
		if (lump < 0) return;
		string text = Wads.ReadLump(lump);
		Array<string> lines;
		text.Split(lines, "\n", TOK_SKIPEMPTY);
		for (int i = 0; i < lines.Size(); i++)
		{
			string l = lines[i];
			l.Replace("\r", "");
			Array<string> f;
			l.Split(f, "|");
			if (f.Size() < 3) continue;
			for (int k = 0; k < 3; k++) res.Push(f[k]);
			res.Push(f.Size() > 3 ? f[3] : "1");
		}
	}

	// one of the game's own (ajar/...), not one of Doom's
	clearscope static bool IsOwn(string logical) { return logical.IndexOf("ajar/") == 0; }

	// the lump of a logical sound: ajar/take2 is ajtake2 (tools/sfx.py)
	clearscope static string LumpOf(string logical)
	{
		string l = logical;
		l.Replace("ajar/", "aj");
		return l;
	}

	// "3 of 8: Doom: weapon pick-up", "1 of 8: the game's: field drops": the game's counted as the first
	clearscope string Label(bool isTake, int i)
	{
		return String.Format("%d of %d: %s", i + 1, (isTake ? takes.Size() : sets.Size()) + 1,
			i == 0 ? "the game's: " .. (isTake ? gameTakeName : gameSetName) : isTake ? takeNames[i - 1] : setNames[i - 1]);
	}

	clearscope string SoundOf(bool isTake, int i)
	{
		if (i == 0) return "";
		return isTake ? takes[i - 1] : sets[i - 1];
	}

	clearscope double PitchOf(bool isTake, int i)
	{
		if (i == 0) return 0;
		return isTake ? takePitches[i - 1] : setPitches[i - 1];
	}

	clearscope string Said(bool isTake, int i)
	{
		return (isTake ? "Take sound " : "Set sound ") .. Label(isTake, i);
	}

	AjarHandler Game() { return AjarHandler(EventHandler.Find("AjarHandler")); }

	override void WorldLoaded(WorldEvent e)
	{
		if (e.IsSaveGame) return;
		ReadLists();
	}

	// ajsounds.txt: kind|logical name|its name[|pitch]; ajmusic.txt: LUMP|Title|what it is for
	void ReadLists()
	{
		Array<string> f;
		takes.Clear(); takeNames.Clear(); sets.Clear(); setNames.Clear(); takePitches.Clear(); setPitches.Clear();
		gameTake = ""; gameSet = ""; gameTakeName = "?"; gameSetName = "?"; gameTakePitch = 0; gameSetPitch = 0;
		ReadSounds(f);
		for (int i = 0; i + 3 < f.Size(); i += 4)
		{
			double p = f[i + 3].ToDouble();
			if (f[i] == "take") { takes.Push(f[i + 1]); takeNames.Push(f[i + 2]); takePitches.Push(p); }
			else if (f[i] == "set") { sets.Push(f[i + 1]); setNames.Push(f[i + 2]); setPitches.Push(p); }
			else if (f[i] == "gametake") { gameTake = f[i + 1]; gameTakeName = f[i + 2]; gameTakePitch = p; }
			else if (f[i] == "gameset") { gameSet = f[i + 1]; gameSetName = f[i + 2]; gameSetPitch = p; }
		}
		lumps.Clear(); titles.Clear(); whats.Clear();
		ReadList("ajmusic.txt", 3, f);
		for (int i = 0; i + 2 < f.Size(); i += 3)
		{
			lumps.Push(f[i]);
			titles.Push(f[i + 1]);
			whats.Push(f[i + 2]);
		}
	}

	void Press(int what, Actor who)
	{
		let h = Game();
		if (!h) return;
		if (what == 1)
		{
			take = (take + 1) % (takes.Size() + 1);
			h.takeSound = SoundOf(true, take);
			h.takePitch = PitchOf(true, take);
			h.PlayTake(who);
			h.Say(Said(true, take));
		}
		else if (what == 2)
		{
			setv = (setv + 1) % (sets.Size() + 1);
			h.setSound = SoundOf(false, setv);
			h.setPitch = PitchOf(false, setv);
			h.PlaySet(who);
			h.Say(Said(false, setv));
		}
		else if (what == 3 || what == 4)
		{
			int n = lumps.Size() + 1;
			if (n == 1)
			{
				h.Say(NoMusic());
				return;
			}
			track = (track + (what == 3 ? 1 : n - 1)) % n;
			if (track == 0)
			{
				changed = S_ChangeMusic("", 0, true, true);
				h.Say("Music: silence");
			}
			else
			{
				changed = S_ChangeMusic(lumps[track - 1], 0, true, true);
				h.Say(String.Format("Music %d/%d: %s\n%s", track, lumps.Size(), titles[track - 1], whats[track - 1]));
			}
		}
	}

	override void RenderOverlay(RenderEvent e)
	{
		if (automapactive) return;
		string m = !lumps.Size() ? "none in this build" : track ? String.Format("%d/%d %s", track, lumps.Size(), titles[track - 1]) : "silence";
		Line3(0, "take " .. Label(true, take), Font.CR_GOLD);
		Line3(1, "set " .. Label(false, setv), Font.CR_GOLD);
		Line3(2, "music: " .. m, Font.CR_GREEN);
	}

	ui void Line3(int i, string s, int colour)
	{
		Screen.DrawText(SmallFont, colour, 632 - SmallFont.StringWidth(s), 6 + 11 * i, s, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
	}

	// --- the walkthrough (ajar_autotest 1) -----------------------------------------
	// Steps 10 tics apart, every count taken from the two lists. Every sound of
	// ajsounds.txt defined and its lump there, the game's two as AjarHandler
	// plays them, every lump of ajmusic.txt there;
	// Music + through every track; then rounds of TAKE and SET (each moves
	// both sounds on one; as many rounds as it takes for both to come round
	// to the game's together, so with as many sets as takes every pair of the
	// same number is heard together, and the game's pair), each round taking a door from
	// 101, hanging it in 103, taking it again and swapping it for the door in
	// 102, and hanging that in 101; GREEN taken from where it leans; Music +
	// once more (silence) and Music - all the way round back to silence.
	int tic, checks, fails, rounds;
	AjarDoor d, old;

	void Check(string what, bool ok, string info = "")
	{
		checks++;
		if (!ok) fails++;
		Console.Printf("AJARTEST %s=%d%s%s", what, ok, info != "" ? "  " : "", info);
	}

	void Pose(Actor mo, double x, double y, double ang)
	{
		mo.SetOrigin((x, y, 0), false);
		mo.angle = ang;
		mo.pitch = 0;
		mo.vel = (0, 0, 0);
	}

	void PressAt(Actor mo, int what)
	{
		Pose(mo, 960, what == 1 ? 544 : what == 2 ? 448 : what == 4 ? 288 : 192, 0);
		let h = Game();
		Line l = h.FindLine(800 + what);
		if (l) l.Activate(mo, 0, SPAC_Use);
		else Console.Printf("AJARTEST info no switch line %d", 800 + what);
	}

	void UseFrame(Actor mo, int id)
	{
		let f = Game().FindFrame(id);
		Pose(mo, f.pos.x, 700, 90);
		f.Activate(mo);
	}

	void CheckTrack(string what, int want)
	{
		string l = want ? lumps[want - 1] : "";
		bool there = want == 0 || Wads.CheckNumForName(l, Wads.ns_music) >= 0;
		// (S_ChangeMusic's answer is printed, not checked: under -nosound the
		// music is off and it is always false)
		string said = Game().said;
		said.Replace("\n", " / ");
		string meant = want ? String.Format("Music %d/%d: %s / %s", want, lumps.Size(), titles[want - 1], whats[want - 1])
			: lumps.Size() ? "Music: silence" : NoMusic();
		Check(what, track == want && there && said == meant,
			String.Format("track %d (want %d) %s, S_ChangeMusic %d, said \"%s\"", track, want, want ? l : "silence", changed, said));
	}

	override void WorldTick()
	{
		if (!CVar.GetCVar("ajar_autotest").GetInt() || !(level.mapname ~== "SOUND")) return;
		let mo = players[consoleplayer].mo;
		let h = Game();
		if (!mo || !h) return;
		int t = tic++;
		if (t % 10) return;
		int s = t / 10;
		int n = lumps.Size();

		if (s == 1)
		{
			for (int i = 0; i < takes.Size() + sets.Size(); i++)
			{
				bool isTake = i < takes.Size();
				int k = isTake ? i + 1 : i + 1 - takes.Size();
				string name = SoundOf(isTake, k), lump = LumpOf(name);
				double p = PitchOf(isTake, k);
				Sound snd = name;
				// the game's own has its lump in the package; Doom's is known to the engine by name (its lump in the IWAD)
				bool own = IsOwn(name);
				int l = own ? Wads.CheckNumForName(lump, Wads.ns_sounds) : 0;
				// (the length is what the engine made of the sound; under -nosound, which loads none, every sound is 0.25 s)
				Check(String.Format("defined_%s%d", isTake ? "take" : "set", k), snd != 0 && l >= 0 && p >= 0.5 && p <= 2,
					String.Format("%s, %s, pitch %.2f, length %.3f s: %s", name, own ? String.Format("lump %s %d", lump, l) : "Doom's",
						p, S_GetLength(snd), isTake ? takeNames[k - 1] : setNames[k - 1]));
			}
			// the game's two: what ajsounds.txt names them is what AjarHandler plays with nothing chosen
			for (int i = 0; i < 2; i++)
			{
				bool isTake = i == 0;
				string name = isTake ? gameTake : gameSet, lump = LumpOf(name);
				string plays = isTake ? h.TakeName() : h.SetName();
				double p = isTake ? gameTakePitch : gameSetPitch, pp = isTake ? h.UsedTakePitch() : h.UsedSetPitch();
				Sound snd = name;
				bool own = IsOwn(name);
				int l = own ? Wads.CheckNumForName(lump, Wads.ns_sounds) : 0;
				Check(isTake ? "defined_gametake" : "defined_gameset", name != "" && name == plays && p == pp && snd != 0 && l >= 0,
					String.Format("%s, %s, pitch %.2f (the handler plays %s at %.2f), length %.3f s: %s", name,
						own ? String.Format("lump %s %d", lump, l) : "Doom's", p, plays, pp, S_GetLength(snd), Label(isTake, 0)));
			}
			Check("sounds", takes.Size() > 0 && sets.Size() > 0, String.Format("ajsounds.txt: %d takes, %d sets", takes.Size(), sets.Size()));
			string all = "";
			bool ok = true;
			for (int i = 0; i < n; i++)
			{
				int l = Wads.CheckNumForName(lumps[i], Wads.ns_music);
				all = all .. String.Format(" %s=%d", lumps[i], l >= 0);
				if (l < 0) ok = false;
			}
			Check("manifest", ok, String.Format("ajmusic.txt: %d tracks:%s", n, all));
			// as many rounds as it takes for both to come round to the game's together
			rounds = 1;
			while (rounds % (takes.Size() + 1) || rounds % (sets.Size() + 1)) rounds++;
			Check("start", take == 0 && setv == 0 && track == 0 && h.takeSound == "" && h.setSound == "" && h.takePitch == 0 && h.setPitch == 0 && !h.carried
				&& h.FindFrame(101).door && h.FindFrame(102).door && !h.FindFrame(103).door && !h.FindFrame(104).door,
				String.Format("%d rounds of the door sounds", rounds));
			return;
		}
		// music + through every track
		int m0 = 2;
		if (s >= m0 && s < m0 + n)
		{
			PressAt(mo, 3);
			CheckTrack(String.Format("musicNext%d", s - m0 + 1), s - m0 + 1);
			return;
		}
		// the rounds of the door sounds
		int r0 = m0 + n;
		if (s >= r0 && s < r0 + 7 * rounds)
		{
			int k = (s - r0) / 7, j = (s - r0) % 7;
			int vt = (k + 1) % (takes.Size() + 1), vs = (k + 1) % (sets.Size() + 1);
			string at = String.Format("round%d_", k + 1);
			switch (j)
			{
			case 0:
				PressAt(mo, 1);
				Check(at .. "takeSelected", take == vt && h.takeSound == SoundOf(true, vt) && h.takePitch == PitchOf(true, vt) && h.said == Said(true, vt),
					String.Format("%s (%s, pitch %.2f)", h.said, h.TakeName(), h.UsedTakePitch()));
				break;
			case 1:
				PressAt(mo, 2);
				Check(at .. "setSelected", setv == vs && h.setSound == SoundOf(false, vs) && h.setPitch == PitchOf(false, vs) && h.said == Said(false, vs),
					String.Format("%s (%s, pitch %.2f)", h.said, h.SetName(), h.UsedSetPitch()));
				break;
			case 2:
				d = h.FindFrame(101).door;
				UseFrame(mo, 101);
				Check(at .. "take", d && h.carried == d && !h.FindFrame(101).door, d ? d.Label() : "no door in 101");
				break;
			case 3:
				UseFrame(mo, 103);
				Check(at .. "hang", d && !h.carried && h.FindFrame(103).door == d);
				break;
			case 4:
				UseFrame(mo, 103);
				Check(at .. "takeAgain", d && h.carried == d && !h.FindFrame(103).door);
				break;
			case 5:
				old = h.FindFrame(102).door;
				UseFrame(mo, 102);
				Check(at .. "swap", old && h.FindFrame(102).door == d && h.carried == old
					&& h.swapSetTics == 9 && h.swapBy == mo,
					String.Format("%s off, %s on; set sound to come in %d tics", old ? old.Label() : "-", d ? d.Label() : "-", h.swapSetTics));
				break;
			case 6:
				Check(at .. "swapSetPlayed", h.swapSetTics == 0 && !h.swapBy);
				UseFrame(mo, 101);
				Check(at .. "hangTheOther", old && !h.carried && h.FindFrame(101).door == old);
				break;
			}
			return;
		}
		int g0 = r0 + 7 * rounds;
		if (s == g0)            // GREEN, where it leans
		{
			AjarDoor green;
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor o;
			while (o = AjarDoor(di.Next())) if (o.args[1] == 3) green = o;
			Pose(mo, 416, 640, 90);
			if (green) green.Used(mo);
			Check("takeLeaning", green && h.carried == green);
			return;
		}
		if (s == g0 + 1)
		{
			let green = h.carried;
			UseFrame(mo, 104);
			Check("hangLeaning", green && !h.carried && h.FindFrame(104).door == green);
			return;
		}
		// music + once more: round to silence; then music - all the way round
		int b0 = g0 + 2;
		if (s == b0)
		{
			PressAt(mo, 3);
			CheckTrack("musicNextToSilence", 0);
			return;
		}
		if (s > b0 && s <= b0 + n + 1)
		{
			int i = s - b0;
			PressAt(mo, 4);
			CheckTrack(String.Format("musicBack%d", i), (n + 1 - i) % (n + 1));
			return;
		}
		if (s == b0 + n + 2)
		{
			Pose(mo, 560, 160, 80);
			Console.Printf("AJARTEST soundlab=%s  (%d checks, %d failed; %d takes, %d sets, %d rounds, %d tracks)",
				fails ? "FAILED" : "ok", checks, fails, takes.Size(), sets.Size(), rounds, n);
		}
	}
}
