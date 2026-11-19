"""Act 2, level 2: "Going Up" (MAP12). It wears MAP11's look (AJAR_INSTITUTE).

The institute's goods wing: three floors round one lift shaft, and no stairs.
One new thing, the moving room (ajarmap.lift_button, src/zscript/lift.zs):
a door that opens onto the lift car opens onto whichever floor the car is at.

Places. The loading hall (ground; the start; RED; one frame), the car (one
frame, and RED's far side), the workshops (first floor, west of the shaft;
GREEN, a TEAL leaf; no frame), the winding room (top floor, north; key 1;
no frame), and beyond its door with locks 1 and 2 the night room, whose
brass frame takes VIOLET only. The car's own panel is torn out: it is sent
from the landings (the hall and the workshops: ground and first), and from
the dispatcher's booth, which alone can send it to the top. The booth is
walled up behind glass on the first floor; the other TEAL leaf hangs in its
frame, which takes a TEAL leaf and nothing else. The battery room (GREEN's
far side; key 2) has no way in but GREEN. The store (VIOLET; two frames) is
sunk off the hall behind lock 1: a drop in, and a hole and steps out that
no door fits. From the top a gap drops to the workshops, and from the
workshops one to the hall: the way up is the lift.

So: RED in the hall's frame, send the car up, and through RED: the first
floor. The leaf in the car's frame: the booth opens onto the car, wherever
it has just been sent. Key 1 at the top, key 2 by GREEN, VIOLET out of the
store by RED hung down there (it opens onto the car), and from the car by
the leaf to the booth, the top button, and back: the top, with VIOLET.

Secret: none yet.
"""
import ajarmap
import map_institute1 as I1
from ajarmap import RED, GREEN, VIOLET, TEAL, far_id
from map_institute1 import T, dress, tint, over, named, hang, things, frame, LOOK, FACES
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS
from udmf import Map, rect

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end). Names over ways and
# locked doors' faces go into MAP11's SIGNS and FACES, which gfx.py draws.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED
Z1, Z2 = 192, 384                           # the first floor, the top
H = 256                                     # every room's height but those named
PALE, RUST, COLD, STEEL, DIM, PAPER = 0xDCE8DC, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8, 0xF0E4C8
B0, B1, B2 = 711, 713, 715                  # thing ids of the buttons: the hall's two, the workshops', the booth's three


def box(base, height, top="BT", side=None, **k):
    return dict(I1.box(height, top, side, **k), floor=base + height)


def solid(base, part, height=H):            # to the ceiling: a pillar, a stack, a tank, the winding engine
    return dict(floor=base + height, **dress(side=part))


def way_in(x1, y1, x2, y2, floor):
    """A landing: at any other stop of the car it is a wall."""
    m.sector(rect(x1, y1, x2, y2), floor=floor, ceil=floor + 112, light=176, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")


def button(a, b, n, tid, at):
    ajarmap.lift_button(m, a, b, (0, Z1, Z2)[n], tid, at, tex=f"AJLB{n}", foot=True)


def locked(a, b, out, floor, keys, line_id, near, far, words, **k):
    """A locked room door between the rooms whose walls are `near` and `far`."""
    ajarmap.roomdoor(m, a, b, out, floor, keys=keys, line_id=line_id, **k)
    if LOOK:
        c, d = I1._far(a, b, out)
        for (p, q), o, part, s in (((a, b), out, near, words), ((c, d), (-out[0], -out[1]), far, "")):
            key = (LOOK, part, I1._shift(p, q, o), keys, s)
            m.line(p, q, upper=FACES.setdefault(key, f"AJID{LOOK}{len(FACES):02d}"))


# --- the car and its three landings --------------------------------------------
m.sector(rect(-96, -96, 96, 96), ceil=128, light=200, color=tint(PAPER), id=ajarmap.LIFT,
         **dress(wall="EV", ftex="FE", ctex="KE"))
ajarmap.recess(m, (96, -80), (96, -16), (1, 0), 0, 110, far_id(RED), color=tint(PAPER), tag=ajarmap.LIFT)
ajarmap.recess(m, (96, 16), (96, 80), (1, 0), 0, far_id(RED), 101, far_colour=RED, color=tint(PAPER), tag=ajarmap.LIFT)
m.cut((48, -96), (80, -96))
m.line((48, -96), (80, -96), mid="AJLBX", exact=True, dontpegbottom=True)        # its own panel: torn out
way_in(-48, -128, 48, -96, 0)
way_in(-128, -48, -96, 48, Z1)
way_in(-48, 96, 48, 128, Z2)

# --- the loading hall (ground) ----------------------------------------------------
ajarmap.fitted(m, (-448, -832, 448, -128), [
    ((-336, -624, -208, -496), box(0, 64)), ((192, -656, 320, -528), box(0, 96)),
    ((208, -400, 336, -336), box(0, 48)), ((-304, -336, -240, -272), box(0, 48)),
], floor=0, ceil=H, light=190, color=tint(STEEL), **dress(wall="EX", ftex="FE", ctex="KE"))
over((-48, -128), (48, -128), "EX")
named((-48, -128), (48, -128), (0, 1), "EX", "LIFT", oh=112)
button((-112, -128), (-80, -128), 0, B0, (-96, -176))
button((80, -128), (112, -128), 1, B0 + 1, (96, -176))
frame((-448, -512), (-448, -448), (-1, 0), 101, STEEL)
hang((-448, -768), (-448, -704), "WS")
hang((448, -768), (448, -704), "WS")
hang((-64, -832), (64, -832), "CP")

# --- the store, sunk off the hall behind lock 1: a drop in, a hole and steps out ----
SUNK = -64
ajarmap.fitted(m, (464, -704, 896, -272), [
    ((464, -544, 528, -416), dict(floor=0)),                                 # the ledge inside the door
    ((656, -560, 720, -400), solid(SUNK, "SK")),                             # a stack
], floor=SUNK, ceil=SUNK + H, light=150, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
locked((448, -512), (448, -448), (1, 0), 0, "1", 302, "EX", "AR", "STORE")
frame((896, -640), (896, -576), (1, 0), 107, DIM, SUNK)
frame((896, -432), (896, -368), (1, 0), 109, DIM, SUNK)                      # two: hands can be emptied down here
hang((704, -704), (832, -704), "CI")
I1.squeeze((560, -272), (608, -272), (0, 1), SUNK, "AR", "AR")
ajarmap.stairs(m, (560, -256), (608, -256), (0, 1), SUNK, -SUNK, steps=3, depth=16, ceil=128, light=140,
               **dress(wall="AR", ftex="FR", ctex="KA"))
m.sector(rect(464, -208, 608, -144), ceil=128, light=150, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
ajarmap.opening(m, (448, -208), (448, -144), (1, 0), 0, color=tint(STEEL))
over((448, -208), (448, -144), "EX")

# --- the workshops (first floor, west of the shaft) ------------------------------------
ajarmap.fitted(m, (-1024, -96, -128, 608), [
    ((-800, 64, -672, 192), box(Z1, 48)), ((-480, 288, -352, 416), box(Z1, 64)),
    ((-896, 416, -832, 480), box(Z1, 96)), ((-416, 0, -288, 64), box(Z1, 48)),
], floor=Z1, ceil=Z1 + H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
over((-128, -48), (-128, 48), "LA")
named((-128, -48), (-128, 48), (1, 0), "LA", "LIFT", oh=112)
button((-128, 64), (-128, 96), 1, B1, (-176, 80))
button((-128, 112), (-128, 144), 0, B1 + 1, (-176, 128))
# the gap: from the workshops down into the hall, and not back
m.sector(rect(-400, -128, -272, -96), floor=Z1, ceil=Z1 + 112, light=176, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
over((-400, -96), (-272, -96), "LA")
over((-400, -128), (-272, -128), "EX")
hang((-640, -96), (-512, -96), "BB")
hang((-320, 608), (-192, 608), "CB")

# --- the dispatcher's booth: walled up, behind glass; its frame takes a TEAL leaf only --
m.sector(rect(-1216, 160, -1040, 352), floor=Z1, ceil=Z1 + 160, light=180, color=tint(PAPER),
         **dress(wall="CK", ftex="FC", ctex="KC"))
m.sector(rect(-1040, 192, -1024, 320), floor=Z1 + 40, ceil=Z1 + 104, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
m.line((-1024, 192), (-1024, 320), mid="AJWIN", midboth=True, blocking=True)
over((-1024, 192), (-1024, 320), "LA")
over((-1040, 192), (-1040, 320), "CK")
ajarmap.recess(m, (-1216, 224), (-1216, 288), (-1, 0), Z1, 106, far_id(RED), color=tint(PAPER), home=TEAL, only=3)
button((-1200, 352), (-1168, 352), 0, B2, (-1184, 312))
button((-1152, 352), (-1120, 352), 1, B2 + 1, (-1136, 312))
button((-1104, 352), (-1072, 352), 2, B2 + 2, (-1088, 312))

# --- the battery room: GREEN's far side, and no other way in ------------------------------
ajarmap.fitted(m, (-1600, -640, -1216, -256), [
    ((-1504, -544, -1440, -480), solid(0, "TK", 192)), ((-1376, -416, -1312, -352), solid(0, "TK", 192)),
], floor=0, ceil=192, light=120, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
ajarmap.recess(m, (-1216, -480), (-1216, -416), (1, 0), 0, far_id(GREEN), 101, far_colour=GREEN, color=tint(COLD))
hang((-1472, -256), (-1344, -256), "GA")

# --- the winding room (top floor, north of the shaft) --------------------------------------
PLATFORM = box(Z2, 64, "PT", "PS")
ajarmap.fitted(m, (-112, 128, 912, 896), [
    ((336, 448, 464, 576), solid(Z2, "MC")),                                 # the winding engine
    ((112, 320, 176, 384), solid(Z2, "PI")), ((624, 320, 688, 384), solid(Z2, "PI")),
    ((112, 640, 176, 704), solid(Z2, "PI")), ((624, 640, 688, 704), solid(Z2, "PI")),
    ((784, 128, 912, 256), PLATFORM), ((784, 768, 912, 896), PLATFORM), ((-112, 768, 16, 896), PLATFORM),
], floor=Z2, ceil=Z2 + H, light=200, color=tint(PALE), **dress(wall="LB", ftex="FL", ctex="KL"))
over((-48, 128), (48, 128), "LB")
named((-48, 128), (48, 128), (0, -1), "LB", "LIFT", oh=112)
hang((912, 448), (912, 576), "NB")
# the gap: from the top down into the workshops, and not back
m.sector(rect(-128, 400, -112, 528), floor=Z2, ceil=Z2 + 112, light=176, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
over((-112, 400), (-112, 528), "LB")
over((-128, 400), (-128, 528), "LA")
# the door with locks 1 and 2, and beyond it the night room
m.sector(rect(336, 912, 464, 992), floor=Z2, ceil=Z2 + 160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
locked((368, 896), (432, 896), (0, 1), Z2, "12", 301, "LB", "EV", "WAY OUT", free_inside=True)
ajarmap.way_home(m, 240, 992, VIOLET, only=True, floor=Z2)

# --- doors and keys ---------------------------------------------------------------------------
ajarmap.door(m, RED, -400, -300, angle=0)
ajarmap.door(m, GREEN, -200, -50, angle=180)
ajarmap.door(m, VIOLET, 850, -500, angle=180)
ajarmap.pair(m, TEAL, (-1190, 256, 0, 106), (-980, 560, 0))
ajarmap.key(m, 1, 744, 864)                                                  # at the foot of the far platform of the winding room
ajarmap.key(m, 2, -1560, -300)

# --- things: the loading hall -------------------------------------------------------------------
m.thing(0, -776, 1, angle=90)
m.thing(0, -700, 2001)                                                      # shotgun
things(2008, (-60, -700), (60, -700))
m.thing(380, -780, 2002)                                                    # chaingun
things(2048, (400, -700))
things(ZOMBIE, (-120, -420), (120, -420), (-380, -180), angle=270)
things(SERGEANT, (-272, -560), (256, -592), (380, -200), angle=270)         # two of them on crates
things(IMP, (0, -240), (-272, -304), (272, -368), (-400, -700), angle=270)
things(DEMON, (-100, -180), (100, -180), angle=270)
m.thing(390, -480, CHAINGUNNER, angle=180)
things(2011, (-400, -780), (-340, -780))
things(2012, (420, -160))
things(2049, (-420, -160))

# --- the workshops: the super shotgun by a bench (the bench is too tall to take it from) -----------
m.thing(-416, 260, 82)
things(2049, (-960, -40), (-180, 560))
things(2048, (-960, 20))
m.thing(-300, -50, 2018)                                                    # green armour
things(2012, (-180, 400), (-700, 560))
things(IMP, (-736, 128), (-864, 448), (-352, 32), (-600, 300), (-900, 100), angle=0)
things(DEMON, (-560, 80), (-560, 480), (-260, 250), angle=0)
things(SERGEANT, (-700, -40), (-240, 480), angle=0)
things(CHAINGUNNER, (-940, 300), (-420, 520), angle=0)
things(KNIGHT, (-760, 400), (-300, 180), angle=0)
m.thing(-900, -40, REVENANT, angle=0)

# --- the battery room: dark, and the plasma rifle -----------------------------------------------------
m.thing(-1400, -300, 2004)
things(17, (-1560, -600), (-1260, -600))
things(SPECTRE, (-1540, -400), (-1400, -580), (-1290, -300), angle=0)
m.thing(-1480, -340, KNIGHT, angle=0)
things(2012, (-1560, -480))

# --- the store ----------------------------------------------------------------------------------------
things(IMP, (600, -640), (780, -330), angle=180)
things(SOUL, (760, -620), (600, -340), angle=180)
m.thing(800, -480, KNIGHT, angle=180)
things(2049, (500, -650))
things(2046, (500, -320))
things(2012, (860, -310))

# --- the winding room ------------------------------------------------------------------------------------
m.thing(0, 220, 2019)                                                       # blue armour by the lift
m.thing(-60, 300, 2003)                                                     # rocket launcher
things(2046, (60, 300), (748, 148))
things(17, (240, 180), (-60, 600))
things(2049, (560, 180))
things(2012, (-60, 180), (240, 840), (720, 500), (500, 840))
m.thing(748, 192, 2013)                                                     # a soul sphere at the foot of a platform
things(MANCUBUS, (250, 512), (560, 512), angle=270)
things(REVENANT, (-48, 832), (840, 816), angle=270)                         # on the far platforms
things(IMP, (60, 420), (400, 320), (740, 420), (60, 700), (740, 700), (400, 700), angle=270)
things(KNIGHT, (240, 720), (560, 720), (400, 380), angle=270)
things(CACO, (240, 320), (560, 320), angle=270)
things(CHAINGUNNER, (840, 500), (-60, 500), angle=270)
m.thing(400, 800, BARON, angle=270)                                         # before the way out

# --- more of them, and what it takes: the level is a little bigger than MAP11 ---------------------------------
things(IMP, (-60, -560), (60, -560), angle=270)                             # the hall
things(DEMON, (0, -400), angle=270)
things(SERGEANT, (-400, -600), angle=0)
m.thing(-272, -272, 2012)
m.thing(-256, -320, 8)                                                      # a backpack on the low crate under the gap from the workshops
things(2049, (420, -800))
things(IMP, (-180, 300), (-960, 480), angle=0)                              # the workshops
things(SPECTRE, (-640, -40), (-500, 560), angle=0)
things(DEMON, (-860, 200), angle=0)
things(2048, (-180, -60))
things(2049, (-600, 180))
things(2046, (-960, 200))
things(2012, (-960, 120), (-420, 180))
m.thing(-700, 80, 2023)                                                    # berserk, at the edge of a bench
things(DEMON, (-1300, -560), (-1420, -440), angle=0)               # the battery room
things(2047, (-1260, -300), (-1260, -340))
things(IMP, (500, -480), angle=180)                                         # the store
things(DEMON, (600, -560), (780, -420), angle=180)
things(2012, (500, -600))
things(2049, (860, -660))
things(IMP, (-60, 640), (840, 320), (200, 610), (610, 610), angle=270)      # the winding room
things(KNIGHT, (400, 240), angle=270)
things(REVENANT, (240, 440), (560, 440), angle=270)
things(DEMON, (120, 220), (680, 220), angle=270)
m.thing(400, 640, CACO, angle=270)
things(2046, (-60, 240), (700, 840))
things(17, (700, 180))
things(2049, (100, 840), (840, 640))
things(2012, (560, 840), (-60, 420))
things(2049, (-420, -800), (300, 180))
things(17, (748, 236))

# --- ambushes ----------------------------------------------------------------------------------------------
# RED, taken: the hall
ajarmap.ambush(m, 10 + RED, IMP, (-200, -760), (200, -760), angle=90)
ajarmap.ambush(m, 10 + RED, SERGEANT, (-380, -420), (380, -420), angle=0, after=3)
# the leaf, taken: the workshops, round you
ajarmap.ambush(m, 10 + TEAL, SPECTRE, (-900, 380), (-760, 540), (-860, 250), angle=0)
ajarmap.ambush(m, 10 + TEAL, REVENANT, (-200, 100), (-200, 320), angle=180, after=4)
# key 1, at the top: cacodemons over the engine, then knights at the lift
ajarmap.ambush(m, 1, CACO, (250, 250), (560, 250), (400, 650), angle=90)
ajarmap.ambush(m, 1, KNIGHT, (-40, 400), (60, 220), angle=90, after=4)
# key 2, in the battery room: the car arrives with company, and they come by whatever door opens onto it
ajarmap.ambush(m, 2, DEMON, (-44, -44), (44, 44), angle=180)
ajarmap.ambush(m, 2, IMP, (-1300, -480), (-1560, -540), angle=0, after=2)
# VIOLET, taken: the store
ajarmap.ambush(m, 10 + VIOLET, SPECTRE, (600, -480), (780, -640), angle=0)
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (780, -320), angle=180, after=3)

LEAF_A, LEAF_B = ajarmap.LEAVES[TEAL]
PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("top", "first"), ("first", "hall"),                              # the gaps
          ("hall", "store", "1"),                                           # the store's door, and the drop inside it
          ("store", "hall", "", "squeeze"), ("hall", "store", "", "squeeze"),   # the hole and the steps
          ("top", "night", "12"), ("night", "top")],
    keys={"1": "top", "2": "battery"},
    frames={101: "hall", 110: "car", 106: "booth", 107: "store", 109: "store", ajarmap.HOME: "night"},
    only={ajarmap.HOME: VIOLET, 106: (LEAF_A, LEAF_B)},
    doors={
        RED: dict(home="car", lean="hall"),
        GREEN: dict(home="battery", lean="first"),
        VIOLET: dict(home="night", lean="store"),
        **ajarmap.leaves(TEAL, 106, "first"),
    },
    lift=dict(car="car", floors=["hall", "first", "top"],
              buttons={"hall": (0, 1), "first": (0, 1), "booth": (0, 1, 2)}),
)
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
