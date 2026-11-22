"""The one-sided doorway lab (map ONESIDE): MAP=ONESIDE ./run.sh

A doorway that is ordinary from one side and leads elsewhere from the other
(PLAN.md, "Idea: one-sided portals"; ajarmap.oneside). Bays off one corridor,
west to east; no carried doors. Each room has its own walls, floor, tint and
light:
  1 the turn-round: A (green, STARTAN3), north of it B (blue, BRICK7), and
    far away C (red, MARBLE1). From A the doorway is a plain way into B; from
    B it shows C and leads into C through the opening in C's north wall,
    facing south into C. C's opening is a plain portal back: out of it you
    come out of the doorway into B (B's face and C's opening are a normal
    pair; only A's side is odd). B has a way back to the corridor on foot.
  2 (what comes back from C: in bay 1.)
  3 the longer way back: P (west), a corridor 256 long east to Q, the
    doorway at its east end. Coming back west from Q the doorway leads into X,
    a corridor 752 long far away, whose west end puts you out of the
    doorway's plain mouth into the corridor, heading west: 1024 in all.
  4 bigger inside: a booth 160 square in a hall, walls 16 thick, a plain
    opening at its back. Its front doorway, from the hall, shows and leads
    into R, a room 768 square; R's opening leads back out to the hall. From
    inside the booth (in by its back) the front is a plain way out.
  5 one-way sight: the player's room PL (south) and the monsters' room MR
    (north). From PL the doorway shows MR; from MR it shows and leads to E.
    Its odd face blocks monsters' sight (blind=True). MR has a way round on
    foot to the corridor.
The checks are in src/zscript/oneside.zs (MODE=1..6 tools/smoke.sh).
"""
from ajarmap import oneside, opening, DEPTH, STUB, DOOR_H
from udmf import Map, rect

m = Map()


def gate(m1, m2, out, line_id, target):
    """An opening in a room's wall with a portal at its back, fixed from the
    start (as map ENG's): a DEPTH-deep recess and a STUB behind its line."""
    b1, b2 = (m1[0] + out[0] * DEPTH, m1[1] + out[1] * DEPTH), (m2[0] + out[0] * DEPTH, m2[1] + out[1] * DEPTH)
    c1, c2 = (b1[0] + out[0] * STUB, b1[1] + out[1] * STUB), (b2[0] + out[0] * STUB, b2[1] + out[1] * STUB)
    look = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.sector([m1, m2, b2, b1], ceil=DOOR_H, light=176, **look)
    m.sector([b1, b2, c2, c1], ceil=DOOR_H, light=96, **look)
    m.line(b1, b2, id=line_id, special=156, args=(target, 0, 1, 1))


LOOKS = {   # wall, floor, light, tint
    "A": ("STARTAN3", "FLOOR0_1", 200, 0xD0FFD0),
    "B": ("BRICK7", "FLAT14", 240, 0xC8D8FF),
    "C": ("MARBLE1", "FLOOR4_8", 190, 0xFFC0A8),
    "P": ("WOOD1", "FLOOR7_1", 200, 0xFFF0C8),
    "Q": ("STONE2", "FLAT1", 220, 0xE0E0FF),
    "X": ("ASHWALL2", "RROCK09", 150, 0xFFD8FF),
    "H": ("GRAY1", "FLAT5_4", 210, 0xF0F0F0),
    "R": ("PANEL1", "GRASS1", 255, 0xD8FFE8),
    "S": ("COMPBLUE", "FLAT3", 180, 0xC0E8FF),
    "PL": ("BROWN1", "FLOOR1_1", 200, 0xFFE8D0),
    "MR": ("BIGBRIK1", "SLIME13", 230, 0xE8FFC0),
    "E": ("ICKWALL1", "FLAT22", 160, 0xFFB0B0),
    "T": ("TANROCK2", "FLAT5_3", 200, 0xFFFFC0),
}


def room(name, box, ceil=192):
    wall, flat, light, tint = LOOKS[name]
    return m.sector(rect(*box), ceil=ceil, light=light, wall=wall, ftex=flat, ctex="CEIL5_1", color=tint)


# --- the corridor -------------------------------------------------------------
m.sector(rect(-64, -192, 3200, -64), light=160)
m.thing(112, -128, 1, angle=90)


def neck(x1, x2, y2=32):
    m.sector(rect(x1, -64, x2, y2), light=160)


# --- 1 and 2: A, B, C -----------------------------------------------------------
room("A", (0, 32, 384, 352))
room("B", (0, 368, 384, 688))
room("C", (0, 1200, 384, 1520))
neck(160, 224)
oneside(m, (160, 352), (224, 352), (0, 1), 0, 401, 402)       # the odd face (y 368) faces B
gate((160, 1520), (224, 1520), (0, 1), 402, 401)               # C's opening, in its north wall
# C2: a room for a turned far side (its opening in its west wall); the odd face
# leads here only when MODE=1 points it here with Line_SetPortalTarget
room("T", (0, 2000, 384, 2320))
gate((0, 2128), (0, 2192), (-1, 0), 403, 401)
m.sector(rect(400, -64, 464, 688), light=160)                  # B's way back to the corridor
m.sector(rect(384, 560, 400, 624), light=160)
# Both ends of that neck block sound (Doom's rule: sound stops at the second
# such line), so that what is heard in A from B is heard through the doorway.
m.line((384, 560), (384, 624), blocksound=True)
m.line((400, 560), (400, 624), blocksound=True)
m.thing(32, 64, 2028)
m.thing(32, 656, 2028)
m.thing(32, 1232, 2028)

# --- 3: the longer way back -----------------------------------------------------
room("P", (800, 96, 960, 256))
m.sector(rect(960, 144, 1200, 208), ceil=128, light=200, wall="WOOD1", ftex="FLOOR7_1", ctex="CEIL5_1", color=0xFFF0C8)   # M
room("Q", (1216, 96, 1376, 256))
oneside(m, (1200, 144), (1200, 208), (1, 0), 0, 411, 413, mouth_id=412)   # the odd face (x 1216) faces Q
m.sector(rect(800, 1800, 1552, 1864), ceil=128, light=150, wall="ASHWALL2", ftex="RROCK09", ctex="CEIL5_1", color=0xFFD8FF)   # X
gate((1552, 1800), (1552, 1864), (1, 0), 413, 411)            # X's east end: back out into Q
gate((800, 1800), (800, 1864), (-1, 0), 414, 412)             # X's west end: out of the doorway's mouth, west
neck(848, 912, 96)
neck(1264, 1328, 96)

# --- 4: bigger inside -----------------------------------------------------------
HX1, HY1, HX2, HY2 = 1700, 32, 2340, 640                       # the hall
BX1, BY1, BX2, BY2 = 1940, 300, 2100, 460                      # the booth, outside
for box in ((HX1, HY1, HX2, BY1), (HX1, BY2, HX2, HY2), (HX1, BY1, BX1, BY2), (BX2, BY1, HX2, BY2)):
    room("H", box)
room("S", (BX1 + 16, BY1 + 16, BX2 - 16, BY2 - 16), ceil=128)  # inside the booth: 128 square
oneside(m, (1988, BY1 + 16), (2052, BY1 + 16), (0, -1), 0, 421, 422, wall="COMPBLUE", flat="FLAT3")   # the odd face (y 300) faces the hall
opening(m, (1988, BY2 - 16), (2052, BY2 - 16), (0, 1), 0)      # the booth's back: a plain opening
room("R", (1700, 2400, 2468, 3168), ceil=256)
gate((2052, 2400), (2116, 2400), (0, -1), 422, 421)            # R's way out, in its south wall
neck(1990, 2054)
m.thing(1720, 52, 2028)
m.thing(1720, 3148, 2028)
m.thing(2448, 3148, 2028)

# --- 5: one-way sight -----------------------------------------------------------
room("PL", (2600, 32, 2984, 352))
room("MR", (2600, 368, 2984, 816))
room("E", (2600, 1400, 2984, 1720))
oneside(m, (2760, 352), (2824, 352), (0, 1), 0, 431, 432, blind=True)   # the odd face (y 368) faces MR
gate((2760, 1720), (2824, 1720), (0, 1), 432, 431)             # E's way out: back into MR
neck(2760, 2824)
m.sector(rect(3000, -64, 3064, 816), light=160)                # MR's way round to the corridor
m.sector(rect(2984, 720, 3000, 784), light=160)
m.line((2984, 720), (2984, 784), blocksound=True)                # as B's way back (bay 1)
m.line((3000, 720), (3000, 784), blocksound=True)
for x in (2680, 2792, 2904):                                   # MR's monsters, for play by hand
    m.thing(x, 640, 3001, angle=270)
m.thing(2730, 720, 3004, angle=270)
m.thing(2860, 720, 3004, angle=270)

# --- a sealed room, the control for the sound test (MODE=5) ---------------------
m.sector(rect(3300, 1400, 3428, 1528), light=120)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
