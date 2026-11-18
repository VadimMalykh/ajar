"""MAP31's cinema: three looks (see AJAR_CINEMA in map_secret1.py).

  1 Palace   a picture palace of the 1930s: burgundy damask between gilt
             pilasters, walnut, black marble and cream, a carpet of gold
             scales, brass round the glass.
  2 Kino     a town cinema of the 1960s: perforated white panels over ash
             slats, mosaic and terrazzo, a painted plank floor, a red runner
             with green edges, speaker cabinets.
  3 Fleapit  the same sort of house in the 1980s, run down: hessian gone
             orange over brown gloss, three stripes, a swirl carpet with gum
             on it, stained ceiling tiles and strip lights, plastic seats.

Every name is AJY<part><look>. Walls (64 wide, laid by world position:
ALIGNED):
  H 256, G 288  a hall, the great hall     F 160  the foyer
  W 128  the way into a hall               B 128  a box
  L 128  a lobby behind a steel door       C 128  the closet: film cans
  BS 80  the side of a tall block          SP 32  the step down into a hall
  CS 40  the front of the box office's counter
Pictures (one to a wall piece, not aligned):
  S1, S2 256x96, S3 256x128  the screen of each hall, over the way in: a
                film leader's frame on it, counting down (3, 2, 1) from hall to
                hall; its sweep is at a quarter to, as the time door's clock
  TH, TG        the hall's wall over a time door: a dark lintel in it
                (aligned); TT (and flat) the door's dark surround
  SS 12, SB 24  a row of seats from the side: the seats' edge, their backs
                (aligned; two seats to 64)
  DH, DG, DL    the steel door let into a hall's, the great hall's, a lobby's wall
  GL 160x112    the frame of a box's glass: clear but for the frame; GT (and
                flat) its sill, head and sides
  PA..PF 64x160 posters of the town's other places, on the foyer's wall
  BO 128x160    the box office's window     ST 128x160  the street doors
  N<look><hall> the sign of a hall: 256x32 for the first, 64x32 for the others
Flats:
  HF, HC (128) a hall's floor and ceiling   FF, FC, FL the foyer's, and a lamp
  RG a runner 64 wide (its edges are in the middle of the flat: it lies from
     32 to 32)   BF, BC a box   LF, LC a lobby and the closet
  BT, BA the top of a tall block, and with the arrow   CT the counter   BE a bench
  SF a row of seats from above, two rows to the flat: the back is the north
     12 of every 32, so a row starts at a multiple of 32
"""
import math
import random

from gfx import DIGITS, Img, digit, shade, text, unpng
from gfx_bus import blend, mix

DIGITS.update({"K": ("10010", "10100", "11000", "10100", "10010"),
               "W": ("10001", "10001", "10101", "11011", "10001"),
               "X": ("10001", "01010", "00100", "01010", "10001")})

LOOKS = (1, 2, 3)
WALLS = ("H", "G", "F", "W", "B", "L", "C", "BS", "SP", "CS", "TH", "TG", "SS", "SB")
ALIGNED = {f"AJY{p}{n}" for p in WALLS for n in LOOKS}
LIGHT = {1: 148, 2: 160, 3: 144}                # a hall's light: the lights are down (they were 180, 200, 176)
SURROUND = {1: (34, 28, 30), 2: (58, 66, 76), 3: (44, 30, 24)}   # round a time door

GOLD, BRASS = (212, 172, 84), (196, 160, 80)
BURG, CREAM, WALNUT, MARBLE = (112, 26, 34), (228, 214, 180), (78, 48, 30), (30, 28, 32)
WHITE, ASH, BLUE, PLANK = (230, 230, 222), (196, 162, 108), (150, 176, 190), (132, 62, 40)
HESS, GLOSS, NICO, ORANGE = (168, 104, 52), (70, 46, 34), (188, 170, 128), (214, 120, 40)
STAIN = (70, 52, 30)


def name(part, n):
    return f"AJY{part}{n}"


def paste(dst, src, x0, y0):
    for y in range(src.h):
        for x in range(src.w):
            p = src.px[y * src.w + x]
            if p[3]:
                dst.set(x0 + x, y0 + y, p)


def tiled(src, w, h, bottom=False):
    """src repeated over w by h; `bottom`: its foot at the foot."""
    im = Img(w, h)
    off = (src.h - h % src.h) % src.h if bottom else 0
    for y in range(h):
        for x in range(w):
            im.px[y * w + x] = list(src.px[((y + off) % src.h) * src.w + x % src.w])
    return im


def blot(im, cx, cy, r, c, f, wrap=False):
    """A soft stain."""
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / r
            if d < 1:
                k = f * (1 - d) * (1.6 if d > 0.75 else 1)          # a tide mark at its rim
                if wrap:
                    blend(im, x % im.w, y % im.h, c, k)
                else:
                    blend(im, x, y, c, k)


def veins(im, y1, y2, rnd, c, n=3):
    for _ in range(n):
        x, y = rnd.randrange(im.w), y1
        while y < y2:
            blend(im, x % im.w, y, c, 0.5)
            x += rnd.choice((-1, 0, 1, 1))
            y += rnd.choice((0, 1, 1))


def folds(im, x1, x2, y1, y2, c, period=16, phase=0):
    """Cloth hanging in folds."""
    for x in range(x1, x2):
        f = 0.78 + 0.34 * (0.5 + 0.5 * math.cos((x + phase) * 2 * math.pi / period)) ** 2
        for y in range(y1, y2):
            im.set(x, y, shade(c, f))


# === walls ===================================================================
def wall(n, part, seed=0):
    h = {"H": 256, "G": 288, "F": 160}.get(part, 128)
    rnd = random.Random(310 + n * 17 + ord(part[0]) + seed)
    im = Img(64, h, CREAM)
    if n == 1:
        if part in "HG":
            im.rect(0, 0, 64, h, BURG)
            for y in range(22, h - 56):                          # damask: a lattice with a leaf in each lozenge
                for x in range(64):
                    u, v = (x + y) % 16, (x - y) % 16
                    if u == 0 or v == 0:
                        im.set(x, y, shade(BURG, 1.3))
                    elif abs(u - 8) + abs(v - 8) < 4:
                        im.set(x, y, shade(BURG, 0.8))
            for x in range(6):                                   # half a fluted gilt pilaster at each edge
                c = shade(GOLD, (1.05, 0.7, 1.0, 0.66, 0.95, 0.55)[x])
                im.rect(x, 22, x + 1, h - 56, c)
                im.rect(63 - x, 22, 64 - x, h - 56, c)
            for x1, x2 in ((0, 9), (55, 64)):
                im.rect(x1, 22, x2, 30, GOLD)
                im.rect(x1, 30, x2, 32, shade(GOLD, 0.6))
            cy = h - 150                                         # a gilt sunburst
            for y in range(-18, 1):
                for x in range(-18, 19):
                    d = (x * x + y * y) ** 0.5
                    if d <= 18:
                        ray = int((math.atan2(-y, x) / math.pi) * 9) % 2
                        im.set(32 + x, cy + y, shade(GOLD, 0.6 if d < 6 else 1.05 if ray else 0.72))
            im.rect(12, cy + 1, 52, cy + 3, shade(GOLD, 0.6))
            im.rect(0, 0, 64, 9, shade(CREAM, 1.04))             # the cornice, stepped
            im.rect(0, 9, 64, 14, GOLD)
            im.rect(0, 14, 64, 20, shade(CREAM, 0.86))
            for x in range(2, 64, 8):
                im.rect(x, 15, x + 4, 20, shade(CREAM, 1.02))
            im.rect(0, 20, 64, 22, shade(GOLD, 0.6))
            dado(im, h - 56, h, WALNUT, BRASS, rnd)
        elif part == "F":
            im.rect(0, 2, 64, 16, MARBLE)                        # a frieze of gilt chevrons
            for x in range(64):
                y = 4 + abs(x % 16 - 8)
                im.rect(x, y, x + 1, y + 3, GOLD)
            im.rect(0, 16, 64, 18, GOLD)
            for x in (0, 62):
                im.rect(x, 22, x + 2, 122, shade(CREAM, 0.84))
            im.rect(0, 124, 64, 160, MARBLE)
            veins(im, 126, 160, rnd, (120, 116, 110), 4)
            im.rect(0, 124, 64, 127, GOLD)
        elif part == "W":
            folds(im, 0, 64, 0, 128, shade(BURG, 1.15))
            im.rect(0, 0, 64, 8, GOLD)
            for x in range(64):
                im.rect(x, 8, x + 1, 9 + int(3 * abs(math.sin(x * math.pi / 16))), GOLD)
            for x in range(0, 64, 2):
                im.rect(x, 114, x + 1, 121, GOLD)
            im.rect(0, 112, 64, 114, shade(GOLD, 0.7))
            im.rect(0, 122, 64, 128, shade(MARBLE, 1.0))
        elif part == "B":
            pad = (96, 22, 30)
            for y in range(128):                                 # buttoned velvet
                for x in range(64):
                    d = (abs(x % 16 - 8) + abs(y % 16 - 8)) / 16
                    d2 = (abs((x + 8) % 16 - 8) + abs((y + 8) % 16 - 8)) / 16
                    im.set(x, y, shade(pad, 0.7 + 0.5 * min(d, d2) * 2))
            for y in range(0, 128, 8):
                for x in range(8 if y % 16 else 0, 64, 16):
                    im.set(x, y, GOLD)
            im.rect(0, 0, 64, 6, GOLD)
            im.rect(0, 6, 64, 7, shade(GOLD, 0.6))
            im.rect(0, 118, 64, 128, WALNUT)
        elif part == "L":
            im.rect(0, 0, 64, 128, (214, 200, 168))
            dado(im, 84, 128, (100, 62, 42), shade(CREAM, 0.7), rnd, panel=False)
    elif n == 2:
        if part in "HG":
            im.rect(0, 0, 64, h, WHITE)
            for y in range(20, h - 104, 4):                      # perforated panels, two to a width
                for x in range(2, 64, 4):
                    if x % 32 > 2 and (y - 20) % 64 > 3:
                        im.set(x, y, shade(WHITE, 0.55))
            for y in range(20, h - 104, 64):
                im.rect(0, y, 64, y + 1, shade(WHITE, 0.72))
            for x in (0, 32):
                im.rect(x, 20, x + 1, h - 104, shade(WHITE, 0.72))
            im.rect(0, 0, 64, 18, BLUE)                          # a painted band under the ceiling
            im.rect(0, 18, 64, 20, shade(ASH, 0.7))
            for x in range(64):                                  # ash slats
                f = (1.06, 1.0, 1.0, 0.98, 0.96, 0.9, 0.5, 0.42)[x % 8]
                im.rect(x, h - 104, x + 1, h - 10, shade(ASH, f * rnd.uniform(0.97, 1.03)))
            im.rect(0, h - 106, 64, h - 102, shade(ASH, 1.1))
            im.rect(0, h - 102, 64, h - 101, shade(ASH, 0.55))
            im.rect(0, h - 10, 64, h, (60, 60, 64))
        elif part == "F":
            im.rect(0, 0, 64, 160, WHITE)
            im.rect(0, 0, 64, 3, BLUE)
            for y in range(92, 156, 4):                          # a dado of small mosaic
                for x in range(0, 64, 4):
                    c = rnd.choice((BLUE, BLUE, shade(BLUE, 0.82), (198, 208, 206), (112, 150, 176)))
                    im.rect(x, y, x + 3, y + 3, c)
                    im.rect(x + 3, y, x + 4, y + 4, (176, 178, 172))
                    im.rect(x, y + 3, x + 4, y + 4, (176, 178, 172))
            im.rect(0, 90, 64, 92, shade(ASH, 0.8))
            im.rect(0, 156, 64, 160, (70, 70, 74))
        elif part == "W":
            im.rect(0, 0, 64, 128, ASH)                          # veneered sheets
            for x in range(64):
                for y in range(128):
                    g = 0.94 + 0.1 * math.sin((x % 32) * 0.9 + 2.5 * math.sin(y * 0.05 + x // 32))
                    im.set(x, y, shade(ASH, g))
            for x in (0, 32):
                im.rect(x, 0, x + 1, 128, shade(ASH, 0.55))
            im.rect(0, 120, 64, 128, (60, 60, 64))
            im.rect(0, 0, 64, 2, shade(ASH, 0.6))
        elif part == "B":
            grey = (168, 176, 172)
            im.rect(0, 0, 64, 128, grey)                         # pegboard
            for y in range(4, 84, 4):
                for x in range(2, 64, 4):
                    im.set(x, y, shade(grey, 0.6))
            im.rect(0, 84, 64, 122, shade(ASH, 0.9))
            for x in range(0, 64, 16):
                im.rect(x, 86, x + 1, 122, shade(ASH, 0.6))
            im.rect(0, 84, 64, 86, shade(ASH, 1.12))
            im.rect(0, 122, 64, 128, (60, 60, 64))
        elif part == "L":
            im.rect(0, 0, 64, 128, (222, 222, 212))              # whitewash over green oil paint
            green = (74, 118, 96)
            im.rect(0, 64, 64, 128, green)
            im.rect(0, 64, 64, 66, shade(green, 0.6))
            for y in range(66, 128):
                for x in range(64):
                    if rnd.random() < 0.04:
                        blend(im, x, y, (230, 240, 230), 0.25)
            im.rect(0, 122, 64, 128, shade(green, 0.5))
    else:
        if part in "HG":
            im.rect(0, 0, 64, h, HESS)
            for y in range(h - 80):                              # hessian: a coarse weave
                for x in range(64):
                    im.set(x, y, shade(HESS, 0.9 + 0.12 * ((x + y) % 2) + rnd.uniform(-0.06, 0.06)))
            for x in (0, 60):                                    # battens over the joins
                im.rect(x, 14, x + 4, h - 80, shade(GLOSS, 1.2))
            im.rect(0, 0, 64, 14, NICO)
            im.rect(0, 14, 64, 16, shade(GLOSS, 1.1))
            for _ in range(3):                                   # water from the roof
                x, n2 = rnd.randrange(6, 58), rnd.randrange(50, 130)
                for k in range(n2):
                    for dx in (-1, 0, 1):
                        blend(im, x + dx, 2 + k, STAIN, 0.42 * (1 - k / n2))
            blot(im, rnd.randrange(14, 50), 60, 13, STAIN, 0.28)
            im.rect(0, h - 80, 64, h, GLOSS)                     # brown gloss, scuffed
            im.rect(0, h - 80, 64, h - 77, shade(GLOSS, 1.5))
            for _ in range(26):
                x, y = rnd.randrange(64), rnd.randrange(h - 60, h - 4)
                for k in range(rnd.randrange(2, 9)):
                    blend(im, x + k, y, (150, 130, 104), 0.5)
            for x in range(64):
                for k in range(rnd.randrange(2, 7)):
                    blend(im, x, h - 1 - k, (30, 26, 22), 0.6)
        elif part == "F":
            for y in range(88):                                  # woodchip paper gone yellow
                for x in range(64):
                    im.set(x, y, shade(NICO, 1.08 + (0.07 if rnd.random() < 0.2 else 0) - (0.08 if rnd.random() < 0.1 else 0)))
            im.rect(0, 0, 64, 3, shade(NICO, 0.75))
            lam = (112, 76, 48)
            for x in range(64):                                  # wood-effect boards
                f = 0.58 if x % 16 == 0 else 1 + 0.08 * math.sin(x * 1.7) + rnd.uniform(-0.03, 0.03)
                im.rect(x, 88, x + 1, 160, shade(lam, f))
            im.rect(0, 88, 64, 91, shade(lam, 1.3))
            im.rect(0, 154, 64, 160, (40, 34, 30))
            blot(im, 44, 20, 14, STAIN, 0.22)
        elif part == "W":
            dark = (58, 44, 38)
            im.rect(0, 0, 64, 128, dark)
            for y1, c in ((40, ORANGE), (52, (226, 180, 60)), (64, (150, 70, 36))):
                im.rect(0, y1, 64, y1 + 9, c)
            for _ in range(30):
                x, y = rnd.randrange(64), rnd.randrange(30, 126)
                for k in range(rnd.randrange(2, 8)):
                    blend(im, x + k, y, (120, 104, 90), 0.4)
        elif part == "B":
            cork = (150, 108, 66)
            for y in range(128):                                 # cork tiles
                for x in range(64):
                    f = 0.6 if x % 32 == 0 or y % 32 == 0 else rnd.uniform(0.82, 1.1)
                    im.set(x, y, shade(cork, f))
            im.rect(0, 0, 64, 4, GLOSS)
            im.rect(0, 120, 64, 128, GLOSS)
            blot(im, 20, 30, 10, STAIN, 0.25)
        elif part == "L":
            blk = (176, 168, 150)
            for row in range(8):                                 # painted blockwork
                for col in range(-1, 3):
                    x0 = col * 32 + (16 if row % 2 else 0)
                    im.rect(x0, row * 16, x0 + 31, row * 16 + 15, shade(blk, rnd.uniform(0.93, 1.05)))
                    im.rect(x0 + 31, row * 16, x0 + 32, row * 16 + 16, shade(blk, 0.7))
                im.rect(0, row * 16 + 15, 64, row * 16 + 16, shade(blk, 0.7))
            for x in range(64):
                for k in range(rnd.randrange(8, 26)):
                    blend(im, x, 127 - k, (60, 54, 44), 0.35 * (1 - k / 26))
    if part == "C":                                              # the closet: shelves of film cans
        back = {1: (150, 132, 104), 2: (176, 184, 176), 3: (128, 116, 98)}[n]
        wood = {1: WALNUT, 2: ASH, 3: (104, 80, 56)}[n]
        im.rect(0, 0, 64, 128, back)
        for sy in (30, 62, 94, 126):
            x = 2
            while x < 60:
                w, cans = rnd.choice((13, 14, 15)), rnd.randrange(1, 6)
                for k in range(cans):
                    c = shade(rnd.choice(((150, 154, 160), (132, 136, 144), (160, 150, 120))), rnd.uniform(0.85, 1.05))
                    im.rect(x, sy - 5 * (k + 1), x + w, sy - 5 * k - 1, c)
                    im.rect(x, sy - 5 * (k + 1), x + w, sy - 5 * (k + 1) + 1, shade(c, 1.2))
                    if rnd.random() < 0.5:
                        im.rect(x + 3, sy - 5 * k - 4, x + 9, sy - 5 * k - 2, (226, 220, 200))
                x += w + 1
            im.rect(0, sy, 64, sy + 2, wood)
            im.rect(0, sy + 2, 64, sy + 4, shade(back, 0.7))
    im.noise(4, 310 + n)
    return im


def dado(im, y1, y2, c, rail, rnd, panel=True):
    im.rect(0, y1, 64, y2, c)
    for x in range(64):
        for y in range(y1, y2):
            if rnd.random() < 0.12:
                blend(im, x, y, shade(c, 1.4), 0.3)
    if panel:
        im.frame(5, y1 + 8, 59, y2 - 12, shade(c, 0.6), 2)
        im.frame(7, y1 + 10, 57, y2 - 14, shade(c, 1.25), 1)
    im.rect(0, y1, 64, y1 + 3, rail)
    im.rect(0, y1 + 3, 64, y1 + 4, shade(rail, 0.55))
    im.rect(0, y2 - 8, 64, y2, shade(MARBLE, 0.9))


def block_side(n):
    im = Img(64, 80, MARBLE)
    rnd = random.Random(320 + n)
    if n == 1:                                                   # a plinth of black marble, banded with gilt
        veins(im, 0, 80, rnd, (110, 106, 100), 5)
        im.rect(0, 0, 64, 5, GOLD)
        im.rect(0, 5, 64, 7, shade(GOLD, 0.6))
        im.rect(0, 68, 64, 71, GOLD)
        im.frame(6, 14, 58, 62, shade(GOLD, 0.8), 1)
    elif n == 2:                                                 # a loudspeaker cabinet: ash round a cloth front
        im.rect(0, 0, 64, 80, ASH)
        cloth = (86, 84, 76)
        for y in range(8, 70):
            for x in range(6, 58):
                im.set(x, y, shade(cloth, 0.86 + 0.2 * ((x + y) % 2)))
        im.frame(5, 7, 59, 71, shade(ASH, 0.6), 1)
        for x in (0, 63):
            im.rect(x, 0, x + 1, 80, shade(ASH, 0.6))
        im.rect(0, 74, 64, 80, (50, 50, 54))
    else:                                                        # a bank of plastic seats on a boxed riser
        im.rect(0, 0, 64, 80, (66, 52, 44))
        for x0 in (1, 33):
            im.rect(x0 + 2, 4, x0 + 28, 34, ORANGE)
            im.rect(x0 + 2, 4, x0 + 28, 7, shade(ORANGE, 1.2))
            im.rect(x0 + 10, 12, x0 + 20, 15, shade(ORANGE, 0.55))       # the hand hole
            im.rect(x0 + 2, 34, x0 + 28, 40, shade(ORANGE, 0.7))
            im.rect(x0 + 13, 40, x0 + 17, 50, (40, 40, 44))
        im.rect(0, 50, 64, 53, (110, 92, 76))
        for _ in range(14):
            x, y = rnd.randrange(64), rnd.randrange(54, 78)
            for k in range(rnd.randrange(2, 8)):
                blend(im, x + k, y, (130, 112, 96), 0.45)
    im.noise(4, 321 + n)
    return im


def block_top(n, arrow=False):
    rnd = random.Random(330 + n)
    if n == 1:
        im = Img(64, 64, (216, 204, 176))
        veins(im, 0, 64, rnd, (150, 136, 110), 4)
        im.frame(0, 0, 64, 64, MARBLE, 3)
        im.frame(3, 3, 61, 61, GOLD, 2)
    elif n == 2:
        im = Img(64, 64, ASH)
        for x in range(64):
            for y in range(64):
                im.set(x, y, shade(ASH, 0.95 + 0.08 * math.sin(y * 0.8 + 2 * math.sin(x * 0.07))))
        im.frame(0, 0, 64, 64, shade(ASH, 0.55), 2)
    else:
        im = Img(64, 64, (66, 52, 44))
        if not arrow:
            for x0 in (2, 34):                                   # seats from above: backs to the north
                for y0 in (2, 34):
                    im.rect(x0, y0, x0 + 28, y0 + 6, shade(ORANGE, 1.15))
                    im.rect(x0 + 1, y0 + 8, x0 + 27, y0 + 28, ORANGE)
                    im.frame(x0 + 1, y0 + 8, x0 + 27, y0 + 28, shade(ORANGE, 0.7), 1)
        else:
            im.rect(2, 2, 62, 62, (150, 140, 122))               # a sheet of board where the seats were
            im.frame(2, 2, 62, 62, (100, 90, 78), 1)
    if arrow:                                                    # pointing south (a flat's top is north)
        red = (196, 36, 28)
        im.rect(28, 10, 36, 40, red)
        for i in range(14):
            im.rect(32 - (14 - i), 40 + i, 32 + (14 - i), 41 + i, red)
    im.noise(4, 331 + n)
    return im


def step(n):
    c = {1: WALNUT, 2: (96, 100, 100), 3: (52, 42, 38)}[n]
    im = Img(64, 32, c)
    im.noise(6, 340 + n)
    im.rect(0, 0, 64, 3, {1: BRASS, 2: (190, 192, 190), 3: (226, 190, 50)}[n])
    im.rect(0, 3, 64, 4, shade(c, 0.5))
    if n == 3:                                                   # a yellow edge, worn through
        rnd = random.Random(343)
        for x in range(64):
            if rnd.random() < 0.3:
                im.rect(x, 0, x + 1, 3, (60, 52, 44))
    return im


def counter(n):
    c = {1: WALNUT, 2: ASH, 3: (112, 76, 48)}[n]
    side = Img(64, 40, c)
    side.noise(5, 350 + n)
    side.frame(4, 6, 60, 36, shade(c, 0.6), 2)
    side.rect(0, 0, 64, 3, {1: BRASS, 2: shade(ASH, 1.15), 3: shade(c, 0.5)}[n])
    side.rect(0, 36, 64, 40, shade(MARBLE, 1.0))
    top = Img(64, 64, {1: (44, 40, 44), 2: (206, 208, 200), 3: (150, 120, 84)}[n])
    top.noise(6, 351 + n)
    if n == 1:
        veins(top, 0, 64, random.Random(352), (130, 126, 120), 4)
    return side, top


def bench(n):
    if n == 1:                                                   # a banquette in buttoned velvet
        im = Img(64, 64, shade(BURG, 1.1))
        for y in range(8, 64, 16):
            for x in range(8, 64, 16):
                im.disc(x, y, 1, GOLD)
                blot(im, x, y, 6, (40, 8, 12), 0.35)
    elif n == 2:                                                 # slats
        im = Img(64, 64, ASH)
        for k in range(0, 64, 8):
            im.rect(0, k + 6, 64, k + 8, shade(ASH, 0.45))
            im.rect(0, k, 64, k + 1, shade(ASH, 1.12))
    else:                                                        # plastic shells
        im = Img(64, 64, (60, 50, 44))
        for x0 in (2, 34):
            for y0 in (2, 34):
                im.rect(x0, y0, x0 + 28, y0 + 28, ORANGE)
                im.frame(x0, y0, x0 + 28, y0 + 28, shade(ORANGE, 0.7), 1)
    im.noise(4, 355 + n)
    return im


# === flats ===================================================================
def hall_floor(n):
    rnd = random.Random(360 + n)
    if n == 1:                                                   # a carpet of gold scales on burgundy
        im = Img(64, 64, shade(BURG, 0.95))
        for y in range(64):
            for x in range(64):
                ox = 8 if (y // 8) % 2 else 0
                dx, dy = (x + ox) % 16 - 7.5, y % 8 - 8
                d = (dx * dx + dy * dy) ** 0.5
                if 7.2 <= d < 8.4:
                    im.set(x, y, shade(GOLD, 0.8))
                elif d < 2.2:
                    im.set(x, y, shade(BURG, 1.45))
        im.noise(5, 361)
    elif n == 2:                                                 # boards under floor paint
        im = Img(64, 64, PLANK)
        for x in range(64):
            b = x // 16
            f = 0.6 if x % 16 == 0 else 1.0 + 0.05 * math.sin(b * 2.1) + (0.1 if x % 16 in (6, 7) else 0)
            for y in range(64):
                im.set(x, y, shade(PLANK, f))
        for b in range(4):
            y = (b * 23 + 9) % 64
            im.rect(b * 16 + 1, y, b * 16 + 16, y + 1, shade(PLANK, 0.6))
        im.noise(4, 362)
    else:                                                        # a swirl carpet, trodden and gummed
        im = Img(128, 128, (104, 62, 40))
        for y in range(128):
            for x in range(128):
                dx, dy = x % 32 - 16, y % 32 - 16
                d = (dx * dx + dy * dy) ** 0.5
                a = math.atan2(dy, dx)
                v = math.sin(d * 0.9 + a * 2)
                c = ORANGE if v > 0.55 else (150, 84, 40) if v > 0 else (86, 50, 36) if v > -0.6 else (60, 40, 32)
                im.set(x, y, shade(c, 0.82))
        for _ in range(5):
            blot(im, rnd.randrange(128), rnd.randrange(128), rnd.randrange(12, 26), (70, 60, 52), 0.45, wrap=True)
        for _ in range(7):
            im.disc(rnd.randrange(4, 124), rnd.randrange(4, 124), 1.5, (34, 30, 30))
        im.noise(6, 363)
    return im


def coffer(im, x0, y0, n, lamp=False):
    if n == 1:
        im.rect(x0, y0, x0 + 64, y0 + 64, CREAM)
        im.frame(x0, y0, x0 + 64, y0 + 64, shade(GOLD, 0.8), 2)
        im.frame(x0 + 5, y0 + 5, x0 + 59, y0 + 59, shade(CREAM, 0.8), 2)
        im.rect(x0 + 7, y0 + 7, x0 + 57, y0 + 57, shade(CREAM, 0.9))
        im.frame(x0 + 14, y0 + 14, x0 + 50, y0 + 50, shade(CREAM, 0.78), 1)
        if lamp:
            im.disc(x0 + 31.5, y0 + 31.5, 13, GOLD)
            im.disc(x0 + 31.5, y0 + 31.5, 11, (255, 246, 206))
    elif n == 2:
        im.rect(x0, y0, x0 + 64, y0 + 64, (226, 226, 220))
        im.frame(x0, y0, x0 + 64, y0 + 64, (190, 190, 184), 1)
        if lamp:
            im.rect(x0 + 14, y0 + 14, x0 + 50, y0 + 50, (160, 162, 160))
            im.rect(x0 + 16, y0 + 16, x0 + 48, y0 + 48, (250, 252, 244))
            for k in (26, 37):
                im.rect(x0 + 16, y0 + k, x0 + 48, y0 + k + 1, (214, 218, 212))
    else:
        for tx in (0, 32):
            for ty in (0, 32):
                im.rect(x0 + tx, y0 + ty, x0 + tx + 32, y0 + ty + 32, shade(NICO, 1.1))
                im.frame(x0 + tx, y0 + ty, x0 + tx + 32, y0 + ty + 32, (120, 110, 90), 1)
        if lamp:                                                 # a strip light, its cover gone
            im.rect(x0 + 4, y0 + 22, x0 + 60, y0 + 42, (110, 104, 92))
            im.rect(x0 + 7, y0 + 26, x0 + 57, y0 + 38, (255, 252, 226))


def hall_ceiling(n):
    im = Img(128, 128)
    rnd = random.Random(370 + n)
    for k, (x0, y0) in enumerate(((0, 0), (64, 0), (0, 64), (64, 64))):
        coffer(im, x0, y0, n, lamp=k in (0, 3))
    if n == 3:
        for _ in range(60):
            im.set(rnd.randrange(128), rnd.randrange(128), (150, 136, 100))
        blot(im, 40, 96, 20, STAIN, 0.4)
        blot(im, 84, 50, 11, STAIN, 0.3)
    im.noise(3, 371 + n)
    return im


def small_ceiling(n, lamp=False):
    im = Img(64, 64)
    coffer(im, 0, 0, n, lamp)
    if n == 3:
        blot(im, 20, 44, 12, STAIN, 0.3)
    im.noise(3, 375 + n)
    return im


def foyer_floor(n):
    rnd = random.Random(380 + n)
    im = Img(64, 64)
    if n == 1:                                                   # black and cream marble
        for y in range(64):
            for x in range(64):
                im.set(x, y, MARBLE if (x // 32 + y // 32) % 2 else (220, 208, 180))
        veins(im, 0, 64, rnd, (128, 120, 108), 6)
    elif n == 2:                                                 # terrazzo between brass strips
        im.rect(0, 0, 64, 64, (164, 162, 152))
        for _ in range(420):
            x, y = rnd.randrange(64), rnd.randrange(64)
            c = rnd.choice(((214, 210, 198), (112, 110, 104), (150, 120, 100), (196, 190, 170)))
            im.rect(x, y, x + rnd.randrange(1, 3), y + rnd.randrange(1, 3), c)
        im.rect(0, 0, 64, 1, shade(BRASS, 0.9))
        im.rect(0, 0, 1, 64, shade(BRASS, 0.9))
    else:                                                        # lino squares, scuffed
        for y in range(64):
            for x in range(64):
                im.set(x, y, (120, 84, 56) if (x // 32 + y // 32) % 2 else (190, 170, 130))
        for _ in range(40):
            x, y = rnd.randrange(64), rnd.randrange(64)
            for k in range(rnd.randrange(3, 10)):
                blend(im, (x + k) % 64, (y + k // 3) % 64, (60, 52, 46), 0.35)
        for k in range(0, 64, 32):
            im.rect(k, 0, k + 1, 64, (70, 56, 44))
            im.rect(0, k, 64, k + 1, (70, 56, 44))
    im.noise(4, 381 + n)
    return im


def runner(n):
    """64 wide, lying from 32 to 32 of the flat: its edges are in the middle."""
    c = {1: (150, 30, 38), 2: (176, 40, 36), 3: (40, 40, 42)}[n]
    im = Img(64, 64, c)
    if n == 3:                                                   # ribbed rubber
        for x in range(0, 64, 4):
            im.rect(x, 0, x + 2, 64, shade(c, 1.35))
    else:
        edge = GOLD if n == 1 else (52, 110, 66)
        for x1, x2, e in ((32, 34, c), (34, 38, edge), (26, 30, edge), (30, 32, c)):
            im.rect(x1, 0, x2, 64, shade(e, 0.9))
        if n == 1:
            for y in range(0, 64, 16):
                im.diamond(0, y + 8, 4, shade(GOLD, 0.85))
                im.diamond(63, y + 8, 4, shade(GOLD, 0.85))
    im.noise(6, 385 + n)
    return im


def plain_flat(c, seed, grid=0, line=0.7):
    im = Img(64, 64, c)
    im.noise(6, seed)
    if grid:
        for k in range(0, 64, grid):
            im.rect(k, 0, k + 1, 64, shade(c, line))
            im.rect(0, k, 64, k + 1, shade(c, line))
    return im


def box_floor(n):
    if n == 1:
        im = plain_flat((84, 20, 28), 390)
        for y in range(4, 64, 8):
            for x in range(4 if y % 16 == 4 else 8, 64, 8):
                im.set(x, y, shade(GOLD, 0.9))
        return im
    if n == 2:
        return plain_flat((110, 128, 120), 391, 32, 0.8)         # lino
    im = plain_flat((92, 70, 56), 392, 32, 0.75)                 # carpet tiles
    for x, y in ((14, 20), (40, 50), (52, 12)):
        im.disc(x, y, 1.5, (30, 26, 24))                         # cigarette burns
    return im


# === pictures ================================================================
def leader(im, x1, y1, x2, y2, d):
    """A film leader's frame thrown on the screen x1..x2, y1..y2: the number
    d in two rings on a cross. The sweep has a quarter to go, from nine to
    twelve: the time door's clock."""
    field, swept, line = (214, 210, 196), (164, 160, 148), (52, 50, 48)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    r = (y2 - y1) // 2 - 5
    for y in range(y1, y2):
        for x in range(x1, x2):
            dx, dy = x - cx + 0.5, y - cy + 0.5
            dist = (dx * dx + dy * dy) ** 0.5
            c = field
            if dist < r and math.atan2(dx, -dy) % (2 * math.pi) < 1.5 * math.pi:
                c = swept
            if abs(dist - r) < 1.2 or abs(dist - r + 6) < 0.9 or abs(dx) < 1 or abs(dy) < 1:
                c = line
            blend(im, x, y, c, 0.9)
    sc = max(2, int(r * 1.1) // 5)
    w = len(DIGITS[d][0]) * sc
    for ox, oy, c in ((1, 1, field), (0, 0, line)):              # the number, with a light edge to stand off the cross
        digit(im, d, cx - w // 2 + ox, cy - 5 * sc // 2 + oy, c, sc)


def lintel(n, part):
    """A hall's wall with a dark lintel where a time door's head is."""
    im = wall(n, part)
    y = im.h - 96
    im.rect(0, y - 9, 64, y, SURROUND[n])
    im.rect(0, y - 10, 64, y - 9, shade(SURROUND[n], 1.8))
    return im


def seats(n):
    """A row of seats: from above (a flat, two rows), the seats' front edge
    (64 by 12) and their backs (64 by 24). Two seats to 64, each symmetric."""
    cloth, back, frame = {1: (shade(BURG, 1.15), BURG, GOLD), 2: ((96, 116, 132), ASH, (60, 62, 66)),
                          3: (ORANGE, shade(ORANGE, 1.1), (44, 42, 44))}[n]
    rnd = random.Random(440 + n)
    top = Img(64, 64, shade(frame, 0.8))
    for y0 in (0, 32):
        for x0 in (0, 32):
            f = rnd.choice((1.0, 1.0, 0.9, 0.82)) if n == 3 else 1.0         # some have faded
            top.rect(x0 + 1, y0, x0 + 31, y0 + 12, shade(back, f))          # the back, to the north
            top.rect(x0 + 1, y0, x0 + 31, y0 + 3, shade(back, 1.2 * f))
            top.rect(x0 + 2, y0 + 13, x0 + 30, y0 + 31, shade(cloth, f))
            top.frame(x0 + 2, y0 + 13, x0 + 30, y0 + 31, shade(cloth, 0.7 * f), 1)
            if n == 1:
                top.disc(x0 + 16, y0 + 22, 1.5, shade(BURG, 0.6))            # a button
            elif n == 3:
                top.rect(x0 + 11, y0 + 5, x0 + 21, y0 + 8, shade(back, 0.5)) # the hand hole
    top.noise(4, 441 + n)
    edge = Img(64, 12, (22, 20, 20))
    rear = Img(64, 24, (22, 20, 20))
    for x0 in (0, 32):
        edge.rect(x0 + 2, 0, x0 + 30, 5, shade(cloth, 0.85))
        edge.rect(x0 + 2, 0, x0 + 30, 1, shade(cloth, 1.15))
        edge.rect(x0 + 14, 5, x0 + 18, 12, frame)
        rear.rect(x0 + 1, 0, x0 + 31, 18, shade(back, 0.9))
        rear.rect(x0 + 1, 0, x0 + 31, 2, shade(back, 1.2))
        if n == 3:
            rear.rect(x0 + 11, 4, x0 + 21, 7, shade(back, 0.5))
        elif n == 1:
            rear.frame(x0 + 4, 3, x0 + 28, 15, shade(GOLD, 0.7), 1)
        rear.rect(x0 + 14, 18, x0 + 18, 24, frame)
    edge.noise(3, 442 + n)
    rear.noise(3, 443 + n)
    return top, edge, rear


def screen(n, h, d):
    """The screen over the way in: 256 wide, as high as the wall over it,
    with the leader's frame `d` on it."""
    rnd = random.Random(400 + n)
    if n == 1:
        im = Img(256, h, MARBLE)
        im.rect(30, 14, 226, h - 6, (232, 232, 226))
        leader(im, 30, 14, 226, h - 6, d)
        for x in range(30, 226, 2):                              # the sheen of a silver screen
            for y in range(14, h - 6):
                blend(im, x, y, (255, 255, 255), 0.25)
        folds(im, 4, 34, 4, h - 4, shade(BURG, 1.2), 10)
        folds(im, 222, 252, 4, h - 4, shade(BURG, 1.2), 10, 5)
        folds(im, 4, 252, 4, 14, shade(BURG, 1.0), 12)           # the pelmet
        for x in range(4, 252):
            im.rect(x, 14, x + 1, 15 + int(4 * abs(math.sin(x * math.pi / 24))), GOLD)
        im.frame(0, 0, 256, h, GOLD, 4)
        im.frame(4, 4, 252, h - 4, shade(GOLD, 0.6), 1)
    elif n == 2:
        im = tiled(wall(2, "H"), 256, h)                         # the wall's top, and a plain white screen on it
        im.rect(14, 6, 242, h - 6, (40, 40, 44))
        im.rect(18, 10, 238, h - 10, (240, 240, 234))
        leader(im, 18, 10, 238, h - 10, d)
        im.frame(12, 4, 244, h - 4, (170, 174, 176), 2)
        folds(im, 18, 34, 10, h - 10, (120, 140, 156), 8)
        folds(im, 222, 238, 10, h - 10, (120, 140, 156), 8)
    else:
        im = Img(256, h, (44, 38, 36))
        for _ in range(120):
            x, y = rnd.randrange(256), rnd.randrange(h)
            for k in range(rnd.randrange(2, 9)):
                blend(im, x + k, y, (96, 86, 78), 0.4)
        im.rect(22, 8, 234, h - 8, (214, 204, 170))
        leader(im, 22, 8, 234, h - 8, d)
        blot(im, 180, 20, 30, STAIN, 0.3)                        # damp
        blot(im, 70, h - 30, 18, STAIN, 0.2)
        x, y = 120, 26                                           # a tear, stitched
        for k in range(34):
            im.set(x, y, (70, 60, 50))
            if k % 4 == 0:
                im.rect(x - 2, y, x + 3, y + 1, (60, 52, 46))
            x += rnd.choice((0, 1))
            y += 1
        for x in range(8, 40):                                   # one curtain left, sagging
            f = 0.78 + 0.34 * (0.5 + 0.5 * math.cos(x * 2 * math.pi / 9)) ** 2
            for y in range(6, h - 10 - (x - 8) // 3):
                im.set(x, y, shade((176, 96, 40), f))
        im.rect(0, 0, 256, 6, GLOSS)
    im.noise(3, 401 + n)
    return im


def glass(n):
    """The frame round a box's window: 160 by 112, clear inside."""
    im = Img(160, 112, (0, 0, 0, 0))
    rnd = random.Random(410 + n)
    if n == 1:
        im.frame(0, 0, 160, 112, BRASS, 5)
        im.frame(0, 0, 160, 112, shade(BRASS, 0.6), 1)
        im.frame(4, 4, 156, 108, shade(BRASS, 1.2), 1)
        for x in (52, 106):
            im.rect(x, 5, x + 2, 107, BRASS)
        for x0 in (0, 150):                                      # a plate at each corner
            for y0 in (0, 102):
                im.rect(x0, y0, x0 + 10, y0 + 10, BRASS)
                im.frame(x0, y0, x0 + 10, y0 + 10, shade(BRASS, 0.6), 1)
                im.disc(x0 + 4.5, y0 + 4.5, 1.5, shade(BRASS, 1.25))
    elif n == 2:
        c = (224, 226, 220)
        im.frame(0, 0, 160, 112, c, 4)
        im.frame(0, 0, 160, 112, shade(c, 0.7), 1)
        im.rect(79, 4, 81, 108, c)
    else:
        c = (92, 62, 44)
        im.frame(0, 0, 160, 112, c, 5)
        for _ in range(70):                                      # the paint is going
            x, y = rnd.randrange(160), rnd.randrange(112)
            if im.px[y * 160 + x][3]:
                im.set(x, y, (170, 150, 120))
        x, y = 118, 5                                            # a crack across one corner
        while x < 155 and y < 60:
            im.set(x, y, (224, 232, 232))
            x += 1
            y += rnd.choice((0, 1, 1, 2))
        for k in range(10):                                      # and tape over it
            im.rect(128 + k, 18 + k, 132 + k, 20 + k, (196, 176, 120))
    return im


def poster(k):
    """48 by 72: the town's other places, as films nobody has heard of."""
    rnd = random.Random(420 + k)
    ink, paper = (28, 26, 30), (240, 232, 208)
    if k == 0:                                                   # All Change: the bus
        im = Img(48, 72, (232, 190, 60))
        im.rect(0, 46, 48, 50, (90, 84, 76))
        im.rect(5, 22, 43, 44, (196, 44, 34))
        im.rect(5, 22, 43, 25, paper)
        im.rect(5, 34, 43, 36, paper)
        for x in range(8, 40, 7):
            im.rect(x, 27, x + 5, 33, (40, 50, 64))
        for x in (13, 35):
            im.disc(x, 44, 3.5, ink)
            im.disc(x, 44, 1.2, (150, 150, 150))
        text(im, "ALL", 15, 54, ink, 1)
        text(im, "CHANGE", 6, 62, ink, 1)
        text(im, "10", 18, 8, (196, 44, 34), 2)
    elif k == 1:                                                 # Small Hours: the dome
        im = Img(48, 72)
        for y in range(72):
            im.rect(0, y, 48, y + 1, mix((14, 18, 50), (50, 60, 110), y / 72))
        for _ in range(26):
            im.set(rnd.randrange(48), rnd.randrange(40), (250, 250, 220))
        im.disc(37, 11, 4.5, (244, 236, 190))
        im.disc(39, 10, 3.6, (22, 28, 66))
        for y in range(-13, 1):
            for x in range(-13, 14):
                if x * x + y * y <= 169:
                    im.set(24 + x, 44 + y, (150, 156, 170) if abs(x - 3) > 1 else ink)
        im.rect(9, 44, 39, 52, (96, 100, 116))
        text(im, "SMALL", 9, 56, paper, 1)
        text(im, "HOURS", 9, 64, paper, 1)
    elif k == 2:                                                 # Lost Property: a clock and a case
        im = Img(48, 72, (40, 112, 112))
        im.disc(24, 15, 10, ink)
        im.disc(24, 15, 8.5, paper)
        im.rect(23, 8, 25, 16, ink)
        im.rect(23, 14, 30, 16, ink)
        im.rect(11, 34, 37, 50, (150, 96, 50))
        im.frame(11, 34, 37, 50, (90, 56, 30), 1)
        im.frame(20, 29, 28, 35, (90, 56, 30), 1)
        for x in (16, 31):
            im.rect(x, 34, x + 2, 50, (90, 56, 30))
        im.rect(22, 40, 26, 43, (220, 190, 110))
        text(im, "LOST", 12, 54, paper, 1)
        text(im, "PROPERTY", 1, 62, paper, 1)
    elif k == 3:                                                 # After Hours: the museum
        im = Img(48, 72, (62, 34, 70))
        im.disc(9, 9, 4, (240, 230, 190))
        stone = (222, 210, 180)
        for y in range(8):
            im.rect(24 - y * 2 - 2, 18 + y, 24 + y * 2 + 2, 19 + y, stone)
        im.rect(6, 26, 42, 29, shade(stone, 0.8))
        for x in range(8, 40, 8):
            im.rect(x, 29, x + 4, 46, stone)
            im.rect(x + 3, 29, x + 4, 46, shade(stone, 0.7))
        im.rect(21, 34, 27, 46, (240, 180, 70))                  # a light on inside
        im.rect(4, 46, 44, 49, shade(stone, 0.9))
        im.rect(2, 49, 46, 52, shade(stone, 0.75))
        text(im, "AFTER", 9, 56, paper, 1)
        text(im, "HOURS", 9, 64, paper, 1)
    elif k == 4:                                                 # Putting You Through: the telephone
        im = Img(48, 72, (206, 78, 40))
        for y in range(12):
            im.rect(14 - y // 2, 28 + y, 34 + y // 2, 29 + y, ink)
        im.disc(24, 34, 5, paper)
        im.disc(24, 34, 2, ink)
        im.rect(10, 20, 38, 25, ink)
        for x in (10, 33):
            im.rect(x, 20, x + 5, 29, ink)
        for i in range(14):                                      # the cord
            im.set(38 + (i % 4 in (1, 2)), 26 + i, ink)
        text(im, "PUTTING", 3, 46, paper, 1)
        text(im, "YOU", 15, 54, paper, 1)
        text(im, "THROUGH", 3, 62, paper, 1)
    else:                                                        # Party Wall: two doors in one wall
        im = Img(48, 72, (150, 70, 50))
        for row in range(13):
            im.rect(0, row * 4 + 3, 48, row * 4 + 4, (110, 50, 36))
            for x in range(4 if row % 2 else 0, 48, 8):
                im.rect(x, row * 4, x + 1, row * 4 + 4, (110, 50, 36))
        for x, c in ((6, (60, 110, 220)), (28, (60, 170, 80))):
            im.rect(x, 16, x + 14, 46, c)
            im.frame(x, 16, x + 14, 46, shade(c, 0.5), 1)
            im.disc(x + 11, 32, 1, (235, 215, 140))
        im.rect(0, 46, 48, 52, (70, 66, 62))
        im.rect(0, 52, 48, 72, ink)
        text(im, "PARTY", 9, 56, paper, 1)
        text(im, "WALL", 12, 64, paper, 1)
    im.noise(3, 421 + k)
    return im


def hung(n, k):
    """Poster k on a piece of the foyer's wall in look n."""
    im = wall(n, "F")
    p = poster(k)
    x0, y0 = 8, 36
    rnd = random.Random(430 + n * 7 + k)
    if n == 1:                                                   # a gilt frame, a lamp at each corner
        im.rect(x0 - 5, y0 - 5, x0 + 53, y0 + 77, GOLD)
        im.frame(x0 - 5, y0 - 5, x0 + 53, y0 + 77, shade(GOLD, 0.6), 1)
        im.rect(x0 - 1, y0 - 1, x0 + 49, y0 + 73, MARBLE)
        paste(im, p, x0, y0)
        for cx, cy in ((x0 - 3, y0 - 3), (x0 + 50, y0 - 3), (x0 - 3, y0 + 74), (x0 + 50, y0 + 74)):
            im.disc(cx + 0.5, cy + 0.5, 1.5, (255, 250, 214))
    elif n == 2:                                                 # a glazed case of ash
        im.rect(x0 - 3, y0 - 3, x0 + 51, y0 + 75, shade(ASH, 0.9))
        im.frame(x0 - 3, y0 - 3, x0 + 51, y0 + 75, shade(ASH, 0.55), 1)
        paste(im, p, x0, y0)
        for i in range(30):                                      # a glint on the glass
            blend(im, x0 + 6 + i, y0 + 36 - i, (255, 255, 255), 0.22)
            blend(im, x0 + 7 + i, y0 + 36 - i, (255, 255, 255), 0.22)
    else:                                                        # pasted up years ago
        for y in range(72):
            for x in range(48):
                if (47 - x) + y < 12 + rnd.randrange(3):         # a corner torn off
                    continue
                if y > 60 and rnd.random() < (y - 60) / 16:
                    continue
                c = mix(p.px[y * 48 + x][:3], (196, 176, 140), 0.38)
                im.set(x0 + x, y0 + y, c)
        for cx, cy in ((x0 - 2, y0 - 1), (x0 + 20, y0 + 70)):
            im.rect(cx, cy, cx + 8, cy + 3, (214, 200, 150))
    return im


def sign(n, s, w):
    """The name of a hall over the way to it: w by 32."""
    im = tiled(wall(n, "F" if w > 64 else "L"), w, 32)
    if w > 64 and n == 1:
        im.rect(0, 0, w, 32, CREAM)
    sc = 2 if w > 64 else 1
    tw = len(s) * 6 * sc - sc
    x0, y0, y1 = (w - tw) // 2, 16 - 5 * sc // 2 - 4, 16 + 5 * sc // 2 + 5
    plate, ink, rim = {1: (MARBLE, GOLD, GOLD), 2: ((236, 238, 232), (40, 70, 130), (40, 70, 130)),
                       3: ((226, 150, 50), (50, 36, 30), (60, 50, 44))}[n]
    im.rect(x0 - 8, y0, x0 + tw + 8, y1, plate)
    im.frame(x0 - 8, y0, x0 + tw + 8, y1, rim, 1)
    text(im, s, x0, 16 - 5 * sc // 2, ink, sc)
    if n == 3:                                                   # a lit box: one tube has gone
        for y in range(y0 + 1, y1 - 1):
            for x in range(x0 + tw // 2, x0 + tw + 7):
                blend(im, x, y, (90, 60, 30), 0.4)
    return im


def box_office(n):
    im = tiled(wall(n, "F"), 128, 160)
    rnd = random.Random(440 + n)
    frame = {1: GOLD, 2: shade(ASH, 0.85), 3: (86, 60, 42)}[n]
    plate, ink = {1: (MARBLE, GOLD), 2: ((236, 238, 232), (40, 70, 130)), 3: ((226, 150, 50), (50, 36, 30))}[n]
    im.rect(4, 4, 124, 20, plate)
    im.frame(4, 4, 124, 20, frame, 1)
    text(im, "BOX OFFICE", 5, 7, ink, 2)
    im.rect(20, 26, 108, 116, frame)                             # the window
    im.rect(24, 30, 104, 112, (34, 34, 40))
    for i in range(40):                                          # glass
        blend(im, 30 + i, 80 - i, (200, 210, 220), 0.25)
        blend(im, 60 + i, 100 - i, (200, 210, 220), 0.18)
    if n == 1:                                                   # a brass grille over it
        for x in range(30, 104, 8):
            im.rect(x, 30, x + 1, 92, BRASS)
        for y in range(8):
            im.rect(64 - 3 * (8 - y), 30 + y * 2, 64 + 3 * (8 - y), 32 + y * 2, shade(GOLD, 0.7 + 0.04 * y))
    elif n == 3:                                                 # a sheet of board over half of it
        im.rect(64, 30, 104, 112, (150, 126, 90))
        for x, y in ((67, 33), (100, 33), (67, 108), (100, 108)):
            im.set(x, y, (50, 44, 40))
    im.disc(64, 100, 7, (20, 20, 24))                            # the hole to speak through
    im.rect(24, 108, 104, 112, shade(frame, 0.7))
    cx = 44 if n == 3 else 64                                    # CLOSED, on a card
    im.rect(cx - 20, 60, cx + 20, 73, (240, 232, 208))
    text(im, "CLOSED", cx - 17, 64, (170, 30, 26), 1)
    im.rect(cx - 1, 30, cx, 60, (200, 200, 200))
    im.noise(3, 441 + n)
    return im


def street_doors(n):
    """The doors you came in by, shut: the night behind their glass."""
    im = tiled(wall(n, "F"), 128, 160)
    c = {1: WALNUT, 2: (198, 196, 180), 3: (150, 154, 158)}[n]
    night = (22, 28, 52)
    im.rect(10, 22, 118, 160, shade(c, 0.6))
    for x0 in (14, 65):
        im.rect(x0, 26, x0 + 49, 158, c)
        im.frame(x0, 26, x0 + 49, 158, shade(c, 0.7), 1)
        im.rect(x0 + 7, 34, x0 + 42, 112 if n != 3 else 150, night)
        if n == 1:                                               # glazing bars as a sunburst
            for i in range(-3, 4):
                for k in range(40):
                    im.set(int(x0 + 24.5 + i * k * 0.14), 111 - k, BRASS)
            im.rect(x0 + 7, 112, x0 + 42, 114, BRASS)
            im.frame(x0 + 9, 122, x0 + 40, 150, shade(c, 0.6), 2)
        elif n == 2:
            im.rect(x0 + 7, 72, x0 + 42, 74, c)
            im.frame(x0 + 9, 120, x0 + 40, 150, shade(c, 0.75), 2)
        else:                                                    # wired glass
            for y in range(34, 150, 6):
                im.rect(x0 + 7, y, x0 + 42, y + 1, shade(night, 1.6))
            for x in range(x0 + 7, x0 + 42, 6):
                im.rect(x, 34, x + 1, 150, shade(night, 1.6))
    for x in (59, 67):                                           # the handles
        im.rect(x, 80, x + 2, 104, BRASS if n == 1 else (60, 60, 64))
    if n == 3:
        im.rect(72, 34, 107, 92, (150, 126, 90))                 # one pane is board
    for x, y in ((30, 44), (92, 60), (100, 40)):                 # street lamps, far off
        if n != 3 or x < 70:
            im.disc(x, y, 1.5, (240, 210, 130))
    im.noise(3, 445 + n)
    return im


def steel_door(base, bolt):
    """The steel door (the lowest 96 of AJBOLT) let into the foot of a wall."""
    im = Img(base.w, base.h)
    im.px = [list(p) for p in base.px]
    for y in range(96):
        for x in range(64):
            im.px[(base.h - 96 + y) * 64 + x] = list(bolt.px[(bolt.h - 96 + y) * 64 + x])
    return im


def make(out, looks=LOOKS):
    def put(kind, nm, im):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = im.png()

    bolt = unpng(out["textures/AJBOLT.png"])
    for n in looks:
        walls = {p: wall(n, p) for p in ("H", "G", "F", "W", "B", "L", "C")}
        for p, im in walls.items():
            put("textures", name(p, n), im)
        put("textures", name("BS", n), block_side(n))
        put("textures", name("SP", n), step(n))
        side, top = counter(n)
        put("textures", name("CS", n), side)
        put("flats", name("CT", n), top)
        be = bench(n)
        put("textures", name("BE", n), be)
        put("flats", name("BE", n), be)
        put("textures", name("S1", n), screen(n, 96, "3"))
        put("textures", name("S2", n), screen(n, 96, "2"))
        put("textures", name("S3", n), screen(n, 128, "1"))
        put("textures", name("TH", n), lintel(n, "H"))
        put("textures", name("TG", n), lintel(n, "G"))
        tt = plain_flat(SURROUND[n], 450 + n)
        put("textures", name("TT", n), tt)
        put("flats", name("TT", n), tt)
        top, edge, rear = seats(n)
        put("flats", name("SF", n), top)
        put("textures", name("SS", n), edge)
        put("textures", name("SB", n), rear)
        put("textures", name("DH", n), steel_door(walls["H"], bolt))
        put("textures", name("DG", n), steel_door(walls["G"], bolt))
        put("textures", name("DL", n), steel_door(walls["L"], bolt))
        put("textures", name("GL", n), glass(n))
        gt = plain_flat({1: BRASS, 2: (224, 226, 220), 3: (92, 62, 44)}[n], 415 + n)
        put("textures", name("GT", n), gt)
        put("flats", name("GT", n), gt)
        for k in range(6):
            put("textures", name("P" + "ABCDEF"[k], n), hung(n, k))
        put("textures", name("BO", n), box_office(n))
        put("textures", name("ST", n), street_doors(n))
        put("textures", f"AJYN{n}1", sign(n, "HALL 1", 256))
        put("textures", f"AJYN{n}2", sign(n, "HALL 2", 64))
        put("textures", f"AJYN{n}3", sign(n, "HALL 3", 64))
        put("flats", name("HF", n), hall_floor(n))
        put("flats", name("HC", n), hall_ceiling(n))
        put("flats", name("FF", n), foyer_floor(n))
        put("flats", name("FC", n), small_ceiling(n))
        put("flats", name("FL", n), small_ceiling(n, lamp=True))
        put("flats", name("RG", n), runner(n))
        put("flats", name("BF", n), box_floor(n))
        put("flats", name("BC", n), {1: plain_flat(WALNUT, 395, 32, 0.7), 2: plain_flat((214, 216, 208), 396, 32, 0.85),
                                     3: plain_flat(shade(NICO, 0.9), 397, 32, 0.7)}[n])
        put("flats", name("LF", n), {1: plain_flat((120, 84, 56), 398, 16, 0.75), 2: plain_flat((132, 120, 104), 399, 32, 0.8),
                                     3: plain_flat((112, 110, 104), 400)}[n])
        put("flats", name("LC", n), plain_flat({1: (206, 194, 164), 2: (220, 220, 212), 3: (160, 150, 128)}[n], 401 + n))
        put("flats", name("BT", n), block_top(n))
        put("flats", name("BA", n), block_top(n, arrow=True))


if __name__ == "__main__":
    # swatches for the look board: python3 tools/gfx_cinema.py <dir>
    import os
    import sys
    import gfx
    out = gfx.make_all()
    os.makedirs(sys.argv[1], exist_ok=True)
    for key, data in out.items():
        if "/AJY" in key:
            with open(os.path.join(sys.argv[1], os.path.basename(key)), "wb") as f:
                f.write(data)
