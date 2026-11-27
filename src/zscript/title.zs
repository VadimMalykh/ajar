// The title and the menus (AJAR_TITLE; tools/gfx_title.py, tools/map_title.py).
//
// Compiled always, but nothing here does anything unless the switch is on: AjarTitleHandler is named only in
// the title map's own mapinfo block, the camera and the spot only stand on that map (DoomEdNums 20200 and
// 20201 are given in the same generated mapinfo), and AjarMenuDelegate is gameinfo's MenuDelegateClass only
// in a build with the switch on. With the switch off the game keeps GZDoom's own (DoomMenuDelegate).

// The title map's camera. args: [0] sway, units across its view; [1] the period, seconds; [2] the tid of
// an AjarTitleSpot to glide to and back instead; [3] its pitch, degrees down.
class AjarTitleCamera : Actor
{
	Default
	{
		+NOINTERACTION +NOBLOCKMAP +NOGRAVITY +INVISIBLE +DONTSPLASH
		CameraHeight 0;
		Radius 1;
		Height 1;
	}
	States
	{
	Spawn:
		TNT1 A -1;
		Stop;
	}
}

// Where a gliding camera goes (args[3]: the pitch it has there).
class AjarTitleSpot : AjarTitleCamera
{
}

class AjarTitleHandler : EventHandler
{
	AjarTitleCamera cam;
	Vector3 home;
	double homeAngle;
	ui bool opened;

	override void WorldLoaded(WorldEvent e)
	{
		let it = ThinkerIterator.Create("AjarTitleCamera");
		AjarTitleCamera c;
		while (c = AjarTitleCamera(it.Next()))
		{
			if (c is "AjarTitleSpot") c.pitch = c.args[3];
			else cam = c;
		}
		if (!cam) return;
		home = cam.pos;
		homeAngle = cam.angle;
		cam.pitch = cam.args[3];
		Look();
	}

	void Look()
	{
		for (int i = 0; i < MAXPLAYERS; i++)
			if (playeringame[i] && players[i].camera != cam) players[i].camera = cam;
	}

	override void WorldTick()
	{
		if (!cam) return;
		Look();
		double period = max(1, cam.args[1]) * TICRATE;
		double t = level.maptime / period;
		if (cam.args[2])
		{
			let to = AjarTitleSpot(level.CreateActorIterator(cam.args[2], "AjarTitleSpot").Next());
			if (!to) return;
			double f = 0.5 - 0.5 * cos(360 * t);                 // there and back, easing at both ends
			cam.SetOrigin(home + (to.pos - home) * f, true);
			cam.angle = homeAngle + Actor.deltaangle(homeAngle, to.angle) * f;
			cam.pitch = cam.args[3] + (to.args[3] - cam.args[3]) * f;
		}
		else if (cam.args[0] && cam.args[1])
		{
			// a slow drift across the view (and a breath of a turn with it)
			double s = sin(360 * t);
			cam.SetOrigin(home + (Actor.AngleToVector(homeAngle - 90, cam.args[0] * s), 0), true);
			cam.angle = homeAngle + 0.4 * sin(360 * t + 90);
		}
	}

	// The menu opens over the title by itself, once; Esc still shuts it and shows the bare title.
	// Over the title the list menus do not dim it: the cell is lit as MAP01 lights it. (The options menus
	// still dim it, for their small text; in play every menu dims the game as gameinfo says.)
	override void UiTick()
	{
		if (gamestate != GS_TITLELEVEL) return;
		if (!opened)
		{
			opened = true;
			if (menuactive == Menu.Off) Menu.SetMenu('MainMenu');
		}
		let m = Menu.GetCurrentMenu();
		if (m is "ListMenu") m.DontDim = true;
	}
}

// A still title picture (gameinfo titlepage; this handler is named in gameinfo only then): the menu opens
// over it by itself, once.
class AjarTitlePageHandler : StaticEventHandler
{
	ui bool opened;

	override void UiTick()
	{
		if (gamestate != GS_DEMOSCREEN) return;
		if (!opened)
		{
			opened = true;
			if (menuactive == Menu.Off) Menu.SetMenu('MainMenu');
		}
		let m = Menu.GetCurrentMenu();
		if (m is "ListMenu") m.DontDim = true;             // as over a title map
	}
}

// The cursor of the list menus: two frames, the shut leaf (the menu's Selector, AJCUR0) and the ajar one
// (AJCUR1), shown in turn. A look with one frame has no AJCUR1, and the engine's blinking selector is left.
class AjarMenuDelegate : DoomMenuDelegate
{
	const TICS_SHUT = 26;       // menu tics shut
	const TICS_AJAR = 14;       // and then ajar

	override bool DrawSelector(ListMenuDescriptor desc)
	{
		TextureID open = TexMan.CheckForTexture("AJCUR1", TexMan.Type_MiscPatch);
		if (!open.IsValid() || desc.mSelector.IsNull()) return false;
		if (desc.mSelectedItem < 0 || desc.mSelectedItem >= desc.mItems.Size()) return false;
		let item = desc.mItems[desc.mSelectedItem];
		TextureID tex = Menu.MenuTime() % (TICS_SHUT + TICS_AJAR) < TICS_SHUT ? desc.mSelector : open;
		double x = item.GetX() + desc.mSelectOfsX, y = item.GetY() + desc.mSelectOfsY;
		int w = desc.DisplayWidth();
		if (w == ListMenuDescriptor.CleanScale)
			screen.DrawTexture(tex, true, x, y, DTA_Clean, true);
		else
			screen.DrawTexture(tex, true, x, y, DTA_VirtualWidth, w, DTA_VirtualHeight, desc.DisplayHeight(), DTA_FullscreenScale, FSMode_ScaleToFit43);
		return true;
	}
}
