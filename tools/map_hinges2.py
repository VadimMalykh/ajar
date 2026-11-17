"""Act 1, level 2: "No Vacancy" (MAP02).

A hotel, and the first level that is not one thing after another.

The ground floor is a place to walk about in: the lobby (reception desk,
boarded front doors), a hall of guest rooms behind ordinary doors, a dining
room and a kitchen. Upstairs is a second hall of rooms, but the stairs are
gone, so everything above the ground floor is reached by door and left by
dropping. Nothing is handed over: doors lean in rooms and keys lie in
bathrooms, and have to be looked for.

New here: ordinary room doors, some of them locked; numbered room keys;
the first of Ajar's own monsters, the lodger; and running out of frames.
The way out is the VIOLET door, leaning on the balcony over the lobby. To
take it you must get there with empty hands, and there is no frame beyond
the terrace, so GREEN has to go into an empty frame, and there are four
frames for four doors. One of them is in the cellar.

No key lies on the floor where it is used; each sends you back to a lock
you walked past earlier. RED (ground floor, room 104) leads upstairs.
Upstairs are key 4 (the bathroom of 201) and YELLOW (room 204), which leads
to the attic and key 1. Both open rooms at the far end of the ground
floor: 105 (key 4), a suite with key 3 in its bath, and 106 (key 1), with
BLUE, which leads to the cellar and key 2. Keys 2 and 3 together open
suite 203 upstairs: GREEN, which leads to the terrace. From there: garden,
stone doorway, balcony, VIOLET, and a drop to the lobby.
"""
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


TALL, LOW = 336, 128                              # lobby ceiling; halls and rooms
UP, LOFT, BALC, DECK = 144, 304, 112, 128         # upstairs, attic, balcony, terrace floors
WARM, GOLD, SKY = 0xFFD8CC, 0xFFE890, 0xA8C0FF
OPEN = dict(ctex="F_SKY1", wall="AJBRICK")        # Doom's own sky
HALL = (160, 288)                                 # both halls run east-west between these


# The hotel's look (gfx_hotel.py): 1, a grand old hotel, is the user's choice.
# AJAR_HOTEL=2 and 3 are the candidates that lost (a seaside hotel out of
# season, a deco hotel at night); AJAR_HOTEL=0 is the hotel as first built.
# With a look, rooms are not tinted: far sides, torches and doors carry colour.
LOOK = (os.environ.get("AJAR_HOTEL") or "1").replace("0", "")
if LOOK:
    WARM = GOLD = SKY = None
    LOBBY = dict(wall=f"AJ2L{LOOK}", ftex=f"AJ2F{LOOK}")
    BALCONY = dict(wall=f"AJ2M{LOOK}", side=f"AJ2L{LOOK}", ftex=f"AJ2F{LOOK}")
    HALLS = dict(wall=f"AJ2H{LOOK}", ftex=f"AJ2F{LOOK}")
    UPHALL = dict(wall=f"AJ2U{LOOK}", ftex=f"AJ2F{LOOK}")
    ROOM = dict(wall=f"AJ2W{LOOK}", ftex=f"AJ2C{LOOK}")
    BATH = dict(wall=f"AJ2T{LOOK}", ftex=f"AJ2B{LOOK}")
    KITCHEN = dict(wall="AJ2KW", ftex="AJ2KF")
    ATTIC = dict(wall="AJ2AW", ftex="AJBOARD")
    CELLAR = dict(wall="AJPW1", ftex="AJPG1")
    RUG, QUILT, EDGE, SEAT = f"AJ2R{LOOK}", f"AJ2Q{LOOK}", f"AJ2E{LOOK}", f"AJ2S{LOOK}"
else:
    LOBBY, BALCONY, HALLS, UPHALL, ROOM = {}, {}, {}, {}, {}
    BATH = dict(wall="AJTILE", ftex="AJTILEF")
    KITCHEN, ATTIC, CELLAR = dict(wall="AJSAFE"), dict(wall="AJBRICK"), dict(wall="AJBRICK")
    RUG, QUILT, EDGE, SEAT = "AJRUG", "AJQUILT", "AJTILE", "AJSOFA"
TUB = dict(ftex="AJWATER", side=EDGE)
SINK = dict(ftex="AJSINK", side=EDGE)
SOFA = dict(ftex=SEAT, side=SEAT)


def guest(x, north, floor=0, keys="", line_id=0, bath="w", bathdoor=True, windows=True,
          suite=False, **k):
    """A guest room off a hall, behind an ordinary door (locked, with `keys`):
    256 square, with a bed, a bathroom on its west or east side (`bath`;
    behind a door or an open way) and two windows in the back wall. A
    `suite` is two rooms deep: a sitting room, then the bedroom.

    Returns at(u, v), which turns room coordinates into map ones: u from the
    west wall (0 to 256), v from the hall wall back (0 to 256, a suite 464).
    Furniture stands against the side wall away from the bathroom."""
    sgn = 1 if north else -1
    k = dict(k, **ROOM)
    y0 = HALL[1] + 16 if north else HALL[0] - 16
    ceil, color = floor + 112, k.get("color")

    def at(u, v):
        return (x + u, y0 + sgn * v)

    def box(u1, v1, u2, v2):
        (xa, ya), (xb, yb) = at(u1, v1), at(u2, v2)
        return (min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb))

    f = 192 if bath == "w" else 0

    def bed(v):
        return [(box(f, v, f + 64, v + 112), dict(floor=floor + 20, ftex=QUILT, side="AJWOOD")),
                (box(f, v + 112, f + 64, v + 136), dict(floor=floor + 24, ftex="AJPILLOW", side="AJWOOD"))]

    sofa = [(box(f + 48 if f else 0, 96, f + 64 if f else 16, 208), dict(SOFA, floor=floor + 40)),
            (box(f + 16 if f else 16, 96, f + 48 if f else 48, 208), dict(SOFA, floor=floor + 16))]
    ajarmap.fitted(m, box(0, 0, 256, 256), sofa if suite else bed(96), floor=floor, ceil=ceil, **k)
    edge = HALL[1] if north else HALL[0]
    ajarmap.roomdoor(m, (x + 96, edge), (x + 160, edge), (0, sgn), floor, keys=keys, line_id=line_id, look=LOOK)
    back = 256
    if suite:
        ajarmap.opening(m, at(96, 256), at(160, 256), (0, sgn), floor, color=color)
        ajarmap.fitted(m, box(0, 272, 256, 464), bed(312), floor=floor, ceil=ceil, **k)
        back = 464
    if windows:
        for u in ((32, 128) if f else (64, 160)):
            ajarmap.window(m, at(u, back), at(u + 64, back), (0, sgn), floor, color=color,
                           wall=k.get("wall", "AJWALL"))
    if bath:
        ua, ub = (-144, -16) if bath == "w" else (272, 400)
        su = ua if bath == "w" else ub - 32
        ajarmap.fitted(m, box(ua, 96, ub, 256),
                       [(box(ua, 208, ub, 256), dict(TUB, floor=floor + 16)),
                        (box(su, 96, su + 32, 128), dict(SINK, floor=floor + 32))],
                       floor=floor, ceil=ceil, light=200, **BATH)
        wu = 0 if bath == "w" else 256
        if bathdoor:
            ajarmap.roomdoor(m, at(wu, 144), at(wu, 208), (-1 if bath == "w" else 1, 0), floor, look=LOOK)
        else:
            ajarmap.opening(m, at(wu, 144), at(wu, 208), (-1 if bath == "w" else 1, 0), floor)
    return at


# --- the lobby: start here. Reception desk under the balcony, which has a gap
# in its rail; a sofa; the front doors, boarded up from outside ---------------
ajarmap.fitted(m, (0, 0, 512, 448), [
    ((224, 0, 288, 448), ajarmap.RUNNER), ((0, 192, 512, 256), ajarmap.RUNNER),
    ((48, 408, 208, 448), dict(floor=40, ftex="AJWOOD", side="AJWOOD")),          # the desk
    ((0, 16, 16, 144), dict(SOFA, floor=40)), ((16, 16, 48, 144), dict(SOFA, floor=16)),
], ceil=TALL, light=190, rug=RUG, **LOBBY)
m.sector(rect(0, 448, 512, 576), floor=BALC, ceil=TALL, light=205, **BALCONY)   # the balcony
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
for a, b in (((0, 448), (224, 448)), ((288, 448), (512, 448))):
    m.line(a, b, **RAIL)
m.line((224, 448), (288, 448), dontpegbottom=True)    # the gap in the rail: its wall hangs like the rest
m.line((48, 448), (208, 448), lower=f"AJ2Y{LOOK}" if LOOK else "AJKEYS", exact=True, **RAIL)         # the key rack behind the desk
m.cut((512, 16), (512, 144))
m.line((512, 16), (512, 144), mid=f"AJ2X{LOOK}" if LOOK else "AJFRONT", exact=True)
if LOOK:                                  # the lobby's wall carries on over the mouths of the two halls
    m.line((0, 160), (0, 288), upper=LOBBY["wall"], dontpegtop=True)
    m.line((512, 160), (512, 288), upper=LOBBY["wall"], lower=LOBBY["wall"], dontpegtop=True, dontpegbottom=True)

# --- the ground-floor hall, west of the lobby: six rooms, dining, kitchen ---
ajarmap.room(m, [-1408, 0], [HALL[0], 192, 256, HALL[1]], lambda i, j: j == 1, ceil=LOW, light=165, rug=RUG, **HALLS)
TABLE = dict(floor=28, ftex="AJCLOTH", side="AJCLOTH")
ajarmap.fitted(m, (-1920, -64, -1408, 512), [((-1728, 40, -1600, 104), TABLE),
                                             ((-1728, 344, -1600, 408), TABLE)],
               ceil=LOW, light=185, **HALLS)                               # dining room
for y in (128, 256):
    ajarmap.window(m, (-1920, y), (-1920, y + 64), (-1, 0), 0, wall=HALLS.get("wall", "AJWALL"))
ajarmap.fitted(m, (-1920, 528, -1408, 848),
               [((-1920, 560, -1880, 816), dict(floor=36, ftex="AJSTEEL", side="AJSTEEL"))],
               ceil=LOW, light=200, **KITCHEN)                             # kitchen
ajarmap.roomdoor(m, (-1696, 512), (-1632, 512), (0, 1), 0, look=LOOK)
R101 = guest(-352, True, light=150)
R102 = guest(-352, False, bathdoor=False, light=175)
R103 = guest(-800, True, light=140)
R104 = guest(-800, False, windows=False, light=175)                 # RED
R105 = guest(-1248, True, keys="4", line_id=303, suite=True, light=160)    # locked: key 3 in the bath
R106 = guest(-1248, False, keys="1", line_id=301, windows=False, light=130)   # locked: BLUE

# --- upstairs: the stairs are gone, so the hall ends in a drop to the lobby --
ajarmap.room(m, [512, 1664], [HALL[0], 192, 256, HALL[1]], lambda i, j: j == 1,
             floor=UP, ceil=UP + 112, light=175, color=WARM, rug=RUG, **UPHALL)
m.sector(rect(1664, 160, 1792, 288), floor=UP, ceil=LOFT + 144, light=170, color=WARM,
         **dict(UPHALL, **ATTIC))                                           # under the attic
R201 = guest(704, True, UP, bath="e", light=165, color=WARM)        # key 4 in the bathroom
R202 = guest(704, False, UP, bathdoor=False, light=140, color=WARM)
R203 = guest(1216, True, UP, keys="23", line_id=302, bath="e", suite=True,
             light=150, color=WARM)                                 # two locks: GREEN
R204 = guest(1216, False, UP, windows=False, light=175, color=WARM)   # YELLOW

# --- the attic: a drop into the upstairs hall --------------------------------
m.sector(rect(1792, 64, 2176, 384), floor=LOFT, ceil=LOFT + 128, light=170, color=GOLD, **ATTIC)

# --- the terrace over the garden; a stone doorway joins garden and balcony --
m.sector(rect(3000, 0, 3256, 448), floor=DECK, ceil=400, light=220, color=0xD4F4D0, **OPEN)
m.sector(rect(3256, 0, 3896, 448), ceil=400, light=220, ftex="AJGRASS", **OPEN)
ajarmap.doorway(m, 1, (96, 576), (160, 576), (0, 1), BALC, (3896, 192), (3896, 256), (1, 0), 0)

# --- the cellar: a dead end ---------------------------------------------------
m.sector(rect(4200, 0, 4520, 320), ceil=160, light=150, color=SKY, **CELLAR)

# --- the way out (VIOLET's far side): the same room in every level -----------
ajarmap.way_out(m, 5000, 0, VIOLET)

# --- frames: four in the whole hotel -----------------------------------------
recess((224, 0), (288, 0), (0, -1), 0, 101, 201)                          # lobby
recess((-1696, 848), (-1632, 848), (0, 1), 0, 105, 201)                   # kitchen
recess((992, 160), (1056, 160), (0, -1), UP, 102, 201, color=WARM)        # upstairs hall
recess((4520, 128), (4520, 192), (1, 0), 0, 104, 201, color=SKY)          # cellar

# --- far sides ---------------------------------------------------------------
recess((576, 288), (640, 288), (0, 1), UP, far_id(RED), 101, far_colour=RED, color=WARM)
recess((2176, 192), (2176, 256), (1, 0), LOFT, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)
recess((4200, 128), (4200, 192), (-1, 0), 0, far_id(BLUE), 101, far_colour=BLUE, color=SKY)
recess((3000, 192), (3000, 256), (-1, 0), DECK, far_id(GREEN), 101, far_colour=GREEN, color=0xD4F4D0)

# --- pictures in the lobby of the two doors that start it all ---------------
ajarmap.picture(m, (96, 0), (160, 0), RED, TALL, tex=f"AJ2P{LOOK}{RED}" if LOOK else None)
ajarmap.picture(m, (352, 0), (416, 0), VIOLET, TALL, tex=f"AJ2P{LOOK}{VIOLET}" if LOOK else None)

# --- doors and keys ----------------------------------------------------------
m.thing(256, 96, 1, angle=90)                                             # player start, facing the balcony
ajarmap.door(m, RED, *R104(128, 242), angle=90)
ajarmap.door(m, BLUE, *R106(128, 242), angle=90)                          # locked in (key 1)
ajarmap.door(m, YELLOW, *R204(128, 242), angle=90)
ajarmap.door(m, GREEN, *R203(242, 368), angle=180)                        # locked in (keys 2 and 3), in the bedroom
ajarmap.door(m, VIOLET, 256, 562, angle=270)                              # the balcony
ajarmap.key(m, 1, 2100, 110)                                              # attic
ajarmap.key(m, 2, 4440, 60)                                               # cellar
ajarmap.key(m, 3, *R105(-80, 232))                                        # in the bath of suite 105
ajarmap.key(m, 4, *R201(336, 176))                                        # bathroom of 201

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
SHOTGUN, CHAINGUN, SHELLS, CLIP, AMMOBOX, STIM, MEDIKIT, BONUS, HELMET, ARMOR = (
    2001, 2002, 2008, 2007, 2048, 2011, 2012, 2014, 2015, 2018)
CANDLE, CANDELABRA, LAMP, TECHLAMP, TREE, STUMP = 34, 35, 2028, 86, 54, 43
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, DEAD_ZOMBIE = 24, 18


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the lobby: nobody home, a candle on the desk
things(ARMOR, (112, 376))
things(CANDELABRA, (196, 24), (316, 24))
things(CANDLE, (68, 428))
things(LAMP, (488, 424))
things(TECHLAMP, (24, 552), (488, 552))                                   # the balcony
# the ground-floor hall: two of the staff at the far end
things(ZOMBIE, (-1000, 200), (-1150, 250))
things(CANDLE, (-16, 176), (-16, 272))
things(DEAD_ZOMBIE, (-600, 270))
# 101: two guests who never checked out
things(ZOMBIE, R101(72, 176), R101(150, 200), angle=270)
things(CLIP, R101(22, 236), R101(-80, 150))
# 102: somebody's luggage, on the bed
things(SHOTGUN, R102(224, 150))
things(SHELLS, R102(100, 200), R102(150, 200))
things(STIM, R102(-80, 150))
# 103: dark, and not empty; nor is its bathroom
things(IMP, R103(72, 196), R103(150, 196), R103(-60, 170), angle=270)
things(STIM, R103(22, 236))
# 104: RED, and a sergeant in front of it
things(SERGEANT, R104(128, 164), angle=90)
things(TORCH_R, R104(80, 234), R104(176, 234))
# 105, locked: a suite. Key 3 is in the bath; somebody is in the bedroom
things(SERGEANT, R105(100, 380), angle=270)
things(IMP, R105(100, 150), angle=270)
things(MEDIKIT, R105(128, 440))
things(BONUS, R105(60, 300), R105(100, 300), R105(140, 300))
things(LAMP, R105(20, 236), R105(20, 444))
# 106, locked: BLUE, and what was shut in with it
things(DEMON, R106(128, 144), angle=90)
things(TORCH_B, R106(80, 234), R106(176, 234))
things(SHELLS, R106(28, 234))
# the dining room
things(IMP, (-1820, 20), (-1820, 430), angle=0)
things(ZOMBIE, (-1700, 224), angle=0)
things(CANDELABRA, (-1896, -40), (-1896, 488), (-1432, -40), (-1432, 488))
things(STIM, (-1880, 224))
# the kitchen: a frame, a sergeant, and a lodger that wakes when you come in
things(SERGEANT, (-1500, 760), angle=180)
things(LODGER, (-1664, 640), args=(200,))
things(SHELLS, (-1840, 820))
things(STIM, (-1440, 560), (-1470, 560))
# upstairs hall: three of the old guests, red torches by the RED far side
things(ZOMBIE, (1150, 200), (1300, 248), angle=180)
things(SERGEANT, (1500, 224), angle=180)
things(TORCH_R, (548, 272), (668, 272))
things(CLIP, (900, 176))
things(STIM, (1700, 176))
# 201: an imp in the corner; key 4 is in the bathroom
things(IMP, R201(180, 180), angle=225)
things(LAMP, R201(236, 236))
# 202: the chaingun, and two who were arguing over it
things(CHAINGUN, R202(128, 184))
things(AMMOBOX, R202(166, 214))
things(ZOMBIE, R202(56, 204), R202(150, 110), angle=90)
# 203, two locks: a suite, well guarded, GREEN in the bedroom
things(IMP, R203(100, 200), R203(200, 200), angle=270)
things(SERGEANT, R203(128, 340), angle=270)
things(TORCH_G, R203(240, 312), R203(240, 424))
things(MEDIKIT, R203(24, 26))
# 204: YELLOW
things(SERGEANT, R204(128, 164), angle=90)
things(CANDELABRA, R204(24, 234), R204(176, 240))
things(HELMET, R204(44, 44), R204(84, 44))
# the attic: key 1, two imps over the drop
things(IMP, (1900, 112), (1900, 336), angle=0)
things(CANDELABRA, (2152, 88), (2152, 360))
things(BONUS, (1960, 224), (2000, 224), (2040, 224))
# the cellar: key 2, a frame, and two things you cannot quite see
things(SPECTRE, (4440, 240), (4300, 60), angle=180)
things(TORCH_B, (4224, 96), (4224, 224))
things(SHELLS, (4240, 290), (4270, 290))
things(STIM, (4500, 300))
# the terrace: nothing, and no frame
things(TORCH_G, (3024, 160), (3024, 288))
things(SHELLS, (3220, 40))
things(STIM, (3220, 408))
# the garden: two demons and an imp, trees, lamps by the doorway
things(DEMON, (3620, 96), (3620, 352), angle=180)
things(IMP, (3800, 80), angle=180)
things(TREE, (3320, 48), (3840, 400))
things(STUMP, (3480, 400), (3700, 40))
things(TECHLAMP, (3872, 160), (3872, 288))
things(MEDIKIT, (3840, 60))
things(POOL, (3500, 220))
# the way out: two more between you and it
things(SERGEANT, (5240, 48), angle=180)
things(ZOMBIE, (5240, 208), angle=180)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
PUZZLE = dict(
    start="ground", goal="exit", names=ajarmap.NAMES,
    walk=[("upstairs", "ground"), ("attic", "upstairs"), ("terrace", "garden"),
          ("garden", "balcony"), ("balcony", "garden"),                   # the stone doorway
          ("balcony", "ground"),                                          # the gap in the rail
          ("ground", "room 105", "4"), ("room 105", "ground", "4"),
          ("ground", "room 106", "1"), ("room 106", "ground", "1"),
          ("upstairs", "room 203", "23"), ("room 203", "upstairs", "23")],
    keys={"1": "attic", "2": "cellar", "3": "room 105", "4": "upstairs"},
    frames={101: "ground", 105: "ground", 102: "upstairs", 104: "cellar"},
    doors={
        RED: dict(home="upstairs", lean="ground"),
        YELLOW: dict(home="attic", lean="upstairs"),
        BLUE: dict(home="cellar", lean="room 106"),
        GREEN: dict(home="terrace", lean="room 203"),
        VIOLET: dict(home="exit", lean="balcony"),
    },
)
