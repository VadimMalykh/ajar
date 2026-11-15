"""Candidate looks for MAP04, the yard (see AJAR_YARD in map_hinges4.py).

Three looks for the whole block, numbered 1 to 3. The yard has a house on each
side (W, N, E, S), and each house has its own colour within a look. For look n:
  AJ4Y<n><h>  house h's front, 512 from the yard floor to the sky, no windows;
              AJ4Z<n><h>, AJ4U<n><h> the same with a window on both upper
              storeys (lit below, lit above), for 64-wide pieces of wall
  AJ4B<n>, AJ4T<n>  house W and E again, with the edge of the balcony (at 160)
              and of the loft (at 192) drawn on, for the wall below them
  AJ4R<n>  front of the roof, 320; AJ4Q<n> with a window
  AJ4G<n>  the walls that stand round the roof, 192
  AJ4L<n>  lining of the light well, 448 below the roof; AJ4V<n> its outer
           wall, 640 (AJ4G over AJ4L)
  AJ4F<n> yard floor   AJ4P<n> path   AJ4M<n> roof   AJ4N<n> railing
  AJ4A<n> gate passage and porches, 128        AJ4E<n> ceiling of low rooms
  AJ4H<n> wash house, 128   AJ4I<n> its floor
  AJ4O<n> office, 128       AJ4K<n> carpet     AJ4W<n> suite, 112
  AJ4J<n> loft, 144         AJ4C<n> its ceiling
  AJ4D<n>W, AJ4D<n>O, AJ4D<n>O34, AJ4D<n>S, AJ4D<n>S12  room doors
Below ground is the same in all three: AJ4XC cellar (128), AJ4XR its stairs,
AJ4XK kennel (128), AJ4XF and AJ4XS their floors, AJ4XD ceiling, AJ4XB bars,
AJ4XP the pantry's shelves (112).
Storeys are 160 high (the balcony stands on the first, the roof on the second).
Every wall is 64 wide and the same mirrored, and the map lines them up by
world position (Map.align), so cuts in a wall do not show.
"""
import random

from gfx import Img, shade
import gfx_theatre as th

STONE, OAK, IRON, TERRA = (192, 182, 162), (64, 46, 32), (34, 34, 40), (186, 98, 62)
GLASS, LAMP = (34, 42, 58), (240, 200, 118)
BRASSY = (204, 168, 84)

LOOKS = {
    # a brick tenement: soot-brown brick, stone bands, sash windows, iron and slate
    "1": dict(style="brick",
              houses=dict(W=dict(c=(124, 74, 58)), N=dict(c=(150, 126, 88)),
                          E=dict(c=(136, 96, 78)), S=dict(c=(100, 66, 60))),
              passage=dict(field=(206, 198, 176), fstyle="block", mark=(170, 162, 142), dado=(104, 62, 44),
                           dstyle="concrete", rail=(40, 36, 34), skirt=(40, 30, 26), cornice=(170, 162, 142)),
              wash=dict(field=(230, 234, 228), fstyle="tile", mark=(190, 200, 196), dado=(46, 96, 76),
                        dstyle="concrete", rail=(30, 34, 34), skirt=(30, 44, 38), cornice=(46, 96, 76)),
              office=dict(field=(44, 74, 60), fstyle="stripe", mark=(58, 92, 74), dado=(92, 48, 34),
                          dstyle="panel", rail=BRASSY, skirt=(44, 24, 18), cornice=(222, 212, 186)),
              loft=dict(field=(178, 160, 132), fstyle="plaster", mark=(150, 132, 106), dado=(112, 84, 58),
                        dstyle="boards", rail=(70, 50, 34), skirt=(60, 44, 30), cornice=(90, 66, 44)),
              suite=dict(field=(190, 144, 138), fstyle="damask", mark=(170, 120, 118), dado=(216, 206, 182),
                         dstyle="panel", rail=(150, 110, 100), skirt=(80, 56, 44), cornice=(226, 218, 196)),
              low=(202, 194, 174), wood=(70, 86, 70)),
    # a whitewashed court in the south: lime wash, painted dados and shutters, pantiles
    "2": dict(style="render",
              houses=dict(W=dict(c=(236, 232, 218), trim=(62, 104, 150)), N=dict(c=(226, 214, 190), trim=(70, 112, 84)),
                          E=dict(c=(224, 184, 112), trim=(120, 76, 48)), S=dict(c=(222, 170, 140), trim=(110, 62, 48))),
              passage=dict(field=(234, 230, 216), fstyle="plaster", mark=(216, 210, 194), dado=(206, 160, 90),
                           dstyle="concrete", rail=(150, 104, 60), skirt=(120, 84, 52), cornice=(120, 84, 52)),
              wash=dict(field=(236, 234, 224), fstyle="plaster", mark=(220, 216, 204), dado=(60, 104, 160),
                        dstyle="panel", rail=(236, 234, 224), skirt=(40, 70, 112), cornice=(60, 104, 160)),
              office=dict(field=(234, 228, 210), fstyle="plaster", mark=(214, 206, 186), dado=(98, 64, 42),
                          dstyle="boards", rail=(70, 46, 30), skirt=(60, 40, 26), cornice=(98, 64, 42)),
              loft=dict(field=(226, 206, 160), fstyle="plaster", mark=(208, 186, 138), dado=(214, 190, 140),
                        dstyle="concrete", rail=(150, 104, 60), skirt=(120, 84, 52), cornice=(120, 84, 52)),
              suite=dict(field=(196, 212, 216), fstyle="stripe", mark=(176, 196, 204), dado=(236, 232, 220),
                         dstyle="boards", rail=(150, 170, 178), skirt=(110, 130, 138), cornice=(236, 232, 220)),
              low=(236, 232, 220), wood=(98, 64, 42)),
    # an inn yard: black timber frames and cream panels over rubble stone, thatch
    "3": dict(style="timber",
              houses=dict(W=dict(c=(228, 216, 186)), N=dict(c=(216, 192, 142)),
                          E=dict(c=(234, 228, 210)), S=dict(c=(204, 184, 152))),
              passage=dict(field=(160, 152, 138), fstyle="block", mark=(120, 114, 102), dado=(132, 126, 114),
                           dstyle="concrete", rail=OAK, skirt=(70, 66, 60), cornice=OAK),
              wash=dict(field=(226, 218, 196), fstyle="plaster", mark=(206, 196, 172), dado=(150, 144, 132),
                        dstyle="concrete", rail=OAK, skirt=(90, 86, 78), cornice=OAK),
              office=dict(field=(126, 88, 54), fstyle="panel", mark=(84, 56, 32), dado=(104, 70, 42),
                          dstyle="boards", rail=(60, 40, 24), skirt=(50, 34, 22), cornice=(70, 46, 28)),
              loft=dict(field=(190, 164, 112), fstyle="slats", mark=(120, 92, 56), dado=(110, 80, 50),
                        dstyle="boards", rail=OAK, skirt=(54, 38, 26), cornice=OAK),
              suite=dict(field=(66, 90, 68), fstyle="damask", mark=(96, 122, 86), dado=(110, 76, 46),
                         dstyle="panel", rail=BRASSY, skirt=(50, 34, 22), cornice=(70, 46, 28)),
              low=(128, 92, 58), wood=OAK),
}


def mirror(im, y0=0, y1=None):
    """Makes rows y0..y1 read the same from the right as from the left."""
    for y in range(y0, im.h if y1 is None else y1):
        for x in range(1, im.w // 2):
            im.px[y * im.w + im.w - x] = list(im.px[y * im.w + x])
    return im


def crop(im, y0, y1):
    out = Img(im.w, y1 - y0)
    out.px = [list(p) for p in im.px[y0 * im.w:y1 * im.w]]
    return out


def paste(dst, src, y):
    for i, p in enumerate(src.px):
        dst.px[y * dst.w + i] = list(p)


def grime(im, y0, y1, f):
    """Darkens rows y0..y1, more towards y1 (down to factor f)."""
    for y in range(max(0, y0), min(im.h, y1)):
        k = 1 - (1 - f) * (y - y0) / max(1, y1 - y0 - 1)
        for x in range(im.w):
            p = im.px[y * im.w + x]
            p[:3] = shade(p[:3], k)


def rubble(im, y0, y1, c, seed):
    """Rough stonework over rows y0..y1."""
    rnd = random.Random(seed)
    y = y0
    while y < y1:
        hh = rnd.choice((10, 12, 14))
        x = -rnd.randrange(12)
        while x < 34:
            w = rnd.randrange(10, 22)
            col = shade(c, rnd.choice((0.86, 0.94, 1.0, 1.0, 1.08)))
            im.rect(max(0, x), y, min(64, x + w), min(y1, y + hh), col)
            im.rect(max(0, x), y, min(64, x + 1), min(y1, y + hh), shade(c, 0.55))
            x += w
        im.rect(0, y, 64, y + 1, shade(c, 0.55))
        y += hh
    mirror(im, y0, y1)


def top_edge(im, style, rows):
    """What a front ends in at the top, over `rows` rows: gutter and cornice,
    pantiles, or thatch."""
    if style == "brick":
        a, b, c = rows * 3 // 16, rows * 5 // 16, rows // 2
        im.rect(0, 0, 64, a, (66, 70, 82))                           # slates
        im.rect(0, a - 1, 64, a, (96, 100, 112))
        im.rect(0, a, 64, b, (26, 28, 32))                           # gutter
        im.rect(0, b, 64, c, STONE)
        for x in range(0, 64, 8):                                    # dentils
            im.rect(x, c, x + 4, rows - 2, STONE)
            im.rect(x + 4, c, x + 8, rows - 2, shade(STONE, 0.45))
        im.rect(0, rows - 2, 64, rows, shade(STONE, 0.8))
    elif style == "render":
        t = rows * 3 // 4
        for x in range(64):
            f = 0.72 + 0.4 * abs(((x % 16) - 8) / 8)
            im.rect(x, 0, x + 1, t, shade(TERRA, f))
            d = 3 if 4 <= x % 16 < 12 else 0
            im.rect(x, t, x + 1, t + d, shade(TERRA, f * 0.8))
            im.rect(x, t + d, x + 1, rows, (70, 56, 50))
        im.rect(0, t // 2, 64, t // 2 + 1, shade(TERRA, 0.6))
    else:
        straw = (170, 142, 86)
        rnd = random.Random(rows)
        for x in range(33):
            col = shade(straw, rnd.choice((0.8, 0.9, 1.0, 1.1)))
            d = rows - 6 + rnd.randrange(5)
            for xx in (x, (64 - x) % 64):
                im.rect(xx, 0, xx + 1, d, col)
                im.rect(xx, d, xx + 1, rows, (48, 38, 28))
        im.rect(0, 0, 64, 2, shade(straw, 0.6))
        im.rect(0, rows // 2, 64, rows // 2 + 1, shade(straw, 0.7))  # the binding


def window(im, style, p, t, lit):
    """A window whose head is at row t, in the middle of a 64-wide front."""
    glass = LAMP if lit else GLASS
    if style == "brick":
        im.rect(6, t - 12, 58, t, STONE)                             # lintel
        im.rect(6, t - 1, 58, t, shade(STONE, 0.6))
        for x in (20, 31, 43):
            im.rect(x, t - 12, x + 1, t - 1, shade(STONE, 0.75))
        im.rect(12, t, 52, t + 76, (232, 226, 206))                  # sash
        im.rect(15, t + 3, 49, t + 73, glass)
        im.rect(15, t + 36, 49, t + 40, (232, 226, 206))
        im.rect(31, t + 3, 33, t + 73, (232, 226, 206))
        if lit:                                                      # curtains
            for i in range(34):
                im.rect(15, t + 3 + i, 15 + (34 - i) // 5, t + 4 + i, (176, 96, 70))
                im.rect(49 - (34 - i) // 5, t + 3 + i, 49, t + 4 + i, (176, 96, 70))
        else:
            for i in range(12):
                im.set(18 + i, t + 30 - i, (70, 84, 104))
        im.frame(12, t, 52, t + 76, (120, 112, 96), 1)
        im.rect(6, t + 76, 58, t + 82, STONE)                        # sill
        im.rect(6, t + 82, 58, t + 84, shade(p["c"], 0.55))
    elif style == "render":
        trim = p["trim"]
        im.rect(18, t - 2, 46, t + 80, shade(p["c"], 0.78))          # reveal
        im.rect(20, t, 44, t + 80, glass if lit else (30, 30, 34))
        im.rect(31, t, 33, t + 80, (70, 50, 36))
        im.rect(20, t + 38, 44, t + 40, (70, 50, 36))
        for x1 in (8, 44):                                           # shutters, folded back
            im.rect(x1, t, x1 + 12, t + 80, trim)
            for y in range(t + 3, t + 78, 4):
                im.rect(x1 + 2, y, x1 + 10, y + 1, shade(trim, 0.68))
            im.frame(x1, t, x1 + 12, t + 80, shade(trim, 0.6), 1)
        im.rect(16, t + 80, 48, t + 84, TERRA)                       # sill
        im.rect(16, t + 84, 48, t + 86, shade(p["c"], 0.7))
    else:
        im.rect(8, t, 56, t + 72, OAK)
        for y in range(t + 3, t + 69):
            for x in range(11, 53):
                lead = (x + y) % 8 == 0 or (x - y) % 8 == 0
                im.set(x, y, (56, 54, 50) if lead else glass if lit else (44, 56, 62))
        im.rect(31, t, 33, t + 72, OAK)
        im.rect(8, t + 72, 56, t + 75, shade(OAK, 1.5))


def facade(L, h, win=0, top="edge"):
    """House h's front in look L, 64 by 512: three storeys of 160 under 32
    rows of eaves. win 1 or 2: a window on each upper storey (1: the lower
    one is lit; 2: the upper one). top "coping": a plain top instead of eaves."""
    style, p = LOOKS[L]["style"], LOOKS[L]["houses"][h]
    c, seed = p["c"], 600 + 10 * int(L) + "WNES".index(h)
    if style == "brick":
        im = mirror(th.brick(64, 512, c, shade(c, 0.6), seed))
        im.noise(5, seed)
        grime(im, 300, 512, 0.84)
        for r in (190, 350):                                         # a stone band at every floor
            im.rect(0, r, 64, r + 6, STONE)
            im.rect(0, r, 64, r + 1, shade(STONE, 1.12))
            im.rect(0, r + 6, 64, r + 8, shade(c, 0.5))
        for y in range(486, 512):                                    # plinth
            for x in range(64):
                q = im.px[y * 64 + x]
                q[:3] = shade(q[:3], 0.62)
        im.rect(0, 484, 64, 486, shade(c, 0.45))
    elif style == "render":
        im = Img(64, 512, c)
        rnd = random.Random(seed)
        for _ in range(7):                                           # rain marks
            x, y, n = rnd.randrange(2, 31), rnd.randrange(40, 380), rnd.randrange(30, 90)
            im.rect(x, y, x + 2, y + n, shade(c, 0.93))
        mirror(im)
        im.noise(4, seed)
        trim = p["trim"]
        im.rect(0, 440, 64, 512, shade(trim, 0.9))                   # the painted dado
        im.rect(0, 438, 64, 440, shade(trim, 0.6))
        grime(im, 490, 512, 0.7)
        for r in (192, 352):
            im.rect(0, r - 1, 64, r + 1, shade(c, 0.86))
    else:
        im = Img(64, 512, c)
        im.noise(6, seed)
        rubble(im, 358, 512, (146, 138, 124), seed)
        grime(im, 440, 512, 0.8)
        for x1, x2 in ((0, 4), (60, 64), (30, 34)):                  # posts and a stud
            im.rect(x1, 0, x2, 358, OAK)
        for r in (108, 268):                                         # rails
            im.rect(0, r, 64, r + 4, OAK)
        for r0, r1 in ((112, 186), (272, 346)):                      # braces
            for i in range(r1 - r0):
                x = 5 + i * 24 // (r1 - r0)
                im.rect(x, r1 - i - 1, x + 4, r1 - i, OAK)
                im.rect(60 - x - 3, r1 - i - 1, 60 - x + 1, r1 - i, OAK)
        for r in (186, 346):                                         # the beam under each storey
            im.rect(0, r, 64, r + 12, OAK)
            im.rect(0, r, 64, r + 1, shade(OAK, 1.6))
            im.rect(0, r + 12, 64, r + 15, shade(c if r < 300 else (146, 138, 124), 0.55))
            for x in (16, 48):
                im.disc(x, r + 6, 1, shade(OAK, 1.7))
    if win:
        for t, lit in ((64, win == 2), (224, win == 1)):
            window(im, style, p, t, lit)
    if top == "coping":
        cc = {"brick": STONE, "render": TERRA, "timber": OAK}[style]
        im.rect(0, 0, 64, 8, cc)
        im.rect(0, 8, 64, 10, shade(cc, 0.5))
    else:
        top_edge(im, style, 32)
    return im


def lining(L):
    """The light well below the roof, 448: pale, to throw light down, and dirtier
    the deeper it goes."""
    style = LOOKS[L]["style"]
    if style == "brick":                                             # white glazed brick
        im = mirror(th.brick(64, 448, (226, 228, 220), (168, 174, 170), 640))
        im.rect(0, 0, 64, 6, STONE)
    elif style == "render":
        im = Img(64, 448, (234, 230, 216))
        rnd = random.Random(641)
        for _ in range(10):
            x, y = rnd.randrange(2, 31), rnd.randrange(10, 330)
            im.rect(x, y, x + 2, y + rnd.randrange(40, 110), (212, 208, 190))
        mirror(im)
        im.rect(0, 384, 64, 448, (62, 104, 150))
        im.rect(0, 382, 64, 384, (40, 70, 112))
        im.rect(0, 0, 64, 6, TERRA)
    else:
        im = Img(64, 448, (146, 138, 124))
        rubble(im, 0, 448, (146, 138, 124), 642)
        rnd = random.Random(643)
        for _ in range(160):                                         # moss, thicker lower down
            y = int(448 * rnd.random() ** 0.5)
            x = rnd.randrange(32)
            for xx in (x, (64 - x) % 64):
                im.rect(xx, y, xx + 2, y + 2, (92, 112, 70))
        im.rect(0, 0, 64, 8, OAK)
    im.noise(4, 644 + int(L))
    grime(im, 160, 448, 0.8 if style == "brick" else 0.7)
    return im


def flat(kind, seed):
    f = Img(64, 64)
    rnd = random.Random(seed)
    if kind == "setts":                                              # small dressed stones
        f = th.brick(64, 64, (100, 102, 110), (56, 56, 64), seed)
        f.noise(8, seed)
    elif kind == "slabs":
        f = Img(64, 64, (208, 188, 148))
        f.noise(7, seed)
        for i in (0, 32):
            f.rect(i, 0, i + 1, 64, (168, 148, 110))
            f.rect(0, i, 64, i + 1, (168, 148, 110))
    elif kind == "earth":
        f = Img(64, 64, (122, 98, 68))
        f.noise(12, seed)
        for _ in range(26):                                          # straw
            x, y = rnd.randrange(60), rnd.randrange(62)
            f.rect(x, y, x + rnd.randrange(2, 5), y + 1, (190, 168, 106))
        for _ in range(6):
            f.disc(rnd.randrange(64), rnd.randrange(64), 2, (146, 140, 128))
    elif kind == "flags":                                            # big pale flagstones
        f = Img(64, 64, (172, 164, 148))
        f.noise(6, seed)
        for j, y in enumerate((0, 32)):
            f.rect(0, y, 64, y + 2, (112, 106, 96))
            for x in ((0, 40) if j else (20, 52)):
                f.rect(x, y, x + 2, y + 32, (112, 106, 96))
    elif kind == "tiles":                                            # terracotta squares
        f = Img(64, 64, (190, 106, 70))
        for i in range(0, 64, 16):
            for j in range(0, 64, 16):
                f.rect(i, j, i + 16, j + 16, shade((190, 106, 70), rnd.choice((0.92, 1.0, 1.07))))
            f.rect(i, 0, i + 1, 64, (138, 72, 48))
            f.rect(0, i, 64, i + 1, (138, 72, 48))
        f.noise(5, seed)
    elif kind == "cobbles":
        f = Img(64, 64, (78, 72, 66))
        for j, y in enumerate(range(4, 64, 8)):
            for x in range(4 + (4 if j % 2 else 0), 68, 8):
                f.disc(x % 64, y, 3, shade((146, 142, 132), rnd.choice((0.85, 1.0, 1.1))))
        f.noise(6, seed)
    elif kind == "lead":                                             # sheet lead, rolled at the joints
        f = Img(64, 64, (118, 124, 134))
        f.noise(5, seed)
        for x in (0, 32):
            f.rect(x, 0, x + 3, 64, (150, 156, 166))
            f.rect(x + 3, 0, x + 5, 64, (80, 84, 92))
    elif kind == "rooftiles":
        f = Img(64, 64, (204, 132, 92))
        for j, y in enumerate(range(0, 64, 16)):
            f.rect(0, y, 64, y + 2, (150, 86, 58))
            for x in range(8 if j % 2 else 0, 64, 16):
                f.rect(x, y, x + 1, y + 16, (150, 86, 58))
        f.noise(6, seed)
    elif kind == "shingles":                                         # weathered boards, moss in the joints
        f = Img(64, 64, (112, 100, 76))
        f.noise(8, seed)
        for y in range(0, 64, 8):
            f.rect(0, y, 64, y + 1, (66, 58, 44))
        for _ in range(40):
            f.set(rnd.randrange(64), rnd.randrange(8) * 8 + 1, (96, 118, 70))
    elif kind == "quarry":                                           # red and black quarry tiles
        f = Img(64, 64, (134, 72, 54))
        for i in range(4):
            for j in range(4):
                if (i + j) % 2:
                    f.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, (58, 52, 52))
        f.noise(5, seed)
    elif kind == "bluewhite":
        f = Img(64, 64, (236, 236, 228))
        for i in range(4):
            for j in range(4):
                if (i + j) % 2:
                    f.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, (72, 116, 168))
        f.noise(4, seed)
    elif kind == "baize":                                            # a dark green carpet, gold spots
        f = Img(64, 64, (40, 74, 58))
        f.noise(5, seed)
        for cx in range(0, 65, 16):
            for cy in range(0, 65, 16):
                if (cx + cy) // 16 % 2:
                    f.diamond(cx, cy, 2, BRASSY)
    elif kind == "rush":                                             # rush matting
        f = Img(64, 64, (172, 148, 98))
        for y in range(0, 64, 4):
            for x in range(0, 64, 8):
                if (x // 8 + y // 4) % 2:
                    f.rect(x, y, x + 8, y + 4, (150, 126, 80))
        f.noise(6, seed)
    return f


def ceiling(base, beam, step, seed):
    """A flat `base` crossed by beams every `step`."""
    c = Img(64, 64, base)
    c.noise(4, seed)
    if beam:
        for x in range(0, 64, step):
            c.rect(x, 0, x + 6, 64, beam)
            c.rect(x + 6, 0, x + 7, 64, shade(base, 0.6))
    else:
        c.frame(0, 0, 64, 64, shade(base, 0.9), 1)
    return c


def railing(style):
    r = Img(64, 32, (0, 0, 0, 0))
    if style == "brick":                                             # iron, with spear heads
        r.rect(0, 3, 64, 6, IRON)
        r.rect(0, 28, 64, 31, IRON)
        for x in range(3, 64, 8):
            r.rect(x, 2, x + 2, 28, IRON)
            r.set(x, 1, IRON)
            r.set(x + 1, 0, IRON)
    elif style == "render":                                          # turned wood
        w = (132, 90, 56)
        r.rect(0, 0, 64, 5, w)
        r.rect(0, 0, 64, 1, shade(w, 1.3))
        r.rect(0, 27, 64, 32, shade(w, 0.8))
        for x in range(6, 64, 16):
            r.rect(x, 5, x + 4, 27, w)
            r.rect(x - 1, 12, x + 5, 20, shade(w, 1.12))
    else:                                                            # oak, cross-braced
        r.rect(0, 0, 64, 6, OAK)
        r.rect(0, 0, 64, 1, shade(OAK, 1.6))
        r.rect(0, 26, 64, 32, OAK)
        for x in (0, 32):
            r.rect(x, 6, x + 4, 26, OAK)
            for i in range(20):
                xx = x + 4 + i * 28 // 20
                r.rect(xx, 6 + i, xx + 3, 7 + i, OAK)
                r.rect(x + 32 - (xx - x) - 3, 6 + i, x + 32 - (xx - x), 7 + i, OAK)
    return r


def make(out, rd):
    """`rd` is the plain room door (leaf in its bottom 96 rows)."""
    FLATS = {"1": ("setts", "flags", "lead", "quarry", "baize"),
             "2": ("slabs", "tiles", "rooftiles", "bluewhite", "tiles"),
             "3": ("earth", "cobbles", "shingles", "flags", "rush")}
    for n, c in LOOKS.items():
        k, style = int(n), c["style"]
        fronts = {}
        for h in "WNES":
            fronts[h] = facade(n, h)
            out[f"textures/AJ4Y{n}{h}.png"] = fronts[h].png()
            out[f"textures/AJ4Z{n}{h}.png"] = facade(n, h, 1).png()
            out[f"textures/AJ4U{n}{h}.png"] = facade(n, h, 2).png()
        # the fronts of the balcony, the roof and the loft: the house below them
        # (balcony and loft: the whole front with their edge at its height,
        # because the railing's line is lower-unpegged; see map_hinges4.py)
        deck = facade(n, "W")
        edge = {"brick": (60, 62, 70), "render": (132, 90, 56), "timber": OAK}[style]
        deck.rect(0, 352, 64, 362, edge)
        deck.rect(0, 352, 64, 353, shade(edge, 1.5))
        for x in range(4, 64, 16):                                   # joist ends
            deck.rect(x, 362, x + 6, 370, shade(edge, 0.8))
            deck.rect(x, 370, x + 6, 372, shade(edge, 0.4))
        out[f"textures/AJ4B{n}.png"] = deck.png()
        for name, w in (("R", 0), ("Q", 1)):
            face = crop(fronts["N"] if not w else facade(n, "N", 1), 192, 512)
            top_edge(face, style, 16)
            out[f"textures/AJ4{name}{n}.png"] = face.png()
        loft = facade(n, "E")
        loft.rect(0, 320, 64, 328, edge)
        loft.rect(0, 320, 64, 321, shade(edge, 1.5))
        loft.rect(0, 328, 64, 330, shade(edge, 0.4))
        out[f"textures/AJ4T{n}.png"] = loft.png()
        gable = crop(facade(n, "N", top="coping"), 0, 192)
        out[f"textures/AJ4G{n}.png"] = gable.png()
        lin = lining(n)
        out[f"textures/AJ4L{n}.png"] = lin.png()
        well = Img(64, 640)
        paste(well, gable, 0)
        paste(well, lin, 192)
        out[f"textures/AJ4V{n}.png"] = well.png()
        out[f"textures/AJ4N{n}.png"] = railing(style).png()
        for tag, kind in zip("FPMIK", FLATS[n]):
            out[f"flats/AJ4{tag}{n}.png"] = flat(kind, 650 + 10 * k + "FPMIK".index(tag)).png()
        # rooms
        walls = {}
        for tag, part, h in (("A", "passage", 128), ("H", "wash", 128), ("O", "office", 128),
                             ("J", "loft", 144), ("W", "suite", 112)):
            walls[tag] = th.wall(c[part], h, seed=700 + 10 * k + ord(tag))
            out[f"textures/AJ4{tag}{n}.png"] = walls[tag].png()
        out[f"flats/AJ4E{n}.png"] = ceiling(c["low"], None if n == "1" else c["wood"], 32, 690 + k).png()
        under = {"1": (62, 60, 62), "2": (198, 172, 112), "3": (150, 124, 72)}[n]   # slates, cane, thatch
        out[f"flats/AJ4C{n}.png"] = ceiling(under, (122, 92, 60) if n != "3" else OAK, 16, 695 + k).png()
        wood = (104, 72, 44)
        for tag, base, keys in (("W", "H", ""), ("O", "O", "34"), ("S", "W", "12")):
            d = th.door(walls[base], rd, wood)
            out[f"textures/AJ4D{n}{tag}.png"] = d.png()
            if keys:
                out[f"textures/AJ4D{n}{tag}{keys}.png"] = th.locked(d, keys).png()

    # --- below ground, the same whatever stands on it -------------------------
    cellar = mirror(th.brick(64, 128, (104, 88, 78), (54, 46, 44), 760))
    cellar.noise(6, 761)
    grime(cellar, 60, 128, 0.62)
    cellar.rect(0, 0, 64, 4, (40, 34, 32))
    out["textures/AJ4XC.png"] = cellar.png()
    st = mirror(th.brick(64, 64, (104, 88, 78), (54, 46, 44), 762))
    st.noise(6, 763)
    out["textures/AJ4XR.png"] = st.png()
    kennel = mirror(th.brick(64, 128, (190, 186, 172), (150, 146, 134), 764))   # whitewash, once
    kennel.noise(5, 765)
    grime(kennel, 70, 128, 0.55)
    kennel.disc(32, 70, 6, IRON)                                     # a ring for a chain
    kennel.disc(32, 70, 4, (150, 146, 134))
    kennel.rect(30, 58, 34, 64, IRON)
    kennel.rect(0, 0, 64, 4, (40, 34, 32))
    out["textures/AJ4XK.png"] = kennel.png()
    earth = Img(64, 64, (64, 56, 50))
    earth.noise(10, 766)
    for x, y in ((0, 0), (32, 32)):
        earth.rect(x, y, x + 32, y + 1, (44, 38, 34))
        earth.rect(x, y, x + 1, y + 32, (44, 38, 34))
    out["flats/AJ4XF.png"] = earth.png()
    straw = Img(64, 64, (170, 144, 82))
    straw.noise(14, 767)
    rnd = random.Random(768)
    for _ in range(70):
        x, y, n = rnd.randrange(64), rnd.randrange(64), rnd.randrange(3, 8)
        for i in range(n):
            straw.set((x + i) % 64, (y + (i // 2 if x % 2 else -i // 2)) % 64, rnd.choice(((206, 182, 112), (124, 100, 54))))
    out["flats/AJ4XS.png"] = straw.png()
    out["flats/AJ4XD.png"] = ceiling((36, 30, 26), (78, 58, 40), 32, 769).png()
    bars = Img(64, 56, (0, 0, 0, 0))
    for x in range(2, 64, 8):
        bars.rect(x, 0, x + 3, 56, IRON)
        bars.rect(x, 0, x + 1, 56, (74, 74, 82))
    for y in (6, 46):
        bars.rect(0, y, 64, y + 4, IRON)
    out["textures/AJ4XB.png"] = bars.png()
    shelf = Img(64, 112, (70, 50, 36))                               # the pantry: shelves of jars
    rnd = random.Random(770)
    for y in range(8, 112, 26):
        x = 3
        while x < 30:
            w, hh = rnd.choice((5, 6, 8)), rnd.randrange(10, 19)
            col = rnd.choice(((176, 60, 50), (206, 170, 70), (120, 150, 90), (226, 222, 206), (150, 96, 56)))
            shelf.rect(x, y + 22 - hh, x + w, y + 22, col)
            shelf.rect(x, y + 22 - hh, x + w, y + 24 - hh, (226, 222, 206))
            shelf.rect(x, y + 22 - hh, x + 1, y + 22, shade(col, 1.3))
            x += w + 2
        shelf.rect(0, y + 22, 64, y + 26, (132, 96, 62))
        shelf.rect(0, y + 25, 64, y + 26, (40, 28, 20))
    mirror(shelf)
    shelf.rect(0, 0, 64, 8, (132, 96, 62))
    shelf.rect(0, 7, 64, 8, (40, 28, 20))
    shelf.noise(4, 771)
    out["textures/AJ4XP.png"] = shelf.png()
