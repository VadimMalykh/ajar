"""The water lab's own pictures (tools/map_water.py, map WATER; ajarwater.py).

AJGAUGE: a staff gauge, the depth from the floor it stands on painted every
32 units (a long mark and its number) and every 8 (a short one), white on a
dark board. It is laid from the floor up (`dontpegbottom`): its bottom row
is the floor. 320 tall, more than any basin is deep.
AJFLOATM: MAP20's float mark, on the feed tank's side beside its gauge glass:
272 tall (the tank's rim over the boiler house's floor), a lower texture
pegged at its top, with a red band at 216 (row 56) and the words FLOAT 216.
AJWH A0: the paddle wheel of a spillway (AjarWaterWheel), seen side on, to
be turned by its roll."""
import math

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
    """A paddle wheel 64 across: a rim, eight spokes and paddles, a hub."""
    im = Img(64, 64, (0, 0, 0, 0))
    wood, iron = (128, 92, 56), (70, 72, 78)
    c = 31.5
    for y in range(64):
        for x in range(64):
            r = math.hypot(x - c, y - c)
            a = math.degrees(math.atan2(y - c, x - c)) % 45
            if 26 <= r <= 31 and (a < 9 or a > 36):
                im.set(x, y, shade(wood, 0.8))            # the paddles
            elif 22 <= r <= 25:
                im.set(x, y, iron)                        # the rim
            elif r < 22 and (a < 3 or a > 42):
                im.set(x, y, wood)                        # the spokes
            elif r <= 5:
                im.set(x, y, shade(iron, 1.4))            # the hub
    return im


def make(out):
    out["textures/AJGAUGE.png"] = gauge().png()
    out["textures/AJFLOATM.png"] = float_mark().png()
    out["sprites/AJWHA0.png"] = wheel().png(grab=(32, 32))
