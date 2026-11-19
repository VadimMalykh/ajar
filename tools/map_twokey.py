"""Two keys at once (map TWOKEY): a Pair that joins only if both leaves are
hung together. MAP=TWOKEY ./run.sh; the test is MAP=TWOKEY MODE=3
tools/smoke.sh. See src/zscript/goes.zs.

A room of goes (plate.zs) shaped as an L: a south arm and, at its east end,
a north arm. Frame A (131) in the west wall of the south arm, frame B (132)
in the north wall of the north arm, each with a lamp beside it (AjarTogether)
and a TEAL leaf leaning by it. On foot they are some 1500 apart: more than
two seconds at a run, so one body cannot hang both in time. The time door is
in the south wall, the box (with the plate that forgets every go) behind it.
The joined Pair is the way across (from B to A and back); the exit is a
nook off the north arm's east wall, a line to walk over.
"""
import ajarmap
import ajartime
from ajarmap import TEAL
from udmf import Map, rect

m = Map()
ROOM = 0xE8E4D8
BOX = 0xFFE8C0
FA, FB = 131, 132

m.sector(rect(0, 0, 1152, 320), ceil=192, light=200, color=ROOM)
m.sector(rect(832, 320, 1152, 1088), ceil=192, light=190, color=ROOM)
m.thing(480, 100, 1, angle=90)
ajartime.zone(m, 1, 0, 0, 0, 1152, 320, grow=72, goes=True)
ajartime.zone(m, 1, 0, 832, 320, 1152, 1088, grow=72, goes=True)

# the two frames, their lamps and their leaves
ajarmap.recess(m, (0, 128), (0, 192), (-1, 0), 0, FA, FB, color=ROOM)
ajarmap.recess(m, (960, 1088), (1024, 1088), (0, 1), 0, FB, FA, color=ROOM)
ajartime.together(m, 2, 224, 0, FA)
ajartime.together(m, 1056, 1086, 270, FB)
ajarmap.pair(m, TEAL, (100, 260, 0), (1100, 1000, 180))


def walk(*ps):
    return sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(ps, ps[1:]))


# from before A round the inside corner to before B: over two seconds at a run (16.7 a tic)
assert walk((40, 160), (842, 330), (992, 1048)) > 1400

# the time door, south, and the box behind it
ajartime.hall_door(m, 1, 1, (448, 0), (512, 0), (0, -1), 0, color=ROOM)
m.sector(rect(352, -320, 608, -128), ceil=160, light=210, color=BOX)
ajartime.box_door(m, 1, 1, (352, -256), (352, -192), (-1, 0), 0, color=BOX)
ajartime.zone(m, 1, 1, 288, -320, 608, -128)
ajartime.anew(m, 606, -224, 180)

# the exit: a nook off the north arm
m.sector(rect(1152, 640, 1216, 768), ceil=128, light=200, color=ROOM)
m.sector(rect(1216, 640, 1280, 768), ceil=128, light=230, color=ROOM, ftex="AJTRIMF")
m.line((1216, 640), (1216, 768), special=243, playercross=True)
m.line((1280, 640), (1280, 768), mid="AJEXIT", exact=True)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
