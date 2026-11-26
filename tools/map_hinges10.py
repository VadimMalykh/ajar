"""Act 1, level 10: "All Change" (MAP10).

A town square at night, and a bus standing at its stop (Vadim's idea,
2026-11-16: the teleporter bus of "Гостья из будущего"). The bus is the flat
red outline of a bus with numbered doors, and every door is another place:
the places are the earlier levels. It stands free in the square, as in the
film, and you walk round it (Vadim, 2026-11-17): six doors in the face it
turns to the stop, 1 to 6, and two in its back, 7 and 8 (ajarmap.bus). The
square's walls are no taller than the bus: the engine draws sky over a solid
block, whatever stands behind it.

  1  the hotel (MAP02): a line that always runs. You come in where MAP02
     began, and it is MAP02's ground floor as it stands (ajarmap.excerpt)
  2  a frame: whatever you hang there is a line of your own
  3  GREEN's far side: GREEN is a ticket back to the stop from anywhere
  4  no number: one of the places a Stray door opens onto
  5  the station (MAP05), the same way: concourse, platforms, tracks
  6  a brass frame, and facing it across the pavement, in the shelter, the
     other one: the way out
  7  a second frame
  8  the other stop: a line that always runs

The other stop (Vadim, 2026-11-17) is another square with another bus, the
20, amber where the 10 is red, and other doors: 1 back to the first stop,
2 the pit under the theatre's stage door, a door with no number (Stray
doors), and in its back 4, the observatory (MAP07).

The depot is a yard beyond the lane behind the bus. Nothing on the bus goes
there: YELLOW's far side is in its wall, and YELLOW is the ticket.

RED opens onto the theatre: MAP03's foyer, house and the rooms behind, as
they stand. The districts have doors of their own, and they lead to each
other or to the stop: RED leans in the hotel, YELLOW on the station's far
platform, GREEN in the theatre. The museum (MAP06) stands on the square,
locked. A route board in the shelter has a lamp for each door of the bus and
shows what runs (ajarmap.route_board).

The way out is MAP09's chain. The night room hangs over the shelter, with
BLUE's far side and VIOLET's in its two ends; hang those two in the two brass
frames and the bus and the shelter open onto each other through it, without
end. Nothing is fixed until you walk onto the line.

The secret way out (Vadim, 2026-11-17) is the same place, built with three
doors: PINK is the third. PINK opens, as it always has, onto a room nobody can
get into otherwise, and that room has a brass frame of its own
(ajarmap.way_longer). PINK in one brass frame at the stop, BLUE or VIOLET in
the other, and the last of them in PINK's room: a loop of three rooms. Closing
it is a secret, and leaving the line by it is the secret exit. A door gets
into PINK's room only through PINK, so PINK has to hang somewhere else first.

The catches. VIOLET leans in the museum's cellar: you drop in with whatever
you carry and leave by a hole no door fits through, so VIOLET comes out
through another door, hung in the cellar's frame (GREEN takes you straight
to the stop). BLUE is under the observatory's dome, behind the depot's
key, and the dome is such a place too: a ledge, a drop, stairs up to a
hole. Two doors have to be spared for the two of them while a third keeps a
line running.

Places. "main" is the two stops, the hotel, the station and the
observatory's library (the lines that always run). The theatre (RED's far
side): GREEN, key 1; its stage door is a ledge over a pit, and from the pit
a line runs to the other stop: out, and never in. The museum (key 1):
hall and gallery; the cellar; PINK's store (secret: ring its bell). The depot
(YELLOW's far side): key 2. The dome, off the observatory's library (key 2):
BLUE. The depot's gate lets you out to the lane behind the bus, a step down,
and never in.

Company: lodgers in the bus's empty frames. What a key or a door brings arrives at the square.
"""
import os

import ajarmap
import gfx_museum
import map_hinges6 as six                             # the museum, as MAP06 dresses it
import map_hinges7 as seven                           # the observatory, as MAP07 does
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id, HOME, HOME2, HOME3
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


D = 48                                                # the depot's ground: a step nobody climbs
LINE = 64                                             # the floor of the night room, over the shelter
PF = D + 96                                           # PINK's room, over the depot
NIGHT = 150
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, ajarmap.ROSE
# The square's look (gfx_square.py): where the film's bus was left, forty years
# on: a concrete fence, cracked asphalt, a sheet-steel shelter, a kiosk.
# AJAR_SQUARE=0 is the square in the plain textures it was first built in. A
# look changes textures only. The bus has one look (gfx_bus.py).
LOOK = (os.environ.get("AJAR_SQUARE") or "1") != "0"
FENCE, BRICK = ("AJQF", "AJQB") if LOOK else ("AJBRICK", "AJBRICK")
OPEN = dict(ceil=512, ctex="F_SKY1", wall=BRICK)
SQUARE = dict(ceil=ajarmap.BUS_H, ctex="F_SKY1", wall=FENCE)         # no wall taller than the bus (ajarmap.bus)
DY = 352                                              # how far north of the bus the depot's yard begins, less 192
SEAT = dict(ftex="AJQBE", side="AJQBE", floor=16) if LOOK else dict(ftex="AJSOFA", side="AJSOFA", floor=16)
CASE = dict(ftex="AJSTEEL", side="AJWOOD", floor=40)
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
KIOSK, STORE = 401, 402
NX, NY = 304, -560                                    # the night room's south-west corner

# the districts wear what their levels wear (the looks chosen from the boards)
HOTEL = dict(wall="AJ2L1", ftex="AJ2F1")                              # MAP02's lobby
HROOM = dict(wall="AJ2W1", ftex="AJ2C1")                              # ... and a room
STATION = dict(wall="AJ5H1", ftex="AJ5F1", ctex="AJ5CH1")             # MAP05's concourse
WAITING = dict(wall="AJ5W1", ftex="AJ5I1", ctex="AJ5CL1")             # ... its waiting room
PLATFORM = dict(ceil=512, ctex="F_SKY1", wall="AJ5Y1", ftex="AJ5P1")  # ... a platform
FOYER = dict(wall="AJ3F1", ftex="AJ3O1", ctex="AJ3E1")                # MAP03's foyer
STALLS = dict(wall="AJ3H1A", ftex="AJ3M1", ctex="AJ3C1")              # ... the house
BACKSTAGE = dict(wall="AJ3XW", ftex="AJ3XF")                          # ... behind it
PAVE = dict(ftex="AJQAS" if LOOK else "AJ4F1")                        # asphalt (plain: MAP04's yard)
STOP = dict(ftex="AJQPV" if LOOK else "AJ4F1")                        # the slabs a stop is paved with
if LOOK:
    import gfx_square
    m.align |= gfx_square.ALIGNED
m.align |= six.m.align | seven.m.align


def low(floor=0, wall=None, ctex=None):
    """A porch: doors and frames under the sky stand under one. In the look
    `wall` is the wall under it and `ctex` what it is roofed with."""
    return dict(dict(ceil=floor + 128, ctex=ctex if LOOK and ctex else "AJBOARD"), **(dict(wall=wall) if LOOK and wall else {}))


def over(a, b, tex, **k):
    """The wall over the opening a-b (under a lower ceiling) carries on as
    `tex`, in line with the wall beside it."""
    if tex:
        m.line(a, b, upper=tex, dontpegtop=True, **k)


def porch(box, tex, sides, peg=True):
    """What is over the open sides ("SENW") of a low-roofed piece of a taller
    place: the taller place's wall (`peg`), or the edge of a canopy."""
    x1, y1, x2, y2 = box
    ends = dict(S=((x1, y1), (x2, y1)), E=((x2, y1), (x2, y2)), N=((x2, y2), (x1, y2)), W=((x1, y2), (x1, y1)))
    for side in sides if tex else ():
        m.line(*ends[side], upper=tex, **(dict(dontpegtop=True) if peg else dict(exact=True)))


def pieces(fixed, starts, axis, tex):
    """64-long pieces of a wall with a texture of their own, each starting at a multiple of 64."""
    for s in starts if tex else ():
        a, b = ((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
        m.cut(a, b)
        m.line(a, b, mid=tex)


def bars(a, b, out, floor, thick=16, near=None, far=None):
    """A barred opening in a wall: to look and shoot through. `near` and `far`
    are the walls it is cut through on either side."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall="AJTRIM" if near else "AJBRICK",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)
    if near:
        m.line(a, b, upper=near, lower=near, dontpegtop=True, dontpegbottom=True)
    if far:
        m.line(c, d, upper=far, lower=far, dontpegtop=True, dontpegbottom=True)


def pools(spots, base):
    """Small hours, as in MAP07: the light round each lamp, falling off in three steps."""
    return [((x - d, y - d, x + d, y + d), dict(light=min(255, base + up)))
            for d, up in ((112, 25), (80, 50), (48, 80)) for x, y in spots] if seven.DIM else []


Q = (lambda name: name) if LOOK else (lambda name: None)             # a texture of the square's look, or nothing
T6, T7 = (six.T if six.LOOK else (lambda *a: None)), (seven.T if seven.LOOK else (lambda *a: None))

# === the square, the bus ===========================================================
# start here: nobody about but whoever lives in the bus
ajarmap.fitted(m, (-512, -640, 224, -48), [
    ((-448, -640, -256, -576), low(wall="AJQK", ctex="AJQSC")),              # before the kiosk: its canopy
    ((-512, -432, -448, -304), low(wall="AJQMP")),                           # before the museum's door
    ((-192, -400, -64, -368), SEAT), ((64, -400, 192, -368), SEAT),
], floor=0, light=NIGHT, **PAVE, **SQUARE)
porch((-448, -640, -256, -576), Q("AJQKF"), "NEW", peg=False)
porch((-512, -432, -448, -304), Q("AJQMF"), "NES", peg=False)
for a, b in (((-512, -640), (-512, -432)), ((-512, -304), (-512, -128))):    # the museum's side of the square
    m.cut(a, b)
    if LOOK:
        m.line(a, b, mid="AJQM")
pieces(-512, (-576, -256), "y", Q("AJQMA"))
pieces(-640, (-192,), "x", Q("AJQFA"))                                       # the fence: posters, a corner knocked out
pieces(-640, (64,), "x", Q("AJQFB"))
# the shelter: the second brass frame, facing door 6 across the pavement; the
# route board; over it, a hole with a starry ceiling behind
SHELTER = low(wall="AJQS", ctex="AJQSC")
ajarmap.fitted(m, (224, -208, 512, -48), [
    ((256, -208, 512, -144), SHELTER),                                       # the shelter's roof: its frame, the hole
    ((448, -208, 512, -48), SHELTER),                                        # over the route board
], floor=0, light=NIGHT + 10, **STOP, **SQUARE)
if LOOK:                                                                     # the edge of its roof; the stop's sign
    for a, b in (((256, -144), (448, -144)), ((256, -208), (256, -144)), ((448, -144), (448, -48)), ((448, -48), (512, -48))):
        m.line(a, b, upper="AJQSF", exact=True)
    pieces(-208, (448,), "x", "AJQSA")
# the bus stands free: past its two ends and along the lane behind it
ajarmap.fitted(m, (-640, -48, -400, 192), [], floor=0, light=NIGHT, **PAVE, **SQUARE)
ajarmap.fitted(m, (400, -48, 640, 192), [], floor=0, light=NIGHT, **PAVE, **SQUARE)
ajarmap.fitted(m, (-640, 192, 640, 448), [
    ((416, 384, 512, 448), low(wall=Q("AJQB"))),                             # under the depot's gate
    ((-192, 304, -64, 336), SEAT), ((64, 304, 192, 336), SEAT),
], floor=0, light=NIGHT, **PAVE, **SQUARE)
porch((416, 384, 512, 448), Q("AJQDF"), "SEW", peg=False)
pieces(448, (-448, 256), "x", Q("AJQFA"))
pieces(448, (-128,), "x", Q("AJQFB"))
pieces(640, (64,), "y", Q("AJQFA"))
pieces(-640, (256,), "y", Q("AJQFB"))
south = ajarmap.bus(m, -400, 0, face=1, floor=0, first=1, free=True, light=NIGHT + 20, **STOP)
north = ajarmap.bus(m, -400, 144, face=-1, floor=0, first=7, slots=(4, 1), free=True, light=NIGHT + 20, **STOP)
ajarmap.bus_ends(m, -400, 0)
recess(*south[1], (0, 1), 0, 101, 201)                                       # 2: a frame
recess(*south[2], (0, 1), 0, far_id(GREEN), 101, far_colour=GREEN)           # 3: GREEN's far side
ajarmap.stray_place(m, 0, *south[3], (0, 1), 0)                              # 4: no number
m.line(*south[3], upper="AJBN0")
ajarmap.brass_pair(m, *south[5], (288, -208), (352, -208), 0, BLUE, VIOLET, outs=((0, 1), (0, -1)))   # 6, and the shelter
recess(*north[0], (0, -1), 0, 102, 201)                                      # 7: a second frame
ajarmap.route_board(m, (512, -56), [(1, None), (2, 101), (3, GREEN), (5, None), (6, HOME), (0, HOME2),
                                    (7, 102), (8, None)], step=(0, -16))
# the line: BLUE's far side at its west end, VIOLET's at its east end, and a
# hole to drop out by, into the shelter
ajarmap.way_through(m, NX, NY, BLUE, VIOLET, floor=LINE, longer=PINK)
m.sector(rect(384, NY + 256, 448, -208), floor=LINE, ceil=LINE + 96, light=150, wall="AJBRICK",
         ftex="AJTRIMF", ctex="AJTRIMF")
# the kiosk (secret), seen through bars: shoot its bell. A Stray door opens onto it too
m.sector(rect(-464, -720, -240, -656), ceil=112, light=170, color=ROSE, wall="AJSAFE")
m.sector(rect(-464, -848, -240, -720), ceil=112, light=170, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (-448, -640), (-384, -640), (0, -1), 0, KIOSK, line_id=305)
ajarmap.unbolt(m, (-464, -720), (-240, -720), KIOSK)
bars((-320, -640), (-256, -640), (0, -1), 0, near=Q("AJQK"), far=Q("AJSAFE"))
m.cut((-320, -848), (-256, -848))
m.line((-320, -848), (-256, -848), special=11, args=(KIOSK, 32), impact=True, mid="AJTARG", exact=True)
ajarmap.stray_place(m, 1, (-464, -816), (-464, -752), (-1, 0), 0, color=ROSE)

# === the places the lines go: the earlier levels, as they stand ====================
# (Vadim, 2026-11-17: "bigger parts of other maps". ajarmap.excerpt lifts out of
# a level all that can be walked without a door that is carried; where that
# level had a frame or a far side there is a place for one of this level's.)
import map_hinges2, map_hinges3, map_hinges5
HX, SX, TY = -6400, 3200, -4480                       # where the hotel, the station and the theatre are put
hotel = ajarmap.excerpt(m, map_hinges2.m, (256, 96), HX, 0)          # MAP02's ground floor
station = ajarmap.excerpt(m, map_hinges5.m, (256, 64), SX, 0)        # MAP05: concourse, platforms, tracks
theatre = ajarmap.excerpt(m, map_hinges3.m, (-200, 1352), 0, TY,     # MAP03: foyer, house, the rooms behind
                          without=[(224, 912 + TY, 672, 1008 + TY), (224, 896 + TY, 288, 912 + TY)])   # (the stage door, its pit and the pit's line are this level's)
m.things = [t for t in m.things if (t["x"], t["y"]) != (HX - 16, 272)]     # a candle whose niche stayed behind
# line 1 comes in where MAP02 began, line 5 where MAP05 did
ajarmap.doorway(m, 1, *south[0], (0, 1), 0, *hotel[0])
ajarmap.doorway(m, 2, *south[4], (0, 1), 0, *station[0])
ajarmap.stray_place(m, 2, *station[2][:3], station[2][3])                    # on a platform
ajarmap.stray_place(m, 4, *hotel[1][:3], hotel[1][3])                        # in the hotel's far hall
# the theatre: RED's far side is in its foyer. Its stage door is a ledge over
# a pit behind the house: down there is a line that always runs, to the other
# stop; nobody climbs back. (A place a Stray door may open onto needs a way
# out on foot.)
recess(*theatre[0][:3], theatre[0][3], far_id(RED), 101, far_colour=RED)
ajarmap.opening(m, (224, 896 + TY), (288, 896 + TY), (0, 1), 0)
ajarmap.fitted(m, (224, 912 + TY, 608, 1008 + TY), [
    ((224, 912 + TY, 288, 1008 + TY), dict(floor=0, ftex="AJBOARD", side="AJWOOD")),     # the ledge
], floor=-48, ceil=128, light=160, **BACKSTAGE)
for a, b in (((288, 912 + TY), (608, 912 + TY)), ((608, 912 + TY), (608, 1008 + TY)), ((224, 1008 + TY), (608, 1008 + TY))):
    m.line(a, b, lower=BACKSTAGE["wall"])               # the circle is over the pit, round it: the pit's walls stay its own

# === the other stop: another bus, other doors ======================================
# (Vadim, 2026-11-17.) Door 8 of the first bus is door 1 of this one.
BY = 3168                                             # this bus's south face
for box, feats in (((-640, BY - 288, 640, BY - 48), [((-192, BY - 208, -64, BY - 176), SEAT), ((64, BY - 208, 192, BY - 176), SEAT)]),
                   ((-640, BY - 48, -400, BY + 192), []), ((400, BY - 48, 640, BY + 192), []),
                   ((-640, BY + 192, 640, BY + 432), [])):
    ajarmap.fitted(m, box, feats, floor=0, light=NIGHT, **(PAVE if LOOK else dict(ftex="AJ5P1")), **SQUARE)
STOP2 = STOP if LOOK else dict(ftex="AJ5P1")
south2 = ajarmap.bus(m, -400, BY, face=1, first=1, slots=(0, 2, 4), free=True, livery="C", light=NIGHT + 20, **STOP2)
north2 = ajarmap.bus(m, -400, BY + 144, face=-1, first=4, slots=(3,), free=True, livery="C", light=NIGHT + 20, **STOP2)
pieces(BY - 288, (-320, 384), "x", Q("AJQFA"))
pieces(BY + 432, (128,), "x", Q("AJQFB"))
pieces(BY + 432, (-512,), "x", Q("AJQFA"))
ajarmap.bus_ends(m, -400, BY, livery="C")
ajarmap.doorway(m, 3, *north[1], (0, -1), 0, *south2[0], (0, 1), 0)          # 8 of the first bus: 1 of this one
ajarmap.doorway(m, 5, *south2[1], (0, 1), 0, (608, 928 + TY), (608, 992 + TY), (1, 0), -48)   # 2: under the stage door
ajarmap.stray_place(m, 3, *south2[2], (0, 1), 0)                             # 3: no number
m.line(*south2[2], upper="AJCN0")

# === the museum, on the square: one lock ===========================================
# Rooms of this level's own plan, dressed as MAP06 dresses its own (Vadim,
# 2026-11-17: what is of another level is to look as it does there): the great
# hall 384 high with its porches, a wing's gallery 160 high with its pictures,
# the cellar 128 high. Its dictionaries are MAP06's (the look chosen there).
HK, LOW6 = T6("HK"), six.LOW
ajarmap.fitted(m, (-1168, -640, -528, -128), [
    ((-592, -432, -528, -304), LOW6),                                        # inside its door
    ((-1168, -464, -1104, -336), LOW6),                                      # before the way down
    ((-932, -192, -804, -128), LOW6),                                        # before the gallery
    ((-960, -480, -832, -352), six.CASE),                                    # a case
    ((-720, -608, -592, -576), six.SEAT),
], floor=0, ceil=384, light=190, **six.HALL)
porch((-592, -432, -528, -304), HK, "NSW")
porch((-1168, -464, -1104, -336), HK, "NSE")
porch((-932, -192, -804, -128), HK, "SEW")
pieces(-128, (-1088,), "x", T6("H", "1"))                                    # its two big pictures
pieces(-640, (-896,), "x", T6("H", "2"))
ajarmap.roomdoor(m, (-512, -400), (-512, -336), (-1, 0), 0, keys="1", line_id=301)
if LOOK:
    m.line((-512, -400), (-512, -336), upper="AJQMD1")                       # its face on the square
if six.LOOK:
    gfx_museum.FACES["P"] = ("A", 16, "1")                                   # ... and inside, under the hall's porch
    m.line((-528, -400), (-528, -336), upper=T6("D") + "P")
# the cellar: you drop in with what you carry, and leave by a hole no door fits
# through. 128 high, as MAP06's, but for the bay you drop into
CELL = dict(floor=-128, ceil=0, light=140, wall=six.CELLW, ftex="AJPIT")
ajarmap.fitted(m, (-1600, -560, -1184, -112), [
    ((-1440, -400, -1344, -304), dict(six.CRATE, floor=-128 + 48)),          # crates
    ((-1280, -208, -1216, -144), dict(six.CRATE, floor=-128 + 48)),
    ((-1248, -464, -1184, -336), dict(ceil=128, wall=six.STAIR["wall"], ctex=six.STAIR.get("ctex", "AJBOARD"))),   # under the hole
], **CELL)
ajarmap.opening(m, (-1168, -432), (-1168, -368), (-1, 0), 0)
over((-1168, -432), (-1168, -368), six.LOWW)
recess((-1600, -368), (-1600, -304), (-1, 0), -128, 114, 201)                # the cellar's frame
ajarmap.stairs(m, (-1560, -112), (-1496, -112), (0, 1), -128, 128, ceil=128, light=140, **six.STAIR)
m.sector(rect(-1560, 144, -1496, 208), floor=0, ceil=128, light=150, **six.LANDING)
ajarmap.squeeze(m, (-1496, 152), (-1496, 200), (1, 0), 0)
over((-1496, 152), (-1496, 200), six.CELLW if six.LOOK else None)
over((-1480, 152), (-1480, 200), six.WA.get("wall"))
# the gallery
ajarmap.fitted(m, (-1480, -96, -720, 400), [
    ((-1320, 64, -1192, 192), six.CASE),                                     # cases
    ((-1000, 64, -872, 192), six.CASE),
    ((-784, 256, -720, 384), six.SEAT),
], floor=0, ceil=160, light=175, **six.WA)
for i, (fixed, start) in enumerate(((400, -1408), (400, -960), (400, -832), (-96, -1344), (-96, -1152), (-96, -1024))):
    pieces(fixed, (start,), "x", T6("WA", "123"[i % 3]))                     # its pictures
ajarmap.opening(m, (-900, -128), (-836, -128), (0, 1), 0, thick=32)
over((-900, -128), (-836, -128), six.LOWW)
over((-900, -96), (-836, -96), six.WA.get("wall"))
# PINK's store (secret), seen through bars: ring its bell. PINK leans in it
m.sector(rect(-1320, 416, -1000, 480), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(-1320, 480, -1000, 640), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (-1260, 400), (-1196, 400), (0, 1), 0, STORE, line_id=306)
if six.LOOK:
    gfx_museum.BOLTS["G"] = ("WA", -1260 % 64)                               # its face in the gallery's wall
    m.line((-1260, 400), (-1196, 400), upper=f"AJ6Z{six.LOOK}G")
ajarmap.unbolt(m, (-1320, 480), (-1000, 480), STORE)
bars((-1100, 400), (-1036, 400), (0, 1), 0, near=six.WA.get("wall"), far="AJSAFE" if six.LOOK else None)
m.cut((-1100, 640), (-1036, 640))
m.line((-1100, 640), (-1036, 640), special=11, args=(STORE, 32), impact=True, mid="AJTARG", exact=True)

# === the depot (YELLOW's far side), beyond the lane ================================
BUSES = dict(ftex="AJQRF" if LOOK else "AJSTEEL", side="AJBUS", floor=D + ajarmap.BUS_H)   # the ones that are only buses
ajarmap.fitted(m, (-512, 192 + DY, 512, 640 + DY), [
    ((-448, 384 + DY, -128, 512 + DY), BUSES), ((128, 448 + DY, 448, 576 + DY), BUSES),
    ((-64, 576 + DY, 64, 640 + DY), dict(WOOD, floor=D + 48)),
    ((176, 576 + DY, 336, 640 + DY), dict(low(D + 32), lift=D + 160 - 512)),   # under the hole from PINK's room
    ((-64, 192 + DY, 64, 256 + DY), dict(low(D), lift=D + 128 - 512)),      # over YELLOW's far side
], floor=D, light=NIGHT, ftex="AJQOC" if LOOK else "AJSTEEL", **OPEN)       # (a porch's wall laid as the yard's: lift)
recess((-32, 192 + DY), (32, 192 + DY), (0, -1), D, far_id(YELLOW), 101, far_colour=YELLOW)
# the gate: out to the lane behind the bus, a step down, and never in. It takes
# a door through: with a hole for empty hands only, whoever carried YELLOW in
# here had shut the depot for good (the solver)
ajarmap.opening(m, (432, 192 + DY), (496, 192 + DY), (0, -1), D, thick=96)
# PINK's room (secret), over the depot: the third frame of the long way out
ajarmap.way_longer(m, 96, 720 + DY, PINK, BLUE, VIOLET, floor=PF)
m.sector(rect(224, 640 + DY, 288, 720 + DY), floor=PF, ceil=PF + 96, light=150, wall="AJBRICK",
         ftex="AJTRIMF", ctex="AJTRIMF")

# === the observatory (line 4 of the other bus) ======================================================
# This level's own rooms again, dressed and lit as MAP07's: the library 320
# high and dim, a pool of light at each torch; the dome 448 high and dark, the
# telescope on its pier; doors and frames under porches.
LIB, DOME, LOW7 = seven.LIB, seven.DOME, seven.low()
PASSAGE = dict(wall=seven.LOWW or LIB["wall"], ftex=LIB["ftex"], ctex=LOW7["ctex"])
TORCHES = [(1616, 1100), (2096, 1100), (1616, 1290), (2096, 1290)]
LBOX = (1600, 1000, 2112, 1384)
ajarmap.shaped(m, LBOX, pools(TORCHES, seven.DARK) + [
    ((1824, 1000, 1888, 1384), seven.RUN),
    ((1632, 1160, 1760, 1224), dict(seven.BOOKS, floor=96)),                             # stacks
    ((1952, 1160, 2080, 1224), dict(seven.BOOKS, floor=96)),
    ((1792, 1000, 1920, 1064), LOW7),                                                    # before the bus's door
    ((1792, 1320, 1920, 1384), LOW7),                                                    # before the dome's
    ((1600, 1320, 1664, 1384), LOW7),                                                    # before the way round
], floor=0, ceil=320, light=seven.DARK, **LIB)
porch((1792, 1000, 1920, 1064), LIB["wall"] if seven.LOOK else None, "NEW")
porch((1792, 1320, 1920, 1384), LIB["wall"] if seven.LOOK else None, "SEW")
porch((1600, 1320, 1664, 1384), LIB["wall"] if seven.LOOK else None, "SE")
ajarmap.doorway(m, 4, *north2[0], (0, -1), 0, (1824, 1000), (1888, 1000), (0, -1), 0)   # 4 of the other bus
# the dome: its floor is sunk. The door lets onto a ledge; you drop in with what
# you carry and leave by stairs and a hole no door fits through, as in the
# museum's cellar. So BLUE leaves through another door, hung in the dome's frame
PIT = -96
LEDGE = (1792, 1400, 1920, 1464)
ajarmap.shaped(m, (1664, 1400, 2048, 1784), pools([(1688, 1424), (2024, 1424)], seven.DARK) + [
    (LEDGE, dict(LOW7, floor=0, **seven.WOOD)),                                          # the ledge inside the door
    ((1808, 1544, 1904, 1640), dict(seven.PIER, floor=PIT + 64, light=min(255, seven.DARK + 85) if seven.DIM else seven.DARK)),   # the pier
], floor=PIT, ceil=448, light=seven.DARK, **DOME)
porch(LEDGE, DOME["wall"] if seven.LOOK else None, "NEW")
ajarmap.roomdoor(m, (1824, 1384), (1888, 1384), (0, 1), 0, keys="2", line_id=302)
if seven.LOOK:                                                               # its two faces, each under a porch
    m.line((1824, 1384), (1888, 1384), upper=seven._face("D", "A", (1824, 1384), (0, 1), "2"))
    m.line((1824, 1400), (1888, 1400), upper=seven._face("D", "A", (1824, 1384), (0, -1), "2"))
recess((2048, 1560), (2048, 1624), (1, 0), PIT, 116, 201)                    # the dome's frame
ajarmap.stairs(m, (1664, 1700), (1664, 1764), (-1, 0), PIT, 96, steps=6, ceil=160, light=150,
               lift=160 - 448, **DOME)                  # its walls laid as the dome's are, from the dome's ceiling
over((1664, 1700), (1664, 1764), DOME["wall"] if seven.LOOK else None)
m.sector(rect(1408, 1700, 1472, 1764), floor=0, ceil=128, light=150, **PASSAGE)
ajarmap.squeeze(m, (1416, 1700), (1464, 1700), (0, -1), 0)
m.sector(rect(1408, 1320, 1472, 1684), floor=0, ceil=128, light=150, **PASSAGE)
m.sector(rect(1472, 1320, 1584, 1384), floor=0, ceil=128, light=150, **PASSAGE)
ajarmap.opening(m, (1600, 1320), (1600, 1384), (-1, 0), 0)

# --- walls that carry on ------------------------------------------------------
# (Vadim, 2026-11-26, in the pit under the stage door: "decor issue". Its band
# stepped where the wall went on over a higher floor, and over its doorway
# stood a block of the arch's stone.)
#
# 1. The wall over (or under) a frame, a far side, a doorway, an opening, a
# hole or a squeeze is the room's own: no trim, no arch stone, no other room's
# wall. Door faces, signs, bars and nailed-up doors stay as they are.
BAR, GREENROOM, HOUSE, CIRCLE = "AJ3B1", "AJ3XG", "AJ3H1D", "AJ3H1B"       # MAP03's, where its pieces are
for a, b, tex in (
        ((608, 928 + TY), (608, 992 + TY), BACKSTAGE["wall"]),              # the pit under the stage door: its doorway
        ((224, 912 + TY), (288, 912 + TY), BACKSTAGE["wall"]),              # ... the stage door, from the ledge
        ((224, 896 + TY), (288, 896 + TY), STALLS["wall"]),                 # ... and from the house
        ((672, 928 + TY), (672, 976 + TY), CIRCLE), ((672, 976 + TY), (672, 992 + TY), CIRCLE),   # ... the doorway's back, on the circle
        ((-256, 1024 + TY), (-192, 1024 + TY), FOYER["wall"]),              # RED's far side in the foyer
        ((240, 1488 + TY), (240, 1552 + TY), FOYER["wall"]), ((256, 1488 + TY), (256, 1552 + TY), BAR),   # foyer and bar
        ((2112, 992 + TY), (2112, 1056 + TY), BACKSTAGE["wall"]), ((2128, 992 + TY), (2128, 1056 + TY), GREENROOM),
        ((512, -96 + TY), (640, -96 + TY), HOUSE),                          # high in the house
        ((HX + 224, 0), (HX + 288, 0), HOTEL["wall"]),                      # line 1, in the hotel's lobby
        ((HX - 352, -64), (HX - 352, 0), HROOM["wall"]), ((HX - 368, -64), (HX - 368, 0), "AJ2T1"),   # a room and its bath
        ((HX - 1696, 848), (HX - 1632, 848), "AJ2KW"),                      # a Stray door's place, in the kitchen
        ((SX + 352, 0), (SX + 416, 0), "AJ5A1"),                            # line 5, in the station's vestibule
        ((SX + 1088, 1280), (SX + 1152, 1280), "AJ5A1"),                    # a Stray door's place, on a platform
        ((-464, -816), (-464, -752), "AJSAFE"),                             # ... and in the kiosk
        ((304, -464), (304, -400), "AJXW2"), ((624, -464), (624, -400), "AJXW2"),   # the line: BLUE's and VIOLET's far sides
        ((384, -304), (448, -304), "AJXW2"),                                # ... its hole
        ((96, 1168), (96, 1232), "AJXW2"), ((416, 1168), (416, 1232), "AJXW2"),     # PINK's room: PINK's far side, its brass frame
        ((224, 1072), (288, 1072), "AJXW2"),                                # ... its hole
        ((288, -208), (352, -208), Q("AJQS")),                              # the shelter's brass frame
        ((-32, 192 + DY), (32, 192 + DY), BRICK),                           # YELLOW's far side in the depot
        ((432, 192 + DY), (448, 192 + DY), BRICK), ((448, 192 + DY), (496, 192 + DY), BRICK),   # the depot's gate
        ((1824, 1000), (1888, 1000), seven.LOWW),                           # line 4, in the observatory's library
        ((1600, 1320), (1600, 1338), seven.LOWW), ((1600, 1338), (1600, 1370), seven.LOWW),
        ((1600, 1370), (1600, 1384), seven.LOWW),                           # ... the way round, from the library
        ((1584, 1320), (1584, 1384), PASSAGE["wall"]),                      # ... and from the passage
        ((1416, 1684), (1464, 1684), PASSAGE["wall"]), ((1416, 1700), (1464, 1700), PASSAGE["wall"]),   # its squeeze
        ((2048, 1560), (2048, 1624), DOME["wall"] if seven.LOOK else None),  # the dome's frame
        ((1472, 1700), (1472, 1764), DOME["wall"] if seven.LOOK else None),  # the top of the dome's stairs
        ((-1600, -368), (-1600, -304), six.CELLW),                          # the cellar's frame (its mouth, whole)
):
    over(a, b, tex)
for a, b, tex in (                                                           # ... and under
        ((432, 448), (496, 448), BRICK),                                    # the depot's gate, from the lane
        ((224, 640 + DY), (288, 640 + DY), BRICK),                          # the hole from PINK's room, in the depot
        ((384, -208), (448, -208), Q("AJQS") or FENCE),                     # the hole from the line, in the shelter
        ((-1184, -432), (-1184, -400), six.STAIR["wall"]),                  # the hall, from the cellar's bay
        ((-1184, -400), (-1184, -368), six.STAIR["wall"]),
):
    m.line(a, b, lower=tex)
m.line((432, 448), (496, 448), upper="AJTRIM")                               # (inside the gate)
m.line((384, -208), (448, -208), upper="AJBRICK")                            # (inside the holes)
m.line((224, 640 + DY), (288, 640 + DY), upper="AJBRICK")
over((-1560, -112), (-1496, -112), six.STAIR["wall"])                        # the foot of the cellar's stairs, from them
for a, b in (((-1184, -432), (-1184, -400)), ((-1184, -400), (-1184, -368))):
    m.line(a, b, upper=six.STAIR["wall"])


# 2. Where a room's own wall goes on over or under a step in the ceiling or the
# floor (a porch, a window, a higher floor beyond, a riser), it is laid from the
# room's ceiling as the rest of that wall is, not from the step: its bands and
# courses run on. Only where every side that shows that part shows its own
# room's wall, and never on a line with something on it (a railing).
def carried(ld, sides, a, b, si, other, given):
    if other is None or given["mid"] not in (None, "AJWIN"):          # (a window's glass is as tall as its opening)
        return
    for part, flag, shows in (("top", "dontpegtop", lambda s, o: s["ceil"] > o["ceil"]),
                              ("bottom", "dontpegbottom", lambda s, o: o["floor"] > s["floor"])):
        seen = [(k, m.sectors[x]) for k, x, y in (("sidefront", si, other), ("sideback", other, si))
                if shows(m.sectors[x], m.sectors[y])]
        if ld.get(flag) or not seen or any(sides[ld[k]].get("texture" + part) != s["wall"] for k, s in seen):
            continue
        ld[flag] = True
        for k, s in seen:                                             # a room under a strip of lights (sector(lift=))
            if s["lift"]:
                sides[ld[k]]["offsety_" + part] = float(-s["lift"])


m.line_hook = carried


# 3. The same for the walls of a low piece of a room: the reveals of the
# hotel's windows (sill and sky, MAP02's ajarmap.window) and the attic's floor
# seen up its shaft are laid from the ceiling of the room they open off.
def sector_at(x, y):
    for i, poly in enumerate(m.polys):
        hit = False
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                hit = not hit
        if hit:
            return m.sectors[i]
    return None


def laid_from(low, room):
    low["lift"] = low["ceil"] - (room["ceil"] - room["lift"])


for key, p in list(m.lineprops.items()):
    if p.get("mid") != "AJWIN" or p.get("upper") or p.get("dontpegtop"):     # (bars have their own)
        continue
    (ax, ay), (bx, by) = sorted(key)
    mx, my, n = (ax + bx) / 2, (ay + by) / 2, ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    ux, uy = (by - ay) / n, (ax - bx) / n
    for s in (1, -1):
        sill, room = sector_at(mx + s * ux * 4, my + s * uy * 4), sector_at(mx - s * ux * 4, my - s * uy * 4)
        if sill and room and sill["ftex"] == "AJTRIMF" and sill["ceil"] - sill["floor"] == 56:
            laid_from(sill, room)
            laid_from(sector_at(mx + s * ux * 10, my + s * uy * 10), room)
laid_from(sector_at(HX + 1800, 224), sector_at(HX + 1700, 224))              # the attic, from its shaft

# --- doors and keys ----------------------------------------------------------
m.thing(-64, -592, 1, angle=90)                                           # player start, in the square
ajarmap.door(m, RED, HX - 300, 330, angle=0)                              # leaning in a hotel room
ajarmap.door(m, YELLOW, SX + 1700, 1250, angle=180)                       # on the station's far platform
ajarmap.door(m, GREEN, 600, 1450 + TY, angle=180)                        # in the rooms behind the theatre's foyer
ajarmap.door(m, VIOLET, -1210, -536, angle=180)                           # in the museum's cellar
ajarmap.door(m, BLUE, 2020, 1756, angle=180)                              # under the dome
ajarmap.door(m, PINK, -1300, 616, angle=0)                                # in its store
ajarmap.stray(m, -492, -68, angle=0)                                      # Stray doors: by the bus
ajarmap.stray(m, -300, 1200 + TY, angle=0)                                # in the theatre's foyer
ajarmap.stray(m, -740, -80, angle=180)                                    # in the museum's gallery
ajarmap.stray(m, 492, 620 + DY, angle=180)                                     # in the depot
ajarmap.key(m, 1, 1104, 520 + TY)                                          # down by the stage
ajarmap.key(m, 2, -470, 600 + DY)                                              # the far corner of the depot

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACHNO, PAIN, VILE = 65, 69, 3003, 66, 3006, 3005, 67, 68, 71, 64
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
BACKPACK = 8


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the square: lamps, and those who live in the bus's empty frames
things(LAMP, (-480, -176), (192, -80), (-480, -608), (192, -608), (480, -80), (-616, 424), (616, 424))
things(LODGER, (-192, -24), (320, -100), args=(300,))
things(BONUS, (-128, -200), (-64, -200), (0, -200), (64, -200))
things(SHOTGUN, (-64, -480))
things(SHELLS, (-104, -480), (-24, -480))
things(STIM, (-160, -340), (160, -340))
# the kiosk
things(PLASMA, (-352, -790))
things(CELLS, (-420, -810), (-420, -770))
things(MEGA, (-280, -690))
# the line: nobody
# the other stop: whoever waits for the 20
things(LAMP, (-616, BY - 264), (616, BY - 264), (-616, BY + 408), (616, BY + 408))
things(REVENANT, (-300, BY - 150), (300, BY - 150), angle=270)
things(KNIGHT, (0, BY - 240), angle=90)
things(IMP, (-520, BY + 60), (520, BY + 60), (-200, BY + 320), (200, BY + 320), angle=270)
things(CACO, (0, BY + 360), angle=270, ambush=True)
things(SHELLBOX, (-600, BY - 100))
things(MEDIKIT, (600, BY - 100), (0, BY + 400))
things(ROCKETBOX, (600, BY + 300))
# under the stage door
things(STIM, (500, 960 + TY))
# the museum's hall
things(KNIGHT, (-700, -250), (-1050, -560), angle=0)
things(REVENANT, (-1100, -330), (-640, -520), angle=0)
things(IMP, (-760, -400), (-1000, -420), (-900, -600), (-640, -180), angle=0)
things(SERGEANT, (-800, -540), (-1120, -500), angle=0)
things(ARACHNO, (-1000, -230), angle=0)
things(SHELLBOX, (-560, -600))
things(MEDIKIT, (-560, -170), (-1130, -160))
things(ROCKETBOX, (-896, -530))
things(TECHLAMP, (-552, -616), (-1144, -616))
# the cellar: VIOLET, and teeth
things(DEMON, (-1300, -480), (-1500, -200), (-1250, -300), angle=180)
things(SPECTRE, (-1400, -500), (-1540, -480), (-1380, -180), angle=180)
things(MEDIKIT, (-1560, -150))
things(SHELLS, (-1220, -420))
# the gallery
things(PAIN, (-1100, 300), angle=270)
things(CACO, (-1400, 300), (-800, 40), angle=270, ambush=True)
things(CHAINGUNNER, (-1440, -40), (-760, 200), angle=270)
things(IMP, (-1250, 20), (-940, 20), (-1100, 130), angle=270)
things(PLASMA, (-1096, 240))
things(CELLS, (-1136, 240), (-1056, 240))
things(MEDIKIT, (-1440, 360))
things(SHELLBOX, (-760, -60))
# PINK's store
things(CANDLE, (-1020, 500), (-1020, 620))
things(ROCKETBOX, (-1100, 520), (-1140, 520))
things(HELMET, (-1200, 600), (-1160, 600))
things(MEDIKIT, (-1280, 520))
# the depot: key 2
things(KNIGHT, (-300, 652), (300, 672), angle=270)
things(MANCUBUS, (0, 792), angle=270)
things(REVENANT, (-480, 652), (470, 752), angle=270)
things(IMP, (-200, 912), (100, 652), (480, 962), (-80, 602), angle=270)
things(SERGEANT, (-340, 912), (60, 872), (380, 602), angle=270)
things(CACO, (-240, 602), (240, 732), angle=270, ambush=True)
things(SHELLBOX, (-480, 892), (80, 752))
things(MEDIKIT, (-480, 582), (490, 582))
things(CELLS, (-90, 892))
things(ROCKETBOX, (-100, 732))
things(LAMP, (-488, 968), (-440, 568))
# PINK's room: what the long way round is worth
things(MEGA, (256, 1112))
things(SPHERE, (160, 1292))
things(CELLS, (352, 1292), (352, 1112))
things(CANDELABRA, (128, 1104), (384, 1296))
# the observatory: the library
things(IMP, (1660, 1060), (2060, 1060), (1856, 1300), angle=270)
things(REVENANT, (1700, 1320), angle=270)
things(KNIGHT, (2000, 1320), angle=270)
things(CHAINGUNNER, (1856, 1180), angle=270)
things(SHELLBOX, (1630, 1350))
things(MEDIKIT, (2080, 1350))
# the dome: BLUE
things(BARON, (1856, 1700), angle=270)
things(ARACHNO, (1740, 1580), angle=270)
things(MEDIKIT, (1760, 1750))
things(CELLS, (2010, 1440))
things(TECHLAMP, (1688, 1424), (2024, 1424))
things(46, *TORCHES)                                                       # the library's torches, as MAP07's
things(20021, (1856, 1592), angle=90)                                      # the telescope on its pier

# --- ambushes: what a key or a door brings (ajarmap.ambush) -------------------
# The square is where they come: an arena that fills from its own stop.
# GREEN, taken: the house you go back through
# (No two alike: Vadim, 2026-11-17.) The imps at once, and when they are
# down, the revenant
ajarmap.ambush(m, 10 + GREEN, REVENANT, (520, 448 + TY), angle=90, after=5)
ajarmap.ambush(m, 10 + GREEN, IMP, (200, 448 + TY), (960, 400 + TY), angle=90)
# key 1, by the stage: either side of you, and not to be seen; and the square
# you go back to
ajarmap.ambush(m, 1, SPECTRE, (1104, 640 + TY), (1104, 440 + TY), angle=90)
ajarmap.ambush(m, 1, KNIGHT, (-300, -250), (100, -250), angle=270)
ajarmap.ambush(m, 1, IMP, (-420, -500), (160, -500), angle=90)
# VIOLET, taken in the cellar: a spectre at once, and 3 s later an arch-vile at
# the foot of the stairs, the way out, to raise the teeth you put down (Vadim,
# 2026-11-18). In a spectre's place in the order, so nothing else is thinned
# differently: it is not there on the easiest skill
ajarmap.ambush(m, 10 + VIOLET, VILE, (-1528, -190), angle=315, after=3)
ajarmap.ambush(m, 10 + VIOLET, SPECTRE, (-1500, -420), angle=0)
# key 2, in the depot: between you and the way out of its corner; and the
# square again
ajarmap.ambush(m, 2, DEMON, (-390, 600 + DY), (-300, 600 + DY), angle=180)
ajarmap.ambush(m, 2, CACO, (-200, -300), (0, -450), angle=90)
ajarmap.ambush(m, 2, IMP, (-540, 320), (540, 320), angle=270)             # and the lane behind the bus
# BLUE, taken under the dome: the library you go back through
ajarmap.ambush(m, 10 + BLUE, REVENANT, (1730, 1100), (1980, 1100), angle=90)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "main" is the two stops, the hotel, the station, the observatory's
# library, the pit under the stage door (the lines that always run) and the kiosk; "museum"
# its hall, gallery and PINK's store; "night" is the line, "pink" PINK's room.
PUZZLE = dict(
    start="main", goal="exit", names=ajarmap.NAMES, complete=True,
    home_chain=dict(frames=[HOME, HOME2], doors=[BLUE, VIOLET], secret=dict(frame=HOME3, door=PINK)),
    walk=[("main", "museum", "1"), ("museum", "main", "1"),
          ("museum", "cellar"), ("cellar", "museum", "", "squeeze"),      # down the hole; up the stairs and out
          ("depot", "main"),                                              # the gate, a step down
          ("main", "dome", "2"), ("dome", "main", "", "squeeze"),         # down off the ledge; up the stairs and out
          ("theatre", "main"),                                            # the stage door: a drop
          ("night", "main"),                                              # the hole over the shelter
          ("pink", "depot")],                                             # the hole over the depot
    keys={"1": "theatre", "2": "depot"},
    frames={101: "main", 102: "main", HOME: "main", HOME2: "main", 114: "cellar", 116: "dome",
            HOME3: "pink"},
    doors={
        RED: dict(home="theatre", lean="main"),
        YELLOW: dict(home="depot", lean="main"),
        GREEN: dict(home="main", lean="theatre"),
        VIOLET: dict(home="night", lean="cellar"),
        BLUE: dict(home="night", lean="dome"),
        PINK: dict(home="pink", lean="museum"),
    },
    pool=["main"],                         # the doors with no number; the kiosk; a platform; the hotel's far hall
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
