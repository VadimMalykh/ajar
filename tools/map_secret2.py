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
   foot; joined, the Pair stays so three seconds only. YELLOW leans at the
   far south end of the pit, too far to fetch while it is joined; its frame
   W (YELLOW only) is on the gallery; the pit is left only by its own time
   door or the joined Pair.
3. The press (a fight of goes), two shifts. A hall 1536 by 768 with four
   slabs for cover; north of it the press, a chamber with one mouth, two slabs
   and two time doors that are out only. The bait fights in the chamber; the
   wing south of the hall (a shutter open only while someone is under the
   press, stairs, the lever in an upper room by a window onto the hall, a pen
   of guards behind bars) is the next self's. 34 monsters in the south and
   middle, then 10, then two cyberdemons, and eight guards with the waves,
   none fighting another. Ammunition for about a third of them: the press is
   the way.
4. The range (a fight of goes), two keys under fire. A pen of 13 behind a
   shutter at the north end of a range 1400 long, the firing spot at the south
   end. Beside the range two wings that mirror each other, guarded, a key
   lever at the far end of each: pulled within two seconds of each other (by
   two selves: they are over 1750 apart on foot) they open the shutter for
   half a minute.
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
    angle); asserted sealed and every figure inside it (8 clear of its
    walls; a frame and the door in it may stand against the back wall)."""
    si = ajartime.case(m, a, b, out, floor, deep=deep, **look)
    xs = [a[0], b[0], a[0] + out[0] * (16 + deep), b[0] + out[0] * (16 + deep)]
    ys = [a[1], b[1], a[1] + out[1] * (16 + deep), b[1] + out[1] * (16 + deep)]
    for x, y, what, kind, ang in figures:
        r = 1 if what in ("frame", "hung", "lever") else 8
        assert min(xs) + r < x < max(xs) - r and min(ys) + r < y < max(ys) - r, (x, y, what)
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
# the case, in the north wall: VIOLET hung in its inlaid frame against the
# back wall, the second go walking into it, the first go on the pressed plate
# to one side, turned to the door
case((384, 512), (576, 512), (0, 1), 0, [(520, 622, "frame", VIOLET, 270), (520, 620, "hung", VIOLET, 270),
                                       (512, 600, "walking", 0, 90), (512, 600, "go", 2, 0),
                                       (430, 556, "plate", 0, 0), (430, 556, "me", 0, 35), (430, 556, "go", 1, 0)],
     color=ROOM)
REGIONS[1] = ajartime.on_foot("room 1", {"hall": (0, -192, 640, 512), "box": (-400, 32, -208, 224)},
                              [("box", "hall")], {"hall": [(4, 128)], "box": [(-212, 128)]})
ajartime.covers(m, "room 1", FIRST, REGIONS[1], zone=(-72, -264, 712, 584), exempt=CASES)

# === 2. two keys: a room of goes =============================================
# A gallery (floor 0) and, east of it, a pit (floor -96): the gallery's east
# end is the pit's edge. Frame A in the gallery's west wall, frame B in the
# pit's north wall, a clock lamp by each; YELLOW in the pit, W (YELLOW only)
# in the gallery's south wall. VIOLET's far side (from room 1) is in the
# gallery's south wall, the case in its north wall. Joined, the Pair stays so
# for PAIR2 seconds only (PLAN.md, "MAP32 room 2: the Pair shuts again"), and
# the pit is long: YELLOW leans at its far south end, so that hanging the leaf
# in B and only then fetching YELLOW is too late; a self that waits at B with
# YELLOW gets through.
FIRST = len(m.polys)
FA, FB, FW = 131, 132, 133
PITF = -96
PAIR2 = 3
PIT2 = (3280, -900, 3792, 640)
m.sector(rect(2000, 0, 3280, 320), ceil=192, light=200, color=ROOM)
m.sector(rect(*PIT2), floor=PITF, ceil=192, light=180, color=PIT, wall="AJBOLT")
ajartime.zone(m, 2, 0, 2000, 0, 3280, 320, grow=72, goes=True)
ajartime.zone(m, 2, 0, *PIT2, grow=72, goes=True)
ajarmap.recess(m, (2160, 0), (2224, 0), (0, -1), 0, far_id(VIOLET), F1, far_colour=VIOLET, color=ROOM)
spots(2011, (2140, 60), (2244, 60))         # stimpacks
spots(2012, (2192, 100))                    # medikit
spots(2049, (2300, 60))                     # shells
spots(2048, (2340, 60))                     # bullets
# A and B, their lamps and leaves
ajarmap.recess(m, (2000, 128), (2000, 192), (-1, 0), 0, FA, FB, home=TEAL, only=3, color=ROOM)
ajarmap.recess(m, (3664, 640), (3728, 640), (0, 1), PITF, FB, FA, home=TEAL, only=3, color=PIT)
ajartime.together(m, 2002, 224, 0, FA, seconds=PAIR2)
ajartime.together(m, 3760, 638, 270, FB, seconds=PAIR2)
LEAF_A, LEAF_B = (2100, 260), (3560, 560)
ajarmap.pair(m, TEAL, LEAF_A + (0,), LEAF_B + (270,))
# from before A along the gallery, over the edge and across the pit to before B
A_TO_B = walk((2040, 160), (3296, 160), (3696, 600))
assert A_TO_B >= 1400 and A_TO_B > JOIN, A_TO_B
# YELLOW at the pit's far south end: from before B to it and back takes longer than the Pair stays joined,
# at the fastest run, with 10 tics to spare; W, which takes it only, in the gallery's south wall
YELLOW_AT = (3600, PIT2[1] + 60)
B_TO_YELLOW = walk((3696, 600), YELLOW_AT)
assert B_TO_YELLOW >= 1400 and 2 * B_TO_YELLOW / 23.6 >= 35 * PAIR2 + 10, B_TO_YELLOW
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
# the case: self 1 at one hung leaf, self 2 at the other, both lamps green; self 3 by the second with YELLOW
# leaning beside it (there is no figure of a self carrying a door). (YELLOW in W is left out: a case wider
# than 256 has glass bigger than covers() lets go.)
case((2048, 320), (2304, 320), (0, 1), 0, [(2088, 410, "hung", TEAL, 270), (2112, 420, "lamp", 0, 270),
                                         (2068, 372, "me", 0, 300), (2068, 372, "go", 1, 0),
                                         (2184, 410, "hung", TEAL, 270), (2208, 420, "lamp", 0, 270),
                                         (2164, 372, "me", 0, 270), (2164, 372, "go", 2, 0),
                                         (2242, 380, "me", 0, 240), (2242, 380, "go", 3, 0),
                                         (2274, 404, "leaning", YELLOW, 270)], color=ROOM)
REGIONS[2] = ajartime.on_foot("room 2", {"gallery": (2000, 0, 3280, 320), "pit": PIT2,
                                         "box": (2384, 480, 2576, 672)},
                              [("gallery", "pit"), ("box", "gallery")],          # (the pit to the gallery: the Pair only)
                              {"gallery": [(2480, 316)], "pit": [(3788, -96)], "box": [(2480, 484)]})
ajartime.covers(m, "room 2", FIRST, REGIONS[2], zone=(1928, PIT2[1] - 72, 3864, 712), exempt=CASES)

# === 3. the press: a fight of goes ===========================================
# The hall (5000..6536, 0..768) and north of it the press, a chamber
# (5000..6536, 800..1280) of steel, open onto the hall along most of its
# width: of the wall between only two stubs 128 wide are left at the west and
# east ends, and the mouth between them is 1280 wide (it is part of the press:
# whatever stands in it when the press comes down is under it, so the press
# begins at the hall's north edge; the hall's higher ceiling leaves a steel
# lintel over the opening). It was a mouth 192 wide until 2026-11-21: monsters
# after a bait slid along the wall towards its x and bunched there, and a pull
# took 6 to 11; now whatever walks at a bait at the back is under the press for
# the last 500 of its way. Two shifts: the bait fights in
# the chamber, behind two slabs of its own, and leaves by time door 3 (east)
# or 4 (west), which are out only (the next go comes out by door 1, not into
# the crowd in the chamber). The lever is in the wing south of the hall: a
# shutter in the hall's south wall that is open only while the player or an
# earlier self is under the press, a landing, stairs up east, an upper room
# with the lever beside a window onto the hall (the way out, a drop of 96),
# and south of the upper room the pen of the guards, behind bars. So one
# body is never the bait and at the lever (the shutter, not the wall, keeps
# them apart). Four slabs in the hall to hide
# behind. Entered from YELLOW's far side, a ledge 96 over the lobby
# (south-west), which is part of the fight from 16 past the ledge's edge: so
# a player on the ledge is in no room, and one in the lobby cannot climb back.
# Wave 1 starts in the hall's east half, the slow ones nearest the press, 700
# or more from the lobby (since 2026-11-21: from a pistol start the first self
# takes the lobby's guns and goes north along the west wall under the press
# before the horde is on it).
FIRST = len(m.polys)
K3 = 3
HX, HY, HW, HH = 5000, 0, 1536, 1280
PRESS3 = 3530           # the press's sector tag (map32.zs: PRESS32)
SHUT3 = 3535            # the wing's shutter (map32.zs: SHUT33)
SCREEN3 = 3536          # the screen before the guards (map32.zs: SCREEN3)
CAGE3 = 3537            # the cage's shutter (map32.zs: CAGE3)
PENTAG3 = 3538          # the pen's sector: where the sentries stand (time.zs, AjarSentry)
WING3TAG = 3539         # the wing's walkable sectors that have no tag of their own: what trips them
PY = HY + 768           # the hall's north wall
CY = PY + 32            # the chamber's south side (the wall between is two stubs at the ends; the rest is the mouth)
WY = HY + HH            # the chamber's north wall
MOUTH3 = (HX + 128, HX + HW - 128)     # the opening between the two stubs
CSLABS3 = [(HX + 320, CY + 208, HX + 448, CY + 272), (HX + 1088, CY + 208, HX + 1216, CY + 272)]   # the chamber's
DOORS3 = (CY + 208, CY + 272)       # time doors 3 (east) and 4 (west): in the chamber's walls, out only
# the wing, south of the hall (all of it the fight's hall)
WF, WC = HY + 96, HY + 224          # the upper room's floor, and the wing's ceiling
SHUTTER3 = (HX + 128, HX + 256)     # in the hall's south wall (HY .. HY - 16)
LANDING3 = (HX + 112, HY - 176, HX + 272, HY - 16)
STAIRS3 = (HX + 272, HY - 96, HX + 464, HY - 16)     # six steps of 16 going east, 32 deep, along the north wall
UPPER3 = (HX + 464, HY - 160, HX + 880, HY - 16)     # (16 shallower than the pen: the screen is south of it)
SCREENS3 = (HX + 464, HY - 176, HX + 880, HY - 160)  # the screen, along the whole of the bars, on the upper room's side
CAGE3BOX = (HX + 896, HY - 152, HX + 976, HY - 56)   # the cage, east of the upper room behind its wall
CAGEDOOR3 = (HY - 152, HY - 88)     # its shutter in the upper room's east wall (and the glass, HY - 88 .. HY - 56)
WINDOW3 = (HX + 704, HX + 832)      # in the upper room's north wall, open, its sill at the upper room's floor
LEVER3 = (HX + 856, HY - 18)        # on that wall just east of the window
PEN3 = (HX + 464, HY - 432, HX + 880, HY - 176)      # the guards, behind bars along the upper room's south side
SLABS3 = [(HX + x, HY + y, HX + x + 192, HY + y + 64) for x, y in ((160, 160), (1184, 160), (480, 320), (864, 320))]
ajarmap.fitted(m, (HX, HY, HX + HW, PY), [(s, dict(floor=320)) for s in SLABS3], ceil=320, light=200, color=HALL)
# the chamber, in three sectors of the press's tag (and the slabs in two of them, of no tag: they stay up);
# the mouth, one more of the press's tag, borders all three (udmf splits the shared edges)
for x1, x2 in ((HX, HX + 512), (HX + 512, HX + 1024), (HX + 1024, HX + HW)):
    ajarmap.fitted(m, (x1, CY, x2, WY), [(s, dict(floor=192, id=0)) for s in CSLABS3 if x1 <= s[0] and s[2] <= x2],
                   ceil=192, light=185, color=HALL, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF", id=PRESS3)
m.sector(rect(MOUTH3[0], PY, MOUTH3[1], CY), ceil=192, light=185, color=HALL, wall="AJBOLT", ftex="AJTRIMF",
         ctex="AJTRIMF", id=PRESS3)
assert MOUTH3[0] - HX == 128 and HX + HW - MOUTH3[1] == 128 and MOUTH3[0] < HX + 512 and HX + 1024 < MOUTH3[1]
ajartime.press(m, HX + 768, HY + 1024, PRESS3)
# the press's lamps: two in the chamber on the stubs' north faces, either side of the mouth; one in the hall
# on the west stub's south face
assert HX < MOUTH3[0] - 32 - 16 and MOUTH3[1] + 32 + 16 < HX + HW     # (each on its stub)
ajartime.press_lamp(m, MOUTH3[0] - 32, CY + 2, 90, PRESS3)
ajartime.press_lamp(m, MOUTH3[1] + 32, CY + 2, 90, PRESS3)
ajartime.press_lamp(m, MOUTH3[0] - 32, PY - 2, 270, PRESS3)
# the chamber's slabs: 160 or more from every wall and from the mouth, and clear of the time doors' way in
for s in CSLABS3:
    assert s[0] - HX >= 160 and HX + HW - s[2] >= 160 and s[1] - CY >= 160 and WY - s[3] >= 160, s
    gx = max(MOUTH3[0] - s[2], s[0] - MOUTH3[1], 0)
    assert (gx * gx + max(s[1] - CY, 0) ** 2) ** 0.5 >= 160, ("a slab by the mouth", s)
# the time doors out of the chamber: out only (time.zs: the next go's box opens onto door 1)
ajartime.hall_door(m, K3, 3, (HX + HW, DOORS3[0]), (HX + HW, DOORS3[1]), (1, 0), 0, out_only=True, color=HALL)
ajartime.hall_door(m, K3, 4, (HX, DOORS3[0]), (HX, DOORS3[1]), (-1, 0), 0, out_only=True, color=HALL)
# two plates in the chamber that work the wing: the screen's at the back opposite the mouth, the cage's in
# the north-west corner (each says what it does the first time the player steps on it)
SCREEN_PLATE3 = (HX + 768, WY - 64)
CAGE_PLATE3 = (HX + 96, WY - 96)
ajartime.shutter_plate(m, *SCREEN_PLATE3, SCREEN3, say=1)
ajartime.shutter_plate(m, *CAGE_PLATE3, CAGE3, say=2)


def gap(p, box):
    """How far the point p is from the rectangle box."""
    gx, gy = max(box[0] - p[0], p[0] - box[2], 0), max(box[1] - p[1], p[1] - box[3], 0)
    return (gx * gx + gy * gy) ** 0.5


for pl in (SCREEN_PLATE3, CAGE_PLATE3):
    r = 28          # AjarPlate.REACH, and its picture's half
    assert HX + r <= pl[0] <= HX + HW - r and CY + r <= pl[1] <= WY - r, ("a plate not wholly in the chamber", pl)
    for sl in CSLABS3:
        assert gap(pl, sl) >= r + 64, ("a plate by a slab", pl, sl)
    for dx in (HX, HX + HW):        # the time doors' way in: their mouths in the chamber's side walls
        assert gap(pl, (dx, DOORS3[0], dx, DOORS3[1])) >= r + 64, ("a plate by a time door", pl)
    # one body is never on a plate and in the wing (south through the mouth where it is nearest)
    mx = min(max(pl[0], MOUTH3[0] + 16), MOUTH3[1] - 16)
    w = walk(pl, (mx, CY), (mx, PY), (SHUTTER3[1], HY))
    assert w > 600, (pl, w)
# the wing: the shutter (open while someone is under the press; nothing of the hall's walks or flies past
# its face), the landing, the stairs, the upper room, the window and the lever, the pen
m.sector(rect(*LANDING3), floor=HY, ceil=WC, light=200, color=HALL, id=WING3TAG)
ajarmap.stairs(m, (STAIRS3[0], STAIRS3[1]), (STAIRS3[0], STAIRS3[3]), (1, 0), HY, WF - HY, steps=6, depth=32,
               ceil=WC, light=200, color=HALL, id=WING3TAG)
m.sector(rect(*UPPER3), floor=WF, ceil=WC, light=210, color=HALL, id=WING3TAG)
m.sector(rect(*PEN3), floor=WF, ceil=WC, light=170, color=PEN, wall="AJBOLT", id=PENTAG3)
PEN_SECTOR3 = len(m.polys) - 1
assert STAIRS3[2] - STAIRS3[0] == 6 * 32 and LANDING3[2] == STAIRS3[0] and STAIRS3[2] == UPPER3[0]
assert LANDING3[0] <= SHUTTER3[0] and SHUTTER3[1] <= LANDING3[2] and PEN3[0] == UPPER3[0] and PEN3[2] == UPPER3[2]
# the screen: shut while someone stands on its plate in the chamber, open otherwise; worked from the
# upper room (a player in its way is put north), the full height of the wing. Shut, nothing passes it
assert SCREENS3[1] == PEN3[3] and SCREENS3[3] == UPPER3[1] and SCREENS3[0] == PEN3[0] and SCREENS3[2] == PEN3[2]
ajartime.shutter(m, (SCREENS3[0], SCREENS3[3]), (SCREENS3[2], SCREENS3[3]), (0, -1), WF, SCREEN3, high=WC - WF,
                 screen=True, color=HALL)
# the bars, between the pen and the screen: nothing walks across (players and monsters), shots and sight
# pass; so no guard stands in the screen's way
m.line((PEN3[0], PEN3[3]), (PEN3[2], PEN3[3]), mid="AJGRIL", midboth=True, wrapmidtex=True, blocking=True)
# the screen's lamps: in the upper room on its north wall west of the window, and a repeater on the
# landing's east wall south of the stairs, seen as the player comes in through the shutter
ajartime.shut_lamp(m, HX + 672, HY - 18, 270, SCREEN3)
ajartime.shut_lamp(m, LANDING3[2] - 2, HY - 136, 180, SCREEN3)
assert STAIRS3[1] > HY - 136 + 8
# the cage: an alcove east of the upper room, steel inside and lit, entered only by its shutter (worked
# from the upper room: a player inside when it shuts is put out); beside it a slit of glass; inside, in
# view of the glass, a megasphere
m.sector(rect(*CAGE3BOX), floor=WF, ceil=WC, light=230, color=HALL, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF",
         id=WING3TAG)
CAGE_SECTOR3 = len(m.polys) - 1
ajartime.shutter(m, (UPPER3[2], CAGEDOOR3[0]), (UPPER3[2], CAGEDOOR3[1]), (1, 0), WF, CAGE3, behind=True,
                 color=HALL)
CAGE_SHUT_SECTOR3 = len(m.polys) - 1
ajartime.glass(m, (UPPER3[2], CAGEDOOR3[1]), (UPPER3[2], CAGE3BOX[3]), (1, 0), WF)
# (the post between the shutter and the glass: no trim drawn in it, and nothing steps sideways into the glass)
m.line((UPPER3[2], CAGEDOOR3[1]), (UPPER3[2] + 16, CAGEDOOR3[1]), mid=None, dontpegbottom=False, blocking=True)
assert CAGE3BOX[0] == UPPER3[2] + 16 and CAGEDOOR3[0] == CAGE3BOX[1] and CAGEDOOR3[1] - CAGEDOOR3[0] == 64
assert CAGE3BOX[3] - CAGEDOOR3[1] == 32 and UPPER3[1] < CAGE3BOX[1] and CAGE3BOX[3] < UPPER3[3]
MEGA3 = (HX + 940, HY - 72)
spots(83, MEGA3)
assert CAGE3BOX[0] + 24 < MEGA3[0] < CAGE3BOX[2] - 24 and CAGEDOOR3[1] <= MEGA3[1] <= CAGE3BOX[3] - 16
ajartime.shut_lamp(m, UPPER3[2] - 2, HY - 36, 180, CAGE3)
ajartime.shutter(m, (SHUTTER3[0], HY), (SHUTTER3[1], HY), (0, -1), HY, SHUT3, under=PRESS3, nomonsters=True,
                 color=HALL)
ajartime.shut_lamp(m, SHUTTER3[1] + 24, HY + 2, 90, SHUT3)
# the window: a gap in the wall 16 thick, its sill at the upper room's floor, 96 high; a drop of 96 into the hall
m.sector(rect(WINDOW3[0], HY - 16, WINDOW3[1], HY), floor=WF, ceil=WF + 96, light=200, color=HALL, wall="AJTRIM",
         ftex="AJTRIMF", ctex="AJTRIMF", id=WING3TAG)
for y in (HY, HY - 16):
    m.line((WINDOW3[0], y), (WINDOW3[1], y), blockmonsters=True)
assert UPPER3[0] < WINDOW3[0] and WINDOW3[1] < LEVER3[0] < UPPER3[2] - 16 and LEVER3[0] - WINDOW3[1] <= 32
ajartime.press_switch(m, *LEVER3, 270, PRESS3)
ajartime.zone(m, K3, 0, LANDING3[0], PEN3[1], CAGE3BOX[2] + 16, HY, mix=True)    # (the cage too)
# the guards are sentries: the player (not an earlier self) on the landing, the stairs, the upper room, the
# window or in the cage wakes those on the demo in the pen (time.zs, AjarSentry)
ajartime.sentries(m, HX + 672, HY - 300, K3, PENTAG3, WING3TAG)
ajartime.zone(m, K3, 0, HX, HY, HX + HW, HY + HH, grow=72, mix=True)
spots(17, (HX + 150, HY - 140))             # a cell pack and a medikit on the landing
spots(2012, (HX + 230, HY - 140))
WING3 = [17, 2012]
# one body is never the bait and at the lever: from the nearest point under the press to the shutter
# (straight south from the mouth's west end: the west slab of the hall's south row is east of that line)
NEAR3 = max(MOUTH3[0], SHUTTER3[0]) + 16
assert NEAR3 + 16 <= SLABS3[0][0] and SHUTTER3[0] <= NEAR3 <= SHUTTER3[1]
WALK3 = walk((NEAR3, PY), (NEAR3, HY))
assert WALK3 > 600, WALK3


def cuts(p, q, box):
    """Does the rectangle `box` cut the segment p-q (Liang-Barsky)?"""
    t0, t1 = 0.0, 1.0
    for d, lo, hi, s in ((q[0] - p[0], box[0], box[2], p[0]), (q[1] - p[1], box[1], box[3], p[1])):
        if d == 0:
            if not lo < s < hi:
                return False
            continue
        a, b = (lo - s) / d, (hi - s) / d
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    return t0 < t1


# from the window the mouth is seen, between the hall's two middle slabs
WIN_MID, MOUTH_MID = ((WINDOW3[0] + WINDOW3[1]) / 2, HY - 8), ((MOUTH3[0] + MOUTH3[1]) / 2, PY + 16)
assert not any(cuts(WIN_MID, MOUTH_MID, s) for s in SLABS3), "a slab between the window and the mouth"
# what the pen sees: the upper room, the lever and the window, but not the landing or the lower stairs
# (so the top of the stairs is where the player fights from). Sight in 2.5D: the wing's floors and ceilings
WING_SPACES3 = [LANDING3 + (HY, WC), PEN3 + (WF, WC), UPPER3 + (WF, WC), SCREENS3 + (WF, WC)]    # (the screen open)
WING_SPACES3 += [(STAIRS3[0] + 32 * i, STAIRS3[1], STAIRS3[0] + 32 * (i + 1), STAIRS3[3], HY + 16 * (i + 1), WC)
                 for i in range(6)]
EYES3 = [(x, y) for x in range(PEN3[0] + 20, PEN3[2] - 19, 16) for y in range(PEN3[1] + 20, PEN3[3] - 19, 16)]


def pen_sees(x, y, fl):
    """From how many of the pen's places (a grid of 16, 20 off its walls; a monster's eye 42 or 48 over the
    floor) a player standing at x, y on the floor `fl` is seen (feet, middle or head)."""
    return sum(any(ajartime.seen(WING_SPACES3, (ex, ey, WF + e), (x, y, fl + z)) for e in (42, 48) for z in (4, 30, 54))
               for ex, ey in EYES3)


for x in range(LANDING3[0] + 16, LANDING3[2] + 1, 16):
    for y in range(LANDING3[1] + 16, LANDING3[3] - 15, 16):
        assert not pen_sees(x, y, HY), ("the pen sees the landing", x, y)
# the steps (the middle of each, across the stairs): the first is seen from nowhere in the pen, the second
# and third from no more than a fifth of it (by the bars, far east), the top ones from most of it
for i, most in ((0, 0), (1, 0.2), (2, 0.2), (4, 0.5), (5, 0.8)):
    n = max(pen_sees(STAIRS3[0] + 32 * i + 16, y, HY + 16 * (i + 1)) for y in range(STAIRS3[1] + 16, STAIRS3[3] - 15, 16))
    assert (n <= most * len(EYES3)) if i < 4 else (n >= most * len(EYES3)), ("the pen and step", i + 1, n, len(EYES3))
PEN_MID3 = ((PEN3[0] + PEN3[2]) / 2, PEN3[1] + 80, WF + 48)
for what, at in (("the upper room", ((UPPER3[0] + UPPER3[2]) / 2, (UPPER3[1] + UPPER3[3]) / 2, WF + 30)),
                 ("the lever", (LEVER3[0], LEVER3[1] - 4, WF + 40)), ("the window", (WIN_MID[0], HY - 20, WF + 48))):
    assert ajartime.seen(WING_SPACES3, PEN_MID3, at), ("the pen does not see " + what)


# each slab: 160 from every wall and from the other slabs, and behind it (south) a place out of sight of
# the mouth and of the hall's middle
for i, s in enumerate(SLABS3):
    assert s[0] - HX >= 160 and HX + HW - s[2] >= 160 and s[1] - HY >= 160 and PY - s[3] >= 160, s
    for o in SLABS3[i + 1:]:
        gx, gy = max(o[0] - s[2], s[0] - o[2], 0), max(o[1] - s[3], s[1] - o[3], 0)
        assert (gx * gx + gy * gy) ** 0.5 >= 160, (s, o)
    hide = ((s[0] + s[2]) / 2, s[1] - 40)
    for eye in ((HX + 768, PY), (HX + 768, HY + 384)):
        assert cuts(hide, eye, s), (s, eye)
# the lobby and YELLOW's ledge in its south wall
m.sector(rect(4744, 64, 5000, 320), ceil=192, light=190, color=HALL)
ajarmap.recess(m, (4840, 64), (4904, 64), (0, -1), 96, far_id(YELLOW), FW, far_colour=YELLOW, color=HALL)
ajartime.zone(m, K3, 0, 4744, 80, 5000, 320, mix=True)     # from 16 past the ledge
spots(2004, (4800, 200))                    # plasma rifle
spots(2046, (4860, 260))                    # rockets
spots(2011, (4920, 140), (4920, 180))
# Vadim, after playing the two shifts: a BFG, a rocket launcher and more ammunition
spots(2006, (4780, 280))                    # BFG
spots(2003, (4940, 260))                    # rocket launcher
spots(2046, (4900, 290))                    # more rockets
spots(17, (4780, 130))                      # a cell pack
LOBBY3 = [2004, 2046, 2006, 2003, 2046, 17]
# the case in the lobby's north wall: self 1 standing among three bodies (under the press), and apart, at
# the east end, self 2 at the lever on the case's side wall
CASE3 = case((4776, 320), (4968, 320), (0, 1), 0, [(4826, 396, "plate", 0, 0), (4826, 396, "me", 0, 270),
                                                 (4826, 396, "go", 1, 0), (4800, 360, "body", 66, 0),
                                                 (4866, 366, "body", 67, 0), (4850, 416, "body", 3003, 0),
                                                 (4942, 384, "me", 0, 0), (4942, 384, "go", 2, 0),
                                                 (4966, 384, "lever", 0, 180)],
             color=HALL, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF")
# time doors west and east (doors 3 and 4 are the chamber's); boxes west, east, south behind glass
ajartime.hall_door(m, K3, 1, (HX, 688), (HX, 752), (-1, 0), 0, color=HALL)
ajartime.hall_door(m, K3, 2, (HX + HW, 688), (HX + HW, 752), (1, 0), 0, color=HALL)
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
          + stock(6130, -190, (40, 0), 2012, 2012, 17, 2046)
          + stock(4810, 500, (40, 0), 2046) + stock(6600, 500, (40, 0), 2046) + stock(6130, -60, (40, 0), 2046))
# the steel door the win opens, east, and the corridor on to room 4 (no fight's)
steel(K3, (HX + HW, 128), (HX + HW, 192), (1, 0), 0)
m.sector(rect(6552, 96, 6872, 224), ceil=128, light=180, color=HALL)
# the fight: all of it AjarCues; wave 1 in the hall's east half (2026-11-21; it was spread over the south
# and middle), in rows: the slow ones nearest the press (mancubi and barons north, hell knights in the
# middle, revenants and imps south), so that the horde comes under the press together
c3 = ajartime.Crowd(m, K3, [(HX, HY, HX + HW, PY), (HX, CY, HX + HW, HY + HH), PEN3], SLABS3 + CSLABS3, calm=True)


def at3(*pts):
    return [(HX + a, HY + b) for a, b in pts]


c3.cue(1, 0, 67, *at3((832, 696), (960, 696), (1088, 696), (1216, 696)), angle=90)                  # mancubi
c3.cue(1, 0, 3003, *at3((1320, 696), (1400, 696), (800, 616), (880, 616), (960, 616), (1040, 616)), angle=90)   # barons
c3.cue(1, 0, 69, *at3((1120, 616), (1200, 616), (1280, 616), (1360, 616), (800, 536), (880, 536), (960, 536),
                      (1040, 536)), angle=90)                                                        # hell knights
c3.cue(1, 0, 66, *at3((1120, 536), (1200, 536), (1280, 536), (1360, 536), (800, 456), (880, 456)), angle=90)   # revenants
c3.cue(1, 0, 3001, *at3((960, 456), (1040, 456), (1120, 456), (1200, 456), (1280, 456), (1360, 456),
                        (1120, 296), (1200, 296), (1280, 296), (1360, 296)), angle=90)               # imps
W1HALL3 = [(x, y) for x, y, _ in c3.placed[1]]
assert len(W1HALL3) == 34 and all(x >= HX + 768 for x, y in W1HALL3)
# clear of box 2's glass, door 2 and the steel door (the east wall) and of box 3's glass (the south wall)
assert all(x <= HX + HW - 128 and y >= HY + 160 for x, y in W1HALL3)
# none within 700 of the lobby's opening onto the hall (x = HX, y 64..320)
assert all(((x - HX) ** 2 + (y - min(max(y, 64), 320)) ** 2) ** 0.5 >= 700 for x, y in W1HALL3)
c3.cue(2, 16, 64, *at3((200, 720), (1336, 720)), angle=90, always=True)                             # arch-viles
c3.cue(2, 16, 68, *at3((500, 600), (1036, 600), (500, 230), (1036, 230)), angle=90)                # arachnotrons
c3.cue(2, 16, 3005, *at3((768, 600), (200, 300), (1336, 300), (768, 200)), angle=90)               # cacodemons
c3.cue(3, 8, 16, *at3((400, 500), (1136, 500)), angle=90, always=True)                             # cyberdemons
# the guards, in the pen, with the waves: they never leave it. Later waves at its back (the earlier ones
# come to the bars), and every spot clear of every other, whatever the wave (the earlier may still be there)
GUARDS3 = {1: [(69, (544, -240)), (69, (800, -240))],
           2: [(66, (512, -392)), (67, (672, -368)), (66, (832, -392))],
           3: [(64, (672, -280)), (69, (592, -392)), (69, (752, -392))]}
for wave, gs in GUARDS3.items():
    for kind, at in gs:
        c3.cue(wave, {1: 0, 2: 16, 3: 8}[wave], kind, *at3(at), angle=90, always=kind == 64)
PENSPOTS3 = [(kind, HX + x, HY + y) for gs in GUARDS3.values() for kind, (x, y) in gs]
for i, (k1, x1, y1) in enumerate(PENSPOTS3):
    assert PEN3[0] < x1 < PEN3[2] and PEN3[1] < y1 < PEN3[3]
    for k2, x2, y2 in PENSPOTS3[i + 1:]:
        assert max(abs(x1 - x2), abs(y1 - y2)) >= ajartime.RADIUS[k1] + ajartime.RADIUS[k2], ("guards", x1, y1, x2, y2)
assert not c3.bad, c3.bad
# every monster of the fight goes through the mouth: wider than the widest by 32, and under its ceiling
assert MOUTH3[1] - MOUTH3[0] > 2 * max(ajartime.RADIUS[k] for k in c3.kinds) + 32
assert all(ajartime.HEIGHT[k] < 192 for k in c3.kinds)
for x, y, _ in c3.placed[1]:
    assert y < PY - 24, "wave 1 starts out of the press"
# over half of what it would take (it was a third until Vadim asked for more): the lobby's, the landing's
# and the boxes' ammunition against every monster's health; the BFG does more with a cell than is reckoned
HARD3 = ajartime.toughness(c3.kinds)
FIRE3 = ajartime.firepower(LOBBY3 + WING3 + BOXES3)
assert 0.5 <= FIRE3 / HARD3 <= 0.7, (FIRE3, HARD3)
REGIONS[3] = ajartime.on_foot("room 3", {"hall": (HX, HY, HX + HW, PY), "chamber": (HX, PY, HX + HW, HY + HH),
                                         "wing": (LANDING3[0], LANDING3[1], UPPER3[2], HY), "cage": CAGE3BOX,
                                         "lobby": (4744, 64, 5000, 320), "box1": (4776, 464, 4984, 656),
                                         "box2": (6552, 464, 6760, 656), "box3": (6100, -216, 6356, -16)},
                              [("hall", "chamber", True), ("hall", "lobby", True), ("wing", "hall"), ("cage", "wing"),
                               ("box1", "hall"), ("box2", "hall"), ("box3", "hall")],
                              # (the hall to the wing: only while someone is under the press, which needs an
                              # earlier self to be of use; the wing to the hall: the window, a drop; the wing
                              # to the cage: only while someone stands on its plate in the chamber)
                              {"hall": [(HX + 4, 720), (HX + HW - 4, 720)],
                               "chamber": [(HX + 4, sum(DOORS3) / 2), (HX + HW - 4, sum(DOORS3) / 2)],
                               "box1": [(4780, 560)], "box2": [(6756, 560)], "box3": [(6228, -212)]})
ajartime.covers(m, "room 3", FIRST, REGIONS[3], zone=(4744, -440, 6608, 1400), exempt=CASES + [PEN_SECTOR3])
# the plate that begins the fight anew: on the lobby's west wall, to the left of the way in
ajartime.fight_anew(m, K3, 4746, 192, 0)


def neighbours(si):
    """The sectors reached from sector si over a two-sided line that does not block."""
    import re
    text = m.textmap()
    sides = [int(v) for v in re.findall(r"sidedef\{[^}]*?sector=(\d+);", text)]
    out = set()
    for ld in re.findall(r"linedef\{([^}]*)\}", text):
        if "sideback" not in ld or "blocking=true" in ld:
            continue
        f = sides[int(re.search(r"sidefront=(\d+);", ld).group(1))]
        k = sides[int(re.search(r"sideback=(\d+);", ld).group(1))]
        if si in (f, k):
            out.add(k if f == si else f)
    return out


# the cage is entered only by its shutter, and overlaps nothing (box 3 or anything else)
assert neighbours(CAGE_SECTOR3) == {CAGE_SHUT_SECTOR3}, neighbours(CAGE_SECTOR3)
for si, poly in enumerate(m.polys):
    if si == CAGE_SECTOR3:
        continue
    xs, ys = [q[0] for q in poly], [q[1] for q in poly]
    assert not (min(xs) < CAGE3BOX[2] and CAGE3BOX[0] < max(xs) and min(ys) < CAGE3BOX[3] and CAGE3BOX[1] < max(ys)), \
        ("the cage overlaps", si, poly)

# === 4. the range: a fight of goes ============================================
# Two keys under fire. The corridor from room 3 ends in a drop of 96 into the
# lobby, which is part of the fight from 16 past the edge. The range
# (7200..7712, 0..1400), the shutter in its north wall and the pen behind it,
# level with the range; the firing spot at the south end. Beside the range's
# north half two wings that mirror each other, each with a key lever at its
# far end: pulled within two seconds of each other (two selves: they are over
# 1750 apart on foot) they open the shutter for half a minute (keys.zs). Each
# wing has guards at their posts (idle until they see the player), more on the
# clock, and wakes those on the demo, idle, as the player steps in (sentries).
FIRST = len(m.polys)
K4, F4 = 4, -96
RX, RY, RW, RL = 7200, 0, 512, 1400
SHUT4 = 3540            # the shutter's sector tag (map32.zs: SHUT32)
WEST4TAG, EAST4TAG = 3541, 3542     # the wings' sectors (and their doorways'): what trips their sentries
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
# the shutter, 384 wide, and the pen behind it (7072..7840, 1416..1736); worked by the key levers only
SHUTTER4 = (7264, 7648)
ajartime.shutter(m, (SHUTTER4[0], RY + RL), (SHUTTER4[1], RY + RL), (0, 1), F4, SHUT4, keep=True)
PEN4 = (7072, 1416, 7840, 1736)
m.sector(rect(*PEN4), floor=F4, ceil=F4 + 192, light=170, color=PEN, wall="AJBOLT")
PEN_SECTOR = len(m.polys) - 1
ajartime.zone(m, K4, 0, *PEN4, mix=True)
# its lamps, on the range's north wall either side of it, facing south
ajartime.shut_lamp(m, SHUTTER4[0] - 32, RY + RL - 2, 270, SHUT4)
ajartime.shut_lamp(m, SHUTTER4[1] + 32, RY + RL - 2, 270, SHUT4)

# the wings. Drawn for the west one, the east one its mirror about the range's axis (x 7456)
MID4 = RX + RW // 2
WING4C = 0xD0D8E0       # the wings' own colour
WW4 = (6896, 720, 7184, 1380)           # the west wing (288 by 660); its range-side wall is 16 thick
WC4 = F4 + 160
DOOR4 = (720, 848)      # the doorway from the range, at the wing's south end, in the range-side wall
BAFFLE4 = 224           # the baffles' length (gap 64): the first from the outer wall, the second from the range side
B1Y, B2Y = 960, 1168
WIN4 = (1268, 1364)     # the window in the range-side wall, beside the lever: its sill 32 over the floor, 80 high
LEVER4 = (7040, 1378)   # in the middle of the north wall, 2 off it


def mx(x, west):
    return x if west else 2 * MID4 - x


def mrect(r, west):
    """The rectangle r of the west wing, in the wing `west` (or the east)."""
    xa, xb = mx(r[0], west), mx(r[2], west)
    return (min(xa, xb), r[1], max(xa, xb), r[3])


def mpt(p, west):
    return (mx(p[0], west), p[1])


BAFFLES4W = [(WW4[0], B1Y, WW4[0] + BAFFLE4, B1Y + 32), (WW4[2] - BAFFLE4, B2Y, WW4[2], B2Y + 32)]
DOORWAY4W = (WW4[2], DOOR4[0], RX, DOOR4[1])
WINDOW4W = (WW4[2], WIN4[0], RX, WIN4[1])
WINGS4 = [WW4, mrect(WW4, False)]
BAFFLES4 = BAFFLES4W + [mrect(b, False) for b in BAFFLES4W]
LEVERS4 = []            # what lies by each lever, for the reckoning
for west in (True, False):
    tag, n = (WEST4TAG, 1) if west else (EAST4TAG, 2)
    wing = mrect(WW4, west)
    ajarmap.fitted(m, wing, [(mrect(b, west), dict(floor=WC4)) for b in BAFFLES4W], floor=F4, ceil=WC4, light=190,
                   color=WING4C, id=tag)
    # the doorway: a gap 16 thick; nothing of the fight walks or flies through it, nor is heard
    door = mrect(DOORWAY4W, west)
    m.sector(rect(*door), floor=F4, ceil=F4 + 128, light=190, color=WING4C, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF",
             id=tag)
    for x in (door[0], door[2]):
        m.line((x, door[1]), (x, door[3]), blockmonsters=True, blocksound=True)
    # the window: open (shots and sight pass), nobody walks through it
    win = mrect(WINDOW4W, west)
    m.sector(rect(*win), floor=F4 + 32, ceil=F4 + 112, light=200, color=WING4C, wall="AJTRIM", ftex="AJTRIMF",
             ctex="AJTRIMF", id=tag)
    for x in (win[0], win[2]):
        m.line((x, win[1]), (x, win[3]), blocking=True)
    # the lever, its lamp beside it (on the range side), and by it two boxes of rockets, a cell pack, a medikit
    ajartime.key_lever(m, *mpt(LEVER4, west), 270, SHUT4, n)
    ajartime.key_lamp(m, *mpt((LEVER4[0] + 48, LEVER4[1]), west), 270, SHUT4, n)
    LEVERS4 += stock(*mpt((6960, 1250), west), (40 if west else -40, 0), 2046, 2046, 17, 2012)
    ajartime.zone(m, K4, 0, *wing, mix=True)
    # the player (not an earlier self) in the wing wakes, idle, what of it stands there on the demo
    ajartime.sentries(m, (wing[0] + wing[2]) / 2, wing[1] + 40, K4, tag, tag, idle=True)

# the two windows face each other across the range, nothing between them
WMID4 = [((w[0] + w[2]) / 2, (w[1] + w[3]) / 2) for w in (WINDOW4W, mrect(WINDOW4W, False))]
assert WMID4[0][1] == WMID4[1][1] and not any(cuts(WMID4[0], WMID4[1], (x, y, x + 64, y + 64)) for x, y in PILLARS4)
assert B2Y + 32 < WIN4[0] and WIN4[1] < WW4[3] and DOOR4[1] < B1Y - 64
# one body cannot pull both levers in time: from one lever to the other (round the baffles, a player's
# middle 16 off every corner, through both doorways) is more than the fastest run in 70 tics
HALF4 = [(LEVER4[0], LEVER4[1] - 22), (BAFFLES4W[1][0] - 16, B2Y + 48), (BAFFLES4W[1][0] - 16, B2Y - 16),
         (BAFFLES4W[0][2] + 16, B1Y + 48), (BAFFLES4W[0][2] + 16, B1Y - 16), (RX, DOOR4[1] - 16)]
LEVER_TO_LEVER4 = walk(*HALF4, *[mpt(p, False) for p in reversed(HALF4)])
assert LEVER_TO_LEVER4 > 1750 and LEVER_TO_LEVER4 > JOIN, LEVER_TO_LEVER4
# the wings clear the boxes, the time doors' recesses, the corridor to room 5 and room 5
for w in WINGS4:
    for o in [(6992, 500, 7184, 680), (7136, 400, 7200, 464), (7712, 560, 7776, 624), (7712, 388, 8048, 516),
              (8048, 96, 8632, 744)]:
        assert w[2] <= o[0] or o[2] <= w[0] or w[3] <= o[1] or o[3] <= w[1], ("a wing overlaps", w, o)

# the fight: all of it AjarCues, calm. The pen: wave 1
c4 = ajartime.Crowd(m, K4, [PEN4] + WINGS4, BAFFLES4, calm=True)


def at4(*pts):
    return [(PEN4[0] + a, PEN4[1] + b) for a, b in pts]


c4.cue(1, 0, 67, *at4((100, 260), (260, 260), (508, 260), (668, 260)), angle=270)       # mancubi
c4.cue(1, 0, 16, *at4((384, 240)), angle=270, always=True)                              # the cyberdemon
c4.cue(1, 0, 3003, *at4((180, 120), (588, 120)), angle=270)                             # barons
c4.cue(1, 0, 66, *at4((60, 60), (300, 60), (468, 60), (708, 60)), angle=270)            # revenants
c4.cue(1, 0, 64, *at4((384, 60), (384, 140)), angle=270, always=True)                   # arch-viles
# the guards of each wing, drawn for the west one: wave 1 idle at their posts, out of sight of the doorway
# (two imps behind the first baffle, two hell knights behind the second, a revenant by the lever); on the
# clock (threshold 0: 25 and 50 seconds) a hell knight and a revenant, then a baron, at the doorway end
GUARDS4 = [(1, 3001, (6930, 1040), 270, True), (1, 3001, (6950, 1110), 270, True),
           (1, 69, (7130, 1260), 180, True), (1, 69, (7130, 1330), 180, True), (1, 66, (6940, 1320), 270, True),
           (2, 69, (6960, 790), 0, False), (2, 66, (7060, 800), 0, False), (3, 3003, (7000, 880), 0, False)]
for west in (True, False):
    for wave, kind, at, ang, idle in GUARDS4:
        c4.cue(wave, 0, kind, mpt(at, west), angle=ang if west else (180 - ang) % 360, idle=idle)
assert not c4.bad, c4.bad
# the posts are out of sight of the doorway: every line from its opening to a wave 1 guard crosses a baffle
for wave, kind, at, ang, idle in GUARDS4:
    if wave == 1:
        for y in range(DOOR4[0], DOOR4[1] + 1, 16):
            for x in (WW4[2], RX):
                assert any(cuts((x, y), at, b) for b in BAFFLES4W), ("a guard seen from the doorway", at, (x, y))
# supplies: the entrance's and what lies by the levers, against the pen's and the guards' health
HARD4 = ajartime.toughness(c4.kinds)
FIRE4X = ajartime.firepower(ENTRY4 + LEVERS4)
assert FIRE4X >= 1.2 * HARD4, (FIRE4X, HARD4)
# time doors west and east (moved south of the wings); boxes 1 and 2 south behind glass, box 3 west
ajartime.hall_door(m, K4, 1, (RX, 400), (RX, 464), (-1, 0), F4, color=HALL)
ajartime.hall_door(m, K4, 2, (RX + RW, 560), (RX + RW, 624), (1, 0), F4, color=HALL)
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
# the case in the range's east wall, seen from the way in: self 1 at a lever on the case's south wall, self 2
# at a lever on its north wall, a clock lamp lit green between them, a dead cyberdemon and mancubus
case((RX + RW, 96), (RX + RW, 288), (1, 0), F4, [(7776, 98, "lever", 0, 90), (7776, 122, "me", 0, 270),
                                                (7776, 122, "go", 1, 0), (7776, 286, "lever", 0, 270),
                                                (7776, 262, "me", 0, 90), (7776, 262, "go", 2, 0),
                                                (7812, 192, "lamp", 0, 180), (7790, 160, "body", 16, 0),
                                                (7800, 225, "body", 67, 0)], color=HALL, ceil=256)
# the steel door the win opens, east, and the corridor on to room 5 (no fight's)
steel(K4, (RX + RW, 420), (RX + RW, 484), (1, 0), F4)
CORRIDOR4 = m.sector(rect(7728, 388, 8048, 516), floor=F4, ceil=F4 + 128, light=180, color=HALL)
REGIONS[4] = ajartime.on_foot("room 4", {"range": (RX, RY, RX + RW, RY + RL + 16), "lobby": (6872, 32, 7200, 320),
                                         "west": WINGS4[0], "east": WINGS4[1], "box1": (7200, -208, 7376, -16),
                                         "box2": (7536, -208, 7712, -16), "box3": (6992, 500, 7184, 680)},
                              [("lobby", "range", True), ("range", "west", True), ("range", "east", True),
                               ("box1", "range"), ("box2", "range"), ("box3", "range")],
                              {"range": [(RX + 4, 432), (RX + RW - 4, 592)], "box1": [(7204, -112)],
                               "box2": [(7708, -112)], "box3": [(6996, 592)]})
ajartime.covers(m, "room 4", FIRST, REGIONS[4], zone=(6888, -72, 8020, 1736), exempt=CASES + [PEN_SECTOR, CORRIDOR4])
# the plate that begins the fight anew: on the lobby's north wall, to the left of the way in
ajartime.fight_anew(m, K4, 6960, 318, 270)

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
     [(SX + 540, CY + 374, "plate", 0, 0), (SX + 540, CY + 374, "me", 0, 180), (SX + 540, CY + 374, "go", 1, 0),
      (SX + 540, CY + 458, "plate", 0, 0), (SX + 540, CY + 458, "me", 0, 180), (SX + 540, CY + 458, "go", 2, 0),
      (SX + 600, CY + 380, "hung", RED, 0), (SX + 600, CY + 452, "hung", BLUE, 0)],
     color=ROOM)
REGIONS[5] = ajartime.on_foot("room 5", {"S": (SX, CY, SX + 512, CY + 512), "L": (LX, CY, LX + 448, CY + 512),
                                         "E": (EX, CY, EX + 512, CY + 448), "night": (NX, NY - 16, NX + 320, NY + 256),
                                         "box": (SX + 152, -240, SX + 344, -48)},
                              [("night", "E"), ("box", "S")],          # (S to L, L to E: earlier selves only)
                              {"S": [(SX + 184, CY + 4)], "L": [(LX + 232, CY + 4)], "E": [(EX + 432, CY + 4)],
                               "box": [(SX + 248, -52)]})
ajartime.covers(m, "room 5", FIRST, REGIONS[5], zone=(SX + 16, -240, EX + 584, NY + 264), exempt=CASES)

# a fight of goes whose boxes are spent is never a dead end: its plate that begins it anew is reached on foot
ajartime.fight_anew_reached(m, {K3: "room 3", K4: "room 4"})

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
