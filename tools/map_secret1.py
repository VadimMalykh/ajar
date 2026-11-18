"""The first secret level: "This Is Where We Came In" (MAP31), reached by
MAP10's secret way out.

A cinema with three halls, and no door to carry. Each hall is a fight that is
too much for one go. In its walls are time doors (a clock on them): through
one, the player is in a box behind glass, before the fight began, and watches
it from its start with their earlier self in it. When it comes to the moment
they left, the box's door opens onto the door they left by, and they go on
from there. That is the first hall. In the second and third the box's door
is open at once: the fight begins again, and they fight it beside their
earlier selves (time.zs, "the open fight"). Three boxes to a hall, each used
once; what is in a box is all that a trip gives. See src/zscript/time.zs and tools/ajartime.py.

- Where you leave is where you come back, with whatever was after you a step
  away; and what was right behind you comes into the box with you.
- From a box the whole hall is seen from above: what comes in later and
  where. For cover a hall has pillars and banks of raked seats (sheer at the
  back and sides). In the great hall one bank has an arrow on its top, at a
  piece of wall that opens: the level's secret.
- A room key lies in the second and third halls; cupboards in their boxes
  want it.
- Each fight has something to remember it by, that is seen again from the
  box: hall 1 an arch-vile and then two more (the answers are in its boxes:
  rocket launcher, BFG), hall 2 a cyberdemon early.
- A hall is entered by a step down that cannot be climbed, and left by a
  steel door that opens when nothing in it is left alive.
"""
import os

import ajarmap
import ajartime
from udmf import Map, rect

m = Map()
# The cinema's look (gfx_cinema.py): 1 Palace (the 1930s), 2 Kino (the 1960s),
# 3 Fleapit (the 1980s); AJAR_CINEMA=0 is the level in the plain textures it
# was built in. Vadim chose 3 (2026-11-18). A look changes textures, flats and
# light, furnishes the foyer and puts rows of seats in the halls (low steps
# that everything walks over); nothing in a hall or a box moves.
LOOK = int(os.environ.get("AJAR_CINEMA") or "3")


def tx(part):
    return f"AJY{part}{LOOK}"


def dress(**parts):
    """Sector properties for the look: wall="H" is the look's texture H."""
    return {k: tx(v) for k, v in parts.items()} if LOOK else {}


def over(a, b, part, **k):
    """The wall over (and under) the opening a-b carries on as the look's
    wall `part`, in line with the wall beside it."""
    if LOOK:
        m.line(a, b, upper=tx(part), dontpegtop=True, **k)


if LOOK:
    import gfx_cinema
    m.align |= gfx_cinema.ALIGNED
BOXF = 64                   # a box's floor above its hall's
UP = 32                     # the way into a hall, above its floor
SEAT, BACK = 12, 24         # a row of seats: its seats and their backs. Nothing is more than a step (24)
ROW, PITCH = 32, 96         # a row is 32 deep (20 of seat, 12 of back), one every 96


def rows(k, x, y, w, h):
    """The seats of hall k, facing the screen (south): two banks either side
    of a middle aisle 128 wide, 96 from the walls, the first row 192 from the
    screen. In look 3 some seats are gone. As fitted()'s features."""
    import random
    rnd = random.Random(31 + k)
    out = []
    for ry in range(192, h - 96 - ROW + 1, PITCH):
        for x1, x2 in ((96, w // 2 - 64), (w // 2 + 64, w - 96)):
            gone = set()
            if LOOK == 3 and rnd.random() < 0.45:
                at = rnd.randrange(x1, x2, 32)
                gone = {at + 32 * i for i in range(rnd.randrange(1, 4))}
            for sx in range(x1, x2, 32):
                if sx not in gone:
                    out.append(((x + sx, y + ry, x + sx + 32, y + ry + 20),
                                dict(floor=SEAT, **dress(ftex="SF", side="SS"))))
                    out.append(((x + sx, y + ry + 20, x + sx + 32, y + ry + ROW),
                                dict(floor=BACK, **dress(ftex="SF", side="SB"))))
    return out


def first(k, kind, *at):
    """The monsters hall k's fight begins with. The hall is empty until the
    screen has counted down; then they come in, facing the way in."""
    ajartime.cue(m, k, 1, 0, kind, *at, angle=270)


ARROW = dress(side="BS", ftex="BA") if LOOK else dict(ftex="AJARROW")


def pillar(x, y):
    """A square pillar to the ceiling, 64 by 64, in the hall's wall (Hall()
    makes it so): cover, and plainly part of the building."""
    return [((x, y, x + 64, y + 64), dict(pillar=True))]


def platform(x, y, arrow=False):
    """A bank of raked seats, 192 square, rising away from the screen: three
    rows, each 24 higher than the one before, with a walk behind each, and a
    plain rim either side. Every step is 12, so everything walks up it from
    the front; its back and sides are sheer (72 at the back): cover. From a
    box its top is seen. `arrow`: the middle of the top row is a bare patch
    with the arrow on it."""
    out = []
    for i in range(3):
        base, ya = 24 * i, y + 64 * i
        out.append(((x, ya, x + 192, ya + 64), dict(floor=base + 24, **dress(side="BS"))))        # the rim, the walk
        for sx in range(x + 32, x + 160, 32):
            if arrow and i == 2 and x + 64 <= sx < x + 128:
                continue
            out.append(((sx, ya, sx + 32, ya + 20), dict(floor=base + SEAT, **dress(ftex="SF", side="SS"))))
            out.append(((sx, ya + 20, sx + 32, ya + ROW), dict(floor=base + BACK, **dress(ftex="SF", side="SB"))))
    if arrow:
        out.append(((x + 64, y + 128, x + 128, y + 192), dict(floor=72, **ARROW)))
    return out


def spots(kind, *at):
    for x, y in at:
        m.thing(x, y, kind)


class Hall:
    def __init__(self, k, x, y, w, h, blocks, *, ceil=256, light=190, last=False, open=False):
        self.k, self.x, self.y, self.w, self.h = k, x, y, w, h
        cx, cy = self.cx, self.cy = x + w // 2, y + h // 2
        W = "G" if ceil > 256 else "H"                  # the hall's wall is as tall as the hall
        seats = []
        if LOOK:
            # the lights are down: the hall is dark but for what the screen
            # throws on the floor before it; then the seats
            light = gfx_cinema.LIGHT[LOOK]
            seats = [((x, y, x + w, y + 96), dict(light=light + 40)),
                     ((x, y + 96, x + w, y + 192), dict(light=light + 20))] + rows(k, x, y, w, h)
        if k == 1:
            # the big screen, for the reel when all is over (time.zs): a slice
            # of the hall before the way in whose ceiling comes down, 512 wide;
            # what a camera sees is on its face. Until then it is not there.
            seats = seats + [((cx - 256, y, cx + 256, y + 8), dict(id=ajartime.REEL_TAG))]
            m.line((cx - 256, y + 8), (cx + 256, y + 8), upper="AJREEL", exact=True, lit=255)
            m.thing(cx, y + 420, 14, angle=270, id=ajartime.REEL_TAG)        # where the last way out leads: a seat for it
        ajarmap.fitted(m, (x, y, x + w, y + h), seats +
                       [((x + a, y + b, x + c, y + d), dict(floor=ceil, **dress(side=W)) if look.get("pillar") else look)
                        for (a, b, c, d), look in blocks],
                       ceil=ceil, light=light, id=ajartime.show_tag(k), **dress(wall=W, ftex="HF", ctex="HC"))
        ajartime.zone(m, k, 0, x, y, x + w, y + h, grow=72, open=open)
        # the way in: a step down
        m.sector(rect(cx - 128, y - 320, cx + 128, y), floor=UP, ceil=160, light=170,
                 **dress(wall="W", side="SP", ftex="FF", ctex="FC"))
        if LOOK:                                        # over the way in: the screen, lit; time.zs counts down on it
            m.line((cx - 128, y), (cx + 128, y), upper=tx("R0" if ceil > 256 else "Q0"), exact=True, lit=255,
                   id=ajartime.show_tag(k))
        ajartime.zone(m, k, 0, cx - 128, y - 128, cx + 128, y)
        # the time doors
        # the time doors: in a look their surround is dark, and so is a
        # lintel in the wall over them
        dark = dict(trim=(tx("TT"), tx("TT"))) if LOOK else {}
        ajartime.hall_door(m, k, 1, (x, y + 96), (x, y + 160), (-1, 0), 0, **dark)
        ajartime.hall_door(m, k, 2, (x + w, y + h - 160), (x + w, y + h - 96), (1, 0), 0, **dark)
        ajartime.hall_door(m, k, 3, (x + 96, y + h), (x + 160, y + h), (0, 1), 0, **dark)
        over((x, y + 96), (x, y + 160), "T" + W)
        over((x + w, y + h - 160), (x + w, y + h - 96), "T" + W)
        over((x + 96, y + h), (x + 160, y + h), "T" + W)
        # the boxes: west, north, east. Each is (its middle, the way from the
        # hall to its back, the way along its glass)
        self.box = {}
        for n, (bx, by, u) in enumerate(((x - 136, cy, (-1, 0)), (cx, y + h + 136, (0, 1)), (x + w + 136, cy, (1, 0))), 1):
            v = (-u[1], u[0])
            self.box[n] = (bx, by, u, v)
            hw, hh = (120, 112) if u[0] else (112, 120)
            m.sector(rect(bx - hw, by - hh, bx + hw, by + hh), floor=BOXF, ceil=BOXF + 128, light=210,
                     **dress(wall="B", ftex="BF", ctex="BC"))
            g = (bx - u[0] * 136, by - u[1] * 136)
            ga, gb = (g[0] - v[0] * 80, g[1] - v[1] * 80), (g[0] + v[0] * 80, g[1] + v[1] * 80)
            ajartime.glass(m, ga, gb, u, BOXF, **(dict(trim=(tx("GT"), tx("GT"))) if LOOK else {}))
            d = (bx + u[0] * 120, by + u[1] * 120)
            da, db = (d[0] - v[0] * 32, d[1] - v[1] * 32), (d[0] + v[0] * 32, d[1] + v[1] * 32)
            ajartime.box_door(m, k, n, da, db, u, BOXF, **dark)
            if LOOK:
                # the wall under and over the glass is the hall's on the
                # hall's side and the box's on the box's; the glass has a
                # frame, and is clear inside it
                over(ga, gb, W, lower=tx(W), dontpegbottom=True)
                ia, ib = (ga[0] + u[0] * 16, ga[1] + u[1] * 16), (gb[0] + u[0] * 16, gb[1] + u[1] * 16)
                over(ia, ib, "B", lower=tx("B"), dontpegbottom=True, mid=tx("GL"), midboth=True)
                over(da, db, "B")
            # the zone: the box, its glass, and the recess and stub of its door
            lo = (bx - u[0] * 135 - abs(v[0]) * 112, by - u[1] * 135 - abs(v[1]) * 112)
            hi = (bx + u[0] * 190 + abs(v[0]) * 112, by + u[1] * 190 + abs(v[1]) * 112)
            ajartime.zone(m, k, n, min(lo[0], hi[0]), min(lo[1], hi[1]), max(lo[0], hi[0]), max(lo[1], hi[1]))
        # the way on: a steel door in the north wall, shut until the fight is won
        a, b = (x + w - 192, y + h), (x + w - 128, y + h)
        c, d = (a[0], a[1] + 16), (b[0], b[1] + 16)
        m.sector([a, b, d, c], floor=0, ceil=0, light=160, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF",
                 id=3090 + 100 * k)
        m.line(a, b, exact=True)
        m.line(c, d, exact=True)
        if LOOK:                                        # the door is let into the wall of each side
            m.line(a, b, upper=tx("D" + W))
            m.line(c, d, upper=tx("DL"))
        for p, q in ((a, c), (b, d)):
            m.line(p, q, mid="AJTRIM", dontpegbottom=True)
        m.sector(rect(x + w - 256, y + h + 16, x + w - 64, y + h + 208), ceil=128, light=180,
                 **dress(wall="L", ftex="LF", ctex="LC"))
        self.on = ((x + w - 192, y + h + 208), (x + w - 128, y + h + 208))        # the lobby's north wall
        if LOOK and not last:                           # over the way on: the next hall's name
            m.line(*self.on, upper=f"AJYN{LOOK}{k + 1}")
        if LOOK and k > 1:                              # the arch you come in by
            over((cx - 32, y - 320), (cx + 32, y - 320), "W")
        if last:
            m.cut(*self.on)
            # the way out leads back to the first hall, for the reel; the level ends after it
            m.line(*self.on, special=70, args=(ajartime.REEL_TAG,), playeruse=True, repeatspecial=True, mid="AJEXIT", exact=True)

    def at(self, *pts):
        return [(self.x + a, self.y + b) for a, b in pts]

    def spot(self, n, u, v):
        """A place in box n: u from its middle towards its back, v along its glass."""
        bx, by, du, dv = self.box[n]
        return bx + du[0] * u + dv[0] * v, by + du[1] * u + dv[1] * v

    def stock(self, n, *kinds):
        """Things in box n, from the back corners forward."""
        for kind, (u, v) in zip(kinds, ((70, -85), (70, 85), (20, -90), (-30, -90), (-75, -90), (-75, 90))):
            m.thing(*self.spot(n, u, v), kind)

    def ammo(self, n, *kinds):
        """More for box n, on the floor in its middle: ammunition for a
        player who came out of the fight with little left."""
        for kind, (u, v) in zip(kinds, ((20, -40), (20, 0), (20, 40), (-30, -40), (-30, 0), (-30, 40))):
            m.thing(*self.spot(n, u, v), kind)

    def locker(self, n, key, *what):
        bx, by, du, dv = self.box[n]
        ang = {(1, 0): 180, (-1, 0): 0, (0, 1): 270, (0, -1): 90}[dv]         # facing into the box
        ajartime.locker(m, *self.spot(n, -10, 90), key, *what, angle=ang)


# === the foyer and the small hall ==========================================
# The halls are big, and a fight is short and thick: its monsters come in
# kinds, each kind in its own part of the hall, and the next wave comes while
# half of the last is still alive, so that they are in each other's fire and
# fight each other. (A fight that is long is long to watch again from a box.)
h1 = Hall(1, -192, 0, 1152, 960, pillar(256, 352) + pillar(832, 352) + platform(192, 576) + platform(768, 576))
if LOOK:
    # the foyer: a runner from the street doors to the way in, lamps, the box
    # office (shut) on the west wall, a bench on the east, posters of the
    # town's other places
    ajarmap.fitted(m, (64, -768, 704, -320),
                   [((352, -768, 416, -320), dress(ftex="RG"))] +
                   [((x, y, x + 64, y + 64), dress(ctex="FL")) for x in (192, 512) for y in (-640, -512)] +
                   [((64, -656, 96, -528), dict(floor=UP + 40, **dress(ftex="CT", side="CS"))),
                    ((672, -640, 704, -512), dict(floor=UP + 16, **dress(ftex="BE", side="BE")))],
                   floor=UP, ceil=192, light=200, **dress(wall="F", ftex="FF", ctex="FC"))
    for a, b, part in (((64, -656), (64, -528), "BO"), ((320, -768), (448, -768), "ST"),
                       ((96, -320), (160, -320), "PA"), ((160, -320), (224, -320), "PB"),
                       ((544, -320), (608, -320), "PC"), ((608, -320), (672, -320), "PD"),
                       ((704, -496), (704, -432), "PE"), ((704, -432), (704, -368), "PF")):
        m.cut(a, b)
        m.line(a, b, mid=tx(part), exact=True)
    m.line((256, -320), (512, -320), upper=f"AJYN{LOOK}1", exact=True)
else:
    m.sector(rect(64, -768, 704, -320), floor=UP, ceil=192, light=200)
m.thing(384, -640, 1, angle=90)
spots(2001, (300, -480))                    # shotgun
spots(2002, (468, -480))                    # chaingun
spots(2049, (300, -430), (340, -430))       # boxes of shells
spots(2048, (468, -430), (428, -430))       # boxes of bullets
spots(2018, (384, -400))                    # armour
first(1, 3001, *h1.at((112, 860), (184, 860), (256, 860), (112, 790), (184, 790), (256, 790)))       # imps, north-west
first(1, 9, *h1.at((1040, 860), (968, 860), (896, 860), (1040, 790)))                               # shotgun guys, north-east
first(1, 3002, *h1.at((480, 560), (672, 560), (480, 460), (672, 460)))                              # demons, the middle
first(1, 65, *h1.at((100, 480), (1052, 480)))                                                       # a chaingunner at each side
first(1, 3005, *h1.at((576, 700), (576, 300)))
# What the fight is remembered by, and seen again from a box: an arch-vile
# comes while the first monsters are still about (it raises them), and there
# is nothing in the player's hands for it: the rocket launcher is in the first
# box. With it come hell knights down the west side and revenants down the
# east, across the hall from each other. Then two more arch-viles: the BFG is
# in the second box.
ajartime.cue(m, 1, 2, 10, 64, *h1.at((576, 860)), angle=270, always=True)
ajartime.cue(m, 1, 2, 10, 69, *h1.at((120, 300), (120, 400), (120, 600)))
ajartime.cue(m, 1, 2, 10, 66, *h1.at((1032, 300), (1032, 400), (1032, 600)), angle=180)
ajartime.cue(m, 1, 3, 6, 64, *h1.at((200, 200), (952, 200)), always=True)
ajartime.cue(m, 1, 3, 6, 67, *h1.at((400, 860), (752, 860)), angle=270)
ajartime.cue(m, 1, 3, 6, 3005, *h1.at((576, 500), (400, 400), (752, 400)))
h1.stock(1, 2003, 2046, 2046, 2012, 2049, 2048)
h1.stock(2, 2006, 17, 2012, 2012, 2046, 2049)
h1.stock(3, 2012, 2012, 2046, 17, 2049, 2011)
# ammunition in every box (Vadim: he came out of the fights too weak):
# shells, bullets, and rockets and cells for what the boxes gave
h1.ammo(1, 2049, 2048, 2048)
h1.ammo(2, 2049, 2048, 2046, 17)
h1.ammo(3, 2049, 2048, 2046, 17)

# === the second hall: a room key, and a cupboard in the first two boxes ======
h2 = Hall(2, 2752, 0, 1536, 1216, pillar(384, 352) + pillar(1088, 352) + platform(320, 736) + platform(1024, 736),
          open=True)        # the box's door is open from the start: the fight is fought again, beside oneself
ajarmap.doorway(m, 1, h1.on[0], h1.on[1], (0, 1), 0,
                (h2.cx - 32, -320), (h2.cx + 32, -320), (0, -1), UP)
spots(82, (h2.cx, -200))                    # super shotgun
spots(2049, (h2.cx - 60, -200), (h2.cx + 60, -200))
spots(2048, (h2.cx - 60, -150))
spots(2012, (h2.cx + 60, -150))
# for having come through a fight: a megasphere, and something for the
# rocket launcher and the BFG that hall 1's boxes gave
spots(83, (h2.cx, -100))
spots(2046, (h2.cx - 60, -100))
spots(17, (h2.cx + 60, -100))
ajarmap.key(m, 1, *h2.at((768, 1140))[0])
first(2, 3001, *h2.at(*[(200 + 160 * i, 1080) for i in range(8)]))                                  # imps along the far wall
first(2, 65, *h2.at((120, 608), (1416, 608), (120, 300), (1416, 300)))                              # chaingunners down the sides
first(2, 69, *h2.at((600, 900), (936, 900), (600, 760), (936, 760)))                                # hell knights, the middle
first(2, 66, *h2.at((200, 800), (200, 900), (300, 800), (300, 900)))                                # revenants, the west
first(2, 3005, *h2.at((768, 500), (600, 400), (936, 400), (768, 300)))
first(2, 3002, *h2.at((500, 250), (1036, 250), (650, 250), (886, 250)))
# remembered by: a cyberdemon in the middle of the hall, in the thick of them
ajartime.cue(m, 2, 2, 14, 16, *h2.at((768, 608)), angle=270, always=True)
ajartime.cue(m, 2, 2, 14, 67, *h2.at((1300, 800), (1300, 950), (1300, 500)), angle=180)             # mancubi, the east
ajartime.cue(m, 2, 2, 14, 68, *h2.at((220, 200), (1316, 200)), angle=90)
ajartime.cue(m, 2, 3, 8, 64, *h2.at((768, 1080)), angle=270, always=True)
ajartime.cue(m, 2, 3, 8, 3003, *h2.at((500, 608), (1036, 608), (768, 900)), angle=270)
ajartime.cue(m, 2, 3, 8, 71, *h2.at((768, 300)))
ajartime.cue(m, 2, 3, 8, 66, *h2.at((1300, 1000), (1300, 1100), (1200, 1100)), angle=180)
h2.stock(1, 2012, 2012, 2049, 2046, 2046)
h2.locker(1, 1, 2046, 17)
h2.stock(2, 2012, 2012, 2049, 2046, 2011)
h2.locker(2, 1, 17, 2013)
h2.stock(3, 2012, 2012, 2049, 2046, 2011, 17)
for n in (1, 2, 3):
    h2.ammo(n, 2049, 2049, 2048, 2046, 17)

# === the great hall: the arrow, the wall that opens, a room key ==============
h3 = Hall(3, 5696, 0, 1920, 1472, pillar(448, 352) + pillar(1408, 352) + pillar(1216, 704) +
          platform(384, 992) + platform(1344, 992) + platform(320, 576, arrow=True),
          ceil=288, last=True, open=True)       # an open fight, as hall 2 is
ajarmap.doorway(m, 2, h2.on[0], h2.on[1], (0, 1), 0,
                (h3.cx - 32, -320), (h3.cx + 32, -320), (0, -1), UP)
spots(2004, (h3.cx, -200))                  # plasma rifle
spots(17, (h3.cx - 60, -200))
spots(2046, (h3.cx + 60, -200))
spots(2049, (h3.cx - 60, -150))
spots(2012, (h3.cx + 60, -150))
spots(83, (h3.cx, -150))                    # megasphere (it was blue armour)
spots(2046, (h3.cx - 60, -100))
spots(17, (h3.cx + 60, -100))
# the wall the arrow points at: straight south of its block. It opens with
# USE, from the hall only; behind it the level's one secret.
sx = h3.x + 384
a, b = (sx, 0), (sx + 64, 0)
c, d = (sx, -16), (sx + 64, -16)
m.sector([a, b, d, c], floor=0, ceil=0, light=160, ftex="AJTRIMF", ctex="AJTRIMF", id=3399)
m.line(a, b, special=11, args=(3399, 32), playeruse=True, exact=True)
for p, q in ((a, c), (b, d)):
    m.line(p, q, mid="AJTRIM", dontpegbottom=True)
m.sector(rect(sx - 32, -144, sx + 96, -16), ceil=128, light=220, special=1024, **dress(wall="C", ftex="LF", ctex="LC"))
if LOOK:                                    # shut, it is the wall of each side
    m.line(a, b, upper=tx("G"))
    m.line(c, d, upper=tx("C"))
spots(83, (sx + 32, -80))                   # megasphere (the BFG is in hall 1's second box now)
spots(17, (sx, -110), (sx + 64, -110))
ajarmap.key(m, 2, *h3.at((960, 1420))[0])
first(3, 3001, *h3.at(*[(160 + 170 * i, 1360) for i in range(10)]))                                 # imps along the far wall
first(3, 65, *h3.at((120, 736), (1800, 736), (120, 400), (1800, 400), (120, 1100), (1800, 1100)))   # chaingunners down the sides
first(3, 66, *h3.at((700, 1000), (1220, 1000), (700, 900), (1220, 900)))
first(3, 3005, *h3.at((960, 600), (760, 500), (1160, 500), (860, 350), (1060, 350)))
first(3, 69, *h3.at((800, 1200), (1120, 1200), (800, 1100), (1120, 1100)))
first(3, 67, *h3.at((300, 900), (1620, 900)))
ajartime.cue(m, 3, 2, 16, 68, *h3.at((250, 250), (1670, 250), (960, 250)), angle=90)
ajartime.cue(m, 3, 2, 16, 69, *h3.at((250, 1250), (350, 1250), (250, 1150)))
ajartime.cue(m, 3, 2, 16, 58, *h3.at((860, 160), (1060, 160), (860, 1300), (1060, 1300), (960, 480)))
ajartime.cue(m, 3, 2, 16, 71, *h3.at((960, 900)))
ajartime.cue(m, 3, 3, 10, 3003, *h3.at((600, 600), (1320, 600), (960, 1250), (960, 400)), angle=270)
ajartime.cue(m, 3, 3, 10, 64, *h3.at((200, 736), (1720, 736)), always=True)
ajartime.cue(m, 3, 3, 10, 66, *h3.at((1620, 1250), (1720, 1250), (1620, 1150)), angle=180)
# remembered by: two cyberdemons at once, with whatever is left around them
ajartime.cue(m, 3, 4, 6, 16, *h3.at((760, 736), (1100, 736)), angle=270, always=True)
ajartime.cue(m, 3, 4, 6, 3001, *h3.at((200, 1300), (1720, 1300), (200, 160), (1720, 160)))
h3.stock(1, 2012, 2012, 17, 2046, 2011)
h3.locker(1, 2, 17, 2013)
h3.stock(2, 2012, 2012, 17, 2046, 2049, 2011)
h3.locker(2, 2, 2019, 17)
h3.stock(3, 2012, 2012, 17, 2046, 2049, 2011)
for n in (1, 2, 3):
    h3.ammo(n, 2049, 2049, 2048, 2046, 17, 17)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
