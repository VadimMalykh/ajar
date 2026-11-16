"""Procedural placeholder art, written as PNG with no dependencies."""
import os
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
                4: (215, 170, 40), 5: (150, 80, 200), 6: (240, 120, 180)}


STRAY = 7           # the Stray door: every colour at once, and no far side of its own
STRAY_GREY = (120, 120, 130)


def stray_door():
    """The Stray door's leaf: slanting bands of all six colours and a question mark."""
    im = Img(64, 96)
    for y in range(96):
        for x in range(64):
            im.set(x, y, DOOR_COLOURS[1 + ((x + y) // 12) % 6])
    im.frame(0, 0, 64, 96, (40, 40, 48), 3)
    for y1, y2 in ((8, 44), (52, 88)):
        im.frame(9, y1, 55, y2, (40, 40, 48), 2)
    im.noise(6, 7)
    im.disc(53, 49, 3, (235, 215, 140))
    white = (245, 245, 235)
    im.rect(24, 15, 40, 19, white)                # ?
    im.rect(36, 19, 40, 27, white)
    im.rect(30, 25, 40, 29, white)
    im.rect(30, 29, 34, 33, white)
    im.rect(30, 35, 34, 39, white)
    return im


def door(colour):
    """64x96 door leaf: two panels, a knob and a glyph that names the far side."""
    if colour == STRAY:
        return stray_door()
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
    elif colour == 5:
        im.rect(29, 15, 35, 37, white)
        im.rect(21, 23, 43, 29, white)
    else:
        im.disc(32, 26, 10, white)
        im.disc(32, 26, 5, shade(base, 0.8))
    return im


DIGITS = {"1": ("010", "110", "010", "010", "111"), "2": ("111", "001", "111", "100", "111"),
          "3": ("111", "001", "111", "001", "111"), "4": ("101", "101", "111", "001", "001")}
DIGITS.update({
    "N": ("10001", "11001", "10101", "10011", "10001"), "O": ("01110", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "01010", "00100"), "A": ("01110", "10001", "11111", "10001", "10001"),
    "C": ("01111", "10000", "10000", "10000", "01111"), "Y": ("10001", "01010", "00100", "00100", "00100"),
    "R": ("11110", "10001", "11110", "10010", "10001"), "E": ("11111", "10000", "11110", "10000", "11111"),
    "P": ("11110", "10001", "11110", "10000", "10000"), "T": ("11111", "00100", "00100", "00100", "00100"),
    "I": ("11111", "00100", "00100", "00100", "11111"), " ": ("00000",) * 5})
BRASS = (206, 180, 96)
LOCKS = ("1", "2", "3", "4", "12", "23", "34")     # which keys a locked room door can ask for


def digit(im, ch, x, y, c, s=2):
    """Draws a 3x5 digit, each dot s pixels, with its top left at x, y."""
    for j, row in enumerate(DIGITS[ch]):
        for i, on in enumerate(row):
            if on == "1":
                im.rect(x + i * s, y + j * s, x + i * s + s, y + j * s + s, c)


def text(im, s, x, y, c, scale=2):
    """Writes capitals (those in DIGITS) with a 5x5 face, top left at x, y."""
    for n, ch in enumerate(s):
        digit(im, ch, x + n * 6 * scale, y, c, scale)


def furniture(out, wall):
    """Hotel furniture: beds, baths, windows, the lobby's desk and front doors."""
    def both(name, im):                       # usable on walls and on floors
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    quilt = Img(64, 64, (124, 44, 52))
    quilt.noise(5, 51)
    for cx in range(0, 65, 16):
        for cy in range(0, 65, 16):
            quilt.diamond(cx, cy, 5, (150, 66, 70))
            quilt.diamond(cx, cy, 2, (214, 190, 150))
    both("AJQUILT", quilt)
    pillow = Img(64, 64, (238, 234, 224))
    pillow.noise(4, 52)
    both("AJPILLOW", pillow)
    wood = Img(64, 64, (122, 86, 54))
    for x in range(4, 64, 9):
        wood.rect(x, 0, x + 1, 64, (104, 72, 44))
    wood.noise(5, 53)
    wood.rect(0, 0, 64, 2, (84, 58, 34))
    both("AJWOOD", wood)
    tile = Img(64, 64, (232, 236, 238))
    tile.noise(3, 54)
    for i in range(0, 64, 16):
        tile.rect(i, 0, i + 1, 64, (168, 176, 182))
        tile.rect(0, i, 64, i + 1, (168, 176, 182))
    both("AJTILE", tile)
    chk = Img(64, 64, (226, 230, 232))
    for i in range(4):
        for j in range(4):
            if (i + j) % 2:
                chk.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, (120, 150, 170))
    chk.noise(4, 55)
    both("AJTILEF", chk)
    water = Img(64, 64, (70, 130, 190))
    water.noise(8, 56)
    for y in range(4, 64, 16):
        for x in range(64):
            water.set(x, y + (x // 8) % 2, (150, 196, 230))
    both("AJWATER", water)
    sink = Img(64, 64, (240, 240, 238))
    sink.noise(3, 57)
    sink.frame(0, 0, 64, 64, (170, 176, 182), 3)
    sink.disc(32, 32, 22, (206, 214, 220))
    sink.disc(32, 32, 4, (60, 64, 70))
    both("AJSINK", sink)
    sofa = Img(64, 64, (146, 54, 50))
    sofa.noise(6, 58)
    for cx in range(8, 64, 16):
        for cy in range(8, 64, 16):
            sofa.disc(cx, cy, 1, (88, 28, 28))
    both("AJSOFA", sofa)
    cloth = Img(64, 64, (236, 232, 222))
    cloth.noise(4, 59)
    cloth.frame(0, 0, 64, 64, (206, 190, 150), 2)
    both("AJCLOTH", cloth)
    steel = Img(64, 64, (176, 182, 190))
    steel.noise(4, 60)
    for y in range(0, 64, 32):
        steel.rect(0, y, 64, y + 1, (120, 126, 134))
    both("AJSTEEL", steel)

    # window: glazing bars only, the panes are see-through (ajarmap.window)
    win = Img(64, 56, (0, 0, 0, 0))
    pale = (232, 228, 214)
    win.frame(0, 0, 64, 56, pale, 4)
    win.rect(30, 0, 34, 56, pale)
    win.rect(0, 26, 64, 30, pale)
    win.frame(0, 0, 64, 56, (150, 146, 136), 1)
    out["textures/AJWIN.png"] = win.png()

    def strip(w, tall):
        im = Img(w, tall)
        for y in range(tall):
            for x in range(w):
                im.set(x, y, wall.px[(y % 128) * 128 + x % 128])
        return im

    # the hotel's front doors, on a strip of lobby wall (128 by 336): boarded
    # up from outside, under a lit sign
    def front(fd):
        fd.rect(2, 180, 126, 204, (26, 22, 22))
        fd.frame(2, 180, 126, 204, BRASS, 1)
        text(fd, "NO VACANCY", 5, 187, (255, 74, 50))
        dark = (72, 50, 32)
        fd.rect(10, 212, 118, 336, dark)
        for x1 in (16, 66):
            fd.rect(x1, 218, x1 + 46, 336, (104, 74, 46))
            fd.rect(x1 + 6, 226, x1 + 40, 300, (44, 56, 76))             # glass, dark outside
            fd.rect(x1 + 9, 229, x1 + 14, 297, (86, 104, 128))
            fd.frame(x1 + 6, 226, x1 + 40, 300, dark, 2)
            fd.rect(x1 + 6, 308, x1 + 40, 330, (90, 62, 38))
        fd.rect(60, 262, 68, 274, BRASS)                                 # handles
        for y0 in (238, 282):                                            # two planks across
            for i in range(108):
                y = y0 + i // 9
                fd.rect(10 + i, y, 11 + i, y + 9, (160, 120, 78))
                fd.set(10 + i, y, (92, 66, 40))
                fd.set(10 + i, y + 8, (92, 66, 40))
            for x in (14, 113):
                fd.disc(x, y0 + (x - 10) // 9 + 4, 1, (226, 226, 230))

    fd = strip(128, 336)
    front(fd)
    out["textures/AJFRONT.png"] = fd.png()

    # the key rack behind the reception desk, on a strip of lobby wall (160
    # by 336): the 72 rows between the counter top (40) and the balcony
    # floor (112)
    def keyrack(kr):
        kr.rect(0, 224, 160, 296, (86, 60, 38))
        kr.frame(0, 224, 160, 296, (56, 38, 22), 2)
        text(kr, "RECEPTION", 27, 229, BRASS)
        rnd = random.Random(7)
        for i in range(9):
            for j in range(3):
                x, y = 9 + i * 16, 244 + j * 16
                kr.rect(x, y, x + 14, y + 14, (40, 28, 18))
                if rnd.random() < 0.3:                                   # a key left on its hook
                    kr.rect(x + 6, y + 2, x + 8, y + 8, BRASS)
                    kr.rect(x + 4, y + 8, x + 10, y + 12, (236, 228, 204))
                else:
                    kr.set(x + 7, y + 3, BRASS)

    kr = strip(160, 336)
    keyrack(kr)
    out["textures/AJKEYS.png"] = kr.png()
    return front, keyrack


def hang_picture(pic, tall, base):
    """A framed picture of a door of colour `base`, 48 to 124 above the floor
    of a 64-wide wall strip `tall` high."""
    top = tall - 124
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


def hall_walls(out):
    """Candidate wall treatments for MAP01's hall (see AJAR_HALL in
    map_hinges1.py): AJHW<n> is a full-height wall, 336 from skirting to
    cornice; AJHF<n> its lowest 160 as the front of the gallery; AJHP<n><c>
    the wall with a picture of door c on it; AJHS<n> and AJHT<n><c> the same
    two for the gallery, where the wall is 176 high. Everything repeats every 32
    across, because walls are cut at multiples of 32."""
    H = 336
    CREAM, GOLD = (226, 214, 190), (200, 164, 84)

    def band(im, h1, h2, c):
        im.rect(0, H - h2, 64, H - h1, c)

    def rail(im, h1, h2, c):
        band(im, h1, h2, c)
        band(im, h2 - 1, h2, shade(c, 1.35))
        band(im, h1, h1 + 1, shade(c, 0.6))

    def panels(im, h1, h2, c, inset=4):
        """Sunk panels, one per 32 across, between heights h1 and h2."""
        for x in (0, 32):
            x1, x2, y1, y2 = x + inset, x + 32 - inset, H - h2 + inset, H - h1 - inset
            im.rect(x1, y1, x2, y2, shade(c, 0.92))
            im.rect(x1, y1, x2, y1 + 1, shade(c, 0.6))
            im.rect(x1, y1, x1 + 1, y2, shade(c, 0.6))
            im.rect(x1, y2 - 1, x2, y2, shade(c, 1.25))
            im.rect(x2 - 1, y1, x2, y2, shade(c, 1.25))

    def grain(im, h1, h2, c, seed):
        rnd = random.Random(seed)
        for x in range(32):
            if rnd.random() < 0.35:
                f = rnd.choice((0.9, 0.94, 1.06))
                for xx in (x, x + 32):
                    for y in range(H - h2, H - h1):
                        im.set(xx, y, shade(im.px[y * 64 + xx][:3], f))

    walls = {}

    # 1. oxblood stripe over cream panelling
    ox, wood = (132, 46, 42), (72, 46, 32)
    im = Img(64, H, ox)
    for x in range(0, 64, 32):
        im.rect(x + 16, 0, x + 32, H, shade(ox, 0.8))
        im.rect(x, 0, x + 1, H, shade(GOLD, 0.8))
        im.rect(x + 16, 0, x + 17, H, shade(GOLD, 0.8))
    im.noise(5, 201)
    band(im, 10, 48, CREAM)
    panels(im, 10, 48, CREAM)
    rail(im, 48, 55, wood)
    rail(im, 0, 10, wood)
    band(im, 308, H, CREAM)
    for x in range(0, 64, 8):
        im.rect(x, H - 316, x + 5, H - 310, shade(CREAM, 0.72))      # dentils
    rail(im, 304, 308, wood)
    walls[1] = (im, wood)

    # 2. terracotta field, navy dado, cream frieze with a key pattern
    terra, navy = (178, 88, 58), (38, 46, 80)
    im = Img(64, H, terra)
    im.noise(7, 202)
    band(im, 76, 78, shade(terra, 0.62))
    band(im, 262, 264, shade(terra, 0.62))
    band(im, 10, 66, navy)
    for x in (0, 32):
        im.frame(x + 4, H - 60, x + 28, H - 16, GOLD, 1)
    rail(im, 66, 72, CREAM)
    rail(im, 0, 10, (26, 26, 34))
    band(im, 270, H, CREAM)
    for x in range(0, 64, 16):                                       # key pattern
        im.rect(x, H - 300, x + 12, H - 297, terra)
        im.rect(x, H - 300, x + 3, H - 284, terra)
        im.rect(x, H - 287, x + 16, H - 284, terra)
        im.rect(x + 6, H - 293, x + 9, H - 284, terra)
    rail(im, 270, 274, GOLD)
    band(im, 308, 310, navy)
    walls[2] = (im, navy)

    # 3. mustard plaster over bottle-green glazed tile
    must, tile, black = (206, 162, 74), (38, 100, 80), (26, 30, 30)
    im = Img(64, H, must)
    rnd = random.Random(203)
    for _ in range(26):                                              # uneven plaster
        cx, cy, r, f = rnd.randrange(32), rnd.randrange(30, 250), rnd.randrange(5, 14), rnd.choice((0.95, 0.97, 1.04))
        for dx in (-32, 0, 32, 64):
            for y in range(cy - r, cy + r):
                for x in range(cx + dx - r, cx + dx + r):
                    if 0 <= x < 64 and 0 <= y < H and (x - cx - dx) ** 2 + (y - cy) ** 2 < r * r:
                        im.set(x, y, shade(im.px[y * 64 + x][:3], f))
    im.noise(6, 203)
    for h in range(0, 80, 16):
        for i, x in enumerate(range(0, 64, 16)):
            c = shade(tile, 1.0 if (i + h // 16) % 2 else 0.88)
            im.rect(x, H - h - 16, x + 16, H - h, c)
            im.rect(x + 1, H - h - 15, x + 15, H - h - 14, shade(c, 1.45))    # glaze
            im.rect(x + 1, H - h - 15, x + 2, H - h - 1, shade(c, 1.25))
            im.frame(x, H - h - 16, x + 16, H - h, shade(tile, 0.45), 1)
    rail(im, 80, 88, black)
    band(im, 296, H, CREAM)
    rail(im, 292, 297, tile)
    walls[3] = (im, black)

    # 4. teal damask over walnut
    teal, walnut = (36, 94, 102), (108, 68, 42)
    im = Img(64, H, teal)
    lite = shade(teal, 1.5)
    for row, h in enumerate(range(72, 300, 24)):
        for x in ((0, 32, 64) if row % 2 else (16, 48)):
            cy = H - h
            im.diamond(x, cy, 8, lite)
            im.diamond(x, cy, 5, teal)
            im.diamond(x, cy, 2, lite)
            im.diamond(x, cy - 11, 2, lite)
            im.diamond(x, cy + 11, 2, lite)
    im.noise(5, 204)
    band(im, 0, 56, walnut)
    grain(im, 0, 56, walnut, 204)
    panels(im, 10, 50, walnut)
    rail(im, 50, 58, shade(walnut, 0.8))
    rail(im, 0, 10, shade(walnut, 0.65))
    band(im, 300, H, (214, 204, 180))
    rail(im, 296, 302, shade(walnut, 0.8))
    walls[4] = (im, shade(walnut, 0.8))

    # 5. walnut panelling to the picture rail, green frieze
    wal, green = (124, 80, 48), (44, 78, 62)
    im = Img(64, H, wal)
    im.noise(5, 205)
    grain(im, 0, 292, wal, 205)
    panels(im, 10, 106, wal, 5)
    panels(im, 120, 288, wal, 5)
    rail(im, 110, 116, GOLD)
    rail(im, 0, 10, shade(wal, 0.6))
    band(im, 296, H, green)
    for x in range(0, 64, 16):
        im.diamond(x + 8, H - 316, 4, shade(green, 1.5))
    rail(im, 290, 297, shade(wal, 0.7))
    rail(im, 330, H, shade(wal, 0.7))
    walls[5] = (im, shade(wal, 0.7))

    for n, (im, cap) in walls.items():
        out[f"textures/AJHW{n}.png"] = im.png()
        front = Img(64, 160)
        front.px = [list(p) for p in im.px[(H - 160) * 64:]]
        front.rect(0, 0, 64, 8, cap)
        front.rect(0, 0, 64, 1, shade(cap, 1.4))
        front.rect(0, 7, 64, 8, shade(cap, 0.6))
        out[f"textures/AJHF{n}.png"] = front.png()
        for c, base in DOOR_COLOURS.items():
            pic = Img(64, H)
            pic.px = [list(p) for p in im.px]
            hang_picture(pic, H, base)
            out[f"textures/AJHP{n}{c}.png"] = pic.png()
        # the same wall for the gallery, 176 high: the top 76 rows over the bottom 100
        short = Img(64, 176)
        short.px = [list(p) for p in im.px[:76 * 64]] + [list(p) for p in im.px[(H - 100) * 64:]]
        out[f"textures/AJHS{n}.png"] = short.png()
        for c, base in DOOR_COLOURS.items():
            pic = Img(64, 176)
            pic.px = [list(p) for p in short.px]
            hang_picture(pic, 176, base)
            out[f"textures/AJHT{n}{c}.png"] = pic.png()
    return walls


def hall_floors(out):
    """Candidate floors for MAP01's hall (see AJAR_FLOOR in map_hinges1.py):
    flats AJHG<n> for the floor and AJHR<n> for the carpet runner on it.
    Runners have no direction, because they turn corners."""
    CREAM, NAVY, TERRA, GOLD = (226, 216, 196), (38, 46, 80), (178, 88, 58), (200, 164, 84)

    def runner(base, line, dot, seed):
        r = Img(64, 64, base)
        r.noise(5, seed)
        for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64), (32, 32)):
            r.diamond(cx, cy, 15, line)
            r.diamond(cx, cy, 13, base)
            r.diamond(cx, cy, 4, dot)
        return r

    floors = {}

    # 1. marble chequer, cream and charcoal
    im = Img(64, 64)
    rnd = random.Random(401)
    for by in (0, 32):
        for bx in (0, 32):
            c = CREAM if (bx + by) % 64 == 0 else (54, 54, 62)
            im.rect(bx, by, bx + 32, by + 32, c)
            for _ in range(3):                                       # veins
                x, y = bx + rnd.randrange(32), by + rnd.randrange(32)
                for _ in range(rnd.randrange(8, 22)):
                    if bx <= x < bx + 32 and by <= y < by + 32:
                        im.set(x, y, shade(c, 0.86 if c == CREAM else 1.5))
                    x += rnd.choice((0, 1, 1))
                    y += rnd.choice((-1, 0, 1, 1))
            im.frame(bx, by, bx + 32, by + 32, shade(c, 0.8), 1)
    im.noise(4, 401)
    floors[1] = (im, runner(NAVY, GOLD, GOLD, 411))

    # 2. oak parquet, basket weave
    oak = (154, 106, 62)
    im = Img(64, 64, oak)
    rnd = random.Random(402)
    for by in (0, 32):
        for bx in (0, 32):
            across = (bx + by) % 64 == 0
            for k in range(4):
                c = shade(oak, rnd.choice((0.84, 0.92, 1.0, 1.08)))
                if across:
                    im.rect(bx, by + k * 8, bx + 32, by + k * 8 + 8, c)
                    im.rect(bx, by + k * 8, bx + 32, by + k * 8 + 1, shade(oak, 0.6))
                else:
                    im.rect(bx + k * 8, by, bx + k * 8 + 8, by + 32, c)
                    im.rect(bx + k * 8, by, bx + k * 8 + 1, by + 32, shade(oak, 0.6))
            im.frame(bx, by, bx + 32, by + 32, shade(oak, 0.55), 1)
    im.noise(6, 402)
    floors[2] = (im, runner(NAVY, GOLD, TERRA, 412))

    # 3. encaustic tile: terracotta and navy on cream
    im = Img(64, 64, CREAM)
    for cy in (16, 48):
        for cx in (16, 48):
            im.diamond(cx, cy, 13, (60, 50, 50))
            im.diamond(cx, cy, 12, TERRA)
            im.diamond(cx, cy, 5, CREAM)
            im.diamond(cx, cy, 3, NAVY)
    for cy in (0, 32, 64):
        for cx in (0, 32, 64):
            im.diamond(cx, cy, 7, NAVY)
            im.diamond(cx, cy, 3, GOLD)
    for i in (0, 32):
        im.rect(i, 0, i + 1, 64, (150, 140, 124))
        im.rect(0, i, 64, i + 1, (150, 140, 124))
    im.noise(5, 403)
    plain = Img(64, 64, NAVY)
    plain.noise(6, 413)
    floors[3] = (im, plain)

    # 4. slate flags with pale joints
    slate = (72, 78, 90)
    im = Img(64, 64, slate)
    rnd = random.Random(404)
    for x1, y1, x2, y2 in ((0, 0, 64, 20), (0, 20, 28, 44), (28, 20, 64, 44), (0, 44, 40, 64), (40, 44, 64, 64)):
        c = shade(slate, rnd.choice((0.82, 0.92, 1.0, 1.1)))
        im.rect(x1, y1, x2, y2, c)
        im.frame(x1, y1, x2, y2, (128, 124, 116), 1)
        im.rect(x1 + 1, y1 + 1, x2 - 1, y1 + 2, shade(c, 1.25))
    im.noise(7, 404)
    floors[4] = (im, runner((214, 204, 190), (160, 146, 128), TERRA, 414))

    # 5. cream stone with a navy inlay and gold studs
    stone = (216, 202, 174)
    im = Img(64, 64, stone)
    rnd = random.Random(405)
    for y in range(64):                                              # bedding
        f = rnd.choice((0.96, 0.98, 1.0, 1.0, 1.02))
        for x in range(64):
            im.set(x, y, shade(stone, f))
    im.noise(5, 405)
    im.rect(0, 0, 64, 2, NAVY)
    im.rect(0, 0, 2, 64, NAVY)
    for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64)):
        im.diamond(cx, cy, 7, NAVY)
        im.diamond(cx, cy, 3, GOLD)
    floors[5] = (im, runner(TERRA, GOLD, NAVY, 415))

    for n, (im, rug) in floors.items():
        out[f"flats/AJHG{n}.png"] = im.png()
        out[f"flats/AJHR{n}.png"] = rug.png()


def pit_walls(out, hall):
    """Candidate treatments for MAP01's pit (see AJAR_PIT in map_hinges1.py):
    AJPW<n> is the 192 of wall below the hall floor, darker towards the
    bottom; AJPE<n> the pit's end walls, 544 from pit floor to ceiling, with
    the hall's wall (`hall`, 336) above it; AJPG<n> the floor. Walls repeat
    every 32 across."""
    D = 192

    def falloff(im, lo=0.42):
        for y in range(D):
            f = 1 - (1 - lo) * y / D
            for x in range(64):
                im.set(x, y, shade(im.px[y * 64 + x][:3], f))

    def lip(im, c, t=8):
        im.rect(0, 0, 64, t, c)
        im.rect(0, 0, 64, 1, shade(c, 1.3))
        im.rect(0, t - 2, 64, t, shade(c, 0.55))

    pits = {}

    # 1. cellar: coursed stone, damp at the foot, packed earth
    stone, mortar = (118, 110, 100), (50, 46, 44)
    im = Img(64, D, stone)
    rnd = random.Random(301)
    for row, y in enumerate(range(0, D, 24)):
        for x in ((0, 32) if row % 2 else (16, 48)):
            c = shade(stone, rnd.choice((0.86, 0.94, 1.0, 1.08)))
            for xx in range(x, x + 32):
                im.rect(xx % 64, y, xx % 64 + 1, y + 24, c)
        im.rect(0, y, 64, y + 2, mortar)
        for x in ((0, 32) if row % 2 else (16, 48)):
            im.rect(x, y, x + 2, y + 24, mortar)
    im.noise(9, 301)
    for y in range(D - 44, D):                                       # damp
        for x in range(64):
            r, g, b = im.px[y * 64 + x][:3]
            k = (y - (D - 44)) / 44 * 0.5
            im.set(x, y, (int(r * (1 - k)), int(g * (1 - k * 0.6)), int(b * (1 - k * 0.8))))
    falloff(im)
    lip(im, (156, 150, 142))
    fl = Img(64, 64, (74, 62, 50))
    fl.noise(13, 302)
    for _ in range(9):
        fl.disc(rnd.randrange(4, 60), rnd.randrange(4, 60), rnd.choice((1, 2)), (104, 98, 90))
    pits[1] = (im, fl)

    # 2. furnace: sooty brick glowing from below, an iron grate over embers
    soot, joint = (70, 54, 50), (28, 22, 22)
    im = Img(64, D, soot)
    for row, y in enumerate(range(0, D, 8)):
        im.rect(0, y, 64, y + 1, joint)
        for x in range(0 if row % 2 else 8, 64, 16):
            im.rect(x, y, x + 1, y + 8, joint)
    im.noise(7, 303)
    falloff(im, 0.6)
    for y in range(D - 72, D):                                       # heat
        k = ((y - (D - 72)) / 72) ** 1.6
        for x in range(64):
            r, g, b = im.px[y * 64 + x][:3]
            im.set(x, y, (min(255, int(r + 200 * k)), min(255, int(g + 78 * k)), min(255, int(b + 10 * k))))
    lip(im, (58, 60, 66), 10)
    for x in range(8, 64, 16):
        im.disc(x, 4, 1, (130, 134, 142))                            # rivets
    fl = Img(64, 64, (226, 96, 28))
    rnd = random.Random(304)
    for _ in range(60):
        fl.disc(rnd.randrange(64), rnd.randrange(64), rnd.choice((1, 2, 3)),
                rnd.choice(((255, 190, 70), (180, 50, 20), (120, 30, 16), (255, 140, 40))))
    fl.noise(10, 304)
    for i in range(0, 64, 16):
        fl.rect(i, 0, i + 6, 64, (34, 34, 38))
        fl.rect(i, 0, i + 1, 64, (70, 70, 78))
    for i in range(0, 64, 32):
        fl.rect(0, i, 64, i + 5, (34, 34, 38))
        fl.rect(0, i, 64, i + 1, (70, 70, 78))
    pits[2] = (im, fl)

    # 3. cistern: dark glazed tile with a tide line, still water
    tile = (40, 92, 96)
    im = Img(64, D, tile)
    for h, y in enumerate(range(0, D, 16)):
        for i, x in enumerate(range(0, 64, 16)):
            c = shade(tile, 1.0 if (i + h) % 2 else 0.9)
            im.rect(x, y, x + 16, y + 16, c)
            im.rect(x + 1, y + 1, x + 15, y + 2, shade(c, 1.5))
            im.frame(x, y, x + 16, y + 16, shade(tile, 0.4), 1)
    im.noise(4, 305)
    falloff(im, 0.55)
    tide = D - 58
    for y in range(tide, D):                                         # below the old water line
        for x in range(64):
            r, g, b = im.px[y * 64 + x][:3]
            im.set(x, y, (int(r * 0.6 + 8), int(g * 0.72 + 14), int(b * 0.5)))
    rnd = random.Random(306)
    for x in range(32):                                              # scum at the line, drips below it
        t = rnd.randrange(2, 6)
        d = rnd.randrange(0, 22) if rnd.random() < 0.3 else 0
        for xx in (x, x + 32):
            im.rect(xx, tide - t, xx + 1, tide + 2 + d, (96, 118, 60))
    lip(im, (176, 180, 176))
    fl = Img(64, 64, (22, 58, 66))
    fl.noise(5, 307)
    for _ in range(14):
        x, y, w = rnd.randrange(64), rnd.randrange(64), rnd.randrange(6, 18)
        for xx in range(x, x + w):
            fl.set(xx % 64, y, (70, 124, 128))
    pits[3] = (im, fl)

    # 4. the dig: a broken slab, old brick footings, then raw earth
    im = Img(64, D, (104, 76, 52))
    rnd = random.Random(308)
    for y1, y2, c in ((52, 92, (112, 82, 54)), (92, 118, (86, 66, 50)), (118, 160, (120, 92, 60)), (160, D, (70, 54, 44))):
        for x in range(32):
            w = rnd.randrange(-3, 4)
            for xx in (x, x + 32):
                im.rect(xx, y1 + w, xx + 1, y2 + 4, c)
    im.noise(12, 308)
    for _ in range(16):                                              # stones
        x, y, r = rnd.randrange(32), rnd.randrange(60, D - 4), rnd.choice((1, 2, 2, 3))
        for xx in (x, x + 32):
            im.disc(xx, y, r, (138, 132, 122))
            im.disc(xx, y + 1, max(1, r - 1), (104, 98, 92))
    for x in (7, 22):                                                # roots
        y, xx = 52, x
        stop = 52 + rnd.randrange(50, 110)
        while y < stop:
            for o in (0, 32):
                im.set(xx + o, y, (48, 34, 24))
            y += 1
            xx = max(0, min(31, xx + rnd.choice((-1, 0, 0, 1))))
    brick, bj = (132, 70, 52), (74, 60, 52)
    for row, y in enumerate(range(12, 52, 8)):                       # footings
        im.rect(0, y, 64, y + 8, shade(brick, 0.9 + 0.1 * (row % 2)))
        im.rect(0, y, 64, y + 1, bj)
        for x in range(0 if row % 2 else 8, 64, 16):
            im.rect(x, y, x + 1, y + 8, bj)
    for x in range(32):                                              # ragged lower edge
        if rnd.random() < 0.4:
            for xx in (x, x + 32):
                im.rect(xx, 48, xx + 1, 52, (112, 82, 54))
    falloff(im, 0.5)
    lip(im, (140, 138, 136), 12)
    fl = Img(64, 64, (82, 64, 48))
    fl.noise(14, 309)
    for _ in range(12):
        x, y, r = rnd.randrange(6, 58), rnd.randrange(6, 58), rnd.choice((2, 3, 4))
        fl.disc(x, y, r, (126, 122, 116))
        fl.disc(x + 1, y + 1, r - 1, (96, 92, 88))
    pits[4] = (im, fl)

    for n, (im, fl) in pits.items():
        out[f"textures/AJPW{n}.png"] = im.png()
        out[f"flats/AJPG{n}.png"] = fl.png()
        end = Img(64, 16 + 336 + D)
        end.px = [list(hall.px[x]) for _ in range(16) for x in range(64)] + [list(p) for p in hall.px] + [list(p) for p in im.px]
        out[f"textures/AJPE{n}.png"] = end.png()


def bell(wall, cx, cy, h=None):
    """A copy of the wall `wall` (its top `h` rows) with a small brass bell
    hanging on it at cx, cy: what there is to shoot at where a shot opens a
    secret. It used to be a red and white target, which nobody could miss
    (Vadim, 2026-11-16); a bell wants looking for."""
    im = Img(wall.w, h or wall.h)
    im.px = [list(p) for p in wall.px[:wall.w * im.h]]
    dark, brass, shine = (58, 46, 26), (150, 118, 54), (198, 168, 96)
    im.rect(cx - 1, cy - 9, cx + 1, cy - 5, dark)                    # the bracket it hangs from
    im.rect(cx - 3, cy - 10, cx + 3, cy - 9, dark)
    im.disc(cx, cy - 1, 4, brass)
    im.rect(cx - 4, cy - 1, cx + 5, cy + 3, brass)
    im.rect(cx - 5, cy + 3, cx + 6, cy + 5, brass)                   # the lip
    im.rect(cx - 5, cy + 5, cx + 6, cy + 6, dark)
    im.rect(cx - 2, cy - 3, cx - 1, cy + 2, shine)
    im.disc(cx, cy + 7, 1, dark)                                     # the clapper
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
    pit_walls(out, hall_walls(out)[2][0])
    hall_floors(out)
    front, keyrack = furniture(out, wall)

    # an ordinary hotel-room door (ajarmap.roomdoor): plain wood, no colour, so
    # it cannot be mistaken for one of yours.
    # The leaf is the bottom 96 rows; above it is wall, as far up as any room goes.
    wood = (122, 86, 54)
    T = 128                                                      # rows of wall above the old 128
    rd = Img(64, 128 + T)
    for y in range(128 + T):
        for x in range(64):
            rd.set(x, y, wall.px[(y % 128) * 128 + x])
    rd.rect(0, T + 28, 64, T + 32, (96, 92, 88))                 # lintel
    rd.rect(0, T + 32, 64, T + 128, wood)
    for x in range(4, 64, 9):
        rd.rect(x, T + 32, x + 1, T + 128, shade(wood, 0.86))    # grain
    rd.frame(0, T + 32, 64, T + 128, shade(wood, 0.5), 3)
    for y1, y2 in ((42, 76), (84, 120)):
        rd.frame(10, T + y1, 54, T + y2, shade(wood, 0.62), 2)
    rd.rect(26, T + 50, 38, T + 58, (206, 180, 96))              # brass number plate
    rd.frame(26, T + 50, 38, T + 58, (120, 96, 40), 1)
    rd.disc(53, T + 81, 3, (206, 180, 96))                       # knob
    rd.noise(5, 77)
    out["textures/AJHDOR.png"] = rd.png()
    import gfx_hotel                                             # MAP02's candidate looks
    gfx_hotel.make(out, rd, front, keyrack)
    import gfx_theatre                                           # MAP03's candidate looks
    gfx_theatre.make(out, rd)
    import gfx_yard                                              # MAP04's candidate looks
    gfx_yard.make(out, rd)
    import gfx_station                                           # MAP05's candidate looks
    gfx_station.make(out, rd)
    import gfx_museum                                            # MAP06's candidate looks
    gfx_museum.make(out, rd)
    import gfx_observatory                                       # MAP07's candidate looks
    import map_hinges7                                           # ... and the door faces the map asks for
    gfx_observatory.make(out, rd, map_hinges7.FACES)
    import gfx_store                                             # MAP08's candidate looks
    import map_hinges8
    gfx_store.make(out, rd, map_hinges8.FACES)
    import gfx_things                                            # ... and what stands in its rooms
    gfx_things.make(out)

    # the same door, locked (ajarmap.roomdoor with keys): one brass lock plate
    # per key it needs, each with that key's number, where a hand would be
    for keys in LOCKS:
        lk = Img(64, 128 + T)
        lk.px = [list(p) for p in rd.px]
        for n, ch in enumerate(keys):
            x = 32 - 9 * len(keys) + 18 * n + 1
            lk.rect(x, T + 62, x + 16, T + 82, BRASS)
            lk.frame(x, T + 62, x + 16, T + 82, (110, 88, 36), 1)
            digit(lk, ch, x + 5, T + 65, (60, 40, 16))
            lk.rect(x + 7, T + 77, x + 9, T + 80, (30, 22, 10))  # keyhole
        out[f"textures/AJHK{keys}.png"] = lk.png()

    # a door bolted on its other side (ajarmap.bolted): grey steel, no handle,
    # no plate. It opens by itself once you have come to the side it is bolted on.
    bd = Img(64, 128 + T)
    bd.px = [list(p) for p in rd.px]
    steel = (132, 138, 148)
    bd.rect(0, T + 32, 64, T + 128, steel)
    bd.frame(0, T + 32, 64, T + 128, shade(steel, 0.5), 3)
    for y in (T + 44, T + 78, T + 112):
        bd.rect(3, y, 61, y + 3, shade(steel, 0.7))
        for x in (8, 32, 56):
            bd.disc(x, y + 1, 2, (200, 204, 210))
    bd.noise(5, 78)
    out["textures/AJBOLT.png"] = bd.png()
    # a rolling shutter (ajarmap.shutter): steel slats and a pull at the foot
    sh = Img(64, 128 + T)
    sh.px = [list(p) for p in rd.px]
    sh.rect(0, T + 32, 64, T + 128, steel)
    for y in range(T + 32, T + 128, 8):
        sh.rect(0, y, 64, y + 1, shade(steel, 0.5))
        sh.rect(0, y + 1, 64, y + 2, (176, 182, 192))
    sh.rect(0, T + 120, 64, T + 128, shade(steel, 0.6))
    sh.rect(24, T + 122, 40, T + 126, (200, 204, 210))
    sh.noise(4, 79)
    out["textures/AJSHUT.png"] = sh.png()
    # a brass grille from floor to ceiling (ajarmap.way_home): see-through, tiles
    gr = Img(64, 64, (0, 0, 0, 0))
    for x in range(6, 64, 16):
        gr.rect(x, 0, x + 4, 64, (150, 118, 48))
    gr.rect(0, 30, 64, 34, (176, 140, 60))
    out["textures/AJGRIL.png"] = gr.png()
    # the same as a block of floor that sinks (the stage front)
    bl = Img(64, 128, steel)
    bl.frame(0, 0, 64, 128, shade(steel, 0.5), 3)
    for y in range(10, 120, 12):
        bl.rect(6, y, 58, y + 5, shade(steel, 0.45))
    bl.noise(5, 79)
    out["textures/AJGRATE.png"] = bl.png()

    # room keys, numbered: a brass key on a tag. Sprite, and a HUD icon
    for ch in "1234":
        for name in (f"sprites/AJK{ch}A0.png", f"graphics/AJKI{ch}.png"):
            k = Img(28, 20, (0, 0, 0, 0))
            k.disc(6, 8, 5, BRASS)                               # bow
            k.disc(6, 8, 2, (0, 0, 0, 0))
            k.rect(10, 7, 22, 10, BRASS)                         # stem
            k.rect(18, 10, 20, 14, BRASS)                        # bits
            k.rect(21, 10, 23, 13, BRASS)
            k.rect(13, 3, 27, 19, (236, 228, 204))               # tag
            k.frame(13, 3, 27, 19, (120, 96, 40), 1)
            digit(k, ch, 17, 6, (40, 30, 20))
            out[name] = k.png(grab=(14, 20) if "sprites" in name else None)

    # framed pictures of doors, one per colour, on a strip of that wall as
    # tall as the wall they hang on (A: 336, the hall; B: 176, the gallery)
    for c, base in DOOR_COLOURS.items():
        for tag, tall in (("A", 336), ("B", 176)):
            pic = Img(64, tall)
            for y in range(tall):
                for x in range(64):
                    pic.set(x, y, wall.px[(y % 128) * 128 + x])
            hang_picture(pic, tall, base)
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
    out["textures/AJTARG.png"] = bell(safe, 32, 44).png()            # the bell of a kiosk (MAP05, MAP08, MAP09)

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

    # The way out, the same room in every level (ajarmap.way_out): far sides
    # have a colour, the way out has none. A night room: ink walls and ceiling
    # with gold stars, a dark floor with brass inlay, a gold runner. Walls are
    # 160 high, as the room; AJXA is the brass of its doorway.
    INK, BRASSY = (20, 22, 36), (204, 170, 92)
    night = Img(64, 160, INK)
    night.noise(3, 62)
    rnd = random.Random(62)
    for _ in range(14):                                          # gold stars, two sizes
        x, y, big = rnd.randrange(4, 60), rnd.randrange(6, 146), rnd.random() < 0.3
        night.set(x, y, (255, 226, 140))
        if big:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                night.set(x + dx, y + dy, BRASSY)
    night.rect(0, 150, 64, 152, BRASSY)
    night.rect(0, 152, 64, 160, (8, 8, 14))
    out["textures/AJXW2.png"] = night.png()
    nc = Img(64, 64, INK)
    nc.noise(3, 64)
    for _ in range(7):
        nc.set(rnd.randrange(64), rnd.randrange(64), (255, 226, 140))
    out["flats/AJXC2.png"] = nc.png()
    ng = Img(64, 64, (26, 26, 34))                               # dark polished floor, brass inlay
    ng.noise(4, 65)
    ng.rect(0, 0, 64, 1, BRASSY)
    ng.rect(0, 0, 1, 64, BRASSY)
    for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64)):
        ng.diamond(cx, cy, 4, BRASSY)
    out["flats/AJXG2.png"] = ng.png()
    base = (176, 140, 66)
    r = Img(64, 64, base)
    r.noise(5, 67)
    for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64), (32, 32)):
        r.diamond(cx, cy, 5, INK)
        r.diamond(cx, cy, 3, base)
    out["flats/AJXR2.png"] = r.png()
    xa = Img(64, 64, BRASSY)
    xa.noise(5, 68)
    for y in range(0, 64, 32):
        xa.rect(0, y, 64, y + 2, shade(BRASSY, 0.55))
        xa.rect(0, y + 2, 64, y + 4, shade(BRASSY, 1.25))
    out["textures/AJXA.png"] = xa.png()
    out["flats/AJXAF.png"] = xa.png()

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

    # nailer: the shadow of a hell knight, drawn by the engine from Doom's own
    # sprites (AjarNailer in enemies.zs). Only its eyes are ours: two nail heads.
    head = (232, 236, 244)
    ne = Img(13, 5, (0, 0, 0, 0))
    for cx in (2, 10):
        ne.disc(cx, 2, 2, head)
        ne.set(cx, 2, (120, 124, 134))
    out["sprites/AJNEA0.png"] = ne.png(grab=(6, 3))

    # lodger: the shadow of a revenant, drawn by the engine from Doom's own
    # sprites (AjarLodger in enemies.zs). Only its eyes are ours: the two
    # brass hinge plates of an empty frame.
    brass, screw = (214, 192, 122), (60, 50, 30)
    le = Img(10, 7, (0, 0, 0, 0))
    for x in (0, 7):
        le.rect(x, 0, x + 3, 7, brass)
        le.set(x + 1, 1, screw)
        le.set(x + 1, 5, screw)
    out["sprites/AJLEA0.png"] = le.png(grab=(5, 4))

    # AJAR_LODGER=1..7 adds the AJLG sprites of a look that lost, for the
    # board's photographs (gfx_lodger.py, design/lodger-board.html)
    if os.environ.get("AJAR_LODGER", "0") not in ("", "0"):
        import gfx_lodger
        gfx_lodger.make(out, os.environ["AJAR_LODGER"])

    # MAP05, the terminus: a carriage side (176 high: rail to roof), track
    # ballast with two rails, and the signal box's lever.
    GREENC, CREAM = (38, 78, 58), (226, 214, 180)
    tr = Img(64, 176, GREENC)
    tr.noise(5, 90)
    tr.rect(0, 0, 64, 6, (60, 62, 66))                          # roof edge
    tr.rect(0, 22, 64, 78, CREAM)
    for x in (6, 36):
        tr.rect(x, 28, x + 22, 70, (30, 40, 56))                # windows
        tr.frame(x, 28, x + 22, 70, (120, 96, 50), 2)
    tr.rect(0, 120, 64, 124, (206, 180, 96))
    tr.rect(0, 140, 64, 176, (26, 26, 28))                      # underframe
    for cx in (16, 48):
        tr.disc(cx, 160, 13, (58, 58, 62))
        tr.disc(cx, 160, 4, (120, 120, 126))
    out["textures/AJTRN.png"] = tr.png()
    bl = Img(64, 64, (86, 78, 70))
    bl.noise(14, 91)
    for x in range(0, 64, 16):
        bl.rect(x + 2, 12, x + 12, 52, (70, 52, 36))            # sleepers
    for y in (18, 44):
        bl.rect(0, y, 64, y + 3, (150, 150, 158))
        bl.rect(0, y + 3, 64, y + 4, (60, 60, 66))
    out["flats/AJRAILS.png"] = bl.png()
    lv = Img(64, 128, (58, 62, 60))
    lv.noise(4, 92)
    lv.frame(0, 0, 64, 128, (30, 32, 30), 3)
    lv.rect(10, 86, 54, 96, (24, 24, 24))
    for i, c in enumerate(((200, 60, 50), (215, 170, 40), (60, 170, 80))):
        x = 16 + i * 14
        lv.rect(x, 40, x + 4, 90, (170, 170, 176))
        lv.rect(x - 2, 32, x + 6, 44, c)
    out["textures/AJLEVR.png"] = lv.png()

    for c in list(DOOR_COLOURS) + [STRAY]:
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
        rgb = DOOR_COLOURS.get(c, STRAY_GREY)
        t = Img(64, 64, shade(rgb, 0.7))
        t.noise(5, 20 + c)
        for y in range(0, 64, 16):
            t.rect(0, y, 64, y + 1, shade(rgb, 0.4))
        if c == STRAY:                             # a band of every colour round a place it may open onto
            for i in range(64):
                t.rect(i, 6, i + 1, 10, DOOR_COLOURS[1 + (i // 11) % 6])
        out[f"textures/AJTR{c}.png"] = t.png()
        out[f"flats/AJTF{c}.png"] = t.png()
    return out
