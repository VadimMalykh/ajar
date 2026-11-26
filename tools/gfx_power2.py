"""MAP33's look 2, "The Grid" (the 1960s): the same station as rebuilt by a national electricity board about
1962, a machine, not a temple. Fair-faced and board-marked concrete, pale ribbed cladding, continuous strips of
glazing in aluminium frames, grey painted steel, painted blockwork, vinyl tile, laminate, stencilled plant
numbers; a flat white overcast. Neutral to slightly warm greys and off-whites only: the doors are BLUE, VIOLET
and PINK and the parts yellow, green and red, which appear only as each place's phase band (a painted stripe,
the part's numeral stencilled black in a small white square along it), as the bar on a plate, the three ways of
the plan and the diagram, the synchroscope's lamps (and red on DANGER plates). Hazard marking is black and
white. The slots are tools/gfx_power.py's; the map's side is tools/power33.py.
"""
import math

import gfx_power as G
from gfx import DIGITS, Img, digit
from gfx_power import Wall, flat, h32, jit, mix, shade, text_width

# --- the palette (no blue: every grey has its blue lowest) --------------------------------------------------
CONC = (170, 166, 158)                  # fair-faced concrete
CONC_D = (146, 142, 134)                # board-marked, darker in ducts
CLAD = (214, 212, 204)                  # pale ribbed cladding
BLOCK = (226, 223, 214)                 # off-white painted blockwork
DADO = (92, 92, 88)                     # dark grey paint
ALU = (188, 188, 184)                   # aluminium
GREY = (124, 124, 120)                  # grey painted steel
ENAMEL = (136, 136, 132)                # grey enamel (cubicles, desks)
GALV = (156, 156, 150)                  # galvanised steel
LAM = (158, 158, 154)                   # grey laminate
WHITE = (238, 237, 232)
BLACK = (30, 30, 30)
INK = (26, 26, 26)
GLASS = (50, 52, 50)                    # dark glazing
LIT = (246, 238, 214)                   # a lit pane, warm white
AMBER = (236, 156, 44)
RED = (190, 40, 34)                     # DANGER plates only (part 3's places)


# === lettering: the game's face, stencilled ===================================================================
def stencil_on(w, s, c, ztop, col, ground, scale=2):
    """Stencilled letters with their bridges cut back to `ground`."""
    for n, ch in enumerate(s):
        rows = DIGITS[ch]
        mid = len(rows[0]) // 2
        for j, row in enumerate(rows):
            for i, on in enumerate(row):
                if on != "1":
                    continue
                x0, z0 = c + n * 6 * scale + i * scale, ztop - j * scale
                w.rect(x0, z0, x0 + scale, z0 - scale, col)
                if scale >= 2 and j in (0, len(rows) - 1) and i == mid and len(row) > 1:
                    w.rect(x0 + scale // 2, z0, x0 + scale // 2 + 1, z0 - scale, ground)


def stencil_mid(w, s, cx, ztop, col, ground, scale=2):
    stencil_on(w, s, cx - (len(s) * 6 * scale - scale) // 2, ztop, col, ground, scale)


# === patterns: f(x, z) -> colour (x along the wall in its period, z the row's top edge) =======================
def blockwork(c, P=64, seed=1, bl=32, bh=16, joint=0.91):
    """Painted blockwork: blocks 32 by 16 in stretcher bond, the joints showing through the paint."""
    nb = max(1, P // bl)

    def f(x, z):
        kz = (z - 1) // bh
        off = bl // 2 if kz % 2 else 0
        if z % bh == 0 or (x + off) % bl == 0:
            return jit(shade(c, joint), x, z, seed + 5, 0.01)
        k = h32(((x + off) // bl) % nb, kz, seed)
        g = 1 + (k - 0.5) * 0.03
        if z % bh == bh - 1 or (x + off) % bl == 1:
            g *= 0.965
        if h32(x, z, seed + 2) < 0.035:
            g *= 0.95
        return jit(shade(c, g), x // 2, z // 2, seed + 1, 0.01)
    return f


def boards(c, P=64, seed=2, bh=6, joint=0.86):
    """Board-marked concrete: the boards' imprint in courses `bh` high, their grain and butt joints."""
    nb = max(1, P // 64)

    def f(x, z):
        kz = (z - 1) // bh
        if z % bh == 0:
            return shade(c, joint + 0.05 * h32(x // 8, kz, seed))
        off = int(h32(kz, 0, seed) * 64)
        if (x + off) % 64 == 0:
            return shade(c, 0.88)
        k = h32(((x + off) // 64) % nb, kz, seed + 1)
        g = 0.93 + 0.12 * k + (h32(x // 7, kz, seed + 2) - 0.5) * 0.06
        if z % bh == 1:
            g *= 0.97
        return jit(shade(c, g), x // 2, z, seed + 3, 0.02)
    return f


def fairfaced(c, seed=3, pw=64, ph=48, ties=True, P=64):
    """Fair-faced concrete: smooth, the form panels' joints, tie holes in pairs."""
    nb = max(1, P // pw)

    def f(x, z):
        u, v = x % pw, z % ph
        if u == 0 or v == 0:
            return shade(c, 0.89)
        if ties and u in (16, 17, 48, 49) and v in (12, 13, 36, 37):
            return shade(c, 0.6 if (u in (17, 49) and v in (12, 36)) else 0.75)
        k = h32((x // pw) % nb, (z - 1) // ph, seed)
        g = 0.97 + 0.06 * k
        if h32(x, z, seed + 1) < 0.025:
            g *= 0.86
        return jit(shade(c, g), x // 3, z // 3, seed + 2, 0.025)
    return f


RIB = (1.13, 1.05, 1.05, 1.04, 0.8, 0.95) + (0.98,) * 10


def cladding(c, P=64, seed=4, lap=128):
    """Pale profiled sheeting: vertical ribs every 16, the sheets' end laps every `lap`, fixings along them."""
    nb = max(1, P // 64)

    def f(x, z):
        u = x % 16
        v = z % lap
        g = RIB[u]
        if v == 0:
            return shade(c, 0.66)
        if v == 1:
            g *= 1.06
        elif v == 4 and u == 2:
            return shade(c, 0.5)
        elif v == 5 and u == 2:
            return shade(c, 1.2)
        if x % 64 == 63 and u == 15:
            g *= 0.9
        k = h32((x // 64) % nb, (z - 1) // lap, seed)
        return jit(shade(c, g * (0.975 + 0.05 * k)), x // 4, z // 4, seed + 1, 0.01)
    return f


def glazing(lo, hi, lit=False, seed=5, pane=32):
    """A strip of glazing between lo and hi: aluminium frame, mullions every `pane`, dark glass with a
    reflection (or lit warm white, `lit` a fraction of panes)."""
    span = max(1, hi - lo)

    def f(x, z):
        u = x % pane
        if z > hi - 2 or z <= lo + 2:
            return shade(ALU, 1.15 if z in (hi, lo + 2) else 0.8)
        if u < 2:
            return shade(ALU, 1.1 if u == 0 else 0.78)
        t = (z - lo) / span
        if lit and h32(x // pane, 0, seed) < lit:
            return jit(shade(LIT, 0.9 + 0.12 * t), x // 2, z // 2, seed + 1, 0.02)
        g = 0.85 + 0.55 * t
        if (x - z) % 64 < 7:
            g += 0.35
        return jit(shade(GLASS, g), x // 2, z // 2, seed + 2, 0.03)
    return f


def daylight(lo, hi, seed=6, pane=32):
    """Glazing seen from inside by day: pale panes, aluminium bars, a transom."""
    span = max(1, hi - lo)
    mid = (lo + hi) // 2

    def f(x, z):
        u = x % pane
        if z > hi - 3 or z <= lo + 3 or u < 3 or z in (mid, mid + 1):
            return shade(ALU, 0.62 if u == 2 or z == lo + 1 else 0.85)
        t = (z - lo) / span
        return jit(shade((238, 236, 228), 0.94 + 0.08 * t), x // 2, z // 2, seed, 0.015)
    return f


def solid(c, amt=0.02, seed=7):
    return lambda x, z: jit(c, x // 2, z // 2, seed, amt)


def trim(w, ztop, zbot, c, lit=1.25, dark=0.62):
    w.fill(ztop, zbot, lambda x, z: shade(c, lit) if z == ztop else shade(c, dark) if z == zbot + 1 else c)


def chevrons(w, ztop, zbot, step=8):
    """Black and white hazard stripes, diagonal."""
    w.fill(ztop, zbot, lambda x, z: (226, 224, 218) if ((x + z) // step) % 2 else (34, 34, 34))


def band(w, F, part):
    """The phase band: a painted stripe in the part's colour from F + 72 to F + 80, the part's numeral
    stencilled black in a small white square every 64 along it."""
    if not part:
        return
    lo, hi = F + G.BAND[0], F + G.BAND[1]
    col = G.PART_COLOURS[part]
    glyph = DIGITS[str(part)]
    sq = (240, 239, 234)

    def f(x, z):
        u = x % 64
        if 27 <= u < 36:
            dz, dx = hi - 1 - z, u - 30
            if 0 <= dz < 5 and 0 <= dx < 3 and glyph[dz][dx] == "1":
                return INK
            return sq
        return jit(col, x // 8, 0, 41, 0.012)
    w.fill(hi, lo, f)


def skirting(w, F, h=6, c=(44, 44, 42)):
    """A black rubber skirting, its top edge lit."""
    w.fill(F + h, max(w.bot, F - 8), lambda x, z: shade(c, 1.6) if z == F + h else jit(c, x, z, 12, 0.04))


def streaks(w, ztop, zbot, c, density=0.1, strength=0.35, seed=30, width=2):
    """Runs down from ztop: lime or rust, of varying length."""
    def f(x, z, col):
        k = h32(x // width, 0, seed)
        if k < density:
            ln = 30 + h32(x // width, 1, seed) * (ztop - zbot)
            if ztop - z < ln:
                return mix(col, c, strength * (1 - (ztop - z) / ln))
        return col
    w.tint(ztop, zbot, f)


def ladder(w, zc, c1=0, c2=None, cables=True):
    """A galvanised cable ladder along the wall at zc (its rail), black cables on it."""
    c2 = c2 or w.w
    w.rect(c1, zc, c2, zc - 3, GALV)
    w.rect(c1, zc, c2, zc - 1, shade(GALV, 1.3))
    w.rect(c1, zc - 2, c2, zc - 3, shade(GALV, 0.6))
    if cables:
        for c in range(c1, c2):
            for k, (dz, g) in enumerate(((5, 1.0), (4, 1.6), (3, 1.2), (2, 0.8))):
                if k == 0 or c % 7:
                    w.at(c, zc + dz, shade((24, 24, 24), g))


# === the walls ================================================================================================
def rooms(w, F, part, top, dado=None, seed=8):
    """Painted blockwork (off-white), a dark grey painted dado up to `dado` over the floor, a black rubber
    skirting, an aluminium trim under the suspended ceiling; the stripe."""
    P = w.period
    w.fill(w.z0, w.bot, blockwork(BLOCK, P, seed))
    if dado:
        w.fill(F + dado, F, blockwork(DADO, P, seed))
        trim(w, F + dado + 1, F + dado - 1, shade(DADO, 0.8), 1.0, 1.0)
    if top is not None:
        w.fill(top, top - 3, lambda x, z: shade(ALU, 1.2 if z == top - 1 else 0.7 if z == top - 2 else 1.0))
        w.fill(top - 3, top - 5, lambda x, z: shade(BLOCK, 0.82))
    skirting(w, F)
    band(w, F, part)


def m_TD(w, F, part, top):
    rooms(w, F, part, top, dado=64)


def m_CO(w, F, part, top):
    rooms(w, F, part, top, seed=9)


def m_GP(w, F, part):
    """The gatehouse's pillars: fair-faced concrete, chamfered arrises, the stripe."""
    ff = fairfaced(shade(CONC, 1.08), 10, 64, 64, ties=False)

    def f(x, z):
        u = x % 64
        col = ff(x, z)
        if u < 2:
            return shade(col, 1.18 if u == 0 else 1.08)
        if u > 61:
            return shade(col, 0.8)
        return col
    w.fill(w.z0, w.bot, f)
    w.fill(F + 4, max(w.bot, F - 8), lambda x, z: shade(CONC, 0.7))
    band(w, F, part)


def m_CT(w):
    """The counter's front: off-white laminate in panels, a dark plinth, an aluminium edge."""
    lam = (226, 224, 216)

    def f(x, z):
        u = x % 64
        if z <= 5:
            return jit((50, 50, 48), x, z, 14, 0.04) if z < 5 else (80, 80, 76)
        if z >= 37:
            return shade(ALU, 1.25 if z == 40 else 1.0 if z > 37 else 0.7)
        if u == 0:
            return shade(lam, 0.78)
        if u == 1:
            return shade(lam, 1.04)
        return jit(shade(lam, 0.97 + 0.03 * (z - 6) / 30), x // 3, z // 3, 15, 0.01)
    w.fill(w.z0, w.bot, f)


def m_SK(w):
    """A floor's edge: a concrete kerb with a steel nosing."""
    cf = fairfaced(CONC, 17, 64, 16, ties=False)
    w.fill(w.z0, w.bot, cf)
    w.fill(w.z0, w.z0 - 3, lambda x, z: shade(GALV, 1.3 if z == w.z0 else 0.85 if z == w.z0 - 2 else 1.0))


def m_RI(w, kind):
    """A stair's risers: concrete with a galvanised nosing (`stone`), grey vinyl with an aluminium one."""
    c, nose = {"stone": ((164, 160, 152), GALV), "marble": ((150, 150, 146), ALU)}[kind]

    def f(x, z):
        m = z % 8
        if m in (0, 7):
            return shade(nose, 1.3 if m == 0 else 0.95)
        if m == 6:
            return shade(nose, 0.6)
        return jit(c, x // 2, z // 2, 18, 0.03)
    w.fill(w.z0, w.bot, f)


YD_GLAZ = (304, 336)                    # the yards' strip of glazing (absolute)


def m_YD(w, F, part, damp=0):
    """Out of doors: board-marked concrete to F + 192, pale ribbed cladding above it with one continuous strip
    of dark glazing in an aluminium frame, a dark flashing under the sky; a concrete column every 256."""
    P = w.period
    top = G.SKY_TOP
    w.fill(top, w.bot, cladding(CLAD, P, 19))
    lo, hi = YD_GLAZ
    w.fill(hi, lo, glazing(lo, hi, seed=20))
    w.fill(lo, lo - 3, lambda x, z: shade(ALU, 0.9 if z == lo else 0.55))
    w.fill(top, top - 12, lambda x, z: shade((64, 64, 62), 1.4 if z == top - 11 else 0.9 if z == top - 10 else 1.0))
    cb = F + 192
    w.fill(cb, w.bot, boards(CONC, P, 21))
    w.fill(cb + 4, cb, lambda x, z: shade(CONC, 1.22 if z == cb + 4 else 0.7 if z == cb + 1 else 1.05))
    w.fill(F + 97, F + 96, lambda x, z: shade(CONC, 0.74))            # the day joint
    w.tint(F + 18, w.bot, lambda x, z, c: mix(c, (96, 92, 86), 0.25 * (F + 18 - z) / 18) if z <= F + 18 else c)
    col = fairfaced(shade(CONC, 1.05), 22, 64, 96, ties=False)

    def column(x, z, c):
        d = min(x, P - x)                       # the column: 40 wide, centred at x 0
        if d >= 20:
            return c
        k = col(x, z)
        if d in (19, 18):
            k = shade(k, 1.2 if x > P // 2 else 0.68)
        return k
    w.tint(top - 12, w.bot, column)
    if damp:
        def wet(x, z, col):
            t = 0.42 * (1 - (z - w.bot) / 64) if z < w.bot + 64 else 0
            e = F + 44 - int(h32(x // 3, 0, 23) * 10)
            if z <= e:
                col = mix(col, (58, 56, 52), max(t, 0.3))
                if h32(x, 2, 24) < 0.1:
                    col = mix(col, (196, 192, 184), 0.22)
            return col
        w.tint(F + 56, w.bot, wet)
    band(w, F, part)


def m_SL(w):
    """The bunker's wall: precast concrete planks laid on edge between steel H-posts."""
    plank = (160, 156, 148)
    post = GREY

    def f(x, z):
        if x < 6 or x > 57:
            u = x if x < 6 else 63 - x
            return shade(post, (0.58, 1.2, 1.05, 1.0, 0.95, 0.7)[u])
        m = z % 16
        if m == 0:
            return shade(plank, 0.5)
        k = h32(0, (z - 1) // 16, 25)
        g = 0.9 + 0.12 * k
        if m == 15:
            g *= 1.12
        elif m == 1:
            g *= 0.86
        if h32(x, z, 26) < 0.03:
            g *= 0.85
        return jit(shade(plank, g), x // 3, z // 2, 26, 0.03)
    w.fill(w.z0, w.bot, f)
    w.fill(w.z0, w.z0 - 3, lambda x, z: shade(plank, 1.25))


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
        if glint and best < 0.9 and kb > 0.94:
            return glint
        if best < 1 and kb > 0.75:
            col = mix(col, hi, 0.25)
        return col
    return f


def m_CF(w):
    w.fill(w.z0, w.bot, lumps((40, 39, 38), (150, 148, 144), 27, 5, glint=(198, 196, 190)))


def m_EF(w):
    w.fill(w.z0, w.bot, lumps((86, 72, 58), (128, 116, 102), 28, 6))


def gravel(seed):
    """Grey-white gravel, calm: the stones' shading halved toward the ground's tone."""
    base = (182, 180, 174)
    fn = lumps(base, (222, 220, 214), seed, 3)
    return lambda x, z: mix(fn(x, z), base, 0.5)


def m_GF(w):
    w.fill(w.z0, w.bot, gravel(29))


def m_SF(w, F=None, part=0):
    """Retaining walls: board-marked concrete, a coping."""
    w.fill(w.z0, w.bot, boards(CONC, 64, 31))
    w.fill(w.z0, w.z0 - 3, lambda x, z: shade(CONC, 1.22 if z == w.z0 else 1.05))
    if part:
        band(w, F, part)


def m_PF(w):
    """The pond's revetment: precast concrete slabs, open joints, wet low down."""
    c = (158, 154, 146)

    def f(x, z):
        kz = (z - 1) // 32
        off = 32 if kz % 2 else 0
        if z % 32 == 0 or (x + off) % 64 == 0:
            return (96, 94, 90)
        k = h32(0, kz, 34)
        g = 0.92 + 0.1 * k
        if z % 32 == 1 or (x + off) % 64 == 63:
            g *= 0.9
        return jit(shade(c, g), x // 2, z // 2, 35, 0.04)
    w.fill(w.z0, w.bot, f)
    w.tint(w.bot + 24, w.bot, lambda x, z, col: mix(col, (70, 68, 62), 0.35 * (w.bot + 24 - z) / 24))


def m_CH(w):
    """The chimney: plain concrete, a formwork ring every 24, two black bands high up, a concrete base."""
    c = (186, 182, 174)

    def f(x, z):
        m = z % 24
        if m == 0:
            return shade(c, 0.8)
        if m == 23:
            return shade(c, 1.05)
        k = h32(0, (z - 1) // 24, 36)
        return jit(shade(c, 0.96 + 0.06 * k), x // 2, z // 3, 37, 0.02)
    w.fill(w.z0, w.bot, f)
    w.fill(48, w.bot, fairfaced(shade(CONC, 0.92), 38, 64, 48, ties=False))
    w.fill(52, 48, lambda x, z: shade(CONC, 1.2 if z == 52 else 0.75 if z == 49 else 1.0))
    t = w.z0
    for a, b in ((t - 8, t - 22), (t - 44, t - 58)):
        w.fill(a, b, lambda x, z, a=a, b=b: shade(BLACK, 1.5 if z == a else 0.8 if z == b + 1 else 1.0))
    w.fill(t, t - 3, lambda x, z: shade(BLACK, 1.3))
    streaks(w, t - 58, t - 300, (120, 118, 112), 0.08, 0.18, seed=39)


BH_GLAZ = (296, 336)                    # the boiler house's strip of glazing (absolute)


def m_BH(w, F, part):
    """The boiler house: grey painted steel stanchions every 128, painted blockwork to F + 112, pale ribbed
    cladding above, a strip of glazing high up, a girt, the eaves beam."""
    P = w.period
    w.fill(w.z0, w.bot, cladding(shade(CLAD, 0.97), P, 40, 96))
    lo, hi = BH_GLAZ
    w.fill(hi, lo, glazing(lo, hi, seed=41))
    w.fill(F + 112, w.bot, blockwork(BLOCK, P, 42))
    trim(w, F + 114, F + 111, ALU)
    w.fill(F + 256, F + 248, lambda x, z: shade(GREY, 1.3 if z == F + 256 else 0.7 if z == F + 249 else 1.0))
    w.fill(w.z0, w.z0 - 10, lambda x, z: shade(GREY, 1.2 if z == w.z0 - 9 else 0.8))
    skirting(w, F)

    def stanchion(x, z, c):
        d = min(x, P - x)
        if d >= 8:
            return c
        if d == 0:
            return shade(GREY, 0.55)
        return jit(shade(GREY, 1.2 if d in (1, 6) else 0.85 if d == 7 else 1.0), x, z // 3, 43, 0.015)
    w.tint(w.z0, w.bot, stanchion)
    band(w, F, part)


def m_BS(w):
    """A boiler's sides: pale lagging panels, aluminium strap bands, a lit top edge."""
    lag = (218, 216, 208)

    def f(x, z):
        u, v = x % 64, z % 48
        if z % 96 in (40, 41, 42):
            return shade(ALU, (0.7, 1.0, 1.25)[z % 96 - 40])
        if u == 0 or v == 0:
            return shade(lag, 0.78)
        if u == 1 or v == 47:
            return shade(lag, 1.04)
        k = h32(x // 64, (z - 1) // 48, 44)
        return jit(shade(lag, 0.96 + 0.05 * k), x // 3, z // 3, 45, 0.01)
    w.fill(w.z0, w.bot, f)
    w.fill(w.z0, w.z0 - 4, lambda x, z: shade(lag, 1.12 if z == w.z0 else 0.92))


def m_SE(w):
    """A firing step's edge: a galvanised nosing, black and white chevrons on the riser."""
    chevrons(w, w.z0 - 3, w.bot, 6)
    w.fill(w.z0, w.z0 - 3, lambda x, z: shade(GALV, 1.3 if z == w.z0 else 0.8 if z == w.z0 - 2 else 1.0))


def m_AT(w, F, part):
    """The ash tunnel: a board-marked concrete duct."""
    w.fill(w.z0, w.bot, boards(CONC_D, 64, 46))
    w.tint(F + 16, w.bot, lambda x, z, c: mix(c, (104, 102, 96), 0.3))
    band(w, F, part)


def m_PC(w, F):
    """A pump's casing: pale grey paint, a black and white band, a bolted flange at the top. (No stencil: the
    octagon's square faces are laid by world position, so lettering would be cut anywhere.)"""
    top = w.z0
    c = (196, 196, 190)

    def f(x, z):
        u = x % 64
        if z > top - 4:
            return shade(c, 1.2 if z == top else 0.85 if z == top - 3 else 1.0)
        if z == top - 6 and u % 8 == 4:
            return shade(c, 1.4)
        if z == top - 7 and u % 8 == 4:
            return shade(c, 0.5)
        if F + 18 < z <= F + 26:
            return (232, 230, 224) if ((u + z) // 6) % 2 else (34, 34, 34)
        if z <= F + 6:
            return shade((66, 66, 64), 1.3 if z == F + 6 else 1.0)
        g = 0.93 + 0.1 * math.sin(math.pi * u / 64)
        return jit(shade(c, g), x // 2, z // 2, 48, 0.015)
    w.fill(w.z0, w.bot, f)


def m_LP(w):
    """A pipe run clad in aluminium sheet: round, a band every 64, the sheets' laps."""
    top, bot = w.z0, w.bot

    def f(x, z):
        t = (z - bot) / max(1, top - bot)
        g = 0.68 + 0.42 * math.sin(t * math.pi)
        u = x % 64
        if u < 3:
            return shade(ALU, (0.72 + 0.5 * g) * (1.1 if u == 1 else 0.95))
        if u == 32:
            g *= 0.9
        return jit(shade(ALU, g), x // 3, z, 49, 0.015)
    w.fill(w.z0, w.bot, f)


CLER = (280, 352)                       # the turbine hall's strip window (absolute), the crane rail under it


def m_TH(w, F, part):
    """The turbine hall: fair-faced concrete to F + 128, pale ribbed sheeting above, the grey crane rail,
    the continuous strip window high up (daylight), sheeting to the eaves."""
    P = w.period
    lo, hi = CLER
    w.fill(w.z0, w.bot, cladding(CLAD, P, 50, 128))
    w.fill(hi, lo, daylight(lo, hi, 51))
    w.fill(F + 128, w.bot, fairfaced(CONC, 52, 64, 64, P=P))
    trim(w, F + 130, F + 127, ALU)
    w.fill(lo, lo - 6, lambda x, z: shade(GREY, 1.25 if z == lo else 0.7 if z == lo - 5 else 1.0))
    rail = (110, 110, 106)
    w.fill(lo - 10, lo - 26, lambda x, z: shade(rail, 1.3) if z == lo - 10 else
           shade(rail, 1.6) if x % 16 == 8 and z in (lo - 14, lo - 22) else
           shade(rail, 0.6) if z == lo - 25 else shade(rail, 0.9))
    w.fill(w.z0, w.z0 - 6, lambda x, z: shade(GREY, 1.15 if z == w.z0 - 5 else 0.8))
    skirting(w, F, 6)
    band(w, F, part)


def m_GG(w):
    """The gantry's edge over R: a welded plate girder painted grey, stiffeners every 64."""
    top, bot = w.z0, w.bot
    g = GREY

    def f(x, z):
        if z > top - 8 or z <= bot + 8:
            return shade(g, 1.3 if z in (top, bot + 8) else 0.85 if z in (top - 7, bot + 1) else 1.0)
        u = x % 64
        if u < 6:
            return shade(g, (0.65, 1.2, 1.1, 1.05, 1.0, 0.75)[u])
        return jit(g, x // 3, z // 3, 52, 0.025)
    w.fill(w.z0, w.bot, f)
    chevrons(w, top, top - 6, 8)


def m_TE(w):
    """A turbine casing's ends: pale grey sheet in panels."""
    c = (196, 196, 192)

    def f(x, z):
        if z % 48 in (0, 1):
            return shade(c, 0.72 if z % 48 == 0 else 1.1)
        if x % 64 == 0:
            return shade(c, 0.8)
        return jit(c, x // 3, z // 3, 53, 0.015)
    w.fill(w.z0, w.bot, f)


def m_SW(w):
    """The spider's pit: bare concrete, two pipes along it, chevrons round its lip."""
    w.fill(w.z0, w.bot, fairfaced(shade(CONC, 0.78), 54, 64, 64, ties=False))
    for zc, c in ((w.bot + 26, GREY), (w.bot + 13, ALU)):
        w.fill(zc + 3, zc - 3, lambda x, z, zc=zc, c=c: shade(c, 0.65 + 0.5 * math.cos((z - zc) / 3.5)))
    chevrons(w, w.z0, w.z0 - 5, 8)


def m_CW(w):
    """A condenser pit: the steel tube plate, rows of tube ends."""
    plate_c = (128, 128, 124)

    def f(x, z):
        u, v = x % 6, z % 6
        d = (u - 3) ** 2 + (v - 3) ** 2
        if d <= 4:
            return (36, 36, 34) if d <= 1 else (166, 166, 160)
        return jit(plate_c, x, z, 55, 0.03)
    w.fill(w.z0, w.bot, f)


def m_WS(w, F, part):
    """The workshop: white painted blockwork, a dark grey dado, a grey steel channel under the roof."""
    P = w.period
    w.fill(w.z0, w.bot, blockwork((232, 230, 224), P, 56))
    w.fill(F + 64, F, blockwork(shade(DADO, 0.85), P, 56))
    w.fill(w.z0, w.z0 - 8, lambda x, z: shade(GREY, 1.2 if z == w.z0 - 7 else 0.8))
    skirting(w, F, 5)
    band(w, F, part)


def m_BN(w):
    """A bench's front: grey steel drawers with aluminium pulls under a laminate top."""
    top = w.z0
    steel = (128, 128, 124)

    def f(x, z):
        u = x % 32
        if z > top - 4:
            return shade(LAM, 1.25 if z == top else 0.95) if z > top - 3 else shade(ALU, 0.8)
        if z <= w.bot + 3:
            return (44, 44, 42)
        if u < 2:
            return shade(steel, 0.6 if u == 0 else 1.2)
        if 11 < u < 21 and top - 12 >= z > top - 14:
            return shade(ALU, 1.2 if z == top - 12 else 0.8)
        if z == top - 22:
            return shade(steel, 0.6)
        if z == top - 23:
            return shade(steel, 1.15)
        return jit(steel, x // 2, z // 2, 59, 0.02)
    w.fill(w.z0, w.bot, f)


def m_LA(w):
    """A lathe's side: machine grey, a black base, the bed and its ways, the headstock, a handwheel, the
    motor's rating stencilled white on the base."""
    P = w.period
    bot, top = w.bot, w.z0
    mg = (118, 118, 114)
    w.fill(top, bot, lambda x, z: jit(mg, x // 2, z // 2, 60, 0.02))
    w.fill(top, top - 9, lambda x, z: shade((184, 184, 180), 1.2 if z == top else 0.9))   # the ways
    w.fill(top - 9, top - 14, lambda x, z: shade(mg, 0.6))
    w.rect(0, top, 30, top - 46, shade(mg, 1.08))                                         # the headstock
    w.frame(0, top, 30, top - 46, shade(mg, 0.6))
    w.disc(15, top - 22, 9, (170, 170, 166))                                               # the chuck
    w.disc(15, top - 22, 3, (44, 44, 42))
    cx, cz = 86, bot + 40                                                                  # the handwheel
    w.ring(cx, cz, 8, 10, (176, 176, 170))
    for a in range(0, 360, 120):
        t = math.radians(a + 30)
        w.line(cx, cz, cx + 8 * math.cos(t), cz + 8 * math.sin(t), (160, 160, 154))
    w.disc(cx, cz, 2, (60, 60, 58))
    w.rect(2, bot + 28, P - 2, bot, (36, 36, 36))                                           # the base
    w.rect(2, bot + 28, P - 2, bot + 27, (70, 70, 68))
    stencil_on(w, "7 HP", 40, bot + 20, (232, 230, 224), (36, 36, 36), 2)


def m_AR(w, F, part):
    """The armoury: steel sheet walls painted grey, bolted at the seams."""
    c = (130, 130, 126)

    def f(x, z):
        u, v = x % 32, z % 96
        if u == 0 or v == 0:
            return shade(c, 0.6)
        if u == 1 or v == 95:
            return shade(c, 1.15)
        if (u in (4, 28) and v % 12 == 6) or (v in (4, 91) and u % 8 == 4):
            return shade(c, 1.4)
        return jit(c, x // 3, z // 3, 61, 0.02)
    w.fill(w.z0, w.bot, f)
    skirting(w, F, 5)
    band(w, F, part)


def m_TU(w, F, part):
    """The cable tunnel: board-marked concrete, galvanised brackets, two cable ladders with black cables."""
    w.fill(w.z0, w.bot, boards(CONC_D, 64, 62))
    for x0 in (14, 46):
        w.rect(x0, F + 66, x0 + 3, F + 28, shade(GALV, 0.9))
        w.rect(x0, F + 66, x0 + 1, F + 28, shade(GALV, 1.2))
    for zc in (F + 38, F + 60):
        ladder(w, zc)
    w.fill(F + 4, max(w.bot, F - 8), lambda x, z: shade(CONC_D, 0.7))
    band(w, F, part)


def m_TR(w, F=0, part=0):
    """A cable tray's edge: a galvanised channel, cable ends in it."""
    def f(x, z):
        if z == w.z0 or z == w.bot + 1:
            return shade(GALV, 1.3)
        dd = (x % 6 - 3) ** 2 + (z % 6 - 3) ** 2
        if dd <= 4 and w.bot + 2 < z < w.z0 - 1:
            return (20, 20, 20) if dd > 1 else (120, 116, 108)
        return jit(shade(GALV, 0.85), x, z, 63, 0.02)
    w.fill(w.z0, w.bot, f)
    band(w, F, part)


def m_TF(w):
    """A transformer's cooling fins: radiator banks between headers, painted light grey."""
    top, bot = w.z0, w.bot
    g = (128, 128, 124)

    def f(x, z):
        if top - 12 < z <= top - 4 or bot + 4 < z <= bot + 12:
            return shade(g, 0.8 + 0.5 * math.sin((z % 8) / 8 * math.pi))
        if z > top - 4 or z <= bot + 4:
            return shade(g, 0.6)
        return shade(g, (0.45, 0.7, 1.0, 1.22, 1.28, 1.1, 0.85, 0.6)[x % 8])
    w.fill(w.z0, w.bot, f)


def m_PL(w):
    w.fill(w.z0, w.bot, lambda x, z: jit((178, 174, 166), x // 2, z, 64, 0.04) if z != w.z0 else (204, 200, 192))


def m_GL(w):
    """The switchyard's gantry: a galvanised lattice girder, its chords and diagonals."""
    top, bot = w.z0, w.bot

    def f(x, z):
        if z > top - 10 or z <= bot + 10:
            return shade(GALV, 1.25 if z in (top, bot + 10) else 0.95)
        u = x % 64
        h = z - bot - 10
        span = top - bot - 20
        d1 = abs(u - h * 64 / span)
        d2 = abs(u - (64 - h * 64 / span))
        if min(d1, d2) < 3 or u < 4:
            return shade(GALV, 1.15 if min(d1, d2) < 1.2 else 0.9)
        return jit((34, 34, 32), x, z, 65, 0.05)
    w.fill(w.z0, w.bot, f)


def m_RR(w, F, part):
    """The relay room: painted blockwork, a dark grey dado, an aluminium trim."""
    rooms(w, F, part, None, dado=64, seed=66)
    trim(w, w.z0, w.z0 - 4, ALU)


def m_RC(w):
    """The relay cubicles: grey steel, rows of small relays behind windows, a white label strip under each."""
    steel = (132, 132, 128)

    def f(x, z):
        u = x % 64
        if u in (0, 63):
            return (40, 40, 38)
        if u == 1:
            return shade(steel, 1.2)
        return jit(steel, x // 2, z // 2, 69, 0.015)
    w.fill(w.z0, w.bot, f)
    for zr in (w.z0 - 8, w.z0 - 34, w.z0 - 60):
        for base in range(0, w.w, 64):
            w.rect(base + 4, zr, base + 60, zr - 16, shade(ALU, 0.8))
            w.rect(base + 5, zr - 1, base + 59, zr - 15, (66, 68, 66))
            for c in range(base + 7, base + 57, 10):
                w.rect(c, zr - 3, c + 7, zr - 13, (40, 40, 40))
                w.rect(c + 1, zr - 4, c + 6, zr - 6, (210, 208, 200))
                w.rect(c + 2, zr - 9, c + 5, zr - 11, (90, 90, 88))
            w.rect(base + 5, zr - 1, base + 59, zr - 2, (104, 106, 104))
            w.rect(base + 6, zr - 18, base + 58, zr - 22, (232, 231, 226))
            for c in range(base + 9, base + 56, 10):
                w.rect(c, zr - 19, c + 5, zr - 20, (120, 120, 116))
    w.fill(w.bot + 5, w.bot, lambda x, z: (36, 36, 34))


def m_OC(w, F, part):
    """The outfall: a concrete culvert, wet and stained low down, lime streaks."""
    w.fill(w.z0, w.bot, boards(shade(CONC, 0.88), 64, 70))
    w.tint(F + 56, w.bot, lambda x, z, c: mix(c, (60, 58, 52), 0.42))
    streaks(w, F + 56, w.bot, (196, 194, 184), 0.15, 0.3, seed=71)
    band(w, F, part)


def m_TW(w, F, part):
    """The cooling tower's shell from inside: concrete board-marked in rings (lifts of 24), lime and rust-brown
    streaks running down, a ring beam high up."""
    conc = (170, 166, 158)

    def f(x, z):
        m = z % 24
        if m == 0:
            return shade(conc, 0.78)
        if m == 1:
            return shade(conc, 0.92)
        k = h32(0, (z - 1) // 24, 72)
        g = 0.95 + 0.08 * k
        if z % 6 == 0:
            g *= 0.96
        return jit(shade(conc, g), x // 3, z // 2, 73, 0.03)
    w.fill(w.z0, w.bot, f)
    streaks(w, 400, w.bot, (238, 236, 228), 0.2, 0.75, seed=74, width=3)
    streaks(w, 400, w.bot, (108, 74, 48), 0.1, 0.7, seed=75, width=2)
    w.fill(418, 400, lambda x, z: shade(conc, 1.22 if z == 418 else 0.68 if z == 401 else 1.02))
    band(w, F, part)


def m_TP(w):
    conc = (176, 172, 164)
    w.fill(w.z0, w.bot, lambda x, z: shade(conc, 1.18) if x % 64 < 2 else
           shade(conc, 0.78) if z % 24 == 0 else jit(conc, x // 3, z // 3, 76, 0.03))
    streaks(w, w.z0, w.bot, (236, 234, 226), 0.14, 0.6, seed=77, width=3)
    streaks(w, w.z0, w.bot, (108, 74, 48), 0.08, 0.6, seed=78, width=2)


def m_TL(w):
    conc = (170, 166, 158)
    w.fill(w.z0, w.bot, lambda x, z: shade(conc, 0.7) if x % 32 == 0 else jit(conc, x // 2, z // 2, 79, 0.03))
    w.fill(w.z0, w.z0 - 6, lambda x, z: shade(conc, 1.28 if z == w.z0 else 0.75 if z == w.z0 - 5 else 1.05))


def m_DK(w, F, part):
    """The duct along R: board-marked concrete, a cable ladder rack high up with black cables."""
    w.fill(w.z0, w.bot, boards(CONC_D, 64, 80))
    w.rect(30, F + 128, 33, F + 94, shade(GALV, 0.9))
    for zc in (F + 100, F + 112, F + 124):
        ladder(w, zc)
    w.fill(F + 4, max(w.bot, F - 8), lambda x, z: shade(CONC_D, 0.7))
    band(w, F, part)


def m_LH(w, F, part):
    """The switchgear hall, a control room of the 1960s: grey laminate panels with aluminium joints up to the
    stands' level (0), pale perforated acoustic panels with aluminium strips above, a plain cornice line; its
    stands the same with their part's stripe."""
    pale = (216, 214, 206)

    def acoustic(x, z):
        u = x % 64
        if u < 3:
            return shade(ALU, (0.7, 1.25, 0.95)[u])
        if z % 128 == 0:
            return shade(pale, 0.72)
        if z % 128 == 127:
            return shade(pale, 1.05)
        if x % 3 == 1 and z % 3 == 1:
            return shade(pale, 0.955)
        return jit(pale, x // 4, z // 4, 77, 0.008)
    w.fill(w.z0, w.bot, acoustic)

    def dado(x, z):
        u = x % 64
        if u < 2:
            return shade(ALU, 0.75 if u == 0 else 1.2)
        k = h32(x // 64, 0, 78)
        return jit(shade(LAM, 0.97 + 0.05 * k + 0.03 * (z + 96) / 96), x // 3, z // 3, 79, 0.01)
    w.fill(0, w.bot, dado)
    w.fill(4, 0, lambda x, z: shade(ALU, 1.25 if z == 4 else 0.7 if z == 1 else 1.0))
    skirting(w, -96, 6)
    w.fill(w.z0, w.z0 - 10, lambda x, z: shade(pale, 1.05 if z > w.z0 - 8 else 0.7 if z == w.z0 - 9 else 0.85))
    band(w, F, part)


def m_SN(w):
    """A switchgear cabinet's ends: grey enamel, a rim."""
    def f(x, z):
        if z > w.z0 - 3:
            return shade(ENAMEL, 1.25 if z == w.z0 else 0.95)
        if x % 64 in (0, 63):
            return shade(ENAMEL, 0.55)
        if z <= w.bot + 4:
            return (40, 40, 38)
        return jit(ENAMEL, x // 2, z // 2, 81, 0.015)
    w.fill(w.z0, w.bot, f)


def m_SH(w):
    """The sheds: plain grey painted blockwork."""
    w.fill(w.z0, w.bot, blockwork((172, 170, 162), 64, 82, joint=0.86))


WALLS = dict(TD=m_TD, CO=m_CO, GP=m_GP, CT=m_CT, SK=m_SK, RI=m_RI, YD=m_YD, SL=m_SL, CF=m_CF, EF=m_EF, GF=m_GF,
             SF=m_SF, PF=m_PF, CH=m_CH, BH=m_BH, BS=m_BS, SE=m_SE, AT=m_AT, PC=m_PC, LP=m_LP, TH=m_TH, GG=m_GG,
             TE=m_TE, SW=m_SW, CW=m_CW, WS=m_WS, BN=m_BN, LA=m_LA, AR=m_AR, TU=m_TU, TR=m_TR, TF=m_TF, PL=m_PL,
             GL=m_GL, RR=m_RR, RC=m_RC, OC=m_OC, TW=m_TW, TP=m_TP, TL=m_TL, DK=m_DK, LH=m_LH, SN=m_SN, SH=m_SH)


# === pictures =================================================================================================
def sign(w, cx, zbot, lines, ground=WHITE, ink=INK, rim=ALU, pad=3, bar=None, scale=1):
    """A sign with lines of capitals, centred at cx, its foot at zbot, in an aluminium rim; `bar` the part's
    colour as a bar at its left end. Returns its top."""
    tw = max(text_width(s, scale) for s in lines)
    lh = 7 * scale
    hgt = len(lines) * lh - 2 * scale + 2 * pad
    bw = 6 if bar else 0
    c1 = cx - (tw + bw) // 2 - pad - 2
    c2 = c1 + tw + bw + 2 * pad + 4
    top = zbot + hgt + 1
    w.rect(c1, top, c2, zbot - 1, shade(rim, 0.7))
    w.rect(c1 + 1, top - 1, c2 - 1, zbot, rim)
    w.rect(c1 + 1, top - 1, c2 - 1, top - 1 - 1, shade(rim, 1.25))
    w.rect(c1 + 2, top - 2, c2 - 2, zbot + 1, ground)
    if bar:
        w.rect(c1 + 2, top - 2, c1 + 2 + bw, zbot + 1, bar)
    for k, s in enumerate(lines):
        w.centre(s, cx + bw // 2 + 1, top - pad - 1 - k * lh, ink, scale)
    return top


def p_plate(w, spec):
    sign(w, spec["w"] // 2, spec["head"] + 6, spec["words"], bar=G.PART_COLOURS[spec["part_no"]])


def p_plateside(w, spec):
    cx, at = spec["w"] // 2, spec["at"]
    sign(w, cx, at + 14, spec["words"], bar=G.PART_COLOURS[spec["part_no"]])
    cz, a = at + 7, spec["arrow"]
    w.rect(cx - 12, cz + 1, cx + 12, cz - 1, INK)
    for i in range(5):
        c = cx + 12 + i if a > 0 else cx - 13 - i
        w.rect(c, cz + 5 - i, c + 1, cz - 5 + i, INK)


def p_danger(w, spec):
    cx, at = spec["w"] // 2, spec["at"]
    c1, c2 = cx - 22, cx + 22
    w.rect(c1, at + 34, c2, at, (238, 236, 230))
    w.frame(c1, at + 34, c2, at, RED, 2)
    w.rect(c1, at + 34, c2, at + 22, RED)
    w.centre("DANGER", cx, at + 31, (244, 242, 236))
    w.centre("33000", cx, at + 18, RED)
    w.centre("VOLTS", cx, at + 10, (30, 30, 30))


def p_window(w, spec):
    """A horizontal window in a yard's cladding: an aluminium frame, four panes, dark (or lit warm white),
    a sill."""
    lit = spec.get("lit")
    c1, c2, lo, hi = 4, 60, 228, 262
    w.rect(c1 - 1, hi + 1, c2 + 1, lo - 1, shade(ALU, 0.6))
    w.rect(c1 - 2, lo - 1, c2 + 2, lo - 4, shade(ALU, 0.95))
    w.rect(c1 - 2, lo - 3, c2 + 2, lo - 4, shade(ALU, 0.55))
    for z in range(lo, hi + 1):
        for c in range(c1, c2):
            u = (c - c1) % 14
            if u < 2 or z <= lo + 1 or z >= hi - 1:
                col = shade(ALU, 1.1 if u == 0 or z == hi else 0.8)
            elif lit and (c - c1) // 14 != 1:
                col = jit(shade(LIT, 0.9 + 0.12 * (z - lo) / (hi - lo)), c // 3, z // 3, 84, 0.02)
            else:
                g = 0.85 + 0.5 * (z - lo) / (hi - lo)
                if (c - z) % 40 < 5:
                    g += 0.3
                col = jit(shade(GLASS, g), c // 2, z // 2, 85, 0.03)
            w.at(c, z, col)


def p_bhwindow(w, spec):
    """A glazed bay under the boiler house's strip of glazing: the glass runs down to 224 here."""
    c1, c2 = 2, 62
    lo, hi = 224, BH_GLAZ[0] + 2
    f = glazing(lo, hi, seed=86)
    for z in range(lo + 1, hi + 1):
        for c in range(c1, c2):
            w.at(c, z, f(c, z) if c1 + 1 < c < c2 - 2 else shade(ALU, 1.15 if c in (c1, c2 - 2) else 0.75))
    w.rect(c1 - 2, lo + 1, c2 + 2, lo - 3, shade(ALU, 0.9))
    w.rect(c1 - 2, lo - 2, c2 + 2, lo - 3, shade(ALU, 0.55))


def p_pilaster(w, spec):
    """A portal frame's concrete column on the turbine hall's wall, from the floor to the eaves; a corbel
    under the crane rail; the stripe painted round it."""
    W = spec["w"]
    bp = spec["basespec"]["params"]
    F, part = bp["F"], bp.get("part", 0)
    c1, c2 = (0, W) if W <= 32 else (10, W - 10)
    lo, hi = CLER
    col = fairfaced(shade(CONC, 1.06), 87, 64, 96, ties=False)
    for z in range(F + 1, w.z0 + 1):
        for c in range(c1, c2):
            u = c - c1
            k = col(u, z)
            if u < 2:
                k = shade(k, 1.2)
            elif u >= c2 - c1 - 2:
                k = shade(k, 0.7)
            w.at(c, z, k)
    k1, k2 = (0, W) if W <= 32 else (4, W - 4)
    for z in range(lo - 48, lo - 9):
        t = (z - (lo - 48)) / 38
        for c in range(k1, k2):
            if c1 <= c < c2 or t > 0.4:
                w.at(c, z, shade(CONC, 1.12 if z == lo - 10 else 0.95 + 0.1 * t))
    w.rect(c1, F + 4, c2, F, shade(CONC, 0.7))
    band(w, F, part)


def p_cplate(w, spec):
    """The chimney's aluminium plate: 1962."""
    w.rect(14, 92, 50, 70, shade(ALU, 0.6))
    w.rect(15, 91, 49, 71, ALU)
    w.rect(15, 91, 49, 90, shade(ALU, 1.25))
    for k, ch in enumerate("1962"):
        im = Img(6, 10, (0, 0, 0, 0))
        digit(im, ch, 0, 0, INK, 2)
        w.paste(im, 18 + k * 8, 86)


def p_boiler(w, spec):
    """A boiler's front clad in pale lagging panels with strap bands: two access doors low down with wheel
    handles, a sight port with an amber dot, an instrument panel (two square dials, a row of white and amber
    lamps), BOILER n stencilled large. `gap`: the frame's columns, kept clear."""
    W = spec["w"]
    n = spec["n"]
    lag = (220, 218, 210)

    def f(x, z):
        u, v = x % 56, z % 48
        if z in (96, 97, 98, 176, 177, 178, 256, 257, 258):
            return shade(ALU, (0.7, 1.0, 1.25)[(z - 96) % 80 % 3])
        if u == 0 or v == 0:
            return shade(lag, 0.8)
        if u == 1 or v == 47:
            return shade(lag, 1.03)
        return jit(shade(lag, 0.97 + 0.04 * h32(x // 56, (z - 1) // 48, 88)), x // 3, z // 3, 89, 0.01)
    w.fill(w.z0, w.bot, f)
    w.fill(w.z0, w.z0 - 4, lambda x, z: shade(lag, 1.1 if z == w.z0 else 0.9))
    gap = spec.get("gap")
    for cx in (40, W - 40):                                     # the access doors
        w.rect(cx - 25, 86, cx + 25, 12, shade(GREY, 0.6))
        w.rect(cx - 23, 84, cx + 23, 14, GREY)
        w.rect(cx - 23, 84, cx + 23, 83, shade(GREY, 1.3))
        for hz in (74, 24):
            w.rect(cx - 26, hz, cx - 21, hz - 6, (60, 60, 58))
        hx, hz = cx + 6, 49                                     # the wheel handle
        w.ring(hx, hz, 7, 9, (48, 48, 46))
        for a in (0, 60, 120):
            t = math.radians(a)
            w.line(hx - 8 * math.cos(t), hz - 8 * math.sin(t), hx + 8 * math.cos(t), hz + 8 * math.sin(t),
                   (56, 56, 54))
        w.disc(hx, hz, 2, (170, 170, 164))
    if gap:
        px, sight, numx = gap[1] + 40, (40, 104), gap[1] + 40
    else:
        px, sight, numx = W // 2, (W // 2, 52), W // 2
    sx, sz = sight                                              # the sight port
    w.disc(sx, sz, 7, (60, 60, 58))
    w.disc(sx, sz, 5, (40, 38, 36))
    w.disc(sx, sz, 2.5, AMBER)
    w.disc(sx - 1, sz + 1, 1, (255, 220, 150))
    p1, p2, pt, pb = px - 34, px + 34, 232, 192                 # the instrument panel
    w.rect(p1 - 1, pt + 1, p2 + 1, pb - 1, (60, 60, 58))
    w.rect(p1, pt, p2, pb, (112, 112, 108))
    w.rect(p1, pt, p2, pt - 1, (140, 140, 136))
    for dx in (px - 18, px + 2):                                # two square dials
        w.rect(dx - 1, pt - 5, dx + 17, pt - 23, (30, 30, 30))
        w.rect(dx, pt - 6, dx + 16, pt - 22, (236, 234, 226))
        for k in range(5):
            t = math.radians(150 - k * 30)
            ox, oz = dx + 8, pt - 20
            w.at(ox + 12 * math.cos(t), oz + 12 * math.sin(t), INK)
        t = math.radians(150 - 120 * (0.55 if dx < px else 0.7))
        w.line(dx + 8, pt - 20, dx + 8 + 11 * math.cos(t), pt - 20 + 11 * math.sin(t), INK)
    for k in range(6):                                          # a row of lamps
        lx = px - 25 + k * 10
        w.disc(lx, pb + 7, 3, (40, 40, 38))
        w.disc(lx, pb + 7, 2, AMBER if k in (1, 4) else (244, 242, 232))
    if gap:                                                     # BOILER n stencilled
        stencil_mid(w, "BOILER", numx, 142, INK, lag, 2)
        stencil_mid(w, str(n), numx, 126, INK, lag, 4)
    else:
        stencil_mid(w, f"BOILER {n}", numx, 134, INK, lag, 3)


def p_casing(w, spec):
    """A turbine's casing: lagging clad in pale grey sheet, panel joints, a black and white band, NO n and
    30 MW 3000 RPM stencilled, a small aluminium plate."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    c = (198, 198, 194)

    def f(x, z):
        if z > top - 4:
            return shade(c, 1.2 if z == top else 0.9)
        if bot + 50 < z <= bot + 58:
            return (232, 230, 224) if ((x + z) // 8) % 2 else (34, 34, 34)
        if x % 80 == 0:
            return shade(c, 0.78)
        if x % 80 == 1:
            return shade(c, 1.05)
        if z <= bot + 5:
            return shade(c, 0.55)
        return jit(shade(c, 0.97 + 0.05 * math.sin((z - bot) / 96 * math.pi)), x // 3, z // 3, 89, 0.012)
    w.fill(top, bot, f)
    cx = W // 2
    stencil_mid(w, f"NO {spec['n']}", cx - 40, bot + 88, INK, c, 4)
    stencil_mid(w, "30 MW 3000 RPM", cx, bot + 42, INK, c, 2)
    px = cx + 70                                                # the maker's plate
    w.rect(px, bot + 88, px + 40, bot + 66, shade(ALU, 0.6))
    w.rect(px + 1, bot + 87, px + 39, bot + 67, ALU)
    w.rect(px + 1, bot + 87, px + 39, bot + 86, shade(ALU, 1.25))
    for k, zl in enumerate((bot + 83, bot + 77, bot + 72)):
        w.rect(px + 5, zl, px + (35 if k else 28), zl - 1, (70, 70, 68))


def p_tend(w, spec):
    """A transformer's end: its tank painted light grey, bolted, the aluminium rating plate T<n>, a DANGER
    plate if `danger`."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    g = (128, 128, 124)
    w.fill(top, bot, lambda x, z: shade(g, 1.25 if z == top else 0.7 if z == top - 6 else 0.95) if z > top - 7 else
           jit(g, x // 2, z // 2, 90, 0.02))
    for c in range(6, W, 12):
        w.disc(c, top - 3, 1.2, shade(g, 1.5))
    cx = W // 2
    w.rect(cx - 23, bot + 85, cx + 23, bot + 61, shade(ALU, 0.6))
    w.rect(cx - 22, bot + 84, cx + 22, bot + 62, ALU)
    w.centre("T" + str(spec["n"]), cx, bot + 81, INK)
    w.centre("33 KV", cx, bot + 72, INK)
    if spec.get("danger"):
        p_danger(w, dict(w=W, at=bot + 18))
    w.rect(cx + 30, bot + 22, cx + 40, bot + 12, (70, 70, 68))
    w.disc(cx + 35, bot + 17, 4, (176, 176, 170))


def p_cabinet(w, spec):
    """A switchgear cubicle's long side in grey enamel: two doors, each with a square meter, a row of small
    switches and its number."""
    W = spec["w"]
    top, bot = w.z0, w.bot
    w.fill(top, bot, lambda x, z: shade(ENAMEL, 1.25 if z == top else 0.95) if z > top - 3 else
           (40, 40, 38) if z <= bot + 4 else jit(ENAMEL, x // 2, z // 2, 91, 0.015))
    for k in range(2):
        c1 = 3 + k * (W // 2)
        c2 = c1 + W // 2 - 6
        w.frame(c1, top - 4, c2, bot + 5, shade(ENAMEL, 0.55))
        w.rect(c1 + 1, top - 5, c2 - 1, top - 6, shade(ENAMEL, 1.2))
        mx = (c1 + c2) // 2
        w.rect(mx - 9, top - 8, mx + 9, top - 26, (34, 34, 34))       # the square meter
        w.rect(mx - 7, top - 10, mx + 7, top - 24, (238, 236, 228))
        for j in range(5):
            t = math.radians(150 - j * 30)
            w.at(mx + 10 * math.cos(t), top - 22 + 10 * math.sin(t), INK)
        w.line(mx, top - 22, mx - 4, top - 13, INK)
        for j in range(4):                                           # a row of small switches
            sx = mx - 14 + j * 8
            w.rect(sx, top - 31, sx + 5, top - 37, (40, 40, 38))
            w.rect(sx + 2, top - 30 - (0 if j % 2 else 4), sx + 3, top - 33 - (0 if j % 2 else 4), (210, 208, 200))
        w.rect(c2 - 7, bot + 30, c2 - 4, bot + 18, ALU)
        num = str(2 * spec["n"] - 1 + k)
        w.rect(mx - 9, bot + 16, mx + 9, bot + 8, (240, 238, 232))
        im = Img(len(num) * 4, 5, (0, 0, 0, 0))
        for i, ch in enumerate(num):
            digit(im, ch, i * 4, 0, INK, 1)
        w.paste(im, mx - len(num) * 2, bot + 14)


def p_store(w, spec):
    sign(w, spec["w"] // 2, 170, ("INSTRUMENT STORE",), bar=G.PART_COLOURS[2])


def board(w, c1, top, c2, bot, frame=ALU, ground=WHITE, t=3):
    w.rect(c1, top, c2, bot, shade(frame, 0.6))
    w.rect(c1 + 1, top - 1, c2 - 1, bot + 1, frame)
    w.rect(c1 + 1, top - 1, c2 - 1, top - 2, shade(frame, 1.25))
    w.rect(c1 + t, top - t, c2 - t, bot + t, ground)


def p_plan(w, spec):
    """GENERATING STATION: the plan on a white board in an aluminium frame, black lines; the three ways in
    yellow, green and red from the gatehouse to the switchgear hall, numbered."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 176, F + 44
    board(w, 0, top, W, bot)
    ink = INK
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
        col = shade(G.PART_COLOURS[k], 0.9)
        for a, b in zip(pts, pts[1:]):
            w.line(X(a[0]), Z(a[1]) + 1, X(b[0]), Z(b[1]) + 1, col, 2)
        ex_, ez_ = X(pts[-1][0]), Z(pts[-1][1])
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k), 0, 0, INK, 1)
        w.paste(im, int(X(9060)), int(ez_) + 3)
        w.line(ex_, ez_ + 1, X(9040), ez_ + 1, col, 1)
    ex, ey = pl["exit"]
    w.rect(X(ex) - 2, Z(ey) + 3, X(ex) + 2, Z(ey) - 2, ink)


def p_rules(w, spec):
    """The safety rules: a white plastic sign, black letters, a black rule round it."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 156, F + 56
    w.rect(4, top, W - 4, bot, (206, 206, 200))
    w.rect(5, top - 1, W - 5, bot + 1, (242, 241, 236))
    w.frame(8, top - 4, W - 8, bot + 4, INK)
    for c, z in ((7, top - 3), (W - 8, top - 3), (7, bot + 4), (W - 8, bot + 4)):
        w.disc(c, z, 1.2, (150, 150, 146))
    w.centre("SAFETY RULES", W // 2, top - 9, INK)
    w.rect(W // 2 - 38, top - 16, W // 2 + 38, top - 17, INK)
    lines = ["1. NO ONE IS TO WORK ALONE.", "2. KNOW WHERE YOUR MATES ARE", "   AT ALL TIMES.",
             "3. NEVER CLOSE A SWITCH", "   ANOTHER HAS OPENED."]
    for k, s in enumerate(lines):
        w.text(s, 13, top - 23 - k * 9, INK)
    w.text("BY ORDER", W - 13 - text_width("BY ORDER"), bot + 13, shade(INK, 2.2))


def p_shadow(w, spec):
    """A tool shadow board on white pegboard in an aluminium frame: black outlines of the tools; three of the
    tools gone from their outlines."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 160, F + 60
    board(w, 0, top, W, bot, frame=ALU, ground=(232, 231, 226), t=3)
    for z in range(bot + 5, top - 3, 6):
        for c in range(5, W - 3, 6):
            w.at(c, z, (176, 175, 170))
    sil = (28, 28, 28)
    steel = (176, 176, 172)
    handle = (64, 64, 62)

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


def p_single(w, spec):
    """The single-line diagram as a grey mimic panel: G1 and G2, the three busbars as yellow, green and red
    tape, the feeders TOWN, WORKS, INSTITUTE each with a square load meter: the institute's hard against its
    stop."""
    W = spec["w"]
    F = spec["basespec"]["params"]["F"]
    top, bot = F + 172, F + 44
    panel = (150, 150, 146)
    board(w, 0, top, W, bot, frame=ALU, ground=panel, t=3)
    for c in range(64, W - 3, 64):
        w.rect(c, top - 3, c + 1, bot + 3, shade(panel, 0.82))
    ink = (24, 24, 24)
    w.rect(W // 2 - 62, top - 5, W // 2 + 62, top - 14, (240, 238, 232))
    w.centre("SINGLE LINE DIAGRAM", W // 2, top - 7, ink)
    gz = (top - 40, top - 76)
    for k, gzz in enumerate(gz):
        w.disc(26, gzz, 10.5, (236, 234, 228))
        w.ring(26, gzz, 9, 10.5, ink)
        w.text("G", 20, gzz + 3, ink)
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k + 1), 0, 0, ink, 1)
        w.paste(im, 27, gzz + 3)
        w.line(37, gzz, 52, gzz, ink, 2)
    w.line(52, gz[0] + 6, 52, gz[1] - 30, ink, 2)
    bars = []
    for k in range(3):
        zb = top - 34 - k * 22
        col = G.PART_COLOURS[k + 1]
        w.rect(60, zb + 2, W - 14, zb - 2, col)
        w.rect(60, zb + 2, W - 14, zb + 1, mix(col, (255, 255, 255), 0.35))
        w.rect(52, zb + 1, 60, zb - 1, ink)
        bars.append(zb)
    names = ("TOWN", "WORKS", "INSTITUTE")
    for k, nm in enumerate(names):
        fx = 92 + k * 58
        w.line(fx, bars[0] + 1, fx, bot + 36, ink, 2)
        for zb in bars:
            w.rect(fx - 2, zb + 2, fx + 4, zb - 3, ink)
        mz = bot + 27                                            # the square meter
        w.rect(fx - 9, mz + 9, fx + 10, mz - 9, (34, 34, 34))
        w.rect(fx - 7, mz + 7, fx + 8, mz - 7, (240, 238, 230))
        for j in range(5):
            t = math.radians(150 - j * 30)
            w.at(fx + 9 * math.cos(t), mz - 5 + 9 * math.sin(t), ink)
        frac = 0.18 if k < 2 else 1.0
        t = math.radians(150 - 120 * frac)
        w.line(fx, mz - 5, fx + 8 * math.cos(t), mz - 5 + 8 * math.sin(t), ink)
        if k == 2:
            w.rect(fx + 7, mz + 1, fx + 9, mz - 3, ink)
        tw = text_width(nm)
        w.rect(fx - tw // 2 - 3, bot + 17, fx + tw // 2 + 4, bot + 8, (240, 238, 232))
        w.centre(nm, fx, bot + 15, ink)


def p_synchro(w, spec):
    """The synchroscope: a square-cased instrument with a round dial on a grey panel, its pointer straight up,
    SLOW to the left, FAST to the right; beside it three small square meters lettered 1, 2, 3, each with a lamp
    in its part's colour."""
    W = spec["w"]
    top, bot = 236, 40
    panel = (146, 146, 142)
    w.rect(0, top, W, bot, shade(ALU, 0.6))
    w.rect(1, top - 1, W - 1, bot + 1, ALU)
    w.rect(4, top - 4, W - 4, bot + 4, panel)
    for z in range(bot + 4, top - 4):
        for c in range(4, W - 4):
            if c % 64 == 0:
                w.at(c, z, shade(panel, 0.8))
    cx, cz = 72, 150
    w.rect(cx - 46, cz + 46, cx + 46, cz - 46, (32, 32, 32))           # the square case
    w.rect(cx - 46, cz + 46, cx + 46, cz + 45, (70, 70, 68))
    w.disc(cx, cz, 40, (240, 238, 230))
    w.ring(cx, cz, 39, 40.5, (90, 90, 88))
    for k in range(24):
        t = math.radians(90 - k * 15)
        r1 = 31 if k % 6 else 26
        w.line(cx + r1 * math.cos(t), cz + r1 * math.sin(t), cx + 36 * math.cos(t), cz + 36 * math.sin(t), INK)
    w.line(cx, cz - 6, cx, cz + 33, INK, 2)
    w.disc(cx, cz, 4, INK)
    w.text("SLOW", cx - 34, cz - 8, INK)
    w.text("FAST", cx + 34 - text_width("FAST"), cz - 8, INK)
    w.rect(cx - 40, cz - 52, cx + 41, cz - 62, (240, 238, 232))
    w.centre("SYNCHROSCOPE", cx, cz - 54, INK)
    for k in range(3):
        mx, mz = 158, 196 - k * 54
        w.rect(mx - 16, mz + 16, mx + 16, mz - 16, (32, 32, 32))
        w.rect(mx - 13, mz + 13, mx + 13, mz - 13, (240, 238, 230))
        for j in range(5):
            t = math.radians(150 - j * 30)
            w.at(mx + 11 * math.cos(t), mz - 7 + 11 * math.sin(t), INK)
        t = math.radians(120 - 40 * k)
        w.line(mx, mz - 7, mx + 11 * math.cos(t), mz - 7 + 11 * math.sin(t), INK)
        im = Img(3, 5, (0, 0, 0, 0))
        digit(im, str(k + 1), 0, 0, INK, 1)
        w.paste(im, mx - 1, mz + 11)
        lx = mx + 23
        w.disc(lx, mz, 5.5, (40, 40, 38))
        w.disc(lx, mz, 4, G.PART_COLOURS[k + 1])
        w.disc(lx - 1, mz + 1, 1.5, mix(G.PART_COLOURS[k + 1], (255, 255, 255), 0.6))


PICTURES = dict(plan=p_plan, rules=p_rules, shadow=p_shadow, single=p_single, synchro=p_synchro, plate=p_plate,
                plateside=p_plateside, danger=p_danger, window=p_window, bhwindow=p_bhwindow, pilaster=p_pilaster,
                cplate=p_cplate, boiler=p_boiler, casing=p_casing, tend=p_tend, cabinet=p_cabinet, store=p_store)


# === flats ====================================================================================================
def f_vinyl(base=(194, 192, 186), tile=32, seed=100, joint=0.93, fleck=0.1, size=64):
    """Vinyl tile: flecks of darker and lighter, faint joints."""
    def f(x, y):
        if x % tile == 0 or y % tile == 0:
            return shade(base, joint)
        k = h32(x, y, seed)
        if k < fleck * 0.5:
            return shade(base, 0.84)
        if k < fleck:
            return shade(base, 1.08)
        t = h32((x // tile) % (size // tile), (y // tile) % (size // tile), seed + 1)
        return jit(shade(base, 0.985 + 0.03 * t), x // 2, y // 2, seed + 2, 0.012)
    return flat(f, size)


def f_ceiling_tiles(c=(228, 226, 220), seed=101, size=64, t=32):
    """Suspended ceiling tiles in an aluminium T-bar grid, fissured."""
    def f(x, y):
        if x % t == 0 or y % t == 0:
            return shade(ALU, 0.95)
        if x % t == 1 or y % t == 1:
            return shade(c, 0.86)
        if h32(x, y, seed) < 0.07:
            return shade(c, 0.9)
        return jit(c, x // 2, y // 2, seed + 1, 0.008)
    return flat(f, size)


def f_laminate(c=LAM, seed=102):
    return flat(lambda x, y: shade(ALU, 1.1) if x % 64 in (0, 63) else jit(c, x // 2, y // 2, seed, 0.012))


def f_noise(c, amt, seed, scale=1):
    return flat(lambda x, y: jit(c, x // scale, y // scale, seed, amt))


def f_lumps(base, hi, seed, size, glint=None):
    fn = lumps(base, hi, seed, size, glint)
    return flat(lambda x, y: fn(x, y))


def f_tarmac():
    """The coal yard's tarmac: fine dark aggregate, coal dust lying on it."""
    def f(x, y):
        k = h32(x, y, 103)
        col = jit((76, 75, 72), x, y, 104, 0.05)
        if k < 0.08:
            col = shade(col, 1.3)
        d = 0.5 + 0.5 * math.sin(x * 0.098 + 2.2 * math.sin(y * 0.098 * 2)) * math.sin(y * 0.098 + 1)
        return mix(col, (34, 33, 32), 0.45 * d * h32(x // 4, y // 4, 105))
    return flat(f)


def f_slabs(c=(170, 166, 158), s=32, seed=105, joint=0.62):
    """Concrete slabs: sealed joints, each slab its own tone."""
    n = 64 // s

    def f(x, y):
        if x % s == 0 or y % s == 0:
            return shade(c, joint)
        g = 0.94 + 0.1 * h32((x // s) % n, (y // s) % n, seed)
        return jit(shade(c, g), x // 2, y // 2, seed + 1, 0.03)
    return flat(f)


def f_drains():
    def f(x, y):
        if 28 <= x < 36:
            if x in (28, 35):
                return (110, 110, 106)
            return (40, 40, 38) if y % 4 else (128, 128, 124)
        if y % 64 == 0 or x % 64 == 0:
            return (124, 122, 116)
        return jit((166, 162, 154), x // 2, y // 2, 106, 0.04)
    return flat(f)


def f_screed():
    """The boiler house floor: grey screed, saw-cut joints every 64, faint stains."""
    def f(x, y):
        if x % 64 == 0 or y % 64 == 0:
            return (100, 98, 94)
        col = jit((140, 138, 132), x // 2, y // 2, 107, 0.035)
        if h32(x // 8, y // 8, 108) < 0.12:
            col = shade(col, 0.93)
        return col
    return flat(f)


def f_chequer(c=GALV):
    """Galvanised chequer plate: raised bars in alternating directions, low contrast."""
    def f(x, y):
        u, v = x % 8, y % 8
        up = (x // 8 + y // 8) % 2
        on = (u, v) in ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5)) if up else (u, 6 - v) in ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
        if on:
            return shade(c, 1.18)
        return jit(shade(c, 0.9), x // 2, y // 2, 109, 0.04)
    return flat(f)


def f_grating():
    def f(x, y):
        if x % 8 in (0, 1) or y % 4 == 0:
            return shade(GALV, 0.8 if x % 8 == 0 or y % 4 == 0 else 1.08)
        return (58, 58, 56)
    return flat(f)


def f_boiler_top():
    """A boiler's top: pale sheet in panels, a hatch with a handle."""
    lag = (214, 212, 204)

    def f(x, y):
        if 44 <= x < 84 and 44 <= y < 84:
            if x in (44, 83) or y in (44, 83):
                return (90, 90, 86)
            if x in (45, 82) or y in (45, 82):
                return shade(GREY, 1.2)
            if 60 <= x < 68 and y in (62, 63, 64, 65):
                return (50, 50, 48)
            return jit(GREY, x // 2, y // 2, 110, 0.02)
        if x % 64 == 0 or y % 32 == 0:
            return shade(lag, 0.8)
        return jit(lag, x // 3, y // 3, 111, 0.012)
    return flat(f, 128)


def f_concrete(c=(152, 150, 144), seed=130, joint=64):
    def f(x, y):
        if x % joint == 0 or y % joint == 0:
            return shade(c, 0.78)
        k = jit(c, x // 2, y // 2, seed, 0.04)
        if h32(x, y, seed + 1) < 0.03:
            k = shade(k, 0.9)
        return k
    return flat(f)


def f_soffit(c=(150, 147, 140), seed=114):
    """A board-marked concrete soffit: the boards along x."""
    def f(x, y):
        if y % 6 == 0:
            return shade(c, 0.85)
        k = h32(0, y // 6, seed)
        return jit(shade(c, 0.94 + 0.1 * k + (h32(x // 7, y // 6, seed + 1) - 0.5) * 0.05), x // 2, y, seed + 2, 0.02)
    return flat(f)


def f_pump_top():
    """A pump's lid: pale grey, bolted round its rim."""
    c = (196, 196, 190)

    def f(x, y):
        d = math.hypot(x - 64 + 0.5, y - 64 + 0.5)
        if d < 26:
            if d > 23:
                return shade(c, 0.6)
            return jit(shade(c, 0.95), x, y, 117, 0.02)
        if abs(d - 30) < 2 and int(math.degrees(math.atan2(y - 64, x - 64)) + 360) % 30 < 10:
            return shade(c, 1.2)
        return jit(c, x // 2, y // 2, 118, 0.015)
    return flat(f, 128)


def f_alu_top():
    """A pipe's aluminium cladding seen from above: sheets, a band every 64."""
    return flat(lambda x, y: shade(ALU, 0.8 if x % 64 < 3 else 1.0) if x % 64 < 3 else
                jit(shade(ALU, 0.98 + 0.06 * math.sin(y / 64 * math.pi)), x // 3, y, 119, 0.015))


def f_studded(base=(192, 190, 184), seed=120, size=128, tile=64, joint=0.7, contrast=0.05):
    """Studded tile in large squares: round studs on an 8 grid, thin dark joints, quiet."""
    def f(x, y):
        if x % tile == 0 or y % tile == 0:
            return shade(base, joint)
        u, v = x % 8 - 4, y % 8 - 4
        d = u * u + v * v
        if d <= 4:
            return shade(base, 1 + contrast if u + v < 0 else 1 - contrast)
        return jit(base, x // 2, y // 2, seed, 0.012)
    return flat(f, size)


def f_roof():
    """R's roof from below: grey steel decking with troughs along x, a beam along y every 128, strip lights."""
    deck = (150, 150, 146)

    def f(x, y):
        if 60 <= x <= 67:
            return shade(GREY, 0.6 if x in (60, 67) else 0.9)
        if 30 <= x < 34 and 8 <= y % 64 < 56:
            return (252, 248, 236) if x in (31, 32) else (200, 198, 190)
        if 94 <= x < 98 and 8 <= (y + 32) % 64 < 56:
            return (252, 248, 236) if x in (95, 96) else (200, 198, 190)
        v = y % 8
        return jit(shade(deck, (0.75, 0.92, 1.05, 1.08, 1.05, 0.92, 0.85, 0.8)[v]), x // 4, y, 121, 0.015)
    return flat(f, 128)


def f_casing_top():
    c = (198, 198, 194)

    def f(x, y):
        if y % 64 in (31, 32):
            return shade(c, 0.6 if y % 64 == 31 else 1.15)
        if y % 64 in (27, 36) and x % 8 == 4:
            return shade(c, 0.7)
        return jit(c, x // 2, y // 4, 122, 0.015)
    return flat(f)


def f_steel_plate(c=(124, 124, 120), seed=123):
    """Steel plate: welded seams, countersunk bolts."""
    def f(x, y):
        u, v = x % 64, y % 32
        if u == 0 or v == 0:
            return shade(c, 0.7)
        if u == 1 or v == 1:
            return shade(c, 1.12)
        if u in (4, 60) and v in (4, 28):
            return shade(c, 0.75)
        return jit(c, x // 2, y // 2, seed, 0.03)
    return flat(f)


def f_sealed_concrete():
    """The workshop's floor: sealed concrete, grey, a little sheen, saw-cut joints."""
    def f(x, y):
        if x % 64 == 0 or y % 64 == 0:
            return (110, 108, 104)
        col = jit((148, 146, 140), x // 3, y // 3, 124, 0.03)
        s = math.sin((x + y) * 0.05) * math.sin((x - y) * 0.07)
        return shade(col, 1 + 0.03 * s)
    return flat(f)


def f_lathe_top():
    def f(x, y):
        v = y % 64
        if 20 <= v < 26 or 38 <= v < 44:
            return (186, 186, 182) if v in (20, 38) else (150, 150, 146)
        return jit((118, 118, 114), x // 2, y // 2, 126, 0.02)
    return flat(f)


def f_deck():
    """A roof from below: profiled steel decking with troughs along x, a grey purlin along x."""
    deck = (176, 176, 172)

    def f(x, y):
        if 26 <= y <= 37:
            return shade(GREY, 0.55 if y in (26, 37) else 1.15 if y in (27, 36) else 0.95)
        v = x % 8
        return jit(shade(deck, (0.75, 0.92, 1.05, 1.08, 1.05, 0.92, 0.85, 0.8)[v]), x, y // 4, 128, 0.015)
    return flat(f)


def f_cables(along_x):
    """Cables on a galvanised tray seen from under it: black cables, the tray's rungs across them."""
    def f(x, y):
        u, v = (x, y) if along_x else (y, x)
        if u % 16 in (0, 1):
            return shade(GALV, 0.8 if u % 16 else 1.1)
        k = v % 6
        if k == 0:
            return (70, 70, 66)
        g = (0.0, 0.7, 1.4, 1.6, 1.1, 0.6)[k]
        return jit(shade((26, 26, 26), g), u // 8, v, 129, 0.05)
    return flat(f)


def f_trans_top():
    def f(x, y):
        for cx in (16, 48):
            d = math.hypot(x - cx + 0.5, y - 32 + 0.5)
            if d < 9:
                return (230, 228, 222) if d < 4 else (180, 178, 172) if d < 7 else (60, 60, 58)
        if x % 64 in (0, 63) or y % 64 in (0, 63):
            return (78, 78, 76)
        return jit((128, 128, 124), x // 2, y // 2, 131, 0.02)
    return flat(f)


def f_dry_grass():
    def f(x, y):
        k = h32(x, y, 132)
        base = mix((166, 148, 108), (190, 174, 132), h32(x // 3, y // 5, 133))
        if k < 0.2:
            return shade(base, 1.15)
        if k > 0.82:
            return mix(base, (104, 88, 66), 0.55)
        return jit(base, x, y, 134, 0.05)
    return flat(f)


def f_wet_concrete():
    def f(x, y):
        c = jit((132, 130, 124), x // 2, y // 2, 135, 0.05)
        if y % 32 in (15, 16):
            return (70, 70, 66)
        s = 0.5 + 0.5 * math.sin(x * 0.11 + 2 * math.sin(y * 0.07))
        return mix(c, (84, 82, 78), 0.4 * s * h32(x // 6, y // 6, 136))
    return flat(f)


def f_grey_top(c=(124, 124, 120), rim=3, seed=142):
    return flat(lambda x, y: shade(c, 1.25) if x % 64 < rim or y % 64 < rim else jit(c, x // 2, y // 2, seed, 0.015))


def f_rubber():
    """The stands: black studded rubber."""
    base = (44, 44, 43)

    def f(x, y):
        u, v = x % 8 - 4, y % 8 - 4
        d = u * u + v * v
        if d <= 5:
            return shade(base, 1.45 if u + v < 0 else 1.12)
        return jit(base, x // 2, y // 2, 153, 0.03)
    return flat(f)


def f_acoustic():
    """L's ceiling: acoustic tiles, 32 square, in an aluminium grid, pinholes."""
    c = (230, 228, 222)

    def f(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return shade(ALU, 0.95)
        if x % 4 == 2 and y % 4 == 2:
            return shade(c, 0.88)
        return jit(c, x // 2, y // 2, 140, 0.008)
    return flat(f, 128)


FLATS = dict(
    TZ=lambda: f_vinyl(), PK=lambda: f_ceiling_tiles(), TK=lambda: f_laminate(),
    CN=f_tarmac, CL=lambda: f_lumps((36, 35, 34), (140, 138, 134), 146, 6, (204, 202, 196)),
    ER=lambda: f_lumps((86, 72, 58), (124, 112, 98), 147, 5), ST=lambda: f_slabs((166, 162, 154), 64, 103, 0.5),
    SB=lambda: f_slabs(), CD=f_drains, GV=lambda: flat(gravel(148)),
    BP=f_screed, CQ=lambda: f_chequer(), GR=f_grating, BT=f_boiler_top, AS=lambda: f_concrete((138, 136, 130), 112),
    BV=lambda: f_soffit(), QT=lambda: f_vinyl((170, 168, 162), 32, 115), PT=f_pump_top, LG=f_alu_top,
    TT=lambda: f_studded(), RG=f_roof, CS=f_casing_top, SP=lambda: f_steel_plate(), WB=f_sealed_concrete,
    BB=lambda: f_laminate((176, 176, 170), 149), LT=f_lathe_top, KB=f_deck, DP=lambda: f_steel_plate((112, 112, 108), 150),
    CA=lambda: f_cables(True), CB=lambda: f_cables(False), CF=lambda: f_concrete(),
    KC=lambda: f_soffit((144, 142, 136), 151), TO=f_trans_top, PN=lambda: f_concrete((178, 174, 166), 152),
    DG=f_dry_grass, WC=f_wet_concrete, LI=lambda: f_vinyl((172, 170, 164), 32, 137),
    RT=lambda: f_grey_top((132, 132, 128), 2, 142), MC=lambda: f_vinyl((206, 204, 198), 64, 138, 0.9, 0.06, 128),
    KF=f_acoustic, TS=f_rubber, SC=lambda: f_grey_top(ENAMEL, 3, 143), KS=lambda: f_slabs((170, 166, 158), 64, 154),
    TB=lambda: f_concrete((166, 162, 154), 155, 16))


# === the sky ==================================================================================================
def sky():
    """A flat white overcast, very faint structure (no blue: the doors are BLUE)."""
    W, H = 1024, 256
    im = Img(W, H)
    for y in range(H):
        t = y / (H - 1)
        base = mix((222, 222, 218), (238, 237, 232), t ** 1.4)
        for x in range(W):
            u = x / W * 2 * math.pi
            c = math.sin(2 * u + y / 41.0 + 1.3 * math.sin(3 * u)) + 0.6 * math.sin(5 * u - y / 23.0)
            col = shade(base, 1 + 0.018 * c)
            im.px[y * W + x] = [col[0], col[1], col[2], 255]
    return im
