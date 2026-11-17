"""The first secret level: "This Is Where We Came In" (MAP31), reached by
MAP10's secret way out.

A cinema with three halls, and no door to carry. Each hall is a fight that is
too much for one go. In its walls are time doors (a clock on them): through
one, the player is in a box behind glass, before the fight began, and watches
it from its start with their earlier self in it. When it comes to the moment
they left, the box's door opens onto the door they left by, and they go on
from there. Three boxes to a hall, each used once; what is in a box is all
that a trip gives. See src/zscript/time.zs and tools/ajartime.py.

- Where you leave is where you come back, with whatever was after you a step
  away; and what was right behind you comes into the box with you.
- From a box the whole hall is seen from above: what comes in later and
  where, and the tops of the tall blocks. In the great hall one of them has
  an arrow on it, at a piece of wall that opens: the level's secret.
- A room key lies in the second and third halls; cupboards in their boxes
  want it.
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
# was built in. A look changes textures, flats and light, and furnishes the
# foyer; nothing in a hall or a box is added, and nothing there moves.
LOOK = int(os.environ.get("AJAR_CINEMA") or "1")


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
BLOCK = 80                  # the tall blocks: too high to see over from the floor


def spots(kind, *at):
    for x, y in at:
        m.thing(x, y, kind)


class Hall:
    def __init__(self, k, x, y, w, h, blocks, *, ceil=256, light=190, last=False):
        self.k, self.x, self.y, self.w, self.h = k, x, y, w, h
        cx, cy = self.cx, self.cy = x + w // 2, y + h // 2
        W = "G" if ceil > 256 else "H"                  # the hall's wall is as tall as the hall
        if LOOK:
            light = gfx_cinema.LIGHT[LOOK]
        ajarmap.fitted(m, (x, y, x + w, y + h),
                       [((x + a, y + b, x + c, y + d), dict(floor=BLOCK, **look)) for (a, b, c, d), look in blocks],
                       ceil=ceil, light=light, **dress(wall=W, ftex="HF", ctex="HC"))
        ajartime.zone(m, k, 0, x, y, x + w, y + h, grow=72)
        # the way in: a step down
        m.sector(rect(cx - 128, y - 320, cx + 128, y), floor=UP, ceil=160, light=170,
                 **dress(wall="W", side="SP", ftex="FF", ctex="FC"))
        if LOOK:                                        # over the way in: the screen
            m.line((cx - 128, y), (cx + 128, y), upper=tx("SG" if W == "G" else "SC"), exact=True)
        ajartime.zone(m, k, 0, cx - 128, y - 128, cx + 128, y)
        # the time doors
        ajartime.hall_door(m, k, 1, (x, y + 96), (x, y + 160), (-1, 0), 0)
        ajartime.hall_door(m, k, 2, (x + w, y + h - 160), (x + w, y + h - 96), (1, 0), 0)
        ajartime.hall_door(m, k, 3, (x + 96, y + h), (x + 160, y + h), (0, 1), 0)
        over((x, y + 96), (x, y + 160), W)
        over((x + w, y + h - 160), (x + w, y + h - 96), W)
        over((x + 96, y + h), (x + 160, y + h), W)
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
            ajartime.box_door(m, k, n, da, db, u, BOXF)
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
            m.line(*self.on, special=243, playeruse=True, mid="AJEXIT", exact=True)

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

    def locker(self, n, key, *what):
        bx, by, du, dv = self.box[n]
        ang = {(1, 0): 180, (-1, 0): 0, (0, 1): 270, (0, -1): 90}[dv]         # facing into the box
        ajartime.locker(m, *self.spot(n, -10, 90), key, *what, angle=ang)


PLAIN = dress(side="BS", ftex="BT")
ARROW = dress(side="BS", ftex="BA") if LOOK else dict(ftex="AJARROW")

# === the foyer and the small hall ==========================================
h1 = Hall(1, 0, 0, 768, 704, [((192, 288, 256, 416), PLAIN), ((512, 288, 576, 416), PLAIN)])
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
spots(3001, *h1.at((128, 560), (384, 610), (640, 560), (260, 500), (500, 500)))
spots(9, *h1.at((384, 440), (100, 330), (668, 330)))
spots(3002, *h1.at((320, 250), (448, 250)))
ajartime.cue(m, 1, 1, 3, 3002, *h1.at((150, 200), (618, 200), (384, 560)))
ajartime.cue(m, 1, 1, 3, 3005, *h1.at((384, 352)))
ajartime.cue(m, 1, 2, 2, 69, *h1.at((384, 620), (384, 120)))
ajartime.cue(m, 1, 2, 2, 3005, *h1.at((120, 352), (648, 352)))
h1.stock(1, 2012, 2012, 2049, 2048)
h1.stock(2, 2012, 2012, 2049, 2048, 2011)
h1.stock(3, 2012, 2012, 2049, 2048, 2011, 2011)

# === the second hall: a room key, and a cupboard in the first two boxes ======
h2 = Hall(2, 3008, 0, 1024, 896, [((256, 256, 320, 384), PLAIN), ((704, 256, 768, 384), PLAIN),
                                  ((256, 512, 320, 640), PLAIN), ((704, 512, 768, 640), PLAIN)])
ajarmap.doorway(m, 1, h1.on[0], h1.on[1], (0, 1), 0,
                (h2.cx - 32, -320), (h2.cx + 32, -320), (0, -1), UP)
spots(82, (h2.cx, -200))                    # super shotgun
spots(2049, (h2.cx - 60, -200), (h2.cx + 60, -200))
spots(2048, (h2.cx - 60, -150))
spots(2012, (h2.cx + 60, -150))
ajarmap.key(m, 1, *h2.at((512, 800))[0])
spots(3001, *h2.at((128, 700), (896, 700), (400, 760), (624, 760), (128, 448), (896, 448)))
spots(65, *h2.at((512, 700), (180, 820), (844, 820), (512, 448)))
spots(69, *h2.at((400, 560), (624, 560)))
spots(66, *h2.at((288, 448), (736, 448)))
spots(3002, *h2.at((400, 300), (624, 300), (512, 200)))
ajartime.cue(m, 2, 1, 4, 67, *h2.at((200, 448), (824, 448)))
ajartime.cue(m, 2, 1, 4, 3002, *h2.at((400, 150), (624, 150), (400, 700), (624, 700)))
ajartime.cue(m, 2, 1, 4, 3005, *h2.at((512, 320), (512, 576)))
ajartime.cue(m, 2, 2, 3, 3003, *h2.at((400, 448), (624, 448)))
ajartime.cue(m, 2, 2, 3, 66, *h2.at((128, 200), (896, 200)))
ajartime.cue(m, 2, 2, 3, 64, *h2.at((512, 820)))
h2.stock(1, 2012, 2012, 2049, 2048)
h2.locker(1, 1, 2003, 2046)
h2.stock(2, 2012, 2012, 2049, 2046, 2011)
h2.locker(2, 1, 2003, 2046)
h2.stock(3, 2012, 2012, 2049, 2046, 2011, 2048)

# === the great hall: the arrow, the wall that opens, a room key ==============
h3 = Hall(3, 6016, 0, 1280, 1024, [((256, 256, 320, 384), PLAIN), ((960, 256, 1024, 384), PLAIN),
                                   ((256, 640, 320, 768), PLAIN), ((960, 640, 1024, 768), PLAIN),
                                   ((384, 448, 448, 512), ARROW), ((768, 448, 832, 576), PLAIN)],
          ceil=288, last=True)
ajarmap.doorway(m, 2, h2.on[0], h2.on[1], (0, 1), 0,
                (h3.cx - 32, -320), (h3.cx + 32, -320), (0, -1), UP)
spots(2004, (h3.cx, -200))                  # plasma rifle
spots(17, (h3.cx - 60, -200))
spots(2046, (h3.cx + 60, -200))
spots(2049, (h3.cx - 60, -150))
spots(2012, (h3.cx + 60, -150))
spots(2019, (h3.cx, -150))
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
spots(2006, (sx + 32, -80))
spots(17, (sx, -110), (sx + 64, -110))
ajarmap.key(m, 2, *h3.at((640, 930))[0])
spots(3001, *h3.at((128, 860), (1152, 860), (400, 900), (880, 900), (128, 512), (1152, 512), (540, 700), (740, 700)))
spots(65, *h3.at((640, 820), (200, 960), (1080, 960), (400, 600), (880, 600)))
spots(66, *h3.at((288, 512), (992, 512), (640, 640)))
spots(3005, *h3.at((400, 320), (880, 320), (640, 400), (640, 240)))
spots(69, *h3.at((520, 820), (760, 820), (640, 540)))
spots(67, *h3.at((160, 700), (1120, 700)))
ajartime.cue(m, 3, 1, 5, 68, *h3.at((150, 150), (1130, 150)))
ajartime.cue(m, 3, 1, 5, 69, *h3.at((340, 570), (880, 512), (640, 760)))
ajartime.cue(m, 3, 1, 5, 58, *h3.at((560, 160), (720, 160), (560, 880), (720, 880), (640, 320)))
ajartime.cue(m, 3, 2, 4, 3003, *h3.at((400, 400), (880, 400), (640, 860)))
ajartime.cue(m, 3, 2, 4, 64, *h3.at((640, 620)))
ajartime.cue(m, 3, 2, 4, 71, *h3.at((640, 200)))
ajartime.cue(m, 3, 2, 4, 66, *h3.at((128, 320), (1152, 320), (128, 900)))
ajartime.cue(m, 3, 3, 2, 16, *h3.at((640, 512)))
ajartime.cue(m, 3, 3, 2, 3001, *h3.at((200, 860), (1080, 860), (200, 160), (1080, 160)))
h3.stock(1, 2012, 2012, 17, 2046, 2011)
h3.locker(1, 2, 17, 2013)
h3.stock(2, 2012, 2012, 17, 2046, 2049, 2011)
h3.locker(2, 2, 2019, 17)
h3.stock(3, 2012, 2012, 17, 2046, 2049, 2011)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
