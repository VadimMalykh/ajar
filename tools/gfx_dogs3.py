"""MAP23's look 3, "The Kennels" (kept animals; a working kennel and stable yard): art only, the slots of
tools/gfx_dogs.py (read its docstring first; tools/gfx_dogs1.py is the model).

THEN: a black tarred dado to 48 under whitewashed brick (the courses showing through the lime) in the runs, the
passages and the hall; creosoted upright boards to 96 in the pens over an iron kicking plate, whitewash above;
blue-grey brick paviours with a dished gutter in the runs, straw over paviours in the pens, trowelled concrete in
the passages; gates of planks, ledged and braced, tarred at the foot, black iron strap hinges and a bolt; hatch
surrounds of oak with an iron lip. The yard: granite setts, whitewashed walls on a tarred base with piers and a
blue brick coping, the house's front with a row of small black-framed windows and a black-painted door surround,
the shelter of black weatherboard under a row of slates. Lettering: slates in thin oak frames, white chalk
capitals, a little uneven, a smudge here and there; the runs' boards chalk the animals' names with a tick by each.
NOW: the whitewash green with algae from the floor up and grey above, fallen in patches to the brick; the boards
rotted through at the foot, some gone; the straw black and thin, the paviours heaved; the slates cracked, the chalk
half rubbed off; the tar dull. Drawn a little lighter than it would be, to read at light 120.
"""
import math
import random

from gfx_dogs import (RUNS, Img, arrow, draw_plan, flat, h32, mix, rust_run, shade, sprite_img, text_width)
from gfx import text

# --- the palette ------------------------------------------------------------------------------------------------
TAR = (27, 26, 25)
TAR_N = (68, 66, 62)              # dull, and lighter for the night
WASH = (232, 230, 220)            # whitewash (lime over brick)
WASH_N = (178, 180, 168)          # grey with forty years
ALGAE = (98, 128, 70)
BRICK = (128, 108, 94)            # the brick under the lime (a dull grey-brown: never door red, never blood)
MORTAR = (162, 156, 142)
CREO = (70, 50, 34)               # creosoted boards
CREO_N = (104, 88, 68)
PEN_N = (158, 144, 122)           # the pens' boards NOW: grey timber, lighter, to read at 120 from the run
WOOD = (122, 94, 64)              # the gates' planks
WOOD_N = (128, 118, 102)
OAK = (158, 126, 86)              # frames, hatch surrounds
IRON = (40, 42, 46)
IRON_HI = (88, 92, 98)
RUST = (128, 72, 40)
SLATE = (58, 64, 74)
SLATE_N = (86, 92, 102)
CHALK = (238, 238, 230)
CHALK_Y = (236, 214, 120)         # a stick of yellow chalk (YOU ARE HERE)
PAVE = (82, 92, 108)              # blue brick paviours
PAVE_N = (104, 110, 120)
JOINT = (46, 50, 58)
STRAW = (214, 182, 92)
SETT = (112, 118, 128)
CONC = (178, 176, 168)
BLUEDOOR = (78, 96, 116)          # the front door's paint: blue-grey
DARK = (14, 12, 12)


def jt(c, x, z, s, a):
    return shade(c, 1 + (h32(x, z, s) - 0.5) * 2 * a)


def vn(x, z, s, cell):
    """Smooth value noise in [0, 1): h32 on a grid of `cell`, eased between (for patches with soft edges)."""
    gx, gz = x / cell, z / cell
    ix, iz = math.floor(gx), math.floor(gz)
    fx, fz = gx - ix, gz - iz
    fx, fz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a = h32(ix, iz, s) + (h32(ix + 1, iz, s) - h32(ix, iz, s)) * fx
    b = h32(ix, iz + 1, s) + (h32(ix + 1, iz + 1, s) - h32(ix, iz + 1, s)) * fx
    return a + (b - a) * fz


def patch(x, z, s, cell=14):
    """A patch's measure: low where something has fallen away (rough at the edge)."""
    return vn(x, z, s, cell) * 0.88 + h32(x // 3, z // 3, s + 1) * 0.12


# === the surfaces, by absolute height ==========================================================================
def course(x, z, length=32, high=8):
    """Stretcher bond by absolute height: (course, x along the brick, row within the course; 0 the joint)."""
    row = (z - 1) // high
    return row, (x + (length // 2 if row % 2 else 0)) % length, (z - 1) % high


def raw_brick(x, z, s):
    row, bx, bz = course(x, z)
    if bz == 0 or bx == 0:
        return jt(MORTAR, x, z, s, 0.08)
    return jt(BRICK, (x + 16 * (row % 2)) // 32, row, s, 0.14)


def wash(x, z, then, seed, floor=48, fallen=0.22):
    """Whitewash on brick: the courses show (a joint's shadow, the brick's face a shade apart). NOW: grey with
    streaks, green with algae from `floor` up, fallen in patches to the brick."""
    row, bx, bz = course(x, z)
    if not then:
        if patch(x, z, seed + 1) < fallen:
            return raw_brick(x, z, seed + 3)
    if bz == 0 or bx == 0:
        c = shade(WASH, 0.82)
    else:
        c = jt(WASH, (x + 16 * (row % 2)) // 32 * 7 + row, row, seed, 0.03)
        c = jt(c, x, z, seed + 4, 0.018)
        if bz == 7:
            c = shade(c, 1.03)
        elif bz == 1:
            c = shade(c, 0.94)
    if then:
        return c
    c = mix(c, WASH_N, 0.55)
    if h32(x // 2, z // 48, seed + 5) < 0.22:
        c = shade(c, 0.86)                                          # streaks down from the top
    lim = floor + 34 + 50 * h32(x // 6, 0, seed + 6)
    if z < lim:
        f = 1 - (z - floor) / (lim - floor)
        c = mix(c, ALGAE, min(0.75, 0.15 + 0.6 * f * (0.7 + 0.3 * h32(x, z, seed + 7))))
    return c


def tar(x, z, then, seed, top=48):
    """The tarred dado: black, a brush's streaks; its top one straight line. NOW dull and grey-black."""
    if then:
        c = jt(TAR, x, z, seed, 0.12)
        if h32(x // 7, z, seed + 1) < 0.06:
            c = (52, 50, 48)                                        # the brush's gloss
        if z == top:
            c = (12, 12, 12)
        return c
    c = jt(TAR_N, x, z, seed, 0.12)
    c = mix(c, (118, 120, 108), 0.25 * h32(x // 4, z // 3, seed + 2))    # the bloom
    if z < 8 + 10 * h32(x // 5, 0, seed + 3):
        c = mix(c, ALGAE, 0.16)
    if z == top:
        c = shade(c, 0.6)
    return c


def boards_v(x, z, then, seed, base=CREO, width=8):
    """Upright boards, `width` wide, a dark gap between; the grain along them."""
    k = x // width
    if x % width == 0:
        return (20, 15, 11) if then else (40, 34, 28)
    c = jt(base, k, 0, seed, 0.08)
    c = jt(c, x, z // 7, seed + 1, 0.05)
    if x % width == width - 1:
        c = shade(c, 0.85)
    return c


def wood_now(c, x, z, seed, rot=40, floor=0):
    """Timber forty years on: grey, rotted through to the dark in holes at its foot."""
    c = mix(c, (132, 124, 110), 0.45)
    if z < floor + rot:
        f = 1 - (z - floor) / rot
        if vn(x, z, seed, 5) * 0.85 + h32(x // 2, z // 2, seed + 2) * 0.15 < 0.62 * f * (0.3 + 0.9 * h32(x // 8, 1, seed + 1)):
            return DARK
        c = mix(c, (50, 44, 36), 0.35 * f)
    return c


def iron(x, z, then, seed):
    c = jt(IRON, x // 2, z // 2, seed, 0.1)
    return c if then else mix(jt((96, 90, 84), x, z, seed, 0.1), RUST, 0.45 + 0.35 * h32(x // 3, z // 3, seed + 1))


# === walls =====================================================================================================
def runs_wall(w, then):
    """Tar to 48, whitewashed brick over it; an iron air brick at 136..144 every 64 (rust runs from it NOW)."""
    def fn(x, z):
        if z <= 48:
            return tar(x, z, then, 11)
        if 136 < z <= 144 and 24 <= x < 40:
            if x in (24, 39) or z in (137, 144):
                return iron(x, z, then, 12)
            return DARK if (x - 24) % 3 == 0 else iron(x, z, then, 12)
        return wash(x, z, then, 13)
    w.fill(w.z0, w.bot, fn)
    if not then:
        for c in range(w.w):
            if (w.shift + c) % 64 in (27, 34):
                rust_run(w, c, 136, 12 + 8 * h32((w.shift + c) % 64, 1, 14), (100, 82, 64), 0.4, 1)


def passage_wall(w, then):
    """Tar to 48, whitewash over it; an iron hook every 64 at 88..96."""
    def fn(x, z):
        if z <= 48:
            return tar(x, z, then, 51)
        return wash(x, z, then, 52)
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        if (w.shift + c) % 64 == 40:
            col = IRON if then else shade(RUST, 1.1)
            w.rect(c - 1, 97, c + 2, 94, col)                          # the plate
            w.rect(c, 94, c + 1, 86, col)
            w.rect(c, 87, c + 4, 86, col)
            w.rect(c + 3, 89, c + 4, 86, col)
            if not then:
                rust_run(w, c, 93, 22, RUST, 0.45, 1)


def hall_wall(w, then):
    """The harness room's hall: tar to 48, whitewash, an oak peg rail at 116..124, its pegs every 16."""
    def fn(x, z):
        if z <= 48:
            return tar(x, z, then, 41)
        if 116 < z <= 124:
            c = jt(OAK, x, z // 3, 42, 0.05)
            if z in (117, 124):
                c = shade(c, 0.75)
            if not then:
                c = wood_now(c, x, 200, 43)
                if h32(x // 21, 0, 44) < 0.3:
                    return wash(x, z, then, 45)                     # the rail gone there
            return c
        return wash(x, z, then, 45)
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        if xw % 16 == 8 and (then or h32(xw, 3, 46) < 0.5):
            col = shade(OAK, 1.15) if then else (120, 110, 94)
            w.rect(c - 1, 116, c + 2, 112, col)
            w.at(c - 1, 112, shade(col, 0.6))


def pens_wall(w, then):
    """An iron kicking plate to 12, creosoted upright boards to 96, a capping rail to 102, whitewash above.
    NOW: the plate rusted, the boards grey and rotted through at the foot, here and there one gone to the brick."""
    def fn(x, z):
        if z <= 12:
            c = iron(x, z, then, 21)
            if z == 12:
                c = shade(c, 1.6)
            return c
        if z <= 96:
            c = boards_v(x, z, then, 22)
            if not then:
                if h32(x // 8, 5, 23) < 0.1:
                    return raw_brick(x, z, 24)                       # a board gone
                c = wood_now(mix(c, PEN_N, 0.6), x, z, 25, 34, 12)
            return c
        if z <= 102:
            c = jt(CREO, x, z, 26, 0.05)
            if z == 102:
                c = shade(c, 1.25)
            elif z == 97:
                c = (18, 14, 10)
            return c if then else wood_now(mix(c, PEN_N, 0.6), x, z, 27, 0)
        return wash(x, z, then, 28, floor=102, fallen=0.2)
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        if (w.shift + c) % 16 == 8:
            w.at(c, 6, IRON_HI if then else (150, 100, 64))         # the plate's bolts


def ledge_face(w, then):
    """NOW: the pen's wall's lowest 48 rows: the boards broken off at ragged heights, the brick behind them."""
    pens_wall(w, then)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        top = 36 + int(8 * h32(xw // 8, 1, 31)) + int(2 * h32(xw, 2, 32))
        for z in range(top + 1, 49):
            w.at(c, z, raw_brick(xw, z, 33))
        w.at(c, top, (170, 150, 120))                                # the splintered end
        w.at(c, 48, shade(MORTAR, 0.7))


def plank_gate(x, z, then, seed, ledges, base=WOOD, foot=48):
    """A plank gate, ledged and braced: upright planks, ledges across, a brace rising from hinge to latch
    between each pair of ledges; tarred to `foot`. (The straps, the bolt: strap_hinges.)"""
    c = boards_v(x, z, then, seed, base)
    for k, (a, b) in enumerate(ledges):
        if a < z <= b:
            c = jt(shade(base, 1.1), x, z // 4, seed + 2, 0.04)
            if z in (a + 1, b):
                c = shade(c, 0.7 if z == a + 1 else 1.15)
            break
    else:
        for (a1, b1), (a2, b2) in zip(ledges, ledges[1:]):
            if b1 < z <= a2:
                zc = b1 + (x - 4) * (a2 - b1) / 56
                d = z - zc
                if 4 <= x <= 60 and abs(d) <= 4:
                    c = jt(shade(base, 1.06), x, z // 4, seed + 3, 0.04)
                    if abs(d) > 3.2:
                        c = shade(c, 0.7)
    if z <= foot:
        t = tar(x, z, then, seed + 4, foot)
        c = shade(t, 0.55) if x % 8 == 0 else t
    if not then and z > foot:
        c = wood_now(mix(c, WOOD_N, 0.5), x, z, seed + 5, 30, foot)
    return c


def strap_hinges(w, then, zs, reach=44):
    """Black iron strap hinges from each gate's hinge side (x 0) along its ledges; their bolts; a bolt."""
    col = IRON if then else (112, 80, 58)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        for zc in zs:
            if xw <= reach:
                t = 2 if xw < reach - 10 else 1 + (reach - xw) // 6
                w.rect(c, zc + t, c + 1, zc - t - 1, col)
                if xw % 10 == 6:
                    w.at(c, zc, shade(col, 1.9))
            if xw in (0, 1):
                w.rect(c, zc + 4, c + 1, zc - 5, shade(col, 0.7))           # the knuckle
    if not then:
        for c in range(w.w):
            xw = (w.shift + c) % 64
            if xw in (12, 30):
                for zc in zs:
                    rust_run(w, c, zc - 3, 14, RUST, 0.5, 1)


def bolt(w, then, zc):
    col = IRON if then else (112, 80, 58)
    for c in range(w.w):
        xw = (w.shift + c) % 64
        if 46 <= xw <= 62:
            w.rect(c, zc + 2, c + 1, zc - 2, col)                          # the bolt's barrel
        if xw in (52, 53):
            w.rect(c, zc + 6, c + 1, zc + 1, col)                          # its knob
        if xw in (47, 61):
            w.rect(c, zc + 4, c + 1, zc - 4, shade(col, 1.6))              # its staples


GL_LEDGES = ((12, 22), (66, 76), (120, 130), (174, 184))


def gate_leaf(w, then):
    """A gate's leaf: a plank gate, ledged and braced, tarred to 48, strap hinges, a bolt at 92."""
    w.fill(w.z0, w.bot, lambda x, z: plank_gate(x, z, then, 121, GL_LEDGES))
    strap_hinges(w, then, [(a + b) // 2 for a, b in GL_LEDGES[1:]])
    bolt(w, then, 92)


def gate_reveal(w, then):
    """A gate's jamb: an oak post, tarred to 48, an iron guide down its middle; NOW grey, the iron rusted."""
    def fn(x, z):
        if z <= 48:
            c = tar(x, z, then, 131)
        else:
            c = jt(OAK, x // 2, z // 6, 132, 0.05)
            c = shade(c, 0.75) if x % 16 in (0, 15) else c
            if not then:
                c = wood_now(c, x, z, 133, 24, 48)
        if x % 16 in (6, 7, 8, 9):
            c = iron(x, z, then, 134)
            if x % 16 == 6:
                c = shade(c, 1.5)
        return c
    w.fill(w.z0, w.bot, fn)


def hatch_surround(w, then):
    """A hatch's surround: tar to 20 under it, an iron lip 20..24 (the sill's edge), oak jambs 24..56, an oak
    head 56..66 with its iron lip at 56..58, whitewash over it."""
    def fn(x, z):
        if z <= 20:
            return tar(x, z, then, 141, 20)
        if z <= 24:
            c = iron(x, z, then, 142)
            return shade(c, 1.7) if z == 24 else c
        if z <= 66:
            if z <= 58 and z > 56:
                c = iron(x, z, then, 143)
                return shade(c, 1.4) if z == 57 else c
            c = jt(OAK, x // 2, z // 5, 144, 0.06)
            if z in (66, 59):
                c = shade(c, 0.7)
            return c if then else wood_now(c, x, z, 145, 0)
        return wash(x, z, then, 146, floor=66)
    w.fill(w.z0, w.bot, fn)
    for c in range(w.w):
        if (w.shift + c) % 16 == 8:
            w.at(c, 62, IRON if then else RUST)
            w.at(c, 22, IRON_HI if then else (150, 100, 64))


def turnstile_jamb(w, then):
    """A turnstile's jamb: an oak post, tarred to 48, black iron bands; NOW a rotted stump of it."""
    def fn(x, z):
        if z <= 48:
            c = tar(x, z, then, 151)
        else:
            c = jt(OAK, x // 2, z // 6, 152, 0.05)
            c = shade(c, 0.8 + 0.3 * abs(math.sin(x * 0.2)))
        if z % 24 in (0, 1, 2, 3) and z > 48:
            c = iron(x, z, then, 153)
        if not then and z > 48:
            c = wood_now(c, x, z, 154, 20, 48)
            if z > 66 + 18 * h32(x // 4, 0, 155):
                c = mix(c, (60, 52, 44), 0.5)
        return c
    w.fill(w.z0, w.bot, fn)


# --- the yard ---------------------------------------------------------------------------------------------------
def coping(x, z, then, seed):
    """Blue bricks on edge."""
    if x % 6 == 0 or z == 244:
        return jt(JOINT, x, z, seed, 0.1) if then else jt((96, 98, 100), x, z, seed, 0.1)
    c = jt(PAVE, x // 6, 0, seed, 0.1)
    if z == 256:
        c = shade(c, 1.25)
    return c if then else mix(c, (140, 144, 140), 0.35)


def window(x, z, then, seed, x1=20, x2=44, z1=200, z2=232):
    """A small stable window: a black frame, four panes, a slate sill under it. None outside it."""
    xm = x % 64
    if z1 - 3 < z <= z1 and x1 - 2 <= xm < x2 + 2:
        return jt(SLATE if then else SLATE_N, x, z, seed, 0.05) if z < z1 else shade(SLATE, 1.5)
    if not (z1 < z <= z2 and x1 <= xm < x2):
        return None
    if xm in (x1, x1 + 1, x2 - 2, x2 - 1, (x1 + x2) // 2) or z in (z1 + 1, z1 + 2, z2, z2 - 1, (z1 + z2) // 2):
        return (22, 22, 22) if then else (70, 68, 64)
    if then:
        g = shade((70, 88, 104), 1 + 0.4 * ((xm - x1) + (z - z1)) / 56)
        if (xm - x1) - (z - z1) // 2 in (4, 5):
            g = shade(g, 1.4)
        return g
    if h32(xm // 12, z // 16, seed + 1) < 0.6:
        return (10, 10, 12) if h32(x, z, seed + 2) < 0.85 else (96, 104, 110)
    return (60, 70, 76)


def yard_front(w, then):
    """The house's front: tar to 48, whitewashed brick, a row of small black-framed windows (200..232), the
    blue brick coping (244..256)."""
    def fn(x, z):
        if z <= 48:
            return tar(x, z, then, 61)
        if z > 244:
            return coping(x, z, then, 62)
        if z == 244:
            return coping(x, z, then, 62)
        c = window(x, z, then, 63)
        return c if c is not None else wash(x, z, then, 64)
    w.fill(w.z0, w.bot, fn)


def pier(x, z, c):
    """A pier every 64: the wall's face steps out (its edges lit and shaded)."""
    xm = x % 64
    if xm == 0:
        return shade(c, 0.72)
    if xm == 1:
        return shade(c, 1.08)
    if xm == 15:
        return shade(c, 0.85)
    return c


def yard_wall(w, then):
    """The yard's other walls: tar to 48, whitewashed brick with piers every 64, the blue brick coping."""
    def fn(x, z):
        if z >= 244:
            return coping(x, z, then, 71)
        c = tar(x, z, then, 72) if z <= 48 else wash(x, z, then, 73)
        return pier(x, z, c)
    w.fill(w.z0, w.bot, fn)


def shelter_mass(w, then):
    """The shelter: a black fascia (112..120), black weatherboard (120..232), a row of slates (232..256)."""
    def fn(x, z):
        if z <= 120:
            c = jt((30, 30, 30) if then else (82, 80, 76), x, z, 81, 0.06)
            return shade(c, 1.6) if z <= 113 else c
        if z <= 232:
            b = (z - 121) % 14
            base = (58, 56, 54) if then else (100, 98, 92)
            c = jt(base, x // 16 + (z - 121) // 14 * 5, 0, 82, 0.08)
            c = jt(c, x, z // 3, 83, 0.03)
            if b == 0:
                c = (6, 6, 6) if then else (40, 38, 36)                  # the lap's shadow
            elif b == 1:
                c = shade(c, 0.6)
            elif b == 13:
                c = shade(c, 1.7)
            elif b == 12:
                c = shade(c, 1.3)
            if not then and h32(x // 24, (z - 121) // 14, 84) < 0.08:
                c = DARK                                                # a board gone
            return c
        row = (z - 233) // 8
        sx = (x + (6 if row % 2 else 0)) % 12
        if sx == 0 or (z - 233) % 8 == 0:
            return JOINT if then else (70, 74, 80)
        c = jt(SLATE if then else SLATE_N, (x + 6 * (row % 2)) // 12, row, 85, 0.1)
        if not then and h32((x + 6 * (row % 2)) // 12, row, 86) < 0.12:
            c = (16, 16, 18)                                            # a slate slipped
        return c
    w.fill(w.z0, w.bot, fn)


def sill(w, then):
    """A slate sill (0..8); black-painted timber to 148 (the glass's frame, the front door's reveal); whitewash
    over it."""
    def fn(x, z):
        if z <= 8:
            c = jt(SLATE if then else SLATE_N, x, z, 91, 0.05)
            return shade(c, 1.4) if z == 8 else c
        if z <= 148:
            c = jt((24, 24, 24), x, z // 4, 92, 0.1)
            if z == 148:
                c = (60, 60, 60)
            if not then:
                c = jt((76, 74, 70), x, z // 4, 92, 0.1)
                if patch(x, z, 93, 10) < 0.35:
                    c = jt((126, 116, 100), x, z, 94, 0.05)             # the paint flaked to the timber
            return c
        return wash(x, z, then, 95)
    w.fill(w.z0, w.bot, fn)


GW_LEDGES = ((12, 22), (82, 92), (154, 164))


def gateway(w, then):
    """The big run's gateway THEN, shut: a pair of plank gates (0..176), ledged and braced, tarred to 48, strap
    hinges; a black beam over it (176..186), whitewash above."""
    def fn(x, z):
        if z > 186:
            return wash(x, z, then, 101)
        if z > 176:
            c = jt((28, 28, 28), x, z, 102, 0.08)
            return shade(c, 2) if z == 177 else c
        return plank_gate(x, z, then, 103, GW_LEDGES)
    w.fill(w.z0, w.bot, fn)
    strap_hinges(w, then, [(a + b) // 2 for a, b in GW_LEDGES[1:]], 48)
    bolt(w, then, 120)


def house_door(w, then):
    """The front door THEN (64 x 128): a blue-grey stable door in two halves, matchboarded, black strap hinges,
    a thumb latch and a padlocked hasp ('Locked for the night'), in its black surround."""
    def fn(x, z):
        if x < 4 or x >= 60 or z > 123:
            return jt((24, 24, 24), x, z, 111, 0.08)
        c = jt(BLUEDOOR, x // 8, 0, 112, 0.03)
        c = jt(c, x, z // 6, 113, 0.025)
        if (x - 4) % 8 == 0:
            c = shade(c, 0.66)                                        # the matchboards' V
        if 62 <= z <= 66:
            c = shade(BLUEDOOR, 1.15 if z == 66 else 0.8)             # the halves' meeting rail
        if z <= 4:
            c = shade(BLUEDOOR, 0.7)
        return c
    w.fill(w.z0, w.bot, fn)
    for zc in (24, 104):                                              # the straps
        w.rect(4, zc + 2, 40, zc - 2, IRON)
        w.rect(40, zc + 1, 44, zc - 1, IRON)
        for c in (10, 20, 30):
            w.at(c, zc, IRON_HI)
    w.rect(48, 74, 50, 58, IRON)                                      # the latch's handle
    w.rect(46, 75, 52, 73, IRON)
    w.rect(46, 59, 52, 57, IRON)
    w.rect(50, 86, 58, 82, IRON)                                      # the hasp, its padlock
    w.rect(52, 82, 57, 75, (54, 56, 60))
    w.frame(52, 82, 57, 75, IRON, 1)


WALLS = {"YF": yard_front, "YW": yard_wall, "SM": shelter_mass, "SL": sill, "GW": gateway, "HD": house_door,
         "HW": hall_wall, "RW": runs_wall, "PW": pens_wall, "LF": ledge_face, "GL": gate_leaf, "GR": gate_reveal,
         "HS": hatch_surround, "KW": passage_wall, "TS": turnstile_jamb}


# === flats =====================================================================================================
def setts(then):
    """Granite setts, 16 by 8, staggered, domed, dark joints; NOW moss in the joints, some gone to the earth."""
    def fn(x, y):
        row = y // 8
        off = 8 if row % 2 else 0
        sx, sy = (x + off) % 16, y % 8
        k = ((x + off) // 16, row)
        if sx == 0 or sy == 0:
            if not then and h32(x, y, 201) < 0.55:
                return jt((70, 96, 52), x, y, 202, 0.15)
            return jt((40, 42, 46), x, y, 203, 0.1)
        if not then and h32(k[0], k[1], 204) < 0.06:
            return jt((70, 60, 48), x, y, 205, 0.15)                   # a sett gone: the earth
        c = jt(SETT, k[0] * 3, k[1], 206, 0.12)
        c = mix(c, (130, 118, 104), 0.3 * h32(k[0], k[1], 207))
        f = 1 - 0.18 * (((sx - 8) / 8) ** 2 + ((sy - 4) / 4) ** 2)
        if sx + sy < 6:
            f += 0.06
        c = shade(jt(c, x, y, 208, 0.04), f)
        if not then:
            c = shade(mix(c, (128, 130, 124), 0.2), 0.8 + 0.35 * h32(k[0], k[1], 209))     # heaved
        return c
    return flat(fn)


def rafters(then, seed=211, boards=(128, 108, 82), wash_it=False):
    """A lean-to's underside: creosoted rafters every 16 (along y), boards across them."""
    def fn(x, y):
        if x % 16 < 4:
            c = jt(CREO, x, y // 4, seed, 0.06)
            c = shade(c, 1.3) if x % 16 == 0 else c
            return c if then else mix(c, (90, 80, 66), 0.4)
        base = WASH if wash_it else boards
        c = jt(base, x // 16, y // 8, seed + 1, 0.06 if not wash_it else 0.03)
        if y % 8 == 0:
            c = shade(c, 0.8)
        if not then:
            c = mix(c, (110, 106, 96), 0.4)
            if h32(x // 16, y // 8, seed + 2) < 0.12:
                return (10, 10, 12)                                     # a board gone: the dark above
            c = mix(c, (70, 66, 52), 0.3 * h32(x // 5, y // 5, seed + 3))
        return c
    return flat(fn)


def sill_top(then):
    def fn(x, y):
        c = jt(SLATE if then else SLATE_N, x, y // 3, 221, 0.05)
        return shade(c, 1.15) if y % 21 == 0 else c
    return flat(fn)


def hall_floor(then):
    """A brick floor in basket weave (blue brick, brindled); NOW (the hall is NOW only) dirt, cracks, a brick gone."""
    def fn(x, y):
        cx, cy = x // 16, y // 16
        u, v = x % 16, y % 16
        if (cx + cy) % 2:
            k, joint = (cx, cy, v // 8), (u == 0 or v % 8 == 0)
        else:
            k, joint = (cx, cy, u // 8 + 2), (v == 0 or u % 8 == 0)
        if joint:
            return jt((70, 68, 66) if then else (96, 92, 86), x, y, 231, 0.08)
        kk = k[0] * 7 + k[1] * 3 + k[2]
        c = jt((88, 88, 100), kk, 0, 232, 0.1)
        c = mix(c, (120, 94, 80), 0.45 * h32(kk, 1, 233))
        c = jt(c, x, y, 234, 0.04)
        if not then:
            c = mix(c, (118, 112, 100), 0.3)
            if h32(kk, 2, 235) < 0.05:
                return jt((60, 52, 44), x, y, 236, 0.1)
            if abs(math.sin(x * 0.17 + 2 * math.sin(y * 0.11))) < 0.04:
                c = (40, 38, 36)
            c = mix(c, (96, 86, 64), 0.25 * h32(x // 6, y // 6, 237))
        return c
    return flat(fn)


def plain_boards(then, seed, joist=32, base=WASH):
    """A ceiling of whitewashed boards on tarred joists every `joist`; NOW grey, stained, boards gone."""
    def fn(x, y):
        if x % joist < 5:
            c = jt((36, 34, 32), x, y // 4, seed, 0.08)
            if x % joist == 0:
                c = shade(c, 1.6)
            return c if then else jt((86, 82, 76), x, y // 4, seed, 0.08)
        c = jt(base, x // joist, y // 8, seed + 1, 0.025)
        if y % 8 == 0:
            c = shade(c, 0.86)
        if not then:
            c = mix(c, (150, 150, 138), 0.5)
            c = mix(c, (100, 92, 70), 0.35 * h32(x // 7, y // 7, seed + 2))
            if h32(x // joist, y // 8, seed + 3) < 0.1:
                return (10, 10, 12)
        return c
    return flat(fn)


def run_floor(then):
    """Blue brick paviours (16 by 8, chequered in four), 128; a dished gutter along x at y 56..72; NOW heaved,
    moss in the joints, muck in the gutter."""
    def fn(x, y):
        if 56 <= y < 72:
            d = abs(y - 63.5) / 8
            if x % 16 == 0:
                c = JOINT
            else:
                c = shade(jt(PAVE if then else PAVE_N, x // 16, 99, 251, 0.08), 0.62 + 0.4 * d)
                if then and y in (63, 64) and x % 7 < 4:
                    c = shade(c, 1.5)                                   # wet
            if not then and d < 0.55:
                c = mix(c, (52, 44, 34), 0.7)
            return c
        row = y // 8
        off = 8 if row % 2 else 0
        sx, sy = (x + off) % 16, y % 8
        k = ((x + off) // 16, row)
        if sx == 0 or sy == 0:
            if not then and h32(x, y, 252) < 0.5:
                return jt((76, 102, 56), x, y, 253, 0.15)
            return JOINT if then else (66, 70, 76)
        c = jt(PAVE if then else PAVE_N, k[0] * 5, k[1], 254, 0.08)
        if sx == 8 or sy == 4:
            c = shade(c, 0.84)                                         # the chequer's grooves
        c = jt(c, x, y, 255, 0.03)
        if not then:
            c = shade(c, 0.84 + 0.26 * h32(k[0], k[1], 256))
            if h32(k[0], k[1], 257) < 0.08 and abs(sx - 2 - sy * 1.5) < 0.6:
                c = (40, 40, 42)                                        # a cracked paviour
        return c
    return flat(fn, 128)


def _strands(im, n, seed, cols, size, ln=(4, 9)):
    r = random.Random(seed)
    for _ in range(n):
        x0, y0 = r.uniform(0, size), r.uniform(0, size)
        a = r.uniform(0, math.pi)
        L = r.uniform(*ln)
        col = r.choice(cols)
        for i in range(int(L * 2)):
            x = int(x0 + math.cos(a) * i / 2) % size
            y = int(y0 + math.sin(a) * i / 2) % size
            im.set(x, y, col)


def straw_floor(then, size=64, seed=271):
    """Straw over paviours: thick and yellow, the paviours showing where it is trodden thin; NOW black and thin
    over heaved paviours."""
    def base(x, y):
        row = y // 8
        off = 8 if row % 2 else 0
        if (x + off) % 16 == 0 or y % 8 == 0:
            c = JOINT if then else (64, 66, 70)
        else:
            c = jt(PAVE if then else PAVE_N, (x + off) // 16 * 5, row, seed, 0.08)
            if not then:
                c = shade(c, 0.78 + 0.18 * h32((x + off) // 16, row, seed + 1))
        thin = vn(x, y, seed + 2, 16) * 0.85 + h32(x // 2, y // 2, seed + 5) * 0.15 < (0.28 if then else 0.36)
        if not thin:
            c = jt((150, 118, 52), x, y, seed + 3, 0.15) if then else jt((70, 62, 46), x, y, seed + 3, 0.15)
        return c
    im = flat(base, size)
    if then:
        _strands(im, 15 * size, seed + 4, [(222, 190, 98), (196, 160, 74), (238, 214, 132), (176, 140, 60),
                                           (230, 200, 110)], size)
    else:
        _strands(im, 6 * size, seed + 4, [(66, 58, 44), (88, 78, 56), (54, 48, 38), (104, 94, 68)], size)
    return im


def weigh_plate(then):
    """Pen 1's floor: an oak platform 240 by 256 (columns 0..240) in an iron frame, iron straps across at every
    64, four bolts; straw blown on it."""
    def fn(x, y):
        if x >= 240:
            return (30, 30, 30)
        if x < 6 or x >= 234 or y < 6 or y >= 250:
            c = iron(x, y, then, 281)
            if x in (5, 234) or y in (5, 250):
                c = shade(c, 1.6)
            return c
        if (y - 6) % 61 < 4 and 6 < y < 248:
            return shade(iron(x, y, then, 282), 1.3 if (y - 6) % 61 == 0 else 1)
        c = jt(OAK, (x - 6) // 16, 0, 283, 0.08)
        c = jt(c, x, y // 6, 284, 0.04)
        if (x - 6) % 16 == 0:
            c = (40, 30, 22)
        if not then:
            c = wood_now(c, x, 999, 285)
            if h32((x - 6) // 16, y // 20, 286) < 0.04:
                c = DARK
        return c
    im = flat(fn, 256)
    for cx, cy in ((12, 12), (228, 12), (12, 244), (228, 244)):
        im.disc(cx, cy, 3, IRON_HI if then else (140, 96, 64))
    r = random.Random(287)
    cols = [(222, 190, 98), (196, 160, 74)] if then else [(70, 62, 46), (90, 80, 58)]
    for _ in range(180):
        x0, y0, a = r.uniform(8, 230), r.uniform(8, 246), r.uniform(0, math.pi)
        col = r.choice(cols)
        for i in range(r.randint(6, 14)):
            im.set(int(x0 + math.cos(a) * i / 2), int(y0 + math.sin(a) * i / 2), col)
    return im


def rubble(then):
    """NOW: a ledge's top: broken board ends, brick and mortar, black straw."""
    def fn(x, y):
        r = h32(x // 4, y // 4, 291)
        if r < 0.35:
            return jt(BRICK, x, y, 292, 0.15)
        if r < 0.55:
            return jt((120, 104, 84), x // 2, y // 6, 293, 0.12)         # board ends
        if r < 0.8:
            return jt(MORTAR, x, y, 294, 0.1)
        return (54, 48, 40)
    im = flat(fn)
    _strands(im, 60, 295, [(64, 58, 44), (86, 78, 56)], 64)
    return im


def gate_top(then, seed=301):
    """A gate's and a hatch's head and sill: oak boards along x, an iron lip along each edge (every 16)."""
    def fn(x, y):
        if y % 16 in (0, 15):
            c = iron(x, y, then, seed)
            return shade(c, 1.4) if y % 16 == 0 else c
        c = jt(OAK, 0, y // 5, seed + 1, 0.06)
        c = jt(c, x // 3, y, seed + 2, 0.03)
        if y % 16 in (5, 10):
            c = shade(c, 0.7)
        return c if then else wood_now(c, x, 999, seed + 3)
    return flat(fn)


def concrete(then):
    """Plain trowelled concrete: the trowel's arcs faint in it, a sawn joint every 64; NOW cracked, damp."""
    def fn(x, y):
        if x == 0 or y == 0:
            return (120, 118, 112) if then else (100, 98, 92)
        c = jt(CONC, x, y, 311, 0.03)
        best = min(math.hypot(x - cx - 10 * h32(cx, cy, 314), y - cy - 10 * h32(cy, cx, 315))
                   for cx in (0, 32, 64) for cy in (0, 32, 64))
        c = shade(c, 1 + 0.014 * math.sin(best * 0.5 + 3 * vn(x, y, 316, 24)))
        if not then:
            c = mix(c, (150, 148, 138), 0.2)
            if abs(math.sin(x * 0.09 + 2.5 * math.sin(y * 0.07))) < 0.035:
                c = (52, 50, 46)
            c = mix(c, (80, 82, 66), 0.35 * h32(x // 9, y // 9, 312))
        return c
    im = flat(fn)
    if not then:
        _strands(im, 30, 313, [(70, 62, 46), (90, 80, 58)], 64)
    return im


FLATS = {"YG": setts, "SC": rafters, "SF": sill_top, "HF": hall_floor,
         "HC": lambda then: plain_boards(then, 241, 32), "RF": run_floor,
         "RC": lambda then: plain_boards(then, 261, 32), "PF": straw_floor, "WP": weigh_plate,
         "PC": lambda then: rafters(then, 331, wash_it=True), "LT": rubble, "GT": gate_top,
         "KF": concrete, "KK": lambda then: plain_boards(then, 321, 64), "TF": lambda then: gate_top(then, 341)}


# === pictures: slates in thin oak frames, white chalk capitals ===================================================
def slate(w, c1, ztop, c2, zbot, then, seed, fw=2):
    """A slate in a thin oak frame (covering heights zbot < z <= ztop); a smudge or two of old chalk; NOW cracked."""
    fr = OAK if then else (138, 126, 106)
    w.rect(c1, ztop, c2, zbot, fr)
    w.frame(c1, ztop, c2, zbot, shade(fr, 0.62), 1)
    w.rect(c1 + 1, ztop - 1, c2 - 1, ztop - 2, shade(fr, 1.18))
    sc = SLATE if then else SLATE_N
    for c in range(c1 + fw, c2 - fw):
        for z in range(zbot + fw + 1, ztop - fw + 1):
            col = jt(sc, c // 2, z // 2, seed, 0.05)
            if (c + 2 * z) % 37 == 0:
                col = shade(col, 1.08)
            w.at(c, z, col)
    r = random.Random(seed)
    for _ in range(max(1, (c2 - c1) // 50)):
        smudge(w, r.uniform(c1 + 8, c2 - 8), r.uniform(zbot + 6, ztop - 6), r.uniform(6, 16), r.uniform(2, 4),
               (c1 + fw, ztop - fw, c2 - fw, zbot + fw), 0.16 if then else 0.2)
    for cx in (c1 + 1, c2 - 2):
        w.at(cx, ztop - 1, IRON)                                       # the nails


def smudge(w, cx, cz, rx, rz, box, a):
    """A soft smear of chalk, inside the box (c1, ztop, c2, zbot)."""
    c1, zt, c2, zb = box
    for c in range(int(cx - rx), int(cx + rx) + 1):
        for z in range(int(cz - rz), int(cz + rz) + 1):
            d = ((c - cx) / rx) ** 2 + ((z - cz) / rz) ** 2
            if d < 1 and c1 <= c < c2 and zb < z <= zt:
                w.at(c, z, CHALK, a * (1 - d))


def crack(w, c1, ztop, c2, zbot, seed, fw=2):
    """NOW: a crack across the slate, jagged, from its top edge to its bottom or a side."""
    r = random.Random(seed)
    c = r.uniform(c1 + (c2 - c1) * 0.2, c1 + (c2 - c1) * 0.8)
    drift = r.choice((-1, 1)) * r.uniform(0.2, 0.7)
    for z in range(ztop - fw, zbot + fw, -1):
        c += drift + r.uniform(-0.8, 0.8)
        if c < c1 + fw or c >= c2 - fw:
            break
        w.at(int(c), z, (22, 24, 28))
        w.at(int(c) + 1, z, shade(SLATE_N, 1.25))


def chalk_text(w, s, c0, ztop, then, seed, scale=1, col=CHALK):
    """A line of chalk capitals, its left at c0, its top at ztop: each letter a little up or down, the chalk's
    grain in it; NOW half rubbed off (but every letter still there)."""
    r = random.Random(seed * 131 + len(s))
    for n, ch in enumerate(s):
        if ch == " ":
            continue
        im = Img(5 * scale, 5 * scale, (0, 0, 0, 0))
        text(im, ch, 0, 0, (255, 255, 255), scale)
        dz = r.choice((0, 0, 0, 1, -1)) if scale == 1 else r.randint(-1, 1) * max(1, scale // 2)
        rub = r.random() < 0.35
        for y in range(im.h):
            for x in range(im.w):
                if not im.px[y * im.w + x][3]:
                    continue
                c, z = c0 + n * 6 * scale + x, ztop + dz - y
                g = h32(c, z, seed)
                if then:
                    a = 0.5 if g < 0.06 else 0.82 + 0.18 * h32(c, z, seed + 1)
                elif scale == 1:
                    a = 0.45 if g < 0.12 else 0.66 + 0.26 * h32(c, z, seed + 1)
                else:
                    a = 0.2 if g < (0.3 if rub else 0.15) else 0.6 + 0.3 * h32(c, z, seed + 1)
                w.at(c, z, col, a)


def chalk_lines(w, lines, cx, ztop, then, seed, scales, gap=3, left=None):
    z = ztop
    for k, (s, sc) in enumerate(zip(lines, scales)):
        c0 = cx - (len(s) * 6 * sc - sc) // 2 if left is None else left
        chalk_text(w, s, c0, z, then, seed + k, sc)
        z -= 5 * sc + gap
    return z


def tick(w, c, z, then, s=1):
    """A chalk tick, its foot at (c + 2s, z - 4s)."""
    pts = [(0, 2), (1, 3), (2, 4), (3, 3), (4, 2), (5, 1), (6, 0)]
    a = 0.9 if then else 0.7
    for (dx, dz) in pts:
        for i in range(s):
            for j in range(s):
                w.at(c + dx * s + i, z - dz * s - j, CHALK, a)


def slate_lines(w, spec, then, ztop, scales, pad, seed, gap=3, extra=0, fw=2):
    """A slate sized to its lines, centred on the wall, its top at ztop; the lines chalked on it. Returns its
    box (c1, c2, zbot)."""
    lines = spec["lines"]
    tw = max(text_width(s, sc) for s, sc in zip(lines, scales))
    hh = sum(5 * sc for sc in scales) + gap * (len(lines) - 1)
    cx = w.w // 2
    c1, c2 = max(0, cx - tw // 2 - pad - fw), min(w.w, cx + (tw + 1) // 2 + pad + fw)
    zbot = ztop - hh - 2 * pad - 2 * fw - extra
    slate(w, c1, ztop, c2, zbot, then, seed, fw)
    chalk_lines(w, lines, cx, ztop - fw - pad, then, seed, scales, gap)
    if not then:
        crack(w, c1, ztop, c2, zbot, seed + 7, fw)
    return c1, c2, zbot


def p_shelter(w, spec, then):
    slate_lines(w, spec, then, 214, (3, 2), 5, 401, 5)


def p_house(w, spec, then):
    """ANIMAL HOUSE on a slate over the front door; the door's black-painted surround (the door's columns
    spec["door"], its head spec["head"])."""
    c1, c2 = spec.get("door", (48, 112))
    head = spec.get("head", 128)
    col = (22, 22, 22) if then else (70, 68, 64)
    for c in range(c1 - 8, c2 + 8):
        for z in range(1, head + 9):
            if c1 <= c < c2 and z <= head:
                continue
            k = jt(col, c, z // 4, 402, 0.1)
            if c in (c1 - 8, c2 + 7) or z == head + 8:
                k = shade(k, 1.8)                                      # the surround's arris
            if not then and patch(c, z, 403, 8) < 0.3:
                k = jt((126, 116, 100), c, z, 404, 0.05)
            w.at(c, z, k)
    slate_lines(w, spec, then, 170, (2,), 5, 405)


def p_plan(w, spec, then):
    c1, c2, ztop, zbot = 4, w.w - 4, 196, 36
    slate(w, c1, ztop, c2, zbot, then, 406, 3)
    chalk_text(w, "ANIMAL HOUSE", w.w // 2 - (12 * 6 - 1) // 2, ztop - 5, then, 407, 1)
    tmp_ink = (250, 250, 246)
    draw_plan(w, spec["plan"], c1 + 5, ztop - 12, c2 - 5, zbot + 5, tmp_ink, faint=(200, 200, 196),
              here=CHALK_Y)
    # the plan in chalk: its lines' grain; NOW half rubbed
    sc = SLATE if then else SLATE_N
    for c in range(c1 + 3, c2 - 3):
        for z in range(zbot + 4, ztop - 3):
            p = w.get(c, z)
            if p is None or p[0] < 150:
                continue
            g = h32(c, z, 408)
            if then:
                a = 0.4 if g < 0.12 else 0.08
            else:
                a = 0.6 if g < 0.3 else 0.25
            w.at(c, z, sc, a)
    if not then:
        crack(w, c1, ztop, c2, zbot, 409, 3)


def p_gate(w, spec, then):
    z, n = spec.get("head", 128), len(spec["lines"])
    slate_lines(w, spec, then, z + (30 if n > 1 else 26), (2,) + (1,) * (n - 1), 3, 410, 3)


def p_hatch(w, spec, then):
    d = spec.get("arrow") or 0
    n = len(spec["lines"])
    extra = 9 if d else 0
    top = 70 + 5 * n + 3 * (n - 1) + 6 + 4 + extra
    c1, c2, zb = slate_lines(w, spec, then, top, (1,) * n, 3, 411, 3, extra)
    if d:
        cx = w.w // 2
        arrow(w, cx + d * 6, zb + 2 + 6, d, CHALK if then else (200, 200, 194), 3)


def p_lever(w, spec, then):
    d = spec.get("arrow", 0)
    c1, c2, zb = slate_lines(w, spec, then, 104, (2, 1), 4, 412, 4, 12 if d else 0)
    if d:
        arrow(w, w.w // 2 + d * 6, zb + 2 + 9, d, CHALK if then else (200, 200, 194), 4)


def p_rules(w, spec, then):
    lines = spec["lines"]
    slate_lines(w, dict(spec, lines=lines), then, 122, (2,) + (1,) * (len(lines) - 1), 6, 413, 4)


def p_weigh(w, spec, then):
    slate_lines(w, spec, then, 118, (2, 1, 1, 1), 6, 414, 5)


def p_glass(w, spec, then):
    slate_lines(w, spec, then, 186, (2, 2), 4, 415, 3)


def p_keepers(w, spec, then):
    slate_lines(w, spec, then, 118, (1,), 3, 416)


HEADS = dict(kennels="KENNELS", stalls="STALLS", isolation="ISOLATION", big="BIG RUN")


def name_slate(w, run, then, ztop, sc, hsc, seed, pad=5, gap=5):
    """A run's slate: its name over a chalk line, the animals' names one to a line, a tick by each."""
    r = RUNS[run]
    head, names = HEADS[run], r["names"]
    nw = max(text_width(s, sc) for s in names) + 10 * sc
    tw = max(nw, text_width(head, hsc))
    hh = 5 * hsc + 6 + len(names) * (5 * sc + gap) - gap
    cx, fw = w.w // 2, 2
    c1, c2 = max(0, cx - tw // 2 - pad - fw), min(w.w, cx + (tw + 1) // 2 + pad + fw)
    zbot = ztop - hh - 2 * pad - 2 * fw
    slate(w, c1, ztop, c2, zbot, then, seed, fw)
    z = ztop - fw - pad
    chalk_text(w, head, cx - text_width(head, hsc) // 2, z, then, seed + 1, hsc)
    z -= 5 * hsc + 2
    rr = random.Random(seed)
    for c in range(cx - text_width(head, hsc) // 2, cx + text_width(head, hsc) // 2 + 1):
        w.at(c, z - (1 if rr.random() < 0.1 else 0), CHALK, 0.8 if then else 0.6)     # the line under it
    z -= 4
    left = cx - nw // 2
    for k, s in enumerate(names):
        chalk_text(w, s, left, z, then, seed + 2 + k, sc)
        tick(w, left + nw - 7 * sc, z, then, max(1, sc // 2) if sc > 1 else 1)
        z -= 5 * sc + gap
    if not then:
        crack(w, c1, ztop, c2, zbot, seed + 9, fw)


def p_board(w, spec, then):
    name_slate(w, spec["run"], then, 148, 2, 2, 417)


def p_card(w, spec, then):
    run = spec["run"]
    n = len(RUNS[run]["names"])
    top = 58 + 4 + 5 + 6 + n * 8 + 6
    name_slate(w, run, then, top, 1, 1, 430, pad=3, gap=3)


PICTURES = {"shelter": p_shelter, "house": p_house, "plan": p_plan, "gate": p_gate, "hatch": p_hatch,
            "lever": p_lever, "rules": p_rules, "weigh": p_weigh, "glass": p_glass, "keepers": p_keepers,
            "board": p_board, "card": p_card}


# === sprites ======================================================================================================
def s_bowl(then):
    """An enamel dog bowl, white with a dark blue-black rim (THEN with biscuits in it); NOW chipped and rusted."""
    im = sprite_img(24, 12)
    rim = (30, 36, 54)
    white = (240, 240, 234) if then else (214, 208, 190)
    for y in range(4, 11):
        half = 11 - (y - 4) // 2
        for x in range(12 - half, 12 + half):
            c = shade(white, 0.86 + 0.18 * (1 - abs(x - 12) / half))
            if not then and h32(x, y, 501) < 0.22:
                c = mix((60, 40, 30), RUST, h32(x, y, 502))
            im.set(x, y, c)
    im.rect(0, 3, 24, 5, rim if then else (70, 66, 70))
    im.rect(6, 10, 18, 12, rim)
    if then:
        for x in range(3, 21):                                      # a heap of biscuit
            top = 3 - int(2.6 * math.sin((x - 3) / 18 * math.pi))
            for y in range(top, 4):
                im.set(x, y, jt((150, 104, 60), x, y, 503, 0.18))
    else:
        for x, y in ((5, 6), (15, 8), (9, 4), (19, 5)):
            im.set(x, y, (30, 26, 24))
            im.set(x + 1, y, (30, 26, 24))
    return im, (12, 12)


def s_bucket(then):
    """A wooden pail with two black iron hoops and a yard brush leant on it; NOW grey, a hoop slipped, the brush
    worn to its stock."""
    im = sprite_img(34, 36)
    wood = OAK if then else (128, 118, 102)
    for y in range(14, 36):
        half = 10 - (y - 14) // 7
        for x in range(13 - half, 13 + half):
            k = (x - 13 + half) // 3
            c = shade(wood, 0.82 + 0.2 * (k % 2) + 0.12 * (1 - abs(x - 13) / half))
            im.set(x, y, c)
    for yh in ((17, 18), (31, 32) if then else (33, 34)):
        y = yh[0]
        half = 10 - (y - 14) // 7
        im.rect(13 - half, yh[0], 13 + half, yh[1] + 1, IRON if then else RUST)
    im.rect(3, 13, 23, 15, shade(wood, 1.2))
    if not then:
        im.rect(15, 16, 18, 30, (20, 18, 16))                          # a stave gone
    for x in range(4, 23):                                            # the rope handle
        y = 13 - int(9 * math.sin((x - 4) / 18 * math.pi))
        im.set(x, y, (180, 160, 120) if then else (110, 100, 84))
    # the yard brush, leant on it: its handle, its stock, its bristles
    h = (176, 140, 96) if then else (112, 100, 86)
    for i in range(30):
        x, y = 30 - i * 0.13, 2 + i
        im.set(int(x), int(y), h)
        im.set(int(x) + 1, int(y), shade(h, 0.8))
    im.rect(22, 30, 34, 33, (110, 84, 56) if then else (92, 80, 66))
    for x in range(22, 34):
        if x % 2 == 0 or then:
            im.rect(x, 33, x + 1, 36 if then else 35, (36, 30, 24) if then else (70, 64, 54))
    return im, (14, 36)


def s_store(then):
    """THEN: a straw bale and two sacks of feed; NOW: their rotted heap, a torn sack, black straw."""
    im = sprite_img(48, 40)
    if then:
        for y in range(14, 40):                                        # the bale
            for x in range(1, 30):
                c = jt(STRAW, x // 2, y, 511, 0.12)
                if (x + y * 3) % 7 == 0:
                    c = shade(c, 0.8)
                if y == 14 or x in (1, 29):
                    c = shade(c, 0.85)
                im.set(x, y, c)
        for x in (8, 22):                                              # the twine
            im.rect(x, 14, x + 1, 40, (120, 90, 50))
        for k, (cx, top) in enumerate(((30, 12), (40, 18))):            # the sacks
            hess = (186, 158, 108) if k == 0 else (172, 146, 98)
            for y in range(top, 40):
                half = 7 + min(3, (y - top) // 3)
                if y > 36:
                    half -= (y - 36)
                for x in range(cx - half, cx + half):
                    c = jt(hess, x, y, 512 + k, 0.06)
                    if (x + y) % 3 == 0:
                        c = shade(c, 0.92)
                    im.set(x, y, c)
            im.rect(cx - 2, top - 4, cx + 2, top, shade(hess, 0.8))   # the tied neck
            im.rect(cx - 3, top, cx + 3, top + 1, (90, 70, 44))
            im.rect(cx - 5, top + 10, cx + 5, top + 12, (60, 70, 92))   # a blue band woven in
    else:
        for y in range(16, 40):                                        # the heap
            half = int(22 * math.sqrt(max(0, 1 - ((40 - y) / 24) ** 2)))
            for x in range(24 - half, 24 + half):
                c = jt((76, 66, 50), x // 2, y // 2, 521, 0.18)
                if h32(x, y, 522) < 0.2:
                    c = (40, 34, 28)
                im.set(x, y, c)
        for y in range(22, 40):                                        # a torn sack slumped on it
            for x in range(26, 44):
                if (x - 35) ** 2 / 81 + (y - 32) ** 2 / 64 < 1 and h32(x // 2, y // 2, 523) > 0.18:
                    im.set(x, y, jt((134, 120, 94), x, y, 524, 0.08))
        _r = random.Random(525)
        for _ in range(40):
            x0, y0, a = _r.uniform(4, 44), _r.uniform(20, 38), _r.uniform(0, math.pi)
            for i in range(_r.randint(4, 10)):
                x, y = int(x0 + math.cos(a) * i / 2), int(y0 + math.sin(a) * i / 2)
                if 0 <= x < 48 and 16 <= y < 40:
                    im.set(x, y, (58, 52, 40) if i % 2 else (90, 80, 58))
    return im, (24, 40)


SPRITES = {"bowl": s_bowl, "bucket": s_bucket, "store": s_store}
