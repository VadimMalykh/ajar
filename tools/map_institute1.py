"""Act 2, level 1: "By Appointment" (MAP11). First build: plain walls, no look yet.

The way into the institute that studies the doors. One new thing, the Pair:
two leaves of one colour (TEAL) that open onto each other. Plain doors are
here beside it, and the level asks for the Pair's basic move once, the rope:
a Pair cannot take you anywhere new, but it keeps a way open to a place you
have been, for whatever you carry.

Places. The lobby (start) and the corridor north of it are one place to walk
about in. Both TEAL leaves and RED lean in the lobby, whose two frames face
each other: hang both leaves there and the lobby has no end. The gallery
(RED's far side; key 1) runs above the corridor's east side, too high to
climb; from it you can drop into the corridor or into the archive. The
archive (VIOLET; two frames) has no door: a hole in its wall lets empty
hands through, and nothing else. West of the corridor, behind a door with
one lock, the vestibule and the night room: VIOLET's far side and the brass
frame that takes VIOLET only.

So VIOLET has to come out of the archive in your hands, and the hole will
not have it. Hang a leaf in the lobby; go up by RED with the other, take the
key, drop into the archive and hang it there: the archive opens onto the
lobby. Carry VIOLET through, to the night room, and hang it.

Secret: a nook off the gallery (to be made a better one with the look).
"""
import ajarmap
from ajarmap import RED, VIOLET, TEAL, far_id
from udmf import Map, rect

m = Map()
UP = 128                                    # the gallery's floor
PALE, GREEN, PAPER, DIM = 0xDCE8DC, 0xC8E0C8, 0xF0E4C8, 0xB0B8C8
HIGH = dict(ceil=256)

# --- the lobby and the corridor ---------------------------------------------
m.sector(rect(0, 0, 768, 512), ceil=224, light=200, color=PALE)
m.sector(rect(256, 512, 512, 1280), light=180, color=GREEN, **HIGH)
ajarmap.recess(m, (0, 224), (0, 288), (-1, 0), 0, 101, far_id(RED), color=PALE)
ajarmap.recess(m, (768, 224), (768, 288), (1, 0), 0, 102, far_id(RED), color=PALE)
ajarmap.recess(m, (256, 640), (256, 704), (-1, 0), 0, 103, far_id(RED), color=GREEN)      # a third, in the corridor: hands can always be emptied

# --- the gallery, over the corridor's east side; its nook (secret) ----------
m.sector(rect(512, 640, 704, 1152), floor=UP, light=190, color=PAPER, **HIGH)
ajarmap.recess(m, (704, 864), (704, 928), (1, 0), UP, far_id(RED), 101, far_colour=RED, color=PAPER)
m.sector(rect(704, 656, 800, 720), floor=UP, ceil=UP + 96, light=120, color=DIM, special=1024)

# --- the archive: a drop from the gallery, a hole from the corridor ---------
m.sector(rect(528, 1152, 896, 1472), light=170, color=DIM, **HIGH)
ajarmap.squeeze(m, (512, 1200), (512, 1248), (1, 0), 0)
ajarmap.recess(m, (896, 1280), (896, 1344), (1, 0), 0, 106, far_id(RED), color=DIM)
ajarmap.recess(m, (672, 1472), (736, 1472), (0, 1), 0, 107, far_id(RED), color=DIM)

# --- the night room and its vestibule, behind the door with one lock --------
ajarmap.way_home(m, -192, 640, VIOLET, only=True)
m.sector(rect(-64, 896, 240, 1024), ceil=160, light=160, color=DIM)
ajarmap.roomdoor(m, (256, 928), (256, 992), (-1, 0), 0, keys="1", line_id=301, free_inside=True)

# --- doors --------------------------------------------------------------------
ajarmap.pair(m, TEAL, (40, 150, 0), (728, 150, 180))
ajarmap.door(m, RED, 384, 480, angle=270)
ajarmap.door(m, VIOLET, 860, 1180, angle=180)
ajarmap.key(m, 1, 608, 1100)

# --- things -------------------------------------------------------------------
m.thing(384, 64, 1, angle=90)
m.thing(300, 100, 2001)                     # a shotgun, shells
m.thing(300, 60, 2008)
m.thing(468, 100, 2008)
m.thing(384, 700, 3004, angle=270)          # the corridor: two zombies
m.thing(384, 1150, 3004, angle=270)
m.thing(608, 760, 3001, angle=180)          # the gallery: an imp
m.thing(752, 688, 2018)                     # the nook: armour
m.thing(600, 1400, 3001, angle=270)         # the archive: two imps, shells, a medikit
m.thing(820, 1400, 3001, angle=225)
m.thing(580, 1200, 2049)
m.thing(580, 1440, 2012)
m.thing(60, 960, 9, angle=0)                # the vestibule: a sergeant
m.thing(320, 1240, 2011)                    # the corridor's end: a stimpack

PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("gallery", "hall"), ("gallery", "archive"),
          ("hall", "archive", "", "squeeze"), ("archive", "hall", "", "squeeze"),     # the hole
          ("hall", "night", "1"), ("night", "hall")],          # no key is needed to come out
    keys={"1": "gallery"},
    frames={101: "hall", 102: "hall", 103: "hall", 106: "archive", 107: "archive", ajarmap.HOME: "night"},
    only={ajarmap.HOME: VIOLET},
    doors={
        RED: dict(home="gallery", lean="hall"),
        VIOLET: dict(home="night", lean="archive"),
        **ajarmap.leaves(TEAL, "hall", "hall"),
    },
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
