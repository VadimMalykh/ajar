"""Act 1, level 1: "Borrowed Rooms" (MAP01).

You start locked in a cell with a door and a frame. The hall beyond is cut
by a pit; the only way out of the pit is the door hanging in it. Every door
you need is somewhere the last one leads.

Company is Doom's own (none of Ajar's monsters yet): zombies in the hall, a
demon down in the pit, imps on the ledge, on the gallery and in the vault.
Each far side is lit in its door's colour.
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


TALL = 352
WARM, GOLD, SKY, LEAF, PLUM = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0x80FF90, 0xD0A0FF

# --- the cell: one door, one frame ----------------------------------------
m.sector(rect(0, -1500, 256, -1244), ceil=128, light=170, wall="AJBRICK")
recess((96, -1244), (160, -1244), (0, 1), 0, 101, 201)                    # frame, empty

# --- the hall (RED's far side), the pit, the ledge (YELLOW's far side) -----
# Rooms are cut into grids so that a carpet runner under a row of ceiling
# lights can lead from each door to where it matters.
ajarmap.room(m, [0, 352, 416, 768], [0, 288, 352, 640],                  # RED to the pit, frame to RED
             lambda i, j: j == 1 or (i == 1 and j == 0), ceil=TALL - 16, light=190, color=WARM)
m.sector(rect(768, 0, 1024, 640), floor=-192, ceil=TALL, light=176, ftex="AJPIT", wall="AJTRIM")
ajarmap.room(m, [1024, 1280], [0, 288, 352, 640], lambda i, j: j == 1,
             ceil=TALL - 16, light=200, color=GOLD)
recess((0, 288), (0, 352), (-1, 0), 0, far_id(RED), 101, far_colour=RED, color=WARM)
recess((352, 0), (416, 0), (0, -1), 0, 102, 201)                          # hall frame, empty
recess((864, 640), (928, 640), (0, 1), -192, 103, 201)                    # pit frame, starts with YELLOW
recess((1280, 288), (1280, 352), (1, 0), 0, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)

# --- the gallery above the hall (BLUE's far side): you can only drop off it --
ajarmap.room(m, [0, 352, 416, 768], [640, 704, 768, 832],                # BLUE to the edge, and to the frame
             lambda i, j: i == 1 or (i == 0 and j == 1), floor=160, ceil=TALL - 16, light=200, color=SKY)
recess((352, 832), (416, 832), (0, 1), 160, far_id(BLUE), 101, far_colour=BLUE, color=SKY)
recess((0, 704), (0, 768), (-1, 0), 160, 104, 201, color=SKY)             # gallery frame, empty

# --- the vault (GREEN's far side): no frame, only the VIOLET door ----------
ajarmap.room(m, [2000, 2320], [0, 128, 192, 320], lambda i, j: j == 1,
             ceil=160, light=210, color=LEAF, wall="AJSAFE")
recess((2000, 128), (2000, 192), (-1, 0), 0, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)

# --- the way out (VIOLET's far side) ---------------------------------------
ajarmap.room(m, [3000, 3320], [0, 96, 160, 256], lambda i, j: j == 1,
             ceil=160, light=210, color=PLUM)
recess((3000, 96), (3000, 160), (-1, 0), 0, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)
m.line((3320, 96), (3320, 160), special=243, playeruse=True, mid="AJEXIT", exact=True)

# --- light niches in the hall's south wall, either side of the frame --------
for x in (128, 576):
    m.sector(rect(x, -32, x + 64, 0), floor=32, ceil=112, light=255, wall="AJTRIM",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.thing(x + 32, -16, 35)                                              # candelabra

# --- pictures of the doors, in the order you will need them ----------------
ajarmap.picture(m, (256, 0), (320, 0), GREEN, TALL - 16)                  # hall, left of the frame
ajarmap.picture(m, (448, 0), (512, 0), VIOLET, TALL - 16)                 # hall, right of the frame
ajarmap.picture(m, (192, 832), (256, 832), YELLOW, TALL - 16 - 160)      # gallery
ajarmap.picture(m, (512, 832), (576, 832), GREEN, TALL - 16 - 160)

# --- things ----------------------------------------------------------------
m.thing(128, -1420, 1, angle=90)                                          # player start
ajarmap.door(m, RED, 48, -1258, angle=270)                               # leaning in the cell
ajarmap.door(m, YELLOW, 896, 600, frame=103)                              # hanging in the pit
ajarmap.door(m, BLUE, 1266, 128, angle=180)                               # leaning on the ledge
ajarmap.door(m, GREEN, 754, 700, angle=180)                               # leaning on the gallery
ajarmap.door(m, VIOLET, 2306, 160, angle=180)                             # leaning in the vault

# Doom thing numbers. Nothing here is on a line the player has to walk
# (blocking lights stand in corners and beside recesses, never in front).
ZOMBIE, IMP, DEMON = 3004, 3001, 3002
SHOTGUN, SHELLS, CLIP, STIM, MEDIKIT, BONUS = 2001, 2008, 2007, 2011, 2012, 2014
BARREL, CANDLE, CANDELABRA, LAMP, TECHLAMP = 2035, 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55                                   # tall, tall, short
POOL, MESS, DEAD_IMP, DEAD_ZOMBIE = 24, 10, 20, 18


def things(kind, *spots, angle=0):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle)


# the cell: nothing but two candles
things(CANDLE, (20, -1480), (236, -1480))
# the hall: two zombies with their backs to a pair of barrels, a shotgun on
# the way to the pit, red torches by the RED far side
things(ZOMBIE, (540, 470), (600, 170), angle=180)
things(BARREL, (690, 60), (724, 100))
things(TORCH_R, (24, 232), (24, 408))
things(SHOTGUN, (300, 500))
things(SHELLS, (330, 520))
things(STIM, (40, 40))
# the pit: a demon, and what it left of the last visitors
things(DEMON, (896, 180), angle=90)
things(POOL, (820, 90), (980, 300))
things(MESS, (960, 470))
things(DEAD_ZOMBIE, (830, 520))
things(DEAD_IMP, (990, 70))
things(CLIP, (800, 600))
# the ledge: an imp throwing across the pit, lamps by the YELLOW far side
things(IMP, (1160, 150), angle=180)
things(CANDELABRA, (1256, 232), (1256, 408))
things(LAMP, (1256, 24), (1256, 616))
things(SHELLS, (1200, 560))
things(STIM, (1100, 610))
# the gallery: an imp looking down into the hall, blue torches
things(IMP, (610, 740), angle=270)
things(TORCH_B, (304, 808), (464, 808))
things(BONUS, (100, 736), (140, 736), (180, 736), (220, 736))
things(STIM, (40, 808))
# the vault: two imps keeping the VIOLET door, green torches in the corners
things(IMP, (2210, 60), (2210, 260), angle=180)
things(TORCH_G, (2024, 24), (2024, 296), (2296, 24), (2296, 296))
things(MEDIKIT, (2270, 90))
things(SHELLS, (2270, 230))
# the way out: one last zombie, lamps by the switch
things(ZOMBIE, (3250, 200), angle=180)
things(TECHLAMP, (3296, 56), (3296, 200))

# The same level as a graph, for tools/solve.py. Keep in step with the above.
PUZZLE = dict(
    start="cell", goal="exit", names=ajarmap.NAMES,
    walk=[("hall", "pit"), ("ledge", "pit"), ("gallery", "hall")],
    frames={101: "cell", 102: "hall", 103: "pit", 104: "gallery"},
    doors={
        RED: dict(home="hall", lean="cell"),
        YELLOW: dict(home="ledge", frame=103),
        BLUE: dict(home="gallery", lean="ledge"),
        GREEN: dict(home="vault", lean="gallery"),
        VIOLET: dict(home="exit", lean="vault"),
    },
)
