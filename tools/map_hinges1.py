"""Act 1, level 1: "Borrowed Rooms" (MAP01).

You start locked in a cell with a door and a frame. The hall beyond is cut
by a pit; the only way out of the pit is the door hanging in it. Every door
you need is somewhere the last one leads.
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
m.sector(rect(0, -1500, 256, -1244), ceil=128, light=170)
recess((96, -1244), (160, -1244), (0, 1), 0, 101, 201)                    # frame, empty

# --- the hall (RED's far side), the pit, the ledge (YELLOW's far side) -----
m.sector(rect(0, 0, 768, 640), ceil=TALL, light=200, color=WARM)
m.sector(rect(768, 0, 1024, 640), floor=-192, ceil=TALL, light=176, ftex="AJPIT", wall="AJTRIM")
m.sector(rect(1024, 0, 1280, 640), ceil=TALL, light=210, color=GOLD)
recess((0, 288), (0, 352), (-1, 0), 0, far_id(RED), 101, far_colour=RED, color=WARM)
recess((352, 0), (416, 0), (0, -1), 0, 102, 201)                          # hall frame, empty
recess((864, 640), (928, 640), (0, 1), -192, 103, 201)                    # pit frame, starts with YELLOW
recess((1280, 288), (1280, 352), (1, 0), 0, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)

# --- the gallery above the hall (BLUE's far side): you can only drop off it --
m.sector(rect(0, 640, 768, 832), floor=160, ceil=TALL, light=210, color=SKY)
recess((352, 832), (416, 832), (0, 1), 160, far_id(BLUE), 101, far_colour=BLUE, color=SKY)
recess((0, 704), (0, 768), (-1, 0), 160, 104, 201, color=SKY)             # gallery frame, empty

# --- the vault (GREEN's far side): no frame, only the VIOLET door ----------
m.sector(rect(2000, 0, 2320, 320), ceil=160, light=220, color=LEAF)
recess((2000, 128), (2000, 192), (-1, 0), 0, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)

# --- the way out (VIOLET's far side) ---------------------------------------
m.sector([(3000, 0), (3000, 256), (3320, 256), (3320, 160), (3320, 96), (3320, 0)],
         ceil=160, light=220, color=PLUM)
recess((3000, 96), (3000, 160), (-1, 0), 0, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)
m.line((3320, 96), (3320, 160), special=243, playeruse=True, mid="AJEXIT", exact=True)

# --- things ----------------------------------------------------------------
m.thing(128, -1420, 1, angle=90)                                          # player start
ajarmap.door(m, RED, 48, -1258, angle=270)                               # leaning in the cell
ajarmap.door(m, YELLOW, 896, 600, frame=103)                              # hanging in the pit
ajarmap.door(m, BLUE, 1266, 128, angle=180)                               # leaning on the ledge
ajarmap.door(m, GREEN, 754, 700, angle=180)                               # leaning on the gallery
ajarmap.door(m, VIOLET, 2306, 160, angle=180)                             # leaning in the vault

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
