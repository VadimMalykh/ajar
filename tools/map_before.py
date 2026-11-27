"""The three times lab (map BEFORE): MAP=BEFORE ./run.sh

An engine lab for MAP24 (PLAN.md, "MAP24 "Left Hanging"" and "The three times
lab"): a place built three times, NOW, THEN (forty years earlier, 4096
north) and BEFORE (ten years before THEN, 8192 north: tools/ajarthen.py,
Times(before=True)), and two carried doors that join them, the clocked door
(NOW and THEN) and the ten-year door (THEN and BEFORE; src/zscript/then.zs).
NOW and THEN are a corridor with six bays, MAP11's look 3 (Post Box) and look
2 (Thaw); BEFORE is one open yard under the sky in look 1, the frames standing
free in their piers (short pieces of the walls to come) and nothing else but
what is said below.

  1 the hall (x 0..512): the clocked door, RED and the supplies lean NOW, the
    ten-year door leans THEN; the player starts NOW. Frames 101 and 102 (north
    wall) at all three times (121, 122 THEN; 141, 142 BEFORE); 103 (east wall)
    NOW and THEN only (123), so BEFORE has no twin of it. RED's far side is in
    the corridor's south wall at every time (201 NOW, 221 THEN, 241 BEFORE: a
    pier of its own BEFORE).
  2 the strongroom (x 640..1152): THEN and NOW four walls and no door. Frame
    104 (north wall) is the free frame BEFORE (144): the ten-year door hung
    there opens into the strongroom THEN (124). Frame 105 beside it, the
    second frame inside, for the clocked door on to NOW (125, 105). THEN a
    soul sphere, NOW a megasphere.
  3 the string line (x 1280..1792): BEFORE the builders' string line, A or B
    (a cause BEFORE; its lever on a pier where the bay's south wall will
    stand, and a target for each line before it, A west, B east, lit for the
    line strung). THEN and NOW the partition was built along it: A (x 1440)
    cuts off the west strip (a rocket launcher NOW), B (x 1616) the east strip
    (a plasma rifle NOW). Frame 106 (north wall): the targets BEFORE are seen
    and shot from THEN through the ten-year door hung there.
  4 the hoist (x 1920..2432): BEFORE the builders' hoist, its platform down
    or up 128 (a cause BEFORE; lever and two targets, down and up, on a pier
    where the east wall will stand). THEN and NOW a gallery at 128 (stairs)
    and a ledge at 128 (a megasphere NOW) with a gap between: the platform
    left up is a landing there, at both times, and the ledge is walked to.
    Frame 107 (west wall) faces the targets.
  5 the drip (x 2560..3072): the THEN lab's, a cause THEN that moves NOW only:
    THEN's valve, NOW a tank 96 deep and the ledge at 112 (blue armour).
    Frame 108 (west wall), the lever and target THEN on the east wall.
  6 company (x 3200..3712): the THEN lab's pen, NOW two imps and a demon,
    each time its own gate and lever; frame 109 (west wall).
The old door lab (PLAN.md, "The old door lab"; Times(old=True), then.zs: a
colour door hung at an earlier time is an old door in the same frame at every
later time) adds three bays and BLUE:
  7 the door left on the site (x 3840..4352): frame 110 (north wall); BLUE
    hangs BEFORE in 150 from the start, so THEN (130) and NOW (110) an old BLUE
    hangs there, ten and fifty years old, onto BLUE's far side in bay 8. THEN
    and NOW a closet off the north wall, open only while a colour door hangs
    BEFORE in 150 (a cause that follows that frame); a berserk pack in it NOW.
    An imp NOW (deaf), to follow the player through the old door.
  8 the water (x 4480..4992): NOW a tank (west, frame 111 in its north wall)
    and a dry room (east, BLUE's far side 202 in its north wall), each with a
    door from the corridor; THEN's valve on the tank's west wall fills the tank
    96 deep. BLUE left hanging THEN or BEFORE in 111's frame is an old door NOW
    between the two, and the water stands in both.
  9 the belt (x 5120..5632): THEN a belt runs east into frame 132 (east wall)
    with three crates on it, its lever THEN on the south wall. NOW a heap: at
    the belt's end, in front of 112, while the belt ran into an empty frame;
    in the corridor in front of RED's far side 201 while it ran with RED in
    132 (the crates went through RED THEN, onto the corridor at 221); none
    while it stood (a cause that follows frame 132 and the belt's cause).
The checks are src/zscript/beforetest.zs (MODE=1..9 tools/smoke.sh).
"""
import ajarmap
import ajarthen
import ajarwater as W
from ajarmap import RED, BLUE
from ajarthen import (Times, NOW, THEN, BEFORE, THEN_ID, LB, CO, LA, AR, FL, FC, FA, FR, KL, KC, KA, heights, LIVE,
                      CLOCKED, TENYEAR)
from udmf import Map, rect

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are
t = Times(m, at=(128, -96), before=True, old=True)      # the AjarThen thing, in NOW's corridor; BEFORE at twice the
                                                        # offset; a door left hanging is an old door later

ROOM = dict(wall=LA, ftex=FA, ctex=KA, ceil=256)
HALL = dict(wall=LB, ftex=FL, ctex=KL, ceil=256)
YARD = dict(wall=LA, ftex="FLAT10", ctex="F_SKY1", ceil=256)       # BEFORE: the site, under the sky; the piers look 1
HALL_X, STRONG_X, STRING_X, HOIST_X, DRIP_X, PEN_X = 0, 640, 1280, 1920, 2560, 3200
OLD_X, WATER_X, BELT_X = 3840, 4480, 5120                          # the old door lab's bays
STRING_TAG, HOIST_TAG, BASIN, GATE_NOW, GATE_THEN = 31, 32, 41, 61, 62
CLOSET_TAG, HEAP_TAG, TANK, DRY = 33, 34, 42, 43
BELT = ajarmap.BELT_TAG + 1
STRING, HOIST, DRIP = 11, 12, 13                                   # the causes' tids
VALVE, BELT_RUN, HEAP, CLOSET = 14, 15, 16, 17                     # ... the old door lab's
HEAP_FAR = (144, -176, 240, -128)                                  # NOW: the heap in front of RED's far side 201
END = BELT_X + 576                                                 # the corridor's east end
LATER = (NOW, THEN)                                                # the two times with walls


def box(x0, x1, y1, x2, y2):
    return (x0 + x1, y1, x0 + x2, y2)


def bay_door(x0, at=32):
    """The way in from the corridor NOW and THEN: an opening in the bay's south wall."""
    t.opening((x0 + at, 0), (x0 + at + 64, 0), (0, -1), only=LATER)


PIERS = []          # BEFORE: what stands in the yard, (x1, y1, x2, y2) in NOW's coordinates


def frame(a, b, out, n, **k):
    """A frame at every time (or `only`); BEFORE it stands in a pier: 16 of
    jamb either side, 16 behind the stub. BEFORE the recess is drawn before
    the yard round it, so its mouth (the line pressed to hang a door) would
    face into the recess: it is turned to face the yard (a use line only works
    from its front)."""
    first = len(m.polys)
    t.frame(a, b, out, n, **k)
    only = k.get("only")
    if only is None or BEFORE in (only if isinstance(only, tuple) else (only,)):
        pier(a, b, out)
        a2, b2 = t.before.P(a), t.before.P(b)
        recess = next(i for i in range(first, len(m.polys)) if a2 in m.polys[i] and b2 in m.polys[i])
        m.line(a2, b2, back=recess)


def pier(a, b, out):
    d = ajarmap.DEPTH + ajarmap.STUB + 16
    xs, ys = (a[0], b[0], a[0] + out[0] * d, b[0] + out[0] * d), (a[1], b[1], a[1] + out[1] * d, b[1] + out[1] * d)
    x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
    if out[1]:
        x1, x2 = x1 - 16, x2 + 16
    else:
        y1, y2 = y1 - 16, y2 + 16
    PIERS.append((x1, y1, x2, y2))


# --- the corridor ---------------------------------------------------------------------------------
CORRIDOR = dict(wall=CO, ftex=FC, ctex=KC, ceil=160)
t.room((-64, -176, END, -16), **CORRIDOR, light=208, only=THEN)


def tiles(area, holes):
    """The rectangle `area` less the rectangles `holes`, as rectangles: strips
    between the holes' x edges, each cut along y round the holes it crosses,
    strips alike side by side joined."""
    x1, y1, x2, y2 = area
    xs = sorted({x1, x2} | {h[0] for h in holes if x1 < h[0] < x2} | {h[2] for h in holes if x1 < h[2] < x2})
    out, open_ = [], {}
    for xa, xb in zip(xs, xs[1:]):
        cover = sorted((h[1], h[3]) for h in holes if h[0] <= xa and h[2] >= xb)
        spans, y = [], y1
        for ha, hb in cover:
            if ha > y:
                spans.append((y, ha))
            y = max(y, hb)
        if y < y2:
            spans.append((y, y2))
        for s in [s for s in open_ if s not in spans]:
            out.append((open_.pop(s), s[0], xa, s[1]))
        for s in spans:
            open_.setdefault(s, xa)
    out += [(xa, s[0], x2, s[1]) for s, xa in open_.items()]
    return out


for r in tiles((-64, -176, END, -16), [HEAP_FAR]):                        # NOW round the heap that may lie there
    t.now.room(r, **CORRIDOR, light=104)
HEAP_SECTOR = dict(side="AJDSTOR", id=HEAP_TAG)                            # (the heap's look: crates, their lids)
t.now.room(HEAP_FAR, **dict(CORRIDOR, **HEAP_SECTOR), light=104, raw=heights(floors=(0, 0, 24), raised="AJDSTOF"))
t.far((160, -176), (224, -176), (0, -1), RED)                              # RED's far side: 201 NOW, 221 THEN, 241 BEFORE
pier((160, -176), (224, -176), (0, -1))

# --- 1: the hall ----------------------------------------------------------------------------------
t.room((0, 0, 512, 512), **HALL, only=LATER)
bay_door(HALL_X, 96)
frame((96, 512), (160, 512), (0, 1), 101)
frame((352, 512), (416, 512), (0, 1), 102)
frame((512, 224), (512, 288), (1, 0), 103, only=LATER)                    # no BEFORE: the ten-year door refuses it
t.clocked(64, 96, 90)
ajarmap.door(m, RED, 200, 96, angle=90)
t.ten_year(400, 96, 90, when=THEN)
m.thing(128, 200, 1, angle=90)
for x, kind in ((48, 2001), (80, 2049), (176, 2002), (208, 2048)):       # a shotgun, shells, a chaingun, bullets
    m.thing(x, 320, kind)

# --- 2: the strongroom ----------------------------------------------------------------------------
X = STRONG_X
t.room(box(X, 0, 0, 512, 512), wall=AR, ftex=FR, ctex=KA, ceil=192, only=LATER)     # no door THEN and NOW
frame((X + 96, 512), (X + 160, 512), (0, 1), 104)                         # the free frame BEFORE: 144 to 124
frame((X + 352, 512), (X + 416, 512), (0, 1), 105)                        # the second frame inside: 125 to 105
t.then.thing(X + 256, 256, 2013)                                           # a soul sphere THEN
t.now.thing(X + 256, 256, 83)                                              # a megasphere NOW

# --- 3: the string line ---------------------------------------------------------------------------
X = STRING_X
A_X, B_X = 160, 336                                                        # the two partitions, 16 thick


def string_bay(c):
    if c.before:
        return
    for x1, x2 in ((0, A_X), (A_X + 16, B_X), (B_X + 16, 512)):
        c.room(box(X, x1, 0, x2, 512), **ROOM)
    for x, ceils in ((A_X, (0, 256)), (B_X, (256, 0))):                    # A built in setting 0, B in 1
        c.room(box(X, x, 0, x + 16, 512), floor=0, ceil=ceils[0], wall=LA, ftex=FA, ctex=FA, id=STRING_TAG,
               raw=heights(ceils=ceils, hold=True))
        for side in (x, x + 16):                                           # built, the wall goes on over it
            c.line((X + side, 0), (X + side, 512), upper=LA, dontpegtop=True)


t.both(string_bay)
bay_door(X, 192)
frame((X + 224, 512), (X + 288, 512), (0, 1), 106)
PIERS.append((X + A_X, -16, X + B_X + 16, 0))                              # BEFORE: where the south wall will stand
t.lever((X + 272, 0), (X + 336, 0), STRING, when=BEFORE)
for x, setting in ((A_X + 8, 0), (B_X + 8, 1)):                            # a target at each line's peg: A, B
    t.target(X + x, 12, STRING, setting, when=BEFORE)
t.cause(X + 256, 160, STRING, 2, tag=STRING_TAG, when=BEFORE)
t.now.thing(X + 80, 256, 2003)                                             # a rocket launcher in the west strip
t.now.thing(X + 432, 256, 2004)                                            # a plasma rifle in the east strip

# --- 4: the hoist ---------------------------------------------------------------------------------
X = HOIST_X
GAL, LAND, LEDGE, UP = (0, 192), (192, 320), (320, 512), 128
STAIR = (96, 192)


def hoist_bay(c):
    # (built up: then.zs puts it at its setting at once, Snap; so itemcheck, which knows nothing of causes, walks it)
    landing = dict(floor=UP, id=HOIST_TAG, side=LA, raw=heights(floors=(0, UP)))
    if c.before:
        c.room(box(X, LAND[0], 384, LAND[1], 512), **dict(YARD, ftex="AJTRIMF", **landing))     # the platform
        PIERS.append(box(X, LAND[0], 384, LAND[1], 512))
        return
    c.room(box(X, 0, 0, 512, 128), **ROOM)
    c.room(box(X, 0, 128, STAIR[0], 384), **ROOM)
    c.room(box(X, STAIR[1], 128, 512, 384), **ROOM)
    for k in range(8):                                                     # up to the gallery, 16 a step
        c.room(box(X, STAIR[0], 128 + 32 * k, STAIR[1], 160 + 32 * k), **dict(ROOM, floor=16 * (k + 1)))
    c.room(box(X, GAL[0], 384, GAL[1], 512), **dict(ROOM, floor=UP))
    c.room(box(X, LAND[0], 384, LAND[1], 512), **dict(ROOM, **landing))    # the landing, there or not
    c.room(box(X, LEDGE[0], 384, LEDGE[1], 512), **dict(ROOM, floor=UP))


t.both(hoist_bay)
bay_door(X, 224)
frame((X, 160), (X, 224), (-1, 0), 107)
PIERS.append((X + 512, 32, X + 528, 160))                                  # BEFORE: where the east wall will stand
t.lever((X + 512, 64), (X + 512, 128), HOIST, when=BEFORE)
for y, setting in ((48, 0), (144, 1)):                                     # down, up
    t.target(X + 500, y, HOIST, setting, when=BEFORE)
t.cause(X + 256, 200, HOIST, 2, tag=HOIST_TAG, when=BEFORE)
t.now.thing(X + 448, 448, 83)                                              # a megasphere on the ledge NOW

# --- 5: the drip (the THEN lab's) -----------------------------------------------------------------
X = DRIP_X


def drip_bay(c):
    if c.before:
        return
    tag = dict(id=BASIN) if c.now else {}
    for b in ((0, 0, 512, 448), (0, 448, 128, 512), (384, 448, 512, 512)):
        c.room(box(X, *b), **ROOM, **tag)
    c.room(box(X, 128, 448, 384, 512), **dict(ROOM, floor=112), **tag)     # the ledge
    ajarmap.roomdoor(m, c.P((X + 32, -16)), c.P((X + 96, -16)), (0, 1), 0)


t.both(drip_bay)
frame((X, 224), (X, 288), (-1, 0), 108, now=dict(tag=BASIN))
t.lever((X + 512, 288), (X + 512, 352), DRIP)
t.target(X + 500, 256, DRIP)
t.cause(X + 256, 160, DRIP, 2, basin=BASIN, depth=96)
W.basin(m, BASIN, 512 * 512, 240, floor=0, at=(X + 256, 200))
W.rate(m, X + 300, 100, 0, 0, W.FLOAT)                                    # the player floats up when idle under water
t.now.thing(X + 256, 480, 2019)                                            # blue armour on the ledge

# --- 6: company (the THEN lab's pen) --------------------------------------------------------------
X = PEN_X


def pen_bay(c):
    if c.before:
        return
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
frame((X, 224), (X, 288), (-1, 0), 109)
for kind, x, y in ((3001, 176, 700), (3001, 336, 700), (3002, 256, 620)):  # two imps and a demon, NOW
    t.now.thing(X + x, y, kind, angle=270, skill=1)


# --- 7: the door left on the site (the old door lab) ---------------------------------------------
X = OLD_X


def old_bay(c):
    if c.before:
        return
    c.room(box(X, 0, 0, 512, 512), **ROOM)
    c.room(box(X, 352, 512, 416, 528), floor=0, ceil=128, wall=LA, ftex=FA, ctex=FA, id=CLOSET_TAG,
           raw=heights(ceils=(0, 128), hold=True))                         # the closet's mouth: open while 150 holds a door
    for y in (512, 528):
        c.line((X + 352, y), (X + 416, y), upper=LA, dontpegtop=True)
    c.room(box(X, 320, 528, 448, 656), **dict(ROOM, ceil=128))              # the closet


t.both(old_bay)
bay_door(X, 224)
frame((X + 96, 512), (X + 160, 512), (0, 1), 110)                          # BLUE in it BEFORE (150) from the start
ajarmap.door(m, BLUE, *t.before.P((X + 128, 400)), frame=150)
t.frame_cause(X + 256, 200, CLOSET, 150, tag=CLOSET_TAG)
t.now.thing(X + 384, 600, 2023)                                            # a berserk pack in the closet NOW
t.now.thing(X + 256, 400, 3001, angle=270, skill=1, ambush=True)           # an imp NOW, deaf: it follows through old BLUE

# --- 8: the water (the old door lab) --------------------------------------------------------------
X = WATER_X


def water_bay(c):
    if c.before:
        return
    c.room(box(X, 0, 0, 224, 512), **ROOM, **(dict(id=TANK) if c.now else {}))          # the tank
    c.room(box(X, 288, 0, 512, 512), **ROOM, **(dict(id=DRY) if c.now else {}))         # the dry room
    for x in (80, 368):
        ajarmap.roomdoor(m, c.P((X + x, -16)), c.P((X + x + 64, -16)), (0, 1), 0)


t.both(water_bay)
frame((X + 80, 512), (X + 144, 512), (0, 1), 111, now=dict(tag=TANK))
t.far((X + 368, 512), (X + 432, 512), (0, 1), BLUE, now=dict(tag=DRY))     # BLUE's far side: 202, 222, 242
pier((X + 368, 512), (X + 432, 512), (0, 1))
t.lever((X, 288), (X, 352), VALVE)
t.cause(X + 112, 160, VALVE, 2, basin=TANK, depth=96)
W.basin(m, TANK, 224 * 512, 240, floor=0, at=(X + 112, 200))
W.basin(m, DRY, 224 * 512, 240, floor=0, at=(X + 400, 200))

# --- 9: the belt (the old door lab) ---------------------------------------------------------------
X = BELT_X
BELT_Y = (224, 288)                                                        # the belt, a door wide; its curbs 16 more


def belt_bay(c):
    if c.before:
        return
    if c.then:
        for b in ((0, 0, 512, BELT_Y[0] - 16), (0, BELT_Y[1] + 16, 512, 512), (0, BELT_Y[0] - 16, 64, BELT_Y[1] + 16)):
            c.room(box(X, *b), **ROOM)
        first = len(m.sectors)
        ajarmap.belt(m, c.P((X + 64, 256)), c.P((X + 512, 256)), BELT, scroll=False, light=c.light)
        for sec in m.sectors[first:]:                                      # under the room's own ceiling
            sec.update(ceil=256, ctex=c.tex(KA))
        return
    for b in ((0, 0, 512, 208), (0, 304, 512, 512), (0, 208, 352, 304)):
        c.room(box(X, *b), **ROOM)
    for x1, x2, up in ((352, 432, 12), (432, 512, 24)):                    # the heap at the belt's end: setting 1
        c.room(box(X, x1, 208, x2, 304), **dict(ROOM, **HEAP_SECTOR), raw=heights(floors=(0, up, 0), raised="AJDSTOF"))


t.both(belt_bay)
bay_door(X, 224)
frame((X + 512, 224), (X + 512, 288), (1, 0), 112, then=dict(tag=BELT))    # the belt runs into it THEN (132)
t.lever((X + 352, 0), (X + 416, 0), BELT_RUN)
t.cause(X + 256, 420, BELT_RUN, 2)
t.belt_run(X + 256, 440, BELT_RUN, BELT, (ajarmap.BELT_SPEED, 0))
for x in (160, 224, 288):                                                  # three crates on it THEN
    t.then.thing(X + x, 256, 20094)
t.frame_cause(X + 128, 400, HEAP, 132, tag=HEAP_TAG, gate=BELT_RUN, colour=RED)

# --- BEFORE: the yard -----------------------------------------------------------------------------
for r in tiles((-192, -384, END + 128, 720), PIERS):
    t.before.room(r, **YARD)

# --- the times' ids (frames n, n + 20, n + 40; RED's far side 201, 221, 241) ------------------------
problems = ajarthen.check_ids(m)
assert not problems, problems

# --- the puzzle (tools/solve.py: three times, two clocked doors, a door left hanging) --------------
# NOW and THEN each one region but for what a cause cuts off (the strips beside the partitions, the hoist's
# ledge, the drip's ledge NOW) and the strongroom; BEFORE one yard. The goal is the strongroom NOW
# (the three times lab's was the strongroom THEN: NOW was out of reach with the two clocked doors alone, since the
# clocked door could not be brought into the strongroom THEN). With a door left hanging (old=True) a colour door
# left BEFORE in the strongroom's free frame 144 is an old door into it THEN (124) and NOW (104), each onto its
# far side at that time. Bays 7 to 9 (BLUE, the closet, the water, the belt) move nothing the puzzle needs and
# are left out: with BLUE as a fourth door the search ran past ten minutes and 3.7 GB (57375 states without).
ROOMS = {101: "now", 102: "now", 103: "now", 104: "strongroom now", 105: "strongroom now", 106: "now",
         107: "now", 108: "now", 109: "now"}
FRAMES = dict(ROOMS)
FRAMES.update({n + THEN_ID: r.replace("now", "then") for n, r in ROOMS.items()})
FRAMES.update({n + 2 * THEN_ID: "before" for n in ROOMS if n != 103})
PUZZLE = dict(
    start="now", goal="strongroom now", old=True,
    names={RED: "RED", CLOCKED: "the clocked door", TENYEAR: "the ten-year door"},
    frames=FRAMES,
    twins={n: n + THEN_ID for n in ROOMS},
    befores={n + THEN_ID: n + 2 * THEN_ID for n in ROOMS if n != 103},
    doors={CLOCKED: dict(clock=True, lean="now"),
           TENYEAR: dict(clock=True, span=1, lean="then"),
           RED: dict(home="now", home_then="then", home_before="before", lean="now")},
    causes={"string": dict(states=("A", "B"), start="A", at=["before"], via={106 + THEN_ID: "then"}, door=TENYEAR),
            "hoist": dict(states=("down", "up"), start="down", at=["before"], via={107 + THEN_ID: "then"}, door=TENYEAR),
            "valve": dict(states=("shut", "open"), start="shut", at=["then"], via={108: "now"}, door=CLOCKED)},
    walk=[w for time in ("now", "then") for w in (
              (time, f"string west {time}", "", None, {"string": "B"}), (f"string west {time}", time, "", None, {"string": "B"}),
              (time, f"string east {time}", "", None, {"string": "A"}), (f"string east {time}", time, "", None, {"string": "A"}),
              (time, f"hoist ledge {time}", "", None, {"hoist": "up"}), (f"hoist ledge {time}", time))]
         + [("now", "drip ledge now", "", None, {"valve": "open"}), ("drip ledge now", "now")],
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
