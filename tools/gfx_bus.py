"""MAP10's bus (ajarmap.bus) and the route board beside it (ajarmap.route_board).

The bus is after the teleporter bus of "Гостья из будущего" (1984): a flat
plywood bus painted red, standing at its stop, a row of numbered doors in its
side and a place of the town behind each. Vadim, 2026-11-17: to be known for
it by somebody who has seen the film, not copied from it; and forty years
older than it was there. So: the red has gone chalky, the cream of the roof
and the waist has yellowed, rust runs from every edge, the paint has come off
in sheets and the plywood under it shows its plies, a window is cracked and
another is boarded up, moss stands along the foot. The plates over the doors
are the white route plates of a Soviet bus, in Russian: АВТОБУС, the number,
and where the line goes for the lines that always run.

For a livery L (B the red 10, C the amber 20):
AJ?US    64x144  the body between two doors: a window. The sector's wall,
                 and the side of the depot's buses
AJ?US1..4        the same, weathered otherwise (ajarmap.bus lays them by turns)
AJ?USZ   48x144  an end of the body, the bus's corner on the left; AJ?USY on the right
AJ?USF  144x144  its front: the windscreen, the lamps, the number
AJ?USR  144x144  its back
AJ?Nn    64x48   what is over door n (1..9): the route plate (0: a door with
                 no number: the plate is gone, its shape left in the paint)
AJRnc    16x128  the route board's lamp for door n (0..9; 0 is the shelter):
                 c is 0 (nothing runs), a door's colour 1..6, 7 (a line
                 that always runs, or a Stray door), 8 and 9 (a Pair's TEAL
                 and ORANGE leaves) or C (the clocked door: an ivory dial
                 with two hands). AjarHandler.Lamp picks them.
"""
import random

from gfx import Img, shade, digit, DOOR_COLOURS, PAIR_COLOURS

RED = (190, 40, 32)
AMBER = (222, 164, 44)
CREAM = (214, 202, 168)
GLASS = (44, 54, 66)
PLY = (176, 138, 88)
RUST = (104, 52, 26)
RUBBER = (26, 26, 28)
PLATE = (226, 222, 206)
INK = (26, 24, 26)
H = 144
# a livery: the letter in its textures' names (AJ?US...), its paint, its number,
# and where its lines that always run go, by door
LIVERIES = (("B", RED, "10", {1: "ГОСТИНИЦА", 5: "ВОКЗАЛ", 8: "ПЕРЕСАДКА"}),
            ("C", AMBER, "20", {1: "ПЕРЕСАДКА", 2: "ТЕАТР", 4: "ПЛАНЕТАРИЙ"}))
VARIANTS = 5        # AJ?US and AJ?US1..4

CYR = {
    "А": ("01110", "10001", "11111", "10001", "10001"), "Б": ("11111", "10000", "11110", "10001", "11110"),
    "В": ("11110", "10001", "11110", "10001", "11110"), "Г": ("11111", "10000", "10000", "10000", "10000"),
    "Д": ("01110", "01010", "01010", "11111", "10001"), "Е": ("11111", "10000", "11110", "10000", "11111"),
    "З": ("11110", "00001", "01110", "00001", "11110"), "И": ("10001", "10011", "10101", "11001", "10001"),
    "К": ("10001", "10010", "11100", "10010", "10001"), "Л": ("01111", "01001", "01001", "01001", "10001"),
    "Н": ("10001", "10001", "11111", "10001", "10001"), "О": ("01110", "10001", "10001", "10001", "01110"),
    "П": ("11111", "10001", "10001", "10001", "10001"), "Р": ("11110", "10001", "11110", "10000", "10000"),
    "С": ("01111", "10000", "10000", "10000", "01111"), "Т": ("11111", "00100", "00100", "00100", "00100"),
    "Й": ("10001", "10011", "10101", "11001", "10001"),      # and its mark over it: see cyr()
    "У": ("10001", "10001", "01111", "00001", "01110"), "Ц": ("10010", "10010", "10010", "11111", "00001"),
}


def cyr(im, s, x, y, c, scale=1, worn=None):
    """Russian capitals, 5 by 5, top left at x, y. `worn` is a random.Random:
    some of the paint of the letters has gone."""
    for n, ch in enumerate(s):
        if ch == "Й":
            im.rect(x + (n * 6 + 1) * scale, y - 2 * scale, x + (n * 6 + 4) * scale, y - scale, c)
        for j, row in enumerate(CYR[ch]):
            for i, bit in enumerate(row):
                if bit == "1" and not (worn and worn.random() < 0.05):
                    im.rect(x + (n * 6 + i) * scale, y + j * scale, x + (n * 6 + i + 1) * scale, y + (j + 1) * scale, c)


def mix(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def blend(im, x, y, c, f):
    if 0 <= x < im.w and 0 <= y < im.h and f > 0:
        p = im.px[y * im.w + x]
        im.px[y * im.w + x] = list(mix(p, c, min(1, f))) + [255]


def faded(c):
    """Paint after forty summers: paler, chalkier, a little towards brick."""
    grey = sum(c) / 3
    return tuple(int(v + (grey - v) * 0.16 + (196 - v) * 0.07) for v in c)


def weather(im, seed, paint, *, top=11, foot=None, streaks=5, chips=4, glass=()):
    """Forty years on a painted panel: blotches of chalk, rust running down
    from the roof's gutter (row `top`) and from under each window (`glass`:
    their boxes), paint gone in patches with plywood under it, dirt thrown up
    from the road, moss along the foot."""
    rnd = random.Random(seed)
    w, h = im.w, im.h
    foot = h if foot is None else foot
    inside = lambda x, y: any(x1 <= x < x2 and y1 <= y < y2 for x1, y1, x2, y2 in glass)
    # chalky blotches: a few soft spots where the sun has had the paint
    for _ in range(3 + w // 32):
        cx, cy, r = rnd.randrange(w), rnd.randrange(top, foot), rnd.randrange(8, 22)
        tone = rnd.choice(((224, 206, 196), (120, 84, 70)))
        for y in range(cy - r, cy + r):
            for x in range(cx - r, cx + r):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / r
                if d < 1 and not inside(x, y):
                    blend(im, x, y, tone, 0.16 * (1 - d))
    # paint gone in sheets: plywood under it, and under that the next ply
    for n in range(chips):
        cx, cy = rnd.randrange(w), rnd.randrange(top + 6, foot - 4) if n % 2 else rnd.randrange(foot - 44, foot - 6)
        rh = rnd.randrange(3, 13)
        lo, hi = -rnd.randrange(2, 7), rnd.randrange(2, 7)
        for y in range(cy - rh, cy + rh + 1):
            lo += rnd.choice((-2, -1, 0, 0, 1, 2))
            hi += rnd.choice((-2, -1, 0, 0, 1, 2))
            taper = min(y - (cy - rh), cy + rh - y, 3)                     # ragged, and narrow at its two ends
            l, r = min(lo, -1) * taper // 3, max(hi, 1) * taper // 3
            for x in range(cx + l, cx + r + 1):
                if not (0 <= x < w and top <= y < foot) or inside(x, y):
                    continue
                deep = abs(x - cx) < 2 and abs(y - cy) < rh // 2
                im.set(x, y, shade(PLY, (0.6 if deep else 0.86) * (0.9 if x % 5 == 0 else 1)))
            for x in (cx + l - 1, cx + r + 1):                              # the paint's lip
                if 0 <= x < w and top <= y < foot and not inside(x, y):
                    blend(im, x, y, (30, 20, 16), 0.35)
    # rust: from the gutter, and from the corners of the windows
    starts = [(rnd.randrange(w), top) for _ in range(streaks)]
    for x1, y1, x2, y2 in glass:
        starts += [(x1 + 1, y2), (x2 - 2, y2), (rnd.randrange(x1, x2), y2)]
    for x, y0 in starts:
        n, wide = rnd.randrange(14, 46), rnd.choice((1, 1, 2))
        for k in range(n):
            for dx in range(wide):
                if not inside(x + dx, y0 + k):
                    blend(im, x + dx, y0 + k, RUST, 0.55 * (1 - k / n))
    # the road's dirt, thrown up; moss along the foot
    for y in range(foot - 34, foot):
        f = ((y - (foot - 34)) / 34) ** 2
        for x in range(w):
            blend(im, x, y, (46, 40, 34), 0.5 * f + (0.12 if rnd.random() < f else 0))
    for x in range(w):
        for k in range(rnd.randrange(0, 7)):
            blend(im, x, foot - 1 - k, (64, 88, 44), 0.75 - k * 0.09)
    im.noise(5, seed)


def window(im, x1, y1, x2, y2, seed, state=""):
    """A window in its rubber: dull glass that shows a little sky at the top.
    `state`: "cracked", or "boarded" (a sheet of plywood where the glass was)."""
    rnd = random.Random(seed)
    im.rect(x1 - 2, y1 - 2, x2 + 2, y2 + 2, RUBBER)
    for cx, cy in ((x1 - 2, y1 - 2), (x2 + 1, y1 - 2), (x1 - 2, y2 + 1), (x2 + 1, y2 + 1)):
        im.set(cx, cy, tuple(im.px[0][:3]))                                 # rounded corners
    if state == "boarded":
        for y in range(y1, y2):
            for x in range(x1, x2):
                im.set(x, y, shade(PLY, (0.78 if (x // 9) % 2 else 0.86) * (0.92 if y % 7 == 0 else 1)))
        for nx, ny in ((x1 + 2, y1 + 2), (x2 - 3, y1 + 2), (x1 + 2, y2 - 3), (x2 - 3, y2 - 3), ((x1 + x2) // 2, y1 + 2)):
            im.set(nx, ny, (60, 56, 56))
        for k in range(8):
            blend(im, x1 + 5, y1 + 3 + k, RUST, 0.5 - k * 0.05)
        return
    for y in range(y1, y2):
        f = (y - y1) / (y2 - y1)
        for x in range(x1, x2):
            im.set(x, y, mix((86, 98, 106), GLASS, min(1, f * 1.6)))
            if rnd.random() < 0.10:
                blend(im, x, y, (150, 146, 130), 0.25)                       # dust
    for k in range(x2 - x1 - 8):                                             # a wiped streak of light
        blend(im, x1 + 4 + k, y1 + 3 + k // 4, (170, 180, 184), 0.18)
    if state == "cracked":
        x, y = x1 + (x2 - x1) * 2 // 3, y2 - 1
        while y > y1 and x1 < x < x2 - 1:
            im.set(x, y, (196, 204, 206))
            if rnd.random() < 0.3:
                for k in range(1, rnd.randrange(3, 9)):
                    if x1 <= x - k:
                        blend(im, x - k, y - k // 2, (196, 204, 206), 0.7)
            x += rnd.choice((-1, 0, 0, 1))
            y -= 1


def paintwork(w, paint, seed):
    """A piece of the bus's side, w wide: the yellowed roof and its gutter,
    the paint, the waist stripe, the black skirt."""
    im = Img(w, H, faded(paint))
    old = faded(CREAM)
    im.rect(0, 0, w, 9, old)                                                 # the roof's edge
    im.rect(0, 9, w, 11, shade(old, 0.55))                                   # its gutter
    im.rect(0, 100, w, 105, old)                                             # the waist
    im.rect(0, 105, w, 106, shade(faded(paint), 0.7))
    im.rect(0, H - 10, w, H, (30, 28, 28))                                   # the skirt
    return im


def plate(im, x1, y1, x2, y2):
    im.rect(x1, y1, x2, y2, PLATE)
    im.frame(x1, y1, x2, y2, INK, 1)
    for cx, cy in ((x1, y1), (x2 - 1, y1), (x1, y2 - 1), (x2 - 1, y2 - 1)):
        im.set(cx, cy, tuple(im.px[(y1 - 1) * im.w + x1][:3]))
    for cx in (x1 + 3, x2 - 4):                                              # its two screws, and what runs from them
        im.set(cx, y1 + 2, (90, 70, 56))
        for k in range(1, 7):
            blend(im, cx, y1 + 2 + k, RUST, 0.4 - k * 0.05)


def make(out):
    for L, paint, num, goes in LIVERIES:
        seed = 100 + ord(L) * 10
        old = faded(paint)
        for v in range(VARIANTS):
            body = paintwork(64, paint, seed)
            box = (7, 46, 57, 90)
            window(body, *box, seed + v, ("", "", "cracked", "boarded", "")[v])
            weather(body, seed + v * 7, old, chips=(3, 5, 2, 4, 9)[v], streaks=(4, 6, 3, 5, 7)[v], glass=[box])
            out[f"textures/AJ{L}US{v or ''}.png"] = body.png()

        for name, left in (("Z", True), ("Y", False)):                      # an end: a wheel, the corner's trim
            end = paintwork(48, paint, seed)
            box = (9, 46, 39, 90) if left else (9, 46, 39, 90)
            window(end, *box, seed + 31 + left)
            cx = 24
            end.disc(cx, H - 20, 19, (24, 22, 22))                          # the wheel arch
            end.disc(cx, H - 18, 16, (38, 36, 36))                          # the tyre: flat, and painted on
            end.disc(cx, H - 18, 7, shade(faded(CREAM), 0.8))
            end.disc(cx, H - 18, 3, RUST)
            for k in range(0, 6):
                end.set(cx - 6 + k * 2, H - 18 + (-5 if k % 2 else 5), RUST)
            x = 0 if left else 44
            end.rect(x, 0, x + 4, H - 10, faded(CREAM))                     # the corner's trim
            end.rect(x + (4 if left else -1), 0, x + (5 if left else 0), H - 10, shade(old, 0.6))
            weather(end, seed + 40 + left, old, chips=3, streaks=3, glass=[box])
            out[f"textures/AJ{L}US{name}.png"] = end.png()

        front = paintwork(144, paint, seed)
        panes = [(14, 40, 70, 92), (74, 40, 130, 92)]
        window(front, *panes[0], seed + 51, "cracked")
        window(front, *panes[1], seed + 52)
        plate(front, 14, 12, 132, 35)                                        # АВТОБУС and its number
        rnd = random.Random(seed + 53)
        cyr(front, "АВТОБУС", 20, 19, INK, 2, rnd)
        digit(front, num[0], 108, 16, (150, 30, 26), 3)
        digit(front, num[1], 119, 16, (150, 30, 26), 3)
        for cx, alive in ((24, True), (120, False)):                         # lamps: one has gone
            front.disc(cx, 116, 10, (60, 58, 58))
            front.disc(cx, 116, 8, (206, 196, 150) if alive else (52, 52, 56))
            if alive:
                front.disc(cx - 2, 114, 3, (236, 228, 190))
            else:
                for k in range(-6, 7):
                    front.set(cx + k, 116 + k // 2, (20, 20, 22))            # its glass, broken
        front.rect(46, 108, 98, 126, (34, 32, 32))                           # the grille
        for gy in range(110, 126, 3):
            front.rect(48, gy, 96, gy + 1, (96, 90, 84))
        front.rect(0, H - 14, 144, H - 6, (112, 108, 104))                   # the bumper
        front.rect(0, H - 14, 144, H - 13, (150, 146, 140))
        for bx in range(4, 144, 9):
            blend(front, bx + rnd.randrange(4), H - 12, RUST, 0.8)
            blend(front, bx + rnd.randrange(4), H - 10, RUST, 0.8)
        for x in (0, 140):
            front.rect(x, 0, x + 4, H - 14, faded(CREAM))
        weather(front, seed + 55, old, chips=7, streaks=9, glass=panes + [(14, 12, 132, 35), (0, H - 14, 144, H), (12, 104, 132, 128)])
        out[f"textures/AJ{L}USF.png"] = front.png()

        back = paintwork(144, paint, seed)
        pane = (30, 44, 114, 84)
        window(back, *pane, seed + 61)
        back.rect(40, 108, 104, 130, shade(old, 0.8))                        # the engine's cover
        back.frame(40, 108, 104, 130, shade(old, 0.5), 1)
        for gx in range(46, 100, 6):
            back.rect(gx, 112, gx + 2, 127, (40, 34, 32))
        for cx in (16, 128):                                                 # tail lamps
            back.rect(cx - 6, 108, cx + 6, 128, (40, 38, 38))
            back.rect(cx - 5, 109, cx + 5, 120, (150, 34, 30))
            back.rect(cx - 5, 121, cx + 5, 127, (176, 128, 52))
        digit(back, num[0], 58, 18, faded(CREAM), 4)                         # its number, painted large
        digit(back, num[1], 76, 18, faded(CREAM), 4)
        back.rect(0, H - 14, 144, H - 6, (112, 108, 104))
        back.rect(0, H - 14, 144, H - 13, (150, 146, 140))
        for x in (0, 140):
            back.rect(x, 0, x + 4, H - 14, faded(CREAM))
        weather(back, seed + 65, old, chips=8, streaks=8, glass=[pane, (0, H - 14, 144, H), (8, 106, 136, 131), (54, 16, 96, 40)])
        out[f"textures/AJ{L}USR.png"] = back.png()

        for n in range(10):                                                  # 0: a door with no number
            top = Img(64, 48, old)
            top.rect(0, 0, 64, 9, faded(CREAM))
            top.rect(0, 9, 64, 11, shade(faded(CREAM), 0.55))
            rnd = random.Random(seed + 70 + n)
            if n:
                name = goes.get(n, "")
                wide = 2 if len(name) > 9 else 0                             # ten letters want the whole width
                plate(top, 3 - wide, 15, 61 + wide, 45)
                digit(top, str(n), 27, 18 if name else 21, INK, 3 if name else 4)
                if name:
                    cyr(top, name, 32 - len(name) * 3, 37, (150, 30, 26), 1, rnd)
                weather(top, seed + 80 + n, old, top=11, foot=200, chips=1, streaks=2, glass=[(3 - wide, 15, 61 + wide, 45)])
                for _ in range(40):                                          # the plate has had its weather too
                    blend(top, rnd.randrange(4, 60), rnd.randrange(16, 44), (120, 96, 70), 0.3)
            else:
                top.rect(3, 15, 61, 45, shade(paint, 0.92))                  # where the plate kept the sun off
                top.frame(3, 15, 61, 45, shade(old, 0.7), 1)
                for cx in (6, 57):
                    top.set(cx, 17, (30, 26, 26))                            # its screw holes
                    for k in range(1, 12):
                        blend(top, cx, 17 + k, RUST, 0.6 - k * 0.05)
                weather(top, seed + 80, old, top=11, foot=200, chips=2, streaks=3)
            out[f"textures/AJ{L}N{n}.png"] = top.png()

    for n in range(10):
        for c in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "C"):
            lamp = Img(16, 128, (30, 30, 36))
            lamp.frame(0, 0, 16, 128, (70, 66, 60), 1)
            digit(lamp, str(n), 5, 30, (232, 224, 200), 2)
            col = ((236, 228, 204) if c == "C" else (232, 224, 200) if c == 7 else PAIR_COLOURS[c] if c in PAIR_COLOURS
                   else DOOR_COLOURS[c] if c else (52, 52, 58))
            lamp.disc(8, 54, 5, col)
            if c == "C":                                                     # the clocked door: a dial, its two hands
                lamp.rect(8, 50, 9, 55, (30, 30, 46))
                lamp.rect(8, 54, 11, 55, (30, 30, 46))
            elif c:
                lamp.disc(7, 53, 2, shade(col, 1.3))
            out[f"textures/AJR{n}{c}.png"] = lamp.png()
