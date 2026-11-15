"""Act 1, level 3: "Stage Door" (MAP03).

A theatre. The way out is the RED door, leaning up in the gods at the back
of the house. Nearly every door here opens onto a ledge: you can step out
onto the box, the gods or the flies, but the only way on from there is to
drop, and you cannot climb back. The stage is too high to climb from the
stalls, and the trap at the back of it is a pit whose one way out is the
YELLOW door hanging in it.

New here: doors that are one-way trips, a door hung where you need it for
the way back, and needing free hands at the far end of a drop.

Foyer =(doorway)= stalls -> dressing room (VIOLET's far side) -> box
(BLUE's) -> flies (GREEN's) -> stage -> trap -> gods (YELLOW's) -> the
alley (RED's).
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


HOUSE = 384                                       # auditorium ceiling
STAGE, TRAP, BOX, GODS, FLIES = 64, -128, 144, 208, 256
WARM, GOLD, SKY, LEAF, PLUM = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF
OPEN = dict(ctex="F_SKY1", wall="AJBRICK")

# --- the foyer: start here; a stone doorway leads into the house ------------
m.sector(rect(2000, 0, 2384, 320), ceil=160, light=200)
ajarmap.doorway(m, 1, (64, 640), (128, 640), (0, 1), 0, (2384, 128), (2384, 192), (1, 0), 0)

# --- the stalls: an aisle down to the stage, two frames in the south wall ---
ajarmap.room(m, [0, 640], [0, 288, 352, 640], lambda i, j: j == 1, ceil=HOUSE - 16, light=170)
recess((128, 0), (192, 0), (0, -1), 0, 102, 201)                          # stalls frames, empty
recess((384, 0), (448, 0), (0, -1), 0, 103, 201)

# --- the stage, too high to climb, and the trap at the back of it ----------
BOARDS = dict(floor=STAGE, ceil=HOUSE, light=200, wall="AJCURT", ftex="AJBOARD")
for xs, ys in (((640, 832), (0, 640)), ((832, 1024), (0, 224)), ((832, 1024), (416, 640))):
    m.sector(rect(xs[0], ys[0], xs[1], ys[1]), **BOARDS)
m.sector(rect(832, 224, 1024, 416), floor=TRAP, ceil=HOUSE, light=120, wall="AJTRIM", ftex="AJPIT")
recess((896, 640), (960, 640), (0, 1), STAGE, 105, 201)                   # stage frame, empty
recess((1024, 288), (1024, 352), (1, 0), TRAP, 104, 201)                  # trap frame, starts with YELLOW

# --- the box (BLUE's far side): a ledge over the stalls ----------------------
m.sector(rect(192, 640, 448, 832), floor=BOX, ceil=HOUSE - 16, light=190, color=SKY)
recess((288, 832), (352, 832), (0, 1), BOX, far_id(BLUE), 101, far_colour=BLUE, color=SKY)

# --- the gods (YELLOW's far side): the back of the house, high up -----------
m.sector(rect(-224, 128, 0, 512), floor=GODS, ceil=HOUSE - 16, light=180, color=GOLD)
recess((-224, 288), (-224, 352), (-1, 0), GODS, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)

# --- the flies (GREEN's far side): a catwalk over the stage ------------------
m.sector(rect(640, -192, 1024, 0), floor=FLIES, ceil=HOUSE, light=180, color=LEAF, wall="AJTRIM")
recess((800, -192), (864, -192), (0, -1), FLIES, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)

# --- the dressing room (VIOLET's far side): a dead end ----------------------
m.sector(rect(3000, 0, 3320, 320), ceil=160, light=210, color=PLUM)
recess((3000, 128), (3000, 192), (-1, 0), 0, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)

# --- the alley behind the theatre (RED's far side) ---------------------------
m.sector(rect(5000, 0, 5448, 192), ceil=160, light=200, color=WARM, ftex="AJPIT", **OPEN)
recess((5000, 64), (5000, 128), (-1, 0), 0, far_id(RED), 101, far_colour=RED, color=WARM)
m.cut((5448, 64), (5448, 128))
m.line((5448, 64), (5448, 128), special=243, playeruse=True, mid="AJEXIT", exact=True)

# --- things ----------------------------------------------------------------
m.thing(2100, 160, 1, angle=0)                                            # player start, facing the doorway
ajarmap.door(m, VIOLET, 2200, 306, angle=270)                             # leaning in the foyer
ajarmap.door(m, BLUE, 3306, 256, angle=180)                               # leaning in the dressing room
ajarmap.door(m, GREEN, 420, 818, angle=270)                               # leaning on the box
ajarmap.door(m, YELLOW, 1000, 320, frame=104)                             # hanging in the trap
ajarmap.door(m, RED, -80, 498, angle=270)                                 # leaning up in the gods

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, REVENANT, SOUL = 65, 69, 66, 3006                   # new in this level
SHOTGUN, SUPER, SHELLS, SHELLBOX, CLIP, AMMOBOX, STIM, MEDIKIT, BONUS, ARMOR = (
    2001, 82, 2008, 2049, 2007, 2048, 2011, 2012, 2014, 2018)
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, DEAD_ZOMBIE = 24, 18


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the foyer: quiet. A shotgun for anyone who came without one.
things(SHOTGUN, (2060, 60))
things(SHELLS, (2090, 60), (2120, 60))
things(STIM, (2060, 280))
things(CANDELABRA, (2024, 24), (2024, 296))
things(LAMP, (2360, 88), (2360, 232))
# the stalls: an audience of imps and former humans; the lodger wakes when
# you are well into the house (250 units from the middle of it)
things(IMP, (500, 120), (500, 520), (560, 320), angle=180)
things(ZOMBIE, (300, 200), (300, 440), angle=180)
things(LAMP, (24, 24), (24, 616))
things(CLIP, (40, 320))
things(MEDIKIT, (600, 600))
things(LODGER, (320, 320), args=(250,))
# the stage: tonight's act, and the stage frame's footlights
things(KNIGHT, (740, 320), angle=180)
things(CANDELABRA, (664, 24), (664, 616))
things(SHELLBOX, (980, 60))
things(STIM, (980, 600))
# the trap: something you cannot quite see
things(SPECTRE, (880, 260), angle=90)
things(POOL, (900, 380))
# the box: the best seat, and the best gun
things(SUPER, (230, 790))
things(SHELLS, (230, 760), (260, 790))
things(TORCH_B, (216, 808), (424, 664))
# the gods: a sniper at the rail, lamps by the YELLOW far side
things(CHAINGUNNER, (-40, 200), angle=0)
things(CANDELABRA, (-200, 256), (-200, 384))
things(AMMOBOX, (-190, 160))
things(MEDIKIT, (-190, 480))
# the flies: two lost souls among the ropes, green torches
things(SOUL, (700, -96), (960, -96), angle=90)
things(TORCH_G, (768, -168), (896, -168))
things(BONUS, (680, -160), (984, -160))
# the dressing room: the rest of the company
things(SERGEANT, (3240, 60), (3240, 260), angle=180)
things(IMP, (3160, 280), angle=180)
things(CANDELABRA, (3296, 24), (3296, 296))
things(STIM, (3040, 40))
things(SHELLS, (3040, 280))
# the alley: one last thing between you and the street
things(REVENANT, (5360, 96), angle=180)
things(TECHLAMP, (5424, 24), (5424, 168))
things(TORCH_R, (5024, 24), (5024, 168))

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# The foyer is part of "stalls": the doorway joins them for good.
PUZZLE = dict(
    start="stalls", goal="alley", names=ajarmap.NAMES,
    walk=[("box", "stalls"), ("gods", "stalls"), ("flies", "stage"), ("stage", "stalls"), ("stage", "trap")],
    frames={102: "stalls", 103: "stalls", 104: "trap", 105: "stage"},
    doors={
        VIOLET: dict(home="dressing", lean="stalls"),
        BLUE: dict(home="box", lean="dressing"),
        GREEN: dict(home="flies", lean="box"),
        YELLOW: dict(home="gods", frame=104),
        RED: dict(home="alley", lean="gods"),
    },
)
