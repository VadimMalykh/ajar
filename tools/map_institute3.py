"""Act 2, level 3: "Sight Unseen" (MAP13). It wears MAP11's look (AJAR_INSTITUTE).

The institute's optics wing. One new thing, sight lines (ajarmap.target,
emitter, watch; src/zscript/optics.zs): what a hung door lets through
besides the player.

Places. The optics hall (the start; GREEN, both TEAL leaves; frames 101 west
and 102 east, which face each other, and 103 north, which faces a wall). West
of it the darkroom: frame 104, which takes a TEAL leaf only, and across from
it the sensor. North, behind a steel door, the range: 1664 long, an emitter
at its west end, a pit across it, and beyond the pit RED's far side (key 1;
a drop into the pit and steps out of it west). RED and BLUE lean in the
range. North of the range two test cells behind steel doors: GREEN's far
side (knights and barons, key 2, and a target on the far wall) and BLUE's
(mancubi and cacodemons; the lens store beyond it has VIOLET). A rail stands
before both far sides: shots and sight, no walking. Off the hall behind
locks 1 and 2, the night room, whose brass frame takes VIOLET only.

So: GREEN hung in the hall and the target shot through it (the range
opens). RED in 101 or 102 and a leaf in the frame facing it, its twin in
the darkroom: the emitter's beam flies into RED's far side, out of RED's
frame, across the hall, in at the leaf and out at the sensor (the cells
open). Key 1 by RED, key 2 and VIOLET from the cells, and the night room.
Not needed, and worth doing: GREEN and BLUE in the two frames that face each
other, before the cells are opened. What lives in them fights it out.

Secret: none yet.
"""
import ajarmap
import map_institute1 as I1
from ajarmap import RED, BLUE, GREEN, VIOLET, TEAL, far_id
from map_institute1 import T, dress, tint, over, named, hang, things, frame, LOOK, FACES
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS
from udmf import Map, rect

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    import gfx_institute2                       # this level's own props and pictures
    m.align |= gfx_institute.ALIGNED | gfx_institute2.ALIGNED
H = 256
PALE, RUST, COLD, STEEL, DIM, PAPER = 0xDCE8DC, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8, 0xF0E4C8
PIT = -128
EMIT = 721                                  # the emitter's thing id


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


# --- the optics hall ----------------------------------------------------------------
# Nothing stands on the line between frames 101 and 102: the beam flies there.
ajarmap.fitted(m, (0, 0, 768, 640), [
    ((160, 448, 288, 512), I1.box(48, "OT", "OS")), ((480, 448, 608, 512), I1.box(64)), ((576, 176, 640, 240), I1.box(96)),
], floor=0, ceil=H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
frame((0, 288), (0, 352), (-1, 0), 101, RUST)
frame((768, 288), (768, 352), (1, 0), 102, RUST)
frame((352, 640), (416, 640), (0, 1), 103, RUST)
hang((192, 0), (320, 0), "BB")
hang((544, 640), (672, 640), "CB")
hang((448, 0), (576, 0), "RD")                                               # how the beam goes

# --- the darkroom, west: the sensor, and a frame for a leaf --------------------------
DARK_H = 192
ajarmap.fitted(m, (-704, -64, -128, 256), [
    ((-576, -32, -480, 64), solid("TK", DARK_H)), ((-352, -32, -256, 64), solid("TK", DARK_H)),
    ((-576, 192, -512, 256), solid("TK", DARK_H)),
], floor=0, ceil=DARK_H, light=110, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
passage((-128, 160, 0, 224), "LA", "PU", "DARKROOM", ((0, 160), (0, 224)), (-1, 0))
over((-128, 160), (-128, 224), "PU")
ajarmap.recess(m, (-704, 96), (-704, 160), (-1, 0), 0, 104, far_id(RED), color=tint(COLD), home=TEAL, only=3)
ajarmap.target(m, -146, 128, 2, beam=True, z=30)
hang((-448, 256), (-320, 256), "SL")                                         # the safelight, prints on a line

# --- the range, north, behind the steel door the target opens -----------------------
ajarmap.fitted(m, (-448, 816, 1216, 1072), [
    ((-96, 832, 32, 896), I1.box(48, "OT", "OS")), ((160, 992, 288, 1056), I1.box(64)),
] + [((544 + 24 * i, 816, 568 + 24 * i, 1072), dict(floor=PIT * (i + 1) // 8)) for i in range(8)] + [
    ((736, 816, 992, 1072), dict(floor=PIT)),
], floor=0, ceil=H, light=190, color=tint(STEEL), **dress(wall="EX", ftex="FE", ctex="KE"))
passage((96, 656, 160, 816), "LA", "EX", "RANGE", ((96, 640), (160, 640)), (0, 1))
over((96, 816), (160, 816), "EX")
ajarmap.steel(m, (96, 640), (160, 640), (0, 1), 0, 1)
m.line((96, 640), (160, 640), id=311)
ajarmap.recess(m, (1216, 912), (1216, 976), (1, 0), 0, far_id(RED), 101, far_colour=RED, color=tint(STEEL))
ajarmap.watch(m, (992, 816, 1216, 1072), RED)
ajarmap.emitter(m, -400, 944, 0, EMIT, (-448, 1008), (-448, 1040), tex="AJLBF", foot=True)
frame((-320, 816), (-256, 816), (0, -1), 105, STEEL)                         # somewhere to put a door down: five doors, and hands for one
hang((-448, 832), (-448, 960), "CP")                                         # the desk it is fired from
hang((-256, 816), (-192, 816), "WS")
hang((320, 1072), (384, 1072), "WS")
hang((192, 816), (256, 816), "R1")                                           # the range's marks
hang((416, 816), (480, 816), "R2")
hang((1024, 816), (1088, 816), "R3")


# --- the two test cells, north of the range, behind the steel doors the sensor opens --
def cell(box, colour, a, b, out, rail, door):
    x1, y1, x2, y2 = box
    xs = sorted({x1, x2, rail})
    for p, q in zip(xs, xs[1:]):
        m.sector(rect(p, y1, q, y2), ceil=160, light=170, color=tint(PAPER), **dress(wall="CK", ftex="FC", ctex="KC"))
    m.line((rail, y1), (rail, y2), mid="AJGRIL", midboth=True, blocking=True, wrapmidtex=True)
    ajarmap.recess(m, a, b, out, 0, far_id(colour), 101, far_colour=colour, color=tint(PAPER))
    ajarmap.watch(m, box, colour)
    ajarmap.steel(m, door[0], door[1], (0, 1), 0, 2)
    over(door[0], door[1], "EX")
    named(door[0], door[1], (0, 1), "EX", "TEST CELL")


CELL_A, CELL_B = (-384, 1088, 128, 1408), (384, 1088, 896, 1408)
cell(CELL_A, GREEN, (128, 1216), (128, 1280), (1, 0), 88, ((-160, 1072), (-96, 1072)))
m.line((-160, 1072), (-96, 1072), id=312)
ajarmap.target(m, -366, 1248, 1)
cell(CELL_B, BLUE, (384, 1216), (384, 1280), (-1, 0), 424, ((448, 1072), (512, 1072)))
m.line((448, 1072), (512, 1072), id=313)

# --- the lens store, beyond BLUE's cell ----------------------------------------------
ajarmap.fitted(m, (384, 1424, 896, 1744), [
    ((512, 1520, 576, 1680), solid("SK")), ((704, 1520, 768, 1680), solid("SK")),
], floor=0, ceil=H, light=150, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
I1.opening((608, 1408), (672, 1408), (0, 1), "CK", "AR", "LENS STORE")
hang((384, 1552), (384, 1680), "CI")
hang((896, 1552), (896, 1680), "LS")                                         # racks of lenses

# --- the door with locks 1 and 2, and beyond it the night room ----------------------
EV = dict(ceil=160, light=150, color=tint(STEEL), **dress(wall="EV", ftex="FE", ctex="KE"))
m.sector(rect(784, 96, 880, 160), **EV)
m.sector(rect(880, 64, 1008, 192), **EV)
locked((768, 96), (768, 160), (1, 0), 0, "12", 301, "LA", "EV", "WAY OUT", free_inside=True)
ajarmap.way_home(m, 784, -192, VIOLET, only=True)

# --- doors and keys ------------------------------------------------------------------
ajarmap.door(m, GREEN, 40, 440, angle=0)
ajarmap.pair(m, TEAL, (40, 520, 0), (728, 520, 180))
ajarmap.door(m, RED, -300, 850, angle=270)
ajarmap.door(m, BLUE, -200, 1040, angle=90)
ajarmap.door(m, VIOLET, 850, 1700, angle=180)
ajarmap.key(m, 1, 1170, 850)
ajarmap.key(m, 2, -340, 1130)

# --- things: the optics hall ---------------------------------------------------------
m.thing(384, 48, 1, angle=90)
m.thing(384, 120, 2001)                                                     # shotgun
things(2008, (330, 120), (438, 120))
m.thing(608, 152, 2002)                                                     # chaingun, by the tall bench
things(2048, (700, 40))
things(2011, (40, 40), (90, 40))
things(2012, (700, 600))
things(2049, (40, 600))
things(ZOMBIE, (300, 250), (470, 250), (384, 400), angle=270)
things(SERGEANT, (270, 410), (500, 410), (680, 420), angle=270)              # by the benches, not on them: they could not get down
things(IMP, (120, 300), (650, 300), (250, 580), (520, 580), (384, 560), angle=270)
things(DEMON, (200, 380), (560, 380), angle=270)

# --- the darkroom: dark, and the super shotgun ------------------------------------------
m.thing(-640, 200, 82)
things(2049, (-660, -30), (-180, -30))
things(2012, (-660, 30), (-180, 230))
m.thing(-420, 100, 2018)                                                    # green armour
things(SPECTRE, (-420, 0), (-640, 100), (-420, 220), (-220, 100), angle=0)
things(DEMON, (-300, 150), (-520, 130), angle=0)
things(IMP, (-600, -40), (-200, 30), (-200, -30), (-640, 160), (-160, 40), angle=0)
m.thing(-640, 30, KNIGHT, angle=0)

# --- the range ---------------------------------------------------------------------------
m.thing(-32, 880, 2003)                                                     # rocket launcher, at the edge of a crate
things(2046, (200, 968), (-420, 850))
things(2049, (-420, 1040), (500, 840), (300, 840))
things(2048, (100, 1040), (-150, 840))
things(2012, (500, 1040), (-300, 944), (60, 1040))
m.thing(400, 1040, 2019)                                                    # blue armour
things(IMP, (-100, 1000), (120, 860), (330, 1000), (420, 900), (-200, 880), (480, 980), angle=180)
things(SERGEANT, (0, 944), (130, 1024), (350, 860), angle=180)
things(CHAINGUNNER, (200, 944), (500, 900), angle=180)
things(KNIGHT, (100, 944), (400, 980), angle=180)
things(DEMON, (-60, 944), (260, 900), (460, 1040), angle=180)
things(REVENANT, (520, 944), angle=180)
things(DEMON, (800, 860), (900, 1000), angle=180)                           # in the pit
things(SPECTRE, (840, 944), (940, 880), angle=180)
things(2012, (960, 1040))
things(2049, (780, 1040))
things(CHAINGUNNER, (1060, 880), (1060, 1010), (1150, 944), angle=180)      # beyond the pit, by RED's far side
things(IMP, (1040, 944), (1160, 1030), angle=180)
things(2046, (1180, 1040))
things(17, (1180, 890))

# --- the cells ------------------------------------------------------------------------------
things(BARON, (-200, 1248), (-300, 1350), angle=0)
things(KNIGHT, (-60, 1180), (-60, 1320), (-200, 1140), (0, 1248), angle=0)
things(2012, (-340, 1380))
things(MANCUBUS, (560, 1248), (720, 1160), (720, 1340), angle=180)
things(CACO, (840, 1180), (840, 1320), angle=180)
things(2012, (860, 1120))
things(17, (860, 1380))

# --- the lens store: the plasma rifle ----------------------------------------------------------
m.thing(440, 1700, 2004)
things(17, (440, 1460))
things(2046, (850, 1460))
things(2012, (640, 1700), (440, 1600))
things(IMP, (640, 1480), (460, 1560), (820, 1560), angle=270)
things(SOUL, (640, 1600), (420, 1720), (860, 1620), angle=270)
things(REVENANT, (640, 1710), angle=270)
m.thing(820, 1700, KNIGHT, angle=180)

# --- ambushes ------------------------------------------------------------------------------------
# GREEN, taken: the hall
ajarmap.ambush(m, 10 + GREEN, IMP, (300, 60), (470, 60), angle=90)
ajarmap.ambush(m, 10 + GREEN, SERGEANT, (120, 200), (700, 200), angle=0, after=3)
# a leaf, taken: the hall, and the darkroom's way
ajarmap.ambush(m, 10 + TEAL, DEMON, (384, 320), (340, 540), (430, 540), angle=90)
ajarmap.ambush(m, 10 + TEAL, REVENANT, (60, 100), (700, 240), angle=0, after=4)
# RED, taken: the range, behind you
ajarmap.ambush(m, 10 + RED, IMP, (-400, 880), (-400, 1000), (-250, 944), angle=0)
ajarmap.ambush(m, 10 + RED, KNIGHT, (-160, 880), angle=180, after=3)
# key 1, beyond the pit: cacodemons over it, then the range
ajarmap.ambush(m, 1, CACO, (800, 944), (900, 860), (900, 1030), angle=0)
ajarmap.ambush(m, 1, REVENANT, (300, 944), (420, 860), angle=0, after=4)
# key 2, in GREEN's cell: round you, and then the range outside
ajarmap.ambush(m, 2, SPECTRE, (-300, 1180), (-150, 1350), (-40, 1150), angle=180)
ajarmap.ambush(m, 2, KNIGHT, (-128, 980), (60, 980), angle=90, after=3)
# VIOLET, taken: the store, and BLUE's cell behind you
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (460, 1460), (820, 1460), angle=270)
ajarmap.ambush(m, 10 + VIOLET, SPECTRE, (640, 1300), (520, 1150), angle=90, after=3)
m.thing(944, 128, BARON, angle=180)                                         # before the night room

# --- more of them, and what it takes: a little over MAP12 ---------------------------------------
things(IMP, (60, 600), (700, 120), angle=270)                               # the hall
things(SERGEANT, (-300, 1000), (480, 860), angle=180)                       # the range
things(IMP, (-380, 944), (40, 1000), angle=180)
things(DEMON, (500, 1480), (780, 1480), angle=270)                          # the store
things(2049, (384, 600), (120, 40), (-660, 230), (-180, 180), (-100, 1040), (440, 1040), (40, 880))
things(17, (-420, 944), (520, 1040), (640, 1440), (860, 1700))
things(2046, (700, 500), (-640, -40), (360, 1040), (1100, 850))
things(2048, (60, 150), (700, 400), (-200, 944), (300, 900))
things(2012, (384, 300), (60, 250), (-400, 220), (-150, 1000), (540, 840), (1190, 1000), (-60, 1380), (860, 1250), (440, 1500), (984, 80))
m.thing(-330, 1112, 2013)                                                   # a soul sphere, in GREEN's cell
things(8, (256, 464))                                                       # a backpack at the edge of a bench

LEAF_A, LEAF_B = ajarmap.LEAVES[TEAL]
FACING = ((101, 102), (102, 101))
PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("hall", "dark"), ("dark", "hall"),
          ("hall", "range", "a"), ("range", "hall", "a"),                   # the steel door the target opens
          ("far", "range"),                                                 # the pit, and its steps
          ("range", "cellA", "b"), ("cellA", "range", "b"),                 # the steel doors the sensor opens
          ("range", "cellB", "b"), ("cellB", "range", "b"),
          ("hall", "night", "12"), ("night", "hall")],
    keys={"1": "far", "2": "cellA"},
    frames={101: "hall", 102: "hall", 103: "hall", 104: "dark", 105: "range", ajarmap.HOME: "night"},
    only={ajarmap.HOME: VIOLET, 104: (LEAF_A, LEAF_B)},
    doors={
        RED: dict(home="far", lean="range"),
        GREEN: dict(home="cellA", lean="hall", barred=True),
        BLUE: dict(home="cellB", lean="range", barred=True),
        VIOLET: dict(home="night", lean="cellB"),
        **ajarmap.leaves(TEAL, "hall", "hall"),
    },
    sights={
        "a": dict(through=GREEN, say="shoot the target through GREEN"),
        "b": dict(at="range", say="fire the emitter: the beam is on the sensor",
                  lines=[{RED: (r,), x: (f,), y: (104,)} for r, f in FACING for x, y in ((LEAF_A, LEAF_B), (LEAF_B, LEAF_A))]),
    },
)
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
