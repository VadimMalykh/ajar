"""MAP33's look 1, "Temple of Power" (the 1930s): brown brick with tall piers, cream faience tile, black bands,
bronze and brass, teak, terrazzo; a fine afternoon haze with high thin cloud. Warm and neutral colours only:
the doors are BLUE, VIOLET and PINK and the parts yellow, green and red, which appear only as each place's
phase band (a course of glazed tile between two black lines) and as the bar on a plate (and red on DANGER
plates in part 3's places). The slots are tools/gfx_power.py's; the map's side is tools/power33.py.
"""
import math

import gfx_power as G
from gfx import Img, digit
from gfx_power import Wall, flat, h32, jit, mix, shade, text_width

# --- the palette --------------------------------------------------------------------------------------------
BRICK, MORTAR = (122, 72, 50), (160, 144, 120)
ENG = (78, 50, 40)                       # engineering brick, dark
CREAM, IVORY, CREAM_PL = (226, 212, 172), (236, 230, 210), (222, 212, 186)
STONE, GRANITE = (206, 192, 160), (138, 132, 122)
BLACK, SOOT = (30, 28, 28), (34, 30, 28)
BRONZE, BRASS = (138, 96, 50), (198, 162, 84)
TEAK, WALNUT = (118, 76, 42), (84, 52, 32)
STEEL, IRON = (112, 108, 100), (58, 54, 52)
PAPER = (232, 222, 196)
INK = (36, 30, 26)
RED = (190, 40, 34)                     # DANGER plates only (part 3's places)


# === patterns: f(x, z) -> colour (x along the wall in its period, z the row's top edge) =======================
def tile(c, s=16, grout=0.76, var=0.035, seed=1, sh=None):
    sh = sh or s

    def f(x, z):
        if x % s == 0 or z % sh == 0:
            return jit(shade(c, grout), x, z, seed + 9, 0.02)
        k = h32(x // s, (z - 1) // sh, seed)
        g = 1 + (k - 0.5) * 2 * var + (0.06 if (z % sh == sh - 1 or x % s == 1) else 0)
        return jit(shade(c, g), x, z, seed, 0.012)
    return f


def brick(c, mortar=MORTAR, course=8, length=32, var=0.09, seed=2):
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


def ashlar(c, course=32, block=64, seed=5, joint=0.7):
    def f(x, z):
        kz = (z - 1) // course
        o = block // 2 if kz % 2 else 0
        if z % course == 0 or (x + o) % block == 0:
            return jit(shade(c, joint), x, z, seed + 3, 0.04)
        k = h32((x + o) // block, kz, seed)
        g = 1 + (k - 0.5) * 0.12 + (0.06 if z % course == course - 1 else 0)
        return jit(shade(c, g), x // 2, z // 2, seed, 0.05)
    return f


def plaster(c, seed=6, amt=0.025):
    return lambda x, z: jit(c, x // 2, z // 2, seed, amt)


def plate(c, seam=64, pw=64, seed=4, rivet=8):
    """Riveted plate: seams every `seam` of height and `pw` along, rivets along them."""
    def f(x, z):
        m, u = z % seam, x % pw
        if m == 0 or u == 0:
            return shade(c, 0.55)
        if m == 1 or u == 1 or u == pw - 1:
            return shade(c, 1.22 if m == 1 else 0.8)
        if (m in (5, seam - 4) and u % rivet == 4) or (u in (5, pw - 5) and m % rivet == 4):
            return shade(c, 1.45)
        if (m in (4, seam - 5) and u % rivet == 4) or (u in (4, pw - 6) and m % rivet == 5):
            return shade(c, 0.6)
        g = 1 + 0.04 * math.sin(u * math.pi / (pw / 2)) + (h32(x // 4, z // 6, seed) - 0.5) * 0.06
        return shade(c, g)
    return f


def solid(c, amt=0.02, seed=7):
    return lambda x, z: jit(c, x // 2, z // 2, seed, amt)


def moulding(c, top, bot):
    """A run of mouldings between top and bot: lit tops, shadowed undersides."""
    def f(x, z):
        k = (top - z) % 6
        g = (1.25, 1.1, 1.0, 0.95, 0.8, 0.62)[k]
        return jit(shade(c, g), x, z, 13, 0.015)
    return f


def lit_band(c):
    def make(top, bot):
        def f(x, z):
            if z == top:
                return shade(c, 1.3)
            if z == bot + 1:
                return shade(c, 0.6)
            return jit(c, x, z, 11, 0.03)
        return f
    return make


def band(w, F, part):
    """The phase band: one course of glazed tile in the part's colour between two black lines, F + 72 to 80."""
    if not part:
        return
    lo, hi = F + G.BAND[0], F + G.BAND[1]
    col = G.PART_COLOURS[part]
    w.fill(hi + 2, hi, lambda x, z: BLACK if z == hi + 1 else shade(BLACK, 1.5))
    w.fill(lo, lo - 2, lambda x, z: BLACK if z == lo else shade(BLACK, 0.8))

    def glaze(x, z):
        if x % 16 == 0:
            return shade(col, 0.62)
        if z == hi:
            return mix(col, (255, 250, 236), 0.45)
        if z == lo + 1:
            return shade(col, 0.78)
        return jit(col, x // 16, 0, 41, 0.03)
    w.fill(hi, lo, glaze)


def skirting(w, F, h=8):
    w.fill(F + h, max(w.bot, F - 8), lambda x, z: shade(BLACK, 1.35) if z == F + h else jit(BLACK, x, z, 12, 0.05))


def soot(w, zfrom, ztop, most=0.6, seed=10):
    def f(x, z, col):
        t = most * min(1, max(0, (z - zfrom) / max(1, ztop - zfrom))) ** 1.3
        t *= 0.85 + 0.3 * h32(x // 4, z // 16, seed)
        return mix(col, SOOT, min(1, t))
    w.tint(ztop, zfrom, f)


def streaks(w, ztop, zbot, c, density=0.1, strength=0.35, seed=30, P=64):
    """Runs down from the top: dark (or lime) streaks of varying length."""
    def f(x, z, col):
        k = h32(x // 2, 0, seed)
        if k < density:
            ln = 40 + h32(x // 2, 1, seed) * (ztop - zbot)
            if ztop - z < ln:
                t = strength * (1 - (ztop - z) / ln)
                return mix(col, c, t)
        return col
    w.tint(ztop, zbot, f)


# === the walls ================================================================================================
def w_tiled(w, F, part, top, dado=112, cornice=14):
    """The tile family: a black skirting, cream faience to the dado under a black capping, cream plaster above,
    a cornice under the ceiling; the band in the tiles."""
    w.fill(w.z0, w.bot, plaster(CREAM_PL))
    w.fill(top, top - cornice, moulding((214, 202, 170), top, top - cornice))
    w.fill(F + dado + 6, F + dado, lit_band(BLACK)(F + dado + 6, F + dado))
    w.fill(F + dado, F + 8, tile(CREAM))
    skirting(w, F)
    band(w, F, part)


def m_TD(w, F, part, top):
    w_tiled(w, F, part, top)


def m_CO(w, F, part, top):
    w_tiled(w, F, part, top, dado=96, cornice=8)


def m_GP(w, F, part):
    """The gatehouse's pillars: faience all the way, a moulded capital, the band."""
    w.fill(w.z0, w.bot, tile(CREAM, 16, seed=3))
    w.fill(w.z0, w.z0 - 16, moulding((214, 202, 170), w.z0, w.z0 - 16))
    w.fill(F + 120, F + 114, lit_band(BLACK)(F + 120, F + 114))
    skirting(w, F, 12)
    band(w, F, part)


def m_CT(w):
    """The counter's front: teak, panelled, on a black plinth."""
    def f(x, z):
        u = x % 32
        if z <= 4:
            return jit(BLACK, x, z, 14, 0.05)
        if z >= 37:
            return shade(TEAK, 1.3 if z == 40 else 0.8)
        if u in (0, 1, 30, 31) or z in (5, 6, 7, 34, 35, 36):
            return jit(shade(TEAK, 0.85), x, z, 15, 0.04)
        if u in (4, 27) or z in (10, 31):
            return shade(TEAK, 0.7 if u == 27 or z == 10 else 1.2)
        g = 1 + 0.06 * math.sin(z * 0.9 + u * 0.15) + (h32(u, 0, 16) - 0.5) * 0.05
        return shade(TEAK, g)
    w.fill(w.z0, w.bot, f)


def m_SK(w):
    w.fill(w.z0, w.bot, ashlar(GRANITE, 16, 32, seed=17))


def m_RI(w, kind):
    c = {"stone": (176, 166, 146), "marble": (200, 198, 192)}[kind]

    def f(x, z):
        if z % 16 == 0:
            return shade(c, 1.3)
        if z % 16 == 15:
            return shade(c, 0.6)
        if z % 8 == 0:
            return shade(c, 0.85)
        return jit(c, x // 2, z // 2, 18, 0.04)
    w.fill(w.z0, w.bot, f)


def m_YD(w, F, part, damp=0):
    """Out of doors: brown brick on a cream stone plinth, a tall pier every 256, a stone string course and a
    coping under the sky; the band in a course of glazed tile."""
    P = w.period
    br = brick(BRICK)
    pier = brick(shade(BRICK, 0.9), seed=19)

    def f(x, z):
        d = min(x, P - x)                       # the pier: 40 wide, centred at x 0
        if d < 20:
            col = pier(x, z)
            if d in (19, 18):
                col = shade(col, 1.18 if x > P // 2 else 0.7)
            return col
        return br(x, z)
    w.fill(w.z0, w.bot, f)
    w.fill(F + 32, w.bot, ashlar(STONE, 16, 64, seed=20))
    w.fill(F + 34, F + 32, lit_band(STONE)(F + 34, F + 32))
    w.fill(F + 200, F + 192, lit_band(shade(STONE, 0.95))(F + 200, F + 192))
    w.fill(G.SKY_TOP, G.SKY_TOP - 16, ashlar(STONE, 16, 64, seed=21))
    w.fill(G.SKY_TOP - 16, G.SKY_TOP - 20, lambda x, z: shade(STONE, 0.6))
    soot(w, F + 240, G.SKY_TOP, 0.18, seed=22)
    if damp:
        def wet(x, z, col):
            t = 0.42 * (1 - (z - w.bot) / 64) if z < w.bot + 64 else 0
            e = F + 48 - int(h32(x // 3, 0, 23) * 10)
            if z <= e:
                col = mix(col, (52, 44, 36), max(t, 0.28))
                if h32(x, 2, 24) < 0.12:
                    col = mix(col, (190, 184, 168), 0.25)
            return col
        w.tint(F + 60, w.bot, wet)
    band(w, F, part)


def m_SL(w):
    """The bunker's wall: tarred sleepers laid on edge between iron posts."""
    tar = (58, 44, 32)

    def f(x, z):
        if x < 6 or x > 57:
            u = x if x < 6 else 63 - x
            return shade(IRON, (0.6, 1.2, 1.0, 1.0, 0.9, 0.7)[u])
        if z % 12 == 0:
            return shade(tar, 0.5)
        k = h32(0, (z - 1) // 12, 25)
        g = 0.85 + 0.3 * k + 0.06 * math.sin(x * 0.4 + k * 9)
        if z % 12 == 11:
            g *= 1.2
        return jit(shade(tar, g), x, z, 26, 0.05)
    w.fill(w.z0, w.bot, f)
    w.fill(w.z0, w.z0 - 3, lambda x, z: shade(tar, 1.3))


def lumps(base, hi, seed, size=5, glint=None):
    def f(x, z):
        cx, cz = x // size, z // size
        best, kb = 9, 0
        for dx in (0, 1):
            for dz in (0, 1):
                px = (cx + dx) * size + h32(cx + dx, cz + dz, seed) * size
                pz = (cz + dz) * size + h32(cx + dx, cz + dz, seed + 1) * size
                d = math.hypot(x - px, z - pz)
                if d < best:
                    best, kb = d, h32(cx + dx, cz + dz, seed + 2)
        g = 0.75 + 0.5 * kb - 0.05 * best
        col = shade(base, max(0.4, g))
        if glint and best < 1.2 and kb > 0.7:
            return glint
        if best < 1 and kb > 0.5:
            col = mix(col, hi, 0.4)
        return col
    return f


def m_CF(w):
    w.fill(w.z0, w.bot, lumps((40, 38, 38), (150, 146, 140), 27, 5, glint=(196, 192, 184)))


def m_EF(w):
    w.fill(w.z0, w.bot, lumps((104, 82, 58), (150, 136, 118), 28, 6))


def m_GF(w):
    w.fill(w.z0, w.bot, lumps((168, 164, 152), (210, 206, 196), 29, 3))


def m_SF(w, F=None, part=0):
    w.fill(w.z0, w.bot, ashlar(STONE, 16, 32, seed=31))
    if part:
        band(w, F, part)


def m_PF(w):
    """Stone pitching: rough stones in rough courses."""
    def f(x, z):
        kz = (z - 1) // 12
        o = int(h32(kz, 0, 32) * 20)
        u = (x + o) % 64
        blk = u // (14 + int(h32(kz, 1, 32) * 8))
        if z % 12 == 0 or (x + o) % (14 + int(h32(kz, 1, 32) * 8)) == 0:
            return jit((70, 64, 56), x, z, 33, 0.08)
        k = h32(blk, kz, 34)
        return jit(shade((140, 128, 108), 0.8 + 0.35 * k), x // 2, z // 2, 35, 0.07)
    w.fill(w.z0, w.bot, f)


def m_CH(w):
    """The chimney: cream fluted concrete on a dark brick base."""
    def flute(x, z):
        u = x % 16
        g = 0.82 + 0.3 * math.sin(math.pi * (u + 0.5) / 16)
        if u == 0:
            g = 0.7
        if z % 96 == 0:
            g *= 0.85
        return jit(shade((220, 208, 176), g), x // 2, z // 3, 36, 0.02)
    w.fill(w.z0, w.bot, flute)
    w.fill(48, w.bot, brick(ENG, (90, 80, 72), seed=37))
    w.fill(54, 48, lit_band(STONE)(54, 48))
    w.fill(w.z0, w.z0 - 20, lambda x, z: shade(BLACK, 1.2 if z == w.z0 - 19 else 1.0))
    soot(w, w.z0 - 120, w.z0 - 20, 0.5, seed=38)


def m_BH(w, F, part):
    """The boiler house: brown brick between steel stanchions (every 128), engineering brick at the foot, an
    iron tie, soot growing upward."""
    P = w.period
    br = brick(BRICK, seed=39)

    def f(x, z):
        d = min(x, P - x)
        if d < 7:
            if d == 0:
                return shade(IRON, 0.55)
            return jit(shade(IRON, 1.15 if d in (1, 5) else 0.9 if d == 6 else 1.0), x, z, 40, 0.03)
        return br(x, z)
    w.fill(w.z0, w.bot, f)
    w.fill(F + 24, w.bot, brick(ENG, (90, 80, 72), seed=41))
    w.fill(F + 260, F + 250, lambda x, z: shade(IRON, 1.25 if z == F + 260 else 0.95))
    soot(w, F + 140, w.z0, 0.62, seed=42)
    band(w, F, part)


def m_BS(w):
    """A boiler's sides: riveted black plate, a lagging band."""
    w.fill(w.z0, w.bot, plate((44, 40, 38), 64, 64, seed=43))
    lag = (184, 176, 156)
    w.fill(208, 168, lambda x, z: shade(BLACK, 1.1) if x % 64 in (0, 1, 2, 31, 32, 33) else
           jit(shade(lag, 0.8 + 0.3 * math.sin((z - 168) / 40 * math.pi)), x, z, 44, 0.04))
    w.fill(w.z0, w.z0 - 4, lambda x, z: shade((44, 40, 38), 1.5))


def m_SE(w):
    def f(x, z):
        if z == w.z0:
            return (150, 142, 132)
        if z == w.z0 - 1:
            return (104, 98, 92)
        return jit((70, 66, 62), x, z, 45, 0.06)
    w.fill(w.z0, w.bot, f)


def m_AT(w, F, part):
    """The ash tunnel: white glazed brick gone grey, ash at its foot."""
    gb = brick((196, 192, 180), (150, 146, 138), seed=46, var=0.05)

    def f(x, z):
        col = gb(x, z)
        return mix(col, (90, 88, 84), 0.25 + 0.3 * h32(x // 8, z // 12, 47))
    w.fill(w.z0, w.bot, f)
    w.tint(F + 24, w.bot, lambda x, z, c: mix(c, (110, 106, 100), 0.5))
    band(w, F, part)


def m_PC(w, F):
    """A pump's casing: machine grey, a bolted flange course, a brass cap line at the top."""
    top = w.z0

    def f(x, z):
        if z > top - 3:
            return shade(BRASS, 1.25 if z == top else 0.9)
        if F + 56 < z <= F + 64:
            if x % 8 == 4 and z in (F + 60, F + 61):
                return shade(STEEL, 1.5)
            return shade(STEEL, 0.75 if z in (F + 57, F + 64) else 0.9)
        if z <= F + 6:
            return shade(STEEL, 0.7)
        g = 0.92 + 0.12 * math.sin(math.pi * (x % 64) / 64)
        return jit(shade(STEEL, g), x // 2, z // 2, 48, 0.02)
    w.fill(w.z0, w.bot, f)


def m_LP(w):
    """A lagged pipe run: cream lagging with black bands every 64, round."""
    top, bot = w.z0, w.bot

    def f(x, z):
        t = (z - bot) / max(1, top - bot)
        g = 0.62 + 0.5 * math.sin(t * math.pi)
        if x % 64 < 5:
            return shade(BLACK, 0.8 + 0.6 * g)
        return jit(shade((214, 204, 178), g), x, z, 49, 0.03)
    w.fill(w.z0, w.bot, f)


CLER = (280, 352)                       # the turbine hall's clerestory (absolute), the crane rail under it


def m_TH(w, F, part):
    """The turbine hall: ivory faience, a black skirting and a black band at the dado, the clerestory high up
    over the crane rail, a cornice."""
    w.fill(w.z0, w.bot, tile(IVORY, 16, 0.8, seed=50))
    w.fill(F + 120, F + 112, lit_band(BLACK)(F + 120, F + 112))
    skirting(w, F, 10)
    lo, hi = CLER

    def glaze(x, z):
        u, v = x % 32, (z - lo) % 24
        if u < 2 or v < 2:
            return shade(IRON, 0.8)
        g = 0.95 + 0.1 * (v / 24)
        return jit(shade((236, 232, 220), g), x, z, 51, 0.02)
    w.fill(hi, lo, glaze)
    w.fill(hi + 4, hi, lambda x, z: shade(IRON, 1.1))
    w.fill(lo, lo - 4, lambda x, z: shade(IRON, 1.1))
    w.fill(lo - 8, lo - 24, lambda x, z: shade(IRON, 1.3) if z == lo - 8 else
           (shade(IRON, 1.5) if x % 16 == 8 and z in (lo - 12, lo - 20) else shade(IRON, 0.85)))
    w.fill(w.z0, w.z0 - 12, moulding((216, 210, 192), w.z0, w.z0 - 12))
    band(w, F, part)


def m_GG(w):
    """The gantry's crane girder: a deep riveted plate girder, stiffeners every 64."""
    top, bot = w.z0, w.bot
    g = (70, 66, 62)

    def f(x, z):
        if z > top - 10 or z <= bot + 10:
            return shade(g, 1.3 if z in (top, bot + 10) else 0.95)
        if x % 64 < 8:
            return shade(g, 1.15 if x % 64 in (1, 2) else 0.8 if x % 64 == 7 else 1.0)
        if (z in (top - 14, bot + 14)) and x % 8 == 4:
            return shade(g, 1.6)
        return jit(g, x // 3, z // 3, 52, 0.04)
    w.fill(w.z0, w.bot, f)


def m_TE(w):
    def f(x, z):
        if z % 48 in (0, 1):
            return shade(STEEL, 0.7 if z % 48 == 0 else 1.2)
        return jit(shade(STEEL, 1.0), x // 2, z // 2, 53, 0.02)
    w.fill(w.z0, w.bot, f)


def m_SW(w):
    """The spider's pit: black oiled concrete, two pipes along it."""
    w.fill(w.z0, w.bot, lambda x, z: jit((34, 32, 30), x // 3, z // 2, 54, 0.12))
    for zc, c in ((w.bot + 26, (90, 84, 76)), (w.bot + 14, (110, 92, 62))):
        w.fill(zc + 3, zc - 3, lambda x, z, zc=zc, c=c: shade(c, 0.7 + 0.5 * math.cos((z - zc) / 3.5)))


def m_CW(w):
    """A condenser pit: the tube plate, rows of small tube ends."""
    def f(x, z):
        u, v = x % 6, z % 6
        if (u - 3) ** 2 + (v - 3) ** 2 <= 4:
            return (42, 36, 30) if (u - 3) ** 2 + (v - 3) ** 2 <= 1 else (150, 120, 76)
        return jit((122, 104, 74), x, z, 55, 0.04)
    w.fill(w.z0, w.bot, f)


def m_WS(w, F, part):
    """The workshop: a brown glazed brick dado, cream painted brick above."""
    w.fill(w.z0, w.bot, brick((214, 204, 176), (192, 182, 156), seed=56, var=0.03))
    w.fill(F + 104, F, brick((110, 66, 40), (78, 50, 34), seed=57, var=0.07))
    w.fill(F + 108, F + 104, lit_band((86, 54, 34))(F + 108, F + 104))
    w.fill(w.z0, w.z0 - 8, lambda x, z: shade(IRON, 1.0))
    skirting(w, F, 6)
    band(w, F, part)


def m_BN(w):
    """A bench's front: an iron frame, two drawers each 64, brass pulls, the timber top's edge."""
    top = w.z0

    def f(x, z):
        u = x % 32
        if z > top - 5:
            return jit(shade(TEAK, 1.15 if z == top else 0.95), x, z, 58, 0.04)
        if u < 2 or z <= w.bot + 3:
            return shade(IRON, 0.9)
        if 12 < u < 20 and top - 15 >= z > top - 18:
            return shade(BRASS, 1.1)
        if z > top - 24:
            return shade((92, 64, 40), 1.2 if z == top - 5 else 0.95 if u > 2 else 0.7)
        return jit(shade(IRON, 0.75), x // 2, z // 2, 59, 0.05)
    w.fill(w.z0, w.bot, f)


def m_LA(w):
    """A lathe's side: the cabinet stand, the bed and its ways, the headstock, a handwheel."""
    P = w.period
    bot, top = w.bot, w.z0
    w.fill(top, bot, lambda x, z: jit((52, 50, 48), x // 2, z // 2, 60, 0.05))
    w.fill(top, top - 10, lambda x, z: shade((170, 166, 158), 1.2 if z == top else 0.9))      # the ways
    w.fill(top - 10, top - 16, lambda x, z: shade((40, 38, 36), 1.0))
    w.rect(0, top, 30, top - 46, (64, 62, 58))                                                # the headstock
    w.frame(0, top, 30, top - 46, (40, 38, 36))
    w.disc(15, top - 22, 9, (148, 144, 136))                                                  # the chuck
    w.disc(15, top - 22, 3, (40, 38, 36))
    cx, cz = 86, bot + 30                                                                     # the handwheel
    w.ring(cx, cz, 9, 11, (130, 126, 118))
    for a in range(0, 360, 60):
        t = math.radians(a)
        w.line(cx, cz, cx + 9 * math.cos(t), cz + 9 * math.sin(t), (120, 116, 108))
    w.disc(cx, cz, 2, BRASS)
    w.rect(4, bot + 30, P - 4, bot, (44, 42, 40))                                             # the stand
    w.frame(6, bot + 28, 60, bot + 2, (30, 28, 28))
    w.frame(68, bot + 28, P - 6, bot + 2, (30, 28, 28))
    w.rect(28, bot + 18, 36, bot + 15, BRASS)


def m_AR(w, F, part):
    w.fill(w.z0, w.bot, plate((100, 96, 88), 32, 64, seed=61))
    skirting(w, F, 6)
    band(w, F, part)


def m_TU(w, F, part):
    """The cable tunnel: dark brick with cable brackets, black cables on them."""
    w.fill(w.z0, w.bot, brick(shade(BRICK, 0.85), seed=62))
    for x0 in (14, 46):
        w.rect(x0, F + 70, x0 + 3, F + 28, shade(IRON, 0.9))
    for zc in (F + 40, F + 64):
        w.fill(zc, zc - 2, lambda x, z: shade(IRON, 1.2))
        w.fill(zc + 5, zc, lambda x, z, zc=zc: shade((22, 22, 22), 1.6 if z == zc + 4 else 1.0) if x % 6 else (50, 48, 46))
    skirting(w, F, 6)
    band(w, F, part)


def m_TR(w, F=0, part=0):
    """A cable tray's edge: a steel channel, cable ends in it."""
    def f(x, z):
        if z == w.z0 or z == w.bot + 1:
            return shade(STEEL, 1.3)
        if (x % 6 - 3) ** 2 + (z % 6 - 3) ** 2 <= 4 and w.bot + 2 < z < w.z0 - 1:
            return (20, 18, 18) if (x % 6 - 3) ** 2 + (z % 6 - 3) ** 2 > 1 else (150, 110, 60)
        return jit(shade(STEEL, 0.8), x, z, 63, 0.03)
    w.fill(w.z0, w.bot, f)
    band(w, F, part)


def m_TF(w):
    """A transformer's cooling fins: radiator banks between headers."""
    top, bot = w.z0, w.bot
    g = (74, 72, 68)

    def f(x, z):
        if top - 12 < z <= top - 4 or bot + 4 < z <= bot + 12:
            return shade(g, 0.8 + 0.5 * math.sin((z % 8) / 8 * math.pi))
        if z > top - 4 or z <= bot + 4:
            return shade(g, 0.6)
        u = x % 8
        return shade(g, (0.45, 0.7, 1.0, 1.25, 1.3, 1.1, 0.85, 0.6)[u])
    w.fill(w.z0, w.bot, f)


def m_PL(w):
    w.fill(w.z0, w.bot, lambda x, z: jit((176, 170, 160), x // 2, z, 64, 0.05) if z != w.z0 else (198, 192, 182))


def m_GL(w):
    """The switchyard's gantry: a lattice girder's face, the chords and the diagonals over its shadow."""
    top, bot = w.z0, w.bot
    g = (86, 82, 76)

    def f(x, z):
        if z > top - 12 or z <= bot + 12:
            return shade(g, 1.3 if z in (top, bot + 12) else 1.0)
        u = x % 64
        h = z - bot - 12
        span = top - bot - 24
        d1 = abs(u - h * 64 / span)
        d2 = abs(u - (64 - h * 64 / span))
        if min(d1, d2) < 4 or u < 4:
            return shade(g, 1.15 if min(d1, d2) < 1.5 else 0.95)
        return jit((32, 30, 28), x, z, 65, 0.05)
    w.fill(w.z0, w.bot, f)


def m_RR(w, F, part):
    """The relay room: cream plaster, a dark wood dado, a picture rail."""
    w.fill(w.z0, w.bot, plaster(CREAM_PL, 66))
    def dado(x, z):
        u = x % 64
        if u < 3 or u > 60 or z > F + 92 or z <= F + 8:
            return jit(shade(WALNUT, 0.85), x, z, 67, 0.04)
        if u in (8, 55) or z in (F + 86, F + 14):
            return shade(WALNUT, 0.7 if u == 55 or z == F + 14 else 1.3)
        return jit(shade(WALNUT, 1.05 + 0.04 * math.sin(z * 0.7)), x, z, 68, 0.03)
    w.fill(F + 96, F, dado)
    w.fill(F + 100, F + 96, lit_band(WALNUT)(F + 100, F + 96))
    w.fill(F + 160, F + 156, lit_band(WALNUT)(F + 160, F + 156))
    skirting(w, F, 6)
    band(w, F, part)


def m_RC(w):
    """A relay cabinet: black slate panels, rows of brass relays under small glass covers, label strips."""
    slate = (34, 34, 36)
    w.fill(w.z0, w.bot, lambda x, z: jit(slate, x // 2, z // 2, 69, 0.04) if x % 64 not in (0, 63) else (16, 16, 16))
    for zr in (w.z0 - 10, w.z0 - 34, w.z0 - 58):
        for c in range(4, w.w, 12):
            w.rect(c, zr, c + 8, zr - 12, shade(BRASS, 0.9))
            w.rect(c + 1, zr - 1, c + 7, zr - 2, (236, 232, 218))
            w.rect(c + 2, zr - 4, c + 6, zr - 10, shade(BRASS, 0.6))
        w.rect(2, zr - 15, w.w - 2, zr - 19, (220, 212, 190))
    w.fill(w.bot + 6, w.bot, lambda x, z: (16, 16, 16))


def m_OC(w, F, part):
    """The outfall: a brick culvert's lining, dark and wet."""
    w.fill(w.z0, w.bot, brick(shade(BRICK, 0.8), seed=70))
    w.tint(F + 64, w.bot, lambda x, z, c: mix(c, (40, 36, 30), 0.45))
    streaks(w, F + 64, w.bot, (60, 56, 46), 0.2, 0.4, seed=71)
    band(w, F, part)


def m_TW(w, F, part):
    """The cooling tower's shell: concrete with vertical ribs, dark lime streaks, a ring beam high up."""
    conc = (186, 180, 168)

    def f(x, z):
        u = x % 64
        if u < 6:
            return shade(conc, (1.25, 1.15, 1.05, 0.95, 0.85, 0.7)[u])
        return jit(conc, x // 3, z // 4, 72, 0.04)
    w.fill(w.z0, w.bot, f)
    streaks(w, 400, w.bot, (70, 70, 64), 0.16, 0.45, seed=73)
    w.fill(416, 400, lambda x, z: shade(conc, 1.25 if z == 416 else 0.7 if z == 401 else 1.0))
    band(w, F, part)


def m_TP(w):
    conc = (176, 170, 158)
    w.fill(w.z0, w.bot, lambda x, z: shade(conc, 1.2) if x % 64 < 2 else jit(conc, x // 3, z // 4, 74, 0.04))
    streaks(w, w.z0, w.bot, (80, 78, 70), 0.1, 0.35, seed=75)


def m_TL(w):
    conc = (170, 164, 152)
    w.fill(w.z0, w.bot, lambda x, z: shade(conc, (1.2, 1.0, 0.85, 0.7)[x % 16 // 4]))
    w.fill(w.z0, w.z0 - 6, lambda x, z: shade(conc, 1.3 if z == w.z0 else 1.05))


def m_DK(w, F, part):
    """The duct: brick with cable racks, black cables."""
    w.fill(w.z0, w.bot, brick(shade(BRICK, 0.9), seed=76))
    w.rect(30, F + 126, 33, F + 96, IRON)
    for zc in (F + 104, F + 112, F + 120):
        w.fill(zc, zc - 5, lambda x, z, zc=zc: shade((22, 22, 22), 1.6 if z == zc - 1 else 1.0))
    skirting(w, F, 6)
    band(w, F, part)


def m_LH(w, F, part):
    """The switchgear hall: a walnut panelled dado to the stands' level (0), grey-veined marble panels
    between bronze strips above it, a cornice; its stands the same with their part's band."""
    P = w.period

    def marble(x, z):
        v = math.sin(x * 0.11 + z * 0.045 + 3 * math.sin(z * 0.02 + x * 0.03)) + 0.6 * math.sin(x * 0.05 - z * 0.08)
        g = 0.93 + 0.06 * h32(x // 8, z // 8, 77)
        col = shade((214, 212, 204), g)
        if abs(v) < 0.08:
            col = mix(col, (112, 110, 106), 0.7)
        elif abs(v) < 0.2:
            col = mix(col, (150, 148, 142), 0.3)
        u = x % P
        if u < 3:
            return shade(BRONZE, (0.7, 1.3, 1.0)[u])
        if z % 192 in (0, 1, 2) and z > 0:
            return shade(BRONZE, (0.7, 1.0, 1.3)[z % 192])
        return col
    w.fill(w.z0, w.bot, marble)

    def dado(x, z):
        u = x % 64
        if u < 4 or u > 59 or z > -10 or z <= -84:
            return jit(shade(WALNUT, 0.9), x, z, 78, 0.04)
        if u in (8, 55) or z in (-16, -78):
            return shade(WALNUT, 0.65 if u == 55 or z == -78 else 1.35)
        return jit(shade(WALNUT, 1.08 + 0.05 * math.sin(z * 0.5 + u * 0.1)), x, z, 79, 0.03)
    w.fill(0, w.bot, dado)
    w.fill(4, 0, lit_band(BRONZE)(4, 0))
    w.fill(-88, w.bot, lambda x, z: jit(BLACK, x, z, 80, 0.05))
    w.fill(w.z0, w.z0 - 16, moulding((222, 218, 206), w.z0, w.z0 - 16))
    band(w, F, part)


def m_SN(w):
    def f(x, z):
        if z > w.z0 - 3:
            return (70, 66, 62)
        if x % 64 in (0, 63):
            return (14, 14, 14)
        return jit((22, 22, 24), x // 2, z // 2, 81, 0.04)
    w.fill(w.z0, w.bot, f)


def m_SH(w):
    w.fill(w.z0, w.bot, brick((132, 84, 62), (150, 136, 116), seed=82))


WALLS = dict(TD=m_TD, CO=m_CO, GP=m_GP, CT=m_CT, SK=m_SK, RI=m_RI, YD=m_YD, SL=m_SL, CF=m_CF, EF=m_EF, GF=m_GF,
             SF=m_SF, PF=m_PF, CH=m_CH, BH=m_BH, BS=m_BS, SE=m_SE, AT=m_AT, PC=m_PC, LP=m_LP, TH=m_TH, GG=m_GG,
             TE=m_TE, SW=m_SW, CW=m_CW, WS=m_WS, BN=m_BN, LA=m_LA, AR=m_AR, TU=m_TU, TR=m_TR, TF=m_TF, PL=m_PL,
             GL=m_GL, RR=m_RR, RC=m_RC, OC=m_OC, TW=m_TW, TP=m_TP, TL=m_TL, DK=m_DK, LH=m_LH, SN=m_SN, SH=m_SH)


# === pictures =================================================================================================
def enamel(w, cx, zbot, lines, ground=(232, 224, 200), ink=INK, rim=BRONZE, pad=3, bar=None, scale=1):
    """A plate with lines of capitals, centred at cx, its foot at zbot; `bar` a colour for a short bar at its
    left end. Returns its top."""
    tw = max(text_width(s, scale) for s in lines)
    lh = 7 * scale
    hgt = len(lines) * lh - 2 * scale + 2 * pad
    bw = 6 if bar else 0
    c1 = cx - (tw + bw) // 2 - pad - 1
    c2 = c1 + tw + bw + 2 * pad + 2
    top = zbot + hgt
    w.rect(c1, top, c2, zbot, ground)
    w.frame(c1, top, c2, zbot, rim)
    w.rect(c1 + 1, top - 1, c2 - 1, top - 2, mix(ground, (255, 255, 255), 0.5))
    if bar:
        w.rect(c1 + 2, top - 2, c1 + 2 + bw - 1, zbot + 2, bar)
    for k, s in enumerate(lines):
        w.centre(s, cx + bw // 2, top - pad - k * lh, ink, scale)
    return top


def p_plate(w, spec):
    enamel(w, spec["w"] // 2, spec["head"] + 6, spec["words"], bar=G.PART_COLOURS[spec["part_no"]])


def p_plateside(w, spec):
    cx, at = spec["w"] // 2, spec["at"]
    enamel(w, cx, at + 14, spec["words"], bar=G.PART_COLOURS[spec["part_no"]])
    cz, a = at + 7, spec["arrow"]
    w.rect(cx - 12, cz + 1, cx + 12, cz - 1, INK)
    for i in range(5):
        c = cx + 12 + i if a > 0 else cx - 13 - i
        w.rect(c, cz + 5 - i, c + 1, cz - 5 + i, INK)


def p_danger(w, spec):
    cx, at = spec["w"] // 2, spec["at"]
    c1, c2 = cx - 22, cx + 22
    w.rect(c1, at + 34, c2, at, (236, 232, 222))
    w.frame(c1, at + 34, c2, at, RED, 2)
    w.rect(c1, at + 34, c2, at + 22, RED)
    w.centre("DANGER", cx, at + 31, (244, 240, 232))
    w.centre("33000", cx, at + 18, RED)
    w.centre("VOLTS", cx, at + 10, (30, 28, 28))


def p_window(w, spec):
    """A tall steel-framed window high in a yard's wall, a stone sill and head; dark glass, some lit warm."""
    lit = spec.get("lit")
    c1, c2, lo, hi = 12, 52, 220, 404
    w.rect(c1 - 4, lo, c2 + 4, lo - 6, STONE)
    w.rect(c1 - 4, lo - 5, c2 + 4, lo - 6, shade(STONE, 0.6))
    w.rect(c1 - 2, hi + 8, c2 + 2, hi, shade(STONE, 0.95))
    for z in range(lo, hi):
        for c in range(c1, c2):
            u, v = (c - c1) % 10, (z - lo) % 14
            if u == 0 or v == 0 or c == c2 - 1:
                col = (38, 34, 30)
            elif lit:
                col = jit(shade((236, 206, 146), 0.85 + 0.2 * h32(c // 10, z // 14, 83)), c, z, 84, 0.03)
            else:
                col = jit((58, 56, 54), c // 3, z // 3, 85, 0.08)
                if u == 1 or v == 13:
                    col = shade(col, 1.4)
            w.at(c, z, col)


def p_bhwindow(w, spec):
    c1, c2, lo, hi = 10, 54, 216, 352
    w.rect(c1 - 3, lo, c2 + 3, lo - 5, shade(STONE, 0.7))
    for z in range(lo, hi):
        for c in range(c1, c2):
            u, v = (c - c1) % 11, (z - lo) % 12
            if u == 0 or v == 0 or c == c2 - 1:
                col = (30, 28, 26)
            else:
                g = 0.65 + 0.35 * (z - lo) / (hi - lo)
                col = mix(jit((214, 206, 186), c, z, 86, 0.04), SOOT, 0.55 - 0.3 * g)
            w.at(c, z, col)


def p_pilaster(w, spec):
    """A giant pilaster on the turbine hall's wall: faience, a black plinth, a moulded capital under the rail."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    c1, c2 = (0, W) if W <= 32 else (8, W - 8)
    lo, hi = CLER
    for z in range(F, lo - 24):
        for c in range(c1, c2):
            u = c - c1
            col = tile(shade(CREAM, 1.02), 16, 0.82, seed=87)(u, z)
            if u == 0 or u == 1:
                col = shade(col, 1.2)
            if u >= c2 - c1 - 2:
                col = shade(col, 0.72)
            w.at(c, z, col)
    w.rect(c1, F + 28, c2, F, BLACK)
    w.rect(c1, F + 28, c2, F + 27, shade(BLACK, 1.8))
    for z in range(lo - 40, lo - 24):
        for c in range(c1 - 2 if c1 else 0, c2 + 2 if c2 < W else W):
            w.at(c, z, moulding((214, 204, 176), lo - 24, lo - 40)(c, z))


def p_cplate(w, spec):
    """The chimney's bronze plate: 1933."""
    w.rect(14, 92, 50, 70, shade(BRONZE, 0.75))
    w.rect(16, 90, 48, 72, BRONZE)
    w.rect(16, 90, 48, 89, shade(BRONZE, 1.3))
    for k, ch in enumerate("1933"):
        im = Img(6, 10, (0, 0, 0, 0))
        digit(im, ch, 0, 0, (226, 196, 120), 2)
        w.paste(im, 18 + k * 8, 86)


def p_boiler(w, spec):
    """A boiler's front: riveted black plate; two fire doors low down (a dull amber glow at their slots), a pair
    of gauge glasses, a pressure dial with a brass rim, a valve wheel, the number plate. `gap`: the frame's
    columns, kept clear."""
    W = spec["w"]
    w.fill(w.z0, w.bot, plate((40, 36, 34), 48, 56, seed=88))
    gap = spec.get("gap")

    def clear(c1, c2):
        return not gap or c2 <= gap[0] or c1 >= gap[1]
    for cx in (40, W - 40):                                     # the fire doors
        w.rect(cx - 26, 84, cx + 26, 14, (24, 22, 22))
        w.rect(cx - 22, 78, cx + 22, 20, (54, 50, 46))
        w.frame(cx - 22, 78, cx + 22, 20, (90, 84, 76))
        for z in range(70, 36, -6):
            w.rect(cx - 14, z, cx + 14, z - 2, (120, 70, 30))
            w.rect(cx - 12, z, cx + 12, z - 1, (168, 104, 44))
        w.rect(cx + 14, 54, cx + 20, 48, BRASS)
    layout = dict(gl=(72, W - 72), dial=(W // 2, 210), wheel=(W // 2 + 44, 250), num=(W // 2, 112))
    if gap:
        layout = dict(gl=(gap[1] + 10, W - 14), dial=(gap[1] + 40, 214), wheel=(30, 250), num=(gap[1] + 40, 112))
    for gx in layout["gl"]:                                     # the gauge glasses
        w.rect(gx - 4, 190, gx + 4, 184, BRASS)
        w.rect(gx - 4, 138, gx + 4, 132, BRASS)
        w.rect(gx - 2, 184, gx + 2, 138, (196, 190, 170))
        w.rect(gx - 2, 160, gx + 2, 138, (150, 126, 74))
        w.rect(gx - 1, 184, gx, 138, (240, 236, 224))
    dx, dz = layout["dial"]                                     # the pressure dial
    w.disc(dx, dz, 19, BRASS)
    w.disc(dx, dz, 16, (236, 230, 212))
    for k in range(9):
        t = math.radians(225 - k * 270 / 8)
        w.line(dx + 12 * math.cos(t), dz + 12 * math.sin(t), dx + 15 * math.cos(t), dz + 15 * math.sin(t), INK)
    t = math.radians(225 - 270 * 0.62)
    w.line(dx, dz, dx + 13 * math.cos(t), dz + 13 * math.sin(t), INK)
    w.disc(dx, dz, 2, INK)
    vx, vz = layout["wheel"]                                    # the valve wheel
    w.ring(vx, vz, 10, 13, (60, 56, 52))
    for a in range(0, 360, 72):
        t = math.radians(a)
        w.line(vx, vz, vx + 11 * math.cos(t), vz + 11 * math.sin(t), (70, 66, 60))
    w.disc(vx, vz, 3, BRASS)
    w.rect(vx - 2, vz - 13, vx + 2, vz - 40, (50, 46, 44))
    nx, nz = layout["num"]                                      # the number plate
    w.rect(nx - 16, nz, nx + 16, nz - 18, BRASS)
    w.frame(nx - 16, nz, nx + 16, nz - 18, shade(BRASS, 0.6))
    w.text("NO", nx - 13, nz - 4, (50, 34, 18))
    im = Img(6, 10, (0, 0, 0, 0))
    digit(im, str(spec["n"]), 0, 0, (50, 34, 18), 2)
    w.paste(im, nx + 4, nz - 4)


def p_casing(w, spec):
    """A turbine's lagged casing: warm grey paint, bolted flange lines, the maker's brass plate."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    grey = (150, 142, 128)

    def f(x, z):
        if z in (bot + 48, bot + 47) or x % 160 in (0, 1):
            return shade(grey, 0.6 if z == bot + 47 or x % 160 == 1 else 1.25)
        if (z in (bot + 44, bot + 51) and x % 10 == 5) or (x % 160 in (5, 155) and z % 10 == 5):
            return shade(grey, 1.5)
        if z > top - 4:
            return shade(grey, 1.3 if z == top else 1.1)
        if z <= bot + 6:
            return shade(grey, 0.7)
        return jit(shade(grey, 0.97 + 0.06 * math.sin((z - bot) / 96 * math.pi)), x // 2, z // 2, 89, 0.02)
    w.fill(top, bot, f)
    cx = W // 2
    w.rect(cx - 46, bot + 82, cx + 46, bot + 56, shade(BRASS, 0.7))
    w.rect(cx - 44, bot + 80, cx + 44, bot + 58, BRASS)
    w.rect(cx - 44, bot + 80, cx + 44, bot + 79, shade(BRASS, 1.3))
    ink = (54, 36, 18)
    w.centre(f"NO {spec['n']}", cx, bot + 77, ink)
    w.centre("30 MW 3000 RPM", cx, bot + 68, ink)


def p_tend(w, spec):
    """A transformer's end: its tank, bolted, the rating plate T<n>, a DANGER plate on some."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    g = (82, 80, 76)
    w.fill(top, bot, lambda x, z: shade(g, 1.25 if z == top else 0.7 if z == top - 6 else 0.95) if z > top - 7 else
           jit(g, x // 2, z // 2, 90, 0.03))
    for c in range(6, W, 12):
        w.disc(c, top - 3, 1.2, shade(g, 1.6))
    cx = W // 2
    w.rect(cx - 22, bot + 84, cx + 22, bot + 62, (200, 194, 176))
    w.frame(cx - 22, bot + 84, cx + 22, bot + 62, BRASS, 2)
    w.centre("T" + str(spec["n"]), cx, bot + 81, INK)
    w.centre("33 KV", cx, bot + 72, INK)
    if spec.get("danger"):
        p_danger(w, dict(w=W, at=bot + 18))
    w.rect(cx + 30, bot + 22, cx + 40, bot + 12, (60, 58, 54))
    w.disc(cx + 35, bot + 17, 4, BRASS)


def p_cabinet(w, spec):
    """A switchgear cabinet's long side: two cubicle doors in black enamel, each with a small round meter, a
    handle and a number."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    w.fill(top, bot, lambda x, z: (60, 56, 52) if z > top - 3 else jit((22, 22, 24), x // 2, z // 2, 91, 0.03))
    for k in range(2):
        c1 = 3 + k * (W // 2)
        c2 = c1 + W // 2 - 6
        w.frame(c1, top - 4, c2, bot + 4, (60, 58, 56))
        w.rect(c1 + 1, top - 5, c2 - 1, top - 6, (50, 48, 48))
        mx = (c1 + c2) // 2
        w.disc(mx, top - 18, 9, BRASS)
        w.disc(mx, top - 18, 7, (232, 228, 214))
        w.line(mx, top - 18, mx - 4, top - 14, INK)
        w.rect(c2 - 8, bot + 34, c2 - 5, bot + 20, (180, 176, 168))
        num = str(2 * spec["n"] - 1 + k)
        w.rect(mx - 9, bot + 16, mx + 9, bot + 8, (220, 214, 196))
        im = Img(len(num) * 4, 5, (0, 0, 0, 0))
        for i, ch in enumerate(num):
            digit(im, ch, i * 4, 0, INK, 1)
        w.paste(im, mx - len(num) * 2, bot + 14)


def p_store(w, spec):
    lo = 160
    enamel(w, spec["w"] // 2, lo + 10, ("INSTRUMENT STORE",), bar=G.PART_COLOURS[2])


def board(w, c1, top, c2, bot, frame=BRONZE, ground=PAPER, t=4):
    w.rect(c1, top, c2, bot, frame)
    w.rect(c1 + 1, top - 1, c2 - 1, top - 2, shade(frame, 1.35))
    w.rect(c1 + t, top - t, c2 - t, bot + t, ground)


def p_plan(w, spec):
    """GENERATING STATION: the plan engraved on a bronze-framed cream board: the rooms as outlines, the three
    ways in yellow, green and red from the gatehouse to the switchgear hall, numbered."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 176, F + 44
    board(w, 0, top, W, bot)
    ink = (60, 44, 30)
    w.centre("GENERATING STATION", W // 2, top - 8, ink)
    w.rect(W // 2 - 56, top - 15, W // 2 + 56, top - 16, ink)
    pl = spec["plan"]
    x0, x1, y0, y1 = -100, 9300, 300, 5050
    pc1, pc2, pz1, pz2 = 10, W - 10, bot + 10, top - 22
    s = min((pc2 - pc1) / (x1 - x0), (pz2 - pz1) / (y1 - y0))
    ox = pc1 + ((pc2 - pc1) - (x1 - x0) * s) / 2
    oz = pz1 + ((pz2 - pz1) - (y1 - y0) * s) / 2
    X = lambda x: ox + (x - x0) * s
    Z = lambda y: oz + (y - y0) * s
    for b in pl["boxes"]:
        c1, c2, za, zb = X(b[0]), X(b[2]), Z(b[1]), Z(b[3])
        w.line(c1, za, c2, za, ink)
        w.line(c1, zb, c2, zb, ink)
        w.line(c1, za, c1, zb, ink)
        w.line(c2, za, c2, zb, ink)
    for x, y, r in pl["rounds"]:
        w.ring(X(x), Z(y) + 1, r * s - 0.6, r * s + 0.4, ink)
    for k in (1, 2, 3):
        pts = pl["ways"][k]
        col = shade(G.PART_COLOURS[k], 0.92)
        for a, b in zip(pts, pts[1:]):
            w.line(X(a[0]), Z(a[1]) + 1, X(b[0]), Z(b[1]) + 1, col, 2)
        ex_, ez_ = X(pts[-1][0]), Z(pts[-1][1])           # its number at its end, in the last hall
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k), 0, 0, shade(col, 0.8), 1)
        w.paste(im, int(X(9060)), int(ez_) + 3)
        w.line(ex_, ez_ + 1, X(9040), ez_ + 1, col, 1)
    ex, ey = pl["exit"]
    w.rect(X(ex) - 2, Z(ey) + 3, X(ex) + 2, Z(ey) - 2, ink)


def p_rules(w, spec):
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 156, F + 56
    board(w, 4, top, W - 4, bot, frame=(40, 36, 32), ground=(232, 228, 214), t=3)
    w.rect(8, top - 3, W - 8, top - 4, (120, 112, 100))
    w.centre("SAFETY RULES", W // 2, top - 8, INK)
    w.rect(W // 2 - 38, top - 15, W // 2 + 38, top - 16, INK)
    lines = ["1. NO ONE IS TO WORK ALONE.", "2. KNOW WHERE YOUR MATES ARE", "   AT ALL TIMES.",
             "3. NEVER CLOSE A SWITCH", "   ANOTHER HAS OPENED."]
    for k, s in enumerate(lines):
        w.text(s, 12, top - 22 - k * 9, INK)
    w.text("BY ORDER", W - 12 - text_width("BY ORDER"), bot + 12, shade(INK, 1.6))


def p_shadow(w, spec):
    """A tool shadow board: black outlines of the tools; three of the tools gone from their outlines."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 160, F + 60
    board(w, 0, top, W, bot, frame=(96, 62, 36), ground=(212, 200, 170), t=3)
    sil = (28, 26, 24)
    steel = (164, 162, 156)
    handle = (110, 70, 40)

    def spanner(cx, z1, z2, gone):
        for z in range(z2, z1):
            w.rect(cx - 2, z, cx + 2, z - 1, sil)
        for zz in (z1, z2):
            w.ring(cx, zz, 2, 5, sil)
        if not gone:
            for z in range(z2, z1):
                w.rect(cx - 1, z, cx + 1, z - 1, steel)
            for zz in (z1, z2):
                w.ring(cx, zz, 2.5, 4, steel)

    def hammer(cx, gone):
        w.rect(cx - 2, top - 20, cx + 2, top - 66, sil)
        w.rect(cx - 12, top - 14, cx + 12, top - 24, sil)
        if not gone:
            w.rect(cx - 1, top - 22, cx + 1, top - 65, handle)
            w.rect(cx - 11, top - 15, cx + 11, top - 23, steel)

    def saw(c1, gone):
        for z in range(top - 18, top - 70, -1):
            d = (top - 18 - z) / 52
            w.rect(c1, z, c1 + int(10 + 16 * d), z - 1, sil)
        w.rect(c1 - 4, top - 14, c1 + 8, top - 30, sil)
        if not gone:
            for z in range(top - 20, top - 68, -1):
                d = (top - 18 - z) / 52
                w.rect(c1 + 1, z, c1 + int(8 + 16 * d), z - 1, steel)
            w.rect(c1 - 3, top - 15, c1 + 7, top - 29, handle)

    def calipers(cx, gone):
        for s in (-1, 1):
            w.line(cx, top - 18, cx + s * 10, top - 64, sil, 3)
        w.disc(cx, top - 18, 4, sil)
        if not gone:
            for s in (-1, 1):
                w.line(cx, top - 19, cx + s * 10, top - 63, steel, 1)
            w.disc(cx, top - 18, 2, steel)

    spanner(16, top - 16, top - 50, False)
    spanner(28, top - 16, top - 58, True)
    spanner(40, top - 16, top - 66, False)
    hammer(64, True)
    saw(84, False)
    calipers(132, True)
    spanner(152, top - 16, top - 46, False)
    hammer(174, False)
    w.rect(8, bot + 12, W - 8, bot + 10, (150, 136, 110))


def p_single(w, spec):
    """The single-line diagram: G1 and G2, the three busbars in yellow, green and red, the feeders TOWN,
    WORKS, INSTITUTE each with a load meter: the institute's hard against its stop."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 172, F + 44
    board(w, 0, top, W, bot, frame=(40, 34, 30), ground=PAPER)
    ink = INK
    w.centre("SINGLE LINE DIAGRAM", W // 2, top - 8, ink)
    gz = (top - 40, top - 76)
    for k, gzz in enumerate(gz):
        w.ring(26, gzz, 9, 10.5, ink)
        w.text("G", 20, gzz + 3, ink)
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k + 1), 0, 0, ink, 1)
        w.paste(im, 27, gzz + 3)
        w.line(37, gzz, 52, gzz, ink)
    w.line(52, gz[0] + 6, 52, gz[1] - 30, ink)
    bars = []
    for k in range(3):
        zb = top - 34 - k * 22
        col = shade(G.PART_COLOURS[k + 1], 0.9)
        w.line(60, zb, W - 14, zb, col, 3)
        w.rect(52, zb + 1, 60, zb - 1, ink)
        bars.append(zb)
    names = ("TOWN", "WORKS", "INSTITUTE")
    for k, nm in enumerate(names):
        fx = 92 + k * 58
        w.line(fx, bars[0] + 1, fx, bot + 34, ink)
        for zb in bars:
            w.disc(fx, zb - 1, 2.2, ink)
        mz = bot + 26
        w.ring(fx, mz, 7, 8.5, ink)
        w.disc(fx, mz, 6.5, (244, 238, 222))
        frac = 0.18 if k < 2 else 1.0
        t = math.radians(150 - 120 * frac)
        w.line(fx, mz - 2, fx + 7 * math.cos(t), mz - 2 + 7 * math.sin(t), (150, 30, 26) if k == 2 else ink)
        if k == 2:
            w.rect(fx + 6, mz + 1, fx + 8, mz - 3, ink)
        w.centre(nm, fx, bot + 15, ink)


def p_synchro(w, spec):
    """The synchroscope on a black marble panel, brass-rimmed: its pointer straight up, SLOW to the left, FAST
    to the right; beside it three small meters lettered 1, 2, 3, each with a lamp in its part's colour."""
    W = spec["w"]
    top, bot = 236, 40
    w.rect(0, top, W, bot, BRONZE)
    for z in range(bot + 3, top - 3):
        for c in range(3, W - 3):
            v = math.sin(c * 0.09 + z * 0.05 + 2 * math.sin(z * 0.03))
            col = jit((26, 26, 28), c // 3, z // 3, 92, 0.05)
            if abs(v) < 0.06:
                col = (78, 76, 74)
            w.at(c, z, col)
    cx, cz = 72, 150
    w.disc(cx, cz, 46, shade(BRASS, 0.7))
    w.disc(cx, cz, 43, BRASS)
    w.disc(cx, cz, 38, (238, 232, 214))
    for k in range(24):
        t = math.radians(90 - k * 15)
        r1 = 30 if k % 6 else 26
        w.line(cx + r1 * math.cos(t), cz + r1 * math.sin(t), cx + 35 * math.cos(t), cz + 35 * math.sin(t), INK)
    w.line(cx, cz - 6, cx, cz + 32, INK, 2)
    w.disc(cx, cz, 4, INK)
    w.text("SLOW", cx - 33, cz - 8, INK)
    w.text("FAST", cx + 33 - text_width("FAST"), cz - 8, INK)
    w.centre("SYNCHROSCOPE", cx, cz - 54, (214, 186, 110))
    for k in range(3):
        mx, mz = 158, 196 - k * 54
        w.disc(mx, mz, 15, BRASS)
        w.disc(mx, mz, 12, (236, 230, 212))
        t = math.radians(120 - 40 * k)
        w.line(mx, mz - 3, mx + 10 * math.cos(t), mz - 3 + 10 * math.sin(t), INK)
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k + 1), 0, 0, INK, 1)
        w.paste(im, mx - 1, mz + 8)
        lx = mx + 22
        w.disc(lx, mz, 5, (60, 56, 50))
        w.disc(lx, mz, 4, G.PART_COLOURS[k + 1])
        w.disc(lx - 1, mz + 1, 1.5, mix(G.PART_COLOURS[k + 1], (255, 255, 255), 0.6))


PICTURES = dict(plan=p_plan, rules=p_rules, shadow=p_shadow, single=p_single, synchro=p_synchro, plate=p_plate,
                plateside=p_plateside, danger=p_danger, window=p_window, bhwindow=p_bhwindow, pilaster=p_pilaster,
                cplate=p_cplate, boiler=p_boiler, casing=p_casing, tend=p_tend, cabinet=p_cabinet, store=p_store)


# === flats ====================================================================================================
def f_terrazzo(base=(204, 194, 172), size=64, border=None, seed=100):
    def f(x, y):
        if border and (x % size < 2 or y % size < 2):
            return BLACK
        k = h32(x, y, seed)
        if k < 0.06:
            return jit((96, 84, 70), x, y, seed + 1, 0.2)
        if k < 0.12:
            return jit((238, 234, 224), x, y, seed + 2, 0.05)
        if k < 0.16:
            return jit((150, 120, 90), x, y, seed + 3, 0.1)
        return jit(base, x // 2, y // 2, seed + 4, 0.025)
    return flat(f, size)


def f_plaster():
    def f(x, y):
        if x in (0, 63) or y in (0, 63):
            return (196, 186, 160)
        return jit((230, 222, 200), x // 2, y // 2, 101, 0.02)
    return flat(f)


def f_wood(c, plank=8, along_x=True, seed=102, joint=0.55):
    def f(x, y):
        u, v = (x, y) if along_x else (y, x)
        if v % plank == 0:
            return shade(c, joint)
        k = h32(0, v // plank, seed)
        if (u + int(k * 64)) % 64 == 0:
            return shade(c, joint)
        g = 0.88 + 0.22 * k + 0.05 * math.sin(u * 0.3 + k * 7)
        return jit(shade(c, g), u, v, seed + 1, 0.03)
    return flat(f)


def f_noise(c, amt, seed, scale=1):
    return flat(lambda x, y: jit(c, x // scale, y // scale, seed, amt))


def f_lumps(base, hi, seed, size, glint=None):
    fn = lumps(base, hi, seed, size, glint)
    return flat(lambda x, y: fn(x, y))


def f_setts():
    def f(x, y):
        k = y // 8
        off = (k * 5) % 16
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (60, 56, 52)
        return jit(shade((132, 126, 118), 0.85 + 0.3 * h32((x + off) // 16, k, 103)), x, y, 104, 0.05)
    return flat(f)


def f_slabs(c=(176, 166, 146), s=32, seed=105):
    def f(x, y):
        if x % s == 0 or y % s == 0:
            return shade(c, 0.6)
        return jit(shade(c, 0.9 + 0.2 * h32(x // s, y // s, seed)), x // 2, y // 2, seed + 1, 0.04)
    return flat(f)


def f_drains():
    def f(x, y):
        if 28 <= x < 36:
            if x in (28, 35):
                return (90, 86, 80)
            return (40, 38, 36) if y % 4 else (100, 96, 90)
        if y % 64 == 0 or x % 64 == 0:
            return (120, 116, 108)
        return jit((168, 162, 150), x // 2, y // 2, 106, 0.05)
    return flat(f)


def f_brick_paving():
    def f(x, y):
        k = y // 8
        off = 8 if k % 2 else 0
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (104, 92, 80)
        return jit(shade((128, 70, 50), 0.9 + 0.2 * h32((x + off) // 16, k, 107)), x, y, 108, 0.04)
    return flat(f)


def f_chequer():
    def f(x, y):
        u, v = x % 8, y % 8
        if (u, v) in ((1, 1), (2, 2), (3, 3), (5, 5), (6, 6)) or (x // 8 + y // 8) % 2 and (u, 7 - v) in ((1, 1), (2, 2), (3, 3), (5, 5)):
            return (128, 122, 112)
        return jit((74, 70, 66), x // 2, y // 2, 109, 0.05)
    return flat(f)


def f_grating():
    def f(x, y):
        if x % 8 in (0, 1) or y % 4 == 0:
            return (96, 92, 86) if x % 8 == 0 or y % 4 == 0 else (124, 118, 110)
        return (18, 16, 16)
    return flat(f)


def f_boiler_top():
    def f(x, y):
        d = math.hypot(x - 64, y - 64)
        if 18 < d < 22:
            return (70, 64, 60) if d < 20 else (24, 22, 22)
        if abs(d - 25) < 1 and int(math.degrees(math.atan2(y - 64, x - 64))) % 30 < 8:
            return (110, 104, 96)
        if x % 64 == 0 or y % 64 == 0:
            return (20, 18, 18)
        if (x % 64 in (4, 60) and y % 8 == 4) or (y % 64 in (4, 60) and x % 8 == 4):
            return (96, 90, 84)
        return jit((46, 42, 40), x // 2, y // 2, 110, 0.04)
    return flat(f, 128)


def f_ash():
    return flat(lambda x, y: jit((118, 114, 108), x // 2, y // 2, 111, 0.08) if h32(x, y, 112) > 0.08 else (70, 68, 64))


def f_vault():
    def f(x, y):
        k = y // 8
        off = 16 if k % 2 else 0
        if y % 8 == 0 or (x + off) % 32 == 0:
            return (84, 72, 62)
        return jit(shade((112, 62, 44), 0.85 + 0.2 * h32((x + off) // 32, k, 113)), x, y, 114, 0.04)
    return flat(f)


def f_quarry():
    def f(x, y):
        if x % 16 == 0 or y % 16 == 0:
            return (110, 96, 84)
        return jit(shade((150, 74, 52), 0.9 + 0.2 * h32(x // 16, y // 16, 115)), x, y, 116, 0.03)
    return flat(f)


def f_pump_top():
    def f(x, y):
        d = math.hypot(x - 64 + 0.5, y - 64 + 0.5)
        if d < 26:
            if d > 23:
                return (90, 86, 80)
            return jit((132, 126, 116), x, y, 117, 0.03)
        if abs(d - 30) < 2 and int(math.degrees(math.atan2(y - 64, x - 64)) + 360) % 30 < 10:
            return (176, 168, 150)
        return jit(STEEL, x // 2, y // 2, 118, 0.03)
    return flat(f, 128)


def f_lagged_top():
    return flat(lambda x, y: shade(BLACK, 1.2) if x % 64 < 5 else jit((220, 210, 184), x, y // 2, 119, 0.03))


def f_big_terrazzo():
    return f_terrazzo((210, 204, 188), 128, border=True, seed=120)


def f_roof():
    """Trusses and glazing: panes of pale glass between black bars, a lattice truss along y every 128."""
    def f(x, y):
        if 56 <= x <= 71:
            if x in (56, 71) or (x - 56 + y) % 16 in (0, 1) or (71 - x + y) % 16 in (0, 1):
                return (30, 28, 28)
            return (210, 206, 194)
        if x % 16 in (0, 1) or y % 32 in (0, 1):
            return (40, 38, 36)
        g = 0.94 + 0.1 * ((x % 16) + (y % 32)) / 46
        return jit(shade((226, 222, 208), g), x, y, 121, 0.02)
    return flat(f, 128)


def f_casing_top():
    def f(x, y):
        if y % 64 in (31, 32):
            return (90, 86, 80)
        if y % 64 in (28, 35) and x % 8 == 4:
            return (190, 186, 176)
        return jit((156, 152, 144), x // 2, y // 4, 122, 0.04)
    return flat(f)


def f_plate_floor(c=(90, 84, 78), seed=123):
    w = Wall(64, 64, 64)
    w.fill(64, 0, plate(c, 32, 64, seed=seed))
    return w.im


def f_wood_block():
    def f(x, y):
        bx, by = x // 16, y // 8
        if y % 8 == 0 or (x + (8 if by % 2 else 0)) % 16 == 0:
            return (70, 46, 28)
        k = h32((x + (8 if by % 2 else 0)) // 16, by, 124)
        return jit(shade((130, 88, 52), 0.85 + 0.25 * k), x, y, 125, 0.05)
    return flat(f)


def f_lathe_top():
    def f(x, y):
        v = y % 64
        if 20 <= v < 26 or 38 <= v < 44:
            return (176, 172, 164) if v in (20, 38) else (140, 136, 128)
        return jit((52, 50, 48), x // 2, y // 2, 126, 0.05)
    return flat(f)


def f_boards_beams():
    def f(x, y):
        if 26 <= y <= 37:
            return (24, 22, 22) if y in (26, 37) else shade((50, 46, 44), 1.2 if y in (27, 36) else 1)
        if y % 8 == 0:
            return (60, 42, 28)
        return jit(shade((132, 96, 62), 0.9 + 0.2 * h32(0, y // 8, 127)), x, y, 128, 0.04)
    return flat(f)


def f_cables(along_x):
    def f(x, y):
        u, v = (x, y) if along_x else (y, x)
        k = v % 6
        if k == 0:
            return (70, 66, 60)
        g = (0.0, 0.7, 1.4, 1.6, 1.1, 0.6)[k]
        return jit(shade((26, 24, 24), g), u // 8, v, 129, 0.05)
    return flat(f)


def f_concrete(c=(150, 146, 138), seed=130):
    def f(x, y):
        if x % 64 == 0 or y % 64 == 0:
            return shade(c, 0.8)
        return jit(c, x // 2, y // 2, seed, 0.05)
    return flat(f)


def f_trans_top():
    def f(x, y):
        for cx in (16, 48):
            d = math.hypot(x - cx + 0.5, y - 32 + 0.5)
            if d < 9:
                return (200, 190, 170) if d < 4 else (120, 112, 100) if d < 7 else (40, 38, 36)
        if x % 64 in (0, 63) or y % 64 in (0, 63):
            return (48, 46, 44)
        return jit((86, 84, 80), x // 2, y // 2, 131, 0.04)
    return flat(f)


def f_dry_grass():
    def f(x, y):
        k = h32(x, y, 132)
        base = mix((132, 112, 76), (156, 138, 96), h32(x // 3, y // 5, 133))
        if k < 0.2:
            return shade(base, 1.2)
        if k > 0.82:
            return mix(base, (92, 74, 52), 0.6)
        return jit(base, x, y, 134, 0.06)
    return flat(f)


def f_wet_concrete():
    def f(x, y):
        c = jit((116, 112, 104), x // 2, y // 2, 135, 0.06)
        if y % 32 in (15, 16):
            return (60, 58, 54)
        s = 0.5 + 0.5 * math.sin(x * 0.11 + 2 * math.sin(y * 0.07))
        return mix(c, (70, 66, 60), 0.4 * s * h32(x // 6, y // 6, 136))
    return flat(f)


def f_lino():
    def f(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return (82, 56, 38)
        return jit((112, 74, 48), x // 2, y // 2, 137, 0.04)
    return flat(f)


def f_marble_chequer():
    def f(x, y):
        black = (x // 64 + y // 64) % 2
        v = math.sin(x * 0.12 + y * 0.05 + 3 * math.sin(y * 0.03 + x * 0.02))
        if black:
            col = jit((30, 30, 32), x // 4, y // 4, 138, 0.05)
            if abs(v) < 0.06:
                col = (90, 88, 86)
        else:
            col = jit((226, 222, 208), x // 4, y // 4, 139, 0.03)
            if abs(v) < 0.06:
                col = (160, 156, 148)
        if x % 64 == 0 or y % 64 == 0:
            col = shade(col, 0.75)
        return col
    return flat(f, 128)


def f_coffers():
    def f(x, y):
        u, v = x % 64, y % 64
        d = min(u, v, 63 - u, 63 - v)
        if d < 6:
            return jit((228, 220, 200), x, y, 140, 0.02) if d > 1 else (196, 186, 162)
        if d < 10:
            return (204, 194, 170) if (u < 32) == (v < 32) else (214, 204, 182)
        return jit((236, 230, 214), x // 2, y // 2, 141, 0.015)
    return flat(f, 128)


def f_slate_top():
    return flat(lambda x, y: (60, 58, 56) if x % 64 in (0, 63) or y % 64 in (0, 63) else jit((30, 30, 32), x // 2, y // 2, 142, 0.04))


def f_cab_top():
    return flat(lambda x, y: (70, 66, 62) if x % 64 < 3 or y % 64 < 3 else jit((24, 24, 26), x // 2, y // 2, 143, 0.03))


FLATS = dict(
    TZ=lambda: f_terrazzo(), PK=f_plaster, TK=lambda: f_wood(TEAK, 8, True, 144, 0.7),
    CN=lambda: f_lumps((58, 54, 50), (120, 114, 106), 145, 3), CL=lambda: f_lumps((34, 32, 32), (140, 136, 130), 146, 6, (200, 196, 188)),
    ER=lambda: f_lumps((104, 84, 60), (140, 122, 98), 147, 5), ST=f_setts, SB=lambda: f_slabs(), CD=f_drains,
    GV=lambda: f_lumps((176, 172, 160), (214, 210, 200), 148, 3), BP=f_brick_paving, CQ=f_chequer, GR=f_grating,
    BT=f_boiler_top, AS=f_ash, BV=f_vault, QT=f_quarry, PT=f_pump_top, LG=f_lagged_top, TT=f_big_terrazzo,
    RG=f_roof, CS=f_casing_top, SP=lambda: f_plate_floor(), WB=f_wood_block, BB=lambda: f_wood((150, 108, 66), 8, True, 149),
    LT=f_lathe_top, KB=f_boards_beams, DP=lambda: f_plate_floor((60, 56, 52), 150), CA=lambda: f_cables(True),
    CB=lambda: f_cables(False), CF=lambda: f_concrete(), KC=lambda: f_concrete((140, 136, 128), 151), TO=f_trans_top,
    PN=lambda: f_concrete((176, 170, 160), 152), DG=f_dry_grass, WC=f_wet_concrete, LI=f_lino, RT=f_slate_top,
    MC=f_marble_chequer, KF=f_coffers, TS=lambda: f_wood(TEAK, 8, False, 153, 0.6), SC=f_cab_top,
    KS=lambda: f_slabs((168, 162, 150), 64, 154), TB=lambda: f_wood((52, 40, 30), 12, True, 155, 0.5))


# === the sky ==================================================================================================
def sky():
    """A fine afternoon: a pale hazy sky, high thin cloud drawn out in streaks, warm near the horizon (no blue:
    the doors are BLUE)."""
    W, H = 1024, 256
    im = Img(W, H)
    for y in range(H):
        t = y / (H - 1)
        base = mix((198, 198, 194), (240, 226, 198), t ** 1.6)
        for x in range(W):
            u = x / W * 2 * math.pi
            c = 0.5 + 0.25 * math.sin(3 * u + y / 17.0 + math.sin(5 * u) * 1.5) + 0.25 * math.sin(11 * u - y / 9.0)
            streak = max(0.0, math.sin(y / 6.0 + 4 * math.sin(2 * u + 1.3) + 0.6 * math.sin(9 * u)))
            k = max(0.0, c - 0.45) * streak * (1 - 0.6 * t)
            col = mix(base, (250, 248, 242), min(1, k * 1.6))
            im.px[y * W + x] = [col[0], col[1], col[2], 255]
    return im
