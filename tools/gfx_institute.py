"""MAP11's institute: three looks (see AJAR_INSTITUTE in map_institute1.py).

  1 Academy   an academy's institute of the 1950s: cream plaster under a
              cornice, oak panelling, marble pillars, parquet, white tile in
              the labs, globes for lamps.
  2 Thaw      a science town's institute of the 1960s: white perforated
              panels, ash slats, aluminium, terrazzo, a mosaic of small tile,
              glass blocks, one flat colour to a room.
  3 Post Box  a closed establishment with a number for a name, some years
              on: two coats of oil paint over whitewash, brown lino, khaki
              steel, tiles gone from the walls, red stencils.

Every name is AJI<part><look>. Walls (64 wide, laid by world position:
ALIGNED; 256 high but for those marked):
  LB the lobby      CK 160 the cloakroom     CO the corridor   LA the lab
  CA the canteen: two storeys of 128, the upper one the gallery's
  AR the archive    PU 192 the pump room     EX the experiment hall
  EV 160 the way from it to the night room
Furniture, from the side (aligned unless marked):
  PI 256 a pillar of the lobby (one face, not aligned)   DS 40 the desk
  US 48 the cloakroom's counter     B4, B6, B9  a bench of the lab, 48, 64, 96
  TS 32 a table     GF 128 the gallery's front: the servery
  SK 256 a stack of the archive     TK 64 a tank     PS 64 a platform
  MC 128x256 the machine (one face, not aligned)
Pictures (one to a wall piece, on the room's wall, not aligned):
  ST 128 the street doors    MO 256 the lobby's long wall    NB 128 clock, notices
  CT 64x160 coats            BB 128 a blackboard             CB 128 cabinets
  MN 128 the menu            CI 128 a card index             GA 128x192 gauges
  CP 128 a control panel     WS 64 a warning
  S<look><nn>  a name over a way through a wall, D<look><nn> a locked door's
               face: the map asks for these (map_institute1.SIGNS, FACES)
Flats:
  FL FC FA FN FR FP FE  floors: lobby, corridor and cloakroom, lab, canteen,
                        archive, pump room, hall
  KQ                    the pump room's ceiling where its lamp is
  KL KC KA KP KE        ceilings: lobby, corridor and canteen, lab and
                        archive, pump room, hall
  DT UT BT TT PT GT     tops: desk, counter, bench, table, platform; the
                        gallery's floor
"""
import math
import random

import gfx_cinema                               # the lettering's K, W and X
from gfx import DIGITS, Img, digit, shade, text
from gfx_bus import blend, mix
from gfx_cinema import blot, paste, tiled

DIGITS.update({"J": ("00111", "00010", "00010", "10010", "01100"),
               "Z": ("11111", "00010", "00100", "01000", "11111"),
               ".": ("00000", "00000", "00000", "00000", "00100")})

LOOKS = (1, 2, 3)
WALLS = ("LB", "CK", "CO", "LA", "CA", "AR", "PU", "EX", "EV")
SIDES = ("DS", "US", "B4", "B6", "B9", "TS", "GF", "SK", "TK", "PS")
ALIGNED = {f"AJI{p}{n}" for p in WALLS + SIDES for n in LOOKS}
HEIGHT = {"CK": 160, "PU": 192, "EV": 160}

CREAM, OAK, MARB, GILT = (226, 212, 180), (124, 84, 50), (34, 30, 34), (204, 168, 86)
OLIVE, SEA, TILE, DGREEN, TERRA = (104, 116, 80), (112, 152, 140), (232, 232, 224), (52, 78, 62), (168, 92, 60)
WH, PB, AL, ASH = (232, 232, 226), (150, 186, 204), (176, 182, 188), (198, 164, 110)
ORANGE, YELLOW, ENAMEL, CONC, STEELB = (226, 122, 52), (232, 196, 72), (176, 204, 184), (168, 166, 160), (120, 132, 142)
DIRTY, IGREEN, BGREY, KHAKI, LINO = (200, 190, 154), (84, 118, 98), (100, 120, 136), (112, 116, 94), (112, 78, 54)
TAR, RED, RUST, DARK = (44, 42, 44), (170, 44, 36), (120, 66, 36), (60, 62, 66)
WOOD = {1: OAK, 2: ASH, 3: (128, 104, 74)}                  # what things are made of
METAL = {1: (190, 156, 84), 2: AL, 3: KHAKI}
PLATE = {1: (MARB, GILT), 2: (WH, (40, 70, 130)), 3: ((222, 216, 190), RED)}     # a sign: its ground, its letters


def name(part, n):
    return f"AJI{part}{n}"


# === bands: a wall is a pile of them ===========================================
def plain(im, y1, y2, rnd, c, var=0.025):
    for y in range(y1, y2):
        for x in range(im.w):
            im.set(x, y, shade(c, 1 + rnd.uniform(-var, var)))


def line(im, y1, y2, rnd, c):
    im.rect(0, y1, im.w, y2, c)
    if y2 - y1 > 2:
        im.rect(0, y1, im.w, y1 + 1, shade(c, 1.3))
        im.rect(0, y2 - 1, im.w, y2, shade(c, 0.6))


def cornice(im, y1, y2, rnd, c, gilt=None):
    h = y2 - y1
    im.rect(0, y1, im.w, y1 + h * 2 // 5, shade(c, 1.07))
    im.rect(0, y1 + h * 2 // 5, im.w, y2, shade(c, 0.9))
    im.rect(0, y1 + h * 2 // 5, im.w, y1 + h * 2 // 5 + 1, shade(c, 0.72))
    for x in range(2, im.w, 8):                                  # dentils
        im.rect(x, y1 + h * 3 // 5, x + 4, y2 - 3, shade(c, 1.04))
    im.rect(0, y2 - 3, im.w, y2 - 1, gilt or shade(c, 0.8))
    im.rect(0, y2 - 1, im.w, y2, shade(c, 0.6))


def panels(im, y1, y2, rnd, c, w=32):
    """Wood panelling: a framed panel to every w, under a rail."""
    for y in range(y1, y2):
        for x in range(im.w):
            g = 1 + 0.05 * math.sin((x % w) * 0.9 + 2.2 * math.sin(y * 0.07 + x // w)) + rnd.uniform(-0.02, 0.02)
            im.set(x, y, shade(c, g))
    for x0 in range(0, im.w, w):
        im.frame(x0 + 3, y1 + 9, x0 + w - 3, y2 - 5, shade(c, 0.6), 2)
        im.frame(x0 + 5, y1 + 11, x0 + w - 5, y2 - 7, shade(c, 1.22), 1)
    im.rect(0, y1, im.w, y1 + 3, shade(c, 1.25))
    im.rect(0, y1 + 3, im.w, y1 + 4, shade(c, 0.5))


def boards(im, y1, y2, rnd, c, w=8, gap=0.5):
    """Upright boards or slats, one to every w."""
    for x in range(im.w):
        k = x % w
        f = gap if k == 0 or k == w - 1 else 1 + 0.06 * math.sin(x // w * 2.3) + (0.08 if k == 1 else 0)
        for y in range(y1, y2):
            im.set(x, y, shade(c, f + rnd.uniform(-0.02, 0.02)))
    im.rect(0, y1, im.w, y1 + 2, shade(c, 1.2))
    im.rect(0, y1 + 2, im.w, y1 + 3, shade(c, 0.5))


def tiles(im, y1, y2, rnd, c, s=16, bond=False, gloss=True, gone=0.0, grout=0.72, var=0.04):
    """Square tiles (or blocks, with bond) of s, from the foot up; `gone`: how
    many have fallen and left their cement."""
    row = 0
    for ty in range(y2 - s, y1 - s, -s):
        off = s // 2 if bond and row % 2 else 0
        row += 1
        for tx in range(-off, im.w, s):
            lost = rnd.random() < gone
            f = rnd.uniform(1 - var, 1 + var)
            for y in range(max(ty, y1), min(ty + s, y2)):
                for x in range(max(tx, 0), min(tx + s, im.w)):
                    if lost:
                        cc = shade((150, 138, 118), rnd.uniform(0.85, 1.05))
                    elif x - tx in (0, s - 1) or y - ty in (0, s - 1):
                        cc = shade(c, grout)
                    elif gloss and (x - tx == 1 or y - ty == 1):
                        cc = shade(c, f * 1.06)
                    else:
                        cc = shade(c, f)
                    im.set(x, y, cc)


def perf(im, y1, y2, rnd, c, step=4, joint=32):
    for y in range(y1, y2):
        for x in range(im.w):
            hole = x % step == step // 2 and (y - y1) % step == step // 2
            edge = x % joint in (0, joint - 1)
            im.set(x, y, shade(c, 0.55 if hole else 0.8 if edge else 1))


def concrete(im, y1, y2, rnd, c):
    """Cast against boards: a line every 32, the holes of the ties."""
    for y in range(y1, y2):
        for x in range(im.w):
            im.set(x, y, shade(c, 1 + rnd.uniform(-0.06, 0.05) + 0.03 * math.sin(y * 1.3)))
    for y in range(y2 - 32, y1, -32):
        im.rect(0, y, im.w, y + 1, shade(c, 0.8))
        for x in (15, 47):
            im.disc(x + 0.5, y + 16.5, 1.5, shade(c, 0.6))


def glassblock(im, y1, y2, rnd, c, s=16):
    for y in range(y1, y2):
        for x in range(im.w):
            u, v = x % s, (y - y1) % s
            if u in (0, s - 1) or v in (0, s - 1):
                cc = (206, 208, 204)
            else:
                d = (abs(u - s / 2) + abs(v - s / 2)) / s
                cc = shade(c, 0.86 + 0.3 * d + (0.12 if u + v == s - 2 else 0))
            im.set(x, y, cc)


def mosaic(im, y1, y2, rnd, cols, s=4):
    for ty in range(y1, y2, s):
        for tx in range(0, im.w, s):
            c = shade(rnd.choice(cols), rnd.uniform(0.94, 1.04))
            im.rect(tx, ty, tx + s, min(ty + s, y2), (188, 186, 176))
            im.rect(tx, ty, tx + s - 1, min(ty + s - 1, y2), c)


def hazard(im, y1, y2, rnd, a, b, w=8):
    for y in range(y1, y2):
        for x in range(im.w):
            im.set(x, y, a if (x + y - y1) // w % 2 else b)


def pipes(im, y1, y2, rnd, c, bg):
    """Two painted pipes along the wall."""
    im.rect(0, y1, im.w, y2, bg)
    h = (y2 - y1) // 2
    for k in range(2):
        for i in range(h - 1):
            f = 1.25 - 0.9 * abs(i - (h - 2) / 3) / h
            im.rect(0, y1 + k * h + i, im.w, y1 + k * h + i + 1, shade(c, f))
    for x in (30, 31, 32, 33):                                   # a clip
        im.rect(x, y1, x + 1, y2, shade(c, 0.55))


def pile(h, bands, seed, w=64):
    """A wall h high from bands, top to bottom: (painter, height, arguments);
    one height is None and takes what is left."""
    rnd = random.Random(seed)
    im = Img(w, h)
    rest = h - sum(b[1] for b in bands if b[1])
    y = 0
    for fn, bh, *args in bands:
        bh = rest if bh is None else bh
        kw = args[-1] if args and isinstance(args[-1], dict) else {}
        fn(im, y, y + bh, rnd, *[a for a in args if a is not kw or not isinstance(a, dict)], **kw)
        y += bh
    return im


# --- what time does to a wall (look 3) ------------------------------------------
def drips(im, rnd, n, c, y1=2, far=120):
    for _ in range(n):
        x, k = rnd.randrange(3, im.w - 3), rnd.randrange(far // 3, far)
        for i in range(k):
            for dx in (-1, 0, 1):
                blend(im, x + dx, y1 + i, c, 0.4 * (1 - i / k))


def scuffs(im, rnd, y1, y2, n, c):
    for _ in range(n):
        x, y = rnd.randrange(im.w), rnd.randrange(y1, y2)
        for k in range(rnd.randrange(2, 10)):
            blend(im, (x + k) % im.w, y, c, 0.45)


def peel(im, rnd, y1, y2, n, under):
    """Paint come away in flakes."""
    for _ in range(n):
        cx, cy, r = rnd.randrange(im.w), rnd.randrange(y1, y2), rnd.randrange(3, 8)
        for y in range(cy - r, cy + r):
            for x in range(cx - r, cx + r):
                if y1 <= y < y2 and (x - cx) ** 2 + (y - cy) ** 2 < r * r * rnd.uniform(0.4, 1.1):
                    im.set(x % im.w, y, shade(under, rnd.uniform(0.9, 1.05)))


def grime(im, rnd, n=22):
    """Dirt up from the floor."""
    for x in range(im.w):
        for k in range(rnd.randrange(n // 3, n)):
            blend(im, x, im.h - 1 - k, (48, 42, 36), 0.4 * (1 - k / n))


# === walls =====================================================================
def wall(n, part, h=None):
    h = h or HEIGHT.get(part, 256)
    seed = 1100 + n * 31 + WALLS.index(part)
    rnd = random.Random(seed + 7)
    skirt = {1: MARB, 2: DARK, 3: (62, 52, 46)}[n]
    if n == 1:
        b = {
            "LB": [(cornice, 22, CREAM, GILT), (plain, None, CREAM), (line, 2, GILT), (panels, 88, OAK), (line, 10, skirt)],
            "CK": [(cornice, 10, CREAM), (plain, None, CREAM), (boards, 64, OAK), (line, 8, skirt)],
            "CO": [(cornice, 16, CREAM), (plain, None, CREAM), (line, 3, shade(OLIVE, 0.55)), (plain, 104, OLIVE, 0.02),
                   (line, 8, shade(OAK, 0.7))],
            "LA": [(cornice, 12, CREAM), (plain, None, CREAM), (line, 2, MARB), (tiles, 144, TILE), (line, 8, (96, 98, 100))],
            "CA": [(cornice, 16, CREAM), (plain, None, CREAM), (line, 8, shade(OAK, 0.8)),
                   (plain, 37, CREAM), (line, 3, shade(SEA, 0.5)), (plain, 80, SEA, 0.02), (line, 8, shade(OAK, 0.7))],
            "AR": [(cornice, 12, CREAM), (plain, None, DGREEN, 0.03), (line, 2, GILT), (panels, 96, OAK), (line, 8, skirt)],
            "PU": [(tiles, 96, (226, 222, 208), 32, True, False), (line, 2, (30, 30, 32)),
                   (tiles, 86, TAR, 32, True, False, {"grout": 0.6}), (line, 8, (30, 30, 32))],
            "EX": [(cornice, 14, (206, 212, 204)), (plain, None, (176, 188, 180)), (line, 4, (150, 40, 34)), (tiles, 112, TILE),
                   (line, 10, (70, 72, 76))],
            "EV": [(cornice, 10, (206, 212, 204)), (plain, None, (176, 188, 180)), (line, 4, (150, 40, 34)), (tiles, 64, TILE),
                   (line, 8, (70, 72, 76))],
        }[part]
    elif n == 2:
        b = {
            "LB": [(line, 6, AL), (perf, None, WH), (line, 2, AL), (boards, 96, ASH, 8, 0.45), (line, 8, skirt)],
            "CK": [(line, 4, AL), (perf, None, (190, 196, 198), 4, 64), (boards, 56, ASH, 8, 0.6), (line, 8, skirt)],
            "CO": [(line, 4, AL), (plain, None, WH, 0.012), (line, 2, AL), (plain, 110, PB, 0.015), (line, 8, skirt)],
            "LA": [(line, 4, AL), (tiles, None, ENAMEL, 32, False, True, {"var": 0.015, "grout": 0.82}), (line, 5, DARK),
                   (plain, 59, (208, 212, 208), 0.012), (line, 8, skirt)],
            "CA": [(line, 4, AL), (glassblock, 64, (186, 212, 220)), (plain, None, WH, 0.012), (line, 8, shade(ASH, 0.85)),
                   (plain, 36, WH, 0.012), (line, 2, AL),
                   (mosaic, 82, (YELLOW, YELLOW, shade(YELLOW, 0.88), WH, ORANGE)), (line, 8, skirt)],
            "AR": [(line, 4, AL), (perf, None, WH), (line, 2, AL), (tiles, 96, STEELB, 32, False, False, {"var": 0.01}),
                   (line, 8, skirt)],
            "PU": [(concrete, 64, CONC), (pipes, 12, (60, 110, 170), shade(CONC, 0.8)), (concrete, None, CONC), (line, 8, skirt)],
            "EX": [(line, 6, AL), (concrete, None, CONC), (line, 3, (50, 96, 150)), (plain, 77, (124, 152, 178), 0.015),
                   (hazard, 16, YELLOW, (36, 36, 40))],
            "EV": [(line, 4, AL), (concrete, None, CONC), (line, 3, (50, 96, 150)), (plain, 45, (124, 152, 178), 0.015),
                   (hazard, 16, YELLOW, (36, 36, 40))],
        }[part]
    else:
        b = {
            "LB": [(plain, None, DIRTY, 0.04), (line, 3, shade(IGREEN, 0.6)), (plain, 125, IGREEN, 0.03), (line, 8, skirt)],
            "CK": [(plain, None, DIRTY, 0.04), (line, 2, shade(IGREEN, 0.6)), (plain, 78, IGREEN, 0.03), (line, 8, skirt)],
            "CO": [(pipes, 12, shade(DIRTY, 0.92), shade(DIRTY, 0.7)), (plain, None, DIRTY, 0.04), (line, 3, shade(BGREY, 0.6)),
                   (plain, 117, BGREY, 0.03), (line, 8, skirt)],
            "LA": [(plain, None, (190, 192, 178), 0.04), (line, 2, (70, 72, 70)),
                   (tiles, 112, (216, 214, 198), 16, False, True, {"gone": 0.13}), (line, 8, skirt)],
            "CA": [(plain, None, DIRTY, 0.04), (line, 8, (92, 70, 52)),
                   (plain, 38, DIRTY, 0.04), (line, 2, (90, 84, 70)), (tiles, 80, (222, 218, 202), 16, False, True, {"gone": 0.1}),
                   (line, 8, skirt)],
            "AR": [(plain, None, DIRTY, 0.04), (line, 3, shade(BGREY, 0.6)), (plain, 109, BGREY, 0.03), (line, 8, skirt)],
            "PU": [(tiles, 96, (214, 208, 190), 32, True, False, {"var": 0.07}), (line, 2, (30, 30, 32)),
                   (tiles, 86, TAR, 32, True, False, {"grout": 0.6}), (line, 8, (30, 30, 32))],
            "EX": [(tiles, None, (152, 150, 142), 32, True, False, {"var": 0.06}), (line, 6, RED), (plain, 96, IGREEN, 0.03),
                   (line, 10, skirt)],
            "EV": [(tiles, None, (152, 150, 142), 32, True, False, {"var": 0.06}), (line, 6, RED), (plain, 64, IGREEN, 0.03),
                   (line, 8, skirt)],
        }[part]
    im = pile(h, b, seed)
    if n == 1 and part == "LB":                                  # half a pilaster at each edge
        for x in range(5):
            f = (0.82, 1.06, 0.9, 1.04, 0.86)[x]
            im.rect(x, 22, x + 1, h - 100, shade(CREAM, f))
            im.rect(63 - x, 22, 64 - x, h - 100, shade(CREAM, f))
    if n == 1 and part == "CA":                                  # a stencilled frieze under the cornice
        for x in range(0, 64, 16):
            im.diamond(x + 8, 26, 3, shade(SEA, 0.9))
        im.rect(0, 33, 64, 34, shade(SEA, 0.9))
    if n == 1 and part == "PU":
        drips(im, rnd, 2, RUST, 96, 60)
    if n == 3:
        dado = {"LB": 133, "CK": 86, "CO": 125, "LA": 120, "CA": 88, "AR": 117, "PU": 94, "EX": 106, "EV": 72}[part]
        drips(im, rnd, 3, (96, 78, 48), 0, 110)
        blot(im, rnd.randrange(12, 52), rnd.randrange(24, 70), rnd.randrange(9, 15), (104, 86, 52), 0.25)
        if part in ("LB", "CK", "CO", "AR", "EX", "EV"):
            peel(im, rnd, h - dado, h - 12, 4, (176, 168, 140))
        if part == "PU":
            peel(im, rnd, 0, 96, 9, (150, 96, 76))               # the whitewash off the brick
            drips(im, rnd, 3, RUST, 60, 100)
        scuffs(im, rnd, h - 70, h - 8, 26, (40, 36, 32))
        grime(im, rnd)
    im.noise(3, seed)
    return im


# === furniture from the side ====================================================
def pillar(n):
    rnd = random.Random(1200 + n)
    if n == 1:                                                   # red marble, a gilt capital, a black foot
        c = (128, 44, 40)
        im = Img(64, 256, c)
        for y in range(256):
            for x in range(64):
                im.set(x, y, shade(c, 0.9 + 0.16 * math.sin(x * 0.21 + 2.4 * math.sin(y * 0.045)) + rnd.uniform(-0.03, 0.03)))
        gfx_cinema.veins(im, 24, 236, rnd, (214, 190, 170), 5)
        for x in range(64):                                      # round, by its shading
            f = 0.62 + 0.5 * math.sin((x + 0.5) * math.pi / 64)
            for y in range(256):
                p = im.px[y * 64 + x]
                im.px[y * 64 + x] = list(shade(p[:3], f)) + [255]
        im.rect(0, 0, 64, 10, CREAM)
        im.rect(0, 10, 64, 20, GILT)
        im.rect(0, 20, 64, 23, shade(GILT, 0.6))
        im.rect(0, 232, 64, 236, GILT)
        im.rect(0, 236, 64, 256, MARB)
    elif n == 2:                                                 # small blue tile round a square column
        im = pile(256, [(line, 6, AL), (mosaic, None, (PB, PB, shade(PB, 0.8), (88, 136, 170), WH)), (line, 8, DARK)], 1202)
    else:                                                        # the wall's two coats; a notice pasted on
        im = pile(256, [(plain, None, DIRTY, 0.04), (line, 3, shade(IGREEN, 0.6)), (plain, 125, IGREEN, 0.03),
                        (line, 8, (62, 52, 46))], 1203)
        peel(im, rnd, 130, 244, 6, (176, 168, 140))
        im.rect(16, 76, 48, 116, (226, 220, 196))
        for y in range(82, 112, 5):
            im.rect(20, y, 20 + rnd.randrange(14, 25), y + 1, (90, 86, 80))
        scuffs(im, rnd, 180, 248, 20, (40, 36, 32))
        grime(im, rnd)
        for x in (0, 63):
            im.rect(x, 0, x + 1, 256, shade(DIRTY, 0.6))
    im.noise(3, 1210 + n)
    return im


def cabinet(n, h, kind="bench"):
    """The side of something standing in a room, h high: a top's edge, then
    doors or drawers 16 wide, then a plinth. `kind`: bench, desk, counter,
    platform."""
    rnd = random.Random(1300 + n * 13 + h)
    c = {"bench": {1: OAK, 2: (150, 158, 164), 3: KHAKI},
         "desk": {1: OAK, 2: ASH, 3: (128, 104, 74)},
         "counter": {1: OAK, 2: ASH, 3: (128, 104, 74)},
         "platform": {1: (86, 92, 96), 2: (128, 148, 168), 3: (98, 102, 84)}}[kind][n]
    top = {"bench": {1: (36, 34, 36), 2: (236, 236, 230), 3: (96, 98, 84)},
           "desk": {1: (60, 88, 66), 2: (236, 236, 230), 3: (150, 124, 90)},
           "counter": {1: shade(OAK, 1.2), 2: (236, 236, 230), 3: (112, 78, 54)},
           "platform": {1: (60, 64, 68), 2: (60, 62, 66), 3: (60, 62, 52)}}[kind][n]
    im = Img(64, h, c)
    for y in range(h):
        for x in range(64):
            im.set(x, y, shade(c, 1 + rnd.uniform(-0.03, 0.03)))
    im.rect(0, 0, 64, 4, top)
    im.rect(0, 4, 64, 5, shade(c, 0.5))
    foot = 6 if h > 40 else 4
    if kind == "platform":                                       # louvres, a plate of rivets
        for x0 in range(0, 64, 32):
            im.frame(x0 + 1, 7, x0 + 31, h - foot - 1, shade(c, 0.6), 1)
            for y in range(12, h - foot - 6, 4):
                im.rect(x0 + 5, y, x0 + 27, y + 2, shade(c, 0.5))
                im.rect(x0 + 5, y + 2, x0 + 27, y + 3, shade(c, 1.25))
            for cx, cy in ((x0 + 3, 9), (x0 + 28, 9), (x0 + 3, h - foot - 4), (x0 + 28, h - foot - 4)):
                im.set(cx, cy, shade(c, 1.5))
        if n == 3:
            drips(im, rnd, 3, RUST, 6, h - 10)
    else:
        rows = max(1, (h - 5 - foot) // 22)
        rh = (h - 5 - foot) // rows
        for r in range(rows):
            for x0 in range(0, 64, 16):
                y0 = 6 + r * rh
                im.frame(x0 + 1, y0, x0 + 15, y0 + rh - 1, shade(c, 0.62), 1)
                if n == 1:
                    im.frame(x0 + 3, y0 + 2, x0 + 13, y0 + rh - 3, shade(c, 1.2), 1)
                kn = METAL[n] if n != 3 else (60, 60, 56)
                im.rect(x0 + 6, y0 + rh // 2 - 1, x0 + 10, y0 + rh // 2 + 1, kn)
        if n == 3:
            scuffs(im, rnd, 6, h - 2, 14, (60, 54, 44))
            peel(im, rnd, 8, h - 6, 2, (150, 150, 150) if kind == "bench" else (190, 170, 130))
    im.rect(0, h - foot, 64, h, shade(c, 0.4))
    im.noise(3, 1310 + n)
    return im


def table(n):
    """A table from the side: the top's edge, legs every 32, the dark under it."""
    im = Img(64, 32, (26, 24, 26))
    c = {1: (236, 232, 220), 2: ORANGE, 3: (150, 60, 50)}[n]    # a cloth, formica, oilcloth
    leg = {1: shade(OAK, 0.8), 2: AL, 3: (96, 100, 96)}[n]
    im.rect(0, 0, 64, 4, c)
    im.rect(0, 4, 64, 5, shade(c, 0.6))
    if n == 1:                                                   # the cloth hangs
        for x in range(64):
            im.rect(x, 5, x + 1, 11 + int(2 * math.sin(x * math.pi / 8)), shade(c, 0.86 + 0.1 * math.sin(x * math.pi / 4)))
    for x0 in (2, 28, 34, 60):
        im.rect(x0, 5 if n != 1 else 11, x0 + 2, 32, leg)
    if n != 1:
        im.rect(0, 5, 64, 8, shade(leg, 0.7))
    im.noise(3, 1320 + n)
    return im


def servery(n):
    """The gallery's front, 128 high: the kitchen's hatch, a counter under it."""
    base = wall(n, "CA")
    im = Img(64, 128)
    im.px = [list(p) for p in base.px[128 * 64:]]
    frame = {1: OAK, 2: AL, 3: (128, 132, 128)}[n]
    im.rect(4, 22, 60, 78, frame)
    im.rect(7, 25, 57, 75, (38, 36, 40))                         # the kitchen, dark
    for x in range(10, 56, 9):                                   # pans hung up
        im.rect(x, 25, x + 1, 31, (120, 120, 124))
        im.disc(x + 0.5, 35, 4, (150, 150, 156) if n != 3 else (112, 110, 104))
    im.rect(7, 60, 57, 75, {1: (226, 222, 210), 2: (206, 210, 212), 3: (170, 166, 150)}[n])    # the shutter half down
    for y in range(62, 75, 4):
        im.rect(7, y, 57, y + 1, (120, 120, 118))
    im.rect(2, 78, 62, 83, {1: (236, 232, 220), 2: ORANGE, 3: (150, 150, 146)}[n])             # the shelf
    im.rect(2, 83, 62, 84, (40, 38, 38))
    if n == 2:
        for x in (6, 56):
            im.rect(x, 84, x + 2, 120, AL)
    if n == 3:
        rnd = random.Random(1333)
        drips(im, rnd, 2, (90, 70, 44), 84, 34)
    im.noise(2, 1330 + n)
    return im


def stack(n):
    """An archive stack's side: shelves 32 apart, full."""
    rnd = random.Random(1340 + n)
    back = {1: shade(OAK, 0.45), 2: (70, 76, 82), 3: (56, 58, 50)}[n]
    shelf = {1: OAK, 2: (170, 176, 182), 3: KHAKI}[n]
    im = Img(64, 256, back)
    for sy in range(32, 257, 32):
        x = 1
        while x < 62:
            if n == 1:                                           # bound volumes, gilt on the spines
                w, hh = rnd.choice((4, 5, 6)), rnd.randrange(20, 27)
                c = shade(rnd.choice(((110, 40, 36), (52, 78, 62), (120, 84, 50), (40, 52, 84), (150, 120, 80))), rnd.uniform(0.8, 1.1))
                im.rect(x, sy - 3 - hh, x + w, sy - 3, c)
                im.rect(x, sy - 3 - hh, x + 1, sy - 3, shade(c, 0.7))
                im.rect(x + 1, sy - hh + 2, x + w - 1, sy - hh + 3, GILT)
                im.rect(x + 1, sy - 9, x + w - 1, sy - 8, GILT)
            elif n == 2:                                         # box files, a colour to a year
                w, hh = 7, 24
                c = shade(rnd.choice(((206, 206, 196), ORANGE, (88, 136, 170), YELLOW, (206, 206, 196))), rnd.uniform(0.9, 1.05))
                im.rect(x, sy - 3 - hh, x + w, sy - 3, c)
                im.frame(x, sy - 3 - hh, x + w, sy - 3, shade(c, 0.7), 1)
                im.rect(x + 2, sy - 20, x + w - 2, sy - 14, (240, 240, 232))
                im.disc(x + 3.5, sy - 8, 1, (40, 40, 44))
            else:                                                # card folders tied with tape, some lying
                if rnd.random() < 0.18:
                    w = rnd.randrange(12, 18)
                    for k in range(rnd.randrange(2, 6)):
                        c = shade((170, 150, 110), rnd.uniform(0.75, 1.05))
                        im.rect(x, sy - 6 - 3 * k, x + w, sy - 3 - 3 * k, c)
                        im.rect(x, sy - 4 - 3 * k, x + w, sy - 3 - 3 * k, shade(c, 0.7))
                else:
                    w, hh = rnd.choice((3, 4, 5)), rnd.randrange(18, 26)
                    c = shade(rnd.choice(((170, 150, 110), (150, 134, 104), (120, 116, 96), (176, 160, 130))), rnd.uniform(0.8, 1.05))
                    im.rect(x, sy - 3 - hh, x + w, sy - 3, c)
                    im.rect(x, sy - 3 - hh, x + 1, sy - 3, shade(c, 0.7))
                    im.rect(x, sy - 14, x + w, sy - 13, (226, 220, 200))
            x += w + (1 if rnd.random() < 0.85 else rnd.randrange(3, 9))
        im.rect(0, sy - 3, 64, sy, shelf)
        im.rect(0, sy - 3, 64, sy - 2, shade(shelf, 1.25))
    for x in (0, 63):
        im.rect(x, 0, x + 1, 256, shade(shelf, 0.8))
    im.noise(3, 1345 + n)
    return im


def tank(n):
    """A tank's plates, 64 high, riveted every 16; it repeats up the tank."""
    rnd = random.Random(1350 + n)
    c = {1: (52, 78, 66), 2: (176, 184, 190), 3: (96, 92, 78)}[n]
    im = Img(64, 64, c)
    for y in range(64):
        for x in range(64):
            im.set(x, y, shade(c, 1 + 0.07 * math.sin(x * math.pi / 32) + rnd.uniform(-0.03, 0.03)))
    for y0 in (0, 32):
        im.rect(0, y0, 64, y0 + 2, shade(c, 0.6))
        im.rect(0, y0 + 2, 64, y0 + 3, shade(c, 1.25))
        for x in range(4, 64, 8):
            im.set(x, y0 + 5, shade(c, 1.5))
            im.set(x, y0 + 6, shade(c, 0.6))
    if n == 2:
        im.rect(0, 14, 64, 20, (60, 110, 170))                   # a blue band
    if n == 3:
        drips(im, rnd, 5, RUST, 2, 56)
        digit(im, "7", 26, 40, RED, 3)
    im.noise(3, 1355 + n)
    return im


def dial(im, cx, cy, r, rim, a=0.6):
    im.disc(cx, cy, r, rim)
    im.disc(cx, cy, r - 1.5, (236, 232, 214))
    for k in range(7):
        t = math.pi * (0.85 + 1.3 * k / 6)
        im.set(int(cx + (r - 3) * math.cos(t)), int(cy + (r - 3) * math.sin(t)), (40, 40, 40))
    t = math.pi * (0.85 + 1.3 * a)
    for k in range(int(r - 2)):
        im.set(int(cx + k * math.cos(t)), int(cy + k * math.sin(t)), (170, 30, 26))


def machine(n):
    """One face of the machine in the experiment hall: 128 by 256."""
    rnd = random.Random(1360 + n)
    c = {1: (40, 40, 44), 2: (128, 150, 172), 3: KHAKI}[n]
    rim = METAL[n]
    im = Img(128, 256, c)
    for y in range(256):
        for x in range(128):
            im.set(x, y, shade(c, 1 + rnd.uniform(-0.03, 0.03)))
    im.frame(0, 0, 128, 256, shade(c, 0.55), 3)
    im.rect(3, 3, 125, 5, shade(c, 1.3))
    # a door's outline in the middle of it, in brass: what it is all for
    im.frame(40, 24, 88, 104, rim, 2)
    im.rect(42, 26, 86, 102, (16, 16, 22))
    for k in range(5):                                           # and the same again inside it, smaller
        d = 4 + k * 4
        im.frame(42 + d, 26 + d * 76 // 44, 86 - d, 102 - d * 76 // 44, shade(rim, 0.8 - k * 0.13), 1)
    for x, a in ((20, 0.3), (108, 0.75)):
        dial(im, x, 44, 11, rim, a)
        dial(im, x, 78, 8, rim, 1 - a)
    y0 = 116
    if n == 2:                                                   # two screens
        for x0 in (10, 70):
            im.rect(x0, y0, x0 + 48, y0 + 36, (30, 34, 34))
            im.frame(x0, y0, x0 + 48, y0 + 36, AL, 2)
            for x in range(x0 + 4, x0 + 44):
                im.set(x, int(y0 + 18 + 9 * math.sin((x - x0) * 0.45 + x0)), (120, 240, 150))
    else:                                                        # coils behind a grille
        im.rect(10, y0, 118, y0 + 36, (20, 18, 18))
        for x0 in range(16, 112, 14):
            for y in range(y0 + 4, y0 + 32, 2):
                im.rect(x0, y, x0 + 9, y + 1, (190, 110, 60) if n == 1 else (130, 84, 50))
        for x in range(10, 118, 6):
            im.rect(x, y0, x + 1, y0 + 36, shade(c, 0.7 if n == 1 else 1.2))
        im.frame(10, y0, 118, y0 + 36, rim, 1)
    for r in range(3):                                           # rows of switches and lamps
        for x in range(14, 116, 10):
            y = 166 + r * 14
            lamp = rnd.random() < 0.3
            col = rnd.choice(((230, 60, 40), (240, 200, 60), (90, 220, 110))) if lamp else (190, 190, 186)
            if lamp:
                im.disc(x + 1.5, y + 2, 2.5, col)
            else:
                im.rect(x, y, x + 3, y + 6, col)
                im.rect(x, y, x + 3, y + 2, shade(col, 0.6))
    im.rect(8, 210, 120, 212, shade(c, 0.6))
    for x0 in (8, 68):                                           # louvres at the foot
        for y in range(218, 246, 4):
            im.rect(x0 + 4, y, x0 + 48, y + 2, shade(c, 0.5))
    plate, ink = PLATE[n]
    im.rect(44, 8, 84, 20, plate)
    text(im, "No 7".upper(), 49, 11, ink, 1)
    if n == 3:
        drips(im, rnd, 4, RUST, 4, 150)
        scuffs(im, rnd, 150, 250, 30, (60, 54, 44))
    im.noise(3, 1365 + n)
    return im


# === flats =====================================================================
def flat(c, seed, amount=5):
    im = Img(64, 64, c)
    im.noise(amount, seed)
    return im


def checker(a, b, s, seed, joint=None):
    im = Img(64, 64)
    rnd = random.Random(seed)
    for ty in range(0, 64, s):
        for tx in range(0, 64, s):
            c = shade(a if (tx // s + ty // s) % 2 else b, rnd.uniform(0.94, 1.05))
            im.rect(tx, ty, tx + s, ty + s, c)
            if joint:
                im.rect(tx, ty, tx + s, ty + 1, joint)
                im.rect(tx, ty, tx + 1, ty + s, joint)
    im.noise(4, seed)
    return im


def parquet(c, seed):
    """Basket weave: squares of four blocks, turned by turns."""
    im = Img(64, 64, c)
    rnd = random.Random(seed)
    for by in range(0, 64, 16):
        for bx in range(0, 64, 16):
            across = (bx // 16 + by // 16) % 2
            for k in range(4):
                f = rnd.uniform(0.86, 1.1)
                for t in range(4):
                    for u in range(16):
                        x, y = (bx + u, by + k * 4 + t) if across else (bx + k * 4 + t, by + u)
                        im.set(x, y, shade(c, 0.62 if t == 0 or u == 0 else f))
    im.noise(4, seed)
    return im


def planks(c, seed, w=16, worn=None):
    im = Img(64, 64, c)
    rnd = random.Random(seed)
    for x in range(64):
        f = 0.6 if x % w == 0 else 1 + 0.06 * math.sin(x // w * 2.1)
        for y in range(64):
            im.set(x, y, shade(c, f + rnd.uniform(-0.03, 0.03)))
    for b in range(64 // w):
        y = (b * 23 + 9) % 64
        im.rect(b * w + 1, y, b * w + w, y + 1, shade(c, 0.6))
    if worn:
        for _ in range(26):
            blot(im, rnd.randrange(64), rnd.randrange(64), rnd.randrange(4, 9), worn, 0.5, wrap=True)
    im.noise(4, seed)
    return im


def terrazzo(c, seed, strips=True):
    im = Img(64, 64, c)
    rnd = random.Random(seed)
    for _ in range(460):
        x, y = rnd.randrange(64), rnd.randrange(64)
        cc = rnd.choice((shade(c, 1.25), shade(c, 0.66), (150, 120, 100), shade(c, 1.12)))
        im.rect(x, y, x + rnd.randrange(1, 3), y + rnd.randrange(1, 3), cc)
    if strips:
        im.rect(0, 0, 64, 1, (190, 160, 90))
        im.rect(0, 0, 1, 64, (190, 160, 90))
    im.noise(3, seed)
    return im


def lino(c, seed, wear=30, grid=32):
    im = Img(64, 64, c)
    rnd = random.Random(seed)
    for y in range(64):
        for x in range(64):
            im.set(x, y, shade(c, 1 + 0.05 * math.sin(x * 0.4 + 3 * math.sin(y * 0.11)) + rnd.uniform(-0.03, 0.03)))
    for _ in range(wear):
        x, y = rnd.randrange(64), rnd.randrange(64)
        for k in range(rnd.randrange(3, 10)):
            blend(im, (x + k) % 64, (y + k // 3) % 64, (56, 48, 42), 0.35)
    if grid:
        for k in range(0, 64, grid):
            im.rect(k, 0, k + 1, 64, shade(c, 0.6))
            im.rect(0, k, 64, k + 1, shade(c, 0.6))
    return im


def wet(c, seed, rust=False, drain=True):
    im = Img(64, 64, c)
    rnd = random.Random(seed)
    for _ in range(9):
        blot(im, rnd.randrange(64), rnd.randrange(64), rnd.randrange(7, 15), shade(c, 0.5), 0.5, wrap=True)
    if rust:
        for _ in range(4):
            blot(im, rnd.randrange(64), rnd.randrange(64), rnd.randrange(5, 10), RUST, 0.45, wrap=True)
    if drain:
        for x in range(26, 38):                                  # a drain's grating
            if x % 3:
                im.rect(x, 26, x + 1, 38, (24, 24, 26))
        im.frame(25, 25, 39, 39, (60, 60, 62), 1)
    im.noise(7, seed)
    return im


def grating(seed):
    im = Img(64, 64, (22, 24, 28))
    for k in range(0, 64, 4):
        im.rect(k, 0, k + 1, 64, (132, 138, 146))
    for k in range(0, 64, 16):
        im.rect(0, k, 64, k + 2, (150, 156, 164))
    im.noise(3, seed)
    return im


def lined(c, seed, stripe, cracks=0):
    """A workshop floor with a painted line along it."""
    im = flat(c, seed, 6)
    rnd = random.Random(seed)
    for y in range(64):
        for x in range(4):
            if not cracks or rnd.random() < 0.6:
                im.set(x, y, stripe)
    for _ in range(cracks):
        x, y = rnd.randrange(8, 64), rnd.randrange(64)
        for k in range(rnd.randrange(14, 40)):
            im.set(x % 64, y % 64, shade(c, 0.5))
            x += rnd.choice((-1, 0, 1, 1))
            y += rnd.choice((0, 1, 1))
    return im


def pump_lamp(n):
    """The pump room's ceiling with its one lamp. The lamp is drawn round the
    flat's corners, so that a square 32 off the grid shows it whole."""
    im = ceiling(n, "P")
    cage = {1: (60, 62, 60), 2: AL, 3: (70, 74, 56)}[n]
    glass = {1: (255, 244, 200), 2: (244, 250, 255), 3: (255, 232, 170)}[n]
    for cx in (0, 64):
        for cy in (0, 64):
            im.disc(cx - 0.5, cy - 0.5, 13, cage)
            im.disc(cx - 0.5, cy - 0.5, 10, glass)
    for k in (0, 5, 58, 63):                                     # the cage's bars
        d = 11 if k in (0, 63) else 9
        for t in range(d):
            for a, b in ((k, t), (k, 63 - t), (t, k), (63 - t, k)):
                im.set(a, b, cage)
    return im


def ceiling(n, part):
    rnd = random.Random(1500 + n * 7 + ord(part))
    if n == 1:
        c = (234, 226, 204)
        im = flat(c, 1500 + n, 3)
        if part == "L":                                          # coffers, a globe in each
            im.frame(0, 0, 64, 64, shade(GILT, 0.85), 2)
            im.frame(5, 5, 59, 59, shade(c, 0.8), 2)
            im.rect(7, 7, 57, 57, shade(c, 0.92))
            im.disc(31.5, 31.5, 11, shade(GILT, 0.9))
            im.disc(31.5, 31.5, 9, (255, 248, 214))
        elif part == "P":                                        # brick vaulting, whitewashed
            for y in range(0, 64, 8):
                im.rect(0, y, 64, y + 1, shade(c, 0.8))
                for x in range(4 if y % 16 else 0, 64, 16):
                    im.rect(x, y, x + 1, y + 8, shade(c, 0.8))
        else:
            im.frame(0, 0, 64, 64, shade(c, 0.86), 1)
            if part in "CE":
                im.disc(31.5, 31.5, 8, shade(c, 0.7))
                im.disc(31.5, 31.5, 6.5, (255, 248, 214))
            else:                                                # a green shade over a bench
                im.disc(31.5, 31.5, 9, (52, 78, 62))
                im.disc(31.5, 31.5, 4, (255, 248, 214))
    elif n == 2:
        c = (228, 228, 222)
        im = flat(c, 1500 + n, 2)
        if part == "P":
            im = flat(shade(CONC, 0.9), 1502, 5)
            im.rect(0, 28, 64, 36, (60, 110, 170))
            im.rect(0, 28, 64, 30, (96, 150, 206))
        elif part in "LE":                                       # a lit grid
            for k in range(0, 64, 16):
                im.rect(k, 0, k + 1, 64, AL)
                im.rect(0, k, 64, k + 1, AL)
            for x0, y0 in ((1, 1), (33, 33)):
                im.rect(x0, y0, x0 + 15, y0 + 15, (252, 252, 240))
        else:                                                    # acoustic tile and a strip light
            for y in range(2, 64, 4):
                for x in range(2, 64, 4):
                    im.set(x, y, shade(c, 0.7))
            im.frame(0, 0, 64, 64, (190, 190, 184), 1)
            im.rect(6, 26, 58, 38, (170, 174, 176))
            im.rect(8, 28, 56, 36, (252, 252, 238))
    else:
        c = (190, 182, 152)
        im = flat(c, 1500 + n, 5)
        blot(im, rnd.randrange(10, 54), rnd.randrange(10, 54), rnd.randrange(10, 18), (96, 78, 48), 0.35, wrap=True)
        if part == "P":
            im = wet((120, 114, 100), 1503, rust=True, drain=False)
        else:
            for k in range(3):                                   # cracks in the plaster
                x, y = rnd.randrange(64), rnd.randrange(64)
                for i in range(rnd.randrange(12, 30)):
                    im.set(x % 64, y % 64, shade(c, 0.6))
                    x += rnd.choice((0, 1, 1))
                    y += rnd.choice((-1, 0, 1))
            im.rect(12, 28, 52, 36, (120, 116, 104))             # a bare tube on a batten
            if part != "A":                                      # (the archive's has gone)
                im.rect(14, 30, 50, 34, (255, 252, 226))
            else:
                im.rect(14, 30, 50, 34, (150, 146, 130))
    return im


def tops(n):
    out = {}
    out["DT"] = {1: flat((60, 88, 66), 1601), 2: flat((236, 236, 230), 1602, 3), 3: lino((150, 124, 90), 1603, 12, 0)}[n]
    out["UT"] = {1: planks(shade(OAK, 1.2), 1611, 32), 2: flat((236, 236, 230), 1612, 3), 3: lino(LINO, 1613, 16, 0)}[n]
    out["BT"] = {1: flat((36, 34, 36), 1621), 2: flat((236, 236, 230), 1622, 3), 3: lino((96, 98, 84), 1623, 20, 0)}[n]
    if n == 1:                                                   # a white cloth, a cruet
        t = flat((236, 232, 220), 1631, 3)
        t.frame(2, 2, 62, 62, (214, 208, 194), 1)
        t.disc(31.5, 31.5, 4, (200, 196, 186))
        t.disc(31.5, 31.5, 2, (150, 60, 40))
    elif n == 2:                                                 # orange formica, an aluminium edge
        t = flat(ORANGE, 1632, 3)
        t.frame(0, 0, 64, 64, AL, 2)
    else:                                                        # oilcloth in a check, rubbed through
        t = checker((150, 60, 50), (214, 204, 180), 8, 1633)
        rnd = random.Random(1634)
        for _ in range(5):
            blot(t, rnd.randrange(64), rnd.randrange(64), rnd.randrange(5, 11), (176, 160, 130), 0.6, wrap=True)
    out["TT"] = t
    p = {1: flat((60, 64, 68), 1641), 2: flat((60, 62, 66), 1642), 3: flat((60, 62, 52), 1643)}[n]
    for k in range(4, 64, 8):
        p.rect(k, 4, k + 2, 60, shade(tuple(p.px[0][:3]), 1.5))  # tread plate
    out["PT"] = p
    out["GT"] = {1: parquet(shade(OAK, 1.15), 1651), 2: lino((150, 158, 150), 1652, 6), 3: lino(LINO, 1653, 34)}[n]
    return out


def floors(n):
    if n == 1:
        return dict(FL=checker((112, 48, 44), (186, 178, 164), 32, 1701, (70, 60, 56)), FC=parquet(OAK, 1702),
                    FA=checker(TERRA, shade(TERRA, 0.86), 16, 1703, (96, 60, 44)),
                    FN=checker((214, 190, 120), (120, 74, 48), 16, 1704, (90, 70, 50)), FR=planks((140, 100, 62), 1705),
                    FP=wet((104, 104, 100), 1706), FE=checker((150, 154, 156), (138, 142, 146), 32, 1707, (84, 86, 90)))
    if n == 2:
        return dict(FL=terrazzo((176, 172, 160), 1711), FC=lino((128, 150, 134), 1712, 4),
                    FA=checker((182, 186, 184), (150, 156, 158), 16, 1713), FN=terrazzo((206, 196, 172), 1714, False),
                    FR=lino((120, 136, 150), 1715, 4), FP=grating(1716), FE=lined((150, 154, 156), 1717, YELLOW))
    return dict(FL=lino(LINO, 1721, 46), FC=lino((120, 96, 70), 1722, 40, 0), FA=lino((110, 122, 104), 1723, 36),
                FN=checker((176, 150, 96), (104, 70, 50), 16, 1724, (70, 56, 44)),
                FR=planks((112, 66, 44), 1725, 16, (150, 126, 96)), FP=wet((96, 92, 84), 1726, rust=True),
                FE=lined((132, 130, 124), 1727, (190, 160, 70), 5))


# === pictures: one to a piece of wall ============================================
def on_wall(n, part, w, shift=0):
    """The wall `part`, w wide, starting `shift` into its 64."""
    base = wall(n, part)
    im = Img(w, base.h)
    for y in range(base.h):
        for x in range(w):
            im.px[y * w + x] = list(base.px[y * 64 + (x + shift) % 64])
    return im


def plate(im, s, cx, y, n, sc=1):
    """A name on a plate, centred at cx with its top at y."""
    ground, ink = PLATE[n]
    tw = len(s) * 6 * sc - sc
    x0 = cx - tw // 2
    im.rect(x0 - 3, y, x0 + tw + 3, y + 5 * sc + 6, ground)
    im.frame(x0 - 3, y, x0 + tw + 3, y + 5 * sc + 6, shade(ink, 0.8) if n != 3 else (90, 84, 70), 1)
    text(im, s, x0, y + 3, ink, sc)


def sign(n, part, s, shift, w, oh=96):
    """The wall over a way through it, with the name of what is beyond: the
    plate is just over the opening, whose head is `oh` above the floor."""
    im = on_wall(n, part, w, shift)
    plate(im, s, w // 2, im.h - oh - 15, n)
    return im


def leaf(n, keys):
    """A locked door's leaf, 64 by 96, with a plate for each key it asks for."""
    rnd = random.Random(1800 + n)
    c = {1: OAK, 2: (206, 210, 212), 3: (96, 104, 96)}[n]
    im = Img(64, 96, c)
    for y in range(96):
        for x in range(64):
            g = 1 + (0.05 * math.sin(x * 0.9 + 2 * math.sin(y * 0.06)) if n == 1 else 0) + rnd.uniform(-0.02, 0.02)
            im.set(x, y, shade(c, g))
    im.frame(0, 0, 64, 96, shade(c, 0.5), 3)
    if n == 1:
        for y1, y2 in ((8, 44), (52, 90)):
            im.frame(9, y1, 55, y2, shade(c, 0.6), 2)
            im.frame(11, y1 + 2, 53, y2 - 2, shade(c, 1.25), 1)
    elif n == 2:                                                 # flush, with a round window
        im.disc(31.5, 24, 10, AL)
        im.disc(31.5, 24, 8, (40, 52, 64))
        im.rect(6, 86, 58, 92, AL)
    else:                                                        # sheet steel, a spy-hole, a stencil
        for y in (10, 46, 84):
            im.rect(3, y, 61, y + 2, shade(c, 0.7))
            for x in (8, 32, 56):
                im.disc(x, y + 1, 1.5, shade(c, 1.4))
        im.disc(31.5, 22, 2.5, (30, 30, 30))
        drips(im, rnd, 3, RUST, 12, 70)
    for k, ch in enumerate(keys):                                # as gfx.py's locked door
        x = 32 - 9 * len(keys) + 18 * k + 1
        im.rect(x, 54, x + 16, 74, (206, 180, 96))
        im.frame(x, 54, x + 16, 74, (110, 88, 36), 1)
        digit(im, ch, x + 5, 57, (60, 40, 16))
        im.rect(x + 7, 69, x + 9, 72, (30, 22, 10))
    im.noise(3, 1805 + n)
    return im


def face(n, part, shift, keys, s=""):
    """A door's face: the wall of the room it is seen from, the leaf at its
    foot, and (`s`) a name over it."""
    im = on_wall(n, part, 64, shift)
    im.rect(0, im.h - 100, 64, im.h - 96, {1: shade(OAK, 0.6), 2: AL, 3: (60, 62, 60)}[n])
    paste(im, leaf(n, keys), 0, im.h - 96)
    if s:
        plate(im, s, 32, im.h - 96 - 19, n)
    return im


def street_doors(n):
    """128 wide: the doors you came in by, shut."""
    im = on_wall(n, "LB", 128)
    c = {1: OAK, 2: AL, 3: (86, 92, 88)}[n]
    glass = (150, 176, 190) if n != 3 else (96, 104, 104)
    top = 256 - 140
    im.rect(8, top - 6, 120, 256, shade(c, 0.6))
    for x0 in (12, 65):
        im.rect(x0, top, x0 + 51, 254, c)
        im.frame(x0, top, x0 + 51, 254, shade(c, 0.7), 1)
        if n == 3:                                               # padded, studded; a small wired pane
            for y in range(top + 6, 250, 12):
                for x in range(x0 + 6 + (6 if (y // 12) % 2 else 0), x0 + 48, 12):
                    im.set(x, y, (190, 180, 150))
            im.rect(x0 + 16, top + 14, x0 + 36, top + 40, glass)
            for k in range(0, 20, 5):
                im.rect(x0 + 16 + k, top + 14, x0 + 17 + k, top + 40, shade(glass, 0.6))
        else:
            im.rect(x0 + 7, top + 8, x0 + 44, top + 96, glass)
            for i in range(30):
                blend(im, x0 + 12 + i, top + 70 - i, (255, 255, 255), 0.3)
            if n == 1:
                im.rect(x0 + 7, top + 50, x0 + 44, top + 53, c)
                im.rect(x0 + 24, top + 8, x0 + 27, top + 96, c)
                im.frame(x0 + 9, top + 104, x0 + 42, 248, shade(c, 0.62), 2)
            else:
                im.rect(x0 + 2, 244, x0 + 49, 252, shade(c, 0.8))
    for x in (59, 67):
        im.rect(x, top + 60, x + 2, top + 92, METAL[n] if n != 3 else (40, 40, 40))
    plate(im, "ENTRANCE" if n != 3 else "PASSES", 64, top - 26, n)
    im.noise(2, 1810 + n)
    return im


def long_wall(n):
    """256 wide, on the lobby's north wall: what the institute says of itself."""
    im = on_wall(n, "LB", 256)
    rnd = random.Random(1820 + n)
    if n == 1:                                                   # a painting in a gilt frame: an open door, light through it
        x1, y1, x2, y2 = 36, 40, 220, 150
        im.rect(x1 - 6, y1 - 6, x2 + 6, y2 + 6, GILT)
        im.frame(x1 - 6, y1 - 6, x2 + 6, y2 + 6, shade(GILT, 0.6), 1)
        im.frame(x1 - 2, y1 - 2, x2 + 2, y2 + 2, shade(GILT, 0.6), 1)
        for y in range(y1, y2):
            for x in range(x1, x2):
                im.set(x, y, mix((40, 48, 70), (96, 84, 74), (y - y1) / (y2 - y1)))
        for y in range(y1 + 60, y2):                             # a floor going off
            for x in range(x1, x2):
                im.set(x, y, shade((120, 84, 56), 0.7 + 0.3 * (y - y1 - 60) / 50 - (0.12 if (x - 128) * 60 // (y - y1 - 40) % 2 else 0)))
        im.rect(108, y1 + 14, 148, y1 + 84, (250, 240, 200))     # the door's opening, lit
        im.frame(106, y1 + 12, 150, y1 + 84, (70, 50, 36), 2)
        for k in range(26):                                      # the leaf, ajar
            im.rect(148 + k, y1 + 14 + k // 3, 149 + k, y1 + 84 + k // 2, shade((40, 150, 140), 1 - k * 0.012))
        for i in range(70):                                      # light across the floor
            for k in range(-i // 3, i // 3 + 1):
                blend(im, 128 + k, y1 + 84 + i * 26 // 70, (250, 240, 200), 0.5 * (1 - i / 70))
        for x, hgt in ((70, 44), (84, 40), (176, 46), (192, 42)):   # staff in white coats, looking at it
            im.rect(x, y2 - hgt, x + 9, y2 - 6, (226, 224, 214))
            im.disc(x + 4.5, y2 - hgt - 5, 4, (196, 160, 130))
            im.rect(x + 1, y2 - 6, x + 8, y2, (50, 50, 56))
        plate(im, "THE FIRST DOOR", 128, 160, n)
    elif n == 2:                                                 # a mosaic the width of the wall
        x1, y1, x2, y2 = 8, 20, 248, 156
        cols = ((30, 70, 130), (40, 96, 160), (24, 56, 110))
        for ty in range(y1, y2, 4):
            for tx in range(x1, x2, 4):
                cx, cy = tx - 128, ty - 88
                d = (cx * cx + cy * cy) ** 0.5
                c = rnd.choice(cols)
                for k, (a, b, rot) in enumerate(((100, 34, 0.5), (100, 34, -0.5), (60, 60, 0))):   # orbits
                    u = cx * math.cos(rot) + cy * math.sin(rot)
                    v = -cx * math.sin(rot) + cy * math.cos(rot)
                    if abs((u / a) ** 2 + (v / b) ** 2 - 1) < 0.09:
                        c = (240, 236, 220) if k < 2 else YELLOW
                if d < 14:
                    c = ORANGE if d < 9 else YELLOW
                if abs(cx) < 14 and -70 < cy < -30 and d > 30:
                    c = c
                if rnd.random() < 0.02:
                    c = (240, 236, 220)                          # stars
                im.rect(tx, ty, tx + 4, ty + 4, (150, 156, 160))
                im.rect(tx, ty, tx + 3, ty + 3, shade(c, rnd.uniform(0.9, 1.06)))
        # a door, small, on one orbit
        im.rect(204, 68, 216, 92, (40, 170, 160))
        im.frame(204, 68, 216, 92, (240, 236, 220), 1)
        im.frame(x1 - 2, y1 - 2, x2 + 2, y2 + 2, AL, 2)
    else:                                                        # a board of honour, its photographs gone grey
        x1, y1, x2, y2 = 20, 34, 236, 126
        im.rect(x1, y1, x2, y2, (120, 40, 36))
        im.frame(x1, y1, x2, y2, (128, 104, 74), 3)
        text(im, "OUR BEST WORKERS", x1 + 12, y1 + 8, (226, 200, 120), 2)
        for k in range(8):
            x0 = x1 + 14 + k * 25
            if k in (2, 5):                                      # two have been taken down
                im.rect(x0, y1 + 30, x0 + 19, y1 + 56, (104, 34, 30))
            else:
                g = rnd.randrange(120, 170)
                im.rect(x0, y1 + 30, x0 + 19, y1 + 56, (g, g, g - 10))
                im.disc(x0 + 9.5, y1 + 39, 4, (g - 50, g - 50, g - 56))
                im.rect(x0 + 4, y1 + 45, x0 + 15, y1 + 56, (g - 60, g - 60, g - 64))
            im.rect(x0, y1 + 60, x0 + 19, y1 + 64, (214, 204, 170))
            for kk in range(2):
                im.rect(x0 + 1, y1 + 68 + kk * 5, x0 + 4 + rnd.randrange(8, 15), y1 + 69 + kk * 5, (214, 204, 170))
        drips(im, rnd, 4, (70, 56, 40), y2, 40)
    im.noise(2, 1825 + n)
    return im


def notices(n):
    """128 wide: the clock, and what visitors are told."""
    im = on_wall(n, "LB", 128)
    rnd = random.Random(1830 + n)
    rim = METAL[n]
    im.disc(30, 70, 17, rim)
    im.disc(30, 70, 15, (240, 236, 220) if n != 3 else (206, 198, 168))
    for k in range(12):
        t = k * math.pi / 6
        im.set(int(30 + 12 * math.sin(t)), int(70 - 12 * math.cos(t)), (30, 30, 30))
    for t, ln in ((1.5 * math.pi + 0.0, 9), (0.0, 12)):           # a quarter to: the time door's clock
        for k in range(ln):
            im.set(int(30 + k * math.sin(t)), int(70 - k * math.cos(t)), (30, 30, 30))
    ground, ink = PLATE[n]
    im.rect(56, 48, 122, 96, ground)
    im.frame(56, 48, 122, 96, rim if n != 3 else (90, 84, 70), 1)
    for k, s in enumerate(("VISITORS", "BY", "APPOINTMENT", "ONLY")):
        text(im, s, 89 - (len(s) * 6 - 1) // 2, 53 + k * 10, ink, 1)
    if n == 3:
        for k in range(3):                                       # orders pinned up under it
            x0 = 58 + k * 22
            im.rect(x0, 102 + k % 2 * 3, x0 + 18, 126 + k % 2 * 3, (226, 220, 196))
            for y in range(106, 124, 4):
                im.rect(x0 + 2, y + k % 2 * 3, x0 + 4 + rnd.randrange(6, 13), y + 1 + k % 2 * 3, (90, 86, 80))
    im.noise(2, 1835 + n)
    return im


def coats(n):
    """64 by 160: a rail of pegs and what hangs on it, numbered."""
    im = on_wall(n, "CK", 64)
    rnd = random.Random(1840 + n)
    rail = METAL[n] if n != 3 else (70, 70, 66)
    im.rect(0, 40, 64, 43, rail)
    for k, x in enumerate(range(3, 64, 15)):
        im.rect(x + 5, 43, x + 7, 47, rail)
        im.disc(x + 6, 36, 3.5, (236, 228, 204))                 # the number
        if rnd.random() < (0.3 if n == 3 else 0.75):
            c = shade(rnd.choice(((60, 60, 70), (96, 80, 60), (70, 84, 70), (110, 100, 90), (50, 60, 90))), rnd.uniform(0.8, 1.2))
            hh = rnd.randrange(46, 62)
            for y in range(47, 47 + hh):
                w = 4 + min(3, (y - 47) // 4)
                for xx in range(x + 6 - w, x + 6 + w + 1):
                    im.set(xx, y, shade(c, 0.8 + 0.3 * abs(xx - x - 6) / w))
            im.rect(x + 6, 50, x + 7, 47 + hh, shade(c, 0.6))
    im.noise(2, 1845 + n)
    return im


def blackboard(n):
    im = on_wall(n, "LA", 128)
    rnd = random.Random(1850 + n)
    c = (38, 60, 50) if n != 2 else (56, 70, 64)
    im.rect(6, 60, 122, 136, WOOD[n] if n != 2 else AL)
    im.rect(9, 63, 119, 131, c)
    chalk = (226, 226, 214)
    # two frames, an arrow from one into the other and out again
    for x0 in (22, 82):
        im.frame(x0, 76, x0 + 14, 104, chalk, 1)
    for x in range(38, 80, 3):
        im.set(x, int(90 - 8 * math.sin((x - 38) * math.pi / 42)), chalk)
    im.rect(76, 86, 80, 87, chalk)
    for y in range(110, 128, 6):                                 # and the working, rubbed at
        x = 14
        while x < 100:
            k = rnd.randrange(3, 9)
            if rnd.random() < 0.8:
                im.rect(x, y, x + k, y + 1, shade(chalk, rnd.uniform(0.55, 1)))
            x += k + rnd.randrange(2, 5)
    text(im, "A - B - A", 34, 66, chalk, 1)
    if n == 3:
        blot(im, 90, 100, 22, (120, 130, 122), 0.3)
    im.rect(6, 132, 122, 136, shade(WOOD[n], 0.8))
    im.noise(2, 1855 + n)
    return im


def cabinets(n):
    """128 wide: glazed cabinets of lenses and prisms."""
    im = on_wall(n, "LA", 128)
    rnd = random.Random(1860 + n)
    c = {1: OAK, 2: (206, 210, 212), 3: KHAKI}[n]
    im.rect(4, 70, 124, 248, c)
    im.frame(4, 70, 124, 248, shade(c, 0.6), 2)
    for x0 in (8, 66):
        im.rect(x0, 76, x0 + 54, 180, (58, 66, 70))
        for sy in (100, 126, 152, 178):
            im.rect(x0, sy, x0 + 54, sy + 2, shade(c, 0.9))
            x = x0 + 3
            while x < x0 + 48:
                k = rnd.choice("lpb")
                if n == 3 and rnd.random() < 0.4:
                    x += 9
                    continue
                if k == "l":                                     # a lens on a stand
                    im.disc(x + 3.5, sy - 9, 4, (176, 214, 226))
                    im.disc(x + 3.5, sy - 9, 2.5, (220, 240, 246))
                    im.rect(x + 3, sy - 5, x + 4, sy, (150, 130, 80))
                elif k == "p":                                   # a prism
                    for i in range(8):
                        im.rect(x + 4 - i // 2, sy - 8 + i, x + 5 + i // 2, sy - 7 + i, (200, 226, 232))
                else:                                            # a brass tube
                    im.rect(x, sy - 6, x + 8, sy - 2, (190, 156, 84))
                    im.rect(x, sy - 6, x + 2, sy - 2, (60, 60, 60))
                x += 10
        for i in range(40):
            blend(im, x0 + 6 + i, 150 - i, (255, 255, 255), 0.2)
        im.frame(x0, 76, x0 + 54, 180, shade(c, 0.6), 1)
        im.frame(x0 + 2, 188, x0 + 52, 242, shade(c, 0.62), 1)   # cupboards under
        im.rect(x0 + 25, 212, x0 + 29, 216, METAL[n] if n != 3 else (60, 60, 56))
    im.noise(2, 1865 + n)
    return im


def menu(n):
    im = on_wall(n, "CA", 128)
    rnd = random.Random(1870 + n)
    ground, ink = PLATE[n]
    y0 = 150
    im.rect(16, y0, 112, y0 + 66, ground if n != 1 else (36, 44, 40))
    im.frame(16, y0, 112, y0 + 66, WOOD[n] if n != 2 else AL, 2)
    text(im, "MENU", 41, y0 + 6, ink if n != 1 else (226, 226, 214), 2)
    dishes = ("SOUP", "CUTLETS", "BUCKWHEAT", "COMPOTE", "TEA")
    for k, s in enumerate(dishes):
        if n == 3 and k in (1, 3):                               # none today
            im.rect(24, y0 + 25 + k * 8, 24 + len(s) * 6, y0 + 26 + k * 8, ink)
            continue
        text(im, s, 24, y0 + 22 + k * 8, ink if n != 1 else (226, 226, 214), 1)
        im.rect(96, y0 + 24 + k * 8, 106, y0 + 25 + k * 8, ink if n != 1 else (226, 226, 214))
    im.noise(2, 1875 + n)
    return im


def card_index(n):
    """128 wide: a wall of small drawers, each with its label."""
    im = on_wall(n, "AR", 128)
    rnd = random.Random(1880 + n)
    c = {1: OAK, 2: (150, 158, 164), 3: KHAKI}[n]
    im.rect(2, 96, 126, 250, shade(c, 0.6))
    for y in range(98, 246, 14):
        for x in range(4, 124, 20):
            if n == 3 and rnd.random() < 0.08:                   # one pulled out and gone
                im.rect(x, y, x + 19, y + 13, (20, 20, 20))
                continue
            f = rnd.uniform(0.92, 1.06)
            im.rect(x, y, x + 19, y + 13, shade(c, f))
            im.rect(x, y, x + 19, y + 1, shade(c, f * 1.2))
            im.rect(x + 4, y + 3, x + 15, y + 8, (232, 226, 204))
            im.rect(x + 8, y + 10, x + 11, y + 12, METAL[n] if n != 3 else (60, 60, 56))
    plate(im, "A - Z", 64, 78, n)
    im.noise(2, 1885 + n)
    return im


def gauges(n):
    """128 by 192, in the pump room: a board of dials over valves."""
    im = on_wall(n, "PU", 128)
    rnd = random.Random(1890 + n)
    c = {1: (60, 44, 34), 2: (206, 210, 212), 3: (86, 88, 76)}[n]
    im.rect(10, 40, 118, 110, c)
    im.frame(10, 40, 118, 110, shade(c, 0.6), 2)
    for k, x in enumerate((30, 64, 98)):
        dial(im, x, 66, 13, METAL[n], (0.2, 0.55, 0.9)[k] if n != 3 else 0.02)
        im.rect(x - 9, 88, x + 9, 96, (232, 226, 204))
    pipe = {1: (150, 96, 60), 2: (60, 110, 170), 3: (110, 70, 44)}[n]
    for x in (30, 64, 98):                                       # a pipe down from each, a wheel on it
        for dx in range(-3, 4):
            im.rect(x + dx, 110, x + dx + 1, 192, shade(pipe, 1.2 - 0.14 * abs(dx)))
        im.disc(x, 146, 9, (170, 40, 34) if n != 2 else YELLOW)
        im.disc(x, 146, 6, shade(pipe, 0.5))
        im.rect(x - 8, 145, x + 9, 147, (170, 40, 34) if n != 2 else YELLOW)
        im.rect(x - 1, 138, x + 1, 155, (170, 40, 34) if n != 2 else YELLOW)
    if n == 3:
        drips(im, rnd, 5, RUST, 110, 70)
    im.noise(2, 1895 + n)
    return im


def control(n):
    """128 wide, in the experiment hall: the desk it was run from."""
    im = on_wall(n, "EX", 128)
    rnd = random.Random(1900 + n)
    c = {1: (40, 40, 44), 2: (206, 210, 212), 3: KHAKI}[n]
    im.rect(4, 100, 124, 250, c)
    im.frame(4, 100, 124, 250, shade(c, 0.55), 2)
    for k, x in enumerate((24, 52, 80, 104)):
        dial(im, x, 122, 10, METAL[n], (0.15, 0.5, 0.7, 0.95)[k] if n != 3 else 0.02)
    for r in range(4):
        for x in range(12, 118, 9):
            y = 144 + r * 12
            lamp = rnd.random() < (0.12 if n == 3 else 0.4)
            if lamp:
                im.disc(x + 1.5, y + 2, 2.5, rnd.choice(((230, 60, 40), (240, 200, 60), (90, 220, 110))))
            else:
                im.rect(x, y, x + 3, y + 5, (176, 176, 170) if n != 1 else (190, 156, 84))
    im.rect(4, 194, 124, 200, shade(c, 1.3))                     # the desk's edge
    im.rect(4, 200, 124, 202, shade(c, 0.5))
    im.rect(50, 206, 78, 216, (170, 40, 34))                     # the one big button
    text(im, "STOP", 53, 208, (240, 236, 220), 1)
    plate(im, "CONTROL", 64, 80, n)
    if n == 3:
        scuffs(im, rnd, 204, 248, 24, (60, 54, 44))
    im.noise(2, 1905 + n)
    return im


def warning(n):
    im = on_wall(n, "EX", 64)
    y0 = 92
    if n == 2:                                                   # a yellow triangle
        for i in range(34):
            im.rect(32 - i // 2 - 1, y0 + i, 32 + i // 2 + 1, y0 + i + 1, (36, 36, 40))
        for i in range(3, 31):
            im.rect(32 - (i - 3) // 2, y0 + i, 32 + (i - 3) // 2, y0 + i + 1, YELLOW)
        im.rect(31, y0 + 12, 33, y0 + 24, (36, 36, 40))
        im.rect(31, y0 + 26, 33, y0 + 28, (36, 36, 40))
    else:
        ground, ink = ((236, 232, 220), (170, 40, 34)) if n == 1 else PLATE[3]
        im.rect(5, y0, 59, y0 + 40, ground)
        im.frame(5, y0, 59, y0 + 40, ink, 2)
        for k, s in enumerate(("DO NOT", "OPEN", "ANYTHING")):
            text(im, s, 32 - (len(s) * 6 - 1) // 2, y0 + 6 + k * 10, ink, 1)
    im.noise(2, 1915 + n)
    return im


WEIGH_STEPS = 12        # the needle's places: none, the tenths to the mark (10), one past it


def weigh_dial(out, n):
    """MAP16's weighbridge dial (map16.zs, AjarWeighDial), a wall sprite in
    look n's steel: a round face with ten tenths to a red mark, a red band
    past it, and a lamp over it. Frames A to L: the needle at 0 to 11
    tenths; at the mark and past it (K, L) the lamp is green."""
    metal = METAL[n] if n else KHAKI
    ink, red, face = (28, 28, 30), (196, 36, 30), (240, 236, 218)
    cx, cy, r = 32, 48, 29

    def at(p, rad):
        t = math.pi * (0.75 + 1.5 * p / (WEIGH_STEPS - 1))
        return cx + rad * math.cos(t), cy + rad * math.sin(t)

    def stroke(im, p, r1, r2, c, w=1.0):
        for k in range(int(r1 * 4), int(r2 * 4) + 1):
            x, y = at(p, k / 4)
            im.disc(x, y, w, c)

    for k in range(WEIGH_STEPS):
        im = Img(64, 84, (0, 0, 0, 0))
        im.rect(2, 0, 62, 84, shade(metal, 0.8))                 # the housing: a steel plate, riveted
        im.frame(2, 0, 62, 84, shade(metal, 0.45), 2)
        for x, y in ((6, 4), (57, 4), (6, 79), (57, 79)):
            im.disc(x, y, 1, shade(metal, 0.4))
        im.disc(32, 9, 7, shade(metal, 0.4))                     # the lamp
        im.disc(32, 9, 5, (90, 236, 110) if k >= 10 else (70, 54, 46))
        if k >= 10:
            im.disc(31, 8, 1.5, (210, 255, 210))
        im.disc(cx, cy, r + 1, shade(metal, 0.45))               # the face
        im.disc(cx, cy, r - 1, face)
        for y in range(cy - r, cy + r + 1):                      # the red band, from the mark on
            for x in range(cx - r, cx + r + 1):
                d = math.hypot(x - cx, y - cy)
                t = math.atan2(y - cy, x - cx) / math.pi % 2
                q = ((t - 0.75) % 2) / 1.5 * (WEIGH_STEPS - 1)
                if r - 9 <= d <= r - 2 and 9.85 <= q <= 11.7:
                    im.set(x, y, red)
        for p in range(10):                                      # a tick at each tenth
            stroke(im, p, r - 7 if p % 5 == 0 else r - 5, r - 3, ink, 0.6)
        stroke(im, 10, r - 16, r - 2, red, 1.8)                  # the mark
        stroke(im, k, 0, r - 5, ink, 1.3)                        # the needle
        im.disc(cx, cy, 3, ink)
        im.disc(cx, cy, 1, shade(metal, 1.2))
        im.noise(2, 1950 + k)
        out[f"sprites/AJWG{'ABCDEFGHIJKL'[k]}0.png"] = im.png(grab=(32, 84))


def make(out, signs={}, faces={}, looks=LOOKS):
    """`signs`, `faces`: what the map asks for (map_institute1.SIGNS, FACES):
    {(look, wall, words, shift, width, the opening's height): name},
    {(look, wall, shift, keys, words): name}."""
    def put(kind, nm, im):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = im.png()

    for n in looks:
        for p in WALLS:
            put("textures", name(p, n), wall(n, p))
        put("textures", name("PI", n), pillar(n))
        put("textures", name("DS", n), cabinet(n, 40, "desk"))
        put("textures", name("US", n), cabinet(n, 48, "counter"))
        for tag, h in (("B4", 48), ("B6", 64), ("B9", 96)):
            put("textures", name(tag, n), cabinet(n, h))
        put("textures", name("PS", n), cabinet(n, 64, "platform"))
        put("textures", name("TS", n), table(n))
        put("textures", name("GF", n), servery(n))
        put("textures", name("SK", n), stack(n))
        put("textures", name("TK", n), tank(n))
        put("textures", name("MC", n), machine(n))
        for tag, fn in (("ST", street_doors), ("MO", long_wall), ("NB", notices), ("CT", coats), ("BB", blackboard),
                        ("CB", cabinets), ("MN", menu), ("CI", card_index), ("GA", gauges), ("CP", control), ("WS", warning)):
            put("textures", name(tag, n), fn(n))
        for tag, im in list(floors(n).items()) + list(tops(n).items()):
            put("flats", name(tag, n), im)
        for part in "LCAPE":
            put("flats", name("K" + part, n), ceiling(n, part))
        put("flats", name("KQ", n), pump_lamp(n))
    for (n, part, s, shift, w, oh), nm in signs.items():
        put("textures", nm, sign(int(n), part, s, shift, w, oh))
    for (n, part, shift, keys, s), nm in faces.items():
        put("textures", nm, face(int(n), part, shift, keys, s))


if __name__ == "__main__":
    # swatches for the look board: python3 tools/gfx_institute.py <dir>
    import os
    import sys
    import gfx
    out = gfx.make_all()
    os.makedirs(sys.argv[1], exist_ok=True)
    for key, data in out.items():
        if "/AJI" in key:
            with open(os.path.join(sys.argv[1], os.path.basename(key)), "wb") as f:
                f.write(data)
