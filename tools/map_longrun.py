"""Act 3, level 1: "In the Long Run" (MAP21). PLAN.md, "MAP21 "In the Long
Run": the first version, as decided" and "... the first playable version".

The institute twice: NOW (MAP11's look 3, Post Box: emptied, Doom's stone grown
through it, Doom's doors) and THEN, forty years before (look 2, Thaw: full,
every room locked for the night), THEN 8192 north of NOW (tools/ajarthen.py,
src/zscript/then.zs). The clocked door joins the two times: hung in a frame it
hangs in that frame's twin too, and each leads to the other.

Places (NOW's coordinates; x east, y north):
  hall      (0, 0, 1024, 768), the start: the machine in the middle with its
            frame 101 (the clocked door's alone, at both times; it hangs there
            at the start); north of it the desk on a dais. THEN the brass
            shutter in the north wall and the night room behind it. NOW the
            hall is sealed: its only way is the vestibule's bolted door.
  vestibule (1040, 224, 1296, 544). THEN the security post: open to the hall,
            the goods edge (a drop of 40 into the pocket, never back) and the
            turnstile (a squeeze). NOW bolted on both sides; BLUE's far side is
            in it, and arriving draws both bolts (the hall wakes).
  corridor  (1312, 160, 1504, 2256), floor -40. THEN only its first stretch,
            the pocket (y 160..640), behind a night grille. Frame 103 in its
            east wall (NOW the clocked door's alone, THEN any door's).
  cellar    west of the corridor: the landing (1056..1232, 1088..1600, -40)
            with frame 105 in its east wall, the pit (576..1056, floor -200)
            with a stair down, the ledge (576..704, 1280..1472, -56), the store
            behind a pressure door in the pit's north wall (NOW only: key 2).
            The valve THEN (open at the start): NOW the pit stands full to -72.
  goods bay east of the corridor (1568..2160, 1088..1536, -40), frame 108 in
            its north wall; the gallery (2032..2160, 56) along its east wall,
            RED on it. The belt THEN (standing at the start): NOW the hatch
            stair down to the bay cellar (the super shotgun) is open; running,
            a heap of crates climbs to the gallery.
  optics    north of the corridor (1152..1664, 2320..2832, -40), frame 106 in
            its south wall. The beam THEN (at C at the start): NOW a burnt hole
            in wall A, B or C, a closet behind each (A: BLUE; B: a secret; C:
            the rocket launcher).
  lobby     MAP11's lobby and cloakroom, 2560 east (2560..3584, 0..640),
            sealed at both times; RED's far side THEN, frame 110 (NOW a secret).
Room doors NOW are Doom's (BIGDOOR2, USE); THEN the same doorways are the
institute's doors, locked for the night. The checks: src/zscript/map21.zs.
"""
import math

import ajarmap
import ajarthen
import ajarwater as W
import budget
import map_institute1 as I1
import puzzle21
from ajarmap import RED, BLUE
from ajarthen import Times, Part, NOW, THEN, THEN_ID, heights
from udmf import Map

m = Map()
import gfx_institute
m.align |= gfx_institute.ALIGNED            # MAP11's walls are laid by where they are

OFF = (0, 8192)
t = Times(m, off=OFF, at=(512, 32))         # the AjarThen thing, in the hall NOW

EX, EV, LB, CK, CO, LA, AR, PU = (Part(p) for p in ("EX", "EV", "LB", "CK", "CO", "LA", "AR", "PU"))
FE, FL, FC, FA, FR, FP = (Part(p) for p in ("FE", "FL", "FC", "FA", "FR", "FP"))
KE, KL, KC, KA, KP = (Part(p) for p in ("KE", "KL", "KC", "KA", "KP"))
H = 256                                     # every room is this high over its floor (MAP11's walls)
LOW = -40                                   # the corridor's floor, and the rooms off it
STONE, STONE_FLAT = "TANROCK2", "RROCK09"   # Doom's stone, grown through the building NOW
DOOM_DOOR, TRACK = "BIGDOOR2", "DOORTRAK"   # Doom's room doors NOW

# tags and tids
BOLTS = 2100            # the vestibule's two bolted doors (ajarmap.bolted)
SHUTTER = 2101          # the brass shutter THEN (opened by the machine)
MACHINE_LIGHT = 2102    # the hall THEN: brighter once the machine runs
BASIN, PDOOR, LAMP = 2110, 2111, 2112       # the cellar's pit (ajarwater), the store's pressure door, its lamps
HEAP = 2120             # the heap's steps (the belt)
HOLES = 2130            # optics' three holes (the beam)
BELT_TAG = 921          # THEN's belt (ajarmap.BELT_TAG + 21)
VALVE, BELT, BEAM = 11, 12, 13              # the causes' tids (then.zs, map21.zs)
DESK = 2140             # the desk (AjarLongRunDesk, map21.zs)
LOCKED = 2141           # THEN's room doors: "Locked for the night." (AjarThenLocked)
DESK_T = 20187

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACH = 65, 69, 3003, 66, 3006, 3005, 67, 68


def fit(c, box, features, **base):
    """ajarmap.fitted for one copy: the room `box` cut along every feature's
    edges; a feature's changes (later ones win), or None: no sector there."""
    xs = sorted({box[0], box[2]} | {v for r, _ in features for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in features for v in (r[1], r[3])})
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            props, there = dict(base), True
            for (a, b, cc, d), change in features:
                if a <= x1 and x2 <= cc and b <= y1 and y2 <= d:
                    if change is None:
                        there = False
                    else:
                        there = True
                        props.update(change)
            if there:
                c.room((x1, y1, x2, y2), **props)


def look(wall, ftex, ctex, floor=0, **k):
    return dict(wall=wall, ftex=ftex, ctex=ctex, floor=floor, ceil=floor + H, **k)


def box(height, top, side, floor=0):
    return dict(floor=floor + height, ftex=Part(top), side=Part(side))


def pillar(side, floor=0):                  # to the ceiling: the machine, a tank, a pillar
    return dict(floor=floor + H, side=Part(side))


def hang(c, a, b, part):
    """The wall piece a-b shows MAP11's picture `part` in the copy's look."""
    c.cut(a, b)
    c.line(a, b, mid=Part(part), exact=True)


def stone(c, a, b):
    """NOW: Doom's stone where the institute had a way (a wall piece)."""
    c.cut(a, b)
    c.line(a, b, mid=STONE, exact=True)


def frame(a, b, out, n, wall, floor=0, clock=None, **k):
    """A twinned frame; the wall over its mouth is the room's. `clock`: the
    copies where it takes only the clocked door."""
    if clock:
        t.clock_frame(a, b, out, n, floor, when=clock, **k)
    else:
        t.frame(a, b, out, n, floor, **k)
    t.line(a, b, upper=wall)


def sign(c, a, b, out, part, words, oh):
    """MAP11's plate with `words` over the way a-b, seen looking `out`, in the
    copy's look (map_institute1.SIGNS: gfx_institute draws it)."""
    w = abs(a[0] - b[0]) + abs(a[1] - b[1])
    key = (c.look, part, words, I1._shift(c.P(a), c.P(b), out), w, oh)
    c.line(a, b, upper=I1.SIGNS.setdefault(key, f"AJIS{c.look}{len(I1.SIGNS):02d}"), exact=True)


def room_door(a, b, out, floor, wall_near, wall_far, name, *, thick=64):
    """A room door in a wall `thick` deep; a-b its mouth on the corridor's
    side, `out` into the room. NOW Doom's: a door sector between two jamb
    strips, USE opens it (Door_Raise), monsters too. THEN the corridor
    beyond is not built: from inside the room the institute's door, shut,
    "Locked for the night." (AjarThenLocked); declare the rooms first.
    Over it inside the room, at both times, the same plate: CORRIDOR (THEN
    on the door's face, NOW over Doom's door); NOW `name` over it on the
    corridor's side."""
    def p(q, d):
        return (q[0] + out[0] * d, q[1] + out[1] * d)
    n = t.now
    a1, b1, a2, b2, a3, b3 = p(a, 16), p(b, 16), p(a, thick - 16), p(b, thick - 16), p(a, thick), p(b, thick)
    n.sector([a, b, b1, a1], floor=floor, ceil=floor + 96, wall=wall_near, ftex="FLAT20", ctex="FLAT20", light=140)
    n.sector([a2, b2, b3, a3], floor=floor, ceil=floor + 96, wall=wall_far, ftex="FLAT20", ctex="FLAT20", light=140)
    d = n.sector([a1, b1, b2, a2], floor=floor, ceil=floor, wall=DOOM_DOOR, ftex="FLAT20", ctex="FLAT20", light=140)
    for q1, q2 in ((a1, b1), (a2, b2)):
        n.line(q1, q2, back=d, special=12, args=(0, 32, 150), playeruse=True, monsteruse=True, repeatspecial=True)
    for q1, q2 in ((a, a3), (b, b3)):
        n.line(q1, q2, mid=TRACK, dontpegbottom=True)
    sign(n, a, b, out, wall_near, name, 96)
    sign(n, a3, b3, (-out[0], -out[1]), wall_far, "CORRIDOR", 96)
    th = t.then                                     # THEN: the door's face on the room's wall
    key = (th.look, wall_far, I1._shift(th.P(a3), th.P(b3), (-out[0], -out[1])), "", "CORRIDOR")
    th.cut(a3, b3)
    th.line(a3, b3, mid=I1.FACES.setdefault(key, f"AJID{th.look}{len(I1.FACES):02d}"), special=130, args=(LOCKED,),
            playeruse=True, repeatspecial=True, exact=True)


# =================================================================================================
# 1. THE MACHINE HALL (the start)
# =================================================================================================
HALL = look(EX, FE, KE)
MACHINE = [((384, 320, 480, 448), pillar("MC")), ((544, 320, 640, 448), pillar("MC")),
           ((480, 384, 544, 448), pillar("MC")), ((480, 320, 544, 384), None),      # 101's recess in its south face
           ((384, 256, 464, 320), pillar("MC")), ((560, 256, 640, 320), pillar("MC"))]   # its wings, either side of 101
# the desk it is run from, south of it on a dais: through 101 the other time's desk and machine are in view
DAIS = ((416, 112, 608, 208), dict(floor=8, side=Part("B4"), ftex=Part("FA")))
DESK_BOX = ((464, 144, 560, 176), box(40, "DT", "DS", floor=8))
BENCHES = [(896, 448, 960, 640), (64, 448, 128, 640)]                           # THEN benches; NOW their footprints
for c in t.copies:
    furn = [(r, box(48, "BT", "B4") if c.then else dict(ftex="AJIFE2")) for r in BENCHES]
    fit(c, (0, 0, 1024, 768), MACHINE + [DAIS, DESK_BOX] + furn, **HALL,
        **(dict(id=MACHINE_LIGHT, light=176) if c.then else {}))
    hang(c, (640, 0), (768, 0), "NB")                                           # the clock: going THEN, stopped NOW
frame((480, 320), (544, 320), (0, 1), 101, Part("MC"), clock=(NOW, THEN))
t.clocked(512, 300, 90, frame=101)                                              # found hung in the machine
t.line((480, 176), (544, 176), special=130, args=(DESK,), playeruse=True, playeruseback=True, repeatspecial=True,   # its panel faces the machine
       now=dict(lower="AJTHK3"), then=dict(lower="AJTHK2"))
t.now.thing(512, 192, DESK_T, id=DESK)                                         # one desk thing: it tells the times apart
hang(t.then, (64, 768), (192, 768), "CP")                                       # the desk's old controls; a warning
hang(t.then, (832, 768), (896, 768), "WS")
# north wall: THEN the brass shutter and the night room; NOW Doom's stone (all of it)
t.then.sector([(480, 768), (544, 768), (544, 784), (480, 784)], floor=0, ceil=0, wall="AJSHUT", ftex="AJTRIMF",
              ctex="AJTRIMF", light=160, id=SHUTTER)
for x in (480, 544):
    t.then.line((x, 768), (x, 784), mid="AJTRIM", dontpegbottom=True)
ajarmap.way_out(m, *t.then.P((352, 784)), None)
for x0, x1 in ((0, 384), (384, 640), (640, 1024)):
    t.now.line((x0, 768), (x1, 768), mid=STONE)
t.now.cut((384, 768), (640, 768))
# the start: MAP20's sluice in the south wall, shut behind the player (NOW)
t.now.sector([(480, -16), (480, 0), (544, 0), (544, -16)], floor=0, ceil=0, wall="AJSHUT", ftex="AJTRIMF",
             ctex="AJTRIMF", light=120)
m.thing(512, 64, 1, angle=90)
# the hall NOW: Doom's lamps; THEN: benches along the walls
for x, y in ((96, 96), (928, 96), (96, 672), (928, 672)):
    t.now.thing(x, y, 2028)                                                      # floor lamps
# --- the doorway to the vestibule: THEN open; NOW bolted on the vestibule's side
t.then.opening((1024, 352), (1024, 416), (1, 0))
ajarmap.bolted(m, (1024, 352), (1024, 416), (1, 0), 0, BOLTS)

# =================================================================================================
# 2. THE VESTIBULE
# =================================================================================================
VEST = look(AR, FR, KA)
fit(t.now, (1040, 224, 1296, 544), [((1232, 272, 1264, 336), dict(floor=-20, side=Part("B4"))),
                                    ((1264, 272, 1296, 336), dict(floor=-40, side=Part("B4"))),
                                    ((1104, 432, 1200, 496), dict(ftex="AJIFR2"))], **VEST)    # the porter's desk's footprint
fit(t.then, (1040, 224, 1296, 544), [((1104, 432, 1200, 496), box(40, "DT", "DS")),          # the porter's desk
                                     ((1256, 440, 1296, 504), dict(floor=-16, side=Part("B4")))], **VEST)
# (the turnstile's step: down 16 before the squeeze, whose ceiling (-20 + 64) leaves 60 over it; 56 over the
# vestibule's floor would not let the player in)
t.now.far((1136, 224), (1200, 224), (0, -1), BLUE, target=101)                 # BLUE's far side, NOW
t.now.line((1136, 224), (1200, 224), upper=AR)
ajarmap.unbolt(m, (1136, 224), (1200, 224), BOLTS)                              # arriving draws both bolts
ajarmap.bolted(m, (1312, 272), (1312, 336), (-1, 0), LOW, BOLTS)               # to the corridor (NOW)
# THEN: the goods edge (out with a door, never in) and the turnstile (empty hands, both ways)
t.then.room((1296, 272, 1312, 368), floor=0, ceil=128, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF", light=200)
t.then.line((1296, 272), (1296, 368), upper=AR)
ajarmap.squeeze(m, t.then.P((1296, 448)), t.then.P((1296, 496)), (1, 0), -20)
t.then.line((1296, 448), (1296, 496), upper=AR)

# =================================================================================================
# 3. THE CORRIDOR (NOW) / THE POCKET (THEN)
# =================================================================================================
CORR = look(CO, FC, KC, LOW)
t.now.room((1312, 160, 1504, 2256), **CORR, light=104)
t.then.room((1312, 160, 1504, 640), **CORR)
t.then.room((1312, 640, 1504, 704), **dict(CORR, light=40))                     # beyond the night grille: dark
t.then.line((1312, 640), (1504, 640), mid="AJGRIL", midboth=True, blocking=True, dontpegbottom=True)
sign(t.then, (1312, 272), (1312, 368), (-1, 0), "CO", "NO DOORS BEYOND THIS POINT", 168)
t.then.line((1312, 448), (1312, 496), upper=CO)
for c in t.copies:
    hang(c, (1312, 512), (1312, 640), "NB")                                     # the clock in the pocket's stretch
frame((1504, 448), (1504, 512), (1, 0), 103, CO, LOW, clock=(NOW,))

# =================================================================================================
# 4. THE CELLAR (the valve: undo a cause)
# =================================================================================================
PIT, WATER, LEDGE = -200, -72, -56
STEPS = [(1056 - 32 * (i + 1), LOW + (PIT - LOW) * (i + 1) // 7) for i in range(7)]       # x of each step's west edge, its floor
CELLAR = look(LA, FA, KA, LOW)
TANKS = [(640, 1104, 736, 1168), (864, 1520, 960, 1584), (736, 1520, 800, 1584)]
for c in t.copies:
    tag = dict(id=BASIN) if c.now else {}
    feats = [((576, 1088, 1056, 1600), dict(floor=PIT, ftex=Part("FP"), **tag)),
             ((576, 1280, 704, 1472), dict(floor=LEDGE, side=Part("B4"), ftex=Part("FA"), **tag))]
    feats += [((x, 1088, x + 32, 1184), dict(floor=f, side=Part("B4"), **tag)) for x, f in STEPS]
    if c.then:                                                                      # THEN: tanks in the dry pit
        feats += [(r, pillar("TK", LOW)) for r in TANKS]
    else:                                                                           # NOW: where the tanks stood
        feats += [(r, dict(ftex="AJIFP2")) for r in TANKS]
    fit(c, (576, 1088, 1232, 1600), feats, **CELLAR)
room_door((1312, 1440), (1312, 1504), (-1, 0), LOW, CO, LA, "CELLAR", thick=80)
frame((1232, 1248), (1232, 1312), (1, 0), 105, LA, LOW)
# the store (NOW): behind a pressure door in the pit's north wall; it cannot see 105
t.now.room((608, 1632, 736, 1760), floor=PIT, ceil=PIT + 128, wall=LA, ftex=FP, ctex=KA, light=96)
W.pressure_door(m, (640, 1600), (704, 1600), (0, 1), PIT, PDOOR, (BASIN, 0), LAMP,
                look=dict(wall="SPCDOOR1", ftex="FLAT20", ctex="FLAT20"), strip=dict(wall="SUPPORT2", ftex="FLAT20"))
ajarmap.key(m, 2, 672, 1712)
W.basin(m, BASIN, 480 * 512, LOW, floor=PIT, at=(800, 1350))
W.rate(m, 900, 1350, 0, 0, W.FLOAT)                                             # the player floats up when idle in it
t.cause(1144, 1500, VALVE, 2, basin=BASIN, depth=WATER - PIT, start=1)           # 0 shut (dry), 1 open (full): found open
t.lever((1120, 1600), (1184, 1600), VALVE)                                      # on the landing
t.target(588, 1376, VALVE, z=44)                                                # on the ledge, across the pit: 105 sees it
hang(t.then, (576, 1312), (576, 1440), "GA")                                    # the valve's gauges, over the target
for c in t.copies:
    hang(c, (1088, 1088), (1216, 1088), "NB")                                   # the clock on the landing

# =================================================================================================
# 5. THE GOODS BAY (the belt: make a cause)
# =================================================================================================
BAY = look(AR, FR, KA, LOW)
UP_ = 56                                                                         # the gallery
RACKS = [(1616, 1376, 1696, 1440), (1760, 1376, 1840, 1440)]
HEAP_STEPS = [(1840, -64, -16), (1904, -88, 8), (1968, -112, 32)]               # x, floor standing (0), running (1)
for c in t.copies:
    feats = [((2032, 1088, 2160, 1536), dict(floor=UP_, side=Part("B6"), ftex=Part("FA")))]
    if c.now:
        feats += [((x, 1088, x + 64, 1216), dict(floor=f0, side="AJDSTOR", id=HEAP,
                                                 raw=heights(floors=(f0, f1), raised="AJDSTOF")))
                  for x, f0, f1 in HEAP_STEPS]
        feats += [(r, dict(ftex="AJIFR2")) for r in RACKS]                       # where the racks stood
    else:
        feats += [((1600, 1120, 2032, 1216), None)]                                # the belt's band
        feats += [(r, box(96, "BT", "B9", LOW)) for r in RACKS]
    fit(c, (1568, 1088, 2160, 1536), feats, **BAY)
    if c.then:
        first = len(m.sectors)
        ajarmap.belt(m, c.P((1600, 1168)), c.P((2032, 1168)), BELT_TAG, floor=LOW, scroll=False, light=c.light)
        for sec in m.sectors[first:]:                                               # under the room's own ceiling
            sec.update(ceil=LOW + H, ctex=c.tex(KA))
room_door((1504, 1280), (1504, 1344), (1, 0), LOW, CO, AR, "GOODS")
frame((1680, 1536), (1744, 1536), (0, 1), 108, AR, LOW)
# the bay cellar (NOW): the hatch stair's foot, south of the last step; and a secret beside it
t.now.room((1968, 1024, 2032, 1088), floor=-112, ceil=-40, wall="SUPPORT2", ftex="FLAT20", ctex="FLAT20", light=110)
t.now.room((1904, 880, 2096, 1024), floor=-112, ceil=16, wall=PU, ftex=FP, ctex=KP, light=110)
t.now.room((2096, 912, 2112, 976), floor=-112, ceil=-16, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF", light=100)
t.now.room((2112, 880, 2240, 1008), floor=-112, ceil=16, wall=PU, ftex=FP, ctex=KP, light=90, special=1024)
t.now.thing(2000, 940, 82)                                                      # the super shotgun
t.cause(1700, 1300, BELT, 2, tag=HEAP)                                          # 0 standing (found), 1 running
t.belt_run(1700, 1340, BELT, BELT_TAG, (8, 0))
t.lever((1632, 1088), (1696, 1088), BELT)
t.target(1760, 1100, BELT)
ajarmap.door(m, RED, 2096, 1480, angle=270)                                     # on the gallery

# =================================================================================================
# 6. OPTICS (the beam: choose a cause)
# =================================================================================================
OPT = look(LA, FA, KA, LOW)
OPT_BENCHES = [(1216, 2400, 1312, 2448), (1568, 2688, 1648, 2736)]       # clear of the shots from 126 to the targets
for c in t.copies:
    feats = [((1344, 2512, 1472, 2640), dict(ftex=Part("FN")))]                     # an inlay under the emitter, both times
    feats += [(r, box(48, "BT", "B4", LOW) if c.then else dict(ftex="AJIFA2")) for r in OPT_BENCHES]
    fit(c, (1152, 2320, 1664, 2832), feats, **OPT)
    hang(c, (1664, 2672), (1664, 2800), "NB")
room_door((1376, 2256), (1440, 2256), (0, 1), LOW, CO, LA, "OPTICS")
frame((1536, 2320), (1600, 2320), (0, -1), 106, LA, LOW)
OPEN = LOW + 96
HOLE_AT = {1: ((1136, 2544, 1152, 2608), (1008, 2512, 1136, 2640), (1152, 1136)),       # A, west: hole, closet, faces
           2: ((1376, 2832, 1440, 2848), (1344, 2848, 1472, 2976), (2832, 2848)),       # B, north
           3: ((1664, 2544, 1680, 2608), (1680, 2512, 1808, 2640), (1664, 1680))}       # C, east
for n, (hole, closet, faces) in HOLE_AT.items():
    ceils = tuple(OPEN if s == n else LOW for s in range(4))
    t.now.room(hole, floor=LOW, ceil=ceils[3], wall="ASHWALL2", ftex="AJTRIMF", ctex="AJTRIMF", id=HOLES,
               raw=heights(ceils=ceils, hold=True))
    t.now.room(closet, floor=LOW, ceil=LOW + 128, wall=LA, ftex=FA, ctex=KA, light=100,
               **(dict(special=1024) if n == 2 else {}))
    x1, y1, x2, y2 = hole
    for f in faces:                                                                 # shut, the wall goes on over it
        a, b = ((f, y1), (f, y2)) if n != 2 else ((x1, f), (x2, f))
        t.now.line(a, b, upper=LA, dontpegtop=True)
t.cause(1408, 2700, BEAM, 4, tag=HOLES, start=3)                                # 0 off, 1 A, 2 B, 3 C: found at C
t.beam(1408, 2576, BEAM, (180, 90, 0))
t.lever((1216, 2320), (1280, 2320), BEAM)
for x, setting in ((1216, 0), (1280, 1), (1504, 2), (1568, 3)):                 # off, A, B, C: on the north wall
    t.target(x, 2820, BEAM, setting)
ajarmap.door(m, BLUE, 1056, 2576, angle=0)                                      # behind A
t.now.thing(1416, 2920, 2013)                                                   # behind B, the secret: a soul sphere
t.now.thing(1376, 2900, 2046)                                                   # ... rockets
t.now.thing(1744, 2576, 2003)                                                   # behind C: the rocket launcher
t.now.thing(1760, 2540, 2046)

# =================================================================================================
# 7. THE LOBBY (MAP11's, 2560 east): RED's far side THEN; frame 110
# =================================================================================================
LX = 2560
LOBBY = look(LB, FL, KL)
for c in t.copies:
    feats = [((LX + 384, 352, LX + 640, 416), box(40, "DT", "DS")),
             ((LX + 224, 160, LX + 288, 224), pillar("PI")), ((LX + 736, 160, LX + 800, 224), pillar("PI")),
             ((LX + 224, 416, LX + 288, 480), pillar("PI")), ((LX + 736, 416, LX + 800, 480), pillar("PI"))]
    if c.now:
        feats.append(((LX + 896, 256, LX + 1024, 352), dict(special=1024)))         # the lobby now: a secret
    fit(c, (LX, 0, LX + 1024, 640), feats, **LOBBY)
    fit(c, (LX - 336, 64, LX - 16, 256), [((LX - 336, 64, LX - 304, 256), box(48, "UT", "US"))],
        floor=0, ceil=160, wall=CK, ftex=FC, ctex=KC, light=c.light - 40)
    c.opening((LX, 128), (LX, 192), (-1, 0))
    c.line((LX, 128), (LX, 192), upper=LB)
    c.line((LX - 16, 128), (LX - 16, 192), upper=CK)
    hang(c, (LX + 448, 0), (LX + 576, 0), "ST")                                    # the street doors
    hang(c, (LX + 64, 640), (LX + 320, 640), "MO")
    hang(c, (LX + 768, 640), (LX + 896, 640), "NB")
    for y in (64, 128, 192):
        hang(c, (LX - 336, y), (LX - 336, y + 64), "CT")
    c.cut((LX + 384, 640), (LX + 640, 640))                                         # the way north, sealed
    c.line((LX + 384, 640), (LX + 640, 640), mid="AJSHUT" if c.then else STONE, exact=True)
t.then.far((LX, 288), (LX, 352), (-1, 0), RED, target=110)                     # RED's far side THEN
t.then.line((LX, 288), (LX, 352), upper=LB)
frame((LX + 1024, 288), (LX + 1024, 352), (1, 0), 110, LB)
t.then.thing(LX + 512, 470, ajarmap.KEY_T["1"])                                 # key 1, on the porter's board behind the desk
t.then.thing(LX - 240, 160, 8)                                                  # a backpack in the cloakroom
t.now.thing(LX + 512, 520, 83)                                                  # NOW: a megasphere in the dust
for x, y, k in ((LX + 300, 300, 18), (LX + 700, 120, 19), (LX + 820, 520, 20), (LX + 160, 560, 15), (LX + 600, 200, 10)):
    t.now.thing(x, y, k)                                                        # MAP11's fight, forty years on

# =================================================================================================
# THE FIGHTS AND WHAT IS PICKED UP (Doom's monsters NOW; THEN is quiet but for key 1's ambush)
# =================================================================================================
AREAS = {   # name: the box things stand in (NOW's coordinates unless THEN), its copy
    "hall": ((48, 480, 976, 736), NOW), "hallS": ((48, 48, 360, 288), NOW),
    "corrS": ((1328, 560, 1488, 1000), NOW), "corrM": ((1328, 1000, 1488, 1900), NOW),
    "corrN": ((1328, 1900, 1488, 2240), NOW),
    "landing": ((1072, 1104, 1216, 1584), NOW), "pit": ((720, 1200, 1040, 1584), NOW),
    "bay": ((1584, 1232, 2016, 1520), NOW), "gallery": ((2040, 1104, 2152, 1440), NOW),
    "baycell": ((1912, 888, 2088, 1016), NOW),
    "optics": ((1168, 2336, 1648, 2816), NOW),
    "lobbyT": ((LX + 320, 40, LX + 992, 150), THEN), "lobbyE": ((LX + 850, 180, LX + 1000, 600), THEN),
}
AVOID = [(512, 300), (512, 64), (512, 160), (512, 230), (1040, 384), (1168, 240), (1490, 480), (1296, 304), (1248, 1280), (1300, 1472),
         (1520, 1312), (1712, 1520), (1408, 2272), (1568, 2336), (1408, 2576), (LX + 1008, 320), (LX + 16, 320),
         (2096, 1480), (1056, 2576), (1144, 1500), (1700, 1300), (1700, 1340), (LX + 512, 470),
         (1000, 1136), (1150, 1590), (672, 1616), (1408, 2700), (720, 1560)]
TAKEN = []
R = {CACO: 31, MANCUBUS: 48, ARACH: 64, BARON: 24, KNIGHT: 24, DEMON: 30, SPECTRE: 30}
PART_OF = []            # (thing index, part) for every monster and pickup: the budget by part
PROBLEMS = []


def halton(i, b):
    f, r = 1, 0
    while i:
        f /= b
        r += f * (i % b)
        i //= b
    return r


def spot(name, r=20):
    """A free place for a thing of radius r in area `name` (a Halton sequence: the same every build)."""
    (x1, y1, x2, y2), when = AREAS[name]
    for k in range(1, 4000):
        x = round((x1 + r + halton(k, 2) * (x2 - x1 - 2 * r)) / 8) * 8
        y = round((y1 + r + halton(k, 3) * (y2 - y1 - 2 * r)) / 8) * 8
        if not (x1 + r <= x <= x2 - r and y1 + r <= y <= y2 - r):
            continue
        if any(max(abs(x - tx), abs(y - ty)) < r + tr + 8 for tx, ty, tr, tw in TAKEN if tw == when):
            continue
        if any(math.hypot(x - ax, y - ay) < 72 + r for ax, ay in AVOID):
            continue
        px, py = t.copies[when].P((x, y))
        if any(math.hypot(px - th["x"], py - th["y"]) < r + 28 for th in m.things):     # lamps, pickups, the others
            continue
        TAKEN.append((x, y, r, when))
        return x, y
    PROBLEMS.append(f"no room in {name}")
    return x1 + 64, y1 + 64


def mark(part, first):
    PART_OF.extend((i, part) for i in range(first, len(m.things)))


def put(part, name, kind, n, angle=0):
    first = len(m.things)
    for _ in range(n):
        x, y = spot(name, R.get(kind, 20))
        t.copies[AREAS[name][1]].thing(x, y, kind, angle=angle)
    mark(part, first)


def ambush(part, name, cause, kind, n, *, arg=None, angle=0, after=0, near=0):
    """An ambush of n at free spots of `name`: ajarmap's (cause 1..49), or
    ajarthen's (cause 62, 63: `arg`), or the water's (61: `arg` (tag, height))."""
    first = len(m.things)
    spots = [t.copies[AREAS[name][1]].P(spot(name, R.get(kind, 20))) for _ in range(n)]
    if cause == W.AMBUSH_UNDER:
        W.water_ambush(m, False, arg[0], arg[1], kind, *spots, angle=angle, after=after, near=near)
    elif cause >= 62:
        ajarthen.ambush(m, cause, arg, kind, *spots, angle=angle, after=after, near=near)
    else:
        ajarmap.ambush(m, cause, kind, *spots, angle=angle, after=after, near=near)
    mark(part, first)


def items(part, *spec):
    """Pickups: (x, y, kind) in NOW's coordinates, or (x, y, kind, THEN)."""
    first = len(m.things)
    for x, y, kind, *when in spec:
        t.copies[when[0] if when else NOW].thing(x, y, kind)
    mark(part, first)


# --- the hall: the start's shotgun; it wakes when the bolts are drawn (the level's biggest fight)
items("hall", (384, 64, 2001), (640, 64, 2049), (400, 160, 2049), (624, 160, 2048), (160, 400, 2046),
      (864, 400, 2046), (160, 560, 17), (864, 560, 17), (128, 240, 2012), (896, 240, 2012), (512, 200, 2018),
      (288, 112, 2049), (736, 112, 2049))
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, MANCUBUS, 2, arg=BOLTS, angle=270)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, KNIGHT, 3, arg=BOLTS, angle=270, after=1)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, REVENANT, 2, arg=BOLTS, angle=270, after=2)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, CACO, 3, arg=BOLTS, angle=270, after=3)
ambush("hall", "hall", ajarthen.AMBUSH_BOLTS, BARON, 1, arg=BOLTS, angle=270, after=4)
ambush("hall", "hallS", ajarthen.AMBUSH_BOLTS, IMP, 4, arg=BOLTS, angle=90, after=2)
# --- the corridor: the first fight on stepping out of 103; chaingunners at its far end; demons from the rooms
items("corridor", (1456, 400, 2002), (1360, 400, 2048), (1360, 1200, 2048), (1456, 1700, 2049), (1360, 2000, 2049),
      (1456, 2100, 2048), (1456, 900, 2011), (1360, 1600, 2012), (1408, 1100, 2049), (1456, 1500, 2048),
      (1408, 1950, 2015), (1360, 640, 2049))
put("corridor", "corrS", ZOMBIE, 6, 270)
put("corridor", "corrS", SERGEANT, 4, 270)
put("corridor", "corrS", IMP, 4, 270)
put("corridor", "corrM", IMP, 4, 270)
put("corridor", "corrM", DEMON, 4, 270)
put("corridor", "corrM", SERGEANT, 2, 270)
put("corridor", "corrN", CHAINGUNNER, 4, 270)
put("corridor", "corrN", IMP, 3, 270)
# --- the cellar: on the landing; spectres and demons in the dry pit, a knight by the store; cacodemons and
# lost souls over the water when it first stands full again. On the ledge the plasma rifle.
items("cellar", (640, 1376, 2004), (656, 1440, 2047), (640, 1312, 2019), (1080, 1560, 2049), (1200, 1120, 2048),
      (1176, 1560, 2012), (900, 1500, 2046), (1000, 1250, 17))
put("cellar", "landing", IMP, 3, 180)
put("cellar", "landing", SERGEANT, 3, 180)
ambush("cellar", "pit", W.AMBUSH_UNDER, SPECTRE, 3, arg=(BASIN, PIT + 8), angle=0, after=1)
ambush("cellar", "pit", W.AMBUSH_UNDER, DEMON, 3, arg=(BASIN, PIT + 8), angle=0, after=2)
first = len(m.things)
W.water_ambush(m, False, BASIN, PIT + 8, KNIGHT, (720, 1560), angle=270, after=3)
mark("cellar", first)
ambush("cellar", "pit", ajarthen.AMBUSH_CAUSE, CACO, 3, arg=VALVE * 16 + 1, angle=0, after=1)
ambush("cellar", "pit", ajarthen.AMBUSH_CAUSE, SOUL, 4, arg=VALVE * 16 + 1, angle=0, after=2)
# --- the goods bay: among the racks and on the gallery; revenants; an ambush when RED is taken
items("bay", (1600, 1500, 2049), (1640, 1500, 2048), (2120, 1120, 2046), (2000, 960, 2049), (1960, 960, 2049),
      (1600, 1260, 2012), (1800, 1500, 2008), (1840, 1500, 2008))
put("bay", "bay", SERGEANT, 4, 180)
put("bay", "bay", IMP, 4, 180)
put("bay", "bay", REVENANT, 2, 180)
put("bay", "gallery", IMP, 2, 180)
put("bay", "gallery", SERGEANT, 2, 180)
put("bay", "baycell", IMP, 2, 90)
ambush("bay", "bay", 10 + RED, IMP, 3, angle=0, after=1)
ambush("bay", "bay", 10 + RED, KNIGHT, 2, angle=0, after=2)
ambush("bay", "bay", 10 + RED, CHAINGUNNER, 2, angle=0, after=3)
# --- optics: knights and an arachnotron; an ambush through the holes when BLUE is taken
items("optics", (1200, 2360, 2047), (1620, 2360, 2047), (1200, 2780, 17), (1620, 2780, 2046), (1300, 2780, 2048),
      (1500, 2780, 2049), (1408, 2360, 2011), (1300, 2360, 2049))
put("optics", "optics", KNIGHT, 3, 270)
put("optics", "optics", ARACH, 1, 270)
put("optics", "optics", IMP, 4, 270)
ambush("optics", "optics", 10 + BLUE, CACO, 2, angle=270, after=1)
ambush("optics", "optics", 10 + BLUE, SOUL, 3, angle=270, after=1)
ambush("optics", "optics", 10 + BLUE, REVENANT, 1, angle=270, after=2)
ambush("optics", "optics", 10 + BLUE, DEMON, 3, angle=270, after=2)
# --- the lobby THEN: key 1 taken, the ruin's monsters come in (THEN's only fight); NOW the secret
items("lobby", (LX + 128, 96, 2049, THEN), (LX + 896, 96, 2048, THEN), (LX + 128, 544, 2046, THEN),
      (LX + 896, 544, 2049, THEN), (LX + 448, 96, 2012, THEN))
ambush("lobby", "lobbyT", 1, IMP, 4, angle=90, after=0)
ambush("lobby", "lobbyT", 1, SERGEANT, 3, angle=90, after=1)
ambush("lobby", "lobbyE", 1, KNIGHT, 1, angle=180, after=1)
ambush("lobby", "lobbyE", 1, CACO, 2, angle=180, after=3)
items("secrets", (LX + 960, 320, 2019), (2176, 944, 2023), (2200, 920, 2018), (2160, 980, 2046))

# --- the budget, part by part: each part's ammunition does at least 1.6 times its monsters' health (Resident)
SKILLS = m._skills()
BUDGET = {}
for part in dict.fromkeys(p for _, p in PART_OF):
    idx = [i for i, p in PART_OF if p == part]
    for level in (3, 1):
        BUDGET[(part, level)] = budget.reckon([m.things[i] for i in idx], [SKILLS[i] for i in idx], level)
    r = BUDGET[(part, 3)]
    if part != "secrets":
        assert r["dmg"] >= 1.6 * r["hp"], budget.line(part, r, 3)
MONSTERS = {lv: sum(budget.reckon(m.things, SKILLS, lv)["monsters"].values()) for lv in (1, 2, 3, 4)}
assert 110 <= MONSTERS[3] <= 140, MONSTERS
assert not PROBLEMS, PROBLEMS

# =================================================================================================
# THE PUZZLE (tools/puzzle21.py, as built): solved in the full build; nothing stuck, nothing lost
# =================================================================================================
PUZZLE = puzzle21.BUILT

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["budget"]:
        for (part, level), r in BUDGET.items():
            print(budget.line(part, r, level))
        print("monsters by skill:", MONSTERS)
    else:
        sys.stdout.write(m.textmap())
