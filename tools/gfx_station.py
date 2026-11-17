"""Candidate looks for MAP05, the terminus (see AJAR_STATION in map_hinges5.py).

Three looks for the whole station, numbered 1 to 3. For look n:
  AJ5Y<n>   the station's front, 576: 512 from platform level to the sky and 64
            more below it; AJ5YA<n>, AJ5YB<n> the same with a window on both
            upper storeys (lit below, lit above), for 64-wide pieces of wall
  AJ5K<n>, AJ5KA<n>, AJ5KB<n>  the same again with the edge of a canopy drawn
            at 128, for the wall over a canopy
  AJ5G<n>   the goods side's wall, 576; AJ5GA<n> with windows
  AJ5B<n>   the bridge's side, 224: the deck's edge and what carries it, down
            past the platforms to the rails; AJ5M<n> the loft's front, 160
  AJ5H<n>   concourse wall, 384; AJ5V<n> the gallery's front, 192
  AJ5A<n>   under canopies, in the vestibule and porches, 128
  AJ5W<n> waiting room   AJ5O<n> offices   AJ5R<n> station master (all 128)
  AJ5S<n>   engine shed, 192
  AJ5N<n>   carriage side, 176 (AJ5NE<n> its end, 192 wide)
  AJ5E<n>   platform edge, 64     AJ5L<n> railing
  AJ5D<n>, AJ5D<n>12, AJ5D<n>34  room doors
  flats: AJ5F<n> concourse floor, AJ5P<n> platforms and the way through,
         AJ5J<n> goods yard, AJ5I<n> room floor, AJ5T<n> the master's carpet,
         AJ5C<n> under a canopy, AJ5CH<n> concourse roof, AJ5CL<n> room ceiling
The same in all three: AJ5XL signal box (128), AJ5XE and AJ5XF the engine's side
and ends (96), AJ5XR the shed's roof, AJ5XB a bench.
Rows of the outdoor walls count down from the sky's edge at 512, whatever the
floor in front of them. Every wall is 64 wide and the same mirrored, and the map
lines them up by world position (Map.align), so cuts in a wall do not show.
"""
import random

from gfx import Img, shade, levers
import gfx_theatre as th
import gfx_yard as gy

STONE, BLUEB, IRON, DARK = (214, 200, 168), (62, 64, 78), (34, 34, 40), (22, 20, 24)
GLASS, LAMP, BRASSY = (34, 42, 58), (240, 200, 118), (204, 168, 84)
GREEN1, GREEN2, CHOC, CREAM = (36, 70, 54), (46, 110, 92), (92, 58, 40), (226, 214, 180)
FAIENCE, BLACK, BRONZE, CONCRETE = (232, 224, 200), (32, 32, 36), (112, 86, 50), (170, 168, 160)

NAMES = {"1": "Terminus", "2": "Metropolitan", "3": "Branch line"}

ROOMS = {
    "1": dict(
        hall=dict(field=(206, 180, 132), fstyle="plain", mark=(176, 150, 106), stile=STONE, bead=(150, 136, 110),
                  dado=(40, 84, 66), dstyle="concrete", rail=(26, 30, 30), skirt=(26, 40, 34),
                  frieze=STONE, fz="stencil", cornice=(226, 214, 186)),
        low=dict(field=(226, 218, 196), fstyle="tile", mark=(196, 188, 166), dado=(40, 84, 66),
                 dstyle="concrete", rail=(26, 30, 30), skirt=(26, 40, 34), cornice=(226, 218, 196)),
        wait=dict(field=(198, 166, 112), fstyle="plaster", mark=(180, 148, 96), dado=(92, 58, 38),
                  dstyle="boards", rail=(60, 38, 24), skirt=(50, 32, 22), cornice=(226, 214, 186)),
        office=dict(field=(150, 162, 132), fstyle="stripe", mark=(132, 146, 116), dado=(110, 76, 46),
                    dstyle="panel", rail=(70, 46, 28), skirt=(50, 34, 22), cornice=(226, 214, 186)),
        master=dict(field=(116, 36, 44), fstyle="damask", mark=(140, 52, 54), dado=(86, 44, 30),
                    dstyle="panel", rail=BRASSY, skirt=(44, 24, 18), cornice=(226, 214, 186)),
        ceil=(214, 204, 180), wood=(96, 62, 38)),
    "2": dict(
        hall=dict(field=FAIENCE, fstyle="block", mark=(204, 196, 172), dado=(44, 44, 48),
                  dstyle="marble", rail=GREEN2, skirt=(26, 26, 30), frieze=GREEN2, fz="stencil",
                  cornice=(236, 230, 210)),
        low=dict(field=FAIENCE, fstyle="tile", mark=(204, 196, 172), dado=GREEN2,
                 dstyle="concrete", rail=BLACK, skirt=(26, 26, 30), cornice=BLACK),
        wait=dict(field=(224, 214, 186), fstyle="block", mark=(200, 190, 162), dado=(150, 98, 58),
                  dstyle="boards", rail=BLACK, skirt=(36, 36, 40), cornice=BLACK),
        office=dict(field=(190, 206, 186), fstyle="plaster", mark=(172, 190, 170), dado=FAIENCE,
                    dstyle="concrete", rail=BLACK, skirt=(36, 36, 40), cornice=BLACK),
        master=dict(field=(126, 86, 52), fstyle="panel", mark=(88, 58, 34), dado=(100, 66, 40),
                    dstyle="panel", rail=BRASSY, skirt=(36, 30, 26), cornice=BLACK),
        ceil=(236, 232, 220), wood=(150, 98, 58)),
    "3": dict(
        hall=dict(field=CREAM, fstyle="slats", mark=(190, 178, 144), stile=CHOC, bead=(56, 34, 22),
                  dado=CHOC, dstyle="boards", rail=(56, 34, 22), skirt=(48, 30, 20), cornice=CHOC),
        low=dict(field=CREAM, fstyle="slats", mark=(190, 178, 144), dado=CHOC,
                 dstyle="boards", rail=(56, 34, 22), skirt=(48, 30, 20), cornice=CHOC),
        wait=dict(field=(172, 188, 152), fstyle="plaster", mark=(154, 172, 134), dado=(214, 202, 170),
                  dstyle="boards", rail=CHOC, skirt=(70, 46, 30), cornice=CHOC),
        office=dict(field=(214, 200, 160), fstyle="slats", mark=(178, 164, 126), dado=(120, 84, 52),
                    dstyle="boards", rail=(70, 46, 30), skirt=(56, 38, 26), cornice=(120, 84, 52)),
        master=dict(field=(190, 172, 134), fstyle="damask", mark=(150, 120, 88), dado=(104, 70, 42),
                    dstyle="panel", rail=(70, 46, 30), skirt=(50, 34, 22), cornice=(226, 218, 196)),
        ceil=(224, 214, 186), wood=CHOC),
}


def arch(im, cx, top, r, bottom, c):
    """A round-headed shape: crown at row `top`, half-width r, down to `bottom`."""
    for y in range(top, bottom):
        d = top + r - y
        half = int((r * r - d * d) ** 0.5) if d > 0 else r
        im.rect(cx - half, y, cx + half, y + 1, c)


def copy(im):
    out = Img(im.w, im.h)
    out.px = [list(p) for p in im.px]
    return out


# --- the outdoor walls -------------------------------------------------------
def base(n, kind, seed):
    """A front without windows, 64 by 576. kind "Y" the station, "G" the goods side."""
    goods = kind == "G"
    if n == "1":                                                     # brick: red with stone, or soot with blue brick
        c = (108, 76, 62) if goods else (160, 74, 54)
        im = gy.mirror(th.brick(64, 576, c, shade(c, 0.62), seed))
        im.noise(5, seed)
        gy.grime(im, 300, 512, 0.86)
        for r in (190, 350):
            im.rect(0, r, 64, r + 6, BLUEB if goods else STONE)
            im.rect(0, r, 64, r + 1, shade(BLUEB if goods else STONE, 1.12))
            im.rect(0, r + 6, 64, r + 8, shade(c, 0.5))
        gy.paste(im, gy.mirror(th.brick(64, 96, BLUEB, shade(BLUEB, 0.6), seed + 1)), 480)
        if not goods:
            im.rect(0, 476, 64, 480, STONE)
        gy.grime(im, 512, 576, 0.55)
        if goods:
            im.rect(0, 0, 64, 8, STONE)
            im.rect(0, 8, 64, 10, shade(c, 0.45))
            for x in range(0, 64, 8):
                im.rect(x, 10, x + 4, 16, shade(c, 0.8))
        else:
            gy.top_edge(im, "brick", 32)
    elif n == "2":                                                   # faience, or board-marked concrete
        if goods:
            im = Img(64, 576, CONCRETE)
            im.noise(6, seed)
            for y in range(12, 576, 12):
                im.rect(0, y, 64, y + 1, shade(CONCRETE, 0.9))
            for r in (192, 352):
                im.rect(0, r - 1, 64, r + 1, shade(CONCRETE, 0.78))
            im.rect(0, 448, 64, 512, GREEN2)
            im.rect(0, 446, 64, 448, shade(GREEN2, 0.6))
            gy.grime(im, 496, 512, 0.7)
            im.rect(0, 512, 64, 576, shade(CONCRETE, 0.5))
            im.rect(0, 0, 64, 6, shade(CONCRETE, 1.15))
            im.rect(0, 6, 64, 8, shade(CONCRETE, 0.55))
        else:
            im = Img(64, 576, FAIENCE)
            im.noise(3, seed)
            for y in range(0, 512, 16):
                im.rect(0, y, 64, y + 1, shade(FAIENCE, 0.86))
            for x in (0, 32):
                im.rect(x, 0, x + 1, 512, shade(FAIENCE, 0.86))
            for r in (184, 344):
                im.rect(0, r, 64, r + 4, BLACK)
                im.rect(0, r + 4, 64, r + 12, GREEN2)
                im.rect(0, r + 4, 64, r + 5, shade(GREEN2, 1.3))
            im.rect(0, 464, 64, 512, (44, 44, 48))                   # polished black plinth
            im.rect(0, 464, 64, 465, (110, 110, 116))
            im.rect(0, 512, 64, 576, shade(CONCRETE, 0.5))
            im.rect(0, 0, 64, 10, (240, 234, 214))
            im.rect(0, 10, 64, 14, BLACK)
            im.rect(0, 14, 64, 26, GREEN2)
            im.rect(0, 14, 64, 15, shade(GREEN2, 1.3))
            im.rect(0, 26, 64, 28, BLACK)
    else:                                                            # weatherboard, or tarred boards
        if goods:
            c = (58, 52, 48)
            im = Img(64, 576, c)
            im.noise(7, seed)
            for x in range(0, 64, 8):
                im.rect(x, 0, x + 1, 512, shade(c, 0.6))
                im.rect(x + 1, 0, x + 2, 512, shade(c, 1.25))
            im.rect(0, 348, 64, 354, CREAM)
            im.rect(0, 354, 64, 356, shade(c, 0.5))
            im.rect(0, 0, 64, 6, (96, 100, 108))                     # the edge of a tin roof
            im.rect(0, 6, 64, 8, shade(c, 0.5))
        else:
            im = Img(64, 576, CREAM)
            im.noise(4, seed)
            for y in range(0, 512, 8):
                im.rect(0, y, 64, y + 1, shade(CREAM, 0.76))
                im.rect(0, y + 1, 64, y + 2, shade(CREAM, 1.06))
            for x1, x2 in ((0, 3), (61, 64)):
                im.rect(x1, 0, x2, 512, (240, 234, 214))
            im.rect(0, 440, 64, 512, CHOC)
            for x in range(0, 64, 8):
                im.rect(x, 440, x + 1, 512, shade(CHOC, 0.7))
            im.rect(0, 436, 64, 440, shade(CHOC, 0.8))
            for r in (190, 350):
                im.rect(0, r, 64, r + 5, CHOC)
                im.rect(0, r + 5, 64, r + 7, shade(CREAM, 0.6))
            im.rect(0, 0, 64, 8, (70, 72, 82))                       # slates
            im.rect(0, 8, 64, 14, CHOC)
            for x in range(64):                                      # a cut edge along the eaves
                d = 14 + 12 - abs((x % 8) - 4) * 3
                im.rect(x, 14, x + 1, d, CHOC)
                im.rect(x, d, x + 1, d + 2, shade(CREAM, 0.6))
        gy.rubble(im, 512, 576, (104, 96, 88), seed)
        gy.grime(im, 480, 512, 0.8)
    return im


def window(im, n, goods, t, lit):
    """A window whose head is at row t, in the middle of a 64-wide front."""
    glass = LAMP if lit else GLASS
    if n == "1" and not goods:                                       # round-headed, in stone
        arch(im, 32, t, 23, t + 84, STONE)
        arch(im, 32, t + 5, 18, t + 80, (232, 226, 206))
        arch(im, 32, t + 8, 15, t + 77, glass)
        im.rect(17, t + 24, 47, t + 27, (232, 226, 206))
        im.rect(17, t + 50, 47, t + 53, (232, 226, 206))
        im.rect(31, t + 8, 34, t + 77, (232, 226, 206))
        if lit:
            for i in range(26):
                im.rect(17, t + 27 + i, 17 + (26 - i) // 4, t + 28 + i, (150, 60, 52))
                im.rect(47 - (26 - i) // 4, t + 27 + i, 47, t + 28 + i, (150, 60, 52))
        im.rect(5, t + 84, 59, t + 90, STONE)
        im.rect(5, t + 90, 59, t + 92, (90, 44, 34))
    elif n == "1":                                                   # a barred warehouse light
        im.rect(16, t + 16, 48, t + 22, BLUEB)
        im.rect(20, t + 22, 44, t + 64, (26, 28, 34))
        for x in (25, 31, 38):
            im.rect(x, t + 22, x + 1, t + 64, (84, 84, 92))
        im.rect(16, t + 64, 48, t + 68, BLUEB)
    elif n == "2" and not goods:                                     # a long steel window
        im.rect(3, t, 61, t + 60, BRONZE)
        im.rect(6, t + 3, 58, t + 57, glass)
        for x in (18, 31, 45):
            im.rect(x, t + 3, x + 2, t + 57, BRONZE)
        for y in (t + 20, t + 39):
            im.rect(6, y, 58, y + 2, BRONZE)
        im.rect(3, t - 4, 61, t, BLACK)
        im.rect(1, t + 60, 63, t + 64, GREEN2)
    elif n == "2":                                                   # glass bricks
        im.rect(14, t + 14, 50, t + 66, shade(CONCRETE, 0.6))
        for y in range(t + 16, t + 64, 8):
            for x in range(16, 48, 8):
                im.rect(x, y, x + 7, y + 7, (150, 176, 172))
                im.rect(x + 1, y + 1, x + 4, y + 3, (196, 214, 208))
    elif not goods:                                                  # a tall sash, small panes
        im.rect(13, t, 51, t + 84, CHOC)
        im.rect(16, t + 3, 48, t + 81, glass)
        for x in (24, 31, 32, 39):
            im.rect(x, t + 3, x + 1, t + 81, (240, 234, 214))
        for y in range(t + 15, t + 80, 13):
            im.rect(16, y, 48, y + 1, (240, 234, 214))
        im.rect(16, t + 41, 48, t + 44, CHOC)
        im.rect(10, t + 84, 54, t + 88, (240, 234, 214))
        im.rect(10, t + 88, 54, t + 90, shade(CREAM, 0.6))
    else:                                                            # four panes in a shed wall
        im.rect(18, t + 20, 46, t + 52, CREAM)
        im.rect(21, t + 23, 43, t + 49, (30, 34, 40))
        im.rect(31, t + 23, 33, t + 49, CREAM)
        im.rect(21, t + 35, 43, t + 37, CREAM)


def fascia(im, n):
    """The edge of a canopy across a front, rows 352..384 (128 to 160 up)."""
    if n == "1":                                                     # cast iron, cut to points
        im.rect(0, 352, 64, 384, (20, 22, 22))
        im.rect(0, 352, 64, 362, GREEN1)
        im.rect(0, 352, 64, 353, shade(GREEN1, 1.6))
        for x in range(64):
            k = abs((x % 8) - 4)
            im.rect(x, 362, x + 1, 382 - k * 3, GREEN1)
            if k == 0:
                im.set(x, 374, STONE)
    elif n == "2":                                                   # a flat slab
        im.rect(0, 352, 64, 372, (240, 236, 226))
        im.rect(0, 352, 64, 353, (255, 252, 244))
        im.rect(0, 372, 64, 378, GREEN2)
        im.rect(0, 378, 64, 384, (20, 22, 22))
    else:                                                            # boards with rounded ends
        im.rect(0, 352, 64, 384, (24, 20, 18))
        im.rect(0, 352, 64, 360, CHOC)
        im.rect(0, 352, 64, 353, shade(CHOC, 1.5))
        for x in range(64):
            k = abs((x % 8) - 4)
            if k < 4:
                im.rect(x, 360, x + 1, 382 - (1 if k < 2 else 3 if k < 3 else 6), CREAM)
                if k == 3:
                    im.rect(x, 360, x + 1, 376, shade(CREAM, 0.8))


def front(n, kind="Y", win=0, canopy=False):
    im = base(n, kind, 800 + 10 * int(n) + (5 if kind == "G" else 0))
    if win:
        for t, lit in ((64, win == 2), (224, win == 1)):
            window(im, n, kind == "G", t, lit and kind != "G")
    if canopy:
        fascia(im, n)
    return im


def bridge(n):
    """The bridge from below: the station's front down to the deck at row 352,
    then what carries it, down past platform level (512) to the rails (576)."""
    im = front(n)
    if n == "1":                                                     # a brick viaduct
        im.rect(0, 352, 64, 362, STONE)
        im.rect(0, 362, 64, 364, (90, 44, 34))
        arch(im, 32, 384, 26, 576, STONE)
        arch(im, 32, 388, 22, 576, DARK)
        for y in range(440, 576):                                    # a little of the far side
            f = min(1.0, (y - 440) / 136)
            im.rect(12, y, 52, y + 1, shade((60, 50, 48), 0.4 + 0.5 * f))
    elif n == "2":                                                   # a concrete beam on tiled piers
        im.rect(0, 352, 64, 376, (240, 236, 226))
        im.rect(0, 352, 64, 353, (255, 252, 244))
        im.rect(0, 376, 64, 382, GREEN2)
        im.rect(5, 382, 59, 576, DARK)
        for y in range(450, 576):
            im.rect(8, y, 56, y + 1, shade((58, 60, 62), 0.4 + 0.5 * min(1.0, (y - 450) / 126)))
        im.rect(5, 382, 59, 386, (12, 12, 14))
    else:                                                            # a timber trestle
        im.rect(0, 364, 64, 576, (26, 22, 20))
        im.rect(0, 352, 64, 366, CHOC)
        im.rect(0, 352, 64, 353, shade(CHOC, 1.6))
        for i in range(140):
            x = 5 + i * 50 // 140
            im.rect(x, 366 + i, x + 4, 367 + i, shade(CHOC, 1.15))
            im.rect(59 - (x - 5) - 4, 366 + i, 59 - (x - 5), 367 + i, shade(CHOC, 1.15))
        for x1, x2 in ((0, 5), (59, 64)):
            im.rect(x1, 366, x2, 576, CHOC)
        im.rect(0, 504, 64, 512, CHOC)
        im.rect(0, 504, 64, 505, shade(CHOC, 1.5))
    return im


def decked(im, row, edge):
    """The edge of a floor drawn across a wall at `row`, joist ends under it."""
    im.rect(0, row, 64, row + 10, edge)
    im.rect(0, row, 64, row + 1, shade(edge, 1.5))
    for x in range(4, 64, 16):
        im.rect(x, row + 10, x + 6, row + 18, shade(edge, 0.8))
        im.rect(x, row + 18, x + 6, row + 20, shade(edge, 0.4))
    return im


# --- indoors -----------------------------------------------------------------
def hall(n):
    s = ROOMS[n]["hall"]
    im = th._wall64(s, 384)
    f0, f1 = th._wall(s, 384).field
    if n == "1":                                                     # yellow brick between stone piers
        b = gy.mirror(th.brick(64, f1 - f0 - 4, s["field"], s["mark"], 830))
        for y in range(b.h):
            for x in range(5, 60):
                im.set(x, f0 + y, b.px[y * 64 + x][:3])
        for r in range(f0 + 60, f1 - 30, 64):                        # a band of red every eighth course
            im.rect(5, r, 60, r + 8, (160, 74, 54))
            im.rect(5, r, 60, r + 1, (110, 50, 38))
    im.noise(4, 831 + int(n))
    return im


def shed(n):
    if n == "1":
        im = gy.mirror(th.brick(64, 192, (98, 72, 62), (52, 42, 40), 840))
        im.noise(6, 841)
        gy.grime(im, 110, 192, 0.7)
        for y in range(0, 50):                                       # soot under the roof
            f = 0.45 + 0.55 * y / 50
            for x in range(64):
                p = im.px[y * 64 + x]
                p[:3] = shade(p[:3], f)
    elif n == "2":
        im = Img(64, 192, (150, 150, 146))
        im.noise(6, 842)
        for y in range(12, 192, 12):
            im.rect(0, y, 64, y + 1, (132, 132, 128))
        im.rect(3, 20, 61, 68, (60, 62, 66))                         # a band of steel windows
        im.rect(5, 22, 59, 66, (96, 112, 116))
        for x in (17, 31, 45):
            im.rect(x, 22, x + 2, 66, (60, 62, 66))
        im.rect(5, 43, 59, 45, (60, 62, 66))
        im.rect(0, 144, 64, 192, GREEN2)
        gy.grime(im, 150, 192, 0.6)
    else:
        c = (52, 46, 42)
        im = Img(64, 192, c)
        im.noise(7, 843)
        for x in range(0, 64, 8):
            im.rect(x, 0, x + 1, 192, (20, 18, 16))
            im.rect(x + 1, 0, x + 2, 192, shade(c, 1.3))
        for x, y, k in ((16, 30, 24), (48, 30, 24), (0, 96, 40), (32, 80, 30)):   # daylight between boards
            im.rect(x, y, x + 1, y + k, (214, 206, 180))
        im.rect(0, 60, 64, 66, shade(c, 1.4))
        im.rect(0, 150, 64, 156, shade(c, 1.4))
    im.rect(0, 0, 64, 4, (24, 22, 22))
    return im


def train(n):
    body, band, roof = {"1": ((38, 78, 58), (226, 214, 180), (60, 62, 66)),
                        "2": ((176, 182, 190), (40, 42, 48), (150, 156, 164)),
                        "3": ((92, 58, 40), (226, 214, 180), (70, 66, 62))}[n]
    tr = Img(64, 176, body)
    tr.noise(5, 850 + int(n))
    tr.rect(0, 0, 64, 6, roof)
    tr.rect(0, 22, 64, 78, band)
    for x in (6, 36):
        tr.rect(x, 28, x + 22, 70, (30, 40, 56))
        tr.frame(x, 28, x + 22, 70, (120, 96, 50) if n != "2" else (120, 124, 132), 2)
    tr.rect(0, 120, 64, 124, (206, 180, 96) if n != "2" else (200, 120, 50))
    if n == "2":                                                     # ribbed metal
        for y in range(84, 118, 6):
            tr.rect(0, y, 64, y + 1, (140, 146, 154))
    tr.rect(0, 140, 64, 176, (26, 26, 28))
    for cx in (16, 48):
        tr.disc(cx, 160, 13, (58, 58, 62))
        tr.disc(cx, 160, 4, (120, 120, 126))
    return tr


def train_end(n):
    """The end of the carriage, 192 wide: the side's paint, a door to the next
    carriage with a window in it, a lamp each side, the buffers and the hook."""
    side = train(n)
    tr = Img(192, 176)
    for y in range(176):
        tr.px[y * 192:(y + 1) * 192] = [list(side.px[y * 64]) for _ in range(192)]      # the side's rows, no windows
    body = tuple(side.px[100 * 64][:3])
    metal = (120, 96, 50) if n != "2" else (120, 124, 132)
    tr.rect(0, 6, 3, 140, shade(body, 0.6))                              # the corners
    tr.rect(189, 6, 192, 140, shade(body, 0.6))
    tr.rect(72, 16, 120, 140, shade(body, 0.8))                          # the door
    tr.frame(72, 16, 120, 140, metal, 2)
    tr.rect(82, 28, 110, 70, (30, 40, 56))
    tr.frame(82, 28, 110, 70, metal, 2)
    tr.rect(112, 84, 116, 92, metal)                                     # its handle
    for x in (20, 136):                                                  # a window each side of it
        tr.rect(x, 28, x + 36, 70, (30, 40, 56))
        tr.frame(x, 28, x + 36, 70, metal, 2)
    for cx in (22, 170):                                                 # tail lamps
        tr.disc(cx, 108, 6, (40, 38, 40))
        tr.disc(cx, 108, 4, (176, 44, 36))
    tr.rect(0, 140, 192, 176, (26, 26, 28))                              # the frame under it
    tr.rect(0, 140, 192, 146, (58, 58, 62))
    for cx in (34, 158):                                                 # buffers
        tr.rect(cx - 5, 150, cx + 5, 160, (70, 70, 74))
        tr.disc(cx, 155, 11, (96, 96, 102))
        tr.disc(cx, 155, 8, (58, 58, 62))
    tr.rect(90, 150, 102, 166, (70, 70, 74))                             # the hook
    tr.rect(93, 160, 99, 172, (40, 40, 44))
    tr.noise(4, 860 + int(n))
    return tr


def flat(n, tag, seed):
    rnd = random.Random(seed)
    if tag == "F":                                                   # the concourse
        if n == "1":                                                 # encaustic tiles
            f = Img(64, 64, (206, 180, 132))
            for i in range(4):
                for j in range(4):
                    if (i + j) % 2:
                        f.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, (164, 84, 60))
            for cx in range(0, 65, 16):
                for cy in range(0, 65, 16):
                    f.diamond(cx, cy, 3, (40, 38, 42))
            f.noise(5, seed)
            return f
        if n == "2":
            return th.flat("terrazzo", (190, 180, 168), (120, 104, 96), seed)
        return th.flat("boards", (150, 112, 70), (96, 68, 42), seed)
    if tag == "P":                                                   # platforms
        if n == "1":
            return gy.flat("flags", seed)
        if n == "2":
            f = Img(64, 64, (184, 182, 176))
            f.noise(6, seed)
            for i in (0, 32):
                f.rect(i, 0, i + 1, 64, (140, 138, 132))
                f.rect(0, i, 64, i + 1, (140, 138, 132))
            return f
        f = th.brick(64, 64, (150, 84, 62), (104, 58, 44), seed)
        f.noise(7, seed)
        return f
    if tag == "J":                                                   # the goods yard
        if n == "1":
            return gy.flat("setts", seed)
        if n == "3":
            return gy.flat("earth", seed)
        f = Img(64, 64, (74, 74, 78))
        f.noise(10, seed)
        for _ in range(5):
            x, y = rnd.randrange(64), rnd.randrange(64)
            for i in range(rnd.randrange(8, 20)):
                f.set((x + i) % 64, (y + i // 3) % 64, (50, 50, 54))
        return f
    if tag == "I":                                                   # rooms
        if n == "2":                                                 # green and cream lino
            f = Img(64, 64, (222, 214, 190))
            for i in range(4):
                for j in range(4):
                    if (i + j) % 2:
                        f.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, (70, 116, 98))
            f.noise(4, seed)
            return f
        a = (104, 72, 44) if n == "1" else (170, 132, 86)
        return th.flat("boards", a, shade(a, 0.62), seed)
    a, b = {"1": ((96, 28, 40), BRASSY), "2": ((36, 84, 92), (220, 210, 180)),
            "3": ((112, 72, 48), (170, 132, 86))}[n]                # the master's carpet
    return th.flat("carpet", a, b, seed)


def ceiling(n, tag, seed):
    if tag == "CH":                                                  # the concourse roof
        if n == "1":                                                 # iron and glass
            c = Img(64, 64, (170, 190, 200))
            c.noise(6, seed)
            for x in range(0, 64, 16):
                c.rect(x, 0, x + 1, 64, (60, 70, 70))
            c.rect(0, 0, 64, 5, GREEN1)
            c.rect(0, 5, 64, 6, (16, 30, 24))
            c.rect(0, 0, 5, 64, GREEN1)
            c.rect(5, 6, 6, 64, (16, 30, 24))
            for x in range(8, 64, 16):
                c.disc(x, 2, 1, (120, 140, 120))
            return c
        if n == "2":                                                 # coffers with a round light
            c = Img(64, 64, (236, 232, 220))
            c.frame(0, 0, 64, 64, (200, 196, 184), 3)
            c.frame(3, 3, 61, 61, (250, 248, 240), 1)
            c.disc(32, 32, 14, (200, 196, 184))
            c.disc(32, 32, 12, (214, 232, 232))
            c.disc(32, 32, 5, (255, 252, 236))
            c.noise(3, seed)
            return c
        return gy.ceiling(CREAM, CHOC, 32, seed)
    if tag == "C":                                                   # under a canopy
        if n == "1":
            c = Img(64, 64, (176, 194, 200))
            c.noise(5, seed)
            for y in range(0, 64, 8):
                c.rect(0, y, 64, y + 1, (60, 70, 70))
            c.rect(0, 0, 4, 64, GREEN1)
            c.rect(4, 0, 5, 64, (16, 30, 24))
            return c
        if n == "2":
            c = Img(64, 64, (238, 236, 228))
            c.noise(3, seed)
            c.disc(32, 32, 7, (200, 198, 190))
            c.disc(32, 32, 6, (255, 250, 226))
            return c
        return gy.ceiling((214, 202, 170), CHOC, 16, seed)
    c = Img(64, 64, ROOMS[n]["ceil"])
    c.frame(0, 0, 64, 64, shade(ROOMS[n]["ceil"], 0.9), 1)
    c.noise(3, seed)
    return c


def railing(n):
    if n == "1":
        return gy.railing("brick")
    if n == "3":
        r = Img(64, 32, (0, 0, 0, 0))                                # white palings
        w = (236, 230, 210)
        r.rect(0, 6, 64, 9, w)
        r.rect(0, 24, 64, 27, w)
        for x in range(2, 64, 8):
            r.rect(x, 2, x + 4, 32, w)
            r.rect(x + 1, 0, x + 3, 2, w)
            r.rect(x + 3, 2, x + 4, 32, shade(w, 0.8))
        return r
    r = Img(64, 32, (0, 0, 0, 0))                                    # steel tube
    for y in (0, 11, 22):
        r.rect(0, y, 64, y + 3, (150, 156, 164))
        r.rect(0, y, 64, y + 1, (210, 214, 220))
    for x in (0, 32):
        r.rect(x, 0, x + 3, 32, (150, 156, 164))
    return r


def make(out, rd):
    """`rd` is the plain room door (leaf in its bottom 96 rows)."""
    def both(name, im):
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    for n, c in ROOMS.items():
        k = int(n)
        out[f"textures/AJ5Y{n}.png"] = front(n).png()
        out[f"textures/AJ5YA{n}.png"] = front(n, win=1).png()
        out[f"textures/AJ5YB{n}.png"] = front(n, win=2).png()
        out[f"textures/AJ5K{n}.png"] = front(n, canopy=True).png()
        out[f"textures/AJ5KA{n}.png"] = front(n, win=1, canopy=True).png()
        out[f"textures/AJ5KB{n}.png"] = front(n, win=2, canopy=True).png()
        out[f"textures/AJ5G{n}.png"] = front(n, "G").png()
        out[f"textures/AJ5GA{n}.png"] = front(n, "G", win=1).png()
        out[f"textures/AJ5B{n}.png"] = gy.crop(bridge(n), 352, 576).png()
        edge = {"1": (60, 62, 70), "2": (240, 236, 226), "3": CHOC}[n]
        out[f"textures/AJ5M{n}.png"] = decked(gy.crop(front(n, "G"), 352, 512), 0, edge).png()
        h = hall(n)
        out[f"textures/AJ5H{n}.png"] = h.png()
        out[f"textures/AJ5V{n}.png"] = decked(gy.crop(h, 192, 384), 0, {"1": GREEN1, "2": (240, 236, 226), "3": CHOC}[n]).png()
        walls = {}
        for tag, part in (("A", "low"), ("W", "wait"), ("O", "office"), ("R", "master")):
            walls[tag] = th.wall(c[part], 128, seed=860 + 10 * k + ord(tag))
            out[f"textures/AJ5{tag}{n}.png"] = walls[tag].png()
        out[f"textures/AJ5S{n}.png"] = shed(n).png()
        out[f"textures/AJ5N{n}.png"] = train(n).png()
        out[f"textures/AJ5NE{n}.png"] = train_end(n).png()
        e = Img(64, 64, {"1": BLUEB, "2": (120, 120, 118), "3": (120, 70, 54)}[n])   # the platform's edge
        e.noise(6, 870 + k)
        for y in range(8, 64, 8):
            e.rect(0, y, 64, y + 1, shade(e.px[0][:3], 0.7))
        e.rect(0, 0, 64, 7, (232, 228, 214))
        e.rect(0, 7, 64, 9, (60, 58, 56))
        out[f"textures/AJ5E{n}.png"] = e.png()
        out[f"textures/AJ5L{n}.png"] = railing(n).png()
        d = th.door(walls["A"], rd, c["wood"])
        out[f"textures/AJ5D{n}.png"] = d.png()
        for keys in ("12", "34"):
            out[f"textures/AJ5D{n}{keys}.png"] = th.locked(d, keys).png()
        for tag in "FPJIT":
            out[f"flats/AJ5{tag}{n}.png"] = flat(n, tag, 880 + 10 * k + "FPJIT".index(tag)).png()
        for tag in ("C", "CH", "CL"):
            out[f"flats/AJ5{tag}{n}.png"] = ceiling(n, tag, 890 + 10 * k + len(tag)).png()

    # --- the same in every look ------------------------------------------------
    box = Img(64, 128, (206, 196, 168))                              # the signal box: boards under a row of windows
    box.noise(4, 900)
    for x in range(0, 64, 8):
        box.rect(x, 78, x + 1, 128, (160, 150, 124))
    box.rect(0, 14, 64, 78, (240, 236, 222))
    for x in (2, 34):
        box.rect(x, 18, x + 28, 74, (44, 58, 78))
        box.rect(x + 13, 18, x + 15, 74, (240, 236, 222))
        box.rect(x, 44, x + 28, 46, (240, 236, 222))
        for i in range(12):
            box.set(x + 3 + i, 40 - i, (86, 104, 126))
    box.rect(0, 78, 64, 82, (120, 104, 78))
    box.rect(0, 0, 64, 14, (60, 84, 70))
    box.rect(0, 12, 64, 14, (30, 44, 36))
    box.rect(0, 120, 64, 128, (60, 52, 40))
    out["textures/AJ5XL.png"] = gy.mirror(box).png()
    levers(out, "AJ5LV", gy.mirror(box))                             # the signal box's lever
    eng = Img(64, 96, (30, 30, 34))                                  # the engine: boiler, footplate, a wheel
    eng.noise(4, 901)
    eng.rect(0, 0, 64, 3, (70, 70, 76))
    for y in (14, 30):
        eng.rect(0, y, 64, y + 2, (190, 160, 80))                    # boiler bands
    eng.rect(0, 46, 64, 52, (150, 34, 30))                           # footplate
    eng.rect(0, 52, 64, 54, (12, 12, 14))
    eng.rect(0, 54, 64, 96, (16, 16, 18))
    eng.disc(32, 74, 20, (150, 34, 30))
    eng.disc(32, 74, 16, (16, 16, 18))
    for dx, dy in ((0, 1), (1, 0), (1, 1), (1, -1)):
        for i in range(-15, 16):
            eng.set(int(32 + dx * i * (0.7 if dx and dy else 1)), int(74 + dy * i * (0.7 if dx and dy else 1)), (150, 34, 30))
    eng.disc(32, 74, 4, (190, 160, 80))
    eng.rect(0, 70, 64, 73, (176, 180, 188))                         # the coupling rod
    out["textures/AJ5XE.png"] = eng.png()
    end = Img(64, 96, (30, 30, 34))
    end.noise(4, 902)
    end.rect(0, 0, 64, 3, (70, 70, 76))
    end.rect(0, 46, 64, 60, (150, 34, 30))                           # buffer beam
    end.rect(0, 60, 64, 96, (16, 16, 18))
    for cx in (12, 52):
        end.disc(cx, 53, 5, (120, 120, 126))
    for x in range(4, 64, 8):
        end.disc(x, 6, 1, (90, 90, 96))
    out["textures/AJ5XF.png"] = gy.mirror(end).png()
    roofc = Img(64, 64, (36, 32, 30))
    roofc.noise(4, 903)
    roofc.rect(0, 0, 64, 6, (70, 54, 40))
    roofc.rect(0, 6, 64, 7, (16, 14, 12))
    roofc.rect(0, 30, 64, 32, (56, 44, 34))
    out["flats/AJ5XR.png"] = roofc.png()
    bench = Img(64, 64, (126, 88, 52))
    bench.noise(5, 904)
    for y in range(0, 64, 8):
        bench.rect(0, y, 64, y + 1, (60, 40, 24))
        bench.rect(0, y + 1, 64, y + 2, (160, 116, 72))
    both("AJ5XB", bench)
