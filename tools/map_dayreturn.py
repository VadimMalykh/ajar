"""Act 3, level 2: "Day Return" (MAP22). PLAN.md, "MAP22 "Day Return": the
first version, as decided" and "... the first playable version"; the puzzle
is tools/puzzle22.py, the level's script src/zscript/map22.zs.

MAP10's square twice (tools/ajarthen.py, src/zscript/then.zs):
  NOW   MAP10's own, at night, at MAP10's own coordinates: the old bus, the
        kiosk (a secret), the shelter, the depot with its company, the theatre
        (MAP03's excerpt with MAP03's monsters and pick-ups), the night room
        over the shelter, whole (frame 105; its hole down into the shelter
        shut by Doom's stone). No hotel, no station: doors 1 and 5 of the old
        bus are Doom's stone.
  THEN  forty years earlier, by day, NOW + OFF (12288 north): the new bus, the
        shelter, the depot (the clocked door leans in its fitters' corner),
        the theatre, and the two places the fixed lines go, the hotel (MAP02,
        line 1) and the station (MAP05, line 5; YELLOW on its far platform),
        all as MAP10 lifts them out (ajarmap.excerpt) but with no monsters and
        no pick-ups. Behind the shelter's brass door (keys 1 and 2) a stair up
        to the night room: BLUE's far side THEN west of a gate (a bolted door,
        bolted on its east side), the brass frame HOME and frame 125 east of
        it.

The bus's doors (south face 1..6, back 7 and 8), THEN / NOW:
  1  the hotel (doorway 1)                 / Doom's stone
  2  frame 121, RED hangs in it             / frame 101
  3  GREEN's far side, shut (no GREEN)      / the same
  4  frame 124, the clocked door's alone    / frame 104, the same
  5  the station (doorway 2)                / Doom's stone
  6  frame 123, brass, any door, no twin    / MAP10's brass frame, stone in it
  7  frame 122                              / frame 102
  8  doorway 4, from the pit under the theatre's stage door / doorway 3, the same
Far sides at both times (Times.far): RED in the theatre's foyer, YELLOW in the
depot's south wall, BLUE in the night room's west end.

The turn (map22.zs): the first time the clocked door hangs in a twinned
frame. Ambush cause 64 (the turn) brings every THEN place its company, each
when the player is next there (near=); two of them carry keys (args[4]): key 1
the hotel lobby's baron, key 2 the theatre's baron in the orchestra pit. Cause 65:
both keys in hand, at the shelter. BLUE taken (cause 10 + BLUE): the theatre
now's ambush, an arch-vile with it. The gate's bolt drawn (AMBUSH_BOLTS): a
small company west of it.
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
TURN, BOTH_KEYS = 64, 65            # ambush causes (ajar.zs): the turn; keys 1 and 2 both in hand
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
    # the museum's door: shut at both times (not built). No lock plate on it: the player has keys 1 and 2 here,
    # and a plate with a 1 says that key 1 opens it. A card instead: CLOSED.
    S.cut((-512, -400), (-512, -336))
    S.line((-512, -400), (-512, -336), mid="AJQMD0" if ten.LOOK else "AJHDOR", exact=True)
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
# doors 2 and 7: twins at both times, any door; door 4: the clocked door's alone at both times
t.frame(*MOUTHS[NOW, 2], (0, 1), 101)
t.frame(*MOUTHS[NOW, 7], (0, -1), 102)
t.clock_frame(*MOUTHS[NOW, 4], (0, 1), 104, when=(NOW, THEN))
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
# The way in from below: the shelter's brass door (keys 1 and 2) and a stair up to it.
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
ajarmap.roomdoor(St, (288, -208), (352, -208), (0, -1), 0, keys="12", skin="AJ22D", line_id=310)   # (the rooms first)
over(St, (304, NY + 256), (448, NY + 256), "AJXW2")
for c in t.copies:                                       # over BLUE's far side (both) and HOME (THEN), the room's wall
    over(AT_[c.when], (NX, NY + 96), (NX, NY + 160), "AJXW2")
over(St, (NX + 320, NY + 96), (NX + 320, NY + 160), "AJXW2")

# =================================================================================================================
# THE DEPOT (YELLOW's far side), beyond the lane, at both times
# =================================================================================================================
FITTERS = (320, 944, 512, 992)          # THEN: the fitters' bench along the north wall, east of the clocked door
PLATE4 = ((192, 992), (320, 992))       # ... the plate over the clocked door: LINE 4, FROM TOMORROW
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
    # door 8 of the bus at this time: from the pit, both ways
    ajarmap.doorway(S, 3 if c.now else 4, *MOUTHS[c.when, 8], (0, -1), 0, (608, 928 + TY), (608, 992 + TY), (1, 0), -48)
assert THEATRE[NOW][0] == THEATRE[THEN][0]
_a, _b, _out, _floor = THEATRE[NOW][0]
t.far(_a, _b, _out, RED, floor=_floor)                                          # RED's far side in the foyer

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
# mouths of frames and doorways, far sides, the doors where they lean: nothing stands there
AVOID = [(x, y + 24 * s) for x in (-320, -192, -64, 64, 192, 320) for y, s in ((0, -1), (144, 1))]
AVOID += [(320, -208), (0, 544), (256, 966), (-224, -3456), (256, -3584), (600, 1450 + TY), (590, -432),
          (SX + 1700, 1250), (SX + 384, 0), (HX + 256, 0), (-448, 1024), (640, 960 + TY),
          (NX, NY + 128), (376, NY + 256), (GATE_X, NY + 128)]       # the night room: BLUE's far side, the stair, the gate
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
# --- the last one: both keys in hand, at the stop then
ambush("then", "sqST", BOTH_KEYS, KNIGHT, 2, angle=90, after=1)
ambush("then", "sqWT", BOTH_KEYS, REVENANT, 2, angle=0, after=2)
ambush("then", "sqET", BOTH_KEYS, CACO, 2, angle=180, after=2)
ambush("then", "laneT", BOTH_KEYS, IMP, 3, angle=270, after=1)
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
items("secrets", (-448, 1024, 2019), (-288, -560, 2013))       # the depot's cache, the kiosk

# --- the budget, part by part: each part's ammunition does at least 1.6 times its monsters' health ("Resident").
# The fights then are paid for by the square now, which is where the supplies are (PLAN.md)
SKILLS = m._skills()
BUDGET = {}
for part in dict.fromkeys(p for _, p in PART_OF):
    idx = [i for i, p in PART_OF if p == part]
    for level in (3, 1):
        BUDGET[(part, level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
for level in (3, 1):
    idx = [i for i, p in PART_OF if p in ("square", "then", "station")]
    BUDGET[("square and then", level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
for part in ("theatre now", "depot now", "square and then"):
    r = BUDGET[(part, 3)]
    assert r["dmg"] >= 1.6 * r["hp"], budget.line(part, r, 3)
MONSTERS = {lv: sum(budget.reckon(m.things, SKILLS, lv)["monsters"].values()) for lv in (1, 2, 3, 4)}
assert 130 <= MONSTERS[3] <= 160, MONSTERS
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
