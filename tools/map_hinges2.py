"""Act 1, level 2: "No Vacancy" (MAP02).

A hotel. The way out is the VIOLET door, leaning on a balcony over the lobby
that nothing climbs to. A plain stone doorway joins the balcony to a garden,
so the balcony is reached from the garden, and the garden from the terrace
above it. New here: fixed doorways (part of the building, not yours to
take), a drop back to where you started, having to arrive somewhere with
your hands free, and the first of Ajar's own monsters, the lodger, which
lives in empty frames.

Upstairs corridor (RED's far side) -> attic (YELLOW's) -> kitchen (BLUE's)
-> terrace (GREEN's) -> garden -> balcony -> the street (VIOLET's).
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


TALL = 336
UP, LOFT, BALC, DECK = 144, 304, 112, 128        # corridor, attic, balcony, terrace floors
WARM, GOLD, SKY, LEAF, PLUM = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0x80FF90, 0xD0A0FF
OPEN = dict(ctex="F_SKY1", wall="AJBRICK")       # Doom's own sky

# --- the lobby: one frame, the RED door, and the balcony out of reach -------
ajarmap.room(m, [0, 224, 288, 512], [0, 192, 256, 448],                  # start to balcony, frame to stairs
             lambda i, j: i == 1 or j == 1, ceil=TALL, light=190)
recess((0, 192), (0, 256), (-1, 0), 0, 101, 201)                          # lobby frame, empty
m.sector(rect(0, 448, 512, 576), floor=BALC, ceil=TALL, light=205)        # the balcony
m.line((0, 448), (512, 448), mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
recess((352, 576), (416, 576), (0, 1), BALC, 106, 201)                    # balcony frame, empty

# --- upstairs (RED's far side): the stairs are gone, so it is a drop back ---
ajarmap.room(m, [512, 1408], [160, 192, 256, 288], lambda i, j: j == 1,
             floor=UP, ceil=UP + 112, light=180, color=WARM)
m.sector(rect(1408, 160, 1536, 288), floor=UP, ceil=LOFT + 144, light=170, color=WARM)   # under the attic
recess((576, 288), (640, 288), (0, 1), UP, far_id(RED), 101, far_colour=RED, color=WARM)
recess((832, 160), (896, 160), (0, -1), UP, 102, 201, color=WARM)        # corridor frames, empty
recess((1088, 160), (1152, 160), (0, -1), UP, 103, 201, color=WARM)

# --- the attic (YELLOW's far side): no frame, and a drop into the corridor --
m.sector(rect(1536, 64, 1920, 384), floor=LOFT, ceil=LOFT + 128, light=170, color=GOLD, wall="AJBRICK")
recess((1920, 192), (1920, 256), (1, 0), LOFT, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)

# --- the kitchen (BLUE's far side): a dead end -------------------------------
m.sector(rect(4200, 0, 4520, 320), ceil=160, light=200, color=SKY, wall="AJSAFE")
recess((4200, 128), (4200, 192), (-1, 0), 0, far_id(BLUE), 101, far_colour=BLUE, color=SKY)

# --- the terrace (GREEN's far side) over the garden --------------------------
m.sector(rect(3000, 0, 3256, 448), floor=DECK, ceil=400, light=220, color=0xD4F4D0, **OPEN)
m.sector(rect(3256, 0, 3896, 448), ceil=400, light=220, ftex="AJGRASS", **OPEN)
recess((3000, 192), (3000, 256), (-1, 0), DECK, far_id(GREEN), 101, far_colour=GREEN, color=0xD4F4D0)
recess((3096, 448), (3160, 448), (0, 1), DECK, 104, 201)                  # terrace frame, empty
# the fixed doorway: garden <-> balcony
ajarmap.doorway(m, 1, (96, 576), (160, 576), (0, 1), BALC, (3896, 192), (3896, 256), (1, 0), 0)

# --- the street (VIOLET's far side) ----------------------------------------
m.sector(rect(5000, 0, 5448, 192), ceil=160, light=210, color=PLUM, ftex="AJPIT", **OPEN)
recess((5000, 64), (5000, 128), (-1, 0), 0, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)
m.cut((5448, 64), (5448, 128))
m.line((5448, 64), (5448, 128), special=243, playeruse=True, mid="AJEXIT", exact=True)

# --- pictures in the lobby of the two doors to look for first ---------------
ajarmap.picture(m, (96, 0), (160, 0), YELLOW, TALL)
ajarmap.picture(m, (352, 0), (416, 0), BLUE, TALL)

# --- things ----------------------------------------------------------------
m.thing(256, 64, 1, angle=90)                                             # player start, facing the balcony
ajarmap.door(m, RED, 14, 96, angle=0)                                     # leaning in the lobby
ajarmap.door(m, YELLOW, 1472, 274, angle=270)                             # leaning at the corridor's end
ajarmap.door(m, BLUE, 1906, 112, angle=180)                               # leaning in the attic
ajarmap.door(m, GREEN, 4506, 256, angle=180)                              # leaning in the kitchen
ajarmap.door(m, VIOLET, 256, 562, angle=270)                              # leaning on the balcony

ZOMBIE, SERGEANT, IMP, DEMON, LODGER = 3004, 9, 3001, 3002, 20005
SHOTGUN, CHAINGUN, SHELLS, CLIP, AMMOBOX, STIM, MEDIKIT, BONUS, ARMOR = (
    2001, 2002, 2008, 2007, 2048, 2011, 2012, 2014, 2018)
CANDLE, CANDELABRA, LAMP, TECHLAMP, TREE, STUMP = 34, 35, 2028, 86, 54, 43
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, DEAD_ZOMBIE = 24, 18


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the lobby: nobody home. A shotgun by the door that used to lead outside.
things(SHOTGUN, (400, 80))
things(SHELLS, (432, 104))
things(ARMOR, (72, 392))
things(CANDELABRA, (24, 24), (488, 24))
things(LAMP, (24, 424), (488, 424))
# the balcony: lamps at either end
things(TECHLAMP, (24, 552), (488, 552))
# upstairs: three of the old guests, red torches by the RED far side. A
# lodger wakes when you come 300 units from where it is placed, here halfway
# along the corridor, and knocks in the first empty frame you can see.
things(ZOMBIE, (1100, 200), (1250, 248), angle=180)
things(SERGEANT, (1370, 224), angle=180)
things(TORCH_R, (548, 272), (668, 272))
things(CLIP, (700, 176), (1300, 176))
things(STIM, (1500, 176))
things(DEAD_ZOMBIE, (980, 270))
things(LODGER, (1000, 224), args=(300,))
# the attic: two imps over the drop, a chaingun for getting this far
things(IMP, (1640, 112), (1640, 336), angle=0)
things(CHAINGUN, (1580, 356))
things(AMMOBOX, (1620, 356))
things(CANDELABRA, (1896, 88), (1896, 360))
things(BONUS, (1700, 224), (1740, 224), (1780, 224))
# the terrace: quiet until the second lodger finds the empty frame up here
things(TORCH_G, (3024, 160), (3024, 288))
things(SHELLS, (3220, 40))
things(STIM, (3220, 408))
things(LODGER, (3128, 224), args=(220,))
# the garden: two demons and an imp, trees, lamps by the doorway
things(DEMON, (3620, 96), (3620, 352), angle=180)
things(IMP, (3800, 80), angle=180)
things(TREE, (3320, 48), (3840, 400))
things(STUMP, (3480, 400), (3700, 40))
things(TECHLAMP, (3872, 160), (3872, 288))
things(MEDIKIT, (3840, 60))
things(SHELLS, (3300, 400))
things(POOL, (3500, 220))
# the kitchen: staff, blue torches by the BLUE far side
things(IMP, (4440, 60), (4440, 200), angle=180)
things(SERGEANT, (4360, 280), angle=180)
things(TORCH_B, (4224, 96), (4224, 224))
things(STIM, (4480, 30), (4500, 30))
things(SHELLS, (4240, 290))
# the street: two more between you and the way out
things(SERGEANT, (5330, 48), angle=180)
things(ZOMBIE, (5380, 150), angle=180)
things(TECHLAMP, (5424, 24), (5424, 168))

# The same level as a graph, for tools/solve.py. Keep in step with the above.
PUZZLE = dict(
    start="lobby", goal="street", names=ajarmap.NAMES,
    walk=[("corridor", "lobby"), ("attic", "corridor"), ("terrace", "garden"),
          ("garden", "balcony"), ("balcony", "garden")],                  # the last two: the doorway
    frames={101: "lobby", 102: "corridor", 103: "corridor", 104: "terrace", 106: "balcony"},
    doors={
        RED: dict(home="corridor", lean="lobby"),
        YELLOW: dict(home="attic", lean="corridor"),
        BLUE: dict(home="kitchen", lean="attic"),
        GREEN: dict(home="terrace", lean="kitchen"),
        VIOLET: dict(home="street", lean="balcony"),
    },
)
