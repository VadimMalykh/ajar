"""Act 2, level 6: "Watch Your Step" (MAP16). It wears MAP11's look (AJAR_INSTITUTE).

Rebuilt after Vadim played it (2026-11-20): the well is closed. Four floors,
each a wing walked through, and the way down from each is at its far end:
the top, the labs, the canteen, the base. A drop once opened stays open.

The endless stair is still the spine: a TEAL Pair whose one leaf (the head)
is part of the building, in a sealed lobby on the top floor; the other leaf
is the player's. Hung at the foot, in the base, the stair goes round.

Places. The top: the reading room (the start; the leaf; stacks), and beside
it the head lobby, sealed: the head, a weighbridge in front of it, and a
heavy shutter to the test hall (off its south-east corner, at floor level,
the corridor to the night room's brass frame, which takes VIOLET only).
Glass lets the reading room see into the lobby; the door between them opens
from the lobby's side only. From the test hall a hatch
drops to the labs (whoever comes in by VIOLET's far side gets out again).
The labs (second floor): the room that is its own neighbour. A hall cut in
two by a trench with bars on both sides: shots and sight cross, nobody
walks. GREEN leans in the south half, frame 102 is in the south wall and
GREEN's far side in the north wall: out south, in north, and through the
door you see your own back. The drop to the canteen is off the north half.
The canteen (first floor): the room over itself. RED leans there, frame 101
is in its west wall, and RED's far side is on the gallery above the room.
On the gallery a lever opens the shutter to the drop to the base, for good,
and a panel in its west wall is the secret (blue armour). The base: the
foot (frame 104) in the boiler room's south wall; the den behind bars,
raised, with frame 105 (a TEAL leaf only) and VIOLET; a hole (empty hands)
to the cubby, whose doorway of the building's goes up to the lobby.

Company. The porter, a thief that takes the TEAL leaf only and only while
it sees the player, from any frame but its own, and always hangs it in the
den's frame (its args[2]); killed, another comes out of the den 30 seconds
later. Only it passes the staff stair into the den (its top step 54 high: the player and
every Doom monster are 56 or more).

The weighbridge (AjarWeighbridge, map16.zs) weighs what stands or lies on
its plate: the player 100, live monsters and dead ones' bodies by their
Mass. While the total is 1000 or more the test hall's shutter goes up; when
it falls below, the shutter comes down again (never on anyone). A body of
1000 or more lying on the plate (a dead baron) holds it up for good. A dial
on the lobby's east wall beside the head shows the total in tenths up to a
red mark, and a glass case in the reading room's north wall, by the window,
shows it solved: a baron lying dead on the plate, the dial at the mark.
Its baron stands on the canteen's gallery from the start, on every skill;
20 seconds after each that dies another comes there, announced, until the
weighbridge holds a body. It is dogged: seeing the player on the canteen
floor below it does not give up a door it is making for.

So: RED hung in the canteen's frame, up through it to the gallery with the
leaf, and down through RED again with the baron behind; in the canteen RED
swapped out of the frame for the leaf, and through the leaf to the lobby:
the baron follows and comes out of the head onto the weighbridge, and the
shutter goes up while it stands there. Killed on the plate, its body holds
the shutter up. (The same from any floor's frame: RED hung in the labs' or
at the foot, swapped there for the leaf.) Then the leaf to the foot; the
porter carries it to the den, and the head opens into the den. By the hole
and the cubby up to the lobby, through the head, VIOLET out to the lobby and
into the brass frame.

Nothing as heavy as a baron (a hell knight, a mancubus) is anywhere but the
gallery and the test hall: one coming through the head would hold the
shutter up as well while it stood on the plate.

In the PUZZLE graph the leaf is a plain door whose far side is the lobby,
which is what a Pair with one leaf fixed is.

Secret: the panel on the canteen's gallery.
"""
import ajarmap
import ajartime
import map_institute1 as I1
from ajarmap import RED, GREEN, VIOLET, TEAL, far_id, HOME
from map_institute1 import T, dress, tint, over, named, hang, things, frame, LOOK, FACES
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, REVENANT, CACO
from udmf import Map, rect

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED
Z1, Z2, Z3 = 128, 256, 384                  # the first floor, the second, the top
DEN_Z = 40                                  # the den's floor: a step nobody climbs
H = 256                                     # every room's height but those named
PALE, RUST, COLD, STEEL, DIM, PAPER = 0xDCE8DC, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8, 0xF0E4C8
HEAD, FOOT, DEN, LABS, CANTEEN = 110, 104, 105, 102, 101    # frames
THIEF, WEIGHBRIDGE_T, WEIGH_DIAL_T = 20003, 20070, 20071
DIAL_AT = (1166, -1912)                     # the weighbridge's dial: 2 off the lobby's east wall
BARON = 3003
ARACHNO = 68
LEAF = ajarmap.LEAVES[TEAL][1]              # the player's leaf, in the PUZZLE graph
# sector tags: the lobby, its weighbridge, the test hall's shutter, the bolted
# door into the reading room, the canteen's shutter to the base
LOBBY, PLATE, TEST_SHUTTER, LOBBY_DOOR, BASE_SHUTTER = 616, 618, 617, 615, 614
BARON_SPOT = 16                             # the MapSpot on the gallery where the baron stands


def box(base, height, top="BT", side=None, **k):
    return dict(I1.box(height, top, side, **k), floor=base + height)


def solid(base, part, height=H):            # to the ceiling: a pillar, a stack, a tank
    return dict(floor=base + height, **dress(side=part))


def table(base=0):
    return dict(floor=base + 32, ftex=T("TT"), side=T("TS")) if LOOK else box(base, 48)


def way(a, b, out, floor, near, far, words="", color=None):
    """An open way on any floor (MAP11's opening() is for the ground)."""
    ajarmap.opening(m, a, b, out, floor, color=tint(color))
    over(a, b, near)
    over(*I1._far(a, b, out), far)
    named(a, b, out, near, words)


def door_faces(a, b, out, near, far, words="", keys=""):
    """In a look: a door's two faces, the wall of each side over the leaf (MAP14's)."""
    if LOOK:
        c, d = I1._far(a, b, out)
        for (p, q), o, part, s in (((a, b), out, near, words), ((c, d), (-out[0], -out[1]), far, "")):
            key = (LOOK, part, I1._shift(p, q, o), keys, s)
            m.line(p, q, upper=FACES.setdefault(key, f"AJID{LOOK}{len(FACES):02d}"))


def shut(a, b, out, floor, tag, thick=16):
    """A shutter that something else opens for good (Door_Open on `tag`):
    no handle on either side."""
    c, d = (a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF", id=tag)
    for p, q in ((a, b), (c, d)):
        m.line(p, q, exact=True)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


GLASS = dict(mid="AJGLAS", midboth=True, blocking=True, blockhitscan=True, blockprojectiles=True)
BARS = dict(mid="AJGRIL", midboth=True, blocking=True, wrapmidtex=True)


# --- the top: the reading room ------------------------------------------------------------
STACK = solid(Z3, "SK")
ajarmap.fitted(m, (0, -2560, 768, -1664), [
    ((96, -2432, 160, -2240), STACK), ((224, -2432, 288, -2240), STACK),
    ((480, -2432, 544, -2240), STACK), ((608, -2432, 672, -2240), STACK),
    ((96, -2048, 160, -1856), STACK), ((224, -2048, 288, -1856), STACK),
    ((480, -2048, 544, -1856), STACK), ((608, -2048, 672, -1856), STACK),
    ((320, -2176, 448, -2112), box(Z3, 40, "DT", "DS")),                    # the librarian's desk
], floor=Z3, ceil=Z3 + H, light=200, color=tint(PALE), **dress(wall="LB", ftex="FL", ctex="KL"))
hang((64, -2560), (192, -2560), "CI")                                       # card indexes, behind the start
hang((576, -2560), (704, -2560), "CI")
hang((0, -2368), (0, -2240), "NB")                                          # notices: quiet, please
# the stair head: the flights are gone, and the labs are a drop below
way((224, -1664), (288, -1664), (0, 1), Z3, "LB", "EV", "STAIRS")
m.sector(rect(192, -1648, 320, -1600), floor=Z3, ceil=Z3 + 160, light=170, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
m.sector(rect(192, -1600, 320, -1440), floor=Z2, ceil=Z3 + 160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))

# --- the head lobby: sealed. The head, the weighbridge, the test hall's shutter ------------
ajarmap.fitted(m, (784, -2240, 1168, -1856), [
    ((1040, -2112, 1168, -1984), dict(id=PLATE, **(dress(ftex="PT") if LOOK else dict(ftex="AJTRIMF")))),
], floor=Z3, ceil=Z3 + H, light=190, color=tint(STEEL), id=LOBBY, **dress(wall="EX", ftex="FE", ctex="KE"))
frame((1168, -2080), (1168, -2016), (1, 0), HEAD, STEEL, floor=Z3)
named((1168, -2080), (1168, -2016), (1, 0), "EX", "WEIGHBRIDGE")
hang((1168, -2176), (1168, -2112), "WS")                                    # a warning beside it
# the door to the reading room: bolted on the lobby's side
ajarmap.bolted(m, (768, -2208), (768, -2144), (1, 0), Z3, LOBBY_DOOR, line_id=315)
door_faces((768, -2208), (768, -2144), (1, 0), "LB", "EX")
# the glass: the reading room sees the leaf, the weighbridge, the shutter
m.sector(rect(768, -2016, 784, -1888), floor=Z3 + 32, ceil=Z3 + 160, light=190, wall="AJTRIM",
         ftex="AJTRIMF", ctex="AJTRIMF")
for x in (768, 784):
    m.line((x, -2016), (x, -1888), **GLASS)
# the shutter to the test hall: opened by the weighbridge, from neither side
shut((944, -1856), (1008, -1856), (0, 1), Z3, TEST_SHUTTER)
named((944, -1856), (1008, -1856), (0, 1), "EX", "TEST HALL")
m.thing(1104, -2048, WEIGHBRIDGE_T, args=(PLATE, TEST_SHUTTER, LOBBY, BARON_SPOT, 20))
# its dial, on the east wall north of the head: seen from the plate, the door and through the glass
m.thing(DIAL_AT[0], DIAL_AT[1], WEIGH_DIAL_T, angle=180, height=40.0)

# --- the test hall, and the night room beyond --------------------------------------------------
PLATFORM = box(Z3, 64, "PT", "PS")
ajarmap.fitted(m, (784, -1840, 1232, -1456), [
    ((960, -1712, 1088, -1584), solid(Z3, "MC")),                            # the machine
    ((1104, -1776, 1232, -1712), PLATFORM), ((1104, -1520, 1232, -1456), PLATFORM),
], floor=Z3, ceil=Z3 + H, light=180, color=tint(STEEL), **dress(wall="EX", ftex="FE", ctex="KE"))
hang((784, -1776), (784, -1648), "CP")                                       # the desk it was run from
# the hatch: a drop into the labs, for whoever came in by VIOLET's far side
m.sector(rect(816, -1456, 880, -1440), floor=Z2, ceil=Z3 + 96, light=150, wall="AJTRIM", ftex="AJTRIMF",
         ctex="AJTRIMF", color=tint(STEEL))
m.sector(rect(1232, -1840, 1440, -1792), floor=Z3, ceil=Z3 + 160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
m.sector(rect(1376, -1792, 1440, -1776), floor=Z3, ceil=Z3 + 160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
over((1232, -1840), (1232, -1792), "EX")
ajarmap.way_home(m, 1328, -1776, VIOLET, only=True, floor=Z3)

# --- the labs: the room that is its own neighbour -------------------------------------------
TRENCH = (-1136, -1104)
ajarmap.fitted(m, (144, -1440, 912, -800), [
    ((272, -1344, 400, -1280), box(Z2, 48)), ((656, -1344, 784, -1280), box(Z2, 48)),
    ((272, -1008, 400, -944), box(Z2, 48)), ((656, -1008, 784, -944), box(Z2, 48)),
    ((144, TRENCH[0], 912, TRENCH[1]), dict(floor=Z2 - 64, **dress(ftex="FP"))),
], floor=Z2, ceil=Z2 + H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
for y in TRENCH:
    m.line((144, y), (912, y), **BARS)
hang((144, -1056), (144, -928), "BB")                                       # a blackboard, in the north half
hang((912, -1408), (912, -1280), "CB")                                      # cabinets, in the south half
frame((496, -1440), (560, -1440), (0, -1), LABS, RUST, floor=Z2)
ajarmap.recess(m, (496, -800), (560, -800), (0, 1), Z2, far_id(GREEN), FOOT, far_colour=GREEN, color=tint(RUST))
# the side labs: west off the south half, east off the north half
ajarmap.fitted(m, (-208, -1440, 128, -1152), [
    ((-144, -1376, -48, -1280), box(Z2, 64)), ((-144, -1248, -16, -1216), box(Z2, 48)),
], floor=Z2, ceil=Z2 + H, light=160, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
way((128, -1344), (128, -1280), (1, 0), Z2, "LA", "LA")
ajarmap.fitted(m, (928, -1104, 1264, -800), [
    ((1104, -1040, 1200, -944), box(Z2, 96)), ((992, -864, 1120, -832), box(Z2, 48)),
], floor=Z2, ceil=Z2 + H, light=160, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
way((912, -992), (912, -928), (1, 0), Z2, "LA", "LA")
# the drop to the canteen, off the north half
m.sector(rect(784, -800, 848, -704), floor=Z1, ceil=Z1 + H, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
named((784, -800), (848, -800), (0, 1), "LA", "CANTEEN", oh=128)

# --- the canteen: the room over itself ------------------------------------------------------
GALLERY = dress(ftex="GT", side="GF") if LOOK else dict(side="AJTRIM")
ajarmap.fitted(m, (144, -704, 912, -80), [
    ((272, -576, 400, -512), table(Z1)), ((528, -576, 656, -512), table(Z1)),
    ((272, -448, 400, -384), table(Z1)), ((528, -448, 656, -384), table(Z1)),
    ((144, -208, 912, -80), dict(floor=Z2, **GALLERY)),
], floor=Z1, ceil=Z1 + H, light=200, color=tint(PAPER), **dress(wall="CA", ftex="FN", ctex="KC"))
if LOOK:                                                                    # under the gallery: the canteen's own wall
    m.line((144, -208), (912, -208), lower=T("CA"), dontpegbottom=True)
hang((400, -704), (528, -704), "MN")                                        # the menu
frame((144, -640), (144, -576), (-1, 0), CANTEEN, PAPER, floor=Z1)
ajarmap.recess(m, (496, -80), (560, -80), (0, 1), Z2, far_id(RED), FOOT, far_colour=RED, color=tint(PAPER))
# the lever on the gallery: the shutter to the drop to the base goes up for good
m.cut((704, -80), (768, -80))
m.line((704, -80), (768, -80), special=11, args=(BASE_SHUTTER, 32), playeruse=True, exact=True, id=320,
       mid=T("CL") if LOOK else "AJLEVR")
# the secret: a panel in the gallery's west wall (its wall is the storey
# below's, out of line with the rest), and a closet behind it
m.sector(rect(32, -208, 128, -80), floor=Z2, ceil=Z2 + 128, light=120, color=tint(PAPER), special=1024,
         **dress(wall="CK", ftex="FC", ctex="KC"))
m.sector(rect(128, -176, 144, -112), floor=Z2, ceil=Z2, light=160, wall=T("CA") if LOOK else "AJWALL",
         ftex="AJTRIMF", ctex="AJTRIMF")
m.line((144, -176), (144, -112), special=11, args=(0, 32), playeruse=True, exact=True, id=321,
       **(dict(upper=T("CA")) if LOOK else {}))
# the kitchen, east
ajarmap.fitted(m, (928, -704, 1312, -320), [
    ((1056, -640, 1184, -576), box(Z1, 48)), ((1248, -704, 1312, -448), box(Z1, 48)),
], floor=Z1, ceil=Z1 + 160, light=180, color=tint(PAPER), **dress(wall="CK", ftex="FC", ctex="KC"))
way((912, -544), (912, -480), (1, 0), Z1, "CA", "CK", "KITCHEN")
# the shutter to the drop to the base, and the landing over it
shut((144, -480), (144, -416), (-1, 0), Z1, BASE_SHUTTER)
named((144, -480), (144, -416), (-1, 0), "CA", "STAIRS")
m.sector(rect(64, -512, 128, -384), floor=Z1, ceil=Z1 + 128, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))

# --- the base: the boiler room and the foot; the den; the cubby -------------------------------
TANK = solid(0, "TK", 224)
ajarmap.fitted(m, (-1024, -768, -128, -192), [
    ((-896, -640, -800, -544), TANK), ((-352, -640, -256, -544), TANK),
    ((-896, -416, -800, -320), TANK), ((-352, -416, -256, -320), TANK),
], floor=0, ceil=224, light=130, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
frame((-608, -768), (-544, -768), (0, -1), FOOT, COLD)
hang((-1024, -704), (-1024, -576), "GA")                                    # gauges
# the foot of the flights that are gone: a drop from the canteen's landing
m.sector(rect(-128, -512, 64, -384), floor=0, ceil=Z1 + 128, light=140, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
# the den, raised behind bars, and the staff stair into it (its top step 54 high)
DEN_LOOK = dict(ceil=DEN_Z + 128, light=120, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
m.sector(rect(-768, -192, -624, -112), floor=DEN_Z, **DEN_LOOK)
m.sector(rect(-528, -192, -384, -112), floor=DEN_Z, **DEN_LOOK)
m.sector(rect(-768, -112, -384, 96), floor=DEN_Z, **DEN_LOOK)
m.cut((-704, -192))
m.line((-704, -192), (-624, -192), **BARS)
m.line((-528, -192), (-384, -192), **BARS)
for i, (y1, y2) in enumerate(((-192, -176), (-176, -160), (-160, -144), (-144, -112))):
    # only the top step, level with the den, is low (54): so the porter in the den sees down the stair
    m.sector(rect(-608, y1, -544, y2), floor=10 * (i + 1), ceil=DEN_Z + 54 if i == 3 else 160, light=110, color=tint(DIM),
             **dress(wall="AR", ftex="FR", ctex="KA"))
m.line((-608, -192), (-544, -192), blockplayers=True)                       # only the porter: see the docstring
named((-608, -192), (-544, -192), (0, 1), "PU", "STAFF", oh=62)
frame((-608, 96), (-544, 96), (0, 1), DEN, DIM, floor=DEN_Z, home=TEAL, only=3)
# the hole, and the cubby behind it: a doorway of the building's up to the lobby
m.sector(rect(-1232, -608, -1040, -384), floor=0, ceil=128, light=120, color=tint(DIM),
         **dress(wall="AR", ftex="FR", ctex="KA"))
I1.squeeze((-1024, -520), (-1024, -472), (-1, 0), 0, "PU", "AR", "HATCH")
ajarmap.doorway(m, 1, (-1232, -528), (-1232, -464), (-1, 0), 0, (880, -2240), (944, -2240), (0, -1), Z3)

# --- doors ---------------------------------------------------------------------------------
m.thing(1140, -2048, ajarmap.DOOR_T, args=(0, TEAL, HEAD, 1, TEAL))          # the head's leaf: part of the building
m.thing(384, -2080, ajarmap.DOOR_T, angle=270, args=(0, TEAL, 0, 0, TEAL))   # the player's, by the librarian's desk
ajarmap.door(m, GREEN, 700, -1400, angle=90)
ajarmap.door(m, RED, 820, -650, angle=180)
ajarmap.door(m, VIOLET, -720, 40, angle=0)

# --- the reading room: the start -------------------------------------------------------------
m.thing(384, -2500, 1, angle=90)
m.thing(384, -2420, 2001)                                                   # shotgun
things(2008, (330, -2420), (440, -2420))
m.thing(720, -2500, 2002)                                                   # chaingun
things(2048, (720, -2440), (40, -2500))
things(ZOMBIE, (60, -2300), (192, -2300), (580, -2300), (710, -2300), (330, -2010), (60, -1950), (192, -1950),
       (580, -1950), angle=90)
things(SERGEANT, (192, -2150), (580, -2150), (384, -1800), (60, -1720), (710, -1720), angle=270)
things(IMP, (60, -2150), (710, -2150), (192, -1760), (580, -1760), (420, -1900), (330, -1900),
       (720, -1950), (40, -2050), angle=270)
things(CHAINGUNNER, (250, -1720), (520, -1720), angle=270)
things(DEMON, (384, -2300), (384, -1960), angle=270)
things(IMP, (320, -2240), (450, -2240), angle=90)
m.thing(650, -1820, CACO, angle=270)
things(2011, (40, -2400), (720, -2400))
things(2012, (720, -1800))
things(2049, (40, -1800), (560, -2120))
m.thing(200, -2120, 2018)                                                   # green armour

# the glass case in the reading room's north wall, by the window onto the
# lobby: the weighbridge solved (a baron lying dead on the plate, the dial at the mark).
# No time doors in this level: no plaque, and the glass framed as the window.
CASE_A, CASE_B, CASE_DEEP = (576, -1664), (736, -1664), 96
CASE = ajartime.case(m, CASE_A, CASE_B, (0, 1), Z3, deep=CASE_DEEP, light=220, color=tint(STEEL), plaque=False,
                     trim=("AJTRIM", "AJTRIMF"), **dress(wall="EX", ftex="FE", ctex="KE"))
CASE_FIGURES = [(648, -1606, "plate", 0, 270), (648, -1606, "body", BARON, 270), (704, -1554, "dial", 0, 270)]
for x, y, what, kind, ang in CASE_FIGURES:
    r = 1 if what == "dial" else 8
    assert CASE_A[0] + r < x < CASE_B[0] - r and CASE_A[1] + 16 + r < y < CASE_A[1] + 16 + CASE_DEEP - r, (x, y, what)
    ajartime.figure(m, x, y, what, kind=kind, angle=ang, scale=0.6 if what == "dial" else None)
assert ajartime.sealed(m, CASE), "the glass case is not sealed"

# --- the test hall: shut in until the shutter goes up -----------------------------------------
things(REVENANT, (1168, -1744), (1168, -1488), angle=270)                   # on the platforms
things(IMP, (830, -1800), (1040, -1810), (880, -1620), (1160, -1640), angle=270)
things(KNIGHT, (900, -1700), (1040, -1760), angle=270)
m.thing(1024, -1500, CACO, angle=270)
things(IMP, (830, -1530), (920, -1530), angle=270)
things(2046, (830, -1700), (1190, -1580))
things(2012, (1020, -1780))
things(17, (1300, -1816))

# --- the labs ------------------------------------------------------------------------------------
m.thing(500, -1380, 82)                                                     # super shotgun
things(IMP, (200, -1400), (840, -1300), (460, -1200), (600, -1200), (200, -1180), (720, -1400), angle=90)
things(DEMON, (336, -1220), (720, -1220), angle=90)
things(SERGEANT, (450, -1330), (600, -1400), (230, -1250), angle=90)
m.thing(820, -1190, CHAINGUNNER, angle=90)
things(IMP, (560, -1320), (880, -1200), angle=90)
m.thing(450, -1250, REVENANT, angle=90)
things(IMP, (-160, -1180), (60, -1420), (-180, -1420), angle=0)             # the west lab
m.thing(40, -1200, REVENANT, angle=0)
things(2049, (860, -1420))
things(2012, (-60, -1420))
things(2011, (180, -1420), (180, -1180))
# the north half: they fire across, and back
things(IMP, (200, -1060), (360, -1060), (520, -1060), (680, -1060), (840, -1060), (440, -860), angle=270)
things(CHAINGUNNER, (300, -900), (600, -900), angle=270)
things(REVENANT, (220, -860), (860, -900), angle=270)
m.thing(520, -960, CACO, angle=270)
things(IMP, (760, -860), (380, -900), angle=270)
m.thing(860, -980, SPECTRE, angle=270)
things(IMP, (980, -1060), (1220, -860), (1220, -1060), angle=180)            # the east lab
m.thing(1030, -960, ARACHNO, angle=180)
things(ZOMBIE, (1150, -880), (1150, -1080), angle=180)
things(2047, (960, -820), (1220, -940))
things(2012, (200, -840), (860, -840))
things(2048, (1220, -1080))

# --- the canteen ---------------------------------------------------------------------------------
m.thing(464, -640, 2003)                                                    # rocket launcher, between the tables
things(2046, (464, -600), (200, -680))
things(IMP, (200, -480), (720, -480), (200, -320), (720, -320), (464, -300), (840, -560), (330, -660), (600, -660),
       angle=0)
things(SERGEANT, (464, -480), (330, -340), (600, -340), (840, -300), angle=0)
things(REVENANT, (200, -260), (720, -260), (780, -640), angle=270)
things(DEMON, (464, -400), (820, -420), (210, -560), angle=270)
m.thing(860, -660, CHAINGUNNER, angle=90)
m.thing(720, -600, IMP, angle=0)
m.thing(200, -400, SERGEANT, angle=0)
things(2049, (190, -620))
things(2012, (860, -600))
things(2011, (190, -250), (464, -680))
m.thing(400, -470, 2023)                                                    # berserk, between the tables
# the gallery: the weighbridge's baron stands at its east end, over the
# canteen (AjarWeighbridge puts it on this spot, and each that comes after)
m.thing(840, -150, 9001, id=BARON_SPOT, angle=270)
things(IMP, (240, -140), (400, -140), (640, -140), (320, -110), angle=270)
m.thing(720, -110, CHAINGUNNER, angle=270)
things(2049, (200, -110))
things(2048, (620, -110))
m.thing(80, -144, 2019)                                                     # blue armour: the secret
things(2012, (60, -110))
# the kitchen
things(IMP, (990, -400), (1200, -400), (1000, -680), angle=180)
things(SERGEANT, (1120, -500), (1260, -360), angle=180)
m.thing(1100, -360, DEMON, angle=180)
m.thing(1120, -680, IMP, angle=180)
m.thing(1180, -500, SPECTRE, angle=180)
things(2012, (1260, -400))
things(2049, (960, -360))
m.thing(1200, -660, 2013)                                                   # a soul sphere, at the back

# --- the base -----------------------------------------------------------------------------------------
m.thing(-576, -40, THIEF, angle=270, args=(0, 1, DEN))                       # the porter, at its post in the den
things(SPECTRE, (-960, -720), (-700, -260), (-200, -720), angle=0)
things(IMP, (-960, -260), (-200, -260), (-960, -480), (-200, -470), angle=0)
things(DEMON, (-700, -480), (-450, -480), angle=0)
things(REVENANT, (-960, -600), (-200, -660), angle=90)
m.thing(-760, -620, CACO, angle=90)
things(IMP, (-640, -260), (-450, -260), angle=270)
m.thing(-300, -720, CHAINGUNNER, angle=90)
m.thing(-40, -440, SERGEANT, angle=180)                                     # at the foot of the flights
m.thing(-1000, -330, 2004)                                                  # plasma rifle
things(17, (-160, -330))
things(2012, (-160, -720), (-1100, -420))
things(2046, (-640, -330))
things(2011, (-1200, -580), (-1100, -580))

# --- ambushes ------------------------------------------------------------------------------------------
# VIOLET, taken: company in the boiler room. (The nailer came to the foot
# here, the first of the level's ambushers, until it went out of the game,
# 2026-11-28: its turn in the thinning is kept, so that those after it are
# there on the difficulties they were.)
m.ambushers = 0
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (-700, -580), (-450, -600), angle=90)
ajarmap.ambush(m, 10 + VIOLET, CACO, (-750, -400), (-400, -400), angle=90, after=3)
# the leaf, taken: the reading room
ajarmap.ambush(m, 10 + TEAL, IMP, (60, -2480), (710, -2480), angle=90)
ajarmap.ambush(m, 10 + TEAL, SERGEANT, (192, -2500), (580, -2500), angle=90, after=2)
# GREEN, taken: the labs' south half, and the north half
ajarmap.ambush(m, 10 + GREEN, SPECTRE, (336, -1400), (720, -1180), angle=90)
ajarmap.ambush(m, 10 + GREEN, IMP, (360, -880), (680, -880), angle=270, after=2)
# RED, taken: the canteen
ajarmap.ambush(m, 10 + RED, SPECTRE, (300, -300), (650, -300), angle=270)
ajarmap.ambush(m, 10 + RED, CACO, (464, -560), (780, -400), angle=0, after=3)

PUZZLE = dict(
    start="read", goal="exit", names={**ajarmap.NAMES, LEAF: "the TEAL leaf"}, complete=True, home_frame=HOME,
    walk=[("read", "labS"), ("labN", "canteen"), ("gallery", "canteen"),                 # the drops
          ("canteen", "base", "L"),                                                     # the shutter: the gallery's lever
          ("base", "cubby", "", "squeeze"), ("cubby", "base", "", "squeeze"),          # the hole
          ("cubby", "lobby"), ("lobby", "cubby"),                                       # the cubby's doorway
          ("lobby", "read", "b"), ("read", "lobby", "b"),                               # bolted on the lobby's side
          ("lobby", "test", "W"),                                                       # the shutter: the weighbridge
          ("test", "night"), ("night", "test"), ("test", "labS"),                       # the hatch to the labs
          ("den", "base")],                                                             # out of the den: a drop
    keys={"L": "gallery", "b": "lobby"},
    auto=("b",),                            # the bolt is drawn from the lobby
    frames={LABS: "labS", CANTEEN: "canteen", FOOT: "base", DEN: "den", HOME: "night"},
    only={HOME: VIOLET, DEN: (LEAF,)},
    doors={
        GREEN: dict(home="labN", lean="labS"),
        RED: dict(home="gallery", lean="canteen"),
        VIOLET: dict(home="night", lean="den"),
        LEAF: dict(home="lobby", lean="read"),                                          # its twin is fixed at the head
    },
    # the porter: it sees the base from the den, the cubby through the hole
    # and the canteen's landing from the foot of the flights
    thief=dict(zone="base", sees=["den", "cubby", "canteen"], takes=(LEAF,), into=DEN, watched=True, respawn=True),
    # the baron on the gallery: it follows the player through hung doors, and
    # out of the head it is on the weighbridge
    lures=[dict(home="gallery", to="lobby", key="W", name="baron")],
)
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
