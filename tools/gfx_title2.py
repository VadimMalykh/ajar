"""Title look 2, "Portals" (AJAR_TITLE=2; the shared part and what a look supplies: tools/gfx_title.py).

The game's own sight: a door hung in a frame opens onto the place it has always opened onto. The title is
a dark hall with three colour doors hung in its wall and standing open, and through each a bright place
of the game, built with that level's own textures and props (tools/map_title2.py): BLUE onto MAP07's
planetarium, RED onto MAP03's stalls and stage, YELLOW onto MAP08's toy department. The camera glides
along the hall and back, and the places shift in their doorways.

The word AJAR is set in tall thin ivory capitals with the door in it: A and J stand on the wall, then a
door-high slit of warm light, and A and R are on the leaf, swung a little towards you (drawn foreshortened)
with a wedge of the light on the floor under the gap. The menus are thin monoline capitals, as on a
hotel's engraved plates: ivory, the selected item the warm yellow of the light through a door; the cursor
is a small doorway, shut and then open onto that light. Slate and ink for the darks, brass for the rest;
the help page is the notice as a card in a thin brass holder on the hall's wall.
"""
import math
import random

import gfx
from gfx import Img, shade
import gfx_title as T

NAME = "Portals"
FONT = "AjarPortals"

IVORY = (238, 230, 210)
LAMP = (255, 196, 84)                 # the light through a door
LAMP_HI = (255, 234, 170)
INK = (14, 16, 22)
SLATE = (54, 60, 74)
BRASS = (196, 164, 96)
CARD = (238, 230, 208)
GOLD_INK = (116, 84, 26)              # the heading and the numbers on the card


def hexc(c):
    return "#%02X%02X%02X" % c


class Mono(T.Pen):
    """Thin monoline capitals with round ends, set wide, as on an engraved plate; a thin ink edge, only so
    much that they read over a bright doorway."""
    cap, small, weight, gap, butt, edge, track, spacing = 14, 10.5, 1.9, 0, False, 0.6, 1.05, 17
    light, dark = 240, 20


pen = Mono()

COLOURS = {"AjarPortIvory": (hexc(INK), hexc(IVORY)),
           "AjarPortLamp": ("#2A1804", hexc(LAMP)),
           "AjarPortBrass": ("#241B0C", "#D8B66E"),        # the options menus: Doom's own fonts, dark to light
           "AjarPortSlate": ("#101319", "#A3AEC0")}
NORMAL, SELECTED = "AjarPortIvory", "AjarPortLamp"
OPTIONS = dict(title="AjarPortIvory", label="AjarPortIvory", value="AjarPortBrass", action="AjarPortIvory",
               header="AjarPortBrass", highlight="AjarPortLamp", selection="AjarPortLamp",
               slider="AjarPortLamp", sliderback="AjarPortSlate")
DIM = ("10 12 18", 0.62)
CURSOR_AT = (-18, -2)
# The menus stand on the hall's plain wall at the left; the doorways step away across the right
# (map_title2), the furthest, YELLOW's, starting just right of the middle: the widest menu line ends
# some 15 short of it.
MENU_X, LOGO_X, LOGO_Y = 14, 68, 4


# --- the logo ----------------------------------------------------------------------------------------
class Tall(Mono):
    cap, weight, edge, track = 40, 3.0, 0, 1.6


SQUEEZE = 0.74                       # the logo's capitals are drawn this much narrower than the menu's: tall
SWING = 34                           # degrees the leaf stands open, towards you
NEAR = 4.2                           # how far the eye is from the wall, in leaf widths (the perspective)


def _letters(text, cap):
    """The capitals of `text`, ivory, no edge, squeezed: an Img at RES with the cap line 3 px from the top."""
    big = Tall()
    R = T.RES
    w = T.width(big, text, cap) + 4
    flat = Img(round(w * R), round((cap + 8) * R), (0, 0, 0, 0))
    T.write(flat, big, text, 0, 3, cap, (IVORY, IVORY))
    out = T.shrink(flat, max(1, round(flat.w * SQUEEZE)), flat.h)
    return out


def _bbox(im):
    xs = [x for y in range(im.h) for x in range(im.w) if im.px[y * im.w + x][3] > 8]
    return min(xs), max(xs) + 1


def _sample(im, x, y):
    """im at (x, y), bilinear, transparent outside."""
    x0, y0 = math.floor(x - 0.5), math.floor(y - 0.5)
    fx, fy = x - 0.5 - x0, y - 0.5 - y0
    acc = [0.0, 0.0, 0.0, 0.0]
    for dx, dy, wgt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xx, yy = x0 + dx, y0 + dy
        if 0 <= xx < im.w and 0 <= yy < im.h and wgt:
            p = im.px[yy * im.w + xx]
            a = p[3] / 255 * wgt
            for i in range(3):
                acc[i] += p[i] * a
            acc[3] += a
    if acc[3] <= 0:
        return None
    return [acc[0] / acc[3], acc[1] / acc[3], acc[2] / acc[3], acc[3] * 255]


def logo():
    """AJAR: A and J on the wall, a door-high slit of warm light, A and R on the leaf swung towards you
    (its free edge nearer, so taller; its top and bottom edges converging on the hinge at the right), and
    the light's wedge on the floor under the gap. Ivory capitals 44 px high on the 320 grid with a thin
    hard ink edge, the slit edged alike and the leaf outlined, so that it reads over the dark hall and over
    a bright room in play alike."""
    R = T.RES
    cap = 44
    aj, ar = _letters("AJ", cap), _letters("AR", cap)
    ajl, ajr = _bbox(aj)
    arl, arr = _bbox(ar)
    pad = 4 * R                                         # room for the dark ground round it all
    top = 3 * R                                         # the cap line in the letters' images
    gap = 6 * R                                         # from J to the leaf's free edge: the slit
    lw = (arr - arl) + 6 * R                            # the leaf, flat: the letters and a margin each side
    lh = round((cap + 6) * R)                           # its height: the doorway's
    a = math.radians(SWING)
    D = NEAR * lw
    t_free = lw                                         # the free edge is the leaf's width from the hinge
    z_free = D - t_free * math.sin(a)
    free_w = t_free * math.cos(a) * D / z_free          # the leaf as drawn, from hinge to free edge
    grow = D / z_free                                   # the free edge's height over the hinge's
    W = pad + (ajr - ajl) + gap + round(free_w) + pad
    door_top = pad + round(2 * R)                       # the doorway's top, in the wall
    H = door_top + round(lh * (grow + 1) / 2) + 10 * R + pad
    yc = door_top + lh / 2                              # the eye's height: the leaf's middle
    im = Img(W, H, (0, 0, 0, 0))
    light = [[0.0] * W for _ in range(H)]               # the warm light: slit, the leaf's edge, the floor
    ink = Img(W, H, (0, 0, 0, 0))                       # the ivory capitals
    leaf = [[0.0] * W for _ in range(H)]                # the leaf's face (a dark ground under A R)
    # A and J, on the wall: their cap line `top + 3` px down in the doorway's terms
    x0 = pad
    oy = door_top + 3 * R - top
    for y in range(aj.h):
        for x in range(ajl, ajr):
            p = aj.px[y * aj.w + x]
            if p[3]:
                T._over(ink, x0 + x - ajl, oy + y, p)
    jamb = x0 + (ajr - ajl) + gap // 3                  # the wall's edge: the slit runs from here
    hinge = x0 + (ajr - ajl) + gap + round(free_w)
    free = hinge - free_w
    foot = door_top + lh                                # the floor, at the wall
    # the slit, door-high, from the jamb to the leaf's free edge (the leaf, nearer, hides the rest)
    for y in range(door_top, foot):
        for x in range(jamb, math.ceil(free) + 2):
            c = 1.0 - 0.35 * abs((y - yc) / (lh / 2)) ** 3
            light[y][x] = max(light[y][x], c)
    # the wedge of light on the floor, from the slit's foot towards you and to the left, fading
    deep = 10 * R
    for k in range(deep):
        f = k / deep
        y = foot + k
        left = jamb - f * 16 * R
        right = free + 2 + f * 1 * R
        for x in range(max(0, math.floor(left)), min(W, math.ceil(right))):
            cov = min(1, x + 1 - left, right - x)
            light[y][x] = max(light[y][x], (1 - f) ** 1.2 * 0.95 * max(0, cov))
    # the leaf: A R on it, as seen swung `SWING` degrees towards you about the hinge at its right
    flat_ar = Img(lw, lh, (0, 0, 0, 0))
    for y in range(min(ar.h, lh)):
        for x in range(arl, arr):
            p = ar.px[y * ar.w + x]
            if p[3]:
                T._over(flat_ar, x - arl + 3 * R, y - top + 3 * R, p)
    for Y in range(H):
        for X in range(W):
            d = hinge - (X + 0.5)
            if d < 0:
                continue
            t = d * D / (D * math.cos(a) + d * math.sin(a))
            if t > lw:
                continue
            z = D - t * math.sin(a)
            yl = (Y + 0.5 - yc) * z / D + lh / 2
            if not 0 <= yl < lh:
                continue
            s = lw - t
            leaf[Y][X] = 2 if min(yl, lh - yl) < 0.8 * R else 1
            p = _sample(flat_ar, s, yl)
            if p:
                T._over(ink, X, Y, [round(v) for v in p])
            if s < 1.4 * R:                               # its edge, lit by the slit
                light[Y][X] = max(light[Y][X], 0.75)
    # a thin hard dark edge round the capitals and the slit (not a soft ground: that blurs over a light
    # room), the leaf's face under A R, and its edge
    mask = [[max(ink.px[y * W + x][3] / 255, light[y][x] if y < foot else 0) for x in range(W)] for y in range(H)]
    rim = _soften(mask, 1.5 * R, hard=True)
    for y in range(H):
        for x in range(W):
            if leaf[y][x]:
                c = (INK, shade(SLATE, 0.8), shade(SLATE, 1.7))[int(leaf[y][x])]
                im.px[y * W + x] = list(c) + [242]
            elif rim[y][x] > 0:
                im.px[y * W + x] = list(INK) + [round(255 * min(1, rim[y][x]))]
    # and the leaf's own outline, hard, so that its slate reads on a light ground too
    for y in range(H):
        for x in range(W):
            if leaf[y][x] and any(not (0 <= x + dx < W and 0 <= y + dy < H) or not leaf[y + dy][x + dx]
                                  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                for dy in range(-1, 1):
                    for dx in range(-1, 1):
                        if 0 <= x + dx < W and 0 <= y + dy < H:
                            im.px[(y + dy) * W + x + dx] = list(INK) + [255]
    for y in range(H):
        for x in range(W):
            if light[y][x] > 0:
                v = light[y][x]
                c = tuple(round(LAMP[i] + (LAMP_HI[i] - LAMP[i]) * max(0, v - 0.6) / 0.4) for i in range(3))
                T._over(im, x, y, list(c) + [round(255 * min(1, v))])
    # the capitals, with a thin ink edge
    edge = _soften([[ink.px[y * W + x][3] / 255 for x in range(W)] for y in range(H)], 1.2 * R, hard=True)
    for y in range(H):
        for x in range(W):
            if edge[y][x] > 0:
                T._over(im, x, y, list(INK) + [round(255 * min(1, edge[y][x]))])
    for y in range(H):
        for x in range(W):
            p = ink.px[y * W + x]
            if p[3]:
                T._over(im, x, y, list(IVORY) + [p[3]])
    return im


def _soften(mask, r, hard=False):
    """The mask spread `r` px round: each pixel the most of the mask near it, falling off with distance
    (hard: kept full up to r)."""
    H, W = len(mask), len(mask[0])
    ri = math.ceil(r)
    offs = [(dx, dy, math.hypot(dx, dy)) for dy in range(-ri, ri + 1) for dx in range(-ri, ri + 1)
            if math.hypot(dx, dy) <= r + 0.5]
    out = [[0.0] * W for _ in range(H)]
    pts = [(x, y, mask[y][x]) for y in range(H) for x in range(W) if mask[y][x] > 0.02]
    for x, y, v in pts:
        for dx, dy, d in offs:
            xx, yy = x + dx, y + dy
            if 0 <= xx < W and 0 <= yy < H:
                f = (min(1, r + 0.5 - d) if hard else max(0, 1 - d / (r + 0.5)) ** 1.3) * v
                if f > out[yy][xx]:
                    out[yy][xx] = f
    return out


# --- the cursor --------------------------------------------------------------------------------------
def cursor():
    """A small doorway, drawn pixel by pixel (13 x 17 on the 320 grid): shut, a dark leaf in its brass
    frame; then open, the leaf swung towards you on its hinge (left), its edge catching the light, and the
    doorway full of warm light."""
    shut = [".............",
            "....KKKKKKKKK",
            "....KFFFFFFFK",
            "....KFdddddFK",
            "....KFdmmmdFK",
            "....KFdmmmdFK",
            "....KFdmmmdFK",
            "....KFdddddFK",
            "....KFddddkFK",
            "....KFdmmmdFK",
            "....KFdmmmdFK",
            "....KFdmmmdFK",
            "....KFdmmmdFK",
            "....KFdddddFK",
            "....KFdddddFK",
            "....KFdddddFK",
            "....KKKKKKKKK"]
    ajar = [".............",
            ".l..KKKKKKKKK",
            ".ld.KFFFFFFFK",
            ".lddKFyyyyyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFywwwyFK",
            ".lddKFyyyyyFK",
            ".ld.KFyyyyyFK",
            ".l..KKKKKKKKK"]
    pal = {"K": INK, "F": BRASS, "d": SLATE, "m": shade(SLATE, 1.3), "k": (236, 204, 120),
           "y": LAMP, "w": LAMP_HI, "l": (255, 214, 130)}
    out = []
    for rows, f in ((shut, 1), (ajar, 0.8)):
        im = Img(len(rows[0]), len(rows), (0, 0, 0, 0))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    c = pal[ch]
                    im.set(i, j, shade(c, f) if ch in "dm" else c)
        out.append(im)
    return out


def pause():
    """The pause sign: PAUSE in the menu's lettering, ivory with its ink edge, between two short rules."""
    R = T.RES
    w = T.width(pen, "PAUSE")
    im = Img(round((w + 28) * R), round((pen.cap + 6) * R), (0, 0, 0, 0))
    T.write(im, pen, "PAUSE", 14, 3, pen.cap, (IVORY, INK))
    y = round((3 + pen.cap / 2) * R)
    for x1, x2 in ((2, 10), (w + 18, w + 26)):
        x1, x2 = round(x1 * R), round(x2 * R)
        im.rect(x1 - 1, y - R // 2 - 1, x2 + 1, y + R // 2 + 1, INK)
        im.rect(x1, y - R // 2, x2, y + R // 2, BRASS)
    return im


# --- the backdrop ------------------------------------------------------------------------------------
def backdrop():
    import map_title2
    return ("map",) + map_title2.portals()


def hall_wall():
    """The hall's wall (AJT2W, 64 x 176, the hall's height): plain slate plaster, a dado of darker panels
    under a rail, a dark skirting. Neutral, and low in contrast: it is lit dimly and must not compete with
    the doorways."""
    im = Img(64, 176)
    field, dado, rail, skirt = (84, 88, 98), (62, 64, 72), (104, 98, 86), (34, 34, 38)
    im.rect(0, 0, 64, 176, field)
    im.rect(0, 0, 64, 6, shade(field, 0.78))                     # a shadow under the cornice
    im.rect(0, 6, 64, 7, shade(field, 1.08))
    im.rect(0, 124, 64, 168, dado)
    for x1 in (4, 36):                                           # two panels a 64
        im.frame(x1, 132, x1 + 24, 162, shade(dado, 0.8), 1)
        im.rect(x1 + 1, 161, x1 + 24, 162, shade(dado, 1.15))
    im.rect(0, 121, 64, 125, rail)
    im.rect(0, 121, 64, 122, shade(rail, 1.2))
    im.rect(0, 124, 64, 125, shade(rail, 0.6))
    im.rect(0, 168, 64, 176, skirt)
    im.rect(0, 168, 64, 169, shade(skirt, 1.4))
    im.noise(3, 211)
    return im


def hall_floor():
    """The hall's floor (AJT2F): dark oak boards, 16 wide, the joints staggered."""
    im = Img(64, 64)
    wood = (70, 56, 46)
    rnd = random.Random(212)
    for k in range(4):
        x1 = k * 16
        c = shade(wood, rnd.uniform(0.9, 1.08))
        im.rect(x1, 0, x1 + 16, 64, c)
        im.rect(x1, 0, x1 + 1, 64, shade(wood, 0.6))
        j = (k * 23) % 64
        im.rect(x1, j, x1 + 16, j + 1, shade(wood, 0.6))
        for g in range(3):
            gx = x1 + rnd.randint(3, 13)
            im.rect(gx, 0, gx + 1, 64, shade(c, 0.9))
    im.noise(3, 213)
    return im


def hall_ceiling():
    """The hall's ceiling (AJT2C): plain plaster, darker than the wall."""
    im = Img(64, 64, (66, 68, 76))
    im.noise(2, 214)
    return im


def files():
    """What the hall wears of its own (map_title2: WALL, FLOOR, CEIL)."""
    return {"textures/AJT2W.png": hall_wall().png(),
            "flats/AJT2F.png": hall_floor().png(),
            "flats/AJT2C.png": hall_ceiling().png()}


# --- the help page -----------------------------------------------------------------------------------
def page_ground(w, h):
    """The hall's wall (its plaster), each pixel RES x RES, dim."""
    wall = hall_wall()
    R = T.RES
    im = Img(w, h)
    for y in range(h):
        for x in range(w):
            p = wall.px[(((y // R) % 112) + 8) * wall.w + (x // R) % wall.w]
            im.px[y * w + x] = list(shade(p[:3], 0.55)) + [255]
    return im


def page_sheet(im, box):
    """A cream card in a thin brass holder, screwed to the wall: a soft shadow, the holder's bevel, the
    card a little uneven, a screw at each corner."""
    x1, y1, x2, y2 = box
    R = T.RES
    b = 3 * R                                                    # the holder's width
    for k in range(6, 0, -1):                                    # the shadow
        f = 0.92 - 0.07 * k
        for y in range(y1 - b + 2 * R, y2 + b + k * R):
            for x in range(x1 - b + 2 * R, x2 + b + k * R):
                if 0 <= x < im.w and 0 <= y < im.h:
                    p = im.px[y * im.w + x]
                    p[:3] = list(shade(p[:3], f))
    for y in range(y1 - b, y2 + b):                              # the holder: lit from the top left
        for x in range(x1 - b, x2 + b):
            sides = (x - (x1 - b), y - (y1 - b), (x2 + b - 1) - x, (y2 + b - 1) - y)    # left, top, right, bottom
            e = min(sides)
            if e < 0:
                continue
            lit = sides.index(e) < 2                             # the top and left faces catch the light
            c = BRASS
            if e < R:
                c = shade(BRASS, 1.3) if lit else shade(BRASS, 0.55)
            elif e >= b - R:
                c = shade(BRASS, 0.55) if lit else shade(BRASS, 1.25)
            im.set(x, y, c)
    rnd = random.Random(15)
    for y in range(y1, y2):
        for x in range(x1, x2):
            edge = min(x - x1, x2 - 1 - x, y - y1, y2 - 1 - y)
            f = 0.94 + 0.06 * min(1, edge / (5 * R))
            d = rnd.randint(-4, 3)
            im.set(x, y, tuple(max(0, min(255, int(v * f) + d)) for v in CARD))
    for sx, sy in ((x1 - b // 2, y1 - b // 2), (x2 + b // 2, y1 - b // 2),
                   (x1 - b // 2, y2 + b // 2), (x2 + b // 2, y2 + b // 2)):
        im.disc(sx, sy, 1.6 * R, shade(BRASS, 0.5))
        im.disc(sx - 1, sy - 1, 1.1 * R, shade(BRASS, 1.3))
        im.rect(sx - R, sy, sx + R, sy + 1, shade(BRASS, 0.45))


PAGE = dict(ink=((34, 30, 28), CARD), head=(GOLD_INK, CARD), rule=(GOLD_INK, CARD), pics=True)
