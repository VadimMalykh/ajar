"""MAP20's look, "Municipal" (PLAN.md, "Look: MAP20, Municipal"): a town waterworks and public baths built
around 1900-1930, older than the institute that took it over. Warm and neutral only (glazed white and cream,
oxblood, black, brick red, maroon iron, brass, buff stone, soot): the level's doors are BLUE, GREEN and TEAL
and its water is blue, so nothing else is.

Every name is AJV... The map (tools/map_highwater.py) says what it needs:
  WALLS  {name: dict(H, z0, mat, ...)}: a wall texture 64 wide and H high whose row 0 stands at the absolute
         height z0 (the map's line hook lays it so on every side, whatever the sector): so a course, a tide
         line or a stain is at one height on every wall of a room, seen from any floor. Its pattern is a
         function of the absolute height and of x mod 64, symmetric left to right, so that walls laid by world
         position (udmf's align) show no seams. `mat` picks the painter below.
  PICS   {name: dict(kind, w, H, z0, base, shift, ...)}: a picture or a plate on a piece of wall w wide, drawn
         over its wall texture `base` (`shift`: where in its 64 the wall stands at the picture's left edge).
Flats (64 x 64, laid by the world's grid): FQ red quarry tile, KP plaster, FP the plunge's tile, KG iron
trusses and glass, FB the bath's tile (with a lane line), FC red and black quarry tile, KB boards on iron
beams, FW chequer plate, FS concrete with silt and a drain, FR brick paving, FT riveted plate, FG granite
setts, FL dry grass, FK stone flags, FD timber boards, FO wet brick, KO a brick vault, KR dark plate.
"""
import math

import gfx_institute                            # (its letters: J, Z and the full stop)
import gfx_cinema                               # (its K, W and X)
from gfx import DIGITS, Img, shade, text
from gfx_bus import blend
from gfx_water import digit_text

DIGITS.update({":": ("00000", "00100", "00000", "00100", "00000"),
               "'": ("00100", "00100", "00000", "00000", "00000"),
               ",": ("00000", "00000", "00000", "00100", "01000"),
               "Q": ("01110", "10001", "10101", "10010", "01101")})

CREAM_TILE, CREAM_PL, OXBLOOD, BLACK = (230, 220, 190), (224, 212, 182), (112, 32, 30), (34, 32, 32)
WHITE_TILE, MAROON, CREAM_BR, BRICK = (234, 234, 226), (104, 36, 36), (214, 202, 168), (150, 68, 48)
ENG, GRANITE, BUFF, IRON = (84, 42, 38), (140, 134, 124), (198, 176, 132), (62, 56, 54)
RUST, BRASS, LIME, SOOT, PAPER = (122, 68, 38), (200, 164, 82), (218, 214, 198), (30, 26, 24), (232, 222, 196)


def h32(x, z, s=0):
    """A number in [0, 1) for a place (x, z) and a seed: the same wherever the place is drawn."""
    v = (x * 73856093) ^ (z * 19349663) ^ (s * 83492791) ^ 0x5bd1e995
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    return ((v ^ (v >> 16)) & 0xffff) / 65536


def jit(c, x, z, s, amt):
    return shade(c, 1 + (h32(x, z, s) - 0.5) * 2 * amt)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Wall:
    """An image whose row r stands at the absolute height z0 - r (its top edge); column c at x = shift + c."""

    def __init__(self, w, H, z0, shift=0):
        self.w, self.H, self.z0, self.shift = w, H, z0, shift
        self.im = Img(w, H)

    def r(self, z):
        return self.z0 - z

    def rows(self, ztop, zbot):
        return range(max(0, self.z0 - ztop), min(self.H, self.z0 - zbot))

    def fill(self, ztop, zbot, fn):
        for r in self.rows(ztop, zbot):
            z = self.z0 - r
            for c in range(self.w):
                self.im.set(c, r, fn((self.shift + c) % 64, z))

    def tint(self, ztop, zbot, fn):
        """fn(x, z, colour) -> colour, over what is drawn."""
        for r in self.rows(ztop, zbot):
            z = self.z0 - r
            for c in range(self.w):
                p = self.im.px[r * self.w + c]
                self.im.px[r * self.w + c] = list(fn((self.shift + c) % 64, z, tuple(p[:3]))) + [255]

    def at(self, c, z, col, a=1.0):
        r = self.z0 - z
        if 0 <= r < self.H and 0 <= c < self.w:
            if a >= 1:
                self.im.set(c, r, col)
            else:
                blend(self.im, c, r, col, a)

    def rect(self, c1, ztop, c2, zbot, col):
        """Columns c1..c2 (exclusive), heights ztop down to zbot (exclusive)."""
        for r in self.rows(ztop, zbot):
            for c in range(max(0, c1), min(self.w, c2)):
                self.im.set(c, r, col)

    def frame(self, c1, ztop, c2, zbot, col, t=1):
        self.rect(c1, ztop, c2, ztop - t, col)
        self.rect(c1, zbot + t, c2, zbot, col)
        self.rect(c1, ztop, c1 + t, zbot, col)
        self.rect(c2 - t, ztop, c2, zbot, col)

    def disc(self, cx, cz, rad, col):
        for z in range(int(cz - rad) - 1, int(cz + rad) + 2):
            for c in range(int(cx - rad) - 1, int(cx + rad) + 2):
                if (c + 0.5 - cx) ** 2 + (z - 0.5 - cz) ** 2 <= rad * rad:
                    self.at(c, z, col)

    def ring(self, cx, cz, r1, r2, col):
        for z in range(int(cz - r2) - 1, int(cz + r2) + 2):
            for c in range(int(cx - r2) - 1, int(cx + r2) + 2):
                d = math.hypot(c + 0.5 - cx, z - 0.5 - cz)
                if r1 <= d <= r2:
                    self.at(c, z, col)

    def text(self, s, c, ztop, col, scale=1):
        """Capitals with their top at the height ztop (the 5x5 face, 6 to a letter)."""
        im = Img(len(s) * 6 * scale, 5 * scale, (0, 0, 0, 0))
        text(im, s, 0, 0, col, scale)
        self._paste(im, c, ztop)

    def digits(self, s, c, ztop, col, scale=1):
        """Figures in the 3x5 face, 4 to a figure."""
        im = Img(len(s) * 4 * scale, 5 * scale, (0, 0, 0, 0))
        digit_text(im, s, 0, 0, col, scale)
        self._paste(im, c, ztop)

    def _paste(self, im, c, ztop):
        for y in range(im.h):
            for x in range(im.w):
                p = im.px[y * im.w + x]
                if p[3]:
                    self.at(c + x, ztop - y, p[:3])

    def centre(self, s, cx, ztop, col, scale=1):
        self.text(s, cx - (len(s) * 6 * scale - scale) // 2, ztop, col, scale)


# === what walls are made of: f(x, z) -> colour, z the top edge of a row, x mod 64 ===================
def tile(c, s=16, grout=0.74, var=0.035, seed=1):
    def f(x, z):
        if x % s == 0 or z % s == 0:
            return jit(shade(c, grout), x, z, seed + 9, 0.02)
        k = h32(x // s, (z - 1) // s, seed)
        g = 1 + (k - 0.5) * 2 * var + (0.05 if (z % s == s - 1 or x % s == 1) else 0)
        return jit(shade(c, g), x, z, seed, 0.012)
    return f


def brick(c, mortar=(176, 166, 148), course=8, length=32, var=0.08, seed=2):
    def f(x, z):
        kz = (z - 1) // course
        off = length // 2 if kz % 2 else 0
        if z % course == 0 or (x + off) % length == 0:
            return jit(mortar, x, z, seed + 5, 0.05)
        k = h32((x + off) // length, kz, seed)
        g = 1 + (k - 0.5) * 2 * var
        if z % course == course - 1:
            g *= 0.9
        return jit(shade(c, g), x, z, seed, 0.04)
    return f


def painted_brick(c, seed=3):
    return brick(c, shade(c, 0.86), var=0.02, seed=seed)


def plate(c, seam=64, seed=4, rust=0.0):
    """Riveted iron plate: a seam at every multiple of `seam` and at x 0, rivets along them every 8."""
    def f(x, z):
        m = z % seam
        if m == 0 or x == 0:
            return shade(c, 0.55)
        if m == 1 or x == 1 or x == 63:
            return shade(c, 1.25 if m == 1 else 0.8)
        if (m in (5, seam - 4) and x % 8 == 4) or (x in (5, 59) and m % 8 == 4):
            return shade(c, 1.45)
        if (m in (4, seam - 5) and x % 8 == 4) or (x in (4, 58) and m % 8 == 5):
            return shade(c, 0.6)
        g = 1 + 0.05 * math.sin(x * math.pi / 32) + (h32(x // 4, z // 6, seed) - 0.5) * 0.06
        col = shade(c, g)
        if rust and h32(x, z // 3, seed + 1) < rust:
            col = mix(col, RUST, 0.5)
        return col
    return f


def ashlar(c, course=32, seed=5):
    def f(x, z):
        kz = (z - 1) // course
        if z % course == 0 or (x + (32 if kz % 2 else 0)) % 64 == 0:
            return jit(shade(c, 0.7), x, z, seed + 3, 0.04)
        k = h32((x + (32 if kz % 2 else 0)) // 64, kz, seed)
        g = 1 + (k - 0.5) * 0.12 + (0.06 if z % course == course - 1 else 0)
        return jit(shade(c, g), x // 2, z // 2, seed, 0.05)
    return f


def plaster(c, seed=6):
    return lambda x, z: jit(c, x // 2, z // 2, seed, 0.025)


def flat_band(c, light=1.25, dark=0.6):
    """A band with a lit top row and a dark bottom row: give it (ztop, zbot)."""
    def make(ztop, zbot):
        def f(x, z):
            if z == ztop:
                return shade(c, light)
            if z == zbot + 1:
                return shade(c, dark)
            return jit(c, x, z, 11, 0.03)
        return f
    return make


def boards(c, w=8, seed=7):
    """Horizontal planks w high, a post at x 0."""
    def f(x, z):
        if x in (0, 63, 1):
            return shade(c, 0.55 if x == 0 else 0.75)
        if z % w == 0:
            return shade(c, 0.6)
        k = h32(0, (z - 1) // w, seed)
        g = 1 + (k - 0.5) * 0.2 + 0.05 * math.sin(x * 0.35 + k * 9)
        return jit(shade(c, g), x, z, seed, 0.03)
    return f


# === weather ===================================================================================
def stain(w, level, bottom, c=(70, 60, 48), strength=0.45, edge=6, seed=8):
    """Darker and browner below `level`, its edge wavering a little; pale streaks of lime down from it."""
    def f(x, z, col):
        e = level - int(h32(x // 3, 0, seed) * edge)
        if z > e:
            if z > level + 2 and h32(x, 0, seed + 1) < 0.08 and z < level + 2 + int(h32(x, 1, seed) * 30):
                return mix(col, (120, 100, 70), 0.25)       # a run of wet above the mark
            return col
        t = strength * (1 - 0.25 * (z - bottom) / max(1, level - bottom))
        col = mix(col, c, t)
        if h32(x, 7, seed + 2) < 0.12 and z > e - 6 - int(h32(x, 8, seed) * 80):
            col = mix(col, LIME, 0.35)                      # limescale run down the wall
        return col
    w.tint(level + 40, bottom - 1, f)


def crust(w, level, seed=9):
    """The line the water stood at: a pale crust two or three rows deep, ragged."""
    def f(x, z, col):
        d = level - z
        thick = 2 + int(h32(x // 2, 3, seed) * 3)
        if 0 <= d < thick:
            return jit(LIME, x, z, seed, 0.06)
        if d == thick:
            return shade(col, 0.7)
        return col
    w.tint(level + 1, level - 8, f)


def soot(w, zfrom, ztop, most=0.6, seed=10):
    def f(x, z, col):
        t = most * min(1, max(0, (z - zfrom) / max(1, ztop - zfrom))) ** 1.3
        t *= 0.85 + 0.3 * h32(x // 4, z // 16, seed)
        return mix(col, SOOT, min(1, t))
    w.tint(ztop, zfrom, f)


# === the walls =================================================================================
def m_tiled(w, floor, **k):
    """The changing rooms: cream tile to 96 under an oxblood capping, cream plaster above, a cornice."""
    F, top = floor, w.z0
    w.fill(top, F + 104, plaster(CREAM_PL))
    w.fill(top, top - 10, flat_band((206, 194, 164))(top, top - 10))
    w.fill(top - 4, top - 5, lambda x, z: (176, 164, 136))
    w.fill(F + 104, F + 92, lambda x, z: shade(OXBLOOD, (1.35 if z >= F + 102 else 1.15 if z >= F + 99 else
                                                        0.75 if z <= F + 93 else 1.0)) if x % 32 else shade(OXBLOOD, 0.6))
    w.fill(F + 92, F + 8, tile(CREAM_TILE))
    w.fill(F + 8, w.z0 - w.H, tile(shade(OXBLOOD, 0.75), 8, seed=12))


def m_plunge(w, brim, step, **k):
    """The plunge hall: white tile floor to roof, a black course under every `step` of height (the wall is the
    gauge), an oxblood course under the brim, an iron frieze at the roof."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, tile(WHITE_TILE))
    for zc in range(step, top, step):
        w.fill(zc, zc - 8, tile(BLACK, 8, grout=1.6, seed=13))
    w.fill(bot + 8, bot, tile(BLACK, 8, grout=1.6, seed=13))
    w.fill(brim, brim - 8, tile(OXBLOOD, 8, grout=0.7, seed=14))
    w.fill(top, top - 16, plate(IRON, 16))


def m_bath(w, rim, **k):
    """The swimming bath: the plunge's family. White tile; a black course under the rim (the poolside), an
    oxblood one at 96, the iron frieze at the roof."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, tile(WHITE_TILE, seed=15))
    w.fill(rim, rim - 8, tile(BLACK, 8, grout=1.6, seed=16))
    w.fill(rim + 96, rim + 88, tile(OXBLOOD, 8, grout=0.7, seed=17))
    w.fill(rim + 8, rim, tile(shade(OXBLOOD, 0.8), 8, grout=0.7, seed=18))
    w.fill(top, top - 16, plate(IRON, 16))


def m_engine(w, dados, **k):
    """The engine house: cream-painted brick; a maroon dado 40 high over a black skirting at each floor."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, painted_brick(CREAM_BR))
    for D in dados:
        w.fill(D + 44, D + 40, flat_band(BLACK)(D + 44, D + 40))
        w.fill(D + 40, D + 4, painted_brick(MAROON, 19))
        w.fill(D + 4, D, lambda x, z: shade(BLACK, 1.1))
    w.fill(top, top - 12, plate(BLACK, 12))


def m_pumps(w, floor, **k):
    """The pump house: riveted cast-iron plate in maroon to 64, a black band, cream brick above, an iron beam."""
    F, top = floor, w.z0
    w.fill(top, F + 72, painted_brick(CREAM_BR))
    w.fill(F + 72, F + 64, flat_band(BLACK)(F + 72, F + 64))
    w.fill(F + 64, F, plate(MAROON, 32, seed=20))
    w.fill(F + 4, F, lambda x, z: BLACK)
    w.fill(top, top - 16, plate(BLACK, 16))


def m_hall(w, tide, **k):
    """The cooling hall is a tank: riveted iron plate, maroon with black seams where it is dry; below the
    tide line (where it is found) wet black and brown, streaked with lime, a crust at the line."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, tide, plate(MAROON, 64, seed=21))
    w.fill(tide, bot, plate((52, 42, 36), 64, seed=22, rust=0.25))
    for zc in range(tide - tide % 64 + 64, top, 64):
        w.fill(zc, zc - 3, lambda x, z: BLACK)

    def wet(x, z, col):
        t = 0.25 + 0.2 * h32(x // 2, z // 12, 23)
        col = mix(col, (24, 20, 18), t)
        if h32(x, 5, 24) < 0.14 and z > tide - 4 - int(h32(x, 6, 24) * 140):
            col = mix(col, LIME, 0.45)
        return col
    w.tint(tide, bot, wet)
    crust(w, tide)


def m_boiler(w, **k):
    """The boiler house: red brick on an engineering brick plinth, a black iron tie, soot towards the roof."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, brick(BRICK))
    w.fill(bot + 24, bot, brick(ENG, (90, 84, 80), seed=25))
    w.fill(top - 128, top - 140, plate(BLACK, 12))
    soot(w, bot + 120, top)


def m_tank(w, rim, **k):
    """The feed tank: riveted black iron plate to its rim, the boiler house's brick above."""
    m_boiler(w)
    bot = w.z0 - w.H
    w.fill(rim, bot, plate((56, 50, 46), 64, seed=26, rust=0.12))
    w.fill(rim, rim - 6, flat_band(BLACK)(rim, rim - 6))


def m_yard(w, floor, **k):
    """A yard: red brick on a stone plinth 32 high, a stone band at 128 over the floor, a coping at the top."""
    F, top, bot = floor, w.z0, w.z0 - w.H
    w.fill(top, bot, brick(shade(BRICK, 1.05), seed=27))
    w.fill(F + 32, bot, ashlar(GRANITE, 16, seed=28))
    w.fill(F + 32, F + 28, flat_band(shade(GRANITE, 1.1))(F + 32, F + 28))
    w.fill(F + 136, F + 128, flat_band(shade(BUFF, 0.95))(F + 136, F + 128))
    w.fill(top, top - 16, ashlar(shade(BUFF, 0.92), 16, seed=29))
    soot(w, F + 200, top, 0.25, seed=30)


def m_tower(w, floor, **k):
    """The water tower's foot: darker engineering brick, a stone band, riveted tank plates high up."""
    F, top, bot = floor, w.z0, w.z0 - w.H
    w.fill(top, bot, brick(ENG, (110, 100, 92), seed=31))
    w.fill(F + 32, bot, ashlar(GRANITE, 16, seed=28))
    w.fill(F + 224, F + 208, flat_band(shade(BUFF, 0.95))(F + 224, F + 208))
    w.fill(top, F + 224, plate((70, 62, 58), 64, seed=32, rust=0.08))


def m_vault(w, tide, **k):
    """The outfall: a brick vault, damp, an old tide stain."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, brick(shade(BRICK, 0.85), seed=33))
    stain(w, tide, bot, strength=0.55, edge=10, seed=34)
    crust(w, tide, seed=35)


def m_reservoir(w, water, **k):
    """The reservoir: riveted plate, darker and wet where the water stands."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, plate((92, 76, 64), 64, seed=36, rust=0.15))
    stain(w, water, bot, c=(30, 26, 22), strength=0.5, seed=37)


def m_stone(w, stain=None, **k):
    """Dressed buff stone; old stains up to where water can stand."""
    top, bot = w.z0, w.z0 - w.H
    w.fill(top, bot, ashlar(BUFF))
    if stain is not None:
        globals()["stain"](w, stain, bot, seed=38)
        crust(w, stain, seed=39)


def m_timber(w, top, **k):
    """The spillway: tarred timber boards up to `top`, buff stone above."""
    m_stone(w)
    w.fill(top, w.z0 - w.H, boards((96, 66, 40)))
    w.fill(top, top - 4, flat_band((70, 48, 30))(top, top - 4))


MATS = dict(tiled=m_tiled, plunge=m_plunge, bath=m_bath, engine=m_engine, pumps=m_pumps, hall=m_hall,
            boiler=m_boiler, tank=m_tank, yard=m_yard, tower=m_tower, vault=m_vault, reservoir=m_reservoir,
            stone=m_stone, timber=m_timber)


def wall(spec, w=64, H=None, z0=None, shift=0):
    """The wall texture of `spec` (a WALLS entry), or a piece of it w wide for a picture."""
    out = Wall(w, H or spec["H"], spec["z0"] if z0 is None else z0, shift)
    params = {k: v for k, v in spec.items() if k not in ("H", "z0", "mat")}
    MATS[spec["mat"]](out, **params)
    return out


# === pictures ==================================================================================
def plaque_at(w, cx, ztop, year, tw=40):
    """A brass high-water plaque with its top edge at ztop: HIGH WATER and the year; a black line along its
    top, run out past it either side, is the mark."""
    c1, c2 = cx - tw // 2, cx + tw // 2
    w.rect(c1, ztop, c2, ztop - 25, BRASS)
    w.frame(c1, ztop, c2, ztop - 25, shade(BRASS, 0.55))
    w.rect(c1 + 1, ztop - 1, c2 - 1, ztop - 2, shade(BRASS, 1.25))
    w.rect(c1 - 6, ztop + 1, c2 + 6, ztop - 1, (24, 20, 18))           # the mark: its top row is the level
    for c in (c1 - 6, c2 + 5):                                          # its ends turned down, a pointer
        w.rect(c, ztop, c + 1, ztop - 4, (24, 20, 18))
    ink = (52, 34, 18)
    w.centre("HIGH", cx, ztop - 4, ink)
    w.centre("WATER", cx, ztop - 11, ink)
    s = str(year)
    w.digits(s, cx - (len(s) * 4 - 1) // 2, ztop - 18, ink)


def enamel(w, cx, ztop, lines, ground=(28, 26, 26), ink=(232, 222, 196), rim=BRASS, pad=3):
    """A plate with lines of capitals, centred at cx, its top at ztop. Returns its bottom."""
    tw = max(len(s) for s in lines) * 6 - 1
    hgt = len(lines) * 7 - 2 + 2 * pad
    c1, c2 = cx - tw // 2 - pad - 1, cx + (tw + 1) // 2 + pad + 1
    w.rect(c1, ztop, c2, ztop - hgt, ground)
    w.frame(c1, ztop, c2, ztop - hgt, rim)
    for k, s in enumerate(lines):
        w.centre(s, cx, ztop - pad - k * 7, ink)
    return ztop - hgt


def p_sign(spec, w):
    """A plate over a way: what is beyond, just over the way's head."""
    lines = spec["words"]
    hgt = len(lines) * 7 - 2 + 6
    enamel(w, spec["w"] // 2, spec["head"] + 6 + hgt, lines)


def p_plate(spec, w):
    """A plate beside a way (a Doom door has its own surround over it), an arrow under it to the way."""
    bottom = enamel(w, spec["w"] // 2, spec["at"] + len(spec["words"]) * 7 + 4 + 8, spec["words"])
    cz, cx, a = bottom - 5, spec["w"] // 2, spec["arrow"]
    w.rect(cx - 10, cz + 1, cx + 10, cz - 1, (28, 26, 26))
    for i in range(5):
        c = cx + a * (10 + i) if a > 0 else cx - 11 - i
        w.rect(c, cz + 4 - i, c + 1, cz - 4 + i, (28, 26, 26))


def p_plaque(spec, w):
    plaque_at(w, spec["w"] // 2, spec["at"], spec["year"])


def p_flood(spec, w):
    for at, year in zip(spec["ats"], spec["years"]):
        plaque_at(w, spec["w"] // 2, at, year)


def p_words(spec, w):
    """Painted on the tiles: black capitals two to a unit, their top at `at`."""
    for k, s in enumerate(spec["words"]):
        w.centre(s, spec["w"] // 2, spec["at"] - k * 14, (24, 22, 22), 2)


def p_lockers(spec, w):
    """A bank of four varnished lockers, numbered, louvred at the top, on the changing room's tiles."""
    F = spec["basespec"].get("floor", 0)
    wood = (118, 74, 42)
    for k in range(4):
        c1 = 2 + k * 31
        top, bot = F + 152, F + 6
        w.rect(c1, top, c1 + 30, bot, wood)
        for r in w.rows(top, bot):
            for c in range(c1, c1 + 30):
                g = 1 + 0.06 * math.sin(c * 0.7 + r * 0.05 + k) + (h32(c, r, 40 + k) - 0.5) * 0.06
                w.im.set(c, r, shade(wood, g))
        w.frame(c1, top, c1 + 30, bot, shade(wood, 0.55))
        w.frame(c1 + 3, top - 3, c1 + 27, bot + 3, shade(wood, 0.75))
        for z in range(top - 10, top - 26, -3):                           # louvres
            w.rect(c1 + 7, z, c1 + 23, z - 1, shade(wood, 0.45))
        w.rect(c1 + 10, top - 32, c1 + 20, top - 39, BRASS)              # the number plate
        s = str(spec["first"] + k)
        w.digits(s, c1 + 15 - (len(s) * 4 - 1) // 2, top - 33, (50, 30, 14))
        w.rect(c1 + 23, F + 82, c1 + 25, F + 74, shade(BRASS, 0.9))      # the handle
    w.rect(0, F + 6, spec["w"], F, shade(wood, 0.4))                       # the plinth


def p_rules(spec, w):
    F = spec["basespec"].get("floor", 0)
    W_, top = spec["w"], F + 170
    lines = ["1. NO RUNNING.", "2. NO DIVING AT THE", "   SHALLOW END.", "3. DOORS ARE NOT TO BE",
             "   BROUGHT INTO THE WATER."]
    w.rect(4, top, W_ - 4, top - 92, (96, 62, 36))                          # an oak frame ...
    w.rect(8, top - 4, W_ - 8, top - 88, (30, 32, 30))                      # ... round a black board
    ink = (226, 218, 190)
    w.centre("RULES OF THE BATHS", W_ // 2, top - 10, (214, 176, 90))
    w.rect(W_ // 2 - 50, top - 18, W_ // 2 + 50, top - 19, (214, 176, 90))
    for k, s in enumerate(lines):
        w.text(s, 18, top - 26 - k * 9, ink)
    w.text("BY ORDER", W_ - 18 - 47, top - 77, shade(ink, 0.8))


def p_clock(spec, w):
    F = spec["basespec"].get("floor", 0)
    cx, cz = spec["w"] / 2, F + 150
    w.disc(cx, cz, 20, BRASS)
    w.disc(cx, cz, 17, (236, 230, 210))
    for k in range(12):
        t = k * math.pi / 6
        r1 = 13 if k % 3 else 11
        for rr in range(r1, 16):
            w.at(int(cx + rr * math.sin(t)), int(cz + rr * math.cos(t)), (30, 28, 26))
    for t, ln in ((math.pi * 2 * 50 / 60, 14), (math.pi * 2 * (10 + 50 / 60) / 12, 9)):   # ten to eleven
        for k in range(ln):
            w.at(int(cx + k * math.sin(t)), int(cz + k * math.cos(t)), (30, 28, 26))
    w.disc(cx, cz, 1.5, (120, 30, 26))


def p_boilers(spec, w):
    """Three boilers' fronts set in the brick: round black ends, two fire doors each, brass gauges, a nameplate;
    the steam main over them."""
    F = 0
    for k in range(spec["w"] // 128):
        cx = k * 128 + 64
        w.rect(cx - 62, F + 30, cx + 62, F, brick(ENG, (90, 84, 80), seed=25)(0, 1))   # the setting
        for r in w.rows(F + 30, F):
            for c in range(cx - 62, cx + 62):
                w.im.set(c, r, brick(ENG, (90, 84, 80), seed=25)((c + 7) % 64, w.z0 - r))
        w.disc(cx, F + 92, 60, (20, 18, 18))                            # the front
        w.ring(cx, F + 92, 56, 58, (52, 46, 42))
        for a in range(0, 360, 15):                                     # its rivets
            t = math.radians(a)
            w.disc(cx + 53 * math.cos(t), F + 92 + 53 * math.sin(t), 1.2, (88, 80, 72))
        for fx in (cx - 24, cx + 24):                                   # the fire doors
            w.disc(fx, F + 66, 17, shade(BRASS, 0.8))
            w.disc(fx, F + 66, 15, (36, 30, 28))
            for z in range(F + 74, F + 58, -4):
                w.rect(fx - 9, z, fx + 9, z - 2, (70, 30, 20))          # the draught slots, a glow behind
            w.rect(fx + 10, F + 68, fx + 15, F + 64, BRASS)            # the latch
        w.rect(cx - 16, F + 126, cx + 16, F + 116, BRASS)               # the nameplate
        w.text("NO", cx - 13, F + 124, (50, 30, 14))
        w.digits(str(k + 1), cx + 5, F + 124, (50, 30, 14))
        for gx in (cx - 22, cx + 22):                                   # gauges on stalks
            w.rect(gx - 1, F + 152, gx + 2, F + 132, (40, 36, 34))
            w.disc(gx, F + 162, 9, BRASS)
            w.disc(gx, F + 162, 7, (236, 230, 210))
            for i in range(6):
                w.at(int(gx + i * 0.6), F + 162 + i - 3, (150, 30, 26))
        w.rect(cx - 2, F + 230, cx + 3, F + 152, (40, 36, 34))           # the stop valve's pipe to the main
        w.disc(cx, F + 206, 7, (130, 40, 30))
        w.rect(cx - 8, F + 207, cx + 9, F + 205, (90, 30, 24))
    for r in w.rows(F + 240, F + 226):                                  # the steam main, lagged in black
        z = w.z0 - r
        g = 0.7 + 0.5 * math.sin((z - F - 226) / 14 * math.pi)
        for c in range(w.w):
            w.im.set(c, r, shade((44, 40, 38), g))
    for c in range(16, w.w, 64):
        w.rect(c, F + 242, c + 4, F + 224, (24, 22, 22))                 # its clips


def p_section(spec, w):
    """WATERWORKS: LEVELS. Each basin a box from its floor to its brim against a height scale, each frame a
    small door at its sill with its number, the reservoir's level dashed. Drawn from the generator's figures."""
    W_ = spec["w"]
    basins, res = spec["basins"], spec["reservoir"]
    lo = min(b[1] for b in basins) - 16
    hi = max(max(b[2] for b in basins), res) + 24
    top, bot = 344, 24                                                  # the paper (heights on the wall)
    w.rect(4, top, W_ - 4, bot, (110, 80, 48))
    w.rect(7, top - 3, W_ - 7, bot + 3, PAPER)
    ink, red = (34, 30, 30), (150, 34, 30)
    w.centre("WATERWORKS: LEVELS", W_ // 2, top - 8, ink)
    w.rect(W_ // 2 - 56, top - 15, W_ // 2 + 56, top - 16, ink)
    ctop, cbot = top - 26, bot + 22                                     # the chart
    sc = (ctop - cbot) / (hi - lo)
    Z = lambda h: int(round(cbot + (h - lo) * sc))
    ax = 34
    w.rect(ax, ctop, ax + 1, cbot, ink)
    for h in range(lo - lo % 32 + 32, hi, 32):
        w.rect(ax - (5 if h % 64 == 0 else 3), Z(h) + 1, ax, Z(h), ink)
        if h % 64 == 0:
            s = str(h)
            w.digits(s, ax - 7 - len(s) * 4, Z(h) + 3, ink)
        w.rect(ax + 1, Z(h) + 1, W_ - 10, Z(h), (210, 198, 170))       # a faint rule across
    w.rect(ax + 1, Z(0) + 1, W_ - 10, Z(0), (176, 160, 130))
    bw, gap = 38, 7
    for k, (label, floor, brim, frames) in enumerate(basins):
        c1 = ax + 8 + k * (bw + gap)
        c2 = c1 + bw
        z1, z2 = Z(brim), Z(floor)
        for r in w.rows(z1, z2):                                        # hatched: what it can hold
            for c in range(c1, c2):
                if (c + r) % 5 == 0:
                    w.im.set(c, r, (176, 190, 200) if False else (196, 180, 150))
        w.frame(c1, z1 + 1, c2, z2, ink)
        w.rect(c1, z1 + 1, c2, z1 - 1, red)                             # the brim
        w.centre(label, (c1 + c2) // 2, bot + 18, ink)
        s = str(brim)
        w.digits(s, c2 - len(s) * 4, z1 + 7, red)                     # (on the right: the frames' on the left)
        sills = {}
        for n, sill in frames:
            sills.setdefault(sill, []).append(n)
        for sill, ns in sills.items():
            for j, n in enumerate(ns):
                dc = c1 + 2 + j * 18
                zz = Z(sill)
                w.rect(dc, zz + 7, dc + 4, zz, ink)                     # a door at its sill
                w.rect(dc + 1, zz + 6, dc + 3, zz + 1, (150, 120, 70))
                w.digits(str(n), dc + 5, zz + 6, ink)
    zr = Z(res)                                                          # the reservoir's level, dashed
    for c in range(ax + 2, W_ - 12, 6):
        w.rect(c, zr + 1, c + 3, zr - 1, red)
    w.text("RESERVOIR", W_ - 12 - 53, zr + 8, red)
    w.digits(str(res), W_ - 12 - 53 - 16, zr + 8, red)


def p_patent(spec, w):
    """Framed: the patent office's answer to the wheel."""
    W_ = spec["w"]
    top, bot = 100, 14
    w.rect(10, top, W_ - 10, bot, (40, 30, 22))
    w.rect(13, top - 3, W_ - 13, bot + 3, PAPER)
    ink = (40, 34, 30)
    w.centre("PATENT OFFICE", W_ // 2, top - 8, ink)
    w.rect(W_ // 2 - 40, top - 15, W_ // 2 + 40, top - 16, ink)
    w.centre("APPLICATION", W_ // 2, top - 21, ink)
    w.digits("1904", W_ // 2 - 7, top - 29, ink)
    w.centre("PERPETUAL", W_ // 2, top - 38, ink)
    w.centre("MOTION", W_ // 2, top - 46, ink)
    red = (170, 36, 30)                                                 # the stamp: REFUSED in a box
    cx = W_ // 2
    w.frame(cx - 26, top - 55, cx + 26, top - 71, red)
    w.frame(cx - 24, top - 57, cx + 24, top - 69, red)
    w.centre("REFUSED", cx, top - 60, red)


def p_seam(spec, w):
    enamel(w, spec["w"] // 2, 96, ("END OF", "INSTITUTE", "PREMISES"), ground=(232, 224, 200), ink=(28, 26, 26),
           rim=(140, 30, 28))


def p_culvert(spec, w):
    """Over the outfall's glass: a culvert's brick arch, its mouth dark, and the plate."""
    W_, head = spec["w"], spec["head"]
    for c in range(W_):
        u = (c + 0.5) / W_
        rise = int(26 * math.sin(math.pi * u))
        for z in range(head, head + rise + 1):
            w.at(c, z, (16, 14, 14))                                    # the mouth's dark
        for d in range(12):
            z = head + rise + 1 + d
            ang = math.atan2(head + rise - head, (u - 0.5) * W_)
            k = int(((u - 0.5) * W_ + 200) // 9)
            col = shade((128, 50, 36), 0.9 + 0.2 * h32(k, 3, 50)) if (int((u * W_) / 9) + 0) % 1 == 0 else BRICK
            if int((c + d * 0.3)) % 9 == 0:
                col = (170, 160, 140)
            w.at(c, z, col)
    w.rect(W_ // 2 - 6, head + 42, W_ // 2 + 6, head + 24, shade(BUFF, 0.95))   # the keystone
    enamel(w, W_ // 2, head + 66, spec["words"])


def p_tower(spec, w):
    """Over the reservoir's glass in the tower's foot: a stone lintel and the plate."""
    W_, head = spec["w"], spec["head"]
    w.fill(head + 14, head, ashlar(shade(BUFF, 0.95), 14, seed=51))
    enamel(w, W_ // 2, head + 40, spec["words"])


PAINT = dict(sign=p_sign, plate=p_plate, plaque=p_plaque, flood=p_flood, words=p_words, lockers=p_lockers,
             rules=p_rules, clock=p_clock, boilers=p_boilers, section=p_section, patent=p_patent, seam=p_seam,
             culvert=p_culvert, tower=p_tower)


def picture(spec):
    w = wall(spec["basespec"], spec["w"], spec["H"], spec["z0"], spec["shift"])
    PAINT[spec["kind"]](spec, w)
    return w.im


# === flats =====================================================================================
def flat(fn):
    im = Img(64, 64)
    for y in range(64):
        for x in range(64):
            im.set(x, y, fn(x, y))
    return im


def f_squares(a, b=None, s=16, grout=(120, 100, 90), seed=60, var=0.05):
    def f(x, y):
        if x % s == 0 or y % s == 0:
            return jit(grout, x, y, seed + 1, 0.04)
        c = b if b is not None and (x // s + y // s) % 2 else a
        return jit(shade(c, 1 + (h32(x // s, y // s, seed) - 0.5) * 2 * var), x, y, seed, 0.02)
    return flat(f)


def f_plunge():
    """White tile in 8s, a black dot where four meet every 16."""
    def f(x, y):
        if (x % 16 in (15, 0) and y % 16 in (15, 0)):
            return BLACK
        if x % 8 == 0 or y % 8 == 0:
            return (184, 182, 172)
        return jit(WHITE_TILE, x // 8, y // 8, 61, 0.03)
    return flat(f)


def f_bath():
    """White tile in 16s; a black lane line along x every 64 (the bath's floor and poolside: the build's own)."""
    def f(x, y):
        if 28 <= y % 64 <= 35:
            return jit(BLACK, x // 8, y, 62, 0.04) if x % 16 else (90, 88, 84)
        if x % 16 == 0 or y % 16 == 0:
            return (184, 182, 172)
        return jit(WHITE_TILE, x // 16, y // 16, 63, 0.03)
    return flat(f)


def f_glass_roof():
    """Iron trusses and glass: panes of pale glass between black glazing bars, a lattice truss along y."""
    def f(x, y):
        if 28 <= x <= 35:                                               # the truss: chords and a lattice
            if x in (28, 35) or (x - 28 + y) % 16 in (0, 1) or (35 - x + y) % 16 in (0, 1):
                return (26, 24, 24)
            return (196, 196, 186)
        if x % 16 in (0, 1) or y % 32 in (0, 1):
            return (34, 32, 32)
        g = 0.92 + 0.12 * ((x % 16) + (y % 32)) / 46
        return jit(shade((214, 214, 204), g), x, y, 64, 0.02)
    return flat(f)


def f_plaster_ceiling():
    def f(x, y):
        if x in (0, 63) or y in (0, 63):
            return (190, 178, 150)
        if x in (4, 59) or y in (4, 59):
            return (204, 192, 164)
        return jit((228, 218, 192), x // 2, y // 2, 65, 0.02)
    return flat(f)


def f_boards_beams():
    """Boards along x, every 8, on a black iron beam along x every 64."""
    def f(x, y):
        if 26 <= y <= 37:
            return (24, 22, 22) if y in (26, 37) else shade((50, 46, 44), 1.2 if y in (27, 36) else 1)
        if y % 8 == 0:
            return (60, 42, 28)
        k = h32(0, y // 8, 66)
        return jit(shade((132, 96, 62), 0.9 + 0.2 * k), x, y, 67, 0.04)
    return flat(f)


def f_chequer_plate():
    def f(x, y):
        u, v = x % 8, y % 8
        if (u, v) in ((1, 1), (2, 2), (3, 3), (5, 5), (6, 6)) or (x // 8 + y // 8) % 2 and (u, 7 - v) in ((1, 1), (2, 2), (3, 3), (5, 5)):
            return (120, 112, 104)
        return jit((68, 62, 58), x // 2, y // 2, 68, 0.05)
    return flat(f)


def f_silt():
    """Concrete with silt washed over it and a drain."""
    def f(x, y):
        c = jit((132, 126, 116), x, y, 69, 0.06)
        s = 0.5 + 0.5 * math.sin(x * 0.09 + 2 * math.sin(y * 0.11))
        c = mix(c, (100, 82, 60), 0.45 * s * h32(x // 6, y // 6, 70))
        if 24 <= x < 40 and 24 <= y < 40:
            if x in (24, 39) or y in (24, 39):
                return (70, 66, 62)
            return (22, 20, 20) if x % 3 else (90, 86, 80)
        if x % 64 == 0 or y % 64 == 0:
            return (96, 92, 86)
        return c
    return flat(f)


def f_brick_paving():
    def f(x, y):
        k = y // 8
        off = 8 if k % 2 else 0
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (120, 108, 96)
        return jit(shade((140, 70, 50), 0.9 + 0.2 * h32((x + off) // 16, k, 71)), x, y, 72, 0.04)
    return flat(f)


def f_plate_floor():
    w = Wall(64, 64, 64)
    w.fill(64, 0, plate((80, 70, 62), 32, seed=73, rust=0.1))
    return w.im


def f_setts():
    """Granite setts in rows across x, 16 by 8."""
    def f(x, y):
        k = y // 8
        off = (k * 5) % 16
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (60, 56, 52)
        g = 0.85 + 0.3 * h32((x + off) // 16, k, 74)
        return jit(shade((132, 126, 118), g), x, y, 75, 0.05)
    return flat(f)


def f_grass():
    """Dry grass: straw and olive, worn."""
    def f(x, y):
        k = h32(x, y, 76)
        base = mix((128, 118, 70), (150, 132, 80), h32(x // 3, y // 5, 77))
        if k < 0.22:
            return shade(base, 1.25)
        if k > 0.85:
            return mix(base, (92, 76, 52), 0.6)
        return jit(base, x, y, 78, 0.06)
    return flat(f)


def f_flags(c=(150, 136, 108)):
    """Stone flags, 32 square, worn."""
    def f(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return (82, 76, 66)
        k = h32(x // 32, y // 32, 79)
        return jit(shade(c, 0.88 + 0.22 * k), x // 2, y // 2, 80, 0.05)
    return flat(f)


def f_timber():
    def f(x, y):
        if x % 16 == 0:
            return (40, 28, 18)
        k = h32(x // 16, 0, 81)
        return jit(shade((104, 72, 44), 0.85 + 0.25 * k + 0.05 * math.sin(y * 0.3 + k * 7)), x, y, 82, 0.04)
    return flat(f)


def f_wet_brick():
    im = f_brick_paving()
    for p in im.px:
        p[:3] = list(mix(tuple(p[:3]), (40, 34, 30), 0.4))
    return im


def f_vault():
    def f(x, y):
        k = y // 8
        off = 16 if k % 2 else 0
        if y % 8 == 0 or (x + off) % 32 == 0:
            return (70, 62, 56)
        return jit(shade((112, 52, 40), 0.85 + 0.2 * h32((x + off) // 32, k, 83)), x, y, 84, 0.04)
    return flat(f)


def f_dark_plate():
    w = Wall(64, 64, 64)
    w.fill(64, 0, plate((48, 42, 38), 32, seed=85))
    return w.im


FLATS = dict(FQ=lambda: f_squares((150, 56, 40), None, 16, (110, 92, 80), 86), KP=f_plaster_ceiling, FP=f_plunge,
             KG=f_glass_roof, FB=f_bath, FC=lambda: f_squares((150, 54, 40), (32, 30, 30), 16, (96, 84, 76), 87),
             KB=f_boards_beams, FW=f_chequer_plate, FS=f_silt, FR=f_brick_paving, FT=f_plate_floor, FG=f_setts,
             FL=f_grass, FK=f_flags, FD=f_timber, FO=f_wet_brick, KO=f_vault, KR=f_dark_plate)


def make(out, mod):
    """The textures and flats the map (tools/map_highwater.py, `mod`) asks for: WALLS, PICS and the flats."""
    if not mod.LOOK:
        return
    import gfx_water
    tank = wall(mod.WALLS["AJVTK"], 64, 272, 272)                      # the float mark on the tank's own plates
    out["textures/AJFLOATM.png"] = gfx_water.float_mark(tank.im).png()

    def put(kind, nm, im):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = im.png()
    for nm, spec in mod.WALLS.items():
        put("textures", nm, wall(spec).im)
    for nm, spec in mod.PICS.items():
        put("textures", nm, picture(spec))
    for tag, fn in FLATS.items():
        put("flats", "AJV" + tag, fn())
