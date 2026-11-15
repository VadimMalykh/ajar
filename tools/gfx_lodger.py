"""Candidate looks for the lodger (see AJAR_LODGER in gfx.py and the board in
design/lodger-board.html).

  1 Shadow        a flat hole in the room with a green rim
  2 Guest         long coat, hat and suitcase
  3 Missing door  the door that ought to hang in the frame
  4 Knocker       a door-knocker for a face and one great fist
  5 Reach         mostly arms, in white gloves
  6 Shadow guest  the guest's outline drawn as the shadow

Every look has the same seven frames, 64x76 with the feet at the bottom
centre: A/B walking, C arm up, D striking, E dead, F/G coming out of a frame.

  python3 tools/gfx_lodger.py OUT   writes OUT/<look>/<frame>.png and OUT/sheet.png
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gfx import Img, shade

W, H = 64, 76
FRAMES = "ABCDEFG"
NAMES = {1: "Shadow", 2: "Guest", 3: "Missing door", 4: "Knocker", 5: "Reach", 6: "Shadow guest"}

DARK, EDGE, LITE = (44, 42, 46), (20, 18, 22), (72, 68, 78)      # the empty frame's dark
BRASS, SCREW = (190, 170, 110), (60, 50, 30)                     # its hinge plates
VOID, RIM = (10, 9, 14), (140, 214, 146)                         # the shadow, and the knock's green
GLOW = (216, 255, 208)
GLOVE, CUFF = (236, 232, 218), (170, 166, 156)


class Art(Img):
    def __init__(self, w=W, h=H):
        super().__init__(w, h, (0, 0, 0, 0))

    def solid(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.px[y * self.w + x][3] > 0

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            yc, xs = y + 0.5, []
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                if (y1 <= yc) != (y2 <= yc):
                    xs.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for xa, xb in zip(xs[::2], xs[1::2]):
                for x in range(int(round(xa)), int(round(xb))):
                    self.set(x, y, c)

    def line(self, x1, y1, x2, y2, c, t=2):
        n = int(max(abs(x2 - x1), abs(y2 - y1))) * 2 + 1
        for i in range(n + 1):
            x, y = x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n
            x0, y0 = int(round(x - t / 2)), int(round(y - t / 2))
            self.rect(x0, y0, x0 + t, y0 + t, c)

    def path(self, pts, c, t=2):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            self.line(x1, y1, x2, y2, c, t)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    self.set(x, y, c)

    def ring(self, cx, cy, r, c, sy=1.0, t=2):
        for i in range(120):
            a = i * math.pi / 60
            x, y = int(round(cx + r * math.cos(a))), int(round(cy + r * sy * math.sin(a)))
            self.rect(x, y, x + t, y + t, c)

    def rim(self, c):
        """One pixel of c around the outside of everything drawn so far."""
        todo = [(x, y) for y in range(self.h) for x in range(self.w) if not self.solid(x, y)
                and any(self.solid(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in todo:
            self.set(x, y, c)

    def edge(self, c):
        """The outermost pixel of everything drawn so far becomes c."""
        todo = [(x, y) for y in range(self.h) for x in range(self.w) if self.solid(x, y)
                and not all(self.solid(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in todo:
            self.set(x, y, c)

    def dissolve(self, y0, y1, seed=7):
        """Fades to nothing between rows y0 and y1; nothing is left below y1."""
        rnd = random.Random(seed)
        for y in range(max(0, y0), self.h):
            p = (y - y0) / max(1, y1 - y0)
            for x in range(self.w):
                if rnd.random() < p:
                    self.px[y * self.w + x] = [0, 0, 0, 0]

    def skew(self, k, pivot=66):
        out = Art(self.w, self.h)
        for y in range(self.h):
            dx = int(round((pivot - y) * k))
            for x in range(self.w):
                if self.solid(x, y):
                    out.set(x + dx, y, self.px[y * self.w + x])
        return out

    def paste(self, other, dx=0, dy=0):
        for y in range(other.h):
            for x in range(other.w):
                if other.solid(x, y):
                    self.set(x + dx, y + dy, other.px[y * other.w + x])


def plate(a, x, y, w=3, h=7, c=BRASS):
    """A hinge plate with its two screws: every look's eye."""
    a.rect(x, y, x + w, y + h, c)
    a.set(x + w // 2, y + 1, SCREW)
    a.set(x + w // 2, y + h - 2, SCREW)


# --- 1: the shadow ---------------------------------------------------------

def shadow(fr):
    a = Art()
    if fr == "E":                                    # a door-shaped patch on the floor
        a.poly([(7, 75), (57, 75), (48, 65), (16, 65)], VOID)
        a.rect(24, 69, 30, 71, shade(BRASS, 0.6))
        a.rect(34, 69, 40, 71, shade(BRASS, 0.6))
        a.rim(shade(RIM, 0.6))
        return a
    b = fr in "BG"
    hx = 34 if fr == "D" else 32
    a.ellipse(hx, 12, 7, 9, VOID)
    a.poly([(hx - 5, 17), (hx + 5, 17), (45, 24), (43, 52), (21, 52), (19, 24)], VOID)
    a.poly([(21, 52), (43, 52), (41, 62), (23, 62)], VOID)
    for x1, x2, tip, ty in ((22, 30, 27, 72), (27, 37, 31, 75), (34, 42, 38, 71)) if b else \
                           ((22, 30, 24, 75), (27, 37, 33, 70), (34, 42, 41, 75)):
        a.poly([(x1, 60), (x2, 60), (tip, ty)], VOID)

    def hand(x, y, dy, t=1):
        for dx in (-4, 0, 4):
            a.line(x, y, x + dx, y + dy, VOID, t)

    if fr != "F":
        lx, ly = (13, 57) if b else (14, 54)
        a.line(20, 25, lx, ly, VOID, 3)
        hand(lx, ly, 8)
        if fr == "C":
            a.line(44, 25, 54, 9, VOID, 3)
            hand(54, 9, -8)
        elif fr == "D":
            a.line(46, 25, 56, 38, VOID, 4)
            hand(56, 39, 11, 2)
        elif fr == "G":
            a.line(44, 25, 54, 40, VOID, 3)
            hand(54, 41, 9, 2)
        else:
            rx, ry = (51, 51) if b else (50, 54)
            a.line(44, 25, rx, ry, VOID, 3)
            hand(rx, ry, 8)
    plate(a, hx - 5, 8)
    plate(a, hx + 2, 8)
    a.rim(RIM)
    if fr == "F":
        a.dissolve(22, 52)
    elif fr == "G":
        a.dissolve(46, 78)
    else:
        a.dissolve(60, 92)
    return a


# --- 2 and 6: the guest ----------------------------------------------------

def case(a, x, y, w, h, body, flat):
    a.rect(x, y, x + w, y + h, body)
    a.rect(x + w // 2 - 3, y - 3, x + w // 2 + 3, y - 2, body if flat else EDGE)      # handle
    a.rect(x + w // 2 - 3, y - 3, x + w // 2 - 2, y, body if flat else EDGE)
    a.rect(x + w // 2 + 2, y - 3, x + w // 2 + 3, y, body if flat else EDGE)
    if not flat:
        a.frame(x, y, x + w, y + h, EDGE, 1)
        a.rect(x + 1, y + h // 2, x + w - 1, y + h // 2 + 1, LITE)
    a.rect(x + 2, y + 1, x + 4, y + 3, BRASS)
    a.rect(x + w - 4, y + 1, x + w - 2, y + 3, BRASS)


def guest(fr, flat=False):
    coat, edge, lite = (VOID, VOID, VOID) if flat else (DARK, EDGE, LITE)
    a = Art()
    if fr == "E":                                    # coat in a heap, hat and case left behind
        a.poly([(16, 75), (58, 75), (52, 67), (22, 67)], coat)
        a.rect(32, 63, 56, 66, coat)
        a.rect(37, 57, 51, 63, coat)
        if not flat:
            a.edge(edge)
            a.rect(38, 61, 50, 63, lite)
        case(a, 2, 63, 14, 12, coat, flat)
        a.diamond(27, 71, 2, BRASS)
        if flat:
            a.rim(shade(RIM, 0.6))
        return a
    step = 2 if fr in "BG" else 0
    if fr != "F":
        for x in (23 + step, 35 - step):
            a.rect(x, 64, x + 6, 74, edge)
            a.rect(x - 1, 73, x + 8, 76, edge)
    a.poly([(18, 26), (46, 26), (49, 66), (15, 66)], coat)
    a.poly([(21, 20), (43, 20), (46, 27), (18, 27)], coat)
    a.rect(27, 10, 37, 21, edge)                     # the face, in the hat's shadow
    a.rect(20, 8, 44, 11, coat)                      # brim
    a.rect(26, 1, 38, 2, coat)
    a.rect(25, 2, 39, 8, coat)
    if fr != "F":
        if fr == "C":                                # the case goes up
            a.poly([(15, 27), (20, 27), (13, 13), (8, 15)], coat)
        elif fr == "D":
            a.poly([(15, 27), (20, 27), (25, 44), (20, 46)], coat)
        else:
            a.poly([(14, 27), (19, 27), (16, 52), (11, 52)], coat)
            a.rect(11, 52, 16, 55, edge)
        a.poly([(45, 27), (50, 27), (53, 52), (48, 52)], coat)
        a.rect(48, 52, 53, 55, edge)
    if not flat:
        a.edge(edge)
        a.rect(25, 6, 39, 8, lite)                   # hat band
        a.rect(31, 22, 32, 66, edge)                 # coat front, belt, buttons
        a.rect(16, 44, 48, 46, edge)
        for y in (31, 38):
            a.rect(27, y, 29, y + 2, BRASS)
            a.rect(34, y, 36, y + 2, BRASS)
    plate(a, 28, 12, 3, 6)
    plate(a, 33, 12, 3, 6)
    if fr == "C":
        case(a, 1, 3, 15, 11, coat, flat)
    elif fr == "D":
        case(a, 12, 42, 26, 19, coat, flat)
        if flat:
            a.frame(12, 42, 38, 61, shade(RIM, 0.55), 1)
    elif fr != "F":
        case(a, 5, 58, 15, 12, coat, flat)
    if fr != "F":                                    # the room key and its fob
        a.rect(50, 55, 51, 59, BRASS)
        a.diamond(50, 62, 3, BRASS)
    if flat:
        a.rim(RIM)
    if fr == "F":
        a.dissolve(24, 50)
    elif fr == "G":
        a.dissolve(50, 80)
    return a


# --- 3: the missing door ---------------------------------------------------

def keyhole(a, x, y, lit=True, big=False):
    w, h = (9, 13) if big else (7, 11)
    a.rect(x, y, x + w, y + h, BRASS)
    c = GLOW if lit else SCREW
    a.rect(x + w // 2 - 1, y + 2, x + w // 2 + 2, y + 5, c)
    a.rect(x + w // 2, y + 5, x + w // 2 + 1, y + h - 2, c)


def missing_door(fr):
    a = Art()
    if fr == "E":                                    # flat on the floor, its light out
        a.poly([(4, 75), (48, 75), (58, 65), (14, 65)], DARK)
        a.noise(4, 31)
        a.edge(EDGE)
        a.poly([(10, 73), (25, 73), (32, 68), (17, 68)], shade(DARK, 0.75))
        a.poly([(30, 73), (45, 73), (52, 68), (37, 68)], shade(DARK, 0.75))
        a.rect(8, 74, 15, 76, BRASS)
        a.rect(36, 74, 43, 76, BRASS)
        a.rect(27, 66, 31, 68, SCREW)
        return a
    if fr == "D":                                    # falling on you
        a.poly([(11, 20), (53, 20), (47, 68), (17, 68)], DARK)
        a.noise(4, 31)
        a.rect(22, 68, 25, 76, EDGE)
        a.rect(39, 68, 42, 76, EDGE)
        a.poly([(13, 15), (51, 15), (53, 20), (11, 20)], LITE)
        a.line(15, 36, 6, 28, DARK, 3)
        a.line(49, 36, 58, 28, DARK, 3)
        a.edge(EDGE)
        a.poly([(17, 25), (47, 25), (45, 39), (19, 39)], shade(DARK, 0.75))
        a.poly([(20, 53), (44, 53), (43, 64), (21, 64)], shade(DARK, 0.75))
        plate(a, 13, 24, 4, 9)
        plate(a, 17, 56, 4, 9)
        keyhole(a, 39, 40, big=True)
        return a
    p = Art()
    p.rect(18, 6, 46, 66, DARK)
    p.noise(4, 31)
    p.frame(18, 6, 46, 66, EDGE, 2)
    for y1, y2 in ((10, 29), (44, 62)):
        p.rect(22, y1, 42, y2, shade(DARK, 0.75))
        p.frame(22, y1, 42, y2, EDGE, 1)
    plate(p, 18, 11, 4, 9)
    plate(p, 18, 51, 4, 9)
    keyhole(p, 37, 31)
    k = {"A": 0.06, "B": -0.06, "C": -0.1, "F": 0.0, "G": 0.05}[fr]
    top = int(round(36 * k))
    if fr != "F":
        for x in ((23, 39) if fr in "BG" else (25, 37)):
            a.rect(x, 64, x + 3, 76, EDGE)
            a.rect(x - 1, 74, x + 5, 76, EDGE)
        a.line(19 + top, 30, 10 + top, 45, EDGE, 2)
        a.rect(8 + top, 45, 12 + top, 49, DARK)
        if fr == "C":
            a.line(45 + top, 28, 57, 10, EDGE, 2)
            a.rect(55, 6, 60, 11, DARK)
        else:
            a.line(45 + top, 30, 54 + top, 45, EDGE, 2)
            a.rect(53 + top, 45, 57 + top, 49, DARK)
    a.paste(p.skew(k))
    return a


# --- 4: the knocker --------------------------------------------------------

def fist(s, cuff=True):
    f = Art(s + 2, s + 6)
    f.rect(1, 0, s - 1, s, DARK)
    f.rect(0, 1, s, s - 1, DARK)
    f.edge(EDGE)
    for i in (1, 2, 3):
        f.rect(i * s // 4, 1, i * s // 4 + 1, s // 3 + 1, EDGE)
    f.rect(2, s * 2 // 3, s - 3, s * 2 // 3 + 1, EDGE)
    for i in range(4):
        f.rect(i * s // 4 + 1, 1, (i + 1) * s // 4 - 1, 2, LITE)
    return f


def knocker(fr):
    a = Art()
    if fr == "E":
        a.poly([(8, 75), (40, 75), (36, 67), (13, 67)], DARK)
        a.edge(EDGE)
        a.paste(fist(16), 40, 59)
        a.ring(23, 71, 6, BRASS, 0.4)
        a.rect(13, 63, 21, 67, BRASS)
        return a
    step = 2 if fr in "BG" else 0
    if fr != "F":
        for x in (27 + step, 35 - step):
            a.rect(x, 56, x + 4, 75, DARK)
            a.rect(x - 1, 73, x + 6, 76, DARK)
        a.poly([(26, 23), (38, 23), (40, 57), (26, 57)], DARK)
        a.ellipse(32, 12, 8, 9, DARK)
        a.line(25, 27, 20, 46, DARK, 3)
        arm = {"A": (49, 46), "B": (50, 43), "C": (51, 16), "D": (38, 34), "G": (42, 36)}[fr]
        a.line(38, 27, arm[0], arm[1], DARK, 5)
        a.edge(EDGE)
        a.ellipse(32, 9, 5, 5, BRASS)                # the knocker: plate, two screws, ring
        a.rect(29, 7, 31, 9, SCREW)
        a.rect(34, 7, 36, 9, SCREW)
        a.rect(31, 12, 34, 15, BRASS)
        a.ring(31.5, 21, 6, BRASS)
    if fr == "A":
        a.rect(45, 45, 54, 48, BRASS)
        a.paste(fist(16), 42, 48)
    elif fr == "B":
        a.rect(46, 42, 55, 45, BRASS)
        a.paste(fist(16), 43, 45)
    elif fr == "C":
        a.rect(48, 17, 57, 20, BRASS)
        a.paste(fist(16), 45, 1)
    elif fr == "D":
        a.paste(fist(28), 19, 30)
    elif fr == "G":
        a.paste(fist(22), 34, 32)
        a.dissolve(52, 80)
    else:                                            # F: the fist comes first
        a.rect(28, 50, 38, 66, DARK)
        a.edge(EDGE)
        a.dissolve(52, 66)
        a.rect(27, 48, 39, 51, BRASS)
        a.paste(fist(22), 22, 26)
    return a


# --- 5: the reach ----------------------------------------------------------

def glove_down(a, x, y=76):
    a.rect(x - 2, y - 6, x + 2, y - 3, CUFF)
    a.rect(x - 4, y - 3, x + 4, y, GLOVE)
    a.rect(x - 2, y - 1, x - 1, y, CUFF)
    a.rect(x + 1, y - 1, x + 2, y, CUFF)


def glove_up(a, x, y):
    a.rect(x - 3, y, x + 3, y + 5, GLOVE)
    for dx in (-3, -1, 1):
        a.rect(x + dx, y - 5, x + dx + 1, y, GLOVE)
    a.rect(x + 3, y + 1, x + 5, y + 3, GLOVE)
    a.rect(x - 2, y + 5, x + 2, y + 7, CUFF)


def glove_big(a, x, y):
    g = Art(16, 20)
    g.rect(1, 7, 13, 19, GLOVE)
    for i in range(4):
        g.rect(1 + i * 3, 0 + (i % 2), 3 + i * 3, 8, GLOVE)
    g.rect(13, 10, 16, 14, GLOVE)
    g.edge(CUFF)
    a.paste(g, x - 7, y - 10)


def glove_jamb(a, left, y):
    x = 0 if left else 58
    a.rect(x, y, x + 6, y + 9, GLOVE)
    for dy in (2, 4, 6):
        a.rect(x + (2 if left else 0), y + dy, x + (6 if left else 4), y + dy + 1, CUFF)


def reach(fr):
    a = Art()
    by = 68 if fr == "E" else 34 if fr == "F" else 39 if fr == "B" else 40
    arms = {
        "A": [((25, 38), (12, 18), (6, 70)), ((26, 43), (17, 31), (19, 70)),
              ((39, 38), (52, 18), (58, 70)), ((38, 43), (47, 31), (45, 70))],
        "B": [((25, 37), (13, 15), (10, 62)), ((26, 42), (16, 33), (16, 70)),
              ((39, 37), (52, 20), (56, 70)), ((38, 42), (49, 29), (49, 62))],
        "C": [((25, 38), (15, 24), (10, 13)), ((26, 43), (15, 33), (13, 70)),
              ((39, 38), (49, 24), (54, 13)), ((38, 43), (49, 33), (51, 70))],
        "D": [((25, 40), (15, 34), (15, 46)), ((26, 43), (10, 28), (5, 70)),
              ((39, 40), (49, 34), (49, 46)), ((38, 43), (54, 28), (59, 70))],
        "E": [((25, 66), (13, 52), (21, 43)), ((28, 63), (23, 48), (29, 40)),
              ((39, 66), (51, 52), (43, 43)), ((36, 63), (41, 48), (35, 40))],
        "F": [((25, 32), (12, 26), (4, 22)), ((25, 36), (12, 44), (4, 50)),
              ((39, 32), (52, 26), (60, 22)), ((39, 36), (52, 44), (60, 50))],
        "G": [((25, 38), (13, 20), (9, 70)), ((26, 43), (12, 34), (4, 26)),
              ((39, 38), (51, 20), (55, 70)), ((38, 43), (52, 34), (60, 26))],
    }[fr]
    for pts in arms:
        a.path(list(pts), DARK, 3)
    a.ellipse(32, by, 9, 7, DARK)
    a.edge(EDGE)
    plate(a, 27, by - 3, 3, 6, shade(BRASS, 0.6) if fr == "E" else BRASS)
    plate(a, 34, by - 3, 3, 6, shade(BRASS, 0.6) if fr == "E" else BRASS)
    for i, pts in enumerate(arms):
        x, y = pts[2]
        front = i in (0, 2)
        if fr == "F" or (fr == "G" and not front):
            glove_jamb(a, i < 2, y - 4)
        elif fr == "C" and front:
            glove_up(a, x, y - 7)
        elif fr == "D" and front:
            glove_big(a, x, y + 6)
        elif fr == "E":
            a.rect(x - 2, y - 3, x + 3, y + 2, GLOVE)
            a.rect(x - 2, y + 2, x + 3, y + 3, CUFF)
        else:
            glove_down(a, x, y + 6)
    return a


# --- 7: smoke (second round) -------------------------------------------------
# Drawn four times as fine as the others and soft at the edges; the game shows
# it at a quarter scale and blended (see LodgerPortrait in ajar.zs).

SMOKE_SCALE = 4
_rnd = random.Random(5)
_grid = [[_rnd.random() for _ in range(64)] for _ in range(64)]


def _noise(x, y):
    xi, yi = math.floor(x), math.floor(y)
    fx, fy = x - xi, y - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    g = lambda i, j: _grid[j % 64][i % 64]
    top = g(xi, yi) + (g(xi + 1, yi) - g(xi, yi)) * fx
    bot = g(xi, yi + 1) + (g(xi + 1, yi + 1) - g(xi, yi + 1)) * fx
    return top + (bot - top) * fy


def _fbm(x, y):
    return (_noise(x, y) + 0.5 * _noise(2 * x, 2 * y) + 0.25 * _noise(4 * x, 4 * y)) / 1.75 * 2 - 1


def _cap(x, y, ax, ay, bx, by, ra, rb):
    dx, dy = bx - ax, by - ay
    ll = dx * dx + dy * dy
    t = 0 if ll == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / ll))
    return math.hypot(x - ax - dx * t, y - ay - dy * t) - (ra + (rb - ra) * t)


def smoke(fr):
    S = SMOKE_SCALE
    a = Art(W * S, H * S)
    sway = {"A": -2, "B": 2}.get(fr, 0)
    hx, hy, eye = 32, 13, True
    if fr == "D":                                    # lunging: bigger, both arms out
        hy = 17
        parts = [(32, hy, 32, hy, 9, 9), (32, 28, 32, 54, 14, 10), (32, 54, 31, 74, 10, 3),
                 (20, 30, 12, 43, 4, 3), (12, 43, 10, 52, 4, 5), (44, 30, 52, 43, 4, 3), (52, 43, 54, 52, 4, 5)]
    elif fr == "E":
        parts, eye = [(10, 72, 54, 72, 2, 3), (20, 70, 44, 70, 3, 3)], False
    else:
        parts = [(hx, hy, hx, hy, 7, 7), (32, 22, 32, 50, 11, 8), (32, 50, 32 + sway * 2, 74, 8, 2),
                 (22, 24, 15 - sway, 48, 3, 2), (15 - sway, 48, 13 - sway, 60, 2, 1)]
        if fr == "C":
            parts += [(42, 24, 50, 12, 3, 2), (50, 12, 53, 3, 2, 1)]
        elif fr == "G":
            parts += [(42, 24, 52, 38, 3, 2), (52, 38, 56, 46, 2, 2)]
        else:
            parts += [(42, 24, 49 - sway, 48, 3, 2), (49 - sway, 48, 51 - sway, 60, 2, 1)]
    phase = {"A": 0, "B": 3.1, "C": 6.3, "D": 9.7, "E": 13, "F": 1.5, "G": 4.4}[fr]
    core, haze = (9, 8, 13), (34, 52, 40)
    for j in range(H * S):
        y = (j + 0.5) / S
        fade = 1.0
        if fr == "F":
            fade = max(0.0, min(1.0, (46 - y) / 26))
        elif fr == "G":
            fade = max(0.2, min(1.0, (84 - y) / 40))
        if fade <= 0:
            continue
        for i in range(W * S):
            x = (i + 0.5) / S
            if fr == "E":
                d = min(_cap(x, y, *p) for p in parts)
            else:
                e = sum(math.exp(-_cap(x, y, *p) / 2.0) for p in parts)      # a soft union
                d = -2.0 * math.log(e) if e > 1e-9 else 99
            if d > 8:
                continue
            d += _fbm(x / 6 + phase, y / 6 - phase) * (1.2 + 3.2 * y / H)
            al = max(0.0, min(1.0, 0.5 - d / 3.0)) * fade
            if al <= 0.02:
                continue
            k = max(0.0, min(1.0, 1 + d / 3.0))      # towards the edge it thins to a green haze
            a.px[j * a.w + i] = [int(core[c] + (haze[c] - core[c]) * k) for c in range(3)] + [int(255 * al)]
    if eye:
        for ex in (hx - 5, hx + 2):
            for j in range((hy - 5) * S - 6, (hy + 2) * S + 6):
                for i in range(ex * S - 6, (ex + 3) * S + 6):
                    inside = ex * S <= i < (ex + 3) * S and (hy - 5) * S <= j < (hy + 2) * S
                    p = a.px[j * a.w + i]
                    if inside:
                        a.px[j * a.w + i] = [226, 204, 128, 255]
                    elif p[3]:                       # a little glow round each eye
                        a.px[j * a.w + i] = [min(255, p[0] + 60), min(255, p[1] + 52), min(255, p[2] + 24), p[3]]
    return a


def figure(look, fr):
    look = int(look)
    if look == 7:
        return smoke(fr)
    if look == 1:
        return shadow(fr)
    if look in (2, 6):
        return guest(fr, look == 6)
    if look == 3:
        return missing_door(fr)
    if look == 4:
        return knocker(fr)
    return reach(fr)


def make(out, look):
    """Adds the AJLG sprites of one candidate look to a pk3 file dict."""
    for fr in FRAMES:
        f = figure(look, fr)
        out[f"sprites/AJLG{fr}0.png"] = f.png(grab=(f.w // 2, f.h))


def sheet(scale=5):
    """Every look, every frame, for looking over."""
    im = Img((W + 4) * len(FRAMES) * scale, (H + 6) * 6 * scale, (206, 204, 198))
    for row, look in enumerate(range(1, 7)):
        for col, fr in enumerate(FRAMES):
            ox, oy = (col * (W + 4) + 2) * scale, (row * (H + 6) + 4) * scale
            if fr in "FG":                           # these two stand in a frame
                im.rect(ox, oy - 3 * scale, ox + W * scale, oy + H * scale, DARK)
            im.rect(ox, oy + H * scale, ox + W * scale, oy + (H + 1) * scale, (150, 70, 56))
            f = figure(look, fr)
            for y in range(H):
                for x in range(W):
                    if f.solid(x, y):
                        im.rect(ox + x * scale, oy + y * scale, ox + (x + 1) * scale, oy + (y + 1) * scale,
                                f.px[y * W + x][:3])
    return im


if __name__ == "__main__":
    dest = sys.argv[1]
    for look in range(1, 7):
        os.makedirs(os.path.join(dest, str(look)), exist_ok=True)
        for fr in FRAMES:
            with open(os.path.join(dest, str(look), fr + ".png"), "wb") as fh:
                fh.write(figure(look, fr).png())
    os.makedirs(os.path.join(dest, "7"), exist_ok=True)
    for fr in FRAMES:
        with open(os.path.join(dest, "7", fr + ".png"), "wb") as fh:
            fh.write(figure(7, fr).png())
    with open(os.path.join(dest, "sheet.png"), "wb") as fh:
        fh.write(sheet().png())
