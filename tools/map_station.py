"""The third secret level: "Third Person" (MAP33), reached by MAP20's secret
way out once MAP20 is built. PLAN.md: "MAP33, the third secret level" (the
outline), "The three goes lab" (the engine: src/zscript/third.zs, its helpers
tools/ajarthird.py, the lab map tools/map_third.py), "MAP33 "Third Person": the
first version, as decided" (this map's design) and "... the first playable
version" (what was built). The tests: src/zscript/map33.zs, MAP=MAP33 MODE=n
tools/smoke.sh.

A power station, played whole three times: go k plays part k, and the time
door at the end of part k leads to before, into box k + 1, which looks onto
the gatehouse S where the earlier selves set off. No part is joined to
another on foot (ajarthird.apart): where they meet it is glass, a railing or
a height. North is up (+y), x east; about 8300 x 3000 of rooms in a frame of
8400 x 5400.

Part 1, yellow, along the north (S, the coal yard, the boiler house, the ash
tunnel and its cache, the pump room, the stack court, the gantry over the
turbine hall, E1). Part 2, green, through the middle (box 2, the gallery, the
workshop and its armoury, the pump hall, the stores, the mezzanine, the
turbine hall R, E2). Part 3, red, along the south (box 3, the cable tunnel,
the switchyard, the relay room, the duct along R's south wall, E3 and the
exit). E1, E2 and E3 are a row north to south with glass between.

Window halls (third.zs): 1 the coal yard (part 1; its gate opens when it is
clear), 2 the workshop (part 2; seen from the relay room), 3 the turbine hall
R (part 2; its gantry is the watched place, its posts the future seen; seen
from the duct), 4 the boiler house (part 1; seen from the gallery, so that
BLUE hung again is seen with the fight round it as it was).

Generator checks: the parts apart; every window hall closed to monsters at its
mouths; every post where its monster cannot leave and in sight from the
gantry; the supplies of each part against its monsters (tools/budget.py);
each part's length on foot (python3 tools/map_station.py --walk).
"""
import heapq
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import ajarmap
import ajartime
import ajarthird
import budget
from ajarmap import BLUE, VIOLET, PINK, far_id
from udmf import Map, rect, MONSTERS

m = Map()

# --- heights, tags, colours -----------------------------------------------------------
G, RF, CAT = 0, -128, 128       # the ground; the turbine hall's floor; the boiler house's catwalk and the pump room
SKY = 448                       # an open yard's sky
YARD, WORK, RT, BOIL = 3341, 3342, 3343, 3344          # the window halls' sector tags
GANTRY = 3346                   # the gantry: R's second tag, the watched place
GATE, GSHUT, STEEL, EXIT, OUT, RELAYSHUT = 3351, 3352, 3353, 3354, 3355, 3356
H_YARD, H_WORK, H_R, H_BOIL = 1, 2, 3, 4                # the window halls' numbers
F_BLUE, F_VIOLET, F_PINK, F_CACHE = 101, 102, 103, 104  # frames

Y_ROOM, Y_WAY = 0xF2EAD0, 0xFFE070      # part 1: its rooms, and its corridors and doorways (yellow)
G_ROOM, G_WAY = 0xDCECDA, 0x98EC8C      # part 2 (green)
R_ROOM, R_WAY = 0xF2DCD8, 0xFF9C8C      # part 3 (red)
HALLC = 0xD8D6D0                         # the turbine hall
COAL = 0x58585C
STEELC = 0x9CA4AC
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
BARS = dict(mid="AJGRIL", midboth=True, blocking=True, dontpegbottom=True)


class _Holes:
    """ajarmap.shaped() draws through this: a piece marked `hole` is left out (solid)."""
    def sector(self, poly, **props):
        if not props.pop("hole", False):
            m.sector(poly, **props)


def area(box, feats=(), holes=(), **base):
    """A room `box` with raised or sunk pieces (`feats`: (rect or convex polygon,
    changes)) and solid pieces (`holes`)."""
    ajarmap.shaped(_Holes(), box, list(feats) + [(h, dict(hole=True)) for h in holes], **base)


def inside(poly, x, y):
    n = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            n = not n
    return n


def sec_at(x, y):
    """The sector at x, y (its index)."""
    for i, p in enumerate(m.polys):
        if inside(p, x + .5, y + .5):
            return i
    return None


def grid(box, n, *, step=96, r=24, avoid=()):
    """n places spread over a grid in `box`, `r` clear of its walls and of the
    rectangles `avoid` (grown by r + 8)."""
    x1, y1, x2, y2 = box
    pts = []
    y = y1 + r + 8
    while y <= y2 - r - 8:
        x = x1 + r + 8
        while x <= x2 - r - 8:
            if not any(a[0] - r - 8 < x < a[2] + r + 8 and a[1] - r - 8 < y < a[3] + r + 8 for a in avoid):
                pts.append((x, y))
            x += step
        y += step
    assert len(pts) >= n, (box, n, len(pts))
    return [pts[int(i * len(pts) / n)] for i in range(n)]


def mon(kind, pts, angle=0, skill=None):
    for x, y in pts:
        if skill:
            m.thing(x, y, kind, angle=angle, skill=skill)
        else:
            m.thing(x, y, kind, angle=angle)


def items(kind, *pts):
    for x, y in pts:
        m.thing(x, y, kind)


def opening(a, b, out, floor, color, thick=16, ceil=96):
    """A doorway in a wall, tinted with its part's colour."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    return m.sector([a, b, d, c], floor=floor, ceil=floor + ceil, light=176, wall="AJTRIM", ftex="AJTRIMF",
                    ctex="AJTRIMF", color=color)


def no_monsters(a, b):
    """No monster walks or flies over the line a-b (a window hall's mouth)."""
    m.line(a, b, blockmonsters=True)
    MOUTHS.append((a, b))


def railing(a, b):
    m.line(a, b, **RAIL)


MOUTHS = []          # every window hall's mouths (checked below)
CASES = []


def case(a, b, out, floor, figures, **look):
    """A glass case (ajartime.case) with figures: (x, y, what, kind, angle),
    each inside it (8 clear of its walls; a frame against the back wall)."""
    si = ajartime.case(m, a, b, out, floor, **look)
    deep = 96
    xs = [a[0], b[0], a[0] + out[0] * (16 + deep), b[0] + out[0] * (16 + deep)]
    ys = [a[1], b[1], a[1] + out[1] * (16 + deep), b[1] + out[1] * (16 + deep)]
    for x, y, what, kind, ang in figures:
        r = 1 if what in ("frame", "hung") else 8
        assert min(xs) + r < x < max(xs) - r and min(ys) + r < y < max(ys) - r, (x, y, what)
        ajartime.figure(m, x, y, what, kind=kind, angle=ang)
    CASES.append(si)
    return si


def three(a, b, out, floor, **look):
    """The sign of the level, in a case: the first self (yellow) and the
    second (green) each on a plate, the third (red) walking into a door
    frame at the back."""
    ux, uy = (b[0] - a[0], b[1] - a[1])
    ln = math.hypot(ux, uy)
    ux, uy = ux / ln, uy / ln
    face = {(0, 1): 270, (0, -1): 90, (1, 0): 180, (-1, 0): 0}[tuple(out)]
    back = {(0, 1): 90, (0, -1): 270, (1, 0): 0, (-1, 0): 180}[tuple(out)]

    def at(along, deep):
        return (round(a[0] + ux * along + out[0] * (16 + deep)), round(a[1] + uy * along + out[1] * (16 + deep)))
    figs = []
    for k, along in ((1, 0.22), (2, 0.48)):
        x, y = at(ln * along, 40)
        figs += [(x, y, "plate", 0, 0), (x, y, "me", k, face), (x, y, "go", k, 0)]
    fx, fy = at(ln * 0.78, 94)
    wx, wy = at(ln * 0.78, 64)
    figs += [(fx, fy, "frame", 0, face), (wx, wy, "walking", 3, back), (wx, wy, "go", 3, 0)]
    return case(a, b, out, floor, figs, **look)


# =====================================================================================
# PART 1, yellow: the boiler side
# =====================================================================================
# --- S, the gatehouse: the start; box 2 and box 3 look into it from the south ---------
S_BOX = (0, 2560, 768, 3200)
area(S_BOX, [((96, 2976, 352, 3040), dict(floor=40, side="AJWOOD")),          # the gatekeeper's counter
             ((96, 3040, 128, 3136), dict(floor=40, side="AJWOOD"))],
     holes=[(224, 2752, 288, 2816), (480, 2752, 544, 2816)],                   # two pillars
     ceil=192, light=200, color=Y_ROOM)
m.thing(384, 2640, 1, angle=90)
m.thing(640, 3040, 2001, angle=180)                    # a shotgun
items(2008, (680, 3100), (600, 3100))
items(2011, (160, 2640))
three((0, 2816), (0, 3008), (-1, 0), G, color=Y_ROOM)
# the doorway north, a corridor, the coal yard
opening((448, 3200), (576, 3200), (0, 1), G, Y_WAY)
m.sector(rect(448, 3216, 576, 3696), ceil=128, light=170, color=Y_WAY)
opening((448, 3696), (576, 3696), (0, 1), G, Y_WAY)
mon(3004, [(480, 3620), (544, 3560)], angle=270)

# --- the coal yard: window hall 1, open to the sky -----------------------------------
YARD_BOX = (256, 3712, 1920, 4992)
HEAPS = [(512, 3968, 768, 4160), (1024, 3904, 1216, 4096), (1408, 4032, 1664, 4224), (640, 4352, 896, 4544),
         (1152, 4352, 1408, 4512), (1600, 4416, 1792, 4576)]
yfeat = []
for x1, y1, x2, y2 in HEAPS:
    yfeat.append(((x1, y1, x2, y2), dict(floor=32, color=COAL, ftex="AJPIT", side="AJWALL")))
    yfeat.append(((x1 + 48, y1 + 48, x2 - 48, y2 - 48), dict(floor=72, color=COAL, ftex="AJPIT")))
BUNKER_WALL = (256, 4672, 1920, 4736)
yfeat.append((BUNKER_WALL, dict(floor=176, side="AJBRICK", ftex="AJTRIMF")))      # the bunker's wall: the cacodemons behind it
yfeat.append(((320, 4800, 1856, 4928), dict(floor=48, color=COAL, ftex="AJPIT")))    # coal in the bunker
area(YARD_BOX, yfeat, ceil=SKY, ctex="F_SKY1", light=210, wall="AJBRICK", color=Y_ROOM, id=YARD)
no_monsters((448, 3712), (576, 3712))
ajarthird.hall(m, 300, 3760, H_YARD, 1, YARD)
# the gate to the boiler house: shut until the yard is clear
ajartime.shutter(m, (1920, 4480), (1920, 4352), (1, 0), G, GATE, nomonsters=True, color=Y_WAY)
MOUTHS.append(((1920, 4480), (1920, 4352)))
no_monsters((1936, 4480), (1936, 4352))                 # (and none of the boiler house's stands in it)
m.sector(rect(1936, 4352, 2048, 4480), ceil=128, light=170, color=Y_WAY, id=BOIL)
ajarthird.win(m, 1980, 4416, H_YARD, GATE)
# the fight: zombiemen, sergeants, imps and demons in the yard; cacodemons behind the bunker's wall
YARD_FLOOR = (288, 3744, 1888, 4640)
yard_pts = grid(YARD_FLOOR, 40, step=96, r=32, avoid=HEAPS + [(256, 3712, 704, 3904)])
mon(3004, yard_pts[0:9], angle=270)
mon(9, yard_pts[9:18], angle=270)
mon(3001, yard_pts[18:30], angle=270)
mon(3002, yard_pts[30:37], angle=270)
mon(3002, yard_pts[37:40], angle=270, skill=4)
mon(3005, [(448, 4864), (768, 4864), (1088, 4864), (1408, 4864), (1728, 4864)], angle=270)
mon(3005, [(608, 4864), (1568, 4864)], angle=270, skill=4)
items(2008, (360, 3800), (1800, 3800), (1800, 4300), (360, 4400))
items(2049, (980, 4250), (1300, 4280))
items(2012, (1320, 3800), (900, 3780))
items(2011, (330, 4200), (1860, 4600))
items(2018, (1000, 4600))

# --- the boiler house: window hall 4. BLUE leans on the floor; its frame is in the
# first boiler's face; its far side is on the catwalk, 128 up, where the way on is ----
BOIL_BOX = (2048, 3712, 3584, 4992)
CATWALK = (2048, 4800, 3584, 4992)
BOILERS = [(2176, 4224, 2400, 4544), (2528, 4224, 2752, 4544), (2880, 4224, 3104, 4544), (3232, 4224, 3456, 4544)]
FRAME_B = (2256, 2320)          # frame 101's mouth on the first boiler's south face
bfeat = [(CATWALK, dict(floor=CAT, color=Y_WAY))]
for b in BOILERS:
    bfeat.append((b, dict(floor=288, side="AJBOLT", ftex="AJTRIMF", color=STEELC)))
    bfeat.append(((b[0] + 32, b[1] - 32, b[2] - 32, b[1]), dict(floor=16, side="AJBRICK", color=0xB0A090)))  # its firing step
area(BOIL_BOX, bfeat, holes=[(FRAME_B[0], 4224, FRAME_B[1], 4288)],
     ceil=384, light=172, wall="AJBRICK", color=Y_ROOM, id=BOIL)
ajarmap.recess(m, (FRAME_B[0], 4224), (FRAME_B[1], 4224), (0, 1), G, F_BLUE, far_id(BLUE), color=Y_WAY, tag=BOIL)
ajarmap.recess(m, (2240, 4992), (2304, 4992), (0, 1), CAT, far_id(BLUE), F_BLUE, far_colour=BLUE, tag=BOIL)
ajarmap.door(m, BLUE, 3330, 3880, angle=180)
railing((2048, 4800), (3584, 4800))
ajarthird.hall(m, 2100, 3760, H_BOIL, 1, BOIL)
# the catwalk's way on (east, to the pump room) and the ash tunnel's mouth (east, on the floor)
opening((3584, 4832), (3584, 4960), (1, 0), CAT, Y_WAY)
no_monsters((3584, 4832), (3584, 4960))
opening((3584, 3840), (3584, 3968), (1, 0), G, Y_WAY)
no_monsters((3584, 3840), (3584, 3968))
# the fight: imps and sergeants on the floor; hell knights, revenants, chaingunners on the catwalk
mon(3001, [(2160, 3900), (2600, 3800), (3000, 4000), (3420, 4100)], angle=180)
mon(9, [(2480, 4000), (2860, 3800), (3200, 3760)], angle=180)
mon(69, [(2400, 4900), (2900, 4880), (3400, 4900)], angle=270)
mon(66, [(2150, 4880), (2650, 4900), (3150, 4880)], angle=270)
mon(65, [(2280, 4860), (2520, 4860), (2780, 4860), (3030, 4860), (3280, 4860), (3500, 4860)], angle=270)
mon(69, [(2770, 4920)], angle=270, skill=4)
mon(3001, [(2300, 3760), (3100, 3880)], angle=180)
m.thing(2640, 3780, 2002, angle=90)                     # the chaingun
items(2048, (2700, 3780), (3480, 3780))
items(2012, (2100, 4100), (3500, 4600))
items(2049, (3480, 3840))
m.thing(3200, 4930, 82, angle=180)                      # the super shotgun, on the catwalk
items(2049, (3000, 4930))

# --- the ash tunnel (from the boiler house floor) and the cache at its end (the
# secret of part 1): frame 104 there takes BLUE back to the catwalk, a short cut ----
area((3600, 3840, 4352, 3968), [((3600, 3840, 4352, 3872), dict(ceil=80)), ((3600, 3936, 4352, 3968), dict(ceil=80))],
     ceil=104, light=112, color=Y_WAY, ftex="AJPIT")
mon(3002, [(3760, 3904), (4000, 3904)], angle=180)
mon(58, [(3880, 3904), (4120, 3904), (4260, 3904)], angle=180)
mon(3002, [(4200, 3904)], angle=180, skill=4)
items(2008, (3700, 3880), (3700, 3930))
CACHE = (4352, 3776, 4608, 4032)
m.sector(rect(*CACHE), ceil=128, light=160, color=Y_ROOM, special=1024)
ajarmap.recess(m, (4608, 3872), (4608, 3936), (1, 0), G, F_CACHE, far_id(BLUE), color=Y_WAY)
items(2013, (4480, 3904))
items(2049, (4420, 3820), (4420, 3990))
items(2048, (4550, 3820))

# --- the pump room, 128 up, from the catwalk -------------------------------------------
PUMP1 = (3600, 4352, 4608, 4992)
PUMPS1 = [(3776, 4480, 3904, 4608), (4160, 4480, 4288, 4608), (3776, 4736, 3904, 4864), (4160, 4736, 4288, 4864)]
area(PUMP1, [(p, dict(floor=CAT + 72, side="AJBOLT", color=STEELC)) for p in PUMPS1],
     floor=CAT, ceil=CAT + 192, light=176, color=Y_ROOM)
mon(3002, [(3700, 4420), (4040, 4680), (4480, 4900)], angle=180)
mon(58, [(3700, 4700), (4040, 4420), (4400, 4420), (4040, 4920)], angle=180)
mon(69, [(4480, 4560), (4480, 4440), (4380, 4700)], angle=180)
mon(3001, [(3700, 4920), (4560, 4800), (3980, 4560), (4100, 4380)], angle=180)
mon(69, [(4560, 4680)], angle=180, skill=4)
mon(3001, [(4300, 4920), (3700, 4560)], angle=180)
items(2049, (3680, 4900))
items(2048, (4580, 4380), (4580, 4440))
items(2012, (4000, 4920), (4000, 4400))
items(2018, (3660, 4380))
# the stairs down to the stack court
ajarmap.stairs(m, (4608, 4608), (4608, 4736), (1, 0), CAT, -CAT, steps=8, depth=32, ceil=CAT + 128, color=Y_WAY)

# --- the stack court, open, at the foot of the chimney ----------------------------------
STACK = (4864, 3584, 6144, 4864)
CHIMNEY = ajarmap.octagon(5312, 4032, 5696, 4416, 112)
LEDGES = [(4864, 4768, 6144, 4864), (6048, 3584, 6144, 4768)]
area(STACK, [(l, dict(floor=96, side="AJBRICK", ftex="AJTRIMF")) for l in LEDGES],
     holes=[CHIMNEY], ceil=SKY, ctex="F_SKY1", light=204, wall="AJBRICK", color=Y_ROOM)
mon(3003, [(5200, 4240), (5820, 4100)], angle=180)
m.thing(5504, 3800, 64, angle=90, skill=3)               # the arch-vile, on the higher difficulties
mon(3001, [(4960 + 128 * i, 4816) for i in range(9)], angle=270)          # the ring of imps on the ledges
mon(3001, [(6096, 3680 + 128 * i) for i in range(8)], angle=180)
mon(65, [(5000, 3700), (5900, 3700), (5000, 4600), (5900, 4600)], angle=90)
mon(9, [(5150, 3800), (5750, 3780), (5150, 4500), (5750, 4500)], angle=90)
mon(3003, [(5500, 4600)], angle=270, skill=4)
mon(9, [(5450, 3700), (5300, 4700), (5700, 4700)], angle=90)
mon(3004, [(5000, 4300), (5900, 4300)], angle=90)
m.thing(5504, 3940, 2003, angle=90)                     # the rocket launcher
items(2046, (5380, 3940), (5620, 3940))
items(2010, (4950, 4100), (4950, 4200), (5960, 4100), (5960, 4200))
items(2049, (5960, 3660))
items(2012, (4950, 3660), (5200, 3660))
items(2048, (5960, 4600))
items(2046, (5960, 3800))
items(2008, (5100, 4000), (5100, 4060), (5900, 4000), (5900, 4060))
items(2012, (5600, 4500), (5400, 4500))

# --- the way to the gantry, the gantry over R (128 over its floor, behind a railing),
# its shutter (R's win opens it), E1 ----------------------------------------------------
m.sector(rect(4928, 3264, 5056, 3584), ceil=160, light=170, color=Y_WAY)
mon(3001, [(4992, 3520), (4992, 3440)], angle=90)
GANTRY_BOX = (5056, 3264, 7040, 3392)
m.sector(rect(*GANTRY_BOX), floor=G, ceil=384, light=160, color=Y_WAY, id=GANTRY)
railing((5056, 3264), (7040, 3264))
no_monsters((5056, 3264), (5056, 3392))
ajartime.shutter(m, (7040, 3392), (7040, 3264), (1, 0), G, GSHUT, color=Y_WAY)
MOUTHS.append(((7040, 3392), (7040, 3264)))
m.line((7040, 3392), (7040, 3264), blockmonsters=True)
m.sector(rect(7056, 3264, 7424, 3392), ceil=128, light=176, color=Y_WAY)

E1_BOX = (7424, 3136, 8064, 3520)
E1 = m.sector(rect(*E1_BOX), ceil=192, light=210, color=Y_ROOM)
PLATE1 = (7808, 3328)
ajarthird.plate(m, *PLATE1, 1)
ajarthird.time_door_at(m, 1, (8064, 3296), (8064, 3360), (1, 0), G, color=Y_WAY)
three((7616, 3520), (7808, 3520), (0, 1), G, color=Y_ROOM)

# =====================================================================================
# THE TURBINE HALL R: window hall 3 (part 2's fight), the future seen
# =====================================================================================
R_BOX = (5056, 2048, 7040, 3264)
CASINGS = [(5248, 2560, 5888, 2752), (6208, 2560, 6848, 2752)]       # the two turbines, 96 high
SPIDER_PIT = (5888, 2496, 6208, 2816)                                 # between them, 40 deep
CONDENSERS = [(5376, 2880, 5568, 3072), (6528, 2880, 6720, 3072)]    # 32 deep
BAYS = [(5376, 2048, 5472, 2144), (6016, 2048, 6112, 2144), (6624, 2048, 6720, 2144),     # south wall
        (6944, 2304, 7040, 2400), (6944, 2560, 7040, 2656), (6944, 3072, 7040, 3168)]     # east wall, 96 high
CASING_H, PIT_SPIDER, PIT_COND, BAY_H = 96, 40, 32, 96
rfeat = [(c, dict(floor=RF + CASING_H, side="AJBOLT", ftex="AJTRIMF", color=STEELC)) for c in CASINGS]
rfeat.append((SPIDER_PIT, dict(floor=RF - PIT_SPIDER, ftex="AJPIT", light=150)))
rfeat += [(c, dict(floor=RF - PIT_COND, ftex="AJPIT", light=150)) for c in CONDENSERS]
rfeat += [(b, dict(floor=RF + BAY_H, side="AJBRICK", ftex="AJTRIMF")) for b in BAYS]
area(R_BOX, rfeat, floor=RF, ceil=384, light=168, color=HALLC, id=RT)
for x1, y1, x2, y2 in [SPIDER_PIT] + CONDENSERS:              # the pits: railings nothing passes
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        railing(a, b)
for x1, y1, x2, y2 in CASINGS + BAYS:                         # the islands: no monster is thrown off them
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        if not (a[0] == b[0] == 7040 or a[1] == b[1] == 2048):     # (not along R's walls)
            m.line(a, b, blockmonsters=True)
ajarthird.hall(m, 5100, 2100, H_R, 2, RT, GANTRY)
ajarthird.watch(m, 5120, 3328, GANTRY, H_R, 1)
ajarthird.win(m, 7000, 3330, H_R, GSHUT)
ajarthird.win(m, 7000, 2880, H_R, STEEL)
# the posts: (kind, x, y, angle, the place it stands, skill)
MID = lambda b: ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)
POSTS = [(67, 5408, 2656, 90, CASINGS[0], 1), (67, 5728, 2656, 90, CASINGS[0], 2),
         (67, 6368, 2656, 90, CASINGS[1], 1), (67, 6688, 2656, 90, CASINGS[1], 3),
         (68, *MID(CONDENSERS[0]), 270, CONDENSERS[0], 1), (68, *MID(CONDENSERS[1]), 270, CONDENSERS[1], 2),
         (7, *MID(SPIDER_PIT), 90, SPIDER_PIT, 3),
         (66, *MID(BAYS[0]), 90, BAYS[0], 1), (65, *MID(BAYS[1]), 90, BAYS[1], 1), (66, *MID(BAYS[2]), 90, BAYS[2], 2),
         (65, *MID(BAYS[3]), 180, BAYS[3], 1), (66, *MID(BAYS[4]), 180, BAYS[4], 2), (65, *MID(BAYS[5]), 180, BAYS[5], 3),
         (71, 5300, 2300, 90, None, 1), (71, 6150, 3100, 270, None, 2), (71, 6560, 2300, 90, None, 3),
         (71, 5900, 2200, 90, None, 4)]
for kind, x, y, ang, place, sk in POSTS:
    m.thing(x, y, ajarthird.POST_T, angle=ang, args=(H_R, kind), skill=sk)
FLOOR_AT = {}


def neighbours():
    """Sector -> the sectors it shares a two-sided line with."""
    polys = m._split()
    edges = {}
    for i, p in enumerate(polys):
        for a, b in zip(p, p[1:] + p[:1]):
            edges[(a, b)] = i
    out = {}
    for (a, b), i in edges.items():
        j = edges.get((b, a))
        if j is not None:
            out.setdefault(i, set()).add(j)
    return out


NEAR = neighbours()
for kind, x, y, ang, place, sk in POSTS:
    if place is None:
        assert kind == 71                                                  # (it moves, and leaves no body)
        continue
    r = ajartime.RADIUS[kind]
    assert place[0] + r < x < place[2] - r and place[1] + r < y < place[3] - r, ("no room at the post", kind, x, y)
    s = sec_at(x, y)
    f = m.sectors[s]["floor"]
    FLOOR_AT[(x, y)] = f
    # the floor it can walk on from there (steps of 24 at most) is its island or its pit and nothing more:
    # every neighbour of it differs by more than 24
    island, todo = {s}, [s]
    while todo:
        for j in NEAR.get(todo.pop(), ()):
            if j not in island and abs(m.sectors[j]["floor"] - f) <= 24:
                island.add(j)
                todo.append(j)
    for i in island:
        xs = [p[0] for p in m.polys[i]]
        ys = [p[1] for p in m.polys[i]]
        assert place[0] <= min(xs) and max(xs) <= place[2] and place[1] <= min(ys) and max(ys) <= place[3], \
            ("a post's monster can walk off", kind, x, y)
        for j in NEAR.get(i, ()):
            assert j in island or abs(m.sectors[j]["floor"] - f) > 24
    if f > RF:
        assert f - RF >= 64                                             # a pedestal 64 high or more
    else:
        assert 32 <= RF - f <= 48                                       # a pit 32 deep or more,
        assert RF - f < ajartime.HEIGHT[kind] * 3 / 4                   # shallow enough that its eyes are over the rim
assert SPIDER_PIT[2] - SPIDER_PIT[0] >= 320 and SPIDER_PIT[3] - SPIDER_PIT[1] >= 320

# The sight from the gantry: R in pieces of (x1, y1, x2, y2, floor, ceil), the gantry over it
def tiles(box, feats, floor, ceil):
    xs = sorted({box[0], box[2]} | {v for r, _ in feats for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in feats for v in (r[1], r[3])})
    out = []
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            f = floor
            for r, ch in feats:
                if r[0] <= x1 and x2 <= r[2] and r[1] <= y1 and y2 <= r[3]:
                    f = ch["floor"]
            out.append((x1, y1, x2, y2, f, ceil))
    return out


R_SPACES = tiles(R_BOX, rfeat, RF, 384) + [GANTRY_BOX + (G, 384)]
SEEN_FROM = {}
for kind, x, y, ang, place, sk in POSTS:
    if place is None:
        continue
    body = (x, y, FLOOR_AT[(x, y)] + 8)
    eyes = [(gx, 3328, G + 41) for gx in range(5088, 7024, 32)]
    seen = [e for e in eyes if ajartime.seen(R_SPACES, e, body)]
    assert seen, ("a post not in sight from the gantry", kind, x, y)
    SEEN_FROM[(x, y)] = seen[len(seen) // 2]

# =====================================================================================
# PART 2, green: the machine side
# =====================================================================================
BOX2_BOX = (448, 2304, 704, 2544)
BOX2 = ajarthird.box(m, 2, rect(*BOX2_BOX), ceil=160, light=210, color=G_ROOM)
ajartime.glass(m, (480, 2560), (672, 2560), (0, -1), G)
ajarthird.box_door_at(m, 2, (544, 2304), (608, 2304), (0, -1), G, color=G_WAY)
opening((704, 2368), (704, 2496), (1, 0), G, G_WAY)
m.sector(rect(720, 2368, 1024, 2496), ceil=128, light=170, color=G_WAY)
m.sector(rect(896, 2496, 1024, 3504), ceil=128, light=170, color=G_WAY)
opening((896, 3504), (1024, 3504), (0, 1), G, G_WAY)
mon(3004, [(960, 2800), (960, 3200)], angle=270)
mon(3001, [(960, 3000), (960, 3400)], angle=270)
items(2008, (940, 2560), (980, 2560))
items(2011, (960, 2640))

# --- the gallery: windows onto the coal yard and the boiler house's floor --------------
GALLERY = (896, 3520, 3840, 3696)
area(GALLERY, [((896 + 192 * i, 3520, 896 + 192 * i + 64, 3552), dict(ceil=128)) for i in range(15)],
     ceil=160, light=176, color=G_ROOM)
for a, b in (((960, 3712), (1344, 3712)), ((1472, 3712), (1856, 3712)), ((2112, 3712), (2560, 3712))):
    ajartime.glass(m, a, b, (0, -1), G, top=128)
mon(3001, [(3300, 3600), (3500, 3640), (3700, 3580)], angle=180)
mon(3004, [(3200, 3640), (3420, 3560), (3620, 3640)], angle=180)
mon(9, [(3560, 3600), (3760, 3640)], angle=180)
mon(9, [(3360, 3600)], angle=180, skill=4)
mon(3001, [(2400, 3600), (2600, 3640)], angle=180)
mon(9, [(2800, 3580)], angle=180)
mon(3004, [(3000, 3600), (1800, 3600)], angle=180)
items(2008, (1100, 3560), (1200, 3560), (2000, 3640), (2100, 3640))
items(2007, (1600, 3640), (2420, 3650))
items(2012, (2900, 3640))
items(2049, (1400, 3600))
items(2048, (2240, 3600))
# down, and back west along the workshop's north wall to its door
opening((3712, 3520), (3840, 3520), (0, -1), G, G_WAY)
m.sector(rect(3712, 3216, 3840, 3504), ceil=128, light=170, color=G_WAY)
m.sector(rect(2752, 3104, 3840, 3216), ceil=128, light=170, color=G_WAY)
mon(3001, [(3776, 3300), (3300, 3160)], angle=270)
mon(3004, [(3000, 3160)], angle=0)
opening((2752, 3104), (2880, 3104), (0, -1), G, G_WAY, thick=32)

# --- the workshop: window hall 2. VIOLET leans here; its far side is in the armoury
# behind bars (a plasma rifle, cells, armour for R) -------------------------------------
WORK_BOX = (2688, 2176, 3840, 3072)
BENCHES = [(2944, 2432, 3200, 2496), (3328, 2432, 3584, 2496), (2944, 2752, 3200, 2816), (3328, 2752, 3584, 2816)]
LATHES = [(3072, 2560, 3200, 2688), (3456, 2560, 3584, 2688)]
wfeat = [(b, dict(floor=40, side="AJWOOD", ftex="AJTRIMF")) for b in BENCHES]
wfeat += [(b, dict(floor=72, side="AJBOLT", color=STEELC)) for b in LATHES]
area(WORK_BOX, wfeat, ceil=256, light=184, color=G_ROOM, id=WORK)
no_monsters((2752, 3072), (2880, 3072))
ajarthird.hall(m, 2740, 3020, H_WORK, 2, WORK)
ARMOURY = (2368, 2240, 2688, 2496)
m.sector(rect(*ARMOURY), ceil=160, light=200, color=G_ROOM, id=WORK)
m.line((2688, 2240), (2688, 2496), **BARS)
ajarmap.recess(m, (2688, 2752), (2688, 2816), (-1, 0), G, F_VIOLET, far_id(VIOLET), color=G_WAY, tag=WORK)
ajarmap.recess(m, (2368, 2336), (2368, 2400), (-1, 0), G, far_id(VIOLET), F_VIOLET, far_colour=VIOLET, tag=WORK)
ajarmap.door(m, VIOLET, 3700, 2280, angle=180)
m.thing(2560, 2368, 2004, angle=0)                      # the plasma rifle
items(17, (2460, 2290), (2460, 2440))
items(2019, (2600, 2300))
# the fight
mon(65, [(2800, 2300), (2800, 2960), (3760, 2700), (3300, 2960), (3000, 2240), (3700, 2960)], angle=90)
mon(3002, [(3010, 2620), (3300, 2620), (3400, 2340), (2900, 2620), (3640, 2400), (3250, 2880)], angle=90)
mon(66, [(3000, 2950), (3500, 2940), (2780, 2620), (3740, 2560)], angle=270)
m.thing(3270, 2300, 67, angle=90)                        # a mancubus
mon(3001, [(2780, 2440), (2880, 2860), (3420, 2860), (3740, 2860), (3140, 2900), (3540, 2300)], angle=90)
mon(9, [(3000, 2340), (3200, 2340), (3400, 2620), (3640, 2640)], angle=90)
mon(66, [(2900, 2340)], angle=90, skill=4)
mon(3001, [(3150, 2380), (3400, 2200)], angle=90)
mon(3002, [(2940, 3020), (3160, 3020)], angle=270)
mon(9, [(3460, 3020), (3720, 2440)], angle=270)
items(2049, (2760, 3020), (3620, 3020))
items(2048, (2760, 2200), (3800, 2200))
items(2046, (3260, 2560))
items(2012, (3800, 3020), (2760, 2700))
items(2049, (3100, 2240))
items(2047, (3400, 2240), (3440, 2240))
items(2011, (3700, 2600), (3700, 2650))
# to the pump hall
opening((3840, 2816), (3840, 2944), (1, 0), G, G_WAY)
no_monsters((3840, 2816), (3840, 2944))
m.sector(rect(3856, 2816, 3968, 2944), ceil=128, light=170, color=G_WAY)

# --- the pump hall and the stores: the way round to R's west mezzanine ------------------
PUMP2 = (3968, 2560, 4736, 3136)
PUMPS2 = [(4096, 2688, 4224, 2816), (4480, 2688, 4608, 2816), (4096, 2944, 4224, 3072), (4480, 2944, 4608, 3072)]
area(PUMP2, [(p, dict(floor=80, side="AJBOLT", color=STEELC)) for p in PUMPS2],
     ceil=288, light=176, color=G_ROOM)
mon(3005, [(4352, 2750), (4352, 3000), (4060, 2620), (4660, 2620)], angle=180)
mon(69, [(4060, 3080), (4660, 3080), (4352, 2620)], angle=180)
mon(3001, [(4040, 2880), (4660, 2880), (4290, 3080), (4420, 3080)], angle=180)
mon(3002, [(4290, 2880), (4420, 2880)], angle=180)
mon(65, [(4660, 2750), (4660, 3000)], angle=180)
mon(3005, [(4352, 2880)], angle=180, skill=4)
mon(58, [(4160, 2880), (4544, 2880)], angle=180)
mon(3004, [(4160, 2620), (4544, 2620)], angle=180)
mon(9, [(4224, 3100), (4500, 3100)], angle=180)
items(2046, (4040, 3000), (4040, 3080))
items(2047, (4600, 2620), (4600, 2660))
items(2012, (4290, 2620), (4420, 2620))
items(2049, (4040, 2620), (4680, 3080))
items(17, (4352, 3100))
items(2046, (4680, 2880))
items(2048, (4040, 2700))
opening((4288, 2560), (4416, 2560), (0, -1), G, G_WAY)
STORES = (3968, 2112, 4736, 2544)
SHELVES = [(4128, 2304, 4160, 2496), (4320, 2304, 4352, 2496), (4512, 2304, 4544, 2496)]
NOOK_WALL = [(3968, 2240, 4112, 2272), (4144, 2112, 4176, 2272)]     # crates round the clerk's nook; a gap 32 wide
NOOK = (3968, 2112, 4144, 2240)
area(STORES, [(s, dict(floor=64, side="AJWOOD", ftex="AJTRIMF")) for s in SHELVES]
     + [(w, dict(floor=64, side="AJWOOD", ftex="AJTRIMF")) for w in NOOK_WALL]
     + [(NOOK, dict(special=1024, light=150))],
     ceil=192, light=170, color=G_ROOM)
mon(58, [(4220, 2180), (4420, 2180), (4600, 2180), (4220, 2400)], angle=90)
mon(3001, [(4420, 2400), (4620, 2420), (4040, 2420)], angle=90)
mon(69, [(4600, 2300), (4240, 2300), (4440, 2300)], angle=180)
mon(3002, [(4040, 2340)], angle=90)
mon(58, [(4060, 2500)], angle=90, skill=4)
mon(3004, [(4320, 2180), (4520, 2180)], angle=90)
mon(9, [(4680, 2400), (4240, 2470)], angle=90)
mon(3001, [(4440, 2480)], angle=90)
items(2013, (4680, 2480))                                # a soulsphere before the drop
items(2046, (4680, 2170))
items(17, (4400, 2480))
items(2049, (4040, 2480), (4240, 2200))
items(2047, (4600, 2480), (4560, 2480))
items(2012, (4680, 2260), (4680, 2320))
items(2046, (4050, 2160), (3990, 2200))                  # the clerk's nook: the secret of part 2
items(2019, (4100, 2160))
opening((4736, 2304), (4736, 2432), (1, 0), G, G_WAY)
m.sector(rect(4752, 2304, 4864, 2432), ceil=128, light=170, color=G_WAY)
MEZZ = (4864, 2304, 5056, 3136)
m.sector(rect(*MEZZ), ceil=384, light=168, color=G_WAY)
no_monsters((5056, 2304), (5056, 3136))                  # the drop into R: no monster of R comes up it (lost souls)
mon(3001, [(4960, 3060), (4960, 2380), (4960, 2600), (4960, 2800), (4960, 2960)], angle=0)
items(2046, (4900, 2480))

# --- the steel door (R's win), the stairs up, E2 -----------------------------------------
ajartime.shutter(m, (7040, 2944), (7040, 2816), (1, 0), RF, STEEL, nomonsters=True, color=G_WAY)
MOUTHS.append(((7040, 2944), (7040, 2816)))
ajarmap.stairs(m, (7056, 2816), (7056, 2944), (1, 0), RF, -RF, steps=8, depth=32, ceil=G + 128, color=G_WAY)
m.sector(rect(7312, 2816, 7424, 2944), ceil=128, light=176, color=G_WAY)
E2_BOX = (7424, 2720, 8064, 3120)
E2 = m.sector(rect(*E2_BOX), ceil=192, light=210, color=G_ROOM)
ajartime.glass(m, (7456, 3136), (8032, 3136), (0, -1), G, top=160)       # E1 | E2
PLATE2 = (7808, 2880)
ajarthird.plate(m, *PLATE2, 2)
ajarthird.time_door_at(m, 2, (8064, 2848), (8064, 2912), (1, 0), G, color=G_WAY)
WIND2 = (8062, 3040)
ajarthird.wind(m, *WIND2, 180)
three((7424, 3104), (7424, 2960), (-1, 0), G, color=G_ROOM)

# =====================================================================================
# PART 3, red: the cable side
# =====================================================================================
BOX3_BOX = (64, 2304, 320, 2544)
BOX3 = ajarthird.box(m, 3, rect(*BOX3_BOX), ceil=160, light=210, color=R_ROOM)
ajartime.glass(m, (96, 2560), (288, 2560), (0, -1), G)
ajarthird.box_door_at(m, 3, (64, 2432), (64, 2368), (-1, 0), G, color=R_WAY)
opening((256, 2304), (128, 2304), (0, -1), G, R_WAY)
# --- the cable tunnel: low and dark, trays of cable along its walls ----------------------
TUN = [(128, 1984, 256, 2288), (256, 1984, 1280, 2112)]
area(TUN[0], [((128, 1984, 152, 2288), dict(ceil=72)), ((232, 1984, 256, 2288), dict(ceil=72))],
     ceil=96, light=112, color=R_WAY, ftex="AJPIT")
area(TUN[1], [((256, 1984, 1280, 2008), dict(ceil=72)), ((256, 2088, 1280, 2112), dict(ceil=72))],
     ceil=96, light=112, color=R_WAY, ftex="AJPIT")
mon(58, [(192, 2100), (500, 2048), (760, 2048), (1000, 2048), (1180, 2060), (640, 2060)], angle=180)
mon(3001, [(420, 2048), (880, 2048), (1100, 2048), (1240, 2040)], angle=180)
mon(3001, [(330, 2048), (560, 2048)], angle=180, skill=4)
items(2008, (192, 2250), (192, 2220), (300, 2048), (340, 2048))
items(2011, (700, 2048))

# --- the switchyard, open: transformers in rows, gantries along its south wall ----------
SW = (1280, 896, 2816, 2112)
TRANS = [(x, y, x + 128, y + 192) for x in (1536, 1920, 2304) for y in (1088, 1440)] + \
        [(1920, 1792, 2048, 1984), (2304, 1792, 2432, 1984)]
SWG = [(1344, 896, 2688, 992)]                         # a gantry for the imps, 160 up
sfeat = [(t, dict(floor=112, side="AJBOLT", ftex="AJTRIMF", color=0x8C94A0)) for t in TRANS]
sfeat += [((t[0] - 16, t[1] - 16, t[2] + 16, t[3] + 16), dict(floor=8, color=0xA0A0A0)) for t in TRANS]
sfeat = [f for pair in zip(sfeat[len(TRANS):], sfeat[:len(TRANS)]) for f in pair]     # (plinth, then transformer on it)
sfeat += [(g, dict(floor=160, side="AJBOLT", ftex="AJTRIMF")) for g in SWG]
area(SW, sfeat, ceil=SKY, ctex="F_SKY1", light=200, wall="AJBRICK", color=R_ROOM)
ajarmap.door(m, PINK, 1400, 1860, angle=0)
ajarmap.recess(m, (2816, 1408), (2816, 1472), (1, 0), G, F_PINK, far_id(PINK), color=R_WAY)
# the relay room's shutter, which does not open
m.sector(rect(2816, 1984, 2928, 2112), ceil=128, light=150, color=R_WAY)
ajartime.shutter(m, (2928, 2112), (2928, 1984), (1, 0), G, RELAYSHUT, color=R_WAY)
mon(3001, [(1400 + 96 * i, 944) for i in range(0, 13, 2)], angle=90)                   # imps on the gantry
mon(3001, [(1496 + 192 * i, 944) for i in range(3)], angle=90, skill=4)
mon(68, [(2650, 1200), (2650, 1700), (2200, 1680)], angle=180)
mon(3005, [(2500, 1300), (2600, 1900), (2100, 1300), (2200, 1560), (2560, 1560), (2400, 1050)], angle=180)
mon(3004, [(1700, 1300), (1800, 1700), (1750, 1950), (1400, 1600)], angle=0)
mon(9, [(1700, 1100), (1840, 1500), (2140, 1950), (1400, 1300), (2150, 1150), (1700, 1820)], angle=0)
items(2046, (1360, 2060), (1360, 2000))
items(2049, (1760, 1400), (2160, 1700))
items(2048, (1760, 1600))
items(2012, (1440, 1100), (2760, 1340))
items(2047, (2760, 1600), (2760, 1700))
# the hut by the switchyard's south-east corner: the secret of part 3
opening((2816, 1024), (2816, 960), (1, 0), G, R_ROOM, ceil=72)
m.sector(rect(2832, 928, 2960, 1056), ceil=96, light=140, color=R_ROOM, special=1024)
items(8, (2896, 990))
items(2046, (2930, 1030))
items(2012, (2860, 1030))

# --- the relay room: PINK's far side; a window onto the workshop --------------------------
RELAY = (2944, 1792, 3584, 2160)
CABINETS = [(3072, 1792, 3456, 1840)]
area(RELAY, [(c, dict(floor=96, side="AJBOLT", ftex="AJTRIMF", color=STEELC)) for c in CABINETS],
     ceil=192, light=168, color=R_ROOM)
ajarmap.recess(m, (2944, 1856), (2944, 1920), (-1, 0), G, far_id(PINK), F_PINK, far_colour=PINK)
ajartime.glass(m, (3008, 2176), (3520, 2176), (0, -1), G)          # onto the workshop (from its side)
mon(3001, [(3300, 1950), (3500, 2080)], angle=180)
mon(9, [(3100, 2080), (3500, 1900)], angle=180)
items(2049, (3540, 1880))
items(2012, (3000, 2100))
opening((3584, 1856), (3584, 1984), (1, 0), G, R_WAY)
m.sector(rect(3600, 1856, 4864, 1984), ceil=128, light=150, color=R_WAY)
mon(65, [(4200, 1920), (4600, 1920)], angle=180)
mon(9, [(4400, 1900)], angle=180)
mon(3001, [(4000, 1920), (3800, 1920), (4800, 1920)], angle=180)
items(2049, (4100, 1880))
items(2012, (4300, 1960))
ajarmap.stairs(m, (4864, 1856), (4864, 1984), (1, 0), G, RF, steps=8, depth=24, ceil=G + 128, color=R_WAY)

# --- the duct along R's south wall, behind glass -------------------------------------------
DUCT = (5056, 1856, 7040, 2032)
area(DUCT, [((5056 + 256 * i, 1856, 5056 + 256 * i + 32, 1888), dict(ceil=RF + 96)) for i in range(8)],
     floor=RF, ceil=RF + 128, light=140, color=R_ROOM)
DUCT_WINDOWS = [(5120, 5344), (5504, 5984), (6144, 6592), (6752, 7008)]
for x1, x2 in DUCT_WINDOWS:
    ajartime.glass(m, (x1, 2048), (x2, 2048), (0, -1), RF, top=112)
mon(58, [(5600, 1950), (6300, 1950), (6900, 1950)], angle=180)
mon(3001, [(5900, 1950)], angle=180)
items(2011, (5200, 1950), (6600, 1950))
m.sector(rect(7040, 1856, 7616, 1984), floor=RF, ceil=RF + 128, light=150, color=R_WAY)
ajarmap.stairs(m, (7488, 1984), (7616, 1984), (0, 1), RF, -RF, steps=8, depth=32, ceil=G + 128, color=R_WAY)
m.sector(rect(7488, 2240, 7616, 2304), ceil=128, light=170, color=R_WAY)

# --- E3: the exit door (open while both plates are stood on, and ten seconds more) --------
E3_BOX = (7424, 2304, 8064, 2704)
E3 = m.sector(rect(*E3_BOX), ceil=192, light=210, color=R_ROOM)
ajartime.glass(m, (7456, 2720), (8032, 2720), (0, -1), G, top=160)       # E2 | E3
ajartime.shutter(m, (8064, 2560), (8064, 2496), (1, 0), G, EXIT, color=R_WAY)
m.sector(rect(8080, 2464, 8208, 2592), ceil=128, light=220, color=R_WAY, id=OUT)
m.sector(rect(8208, 2464, 8272, 2592), ceil=128, light=230, color=R_WAY, ftex="AJTRIMF")
m.line((8208, 2464), (8208, 2592), special=243, playercross=True)
m.line((8272, 2464), (8272, 2592), mid="AJEXIT", exact=True)
WIND3 = (8062, 2400)
ajarthird.wind(m, *WIND3, 180)
three((7424, 2592), (7424, 2400), (-1, 0), G, color=R_ROOM)

ajarthird.third(m, 8000, 2660, EXIT, OUT, (-264, 0, 8400, 5400))      # (its middle on the pump hall's floor)

# =====================================================================================
# CHECKS
# =====================================================================================
S = sec_at(384, 2640)
# each part from its start, and from beyond its doors' far sides (BLUE: the catwalk; VIOLET: the armoury;
# PINK: the relay room); a pit behind its railing is reached from nowhere and counted with R below
PARTS = ajarthird.apart(m, {1: [S, sec_at(2272, 4900)], 2: [BOX2, sec_at(2500, 2400)], 3: [BOX3, sec_at(3200, 1950)]})
assert E1 in PARTS[1] and E2 in PARTS[2] and E3 in PARTS[3]
assert sec_at(6000, 2300) in PARTS[2]                                   # R is part 2's
assert sec_at(6000, 3330) in PARTS[1]                                   # the gantry part 1's
assert sec_at(6000, 1950) in PARTS[3]                                   # the duct part 3's


def part_of(x, y):
    s = sec_at(x, y)
    for p, got in PARTS.items():
        if s in got:
            return p
    if s is not None and m.sectors[s]["id"] == RT:                    # R's pits, behind their railings
        return 2
    return None


# each sector's part, for the tests (map33.zs reads it: user_part)
for i, sec in enumerate(m.sectors):
    p = next((q for q, got in PARTS.items() if i in got), 2 if sec["id"] == RT else 0)
    if p:
        sec["raw"]["user_part"] = p


# Every window hall is closed to monsters: each two-sided way out of its sectors is a mouth with a
# monster-blocking line, a line that blocks, glass, or a step no monster takes (more than 24 up from
# inside and the hall's own side the low one is not enough: a flyer goes up it).
def hall_ways(tags):
    """The two-sided lines between a sector with one of `tags` and one without (as edge keys)."""
    polys = m._split()
    edges = {}
    for i, p in enumerate(polys):
        for a, b in zip(p, p[1:] + p[:1]):
            edges[(a, b)] = i
    out = []
    for (a, b), i in edges.items():
        j = edges.get((b, a))
        if j is None or (m.sectors[i]["id"] in tags) == (m.sectors[j]["id"] in tags) or m.sectors[i]["id"] not in tags:
            continue
        out.append((a, b, j))
    return out


def blocked(a, b):
    """Does a line given in m.lineprops cover the edge a-b and keep monsters off it?"""
    for key, pr in m.lineprops.items():
        if len(key) != 2:
            continue
        p1, p2 = tuple(key)
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        ok = True
        for v in (a, b):
            px, py = v[0] - p1[0], v[1] - p1[1]
            t = (px * dx + py * dy) / (dx * dx + dy * dy)
            if dx * py - dy * px != 0 or not -1e-9 <= t <= 1 + 1e-9:
                ok = False
        if ok and (pr.get("blockmonsters") or pr.get("blocking") or pr.get("special") == 156):
            return True
    return False


for tags in ((YARD,), (WORK,), (RT, GANTRY), (BOIL,)):
    for a, b, j in hall_ways(tags):
        assert blocked(a, b), ("a window hall open to monsters", tags, a, b, m.sectors[j]["id"])

# Things in each part, and the supplies against the monsters (skill 3 "Resident", 1 "Just visiting")
SK = m._skills()
BY_PART = {1: [], 2: [], 3: []}
for t, s in zip(m.things, SK):
    p = part_of(t["x"], t["y"])
    if p:
        BY_PART[p].append((t, s))
SUPPLY = {}
RATIO = {1: 1.6, 2: 1.6, 3: 1.6}          # ammunition's damage against the monsters' health, at least
for p, ts in BY_PART.items():
    for level in (3, 1):
        r = budget.reckon([t for t, s in ts], [s for t, s in ts], level)
        SUPPLY[p, level] = r
    r = SUPPLY[p, 3]
    assert r["dmg"] >= RATIO[p] * r["hp"], ("part", p, r["dmg"], r["hp"])
MONSTERS3 = {p: sum(SUPPLY[p, 3]["monsters"].values()) for p in BY_PART}
assert 110 <= MONSTERS3[1] <= 130 and 100 <= MONSTERS3[2] <= 120 and 45 <= MONSTERS3[3] <= 55, MONSTERS3
# every monster of the level is in one of the parts
for t in m.things:
    if t["type"] in MONSTERS or t["type"] == ajarthird.POST_T:
        assert part_of(t["x"], t["y"]), ("a monster in no part", t)

MEASURE = [f"MAP33: {len(m.sectors)} sectors, {len(m.things)} things; monsters on skill 3 "
           f"{MONSTERS3[1]} + {MONSTERS3[2]} + {MONSTERS3[3]}"] + \
          ["    " + budget.line(f"part {p}", SUPPLY[p, lv], lv) for p in (1, 2, 3) for lv in (3, 1)]


# --- each part's length on foot (python3 tools/map_station.py --walk) ---------------------------
RUN = 583            # units a second, running (MAP08's measure)


def walk_lengths(step=16):
    """The shortest walk of each part from its start to its end (plate 1, plate 2, through the exit
    door), with the door it needs fetched and hung on the way: a grid of `step`, the player's box
    kept clear of walls, steps of 24 up at most, any drop down, 56 of headroom, no line that blocks
    crossed (railings, glass, bars); shutters taken as open."""
    x0, y0 = -256, -64
    xs = [p[0] for poly in m.polys for p in poly]
    ys = [p[1] for poly in m.polys for p in poly]
    W, H = int((max(xs) - x0) // step) + 2, int((max(ys) - y0) // step) + 2
    cell = [-1] * (W * H)
    for i, poly in enumerate(m.polys):
        bx = (min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly))
        for cy in range(int((bx[1] - y0) // step), int((bx[3] - y0) // step) + 1):
            for cx in range(int((bx[0] - x0) // step), int((bx[2] - x0) // step) + 1):
                px, py = x0 + cx * step + step / 2, y0 + cy * step + step / 2
                if 0 <= cx < W and 0 <= cy < H and inside(poly, px, py):
                    cell[cy * W + cx] = i
    fl = [s["floor"] for s in m.sectors]
    ce = [s["ceil"] if s["ceil"] > s["floor"] else s["floor"] + 96 for s in m.sectors]
    # cells by a line that blocks are not stood in
    for key, pr in m.lineprops.items():
        if len(key) != 2 or not (pr.get("blocking") or pr.get("blockeverything")):
            continue
        (ax, ay), (bx_, by) = tuple(key)
        n = int(max(abs(bx_ - ax), abs(by - ay)) / 4) + 1
        for k in range(n + 1):
            px, py = ax + (bx_ - ax) * k / n, ay + (by - ay) * k / n
            for dx in (-12, 0, 12):
                for dy in (-12, 0, 12):
                    cx, cy = int((px + dx - x0) // step), int((py + dy - y0) // step)
                    if 0 <= cx < W and 0 <= cy < H:
                        cell[cy * W + cx] = -2
    ok = [False] * (W * H)
    for cy in range(1, H - 1):
        for cx in range(1, W - 1):
            k = cy * W + cx
            if cell[k] >= 0 and all(cell[k + d] >= 0 for d in (1, -1, W, -W, W + 1, W - 1, -W + 1, -W - 1)):
                ok[k] = True

    def at(x, y):
        return int((y - y0) // step) * W + int((x - x0) // step)

    def dist(a, b):
        src, dst = at(*a), at(*b)
        assert ok[src] and ok[dst], ("a walk's end is not stood in", a, b)
        best = {src: 0.0}
        todo = [(0.0, src)]
        moves = [(d, step * (1.4142 if dx and dy else 1)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                 if dx or dy for d in [dy * W + dx]]
        while todo:
            c, k = heapq.heappop(todo)
            if k == dst:
                return c
            if c > best.get(k, 1e18):
                continue
            s1 = cell[k]
            for d, w in moves:
                j = k + d
                if not ok[j]:
                    continue
                s2 = cell[j]
                if fl[s2] - fl[s1] > 24 or min(ce[s1], ce[s2]) - max(fl[s1], fl[s2]) < 56:
                    continue
                if c + w < best.get(j, 1e18):
                    best[j] = c + w
                    heapq.heappush(todo, (c + w, j))
        raise AssertionError(("no walk", a, b))

    legs = {1: [((384, 2640), (3330, 3880)), ((3330, 3880), (FRAME_B[0] + 32, 4200)), ((2272, 4960), PLATE1)],
            2: [((576, 2400), PLATE2)],
            3: [((192, 2400), (1400, 1860)), ((1400, 1860), (2790, 1440)), ((2976, 1888), (8150, 2528))]}
    return {p: [dist(a, b) for a, b in ls] for p, ls in legs.items()}


if __name__ == "__main__":
    if "--walk" in sys.argv:
        for p, ls in walk_lengths().items():
            print(f"part {p}: {round(sum(ls))} units ({' + '.join(str(round(x)) for x in ls)}), "
                  f"{sum(ls) / RUN:.1f} s at a run")
    else:
        sys.stdout.write(m.textmap())
