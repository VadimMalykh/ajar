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
//    pTag) that is still in its log (MixGoOnAs drops the rest); and every
//    key lever pull (keys.zs; AjarGoLog.kTic, kTag, kNum: KEY PULLS).
//  * For a shutter worked by key levers (keys.zs), HOLDS too: for every
//    moment at which the earlier selves' own key pulls, as logged, have every
//    lever of its set live at once, a span from that tic for the set's time
//    (KeyHolds).
//  * For a Pair joined for a time (goes.zs, AjarTogether args[1]), HOLDS too:
//    the spans in which the earlier selves' own hangings, as logged, have it
//    joined by the live rules (the second leaf hung within TOGETHER_TICS of
//    the first, in frames of which one has such a lamp: from that tic for the
//    lamps' seconds, or until a leaf is taken down), one row for the Pair
//    (PAIR SPANS: jFa, jFb, jFrom, jTo, for PairJoinIn(frame)).
// It is a forecast of the records and nothing more: if the live game differs
// (a pull that finds the press not up) the table is not corrected.
// Two questions: HoldIn(tag), the tics until some earlier self begins to hold
// that shutter (0 while one holds it, -1 if none will), and PullIn(tag), the
// tics until an earlier self's next pull of that press (-1 if none); and
// KeyPullIn(tag, n) (keys.zs), the tics until an earlier self's next pull of a
// key lever of the set `tag` other than number n. The lamps ask them
// (AjarShutLamp, AjarPressLamp, shut.zs; AjarKeyLamp, keys.zs): amber within SOON.
// The clock at the top draws it as a bar under the text (TableBar): a dark
// strip for tic 0 to the clock's length, one row for each shutter, screen or
// sprung frame's plate an earlier self holds in this go (green where held,
// in a fixed order: shutters by tag, then plates by frame), a gold tick at
// each pull and each key pull, a white cursor at this go's tic. The ui only reads the timetable.

class AjarTable play
{
	bool on;                            // a room of goes or a fight of goes, with an earlier self
	Array<int> rTag, rFrame;            // the rows: a shutter's tag, or (rTag 0) a sprung frame's plate, its frame
	Array<int> rPair;                   // or (both 0) a Pair joined for a time: its args[4] (0 for the others)
	Array<int> jFa, jFb, jFrom, jTo;    // the spans a Pair is joined for a time: its two frames, first tic, the tic after the last
	Array<int> sRow, sSelf, sFrom, sTo; // the holds: row, earlier self (its take), first tic, the tic after the last
	Array<int> pSelf, pTic, pTag;       // the pulls: earlier self, tic, the press's tag
	Array<int> kSelf, kTic, kTag, kNum; // the key pulls (keys.zs): earlier self, tic, the shutter's tag, the lever's number

	bool Empty() { return !rTag.Size() && !sRow.Size() && !pTic.Size() && !kTic.Size(); }
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
		for (int i = 0; i < logs.Size(); i++) { keyNow.Push(logs[i].pTic.Size()); keyNow.Push(logs[i].kTic.Size()); }
		for (int i = 0; i < takes.Size() - 1 && i < logs.Size(); i++) keyNow.Push(logs[i].tic.Size());
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
		// a shutter worked by key levers: held while the earlier selves' own pulls have it keyed (keys.zs)
		for (int r = 0; r < sh.Size(); r++)
		{
			KeyHolds(sh[r].args[0], n);
			for (int e = 0; e < khFrom.Size(); e++) { sRow.Push(r); sSelf.Push(khSelf[e]); sFrom.Push(khFrom[e]); sTo.Push(khTo[e]); }
		}
		// a Pair joined for a time: held while the earlier selves' own hangings have it joined (goes.zs)
		Array<int> pairs;
		PairHolds(n);
		for (int e = 0; e < phPair.Size(); e++)
		{
			int q = pairs.Find(phPair[e]);
			if (q == pairs.Size()) pairs.Push(phPair[e]);
			sRow.Push(rows + q); sSelf.Push(phSelf[e]); sFrom.Push(phFrom[e]); sTo.Push(phTo[e]);
			timetable.jFa.Push(phFa[e]); timetable.jFb.Push(phFb[e]); timetable.jFrom.Push(phFrom[e]); timetable.jTo.Push(phTo[e]);
		}
		// only the rows that some earlier self holds, in their order
		Array<int> keep;
		for (int r = 0; r < rows + pairs.Size(); r++)
		{
			keep.Push(-1);
			if (sRow.Find(r) == sRow.Size()) continue;
			keep[r] = timetable.rTag.Size();
			timetable.rTag.Push(r < sh.Size() ? sh[r].args[0] : 0);
			timetable.rFrame.Push(r < sh.Size() || r >= rows ? 0 : fp[r - sh.Size()].args[0]);
			timetable.rPair.Push(r < rows ? 0 : pairs[r - rows]);
		}
		for (int i = 0; i < sRow.Size(); i++)
		{
			timetable.sRow.Push(keep[sRow[i]]); timetable.sSelf.Push(sSelf[i]); timetable.sFrom.Push(sFrom[i]); timetable.sTo.Push(sTo[i]);
		}
		for (int i = 0; i < n && i < logs.Size(); i++)
			for (int e = 0; e < logs[i].pTic.Size(); e++) { timetable.pSelf.Push(i); timetable.pTic.Push(logs[i].pTic[e]); timetable.pTag.Push(logs[i].pTag[e]); }
		for (int i = 0; i < n && i < logs.Size(); i++)
			for (int e = 0; e < logs[i].kTic.Size(); e++)
			{
				timetable.kSelf.Push(i); timetable.kTic.Push(logs[i].kTic[e]); timetable.kTag.Push(logs[i].kTag[e]); timetable.kNum.Push(logs[i].kNum[e]);
			}
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

	// Tics until the earlier selves' hangings join a Pair for a time in frame `id` (0: they have it joined now; -1: never).
	int PairJoinIn(int id)
	{
		let tb = Table();
		if (!tb.on) return -1;
		int best = -1;
		for (int i = 0; i < tb.jFrom.Size(); i++)
		{
			if (tb.jFa[i] != id && tb.jFb[i] != id) continue;
			if (tb.jFrom[i] <= ot && ot < tb.jTo[i]) return 0;
			if (tb.jFrom[i] > ot && (best < 0 || tb.jFrom[i] - ot < best)) best = tb.jFrom[i] - ot;
		}
		return best;
	}

	// The spans in which the earlier selves' own hangings (of the first n takes), as logged, have a Pair
	// joined for a time, by the live rules (Hang, InTime, JoinFor, Unhang): phPair (its args[4]), phSelf
	// (the self whose hanging joined it), phFa, phFb (the frames), phFrom, phTo (the tic after the last).
	Array<int> phPair, phSelf, phFa, phFb, phFrom, phTo;
	void PairHolds(int n)
	{
		phPair.Clear(); phSelf.Clear(); phFa.Clear(); phFb.Clear(); phFrom.Clear(); phTo.Clear();
		let h = Doors();
		// the hangings and takings down of Pair leaves, in the order of their tics
		Array<int> et, ed, es;
		Array<AjarFrame> ef;
		for (int i = 0; i < n && i < logs.Size(); i++)
		{
			AjarGoLog lg = logs[i];
			for (int e = 0; e < lg.tic.Size(); e++)
			{
				int di = lg.door[e];
				if (di >= dDoor.Size() || !dDoor[di] || !dDoor[di].IsPair() || lg.frm[e] == lg.fFrm[e]) continue;
				int j = 0;
				while (j < et.Size() && et[j] <= lg.tic[e]) j++;
				et.Insert(j, lg.tic[e]); ed.Insert(j, di); es.Insert(j, i); ef.Insert(j, lg.frm[e]);
			}
		}
		if (!et.Size()) return;
		// each leaf: where it hangs, since when; and the span that is open (-1: none)
		Array<AjarFrame> at;
		Array<int> since, open;
		for (int i = 0; i < dDoor.Size(); i++) { at.Push(d0Frame[i]); since.Push(-1000000); open.Push(-1); }
		for (int e = 0; e < et.Size(); e++)
		{
			int di = ed[e], t = et[e];
			AjarDoor d = dDoor[di];
			int ti = dDoor.Find(d.Twin());
			if (ti == dDoor.Size()) continue;
			// taken down (or moved): the span it was joined in ends
			if (at[di] && at[di] != ef[e] && open[di] >= 0)
			{
				phTo[open[di]] = min(phTo[open[di]], t);
				open[ti] = open[di] = -1;
			}
			at[di] = ef[e];
			if (!ef[e]) continue;
			since[di] = t;
			if (!at[ti] || t - since[ti] > AjarHandler.TOGETHER_TICS || (!h.Together(ef[e]) && !h.Together(at[ti]))) continue;
			if (open[ti] >= 0 && phTo[open[ti]] > t) continue;       // (joined already: not as the live game has it)
			int secs = h.JoinSeconds(ef[e].args[0], at[ti].args[0]);
			if (secs <= 0) continue;
			phPair.Push(d.args[4]); phSelf.Push(es[e]); phFa.Push(ef[e].args[0]); phFb.Push(at[ti].args[0]);
			phFrom.Push(t); phTo.Push(t + 35 * secs);
			open[di] = open[ti] = phFrom.Size() - 1;
		}
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
		for (int i = 0; i < timetable.kTic.Size(); i++)
			if (timetable.kTic[i] <= len) Fill(x0 + W * timetable.kTic[i] / len - 1, y0, 2, h, 0xFFC020);
		Fill(x0 + W * ot / len - 1, y0 - 2, 2, h + 4, 0xFFFFFF);
	}
}
