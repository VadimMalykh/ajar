"""Sight lines (map OPT): a room to try what a hung door lets through.
MAP=OPT ./run.sh; the checks are in src/zscript/optics.zs (MODE=1..3
tools/smoke.sh).

The hall has frames 101 (west) and 102 (east), which face each other, and
103 (north), which faces a wall. North of it the range: an emitter at its
west end fires a beam east into RED's far side. South the dark room: frame
104, and across from it a sensor. Two sealed cells, each some door's far
side behind a rail: GREEN's, with a baron and a target on its far wall, and
BLUE's, with a mancubus.
  1. The beam comes out of whichever frame RED hangs in, square to it. From
     101 it crosses the hall into 102; a leaf there and its twin in 104 put
     it on the sensor.
  2. GREEN hung in the hall: the target is shot through it, and the baron
     fires back through it.
  3. GREEN in 101 and BLUE in 102: the baron and the mancubus fight.
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN, TEAL, far_id
from udmf import Map, rect

m = Map()
HALL, RANGE, DARK, CELL = 0xD8E8FF, 0xFFE8C0, 0x9098B0, 0xFFD8D8

m.sector(rect(0, 0, 640, 512), ceil=192, light=200, color=HALL)
ajarmap.recess(m, (0, 224), (0, 288), (-1, 0), 0, 101, 201, color=HALL)
ajarmap.recess(m, (640, 224), (640, 288), (1, 0), 0, 102, 201, color=HALL)
ajarmap.recess(m, (288, 512), (352, 512), (0, 1), 0, 103, 201, color=HALL)

# the range, behind the steel door the target opens
m.sector(rect(0, 704, 1024, 896), ceil=192, light=200, color=RANGE)
m.sector(rect(64, 528, 128, 704), ceil=96, light=170)
ajarmap.steel(m, (64, 512), (128, 512), (0, 1), 0, 1)
m.line((64, 512), (128, 512), id=301)
ajarmap.recess(m, (1024, 768), (1024, 832), (1, 0), 0, far_id(RED), 101, far_colour=RED, color=RANGE)
ajarmap.emitter(m, 40, 800, 0, 721, (0, 832), (0, 864))

# the dark room: a frame, a sensor across from it, and the steel door it opens (onto nothing much)
m.sector(rect(0, -400, 640, -80), ceil=192, light=120, color=DARK)
m.sector(rect(500, -80, 564, 0), ceil=96, light=170)
ajarmap.recess(m, (0, -272), (0, -208), (-1, 0), 0, 104, 201, color=DARK)
ajarmap.target(m, 626, -240, 2, beam=True)
m.sector(rect(200, -496, 264, -416), ceil=96, light=170)
ajarmap.steel(m, (200, -400), (264, -400), (0, -1), 0, 2)
m.line((200, -400), (264, -400), id=302)


def cell(box, colour, a, b, out, rail):
    x1, y1, x2, y2 = box
    xs = sorted({x1, x2, rail})
    for p, q in zip(xs, xs[1:]):
        m.sector(rect(p, y1, q, y2), ceil=160, light=180, color=CELL)
    m.line((rail, y1), (rail, y2), blocking=True)
    ajarmap.recess(m, a, b, out, 0, far_id(colour), 101, far_colour=colour, color=CELL)
    ajarmap.watch(m, box, colour)


cell((-700, 600, -300, 900), GREEN, (-300, 720), (-300, 784), (1, 0), -340)
ajarmap.target(m, -686, 752, 1)
m.thing(-560, 660, 3003, angle=0)                         # a baron
cell((1200, 0, 1600, 300), BLUE, (1200, 120), (1200, 184), (-1, 0), 1240)
m.thing(1480, 150, 67, angle=180)                         # a mancubus

m.thing(320, 100, 1, angle=90)
ajarmap.door(m, RED, 200, 60, angle=90)
ajarmap.door(m, GREEN, 260, 60, angle=90)
ajarmap.door(m, BLUE, 380, 60, angle=90)
ajarmap.pair(m, TEAL, (440, 60, 90), (500, 60, 90))
m.thing(320, 200, 2001)
m.thing(320, 240, 2002)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
