"""Procedural placeholder art, written as PNG with no dependencies."""
import random
import struct
import zlib


class Img:
    def __init__(self, w, h, color=(0, 0, 0, 255)):
        self.w, self.h = w, h
        color = list(color) + [255] * (4 - len(color))
        self.px = [list(color) for _ in range(w * h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y * self.w + x] = list(c) + [255] * (4 - len(c))

    def rect(self, x1, y1, x2, y2, c):
        for y in range(y1, y2):
            for x in range(x1, x2):
                self.set(x, y, c)

    def frame(self, x1, y1, x2, y2, c, t=1):
        self.rect(x1, y1, x2, y1 + t, c)
        self.rect(x1, y2 - t, x2, y2, c)
        self.rect(x1, y1, x1 + t, y2, c)
        self.rect(x2 - t, y1, x2, y2, c)

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def tri(self, cx, cy, r, c):
        for y in range(int(cy - r), int(cy + r) + 1):
            half = (y - (cy - r)) / 2
            for x in range(int(cx - half), int(cx + half) + 1):
                self.set(x, y, c)

    def diamond(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            half = r - abs(y - cy)
            for x in range(cx - half, cx + half + 1):
                self.set(x, y, c)

    def noise(self, amount, seed=1):
        rnd = random.Random(seed)
        for p in self.px:
            d = rnd.randint(-amount, amount)
            for i in range(3):
                p[i] = max(0, min(255, p[i] + d))

    def png(self, grab=None):
        raw = b"".join(b"\0" + bytes(v for p in self.px[y * self.w:(y + 1) * self.w] for v in p)
                       for y in range(self.h))
        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
        out = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
        if grab:
            out += chunk(b"grAb", struct.pack(">ii", *grab))
        return out + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


DOOR_COLOURS = {1: (200, 60, 50), 2: (60, 110, 220), 3: (60, 170, 80),
                4: (215, 170, 40), 5: (150, 80, 200)}


def door(colour):
    """64x96 door leaf: two panels, a knob and a glyph that names the far side."""
    base = DOOR_COLOURS[colour]
    im = Img(64, 96, base)
    im.frame(0, 0, 64, 96, shade(base, 0.45), 3)
    for y1, y2 in ((8, 44), (52, 88)):
        im.rect(9, y1, 55, y2, shade(base, 0.8))
        im.frame(9, y1, 55, y2, shade(base, 0.55), 2)
    im.noise(6, colour)
    im.disc(53, 49, 3, (235, 215, 140))
    white = (245, 245, 235)
    if colour == 1:
        im.disc(32, 26, 9, white)
    elif colour == 2:
        im.tri(32, 26, 10, white)
    elif colour == 3:
        im.rect(23, 17, 41, 35, white)
    elif colour == 4:
        im.diamond(32, 26, 11, white)
    else:
        im.rect(29, 15, 35, 37, white)
        im.rect(21, 23, 43, 29, white)
    return im


def make_all():
    """Returns {path inside pk3: png bytes}."""
    out = {}

    wall = Img(128, 128, (188, 184, 176))
    wall.noise(7, 11)
    for i in range(0, 128, 64):
        wall.rect(i, 0, i + 1, 128, (150, 146, 140))
        wall.rect(i + 1, 0, i + 2, 128, (206, 202, 196))
    wall.rect(0, 0, 128, 2, (150, 146, 140))
    wall.rect(0, 118, 128, 128, (120, 116, 112))
    out["textures/AJWALL.png"] = wall.png()

    # framed pictures of doors, one per colour, on a strip of that wall as
    # tall as the wall they hang on (A: 336, the hall; B: 176, the gallery)
    for c, base in DOOR_COLOURS.items():
        for tag, tall in (("A", 336), ("B", 176)):
            pic = Img(64, tall)
            for y in range(tall):
                for x in range(64):
                    pic.set(x, y, wall.px[(y % 128) * 128 + x])
            top = tall - 124                                     # picture: 48 to 124 above the floor
            pic.rect(11, top + 3, 57, top + 79, (60, 56, 52))    # shadow
            pic.rect(8, top, 54, top + 76, (176, 140, 60))       # gilt frame
            pic.frame(8, top, 54, top + 76, (110, 84, 30), 1)
            pic.rect(13, top + 5, 49, top + 71, (28, 30, 44))    # a dark room
            pic.rect(13, top + 56, 49, top + 71, (58, 56, 66))   # its floor
            pic.rect(22, top + 18, 40, top + 58, base)           # a door standing in it
            pic.frame(22, top + 18, 40, top + 58, shade(base, 0.5), 1)
            pic.rect(25, top + 22, 37, top + 36, shade(base, 0.8))
            pic.rect(25, top + 40, 37, top + 54, shade(base, 0.8))
            pic.disc(37, top + 39, 1, (250, 240, 200))
            pic.frame(13, top + 5, 49, top + 71, (20, 18, 24), 1)
            out[f"textures/AJP{tag}{c}.png"] = pic.png()

    # the cell: brick
    brick = Img(64, 64, (150, 140, 132))
    brick.noise(9, 31)
    for row in range(4):
        brick.rect(0, row * 16, 64, row * 16 + 2, (92, 86, 82))
        for x in ((0, 32) if row % 2 else (16, 48)):
            brick.rect(x, row * 16, x + 2, row * 16 + 16, (92, 86, 82))
    out["textures/AJBRICK.png"] = brick.png()

    # the vault: rows of small locked doors
    safe = Img(64, 64, (176, 178, 184))
    safe.noise(4, 32)
    for bx in (0, 32):
        for by in (0, 32):
            safe.frame(bx, by, bx + 32, by + 32, (104, 106, 114), 2)
            safe.frame(bx + 5, by + 5, bx + 27, by + 27, (206, 208, 214), 1)
            safe.disc(bx + 22, by + 16, 2, (60, 60, 66))
            safe.rect(bx + 21, by + 17, bx + 24, by + 21, (60, 60, 66))
    out["textures/AJSAFE.png"] = safe.png()

    # carpet for the runners between doors: pale, so the room's tint colours it
    rug = Img(64, 64, (214, 204, 190))
    rug.noise(6, 33)
    for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64), (32, 32)):
        rug.diamond(cx, cy, 14, (160, 146, 128))
        rug.diamond(cx, cy, 9, (228, 220, 208))
        rug.diamond(cx, cy, 4, (150, 60, 50))
    out["flats/AJRUG.png"] = rug.png()

    # the row of ceiling lights over a runner
    lite = Img(64, 64, (96, 98, 104))
    lite.noise(4, 34)
    lite.rect(8, 8, 56, 56, (255, 252, 236))
    lite.frame(8, 8, 56, 56, (60, 62, 68), 2)
    lite.rect(31, 8, 33, 56, (190, 188, 176))
    out["flats/AJLITE.png"] = lite.png()

    # a balcony railing (see-through) and the garden's grass
    rail = Img(64, 32, (0, 0, 0, 0))
    rail.rect(0, 0, 64, 4, (176, 140, 60))
    rail.rect(0, 28, 64, 32, (110, 84, 30))
    for x in range(4, 64, 16):
        rail.rect(x, 4, x + 4, 28, (150, 118, 48))
    out["textures/AJRAIL.png"] = rail.png()
    grass = Img(64, 64, (150, 170, 120))
    grass.noise(14, 35)
    out["flats/AJGRASS.png"] = grass.png()

    # fixed doorways: heavy pale stone, nothing like a coloured door's trim
    arch = Img(64, 64, (214, 208, 196))
    arch.noise(8, 36)
    for y in range(0, 64, 32):
        arch.rect(0, y, 64, y + 2, (120, 114, 104))
        arch.rect(0, y + 2, 64, y + 4, (238, 234, 226))
        for x in ((0, 32) if y else (16, 48)):
            arch.rect(x, y, x + 2, y + 32, (120, 114, 104))
    out["textures/AJARCH.png"] = arch.png()
    out["flats/AJARCHF.png"] = arch.png()

    # stage curtain
    curt = Img(64, 64, (150, 28, 34))
    for x in range(64):
        f = 0.62 + 0.38 * abs(((x % 16) - 8) / 8)
        curt.rect(x, 0, x + 1, 64, shade((150, 28, 34), f))
    curt.noise(4, 37)
    out["textures/AJCURT.png"] = curt.png()
    boards = Img(64, 64, (150, 112, 72))
    boards.noise(7, 38)
    for y in range(0, 64, 16):
        boards.rect(0, y, 64, y + 1, (96, 70, 44))
    out["flats/AJBOARD.png"] = boards.png()

    floor = Img(64, 64, (120, 118, 122))
    floor.noise(8, 12)
    floor.frame(0, 0, 64, 64, (92, 90, 94), 1)
    out["flats/AJFLOOR.png"] = floor.png()

    ceil = Img(64, 64, (150, 150, 150))
    ceil.noise(4, 13)
    ceil.frame(0, 0, 64, 64, (128, 128, 128), 1)
    ceil.rect(24, 24, 40, 40, (250, 250, 240))
    out["flats/AJCEIL.png"] = ceil.png()

    pit = Img(64, 64, (58, 54, 60))
    pit.noise(10, 14)
    out["flats/AJPIT.png"] = pit.png()

    trim = Img(64, 64, (70, 74, 82))
    trim.noise(5, 15)
    for y in range(0, 64, 16):
        trim.rect(0, y, 64, y + 1, (40, 42, 48))
        trim.rect(0, y + 1, 64, y + 2, (104, 108, 118))
    out["textures/AJTRIM.png"] = trim.png()
    out["flats/AJTRIMF.png"] = trim.png()

    # empty frame: a dark blank recess with two hinge plates waiting for a door
    fr = Img(64, 96, (44, 42, 46))
    fr.noise(5, 16)
    fr.frame(0, 0, 64, 96, (24, 22, 26), 2)
    for y in (14, 70):
        fr.rect(2, y, 8, y + 12, (190, 170, 110))
        fr.rect(3, y + 2, 5, y + 4, (60, 50, 30))
        fr.rect(3, y + 8, 5, y + 10, (60, 50, 30))
    out["textures/AJFRAME.png"] = fr.png()

    ex = Img(64, 160, (40, 44, 40))          # as tall as the exit room wall
    ex.frame(0, 0, 64, 160, (20, 22, 20), 3)
    ex.rect(12, 62, 52, 98, (70, 230, 90))
    ex.rect(20, 78, 36, 82, (20, 40, 20))    # arrow pointing right
    for i in range(10):
        ex.rect(34 + i, 71 + i, 35 + i, 90 - i, (20, 40, 20))
    out["textures/AJEXIT.png"] = ex.png()

    # thief: a small hooded figure. A/B walking, C picking a hinge, D dead,
    # E/F walking with a door on its back.
    cloak, dark, face, slab = (92, 70, 48), (48, 36, 26), (236, 226, 200), (200, 180, 140)
    for fr_name in "ABCDEF":
        th = Img(36, 52, (0, 0, 0, 0))
        if fr_name == "D":
            th.rect(4, 42, 32, 52, cloak)
            th.frame(4, 42, 32, 52, dark, 2)
        else:
            if fr_name in "EF":                                  # the stolen door
                th.rect(2, 0, 26, 44, slab)
                th.frame(2, 0, 26, 44, dark, 2)
                th.disc(21, 24, 2, dark)
            th.rect(10, 16, 28, 44, cloak)
            th.frame(10, 16, 28, 44, dark, 2)
            th.disc(19, 12, 8, cloak)                            # hood
            th.rect(15, 10, 24, 15, face)
            th.rect(16, 11, 18, 13, dark)
            th.rect(21, 11, 23, 13, dark)
            step = 0 if fr_name in "AE" else 4
            th.rect(11 + step, 44, 17 + step, 52, dark)          # legs
            th.rect(22 - step, 44, 28 - step, 52, dark)
            if fr_name == "C":                                   # arms up at the hinge
                th.rect(28, 6, 32, 24, cloak)
                th.rect(28, 4, 34, 8, face)
        out[f"sprites/AJTH{fr_name}0.png"] = th.png(grab=(18, 52))

    # nailer: a broad figure in grey overalls with a hammer. A/B walking,
    # C hammer raised, D hammer down, E dead.
    suit, dark, skin, steel, wood = (96, 104, 116), (40, 44, 52), (224, 196, 170), (190, 196, 204), (150, 110, 70)
    for fr_name in "ABCDE":
        nl = Img(44, 56, (0, 0, 0, 0))
        if fr_name == "E":
            nl.rect(4, 46, 40, 56, suit)
            nl.frame(4, 46, 40, 56, dark, 2)
        else:
            nl.rect(10, 18, 34, 48, suit)
            nl.frame(10, 18, 34, 48, dark, 2)
            nl.rect(15, 24, 29, 27, dark)                        # bib
            nl.disc(22, 11, 8, skin)
            nl.rect(13, 3, 31, 8, dark)                          # cap
            nl.rect(17, 10, 20, 13, dark)
            nl.rect(24, 10, 27, 13, dark)
            step = 0 if fr_name in "ACD" else 4
            nl.rect(12 + step, 48, 20 + step, 56, dark)
            nl.rect(26 - step, 48, 34 - step, 56, dark)
            if fr_name == "C":                                   # hammer raised
                nl.rect(35, 6, 38, 30, wood)
                nl.rect(31, 2, 43, 9, steel)
            elif fr_name == "D":                                 # hammer down
                nl.rect(34, 30, 37, 46, wood)
                nl.rect(30, 44, 42, 51, steel)
            else:                                                # hammer at its side
                nl.rect(35, 22, 38, 44, wood)
                nl.rect(31, 40, 43, 47, steel)
        out[f"sprites/AJNL{fr_name}0.png"] = nl.png(grab=(22, 56))

    # lodger: made of the same dark as an empty frame, with the frame's two
    # brass hinge plates for eyes. A/B walking, C arm up, D striking, E dead.
    body, edge, brass = (44, 42, 46), (20, 18, 22), (190, 170, 110)
    for fr_name in "ABCDE":
        lg = Img(40, 64, (0, 0, 0, 0))
        if fr_name == "E":
            lg.rect(2, 56, 38, 64, body)
            lg.frame(2, 56, 38, 64, edge, 2)
            lg.rect(8, 58, 14, 61, brass)
        else:
            lg.rect(12, 6, 28, 54, body)                         # a tall narrow slab
            lg.frame(12, 6, 28, 54, edge, 2)
            lg.rect(15, 12, 19, 20, brass)
            lg.rect(21, 12, 25, 20, brass)
            lg.rect(16, 14, 18, 16, edge)
            lg.rect(22, 14, 24, 16, edge)
            step = 0 if fr_name in "ACD" else 3
            lg.rect(13 + step, 54, 18 + step, 64, edge)
            lg.rect(22 - step, 54, 27 - step, 64, edge)
            if fr_name == "C":
                lg.rect(28, 2, 32, 26, body)
                lg.rect(28, 0, 36, 5, brass)
            elif fr_name == "D":
                lg.rect(28, 24, 40, 28, body)
                lg.rect(35, 22, 40, 31, brass)
            else:
                lg.rect(28, 22, 32, 46, body)
            lg.rect(8, 22, 12, 46, body)
        out[f"sprites/AJLG{fr_name}0.png"] = lg.png(grab=(20, 64))

    for c in DOOR_COLOURS:
        d = door(c)
        out[f"textures/AJDR{c}.png"] = d.png()
        out[f"sprites/AJD{c}A0.png"] = d.png(grab=(32, 96))
        # the same door nailed to its frame: two planks across it
        for y0 in (22, 62):
            for i in range(64):
                y = y0 + i // 6
                d.rect(i, y, i + 1, y + 7, (150, 110, 70))
                d.set(i, y, (90, 64, 40))
                d.set(i, y + 6, (90, 64, 40))
            for x in (5, 58):
                d.disc(x, y0 + x // 6 + 3, 1, (220, 220, 225))
        out[f"sprites/AJN{c}A0.png"] = d.png(grab=(32, 96))
        t = Img(64, 64, shade(DOOR_COLOURS[c], 0.7))
        t.noise(5, 20 + c)
        for y in range(0, 64, 16):
            t.rect(0, y, 64, y + 1, shade(DOOR_COLOURS[c], 0.4))
        out[f"textures/AJTR{c}.png"] = t.png()
        out[f"flats/AJTF{c}.png"] = t.png()
    return out
