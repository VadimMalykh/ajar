"""Mirrors (map MIR): what MAP15 needs of a mirror. MAP=MIR ./run.sh; the
checks are in src/zscript/mirror.zs (MODE=1..3 tools/smoke.sh).

Three rooms with no way between them (the checks put the player in each).
  1. The hall: a mirror on the west wall. An emitter fires at it aslant, and
     a sensor on the east wall is where light would go on to. A GREEN door
     that only the mirror shows leans by the east wall; frame 101 north.
  2. The cell: a mirror on the west wall and an imp that only it shows.
  3. The lodging: frames 111 and 112, which face each other, both TEAL
     leaves and BLUE. The check brings a lodger.
"""
import ajarmap
from ajarmap import BLUE, GREEN, TEAL, far_id
from udmf import Map, rect

m = Map()
HALL, CELL, LODGE, FAR = 0xD8E8FF, 0xFFD8D8, 0xE0FFD8, 0xFFE8C0
MIRROR = 182        # Line_Mirror
UNSEEN_IMP_T = 20092


def mirror(a, b):
    m.cut(a, b)
    m.line(a, b, special=MIRROR)


# --- 1: the hall ------------------------------------------------------------
m.sector(rect(0, 0, 640, 640), ceil=192, light=200, color=HALL)
mirror((0, 96), (0, 416))
ajarmap.recess(m, (288, 640), (352, 640), (0, 1), 0, 101, 201, color=HALL)
# the beam leaves (382, 65) along 153 degrees, strikes the mirror at y = 260
# and would go on to (626, 579)
ajarmap.emitter(m, 400, 56, 153, 721, (480, 0), (512, 0))
ajarmap.target(m, 626, 579, 5, beam=True)
ajarmap.door(m, GREEN, 520, 420, angle=180, unseen=True)
m.sector(rect(0, 1000, 256, 1256), ceil=160, light=200, color=FAR)       # GREEN's far side
ajarmap.recess(m, (0, 1096), (0, 1160), (-1, 0), 0, far_id(GREEN), 101, far_colour=GREEN, color=FAR)
m.thing(320, 100, 1, angle=90)
m.thing(600, 40, 2028)

# --- 2: the cell ------------------------------------------------------------
m.sector(rect(2000, 0, 2384, 384), ceil=192, light=200, color=CELL)
mirror((2000, 64), (2000, 320))
m.thing(2080, 300, UNSEEN_IMP_T, angle=0)
m.thing(2340, 40, 2028)

# --- 3: the lodging ---------------------------------------------------------
m.sector(rect(4000, 0, 4512, 384), ceil=192, light=200, color=LODGE)
ajarmap.recess(m, (4000, 160), (4000, 224), (-1, 0), 0, 111, 201, color=LODGE)
ajarmap.recess(m, (4512, 160), (4512, 224), (1, 0), 0, 112, 201, color=LODGE)
ajarmap.pair(m, TEAL, (4200, 60, 90), (4260, 60, 90))
ajarmap.door(m, BLUE, 4320, 60, angle=90)
m.sector(rect(4000, 1000, 4256, 1256), ceil=160, light=200, color=FAR)   # BLUE's far side
ajarmap.recess(m, (4000, 1096), (4000, 1160), (-1, 0), 0, far_id(BLUE), 101, far_colour=BLUE, color=FAR)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
