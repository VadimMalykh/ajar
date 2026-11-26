"""The clocked door's leaf and its frame's trim, in three looks to choose from
(PLAN.md, "Look: the clocked door and its frame's trim"). gfx.CLOCKDOOR (the
build's AJAR_CLOCKDOOR) picks one; 0 is the art as it was (gfx.clocked_door,
gfx_then.clock_trim) and is the default until Vadim chooses.

  1  Long-case clock: walnut with a grain and a moulded edge; a brass bezel and
     an ivory dial with roman-like ticks over brass spandrels; the lower panel
     glazed, the pendulum and two weights behind the glass. Trim: walnut, a
     brass inlay and graduations.
  2  Station clock: black enamel, a thin ivory edge line; a large white dial
     with bold black ticks and hands and a red second hand; in the lower panel
     a small second dial, the same face dimmed (the other time). Trim: black
     and ivory, graduated as the edge of such a dial.
  3  Ivory, done properly: deep cream, shaded (never above about 215), a heavy
     brass edge, brass-framed panels with a shadow line, a dial of twice the
     old one's area in a brass bezel, a small brass escutcheon. Trim: cream,
     brass bands, dark hour ticks.

leaf(look) is the 64x96 leaf (gfx.py makes the sprites AJDT, AJNT and the
texture AJDR10 from it); trim(look) is (wall, flat): AJCKTR (64x64, laid on a
frame's reveal, 16 deep, so only a 16-wide slice of it is ever seen) and
AJCKTF (the reveal's floor and head, a 64x16 strip of the flat in either
direction). Both repeat every 16 across, so any slice shows all of it.
"""
import math
import random

from gfx import Img, shade

INK = (34, 28, 24)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def line(im, x0, y0, x1, y1, c, w=1):
    """A straight stroke w pixels thick."""
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for k in range(n + 1):
        x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
        for dx in range(w):
            for dy in range(w):
                im.set(int(round(x - (w - 1) / 2 + dx)), int(round(y - (w - 1) / 2 + dy)), c)


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def ring(im, cx, cy, r1, r2, c, lit=0.35):
    """A metal ring between radii r1 and r2, lit from the top left: bright on
    that side of its outer half, its inner edge in shadow there."""
    for y in range(int(cy - r2) - 1, int(cy + r2) + 2):
        for x in range(int(cx - r2) - 1, int(cx + r2) + 2):
            d = math.hypot(x - cx, y - cy)
            if r1 <= d <= r2:
                a = math.atan2(y - cy, x - cx)
                towards = math.cos(a - math.radians(225))          # 1 at the top left
                mid = (r1 + r2) / 2
                f = 1 + lit * towards * (1 if d >= mid else -0.8)
                if d > r2 - 0.8:
                    f *= 0.72                                       # its outer lip
                im.set(x, y, shade(c, f))


def face(im, cx, cy, r, c, shadow=0.86, seed=0):
    """A dial's face: a disc, a little darker under the bezel's top left lip."""
    rnd = random.Random(seed)
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                a = math.atan2(y - cy, x - cx)
                f = 1 + rnd.uniform(-0.012, 0.012)
                if d > r - 2.2 and math.cos(a - math.radians(225)) > 0.2:
                    f *= shadow
                im.set(x, y, shade(c, f))


def ticks(im, cx, cy, r_out, hour, quarter, ink, minute=None, minute_ink=None):
    """Hour ticks: each (length, width) inward from r_out; the quarters
    `quarter`; `minute` the radius of a dot for each minute that is not an hour."""
    for k in range(12):
        ln, w = quarter if k % 3 == 0 else hour
        x0, y0 = polar(cx, cy, r_out, k * 30)
        x1, y1 = polar(cx, cy, r_out - ln + 1, k * 30)
        line(im, x0, y0, x1, y1, ink, w)
    if minute:
        for k in range(60):
            if k % 5:
                x, y = polar(cx, cy, minute, k * 6)
                im.set(int(round(x)), int(round(y)), minute_ink or ink)


def hands(im, cx, cy, hour_len, min_len, ink, w_hour=2, w_min=2, tail=0):
    """Ten past ten."""
    for deg, ln, w in ((305, hour_len, w_hour), (60, min_len, w_min)):
        x1, y1 = polar(cx, cy, ln, deg)
        x0, y0 = polar(cx, cy, -tail, deg)
        line(im, x0, y0, x1, y1, ink, w)


def grained(im, x1, y1, x2, y2, c, seed, f=1.0):
    """Walnut: a wavy vertical grain, its darker lines, a little noise."""
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6)
    for y in range(y1, y2):
        for x in range(x1, x2):
            u = x + 2.2 * math.sin(y * 0.055 + x * 0.17 + ph) + 1.2 * math.sin(y * 0.19 + ph * 2)
            g = 0.5 + 0.5 * math.sin(u * 1.1)
            v = f * (0.9 + 0.16 * g + rnd.uniform(-0.035, 0.035))
            if (u * 0.31 + 0.6 * math.sin(y * 0.03 + ph)) % 1 < 0.09:
                v *= 0.74                                          # a dark line of the grain
            im.set(x, y, shade(c, v))


def bevel(im, x1, y1, x2, y2, hi, lo, d=1):
    im.rect(x1, y1, x2, y1 + d, hi)
    im.rect(x1, y1, x1 + d, y2, hi)
    im.rect(x1, y2 - d, x2, y2, lo)
    im.rect(x2 - d, y1, x2, y2, lo)


# === 1: the long-case clock ==================================================================================
WALNUT = (104, 64, 38)
BRASS1 = (190, 150, 70)
DIAL1 = (214, 202, 170)


def leaf1():
    im = Img(64, 96, WALNUT)
    grained(im, 0, 0, 64, 96, WALNUT, 101)
    # the moulded edge: a dark arris, a bead catching the light, a hollow, a step down to the field
    for i, f in enumerate((0.42, 1.38, 1.12, 0.66)):
        bevel(im, i, i, 64 - i, 96 - i, shade(WALNUT, f), shade(WALNUT, f * (0.62 if i else 1)))
    # the upper panel: the hood's dial board, sunk, with the brass bezel and spandrels
    bevel(im, 7, 6, 57, 54, shade(WALNUT, 0.5), shade(WALNUT, 1.35), 2)
    grained(im, 9, 8, 55, 52, WALNUT, 102, 0.86)
    for sx, sy in ((10, 9), (54, 9), (10, 51), (54, 51)):         # brass spandrels in the corners: a quarter fan
        for y in range(-7, 8):
            for x in range(-7, 8):
                px, py = sx + x, sy + y
                if not (9 <= px < 55 and 8 <= py < 52):
                    continue
                dx, dy = abs(px - sx), abs(py - sy)
                d = math.hypot(dx, dy)
                if d <= 7:
                    ray = (int(math.degrees(math.atan2(dy, dx + 0.01))) // 15) % 2
                    f = 0.5 if d > 6.2 else (1.2 if ray else 0.88) - d * 0.03
                    im.set(px, py, shade(BRASS1, f))
    cx, cy = 32, 30
    im.disc(cx + 1, cy + 1, 21, shade(WALNUT, 0.45))                 # the bezel's shadow on the board
    ring(im, cx, cy, 17.5, 21, BRASS1, 0.42)
    face(im, cx, cy, 17.4, DIAL1, 0.84, 103)
    for r in (16, 11):                                               # the chapter ring between two thin circles
        for k in range(360):
            x, y = polar(cx, cy, r, k)
            im.set(int(round(x)), int(round(y)), shade(INK, 1.6))
    for k in range(12):                                              # roman-like hours: one bar, the quarters two
        for off in ((-3.5, 3.5) if k % 3 == 0 else (0,)):
            x0, y0 = polar(cx, cy, 15.5, k * 30 + off)
            x1, y1 = polar(cx, cy, 11.8, k * 30 + off)
            line(im, x0, y0, x1, y1, INK, 1)
        if k % 3 == 0:                                               # and a serif over them, as on a numeral
            x0, y0 = polar(cx, cy, 15.2, k * 30 - 6)
            x1, y1 = polar(cx, cy, 15.2, k * 30 + 6)
            line(im, x0, y0, x1, y1, INK, 1)
    hands(im, cx, cy, 8, 14, (30, 30, 46), 2, 1, tail=2)             # blued steel
    for deg, r in ((305, 6), (60, 11)):                              # the hands' spade and its open loop
        x, y = polar(cx, cy, r, deg)
        im.disc(x, y, 1.4, (30, 30, 46))
    im.disc(cx, cy, 1.6, shade(BRASS1, 1.1))
    # the lower panel: glazed; behind the glass, dark, the pendulum and the weights
    bevel(im, 7, 59, 57, 91, shade(WALNUT, 0.5), shade(WALNUT, 1.35), 2)
    bevel(im, 9, 61, 55, 89, shade(BRASS1, 1.2), shade(BRASS1, 0.6), 1)       # a brass glazing bead
    rnd = random.Random(104)
    for y in range(62, 88):
        for x in range(10, 54):
            im.set(x, y, shade((34, 24, 18), 0.9 + 0.25 * (1 - (y - 62) / 26) + rnd.uniform(-0.04, 0.04)))
    for wx, wy in ((18, 74), (46, 69)):                              # the weights on their cables
        im.rect(wx, 62, wx + 1, wy, shade(BRASS1, 0.8))
        for x in range(wx - 4, wx + 5):
            t = (x - (wx - 4) + 0.5) / 9
            f = 0.55 + 0.75 * math.sin(math.pi * min(1, t * 1.15))
            for y in range(wy, wy + 12):
                im.set(x, y, shade(BRASS1, max(0.5, f)))
        im.rect(wx - 4, wy, wx + 5, wy + 1, shade(BRASS1, 1.3))
    im.rect(32, 62, 33, 79, shade(BRASS1, 0.85))                     # the pendulum's rod and its bob
    im.disc(32, 81, 6.3, shade(BRASS1, 0.62))
    im.disc(32, 81, 5.4, BRASS1)
    im.disc(31, 80, 3.2, shade(BRASS1, 1.18))
    im.disc(30, 79, 1.3, shade(BRASS1, 1.35))
    for k in range(18):                                              # the glass: a glint across it
        x, y = 13 + k, 87 - k
        if 10 <= x < 54 and 62 <= y < 88:
            im.set(x, y, mix(im.px[y * 64 + x][:3], (200, 200, 190), 0.35))
            im.set(x + 1, y, mix(im.px[y * 64 + x + 1][:3], (200, 200, 190), 0.2))
    # the lock: a brass escutcheon and its key
    im.rect(50, 52, 56, 61, shade(BRASS1, 0.6))
    im.rect(50, 52, 55, 60, BRASS1)
    im.rect(50, 52, 55, 53, shade(BRASS1, 1.3))
    im.disc(52, 55, 1, INK)
    im.rect(52, 55, 53, 58, INK)
    return im


def trim1():
    wall = Img(64, 64, WALNUT)
    grained(wall, 0, 0, 64, 64, (100, 60, 36), 110, 0.9)
    for x0 in range(0, 64, 16):
        for y in range(64):
            wall.set(x0 + 1, y, shade(BRASS1, 1.0))                  # a brass inlay line beside each mouth
            wall.set(x0 + 2, y, shade(BRASS1, 0.62))
            wall.set(x0 + 14, y, shade(WALNUT, 0.55))
        for y in range(0, 64, 4):                                    # graduations off it: quarters, hours
            ln = 11 if y % 32 == 0 else 7 if y % 16 == 0 else 4
            c = BRASS1 if y % 16 == 0 else shade(INK, 1.2)
            wall.rect(x0 + 3, y, x0 + 3 + ln, y + 1, c)
            if y % 16 == 0:
                wall.rect(x0 + 3, y + 1, x0 + 3 + ln, y + 2, shade(WALNUT, 0.5))
    flat = Img(64, 64, WALNUT)
    grained(flat, 0, 0, 64, 64, (100, 60, 36), 111, 0.9)
    graduated_grid(flat, BRASS1, shade(BRASS1, 0.6), shade(INK, 1.2))
    return wall, flat


def graduated_grid(im, line_c, line_lo, tick_c):
    """A rule along every 16th row and column with graduations off it every 4:
    any 16-wide strip of it, either way, shows a rule and its marks."""
    for k in range(0, 64, 16):
        for i in range(64):
            im.set(i, k, line_c)
            im.set(i, k + 1, line_lo)
            im.set(k, i, line_c)
            im.set(k + 1, i, line_lo)
        for i in range(0, 64, 4):
            if i % 16 == 0:
                continue
            ln = 4 if i % 8 == 0 else 2
            im.rect(i, k + 2, i + 1, k + 2 + ln, tick_c)
            im.rect(k + 2, i, k + 2 + ln, i + 1, tick_c)
        for i in range(0, 64, 16):
            im.disc(k + 8, i + 8, 1, line_c)                         # a pin in each square


# === 2: the station clock ====================================================================================
ENAMEL = (30, 32, 36)
EDGE2 = (214, 206, 182)
DIAL2 = (226, 224, 216)
STEEL = (150, 154, 160)
RED2 = (196, 40, 30)


def enamel(im, x1, y1, x2, y2, c, seed):
    """Black enamel: a soft sheen falling from the top left, a little noise."""
    rnd = random.Random(seed)
    for y in range(y1, y2):
        for x in range(x1, x2):
            s = math.exp(-((x * 0.8 + y * 0.35 - 30) / 16) ** 2)     # a broad diagonal sheen
            im.set(x, y, shade(c, 1 + 0.55 * s + rnd.uniform(-0.04, 0.04)))


def station_dial(im, cx, cy, r, dim=1.0, second=True):
    """A railway clock's face: a steel bezel, a white face, bold bars for the
    hours and a mark for each minute, black bar hands, a red second hand with
    its disc. dim < 1: the same face in the dark."""
    ring(im, cx, cy, r - 2.2, r + 0.4, shade(STEEL, dim), 0.45)
    face(im, cx, cy, r - 2.3, shade(DIAL2, dim), 0.9, 200 + r)
    ink = shade((16, 16, 18), 1 if dim >= 1 else 1.8)
    big = r >= 16
    ticks(im, cx, cy, r - 3.2, (round(r * 0.26), 2 if big else 1), (round(r * 0.3), 3 if big else 2), ink,
          r - 3.6 if big else None)
    hands(im, cx, cy, r * 0.5, r * 0.78, ink, 3 if big else 2, 2 if big else 1, tail=r * 0.14)
    if second:
        red = shade(RED2, max(dim, 0.55))
        x1, y1 = polar(cx, cy, r * 0.62, 205)
        x0, y0 = polar(cx, cy, -r * 0.22, 205)
        line(im, x0, y0, x1, y1, red, 1)
        x, y = polar(cx, cy, r * 0.52, 205)
        im.disc(x, y, 2.2 if big else 1.2, red)
    im.disc(cx, cy, 1.5 if big else 1, ink)


def leaf2():
    im = Img(64, 96, ENAMEL)
    enamel(im, 0, 0, 64, 96, ENAMEL, 201)
    bevel(im, 0, 0, 64, 96, (88, 90, 96), (10, 10, 12), 1)           # the leaf's steel edge
    bevel(im, 1, 1, 63, 95, (60, 62, 68), (16, 16, 18), 1)
    im.frame(3, 3, 61, 93, EDGE2, 1)                                 # the thin ivory line round it
    # the upper half: the great dial, nearly the leaf's width
    cx, cy = 32, 29
    im.disc(cx + 1, cy + 2, 26, (12, 12, 14))                         # its shadow on the enamel
    station_dial(im, cx, cy, 25.5)
    # the lower panel: sunk, and in it the second dial, the same face dimmed
    bevel(im, 9, 60, 55, 89, (12, 12, 14), (70, 72, 78), 1)
    enamel(im, 10, 61, 54, 88, shade(ENAMEL, 0.8), 202)
    im.frame(11, 62, 53, 87, shade(EDGE2, 0.55), 1)
    im.disc(33, 75, 11.5, (10, 10, 12))
    station_dial(im, 32, 74, 11.2, 0.6)
    # a steel handle
    im.rect(53, 55, 58, 58, (40, 40, 44))
    im.rect(53, 54, 58, 57, STEEL)
    im.rect(53, 54, 58, 55, shade(STEEL, 1.35))
    im.rect(55, 52, 58, 59, shade(STEEL, 0.75))
    im.rect(55, 52, 58, 53, shade(STEEL, 1.2))
    return im


def trim2():
    wall = Img(64, 64, (214, 210, 198))
    wall.noise(3, 210)
    for x0 in range(0, 64, 16):
        wall.rect(x0, 0, x0 + 2, 64, (22, 22, 26))                   # the dial's black rim at each mouth
        wall.rect(x0 + 2, 0, x0 + 3, 64, (120, 120, 124))
        wall.rect(x0 + 14, 0, x0 + 16, 64, (22, 22, 26))
        for y in range(0, 64, 4):                                    # a mark for every minute, a bar each fifth
            if y % 16 == 0:
                wall.rect(x0 + 3, y, x0 + 12, y + 3, (18, 18, 20))
            else:
                wall.rect(x0 + 3, y + 1, x0 + 7, y + 2, (40, 40, 44))
        wall.rect(x0 + 11, 0, x0 + 12, 64, (40, 40, 44))             # the minute track's inner line
    flat = Img(64, 64, (214, 210, 198))
    flat.noise(3, 211)
    graduated_grid(flat, (22, 22, 26), (110, 110, 114), (40, 40, 44))
    return wall, flat


# === 3: ivory, done properly =================================================================================
CREAM = (176, 158, 118)
BRASS3 = (164, 122, 50)
DIAL3 = (200, 190, 164)


def cream(im, x1, y1, x2, y2, c, seed, top=1.08, bottom=0.9):
    """Cream paint: lighter at the top, darker at the foot, a soft noise."""
    rnd = random.Random(seed)
    for y in range(y1, y2):
        t = (y - y1) / max(1, y2 - y1 - 1)
        for x in range(x1, x2):
            im.set(x, y, shade(c, top + (bottom - top) * t + rnd.uniform(-0.02, 0.02)))


def leaf3():
    im = Img(64, 96, CREAM)
    cream(im, 0, 0, 64, 96, CREAM, 301, 1.08, 0.9)
    # the heavy brass edge: four pixels, lit on the top and left
    for i, (hi, lo) in enumerate(((0.62, 0.45), (1.2, 0.62), (1.05, 0.78), (0.95, 0.7))):
        bevel(im, i, i, 64 - i, 96 - i, shade(BRASS3, hi), shade(BRASS3, lo))
    for y1, y2 in ((7, 55), (60, 90)):
        im.rect(8, y1, 56, y2, shade(BRASS3, 0.55))                  # a brass frame round each panel
        bevel(im, 8, y1, 56, y2, shade(BRASS3, 1.15), shade(BRASS3, 0.6), 1)
        bevel(im, 9, y1 + 1, 55, y2 - 1, shade(BRASS3, 0.95), shade(BRASS3, 0.75), 1)
        cream(im, 10, y1 + 2, 54, y2 - 2, shade(CREAM, 0.95), 302 + y1, 1.02, 0.92)
        im.rect(10, y1 + 2, 54, y1 + 4, shade(CREAM, 0.66))          # the shadow line under the frame's top
        im.rect(10, y1 + 2, 12, y2 - 2, shade(CREAM, 0.74))          # and its left side
        im.rect(10, y1 + 2, 54, y1 + 3, shade(CREAM, 0.56))
    cx, cy = 32, 31
    im.disc(cx + 1, cy + 2, 23, shade(CREAM, 0.62))                  # the bezel's shadow
    ring(im, cx, cy, 19.7, 22.9, BRASS3, 0.3)
    face(im, cx, cy, 19.7, DIAL3, 0.82, 303)
    for k in range(360):                                             # a thin minute track
        x, y = polar(cx, cy, 17.7, k)
        im.set(int(round(x)), int(round(y)), shade(INK, 2.6))
    ticks(im, cx, cy, 18.6, (4, 1), (6, 2), INK, 17.7, shade(INK, 1.3))
    hands(im, cx, cy, 10, 15, INK, 2, 2, tail=2)
    for deg, r in ((305, 9), (60, 14)):                              # the hands' tips
        x, y = polar(cx, cy, r, deg)
        im.disc(x, y, 1, INK)
    im.disc(cx, cy, 2.2, shade(BRASS3, 0.9))
    im.disc(cx, cy, 1, (150, 40, 30))
    # a small brass escutcheon between the panels, and the knob
    im.rect(48, 52, 58, 64, shade(BRASS3, 0.45))
    im.rect(48, 52, 57, 63, BRASS3)
    bevel(im, 48, 52, 57, 63, shade(BRASS3, 1.25), shade(BRASS3, 0.65), 1)
    im.disc(52, 55, 2, shade(BRASS3, 0.55))
    im.disc(52, 55, 1.4, shade(BRASS3, 1.2))
    im.disc(52, 60, 1, INK)
    im.rect(52, 60, 53, 62, INK)
    return im


def trim3():
    wall = Img(64, 64, CREAM)
    cream(wall, 0, 0, 64, 64, CREAM, 310, 1.0, 1.0)
    for x0 in range(0, 64, 16):
        wall.rect(x0, 0, x0 + 3, 64, BRASS3)                         # a brass band at each mouth, lit on one side
        wall.rect(x0, 0, x0 + 1, 64, shade(BRASS3, 1.18))
        wall.rect(x0 + 2, 0, x0 + 3, 64, shade(BRASS3, 0.6))
        wall.rect(x0 + 3, 0, x0 + 4, 64, shade(CREAM, 0.7))
        wall.rect(x0 + 14, 0, x0 + 16, 64, shade(BRASS3, 0.82))
        for y in range(0, 64, 8):                                    # the hours: dark ticks, every fourth heavy
            if y % 32 == 0:
                wall.rect(x0 + 4, y, x0 + 13, y + 3, BRASS3)
                wall.rect(x0 + 4, y + 3, x0 + 13, y + 4, shade(BRASS3, 0.55))
            else:
                wall.rect(x0 + 5, y + 1, x0 + 11, y + 3, INK)
    flat = Img(64, 64, CREAM)
    cream(flat, 0, 0, 64, 64, CREAM, 311, 1.0, 1.0)
    graduated_grid(flat, BRASS3, shade(BRASS3, 0.6), INK)
    return wall, flat


def leaf(look):
    return (None, leaf1, leaf2, leaf3)[look]()


def trim(look):
    return (None, trim1, trim2, trim3)[look]()
