// The sound lab (map SOUND, tools/map_soundlab.py): door sounds and music to
// judge by ear. MAP=SOUND ./run.sh
//
// Four switches on the east wall, each a line that activates an
// AjarSoundButton (args[0]: 1 TAKE, 2 SET, 3 MUSIC +, 4 MUSIC -):
//   TAKE, SET    step the sound of taking (or hanging) a door on: Doom's, 1,
//                2, ... n, Doom's ..., the candidates listed in ajsounds.txt
//                (tools/sfx.py: kind|logical name|its name), play it and say
//                which it is. Every door action then uses it
//                (AjarHandler.PlayTake / PlaySet / PlaySwap in ajar.zs).
//   MUSIC +, -   step through silence and the tracks listed in ajmusic.txt
//                (tools/music_trial.py, from trial/music/: LUMP|Title|what it
//                is for), start the chosen one from its beginning and say
//                what it is. A build with none says where they go.
// Nothing about the candidates is written here: both lists are read at load.
// What is chosen is always on screen, top right. The level begins with
// Doom's sounds and silence.
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
	int take, setv;             // 0 Doom's, 1.. the candidates of ajsounds.txt
	int track;                  // 0 silence, 1.. the tracks of ajmusic.txt
	Array<string> takes, takeNames, sets, setNames;     // logical sound names and what each is
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

	// the lump of a logical sound: ajar/take2 is ajtake2 (tools/sfx.py)
	clearscope static string LumpOf(string logical)
	{
		string l = logical;
		l.Replace("ajar/", "aj");
		return l;
	}

	// "2 of 5: door opens 2", or "Doom's"
	clearscope string Label(bool isTake, int i)
	{
		if (i == 0) return "Doom's";
		return String.Format("%d of %d: %s", i, isTake ? takes.Size() : sets.Size(), isTake ? takeNames[i - 1] : setNames[i - 1]);
	}

	clearscope string SoundOf(bool isTake, int i)
	{
		if (i == 0) return "";
		return isTake ? takes[i - 1] : sets[i - 1];
	}

	clearscope string Said(bool isTake, int i)
	{
		string what = isTake ? "Take sound" : "Set sound";
		return i ? what .. " " .. Label(isTake, i) : what .. ": Doom's";
	}

	AjarHandler Game() { return AjarHandler(EventHandler.Find("AjarHandler")); }

	override void WorldLoaded(WorldEvent e)
	{
		if (e.IsSaveGame) return;
		ReadLists();
	}

	// ajsounds.txt: kind|logical name|its name; ajmusic.txt: LUMP|Title|what it is for
	void ReadLists()
	{
		Array<string> f;
		takes.Clear(); takeNames.Clear(); sets.Clear(); setNames.Clear();
		ReadList("ajsounds.txt", 3, f);
		for (int i = 0; i + 2 < f.Size(); i += 3)
		{
			if (f[i] == "take") { takes.Push(f[i + 1]); takeNames.Push(f[i + 2]); }
			else if (f[i] == "set") { sets.Push(f[i + 1]); setNames.Push(f[i + 2]); }
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
			h.PlayTake(who);
			h.Say(Said(true, take));
		}
		else if (what == 2)
		{
			setv = (setv + 1) % (sets.Size() + 1);
			h.setSound = SoundOf(false, setv);
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
		Line3(0, take ? "take " .. Label(true, take) : "take: Doom's", Font.CR_GOLD);
		Line3(1, setv ? "set " .. Label(false, setv) : "set: Doom's", Font.CR_GOLD);
		Line3(2, "music: " .. m, Font.CR_GREEN);
	}

	ui void Line3(int i, string s, int colour)
	{
		Screen.DrawText(SmallFont, colour, 632 - SmallFont.StringWidth(s), 6 + 11 * i, s, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
	}

	// --- the walkthrough (ajar_autotest 1) -----------------------------------------
	// Steps 10 tics apart, every count taken from the two lists. Every sound of
	// ajsounds.txt defined and its lump there, every lump of ajmusic.txt there;
	// Music + through every track; then rounds of TAKE and SET (each moves
	// both sounds on one; as many rounds as it takes for both to come round
	// to Doom's together, so with as many sets as takes every pair of the same
	// number is heard together, and Doom's pair), each round taking a door from
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
				Sound snd = name;
				int l = Wads.CheckNumForName(lump, Wads.ns_sounds);
				// (the length is what the engine made of the WAV; under -nosound, which loads none, every sound is 0.25 s)
				Check(String.Format("defined_%s%d", isTake ? "take" : "set", k), snd != 0 && l >= 0,
					String.Format("%s, lump %s %d, length %.3f s: %s", name, lump, l, S_GetLength(snd), isTake ? takeNames[k - 1] : setNames[k - 1]));
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
			// as many rounds as it takes for both to come round to Doom's together
			rounds = 1;
			while (rounds % (takes.Size() + 1) || rounds % (sets.Size() + 1)) rounds++;
			Check("start", take == 0 && setv == 0 && track == 0 && h.takeSound == "" && h.setSound == "" && !h.carried
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
			bool own = vt != 0 || vs != 0;
			switch (j)
			{
			case 0:
				PressAt(mo, 1);
				Check(at .. "takeSelected", take == vt && h.takeSound == SoundOf(true, vt) && h.said == Said(true, vt),
					String.Format("%s (%s)", h.said, h.TakeName()));
				break;
			case 1:
				PressAt(mo, 2);
				Check(at .. "setSelected", setv == vs && h.setSound == SoundOf(false, vs) && h.said == Said(false, vs),
					String.Format("%s (%s)", h.said, h.SetName()));
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
					&& (own ? h.swapSetTics == 9 && h.swapBy == mo : h.swapSetTics == 0),
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
