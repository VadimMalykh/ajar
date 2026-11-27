"""Ajar's own title, menus, cursor, help page and quit messages, in place of Doom II's (AJAR_TITLE).

The switch: AJAR_TITLE unset or 0 puts nothing of this into the package (make() returns {}, nothing is
appended to mapinfo.txt or language.txt): the title, the menus and the help page are Doom II's, as before.
AJAR_TITLE=n (1, 2, 3) takes every part from look n, the module tools/gfx_title<n>.py. PARTS says which
look each part comes from; to mix looks by part later, set MIX (here, one place) or AJAR_TITLE_MIX, e.g.
AJAR_TITLE=1 AJAR_TITLE_MIX=logo:2,cursor:3.

The parts:
  backdrop   what the title shows behind the menu: a title map (maps/TITLEMAP.wad, tools/map_title.py) or a
             still picture (gameinfo titlepage)
  logo       the word AJAR at the top of the main menu (graphic AJLOGO); it belongs to the menu, so it also
             shows over the game when Esc is pressed in play
  lettering  the list menus' font (fonts/<FONT>/), its colours (TEXTCOLO) and the pause sign (AJPAUSE)
  cursor     the list menus' selector: one graphic that blinks, or two (shut, ajar) that the menu delegate
             (src/zscript/title.zs, AjarMenuDelegate) shows in turn
  page       the help page (AJHELP, "House Rules", F1), and the palette of the options menus and the dim

What is shared, for every look (here): the lettering's skeleton (SKELETON: strokes on a grid, a pen per look
renders it), the font writer, MENUDEF, the extra gameinfo, the LANGUAGE strings (quit messages and menu
words), the help page's layout and words, and the shots' specimens (specimens()).

A look module, tools/gfx_title<n>.py, supplies (by part; tools/gfx_title1.py is the example):
  NAME            its name on the look board
 lettering:
  FONT            the name of its menu font (a folder fonts/<FONT>/; never BigFont or SmallFont)
  pen             a Pen (below, or a subclass with its own paint() or glyph()): how the skeleton is drawn,
                  its sizes on the 320x200 grid
  COLOURS         {TEXTCOLO name: (dark, light)}, "#rrggbb" each: the colours its font is drawn in. The
                  glyphs are grey, so a colour maps their edge to `dark` and their body to `light`
  NORMAL, SELECTED  the COLOURS names of a menu item and of the selected one
  pause()         the pause sign, an Img at RES
 logo:
  logo()          the logo, an Img drawn RES times finer than the 320 grid (TEXTURES scales it back)
 cursor:
  cursor()        [Img, ...]: one frame (the engine blinks it) or two (shut, ajar), at 1x (320 grid pixels)
  CURSOR_AT       (x, y) of the cursor's top left from the selected item's top left, on the 320 grid
 backdrop:
  backdrop()      ("map", wad bytes, extra lines for the map's mapinfo block; tools/map_title.py) or
                  ("picture", an Img 320x200 at RES)
  MENU_X, LOGO_X, LOGO_Y, MENU_TOP   optional: where the menus stand over this backdrop (default: centred)
 page:
  page_ground(w, h)          the help page's ground (an Img w x h, at RES)
  page_sheet(im, box)        draws the notice's sheet on it; box = (x1, y1, x2, y2) at RES
  PAGE            dict: ink, head, rule = (colour, edge colour) of the text, the heading and the rules'
                  numbers; pics: True to edge the pictures
  OPTIONS         gameinfo's menufontcolor_* (title, label, value, action, header, highlight, selection)
                  and menuslidercolor / menusliderbackcolor (slider, sliderback): colour names, the
                  engine's or the lettering look's COLOURS (the colours a look uses must be in the TEXTCOLO
                  of the lettering's look: give `page` and `lettering` the same look, or the same names)
  DIM             (gameinfo dimcolor "rr gg bb", dimamount)
"""
import copy
import importlib
import math
import os

from gfx import Img, shade
import gfx

LOOK = int(os.environ.get("AJAR_TITLE") or 0)
PARTS = ("backdrop", "logo", "lettering", "cursor", "page")
# A mix by part, {part: look}, over AJAR_TITLE's look for every part. Empty: one look whole.
MIX = {}
RES = 2             # the logo, the help page and the font's glyphs are drawn this many times finer than the
                    # 320x200 grid and scaled back down by the engine (TEXTURES XScale / font.inf Scale)


def parts():
    """{part: look number}; every part 0 when the switch is off."""
    mix = dict(MIX)
    for item in filter(None, (os.environ.get("AJAR_TITLE_MIX") or "").split(",")):
        part, n = item.split(":")
        mix[part] = int(n)
    return {p: (mix.get(p, LOOK) if LOOK else 0) for p in PARTS}


def look(n):
    return importlib.import_module(f"gfx_title{n}")


# --- the lettering's skeleton ------------------------------------------------------------------------
# Capitals on a grid 10 high (y down: 0 the cap line, 10 the baseline); x from 0 to the glyph's width.
# A glyph is strokes separated by "|"; a stroke is a path of points "x,y" and arcs "(cx,cy,rx,ry,a0,a1)"
# (degrees; 0 is +x, 90 is +y, i.e. down; a0 to a1 either way round) joined in order. A stroke of one
# point is a dot. Strokes are listed so that a pen that breaks junctions (a stencil) can tell which one
# gives way: a stroke whose end lies on an EARLIER stroke ends short of it there (Pen.gap). So split a
# letter into strokes where a stencil would bridge it (O: two halves; B: the stem, then each bowl), and
# keep as one stroke what a stencil keeps whole (L, M, S). Nothing here assumes a weight: the pen adds it.
SKELETON = {
    "A": "0,10 4,0 8,10 | 1.2,7 6.8,7",
    "B": "0,0 0,10 | 0,0 3.8,0 (3.8,2.4,2.4,2.4,-90,90) 0,4.8 | 0,4.8 4.2,4.8 (4.2,7.4,2.6,2.6,-90,90) 0,10",
    "C": "(4,5,4,5,-42,-318)",
    "D": "0,0 0,10 | 0,0 2.6,0 (2.6,5,4.4,5,-90,90) 0,10",
    "E": "6,0 0,0 0,10 6,10 | 0,5 5,5",
    "F": "6,0 0,0 0,10 | 0,5 5,5",
    "G": "(4,5,4,5,-42,-330) 7.5,10 | 7.5,5.6 4.2,5.6",
    "H": "0,0 0,10 | 7,0 7,10 | 0,5 7,5",
    "I": "0,0 0,10",
    "J": "5,0 5,7 (2.5,7,2.5,3,0,180)",
    "K": "0,0 0,10 | 6.5,0 0,6.5 | 2.3,4.4 6.8,10",
    "L": "0,0 0,10 6,10",
    "M": "0,10 0,0 4.5,7.5 9,0 9,10",
    "N": "0,10 0,0 7,10 7,0",
    "O": "(4.2,5,4.2,5,90,270) | (4.2,5,4.2,5,-90,90)",
    "P": "0,0 0,10 | 0,0 3.9,0 (3.9,2.65,2.65,2.65,-90,90) 0,5.3",
    "Q": "(4.2,5,4.2,5,90,270) | (4.2,5,4.2,5,-90,90) | 5,7 8.4,10.4",
    "R": "0,0 0,10 | 0,0 3.9,0 (3.9,2.65,2.65,2.65,-90,90) 0,5.3 | 3.2,5.3 7,10",
    "S": "(3.6,2.6,3.3,2.6,-25,-270) (3.6,7.4,3.6,2.6,-90,155)",
    "T": "0,0 8,0 | 4,0 4,10",
    "U": "0,0 0,6.2 (3.6,6.2,3.6,3.8,180,0) 7.2,0",
    "V": "0,0 4,10 8,0",
    "W": "0,0 2.6,10 5.2,1.6 7.8,10 10.4,0",
    "X": "0,0 7.4,10 | 7.4,0 0,10",
    "Y": "0,0 4,5 8,0 | 4,5 4,10",
    "Z": "0,0 7,0 0,10 7,10",
    "0": "(3.6,5,3.6,5,90,270) | (3.6,5,3.6,5,-90,90)",
    "1": "0.6,2.2 3.2,0 3.2,10",
    "2": "(3.5,3,3.4,3,-172,32) 0,10 7,10",
    "3": "(3.4,2.5,3.1,2.5,-165,90) | (3.5,7.5,3.6,2.5,-90,165)",
    "4": "5.2,10 5.2,0 0,7 7.6,7",
    "5": "6.6,0 1,0 0.6,4.6 (3.5,6.9,3.6,3.1,-128,150)",
    "6": "(3.6,6.9,3.6,3.1,0,360) | (3.8,5.4,3.6,5.4,-62,-180) 0.05,6.9",
    "7": "0,0 7,0 2.6,10",
    "8": "(3.6,2.5,3.1,2.5,0,360) | (3.6,7.5,3.6,2.5,0,360)",
    "9": "(3.6,3.1,3.6,3.1,0,360) | 7.2,3.1 7.2,5.1 (3.6,5.1,3.6,4.9,0,118)",
    ".": "0,10",
    ",": "0.4,9.6 -0.5,11.8",
    ":": "0,3.6 | 0,10",
    ";": "0.4,3.6 | 0.4,9.6 -0.5,11.8",
    "!": "0,0 0,6.8 | 0,10",
    "?": "(3,2.7,3,2.7,-170,90) 3,6.6 | 3,10",
    "'": "0,0 0,2.8",
    '"': "0,0 0,2.8 | 2,0 2,2.8",
    "-": "0,6 3.6,6",
    "(": "(3.2,5,3.2,6.2,-118,-242)",
    ")": "(0,5,3.2,6.2,-62,62)",
    "/": "5,-0.4 0,10.4",
    "&": "7.4,10 2,3.7 1.4,2.2 1.8,0.8 3,0 4.2,0.6 4.5,1.8 4,3.2 1.2,5.6 0.2,7.2 0.4,8.8 1.6,9.9 3.2,10 "
         "4.8,9.4 6.6,7.4 7.3,5.6",
    "%": "0,10 7.4,0 | (1.5,1.9,1.5,1.9,0,360) | (5.9,8.1,1.5,1.9,0,360)",
}
SPACE = 4.0         # the width of a space, in grid units of the capitals


def strokes(ch):
    """The glyph's strokes as lists of (x, y) in grid units, shifted so that its left is at x = 0, and its
    width; a lowercase letter is its capital (drawn smaller by the pen)."""
    out = []
    for part in SKELETON[ch.upper()].split("|"):
        pts, text = [], part.strip()
        while text:
            if text[0] == "(":
                end = text.index(")")
                cx, cy, rx, ry, a0, a1 = (float(v) for v in text[1:end].split(","))
                n = max(2, int(abs(a1 - a0) / 7.5) + 1)
                for k in range(n + 1):
                    a = math.radians(a0 + (a1 - a0) * k / n)
                    pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
                text = text[end + 1:].strip()
            else:
                tok, _, text = text.partition(" ")
                x, y = tok.split(",")
                pts.append((float(x), float(y)))
                text = text.strip()
        out.append(pts)
    left = min(x for s in out for x, _ in s)
    out = [[(x - left, y) for x, y in s] for s in out]
    return out, max(x for s in out for x, _ in s)


def _seg_dist(p, a, b):
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def _on(p, stroke, eps):
    if len(stroke) == 1:
        return math.hypot(p[0] - stroke[0][0], p[1] - stroke[0][1]) < eps
    return any(_seg_dist(p, stroke[i], stroke[i + 1]) < eps for i in range(len(stroke) - 1))


def _cut(stroke, length):
    """The stroke with `length` taken off its start."""
    s = list(stroke)
    while len(s) > 1 and length > 0:
        (ax, ay), (bx, by) = s[0], s[1]
        d = math.hypot(bx - ax, by - ay)
        if d <= length:
            length -= d
            s.pop(0)
            continue
        f = length / d
        s[0] = (ax + (bx - ax) * f, ay + (by - ay) * f)
        length = 0
    return s


def bridged(strokes_, gap):
    """A stencil's bridges: each end of a stroke that lies on an earlier stroke is drawn `gap` short."""
    if gap <= 0:
        return strokes_
    out = []
    for j, s in enumerate(strokes_):
        if len(s) > 1:
            if any(_on(s[0], strokes_[i], 0.35) for i in range(j)):
                s = _cut(s, gap)
            if any(_on(s[-1], strokes_[i], 0.35) for i in range(j)):
                s = _cut(s[::-1], gap)[::-1]
        out.append(s)
    return out


def coverage(segs, dots, w, h, half, butt):
    """[h][w] of 0..1: how much of each pixel the strokes cover. `segs` are ((x1, y1), (x2, y2)) in pixels,
    `dots` (x, y) points (square with butt ends, else round), `half` the half weight; butt: square ends
    (the joins inside a stroke are rounded either way: every inner point is also a dot)."""
    cov = [[0.0] * w for _ in range(h)]
    pad = half + 1.5
    for a, b in segs:
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:                    # a point left by a bridge's cut: nothing to draw
            continue
        ux, uy = dx / L, dy / L
        for y in range(max(0, int(min(a[1], b[1]) - pad)), min(h, int(max(a[1], b[1]) + pad) + 1)):
            for x in range(max(0, int(min(a[0], b[0]) - pad)), min(w, int(max(a[0], b[0]) + pad) + 1)):
                px, py = x + 0.5 - a[0], y + 0.5 - a[1]
                along = px * ux + py * uy
                across = abs(px * uy - py * ux)
                if butt:
                    out = max(-along, along - L)
                    c = max(0.0, min(1.0, half - across + 0.5)) * max(0.0, min(1.0, 0.5 - out))
                else:
                    t = max(0.0, min(L, along))
                    d = math.hypot(px - t * ux, py - t * uy)
                    c = max(0.0, min(1.0, half - d + 0.5))
                if c > cov[y][x]:
                    cov[y][x] = c
    for cx, cy in dots:
        for y in range(max(0, int(cy - pad)), min(h, int(cy + pad) + 1)):
            for x in range(max(0, int(cx - pad)), min(w, int(cx + pad) + 1)):
                px, py = x + 0.5 - cx, y + 0.5 - cy
                d = max(abs(px), abs(py)) if butt else math.hypot(px, py)
                c = max(0.0, min(1.0, half - d + 0.5))
                if c > cov[y][x]:
                    cov[y][x] = c
    return cov


class Pen:
    """How a look draws the skeleton. Sizes are pixels of the 320x200 grid (glyphs are drawn RES times finer).

    cap, small     the height of a capital and of a small capital (lowercase) in the menus
    weight         the stroke's weight at `cap` (it scales with the size drawn)
    gap            a stencil's bridge, as a part of the weight (0: strokes join)
    butt           square stroke ends (else round)
    edge           a dark edge round the ink, in pixels (0: none)
    track          the space between letters, as a part of the weight
    spacing        the menus' line spacing
    light, dark    the grey of the ink and of its edge in the glyphs (the menu's text colour maps them)
    """
    cap, small, weight, gap, butt, edge, track, spacing = 15, 11, 3.0, 0, False, 0.75, 0.6, 17
    light, dark = 236, 24

    def size(self, cap):
        """(weight, gap, edge, track) at a capital height of `cap` px; the edge does not grow with the size."""
        f = cap / self.cap
        w = self.weight * f
        return w, self.gap * w, self.edge, self.track * w

    def glyph(self, ch, cap, res=RES, top=None, height=None, small=None, ink=None):
        """The glyph of `ch` as an Img: capitals `cap` px high on the 320 grid (a lowercase letter `small`
        px high), drawn at `res` pixels per grid pixel; its top `top` px above the cap line (default: the
        edge), `height` px high in all. ink: None for a grey glyph (light ink, dark edge), else (ink, edge)
        colours to draw it in directly. Returns (Img, advance in grid px)."""
        w_, gap, edge, track = self.size(cap)
        small = small if small is not None else cap * self.small / self.cap
        c = cap
        if ch.islower():
            c = small
            w_ *= 0.86 + 0.14 * small / cap             # small capitals: a little lighter than the capitals
            gap = self.gap * w_
        top = edge + 0.5 if top is None else top
        if ch == " ":
            return None, SPACE * (cap - w_) / 10 + track
        ss, width = strokes(ch)
        s = (c - w_) / 10                                   # grid px per skeleton unit
        base = top + cap                                    # the baseline, from the image's top
        ss = bridged(ss, gap / s if s else 0)
        lead = edge + track / 2 + w_ / 2
        wpx = lead * 2 + width * s
        hpx = height if height is not None else base + w_ * 0.5 + edge + 0.25 * cap
        W, H = max(1, math.ceil(wpx * res)), max(1, math.ceil(hpx * res))
        segs, dots, joins = [], [], []
        for st in ss:
            pts = [((lead + x * s) * res, (base - w_ / 2 - (10 - y) * s) * res) for x, y in st]
            if len(pts) == 1:
                dots.append(pts[0])
            segs += [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
            joins += pts[1:-1]

        def cover(half):
            cov = coverage(segs, dots, W, H, half * res, self.butt)
            if self.butt and joins:             # the bends inside a stroke are round, so that they have no notch
                more = coverage([], joins, W, H, half * res, False)
                cov = [[max(a, b) for a, b in zip(r1, r2)] for r1, r2 in zip(cov, more)]
            return cov
        body = cover(w_ / 2)
        rim = cover(w_ / 2 + edge) if edge else body
        im = self.paint(body, rim, W, H, ch, ink)
        return im, wpx

    def paint(self, body, rim, W, H, ch, ink):
        """The glyph's pixels from the coverage of its ink (body) and of its edge (rim)."""
        im = Img(W, H, (0, 0, 0, 0))
        for y in range(H):
            for x in range(W):
                a = max(body[y][x], rim[y][x])
                if a <= 0:
                    continue
                f = body[y][x] / a
                if ink is None:
                    v = round(self.dark + (self.light - self.dark) * f)
                    im.set(x, y, (v, v, v, round(255 * a)))
                else:
                    c = tuple(round(e + (i - e) * f) for i, e in zip(ink[0], ink[1]))
                    im.set(x, y, c + (round(255 * a),))
        return im


def glyph_set():
    """Every character the font has."""
    return sorted(set(SKELETON) | {c.lower() for c in SKELETON if c.isalpha()})


def font(pen, name):
    """{pk3 path: bytes} of a GZDoom font folder fonts/<name>/: one PNG per code point and font.inf."""
    out = {}
    folder = f"fonts/{name.lower()}/"
    h = None
    for ch in glyph_set():
        im, adv = pen.glyph(ch, pen.cap)
        if h is None:
            h = im.h
        assert im.h == h, (ch, im.h, h)
        out[f"{folder}{ord(ch):04X}.png"] = im.png()
    _, space = pen.glyph(" ", pen.cap)
    out[f"{folder}font.inf"] = (f"// Ajar's menu font (tools/gfx_title.py; the pen: tools/gfx_title{LOOK}.py)\n"
                                f"Scale {RES}\nKerning 0\nSpaceWidth {round(space)}\n"
                                f"FontHeight {pen.spacing}\n").encode()
    return out


_widths = {}


def width(pen, text, cap=None, small=None):
    """The width of `text` in grid px, as the font draws it (rounded as the engine rounds a glyph's
    width when its cap is the menu's)."""
    cap = cap or pen.cap
    total = 0
    for ch in text:
        key = (id(pen), ch, cap, small)
        if key not in _widths:
            im, adv = pen.glyph(ch, cap, small=small)
            _widths[key] = round(adv) if im is None else (im.w / RES if cap == pen.cap else adv)
        total += _widths[key]
    return total


def write(im, pen, text, x, y, cap, ink, res=RES, small=None):
    """Draws `text` onto im (at `res` per grid px) with its cap line at grid (x, y); ink = (ink, edge)
    colours. Returns the x after it, on the grid."""
    for ch in text:
        g, adv = pen.glyph(ch, cap, res=res, small=small, ink=ink)
        if g is not None:
            e = pen.size(cap)[2] + 0.5
            ox, oy = round(x * res), round((y - e) * res)
            for gy in range(g.h):
                for gx in range(g.w):
                    p = g.px[gy * g.w + gx]
                    if p[3]:
                        _over(im, ox + gx, oy + gy, p)
        x += adv
    return x


def _over(im, x, y, p):
    if not (0 <= x < im.w and 0 <= y < im.h):
        return
    q = im.px[y * im.w + x]
    a = p[3] / 255
    im.px[y * im.w + x] = [round(p[i] * a + q[i] * (1 - a)) for i in range(3)] + [max(q[3], p[3])]


def paste(im, src, x, y):
    """src over im with its top left at pixel (x, y)."""
    for sy in range(src.h):
        for sx in range(src.w):
            p = src.px[sy * src.w + sx]
            if p[3]:
                _over(im, x + sx, y + sy, p)


def shrink(src, w, h):
    """src scaled down to w x h by averaging (for the help page's small pictures of the game's art)."""
    out = Img(w, h, (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            x1, x2 = x * src.w / w, (x + 1) * src.w / w
            y1, y2 = y * src.h / h, (y + 1) * src.h / h
            acc, n = [0, 0, 0, 0], 0
            for sy in range(int(y1), max(int(y1) + 1, math.ceil(y2))):
                for sx in range(int(x1), max(int(x1) + 1, math.ceil(x2))):
                    p = src.px[min(src.h - 1, sy) * src.w + min(src.w - 1, sx)]
                    for i in range(4):
                        acc[i] += p[i]
                    n += 1
            out.set(x, y, tuple(round(v / n) for v in acc))
    return out


def scaled(name, im, res=RES):
    """A TEXTURES entry that shows the graphic graphics/<name>H.png (drawn `res` times finer) as <name>."""
    return (f"graphic {name}, {im.w}, {im.h}\n{{\n\tXScale {res}\n\tYScale {res}\n"
            f"\tPatch \"graphics/{name}H.png\", 0, 0\n}}\n")


# --- words -------------------------------------------------------------------------------------------
QUIT = ["Leaving? Shut the door behind you.", "Checking out so soon?", "Leave it ajar and go?",
        "The doors will keep. Go?", "Nothing follows you out. Leave?",
        "You can always come back the way you came. Quit?"]
MENU = [("AJAR_M_NEWGAME", "New Game", "n", "PlayerclassMenu"), ("AJAR_M_LOADGAME", "Load Game", "l", "LoadGameMenu"),
        ("AJAR_M_SAVEGAME", "Save Game", "s", "SaveGameMenu"), ("AJAR_M_OPTIONS", "Options", "o", "OptionsMenu"),
        ("AJAR_M_RULES", "House Rules", "h", "ReadThisMenu"), ("AJAR_M_QUIT", "Quit", "q", "QuitMenu")]
WORDS = dict(AJAR_M_SKILL="How long are you staying?", AJAR_M_EPISODE="Which way in?",
             AJAR_M_CLASS="Who are you?", AJAR_M_LOAD="Load Game", AJAR_M_SAVE="Save Game",
             DOSY="(Y to leave, N to stay)")
RULES = ["A door remembers where it leads. Its colour and its sign say where.",
         "USE a door to take it down and carry it. One at a time.",
         "USE an empty frame to hang it there.",
         "Whatever can come through a door will. It works both ways.",
         "The way out has no colour."]
# What the player can do with a door (src/zscript/ajar.zs, AjarDoor.Used, AjarHandler.UseFrame, TakeLeaning):
# USE on a leaning door takes it (one at a time); USE on a frame hangs the carried door there, takes the hung
# one down, or swaps the two; there is no way to put a carried door down but in a frame.
CONTROLS = ("USE is Doom's open key. USE on a hung door while you carry one swaps the two; a carried door "
            "is put down only in a frame. Everything else is Doom's.")


def wrap(pen, text, room, cap, small):
    """`text` in lines no wider than `room` grid px."""
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if line and width(pen, trial, cap, small) > room:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def skills():
    """The skills' names, as src/mapinfo.txt gives them (the skill menu lists them in the look's font)."""
    import re
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "mapinfo.txt")) as f:
        text = f.read()
    return re.findall(r'\nskill \w+\s*\{\s*Name = "([^"]+)"', text)


def language():
    lines = ["", "// The title and the menus (tools/gfx_title.py, AJAR_TITLE)"]
    for i, q in enumerate(QUIT):
        lines.append(f'AJAR_QUIT{i + 1} = "{q}";')
    for key, text, _, _ in MENU:
        lines.append(f'{key} = "{text}";')
    for key, text in WORDS.items():
        lines.append(f'{key} = "{text}";')
    return "\n".join(lines) + "\n"


def menudef(L, C, B, logo):
    """MENUDEF: the list menus that show Doom's own graphics, in the font and colours of the lettering's
    look L, the cursor of C, laid out for the backdrop of B (its MENU_X, LOGO_X, LOGO_Y, MENU_TOP if it
    has them: menus at the left; else centred)."""
    pen = L.pen
    font = f'Font "{L.FONT}", "{L.NORMAL}", "{L.SELECTED}"'
    cx, cy = C.CURSOR_AT
    sel = f'Selector "AJCUR0", {cx}, {cy}'
    logo_h = logo.h / RES
    top = getattr(B, "MENU_TOP", round(logo_h + 8))
    items = max(width(pen, text) for _, text, _, _ in MENU)
    x = getattr(B, "MENU_X", None)
    x = round(160 - items / 2) if x is None else x
    out = [f"// Made by tools/gfx_title.py for look {LOOK} (AJAR_TITLE): the list menus in Ajar's own lettering",
           "// (the options menus are GZDoom's, coloured by gameinfo's menufontcolor_*). Menus must keep the",
           "// engine's names and links (MainMenu, MainMenuTextOnly, PlayerclassMenu, EpisodeMenu, SkillMenu,",
           "// LoadGameMenu, SaveGameMenu, ReadThisMenu, QuitMenu, OptionsMenu).",
           "", "DEFAULTLISTMENU", "{", f"\t{font}", f"\t{sel}", f"\tLineSpacing {pen.spacing}", "}", ""]
    for name in ("MainMenu", "MainMenuTextOnly"):
        out += [f'LISTMENU "{name}"', "{", f"\t{font}", f"\t{sel}", f"\tLineSpacing {pen.spacing}",
                f'\tStaticPatchCentered {getattr(B, "LOGO_X", 160)}, {getattr(B, "LOGO_Y", 2)}, "AJLOGO"', f"\tPosition {x}, {top}"]
        out += [f'\tTextItem "${key}", "{hot}", "{to}"' for key, _, hot, to in MENU]
        out += ["}", ""]
    skill_top = 46
    sx = round(160 - max(width(pen, n) for n in skills()) / 2)
    head = lambda key, y: f'\tStaticTextCentered 160, {y}, "${key}"'
    if getattr(B, "MENU_X", None) is not None:          # a backdrop whose menus stand at the left: these too
        sx = B.MENU_X
        head = lambda key, y: f'\tStaticText {B.MENU_X + cx}, {y}, "${key}"'
    out += ['ListMenu "PlayerclassMenu"', "{", '\tNetgameMessage "$NEWGAME"', f"\t{font}", f"\t{sel}",
            head("AJAR_M_CLASS", 15), "\tPosition 48, 63", '\tPlayerDisplay 220, 63, "20 00 00", "80 00 40"',
            "\tMouseWindow 0, 220", "}", "",
            'ListMenu "EpisodeMenu"', "{", '\tNetgameMessage "$NEWGAME"', f"\t{font}", f"\t{sel}",
            f"\tLineSpacing {pen.spacing}", head("AJAR_M_EPISODE", 26), f"\tPosition {sx}, {skill_top + 12}", "}", "",
            'ListMenu "SkillMenu"', "{", f"\t{font}", f"\t{sel}", f"\tLineSpacing {pen.spacing}",
            head("AJAR_M_SKILL", 26), f"\tPosition {sx}, {skill_top + 12}", "}", "",
            'ListMenu "LoadGameMenu"', "{", '\tNetgameMessage "$LOADNET"', f"\t{font}", '\tCaptionItem "$AJAR_M_LOAD"',
            "\tPosition 80,40", '\tClass "LoadMenu"', "\tSize Clean", "}", "",
            'ListMenu "SaveGameMenu"', "{", f"\t{font}", '\tCaptionItem "$AJAR_M_SAVE"', "\tPosition 80,40",
            '\tClass "SaveMenu"', "\tSize Clean", "}", ""]
    return "\n".join(out) + "\n"


def textcolo(*looks):
    out = [f"// The colours of the title's looks (tools/gfx_title<n>.py: COLOURS)"]
    colours = {}
    for L in looks:
        colours.update(L.COLOURS)
    for name, (dark, light) in colours.items():
        out += [name, "{", f"\t{dark} {light}", "Console:", f"\t{dark} {light} 0 256", "Flat:", f"\t{light}", "}", ""]
    return "\n".join(out) + "\n"


def gameinfo(L, P, backdrop_kind):
    o = P.OPTIONS
    lines = ["", f"// The title and the menus, look {LOOK} (tools/gfx_title.py, AJAR_TITLE): appended at build time",
             "gameinfo", "{",
             '\ttitlemusic = "AJM_LGHT"                // "Light Under the Door" (tools/music.py; MAP19 plays it)',
             '\tinfopage = "AJHELP"',
             "\tquitmessages = " + ", ".join(f'"$AJAR_QUIT{i + 1}"' for i in range(len(QUIT))),
             '\tquitsound = "ajar/take"',
             f'\tpausesign = "AJPAUSE"',
             f'\tmenufontcolor_title = "{o["title"]}"', f'\tmenufontcolor_label = "{o["label"]}"',
             f'\tmenufontcolor_value = "{o["value"]}"', f'\tmenufontcolor_action = "{o["action"]}"',
             f'\tmenufontcolor_header = "{o["header"]}"', f'\tmenufontcolor_highlight = "{o["highlight"]}"',
             f'\tmenufontcolor_selection = "{o["selection"]}"',
             f'\tmenuslidercolor = "{o["slider"]}"', f'\tmenusliderbackcolor = "{o["sliderback"]}"',
             f'\tdimcolor = "{P.DIM[0]}"', f"\tdimamount = {P.DIM[1]}",
             '\tMenuDelegateClass = "AjarMenuDelegate"     // src/zscript/title.zs: the cursor\'s two frames']
    if backdrop_kind == "picture":                    # a still title: no demos, and the menu opens by itself
        lines += ['\ttitlepage = "AJTITLE"', "\ttitletime = 30000",
                  '\tAddEventHandlers = "AjarTitlePageHandler"     // src/zscript/title.zs']
    lines.append("}")
    return "\n".join(lines) + "\n"


# --- the help page -----------------------------------------------------------------------------------
def help_page(L, P):
    """The help page (AJHELP, 320x200 at RES): the notice on the back of a hotel-room door. The layout is
    shared; the ground, the sheet, the lettering and the ink come from the looks of `page` and
    `lettering` (P and L)."""
    W, H = 320 * RES, 200 * RES
    im = P.page_ground(W, H)
    box = (34, 8, 286, 192)
    P.page_sheet(im, tuple(v * RES for v in box))
    pen = copy.copy(L.pen)                  # dark on paper: no edge, and set a little closer
    pen.edge, pen.track = 0, pen.track * 0.7
    ink, head, num = P.PAGE["ink"], P.PAGE["head"], P.PAGE["rule"]
    x1, y1, x2, y2 = box
    title = "NOTICE TO GUESTS"
    cap = 11
    write(im, pen, title, 160 - width(pen, title, cap) / 2, y1 + 9, cap, head)
    rule_line = lambda y: im.rect((x1 + 12) * RES, y * RES, (x2 - 12) * RES, y * RES + RES, head[0])
    rule_line(y1 + 25)
    cap2, small2, step = 8, 6.5, 10.5
    tx, room = x1 + 25, (x2 - 49) - (x1 + 25)
    y = y1 + 32
    tops = []
    for n, rule in enumerate(RULES):
        tops.append(y)
        write(im, pen, f"{n + 1}.", x1 + 12, y, cap2, num, small=small2)
        for line in wrap(pen, rule, room, cap2, small2):
            write(im, pen, line, tx, y, cap2, ink, small=small2)
            y += step
        y += 4
    # the pictures, the game's own art: RED and BLUE by the first rule, GREEN by the second, the empty
    # frame by the third
    lw, lh = 13, 19
    for pic, gx, k in ((gfx.door(1), x2 - 42, 0), (gfx.door(2), x2 - 27, 0), (gfx.door(3), x2 - 34, 1),
                       (gfx.empty_frame(), x2 - 34, 2)):
        gy = round(tops[k] - 1 if k < 2 else tops[k] - 4)
        if k == 1:
            gy = round(max(gy, tops[0] + lh + 4))
        if P.PAGE.get("pics"):
            im.rect((gx - 1) * RES, (gy - 1) * RES, (gx + lw + 1) * RES, (gy + lh + 1) * RES, ink[0])
        paste(im, shrink(pic, lw * RES, lh * RES), gx * RES, gy * RES)
    y = round(max(y, tops[2] + lh + 4) + 1)
    rule_line(y)
    y += 5
    for line in wrap(pen, CONTROLS, (x2 - 12) - (x1 + 12), 6.5, 5.5):
        write(im, pen, line, x1 + 12, y, 6.5, ink, small=5.5)
        y += 9
    assert y <= y2 + 2, ("the help page's words do not fit", y)
    return im


# --- the whole -----------------------------------------------------------------------------------------
def enlarge(im, k):
    """im k times larger, nearest neighbour."""
    out = Img(im.w * k, im.h * k)
    out.px = [list(im.px[(y // k) * im.w + x // k]) for y in range(im.h * k) for x in range(im.w * k)]
    return out


def flat(im, ground):
    """im over a ground colour (for the specimens)."""
    out = Img(im.w, im.h, ground)
    paste(out, im, 0, 0)
    return out


DARK, LIGHT = (24, 22, 24), (226, 222, 212)       # the specimens' grounds


def specimens(n, folder):
    """The look board's close-ups of look n into folder (tools/title_shots.sh): the logo, the cursor's
    frames and a line of the lettering in the menu's colours, each on a dark and on a light ground,
    4 times the 320 grid, nearest neighbour."""
    L = look(n)
    files = {}
    logo = L.logo()
    cur = L.cursor()
    for gname, g in (("dark", DARK), ("light", LIGHT)):
        files[f"logo{n}_{gname}.png"] = enlarge(flat(logo, g), 4 // RES)
        for k, c in enumerate(cur):
            files[f"cursor{n}_{k}_{gname}.png"] = enlarge(flat(c, g), 4)
        for which in ("NORMAL", "SELECTED"):
            files[f"lettering{n}_{which.lower()}_{gname}.png"] = enlarge(specimen(n, g, getattr(L, which)), 4 // RES)
    for name, im in files.items():
        with open(os.path.join(folder, name), "wb") as f:
            f.write(im.png())
    return sorted(files)


def specimen(n, ground, colour):
    """A specimen line of look n's lettering ("NEW GAME  Just visiting  0123456789") in one of its menu
    colours (a COLOURS name) on a ground colour, drawn at RES."""
    L = look(n)
    pen = L.pen
    text = "NEW GAME  Just visiting  0123456789"
    dark, light = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in L.COLOURS[colour])
    w = width(pen, text) + 16
    im = Img(round(w * RES), round((pen.cap + 14) * RES), ground)
    write(im, pen, text, 8, 7, pen.cap, (light, dark))
    return im


def make():
    """{pk3 path: bytes} of everything the switch puts in; the keys "mapinfo.txt+", "language.txt+" and
    "textures.txt+" are text to append to those files. {} when the switch is off."""
    if not LOOK:
        return {}
    p = parts()
    L, C, P, B, G = (look(p[k]) for k in ("lettering", "cursor", "page", "backdrop", "logo"))
    out = font(L.pen, L.FONT)
    tex = []
    logo = G.logo()
    out["graphics/AJLOGOH.png"] = logo.png()
    tex.append(scaled("AJLOGO", logo))
    frames = C.cursor()
    for k, f in enumerate(frames):
        out[f"graphics/AJCUR{k}.png"] = f.png()
    pause = L.pause()
    out["graphics/AJPAUSEH.png"] = pause.png()
    tex.append(scaled("AJPAUSE", pause))
    page = help_page(L, P)
    out["graphics/AJHELPH.png"] = page.png()
    tex.append(scaled("AJHELP", page))
    kind, *rest = B.backdrop()
    mapinfo = gameinfo(L, P, kind)
    if kind == "map":
        wad, lines = rest
        out["maps/TITLEMAP.wad"] = wad
        mapinfo += ("\nDoomEdNums\n{\n\t20200 = AjarTitleCamera          // src/zscript/title.zs\n"
                    "\t20201 = AjarTitleSpot\n}\n")
        mapinfo += ('\n// The title (tools/map_title.py): the menu opens over it by itself (src/zscript/title.zs)\n'
                    'map TITLEMAP "Ajar"\n{\n\tmusic = "AJM_LGHT"\n\tnointermission\n'
                    '\tEventHandlers = "AjarTitleHandler"\n' + "".join(f"\t{l}\n" for l in lines) + "}\n")
    else:
        pic, = rest
        out["graphics/AJTITLEH.png"] = pic.png()
        tex.append(scaled("AJTITLE", pic))
    out["menudef.txt"] = menudef(L, C, B, logo).encode()
    out["textcolo.txt"] = textcolo(L, P).encode()
    out["gameinfo.txt"] = ('// Made by tools/gfx_title.py (AJAR_TITLE): the window\'s name. No IWAD line: the IWAD is\n'
                           '// still the one given with -iwad.\nSTARTUPTITLE = "Ajar"\n').encode()
    out["mapinfo.txt+"] = mapinfo.encode()
    out["language.txt+"] = language().encode()
    out["textures.txt+"] = ("\n// The title's graphics, drawn finer than the 320 grid (tools/gfx_title.py)\n"
                            + "".join(tex)).encode()
    return out
