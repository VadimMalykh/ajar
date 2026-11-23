// The sound lab (map SOUND, tools/map_soundlab.py): door sounds and music to
// judge by ear. MAP=SOUND ./run.sh
//
// Four switches on the east wall, each a line that activates an
// AjarSoundButton (args[0]: 1 TAKE, 2 SET, 3 MUSIC +, 4 MUSIC -):
//   TAKE, SET    step the sound of taking (or hanging) a door on: Doom's, A,
//                B, C, Doom's ... (src/sndinfo.txt, tools/sfx.py), play it and
//                say which it is. Every door action then uses it
//                (AjarHandler.PlayTake / PlaySet / PlaySwap in ajar.zs).
//   MUSIC +, -   step through silence and the tracks listed in ajmusic.txt
//                (tools/music.py: LUMP|Title|what it is for), start the chosen
//                one from its beginning and say what it is.
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
	int take, setv;             // 0 Doom's, 1 A, 2 B, 3 C
	int track;                  // 0 silence, 1.. the tracks of ajmusic.txt
	Array<string> lumps, titles, whats;
	bool changed;               // what S_ChangeMusic said the last time

	clearscope static string SoundOf(bool isTake, int i)
	{
		static const string takes[] = { "", "ajar/take1", "ajar/take2", "ajar/take3" };
		static const string sets[] = { "", "ajar/set1", "ajar/set2", "ajar/set3" };
		return isTake ? takes[i] : sets[i];
	}

	clearscope static string NameOf(bool isTake, int i)
	{
		static const string takes[] = { "Doom's", "A, squeak and knock", "B, creak and pins", "C, pins only" };
		static const string sets[] = { "Doom's", "A, thud and clack", "B, slide and thud", "C, two pins" };
		return isTake ? takes[i] : sets[i];
	}

	AjarHandler Game() { return AjarHandler(EventHandler.Find("AjarHandler")); }

	override void WorldLoaded(WorldEvent e)
	{
		if (e.IsSaveGame) return;
		ReadTracks();
	}

	// ajmusic.txt: one line a track, LUMP|Title|what it is for
	void ReadTracks()
	{
		lumps.Clear();
		titles.Clear();
		whats.Clear();
		int lump = Wads.CheckNumForFullName("ajmusic.txt");
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
			lumps.Push(f[0]);
			titles.Push(f[1]);
			whats.Push(f[2]);
		}
	}

	void Press(int what, Actor who)
	{
		let h = Game();
		if (!h) return;
		if (what == 1)
		{
			take = (take + 1) % 4;
			h.takeSound = SoundOf(true, take);
			h.PlayTake(who);
			h.Say("Take sound: " .. NameOf(true, take));
		}
		else if (what == 2)
		{
			setv = (setv + 1) % 4;
			h.setSound = SoundOf(false, setv);
			h.PlaySet(who);
			h.Say("Set sound: " .. NameOf(false, setv));
		}
		else if (what == 3 || what == 4)
		{
			int n = lumps.Size() + 1;
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
		string m = track ? String.Format("%d/%d %s", track, lumps.Size(), titles[track - 1]) : "silence";
		Line3(0, "take: " .. NameOf(true, take), Font.CR_GOLD);
		Line3(1, "set: " .. NameOf(false, setv), Font.CR_GOLD);
		Line3(2, "music: " .. m, Font.CR_GREEN);
	}

	ui void Line3(int i, string s, int colour)
	{
		Screen.DrawText(SmallFont, colour, 632 - SmallFont.StringWidth(s), 6 + 11 * i, s, DTA_VirtualWidth, 640, DTA_VirtualHeight, 400);
	}

	// --- the walkthrough (ajar_autotest 1) -----------------------------------------
	// Steps 10 tics apart. Music + through every track; then four rounds of
	// TAKE and SET (each moves both sounds on one, so the four go round to
	// Doom's again), each round taking a door from 101, hanging it in 103,
	// taking it again and swapping it for the door in 102, and hanging that in
	// 101; GREEN taken from where it leans; Music + once more (silence) and
	// Music - all the way round back to silence.
	int tic, checks, fails;
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
		string meant = want ? String.Format("Music %d/%d: %s / %s", want, lumps.Size(), titles[want - 1], whats[want - 1]) : "Music: silence";
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
			for (int i = 1; i <= 3; i++)
			{
				string a = SoundOf(true, i), b = SoundOf(false, i);
				Sound sa = a, sb = b;
				// (the length is what the engine made of the WAV; under -nosound, which loads none, every sound is 0.25 s)
				Check("defined_take" .. i, sa != 0, String.Format("lump %s %d, length %.3f s", "ajtake" .. i,
					Wads.CheckNumForName("ajtake" .. i, Wads.ns_sounds), S_GetLength(sa)));
				Check("defined_set" .. i, sb != 0, String.Format("lump %s %d, length %.3f s", "ajset" .. i,
					Wads.CheckNumForName("ajset" .. i, Wads.ns_sounds), S_GetLength(sb)));
			}
			string all = "";
			bool ok = n > 0;
			for (int i = 0; i < n; i++)
			{
				int l = Wads.CheckNumForName(lumps[i], Wads.ns_music);
				all = all .. String.Format(" %s=%d", lumps[i], l >= 0);
				if (l < 0) ok = false;
			}
			Check("manifest", ok, String.Format("%d tracks:%s", n, all));
			Check("start", take == 0 && setv == 0 && track == 0 && h.takeSound == "" && h.setSound == "" && !h.carried
				&& h.FindFrame(101).door && h.FindFrame(102).door && !h.FindFrame(103).door && !h.FindFrame(104).door);
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
		// four rounds of the door sounds
		int r0 = m0 + n;
		if (s >= r0 && s < r0 + 28)
		{
			int k = (s - r0) / 7, j = (s - r0) % 7, v = (k + 1) % 4;
			string at = String.Format("round%d_", k + 1);
			bool own = v != 0;
			switch (j)
			{
			case 0:
				PressAt(mo, 1);
				Check(at .. "takeSelected", take == v && h.takeSound == SoundOf(true, v) && h.said == "Take sound: " .. NameOf(true, v),
					String.Format("%s (%s)", NameOf(true, take), h.TakeName()));
				break;
			case 1:
				PressAt(mo, 2);
				Check(at .. "setSelected", setv == v && h.setSound == SoundOf(false, v) && h.said == "Set sound: " .. NameOf(false, v),
					String.Format("%s (%s)", NameOf(false, setv), h.SetName()));
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
					&& (own ? h.swapSetTics == 7 && h.swapBy == mo : h.swapSetTics == 0),
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
		int g0 = r0 + 28;
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
			Console.Printf("AJARTEST soundlab=%s  (%d checks, %d failed)", fails ? "FAILED" : "ok", checks, fails);
		}
	}
}
