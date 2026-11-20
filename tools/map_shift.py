"""The lab map SHIFT: the first "Double Shift", built as MAP32 (PLAN.md,
"MAP32 \"Double Shift\", built") and kept as a lab when MAP32 was rebuilt
(tools/map_secret2.py). MAP=SHIFT ./run.sh; the tests are MAP=SHIFT MODE=3
and 4 tools/smoke.sh (src/zscript/shift.zs).

A works with three shops. Each shop is a fight too thick for one go: a pit
(the shop floor) under a gallery (the way in: a drop that cannot be climbed),
with time doors in the pit's walls (a clock on them) as in MAP31, and behind
glass the offices: the first trip out of a fight leads to the big one (the
wing), the next two to small ones with supplies.

Here doors are carried, and **what an earlier self did to a door is done
again** while the fight is watched (src/zscript/timedoor.zs). A door does not
go through a time door, and a door that joins the fight's shop to anywhere
is held shut while the fight is watched.

1. The fitting shop: meet yourself halfway. A TEAL leaf and the YELLOW door
   on the gallery, whose frame takes a TEAL leaf only; the twin and two
   frames in the wing. YELLOW opens onto the next shop and can be hung in
   the wing only. Hang the leaf, drop, step out of the fight, hang the twin:
   when the earlier self has hung its leaf and the fight is where it was
   left, gallery and wing are joined, and YELLOW can be fetched.
2. The press shop: a fight handed across. This one has to be won, and two
   arch-viles make it long. The wing has a frame and the GREEN door, which
   opens onto the lock-up: what is on the player's heels at a time door
   comes out into the wing with them, and can be led through GREEN and shut
   away. It is out of the fight then.
3. The despatch: one chain, two selves. The way out is MAP09's chain: RED
   on the gallery with one brass frame, BLUE in the wing with the other.
   Each self hangs one; the loop is closed when the earlier self hangs its
   own, and open when the fight is where it was left.

Nobody can be stuck: a fight that is won opens steel doors, in shops 1 and 3
a stair from the pit up to the gallery and a passage from the gallery to the
wing, so that everything can then be carried on foot. A fight that is left
unwon is over when the next one begins (AjarTimeHandler.Quit).
No solver. The level's own secret (the glass shows later) waits for MAP15's
mirrors.
"""
import ajarmap
import ajartime
from ajarmap import RED, BLUE, GREEN, YELLOW, TEAL, HOME, HOME2, far_id
from udmf import Map, rect

m = Map()
PIT = 0xD8DCE4
GAL = 0xE8E0D0
WING = 0xFFE8C0
GF = 64                     # the gallery's floor, and every office's, above the pit's
ANY = ajartime.hall_line(1, 1)      # a portal line that is there, for the targets nothing reads
BRASS = ("AJXA", "AJXAF")
FA, FB, FY, FG = 111, 112, 113, 114
BAD = []
RADIUS = {3001: 20, 9: 20, 65: 20, 3002: 30, 58: 30, 3005: 31, 69: 24, 3003: 24, 66: 20, 64: 20, 67: 48, 68: 64, 16: 40}


def steel(k, a, b, out, floor=0):
    """A steel door 16 thick in the wall a-b, shut until fight k is won."""
    c, d = (a[0] + out[0] * 16, a[1] + out[1] * 16), (b[0] + out[0] * 16, b[1] + out[1] * 16)
    m.sector([a, b, d, c], floor=floor, ceil=floor, light=160, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF",
             id=3090 + 100 * k)
    m.line(a, b, exact=True)
    m.line(c, d, exact=True)
    for p, q in ((a, c), (b, d)):
        m.line(p, q, mid="AJTRIM", dontpegbottom=True)


class Shop:
    """Fight k: a pit w by h with its south-west corner at x, y, the gallery
    along its south side, the wing (bw by bh) behind glass in its west wall
    and two small offices, north and east."""

    def __init__(self, k, x, y, w, h, pillars, bw=384, bh=384, light=190):
        self.k, self.x, self.y, self.w, self.h = k, x, y, w, h
        self.pillars, self.placed = pillars, {}
        cx, cy = self.cx, self.cy = x + w // 2, y + h // 2
        ajarmap.fitted(m, (x, y, x + w, y + h),
                       [((x + a, y + b, x + a + 64, y + b + 64), dict(floor=256)) for a, b in pillars],
                       ceil=256, light=light, color=PIT)
        m.sector(rect(x, y - 192, x + w, y), floor=GF, ceil=256, light=light + 10, color=GAL)
        ajartime.zone(m, k, 0, x, y - 192, x + w, y + h, grow=72)
        # the time doors: west (north of the wing), east, north
        ajartime.hall_door(m, k, 1, (x, y + h - 96), (x, y + h - 32), (-1, 0), 0, color=PIT)
        ajartime.hall_door(m, k, 2, (x + w, y + h - 160), (x + w, y + h - 96), (1, 0), 0, color=PIT)
        ajartime.hall_door(m, k, 3, (x + 96, y + h), (x + 160, y + h), (0, 1), 0, color=PIT)
        # the wing: office 1
        wx, wy = self.wx, self.wy = x - 16 - bw, y + 160
        assert wy + bh + 80 <= y + h - 96, "the west time door must be clear of the wing"
        self.bw, self.bh = bw, bh
        m.sector(rect(wx, wy, wx + bw, wy + bh), floor=GF, ceil=GF + 128, light=210, color=WING)
        gy = wy + bh // 2
        ajartime.glass(m, (x, gy - 80), (x, gy + 80), (-1, 0), GF)
        ajartime.box_door(m, k, 1, (wx + 96, wy + bh), (wx + 160, wy + bh), (0, 1), GF, color=WING)
        ajartime.zone(m, k, 1, wx, wy, wx + bw, wy + bh)
        ajartime.zone(m, k, 1, wx + 96, wy + bh, wx + 160, wy + bh + 64)
        # beside the glass, plates that wind the fight as it is watched: back
        # on the left of one who looks out (north), on on the right
        self.plates = {1: ((x - 18, gy + 96), (x - 18, gy - 96))}
        for side, (px, py) in zip((-1, 1), self.plates[1]):
            ajartime.wind(m, px, py, 180, side > 0)
        # the small offices
        self.box = {}
        for n, (bx, by, u) in ((2, (cx, y + h + 136, (0, 1))), (3, (x + w + 136, cy, (1, 0)))):
            v = (-u[1], u[0])
            self.box[n] = (bx, by, u, v)
            hw, hh = (120, 112) if u[0] else (112, 120)
            m.sector(rect(bx - hw, by - hh, bx + hw, by + hh), floor=GF, ceil=GF + 128, light=210, color=WING)
            g = (bx - u[0] * 136, by - u[1] * 136)
            ajartime.glass(m, (g[0] - v[0] * 80, g[1] - v[1] * 80), (g[0] + v[0] * 80, g[1] + v[1] * 80), u, GF)
            d = (bx + u[0] * 120, by + u[1] * 120)
            ajartime.box_door(m, k, n, (d[0] - v[0] * 32, d[1] - v[1] * 32), (d[0] + v[0] * 32, d[1] + v[1] * 32),
                              u, GF, color=WING)
            lo = (bx - u[0] * 135 - abs(v[0]) * 112, by - u[1] * 135 - abs(v[1]) * 112)
            hi = (bx + u[0] * 190 + abs(v[0]) * 112, by + u[1] * 190 + abs(v[1]) * 112)
            ajartime.zone(m, k, n, min(lo[0], hi[0]), min(lo[1], hi[1]), max(lo[0], hi[0]), max(lo[1], hi[1]))
            # the plates, as in MAP31's boxes
            self.plates[n] = tuple((bx - u[0] * 118 + v[0] * 96 * side, by - u[1] * 118 + v[1] * 96 * side)
                                   for side in (-1, 1))
            for side, (px, py) in zip((-1, 1), self.plates[n]):
                ajartime.wind(m, px, py, {(0, 1): 90, (1, 0): 0}[u], side > 0)

    def at(self, *pts):
        return [(self.x + a, self.y + b) for a, b in pts]

    def room_for(self, wave, kind, pts):
        """A monster must stand clear of the walls, the pillars and the others
        of its wave: one that does not never comes, and the fight is never won."""
        r = RADIUS[kind]
        for px, py in pts:
            if not (r + 8 <= px <= self.w - r - 8 and r + 8 <= py <= self.h - r - 8):
                BAD.append((self.k, wave, kind, px, py, "wall"))
            for a, b in self.pillars:
                if a - r < px < a + 64 + r and b - r < py < b + 64 + r:
                    BAD.append((self.k, wave, kind, px, py, "pillar"))
            for ox, oy, orr in self.placed.setdefault(wave, []):
                if max(abs(px - ox), abs(py - oy)) < r + orr:
                    BAD.append((self.k, wave, kind, px, py, "another", ox, oy))
            self.placed[wave].append((px, py, r))

    def first(self, kind, *pts):
        """The monsters the fight begins with: on the shop floor, facing the gallery."""
        self.room_for(1, kind, pts)
        for px, py in self.at(*pts):
            m.thing(px, py, kind, angle=270)

    def cue(self, wave, when, kind, *pts, **look):
        self.room_for(wave, kind, pts)
        ajartime.cue(m, self.k, wave, when, kind, *self.at(*pts), **look)

    def wing(self, u, v):
        """A place in the wing: u from its west wall, v from its south wall."""
        return self.wx + u, self.wy + v

    def stock(self, n, *kinds):
        """Things in small office n, from the back corners forward."""
        bx, by, du, dv = self.box[n]
        for kind, (u, v) in zip(kinds, ((70, -85), (70, 85), (20, -90), (-30, -90), (-75, -90), (-75, 90), (20, 0))):
            m.thing(bx + du[0] * u + dv[0] * v, by + du[1] * u + dv[1] * v, kind)

    def on_foot(self):
        """Won, the fight opens a stair from the pit up to the gallery (east)
        and a passage from the gallery to the wing (west)."""
        k, x, y, w = self.k, self.x, self.y, self.w
        steel(k, (x + w, y + 96), (x + w, y + 160), (1, 0))
        m.sector(rect(x + w + 16, y + 64, x + w + 144, y + 192), ceil=128, light=170, color=PIT)
        for i in range(1, 5):
            m.sector(rect(x + w + 16, y + 64 - 16 * i, x + w + 144, y + 80 - 16 * i), floor=16 * i, ceil=192,
                     light=170, color=PIT)
        m.sector(rect(x + w, y - 192, x + w + 144, y), floor=GF, ceil=192, light=180, color=GAL)
        steel(k, (x, y - 128), (x, y - 64), (-1, 0), GF)
        m.sector(rect(self.wx + 32, y - 128, x - 16, y - 64), floor=GF, ceil=GF + 128, light=170, color=WING)
        m.sector(rect(self.wx + 32, y - 64, self.wx + 96, self.wy), floor=GF, ceil=GF + 128, light=170, color=WING)

    def anteroom(self, depth=320):
        """The room the gallery is entered from, south of its middle; not
        part of the fight. Returns its south wall's middle."""
        m.sector(rect(self.cx - 128, self.y - 192 - depth, self.cx + 128, self.y - 192), floor=GF, ceil=GF + 128,
                 light=200, color=GAL)
        return self.cx, self.y - 192 - depth


def spots(kind, *at):
    for x, y in at:
        m.thing(x, y, kind)


# === 1. the fitting shop: meet yourself halfway ==============================
s1 = Shop(1, 0, 0, 1024, 768, ((256, 288), (704, 288), (480, 544)))
s1.on_foot()
ax, ay = s1.anteroom()
m.thing(ax, ay + 60, 1, angle=90)
spots(2001, (ax - 70, ay + 150))            # shotgun
spots(2002, (ax + 70, ay + 150))            # chaingun
spots(2049, (ax - 70, ay + 200), (ax - 30, ay + 200))
spots(2048, (ax + 70, ay + 200), (ax + 30, ay + 200))
spots(2018, (ax, ay + 240))                 # armour
# the gallery: its frame takes a TEAL leaf and nothing else; a leaf and YELLOW lean by it
ajarmap.recess(m, (160, -192), (224, -192), (0, -1), GF, FA, ANY, home=TEAL, only=3, color=GAL)
ajarmap.pair(m, TEAL, (300, -150, 90), s1.wing(60, 320) + (0,))
ajarmap.door(m, YELLOW, 80, -150, angle=90)
spots(82, (700, -100))                      # super shotgun
spots(2049, (760, -100), (820, -100))
# the wing: the twin's frame in its west wall, a frame for YELLOW in its south wall
ajarmap.recess(m, (s1.wx, s1.wy + 160), (s1.wx, s1.wy + 224), (-1, 0), GF, FB, ANY, color=WING)
ajarmap.recess(m, (s1.wx + 192, s1.wy), (s1.wx + 256, s1.wy), (0, -1), GF, FY, ANY, color=WING)
spots(2012, s1.wing(330, 330), s1.wing(330, 290))
spots(2049, s1.wing(330, 60))
s1.first(3001, *[(140 + 110 * i, 680) for i in range(8)])                   # imps along the far wall
s1.first(9, (120, 500), (904, 500), (120, 400), (904, 400))                 # shotgun guys down the sides
s1.first(3002, (400, 440), (624, 440), (400, 340), (624, 340))              # demons, the middle
s1.first(65, (200, 620), (824, 620))
s1.first(3005, (380, 580), (512, 250))
s1.cue(2, 8, 69, (160, 300), (160, 420), (160, 560))                        # hell knights, the west
s1.cue(2, 8, 66, (864, 300), (864, 420), (864, 560), angle=180)             # revenants, the east
s1.cue(3, 5, 67, (380, 680), (644, 680), angle=270)
s1.cue(3, 5, 3001, (200, 200), (824, 200), (200, 680), (824, 680))
s1.cue(3, 5, 3005, (512, 480), (512, 160))
s1.stock(2, 2012, 2012, 2049, 2048, 2018, 2003, 2046)                       # the rocket launcher is in an office
s1.stock(3, 2012, 2012, 2049, 2046, 2018, 2046)

# === 2. the press shop: a fight handed across ================================
s2 = Shop(2, 3072, 0, 1280, 896, ((320, 320), (896, 320), (608, 608)), bw=320, bh=320)
ax, ay = s2.anteroom()
ajarmap.recess(m, (ax - 32, ay), (ax + 32, ay), (0, -1), GF, far_id(YELLOW), ANY, far_colour=YELLOW, color=GAL)
spots(2003, (ax - 70, ay + 120))            # rocket launcher
spots(2046, (ax - 70, ay + 170), (ax - 30, ay + 170), (ax + 30, ay + 170))
spots(2049, (ax + 70, ay + 120), (ax + 70, ay + 170))
spots(2012, (ax - 90, ay + 240), (ax + 90, ay + 240))
spots(2019, (ax, ay + 240))                 # blue armour
# the wing: a frame, and GREEN, which opens onto the lock-up
ajarmap.recess(m, (s2.wx, s2.wy + 128), (s2.wx, s2.wy + 192), (-1, 0), GF, FG, ANY, color=WING)
ajarmap.door(m, GREEN, *s2.wing(200, 270), angle=180)      # clear of the plate behind it
spots(2012, s2.wing(270, 50), s2.wing(230, 50))
spots(2046, s2.wing(60, 50))
# the lock-up: a room with a pillar to run round, and nothing else leads there
LX, LY = 3072, -2048
ajarmap.fitted(m, (LX, LY, LX + 448, LY + 448), [((LX + 192, LY + 192, LX + 256, LY + 256), dict(floor=160))],
               ceil=160, light=150, color=0xC8D0E0)
ajarmap.recess(m, (LX + 192, LY), (LX + 256, LY), (0, -1), 0, far_id(GREEN), ANY, far_colour=GREEN)
s2.first(3001, *[(160 + 120 * i, 800) for i in range(9)], (640, 700))
s2.first(65, (120, 600), (1160, 600), (120, 300), (1160, 300))
s2.first(69, (500, 640), (780, 640), (500, 520), (780, 520))
s2.first(3002, (440, 260), (840, 260), (560, 260), (720, 260))
s2.first(3005, (640, 460), (400, 700), (880, 700))
# remembered by: two arch-viles, with whatever is left to raise
s2.cue(2, 10, 64, (300, 800), (980, 800), angle=270, always=True)
s2.cue(2, 10, 66, (200, 460), (200, 560), (1080, 460), (1080, 560))
s2.cue(3, 6, 67, (640, 800), (240, 240), (1040, 240), angle=270)
s2.cue(3, 6, 3003, (540, 420), (740, 420), angle=270)
s2.cue(3, 6, 58, (300, 640), (980, 640), (240, 440), (1040, 440))
s2.cue(3, 6, 3001, (160, 180), (1120, 180), (160, 720), (1120, 720), (640, 180), (640, 560))
s2.stock(2, 2012, 2012, 2046, 2049, 2018, 2046)
s2.stock(3, 2012, 2012, 2046, 2048, 2018, 2013)
# the way on: a steel door in the east wall, a lobby, and a doorway to the despatch
steel(2, (s2.x + s2.w, 96), (s2.x + s2.w, 160), (1, 0))
m.sector(rect(s2.x + s2.w + 16, 32, s2.x + s2.w + 208, 224), ceil=128, light=180, color=GAL)

# === 3. the despatch: one chain, two selves ==================================
s3 = Shop(3, 6144, 0, 1280, 1024, ((320, 352), (896, 352), (608, 672), (256, 800), (960, 800)))
s3.on_foot()
ax, ay = s3.anteroom()
ajarmap.doorway(m, 1, (s2.x + s2.w + 208, 96), (s2.x + s2.w + 208, 160), (1, 0), 0,
                (ax - 32, ay), (ax + 32, ay), (0, -1), GF)
spots(2004, (ax - 70, ay + 120))            # plasma rifle
spots(17, (ax - 70, ay + 170), (ax - 30, ay + 170), (ax + 30, ay + 170))
spots(2046, (ax + 70, ay + 120), (ax + 70, ay + 170), (ax + 30, ay + 120))
spots(83, (ax, ay + 240))                   # megasphere
spots(8, (ax - 90, ay + 240))               # a backpack
# the chain: a brass frame on the gallery, RED by it; the other in the wing, BLUE by it
gx = s3.x
ajarmap.recess(m, (gx + 160, -192), (gx + 224, -192), (0, -1), GF, HOME, ANY, trim=BRASS, home=far_id(RED),
               chain=(far_id(BLUE), HOME2), color=GAL)
ajarmap.recess(m, (s3.wx, s3.wy + 160), (s3.wx, s3.wy + 224), (-1, 0), GF, HOME2, ANY, trim=BRASS, home=far_id(RED),
               chain=(far_id(BLUE), HOME), color=WING)
ajarmap.door(m, RED, gx + 300, -150, angle=90)
ajarmap.door(m, BLUE, *s3.wing(60, 320), angle=0)
ajarmap.way_through(m, 6144, -2048, RED, BLUE)
spots(2012, s3.wing(330, 330), s3.wing(330, 290))
spots(17, s3.wing(330, 60))
s3.first(3001, *[(140 + 100 * i, 920) for i in range(11)], (640, 820))
s3.first(65, (120, 700), (1160, 700), (120, 480), (1160, 480), (120, 260), (1160, 260))
s3.first(66, (480, 760), (800, 760), (480, 640), (800, 640))
s3.first(69, (520, 500), (760, 500), (520, 380), (760, 380))
s3.first(3005, (640, 560), (420, 820), (860, 820), (640, 240))
s3.cue(2, 12, 3003, (200, 900), (1080, 900), (640, 900), angle=270)
s3.cue(2, 12, 58, (300, 560), (980, 560), (300, 300), (980, 300))
s3.cue(2, 12, 67, (200, 620), (1080, 620), (640, 820))
s3.cue(2, 12, 64, (640, 440), always=True)
# remembered by: a cyberdemon in the middle of the floor
s3.cue(3, 6, 16, (640, 600), angle=270, always=True)
s3.cue(3, 6, 68, (240, 240), (1040, 240), angle=90)
s3.cue(3, 6, 66, (160, 940), (260, 940), (1020, 940), (1120, 940))
s3.stock(2, 2012, 2012, 17, 2046, 2018, 2046, 17)
s3.stock(3, 2012, 2012, 17, 2046, 2018, 2011, 2046)

assert not BAD, BAD
# a plate is clear of what is in its box: a door, a frame's mark, a supply
for s in (s1, s2, s3):
    for n, plates in s.plates.items():
        for px, py in plates:
            near = [t for t in m.things if t["type"] not in (ajartime.WIND_T, ajartime.ZONE_T)
                    and abs(t["x"] - px) < 40 and abs(t["y"] - py) < 40]
            assert not near, (s.k, n, px, py, near)
        # and a door that leans in the wing is not between a plate and the room
        for px, py in plates:
            for t in m.things:
                if t["type"] == ajarmap.DOOR_T and abs(t["y"] - py) < 48 and 0 < px - t["x"] < 100:
                    assert False, (s.k, n, px, py, t)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
