"""What MAP13 and MAP14 have of their own in MAP11's institute (Vadim,
2026-11-19: props and pictures only, "to introduce something new"; walls,
floors and ceilings stay MAP11's). Names are AJI<part><look>, as in
gfx_institute.py, and every part is drawn in the three looks.

Furniture (the side aligned, 48 high; the top a flat):
  OS OT  an optical bench: a rail down its top, lenses in their holders
  RS RT  the kitchen's range: oven doors; burners and a pan
  AT     an accounts desk's top (on MAP11's desk, DS): a ledger, papers,
         an adding machine
Pictures (one to a wall piece, on the wall named):
  MAP13  RD 128 LA  a chart: the beam through a door and out of its frame
         SL 128 PU  the darkroom's safelight, and prints pegged on a line
         R1 R2 R3 64 EX  the range's marks: 100, 200, 400
         LS 128 AR  racks of lenses
  MAP14  HT 128 EX  the kitchen's hatch, shut, and today's menu
         PN 128 AR  pans on a rail, a shelf of jars
         PF 128 LA  the throat between a door and its far side
         FG 128 LA  filing cabinets
         CW 128 CK  the cashier's window
         SF 128 EV  the safe's door
         PR 128 LB  where the portrait hung
         BC 128 LB  a bookcase
The emitter's lamp (AjarEmitter, optics.zs) is the sprite AJEMA0.
"""
import math
import random

import gfx_institute as G
from gfx import Img, digit, shade, text
from gfx_institute import DARK, KHAKI, METAL, PLATE, RED, RUST, WOOD, dial, drips, name, on_wall, plate, scuffs

LOOKS = G.LOOKS
SIDES = ("OS", "RS")
ALIGNED = {f"AJI{p}{n}" for p in SIDES for n in LOOKS}
PAPER, INK, GLASS = (232, 226, 204), (60, 58, 64), (170, 204, 214)
STEEL = {1: (96, 100, 108), 2: (176, 182, 188), 3: (104, 108, 100)}


# === furniture ====================================================================
def bench_side(n):
    """An optical bench from the side: a slab on a steel frame, a shelf under it."""
    c = STEEL[n]
    im = Img(64, 48, (24, 24, 26))
    im.rect(0, 0, 64, 6, {1: (36, 34, 36), 2: (60, 62, 66), 3: (70, 72, 66)}[n])      # the slab
    im.rect(0, 6, 64, 7, (16, 16, 16))
    for x0 in (2, 58):
        im.rect(x0, 7, x0 + 4, 48, c)
        im.rect(x0, 7, x0 + 1, 48, shade(c, 1.3))
    im.rect(0, 30, 64, 33, shade(c, 0.8))                                              # the shelf
    for x0 in (10, 24, 40):                                                            # boxes of parts on it
        im.rect(x0, 22, x0 + 10, 30, shade(WOOD[n], 0.8))
        im.rect(x0 + 3, 25, x0 + 7, 27, PAPER)
    im.rect(0, 44, 64, 48, (16, 16, 16))
    im.noise(3, 2301 + n)
    return im


def bench_top(n):
    slab = {1: (36, 34, 36), 2: (60, 62, 66), 3: (70, 72, 66)}[n]
    im = Img(64, 64, slab)
    im.noise(4, 2311 + n)
    rail = METAL[n] if n != 3 else (150, 150, 140)
    im.rect(0, 29, 64, 35, shade(rail, 0.6))
    im.rect(0, 30, 64, 34, rail)
    for x in range(2, 64, 4):                                                          # the scale along the rail
        im.set(x, 31, shade(rail, 0.5))
    for x0, r in ((12, 7), (34, 5), (52, 6)):                                          # holders across the rail, a lens in each
        im.rect(x0 - 2, 32 - r - 2, x0 + 2, 32 + r + 2, (30, 30, 34))
        im.rect(x0 - 1, 32 - r, x0 + 1, 32 + r, GLASS)
        im.set(x0, 32 - r + 1, (255, 255, 255))
    im.rect(40, 8, 58, 20, PAPER)                                                      # a notebook
    for y in range(11, 19, 3):
        im.rect(43, y, 55, y + 1, shade(PAPER, 0.7))
    return im


def range_side(n):
    c = {1: (232, 228, 214), 2: (206, 210, 212), 3: (150, 150, 140)}[n]
    im = Img(64, 48, c)
    im.rect(0, 0, 64, 4, (40, 40, 44))                                                 # the top's edge
    for x0 in (0, 32):
        im.frame(x0 + 2, 14, x0 + 30, 42, shade(c, 0.6), 1)                            # an oven door
        im.rect(x0 + 6, 20, x0 + 26, 32, (30, 28, 30))
        im.rect(x0 + 6, 16, x0 + 26, 18, METAL[n] if n != 3 else (70, 70, 66))         # its handle
        for k in range(3):                                                             # knobs
            im.disc(x0 + 8 + k * 8, 9, 2, (30, 30, 34))
    if n == 3:
        rnd = random.Random(2321)
        drips(im, rnd, 3, (90, 70, 44), 6, 36)
        scuffs(im, rnd, 6, 46, 12, (70, 60, 50))
    im.rect(0, 44, 64, 48, shade(c, 0.4))
    im.noise(3, 2320 + n)
    return im


def range_top(n):
    c = {1: (40, 40, 44), 2: (60, 62, 66), 3: (58, 56, 52)}[n]
    im = Img(64, 64, c)
    im.noise(4, 2331 + n)
    for k, (cx, cy) in enumerate(((16, 16), (48, 16), (16, 48), (48, 48))):
        im.disc(cx, cy, 11, (22, 22, 24))
        im.disc(cx, cy, 8, shade(c, 1.2))
        im.disc(cx, cy, 5, (22, 22, 24))
        if k == 1:                                                                     # a pan left on
            im.disc(cx, cy, 12, (120, 120, 124) if n != 3 else (104, 100, 92))
            im.disc(cx, cy, 10, (70, 56, 40) if n == 3 else (190, 150, 90))
            im.rect(cx + 10, cy - 1, cx + 16, cy + 2, (30, 30, 30))
    return im


def desk_top(n):
    c = {1: (60, 88, 66), 2: (236, 236, 230), 3: (150, 124, 90)}[n]                    # baize, formica, lino: as DT
    im = Img(64, 64, c)
    im.noise(4, 2341 + n)
    im.rect(6, 8, 30, 40, (40, 60, 44) if n != 1 else (110, 40, 36))                   # a ledger, open
    im.rect(8, 10, 18, 38, PAPER)
    im.rect(19, 10, 28, 38, PAPER)
    for y in range(13, 36, 3):
        im.rect(9, y, 17, y + 1, shade(PAPER, 0.72))
        im.rect(20, y, 27, y + 1, shade(PAPER, 0.72))
    im.rect(23, 10, 24, 38, (170, 60, 50))                                             # the totals' column
    im.rect(38, 10, 58, 30, (60, 62, 66))                                              # an adding machine
    for yy in range(4):
        for xx in range(4):
            im.rect(40 + xx * 4, 16 + yy * 3, 43 + xx * 4, 18 + yy * 3, (200, 200, 190))
    im.rect(40, 11, 56, 14, (150, 190, 150))
    im.rect(56, 14, 60, 24, (30, 30, 30))                                              # its handle
    for k, (x, y) in enumerate(((36, 40), (42, 46), (14, 46))):                        # loose sheets
        im.rect(x, y, x + 16, y + 12, shade(PAPER, 1 - 0.04 * k))
        im.rect(x + 2, y + 3, x + 12, y + 4, shade(PAPER, 0.7))
        im.rect(x + 2, y + 7, x + 10, y + 8, shade(PAPER, 0.7))
    return im


# === pictures =======================================================================
def sheet(im, x1, y1, x2, y2, n, pins=True):
    im.rect(x1, y1, x2, y2, PAPER if n != 3 else (214, 204, 172))
    im.frame(x1, y1, x2, y2, (150, 140, 110), 1)
    if pins:
        for x, y in ((x1 + 2, y1 + 2), (x2 - 3, y1 + 2)):
            im.set(x, y, RED)


def ray_chart(n):
    """How the beam goes: in at a door, out of the frame the door hangs in."""
    im = on_wall(n, "LA", 128)
    y0 = 118
    sheet(im, 8, y0, 120, y0 + 88, n)
    text(im, "BEAM", 46, y0 + 6, INK, 2)
    # the emitter, the door's far side, and below them the frame and the sensor
    im.rect(16, y0 + 30, 26, y0 + 40, INK)
    im.rect(26, y0 + 33, 30, y0 + 37, INK)
    for x in range(31, 78, 3):
        im.rect(x, y0 + 34, x + 2, y0 + 36, RED)
    im.frame(80, y0 + 24, 92, y0 + 46, (40, 90, 160), 2)                               # a door, from above its lintel
    im.frame(22, y0 + 54, 34, y0 + 76, (40, 90, 160), 2)                               # the same door's frame
    for x in range(36, 96, 3):
        im.rect(x, y0 + 64, x + 2, y0 + 66, RED)
    im.disc(102, y0 + 65, 6, INK)
    im.disc(102, y0 + 65, 3, (120, 220, 250))
    for k in range(4):                                                                 # it is the same opening: a dotted tie
        im.rect(84 - k * 14, y0 + 48 + k * 2, 88 - k * 14, y0 + 49 + k * 2, (40, 90, 160))
    if n == 3:
        drips(im, random.Random(2401), 2, (150, 130, 90), y0 + 20, 50)
    im.noise(2, 2400 + n)
    return im


def safelight(n):
    """128 by 192, in the darkroom: a red lamp, and prints pegged up to dry."""
    im = on_wall(n, "PU", 128)
    im.rect(54, 20, 74, 26, (40, 40, 44))                                              # the lamp's box
    im.rect(50, 26, 78, 46, (60, 20, 18))
    im.rect(53, 29, 75, 43, (220, 50, 40))
    im.rect(55, 31, 73, 34, (255, 130, 110))
    for y in range(47, 90):                                                            # and what it does to the wall
        for x in range(30, 98):
            d = math.hypot(x - 64, (y - 40) * 1.2)
            if d < 46:
                p = im.px[y * 128 + x]
                f = 0.16 * (1 - d / 46)
                im.px[y * 128 + x] = [min(255, int(p[0] + 255 * f)), int(p[1] * (1 - f * 0.5)), int(p[2] * (1 - f * 0.5)), 255]
    for x in range(6, 122):                                                            # the line, sagging
        im.set(x, 96 + int(4 * math.sin((x - 6) * math.pi / 116)), (30, 30, 30))
    rnd = random.Random(2410 + n)
    for k, x0 in enumerate((12, 36, 62, 88)):
        y = 98 + int(4 * math.sin((x0 + 9 - 6) * math.pi / 116))
        im.rect(x0 + 8, y - 3, x0 + 11, y + 3, WOOD[n])                                # a peg
        im.rect(x0, y + 2, x0 + 20, y + 30, (226, 226, 220))
        im.rect(x0 + 2, y + 4, x0 + 18, y + 26, (38, 38, 42))
        if k == 1:                                                                     # a door, standing open, and nothing behind it
            im.frame(x0 + 6, y + 8, x0 + 14, y + 24, (200, 200, 196), 1)
        elif k == 2:                                                                   # a bright line across the dark
            im.rect(x0 + 3, y + 14, x0 + 17, y + 15, (230, 230, 220))
        else:
            for _ in range(5):
                im.rect(x0 + 3 + rnd.randrange(12), y + 6 + rnd.randrange(18), x0 + 5 + rnd.randrange(12), y + 8 + rnd.randrange(18), (120, 120, 124))
    im.noise(2, 2415 + n)
    return im


def range_mark(n, s):
    """64 wide: how far down the range this is, stencilled, over a tick to the floor."""
    im = on_wall(n, "EX", 64)
    ink = {1: (40, 40, 44), 2: (40, 70, 130), 3: RED}[n]
    w = len(s) * 8 - 2                                           # digits are three dots wide: set close
    for k, ch in enumerate(s):
        digit(im, ch, 32 - w // 2 + k * 8, 170, ink, 2)
    im.rect(31, 186, 33, 252, ink)
    for y in range(196, 250, 10):
        im.rect(27, y, 37, y + 1, ink)
    im.noise(2, 2420 + n)
    return im


def lens_racks(n):
    """128 wide, in the lens store: racks of lenses, each in its slot."""
    im = on_wall(n, "AR", 128)
    rnd = random.Random(2430 + n)
    c = {1: G.OAK, 2: (150, 158, 164), 3: KHAKI}[n]
    im.rect(4, 70, 124, 250, shade(c, 0.5))
    for row, y in enumerate(range(74, 246, 29)):
        im.rect(4, y + 25, 124, y + 28, c)
        r = (11, 9, 7, 11, 8, 6)[row]
        x = 8 + r
        while x + r < 122:
            if n == 3 and rnd.random() < 0.15:                   # an empty slot
                im.rect(x - 1, y + 20, x + 1, y + 25, shade(c, 0.8))
            else:
                im.disc(x, y + 25 - r - 1, r, (60, 70, 76))
                im.disc(x, y + 25 - r - 1, r - 1.5, shade(GLASS, rnd.uniform(0.75, 1.05)))
                im.set(int(x - r / 2), int(y + 25 - r - 1 - r / 2), (255, 255, 255))
                im.set(int(x - r / 2) + 1, int(y + 25 - r - 1 - r / 2), (255, 255, 255))
            x += 2 * r + 4
    plate(im, "LENSES", 64, 54, n)
    im.noise(2, 2435 + n)
    return im


def hatch(n):
    """128 wide, in MAP14's canteen: the kitchen's hatch with its shutter down, and the menu."""
    im = on_wall(n, "EX", 128)
    frame = {1: G.OAK, 2: G.AL, 3: (128, 132, 128)}[n]
    im.rect(6, 132, 78, 204, frame)
    im.rect(9, 135, 75, 201, {1: (226, 222, 210), 2: (206, 210, 212), 3: (170, 166, 150)}[n])
    for y in range(137, 200, 4):                                 # the shutter's slats
        im.rect(9, y, 75, y + 1, (120, 120, 118))
    im.rect(38, 196, 46, 199, (40, 40, 40))                      # its pull
    im.rect(4, 204, 80, 209, {1: (236, 232, 220), 2: G.ORANGE, 3: (150, 150, 146)}[n])    # the shelf
    im.rect(4, 209, 80, 210, (40, 38, 38))
    for x in (8, 74):
        im.rect(x, 210, x + 2, 220, shade(frame, 0.7))
    ground, ink = PLATE[n]
    im.rect(86, 134, 124, 204, ground)
    im.frame(86, 134, 124, 204, WOOD[n] if n != 2 else G.AL, 2)
    text(im, "MENU", 93, 140, ink, 1)
    for k, s in enumerate(("SOUP", "PIE", "RICE", "TEA")):
        if n == 3 and k in (1, 2):                               # none today
            im.rect(91, 157 + k * 11, 91 + len(s) * 6, 158 + k * 11, ink)
        else:
            text(im, s, 91, 154 + k * 11, ink, 1)
    if n == 3:
        drips(im, random.Random(2441), 2, (90, 70, 44), 210, 34)
    im.noise(2, 2440 + n)
    return im


def pans(n):
    """128 wide, in the kitchen: pans and ladles on a rail, a shelf of jars."""
    im = on_wall(n, "AR", 128)
    rnd = random.Random(2450 + n)
    rail = METAL[n] if n != 3 else (90, 90, 86)
    im.rect(6, 112, 122, 115, rail)
    pan = (150, 150, 156) if n != 3 else (112, 110, 104)
    for k, x in enumerate(range(16, 116, 16)):
        im.rect(x, 115, x + 1, 121, (60, 60, 60))                # a hook
        if k % 3 == 2:                                           # a ladle
            im.rect(x, 121, x + 1, 150, pan)
            im.disc(x + 0.5, 153, 4, pan)
        else:
            r = (9, 7, 11, 8)[k % 4]
            im.rect(x, 121, x + 1, 121 + 14, shade(pan, 0.7))    # the handle, up
            im.disc(x + 0.5, 135 + r, r, pan)
            im.disc(x + 0.5, 135 + r, r - 2, shade(pan, 0.7 if n == 3 else 0.86))
    im.rect(6, 196, 122, 200, WOOD[n])                           # the shelf
    im.rect(6, 200, 122, 201, (30, 28, 26))
    x = 10
    while x < 112:
        w, h = rnd.choice(((10, 18), (8, 14), (12, 22), (9, 12)))
        if not (n == 3 and rnd.random() < 0.25):
            c = rnd.choice(((176, 60, 50), (190, 170, 110), (120, 150, 110), (210, 200, 180), (90, 70, 60)))
            im.rect(x, 196 - h, x + w, 196, c)
            im.rect(x, 196 - h, x + w, 196 - h + 3, (40, 40, 44))
            im.rect(x + 2, 196 - h + 6, x + w - 2, 196 - h + 10, PAPER)
        x += w + 3
    im.noise(2, 2455 + n)
    return im


def plan_chart(n):
    """128 wide, in accounts: the throat between a door and its far side
    (Vadim, 2026-11-19: "not just PLAN: something scientifically more
    interesting"). Two sheets of space drawn as funnels joined at the neck,
    rings of equal radius, and the path through. In look 3 somebody has
    ringed the neck in red and drawn the path stopping there."""
    im = on_wall(n, "LA", 128)
    y0 = 112
    sheet(im, 10, y0, 118, y0 + 92, n)
    ink = PLATE[n][1] if n != 1 else (40, 40, 44)
    text(im, "THROAT", 29, y0 + 5, ink, 2)
    cx, cy, half = 60, y0 + 54, 27
    grey = shade(PAPER, 0.62)

    def r(z):                                                    # the funnel's radius z from the neck (Flamm's parabola)
        return 5 + z * z / 22.0

    for z in (-27, -20, -12, 0, 12, 20, 27):                     # rings: each a circle seen from the side
        w, h = r(z), max(1.0, r(z) / 5)
        for k in range(160):
            t = k * math.pi / 80
            back = math.sin(t) < 0
            if back and k % 4 > 1 and abs(z) != 27:
                continue                                         # the far half dotted
            im.set(int(cx + w * math.cos(t) + 0.5), int(cy + z - (h * math.sin(t) if z < 0 else -h * math.sin(t)) + 0.5),
                   grey if back else INK)
    for z2 in range(-half * 2, half * 2 + 1):                    # the outline
        z = z2 / 2
        for sgn in (-1, 1):
            im.set(int(cx + sgn * r(z) + 0.5), int(cy + z + 0.5), INK)
    for k in range(1, 6):                                        # lines down the funnel
        t = k * math.pi / 6
        for z2 in range(-half * 2, half * 2 + 1):
            z = z2 / 2
            if z2 % 3:
                continue
            im.set(int(cx + r(z) * math.cos(t) + 0.5), int(cy + z + (1 if z > 0 else -1) * r(z) / 5 * math.sin(t) + 0.5), grey)
    text(im, "A", 106, cy - half - 2, ink, 1)
    text(im, "B", 106, cy + half - 3, ink, 1)
    im.rect(cx + 8, cy, cx + 30, cy + 1, INK)                    # the neck, measured
    text(im, "R0", 93, cy - 2, ink, 1)
    stop = 0 if n == 3 else half + 4                             # the path through
    for z in range(-half - 4, stop):
        if z % 3 < 2:
            im.rect(cx - 1, cy + z, cx + 1, cy + z + 1, RED)
    if n == 3:                                                   # and there it stops
        im.frame(cx - 10, cy - 7, cx + 10, cy + 7, RED, 1)
    else:
        for k in range(4):
            im.rect(cx - 1 - k, cy + stop - k, cx + 1 + k, cy + stop - k + 1, RED)
    im.noise(2, 2460 + n)
    return im


def filing(n):
    """128 wide, in accounts: filing cabinets, four drawers high."""
    im = on_wall(n, "LA", 128)
    rnd = random.Random(2470 + n)
    c = {1: G.OAK, 2: (150, 158, 164), 3: KHAKI}[n]
    for x0 in range(4, 124, 30):
        im.rect(x0, 128, x0 + 29, 252, shade(c, 0.55))
        for k in range(4):
            y = 130 + k * 30
            out = n == 3 and rnd.random() < 0.15                 # one left open, empty
            f = rnd.uniform(0.94, 1.06)
            im.rect(x0 + 1, y, x0 + 28, y + 28, (22, 22, 22) if out else shade(c, f))
            if out:
                continue
            im.rect(x0 + 1, y, x0 + 28, y + 1, shade(c, f * 1.25))
            im.rect(x0 + 8, y + 5, x0 + 21, y + 12, PAPER)
            im.rect(x0 + 11, y + 18, x0 + 18, y + 21, METAL[n] if n != 3 else (60, 60, 56))
    if n == 3:
        scuffs(im, rnd, 130, 250, 24, (60, 54, 44))
    im.noise(2, 2475 + n)
    return im


def cash_window(n):
    """128 wide on the cloakroom's wall (160 high), in the cashier's office: the window, shut."""
    im = on_wall(n, "CK", 128)
    h = im.h
    c = WOOD[n]
    im.rect(20, h - 118, 108, h - 40, c)
    im.rect(24, h - 114, 104, h - 46, (28, 28, 32))
    bar = METAL[n] if n != 3 else (120, 120, 112)
    for x in range(28, 104, 8):                                  # the grille
        im.rect(x, h - 114, x + 2, h - 46, bar)
    for y in (h - 96, h - 70):
        im.rect(24, y, 104, y + 2, bar)
    im.rect(52, h - 62, 76, h - 46, (28, 28, 32))                # the opening money comes through
    im.frame(52, h - 62, 76, h - 46, bar, 1)
    im.rect(16, h - 46, 112, h - 40, shade(c, 1.2))              # the sill
    im.rect(16, h - 40, 112, h - 39, (30, 28, 26))
    plate(im, "CASH", 64, h - 136, n)
    im.rect(44, h - 92, 84, h - 78, PAPER)                       # a card hung inside
    text(im, "CLOSED", 47, h - 88, RED, 1)
    im.noise(2, 2480 + n)
    return im


def safe(n):
    """128 wide on the steel of the way out (160 high), in the safe room: the safe's door."""
    im = on_wall(n, "EV", 128)
    h = im.h
    c = {1: (70, 80, 72), 2: (120, 132, 142), 3: (86, 90, 78)}[n]
    im.rect(14, h - 132, 114, h - 4, shade(c, 0.5))
    im.rect(18, h - 128, 110, h - 8, c)
    im.frame(24, h - 122, 104, h - 14, shade(c, 0.7), 2)
    for x, y in ((21, h - 125), (106, h - 125), (21, h - 12), (106, h - 12), (21, h - 68), (106, h - 68)):
        im.disc(x, y, 1.5, shade(c, 1.5))                        # rivets
    for y in (h - 104, h - 40):                                  # hinges
        im.rect(14, y, 22, y + 12, shade(c, 0.4))
    brass = METAL[n] if n != 3 else (150, 134, 84)
    dial(im, 50, h - 78, 11, brass, 0.3)                         # the lock's dial
    cx, cy = 82, h - 70                                          # the wheel
    im.disc(cx, cy, 15, brass)
    im.disc(cx, cy, 12, c)
    for a in range(0, 180, 60):
        t = math.radians(a)
        for k in range(-14, 15):
            im.set(int(cx + k * math.cos(t)), int(cy + k * math.sin(t)), brass)
            im.set(int(cx + k * math.cos(t)), int(cy + k * math.sin(t)) + 1, brass)
    im.disc(cx, cy, 3, shade(brass, 0.7))
    im.rect(36, h - 116, 92, h - 104, PLATE[n][0])               # the maker's plate
    text(im, "NO 1", 52, h - 113, PLATE[n][1], 1)
    if n == 3:
        rnd = random.Random(2491)
        drips(im, rnd, 3, RUST, h - 100, 70)
    im.noise(2, 2490 + n)
    return im


def portrait_gone(n):
    """128 wide, on the director's floor: where the portrait hung."""
    im = on_wall(n, "LB", 128)
    for y in range(92, 172):                                     # the wall as it was when the portrait went up
        for x in range(34, 94):
            p = im.px[y * 128 + x]
            im.px[y * 128 + x] = list(shade(tuple(p[:3]), 1.14)) + [255]
    im.frame(33, 91, 95, 173, shade(tuple(im.px[92 * 128 + 20][:3]), 0.8), 1)
    im.rect(63, 86, 65, 89, (40, 40, 40))                        # the nail
    im.rect(40, 190, 88, 197, PLATE[n][0])                       # and the plate under it, blank now
    im.frame(40, 190, 88, 197, (90, 84, 70), 1)
    im.noise(2, 2500 + n)
    return im


def bookcase(n):
    """128 wide, on the director's floor: a glazed bookcase."""
    im = on_wall(n, "LB", 128)
    rnd = random.Random(2510 + n)
    c = WOOD[n]
    im.rect(8, 96, 120, 252, shade(c, 0.7))
    im.rect(8, 96, 120, 100, shade(c, 1.2))
    for row in range(5):
        y = 102 + row * 29
        im.rect(12, y, 116, y + 26, (24, 22, 22))
        x = 13
        while x < 112:
            w = rnd.choice((3, 4, 4, 5, 6))
            hh = rnd.randrange(17, 25)
            if n == 3 and rnd.random() < 0.2:                    # gaps: some went with the staff
                x += w + 2
                continue
            col = rnd.choice(((110, 40, 36), (40, 60, 90), (60, 80, 56), (120, 96, 60), (70, 60, 70)))
            im.rect(x, y + 26 - hh, min(x + w, 116), y + 26, col)
            im.rect(x, y + 26 - hh + 3, min(x + w, 116), y + 26 - hh + 4, (200, 180, 110))
            x += w + 1
        im.rect(12, y + 26, 116, y + 29, c)
    im.rect(63, 100, 65, 248, shade(c, 1.1))                     # the doors meet
    im.noise(2, 2515 + n)
    return im


def emitter_lamp():
    """The emitter (AJEMA0): a lamp housing on a stand, its lens 40 above the floor."""
    im = Img(30, 58, (0, 0, 0, 0))
    k = KHAKI
    im.rect(4, 54, 26, 58, shade(k, 0.5))                        # the foot
    im.rect(13, 30, 17, 54, shade(k, 0.8))                       # the post
    im.rect(14, 30, 15, 54, shade(k, 1.3))
    im.rect(3, 6, 27, 30, shade(k, 0.6))                         # the housing
    im.rect(5, 8, 25, 28, k)
    for y in range(10, 27, 4):                                   # cooling slots
        im.rect(6, y, 10, y + 1, shade(k, 0.5))
        im.rect(20, y, 24, y + 1, shade(k, 0.5))
    im.disc(15, 18, 7, (40, 40, 44))                             # the lens
    im.disc(15, 18, 5, (200, 60, 50))
    im.disc(15, 18, 2.5, (255, 190, 170))
    im.rect(11, 2, 19, 6, shade(k, 0.5))                         # a handle
    return im


def make(out):
    def put(kind, nm, im):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = im.png()

    for n in LOOKS:
        put("textures", name("OS", n), bench_side(n))
        put("textures", name("RS", n), range_side(n))
        for tag, im in (("OT", bench_top(n)), ("RT", range_top(n)), ("AT", desk_top(n))):
            put("flats", name(tag, n), im)
        for tag, fn in (("RD", ray_chart), ("SL", safelight), ("LS", lens_racks), ("HT", hatch), ("PN", pans), ("PF", plan_chart),
                        ("FG", filing), ("CW", cash_window), ("SF", safe), ("PR", portrait_gone), ("BC", bookcase)):
            put("textures", name(tag, n), fn(n))
        for tag, s in (("R1", "100"), ("R2", "200"), ("R3", "400")):
            put("textures", name(tag, n), range_mark(n, s))
    out["sprites/AJEMA0.png"] = emitter_lamp().png(grab=(15, 58))


if __name__ == "__main__":
    # swatches: python3 tools/gfx_institute2.py <dir>
    import os
    import sys
    out = {}
    make(out)
    os.makedirs(sys.argv[1], exist_ok=True)
    for key, data in out.items():
        with open(os.path.join(sys.argv[1], os.path.basename(key)), "wb") as f:
            f.write(data)
