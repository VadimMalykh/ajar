"""MAP23's look 1, "Vivarium" (specimens; a laboratory animal house of the 1960s): art only, the slots of
tools/gfx_dogs.py (read its docstring first; this file is the model for looks 2 and 3).

THEN: white glazed tile to shoulder height with one course of green tile, pale grey-green paint above; grey
terrazzo with a drain channel in the runs, red oxide sealed concrete in the pens; galvanised sheet gates with
rivets, stainless hatch surrounds; the passages in cream gloss paint over a grey dado, lino. The yard: pale
concrete panels with a drawn ribbon of windows, asphalt, a concrete shelter. Lettering: white enamel plates, black
capitals, numbers.
NOW: tiles fallen in patches to the brick, rust runs under every fixing, black mould from the floor up, cracked
terrazzo, the paint gone to plaster; drawn a little lighter than it would be, to read at light 120.
"""
import math
import random

from gfx_dogs import (RUNS, Img, arrow, chips, draw_plan, flat, h32, mix, rust_run, shade, sprite_img,
                      text_width, write_lines)

# --- the palette ------------------------------------------------------------------------------------------------
TILE = (234, 236, 230)
GROUT = (176, 182, 178)
GREEN = (58, 132, 96)
PAINT = (192, 208, 196)
STEEL = (184, 190, 194)
STAIN = (206, 212, 216)          # stainless
GALV = (160, 168, 168)
BRICK = (150, 88, 66)
MORTAR = (168, 160, 146)
RUST = (132, 70, 36)
MOULD = (34, 40, 32)
CREAM = (226, 214, 168)
DADO = (118, 126, 130)
CONC = (196, 194, 184)
GLASSD = (52, 70, 82)
ALU = (196, 200, 204)
INK = (24, 24, 26)
ENAMEL = (240, 240, 234)


def jt(c, x, z, s, a):
    return shade(c, 1 + (h32(x, z, s) - 0.5) * 2 * a)


# --- what forty years do (NOW) ------------------------------------------------------------------------------
def mould(c, x, z, then, top=36, s=7):
    """Black mould from the floor up, ragged."""
    if then:
        return c
    lim = top * (0.55 + 0.6 * h32(x // 3, 0, s))
    if z <= lim:
        f = 0.25 + 0.6 * (1 - z / max(lim, 1)) * (0.6 + 0.4 * h32(x, z, s + 1))
        return mix(c, MOULD, min(f, 0.85))
    if z <= lim + 6 and h32(x, z, s + 2) < 0.3:
        return mix(c, MOULD, 0.3)
    return c


def brick_at(x, z, s=3):
    """Common brick in stretcher bond by absolute height (the wall behind the tile)."""
    row = (z - 1) // 8
    bx = (x + (16 if row % 2 else 0)) % 32
    if (z - 1) % 8 == 0 or bx == 0:
        return jt(MORTAR, x, z, s, 0.08)
    return jt(BRICK, x // 4, row, s, 0.12)


def tile_wall(x, z, then, lo, hi, size=16, base=TILE, gone=0.0, seed=1):
    """Glazed tile from lo up to hi; NOW some fallen to the brick."""
    kx, kz = x // size, (z - 1 - lo) // size
    dx, dz = x % size, (z - 1 - lo) % size
    if not then and h32(kx, kz, seed) < gone:
        if dx in (0, size - 1) or dz in (0, size - 1):
            return jt((150, 146, 132), x, z, seed, 0.06)          # the cement bed's edge
        return brick_at(x, z, seed)
    if dx == 0 or dz == 0:
        c = GROUT
    else:
        c = jt(base, kx, kz, seed + 3, 0.025)
        if dx == 1 or dz == size - 1:
            c = shade(c, 1.05)                                    # the glaze's highlight
    if not then:
        c = mix(c, (204, 196, 160), 0.22 + 0.15 * h32(kx, kz, seed + 5))     # yellowed
        if h32(kx * 7 + dx // 3, kz, seed + 9) < 0.04:
            c = shade(c, 0.7)                                     # a crack
    return c


def paint(x, z, then, c, seed=2, plaster=(186, 178, 160)):
    """Flat paint; NOW flaking to the plaster in patches, dull."""
    if then:
        return jt(c, x, z, seed, 0.015)
    if h32(x // 6, z // 5, seed) < 0.16:
        return jt(plaster, x, z, seed + 1, 0.05)
    return jt(mix(c, (170, 168, 150), 0.28), x, z, seed, 0.035)


def rusty(w, then, fix_z, xs=(32,), length=60, seed=4):
    """Rust runs down from fixings at height fix_z (NOW)."""
    if then:
        return
    for c in range(w.w):
        xw = (w.shift + c) % w.period
        if xw in xs:
            ln = length * (0.6 + 0.6 * h32(xw, fix_z, seed))
            rust_run(w, c, fix_z, ln, RUST, 0.6, 2)


# === walls =====================================================================================================
def runs_wall(w, then):
    """Tile to 80, a course of green 80..96, grey-green paint above; a conduit at 140 (its clips rust NOW)."""
    def fn(x, z):
        if z <= 8:
            c = jt((86, 100, 92), x, z, 5, 0.04)                       # coved skirting tile
        elif z <= 80:
            c = tile_wall(x, z, then, 8, 80, gone=0.16, seed=11)
        elif z <= 96:
            c = tile_wall(x, z, then, 80, 96, base=GREEN, gone=0.2, seed=12)
        elif 138 <= z <= 142:
            c = shade(STEEL, 0.9 if z in (138, 142) else 1.05) if then else shade(RUST, 1.25)
        else:
            c = paint(x, z, then, PAINT, 13)
        return mould(c, x, z, then, 34, 14)
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        if (w.shift + c) % 64 in (30, 31, 32, 33):
            w.rect(c, 144, c + 1, 136, shade(STEEL, 0.7) if then else RUST)
    rusty(w, then, 136, (31,), 70, 15)


def pens_wall(w, then):
    """Tile to 104 with a stainless kick plate to 12, a green course 104..112, paint above."""
    def fn(x, z):
        if z <= 12:
            c = jt(STAIN, x, z, 21, 0.03) if then else mix(jt(STAIN, x, z, 21, 0.05), RUST, 0.35 * h32(x // 2, 0, 3))
            if z == 12:
                c = shade(c, 0.7)
        elif z <= 104:
            c = tile_wall(x, z, then, 12, 108, gone=0.22, seed=22)
        elif z <= 112:
            c = tile_wall(x, z, then, 104, 112, size=8, base=GREEN, gone=0.25, seed=23)
        else:
            c = paint(x, z, then, PAINT, 24)
        return mould(c, x, z, then, 48, 25)
    w.fill(w.z0, w.bot, fn)
    if not then:                                                       # rust from the kick plate's screws
        for c in range(w.w):
            if (w.shift + c) % 32 == 8:
                rust_run(w, c, 11, 10, RUST, 0.6, 1)


def ledge_face(w, then):
    """NOW: the pen's wall from its lowest 48 rows, broken off at the top (brick and the cement bed)."""
    pens_wall(w, then)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        top = 40 + int(8 * h32(xw // 3, 1, 31))
        for z in range(top, 49):
            w.at(c, z, brick_at(xw, z, 32) if h32(xw, z, 33) < 0.8 else MORTAR)
        w.at(c, top, shade(MORTAR, 0.7))


def hall_wall(w, then):
    """The hall: pale green tile to 64, a dark green cap course to 72, grey paint above, a picture rail at 150."""
    def fn(x, z):
        if z <= 8:
            c = jt((70, 88, 78), x, z, 41, 0.04)
        elif z <= 64:
            c = tile_wall(x, z, then, 8, 64, size=16, base=(170, 206, 182), gone=0.2, seed=42)
        elif z <= 72:
            c = tile_wall(x, z, then, 64, 72, size=8, base=(52, 112, 84), gone=0.25, seed=43)
        elif 148 <= z <= 151:
            c = jt((150, 156, 150), x, z, 44, 0.03)
        else:
            c = paint(x, z, then, (208, 210, 198), 45)
        return mould(c, x, z, then, 30, 46)
    w.fill(w.z0, w.bot, fn)


def passage_wall(w, then):
    """Cream gloss over a grey dado (8..52), a black skirting, a grey line; a conduit at 100."""
    def fn(x, z):
        if z <= 8:
            c = jt((40, 42, 44), x, z, 51, 0.04)
        elif z <= 52:
            c = jt(DADO, x, z, 52, 0.02) if then else paint(x, z, then, DADO, 52, (150, 146, 136))
            if z == 52:
                c = shade(c, 0.6)
        elif 98 <= z <= 101:
            c = shade(STEEL, 1.05 if z == 100 else 0.85) if then else shade(RUST, 1.3)
        else:
            c = jt(CREAM, x, z, 53, 0.012) if then else paint(x, z, then, CREAM, 53, (176, 168, 150))
        return mould(c, x, z, then, 28, 54)
    w.fill(w.z0, w.bot, fn)
    rusty(w, then, 97, (20,), 50, 55)


def yard_panels(x, z, then, seed=61):
    """Pale precast concrete panels, 64 square, the joints dark; NOW streaked."""
    if z <= 12:
        return mould(jt((120, 122, 120), x, z, seed, 0.05), x, z, then, 14, seed + 1)
    if x % 64 in (0, 63) or (z - 12) % 64 in (0, 1):
        c = (128, 128, 124)
    else:
        c = jt(CONC, x // 2, z // 2, seed + 2, 0.03)
        c = shade(c, 1 + 0.02 * math.sin(x * 0.9 + z * 0.3))
    if not then:
        streak = h32(x // 2, 0, seed + 3)
        if streak < 0.25:
            c = mix(c, (96, 92, 80), 0.25 + 0.3 * streak)
        c = mix(c, (150, 150, 134), 0.15)
        c = mould(c, x, z, then, 24, seed + 4)
    return c


def yard_front(w, then):
    """The house's front: panels, a ribbon of windows (160..208) with aluminium mullions; NOW broken panes."""
    def fn(x, z):
        if 158 <= z <= 160:
            return shade(ALU, 0.9)
        if 160 < z <= 208:
            if x % 32 in (0, 1) or z in (184, 185):
                return shade(ALU, 0.95 if then else 0.75)
            g = shade(GLASSD, 1 + 0.25 * ((x % 32) + (z - 160)) / 80)
            if then and (x % 32) - (z - 160) // 2 in (6, 7, 8):
                g = shade(g, 1.5)                                   # the sky in it
            if not then and h32(x // 32, z // 24, 66) < 0.5:
                g = (10, 12, 14) if h32(x, z, 67) < 0.8 else (90, 100, 104)      # broken: dark behind, shards
            return g
        if 208 < z <= 212:
            return shade(ALU, 0.85)
        if z > 248:
            return jt((210, 208, 198), x, z, 68, 0.03)               # the coping
        return yard_panels(x, z, then)
    w.fill(w.z0, w.bot, fn)
    rusty(w, then, 156, (16, 48), 80, 69)


def yard_wall(w, then):
    """The yard's other walls: the panels, a grey band at 88..92, the coping."""
    def fn(x, z):
        if 88 <= z <= 92:
            return jt((150, 156, 150), x, z, 71, 0.03)
        if z > 248:
            return jt((210, 208, 198), x, z, 72, 0.03)
        return yard_panels(x, z, then, 73)
    w.fill(w.z0, w.bot, fn)
    rusty(w, then, 87, (32,), 50, 74)


def shelter_mass(w, then):
    """The shelter's roof: a concrete slab's edge (112..136), board-marked concrete over it."""
    def fn(x, z):
        if z <= 114:
            return shade(CONC, 0.6)                                    # the drip
        if z <= 136:
            c = jt((206, 204, 194), x // 2, z, 81, 0.03)
            return c if then else mix(c, (110, 106, 92), 0.25 * h32(x // 3, 0, 82))
        c = jt((184, 182, 172), x, z // 8, 83, 0.04)
        if z % 8 == 0:
            c = shade(c, 0.9)                                          # the boards' marks
        if not then:
            c = mix(c, (100, 98, 86), 0.3 * h32(x // 2, 1, 84))
        return c
    w.fill(w.z0, w.bot, fn)


def sill(w, then):
    """A concrete sill (0..8), an aluminium frame's head (136..148), the panels over it."""
    def fn(x, z):
        if z <= 8:
            return jt((206, 204, 196), x, z, 91, 0.03) if then else jt((160, 156, 144), x, z, 91, 0.06)
        if z <= 148:
            c = shade(ALU, 1.08 if z % 6 == 0 else 0.95)
            return c if then else mix(c, (110, 104, 92), 0.35)
        return yard_panels(x, z, then, 92)
    w.fill(w.z0, w.bot, fn)


def gateway(w, then):
    """The big run's gateway THEN, shut: a galvanised sheet gate (0..176) with rails and rivets, a lintel over."""
    def fn(x, z):
        if z > 176:
            return yard_panels(x, z, then, 101)
        if z > 172:
            return shade(GALV, 0.7)
        c = jt(GALV, x // 2, z // 3, 102, 0.05)
        if x % 16 in (0, 1):
            c = shade(c, 0.78)                                         # the sheets' ribs
        if z in range(20, 28) or z in range(84, 92) or z in range(148, 156):
            c = shade(GALV, 0.92)                                      # the rails
        return c if then else mix(c, RUST, 0.4 * h32(x // 4, z // 6, 103))
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        if (w.shift + c) % 8 == 4:
            for zz in (24, 88, 152):
                w.disc(c + 0.5, zz, 1.2, shade(GALV, 1.25))


def house_door(w, then):
    """The front door THEN (64 x 128): a grey-green painted steel door with a wired-glass panel, aluminium frame."""
    w.rect(0, 128, 64, 0, ALU)
    w.rect(4, 124, 60, 0, shade(ALU, 0.8))
    w.rect(6, 122, 58, 0, (88, 112, 104))
    for z in range(0, 122):
        for c in range(6, 58):
            if h32(c, z, 111) < 0.08:
                w.at(c, z, shade((88, 112, 104), 1.06))
    w.rect(16, 108, 48, 64, (150, 170, 178))                            # wired glass
    for c in range(16, 48, 4):
        w.rect(c, 108, c + 1, 64, (110, 126, 132))
    for z in range(64, 108, 4):
        w.rect(16, z + 1, 48, z, (110, 126, 132))
    w.frame(16, 108, 48, 64, shade(ALU, 0.7), 1)
    w.rect(46, 60, 54, 44, STAIN)                                     # the push plate
    w.rect(6, 14, 58, 0, STAIN)                                       # the kick plate
    w.rect(6, 15, 58, 14, shade(STAIN, 0.6))


def gate_leaf(w, then):
    """A gate's leaf: galvanised sheet, stiffeners every 32, rows of rivets; NOW rusted through in places."""
    def fn(x, z):
        c = jt(GALV, x // 2, z // 4, 121, 0.05)
        if x % 32 in (0, 1, 2):
            c = shade(c, 0.8 if x % 32 == 0 else 1.1)
        if z % 48 in (0, 1, 2):
            c = shade(c, 0.85)
        if not then:
            r = h32(x // 3, z // 5, 122)
            c = mix(c, RUST, 0.25 + 0.5 * r)
            if r > 0.93:
                c = (40, 30, 24)                                       # holes
            c = mould(c, x, z, then, 30, 123)
        return c
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        if xw % 8 == 5:
            for zz in range(4, w.z0, 48):
                w.disc(c + 0.5, zz, 1.2, shade(GALV, 1.3) if then else shade(RUST, 0.8))


def gate_reveal(w, then):
    """A gate's jambs: a stainless channel, its groove; NOW rust and the bolts' holes."""
    def fn(x, z):
        c = jt(STAIN, x, z // 3, 131, 0.03)
        if x % 16 in (6, 7, 8, 9):
            c = shade(c, 0.62)                                         # the groove
        if not then:
            c = mix(c, RUST, 0.3 + 0.35 * h32(x // 2, z // 7, 132))
            c = mould(c, x, z, then, 30, 133)
        return c
    w.fill(w.z0, w.bot, fn)


def hatch_surround(w, then):
    """A hatch's surround: a stainless plate from the floor to 72 (the hole at 24..56), light paint over it."""
    def fn(x, z):
        if z <= 72:
            c = jt(STAIN, x, z // 4, 141, 0.03)
            if z in (70, 71, 72) or z in (16, 17):
                c = shade(c, 0.75)
            if not then:
                c = mix(c, RUST, 0.2 + 0.35 * h32(x // 3, z // 5, 142))
                c = mould(c, x, z, then, 20, 143)
            return c
        return paint(x, z, then, (214, 218, 212), 144)
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        if (w.shift + c) % 16 == 8:
            for zz in (66, 20):
                w.disc(c + 0.5, zz, 1.2, shade(STAIN, 0.55))
    rusty(w, then, 64, (8, 24, 40, 56), 22, 145)


def turnstile_jamb(w, then):
    """A turnstile's jamb: a polished steel post, black rubber stops; NOW a rusted stump of it."""
    def fn(x, z):
        c = shade(STAIN, 0.8 + 0.4 * abs(math.sin(x * 0.35)))
        if z % 24 in (0, 1, 2, 3):
            c = (40, 40, 42)
        if not then:
            c = mix(c, RUST, 0.55 * h32(x // 2, z // 4, 151) + 0.2)
            if z > 60 + 20 * h32(x // 4, 0, 152):
                c = mix(c, (60, 52, 44), 0.5)
        return c
    w.fill(w.z0, w.bot, fn)


WALLS = {"YF": yard_front, "YW": yard_wall, "SM": shelter_mass, "SL": sill, "GW": gateway, "HD": house_door,
         "HW": hall_wall, "RW": runs_wall, "PW": pens_wall, "LF": ledge_face, "GL": gate_leaf, "GR": gate_reveal,
         "HS": hatch_surround, "KW": passage_wall, "TS": turnstile_jamb}


# === flats =====================================================================================================
def asphalt(then):
    def fn(x, y):
        c = jt((84, 86, 88), x, y, 201, 0.12)
        if h32(x, y, 202) < 0.06:
            c = (130, 128, 122)
        if not then:
            crack = abs(math.sin(x * 0.11 + 2 * math.sin(y * 0.09))) < 0.05
            if crack:
                c = (30, 30, 30)
            if h32(x // 4, y // 4, 203) < 0.07:
                c = jt((70, 96, 52), x, y, 204, 0.2)                    # weeds
        return c
    return flat(fn)


def soffit(then):
    def fn(x, y):
        c = jt((190, 188, 178), x, y // 8, 211, 0.04)
        if y % 8 == 0:
            c = shade(c, 0.9)
        return c if then else mix(c, (90, 88, 76), 0.3 * h32(x // 5, y // 5, 212))
    return flat(fn)


def sill_top(then):
    return flat(lambda x, y: jt((204, 202, 194), x, y, 221, 0.04) if then else jt((150, 146, 134), x, y, 221, 0.08))


def hall_floor(then):
    def fn(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return (120, 124, 116)
        c = jt((168, 176, 166), x // 2, y // 2, 231, 0.05)
        if h32(x, y, 232) < 0.1:
            c = shade(c, 0.75)
        if not then:
            if h32(x // 32, y // 32, 233) < 0.25:
                c = jt((96, 92, 82), x, y, 234, 0.12)                   # tiles gone to the screed
            if abs(math.sin(x * 0.2 + y * 0.07)) < 0.04:
                c = (40, 40, 38)
        return c
    return flat(fn)


def ceiling_tiles(then, seed=241):
    def fn(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return (150, 152, 150)
        if then:
            c = jt((226, 228, 224), x, y, seed, 0.02)
            return shade(c, 0.85) if (x * 3 + y * 7) % 11 == 0 else c
        if h32(x // 32, y // 32, seed + 1) < 0.3:
            return jt((30, 30, 32), x, y, seed + 2, 0.1)                # a tile gone: the dark above
        return mix(jt((208, 206, 196), x, y, seed, 0.03), (120, 100, 70), 0.3 * h32(x // 6, y // 6, seed + 3))
    return flat(fn)


def run_floor(then):
    """Grey terrazzo, 128, a drain channel along x at y 56..72 with its grating; NOW cracked."""
    def fn(x, y):
        if 56 <= y < 72:
            if y in (56, 71):
                return (90, 92, 92)
            c = (60, 62, 64) if x % 4 in (0, 1) else (132, 136, 138)
            return c if then else mix(c, RUST, 0.6)
        c = jt((172, 174, 168), x, y, 251, 0.03)
        r = h32(x, y, 252)
        if r < 0.12:
            c = jt((220, 218, 210), x, y, 253, 0.05)
        elif r < 0.2:
            c = jt((96, 100, 98), x, y, 254, 0.08)
        if x % 64 == 0 or y % 64 == 0:
            c = (150, 146, 120)                                       # the brass strips
        if not then:
            if abs(math.sin(x * 0.05 + 3 * math.sin(y * 0.04))) < 0.025 or abs(math.sin(y * 0.06 + x * 0.013)) < 0.02:
                c = (34, 34, 32)
            c = mix(c, (110, 100, 80), 0.18 * h32(x // 8, y // 8, 255))
        return c
    return flat(fn, 128)


def plain_ceiling(then, seed=261):
    def fn(x, y):
        c = jt((214, 220, 214), x, y, seed, 0.02)
        if 28 <= x % 64 <= 35 and 4 <= y % 64 <= 59:
            c = (250, 250, 236) if then else (70, 72, 66)              # a strip light (dead NOW)
            if x % 64 in (28, 35):
                c = (150, 150, 146)
        if not then:
            c = mix(c, (96, 90, 74), 0.35 * h32(x // 8, y // 8, seed + 1))
        return c
    return flat(fn)


def red_oxide(then):
    def fn(x, y):
        c = jt((128, 66, 50), x // 2, y // 2, 271, 0.05)
        c = shade(c, 1.06) if h32(x // 9, y // 9, 272) < 0.5 else c
        if not then:
            c = mix(c, (70, 60, 50), 0.4 * h32(x // 5, y // 5, 273))
            if abs(math.sin(x * 0.13 + y * 0.05)) < 0.03:
                c = (30, 26, 24)
        return c
    return flat(fn)


def weigh_plate(then):
    """Pen 1's floor: a steel platform 240 by 256 (columns 0..240), chequer plate, its rim and four bolts."""
    def fn(x, y):
        if x >= 240:
            return (40, 40, 40)
        if x < 6 or x >= 234 or y < 6 or y >= 250:
            c = shade(STEEL, 0.7 if (x in (0, 239) or y in (0, 255)) else 0.95)
        else:
            u, v = x % 12, y % 12
            c = shade(STEEL, 0.82)
            if (u, v) in ((3, 3), (4, 4), (5, 5), (9, 8), (8, 9), (7, 10)):
                c = shade(STEEL, 1.15)
        if not then:
            c = mix(c, RUST, 0.3 + 0.4 * h32(x // 6, y // 6, 281))
        return c
    im = flat(fn, 256)
    for cx, cy in ((12, 12), (228, 12), (12, 244), (228, 244)):
        im.disc(cx, cy, 3, (90, 92, 94))
    return im


def rubble(then):
    def fn(x, y):
        r = h32(x // 5, y // 5, 291)
        if r < 0.45:
            return jt(BRICK, x, y, 292, 0.15)
        if r < 0.6:
            return jt(TILE, x, y, 293, 0.08) if h32(x // 5, y // 5, 294) < 0.5 else jt(GREEN, x, y, 293, 0.1)
        if r < 0.85:
            return jt(MORTAR, x, y, 295, 0.1)
        return (50, 46, 42)
    return flat(fn)


def steel_plate(then):
    def fn(x, y):
        c = jt(STAIN, x, y // 2, 301, 0.03)
        if x % 32 == 0 or y % 32 == 0:
            c = shade(c, 0.7)
        return c if then else mix(c, RUST, 0.35 + 0.3 * h32(x // 4, y // 4, 302))
    return flat(fn)


def lino(then):
    def fn(x, y):
        if x % 32 == 0 or y % 32 == 0:
            return (90, 100, 92)
        c = jt((126, 142, 128), x // 2, y // 2, 311, 0.03)
        c = shade(c, 1 + 0.06 * math.sin(x * 0.4 + 3 * math.sin(y * 0.15)))
        if not then:
            if h32(x // 16, y // 16, 312) < 0.12:
                c = jt((70, 66, 58), x, y, 313, 0.1)                   # lifted to the screed
            c = mix(c, (80, 74, 60), 0.2)
        return c
    return flat(fn)


def cream_ceiling(then):
    return plain_ceiling(then, 321) if then else flat(
        lambda x, y: mix(jt((214, 206, 176), x, y, 322, 0.03), (90, 80, 60), 0.4 * h32(x // 7, y // 7, 323)))


FLATS = {"YG": asphalt, "SC": soffit, "SF": sill_top, "HF": hall_floor, "HC": ceiling_tiles, "RF": run_floor,
         "RC": plain_ceiling, "PF": red_oxide, "WP": weigh_plate, "PC": lambda then: plain_ceiling(then, 331),
         "LT": rubble, "GT": steel_plate, "KF": lino, "KK": cream_ceiling, "TF": steel_plate}


# === pictures: white enamel, black capitals ======================================================================
def enamel(w, c1, ztop, c2, zbot, then, seed, ground=ENAMEL, rim=INK):
    """A white enamel plate with a black rim and four screws; NOW chipped to the iron, rust from the screws."""
    w.rect(c1, ztop, c2, zbot, shade(rim, 1.0))
    w.rect(c1 + 1, ztop - 1, c2 - 1, zbot + 1, ground if then else mix(ground, (214, 200, 150), 0.3))
    w.frame(c1 + 2, ztop - 2, c2 - 2, zbot + 2, rim, 1)
    for cx, cz in ((c1 + 4, ztop - 4), (c2 - 5, ztop - 4), (c1 + 4, zbot + 4), (c2 - 5, zbot + 4)):
        w.at(cx, cz, (110, 110, 112))
    if not then:
        chips(w, c1, ztop, c2, zbot, (40, 34, 30), max(2, (c2 - c1) * (ztop - zbot) // 900), seed, (0.8, 2.2))
        for cx, cz in ((c1 + 4, zbot + 3), (c2 - 5, zbot + 3)):
            rust_run(w, cx, cz, 10 + 8 * h32(cx, cz, seed), RUST, 0.5, 1)


def ink(then):
    return INK if then else (40, 36, 34)


def plate_lines(w, spec, then, ztop, scales, pad=4, seed=0, gap=3):
    lines = spec["lines"]
    tw = max(text_width(s, sc) for s, sc in zip(lines, scales))
    hh = sum(5 * sc for sc in scales) + gap * (len(lines) - 1)
    cx = w.w // 2
    c1, c2 = cx - tw // 2 - pad - 2, cx + (tw + 1) // 2 + pad + 2
    enamel(w, max(0, c1), ztop, min(w.w, c2), ztop - hh - 2 * pad - 2, then, seed)
    write_lines(w, lines, cx, ztop - pad - 1, ink(then), scales, gap)
    return c1, c2, ztop - hh - 2 * pad - 2


def p_shelter(w, spec, then):
    plate_lines(w, spec, then, 212, (3, 2), 5, 401, 5)


def p_house(w, spec, then):
    plate_lines(w, spec, then, 162, (2,), 5, 402)


def p_plan(w, spec, then):
    c1, c2, ztop, zbot = 4, w.w - 4, 196, 36
    enamel(w, c1, ztop, c2, zbot, then, 403)
    w.centre("ANIMAL HOUSE", w.w // 2, ztop - 5, ink(then), 1)
    draw_plan(w, spec["plan"], c1 + 4, ztop - 12, c2 - 4, zbot + 4, ink(then), faint=(110, 110, 112),
              here=(30, 60, 140) if then else (40, 50, 90))


def p_gate(w, spec, then):
    z, n = spec.get("head", 128), len(spec["lines"])
    plate_lines(w, spec, then, z + (27 if n > 1 else 24), (2,) + (1,) * (n - 1), 3, 404, 2)


def p_hatch(w, spec, then):
    plate_lines(w, spec, then, 80, (1,) * len(spec["lines"]), 3, 405, 2)
    if spec.get("arrow"):
        d = spec["arrow"]
        arrow(w, w.w // 2 + d * 22, 66, d, ink(then), 3)


def p_lever(w, spec, then):
    c1, c2, zb = plate_lines(w, spec, then, 100, (2, 1), 4, 406, 3)
    d = spec.get("arrow", 0)
    if d:
        arrow(w, w.w // 2 + d * 4, zb - 8, d, (240, 240, 234) if then else (190, 184, 160), 4)
        arrow(w, w.w // 2 + d * 4, zb - 8, d, ink(then), 3)


def p_rules(w, spec, then):
    lines = spec["lines"]
    plate_lines(w, dict(spec, lines=lines), then, 122, (2,) + (1,) * (len(lines) - 1), 6, 407, 4)


def p_weigh(w, spec, then):
    plate_lines(w, spec, then, 118, (2, 1, 1, 1), 6, 408, 5)


def p_glass(w, spec, then):
    plate_lines(w, spec, then, 176, (2, 2), 4, 409, 3)


def p_keepers(w, spec, then):
    plate_lines(w, spec, then, 116, (1,), 3, 410)


def card(w, c1, ztop, lines, then, seed, width):
    """A specimen's card in a steel holder: white, black capitals."""
    hh = len(lines) * 8 + 5
    w.rect(c1 - 2, ztop + 2, c1 + width + 2, ztop - hh - 2, shade(STAIN, 0.8 if then else 0.5))
    enamel(w, c1, ztop, c1 + width, ztop - hh, then, seed, ground=(248, 248, 244))
    write_lines(w, lines, c1 + width // 2, ztop - 4, ink(then), None, 3)
    return ztop - hh - 6


def p_board(w, spec, then):
    run = RUNS[spec["run"]]
    cols = max(1, (w.w - 8) // 92)
    width = (w.w - 8) // cols - 6
    w.rect(2, 153, w.w - 2, 150, shade(STAIN, 0.8 if then else 0.55))          # the holder's rail
    z0 = 130
    enamel(w, w.w // 2 - 34, z0 + 18, w.w // 2 + 34, z0 + 6, then, 419)
    write_lines(w, ("SPECIMENS",), w.w // 2, z0 + 14, ink(then), (1,))
    for k, ident in enumerate(run["ids"]):
        col, row = k % cols, k // cols
        c1 = 4 + col * (width + 6) + 3
        ztop = z0 - row * 40
        card(w, c1, ztop, (f"SPECIMEN {ident}", f"MASS {run['mass'][k]}", "FED 0600 1800"), then, 420 + k, width)


def p_card(w, spec, then):
    run = RUNS[spec["run"]]
    lines = ("SPECIMEN",) + run["ids"] + ("FED", "0600 1800")
    card(w, 3, 52 + len(lines) * 8 + 6, lines, then, 430, w.w - 6)


PICTURES = {"shelter": p_shelter, "house": p_house, "plan": p_plan, "gate": p_gate, "hatch": p_hatch,
            "lever": p_lever, "rules": p_rules, "weigh": p_weigh, "glass": p_glass, "keepers": p_keepers,
            "board": p_board, "card": p_card}


# === sprites: steel ===============================================================================================
def s_bowl(then):
    im = sprite_img(24, 12)
    if then:
        im.rect(2, 4, 22, 11, STAIN)
        im.rect(1, 3, 23, 5, shade(STAIN, 1.12))
        im.rect(4, 10, 20, 12, shade(STAIN, 0.6))
        for x in range(4, 20, 3):                                       # meat in it
            im.disc(x + 1, 3, 1.6, (120, 62, 44))
        im.rect(3, 8, 21, 9, shade(STAIN, 0.8))
    else:                                                               # rusted, on its side
        for y in range(1, 12):
            half = int(math.sqrt(max(0, 30 - (y - 6) ** 2)))
            im.rect(12 - half - 3, y, 12 + half - 3, y + 1, mix(STAIN, RUST, 0.6 + 0.04 * y))
        im.rect(8, 4, 12, 9, (50, 40, 32))
    return im, (12, 12)


def s_bucket(then):
    im = sprite_img(28, 28)
    body = GALV if then else mix(GALV, RUST, 0.6)
    for y in range(8, 28):
        half = 8 + (27 - y) // 6
        im.rect(14 - half, y, 14 + half, y + 1, shade(body, 0.85 + 0.25 * ((y % 5) == 0)))
    im.rect(4, 8, 24, 10, shade(body, 1.2))
    for x in range(5, 24):                                            # the handle
        y = 8 - int(6 * math.sin((x - 5) / 18 * math.pi))
        im.set(x, y, shade(STEEL, 0.6))
    # the brush leaning against it
    for y in range(2, 22):
        im.set(23 + (y // 7), y, (130, 96, 60) if then else (80, 66, 50))
    im.rect(20, 20, 28, 24, (150, 110, 70) if then else (86, 70, 50))
    im.rect(20, 24, 28, 27, (200, 190, 150) if then else (70, 64, 50))
    return im, (14, 28)


def s_store(then):
    """Two galvanised bins with lids (NOW dented, one lid off)."""
    im = sprite_img(44, 40)
    for k, cx in enumerate((11, 32)):
        body = GALV if then else mix(GALV, RUST, 0.45 + 0.2 * k)
        for y in range(10, 40):
            half = 9
            im.rect(cx - half, y, cx + half, y + 1, shade(body, 0.8 + 0.3 * (y % 8 == 0) + 0.1 * math.cos((y - 10) / 9)))
        for x in range(cx - 9, cx + 9):
            im.set(x, 20, shade(body, 0.7))
            im.set(x, 32, shade(body, 0.7))
        if then or k == 0:
            im.rect(cx - 10, 7, cx + 10, 11, shade(body, 1.15))
            im.rect(cx - 2, 4, cx + 2, 7, shade(body, 0.8))
        else:
            im.rect(cx - 9, 10, cx + 9, 13, (30, 26, 22))
    if not then:
        im.rect(14, 34, 22, 38, (40, 34, 28))                          # a dent's shadow
    return im, (22, 40)


SPRITES = {"bowl": s_bowl, "bucket": s_bucket, "store": s_store}
