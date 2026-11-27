"""Title look 3, "The Way Out" (AJAR_TITLE=3; the shared part and what a look supplies: tools/gfx_title.py).

Every level of the game ends in the same room, the night room (ajarmap.way_out): ink walls and ceiling with
gold stars, a dark floor with brass inlay, a gold runner, candelabra, and a brass doorway that joins its two
ends, so that through it you see the room again and again. It is the one place with no colour, the room
between levels, so it is the menu's room: the title glides down it, through the doorway into the same room,
for good (tools/map_title3.py). Its palette is the look's: ink, gold stars, brass.

The word AJAR is Art Deco brass capitals, thick and thin, light on the upper left edge and dark on the lower
right so that it reads as metal inlaid in the ink, in a thin dark edge; the two A's have no crossbar: the
night room's gold star stands where each bar would be. The menus are the shared skeleton in brass with an
engraved line down the middle of every stroke (an inline face; Inline below); the selected item is bright
gold. The cursor is a gold star that twinkles (two frames). The help page is the notice as a cream card in a
brass frame on the starry ink wall.
"""
import math
import random

from gfx import Img, shade
import gfx_title as T

NAME = "The Way Out"
FONT = "AjarNight"

INK = (20, 22, 36)                  # the night room's walls and ceiling (gfx.py, AJXW2)
BRASSY = (204, 170, 92)             # its brass
STAR = (255, 226, 140)              # its stars' gold
EDGE = (14, 12, 22)                 # the dark edge round the logo, the lettering and the cursor
CREAM = (241, 233, 211)             # the help page's card
INKTEXT = (26, 28, 48)              # its text
DARKBRASS = (112, 78, 22)           # its heading and numbers (legible on cream)


def hexc(c):
    return "#%02X%02X%02X" % tuple(c)


def mix(a, b, f):
    """a to b by f (0: a, 1: b)."""
    return tuple(round(x + (y - x) * f) for x, y in zip(a, b))


# --- the lettering: an inline face ------------------------------------------------------------------------
class Inline(T.Pen):
    """Art Deco capitals from the shared skeleton: square ends, and an engraved line down the middle of every
    stroke (an inline), where a stroke is heavy enough to hold one (`least` RES px half-wide; below that, as
    on the help page, the strokes are plain). The line is found from the drawn ink itself: it is the middle of
    the stroke, the pixels as far from the ink's outside as the stroke's half weight (so it follows any
    skeleton and any spacing). The glyphs are grey: the edge dark, the inline mid grey, the body light and a
    little lighter at the top, like lit metal; the menu's TEXTCOLO colour maps that to dark edge, a brass
    groove and brass. Drawn in given colours (ink, edge), the inline is the ink a little under half way to
    the edge colour: a dark groove in brass with a dark edge, a light line in dark letters on cream."""
    # A little smaller than look 1's (cap 15) and heavy for its size: the widest item (House Rules) has to
    # end left of the doorway at the far end of the room (from 131 on the 320 grid), and the strokes, small
    # capitals too, have to stay heavy enough to hold the inline.
    cap, small, weight, gap, butt, edge, track, spacing = 13, 9.5, 3.2, 0, True, 0.75, 0.25, 16
    light, dark = 236, 24
    groove = 0.45           # the inline: this far from the ink to the edge's colour
    least = 2.9             # the least half weight (RES px) that holds an inline: the menu's capitals' is
                            # 3.2, its small capitals' 3.1; the help page's heading's 2.7 is too light (its
                            # inline came and went with where a stroke fell on the pixels)
    top_lift = 18           # the body's grey this much lighter at its top than at its foot

    def glyph(self, ch, cap, res=T.RES, top=None, height=None, small=None, ink=None):
        """The shared glyph; this only notes the stroke's half weight for paint() (as Pen.glyph weighs it:
        size(), and a small capital a little lighter)."""
        w = self.size(cap)[0]
        if ch.islower():
            sm = small if small is not None else cap * self.small / self.cap
            w *= 0.86 + 0.14 * sm / cap
        self._half = w / 2 * res
        return super().glyph(ch, cap, res=res, top=top, height=height, small=small, ink=ink)

    def paint(self, body, rim, W, H, ch, ink):
        im = Img(W, H, (0, 0, 0, 0))
        inl = self.inline(body, W, H, getattr(self, "_half", 0))
        rows = [y for y in range(H) if any(v > 0.5 for v in body[y])]
        y0, y1 = (rows[0], rows[-1]) if rows else (0, H)
        for y in range(H):
            t = 0 if y1 <= y0 else min(1, max(0, (y - y0) / (y1 - y0)))
            lift = self.top_lift * (1 - t)
            for x in range(W):
                a = max(body[y][x], rim[y][x])
                if a <= 0:
                    continue
                f = body[y][x] / a                          # 1: ink, 0: edge
                g = inl[y][x] * self.groove                 # 0: ink, groove: the inline
                if ink is None:
                    hi = min(255, self.light + lift)
                    lo = self.dark
                    v = hi + (lo - hi) * g
                    v = round(lo + (v - lo) * f)
                    im.set(x, y, (v, v, v, round(255 * a)))
                else:
                    c = mix(ink[0], ink[1], g)
                    c = mix(ink[1], c, f)
                    im.set(x, y, c + (round(255 * a),))
        return im

    def inline(self, body, W, H, h):
        """[H][W] of 0..1: the engraved line down the middle of strokes `h` RES px half-wide (none if they are
        lighter than `least`): where the ink is about h from its outside."""
        out = [[0.0] * W for _ in range(H)]
        if h < self.least:
            return out
        R = int(h) + 2
        for y in range(H):
            for x in range(W):
                if body[y][x] < 0.5:
                    continue
                best = min(R, x + 0.5, W - 0.5 - x, y + 0.5, H - 0.5 - y)   # beyond the image is outside
                for yy in range(max(0, y - R), min(H, y + R + 1)):
                    for xx in range(max(0, x - R), min(W, x + R + 1)):
                        c = body[yy][xx]
                        if c < 0.999:       # the outside, or an edge pixel: the ink ends c - 0.5 beyond it
                            v = math.hypot(xx - x, yy - y) + c - 0.5
                            if v < best:
                                best = v
                # the middle pixel of a stroke is h to h - 0.5 from its outside, the next h - 1 or less
                out[y][x] = min(1.0, max(0.0, (best - (h - 1.0)) / 0.6))
        return out


pen = Inline()

BRASS_PALE = (238, 222, 172)        # the menu's items: pale brass, near ivory
GOLD = (255, 204, 60)               # the selected one
COLOURS = {"AjarNightBrass": (hexc(EDGE), hexc(BRASS_PALE)),
           "AjarNightGold": ("#241402", hexc(GOLD)),
           # the options menus (Doom's own fonts, dark to light)
           "AjarNightIvory": ("#2A2418", "#F2E8CC"),
           "AjarNightBrassy": ("#3C2A0C", "#E2BC6A"),
           "AjarNightStar": ("#5A3C08", "#FFE89A")}
NORMAL, SELECTED = "AjarNightBrass", "AjarNightGold"
OPTIONS = dict(title="AjarNightStar", label="AjarNightIvory", value="AjarNightBrassy", action="AjarNightIvory",
               header="AjarNightBrassy", highlight="AjarNightStar", selection="AjarNightStar",
               slider="AjarNightStar", sliderback="AjarNightBrassy")
DIM = ("10 11 22", 0.65)
CURSOR_AT = (-16, 1)
# The menus stand at the left, over the room's north wall, so that the doorway and the rooms seen through it,
# in the middle of the picture, stay clear: the cursor at the 320 grid's left edge (x 1), the widest item
# ending at 140, short of the regress (the next room's doorway, 148 to 172, as each room's glide begins;
# the far doorway's left jamb, from 131 then, is all it covers). The logo stands over them, its left on theirs.
MENU_X, LOGO_X, LOGO_Y = 17, 65, 5


# --- the logo -------------------------------------------------------------------------------------------
def _inside(x, y, poly):
    n, c = len(poly), False
    j = n - 1
    for i in range(n):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def _arc(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def _letters():
    """The logo's letters, thick and thin, on a cap 40 high: [(fills, holes)], in grid units from the
    word's top left, and the centres of the two stars."""
    def A(ox):
        thin, thick, w, rise = 3.0, 7.0, 24.0, 3.0           # the outer edges meet `rise` above the cap
        slope = (w / 2) / (40 + rise)
        top = w / 2 - slope * rise
        outer = [(ox, 40), (ox + top, 0), (ox + w - top, 0), (ox + w, 40)]
        k = (w - thick - thin) / 2                          # the inner edges meet `k / slope` above the base
        hole = [(ox + thin, 40), (ox + thin + k, 40 - k / slope), (ox + w - thick, 40)]
        return [outer], [hole], (ox + thin + (w - thick - thin) / 2, 28.0)

    def J(ox):
        stem = 7.5
        p = [(ox + 7.5, 0), (ox + 7.5 + stem, 0), (ox + 15, 29)]
        p += _arc(ox + 7.5, 29, 7.5, 11, 0, 180)[1:]
        p += [(ox, 25.5), (ox + 2.9, 25.5)]
        p += _arc(ox + 5.2, 29, 2.3, 7.5, 180, 0)
        return [p], []

    def R(ox):
        stem = [(ox, 0), (ox + 7.5, 0), (ox + 7.5, 40), (ox, 40)]
        bowl = [(ox + 7, 0)] + _arc(ox + 10.5, 10.5, 8.5, 10.5, -90, 90) + [(ox + 7, 21)]
        counter = [(ox + 7.5, 3)] + _arc(ox + 10.5, 10.5, 2.8, 7.5, -90, 90) + [(ox + 7.5, 18)]
        leg = [(ox + 8.5, 19), (ox + 15.0, 19), (ox + 21.5, 40), (ox + 14.5, 40)]
        return [stem, bowl, leg], [counter]

    a1 = A(0)
    a2 = A(46)
    return [a1[:2], J(28), a2[:2], R(74)], (a1[2], a2[2])


def _star(cx, cy, rh, rv, q=0.95):
    """A four-armed star (the night room's): arms rh across and rv up and down, `q` its waist."""
    return [(cx + rh, cy), (cx + q, cy - q), (cx, cy - rv), (cx - q, cy - q),
            (cx - rh, cy), (cx - q, cy + q), (cx, cy + rv), (cx + q, cy + q)]


def _cover(W, H, shapes, ox, oy, R, ss=4):
    """[H][W] coverage (RES px) of shapes [(fills, holes)] whose units are grid px, put at (ox, oy)."""
    cov = [[0.0] * W for _ in range(H)]
    boxes = []
    for fills, holes in shapes:
        pts = [p for f in fills for p in f]
        boxes.append((min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts),
                      max(y for _, y in pts), fills, holes))
    for py in range(H):
        for px in range(W):
            n = 0
            for i in range(ss):
                for j in range(ss):
                    x = (px + (j + 0.5) / ss) / R - ox
                    y = (py + (i + 0.5) / ss) / R - oy
                    for x1, y1, x2, y2, fills, holes in boxes:
                        if x1 <= x <= x2 and y1 <= y <= y2 and any(_inside(x, y, f) for f in fills) \
                                and not any(_inside(x, y, h) for h in holes):
                            n += 1
                            break
            cov[py][px] = n / (ss * ss)
    return cov


def _dilate(cov, W, H, r):
    """cov grown by r RES px, soft at its rim."""
    out = [[0.0] * W for _ in range(H)]
    k = int(math.ceil(r + 1))
    for y in range(H):
        for x in range(W):
            best = cov[y][x]
            if best < 1:
                for yy in range(max(0, y - k), min(H, y + k + 1)):
                    for xx in range(max(0, x - k), min(W, x + k + 1)):
                        c = cov[yy][xx]
                        if c > best:
                            c *= min(1.0, max(0.0, r + 0.5 - math.hypot(xx - x, yy - y)))
                            if c > best:
                                best = c
            out[y][x] = best
    return out


def _over(im, x, y, c, a):
    if a <= 0:
        return
    p = im.px[y * im.w + x]
    q = p[3] / 255
    na = a + q * (1 - a)
    rgb = [(c[i] * a + p[i] * q * (1 - a)) / na for i in range(3)]
    im.px[y * im.w + x] = [round(v) for v in rgb] + [round(255 * na)]


BRASS_RAMP = [(0.0, (250, 230, 162)), (0.36, (216, 180, 100)), (0.39, (253, 238, 178)),
              (0.43, (228, 194, 114)), (1.0, (140, 100, 42))]


def _brass(t):
    for (t0, c0), (t1, c1) in zip(BRASS_RAMP, BRASS_RAMP[1:]):
        if t <= t1:
            return mix(c0, c1, (t - t0) / (t1 - t0))
    return BRASS_RAMP[-1][1]


def logo():
    """AJAR in Art Deco brass capitals 40 px high on the 320 grid, thick and thin, light on the upper left
    edge and dark on the lower right (inlaid metal), a polished line across at a third of their height, a
    thin dark edge round them; in each A a gold star where the crossbar would be."""
    R = T.RES
    m = 2                                                   # the margin, grid px (the edge needs 1)
    shapes, stars = _letters()
    W, H = (96 + 2 * m) * R, (40 + 2 * m) * R
    cov = _cover(W, H, shapes, m, m, R)
    starshapes = [([_star(sx, sy, 4.4, 4.6, 1.1)], []) for sx, sy in stars]
    scov = _cover(W, H, starshapes, m, m, R)
    edge = _dilate([[max(a, b) for a, b in zip(r1, r2)] for r1, r2 in zip(cov, scov)], W, H, 2.0)
    sedge = _dilate(scov, W, H, 1.2)
    at = lambda c, x, y: c[y][x] if 0 <= x < W and 0 <= y < H else 0.0
    im = Img(W, H, (0, 0, 0, 0))
    hl_c, sh_c = (255, 246, 206), (84, 56, 20)
    for y in range(H):
        t = min(1.0, max(0.0, (y + 0.5 - m * R) / (40 * R)))
        base = _brass(t)
        for x in range(W):
            _over(im, x, y, EDGE, edge[y][x])
            c = cov[y][x]
            if c > 0:
                hl = sum(w * (1 - at(cov, x - b, y - b)) for b, w in ((1, 0.55), (2, 0.3), (3, 0.15)))
                sh = sum(w * (1 - at(cov, x + b, y + b)) for b, w in ((1, 0.55), (2, 0.3), (3, 0.15)))
                col = mix(base, hl_c, 0.9 * hl)
                col = mix(col, sh_c, 0.85 * sh)
                _over(im, x, y, col, c)
            _over(im, x, y, EDGE, sedge[y][x] * (1 - scov[y][x]))
            if scov[y][x] > 0:
                d = min(math.hypot((x + 0.5) / R - m - sx, (y + 0.5) / R - m - sy) for sx, sy in stars)
                col = mix((255, 252, 234), STAR, min(1, d / 1.6))
                col = mix(col, (226, 176, 70), max(0, min(1, (d - 1.6) / 2.2)))
                _over(im, x, y, col, scov[y][x])
    return im


# --- the cursor -----------------------------------------------------------------------------------------
CURSOR_PAL = {"W": (255, 252, 232), "Y": (255, 236, 160), "G": (250, 212, 108), "g": (204, 160, 70),
              "d": (150, 116, 48), "K": EDGE}


def cursor():
    """A gold star (the night room's: a bright centre and four arms), 13 x 13 on the 320 grid, drawn pixel
    by pixel: small, and then for a moment large, with glints between its arms (it twinkles)."""
    small = [".............",
             ".............",
             "......K......",
             ".....KgK.....",
             ".....KGK.....",
             "...KKdYdKK...",
             "..KgGYWYGgK..",
             "...KKdYdKK...",
             ".....KGK.....",
             ".....KgK.....",
             "......K......",
             ".............",
             "............."]
    large = ["......K......",
             ".....KgK.....",
             ".....KGK.....",
             "...g.KYK.g...",
             "....KdYdK....",
             ".KKKdYWYdKKK.",
             "KgGYYWWWYYGgK",
             ".KKKdYWYdKKK.",
             "....KdYdK....",
             "...g.KYK.g...",
             ".....KGK.....",
             ".....KgK.....",
             "......K......"]
    out = []
    for rows in (small, large):
        im = Img(len(rows[0]), len(rows), (0, 0, 0, 0))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    im.set(i, j, CURSOR_PAL[ch])
        out.append(im)
    return out


def pause():
    """The pause sign: PAUSE in the menu's lettering, pale brass with its groove and dark edge."""
    R = T.RES
    w = T.width(pen, "PAUSE")
    im = Img(round((w + 4) * R), round((pen.cap + 5) * R), (0, 0, 0, 0))
    T.write(im, pen, "PAUSE", 2, 2, pen.cap, (BRASS_PALE, EDGE))
    return im


def backdrop():
    import map_title3
    return ("map",) + map_title3.night()


# --- the help page --------------------------------------------------------------------------------------
def page_ground(w, h):
    """The night room's wall: ink, a little uneven, with its gold stars (one grid pixel, the bigger ones
    with four brass arms), every pixel RES x RES."""
    R = T.RES
    gw, gh = w // R, h // R
    rnd = random.Random(62)
    grid = []
    for _ in range(gw * gh):
        d = rnd.randint(-3, 3)
        grid.append(tuple(max(0, min(255, v + d)) for v in INK))
    for _ in range(gw * gh * 14 // (64 * 146)):
        x, y, big = rnd.randrange(2, gw - 2), rnd.randrange(2, gh - 2), rnd.random() < 0.3
        grid[y * gw + x] = STAR
        if big:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                grid[(y + dy) * gw + x + dx] = BRASSY
    im = Img(w, h)
    for y in range(h):
        for x in range(w):
            im.px[y * w + x] = list(grid[min(gh - 1, y // R) * gw + min(gw - 1, x // R)]) + [255]
    return im


def page_sheet(im, box):
    """The notice as a cream card in a brass frame (light on its upper left, dark on its lower right), a
    thin dark brass rule inside it, its corners stepped in, a soft shadow on the wall below it."""
    x1, y1, x2, y2 = box
    R = T.RES
    for k in range(6, 0, -1):                              # the shadow
        f = 0.9 - 0.08 * k
        for y in range(y1 + 2 * R, min(im.h, y2 + k * R)):
            for x in range(x1 + 2 * R, min(im.w, x2 + k * R)):
                p = im.px[y * im.w + x]
                p[:3] = list(shade(p[:3], f))
    rnd = random.Random(7)
    fw = 3 * R                                              # the brass frame
    for y in range(y1, y2):
        for x in range(x1, x2):
            e = min(x - x1, x2 - 1 - x, y - y1, y2 - 1 - y)
            if e < fw:
                # which side: the upper left lit, the lower right dark
                lit = (x - x1 == e or y - y1 == e)
                f = (1.18 if lit else 0.66) if e < R else (1.0 if e < fw - R else (0.62 if lit else 1.15))
                c = shade(BRASSY, f)
                d = rnd.randint(-4, 4)
                im.set(x, y, tuple(max(0, min(255, v + d)) for v in c))
            else:
                d = rnd.randint(-3, 2)
                im.set(x, y, tuple(max(0, min(255, v + d)) for v in CREAM))
    # a thin dark brass rule inside, its corners stepped in (the 1930s manner)
    ins = fw + R
    rx1, ry1, rx2, ry2 = x1 + ins, y1 + ins, x2 - ins, y2 - ins
    t, s = R // 2 or 1, 4 * R
    im.rect(rx1 + s, ry1, rx2 - s, ry1 + t, DARKBRASS)
    im.rect(rx1 + s, ry2 - t, rx2 - s, ry2, DARKBRASS)
    im.rect(rx1, ry1 + s, rx1 + t, ry2 - s, DARKBRASS)
    im.rect(rx2 - t, ry1 + s, rx2, ry2 - s, DARKBRASS)
    for cx, sx in ((rx1, 1), (rx2, -1)):
        for cy, sy in ((ry1, 1), (ry2, -1)):
            kx, ky = cx + sx * s, cy + sy * s           # the step's inner corner
            xa, xb = sorted((kx, kx - sx * t))
            ya, yb = sorted((cy, ky))
            im.rect(xa, ya, xb, yb, DARKBRASS)          # down (or up) from the long rule to the step
            xa, xb = sorted((cx, kx))
            ya, yb = sorted((ky, ky - sy * t))
            im.rect(xa, ya, xb, yb, DARKBRASS)          # and across to the side rule


PAGE = dict(ink=(INKTEXT, CREAM), head=(DARKBRASS, CREAM), rule=(DARKBRASS, CREAM), pics=True)
