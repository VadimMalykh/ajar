"""The water lab (map WATER): MAP=WATER ./run.sh

An engine lab for MAP20 "High Water": water goes through doors (PLAN.md,
"The water lab"). Water stands level on both sides of a hung door, measured
from the door's sill (src/zscript/water.zs; the pieces: tools/ajarwater.py).

Bays off one dry corridor (y -320..-192), west to east. Each bay is entered
by a bulkhead that will not open from the corridor while the bay holds
water; each basin has a staff gauge (marks every 32 from its floor).
  R, O  the RESERVOIR (BLUE's far side, its water 96 over its floor) and
        the OUTFALL (GREEN's far side, always dry), each behind glass in
        the corridor's north wall.
  1 see it: hall A (floor 0, ceiling 288): frame 101 at the floor (west
    wall), 102 on the gallery 128 up (north wall; a stair up to it), 103 at
    the floor (east wall), a ledge at 208 with no stair (a medikit on it).
    BLUE and GREEN lean here.
  2 the pipe: room B (floor 0), frame 104 (north wall) and 105 for BLUE
    (west wall); room C (floor 192, a stair up to its bulkhead), frame 106.
    Both TEAL leaves lean in B.
  3 the circle: the lower pool L (floor 0) and the upper pool U (floor
    192) north of it. U spills over a crest at 224 down a chute into L; a
    paddle wheel turns in the chute. Frame 107 at L's foot (west wall), 108
    at U's head (west wall), 109 for BLUE (L's south wall). Both ORANGE
    leaves lean in L. U is reached by a passage with a stair, east of L.
    While the wheel turns, the lamp over the corridor at the machine room
    is lit and the machine room's shutter is held open.
  4 company: the cell K (frame 110, west wall), two imps, a pinky and a
    cacodemon; armoured glass from an alcove of the corridor.
Doors lean where they are needed; nothing here is a puzzle (no solver).
"""
import ajarmap
import ajarwater as W
from ajarmap import GREEN, BLUE, TEAL, ORANGE, far_id
from udmf import Map, rect

m = Map()

LOOKS = {   # wall, floor, light, tint
    "corr": ("GRAY1", "FLAT5_4", 170, 0xF0F0F0),
    "R": ("BRICK7", "FLAT14", 200, 0xC8D8FF),
    "O": ("ASHWALL2", "RROCK09", 140, 0xE0D0C0),
    "A": ("STARTAN3", "FLOOR0_1", 200, 0xD0FFD0),
    "B": ("WOOD1", "FLOOR7_1", 200, 0xFFF0C8),
    "C": ("MARBLE1", "FLOOR4_8", 200, 0xFFC0A8),
    "L": ("STONE2", "FLAT1", 200, 0xE0E0FF),
    "U": ("BIGBRIK1", "SLIME13", 210, 0xE8FFC0),
    "K": ("PANEL1", "GRASS1", 220, 0xD8FFE8),
    "chute": ("STONE2", "FLAT1", 190, 0xE0E0FF),
}
# basin tags
TA, TR, TO, TB, TC, TU, TL, TK = 21, 22, 23, 24, 25, 26, 27, 28
CHUTE, LAMP, SHUTTER = 31, 32, 33
GLASS = dict(light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")


def room(name, box, floor=0, ceil=None, tag=0, **k):
    wall, flat, light, tint = LOOKS[name]
    return m.sector(rect(*box), floor=floor, ceil=floor + 192 if ceil is None else ceil, light=light,
                    wall=wall, ftex=flat, ctex="CEIL5_1", color=tint, id=tag, **k)


def frame(a, b, out, n, floor=0, tag=0):
    ajarmap.recess(m, a, b, out, floor, n, far_id(BLUE), tag=tag)


def far(a, b, out, colour, floor=0, tag=0):
    ajarmap.recess(m, a, b, out, floor, far_id(colour), 101, far_colour=colour, tag=tag)


def glass(box, face, floor=0):
    """A pane in the wall: the sector `box`, its line `face` the glass, which
    nothing passes and everything sees through."""
    m.sector(rect(*box), floor=floor + 24, ceil=floor + 168, **GLASS)
    m.line(*face, blocking=True, blockeverything=True)


def corridor(x1, x2, **k):
    room("corr", (x1, -320, x2, -192), ceil=128, **k)


# --- the corridor ------------------------------------------------------------------------------------
corridor(-900, 3040)
m.sector(rect(3040, -320, 3104, -192), ceil=120, light=96, wall="GRAY1", ftex="FLAT5_4", ctex="TLITE6_5",
         id=LAMP)                                               # the wheel's lamp, a panel in the ceiling
corridor(3104, 4000)
m.thing(-840, -256, 1, angle=0)

# --- R and O: the reservoir and the outfall, behind glass ----------------------------------------------
room("R", (-860, -176, -540, 192), tag=TR)
far((-732, 192), (-668, 192), (0, 1), BLUE, tag=TR)
glass((-796, -192, -604, -176), ((-796, -192), (-604, -192)))
W.gauge(m, (-860, 0), (-860, 64))
W.basin(m, TR, 320 * 368, 184, floor=0, kind=W.RESERVOIR, depth=96, at=(-700, 0))

room("O", (-480, -176, -160, 192), tag=TO)
far((-352, 192), (-288, 192), (0, 1), GREEN, tag=TO)
glass((-416, -192, -224, -176), ((-416, -192), (-224, -192)))
W.basin(m, TO, 320 * 368, 184, floor=0, kind=W.OUTFALL, at=(-320, 0))

# --- 1: see it ---------------------------------------------------------------------------------------
HA = dict(ceil=288, tag=TA)
room("A", (64, 0, 448, 384), **HA)
room("A", (0, 0, 64, 128), **HA)
room("A", (448, 0, 512, 128), **HA)
wall, flat, light, tint = LOOKS["A"]
ajarmap.stairs(m, (0, 128), (64, 128), (0, 1), 0, 128, steps=8, depth=32, ceil=288, light=light, wall=wall,
               ftex=flat, ctex="CEIL5_1", color=tint, id=TA)
room("A", (0, 384, 512, 512), floor=128, **HA)                  # the gallery
room("A", (448, 128, 512, 384), floor=208, **HA)                # the ledge, no stair
m.thing(480, 256, 2012)                                         # a medikit on it
frame((0, 32), (0, 96), (-1, 0), 101, tag=TA)
frame((160, 512), (224, 512), (0, 1), 102, 128, tag=TA)
frame((512, 96), (512, 32), (1, 0), 103, tag=TA)
corridor_neck = room("corr", (224, -192, 288, -16), ceil=128)
W.bulkhead(m, (224, -16), (288, -16), (0, 1), 0, TA)
W.gauge(m, (96, 0), (160, 0))
W.basin(m, TA, 512 * 512, 272, floor=0, at=(256, 200))
ajarmap.door(m, BLUE, 200, 120, angle=90)
ajarmap.door(m, GREEN, 330, 120, angle=90)
W.raft(m, 256, 240)                                             # a raft, for the current from 101 to 103

# --- 2: the pipe -------------------------------------------------------------------------------------
room("B", (800, 0, 1312, 512), ceil=256, tag=TB)
frame((1024, 512), (1088, 512), (0, 1), 104, tag=TB)
frame((800, 224), (800, 288), (-1, 0), 105, tag=TB)
room("corr", (1024, -192, 1088, -16), ceil=128)
W.bulkhead(m, (1024, -16), (1088, -16), (0, 1), 0, TB)
W.gauge(m, (880, 0), (944, 0))
W.basin(m, TB, 512 * 512, 240, floor=0, at=(1056, 200))
ajarmap.pair(m, TEAL, (950, 400, 270), (1150, 400, 270))

room("C", (1500, 0, 2012, 512), floor=192, ceil=416, tag=TC)
frame((1724, 512), (1788, 512), (0, 1), 106, 192, tag=TC)
wall, flat, light, tint = LOOKS["corr"]
ajarmap.stairs(m, (1724, -192), (1788, -192), (0, 1), 0, 192, steps=8, depth=22, ceil=320, light=light,
               wall=wall, ftex=flat, ctex="CEIL5_1", color=tint)
W.bulkhead(m, (1724, -16), (1788, -16), (0, 1), 192, TC)
W.gauge(m, (1580, 0), (1644, 0))
W.basin(m, TC, 512 * 512, 400, floor=192, at=(1756, 200))

# --- 3: the circle -----------------------------------------------------------------------------------
room("L", (2300, 0, 2812, 512), ceil=320, tag=TL)
room("U", (2300, 640, 2812, 1152), floor=192, ceil=448, tag=TU)
room("U", (2500, 608, 2612, 640), floor=224, ceil=448, tag=TU)  # the crest, in a notch of U's south wall
wall, flat, light, tint = LOOKS["chute"]
ajarmap.stairs(m, (2500, 608), (2612, 608), (0, -1), 224, -224, steps=6, depth=16, ceil=448, light=light,
               wall=wall, ftex=flat, ctex="CEIL5_1", color=tint, id=CHUTE)
W.weir(m, 2556, 560, TU, TL, 224, CHUTE, LAMP, SHUTTER)
frame((2300, 224), (2300, 288), (-1, 0), 107, tag=TL)           # the foot
frame((2300, 864), (2300, 928), (-1, 0), 108, 192, tag=TU)      # the head
frame((2700, 0), (2764, 0), (0, -1), 109, tag=TL)               # for BLUE
room("corr", (2420, -192, 2484, -16), ceil=128)
W.bulkhead(m, (2420, -16), (2484, -16), (0, 1), 0, TL)
W.gauge(m, (2340, 0), (2404, 0))
W.gauge(m, (2340, 640), (2404, 640))
W.basin(m, TL, 512 * 512, 304, floor=0, at=(2556, 200))
W.basin(m, TU, 512 * 512, 432, floor=192, at=(2556, 900))
ajarmap.pair(m, ORANGE, (2400, 400, 270), (2700, 400, 270))
# the way up to U: a passage east of L, a stair of 192, a bulkhead into U's east wall
room("corr", (2876, -192, 2940, 300), ceil=128)
wall, flat, light, tint = LOOKS["corr"]
ajarmap.stairs(m, (2876, 300), (2940, 300), (0, 1), 0, 192, steps=8, depth=24, ceil=320, light=light,
               wall=wall, ftex=flat, ctex="CEIL5_1", color=tint)
room("corr", (2876, 492, 2940, 960), floor=192, ceil=320)
room("corr", (2860, 880, 2876, 944), floor=192, ceil=320)
W.bulkhead(m, (2860, 944), (2860, 880), (-1, 0), 192, TU, thick=48)
# the machine room, south of the corridor, behind the shutter the wheel holds open
m.sector(rect(3040, -336, 3104, -320), floor=0, ceil=0, light=160, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF",
         id=SHUTTER)
m.sector(rect(2976, -528, 3168, -336), ceil=128, light=220, wall="SUPPORT3", ftex="FLAT23", ctex="CEIL5_1")
m.thing(3072, -432, 2013)                                       # a soulsphere in it

# --- 4: company --------------------------------------------------------------------------------------
room("K", (3300, 0, 3812, 384), tag=TK)
frame((3300, 160), (3300, 224), (-1, 0), 110, tag=TK)
room("corr", (3332, -192, 3588, -96), ceil=128)                 # the alcove
glass((3332, -96, 3588, 0), ((3332, -96), (3588, -96)))
m.line((3332, 0), (3588, 0), blockeverything=True)              # (the glass, armoured, both faces)
room("corr", (3700, -192, 3764, -16), ceil=128)
W.bulkhead(m, (3700, -16), (3764, -16), (0, 1), 0, TK)
W.gauge(m, (3812, 64), (3812, 128))
W.basin(m, TK, 512 * 384, 176, floor=0, at=(3556, 300))
for t, x, y in ((3001, 3500, 200), (3001, 3600, 260), (3002, 3700, 200), (3005, 3550, 320)):
    m.thing(x, y, t, angle=270, skill=1)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
