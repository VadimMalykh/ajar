"""Candidate looks for MAP03, the theatre (see AJAR_THEATRE in map_hinges3.py).

Three whole-theatre looks, numbered 1 to 3. For look n:
  AJ3H<n>A..D  auditorium wall from skirting to cornice: A 448 (stalls; 64 more
               rows of pit lining below), B 320 (circle), C 224 (gods), D 160 (bridge)
  AJ3T<n>A..C  the front of a tier, parapet at the top: A 128 (circle), B 224
               (gods), C 288 (bridge; 64 more rows of pit lining below)
  AJ3F<n>  foyer wall, 176     AJ3G<n>  the same, 128     AJ3B<n>  bar wall, 144
  AJ3O<n>  foyer floor         AJ3R<n>  runner            AJ3M<n>  auditorium floor
  AJ3S<n>  seats               AJ3C<n>  auditorium ceiling, AJ3L<n> with lamps
  AJ3E<n>  ceiling of the low rooms                       AJ3K<n>  curtain, 384
  AJ3P<n><c>  foyer picture of door c      AJ3D<n>F, AJ3D<n>F1  front-of-house doors
The back of the house is the same in all three: AJ3XW corridor (128), AJ3XD
dressing room (112), AJ3XS the star's (112), AJ3XG green room (112), AJ3XM a
mirror with bulbs (80; AJ3XN on the star's wall), AJ3XB the booth (112), AJ3XU under the stage, AJ3XL the
flies, AJ3XP back stairs, AJ3XF floor, AJ3XC the dark over the stage, AJ3DXB / AJ3DXB23 doors.
Every wall repeats every 32 or 64 across and is symmetric, and the map lines these
textures up by world position (Map.align), so cuts in a wall do not show.
"""
import random

from gfx import Img, shade, digit, hang_picture, BRASS, LOCKS, DOOR_COLOURS
from gfx_hotel import tiled

GILT = (204, 168, 84)

LOOKS = {
    # an opera house: crimson damask between ivory and gilt
    "1": dict(
        house=dict(field=(128, 30, 38), fstyle="damask", mark=(152, 46, 50), stile=(228, 218, 192),
                   bead=GILT, dado=(226, 216, 190), dstyle="panel", rail=GILT, skirt=(70, 50, 40),
                   frieze=(228, 218, 192), fz="swag", cornice=(232, 224, 200), lining=(60, 34, 30)),
        foyer=dict(field=(232, 224, 200), fstyle="panel", mark=(190, 160, 96), dado=(170, 146, 142),
                   dstyle="marble", rail=GILT, skirt=(60, 48, 44), frieze=(128, 30, 38), fz="stencil",
                   cornice=(236, 228, 206)),
        bar=dict(field=(104, 28, 40), fstyle="stripe", mark=(126, 42, 52), dado=(86, 44, 30),
                 dstyle="panel", rail=GILT, skirt=(40, 24, 18), cornice=(226, 216, 190)),
        tier=((230, 220, 194), "swag"), ofloor=("octagon", (226, 218, 198), (44, 38, 42)),
        runner=((142, 30, 40), GILT), mfloor=("carpet", (92, 24, 32), (150, 110, 60)),
        seat=(160, 32, 42), ceil=("coffer", (222, 212, 186), GILT), low=(226, 218, 200),
        curtain=((150, 26, 36), GILT)),
    # an old playhouse: whitewash, oak posts and panelling, green baize
    "2": dict(
        house=dict(field=(224, 218, 200), fstyle="plaster", mark=(206, 198, 178), stile=(92, 62, 38),
                   bead=(58, 38, 24), dado=(102, 70, 42), dstyle="boards", rail=(70, 46, 28),
                   skirt=(50, 34, 22), frieze=(58, 92, 62), fz="stencil", cornice=(92, 62, 38),
                   lining=(54, 38, 26)),
        foyer=dict(field=(226, 220, 202), fstyle="plaster", mark=(208, 200, 180), dado=(106, 72, 44),
                   dstyle="boards", rail=(70, 46, 28), skirt=(50, 34, 22), frieze=(58, 92, 62),
                   fz="stencil", cornice=(92, 62, 38)),
        bar=dict(field=(116, 80, 48), fstyle="panel", mark=(80, 52, 30), dado=(92, 62, 38),
                 dstyle="boards", rail=(60, 40, 24), skirt=(44, 30, 20), cornice=(70, 46, 28)),
        tier=((112, 76, 46), "baluster"), ofloor=("flag", (152, 146, 134), (108, 102, 94)),
        runner=((64, 98, 66), (200, 160, 80)), mfloor=("boards", (128, 92, 58), (84, 58, 36)),
        seat=(66, 100, 62), ceil=("beam", (214, 206, 186), (84, 56, 34)), low=(214, 206, 186),
        curtain=((38, 84, 60), (200, 160, 80))),
    # a civic theatre of the 1960s: teak slats, concrete, burnt orange
    "3": dict(
        house=dict(field=(150, 98, 58), fstyle="slats", mark=(70, 44, 26), dado=(150, 150, 146),
                   dstyle="concrete", rail=(40, 40, 44), skirt=(36, 36, 40), frieze=(26, 26, 30),
                   fz="void", cornice=(26, 26, 30), lining=(44, 44, 48)),
        foyer=dict(field=(226, 226, 220), fstyle="block", mark=(196, 196, 190), dado=(150, 98, 58),
                   dstyle="boards", rail=(40, 40, 44), skirt=(36, 36, 40), cornice=(40, 40, 44)),
        bar=dict(field=(196, 150, 52), fstyle="tile", mark=(168, 124, 40), dado=(150, 98, 58),
                 dstyle="boards", rail=(40, 40, 44), skirt=(36, 36, 40), cornice=(40, 40, 44)),
        tier=((198, 198, 192), "slab"), ofloor=("terrazzo", (178, 174, 166), (96, 92, 88)),
        runner=((72, 74, 80), (208, 98, 40)), mfloor=("carpet", (52, 54, 60), (78, 80, 88)),
        seat=(208, 98, 40), ceil=("rig", (30, 30, 34), (70, 70, 76)), low=(220, 220, 214),
        curtain=((36, 84, 100), None)),
}


def _wall(s, h, below=0, top=True):
    """32 wide, `h` high from skirting to cornice, `below` more rows of lining
    under the skirting. Without `top` it has no cornice or frieze."""
    im = Img(32, h + below, s["field"])
    dh = 72 if h >= 320 else 56 if h >= 200 else 48 if h >= 160 else 40 if h >= 128 else 32
    co = 10 if top else 0
    fz = (40 if h >= 320 else 24) if top and s.get("frieze") and h >= 160 else 0
    f0, f1 = co + fz, h - dh
    fs, mark = s["fstyle"], s["mark"]
    if fs == "damask":
        for cy in range(f0 + 12, f1, 24):
            im.diamond(16, cy, 6, mark)
            im.diamond(16, cy, 3, s["field"])
            for cx in (0, 32):
                im.diamond(cx, cy + 12, 6, mark)
                im.diamond(cx, cy + 12, 3, s["field"])
    elif fs == "stripe":
        for x in (3, 11, 19, 27):
            im.rect(x, f0, x + 2, f1, mark)
    elif fs == "slats":
        for x in range(0, 32, 8):
            im.rect(x + 3, f0, x + 5, f1, mark)
            im.rect(x + 5, f0, x + 6, f1, shade(s["field"], 1.18))
    elif fs == "plaster":
        rnd = random.Random(h)
        for _ in range((f1 - f0) // 6):
            x, y = rnd.randrange(32), rnd.randrange(f0, max(f0 + 1, f1 - 3))
            im.rect(x, y, min(32, x + rnd.randrange(3, 9)), y + 2, mark)
    elif fs == "panel":
        y = f0 + 8
        while y + 24 < f1:
            y2 = min(y + 88, f1 - 8)
            im.frame(5, y, 27, y2, mark, 1)
            im.frame(7, y + 2, 25, y2 - 2, shade(mark, 1.12), 1)
            y = y2 + 10
    elif fs in ("block", "tile"):
        step = 16 if fs == "block" else 8
        for y in range(f0, f1, step):
            im.rect(0, y, 32, y + 1, mark)
            for x in ((0, 16) if (y // step) % 2 or fs == "tile" else (8, 24)):
                im.rect(x, y, x + 1, min(f1, y + step), mark)
            if fs == "tile":
                im.rect(8, y, 9, min(f1, y + step), mark)
                im.rect(24, y, 25, min(f1, y + step), mark)
    im.field = (f0, f1)
    # the dado, its rail and the skirting
    im.rect(0, f1, 32, h, s["dado"])
    ds = s["dstyle"]
    if ds == "panel":
        im.frame(4, f1 + 7, 28, h - 12, shade(s["dado"], 0.7), 2)
        im.rect(6, h - 14, 28, h - 13, shade(s["dado"], 1.25))
    elif ds == "boards":
        for x in range(0, 32, 8):
            im.rect(x, f1, x + 1, h, shade(s["dado"], 0.72))
            im.rect(x + 1, f1, x + 2, h, shade(s["dado"], 1.12))
    elif ds == "marble":
        rnd = random.Random(h + 7)
        for _ in range(dh // 5):
            x, y = rnd.randrange(32), rnd.randrange(f1, h - 8)
            c = shade(s["dado"], rnd.choice((0.8, 1.2)))
            for i in range(rnd.randrange(4, 10)):
                im.set((x + i) % 32, min(h - 9, y + i // 2), c)
        im.rect(0, f1, 1, h, shade(s["dado"], 0.8))
    elif ds == "concrete":
        for y in range(f1 + 11, h - 8, 12):
            im.rect(0, y, 32, y + 1, shade(s["dado"], 0.88))
        im.rect(0, f1, 1, h, shade(s["dado"], 0.8))
        for y in range(f1 + 18, h - 8, 36):
            im.disc(16, y, 1, shade(s["dado"], 0.6))
    im.rect(0, f1 - 4, 32, f1, s["rail"])
    im.rect(0, f1, 32, f1 + 1, shade(s["rail"], 0.55))
    im.rect(0, h - 8, 32, h, s["skirt"])
    im.rect(0, h - 8, 32, h - 7, shade(s["skirt"], 1.5))
    # frieze and cornice
    if fz:
        im.rect(0, co, 32, f0, s["frieze"])
        mid = co + fz // 2
        if s["fz"] == "swag":
            im.disc(16, mid, fz // 4 + 1, GILT)
            im.disc(16, mid, fz // 4 - 2, s["frieze"])
            for cx in (0, 32):
                im.diamond(cx, mid, fz // 6, GILT)
        elif s["fz"] == "stencil":
            ink = GILT if s["frieze"][0] > 100 else (200, 160, 80)
            im.diamond(16, mid, 5, ink)
            im.diamond(16, mid, 2, s["frieze"])
            for cx in (0, 32):
                im.diamond(cx, mid, 2, ink)
        if s["fz"] != "void":
            im.rect(0, f0 - 3, 32, f0, s["rail"])
    if co:
        im.rect(0, 0, 32, co, s["cornice"])
        im.rect(0, co - 3, 32, co - 2, shade(s["cornice"], 0.7))
        im.rect(0, co - 1, 32, co, s["rail"])
    if below:
        c = s.get("lining", s["skirt"])
        im.rect(0, h, 32, h + below, c)
        for x in range(0, 32, 8):
            im.rect(x, h, x + 1, h + below, shade(c, 0.7))
    return im


def _wall64(s, h, below=0, top=True):
    """The same 64 wide, with a post on every 64 where the look has posts."""
    w = _wall(s, h, below, top)
    im = tiled(w, 64, h + below)
    if s.get("stile"):
        f0, f1 = w.field
        for x1, x2 in ((0, 4), (60, 64)):
            im.rect(x1, f0, x2, f1, s["stile"])
        im.rect(4, f0, 5, f1, s["bead"])
        im.rect(59, f0, 60, f1, s["bead"])
    return im


def wall(s, h, below=0, seed=0):
    im = _wall64(s, h, below)
    im.noise(4, 400 + seed + h)
    return im


def tier(s, t, face, below=0, seed=0):
    """The front of a tier `face` high: a 40-row parapet over the house wall."""
    colour, style = t
    im = Img(32, 40, colour)
    if style == "swag":
        im.rect(0, 0, 32, 5, GILT)
        im.rect(0, 35, 32, 40, GILT)
        im.rect(0, 5, 32, 6, shade(colour, 0.8))
        im.disc(16, 20, 9, GILT)
        im.disc(16, 20, 6, colour)
        im.disc(16, 20, 2, GILT)
        for cx in (0, 32):
            im.diamond(cx, 20, 4, GILT)
    elif style == "baluster":
        im.rect(0, 6, 32, 34, shade(colour, 0.36))
        for x in range(0, 32, 8):
            im.rect(x + 2, 6, x + 6, 34, colour)
            im.rect(x + 1, 16, x + 7, 24, shade(colour, 1.15))
            im.rect(x + 2, 6, x + 3, 34, shade(colour, 0.75))
        im.rect(0, 0, 32, 6, shade(colour, 0.8))
        im.rect(0, 0, 32, 1, shade(colour, 1.3))
        im.rect(0, 34, 32, 40, shade(colour, 0.7))
    else:                                                        # a precast slab with a house light
        im.rect(0, 0, 32, 2, shade(colour, 1.12))
        im.rect(0, 34, 32, 40, shade(colour, 0.6))
        im.rect(0, 0, 1, 40, shade(colour, 0.78))
        for y in range(8, 30, 7):
            im.rect(1, y, 32, y + 1, shade(colour, 0.93))
        im.disc(16, 26, 2, (255, 236, 180))
    out = tiled(im, 64, face + below)
    w = _wall64(s, face - 40, below, top=False)
    for y in range(face - 40 + below):
        f = 0.55 + 0.45 * min(1, y / 14)                         # shadow under the parapet
        for x in range(64):
            out.set(x, y + 40, shade(w.px[y * 64 + x][:3], f))
    out.noise(4, 430 + seed + face)
    return out


def flat(style, a, b, seed):
    f = Img(64, 64, a)
    rnd = random.Random(seed)
    if style == "octagon":                                       # pale tiles, dark cabochons
        for i in range(0, 64, 32):
            f.rect(i, 0, i + 1, 64, shade(a, 0.84))
            f.rect(0, i, 64, i + 1, shade(a, 0.84))
        for cx in (0, 32, 64):
            for cy in (0, 32, 64):
                f.diamond(cx, cy, 5, b)
    elif style == "flag":
        for j, y in enumerate(range(0, 64, 32)):
            f.rect(0, y, 64, y + 2, b)
            for x in ((0, 40) if j else (20, 52)):
                f.rect(x, y, x + 2, y + 32, b)
    elif style == "boards":
        for j, y in enumerate(range(0, 64, 16)):
            f.rect(0, y, 64, y + 16, shade(a, rnd.choice((0.92, 1.0, 1.06))))
            f.rect(0, y, 64, y + 1, b)
            f.rect((j * 24 + 8) % 64, y, (j * 24 + 8) % 64 + 1, y + 16, b)
    elif style == "terrazzo":
        for _ in range(260):
            f.set(rnd.randrange(64), rnd.randrange(64), rnd.choice((b, shade(a, 1.2), (150, 110, 80))))
        f.rect(0, 0, 64, 1, (150, 130, 70))
        f.rect(0, 0, 1, 64, (150, 130, 70))
    elif style == "carpet":
        for cx in range(0, 65, 16):
            for cy in range(0, 65, 16):
                if (cx + cy) // 16 % 2:
                    f.diamond(cx, cy, 2, b)
    f.noise(5, seed)
    return f


def ceiling(kind, a, b, lamp, seed):
    c = Img(64, 64, a)
    if kind == "coffer":
        c.frame(0, 0, 64, 64, shade(a, 0.78), 3)
        c.frame(3, 3, 61, 61, b, 1)
        c.frame(10, 10, 54, 54, shade(a, 0.86), 2)
        c.disc(32, 32, 7, b)
        c.disc(32, 32, 4, a)
    elif kind == "beam":
        c.rect(0, 0, 64, 10, b)
        c.rect(0, 10, 64, 11, shade(b, 0.6))
        c.rect(0, 0, 6, 64, shade(b, 1.1))
        c.rect(6, 11, 7, 64, shade(b, 0.6))
    else:
        c.rect(0, 0, 64, 2, b)
        c.rect(0, 0, 2, 64, b)
        for x in (16, 48):
            for y in (16, 48):
                c.disc(x, y, 1, (200, 190, 160))
    if lamp:
        c.disc(32, 32, 9, (255, 244, 204))
        c.disc(32, 32, 9 - 2, (255, 252, 232))
    c.noise(3, seed)
    return c


def curtain(c, trim):
    im = Img(64, 384, c)
    for x in range(64):
        f = 0.6 + 0.4 * abs(((x % 16) - 8) / 8)
        im.rect(x, 0, x + 1, 384, shade(c, f))
    for x in range(64):                                          # a pelmet with a scalloped edge
        d = 44 + int(6 * (1 - abs(((x % 32) - 16) / 16) ** 2))
        im.rect(x, 0, x + 1, d, shade(c, 0.5 + 0.2 * abs(((x % 8) - 4) / 4)))
        im.rect(x, d, x + 1, d + 3, trim or shade(c, 0.34))
    if trim:
        for x in range(0, 64, 2):
            im.rect(x, 374, x + 1, 384, trim)
            im.rect(x + 1, 374, x + 2, 384, shade(trim, 0.6))
        im.rect(0, 370, 64, 374, trim)
    else:
        im.rect(0, 376, 64, 384, shade(c, 0.42))
    im.noise(4, 470)
    return im


def door(base, rd, wood):
    """A room door for the wall `base` (64 wide, the taller room's): rd's leaf
    in the bottom 96 rows, a 16-row wooden architrave, then that wall above."""
    T = rd.h - 128
    im = Img(64, rd.h)
    for y in range(rd.h):
        for x in range(64):
            im.set(x, y, base.px[((y - (rd.h - base.h)) % base.h) * 64 + x][:3])
    for y in range(T + 32, rd.h):
        for x in range(64):
            im.px[y * 64 + x] = list(rd.px[y * 64 + x])
    im.rect(0, T + 16, 64, T + 32, wood)
    im.rect(0, T + 16, 64, T + 17, shade(wood, 1.3))
    im.rect(0, T + 30, 64, T + 32, shade(wood, 0.6))
    return im


def locked(d, keys):
    T = d.h - 128
    lk = Img(64, d.h)
    lk.px = [list(p) for p in d.px]
    for i, ch in enumerate(keys):
        x = 32 - 9 * len(keys) + 18 * i + 1
        lk.rect(x, T + 62, x + 16, T + 82, BRASS)
        lk.frame(x, T + 62, x + 16, T + 82, (110, 88, 36), 1)
        digit(lk, ch, x + 5, T + 65, (60, 40, 16))
        lk.rect(x + 7, T + 77, x + 9, T + 80, (30, 22, 10))
    return lk


def brick(w, h, c, joint, seed, course=8):
    im = Img(w, h, c)
    rnd = random.Random(seed)
    for j, y in enumerate(range(0, h, course)):
        for x in range(0, w, 16):
            x0 = x + (8 if j % 2 else 0)
            col = shade(c, rnd.choice((0.9, 1.0, 1.0, 1.08)))
            for xx in range(x0, x0 + 16):
                im.rect(xx % w, y, xx % w + 1, y + course, col)
            im.rect(x0 % w, y, x0 % w + 1, y + course, joint)
        im.rect(0, y, w, y + 1, joint)
    return im


def make(out, rd):
    """`rd` is the plain room door (leaf in its bottom 96 rows)."""
    def both(name, im):
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    for n, c in LOOKS.items():
        k = int(n)
        for tag, h, below in (("A", 448, 64), ("B", 320, 0), ("C", 224, 0), ("D", 160, 0)):
            out[f"textures/AJ3H{n}{tag}.png"] = wall(c["house"], h, below, k).png()
        for tag, face, below in (("A", 128, 0), ("B", 224, 0), ("C", 288, 64)):
            out[f"textures/AJ3T{n}{tag}.png"] = tier(c["house"], c["tier"], face, below, k).png()
        foyer = wall(c["foyer"], 176, seed=k + 10)
        out[f"textures/AJ3F{n}.png"] = foyer.png()
        out[f"textures/AJ3G{n}.png"] = wall(c["foyer"], 128, seed=k + 10).png()
        out[f"textures/AJ3B{n}.png"] = wall(c["bar"], 144, seed=k + 20).png()
        out[f"flats/AJ3O{n}.png"] = flat(*c["ofloor"], 440 + k).png()
        out[f"flats/AJ3M{n}.png"] = flat(*c["mfloor"], 450 + k).png()
        ra, rb = c["runner"]
        r = Img(64, 64, ra)
        r.noise(5, 460 + k)
        for cx, cy in ((0, 0), (64, 0), (0, 64), (64, 64), (32, 32)):
            r.diamond(cx, cy, 6, rb)
            r.diamond(cx, cy, 4, ra)
        out[f"flats/AJ3R{n}.png"] = r.png()
        s = Img(64, 64, c["seat"])
        s.noise(6, 465 + k)
        for x in range(0, 64, 16):
            s.rect(x, 0, x + 1, 64, shade(c["seat"], 0.7))
            s.rect(x + 1, 0, x + 2, 64, shade(c["seat"], 1.15))
        for cx in range(8, 64, 16):
            for cy in range(8, 64, 16):
                s.disc(cx, cy, 1, shade(c["seat"], 0.5))
        both(f"AJ3S{n}", s)
        kind, a, b = c["ceil"]
        out[f"flats/AJ3C{n}.png"] = ceiling(kind, a, b, False, 480 + k).png()
        out[f"flats/AJ3L{n}.png"] = ceiling(kind, a, b, True, 480 + k).png()
        low = Img(64, 64, c["low"])
        low.frame(0, 0, 64, 64, shade(c["low"], 0.9), 1)
        low.noise(3, 485 + k)
        out[f"flats/AJ3E{n}.png"] = low.png()
        out[f"textures/AJ3K{n}.png"] = curtain(*c["curtain"]).png()
        for col, rgb in DOOR_COLOURS.items():
            pic = tiled(foyer, 64, 176)
            hang_picture(pic, 176, rgb)
            out[f"textures/AJ3P{n}{col}.png"] = pic.png()
        d = door(foyer, rd, (104, 72, 44) if n != "3" else (150, 98, 58))
        out[f"textures/AJ3D{n}F.png"] = d.png()
        out[f"textures/AJ3D{n}F1.png"] = locked(d, "1").png()

    # --- the back of the house, the same whatever the front looks like ------
    def painted(h, upper, dado, dh, seed):
        im = brick(64, h, upper, shade(upper, 0.9), seed)
        lo = brick(64, dh, dado, shade(dado, 0.82), seed + 1)
        for y in range(dh):
            for x in range(64):
                im.set(x, h - dh + y, lo.px[y * 64 + x][:3])
        im.rect(0, h - dh - 2, 64, h - dh, (24, 26, 28))
        im.rect(0, h - 6, 64, h, shade(dado, 0.6))
        im.rect(0, 0, 64, 3, shade(upper, 0.8))
        im.noise(4, seed + 2)
        return im

    corridor = painted(128, (214, 204, 176), (44, 84, 66), 48, 500)
    out["textures/AJ3XW.png"] = corridor.png()
    dressing = painted(112, (222, 192, 172), (112, 72, 52), 36, 505)
    out["textures/AJ3XD.png"] = dressing.png()
    out["textures/AJ3XG.png"] = painted(112, (152, 178, 142), (48, 78, 56), 36, 510).png()
    star = Img(64, 112, (228, 200, 190))                         # the star's: paper, and gold stars
    for cy in range(8, 76, 16):
        for cx in range(0, 65, 16):
            x = cx + (8 if (cy // 16) % 2 else 0)
            star.diamond(x, cy, 3, GILT)
            star.rect(x - 4, cy, x + 5, cy + 1, GILT)
            star.rect(x, cy - 4, x + 1, cy + 5, GILT)
    star.rect(0, 76, 64, 112, (120, 34, 44))
    for x in (0, 32):
        star.frame(x + 4, 82, x + 28, 102, (84, 22, 30), 2)
    star.rect(0, 72, 64, 76, GILT)
    star.rect(0, 104, 64, 112, (60, 20, 24))
    star.rect(0, 0, 64, 4, GILT)
    star.noise(4, 515)
    out["textures/AJ3XS.png"] = star.png()
    for name, base in (("AJ3XM", dressing), ("AJ3XN", star)):    # mirrors over the dressing tables
        mi = Img(64, 80)
        for y in range(80):
            for x in range(64):
                mi.set(x, y, base.px[y * 64 + x][:3])
        mi.rect(5, 8, 59, 68, (96, 66, 42))
        mi.rect(9, 12, 55, 64, (170, 192, 200))
        for i in range(30):
            mi.set(14 + i, 50 - i, (214, 228, 232))
            mi.set(20 + i, 52 - i, (198, 214, 220))
        mi.frame(9, 12, 55, 64, (60, 40, 26), 1)
        for x in range(8, 60, 8):
            mi.disc(x, 10, 2, (255, 246, 200))
        for y in range(18, 66, 8):
            mi.disc(7, y, 2, (255, 246, 200))
            mi.disc(57, y, 2, (255, 246, 200))
        out[f"textures/{name}.png"] = mi.png()
    booth = Img(64, 112, (62, 66, 74))                           # the lighting board
    booth.noise(4, 520)
    for x in (0, 32):
        booth.frame(x + 1, 14, x + 31, 100, (36, 38, 44), 1)
        for y in range(22, 60, 12):
            for dx in (8, 16, 24):
                booth.disc(x + dx, y, 3, (188, 188, 180))
                booth.set(x + dx, y - 2, (30, 30, 34))
        for dx, lamp in ((8, (220, 60, 50)), (16, (230, 190, 60)), (24, (70, 200, 90))):
            booth.disc(x + dx, 66, 1, lamp)
            booth.rect(x + dx - 1, 74, x + dx + 1, 94, (20, 20, 24))
            booth.rect(x + dx - 2, 78 + dx // 2, x + dx + 2, 82 + dx // 2, (200, 196, 184))
    booth.rect(0, 0, 64, 10, (40, 42, 48))
    booth.rect(0, 4, 64, 6, (110, 112, 118))
    booth.rect(0, 104, 64, 112, (30, 32, 36))
    out["textures/AJ3XB.png"] = booth.png()
    under = brick(64, 64, (98, 62, 52), (58, 40, 36), 525)
    under.noise(6, 526)
    out["textures/AJ3XU.png"] = under.png()
    fl = brick(64, 64, (40, 40, 44), (26, 26, 30), 530)
    for x in (7, 23, 39, 55):                                    # ropes
        fl.rect(x, 0, x + 2, 64, (140, 120, 84))
        for y in range(0, 64, 4):
            fl.set(x + (y // 4) % 2, y, (96, 80, 54))
    fl.noise(4, 531)
    out["textures/AJ3XL.png"] = fl.png()
    st = brick(64, 64, (206, 198, 174), shade((206, 198, 174), 0.88), 535)
    st.noise(4, 536)
    out["textures/AJ3XP.png"] = st.png()
    lino = Img(64, 64, (112, 66, 52))
    lino.noise(9, 540)
    lino.rect(0, 0, 64, 1, (88, 52, 42))
    lino.rect(0, 0, 1, 64, (88, 52, 42))
    out["flats/AJ3XF.png"] = lino.png()
    dark = Img(64, 64, (24, 24, 28))                             # over the stage: nothing to see
    dark.noise(3, 545)
    dark.rect(0, 30, 64, 33, (46, 46, 52))
    out["flats/AJ3XC.png"] = dark.png()
    d = door(corridor, rd, (104, 72, 44))
    out["textures/AJ3DXB.png"] = d.png()
    out["textures/AJ3DXB23.png"] = locked(d, "23").png()
