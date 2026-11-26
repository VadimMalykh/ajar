"""MAP33's look 3, "Cold Reserve": the station of look 1 (the 1930s brick and faience) thirty years after its
last coal, shut but kept in cold reserve, and nobody has cleaned or painted anything since. Corrugated iron
where walls were patched, rust runs from every fixing, flaking whitewash and oil paint, fallen tiles, dust,
cold boilers, cracked dial glasses, stained ceilings. Dry and stale, not a ruin: walls and roofs stand,
nothing grows. The palette: rust browns, dark iron, soot, dirty whitewash and bone, dull brown brick, dust
buff; no blue, violet or pink, no bluish grey, nothing green; yellow, green and red only in the phase band
(faded and flaking, a quarter of it gone in small bites), the three ways on the plan and the diagram, the
synchroscope's three lamps, and red on DANGER plates. The slots are tools/gfx_power.py's; the map's side is
tools/power33.py. Middle values stay in about 80 to 160 so that monsters show against walls and floors
(dirty is not dark); only soot, the ash tunnel and the pits go darker.
"""
import math

import gfx_power as G
from gfx import Img, digit, text as gtext
from gfx_power import Wall, flat, h32, jit, mix, shade, text_width

# --- the palette --------------------------------------------------------------------------------------------
BRICK, MORTAR = (112, 76, 58), (124, 112, 96)     # dull brown brick, dirty mortar
ENG = (70, 54, 46)                               # engineering brick
WASH = (178, 168, 140)                           # yellowed whitewash
WASH_GREY = (150, 144, 130)                      # whitewash gone grey (the boiler house)
PLASTER = (146, 130, 104)                        # bare plaster where the wash has come away
PAINT = (98, 72, 52)                             # brown oil paint (dadoes)
BONE = (192, 182, 154)
FAIENCE = (182, 172, 146)                        # ivory faience, crazed and dirty
CREAM = (176, 164, 132)
STONE = (164, 150, 124)
GRANITE = (124, 118, 108)
DARK = (42, 38, 34)                              # what was black: bands, skirtings
SOOT = (34, 30, 28)
IRON = (66, 58, 52)
STEEL = (110, 104, 94)
RUST = (116, 74, 48)
RUST_D = (82, 54, 38)
RUST_L = (140, 98, 66)
CORR = (92, 86, 78)                              # corrugated iron, dark warm grey
DUST = (166, 152, 124)
GRIME = (72, 60, 48)
LIME = (176, 168, 148)                           # pale lime runs (damp brick)
BRONZE = (100, 78, 52)                           # bronze and brass, tarnished
BRASS = (146, 120, 74)
WALNUT = (80, 60, 44)
TEAK = (96, 68, 48)
PAPER = (204, 190, 150)                          # yellowed paper
INK = (48, 40, 32)
CHALK = (198, 194, 182)
RED = (172, 52, 44)                              # DANGER plates only (faded)
BED = (116, 106, 92)                             # the mortar bed under a fallen tile


# === noise ===================================================================================================
def vnoise(x, z, cell, seed, P=0, PZ=0):
    """Smooth value noise in [0, 1), periodic in x with period P (and in z with PZ) when given (P % cell == 0)."""
    gx, rx = divmod(x, cell)
    gz, rz = divmod(z, cell)
    fx, fz = rx / cell, rz / cell
    fx = fx * fx * (3 - 2 * fx)
    fz = fz * fz * (3 - 2 * fz)
    gx1, gz1 = gx + 1, gz + 1
    if P:
        n = P // cell
        gx, gx1 = gx % n, gx1 % n
    if PZ:
        n = PZ // cell
        gz, gz1 = gz % n, gz1 % n
    a, b = h32(gx, gz, seed), h32(gx1, gz, seed)
    c, d = h32(gx, gz1, seed), h32(gx1, gz1, seed)
    return a + (b - a) * fx + (c - a) * fz + (a - b - c + d) * fx * fz


def fbm(x, z, seed, P=0, c1=16, c2=4, PZ=0):
    return 0.68 * vnoise(x, z, c1, seed, P, PZ) + 0.32 * vnoise(x, z, c2, seed + 1, P, PZ)


# === patterns: f(x, z) -> colour ==============================================================================
def brick(c, mortar=MORTAR, course=8, length=32, var=0.1, seed=2):
    def f(x, z):
        kz = (z - 1) // course
        off = length // 2 if kz % 2 else 0
        if z % course == 0 or (x + off) % length == 0:
            return jit(mortar, x, z, seed + 5, 0.07)
        k = h32((x + off) // length, kz, seed)
        g = 1 + (k - 0.5) * 2 * var
        if z % course == course - 1:
            g *= 0.9
        if h32(x, z, seed + 7) < 0.05:                      # spalled pits in the faces
            g *= 0.8
        return jit(shade(c, g), x, z, seed, 0.05)
    return f


def ashlar(c, course=32, block=64, seed=5, joint=0.66):
    def f(x, z):
        kz = (z - 1) // course
        o = block // 2 if kz % 2 else 0
        if z % course == 0 or (x + o) % block == 0:
            return jit(shade(c, joint), x, z, seed + 3, 0.06)
        k = h32((x + o) // block, kz, seed)
        g = 1 + (k - 0.5) * 0.14 + (0.05 if z % course == course - 1 else 0)
        return jit(shade(c, g), x // 2, z // 2, seed, 0.06)
    return f


def plaster(c, seed=6, amt=0.03):
    return lambda x, z: jit(c, x // 2, z // 2, seed, amt)


def crazed(c, s=16, sh=None, seed=1, gone=0.0, P=64, grout=0.72, gone_seed=None):
    """Old glazed tile: crazing in every tile, a few tiles fallen (the bed shows), dirt in the joints."""
    sh = sh or s
    gs = seed + 300 if gone_seed is None else gone_seed

    def f(x, z):
        tx, tz = x // s, (z - 1) // sh
        if gone and vnoise(tx * s, tz * sh, 32, gs, P) * 0.7 + h32(tx, tz, gs + 1) * 0.3 < gone:
            g = 0.9 + 0.12 * h32(x // 3, z // 2, gs + 2)
            if (x + z) % 5 == 0:
                g *= 0.86                                   # the comb marks in the bed
            return shade(BED, g)
        if x % s == 0 or z % sh == 0:
            return jit(shade(c, grout), x, z, seed + 9, 0.04)
        k = h32(tx, tz, seed)
        g = 1 + (k - 0.5) * 0.09 + (0.05 if (z % sh == sh - 1 or x % s == 1) else 0)
        u, v = x % s, z % sh
        if abs(math.sin(u * 0.9 + v * 0.37 + k * 7)) < 0.07 or abs(math.sin(u * 0.31 - v * 0.83 + k * 3)) < 0.06:
            g *= 0.86                                       # crazing
        return jit(shade(c, g), x, z, seed, 0.018)
    return f


def peel(top, under, cover, seed, P, cell=16, fine=4):
    """Paint (top) come away in patches to what is under it: where the noise is under `cover`."""
    def f(x, z):
        n = 0.68 * vnoise(x, z, cell, seed, P) + 0.32 * vnoise(x, z, fine, seed + 1, P)
        if n < cover:
            c = under(x, z)
            return shade(c, 0.72) if n > cover - 0.016 else c
        c = top(x, z)
        return shade(c, 1.12) if n < cover + 0.014 else c
    return f


def plate(c, seam=64, pw=64, seed=4, rivet=8, rust=0.4, P=64):
    """Riveted plate, rusted: seams every `seam` of height and `pw` along, rivets along them, rust in blooms,
    and a brown run under every rivet."""
    def f(x, z):
        m, u = z % seam, x % pw
        if m == 0 or u == 0:
            return shade(c, 0.55)
        if m == 1 or u == 1 or u == pw - 1:
            return shade(c, 1.18 if m == 1 else 0.8)
        if (m in (5, seam - 4) and u % rivet == 4) or (u in (5, pw - 5) and m % rivet == 4):
            return shade(RUST_L, 1.0)
        if (m in (4, seam - 5) and u % rivet == 4) or (u in (4, pw - 6) and m % rivet == 5):
            return shade(c, 0.6)
        g = 1 + 0.04 * math.sin(u * math.pi / (pw / 2)) + (h32(x // 4, z // 6, seed) - 0.5) * 0.06
        col = shade(c, g)
        t = rust * vnoise(x, z, 16, seed + 2, P) ** 1.5
        col = mix(col, RUST, t)
        # runs under the rivet rows: from the row at m == seam - 4 (top of a plate) and m == 5
        if u % rivet in (3, 4, 5):
            for src in (seam - 4, 5):
                d = src - m
                if 0 < d:
                    k = h32(x // rivet, (z - m) // seam * 2 + (src == 5), seed + 3)
                    L = 4 + 26 * k
                    if k > 0.25 and d < L:
                        col = mix(col, RUST_D if u % rivet == 4 else RUST, 0.6 * (1 - d / L))
                        break
        return col
    return f


def solid(c, amt=0.03, seed=7):
    return lambda x, z: jit(c, x // 2, z // 2, seed, amt)


def moulding(c, top, bot):
    def f(x, z):
        k = (top - z) % 6
        g = (1.2, 1.08, 1.0, 0.95, 0.8, 0.62)[k]
        return jit(shade(c, g), x, z, 13, 0.03)
    return f


def lit_band(c):
    def make(top, bot):
        def f(x, z):
            if z == top:
                return shade(c, 1.25)
            if z == bot + 1:
                return shade(c, 0.6)
            return jit(c, x, z, 11, 0.04)
        return f
    return make


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
        g = 0.78 + 0.42 * kb - 0.045 * best
        col = shade(base, max(0.45, g))
        if glint and best < 0.9 and kb > 0.97:
            return glint
        if best < 1 and kb > 0.75:
            col = mix(col, hi, 0.25)
        return col
    return f


# === weathering, over what is drawn ==========================================================================
def runs(w, srcs, col, density, strength, seed, length, width=2, zbot=None):
    """Runs down from the heights srcs: streaks of varying length (rust under a rail, soot, lime)."""
    top = max(srcs)
    bot = w.bot if zbot is None else zbot

    def f(x, z, c):
        g = x // width
        for i, s in enumerate(srcs):
            d = s - z
            if d >= 0:
                k = h32(g, i, seed)
                if k < density:
                    L = length * (0.25 + 0.75 * h32(g, i, seed + 1))
                    if d < L:
                        t = strength * (1 - d / L) ** 0.8 * (0.75 + 0.25 * h32(x, i, seed + 2))
                        c = mix(c, col, t)
        return c
    w.tint(top, bot, f)


def stains(w, ztop, zbot, col, amt, seed, cell=32, cut=0.45):
    """Patchy stains: where the slow noise is over `cut`, toward col."""
    P = w.period

    def f(x, z, c):
        n = 0.75 * vnoise(x, z, cell, seed, P) + 0.25 * vnoise(x, z, 8, seed + 1, P)
        if n > cut:
            return mix(c, col, min(1, (n - cut) * 2.2) * amt)
        return c
    w.tint(ztop, zbot, f)


def gradient(w, zfrom, zto, col, most, seed=10):
    """Toward col more and more from zfrom to zto (either way up): soot up high, grime down low."""
    lo, hi = min(zfrom, zto), max(zfrom, zto)
    span = max(1, zto - zfrom)

    def f(x, z, c):
        t = most * min(1, max(0, (z - zfrom) / span)) ** 1.3
        t *= 0.8 + 0.4 * h32(x // 4, z // 16, seed)
        return mix(c, col, min(1, t))
    w.tint(hi, lo, f)


def cracks(w, ztop, zbot, col, seed, cell=24, thin=0.012, keep=0.55, P=None):
    """Thin meandering cracks: contour lines of a slow noise, only where a second noise allows."""
    P = P or w.period

    def f(x, z, c):
        if vnoise(x, z, 32, seed + 1, P) < keep:
            return c
        n = vnoise(x, z, cell, seed, P)
        if abs(n - 0.5) < thin:
            return mix(c, col, 0.75)
        return c
    w.tint(ztop, zbot, f)


# --- the phase band: faded and flaking --------------------------------------------------------------------
_BITES = {}


def bites(P, seed):
    """Which columns of a band of period P are gone (0 kept, 1 gone, 2 chipped at the top, 3 at the foot):
    small bites, about a quarter of the length, none longer than 14."""
    key = (P, seed)
    if key not in _BITES:
        gone = [0] * P
        x = int(h32(seed, 0, 401) * P)
        total, i = 0, 0
        while True:
            solid_ = 10 + int(h32(i, 1, seed) * 26)
            gap = 3 + int(h32(i, 2, seed) * 12)
            if total + solid_ + gap > P - 8:
                break
            for k in range(gap):
                gone[(x + solid_ + k) % P] = 1
            for k, side in ((-1, 2 + (i % 2)), (gap, 3 - (i % 2))):
                gone[(x + solid_ + k) % P] = side
            x += solid_ + gap
            total += solid_ + gap
            i += 1
        _BITES[key] = gone
    return _BITES[key]


def band_colour(part):
    return shade(mix(G.PART_COLOURS[part], (124, 112, 96), 0.2), 0.94)


def band(w, F, part, manner="tile"):
    """The phase band from F + 72 to F + 80 between two dark lines, faded, with a quarter of it gone in small
    bites (tile: the bed shows; paint, on iron: the iron shows, and the paint keeps the iron's shading)."""
    if not part:
        return
    lo, hi = F + G.BAND[0], F + G.BAND[1]
    col = band_colour(part)
    gone = bites(w.period, 17 + 13 * part + (F // 8) % 7)
    paint = manner == "paint"

    def under(x, z, c):
        if paint:
            return c
        return jit(BED, x, z, 403, 0.07)

    def f(x, z, c):
        g = gone[x]
        if z > hi:                                          # the dark lines
            if g == 1 and h32(x // 2, 0, 404) < 0.5:
                return under(x, z, c)
            if paint:
                return shade(DARK, 0.6 + 0.6 * lum(c) / 90)
            return shade(DARK, 1.0 if z == hi + 1 else 1.4)
        if z <= lo:
            if g == 1 and h32(x // 2, 1, 404) < 0.5:
                return under(x, z, c)
            if paint:
                return shade(DARK, 0.6 + 0.6 * lum(c) / 90)
            return shade(DARK, 1.0 if z == lo else 0.8)
        if g == 1 or (g == 2 and z > hi - 3) or (g == 3 and z <= lo + 3):
            return under(x, z, c)
        if (z == hi and h32(x, 2, 405) < 0.14) or (z == lo + 1 and h32(x, 3, 405) < 0.14):
            return under(x, z, c)                           # chips along its edges
        if paint:
            return shade(col, max(0.55, min(1.25, 0.25 + 0.75 * lum(c) / 86)) * (0.94 + 0.06 * h32(x // 3, z, 406)))
        if x % 16 == 0:
            return shade(col, 0.6)
        if z == hi:
            return mix(col, (236, 226, 204), 0.3)
        if z == lo + 1:
            return shade(col, 0.78)
        k = h32(x // 16, 0, 41)
        cc = jit(shade(col, 0.95 + 0.08 * k), x, z, 407, 0.03)
        u, v = x % 16, z % 8
        if abs(math.sin(u * 0.9 + v * 0.5 + k * 7)) < 0.08:
            cc = shade(cc, 0.86)                            # crazing
        return cc
    w.tint(hi + 2, lo - 2, f)


def lum(c):
    return (c[0] * 3 + c[1] * 6 + c[2]) / 10


def skirting(w, F, h=8):
    w.fill(F + h, max(w.bot, F - 8), lambda x, z: shade(DARK, 1.3) if z == F + h else
           jit(DARK, x // 2, z, 12, 0.08) if h32(x // 3, z // 3, 412) > 0.12 else jit(BED, x, z, 413, 0.06))


# === the walls ================================================================================================
def w_painted(w, F, part, top, dado=112, cornice=14):
    """Flaking brown oil paint to the dado over yellowed whitewash that has come away to the plaster; a stained
    cornice under the ceiling; water stains down from it; grime low down; the band in the paint."""
    P = w.period
    under = plaster(PLASTER, 501, 0.05)
    w.fill(w.z0, w.bot, peel(plaster(WASH, 502), under, 0.36, 503, P))
    w.fill(top, top - cornice, moulding((166, 154, 128), top, top - cornice))
    w.fill(F + dado + 4, F + dado, lambda x, z: shade(GRIME, 1.25 if z == F + dado + 4 else 0.9))
    w.fill(F + dado, F + 8, peel(plaster(PAINT, 504, 0.04), under, 0.3, 505, P, cell=8))
    stains(w, top, F + dado, (130, 104, 70), 0.55, 506, cell=32, cut=0.5)
    runs(w, [top - cornice], (120, 96, 66), 0.25, 0.35, 507, 70, width=4)
    gradient(w, F + 40, F, GRIME, 0.35, 508)
    skirting(w, F)
    band(w, F, part)


def m_TD(w, F, part, top):
    w_painted(w, F, part, top)


def m_CO(w, F, part, top):
    w_painted(w, F, part, top, dado=96, cornice=8)


def m_GP(w, F, part):
    """The gatehouse's pillars: faience all the way, crazed and dirty, a few tiles gone; a stained capital."""
    w.fill(w.z0, w.bot, crazed(FAIENCE, 16, seed=3, gone=0.12, P=w.period))
    w.fill(w.z0, w.z0 - 16, moulding((160, 150, 124), w.z0, w.z0 - 16))
    w.fill(F + 120, F + 114, lit_band(DARK)(F + 120, F + 114))
    gradient(w, F + 48, F, GRIME, 0.3, 511)
    runs(w, [w.z0 - 16], (110, 90, 64), 0.2, 0.3, 512, 90, width=3)
    skirting(w, F, 12)
    band(w, F, part)


def m_CT(w):
    """The counter's front: dark teak, scarred and scratched, its edges worn pale, on a chipped plinth."""
    def f(x, z):
        u = x % 32
        if z <= 4:
            return jit(DARK, x, z, 14, 0.08)
        if z >= 37:
            return shade(TEAK, 1.25 if z == 40 else 0.78)
        if u in (0, 1, 30, 31) or z in (5, 6, 7, 34, 35, 36):
            col = jit(shade(TEAK, 0.85), x, z, 15, 0.05)
        elif u in (4, 27) or z in (10, 31):
            col = shade(TEAK, 0.7 if u == 27 or z == 10 else 1.15)
        else:
            g = 1 + 0.06 * math.sin(z * 0.9 + u * 0.15) + (h32(u, 0, 16) - 0.5) * 0.05
            col = shade(TEAK, g)
        s = (x * 3 + z * 2) % 23
        if s == 0 and h32(x // 6, z // 6, 517) < 0.4:
            col = mix(col, (150, 124, 94), 0.6)             # scratches
        if h32(x // 2, z // 2, 518) < 0.03:
            col = shade(col, 0.7)                           # dents
        return col
    w.fill(w.z0, w.bot, f)
    stains(w, w.z0, w.bot, GRIME, 0.4, 519, cell=16, cut=0.55)


def m_SK(w):
    w.fill(w.z0, w.bot, ashlar(GRANITE, 16, 32, seed=17))
    stains(w, w.z0, w.bot, DUST, 0.35, 521, cell=16, cut=0.4)


def m_RI(w, kind):
    c = {"stone": (156, 144, 122), "marble": (164, 158, 146)}[kind]

    def f(x, z):
        if z % 16 == 0:
            return shade(DUST, 1.0) if h32(x // 2, z, 522) < 0.6 else shade(c, 1.2)
        if z % 16 == 15:
            return shade(c, 0.6)
        if z % 8 == 0:
            return shade(c, 0.85)
        return jit(c, x // 2, z // 2, 18, 0.05)
    w.fill(w.z0, w.bot, f)
    stains(w, w.z0, w.bot, GRIME, 0.3, 523, cell=16)


def m_YD(w, F, part, damp=0):
    """Out of doors: a dull brown brick foot (64 high, stained) under a concrete sill; above it corrugated iron
    sheets in rows, rust running from their fixings, some sheets of another age (lighter, or rustier), a patch,
    a curled corner; a rusty steel stanchion every 256; a plain flashing under the sky; the band painted on
    the iron, flaking."""
    P = w.period
    foot = F + 64
    br = brick(BRICK, seed=531)
    sky = G.SKY_TOP

    def iron(x, z):
        zr = z - foot - 4
        sx, sz = x // 32, (zr - 1) // 96
        u = x % 8
        g = 0.82 + 0.26 * math.sin(2 * math.pi * (u + 0.5) / 8)
        k = h32(sx, sz, 532)
        base = CORR
        if k < 0.14:
            base = (130, 124, 112)                          # a newer sheet, galvanised
        elif k < 0.3:
            base = mix(CORR, RUST, 0.6)                     # an older one, rustier
        col = jit(shade(base, g), x // 2, z // 3, 533, 0.03)
        col = mix(col, RUST, 0.45 * vnoise(x, z, 32, 534, P) ** 2 + (0.25 if k < 0.3 and k >= 0.14 else 0)
                  * vnoise(x, z, 8, 535, P))
        if x % 32 == 0:
            return shade(col, 0.55)                         # the side laps
        if x % 32 == 1:
            col = shade(col, 1.12)
        m = zr % 96
        if m == 0:
            return shade(col, 0.5)                          # the end laps
        if m == 1:
            col = shade(col, 1.15)
        # the fixings: on every other crest, 3 under a lap and on the rail half way; rust runs down from them
        d = (93 - zr) % 48
        fi = (zr + d) // 48
        xb = x % 16
        if d < 2 and xb in (4, 5):
            return (128, 92, 64)
        if xb in (3, 4, 5, 6):
            k2 = h32(x // 16, fi, 536)
            L = 10 + 46 * h32(x // 16, fi, 537)
            if k2 < 0.62 and d < L:
                t = (0.62 if xb in (4, 5) else 0.28) * (1 - d / L) ** 0.8
                col = mix(col, RUST_D, t)
        return col

    def f(x, z):
        d = min(x, P - x)
        if d < 9 and z > foot - 8:                          # the stanchion: an I-section, rusty
            if d == 8:
                return (36, 32, 28)
            g = (1.0, 1.0, 0.97, 0.95, 0.95, 1.0, 1.1, 1.2)[d] if x < P // 2 else (1.0, 0.95, 0.9, 0.85, 0.85, 0.82, 0.75, 0.7)[d]
            col = shade(mix(STEEL, RUST, 0.5 + 0.4 * vnoise(x, z, 8, 538, P)), g)
            if (z - foot) % 48 in (2, 3) and d in (5, 6):
                col = (60, 48, 40)                          # the rail cleats
            return jit(col, x, z // 2, 539, 0.04)
        if z <= foot:
            return br(x, z)
        if z <= foot + 4:
            return shade((132, 124, 110), 1.2 if z == foot + 4 else 0.9 if z > foot + 1 else 0.6)
        return iron(x, z)
    w.fill(w.z0, w.bot, f)
    # the patch: a smaller sheet bolted over a hole, rustier, its edge in shadow
    pc1, pc2, pt, pb = 148, 176, F + 236, F + 204

    def patch(x, z, c):
        if pc1 <= x < pc2 and pb < z <= pt:
            if x in (pc1, pc2 - 1) or z in (pt, pb + 1):
                return shade(c, 0.6)
            if (x - pc1) % 8 == 4 and z in (pt - 2, pb + 3) or x in (pc1 + 2, pc2 - 3) and (z - pb) % 8 == 4:
                return (130, 94, 66)
            return mix(c, RUST, 0.35 + 0.3 * vnoise(x, z, 4, 540, P))
        if pc1 <= x < pc2 + 1 and pb - 2 < z <= pb:
            return shade(c, 0.7)
        return c
    w.tint(pt, pb - 2, patch)
    # a curled corner: the bottom right corner of one sheet in the second row lifts away from the rail
    cx, cz = 95, foot + 4 + 97

    def curl(x, z, c):
        s = (cx - x) + (z - cz)
        if 0 <= cx - x < 16 and 0 <= z - cz < 16:
            if s < 11:
                return jit((34, 30, 26), x, z, 541, 0.08)    # the dark behind
            if s < 14:
                return shade(mix(CORR, RUST, 0.4), 1.35 if s < 12 else 1.1)   # the lifted edge, lit
        return c
    w.tint(cz + 16, cz, curl)
    # the foot: rising damp's tide, splash grime, dark drips from the sill
    gradient(w, F + 24, F, GRIME, 0.4, 542)
    stains(w, foot, w.bot, (84, 62, 48), 0.5, 543, cell=32, cut=0.5)
    runs(w, [foot], (66, 52, 42), 0.3, 0.4, 544, 40, width=3)
    # the flashing under the sky
    w.fill(sky, sky - 10, lambda x, z: shade((96, 88, 76), 1.25 if z == sky else 0.55 if z == sky - 9 else
                                             0.95 + 0.1 * h32(x // 8, 0, 545)))
    runs(w, [sky - 10], RUST, 0.2, 0.45, 546, 80, width=2)
    if damp:
        def wet(x, z, col):
            e = F + 40 - int(vnoise(x, 0, 16, 547, P) * 14)
            if z <= e:
                col = mix(col, (58, 48, 40), 0.4)
                if h32(x, z // 2, 548) < 0.08:
                    col = mix(col, LIME, 0.5)               # efflorescence
            elif z <= e + 2:
                col = mix(col, LIME, 0.35)                  # the tide line
            return col
        w.tint(F + 56, w.bot, wet)
    band(w, F, part, "paint")


def m_SL(w):
    """The bunker's wall: old sleepers, grey, split and checked, between rusty posts."""
    wood = (118, 108, 94)

    def f(x, z):
        if x < 6 or x > 57:
            u = x if x < 6 else 63 - x
            col = shade(mix(IRON, RUST, 0.6 * vnoise(x, z, 8, 551, 64)), (0.6, 1.2, 1.0, 1.0, 0.9, 0.7)[u])
            return jit(col, x, z // 2, 552, 0.05)
        if z % 12 == 0:
            return shade(wood, 0.42)
        kz = (z - 1) // 12
        k = h32(0, kz, 25)
        g = 0.86 + 0.24 * k + 0.07 * math.sin(x * 0.45 + k * 9 + (z % 12) * 0.9)
        if z % 12 == 11:
            g *= 1.15
        # splits along the grain, part of the length
        sz = 3 + int(h32(1, kz, 553) * 6)
        if z % 12 == sz and abs(x - 12 - h32(2, kz, 553) * 30) < 10 + 12 * h32(3, kz, 553):
            return shade(wood, 0.4)
        col = jit(shade(wood, g), x, z, 26, 0.06)
        if h32(4, kz, 554) < 0.3:
            col = mix(col, (70, 60, 50), 0.5 * vnoise(x, z, 8, 555, 64))   # old tar
        return col
    w.fill(w.z0, w.bot, f)
    w.fill(w.z0, w.z0 - 3, lambda x, z: shade((96, 86, 74), 1.25 if z == w.z0 else 1.0))
    runs(w, [w.z0 - 3], RUST, 0.12, 0.4, 556, 60)


def m_CF(w):
    """Coal, dusty: a grey bloom over it, few glints."""
    fn = lumps((58, 54, 50), (128, 122, 112), 27, 5, glint=(170, 166, 156))
    w.fill(w.z0, w.bot, lambda x, z: mix(fn(x, z), (104, 98, 90), 0.3 * vnoise(x, z, 8, 561, 64)))


def m_EF(w):
    w.fill(w.z0, w.bot, lumps((130, 106, 80), (172, 154, 124), 28, 6))
    stains(w, w.z0, w.bot, DUST, 0.35, 562, cell=16)


def m_GF(w):
    fn = lumps((140, 134, 122), (178, 172, 160), 29, 3)
    w.fill(w.z0, w.bot, lambda x, z: mix(fn(x, z), (70, 62, 54), 0.55) if vnoise(x, z, 8, 563, 64) > 0.78
           else fn(x, z))


def m_SF(w, F=None, part=0):
    """Stained stone: dark runs down from the joints, lime under them, the joints eroded."""
    w.fill(w.z0, w.bot, ashlar(STONE, 16, 32, seed=31, joint=0.55))
    stains(w, w.z0, w.bot, (104, 88, 66), 0.5, 571, cell=32)
    srcs = list(range(w.z0 - (w.z0 % 16), w.bot, -32))[:12] or [w.z0]
    runs(w, srcs, (96, 82, 64), 0.18, 0.4, 572, 28)
    if part:
        band(w, F, part)


def m_PF(w):
    """The pond's banks: rubble set in dried mud, the mud cracked."""
    mud = (128, 110, 84)

    def f(x, z):
        kz = (z - 1) // 12
        o = int(h32(kz, 0, 32) * 20)
        ln = 14 + int(h32(kz, 1, 32) * 8)
        u = (x + o) % 64
        blk = u // ln
        if z % 12 in (0, 1) or (x + o) % ln in (0, 1) or h32(blk, kz, 581) < 0.25:
            n = vnoise(x, z, 8, 582, 64)
            if abs(n - 0.5) < 0.03:
                return shade(mud, 0.55)                     # the cracks in the mud
            return jit(mud, x // 2, z // 2, 583, 0.05)
        k = h32(blk, kz, 34)
        return jit(shade((138, 126, 106), 0.8 + 0.3 * k), x // 2, z // 2, 35, 0.07)
    w.fill(w.z0, w.bot, f)
    stains(w, w.z0, w.bot, DUST, 0.3, 584, cell=16)


def m_CH(w):
    """The chimney: brown brick with iron straps round it every 96, rust under them, soot down from the top
    in streaks; engineering brick at its foot under a stained stone band."""
    P = w.period
    br = brick(shade(BRICK, 0.95), seed=591)

    def f(x, z):
        if z > 64 and z % 96 in (0, 1, 2, 3, 4):
            m = z % 96
            col = shade(mix(IRON, RUST, 0.5 * vnoise(x, z, 8, 592, P)), (0.6, 0.9, 1.0, 1.1, 1.25)[m])
            if x % 32 == 16 and m in (1, 2, 3):
                col = (126, 90, 62)                         # the bolts
            return col
        return br(x, z)
    w.fill(w.z0, w.bot, f)
    straps = [z for z in range(96 * (w.z0 // 96), 64, -96)]
    if straps:
        runs(w, straps, RUST, 0.35, 0.5, 593, 40, width=2, zbot=64)
    w.fill(48, w.bot, brick(ENG, (88, 78, 70), seed=37))
    w.fill(54, 48, lit_band(STONE)(54, 48))
    w.fill(w.z0, w.z0 - 20, lambda x, z: shade(SOOT, 1.3 if z == w.z0 - 19 else 1.0))
    gradient(w, w.z0 - 200, w.z0 - 20, SOOT, 0.55, 594)
    runs(w, [w.z0 - 20], SOOT, 0.4, 0.55, 595, 260, width=4)


def m_BH(w, F, part):
    """The boiler house: whitewashed brick gone grey and flaking to the brown brick, rusty stanchions every
    128, engineering brick at the foot, a rusty tie, soot high up."""
    P = w.period
    br = brick(BRICK, seed=39)
    wash = brick(WASH_GREY, shade(WASH_GREY, 0.86), seed=601, var=0.03)
    walls = peel(wash, br, 0.48, 602, P, cell=16)

    def f(x, z):
        d = min(x, P - x)
        if d < 7:
            if d == 0:
                return shade(IRON, 0.55)
            col = mix(IRON, RUST, 0.3 + 0.5 * vnoise(x, z, 8, 603, P))
            return jit(shade(col, 1.15 if d in (1, 5) else 0.9 if d == 6 else 1.0), x, z, 40, 0.04)
        return walls(x, z)
    w.fill(w.z0, w.bot, f)
    w.fill(F + 24, w.bot, brick(ENG, (88, 78, 70), seed=41))
    w.fill(F + 260, F + 250, lambda x, z: shade(mix(IRON, RUST, 0.5), 1.25 if z == F + 260 else 0.95))
    runs(w, [F + 250], RUST, 0.3, 0.5, 604, 60)
    gradient(w, F + 140, w.z0, SOOT, 0.6, 42)
    gradient(w, F + 32, F, GRIME, 0.3, 605)
    band(w, F, part)


def m_BS(w):
    """A boiler's sides: rusted plate, brown runs under every rivet line; the lagging band split and torn."""
    w.fill(w.z0, w.bot, plate((72, 62, 54), 64, 64, seed=43, rust=0.55, P=w.period))
    lag = (150, 140, 118)

    def f(x, z, c):
        if x % 64 in (0, 1, 2, 31, 32, 33):
            return shade(mix(IRON, RUST, 0.5), 1.1)
        n = vnoise(x, z, 8, 611, w.period)
        if n < 0.3:
            return c                                        # torn away: the plate shows
        col = jit(shade(lag, 0.8 + 0.3 * math.sin((z - 168) / 40 * math.pi)), x, z, 44, 0.05)
        if n < 0.33:
            return shade(col, 0.6)
        if x % 16 == 7 and h32(x // 16, 0, 612) < 0.6:
            return shade(col, 0.6)                          # splits
        return mix(col, GRIME, 0.3 * vnoise(x, z, 16, 613, w.period))
    w.tint(208, 168, f)
    w.fill(w.z0, w.z0 - 4, lambda x, z: shade(mix((72, 62, 54), RUST, 0.4), 1.4))


def m_SE(w):
    def f(x, z):
        if z == w.z0:
            return (140, 124, 104)
        if z == w.z0 - 1:
            return (98, 82, 66)
        return jit(mix((84, 76, 68), RUST, 0.4), x, z, 45, 0.08)
    w.fill(w.z0, w.bot, f)


def m_AT(w, F, part):
    """The ash tunnel: brick black with soot (the one near-black place), ash heaped grey at its foot."""
    gb = brick((56, 50, 46), (70, 64, 58), seed=46, var=0.12)
    w.fill(w.z0, w.bot, lambda x, z: mix(gb(x, z), SOOT, 0.3 * vnoise(x, z, 16, 621, w.period)))
    w.tint(F + 24, w.bot, lambda x, z, c: mix(c, (112, 108, 100), 0.6 if z < F + 10 + 10 * vnoise(x, 0, 16, 622, w.period) else 0.15))
    band(w, F, part)


def m_PC(w, F):
    """A pump's casing: grey paint flaking to rust, the flange course rusty, the brass cap line tarnished."""
    top = w.z0
    P = w.period
    paint = (126, 120, 110)

    def base(x, z):
        g = 0.92 + 0.12 * math.sin(math.pi * (x % 64) / 64)
        return jit(shade(paint, g), x // 2, z // 2, 48, 0.03)

    def rust(x, z):
        return jit(mix(RUST, RUST_D, vnoise(x, z, 4, 631, P)), x, z, 632, 0.05)
    body = peel(base, rust, 0.36, 633, P, cell=8)

    def f(x, z):
        if z > top - 3:
            return shade(BRASS, 1.2 if z == top else 0.85)
        if F + 56 < z <= F + 64:
            if x % 8 == 4 and z in (F + 60, F + 61):
                return RUST_L
            return shade(mix(STEEL, RUST, 0.6), 0.75 if z in (F + 57, F + 64) else 0.9)
        if z <= F + 6:
            return shade(mix(STEEL, RUST, 0.5), 0.7)
        return body(x, z)
    w.fill(w.z0, w.bot, f)
    runs(w, [F + 56], RUST_D, 0.4, 0.5, 634, 30)


def m_LP(w):
    """A lagged pipe run: the lagging dirty and split, hanging loose at the rusty bands."""
    top, bot = w.z0, w.bot
    P = w.period

    def f(x, z):
        t = (z - bot) / max(1, top - bot)
        g = 0.62 + 0.5 * math.sin(t * math.pi)
        u = x % 64
        if u < 5:
            return shade(mix(IRON, RUST, 0.6), 0.8 + 0.6 * g)
        col = jit(shade((168, 156, 130), g), x, z, 49, 0.04)
        col = mix(col, GRIME, 0.35 * vnoise(x, z, 16, 641, P))
        if 5 <= u < 16 and z < bot + 10 + 4 * (u - 5) / 11:   # the lagging sags off the band
            return shade(col, 0.55) if z > bot + 6 else (30, 28, 26)
        if u in (36, 37) and h32(x // 64, z // 12, 642) < 0.6:
            return shade(col, 0.5)                          # a split along it
        return col
    w.fill(w.z0, w.bot, f)


CLER = (280, 352)                       # the turbine hall's clerestory (absolute), the crane rail under it


def m_TH(w, F, part):
    """The turbine hall: ivory faience crazed and dirty, tiles fallen in patches to the brown brick, rust run
    down from the crane rail, the black band chipped, the clerestory dark and broken in places."""
    P = w.period
    tl = crazed(FAIENCE, 16, seed=50, P=P, grout=0.76)
    br = brick(BRICK, seed=651)

    def f(x, z):
        tx, tz = x // 16, (z - 1) // 16
        n = vnoise(tx * 16, tz * 16, 32, 652, P) * 0.75 + h32(tx, tz, 653) * 0.25
        if n < 0.24:
            return br(x, z)
        if n < 0.255:
            return jit(BED, x, z, 654, 0.06)
        return tl(x, z)
    w.fill(w.z0, w.bot, f)

    def chipband(x, z):
        if h32(x // 3, z // 3, 655) < 0.18:
            return jit(BED, x, z, 656, 0.06)
        return lit_band(DARK)(F + 120, F + 112)(x, z)
    w.fill(F + 120, F + 112, chipband)
    skirting(w, F, 10)
    lo, hi = CLER

    def glaze(x, z):
        u, v = x % 32, (z - lo) % 24
        if u < 2 or v < 2:
            return shade(mix(IRON, RUST, 0.4), 0.8)
        k = h32(x // 32, (z - lo) // 24, 657)
        if k < 0.18:
            return jit((24, 22, 20), x, z, 658, 0.1)        # a broken pane: the dark of the roof space
        g = 0.9 + 0.1 * (v / 24)
        return jit(shade((92, 86, 76) if k > 0.5 else (106, 98, 86), g), x // 2, z // 2, 51, 0.05)
    w.fill(hi, lo, glaze)
    w.fill(hi + 4, hi, lambda x, z: shade(mix(IRON, RUST, 0.5), 1.1))
    w.fill(lo, lo - 4, lambda x, z: shade(mix(IRON, RUST, 0.5), 1.1))
    w.fill(lo - 8, lo - 24, lambda x, z: shade(mix(IRON, RUST, 0.55), 1.3) if z == lo - 8 else
           (RUST_L if x % 16 == 8 and z in (lo - 12, lo - 20) else shade(mix(IRON, RUST, 0.55), 0.85)))
    w.fill(w.z0, w.z0 - 12, moulding((164, 154, 132), w.z0, w.z0 - 12))
    runs(w, [lo - 24], (104, 68, 44), 0.3, 0.6, 659, 240, width=2)
    runs(w, [lo - 24], (84, 70, 56), 0.2, 0.3, 660, 120, width=6)
    stains(w, lo - 24, F + 120, GRIME, 0.35, 661, cell=32)
    gradient(w, F + 40, F, GRIME, 0.35, 662)
    band(w, F, part)


def m_GG(w):
    """The gantry's crane girder: a riveted plate girder, rust running from its rivets and its top flange."""
    top, bot = w.z0, w.bot
    g = mix((70, 66, 62), RUST, 0.45)

    def f(x, z):
        if z > top - 10 or z <= bot + 10:
            return shade(g, 1.3 if z in (top, bot + 10) else 0.95)
        if x % 64 < 8:
            return shade(g, 1.15 if x % 64 in (1, 2) else 0.8 if x % 64 == 7 else 1.0)
        if (z in (top - 14, bot + 14)) and x % 8 == 4:
            return RUST_L
        return jit(g, x // 3, z // 3, 52, 0.05)
    w.fill(w.z0, w.bot, f)
    runs(w, [top - 10, top - 14], RUST_D, 0.4, 0.55, 671, 60)


def m_TE(w):
    """A casing's end: warm grey paint flaking to bare rusty steel."""
    P = w.period
    paint = (132, 124, 110)

    def top(x, z):
        if z % 48 in (0, 1):
            return shade(paint, 0.7 if z % 48 == 0 else 1.15)
        return jit(paint, x // 2, z // 2, 53, 0.03)
    w.fill(w.z0, w.bot, peel(top, lambda x, z: jit(mix(STEEL, RUST, 0.6), x, z, 681, 0.06), 0.36, 682, P, cell=8))


def m_SW(w):
    """The spider's pit: black oily concrete, two corroded pipes along it."""
    w.fill(w.z0, w.bot, lambda x, z: jit((40, 37, 34), x // 3, z // 2, 54, 0.14))
    for zc, c in ((w.bot + 26, (92, 78, 64)), (w.bot + 14, (104, 74, 50))):
        w.fill(zc + 3, zc - 3, lambda x, z, zc=zc, c=c: shade(mix(c, RUST_D, 0.4 * vnoise(x, z, 8, 691, w.period)),
                                                              0.7 + 0.5 * math.cos((z - zc) / 3.5)))


def m_CW(w):
    """A condenser pit: the tube plate corroded, a pale crust in blooms over it."""
    P = w.period

    def f(x, z):
        u, v = x % 6, z % 6
        if (u - 3) ** 2 + (v - 3) ** 2 <= 4:
            return (36, 30, 26) if (u - 3) ** 2 + (v - 3) ** 2 <= 1 else (112, 86, 58)
        col = jit((100, 82, 60), x, z, 55, 0.06)
        n = vnoise(x, z, 8, 701, P)
        if n > 0.62:
            col = mix(col, (166, 156, 132), min(1, (n - 0.62) * 4))
        return col
    w.fill(w.z0, w.bot, f)


def m_WS(w, F, part):
    """The workshop: an oily dark brick dado, grimy cream painted brick above it flaking to the brick."""
    P = w.period
    under = brick(BRICK, seed=711)
    w.fill(w.z0, w.bot, peel(brick((168, 156, 128), (150, 140, 116), seed=56, var=0.03), under, 0.33, 712, P))
    oily = brick((82, 60, 44), (64, 50, 40), seed=57, var=0.08)
    w.fill(F + 104, F, lambda x, z: mix(oily(x, z), (110, 96, 80), 0.25 * vnoise(x, z, 8, 713, P) ** 2))
    w.fill(F + 108, F + 104, lit_band((76, 56, 40))(F + 108, F + 104))
    w.fill(w.z0, w.z0 - 8, lambda x, z: shade(mix(IRON, RUST, 0.4), 1.0))
    stains(w, w.z0 - 8, F + 108, GRIME, 0.45, 714, cell=32)
    runs(w, [w.z0 - 8], (96, 80, 62), 0.2, 0.35, 715, 80, width=3)
    skirting(w, F, 6)
    band(w, F, part)


def m_BN(w):
    """A bench's front: the timber top's edge scarred, the iron front rusty, the drawer pulls dull."""
    top = w.z0
    P = w.period

    def f(x, z):
        u = x % 32
        if z > top - 5:
            col = jit(shade((90, 66, 46), 1.15 if z == top else 0.92), x, z, 58, 0.06)
            return shade(col, 0.6) if h32(x // 2, 0, 721) < 0.12 else col
        if u < 2 or z <= w.bot + 3:
            return shade(mix(IRON, RUST, 0.5), 0.9)
        if 12 < u < 20 and top - 15 >= z > top - 18:
            return shade(BRASS, 0.95)
        if z > top - 24:
            return shade(mix((80, 62, 46), RUST, 0.3), 1.2 if z == top - 5 else 0.95 if u > 2 else 0.7)
        return jit(shade(mix(IRON, RUST, 0.25 + 0.55 * vnoise(x, z, 8, 722, P)), 0.85), x // 2, z // 2, 59, 0.05)
    w.fill(w.z0, w.bot, f)


def m_LA(w):
    """A lathe's side, rusted under dust: the stand, the bed and its ways, the headstock, a handwheel."""
    P = w.period
    bot, top = w.bot, w.z0
    body = (76, 64, 54)
    w.fill(top, bot, lambda x, z: jit(mix(body, RUST, 0.5 * vnoise(x, z, 8, 731, P)), x // 2, z // 2, 60, 0.06))
    w.fill(top, top - 10, lambda x, z: shade(mix((150, 138, 120), RUST, 0.4 * vnoise(x, 0, 8, 732, P)),
                                             1.1 if z == top else 0.85))
    w.fill(top - 10, top - 16, lambda x, z: shade((50, 44, 40), 1.0))
    w.rect(0, top, 30, top - 46, mix(body, RUST, 0.3))
    w.frame(0, top, 30, top - 46, (46, 40, 36))
    w.disc(15, top - 22, 9, (124, 98, 74))
    w.disc(15, top - 22, 3, (44, 38, 34))
    cx, cz = 86, bot + 30
    w.ring(cx, cz, 9, 11, (112, 84, 62))
    for a in range(0, 360, 60):
        t = math.radians(a)
        w.line(cx, cz, cx + 9 * math.cos(t), cz + 9 * math.sin(t), (100, 76, 56))
    w.disc(cx, cz, 2, BRASS)
    w.rect(4, bot + 30, P - 4, bot, mix((56, 50, 46), RUST, 0.3))
    w.frame(6, bot + 28, 60, bot + 2, (36, 32, 30))
    w.frame(68, bot + 28, P - 6, bot + 2, (36, 32, 30))
    w.rect(28, bot + 18, 36, bot + 15, BRASS)
    # dust settled on every upward face, rust running under the ways
    runs(w, [top - 16], RUST_D, 0.3, 0.5, 733, 30)
    w.tint(top, top - 2, lambda x, z, c: mix(c, DUST, 0.5))
    w.tint(bot + 31, bot + 29, lambda x, z, c: mix(c, DUST, 0.45))
    w.tint(top - 46, top - 47, lambda x, z, c: mix(c, DUST, 0.4))


def m_AR(w, F, part):
    w.fill(w.z0, w.bot, plate((106, 96, 84), 32, 64, seed=61, rust=0.65, P=w.period))
    skirting(w, F, 6)
    band(w, F, part)


def sag_cables(w, F, zcs, xs, sag=5, col=(28, 26, 24)):
    """Cables sagging between brackets at the columns xs (the period's): black, round."""
    P = w.period
    pts = sorted(xs)

    def f(x, z, c):
        for i, a in enumerate(pts):
            b = pts[(i + 1) % len(pts)] + (P if i == len(pts) - 1 else 0)
            xx = x if x >= a else x + P
            if a <= xx < b:
                t = (xx - a) / (b - a)
                dz = sag * math.sin(math.pi * t)
                for k, zc in enumerate(zcs):
                    zz = zc - dz * (1 + 0.3 * k)
                    d = z - zz
                    if -2 < d <= 2:
                        return shade(col, (0.7, 1.0, 1.6, 1.2)[int(d + 2) % 4] if d > -2 else 0.7)
                break
        return c
    w.tint(max(zcs) + 3, min(zcs) - sag * 2 - 4, f)


def m_TU(w, F, part):
    """The cable tunnel: damp dull brick with pale lime runs, rusty brackets, the cables sagging between."""
    P = w.period
    w.fill(w.z0, w.bot, brick(shade(BRICK, 0.85), seed=62))
    runs(w, [w.z0], LIME, 0.22, 0.45, 741, 70, width=2)
    stains(w, F + 30, w.bot, (64, 52, 42), 0.5, 742, cell=16)
    for x0 in (14, 46):                                     # the brackets: a post, two arms
        w.rect(x0, F + 70, x0 + 3, F + 28, shade(mix(IRON, RUST, 0.6), 0.9))
        for zc in (F + 40, F + 64):
            w.rect(x0 - 2, zc, x0 + 7, zc - 3, shade(mix(IRON, RUST, 0.6), 1.15))
    runs(w, [F + 70, F + 40, F + 64], RUST_D, 0.5, 0.45, 743, 24, width=2)
    sag_cables(w, F, [F + 44, F + 68], [15, 47], sag=6)
    skirting(w, F, 6)
    band(w, F, part)


def m_TR(w, F=0, part=0):
    """A cable tray's edge: a rusty channel, dusty cable ends in it."""
    P = w.period

    def f(x, z):
        if z == w.z0 or z == w.bot + 1:
            return shade(mix(STEEL, RUST, 0.5), 1.25)
        if (x % 6 - 3) ** 2 + (z % 6 - 3) ** 2 <= 4 and w.bot + 2 < z < w.z0 - 1:
            return (36, 32, 30) if (x % 6 - 3) ** 2 + (z % 6 - 3) ** 2 > 1 else (120, 92, 62)
        return jit(shade(mix(STEEL, RUST, 0.3 + 0.5 * vnoise(x, z, 8, 751, P)), 0.8), x, z, 63, 0.04)
    w.fill(w.z0, w.bot, f)
    band(w, F, part)


def m_TF(w):
    """A transformer's cooling fins, rusty, rust running from the top header."""
    top, bot = w.z0, w.bot
    P = w.period
    g = (84, 74, 64)

    def f(x, z):
        c = mix(g, RUST, 0.25 + 0.4 * vnoise(x, z, 16, 761, P))
        if top - 12 < z <= top - 4 or bot + 4 < z <= bot + 12:
            return shade(c, 0.8 + 0.5 * math.sin((z % 8) / 8 * math.pi))
        if z > top - 4 or z <= bot + 4:
            return shade(c, 0.6)
        u = x % 8
        return shade(c, (0.45, 0.7, 1.0, 1.25, 1.3, 1.1, 0.85, 0.6)[u])
    w.fill(w.z0, w.bot, f)
    runs(w, [top - 12], RUST_D, 0.3, 0.5, 762, 50)


def m_PL(w):
    w.fill(w.z0, w.bot, lambda x, z: jit((150, 142, 128), x // 2, z, 64, 0.06) if z != w.z0 else (170, 162, 146))
    stains(w, w.z0, w.bot, (92, 70, 50), 0.6, 771, cell=8, cut=0.5)


def m_GL(w):
    """The switchyard's gantry: a rusty lattice girder's face."""
    top, bot = w.z0, w.bot
    P = w.period
    g = mix((86, 82, 76), RUST, 0.5)

    def f(x, z):
        if z > top - 12 or z <= bot + 12:
            return shade(g, 1.3 if z in (top, bot + 12) else 1.0)
        u = x % 64
        h = z - bot - 12
        span = top - bot - 24
        d1 = abs(u - h * 64 / span)
        d2 = abs(u - (64 - h * 64 / span))
        if min(d1, d2) < 4 or u < 4:
            return shade(mix(g, RUST_D, 0.4 * vnoise(x, z, 8, 781, P)), 1.15 if min(d1, d2) < 1.5 else 0.95)
        return jit((32, 30, 28), x, z, 65, 0.05)
    w.fill(w.z0, w.bot, f)


def m_RR(w, F, part):
    """The relay room: plaster with its wash flaking, a dull scratched walnut dado, a picture rail."""
    P = w.period
    w.fill(w.z0, w.bot, peel(plaster(WASH, 66), plaster(PLASTER, 791, 0.05), 0.38, 792, P))

    def dado(x, z):
        u = x % 64
        if u < 3 or u > 60 or z > F + 92 or z <= F + 8:
            col = jit(shade(WALNUT, 0.85), x, z, 67, 0.05)
        elif u in (8, 55) or z in (F + 86, F + 14):
            col = shade(WALNUT, 0.7 if u == 55 or z == F + 14 else 1.25)
        else:
            col = jit(shade(WALNUT, 1.05 + 0.04 * math.sin(z * 0.7)), x, z, 68, 0.04)
        if (x * 2 + z * 3) % 29 == 0 and h32(x // 8, z // 8, 793) < 0.5:
            col = mix(col, (140, 118, 92), 0.5)             # scratches
        return mix(col, DUST, 0.18)
    w.fill(F + 96, F, dado)
    w.fill(F + 100, F + 96, lit_band(mix(WALNUT, DUST, 0.3))(F + 100, F + 96))
    w.fill(F + 160, F + 156, lit_band(mix(WALNUT, DUST, 0.3))(F + 160, F + 156))
    stains(w, w.z0, F + 100, (128, 104, 72), 0.5, 794, cell=32, cut=0.52)
    skirting(w, F, 6)
    band(w, F, part)


def m_RC(w):
    """A relay cabinet: dusty slate panels; rows of relays, several gone (a dark hole, two wire ends), the
    glass covers cracked, the label strips peeling."""
    slate = (60, 58, 56)
    w.fill(w.z0, w.bot, lambda x, z: jit(slate, x // 2, z // 2, 69, 0.05) if x % 64 not in (0, 63) else (30, 28, 26))
    for i, zr in enumerate((w.z0 - 10, w.z0 - 34, w.z0 - 58)):
        for j, c in enumerate(range(4, w.w, 12)):
            k = h32((c // 12) % 6, i, 801)
            if k < 0.3:                                     # gone: the hole, two wire ends
                w.rect(c + 1, zr - 1, c + 7, zr - 11, (22, 20, 18))
                w.rect(c + 2, zr - 9, c + 3, zr - 4, (128, 92, 62))
                w.rect(c + 5, zr - 9, c + 6, zr - 6, (128, 92, 62))
                continue
            w.rect(c, zr, c + 8, zr - 12, shade(BRASS, 0.8))
            w.rect(c + 1, zr - 1, c + 7, zr - 2, (176, 170, 156))
            w.rect(c + 2, zr - 4, c + 6, zr - 10, shade(BRASS, 0.55))
            if k > 0.7:                                     # its cover cracked
                w.line(c + 1, zr - 3, c + 6, zr - 9, (196, 192, 180))
        # the label strip, its end curling away
        w.rect(2, zr - 15, w.w - 2, zr - 19, (180, 168, 140))
        for c in range(2, w.w - 2):
            if (c % 64) > 50 and (c % 64) < 62:
                w.rect(c, zr - 15, c + 1, zr - 19 + ((c % 64) - 50) // 3, (40, 38, 36))
    w.fill(w.bot + 6, w.bot, lambda x, z: (30, 28, 26))
    w.tint(w.z0, w.bot, lambda x, z, c: mix(c, (120, 114, 104), 0.12 + 0.12 * vnoise(x, z, 16, 802, w.period)))


def m_OC(w, F, part):
    """The outfall: a stained brick culvert, dark and damp low down, lime runs."""
    w.fill(w.z0, w.bot, brick(shade(BRICK, 0.85), seed=70))
    w.tint(F + 64, w.bot, lambda x, z, c: mix(c, (52, 44, 36), 0.4))
    runs(w, [F + 64], (60, 52, 42), 0.25, 0.4, 71, 60)
    runs(w, [w.z0], LIME, 0.15, 0.4, 811, 60)
    band(w, F, part)


def m_TW(w, F, part):
    """The cooling tower's shell: concrete streaked black and brown from the top, patches where the surface has
    spalled (the rusty steel in it), a rusty ring beam high up."""
    P = w.period
    conc = (156, 148, 132)

    def f(x, z):
        u = x % 64
        if u < 6:
            return shade(conc, (1.2, 1.1, 1.02, 0.95, 0.85, 0.7)[u])
        n = vnoise(x, z, 16, 821, P) * 0.7 + vnoise(x, z, 4, 822, P) * 0.3
        if n > 0.7:                                         # spalled: rough, paler, the rebar showing
            if (z % 24) in (0, 1) and n > 0.73:
                return RUST_D
            return jit((176, 166, 146), x, z, 823, 0.08)
        if n > 0.685:
            return shade(conc, 0.7)
        return jit(conc, x // 3, z // 4, 72, 0.05)
    w.fill(w.z0, w.bot, f)
    runs(w, [400], (50, 46, 42), 0.2, 0.55, 73, 400, width=3)
    runs(w, [400], (110, 80, 56), 0.15, 0.45, 824, 200, width=2)
    w.fill(416, 400, lambda x, z: shade(mix(conc, RUST, 0.55), 1.2 if z == 416 else 0.7 if z == 401 else 1.0))
    runs(w, [400], RUST_D, 0.25, 0.5, 825, 50, width=2)
    band(w, F, part)


def m_TP(w):
    conc = (150, 142, 128)
    w.fill(w.z0, w.bot, lambda x, z: shade(conc, 1.15) if x % 64 < 2 else jit(conc, x // 3, z // 4, 74, 0.05))
    runs(w, [w.z0], (72, 64, 56), 0.15, 0.45, 75, 200, width=3)
    stains(w, w.z0, w.bot, (104, 90, 72), 0.4, 831, cell=32)


def m_TL(w):
    conc = (148, 140, 126)
    w.fill(w.z0, w.bot, lambda x, z: shade(conc, (1.2, 1.0, 0.85, 0.7)[x % 16 // 4]))
    w.fill(w.z0, w.z0 - 6, lambda x, z: shade(conc, 1.25 if z == w.z0 else 1.02))
    runs(w, [w.z0 - 6], (70, 62, 54), 0.25, 0.5, 841, 60, width=2)


def m_DK(w, F, part):
    """The duct: damp brick with lime runs, a rusty rack, the cables sagging."""
    w.fill(w.z0, w.bot, brick(shade(BRICK, 0.9), seed=76))
    runs(w, [w.z0], LIME, 0.2, 0.45, 851, 80, width=2)
    w.rect(30, F + 126, 33, F + 96, mix(IRON, RUST, 0.6))
    sag_cables(w, F, [F + 104, F + 112, F + 120], [31], sag=4)
    stains(w, F + 30, w.bot, (64, 52, 42), 0.45, 852, cell=16)
    skirting(w, F, 6)
    band(w, F, part)


def m_LH(w, F, part):
    """The switchgear hall: the walnut dado dull and scratched; above it the grey-veined marble panels streaked
    with dust and cracked, a piece broken away from each to the brown brick, the bronze strips dull; a cornice
    stained; its stands the same with their part's band."""
    P = w.period
    br = brick(BRICK, seed=861)

    def marble(x, z):
        u = x % P
        if u < 3:
            return shade(BRONZE, (0.7, 1.2, 1.0)[u])
        if z % 192 in (0, 1, 2) and z > 0:
            return shade(BRONZE, (0.7, 1.0, 1.2)[z % 192])
        # a piece broken away: the lower left corner of each upper panel, a ragged edge
        pu, pv = u - 3, (z - 1) % 192
        if z > 192 and pu + pv * 0.8 + 6 * vnoise(x, z, 4, 862, P) < 34:
            return br(x, z) if pu + pv * 0.8 < 28 else jit(BED, x, z, 863, 0.06)
        v = math.sin(x * 0.11 + z * 0.045 + 3 * math.sin(z * 0.02 + x * 0.03)) + 0.6 * math.sin(x * 0.05 - z * 0.08)
        g = 0.93 + 0.06 * h32(x // 8, z // 8, 77)
        col = shade((178, 174, 164), g)
        v += 0.25 * math.sin(x * 0.37 + z * 0.23) * h32(x // 16, z // 16, 76)
        if abs(v) < 0.035:
            col = mix(col, (104, 100, 94), 0.5)
        elif abs(v) < 0.12:
            col = mix(col, (140, 136, 128), 0.18)
        return col
    w.fill(w.z0, w.bot, marble)
    cracks(w, w.z0, 4, (70, 64, 58), 864, cell=48, thin=0.01, keep=0.5)
    runs(w, [z for z in range(192 * (w.z0 // 192), 0, -192)] or [w.z0], (132, 120, 100), 0.35, 0.3, 865, 150,
         width=4, zbot=4)

    def dado(x, z):
        u = x % 64
        if u < 4 or u > 59 or z > -10 or z <= -84:
            col = jit(shade(WALNUT, 0.9), x, z, 78, 0.05)
        elif u in (8, 55) or z in (-16, -78):
            col = shade(WALNUT, 0.65 if u == 55 or z == -78 else 1.25)
        else:
            col = jit(shade(WALNUT, 1.06 + 0.05 * math.sin(z * 0.5 + u * 0.1)), x, z, 79, 0.04)
        if (x * 3 + z * 2) % 31 == 0 and h32(x // 8, z // 8, 866) < 0.5:
            col = mix(col, (136, 114, 88), 0.5)
        return mix(col, DUST, 0.15)
    w.fill(0, w.bot, dado)
    w.fill(4, 0, lit_band(BRONZE)(4, 0))
    w.fill(-88, w.bot, lambda x, z: jit(DARK, x, z, 80, 0.08))
    w.fill(w.z0, w.z0 - 16, moulding((168, 160, 140), w.z0, w.z0 - 16))
    stains(w, w.z0 - 16, w.z0 - 80, (132, 110, 78), 0.4, 867, cell=32, cut=0.5)
    band(w, F, part)


def m_SN(w):
    """A cabinet's end: black enamel chipped at its edges to grey steel."""
    def f(x, z):
        if z > w.z0 - 3:
            return (82, 76, 70)
        if x % 64 in (0, 63):
            return (26, 24, 24)
        e = min(x % 64, 63 - x % 64, w.z0 - z, z - w.bot)
        if e < 6 and h32(x // 2, z // 2, 871) < 0.35 * (1 - e / 6):
            return jit((112, 106, 98), x, z, 872, 0.05)
        return jit((34, 32, 32), x // 2, z // 2, 81, 0.05)
    w.fill(w.z0, w.bot, f)
    w.tint(w.z0, w.bot, lambda x, z, c: mix(c, (120, 112, 100), 0.1 * vnoise(x, z, 8, 873, w.period)))


def m_SH(w):
    w.fill(w.z0, w.bot, brick((118, 82, 62), (136, 124, 106), seed=82))
    stains(w, w.z0, w.bot, GRIME, 0.35, 881, cell=32)


WALLS = dict(TD=m_TD, CO=m_CO, GP=m_GP, CT=m_CT, SK=m_SK, RI=m_RI, YD=m_YD, SL=m_SL, CF=m_CF, EF=m_EF, GF=m_GF,
             SF=m_SF, PF=m_PF, CH=m_CH, BH=m_BH, BS=m_BS, SE=m_SE, AT=m_AT, PC=m_PC, LP=m_LP, TH=m_TH, GG=m_GG,
             TE=m_TE, SW=m_SW, CW=m_CW, WS=m_WS, BN=m_BN, LA=m_LA, AR=m_AR, TU=m_TU, TR=m_TR, TF=m_TF, PL=m_PL,
             GL=m_GL, RR=m_RR, RC=m_RC, OC=m_OC, TW=m_TW, TP=m_TP, TL=m_TL, DK=m_DK, LH=m_LH, SN=m_SN, SH=m_SH)


# === pictures =================================================================================================
def chips(w, c1, top, c2, bot, seed, edge=4, amt=0.35, rust=True):
    """Enamel chipped near its edges: dark spots, a rust ring round each."""
    for z in range(bot, top):
        for c in range(c1, c2):
            e = min(c - c1, c2 - 1 - c, top - 1 - z, z - bot)
            if e >= edge:
                continue
            k = h32(c // 2, z // 2, seed)
            if k < amt * (1 - e / edge):
                w.at(c, z, (44, 38, 34))
            elif rust and k < amt * (1 - e / edge) + 0.12:
                w.at(c, z, RUST, 0.7)


def enamel(w, cx, zbot, lines, ground=(204, 196, 170), ink=INK, rim=RUST_D, pad=3, bar=None, scale=1, seed=901):
    """A plate with lines of capitals, its enamel chipped and rust at its rim; `bar` a faded colour bar at its
    left. Returns its top."""
    tw = max(text_width(s, scale) for s in lines)
    lh = 7 * scale
    hgt = len(lines) * lh - 2 * scale + 2 * pad
    bw = 6 if bar else 0
    c1 = cx - (tw + bw) // 2 - pad - 1
    c2 = c1 + tw + bw + 2 * pad + 2
    top = zbot + hgt
    w.rect(c1, top, c2, zbot, ground)
    for z in range(zbot + 1, top + 1):
        for c in range(max(0, c1), min(w.w, c2)):
            w.at(c, z, mix(ground, (150, 132, 100), 0.35 * vnoise(c, z, 4, seed, 0)))
    w.frame(c1, top, c2, zbot, rim)
    if bar:
        w.rect(c1 + 2, top - 2, c1 + 2 + bw - 1, zbot + 2, shade(mix(bar, (150, 140, 120), 0.25), 0.92))
    for k, s in enumerate(lines):
        w.centre(s, cx + bw // 2, top - pad - k * lh, ink, scale)
    chips(w, max(0, c1), top + 1, min(w.w, c2), zbot + 1, seed + 1, edge=2, amt=0.4)
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
    white = (214, 206, 186)
    w.rect(c1, at + 34, c2, at, white)
    w.frame(c1, at + 34, c2, at, RED, 2)
    w.rect(c1, at + 34, c2, at + 22, RED)
    w.centre("DANGER", cx, at + 31, (226, 218, 200))
    w.centre("33000", cx, at + 18, RED)
    w.centre("VOLTS", cx, at + 10, (40, 36, 32))
    chips(w, c1, at + 35, c2, at + 1, 911, edge=3, amt=0.45)


def p_window(w, spec):
    """A tall steel window high in a yard's wall, the frame rusty; the panes dirty, broken or boarded; none lit."""
    c1, c2, lo, hi = 12, 52, 220, 404
    w.rect(c1 - 4, lo, c2 + 4, lo - 6, mix(STONE, GRIME, 0.3))
    w.rect(c1 - 4, lo - 5, c2 + 4, lo - 6, shade(STONE, 0.5))
    w.rect(c1 - 2, hi + 8, c2 + 2, hi, mix(STONE, GRIME, 0.35))
    seed = 921 + spec.get("shift", 0) % 7
    board = (122, 108, 88)
    for z in range(lo, hi):
        for c in range(c1, c2):
            u, v = (c - c1) % 10, (z - lo) % 14
            pu, pv = (c - c1) // 10, (z - lo) // 14
            k = h32(pu, pv, seed)
            if u == 0 or v == 0 or c == c2 - 1:
                col = shade(mix(IRON, RUST, 0.5), 0.9)
            elif pv < 5 and h32(pu, 0, seed + 1) < 0.5 or k < 0.12:
                # boarded: grey planks across, nails
                pl = (z - lo) % 7
                col = jit(shade(board, 0.85 + 0.25 * h32((z - lo) // 7, pu, seed + 2)), c, z, seed + 3, 0.06)
                if pl == 0:
                    col = shade(board, 0.5)
                if u in (2, 7) and pl == 3:
                    col = (60, 50, 42)
            elif k < 0.38:
                # broken: the dark inside, shards left at the edges
                shard = (u + v * 0.7) < 4 + 3 * h32(pu, pv, seed + 4) or (10 - u) + (14 - v) * 0.5 < 3
                col = (78, 74, 68) if shard else jit((22, 20, 18), c, z, seed + 5, 0.1)
            else:
                col = jit((70, 66, 60), c // 3, z // 3, 85, 0.08)
                col = mix(col, (112, 100, 82), 0.4 * vnoise(c, z, 8, seed + 6, 0))
                if u == 1 or v == 13:
                    col = shade(col, 1.25)
            w.at(c, z, col)
    runs(w, [lo - 6], RUST_D, 0.4, 0.45, seed + 7, 40, width=2, zbot=max(w.bot, lo - 60))


def p_bhwindow(w, spec):
    c1, c2, lo, hi = 10, 54, 216, 352
    w.rect(c1 - 3, lo, c2 + 3, lo - 5, shade(STONE, 0.6))
    for z in range(lo, hi):
        for c in range(c1, c2):
            u, v = (c - c1) % 11, (z - lo) % 12
            k = h32((c - c1) // 11, (z - lo) // 12, 931)
            if u == 0 or v == 0 or c == c2 - 1:
                col = shade(mix(IRON, RUST, 0.4), 0.7)
            elif k < 0.22:
                col = jit((20, 18, 16), c, z, 932, 0.1)          # broken
            else:
                g = 0.65 + 0.35 * (z - lo) / (hi - lo)
                col = mix(jit((132, 124, 108), c, z, 86, 0.05), SOOT, 0.6 - 0.3 * g)
            w.at(c, z, col)


def p_pilaster(w, spec):
    """A giant pilaster: crazed dirty faience, tiles gone here and there, a chipped black plinth, a stained
    capital, rust down from the rail."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    c1, c2 = (0, W) if W <= 32 else (8, W - 8)
    lo, hi = CLER
    tl = crazed(shade(FAIENCE, 1.02), 16, seed=87, P=64)
    for z in range(F, lo - 24):
        for c in range(c1, c2):
            u = c - c1
            tx, tz = u // 16, (z - 1) // 16
            if h32(tx, tz, 941) < 0.06:
                col = jit(BED, c, z, 942, 0.06)
            else:
                col = tl(u, z)
            if u == 0 or u == 1:
                col = shade(col, 1.15)
            if u >= c2 - c1 - 2:
                col = shade(col, 0.72)
            if z > F + 28:
                col = mix(col, GRIME, 0.25 * vnoise(u, z, 16, 943, 0))
            w.at(c, z, col)
    for z in range(F, F + 28):
        for c in range(c1, c2):
            w.at(c, z, jit(DARK, c, z, 944, 0.08) if h32(c // 3, z // 3, 945) > 0.12 else jit(BED, c, z, 946, 0.06))
    w.rect(c1, F + 28, c2, F + 27, shade(DARK, 1.6))
    for z in range(lo - 40, lo - 24):
        for c in range(c1 - 2 if c1 else 0, c2 + 2 if c2 < W else W):
            w.at(c, z, moulding((160, 150, 126), lo - 24, lo - 40)(c, z))
    for c in range(c1, c2):
        if h32(c // 2, 0, 947) < 0.3:
            L = 40 + 120 * h32(c // 2, 1, 947)
            for z in range(lo - 40, int(lo - 40 - L), -1):
                p = w.get(c, z)
                if p:
                    w.at(c, z, mix(p, (104, 70, 46), 0.5 * (1 - (lo - 40 - z) / L)))


def p_cplate(w, spec):
    """The chimney's plate, 1933, tarnished bronze; on this face the lightning conductor's strip, its clips."""
    for z in range(w.bot, w.z0):
        for c in range(54, 57):
            w.at(c, z, shade((86, 66, 48), (1.2, 1.0, 0.7)[c - 54]))
        if z % 48 == 0:
            w.rect(52, z + 2, 59, z - 1, mix(IRON, RUST, 0.5))
    w.rect(14, 92, 50, 70, shade(BRONZE, 0.7))
    w.rect(16, 90, 48, 72, BRONZE)
    w.rect(16, 90, 48, 89, shade(BRONZE, 1.25))
    for z in range(72, 89):
        for c in range(16, 48):
            if vnoise(c, z, 4, 951, 0) > 0.62:
                w.at(c, z, (88, 82, 64), 0.5)               # the tarnish in blooms
    for k, ch in enumerate("1933"):
        im = Img(6, 10, (0, 0, 0, 0))
        digit(im, ch, 0, 0, (178, 150, 98), 2)
        w.paste(im, 18 + k * 8, 86)
    for z in range(70, 40, -1):
        for c in range(16, 48):
            if h32(c // 2, 0, 952) < 0.3:
                p = w.get(c, z)
                if p:
                    w.at(c, z, mix(p, (70, 60, 46), 0.4 * (z - 40) / 30))


def p_boiler(w, spec):
    """A boiler's front, cold: rusted plate with runs under the rivets; two fire doors, one hanging open on
    the black (no glow); the gauge glasses cracked and empty; the dial's glass cracked, its needle at zero; a
    rusty valve wheel; the tarnished number plate; NOT TO BE FIRED chalked on it. `gap`: kept clear."""
    W = spec["w"]
    w.fill(w.z0, w.bot, plate((70, 60, 52), 48, 56, seed=88, rust=0.55, P=0))
    gap = spec.get("gap")
    for k, cx in enumerate((40, W - 40)):                       # the fire doors
        w.rect(cx - 26, 84, cx + 26, 14, (30, 26, 24))
        if k == 0:
            w.rect(cx - 22, 78, cx + 22, 20, (12, 11, 10))      # open: the dead firebox
            for z in range(22, 40):
                for c in range(cx - 20, cx + 20):
                    if z < 24 + 10 * vnoise(c, 0, 8, 961, 0):
                        w.at(c, z, jit((62, 58, 54), c, z, 962, 0.15))   # cold ash in it
            # the door, swung out on its hinges and dropped, seen nearly edge-on
            for z in range(14, 80):
                for c in range(cx - 34, cx - 22):
                    t = (c - (cx - 34)) / 12
                    if 16 + 4 * (1 - t) <= z <= 76 + 2 * (1 - t) - 6 * (1 - t):
                        w.at(c, z, shade(mix((76, 64, 54), RUST, 0.5), 0.7 + 0.5 * t))
        else:
            w.rect(cx - 22, 78, cx + 22, 20, mix((64, 56, 50), RUST, 0.4))
            w.frame(cx - 22, 78, cx + 22, 20, (96, 80, 64))
            for z in range(70, 36, -6):
                w.rect(cx - 14, z, cx + 14, z - 2, (34, 30, 28))
            w.rect(cx + 14, 54, cx + 20, 48, shade(BRASS, 0.8))
    layout = dict(gl=(72, W - 72), dial=(W // 2, 210), wheel=(W // 2 + 44, 250), num=(W // 2, 112))
    if gap:
        layout = dict(gl=(gap[1] + 10, W - 14), dial=(gap[1] + 40, 214), wheel=(30, 250), num=(gap[1] + 40, 112))
    for i, gx in enumerate(layout["gl"]):                      # the gauge glasses, empty, cracked
        w.rect(gx - 4, 190, gx + 4, 184, shade(BRASS, 0.8))
        w.rect(gx - 4, 138, gx + 4, 132, shade(BRASS, 0.8))
        w.rect(gx - 2, 184, gx + 2, 138, (112, 104, 92))
        w.rect(gx - 1, 184, gx, 138, (150, 144, 130))
        zc = 170 - 14 * i
        w.line(gx - 2, zc + 3, gx + 1, zc - 2, (36, 32, 28))
    dx, dz = layout["dial"]                                     # the pressure dial
    w.disc(dx, dz, 19, shade(BRASS, 0.85))
    w.disc(dx, dz, 16, (196, 188, 166))
    for k in range(9):
        t = math.radians(225 - k * 270 / 8)
        w.line(dx + 12 * math.cos(t), dz + 12 * math.sin(t), dx + 15 * math.cos(t), dz + 15 * math.sin(t), INK)
    t = math.radians(225)                                       # its needle at zero
    w.line(dx, dz, dx + 13 * math.cos(t), dz + 13 * math.sin(t), INK)
    w.disc(dx, dz, 2, INK)
    w.line(dx - 13, dz + 8, dx + 2, dz - 2, (238, 234, 222))    # the glass cracked across
    w.line(dx + 2, dz - 2, dx + 12, dz - 9, (238, 234, 222))
    w.line(dx + 2, dz - 2, dx + 6, dz + 12, (238, 234, 222))
    vx, vz = layout["wheel"]                                    # the valve wheel, rusty
    w.ring(vx, vz, 10, 13, (100, 66, 44))
    for a in range(0, 360, 72):
        t = math.radians(a)
        w.line(vx, vz, vx + 11 * math.cos(t), vz + 11 * math.sin(t), (96, 64, 44))
    w.disc(vx, vz, 3, shade(BRASS, 0.7))
    w.rect(vx - 2, vz - 13, vx + 2, vz - 40, (80, 56, 40))
    nx, nz = layout["num"]                                      # the number plate, tarnished
    w.rect(nx - 16, nz, nx + 16, nz - 18, BRASS)
    for z in range(nz - 17, nz):
        for c in range(nx - 15, nx + 15):
            if vnoise(c, z, 4, 963, 0) > 0.6:
                w.at(c, z, (100, 92, 66), 0.5)
    w.frame(nx - 16, nz, nx + 16, nz - 18, shade(BRASS, 0.55))
    w.text("NO", nx - 13, nz - 4, (44, 30, 18))
    im = Img(6, 10, (0, 0, 0, 0))
    digit(im, str(spec["n"]), 0, 0, (44, 30, 18), 2)
    w.paste(im, nx + 4, nz - 4)
    # NOT TO BE FIRED, chalked under the gauge glasses
    a, b = ((gap[1] + 4) if gap else 4), W - 4
    words = ["NOT TO BE FIRED"] if b - a >= text_width("NOT TO BE FIRED") + 4 else ["NOT TO BE", "FIRED"]
    mx = (a + b) // 2
    zt = 126 + 4 * (len(words) - 1)
    for k, s in enumerate(words):
        im = Img(text_width(s) + 1, 5, (0, 0, 0, 0))
        gtext(im, s, 0, 0, CHALK, 1)
        for y in range(im.h):
            for x in range(im.w):
                if im.px[y * im.w + x][3] and h32(x, y + 7 * k, 964 + spec["n"]) > 0.12:
                    w.at(mx - im.w // 2 + x, zt - 7 * k - y, CHALK, 0.85)


def p_casing(w, spec):
    """A turbine's casing: warm grey paint flaking to bare rusty steel, the flange bolts rusty, the maker's
    brass plate tarnished: No n, 30 MW 3000 RPM."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    grey = (138, 130, 116)

    def paint(x, z):
        return jit(shade(grey, 0.97 + 0.06 * math.sin((z - bot) / 96 * math.pi)), x // 2, z // 2, 89, 0.03)

    def bare(x, z):
        return jit(mix(STEEL, RUST, 0.45 + 0.4 * vnoise(x, z, 4, 971, 0)), x, z, 972, 0.05)
    body = peel(paint, bare, 0.34, 973, 0, cell=8)

    def f(x, z):
        if z in (bot + 48, bot + 47) or x % 160 in (0, 1):
            return shade(mix(grey, RUST, 0.3), 0.6 if z == bot + 47 or x % 160 == 1 else 1.15)
        if (z in (bot + 44, bot + 51) and x % 10 == 5) or (x % 160 in (5, 155) and z % 10 == 5):
            return RUST_L
        if z > top - 4:
            return mix(shade(grey, 1.2 if z == top else 1.05), DUST, 0.4)
        if z <= bot + 6:
            return shade(mix(grey, RUST, 0.4), 0.7)
        return body(x, z)
    w.fill(top, bot, f)
    runs(w, [bot + 44], RUST_D, 0.3, 0.5, 974, 30, width=1)
    cx = W // 2
    w.rect(cx - 46, bot + 82, cx + 46, bot + 56, shade(BRASS, 0.65))
    w.rect(cx - 44, bot + 80, cx + 44, bot + 58, BRASS)
    for z in range(bot + 59, bot + 80):
        for c in range(cx - 43, cx + 44):
            if vnoise(c, z, 4, 975, 0) > 0.64:
                w.at(c, z, (104, 96, 70), 0.45)
    w.rect(cx - 44, bot + 80, cx + 44, bot + 79, shade(BRASS, 1.2))
    ink = (48, 32, 18)
    w.centre(f"NO {spec['n']}", cx, bot + 77, ink)
    w.centre("30 MW 3000 RPM", cx, bot + 68, ink)


def p_tend(w, spec):
    """A transformer's end: its tank rusty, the rating plate T<n> yellowed, a faded DANGER plate on some."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    g = (88, 78, 68)
    w.fill(top, bot, lambda x, z: shade(g, 1.2 if z == top else 0.7 if z == top - 6 else 0.95) if z > top - 7 else
           jit(mix(g, RUST, 0.2 + 0.5 * vnoise(x, z, 16, 981, 0)), x // 2, z // 2, 90, 0.04))
    runs(w, [top - 7], RUST_D, 0.3, 0.5, 982, 60, width=2)
    for c in range(6, W, 12):
        w.disc(c, top - 3, 1.2, RUST_L)
    cx = W // 2
    w.rect(cx - 22, bot + 84, cx + 22, bot + 62, (178, 168, 142))
    w.frame(cx - 22, bot + 84, cx + 22, bot + 62, shade(BRASS, 0.7), 2)
    w.centre("T" + str(spec["n"]), cx, bot + 81, INK)
    w.centre("33 KV", cx, bot + 72, INK)
    if spec.get("danger"):
        p_danger(w, dict(w=W, at=bot + 18))
    w.rect(cx + 30, bot + 22, cx + 40, bot + 12, (64, 56, 50))
    w.disc(cx + 35, bot + 17, 4, shade(BRASS, 0.7))


def p_cabinet(w, spec):
    """A switchgear cabinet's long side: two cubicle doors in black enamel chipped to grey steel at the edges,
    each with a small meter (its glass cracked), a handle and a number."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    w.fill(top, bot, lambda x, z: (82, 76, 70) if z > top - 3 else jit((34, 32, 32), x // 2, z // 2, 91, 0.04))
    for k in range(2):
        c1 = 3 + k * (W // 2)
        c2 = c1 + W // 2 - 6
        w.frame(c1, top - 4, c2, bot + 4, (72, 68, 64))
        chips(w, c1, top - 4, c2, bot + 4, 991 + k, edge=4, amt=0.4, rust=False)
        mx = (c1 + c2) // 2
        w.disc(mx, top - 18, 9, shade(BRASS, 0.8))
        w.disc(mx, top - 18, 7, (192, 184, 164))
        w.line(mx, top - 18, mx - 4, top - 14, INK)
        w.line(mx - 6, top - 13, mx + 5, top - 22, (236, 232, 220))
        w.rect(c2 - 8, bot + 34, c2 - 5, bot + 20, (130, 118, 100))
        num = str(2 * spec["n"] - 1 + k)
        w.rect(mx - 9, bot + 16, mx + 9, bot + 8, (186, 178, 156))
        im = Img(len(num) * 4, 5, (0, 0, 0, 0))
        for i, ch in enumerate(num):
            digit(im, ch, i * 4, 0, INK, 1)
        w.paste(im, mx - len(num) * 2, bot + 14)
    w.tint(top, bot, lambda x, z, c: mix(c, (124, 116, 104), 0.1 * vnoise(x, z, 8, 993, 0)))


def p_store(w, spec):
    lo = 160
    enamel(w, spec["w"] // 2, lo + 10, ("INSTRUMENT STORE",), bar=G.PART_COLOURS[2])


def board(w, c1, top, c2, bot, frame=BRONZE, ground=PAPER, t=4):
    w.rect(c1, top, c2, bot, frame)
    w.rect(c1 + 1, top - 1, c2 - 1, top - 2, shade(frame, 1.3))
    w.rect(c1 + t, top - t, c2 - t, bot + t, ground)


def foxing(w, c1, top, c2, bot, seed, amt=1.0):
    """Old paper: yellowed unevenly, brown foxing spots, darker toward its edges."""
    for z in range(bot + 1, top + 1):
        for c in range(max(0, c1), min(w.w, c2)):
            p = w.get(c, z)
            if p is None:
                continue
            e = min(c - c1, c2 - 1 - c, top - z, z - bot - 1)
            t = 0.22 * vnoise(c, z, 16, seed, 0) + (0.22 * (1 - e / 8) if e < 8 else 0)
            col = mix(p, (150, 118, 72), t * amt)
            k = h32(c // 2, z // 2, seed + 1)
            if k < 0.012:
                col = mix(col, (128, 92, 56), 0.5)
            w.at(c, z, col)


def p_plan(w, spec):
    """GENERATING STATION: the plan on yellowed, foxed paper in a dull bronze frame, one corner torn away (one
    with no way in it); the rooms as outlines, the three ways in yellow, green and red, numbered."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 176, F + 44
    board(w, 0, top, W, bot, frame=(92, 72, 50))
    ink = (78, 60, 42)
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
    foxing(w, 4, top - 4, W - 4, bot + 4, 1001)
    wayp = []
    for k in (1, 2, 3):
        pts = pl["ways"][k]
        col = shade(G.PART_COLOURS[k], 0.85)
        for a, b in zip(pts, pts[1:]):
            w.line(X(a[0]), Z(a[1]) + 1, X(b[0]), Z(b[1]) + 1, col, 2)
            for i in range(11):
                wayp.append((X(a[0] + (b[0] - a[0]) * i / 10), Z(a[1] + (b[1] - a[1]) * i / 10)))
        ex_, ez_ = X(pts[-1][0]), Z(pts[-1][1])
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k), 0, 0, shade(col, 0.8), 1)
        w.paste(im, int(X(9060)), int(ez_) + 3)
        w.line(ex_, ez_ + 1, X(9040), ez_ + 1, col, 1)
        wayp.append((X(9060), ez_ + 3))
    ex, ey = pl["exit"]
    w.rect(X(ex) - 2, Z(ey) + 3, X(ex) + 2, Z(ey) - 2, ink)
    # the torn corner: the first corner with no way (nor its number) near it
    tw_, th_ = 30, 22
    corners = [(4, top - 4, 1, -1), (W - 4, top - 4, -1, -1), (4, bot + 4, 1, 1), (W - 4, bot + 4, -1, 1)]
    for cc, cz, sx, sz in corners:
        if all(not (min(cc, cc + sx * (tw_ + 4)) <= px <= max(cc, cc + sx * (tw_ + 4)) and
                    min(cz, cz + sz * (th_ + 4)) <= pz <= max(cz, cz + sz * (th_ + 4))) for px, pz in wayp):
            break
    else:
        cc = None
    if cc is not None:
        for i in range(tw_ + 3):
            for j in range(th_ + 3):
                d = i / tw_ + j / th_
                jag = 0.08 * (vnoise(i * 3 + j * 2, 0, 4, 1002, 0) - 0.5)
                c, z = cc + sx * i, cz + sz * j
                if d < 1 + jag:
                    w.at(c, z, jit((84, 66, 48), c, z, 1003, 0.06))         # the board under the paper
                elif d < 1.06 + jag:
                    w.at(c, z, (222, 212, 184))                             # the torn edge, its fibres pale


def p_rules(w, spec):
    """SAFETY RULES on an enamel board, its enamel chipped and rust blooming at its four screws."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 156, F + 56
    board(w, 4, top, W - 4, bot, frame=(48, 42, 36), ground=(212, 204, 184), t=3)
    for z in range(bot + 4, top - 2):
        for c in range(7, W - 7):
            w.at(c, z, mix((212, 204, 184), (160, 140, 104), 0.25 * vnoise(c, z, 16, 1011, 0)))
    w.rect(8, top - 3, W - 8, top - 4, (110, 100, 86))
    w.centre("SAFETY RULES", W // 2, top - 8, INK)
    w.rect(W // 2 - 38, top - 15, W // 2 + 38, top - 16, INK)
    lines = ["1. NO ONE IS TO WORK ALONE.", "2. KNOW WHERE YOUR MATES ARE", "   AT ALL TIMES.",
             "3. NEVER CLOSE A SWITCH", "   ANOTHER HAS OPENED."]
    for k, s in enumerate(lines):
        w.text(s, 12, top - 22 - k * 9, INK)
    w.text("BY ORDER", W - 12 - text_width("BY ORDER"), bot + 12, shade(INK, 1.6))
    chips(w, 7, top - 2, W - 7, bot + 4, 1012, edge=4, amt=0.45)
    for c, z in ((9, top - 6), (W - 10, top - 6), (9, bot + 7), (W - 10, bot + 7)):
        w.disc(c, z, 4, RUST, 0.8)
        w.disc(c, z, 1.5, (40, 34, 30))
        for k in range(14):
            p = w.get(c, z - 4 - k)
            if p:
                w.at(c, z - 4 - k, mix(p, RUST_D, 0.6 * (1 - k / 14)))


def p_shadow(w, spec):
    """The tool shadow board, warped and stained: the tools' black outlines, most of them empty now (two tools
    left, five gone)."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 160, F + 60
    ground = (178, 162, 128)
    board(w, 0, top, W, bot, frame=(84, 58, 38), ground=ground, t=3)
    for z in range(bot + 3, top - 2):
        for c in range(3, W - 3):
            warp = 0.08 * math.sin(c / W * math.pi * 3 + 0.5) * math.sin((z - bot) / (top - bot) * math.pi)
            col = shade(ground, 1 + warp)
            col = mix(col, (118, 96, 66), 0.35 * vnoise(c, z, 16, 1021, 0) ** 1.5)
            n = vnoise(c, z, 24, 1022, 0)
            if abs(n - 0.62) < 0.012:
                col = mix(col, (96, 74, 50), 0.6)                    # the tide marks of a leak
            w.at(c, z, col)
    w.line(3, top - 40, W - 3, top - 46, (92, 72, 50))              # a split in the board
    sil = (36, 32, 28)
    steel = (128, 112, 94)
    handle = (100, 66, 40)

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
    spanner(40, top - 16, top - 66, True)
    hammer(64, True)
    saw(84, False)
    calipers(132, True)
    hammer(164, True)
    w.rect(8, bot + 12, W - 8, bot + 10, (120, 104, 82))


def p_single(w, spec):
    """The single-line diagram, faded: G1 and G2, the three busbars in yellow, green and red, the feeders TOWN,
    WORKS, INSTITUTE each with a load meter: the institute's still hard against its stop."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 172, F + 44
    board(w, 0, top, W, bot, frame=(52, 44, 36), ground=PAPER)
    ink = (54, 44, 34)
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
    foxing(w, 4, top - 4, W - 4, bot + 4, 1031, 0.8)
    bars = []
    for k in range(3):
        zb = top - 34 - k * 22
        col = shade(G.PART_COLOURS[k + 1], 0.82)
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
        w.disc(fx, mz, 6.5, (210, 198, 166))
        frac = 0.18 if k < 2 else 1.0
        t = math.radians(150 - 120 * frac)
        w.line(fx, mz - 2, fx + 7 * math.cos(t), mz - 2 + 7 * math.sin(t), (150, 36, 30) if k == 2 else ink)
        if k == 2:
            w.rect(fx + 6, mz + 1, fx + 8, mz - 3, ink)
        w.centre(nm, fx, bot + 15, ink)


def p_synchro(w, spec):
    """The synchroscope on its black marble panel, dusty: the dial's glass cracked across, the brass dull, the
    pointer still straight up, SLOW and FAST; three small meters 1, 2, 3, each with its lamp: the lamps the only
    clean colour in the room."""
    W = spec["w"]
    top, bot = 236, 40
    w.rect(0, top, W, bot, shade(BRONZE, 0.9))
    for z in range(bot + 3, top - 3):
        for c in range(3, W - 3):
            v = math.sin(c * 0.09 + z * 0.05 + 2 * math.sin(z * 0.03))
            col = jit((40, 38, 36), c // 3, z // 3, 92, 0.06)
            if abs(v) < 0.06:
                col = (84, 80, 74)
            col = mix(col, (118, 110, 98), 0.22 * vnoise(c, z, 16, 1041, 0))
            w.at(c, z, col)
    cx, cz = 72, 150
    w.disc(cx, cz, 46, shade(BRASS, 0.6))
    w.disc(cx, cz, 43, shade(BRASS, 0.85))
    w.disc(cx, cz, 38, (200, 190, 164))
    for k in range(24):
        t = math.radians(90 - k * 15)
        r1 = 30 if k % 6 else 26
        w.line(cx + r1 * math.cos(t), cz + r1 * math.sin(t), cx + 35 * math.cos(t), cz + 35 * math.sin(t), INK)
    w.line(cx, cz - 6, cx, cz + 32, INK, 2)
    w.disc(cx, cz, 4, INK)
    w.text("SLOW", cx - 33, cz - 8, INK)
    w.text("FAST", cx + 33 - text_width("FAST"), cz - 8, INK)
    glass = (240, 236, 226)                                     # the crack across the glass
    pts = [(cx - 37, cz + 12), (cx - 20, cz + 6), (cx - 8, cz + 9), (cx + 6, cz - 2), (cx + 20, cz - 6),
           (cx + 36, cz - 16)]
    for a, b in zip(pts, pts[1:]):
        w.line(a[0], a[1], b[0], b[1], glass)
    w.line(cx - 8, cz + 9, cx - 14, cz + 26, glass)
    w.line(cx + 6, cz - 2, cx + 14, cz - 24, glass)
    w.centre("SYNCHROSCOPE", cx, cz - 54, (168, 146, 96))
    for k in range(3):
        mx, mz = 158, 196 - k * 54
        w.disc(mx, mz, 15, shade(BRASS, 0.8))
        w.disc(mx, mz, 12, (198, 188, 164))
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
def fn2(x, y, cell, seed, S=64):
    return vnoise(x, y, cell, seed, S, S)


def f_lino_worn():
    """Rooms and corridors: worn brown lino, paler where people walked, dust in its joints."""
    lino = (116, 84, 58)

    def f(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return (82, 62, 46)
        col = jit(lino, x // 2, y // 2, 1101, 0.04)
        n = fn2(x, y, 32, 1102)
        col = mix(col, (150, 124, 94), 0.5 * max(0, n - 0.4))
        if h32(x, y, 1103) < 0.02:
            col = shade(col, 0.82)
        return col
    return flat(f)


def f_plaster_stained():
    def f(x, y):
        if x in (0, 63) or y in (0, 63):
            return (140, 128, 104)
        col = jit((176, 166, 140), x // 2, y // 2, 1111, 0.03)
        n = fn2(x, y, 32, 1112)
        if abs(n - 0.6) < 0.012:
            return mix(col, (110, 84, 56), 0.6)             # the tide ring of an old leak
        if n > 0.6:
            col = mix(col, (150, 124, 88), 0.5)
        return col
    return flat(f)


def f_wood(c, plank=8, along_x=True, seed=102, joint=0.55, scars=0.0, grey=0.0):
    def f(x, y):
        u, v = (x, y) if along_x else (y, x)
        if v % plank == 0:
            return shade(c, joint)
        k = h32(0, v // plank, seed)
        if (u + int(k * 64)) % 64 == 0:
            return shade(c, joint)
        g = 0.88 + 0.22 * k + 0.05 * math.sin(u * 0.3 + k * 7)
        col = jit(shade(c, g), u, v, seed + 1, 0.04)
        if grey:
            col = mix(col, (140, 132, 118), grey * (0.6 + 0.4 * fn2(x, y, 16, seed + 2)))
        if scars and (u * 2 + v * 5) % 37 == 0 and h32(u // 8, v // 8, seed + 3) < scars:
            col = mix(col, (168, 146, 112), 0.5)
        return col
    return flat(f)


def f_lumps(base, hi, seed, size, glint=None, S=64):
    fn = lumps(base, hi, seed, size, glint)
    return flat(lambda x, y: fn(x, y))


def f_cinder():
    """The coal yard's cinder, with dry tufts of dead weed, buff and sparse."""
    fn = lumps((70, 64, 58), (124, 116, 106), 145, 3)

    def f(x, y):
        col = fn(x, y)
        for cx, cy in ((14, 20), (46, 50), (52, 12)):
            dx, dy = (x - cx + 32) % 64 - 32, (y - cy + 32) % 64 - 32
            r = math.hypot(dx, dy)
            if r < 5 and ((math.atan2(dy, dx) * 4.5 + r * 0.3) % 1.0) < 0.42:
                return shade((170, 148, 104), 0.8 + 0.4 * (1 - r / 5))
        return col
    return flat(f)


def f_setts():
    """Setts with gaps and dust between them."""
    def f(x, y):
        k = y // 8
        off = (k * 5) % 16
        if y % 8 == 0 or (x + off) % 16 == 0:
            return jit((128, 116, 96), x, y, 1121, 0.08)
        col = jit(shade((124, 118, 108), 0.85 + 0.3 * h32((x + off) // 16, k, 103)), x, y, 104, 0.05)
        if h32((x + off) // 16, k, 1122) < 0.06:
            return jit((112, 98, 78), x, y, 1123, 0.08)     # a sett gone: dust in its hole
        return mix(col, DUST, 0.2 * fn2(x, y, 32, 1124))
    return flat(f)


def f_slabs(c=(160, 150, 130), s=32, seed=105):
    """Cracked slabs, stained."""
    def f(x, y):
        if x % s == 0 or y % s == 0:
            return shade(c, 0.6)
        col = jit(shade(c, 0.9 + 0.2 * h32(x // s, y // s, seed)), x // 2, y // 2, seed + 1, 0.05)
        n = fn2(x, y, 16, seed + 2)
        if abs(n - 0.5) < 0.014 and fn2(x, y, 32, seed + 3) > 0.5:
            return shade(col, 0.62)
        return mix(col, (104, 90, 70), 0.3 * fn2(x, y, 32, seed + 4))
    return flat(f)


def f_drains():
    """Stained concrete with dark drain channels."""
    def f(x, y):
        if 28 <= x < 36:
            if x in (28, 35):
                return (84, 78, 70)
            return (34, 32, 30) if y % 4 else (82, 66, 50)
        if y % 64 == 0 or x % 64 == 0:
            return (110, 104, 94)
        col = jit((150, 144, 130), x // 2, y // 2, 106, 0.06)
        return mix(col, (90, 78, 62), 0.45 * fn2(x, y, 16, 1131) ** 2)
    return flat(f)


def f_brick_paving():
    """Brick paving under dust, stained."""
    def f(x, y):
        k = y // 8
        off = 8 if k % 2 else 0
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (112, 100, 86)
        col = jit(shade((116, 76, 58), 0.9 + 0.2 * h32((x + off) // 16, k, 107)), x, y, 108, 0.05)
        return mix(col, (138, 124, 102), 0.45 * fn2(x, y, 32, 1141))
    return flat(f)


def f_chequer():
    """Rusty chequer plate."""
    def f(x, y):
        u, v = x % 8, y % 8
        base = mix((84, 76, 68), RUST, 0.3 + 0.5 * fn2(x, y, 16, 1151))
        if (u, v) in ((1, 1), (2, 2), (3, 3), (5, 5), (6, 6)) or (x // 8 + y // 8) % 2 and (u, 7 - v) in ((1, 1), (2, 2), (3, 3), (5, 5)):
            return shade(base, 1.4)
        return jit(base, x // 2, y // 2, 109, 0.05)
    return flat(f)


def f_grating():
    def f(x, y):
        if x % 8 in (0, 1) or y % 4 == 0:
            base = mix((96, 88, 80), RUST, 0.4 + 0.4 * fn2(x, y, 16, 1161))
            return shade(base, 1.0 if x % 8 == 0 or y % 4 == 0 else 1.2)
        return (22, 20, 18)
    return flat(f)


def f_boiler_top():
    def f(x, y):
        d = math.hypot(x - 64, y - 64)
        base = mix((70, 60, 52), RUST, 0.25 + 0.5 * fn2(x, y, 32, 1171, 128))
        if 18 < d < 22:
            return shade(base, 1.2) if d < 20 else (28, 24, 22)
        if abs(d - 25) < 1 and int(math.degrees(math.atan2(y - 64, x - 64))) % 30 < 8:
            return RUST_L
        if x % 64 == 0 or y % 64 == 0:
            return (32, 28, 26)
        if (x % 64 in (4, 60) and y % 8 == 4) or (y % 64 in (4, 60) and x % 8 == 4):
            return RUST_L
        return mix(jit(base, x // 2, y // 2, 110, 0.05), DUST, 0.25 * fn2(x, y, 16, 1172, 128))
    return flat(f, 128)


def f_ash():
    return flat(lambda x, y: jit((116, 112, 104), x // 2, y // 2, 111, 0.08) if h32(x, y, 112) > 0.08 else (72, 68, 62))


def f_vault():
    """The ash tunnel's vault: brick black with soot."""
    def f(x, y):
        k = y // 8
        off = 16 if k % 2 else 0
        if y % 8 == 0 or (x + off) % 32 == 0:
            return (66, 60, 54)
        return jit(shade((56, 48, 44), 0.85 + 0.25 * h32((x + off) // 32, k, 113)), x, y, 114, 0.05)
    return flat(f)


def f_quarry():
    """The pump room's floor: dull brown quarry tiles under dust."""
    def f(x, y):
        if x % 16 == 0 or y % 16 == 0:
            return (100, 88, 74)
        col = jit(shade((122, 84, 62), 0.9 + 0.2 * h32(x // 16, y // 16, 115)), x, y, 116, 0.04)
        return mix(col, (140, 126, 104), 0.4 * fn2(x, y, 32, 1181))
    return flat(f)


def f_pump_top():
    def f(x, y):
        d = math.hypot(x - 64 + 0.5, y - 64 + 0.5)
        paint = (126, 120, 110)
        n = fn2(x, y, 8, 1191, 128) * 0.7 + fn2(x, y, 32, 1192, 128) * 0.3
        base = jit(paint, x // 2, y // 2, 118, 0.03) if n > 0.4 else jit(RUST, x, y, 1193, 0.06)
        if d < 26:
            if d > 23:
                return (86, 76, 66)
            return mix(base, DUST, 0.3)
        if abs(d - 30) < 2 and int(math.degrees(math.atan2(y - 64, x - 64)) + 360) % 30 < 10:
            return RUST_L
        return base
    return flat(f, 128)


def f_lagged_top():
    def f(x, y):
        if x % 64 < 5:
            return shade(mix(IRON, RUST, 0.6), 1.1)
        col = jit((166, 154, 128), x, y // 2, 119, 0.04)
        if y % 64 in (30, 31) and h32(x // 8, 0, 1201) < 0.6:
            return shade(col, 0.5)
        return mix(col, GRIME, 0.35 * fn2(x, y, 16, 1202))
    return flat(f)


def f_big_terrazzo():
    """R's floor: terrazzo in large squares, dusty, cracked and stained, its black lines worn (quiet)."""
    base = (164, 156, 140)

    def f(x, y):
        if x % 128 < 2 or y % 128 < 2:
            if fn2(x, y, 8, 1211, 128) > 0.42:
                return jit((92, 86, 78), x, y, 1212, 0.05)
        k = h32(x, y, 120)
        if k < 0.05:
            col = jit((110, 100, 88), x, y, 121, 0.12)
        elif k < 0.1:
            col = jit((186, 180, 166), x, y, 122, 0.04)
        else:
            col = jit(base, x // 2, y // 2, 124, 0.03)
        n = fn2(x, y, 32, 1213, 128)
        col = mix(col, (132, 118, 98), 0.35 * max(0, n - 0.45) * 2)
        c = fn2(x, y, 16, 1214, 128)
        if abs(c - 0.5) < 0.01 and fn2(x, y, 64, 1215, 128) > 0.55:
            col = shade(col, 0.72)
        return col
    return flat(f, 128)


def f_roof():
    """Rusty trusses and dark dirty glazing, panes broken here and there."""
    def f(x, y):
        if 56 <= x <= 71:
            if x in (56, 71) or (x - 56 + y) % 16 in (0, 1) or (71 - x + y) % 16 in (0, 1):
                return shade(mix(IRON, RUST, 0.4), 0.8)
            return (64, 60, 54)
        if x % 16 in (0, 1) or y % 32 in (0, 1):
            return shade(mix(IRON, RUST, 0.3), 0.85)
        k = h32(x // 16, y // 32, 1221)
        if k < 0.12:
            return jit((20, 18, 16), x, y, 1222, 0.1)
        g = 0.9 + 0.12 * ((x % 16) + (y % 32)) / 46
        col = jit(shade((110, 102, 90), g), x, y, 121, 0.03)
        return mix(col, (60, 54, 46), 0.4 * fn2(x, y, 16, 1223, 128))
    return flat(f, 128)


def f_casing_top():
    def f(x, y):
        if y % 64 in (31, 32):
            return (88, 80, 70)
        if y % 64 in (28, 35) and x % 8 == 4:
            return RUST_L
        col = jit((132, 126, 116), x // 2, y // 4, 122, 0.04)
        return mix(col, DUST, 0.45 * fn2(x, y, 16, 1231))
    return flat(f)


def f_plate_floor(c=(100, 92, 82), seed=123, rust=0.5):
    w = Wall(64, 64, 64)
    w.fill(64, 0, plate(c, 32, 64, seed=seed, rust=rust, P=64))
    return w.im


def f_wood_block():
    """The workshop's wood blocks, worn black with oil, a few gone."""
    def f(x, y):
        by = y // 8
        off = 8 if by % 2 else 0
        if y % 8 == 0 or (x + off) % 16 == 0:
            return (58, 42, 30)
        k = h32((x + off) // 16, by, 124)
        if h32((x + off) // 16, by, 1241) < 0.05:
            return jit((96, 90, 80), x, y, 1242, 0.08)      # a block gone: the screed
        col = jit(shade((112, 80, 52), 0.85 + 0.25 * k), x, y, 125, 0.05)
        return mix(col, (52, 42, 34), 0.55 * fn2(x, y, 16, 1243))
    return flat(f)


def f_lathe_top():
    def f(x, y):
        v = y % 64
        if 20 <= v < 26 or 38 <= v < 44:
            col = (150, 138, 120) if v in (20, 38) else (120, 104, 86)
            return mix(col, RUST, 0.4 * fn2(x, y, 8, 1251))
        return mix(jit((76, 64, 54), x // 2, y // 2, 126, 0.05), DUST, 0.35)
    return flat(f)


def f_boards_beams():
    """A roof: boards grey and stained on rusty beams."""
    def f(x, y):
        if 26 <= y <= 37:
            return (32, 28, 26) if y in (26, 37) else shade(mix((60, 54, 48), RUST, 0.4), 1.2 if y in (27, 36) else 1)
        if y % 8 == 0:
            return (62, 50, 40)
        col = jit(shade((124, 108, 88), 0.9 + 0.2 * h32(0, y // 8, 127)), x, y, 128, 0.05)
        return mix(col, (86, 66, 46), 0.4 * fn2(x, y, 16, 1261))
    return flat(f)


def f_cables(along_x):
    def f(x, y):
        u, v = (x, y) if along_x else (y, x)
        k = v % 6
        if k == 0:
            return (76, 68, 60)
        g = (0.0, 0.7, 1.4, 1.6, 1.1, 0.6)[k]
        col = jit(shade((34, 32, 30), g), u // 8, v, 129, 0.05)
        return mix(col, DUST, 0.18 * fn2(x, y, 16, 1271))
    return flat(f)


def f_concrete(c=(140, 134, 122), seed=130, stain=0.4):
    def f(x, y):
        if x % 64 == 0 or y % 64 == 0:
            return shade(c, 0.78)
        col = jit(c, x // 2, y // 2, seed, 0.05)
        n = fn2(x, y, 16, seed + 1)
        return mix(col, (88, 76, 62), stain * max(0, n - 0.5) * 2)
    return flat(f)


def f_trans_top():
    def f(x, y):
        for cx in (16, 48):
            d = math.hypot(x - cx + 0.5, y - 32 + 0.5)
            if d < 9:
                return (168, 156, 136) if d < 4 else (104, 86, 70) if d < 7 else (44, 38, 34)
        if x % 64 in (0, 63) or y % 64 in (0, 63):
            return (52, 46, 42)
        return jit(mix((86, 78, 70), RUST, 0.2 + 0.4 * fn2(x, y, 16, 1281)), x // 2, y // 2, 131, 0.04)
    return flat(f)


def f_dry_reed():
    """The pond's banks: dry buff reed stubble on caked earth (not green)."""
    def f(x, y):
        k = h32(x, y, 132)
        base = mix((124, 106, 80), (150, 134, 104), fn2(x, y, 8, 1291))
        if k < 0.18:
            return shade((178, 158, 116), 0.9 + 0.2 * h32(x, y, 1292))
        if k > 0.86:
            return mix(base, (84, 70, 54), 0.6)
        return jit(base, x, y, 134, 0.06)
    return flat(f)


def f_silted():
    """The tower's floor: silted concrete, dry, the silt in drifts."""
    def f(x, y):
        c = jit((128, 120, 106), x // 2, y // 2, 135, 0.06)
        if y % 32 in (15, 16):
            return (74, 68, 60)
        s = 0.5 + 0.5 * math.sin(x * 2 * math.pi / 64 + 2 * math.sin(y * 2 * math.pi / 64))
        return mix(c, (150, 136, 110), 0.5 * s * fn2(x, y, 16, 136))
    return flat(f)


def f_lino_curl():
    """The relay room: brown lino, its tiles curling at the joints."""
    def f(x, y):
        u, v = x % 32, y % 32
        if u == 0 or v == 0:
            return (58, 44, 34)
        k = h32(x // 32, y // 32, 1301)
        col = jit((112, 78, 54), x // 2, y // 2, 137, 0.05)
        if k < 0.5 and (u < 3 or v < 3):
            return shade(col, 1.18)                         # an edge lifting
        return mix(col, DUST, 0.25 * fn2(x, y, 32, 1302))
    return flat(f)


def f_marble_dusty():
    """L's floor: the marble squares gone grey with dust, low contrast, a few cracks (quiet)."""
    def f(x, y):
        dark = (x // 64 + y // 64) % 2
        v = math.sin(x * 0.12 + y * 0.05 + 3 * math.sin(y * 0.03 + x * 0.02))
        if dark:
            col = jit((106, 102, 96), x // 4, y // 4, 138, 0.04)
            if abs(v) < 0.06:
                col = (122, 118, 110)
        else:
            col = jit((156, 150, 138), x // 4, y // 4, 139, 0.03)
            if abs(v) < 0.06:
                col = (138, 132, 122)
        col = mix(col, (146, 136, 116), 0.3 * fn2(x, y, 32, 1311, 128))
        if x % 64 == 0 or y % 64 == 0:
            col = shade(col, 0.85)
        c = fn2(x, y, 32, 1312, 128)
        if abs(c - 0.5) < 0.008 and fn2(x, y, 64, 1313, 128) > 0.6:
            col = shade(col, 0.75)
        return col
    return flat(f, 128)


def f_coffers():
    """L's ceiling: coffered plaster, stained, a patch of lath showing in one coffer."""
    def f(x, y):
        u, v = x % 64, y % 64
        d = min(u, v, 63 - u, 63 - v)
        if d < 6:
            col = jit((174, 164, 140), x, y, 140, 0.03) if d > 1 else (140, 128, 104)
        elif d < 10:
            col = (152, 142, 118) if (u < 32) == (v < 32) else (162, 152, 128)
        else:
            col = jit((180, 170, 146), x // 2, y // 2, 141, 0.02)
            if x < 64 and y >= 64:
                n = fn2(x, y, 8, 1321, 128)
                if math.hypot(u - 34, v - 30) < 12 + 6 * n:             # the plaster fallen: the lath
                    return (52, 40, 30) if y % 4 == 0 else jit((112, 86, 60), x, y, 1322, 0.06)
        n = fn2(x, y, 32, 1323, 128)
        if abs(n - 0.62) < 0.01:
            return mix(col, (110, 84, 56), 0.5)
        if n > 0.62:
            col = mix(col, (150, 124, 88), 0.45)
        return col
    return flat(f, 128)


def f_slate_top():
    return flat(lambda x, y: (76, 70, 64) if x % 64 in (0, 63) or y % 64 in (0, 63) else
                mix(jit((44, 42, 40), x // 2, y // 2, 142, 0.04), DUST, 0.35 * fn2(x, y, 16, 1331)))


def f_cab_top():
    return flat(lambda x, y: (86, 80, 72) if x % 64 < 3 or y % 64 < 3 else
                mix(jit((36, 34, 34), x // 2, y // 2, 143, 0.03), DUST, 0.35 * fn2(x, y, 16, 1341)))


FLATS = dict(
    TZ=f_lino_worn, PK=f_plaster_stained, TK=lambda: f_wood((92, 64, 44), 8, True, 144, 0.7, scars=0.6),
    CN=f_cinder, CL=lambda: f_lumps((52, 48, 46), (130, 124, 116), 146, 6, (168, 164, 156)),
    ER=lambda: f_lumps((130, 108, 80), (164, 146, 118), 147, 5), ST=f_setts, SB=lambda: f_slabs(), CD=f_drains,
    GV=lambda: flat(lambda x, y, fn=lumps((150, 144, 132), (184, 178, 166), 148, 3): mix(fn(x, y), (64, 56, 48), 0.6)
                    if fn2(x, y, 16, 1351) > 0.74 else fn(x, y)),
    BP=f_brick_paving, CQ=f_chequer, GR=f_grating, BT=f_boiler_top, AS=f_ash, BV=f_vault, QT=f_quarry,
    PT=f_pump_top, LG=f_lagged_top, TT=f_big_terrazzo, RG=f_roof, CS=f_casing_top,
    SP=lambda: f_plate_floor(), WB=f_wood_block, BB=lambda: f_wood((116, 86, 58), 8, True, 149, scars=0.8, grey=0.2),
    LT=f_lathe_top, KB=f_boards_beams, DP=lambda: f_plate_floor((72, 64, 58), 150, 0.4), CA=lambda: f_cables(True),
    CB=lambda: f_cables(False), CF=lambda: f_concrete(), KC=lambda: f_concrete((134, 126, 112), 151, 0.6),
    TO=f_trans_top, PN=lambda: f_concrete((150, 142, 128), 152), DG=f_dry_reed, WC=f_silted, LI=f_lino_curl,
    RT=f_slate_top, MC=f_marble_dusty, KF=f_coffers, TS=lambda: f_wood((124, 100, 76), 8, False, 153, 0.6, grey=0.45),
    SC=f_cab_top, KS=lambda: f_slabs((150, 142, 128), 64, 154), TB=lambda: f_wood((96, 86, 74), 12, True, 155, 0.5,
                                                                                     grey=0.3))


# === the sky ==================================================================================================
def sky():
    """A dusk: dark warm-grey cloud above, a pale buff band low down, no blue or violet; the cloud drifts
    slowly (look 1's way of making it)."""
    W, H = 1024, 256
    im = Img(W, H)
    for y in range(H):
        t = y / (H - 1)
        base = mix((70, 64, 60), (110, 98, 86), t)
        glow = max(0.0, (t - 0.62) / 0.38) ** 1.4
        base = mix(base, (206, 182, 140), glow)
        for x in range(W):
            u = x / W * 2 * math.pi
            c = 0.5 + 0.25 * math.sin(3 * u + y / 19.0 + math.sin(5 * u) * 1.5) + 0.25 * math.sin(7 * u - y / 11.0)
            band_ = max(0.0, math.sin(y / 9.0 + 3 * math.sin(2 * u + 0.7) + 0.5 * math.sin(9 * u)))
            k = max(0.0, c - 0.4) * band_
            col = mix(base, (48, 44, 42), min(1, k * 1.3) * (1 - 0.7 * glow))
            if k > 0.05 and glow > 0:                       # the clouds' undersides lit low down
                col = mix(col, (176, 148, 110), 0.25 * glow * min(1, k * 3))
            im.px[y * W + x] = [col[0], col[1], col[2], 255]
    return im
