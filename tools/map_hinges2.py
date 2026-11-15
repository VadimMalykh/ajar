"""Act 1, level 2: "No Vacancy" (MAP02).

A hotel, and the first level that is not one thing after another.

The ground floor is a place to walk about in: the lobby, a hall of guest
rooms behind ordinary doors, a dining room and a kitchen. Upstairs is a
second hall of rooms, but the stairs are gone, so everything above the
ground floor is reached by door and left by dropping. Nothing is handed
over: the doors lean in rooms and have to be looked for.

New here: ordinary room doors, some of them locked; numbered room keys;
the first of Ajar's own monsters, the lodger; and running out of frames.
The way out is the VIOLET door, leaning on the balcony over the lobby. To
take it you must get there with empty hands, and there is no frame beyond
the terrace, so GREEN has to go into an empty frame, and there are four
frames for four doors. One of them is in the cellar.

RED (ground floor, room 104) leads upstairs. Upstairs are key 1 (room 201)
and YELLOW (room 204), which leads to the attic and key 3. Key 1 opens
room 106 downstairs: BLUE, which leads to the cellar and key 2. Keys 2 and
3 together open room 203 upstairs: GREEN, which leads to the terrace. From
there: garden, stone doorway, balcony, VIOLET, and a drop to the lobby.
The attic and the cellar can be done in either order.
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


TALL, LOW = 336, 128                              # lobby ceiling; halls and rooms
UP, LOFT, BALC, DECK = 144, 304, 112, 128         # upstairs, attic, balcony, terrace floors
WARM, GOLD, SKY, LEAF, PLUM = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0x80FF90, 0xD0A0FF
OPEN = dict(ctex="F_SKY1", wall="AJBRICK")        # Doom's own sky
HALL = (160, 288)                                 # both halls run east-west between these


def guest(x, north, floor=0, keys="", line_id=0, **k):
    """A 256-square guest room off a hall, behind an ordinary door (locked,
    with `keys`). Returns its (x1, y1, x2, y2)."""
    y1 = HALL[1] + 16 if north else HALL[0] - 272
    box = (x, y1, x + 256, y1 + 256)
    m.sector(rect(*box), floor=floor, ceil=floor + 112, **k)
    edge = HALL[1] if north else HALL[0]
    ajarmap.roomdoor(m, (x + 96, edge), (x + 160, edge), (0, 1 if north else -1), floor,
                     keys=keys, line_id=line_id)
    return box


# --- the lobby: start here. The balcony over it has a gap in its rail -------
ajarmap.room(m, [0, 224, 288, 512], [0, 192, 256, 448],
             lambda i, j: i == 1 or j == 1, ceil=TALL, light=190)
m.sector(rect(0, 448, 512, 576), floor=BALC, ceil=TALL, light=205)        # the balcony
for a, b in (((0, 448), (224, 448)), ((288, 448), (512, 448))):
    m.line(a, b, mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)

# --- the ground-floor hall, west of the lobby: six rooms, dining, kitchen ---
ajarmap.room(m, [-1408, 0], [HALL[0], 192, 256, HALL[1]], lambda i, j: j == 1, ceil=LOW, light=165)
m.sector(rect(-1920, -64, -1408, 512), ceil=LOW, light=185)               # dining room
m.sector(rect(-1920, 528, -1408, 848), ceil=LOW, light=200, wall="AJSAFE")  # kitchen
ajarmap.roomdoor(m, (-1696, 512), (-1632, 512), (0, 1), 0)
R101 = guest(-352, True, light=150)
R102 = guest(-352, False, light=175)
R103 = guest(-800, True, light=140)
R104 = guest(-800, False, light=175)
R105 = guest(-1248, True, light=175)
R106 = guest(-1248, False, keys="1", line_id=301, light=130)        # locked: BLUE

# --- upstairs: the stairs are gone, so the hall ends in a drop to the lobby --
ajarmap.room(m, [512, 1664], [HALL[0], 192, 256, HALL[1]], lambda i, j: j == 1,
             floor=UP, ceil=UP + 112, light=175, color=WARM)
m.sector(rect(1664, 160, 1792, 288), floor=UP, ceil=LOFT + 144, light=170, color=WARM)   # under the attic
R201 = guest(704, True, UP, light=165, color=WARM)
R202 = guest(704, False, UP, light=140, color=WARM)
R203 = guest(1216, True, UP, keys="23", line_id=302, light=150, color=WARM)   # two locks: GREEN
R204 = guest(1216, False, UP, light=175, color=WARM)

# --- the attic: a drop into the upstairs hall --------------------------------
m.sector(rect(1792, 64, 2176, 384), floor=LOFT, ceil=LOFT + 128, light=170, color=GOLD, wall="AJBRICK")

# --- the terrace over the garden; a stone doorway joins garden and balcony --
m.sector(rect(3000, 0, 3256, 448), floor=DECK, ceil=400, light=220, color=0xD4F4D0, **OPEN)
m.sector(rect(3256, 0, 3896, 448), ceil=400, light=220, ftex="AJGRASS", **OPEN)
ajarmap.doorway(m, 1, (96, 576), (160, 576), (0, 1), BALC, (3896, 192), (3896, 256), (1, 0), 0)

# --- the cellar: a dead end ---------------------------------------------------
m.sector(rect(4200, 0, 4520, 320), ceil=160, light=150, color=SKY, wall="AJBRICK")

# --- the street: the way out -------------------------------------------------
m.sector(rect(5000, 0, 5448, 192), ceil=160, light=210, color=PLUM, ftex="AJPIT", **OPEN)
m.cut((5448, 64), (5448, 128))
m.line((5448, 64), (5448, 128), special=243, playeruse=True, mid="AJEXIT", exact=True)

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
recess((5000, 64), (5000, 128), (-1, 0), 0, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)

# --- pictures in the lobby of the two doors that start it all ---------------
ajarmap.picture(m, (96, 0), (160, 0), RED, TALL)
ajarmap.picture(m, (352, 0), (416, 0), VIOLET, TALL)

# --- doors and keys ----------------------------------------------------------
m.thing(256, 96, 1, angle=90)                                             # player start, facing the balcony
ajarmap.door(m, RED, -672, -98, angle=90)                                 # room 104
ajarmap.door(m, BLUE, -1120, -98, angle=90)                               # room 106, locked (key 1)
ajarmap.door(m, YELLOW, 1344, -98, angle=90)                              # room 204
ajarmap.door(m, GREEN, 1344, 546, angle=270)                              # room 203, locked (keys 2 and 3)
ajarmap.door(m, VIOLET, 256, 562, angle=270)                              # the balcony
ajarmap.key(m, 1, 832, 500)                                               # room 201
ajarmap.key(m, 2, 4440, 60)                                               # cellar
ajarmap.key(m, 3, 2100, 110)                                              # attic

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
SHOTGUN, CHAINGUN, SHELLS, CLIP, AMMOBOX, STIM, MEDIKIT, BONUS, HELMET, ARMOR = (
    2001, 2002, 2008, 2007, 2048, 2011, 2012, 2014, 2015, 2018)
CANDLE, CANDELABRA, LAMP, TECHLAMP, TREE, STUMP = 34, 35, 2028, 86, 54, 43
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, DEAD_ZOMBIE = 24, 18


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the lobby: nobody home
things(ARMOR, (72, 392))
things(CANDELABRA, (24, 24), (488, 24))
things(LAMP, (488, 424))
things(TECHLAMP, (24, 552), (488, 552))                                   # the balcony
# the ground-floor hall: two of the staff at the far end
things(ZOMBIE, (-1000, 200), (-1150, 250))
things(CANDLE, (-16, 176), (-16, 272))
things(DEAD_ZOMBIE, (-600, 270))
# 101: two guests who never checked out
things(ZOMBIE, (-280, 480), (-170, 480), angle=270)
things(CLIP, (-330, 540), (-120, 540))
# 102: somebody's luggage
things(SHOTGUN, (-224, -40))
things(SHELLS, (-190, -70), (-260, -70))
# 103: dark, and not empty
things(IMP, (-730, 500), (-610, 500), angle=270)
things(STIM, (-780, 540))
# 104: RED, and a sergeant in front of it
things(SERGEANT, (-672, -20), angle=90)
things(TORCH_R, (-720, -90), (-624, -90))
# 105: quiet
things(MEDIKIT, (-1120, 520))
things(BONUS, (-1180, 440), (-1120, 440), (-1060, 440))
things(LAMP, (-1230, 540), (-1010, 540))
# 106, locked: BLUE, and what was shut in with it
things(DEMON, (-1120, 0), angle=90)
things(TORCH_B, (-1168, -90), (-1072, -90))
things(SHELLS, (-1220, -90))
# the dining room
things(IMP, (-1820, 20), (-1820, 430), angle=0)
things(ZOMBIE, (-1700, 224), angle=0)
things(CANDELABRA, (-1896, -40), (-1896, 488), (-1432, -40), (-1432, 488))
things(STIM, (-1880, 224))
# the kitchen: a frame, a sergeant, and a lodger that wakes when you come in
things(SERGEANT, (-1500, 760), angle=180)
things(LODGER, (-1664, 640), args=(200,))
things(SHELLS, (-1880, 820))
things(STIM, (-1440, 560), (-1470, 560))
# upstairs hall: three of the old guests, red torches by the RED far side
things(ZOMBIE, (1150, 200), (1300, 248), angle=180)
things(SERGEANT, (1500, 224), angle=180)
things(TORCH_R, (548, 272), (668, 272))
things(CLIP, (900, 176))
things(STIM, (1700, 176))
# 201: key 1 on the floor, an imp in the corner
things(IMP, (920, 520), angle=225)
things(LAMP, (724, 540))
# 202: the chaingun, and two who were arguing over it
things(CHAINGUN, (832, -40))
things(AMMOBOX, (870, -70))
things(ZOMBIE, (760, -60), (900, 20), angle=90)
# 203, two locks: GREEN, well guarded
things(IMP, (1260, 500), (1430, 500), angle=270)
things(SERGEANT, (1344, 440), angle=270)
things(TORCH_G, (1296, 540), (1392, 540))
things(MEDIKIT, (1240, 330))
# 204: YELLOW
things(SERGEANT, (1344, -20), angle=90)
things(CANDELABRA, (1240, -90), (1450, -90))
things(HELMET, (1260, 100), (1300, 100))
# the attic: key 3, two imps over the drop
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
# the street: two more between you and the way out
things(SERGEANT, (5330, 48), angle=180)
things(ZOMBIE, (5380, 150), angle=180)
things(TECHLAMP, (5424, 24), (5424, 168))

# The same level as a graph, for tools/solve.py. Keep in step with the above.
PUZZLE = dict(
    start="ground", goal="street", names=ajarmap.NAMES,
    walk=[("upstairs", "ground"), ("attic", "upstairs"), ("terrace", "garden"),
          ("garden", "balcony"), ("balcony", "garden"),                   # the stone doorway
          ("balcony", "ground"),                                          # the gap in the rail
          ("ground", "room 106", "1"), ("room 106", "ground", "1"),
          ("upstairs", "room 203", "23"), ("room 203", "upstairs", "23")],
    keys={"1": "upstairs", "2": "cellar", "3": "attic"},
    frames={101: "ground", 105: "ground", 102: "upstairs", 104: "cellar"},
    doors={
        RED: dict(home="upstairs", lean="ground"),
        YELLOW: dict(home="attic", lean="upstairs"),
        BLUE: dict(home="cellar", lean="room 106"),
        GREEN: dict(home="terrace", lean="room 203"),
        VIOLET: dict(home="street", lean="balcony"),
    },
)
