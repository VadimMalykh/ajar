"""Pictures for stepping out of a fight (tools/ajartime.py): the time door."""
import gfx
from gfx import Img, shade

IVORY = (222, 214, 190)


def time_door():
    """A door the colour of a clock's face, with a clock on it: a quarter to."""
    im = Img(64, 96, IVORY)
    im.frame(0, 0, 64, 96, shade(IVORY, 0.45), 3)
    for y1, y2 in ((8, 44), (52, 88)):
        im.rect(9, y1, 55, y2, shade(IVORY, 0.85))
        im.frame(9, y1, 55, y2, shade(IVORY, 0.55), 2)
    im.noise(6, 10)
    im.disc(53, 49, 3, (235, 215, 140))
    dark = (40, 36, 30)
    im.disc(32, 26, 12, dark)
    im.disc(32, 26, 10, (250, 248, 240))
    for hx, hy in ((32, 17), (41, 26), (32, 35), (23, 26)):          # the quarters
        im.rect(hx - 1, hy - 1, hx + 1, hy + 1, dark)
    for hx, hy in ((36, 18), (40, 22), (40, 30), (36, 34), (27, 34), (23, 30), (23, 22), (27, 18)):
        im.set(hx, hy, shade(IVORY, 0.5))
    im.rect(31, 18, 33, 27, dark)             # the long hand, at twelve
    im.rect(24, 25, 33, 27, dark)             # the short hand, at nine
    return im


def make(out):
    d = time_door()
    out["textures/AJDR10.png"] = d.png()
    t = Img(64, 64, shade(IVORY, 0.7))
    t.noise(5, 30)
    for y in range(0, 64, 16):
        t.rect(0, y, 64, y + 1, shade(IVORY, 0.4))
    out["textures/AJTR10.png"] = t.png()
    out["flats/AJTF10.png"] = t.png()
    # a steel cupboard, shut and open (AjarLocker)
    steel = (120, 128, 136)
    for fr, is_open in (("A", False), ("B", True)):
        c = Img(40, 56, steel)
        c.frame(0, 0, 40, 56, shade(steel, 0.5), 2)
        if is_open:
            c.rect(4, 4, 36, 52, (24, 24, 28))
            c.rect(4, 27, 36, 29, shade(steel, 0.7))          # a shelf
        else:
            c.rect(19, 3, 21, 53, shade(steel, 0.5))          # two leaves
            c.rect(15, 26, 18, 32, (235, 215, 140))
            c.rect(22, 26, 25, 32, (235, 215, 140))
            for x in (6, 24):                                 # louvres at the head of each leaf
                for y in (8, 11, 14):
                    c.rect(x, y, x + 10, y + 1, shade(steel, 0.6))
            c.noise(5, 31)
        out[f"sprites/AJLK{fr}0.png"] = c.png(grab=(20, 56))
    # a plate on the wall that winds the fight back or on by 30 seconds (AjarWind)
    for fr, on in (("A", False), ("B", True)):
        w = Img(30, 30, (34, 36, 42))
        w.frame(0, 0, 30, 30, (206, 180, 96), 2)
        lit = (250, 244, 214)
        for k in range(2):                                    # two arrowheads
            x0 = 5 + 10 * k
            for i in range(10):
                d = (9 - i if on else i) // 2
                w.rect(x0 + i, 9 - d, x0 + i + 1, 10 + d, lit)
        gfx.text(w, "30", 6, 16, lit)
        out[f"sprites/AJWD{fr}0.png"] = w.png(grab=(15, 30))
    # the top of a tall block with an arrow on it, pointing south (a flat's top is north)
    ar = Img(64, 64, (150, 146, 138))
    ar.noise(6, 32)
    ar.frame(0, 0, 64, 64, (110, 106, 100), 2)
    red = (190, 40, 30)
    ar.rect(28, 10, 36, 40, red)
    for i in range(14):
        ar.rect(32 - (14 - i), 40 + i, 32 + (14 - i), 41 + i, red)
    out["flats/AJARROW.png"] = ar.png()
