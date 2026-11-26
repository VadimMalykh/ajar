"""MAP21's apparatus (tools/map_longrun.py, APPARATUS): the institute "then",
lit and full of devices, in three looks, all drawn; the map picks a look for
each group of parts. The walls, floors and ceilings are MAP11's (gfx_institute:
then look 2, Thaw; now look 3, Post Box) and stay.

  1 Lamps and Reels       a computing centre of the 1960s: cabinets in pale
                          grey-blue and cream enamel edged in aluminium, fields
                          of small round lamps, tape reels behind glass, white
                          keys, round green scope screens, orange, black plates
  2 Copper and Porcelain  a high-voltage hall: dark green hammered enamel, black
                          bakelite meters with white faces, knife switches,
                          copper windings and bus bars, white porcelain
                          insulators, red lamps, brass plates
  3 Glass and Mercury     a vacuum and optics laboratory: glass bulbs, tubes and
                          bell jars glowing violet and blue, nickel stands and
                          clamps, white ceramic, black slate, red rubber hose,
                          mercury columns, small dials

Every name is AJU<part><look> (no other family starts AJU).
Furniture (sides 64 wide; "aligned": laid by world position, seamless):
  CB<n><k> 64x128  a cabinet bank's front, k = A to D: four different cabinets,
                   each whole in its 64; the map gives each 64 of a bank's front
                   its own by world position (bank_front), so 256 never repeat
  CS 64x128        a bank's end panel        CT  its top (flat)
  RK 128x96        a goods rack's front (one face)    RS 64x96 its end (aligned)
  RT               its top (flat)
  OB 64x48         an optical bench's side (aligned)  OTA, OTB its top, two variants
  TK 64x256        a tank's face, floor to ceiling in one piece
  PM 64x48         a pump set's side (aligned)        PT its top
  BM 64x48         the belt's motor housing's side (aligned)  BT its top
  CN 64x48         a low console's side (aligned)     CK its top: keys and dials
Pictures, each drawn onto the room's own wall of look 2 (then), so that the
wall's bands run on through it (hang them at a multiple of 64, or give the
shift): 256 high, one to a wall piece, not aligned:
  SC 128  the machine's schematic: a door's outline within itself (hall, EX)
  PB 128  the pass and key board of the security post (vestibule, AR)
  WN 128  a wall newspaper (the pocket, CO)
  PP 64   a pipe run down to an open mouth (lab wall LA: the cellar's)
One of a kind, named by the wall they are on (AJU<part><wall><wall's look>):
  NT 64   the notice: EXPERIMENT 1 TOMORROW AT A QUARTER TO ... (NTEX2, NTAR2)
  CL 32   a tear-off calendar, one bold day; now the same page, yellowed
          (CLEX2 then, CLEX3 now)
Now's walls: ghost(): where a thing stood or hung, the look-3 wall shows a
rectangle of cleaner paint the size of it, bolt holes at its corners, here
and there a cut cable (AJUG<nn>; the map asks for them: GHOSTS).
Flats, one of a kind: DU2 a cable duct's chequer-plate covers then (32 wide
runs), DU3 the same duct now, covers gone, cables cut.
Sprites (decoration; things 20195 to 20198, src/zscript/apparatus.zs), frame
A, B, C the look 1, 2, 3:
  AJUA  S1 an instrument on a trolley, 40x56  (a scope; a meter set; a pump)
  AJUB  S2 a tall piece, 40x96  (a tape drive; a coil on insulators; a tube on a stand)
  AJUC  S3 a small thing on a desk  (a desk radio; a telephone; a glass of tea)
  AJUE  EM the beam's emitter, 40x72; D, E, F its wreck now in the same looks
"""
import math
import random
from contextlib import contextmanager

import gfx_institute as GI
from gfx import Img, shade, text, digit
from gfx_bus import blend, mix

LOOKS = (1, 2, 3)
NAMES = {1: "Lamps and Reels", 2: "Copper and Porcelain", 3: "Glass and Mercury"}

# --- the three looks' colours ------------------------------------------------------------------------------
GB, CREAM, ALU, INK = (168, 186, 200), (232, 226, 204), (204, 208, 212), (30, 30, 34)
AMBER, AMBER_OFF, GREEN, LRED = (255, 184, 60), (112, 82, 50), (110, 240, 130), (240, 72, 52)
KEY, ORANGE, SCOPE, TRACE = (240, 238, 230), (232, 118, 40), (28, 62, 46), (170, 255, 190)
HGREEN, BAK, FACE = (46, 84, 60), (28, 26, 24), (240, 234, 214)
COPPER, BRASS, PORC, WARN = (196, 110, 58), (210, 172, 80), (242, 240, 232), (226, 36, 26)
CER, NICKEL, SLATE = (234, 234, 228), (196, 202, 208), (36, 38, 46)
VIOLET, BLUE, HOSE, MERC = (186, 130, 255), (120, 170, 255), (184, 42, 36), (220, 224, 232)
RUST = (122, 70, 38)
BODY = {1: GB, 2: HGREEN, 3: CER}


def name(part, n):
    return f"AJU{part}{n}"


# === drawing helpers ======================================================================================
def fill(im, x1, y1, x2, y2, c, var=0.02, seed=0):
    rnd = random.Random(seed)
    for y in range(max(0, y1), min(im.h, y2)):
        for x in range(max(0, x1), min(im.w, x2)):
            im.set(x, y, shade(c, 1 + rnd.uniform(-var, var)))


def hammered(im, x1, y1, x2, y2, c, seed=0, s=6):
    """Hammer-tone enamel: dimples on a jittered grid, lit from the top left."""
    rnd = random.Random(seed)
    pts = {}
    for gy in range(y1 // s - 1, y2 // s + 2):
        for gx in range(x1 // s - 1, x2 // s + 2):
            pts[(gx, gy)] = (gx * s + rnd.uniform(0, s), gy * s + rnd.uniform(0, s))
    for y in range(max(0, y1), min(im.h, y2)):
        for x in range(max(0, x1), min(im.w, x2)):
            gx, gy = x // s, y // s
            best, bp = 1e9, (0, 0)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = pts[(gx + dx, gy + dy)]
                    d = (x - p[0]) ** 2 + (y - p[1]) ** 2
                    if d < best:
                        best, bp = d, p
            d = math.sqrt(best)
            lit = ((bp[0] - x) + (bp[1] - y)) / (d + 0.01) * min(1, d / 3)
            im.set(x, y, shade(c, 1 + 0.07 * lit + rnd.uniform(-0.015, 0.015)))


def bevel(im, x1, y1, x2, y2, c, d=1, up=True):
    """A raised (or sunk) panel's edges."""
    hi, lo = (shade(c, 1.3), shade(c, 0.55)) if up else (shade(c, 0.55), shade(c, 1.25))
    im.rect(x1, y1, x2, y1 + d, hi)
    im.rect(x1, y1, x1 + d, y2, hi)
    im.rect(x1, y2 - d, x2, y2, lo)
    im.rect(x2 - d, y1, x2, y2, lo)


def cyl_v(im, x1, y1, x2, y2, c, hi=1.35, lo=0.55):
    """A vertical cylinder (a column, a pipe): shaded across x, lit from the left."""
    w = max(1, x2 - x1)
    for x in range(x1, x2):
        t = (x - x1 + 0.5) / w
        f = lo + (hi - lo) * math.sin(math.pi * min(1, t * 1.15)) if t < 0.87 else lo + (hi - lo) * 0.35 * (1 - t) / 0.13
        f = max(lo, f)
        for y in range(y1, y2):
            im.set(x, y, shade(c, f))


def cyl_h(im, x1, y1, x2, y2, c, hi=1.35, lo=0.55):
    """A horizontal cylinder: shaded across y, lit from above."""
    h = max(1, y2 - y1)
    for y in range(y1, y2):
        t = (y - y1 + 0.5) / h
        f = lo + (hi - lo) * math.sin(math.pi * min(1, t * 1.2)) if t < 0.83 else lo + (hi - lo) * 0.3 * (1 - t) / 0.17
        f = max(lo, f)
        im.rect(x1, y, x2, y + 1, shade(c, f))


def glow(im, cx, cy, r, c, f=0.8):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(x - cx, y - cy) / r
            if d < 1 and 0 <= x < im.w and 0 <= y < im.h and im.px[y * im.w + x][3]:     # (not on a sprite's clear ground)
                blend(im, x, y, c, f * (1 - d) ** 1.6)


def lamp(im, cx, cy, r, c, lit=True, rim=None):
    if rim:
        im.disc(cx, cy, r + 1, rim)
    if lit:
        glow(im, cx, cy, r * 2.4, c, 0.35)
        im.disc(cx, cy, r, c)
        im.disc(cx - r * 0.35, cy - r * 0.35, max(0.6, r * 0.4), mix(c, (255, 255, 255), 0.7))
    else:
        im.disc(cx, cy, r, c)
        im.set(int(cx - r * 0.3), int(cy - r * 0.3), shade(c, 1.5))


def screw(im, x, y, c):
    im.set(x, y, shade(c, 0.45))
    im.set(x + 1, y, shade(c, 1.4))


def legend(im, s, cx, y, ground=INK, ink=(236, 236, 228)):
    """A small plate with a word on it, centred at cx, top at y (7 high)."""
    w = len(s) * 6 - 1
    x0 = cx - w // 2
    im.rect(x0 - 2, y, x0 + w + 2, y + 9, ground)
    text(im, s, x0, y + 2, ink, 1)


def needle_dial(im, cx, cy, r, rim, face=FACE, a=0.5, ink=(30, 30, 30), red=(200, 30, 24), arc=True):
    """A round meter face: ticks on an arc, a needle at a (0..1)."""
    im.disc(cx, cy, r, rim)
    im.disc(cx, cy, r - 1.6, face)
    if arc:
        for k in range(9):
            t = math.pi * (1.15 + 0.7 * k / 8)
            im.set(round(cx + (r - 3) * math.cos(t)), round(cy + (r - 3) * math.sin(t) + r * 0.25), ink)
    t = math.pi * (1.15 + 0.7 * a)
    for k in range(int(r * 0.95)):
        im.set(round(cx + k * math.cos(t)), round(cy + r * 0.25 + k * math.sin(t)), red)
    im.disc(cx, cy + r * 0.25, 1, ink)


def louvres(im, x1, y1, x2, y2, c, step=4):
    for y in range(y1, y2 - 1, step):
        im.rect(x1, y, x2, y + 1, shade(c, 0.45))
        im.rect(x1, y + 1, x2, y + 2, shade(c, 1.2))


def reel(im, cx, cy, r, metal=ALU, pack=(70, 52, 40), fullness=0.6):
    im.disc(cx, cy, r, shade(metal, 0.85))
    im.disc(cx, cy, r - 1, metal)
    im.disc(cx, cy, 3 + (r - 5) * fullness, pack)
    im.disc(cx, cy, 3.2, shade(metal, 0.9))
    im.disc(cx, cy, 1.3, INK)
    for k in range(3):                                           # the windows in the flange, over the pack
        a = k * 2 * math.pi / 3 + 0.5
        im.disc(cx + (r * 0.62) * math.cos(a), cy + (r * 0.62) * math.sin(a), r * 0.2, shade(metal, 0.4))


def glass_glint(im, x1, y1, x2, y2, f=0.22):
    """A pane's reflection: two light diagonals."""
    w = x2 - x1
    for i in range(min(w, y2 - y1)):
        for k, off in ((0, w // 3), (1, w // 3 + 4)):
            blend(im, x1 + off + i // 2 - i, y1 + i, (255, 255, 255), f if k == 0 else f * 0.6)


def bulb(im, cx, cy, r, glowc, neck=6, metal=NICKEL, inner=(24, 20, 36)):
    """A glass bulb on a metal cap, glowing inside (bulb over a dark ground)."""
    glow(im, cx, cy, r * 1.9, glowc, 0.35)
    im.disc(cx, cy, r, shade(glowc, 0.42))
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                blend(im, x, y, glowc, 0.85 * (1 - d / r) ** 1.2)
                if d > r - 1.2:
                    blend(im, x, y, (230, 236, 255), 0.55)
    im.disc(cx - r * 0.4, cy - r * 0.45, max(1, r * 0.18), (255, 255, 255))
    im.rect(int(cx - r * 0.35), int(cy + r - 1), int(cx + r * 0.35) + 1, int(cy + r + neck), metal)
    im.rect(int(cx - r * 0.35), int(cy + r - 1), int(cx - r * 0.35) + 1, int(cy + r + neck), shade(metal, 1.3))


def insulator(im, cx, y1, y2, w, c=PORC):
    """Porcelain: a stack of sheds, top to bottom."""
    y = y1
    while y < y2:
        cyl_v(im, int(cx - w / 2), y, int(cx + w / 2) + 1, min(y2, y + 2), c, 1.15, 0.6)
        cyl_v(im, int(cx - w / 3), min(y2, y + 2), int(cx + w / 3) + 1, min(y2, y + 4), c, 1.1, 0.55)
        y += 4


def coil(im, x1, y1, x2, y2, c=COPPER):
    """A winding seen from the side: turns across, shaded as a cylinder."""
    w = x2 - x1
    for x in range(x1, x2):
        t = (x - x1 + 0.5) / w
        f = 0.55 + 0.75 * math.sin(math.pi * t)
        for y in range(y1, y2):
            ff = f * (0.72 if (y - y1) % 3 == 2 else 1.0)
            im.set(x, y, shade(c, ff))


def hose(im, pts, c=HOSE, r=1.6):
    """A rubber hose through the points (a polyline, drawn thick)."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = int(max(abs(bx - ax), abs(by - ay)) * 2) + 1
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            im.disc(x, y, r, c)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = int(max(abs(bx - ax), abs(by - ay)) * 2) + 1
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            im.set(round(x - r * 0.4), round(y - r * 0.5), shade(c, 1.45))


def curve(a, b, sag, n=12):
    """Points of a hanging curve from a to b, sagging `sag` in the middle."""
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n + sag * math.sin(math.pi * i / n)) for i in range(n + 1)]


def mercury(im, x, y1, y2, level, glass=(190, 210, 220)):
    """A glass tube 3 wide from y1 to y2, mercury up to `level` (0..1)."""
    im.rect(x - 1, y1, x + 2, y2, shade(glass, 0.8))
    im.set(x - 1, y1, shade(glass, 0.6))
    top = int(y2 - (y2 - y1) * level)
    cyl_v(im, x - 1, top, x + 2, y2, MERC, 1.25, 0.55)
    im.rect(x - 1, top, x + 2, top + 1, (255, 255, 255))


# === the cabinet bank: four fronts a look ================================================================
def cab_body(n, seed):
    """A cabinet's front, 64x128: its look's body, edges and plinth."""
    im = Img(64, 128)
    c = BODY[n]
    if n == 2:
        hammered(im, 0, 0, 64, 128, c, seed)
    else:
        fill(im, 0, 0, 64, 128, c, 0.015, seed)
    if n == 1:                                                   # cream top band, aluminium edges, black plinth
        fill(im, 0, 0, 64, 12, CREAM, 0.01, seed + 1)
        im.rect(0, 0, 64, 2, ALU)
        im.rect(0, 12, 64, 13, shade(GB, 0.6))
        for x in (1, 61):
            cyl_v(im, x, 0, x + 2, 120, ALU, 1.2, 0.7)
    elif n == 2:                                                 # bakelite foot, rivets, a dark edge
        for x, y in ((4, 4), (59, 4), (4, 114), (59, 114)):
            im.disc(x, y, 1.2, shade(c, 1.5))
            im.set(x + 1, y + 1, shade(c, 0.5))
    else:                                                        # nickel edges, a black slate band at the top
        im.rect(0, 0, 64, 10, SLATE)
        im.rect(0, 10, 64, 11, NICKEL)
        for x in (1, 61):
            cyl_v(im, x, 0, x + 2, 120, NICKEL, 1.3, 0.65)
    im.rect(0, 0, 1, 128, shade(c, 0.4))                         # the seam between two cabinets
    im.rect(63, 0, 64, 128, shade(c, 0.4))
    foot = {1: (40, 42, 46), 2: BAK, 3: shade(NICKEL, 0.8)}[n]
    im.rect(0, 120, 64, 128, foot)
    im.rect(0, 120, 64, 121, shade(foot, 0.5) if n != 3 else (60, 62, 66))
    if n == 3:
        for x in range(4, 62, 6):
            im.rect(x, 123, x + 3, 126, shade(NICKEL, 0.6))
    return im


def cab1(k, seed):
    im = cab_body(1, seed)
    rnd = random.Random(seed)
    if k == "A":                                                 # a tape drive: two reels behind glass
        legend(im, "TAPE", 32, 2)
        im.rect(6, 16, 58, 70, shade(ALU, 0.8))
        im.rect(7, 17, 57, 69, (40, 46, 54))
        reel(im, 20, 34, 11, ALU, fullness=0.75)
        reel(im, 44, 34, 11, ALU, fullness=0.3)
        im.rect(20, 50, 45, 51, (90, 70, 50))                    # the tape between them, round the head
        im.rect(28, 54, 37, 64, shade(ALU, 0.9))
        im.rect(30, 56, 35, 58, INK)
        glass_glint(im, 7, 17, 57, 69)
        for i, x in enumerate(range(8, 56, 8)):                 # keys, one orange
            c = ORANGE if i == 4 else KEY
            im.rect(x, 76, x + 6, 84, shade(c, 0.7))
            im.rect(x, 76, x + 6, 82, c)
        for x, c in ((12, GREEN), (24, AMBER), (36, AMBER), (48, LRED)):
            lamp(im, x, 92, 2, c, rnd.random() < 0.7, (40, 40, 44))
        louvres(im, 8, 100, 56, 116, GB)
    elif k == "B":                                               # a field of lamps
        legend(im, "MEM", 32, 2)
        im.rect(5, 16, 59, 86, shade(ALU, 0.85))
        im.rect(6, 17, 58, 85, (46, 50, 58))
        for r in range(8):
            for col in range(6):
                x, y = 11 + col * 8.4, 22 + r * 8.2
                q = rnd.random()
                if q < 0.34:
                    lamp(im, x, y, 2.2, AMBER, True)
                elif q < 0.39:
                    lamp(im, x, y, 2.2, GREEN, True)
                elif q < 0.42:
                    lamp(im, x, y, 2.2, LRED, True)
                else:
                    lamp(im, x, y, 2.2, AMBER_OFF, False)
        for i, x in enumerate(range(7, 57, 7)):
            c = ORANGE if i in (0, 6) else KEY
            im.rect(x, 91, x + 5, 101, shade(c, 0.65))
            im.rect(x, 91, x + 5, 99, c)
        im.rect(6, 106, 58, 116, shade(GB, 0.8))
        legend(im, "07", 32, 107)
    elif k == "C":                                               # a scope and its knobs
        legend(im, "SCOPE", 32, 2)
        im.disc(32, 42, 20, CREAM)
        im.disc(32, 42, 19, shade(CREAM, 0.8))
        im.disc(32, 42, 16, SCOPE)
        for x in range(17, 48, 5):                               # the graticule
            for y in range(28, 57, 2):
                if (x - 32) ** 2 + (y - 42) ** 2 < 15 ** 2:
                    blend(im, x, y, (90, 140, 110), 0.5)
        for x in range(18, 47):
            y = 42 + 9 * math.sin((x - 18) * 0.42) * math.exp(-(x - 18) / 30)
            im.disc(x, y, 0.8, TRACE)
            glow(im, x, y, 2.5, TRACE, 0.15)
        im.disc(26, 34, 3, (255, 255, 255))
        blend(im, 25, 33, (255, 255, 255), 0.5)
        for x, a in ((14, 0.3), (32, 0.7), (50, 0.5)):
            im.disc(x, 74, 5, INK)
            im.disc(x, 74, 4, (60, 60, 64))
            im.rect(x - 1, 70, x + 1, 74, KEY)
        im.rect(26, 84, 38, 90, ORANGE)
        im.rect(26, 88, 38, 90, shade(ORANGE, 0.6))
        louvres(im, 8, 96, 56, 116, GB)
    else:                                                        # a printer: paper out of a slot, a keypad
        legend(im, "PRINT", 32, 2)
        im.rect(6, 18, 58, 30, shade(GB, 0.7))
        im.rect(8, 22, 56, 26, INK)
        for y in range(13, 22):                                 # the paper coming out
            im.rect(12, y, 52, y + 1, (244, 242, 232) if y % 6 else (214, 212, 204))
        for y in range(14, 21, 3):
            im.set(14, y, (150, 150, 150))
            im.set(49, y, (150, 150, 150))
        for r in range(4):
            for col in range(3):
                x, y = 9 + col * 10, 38 + r * 11
                c = ORANGE if (r, col) == (3, 2) else KEY
                im.rect(x, y, x + 8, y + 9, shade(c, 0.65))
                im.rect(x, y, x + 8, y + 7, c)
        for r, c in enumerate((GREEN, AMBER, AMBER, LRED)):
            lamp(im, 50, 42 + r * 11, 2.6, c, r != 2, (40, 40, 44))
        im.rect(6, 86, 58, 116, shade(GB, 0.9))
        bevel(im, 6, 86, 58, 116, GB)
        im.rect(28, 98, 36, 101, ALU)
    im.noise(2, seed + 9)
    return im


def cab2(k, seed):
    im = cab_body(2, seed)
    rnd = random.Random(seed)

    def plate(cx, y, w=24):
        im.rect(cx - w // 2, y, cx + w // 2, y + 6, BRASS)
        im.frame(cx - w // 2, y, cx + w // 2, y + 6, shade(BRASS, 0.6), 1)
        for x in range(cx - w // 2 + 3, cx + w // 2 - 3, 3):
            im.set(x, y + 3, shade(BRASS, 0.45))

    if k == "A":                                                 # two knife switches on slate
        plate(32, 8)
        im.rect(8, 18, 56, 104, SLATE)
        bevel(im, 8, 18, 56, 104, SLATE, 1, False)
        for cx in (21, 43):
            for y in (24, 80):                                   # porcelain blocks
                im.rect(cx - 6, y, cx + 7, y + 8, PORC)
                im.rect(cx - 6, y + 6, cx + 7, y + 8, shade(PORC, 0.7))
                im.rect(cx - 1, y + 2, cx + 2, y + 6, COPPER)
            cyl_v(im, cx - 2, 28, cx + 3, 84, COPPER)            # the blade, closed
            im.rect(cx - 2, 28, cx + 3, 30, shade(COPPER, 1.4))
            im.disc(cx + 0.5, 30, 4, BAK)                        # its handle
            im.disc(cx - 0.5, 29, 1.2, (120, 110, 100))
            cyl_v(im, cx - 1, 88, cx + 2, 104, COPPER)           # down to the bus
        im.disc(32, 112, 4, BAK)
        lamp(im, 32, 112, 3, WARN, True)
    elif k == "B":                                               # four bakelite meters, a rotary switch
        plate(32, 6)
        for cx, cy, a in ((17, 28, 0.3), (47, 28, 0.62), (17, 58, 0.48), (47, 58, 0.8)):
            im.disc(cx, cy, 13, BAK)
            im.disc(cx - 1, cy - 1, 12.5, (52, 48, 44))
            im.disc(cx, cy, 12, BAK)
            needle_dial(im, cx, cy, 10, BAK, FACE, a)
        im.disc(32, 90, 9, BAK)
        im.disc(32, 90, 7, (56, 52, 48))
        im.rect(31, 82, 33, 90, FACE)
        for k2 in range(5):
            a = math.pi * (1.1 + 0.2 * k2)
            im.set(round(32 + 12 * math.cos(a)), round(90 + 12 * math.sin(a)), FACE)
        for x in (12, 52):
            im.disc(x, 90, 3.5, BAK)
            lamp(im, x, 90, 2.6, WARN, x == 12)
        plate(32, 106, 30)
    elif k == "C":                                               # a winding behind a mesh
        plate(32, 6)
        im.rect(6, 16, 58, 104, (20, 22, 20))
        insulator(im, 32, 20, 32, 14)
        coil(im, 16, 34, 48, 86)
        im.rect(14, 33, 50, 35, shade(COPPER, 0.6))
        im.rect(14, 85, 50, 87, shade(COPPER, 0.6))
        insulator(im, 32, 88, 102, 14)
        for x in range(6, 58, 4):                                # the mesh over it
            for y in range(16, 104):
                blend(im, x, y, (90, 110, 96), 0.55)
        for y in range(16, 104, 4):
            for x in range(6, 58):
                blend(im, x, y, (90, 110, 96), 0.45)
        im.frame(6, 16, 58, 104, shade(HGREEN, 0.5), 2)
        lamp(im, 32, 112, 3, WARN, True, BAK)
    else:                                                        # bus bars on porcelain stand-offs
        plate(32, 6)
        im.rect(6, 16, 58, 108, SLATE)
        for x in (15, 30, 45):
            cyl_v(im, x, 18, x + 6, 106, COPPER, 1.45, 0.6)
            for y in (26, 62, 98):
                im.rect(x - 4, y - 2, x + 10, y + 3, PORC)
                im.rect(x - 4, y + 1, x + 10, y + 3, shade(PORC, 0.7))
        for i in range(16):                                       # the old warning: a red flash on white
            im.rect(32 - i // 2 - 1, 48 + i, 32 + i // 2 + 1, 49 + i, WARN)
        for i in range(3, 14):
            im.rect(32 - (i - 3) // 2, 49 + i, 32 + (i - 3) // 2, 50 + i, PORC)
        for x, y in ((33, 54), (31, 57), (33, 57), (31, 60)):
            im.rect(x - 1, y, x + 1, y + 3, WARN)
        lamp(im, 16, 114, 2.6, WARN, True, BAK)
        lamp(im, 48, 114, 2.6, WARN, False, BAK)
    im.noise(2, seed + 9)
    return im


def cab3(k, seed):
    im = cab_body(3, seed)
    rnd = random.Random(seed)

    def window(x1, y1, x2, y2):
        im.rect(x1 - 2, y1 - 2, x2 + 2, y2 + 2, NICKEL)
        im.rect(x1 - 1, y1 - 1, x2 + 1, y2 + 1, shade(NICKEL, 0.7))
        im.rect(x1, y1, x2, y2, (22, 20, 32))

    if k == "A":                                                 # a rectifier bulb, glowing violet
        window(8, 16, 56, 96)
        glow(im, 32, 50, 30, VIOLET, 0.45)
        bulb(im, 32, 50, 17, VIOLET, 10)
        for a in (-0.9, 0, 0.9):                                 # its arms
            ax = 32 + 22 * math.sin(a)
            for i in range(9):
                blend(im, round(32 + (ax - 32) * i / 9), 50 - i, (230, 220, 255), 0.6)
        im.rect(20, 77, 44, 82, NICKEL)
        im.rect(18, 82, 46, 86, shade(NICKEL, 0.8))
        glass_glint(im, 8, 16, 56, 96, 0.12)
        for x in (16, 32, 48):
            needle_dial(im, x, 108, 5, NICKEL, CER, 0.5 + (x - 32) / 64)
    elif k == "B":                                               # mercury columns against a scale, on slate
        im.rect(6, 14, 58, 104, SLATE)
        bevel(im, 6, 14, 58, 104, SLATE, 1, False)
        glow(im, 32, 60, 30, BLUE, 0.18)
        for i, (x, lv) in enumerate(((14, 0.72), (26, 0.4), (38, 0.86), (50, 0.55))):
            for y in range(18, 92, 4):
                im.rect(x + 3, y, x + (7 if y % 16 == 2 else 5), y + 1, (220, 222, 228))
            mercury(im, x, 18, 92, lv)
            im.disc(x + 0.5, 95, 4, (200, 214, 222))
            im.disc(x + 0.5, 95, 3, MERC)
            im.set(x - 1, 93, (255, 255, 255))
        im.rect(6, 100, 58, 104, NICKEL)
        hose(im, curve((14, 100), (50, 100), 12), HOSE, 1.5)
    elif k == "C":                                               # vacuum gauges on slate, hoses to a valve
        im.rect(6, 14, 58, 108, SLATE)
        for cx, cy, a in ((18, 28, 0.25), (46, 28, 0.7), (32, 54, 0.45)):
            needle_dial(im, cx, cy, 10, NICKEL, CER, a)
        im.rect(26, 74, 38, 84, NICKEL)                          # the valve
        cyl_h(im, 26, 74, 38, 84, NICKEL)
        im.rect(20, 70, 44, 72, HOSE)
        im.disc(32, 70, 3, HOSE)
        hose(im, curve((18, 39), (26, 79), 8), HOSE, 1.6)
        hose(im, curve((46, 39), (38, 79), 8), HOSE, 1.6)
        hose(im, curve((32, 84), (12, 104), 6), HOSE, 1.6)
        bulb(im, 46, 96, 7, BLUE, 3, NICKEL, (20, 24, 40))
    else:                                                        # a bell jar with a glowing filament
        im.rect(6, 14, 58, 82, SLATE)
        jx1, jx2, top, base = 14, 50, 22, 74
        rr = (jx2 - jx1) / 2
        cxj = (jx1 + jx2) / 2
        for y in range(top, base):
            for x in range(jx1, jx2 + 1):
                dome = y < top + rr and (x - cxj) ** 2 + (y - top - rr) ** 2 > rr * rr
                if dome:
                    continue
                blend(im, x, y, (70, 80, 120), 0.5)
        glow(im, cxj, 54, 16, BLUE, 0.7)
        for x in range(24, 41):                                  # the filament
            im.set(x, int(54 + 2 * math.sin(x * 1.3)), (230, 240, 255))
        for y in range(top, base):                               # the glass's edges and its light
            for x in range(jx1, jx2 + 1):
                dome = y < top + rr
                d = math.hypot(x - cxj, y - top - rr) if dome else abs(x - cxj)
                if abs(d - rr) < 0.9 and (not dome or y <= top + rr):
                    blend(im, x, y, (230, 240, 255), 0.75)
        for y in range(top + 6, base - 4):
            blend(im, jx1 + 5, y, (255, 255, 255), 0.5)
        im.rect(10, 74, 54, 78, NICKEL)
        im.rect(10, 77, 54, 79, shade(NICKEL, 0.6))
        for x in (12, 52):                                       # clamps
            im.rect(x - 1, 66, x + 2, 78, NICKEL)
        for y0 in (86, 102):                                     # drawers
            im.rect(8, y0, 56, y0 + 14, shade(CER, 0.97))
            bevel(im, 8, y0, 56, y0 + 14, CER)
            im.rect(26, y0 + 6, 38, y0 + 8, NICKEL)
    im.noise(2, seed + 9)
    return im


CABS = {1: cab1, 2: cab2, 3: cab3}


def bank_end(n):
    """A bank's end panel, 64x128: the body, a handle, vents (aligned)."""
    im = Img(64, 128)
    c = BODY[n]
    if n == 2:
        hammered(im, 0, 0, 64, 128, c, 4100)
    else:
        fill(im, 0, 0, 64, 128, c, 0.015, 4100 + n)
    top = {1: CREAM, 2: shade(HGREEN, 0.8), 3: SLATE}[n]
    im.rect(0, 0, 64, 12 if n == 1 else 10, top)
    edge = {1: ALU, 2: shade(HGREEN, 0.55), 3: NICKEL}[n]
    im.rect(0, 0, 64, 2, edge)
    for x0 in (10, 38):
        louvres(im, x0, 24, x0 + 16, 56, c, 4)
    im.rect(29, 64, 35, 96, edge)
    im.rect(30, 66, 34, 94, shade(edge, 1.2))
    foot = {1: (40, 42, 46), 2: BAK, 3: shade(NICKEL, 0.8)}[n]
    im.rect(0, 120, 64, 128, foot)
    if n == 1:
        im.rect(0, 12, 64, 13, shade(GB, 0.6))
        im.rect(0, 112, 64, 115, ORANGE)
    if n == 2:
        im.rect(26, 102, 38, 108, BRASS)
    im.noise(2, 4110 + n)
    return im


def bank_top(n):
    im = Img(64, 64)
    c = {1: CREAM, 2: shade(HGREEN, 0.9), 3: CER}[n]
    if n == 2:
        hammered(im, 0, 0, 64, 64, c, 4200)
    else:
        fill(im, 0, 0, 64, 64, c, 0.015, 4200 + n)
    edge = {1: ALU, 2: BAK, 3: NICKEL}[n]
    im.frame(0, 0, 64, 64, edge, 2)
    for y in range(20, 44, 3):                                   # a vent
        im.rect(16, y, 48, y + 1, shade(c, 0.5))
    im.noise(2, 4210 + n)
    return im


# === a goods rack ===========================================================================================
def rack(n, w=128):
    """A rack's front, w x 96: three shelves of cased and crated instruments. RF, the goods bay's racks: 64
    wide, seamless, laid by where it is (the bay is cut into pieces along the racks' faces)."""
    rnd = random.Random(4300 + n)
    back = {1: (60, 66, 74), 2: (30, 34, 30), 3: (70, 72, 78)}[n]
    frame = {1: GB, 2: HGREEN, 3: CER}[n]
    im = Img(w, 96, back)
    fill(im, 0, 0, w, 96, back, 0.03, 4301 + n)
    for sy in (0, 32, 64):
        bot = sy + 29
        x = 4
        while x < w - 8:
            if n == 1:
                kind = rnd.choice("bbcrk")
                if kind == "b":                                  # an instrument case: a dial, a lamp
                    wd, h = rnd.choice((20, 24, 28)), rnd.randrange(16, 24)
                    c = rnd.choice((GB, CREAM, shade(GB, 0.85)))
                    im.rect(x, bot - h, x + wd, bot, c)
                    bevel(im, x, bot - h, x + wd, bot, c)
                    im.rect(x + 2, bot - h + 2, x + wd - 2, bot - h + 5, INK)
                    needle_dial(im, x + wd // 2, bot - h // 2 + 1, min(6, h // 3), ALU, FACE, rnd.random())
                    lamp(im, x + wd - 4, bot - 4, 1.4, rnd.choice((AMBER, GREEN, AMBER_OFF)), True)
                elif kind == "c":                                # a carton, its label
                    wd, h = rnd.choice((18, 22)), rnd.randrange(14, 22)
                    c = shade((176, 146, 104), rnd.uniform(0.85, 1.05))
                    im.rect(x, bot - h, x + wd, bot, c)
                    im.rect(x, bot - h, x + wd, bot - h + 1, shade(c, 1.2))
                    im.rect(x + 3, bot - h + 4, x + wd - 3, bot - h + 9, (240, 238, 226))
                    im.rect(x + 4, bot - h + 6, x + wd - 5, bot - h + 7, INK)
                elif kind == "r":                                # tape in a can
                    wd = 18
                    im.disc(x + 9, bot - 9, 9, ALU)
                    im.disc(x + 9, bot - 9, 3, INK)
                    im.disc(x + 9, bot - 9, 7, shade(ALU, 0.85))
                    im.disc(x + 9, bot - 9, 2, INK)
                else:                                            # a keyboard on its end
                    wd, h = 26, 12
                    im.rect(x, bot - h, x + wd, bot, CREAM)
                    for kx in range(x + 2, x + wd - 3, 4):
                        im.rect(kx, bot - h + 3, kx + 3, bot - 3, KEY if kx % 3 else ORANGE)
            elif n == 2:
                kind = rnd.choice("ccmiw")
                if kind == "c":                                  # a crate, stencilled
                    wd, h = rnd.choice((26, 30)), rnd.randrange(18, 26)
                    c = shade((150, 112, 66), rnd.uniform(0.85, 1.05))
                    im.rect(x, bot - h, x + wd, bot, c)
                    for yy in range(bot - h + 5, bot, 6):
                        im.rect(x, yy, x + wd, yy + 1, shade(c, 0.6))
                    im.frame(x, bot - h, x + wd, bot, shade(c, 0.6), 1)
                    im.rect(x + wd // 2 - 4, bot - h + 2, x + wd // 2 + 4, bot - h + 4, BAK)
                elif kind == "m":                                # a meter in bakelite
                    wd, h = 20, 20
                    im.rect(x, bot - h, x + wd, bot, BAK)
                    needle_dial(im, x + 10, bot - 11, 7, BAK, FACE, rnd.random())
                elif kind == "i":                                # porcelain insulators
                    wd = 22
                    for k in range(2):
                        insulator(im, x + 5 + 12 * k, bot - 18, bot, 9)
                else:                                            # a drum of copper wire
                    wd = 22
                    im.disc(x + 11, bot - 11, 11, shade((150, 112, 66), 0.9))
                    im.disc(x + 11, bot - 11, 8, COPPER)
                    for r in range(3, 8, 2):
                        for a in range(0, 360, 12):
                            im.set(round(x + 11 + r * math.cos(math.radians(a))), round(bot - 11 + r * math.sin(math.radians(a))),
                                   shade(COPPER, 0.7))
                    im.disc(x + 11, bot - 11, 2.5, BAK)
            else:
                kind = rnd.choice("ffbjx")
                if kind == "f":                                  # a flask
                    wd = 14
                    cx = x + 7
                    for y in range(bot - 18, bot):
                        hw = 2 if y < bot - 11 else 2 + (y - (bot - 11)) * 0.7
                        for xx in range(int(cx - hw), int(cx + hw) + 1):
                            im.set(xx, y, mix(back, (200, 220, 230), 0.55))
                        im.set(int(cx - hw), y, (230, 240, 246))
                    im.rect(cx - 5, bot - 5, cx + 6, bot, mix((200, 220, 230), VIOLET, 0.4))
                elif kind == "b":                                # a box marked fragile: glass
                    wd, h = rnd.choice((22, 26)), rnd.randrange(14, 22)
                    im.rect(x, bot - h, x + wd, bot, (214, 200, 160))
                    im.frame(x, bot - h, x + wd, bot, (160, 140, 100), 1)
                    for i in range(6):                           # a red glass drawn on it
                        im.rect(x + wd // 2 - 3 + i // 2, bot - h + 4 + i, x + wd // 2 + 3 - i // 2, bot - h + 5 + i, HOSE)
                    im.rect(x + wd // 2 - 1, bot - h + 10, x + wd // 2 + 1, bot - h + 13, HOSE)
                elif kind == "j":                                # a small bell jar
                    wd = 18
                    im.rect(x + 1, bot - 3, x + 17, bot, NICKEL)
                    for y in range(bot - 16, bot - 3):
                        for xx in range(x + 3, x + 15):
                            if y > bot - 10 or (xx - x - 9) ** 2 + (y - bot + 10) ** 2 < 36:
                                blend(im, xx, y, (190, 210, 230), 0.4)
                    im.set(x + 5, bot - 12, (255, 255, 255))
                else:                                            # bulbs standing in a tray
                    wd = 26
                    im.rect(x, bot - 4, x + wd, bot, (150, 112, 70))
                    for k in range(3):
                        bulb(im, x + 5 + 8 * k, bot - 11, 3.5, mix(VIOLET, (200, 200, 210), 0.6), 3)
            x += wd + rnd.randrange(2, 6)
        im.rect(0, bot, w, bot + 3, frame)
        im.rect(0, bot, w, bot + 1, shade(frame, 1.25))
        im.rect(0, bot + 2, w, bot + 3, shade(frame, 0.55))
    for x in ((0, w // 2 - 2, w - 4) if w != 64 else (0, 32)):
        im.rect(x, 0, x + 4, 96, frame)
        im.rect(x, 0, x + 1, 96, shade(frame, 1.25))
        im.rect(x + 3, 0, x + 4, 96, shade(frame, 0.55))
        if n == 1:
            for y in range(4, 92, 6):
                im.set(x + 2, y, shade(frame, 0.45))
    im.noise(2, 4310 + n)
    return im


def rack_end(n):
    """A rack's end, 64x96: the uprights and the shelves' ends (aligned)."""
    back = {1: (60, 66, 74), 2: (30, 34, 30), 3: (70, 72, 78)}[n]
    frame = {1: GB, 2: HGREEN, 3: CER}[n]
    im = Img(64, 96, back)
    fill(im, 0, 0, 64, 96, back, 0.03, 4320 + n)
    for sy in (29, 61, 93):
        im.rect(0, sy, 64, sy + 3, frame)
    for x in (0, 60):
        im.rect(x, 0, x + 4, 96, frame)
    for i in range(0, 56, 2):                                    # a brace
        im.rect(4 + i, 4 + i // 2, 6 + i, 6 + i // 2, shade(frame, 0.8))
    im.noise(2, 4330 + n)
    return im


def rack_top(n):
    im = Img(64, 64, {1: (150, 160, 170), 2: (60, 70, 62), 3: (210, 212, 214)}[n])
    im.noise(4, 4340 + n)
    frame = {1: GB, 2: HGREEN, 3: CER}[n]
    im.frame(0, 0, 64, 64, frame, 3)
    im.rect(30, 0, 34, 64, frame)
    return im


# === an optical bench ======================================================================================
def bench_side(n):
    """An optical bench's side, 64x48 (aligned): a heavy base, the rail on it."""
    im = Img(64, 48)
    if n == 1:
        fill(im, 0, 0, 64, 48, GB, 0.015, 4400)
        cyl_h(im, 0, 0, 64, 6, ALU, 1.3, 0.6)                    # the rail along the top
        im.rect(0, 6, 64, 8, CREAM)
        for x0 in (2, 34):
            im.rect(x0, 12, x0 + 28, 40, shade(GB, 0.94))
            bevel(im, x0, 12, x0 + 28, 40, GB)
            im.rect(x0 + 11, 24, x0 + 17, 27, ALU)
        im.rect(0, 42, 64, 48, (40, 42, 46))
        im.rect(30, 30, 34, 34, ORANGE)
    elif n == 2:
        hammered(im, 0, 0, 64, 48, HGREEN, 4401)
        im.rect(0, 0, 64, 7, BAK)                                # a black top, a brass rail
        im.rect(0, 1, 64, 3, BRASS)
        im.rect(0, 3, 64, 4, shade(BRASS, 0.55))
        for x in (4, 58):                                        # cast legs, a stretcher
            im.rect(x, 7, x + 3, 48, shade(HGREEN, 0.6))
        im.rect(0, 34, 64, 37, shade(HGREEN, 0.6))
        for x in range(8, 58, 8):
            im.disc(x, 20, 1.2, shade(HGREEN, 1.5))
        im.rect(26, 14, 38, 20, BRASS)
    else:
        im.rect(0, 0, 64, 48, (24, 24, 30))
        fill(im, 0, 4, 64, 16, (40, 40, 46), 0.08, 4402)         # a black granite slab
        im.rect(0, 4, 64, 5, (90, 90, 98))
        cyl_h(im, 0, 0, 64, 4, NICKEL, 1.4, 0.6)                 # the nickel rail on it
        for x in (6, 54):                                        # white ceramic legs, nickel feet
            cyl_v(im, x, 16, x + 6, 44, CER, 1.1, 0.7)
            im.rect(x - 1, 44, x + 7, 48, NICKEL)
        im.rect(0, 30, 64, 32, NICKEL)
    im.noise(2, 4410 + n)
    return im


def bench_top(n, v):
    """An optical bench from above, 64x64 (two variants): the rail along x,
    carriers on it holding lenses, a lamp, a prism."""
    rnd = random.Random(4420 + n * 3 + v)
    base = {1: GB, 2: BAK, 3: (40, 40, 46)}[n]
    im = Img(64, 64, base)
    fill(im, 0, 0, 64, 64, base, 0.03, 4430 + n)
    if n == 2:
        im.frame(0, 0, 64, 64, BRASS, 1)
    rail = {1: ALU, 2: BRASS, 3: NICKEL}[n]
    cyl_h(im, 0, 26, 64, 38, rail, 1.3, 0.6)
    for x in range(0, 64, 8):                                    # its scale
        im.rect(x, 36, x + 1, 38, INK)
    holder = {1: CREAM, 2: COPPER, 3: CER}[n]
    if v == 0:
        for cx, kind in ((12, "lamp"), (36, "lens"), (54, "lens")):
            im.rect(cx - 5, 22, cx + 6, 42, holder)
            bevel(im, cx - 5, 22, cx + 6, 42, holder)
            if kind == "lamp":
                im.disc(cx, 32, 5, {1: ORANGE, 2: BAK, 3: NICKEL}[n])
                im.disc(cx, 32, 3, (255, 240, 200))
            else:
                im.rect(cx - 1, 18, cx + 2, 46, (170, 210, 230))
                im.rect(cx, 18, cx + 1, 46, (240, 250, 255))
    else:
        for cx in (16, 46):
            im.rect(cx - 6, 22, cx + 7, 42, holder)
            bevel(im, cx - 6, 22, cx + 7, 42, holder)
        for i in range(10):                                      # a prism, seen from above
            im.rect(16 - i // 2, 27 + i // 2 - 3, 17 + i // 2, 28 + i // 2 - 3, (190, 220, 236))
        im.rect(44, 24, 48, 40, INK)                             # a slit
        im.rect(45, 30, 47, 34, (240, 250, 255))
    im.noise(2, 4440 + n * 3 + v)
    return im


# === a tank, floor to ceiling ==============================================================================
def tank(n):
    """A tank's face, 64x256 in one piece: a domed top under the ceiling,
    flanges, a sight glass, a plate, a valve at the foot."""
    rnd = random.Random(4500 + n)
    c = {1: CREAM, 2: HGREEN, 3: CER}[n]
    im = Img(64, 256)
    if n == 2:
        hammered(im, 0, 0, 64, 256, c, 4501, 8)
    else:
        fill(im, 0, 0, 64, 256, c, 0.015, 4501)
    for x in range(64):                                          # round: shaded across
        f = 0.62 + 0.5 * math.sin((x + 0.5) * math.pi / 64)
        for y in range(256):
            p = im.px[y * 64 + x]
            im.px[y * 64 + x] = list(shade(p[:3], f)) + [255]
    flange = {1: ALU, 2: shade(HGREEN, 0.7), 3: NICKEL}[n]
    for y in (0, 30, 222):                                       # flanges under the ceiling, a joint, the foot
        cyl_v(im, 0, y, 64, y + 6, flange, 1.25, 0.6)
        for x in range(4, 64, 8):
            im.set(x, y + 3, shade(flange, 0.4))
    im.rect(0, 228, 64, 256, {1: (40, 42, 46), 2: BAK, 3: shade(NICKEL, 0.75)}[n])
    im.rect(0, 228, 64, 229, (24, 24, 26))
    if n == 1:                                                   # a sight glass with amber liquid, orange bands
        for y in (60, 196):
            im.rect(0, y, 64, y + 4, ORANGE)
        im.rect(44, 70, 51, 188, ALU)
        im.rect(46, 72, 49, 186, (40, 46, 54))
        im.rect(46, 120, 49, 186, (230, 170, 70))
        im.rect(46, 120, 49, 121, (255, 230, 160))
        for y in range(76, 186, 10):
            im.rect(51, y, 54, y + 1, INK)
        im.rect(12, 92, 36, 112, INK)                            # a black plate, a number
        text(im, "T", 16, 96, (236, 236, 228), 1)
        digit(im, "3", 24, 96, (236, 236, 228), 1)
        im.rect(14, 104, 34, 106, ORANGE)
        needle_dial(im, 24, 140, 9, ALU, FACE, 0.6)
        lamp(im, 24, 160, 2.5, AMBER, True, INK)
        cyl_h(im, 14, 236, 50, 244, ALU)
        im.disc(32, 240, 7, ORANGE)
        im.disc(32, 240, 3, shade(ORANGE, 0.6))
    elif n == 2:                                                 # rivets, copper pipes, a brass plate, a big dial
        for y in range(38, 222, 16):
            for x in range(6, 60, 10):
                im.disc(x, y, 1, shade(c, 1.5))
        cyl_v(im, 50, 36, 56, 222, COPPER, 1.45, 0.6)
        for y in (60, 120, 180):
            im.rect(48, y, 58, y + 4, BRASS)
        im.rect(10, 70, 40, 84, BRASS)
        im.frame(10, 70, 40, 84, shade(BRASS, 0.55), 1)
        text(im, "HV", 14, 74, BAK, 1)
        digit(im, "2", 30, 74, BAK, 1)
        im.disc(25, 120, 14, BAK)
        needle_dial(im, 25, 120, 12, BAK, FACE, 0.75)
        lamp(im, 25, 150, 3.5, WARN, True, BAK)
        im.disc(30, 240, 9, WARN)                                # the wheel
        im.disc(30, 240, 6, shade(HGREEN, 0.5))
        im.rect(21, 239, 40, 241, WARN)
        im.rect(29, 231, 31, 250, WARN)
    else:                                                        # a sight glass with mercury, a hose, small dials
        im.rect(41, 64, 52, 200, NICKEL)
        im.rect(43, 66, 50, 198, (40, 44, 60))
        glow(im, 46, 130, 30, VIOLET, 0.25)
        cyl_v(im, 44, 140, 49, 198, MERC, 1.3, 0.55)
        im.rect(44, 140, 49, 141, (255, 255, 255))
        for y in range(70, 198, 8):
            im.rect(36, y, 40, y + 1, INK)
        for y0 in (70, 110):
            needle_dial(im, 20, y0, 8, NICKEL, CER, 0.3 + y0 / 300)
        im.rect(8, 150, 32, 168, SLATE)
        text(im, "HG", 10, 154, (230, 230, 236), 1)
        digit(im, "4", 24, 154, (230, 230, 236), 1)
        hose(im, curve((20, 176), (54, 236), 14), HOSE, 2)
        cyl_h(im, 14, 236, 50, 244, NICKEL)
    im.noise(2, 4510 + n)
    return im


def tank_top(n):
    """TT, 64x64: a tank seen from above, its dome, a manhole, a pipe out."""
    c = {1: CREAM, 2: HGREEN, 3: CER}[n]
    floor = {1: (40, 42, 46), 2: (26, 28, 26), 3: (30, 30, 36)}[n]
    im = Img(64, 64, floor)
    fill(im, 0, 0, 64, 64, floor, 0.03, 4530 + n)
    for y in range(64):
        for x in range(64):
            r = math.hypot(x - 31.5, y - 31.5)
            if r < 31:
                im.set(x, y, shade(c, 0.7 + 0.5 * (1 - r / 31) - 0.15 * (x - y) / 64))
    flange = {1: ALU, 2: shade(HGREEN, 0.7), 3: NICKEL}[n]
    for a in range(0, 360, 15):
        im.set(round(31.5 + 29 * math.cos(math.radians(a))), round(31.5 + 29 * math.sin(math.radians(a))), shade(flange, 0.5))
    im.disc(26, 26, 8, flange)
    im.disc(26, 26, 6, shade(c, 0.6))
    im.rect(40, 30, 64, 36, {1: ALU, 2: COPPER, 3: NICKEL}[n])
    im.noise(2, 4540 + n)
    return im


def ledge_face(look):
    """LF, 64x256 (aligned): the cellar's ledge seen from the pit, its 144 high face. The pit's walls show
    the lab's wall (LA) laid from the ceiling, so 16 rows into it where the ledge's top is: the face is
    that wall from row 16, and goes on as the walls beside it do."""
    wall = GI.wall(look, "LA")
    im = Img(64, 256)
    for y in range(256):
        for x in range(64):
            im.px[y * 64 + x] = list(wall.px[((y + 16) % 256) * 64 + x])
    for x in range(64):                                          # the ledge's lip
        im.set(x, 0, shade(tuple(im.px[x][:3]), 1.3))
        im.set(x, 1, shade(tuple(im.px[64 + x][:3]), 0.6))
    return im


# === the belt THEN, new and working (NOW keeps gfx_then's rusted one) ======================================
BELT_RUBBER = {1: (50, 54, 60), 2: (28, 28, 26), 3: (168, 172, 178)}
BELT_FRAME = {1: GB, 2: HGREEN, 3: CER}
BELT_EDGE = {1: ALU, 2: BRASS, 3: NICKEL}


def belt_bed(n):
    """BB, 64x64 flat: the band, ribbed across the way it runs (along x), so that it is seen to move."""
    rub = BELT_RUBBER[n]
    im = Img(64, 64, rub)
    fill(im, 0, 0, 64, 64, rub, 0.025, 4900 + n)
    for x in range(0, 64, 8):                                    # ribs, across
        im.rect(x, 0, x + 2, 64, shade(rub, 1.45 if n != 3 else 0.82))
        im.rect(x + 2, 0, x + 3, 64, shade(rub, 0.7 if n != 3 else 1.08))
    for y in (0, 63):
        im.rect(0, y, 64, y + 1, shade(rub, 0.6))
    if n == 1:                                                   # a painted mark on the band, orange
        im.rect(30, 26, 34, 38, ORANGE)
    im.noise(2, 4910 + n)
    return im


def belt_curb(n):
    """BC, 64x64 flat: the belt's side frames from above, enamel with an edge strip and roller axles."""
    c = BELT_FRAME[n]
    im = Img(64, 64, c)
    if n == 2:
        hammered(im, 0, 0, 64, 64, c, 4920)
    else:
        fill(im, 0, 0, 64, 64, c, 0.02, 4920 + n)
    for y in range(0, 64, 16):
        im.rect(0, y, 64, y + 2, BELT_EDGE[n])
    for x in range(4, 64, 16):
        for y in range(8, 64, 16):
            im.disc(x, y, 1.6, shade(BELT_EDGE[n], 0.6))
    im.noise(2, 4930 + n)
    return im


def belt_side(n):
    """BS, 64x128 (aligned): the belt's frame from the side; its top 16 the curb's face (rollers' ends,
    an edge strip), below it the frame and its legs (seen where the band ends over the hatch)."""
    c, edge = BELT_FRAME[n], BELT_EDGE[n]
    im = Img(64, 128, (22, 22, 24))
    fill(im, 0, 0, 64, 128, (22, 22, 24), 0.04, 4940 + n)
    if n == 2:
        hammered(im, 0, 0, 64, 16, c, 4941)
    else:
        fill(im, 0, 0, 64, 16, c, 0.02, 4941 + n)
    im.rect(0, 0, 64, 2, edge)
    im.rect(0, 14, 64, 16, shade(c, 0.55))
    for x in range(8, 64, 16):                                   # the rollers' ends
        im.disc(x, 8, 3.5, shade(edge, 0.8))
        im.disc(x, 8, 1.5, shade(edge, 0.45))
    if n == 1:
        for x in range(0, 64, 8):
            im.rect(x, 11, x + 4, 13, ORANGE)
    elif n == 2:
        im.rect(28, 4, 36, 7, BRASS)
    for x in (2, 34):                                            # the legs and a stretcher
        im.rect(x, 16, x + 6, 128, shade(c, 0.75))
        im.rect(x, 16, x + 1, 128, shade(c, 1.1))
    im.rect(0, 60, 64, 64, shade(c, 0.6))
    im.noise(2, 4950 + n)
    return im


# === a pump set, the belt's motor, a console (low furniture, 48 high, aligned) ===============================
def pump_side(n):
    im = Img(64, 48)
    if n == 1:
        fill(im, 0, 0, 64, 48, (40, 42, 46), 0.03, 4600)
        cyl_h(im, 2, 6, 34, 40, GB, 1.3, 0.55)                   # the motor, finned
        for x in range(4, 34, 3):
            im.rect(x, 6, x + 1, 40, shade(GB, 0.6))
        im.rect(34, 18, 40, 28, ORANGE)                          # the coupling
        cyl_h(im, 40, 12, 60, 36, CREAM, 1.2, 0.6)               # the pump
        im.disc(50, 24, 6, ALU)
        im.disc(50, 24, 3, INK)
        im.rect(0, 40, 64, 48, GB)
        im.rect(0, 40, 64, 41, shade(GB, 1.3))
    elif n == 2:
        fill(im, 0, 0, 64, 48, (26, 28, 26), 0.03, 4601)
        cyl_h(im, 4, 4, 36, 40, HGREEN, 1.3, 0.5)
        for x in (8, 30):
            im.rect(x, 4, x + 2, 40, COPPER)
        im.rect(36, 20, 42, 26, BRASS)
        cyl_h(im, 42, 10, 60, 38, BAK, 1.6, 0.6)
        im.disc(51, 24, 5, COPPER)
        im.rect(0, 40, 64, 48, shade(HGREEN, 0.7))
        im.rect(14, 12, 26, 18, BRASS)
    else:
        fill(im, 0, 0, 64, 48, (30, 30, 36), 0.03, 4602)
        im.rect(2, 10, 38, 40, CER)                              # a white rotary pump
        bevel(im, 2, 10, 38, 40, CER)
        im.disc(20, 25, 9, NICKEL)
        im.disc(20, 25, 6, shade(NICKEL, 0.7))
        bulb(im, 51, 16, 7, BLUE, 4, NICKEL)                     # its glass trap
        hose(im, curve((28, 14), (46, 20), -6), HOSE, 1.6)
        hose(im, curve((38, 34), (62, 30), 4), HOSE, 1.6)
        im.rect(0, 40, 64, 48, NICKEL)
        im.rect(0, 40, 64, 41, (255, 255, 255))
    im.noise(2, 4610 + n)
    return im


def pump_top(n):
    base = {1: (40, 42, 46), 2: (26, 28, 26), 3: (30, 30, 36)}[n]
    im = Img(64, 64, base)
    fill(im, 0, 0, 64, 64, base, 0.03, 4620 + n)
    if n == 1:
        cyl_v(im, 8, 4, 40, 60, GB)
        for y in range(6, 60, 3):
            im.rect(8, y, 40, y + 1, shade(GB, 0.6))
        im.rect(40, 26, 46, 38, ORANGE)
        im.disc(54, 32, 9, CREAM)
        im.disc(54, 32, 4, ALU)
    elif n == 2:
        cyl_v(im, 8, 6, 40, 58, HGREEN)
        im.rect(40, 28, 46, 36, BRASS)
        im.disc(54, 32, 9, BAK)
        im.disc(54, 32, 5, COPPER)
    else:
        im.rect(6, 10, 38, 54, CER)
        bevel(im, 6, 10, 38, 54, CER)
        im.disc(22, 32, 9, NICKEL)
        im.disc(52, 20, 7, mix(BLUE, (255, 255, 255), 0.3))
        hose(im, curve((30, 40), (52, 52), 4), HOSE, 1.6)
    im.noise(2, 4630 + n)
    return im


def motor_side(n):
    """The belt's motor housing, 64x48 (aligned): a guard over the drive."""
    im = Img(64, 48)
    c = BODY[n] if n != 3 else (60, 62, 70)
    if n == 2:
        hammered(im, 0, 0, 64, 48, c, 4700)
    else:
        fill(im, 0, 0, 64, 48, c, 0.02, 4700 + n)
    edge = {1: ALU, 2: BRASS, 3: NICKEL}[n]
    im.rect(0, 0, 64, 3, edge)
    if n == 1:
        for y in range(8, 34, 4):
            im.rect(6, y, 58, y + 2, shade(c, 0.5))
        for i in range(0, 64, 8):                                # a hazard edge in orange and black
            im.rect(i, 38, i + 4, 44, ORANGE)
            im.rect(i + 4, 38, i + 8, 44, INK)
    elif n == 2:
        im.disc(32, 22, 14, BAK)
        im.disc(32, 22, 11, COPPER)
        for k in range(6):
            a = k * math.pi / 3
            im.rect(round(32 + 6 * math.cos(a)) - 1, round(22 + 6 * math.sin(a)) - 1,
                    round(32 + 6 * math.cos(a)) + 2, round(22 + 6 * math.sin(a)) + 2, shade(COPPER, 0.6))
        im.disc(32, 22, 3, BAK)
        lamp(im, 8, 10, 2.5, WARN, True, BAK)
        im.rect(0, 40, 64, 48, BAK)
    else:
        im.rect(4, 8, 60, 38, (24, 24, 34))
        for x in range(4, 60, 3):
            im.rect(x, 8, x + 1, 38, shade(NICKEL, 0.7))
        glow(im, 32, 23, 18, BLUE, 0.35)
        im.rect(0, 40, 64, 48, NICKEL)
    im.noise(2, 4710 + n)
    return im


def motor_top(n):
    c = BODY[n] if n != 3 else (60, 62, 70)
    im = Img(64, 64)
    if n == 2:
        hammered(im, 0, 0, 64, 64, c, 4720)
    else:
        fill(im, 0, 0, 64, 64, c, 0.02, 4720 + n)
    edge = {1: ALU, 2: BRASS, 3: NICKEL}[n]
    im.frame(0, 0, 64, 64, edge, 2)
    for y in range(10, 54, 4):
        im.rect(10, y, 54, y + 2, shade(c, 0.55))
    im.noise(2, 4730 + n)
    return im


def console_side(n):
    """A low console's side, 64x48 (aligned): its desk's edge, panels under it."""
    im = Img(64, 48)
    c = BODY[n]
    if n == 2:
        hammered(im, 0, 0, 64, 48, c, 4800)
    else:
        fill(im, 0, 0, 64, 48, c, 0.015, 4800 + n)
    edge = {1: CREAM, 2: BAK, 3: SLATE}[n]
    im.rect(0, 0, 64, 6, edge)
    im.rect(0, 0, 64, 1, shade(edge, 1.3))
    im.rect(0, 6, 64, 7, {1: ALU, 2: BRASS, 3: NICKEL}[n])
    for x0 in (2, 34):
        bevel(im, x0, 10, x0 + 28, 42, c)
        if n == 1:
            lamp(im, x0 + 14, 18, 2, AMBER, True, INK)
            im.rect(x0 + 8, 30, x0 + 20, 32, ALU)
        elif n == 2:
            im.rect(x0 + 8, 16, x0 + 20, 21, BRASS)
            im.rect(x0 + 12, 30, x0 + 16, 34, BAK)
        else:
            im.rect(x0 + 10, 28, x0 + 18, 30, NICKEL)
            lamp(im, x0 + 14, 18, 2, VIOLET, True, NICKEL)
    im.rect(0, 44, 64, 48, {1: (40, 42, 46), 2: BAK, 3: NICKEL}[n])
    im.noise(2, 4810 + n)
    return im


def console_top(n):
    """A console from above, 64x64: rows of keys and dials (a 64 square whole)."""
    rnd = random.Random(4820 + n)
    im = Img(64, 64)
    if n == 1:
        fill(im, 0, 0, 64, 64, CREAM, 0.015, 4821)
        im.frame(0, 0, 64, 64, ALU, 2)
        im.rect(4, 4, 60, 24, (46, 50, 58))                      # a lamp field
        for r in range(3):
            for col in range(8):
                q = rnd.random()
                lamp(im, 8 + col * 7, 9 + r * 6, 1.6, AMBER if q < 0.4 else GREEN if q < 0.46 else AMBER_OFF, q < 0.46)
        for r in range(3):                                       # keys
            for col in range(8):
                x, y = 6 + col * 7, 30 + r * 8
                c = ORANGE if (r, col) in ((0, 7), (2, 0)) else KEY
                im.rect(x, y, x + 5, y + 6, shade(c, 0.7))
                im.rect(x, y, x + 5, y + 5, c)
        im.disc(54, 56, 4, SCOPE)
        im.disc(54, 56, 1.5, TRACE)
        legend(im, "07", 20, 54)
    elif n == 2:
        hammered(im, 0, 0, 64, 64, HGREEN, 4822)
        im.frame(0, 0, 64, 64, BAK, 2)
        for cx, cy, a in ((16, 16, 0.3), (48, 16, 0.7)):
            im.disc(cx, cy, 11, BAK)
            needle_dial(im, cx, cy, 9, BAK, FACE, a)
        for cx in (12, 28, 44):                                  # big knobs
            im.disc(cx, 44, 6, BAK)
            im.disc(cx - 1, 43, 4.5, (60, 56, 52))
            im.rect(cx - 1, 38, cx + 1, 44, FACE)
        im.rect(54, 34, 60, 56, PORC)                            # a knife switch seen from above
        im.rect(56, 36, 58, 54, COPPER)
        lamp(im, 57, 60, 2, WARN, True)
        im.rect(18, 56, 46, 61, BRASS)
    else:
        fill(im, 0, 0, 64, 64, SLATE, 0.04, 4823)
        im.frame(0, 0, 64, 64, NICKEL, 2)
        for cx, cy, a in ((12, 12, 0.2), (28, 12, 0.5), (44, 12, 0.8)):
            needle_dial(im, cx, cy, 6, NICKEL, CER, a)
        for col in range(6):                                     # toggle switches
            x = 8 + col * 9
            im.disc(x, 32, 2.5, NICKEL)
            im.rect(x - 1, 26 if col % 2 else 32, x + 1, 32 if col % 2 else 38, (230, 232, 236))
        bulb(im, 16, 50, 6, VIOLET, 3)
        bulb(im, 32, 50, 6, BLUE, 3)
        hose(im, curve((40, 50), (60, 56), 4), HOSE, 1.5)
    im.noise(2, 4830 + n)
    return im


# === pictures on the walls ==================================================================================
def on_wall(look, part, w, shift=0):
    return GI.on_wall(look, part, w, shift)


def schematic(n, shift=0, part="EX"):
    """128 wide on the hall's wall (EX, look 2): the machine drawn, a door's
    outline within itself, its wires out to the lamps."""
    im = on_wall(2, part, 128, shift)
    x1, y1, x2, y2 = 10, 70, 118, 196
    if n == 1:                                                   # a blueprint in an aluminium frame
        ground, ink, frame = (40, 86, 156), (226, 238, 250), ALU
    elif n == 2:                                                 # an old drawing on cream, wood and brass
        ground, ink, frame = (226, 214, 180), (90, 54, 30), (110, 74, 44)
    else:                                                        # a white print, violet ink, nickel
        ground, ink, frame = (240, 240, 244), (90, 50, 150), NICKEL
    im.rect(x1 - 3, y1 - 3, x2 + 3, y2 + 3, frame)
    im.rect(x1 - 3, y1 - 3, x2 + 3, y1 - 2, shade(frame, 1.25))
    im.rect(x1 - 3, y2 + 2, x2 + 3, y2 + 3, shade(frame, 0.5))
    fill(im, x1, y1, x2, y2, ground, 0.02, 4900 + n)
    if n == 1:                                                   # a grid
        for x in range(x1, x2, 8):
            for y in range(y1, y2):
                blend(im, x, y, ink, 0.12)
        for y in range(y1, y2, 8):
            for x in range(x1, x2):
                blend(im, x, y, ink, 0.12)
    # the machine in plan: its box, its wings, the door's outline within itself, smaller and smaller
    mx1, my1, mx2, my2 = 34, 92, 94, 172
    im.frame(mx1, my1, mx2, my2, ink, 2)
    im.frame(mx1 - 12, my2 - 26, mx1, my2, ink, 1)
    im.frame(mx2, my2 - 26, mx2 + 12, my2, ink, 1)
    for k in range(4):
        d = 4 + k * 5
        im.frame(mx1 + d + 6, my1 + d + 4, mx2 - d - 6, my2 - d * 0 - 4 - k * 2, ink, 1)
    im.rect(56, my2 - 2, 72, my2, ground)                        # the door's opening in its face
    for x in (40, 88):                                           # wires out to two lamps
        for y in range(my1 - 6, my1):
            im.set(x, y, ink)
        im.disc(x, my1 - 8, 3, ink)
        im.disc(x, my1 - 8, 1.5, ground)
    for y in range(my2 + 4, my2 + 14):                           # and down to the desk
        im.set(64, y, ink)
    im.frame(52, my2 + 14, 77, my2 + 20, ink, 1)
    head = {1: "MACHINE 7", 2: "MACHINE 7", 3: "MACHINE 7"}[n]
    text(im, head, 64 - (len(head) * 6 - 1) // 2, y1 + 4, ink, 1)
    im.rect(x2 - 30, y2 - 12, x2 - 4, y2 - 4, ink)               # the title block
    im.rect(x2 - 29, y2 - 11, x2 - 5, y2 - 5, ground)
    im.rect(x2 - 26, y2 - 9, x2 - 10, y2 - 8, ink)
    if n == 2:                                                   # brass corners
        for x, y in ((x1 - 3, y1 - 3), (x2 - 3, y1 - 3), (x1 - 3, y2 - 3), (x2 - 3, y2 - 3)):
            im.rect(x, y, x + 6, y + 6, BRASS)
    if n == 3:                                                   # the chambers drawn as bulbs
        for cx in (52, 76):
            for a in range(0, 360, 10):
                im.set(round(cx + 7 * math.cos(math.radians(a))), round(124 + 7 * math.sin(math.radians(a))), ink)
    im.noise(2, 4910 + n)
    return im


def passboard(n, shift=0, part="AR"):
    """128 wide on the vestibule's wall (AR, look 2): the porter's board of
    keys on numbered hooks and passes in pigeonholes."""
    im = on_wall(2, part, 128, shift)
    rnd = random.Random(5000 + n)
    x1, y1, x2, y2 = 8, 78, 120, 178
    if n == 1:
        body, hook, tag = GB, ALU, CREAM
    elif n == 2:
        body, hook, tag = (92, 60, 36), BRASS, (200, 40, 30)
    else:
        body, hook, tag = (44, 46, 54), NICKEL, (236, 236, 232)
    if n == 2:
        fill(im, x1, y1, x2, y2, body, 0.04, 5001)
        for y in range(y1, y2, 5):
            im.rect(x1, y, x2, y + 1, shade(body, 0.85))
    else:
        fill(im, x1, y1, x2, y2, body, 0.015, 5001)
    im.frame(x1, y1, x2, y2, shade(body, 0.55), 2)
    plate = {1: (INK, (236, 236, 228)), 2: (BRASS, BAK), 3: (SLATE, (230, 230, 236))}[n]
    legend(im, "KEYS", 40, y1 + 4, *plate)
    legend(im, "PASSES", 92, y1 + 4, *plate)
    for r in range(4):                                           # keys on hooks, left
        for col in range(5):
            x, y = x1 + 8 + col * 12, y1 + 20 + r * 19
            im.rect(x, y, x + 2, y + 2, hook)
            gone = rnd.random() < 0.18
            if n == 1:                                           # a lamp to a hook: lit while the key is out
                lamp(im, x + 1, y - 4, 1.5, LRED if gone else AMBER_OFF, gone)
            if not gone:
                im.rect(x, y + 2, x + 2, y + 8, shade(hook, 0.8))
                im.rect(x - 1, y + 8, x + 3, y + 10, shade(hook, 0.8))
                im.rect(x - 2, y + 10, x + 4, y + 15, tag)
                im.rect(x - 1, y + 12, x + 3, y + 13, shade(tag, 0.6))
    for r in range(4):                                           # pigeonholes, right, passes in some
        for col in range(3):
            x, y = x1 + 70 + col * 13, y1 + 18 + r * 19
            im.rect(x, y, x + 11, y + 16, shade(body, 0.45))
            if rnd.random() < 0.7:
                c = rnd.choice(((240, 238, 226), (230, 214, 160), (190, 210, 230)))
                im.rect(x + 1, y + 5, x + 10, y + 16, c)
                im.rect(x + 2, y + 7, x + 7, y + 8, (90, 90, 96))
    im.noise(2, 5010 + n)
    return im


def newspaper(n, shift=0, part="CO"):
    """128 wide on the corridor's wall (CO, look 2): a wall newspaper."""
    im = on_wall(2, part, 128, shift)
    rnd = random.Random(5100 + n)
    x1, y1, x2, y2 = 6, 70, 122, 200
    head = {1: ORANGE, 2: WARN, 3: (120, 70, 190)}[n]
    paper = (244, 242, 232)
    im.rect(x1 - 2, y1 - 2, x2 + 2, y2 + 2, {1: ALU, 2: (110, 74, 44), 3: NICKEL}[n])
    fill(im, x1, y1, x2, y2, paper, 0.01, 5101)
    im.rect(x1, y1, x2, y1 + 18, head)
    title = {1: "IMPULSE", 2: "CURRENT", 3: "VACUUM"}[n]
    text(im, title, 64 - (len(title) * 12 - 2) // 2, y1 + 4, (250, 248, 240), 2)
    # a drawing for each paper: a lamp field and a reel; a lightning bolt over a coil; a flask and an atom
    px1, py1 = x1 + 4, y1 + 24
    im.rect(px1, py1, px1 + 46, py1 + 40, shade(paper, 0.93))
    im.frame(px1, py1, px1 + 46, py1 + 40, (120, 120, 120), 1)
    if n == 1:
        reel(im, px1 + 14, py1 + 20, 10, (150, 160, 170))
        for r in range(4):
            for col in range(3):
                lamp(im, px1 + 30 + col * 5, py1 + 8 + r * 7, 1.5, AMBER if (r + col) % 2 else AMBER_OFF, (r + col) % 2 == 1)
    elif n == 2:
        coil(im, px1 + 12, py1 + 16, px1 + 34, py1 + 36)
        for i, (x, y) in enumerate(((26, 2), (20, 8), (26, 8), (20, 14))):
            im.rect(px1 + x - 1, py1 + y, px1 + x + 3, py1 + y + 6, WARN)
    else:
        for a in range(0, 360, 6):
            for rx, ry, rot in ((18, 6, 0.6), (18, 6, -0.6)):
                u, v = rx * math.cos(math.radians(a)), ry * math.sin(math.radians(a))
                im.set(round(px1 + 23 + u * math.cos(rot) - v * math.sin(rot)),
                       round(py1 + 20 + u * math.sin(rot) + v * math.cos(rot)), (120, 70, 190))
        im.disc(px1 + 23, py1 + 20, 3, (120, 70, 190))
    for col, x0 in enumerate((px1 + 52, px1)):                   # the columns: lines of print, a photograph
        ys = range(py1, y2 - 6, 5) if col == 0 else range(py1 + 46, y2 - 6, 5)
        for y in ys:
            ln = rnd.randrange(30, 52) if col == 0 else rnd.randrange(30, 46)
            im.rect(x0, y, x0 + ln, y + 2, (120, 120, 128))
    im.rect(px1 + 52, py1 + 44, px1 + 108, py1 + 76, (150, 150, 148))   # a photograph: people at the machine
    for k in range(5):
        x = px1 + 56 + k * 10
        im.rect(x, py1 + 58, x + 6, py1 + 76, (226, 224, 216))
        im.disc(x + 3, py1 + 54, 2.5, (110, 100, 96))
    im.rect(px1 + 56, py1 + 47, px1 + 104, py1 + 52, (70, 70, 74))
    for x in range(x1 + 2, x2 - 2, 9):                           # pins
        im.disc(x, y1 + 20, 0.8, head)
    im.noise(2, 5110 + n)
    return im


def pipe_run(n, shift=0, part="LA"):
    """64 wide on the lab's wall (LA, look 2), 256 high: a pipe down from the
    ceiling to an open mouth near the floor."""
    im = on_wall(2, part, 64, shift)
    pc = {1: GB, 2: COPPER, 3: NICKEL}[n]
    x1, x2 = 22, 42
    cyl_v(im, x1, 0, x2, 190, pc, 1.4, 0.55)
    for y in (2, 60, 120, 176):                                  # flanges or clamps
        fl = {1: ORANGE, 2: BRASS, 3: shade(NICKEL, 0.8)}[n]
        cyl_v(im, x1 - 4, y, x2 + 4, y + 6, fl, 1.3, 0.55)
        im.set(x1 - 2, y + 3, shade(fl, 0.4))
        im.set(x2 + 1, y + 3, shade(fl, 0.4))
    if n == 3:                                                   # a glass length with something violet in it
        im.rect(x1, 74, x2, 112, (24, 22, 36))
        glow(im, 32, 93, 16, VIOLET, 0.6)
        for y in range(74, 112):
            blend(im, x1 + 3, y, (255, 255, 255), 0.4)
        hose(im, curve((x2, 140), (58, 210), 10), HOSE, 2)
    if n == 2:                                                   # a valve wheel
        im.disc(32, 150, 12, WARN)
        im.disc(32, 150, 9, shade(COPPER, 0.5))
        im.rect(20, 149, 45, 151, WARN)
        im.rect(31, 138, 33, 163, WARN)
        im.disc(32, 150, 3, BRASS)
    if n == 1:                                                   # a gauge on it, a black plate
        needle_dial(im, 32, 145, 8, ALU, FACE, 0.4)
        legend(im, "W", 32, 96)
    # the mouth: the pipe turns out of the wall and opens, dark inside
    cyl_v(im, x1 - 6, 190, x2 + 6, 214, pc, 1.35, 0.5)
    im.disc(32, 208, 13, shade(pc, 0.7))
    im.disc(32, 208, 10, (12, 12, 14))
    im.disc(32, 210, 8, (4, 4, 6))
    for a in range(200, 340, 8):
        im.set(round(32 + 12 * math.cos(math.radians(a))), round(208 + 12 * math.sin(math.radians(a))), shade(pc, 1.5))
    im.noise(2, 5210 + n)
    return im


def gauge_board(n, shift=0, part="LA"):
    """128 wide on the lab's wall (LA, look 2): the valve's gauges over the cellar's ledge, a board of
    dials, a pipe down from each to a valve, a plate VALVE 3. Drawn on the wall it hangs on, so that the
    wall's bands go on round it (MAP11's gauges are the pump room's wall)."""
    im = on_wall(2, part, 128, shift)
    x1, y1, x2, y2 = 10, 76, 118, 190
    board = {1: GB, 2: BAK, 3: SLATE}[n]
    edge = {1: ALU, 2: BRASS, 3: NICKEL}[n]
    im.rect(x1 - 2, y1 - 2, x2 + 2, y2 + 2, edge)
    if n == 2:
        hammered(im, x1, y1, x2, y2, HGREEN, 5300)
    else:
        fill(im, x1, y1, x2, y2, board, 0.02, 5300 + n)
    legend(im, "VALVE 3", 64, y1 + 5, ground=INK if n != 2 else BAK, ink=(236, 236, 228) if n != 2 else BRASS)
    pipe = {1: GB, 2: COPPER, 3: NICKEL}[n]
    for k, x in enumerate((32, 64, 96)):
        if n == 1:
            im.disc(x, y1 + 34, 13, CREAM)
            needle_dial(im, x, y1 + 34, 11, ALU, FACE, (0.25, 0.55, 0.8)[k])
            lamp(im, x, y1 + 54, 2.2, (AMBER, GREEN, AMBER)[k], True, INK)
        elif n == 2:
            im.disc(x, y1 + 34, 14, BAK)
            needle_dial(im, x, y1 + 34, 12, BAK, FACE, (0.3, 0.6, 0.85)[k])
            lamp(im, x, y1 + 54, 2.4, WARN if k == 1 else (90, 30, 24), True, BAK)
        else:
            mercury(im, x - 2, y1 + 18, y1 + 58, (0.4, 0.6, 0.5)[k])
            needle_dial(im, x + 9, y1 + 28, 5, NICKEL, CER, 0.5)
        cyl_v(im, x - 3, y1 + 62, x + 3, y2 - 18, pipe, 1.4, 0.55)
        im.disc(x, y2 - 22, 8, {1: ORANGE, 2: WARN, 3: HOSE}[n])            # a valve's wheel
        im.disc(x, y2 - 22, 5, shade(board, 0.7))
        im.rect(x - 8, y2 - 23, x + 8, y2 - 21, {1: ORANGE, 2: WARN, 3: HOSE}[n])
    cyl_h(im, x1, y2 - 10, x2, y2 - 4, pipe, 1.4, 0.55)               # the header they join
    im.noise(2, 5310 + n)
    return im


NOTICE = [("EXPERIMENT", "r"), ("1", "r"), ("TOMORROW", "b"), ("@", "c"), ("LEAVE", "b"), ("EVERY ROOM", "b"),
          ("AS IT IS", "b"), ("-", "r"), ("LOCK UP", "r")]


def notice(part, look=2, shift=0):
    """64 wide: white card, red and blue: EXPERIMENT 1 TOMORROW, a clock at a
    quarter to, LEAVE EVERY ROOM AS IT IS, LOCK UP. Read from 150 away."""
    im = on_wall(look, part, 64, shift)
    red, blue = (196, 36, 30), (36, 64, 140)
    x1, y1, x2, y2 = 1, 116, 63, 228
    im.rect(x1 + 1, y1 + 1, x2 + 1, y2 + 1, (40, 40, 40))       # its shadow on the wall
    im.rect(x1, y1, x2, y2, (248, 248, 244))
    im.frame(x1, y1, x2, y2, red, 1)
    im.rect(x1 + 2, y1 + 2, x2 - 2, y1 + 4, blue)
    y = y1 + 7
    for s, c in NOTICE:
        if s == "@":                                             # a quarter to, as a clock
            im.disc(32, y + 7, 7, blue)
            im.disc(32, y + 7, 5.6, (248, 248, 244))
            for k in range(12):
                a = k * math.pi / 6
                im.set(round(32 + 4.6 * math.sin(a)), round(y + 7 - 4.6 * math.cos(a)), blue)
            im.rect(27, y + 7, 33, y + 8, blue)                  # the minute hand on the 9: a quarter to
            im.rect(32, y + 4, 33, y + 8, red)                   # the hour hand short of 12
            y += 17
            continue
        if s == "-":
            im.rect(12, y + 1, 52, y + 2, red)
            y += 5
            continue
        if s == "1":                                             # the experiment's number, big
            im.disc(32, y + 6, 6.5, red)
            digit(im, "1", 30, y + 2, (248, 248, 244), 1)
            digit(im, "1", 31, y + 2, (248, 248, 244), 1)
            y += 15
            continue
        w = len(s) * 6 - 1
        text(im, s, 32 - w // 2, y, red if c == "r" else blue, 1)
        y += 9
    im.disc(32, y1 - 0.5, 1.5, (80, 80, 84))                     # the pin
    return im


def calendar(part, look, shift=0, w=32, day="14"):
    """32 wide: a tear-off calendar's page, one bold day. Look 3 (now): the
    same page, forty years yellowed."""
    im = on_wall(look, part, w, shift)
    now = look == 3
    paper = (226, 206, 150) if now else (248, 248, 242)
    red = (150, 70, 50) if now else (206, 36, 30)
    ink = (90, 72, 50) if now else (30, 30, 34)
    x1, x2, y1 = w // 2 - 13, w // 2 + 13, 108
    im.rect(x1 + 1, y1 + 1, x2 + 1, y1 + 47, (50, 46, 40))
    im.rect(x1, y1, x2, y1 + 8, red)                             # the block's head, the month
    im.rect(x1 + 2, y1 + 3, x2 - 2, y1 + 5, shade(red, 1.25) if not now else (180, 110, 80))
    fill(im, x1, y1 + 8, x2, y1 + 46, paper, 0.02, 5300 + look)
    for k, ch in enumerate(day):                                 # the day, bold
        digit(im, ch, w // 2 - 9 + k * 10, y1 + 13, ink, 3)
    for x in range(x1 + 3, x2 - 3, 3):                           # its weekday, a line of small print
        im.rect(x, y1 + 33, x + 2, y1 + 34, red)
    im.rect(x1, y1 + 44, x2, y1 + 46, shade(paper, 0.8))          # the pages under it
    for x in range(x1, x2):                                      # the stubs of torn-off pages at the head
        if x % 3:
            im.set(x, y1 + 8, shade(paper, 0.85))
    if now:                                                      # foxed, curled at a corner, a fly-speck
        rnd = random.Random(5310)
        for _ in range(26):
            blend(im, rnd.randrange(x1, x2), rnd.randrange(y1 + 8, y1 + 46), (150, 110, 60), 0.35)
        for i in range(6):
            im.rect(x2 - 6 + i, y1 + 40 - i, x2, y1 + 41 - i, shade(paper, 0.7))
    im.noise(1, 5320 + look)
    return im


# === now: where it stood ======================================================================================
@contextmanager
def _unworn():
    """gfx_institute's walls without what time did to them (look 3 as painted)."""
    keep = {k: getattr(GI, k) for k in ("drips", "blot", "peel", "scuffs", "grime")}
    for k in keep:
        setattr(GI, k, lambda *a, **kw: None)
    try:
        yield
    finally:
        for k, v in keep.items():
            setattr(GI, k, v)


_CLEAN = {}


def clean_wall(part, look=3):
    if (part, look) not in _CLEAN:
        with _unworn():
            _CLEAN[(part, look)] = GI.wall(look, part)
    return _CLEAN[(part, look)]


def ghost(part, w, rects, shift=0, seed=0, look=3, stubs=None):
    """The wall `part` of look 3, w wide (`shift` into its 64), where things
    stood or hung: in each rectangle (x1, y1, x2, y2; y from the top of the
    256) the paint as it was painted, unfaded and unworn, a rim of dirt round
    it, bolt holes at its corners and here and there a cut cable.
    `stubs`: for each rectangle, how many cables (default: 1 for a big one)."""
    base = GI.wall(look, part)
    clean = clean_wall(part, look)
    im = Img(w, base.h)
    for y in range(base.h):
        for x in range(w):
            im.px[y * w + x] = list(base.px[y * 64 + (x + shift) % 64])
    rnd = random.Random(6000 + seed)
    for i, (x1, y1, x2, y2) in enumerate(rects):
        x1, x2 = max(0, x1), min(w, x2)
        y1, y2 = max(0, y1), min(base.h, y2)
        # on a pale wall (the yellowed whitewash over the dado) the same ghost hardly shows: there the
        # paint as it was is whiter and the soot round it darker, by how pale the wall is where it hung
        lum = sum(sum(base.px[y * 64 + (x + shift) % 64][:3]) / 3 for y in range(y1, y2) for x in range(x1, x2))
        k_pale = min(1.0, max(0.0, (lum / max(1, (y2 - y1) * (x2 - x1)) - 110) / 70))
        sat, bright = 1.4 + 0.3 * k_pale, 1.2 + 0.1 * k_pale
        soot, edge = 0.42 + 0.33 * k_pale, 0.6 + 0.3 * k_pale
        for y in range(y1, y2):
            for x in range(x1, x2):
                p = clean.px[y * 64 + (x + shift) % 64][:3]
                g = sum(p) / 3                                   # unfaded: brighter, the colour as it was
                q = shade(tuple(g + (v - g) * sat for v in p), bright)
                if k_pale:                                       # whitewash as it was: whiter, not yellower
                    q = mix(q, (250, 250, 244), 0.35 * k_pale)
                im.px[y * w + x] = list(q) + [255]
        for x in range(x1 - 8, x2 + 8):                          # the soot and dirt that settled round it
            for k in range(8):
                blend(im, x, y1 - 1 - k, (50, 44, 34), soot * (1 - k / 8) * (1 - max(0, max(x1 - x, x - x2 + 1)) / 9))
        for y in range(y1, y2):
            for k in range(6):
                blend(im, x1 - 1 - k, y, (50, 44, 34), soot * 0.86 * (1 - k / 6))
                blend(im, x2 + k, y, (50, 44, 34), soot * 0.86 * (1 - k / 6))
        for x in range(x1, x2):                                  # the paint's edge: a hard line where it stood
            blend(im, x, y1, (40, 36, 30), edge)
            blend(im, x, y1 + 1, (255, 255, 250), 0.3)
        for y in range(y1, y2):
            blend(im, x1, y, (40, 36, 30), edge - 0.1)
            blend(im, x2 - 1, y, (40, 36, 30), edge - 0.1)
        if y2 < base.h:
            for x in range(x1, x2):
                blend(im, x, y2 - 1, (40, 36, 30), edge - 0.1)
                for k in range(1, 5):                            # under a thing that hung, the soot too
                    blend(im, x, y2 - 1 + k, (50, 44, 34), soot * 0.6 * (1 - k / 5))
        inset = 4 if min(x2 - x1, y2 - y1) > 24 else 2
        holes = [(x1 + inset, y1 + inset), (x2 - 1 - inset, y1 + inset)]
        if y2 < base.h - 4:                                      # a thing that hung: its lower holes too
            holes += [(x1 + inset, y2 - 1 - inset), (x2 - 1 - inset, y2 - 1 - inset)]
        else:
            holes += [(x1 + inset, y2 - 14), (x2 - 1 - inset, y2 - 14)]
        if x2 - x1 >= 128:
            holes += [((x1 + x2) // 2, y1 + inset)]
        for hx, hy in holes:
            im.disc(hx, hy, 1.6, (34, 28, 24))
            im.set(hx - 1, hy - 1, (150, 140, 120))
            for k in range(rnd.randrange(3, 9)):                 # rust run down from it
                blend(im, hx, hy + 2 + k, RUST, 0.45 * (1 - k / 9))
        n = stubs[i] if stubs else (1 if (x2 - x1) * (y2 - y1) > 3000 else 0)
        for _ in range(n):                                       # a cable cut off at the wall
            cx = rnd.randrange(x1 + 10, max(x1 + 11, x2 - 10))
            cy = rnd.randrange(y1 + 8, max(y1 + 9, min(y2 - 8, y1 + 40)))
            im.disc(cx, cy, 3, (30, 26, 22))                     # the hole, a gland
            im.disc(cx, cy, 2, (70, 72, 70))
            col = rnd.choice(((30, 30, 32), (150, 40, 30), (60, 60, 66)))
            drop = rnd.randrange(6, 14)
            for k in range(drop):
                im.rect(cx - 1 + (k // 5) * rnd.choice((0, 1)), cy + k, cx + 1 + (k // 5), cy + k + 1, col)
            im.rect(cx - 1, cy + drop, cx + 1, cy + drop + 2, COPPER)
    im.noise(1, 6100 + seed)
    return im


GHOSTS = {}         # (wall, w, shift, rects, stubs): name; the map asks (ghost_name), make() draws them


def ghost_name(part, w, rects, shift=0, stubs=None):
    key = (part, w, shift, tuple(tuple(r) for r in rects), tuple(stubs) if stubs else None)
    return GHOSTS.setdefault(key, f"AJUG{len(GHOSTS):02d}")


# where each picture covers its wall (x1, y1, x2, y2, y from the top): the size of its ghost now
RECT = {"SC": (6, 66, 122, 200), "PB": (8, 78, 120, 178), "WN": (4, 68, 124, 202), "PP": (16, 0, 48, 222),
        "NT": (1, 116, 64, 229), "GB": (8, 74, 120, 192)}
HOME = {"SC": "EX", "PB": "AR", "WN": "CO", "PP": "LA", "GB": "LA"}         # the wall each is drawn for (its standing name)
PICS = {}           # (kind, look, wall, shift): name, for any other wall or shift


def picture_name(kind, look, part, shift=0):
    """The name of picture `kind` (SC, PB, WN, PP in the apparatus' `look`; NT, and CL with `look` the
    wall's: 2 then, 3 now) on the wall `part` of look 2 (CL: of `look`), `shift` into its 64."""
    if kind in HOME and part == HOME[kind] and not shift:
        return name(kind, look)
    if kind == "NT" and not shift:
        return f"AJUNT{part}2"
    if kind == "CL" and not shift and part == "EX":
        return f"AJUCLEX{look}"
    return PICS.setdefault((kind, look, part, shift), f"AJUP{len(PICS):02d}")


def picture(kind, look, part, shift):
    if kind == "NT":
        return notice(part, 2, shift)
    if kind == "CL":
        return calendar(part, look, shift)
    return {"SC": schematic, "PB": passboard, "WN": newspaper, "PP": pipe_run, "GB": gauge_board}[kind](look, shift, part)


# === flats: the duct ==========================================================================================
def duct(now):
    """64x64, 32 wide runs: then chequer-plate covers; now the covers gone,
    the channel open, the cables cut."""
    rnd = random.Random(6200 + now)
    if not now:
        steel = (150, 156, 160)
        im = Img(64, 64, steel)
        for ty in (0, 32):
            for tx in (0, 32):
                for y in range(ty, ty + 32):
                    for x in range(tx, tx + 32):
                        u, v = (x - tx) % 8, (y - ty) % 8
                        a = (x // 8 + y // 8) % 2
                        on = (abs(u - 3.5) + abs(v - 3.5) < 2.2) if True else False
                        f = 1.0 + (0.2 if on and a else 0.12 if on else 0) + rnd.uniform(-0.03, 0.03)
                        im.set(x, y, shade(steel, f))
                im.frame(tx, ty, tx + 32, ty + 32, shade(steel, 0.55), 1)
                im.rect(tx + 1, ty + 1, tx + 31, ty + 2, shade(steel, 1.25))
                for bx, by in ((tx + 3, ty + 3), (tx + 28, ty + 3), (tx + 3, ty + 28), (tx + 28, ty + 28)):
                    im.disc(bx, by, 1.4, shade(steel, 0.6))
                    im.set(bx - 1, by - 1, shade(steel, 1.4))
        im.noise(3, 6210)
        return im
    im = Img(64, 64, (22, 20, 18))
    for y in range(64):
        for x in range(64):
            im.set(x, y, shade((26, 24, 22), rnd.uniform(0.8, 1.2)))
    for ty in (0, 32):                                           # the angle-iron rims the covers lay on, rusted
        for tx in (0, 32):
            im.frame(tx, ty, tx + 32, ty + 32, (96, 62, 40), 2)
            im.rect(tx, ty, tx + 32, ty + 1, (140, 96, 60))
            for bx, by in ((tx + 3, ty + 3), (tx + 28, ty + 3), (tx + 3, ty + 28), (tx + 28, ty + 28)):
                im.disc(bx, by, 1.2, (40, 30, 24))
    for _ in range(9):                                           # cables cut off: a stub, its copper
        x, y = rnd.randrange(5, 59), rnd.randrange(5, 59)
        col = rnd.choice(((30, 30, 32), (140, 40, 30), (70, 70, 76), (40, 60, 120)))
        dx, dy = rnd.choice(((1, 0), (0, 1), (1, 1), (-1, 1)))
        ln = rnd.randrange(5, 12)
        for k in range(ln):
            im.disc(x + dx * k, y + dy * k, 1.2, col)
        im.disc(x + dx * ln, y + dy * ln, 1, COPPER)
    for _ in range(4):
        x, y = rnd.randrange(64), rnd.randrange(64)
        GI.blot(im, x, y, rnd.randrange(4, 9), (80, 70, 50), 0.4, wrap=True)
    im.noise(3, 6220)
    return im


# === sprites ==================================================================================================
def _sprite(w, h):
    return Img(w, h, (0, 0, 0, 0))


def wheels(im, xs, y, c=(30, 30, 32)):
    for x in xs:
        im.disc(x, y, 3.2, c)
        im.disc(x, y, 1.2, (150, 150, 150))


def trolley(n):
    """S1, 40x56: an instrument on a trolley."""
    im = _sprite(40, 56)
    frame = {1: ALU, 2: BAK, 3: NICKEL}[n]
    for x in (3, 35):                                            # the uprights
        cyl_v(im, x, 24, x + 2, 52, frame, 1.3, 0.6)
    im.rect(1, 50, 39, 52, frame)                                # the lower shelf
    im.rect(1, 36, 39, 38, frame)
    wheels(im, (5, 35), 53)
    if n == 1:                                                   # an oscilloscope on top, a box below
        im.rect(2, 2, 38, 36, GB)
        bevel(im, 2, 2, 38, 36, GB)
        im.rect(2, 2, 38, 6, CREAM)
        im.disc(15, 19, 10, CREAM)
        im.disc(15, 19, 8.5, SCOPE)
        for x in range(8, 23):
            im.set(x, round(19 + 4 * math.sin((x - 8) * 0.8)), TRACE)
        im.disc(12, 16, 1.5, (255, 255, 255))
        for y, c in ((12, INK), (22, INK)):
            im.disc(31, y, 3, c)
            im.rect(30, y - 3, 32, y, KEY)
        im.rect(28, 28, 35, 32, ORANGE)
        lamp(im, 31, 3.5, 1.2, AMBER, True)
        im.rect(6, 40, 34, 50, CREAM)
        im.rect(9, 43, 18, 46, INK)
        lamp(im, 28, 45, 1.6, GREEN, True)
    elif n == 2:                                                 # a set of three meters in bakelite, wire below
        im.rect(1, 8, 39, 36, BAK)
        im.rect(1, 8, 39, 10, (70, 64, 58))
        for cx, a in ((8, 0.3), (20, 0.6), (32, 0.85)):
            needle_dial(im, cx, 20, 5.5, BAK, FACE, a)
        for cx in (8, 20, 32):
            im.disc(cx, 31, 2, (70, 64, 58))
            im.set(cx, 29, FACE)
        im.rect(14, 2, 26, 8, BRASS)
        for cx in (10, 30):                                      # terminals on top
            im.rect(cx - 2, 4, cx + 2, 8, COPPER)
        im.disc(20, 44, 6, (150, 112, 66))                       # a drum of copper wire below
        im.disc(20, 44, 4.5, COPPER)
        im.disc(20, 44, 1.6, BAK)
        lamp(im, 33, 44, 2, WARN, True, BAK)
    else:                                                        # a vacuum pump below, a glass trap on top
        im.rect(4, 39, 30, 50, CER)
        bevel(im, 4, 39, 30, 50, CER)
        im.disc(17, 44.5, 4, NICKEL)
        im.rect(1, 34, 39, 36, frame)
        im.rect(18, 26, 22, 34, NICKEL)
        for y in range(4, 26):                                   # a cold trap: a tall glass, violet inside
            hw = 6 if y > 8 else 4
            for x in range(20 - hw, 20 + hw):
                im.set(x, y, mix((40, 36, 60), VIOLET, 0.35 + 0.4 * (y - 4) / 22))
            im.set(20 - hw, y, (230, 236, 250))
            im.set(20 + hw - 1, y, (150, 160, 190))
        glow(im, 20, 18, 8, VIOLET, 0.5)
        im.rect(15, 2, 25, 4, NICKEL)
        hose(im, curve((25, 6), (34, 40), 4), HOSE, 1.4)
        hose(im, curve((30, 44), (38, 30), -3), HOSE, 1.2)
        needle_dial(im, 8, 20, 4.5, NICKEL, CER, 0.4)
    return im


def tall(n):
    """S2, 40x96: a tape drive; a coil on insulators; a tube on a stand."""
    im = _sprite(40, 96)
    if n == 1:
        im.rect(2, 0, 38, 96, GB)
        bevel(im, 2, 0, 38, 96, GB)
        im.rect(2, 0, 38, 8, CREAM)
        legend(im, "TAPE", 20, 0)
        im.rect(5, 10, 35, 56, (40, 46, 54))
        reel(im, 20, 21, 9, ALU, fullness=0.8)
        reel(im, 20, 44, 9, ALU, fullness=0.25)
        glass_glint(im, 5, 10, 35, 56, 0.15)
        for r in range(2):
            for col in range(5):
                q = (r * 5 + col) % 3
                lamp(im, 8 + col * 6, 62 + r * 6, 1.6, AMBER if q else GREEN, q != 2)
        for col in range(5):
            im.rect(6 + col * 6, 74, 10 + col * 6, 80, KEY if col != 2 else ORANGE)
        louvres(im, 6, 84, 34, 94, GB)
        im.rect(2, 94, 38, 96, (40, 42, 46))
    elif n == 2:
        im.rect(6, 88, 34, 96, BAK)                              # a base, porcelain columns, a winding, a ball
        insulator(im, 20, 52, 88, 14)
        im.rect(8, 50, 32, 53, COPPER)
        coil(im, 9, 18, 31, 50)
        im.rect(8, 17, 32, 19, shade(COPPER, 0.6))
        im.disc(20, 9, 8, shade(COPPER, 0.8))
        im.disc(20, 9, 7, COPPER)
        im.disc(17, 6, 2, COPPER_HI)
        lamp(im, 30, 90, 2, WARN, True, BAK)
        im.rect(10, 90, 18, 93, BRASS)
    else:
        for i, x in enumerate((6, 20, 34)):                      # a tripod in nickel
            for y in range(70, 96):
                im.set(round(20 + (x - 20) * (y - 70) / 26), y, NICKEL)
                im.set(round(20 + (x - 20) * (y - 70) / 26) + 1, y, shade(NICKEL, 0.6))
        cyl_v(im, 18, 40, 22, 72, NICKEL, 1.4, 0.6)
        for y in range(4, 60):                                   # a tall glass tube, glowing
            for x in range(13, 27):
                blend(im, x, y, (40, 36, 70), 0.0)
                im.set(x, y, mix((40, 36, 70), VIOLET if y < 36 else BLUE, 0.3 + 0.5 * math.sin(math.pi * (x - 13) / 14)))
            im.set(13, y, (220, 226, 250))
            im.set(26, y, (150, 160, 190))
            im.set(16, y, (240, 240, 255))
        for y in range(10, 54, 2):
            im.set(20, y, (255, 250, 255))
        glow(im, 20, 30, 18, VIOLET, 0.3)
        for y in (2, 58):                                        # caps and clamps
            im.rect(11, y, 29, y + 4, NICKEL)
            im.rect(11, y, 29, y + 1, (255, 255, 255))
        im.rect(8, 44, 32, 47, shade(NICKEL, 0.8))
        hose(im, curve((28, 4), (38, 70), 6), HOSE, 1.6)
    return im


COPPER_HI = (240, 176, 120)


def small(n):
    """S3, a thing on a desk: a desk radio; a telephone; a glass of tea in its holder."""
    if n == 1:
        im = _sprite(28, 18)
        im.rect(1, 2, 27, 18, CREAM)
        bevel(im, 1, 2, 27, 18, CREAM)
        im.rect(3, 4, 15, 16, (80, 74, 66))                      # the speaker cloth
        for y in range(5, 16, 2):
            im.rect(3, y, 15, y + 1, (60, 56, 50))
        im.rect(17, 5, 26, 9, (240, 220, 160))                   # the dial, lit
        im.rect(21, 5, 22, 9, LRED)
        im.disc(19, 13, 2, INK)
        im.disc(24, 13, 2, INK)
        im.rect(1, 0, 27, 2, ALU)
        glow(im, 21, 7, 6, AMBER, 0.25)
    elif n == 2:
        im = _sprite(26, 18)
        im.rect(2, 8, 24, 18, BAK)                               # the telephone's body, the dial, the handset
        im.rect(2, 8, 24, 9, (70, 66, 60))
        im.disc(13, 13, 4, FACE)
        im.disc(13, 13, 1.5, BAK)
        cyl_h(im, 0, 2, 26, 6, BAK, 2.2, 0.8)
        im.rect(0, 2, 5, 9, BAK)
        im.rect(21, 2, 26, 9, BAK)
        im.rect(4, 15, 8, 17, BRASS)
    else:
        im = _sprite(16, 22)
        for y in range(6, 18):                                   # the tea in its glass
            im.rect(3, y, 13, y + 1, mix((150, 60, 20), (230, 120, 60), (y - 6) / 14))
        im.rect(3, 4, 13, 6, (210, 220, 226))
        for y in range(10, 22):                                  # the nickel holder, its handle
            im.rect(2, y, 14, y + 1, shade(NICKEL, 0.8 + 0.4 * ((y % 3) == 0)))
        im.rect(13, 11, 16, 13, NICKEL)
        im.rect(14, 11, 16, 19, NICKEL)
        im.rect(13, 17, 16, 19, NICKEL)
        im.rect(9, 0, 10, 12, (220, 224, 230))                   # the spoon
        im.set(4, 7, (255, 255, 255))
    return im


def emitter(n, wreck=False, off=False):
    """EM, 40x72: the beam's emitter on its stand (then: lit, or `off`: the beam set to OFF), or its
    wreck (now)."""
    im = _sprite(40, 72)
    rnd = random.Random(6300 + n + 10 * wreck)
    stand = {1: GB, 2: BAK, 3: NICKEL}[n]
    if wreck:
        stand = mix(stand, RUST, 0.6)
    for i, x in enumerate((4, 20, 36)):                          # a tripod
        for y in range(52, 72):
            im.set(round(20 + (x - 20) * (y - 52) / 20), y, stand)
            im.set(round(20 + (x - 20) * (y - 52) / 20) + 1, y, shade(stand, 0.6))
    cyl_v(im, 17, 34, 23, 54, stand, 1.3, 0.6)
    if n == 1:
        body, lens = GB, (140, 200, 255)
        im.rect(4, 8, 36, 34, CREAM if not wreck else (150, 136, 110))
        im.rect(6, 10, 34, 32, body if not wreck else mix(body, RUST, 0.5))
        im.disc(20, 20, 9, ALU if not wreck else (110, 100, 90))
        im.disc(20, 20, 7, (30, 34, 44))
        if not wreck:
            im.disc(20, 20, 5, lens if not off else (44, 56, 70))
            if not off:
                glow(im, 20, 20, 12, lens, 0.4)
            im.disc(18, 18, 1.5, (255, 255, 255) if not off else (120, 130, 140))
            im.rect(4, 2, 36, 7, CREAM)
            for k, c in enumerate((AMBER, GREEN, LRED)):
                lamp(im, 11 + k * 9, 4.5, 1.5, c, not off or k == 2)
            im.rect(26, 28, 32, 31, ORANGE)
        else:
            im.rect(4, 2, 36, 7, (120, 110, 92))
    elif n == 2:
        if not wreck:
            insulator(im, 20, 38, 52, 10)
            coil(im, 8, 14, 32, 36)
            im.rect(6, 12, 34, 14, shade(COPPER, 0.6))
            im.rect(6, 36, 34, 38, shade(COPPER, 0.6))
            im.disc(20, 8, 7, COPPER)
            im.disc(18, 6, 2, COPPER_HI)
            if not off:
                glow(im, 20, 8, 12, (255, 220, 200), 0.4)
            lamp(im, 33, 44, 2, WARN, not off, BAK)
        else:
            insulator(im, 20, 38, 52, 10, (170, 164, 150))
            for y in range(20, 36):                              # the winding unwound, blackened
                im.rect(8, y, 32, y + 1, (60, 40, 30) if y % 3 else (40, 30, 24))
            for k in range(6):
                hose(im, curve((10 + k * 4, 20), (6 + k * 5, 6 + rnd.randrange(8)), 2), (90, 56, 36), 0.6)
            im.rect(6, 36, 34, 38, (70, 50, 36))
    else:
        if not wreck:
            for y in range(6, 36):                               # a glass tube across, violet, in nickel clamps
                for x in range(4, 36):
                    if abs(y - 21) < 8:
                        im.set(x, y, mix((36, 30, 60), VIOLET, (0.3 + 0.6 * (1 - abs(y - 21) / 8)) * (0.35 if off else 1)))
            if not off:
                glow(im, 34, 21, 10, BLUE, 0.6)
            im.disc(35, 21, 4, (230, 240, 255) if not off else (90, 96, 110))
            for x in (8, 30):
                im.rect(x, 11, x + 3, 32, NICKEL)
                im.rect(x, 11, x + 1, 32, (255, 255, 255))
            for x in range(4, 36):
                im.set(x, 14, (240, 240, 255))
            im.rect(14, 32, 26, 36, NICKEL)
            hose(im, curve((6, 28), (14, 50), 4), HOSE, 1.5)
        else:
            for x in range(4, 22):                               # the tube broken off, a jagged end
                for y in range(14, 29):
                    im.set(x, y, (50, 50, 56))
                im.set(x, 14, (170, 176, 186))
            for k in range(8):
                y = 14 + k * 2
                for x in range(22, 22 + rnd.randrange(2, 7)):
                    im.set(x, y, (120, 126, 136))
                    im.set(x, y + 1, (90, 96, 104))
            for x in (8, 30):
                im.rect(x, 11, x + 3, 32, (120, 110, 96))
            im.rect(14, 32, 26, 36, (110, 100, 86))
            hose(im, curve((6, 28), (10, 52), 2), (90, 40, 34), 1.4)
    if wreck:                                                    # rust, dents, dead
        for _ in range(60):
            x, y = rnd.randrange(40), rnd.randrange(72)
            p = im.px[y * 40 + x]
            if p[3]:
                im.set(x, y, shade(mix(p[:3], RUST, 0.6), rnd.uniform(0.6, 1.0)))
    return im


# === the machine: MAP21's centrepiece (map_longrun section 1, MACHINE) =====================================
# Each face is one composition at the face's real width, laid by the map from the face's start whatever pieces
# the face is cut into (exact="lower"): nothing is cut at a wall piece's end or at a corner. Every face shares
# the same bands, top to bottom, so that they go on round the corners: an aluminium cap rail, a vent grille
# (the crown), a cream band, the grey-blue body, an aluminium rail, the black plinth. THEN look 1 (Lamps and
# Reels) is AJUM<face>1; NOW AJUX<face>1 is the same drawing, dead (every element in the same place, drawn
# dead: lamps out, glass broken, reels gone, keys missing), then a ruin pass (the colours of NOW's hall:
# khaki and dark, soot, rust runs, dust) and some panels gone with cable guts behind. Looks 2 and 3 of the
# apparatus wear look 1's machine (only look 1 is chosen: PLAN.md, "MAP21's look board: Vadim's word").
#   N 256  the north face: the works; in the middle the port (a door's outline in brass, the same again
#          inside it, smaller, and again); either side tape reels, a lamp matrix, a scope, keys; the cable
#          trunk to the ceiling and the plate MACHINE 7 over the port
#   W 192  the west face (the body's side and the wing's in one plane), the power side: meters, a painted
#          service door, the cable entry where the floor duct comes in, a breaker, a louvre field; E its mirror
#   A 80   the west wing's south face, a tower of lamps and keys; B the east wing's, its mirror
#   I 64   the west wing's inner face (in the alcove before 101), a column of indicator lamps; J its mirror
#   K 16   the body's south face west of 101's mouth; L east of it
#   O 64   over 101's mouth, 160 high (the frame's head to the ceiling): a brass plate, the port's motif small
MACH_FACES = {"N": 256, "W": 192, "E": 192, "A": 80, "B": 80, "I": 64, "J": 64, "K": 16, "L": 16, "O": 64}
CAP, CROWN, BAND, FOOT, PLINTH = 3, 22, 38, 236, 240        # the rows where each band ends
PLINTH_C, GLASS_C, SEAM = (40, 42, 46), (34, 40, 50), shade(GB, 0.45)
VERDI, YELLOW_W = (84, 140, 112), (232, 196, 72)


def mach_name(face, now=False):
    return f"AJU{'X' if now else 'M'}{face}1"


def m_shell(w, h, seed, ends):
    """The bands of every face, w x h; `ends` (left, right): "alu" an outer corner's aluminium edge,
    "seam" an inner corner's shadow, None the face goes on (into the next piece of the same plane)."""
    im = Img(w, h)
    fill(im, 0, 0, w, h, GB, 0.012, seed)
    cyl_h(im, 0, 0, w, CAP, ALU, 1.25, 0.6)
    im.rect(0, CAP, w, CROWN, (40, 44, 52))
    for y in range(CAP + 2, CROWN - 1, 3):                       # the vent's slats
        im.rect(0, y, w, y + 1, (74, 80, 90))
        im.rect(0, y + 1, w, y + 2, (26, 28, 34))
    im.rect(0, CROWN, w, CROWN + 1, ALU)
    fill(im, 0, CROWN + 1, w, BAND - 1, CREAM, 0.01, seed + 1)
    im.rect(0, BAND - 1, w, BAND, shade(GB, 0.6))
    if h > FOOT:
        cyl_h(im, 0, FOOT, w, PLINTH, ALU, 1.3, 0.6)
        im.rect(0, PLINTH, w, h, PLINTH_C)
        im.rect(0, PLINTH, w, PLINTH + 1, shade(PLINTH_C, 0.5))
    for side, kind in enumerate(ends):
        x = 0 if side == 0 else w - 2
        if kind == "alu":
            cyl_v(im, x, CAP, x + 2, h, ALU, 1.25, 0.65)
        elif kind == "seam":
            for k in range(4):
                for y in range(BAND, min(h, FOOT)):
                    blend(im, k if side == 0 else w - 1 - k, y, (20, 22, 28), 0.45 * (1 - k / 4))
    return im


def m_panel(im, x1, y1, x2, y2, c=GB, up=True):
    """A panel of the body: its edges, a screw at each corner."""
    bevel(im, x1, y1, x2, y2, c, 1, up)
    for x, y in ((x1 + 2, y1 + 2), (x2 - 4, y1 + 2), (x1 + 2, y2 - 3), (x2 - 4, y2 - 3)):
        screw(im, x, y, c)


def m_bay(im, x1, y1, x2, y2, ground=GLASS_C):
    """A glazed or sunk bay: an aluminium frame, a dark ground."""
    im.rect(x1, y1, x2, y2, shade(ALU, 0.75))
    im.rect(x1, y1, x2, y1 + 1, shade(ALU, 1.2))
    im.rect(x1 + 2, y1 + 2, x2 - 2, y2 - 2, ground)
    im.rect(x1 + 2, y1 + 2, x2 - 2, y1 + 3, shade(ground, 0.6))


def m_line(im, a, b, c, f=1.0):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for i in range(n + 1):
        blend(im, round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n), c, f)


def m_cracks(im, cx, cy, box, rnd, n=7, c=(206, 212, 214), hole=0):
    """Glass broken from a blow at cx, cy: cracks out to the bay's edge, a hole there."""
    x1, y1, x2, y2 = box
    for k in range(n):
        a = 2 * math.pi * (k + rnd.uniform(-0.3, 0.3)) / n
        x, y = cx, cy
        while x1 + 1 < x < x2 - 2 and y1 + 1 < y < y2 - 2:
            a += rnd.uniform(-0.5, 0.5) if rnd.random() < 0.2 else 0     # straight, with a kink now and then
            nx, ny = x + 3 * math.cos(a), y + 3 * math.sin(a)
            m_line(im, (x, y), (nx, ny), c, 0.7)
            x, y = nx, ny
    if hole:
        pts = [(cx + hole * rnd.uniform(0.6, 1.2) * math.cos(t), cy + hole * rnd.uniform(0.6, 1.2) * math.sin(t))
               for t in [2 * math.pi * i / 9 for i in range(9)]]
        for y in range(int(cy - hole * 1.3), int(cy + hole * 1.3) + 1):
            for x in range(int(cx - hole * 1.3), int(cx + hole * 1.3) + 1):
                if x1 + 2 <= x < x2 - 2 and y1 + 2 <= y < y2 - 2 and _inside(x, y, pts):
                    im.set(x, y, (8, 8, 10))
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):           # the shards' edges, catching the light
            if x1 + 2 <= ax < x2 - 2 and y1 + 2 <= ay < y2 - 2:
                m_line(im, (ax, ay), (bx, by), (226, 230, 232), 0.55)


def _inside(x, y, pts):
    c = False
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        if (ay > y) != (by > y) and x < ax + (bx - ax) * (y - ay) / (by - ay):
            c = not c
    return c


def m_guts(im, x1, y1, x2, y2, rnd):
    """A panel gone: the cavity behind, a rail, cables hanging in loops, cut ends, the screw holes round it."""
    fill(im, x1, y1, x2, y2, (22, 20, 18), 0.15, rnd.randrange(999))
    for x in range(x1, x2):                                      # the shadow under the opening's top edge
        for k in range(4):
            blend(im, x, y1 + k, (0, 0, 0), 0.6 * (1 - k / 4))
    for y in (y1 + (y2 - y1) // 3, y1 + 2 * (y2 - y1) // 3):    # rails behind, rusted
        im.rect(x1 + 1, y, x2 - 1, y + 2, (92, 64, 44))
    for _ in range(max(3, (x2 - x1) // 6)):
        a = (rnd.uniform(x1 + 2, x2 - 2), y1 + rnd.uniform(2, 8))
        b = (rnd.uniform(x1 + 2, x2 - 2), rnd.uniform(y1 + (y2 - y1) * 0.4, y2 - 2))
        col = rnd.choice(((24, 24, 26), (150, 44, 34), (86, 88, 92), (40, 66, 130), (190, 160, 60)))
        hose(im, curve(a, b, rnd.uniform(2, 9), 10), col, 1.0)
        im.disc(b[0], b[1] + 1, 1, COPPER)
    for x, y in ((x1 - 2, y1 - 2), (x2 + 1, y1 - 2), (x1 - 2, y2 + 1), (x2 + 1, y2 + 1)):
        im.disc(x, y, 1, (30, 24, 20))


def m_reels(im, x1, y1, x2, y2, rnd, dead=0):
    """A tape drive's bay: two reels behind glass, the tape round the head. Dead: 1 the reels gone, the glass
    broken; 2 one reel left, the tape hanging."""
    m_bay(im, x1, y1, x2, y2)
    w, h = x2 - x1, y2 - y1
    cy, r = y1 + int(h * 0.4), min(w * 0.21, h * 0.32)
    cxs = (x1 + w * 0.28, x1 + w * 0.72)
    hx, hy = (x1 + x2) // 2, y2 - 10
    if not dead:
        reel(im, cxs[0], cy, r, ALU, fullness=0.7 + rnd.uniform(-0.1, 0.1))
        reel(im, cxs[1], cy, r, ALU, fullness=0.35 + rnd.uniform(-0.1, 0.1))
        tape = (88, 66, 46)
        m_line(im, (cxs[0] - r * 0.55, cy + r * 0.5), (hx - 6, hy), tape)
        m_line(im, (cxs[1] + r * 0.4, cy + r * 0.6), (hx + 6, hy), tape)
    else:
        for i, cx in enumerate(cxs):
            if dead == 2 and i == 1:                             # the one left, the tape run off it
                reel(im, cx, cy + 2, r, shade(ALU, 0.8), fullness=0.15)
                hose(im, curve((cx - 3, cy + r), (cx - 9, y2 + 18), 5, 14), (80, 60, 44), 0.6)
            else:                                                # its hub, the spindle, the motor plate's bolts
                im.disc(cx, cy, r * 0.55, shade(GLASS_C, 0.7))
                im.disc(cx, cy, 3.4, (96, 98, 104))
                im.disc(cx, cy, 1.4, INK)
                for k in range(3):
                    a = k * 2 * math.pi / 3
                    im.set(round(cx + 6 * math.cos(a)), round(cy + 6 * math.sin(a)), (120, 120, 124))
    im.rect(hx - 7, hy - 3, hx + 7, hy + 5, shade(ALU, 0.9))    # the head
    im.rect(hx - 4, hy - 1, hx + 4, hy + 1, INK)
    if not dead:
        glass_glint(im, x1 + 2, y1 + 2, x2 - 2, y2 - 2, 0.2)
    else:
        m_cracks(im, rnd.uniform(x1 + 8, x2 - 8), rnd.uniform(y1 + 8, y2 - 14), (x1, y1, x2, y2), rnd, 7,
                 hole=6 if dead == 1 else 3)


def m_lamps(im, x1, y1, x2, y2, cols, rows, rnd, dead=0, lit=None, r=2.2):
    """A field of small round lamps in a dark panel. `lit`(col, row): a colour or None; dead: the lamps out,
    some lenses gone."""
    m_bay(im, x1, y1, x2, y2, (46, 50, 58))
    dx, dy = (x2 - x1 - 4) / cols, (y2 - y1 - 4) / rows
    for row in range(rows):
        for col in range(cols):
            x, y = x1 + 2 + dx * (col + 0.5), y1 + 2 + dy * (row + 0.5)
            c = lit(col, row) if lit else (AMBER if rnd.random() < 0.38 else GREEN if rnd.random() < 0.08 else None)
            if dead:
                if rnd.random() < 0.22:                          # the lens gone: its socket
                    im.disc(x, y, r, (12, 12, 14))
                    im.set(round(x), round(y), (90, 80, 60))
                else:
                    lamp(im, x, y, r, shade(AMBER_OFF, rnd.uniform(0.7, 1.0)), False)
            else:
                lamp(im, x, y, r, c or AMBER_OFF, c is not None)


def m_scope(im, cx, cy, r, rnd, dead=0):
    """A round green scope in a cream bezel; dead, its screen smashed."""
    im.disc(cx, cy, r, CREAM)
    im.disc(cx, cy, r - 1, shade(CREAM, 0.78))
    im.disc(cx, cy, r - 3, SCOPE if not dead else (30, 36, 34))
    if not dead:
        for x in range(int(cx - r), int(cx + r) + 1, 4):         # the graticule
            for y in range(int(cy - r), int(cy + r) + 1, 2):
                if (x - cx) ** 2 + (y - cy) ** 2 < (r - 4) ** 2:
                    blend(im, x, y, (90, 140, 110), 0.5)
        ph = rnd.uniform(0, 6)
        for x in range(int(cx - r + 4), int(cx + r - 3)):
            y = cy + (r - 7) * 0.7 * math.sin((x - cx) * 0.5 + ph)
            im.disc(x, y, 0.8, TRACE)
            glow(im, x, y, 2.5, TRACE, 0.15)
        im.disc(cx - r * 0.35, cy - r * 0.35, 2.2, (255, 255, 255))
    else:
        box = (int(cx - r + 3), int(cy - r + 3), int(cx + r - 3), int(cy + r - 3))
        m_cracks(im, cx + rnd.uniform(-3, 3), cy + rnd.uniform(-3, 3), box, rnd, 8, (170, 186, 176),
                 hole=(r - 3) * 0.45 if dead == 1 else 0)
        for y in range(box[1] - 2, box[3] + 3):                  # (nothing past the bezel)
            for x in range(box[0] - 2, box[2] + 3):
                if (x - cx) ** 2 + (y - cy) ** 2 > (r - 3) ** 2 and (x - cx) ** 2 + (y - cy) ** 2 <= (r - 1) ** 2:
                    im.set(x, y, shade(CREAM, 0.78))


def m_knob(im, cx, cy, r, a=0.5, dead=False):
    if dead and a < 0:                                           # gone: its shaft
        im.disc(cx, cy, r * 0.4, (90, 90, 94))
        return
    im.disc(cx, cy, r, INK)
    im.disc(cx - 0.5, cy - 0.5, r - 1, (64, 64, 70))
    t = math.pi * (0.75 + 1.5 * a)
    m_line(im, (cx, cy), (cx + (r - 1) * math.cos(t), cy + (r - 1) * math.sin(t)), KEY)


def m_keys(im, x1, y, n, pitch, kw, kh, rnd, dead=0, orange=()):
    """A row of white keys (some orange); dead, some gone."""
    for k in range(n):
        x = x1 + k * pitch
        if dead and rnd.random() < 0.3:
            im.rect(x, y, x + kw, y + kh, (16, 16, 18))
            im.rect(x + kw // 2 - 1, y + kh // 2, x + kw // 2 + 1, y + kh - 1, (90, 90, 94))
            continue
        c = ORANGE if k in orange else KEY
        if dead:
            c = mix(c, (200, 180, 120), 0.4)
        im.rect(x, y, x + kw, y + kh, shade(c, 0.66))
        im.rect(x, y, x + kw, y + kh - 2, c)
        im.rect(x, y, x + kw, y + 1, shade(c, 1.1))


def m_meter(im, cx, cy, r, a, rnd, dead=False):
    im.disc(cx, cy, r + 2, CREAM)
    needle_dial(im, cx, cy, r, ALU, FACE, 0.02 if dead else a)
    if dead:
        m_cracks(im, cx + rnd.uniform(-3, 3), cy - 2, (cx - r + 2, cy - r + 2, cx + r - 1, cy + r - 1), rnd, 5,
                 (120, 120, 116))
    else:
        im.disc(cx - r * 0.4, cy - r * 0.45, 1.5, (255, 255, 255))


def door_motif(im, cx, cy, w, h, levels, c, t=1, ground=None, f=0.62, vy=0.35):
    """A door's outline, the same again inside it, smaller, and again: `levels` outlines w x h at the largest,
    each next one f the size, drawn towards a point vy of the way up from the door's foot."""
    vx, vyy = cx, cy + h / 2 - h * vy
    for k in range(levels):
        s = f ** k
        x1, x2 = round(vx + (cx - w / 2 - vx) * s), round(vx + (cx + w / 2 - vx) * s)
        y1, y2 = round(vyy + (cy - h / 2 - vyy) * s), round(vyy + (cy + h / 2 - vyy) * s)
        tk = max(1, round(t * s))
        cc = c[k] if isinstance(c, list) else c
        im.frame(x1, y1, x2, y2, cc, tk)
        if ground:
            im.rect(x1 + tk, y1 + tk, x2 - tk, y2 - tk, ground[k])


# --- the faces --------------------------------------------------------------------------------------------
def face_N(dead):
    """The north face, 256: the works. Symmetric about its middle (x 512 in the map)."""
    W = 256
    rnd = random.Random(7100 + 13 * dead)
    im = m_shell(W, 256, 7100, ("alu", "alu"))
    for x in (78, 176):                                          # the joints of the three bays
        im.rect(x, BAND, x + 1, FOOT, SEAM)
        cyl_v(im, x + 1, BAND, x + 2, FOOT, ALU, 1.2, 0.8)
    # the port: a door's outline in brass, the same again inside it, smaller, and again; dark glass over them
    px1, py1, px2, py2 = 82, 44, 174, 206
    im.rect(px1, py1, px2, py2, shade(ALU, 0.7))
    im.rect(px1, py1, px2, py1 + 1, shade(ALU, 1.25))
    im.rect(px1 + 3, py1 + 3, px2 - 3, py2 - 3, (14, 16, 24))
    for y in range(py1 + 3, py2 - 3):                            # the dark inside, a little light far in
        for x in range(px1 + 3, px2 - 3):
            d = math.hypot((x - 128) / 46, (y - 150) / 80)
            blend(im, x, y, (40, 60, 90), 0.5 * max(0, 1 - d))
    brass = [BRASS, shade(BRASS, 0.86), shade(BRASS, 0.72)]
    door_motif(im, 128, 126, 76, 140, 3, brass, 4, f=0.6, vy=0.3)
    if dead:
        im.disc(128, 165, 2, (60, 50, 40))                       # the light far in, out
    else:
        glow(im, 128, 165, 9, (255, 214, 150), 0.6)
        im.disc(128, 165, 1.5, (255, 236, 200))
    for x, y in ((px1 + 1, py1 + 1), (px2 - 3, py1 + 1), (px1 + 1, py2 - 3), (px2 - 3, py2 - 3)):
        screw(im, x, y, ALU)
    if dead:
        m_cracks(im, 104, 178, (px1 + 2, py1 + 2, px2 - 2, py2 - 2), rnd, 9, (190, 196, 200), hole=13)
        m_cracks(im, 150, 70, (px1 + 2, py1 + 2, px2 - 2, py2 - 2), rnd, 5, (150, 156, 160))
        for y in range(py1 + 3, py2 - 3):                        # the brass gone green in places
            for x in range(px1 + 3, px2 - 3):
                p = im.px[y * W + x]
                if p[0] - p[2] > 70 and rnd.random() < 0.45:
                    blend(im, x, y, VERDI, 0.55)
    else:
        glass_glint(im, px1 + 3, py1 + 3, px2 - 3, py2 - 3, 0.16)
        glass_glint(im, px1 + 40, py1 + 60, px2 - 3, py2 - 3, 0.08)
    # either side, the same bays (each its own lamps and its own damage)
    for side in (0, 1):
        def X(x, w=0):
            return x if side == 0 else W - x - w
        dmg = (1, 2)[side] if dead else 0
        m_panel(im, X(4, 72), 40, X(4, 72) + 72, 232)
        m_reels(im, X(8, 66), 44, X(8, 66) + 66, 106, rnd, dmg)
        if dead and side == 1:                                   # the lamp matrix's panel gone
            m_bay(im, X(10, 62), 112, X(10, 62) + 62, 158)
            m_guts(im, X(12, 58), 114, X(12, 58) + 58, 156, rnd)
        else:
            m_lamps(im, X(10, 62), 112, X(10, 62) + 62, 158, 7, 5, rnd, dead)
        m_scope(im, X(28), 182, 17, rnd, (1, 2)[side] if dead else 0)
        m_knob(im, X(62), 172, 4.5, rnd.random(), dead)
        m_knob(im, X(62), 192, 4.5, rnd.random() if not (dead and side == 0) else -1, dead)
        im.rect(X(52, 18), 202, X(52, 18) + 18, 204, ORANGE)
        m_keys(im, X(10, 63), 208, 7, 9, 7, 12, rnd, dead, orange=(6,) if side == 0 else (0,))
    m_keys(im, 92, 210, 8, 9, 7, 10, rnd, dead, orange=(3, 4))  # under the port
    louvres(im, 6, 224, W - 6, 234, GB, 3)
    # the cable trunk up to the ceiling, the cables along the crown into it
    for y0, sag, col in ((8, 3, (30, 30, 34)), (13, 2, (52, 54, 60)), (17, 3, ORANGE)):
        for a, b in (((6, y0), (110, y0 + 1)), ((W - 6, y0), (146, y0 + 1))):
            if dead and col == ORANGE and a[0] > 128:
                hose(im, curve(b, (b[0] + 14, y0 + 26), 4, 8), col, 1.2)     # cut, hanging
                continue
            hose(im, curve(a, b, sag), col, 1.4)
    cyl_v(im, 110, 0, 146, CROWN + 2, ALU, 1.3, 0.55)
    for y in range(1, CROWN + 2, 4):                             # its ribs
        im.rect(110, y, 146, y + 1, shade(ALU, 0.6))
    im.rect(108, CROWN, 148, CROWN + 2, shade(ALU, 0.8))
    # the one plate: the machine's name, as the hall's schematic gives it
    s = "MACHINE 7"
    tw = len(s) * 12 - 2
    im.rect(128 - tw // 2 - 5, 24, 128 + tw // 2 + 6, 37, INK)
    im.rect(128 - tw // 2 - 5, 24, 128 + tw // 2 + 6, 25, (70, 70, 76))
    text(im, s, 128 - tw // 2, 26, (236, 236, 228), 2)
    for x in (128 - tw // 2 - 3, 128 + tw // 2 + 3):
        if not (dead and x > 128):
            im.disc(x, 30.5, 1, ALU)
    return m_finish(im, dead, 7100)


def face_W(dead, mirror=False):
    """The west face, 192 (u 0 at the north end): the power side. Mirrored, the east face (u 0 at its south
    end): the same elements at the same places along the machine."""
    W = 192
    rnd = random.Random(7200 + 13 * dead + 5 * mirror)

    def X(x, w=0):
        return x if not mirror else W - x - w

    im = m_shell(W, 256, 7200 + mirror, ("alu", "alu"))
    im.rect(X(128, 1), BAND, X(128, 1) + 1, FOOT, SEAM)          # the wing's cabinet against the body's
    # meters along the top of the body's side
    m_panel(im, X(8, 112), 42, X(8, 112) + 112, 86)
    for k, (x, a) in enumerate(((30, 0.35), (64, 0.62), (98, 0.5))):
        m_meter(im, X(x), 64, 13, a, rnd, dead and k != 1)
    # the service door: painted on, flush, its seam, two hinges, a latch, a vent, a warning
    dx1, dx2, dy1, dy2 = X(42, 58), X(42, 58) + 58, 96, 232
    im.frame(dx1, dy1, dx2, dy2, SEAM, 1)
    im.rect(dx1 + 1, dy1 + 1, dx2 - 1, dy1 + 2, shade(GB, 1.25))
    im.rect(dx1 + 1, dy1 + 1, dx1 + 2, dy2 - 1, shade(GB, 1.2))
    hinge = dx1 if not mirror else dx2 - 3
    for y in (dy1 + 18, dy2 - 30):
        cyl_v(im, hinge, y, hinge + 3, y + 12, ALU, 1.3, 0.6)
    lx = dx2 - 9 if not mirror else dx1 + 9
    if dead:                                                     # sprung open a crack on the latch's side
        gx = dx2 - 3 if not mirror else dx1
        im.rect(gx, dy1 + 1, gx + 3, dy2 - 1, (12, 12, 14))
        im.disc(lx, 160, 2, (20, 18, 18))
    else:
        im.disc(lx, 160, 4, shade(ALU, 0.8))
        im.disc(lx, 160, 3, ALU)
        bx = lx - 12 if not mirror else lx
        cyl_h(im, bx, 159, bx + 12, 162, ALU, 1.3, 0.6)
    louvres(im, dx1 + 10, dy2 - 34, dx2 - 10, dy2 - 12, GB, 3)
    im.tri(X(71), dy1 + 14, 8, YELLOW_W)                          # a warning: lightning
    for i, (x, y) in enumerate(((1, -3), (0, -1), (-1, 1), (0, 1), (1, 2), (0, 4))):
        im.set(X(71) + x, dy1 + 14 + y, INK)
    # the cable entry where the floor's duct comes in (u 0..32, the duct's 32), cables up into it
    ex1, ex2 = X(4, 28), X(4, 28) + 28
    im.rect(ex1, 196, ex2, 222, (70, 76, 84))
    bevel(im, ex1, 196, ex2, 222, (70, 76, 84))
    im.rect(ex1 + 4, 200, ex2 - 4, 206, INK)
    text(im, "V", (ex1 + ex2) // 2 - 2, 201, (236, 236, 228), 1)
    for k, col in enumerate(((30, 30, 34), (160, 40, 30), (30, 30, 34), (90, 92, 98))):
        x = ex1 + 5 + k * 6
        if dead and k in (1, 2):                                 # cut off at the gland
            cyl_v(im, x - 2, 222, x + 2, 226, col, 1.4, 0.6)
            im.rect(x - 1, 226, x + 1, 228, COPPER)
            continue
        cyl_v(im, x - 2, 222, x + 2, 256, col, 1.4, 0.6)
        im.rect(x - 3, 222, x + 3, 225, shade(ALU, 0.8))         # its gland
    louvres(im, X(8, 22), 96, X(8, 22) + 22, 186, GB, 3)
    # the wing's side: lamps, the breaker, a louvre field
    for k in range(3):
        lamp(im, X(146 + k * 14), 48, 2.6, (GREEN, AMBER, LRED)[k], not dead and k != 2, INK)
    bx1, bx2 = X(136, 50), X(136, 50) + 50
    im.rect(bx1, 56, bx2, 148, shade(GB, 0.7))
    bevel(im, bx1, 56, bx2, 148, GB)
    im.rect(bx1 + 6, 62, bx2 - 6, 142, (58, 62, 70))
    cx = (bx1 + bx2) // 2
    im.rect(cx - 2, 70, cx + 2, 134, (20, 20, 22))                # the handle's slot
    legend(im, "ON", cx, 63)
    legend(im, "OFF", cx, 133 - 1)
    if dead:                                                     # thrown to OFF, its grip broken off; burnt
        cyl_v(im, cx - 2, 104, cx + 3, 128, shade(ALU, 0.7), 1.2, 0.6)
        im.rect(cx - 3, 126, cx + 4, 130, (40, 36, 32))
        GI.blot(im, cx, 66, 14, (20, 16, 12), 0.6)
    else:
        cyl_v(im, cx - 2, 80, cx + 3, 104, ALU, 1.3, 0.6)
        im.rect(cx - 12, 74, cx + 13, 84, shade(ORANGE, 0.7))
        im.rect(cx - 12, 74, cx + 13, 82, ORANGE)
        im.rect(cx - 12, 74, cx + 13, 75, shade(ORANGE, 1.25))
    im.disc(cx, 104, 5, (40, 40, 44))
    im.disc(cx, 104, 2, ALU)
    if dead and not mirror:
        m_guts(im, bx1 + 2, 156, bx2 - 2, 230, rnd)              # (the west's louvres gone, the east's there)
    else:
        m_bay(im, bx1, 154, bx2, 232, GB)
        louvres(im, bx1 + 3, 157, bx2 - 3, 229, GB, 3)
    return m_finish(im, dead, 7200 + mirror)


def face_A(dead, mirror=False):
    """The west wing's south face, 80 (u 0 its outer corner, 80 the alcove's); mirrored the east wing's (u 0
    the alcove's): a tower of lamps and keys, its lamps standing taller towards the alcove and 101."""
    W = 80
    rnd = random.Random(7300 + 13 * dead + 5 * mirror)

    def X(x, w=0):
        return x if not mirror else W - x - w

    im = m_shell(W, 256, 7300 + mirror, ("alu", "alu"))
    im.rect(X(72, 4), BAND, X(72, 4) + 4, FOOT, ORANGE)          # an orange edge along the alcove
    im.rect(X(72, 4) + (3 if not mirror else 0), BAND, X(72, 4) + (4 if not mirror else 1), FOOT, shade(ORANGE, 0.6))

    def lit(col, row):                                           # a bar each column, taller towards the alcove
        c = col if not mirror else 5 - col
        top = 10 - (3 + round(1.4 * c))
        if row < top:
            return None
        return GREEN if row == top else AMBER if c < 5 else ORANGE
    if dead and mirror:                                          # the east tower's lamp panel half gone
        m_lamps(im, X(6, 64), 42, X(6, 64) + 64, 150, 6, 11, rnd, dead, lit, 2.4)
        m_guts(im, X(8, 60), 44, X(8, 60) + 60, 92, rnd)
    else:
        m_lamps(im, X(6, 64), 42, X(6, 64) + 64, 150, 6, 11, rnd, dead, lit, 2.4)
    m_panel(im, X(6, 64), 156, X(6, 64) + 64, 196)
    for k, y in enumerate((160, 178)):
        m_keys(im, X(10, 56), y, 6, 10, 7, 13, rnd, dead, orange=(5,) if not mirror else (0,))
    if dead and not mirror:
        m_guts(im, X(8, 60), 202, X(8, 60) + 60, 232, rnd)
    else:
        louvres(im, X(8, 60), 202, X(8, 60) + 60, 232, GB, 3)
    return m_finish(im, dead, 7300 + mirror)


def face_I(dead, mirror=False):
    """The west wing's inner face, 64 (u 0 at the alcove's mouth, 64 at its back by 101); mirrored the east
    wing's: a column of indicator lamps in aluminium bezels."""
    W = 64
    rnd = random.Random(7400 + 13 * dead + 5 * mirror)

    def X(x, w=0):
        return x if not mirror else W - x - w

    im = m_shell(W, 256, 7400 + mirror, ("alu", "seam") if not mirror else ("seam", "alu"))
    im.rect(X(14, 36), 42, X(14, 36) + 36, 214, shade(GB, 0.85))
    bevel(im, X(14, 36), 42, X(14, 36) + 36, 214, GB, 1, False)
    cols = (AMBER, GREEN, AMBER, AMBER, LRED, AMBER, GREEN, AMBER, AMBER)
    for k in range(9):
        y = 52 + k * 19
        im.disc(32, y, 6, shade(ALU, 0.75))
        im.disc(32, y, 5.2, ALU)
        if dead:
            if k in (2, 6) or (mirror and k == 4):
                im.disc(32, y, 3.8, (14, 14, 16))
            else:
                lamp(im, 32, y, 3.8, shade(cols[k], 0.4), False)
        else:
            lamp(im, 32, y, 3.8, cols[k] if k % 4 != 3 else shade(cols[k], 0.45), k % 4 != 3)
    louvres(im, X(10, 44), 218, X(10, 44) + 44, 232, GB, 3)
    return m_finish(im, dead, 7400 + mirror)


def face_K(dead, mirror=False):
    """The body's south face beside 101's mouth, 16 (K west of it, u 0 at the alcove's corner; L east): a row
    of small lamps down it. It goes on into the piece over the mouth: no edge there."""
    W = 16
    rnd = random.Random(7500 + 13 * dead + 5 * mirror)
    im = m_shell(W, 256, 7500 + mirror, ("seam", None) if not mirror else (None, "seam"))
    x = 9 if not mirror else 7
    im.rect(x - 3, 44, x + 3, 230, (46, 50, 58))
    for k in range(12):
        y = 52 + k * 15
        on = (k + mirror) % 3 != 0
        if dead and rnd.random() < 0.25:
            im.disc(x, y, 1.6, (10, 10, 12))
        elif dead:
            lamp(im, x, y, 1.6, AMBER_OFF, False)
        else:
            lamp(im, x, y, 1.6, AMBER if on else AMBER_OFF, on)
    return m_finish(im, dead, 7500 + mirror)


def face_O(dead):
    """Over 101's mouth, 64 x 160 (the frame's head is 96 up; the picture is its height, so it stands the same
    pegged from the ceiling or from the head): a brass plate with the port's motif small, a row of lamps."""
    W, H = 64, 160
    rnd = random.Random(7600 + 13 * dead)
    im = m_shell(W, H, 7600, (None, None))
    px1, py1, px2, py2 = 8, 46, 56, 124
    im.rect(px1 + 1, py1 + 1, px2 + 1, py2 + 1, shade(GB, 0.55))   # its shadow
    plate = BRASS if not dead else (150, 120, 64)
    fill(im, px1, py1, px2, py2, plate, 0.03, 7601)
    bevel(im, px1, py1, px2, py2, plate)
    im.rect(15, 52, 49, 106, (14, 16, 24))                        # the port in small: a dark inlay,
    for y in range(52, 106):
        for x in range(15, 49):
            blend(im, x, y, (40, 60, 90), 0.5 * max(0, 1 - math.hypot((x - 32) / 17, (y - 90) / 30)))
    door_motif(im, 32, 79, 28, 50, 3, [plate, shade(plate, 0.86), shade(plate, 0.72)], 2, f=0.6, vy=0.3)
    if not dead:                                                 # ... the light far in
        glow(im, 32, 93, 4, (255, 214, 150), 0.6)
        im.set(32, 93, (255, 236, 200))
    im.rect(14, 51, 50, 52, shade(plate, 0.5))
    text(im, "7", 31, 111, shade(plate, 0.4), 1)                 # its number, engraved
    text(im, "7", 30, 110, shade(plate, 1.2) if not dead else shade(plate, 0.9), 1)
    for x, y in ((px1 + 3, py1 + 3), (px2 - 4, py1 + 3), (px1 + 3, py2 - 4), (px2 - 4, py2 - 4)):
        if dead and (x, y) == (px2 - 4, py1 + 3):
            im.disc(x, y, 1, (30, 24, 20))
            for k in range(9):
                blend(im, x, y + 2 + k, RUST, 0.6 * (1 - k / 9))
            continue
        im.disc(x, y, 1.3, shade(plate, 0.6))
        im.set(x, y, shade(plate, 1.3))
    if dead:
        for y in range(py1, py2):                                # tarnish, verdigris
            for x in range(px1, px2):
                p = im.px[y * W + x]
                if p[0] - p[2] > 50 and rnd.random() < 0.3:
                    blend(im, x, y, VERDI, 0.5)
        m_cracks(im, 25, 70, (14, 51, 50, 107), rnd, 6, (180, 186, 190), hole=5)
    else:
        glass_glint(im, 15, 52, 49, 106, 0.14)
    im.rect(14, 132, 50, 142, (46, 50, 58))
    for k in range(5):
        x = 18 + k * 7
        if dead:
            lamp(im, x, 137, 1.8, AMBER_OFF, False)
        else:
            lamp(im, x, 137, 1.8, GREEN if k == 2 else AMBER, k in (0, 2, 4))
    return m_finish(im, dead, 7600)


def m_finish(im, dead, seed):
    if dead:
        ruin(im, seed)
    im.noise(2, seed + 50 + dead)
    return im


def ruin(im, seed):
    """NOW: the colours of the hall NOW (khaki and dark), dust, soot from the top, rust runs, dirt up from the
    floor."""
    rnd = random.Random(seed + 900)
    for i, p in enumerate(im.px):
        r, g, b = p[:3]
        lum = r * 0.3 + g * 0.59 + b * 0.11
        q = mix((r, g, b), (lum * 1.03, lum, lum * 0.76), 0.62)
        q = mix(q, (160, 152, 124), 0.28)                        # a film of dust over all (and the hall NOW is
        im.px[i] = list(q) + [255]                               # dark: the darks are lifted, so that it reads)
    w, h = im.w, im.h
    for _ in range(max(2, w * h // 1400)):
        GI.blot(im, rnd.randrange(w), rnd.randrange(h), rnd.randrange(5, 15), (66, 56, 40), 0.2)
    for y in range(min(h, 56)):                                  # soot from the top
        for x in range(w):
            blend(im, x, y, (26, 24, 20), 0.26 * (1 - y / 56))
    GI.drips(im, rnd, max(1, w // 22), (104, 68, 38), CROWN, 130)
    GI.drips(im, rnd, max(1, w // 40), (40, 36, 30), BAND, 90)
    if h > FOOT:
        GI.grime(im, rnd, 30)
    GI.scuffs(im, rnd, h * 2 // 3, h - 8, w // 6, (40, 36, 32))


def machine_face(face, dead):
    return {"N": lambda: face_N(dead), "W": lambda: face_W(dead), "E": lambda: face_W(dead, True),
            "A": lambda: face_A(dead), "B": lambda: face_A(dead, True), "I": lambda: face_I(dead),
            "J": lambda: face_I(dead, True), "K": lambda: face_K(dead), "L": lambda: face_K(dead, True),
            "O": lambda: face_O(dead)}[face]()


SPRITES = (("AJUA", trolley), ("AJUB", tall), ("AJUC", small))


def make(out):
    def put(kind, nm, im, grab=None):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = im.png(grab) if grab else im.png()

    for n in LOOKS:
        for k in "ABCD":
            put("textures", f"AJUCB{n}{k}", CABS[n](k, 4000 + n * 10 + ord(k)))
        put("textures", name("CS", n), bank_end(n))
        put("flats", name("CT", n), bank_top(n))
        put("textures", name("RK", n), rack(n))
        put("textures", name("RS", n), rack_end(n))
        put("textures", name("RF", n), rack(n, 64))
        put("flats", name("RT", n), rack_top(n))
        put("textures", name("OB", n), bench_side(n))
        put("flats", name("OTA", n), bench_top(n, 0))
        put("flats", name("OTB", n), bench_top(n, 1))
        put("textures", name("TK", n), tank(n))
        put("flats", name("TT", n), tank_top(n))
        put("flats", name("BB", n), belt_bed(n))
        put("flats", name("BC", n), belt_curb(n))
        put("textures", name("BS", n), belt_side(n))
        put("textures", name("GB", n), gauge_board(n))
        put("textures", name("PM", n), pump_side(n))
        put("flats", name("PT", n), pump_top(n))
        put("textures", name("BM", n), motor_side(n))
        put("flats", name("BT", n), motor_top(n))
        put("textures", name("CN", n), console_side(n))
        put("flats", name("CK", n), console_top(n))
        put("textures", name("SC", n), schematic(n))
        put("textures", name("PB", n), passboard(n))
        put("textures", name("WN", n), newspaper(n))
        put("textures", name("PP", n), pipe_run(n))
        for spr, fn in SPRITES:
            im = fn(n)
            put("sprites", f"{spr}{'ABC'[n - 1]}0", im, (im.w // 2, im.h))
        put("sprites", f"AJUE{'ABC'[n - 1]}0", emitter(n), (20, 72))
        put("sprites", f"AJUE{'DEF'[n - 1]}0", emitter(n, True), (20, 72))
        put("sprites", f"AJUE{'GHI'[n - 1]}0", emitter(n, off=True), (20, 72))
    for part in ("EX", "AR", "CO", "LA"):
        put("textures", f"AJUNT{part}2", notice(part))
    put("textures", "AJUCLEX2", calendar("EX", 2))
    put("textures", "AJUCLEX3", calendar("EX", 3))
    put("flats", "AJUDU2", duct(False))
    put("flats", "AJUDU3", duct(True))
    for face in MACH_FACES:                                      # the machine, THEN and NOW (look 1's in every look)
        put("textures", mach_name(face), machine_face(face, False))
        put("textures", mach_name(face, True), machine_face(face, True))
    put("textures", "AJULF2", ledge_face(2))
    put("textures", "AJULF3", ledge_face(3))
    for (kind, look, part, shift), nm in PICS.items():
        put("textures", nm, picture(kind, look, part, shift))
    for (part, w, shift, rects, stubs), nm in GHOSTS.items():
        put("textures", nm, ghost(part, w, rects, shift, int(nm[4:]), stubs=stubs))


# the textures a map lays by world position (they are 64 wide and seamless): map_longrun adds them to m.align
# (RS and BM are laid from their line's end: a rack's end and the motor's box are exactly one picture wide)
ALIGNED = {name(p, n) for p in ("CS", "OB", "PM", "CN", "BS", "RF") for n in LOOKS} | {"AJULF2", "AJULF3"}
