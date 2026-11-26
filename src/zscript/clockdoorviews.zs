// MAP=MAP21 MODE=8 tools/smoke.sh: the clocked door's views, for its look board (tools/clockdoor_shots.sh,
// design/clockdoor-board.html; the looks: tools/gfx_clockdoor.py). One view each 70 tics, a screenshot every 35
// (tools/smoke_MAP21_8.cfg: two a view, the later one kept). Posed; the door is moved by hand between views
// (taken and hung with USE as a player does, put down as the tests put it down). Does nothing in any other mode.
class ClockDoorLookViews : EventHandler
{
	const OFF = 8192;
	int tic;
	AjarHandler h;
	AjarDoor clocked;

	void Pose(Actor mo, double x, double y, double ang, double pitch = 0)
	{
		mo.SetOrigin((x, y, level.PointInSector((x, y)).floorplane.ZatPoint((x, y))), false);
		mo.angle = ang;
		mo.pitch = pitch;
		mo.vel = (0, 0, 0);
		mo.ClearInterpolation();
	}
	void PressUse(Actor mo)
	{
		let pp = PlayerPawn(mo);
		pp.player.cmd.buttons = BT_USE;
		pp.CheckUse();
		pp.player.cmd.buttons = 0;
		pp.CheckUse();                               // the key let go: the next USE in this tic counts too
	}
	// USE from x, y facing ang: takes the door hung in the frame there, or hangs the door carried in it
	void UseAt(Actor mo, double x, double y, double ang) { Pose(mo, x, y, ang); PressUse(mo); }
	// the door carried put down against a wall at x, y, its face toward ang
	void Lean(Actor mo, double x, double y, double ang)
	{
		if (h.carried == clocked) { h.DropDoor(clocked, mo); h.carried = null; }
		clocked.SetOrigin((x, y, level.PointInSector((x, y)).floorplane.ZatPoint((x, y))), false);
		clocked.angle = ang;
	}

	override void WorldTick()
	{
		if (CVar.GetCVar("ajar_autotest").GetInt() != 8 || !(level.mapname ~== "MAP21")) return;
		let mo = players[consoleplayer].mo;
		if (!mo) return;
		tic++;
		if (tic == 10)
		{
			mo.bInvisible = true;
			h = AjarHandler(EventHandler.Find("AjarHandler"));
			let di = ThinkerIterator.Create("AjarDoor");
			AjarDoor d;
			while (d = AjarDoor(di.Next())) if (d.IsClocked() && !d.IsShadow()) clocked = d;
		}
		if (tic < 20 || (tic - 20) % 70 || !h || !clocked) return;
		int i = (tic - 20) / 70;
		string what;
		if (i == 0) { what = "a: THEN, the machine's frame 121, the door hung"; Pose(mo, 545, OFF + 182, 100); }
		else if (i == 1) { what = "b: THEN, the machine from further back, past the desk"; Pose(mo, 720, OFF + 50, 127); }
		else if (i == 2) { what = "c: NOW, the machine's frame 101, the door hung"; Pose(mo, 545, 182, 100); }
		else if (i == 3) { what = "e: NOW, the corridor's frame 103, empty"; Pose(mo, 1392, 480, 0); }
		else if (i == 4)
		{
			UseAt(mo, 512, 280, 90);                 // taken from 101
			UseAt(mo, 1460, 480, 0);                 // hung in 103, and so in 123 THEN
			what = String.Format("d: THEN, the pocket's frame 123, the door hung (%d)", h.FindFrame(123).door != null);
			Pose(mo, 1352, OFF + 352, 42);
		}
		else if (i == 5)
		{
			UseAt(mo, 1460, 480, 0);                 // taken from 103
			Lean(mo, 1316, OFF + 194, 0);            // against the pocket's west wall THEN, south of the goods edge
			what = "f: THEN, the door leaning on the pocket's west wall";
			Pose(mo, 1440, OFF + 200, 180);
		}
		else if (i == 6)
		{
			Lean(mo, 1316, 194, 0);                  // the same wall NOW
			what = "g: NOW, the door leaning on the corridor's west wall";
			Pose(mo, 1440, 200, 180);
		}
		else if (i == 7)
		{
			clocked.Used(mo);                        // picked up
			what = String.Format("h: THEN, the door carried (%d)", h.carried == clocked);
			Pose(mo, 1408, OFF + 200, 90);
		}
		else
		{
			if (i == 8) Console.Printf("AJARTEST clockViewsDone=1");
			return;
		}
		Console.MidPrint(smallfont, " ");                // what the game says on taking or hanging it would cover the view
		Console.Printf("AJARTEST info clock view %d %s", i, what);
	}
}
