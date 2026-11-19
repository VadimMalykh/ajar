"""Act 2, level 1: "By Appointment" (MAP11). Its look: AJAR_INSTITUTE, below.

The way into the institute that studies the doors. One new thing, the Pair:
two leaves of one colour (TEAL) that open onto each other. Plain doors are
here beside it, and the level asks for the Pair's basic move once, the rope:
a Pair cannot take you anywhere new, but it keeps a way open to a place you
have been, for whatever you carry. The rest is a fight through the building.

Places. One place to walk about in ("hall"): the lobby (start; both TEAL
leaves and RED; two frames that face each other), the cloakroom off it, the
corridor north (a third frame), the optics lab west of it and the canteen
east (GREEN). Over the canteen's north side the gallery (RED's far side,
key 1), too high to climb, with a balcony down the canteen's east side; from
the gallery you drop into the canteen or, north, into the archive. The
archive (VIOLET; two frames) has no door: a hole from the corridor lets
empty hands through. The pump room (GREEN's far side, key 2) is west of the
corridor, and its hatch is such a hole too, with a step down into the
corridor that is too high to climb: the way in is GREEN, and whatever goes
in by GREEN in your hands comes out by GREEN. At the
corridor's end a door with locks 1 and 2: the experiment hall, and beyond it
the night room, whose brass frame takes VIOLET only.

So: GREEN to the pump room for key 2; RED to the gallery for key 1; and
VIOLET has to come out of the archive in your hands, which the hole will
not have. A leaf in the hall, its twin up by RED and down into the archive:
the archive opens onto the hall. Then the experiment hall, and the night room.

Secret: the south end of the balcony, seen from the canteen's floor.
"""
import os

import ajarmap
from ajarmap import RED, GREEN, VIOLET, TEAL, far_id
from udmf import Map

m = Map()
# The institute's look (gfx_institute.py): 1 Academy (the 1950s), 2 Thaw (the
# 1960s), 3 Post Box (a closed establishment, some years on); AJAR_INSTITUTE=0
# is the level in the plain walls and tints it was built in. None is chosen
# yet (design/map11-board.html): look 1 is worn until one is. A look changes
# textures and hangs pictures on walls; no wall, floor or thing moves, and
# rooms are not tinted in a look.
LOOK = int(os.environ.get("AJAR_INSTITUTE") or "1")
SIGNS, FACES = {}, {}                       # the names over ways and the door faces this build needs: gfx_institute.make draws them
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED
UP, TOP = 128, 256                          # the gallery's floor; every ceiling
PALE, MINT, PAPER, DIM, RUST, COLD, STEEL = 0xDCE8DC, 0xC8E0C8, 0xF0E4C8, 0xB0B8C8, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0
ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE = 3004, 9, 3001, 3002, 58
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS = 65, 69, 3003, 66, 3006, 3005, 67
SUMP = 32                                   # the pump room's floor: its hatch is a way out, not in


def T(part):
    return f"AJI{part}{LOOK}"


def dress(**parts):
    """Sector properties for the look: wall="LB" is the look's texture LB."""
    return {k: T(v) for k, v in parts.items()} if LOOK else {}


def tint(c):
    return None if LOOK else c


def box(height, top="BT", side=None, **k):  # a crate, a desk, a table: in a look, a bench of the lab unless named
    if LOOK:
        return dict(floor=height, ftex=T(top), side=T(side or {48: "B4", 64: "B6", 96: "B9"}[height]), **k)
    return dict(floor=height, ftex="AJBOARD", side="AJWOOD", **k)


def pillar(part):                           # to the ceiling: a pillar, a stack, a tank, the machine
    return dict(floor=TOP, **dress(side=part))


def over(a, b, part):
    """In a look: the wall over the opening a-b carries on as the wall `part`,
    in line with the wall beside it; and under it, where there is a step."""
    if LOOK:
        m.line(a, b, upper=T(part), lower=T(part), dontpegtop=True, dontpegbottom=True)


def _shift(a, b, out):
    """Where in its 64 a wall's texture stands at the left end of a-b, for
    someone looking `out` at it (udmf lays walls by where they are)."""
    lo, hi = sorted((a[0], b[0]) if out[0] == 0 else (a[1], b[1]))
    return lo % 64 if out in ((0, 1), (-1, 0)) else -hi % 64


def named(a, b, out, part, words, oh=96):
    """In a look: over the way a-b through the wall `part`, seen looking
    `out`, a plate with `words`. The way's head is `oh` above the floor."""
    if LOOK and words:
        w = abs(a[0] - b[0]) + abs(a[1] - b[1])
        key = (LOOK, part, words, _shift(a, b, out), w, oh)
        m.line(a, b, upper=SIGNS.setdefault(key, f"AJIS{LOOK}{len(SIGNS):02d}"), exact=True)


def _far(a, b, out, thick=16):
    return (a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick)


def opening(a, b, out, near, far, words="", color=None):
    """An open way from the room whose wall is `near` to the one whose wall
    is `far`; `words` is what the near side calls what is beyond."""
    ajarmap.opening(m, a, b, out, 0, color=tint(color))
    over(a, b, near)
    over(*_far(a, b, out), far)
    named(a, b, out, near, words)


def squeeze(a, b, out, floor, near, far, words="", oh=64):
    ajarmap.squeeze(m, a, b, out, floor)
    over(a, b, near)
    over(*_far(a, b, out), far)
    named(a, b, out, near, words, oh)


def hang(a, b, part):
    """In a look: the wall piece a-b (a multiple of 64 from a multiple of 64)
    shows the picture `part`."""
    if LOOK:
        m.cut(a, b)
        m.line(a, b, mid=T(part), exact=True)


def things(kind, *spots, angle=0):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle)


def frame(a, b, out, n, color, floor=0):
    ajarmap.recess(m, a, b, out, floor, n, far_id(RED), color=tint(color))


# --- the lobby and its cloakroom ---------------------------------------------
ajarmap.fitted(m, (0, 0, 1024, 640), [
    ((384, 352, 640, 416), box(40, "DT", "DS")),                             # the reception desk
    ((224, 160, 288, 224), pillar("PI")), ((736, 160, 800, 224), pillar("PI")),
    ((224, 416, 288, 480), pillar("PI")), ((736, 416, 800, 480), pillar("PI")),
], floor=0, ceil=TOP, light=200, color=tint(PALE), **dress(wall="LB", ftex="FL", ctex="KL"))
hang((448, 0), (576, 0), "ST")                                               # the street doors, behind the start
hang((64, 640), (320, 640), "MO")                                            # what the institute says of itself
hang((768, 640), (896, 640), "NB")                                           # the clock; visitors by appointment only
frame((0, 288), (0, 352), (-1, 0), 101, PALE)
frame((1024, 288), (1024, 352), (1, 0), 102, PALE)
ajarmap.fitted(m, (-336, 64, -16, 256), [
    ((-336, 64, -304, 256), box(48, "UT", "US")),                            # the counter
], floor=0, ceil=160, light=150, color=tint(PAPER), **dress(wall="CK", ftex="FC", ctex="KC"))
for y in (64, 128, 192):
    hang((-336, y), (-336, y + 64), "CT")                                    # coats, behind it
opening((0, 128), (0, 192), (-1, 0), "LB", "CK", "CLOAKROOM", color=PALE)

# --- the corridor ---------------------------------------------------------------
ajarmap.fitted(m, (384, 640, 640, 1664), [], floor=0, ceil=TOP, light=180, color=tint(MINT),
               **dress(wall="CO", ftex="FC", ctex="KC"))
frame((384, 704), (384, 768), (-1, 0), 103, MINT)

# --- the optics lab, west ---------------------------------------------------------
ajarmap.fitted(m, (-256, 832, 368, 1216), [
    ((-128, 896, -32, 992), box(48)), ((64, 1056, 192, 1152), box(64)), ((-224, 1120, -160, 1184), box(96)),
], floor=0, ceil=TOP, light=170, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
hang((-64, 1216), (64, 1216), "BB")                                          # a blackboard
hang((128, 832), (256, 832), "CB")                                           # cabinets of lenses
opening((384, 992), (384, 1056), (-1, 0), "CO", "LA", "OPTICS", color=MINT)
frame((-256, 1000), (-256, 1064), (-1, 0), 104, RUST)                        # a fourth frame for the hall: hands can always be emptied

TABLE = box(32, "TT", "TS")
HIGH = dress(ftex="GT", side="GF") if LOOK else dict(side="AJTRIM")          # the gallery and the balcony: their floor, their front
# --- the canteen, east; the balcony down its east side, its south end a secret
ajarmap.fitted(m, (656, 672, 1360, 1120), [
    ((800, 768, 928, 832), TABLE), ((800, 928, 928, 992), TABLE),
    ((1024, 768, 1152, 832), TABLE), ((1024, 928, 1152, 992), TABLE),
    ((1264, 672, 1360, 1120), dict(floor=UP, **HIGH)),
    ((1264, 672, 1360, 736), dict(floor=UP, special=1024, **HIGH)),
], floor=0, ceil=TOP, light=200, color=tint(PAPER), **dress(wall="CA", ftex="FN", ctex="KC"))
if LOOK:                                                                     # under the balcony: the canteen's own wall
    m.line((1264, 672), (1264, 1120), lower=T("CA"), dontpegbottom=True)
hang((896, 672), (1024, 672), "MN")                                          # the menu
opening((640, 800), (640, 864), (1, 0), "CO", "CA", "CANTEEN", color=MINT)

# --- the gallery over the canteen's north side ------------------------------------
m.sector([(656, 1120), (656, 1312), (1360, 1312), (1360, 1120)], floor=UP, ceil=TOP, light=190, color=tint(PAPER),
         **dict(HIGH, **dress(wall="CA", ctex="KC")))                         # its front is the kitchen's hatch
ajarmap.recess(m, (1360, 1184), (1360, 1248), (1, 0), UP, far_id(RED), 101, far_colour=RED, color=tint(PAPER))
over((656, 1312), (1360, 1312), "AR")                                        # the drop into the archive: the archive's wall

# --- the archive: a drop from the gallery, a hole from the corridor ----------------
ajarmap.fitted(m, (656, 1312, 1360, 1760), [
    ((784, 1472, 848, 1696), pillar("SK")), ((976, 1472, 1040, 1696), pillar("SK")), ((1168, 1472, 1232, 1696), pillar("SK")),    # the stacks
], floor=0, ceil=TOP, light=140, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
hang((832, 1760), (960, 1760), "CI")                                         # the card index
hang((1088, 1760), (1216, 1760), "CI")
squeeze((640, 1500), (640, 1548), (1, 0), 0, "CO", "AR", "ARCHIVE")
frame((1360, 1500), (1360, 1564), (1, 0), 106, DIM)
frame((976, 1760), (1040, 1760), (0, 1), 107, DIM)
frame((704, 1760), (768, 1760), (0, 1), 108, DIM)                            # three: one more than the doors that can be shut in here

# --- the pump room, west: GREEN's far side; a hatch from the corridor ---------------
ajarmap.fitted(m, (-256, 1296, 368, 1664), [
    ((-128, 1392, -32, 1488), pillar("TK")), ((96, 1392, 192, 1488), pillar("TK")), ((-16, 1552, 80, 1616), pillar("TK")),       # the tanks
], floor=SUMP, ceil=SUMP + 192, light=110, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
hang((192, 1664), (320, 1664), "GA")                                         # gauges and valves
ajarmap.recess(m, (-256, 1456), (-256, 1520), (-1, 0), SUMP, far_id(GREEN), 101, far_colour=GREEN, color=tint(COLD))
squeeze((384, 1448), (384, 1496), (-1, 0), SUMP, "CO", "PU", "PUMPS", oh=96)   # its hatch: empty hands only, and a step too high from the corridor

PLATFORM = box(64, "PT", "PS")
# --- the experiment hall, behind locks 1 and 2; the night room beyond ---------------
ajarmap.fitted(m, (-128, 1680, 624, 2320), [
    ((184, 1936, 312, 2064), pillar("MC")),                                  # the machine
    ((-128, 2192, 0, 2320), PLATFORM), ((496, 2192, 624, 2320), PLATFORM),
    ((-128, 1936, -64, 2064), PLATFORM), ((560, 1936, 624, 2064), PLATFORM),
], floor=0, ceil=TOP, light=190, color=tint(STEEL), **dress(wall="EX", ftex="FE", ctex="KE"))
hang((-128, 1728), (-128, 1856), "CP")                                       # the desk it was run from
hang((624, 1792), (624, 1856), "WS")
ajarmap.roomdoor(m, (480, 1664), (544, 1664), (0, 1), 0, keys="12", line_id=301, free_inside=True)
if LOOK:                                    # the door's two faces: the wall of each side over the leaf, its name on the corridor's
    for (a, b), out, part, words in ((((480, 1664), (544, 1664)), (0, 1), "CO", "TEST HALL"),
                                     (((480, 1680), (544, 1680)), (0, -1), "EX", "")):
        key = (LOOK, part, _shift(a, b, out), "12", words)
        m.line(a, b, upper=FACES.setdefault(key, f"AJID{LOOK}{len(FACES):02d}"))
m.sector([(184, 2320), (184, 2400), (312, 2400), (312, 2320)], ceil=160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
over((184, 2320), (312, 2320), "EX")
ajarmap.way_home(m, 88, 2400, VIOLET, only=True)

# --- doors and keys -------------------------------------------------------------------
ajarmap.pair(m, TEAL, (40, 200, 0), (984, 200, 180))
ajarmap.door(m, RED, 330, 610, angle=270)
ajarmap.door(m, GREEN, 1220, 700, angle=270)
ajarmap.door(m, VIOLET, 1330, 1720, angle=180)
ajarmap.key(m, 1, 700, 1280)
ajarmap.key(m, 2, -216, 1632)

# --- things: the lobby and the cloakroom -----------------------------------------------
m.thing(512, 80, 1, angle=90)
m.thing(512, 170, 2001)                                                     # shotgun
things(2008, (450, 170), (574, 170))
things(ZOMBIE, (160, 300), (860, 300), (120, 560), angle=270)
things(SERGEANT, (440, 460), (584, 460), angle=270)                         # behind the desk
things(IMP, (900, 560), (512, 590), angle=270)
m.thing(-200, 220, 2002)                                                    # chaingun
m.thing(-270, 150, 8)                                                       # backpack
things(2048, (-120, 100))
things(SERGEANT, (-240, 100), (-100, 220), angle=0)
things(2011, (60, 60), (964, 60))

# --- the corridor ------------------------------------------------------------------------
things(IMP, (450, 900), (570, 1150), (450, 1330), angle=270)
things(CHAINGUNNER, (450, 1610), (574, 1610), angle=270)
things(2049, (600, 680), (600, 1400))
things(2012, (420, 1240))
things(2046, (420, 1560))

# --- the optics lab: the super shotgun on a crate -------------------------------------------
m.thing(128, 1104, 82)
things(DEMON, (-180, 1040), (-40, 1090), (260, 900), (300, 1160), angle=0)
things(IMP, (-80, 944), (-192, 1152), (290, 1010), angle=0)
m.thing(0, 870, REVENANT, angle=0)
m.thing(-220, 870, 2018)                                                    # green armour
things(2049, (-200, 960), (220, 1180))
things(2012, (330, 860))

# --- the canteen: GREEN, and the berserk pack for where it leads ------------------------------
m.thing(1180, 720, 2023)
things(IMP, (760, 720), (980, 880), (1200, 880), (720, 1060), (980, 1060), angle=180)
things(SERGEANT, (960, 720), (1100, 880), (760, 900), angle=180)
things(KNIGHT, (1200, 1040), (880, 880), angle=180)
things(2048, (700, 700))
things(2049, (700, 1090))
things(2012, (1230, 800))
m.thing(1312, 704, 2013)                                                    # the balcony's end: a soul sphere
m.thing(1312, 900, IMP, angle=180)

# --- the gallery: the rocket launcher over the canteen -------------------------------------------
m.thing(1100, 1220, 2003)
things(2046, (1040, 1270))
things(IMP, (780, 1220), (1000, 1160), angle=270)
m.thing(900, 1270, CHAINGUNNER, angle=270)
things(2012, (1300, 1290))

# --- the pump room: dark, and the plasma rifle ----------------------------------------------------
m.thing(40, 1340, 2004)
things(17, (220, 1630), (330, 1630))
things(2049, (-220, 1400))
things(SPECTRE, (-180, 1340), (-100, 1570), (40, 1500), (260, 1340), (260, 1620), angle=0)
things(DEMON, (150, 1570), (-60, 1340), angle=0)
m.thing(300, 1472, KNIGHT, angle=180)
things(2012, (-220, 1320), (330, 1320))

# --- the archive ----------------------------------------------------------------------------------
things(IMP, (720, 1440), (912, 1560), (1104, 1600), (1290, 1440), angle=270)
things(KNIGHT, (912, 1724), (1104, 1420), angle=270)
things(SOUL, (840, 1730), (1290, 1640), (1104, 1730), angle=270)
things(17, (1300, 1340))
things(2049, (700, 1340), (1300, 1730))
things(2046, (900, 1340))
things(2012, (1000, 1440), (720, 1620))

# --- the experiment hall ----------------------------------------------------------------------------
m.thing(512, 1740, 2019)                                                    # blue armour at the door
things(2046, (430, 1720), (590, 1720))
things(17, (440, 1790), (-90, 1790))
things(2049, (590, 1850))
things(2012, (590, 1790), (-90, 1720), (-90, 2130), (580, 2130))
things(MANCUBUS, (20, 2000), (480, 2000), angle=270)
things(REVENANT, (-64, 2256), (560, 2256), angle=270)                       # on the far platforms
things(IMP, (-96, 2000), (592, 2000), (20, 1780), (120, 1900), (376, 1900), angle=270)
things(KNIGHT, (120, 2200), (376, 2200), (248, 1820), angle=270)
things(CACO, (60, 2110), (440, 2110), angle=270)
m.thing(248, 2270, BARON, angle=270)                                        # before the way to the night room

# --- ambushes ------------------------------------------------------------------------------------------
# a leaf of the Pair, taken: the lobby
ajarmap.ambush(m, 10 + TEAL, SERGEANT, (330, 110), (700, 110), angle=90)
ajarmap.ambush(m, 10 + TEAL, IMP, (160, 470), (860, 470), angle=270, after=3)
# key 1, on the gallery: cacodemons up from the canteen, then demons along the gallery
ajarmap.ambush(m, 1, CACO, (980, 800), (1200, 960), angle=90)
ajarmap.ambush(m, 1, DEMON, (840, 1180), (1000, 1250), (1240, 1150), angle=180, after=3)
# key 2, in the pump room: revenants by its door, then the corridor outside
ajarmap.ambush(m, 2, REVENANT, (300, 1380), (300, 1580), angle=180)
ajarmap.ambush(m, 2, IMP, (512, 1300), (512, 1560), angle=270, after=3)
# VIOLET, taken: the archive, round you, and then between the stacks
ajarmap.ambush(m, 10 + VIOLET, SPECTRE, (720, 1380), (1000, 1380), (1280, 1380), angle=90)
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (760, 1724), (1200, 1724), angle=0, after=4)

PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("gallery", "hall"), ("gallery", "archive"),
          ("hall", "archive", "", "squeeze"), ("archive", "hall", "", "squeeze"),     # the hole
          ("pump", "hall", "", "squeeze"),                                           # the hatch: out only
          ("hall", "night", "12"), ("night", "hall")],
    keys={"1": "gallery", "2": "pump"},
    frames={101: "hall", 102: "hall", 103: "hall", 104: "hall", 106: "archive", 107: "archive", 108: "archive", ajarmap.HOME: "night"},
    only={ajarmap.HOME: VIOLET},
    doors={
        RED: dict(home="gallery", lean="hall"),
        GREEN: dict(home="pump", lean="hall"),
        VIOLET: dict(home="night", lean="archive"),
        **ajarmap.leaves(TEAL, "hall", "hall"),
    },
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
