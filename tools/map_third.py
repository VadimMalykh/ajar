"""The three goes lab (map THIRD): MAP33's whole structure, small. The map is
played three times, in three parts, by three goes of the player, and the
three meet at the end. MAP=THIRD ./run.sh; the tests are MAP=THIRD MODE=3 to
9 tools/smoke.sh. See src/zscript/third.zs and PLAN.md, "The three goes lab".

Part 1 (yellow): the start hall S, the window hall W1 east of it (a fight of
eight), the gantry along the turbine hall R's north wall (0 over R's floor
at -96, a railing: no way down), the gantry's shutter, then the end room E1
with plate 1 and time door 1. RED leans in S; W1's north wall has a frame
whose RED far side is in S's north wall (hung by go 1, seen from part 2).
Part 2 (green): box 2 south of S (glass onto S), a corridor C2 with glass
onto W1's south wall, its east end open onto R 96 over R's floor (a drop),
the fight in R, the steel door the win opens, stairs up, the end room E2
with plate 2, time door 2 and a plate that winds on.
Part 3 (red): box 3 south-west of S (glass onto S), a corridor south and
east, the duct along R's south wall (glass onto R), the end room E3 with the
exit door (open while both plates are stood on, and ten seconds more), the
exit behind it and a plate that winds on.
E1, E2 and E3 are a row with glass between: each sees the other two.
"""
import ajarmap
import ajartime
import ajarthird
from ajarmap import RED, far_id
from udmf import Map, rect

m = Map()
P1 = 0xF0E8C8       # part 1's rooms, yellowish
P2 = 0xD8ECD8       # part 2's, greenish
P3 = 0xF0D8D4       # part 3's, reddish
HALL = 0xD8D4CC     # the turbine hall

W1H = 3301          # window hall 1: S, the way into W1, W1, the way out (a fight spills)
RH = 3302           # window hall 2: the turbine hall
GANTRY = 3303       # the gantry (R's second tag)
GSHUT = 3304        # the gantry's shutter
STEEL = 3305        # the steel door from R to E2
EXIT = 3306         # the exit door in E3
OUT = 3307          # the room behind it
F1 = 101            # the frame in W1's north wall
FLOOR_R = -96

# --- part 1 ----------------------------------------------------------------------
S = m.sector(rect(0, 448, 384, 832), ceil=192, light=200, color=P1, id=W1H)
m.thing(192, 640, 1, angle=0)
m.sector(rect(384, 576, 512, 640), ceil=128, light=190, color=P1, id=W1H)
m.sector(rect(512, 352, 960, 832), ceil=224, light=200, color=P1, id=W1H)
m.sector(rect(960, 704, 1024, 768), ceil=128, light=190, color=P1, id=W1H)
m.thing(100, 520, 2002, angle=90)          # a chaingun and bullets
m.thing(150, 520, 2048, angle=90)
# RED leans in S; the frame in W1's north wall, its far side in S's north wall
ajarmap.door(m, RED, 300, 760, angle=270)
ajarmap.recess(m, (704, 832), (768, 832), (0, 1), 0, F1, far_id(RED), color=P1)
ajarmap.recess(m, (160, 832), (224, 832), (0, 1), 0, far_id(RED), F1, far_colour=RED, color=P1)
W1_MONSTERS = [(3001, 620, 780), (3001, 880, 760), (3001, 760, 660), (3004, 620, 480), (3004, 880, 480),
               (3004, 760, 560), (9, 680, 420), (9, 840, 420)]
for kind, x, y in W1_MONSTERS:
    m.thing(x, y, kind, angle=180, skill=1)
ajarthird.hall(m, 192, 600, 1, 1, W1H)

# the gantry, along R's north wall, and its shutter at the east end; then E1
m.sector(rect(1024, 704, 1792, 768), floor=0, ceil=256, light=170, color=P1, id=GANTRY)
m.line((1024, 704), (1792, 704), mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
ajartime.shutter(m, (1792, 704), (1792, 768), (1, 0), 0, GSHUT)
m.sector(rect(1808, 704, 1920, 768), ceil=128, light=180, color=P1)
E1 = m.sector(rect(1920, 528, 2176, 768), ceil=192, light=210, color=P1)
ajarthird.plate(m, 2048, 640, 1)
ajarthird.time_door_at(m, 1, (2176, 608), (2176, 672), (1, 0), 0, color=P1)

# --- the turbine hall R, its floor at -96: cut round the pit and the two pedestals
for box in [(1024, 0, 1792, 96), (1024, 96, 1280, 288), (1536, 96, 1792, 288), (1024, 288, 1792, 416),
            (1024, 416, 1152, 544), (1280, 416, 1536, 544), (1664, 416, 1792, 544), (1024, 544, 1792, 704)]:
    m.sector(rect(*box), floor=FLOOR_R, ceil=256, light=170, color=HALL, id=RH)
PIT = (1280, 96, 1536, 288)
m.sector(rect(*PIT), floor=FLOOR_R - 64, ceil=256, light=150, color=HALL, wall="AJBOLT", id=RH)
PEDESTALS = [(1152, 416, 1280, 544), (1536, 416, 1664, 544)]
for p in PEDESTALS:
    m.sector(rect(*p), floor=FLOOR_R + 64, ceil=256, light=180, color=HALL, side="AJBOLT", id=RH)
ajarthird.hall(m, 1408, 360, 2, 2, RH, GANTRY)
POSTS = [(67, 1216, 480, 270), (67, 1600, 480, 270), (68, 1408, 192, 90), (71, 1408, 600, 270)]
for kind, x, y, a in POSTS:
    ajarthird.post(m, x, y, 2, kind, a)
assert all(p[0] + 48 <= x <= p[2] - 48 and p[1] + 48 <= y <= p[3] - 48 for p, (k, x, y, a) in zip(PEDESTALS, POSTS))
assert PIT[0] + 64 <= 1408 <= PIT[2] - 64 and PIT[1] + 64 <= 192 <= PIT[3] - 64
ajarthird.watch(m, 1408, 736, GANTRY, 2, 1)
ajarthird.win(m, 1800, 736, 2, GSHUT)
ajarthird.win(m, 1800, 352, 2, STEEL)

# --- part 2 ----------------------------------------------------------------------
BOX2 = ajarthird.box(m, 2, rect(224, 272, 368, 432), ceil=160, light=210, color=P2)
ajartime.glass(m, (240, 448), (352, 448), (0, -1), 0)
ajarthird.box_door_at(m, 2, (224, 320), (224, 384), (-1, 0), 0, color=P2)
m.sector(rect(368, 272, 448, 336), ceil=128, light=190, color=P2)
m.sector(rect(448, 256, 1024, 336), ceil=160, light=180, color=P2)       # C2: its east end is open onto R, 96 up
ajartime.glass(m, (576, 352), (896, 352), (0, -1), 0)                     # onto W1
m.thing(600, 296, 2003, angle=0)                                          # a rocket launcher and rockets
m.thing(660, 296, 2046, angle=0)
ajartime.shutter(m, (1792, 320), (1792, 384), (1, 0), FLOOR_R, STEEL)
ajarmap.stairs(m, (1808, 320), (1808, 384), (1, 0), FLOOR_R, -FLOOR_R, steps=6, depth=16, ceil=128, color=P2)
m.sector(rect(1904, 320, 1920, 384), ceil=128, light=190, color=P2)
E2 = m.sector(rect(1920, 272, 2176, 512), ceil=192, light=210, color=P2)
ajartime.glass(m, (1952, 528), (2144, 528), (0, -1), 0, top=160)         # E1 | E2
ajarthird.plate(m, 2112, 320, 2)
ajarthird.wind(m, 2174, 320, 180)
ajarthird.time_door_at(m, 2, (2176, 416), (2176, 480), (1, 0), 0, color=P2)

# --- part 3 ----------------------------------------------------------------------
BOX3 = ajarthird.box(m, 3, rect(0, 272, 144, 432), ceil=160, light=210, color=P3)
ajartime.glass(m, (16, 448), (128, 448), (0, -1), 0)
ajarthird.box_door_at(m, 3, (0, 320), (0, 384), (-1, 0), 0, color=P3)
m.sector(rect(32, -48, 112, 272), ceil=128, light=180, color=P3)
m.sector(rect(32, -144, 1024, -48), ceil=128, light=170, color=P3)
m.sector(rect(1024, -112, 1920, -16), ceil=128, light=150, color=P3)       # the duct
ajartime.glass(m, (1088, 0), (1728, 0), (0, -1), 0)                       # onto R
E3 = m.sector(rect(1920, -144, 2176, 256), ceil=192, light=210, color=P3)
ajartime.glass(m, (1952, 272), (2144, 272), (0, -1), 0, top=160)          # E2 | E3
ajarthird.wind(m, 2174, 180, 180)
ajartime.shutter(m, (2176, 32), (2176, 96), (1, 0), 0, EXIT)
m.sector(rect(2192, 0, 2320, 128), ceil=128, light=220, color=P3, id=OUT)
m.sector(rect(2320, 0, 2384, 128), ceil=128, light=230, color=P3, ftex="AJTRIMF")
m.line((2320, 0), (2320, 128), special=243, playercross=True)
m.line((2384, 0), (2384, 128), mid="AJEXIT", exact=True)

ajarthird.third(m, 2100, 100, EXIT, OUT, (-100, -200, 2400, 900))

# no part is joined to another on foot (glass, the railing, the drop's height
# are not ways): from S, box 2 and box 3 nothing of another part is reached
PARTS = ajarthird.apart(m, {1: S, 2: BOX2, 3: BOX3})
assert E1 in PARTS[1] and E2 in PARTS[2] and E3 in PARTS[3]

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
