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


def fight_anew(out):
    """The plate on a wall of a fight's hall that begins the fight anew
    (anew.zs, AjarFightAnew): the begin-anew plate of the boxes (AJAN), twice
    its size, in a wide lit frame, and two frames that pulse, so that it is
    seen across a big hall."""
    for fr, glow in (("A", 0.8), ("B", 1.0)):
        dark = (24, 30, 40)
        a = Img(56, 56, dark)
        rim = shade((150, 210, 245), glow)
        a.frame(0, 0, 56, 56, rim, 5)
        a.frame(6, 6, 50, 50, shade((90, 140, 180), glow), 1)
        lit = shade((235, 248, 255), glow)
        a.disc(28, 29, 17, lit)
        a.disc(28, 29, 11, dark)
        a.rect(28, 9, 47, 29, dark)                           # the ring's open quarter
        for i in range(11):                                   # its arrowhead, at twelve, pointing right
            a.rect(28 + i, 7 + i // 2, 29 + i, 19 - i // 2, lit)
        a.disc(28, 29, 4, shade((250, 220, 120), glow))       # the clock's middle
        out[f"sprites/AJAF{fr}0.png"] = a.png(grab=(28, 56))


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
    # a plate on the wall of a room of goes' box that forgets every go (AjarAnew):
    # the wind plate's face with a ring that runs back to its start
    a = Img(30, 30, (34, 36, 42))
    a.frame(0, 0, 30, 30, (150, 200, 230), 2)
    lit = (230, 244, 250)
    a.disc(15, 15, 9, lit)
    a.disc(15, 15, 6, (34, 36, 42))
    a.rect(15, 4, 25, 15, (34, 36, 42))                       # the ring's open quarter
    for i in range(6):                                        # its arrowhead, at twelve, pointing right
        a.rect(15 + i, 3 + i // 2, 16 + i, 10 - i // 2, lit)
    out["sprites/AJANA0.png"] = a.png(grab=(15, 30))
    # a plate on the floor that holds a sprung frame's door open while it is
    # stood on (AjarPlate): up, and pressed
    brass = (176, 146, 70)
    for fr, down in (("A", False), ("B", True)):
        p = Img(56, 56, shade(brass, 0.45))
        p.rect(4, 4, 52, 52, shade(brass, 0.7 if down else 1.0))
        p.frame(4, 4, 52, 52, shade(brass, 0.55 if down else 1.25), 2)
        p.rect(12, 12, 44, 44, (250, 220, 120) if down else shade(brass, 0.85))
        for cx, cy in ((9, 9), (47, 9), (9, 47), (47, 47)):   # rivets
            p.disc(cx, cy, 1, shade(brass, 0.4))
        p.noise(4, 33)
        out[f"sprites/AJPL{fr}0.png"] = p.png(grab=(28, 28))
    # a switch on the wall that sets off a press (AjarPressSwitch): a steel
    # plate with a red lever, up and ready (A), and down while the press works (B)
    for fr, ready in (("A", True), ("B", False)):
        w = Img(24, 32, (96, 102, 110))
        w.frame(0, 0, 24, 32, (60, 64, 70), 2)
        w.rect(3, 26, 21, 29, (220, 180, 40))                 # hazard stripes on its foot
        for x in range(3, 21, 6):
            w.rect(x, 26, x + 3, 29, (30, 30, 30))
        w.rect(10, 6, 14, 22, (40, 40, 44))                   # the slot
        y = 7 if ready else 17
        w.rect(7, y, 17, y + 4, (210, 40, 30))                # the handle
        w.noise(4, 34)
        out[f"sprites/AJPS{fr}0.png"] = w.png(grab=(12, 32))
    # a lamp beside a frame whose Pair must be hung together (AjarTogether):
    # a small clock face; dark (A), lit while a leaf waits (B), green joined
    # (C), red too late (D); amber (E): an earlier self is about to work a shutter or a press
    # (shut.zs, AjarShutLamp and AjarPressLamp: the timetable)
    for fr, lit in (("A", (70, 66, 56)), ("B", (250, 236, 170)), ("C", (90, 230, 110)), ("D", (230, 60, 40)),
                    ("E", (245, 160, 30))):
        c = Img(26, 26, (0, 0, 0, 0))
        c.disc(13, 13, 12, (150, 128, 70))
        c.disc(13, 13, 10, lit)
        dark = (30, 28, 24)
        c.rect(12, 5, 14, 14, dark)                           # the hands, at twelve and three
        c.rect(12, 12, 19, 14, dark)
        out[f"sprites/AJTW{fr}0.png"] = c.png(grab=(13, 26))
    # the top of a tall block with an arrow on it, pointing south (a flat's top is north)
    ar = Img(64, 64, (150, 146, 138))
    ar.noise(6, 32)
    ar.frame(0, 0, 64, 64, (110, 106, 100), 2)
    red = (190, 40, 30)
    ar.rect(28, 10, 36, 40, red)
    for i in range(14):
        ar.rect(32 - (14 - i), 40 + i, 32 + (14 - i), 41 + i, red)
    out["flats/AJARROW.png"] = ar.png()
    case_pictures(out)


def case_pictures(out):
    """For the glass cases of models of a room solved (ajartime.case,
    AjarFigure): the plaque over a case that says "later", the numbers of the
    goes over the selves' heads, and the frames the door figures stand in."""
    # the plaque: ivory as the time door, a clock face and the wind plate's
    # two arrowheads pointing right (wind on): "later"
    pq = Img(64, 32, IVORY)
    pq.frame(0, 0, 64, 32, shade(IVORY, 0.45), 2)
    pq.noise(4, 35)
    dark = (40, 36, 30)
    pq.disc(16, 16, 12, dark)
    pq.disc(16, 16, 10, (250, 248, 240))
    for hx, hy in ((16, 8), (24, 16), (16, 24), (8, 16)):     # the quarters
        pq.rect(hx - 1, hy - 1, hx + 1, hy + 1, dark)
    pq.rect(15, 8, 17, 17, dark)                              # the long hand, at twelve
    pq.rect(15, 15, 22, 17, dark)                             # the short hand, at three
    for k in range(2):                                        # two arrowheads pointing right
        x0 = 33 + 14 * k
        for i in range(13):
            d = (12 - i) * 10 // 12
            pq.rect(x0 + i, 16 - d, x0 + i + 1, 16 + d, dark)
    out["sprites/AJPQA0.png"] = pq.png(grab=(32, 32))
    # the number of a go, 1 to 3 (frames A to C): an ivory digit with a dark outline
    for n, fr in ((1, "A"), (2, "B"), (3, "C")):
        g = Img(25, 35, (0, 0, 0, 0))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                gfx.digit(g, str(n), 5 + dx, 5 + dy, (24, 22, 20), 5)
        gfx.digit(g, str(n), 5, 5, (255, 248, 220), 5)
        out[f"sprites/AJGN{fr}0.png"] = g.png(grab=(12, 35))
    # a door frame's face, at the door's scale (its opening 64 by 96, as the
    # door's picture): the brass of a frame that takes one door only, inlaid
    # with its colour (frames A to F, colours 1 to 6), or plain brass (G)
    brass = (204, 170, 92)
    for c, fr in [(c, "ABCDEF"[c - 1]) for c in gfx.DOOR_COLOURS] + [(0, "G")]:
        f = Img(96, 112, brass)
        f.noise(5, 36)
        f.frame(0, 0, 96, 112, shade(brass, 0.55), 2)
        if c:
            col = gfx.DOOR_COLOURS[c]
            f.rect(5, 5, 11, 112, col)                        # the inlay, round the opening
            f.rect(85, 5, 91, 112, col)
            f.rect(5, 5, 91, 11, col)
            f.rect(5, 5, 91, 6, shade(col, 1.3))
        f.rect(14, 14, 82, 112, shade(brass, 0.5))            # the reveal, in shadow
        f.rect(16, 16, 80, 112, (44, 42, 46))                 # the opening, dark
        out[f"sprites/AJFM{fr}0.png"] = f.png(grab=(48, 112))
