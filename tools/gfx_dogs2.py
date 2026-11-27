"""MAP23's look 2, "Menagerie" (exhibits; an old zoological garden's house): art only, the slots of
tools/gfx_dogs.py (read its docstring first; tools/gfx_dogs1.py is the model this file follows).

THEN: red-brown brick in English bond with a cream rendered band and a cream coping, dark green ironwork. The
runs dressed as enclosures: mock rock in pale concrete to 96, a painted sky above it (a far painted hill, a few
clouds), a glazed roof light, sand underfoot. The pens: plain brick limewashed to shoulder height, straw over stone
setts. The keepers' passages: plain brick with a dark green dado line, red quarry tile. Gates of iron plate painted
dark green with a row of drawn bars and rivets; hatch surrounds of dark green iron. The yard: the brick front with
a drawn arch over the door (the house's board), gravel, the shelter of green-painted timber with a cream fascia.
The hall: brick to a cream dado cap, cream render above, tiles of octagon and dot. Lettering: painted boards, cream
letters on dark green, a thin cream border; the runs' name boards are species boards (a silhouette, the species,
its Latin name, the animals' names, DO NOT FEED).
NOW: ivy over the brick from the top and in places from the ground, the painted sky flaking to the render, the rock
stained and cracked, the boards sun-bleached with their letters half gone, the sand gone to dirt and weeds, the
gates rusting through the green; drawn a little lighter than it would be, to read at light 120.
"""
import math
from functools import lru_cache

from gfx_dogs import (RUNS, Img, arrow, chips, draw_plan, flat, h32, mix, rust_run, shade, sprite_img,
                      text_width, write_lines)

# --- the palette ------------------------------------------------------------------------------------------------
BRICK = (156, 74, 52)
BRICKD = (104, 50, 40)            # the plinth's dark brick
MORTAR = (196, 184, 160)
CREAM = (232, 218, 176)           # render, the band, the coping
CREAMD = (196, 180, 140)
GREEN = (50, 96, 64)              # the ironwork's and the boards' paint
GREENL = (78, 130, 90)
GREEND = (26, 54, 36)
SKY = (124, 178, 216)             # the painted sky (upper)
SKYH = (200, 224, 234)            # its horizon
HILL = (130, 156, 120)
CLOUD = (246, 246, 240)
ROCK = (204, 196, 178)            # the mock rock's concrete
ROCKD = (128, 120, 106)
LIME = (234, 228, 210)            # limewash
RENDER = (196, 188, 166)          # under the painted sky
SAND = (214, 188, 138)
DIRT = (128, 104, 76)
QUARRY = (166, 72, 50)
STRAW = (206, 178, 96)
SETT = (128, 126, 118)
RUST = (138, 74, 40)
IRON = (88, 90, 92)
IVY = (64, 110, 52)
IVYL = (108, 156, 76)
IVYD = (36, 66, 34)
WOOD = (150, 108, 66)
LETTER = (240, 230, 190)          # the boards' letters (exactly this colour, so that NOW can wear them)
BORDER = (224, 210, 166)
NIGHT = (22, 26, 40)


def jt(c, x, z, s, a):
    return shade(c, 1 + (h32(x, z, s) - 0.5) * 2 * a)


def smooth(t):
    return t * t * (3 - 2 * t)


def vn(x, z, sc, s, per=64):
    """Smooth value noise in [0, 1), periodic in x with `per` (a multiple of sc)."""
    n = max(1, per // sc)
    gx, gz = x / sc, z / sc
    i, j = math.floor(gx), math.floor(gz)
    fx, fz = smooth(gx - i), smooth(gz - j)
    a, b = h32(i % n, j, s), h32((i + 1) % n, j, s)
    c, d = h32(i % n, j + 1, s), h32((i + 1) % n, j + 1, s)
    return (a + (b - a) * fx) * (1 - fz) + (c + (d - c) * fx) * fz


def vn2(x, y, sc, s, per=64):
    """Smooth value noise periodic in both x and y (flats)."""
    n = max(1, per // sc)
    gx, gy = x / sc, y / sc
    i, j = math.floor(gx), math.floor(gy)
    fx, fy = smooth(gx - i), smooth(gy - j)
    a, b = h32(i % n, j % n, s), h32((i + 1) % n, j % n, s)
    c, d = h32(i % n, (j + 1) % n, s), h32((i + 1) % n, (j + 1) % n, s)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def lift(c, f=0.12):
    """NOW: a little lighter than it would be, to read at light 120."""
    return mix(c, (226, 220, 206), f)


# --- what forty years do (NOW) ------------------------------------------------------------------------------
def ivy(x, z, top, s, reach=70, ground=0):
    """NOW: ivy hanging from the height `top` in tongues (and, `ground` > 0, rising from the floor in a few
    places): a leaf's colour, a stem's, or None (the wall shows)."""
    p = 0.0
    depth = top - z
    ln = reach * (0.2 + 1.0 * vn(x, 0, 16, s))
    if depth <= 0:
        p = 0.8
    elif depth < ln:
        p = 0.8 * (1 - depth / ln) ** 0.8
    if ground:
        g = ground * max(0.0, vn(x, 0, 32, s + 5) - 0.42) * 2.4
        if z < g:
            p = max(p, 0.75 * (1 - z / g) ** 0.6)
    if p <= 0.02:
        return None
    cx, cz = x // 4, z // 4
    if h32(cx % 16, cz, s + 1) < p:
        ox, oz = 1 + h32(cx % 16, cz, s + 2) * 1.4, 1 + h32(cx % 16, cz, s + 3) * 1.4
        dx, dz = x % 4, z % 4
        d = abs(dx - ox) + abs(dz - oz)
        if d <= 2.1:
            k = h32(cx % 16, cz, s + 4)
            base = IVY if k < 0.6 else (IVYD if k < 0.8 else IVYL)
            return shade(base, 1.18 if dz > oz else (0.85 if d > 1.4 else 1.0))
    if p > 0.25 and (x + int(3 * math.sin(z * 0.21 + s))) % 16 == s % 16:
        return (86, 70, 46)                                       # a stem
    return None


def grime(c, x, z, then, top=24, s=7, col=(70, 58, 44)):
    """NOW: dirt from the floor up, ragged."""
    if then:
        return c
    lim = top * (0.45 + 0.55 * vn(x, 0, 8, s) + 0.25 * h32(x // 2 % 32, 0, s + 1))
    if z <= lim:
        return mix(c, col, 0.15 + 0.45 * (1 - z / max(lim, 1)))
    return c


# --- brick ----------------------------------------------------------------------------------------------------
def brick_at(x, z, s=3, base=BRICK):
    """English bond by absolute height: a course of stretchers (32) and one of headers (16), 8 high."""
    row = (z - 1) // 8
    dz = (z - 1) % 8
    bw, off = (32, 0) if row % 2 == 0 else (16, 8)
    bx = (x + off) % bw
    if dz == 0 or bx == 0:
        return jt(MORTAR, x, z, s, 0.05)
    k = ((x + off) // bw) % (64 // bw)
    r = h32(k, row, s)
    c = base
    if r < 0.18:
        c = mix(base, (112, 50, 38), 0.6)
    elif r > 0.84:
        c = mix(base, (188, 104, 66), 0.5)
    c = jt(c, k, row, s + 1, 0.06)
    c = jt(c, x, z, s + 2, 0.035)
    if dz == 7:
        c = shade(c, 1.08)
    elif dz == 1 or bx == bw - 1:
        c = shade(c, 0.88)
    return c


def brick_now(x, z, s=3, base=BRICK):
    """NOW: the brick weathered, a little efflorescence, lighter to read at 120."""
    c = brick_at(x, z, s, base)
    if vn(x, z, 8, s + 9) > 0.8:
        c = mix(c, (214, 206, 190), 0.22)                         # salts
    return lift(c, 0.1)


def brick(x, z, then, s=3, base=BRICK):
    return brick_at(x, z, s, base) if then else brick_now(x, z, s, base)


def render(x, z, then, s, col=CREAM):
    """Cream render (smooth, faint trowel marks); NOW stained and cracked."""
    c = jt(col, x // 2, z // 2, s, 0.02)
    if then:
        return c
    c = mix(c, (150, 140, 112), 0.3 * vn(x, z, 8, s + 1))
    if abs(vn(x, z, 16, s + 2) - 0.5) < 0.015:
        c = shade(c, 0.6)                                         # a crack
    return lift(c, 0.06)


# === walls =====================================================================================================
@lru_cache(maxsize=None)
def yard_px(x, z, then, front):
    """The yard's brick: a dark plinth 0..12, a cream band 196..212, (the front) a dentil course 228..236, the
    cream coping 244..256; NOW grime, the band stained, ivy from the top and the ground."""
    if not then:
        v = ivy(x, z, 256, 61 if front else 63, 110, 96)
        if v:
            return v
    if z > 244:
        c = render(x, z, then, 71)
        if z <= 246:
            c = shade(c, 0.7)
        return c
    if 196 < z <= 212:
        c = render(x, z, then, 72)
        if z == 212:
            c = shade(c, 1.06)
        elif z <= 198:
            c = shade(c, 0.72)                                    # its shadow
        return c
    if front and 228 < z <= 236:
        if (x % 16) < 8:
            return shade(brick(x, z, then, 73), 1.1 if z > 233 else 0.95)
        return shade(brick(x, z, then, 73), 0.55)                # between the dentils
    if z <= 12:
        c = brick(x, z, then, 74, BRICKD)
    else:
        c = brick(x, z, then, 75)
    return grime(c, x, z, then, 30, 76)


def yard_front(w, then):
    """The house's front: brick, the cream band and coping, a dentil course under the coping."""
    w.fill(w.z0, w.bot, lambda x, z: yard_px(x, z, then, True))


def yard_wall(w, then):
    """The yard's other walls: the same brick and bands (no dentils)."""
    w.fill(w.z0, w.bot, lambda x, z: yard_px(x, z, then, False))


@lru_cache(maxsize=None)
def shelter_px(x, z, then):
    """The shelter: a dark green drip (112..118), a green fascia board (118..136), green boarding over it with
    a cream fascia (164..222) for its plate, a cream eaves board at 244."""
    def paintg(c, s):
        if then:
            return c
        c = mix(c, (150, 146, 128), 0.35 + 0.25 * vn(x, z, 8, s))
        if vn(x, z, 8, s + 1) > 0.76:
            c = jt((150, 132, 104), x, z, s + 2, 0.05)            # the paint gone to the grey wood
        return lift(c, 0.1)
    if z <= 118:
        return paintg(shade(GREEND, 1.1), 81)
    if z <= 136:
        c = jt(GREEN, x // 4, z, 82, 0.03)
        if z in (119, 136):
            c = shade(c, 0.7)
        return paintg(c, 83)
    if 164 < z <= 222 or 244 < z <= 250:
        c = jt(CREAM, x // 3, z, 84, 0.02)
        if z in (165, 222, 245, 250):
            c = shade(c, 0.75)
        return paintg(c, 85)
    c = jt(GREEN, x // 8, 0, 86, 0.05)
    c = jt(c, x, z // 3, 87, 0.03)
    if x % 8 == 0:
        c = shade(c, 0.6)                                         # the boards' joints
    elif x % 8 == 1:
        c = shade(c, 1.15)
    if not then:
        v = ivy(x, z, 256, 88, 50)
        if v:
            return v
    return paintg(c, 89)


def shelter_mass(w, then):
    w.fill(w.z0, w.bot, lambda x, z: shelter_px(x, z, then))


@lru_cache(maxsize=None)
def sill_px(x, z, then):
    if z <= 8:
        c = jt(CREAM, x, z, 91, 0.03)
        if z == 8:
            c = shade(c, 1.06)
        elif z <= 2:
            c = shade(c, 0.8)
        return c if then else lift(mix(c, (130, 120, 96), 0.35 * vn(x, z, 8, 92)), 0.05)
    if z <= 148:
        c = jt(GREEN, x // 3, z, 93, 0.03)
        if z % 6 == 0:
            c = shade(c, 1.2)
        if z in (137, 148):
            c = shade(c, 0.6)
        return c if then else lift(mix(c, RUST, 0.45 * vn(x, z, 8, 94) + 0.15), 0.1)
    return yard_px(x, z, then, False)


def sill(w, then):
    """A cream stone sill (0..8), a dark green iron head (136..148), the yard's brick over it."""
    w.fill(w.z0, w.bot, lambda x, z: sill_px(x, z, then))


def iron(x, z, then, s, base=GREEN):
    """Iron painted dark green; NOW rusting through the green."""
    c = jt(base, x // 2, z // 3, s, 0.04)
    if then:
        return c
    r = vn(x, z, 8, s + 1) * 0.7 + h32(x // 2, z // 2, s + 2) * 0.3
    c = mix(lift(c, 0.12), RUST, max(0.0, r - 0.3) * 1.5)
    if r > 0.86:
        c = (54, 36, 26)                                          # rusted through
    return c


@lru_cache(maxsize=None)
def gateway_px(x, z, then):
    if z > 184:
        return yard_px(x, z, then, False)
    if z > 176:
        c = render(x, z, then, 101)                               # the cream lintel
        return shade(c, 0.75) if z == 177 else c
    if z > 168 or z <= 6 or 76 < z <= 84:
        c = iron(x, z, then, 102)
        return shade(c, 1.15 if z in (176, 84) else 0.95)        # the rails
    if z <= 76:
        c = iron(x, z, then, 103)
        if x % 32 in (0, 1):
            c = shade(c, 0.75)
        return c
    # the bars, with the dark of the run behind them
    bx = x % 8
    if bx in (3, 4, 5):
        c = iron(x, z, then, 104, GREENL)
        return shade(c, 1.2 if bx == 3 else (0.8 if bx == 5 else 1.0))
    return jt((44, 48, 44), x, z, 105, 0.05)


def gateway(w, then):
    """The big run's gateway THEN, shut: a gate of dark green iron, plate to 76, bars to 168, a cream lintel."""
    w.fill(w.z0, w.bot, lambda x, z: gateway_px(x, z, then))
    for c in range(w.w):
        if (w.shift + c) % 8 == 4:
            for zz in (3, 80, 172):
                w.disc(c + 0.5, zz, 1.1, shade(GREENL, 1.3))


def house_door(w, then):
    """The front door THEN (64 x 128): a pair of dark green panelled leaves, a fanlight, iron rings."""
    w.rect(0, 128, 64, 0, shade(CREAM, 0.85))                        # the cream architrave
    w.rect(3, 125, 61, 0, GREEND)
    w.rect(5, 123, 59, 100, (40, 56, 60))                            # the fanlight
    for c in range(9, 59, 8):
        w.rect(c, 123, c + 1, 100, CREAM)
    w.rect(5, 101, 59, 98, CREAM)
    for k, (c1, c2) in enumerate(((5, 31), (33, 59))):
        w.rect(c1, 98, c2, 0, GREEN)
        for z in range(0, 98):
            for c in range(c1, c2):
                if h32(c, z // 3, 111 + k) < 0.06:
                    w.at(c, z, shade(GREEN, 1.07))
        for (zt, zb) in ((92, 52), (46, 8)):                         # raised panels
            w.rect(c1 + 4, zt, c2 - 4, zb, shade(GREEN, 1.12))
            w.frame(c1 + 4, zt, c2 - 4, zb, shade(GREEN, 0.7), 1)
            w.rect(c1 + 5, zt - 1, c2 - 5, zt - 2, shade(GREEN, 1.3))
    w.rect(31, 98, 33, 0, GREEND)
    for cx in (27, 37):
        w.ring(cx + 0.5, 56, 1.5, 3, (30, 30, 30))                   # iron rings
    w.rect(5, 3, 59, 0, shade(GREEND, 0.8))


@lru_cache(maxsize=None)
def hall_px(x, z):
    """The hall (NOW only): brick to 80 over a green glazed skirting, a cream dado cap, cream render above with
    a cornice at 176; NOW the render flaking to the brick, ivy from the top."""
    v = ivy(x, z, 192, 41, 80, 40)
    if v:
        return v
    if z <= 10:
        c = jt(GREENL, x // 8, z, 42, 0.04)
        c = shade(c, 1.15 if z == 10 else (0.7 if x % 8 == 0 else 1.0))
        return lift(grime(c, x, z, False, 12, 43), 0.12)
    if z <= 76:
        return grime(brick_now(x, z, 44), x, z, False, 30, 45)
    if z <= 82:
        c = jt(CREAM, x, z, 46, 0.02)
        c = shade(c, 1.1 if z == 82 else (0.7 if z == 77 else 1.0))
        return lift(mix(c, (130, 116, 90), 0.3 * vn(x, z, 8, 47)), 0.05)
    if vn(x, z, 12, 48) > 0.66:
        return brick_now(x, z, 49)                                    # the render gone to the brick
    if vn(x, z, 12, 48) > 0.63:
        return (150, 138, 114)                                        # its broken edge
    c = render(x, z, False, 50)
    if 174 <= z <= 178:
        c = shade(c, 0.8 if z in (174, 178) else 1.08)
    return c


def hall_wall(w, then):
    w.fill(w.z0, w.bot, lambda x, z: hall_px(x, z))


# --- the runs: mock rock and a painted sky ----------------------------------------------------------------------
def rock_top(x):
    return 96 + int(round(2.4 * (vn(x, 0, 16, 301) - 0.5) * 2))


def cloud(x, z):
    """The painted clouds: brightness 0..1 (one big cloud and one small in every 64)."""
    v = 0.0
    for cx, cz, rx, rz in ((14, 140, 13, 6), (24, 145, 9, 6), (6, 143, 7, 4), (44, 124, 7, 3), (50, 127, 5, 3)):
        dx = ((x - cx + 32) % 64) - 32
        d = (dx / rx) ** 2 + ((z - cz) / rz) ** 2
        if d < 1:
            v = max(v, 1 - d)
    return v


@lru_cache(maxsize=None)
def rock_px(x, z, then):
    """The mock rock: boulders of pale concrete (a jittered grid, each lit from above left), the joints dark."""
    s = 311
    best, second, cell = 1e9, 1e9, None
    gx, gz = x // 16, z // 12
    for i in (gx - 1, gx, gx + 1):
        for j in (gz - 1, gz, gz + 1):
            px = i * 16 + 3 + h32(i % 4, j, s) * 10
            pz = j * 12 + 2 + h32(i % 4, j, s + 1) * 8
            d = math.hypot((x - px) * 0.9, z - pz)
            if d < best:
                best, second, cell = d, best, (i, j, px, pz)
            elif d < second:
                second = d
    i, j, px, pz = cell
    lit = 0.82 + 0.03 * (z - pz) - 0.018 * (x - px) - 0.006 * best
    c = jt(ROCK, i % 4, j, s + 2, 0.05)
    c = shade(c, max(0.65, min(1.18, lit)))
    c = jt(c, x, z, s + 3, 0.04)
    if second - best < 1.6:
        c = mix(c, ROCKD, 0.75)                                       # the joints
    elif second - best < 2.6:
        c = shade(c, 0.9)
    if then:
        return c
    st = vn(x, 0, 4, s + 4)                                           # stains running down from the top
    c = mix(c, (112, 98, 70), 0.45 * max(0.0, st - 0.4) * (0.3 + z / 96))
    c = mix(c, (92, 104, 70), 0.4 * max(0.0, 1 - z / 20) * vn(x, z, 8, s + 5))     # moss at its foot
    if abs(vn(x, z, 16, s + 6) - 0.5) < 0.007:
        c = (92, 84, 72)                                              # a crack
    return lift(c, 0.1)


@lru_cache(maxsize=None)
def sky_px(x, z, then):
    """The painted sky over the rock: light at the horizon, a far hill, clouds; NOW faded and flaking."""
    t = max(0.0, min(1.0, (z - 96) / 80))
    c = mix(SKYH, SKY, t ** 0.8)
    hz = 104 + 5 * math.sin(2 * math.pi * x / 64) + 3 * math.sin(4 * math.pi * x / 64 + 1)
    if z <= hz:
        c = mix(HILL, SKYH, 0.25 * (z - 96) / 14)
        if z >= hz - 1:
            c = shade(c, 1.08)
    else:
        k = cloud(x, z)
        if k > 0:
            cl = CLOUD if z > 136 or k > 0.5 else (214, 224, 232)
            c = mix(c, cl, min(1.0, k * 2.2))
    c = jt(c, x // 2, z // 2, 321, 0.012)                             # the brush
    if then:
        return c
    c = mix(c, (176, 180, 172), 0.3)                                  # faded
    f = vn(x, z, 10, 322)
    if f > 0.64:
        return jt(RENDER, x, z, 323, 0.04)                            # flaked to the render
    if f > 0.61:
        return (110, 116, 120)                                        # the paint's edge
    c = mix(c, (130, 120, 98), 0.35 * max(0.0, vn(x, 0, 4, 324) - 0.5) * (1.5 - z / 192))   # water stains
    return lift(c, 0.06)


@lru_cache(maxsize=None)
def runs_px(x, z, then):
    if not then:
        v = ivy(x, z, 160, 331, 44)
        if v:
            return v
    top = rock_top(x)
    if z <= 4:
        return grime(jt(ROCKD, x, z, 332, 0.06), x, z, then, 6, 333, (60, 50, 40))
    if z <= top:
        c = rock_px(x, z, then)
        if z >= top - 1:
            c = shade(c, 1.12)                                        # the rock's lit lip
        return c
    if z <= top + 2:
        return shade(sky_px(x, z, then), 0.78)                        # its shadow on the sky
    return sky_px(x, z, then)


def runs_wall(w, then):
    """Mock rock to 96, the painted sky above (0..160, the big run 0..192)."""
    w.fill(w.z0, w.bot, lambda x, z: runs_px(x, z, then))


# --- the pens --------------------------------------------------------------------------------------------------
def lime_top(x):
    return 64 + int(3 * vn(x, 0, 8, 341)) + (1 if h32(x, 0, 342) < 0.3 else 0)


@lru_cache(maxsize=None)
def pens_px(x, z, then):
    """Plain brick, limewashed from 6 to 64 (a brushed edge), a dark green skirting; NOW flaking, ivy."""
    if not then:
        v = ivy(x, z, 128, 351, 46)
        if v:
            return v
    if z <= 6:
        c = jt(GREEND, x, z, 352, 0.06)
        c = shade(c, 1.4) if z == 6 else c
        return grime(c, x, z, then, 10, 353) if then else lift(grime(c, x, z, then, 10, 353), 0.15)
    b = brick_at(x, z, 354)
    if z <= lime_top(x):
        lw = mix(b, LIME, 0.86)
        lw = jt(lw, x, z // 2, 355, 0.02)
        if then:
            return lw
        f = vn(x, z, 8, 356)
        if f > 0.6:
            return lift(b, 0.1)                                       # the wash gone to the brick
        lw = mix(lw, (150, 138, 112), 0.25 * vn(x, z, 6, 357))
        return grime(lw, x, z, then, 34, 358)
    return brick(x, z, then, 354)


def pens_wall(w, then):
    w.fill(w.z0, w.bot, lambda x, z: pens_px(x, z, then))


def ledge_face(w, then):
    """NOW: the pen's wall from its lowest 48 rows, broken off at the top (raw brick and mortar)."""
    pens_wall(w, then)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        top = 38 + int(10 * vn(xw, 1, 8, 361))
        for z in range(top, 49):
            w.at(c, z, lift(brick_at(xw, z, 362), 0.1) if h32(xw, z, 363) < 0.8 else MORTAR)
        w.at(c, top, shade(MORTAR, 0.7))


@lru_cache(maxsize=None)
def leaf_px(x, z, then):
    """A gate's leaf: dark green plate, rails at 4..10, 92..98 and 180..186 with rivets, a row of drawn flat
    bars between 104 and 176; NOW rusting through."""
    s = 371
    rail = 4 < z <= 10 or 92 < z <= 98 or 180 < z <= 186
    if rail:
        c = iron(x, z, then, s, GREEN)
        return shade(c, 1.2 if z in (10, 98, 186) else (0.7 if z in (5, 93, 181) else 1.0))
    if 104 < z <= 176:
        bx = x % 8
        if bx in (2, 3, 4):
            c = iron(x, z, then, s + 1, GREENL)
            return shade(c, 1.2 if bx == 2 else (0.85 if bx == 4 else 1.05))
        c = iron(x, z, then, s + 2, shade(GREEN, 0.78))
        return shade(c, 0.7) if bx == 5 else c
    c = iron(x, z, then, s + 3)
    if x % 32 in (0, 1):
        c = shade(c, 0.7 if x % 32 == 0 else 1.15)
    return c


def gate_leaf(w, then):
    w.fill(w.z0, w.bot, lambda x, z: leaf_px(x, z, then))
    for c in range(w.w):
        xw = (w.shift + c) % 64
        if xw % 8 == 6:
            for zz in (7, 95, 183):
                w.disc(c + 0.5, zz, 1.1, shade(GREENL, 1.35) if then else shade(RUST, 0.9))
    if not then:
        for c in range(w.w):
            xw = (w.shift + c) % 64
            if xw % 16 == 6:
                rust_run(w, c, 4 + 88 * (xw // 16 % 2), 14 + 10 * h32(xw, 0, 372), RUST, 0.5, 1)


@lru_cache(maxsize=None)
def reveal_px(x, z, then):
    c = iron(x, z, then, 381, shade(GREEN, 0.9))
    if x % 16 in (6, 7, 8, 9):
        c = shade(c, 0.55)                                            # the groove
    elif x % 16 in (5, 10):
        c = shade(c, 1.2)
    return c if then else grime(c, x, z, then, 26, 382)


def gate_reveal(w, then):
    """A gate's jambs: a dark green iron channel with its groove; NOW rust."""
    w.fill(w.z0, w.bot, lambda x, z: reveal_px(x, z, then))


@lru_cache(maxsize=None)
def hatch_px(x, z, then):
    if z <= 72:
        c = iron(x, z, then, 391)
        if z in (71, 72) or z in (16, 17):
            c = shade(c, 0.6)
        elif z in (70, 18):
            c = shade(c, 1.25)
        return grime(c, x, z, then, 16, 392)
    if not then:
        v = ivy(x, z, 128, 393, 40)
        if v:
            return v
    return brick(x, z, then, 394)


def hatch_surround(w, then):
    """A hatch's surround: a dark green iron plate from the floor to 72 (the hole at 24..56), brick over it."""
    w.fill(w.z0, w.bot, lambda x, z: hatch_px(x, z, then))
    for c in range(w.w):
        if (w.shift + c) % 16 == 8:
            for zz in (66, 21):
                w.disc(c + 0.5, zz, 1.1, shade(GREENL, 1.3) if then else (70, 46, 30))
    if not then:
        for c in range(w.w):
            if (w.shift + c) % 32 == 8:
                rust_run(w, c, 64, 16, RUST, 0.5, 1)


# --- the passages ------------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def passage_px(x, z, then):
    """Plain brick, a dark green skirting (0..6) and a dark green dado line (48..52); NOW grime, salts, ivy."""
    if not then:
        v = ivy(x, z, 128, 401, 30)
        if v:
            return v
    if z <= 6 or 48 < z <= 52:
        c = jt(GREEN, x // 2, z, 402, 0.04)
        if z in (6, 52):
            c = shade(c, 1.3)
        return c if then else lift(grime(mix(c, (110, 110, 96), 0.25), x, z, then, 10, 403), 0.12)
    return grime(brick(x, z, then, 404), x, z, then, 30, 405)


def passage_wall(w, then):
    w.fill(w.z0, w.bot, lambda x, z: passage_px(x, z, then))


@lru_cache(maxsize=None)
def turnstile_px(x, z, then):
    c = shade(GREEN, 0.75 + 0.5 * abs(math.sin(x * 0.3)))
    if z % 24 in (0, 1, 2):
        c = shade(GREENL, 1.1 if z % 24 == 2 else 0.9)                # the post's rings
    if then:
        return c
    c = mix(lift(c, 0.12), RUST, 0.55 * h32(x // 2, z // 4, 411) + 0.2)
    if z > 60 + 20 * vn(x, 0, 8, 412):
        c = mix(c, (66, 56, 46), 0.45)
    return c


def turnstile_jamb(w, then):
    """A turnstile's jamb: a dark green cast iron post with rings; NOW rusted."""
    w.fill(w.z0, w.bot, lambda x, z: turnstile_px(x, z, then))


WALLS = {"YF": yard_front, "YW": yard_wall, "SM": shelter_mass, "SL": sill, "GW": gateway, "HD": house_door,
         "HW": hall_wall, "RW": runs_wall, "PW": pens_wall, "LF": ledge_face, "GL": gate_leaf, "GR": gate_reveal,
         "HS": hatch_surround, "KW": passage_wall, "TS": turnstile_jamb}


# === flats =====================================================================================================
def weeds(x, y, s, n=0.08, size=64):
    """NOW: a tuft of weeds or None."""
    cx, cy = x // 8, y // 8
    if h32(cx % (size // 8), cy % (size // 8), s) < n * 8:
        ox, oy = 2 + h32(cx, cy, s + 1) * 4, 2 + h32(cx, cy, s + 2) * 4
        dx, dy = (x % 8) - ox, (y % 8) - oy
        if dx * dx + dy * dy < 7 and h32(x, y, s + 3) < 0.7:
            return jt((92, 134, 60), x, y, s + 4, 0.2)
    return None


def gravel(then):
    def fn(x, y):
        c = jt((182, 168, 140), x, y, 501, 0.09)
        r = h32(x // 2, y // 2, 502)
        if r < 0.18:
            c = jt((212, 202, 180), x, y, 503, 0.06)
        elif r < 0.3:
            c = jt((132, 118, 96), x, y, 504, 0.08)
        if (x + y) % 2 == 0 and h32(x, y, 505) < 0.2:
            c = shade(c, 0.8)
        if not then:
            c = mix(c, DIRT, 0.35 * vn2(x, y, 16, 506))
            w = weeds(x, y, 507, 0.07)
            if w:
                c = w
            c = lift(c, 0.06)
        return c
    return flat(fn)


def shelter_ceiling(then):
    def fn(x, y):
        c = jt(GREENL, x, y // 8, 511, 0.04)
        if y % 8 == 0:
            c = shade(c, 0.65)
        elif y % 8 == 1:
            c = shade(c, 1.12)
        if x % 32 in (0, 1, 2, 3):
            c = shade(CREAM, 0.9 if x % 32 in (0, 3) else 1.0)       # a cream joist
        if not then:
            c = lift(mix(c, (130, 120, 98), 0.4 * vn2(x, y, 16, 512)), 0.08)
        return c
    return flat(fn)


def sill_top(then):
    return flat(lambda x, y: jt(CREAM, x, y, 521, 0.03) if then
                else lift(mix(jt(CREAM, x, y, 521, 0.06), (128, 116, 90), 0.4 * vn2(x, y, 16, 522)), 0.05))


def hall_floor(then):
    """Octagon and dot: buff octagons 16, small dark green squares where four meet; NOW tiles gone, dirt."""
    def fn(x, y):
        u, v = x % 16, y % 16
        du, dv = min(u, 15 - u), min(v, 15 - v)
        if du + dv < 4:
            c = jt((52, 86, 62), x // 4, y // 4, 531, 0.06)           # the dot
            if du + dv == 3:
                c = (96, 84, 72)
        elif u == 0 or v == 0:
            c = (120, 104, 88)
        else:
            c = jt((214, 190, 146), x // 16, y // 16, 532, 0.05)
            c = jt(c, x, y, 533, 0.03)
            if (x // 16 + y // 16) % 2:
                c = mix(c, QUARRY, 0.55)                              # red and buff by turns
        if not then:
            if h32((x // 16) % 4, (y // 16) % 4, 534) < 0.22:
                c = jt((112, 104, 92), x, y, 535, 0.1)                 # gone to the screed
            c = mix(c, DIRT, 0.3 * vn2(x, y, 16, 536))
            if abs(vn2(x, y, 32, 537) - 0.5) < 0.02:
                c = (50, 44, 38)
            c = lift(c, 0.08)
        return c
    return flat(fn)


def hall_ceiling(then):
    def fn(x, y):
        if x % 32 in (0, 1) or y % 32 in (0, 1):
            c = jt(GREEN, x, y, 541, 0.04)
            return c if then else lift(mix(c, RUST, 0.4), 0.1)
        c = jt(CREAM, x // 2, y // 2, 542, 0.02)
        if then:
            return c
        if h32((x // 32) % 2, (y // 32) % 2, 543) < 0.35 and vn2(x, y, 8, 544) > 0.45:
            return jt(NIGHT, x, y, 545, 0.1)                            # through to the night
        return lift(mix(c, (110, 96, 70), 0.4 * vn2(x, y, 16, 546)), 0.04)
    return flat(fn)


def sand(then):
    """The run's sand, 128: grains, soft ripples, pebbles; NOW gone to dirt with weeds."""
    def fn(x, y):
        rip = math.sin(2 * math.pi * (x + 8 * math.sin(2 * math.pi * y / 128)) / 16)
        c = shade(SAND, 1 + 0.035 * rip)
        c = jt(c, x, y, 551, 0.05)
        c = mix(c, (190, 162, 112), 0.4 * vn2(x, y, 32, 552, 128))
        if h32(x // 2, y // 2, 553) < 0.02:
            c = jt((130, 118, 100), x, y, 554, 0.1)                   # a pebble
        if not then:
            d = vn2(x, y, 16, 555, 128)
            c = mix(c, DIRT, 0.25 + 0.5 * d)
            w = weeds(x, y, 556, 0.06, 128)
            if w:
                c = w
            c = lift(c, 0.08)
        return c
    return flat(fn, 128)


def roof_light(then, seed=561):
    """A glazed roof light: pale glass between dark green bars (every 16 one way, 32 the other); NOW broken
    panes open to the night."""
    def fn(x, y):
        if x % 16 in (0, 1) or y % 32 in (0, 1):
            c = shade(GREEN, 1.1 if (x % 16 == 1 or y % 32 == 1) else 0.85)
            return c if then else lift(mix(c, RUST, 0.45 * vn2(x, y, 16, seed)), 0.1)
        g = mix((214, 232, 238), (176, 206, 222), (y % 32) / 32)
        g = jt(g, x, y, seed + 1, 0.015)
        if then:
            return g
        if h32((x // 16) % 4, (y // 32) % 2, seed + 2) < 0.4:
            return jt(NIGHT, x, y, seed + 3, 0.1)
        return lift(mix(g, (120, 116, 96), 0.5 * vn2(x, y, 8, seed + 4)), 0.02)
    return flat(fn)


def straw(then):
    """Straw over stone setts: grey setts (16 x 8), straw strands over most of it; NOW rotten and dark."""
    def fn(x, y):
        row = y // 8
        bx = (x + (8 if row % 2 else 0)) % 16
        if y % 8 == 0 or bx == 0:
            c = (84, 80, 74)
        else:
            c = jt(SETT, ((x + (8 if row % 2 else 0)) // 16) % 4, row % 8, 571, 0.08)
            c = jt(c, x, y, 572, 0.04)
        if not then:
            c = lift(mix(c, (70, 62, 46), 0.3 * vn2(x, y, 16, 579)), 0.08)
        return c
    im = flat(fn)
    # the straw: short strands every way, thick where the noise says, wrapped round the flat's edges
    n = 260 if then else 150
    for k in range(n):
        x0, y0 = h32(k, 1, 581) * 64, h32(k, 2, 581) * 64
        if vn2(int(x0), int(y0), 16, 573) < (0.3 if then else 0.45):
            continue
        a = h32(k, 3, 581) * math.pi
        ln = 5 + h32(k, 4, 581) * 9
        tone = 0.75 + 0.4 * h32(k, 5, 581)
        col = shade(STRAW, tone) if then else lift(mix(shade(STRAW, tone), (104, 86, 56), 0.5), 0.05)
        for i in range(int(ln * 2)):
            px = int(x0 + math.cos(a) * i / 2) % 64
            py = int(y0 + math.sin(a) * i / 2) % 64
            im.set(px, py, shade(col, 1.12) if i % 5 == 0 else col)
    return im


def weigh_plate(then):
    """Pen 1's floor: a weighbridge 240 by 256 (columns 0..240): an iron chequer plate, its dark green rim and
    four bolts."""
    def fn(x, y):
        if x >= 240:
            return (40, 40, 40)
        if x < 8 or x >= 232 or y < 8 or y >= 248:
            c = shade(GREEN, 0.7 if (x in (0, 239) or y in (0, 255)) else 1.0)
            return c if then else lift(mix(c, RUST, 0.5 * vn2(x, y, 16, 581, 256)), 0.1)
        u, v = x % 12, y % 12
        c = shade(IRON, 1.0)
        if (u, v) in ((3, 3), (4, 4), (5, 5), (9, 8), (8, 9), (7, 10)):
            c = shade(IRON, 1.35)
        if not then:
            c = lift(mix(c, RUST, 0.25 + 0.4 * vn2(x, y, 16, 582, 256)), 0.1)
        return c
    im = flat(fn, 256)
    for cx, cy in ((14, 14), (226, 14), (14, 242), (226, 242)):
        im.disc(cx, cy, 3, (40, 46, 40))
    return im


def rubble(then):
    def fn(x, y):
        r = h32(x // 5, y // 5, 591)
        if r < 0.5:
            return lift(jt(BRICK, x, y, 592, 0.15), 0.08)
        if r < 0.62:
            return jt(LIME, x, y, 593, 0.08)
        if r < 0.85:
            return jt(MORTAR, x, y, 594, 0.1)
        if r < 0.92:
            return jt(STRAW, x, y, 595, 0.15)
        return (60, 52, 44)
    return flat(fn)


def green_plate(then, seed=601):
    def fn(x, y):
        c = jt(GREEN, x, y // 2, seed, 0.04)
        if x % 32 == 0 or y % 32 == 0:
            c = shade(c, 0.6)
        if (x % 32, y % 32) in ((4, 4), (28, 4), (4, 28), (28, 28)):
            c = shade(GREENL, 1.3)
        return c if then else lift(mix(c, RUST, 0.3 + 0.4 * vn2(x, y, 16, seed + 1)), 0.1)
    return flat(fn)


def quarry(then):
    """Red quarry tile, 16 square, dark joints; NOW worn, dirty, some lifted."""
    def fn(x, y):
        if x % 16 == 0 or y % 16 == 0:
            c = (96, 74, 62)
        else:
            k = h32((x // 16) % 4, (y // 16) % 4, 611)
            c = mix(QUARRY, (128, 52, 38), 0.5) if k < 0.25 else (mix(QUARRY, (184, 100, 64), 0.4) if k > 0.8 else QUARRY)
            c = jt(c, x, y, 612, 0.04)
            if x % 16 == 1 or y % 16 == 1:
                c = shade(c, 1.08)
        if not then:
            if h32((x // 16) % 4, (y // 16) % 4, 613) < 0.12:
                c = jt((104, 96, 84), x, y, 614, 0.1)
            c = mix(c, DIRT, 0.35 * vn2(x, y, 16, 615))
            c = lift(c, 0.1)
        return c
    return flat(fn)


def passage_ceiling(then):
    """Cream plaster, a green enamel lamp shade in every 64 (dead NOW)."""
    def fn(x, y):
        c = jt(CREAM, x // 2, y // 2, 621, 0.02)
        d = math.hypot(x - 31.5, y - 31.5)
        if d < 9:
            c = shade(GREEN, 1.25 - d / 14)
            if d < 3.5:
                c = (252, 246, 220) if then else (70, 66, 58)
        if not then:
            c = lift(mix(c, (110, 96, 70), 0.45 * vn2(x, y, 16, 622)), 0.04)
        return c
    return flat(fn)


def pen_ceiling(then):
    """Limewashed boards between brown joists."""
    def fn(x, y):
        if x % 32 in (0, 1, 2, 3, 4, 5):
            c = jt(WOOD, x, y // 4, 631, 0.05)
            c = shade(c, 0.7 if x % 32 in (0, 5) else 1.0)
        else:
            c = jt(LIME, x, y // 8, 632, 0.03)
            if y % 8 == 0:
                c = shade(c, 0.82)
        if not then:
            c = lift(mix(c, (96, 84, 62), 0.45 * vn2(x, y, 16, 633)), 0.05)
        return c
    return flat(fn)


def tread(then):
    """The turnstile's head and floor: dark green iron, a chequer tread."""
    def fn(x, y):
        c = shade(GREEN, 0.9)
        u, v = x % 8, y % 8
        if (u, v) in ((2, 2), (3, 3), (6, 5), (5, 6)):
            c = shade(GREENL, 1.2)
        if x % 32 == 0 or y % 32 == 0:
            c = shade(c, 0.6)
        return c if then else lift(mix(c, RUST, 0.3 + 0.4 * vn2(x, y, 16, 641)), 0.1)
    return flat(fn)


FLATS = {"YG": gravel, "SC": shelter_ceiling, "SF": sill_top, "HF": hall_floor, "HC": hall_ceiling, "RF": sand,
         "RC": roof_light, "PF": straw, "WP": weigh_plate, "PC": pen_ceiling, "LT": rubble, "GT": green_plate,
         "KF": quarry, "KK": passage_ceiling, "TF": tread}


# === pictures: painted boards, cream letters on dark green ======================================================
def board_ground(c, z, then, seed):
    """The board's paint at a point: dark green planks; NOW sun-bleached, the paint gone to grey wood here and
    there."""
    g = jt(GREEN, c // 3, z, seed, 0.025)
    if (z + seed) % 10 == 0:
        g = shade(g, 0.82)                                            # the planks' joints
    if then:
        return g
    g = mix(g, (150, 160, 140), 0.24)
    if vn(c, z, 4, seed + 1, 4096) > 0.85:
        g = jt((172, 160, 136), c, z, seed + 2, 0.05)                 # bare wood
    return g


def wboard(w, c1, ztop, c2, zbot, then, seed):
    """A painted board from column c1 to c2, ztop down to zbot: a dark edge, the green ground, a thin cream
    border; the ground function is kept for wear()."""
    c1, c2 = max(0, c1), min(w.w, c2)
    w.rect(c1, ztop, c2, zbot, shade(GREEND, 0.8) if then else (70, 76, 66))
    for z in range(zbot + 1, ztop):
        for c in range(c1 + 1, c2 - 1):
            w.at(c, z, board_ground(c, z, then, seed))
    w.frame(c1 + 2, ztop - 2, c2 - 2, zbot + 2, BORDER if then else mix(BORDER, (150, 156, 140), 0.3), 1)
    for cx, cz in ((c1 + 4, ztop - 4), (c2 - 5, ztop - 4), (c1 + 4, zbot + 4), (c2 - 5, zbot + 4)):
        w.at(cx, cz, (30, 30, 28))
    return c1, c2


def wear(w, c1, ztop, c2, zbot, then, seed):
    """NOW: the letters half gone (sun and rain), still readable; rust from the screws."""
    if then:
        return
    for z in range(zbot + 1, ztop):
        for c in range(max(0, c1 + 1), min(w.w, c2 - 1)):
            p = w.get(c, z)
            if p == LETTER:
                if h32(c // 2, z // 2, seed + 7) < 0.08 or vn(c, z, 4, seed + 1, 4096) > 0.85:
                    w.at(c, z, board_ground(c, z, then, seed))
                else:
                    w.at(c, z, (222, 214, 182))
    for cx, cz in ((c1 + 4, zbot + 3), (c2 - 5, zbot + 3)):
        rust_run(w, cx, cz, 6 + 6 * h32(cx, cz, seed), RUST, 0.45, 1)


def board_lines(w, spec, then, ztop, scales, pad=4, seed=0, gap=3):
    lines = spec["lines"]
    tw = max(text_width(s, sc) for s, sc in zip(lines, scales))
    hh = sum(5 * sc for sc in scales) + gap * (len(lines) - 1)
    cx = w.w // 2
    c1, c2 = cx - tw // 2 - pad - 3, cx + (tw + 1) // 2 + pad + 3
    zb = ztop - hh - 2 * pad - 4
    wboard(w, c1, ztop, c2, zb, then, seed)
    write_lines(w, lines, cx, ztop - pad - 2, LETTER, scales, gap)
    wear(w, c1, ztop, c2, zb, then, seed)
    return c1, c2, zb


def p_shelter(w, spec, then):
    board_lines(w, spec, then, 214, (3, 2), 5, 701, 5)


def arch(w, c1, c2, head, then):
    """A drawn brick arch over the door: voussoirs from c1 to c2 springing at `head`, a cream keystone."""
    cx = (c1 + c2) / 2
    r1 = (c2 - c1) / 2
    r2 = r1 + 12
    for z in range(int(head), int(head + r2 * 0.5) + 2):
        for c in range(int(cx - r2) - 1, int(cx + r2) + 2):
            dx, dz = (c + 0.5 - cx), (z - 0.5 - head) * 2.0          # a segmental arch (flattened)
            d = math.hypot(dx, dz)
            if r1 <= d <= r2 and dz >= 0:
                a = math.atan2(dz, dx)
                k = int(a / math.pi * 11)
                edge = abs(a / math.pi * 11 - round(a / math.pi * 11)) < 0.08 or d > r2 - 1 or d < r1 + 1
                if abs(a - math.pi / 2) < 0.1:
                    col = render(c, z, then, 711)                     # the keystone
                else:
                    col = mix(BRICK, (180, 96, 64), 0.3 * h32(k, 0, 712))
                    col = col if then else lift(col, 0.1)
                w.at(c, z, shade(MORTAR, 0.95) if edge else col)


def p_house(w, spec, then):
    c1, c2 = spec.get("door", (48, 112))
    head = spec.get("head", 128)
    arch(w, c1 - 4, c2 + 4, head, then)
    board_lines(w, spec, then, 190, (2,), 5, 702)


def p_plan(w, spec, then):
    c1, c2, ztop, zbot = 4, w.w - 4, 192, 36
    wboard(w, c1, ztop, c2, zbot, then, 703)
    w.centre("ANIMAL HOUSE", w.w // 2, ztop - 5, LETTER, 1)
    ink = LETTER
    draw_plan(w, spec["plan"], c1 + 4, ztop - 12, c2 - 4, zbot + 4, ink, faint=(150, 186, 150),
              here=(150, 206, 240))
    wear(w, c1, ztop, c2, zbot, then, 703)


def p_gate(w, spec, then):
    z, n = spec.get("head", 128), len(spec["lines"])
    board_lines(w, spec, then, z + (28 if n > 1 else 24), (2,) + (1,) * (n - 1), 3, 704, 2)


def p_hatch(w, spec, then):
    board_lines(w, spec, then, 82, (1,) * len(spec["lines"]), 3, 705, 2)
    if spec.get("arrow"):
        d = spec["arrow"]
        arrow(w, w.w // 2 + d * 22, 66, d, BORDER, 3)


def p_lever(w, spec, then):
    c1, c2, zb = board_lines(w, spec, then, 102, (2, 1), 4, 706, 3)
    d = spec.get("arrow", 0)
    if d:
        arrow(w, w.w // 2 + d * 4, zb - 8, d, GREEND, 4)
        arrow(w, w.w // 2 + d * 4, zb - 8, d, CREAM if then else (200, 192, 160), 3)


def p_rules(w, spec, then):
    lines = spec["lines"]
    board_lines(w, dict(spec, lines=lines), then, 124, (2,) + (1,) * (len(lines) - 1), 6, 707, 4)


def p_weigh(w, spec, then):
    board_lines(w, spec, then, 120, (2, 1, 1, 1), 6, 708, 5)


def p_glass(w, spec, then):
    board_lines(w, spec, then, 178, (2, 2), 4, 709, 3)


def p_keepers(w, spec, then):
    board_lines(w, spec, then, 118, (1,), 3, 710)


# --- the species boards ---------------------------------------------------------------------------------------
def ellipse(w, cx, cz, rx, rz, col):
    for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
        for c in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((c + 0.5 - cx) / rx) ** 2 + ((z - 0.5 - cz) / rz) ** 2 <= 1:
                w.at(c, z, col)


def silhouette(w, kind, cx, zb, h, col):
    """The animal in profile or front, h high, its feet at zb, centred on cx."""
    u = h / 32.0

    def E(x, z, rx, rz):
        ellipse(w, cx + x * u, zb + z * u, max(1, rx * u), max(1, rz * u), col)

    def R(x1, z1, x2, z2):
        w.rect(int(cx + x1 * u), int(zb + z1 * u), int(cx + x2 * u) + 1, int(zb + z2 * u), col)

    def L(x1, z1, x2, z2, t=1):
        w.line(cx + x1 * u, zb + z1 * u, cx + x2 * u, zb + z2 * u, col, max(1, int(t * u + 0.5)))
    if kind == "demon":                         # the pinky, in profile, facing left: a hunched bulk, a big jaw
        E(4, 19, 11, 8)                         # the hump
        E(-4, 15, 8, 7)                         # the chest
        E(-12, 17, 5, 5)                        # the head, forward
        R(-19, 21, -11, 18)                     # the upper jaw
        R(-19, 15, -11, 12)                     # the lower jaw (the mouth open between)
        R(-18, 18, -17, 15)
        R(-15, 18, -14, 16)                     # teeth
        L(-10, 21, -7, 25, 1.5)                 # a horn
        R(6, 13, 12, 3)                         # the hind leg
        R(9, 4, 15, 0)
        R(-6, 10, -1, 3)                        # the front leg
        R(-9, 3, -1, 0)
        L(14, 20, 19, 17, 1.5)                  # the tail
    elif kind in ("knight", "baron"):           # front, horned, broad
        E(0, 26, 3.4, 3.6)                      # the head
        L(-3, 28, -7, 32, 1)
        L(3, 28, 7, 32, 1)                      # the horns
        E(0, 18, 8, 6)                          # the shoulders and chest
        R(-5, 18, 5, 10)
        R(-6, 11, -1, 0)
        R(1, 11, 6, 0)                          # the legs (goat's: bent)
        R(-9, 22, -6, 8)
        R(6, 22, 9, 8)                          # the arms
        E(-8, 8, 2, 2)
        E(8, 8, 2, 2)
        if kind == "baron":
            L(-9, 8, -11, 5, 1)
            L(9, 8, 11, 5, 1)                   # claws
    else:                                       # the cyberdemon: front, huge, a cannon for an arm
        E(0, 27, 3, 3.4)
        L(-2, 29, -6, 32, 1)
        L(2, 29, 6, 32, 1)
        E(0, 19, 9, 6)
        R(-6, 19, 6, 11)
        R(-7, 12, -2, 0)
        R(2, 12, 7, 0)
        R(-11, 22, -8, 9)
        R(8, 22, 13, 15)
        R(10, 16, 13, 8)                        # the cannon
        R(13, 13, 16, 9)


def wrap(text, width, scale=1):
    """Words into lines no wider than `width` at `scale`."""
    out, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if text_width(t, scale) <= width or not cur:
            cur = t
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def species_board(w, run, c1, ztop, c2, then, seed, small=False):
    """A species board: the silhouette, the species, its Latin name, the names, a DO NOT FEED bar."""
    inner = c2 - c1 - 10
    sh = 20 if small else 34
    sp_scale = 2 if (not small and text_width(run["species"], 2) <= inner) else 1
    sp = wrap(run["species"], inner, sp_scale)
    lat = wrap(run["latin"], inner)
    names = [] if small else wrap(" ".join(run["names"]), inner)
    feed = wrap("DO NOT FEED", inner - 4)
    hh = 5 + sh + 4 + len(sp) * (5 * sp_scale + 2) + 2 + len(lat) * 7 + (len(names) * 7 + 3 if names else 0) + \
        3 + len(feed) * 7 + 4 + 4
    zbot = ztop - hh
    wboard(w, c1, ztop, c2, zbot, then, seed)
    cx = (c1 + c2) // 2
    z = ztop - 5
    silhouette(w, run["kind"], cx, z - sh, sh, LETTER)
    z -= sh + 4
    for s in sp:
        w.centre(s, cx, z, LETTER, sp_scale)
        z -= 5 * sp_scale + 2
    z -= 2
    for s in lat:
        w.centre(s, cx, z, LETTER, 1)
        z -= 7
    if names:
        z -= 1
        w.rect(cx - 12, z + 1, cx + 12, z, BORDER if then else mix(BORDER, (150, 156, 140), 0.3))
        z -= 2
        for s in names:
            w.centre(s, cx, z, LETTER, 1)
            z -= 7
    z -= 2
    fw = max(text_width(s) for s in feed) + 6
    w.rect(cx - fw // 2, z + 1, cx + (fw + 1) // 2, z - len(feed) * 7 - 1, BORDER if then else (204, 196, 166))
    z -= 1
    for s in feed:
        w.centre(s, cx, z, GREEND, 1)
        z -= 7
    wear(w, c1, ztop, c2, zbot, then, seed)
    if not then:
        chips(w, c1 + 3, ztop - 3, c2 - 3, zbot + 3, (172, 160, 136), 2 + (c2 - c1) // 40, seed + 5, (0.8, 1.8))
    return zbot


def p_board(w, spec, then):
    run = RUNS[spec["run"]]
    bw = min(w.w - 8, 150)
    c1 = (w.w - bw) // 2
    species_board(w, run, c1, 154, c1 + bw, then, 720 + len(run["ids"]))


def p_card(w, spec, then):
    run = RUNS[spec["run"]]
    species_board(w, run, 2, 120, w.w - 2, then, 730, small=True)


PICTURES = {"shelter": p_shelter, "house": p_house, "plan": p_plan, "gate": p_gate, "hatch": p_hatch,
            "lever": p_lever, "rules": p_rules, "weigh": p_weigh, "glass": p_glass, "keepers": p_keepers,
            "board": p_board, "card": p_card}


# === sprites ======================================================================================================
def s_bowl(then):
    """A shallow iron trough, dark green outside; THEN meat in it, NOW rusted and on its side."""
    im = sprite_img(26, 12)
    if then:
        for y in range(4, 12):
            inset = (y - 4) // 3
            im.rect(1 + inset, y, 25 - inset, y + 1, shade(GREEN, 0.8 + 0.06 * (11 - y)))
        im.rect(0, 3, 26, 5, shade(GREENL, 1.1))
        for x in range(3, 23, 3):
            im.disc(x + 1, 3, 1.7, (128, 58, 44))
            im.set(x, 2, (176, 120, 100))
    else:
        for y in range(1, 12):
            half = int(math.sqrt(max(0, 36 - (y - 6) ** 2)))
            im.rect(13 - half, y, 13 + half, y + 1, lift(mix(GREEN, RUST, 0.5 + 0.03 * y), 0.15))
        im.rect(9, 3, 14, 10, (52, 40, 32))
        im.rect(17, 10, 24, 12, lift(mix(GREEN, RUST, 0.7), 0.1))
    return im, (13, 12)


def s_bucket(then):
    """A green pail with a broom leaning on it; NOW rusted and dented."""
    im = sprite_img(28, 30)
    body = GREEN if then else lift(mix(GREEN, RUST, 0.55), 0.15)
    for y in range(10, 30):
        half = 7 + (29 - y) // 6
        for x in range(13 - half, 13 + half):
            f = 0.75 + 0.45 * (1 - abs(x - 10) / (half + 3))
            im.set(x, y, shade(body, f))
    im.rect(4, 10, 23, 12, shade(body, 1.35))
    if not then:
        im.rect(14, 18, 19, 22, shade(body, 0.6))                    # a dent
    for x in range(5, 22):
        y = 10 - int(7 * math.sin((x - 5) / 16 * math.pi))
        im.set(x, y, (60, 60, 60))
    for y in range(0, 24):                                            # the broom's handle
        im.set(22 + y // 8, y, (150, 108, 66) if then else (110, 90, 66))
    im.rect(20, 23, 28, 26, (122, 84, 52) if then else (96, 76, 56))
    for x in range(20, 28):
        for y in range(26, 30):
            if h32(x, y, 801) < 0.75:
                im.set(x, y, (196, 170, 110) if then else (140, 126, 96))
    return im, (13, 30)


def s_store(then):
    """THEN a wooden barrow of meat; NOW its wreck, tipped, a wheel off."""
    im = sprite_img(46, 40)
    wood = WOOD if then else lift((110, 92, 72), 0.1)
    if then:
        for y in range(14, 30):                                       # the box
            for x in range(4, 36):
                c = shade(wood, 0.9 + 0.2 * ((y // 4) % 2))
                if y % 4 == 0:
                    c = shade(wood, 0.7)
                im.set(x, y, c)
        im.rect(4, 14, 36, 16, shade(GREEN, 1.1))                     # a green rim
        for k in range(9):                                            # the meat
            cx, cy = 7 + k * 3.4, 12 - 2 * math.sin(k * 1.3)
            im.disc(int(cx), int(cy), 3, (150, 62 + 6 * (k % 3), 50))
            im.set(int(cx) - 1, int(cy) - 2, (214, 200, 180))
        im.disc(36, 32, 7, (54, 50, 46))                             # the wheel
        im.disc(36, 32, 4, (110, 90, 64))
        im.disc(36, 32, 1, (40, 40, 40))
        im.rect(4, 30, 7, 40, shade(wood, 0.8))                        # the legs
        im.rect(30, 30, 33, 34, shade(wood, 0.8))
        for y in range(16, 30):                                       # the handles
            im.set(4 - (y - 16) // 4, y + 2, shade(wood, 0.7))
    else:
        for y in range(24, 38):                                       # the box on its side
            for x in range(2, 30):
                if h32(x // 3, y // 4, 811) < 0.85:
                    c = shade(wood, 0.85 + 0.2 * ((x // 5) % 2))
                    if x % 5 == 0:
                        c = shade(wood, 0.6)
                    im.set(x, y, c)
        im.rect(6, 28, 12, 34, (40, 34, 28))                          # a plank gone
        for k in range(4):                                            # planks on the ground
            im.rect(28 + k * 2, 36 - k, 44, 37 - k, shade(wood, 0.8 + 0.08 * k))
        for a in range(0, 360, 6):                                    # the wheel, flat on the floor
            x = 38 + 6 * math.cos(math.radians(a))
            y = 34 + 2 * math.sin(math.radians(a))
            im.set(int(x), int(y), (70, 64, 58))
        im.rect(2, 38, 30, 40, (60, 52, 44))
        im.disc(18, 22, 2, (210, 200, 176))                           # a bone
        im.rect(14, 22, 23, 23, (210, 200, 176))
    return im, (22, 40)


SPRITES = {"bowl": s_bowl, "bucket": s_bucket, "store": s_store}
