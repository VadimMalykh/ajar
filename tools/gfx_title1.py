"""Title look 1, "The Cell" (AJAR_TITLE=1; the shared part and what a look supplies: tools/gfx_title.py).

The game begins locked in MAP01's brick cell with the RED door leaning on its wall and one empty frame, and
the planned ending comes back to that picture: so the title is that cell (tools/map_title.py, cell()), and
New Game starts in the picture the title shows. The word AJAR is stencilled on it in ivory paint, with RED's
red used once (its white-on-red sign beside the word). The menus are stencil capitals in ivory, the selected
item RED's red; the cursor is a small RED leaf, shut and then ajar. Brick red, ivory and soot for the rest;
the help page is the notice as a paper sheet pinned on the cell's brick.
"""
import random

import gfx
from gfx import Img, shade
import gfx_title as T

NAME = "The Cell"
FONT = "AjarCell"

IVORY = (237, 227, 201)
SOOT = (26, 20, 17)
RED = gfx.DOOR_COLOURS[1]
BRICK = (150, 62, 46)
PAPER = (233, 224, 200)


def hexc(c):
    return "#%02X%02X%02X" % c


class Stencil(T.Pen):
    """Stencil capitals: heavy strokes with square ends, a bridge where a stroke meets an earlier one, a
    thin soot edge so that they read over brick and over a bright room."""
    cap, small, weight, gap, butt, edge, track, spacing = 15, 11, 3.2, 0.5, True, 0.75, 0.45, 18
    light, dark = 236, 24


pen = Stencil()

# The glyphs are grey; a colour maps their soot edge to `dark` and their body to `light`. The selected item
# is the reverse of the others: RED's red with an ivory edge, so that it reads over the brick (on which red
# alone has little contrast) and over a bright room alike.
COLOURS = {"AjarCellIvory": (hexc(SOOT), hexc(IVORY)),
           "AjarCellRed": (hexc(IVORY), hexc(RED)),
           "AjarCellScarlet": ("#2A0C08", "#E8604E"),     # the options menus: Doom's own fonts, dark to light
           "AjarCellBrick": ("#2A140E", "#D99A80")}
NORMAL, SELECTED = "AjarCellIvory", "AjarCellRed"
OPTIONS = dict(title="AjarCellIvory", label="AjarCellIvory", value="AjarCellBrick", action="AjarCellIvory",
               header="AjarCellBrick", highlight="AjarCellScarlet", selection="AjarCellScarlet",
               slider="AjarCellScarlet", sliderback="AjarCellIvory")
DIM = ("1a 14 11", 0.6)
CURSOR_AT = (-17, -1)
# The menus stand on the cell's west wall, at the left: MAP01 leans RED a hand's breadth from the frame (16
# units between them), so no view of the cell has room for the menu between the two. The camera
# (map_title.cell) puts RED in the middle third and the frame in the right one.
MENU_X, LOGO_X, LOGO_Y = 14, 76, 4


def _wear(im, seed):
    """Paint worn off a wall: small chips where the wall shows through, most of them along the paint's
    edge, and a grain in what is left. The soot edge is left whole, so the word keeps its outline."""
    rnd = random.Random(seed)
    W, H = im.w, im.h
    paint = lambda x, y: 0 <= x < W and 0 <= y < H and im.px[y * W + x][3] > 128 and sum(im.px[y * W + x][:3]) > 450
    edge = [(x, y) for y in range(H) for x in range(W)
            if paint(x, y) and not all(paint(x + dx, y + dy) for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3)))]
    inner = [(x, y) for y in range(0, H, 2) for x in range(0, W, 2) if paint(x, y)]
    for (x, y), r in [(rnd.choice(edge), rnd.choice((1, 1.5, 2))) for _ in range(len(edge) // 40)] + \
                     [(rnd.choice(inner), rnd.choice((1, 1.5))) for _ in range(len(inner) // 90)]:
        for yy in range(int(y - r), int(y + r) + 1):
            for xx in range(int(x - r), int(x + r) + 1):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r and paint(xx, yy):
                    q = im.px[yy * W + xx]
                    q[3] = round(255 * rnd.uniform(0.0, 0.35))
    for p in im.px:                                         # the paint's grain
        if p[3] > 128 and sum(p[:3]) > 450:
            d = rnd.randint(-10, 4)
            p[:3] = [max(0, min(255, v + d)) for v in p[:3]]


def logo():
    """AJAR stencilled in ivory paint, capitals 40 px high on the 320 grid, a little worn, a thin soot edge;
    RED's white-on-red sign beside it (the one use of RED's red)."""
    class Big(Stencil):
        cap, weight, gap, edge, track = 40, 8.4, 0.42, 1.0, 0.5
    big = Big()
    R = T.RES
    word = "AJAR"
    ww = T.width(big, word, 40)
    plate = 20
    W, H = round(ww + 6 + plate + 4), 44
    im = Img(W * R, H * R, (0, 0, 0, 0))
    T.write(im, big, word, 1, 2, 40, (IVORY, SOOT))
    _wear(im, 7)
    # the sign: a red square plate with a white disc, as on RED's leaf, in a soot edge
    x1, y1 = round(ww + 5), 2 + (40 - plate) // 2
    im.rect((x1 - 1) * R, (y1 - 1) * R, (x1 + plate + 1) * R, (y1 + plate + 1) * R, SOOT)
    im.rect(x1 * R, y1 * R, (x1 + plate) * R, (y1 + plate) * R, RED)
    sign = Img(plate * R, plate * R, RED)
    sign.noise(6, 1)
    sign.disc(plate * R / 2 - 0.5, plate * R / 2 - 0.5, plate * R * 0.31, (245, 245, 235))
    T.paste(im, sign, x1 * R, y1 * R)
    return im


def cursor():
    """A small RED leaf, drawn pixel by pixel (11 x 17 on the 320 grid): shut; then ajar, swung towards
    you on its hinge (left), the light beyond showing in the gap."""
    K, r, m, w, y, o, l = SOOT, RED, shade(RED, 0.74), (245, 240, 228), (235, 215, 140), (14, 10, 9), (255, 214, 150)
    shut = ["...........",
            "KKKKKKKKKK.",
            "KrrrrrrrrK.",
            "KrmmmmmmrK.",
            "KrmmwwmmrK.",
            "KrmwwwwmrK.",
            "KrmmwwmmrK.",
            "KrmmmmmmrK.",
            "KrrrrrrryK.",
            "KrmmmmmmrK.",
            "KrmmmmmmrK.",
            "KrmmmmmmrK.",
            "KrmmmmmmrK.",
            "KrmmmmmmrK.",
            "KrrrrrrrrK.",
            "KKKKKKKKKK.",
            "..........."]
    ajar = ["...........",
            "KKKKKKKKKK.",
            "KrrrrrrKlK.",
            "KrmmmmrKlK.",
            "KrmmwmrKlK.",
            "KrmwwwrKlK.",
            "KrmmwmrKlK.",
            "KrmmmmrKlK.",
            "KrrrrryKlK.",
            "KrmmmmrKlK.",
            "KrmmmmrKlK.",
            "KrmmmmrKlK.",
            "KrmmmmrKlK.",
            "KrmmmmrKlK.",
            "KrrrrrrKlK.",
            "KKKKKKKKKK.",
            "..........."]
    out = []
    for rows, f in ((shut, 1), (ajar, 0.82)):            # ajar, the leaf is turned from the light
        pal = {"K": K, "r": shade(r, f), "m": shade(m, f), "w": shade(w, f), "y": y, "o": o, "l": l}
        im = Img(len(rows[0]), len(rows), (0, 0, 0, 0))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    im.set(i, j, pal[ch])
        out.append(im)
    return out


def pause():
    """The pause sign: PAUSE in the menu's lettering, ivory with its soot edge."""
    R = T.RES
    w = T.width(pen, "PAUSE")
    im = Img(round((w + 4) * R), round((pen.cap + 4) * R), (0, 0, 0, 0))
    T.write(im, pen, "PAUSE", 2, 2, pen.cap, (IVORY, SOOT))
    return im


def backdrop():
    import map_title
    return ("map",) + map_title.cell()


def page_ground(w, h):
    """The cell's own brick (gfx.cell_brick), each pixel RES x RES, a little darker."""
    brick = gfx.cell_brick()
    R = T.RES
    im = Img(w, h)
    for y in range(h):
        for x in range(w):
            p = brick.px[((y // R) % brick.h) * brick.w + (x // R) % brick.w]
            im.px[y * w + x] = list(shade(p[:3], 0.62)) + [255]
    return im


def page_sheet(im, box):
    """A sheet of paper pinned on the brick: a soft soot shadow, the paper a little uneven, two pins."""
    x1, y1, x2, y2 = box
    R = T.RES
    for k in range(6, 0, -1):                              # the shadow
        f = 0.9 - 0.06 * k
        for y in range(y1 + 2 * R, y2 + k * R):
            for x in range(x1 + 2 * R, x2 + k * R):
                if 0 <= x < im.w and 0 <= y < im.h:
                    p = im.px[y * im.w + x]
                    p[:3] = list(shade(p[:3], f))
    rnd = random.Random(5)
    for y in range(y1, y2):
        for x in range(x1, x2):
            edge = min(x - x1, x2 - 1 - x, y - y1, y2 - 1 - y)
            f = 0.93 + 0.07 * min(1, edge / (6 * R))
            d = rnd.randint(-5, 4)
            im.set(x, y, tuple(max(0, min(255, int(v * f) + d)) for v in PAPER))
    for px in (x1 + 10 * R, x2 - 10 * R):                   # two pins
        im.disc(px + R, y1 + 5 * R + R, 3 * R, shade(SOOT, 2))
        im.disc(px, y1 + 5 * R, 3 * R, (172, 146, 92))
        im.disc(px - R // 2, y1 + 5 * R - R // 2, R, (226, 206, 150))


PAGE = dict(ink=(SOOT, PAPER), head=(BRICK, PAPER), rule=(RED, PAPER), pics=True)
