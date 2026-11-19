"""Act 2, level 6: "Watch Your Step" (MAP16). It wears MAP11's look (AJAR_INSTITUTE).

The institute's main stairwell, and company comes back. The flights are
gone: four landings go round the shaft, each a drop below the last, and the
foot lies under the head, a cliff of three floors. One new thing, the
endless stair (Vadim, 2026-11-19): a TEAL Pair whose one leaf is part of
the building, in the frame at the head. The other is the player's. Hung at
the foot, the stair only goes down and never ends, and the way up is down.

Places. The top (the start; the reading room off the head; the leaf; frame
103), and behind locks 1 and 2 the night room, whose brass frame takes
VIOLET only. The second floor (the labs; GREEN; frame 102). The first (the
canteen; RED; frame 101). The base: the foot (frame 104), open to the
boiler room (a thief, which stays down here and has nothing to carry off
but what the player brings), and the stores beyond (VIOLET; frame 105). The strongroom (RED's far side; key 1) and the cold store
(GREEN's; key 2) have no other way in. From the boiler room a hole (empty
hands only) leads to a cubby with a doorway of the building's up to the
reading room: nobody is left at the bottom, but no door goes up that way.

So: the leaf down to the foot; RED and GREEN for the keys; VIOLET up by
the stair to the brass frame. The thief takes a hung door only while it
sees you, and the well is open: it sees you from the foot on every
landing. When VIOLET is first taken a nailer comes to the foot. It nails
what hangs there, and a nailed leaf is one the thief cannot take.

In the PUZZLE graph the leaf is a plain door whose far side is the top,
which is what a Pair with one leaf fixed is.

Secret: the cubby.
"""
import ajarmap
import map_institute1 as I1
from ajarmap import RED, GREEN, VIOLET, TEAL, far_id, HOME
from map_institute1 import T, dress, tint, over, named, hang, things, frame, LOOK, FACES
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS
from udmf import Map, rect

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED
Z1, Z2, Z3 = 128, 256, 384                  # the first floor, the second, the top
H = 256                                     # every room's height but those named
SHAFT = Z3 + 192                            # the well's ceiling
PALE, RUST, COLD, STEEL, DIM, PAPER = 0xDCE8DC, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8, 0xF0E4C8
HEAD, FOOT = 110, 104                       # the stair's two frames
THIEF, NAILER = 20003, 20004
LEAF = ajarmap.LEAVES[TEAL][1]              # the player's leaf, in the PUZZLE graph


def box(base, height, top="BT", side=None, **k):
    return dict(I1.box(height, top, side, **k), floor=base + height)


def solid(base, part, height=H):            # to the ceiling: a pillar, a stack, a tank
    return dict(floor=base + height, **dress(side=part))


def table(base=0):
    return dict(floor=base + 32, ftex=T("TT"), side=T("TS")) if LOOK else box(base, 48)


def way(a, b, out, floor, near, far, words="", color=None):
    """An open way on any floor (MAP11's opening() is for the ground)."""
    ajarmap.opening(m, a, b, out, floor, color=tint(color))
    over(a, b, near)
    over(*I1._far(a, b, out), far)
    named(a, b, out, near, words)


def locked(a, b, out, floor, keys, line_id, near, far, words, **k):
    """A locked room door between the rooms whose walls are `near` and `far` (MAP14's)."""
    ajarmap.roomdoor(m, a, b, out, floor, keys=keys, line_id=line_id, **k)
    if LOOK:
        c, d = I1._far(a, b, out)
        for (p, q), o, part, s in (((a, b), out, near, words), ((c, d), (-out[0], -out[1]), far, "")):
            key = (LOOK, part, I1._shift(p, q, o), keys, s)
            m.line(p, q, upper=FACES.setdefault(key, f"AJID{LOOK}{len(FACES):02d}"))


# --- the well: four landings round the shaft, each a drop below the last ---------------
# The shaft itself (-64..64 both ways) is solid. North is the head, then east,
# south, and west the foot, which lies under the head.
WELL = dict(ceil=SHAFT, light=190, color=tint(STEEL), **dress(wall="EV", ftex="FE", ctex="KE"))
m.sector(rect(-256, 64, 64, 256), floor=Z3, **WELL)
m.sector(rect(64, -64, 256, 256), floor=Z2, **WELL)
m.sector(rect(-64, -256, 256, -64), floor=Z1, **WELL)
m.sector(rect(-256, -256, -64, 64), floor=0, **WELL)
frame((-256, 128), (-256, 192), (-1, 0), HEAD, STEEL, floor=Z3)
frame((-256, -160), (-256, -96), (-1, 0), FOOT, STEEL)

# --- the top: the reading room, and behind locks 1 and 2 the night room ------------------
ajarmap.fitted(m, (-640, 272, 240, 912), [
    ((-448, 464, -384, 528), solid(Z3, "PI")), ((48, 464, 112, 528), solid(Z3, "PI")),
    ((-448, 720, -384, 784), solid(Z3, "PI")), ((48, 720, 112, 784), solid(Z3, "PI")),
    ((-360, 624, -232, 688), box(Z3, 40, "DT", "DS")),                       # the librarian's desk
], floor=Z3, ceil=Z3 + H, light=200, color=tint(PALE), **dress(wall="LB", ftex="FL", ctex="KL"))
way((-128, 256), (-64, 256), (0, 1), Z3, "EV", "LB", "READING ROOM")
frame((-640, 560), (-640, 624), (-1, 0), 103, PALE, floor=Z3)
hang((-576, 912), (-448, 912), "BC")
hang((48, 912), (176, 912), "BC")
m.sector(rect(-264, 928, -136, 1008), floor=Z3, ceil=Z3 + 160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
locked((-232, 912), (-168, 912), (0, 1), Z3, "12", 301, "LB", "EV", "TEST HALL", free_inside=True)
over((-264, 1008), (-136, 1008), "EV")
ajarmap.way_home(m, -360, 1008, VIOLET, only=True, floor=Z3)

# --- the second floor: the labs ------------------------------------------------------------
ajarmap.fitted(m, (272, -240, 1040, 400), [
    ((464, -112, 592, 16), box(Z2, 48)), ((720, -112, 848, 16), box(Z2, 48)),
    ((464, 176, 592, 304), box(Z2, 48)), ((720, 176, 848, 304), box(Z2, 48)),
], floor=Z2, ceil=Z2 + H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
way((256, 64), (256, 128), (1, 0), Z2, "EV", "LA", "LABORATORIES")
frame((1040, 48), (1040, 112), (1, 0), 102, RUST, floor=Z2)

# --- the first floor: the canteen ------------------------------------------------------------
ajarmap.fitted(m, (-48, -912, 720, -272), [
    ((144, -560, 272, -432), table(Z1)), ((400, -560, 528, -432), table(Z1)),
    ((144, -800, 272, -672), table(Z1)), ((400, -800, 528, -672), table(Z1)),
], floor=Z1, ceil=Z1 + H, light=200, color=tint(PAPER), **dress(wall="CA", ftex="FN", ctex="KC"))
way((64, -256), (128, -256), (0, -1), Z1, "EV", "CA", "CANTEEN")
frame((304, -912), (368, -912), (0, -1), 101, PAPER, floor=Z1)

# --- the base: the boiler room, open to the foot; the stores beyond ----------------------------
ajarmap.fitted(m, (-720, -720, -64, -256), [
    ((-656, -560, -560, -464), solid(0, "TK", 224)), ((-400, -560, -304, -464), solid(0, "TK", 224)),
], floor=0, ceil=224, light=130, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
over((-256, -256), (-64, -256), "EV")
ajarmap.fitted(m, (-1376, -880, -736, -336), [
    ((-1248, -768, -1184, -448), solid(0, "SK", 192)), ((-1056, -768, -992, -448), solid(0, "SK", 192)),
    ((-928, -768, -864, -448), solid(0, "SK", 192)),
], floor=0, ceil=192, light=140, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
way((-720, -560), (-720, -496), (-1, 0), 0, "PU", "AR", "STORES")
frame((-1376, -640), (-1376, -576), (-1, 0), 105, DIM)
# the hole, and the cubby behind it: a doorway of the building's up to the reading room
m.sector(rect(-592, -864, -400, -736), floor=0, ceil=128, light=120, color=tint(DIM), special=1024,
         **dress(wall="AR", ftex="FR", ctex="KA"))
I1.squeeze((-520, -720), (-472, -720), (0, -1), 0, "PU", "AR", "HATCH")
ajarmap.doorway(m, 1, (-528, -864), (-464, -864), (0, -1), 0, (240, 560), (240, 624), (1, 0), Z3)

# --- the strongroom (RED's far side) and the cold store (GREEN's): no other way in ---------------
m.sector(rect(1600, -640, 1984, -256), floor=0, ceil=160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
ajarmap.recess(m, (1600, -480), (1600, -416), (-1, 0), 0, far_id(RED), FOOT, far_colour=RED, color=tint(STEEL))
m.sector(rect(1600, 200, 1984, 584), floor=0, ceil=192, light=120, color=tint(COLD),
         **dress(wall="PU", ftex="FP", ctex="KP"))
ajarmap.recess(m, (1600, 360), (1600, 424), (-1, 0), 0, far_id(GREEN), FOOT, far_colour=GREEN, color=tint(COLD))

# --- doors and keys ----------------------------------------------------------------------------
m.thing(-240, 160, ajarmap.DOOR_T, args=(0, TEAL, HEAD, 1, TEAL))            # the head's leaf: part of the building
m.thing(-160, 224, ajarmap.DOOR_T, angle=270, args=(0, TEAL, 0, 0, TEAL))    # the player's
ajarmap.door(m, RED, 700, -420, angle=180)
ajarmap.door(m, GREEN, 980, -180, angle=180)
ajarmap.door(m, VIOLET, -1320, -840, angle=90)
ajarmap.key(m, 1, 1940, -300)
ajarmap.key(m, 2, 1940, 540)

# --- things: the reading room ---------------------------------------------------------------------
m.thing(-96, 400, 1, angle=270)
m.thing(-96, 480, 2001)                                                     # shotgun
things(2008, (-40, 480), (-150, 480))
m.thing(160, 860, 2002)                                                     # chaingun
things(2048, (200, 860), (-600, 860))
things(ZOMBIE, (-300, 400), (-520, 400), (160, 400), (-200, 720), angle=270)
things(SERGEANT, (-520, 640), (160, 640), (-300, 820), (0, 840), angle=270)
things(IMP, (-560, 820), (190, 780), (-320, 560), (-20, 600), (-560, 330), (190, 330), angle=270)
m.thing(-200, 850, CHAINGUNNER, angle=270)
things(2011, (-600, 300), (200, 300))
things(2012, (-600, 700))
things(2049, (-20, 880), (-480, 880))
m.thing(200, 500, 2018)                                                     # green armour

# --- the second floor --------------------------------------------------------------------------------
things(IMP, (160, 200), (160, -20), angle=180)                              # on the landing
m.thing(656, 96, 82)                                                        # super shotgun
things(IMP, (400, 96), (656, -180), (656, 360), (900, 96), (400, -180), (400, 340), (900, -160), (900, 340), angle=180)
things(DEMON, (560, 96), (656, -60), (656, 240), angle=180)
things(CHAINGUNNER, (960, 200), (960, -60), angle=180)
things(KNIGHT, (800, 100), (340, 340), angle=180)
things(REVENANT, (980, 340), (840, -200), angle=180)
m.thing(660, 150, CACO, angle=180)
things(2049, (320, -200), (320, 360), (1000, 0))
things(2048, (1000, 360))
things(2012, (320, 0), (1000, -200))
things(2011, (700, -200), (700, 360))

# --- the first floor --------------------------------------------------------------------------------
things(SERGEANT, (160, -160), (40, -200), angle=90)                         # on the landing
m.thing(336, -620, 2003)                                                    # rocket launcher
things(2046, (336, -660), (-10, -300))
things(MANCUBUS, (624, -600), (40, -600), angle=90)
things(KNIGHT, (336, -340), (600, -360), (60, -380), angle=90)
things(IMP, (200, -320), (470, -320), (680, -320), (0, -330), (200, -870), (480, -870), (680, -860), (0, -860), angle=90)
things(REVENANT, (336, -740), (640, -800), angle=90)
things(DEMON, (80, -470), (620, -460), angle=90)
things(SERGEANT, (-10, -760), (690, -700), (336, -420), angle=90)
m.thing(560, -880, CHAINGUNNER, angle=90)
things(2049, (690, -300), (-10, -880))
things(2012, (690, -880), (-10, -520))
things(2011, (336, -880), (690, -520))
m.thing(336, -500, 2023)                                                    # berserk, between the tables

# --- the foot and the boiler room: the thief ------------------------------------------------------------
things(DEMON, (-130, -200), (-130, 0), angle=90)
m.thing(-160, -400, THIEF, angle=90, args=(0, 1))                           # it stays down here, in sight of the foot's frame
things(SPECTRE, (-600, -340), (-120, -640), (-520, -660), angle=0)
things(KNIGHT, (-480, -512), (-640, -640), angle=0)
m.thing(-240, -560, BARON, angle=90)
things(IMP, (-680, -420), (-250, -320), (-500, -320), (-250, -680), angle=0)
things(2049, (-100, -300), (-680, -680))
things(2012, (-100, -680), (-200, 30))
things(2046, (-340, -680))

# --- the stores: dark, and the plasma rifle -----------------------------------------------------------------
m.thing(-1120, -840, 2004)
things(17, (-1340, -380), (-780, -840))
things(REVENANT, (-1120, -400), (-800, -400), angle=0)
things(SPECTRE, (-1310, -400), (-1120, -600), (-800, -800), angle=0)
things(IMP, (-1000, -840), (-800, -650), (-1310, -760), angle=0)
m.thing(-1300, -520, KNIGHT, angle=0)
things(2012, (-960, -380), (-1340, -700))
things(2047, (-780, -380))

# --- the strongroom, the cold store, the cubby -----------------------------------------------------------------
m.thing(1800, -448, KNIGHT, angle=180)
things(IMP, (1900, -600), (1700, -300), angle=180)
m.thing(1940, -600, 2013)                                                   # a soul sphere
things(SPECTRE, (1800, 392), (1900, 250), angle=180)
m.thing(1700, 540, DEMON, angle=180)
things(17, (1940, 240))
things(2012, (1660, 240))
m.thing(-496, -800, 2019)                                                   # blue armour: the secret

# --- ambushes ------------------------------------------------------------------------------------------
# VIOLET, taken: the nailer comes to the foot (the first of the level's
# ambushers: there on every difficulty), and company in the stores and the boiler room
ajarmap.ambush(m, 10 + VIOLET, NAILER, (-190, 20), angle=270)
ajarmap.ambush(m, 10 + VIOLET, REVENANT, (-800, -520), (-1120, -500), angle=180)
ajarmap.ambush(m, 10 + VIOLET, KNIGHT, (-160, -560), (-560, -640), angle=90, after=3)
# the leaf, taken: the reading room, and cacodemons that come up the well
ajarmap.ambush(m, 10 + TEAL, IMP, (-560, 500), (180, 500), angle=270)
ajarmap.ambush(m, 10 + TEAL, CACO, (-200, -220), (-110, -100), angle=90, after=2)
# RED, taken: the canteen
ajarmap.ambush(m, 10 + RED, SPECTRE, (100, -700), (580, -760), angle=90)
# key 1, in the strongroom: knights wait in the boiler room
ajarmap.ambush(m, 1, KNIGHT, (-250, -440), (-560, -300), angle=90)
# GREEN, taken: the labs
ajarmap.ambush(m, 10 + GREEN, DEMON, (430, 220), (900, 0), angle=180)
# key 2, in the cold store: revenants in the labs
ajarmap.ambush(m, 2, REVENANT, (400, 0), (900, 200), angle=180)

PUZZLE = dict(
    start="top", goal="exit", names={**ajarmap.NAMES, LEAF: "the TEAL leaf"}, complete=True, home_frame=HOME,
    walk=[("top", "second"), ("second", "first"), ("first", "base"), ("top", "base"),   # the drops
          ("base", "top", "", "squeeze"),                                               # the hole and the cubby's doorway
          ("top", "night", "12"), ("night", "top")],
    keys={"1": "strong", "2": "cold"},
    frames={103: "top", 102: "second", 101: "first", FOOT: "base", 105: "base", HOME: "night"},
    only={HOME: VIOLET},
    doors={
        RED: dict(home="strong", lean="first"),
        GREEN: dict(home="cold", lean="second"),
        VIOLET: dict(home="night", lean="base"),
        LEAF: dict(home="top", lean="top"),                                             # its twin is fixed at the head
    },
    thief=dict(zone="base", sees=["base", "first", "second", "top"]),
    nailer=dict(zone="base"),
)
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
