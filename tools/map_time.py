"""The time box (map TIME): stepping out of a fight, in one bare hall.
MAP=TIME ./run.sh; the test is MAP=TIME MODE=3 tools/smoke.sh.

A hall with a few monsters and two time doors (east and south), and two
boxes behind glass (west and north), raised, each with a medikit and a door
of its own. See src/zscript/time.zs.
"""
import ajarmap
import ajartime
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

# box 1, west: its window is in the hall's west wall, its door in its north wall
m.sector(rect(-240, 224, -16, 416), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (0, 256), (0, 384), (-1, 0), 64)
ajartime.box_door(m, 1, 1, (-160, 416), (-96, 416), (0, 1), 64, color=BOX)
ajartime.zone(m, 1, 1, -240, 224, -16, 416, grow=72)
m.thing(-200, 300, 2012)

# box 2, north: its door in its east wall
m.sector(rect(288, 656, 512, 848), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (320, 640), (448, 640), (0, 1), 64)
ajartime.box_door(m, 1, 2, (512, 720), (512, 784), (1, 0), 64, color=BOX)
ajartime.zone(m, 1, 2, 288, 656, 512, 848, grow=72)
m.thing(330, 800, 2012)

m.thing(384, -120, 1, angle=90)
m.thing(384, -60, 2001)
m.thing(350, -60, 2049)
for x, y in ((150, 520), (600, 520), (384, 580)):
    m.thing(x, y, 3001, angle=270, skill=1)
m.thing(250, 420, 3004, angle=270, skill=1)
m.thing(500, 420, 3002, angle=270, skill=1)
ajartime.cue(m, 1, 1, 2, 3001, (384, 320), (200, 320))

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
