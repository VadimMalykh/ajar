"""Act 1, level 4: "Party Wall" (MAP04).

A block of houses round an open yard. The way out is the RED door, in the
landlord's strongroom behind two locks and a hole in the wall.

The yard is one place to walk about in, under the sky, with three frames.
Everything else is above it, below it or behind something, and you can see
most of it long before you can get there: the balcony (BLUE), the roof
(GREEN), the loft (YELLOW), the kennel (VIOLET).

What is new:

- The thief. It starts with BLUE, the only door there is, and it stays in
  the yard (thing argument 2): frames out here are where it works.
- Squeezes (ajarmap.squeeze): holes a door will not go through. You pass
  with empty hands or not at all. The coal hole between the light well and
  the cellar, the hatch out of the kennel (a drop: one way), the hole into
  the pantry and the one into the strongroom.
- A frame behind a squeeze. The light well, where the boiler stands, has a
  frame, and the only way to bring a door to it is to jump in from the roof
  with the door in your hands. RED must be picked up with empty hands, there
  are four other doors and three frames in the yard: one door has to go
  down the well.
- Sending something somewhere worse. Two barons sit on RED. VIOLET opens
  onto the kennel, which they cannot leave: let them follow you in, go out
  by the hatch, take the door away. The door with the barons behind it is
  the one to put down the well. (You can also just fight them.)

Keys: 1 on the balcony and 2 on the roof open the suite off the loft
(VIOLET). 3 in the kennel and 4 in the well open the landlord's office.
The cellar door is bolted on the cellar side, so the first way down is the
roof, the well and the coal hole.

Secrets: PINK hangs in the pantry, behind a squeeze, and cannot be carried
out; it opens onto a store. A target in a hole high in the south wall can
only be seen, and shot, from the edge of the roof; it opens a closet in
the yard. A nook off the roof.
"""
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


BALCONY, ROOF, LOFT, CELLAR, KENNEL = 160, 320, 192, -128, -64
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
SEAT = dict(ftex="AJSOFA", side="AJSOFA")
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
GATE_CELLAR, CLOSET = 401, 420

# The block's look (gfx_yard.py): 1, a brick tenement, is the user's choice
# for the whole of it. AJAR_YARD=2 and 3 are the candidates that lost (a
# whitewashed court, an inn yard); AJAR_YARD=0 is the level as first built.
# With a look, each side of the yard is a house of its own (W, N, E, S),
# rooms are not tinted, and everything below ground is the same in all three.
LOOK = (os.environ.get("AJAR_YARD") or "1").replace("0", "")
if LOOK:
    WARM = GOLD = SKY = LEAF = PLUM = ROSE = None
    FRONT = {h: f"AJ4Y{LOOK}{h}" for h in "WNES"}
    LOWC = f"AJ4E{LOOK}"
    RAIL = dict(RAIL, mid=f"AJ4N{LOOK}", floorpeg=True)
    PATH, BARS = f"AJ4P{LOOK}", "AJ4XB"
    YARD = dict(OPEN, ftex=f"AJ4F{LOOK}")
    # a strip of yard along each house, so that its walls are that house's
    EDGES = [((0, 0, 16, 1152), dict(wall=FRONT["W"])), ((1520, 0, 1536, 1152), dict(wall=FRONT["E"])),
             ((16, 0, 1520, 16), dict(wall=FRONT["S"])), ((16, 1136, 1520, 1152), dict(wall=FRONT["N"]))]
    PASSAGE = dict(wall=f"AJ4A{LOOK}", ftex=f"AJ4F{LOOK}", ctex=LOWC)
    PORCH = dict(wall=f"AJ4A{LOOK}", ftex=PATH, ctex=LOWC)
    WASH = dict(wall=f"AJ4H{LOOK}", ftex=f"AJ4I{LOOK}", ctex=LOWC)
    PANTRY = dict(wall="AJ4XP", ftex=f"AJ4I{LOOK}", ctex=LOWC)
    OFFICE = dict(wall=f"AJ4O{LOOK}", ftex=f"AJ4K{LOOK}", ctex=LOWC)
    STRONG = dict(wall="AJSAFE", ftex=f"AJ4K{LOOK}", ctex=LOWC)
    DECK = dict(OPEN, wall=FRONT["W"], side=f"AJ4B{LOOK}", ftex="AJBOARD")
    SLATES = dict(OPEN, wall=f"AJ4G{LOOK}", side=f"AJ4L{LOOK}", ftex=f"AJ4M{LOOK}")
    NOOK = dict(wall=f"AJ4A{LOOK}", ftex=f"AJ4M{LOOK}", ctex=LOWC)
    WELL = dict(OPEN, wall=f"AJ4V{LOOK}", ftex="AJ4XF")
    LOFTL = dict(wall=f"AJ4J{LOOK}", side=f"AJ4T{LOOK}", ftex="AJBOARD", ctex=f"AJ4C{LOOK}")
    SUITE = dict(wall=f"AJ4W{LOOK}", ftex=f"AJ4K{LOOK}", ctex=LOWC)
    DOWN = dict(wall="AJ4XC", ftex="AJ4XF", ctex="AJ4XD")
    STEPS = dict(wall="AJ4XR", ftex="AJ4XF", ctex="AJ4XD")
    DOGS = dict(wall="AJ4XK", ftex="AJ4XS", ctex="AJ4XD")
    HOLE = dict(wall="AJ4XR")
    WDOOR, ODOOR, SDOOR = f"AJ4D{LOOK}W", f"AJ4D{LOOK}O", f"AJ4D{LOOK}S"
    m.align = ({f"AJ4{k}{LOOK}{h}" for k in "YZU" for h in "WNES"} |
               {f"AJ4{k}{LOOK}" for k in "BRQTGLVAHOJW"} | {"AJ4XC", "AJ4XR", "AJ4XK", "AJ4XP"})
else:
    FRONT = dict.fromkeys("WNES")
    PATH, BARS, EDGES = "AJARCHF", "AJWIN", []
    BRICK = dict(wall="AJBRICK")
    YARD = dict(OPEN, ftex="AJPIT")
    PASSAGE = DOWN = dict(BRICK, ftex="AJPIT")
    PORCH = dict(BRICK, ftex="AJARCHF")
    WASH = dict(ftex="AJTILEF")
    PANTRY = OFFICE = SUITE = {}
    STRONG = dict(wall="AJSAFE")
    DECK = dict(OPEN, ftex="AJBOARD")
    SLATES = dict(OPEN, ftex="AJTRIMF")
    NOOK = dict(BRICK, ftex="AJTRIMF")
    WELL = dict(OPEN, ftex="AJPIT")
    LOFTL = dict(BRICK, ftex="AJBOARD")
    STEPS = HOLE = BRICK
    DOGS = dict(BRICK, ftex="AJPIT")
    WDOOR = ODOOR = SDOOR = ""


def front(a, b, house, **k):
    """The wall over or under an opening a-b in a house's front carries on as
    that front, in line with the wall beside it."""
    if LOOK:
        m.line(a, b, upper=FRONT[house], dontpegtop=True, **k)


def windows(house, *pieces, lower=None):
    """Windows on both upper storeys of 64-long pieces of a house's front,
    each given by its two ends; lit below and above by turns. `lower`: the
    pieces are the front of something raised, and that is the texture."""
    for i, (a, b) in enumerate(pieces if LOOK else ()):
        m.cut(a, b)
        if lower:
            m.line(a, b, lower=lower)
        else:
            m.line(a, b, mid=f"AJ4{'ZU'[i % 2]}{LOOK}{house}")


def along(house, fixed, starts, axis="x", **k):
    windows(house, *(((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
                     for s in starts), **k)


def rail(*runs):
    for a, b in runs:
        m.cut(a, b)             # a railing ends where it says, not at the next corner of a room
        m.line(a, b, **RAIL)


def porch(box, a, b, house):
    """A doorway's worth of low ceiling on the yard side of a door, so that
    the door is not drawn again higher up the yard's tall wall. a-b is its
    mouth in the front of `house`."""
    m.sector(rect(*box), ceil=128, light=170, **PORCH)
    front(a, b, house)


# === the yard ================================================================
ajarmap.fitted(m, (0, 0, 1536, 1152), [
    ((736, 0, 800, 512), dict(ftex=PATH)),                                   # the path from the gate
    ((704, 512, 832, 640), dict(floor=24, ftex="AJGRASS", side="AJARCH")),   # a bed of grass
    ((256, 256, 352, 352), dict(WOOD, floor=48)),                            # crates
    ((1184, 800, 1280, 896), dict(WOOD, floor=48)),
] + EDGES, floor=0, light=200, **YARD)
# the gate passage: start here. The street gate behind you is shut
ajarmap.fitted(m, (640, -320, 896, 0), [((736, -320, 800, 0), dict(ftex=PATH))],
               ceil=128, light=170, **PASSAGE)
front((640, 0), (896, 0), "S")
recess((640, -192), (640, -128), (-1, 0), 0, 101, 201)                      # frame in the passage
recess((96, 1152), (160, 1152), (0, 1), 0, 102, 201)                        # frame in the north wall
recess((1536, 448), (1536, 512), (1, 0), 0, 104, 201)                       # frame by the office
front((96, 1152), (160, 1152), "N")
front((1536, 448), (1536, 512), "E")
# windows in the fronts, clear of every opening
along("S", 0, (64, 192, 320, 448, 960, 1216, 1408))
along("W", 0, (192, 960), "y")
along("N", 1152, (192, 1344))
along("E", 1536, (64, 320), "y")

# --- the wash house, south-west, and the pantry behind a hole in its wall -----
porch((-32, 64, 0, 160), (0, 64), (0, 160), "W")
ajarmap.fitted(m, (-416, 0, -48, 224), [((-416, 160, -352, 224), dict(floor=32, ftex="AJSINK", side="AJTILE")),
                                        ((-416, 96, -352, 160), dict(floor=32, ftex="AJSINK", side="AJTILE"))],
               ceil=128, light=160, **WASH)
ajarmap.roomdoor(m, (-32, 80), (-32, 144), (-1, 0), 0, skin=WDOOR)
m.sector(rect(-416, -288, -160, -16), ceil=112, light=140, color=ROSE, special=1024, **PANTRY)   # pantry (secret)
ajarmap.squeeze(m, (-304, 0), (-256, 0), (0, -1), 0)
recess((-416, -184), (-416, -120), (-1, 0), 0, 106, 201, color=ROSE)        # its frame: PINK hangs here

# --- the landlord's office, east: two locks. RED is in the strongroom ---------
porch((1536, 192, 1568, 288), (1536, 192), (1536, 288), "E")
ajarmap.fitted(m, (1584, 64, 1968, 416), [((1840, 96, 1904, 192), dict(WOOD, floor=32))],
               ceil=128, light=170, color=WARM, **OFFICE)
ajarmap.roomdoor(m, (1568, 208), (1568, 272), (1, 0), 0, keys="34", line_id=301, skin=ODOOR)
m.sector(rect(1984, 128, 2240, 352), ceil=112, light=190, color=WARM, **STRONG)
ajarmap.squeeze(m, (1968, 216), (1968, 264), (1, 0), 0)
recess((2240, 208), (2240, 272), (1, 0), 0, 105, 201, color=WARM)           # strongroom frame

# --- secrets in the south wall: a target in a hole that only the roof looks
# into, and the closet it opens --------------------------------------------------
m.sector(rect(1100, -256, 1164, 0), floor=ROOF, ceil=ROOF + 48, light=255,
         ftex="AJTRIMF", ctex="AJTRIMF", **HOLE)
front((1100, 0), (1164, 0), "S", lower=FRONT["S"], dontpegbottom=True)
m.line((1100, -256), (1164, -256), special=11, args=(CLOSET, 16), impact=True, mid="AJTARG")
m.sector(rect(1312, -16, 1376, 0), floor=0, ceil=0, light=160, id=CLOSET, **HOLE)
front((1312, 0), (1376, 0), "S")
m.sector(rect(1280, -144, 1408, -16), ceil=96, light=150, wall="AJSAFE", special=1024)

# === above the yard ============================================================
# --- the balcony (BLUE's far side), along the west wall -------------------------
ajarmap.fitted(m, (-256, 256, 0, 896), [((-256, 704, -224, 832), dict(SEAT, floor=BALCONY + 16))],
               floor=BALCONY, light=200, color=SKY, **DECK)
rail(((0, 256), (0, 320)), ((0, 448), (0, 896)))
along("W", -256, (320, 448, 640, 768), "y")
along("W", 256, (-128,))
along("W", 896, (-128,))
recess((-256, 544), (-256, 608), (-1, 0), BALCONY, far_id(BLUE), 101, far_colour=BLUE, color=SKY)

# --- the roof (GREEN's far side), along the north wall, round the light well ----
SLATE = dict(floor=ROOF, light=210, color=LEAF, **SLATES)
if LOOK:                                  # the strip along the yard has the house's front; the rest, the well's lining
    m.sector(rect(256, 1152, 1280, 1216), **dict(SLATE, side=f"AJ4R{LOOK}"))
    m.sector(rect(256, 1216, 1280, 1344), **SLATE)
    along("N", 1152, range(320, 1280, 128), lower=f"AJ4Q{LOOK}")
else:
    m.sector(rect(256, 1152, 1280, 1344), **SLATE)
m.sector(rect(256, 1344, 640, 1536), **SLATE)
m.sector(rect(896, 1344, 1280, 1536), **SLATE)
recess((256, 1408), (256, 1472), (-1, 0), ROOF, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)
m.sector(rect(160, 1232, 256, 1328), floor=ROOF, ceil=ROOF + 96, light=110, special=1024, **NOOK)   # a nook (secret)
if LOOK:
    m.line((256, 1232), (256, 1328), upper=SLATES["wall"], dontpegtop=True)

# --- the light well in the middle of the roof: the boiler, a frame, and the
# coal hole to the cellar ----------------------------------------------------------
ajarmap.fitted(m, (640, 1344, 896, 1536), [((832, 1360, 880, 1456), dict(floor=CELLAR + 80, ftex="AJSTEEL", side="AJSTEEL"))],
               floor=CELLAR, light=150, **WELL)
recess((656, 1536), (720, 1536), (0, 1), CELLAR, 103, 201)                  # the well's frame
ajarmap.squeeze(m, (800, 1536), (848, 1536), (0, 1), CELLAR, thick=80, unbolt=GATE_CELLAR)
if LOOK:
    for a, b in (((656, 1536), (720, 1536)), ((800, 1536), (848, 1536))):
        m.line(a, b, upper=WELL["wall"], dontpegtop=True)

# --- the loft (YELLOW's far side), along the east wall; the suite off it --------
ajarmap.fitted(m, (1536, 544, 1920, 1104), [((1856, 576, 1920, 704), dict(floor=LOFT + 32, ftex="AJCLOTH", side="AJCLOTH")),
                                            ((1568, 1008, 1632, 1104), dict(floor=LOFT + 32, ftex="AJCLOTH", side="AJCLOTH"))],
               floor=LOFT, ceil=LOFT + 144, light=175, color=GOLD, **LOFTL)
rail(((1536, 544), (1536, 768)), ((1536, 896), (1536, 1104)))
for a, b in (((1536, 544), (1536, 768)), ((1536, 768), (1536, 896)), ((1536, 896), (1536, 1104))):
    front(a, b, "E")
recess((1696, 1104), (1760, 1104), (0, 1), LOFT, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)
ajarmap.fitted(m, (1936, 672, 2256, 992), [((2192, 704, 2256, 832), dict(floor=LOFT + 24, ftex="AJQUILT", side="AJWOOD")),
                                           ((2224, 704, 2256, 832), dict(floor=LOFT + 30, ftex="AJPILLOW", side="AJWOOD"))],
               floor=LOFT, ceil=LOFT + 112, light=180, color=GOLD, **SUITE)
ajarmap.roomdoor(m, (1920, 800), (1920, 864), (1, 0), LOFT, keys="12", line_id=302, skin=SDOOR)

# === below ======================================================================
# --- the cellar, north of the well; stairs up to a door in the yard that is
# bolted on this side ----------------------------------------------------------------
ajarmap.fitted(m, (256, 1616, 1280, 1936), [((512, 1808, 608, 1936), dict(WOOD, floor=CELLAR + 48)),
                                            ((960, 1616, 1056, 1712), dict(WOOD, floor=CELLAR + 48))],
               floor=CELLAR, ceil=0, light=120, **DOWN)
m.sector(rect(1296, 1520, 1520, 1936), floor=CELLAR, ceil=0, light=130, **DOWN)
ajarmap.opening(m, (1280, 1744), (1280, 1808), (1, 0), CELLAR)
porch((1424, 1152, 1520, 1184), (1424, 1152), (1520, 1152), "N")
m.sector(rect(1440, 1200, 1504, 1264), ceil=128, light=150, **STEPS)
ajarmap.bolted(m, (1440, 1184), (1504, 1184), (0, 1), 0, GATE_CELLAR, line_id=303)
ajarmap.stairs(m, (1440, 1264), (1504, 1264), (0, 1), 0, CELLAR, ceil=128, light=140, **STEPS)

# --- the kennel (VIOLET's far side): a step above the cellar. Bars to look
# through, and a hatch to drop out of -------------------------------------------------
m.sector(rect(-144, 1616, 240, 1936), floor=KENNEL, ceil=KENNEL + 128, light=150, color=PLUM, **DOGS)
recess((-144, 1744), (-144, 1808), (-1, 0), KENNEL, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)
ajarmap.squeeze(m, (240, 1648), (240, 1696), (1, 0), KENNEL, unbolt=GATE_CELLAR)
m.sector(rect(240, 1776, 256, 1904), floor=KENNEL, ceil=KENNEL + 56, light=150,
         ftex="AJTRIMF", ctex="AJTRIMF", **HOLE)
m.line((240, 1776), (240, 1904), mid=BARS, midboth=True, blocking=True)

# === far sides that are places of their own ====================================
# --- the store (PINK's far side): no other way in (secret) ----------------------
m.sector(rect(4000, 0, 4448, 384), ceil=160, light=150, color=ROSE, wall="AJSAFE", special=1024)
recess((4000, 160), (4000, 224), (-1, 0), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)

# --- the way out (RED's far side): the same room in every level -------------
ajarmap.way_out(m, 5000, 0, RED)

# --- doors and keys ----------------------------------------------------------
THIEF = 20003
m.thing(768, -200, 1, angle=90)                                           # player start, in the gate passage
m.thing(768, 420, THIEF, angle=270, args=(BLUE, 1))                       # the thief: has BLUE, stays in the yard
ajarmap.door(m, BLUE, 768, 420, angle=270)                                # (on the thief's back)
ajarmap.door(m, GREEN, -200, 870, angle=270)                              # leaning on the balcony
ajarmap.door(m, YELLOW, 1250, 1900, angle=180)                            # leaning in the cellar
ajarmap.door(m, VIOLET, 2170, 940, angle=180)                             # leaning in the suite
ajarmap.door(m, PINK, -400, -152, frame=106)                              # hanging in the pantry
ajarmap.door(m, RED, 2200, 160, angle=180)                                # leaning in the strongroom
ajarmap.key(m, 1, -200, 340)                                              # south end of the balcony
ajarmap.key(m, 2, 1240, 1480)                                             # far end of the roof
ajarmap.key(m, 3, -80, 1660)                                              # the kennel
ajarmap.key(m, 4, 700, 1400)                                              # the well

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO = 65, 69, 3003, 66, 3006, 3005
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX = (
    2001, 82, 2002, 2003, 2008, 2049, 2007, 2048, 2010, 2046)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, BARREL = 24, 2035


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the gate passage: a shotgun for anyone who came without one
things(SHOTGUN, (680, -280))
things(SHELLS, (856, -280), (856, -240))
things(STIM, (680, -60))
things(LAMP, (664, -24), (872, -24))
# the yard: tenants. The lodger wakes when you are well into it
things(ZOMBIE, (500, 200), (1050, 200), (300, 600), (1250, 620), (560, 980), (980, 1000), angle=270)
things(IMP, (150, 150), (1400, 150), (150, 1000), (1400, 1050), (640, 760), (900, 760), angle=270)
things(SERGEANT, (420, 420), (1120, 420), (420, 900), (1120, 950), angle=270)
things(DEMON, (200, 500), (1340, 700), (768, 900), angle=270)
things(CACO, (400, 700), (1100, 600), angle=270, ambush=True)
things(LODGER, (1300, 1000), args=(300,))
things(IMP, (304, 304), (1232, 848), angle=270)                             # on the crates
things(BARREL, (380, 300), (1160, 860), (1300, 300))
things(LAMP, (24, 24), (1512, 24), (24, 1128), (1512, 1128), (728, 664), (808, 664))
things(MEDIKIT, (60, 60), (1480, 1100))
things(SHELLS, (300, 380), (1230, 920), (60, 1100))
things(CLIP, (768, 100), (768, 180))
things(STIM, (1480, 60), (768, 700))
# the wash house: washing day
things(ZOMBIE, (-200, 60), (-300, 180), angle=0)
things(SERGEANT, (-120, 180), angle=0)
things(IMP, (-340, 40), angle=0)
things(SHELLBOX, (-380, 30))
things(STIM, (-100, 30))
# the pantry: something eating
things(IMP, (-220, -80), (-220, -240), angle=90)
things(CANDLE, (-180, -40), (-180, -264))
things(HELMET, (-380, -40))
# the store: what the landlord keeps for himself
things(LAUNCHER, (4380, 192))
things(ROCKETBOX, (4380, 140), (4380, 244))
things(MEGA, (4400, 340))
things(AMMOBOX, (4400, 40))
things(REVENANT, (4250, 100), (4250, 290), angle=180)
things(KNIGHT, (4130, 192), angle=180)
things(CANDELABRA, (4424, 24), (4424, 360))
# the office: the landlords, on RED and deaf to the yard
things(BARON, (1800, 300), (1700, 130), angle=180, ambush=True)
things(TORCH_R, (1944, 88), (1944, 392))
things(MEDIKIT, (1920, 380))
things(TECHLAMP, (2216, 152), (2216, 328))
# the closet behind the target
things(SPHERE, (1344, -100))
things(ROCKETBOX, (1300, -120), (1388, -120))
# the balcony: someone watching the yard
things(CHAINGUNNER, (-60, 600), angle=0)
things(IMP, (-180, 480), (-180, 760), angle=0)
things(SERGEANT, (-120, 840), angle=270)
things(TORCH_B, (-232, 520), (-232, 632))
things(SHELLS, (-230, 280))
things(STIM, (-40, 870))
# the roof: snipers at the edge, souls round the chimneys, a guard on key 2
things(CHAINGUNNER, (420, 1190), (1020, 1190), angle=270)
things(IMP, (700, 1250), (860, 1250), (330, 1300), angle=270)
things(SOUL, (400, 1480), (560, 1400), (980, 1400), (1100, 1300), angle=270)
things(ZOMBIE, (560, 1200), (1200, 1250), angle=270)
things(REVENANT, (1180, 1420), angle=180)
things(SUPER, (960, 1490))
things(SHELLS, (1000, 1490), (920, 1490))
things(BONUS, (1116, 1170), (1148, 1170))                                  # stand here and look south
things(TORCH_G, (280, 1384), (280, 1496))
things(ARMOR, (208, 1280))                                                 # in the nook
things(MEDIKIT, (300, 1180))
# the well: you are not alone down here
things(SPECTRE, (700, 1500), (790, 1380), angle=90)
things(POOL, (760, 1440))
things(STIM, (660, 1360))
things(BERSERK, (824, 1506))                                              # by the coal hole: for the cellar beyond it
# the cellar: dark, and full
things(SPECTRE, (400, 1700), (700, 1850), (900, 1800), (1150, 1700), angle=270)
things(DEMON, (560, 1700), (1100, 1880), angle=270)
things(SERGEANT, (330, 1900), (1200, 1640), angle=270)
things(IMP, (760, 1700), (300, 1640), (880, 1900), angle=270)
things(SPECTRE, (700, 1660), (1180, 1900), angle=270)
things(ZOMBIE, (1400, 1600), (1400, 1880), angle=180)
things(SERGEANT, (1340, 1740), angle=180)
things(CANDLE, (280, 1640), (1256, 1640), (280, 1912), (1320, 1912))
things(SHELLBOX, (540, 1780))
things(MEDIKIT, (1010, 1740))
# the kennel: the dogs, on key 3
things(DEMON, (60, 1680), (100, 1880), angle=180)
things(POOL, (0, 1800))
things(STIM, (200, 1900))
# the loft: tenants who do not pay
things(SERGEANT, (1700, 640), (1860, 900), angle=180)
things(IMP, (1600, 620), (1620, 940), (1840, 1040), angle=180)
things(ZOMBIE, (1700, 1000), (1760, 600), angle=180)
things(KNIGHT, (1780, 800), angle=180)
things(CHAINGUN, (1880, 760))
things(AMMOBOX, (1880, 720))
things(CANDELABRA, (1672, 1080), (1784, 1080))
things(MEDIKIT, (1560, 580))
# the suite: VIOLET, and whoever sleeps here
things(CHAINGUNNER, (2100, 720), angle=180)
things(IMP, (2000, 940), (2000, 720), angle=180)
things(SERGEANT, (2100, 900), angle=180)
things(SHELLBOX, (2230, 960))
things(LAMP, (1960, 696))
# the way out
things(REVENANT, (5264, 128), angle=180)
things(SERGEANT, (5230, 48), (5230, 208), angle=180)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "yard" is the yard, gate passage and wash house: where the thief works.
# "boiler" is the light well. a is the cellar door's bolt.
PUZZLE = dict(
    start="yard", goal="exit", names=ajarmap.NAMES, complete=True,
    walk=[("balcony", "yard"), ("roof", "yard"), ("roof", "boiler"), ("loft", "yard"),
          ("boiler", "cellar", "", "squeeze"), ("cellar", "boiler", "", "squeeze"),   # the coal hole
          ("kennel", "cellar", "", "squeeze"),                                        # the hatch, a drop
          ("yard", "cellar", "a"), ("cellar", "yard", "a"),                           # the cellar door
          ("loft", "suite", "12"), ("suite", "loft", "12"),
          ("yard", "office", "34"), ("office", "yard", "34"),
          ("office", "strong", "", "squeeze"), ("strong", "office", "", "squeeze"),
          ("yard", "pantry", "", "squeeze"), ("pantry", "yard", "", "squeeze")],
    keys={"1": "balcony", "2": "roof", "3": "kennel", "4": "boiler", "a": "cellar"},
    auto="a",
    frames={101: "yard", 102: "yard", 104: "yard", 103: "boiler", 105: "strong", 106: "pantry"},
    doors={
        BLUE: dict(home="balcony", thief=True),
        GREEN: dict(home="roof", lean="balcony"),
        YELLOW: dict(home="loft", lean="cellar"),
        VIOLET: dict(home="kennel", lean="suite"),
        PINK: dict(home="store", frame=106),
        RED: dict(home="exit", lean="strong"),
    },
    thief=dict(zone="yard", sees=("balcony", "roof", "loft")),
)
