"""The second secret level: "Double Shift" (MAP32), reached by MAP15's
secret way out (PLAN.md, "MAP32 rebuilt"). The first build of it is the lab
map SHIFT (tools/map_shift.py).

A works: five rooms in a row, each needing two or three of you in it at once
(earlier selves: src/zscript/plate.zs, goes.zs, shut.zs). Each room is its
own fight number, with its own box 1 and plate that forgets every go. A room
is over for good when it is left by a way that is not a time door; the way
from one room to the next goes one way only (a door that shuts behind, or a
drop). Every frame of a puzzle takes its own door and no other.

1. The plate (a room of goes). A sprung frame that takes VIOLET only, VIOLET
   leaning, its plate 352 from the mouth. Hang it, stand on the plate, out by
   the time door; the next go walks through while the earlier self holds it.
   VIOLET's far side is in room 2.
2. Two keys (a room of goes). A gallery and a pit 96 below it. Frame A on
   the gallery and frame B in the pit join the TEAL Pair only if both leaves
   are hung within two seconds (clock lamps), and they are 1850 apart on
   foot. YELLOW leans in the pit; its frame W (YELLOW only) is on the
   gallery; the pit is left only by its own time door or the joined Pair.
3. The press (a fight of goes). A hall 1536 by 1280 whose north third is a
   press; 34 monsters in the south and middle, then 10, then two
   cyberdemons. Ammunition for about a third of them: the press is the way.
4. The range (a fight of goes). A pen of 13 behind a shutter at the north end
   of a range 1400 long; the shutter's plate is in a booth behind glass, the
   firing spot at the south end.
5. The airlock (a room of goes). S, L and E in a row, joined by two sprung
   frames (GREEN, PINK) whose plates are each in the chamber before; in E
   two brass frames face each other, RED hung in one from the start: BLUE,
   which leans in S, in the other closes the chain (ajarmap.way_through, the
   night room), and walking it ends the level.

Every room has a glass case where it is entered, with figures of it solved.
Generator checks: every monster has room (ajartime.Crowd), every region of
a room reaches a time door on foot (ajartime.on_foot, covers), the plates'
distances, the walk from A to B, the cases sealed, the supplies of rooms 3
and 4 against their monsters' health.
"""
import ajarmap
import ajartime
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, TEAL, HOME, HOME2, far_id
from ajartime import walk
from udmf import Map, rect

m = Map()
ROOM = 0xE8E0D0
PIT = 0xC8C0B4
BOX = 0xFFE8C0
HALL = 0xE4E0D8
PEN = 0xD8C8B8
LOCK = 0xD8E4F0
END = 0xE0F0D8


def inlaid(c):
    """The brass of a frame that takes one door only, inlaid with its colour."""
    return f"AJXA{c}", f"AJXF{c}"


def spots(kind, *at, angle=0):
    for x, y in at:
        m.thing(x, y, kind, angle=angle)


def steel(k, a, b, out, floor):
    """The steel door that opens when fight k is won (time.zs)."""
    ajarmap.steel(m, a, b, out, floor, 3090 + 100 * k)


def case(a, b, out, floor, figures, *, deep=96, **look):
    """A glass case (ajartime.case) with figures in it: (x, y, what, kind,
    angle); asserted sealed and every figure inside it."""
    si = ajartime.case(m, a, b, out, floor, deep=deep, **look)
    xs = [a[0], b[0], a[0] + out[0] * (16 + deep), b[0] + out[0] * (16 + deep)]
    ys = [a[1], b[1], a[1] + out[1] * (16 + deep), b[1] + out[1] * (16 + deep)]
    for x, y, what, kind, ang in figures:
        assert min(xs) + 8 < x < max(xs) - 8 and min(ys) + 8 < y < max(ys) - 8, (x, y, what)
        ajartime.figure(m, x, y, what, kind=kind, angle=ang)
    CASES.append(si)
    return si


CASES = []
REGIONS = {}
JOIN = 70 * 23.6        # two seconds at the fastest run (strafing): how far apart two hangings that must be together are


# === 1. the plate: a room of goes ===========================================
# The start nook (south) is part of the room, so that going back to it does
# not end the room.
FIRST = len(m.polys)
F1 = 101
m.sector(rect(0, 0, 640, 512), ceil=192, light=200, color=ROOM)
m.sector(rect(224, -192, 416, 0), ceil=160, light=190, color=ROOM)
m.thing(320, -120, 1, angle=90)
ajartime.zone(m, 1, 0, 0, -192, 640, 512, grow=72, goes=True)
ajartime.hall_door(m, 1, 1, (0, 96), (0, 160), (-1, 0), 0, color=ROOM)
m.sector(rect(-400, 32, -208, 224), ceil=160, light=210, color=BOX)
ajartime.box_door(m, 1, 1, (-208, 96), (-208, 160), (1, 0), 0, color=BOX)
ajartime.zone(m, 1, 1, -400, 32, -208, 224, grow=64)
ajartime.anew(m, -398, 128, 0)
# the sprung frame that takes VIOLET only, VIOLET by the wall, the plate out in the room
ajarmap.recess(m, (160, 512), (224, 512), (0, 1), 0, F1, far_id(VIOLET), home=far_id(VIOLET), only=True,
               trim=inlaid(VIOLET), color=ROOM)
ajarmap.door(m, VIOLET, 560, 420, angle=180)
P1 = (192, 160)
ajartime.plate(m, *P1, F1)
assert walk(P1, (192, 512)) >= 300
# the case, in the north wall: the player on the plate, VIOLET hanging
case((384, 512), (576, 512), (0, 1), 0, [(430, 570, "plate", 0, 0), (430, 570, "me", 0, 270),
                                       (520, 590, "hung", VIOLET, 270)], color=ROOM)
REGIONS[1] = ajartime.on_foot("room 1", {"hall": (0, -192, 640, 512), "box": (-400, 32, -208, 224)},
                              [("box", "hall")], {"hall": [(4, 128)], "box": [(-212, 128)]})
ajartime.covers(m, "room 1", FIRST, REGIONS[1], zone=(-72, -264, 712, 584), exempt=CASES)

# === 2. two keys: a room of goes =============================================
# A gallery (floor 0) and, east of it, a pit (floor -96): the gallery's east
# end is the pit's edge. Frame A in the gallery's west wall, frame B in the
# pit's north wall, a clock lamp by each; YELLOW in the pit, W (YELLOW only)
# in the gallery's south wall. VIOLET's far side (from room 1) is in the
# gallery's south wall, the case in its north wall.
FIRST = len(m.polys)
FA, FB, FW = 131, 132, 133
PITF = -96
m.sector(rect(2000, 0, 3280, 320), ceil=192, light=200, color=ROOM)
m.sector(rect(3280, -256, 3792, 640), floor=PITF, ceil=192, light=180, color=PIT, wall="AJBOLT")
ajartime.zone(m, 2, 0, 2000, 0, 3280, 320, grow=72, goes=True)
ajartime.zone(m, 2, 0, 3280, -256, 3792, 640, grow=72, goes=True)
ajarmap.recess(m, (2160, 0), (2224, 0), (0, -1), 0, far_id(VIOLET), F1, far_colour=VIOLET, color=ROOM)
spots(2011, (2140, 60), (2244, 60))         # stimpacks
spots(2012, (2192, 100))                    # medikit
spots(2049, (2300, 60))                     # shells
spots(2048, (2340, 60))                     # bullets
# A and B, their lamps and leaves
ajarmap.recess(m, (2000, 128), (2000, 192), (-1, 0), 0, FA, FB, home=TEAL, only=3, color=ROOM)
ajarmap.recess(m, (3664, 640), (3728, 640), (0, 1), PITF, FB, FA, home=TEAL, only=3, color=PIT)
ajartime.together(m, 2002, 224, 0, FA)
ajartime.together(m, 3760, 638, 270, FB)
LEAF_A, LEAF_B = (2100, 260), (3560, 560)
ajarmap.pair(m, TEAL, LEAF_A + (0,), LEAF_B + (270,))
# from before A along the gallery, over the edge and across the pit to before B
A_TO_B = walk((2040, 160), (3296, 160), (3696, 600))
assert A_TO_B >= 1400 and A_TO_B > JOIN, A_TO_B
# YELLOW in the pit; W, which takes it only, in the gallery's south wall
YELLOW_AT = (3700, -150)
ajarmap.door(m, YELLOW, *YELLOW_AT, angle=90)
ajarmap.recess(m, (2600, 0), (2664, 0), (0, -1), 0, FW, far_id(YELLOW), home=far_id(YELLOW), only=5,
               trim=inlaid(YELLOW), color=ROOM)
# time door 1 in the gallery's north wall, the box north of it; time door 2 in the pit's east wall
ajartime.hall_door(m, 2, 1, (2448, 320), (2512, 320), (0, 1), 0, color=ROOM)
ajartime.hall_door(m, 2, 2, (3792, -128), (3792, -64), (1, 0), PITF, color=PIT)
m.sector(rect(2384, 480, 2576, 672), ceil=160, light=210, color=BOX)
ajartime.box_door(m, 2, 1, (2448, 480), (2512, 480), (0, -1), 0, color=BOX)
ajartime.zone(m, 2, 1, 2384, 416, 2576, 672)
ajartime.anew(m, 2480, 670, 270)
# the case: both leaves hanging, both lamps green, YELLOW in W
case((2064, 320), (2288, 320), (0, 1), 0, [(2100, 400, "hung", TEAL, 270), (2116, 420, "lamp", 0, 270),
                                         (2176, 400, "hung", TEAL, 270), (2192, 420, "lamp", 0, 270),
                                         (2250, 400, "hung", YELLOW, 270)], color=ROOM)
REGIONS[2] = ajartime.on_foot("room 2", {"gallery": (2000, 0, 3280, 320), "pit": (3280, -256, 3792, 640),
                                         "box": (2384, 480, 2576, 672)},
                              [("gallery", "pit"), ("box", "gallery")],          # (the pit to the gallery: the Pair only)
                              {"gallery": [(2480, 316)], "pit": [(3788, -96)], "box": [(2480, 484)]})
ajartime.covers(m, "room 2", FIRST, REGIONS[2], zone=(1928, -328, 3864, 712), exempt=CASES)

# === 3. the press: a fight of goes ===========================================
# The hall (5000..6536, 0..1280), its north third the press. Entered from
# YELLOW's far side, a ledge 96 over the lobby (south-west), which is part of
# the fight from 16 past the ledge's edge: so a player on the ledge is in no
# room, and one in the lobby cannot climb back.
FIRST = len(m.polys)
K3 = 3
HX, HY, HW, HH = 5000, 0, 1536, 1280
PRESS3 = 3530           # the press's sector tag (map32.zs: PRESS32)
PY = HY + 768           # the press's south edge
PILLARS3 = [(HX + 288, HY + 288), (HX + 1184, HY + 288), (HX + 288, HY + 544), (HX + 1184, HY + 544)]
ajarmap.fitted(m, (HX, HY, HX + HW, PY), [((x, y, x + 64, y + 64), dict(floor=320)) for x, y in PILLARS3],
               ceil=320, light=200, color=HALL)
for x1, x2 in ((HX, HX + 512), (HX + 512, HX + 1024), (HX + 1024, HX + HW)):
    m.sector(rect(x1, PY, x2, HY + HH), ceil=192, light=185, color=HALL, wall="AJBOLT", ftex="AJTRIMF",
             ctex="AJTRIMF", id=PRESS3)
ajartime.press(m, HX + 768, HY + 1024, PRESS3)
LEVER3 = (HX + 768, HY + 2)
ajartime.press_switch(m, *LEVER3, 90, PRESS3)
ajartime.zone(m, K3, 0, HX, HY, HX + HW, HY + HH, grow=72, mix=True)
# the lobby and YELLOW's ledge in its south wall
m.sector(rect(4744, 64, 5000, 320), ceil=192, light=190, color=HALL)
ajarmap.recess(m, (4840, 64), (4904, 64), (0, -1), 96, far_id(YELLOW), FW, far_colour=YELLOW, color=HALL)
ajartime.zone(m, K3, 0, 4744, 80, 5000, 320, mix=True)     # from 16 past the ledge
spots(2004, (4800, 200))                    # plasma rifle
spots(2046, (4860, 260))                    # rockets
spots(2011, (4920, 140), (4920, 180))
LOBBY3 = [2004, 2046]
# the case in the lobby's north wall: the press up, three bodies under it, the player at the lever
CASE3 = case((4776, 320), (4968, 320), (0, 1), 0, [(4800, 360, "me", 0, 90), (4840, 410, "body", 3003, 0),
                                                 (4890, 400, "body", 66, 0), (4940, 410, "body", 67, 0)],
             color=HALL)
m.sectors[CASE3].update(wall="AJBOLT", ctex="AJTRIMF")
# time doors west, east, south; boxes west, east, south behind glass
ajartime.hall_door(m, K3, 1, (HX, 688), (HX, 752), (-1, 0), 0, color=HALL)
ajartime.hall_door(m, K3, 2, (HX + HW, 688), (HX + HW, 752), (1, 0), 0, color=HALL)
ajartime.hall_door(m, K3, 3, (HX + 300, HY), (HX + 364, HY), (0, -1), 0, color=HALL)
BOXF = 64
m.sector(rect(4776, 464, 4984, 656), floor=BOXF, ceil=192, light=210, color=BOX)
ajartime.glass(m, (HX, 496), (HX, 624), (-1, 0), BOXF)
ajartime.box_door(m, K3, 1, (4776, 528), (4776, 592), (-1, 0), BOXF, color=BOX)
ajartime.zone(m, K3, 1, 4712, 464, 4984, 656)
ajartime.anew(m, 4880, 654, 270, z=BOXF + 30)
m.sector(rect(6552, 464, 6760, 656), floor=BOXF, ceil=192, light=210, color=BOX)
ajartime.glass(m, (HX + HW, 496), (HX + HW, 624), (1, 0), BOXF)
ajartime.box_door(m, K3, 2, (6760, 528), (6760, 592), (1, 0), BOXF, color=BOX)
ajartime.zone(m, K3, 2, 6552, 464, 6824, 656)
m.sector(rect(6100, -216, 6356, -16), floor=BOXF, ceil=192, light=210, color=BOX)
ajartime.glass(m, (6164, HY), (6292, HY), (0, -1), BOXF)
ajartime.box_door(m, K3, 3, (6196, -216), (6260, -216), (0, -1), BOXF, color=BOX)
ajartime.zone(m, K3, 3, 6100, -280, 6356, -16)


def stock(x, y, along, *kinds):
    """Supplies in a row from x, y, `along` apart; returned for the reckoning."""
    for i, k in enumerate(kinds):
        m.thing(x + along[0] * i, y + along[1] * i, k)
    return list(kinds)


BOXES3 = (stock(4810, 630, (40, 0), 2018, 2012, 2012, 17, 2046)
          + stock(6600, 630, (40, 0), 2018, 2012, 17, 2046)
          + stock(6130, -190, (40, 0), 2012, 2012, 2047, 2046))
# the steel door the win opens, east, and the corridor on to room 4 (no fight's)
steel(K3, (HX + HW, 128), (HX + HW, 192), (1, 0), 0)
m.sector(rect(6552, 96, 6872, 224), ceil=128, light=180, color=HALL)
# the fight: all of it AjarCues; wave 1 in the south and middle, to be drawn north
SOLID3 = [(x, y, x + 64, y + 64) for x, y in PILLARS3]
c3 = ajartime.Crowd(m, K3, [(HX, HY, HX + HW, HY + HH)], SOLID3)


def at3(*pts):
    return [(HX + a, HY + b) for a, b in pts]


c3.cue(1, 0, 3001, *at3((120, 150), (220, 150), (420, 150), (520, 150), (1016, 150), (1116, 150),
                        (1316, 150), (1416, 150), (620, 250), (916, 250)), angle=90)                  # imps, the south
c3.cue(1, 0, 67, *at3((140, 330), (560, 400), (976, 400), (1396, 330)), angle=90)                   # mancubi
c3.cue(1, 0, 66, *at3((440, 200), (1096, 200), (220, 470), (768, 330), (1316, 470), (700, 520)), angle=90)   # revenants
c3.cue(1, 0, 69, *at3((120, 520), (440, 560), (560, 560), (976, 560), (1096, 560), (1416, 520),
                      (400, 690), (1136, 690)), angle=90)                                             # hell knights
c3.cue(1, 0, 3003, *at3((180, 680), (300, 680), (680, 680), (856, 680), (1236, 680), (1356, 680)), angle=90)  # barons
c3.cue(2, 16, 64, *at3((200, 720), (1336, 720)), angle=90, always=True)                             # arch-viles
c3.cue(2, 16, 68, *at3((500, 600), (1036, 600), (500, 250), (1036, 250)), angle=90)                # arachnotrons
c3.cue(2, 16, 3005, *at3((768, 600), (200, 300), (1336, 300), (768, 200)), angle=90)               # cacodemons
c3.cue(3, 8, 16, *at3((400, 500), (1136, 500)), angle=90, always=True)                             # cyberdemons
assert not c3.bad, c3.bad
for x, y, _ in c3.placed[1]:
    assert y < PY - 24, "wave 1 starts out of the press"
    assert walk((x, y), (LEVER3[0], LEVER3[1] + 46)) > 150, "a monster on the lever"
# a third of what it would take: the lobby's and the boxes' ammunition against every monster's health
HARD3 = ajartime.toughness(c3.kinds)
FIRE3 = ajartime.firepower(LOBBY3 + BOXES3)
assert 0.28 <= FIRE3 / HARD3 <= 0.4, (FIRE3, HARD3)
REGIONS[3] = ajartime.on_foot("room 3", {"hall": (HX, HY, HX + HW, PY), "press": (HX, PY, HX + HW, HY + HH),
                                         "lobby": (4744, 64, 5000, 320), "box1": (4776, 464, 4984, 656),
                                         "box2": (6552, 464, 6760, 656), "box3": (6100, -216, 6356, -16)},
                              [("hall", "press", True), ("hall", "lobby", True), ("box1", "hall"), ("box2", "hall"),
                               ("box3", "hall")],
                              {"hall": [(HX + 4, 720), (HX + HW - 4, 720), (HX + 332, HY + 4)],
                               "box1": [(4780, 560)], "box2": [(6756, 560)], "box3": [(6228, -212)]})
ajartime.covers(m, "room 3", FIRST, REGIONS[3], zone=(4744, -72, 6608, 1352), exempt=CASES)

# === 4. the range: a fight of goes ============================================
# The corridor from room 3 ends in a drop of 96 into the lobby, which is part
# of the fight from 16 past the edge. The range (7200..7712, 0..1400), the
# shutter in its north wall and the pen behind it, level with the range; the
# booth east of the pen end, behind glass; the firing spot at the south end.
FIRST = len(m.polys)
K4, F4 = 4, -96
RX, RY, RW, RL = 7200, 0, 512, 1400
SHUT4 = 3540            # the shutter's sector tag (map32.zs: SHUT32)
FIRE4 = (7456, 120)     # the firing spot (map32.zs)
PILLARS4 = [(7296, 200), (7552, 200)]
ajarmap.fitted(m, (RX, RY, RX + RW, RY + RL), [((x, y, x + 64, y + 64), dict(floor=F4 + 256)) for x, y in PILLARS4],
               floor=F4, ceil=F4 + 256, light=200, color=HALL)
for x, y in PILLARS4:
    assert not (x - 16 < FIRE4[0] < x + 80), "a pillar in the line of fire"
m.sector(rect(6872, 32, 7200, 320), floor=F4, ceil=F4 + 192, light=190, color=HALL)
ajartime.zone(m, K4, 0, 6888, 32, 7200, 320, mix=True)     # from 16 past the corridor's end
ajartime.zone(m, K4, 0, RX, RY, RX + RW, RY + RL, grow=72, mix=True)
# the entrance's supplies, in the corridor (no fight's): enough to kill the pen once, and some over
ENTRY4 = (stock(6600, 120, (40, 0), 2003, 8, 2046, 2046, 2046, 2046, 2046)
          + stock(6600, 200, (40, 0), 2046, 2046, 2046, 2046, 2046, 17, 17)
          + stock(6840, 120, (0, 40), 17, 2012, 2012))
# the shutter, 384 wide, and the pen behind it (7072..7840, 1416..1736)
ajartime.shutter(m, (7264, RY + RL), (7648, RY + RL), (0, 1), F4, SHUT4, keep=True)
PEN4 = (7072, 1416, 7840, 1736)
m.sector(rect(*PEN4), floor=F4, ceil=F4 + 192, light=170, color=PEN, wall="AJBOLT")
PEN_SECTOR = len(m.polys) - 1
ajartime.zone(m, K4, 0, *PEN4, mix=True)
c4 = ajartime.Crowd(m, K4, [PEN4])


def at4(*pts):
    return [(PEN4[0] + a, PEN4[1] + b) for a, b in pts]


c4.cue(1, 0, 67, *at4((100, 260), (260, 260), (508, 260), (668, 260)), angle=270)       # mancubi
c4.cue(1, 0, 16, *at4((384, 240)), angle=270, always=True)                              # the cyberdemon
c4.cue(1, 0, 3003, *at4((180, 120), (588, 120)), angle=270)                             # barons
c4.cue(1, 0, 66, *at4((60, 60), (300, 60), (468, 60), (708, 60)), angle=270)            # revenants
c4.cue(1, 0, 64, *at4((384, 60), (384, 140)), angle=270, always=True)                   # arch-viles
assert not c4.bad, c4.bad
HARD4 = ajartime.toughness(c4.kinds)
FIRE4X = ajartime.firepower(ENTRY4)
assert FIRE4X >= 1.2 * HARD4, (FIRE4X, HARD4)
# the booth, east of the pen end: a way in from the range, glass onto it, the plate
m.sector(rect(7712, 1100, 7728, 1164), floor=F4, ceil=F4 + 128, light=190, color=HALL)
ajartime.glass(m, (7712, 1180), (7712, 1380), (1, 0), F4)
m.sector(rect(7728, 1100, 7920, 1380), floor=F4, ceil=F4 + 128, light=210, color=HALL)
PLATE4 = (7840, 1300)
ajartime.shutter_plate(m, *PLATE4, SHUT4)
ajartime.zone(m, K4, 0, 7712, 1100, 7920, 1380, mix=True)
# time doors west and east; boxes 1 and 2 south behind glass, box 3 west
ajartime.hall_door(m, K4, 1, (RX, 700), (RX, 764), (-1, 0), F4, color=HALL)
ajartime.hall_door(m, K4, 2, (RX + RW, 700), (RX + RW, 764), (1, 0), F4, color=HALL)
m.sector(rect(7200, -208, 7376, -16), floor=F4 + 64, ceil=F4 + 192, light=210, color=BOX)
ajartime.glass(m, (7232, RY), (7344, RY), (0, -1), F4 + 64)
ajartime.box_door(m, K4, 1, (7200, -144), (7200, -80), (-1, 0), F4 + 64, color=BOX)
ajartime.zone(m, K4, 1, 7136, -208, 7376, -16)
ajartime.anew(m, 7374, -112, 180, z=30)
m.sector(rect(7536, -208, 7712, -16), floor=F4 + 64, ceil=F4 + 192, light=210, color=BOX)
ajartime.glass(m, (7568, RY), (7680, RY), (0, -1), F4 + 64)
ajartime.box_door(m, K4, 2, (7712, -144), (7712, -80), (1, 0), F4 + 64, color=BOX)
ajartime.zone(m, K4, 2, 7536, -208, 7776, -16)
m.sector(rect(6992, 500, 7184, 680), floor=F4 + 64, ceil=F4 + 192, light=210, color=BOX)
ajartime.glass(m, (RX, 540), (RX, 640), (-1, 0), F4 + 64)
ajartime.box_door(m, K4, 3, (6992, 560), (6992, 624), (-1, 0), F4 + 64, color=BOX)
ajartime.zone(m, K4, 3, 6928, 500, 7184, 680)
BOXES4 = (stock(7240, -180, (40, 0), 2018, 2012, 2046) + stock(7576, -180, (40, 0), 2018, 2012, 17)
          + stock(7020, 520, (0, 40), 2012, 2012, 2046))
# the case in the range's east wall, seen from the way in: the player on the
# booth's plate, another at the firing spot, bodies in the pen
case((RX + RW, 96), (RX + RW, 288), (1, 0), F4, [(7760, 120, "plate", 0, 0), (7760, 120, "me", 0, 180),
                                                (7790, 270, "me", 0, 180), (7800, 170, "body", 16, 0),
                                                (7810, 220, "body", 67, 0)], color=HALL)
# the steel door the win opens, east, and the corridor on to room 5 (no fight's)
steel(K4, (RX + RW, 420), (RX + RW, 484), (1, 0), F4)
CORRIDOR4 = m.sector(rect(7728, 388, 8048, 516), floor=F4, ceil=F4 + 128, light=180, color=HALL)
REGIONS[4] = ajartime.on_foot("room 4", {"range": (RX, RY, RX + RW, RY + RL + 16), "lobby": (6872, 32, 7200, 320),
                                         "booth": (7712, 1100, 7920, 1380), "box1": (7200, -208, 7376, -16),
                                         "box2": (7536, -208, 7712, -16), "box3": (6992, 500, 7184, 680)},
                              [("lobby", "range", True), ("range", "booth", True), ("box1", "range"),
                               ("box2", "range"), ("box3", "range")],
                              {"range": [(RX + 4, 732), (RX + RW - 4, 732)], "box1": [(7204, -112)],
                               "box2": [(7708, -112)], "box3": [(6996, 592)]})
ajartime.covers(m, "room 4", FIRST, REGIONS[4], zone=(6888, -72, 7920, 1736), exempt=CASES + [PEN_SECTOR, CORRIDOR4])

# === 5. the airlock and the way out: a room of goes ============================
# S, L and E in a row (floor -192), entered by a drop of 96 from the corridor
# into S. F1 (GREEN only) in S's east wall, GREEN's far side in L's west wall;
# F2 (PINK only) in L's east wall, PINK's far side in E's south wall. In E the
# two brass frames, west (RED hung) and east (BLUE only), face each other;
# the night room north of E, a drop of 96 back into E by a hole in its south
# wall. Each chamber has its own time door; one box, south of S.
FIRST = len(m.polys)
K5, F5 = 5, -192
G1, G2 = 141, 142
SX, LX, EX, CY = 8048, 8800, 9600, 160
m.sector(rect(SX, CY, SX + 512, CY + 512), floor=F5, ceil=F5 + 192, light=200, color=ROOM)
m.sector(rect(LX, CY, LX + 448, CY + 512), floor=F5, ceil=F5 + 192, light=190, color=LOCK)
m.sector(rect(EX, CY, EX + 512, CY + 448), floor=F5, ceil=F5 + 224, light=190, color=END)
spots(2012, (7900, 420), (7940, 420))       # the entrance's: in the corridor (no room's)
spots(2011, (7900, 480), (7940, 480))
ajartime.zone(m, K5, 0, SX + 16, CY - 64, SX + 584, CY + 584, goes=True)     # S, from 16 past the corridor's end
ajartime.zone(m, K5, 0, LX - 72, CY - 64, LX + 520, CY + 584, goes=True)
NX, NY, NF = EX + 96, CY + 464, F5 + 96
ajartime.zone(m, K5, 0, EX - 72, CY - 64, EX + 584, NY + 264, goes=True)    # E and the night room
# F1 and GREEN; F1's plate P1 in S
ajarmap.recess(m, (SX + 512, CY + 224), (SX + 512, CY + 288), (1, 0), F5, G1, far_id(GREEN), home=far_id(GREEN),
               only=True, trim=inlaid(GREEN), color=ROOM)
ajarmap.recess(m, (LX, CY + 224), (LX, CY + 288), (-1, 0), F5, far_id(GREEN), G1, far_colour=GREEN, color=LOCK)
ajarmap.door(m, GREEN, SX + 432, CY + 150, angle=180)
P51 = (SX + 132, CY + 420)
ajartime.plate(m, *P51, G1)
assert walk(P51, (SX + 512, CY + 256)) >= 300
ajarmap.door(m, BLUE, SX + 252, CY + 470, angle=270)
# F2 and PINK; F2's plate P2 in L
ajarmap.recess(m, (LX + 448, CY + 224), (LX + 448, CY + 288), (1, 0), F5, G2, far_id(PINK), home=far_id(PINK),
               only=True, trim=inlaid(PINK), color=LOCK)
ajarmap.recess(m, (EX + 224, CY), (EX + 288, CY), (0, -1), F5, far_id(PINK), G2, far_colour=PINK, color=END)
ajarmap.door(m, PINK, LX + 350, CY + 120, angle=180)
P52 = (LX + 130, CY + 420)
ajartime.plate(m, *P52, G2)
assert walk(P52, (LX + 448, CY + 256)) >= 300
# E: the brass frames face each other, RED hung in the west one; the night room
ajarmap.recess(m, (EX, CY + 192), (EX, CY + 256), (-1, 0), F5, HOME, far_id(RED), trim=inlaid(RED),
               home=far_id(RED), chain=(far_id(BLUE), HOME2), only=True, color=END)
ajarmap.recess(m, (EX + 512, CY + 192), (EX + 512, CY + 256), (1, 0), F5, HOME2, far_id(RED), trim=inlaid(BLUE),
               home=far_id(BLUE), chain=(far_id(RED), HOME), only=True, color=END)
ajarmap.door(m, RED, EX + 40, CY + 224, frame=HOME)
ajarmap.way_through(m, NX, NY, RED, BLUE, floor=NF)
m.sector(rect(NX + 128, NY - 16, NX + 192, NY), floor=NF, ceil=NF + 96, light=150, wall="AJXA", ftex="AJTRIMF",
         ctex="AJTRIMF")
assert NY - 16 == CY + 448 and EX <= NX + 128 and NX + 192 <= EX + 512
# the time doors: S's (door 1) and L's in their south walls, E's in its south wall; the box south of S
ajartime.hall_door(m, K5, 1, (SX + 152, CY), (SX + 216, CY), (0, -1), F5, color=ROOM)
ajartime.hall_door(m, K5, 2, (LX + 200, CY), (LX + 264, CY), (0, -1), F5, color=LOCK)
ajartime.hall_door(m, K5, 3, (EX + 400, CY), (EX + 464, CY), (0, -1), F5, color=END)
m.sector(rect(SX + 152, -240, SX + 344, -48), floor=F5, ceil=F5 + 160, light=210, color=BOX)
ajartime.box_door(m, K5, 1, (SX + 216, -48), (SX + 280, -48), (0, 1), F5, color=BOX)
ajartime.zone(m, K5, 1, SX + 152, -240, SX + 344, 16)
ajartime.anew(m, SX + 248, -238, 90, z=30)
# the case in S's east wall, seen from the way in: BLUE hanging opposite RED, a player on each plate
case((SX + 512, CY + 352), (SX + 512, CY + 480), (1, 0), F5,
     [(SX + 540, CY + 370, "plate", 0, 0), (SX + 540, CY + 370, "me", 0, 180), (SX + 540, CY + 462, "plate", 0, 0),
      (SX + 540, CY + 462, "me", 0, 180), (SX + 600, CY + 380, "hung", RED, 0), (SX + 600, CY + 452, "hung", BLUE, 0)],
     color=ROOM)
REGIONS[5] = ajartime.on_foot("room 5", {"S": (SX, CY, SX + 512, CY + 512), "L": (LX, CY, LX + 448, CY + 512),
                                         "E": (EX, CY, EX + 512, CY + 448), "night": (NX, NY - 16, NX + 320, NY + 256),
                                         "box": (SX + 152, -240, SX + 344, -48)},
                              [("night", "E"), ("box", "S")],          # (S to L, L to E: earlier selves only)
                              {"S": [(SX + 184, CY + 4)], "L": [(LX + 232, CY + 4)], "E": [(EX + 432, CY + 4)],
                               "box": [(SX + 248, -52)]})
ajartime.covers(m, "room 5", FIRST, REGIONS[5], zone=(SX + 16, -240, EX + 584, NY + 264), exempt=CASES)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
