"""Candidate looks for MAP06, the museum (see AJAR_MUSEUM in map_hinges6.py).

Three looks for the whole museum, numbered 1 to 3. For look n (T = tag + n):
  AJ6Y<n>   the building's front round the court and the terrace, 640: rows count
            down from the sky's edge at 512. 0..176 attic and cornice, 176..352 the
            upper floor, 352..512 the ground floor, 512..640 below ground (the court
            is sunk). AJ6YA<n>, AJ6YB<n> with windows (the upper one lit; all dark)
  AJ6YC<n>, AJ6YT<n> (+A, +B)  the same over a porch: a lintel at 56 up (the court's
            porches) or at 128 (the terrace's, the mouth of the steps)
  AJ6YU<n>  the wall round the roof, 288; AJ6YR<n> over the roof's porch
  AJ6YG<n>  what carries the upper gallery, from its floor down (288)
  AJ6YS<n>  the east front, from the roof's edge down (352)
  AJ6YE<n>  the terrace's edge over the court (128)
  AJ6H<n>   great hall wall, 384; AJ6H<n>1, 2 with a big picture; AJ6HK<n> and
            AJ6HL<n> over a porch (128) and over the lobby's mouth (192);
            AJ6HV<n> the mezzanine's front (192), AJ6HG<n> the upper gallery's (160),
            AJ6HM<n> the mezzanine's own wall (192)
  AJ6L<n>   lobby, 192 (AJ6L<n>1 with the plan of the museum)   AJ6A<n> porches, 128
  AJ6S<n>   stairs: a porch wall with 128 rows of lining under it
  AJ6U<n>   upper gallery, 176 (AJ6U<n>1, 2 with pictures)
  AJ6WA<n>, AJ6WB<n>  west wing rooms, 160; AJ6EA<n>, AJ6EB<n> east wing rooms;
            each with pictures 1 to 3 (AJ6WA<n>1 ...)
  AJ6K<n> cloakroom  AJ6M<n> gift shop  AJ6C<n> cafe (AJ6C<n>1 the menu)
  AJ6O<n> office     AJ6R<n> archive (all 128)
  AJ6D<n><letter>  a room door's face, AJ6Z<n><letter> a bolted door's (FACES, BOLTS)
  AJ6RL<n> railing   AJ6V<n> the side of a display case, AJ6VT<n> its top
  AJ6WD<n> desks and counters, AJ6BN<n> benches (wall and flat)
  flats: AJ6F<n> hall floor, AJ6P<n> the way through it, AJ6FW<n> wings and upper
         floors, AJ6FI<n> rooms, AJ6FC<n> cafe, AJ6FR<n> roof, AJ6FG<n> the court's
         ground, AJ6FT<n> paving; AJ6CH<n> hall ceiling, AJ6CG<n> galleries,
         AJ6CL<n> rooms, AJ6CP<n> porches
The same in all three: AJ6XC cellar (128), AJ6XB boiler room, AJ6XG grotto, AJ6XS
gardener's shed, AJ6XK stockroom, AJ6XP stone (steps, the fountain, garden seats),
AJ6XT a laid table, AJ6XA the archive's shelves.

Every wall is 64 wide and the same mirrored, and the map lines them up by world
position (Map.align), so cuts in a wall do not show. A door's face is drawn for
its own place in its wall instead (the shift in FACES). What stands free in a room
(cases, desks, benches, railings) repeats every 16.
"""
import math
import random

from gfx import Img, shade, BRASS
import gfx_theatre as th
import gfx_yard as gy
from gfx_station import arch, copy

NAMES = {"1": "Athenaeum", "2": "Cabinet", "3": "Kunsthalle"}

GILT, IVORY, STONE, MARBLE, INK = (204, 168, 84), (236, 230, 212), (206, 198, 178), (166, 158, 154), (38, 36, 40)
BUFF, SLATE, TERRA, MAHOG, CREAM = (212, 170, 112), (96, 108, 124), (164, 82, 56), (98, 48, 32), (226, 212, 176)
WHITE, CONC, STEEL, PLY = (236, 234, 228), (166, 164, 158), (30, 30, 34), (206, 170, 120)
NIGHT, GLASS, LAMP = (20, 26, 46), (28, 36, 54), (240, 200, 118)


def st(field, fstyle, mark, dado, dstyle, rail, skirt, cornice, **more):
    return dict(field=field, fstyle=fstyle, mark=mark, dado=dado, dstyle=dstyle, rail=rail, skirt=skirt,
                cornice=cornice, **more)


def bare(c, skirt=STEEL, **more):
    """A wall of one colour from skirting to ceiling (the modern look)."""
    return st(c, "plain", c, c, "none", shade(c, 0.94), skirt, c, **more)


LOOKS = {
    # a museum of the 1830s: ashlar and marble, antiquities on Pompeian red, paintings on damask
    "1": dict(
        hall=st((224, 216, 194), "plain", (196, 186, 162), MARBLE, "marble", GILT, (58, 52, 52), IVORY, over="ashlar",
                stile=IVORY, bead=(176, 166, 142), frieze=(148, 60, 48), fz="swag", lining=(120, 114, 104)),
        low=st((226, 218, 198), "panel", (190, 178, 150), MARBLE, "marble", GILT, (58, 52, 52), IVORY,
               lining=(120, 114, 104)),
        upper=st((226, 218, 198), "panel", GILT, MARBLE, "marble", GILT, (58, 52, 52), IVORY,
                 frieze=(148, 60, 48), fz="stencil"),
        wa=st((152, 50, 40), "plain", (170, 66, 50), INK, "marble", GILT, (22, 20, 22), IVORY, frieze=INK, fz="stencil"),
        wb=st((198, 152, 66), "plain", (180, 134, 52), INK, "marble", GILT, (22, 20, 22), IVORY, frieze=INK, fz="stencil"),
        ea=st((58, 90, 70), "damask", (74, 108, 84), (226, 216, 190), "panel", GILT, (60, 48, 40), IVORY,
              frieze=(226, 216, 190), fz="swag"),
        eb=st((60, 74, 104), "damask", (76, 92, 124), (226, 216, 190), "panel", GILT, (60, 48, 40), IVORY,
              frieze=(226, 216, 190), fz="swag"),
        cloak=st((204, 190, 160), "plaster", (188, 174, 144), (104, 72, 46), "boards", (70, 46, 28), (50, 34, 22), IVORY),
        shop=st((226, 214, 180), "stripe", (206, 190, 150), (58, 90, 70), "panel", GILT, (40, 50, 40), IVORY),
        cafe=st((232, 226, 208), "tile", (204, 198, 180), (58, 90, 70), "panel", INK, (30, 40, 34), IVORY),
        office=st((112, 36, 42), "damask", (134, 52, 54), (86, 44, 30), "panel", GILT, (44, 24, 18), IVORY),
        archive=st((120, 84, 50), "panel", (84, 56, 32), (100, 68, 40), "boards", (60, 40, 24), (44, 30, 20), (70, 46, 28)),
        wood=(110, 70, 40), frame=GILT, mount=None, felt=(32, 62, 48), plinth=(214, 206, 186), bench=(104, 34, 36)),
    # a natural history museum of the 1870s: terracotta, glazed tile, mahogany and brass
    "2": dict(
        hall=st(BUFF, "block", (184, 144, 92), (40, 84, 70), "concrete", STEEL, (24, 40, 34), (226, 196, 140),
                stile=TERRA, bead=SLATE, frieze=SLATE, fz="stencil", lining=(70, 78, 90)),
        low=st((220, 184, 130), "tile", (190, 154, 104), (40, 84, 70), "concrete", STEEL, (24, 40, 34), (226, 196, 140),
               lining=(70, 78, 90)),
        upper=st((60, 96, 84), "plain", (60, 96, 84), MAHOG, "panel", BRASS, (40, 22, 16), CREAM, frieze=CREAM, fz="stencil"),
        wa=st((44, 84, 70), "plain", (44, 84, 70), MAHOG, "panel", BRASS, (40, 22, 16), CREAM, frieze=CREAM, fz="stencil"),
        wb=st((158, 112, 52), "stripe", (144, 98, 42), MAHOG, "panel", BRASS, (40, 22, 16), CREAM, frieze=CREAM, fz="stencil"),
        ea=st((36, 60, 94), "plain", (36, 60, 94), MAHOG, "panel", BRASS, (40, 22, 16), CREAM, frieze=CREAM, fz="stencil"),
        eb=st((112, 36, 42), "stripe", (98, 28, 34), MAHOG, "panel", BRASS, (40, 22, 16), CREAM, frieze=CREAM, fz="stencil"),
        cloak=st((214, 200, 164), "plaster", (196, 182, 146), (120, 62, 40), "boards", (70, 36, 24), (44, 24, 18), CREAM),
        shop=st(CREAM, "plaster", (208, 194, 158), MAHOG, "boards", BRASS, (40, 22, 16), CREAM),
        cafe=st(CREAM, "tile", (200, 186, 150), TERRA, "concrete", STEEL, (60, 30, 22), CREAM),
        office=st((44, 84, 70), "damask", (58, 100, 84), MAHOG, "panel", BRASS, (40, 22, 16), CREAM),
        archive=st((110, 56, 36), "panel", (70, 32, 22), MAHOG, "boards", (60, 28, 18), (40, 22, 16), (70, 36, 24)),
        wood=MAHOG, frame=(70, 34, 22), mount=(232, 224, 196), felt=(26, 30, 44), plinth=MAHOG, bench=(86, 42, 28)),
    # a gallery of the 1970s: white walls, board-marked concrete, black steel, pale oak
    "3": dict(
        hall=st(WHITE, "plain", WHITE, CONC, "concrete", (120, 118, 112), STEEL, WHITE, lining=(110, 108, 104)),
        low=st(CONC, "plain", CONC, CONC, "concrete", (130, 128, 122), STEEL, CONC, lining=(110, 108, 104)),
        upper=bare(WHITE),
        wa=bare(WHITE), wb=bare((208, 198, 178)), ea=bare(WHITE), eb=bare((46, 50, 60), skirt=(20, 20, 24)),
        cloak=st(PLY, "slats", (170, 134, 88), PLY, "boards", (150, 116, 74), STEEL, WHITE),
        shop=st(WHITE, "plain", WHITE, PLY, "boards", STEEL, STEEL, WHITE),
        cafe=st((232, 226, 208), "plain", WHITE, (208, 98, 40), "boards", STEEL, STEEL, WHITE),
        office=st((150, 98, 58), "panel", (104, 64, 36), (150, 98, 58), "boards", STEEL, STEEL, WHITE),
        archive=st((150, 156, 164), "slats", (104, 110, 118), (120, 126, 134), "boards", STEEL, STEEL, (150, 156, 164)),
        wood=(190, 150, 100), frame=STEEL, mount=(244, 242, 236), felt=(224, 222, 214), plinth=WHITE, bench=(34, 34, 38)),
}

# The faces of the room doors: letter -> (the wall it stands in, how far along
# that wall's 64 its left edge is, the keys it asks for). See door() in the map.
FACES = {
    "A": ("L", 32, ""), "B": ("K", 32, ""), "C": ("M", 32, ""),          # lobby; cloakroom; gift shop
    "D": ("A", 0, ""), "E": ("C", 0, ""),                                # a porch in the hall; the cafe
    "F": ("A", 0, "1"), "G": ("WA", 0, "1"),                             # the west wing's door
    "H": ("C", 16, "2"), "I": ("EA", 48, "2"),                           # the east wing's
    "J": ("WB", 48, "34"), "K": ("O", 16, "34"),                         # the office's
    "L": ("EB", 16, "23"), "M": ("R", 48, "23"),                         # the archive's
    "N": ("XC", 32, ""), "O": ("XB", 32, ""),                            # the boiler room's
}
BOLTS = {"A": ("A", 32), "B": ("A", 0), "C": ("XC", 48), "D": ("XC", 16), "E": ("XG", 0), "F": ("XS", 32)}

# wall textures the map lays by world position, by tag (the look's number follows)
ALIGNED = ("Y", "YA", "YB", "YC", "YCA", "YCB", "YT", "YTA", "YTB", "YU", "YR", "YG", "YS", "YE",
           "H", "HK", "HL", "HV", "HG", "HM", "L", "A", "S", "U", "WA", "WB", "EA", "EB", "K", "M", "C", "O", "R")
PICTURES = {"H": 2, "L": 1, "U": 2, "WA": 3, "WB": 3, "EA": 3, "EB": 3, "C": 1}
SAME = ("AJ6XC", "AJ6XB", "AJ6XG", "AJ6XS", "AJ6XK")


def aligned(n):
    return ({f"AJ6{t}{n}" for t in ALIGNED} | {f"AJ6{t}{n}{i + 1}" for t, k in PICTURES.items() for i in range(k)}
            | set(SAME))


def mix(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def ashlar(im, y0, y1, c, x0=0, x1=64, step=16):
    """Dressed stone: a joint every `step` rows, upright joints by turns."""
    j = shade(c, 0.84)
    for k, y in enumerate(range(y0, y1, step)):
        im.rect(x0, y, x1, y + 1, j)
        for x in ((0, 32) if k % 2 else (16, 48)):
            if x0 <= x < x1:
                im.rect(x, y, x + 1, min(y1, y + step), j)


# --- outdoors ------------------------------------------------------------------
_fronts = {}


def _base(n):
    if n in _fronts:
        return _fronts[n]
    if n == "1":                                                     # Portland stone
        im = Img(64, 640, STONE)
        ashlar(im, 0, 352, STONE)
        im.rect(0, 0, 64, 12, shade(STONE, 1.1))                     # coping
        im.rect(0, 12, 64, 14, shade(STONE, 0.6))
        im.frame(10, 44, 54, 124, shade(STONE, 0.82), 2)             # a sunk panel with a wreath
        im.rect(12, 46, 52, 122, shade(STONE, 0.95))
        im.disc(32, 84, 13, shade(STONE, 0.8))
        im.disc(32, 84, 9, shade(STONE, 0.95))
        im.rect(0, 150, 64, 164, shade(STONE, 0.93))                 # frieze, cornice
        for x in range(4, 64, 8):
            im.rect(x, 152, x + 1, 162, shade(STONE, 0.74))
        im.rect(0, 164, 64, 172, shade(STONE, 1.12))
        im.rect(0, 172, 64, 176, shade(STONE, 0.55))
        im.rect(0, 344, 64, 350, shade(STONE, 1.1))                  # string course
        im.rect(0, 350, 64, 352, shade(STONE, 0.6))
        for y in range(352, 512, 16):                                # rusticated ground floor
            im.rect(0, y, 64, y + 3, shade(STONE, 0.58))
            im.rect(0, y + 3, 64, y + 4, shade(STONE, 1.1))
        for y in range(512, 640):
            im.rect(0, y, 64, y + 1, shade(STONE, 0.72))
        for k, y in enumerate(range(512, 640, 32)):
            im.rect(0, y, 64, y + 3, shade(STONE, 0.4))
            for x in ((0, 32) if k % 2 else (16, 48)):
                im.rect(x, y, x + 2, y + 32, shade(STONE, 0.4))
        im.noise(5, 911)
        gy.grime(im, 430, 512, 0.9)
        gy.grime(im, 560, 640, 0.7)
    elif n == "2":                                                   # buff terracotta, banded in slate blue
        im = th.brick(64, 640, BUFF, shade(BUFF, 0.72), 912)
        for y in range(208, 344, 48):
            im.rect(0, y, 64, y + 6, SLATE)
            im.rect(0, y, 64, y + 1, shade(SLATE, 1.3))
        im.rect(0, 0, 64, 6, TERRA)                                  # cresting
        for x in range(64):
            im.rect(x, 6, x + 1, 14 - abs((x % 8) - 4), TERRA)
        im.rect(0, 14, 64, 16, shade(BUFF, 0.5))
        for cx in (8, 24, 40, 56):                                   # a blind arcade under the eaves
            arch(im, cx, 52, 6, 136, shade(BUFF, 0.6))
            arch(im, cx, 55, 4, 136, shade(BUFF, 0.78))
        im.rect(0, 136, 64, 140, TERRA)
        im.rect(0, 148, 64, 172, TERRA)                              # frieze of roundels
        for cx in (16, 48):
            im.disc(cx, 160, 7, shade(TERRA, 0.7))
            im.disc(cx, 160, 5, BUFF)
            im.disc(cx, 160, 2, SLATE)
        im.rect(0, 172, 64, 176, shade(SLATE, 0.6))
        im.rect(0, 344, 64, 350, TERRA)
        im.rect(0, 350, 64, 352, shade(TERRA, 0.5))
        for y in range(368, 512, 32):                                # striped ground floor
            for yy in range(y, y + 16):
                for x in range(64):
                    p = im.px[yy * 64 + x]
                    p[:3] = mix(p[:3], SLATE, 0.8)
        im.rect(0, 500, 64, 512, shade(SLATE, 0.7))
        gy.paste(im, th.brick(64, 128, shade(SLATE, 0.8), shade(SLATE, 0.5), 913), 512)
        im.noise(5, 914)
        gy.grime(im, 440, 512, 0.9)
        gy.grime(im, 560, 640, 0.7)
    else:                                                            # white render over board-marked concrete
        im = Img(64, 640, WHITE)
        im.rect(0, 0, 64, 6, STEEL)
        im.rect(0, 88, 64, 89, shade(WHITE, 0.86))
        im.rect(0, 0, 1, 344, shade(WHITE, 0.86))
        im.rect(0, 170, 64, 176, shade(CONC, 0.5))                   # the edges of the floors
        im.rect(0, 344, 64, 352, shade(CONC, 0.5))
        im.rect(0, 352, 64, 640, CONC)
        for y in range(352, 640, 8):
            im.rect(0, y, 64, y + 1, shade(CONC, 0.9))
        for y in range(368, 640, 32):
            for x in (16, 48):
                im.disc(x, y, 1, shade(CONC, 0.6))
        for y in range(512, 640):
            for x in range(64):
                p = im.px[y * 64 + x]
                p[:3] = shade(p[:3], 0.74)
        im.rect(0, 510, 64, 512, shade(CONC, 0.45))
        im.noise(4, 915)
        gy.grime(im, 120, 170, 0.93)
        gy.grime(im, 470, 510, 0.88)
        gy.grime(im, 580, 640, 0.75)
    _fronts[n] = gy.mirror(im)
    return _fronts[n]


def upper_window(im, n, lit):
    g = LAMP if lit else GLASS
    if n == "1":                                                     # tall, under a pediment
        pale = shade(STONE, 1.12)
        for i in range(12):
            im.rect(32 - 2 * i - 2, 196 + i, 32 + 2 * i + 2, 197 + i, pale)
        im.rect(8, 208, 56, 212, shade(STONE, 0.6))
        im.rect(13, 212, 51, 326, pale)
        im.rect(18, 217, 46, 322, g)
        for x in (31,):
            im.rect(x, 217, x + 2, 322, pale)
        for y in (250, 286):
            im.rect(18, y, 46, y + 2, pale)
        im.rect(9, 326, 55, 332, pale)
        im.rect(9, 332, 55, 334, shade(STONE, 0.55))
        if lit:
            for i in range(30):                                      # a curtain drawn back
                w = (30 - i) // 4
                im.rect(18, 217 + i, 18 + w, 218 + i, (120, 40, 40))
                im.rect(46 - w, 217 + i, 46, 218 + i, (120, 40, 40))
    elif n == "2":                                                   # two round-headed lights under one arch
        arch(im, 32, 196, 25, 326, TERRA)
        arch(im, 32, 201, 20, 326, shade(BUFF, 0.86))
        for cx in (22, 42):
            arch(im, cx, 222, 8, 322, shade(TERRA, 0.7))
            arch(im, cx, 225, 6, 320, g)
        im.disc(32, 212, 4, shade(TERRA, 0.7))
        im.disc(32, 212, 2, g)
        im.rect(31, 240, 33, 322, CREAM)
        im.rect(6, 326, 58, 332, TERRA)
        im.rect(6, 332, 58, 334, shade(TERRA, 0.5))
    else:                                                            # a ribbon of glass
        im.rect(0, 208, 64, 312, STEEL)
        im.rect(0, 212, 64, 308, g)
        for x in (0, 31):
            im.rect(x, 212, x + 2, 308, STEEL)
        if lit:
            for y in range(216, 308, 6):
                im.rect(2, y, 31, y + 1, shade(LAMP, 0.86))
                im.rect(33, y, 64, y + 1, shade(LAMP, 0.86))
        else:
            for i in range(40):
                im.set(6 + i // 2, 300 - i, shade(GLASS, 1.8))
                im.set(38 + i // 2, 290 - i, shade(GLASS, 1.8))
        im.rect(0, 312, 64, 314, shade(WHITE, 0.7))


def ground_window(im, n, top=384):
    """A dark window in the ground floor, its head at row `top`."""
    if n == "1":                                                     # round-headed, behind a grille
        arch(im, 32, top - 4, 20, top + 104, shade(STONE, 1.1))
        arch(im, 32, top, 16, top + 100, GLASS)
        for x in range(19, 46, 5):
            im.rect(x, top, x + 1, top + 100, (70, 72, 80))
        for y in (top + 30, top + 66):
            im.rect(16, y, 48, y + 1, (70, 72, 80))
        im.rect(10, top + 100, 54, top + 106, shade(STONE, 1.1))
        im.rect(10, top + 106, 54, top + 108, shade(STONE, 0.5))
    elif n == "2":
        arch(im, 32, top - 4, 19, top + 100, TERRA)
        arch(im, 32, top + 1, 14, top + 98, GLASS)
        im.rect(31, top + 1, 33, top + 98, shade(TERRA, 0.7))
        im.rect(18, top + 44, 46, top + 46, shade(TERRA, 0.7))
        im.rect(10, top + 100, 54, top + 106, TERRA)
        im.rect(10, top + 106, 54, top + 108, shade(TERRA, 0.5))
    else:                                                            # a sheet of glass to the ground
        im.rect(3, top - 16, 61, top + 122, STEEL)
        im.rect(6, top - 13, 58, top + 119, GLASS)
        im.rect(31, top - 13, 33, top + 119, STEEL)
        for i in range(60):
            im.set(8 + i // 3, top + 90 - i, shade(GLASS, 1.8))
            im.set(36 + i // 3, top + 70 - i, shade(GLASS, 1.8))


def lintel(im, n, row):
    """The beam over an opening whose head is at `row`."""
    if n == "1":
        c = shade(STONE, 1.1)
        im.rect(0, row - 18, 64, row, c)
        im.rect(0, row - 20, 64, row - 18, shade(STONE, 0.6))
        for i in range(16):
            im.rect(27 - i // 5, row - 18 + i, 37 + i // 5 + 1, row - 17 + i, shade(STONE, 0.9))
        im.rect(0, row - 3, 64, row, shade(STONE, 0.5))
    elif n == "2":                                                   # a riveted iron beam under a terracotta band
        im.rect(0, row - 20, 64, row - 14, TERRA)
        im.rect(0, row - 14, 64, row, (26, 44, 38))
        im.rect(0, row - 14, 64, row - 13, (70, 100, 88))
        for x in range(4, 64, 8):
            im.disc(x, row - 7, 1, (90, 120, 106))
        im.rect(0, row - 2, 64, row, (10, 16, 14))
    else:
        im.rect(0, row - 12, 64, row, STEEL)
        im.rect(0, row - 12, 64, row - 11, (90, 90, 96))
        im.rect(0, row - 14, 64, row - 12, shade(WHITE, 0.7))


def front(n, win=0, porch=None):
    """win 1: windows, the upper one lit; 2: windows, all dark. `porch` is the
    row of a porch's soffit: a lintel over it, and no window below."""
    im = copy(_base(n))
    if win:
        upper_window(im, n, win == 1)
        if porch is None:
            ground_window(im, n)
    if porch is not None:
        lintel(im, n, porch)
    return gy.mirror(im)


def edge(im, n, rows=10):
    """The edge of a floor or a roof drawn along the top of a wall."""
    c = {"1": shade(STONE, 1.12), "2": TERRA, "3": WHITE}[n]
    im.rect(0, 0, 64, rows, c)
    im.rect(0, 0, 64, 1, shade(c, 1.15))
    im.rect(0, rows, 64, rows + 3, shade(c, 0.5) if n != "3" else STEEL)
    if n == "1":
        for x in range(2, 64, 8):
            im.rect(x, rows + 3, x + 4, rows + 7, shade(STONE, 0.9))
    return im


def gallery_side(n):
    """Under the upper gallery: its floor's edge, a blind arcade, the court's wall."""
    im = gy.crop(_base(n), 352, 640)
    if n == "1":                                                     # an urn in every niche
        arch(im, 32, 24, 24, 152, shade(STONE, 1.08))
        arch(im, 32, 29, 19, 152, shade(STONE, 0.5))
        for y in range(29, 152):
            im.rect(14, y, 17, y + 1, shade(STONE, 0.36))
        im.rect(25, 132, 39, 152, shade(STONE, 0.95))
        im.rect(23, 130, 41, 133, shade(STONE, 1.1))
        bronze = (104, 96, 66)
        im.disc(32, 112, 9, bronze)
        im.rect(29, 96, 35, 104, bronze)
        im.rect(26, 93, 38, 96, bronze)
        im.rect(28, 121, 36, 130, bronze)
        im.disc(29, 109, 2, shade(bronze, 1.5))
    elif n == "2":
        arch(im, 32, 24, 24, 152, TERRA)
        arch(im, 32, 30, 18, 152, shade(SLATE, 0.62))
        im.disc(32, 78, 10, TERRA)
        im.disc(32, 78, 7, BUFF)
        im.disc(32, 78, 3, shade(SLATE, 0.8))
        for y in range(104, 152, 8):
            im.rect(14, y, 50, y + 1, shade(SLATE, 0.45))
    else:                                                            # a recess washed by a lamp
        for y in range(22, 150):
            for x in range(8, 56):
                d = math.hypot((x - 32) / 26, (y - 22) / 110)
                im.set(x, y, shade(CONC, 0.42 + 0.5 * max(0, 1 - d)))
        im.frame(8, 22, 56, 150, STEEL, 2)
        im.rect(28, 22, 36, 25, (255, 244, 214))
    return gy.mirror(edge(im, n))


def roof_side(n):
    """The east front from the roof's edge down: a parapet, the ground floor, the court's wall."""
    im = copy(_base(n))
    if n == "1":                                                     # a figure in every niche
        arch(im, 32, 372, 21, 504, shade(STONE, 1.08))
        arch(im, 32, 377, 16, 504, shade(STONE, 0.5))
        fig = (228, 222, 206)
        im.rect(23, 486, 41, 504, shade(STONE, 0.95))
        im.rect(21, 484, 43, 487, shade(STONE, 1.1))
        for y in range(412, 484):
            half = 5 + (y - 412) // 12
            im.rect(32 - half, y, 32 + half, y + 1, shade(fig, 0.86 + 0.14 * ((y // 3) % 2)))
        im.rect(24, 410, 40, 418, fig)
        im.disc(32, 402, 6, fig)
        im.rect(36, 418, 39, 452, shade(fig, 0.8))
    else:
        ground_window(im, n)
    im = gy.crop(im, 288, 640)
    return gy.mirror(edge(im, n, 16))


# --- pictures and things on walls ----------------------------------------------
def landscape(w, h, seed):
    r = random.Random(seed)
    im = Img(w, h)
    hz = h * r.choice((5, 6)) // 10
    top, low = r.choice((((70, 96, 130), (214, 190, 150)), ((40, 50, 84), (200, 124, 84)), ((120, 150, 170), (226, 220, 200))))
    ground = r.choice(((70, 90, 50), (96, 84, 50), (50, 70, 64)))
    for y in range(hz):
        im.rect(0, y, w, y + 1, mix(top, low, y / hz))
    for y in range(hz, h):
        im.rect(0, y, w, y + 1, shade(ground, 1.15 - 0.5 * (y - hz) / (h - hz)))
    ph = r.random() * 6
    for x in range(w):
        hh = int(5 + 3 * math.sin(x / 5 + ph) + 2 * math.sin(x / 2.3 + ph))
        im.rect(x, hz - hh, x + 1, hz, shade(ground, 0.66))
    im.disc(r.randrange(6, w - 6), r.randrange(5, hz - 10), 2, (250, 240, 200))
    tx = r.randrange(8, w - 8)
    im.rect(tx, hz - 12, tx + 2, hz + 4, (40, 30, 20))
    im.disc(tx, hz - 14, 5, shade(ground, 0.5))
    for _ in range(3):
        x = r.randrange(w - 8)
        im.rect(x, hz + r.randrange(4, h - hz - 2), x + r.randrange(4, 9), hz + r.randrange(4, h - hz - 2) + 1, shade(low, 0.8))
    im.noise(6, seed)
    return im


def portrait(w, h, seed):
    r = random.Random(seed)
    bg = r.choice(((44, 32, 26), (30, 36, 40), (52, 30, 30)))
    im = Img(w, h, bg)
    cx, sh, hy = w // 2, h * 6 // 10, h * 4 // 10
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - cx) / w, (y - hy) / h)
            im.set(x, y, shade(bg, 1.5 - 1.4 * d))
    coat = r.choice(((22, 22, 26), (96, 26, 30), (34, 52, 80), (196, 190, 172)))
    skin, hair = (214, 176, 140), r.choice(((40, 28, 20), (120, 90, 50), (190, 186, 180)))
    for y in range(sh, h):
        half = min(w // 2 - 1, 7 + (y - sh) * 2)
        im.rect(cx - half, y, cx + half, y + 1, shade(coat, 1.0 if (cx - half) % 2 else 0.92))
    im.rect(cx - 3, sh - 3, cx + 3, sh + 4, (232, 228, 216))
    rad = max(4, w // 7)
    im.disc(cx, hy - 2, rad + 1, hair)
    im.disc(cx, hy + 1, rad, skin)
    im.rect(cx - rad, hy + 1, cx - rad + 1, hy + rad, shade(skin, 0.7))
    for dx in (-rad // 2, rad // 2):
        im.set(cx + dx, hy, (30, 24, 20))
    im.rect(cx - 1, hy + rad // 2 + 1, cx + 2, hy + rad // 2 + 2, (150, 90, 80))
    im.noise(5, seed)
    return im


def still(w, h, seed):
    r = random.Random(seed)
    im = Img(w, h, (36, 30, 26))
    ty = h * 2 // 3
    im.rect(0, ty, w, h, (96, 64, 38))
    im.rect(0, ty, w, ty + 1, (150, 110, 70))
    im.rect(w // 2 - 2, ty, w, h, (214, 206, 186))
    bx = r.randrange(6, w // 3)
    im.rect(bx, ty - 22, bx + 7, ty, (36, 70, 50))
    im.rect(bx + 2, ty - 30, bx + 5, ty - 22, (36, 70, 50))
    im.rect(bx + 1, ty - 20, bx + 2, ty - 4, (110, 150, 120))
    im.disc(w * 2 // 3, ty - 3, 9, (150, 130, 96))
    im.rect(w * 2 // 3 - 10, ty - 14, w * 2 // 3 + 11, ty - 5, (36, 30, 26))
    for i, c in enumerate(((204, 120, 40), (170, 40, 36), (190, 170, 60), (110, 140, 60))):
        im.disc(w * 2 // 3 - 7 + i * 5, ty - 7 - (i % 2) * 3, 3, c)
    im.disc(w // 2 - 6, ty - 3, 3, (204, 120, 40))
    im.noise(5, seed)
    return im


def abstract(w, h, seed):
    r = random.Random(seed)
    kind = seed % 3
    if kind == 0:                                                    # two fields of colour
        a, b, c = r.choice((((120, 44, 30), (196, 110, 40), (60, 30, 40)), ((40, 60, 70), (150, 160, 130), (26, 34, 44)),
                            ((150, 140, 60), (200, 190, 150), (90, 80, 40))))
        im = Img(w, h, a)
        im.rect(4, 4, w - 4, h * 4 // 10, b)
        im.rect(4, h * 4 // 10 + 4, w - 4, h - 4, c)
        im.noise(9, seed)
    elif kind == 1:                                                  # a grid, some of it filled
        im = Img(w, h, (238, 234, 222))
        xs = sorted(r.sample(range(8, w - 8, 4), 2))
        ys = sorted(r.sample(range(8, h - 8, 4), 3))
        for (x1, y1, x2, y2), c in (((0, 0, xs[0], ys[0]), (176, 120, 40)), ((xs[1], ys[1], w, ys[2]), (40, 96, 104)),
                                    ((xs[0], ys[2], xs[1], h), (150, 70, 50))):
            im.rect(x1, y1, x2, y2, c)
        for x in xs:
            im.rect(x, 0, x + 2, h, STEEL)
        for y in ys:
            im.rect(0, y, w, y + 2, STEEL)
        im.noise(3, seed)
    else:                                                            # a ring on black
        im = Img(w, h, (24, 24, 28))
        im.disc(w // 2, h // 2, min(w, h) // 2 - 5, (232, 228, 214))
        im.disc(w // 2 + 2, h // 2 + 1, min(w, h) // 2 - 9, (24, 24, 28))
        im.noise(4, seed)
    return im


def relief(w, h, seed):
    c = (190, 178, 150)
    im = Img(w, h, c)
    im.noise(7, seed)
    im.frame(0, 0, w, h, shade(c, 0.7), 2)
    for x in range(4, w - 4, 6):                                     # a key pattern, top and bottom
        for y in (5, h - 9):
            im.rect(x, y, x + 4, y + 1, shade(c, 0.6))
            im.rect(x, y, x + 1, y + 4, shade(c, 0.6))
    dark, lite = shade(c, 0.62), shade(c, 1.14)
    for i, cx in enumerate(range(w // 6 + 2, w - 4, w // 3 - 1)):
        y0 = h // 3 - (2 if i == 1 else 0)
        im.disc(cx, y0, 3, dark)
        im.rect(cx - 3, y0 + 4, cx + 3, y0 + 16, dark)
        im.rect(cx + 3, y0 + 5, cx + 7, y0 + 7, dark)                # an arm held out
        im.rect(cx - 3, y0 + 16, cx - 1, y0 + 28, dark)
        im.rect(cx + 1, y0 + 16, cx + 3, y0 + 28, dark)
        im.rect(cx + 3, y0 + 4, cx + 4, y0 + 16, lite)
    im.rect(3, h // 3 + 29, w - 3, h // 3 + 31, dark)
    return im


def amphora(w, h, seed):
    im = Img(w, h, (30, 26, 28))
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - w / 2) / w, (y - h * 0.45) / h)
            im.set(x, y, shade((84, 76, 70), max(0.3, 1.25 - 2.2 * d)))
    clay, cx, cy = (184, 98, 56), w // 2, h // 2 + 2
    for y in range(cy - 14, cy + 16):
        t = (y - (cy - 14)) / 30
        half = int(3 + 9 * math.sin(math.pi * min(1, t * 1.25)) ** 0.8) if t < 0.8 else int(3 + 6 * (1 - t) / 0.2)
        im.rect(cx - half, y, cx + half, y + 1, shade(clay, 1.1 - 0.3 * abs(t - 0.4)))
    im.rect(cx - 3, cy - 22, cx + 3, cy - 14, clay)
    im.rect(cx - 5, cy - 24, cx + 5, cy - 22, shade(clay, 1.15))
    im.rect(cx - 5, cy + 16, cx + 5, cy + 19, shade(clay, 0.8))
    for s in (-1, 1):
        im.rect(cx + s * 7 - (0 if s > 0 else 1), cy - 20, cx + s * 7 + (1 if s > 0 else 0), cy - 8, clay)
        im.rect(min(cx + s * 3, cx + s * 7), cy - 21, max(cx + s * 3, cx + s * 7), cy - 20, clay)
    im.rect(cx - 11, cy - 4, cx + 11, cy + 3, (28, 22, 22))          # a band of figures
    for x in range(cx - 9, cx + 9, 4):
        im.rect(x, cy - 3, x + 2, cy + 2, clay)
    im.rect(cx - 10, cy + 22, cx + 10, cy + 24, (150, 144, 132))     # its shelf
    im.noise(4, seed)
    return im


def mask(w, h, seed):
    im = Img(w, h, (26, 26, 34))
    gold, blue, cx, cy = (214, 174, 74), (40, 70, 130), w // 2, h // 2 - 2
    for y in range(cy - 18, cy + 22):                                # the headcloth
        half = min(w // 2 - 3, 10 + (y - cy + 18) // 3)
        im.rect(cx - half, y, cx + half, y + 1, gold if (y // 3) % 2 else blue)
    for y in range(cy - 13, cy + 16):
        t = (y - (cy - 13)) / 29
        half = int(9 * math.sin(math.pi * (0.25 + 0.6 * t)) ** 0.7) if t < 0.95 else 3
        im.rect(cx - half, y, cx + half, y + 1, shade(gold, 1.1 - 0.25 * t))
    for s in (-1, 1):
        im.rect(cx + s * 5 - 2, cy - 5, cx + s * 5 + 2, cy - 3, (24, 22, 26))
        im.rect(cx + s * 5 - 3, cy - 8, cx + s * 5 + 3, cy - 7, shade(gold, 0.6))
    im.rect(cx, cy - 4, cx + 1, cy + 4, shade(gold, 0.6))
    im.rect(cx - 3, cy + 8, cx + 3, cy + 9, shade(gold, 0.55))
    im.rect(cx - 2, cy + 16, cx + 2, cy + 24, blue)                  # the beard
    im.noise(4, seed)
    return im


def specimens(w, h, seed):
    r = random.Random(seed)
    im = Img(w, h, (234, 226, 198))
    im.noise(3, seed)
    for cy in range(9, h - 4, 13):
        for cx in range(8, w - 4, 12):
            a = r.choice(((40, 90, 150), (200, 120, 30), (150, 40, 40), (60, 60, 60), (120, 150, 60), (230, 230, 220)))
            for i in range(5):
                im.rect(cx - 5 + i // 2, cy - 4 + i, cx - 1, cy - 3 + i, a)
                im.rect(cx + 2, cy - 4 + i, cx + 6 - i // 2, cy - 3 + i, a)
            im.rect(cx - 4, cy + 1, cx - 1, cy + 3, shade(a, 0.75))
            im.rect(cx + 2, cy + 1, cx + 5, cy + 3, shade(a, 0.75))
            im.rect(cx, cy - 5, cx + 1, cy + 4, (30, 26, 22))
            im.rect(cx - 2, cy + 6, cx + 3, cy + 7, (150, 140, 120))
    return im


def ammonite(w, h, seed):
    c = (88, 88, 92)
    im = Img(w, h, c)
    im.noise(8, seed)
    lite, dark = (196, 184, 156), (58, 56, 58)
    for k in range(260):
        t = k / 260 * 5.5 * math.pi
        rad = 1.5 + t * min(w, h) / 44
        x, y = w / 2 + rad * math.cos(t), h / 2 + rad * math.sin(t)
        im.disc(x, y, 1 + rad / 9, lite if (k // 5) % 2 else shade(lite, 0.78))
    for k in range(60):
        t = k / 60 * 5.5 * math.pi
        rad = 0.5 + t * min(w, h) / 44 - 2
        im.set(int(w / 2 + rad * math.cos(t)), int(h / 2 + rad * math.sin(t)), dark)
    return im


def oldmap(w, h, seed):
    r = random.Random(seed)
    sea, land = (206, 196, 156), (176, 164, 112)
    im = Img(w, h, sea)
    for _ in range(9):
        x, y, rad = r.randrange(w), r.randrange(h), r.randrange(4, 11)
        im.disc(x, y, rad + 1, (120, 108, 76))
        im.disc(x, y, rad, r.choice((land, (160, 172, 120), (196, 170, 120))))
    for x in range(8, w, 12):
        for y in range(0, h, 2):
            im.set(x, y, (150, 136, 100))
    for y in range(8, h, 12):
        for x in range(0, w, 2):
            im.set(x, y, (150, 136, 100))
    im.diamond(w - 9, h - 10, 5, (120, 60, 40))
    im.diamond(w - 9, h - 10, 2, sea)
    im.frame(0, 0, w, h, (120, 108, 76), 1)
    im.frame(2, 2, w - 2, h - 2, (120, 108, 76), 1)
    im.noise(5, seed)
    return im


def plan(w, h, seed):
    """The plan of the museum on a board, and where you are."""
    im = Img(w, h, (28, 40, 60))
    line = (226, 226, 214)
    for box in ((w // 2 - 8, 6, w // 2 + 8, 14), (w // 2 - 14, 14, w // 2 + 14, 30), (4, 24, w // 2 - 15, 44),
                (w // 2 + 15, 24, w - 4, 44), (w // 2 - 10, 32, w // 2 + 10, 50)):
        im.frame(box[0], h - box[3], box[2], h - box[1], line, 1)
    im.disc(w // 2, h - 10, 2, (230, 80, 60))
    for y in range(6, h - 52, 4):
        im.rect(8, y, w - 8 - (y * 7) % 13, y + 1, shade(line, 0.7))
    return im


def menu(w, h, seed):
    r = random.Random(seed)
    im = Img(w, h, (30, 38, 34))
    im.noise(4, seed)
    im.rect(w // 2 - 9, 4, w // 2 + 9, 6, (236, 232, 220))
    for y in range(11, h - 4, 5):
        k = r.randrange(w // 3, w - 14)
        im.rect(5, y, 5 + k, y + 1, (206, 204, 196))
        im.rect(w - 9, y, w - 5, y + 1, (220, 190, 110))
    return im


def hang(im, pic, n, cy):
    """Hangs `pic` on the wall `im`, centred at row `cy`, in the look's frame,
    with a label beside it."""
    c = LOOKS[n]
    mount, fr = (3 if c["mount"] else 0), (4 if n == "1" else 3 if n == "2" else 1)
    w, h = pic.w + 2 * (mount + fr), pic.h + 2 * (mount + fr)
    x0, y0 = 32 - w // 2, cy - h // 2
    im.rect(x0 + 2, y0 + 3, x0 + w + 2, y0 + h + 3, shade(im.px[cy * 64 + 2][:3], 0.62))     # its shadow
    im.rect(x0, y0, x0 + w, y0 + h, c["frame"])
    if n == "1":
        im.frame(x0, y0, x0 + w, y0 + h, shade(GILT, 0.6), 1)
        im.frame(x0 + 1, y0 + 1, x0 + w - 1, y0 + h - 1, shade(GILT, 1.2), 1)
        im.frame(x0 + 3, y0 + 3, x0 + w - 3, y0 + h - 3, shade(GILT, 0.7), 1)
    elif n == "2":
        im.frame(x0, y0, x0 + w, y0 + h, shade(c["frame"], 0.6), 1)
        im.rect(x0 + 1, y0 + 1, x0 + w - 1, y0 + 2, shade(c["frame"], 1.5))
    if mount:
        im.rect(x0 + fr, y0 + fr, x0 + w - fr, y0 + h - fr, c["mount"])
    for y in range(pic.h):
        for x in range(pic.w):
            im.set(x0 + fr + mount + x, y0 + fr + mount + y, pic.px[y * pic.w + x][:3])
    im.rect(x0 + w - 9, y0 + h + 6, x0 + w, y0 + h + 11, (236, 232, 220))                     # the label
    im.rect(x0 + w - 8, y0 + h + 8, x0 + w - 2, y0 + h + 9, (120, 116, 108))
    return im


EAST = {"1": (landscape, portrait, still), "2": (landscape, portrait, oldmap), "3": (abstract, abstract, abstract)}
WEST = {"1": (relief, amphora, mask), "2": (specimens, ammonite, mask), "3": (amphora, relief, mask)}
BIG = {"1": (portrait, landscape), "2": (oldmap, ammonite), "3": (abstract, abstract)}


# --- indoors ---------------------------------------------------------------------
def wall(s, h, below=0, seed=0):
    im = th._wall64(s, h, below)
    f0, f1 = th._wall(s, h, below).field
    if s.get("over") == "ashlar":
        ashlar(im, f0 + 2, f1 - 4, s["field"], 5 if s.get("stile") else 0, 59 if s.get("stile") else 64)
    if s["dstyle"] == "none":
        im.rect(0, f1 - 4, 64, h - 8, s["field"])
    im.noise(4, 920 + seed + h)
    im.field = (f0, f1)
    return gy.mirror(im)


def beam(im, n, row):
    """The head of an opening in an indoor wall at `row`."""
    c = LOOKS[n]["hall"]
    im.rect(0, row - 14, 64, row, c["cornice"] if n != "3" else CONC)
    im.rect(0, row - 16, 64, row - 14, shade(c["field"], 0.6))
    im.rect(0, row - 4, 64, row - 3, c["rail"])
    im.rect(0, row - 2, 64, row, shade(c["skirt"], 0.8))
    return im


def decked(im, n):
    """The edge of an upper floor along the top of the wall under it."""
    c = LOOKS[n]["hall"]
    im.rect(0, 0, 64, 12, c["cornice"] if n != "3" else CONC)
    im.rect(0, 0, 64, 1, shade(c["cornice"], 1.1))
    im.rect(0, 9, 64, 10, c["rail"])
    im.rect(0, 12, 64, 15, shade(c["field"], 0.5))
    for y in range(15, 30):
        f = 0.6 + 0.4 * (y - 15) / 15
        for x in range(64):
            p = im.px[y * 64 + x]
            p[:3] = shade(p[:3], f)
    return im


def face(base, s, leaf, wood):
    """A door's face, 256 high: `leaf` in its bottom 96 rows, a 16-row
    architrave, and above it the wall `base` as it runs past, `s` along."""
    T = 128
    im = Img(64, 256)
    for y in range(256):
        for x in range(64):
            im.set(x, y, base.px[((y - (256 - base.h)) % base.h) * 64 + (x + s) % 64][:3])
    for y in range(T + 32, 256):
        for x in range(64):
            im.px[y * 64 + x] = list(leaf.px[y * 64 + x])
    im.rect(0, T + 16, 64, T + 32, wood)
    im.rect(0, T + 16, 64, T + 17, shade(wood, 1.3))
    im.rect(0, T + 30, 64, T + 32, shade(wood, 0.6))
    return im


def flat(n, tag, seed):
    r = random.Random(seed)
    if tag == "F":                                                   # the hall and the lobby
        if n == "1":
            return th.flat("octagon", (226, 220, 204), (40, 38, 42), seed)
        if n == "3":
            return th.flat("terrazzo", (196, 192, 184), (120, 116, 110), seed)
        f = Img(64, 64, (206, 170, 112))                             # encaustic tiles
        for i in range(4):
            for j in range(4):
                x, y = i * 16, j * 16
                if (i + j) % 2:
                    f.rect(x, y, x + 16, y + 16, (150, 72, 50))
                f.diamond(x + 8, y + 8, 5, (36, 34, 38) if (i + j) % 2 else (150, 72, 50))
                f.diamond(x + 8, y + 8, 2, (226, 206, 150))
        f.noise(5, seed)
        return f
    if tag == "P":                                                   # the way through
        if n == "1":                                                 # honey marble, veined
            f = Img(64, 64, (204, 176, 124))
            for _ in range(14):
                x, y = r.randrange(64), r.randrange(64)
                for i in range(r.randrange(8, 26)):
                    f.set((x + i) % 64, (y + i // 2 + (i // 7) % 2) % 64, (232, 214, 172))
            f.noise(5, seed)
            return f
        if n == "2":
            return gy.flat("quarry", seed)
        return th.flat("terrazzo", (92, 90, 90), (150, 146, 140), seed)
    if tag == "FW":                                                  # wings, upper gallery, mezzanine
        if n == "1":                                                 # oak, laid herringbone
            a = (150, 104, 60)
            f = Img(64, 64, a)
            for y in range(64):
                for x in range(64):
                    k = (x + y) // 8 if (x // 16) % 2 == 0 else (x - y) // 8
                    edge_ = (x + y) % 8 == 0 if (x // 16) % 2 == 0 else (x - y) % 8 == 0
                    f.set(x, y, shade(a, 0.62) if edge_ or x % 16 == 0 else shade(a, (0.92, 1.0, 1.08)[k % 3]))
            f.noise(4, seed)
            return f
        a = (86, 54, 34) if n == "2" else (204, 172, 124)
        return th.flat("boards", a, shade(a, 0.66), seed)
    if tag == "FI":                                                  # rooms
        if n == "3":
            return th.flat("carpet", (96, 100, 108), (120, 124, 132), seed)
        a = (126, 88, 52) if n == "1" else (104, 66, 42)
        return th.flat("boards", a, shade(a, 0.62), seed)
    if tag == "FC":                                                  # the cafe
        if n == "2":
            return gy.flat("bluewhite", seed)
        a, b = ((232, 228, 216), (44, 44, 48)) if n == "1" else ((232, 228, 216), (200, 104, 50))
        f = Img(64, 64, a)
        for i in range(4):
            for j in range(4):
                if (i + j) % 2:
                    f.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, b)
        f.noise(4, seed)
        return f
    if tag == "FR":                                                  # the roof
        if n != "3":
            return gy.flat("lead", seed)
        f = Img(64, 64, (120, 118, 112))                             # shingle
        f.noise(22, seed)
        return f
    if tag == "FG":                                                  # the court
        if n == "1":                                                 # a lawn, mown in stripes
            f = Img(64, 64, (62, 104, 52))
            f.rect(0, 0, 32, 64, (70, 114, 58))
            f.noise(10, seed)
            return f
        c = (176, 160, 128) if n == "2" else (208, 204, 196)
        f = Img(64, 64, c)
        f.noise(16, seed)
        if n == "3":                                                 # raked
            for y in range(0, 64, 4):
                f.rect(0, y, 64, y + 1, shade(c, 0.86))
        return f
    if n == "1":                                                     # paving
        return gy.flat("flags", seed)
    if n == "2":
        f = th.brick(64, 64, (150, 84, 62), (100, 56, 42), seed)
        f.noise(7, seed)
        return f
    f = Img(64, 64, (184, 182, 176))
    f.noise(6, seed)
    for i in (0, 32):
        f.rect(i, 0, i + 1, 64, (140, 138, 132))
        f.rect(0, i, 64, i + 1, (140, 138, 132))
    return f


def ceiling(n, tag, seed):
    if tag == "CH":                                                  # the hall: the night through glass
        if n == "3":                                                 # a grid of lit panels
            c = Img(64, 64, (240, 238, 232))
            for x in (4, 36):
                for y in (4, 36):
                    c.rect(x, y, x + 24, y + 24, (255, 248, 226))
                    c.frame(x, y, x + 24, y + 24, (200, 198, 190), 1)
            c.rect(0, 0, 64, 1, STEEL)
            c.rect(0, 0, 1, 64, STEEL)
            c.noise(2, seed)
            return c
        c = Img(64, 64, NIGHT)
        c.noise(4, seed)
        if n == "1":                                                 # a coffer round every pane
            c.frame(0, 0, 64, 64, (222, 214, 192), 8)
            c.frame(8, 8, 56, 56, GILT, 2)
            c.frame(0, 0, 64, 64, shade((222, 214, 192), 0.8), 1)
            for x in (26, 37):
                c.rect(x, 10, x + 1, 54, (70, 76, 90))
                c.rect(10, x, 54, x + 1, (70, 76, 90))
            c.set(18, 20, (230, 230, 240))
            c.set(45, 44, (200, 200, 220))
        else:                                                        # iron ribs
            for x in range(0, 64, 16):
                c.rect(x, 0, x + 1, 64, (70, 84, 76))
            c.rect(0, 0, 64, 5, (30, 56, 46))
            c.rect(0, 5, 64, 6, (10, 20, 16))
            c.rect(0, 0, 5, 64, (30, 56, 46))
            for x in range(8, 64, 16):
                c.disc(x, 2, 1, (110, 140, 120))
            c.set(22, 30, (230, 230, 240))
            c.set(50, 48, (200, 200, 220))
        return c
    if tag == "CG":                                                  # galleries and lobby
        if n == "1":                                                 # a cove round a lit lay light
            c = Img(64, 64, (226, 218, 198))
            c.frame(0, 0, 64, 64, shade((226, 218, 198), 0.86), 2)
            c.rect(16, 16, 48, 48, (255, 246, 216))
            c.frame(14, 14, 50, 50, GILT, 2)
            c.rect(31, 16, 33, 48, (214, 200, 160))
            c.rect(16, 31, 48, 33, (214, 200, 160))
            c.noise(3, seed)
            return c
        if n == "2":
            return gy.ceiling((214, 200, 168), MAHOG, 32, seed)
        c = Img(64, 64, (240, 238, 232))                             # a strip of light
        c.rect(28, 0, 36, 64, (255, 250, 230))
        c.rect(27, 0, 28, 64, (190, 188, 180))
        c.rect(36, 0, 37, 64, (190, 188, 180))
        c.noise(2, seed)
        return c
    if tag == "CP":                                                  # under a porch
        if n == "1":
            return th.ceiling("coffer", (222, 214, 192), shade((222, 214, 192), 0.8), False, seed)
        if n == "2":
            return gy.ceiling((190, 150, 100), (60, 70, 60), 16, seed)
        c = Img(64, 64, CONC)
        c.noise(5, seed)
        for y in range(0, 64, 8):
            c.rect(0, y, 64, y + 1, shade(CONC, 0.9))
        return c
    base = {"1": (228, 222, 204), "2": (224, 212, 180), "3": (240, 238, 232)}[n]
    c = Img(64, 64, base)
    c.frame(0, 0, 64, 64, shade(base, 0.9), 1)
    if n == "3":
        c.rect(32, 0, 33, 64, shade(base, 0.9))
        c.rect(0, 32, 64, 33, shade(base, 0.9))
    c.noise(3, seed)
    return c


def railing(n):
    r = Img(64, 32, (0, 0, 0, 0))
    if n == "1":                                                     # a stone balustrade
        c = (226, 220, 204)
        r.rect(0, 0, 64, 6, c)
        r.rect(0, 0, 64, 1, shade(c, 1.1))
        r.rect(0, 5, 64, 6, shade(c, 0.7))
        r.rect(0, 27, 64, 32, shade(c, 0.9))
        for x in range(0, 64, 16):
            r.rect(x + 6, 6, x + 10, 27, c)
            r.rect(x + 4, 13, x + 12, 22, c)
            r.rect(x + 5, 11, x + 11, 13, shade(c, 0.9))
            r.rect(x + 4, 20, x + 12, 22, shade(c, 0.75))
    elif n == "2":
        return gy.railing("brick")
    else:                                                            # glass under a steel rail
        r.rect(0, 4, 64, 30, (190, 214, 226, 70))
        r.rect(0, 0, 64, 4, (150, 156, 164))
        r.rect(0, 0, 64, 1, (214, 218, 224))
        r.rect(0, 30, 64, 32, (60, 62, 66))
        for x in range(0, 64, 16):
            r.rect(x, 4, x + 2, 30, (90, 94, 100))
    return r


def case(n, top):
    """A display case: glass over a plinth 40 high. Repeats every 16."""
    c = LOOKS[n]
    if top:                                                          # what lies in it, seen from above
        f = Img(64, 64, c["felt"])
        f.noise(4, 930 + int(n))
        dark = sum(c["felt"]) < 300
        for i in range(4):
            for j in range(4):
                x, y = i * 16 + 8, j * 16 + 8
                if (i + j) % 2:
                    f.disc(x, y, 3, (214, 178, 80))
                    f.disc(x, y, 1, (150, 116, 44))
                else:
                    f.rect(x - 4, y - 2, x + 3, y + 3, (176, 96, 60) if (i // 2 + j) % 2 else (150, 150, 140))
                    f.rect(x - 4, y - 2, x - 1, y, c["felt"])
        for k in range(-64, 64, 32):                                 # light on the glass
            for i in range(64):
                for d in (0, 1, 6):
                    x = k + i + d
                    if 0 <= x < 64:
                        p = f.px[i * 64 + x]
                        p[:3] = mix(p[:3], (255, 255, 255), 0.22 if dark else 0.5)
        return f
    im = Img(64, 64, c["plinth"])
    im.noise(4, 934 + int(n))
    g = (40, 52, 60)
    im.rect(0, 0, 64, 15, g)
    for x in range(0, 64, 16):
        im.rect(x, 0, x + 1, 15, c["frame"])
        for i in range(10):
            im.set(x + 4 + i // 2, 12 - i, shade(g, 1.9))
    im.rect(0, 0, 64, 2, c["frame"])
    im.rect(0, 13, 64, 16, c["frame"])
    im.rect(0, 16, 64, 17, shade(c["plinth"], 0.5))
    for x in range(0, 64, 16):
        im.rect(x, 17, x + 1, 64, shade(c["plinth"], 0.8))
    im.rect(0, 36, 64, 64, shade(c["plinth"], 0.7))
    return im


def make(out, rd):
    """`rd` is the plain room door (leaf in its bottom 96 rows)."""
    def both(name, im):
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    def tex(name, im):
        out[f"textures/{name}.png"] = im.png()
        return im

    T = 128
    steel = Img(64, 256)                                             # a bolted door's leaf (as AJBOLT)
    steel.px = [list(p) for p in rd.px]
    sc = (132, 138, 148)
    steel.rect(0, T + 32, 64, T + 128, sc)
    steel.frame(0, T + 32, 64, T + 128, shade(sc, 0.5), 3)
    for y in (T + 44, T + 78, T + 112):
        steel.rect(3, y, 61, y + 3, shade(sc, 0.7))
        for x in (8, 32, 56):
            steel.disc(x, y + 1, 2, (200, 204, 210))
    steel.noise(5, 78)

    # --- the same in every look ------------------------------------------------
    same = {}
    cel = th.brick(64, 128, (176, 172, 160), (120, 116, 108), 940)   # the cellar: limewashed brick
    cel.noise(6, 941)
    gy.grime(cel, 70, 128, 0.62)
    cel.rect(0, 0, 64, 5, (60, 56, 52))
    same["XC"] = cel
    boil = th.brick(64, 128, (92, 66, 56), (50, 40, 38), 942)        # the boiler room: pipes along sooty brick
    boil.noise(6, 943)
    gy.grime(boil, 0, 128, 0.7)
    for y, c, t in ((18, (168, 104, 60), 9), (40, (120, 124, 132), 5), (96, (120, 124, 132), 7)):
        boil.rect(0, y, 64, y + t, c)
        boil.rect(0, y + 1, 64, y + 2, shade(c, 1.4))
        boil.rect(0, y + t - 2, 64, y + t, shade(c, 0.55))
        for x in range(6, 64, 16):
            boil.rect(x, y - 1, x + 3, y + t + 1, shade(c, 0.7))
    same["XB"] = boil
    grot = Img(64, 128, (84, 96, 90))                                # the grotto: rockwork and shells
    gy.rubble(grot, 0, 128, (92, 104, 96), 944)
    r = random.Random(945)
    for _ in range(26):
        x, y = r.randrange(2, 31), r.randrange(4, 124)
        grot.disc(x, y, r.choice((1, 2, 2)), r.choice(((226, 214, 196), (214, 180, 170), (190, 200, 190))))
    for _ in range(90):
        grot.set(r.randrange(32), r.randrange(128), (70, 110, 70))
    grot.noise(5, 946)
    gy.grime(grot, 60, 128, 0.7)
    same["XG"] = grot
    shed = Img(64, 128, (86, 70, 52))                                # the shed: boards, and tools on a rail
    shed.noise(7, 947)
    for x in range(0, 64, 8):
        shed.rect(x, 0, x + 1, 128, (40, 32, 24))
        shed.rect(x + 1, 0, x + 2, 128, (110, 92, 70))
    shed.rect(0, 34, 64, 38, (120, 100, 74))
    shed.rect(0, 38, 64, 39, (40, 32, 24))
    for x in range(0, 64, 16):
        iron = (150, 152, 158)
        shed.rect(x + 4, 38, x + 5, 76, (150, 120, 80))              # a spade
        shed.rect(x + 2, 76, x + 7, 86, iron)
        shed.rect(x + 11, 38, x + 12, 70, (150, 120, 80))            # a fork
        for dx in (9, 11, 13):
            shed.rect(x + dx, 70, x + dx + 1, 82, iron)
        shed.rect(x + 9, 70, x + 14, 71, iron)
    same["XS"] = shed
    stock = Img(64, 128, (60, 52, 44))                               # the stockroom: shelves of boxes
    r = random.Random(948)
    for y in range(0, 128, 28):
        x = 1
        while x < 31:
            w = r.choice((6, 8, 10))
            hh = r.choice((14, 18, 22))
            c = r.choice(((176, 150, 110), (150, 126, 90), (196, 180, 150), (120, 130, 140)))
            stock.rect(x, y + 24 - hh, min(32, x + w), y + 24, c)
            stock.rect(x, y + 24 - hh, min(32, x + w), y + 25 - hh, shade(c, 1.2))
            stock.rect(x + 2, y + 30 - hh, min(31, x + w - 2), y + 33 - hh, (236, 232, 220))
            x += w + 1
        stock.rect(0, y + 24, 64, y + 28, (130, 104, 72))
        stock.rect(0, y + 27, 64, y + 28, (30, 26, 22))
    stock.noise(4, 949)
    same["XK"] = stock
    for tag, im in same.items():
        both("AJ6" + tag, gy.mirror(im))
    stone = Img(64, 64, (190, 184, 168))                             # steps, the fountain's rim, garden seats
    stone.noise(7, 950)
    stone.rect(0, 0, 64, 3, (214, 208, 192))
    stone.rect(0, 3, 64, 4, (130, 124, 112))
    both("AJ6XP", stone)
    cloth = Img(64, 64, (238, 236, 228))                             # a table laid for supper
    cloth.noise(3, 951)
    for i in range(0, 64, 16):
        cloth.rect(i, 0, i + 1, 64, (214, 212, 204))
        cloth.rect(0, i, 64, i + 1, (214, 212, 204))
        for j in range(0, 64, 16):
            cloth.disc(i + 8, j + 8, 4, (226, 226, 232))
            cloth.disc(i + 8, j + 8, 2, (246, 246, 250))
    out["flats/AJ6XT.png"] = cloth.png()
    skirt = Img(64, 64, (236, 234, 226))
    skirt.noise(3, 952)
    for x in range(0, 64, 8):
        skirt.rect(x, 2, x + 1, 64, (206, 204, 196))
    skirt.rect(0, 26, 64, 28, (190, 60, 50))
    skirt.rect(0, 30, 64, 64, (60, 44, 32))
    out["textures/AJ6XT.png"] = skirt.png()
    files = Img(64, 128, (70, 50, 34))                               # the archive's shelves: box files
    r = random.Random(953)
    for y in range(0, 128, 24):
        for x in range(0, 16, 4):
            c = r.choice(((96, 104, 84), (120, 60, 50), (60, 70, 96), (150, 130, 90), (80, 80, 84)))
            for k in range(0, 64, 16):
                files.rect(k + x, y + 2, k + x + 3, y + 21, c)
                files.rect(k + x, y + 6, k + x + 3, y + 10, (226, 220, 200))
        files.rect(0, y + 21, 64, y + 24, (130, 100, 66))
        files.rect(0, y + 23, 64, y + 24, (30, 22, 16))
    files.noise(4, 954)
    out["textures/AJ6XA.png"] = files.png()

    # --- the three looks ---------------------------------------------------------
    for n, c in LOOKS.items():
        k = int(n)

        def name(tag, pic=""):
            return f"AJ6{tag}{n}{pic}"

        # outdoors
        for tag, win in (("", 0), ("A", 1), ("B", 2)):
            tex(name("Y" + tag), front(n, win))
            tex(name("YC" + tag), front(n, win, 456))
            tex(name("YT" + tag), front(n, win, 384))
        yu = gy.crop(_base(n), 0, 288)
        yu.rect(0, 274, 64, 288, shade(yu.px[200 * 64 + 8][:3], 0.6))
        yu.rect(0, 274, 64, 275, shade(yu.px[200 * 64 + 8][:3], 1.1))
        tex(name("YU"), yu)
        yr = copy(yu)
        lintel(yr, n, 160)
        tex(name("YR"), gy.mirror(yr))
        tex(name("YG"), gallery_side(n))
        tex(name("YS"), roof_side(n))
        tex(name("YE"), edge(gy.crop(_base(n), 512, 640), n, 8))

        # the hall and what opens off it
        hall = wall(c["hall"], 384, seed=k)
        tex(name("H"), hall)
        for i, painter in enumerate(BIG[n]):
            tex(name("H", i + 1), hang(copy(hall), painter(42, 104, 960 + 10 * k + i), n, 214))
        tex(name("HK"), beam(copy(hall), n, 256))
        tex(name("HL"), beam(copy(hall), n, 192))
        tex(name("HV"), decked(gy.crop(hall, 192, 384), n))
        tex(name("HG"), decked(gy.crop(hall, 224, 384), n))
        hm = gy.crop(hall, 0, 192)
        hm.rect(0, 184, 64, 192, c["hall"]["skirt"])
        hm.rect(0, 184, 64, 185, shade(c["hall"]["skirt"], 1.5))
        tex(name("HM"), hm)
        walls = {}
        walls["L"] = tex(name("L"), wall(c["hall"], 192, seed=k + 3))
        tex(name("L", 1), hang(copy(walls["L"]), plan(42, 58, 0), n, 88))
        walls["A"] = tex(name("A"), wall(c["low"], 128, seed=k))
        tex(name("S"), wall(c["low"], 128, below=128, seed=k))
        walls["U"] = tex(name("U"), wall(c["upper"], 176, seed=k))
        for i, painter in enumerate(EAST[n][:2]):
            tex(name("U", i + 1), hang(copy(walls["U"]), painter(42, 50, 970 + 10 * k + i), n,
                                       sum(walls["U"].field) // 2 - 4))
        for tag, part, painters in (("WA", "wa", WEST[n]), ("WB", "wb", WEST[n]), ("EA", "ea", EAST[n]),
                                    ("EB", "eb", EAST[n])):
            walls[tag] = tex(name(tag), wall(c[part], 160, seed=k + ord(tag[0]) + ord(tag[1])))
            for i, painter in enumerate(painters):
                pic = painter(42, 46, 980 + 10 * k + i + (5 if tag[1] == "B" else 0))
                tex(name(tag, i + 1), hang(copy(walls[tag]), pic, n, sum(walls[tag].field) // 2 - 5))
        for tag, part in (("K", "cloak"), ("M", "shop"), ("C", "cafe"), ("O", "office"), ("R", "archive")):
            walls[tag] = tex(name(tag), wall(c[part], 128, seed=k + ord(tag)))
        tex(name("C", 1), hang(copy(walls["C"]), menu(36, 40, 990 + k), n, 44))
        walls.update(same)

        # doors
        for letter, (tag, s, keys) in FACES.items():
            d = face(walls[tag], s, rd, c["wood"])
            tex(f"AJ6D{n}{letter}", th.locked(d, keys) if keys else d)
        for letter, (tag, s) in BOLTS.items():
            tex(f"AJ6Z{n}{letter}", face(walls[tag], s, steel, (70, 74, 82)))

        # what stands in the rooms
        tex(name("RL"), railing(n))
        tex(name("V"), case(n, False))
        out[f"flats/{name('VT')}.png"] = case(n, True).png()
        wd = Img(64, 64, c["wood"])
        wd.noise(5, 955 + k)
        for x in range(0, 64, 8):
            wd.rect(x, 0, x + 1, 64, shade(c["wood"], 0.7))
        wd.rect(0, 0, 64, 3, shade(c["wood"], 1.25))
        wd.rect(0, 3, 64, 4, shade(c["wood"], 0.5))
        both(name("WD"), wd)
        bn = Img(64, 64, c["bench"])
        bn.noise(5, 958 + k)
        if n == "2":                                                 # slats
            for y in range(0, 64, 8):
                bn.rect(0, y, 64, y + 1, shade(c["bench"], 0.5))
                bn.rect(0, y + 1, 64, y + 2, shade(c["bench"], 1.3))
        else:                                                        # buttoned leather
            for x in range(0, 64, 16):
                for y in range(0, 64, 16):
                    bn.disc(x + 8, y + 8, 1, shade(c["bench"], 0.5))
                    bn.set(x + 7, y + 7, shade(c["bench"], 1.8))
            bn.rect(0, 0, 64, 2, shade(c["bench"], 1.4))
        both(name("BN"), bn)

        # floors and ceilings
        for i, tag in enumerate(("F", "P", "FW", "FI", "FC", "FR", "FG", "FT")):
            out[f"flats/{name(tag)}.png"] = flat(n, tag, 1000 + 10 * k + i).png()
        for i, tag in enumerate(("CH", "CG", "CL", "CP")):
            out[f"flats/{name(tag)}.png"] = ceiling(n, tag, 1040 + 10 * k + i).png()
