"""Act 2, level 5: "On Reflection" (MAP15). It wears MAP11's look (AJAR_INSTITUTE).

The optics wing's other half: mirrors (a Line_Mirror wall; ajarmap.unseen,
target(unseen=), door(unseen=); src/zscript/mirror.zs, optics.zs). A mirror
shows what is there and cannot be seen, and it turns the emitter's beam.

Places. The mirror hall (the start; both TEAL leaves; frames 101 west, 102
east and 103 north). A mirror stands aslant in its middle, facing north-west:
what flies out of 103 is turned into 101, and out of 101 into 103; 102 looks
at its back. On the north wall a target that only the mirror shows: shot, it
opens the steel door north. West, the darkroom: frame 106, which takes a
TEAL leaf only, and across from it sensor B. North, the gallery: empty to
look at, and its north wall is one long mirror, which shows what lives
there. RED leans in it, and PINK, which only the mirror shows (the secret).
Frame 105. North of that the beam lab: the emitter at its west end fires
east into RED's far side; frame 107. Off the lab two cells behind steel
doors: sensor B opens the first (key 1, BLUE), sensor C the second (key 2;
beyond it the store, VIOLET). BLUE's far side is the periscope room, which
has no other way in: frame 104 on its west wall, and two mirrors across its
east corners that carry what flies out of 104 round to sensor C. Off the
hall behind locks 1 and 2, the night room, whose brass frame takes VIOLET
only.

So: the target in the glass; RED in 103 and a leaf in 101 (or the other way
round), its twin in the darkroom, the emitter: the beam goes by RED, the
mirror and the Pair to sensor B. BLUE out of the first cell, hung anywhere:
through it with the twin, which goes in 104 (or RED itself does), the
emitter again: sensor C. Keys 1 and 2, VIOLET, and the night room.

Secret: PINK, leaning by the gallery's south wall, drawn only in the
mirror. Its far side is a room with the secret way out.
"""
import ajarmap
import map_institute1 as I1
from ajarmap import RED, BLUE, VIOLET, PINK, TEAL, far_id
from map_institute1 import T, dress, tint, over, named, hang, things, frame, LOOK, FACES
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS
from udmf import Map, rect

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    import gfx_institute2
    m.align |= gfx_institute.ALIGNED | gfx_institute2.ALIGNED
H = 256
PALE, MINT, RUST, COLD, STEEL, DIM, PAPER = 0xDCE8DC, 0xC8E0C8, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8, 0xF0E4C8
EMIT = 721                                  # the emitter's thing id
MIRROR = 182                                # Line_Mirror


def solid(part, height=H):                  # to the ceiling: a stack, a tank
    return dict(floor=height, **dress(side=part))


def passage(box, near, far, words, mouth, out):
    """A way through a thick wall, `mouth` its end in the room whose wall is `near`."""
    m.sector(rect(*box), ceil=96, light=160, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    a, b = mouth
    over(a, b, near)
    named(a, b, out, near, words)


def locked(a, b, out, floor, keys, line_id, near, far, words, **k):
    """A locked room door between the rooms whose walls are `near` and `far`."""
    ajarmap.roomdoor(m, a, b, out, floor, keys=keys, line_id=line_id, **k)
    if LOOK:
        c, d = I1._far(a, b, out)
        for (p, q), o, part, s in (((a, b), out, near, words), ((c, d), (-out[0], -out[1]), far, "")):
            key = (LOOK, part, I1._shift(p, q, o), keys, s)
            m.line(p, q, upper=FACES.setdefault(key, f"AJID{LOOK}{len(FACES):02d}"))


def holed(box, holes, features, **base):
    """ajarmap.fitted(), but nothing is built in the rectangles `holes`: what
    stands there is the caller's (a mirror aslant and the floor before it)."""
    rects = [r for r, _ in features] + list(holes)
    xs = sorted({box[0], box[2]} | {v for r in rects for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r in rects for v in (r[1], r[3])})
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            if any(a <= x1 and x2 <= c and b <= y1 and y2 <= d for a, b, c, d in holes):
                continue
            props = dict(base)
            for (a, b, c, d), change in features:
                if a <= x1 and x2 <= c and b <= y1 and y2 <= d:
                    props.update(change)
            m.sector([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], **props)


def aslant(half, a, b, **base):
    """A mirror from a to b across a square hole of holed(): `half` is the
    half of the square that is room, a triangle with a-b its long side."""
    m.sector(half, **base)
    m.line(a, b, special=MIRROR)


def mirror(a, b):
    """The wall piece a-b is a mirror."""
    m.cut(a, b)
    m.line(a, b, special=MIRROR)


# --- the mirror hall -----------------------------------------------------------------
# The beam flies down x = 384 from frame 103 to the mirror and along y = 320
# from the mirror into frame 101 (or the other way): nothing stands there.
LAB = dict(floor=0, ceil=H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
holed((0, 0, 768, 640), [(320, 256, 448, 384)], [
    ((160, 448, 288, 512), I1.box(48, "OT", "OS")), ((480, 448, 608, 512), I1.box(64)), ((576, 144, 640, 208), I1.box(96)),
], **LAB)
aslant([(320, 256), (320, 384), (448, 384)], (320, 256), (448, 384), **LAB)
frame((0, 288), (0, 352), (-1, 0), 101, RUST)
frame((768, 288), (768, 352), (1, 0), 102, RUST)
frame((352, 640), (416, 640), (0, 1), 103, RUST)
ajarmap.target(m, 240, 626, 1, unseen=True)                                  # on the north wall, in the glass only
hang((192, 0), (320, 0), "BB")
hang((544, 640), (672, 640), "CB")
hang((448, 0), (576, 0), "RD")

# --- the darkroom, west: sensor B, and a frame for a leaf ------------------------------
DARK_H = 192
ajarmap.fitted(m, (-704, -64, -128, 256), [
    ((-576, -32, -480, 64), solid("TK", DARK_H)), ((-352, -32, -256, 64), solid("TK", DARK_H)),
    ((-576, 192, -512, 256), solid("TK", DARK_H)),
], floor=0, ceil=DARK_H, light=110, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
passage((-128, 160, 0, 224), "LA", "PU", "DARKROOM", ((0, 160), (0, 224)), (-1, 0))
over((-128, 160), (-128, 224), "PU")
ajarmap.recess(m, (-704, 96), (-704, 160), (-1, 0), 0, 106, far_id(RED), color=tint(COLD), home=TEAL, only=3)
ajarmap.target(m, -146, 128, 2, beam=True, z=30)
hang((-448, 256), (-320, 256), "SL")

# --- the gallery, north, behind the steel door the target in the glass opens ------------
# Its north wall is mirrors from x = -256 to the east wall.
GAL = (-448, 816, 704, 1264)
ajarmap.fitted(m, GAL, [
    ((-192, 976, -128, 1040), I1.pillar("PI")), ((128, 976, 192, 1040), I1.pillar("PI")),
    ((448, 976, 512, 1040), I1.pillar("PI")),
], floor=0, ceil=H, light=200, color=tint(PALE), **dress(wall="LB", ftex="FL", ctex="KL"))
passage((96, 656, 160, 816), "LA", "LB", "GALLERY", ((96, 640), (160, 640)), (0, 1))
over((96, 816), (160, 816), "LB")
ajarmap.steel(m, (96, 640), (160, 640), (0, 1), 0, 1)
m.line((96, 640), (160, 640), id=311)
for x in (-256, 0, 256, 512):                                                # four panes, a strip of wall between
    # each in a frame of trim: set 8 back, a sill 24 high under it and a head over it
    m.sector(rect(x, 1264, x + 192, 1272), floor=24, ceil=200, light=200, wall="AJTRIM", side="AJTRIM",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line((x, 1272), (x + 192, 1272), special=MIRROR)
frame((288, 816), (352, 816), (0, -1), 105, PALE)
ajarmap.unseen(m, GAL)

# --- the beam lab, north of the gallery ---------------------------------------------------
# The beam flies along y = 1568 from the emitter to RED's far side.
ajarmap.fitted(m, (-448, 1440, 1216, 1696), [
    ((-96, 1456, 32, 1520), I1.box(48, "OT", "OS")), ((160, 1616, 288, 1680), I1.box(64)),
    ((736, 1456, 864, 1520), I1.box(64)),
], floor=0, ceil=H, light=190, color=tint(STEEL), **dress(wall="EX", ftex="FE", ctex="KE"))
passage((-384, 1264, -320, 1440), "LB", "EX", "BEAM LAB", ((-384, 1264), (-320, 1264)), (0, 1))
over((-384, 1440), (-320, 1440), "EX")
ajarmap.recess(m, (1216, 1536), (1216, 1600), (1, 0), 0, far_id(RED), 101, far_colour=RED, color=tint(STEEL))
ajarmap.emitter(m, -400, 1568, 0, EMIT, (-448, 1632), (-448, 1664), tex="AJLBF", foot=True)
frame((-256, 1440), (-192, 1440), (0, -1), 107, STEEL)
hang((-448, 1456), (-448, 1584), "CP")
hang((192, 1440), (256, 1440), "R1")
hang((416, 1440), (480, 1440), "R2")
hang((1024, 1440), (1088, 1440), "R3")


# --- the two cells, north of the lab, behind the steel doors the sensors open ------------
def cell(box, door, tag, line_id):
    ajarmap.fitted(m, box, [], floor=0, ceil=160, light=170, color=tint(PAPER), **dress(wall="CK", ftex="FC", ctex="KC"))
    ajarmap.steel(m, door[0], door[1], (0, 1), 0, tag)
    m.line(door[0], door[1], id=line_id)
    over(door[0], door[1], "EX")
    named(door[0], door[1], (0, 1), "EX", "TEST CELL")


cell((-384, 1712, 128, 2032), ((-160, 1696), (-96, 1696)), 2, 312)
cell((384, 1712, 896, 2032), ((448, 1696), (512, 1696)), 3, 313)

# --- the store, beyond the second cell -----------------------------------------------------
ajarmap.fitted(m, (384, 2048, 896, 2368), [
    ((512, 2144, 576, 2304), solid("SK")), ((704, 2144, 768, 2304), solid("SK")),
], floor=0, ceil=H, light=150, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
I1.opening((608, 2032), (672, 2032), (0, 1), "CK", "AR", "STORE")
hang((384, 2176), (384, 2304), "CI")
hang((896, 2176), (896, 2304), "LS")

# --- the periscope room: BLUE's far side, and no other way in ------------------------------
# What flies out of frame 104 goes east along y = 576, south down x = 2112
# and west along y = 64 to sensor C.
PERI = dict(floor=0, ceil=H, light=180, color=tint(MINT), **dress(wall="CO", ftex="FC", ctex="KC"))
holed((1536, 0, 2176, 640), [(2048, 512, 2176, 640), (2048, 0, 2176, 128)], [
    ((1728, 256, 1856, 384), I1.box(48, "OT", "OS")),
], **PERI)
aslant([(2048, 512), (2048, 640), (2176, 512)], (2048, 640), (2176, 512), **PERI)
aslant([(2048, 128), (2176, 128), (2048, 0)], (2176, 128), (2048, 0), **PERI)
frame((1536, 544), (1536, 608), (-1, 0), 104, MINT)
ajarmap.recess(m, (1536, 288), (1536, 352), (-1, 0), 0, far_id(BLUE), 101, far_colour=BLUE, color=tint(MINT))
ajarmap.target(m, 1550, 64, 3, beam=True, z=30)

# --- the secret: PINK's far side, and the secret way out -----------------------------------
ajarmap.fitted(m, (1536, 900, 1792, 1156), [], floor=0, ceil=160, light=160, color=tint(STEEL),
               special=1024, **dress(wall="EV", ftex="FE", ctex="KE"))
ajarmap.recess(m, (1536, 996), (1536, 1060), (-1, 0), 0, far_id(PINK), 101, far_colour=PINK, color=tint(STEEL))
m.cut((1792, 996), (1792, 1060))
m.line((1792, 996), (1792, 1060), special=244, playeruse=True, mid="AJEXIT", exact=True)      # Exit_Secret

# --- the door with locks 1 and 2, and beyond it the night room ----------------------------
EV = dict(ceil=160, light=150, color=tint(STEEL), **dress(wall="EV", ftex="FE", ctex="KE"))
m.sector(rect(784, 96, 880, 160), **EV)
m.sector(rect(880, 64, 1008, 192), **EV)
locked((768, 96), (768, 160), (1, 0), 0, "12", 301, "LA", "EV", "WAY OUT", free_inside=True)
ajarmap.way_home(m, 784, -192, VIOLET, only=True)

# --- doors and keys -----------------------------------------------------------------------
ajarmap.pair(m, TEAL, (40, 520, 0), (728, 520, 180))
ajarmap.door(m, RED, -400, 1000, angle=0)
ajarmap.door(m, PINK, 600, 856, angle=90, unseen=True)
ajarmap.door(m, BLUE, -340, 1990, angle=270)
ajarmap.door(m, VIOLET, 850, 2324, angle=180)
ajarmap.key(m, 1, -340, 1754)
ajarmap.key(m, 2, 840, 1754)

# --- things: the mirror hall ---------------------------------------------------------------
m.thing(384, 48, 1, angle=90)
m.thing(384, 120, 2001)                                                     # shotgun
things(2008, (330, 120), (438, 120))
m.thing(608, 100, 2002)                                                     # chaingun
things(2048, (700, 40))
things(2011, (40, 40), (90, 40))
things(2012, (700, 600), (60, 250))
things(2049, (40, 600), (120, 40))
things(ZOMBIE, (240, 200), (530, 230), (120, 130), angle=270)
things(SERGEANT, (250, 400), (540, 400), (690, 420), angle=270)
things(IMP, (110, 420), (680, 300), (250, 580), (520, 580), (480, 600), (60, 600), angle=270)
things(DEMON, (200, 330), (560, 330), angle=270)
things(CHAINGUNNER, (700, 120), angle=180)
things(ZOMBIE, (60, 480), (700, 560), angle=270)

# --- the darkroom: dark, and the super shotgun ----------------------------------------------
m.thing(-640, 200, 82)
things(2049, (-660, -30), (-180, -30), (-660, 230))
things(2012, (-660, 30), (-180, 230), (-400, 220))
m.thing(-420, 100, 2018)                                                    # green armour
things(SPECTRE, (-420, 0), (-640, 100), (-420, 220), (-220, 100), angle=0)
things(DEMON, (-300, 150), (-520, 130), angle=0)
things(IMP, (-600, -40), (-200, 30), (-200, -30), (-640, 160), (-160, 40), angle=0)
m.thing(-640, 30, KNIGHT, angle=0)
things(IMP, (-300, 220), angle=0)
things(2046, (-640, -40))

# --- the gallery: what only the glass shows ---------------------------------------------------
things(IMP, (-300, 900), (-60, 1100), (60, 900), (260, 1150), (400, 900), (560, 1100), (640, 950), (-380, 1180), angle=270)
things(DEMON, (-160, 1180), (0, 1000), (320, 1000), (560, 900), (-300, 1050), angle=270)
things(KNIGHT, (240, 900), (-60, 880), angle=270)
things(IMP, (-200, 900), (160, 1100), (520, 1200), angle=270)
things(CACO, (60, 1180), (420, 1160), angle=270)
things(2012, (-410, 850), (660, 1220), (20, 850))
things(2049, (-200, 850), (240, 1230), (500, 850))
things(2048, (-100, 1230), (400, 850))
m.thing(660, 850, 2019)                                                     # blue armour, by the door that is not there
things(2046, (-410, 1230))

# --- the beam lab ---------------------------------------------------------------------------------
m.thing(-32, 1504, 2003)                                                    # rocket launcher, at the edge of a crate
things(2046, (200, 1592), (-420, 1474), (1100, 1474))
things(2049, (-420, 1664), (500, 1464), (300, 1464), (40, 1540), (900, 1664))
things(2048, (100, 1664), (-150, 1464), (640, 1664))
things(2012, (500, 1664), (-300, 1600), (60, 1664), (1000, 1470), (1180, 1660))
things(17, (-420, 1520), (520, 1670))
things(IMP, (-100, 1624), (120, 1484), (330, 1624), (420, 1524), (-200, 1504), (480, 1604), (700, 1620), (960, 1500), angle=180)
things(SERGEANT, (0, 1568), (130, 1648), (350, 1484), (620, 1500), angle=180)
things(CHAINGUNNER, (200, 1568), (500, 1524), (1000, 1640), (1100, 1560), angle=180)
things(KNIGHT, (100, 1580), (400, 1604), (900, 1568), angle=180)
things(DEMON, (-200, 1640), (260, 1524), (460, 1664), (600, 1600), (800, 1620), angle=180)
things(REVENANT, (560, 1470), (1150, 1640), angle=180)
things(CACO, (700, 1540), (1050, 1500), angle=180)

# --- the first cell: key 1, BLUE, the plasma rifle ---------------------------------------------------
things(BARON, (-200, 1872), (-300, 1960), angle=270)
things(KNIGHT, (-60, 1804), (-60, 1944), (-200, 1764), (40, 1872), angle=270)
things(2012, (-340, 1830), (90, 1990))
m.thing(90, 1754, 2004)                                                     # the plasma rifle
things(17, (40, 1760))
m.thing(-330, 1900, 2013)                                                   # a soul sphere

# --- the second cell: key 2 ---------------------------------------------------------------------------
things(MANCUBUS, (560, 1872), (720, 1790), (720, 1960), angle=270)
things(CACO, (800, 1880), (460, 1960), angle=270)
things(2012, (860, 1830), (430, 1760))
things(17, (860, 1990))
things(2046, (430, 1990))

# --- the store: VIOLET --------------------------------------------------------------------------------
things(17, (440, 2084), (440, 2324))
things(2046, (850, 2084))
things(2012, (640, 2324), (440, 2224))
things(IMP, (640, 2104), (460, 2184), (820, 2184), angle=270)
things(SOUL, (640, 2224), (420, 2290), (860, 2244), angle=270)
things(REVENANT, (640, 2300), (820, 2300), angle=270)
things(DEMON, (500, 2104), (780, 2104), angle=270)

# --- the periscope room ---------------------------------------------------------------------------------
things(IMP, (1700, 100), (1900, 150), (1700, 500), (1900, 480), (2000, 570), (1620, 420), angle=180)
things(SERGEANT, (1620, 100), (1800, 80), angle=180)
things(DEMON, (1800, 200), (1800, 440), (1960, 220), (1960, 420), angle=180)
things(CHAINGUNNER, (2010, 160), (2010, 480), (1640, 180), angle=180)
things(KNIGHT, (1900, 320), (2090, 320), angle=180)
things(REVENANT, (2100, 240), (2100, 400), angle=180)
things(CACO, (1640, 300), (1960, 320), angle=180)
things(2012, (1580, 40), (1580, 480), (2130, 320))
things(2049, (1580, 200), (1740, 600))
things(17, (1580, 440), (1900, 40))
things(2046, (1900, 600), (1660, 40))
m.thing(1792, 420, 2019)                                                    # blue armour

# --- the secret ----------------------------------------------------------------------------------------
m.thing(1664, 1100, 83)                                                     # megasphere
things(17, (1600, 940), (1720, 940))
things(2046, (1600, 1116), (1740, 1116))

# --- ambushes --------------------------------------------------------------------------------------------
# a leaf, taken: the hall
ajarmap.ambush(m, 10 + TEAL, IMP, (300, 60), (470, 60), (384, 200), angle=90)
ajarmap.ambush(m, 10 + TEAL, DEMON, (150, 240), (620, 260), angle=0)
ajarmap.ambush(m, 10 + TEAL, REVENANT, (60, 100), (700, 240), angle=0, after=4)
# RED, taken: the gallery again, and this time they are seen
ajarmap.ambush(m, 10 + RED, IMP, (-300, 880), (-60, 1150), (200, 1000), (400, 1100), angle=180)
ajarmap.ambush(m, 10 + RED, SPECTRE, (-250, 1150), (60, 950), angle=180)
ajarmap.ambush(m, 10 + RED, KNIGHT, (560, 1000), (300, 880), angle=180, after=3)
# key 1, in the first cell: round you, and then the lab outside
ajarmap.ambush(m, 1, SPECTRE, (-300, 1790), (-150, 1980), (-40, 1770), angle=180)
ajarmap.ambush(m, 1, KNIGHT, (-128, 1600), (60, 1600), angle=90, after=3)
ajarmap.ambush(m, 1, CACO, (300, 1568), (500, 1500), angle=180, after=4)
# BLUE, taken: the lab
ajarmap.ambush(m, 10 + BLUE, REVENANT, (-300, 1500), (-250, 1640), angle=90)
ajarmap.ambush(m, 10 + BLUE, IMP, (-400, 1600), (60, 1470), (360, 1560), angle=90, after=3)
# key 2: the second cell, and the lab
ajarmap.ambush(m, 2, DEMON, (500, 1780), (640, 1960), (780, 1780), angle=0)
ajarmap.ambush(m, 2, BARON, (480, 1568), angle=90, after=3)
# VIOLET, taken: the store, and the cell behind you
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (460, 2084), (820, 2090), angle=270)
ajarmap.ambush(m, 10 + VIOLET, SPECTRE, (640, 1900), (560, 2000), angle=90, after=3)
ajarmap.ambush(m, 10 + VIOLET, MANCUBUS, (640, 1568), angle=180, after=5)
things(BARON, (944, 100), (944, 156), angle=180)                            # before the night room

# --- and what it takes ---------------------------------------------------------------------------------------
things(2049, (384, 600), (-180, 180), (-100, 1664), (440, 1664), (660, 1000), (-380, 900), (-340, 2000), (480, 1740))
things(17, (700, 500), (2130, 200))
things(2046, (60, 150), (360, 1664), (-340, 1730), (860, 1740))
things(2048, (700, 400), (-200, 1474), (300, 1524), (1580, 600))
things(2012, (384, 420), (-150, 1620), (540, 1464), (-60, 2000), (860, 1900), (440, 2124), (984, 80), (100, 1240), (-420, 980), (1180, 1474))
things(8, (256, 464))                                                       # a backpack at the edge of a bench

LEAF_A, LEAF_B = ajarmap.LEAVES[TEAL]
BY_GLASS = ((103, 101), (101, 103))         # RED's frame, and the frame the hall's mirror turns its beam into
PAIRS = ((LEAF_A, LEAF_B), (LEAF_B, LEAF_A))
PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("hall", "lab"), ("lab", "hall"),                                 # the steel door the target in the glass opens
          ("lab", "cell1", "b"), ("cell1", "lab", "b"),                     # the steel doors the sensors open
          ("lab", "cell2", "c"), ("cell2", "lab", "c"),
          ("hall", "night", "12"), ("night", "hall")],
    keys={"1": "cell1", "2": "cell2"},
    frames={101: "hall", 102: "hall", 103: "hall", 106: "hall", 105: "lab", 107: "lab", 104: "peri",
            ajarmap.HOME: "night"},
    only={ajarmap.HOME: VIOLET, 106: (LEAF_A, LEAF_B)},
    doors={
        RED: dict(home="lab", lean="lab"),
        BLUE: dict(home="peri", lean="cell1"),
        VIOLET: dict(home="night", lean="cell2"),
        PINK: dict(home="secret", lean="lab"),
        **ajarmap.leaves(TEAL, "hall", "hall"),
    },
    sights={
        "b": dict(at="lab", say="fire the emitter: the beam is on sensor B",
                  lines=[{RED: (r,), x: (f,), y: (106,)} for r, f in BY_GLASS for x, y in PAIRS]),
        "c": dict(at="lab", say="fire the emitter: the beam is on sensor C",
                  lines=[{RED: (104,)}] + [{RED: (r,), x: (f,), y: (104,)} for r, f in BY_GLASS for x, y in PAIRS]),
    },
)
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
