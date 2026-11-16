"""Candidate looks for MAP07, the observatory (see AJAR_OBSERVATORY in map_hinges7.py).

Three looks for the whole observatory, numbered 1 to 3. For look n (name = AJ7 + tag + n):
  Y    the building's front, 640: rows count down from the sky's edge at 512.
       0..352 the upper floor and what is over it, 352..512 the ground floor,
       512..640 below ground (the ravine). YA, YB with windows (lit; dark)
  YU   the wall round the roof, 352     YS  the roof's edge from below, 160
  YD   the dome from the roof, 352
  G    the wall round the grounds, 640: trees over a garden wall
  H    hall, 256 (H<n>1 a portrait, H<n>2 a chart)        A  porches, 128
  S    the cellar steps: a porch wall with 128 rows of lining under it
  L    library, 320: two tiers of books. LS the stacks' own wall (160),
       LV the stacks' front (160), LB a bookcase standing free (128)
  D    dome, 448: the shell, the ring it turns on, the wall. DV the gallery's
       front (160), DP the telescope's pier (256)
  WK workshop, WI instrument room, WC clock room, EL lecture room, EO orrery,
  T  transit house (all 160; each with <n>1, <n>2: tools, charts, clocks, a
     blackboard, a diagram)
  EP the planetarium, 176: a town's roofs against the sky that is thrown on its
     dome. ES the band of that sky between the dome's steps (64); DS the same
     for the dome of the telescope (64, the top of D)
  RL railing   V the side of an instrument case, VT its top
  WD tables and desks, BN benches (wall and flat)
  flats: F hall floor, P the way through it, FL library, FD dome, FW wings,
         FI the transit house, FR roof, FS a lit skylight, FT paving, FO the
         drive, FA the gallery's and the stacks' floor; CH hall ceiling, CL
         library, CD the dome's shell, CW rooms, CP porches; FE the
         planetarium's carpet, CS the sky on its dome
The same in all three: AJ7XN the wood round the hill (640), AJ7XR rock (the
ravine's banks, wall and flat), AJ7XL the lens store, AJ7XA the armoury. Where
the hill is open: AJ7XT the tops of the wood below (256 by 128, see-through),
AJ7XK the wood from above (flat), AJ7XH the country beyond (128). AJ7SKY is
the level's sky (1024 by 256). The
cellar, boiler house, cave and shed wear the museum's (AJ6XC, XB, XG, XS), and
stone is the museum's AJ6XP.

A door's face is made for its own place in its wall: AJ7D<n><number> for a room
door, AJ7Z<n><number> for a bolted one. The map says which it needs and names
them (FACES in map_hinges7.py), so only the look being built gets its doors.

Every wall is 64 wide and the same mirrored, and the map lines them up by world
position (Map.align). What stands free in a room repeats every 16.
"""
import math
import random

from gfx import Img, shade, BRASS
import gfx_theatre as th
import gfx_yard as gy
import gfx_museum as mu
from gfx_museum import st, mix
from gfx_station import arch, copy

NAMES = {"1": "Royal", "2": "Mountain", "3": "Star Palace"}

IVORY, GILT, INK = (236, 230, 212), (204, 168, 84), (38, 36, 40)
BRICK, PORT, SAGE, OAK, MAHOG = (128, 68, 52), (212, 204, 184), (150, 164, 140), (120, 84, 50), (98, 48, 32)
GRANITE, LIME, PINE, IRON, VERD = (118, 120, 126), (222, 222, 212), (176, 136, 84), (84, 100, 96), (96, 140, 124)
CONC, BRONZE, MIDN, TRAV, WALNUT = (212, 202, 178), (156, 112, 60), (28, 36, 76), (206, 190, 160), (84, 54, 38)
NIGHT, GLASS, LAMP = (16, 20, 38), (26, 32, 50), (240, 200, 118)

LOOKS = {
    # a royal observatory of the 1770s: brick and Portland stone, sashes, oak, brass, green baize
    "1": dict(
        hall=st((226, 220, 198), "panel", (196, 188, 162), SAGE, "panel", (236, 230, 212), (70, 60, 50), IVORY,
                frieze=SAGE, fz="swag"),
        low=st((226, 220, 198), "plain", (226, 220, 198), SAGE, "panel", IVORY, (70, 60, 50), IVORY),
        dome=st((226, 220, 198), "panel", (196, 188, 162), OAK, "panel", BRASS, (60, 40, 26), IVORY),
        wk=st((206, 196, 168), "plaster", (188, 178, 150), OAK, "boards", (70, 46, 28), (50, 34, 22), IVORY),
        wi=st((60, 92, 76), "plain", (60, 92, 76), OAK, "panel", BRASS, (50, 34, 22), IVORY, frieze=IVORY, fz="stencil"),
        wc=st((120, 40, 44), "stripe", (106, 32, 36), OAK, "panel", BRASS, (50, 34, 22), IVORY, frieze=IVORY, fz="stencil"),
        el=st((204, 190, 150), "plain", (204, 190, 150), OAK, "boards", (70, 46, 28), (50, 34, 22), IVORY),
        eo=st((52, 66, 100), "damask", (68, 84, 120), OAK, "panel", BRASS, (50, 34, 22), IVORY, frieze=IVORY, fz="swag"),
        tr=st((214, 206, 180), "plaster", (196, 188, 160), SAGE, "boards", IVORY, (60, 50, 40), IVORY),
        wood=OAK, case=MAHOG, felt=(32, 70, 50), bench=(40, 74, 54), books=((110, 44, 36), (60, 76, 52), (150, 116, 60), (70, 50, 40)),
        ink=(40, 30, 20), paper=(226, 212, 176)),
    # a mountain station of the 1890s: granite, riveted iron, limewash, pine
    "2": dict(
        hall=st(LIME, "plaster", (200, 200, 190), PINE, "boards", (120, 90, 54), (60, 46, 32), (190, 190, 180)),
        low=st((204, 204, 194), "plaster", (186, 186, 176), PINE, "boards", (120, 90, 54), (60, 46, 32), (190, 190, 180)),
        dome=st(LIME, "plaster", (200, 200, 190), IRON, "concrete", (56, 68, 64), (40, 48, 46), IRON),
        wk=st((150, 112, 70), "slats", (110, 80, 48), PINE, "boards", (90, 66, 40), (60, 46, 32), (120, 90, 54)),
        wi=st(LIME, "plaster", (200, 200, 190), (64, 96, 110), "boards", (40, 62, 74), (34, 44, 50), (190, 190, 180)),
        wc=st(LIME, "tile", (196, 196, 186), (120, 50, 42), "boards", (80, 32, 28), (50, 26, 22), (190, 190, 180)),
        el=st((176, 136, 84), "slats", (140, 104, 62), PINE, "boards", (110, 80, 48), (60, 46, 32), (120, 90, 54)),
        eo=st(LIME, "plaster", (200, 200, 190), IRON, "boards", (56, 68, 64), (40, 48, 46), (190, 190, 180)),
        tr=st((170, 130, 80), "slats", (130, 96, 58), PINE, "boards", (110, 80, 48), (60, 46, 32), (120, 90, 54)),
        wood=PINE, case=IRON, felt=(60, 64, 70), bench=(130, 96, 58), books=((90, 84, 70), (60, 70, 80), (120, 104, 76), (70, 60, 50)),
        ink=(30, 40, 60), paper=(214, 214, 200)),
    # a planetarium of the 1930s: pale concrete, bronze, midnight blue and gold, travertine
    "3": dict(
        hall=st(MIDN, "plain", MIDN, TRAV, "marble", BRONZE, (60, 44, 30), (226, 214, 184), frieze=(18, 24, 54),
                fz="stencil", stile=TRAV, bead=BRONZE),
        low=st(TRAV, "block", (182, 166, 136), TRAV, "marble", BRONZE, (60, 44, 30), (226, 214, 184)),
        dome=st(MIDN, "plain", MIDN, TRAV, "marble", BRONZE, (60, 44, 30), BRONZE, stile=(18, 24, 54), bead=BRONZE),
        wk=st((196, 190, 172), "tile", (172, 166, 150), (70, 100, 96), "concrete", (40, 60, 58), (30, 40, 40), (226, 214, 184)),
        wi=st((34, 70, 74), "plain", (34, 70, 74), WALNUT, "panel", BRONZE, (40, 26, 18), (226, 214, 184),
              frieze=(20, 44, 48), fz="stencil"),
        wc=st((110, 44, 40), "plain", (110, 44, 40), WALNUT, "panel", BRONZE, (40, 26, 18), (226, 214, 184),
              frieze=(70, 24, 24), fz="stencil"),
        el=st(WALNUT, "panel", (120, 80, 54), WALNUT, "boards", BRONZE, (40, 26, 18), (226, 214, 184)),
        eo=st(MIDN, "plain", MIDN, WALNUT, "panel", BRONZE, (40, 26, 18), (226, 214, 184), frieze=(18, 24, 54),
              fz="stencil"),
        tr=st((226, 214, 184), "stripe", (206, 192, 160), TRAV, "marble", BRONZE, (60, 44, 30), (226, 214, 184)),
        wood=WALNUT, case=(60, 40, 30), felt=(24, 30, 62), bench=(110, 40, 40), books=((30, 44, 90), (110, 44, 40), (170, 140, 80), (40, 40, 46)),
        ink=(226, 214, 160), paper=(22, 28, 60)),
}

ROOMS = {"WK": "wk", "WI": "wi", "WC": "wc", "EL": "el", "EO": "eo", "T": "tr"}
ALIGNED = ("Y", "YA", "YB", "YU", "YS", "YD", "G", "H", "A", "S", "L", "LS", "LV", "D", "DV", "DS", "EP", "ES") + tuple(ROOMS)
PICTURES = dict({t: 2 for t in ROOMS}, H=2)
SAME = ("AJ7XN", "AJ7XL", "AJ7XA", "AJ7XH", "AJ6XC", "AJ6XB", "AJ6XG", "AJ6XS")


def aligned(n):
    return ({f"AJ7{t}{n}" for t in ALIGNED} | {f"AJ7{t}{n}{i + 1}" for t, k in PICTURES.items() for i in range(k)}
            | set(SAME))


def darken(im, y0, y1, f0, f1):
    """Shades rows y0..y1 from factor f0 at y0 to f1 at y1."""
    for y in range(y0, y1):
        f = f0 + (f1 - f0) * (y - y0) / max(1, y1 - y0 - 1)
        for x in range(im.w):
            p = im.px[y * im.w + x]
            p[:3] = shade(p[:3], f)


def stars(im, y0, y1, seed, n=10, c=(226, 214, 160)):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.randrange(3, 30), r.randrange(y0 + 2, y1 - 2)
        im.set(x, y, c)
        if r.random() < 0.3:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                im.set(x + dx, y + dy, shade(c, 0.6))


# --- outdoors ------------------------------------------------------------------
def firs(im, y0, y1, seed):
    """A wood at night over rows y0..y1: trunks below, tops against a paler haze."""
    r = random.Random(seed)
    for y in range(y0, y1):
        f = (y - y0) / (y1 - y0)
        im.rect(0, y, 64, y + 1, mix((52, 62, 96), (16, 24, 26), min(1, f * 1.6)))
    for k in range(9):
        cx, top = r.randrange(0, 33), y0 + r.randrange(0, 150) + (0 if k % 3 else 40)
        c = shade((22, 44, 34), r.choice((0.6, 0.9, 1.2)))
        w = 0.0
        for y in range(top, y1):
            w = min(15, w + r.choice((0.0, 0.18, 0.3)))
            jag = int(w) - (y % 7) // 2
            im.rect(max(0, cx - jag), y, min(64, cx + jag + 1), y + 1, c)
    for x in (6, 19, 28):
        im.rect(x, y1 - 90, x + 2, y1, (44, 36, 28))
    gy.mirror(im, y0, y1)


def rock(h, seed):
    im = Img(64, h, (70, 70, 72))
    gy.rubble(im, 0, h, (74, 74, 76), seed)
    r = random.Random(seed + 1)
    for _ in range(h // 2):
        im.set(r.randrange(32), r.randrange(h), (50, 74, 50))
    im.noise(6, seed + 2)
    return gy.mirror(im)


_fronts = {}


def _base(n):
    """The front without windows."""
    if n in _fronts:
        return _fronts[n]
    if n == "1":                                                     # brick, dressed in Portland stone
        im = th.brick(64, 640, BRICK, shade(BRICK, 0.62), 1101)
        im.rect(0, 0, 64, 10, shade(PORT, 1.05))                     # coping
        im.rect(0, 10, 64, 12, shade(PORT, 0.6))
        for x in range(4, 64, 8):                                    # a balustrade, blind
            im.rect(x, 14, x + 3, 40, shade(PORT, 0.86))
        im.rect(0, 40, 64, 56, PORT)                                 # cornice
        im.rect(0, 52, 64, 56, shade(PORT, 0.6))
        for x in range(2, 64, 6):
            im.rect(x, 46, x + 3, 50, shade(PORT, 0.74))
        im.rect(0, 344, 64, 352, PORT)                               # the band between the floors
        im.rect(0, 350, 64, 352, shade(PORT, 0.6))
        im.rect(0, 56, 3, 344, shade(BRICK, 1.12))                   # a pier on every 64, quoined below
        for y in range(356, 488, 24):
            w = 7 if (y // 24) % 2 else 4
            im.rect(0, y, w, y + 23, PORT)
            im.rect(0, y + 22, w, y + 23, shade(PORT, 0.7))
        im.rect(0, 488, 64, 512, PORT)                               # plinth
        im.rect(0, 488, 64, 490, shade(PORT, 1.1))
        gy.paste(im, th.brick(64, 128, shade(BRICK, 0.6), shade(BRICK, 0.36), 1102), 512)
        im.noise(5, 1103)
        gy.grime(im, 440, 512, 0.86)
    elif n == "2":                                                   # granite, as it came out of the hill
        im = Img(64, 640, GRANITE)
        gy.rubble(im, 0, 640, GRANITE, 1104)
        im.rect(0, 0, 64, 8, shade(GRANITE, 0.5))                    # the eaves: iron, and their shadow
        im.rect(0, 8, 64, 10, VERD)
        darken(im, 10, 40, 0.55, 1.0)
        im.rect(0, 344, 64, 352, shade(GRANITE, 1.2))                # a dressed course
        im.rect(0, 350, 64, 352, shade(GRANITE, 0.5))
        for y in range(470, 512):                                    # battered foot
            for x in range(64):
                p = im.px[y * 64 + x]
                p[:3] = shade(p[:3], 0.82)
        darken(im, 512, 640, 0.75, 0.5)
        im.noise(6, 1105)
        gy.grime(im, 300, 344, 0.9)
    else:                                                            # smooth concrete, fluted, with bronze
        im = Img(64, 640, CONC)
        for x in range(64):                                          # a fluted pier on every 64
            d = min(x, 63 - x)
            if d < 10:
                im.rect(x, 40, x + 1, 496, shade(CONC, 0.8 + 0.2 * abs((d % 5) - 2) / 2))
        im.rect(0, 0, 64, 6, BRONZE)                                 # the parapet steps back
        im.rect(0, 6, 64, 24, shade(CONC, 1.06))
        im.rect(0, 24, 64, 26, shade(CONC, 0.6))
        for x in range(0, 64, 8):                                    # a band of chevrons
            for i in range(4):
                im.set(x + i, 36 - i, BRONZE)
                im.set(x + 7 - i, 36 - i, BRONZE)
        im.rect(0, 40, 64, 42, shade(CONC, 0.6))
        im.rect(0, 346, 64, 352, BRONZE)
        im.rect(0, 346, 64, 347, shade(BRONZE, 1.4))
        im.rect(0, 496, 64, 512, (60, 56, 60))                       # a base of dark granite
        im.rect(0, 496, 64, 497, (120, 116, 120))
        for y in range(512, 640, 8):
            im.rect(0, y, 64, y + 8, shade(CONC, 0.62 if (y // 8) % 2 else 0.56))
        im.noise(4, 1106)
        gy.grime(im, 430, 496, 0.9)
    _fronts[n] = gy.mirror(im)
    return _fronts[n]


def window(im, n, top, bottom, lit):
    """A window in the middle of a 64-wide front, its head at row `top`."""
    glass = LAMP if lit else GLASS
    if n == "1":                                                     # a sash, twelve panes, a stone head
        im.rect(18, top - 8, 46, top, PORT)
        im.rect(30, top - 12, 34, top, shade(PORT, 1.08))
        im.rect(18, top, 46, bottom, IVORY)
        im.rect(20, top + 2, 44, bottom - 2, glass)
        for x in (27, 36):
            im.rect(x, top + 2, x + 1, bottom - 2, IVORY)
        for k in range(1, 4):
            y = top + (bottom - top) * k // 4
            im.rect(20, y, 44, y + (2 if k == 2 else 1), IVORY)
        im.rect(16, bottom, 48, bottom + 4, PORT)
        im.rect(16, bottom + 3, 48, bottom + 4, shade(PORT, 0.6))
    elif n == "2":                                                   # small and deep, with a shutter folded back
        top, bottom = top + 12, bottom - 12
        im.rect(20, top - 8, 44, top, shade(GRANITE, 1.25))
        im.rect(22, top, 42, bottom, shade(GRANITE, 0.4))
        im.rect(24, top + 3, 42, bottom, glass)
        im.rect(32, top + 3, 33, bottom, IRON)
        im.rect(24, (top + bottom) // 2, 42, (top + bottom) // 2 + 1, IRON)
        im.rect(12, top, 21, bottom, VERD)
        for y in range(top + 3, bottom, 5):
            im.rect(13, y, 20, y + 1, shade(VERD, 0.6))
        im.rect(20, bottom, 44, bottom + 4, shade(GRANITE, 1.25))
    else:                                                            # tall and narrow, behind a bronze grille
        top, bottom = top - 16, bottom + 8
        im.rect(22, top, 42, bottom, shade(CONC, 0.5))
        im.rect(24, top + 2, 40, bottom - 2, glass)
        for y in range(top + 2, bottom - 2, 12):
            im.rect(24, y, 40, y + 1, BRONZE)
            im.diamond(32, y + 6, 4, BRONZE)
            im.diamond(32, y + 6, 2, glass)
        im.rect(31, top + 2, 33, bottom - 2, BRONZE)
        im.rect(20, bottom, 44, bottom + 3, BRONZE)
    return im


def front(n, win=0):
    im = copy(_base(n))
    if win:
        window(im, n, 216, 304, win == 1)
        window(im, n, 392, 464, False)
        gy.mirror(im)
    return im


def garden_wall(n):
    """Trees over the wall round the grounds: the wall is the front's ground floor."""
    im = Img(64, 640)
    firs(im, 0, 380, 1110 + int(n))
    base = _base(n)
    for y in range(368, 640):
        im.px[y * 64:(y + 1) * 64] = [list(p) for p in base.px[y * 64:(y + 1) * 64]]
    cop = {"1": PORT, "2": shade(GRANITE, 1.25), "3": BRONZE}[n]
    im.rect(0, 360, 64, 368, cop)
    im.rect(0, 360, 64, 361, shade(cop, 1.2))
    im.rect(0, 367, 64, 368, shade(cop, 0.5))
    if n == "1":                                                     # no quoins on a garden wall's piers above the coping
        im.rect(0, 352, 7, 360, PORT)
        im.disc(3, 349, 3, PORT)
    return gy.mirror(im)


def dome_out(n):
    """The dome from the roof, 352: its shell over the drum."""
    c = {"1": (112, 150, 132), "2": IRON, "3": (150, 130, 80)}[n]   # copper gone green; iron; bronze
    im = Img(64, 352, c)
    for y in range(0, 200):                                          # plates, closer together as it curves away
        f = y / 200
        im.rect(0, y, 64, y + 1, shade(c, 0.45 + 0.6 * f))
    y, k = 200, 0
    while y > 0:
        step = max(6, int(30 * (y / 200)))
        im.rect(0, y, 64, y + 1, shade(c, 0.4))
        for x in ((0, 32) if k % 2 else (16, 48)):
            im.rect(x, max(0, y - step), x + 1, y, shade(c, 0.4))
        if n == "2":
            for x in range(4, 64, 8):
                im.set(x, y - 2, shade(c, 1.3))
        y -= step
        k += 1
    im.rect(0, 200, 64, 212, shade(c, 0.5))                          # the ring it turns on
    for x in range(4, 64, 16):
        im.disc(x, 206, 3, BRASS if n != "2" else (150, 156, 160))
    base = _base(n)
    for y in range(212, 352):
        im.px[y * 64:(y + 1) * 64] = [list(p) for p in base.px[(y + 160) * 64:(y + 161) * 64]]
    im.rect(0, 212, 64, 220, {"1": PORT, "2": shade(GRANITE, 1.25), "3": BRONZE}[n])
    im.rect(0, 219, 64, 220, (40, 40, 40))
    return gy.mirror(im)


# --- books ----------------------------------------------------------------------
def shelves(im, y0, y1, c, seed, step=24):
    """Shelves of books over rows y0..y1, in a case of wood c['wood']."""
    r = random.Random(seed)
    wood = c["wood"]
    im.rect(0, y0, 64, y1, shade(wood, 0.35))
    y = y0
    while y + 12 <= y1:
        y2 = min(y1, y + step)
        x = 3
        while x < 32:
            w = r.choice((2, 3, 3, 4))
            hh = min(y2 - y - 4, r.choice((15, 17, 18, 19)))
            col = shade(r.choice(c["books"]), r.choice((0.8, 1.0, 1.15)))
            if r.random() < 0.08:
                x += w
                continue
            im.rect(x, y2 - 3 - hh, min(32, x + w), y2 - 3, col)
            im.rect(x, y2 - 3 - hh, x + 1, y2 - 3, shade(col, 0.7))
            if w > 2:
                im.rect(x + 1, y2 - hh + 1, x + w - 1, y2 - hh + 2, GILT if sum(col) < 330 else INK)
            x += w
        im.rect(0, y2 - 3, 64, y2, wood)
        im.rect(0, y2 - 1, 64, y2, shade(wood, 0.5))
        y = y2
    im.rect(0, y0, 3, y1, wood)                                      # an upright on every 64
    im.rect(3, y0, 4, y1, shade(wood, 0.5))


def library(n):
    c = LOOKS[n]
    wood = c["wood"]
    im = Img(64, 320, wood)
    im.rect(0, 0, 64, 12, c["hall"]["cornice"])
    im.rect(0, 10, 64, 12, shade(wood, 0.5))
    shelves(im, 12, 150, c, 1120 + int(n), 23)
    im.rect(0, 150, 64, 160, wood)                                   # the stacks' floor runs round as a rail
    im.rect(0, 150, 64, 151, shade(wood, 1.3))
    im.rect(0, 158, 64, 160, shade(wood, 0.45))
    shelves(im, 160, 280, c, 1124 + int(n), 24)
    im.rect(0, 280, 64, 320, wood)                                   # cupboards under them
    im.frame(6, 285, 30, 314, shade(wood, 0.66), 2)
    im.disc(27, 300, 1, BRASS)
    im.rect(0, 280, 64, 282, shade(wood, 1.3))
    im.rect(0, 314, 64, 320, shade(wood, 0.45))
    im.noise(4, 1128 + int(n))
    return gy.mirror(im)


# --- the dome inside ---------------------------------------------------------------
def dome_in(n):
    """448: the shell (176), the ring it turns on (16), the wall (256)."""
    c = LOOKS[n]
    im = Img(64, 448)
    w = mu.wall(c["dome"], 256, seed=30 + int(n))
    for y in range(256):
        im.px[(192 + y) * 64:(193 + y) * 64] = [list(p) for p in w.px[y * 64:(y + 1) * 64]]
    if n == "1":                                                     # cream boards between oak ribs
        im.rect(0, 0, 64, 176, (214, 206, 180))
        for x in range(0, 64, 8):
            im.rect(x, 0, x + 1, 176, (180, 170, 144))
        for y in range(40, 176, 44):
            im.rect(0, y, 64, y + 3, OAK)
        im.rect(0, 0, 5, 176, OAK)
        im.rect(5, 0, 6, 176, shade(OAK, 0.5))
    elif n == "2":                                                   # riveted iron
        im.rect(0, 0, 64, 176, IRON)
        for k, y in enumerate(range(0, 176, 44)):
            im.rect(0, y, 64, y + 2, shade(IRON, 0.5))
            for x in range(4, 64, 8):
                im.set(x, y + 5, shade(IRON, 1.5))
            for x in ((0, 32) if k % 2 else (16, 48)):
                im.rect(x, y, x + 2, y + 44, shade(IRON, 0.5))
                for yy in range(y + 6, y + 44, 8):
                    im.set(x + 4, yy, shade(IRON, 1.5))
        gy.grime(im, 120, 176, 0.8)
    else:                                                            # the sky painted on it, between bronze ribs
        im.rect(0, 0, 64, 176, (18, 24, 60))
        stars(im, 0, 176, 1133, 26)
        for a, b in (((8, 30), (20, 60)), ((20, 60), (12, 100)), ((12, 100), (26, 130))):
            for i in range(20):
                im.set(a[0] + (b[0] - a[0]) * i // 20, a[1] + (b[1] - a[1]) * i // 20, (90, 100, 150))
        im.rect(0, 0, 3, 176, BRONZE)
    darken(im, 0, 176, 0.5, 1.0)
    ring = {"1": BRASS, "2": (60, 70, 68), "3": BRONZE}[n]
    im.rect(0, 176, 64, 192, shade(ring, 0.6))
    im.rect(0, 176, 64, 178, shade(ring, 1.2))
    im.rect(0, 190, 64, 192, (20, 20, 20))
    for x in range(8, 64, 16):
        im.disc(x, 184, 3, ring)
        im.disc(x, 184, 1, (30, 30, 30))
    edge = c["dome"]["rail"]                                         # where the gallery meets the wall
    im.rect(0, 280, 64, 288, c["dome"]["skirt"])
    im.rect(0, 280, 64, 281, edge)
    return gy.mirror(im)


def gallery_front(n):
    """What carries the dome's gallery, 160: cupboards for charts and eyepieces."""
    c = LOOKS[n]
    wood = c["case"] if n != "2" else IRON
    im = Img(64, 160, wood)
    im.rect(0, 0, 64, 10, c["dome"]["rail"])
    im.rect(0, 0, 64, 1, shade(c["dome"]["rail"], 1.3))
    im.rect(0, 10, 64, 13, (20, 20, 20))
    if n == "2":                                                     # iron brackets and plate
        for x in (0, 32):
            for i in range(20):
                im.rect(x, 13 + i, x + 20 - i, 14 + i, shade(IRON, 0.6))
            im.rect(x, 13, x + 2, 160, shade(IRON, 0.5))
        for y in range(40, 160, 40):
            im.rect(0, y, 64, y + 1, shade(IRON, 0.5))
            for x in range(4, 64, 8):
                im.set(x, y + 3, shade(IRON, 1.5))
    else:
        for y in range(18, 150, 22):                                 # drawers, with a pull each
            for x in (2, 33):
                im.frame(x, y, x + 29, y + 20, shade(wood, 0.6), 1)
                im.rect(x + 1, y + 1, x + 28, y + 2, shade(wood, 1.3))
                im.rect(x + 11, y + 9, x + 18, y + 11, BRASS if n == "1" else BRONZE)
    im.rect(0, 152, 64, 160, shade(wood, 0.5))
    im.noise(4, 1140 + int(n))
    darken(im, 13, 30, 0.6, 1.0)
    return gy.mirror(im)


def pier(n):
    """The telescope's pier, 256."""
    c = {"1": PORT, "2": shade(GRANITE, 1.1), "3": (60, 56, 60)}[n]
    im = Img(64, 256, c)
    mu.ashlar(im, 0, 256, c, step=32)
    im.rect(0, 0, 64, 14, {"1": BRASS, "2": IRON, "3": BRONZE}[n])  # the mount's bed plate
    im.rect(0, 14, 64, 16, (20, 20, 20))
    for x in range(8, 64, 16):
        im.disc(x, 7, 2, (40, 40, 40))
    im.rect(20, 120, 44, 150, BRASS if n != "2" else (200, 200, 196))     # a plate: who gave it, and when
    im.frame(20, 120, 44, 150, shade(BRASS, 0.5), 1)
    for y in range(126, 146, 5):
        im.rect(24, y, 40, y + 1, (60, 50, 30))
    im.noise(5, 1144 + int(n))
    return gy.mirror(im)


# --- what hangs on the walls -----------------------------------------------------
def chart(w, h, n, seed):
    """A star chart."""
    c, r = LOOKS[n], random.Random(seed)
    p = Img(w, h, c["paper"])
    p.noise(4, seed)
    cx, cy, rad = w // 2, h // 2, min(w, h) // 2 - 3
    for a in range(0, 360, 3):
        p.set(int(cx + rad * math.cos(math.radians(a))), int(cy + rad * math.sin(math.radians(a))), c["ink"])
    for a in range(0, 360, 4):
        p.set(int(cx + rad * 0.55 * math.cos(math.radians(a))) + 2, int(cy + rad * 0.55 * math.sin(math.radians(a))), shade(c["ink"], 0.8))
    p.rect(cx, cy - rad, cx + 1, cy + rad, mix(c["paper"], c["ink"], 0.4))
    p.rect(cx - rad, cy, cx + rad, cy + 1, mix(c["paper"], c["ink"], 0.4))
    for _ in range(18):
        a, d = r.random() * 6.28, r.random() * (rad - 2)
        p.set(int(cx + d * math.cos(a)), int(cy + d * math.sin(a)), c["ink"] if n != "3" else (255, 240, 180))
    return p


def clock(w, h, n, seed):
    """A regulator: a dial over a long case with a pendulum behind glass."""
    c = LOOKS[n]
    wood = c["case"] if n != "2" else PINE
    p = Img(w, h, wood)
    cx = w // 2
    p.disc(cx, 13, 11, shade(wood, 0.6))
    p.disc(cx, 13, 9, (236, 232, 214))
    for a in range(0, 360, 30):
        p.set(int(cx + 8 * math.cos(math.radians(a))), int(13 + 8 * math.sin(math.radians(a))), INK)
    hand = (seed * 7) % 12
    for i in range(7):
        p.set(int(cx + i * math.cos(hand * 0.52)), int(13 + i * math.sin(hand * 0.52)), INK)
    for i in range(5):
        p.set(cx, 13 - i, INK)
    p.rect(cx - 6, 28, cx + 7, h - 3, (30, 30, 34))
    p.rect(cx, 28, cx + 1, h - 12, BRASS)
    p.disc(cx + (seed % 3) - 1, h - 10, 3, BRASS)
    p.frame(cx - 6, 28, cx + 7, h - 3, shade(wood, 0.5), 1)
    return p


def blackboard(w, h, n, seed):
    """A blackboard: an orbit, and somebody's sums."""
    r = random.Random(seed)
    p = Img(w, h, (36, 50, 44) if n != "3" else (30, 30, 34))
    chalk = (226, 226, 214)
    cx, cy = w // 3, h // 2
    for a in range(0, 360, 5):
        p.set(int(cx + 10 * math.cos(math.radians(a))), int(cy + 6 * math.sin(math.radians(a))), chalk)
    p.disc(cx - 5, cy, 1, (240, 220, 120))
    p.set(cx + 10, cy, chalk)
    for y in range(6, h - 6, 6):
        x = w * 2 // 3 - 4
        while x < w - 4:
            ww = r.randrange(2, 6)
            p.rect(x, y, min(w - 3, x + ww), y + 1, shade(chalk, r.choice((0.6, 0.8, 1.0))))
            x += ww + 2
    p.rect(0, h - 3, w, h, (150, 116, 70))
    return p


def tools(w, h, n, seed):
    """A board of tools, each on its painted shadow."""
    p = Img(w, h, shade(LOOKS[n]["wood"], 1.2))
    for x in range(0, w, 6):
        p.rect(x, 0, x + 1, h, shade(LOOKS[n]["wood"], 0.9))
    iron, grip = (160, 164, 170), (120, 60, 40)
    for i, x in enumerate(range(5, w - 5, 9)):
        y = 6 + (i % 2) * 4
        if i % 3 == 0:                                               # a hammer
            p.rect(x - 3, y, x + 4, y + 4, iron)
            p.rect(x, y + 4, x + 1, y + 26, grip)
        elif i % 3 == 1:                                             # a file
            p.rect(x, y, x + 2, y + 20, iron)
            p.rect(x - 1, y + 20, x + 3, y + 28, grip)
        else:                                                        # callipers
            for k in range(22):
                p.set(x - k // 6, y + k, iron)
                p.set(x + 1 + k // 6, y + k, iron)
            p.disc(x, y, 2, BRASS)
    for x in range(8, w - 6, 12):                                    # lenses on a shelf
        p.disc(x, h - 9, 4, (150, 180, 190))
        p.disc(x - 1, h - 10, 2, (210, 230, 236))
    p.rect(0, h - 4, w, h, shade(LOOKS[n]["wood"], 0.6))
    return p


def portrait(w, h, n, seed):
    """Somebody who looked through the telescope, in a wig or a stiff collar."""
    p = mu.portrait(w, h, seed)
    return p


def diagram(w, h, n, seed):
    """The solar system as an engraving: the sun, rings, a few planets."""
    c = LOOKS[n]
    p = Img(w, h, c["paper"])
    p.noise(4, seed)
    cx, cy = w // 2, h // 2
    for k, rad in enumerate((5, 9, 13, 18)):
        for a in range(0, 360, 4):
            p.set(int(cx + rad * math.cos(math.radians(a))), int(cy + rad * 0.8 * math.sin(math.radians(a))),
                  mix(c["paper"], c["ink"], 0.6))
        a = seed * 1.7 + k * 2.1
        p.disc(int(cx + rad * math.cos(a)), int(cy + rad * 0.8 * math.sin(a)), 1 + (k == 2),
               ((150, 110, 70), (90, 120, 170), (190, 150, 90), (150, 90, 70))[k])
    p.disc(cx, cy, 2, (236, 190, 80))
    return p


def hang(im, pic, n, cy, frame=None):
    """Hangs `pic` on the wall `im`, centred at row `cy`, in a plain frame."""
    c = LOOKS[n]
    fr = frame or (GILT if n == "1" else (60, 50, 40) if n == "2" else BRONZE)
    w, h = pic.w + 4, pic.h + 4
    x0, y0 = 32 - w // 2, cy - h // 2
    im.rect(x0 + 2, y0 + 3, x0 + w + 2, y0 + h + 3, shade(im.px[cy * 64 + 2][:3], 0.62))
    im.rect(x0, y0, x0 + w, y0 + h, fr)
    im.frame(x0, y0, x0 + w, y0 + h, shade(fr, 0.6), 1)
    for y in range(pic.h):
        for x in range(pic.w):
            im.set(x0 + 2 + x, y0 + 2 + y, pic.px[y * pic.w + x][:3])
    return im


PICS = {"H": (portrait, chart), "WK": (tools, tools), "WI": (chart, diagram), "WC": (clock, clock),
        "EL": (blackboard, diagram), "EO": (diagram, chart), "T": (chart, clock)}
SIZES = {portrait: (40, 52), chart: (44, 44), tools: (48, 44), clock: (26, 62), blackboard: (52, 40), diagram: (44, 38)}


# --- floors, ceilings, furniture ----------------------------------------------------
def flat(n, tag, seed):
    r = random.Random(seed)
    if tag == "F":                                                   # the hall
        if n == "1":
            return th.flat("octagon", (226, 220, 204), (40, 38, 42), seed)
        if n == "2":
            return gy.flat("flags", seed)
        f = th.flat("terrazzo", (196, 184, 160), (120, 104, 80), seed)     # a compass star in every square
        for cx, cy in ((16, 16), (48, 48)):
            f.diamond(cx, cy, 9, BRONZE)
            f.diamond(cx, cy, 6, MIDN)
            f.diamond(cx, cy, 2, GILT)
        return f
    if tag == "P":                                                   # the way through
        if n == "1":
            return gy.flat("baize", seed)
        if n == "2":
            return gy.flat("rush", seed)
        return th.flat("carpet", (30, 38, 80), (160, 120, 60), seed)
    if tag in ("FL", "FW", "FI"):
        a = {"1": (126, 88, 52), "2": (170, 132, 84), "3": (90, 60, 42)}[n]
        if tag == "FW" and n == "3":
            return th.flat("terrazzo", (150, 146, 140), (96, 92, 88), seed)
        if tag == "FI" and n == "2":
            return gy.flat("quarry", seed)
        return th.flat("boards", shade(a, 1.0 if tag == "FL" else 0.9), shade(a, 0.62), seed)
    if tag == "FD":                                                  # the dome
        if n == "1":
            return gy.flat("slabs", seed)
        if n == "2":
            f = Img(64, 64, (96, 98, 102))                           # chequer plate
            for i in range(0, 64, 8):
                for j in range(0, 64, 8):
                    f.rect(i + 1, j + 3, i + 6, j + 4, (128, 130, 136)) if (i + j) % 16 else f.rect(i + 3, j + 1, i + 4, j + 6, (128, 130, 136))
            f.noise(5, seed)
            return f
        f = th.flat("terrazzo", (40, 44, 70), (150, 130, 90), seed)
        f.frame(0, 0, 64, 64, BRONZE, 1)
        return f
    if tag == "FA":                                                  # galleries: boards, or a grating
        if n == "2":
            f = Img(64, 64, (30, 34, 34))
            for i in range(0, 64, 8):
                f.rect(i, 0, i + 2, 64, IRON)
                f.rect(0, i, 64, i + 1, shade(IRON, 0.7))
            return f
        a = (140, 100, 60) if n == "1" else (70, 46, 34)
        return th.flat("boards", a, shade(a, 0.6), seed)
    if tag == "FR":
        if n == "3":
            f = Img(64, 64, (120, 112, 100))
            f.noise(18, seed)
            return f
        return gy.flat("lead", seed)
    if tag == "FS":                                                  # a skylight, lit from below
        f = Img(64, 64, (236, 214, 150))
        f.noise(6, seed)
        bar = {"1": (226, 222, 206), "2": (50, 60, 58), "3": BRONZE}[n]
        for i in range(0, 64, 16):
            f.rect(i, 0, i + 2, 64, bar)
            f.rect(0, i, 64, i + 2, bar)
        return f
    if tag == "FT":                                                  # paving: the yard and the lane
        return gy.flat({"1": "flags", "2": "cobbles", "3": "slabs"}[n], seed)
    if n == "1":                                                     # the drive: gravel; setts; concrete in bays
        f = Img(64, 64, (176, 160, 128))
        f.noise(18, seed)
        return f
    if n == "2":
        return gy.flat("setts", seed)
    f = Img(64, 64, (150, 146, 136))
    f.noise(6, seed)
    f.rect(0, 0, 64, 1, (110, 106, 98))
    f.rect(0, 0, 1, 64, (110, 106, 98))
    return f


def ceiling(n, tag, seed):
    c = LOOKS[n]
    if tag == "CD":                                                  # the dome's shell overhead
        if n == "1":
            f = gy.ceiling((200, 192, 166), OAK, 32, seed)
        elif n == "2":
            f = Img(64, 64, shade(IRON, 0.7))
            for i in (0, 32):
                f.rect(i, 0, i + 2, 64, shade(IRON, 0.4))
                f.rect(0, i, 64, i + 2, shade(IRON, 0.4))
            for i in range(4, 64, 8):
                for j in (4, 36):
                    f.set(i, j, shade(IRON, 1.3))
                    f.set(j, i, shade(IRON, 1.3))
            f.noise(4, seed)
        else:
            f = Img(64, 64, (14, 18, 50))
            st_ = Img(32, 64, (14, 18, 50))
            stars(st_, 0, 64, seed, 14)
            for y in range(64):
                for x in range(64):
                    f.px[y * 64 + x] = list(st_.px[y * 32 + x % 32]) if x < 32 else list(st_.px[((y + 29) % 64) * 32 + (63 - x)])
            f.rect(0, 0, 64, 1, BRONZE)
        return f
    if tag == "CP":
        if n == "1":
            return th.ceiling("coffer", (222, 214, 192), shade((222, 214, 192), 0.8), False, seed)
        if n == "2":
            return gy.ceiling((150, 116, 72), (90, 66, 40), 16, seed)
        f = Img(64, 64, (206, 196, 172))
        f.frame(0, 0, 64, 64, BRONZE, 1)
        f.frame(6, 6, 58, 58, shade((206, 196, 172), 0.86), 2)
        f.noise(3, seed)
        return f
    if tag in ("CH", "CL"):
        if n == "1":
            f = Img(64, 64, (228, 222, 204))
            f.frame(0, 0, 64, 64, shade((228, 222, 204), 0.86), 2)
            f.disc(32, 32, 14, shade((228, 222, 204), 0.9))
            f.disc(32, 32, 11, (228, 222, 204))
            f.disc(32, 32, 3, GILT)
            f.noise(3, seed)
            return f
        if n == "2":
            return gy.ceiling((196, 196, 186) if tag == "CH" else (170, 132, 84), (110, 80, 48), 32, seed)
        f = Img(64, 64, (22, 28, 64) if tag == "CH" else (226, 214, 184))
        if tag == "CH":
            f.diamond(32, 32, 12, GILT)
            f.diamond(32, 32, 9, (22, 28, 64))
            f.diamond(32, 32, 3, (255, 240, 190))
        f.frame(0, 0, 64, 64, BRONZE, 2)
        f.noise(3, seed)
        return f
    base = {"1": (228, 222, 204), "2": (200, 200, 190), "3": (226, 214, 184)}[n]
    f = Img(64, 64, base)
    f.frame(0, 0, 64, 64, shade(base, 0.9), 1)
    if n == "2":
        for x in range(0, 64, 8):
            f.rect(x, 0, x + 1, 64, shade(base, 0.9))
    f.noise(3, seed)
    return f


def railing(n):
    r = Img(64, 32, (0, 0, 0, 0))
    if n == "1":                                                     # brass rail on turned oak
        r.rect(0, 0, 64, 3, BRASS)
        r.rect(0, 0, 64, 1, shade(BRASS, 1.2))
        r.rect(0, 29, 64, 32, OAK)
        for x in range(0, 64, 8):
            r.rect(x + 3, 3, x + 5, 29, OAK)
            r.rect(x + 2, 12, x + 6, 18, shade(OAK, 1.15))
    elif n == "2":                                                   # iron pipe
        for y in (0, 14):
            r.rect(0, y, 64, y + 3, (120, 128, 126))
            r.rect(0, y, 64, y + 1, (170, 178, 176))
        r.rect(0, 30, 64, 32, (50, 56, 54))
        for x in range(0, 64, 16):
            r.rect(x, 0, x + 3, 32, (96, 104, 102))
    else:                                                            # bronze, a sunburst in every bay
        r.rect(0, 0, 64, 3, BRONZE)
        r.rect(0, 0, 64, 1, shade(BRONZE, 1.4))
        r.rect(0, 29, 64, 32, shade(BRONZE, 0.7))
        for x in range(0, 64, 16):
            r.rect(x, 3, x + 2, 29, BRONZE)
            for a in range(-60, 61, 30):
                for i in range(4, 22):
                    r.set(int(x + 9 + i * math.sin(math.radians(a)) * 0.33), 29 - i, shade(BRONZE, 1.1))
            r.disc(x + 9, 28, 3, GILT)
    return r


def case(n, top):
    """An instrument under glass on a stand 40 high. Repeats every 16."""
    c = LOOKS[n]
    if top:
        f = Img(64, 64, c["felt"])
        f.noise(4, 1150 + int(n))
        for i in range(4):
            for j in range(4):
                x, y = i * 16 + 8, j * 16 + 8
                if (i + j) % 2:                                      # a brass circle, divided
                    f.disc(x, y, 5, BRASS)
                    f.disc(x, y, 3, c["felt"])
                    f.rect(x - 5, y, x + 6, y + 1, shade(BRASS, 0.7))
                else:                                                # a small telescope
                    f.rect(x - 6, y - 1, x + 5, y + 2, BRASS)
                    f.rect(x + 3, y - 2, x + 6, y + 3, shade(BRASS, 0.7))
        for k in range(-64, 64, 32):                                 # light on the glass
            for i in range(64):
                for d in (0, 1, 6):
                    x = k + i + d
                    if 0 <= x < 64:
                        p = f.px[i * 64 + x]
                        p[:3] = mix(p[:3], (255, 255, 255), 0.25)
        return f
    wood = c["case"]
    im = Img(64, 64, wood)
    im.noise(4, 1154 + int(n))
    g = (40, 52, 60)
    edge = BRASS if n == "1" else (150, 156, 160) if n == "2" else BRONZE
    im.rect(0, 0, 64, 15, g)
    for x in range(0, 64, 16):
        im.rect(x, 0, x + 1, 15, edge)
        for i in range(10):
            im.set(x + 4 + i // 2, 12 - i, shade(g, 1.9))
    im.rect(0, 0, 64, 2, edge)
    im.rect(0, 13, 64, 16, edge)
    im.rect(0, 16, 64, 17, shade(wood, 0.5))
    for x in range(0, 64, 16):
        im.rect(x, 17, x + 1, 64, shade(wood, 0.75))
    im.rect(0, 36, 64, 64, shade(wood, 0.7))
    return im

# --- the planetarium ------------------------------------------------------------
SKYLOW, SKYHIGH = (58, 60, 104), (12, 16, 44)


def planetarium(n):
    """176: the roofs of a town, black against the sky the projector throws."""
    c = LOOKS[n]
    im = Img(64, 176)
    for y in range(128):
        f = y / 128
        im.rect(0, y, 64, y + 1, mix(SKYHIGH, SKYLOW, f * f))
    stars(im, 10, 104, 1190, 16)
    roofs, r = (8, 10, 20), random.Random(1191)
    x = 0
    while x < 22:                                                    # roofs and chimneys
        w, h = r.choice((3, 4, 5, 6)), r.choice((5, 8, 10, 13, 18))
        im.rect(x, 128 - h, min(22, x + w), 128, roofs)
        if w > 3 and r.random() < 0.6:
            im.set(x + 1, 128 - h + 3, LAMP)
        x += w
    for dx in range(11):                                             # and, in the middle of every 64, a dome
        im.rect(31 - dx, 128 - 12 - int(math.sqrt(121 - dx * dx)), 32 - dx, 128, roofs)
    im.rect(31, 96, 32, 106, roofs)
    wood = c["wood"]
    im.rect(0, 128, 64, 176, wood)
    im.noise(3, 1192)
    im.rect(0, 128, 64, 131, BRONZE)
    im.rect(0, 131, 64, 132, shade(wood, 0.4))
    im.frame(4, 138, 30, 168, shade(wood, 0.66), 2)
    im.rect(0, 170, 64, 176, shade(wood, 0.5))
    im.rect(0, 0, 64, 6, shade(BRONZE, 0.7))
    im.rect(0, 6, 64, 7, (6, 8, 20))
    return gy.mirror(im)


def starband():
    """64: the thrown sky, where the dome steps up."""
    im = Img(64, 64, SKYHIGH)
    stars(im, 2, 60, 1193, 9)
    im.rect(0, 62, 64, 64, shade(BRONZE, 0.6))
    return gy.mirror(im)


def starflat(seed, base=(10, 13, 38), n=16):
    f, half = Img(64, 64, base), Img(32, 64, base)
    stars(half, 0, 64, seed, n)
    for y in range(64):
        for x in range(64):
            f.px[y * 64 + x] = list(half.px[y * 32 + x % 32]) if x < 32 else list(half.px[((y + 29) % 64) * 32 + (63 - x)])
    return f


# --- where the hill is open -----------------------------------------------------
def treetops():
    """256 by 128, see-through: the tops of the wood below the hill."""
    im = Img(256, 128, (0, 0, 0, 0))
    r = random.Random(1194)
    for k in range(26):
        far = k < 12
        cx, top = r.randrange(256), r.randrange(52, 100) if far else r.randrange(6, 84)
        c = shade((30, 44, 52) if far else (16, 32, 26), r.choice((0.8, 1.0, 1.2)))
        w = 0.0
        for y in range(top, 128):
            w = min(17, w + r.choice((0.0, 0.2, 0.34)))
            jag = int(w) - (y % 7) // 2
            for x in range(cx - jag, cx + jag + 1):
                im.set(x % 256, y, c)
    for x in range(256):                                             # nothing shows between their feet
        for y in range(112 + (x * 7 % 5), 128):
            im.set(x, y, (12, 24, 20))
    return im


def canopy():
    f = Img(64, 64, (12, 24, 20))
    r = random.Random(1195)
    for _ in range(60):
        f.disc(r.randrange(64), r.randrange(64), r.choice((2, 3, 4)), shade((16, 32, 26), r.choice((0.7, 1.0, 1.25))))
    f.noise(4, 1196)
    return f


def country():
    """128: what lies beyond and below the wood, under the haze of the horizon."""
    im = Img(64, 128)
    for y in range(128):
        im.rect(0, y, 64, y + 1, mix((50, 58, 96), (10, 14, 24), min(1, y / 30)))
    r = random.Random(1197)
    for _ in range(7):                                               # a village's lights, a long way off
        im.set(r.randrange(3, 30), r.randrange(9, 26), shade(LAMP, r.choice((0.5, 0.7, 0.9))))
    im.noise(2, 1198)
    return gy.mirror(im)


def night_sky():
    """1024 by 256: once round. Stars, the Milky Way slanting across, a moon."""
    w, h = 1024, 256
    top, low = (4, 6, 18), (36, 42, 76)
    rows = [mix(top, low, (y / (h - 1)) ** 2.2) for y in range(h)]
    im = Img(w, h)
    for y in range(h):
        row = list(rows[y]) + [255]
        im.px[y * w:(y + 1) * w] = [list(row) for _ in range(w)]
    r = random.Random(1199)
    def star(x, y, b):
        c = tuple(min(255, int(v + (255 - v) * b)) for v in rows[y])
        im.set(x % w, y, c)
        if b > 0.85:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= y + dy < h:
                    im.set((x + dx) % w, y + dy, mix(rows[y + dy], c, 0.4))
    for _ in range(900):
        y = int(r.random() ** 1.3 * 236)
        star(r.randrange(w), y, r.choice((0.25, 0.35, 0.5, 0.7, 0.9, 1.0)) * (1 - 0.5 * y / h))
    for _ in range(1500):                                            # the Milky Way
        x = r.randrange(w)
        y = int(20 + 190 * abs(((x / w) * 2) % 2 - 1) + r.gauss(0, 14))
        if 0 <= y < 232:
            star(x, y, r.choice((0.12, 0.18, 0.25, 0.4)))
    mx, my = 690, 70                                                 # a moon, some days old
    for y in range(my - 16, my + 17):
        for x in range(mx - 16, mx + 17):
            d = math.hypot(x - mx, y - my)
            if d <= 14 and math.hypot(x - mx - 7, y - my + 3) > 13.5:
                im.set(x, y, (236, 232, 208))
            elif d <= 17:
                p = im.px[y * w + x]
                p[:3] = mix(p[:3], (120, 124, 150), 0.12)
    return im


def make(out, rd, faces={}):
    """`rd` is the plain room door (leaf in its bottom 96 rows). `faces` is the
    door faces the map needs: {(look, kind "D" or "Z", wall tag, shift, keys): texture}."""
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
    wood = Img(64, 640)
    firs(wood, 0, 512, 1160)
    gy.paste(wood, rock(128, 1161), 512)
    darken(wood, 512, 640, 0.8, 0.5)
    same["XN"] = tex("AJ7XN", gy.mirror(wood))
    both("AJ7XR", rock(128, 1162))
    lens = Img(64, 128, (70, 56, 44))                                # the lens store: glass on felted shelves
    r = random.Random(1163)
    for y in range(0, 128, 26):
        lens.rect(0, y, 64, y + 22, (36, 40, 50))
        for x in range(6, 32, 9):
            rad = r.choice((3, 4, 4))
            lens.disc(x, y + 21 - rad, rad, (130, 160, 172))
            lens.disc(x - 1, y + 20 - rad, rad - 2, (200, 224, 230))
        lens.rect(0, y + 22, 64, y + 26, (140, 110, 76))
        lens.rect(0, y + 25, 64, y + 26, (30, 24, 18))
    lens.noise(4, 1164)
    same["XL"] = tex("AJ7XL", gy.mirror(lens))
    arm = Img(64, 128, (60, 64, 70))                                 # the armoury: a rack along a steel wall
    arm.noise(5, 1165)
    for x in range(0, 64, 16):
        arm.rect(x, 0, x + 1, 128, (36, 40, 46))
    arm.rect(0, 40, 64, 46, (110, 84, 56))
    arm.rect(0, 100, 64, 106, (110, 84, 56))
    for x in range(5, 32, 9):
        arm.rect(x, 24, x + 2, 100, (30, 30, 34))
        arm.rect(x - 1, 70, x + 3, 104, (96, 62, 38))
    same["XA"] = tex("AJ7XA", gy.mirror(arm))
    tex("AJ7XT", treetops())
    out["flats/AJ7XK.png"] = canopy().png()
    tex("AJ7XH", country())
    tex("AJ7SKY", night_sky())

    # --- the three looks ---------------------------------------------------------
    for n, c in LOOKS.items():
        k = int(n)

        def name(tag, pic=""):
            return f"AJ7{tag}{n}{pic}"

        # outdoors
        for tag, win in (("", 0), ("A", 1), ("B", 2)):
            tex(name("Y" + tag), front(n, win))
        base = _base(n)
        yu = gy.crop(base, 0, 352)
        tone = yu.px[200 * 64 + 20][:3]
        yu.rect(0, 340, 64, 352, shade(tone, 0.6))
        yu.rect(0, 340, 64, 341, shade(tone, 1.1))
        tex(name("YU"), yu)
        tex(name("YS"), gy.crop(base, 352, 512))
        tex(name("YD"), dome_out(n))
        tex(name("G"), garden_wall(n))

        # indoors
        walls = {}
        walls["H"] = tex(name("H"), mu.wall(c["hall"], 256, seed=k))
        walls["A"] = tex(name("A"), mu.wall(c["low"], 128, seed=k))
        tex(name("S"), mu.wall(c["low"], 128, below=128, seed=k))
        walls["L"] = tex(name("L"), library(n))
        walls["LS"] = tex(name("LS"), gy.crop(walls["L"], 0, 160))
        lv = gy.crop(walls["L"], 160, 320)
        lv.rect(0, 0, 64, 8, c["wood"])
        lv.rect(0, 0, 64, 1, shade(c["wood"], 1.3))
        lv.rect(0, 8, 64, 10, (20, 20, 20))
        tex(name("LV"), lv)
        tex(name("LB"), gy.crop(walls["L"], 160, 288))
        walls["D"] = tex(name("D"), dome_in(n))
        tex(name("DS"), gy.crop(walls["D"], 0, 64))
        walls["EP"] = tex(name("EP"), planetarium(n))
        tex(name("ES"), starband())
        tex(name("DV"), gallery_front(n))
        tex(name("DP"), pier(n))
        for tag, part in ROOMS.items():
            walls[tag] = tex(name(tag), mu.wall(c[part], 160, seed=k + sum(map(ord, tag))))
        for tag, painters in PICS.items():
            for i, painter in enumerate(painters):
                w, h = SIZES[painter]
                cy = sum(walls[tag].field) // 2 + (2 if tag != "H" else 10)
                h = min(h, walls[tag].field[1] - walls[tag].field[0] - 14)
                tex(name(tag, i + 1), hang(copy(walls[tag]), painter(w, h, n, 1170 + 10 * k + i + len(tag)), n, cy))
        walls.update(same)
        for tag in ("XC", "XB", "XG", "XS"):                         # the museum's, made before these
            walls[tag] = mu.WALLS[tag]

        # doors
        for (look, kind, tag, s, keys), texture in faces.items():
            if look != n:
                continue
            d = mu.face(walls[tag], s, rd if kind == "D" else steel, c["wood"] if kind == "D" else (70, 74, 82))
            tex(texture, th.locked(d, keys) if keys else d)

        # what stands in the rooms
        tex(name("RL"), railing(n))
        tex(name("V"), case(n, False))
        out[f"flats/{name('VT')}.png"] = case(n, True).png()
        wd = Img(64, 64, c["wood"])
        wd.noise(5, 1180 + k)
        for x in range(0, 64, 8):
            wd.rect(x, 0, x + 1, 64, shade(c["wood"], 0.7))
        wd.rect(0, 0, 64, 3, shade(c["wood"], 1.25))
        wd.rect(0, 3, 64, 4, shade(c["wood"], 0.5))
        both(name("WD"), wd)
        bn = Img(64, 64, c["bench"])
        bn.noise(5, 1184 + k)
        if n == "2":                                                 # slats
            for y in range(0, 64, 8):
                bn.rect(0, y, 64, y + 1, shade(c["bench"], 0.5))
                bn.rect(0, y + 1, 64, y + 2, shade(c["bench"], 1.3))
        else:                                                        # buttoned leather
            for x in range(0, 64, 16):
                for y in range(0, 64, 16):
                    bn.disc(x + 8, y + 8, 1, shade(c["bench"], 0.5))
            bn.rect(0, 0, 64, 2, shade(c["bench"], 1.4))
        both(name("BN"), bn)

        # floors and ceilings
        for i, tag in enumerate(("F", "P", "FL", "FD", "FW", "FI", "FA", "FR", "FS", "FT", "FO")):
            out[f"flats/{name(tag)}.png"] = flat(n, tag, 1200 + 20 * k + i).png()
        out[f"textures/{name('FS')}.png"] = out[f"flats/{name('FS')}.png"]       # a skylight's sides are glass too
        for i, tag in enumerate(("CH", "CL", "CD", "CW", "CP")):
            out[f"flats/{name(tag)}.png"] = ceiling(n, tag, 1260 + 10 * k + i).png()
        out[f"flats/{name('FE')}.png"] = th.flat("carpet", (22, 26, 56), (120, 96, 50), 1290 + k).png()
        out[f"flats/{name('CS')}.png"] = starflat(1294).png()
