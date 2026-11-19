"""Act 2, level 4: "On the Level" (MAP14). It wears MAP11's look (AJAR_INSTITUTE).

The institute's staff wing: three floors round one lift, and no stairs. One
new thing (Vadim, 2026-11-19): the way out is a chain (ajarmap.way_through,
MAP09) with one of its two brass frames in the lift car and the other on
the first floor, across the landing from it. The two face each other only
while the car stands at the first floor, and only then is the loop closed
(AjarHandler.BrassLevel; in a PUZZLE graph `home_chain=dict(level=1)`).

Places. The canteen (ground; the start; RED; frame 101) and its kitchen.
The car: the brass frame in its east wall, RED's far side beside it, its
own panel torn out. Accounts (first floor, west of the shaft; GREEN): the
other brass frame in its west wall, in line with the landing; behind lock
1 the cashier's office (BLUE). The director's floor (top, north; key 1),
and behind lock 2 the safe room (VIOLET). The cold store (GREEN's far side;
key 2) has no way in but GREEN. The line (the far sides of BLUE and VIOLET)
is the night room. Gaps drop from the top to accounts and from accounts to
the canteen.

The buttons: the canteen sends the car to the ground and to the top; the
top sends it to the first floor; accounts has none. So the car comes to
the first floor only when sent from the top, and whoever sent it gets
there by the gap.

So: RED in the canteen's frame and the car sent up: the top (key 1). The
car sent to the first floor, and down the gap: GREEN in the brass frame
there (it is a frame like any other) for key 2. VIOLET out of the safe
room and into the car's brass frame by RED; BLUE out of the cashier's
office and swapped in for GREEN. With the car at the first floor the two
face each other: the way out.

Secret: none yet.
"""
import ajarmap
import map_institute1 as I1
from ajarmap import RED, GREEN, BLUE, VIOLET, far_id, HOME, HOME2
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
Z1, Z2 = 192, 384                           # the first floor, the top
H = 256                                     # every room's height but those named
PALE, RUST, COLD, STEEL, DIM, PAPER = 0xDCE8DC, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8, 0xF0E4C8
B0, B1 = 711, 713                           # thing ids of the buttons: the canteen's two, the top's one
BRASS = ("AJXA", "AJXAF")


def box(base, height, top="BT", side=None, **k):
    return dict(I1.box(height, top, side, **k), floor=base + height)


def solid(base, part, height=H):            # to the ceiling: a pillar, a stack, a tank
    return dict(floor=base + height, **dress(side=part))


def table(base=0):                          # a canteen table (MAP11's, 32 high)
    return dict(floor=base + 32, ftex=T("TT"), side=T("TS")) if LOOK else box(base, 48)


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


# --- the car and its three landings ---------------------------------------------------
# 192 by 256. The brass frame is in the middle of its east wall and looks west,
# out of the first floor's landing; RED's far side is beside it.
m.sector(rect(-96, -128, 96, 128), ceil=128, light=200, color=tint(PAPER), id=ajarmap.LIFT,
         **dress(wall="EV", ftex="FE", ctex="KE"))
ajarmap.recess(m, (96, -32), (96, 32), (1, 0), 0, HOME, far_id(BLUE), trim=BRASS, home=far_id(BLUE),
               chain=(far_id(VIOLET), HOME2), tag=ajarmap.LIFT)
ajarmap.recess(m, (96, 48), (96, 112), (1, 0), 0, far_id(RED), 101, far_colour=RED, color=tint(PAPER), tag=ajarmap.LIFT)
m.cut((48, -128), (80, -128))
m.line((48, -128), (80, -128), mid="AJLBX", exact=True, dontpegbottom=True)      # its own panel: torn out
way_in(-48, -160, 48, -128, 0)
way_in(-128, -48, -96, 48, Z1)
way_in(-48, 128, 48, 160, Z2)

# --- the canteen (ground) -------------------------------------------------------------
ajarmap.fitted(m, (-448, -896, 448, -160), [
    ((-336, -720, -208, -592), table()), ((208, -720, 336, -592), table()),
    ((-336, -464, -208, -400), table()), ((208, -464, 336, -400), table()),
], floor=0, ceil=H, light=190, color=tint(STEEL), **dress(wall="EX", ftex="FE", ctex="KE"))
over((-48, -160), (48, -160), "EX")
named((-48, -160), (48, -160), (0, 1), "EX", "LIFT", oh=112)
button((-112, -160), (-80, -160), 0, B0, (-96, -208))
button((80, -160), (112, -160), 2, B0 + 1, (96, -208))
frame((-448, -576), (-448, -512), (-1, 0), 101, STEEL)
hang((-448, -832), (-448, -768), "WS")
hang((-64, -896), (64, -896), "CP")
hang((448, -384), (448, -256), "HT")                                         # the kitchen's hatch, shut; the menu

# --- the kitchen, east of the canteen ---------------------------------------------------
ajarmap.fitted(m, (464, -800, 848, -288), [
    ((592, -640, 720, -448), box(0, 48, "RT", "RS")),                        # the ranges
], floor=0, ceil=H, light=160, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
I1.opening((448, -576), (448, -512), (1, 0), "EX", "AR", "KITCHEN")
hang((656, -800), (784, -800), "PN")                                         # pans on a rail

# --- accounts (first floor, west of the shaft) --------------------------------------------
# Nothing stands between the landing and the brass frame across the room from it.
ajarmap.fitted(m, (-896, -96, -128, 608), [
    ((-704, 128, -576, 256), box(Z1, 40, "AT", "DS")), ((-416, 128, -288, 256), box(Z1, 40, "AT", "DS")),
    ((-704, 384, -576, 512), box(Z1, 40, "AT", "DS")), ((-416, 384, -288, 512), box(Z1, 40, "AT", "DS")),
], floor=Z1, ceil=Z1 + H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
over((-128, -48), (-128, 48), "LA")
named((-128, -48), (-128, 48), (1, 0), "LA", "LIFT", oh=112)
ajarmap.recess(m, (-896, -32), (-896, 32), (-1, 0), Z1, HOME2, far_id(BLUE), trim=BRASS, home=far_id(BLUE),
               chain=(far_id(VIOLET), HOME))
# the gap: from accounts down into the canteen, and not back
m.sector(rect(-400, -160, -272, -96), floor=Z1, ceil=Z1 + 112, light=176, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
over((-400, -96), (-272, -96), "LA")
over((-400, -160), (-272, -160), "EX")
hang((-768, 608), (-640, 608), "PF")                                         # the throat between a door and its far side
hang((-320, 608), (-192, 608), "FG")                                         # filing cabinets
# the cashier's office, behind lock 1
m.sector(rect(-704, 624, -320, 880), floor=Z1, ceil=Z1 + 160, light=170, color=tint(PAPER),
         **dress(wall="CK", ftex="FC", ctex="KC"))
locked((-544, 608), (-480, 608), (0, 1), Z1, "1", 302, "LA", "CK", "CASHIER", free_inside=True)
hang((-576, 880), (-448, 880), "CW")                                         # the cashier's window

# --- the cold store: GREEN's far side, and no other way in ----------------------------------
ajarmap.fitted(m, (-1600, -640, -1216, -256), [
    ((-1504, -544, -1440, -480), solid(0, "TK", 192)), ((-1376, -416, -1312, -352), solid(0, "TK", 192)),
], floor=0, ceil=192, light=120, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
ajarmap.recess(m, (-1216, -480), (-1216, -416), (1, 0), 0, far_id(GREEN), 101, far_colour=GREEN, color=tint(COLD))
hang((-1472, -256), (-1344, -256), "GA")

# --- the director's floor (top, north of the shaft) -------------------------------------------
ajarmap.fitted(m, (-112, 160, 912, 928), [
    ((112, 352, 176, 416), solid(Z2, "PI")), ((624, 352, 688, 416), solid(Z2, "PI")),
    ((112, 672, 176, 736), solid(Z2, "PI")), ((624, 672, 688, 736), solid(Z2, "PI")),
    ((336, 480, 464, 608), box(Z2, 40, "DT", "DS")),                         # the director's desk
    ((784, 160, 912, 288), box(Z2, 48, "UT", "US")), ((-112, 800, 16, 928), box(Z2, 48, "UT", "US")),
], floor=Z2, ceil=Z2 + H, light=200, color=tint(PALE), **dress(wall="LB", ftex="FL", ctex="KL"))
over((-48, 160), (48, 160), "LB")
named((-48, 160), (48, 160), (0, -1), "LB", "LIFT", oh=112)
button((80, 160), (112, 160), 1, B1, (96, 208))
hang((912, 480), (912, 608), "NB")
hang((480, 928), (608, 928), "PR")                                           # where the portrait hung
hang((192, 928), (320, 928), "BC")                                           # a bookcase
# the gap: from the top down into accounts, and not back
m.sector(rect(-128, 400, -112, 528), floor=Z2, ceil=Z2 + 112, light=176, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
over((-112, 400), (-112, 528), "LB")
over((-128, 400), (-128, 528), "LA")
# the safe room, behind lock 2
m.sector(rect(240, 944, 560, 1200), floor=Z2, ceil=Z2 + 160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
locked((368, 928), (432, 928), (0, 1), Z2, "2", 301, "LB", "EV", "SAFE", free_inside=True)
hang((336, 1200), (464, 1200), "SF")                                         # the safe's door

# --- the line: the night room, the far sides of BLUE and VIOLET at its two ends ------------------
ajarmap.way_through(m, 1280, -640, BLUE, VIOLET)

# --- doors and keys ----------------------------------------------------------------------------
ajarmap.door(m, RED, -400, -330, angle=0)
ajarmap.door(m, GREEN, -200, 300, angle=180)
ajarmap.door(m, BLUE, -380, 820, angle=180)
ajarmap.door(m, VIOLET, 500, 1140, angle=180)
ajarmap.key(m, 1, 848, 860)
ajarmap.key(m, 2, -1560, -300)

# --- things: the canteen -------------------------------------------------------------------------
m.thing(0, -840, 1, angle=90)
m.thing(0, -760, 2001)                                                      # shotgun
things(2008, (-60, -760), (60, -760))
m.thing(380, -840, 2002)                                                    # chaingun
things(2048, (400, -760), (-400, -700))
things(8, (-1560, -290))                                                    # a backpack in the cold store: got by GREEN only
things(ZOMBIE, (-120, -480), (120, -480), (-380, -220), (380, -640), angle=270)
things(SERGEANT, (-272, -540), (272, -540), (380, -230), (-120, -300), angle=270)   # by the tables, not on them: they could not get down
things(IMP, (0, -280), (-272, -340), (272, -330), (-400, -780), (120, -620), (-120, -620), angle=270)
things(DEMON, (-100, -220), (100, -220), (0, -420), angle=270)
m.thing(400, -420, CHAINGUNNER, angle=180)
things(2011, (-400, -840), (-340, -840))
things(2012, (420, -200), (-420, -200))
things(2049, (-420, -640), (420, -860), (-60, -880), (60, -880))
things(2048, (-420, -860), (420, -300))

# --- the kitchen: the super shotgun -------------------------------------------------------------------
m.thing(800, -340, 82)
things(IMP, (540, -700), (780, -700), (540, -360), angle=180)
things(SPECTRE, (800, -540), (656, -380), angle=180)
m.thing(656, -720, KNIGHT, angle=180)
things(2049, (500, -760), (810, -760))
things(2012, (500, -320), (810, -420))
m.thing(520, -440, 2018)                                                    # green armour

# --- accounts ---------------------------------------------------------------------------------------
things(IMP, (-640, 320), (-352, 320), (-800, 200), (-240, 80), (-520, 560), (-800, 520), angle=0)
things(DEMON, (-520, 100), (-520, 440), (-200, 420), angle=0)
things(SERGEANT, (-540, 200), (-250, 490), (-800, 80), angle=0)
things(CHAINGUNNER, (-840, 320), (-200, 560), angle=0)
things(KNIGHT, (-760, 0), (-500, 300), angle=0)
m.thing(-840, 560, REVENANT, angle=0)
things(SPECTRE, (-640, -40), (-360, -40), angle=0)
m.thing(-700, 140, 2023)                                                    # berserk, at the edge of a desk
things(2049, (-860, -60), (-180, 580), (-560, 20), (-180, 300), (-860, 500))
things(2048, (-860, 420), (-180, -60))
things(2046, (-860, 200))
things(2012, (-180, 180), (-700, 570), (-860, 120), (-420, 300))

# --- the cashier's office: the rocket launcher ----------------------------------------------------------
m.thing(-660, 840, 2003)
things(2046, (-660, 780), (-600, 840))
things(REVENANT, (-640, 700), (-420, 700), angle=270)
m.thing(-512, 800, BARON, angle=270)
things(2012, (-360, 660))

# --- the cold store: dark, and the plasma rifle ------------------------------------------------------------
m.thing(-1400, -300, 2004)
things(17, (-1560, -600), (-1260, -600))
things(SPECTRE, (-1540, -400), (-1400, -580), (-1290, -300), angle=0)
things(DEMON, (-1300, -560), (-1420, -440), angle=0)
m.thing(-1480, -340, KNIGHT, angle=0)
things(2012, (-1560, -480))
things(2047, (-1260, -300), (-1260, -340))

# --- the director's floor --------------------------------------------------------------------------------
m.thing(0, 260, 2019)                                                       # blue armour by the lift
things(2046, (60, 330), (700, 860), (300, 820), (640, 300), (500, 240))
things(17, (240, 220), (-60, 620), (700, 220), (840, 360), (840, 860), (-60, 300))
things(2049, (560, 220), (100, 860), (840, 660), (300, 220))
things(2012, (-60, 220), (240, 860), (720, 540), (500, 860), (-60, 440))
m.thing(800, 240, 2013)                                                     # a soul sphere at the edge of a side table
things(MANCUBUS, (250, 544), (560, 544), angle=270)
things(REVENANT, (-48, 760), (840, 780), (240, 460), (560, 460), angle=270)
things(IMP, (60, 440), (400, 340), (740, 440), (60, 720), (740, 600), (400, 720), (-60, 660), (840, 440), (200, 620), (610, 620), angle=270)
things(KNIGHT, (240, 760), (560, 760), (400, 400), (400, 260), angle=270)
things(CACO, (240, 340), (560, 340), (400, 660), angle=270)
things(CHAINGUNNER, (840, 540), (-60, 540), angle=270)
things(DEMON, (120, 240), (680, 240), angle=270)
m.thing(400, 840, BARON, angle=270)                                         # before the safe room

# --- the safe room -------------------------------------------------------------------------------------------
things(KNIGHT, (300, 1060), angle=270)
m.thing(480, 1040, 64, angle=270)                                           # an arch-vile (Vadim: "that guy who can revive other monsters")
m.thing(400, 1140, 2013)                                                    # a soul sphere
things(17, (290, 1160), (290, 990))
things(2012, (520, 990))
things(17, (520, 1160), (460, 1160), (290, 1100), (520, 1110))                                        # for what waits outside
things(2046, (340, 1160), (520, 1050))

# --- ambushes --------------------------------------------------------------------------------------------------
# RED, taken: the canteen
ajarmap.ambush(m, 10 + RED, IMP, (-200, -820), (200, -820), angle=90)
ajarmap.ambush(m, 10 + RED, SERGEANT, (-380, -480), (380, -480), angle=0, after=3)
# key 1, at the top: cacodemons over the desk, then knights at the lift
ajarmap.ambush(m, 1, CACO, (250, 280), (560, 280), (400, 640), angle=90)
ajarmap.ambush(m, 1, KNIGHT, (-40, 400), (60, 260), angle=90, after=4)
# GREEN, taken: accounts, round you
ajarmap.ambush(m, 10 + GREEN, SPECTRE, (-800, 380), (-760, 560), (-240, 250), angle=0)
ajarmap.ambush(m, 10 + GREEN, REVENANT, (-200, 100), (-240, 340), angle=180, after=4)
# key 2, in the cold store: they wait before the brass frame GREEN hangs in
ajarmap.ambush(m, 2, DEMON, (-780, -40), (-780, 40), (-700, 0), angle=180)
ajarmap.ambush(m, 2, IMP, (-1300, -480), (-1560, -540), angle=0, after=2)
# VIOLET, taken: the safe room's door, and the top beyond it
# (Vadim, having played it: "more enemies and the main boss, as an ambush")
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (300, 860), (500, 800), (100, 780), angle=270)
ajarmap.ambush(m, 10 + VIOLET, 16, (400, 760), angle=270, after=3)             # the cyberdemon, on every difficulty
ajarmap.ambush(m, 10 + VIOLET, CACO, (400, 320), (200, 520), (600, 520), angle=90, after=3)
ajarmap.ambush(m, 10 + VIOLET, MANCUBUS, (250, 660), (560, 660), angle=90, after=6)
ajarmap.ambush(m, 10 + VIOLET, KNIGHT, (760, 700), (760, 380), (20, 600), angle=180, after=6)
ajarmap.ambush(m, 10 + VIOLET, 64, (80, 480), (740, 540), angle=270, after=8)      # two arch-viles (Vadim)
# BLUE, taken: the cashier's door, and the car: they come out of the brass frame, wherever the car is
ajarmap.ambush(m, 10 + BLUE, KNIGHT, (-512, 500), (-512, 340), angle=90)
ajarmap.ambush(m, 10 + BLUE, DEMON, (-40, -60), (40, 60), angle=180, after=3)

PUZZLE = dict(
    start="canteen", goal="exit", names=ajarmap.NAMES, complete=True,
    walk=[("top", "first"), ("first", "canteen"),                           # the gaps
          ("first", "cashier", "1"), ("cashier", "first"),
          ("top", "safe", "2"), ("safe", "top")],
    keys={"1": "top", "2": "cold"},
    frames={101: "canteen", HOME: "car", HOME2: "first"},
    doors={
        RED: dict(home="car", lean="canteen"),
        GREEN: dict(home="cold", lean="first"),
        BLUE: dict(home="line", lean="cashier"),
        VIOLET: dict(home="line", lean="safe"),
    },
    home_chain=dict(frames=[HOME, HOME2], doors=[BLUE, VIOLET], level=1),
    lift=dict(car="car", floors=["canteen", "first", "top"], buttons={"canteen": (0, 2), "top": (1,)}),
)
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
