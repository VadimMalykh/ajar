"""Look 3's title map, "The Way Out" (AJAR_TITLE=3; tools/gfx_title3.py): the night room, the way out of
every level, as the game builds it (ajarmap.way_out, no colour door's far side in it), and nothing else in
view.

The room is 320 by 256 and 160 high (x 0..320, y 0..256 here). Its brass doorway joins the west and east
ends (ajarmap.doorway number 9): each end is a recess 64 wide, 96 high and 16 deep whose back is a portal
line (159 at x = 336, 259 at x = -16) with a 48-deep stub behind it, so that looking east down the middle
line y = 128 you see the room again through the doorway, and again in that, as deep as the engine draws a
portal in a portal. One room's repeat is 352 units (320 + two recesses). The fixed door that holds the
doorway open stands at (296, 128) (no leaf: nothing is drawn); the frame thing at (328, 128) is not drawn
either. way_out also puts a level exit (Exit_Normal, player cross) on both mouths, x = 0 and x = 320,
96 <= y <= 160: only a player sets it off, and the title's player stands in the closet, far away.

The camera (thing 20200, src/zscript/title.zs, args[4]) stands on the middle line facing east and glides
straight ahead for good, SPEED units a second, through the doorway into the same room, on and on. It is
moved as a thing walks (TryMove), so it crosses the portal as a player would and the engine draws no seam;
it is not a player, so it never sets off the exits. A room's repeat takes 352 / SPEED seconds.
"""
import ajarmap
from udmf import Map
from map_title import CAMERA_T, closet

X0 = 24.2           # where the camera starts: just inside the west end, the doorway at the far end. Not a
                    # whole number of steps (0.4 a tic) from the portal line at x = 336: a camera that stops
                    # exactly on a portal line is shown the stub behind it, a brass box, for that tic (seen
                    # with X0 = 24: the camera stood on the line at tic 780). From 24.2 it stands at 335.8,
                    # then 336.2, which is -15.8 through the portal, and so on every room.
EYE = 48            # its eye over the floor: the doorway's middle (it is 96 high, the room 160), so that the
                    # rooms seen in it are framed one in the other, all round one point
PITCH = 0           # degrees down: level; the runner and the starry ceiling both show
SPEED = 14          # units a second: 352 / 14 = 25 seconds a room
# The engine draws a portal seen through a portal 4 deep (r_portal_recursions, a player's setting, 4 by
# default): the doorway shows the room again 4 times, and in the 4th room's doorway it draws nothing, a dark
# rectangle (the black of the screen, a little lifted). A fog the colour of the night (near black, a touch of
# the ink's blue) thickens with distance so that by the 4th room everything is that dark too, and the end
# cannot be told from the room around it (measured on a 1024x640 shot: the rectangle and the 4th room's
# walls both 8 of 255 at density 320; 5 against 8 at 200). 220: two rooms clear in the doorway, the third
# faint, then dark. Nearer, the room keeps its light: the far end of the room the camera is in is a
# little dimmed. Without the fog (`fade` unset) the rooms are as bright as the near one to the end
# and the dark rectangle shows hard.
FOG = ['fade = "06070C"', "fogdensity = 220"]


def night():
    m = Map()
    ajarmap.way_out(m, 0, 0, None)
    closet(m, 1024, 1024)
    m.thing(X0, 128, CAMERA_T, angle=0, height=EYE, args=(0, 0, 0, PITCH, SPEED))
    return m.wad("TITLEMAP"), FOG
