// The timetable (PLAN.md, "MAP32 room 3: plates in the fight, and the
// timetable"; MAP=MAP32 MODE=7 tools/smoke.sh).
//
// In a room of goes and a fight of goes (zone args[4] 2 or 3) the room shows
// what the earlier selves are about to do. At the start of every go, and
// again whenever the earlier selves or what is left of their records change
// (begin anew, a fight begun anew, the win that makes the fight a room of
// goes, going on as an earlier self, winding: Table() sees it by a key of the
// records' lengths), the table works out from their records what they will
// do in this go:
//  * HOLDS: for every AjarShutter of the room (shutters and screens), the
//    spans of this go's tics during which some earlier self holds it, by the
//    live game's rules: its recorded place within AjarPlate.REACH of a plate
//    that names the shutter and within FEET of the plate's height, or in a
//    sector of the shutter's args[3] tag; and for every plate of a sprung
//    frame (args[0] a frame) in the room, the spans an earlier self stands on
//    it. A span is [from, to): its first tic and the tic after its last.
//  * PULLS: every lever pull an earlier self will make (AjarGoLog.pTic,
//    pTag) that is still in its log (MixGoOnAs drops the rest).
// It is a forecast of the records and nothing more: if the live game differs
// (a pull that finds the press not up) the table is not corrected.
// Two questions: HoldIn(tag), the tics until some earlier self begins to hold
// that shutter (0 while one holds it, -1 if none will), and PullIn(tag), the
// tics until an earlier self's next pull of that press (-1 if none). The
// lamps ask them (AjarShutLamp, AjarPressLamp, shut.zs): amber within SOON.
// The clock at the top draws it as a bar under the text (TableBar): a dark
// strip for tic 0 to the clock's length, one row for each shutter, screen or
// sprung frame's plate an earlier self holds in this go (green where held,
// in a fixed order: shutters by tag, then plates by frame), a gold tick at
// each pull, a white cursor at this go's tic. The ui only reads the timetable.

class AjarTable play
{
	bool on;                            // a room of goes or a fight of goes, with an earlier self
	Array<int> rTag, rFrame;            // the rows: a shutter's tag, or (rTag 0) a sprung frame's plate, its frame
	Array<int> sRow, sSelf, sFrom, sTo; // the holds: row, earlier self (its take), first tic, the tic after the last
	Array<int> pSelf, pTic, pTag;       // the pulls: earlier self, tic, the press's tag

	bool Empty() { return !rTag.Size() && !sRow.Size() && !pTic.Size(); }
}

extend class AjarTimeHandler
{
	const SOON = 105;           // three seconds: a lamp is amber this long before
	AjarTable timetable;
	Array<int> tableKey, keyNow;

	bool TableOn() { return (goes || mixed) && phase == LIVE && takes.Size() > 1; }

	// The table, worked out again if the records have changed since.
	AjarTable Table()
	{
		keyNow.Clear();
		keyNow.Push(fight);
		keyNow.Push((goes ? 1 : 0) + (mixed ? 2 : 0) + (phase == LIVE ? 4 : 0));
		keyNow.Push(takes.Size());
		for (int i = 0; i < takes.Size() - 1; i++) keyNow.Push(takes[i].x.Size());
		for (int i = 0; i < logs.Size(); i++) keyNow.Push(logs[i].pTic.Size());
		bool same = timetable && keyNow.Size() == tableKey.Size();
		for (int i = 0; same && i < keyNow.Size(); i++) if (keyNow[i] != tableKey[i]) same = false;
		if (!same)
		{
			tableKey.Copy(keyNow);
			BuildTable();
		}
		return timetable;
	}

	static bool OnAt(AjarPlate p, AjarTake t, int j)
	{
		double z = p.homed ? p.homeZ : p.pos.z;
		return (t.x[j] - p.pos.x, t.y[j] - p.pos.y).Length() <= AjarPlate.REACH && abs(t.z[j] - z) <= AjarPlate.FEET;
	}

	void BuildTable()
	{
		timetable = new("AjarTable");
		if (!TableOn()) return;
		timetable.on = true;
		int n = takes.Size() - 1;
		// the shutters of the room, by tag; every plate; the sprung frames' plates of the room, by frame
		Array<AjarShutter> sh;
		Array<AjarPlate> all, fp;
		bool anyArea = false;
		let it = ThinkerIterator.Create("AjarShutter");
		AjarShutter s;
		while (s = AjarShutter(it.Next()))
		{
			int k, b;
			[k, b] = Where(s.pos.xy);
			if (k != fight) continue;
			s.Know();
			if (s.area.Size()) anyArea = true;
			int i = 0;
			while (i < sh.Size() && sh[i].args[0] <= s.args[0]) i++;
			sh.Insert(i, s);
		}
		let pi = ThinkerIterator.Create("AjarPlate");
		AjarPlate p;
		while (p = AjarPlate(pi.Next()))
		{
			all.Push(p);
			if (!p.args[0]) continue;
			int k, b;
			[k, b] = Where(p.pos.xy);
			if (k != fight) continue;
			int i = 0;
			while (i < fp.Size() && fp[i].args[0] <= p.args[0]) i++;
			fp.Insert(i, p);
		}
		int rows = sh.Size() + fp.Size();
		Array<int> sRow, sSelf, sFrom, sTo, start;
		for (int i = 0; i < n; i++)
		{
			AjarTake t = takes[i];
			int len = t.x.Size();
			start.Clear();
			for (int r = 0; r < rows; r++) start.Push(-1);
			for (int j = 0; j <= len; j++)
			{
				int sec = j < len && anyArea ? level.PointInSector((t.x[j], t.y[j])).Index() : -1;
				for (int r = 0; r < rows; r++)
				{
					bool on = false;
					if (j < len && r < sh.Size())
					{
						s = sh[r];
						on = sec >= 0 && s.area.Find(sec) < s.area.Size();
						for (int q = 0; !on && q < all.Size(); q++) on = all[q].args[1] == s.args[0] && OnAt(all[q], t, j);
					}
					else if (j < len) on = OnAt(fp[r - sh.Size()], t, j);
					if (on && start[r] < 0) start[r] = j;
					else if (!on && start[r] >= 0)
					{
						sRow.Push(r); sSelf.Push(i); sFrom.Push(start[r]); sTo.Push(j);
						start[r] = -1;
					}
				}
			}
		}
		// only the rows that some earlier self holds, in their order
		Array<int> keep;
		for (int r = 0; r < rows; r++)
		{
			keep.Push(-1);
			if (sRow.Find(r) == sRow.Size()) continue;
			keep[r] = timetable.rTag.Size();
			timetable.rTag.Push(r < sh.Size() ? sh[r].args[0] : 0);
			timetable.rFrame.Push(r < sh.Size() ? 0 : fp[r - sh.Size()].args[0]);
		}
		for (int i = 0; i < sRow.Size(); i++)
		{
			timetable.sRow.Push(keep[sRow[i]]); timetable.sSelf.Push(sSelf[i]); timetable.sFrom.Push(sFrom[i]); timetable.sTo.Push(sTo[i]);
		}
		for (int i = 0; i < n && i < logs.Size(); i++)
			for (int e = 0; e < logs[i].pTic.Size(); e++) { timetable.pSelf.Push(i); timetable.pTic.Push(logs[i].pTic[e]); timetable.pTag.Push(logs[i].pTag[e]); }
	}

	// Tics until some earlier self begins to hold the shutter of `tag` (0: one holds it now; -1: none will).
	int HoldIn(int tag)
	{
		let tb = Table();
		if (!tb.on) return -1;
		int best = -1;
		for (int i = 0; i < tb.sRow.Size(); i++)
		{
			if (tb.rTag[tb.sRow[i]] != tag) continue;
			if (tb.sFrom[i] <= ot && ot < tb.sTo[i]) return 0;
			if (tb.sFrom[i] > ot && (best < 0 || tb.sFrom[i] - ot < best)) best = tb.sFrom[i] - ot;
		}
		return best;
	}

	// Tics until an earlier self's next pull of the press of `tag` (-1: none).
	int PullIn(int tag)
	{
		let tb = Table();
		if (!tb.on) return -1;
		int best = -1;
		for (int i = 0; i < tb.pTic.Size(); i++)
			if (tb.pTag[i] == tag && tb.pTic[i] >= ot && (best < 0 || tb.pTic[i] - ot < best)) best = tb.pTic[i] - ot;
		return best;
	}

	// --- the bar under the clock (virtual 640 by 400) ---------------------------------
	ui void Fill(double x, double y, double w, double h, Color c, double a = 1)
	{
		double sx = Screen.GetWidth() / 640., sy = Screen.GetHeight() / 400.;
		int x1 = int(x * sx), y1 = int(y * sy), x2 = int((x + w) * sx), y2 = int((y + h) * sy);
		if (x2 <= x1) x2 = x1 + 1;
		if (y2 <= y1) y2 = y1 + 1;
		Screen.Dim(c, a, x1, y1, x2 - x1, y2 - y1);
	}

	// tic 0 to `len` (the clock's length), under the clock's text
	ui void TableBar(int len)
	{
		if (!timetable || !timetable.on || len <= 0 || ot >= len) return;
		double W = 240;
		double x0 = 320 - W / 2, y0 = 16 + BigFont.GetHeight();
		int rows = timetable.rTag.Size();
		double h = 4 + 4 * rows;
		Fill(x0 - 2, y0, W + 4, h, 0x101010, 0.75);
		for (int i = 0; i < timetable.sRow.Size(); i++)
		{
			int a = timetable.sFrom[i], b = min(timetable.sTo[i], len);
			if (a >= len) continue;
			Fill(x0 + W * a / len, y0 + 2 + 4 * timetable.sRow[i], max(W * (b - a) / len, 1), 3, 0x40E060);
		}
		for (int i = 0; i < timetable.pTic.Size(); i++)
			if (timetable.pTic[i] <= len) Fill(x0 + W * timetable.pTic[i] / len - 1, y0, 2, h, 0xFFC020);
		Fill(x0 + W * ot / len - 1, y0 - 2, 2, h + 4, 0xFFFFFF);
	}
}
