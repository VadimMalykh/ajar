"""The time box with doors (map TDOOR): a Pair hung by two selves.
MAP=TDOOR ./run.sh; the tests are MAP=TDOOR MODE=3, 4 and 5 tools/smoke.sh.

The time box (map_time.py) with a frame in the hall (121) and one in the
west box (122), and a TEAL leaf in each. Hang the hall's leaf, step out by a
time door, hang the twin in the box: when the earlier self hangs its leaf
the two are joined, and the way is open when the fight is where it was left.

A chain too (MODE=4): a brass frame in the hall and one in the west box, RED
in the hall and BLUE in the box, and the night room their far sides are in.
Each self hangs one door; the loop is closed when the earlier self hangs
its own. MODE=5: a demon comes out of the fight into the box and is led
through BLUE into the night room. See src/zscript/timedoor.zs.
"""
import ajarmap
import ajartime
from ajarmap import TEAL, RED, BLUE, HOME, HOME2, far_id
from udmf import Map, rect

m = Map()
HALL = 0xE8E0D0
BOX = 0xFFE8C0

m.sector(rect(0, 0, 768, 640), ceil=192, light=200, color=HALL)
m.sector(rect(320, -160, 448, 0), ceil=128, light=180, color=HALL)          # the way in
m.line((320, -160), (448, -160), special=243, playeruse=True, mid="AJEXIT", exact=True)
ajartime.zone(m, 1, 0, 0, 0, 768, 640, grow=72)
ajartime.zone(m, 1, 0, 320, -100, 448, 0)

ajartime.hall_door(m, 1, 1, (768, 288), (768, 352), (1, 0), 0, color=HALL)
ajartime.hall_door(m, 1, 2, (96, 0), (160, 0), (0, -1), 0, color=HALL)
ajarmap.recess(m, (608, 640), (672, 640), (0, 1), 0, 121, 122, color=HALL)

# box 1, west: its window is in the hall's west wall, its door in its north
# wall, its frame in its south wall
m.sector(rect(-240, 224, -16, 416), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (0, 256), (0, 384), (-1, 0), 64)
ajartime.box_door(m, 1, 1, (-160, 416), (-96, 416), (0, 1), 64, color=BOX)
ajarmap.recess(m, (-160, 224), (-96, 224), (0, -1), 64, 122, 121, color=BOX)
ajartime.zone(m, 1, 1, -240, 224, -16, 416, grow=72)

# the chain: its brass frames (the hall's south wall, the box's west wall) and its far end
BRASS = ("AJXA", "AJXAF")
ajarmap.recess(m, (560, 0), (624, 0), (0, -1), 0, HOME, far_id(RED), trim=BRASS, home=far_id(RED),
               chain=(far_id(BLUE), HOME2), color=HALL)
ajarmap.recess(m, (-240, 288), (-240, 352), (-1, 0), 64, HOME2, far_id(RED), trim=BRASS, home=far_id(RED),
               chain=(far_id(BLUE), HOME), color=BOX)
ajarmap.way_through(m, 2000, 0, RED, BLUE)
ajarmap.door(m, RED, 500, 500, angle=270)
ajarmap.door(m, BLUE, -40, 400, angle=270)

# box 2, north: its door in its east wall
m.sector(rect(288, 656, 512, 848), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (320, 640), (448, 640), (0, 1), 64)
ajartime.box_door(m, 1, 2, (512, 720), (512, 784), (1, 0), 64, color=BOX)
ajartime.zone(m, 1, 2, 288, 656, 512, 848, grow=72)

m.thing(384, -120, 1, angle=90)
ajarmap.pair(m, TEAL, (600, 500, 270), (-200, 380, 270))

# the fight: one monster shut in a closet of its own, so that it is never won
m.sector(rect(900, 500, 964, 564), ceil=128, light=160, color=HALL)
ajartime.zone(m, 1, 0, 900, 500, 964, 564)
m.thing(932, 532, 3004, angle=270, skill=1)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
