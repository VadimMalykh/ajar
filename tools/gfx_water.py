"""The water lab's own pictures (tools/map_water.py, map WATER; ajarwater.py).

AJGAUGE: a staff gauge, the depth from the floor it stands on painted every
32 units (a long mark and its number) and every 8 (a short one), white on a
dark board. It is laid from the floor up (`dontpegbottom`): its bottom row
is the floor. 320 tall, more than any basin is deep.
AJFLOATM: MAP20's float mark, on the feed tank's side beside its gauge glass:
272 tall (the tank's rim over the boiler house's floor), a lower texture
pegged at its top, with a red band at 216 (row 56) and the words FLOAT 216.
AJWH A0: the paddle wheel of a spillway (AjarWeir), seen side on, to be
turned by its roll: 128 across, drawn at half that in the lab and as large as
the chute lets it be in a level (water.zs).
AJBY A0: MAP20's buoy, a red-and-white ball 24 across with a top mark, its
origin at its bottom (water.zs, AjarBuoy).
AJFJ A0..D0: the lower yard's fountain jet, 96 high, four frames
(AjarFountainJet)."""
import math
import random

from gfx import Img, DIGITS, shade

H = 320


def digit_text(im, s, x, y, c, scale=2):
    for n, ch in enumerate(s):
        for j, row in enumerate(DIGITS[ch]):
            for i, on in enumerate(row):
                if on == "1":
                    xx, yy = x + n * 4 * scale + i * scale, y + j * scale
                    im.rect(xx, yy, xx + scale, yy + scale, c)


def gauge():
    im = Img(64, H, (34, 40, 46))
    im.noise(4, 21)
    board, ink, red = (232, 230, 220), (20, 22, 26), (196, 48, 40)
    im.rect(20, 0, 44, H, board)                     # the staff
    im.frame(19, 0, 45, H, shade(board, 0.5), 1)
    for d in range(0, H, 8):                         # d units above the floor: row H - 1 - d
        y = H - 1 - d
        if d % 32 == 0:
            im.rect(20, y - 1, 44, y + 1, red if d % 64 == 0 else ink)
            if d:
                s = str(d)
                digit_text(im, s, 25 if len(s) < 3 else 21, y - 13, ink)
        else:
            im.rect(20, y, 30, y + 1, ink)
    return im


def float_mark(base=None):
    """`base`: a 64 x 272 picture of the tank's side to paint the mark on (MAP20's look); else plain plates."""
    red, ink = (200, 40, 32), (230, 228, 220)
    if base is not None:
        im = base
    else:
        im = Img(64, 272, (70, 74, 80))
        im.noise(5, 22)
        for y in range(0, 272, 32):                  # the tank's plates, riveted
            im.rect(0, y, 64, y + 1, shade((70, 74, 80), 0.6))
            for x in (6, 58):
                im.rect(x, y + 4, x + 2, y + 6, shade((70, 74, 80), 1.4))
    im.rect(0, 54, 64, 59, red)                      # 216 over the floor: row 272 - 216
    im.rect(28, 60, 36, 80, red)
    im.rect(24, 60, 40, 64, red)
    digit_text(im, "216", 20, 86, ink)
    return im


def wheel():
    """A paddle wheel 128 across: eight paddles of boards with iron edges on
    the ends of eight tapering spokes, a wooden rim between two iron bands,
    a hub with bolts. Wood and iron only. Drawn four samples a pixel each
    way, so that its edges are smooth however it is turned."""
    n, c, ss = 128, 63.5, 4
    wood, dark, iron, steel = (132, 94, 58), (92, 64, 40), (72, 72, 76), (104, 104, 108)
    grain = random.Random(2011)
    streak = [grain.uniform(0.9, 1.08) for _ in range(64)]

    def at(x, y):
        dx, dy = x - c, y - c
        r = math.hypot(dx, dy)
        if r > 63.4:
            return None
        # the nearest of the eight arms: u along it, v across it
        a = math.atan2(dy, dx)
        k = round(a / (math.pi / 4))
        b = k * math.pi / 4
        u = dx * math.cos(b) + dy * math.sin(b)
        v = -dx * math.sin(b) + dy * math.cos(b)
        if 42 <= u <= 63 and abs(v) <= 6.5:                   # a paddle: two boards, an iron edge, a bolt
            if u >= 60.5:
                return iron
            if abs(v) <= 0.6:
                return dark
            if abs(abs(v) - 3.5) < 0.9 and abs(u - 51) < 0.9:
                return steel
            f = streak[int(u) % 64] * (0.88 if v > 3.2 else 1.0)
            return shade(wood, f)
        if 37 <= r <= 45:                                     # the rim: wood between two iron bands
            if r < 38.6 or r > 43.4:
                return iron
            return shade(wood, 0.9 * streak[int(math.degrees(a) / 6) % 64])
        width = 3.2 - (u - 10) * 0.02                         # a spoke, tapering outwards, an iron strap at each end
        if 9 <= u <= 37 and abs(v) <= width:
            if u < 13 or u > 34:
                return iron
            return shade(wood, streak[int(u * 2) % 64] * (0.85 if v > 1.2 else 1.0))
        if r <= 11:                                           # the hub, its ring and four bolts
            if r > 9.4:
                return shade(iron, 0.8)
            for q in range(4):
                bx, by = c + 6 * math.cos(q * math.pi / 2 + math.pi / 4), c + 6 * math.sin(q * math.pi / 2 + math.pi / 4)
                if math.hypot(x - bx, y - by) < 1.4:
                    return steel
            return shade(steel, 0.9) if r < 2.5 else iron
        return None

    im = Img(n, n, (0, 0, 0, 0))
    for y in range(n):
        for x in range(n):
            got = [at(x + (i + 0.5) / ss, y + (j + 0.5) / ss) for i in range(ss) for j in range(ss)]
            hit = [g for g in got if g]
            if hit:
                col = tuple(sum(g[i] for g in hit) // len(hit) for i in range(3))
                im.set(x, y, col + (round(255 * len(hit) / len(got)),))
    return im


def buoy():
    """A safe-water buoy: a ball 24 across in red and white stripes running
    from pole to pole, lit from the upper left, an iron rod and a red ball
    on top. 24 x 34; the ball's bottom is the sprite's last row."""
    w, h, r = 24, 34, 11.6
    cx, cy = 11.5, h - 1 - r
    red, white, iron = (200, 36, 30), (238, 236, 230), (60, 60, 64)
    lx, ly, lz = -0.45, -0.55, 0.7
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    im = Img(w, h, (0, 0, 0, 0))
    ss = 4
    for y in range(h):
        for x in range(w):
            acc, cov = [0, 0, 0], 0
            for i in range(ss):
                for j in range(ss):
                    px, py = x + (i + 0.5) / ss, y + (j + 0.5) / ss
                    nx, ny = (px - cx - 0.5) / r, (py - cy - 0.5) / r
                    col = None
                    if nx * nx + ny * ny <= 1:
                        nz = math.sqrt(1 - nx * nx - ny * ny)
                        lon = math.degrees(math.atan2(nx, nz))           # stripes from pole to pole
                        base = red if int((lon + 90) // 30) % 2 == 0 else white
                        d = max(0, (nx * lx + ny * ly + nz * lz) / ln)
                        f = 0.42 + 0.75 * d + (0.25 if d > 0.93 else 0)
                        col = shade(base, f)
                    elif abs(px - 12) <= 1.1 and 4.5 <= py <= cy - r + 1.5:
                        col = iron                                          # the rod
                    elif math.hypot(px - 12, py - 3.6) <= 3.1:
                        col = shade(red, 1.15 if px < 11.6 and py < 3 else 0.85)   # the top mark
                    if col:
                        cov += 1
                        for k in range(3):
                            acc[k] += col[k]
            if cov:
                im.set(x, y, tuple(v // cov for v in acc) + (round(255 * cov / (ss * ss)),))
    return im


def jet(frame):
    """The fountain's jet, 64 x 96, its foot the bottom row: a column of
    water up to 80, breaking into a crown that falls back to both sides,
    and spray at the foot. Pale water, white where it is thickest; the
    four frames differ in their drops and the column's wobble."""
    w, h = 64, 96
    rnd = random.Random(700 + frame)
    acc = [[0.0] * w for _ in range(h)]

    def dab(x, y, a, rad=0.9):
        for yy in range(int(y - rad - 1), int(y + rad + 2)):
            for xx in range(int(x - rad - 1), int(x + rad + 2)):
                if 0 <= xx < w and 0 <= yy < h:
                    d = math.hypot(xx + 0.5 - x, yy + 0.5 - y)
                    if d <= rad + 0.5:
                        acc[yy][xx] += a * min(1, rad + 0.5 - d)

    top = 15
    for y in range(top, h):                                     # the column
        t = (y - top) / (h - top)
        half = 1.3 + 1.6 * t
        x0 = 32 + 0.8 * math.sin(y * 0.35 + frame * 1.6)
        for xx in range(w):
            d = abs(xx + 0.5 - x0)
            if d <= half + 0.5:
                acc[y][xx] += (0.95 if d < half * 0.5 else 0.6) * min(1, half + 0.5 - d)
    for k in range(18):                                          # the crown: arcs falling back
        side = -1 if k % 2 else 1
        vx = side * rnd.uniform(0.6, 1.5)
        vy = rnd.uniform(0.6, 1.3)
        x, y = 32.0, top + rnd.uniform(-2, 2)
        steps = 0
        while y < h - 2 and 1 < x < w - 2:
            on = (steps + frame * 3 + k) % 7 < 5
            if on:
                dab(x, y, 0.55 if steps < 10 else 0.4, 0.8)
            x += vx * 0.5
            y += -vy * 0.5 + 0.04 * steps
            steps += 1
    for _ in range(28):                                          # drops and spray at the foot
        dab(rnd.uniform(6, 58), rnd.uniform(20, h - 3), rnd.uniform(0.3, 0.7), rnd.uniform(0.4, 1.0))
    for _ in range(30):
        dab(32 + rnd.gauss(0, 7), h - 1 - abs(rnd.gauss(0, 4)), rnd.uniform(0.3, 0.6), 0.8)
    im = Img(w, h, (0, 0, 0, 0))
    pale, foam = (176, 210, 228), (246, 250, 252)
    for y in range(h):
        for x in range(w):
            a = min(1.0, acc[y][x])
            if a > 0.03:
                col = tuple(int(pale[i] + (foam[i] - pale[i]) * min(1, a * 1.2)) for i in range(3))
                im.set(x, y, col + (int(40 + 200 * a),))
    return im


def make(out):
    out["textures/AJGAUGE.png"] = gauge().png()
    out["textures/AJFLOATM.png"] = float_mark().png()
    out["sprites/AJWHA0.png"] = wheel().png(grab=(64, 64))
    out["sprites/AJBYA0.png"] = buoy().png(grab=(12, 34))
    for f in range(4):
        out[f"sprites/AJFJ{'ABCD'[f]}0.png"] = jet(f).png(grab=(32, 96))
