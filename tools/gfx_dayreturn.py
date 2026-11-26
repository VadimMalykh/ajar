"""MAP22 "Day Return" (tools/map_dayreturn.py): what the first version draws of
its own. Modest: the look of THEN is a look board for later (PLAN.md, "MAP22
"Day Return": the first version, as decided").

The new bus (livery E, ajarmap.bus(livery="E")): the old bus's drawing
(gfx_bus.py) forty years younger. Fresh red, a clean cream roof and waist
stripe, clean glass in every window, no rust, no patches, no moss. Its plates
are the white route plates of the old one, new: 1 ГОСТИНИЦА, 2 ТЕАТР, 5 ВОКЗАЛ,
7 ДЕПО; 3, 6 and 8 the number only (6 as MAP10's brass door); 4 a blank white
plate (the line starts tomorrow).
  AJEUS, AJEUS1..4   64x144   the body between two doors (the depot's buses too)
  AJEUSZ, AJEUSY     48x144   its two ends
  AJEUSF, AJEUSR    144x144   its front and its back
  AJENn              64x48    over door n

Others:
  AJ22SKY   1024x256  the day sky THEN (a sky transfer: map_dayreturn.py)
  AJ22D12     64x128  the shelter's brass door THEN, two locks (1 and 2) and
                      a plate over it, LINE 6: the shelter's ribbed steel over
                      the leaf (ajarmap.roomdoor(skin="AJ22D", keys="12"))
  AJ22TT      64x128  the shelter's wall piece with the stop's sign and its
                      timetable THEN, new (where the old one is AJQSA)
  AJ22P4     128x512  the depot's brick (AJQB) with the fitters' plate THEN,
                      LINE 4 / FROM TOMORROW, over the clocked door
Doom's stone NOW (doors 1, 5 and 6 of the old bus, the shelter's brass frame)
is the IWAD's own TANROCK2, as MAP21's: nothing is drawn for it.
"""
import math
import random

import gfx
from gfx import Img, shade, digit, text, unpng
from gfx_bus import (cyr, mix, window, plate, H, RED, CREAM, INK, PLATE, RUBBER, GLASS)

gfx.DIGITS.setdefault("W", ("10001", "10001", "10101", "11011", "10001"))     # (TOMORROW)

LETTER = "E"
NUMBER = "10"
GOES = {1: "ГОСТИНИЦА", 2: "ТЕАТР", 5: "ВОКЗАЛ", 7: "ДЕПО"}
FRESH = (204, 36, 30)           # the red when it was new
STRIPE = (232, 222, 190)        # the cream, clean
BRASS = gfx.BRASS


def paint(w, seed):
    """A piece of the new bus's side, w wide: the cream roof and its gutter,
    the red, the cream waist stripe, the black skirt; a faint even grain."""
    im = Img(w, H, FRESH)
    im.rect(0, 0, w, 9, STRIPE)
    im.rect(0, 9, w, 11, shade(STRIPE, 0.6))
    im.rect(0, 100, w, 105, STRIPE)
    im.rect(0, 105, w, 106, shade(FRESH, 0.7))
    im.rect(0, H - 10, w, H, (28, 26, 26))
    im.rect(0, 11, w, 12, shade(FRESH, 1.12))                                 # the light on the top of the panel
    im.noise(3, seed)
    return im


def clean_window(im, x1, y1, x2, y2, seed):
    """A window in new rubber: clear glass, the sky in its top half."""
    im.rect(x1 - 2, y1 - 2, x2 + 2, y2 + 2, RUBBER)
    for y in range(y1, y2):
        f = (y - y1) / (y2 - y1)
        for x in range(x1, x2):
            im.set(x, y, mix((150, 190, 222), (60, 80, 98), min(1, f * 1.4)))
    for k in range(x2 - x1 - 8):                                             # a glint
        im.set(x1 + 4 + k, y1 + 3 + k // 4, (226, 236, 244))


def new_plate(im, x1, y1, x2, y2):
    im.rect(x1, y1, x2, y2, (244, 242, 232))
    im.frame(x1, y1, x2, y2, INK, 1)
    for cx in (x1 + 3, x2 - 4):
        im.set(cx, y1 + 2, (120, 120, 124))


def bus(out):
    seed = 2200
    for v in range(5):                                                       # no two panels alike: only the grain differs
        body = paint(64, seed + v)
        clean_window(body, 7, 46, 57, 90, seed + v)
        out[f"textures/AJ{LETTER}US{v or ''}.png"] = body.png()
    for name, left in (("Z", True), ("Y", False)):
        end = paint(48, seed + 10 + left)
        clean_window(end, 9, 46, 39, 90, seed + 11)
        cx = 24
        end.disc(cx, H - 20, 19, (24, 22, 22))
        end.disc(cx, H - 18, 16, (34, 34, 36))
        end.disc(cx, H - 18, 7, (200, 200, 196))
        end.disc(cx, H - 18, 3, (90, 90, 94))
        x = 0 if left else 44
        end.rect(x, 0, x + 4, H - 10, STRIPE)
        out[f"textures/AJ{LETTER}US{name}.png"] = end.png()
    front = paint(144, seed + 20)
    for pane in ((14, 40, 70, 92), (74, 40, 130, 92)):
        clean_window(front, *pane, seed + 21)
    new_plate(front, 14, 12, 132, 35)
    cyr(front, "АВТОБУС", 20, 19, INK, 2)
    digit(front, NUMBER[0], 108, 16, (170, 30, 26), 3)
    digit(front, NUMBER[1], 119, 16, (170, 30, 26), 3)
    for cx in (24, 120):
        front.disc(cx, 116, 10, (70, 68, 68))
        front.disc(cx, 116, 8, (236, 230, 196))
        front.disc(cx - 2, 114, 3, (255, 252, 230))
    front.rect(46, 108, 98, 126, (34, 32, 32))
    for gy in range(110, 126, 3):
        front.rect(48, gy, 96, gy + 1, (150, 150, 154))
    front.rect(0, H - 14, 144, H - 6, (176, 178, 182))
    front.rect(0, H - 14, 144, H - 13, (220, 222, 226))
    for x in (0, 140):
        front.rect(x, 0, x + 4, H - 14, STRIPE)
    out[f"textures/AJ{LETTER}USF.png"] = front.png()
    back = paint(144, seed + 30)
    clean_window(back, 30, 44, 114, 84, seed + 31)
    back.rect(40, 108, 104, 130, shade(FRESH, 0.85))
    back.frame(40, 108, 104, 130, shade(FRESH, 0.55), 1)
    for gx in range(46, 100, 6):
        back.rect(gx, 112, gx + 2, 127, (40, 34, 32))
    for cx in (16, 128):
        back.rect(cx - 6, 108, cx + 6, 128, (40, 38, 38))
        back.rect(cx - 5, 109, cx + 5, 120, (210, 40, 32))
        back.rect(cx - 5, 121, cx + 5, 127, (236, 168, 60))
    digit(back, NUMBER[0], 58, 18, STRIPE, 4)
    digit(back, NUMBER[1], 76, 18, STRIPE, 4)
    back.rect(0, H - 14, 144, H - 6, (176, 178, 182))
    back.rect(0, H - 14, 144, H - 13, (220, 222, 226))
    for x in (0, 140):
        back.rect(x, 0, x + 4, H - 14, STRIPE)
    out[f"textures/AJ{LETTER}USR.png"] = back.png()
    for n in range(10):                                                      # over each door
        top = Img(64, 48, FRESH)
        top.rect(0, 0, 64, 9, STRIPE)
        top.rect(0, 9, 64, 11, shade(STRIPE, 0.6))
        top.noise(3, seed + 40 + n)
        name = GOES.get(n, "")
        wide = 2 if len(name) > 9 else 0
        new_plate(top, 3 - wide, 15, 61 + wide, 45)
        if n and n != 4:                                                     # 4: a blank plate, the line not run yet
            digit(top, str(n), 27, 18 if name else 21, INK, 3 if name else 4)
            if name:
                cyr(top, name, 32 - len(name) * 3, 37, (170, 30, 26), 1)
        out[f"textures/AJ{LETTER}N{n}.png"] = top.png()


def sky(out):
    """A day sky, once round, 1024 by 256: blue going pale at the horizon, a few
    soft fair-weather clouds, a sun low in the south-east."""
    w, h = 1024, 256
    top, low = (78, 128, 196), (196, 214, 230)
    rows = [mix(top, low, (y / (h - 1)) ** 1.6) for y in range(h)]
    im = Img(w, h)
    for y in range(h):
        row = list(rows[y]) + [255]
        im.px[y * w:(y + 1) * w] = [list(row) for _ in range(w)]
    r = random.Random(2222)
    clouds = [(r.randrange(w), r.randrange(60, 190), r.randrange(40, 110), r.uniform(0.35, 0.8)) for _ in range(26)]
    for cx, cy, size, a in clouds:
        for _ in range(int(size * 1.2)):                                     # a cloud is puffs
            px, py = cx + r.gauss(0, size * 0.6), cy + r.gauss(0, size * 0.12)
            rad = r.uniform(size * 0.12, size * 0.28)
            for y in range(int(py - rad), int(py + rad) + 1):
                if not 0 <= y < h:
                    continue
                for x in range(int(px - rad), int(px + rad) + 1):
                    d = math.hypot(x - px, (y - py) * 1.6) / rad
                    if d < 1:
                        p = im.px[y * w + x % w]
                        lit = (250, 250, 248) if y < py else (214, 220, 230)
                        p[:3] = mix(p[:3], lit, a * (1 - d) ** 0.7)
    sx, sy = 300, 150
    for y in range(sy - 40, sy + 41):
        for x in range(sx - 40, sx + 41):
            d = math.hypot(x - sx, y - sy)
            if d < 40:
                p = im.px[y * w + x]
                p[:3] = mix(p[:3], (255, 250, 226), 1 if d < 9 else 0.45 * (1 - d / 40) ** 2)
    out["textures/AJ22SKY.png"] = im.png()


def brass_door(out):
    """The shelter's brass door THEN: the shelter's steel over a brass leaf (96)
    with two lock plates, 1 and 2, and LINE 6 over it."""
    steel = unpng(out["textures/AJQS.png"])
    im = Img(64, 128)
    for y in range(128):
        for x in range(64):
            im.px[y * 64 + x] = list(steel.px[(y % steel.h) * steel.w + x % steel.w])
    im.rect(4, 10, 60, 26, (34, 32, 30))                                     # the plate over it: LINE 6
    im.frame(4, 10, 60, 26, BRASS, 1)
    text(im, "LINE 6", 8, 14, BRASS, 1)
    im.rect(0, 28, 64, 32, shade(BRASS, 0.6))                               # its lintel
    leaf = shade(BRASS, 0.92)
    im.rect(0, 32, 64, 128, leaf)
    im.frame(0, 32, 64, 128, shade(BRASS, 0.55), 3)
    for y1, y2 in ((42, 76), (84, 120)):
        im.frame(10, y1, 54, y2, shade(BRASS, 0.7), 2)
    for n, ch in enumerate("12"):                                           # the locks, as AJHK12's
        x = 32 - 18 + 18 * n + 1
        im.rect(x, 62, x + 16, 82, (60, 50, 30))
        im.frame(x, 62, x + 16, 82, (40, 30, 14), 1)
        digit(im, ch, x + 5, 65, BRASS)
        im.rect(x + 7, 77, x + 9, 80, (20, 14, 6))
    im.noise(3, 2231)
    out["textures/AJ22D12.png"] = im.png()


def timetable(out):
    """The shelter's wall piece THEN: the stop's sign and its timetable, new."""
    steel = unpng(out["textures/AJQS.png"])
    im = Img(64, 128)
    for y in range(128):
        for x in range(64):
            im.px[y * 64 + x] = list(steel.px[(y % steel.h) * steel.w + x % steel.w])
    im.rect(6, 6, 58, 34, (236, 232, 214))                                   # the stop's sign
    im.frame(6, 6, 58, 34, (40, 60, 100), 2)
    im.disc(32, 20, 9, (40, 60, 100))
    im.disc(32, 20, 7, (236, 232, 214))
    text(im, "A", 29, 18, (40, 60, 100), 1)
    im.rect(1, 40, 63, 118, (244, 242, 236))                                 # the timetable, pinned: the paper is
    im.frame(1, 40, 63, 118, (120, 118, 110), 1)                             # as wide as ГОСТИНИЦА needs (8..61)
    for k, (n, words) in enumerate((("1", "ГОСТИНИЦА"), ("2", "ТЕАТР"), ("5", "ВОКЗАЛ"), ("7", "ДЕПО"))):
        y = 46 + k * 10
        digit(im, n, 2, y, INK, 1)
        cyr(im, words, 8, y, (60, 60, 70), 1)
    text(im, "LINE 4", 8, 90, (170, 30, 26), 1)
    text(im, "TOMORROW", 8, 100, (170, 30, 26), 1)
    for x, y in ((3, 42), (60, 42), (3, 115), (60, 115)):
        im.set(x, y, (150, 40, 40))
    out["textures/AJ22TT.png"] = im.png()


def fitters_plate(out):
    """The depot's brick, 128 by 512 (laid from its foot: dontpegbottom), with
    the fitters' plate THEN at 96..144 over the floor: LINE 4 / FROM TOMORROW."""
    brick = unpng(out["textures/AJQB.png"])
    w, h = 128, 512
    im = Img(w, h)
    for y in range(h):
        for x in range(w):
            im.px[y * w + x] = list(brick.px[((y - h) % brick.h) * brick.w + x % brick.w])
    y1, y2 = h - 150, h - 96
    im.rect(8, y1, 120, y2, (238, 234, 220))
    im.frame(8, y1, 120, y2, (30, 30, 34), 2)
    for cx, cy in ((12, y1 + 4), (115, y1 + 4), (12, y2 - 5), (115, y2 - 5)):
        im.set(cx, cy, (90, 90, 96))
    text(im, "LINE 4", 40, y1 + 8, (170, 30, 26), 2)
    text(im, "FROM TOMORROW", 14, y1 + 32, INK, 1)
    out["textures/AJ22P4.png"] = im.png()


def make(out):
    bus(out)
    sky(out)
    brass_door(out)
    timetable(out)
    fitters_plate(out)
