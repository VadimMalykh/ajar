"""Act 1, level 10: "All Change" (MAP10).

A town square at night, and a bus standing at its stop (Vadim's idea,
2026-11-16: the teleporter bus of "Гостья из будущего"). The bus is the flat
red outline of a bus with numbered doors, and every door is another place:
the places are the earlier levels. It stands free in the square, as in the
film, and you walk round it (Vadim, 2026-11-17): six doors in the face it
turns to the stop, 1 to 6, and two in its back, 7 and 8 (ajarmap.bus). The
square's walls are no taller than the bus: the engine draws sky over a solid
block, whatever stands behind it.

  1  the hotel (MAP02): a line that always runs
  2  a frame: whatever you hang there is a line of your own
  3  GREEN's far side: GREEN is a ticket back to the stop from anywhere
  4  no number: one of the places a Stray door opens onto
  5  the station (MAP05): a line that always runs
  6  a brass frame, and facing it across the pavement, in the shelter, the
     other one: the way out
  7  a second frame
  8  the observatory (MAP07): a line that always runs

The depot is a yard beyond the lane behind the bus. Nothing on the bus goes
there: YELLOW's far side is in its wall, and YELLOW is the ticket.

RED opens onto the theatre (MAP03). The museum (MAP06) stands on the square,
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

Places. "main" is the square, the hotel and the station (the lines that
always run). The theatre (RED's far side): GREEN, key 1; its stage door
lets you out onto the square, and never in. The museum (key 1):
hall and gallery; the cellar; PINK's store (secret: ring its bell). The depot
(YELLOW's far side): key 2. The dome, off the observatory's library (key 2):
BLUE. The depot's gate lets you out to the lane behind the bus, a step down,
and never in.

Company: a repainter at the stop (it changes where the lines go), lodgers in
the bus's empty frames. What a key or a door brings arrives at the square.
"""
import ajarmap
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
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
SQUARE = dict(ceil=ajarmap.BUS_H, ctex="F_SKY1", wall="AJBRICK")     # no wall taller than the bus (ajarmap.bus)
DY = 352                                              # how far north of the bus the depot's yard begins, less 192
SEAT = dict(ftex="AJSOFA", side="AJSOFA", floor=16)
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
MUSEUM = dict(wall="AJ6H2", ftex="AJ6F2", ctex="AJ6CH2")              # MAP06's great hall
GALLERY = dict(wall="AJ6WA2", ftex="AJ6FW2", ctex="AJ6CG2")           # ... a gallery
CELLAR = dict(wall="AJ6XC", ftex="AJPIT")                             # ... the cellar
LIBRARY = dict(wall="AJ7L3", ftex="AJ7FL3", ctex="AJ7CL3")            # MAP07's library
DOME = dict(wall="AJ7D3", ftex="AJ7FD3", ctex="AJ7CD3")               # ... the dome
PAVE = dict(ftex="AJ4F1")                                             # MAP04's yard, for the square


def low(floor=0):
    """A porch: doors and frames under the sky stand under one."""
    return dict(ceil=floor + 128, ctex="AJBOARD")


def bars(a, b, out, floor, thick=16):
    """A barred opening in a wall: to look and shoot through."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall="AJBRICK",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)


# === the square, the bus ===========================================================
# start here: nobody about but whoever lives in the bus
ajarmap.fitted(m, (-512, -640, 224, -48), [
    ((-448, -640, -256, -576), low()),                                       # before the kiosk
    ((-512, -432, -448, -304), low()),                                       # before the museum's door
    ((0, -640, 96, -592), low()),                                            # under the stage door
    ((-192, -400, -64, -368), SEAT), ((64, -400, 192, -368), SEAT),
], floor=0, light=NIGHT, **PAVE, **SQUARE)
# the shelter: the second brass frame, facing door 6 across the pavement; the
# route board; over it, a hole with a starry ceiling behind
ajarmap.fitted(m, (224, -208, 512, -48), [
    ((256, -208, 512, -144), low()),                                         # the shelter's roof: its frame, the hole
    ((448, -208, 512, -48), low()),                                          # over the route board
], floor=0, light=NIGHT + 10, **PAVE, **SQUARE)
# the bus stands free: past its two ends and along the lane behind it
ajarmap.fitted(m, (-640, -48, -400, 192), [], floor=0, light=NIGHT, **PAVE, **SQUARE)
ajarmap.fitted(m, (400, -48, 640, 192), [], floor=0, light=NIGHT, **PAVE, **SQUARE)
ajarmap.fitted(m, (-640, 192, 640, 448), [
    ((416, 384, 512, 448), low()),                                           # under the depot's gate
    ((-192, 304, -64, 336), SEAT), ((64, 304, 192, 336), SEAT),
], floor=0, light=NIGHT, **PAVE, **SQUARE)
south = ajarmap.bus(m, -400, 0, face=1, floor=0, first=1, free=True, light=NIGHT + 20, **PAVE)
north = ajarmap.bus(m, -400, 144, face=-1, floor=0, first=7, slots=(4, 1), free=True, light=NIGHT + 20, **PAVE)
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
bars((-320, -640), (-256, -640), (0, -1), 0)
m.cut((-320, -848), (-256, -848))
m.line((-320, -848), (-256, -848), special=11, args=(KIOSK, 32), impact=True, mid="AJTARG", exact=True)
ajarmap.stray_place(m, 1, (-464, -816), (-464, -752), (-1, 0), 0, color=ROSE)

# === the hotel (line 1) ============================================================
ajarmap.fitted(m, (-3200, -400, -2688, -16), [
    ((-2976, -400, -2912, -16), ajarmap.RUNNER),
    ((-3168, -112, -3040, -48), CASE),                                       # the desk
    ((-2816, -80, -2720, -48), SEAT),
], rug="AJ2R1", floor=0, ceil=192, light=185, **HOTEL)
ajarmap.doorway(m, 1, *south[0], (0, 1), 0, (-2976, -400), (-2912, -400), (0, -1), 0)
ajarmap.fitted(m, (-2672, -336, -2352, -80), [
    ((-2480, -336, -2384, -208), dict(ftex="AJ2Q1", side="AJ2E1", floor=24)),            # a bed
], floor=0, ceil=128, light=175, **HROOM)
ajarmap.fitted(m, (-3536, -336, -3216, -80), [
    ((-3504, -336, -3408, -208), dict(ftex="AJ2Q1", side="AJ2E1", floor=24)),
    ((-3312, -144, -3248, -80), SEAT),
], floor=0, ceil=128, light=175, **HROOM)
ajarmap.roomdoor(m, (-2688, -240), (-2688, -176), (1, 0), 0, look="1")
ajarmap.roomdoor(m, (-3200, -240), (-3200, -176), (-1, 0), 0, look="1")

# === the station (line 5) ==========================================================
ajarmap.fitted(m, (1600, -400, 2240, -16), [
    ((1888, -400, 1952, -16), dict(ftex="AJ5P1")),
    ((1664, -112, 1792, -80), SEAT), ((2048, -112, 2176, -80), SEAT),
    ((2112, -336, 2176, -208), CASE),                                        # the enquiry desk
], floor=0, ceil=256, light=180, **STATION)
ajarmap.doorway(m, 2, *south[4], (0, 1), 0, (1888, -400), (1952, -400), (0, -1), 0)
ajarmap.fitted(m, (1728, 0, 2112, 256), [
    ((1792, 192, 1920, 224), SEAT), ((1984, 64, 2048, 128), CASE),
], floor=0, ceil=160, light=175, **WAITING)
ajarmap.roomdoor(m, (1888, -16), (1952, -16), (0, 1), 0)
# a platform, under the sky: one of the places a Stray door opens onto
ajarmap.fitted(m, (1152, -400, 1584, -16), [
    ((1520, -272, 1584, -144), low()),
    ((1152, -272, 1216, -144), low()),
    ((1280, -400, 1456, -336), dict(ftex="AJSTEEL", side="AJ5N1", floor=112)),           # a carriage
], floor=0, light=NIGHT, **PLATFORM)
ajarmap.opening(m, (1600, -240), (1600, -176), (-1, 0), 0)
ajarmap.stray_place(m, 2, (1152, -240), (1152, -176), (-1, 0), 0)

# === the theatre (RED's far side) ==================================================
# It stands on the square's south side, a step up, and you would not know: the
# stage door lets you out onto the square and never in. (A place a Stray door
# may open onto needs a way out on foot; so does one the repainter can shut.)
T = 48
TSEAT = dict(SEAT, floor=T + 16)
ajarmap.fitted(m, (-176, -976, 336, -656), [
    ((48, -976, 112, -656), ajarmap.RUNNER),
    ((-144, -720, -48, -688), TSEAT), ((208, -720, 304, -688), TSEAT),
], rug="AJ3R1", lite="AJ3L1", lift=0, floor=T, ceil=T + 176, light=180, **FOYER)
recess((-176, -944), (-176, -880), (-1, 0), T, far_id(RED), 101, far_colour=RED)
ajarmap.opening(m, (16, -656), (80, -656), (0, 1), T)                        # the stage door: a drop into the square
ajarmap.opening(m, (48, -976), (112, -976), (0, -1), T)
# the house: stalls, and the stage at the far end
STAGE = dict(floor=T + 48, ftex="AJBOARD", side="AJWOOD")
ajarmap.fitted(m, (-304, -1504, 464, -992), [
    ((16, -1056, 144, -992), dict(ceil=T + 128, ctex="AJ3E1")),              # under the circle, coming in
    ((-240, -1152, -48, -1120), TSEAT), ((208, -1152, 400, -1120), TSEAT),   # rows
    ((-240, -1248, -48, -1216), TSEAT), ((208, -1248, 400, -1216), TSEAT),
    ((16, -1344, 144, -1312), dict(STAGE, floor=T + 24)),                    # steps up
    ((-304, -1504, 464, -1344), STAGE),
], floor=T, ceil=T + 336, light=170, **STALLS)
ajarmap.fitted(m, (-112, -1776, 272, -1520), [
    ((80, -1744, 208, -1712), dict(WOOD, floor=T + 48 + 32)),                # a dressing table
], floor=T + 48, ceil=T + 48 + 128, light=165, **BACKSTAGE)
ajarmap.opening(m, (48, -1504), (112, -1504), (0, -1), T + 48)

# === the museum, on the square: one lock ===========================================
ajarmap.fitted(m, (-1168, -640, -528, -128), [
    ((-592, -432, -528, -304), low()),                                       # inside its door
    ((-1168, -464, -1104, -336), low()),                                     # before the way down
    ((-932, -192, -804, -128), low()),                                       # before the gallery
    ((-960, -480, -832, -352), dict(ftex="AJ6XP", side="AJ6XP", floor=32)),  # a plinth
    ((-720, -608, -592, -576), SEAT),
], floor=0, ceil=256, light=175, **MUSEUM)
ajarmap.roomdoor(m, (-512, -400), (-512, -336), (-1, 0), 0, keys="1", line_id=301)
# the cellar: you drop in with what you carry, and leave by a hole no door fits through
ajarmap.fitted(m, (-1600, -560, -1184, -112), [
    ((-1440, -400, -1344, -304), dict(ftex="AJWOOD", side="AJWOOD", floor=-128 + 48)),   # crates
    ((-1280, -208, -1216, -144), dict(ftex="AJWOOD", side="AJWOOD", floor=-128 + 48)),
], floor=-128, ceil=128, light=140, **CELLAR)
ajarmap.opening(m, (-1168, -432), (-1168, -368), (-1, 0), 0)
recess((-1600, -368), (-1600, -304), (-1, 0), -128, 114, 201)                # the cellar's frame
ajarmap.stairs(m, (-1560, -112), (-1496, -112), (0, 1), -128, 128, ceil=128, light=140, **CELLAR)
m.sector(rect(-1560, 144, -1496, 208), floor=0, ceil=128, light=150, **CELLAR)
ajarmap.squeeze(m, (-1496, 152), (-1496, 200), (1, 0), 0)
# the gallery
ajarmap.fitted(m, (-1480, -96, -720, 400), [
    ((-1320, 64, -1192, 192), dict(ftex="AJ6VT2", side="AJ6V2", floor=40)),  # cases
    ((-1000, 64, -872, 192), dict(ftex="AJ6VT2", side="AJ6V2", floor=40)),
    ((-784, 256, -720, 384), SEAT),
], floor=0, ceil=192, light=180, **GALLERY)
ajarmap.opening(m, (-900, -128), (-836, -128), (0, 1), 0, thick=32)
# PINK's store (secret), seen through bars: ring its bell. PINK leans in it
m.sector(rect(-1320, 416, -1000, 480), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(-1320, 480, -1000, 640), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (-1260, 400), (-1196, 400), (0, 1), 0, STORE, line_id=306)
ajarmap.unbolt(m, (-1320, 480), (-1000, 480), STORE)
bars((-1100, 400), (-1036, 400), (0, 1), 0)
m.cut((-1100, 640), (-1036, 640))
m.line((-1100, 640), (-1036, 640), special=11, args=(STORE, 32), impact=True, mid="AJTARG", exact=True)

# === the depot (YELLOW's far side), beyond the lane ================================
BUSES = dict(ftex="AJSTEEL", side="AJBUS", floor=D + ajarmap.BUS_H)          # the ones that are only buses
ajarmap.fitted(m, (-512, 192 + DY, 512, 640 + DY), [
    ((-448, 384 + DY, -128, 512 + DY), BUSES), ((128, 448 + DY, 448, 576 + DY), BUSES),
    ((-64, 576 + DY, 64, 640 + DY), dict(WOOD, floor=D + 48)),
    ((176, 576 + DY, 336, 640 + DY), low(D + 32)),                           # under the hole from PINK's room
    ((-64, 192 + DY, 64, 256 + DY), low(D)),                                 # over YELLOW's far side
], floor=D, light=NIGHT, ftex="AJSTEEL", **OPEN)
recess((-32, 192 + DY), (32, 192 + DY), (0, -1), D, far_id(YELLOW), 101, far_colour=YELLOW)
# the gate: out to the lane behind the bus, a step down, and never in. It takes
# a door through: with a hole for empty hands only, whoever carried YELLOW in
# here had shut the depot for good (the solver)
ajarmap.opening(m, (432, 192 + DY), (496, 192 + DY), (0, -1), D, thick=96)
# PINK's room (secret), over the depot: the third frame of the long way out
ajarmap.way_longer(m, 96, 720 + DY, PINK, BLUE, VIOLET, floor=PF)
m.sector(rect(224, 640 + DY, 288, 720 + DY), floor=PF, ceil=PF + 96, light=150, wall="AJBRICK",
         ftex="AJTRIMF", ctex="AJTRIMF")

# === the observatory (line 8) ======================================================
ajarmap.fitted(m, (1600, 1000, 2112, 1384), [
    ((1824, 1000, 1888, 1384), dict(ftex="AJ7P3")),
    ((1632, 1160, 1760, 1224), dict(ftex="AJ7WD3", side="AJ7LB3", floor=96)),            # stacks
    ((1952, 1160, 2080, 1224), dict(ftex="AJ7WD3", side="AJ7LB3", floor=96)),
], floor=0, ceil=192, light=175, **LIBRARY)
ajarmap.doorway(m, 3, *north[1], (0, -1), 0, (1824, 1000), (1888, 1000), (0, -1), 0)
# the dome: its floor is sunk. The door lets onto a ledge; you drop in with what
# you carry and leave by stairs and a hole no door fits through, as in the
# museum's cellar. So BLUE leaves through another door, hung in the dome's frame
PIT = -96
ajarmap.fitted(m, (1664, 1400, 2048, 1784), [
    ((1792, 1400, 1920, 1464), dict(floor=0, ftex="AJ7WD3", side="AJ7WD3")),             # the ledge inside the door
    ((1808, 1544, 1904, 1640), dict(ftex="AJSTEEL", side="AJ7DP3", floor=PIT + 64)),     # the pier
], floor=PIT, ceil=320, light=165, **DOME)
ajarmap.roomdoor(m, (1824, 1384), (1888, 1384), (0, 1), 0, keys="2", line_id=302)
recess((2048, 1560), (2048, 1624), (1, 0), PIT, 116, 201)                    # the dome's frame
ajarmap.stairs(m, (1664, 1700), (1664, 1764), (-1, 0), PIT, 96, steps=6, ceil=160, light=150, **DOME)
m.sector(rect(1408, 1700, 1472, 1764), floor=0, ceil=128, light=150, **LIBRARY)
ajarmap.squeeze(m, (1416, 1700), (1464, 1700), (0, -1), 0)
m.sector(rect(1408, 1320, 1472, 1684), floor=0, ceil=128, light=150, **LIBRARY)
m.sector(rect(1472, 1320, 1584, 1384), floor=0, ceil=128, light=150, **LIBRARY)
ajarmap.opening(m, (1600, 1320), (1600, 1384), (-1, 0), 0)

# --- doors and keys ----------------------------------------------------------
REPAINTER = 20007
m.thing(-64, -592, 1, angle=90)                                           # player start, in the square
ajarmap.door(m, RED, -2380, -100, angle=180)                              # leaning in a hotel room
ajarmap.door(m, YELLOW, 1750, 230, angle=0)                               # in the station's waiting room
ajarmap.door(m, GREEN, 424, -1466, angle=180)                            # on the stage
ajarmap.door(m, VIOLET, -1210, -536, angle=180)                           # in the museum's cellar
ajarmap.door(m, BLUE, 2020, 1756, angle=180)                              # under the dome
ajarmap.door(m, PINK, -1300, 616, angle=0)                                # in its store
m.thing(100, -150, REPAINTER, angle=180)                                   # the repainter: about the stop
ajarmap.stray(m, -492, -68, angle=0)                                      # Stray doors: by the bus
ajarmap.stray(m, -156, -956, angle=0)                                     # in the theatre's foyer
ajarmap.stray(m, -740, -80, angle=180)                                    # in the museum's gallery
ajarmap.stray(m, 492, 620 + DY, angle=180)                                     # in the depot
ajarmap.key(m, 1, -76, -1656)                                              # behind the stage
ajarmap.key(m, 2, -470, 600 + DY)                                              # the far corner of the depot

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACHNO, PAIN = 65, 69, 3003, 66, 3006, 3005, 67, 68, 71
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
BACKPACK = 8


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the square: lamps, and those who live in the bus's empty frames
things(LAMP, (-480, -80), (192, -80), (-480, -608), (192, -608), (480, -80), (-616, 424), (616, 424))
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
# the hotel: the night staff, and guests
things(ZOMBIE, (-3100, -200), (-2800, -300), (-2760, -150), (-2944, -80), angle=270)
things(SERGEANT, (-3130, -330), (-2760, -340), angle=270)
things(IMP, (-3000, -40), (-2840, -100), angle=270)
things(BACKPACK, (-3130, -150))
things(SHELLS, (-2880, -360), (-3010, -360))
things(STIM, (-2720, -360), (-3170, -40))
things(TECHLAMP, (-3176, -376), (-2712, -376))
things(IMP, (-2500, -120), (-2620, -300), angle=180)
things(CHAINGUNNER, (-2400, -160), angle=180)
things(CHAINGUN, (-2620, -110))
things(AMMOBOX, (-2580, -110))
things(DEMON, (-3300, -300), (-3400, -120), angle=0)
things(SERGEANT, (-3500, -110), angle=0)
things(ARMOR, (-3500, -180))
things(MEDIKIT, (-3250, -310))
# the station: the concourse
things(SERGEANT, (1700, -200), (2000, -250), (2180, -60), angle=270)
things(IMP, (1660, -340), (1840, -160), (2040, -340), (1760, -40), angle=270)
things(CHAINGUNNER, (2000, -330), (1640, -50), angle=270)
things(KNIGHT, (1920, -120), angle=270)
things(SHELLBOX, (2200, -150))
things(MEDIKIT, (1640, -150))
things(STIM, (2000, -60))
things(TECHLAMP, (1624, -376), (2216, -376))
# its waiting room: YELLOW
things(REVENANT, (1920, 130), angle=270)
things(IMP, (1800, 60), (2070, 200), angle=270)
things(SHELLS, (2080, 30))
things(MEDIKIT, (1760, 30))
# its platform
things(MANCUBUS, (1360, -120), angle=0)
things(CACO, (1240, -80), (1480, -60), angle=0, ambush=True)
things(SOUL, (1300, -280), (1440, -260), angle=0)
things(LAUNCHER, (1200, -360))
things(ROCKETBOX, (1200, -50), (1250, -50))
things(SPHERE, (1500, -360))
things(LAMP, (1560, -40), (1176, -376))
# the theatre: the foyer
things(IMP, (-106, -856), (264, -856), (80, -916), angle=90)
things(SERGEANT, (-26, -756), (194, -756), angle=90)
things(DEMON, (-76, -946), (244, -946), angle=90)
things(SHELLBOX, (304, -946))
things(STIM, (-146, -756))
# the house and the stage
things(SUPER, (80, -1176))
things(SHELLS, (40, -1176), (120, -1176))
things(IMP, (-266, -1076), (424, -1076), (-266, -1286), (424, -1286), angle=90)
things(KNIGHT, (-16, -1276), (174, -1276), angle=90)
things(SPECTRE, (-176, -1186), (324, -1186), angle=90)
things(CHAINGUNNER, (-176, -1416), (324, -1416), angle=90)
things(CACO, (80, -1416), angle=90, ambush=True)
things(MEDIKIT, (-276, -1466), (434, -1036))
things(BERSERK, (-276, -1036))
things(ROCKETS, (-76, -1466), (-36, -1466))
# behind the stage: key 1
things(BARON, (174, -1636), angle=0)
things(IMP, (240, -1600), angle=0)
things(MEDIKIT, (244, -1556))
things(SHELLBOX, (-76, -1556))
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

# --- ambushes: what a key or a door brings (ajarmap.ambush) -------------------
# The square is where they come: an arena that fills from its own stop.
# GREEN, taken from the stage: the house
ajarmap.ambush(m, 10 + GREEN, REVENANT, (80, -1106), angle=270)
ajarmap.ambush(m, 10 + GREEN, IMP, (-126, -1076), (284, -1076), angle=270)
# key 1, behind the stage: the square you go back to
ajarmap.ambush(m, 1, KNIGHT, (-300, -250), (100, -250), angle=270)
ajarmap.ambush(m, 1, IMP, (-420, -500), (160, -500), (-100, -120), angle=90)
# VIOLET, taken in the cellar
ajarmap.ambush(m, 10 + VIOLET, SPECTRE, (-1300, -200), (-1500, -420), angle=0)
# key 2, in the depot: the square again
ajarmap.ambush(m, 2, CACO, (-200, -300), (0, -450), angle=90)
ajarmap.ambush(m, 2, REVENANT, (-380, -150), angle=0)
ajarmap.ambush(m, 2, IMP, (-540, 320), (540, 320), angle=270)             # and the lane behind the bus
# BLUE, taken under the dome: the library you go back through
ajarmap.ambush(m, 10 + BLUE, REVENANT, (1730, 1100), (1980, 1100), angle=90)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "main" is the square all round the bus, the hotel, the station, the
# observatory's library (lines 1, 5 and 8 always run) and the kiosk; "museum"
# its hall, gallery and PINK's store; "night" is the line, "pink" PINK's room.
PUZZLE = dict(
    start="main", goal="exit", names=ajarmap.NAMES, complete=True,
    home_chain=dict(frames=[HOME, HOME2], doors=[BLUE, VIOLET], secret=dict(frame=HOME3, door=PINK)),
    walk=[("main", "museum", "1"), ("museum", "main", "1"),
          ("museum", "cellar"), ("cellar", "museum", "", "squeeze"),      # down the hole; up the stairs and out
          ("depot", "main"),                                              # the gate, a step down
          ("main", "dome", "2"), ("dome", "main", "", "squeeze"),         # down off the ledge; up the stairs and out
          ("theatre", "main"),                                            # the stage door
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
    only={HOME3: (BLUE, VIOLET)},
    repainter=dict(zone=["main"]),
    pool=["main"],                         # door 4 of the bus; the kiosk; the platform
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
