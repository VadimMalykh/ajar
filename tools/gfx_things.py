"""What stands in MAP07's rooms as sprites: the telescope on its pier (AJTE,
sixteen sides), the planetarium's projector (AJPJ), an orrery (AJOY) and a
globe (AJGB), eight sides each. And in MAP08's: two shop's dummies (AJMQ,
AJMG), a rocking horse (AJRH), a till (AJTL) and rolled carpets (AJCR).

Each is a model of a few solids (tubes, balls, rings), drawn once from every
side: its surfaces are scattered with points, and each point is shaded and
put on the picture if nothing nearer is there already. A model faces +x; one
unit is one map unit. Its origin is where it stands. The engine draws
everything a fifth taller than it is wide (Doom's pixels), so a picture is
drawn a fifth taller than the model and the actor squeezes it back (TALL;
YScale in AjarExhibit): a ball then stays round on the screen.
"""
import math
import random

from gfx import Img, shade

TALL = 1.2
BRONZE, GILT, CREAM, IRON, WALNUT = (156, 112, 60), (224, 184, 90), (226, 214, 184), (52, 54, 62), (84, 54, 38)


def _unit(v):
    d = math.sqrt(sum(x * x for x in v))
    return tuple(x / d for x in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Model:
    def __init__(self):
        self.pts = []                 # (x, y, z, nx, ny, nz, colour, shine)

    def tube(self, p0, p1, r, c, r1=None, shine=0.5, step=0.6, caps=(True, True), paint=None):
        """A tube from p0 to p1, radius r (r1 at p1: a cone). `paint(t, c)`
        gives the colour at t units along it."""
        r1 = r if r1 is None else r1
        axis = tuple(b - a for a, b in zip(p0, p1))
        length = math.sqrt(sum(x * x for x in axis))
        u = _unit(axis)
        e1 = _unit(_cross(u, (0, 0, 1) if abs(u[2]) < 0.9 else (1, 0, 0)))
        e2 = _cross(u, e1)
        nt = max(2, int(length / step))
        for i in range(nt + 1):
            t = length * i / nt
            rad = r + (r1 - r) * i / nt
            col = paint(t, c) if paint else c
            na = max(6, int(2 * math.pi * rad / step))
            for k in range(na):
                a = 2 * math.pi * k / na
                ca, sa = math.cos(a), math.sin(a)
                n = tuple(ca * e1[j] + sa * e2[j] for j in range(3))
                self.pts.append((p0[0] + u[0] * t + n[0] * rad, p0[1] + u[1] * t + n[1] * rad,
                                 p0[2] + u[2] * t + n[2] * rad, n[0], n[1], n[2], col, shine))
        for end, p, rad, sign in ((0, p0, r, -1), (1, p1, r1, 1)):
            cap = caps[end]
            if not cap:
                continue
            col = cap if isinstance(cap, tuple) else c
            d = 0.0
            while d <= rad:
                na = max(1, int(2 * math.pi * d / step))
                for k in range(na):
                    a = 2 * math.pi * k / na
                    ca, sa = math.cos(a) * d, math.sin(a) * d
                    self.pts.append((p[0] + ca * e1[0] + sa * e2[0], p[1] + ca * e1[1] + sa * e2[1],
                                     p[2] + ca * e1[2] + sa * e2[2], u[0] * sign, u[1] * sign, u[2] * sign, col, shine))
                d += step

    def ball(self, centre, r, c, shine=0.5, step=0.6, paint=None):
        """`paint(n, c)` gives the colour where the surface faces n."""
        nl = max(4, int(math.pi * r / step))
        for i in range(nl + 1):
            lat = -math.pi / 2 + math.pi * i / nl
            cl, sl = math.cos(lat), math.sin(lat)
            na = max(1, int(2 * math.pi * r * cl / step))
            for k in range(na):
                a = 2 * math.pi * k / na
                n = (cl * math.cos(a), cl * math.sin(a), sl)
                self.pts.append((centre[0] + n[0] * r, centre[1] + n[1] * r, centre[2] + n[2] * r,
                                 n[0], n[1], n[2], paint(n, c) if paint else c, shine))

    def ring(self, centre, axis, big, r, c, shine=0.6, step=0.6):
        """A ring of radius `big` round `axis`, of wire r thick."""
        u = _unit(axis)
        e1 = _unit(_cross(u, (0, 0, 1) if abs(u[2]) < 0.9 else (1, 0, 0)))
        e2 = _cross(u, e1)
        for i in range(int(2 * math.pi * big / step)):
            a = i * step / big
            out = tuple(math.cos(a) * e1[j] + math.sin(a) * e2[j] for j in range(3))
            for k in range(max(6, int(2 * math.pi * r / step))):
                b = 2 * math.pi * k / max(6, int(2 * math.pi * r / step))
                n = tuple(math.cos(b) * out[j] + math.sin(b) * u[j] for j in range(3))
                self.pts.append((centre[0] + out[0] * big + n[0] * r, centre[1] + out[1] * big + n[1] * r,
                                 centre[2] + out[2] * big + n[2] * r, n[0], n[1], n[2], c, shine))

    def sprites(self, out, name, sides):
        """Writes sprites/<name>A<side>.png for `sides` (8 or 16) sides."""
        half = int(max(math.hypot(p[0], p[1]) for p in self.pts)) + 2
        top = int(max(p[2] for p in self.pts) * TALL) + 2
        low = int(min(p[2] for p in self.pts) * TALL)
        w, h = 2 * half, top - low
        codes = "12345678" if sides == 8 else "192A3B4C5D6E7F8G"
        for s in range(sides):
            al = 2 * math.pi * s / sides                      # where the one who looks stands, round from the front
            ca, sa = math.cos(al), math.sin(al)
            lx, ly, lz = _unit((-0.45, 0.62, 0.64))           # the light, in the picture's own right, up, towards
            depth, colour = {}, {}
            for x, y, z, nx, ny, nz, c, shine in self.pts:
                toward = nx * ca + ny * sa
                if toward < -0.05:
                    continue
                key = (int(half - x * sa + y * ca), int(top - z * TALL))
                d = x * ca + y * sa
                if depth.get(key, -1e9) >= d:
                    continue
                depth[key] = d
                lit = max(0.0, (-nx * sa + ny * ca) * lx + nz * ly + toward * lz)
                f = (0.34 + 0.8 * lit) * (0.62 + 0.38 * min(1.0, max(0.0, toward) * 3))
                col = shade(c, f)
                if shine and lit > 0.9:
                    k = (lit - 0.9) * 10 * shine
                    col = tuple(int(v + (255 - v) * k) for v in col)
                colour[key] = col
            im = Img(w, h, (0, 0, 0, 0))
            for (px, py), col in colour.items():
                im.set(px, py, col)
            out[f"sprites/{name}A{codes[s]}.png"] = im.png(grab=(half, top))


def telescope():
    """A refractor on a fork, pointing forwards and up out of the dome's slit."""
    m = Model()
    el = math.radians(40)
    u, up = (math.cos(el), 0, math.sin(el)), (-math.sin(el), 0, math.cos(el))
    pivot = (0, 0, 92)

    def at(t, lift=0.0, side=0.0):
        return (pivot[0] + u[0] * t + up[0] * lift, pivot[1] + side, pivot[2] + u[2] * t + up[2] * lift)

    m.tube((0, 0, 0), (0, 0, 10), 30, BRONZE, r1=27)
    m.tube((0, 0, 10), (0, 0, 54), 15, IRON, r1=11)
    m.tube((0, -24, 58), (0, 24, 58), 7, IRON)
    for side in (-21, 21):                                           # the fork
        m.tube((0, side, 56), (0, side, 104), 5, IRON, caps=(True, True))
    m.tube((0, -27, 92), (0, 27, 92), 4, BRONZE)                     # the axle
    m.ring((0, 24, 92), (0, 1, 0), 15, 1.5, GILT)                    # the circle it is set by

    def enamel(t, c):
        return BRONZE if t < 6 or 62 < t < 78 or t > 196 else c
    m.tube(at(-68), at(140), 14, CREAM, paint=enamel, caps=(True, False))
    m.tube(at(136), at(160), 16.5, BRONZE, caps=(False, (26, 34, 70)))       # the dew cap, and the glass in it
    m.tube(at(-90), at(-68), 6, BRONZE)                              # the eyepiece
    m.tube(at(-100), at(-90), 3.5, IRON)
    m.tube(at(-40, 20), at(44, 20), 4, BRONZE, caps=(True, (26, 34, 70)))    # the finder
    for t in (-30, 34):
        m.tube(at(t, 12), at(t, 18), 2.5, IRON)
    return m


def projector():
    """The planetarium's: two balls of lenses on a lattice stand."""
    m = Model()
    r = random.Random(1401)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.tube((22 * sx, 22 * sy, 8), (6 * sx, 6 * sy, 66), 2.4, IRON, step=0.5)
    m.tube((0, 0, 0), (0, 0, 8), 30, WALNUT, r1=28)
    for z in (28, 48):                                               # the lattice's ties
        k = 22 - 16 * (z - 8) / 58
        for a, b in (((-k, -k), (k, -k)), ((k, -k), (k, k)), ((k, k), (-k, k)), ((-k, k), (-k, -k))):
            m.tube((a[0], a[1], z), (b[0], b[1], z), 1.4, IRON, step=0.5)
    m.ball((0, 0, 70), 8, BRONZE)
    el = math.radians(32)
    v, c = (math.cos(el), 0, math.sin(el)), (0, 0, 80)
    lenses = [_unit((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1))) for _ in range(46)]

    def eyes(n, col):
        best = max(n[0] * d[0] + n[1] * d[1] + n[2] * d[2] for d in lenses)
        return (196, 214, 236) if best > 0.9955 else BRONZE if best > 0.99 else col
    for s in (-1, 1):
        m.ball(tuple(c[j] + v[j] * 36 * s for j in range(3)), 17, (34, 36, 46), paint=eyes)
        m.tube(tuple(c[j] + v[j] * 14 * s for j in range(3)), tuple(c[j] + v[j] * 24 * s for j in range(3)), 12, BRONZE)
    m.tube(tuple(c[j] - v[j] * 22 for j in range(3)), tuple(c[j] + v[j] * 22 for j in range(3)), 8, IRON)
    return m


def orrery():
    """The sun, four planets on their arms, and the ring of the year round them."""
    m = Model()
    m.tube((0, 0, 0), (0, 0, 5), 17, WALNUT, r1=15)
    m.tube((0, 0, 5), (0, 0, 40), 2.6, BRONZE, step=0.5)
    m.ball((0, 0, 46), 8.5, (244, 196, 84), shine=0.9)
    planets = ((15, 0.6, 2.6, (150, 120, 96)), (23, 2.5, 3.6, (196, 150, 84)), (31, 4.4, 3.8, (70, 120, 176)),
               (40, 5.6, 5.2, (176, 96, 64)))
    for k, (rad, a, size, col) in enumerate(planets):
        z = 36 - 5 * k
        end = (rad * math.cos(a), rad * math.sin(a))
        m.tube((0, 0, z), (end[0], end[1], z), 0.9, BRONZE, step=0.4)
        m.tube((end[0], end[1], z), (end[0], end[1], 46 - size), 0.9, BRONZE, step=0.4)
        m.ball((end[0], end[1], 46), size, col, step=0.45)
    m.ring((0, 0, 37), (0, 0, 1), 46, 1.3, GILT, step=0.5)
    for a in range(0, 360, 90):                                      # what carries the ring
        x, y = 46 * math.cos(math.radians(a + 45)), 46 * math.sin(math.radians(a + 45))
        m.tube((x * 0.3, y * 0.3, 8), (x, y, 36), 0.9, BRONZE, step=0.4)
    return m


def globe():
    """The earth, leaning in a brass meridian."""
    m = Model()
    r = random.Random(1402)
    lands = [(_unit((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 0.7))), r.uniform(0.78, 0.95)) for _ in range(11)]
    tilt = math.radians(23)
    pole = (math.sin(tilt), 0, math.cos(tilt))

    def earth(n, col):
        lat = n[0] * pole[0] + n[2] * pole[2]
        if abs(lat) > 0.93:
            return (226, 230, 232)
        east = math.atan2(n[1], n[0] * pole[2] - n[2] * pole[0])
        if abs((math.degrees(math.asin(lat)) + 90) % 30 - 15) > 14.2 or abs(math.degrees(east) % 30 - 15) > 14.2:
            return shade(col, 0.6)
        land = any(n[0] * d[0] + n[1] * d[1] + n[2] * d[2] > k for d, k in lands)
        return (176, 150, 92) if land else col
    m.tube((0, 0, 0), (0, 0, 5), 15, WALNUT, r1=13)
    m.tube((0, 0, 5), (0, 0, 22), 3, BRONZE, step=0.5)
    m.ball((0, 0, 48), 22, (52, 86, 124), paint=earth, shine=0.7)
    m.ring((0, 0, 48), (0, 1, 0), 25, 1.5, GILT)
    m.ring((0, 0, 48), (0, 0, 1), 26.5, 1.2, BRONZE)                 # the horizon ring
    for a in (45, 135, 225, 315):
        x, y = 26.5 * math.cos(math.radians(a)), 26.5 * math.sin(math.radians(a))
        m.tube((0, 0, 20), (x, y, 48), 1.0, BRONZE, step=0.4)
    return m


# --- MAP08: what a department store has standing about ----------------------------
SKIN, CORAL, TURQ, CHAR, GREY = (226, 200, 170), (226, 112, 92), (60, 164, 164), (50, 52, 58), (170, 174, 180)


def _stand(m):
    m.tube((0, 0, 0), (0, 0, 2), 11, GREY, r1=10)


def mannequin():
    """A shop's dummy in a dress, on its stand."""
    m = Model()
    _stand(m)
    m.tube((0, 0, 2), (0, 0, 16), 1.5, GREY, caps=(False, False))

    def hem(t, c):
        return (236, 234, 226) if t < 2.5 else c
    m.tube((0, 0, 14), (0, 0, 48), 15, CORAL, r1=5.5, paint=hem, caps=((120, 56, 46), False))     # the skirt
    m.tube((0, 0, 47), (0, 0, 50), 5.8, CHAR, caps=(False, False))                                # a belt
    m.tube((0, 0, 50), (0, 0, 62), 5.5, CORAL, r1=8.5, caps=(False, False))
    m.tube((0, 0, 62), (0, 0, 68), 8.5, CORAL, r1=6.5, caps=(False, True))
    m.tube((0, 0, 68), (0, 0, 74), 2.6, SKIN, caps=(False, False))
    m.ball((0, 0, 79), 5.6, SKIN, shine=0.8)
    for side in (-1, 1):                                                                         # arms, a little out
        m.ball((0, 8.6 * side, 65), 2.6, CORAL)
        m.tube((0, 8.8 * side, 65), (2, 12.5 * side, 50), 2.2, SKIN, r1=1.9, caps=(False, False))
        m.tube((2, 12.5 * side, 50), (6, 13.5 * side, 38), 1.9, SKIN, r1=1.5)
    return m


def gentleman():
    """And one in a suit."""
    m = Model()
    _stand(m)
    for side in (-1, 1):
        m.tube((0, 4 * side, 2), (0, 4.4 * side, 42), 3.4, CHAR, r1=4.2, caps=((20, 20, 24), False))
        m.ball((0, 9.4 * side, 65), 3, CHAR)
        m.tube((0, 9.6 * side, 65), (1, 11.5 * side, 50), 2.8, CHAR, r1=2.5, caps=(False, False))
        m.tube((1, 11.5 * side, 50), (3, 11.5 * side, 38), 2.5, CHAR, r1=2.2, caps=(False, SKIN))
        m.ball((3.4, 11.5 * side, 36.5), 2, SKIN)

    def shirt(t, c):
        return c
    m.tube((0, 0, 40), (0, 0, 54), 8.6, CHAR, r1=8, caps=(True, False))                           # the jacket
    m.tube((0, 0, 54), (0, 0, 68), 8, CHAR, r1=9.4, caps=(False, True))
    for z in (46, 52):
        m.ball((8.2, 0, z), 0.9, GREY)                                                           # buttons
    m.tube((7, 0, 58), (8.4, 0, 67), 1.6, (236, 234, 226), r1=2.6, caps=(False, False))           # shirt front
    m.tube((8.2, 0, 58), (9, 0, 66), 0.8, CORAL, caps=(True, False))                              # a tie
    m.tube((0, 0, 68), (0, 0, 74), 2.8, SKIN, caps=(False, False))
    m.ball((0, 0, 79), 5.8, SKIN, shine=0.8)
    m.tube((0, 0, 82.5), (0, 0, 83.5), 8.5, CHAR)                                                 # a hat
    m.tube((0, 0, 83.5), (0, 0, 89), 5.6, CHAR, r1=5)
    return m


def rocking_horse():
    """A dapple grey on red rockers."""
    m = Model()
    r = random.Random(1403)
    spots = [_unit((r.gauss(0, 1), r.gauss(0, 1), r.gauss(0, 1))) for _ in range(14)]
    grey, red, dark = (214, 212, 206), (190, 50, 44), (60, 50, 48)

    def body(t, c):
        return red if 9 < t < 17 else c
    m.tube((-13, 0, 28), (12, 0, 28), 7, grey, paint=body)
    m.tube((9, 0, 31), (17, 0, 45), 4.6, grey, r1=3.6, caps=(False, False))                       # the neck
    m.tube((14, 0, 46), (26, 0, 40), 4, grey, r1=2.6)                                             # the head
    for side in (-1, 1):
        m.tube((15, 2 * side, 48), (14, 2.4 * side, 53), 1.2, grey, r1=0.4)                       # ears
        m.ball((21, 3 * side, 44), 0.9, dark)
        for x0, x1 in ((9, 15), (-10, -16)):                                                     # legs
            m.tube((x0, 4.5 * side, 24), (x1, 6 * side, 5), 2, grey, r1=1.5, caps=(False, dark))
        pts = [(38 * math.sin(math.radians(a)), 6 * side, 41 - 38 * math.cos(math.radians(a))) for a in range(-36, 37, 6)]
        for a, b in zip(pts, pts[1:]):                                                           # a rocker
            m.tube(a, b, 1.5, red, step=0.5)
    for x in (-16, 16):
        m.tube((x, -6, 5.5), (x, 6, 5.5), 1.2, red, step=0.5)
    m.tube((10, 0, 35), (16, 0, 48), 1.4, dark, caps=(False, False))                              # the mane
    m.tube((-13, 0, 30), (-21, 0, 17), 2.2, dark, r1=0.8)                                         # the tail
    m.tube((-2, -7.4, 30), (-2, 7.4, 30), 1.2, dark)                                              # the saddle's girth
    return m


def till():
    """A cash register: enamel, a row of keys, the price in its window."""
    m = Model()
    cream, key = (226, 214, 184), (30, 30, 34)

    def box(lo, hi, c, shine=0.5, step=0.5):
        for axis in range(3):
            u, v = [k for k in range(3) if k != axis]
            for sign, at in ((-1, lo[axis]), (1, hi[axis])):
                a = lo[u]
                while a <= hi[u]:
                    b = lo[v]
                    while b <= hi[v]:
                        p, n = [0, 0, 0], [0, 0, 0]
                        p[axis], p[u], p[v], n[axis] = at, a, b, sign
                        m.pts.append((p[0], p[1], p[2], n[0], n[1], n[2], c, shine))
                        b += step
                    a += step
    box((-9, -9, 0), (10, 9, 8), TURQ)                                                           # the drawer
    box((-9, -9, 8), (1, 9, 22), TURQ)
    box((1, -9, 8), (10, 9, 11), cream)
    for i, x in enumerate((3, 5.5, 8)):                                                          # keys, in three rows
        for y in range(-7, 8, 2):
            m.ball((x, y, 12.2 - 0.4 * i), 0.8, key if (y + i) % 3 else (190, 50, 44), step=0.4)
    box((-8, -7, 22), (-1, 7, 28), cream)                                                        # the window
    box((-0.8, -5.5, 23.5), (-0.6, 5.5, 26.5), (26, 30, 40))
    m.tube((-4, 9, 14), (-4, 12, 14), 1, GREY)                                                    # the handle
    m.tube((-4, 12, 14), (-4, 12, 21), 0.9, GREY)
    m.ball((-4, 12, 22), 1.6, key)
    return m


def carpets():
    """Rolled carpets stood on end."""
    m = Model()
    rolls = ((0, 0, 9, 84, (150, 50, 60), (220, 190, 120)), (15, 6, 7.5, 70, (50, 80, 120), (210, 200, 180)),
             (-8, 14, 8, 92, (190, 150, 80), (120, 50, 40)), (-14, -7, 7, 64, (60, 120, 100), (226, 214, 184)),
             (8, -13, 8, 76, (110, 60, 110), (220, 180, 90)))
    for x, y, rad, h, c, band in rolls:
        def woven(t, col, band=band, h=h):
            return band if t % 14 < 2.5 else shade(col, 0.8) if t > h - 3 else col
        m.tube((x, y, 0), (x, y, h), rad, c, paint=woven, caps=(False, shade(c, 0.55)))
        m.tube((x, y, h - 0.4), (x, y, h), rad * 0.45, (226, 214, 184), caps=(False, (200, 190, 160)))   # its felt back, rolled in
    return m


def make(out):
    mannequin().sprites(out, "AJMQ", 8)
    gentleman().sprites(out, "AJMG", 8)
    rocking_horse().sprites(out, "AJRH", 8)
    till().sprites(out, "AJTL", 8)
    carpets().sprites(out, "AJCR", 8)
    telescope().sprites(out, "AJTE", 16)
    projector().sprites(out, "AJPJ", 8)
    orrery().sprites(out, "AJOY", 8)
    globe().sprites(out, "AJGB", 8)


if __name__ == "__main__":                                           # python3 tools/gfx_things.py <folder>: the pictures
    import os
    import sys
    pics = {}
    make(pics)
    for name, data in pics.items():
        with open(os.path.join(sys.argv[1], os.path.basename(name)), "wb") as f:
            f.write(data)
