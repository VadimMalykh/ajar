"""The then and now lab (map THEN): MAP=THEN ./run.sh

An engine lab for levels 21 to 30 (PLAN.md, "Levels 21 to 30" and "The then
and now lab"): a place built twice, NOW and THEN (forty years earlier,
4096 north: tools/ajarthen.py), and a carried door that joins them, the
clocked door (src/zscript/then.zs). Bays off one corridor, both times alike
but where said; NOW is MAP11's look 3 (Post Box), THEN look 2 (Thaw).

  1 the hall (x 0..768): W, M, E from west to east. The clocked door, RED
    and the supplies lean in W NOW; the player starts there. Frames 101 (W),
    102 (M), 103 (E), all in the north wall, twinned (121..123 THEN). NOW a
    block of rubble cuts W from M; THEN a steel gate (shut for good) closes
    the gap from M to E that NOW stands open. Reaching E takes two hangings,
    one through each time. THEN only: frame 131 in W's west wall, which has
    no twin (it does not take the clocked door). NOW only: RED's far side in
    the corridor's south wall, and the lever that turns the music by time
    off (W's west wall).
  2 the belt (x 896..1408): THEN a belt runs from frame 124 (west wall) east
    to where NOW a heap of crates stands (steps 24 apart up to a ledge at 120
    with a megasphere); with the belt standing the heap was never there and
    a pit with a berserk pack under its first step is open. The lever and a
    target THEN on the east wall, straight across from the frame.
  3 the drip (x 1536..2048): the bay is a tank NOW (water.zs): with the valve
    THEN open it stands 96 deep, and the ledge on the north wall (112, blue
    armour) is reached by floating up; shut, it is dry. THEN dry always.
    Frame 106/126 in the west wall, the valve's lever and target THEN on the
    east wall. An ordinary door from the corridor.
  4 the beam (x 2176..2688): THEN an emitter in the middle: off, at the west
    wall (A) or at the east wall (B). NOW the wall it points at has a burnt
    hole 64 wide and 96 high, a closet behind each (a rocket launcher, a
    plasma rifle). The lever and three targets (A, off, B) THEN on the south
    wall, across from frame 107/127 in the north wall.
  5 company (x 2880..3392): a pen north of the bay behind a gate; NOW two imps
    and a demon in it. A lever beside the gate opens it (at either time, its
    own time's gate). Frame 105/125 in the west wall.
The checks are src/zscript/thentest.zs (MODE=1..6 tools/smoke.sh).
"""
import ajarmap
import ajarwater as W
from ajarmap import RED, far_id
from ajarthen import (Times, NOW, THEN, LB, CO, LA, AR, FL, FC, FA, FR, KL, KC, KA, heights, LIVE)
from udmf import Map, rect

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are
t = Times(m, at=(128, -96))                 # the AjarThen thing, in NOW's corridor

ROOM = dict(wall=LA, ftex=FA, ctex=KA, ceil=256)
HALL = dict(wall=LB, ftex=FL, ctex=KL, ceil=256)
HALL_X, BELT_X, DRIP_X, BEAM_X, PEN_X = 0, 896, 1536, 2176, 2880
HEAP, HOLES, BASIN, GATE_NOW, GATE_THEN, BELT = 31, 50, 41, 61, 62, 901
BELT_CAUSE, DRIP_CAUSE, BEAM_CAUSE, MUSIC = 11, 12, 13, 990


def box(x0, x1, y1, x2, y2):
    return (x0 + x1, y1, x0 + x2, y2)


def bay_door(x0):
    """The way in from the corridor: an opening in the bay's south wall."""
    t.opening((x0 + 32, 0), (x0 + 96, 0), (0, -1))


# --- the corridor ---------------------------------------------------------------------------------
t.room((-64, -176, 3456, -16), wall=CO, ftex=FC, ctex=KC, ceil=160, now=dict(light=104), then=dict(light=208))
t.now.far((160, -176), (224, -176), (0, -1), RED, target=101)              # RED's far side: NOW only

# --- 1: the hall ----------------------------------------------------------------------------------
t.room((0, 0, 256, 512), **HALL)                                           # W
t.room((256, 0, 288, 512), **HALL,                                         # the rubble NOW, floor THEN
       now=dict(floor=256, wall="TANROCK2", side="TANROCK2", ftex="RROCK09", ctex="RROCK09"))
t.room((288, 0, 512, 512), **HALL)                                         # M
t.room((528, 0, 768, 512), **HALL)                                         # E


def gap(c):
    """M to E: open NOW, a steel gate THEN (no lever: shut for good)."""
    if c.now:
        c.room((512, 224, 528, 288), ceil=96, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
        return
    c.room((512, 224, 528, 288), ceil=0, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF", light=160)
    for p, q in (((512, 224), (512, 288)), ((528, 224), (528, 288))):
        c.line(p, q, exact=True)
    for p, q in (((512, 224), (528, 224)), ((512, 288), (528, 288))):
        c.line(p, q, mid="AJTRIM", dontpegbottom=True)


t.both(gap)
bay_door(HALL_X + 64)
t.frame((96, 512), (160, 512), (0, 1), 101)
t.frame((368, 512), (432, 512), (0, 1), 102)
t.frame((616, 512), (680, 512), (0, 1), 103)
t.frame((0, 224), (0, 288), (-1, 0), 131, only=THEN)                      # no twin: no clocked door here
t.music((0, 384), (0, 448), (40, 416), MUSIC)
t.clocked(64, 96, 90)
ajarmap.door(m, RED, 200, 96, angle=90)
m.thing(128, 200, 1, angle=90)
for x, kind in ((48, 2001), (80, 2049), (176, 2002), (208, 2048)):       # a shotgun, shells, a chaingun, bullets
    m.thing(x, 320, kind)
m.thing(648, 256, 2013)                                                    # E's prize: a soulsphere

# --- 2: the belt ----------------------------------------------------------------------------------
X = BELT_X
STEPS = ((208, 256, -24, 24), (256, 304, -48, 24), (304, 352, 0, 48), (352, 400, 0, 72), (400, 448, 0, 96))


def belt_bay(c):
    if c.now:
        for b in ((0, 0, 512, 320), (0, 448, 512, 512), (0, 320, 208, 448)):
            c.room(box(X, *b), **ROOM)
        for x1, x2, down, up in STEPS:                                     # the heap: down (setting 0), up (1)
            c.room(box(X, x1, 320, x2, 448), **dict(ROOM, floor=down, side="AJDSTOR", id=HEAP,
                                                     raw=heights(floors=(down, up), raised="AJDSTOF")))
        c.room(box(X, 448, 320, 512, 448), **dict(ROOM, floor=120))         # the ledge
        return
    for b in ((0, 0, 512, 336), (0, 432, 512, 512), (448, 336, 512, 432)):
        c.room(box(X, *b), **ROOM)
    first = len(m.sectors)
    ajarmap.belt(m, c.P((X, 384)), c.P((X + 448, 384)), BELT, scroll=False, light=c.light)
    for s in m.sectors[first:]:                                            # under the room's own ceiling
        s.update(ceil=256, ctex=c.tex(KA))


t.both(belt_bay)
bay_door(X)
t.frame((X, 352), (X, 416), (-1, 0), 104)
t.lever((X + 512, 224), (X + 512, 288), BELT_CAUSE)
t.target(X + 500, 384, BELT_CAUSE)
t.cause(X + 256, 160, BELT_CAUSE, 2, tag=HEAP)
t.belt_run(X + 256, 200, BELT_CAUSE, BELT, (8, 0))
t.now.thing(X + 480, 384, 83)                                              # a megasphere on the ledge
t.hidden(X + 280, 384, 2023, BELT_CAUSE)                                   # a berserk pack in the pit

# --- 3: the drip ----------------------------------------------------------------------------------
X = DRIP_X


def drip_bay(c):
    tag = dict(id=BASIN) if c.now else {}
    for b in ((0, 0, 512, 448), (0, 448, 128, 512), (384, 448, 512, 512)):
        c.room(box(X, *b), **ROOM, **tag)
    c.room(box(X, 128, 448, 384, 512), **dict(ROOM, floor=112), **tag)     # the ledge
    ajarmap.roomdoor(m, c.P((X + 32, -16)), c.P((X + 96, -16)), (0, 1), 0)


t.both(drip_bay)
t.frame((X, 224), (X, 288), (-1, 0), 106, now=dict(tag=BASIN))
t.lever((X + 512, 288), (X + 512, 352), DRIP_CAUSE)
t.target(X + 500, 256, DRIP_CAUSE)
t.cause(X + 256, 160, DRIP_CAUSE, 2, basin=BASIN, depth=96)
W.basin(m, BASIN, 512 * 512, 240, floor=0, at=(X + 256, 200))
W.rate(m, X + 300, 100, 0, 0, W.FLOAT)                                    # the player floats up when idle under water
t.now.thing(X + 256, 480, 2019)                                            # blue armour on the ledge

# --- 4: the beam ----------------------------------------------------------------------------------
X = BEAM_X


def beam_bay(c):
    c.room(box(X, 0, 0, 512, 512), **ROOM)
    if c.then:
        return
    for (h1, h2), (k1, k2), face, back, ceils in (((-16, 0), (-112, -16), 0, -16, (0, 96, 0)),
                                                  ((512, 528), (528, 624), 512, 528, (0, 0, 96))):
        c.room(box(X, h1, 224, h2, 288), floor=0, ceil=0, wall="ASHWALL2", ftex="AJTRIMF", ctex="AJTRIMF",
               id=HOLES, raw=heights(ceils=ceils, hold=True))
        c.room(box(X, k1, 192, k2, 320), **dict(ROOM, ceil=128))           # the closet behind it
        for x in (face, back):                                             # shut, the wall goes on over it
            c.line((X + x, 224), (X + x, 288), upper=LA, dontpegtop=True)


t.both(beam_bay)
bay_door(X)
t.frame((X + 352, 512), (X + 416, 512), (0, 1), 107)
t.lever((X + 160, 0), (X + 224, 0), BEAM_CAUSE)
for x, setting in ((320, 1), (384, 0), (448, 2)):                          # A (west), off, B (east)
    t.target(X + x, 12, BEAM_CAUSE, setting)
t.cause(X + 256, 160, BEAM_CAUSE, 3, tag=HOLES)
t.beam(X + 256, 256, BEAM_CAUSE, (180, 0))
t.now.thing(X - 64, 256, 2003)                                             # a rocket launcher behind A
t.now.thing(X + 576, 256, 2004)                                            # a plasma rifle behind B

# --- 5: company -----------------------------------------------------------------------------------
X = PEN_X


def pen_bay(c):
    gate = GATE_NOW if c.now else GATE_THEN
    c.room(box(X, 0, 0, 512, 512), **ROOM)
    c.room(box(X, 96, 528, 416, 784), wall=AR, ftex=FR, ctex=KA, ceil=160)
    c.room(box(X, 224, 512, 288, 528), ceil=0, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF", light=160, id=gate)
    for y in (512, 528):
        c.line((X + 224, y), (X + 288, y), exact=True)
    for x in (224, 288):
        c.line((X + x, 512), (X + x, 528), mid="AJTRIM", dontpegbottom=True)
    c.cut((X + 96, 512), (X + 160, 512))
    c.line((X + 96, 512), (X + 160, 512), special=11, args=(gate, 16), playeruse=True, mid=LIVE[c.when],
           exact=True, dontpegbottom=True)


t.both(pen_bay)
bay_door(X)
t.frame((X, 224), (X, 288), (-1, 0), 105)
for kind, x, y in ((3001, 176, 700), (3001, 336, 700), (3002, 256, 620)):  # two imps and a demon, NOW
    t.now.thing(X + x, y, kind, angle=270, skill=1)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
