"""Candidate looks for MAP02, the hotel (see AJAR_HOTEL in map_hinges2.py).

Three whole-hotel looks, numbered 1 to 3. For look n:
  AJ2L<n>  lobby wall, 336 from skirting to cornice; AJ2M<n> its 224 cut for the balcony
  AJ2H<n>  hall and dining room wall, 128      AJ2U<n>  the same, 112 (upstairs)
  AJ2W<n>  guest room wall, 112                AJ2T<n>  bathroom wall, 112
  AJ2F<n>  floor of lobby, halls and dining    AJ2R<n>  runner
  AJ2C<n>  bedroom carpet                      AJ2B<n>  bathroom floor
  AJ2Q<n>  quilt   AJ2S<n>  sofa               AJ2E<n>  tub and basin sides
  AJ2D<n>, AJ2K<n><keys>  room doors           AJ2P<n><c>  lobby picture of door c
  AJ2X<n>  front doors   AJ2Y<n>  key rack     AJ2X<n>N  the front doors when new (MAP22 THEN)
The back of the house is the same in all three: AJ2KW/AJ2KF kitchen,
AJ2AW attic. Walls repeat every 32 across, as walls are cut at multiples of 32.
"""
import random

from gfx import Img, shade, digit, hang_picture, BRASS, LOCKS, DOOR_COLOURS

# name, and for each surface its colours
LOOKS = {
    # an old grand hotel: bottle green panelling, cream paper, crimson carpet
    "1": dict(upper=(226, 216, 190), mark=(204, 190, 158), dado=(38, 74, 58), rail=(196, 160, 84),
              skirt=(24, 44, 36), room=(228, 214, 196), roommark=(196, 150, 140), roomdado=(96, 62, 44),
              floor=((226, 220, 204), (52, 52, 58)), runner=((142, 34, 42), (206, 170, 92)),
              carpet=(120, 40, 46), quilt=(40, 84, 66), sofa=(40, 84, 66),
              tile=(236, 236, 228), band=(38, 96, 72), bath=((232, 232, 224), (38, 74, 58))),
    # a seaside hotel out of season: washed aqua, white boards, coral
    "2": dict(upper=(168, 204, 200), mark=(150, 190, 188), dado=(232, 230, 220), rail=(244, 242, 234),
              skirt=(200, 198, 188), room=(236, 228, 208), roommark=(160, 198, 196), roomdado=(232, 230, 220),
              floor=((196, 172, 132), (170, 146, 108)), runner=((214, 110, 90), (244, 232, 208)),
              carpet=(190, 170, 136), quilt=(214, 110, 90), sofa=(92, 150, 152),
              tile=(238, 240, 238), band=(110, 176, 176), bath=((236, 238, 236), (120, 180, 180))),
    # a deco hotel at night: teal lacquer, black and gold
    "3": dict(upper=(26, 84, 92), mark=(204, 168, 84), dado=(22, 22, 28), rail=(204, 168, 84),
              skirt=(10, 10, 14), room=(190, 150, 70), roommark=(140, 104, 40), roomdado=(58, 38, 28),
              floor=((70, 48, 34), (46, 32, 24)), runner=((22, 70, 78), (204, 168, 84)),
              carpet=(24, 66, 72), quilt=(22, 22, 28), sofa=(150, 110, 40),
              tile=(28, 28, 34), band=(204, 168, 84), bath=((232, 228, 214), (24, 24, 30))),
}


def wall(look, h, kind):
    """A wall `h` high from skirting to cornice. kind: lobby, hall or room."""
    c = LOOKS[look]
    base = c["room"] if kind == "room" else c["upper"]
    mark = c["roommark"] if kind == "room" else c["mark"]
    dado = c["roomdado"] if kind == "room" else c["dado"]
    dh = 64 if kind == "lobby" else 36 if kind == "hall" else 28
    im = Img(64, h, base)
    top = h - dh
    # the paper or paint above the dado
    if look == "1":
        if kind == "room":                                       # narrow stripes
            for x in range(0, 64, 8):
                im.rect(x, 0, x + 2, top, mark)
        else:                                                    # damask
            for cy in range(8, top, 16):
                for cx in range(0, 65, 16):
                    x = cx + (8 if (cy // 16) % 2 else 0)
                    im.diamond(x, cy, 5, mark)
                    im.diamond(x, cy, 2, base)
    elif look == "2":
        if kind == "room":                                       # wide deckchair stripes
            for x in range(0, 64, 16):
                im.rect(x, 0, x + 8, top, mark)
        else:                                                    # painted boards
            for y in range(0, top, 24):
                im.rect(0, y, 64, y + 1, mark)
    else:
        if kind == "room":                                       # scallops
            for cy in range(0, top + 16, 16):
                for cx in range(0, 65, 16):
                    x = cx + (8 if (cy // 16) % 2 else 0)
                    im.disc(x, cy, 8, mark)
                    im.disc(x, cy, 6, base)
            im.rect(0, top, 64, h, base)
        else:                                                    # gold pinstripes, stepped at the top
            for x in (0, 32):
                im.rect(x + 15, 12, x + 17, top, mark)
                im.rect(x + 9, 20, x + 10, top, shade(mark, 0.8))
                im.rect(x + 22, 20, x + 23, top, shade(mark, 0.8))
    im.rect(0, top, 64, h, dado)
    im.noise(4, 200 + int(look) * 10 + len(kind))
    # cornice, and in the lobby a frieze under it
    im.rect(0, 0, 64, 5, shade(base, 0.78))
    im.rect(0, 5, 64, 7, c["rail"])
    if kind == "lobby":
        im.rect(0, 7, 64, 40, shade(dado, 1.0))
        im.rect(0, 40, 64, 43, c["rail"])
        for x in (0, 32):
            im.frame(x + 4, 12, x + 28, 35, shade(c["rail"], 0.8), 1)
    # the dado: beadboard by the sea, panels elsewhere
    if look == "2":
        for x in range(0, 64, 8):
            im.rect(x, top, x + 1, h, shade(dado, 0.8))
    else:
        for x in (0, 32):
            im.frame(x + 4, top + 7, x + 28, h - 12, shade(dado, 0.66), 2)
            im.rect(x + 6, h - 14, x + 28, h - 13, shade(dado, 1.5))
    im.rect(0, top - 4, 64, top, c["rail"])
    im.rect(0, top, 64, top + 1, shade(c["rail"], 0.55))
    im.rect(0, h - 8, 64, h, c["skirt"])
    im.rect(0, h - 8, 64, h - 7, shade(c["skirt"], 1.5))
    return im


def tiled(src, w, h):
    im = Img(w, h)
    for y in range(h):
        for x in range(w):
            im.set(x, y, src.px[(y % src.h) * src.w + x % src.w])
    return im


def make(out, rd, front, keyrack):
    """`rd` is the plain room door (leaf in its bottom 96 rows); `front` and
    `keyrack` draw the front doors and the key rack on a strip of lobby wall."""
    def both(name, im):
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    for n, c in LOOKS.items():
        lobby, hall = wall(n, 336, "lobby"), wall(n, 128, "hall")
        out[f"textures/AJ2L{n}.png"] = lobby.png()
        out[f"textures/AJ2H{n}.png"] = hall.png()
        out[f"textures/AJ2M{n}.png"] = wall(n, 224, "lobby").png()
        out[f"textures/AJ2U{n}.png"] = wall(n, 112, "hall").png()
        out[f"textures/AJ2W{n}.png"] = wall(n, 112, "room").png()

        # floors
        a, b = c["floor"]
        f = Img(64, 64, a)
        if n == "1":                                             # marble chequer
            for i in range(2):
                for j in range(2):
                    if (i + j) % 2:
                        f.rect(i * 32, j * 32, i * 32 + 32, j * 32 + 32, b)
        elif n == "2":                                           # bleached boards
            for y in range(0, 64, 16):
                f.rect(0, y, 64, y + 1, b)
                f.rect((y * 3) % 64, y, (y * 3) % 64 + 1, y + 16, b)
        else:                                                    # walnut blocks, brass studs
            for i in range(4):
                for j in range(4):
                    if (i + j) % 2:
                        f.rect(i * 16, j * 16, i * 16 + 16, j * 16 + 16, b)
            for x in (0, 32):
                for y in (0, 32):
                    f.disc(x, y, 1, c["rail"])
        f.noise(5, 300 + int(n))
        out[f"flats/AJ2F{n}.png"] = f.png()
        ra, rb = c["runner"]
        r = Img(64, 64, ra)
        r.noise(5, 310 + int(n))
        for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64), (32, 32)):
            r.diamond(cx, cy, 7, rb)
            r.diamond(cx, cy, 5, ra)
        out[f"flats/AJ2R{n}.png"] = r.png()
        cp = Img(64, 64, c["carpet"])
        cp.noise(7, 320 + int(n))
        for x in range(8, 64, 16):
            for y in range(8, 64, 16):
                cp.set(x, y, shade(c["carpet"], 1.5))
        out[f"flats/AJ2C{n}.png"] = cp.png()

        # the bathroom: tiled walls with a band at hand height, small chequer floor
        t = Img(64, 112, c["tile"])
        t.noise(3, 330 + int(n))
        for i in range(0, 64, 16):
            t.rect(i, 0, i + 1, 112, shade(c["tile"], 0.74))
        for y in range(0, 112, 16):
            t.rect(0, y, 64, y + 1, shade(c["tile"], 0.74))
        t.rect(0, 64, 64, 72, c["band"])
        t.rect(0, 64, 64, 65, shade(c["band"], 0.6))
        out[f"textures/AJ2T{n}.png"] = t.png()
        e = Img(64, 64, c["tile"])
        e.noise(3, 335 + int(n))
        for i in range(0, 64, 16):
            e.rect(i, 0, i + 1, 64, shade(c["tile"], 0.74))
            e.rect(0, i, 64, i + 1, shade(c["tile"], 0.74))
        both(f"AJ2E{n}", e)
        ba, bb = c["bath"]
        bf = Img(64, 64, ba)
        for i in range(8):
            for j in range(8):
                if (i + j) % 2:
                    bf.rect(i * 8, j * 8, i * 8 + 8, j * 8 + 8, bb)
        bf.noise(4, 340 + int(n))
        out[f"flats/AJ2B{n}.png"] = bf.png()

        # bedding and upholstery
        q = Img(64, 64, c["quilt"])
        q.noise(5, 350 + int(n))
        for cx in range(0, 65, 16):
            for cy in range(0, 65, 16):
                q.diamond(cx, cy, 5, shade(c["quilt"], 1.3))
                q.diamond(cx, cy, 2, c["rail"])
        both(f"AJ2Q{n}", q)
        s = Img(64, 64, c["sofa"])
        s.noise(6, 360 + int(n))
        for cx in range(8, 64, 16):
            for cy in range(8, 64, 16):
                s.disc(cx, cy, 1, shade(c["sofa"], 0.55))
        both(f"AJ2S{n}", s)

        # room doors: the same leaf under a deep wooden architrave (16), so
        # that a 112 room sees only wood above its door; a 128 hall sees its
        # own wall above that
        T = rd.h - 128
        base = tiled(hall, 64, rd.h)
        for y in range(rd.h):
            for x in range(64):
                base.set(x, y, hall.px[((y - T) % 128) * 64 + x])
        for y in range(T + 32, rd.h):
            for x in range(64):
                base.px[y * 64 + x] = list(rd.px[y * 64 + x])
        wood = (104, 72, 44) if n != "2" else (236, 234, 226)
        base.rect(0, T + 16, 64, T + 32, wood)
        base.rect(0, T + 16, 64, T + 17, shade(wood, 1.3))
        base.rect(0, T + 30, 64, T + 32, shade(wood, 0.6))
        out[f"textures/AJ2D{n}.png"] = base.png()
        for keys in LOCKS:
            lk = Img(64, rd.h)
            lk.px = [list(p) for p in base.px]
            for i, ch in enumerate(keys):
                x = 32 - 9 * len(keys) + 18 * i + 1
                lk.rect(x, T + 62, x + 16, T + 82, BRASS)
                lk.frame(x, T + 62, x + 16, T + 82, (110, 88, 36), 1)
                digit(lk, ch, x + 5, T + 65, (60, 40, 16))
                lk.rect(x + 7, T + 77, x + 9, T + 80, (30, 22, 10))
            out[f"textures/AJ2K{n}{keys}.png"] = lk.png()

        # the lobby's pictures, front doors and key rack on its own wall
        for col, rgb in DOOR_COLOURS.items():
            pic = tiled(lobby, 64, 336)
            hang_picture(pic, 336, rgb)
            out[f"textures/AJ2P{n}{col}.png"] = pic.png()
        fd = tiled(lobby, 128, 336)
        front(fd)
        out[f"textures/AJ2X{n}.png"] = fd.png()
        fd = tiled(lobby, 128, 336)
        front(fd, new=True)
        out[f"textures/AJ2X{n}N.png"] = fd.png()
        kr = tiled(lobby, 160, 336)
        keyrack(kr)
        out[f"textures/AJ2Y{n}.png"] = kr.png()

    # the back of the house, the same whatever the front looks like.
    # Kitchen: white tile to the ceiling over a dark band, red quarry floor
    kw = Img(64, 128, (232, 232, 224))
    kw.noise(3, 370)
    for i in range(0, 64, 16):
        kw.rect(i, 0, i + 1, 128, (176, 176, 168))
    for y in range(0, 128, 16):
        kw.rect(0, y, 64, y + 1, (176, 176, 168))
    kw.rect(0, 112, 64, 128, (52, 56, 60))
    kw.rect(0, 80, 64, 82, (52, 56, 60))
    out["textures/AJ2KW.png"] = kw.png()
    kf = Img(64, 64, (150, 70, 52))
    kf.noise(7, 371)
    for i in range(0, 64, 16):
        kf.rect(i, 0, i + 1, 64, (92, 44, 34))
        kf.rect(0, i, 64, i + 1, (92, 44, 34))
    out["flats/AJ2KF.png"] = kf.png()
    # Attic: bare boards on studs, nothing papered
    aw = Img(64, 128, (150, 118, 82))
    rnd = random.Random(372)
    for y in range(0, 128, 16):
        f = rnd.choice((0.9, 1.0, 1.08))
        aw.rect(0, y, 64, y + 16, shade((150, 118, 82), f))
        aw.rect(0, y, 64, y + 1, (84, 62, 40))
    for x in (0, 32):
        aw.rect(x, 0, x + 4, 128, (104, 78, 52))
        aw.rect(x + 4, 0, x + 5, 128, (70, 52, 34))
    aw.noise(6, 373)
    out["textures/AJ2AW.png"] = aw.png()
