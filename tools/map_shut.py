"""The third goes lab (map SHUT): the shutter, an earlier self's shots in a
fight of goes, death in a room of goes, two rooms in one level, and the
figures of a model window. MAP=SHUT ./run.sh; the tests are MAP=SHUT MODE=3
and 4 tools/smoke.sh. See src/zscript/shut.zs.

Two rooms in a row, each its own fight number.

Room A (fight 1) is a room of goes (plate.zs): 640 square with a pit 256
square in its north-east corner, 64 deep and not to be climbed out of. Time
door 1 in the room's west wall, time door 2 in the pit's east wall: both
lead into the one box (west, with the plate that forgets), and the box back
by door 1. In the north wall a sprung frame (101) made with `only`: it takes
RED and no other door (its brass is inlaid red), RED leans in the room and
the frame's plate is 340 from its mouth. RED's far side is in the lobby of
room B. In the south wall a glass case: the player on a pressed plate and
two bodies, a model of nothing in particular (shut.zs, AjarFigure).

Room B (fight 2) is a fight of goes (goes.zs): a range 384 wide and 1100
long, entered from the lobby on its west side. At its north end a pen behind
a shutter 256 wide; the pen's floor is 64 lower, and it holds the fight's
monsters, all AjarCues of wave 1: four imps and two hell knights. The
shutter's plate is in a booth east of the pen end, behind glass, entered
from the range. A firing spot at the south end (where the player starts in
the tests), with a pillar for cover. Time doors in the west and east walls,
box 1 and box 2 south of the range behind glass (box 1 has the plate that
forgets, for after the win). The steel door (tag 3290) in the east wall
leads to a small room with the exit. In the middle of the range a press
(tag 3510, 128 square) with its lever on the west wall.
"""
import ajarmap
import ajartime
from ajarmap import RED, far_id
from udmf import Map, rect

m = Map()
ROOM = 0xE8E0D0
PIT = 0xC8C0B4
BOX = 0xFFE8C0
RANGE = 0xE4E0D8
PEN = 0xD8C8B8
OUT = 0xE0F0D8
F1 = 101
SHUT = 3520         # the shutter's sector tag (shut.zs: AjarTimeHandler.SHUT_TAG)
PRESS = 3510        # the press's (shut.zs: SHUT_PRESS)
FIRE = (1092, 80)   # the firing spot (shut.zs: the tests)

# --- room A, a room of goes ----------------------------------------------------
m.sector([(0, 0), (0, 640), (384, 640), (384, 384), (640, 384), (640, 0)], ceil=192, light=200, color=ROOM)
m.sector(rect(384, 384, 640, 640), floor=-64, ceil=192, light=180, color=PIT, wall="AJBOLT")
m.thing(320, 200, 1, angle=90)
ajartime.zone(m, 1, 0, 0, 0, 640, 640, grow=72, goes=True)
ajartime.hall_door(m, 1, 1, (0, 96), (0, 160), (-1, 0), 0, color=ROOM)
ajartime.hall_door(m, 1, 2, (640, 480), (640, 544), (1, 0), -64, color=PIT)

# the box, west, its door in its east wall
m.sector(rect(-400, 32, -208, 224), ceil=160, light=210, color=BOX)
ajartime.box_door(m, 1, 1, (-208, 96), (-208, 160), (1, 0), 0, color=BOX)
ajartime.zone(m, 1, 1, -400, 32, -208, 224, grow=64)
ajartime.anew(m, -398, 128, 0)

# the sprung frame that takes RED only; RED by it; its plate out in the room
ajarmap.recess(m, (128, 640), (192, 640), (0, 1), 0, F1, far_id(RED), home=far_id(RED), only=True,
               trim=(f"AJXA{RED}", f"AJXF{RED}"), color=ROOM)
ajarmap.door(m, RED, 300, 560, angle=270)
ajartime.plate(m, 160, 300, F1)
assert ((160 - 160) ** 2 + (640 - 300) ** 2) ** 0.5 >= 300

# the glass case in the south wall, and what is in it: the player on a
# pressed plate, an imp and a hell knight lying dead
CASE = ajartime.case(m, (240, 0), (400, 0), (0, -1), 0, deep=96, color=ROOM)
FIGS = [(300, -64, "plate", 0, 0), (300, -64, "me", 0, 90), (352, -48, "body", 3001, 200), (362, -88, "body", 69, 160)]
for x, y, what, kind, ang in FIGS:
    ajartime.figure(m, x, y, what, kind=kind, angle=ang)
assert ajartime.sealed(m, CASE), "the glass case is not sealed"
assert all(240 < x < 400 and -112 < y < -16 for x, y, *_ in FIGS)

# --- room B, a fight of goes ---------------------------------------------------
# the lobby, west of the range, with RED's far side in its south wall
m.sector(rect(740, 640, 900, 830), ceil=160, light=190, color=RANGE)
ajarmap.recess(m, (788, 640), (852, 640), (0, -1), 0, far_id(RED), F1, far_colour=RED, color=RANGE)

# the range, cut round the pillar and the press
m.sector(rect(900, 0, 1284, 160), ceil=192, light=200, color=RANGE)
m.sector(rect(900, 160, 1000, 224), ceil=192, light=200, color=RANGE)
m.sector(rect(1064, 160, 1284, 224), ceil=192, light=200, color=RANGE)       # the pillar is 1000..1064
m.sector(rect(900, 224, 1284, 520), ceil=192, light=200, color=RANGE)
m.sector(rect(900, 520, 1028, 648), ceil=192, light=200, color=RANGE)
m.sector(rect(1028, 520, 1156, 648), ceil=192, light=190, color=RANGE, wall="AJBOLT", ctex="AJTRIMF", id=PRESS)
m.sector(rect(1156, 520, 1284, 648), ceil=192, light=200, color=RANGE)
m.sector(rect(900, 648, 1284, 1100), ceil=192, light=200, color=RANGE)
ajartime.press(m, 1092, 584, PRESS)
ajartime.press_switch(m, 902, 584, 0, PRESS)
assert not (1000 <= FIRE[0] <= 1064), "the pillar is in the line of fire"

# the shutter, 256 wide, and the pen behind it, 64 lower
ajartime.shutter(m, (964, 1100), (1220, 1100), (0, 1), 0, SHUT, keep=True)
m.sector(rect(948, 1116, 1236, 1216), floor=-64, ceil=96, light=170, color=PEN, wall="AJBOLT")
IMPS = [(990, 1140), (1060, 1140), (1130, 1140), (1200, 1140)]
KNIGHTS = [(1030, 1190), (1160, 1190)]
ajartime.cue(m, 2, 1, 0, 3001, *IMPS, angle=270, always=True)
ajartime.cue(m, 2, 1, 0, 69, *KNIGHTS, angle=270, always=True)
assert all(948 + r < x < 1236 - r and 1116 + r < y < 1216 - r for (x, y), r in [(p, 20) for p in IMPS] + [(p, 24) for p in KNIGHTS])

# the booth, east of the pen end: entered from the range, glass onto it
m.sector(rect(1284, 900, 1300, 964), ceil=128, light=190, color=RANGE)
ajartime.glass(m, (1284, 980), (1284, 1100), (1, 0), 0)
m.sector(rect(1300, 900, 1428, 1100), ceil=128, light=210, color=RANGE)
ajartime.shutter_plate(m, 1364, 1040, SHUT)

# the time doors, west and east, and the two boxes south, behind glass
ajartime.hall_door(m, 2, 1, (900, 300), (900, 364), (-1, 0), 0, color=RANGE)
ajartime.hall_door(m, 2, 2, (1284, 300), (1284, 364), (1, 0), 0, color=RANGE)
m.sector(rect(900, -208, 1076, -16), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (932, 0), (1044, 0), (0, -1), 64)
ajartime.box_door(m, 2, 1, (900, -144), (900, -80), (-1, 0), 64, color=BOX)
ajartime.zone(m, 2, 1, 836, -272, 1076, -16)
ajartime.anew(m, 1074, -112, 180)
m.sector(rect(1108, -208, 1284, -16), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (1140, 0), (1252, 0), (0, -1), 64)
ajartime.box_door(m, 2, 2, (1284, -144), (1284, -80), (1, 0), 64, color=BOX)
ajartime.zone(m, 2, 2, 1108, -272, 1348, -16)

# the fight's zones: the range with the pen and the stubs, the booth, the lobby
ajartime.zone(m, 2, 0, 828, -16, 1356, 1260, mix=True)
ajartime.zone(m, 2, 0, 1284, 890, 1440, 1110, mix=True)
ajartime.zone(m, 2, 0, 732, 570, 900, 830, mix=True)

# the steel door the win opens, east, into the room with the exit (outside the fight)
a, b, c, d = (1284, 420), (1284, 484), (1300, 420), (1300, 484)
m.sector([a, b, d, c], floor=0, ceil=0, light=160, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF", id=3090 + 100 * 2)
m.line(a, b, exact=True)
m.line(c, d, exact=True)
for p, q in ((a, c), (b, d)):
    m.line(p, q, mid="AJTRIM", dontpegbottom=True)
m.sector(rect(1300, 388, 1480, 516), ceil=128, light=200, color=OUT)
m.sector(rect(1480, 388, 1544, 516), ceil=128, light=230, color=OUT, ftex="AJTRIMF")
m.line((1480, 388), (1480, 516), special=243, playercross=True)
m.line((1544, 388), (1544, 516), mid="AJEXIT", exact=True)
assert 1480 > 1356, "the exit is in the fight's zone"

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
