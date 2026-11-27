"""Act 3, level 2: "Day Return" (MAP22). PLAN.md, "MAP22 "Day Return": the
first version, as decided", "... the first playable version", "MAP22: BLUE's
ambush ... gated" and "MAP22 bigger"; the puzzle is tools/puzzle22.py, the
level's script src/zscript/map22.zs.

All of MAP10's town twice (tools/ajarthen.py, src/zscript/then.zs):
  NOW   MAP10's own, at night, at MAP10's own coordinates: the old bus, the
        kiosk (a secret), the shelter, the depot with its company, the theatre
        (MAP03's excerpt with MAP03's monsters and pick-ups), the night room
        over the shelter, whole (frame 105; its hole down into the shelter
        shut by Doom's stone); the other stop with the old 20; the
        observatory (library and dome: key 3 lies on the dome's floor); the
        museum (great hall, gallery, cellar; PINK's store a secret). No hotel,
        no station: doors 1 and 5 of the old bus are Doom's stone.
  THEN  forty years earlier, by day, NOW + OFF (12288 north): the new bus, the
        shelter, the depot (the clocked door leans in its fitters' corner,
        under their tag: FOUND IN THE YARD. NOT OURS.), the theatre, the other
        stop with the new 20, the observatory, the museum, and the two places
        the fixed lines go, the hotel (MAP02, line 1) and the station (MAP05,
        line 5; YELLOW on its far platform), the excerpts as MAP10 lifts them
        out (ajarmap.excerpt) but with no monsters and no pick-ups. Behind the
        shelter's brass door (keys 3 and 4) a stair up to the night room:
        BLUE's far side THEN west of a gate (a bolted door, bolted on its east
        side), the brass frame HOME and frame 125 east of it.

The 10's doors (south face 1..6, back 7 and 8), THEN / NOW:
  1  the hotel (doorway 1)                 / Doom's stone
  2  frame 121, RED hangs in it             / frame 101
  3  GREEN's far side, shut (no GREEN)      / the same
  4  frame 124, any door                    / frame 104, any door
  5  the station (doorway 2)                / Doom's stone
  6  frame 123, brass, any door, no twin    / MAP10's brass frame, stone in it
  7  frame 122                              / frame 102
  8  the 20's door 1 (doorway 4)            / the same (doorway 3)
The 20's doors (south face 1..3, back 4), the same at both times: 1 door 8 of
the 10; 2 the pit under the theatre's stage door (doorways 6 THEN, 5 NOW); 3
frames 126 / 106, any door; 4 the observatory's library (doorways 8, 7). No
frame of a bus is the clocked door's alone; 105 / 125 in the night room are.
Far sides at both times (Times.far): RED in the theatre's foyer, YELLOW in the
depot's south wall, BLUE in the night room's west end. Locked doors (both
sides): the museum's (key 1), the dome's (key 2), the shelter's brass door
(keys 3 and 4).

The turn (map22.zs): the first time the clocked door hangs in a twinned
frame. Ambush cause 64 (the turn) brings every THEN place its company, each
when the player is next there (near=); three of them carry keys (args[4]): key
1 the hotel lobby's baron, key 2 the theatre's baron in the orchestra pit, key
4 the museum's mancubus in the great hall. Key 3 taken (cause 3): the dome's
ambush now. Cause 65 with args[4] 34: keys 3 and 4 both in hand, the last
fight at the stop then. BLUE taken (cause 10 + BLUE): the theatre now's
ambush, an arch-vile with it. The gate's bolt drawn (AMBUSH_BOLTS): a small
company west of it.
"""
import math

import ajarmap
import ajarthen
import budget
import map_hinges10 as ten
import map_hinges2
import map_hinges3
import map_hinges5
import puzzle22
from ajarmap import RED, BLUE, GREEN, YELLOW, far_id, HOME
from ajarthen import Times, NOW, THEN, THEN_ID
from udmf import Map, rect, MONSTERS

m = Map()
OFF = (0, 12288)                    # THEN is NOW shifted by this: the NOW theatre (to y -2464) and the THEN theatre
                                    # (from y 7552) lie either side of the half (6144 + AT's y)
AT = (0, -200)                      # the AjarThen thing, in the square NOW
t = Times(m, off=OFF, at=AT)
if ten.LOOK:
    import gfx_square
    m.align |= gfx_square.ALIGNED

D, DY, LINE, NX, NY = ten.D, ten.DY, ten.LINE, ten.NX, ten.NY
HX, SX, TY = ten.HX, ten.SX, ten.TY
Q, FENCE, BRICK = ten.Q, ten.FENCE, ten.BRICK
PAVE, STOP, SQUARE, SEAT, WOOD, OPEN = ten.PAVE, ten.STOP, ten.SQUARE, ten.SEAT, ten.WOOD, ten.OPEN
STALLS, FOYER, BACKSTAGE = ten.STALLS, ten.FOYER, ten.BACKSTAGE
NIGHT, DAY = ten.NIGHT, 224         # the square's light NOW (MAP10's) and THEN
LIVERY = {NOW: "B", THEN: "E"}      # the old bus (gfx_bus) and the new one (gfx_dayreturn)
STONE = "TANROCK2"                  # Doom's stone (as MAP21's), where a way was THEN and is not NOW
BRASS = ("AJXA", "AJXAF")
SKY_TAG = 2200                      # THEN's sky sectors: the day sky (a sky transfer, Static_Init 255)
SQUARE_TID = 2201                   # the square's company NOW, woken by the turn (map22.zs)
KIOSK = ten.KIOSK
TURN, LAST_KEYS = 64, 65            # ambush causes (ajar.zs): the turn; the two keys args[4] names in hand (34)
DAYLIGHT = 40                       # THEN the excerpts are this much lighter than in MAP10


class At:
    """The map as one copy (ajarthen.Copy) sees it: every point given in NOW's
    coordinates is put at that copy's, so that ajarmap's pieces and MAP10's
    code can build either time unchanged."""

    def __init__(self, c):
        self.__dict__.update(c=c, dx=c.dx, dy=c.dy)

    def P(self, p):
        return (p[0] + self.dx, p[1] + self.dy)

    def sector(self, poly, **k):
        return m.sector([self.P(p) for p in poly], **k)

    def line(self, a, b, **k):
        m.line(self.P(a), self.P(b), **k)

    def cut(self, *pts):
        m.cut(*(self.P(p) for p in pts))

    def thing(self, x, y, type, **k):
        m.thing(x + self.dx, y + self.dy, type, **k)

    def __getattr__(self, k):
        return getattr(m, k)

    def __setattr__(self, k, v):
        setattr(m, k, v)


AT_ = {c.when: At(c) for c in t.copies}


# --- MAP10's helpers (map_hinges10.py), for a copy --------------------------------------------------------------
def low(floor=0, wall=None, ctex=None):
    return ten.low(floor, wall, ctex)


def over(S, a, b, tex, **k):
    if tex:
        S.line(a, b, upper=tex, dontpegtop=True, **k)


def porch(S, box, tex, sides, peg=True):
    x1, y1, x2, y2 = box
    ends = dict(S=((x1, y1), (x2, y1)), E=((x2, y1), (x2, y2)), N=((x2, y2), (x1, y2)), W=((x1, y2), (x1, y1)))
    for side in sides if tex else ():
        S.line(*ends[side], upper=tex, **(dict(dontpegtop=True) if peg else dict(exact=True)))


def pieces(S, fixed, starts, axis, tex, **k):
    for s in starts if tex else ():
        a, b = ((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
        S.cut(a, b)
        S.line(a, b, mid=tex, **k)


def bars(S, a, b, out, floor, thick=16, near=None, far=None):
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    S.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall="AJTRIM" if near else "AJBRICK",
             ftex="AJTRIMF", ctex="AJTRIMF")
    S.line(a, b, mid="AJWIN", midboth=True, blocking=True)
    if near:
        S.line(a, b, upper=near, lower=near, dontpegtop=True, dontpegbottom=True)
    if far:
        S.line(c, d, upper=far, lower=far, dontpegtop=True, dontpegbottom=True)


def stone(S, a, b, out, floor=0, trim=None):
    """NOW: Doom's stone in a way that was there THEN (a door of the bus, a
    frame): a shallow recess with the stone at its back."""
    p = lambda q: (q[0] + out[0] * 16, q[1] + out[1] * 16)
    wall, flat = trim or ("AJTRIM", "AJTRIMF")
    S.sector([a, b, p(b), p(a)], floor=floor, ceil=floor + 96, light=150, wall=wall, ftex=flat, ctex=flat)
    S.line(p(a), p(b), mid=STONE, dontpegbottom=True)


def things(S, kind, *spots, angle=0, **k):
    for x, y in spots:
        S.thing(x, y, kind, angle=angle, **k)


def to_now(c, place):
    """An excerpt's recess place (in the map's coordinates) in NOW's."""
    a, b, out, floor = place
    return (a[0] - c.dx, a[1] - c.dy), (b[0] - c.dx, b[1] - c.dy), out, floor


ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACH, PAIN, VILE = 65, 69, 3003, 66, 3006, 3005, 67, 68, 71, 64
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS, CELL = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17, 2047)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGARMOR, SPHERE, BERSERK, MEGA, BACKPACK = (
    2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023, 83, 8)
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
PICKUPS = (set(budget.AMMO) | set(budget.HEAL) | set(budget.ARM) | set(budget.WEAP)
           | {MEGA, 2022, 2024, 2025, 2026, 2045, 5, 6, 13, 38, 39, 40})
GORE = {10, 12, 15, 18, 19, 20, 21, 22, 23, 24, 79, 80, 81}          # what was left lying about in part 1


def peaceful(first_thing, first_sector):
    """THEN: what an excerpt brought along since these indices loses its
    monsters and its pick-ups (lamps, furniture and scenery stay: nothing lies
    about in a town at peace), and its rooms are lit by day."""
    m.things[first_thing:] = [th for th in m.things[first_thing:]
                              if th["type"] not in MONSTERS | PICKUPS | GORE]
    for s in m.sectors[first_sector:]:
        s["light"] = min(255, s["light"] + DAYLIGHT)


# =================================================================================================================
# THE SQUARE, THE BUS, THE SHELTER, THE LANE (both times, MAP10's plan)
# =================================================================================================================
MOUTHS = {}         # (copy, door number 1..8): its mouth (NOW's coordinates)
for c in t.copies:
    S, L, then = AT_[c.when], (DAY if c.then else NIGHT), c.then
    ajarmap.fitted(S, (-512, -640, 224, -48), [
        ((-448, -640, -256, -576), low(wall="AJQK", ctex="AJQSC")),              # before the kiosk: its canopy
        ((-512, -432, -448, -304), low(wall="AJQMP")),                           # before the museum's door
        ((-192, -400, -64, -368), SEAT), ((64, -400, 192, -368), SEAT),
    ], floor=0, light=L, **PAVE, **SQUARE)
    porch(S, (-448, -640, -256, -576), Q("AJQKF"), "NEW", peg=False)
    porch(S, (-512, -432, -448, -304), Q("AJQMF"), "NES", peg=False)
    for a, b in (((-512, -640), (-512, -432)), ((-512, -304), (-512, -128))):    # the museum's side of the square
        S.cut(a, b)
        if ten.LOOK:
            S.line(a, b, mid="AJQM")
    pieces(S, -512, (-576, -256), "y", Q("AJQMA"))
    pieces(S, -640, (-192,), "x", Q("AJQFA"))
    pieces(S, -640, (64,), "x", Q("AJQFB"))
    # (the museum's door, a real one with the plate 1, is built with the museum below)
    # the shelter, its roof, the route board; THEN its timetable
    SHELTER = low(wall="AJQS", ctex="AJQSC")
    ajarmap.fitted(S, (224, -208, 512, -48), [
        ((256, -208, 512, -144), SHELTER),
        ((448, -208, 512, -48), SHELTER),
    ], floor=0, light=L + 10, **STOP, **SQUARE)
    if ten.LOOK:
        for a, b in (((256, -144), (448, -144)), ((256, -208), (256, -144)), ((448, -144), (448, -48)), ((448, -48), (512, -48))):
            S.line(a, b, upper="AJQSF", exact=True)
        pieces(S, -208, (448,), "x", "AJ22TT" if then else "AJQSA")
    # the bus stands free: past its two ends and along the lane behind it
    ajarmap.fitted(S, (-640, -48, -400, 192), [], floor=0, light=L, **PAVE, **SQUARE)
    ajarmap.fitted(S, (400, -48, 640, 192), [], floor=0, light=L, **PAVE, **SQUARE)
    ajarmap.fitted(S, (-640, 192, 640, 448), [
        ((416, 384, 512, 448), low(wall=Q("AJQB"))),                             # under the depot's gate
        ((-192, 304, -64, 336), SEAT), ((64, 304, 192, 336), SEAT),
    ], floor=0, light=L, **PAVE, **SQUARE)
    porch(S, (416, 384, 512, 448), Q("AJQDF"), "SEW", peg=False)
    pieces(S, 448, (-448, 256), "x", Q("AJQFA"))
    pieces(S, 448, (-128,), "x", Q("AJQFB"))
    pieces(S, 640, (64,), "y", Q("AJQFA"))
    pieces(S, -640, (256,), "y", Q("AJQFB"))
    south = ajarmap.bus(S, -400, 0, face=1, floor=0, first=1, free=True, livery=LIVERY[c.when], light=L + 20, **STOP)
    north = ajarmap.bus(S, -400, 144, face=-1, floor=0, first=7, slots=(4, 1), free=True, livery=LIVERY[c.when],
                        light=L + 20, **STOP)
    ajarmap.bus_ends(S, -400, 0, livery=LIVERY[c.when])
    for n, mouth in enumerate(south + north):
        MOUTHS[c.when, n + 1] = mouth
    if c.now:
        S.line(*south[3], upper="AJBN0")                                         # 4: the plate lost
        stone(S, *south[0], (0, 1))                                              # 1 and 5: Doom's stone NOW
        stone(S, *south[4], (0, 1))
        stone(S, *south[5], (0, 1), trim=BRASS)                                  # 6: MAP10's brass frame, stone in it
        stone(S, (288, -208), (352, -208), (0, -1), trim=BRASS)                  # ... and the shelter's, facing it
        # (a lamp for GREEN, which is not in the level, is never lit: doors 1, 3, 5 and 6 run nowhere NOW)
        ajarmap.route_board(S, (512, -56), [(1, GREEN), (2, 101), (3, GREEN), (4, 104), (5, GREEN), (6, GREEN),
                                            (7, 102), (8, None)], step=(0, -16))
    else:
        ajarmap.route_board(S, (512, -56), [(1, None), (2, 121), (3, GREEN), (4, 124), (5, None), (6, 123),
                                            (7, 122), (8, None)], step=(0, -16))
    # lamps and benches, at both times
    things(S, LAMP, (-480, -176), (192, -80), (-480, -608), (192, -608), (480, -80), (-616, 424), (616, 424))

# THEN door 6: frame 123, brass, any colour door; no twin (the clocked door will not hang there)
t.then.frame(*MOUTHS[THEN, 6], (0, 1), 123, twin=False, trim=BRASS)
# doors 2, 4 and 7: twins at both times, any door, in the bus's ordinary trim. No frame of a bus is the clocked
# door's alone (PLAN.md, "MAP22 bigger"): that it hangs there is the accident
t.frame(*MOUTHS[NOW, 2], (0, 1), 101)
t.frame(*MOUTHS[NOW, 7], (0, -1), 102)
t.frame(*MOUTHS[NOW, 4], (0, 1), 104)
# door 3: GREEN's far side at both times, shut for good (there is no GREEN here)
t.far(*MOUTHS[NOW, 3], (0, 1), GREEN)

# The kiosk NOW (MAP10's secret), seen through bars: shoot its bell. THEN it is shut, its front a plain wall.
Sn = AT_[NOW]
Sn.sector(rect(-464, -720, -240, -656), ceil=112, light=170, color=ten.ROSE, wall="AJSAFE")
Sn.sector(rect(-464, -848, -240, -720), ceil=112, light=170, color=ten.ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(Sn, (-448, -640), (-384, -640), (0, -1), 0, KIOSK, line_id=305)
ajarmap.unbolt(Sn, (-464, -720), (-240, -720), KIOSK)
bars(Sn, (-320, -640), (-256, -640), (0, -1), 0, near=Q("AJQK"), far=Q("AJSAFE"))
Sn.cut((-320, -848), (-256, -848))
Sn.line((-320, -848), (-256, -848), special=11, args=(KIOSK, 32), impact=True, mid="AJTARG", exact=True)

# =================================================================================================================
# THE NIGHT ROOM, over the shelter: the same plan at both times
# =================================================================================================================
# THEN (PLAN.md, "MAP22: BLUE's ambush with an arch-vile; the way out is gated"): ajarmap.way_home's room, but gated:
# a wall 16 thick across it at GATE_X, a bolted door in it on the runner (the bolt on its east side) and a barred
# window either side. West of it BLUE's far side THEN and the stair's landing; east of it the brass frame HOME
# (BLUE's alone) and, in the south wall, frame 125 (the clocked door's alone). The only way of arriving east of
# the wall is the clocked door in 125, and its unbolt line (GATE_LINE_Y) is crossed on coming out of that frame.
# The way in from below: the shelter's brass door (keys 3 and 4) and a stair up to it.
# NOW: one room, the wall down (a stub of it at the north wall and at the south wall); BLUE's far side NOW, frame
# 105 (twin of 125), Doom's stone where HOME is THEN. MAP10's hole down into the shelter is shut: the short passage
# north of the room ends in Doom's stone (with the hole open the level could be lost: puzzle22.py).
St = AT_[THEN]
GATE_X = NX + 192                       # the wall's west face; its east face is GATE_X + 16, the east part 112 wide
GATE_TAG, GATE_LINE = 2202, 311         # the bolted door's sector tag; its line on the bolt side (USE opens it)
GATE_LINE_Y = NY + 32                   # the unbolt line across the east part, just north of frame 125's mouth
CLOCK5 = ((NX + 216, NY), (NX + 280, NY))  # frames 105 / 125: their mouth in the south wall, 8 from the gate's wall
WALL_STUB = 64                          # NOW: the length of each stub of the wall left standing
NIGHT_ROOM = dict(ceil=LINE + 160, light=150, wall="AJXW2", ftex="AJXG2", rug="AJXR2", ctex="AJXC2", floor=LINE)
RUNNER_ROW = (NY + 96, NY + 160)
on_runner = lambda ys: (lambda i, j: (ys[j], ys[j + 1]) == RUNNER_ROW)
WEST_YS = [NY, NY + 96, NY + 160, NY + 256]
EAST_YS = [NY, GATE_LINE_Y, NY + 96, NY + 160, NY + 256]
ajarmap.room(St, [NX, GATE_X], WEST_YS, on_runner(WEST_YS), **NIGHT_ROOM)
ajarmap.room(St, [GATE_X + 16, NX + 320], EAST_YS, on_runner(EAST_YS), **NIGHT_ROOM)
ajarmap.bolted(St, (GATE_X, NY + 96), (GATE_X, NY + 160), (1, 0), LINE, GATE_TAG, line_id=GATE_LINE)
ajarmap.unbolt(St, (GATE_X + 16, GATE_LINE_Y), (NX + 320, GATE_LINE_Y), GATE_TAG)
for y in (NY + 16, NY + 176):                       # the barred windows, 16 of wall either side of each
    bars(St, (GATE_X, y + 64), (GATE_X, y), (1, 0), LINE, near="AJXW2", far="AJXW2")
ajarmap.recess(St, (NX, NY + 96), (NX, NY + 160), (-1, 0), LINE, far_id(BLUE) + THEN_ID, HOME, far_colour=BLUE)
ajarmap.recess(St, (NX + 320, NY + 96), (NX + 320, NY + 160), (1, 0), LINE, HOME, far_id(BLUE) + THEN_ID,
               trim=(f"AJXA{BLUE}", f"AJXF{BLUE}"), home=far_id(BLUE) + THEN_ID, only=True)
for xx in (NX, NX + 320):
    St.line((xx, NY + 96), (xx, NY + 160), id=ajarmap.HOME_MOUTH)
# (the candelabra of way_home, those of the east part moved clear of frame 125's mouth)
things(St, CANDELABRA, (NX + 32, NY + 48), (NX + 32, NY + 208), (NX + 296, NY + 24), (NX + 296, NY + 232))
# NOW
NOW_XS = [NX, GATE_X, GATE_X + 16, NX + 320]
NOW_YS = [NY, NY + WALL_STUB, NY + 96, NY + 160, NY + 256 - WALL_STUB, NY + 256]
for i, (x1, x2) in enumerate(zip(NOW_XS, NOW_XS[1:])):
    ys = NOW_YS if i != 1 else NOW_YS[1:-1]         # the wall's line: its two stubs stand, the middle is open
    ajarmap.room(Sn, [x1, x2], ys, on_runner(ys), **NIGHT_ROOM)
ajarmap.recess(Sn, (NX, NY + 96), (NX, NY + 160), (-1, 0), LINE, far_id(BLUE), far_id(BLUE) + THEN_ID, far_colour=BLUE)
Sn.cut((NX + 320, NY + 96), (NX + 320, NY + 160))
Sn.line((NX + 320, NY + 96), (NX + 320, NY + 160), mid=STONE)
things(Sn, CANDELABRA, (NX + 32, NY + 48), (NX + 32, NY + 208), (NX + 296, NY + 24), (NX + 296, NY + 232))
t.clock_frame(*CLOCK5, (0, -1), 105, floor=LINE, when=(NOW, THEN))
for c in t.copies:                                  # over frames 105 / 125, the room's wall
    over(AT_[c.when], *CLOCK5, "AJXW2")
# the passage north of the room NOW: where MAP10 has its hole down into the shelter, Doom's stone
PASSAGE_END = -240
Sn.sector(rect(384, NY + 256, 448, PASSAGE_END), floor=LINE, ceil=LINE + 96, light=150, wall="AJBRICK",
          ftex="AJTRIMF", ctex="AJTRIMF")
over(Sn, (384, -304), (448, -304), "AJXW2")
Sn.line((384, PASSAGE_END), (448, PASSAGE_END), mid=STONE, dontpegbottom=True)
# THEN: the brass door in the shelter's south wall, where MAP10 has its brass frame; behind it a stair up by
# LINE in four steps of 16, and a landing under the night room's north wall
PASSAGE = dict(light=170, wall="AJXW2", ftex="AJXG2", ctex="AJXC2")
ajarmap.stairs(St, (288, -224), (448, -224), (0, -1), 0, LINE, steps=4, depth=16, ceil=LINE + 96, **PASSAGE)
St.sector(rect(288, NY + 256, 448, -288), floor=LINE, ceil=LINE + 96, **PASSAGE)
ajarmap.roomdoor(St, (288, -208), (352, -208), (0, -1), 0, keys="34", skin="AJ22D", line_id=310)   # (the rooms first)
over(St, (304, NY + 256), (448, NY + 256), "AJXW2")
for c in t.copies:                                       # over BLUE's far side (both) and HOME (THEN), the room's wall
    over(AT_[c.when], (NX, NY + 96), (NX, NY + 160), "AJXW2")
over(St, (NX + 320, NY + 96), (NX + 320, NY + 160), "AJXW2")

# =================================================================================================================
# THE DEPOT (YELLOW's far side), beyond the lane, at both times
# =================================================================================================================
FITTERS = (320, 944, 512, 992)          # THEN: the fitters' bench along the north wall, east of the clocked door
PLATE4 = ((192, 992), (320, 992))       # ... the fitters' tag over the clocked door: FOUND IN THE YARD. NOT OURS.
CACHE = (-496, 992, -400, 1056)         # NOW: the cache in the far corner (MAP10's key 2), a secret
for c in t.copies:
    S = AT_[c.when]
    buses = dict(ftex="AJQRF" if ten.LOOK else "AJSTEEL", side=f"AJ{LIVERY[c.when]}US", floor=D + ajarmap.BUS_H)
    feats = [((-448, 384 + DY, -128, 512 + DY), buses), ((128, 448 + DY, 448, 576 + DY), buses),
             ((-64, 576 + DY, 64, 640 + DY), dict(WOOD, floor=D + 48)),
             ((-64, 192 + DY, 64, 256 + DY), dict(low(D), lift=D + 128 - 512))]       # over YELLOW's far side
    if c.then:
        feats.append((FITTERS, dict(ftex="AJWOOD", side="AJWOOD", floor=D + 40)))
    ajarmap.fitted(S, (-512, 192 + DY, 512, 640 + DY), feats, floor=D, light=DAY if c.then else NIGHT,
                   ftex="AJQOC" if ten.LOOK else "AJSTEEL", **OPEN)
    # the gate: out to the lane behind the bus, a step down, and never in
    ajarmap.opening(S, (432, 192 + DY), (496, 192 + DY), (0, -1), D, thick=96)
    for a, b in (((-32, 192 + DY), (32, 192 + DY)), ((432, 192 + DY), (448, 192 + DY)), ((448, 192 + DY), (496, 192 + DY))):
        over(S, a, b, BRICK)
    S.line((432, 448), (496, 448), lower=BRICK, upper="AJTRIM")
    things(S, LAMP, (-488, 968), (-440, 568))
    if c.then:
        S.cut(*PLATE4)
        S.line(*PLATE4, mid="AJ22P4", dontpegbottom=True, exact=True)
        things(S, TECHLAMP, (472, 968))
    else:
        S.sector(rect(*CACHE), floor=D, ceil=D + 112, light=120, wall=BRICK, ftex="AJQOC" if ten.LOOK else "AJSTEEL",
                 ctex="AJTRIMF", special=1024)
t.far((-32, 192 + DY), (32, 192 + DY), (0, -1), YELLOW, floor=D)

# =================================================================================================================
# THE THEATRE (RED's far side), both times: MAP03's foyer, house and the rooms behind; the stage door's ledge
# and the pit, whose doorway is door 8 of the bus at the same time
# =================================================================================================================
THEATRE = {}
for c in t.copies:
    S, ft, fs = AT_[c.when], len(m.things), len(m.sectors)
    places = ajarmap.excerpt(m, map_hinges3.m, (-200, 1352), c.dx, TY + c.dy, nailed=c.now,
                             without=[(224 + c.dx, 912 + TY + c.dy, 672 + c.dx, 1008 + TY + c.dy),
                                      (224 + c.dx, 896 + TY + c.dy, 288 + c.dx, 912 + TY + c.dy)])
    THEATRE[c.when] = [to_now(c, p) for p in places]
    if c.then:
        peaceful(ft, fs)
    else:
        MAP03_NOW = (ft, len(m.things))             # MAP03's monsters and pick-ups, as MAP10 has them
    ajarmap.opening(S, (224, 896 + TY), (288, 896 + TY), (0, 1), 0)              # the stage door
    ajarmap.fitted(S, (224, 912 + TY, 608, 1008 + TY), [
        ((224, 912 + TY, 288, 1008 + TY), dict(floor=0, ftex="AJBOARD", side="AJWOOD")),     # the ledge
    ], floor=-48, ceil=128, light=160 + (DAYLIGHT if c.then else 0), **BACKSTAGE)
    for a, b in (((288, 912 + TY), (608, 912 + TY)), ((608, 912 + TY), (608, 1008 + TY)), ((224, 1008 + TY), (608, 1008 + TY))):
        S.line(a, b, lower=BACKSTAGE["wall"])
    BAR, GREENROOM, HOUSE, CIRCLE = "AJ3B1", "AJ3XG", "AJ3H1D", "AJ3H1B"
    for a, b, tex in (((608, 928 + TY), (608, 992 + TY), BACKSTAGE["wall"]),
                      ((224, 912 + TY), (288, 912 + TY), BACKSTAGE["wall"]),
                      ((224, 896 + TY), (288, 896 + TY), STALLS["wall"]),
                      ((672, 928 + TY), (672, 976 + TY), CIRCLE), ((672, 976 + TY), (672, 992 + TY), CIRCLE),
                      ((-256, 1024 + TY), (-192, 1024 + TY), FOYER["wall"]),
                      ((240, 1488 + TY), (240, 1552 + TY), FOYER["wall"]), ((256, 1488 + TY), (256, 1552 + TY), BAR),
                      ((2112, 992 + TY), (2112, 1056 + TY), BACKSTAGE["wall"]), ((2128, 992 + TY), (2128, 1056 + TY), GREENROOM),
                      ((512, -96 + TY), (640, -96 + TY), HOUSE)):
        over(S, a, b, tex)
    # (the pit's doorway is door 2 of the 20, at the other stop: below)
assert THEATRE[NOW][0] == THEATRE[THEN][0]
_a, _b, _out, _floor = THEATRE[NOW][0]
t.far(_a, _b, _out, RED, floor=_floor)                                          # RED's far side in the foyer


def daylight(first_sector):
    """THEN: this level's own rooms (the museum, the observatory) since this index are lit by day, as the
    excerpts are (peaceful)."""
    for s in m.sectors[first_sector:]:
        s["light"] = min(255, s["light"] + DAYLIGHT)


# =================================================================================================================
# THE OTHER STOP (PLAN.md, "MAP22 bigger"): MAP10's second square at both times, the 20 standing at it: new THEN
# (livery F, gfx_dayreturn), MAP10's old one NOW (C). Its doors, the same at both times: 1 is door 8 of the 10, 2
# the pit under the theatre's stage door, 3 frames 106 / 126 (twins, any door), 4 (in its back) the observatory
# =================================================================================================================
BY = 3168                                           # the 20's south face (MAP10's)
LIVERY20 = {NOW: "C", THEN: "F"}
MOUTHS20 = {}                                       # (copy, door 1..4 of the 20): its mouth
for c in t.copies:
    S, L = AT_[c.when], (DAY if c.then else NIGHT)
    for box, feats in (((-640, BY - 288, 640, BY - 48), [((-192, BY - 208, -64, BY - 176), SEAT),
                                                         ((64, BY - 208, 192, BY - 176), SEAT)]),
                       ((-640, BY - 48, -400, BY + 192), []), ((400, BY - 48, 640, BY + 192), []),
                       ((-640, BY + 192, 640, BY + 432), [])):
        ajarmap.fitted(S, box, feats, floor=0, light=L, **(PAVE if ten.LOOK else dict(ftex="AJ5P1")), **SQUARE)
    STOP2 = STOP if ten.LOOK else dict(ftex="AJ5P1")
    south2 = ajarmap.bus(S, -400, BY, face=1, first=1, slots=(0, 2, 4), free=True, livery=LIVERY20[c.when],
                         light=L + 20, **STOP2)
    north2 = ajarmap.bus(S, -400, BY + 144, face=-1, first=4, slots=(3,), free=True, livery=LIVERY20[c.when],
                         light=L + 20, **STOP2)
    pieces(S, BY - 288, (-320, 384), "x", Q("AJQFA"))
    pieces(S, BY + 432, (128,), "x", Q("AJQFB"))
    pieces(S, BY + 432, (-512,), "x", Q("AJQFA"))
    ajarmap.bus_ends(S, -400, BY, livery=LIVERY20[c.when])
    for n, mouth in enumerate(south2 + north2):
        MOUTHS20[c.when, n + 1] = mouth
    # door 8 of the 10 is door 1 of the 20 (doorways 3 NOW, 4 THEN); door 2 of the 20 is the pit's doorway under the
    # theatre's stage door (5 NOW, 6 THEN): whoever drops off the ledge comes out here
    ajarmap.doorway(S, 3 if c.now else 4, *MOUTHS[c.when, 8], (0, -1), 0, *south2[0], (0, 1), 0)
    ajarmap.doorway(S, 5 if c.now else 6, *south2[1], (0, 1), 0, (608, 928 + TY), (608, 992 + TY), (1, 0), -48)
    things(S, LAMP, (-616, BY - 264), (616, BY - 264), (-616, BY + 408), (616, BY + 408))
t.frame(*MOUTHS20[NOW, 3], (0, 1), 106)                                         # 3: frames 106 / 126, any door

# =================================================================================================================
# THE OBSERVATORY (door 4 of the 20), at both times: MAP10's library and dome, dressed and lit as MAP07's. Not
# MAP10's: no frame in the dome (MAP10's 116 is plain wall), and the top of the stair out is a plain opening 64
# wide, not a squeeze, so that a door carried in can be carried out (puzzle22.py: with MAP10's drop, squeeze and a
# frame RED can be shut in for good). The dome's door opens with key 2 at both times. THEN lit by day
# =================================================================================================================
seven = ten.seven
m.align |= seven.m.align | ten.six.m.align
LIB, DOME, LOW7 = seven.LIB, seven.DOME, seven.low()
PASSAGE7 = dict(wall=seven.LOWW or LIB["wall"], ftex=LIB["ftex"], ctex=LOW7["ctex"])
TORCHES = [(1616, 1100), (2096, 1100), (1616, 1290), (2096, 1290)]
LBOX = (1600, 1000, 2112, 1384)
PIT7 = -96                                          # the dome's sunk floor
LEDGE = (1792, 1400, 1920, 1464)
DOME_DOOR = {NOW: 302, THEN: 322}                   # its mouth's line id (the library's side), for the tests
STAIR_TOP = ((1408, 1700), (1472, 1700))            # the opening at the top of the dome's stair
KEY3 = (2000, 1736)                                 # NOW, on the sunk floor, near where MAP10 leans BLUE
for c in t.copies:
    S, fs = AT_[c.when], len(m.sectors)
    ajarmap.shaped(S, LBOX, ten.pools(TORCHES, seven.DARK) + [
        ((1824, 1000, 1888, 1384), seven.RUN),
        ((1632, 1160, 1760, 1224), dict(seven.BOOKS, floor=96)),                         # stacks
        ((1952, 1160, 2080, 1224), dict(seven.BOOKS, floor=96)),
        ((1792, 1000, 1920, 1064), LOW7),                                                # before the bus's door
        ((1792, 1320, 1920, 1384), LOW7),                                                # before the dome's
        ((1600, 1320, 1664, 1384), LOW7),                                                # before the way round
    ], floor=0, ceil=320, light=seven.DARK, **LIB)
    porch(S, (1792, 1000, 1920, 1064), LIB["wall"] if seven.LOOK else None, "NEW")
    porch(S, (1792, 1320, 1920, 1384), LIB["wall"] if seven.LOOK else None, "SEW")
    porch(S, (1600, 1320, 1664, 1384), LIB["wall"] if seven.LOOK else None, "SE")
    # door 4 of the 20: doorways 7 NOW, 8 THEN
    ajarmap.doorway(S, 7 if c.now else 8, *MOUTHS20[c.when, 4], (0, -1), 0, (1824, 1000), (1888, 1000), (0, -1), 0)
    ajarmap.shaped(S, (1664, 1400, 2048, 1784), ten.pools([(1688, 1424), (2024, 1424)], seven.DARK) + [
        (LEDGE, dict(LOW7, floor=0, **seven.WOOD)),                                      # the ledge inside the door
        ((1808, 1544, 1904, 1640), dict(seven.PIER, floor=PIT7 + 64,
                                        light=min(255, seven.DARK + 85) if seven.DIM else seven.DARK)),   # the pier
    ], floor=PIT7, ceil=448, light=seven.DARK, **DOME)
    porch(S, LEDGE, DOME["wall"] if seven.LOOK else None, "NEW")
    ajarmap.roomdoor(S, (1824, 1384), (1888, 1384), (0, 1), 0, keys="2", line_id=DOME_DOOR[c.when])
    if seven.LOOK:                                                               # its two faces, each under a porch
        S.line((1824, 1384), (1888, 1384), upper=seven._face("D", "A", (1824, 1384), (0, 1), "2"))
        S.line((1824, 1400), (1888, 1400), upper=seven._face("D", "A", (1824, 1384), (0, -1), "2"))
    ajarmap.stairs(S, (1664, 1700), (1664, 1764), (-1, 0), PIT7, 96, steps=6, ceil=160, light=150,
                   lift=160 - 448, **DOME)              # its walls laid as the dome's are, from the dome's ceiling
    over(S, (1664, 1700), (1664, 1764), DOME["wall"] if seven.LOOK else None)
    S.sector(rect(1408, 1700, 1472, 1764), floor=0, ceil=128, light=150, **PASSAGE7)
    ajarmap.opening(S, *STAIR_TOP, (0, -1), 0)                                   # (MAP10: a squeeze)
    S.sector(rect(1408, 1320, 1472, 1684), floor=0, ceil=128, light=150, **PASSAGE7)
    S.sector(rect(1472, 1320, 1584, 1384), floor=0, ceil=128, light=150, **PASSAGE7)
    ajarmap.opening(S, (1600, 1320), (1600, 1384), (-1, 0), 0)
    for a, b, tex in (((1824, 1000), (1888, 1000), seven.LOWW),                  # door 4 of the 20, in the library
                      ((1600, 1320), (1600, 1338), seven.LOWW), ((1600, 1338), (1600, 1370), seven.LOWW),
                      ((1600, 1370), (1600, 1384), seven.LOWW),                  # the way round, from the library
                      ((1584, 1320), (1584, 1384), PASSAGE7["wall"]),            # ... and from the passage
                      ((1408, 1684), (1472, 1684), PASSAGE7["wall"]),            # the opening at the stair's top
                      ((1408, 1700), (1472, 1700), PASSAGE7["wall"]),
                      ((1472, 1700), (1472, 1764), DOME["wall"] if seven.LOOK else None)):   # the stair's top
        over(S, a, b, tex)
    things(S, 46, *TORCHES)                                                      # the library's torches, as MAP07's
    things(S, 20021, (1856, 1592), angle=90)                                     # the telescope on its pier
    things(S, TECHLAMP, (1688, 1424), (2024, 1424))
    if c.then:
        daylight(fs)

# =================================================================================================================
# THE MUSEUM, on the square, at both times: MAP10's great hall, gallery and cellar, dressed as MAP06's. Its door
# on the square is a real door with the plate 1 and opens with key 1, from either side (it was a face with a CLOSED
# card). The cellar as MAP10's (the hole in the hall's floor to drop through, the stair up to the gallery), but no
# frame in it (MAP10's 114 is plain wall) and a plain opening, 64 wide, at the top of its stair (MAP10: a
# squeeze). PINK's store off the gallery NOW: a secret behind bars, opened by shooting its bell (a megasphere in
# it); THEN shut, plain wall, as the kiosk is
# =================================================================================================================
six, T6 = ten.six, ten.T6
HK, LOW6 = T6("HK"), six.LOW
MUSEUM_DOOR = {NOW: 301, THEN: 321}                 # its mouth's line id (the square's side), for the tests
CELL = dict(floor=-128, ceil=0, light=140, wall=six.CELLW, ftex="AJPIT")
STORE = ten.STORE
for c in t.copies:
    S, fs = AT_[c.when], len(m.sectors)
    ajarmap.fitted(S, (-1168, -640, -528, -128), [
        ((-592, -432, -528, -304), LOW6),                                        # inside its door
        ((-1168, -464, -1104, -336), LOW6),                                      # before the way down
        ((-932, -192, -804, -128), LOW6),                                        # before the gallery
        ((-960, -480, -832, -352), six.CASE),                                    # a case
        ((-720, -608, -592, -576), six.SEAT),
    ], floor=0, ceil=384, light=190, **six.HALL)
    porch(S, (-592, -432, -528, -304), HK, "NSW")
    porch(S, (-1168, -464, -1104, -336), HK, "NSE")
    porch(S, (-932, -192, -804, -128), HK, "SEW")
    pieces(S, -128, (-1088,), "x", T6("H", "1"))                                 # its two big pictures
    pieces(S, -640, (-896,), "x", T6("H", "2"))
    ajarmap.roomdoor(S, (-512, -400), (-512, -336), (-1, 0), 0, keys="1", line_id=MUSEUM_DOOR[c.when])
    if ten.LOOK:
        S.line((-512, -400), (-512, -336), upper="AJQMD1")                       # its face on the square: the plate 1
    if six.LOOK:
        S.line((-528, -400), (-528, -336), upper=T6("D") + "P")                  # ... and inside, under the hall's porch
    # the cellar: dropped into through the hole in the hall's floor, left by its stair up to the gallery
    ajarmap.fitted(S, (-1600, -560, -1184, -112), [
        ((-1440, -400, -1344, -304), dict(six.CRATE, floor=-128 + 48)),          # crates
        ((-1280, -208, -1216, -144), dict(six.CRATE, floor=-128 + 48)),
        ((-1248, -464, -1184, -336), dict(ceil=128, wall=six.STAIR["wall"], ctex=six.STAIR.get("ctex", "AJBOARD"))),
    ], **CELL)
    ajarmap.opening(S, (-1168, -432), (-1168, -368), (-1, 0), 0)
    over(S, (-1168, -432), (-1168, -368), six.LOWW)
    ajarmap.stairs(S, (-1560, -112), (-1496, -112), (0, 1), -128, 128, ceil=128, light=140, **six.STAIR)
    S.sector(rect(-1560, 144, -1496, 208), floor=0, ceil=128, light=150, **six.LANDING)
    ajarmap.opening(S, (-1496, 144), (-1496, 208), (1, 0), 0)                    # (MAP10: a squeeze)
    over(S, (-1496, 144), (-1496, 208), six.CELLW if six.LOOK else None)
    over(S, (-1480, 144), (-1480, 208), six.WA.get("wall"))
    # the gallery
    ajarmap.fitted(S, (-1480, -96, -720, 400), [
        ((-1320, 64, -1192, 192), six.CASE),                                     # cases
        ((-1000, 64, -872, 192), six.CASE),
        ((-784, 256, -720, 384), six.SEAT),
    ], floor=0, ceil=160, light=175, **six.WA)
    for i, (fixed, start) in enumerate(((400, -1408), (400, -960), (400, -832), (-96, -1344), (-96, -1152), (-96, -1024))):
        pieces(S, fixed, (start,), "x", T6("WA", "123"[i % 3]))                  # its pictures
    ajarmap.opening(S, (-900, -128), (-836, -128), (0, 1), 0, thick=32)
    over(S, (-900, -128), (-836, -128), six.LOWW)
    over(S, (-900, -96), (-836, -96), six.WA.get("wall"))
    for a, b in (((-1184, -432), (-1184, -400)), ((-1184, -400), (-1184, -368))):  # the hall, from the cellar's bay
        S.line(a, b, lower=six.STAIR["wall"], upper=six.STAIR["wall"])
    over(S, (-1560, -112), (-1496, -112), six.STAIR["wall"])                     # the foot of the cellar's stairs
    things(S, TECHLAMP, (-552, -616), (-1144, -616))
    if c.now:
        # PINK's store (secret), seen through bars: shoot its bell. A megasphere in it
        S.sector(rect(-1320, 416, -1000, 480), ceil=112, light=150, color=ten.ROSE, wall="AJSAFE")
        S.sector(rect(-1320, 480, -1000, 640), ceil=112, light=150, color=ten.ROSE, wall="AJSAFE", special=1024)
        ajarmap.bolted(S, (-1260, 400), (-1196, 400), (0, 1), 0, STORE, line_id=306)
        if six.LOOK:
            S.line((-1260, 400), (-1196, 400), upper=f"AJ6Z{six.LOOK}G")         # its face in the gallery's wall
        ajarmap.unbolt(S, (-1320, 480), (-1000, 480), STORE)
        bars(S, (-1100, 400), (-1036, 400), (0, 1), 0, near=six.WA.get("wall"), far="AJSAFE" if six.LOOK else None)
        S.cut((-1100, 640), (-1036, 640))
        S.line((-1100, 640), (-1036, 640), special=11, args=(STORE, 32), impact=True, mid="AJTARG", exact=True)
        things(S, CANDLE, (-1020, 500), (-1020, 620))
    else:
        daylight(fs)

# =================================================================================================================
# THE HOTEL (line 1) AND THE STATION (line 5): THEN only, as MAP10 lifts them out, at peace
# =================================================================================================================
ft, fs = len(m.things), len(m.sectors)
# (nothing is nailed up THEN: a door that an excerpt leaves behind is its own face, shut; the hotel's front doors
# are whole, with the day in their glass)
hotel = [to_now(t.then, p) for p in ajarmap.excerpt(m, map_hinges2.m, (256, 96), HX + t.then.dx, t.then.dy,
                                                    nailed=False)]
station = [to_now(t.then, p) for p in ajarmap.excerpt(m, map_hinges5.m, (256, 64), SX + t.then.dx, t.then.dy,
                                                      nailed=False)]
peaceful(ft, fs)
for p in m.lineprops.values():
    if map_hinges2.LOOK and p.get("mid") == f"AJ2X{map_hinges2.LOOK}":
        p["mid"] = f"AJ2X{map_hinges2.LOOK}N"
m.things = [th for th in m.things if (th["x"], th["y"]) != (HX - 16 + t.then.dx, 272 + t.then.dy)]   # (MAP10's candle)
ajarmap.doorway(St, 1, *MOUTHS[THEN, 1], (0, 1), 0, *hotel[0])
ajarmap.doorway(St, 2, *MOUTHS[THEN, 5], (0, 1), 0, *station[0])
for a, b, tex in (((HX + 224, 0), (HX + 288, 0), ten.HOTEL["wall"]),
                  ((HX - 352, -64), (HX - 352, 0), ten.HROOM["wall"]), ((HX - 368, -64), (HX - 368, 0), "AJ2T1"),
                  ((HX - 1696, 848), (HX - 1632, 848), "AJ2KW"),
                  ((SX + 352, 0), (SX + 416, 0), "AJ5A1"),
                  ((SX + 1088, 1280), (SX + 1152, 1280), "AJ5A1")):
    over(St, a, b, tex)


# --- walls that carry on (MAP10's rules 2 and 3, map_hinges10.py) ----------------------------------------------
def carried(ld, sides, a, b, si, other, given):
    if other is None or given["mid"] not in (None, "AJWIN"):
        return
    for part, flag, shows in (("top", "dontpegtop", lambda s, o: s["ceil"] > o["ceil"]),
                              ("bottom", "dontpegbottom", lambda s, o: o["floor"] > s["floor"])):
        seen = [(k, m.sectors[x]) for k, x, y in (("sidefront", si, other), ("sideback", other, si))
                if shows(m.sectors[x], m.sectors[y])]
        if ld.get(flag) or not seen or any(sides[ld[k]].get("texture" + part) != s["wall"] for k, s in seen):
            continue
        ld[flag] = True
        for k, s in seen:
            if s["lift"]:
                sides[ld[k]]["offsety_" + part] = float(-s["lift"])


m.line_hook = carried
BOXES = None


def sector_index():
    """The sectors by cells of 256, for sector_at."""
    global BOXES
    BOXES = {}
    for i, poly in enumerate(m.polys):
        xs, ys = [v[0] for v in poly], [v[1] for v in poly]
        for cx in range(int(min(xs) // 256), int(max(xs) // 256) + 1):
            for cy in range(int(min(ys) // 256), int(max(ys) // 256) + 1):
                BOXES.setdefault((cx, cy), []).append(i)


def sector_at(x, y):
    if BOXES is None:
        sector_index()
    for i in BOXES.get((int(x // 256), int(y // 256)), ()):
        poly, hit = m.polys[i], False
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                hit = not hit
        if hit:
            return m.sectors[i]
    return None


def laid_from(low_, room):
    low_["lift"] = low_["ceil"] - (room["ceil"] - room["lift"])


for key, p in list(m.lineprops.items()):            # the hotel's windows' reveals (MAP02's ajarmap.window)
    if p.get("mid") != "AJWIN" or p.get("upper") or p.get("dontpegtop"):
        continue
    (ax, ay), (bx, by) = sorted(key)
    mx, my, n = (ax + bx) / 2, (ay + by) / 2, ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    ux, uy = (by - ay) / n, (ax - bx) / n
    for s in (1, -1):
        sill, room = sector_at(mx + s * ux * 4, my + s * uy * 4), sector_at(mx - s * ux * 4, my - s * uy * 4)
        if sill and room and sill["ftex"] == "AJTRIMF" and sill["ceil"] - sill["floor"] == 56:
            laid_from(sill, room)
            laid_from(sector_at(mx + s * ux * 10, my + s * uy * 10), room)
laid_from(sector_at(HX + 1800 + t.then.dx, 224 + t.then.dy), sector_at(HX + 1700 + t.then.dx, 224 + t.then.dy))

# =================================================================================================================
# DOORS
# =================================================================================================================
m.thing(-64 + t.then.dx, -592 + t.then.dy, 1, angle=90)                         # the start: where MAP10 starts, THEN
ajarmap.door(m, RED, *St.P((-192, 8)), frame=101 + THEN_ID)                    # RED hung in door 2 THEN
ajarmap.door(m, YELLOW, *St.P((SX + 1700, 1250)), angle=180)                   # on the station's far platform THEN
ajarmap.door(m, BLUE, 600, 1450 + TY, angle=180)                               # in the rooms behind the foyer NOW
t.clocked(256, 966, 270, when=THEN)                                            # the fitters' corner THEN, under the plate

# =================================================================================================================
# THE SKY: THEN by day. The map's own sky (mapinfo sky1) is MAP10's NOW; every THEN sector open to the sky is
# tagged SKY_TAG, and a sky transfer (Static_Init(tag, 255): the line's upper texture) gives them AJ22SKY.
# =================================================================================================================
THEN_HALF = AT[1] + OFF[1] / 2
for poly, s in zip(m.polys, m.sectors):
    if "F_SKY1" not in (s["ctex"], s["ftex"]) or min(v[1] for v in poly) < THEN_HALF:
        continue
    if s["id"]:
        ids = s["raw"].get("moreids", "")
        s["raw"] = dict(s["raw"], moreids=(ids + " " + str(SKY_TAG)).strip())
    else:
        s["id"] = SKY_TAG
# the transfer line: between two pieces of the square THEN that are alike (its upper is never drawn)
St.line((-256, -432), (-256, -400), special=190, args=(SKY_TAG, 255), upper="AJ22SKY")

# =================================================================================================================
# THE FIGHTS AND WHAT IS PICKED UP (PLAN.md, "Fights"). Then is quiet until the turn; then every place there gets
# its company by ambush (cause 64), each when the player next comes near it, the stop in two waves. The supplies
# are not then: they lie in the square now and in the theatre now (MAP03's own, as MAP10 has them), and in the
# depot now; then there is only the station's megasphere.
# =================================================================================================================
ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACH = 65, 69, 3003, 66, 3006, 3005, 67, 68
NEAR = 640              # a place's company then comes when the player is this near and in sight

AREAS = {   # name: the box things stand in, in NOW's coordinates, and at which time
    # the square (at both times): south of the bus, its ends, the lane behind it
    "sqS": ((-440, -300, 190, -60), NOW), "sqE": ((410, -40, 630, 180), NOW), "sqW": ((-630, -40, -410, 180), NOW),
    "lane": ((-630, 196, 410, 300), NOW),
    "sqST": ((-440, -300, 190, -60), THEN), "sqET": ((410, -40, 630, 180), THEN), "sqWT": ((-630, -40, -410, 180), THEN),
    "laneT": ((-630, 196, 410, 300), THEN),
    "depotN": ((-500, 560, 500, 980), NOW), "depotT": ((-500, 560, 500, 940), THEN),
    # the theatre: the stage, the house, the foyer
    "stageT": ((1160, -4470, 1780, -3850), THEN), "houseT": ((0, -4410, 1020, -3655), THEN),
    "foyerT": ((-470, -3450, 90, -3165), THEN),
    "foyerN": ((-470, -3450, 90, -3165), NOW), "behindN": ((260, -2988, 475, -2868), NOW),
    # the hotel: the lobby, the long hall, the kitchen
    "lobby": ((HX - 10, 16, HX + 500, 420), THEN), "hall": ((HX - 1400, 165, HX - 10, 285), THEN),
    "kitchen": ((HX - 1870, 565, HX - 1415, 810), THEN),
    # the station: the far platform, the tracks, the concourse
    "farplat": ((SX + 530, 1030, SX + 1595, 1180), THEN), "tracks": ((SX + 520, 520, SX + 2040, 810), THEN),
    "conc": ((SX + 580, 20, SX + 795, 172), THEN),
    # the night room then, west of the gate
    "gateW": ((NX + 24, NY + 24, GATE_X - 24, NY + 232), THEN),
}
for _w, _s in ((NOW, ""), (THEN, "T")):     # the places of "MAP22 bigger", at both times
    AREAS.update({
        # the other stop: south of the 20, its two ends, the lane behind it
        "st2S" + _s: ((-630, BY - 280, 630, BY - 60), _w), "st2E" + _s: ((410, BY - 40, 630, BY + 180), _w),
        "st2W" + _s: ((-630, BY - 40, -410, BY + 180), _w), "st2B" + _s: ((-630, BY + 196, 630, BY + 424), _w),
        # the observatory: the library, the dome's sunk floor
        "lib" + _s: ((1608, 1008, 2104, 1376), _w), "dome" + _s: ((1672, 1472, 2040, 1776), _w),
        # the museum: the great hall, the gallery, the cellar
        "hall" + _s: ((-1160, -632, -536, -136), _w), "gallery" + _s: ((-1472, -88, -728, 392), _w),
        "cellar" + _s: ((-1592, -552, -1192, -120), _w),
    })
# mouths of frames and doorways, far sides, the doors where they lean: nothing stands there
AVOID = [(x, y + 24 * s) for x in (-320, -192, -64, 64, 192, 320) for y, s in ((0, -1), (144, 1))]
AVOID += [(320, -208), (0, 544), (256, 966), (-224, -3456), (256, -3584), (600, 1450 + TY), (590, -432),
          (SX + 1700, 1250), (SX + 384, 0), (HX + 256, 0), (-448, 1024), (640, 960 + TY),
          (NX, NY + 128), (376, NY + 256), (GATE_X, NY + 128)]       # the night room: BLUE's far side, the stair, the gate
AVOID += [(-320, BY - 24), (-64, BY - 24), (192, BY - 24), (64, BY + 168),     # the 20's doors
          (1856, 1024), (1856, 1360), (1632, 1352), (1440, 1700), (1440, 1732), (1680, 1732),   # the library's ways
          (KEY3[0], KEY3[1]),                                                  # ... key 3 on the dome's floor
          (-480, -368), (-560, -368), (-1150, -400), (-868, -150), (-868, -70),   # the museum's ways
          (-1460, 176), (-1528, -136), (-1216, -400)]
TAKEN = []
R = {CACO: 31, MANCUBUS: 48, ARACH: 64, BARON: 24, KNIGHT: 24, DEMON: 30, SPECTRE: 30, REVENANT: 20}
TALL = {CACO: 56, MANCUBUS: 64, ARACH: 64, BARON: 64, KNIGHT: 64}
PART_OF = []            # (thing index, part) for every monster and pick-up: the budget by part
PROBLEMS = []


def halton(i, b):
    f, r = 1, 0
    while i:
        f /= b
        r += f * (i % b)
        i //= b
    return r


def stands(x, y, r, tall):
    """True if a thing of radius r and height tall can stand at (x, y) (absolute): the floor under its middle, its
    corners and its sides is one floor, with room over it, and no secret's floor."""
    mid = sector_at(x, y)
    if not mid or mid.get("special") or mid["ceil"] - mid["floor"] < tall + 8:
        return False
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)):
        s = sector_at(x + dx * (r + 2), y + dy * (r + 2))
        if not s or s["floor"] != mid["floor"] or s["ceil"] - s["floor"] < tall + 8 or s.get("special"):
            return False
    return True


def spot(name, r=20, tall=56):
    """A free place for a thing of radius r in area `name` (a Halton sequence: the same every build)."""
    (x1, y1, x2, y2), when = AREAS[name]
    c = t.copies[when]
    for k in range(1, 4000):
        x = round((x1 + r + halton(k, 2) * (x2 - x1 - 2 * r)) / 8) * 8
        y = round((y1 + r + halton(k, 3) * (y2 - y1 - 2 * r)) / 8) * 8
        if not (x1 + r <= x <= x2 - r and y1 + r <= y <= y2 - r):
            continue
        if any(max(abs(x - tx), abs(y - ty)) < r + tr + 8 for tx, ty, tr, tw in TAKEN if tw == when):
            continue
        if any(math.hypot(x - ax, y - ay) < 64 + r for ax, ay in AVOID):
            continue
        px, py = c.P((x, y))
        if any(math.hypot(px - th["x"], py - th["y"]) < r + 28 for th in m.things):     # lamps, pick-ups, the others
            continue
        if not stands(px, py, r, tall):
            continue
        TAKEN.append((x, y, r, when))
        return x, y
    PROBLEMS.append(f"no room in {name}")
    return x1 + 64, y1 + 64


def mark(part, first, last=None):
    PART_OF.extend((i, part) for i in range(first, len(m.things) if last is None else last))


def put(part, name, kind, n, angle=0, **k):
    first = len(m.things)
    for _ in range(n):
        x, y = spot(name, R.get(kind, 20), TALL.get(kind, 56))
        t.copies[AREAS[name][1]].thing(x, y, kind, angle=angle, **k)
    mark(part, first)


def ambush(part, name, cause, kind, n, *, angle=0, after=0, near=0, arg=0):
    """n of `kind` at free spots of `name`, coming when `cause` is due (ajar.zs, AmbushTick)."""
    first = len(m.things)
    spots = [t.copies[AREAS[name][1]].P(spot(name, R.get(kind, 20), TALL.get(kind, 56))) for _ in range(n)]
    ajarthen.ambush(m, cause, arg, kind, *spots, angle=angle, after=after, near=near)
    mark(part, first)


def bearer(part, x, y, kind, key, angle=0, near=NEAR):
    """The turn's ambusher that carries room key `key` (map22.zs, AjarKeyBearer): there on every difficulty."""
    first = len(m.things)
    m.thing(*St.P((x, y)), ajarmap.AMBUSH_T, angle=angle, args=(TURN, kind, 0, near, key), skill=1)
    TAKEN.append((x, y, R.get(kind, 20), THEN))
    mark(part, first)


def items(part, *spec):
    """Pick-ups: (x, y, kind) in NOW's coordinates, or (x, y, kind, THEN)."""
    first = len(m.things)
    for x, y, kind, *when in spec:
        t.copies[when[0] if when else NOW].thing(x, y, kind)
    mark(part, first)


MEGA = 83
BEHIND_SUPPLIES = [(480, -2860, ROCKETBOX), (560, -2860, CELLS), (400, -3060, MEDIKIT), (480, -3060, MEDIKIT)]
mark("theatre now", *MAP03_NOW)
# --- the square now: a standing company, deaf until the turn wakes it (map22.zs); MAP10's weapons and more
items("square", (-576, -16, 2001), (576, -16, 2049), (-560, 160, 2048), (560, 160, 2049), (-400, -280, 2012),
      (160, -280, 2012), (-160, 280, 2046), (160, 280, 2046), (-576, 120, 2002), (576, 120, 2048),
      (0, -280, 2018), (-300, 280, 2049), (300, 280, 2049), (-576, 60, 82), (576, 60, 2003), (0, 280, 2049),
      (-240, -200, 2048), (80, -200, 2046), (-480, 240, 17), (600, 240, 2004), (-600, 280, 2046), (600, -30, 2049),
      (-600, -30, 2049), (-420, 120, 2049), (420, 120, 17), (-100, 240, 2046), (100, 240, 2046), (-560, 100, 2012),
      (560, 100, 2012), (-320, -120, 2011), (-160, -120, 2011), (120, -120, 2011), (420, -20, 2012), (-400, 280, 2015),
      (400, 280, 2015))
SQ = dict(id=SQUARE_TID, ambush=True)
put("square", "sqS", IMP, 4, 90, **SQ)
put("square", "sqS", SERGEANT, 3, 90, **SQ)
put("square", "sqE", CHAINGUNNER, 2, 180, **SQ)
put("square", "sqE", IMP, 2, 180, **SQ)
put("square", "sqW", KNIGHT, 2, 0, **SQ)
put("square", "sqW", SERGEANT, 2, 0, **SQ)
put("square", "lane", REVENANT, 2, 270, **SQ)
put("square", "lane", IMP, 3, 270, **SQ)
put("square", "sqS", CACO, 2, 90, **SQ)
# --- the stop then: the two waves of the turn
ambush("then", "sqST", TURN, IMP, 5, angle=90, after=3)
ambush("then", "sqET", TURN, SERGEANT, 3, angle=180, after=3)
ambush("then", "laneT", TURN, DEMON, 2, angle=270, after=3)
ambush("then", "sqWT", TURN, KNIGHT, 2, angle=0, after=30)
ambush("then", "sqST", TURN, CHAINGUNNER, 3, angle=90, after=30)
ambush("then", "laneT", TURN, REVENANT, 2, angle=270, after=30)
ambush("then", "sqST", TURN, CACO, 2, angle=90, after=30)
# --- the hotel then: key 1's baron in the lobby; MAP02's kind in the halls
bearer("then", HX + 360, 300, BARON, 1, angle=270)
ambush("then", "lobby", TURN, IMP, 4, angle=270, near=NEAR)
ambush("then", "lobby", TURN, SERGEANT, 2, angle=270, near=NEAR)
ambush("then", "hall", TURN, ZOMBIE, 3, angle=0, near=NEAR)
ambush("then", "hall", TURN, SPECTRE, 2, angle=0, near=NEAR)
ambush("then", "kitchen", TURN, KNIGHT, 1, angle=0, near=NEAR)
ambush("then", "kitchen", TURN, IMP, 2, angle=0, near=NEAR)
# --- the theatre then: key 2's baron down by the stage, in the orchestra pit where MAP10 has key 1 (no
# mancubus: the pit is 96 wide, and the stage cannot be seen from the house, so that what stands on it would hold
# back until the player is up there); the stage, the house and the foyer
bearer("then", 1104, 520 + TY, BARON, 2, angle=180, near=900)
ambush("then", "stageT", TURN, IMP, 3, angle=180, near=900)
ambush("then", "houseT", TURN, DEMON, 3, angle=90, near=NEAR)
ambush("then", "houseT", TURN, SERGEANT, 3, angle=90, near=NEAR)
ambush("then", "foyerT", TURN, IMP, 3, angle=270, near=NEAR)
ambush("then", "foyerT", TURN, CHAINGUNNER, 2, angle=270, near=NEAR)
ambush("then", "stageT", TURN, REVENANT, 1, angle=180, near=900)
# --- the station then: a big one on the platforms, not needed; a megasphere for whoever goes
items("station", (SX + 1060, 1100, MEGA, THEN))
ambush("station", "farplat", TURN, SERGEANT, 4, angle=270, near=900)
ambush("station", "farplat", TURN, CHAINGUNNER, 3, angle=270, near=900)
ambush("station", "tracks", TURN, IMP, 4, angle=90, near=900)
ambush("station", "tracks", TURN, DEMON, 2, angle=90, near=900)
ambush("station", "conc", TURN, IMP, 2, angle=90, near=NEAR)
ambush("station", "tracks", TURN, ARACH, 1, angle=90, near=900)
# --- the depot then, on coming back: MAP10's mix
ambush("then", "depotT", TURN, IMP, 4, angle=270, near=NEAR)
ambush("then", "depotT", TURN, SERGEANT, 3, angle=270, near=NEAR)
ambush("then", "depotT", TURN, DEMON, 2, angle=270, near=NEAR)
ambush("then", "depotT", TURN, KNIGHT, 1, angle=270, near=NEAR)
# --- the last one: keys 3 and 4 both in hand (cause 65, args[4] 34), at the stop then
ambush("then", "sqST", LAST_KEYS, KNIGHT, 2, angle=90, after=1, arg=34)
ambush("then", "sqWT", LAST_KEYS, REVENANT, 2, angle=0, after=2, arg=34)
ambush("then", "sqET", LAST_KEYS, CACO, 2, angle=180, after=2, arg=34)
ambush("then", "laneT", LAST_KEYS, IMP, 3, angle=270, after=1, arg=34)
# --- the theatre now: an ambush when BLUE is taken, in the rooms behind the foyer and the foyer (PLAN.md, "MAP22:
# BLUE's ambush with an arch-vile"): the foyer's dead to raise, the rooms behind it for cover. The arch-vile is
# there on every difficulty but the easiest (skill 2 up: ajarmap.ambush's own `skill`, in its turn in the count)
items("theatre now", *BEHIND_SUPPLIES)          # for it: a box of rockets, a cell pack, two medikits
ambush("theatre now", "behindN", 10 + BLUE, IMP, 2, angle=0, after=1)
ambush("theatre now", "foyerN", 10 + BLUE, CHAINGUNNER, 2, angle=90, after=1)
ambush("theatre now", "foyerN", 10 + BLUE, KNIGHT, 2, angle=90, after=1)
_first = len(m.things)
ajarmap.ambush(m, 10 + BLUE, VILE, t.now.P(spot("foyerN", R.get(VILE, 20), TALL.get(VILE, 56))), angle=90, after=3,
               skill=2)
mark("theatre now", _first)
ambush("theatre now", "foyerN", 10 + BLUE, REVENANT, 2, angle=90, after=6)
items("theatre now", (-400, -3200, 2049), (40, -3200, 2048), (-400, -3420, 2012), (40, -3420, 2046),
      (300, -2900, 2049), (440, -2900, 17))
# --- the gate's small company: when its bolt is drawn (the player east of it, come through frame 125), in the
# west part then
ambush("then", "gateW", ajarthen.AMBUSH_BOLTS, IMP, 2, angle=0, after=1, arg=GATE_TAG)
ambush("then", "gateW", ajarthen.AMBUSH_BOLTS, REVENANT, 1, angle=0, after=1, arg=GATE_TAG)
# --- the depot now: MAP10's company and its stores
put("depot now", "depotN", IMP, 4, 270)
put("depot now", "depotN", SERGEANT, 3, 270)
put("depot now", "depotN", ZOMBIE, 3, 270)
put("depot now", "depotN", DEMON, 2, 270)
put("depot now", "depotN", CHAINGUNNER, 2, 270)
items("depot now", (-480, 580, 2049), (480, 580, 2048), (-480, 900, 2046), (480, 900, 2012), (0, 940, 2049),
      (-200, 580, 2008), (200, 580, 2007))
items("secrets", (-448, 1024, 2019), (-352, -784, 2013))       # the depot's cache; the kiosk: inside it, where MAP10 has its plasma rifle


# --- MAP22 bigger (PLAN.md, "Fights and supplies"): the other stop, the observatory, the museum. The supplies are
# now only, and each part now pays for itself; the fights then are paid for by the square now, the museum now and
# the observatory now together (the budget below). Nothing that comes at the player through hung doors is a
# cacodemon, but for the dome's, which stay in it, and the other stop's two, standing deaf in its lane


def ambush_at(part, cause, kind, when, *spots, angle=0, after=0, near=0, arg=0):
    """As ambush(), at given spots (NOW's coordinates) in copy `when`; each must be one a `kind` can stand at."""
    first, c = len(m.things), t.copies[when]
    for x, y in spots:
        if not stands(*c.P((x, y)), R.get(kind, 20), TALL.get(kind, 56)):
            PROBLEMS.append(f"no room for {kind} at {(x, y)}")
        TAKEN.append((x, y, R.get(kind, 20), when))
    ajarthen.ambush(m, cause, arg, kind, *(c.P(p) for p in spots), angle=angle, after=after, near=near)
    mark(part, first)


# the other stop now: standing, as MAP10's (not woken by the turn: it is not the square's company); bullets and
# stimpacks
items("stop2 now", (-600, BY - 120, AMMOBOX), (600, BY - 120, AMMOBOX), (-560, BY + 400, AMMOBOX),
      (560, BY + 400, AMMOBOX), (0, BY + 400, AMMOBOX), (-560, BY + 60, STIM), (560, BY + 60, STIM),
      (-240, BY - 240, STIM), (240, BY - 240, STIM), (-560, BY + 120, MEDIKIT))
put("stop2 now", "st2S", IMP, 3, 90)
put("stop2 now", "st2S", SERGEANT, 3, 90)
put("stop2 now", "st2B", KNIGHT, 1, 270)
put("stop2 now", "st2E", IMP, 1, 180)
put("stop2 now", "st2B", CACO, 2, 270, ambush=True)
# the other stop then: the turn, when the player is next there
ambush("stop2 then", "st2ST", TURN, IMP, 4, angle=90, near=NEAR)
ambush("stop2 then", "st2ET", TURN, CHAINGUNNER, 2, angle=180, near=NEAR)
ambush("stop2 then", "st2WT", TURN, CHAINGUNNER, 1, angle=0, near=NEAR)
ambush("stop2 then", "st2WT", TURN, KNIGHT, 1, angle=0, near=NEAR)
ambush("stop2 then", "st2BT", TURN, REVENANT, 1, angle=270, near=NEAR)
ambush("stop2 then", "st2BT", TURN, IMP, 1, angle=270, near=NEAR)
# the observatory now: the library standing; the dome standing (cacodemons and lost souls: it is 448 high), key 3
# on its sunk floor and a box of rockets by it; key 3 taken (cause 3), revenants on the ledge and knights at the
# top of the stair out, 2 s on
items("observatory now", (1632, 1040, CELLS), (2080, 1040, CELLS), (1700, 1340, SHELLBOX), (2032, 1340, SHELLBOX),
      (1632, 1300, MEDIKIT), (2080, 1300, MEDIKIT), (1956, 1736, ROCKETBOX), (1720, 1736, MEDIKIT),
      (1440, 1380, SHELLBOX), (1520, 1352, MEDIKIT))
ajarmap.key(m, 3, *KEY3)
put("observatory now", "lib", IMP, 4, 270)
put("observatory now", "lib", REVENANT, 2, 270)
put("observatory now", "lib", KNIGHT, 1, 270)
put("observatory now", "lib", CHAINGUNNER, 1, 270)
put("observatory now", "dome", CACO, 3, 270)
put("observatory now", "dome", SOUL, 2, 270)
ambush_at("observatory now", 3, REVENANT, NOW, (1824, 1432), (1888, 1432), angle=270, after=2)
ambush_at("observatory now", 3, KNIGHT, NOW, (1440, 1732), (1440, 1640), angle=0, after=2)
# the observatory then: the turn, when next there; nothing to find there
ambush("observatory then", "libT", TURN, IMP, 5, angle=270, near=NEAR)
ambush("observatory then", "libT", TURN, KNIGHT, 1, angle=270, near=NEAR)
ambush("observatory then", "domeT", TURN, CACO, 2, angle=270, near=NEAR)
# the museum then: the turn, when the player is next in it: the mancubus in the great hall carries key 4
MANCUBUS_AT = (-736, -280)
if not stands(*St.P(MANCUBUS_AT), R[MANCUBUS], TALL[MANCUBUS]):
    PROBLEMS.append("no room for key 4's mancubus")
bearer("museum then", *MANCUBUS_AT, MANCUBUS, 4, angle=0)
ambush("museum then", "hallT", TURN, KNIGHT, 2, angle=0, near=NEAR)
ambush("museum then", "hallT", TURN, IMP, 2, angle=0, near=NEAR)
ambush("museum then", "galleryT", TURN, IMP, 5, angle=270, near=NEAR)
ambush("museum then", "cellarT", TURN, DEMON, 4, angle=0, near=NEAR)
# the museum now: standing, MAP10's kind; a rocket launcher and its rockets, shells, medikits, armour in the
# cellar, cells in the gallery; the megasphere in PINK's store (a secret)
items("museum now", (-576, -600, LAUNCHER), (-560, -560, ROCKETBOX), (-1080, -600, ROCKETBOX), (-576, -170, SHELLBOX),
      (-1130, -170, MEDIKIT), (-560, -480, MEDIKIT), (-1560, -150, ARMOR), (-1220, -420, SHELLS),
      (-760, -60, SHELLBOX), (-1440, 360, MEDIKIT), (-1440, -40, MEDIKIT), (-1500, -480, MEDIKIT), (-1096, 240, CELLS), (-824, 360, ROCKETBOX))
items("secrets", (-1160, 560, MEGA))
put("museum now", "hall", SERGEANT, 3, 0)
put("museum now", "hall", IMP, 4, 0)
put("museum now", "hall", KNIGHT, 1, 0)
put("museum now", "cellar", SPECTRE, 3, 180)
put("museum now", "gallery", REVENANT, 2, 270)
put("museum now", "gallery", CHAINGUNNER, 1, 270)

# --- the budget, part by part: each part now pays for itself (ammunition at least 1.6 times its monsters' health
# on "Resident"); the fights then (the square's waves, the districts', the last one) are paid for by the square
# now, the museum now and the observatory now together
SKILLS = m._skills()
BUDGET = {}
for part in dict.fromkeys(p for _, p in PART_OF):
    idx = [i for i, p in PART_OF if p == part]
    for level in (3, 1):
        BUDGET[(part, level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
PAY_THEN = ("square", "museum now", "observatory now", "then", "station", "stop2 then", "observatory then",
            "museum then")
for level in (3, 1):
    idx = [i for i, p in PART_OF if p in PAY_THEN]
    BUDGET[("square, museum, observatory now and then", level)] = budget.reckon(
        [m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
for part in ("theatre now", "depot now", "stop2 now", "museum now", "observatory now",
             "square, museum, observatory now and then"):
    r = BUDGET[(part, 3)]
    assert r["dmg"] >= 1.6 * r["hp"], budget.line(part, r, 3)
MONSTERS = {lv: sum(budget.reckon(m.things, SKILLS, lv)["monsters"].values()) for lv in (1, 2, 3, 4)}
assert 200 <= MONSTERS[3] <= 250, MONSTERS
assert not PROBLEMS, PROBLEMS

PUZZLE = puzzle22.PUZZLE22

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["budget"]:
        for (part, level), r in BUDGET.items():
            print(budget.line(part, r, level))
        print("monsters by skill:", MONSTERS)
    else:
        sys.stdout.write(m.textmap())
