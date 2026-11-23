"""The pass lab (map PASS): MAP=PASS ./run.sh

An engine lab for MAP19's outline ("MAP19 'On Paper'": the pass and its
double; PLAN.md, "The pass lab"). The player has a pass; a white double
stands where the pass says the player is: on the player to begin with, and
after every crossing of a line portal it goes on as if the portal line had
been a hole in the wall (src/zscript/pass.zs). Registers are plates in
sealed rooms that the double has to stand on; a pass desk puts the double
back on the player.

Bays off one corridor (y -320..-192), west to east, each room told apart
by its walls, floor and tint. Frames 101..108; far sides RED, GREEN, BLUE;
both TEAL leaves in bay 5, both ORANGE leaves in bay 6.
  desk  a pass desk (a plate across the corridor) at the start, and a
        second at the corridor's east end
  1 see it: hall H1, frame 101 in its north wall, the sealed duty room S1
    behind it (register 1, 96 in from its wall), glass beside the frame.
    RED's far side is in H1's south wall: stepping out of it you look at
    the glass. S1's steel door (register 1's) opens to a passage east.
  2 room to walk: H2, frame 102, the sealed stack S2 700 deep behind it,
    register 2 at its far end. RED's far side has about 300 of floor
    ahead; GREEN's (bay G: a corridor 256 wide and 1024 long) has 1024.
  3 turned: H3, frame 103 in its east wall (a right angle to GREEN's far
    side's facing), the sealed S3 behind, register 3 off to one side.
  4 a floor up: H4, frame 104, the sealed S4 behind whose back half is a
    mezzanine 128 up (register 4). BLUE's far side (room B4) is at the foot
    of a stair of 128, with a lift car beside the stair.
  5 the corridor that goes on: C5, 768 long, frame 105 in its west end wall
    and 106 in its east, facing each other. Beyond the east wall the
    corridor goes on, sealed, 2400 more (glass beside 106), register 5 2000
    beyond the wall.
  6 the stair that goes on: a flight of 8 steps (128 down over 256), frame
    107 in the wall at its foot facing up it, 108 at its head facing down.
    Beyond the foot's wall the stair goes on down three more flights,
    sealed (glass beside 107), register 6 at the bottom of the third. The
    sealed stair's landings are 288 long, not 128: see below.
  7 the building's own: a fixed gate pair (GA's north wall to GB's east
    wall), and a one-sided doorway (A to B plain, B back through it lands
    in C, as map ONESIDE's bay 1).

The pumps: a lap of bay 5 is the distance between the portal lines of 105
and 106, 768 + 16 + 16 = 800; a lap of bay 6 is 544 along (head landing
128 + flight 256 + foot landing 128 + two recesses of 16) and 128 down. For
the double to walk the real sealed corridor and stair, the sealed part has
to repeat with that period: the stair's landings are 128 + 16 + 16 + 128.
The checks are in src/zscript/passtest.zs (MODE=1..5 tools/smoke.sh).
"""
import ajarmap
from ajarmap import RED, GREEN, BLUE, TEAL, ORANGE, far_id, LIFT, DEPTH, STUB, DOOR_H
from udmf import Map, rect

m = Map()
DESK_T, REGISTER_T = 20132, 20133      # AjarPassDesk, AjarPassRegister (src/zscript/pass.zs)

LOOKS = {   # wall, floor, light, tint
    "corr": ("GRAY1", "FLAT5_4", 170, 0xF0F0F0),
    "H1": ("STARTAN3", "FLOOR0_1", 200, 0xD0FFD0),
    "S1": ("BRICK7", "FLAT14", 230, 0xC8D8FF),
    "H2": ("WOOD1", "FLOOR7_1", 200, 0xFFF0C8),
    "S2": ("STONE2", "FLAT1", 220, 0xE0E0FF),
    "G": ("ASHWALL2", "RROCK09", 180, 0xFFD8FF),
    "H3": ("MARBLE1", "FLOOR4_8", 190, 0xFFC0A8),
    "S3": ("TANROCK2", "FLAT5_3", 220, 0xFFFFC0),
    "H4": ("PANEL1", "GRASS1", 220, 0xD8FFE8),
    "S4": ("COMPBLUE", "FLAT3", 200, 0xC0E8FF),
    "B4": ("BROWN1", "FLOOR1_1", 200, 0xFFE8D0),
    "C5": ("BIGBRIK1", "SLIME13", 210, 0xE8FFC0),
    "S5": ("ICKWALL1", "FLAT22", 200, 0xFFB0B0),
    "C6": ("STONE2", "FLAT1", 190, 0xE0E0FF),
    "S6": ("BRICK7", "FLAT14", 200, 0xC8D8FF),
    "GA": ("STARTAN3", "FLOOR0_1", 200, 0xD0FFD0),
    "GB": ("MARBLE1", "FLOOR4_8", 190, 0xFFC0A8),
    "A": ("STARTAN3", "FLOOR0_1", 200, 0xD0FFD0),
    "B": ("BRICK7", "FLAT14", 240, 0xC8D8FF),
    "C": ("MARBLE1", "FLOOR4_8", 190, 0xFFC0A8),
}
PLATE = "GATE3"         # a register's plate
DESK = "FLAT23"         # a pass desk


def room(name, box, floor=0, ceil=None, **k):
    wall, flat, light, tint = LOOKS[name]
    return m.sector(rect(*box), floor=floor, ceil=floor + 192 if ceil is None else ceil, light=light,
                    wall=wall, ftex=flat, ctex="CEIL5_1", color=tint, **k)


def plated(name, box, plate, floor=0, ceil=None):
    """A room with a plate in its floor: five rectangles."""
    x1, y1, x2, y2 = box
    px1, py1, px2, py2 = plate
    wall, flat, light, tint = LOOKS[name]
    for b in ((x1, y1, px1, y2), (px2, y1, x2, y2), (px1, y1, px2, py1), (px1, py2, px2, y2)):
        if b[0] < b[2] and b[1] < b[3]:
            room(name, b, floor, ceil)
    m.sector(rect(*plate), floor=floor, ceil=floor + 192 if ceil is None else ceil, light=min(255, light + 30),
             wall=wall, ftex=PLATE, ctex="CEIL5_1", color=tint)


def register(n, x, y, tag, half=32):
    """Register n (AjarPassRegister): its plate is the box 2*half square
    round x, y; signed, it opens the steel door with `tag`."""
    m.thing(x, y, REGISTER_T, args=(half, half, tag, n))


def glass(box, face):
    """A window through a wall: the sector `box`, its line `face` (a, b) the
    pane, which nothing passes and everything sees through."""
    x1, y1, x2, y2 = box
    m.sector(rect(*box), floor=24, ceil=168, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(*face, blocking=True, blockeverything=True)


def glass_at(box, face, floor):
    m.sector(rect(*box), floor=floor + 24, ceil=floor + 168, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(*face, blocking=True, blockeverything=True)


def frame(a, b, out, n, floor=0):
    ajarmap.recess(m, a, b, out, floor, n, far_id(RED))


def far(a, b, out, colour, floor=0):
    ajarmap.recess(m, a, b, out, floor, far_id(colour), 101, far_colour=colour)


def gate(m1, m2, out, line_id, target, floor=0):
    """An opening in a room's wall with a portal at its back, joined from the
    start (as map ENG's, map ONESIDE's): the building's own doorway."""
    b1, b2 = (m1[0] + out[0] * DEPTH, m1[1] + out[1] * DEPTH), (m2[0] + out[0] * DEPTH, m2[1] + out[1] * DEPTH)
    c1, c2 = (b1[0] + out[0] * STUB, b1[1] + out[1] * STUB), (b2[0] + out[0] * STUB, b2[1] + out[1] * STUB)
    look = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.sector([m1, m2, b2, b1], floor=floor, ceil=floor + DOOR_H, light=176, **look)
    m.sector([b1, b2, c2, c1], floor=floor, ceil=floor + DOOR_H, light=96, **look)
    m.line(b1, b2, id=line_id, special=156, args=(target, 0, 1, 1))


def neck(x1, x2):
    room("corr", (x1, -192, x2, 0), ceil=128)


# --- the corridor, with a pass desk at each end ------------------------------------------------
room("corr", (-64, -320, 128, -192))
m.sector(rect(128, -320, 192, -192), ceil=192, light=210, wall="GRAY1", ftex=DESK, ctex="CEIL5_1")
room("corr", (192, -320, 9440, -192))
m.sector(rect(9440, -320, 9504, -192), ceil=192, light=210, wall="GRAY1", ftex=DESK, ctex="CEIL5_1")
room("corr", (9504, -320, 9600, -192))
m.thing(160, -256, DESK_T, args=(32, 64))
m.thing(9472, -256, DESK_T, args=(32, 64))
m.thing(64, -256, 1, angle=0)

# --- 1: see it ----------------------------------------------------------------------------------
room("H1", (0, 0, 512, 320))
neck(32, 96)
frame((64, 320), (128, 320), (0, 1), 101)
plated("S1", (0, 400, 512, 720), (64, 464, 128, 528))
register(1, 96, 496, 11)
glass((144, 320, 480, 400), ((144, 320), (480, 320)))
far((352, 0), (288, 0), (0, -1), RED)                  # RED's far side: out of it, facing the glass
ajarmap.steel(m, (512, 560), (512, 624), (1, 0), 0, 11)
room("corr", (528, -192, 592, 640), ceil=128)          # the duty room's way out, to the corridor
ajarmap.door(m, RED, 420, 160, angle=270)

# --- 2: room to walk ------------------------------------------------------------------------------
room("H2", (800, 0, 1312, 320))
neck(832, 896)
frame((1024, 320), (1088, 320), (0, 1), 102)
plated("S2", (960, 400, 1280, 1100), (1024, 1008, 1088, 1072))
register(2, 1056, 1040, 12)
ajarmap.steel(m, (1200, 320), (1264, 320), (0, 1), 0, 12, thick=80)
# GREEN's far side: the end of a corridor 256 wide and 1024 long
room("G", (1500, 0, 1756, 1024), ceil=160)
far((1660, 0), (1596, 0), (0, -1), GREEN)
neck(1676, 1740)
ajarmap.door(m, GREEN, 1200, 160, angle=270)

# --- 3: turned ----------------------------------------------------------------------------------
room("H3", (2000, 0, 2512, 320))
neck(2032, 2096)
frame((2512, 128), (2512, 192), (1, 0), 103)
plated("S3", (2592, 0, 3104, 448), (2896, 224, 2960, 288))
register(3, 2928, 256, 13)
ajarmap.steel(m, (2512, 240), (2512, 304), (1, 0), 0, 13, thick=80)

# --- 4: a floor up ------------------------------------------------------------------------------
room("H4", (3300, 0, 3812, 320))
neck(3332, 3396)
frame((3524, 320), (3588, 320), (0, 1), 104)
room("S4", (3400, 400, 3800, 700), ceil=320)
plated("S4", (3400, 700, 3800, 1100), (3524, 868, 3588, 932), floor=128, ceil=320)
register(4, 3556, 900, 14)
ajarmap.steel(m, (3700, 320), (3764, 320), (0, 1), 0, 14, thick=80)
# BLUE's far side, at the foot of a stair of 128; a lift car beside the stair, its top at the landing
room("B4", (3950, 0, 4334, 64), ceil=384)
far((4110, 0), (4046, 0), (0, -1), BLUE)
wall, flat, light, tint = LOOKS["B4"]
ajarmap.stairs(m, (3950, 64), (4206, 64), (0, 1), 0, 128, steps=8, depth=32, ceil=384, light=light, wall=wall,
               ftex=flat, ctex="CEIL5_1", color=tint)
room("B4", (4206, 64, 4334, 192), ceil=384)
m.sector(rect(4206, 192, 4334, 320), floor=0, ceil=384, light=230, wall="SUPPORT3", ftex="FLAT23", ctex="CEIL5_1",
         id=LIFT, color=0xFFF0C0)
room("B4", (3950, 320, 4334, 800), floor=128, ceil=384)
neck(4254, 4318)
ajarmap.lift_button(m, (4334, 208), (4334, 240), 128, 741, (4300, 224))
ajarmap.lift_button(m, (4334, 272), (4334, 304), 0, 742, (4300, 288))
ajarmap.door(m, BLUE, 3400, 200, angle=270)

# --- 5: the corridor that goes on -----------------------------------------------------------------
C5 = (4600, 0, 5368, 256)
room("C5", C5)
neck(4900, 4964)
frame((4600, 160), (4600, 96), (-1, 0), 105)
frame((5368, 96), (5368, 160), (1, 0), 106)
glass((5368, 176, 5448, 240), ((5368, 176), (5368, 240)))
plated("C5", (5448, 0, 7848, 256), (7336, 96, 7400, 160))      # the same corridor going on, sealed
register(5, 7368, 128, 15)
ajarmap.steel(m, (4700, 256), (4764, 256), (0, 1), 0, 15)
room("S5", (4668, 272, 4796, 400))
ajarmap.pair(m, TEAL, (4700, 200, 0), (5250, 200, 180))

# --- 6: the stair that goes on --------------------------------------------------------------------
X1, X2 = 7936, 8256
room("C6", (X1, 0, X2, 128), ceil=192)                          # the head
neck(7952, 8016)
frame((8128, 0), (8064, 0), (0, -1), 108)                       # facing down the flight
wall, flat, light, tint = LOOKS["C6"]
STEP = dict(light=light, wall=wall, ftex=flat, ctex="CEIL5_1", color=tint)
ajarmap.stairs(m, (X1, 128), (X2, 128), (0, 1), 0, -128, steps=8, depth=32, ceil=192, **STEP)
room("C6", (X1, 384, X2, 512), floor=-128, ceil=192)            # the foot
frame((8064, 512), (8128, 512), (0, 1), 107, -128)              # facing up the flight
glass_at((8144, 512, 8240, 592), ((8144, 512), (8240, 512)), -128)
# the stair going on, sealed: it repeats with the lap's period, 544 along and 128 down
wall, flat, light, tint = LOOKS["S6"]
SEAL = dict(light=light, wall=wall, ftex=flat, ctex="CEIL5_1", color=tint)
m.sector(rect(X1, 592, X2, 672), floor=-128, ceil=64, **SEAL)
z, y = -128, 672
for k in range(3):
    ajarmap.stairs(m, (X1, y), (X2, y), (0, 1), z, -128, steps=8, depth=32, ceil=z + 192, **SEAL)
    z, y = z - 128, y + 256
    if k < 2:
        m.sector(rect(X1, y, X2, y + 288), floor=z, ceil=z + 192, **SEAL)
        y += 288
plated("S6", (X1, y, X2, y + 184), (8064, 2048, 8128, 2112), floor=z, ceil=z + 192)
assert (y, z) == (2016, -512)
register(6, 8096, 2080, 16)
ajarmap.steel(m, (8256, 416), (8256, 480), (1, 0), -128, 16)
room("S5", (8272, 384, 8400, 512), floor=-128)
ajarmap.pair(m, ORANGE, (7980, 64, 90), (8220, 440, 90))

# --- 7: the building's own --------------------------------------------------------------------------
room("GA", (8600, 0, 8856, 256))
neck(8632, 8696)
room("GB", (8600, 1200, 8856, 1456))
gate((8696, 256), (8760, 256), (0, 1), 701, 702)                  # GA's north wall ...
gate((8856, 1296), (8856, 1360), (1, 0), 702, 701)                # ... and GB's east wall
room("A", (9000, 0, 9256, 256))
room("B", (9000, 272, 9256, 528))
room("C", (9000, 1200, 9256, 1456))
neck(9032, 9096)
ajarmap.oneside(m, (9096, 256), (9160, 256), (0, 1), 0, 711, 712)    # the odd face (y 272) faces B
gate((9096, 1456), (9160, 1456), (0, 1), 712, 711)                # C's opening, in its north wall
room("corr", (9272, -192, 9336, 528), ceil=128)                  # B's way back to the corridor
room("corr", (9256, 400, 9272, 464), ceil=128)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
