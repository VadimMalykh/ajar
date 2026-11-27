"""MAP10's square, its two stops and the depot (see AJAR_SQUARE in map_hinges10.py).

The bus is the film's, forty years on (gfx_bus.py), and the square is where
such a bus would have been left: a yard behind a concrete fence, cracked
asphalt, a sheet-steel shelter gone to rust, a kiosk nobody opens. One look,
not three: Vadim asked for the bus's (2026-11-17), and this is its setting.
The districts keep the looks of their own levels.

Walls (64 wide, laid by world position: ALIGNED):
  AJQF     144  the fence: concrete panels cast in lozenges, on their blocks;
                AJQFA with what is left of posters, AJQFB with a corner knocked
                out. No wall of the square is taller than the bus.
  AJQM     144  the museum's side of the square: terracotta and stone (MAP06's
                colours); AJQMA with a blind window. AJQMP: its lowest 128,
                for the porch before its door
  AJQB      64  sand-lime brick, for the depot (any height)
  AJQK     128  the kiosk's front, under its canopy
  AJQS     128  the shelter: ribbed sheet steel; AJQSA with the stop's sign
                and what is left of a timetable
Not aligned:
  AJQMD1   128  the museum's door from the square: one lock (shift 48)
  AJQMD0   128  the same with no lock and a card, CLOSED (MAP22, where it never opens)
  AJQSF, AJQKF, AJQMF, AJQDF  16  the edge of a canopy: the shelter's (BUS
                STOP), the kiosk's (PRESS), the museum's (MUSEUM), the depot's
                gate's (DEPOT)
Flats (and walls, for the sides of things):
  AJQAS asphalt   AJQPV paving slabs   AJQOC the depot's concrete, oiled
  AJQRF the roof of a bus   AJQSC under a canopy   AJQBE a bench of slats
"""
import random

from gfx import Img, shade, text, unpng
from gfx_bus import blend, mix, RUST

CONC = (150, 148, 140)
TERRA, BUFF = (164, 82, 56), (212, 170, 112)
LIME = (196, 192, 180)
STEEL = (92, 124, 126)
ALIGNED = {"AJQF", "AJQFA", "AJQFB", "AJQM", "AJQMA", "AJQMP", "AJQB", "AJQK", "AJQS"}


def grime(im, seed, foot=34, moss=True, streaks=4):
    """Rain and dirt on a wall: streaks from its top, dark at its foot, moss."""
    rnd = random.Random(seed)
    for _ in range(streaks):
        x, n = rnd.randrange(im.w), rnd.randrange(20, 70)
        for k in range(n):
            blend(im, x, k, (40, 38, 34), 0.3 * (1 - k / n))
    for y in range(im.h - foot, im.h):
        f = ((y - (im.h - foot)) / foot) ** 2
        for x in range(im.w):
            blend(im, x, y, (40, 38, 32), 0.45 * f)
    if moss:
        for x in range(im.w):
            for k in range(rnd.randrange(0, 9)):
                blend(im, x, im.h - 1 - k, (60, 86, 42), 0.7 - k * 0.07)


def crack(im, x, y, n, rnd, c=(30, 30, 30), f=0.7, wrap=False):
    for _ in range(n):
        blend(im, x % im.w if wrap else x, y % im.h if wrap else y, c, f)
        x += rnd.choice((-1, 0, 0, 1))
        y += rnd.choice((0, 1, 1))


def fence(seed, posters=False, broken=False):
    """A panel of the concrete fence every Soviet yard had: lozenges cast in
    relief, a rim round them, two blocks to stand in."""
    im = Img(64, 144, CONC)
    rnd = random.Random(seed)
    im.noise(7, seed)
    im.rect(0, 0, 64, 3, shade(CONC, 1.12))                                  # the rim
    im.rect(0, 0, 1, 124, shade(CONC, 0.62))                                 # the joint between two panels
    im.rect(63, 0, 64, 124, shade(CONC, 0.62))
    im.rect(1, 0, 3, 124, shade(CONC, 1.1))
    im.rect(61, 0, 63, 124, shade(CONC, 0.8))
    for row in range(7):                                                     # the lozenges: four to a panel
        for col in range(4):
            x0, y0 = 4 + col * 14, 6 + row * 16
            for y in range(16):
                for x in range(14):
                    u, v = (x - 6.5) / 7, (y - 7.5) / 8
                    if abs(u) + abs(v) > 1:
                        continue
                    lit = 1.16 if v < -abs(u) * 0.2 and u < 0.3 else 0.74 if v > abs(u) * 0.2 and u > -0.3 else 1.04 if u < 0 else 0.88
                    im.set(x0 + x, y0 + y, shade(CONC, lit * rnd.uniform(0.95, 1.05)))
    im.rect(0, 118, 64, 124, shade(CONC, 0.9))                               # the foot of the panel
    im.rect(0, 124, 64, 144, shade(CONC, 0.7))                               # the gap under it, dark
    for x1, x2 in ((0, 14), (50, 64)):                                       # the blocks it stands in
        im.rect(x1, 120, x2, 144, shade(CONC, 0.95))
        im.rect(x1, 120, x2, 122, shade(CONC, 1.12))
    crack(im, rnd.randrange(8, 56), 4, rnd.randrange(30, 90), rnd)
    if posters:
        for px, py, c in ((8, 40, (190, 182, 160)), (34, 52, (168, 150, 120))):
            for y in range(py, py + 26):
                for x in range(px, px + 20):
                    if rnd.random() < 0.8 - (y - py) / 60:                   # torn from below
                        blend(im, x, y, c, 0.85)
            for k in range(3):
                im.rect(px + 3, py + 5 + k * 5, px + 3 + rnd.randrange(8, 15), py + 6 + k * 5, shade(c, 0.5))
    if broken:
        for y in range(0, 30):                                               # a corner knocked out: the iron in it
            for x in range(40 + y // 2 + rnd.randrange(3), 61):
                im.set(x, y, (26, 26, 30))
        for x in (46, 53):
            for y in range(4, 26):
                im.set(x + (y // 9) % 2, y, RUST)
    grime(im, seed + 1, foot=40)
    return im


def bricks(w, h, base, seed, bw=16, bh=8, mortar=0.7):
    im = Img(w, h, base)
    rnd = random.Random(seed)
    for row in range(h // bh + 1):
        for col in range(-1, w // bw + 1):
            x0 = col * bw + (bw // 2 if row % 2 else 0)
            c = shade(base, rnd.uniform(0.86, 1.08))
            im.rect(x0, row * bh, x0 + bw - 1, row * bh + bh - 1, c)
    for row in range(h // bh + 1):
        im.rect(0, row * bh + bh - 1, w, row * bh + bh, shade(base, mortar))
        for col in range(-1, w // bw + 1):
            x0 = col * bw + (bw // 2 if row % 2 else 0) + bw - 1
            im.rect(x0, row * bh, x0 + 1, row * bh + bh, shade(base, mortar))
    im.noise(5, seed)
    return im


def museum(seed, window=False):
    """The museum's side: terracotta brick between a stone cornice and a stone foot."""
    im = bricks(64, 144, TERRA, seed)
    im.rect(0, 0, 64, 14, BUFF)
    im.rect(0, 14, 64, 16, shade(BUFF, 0.6))
    for x in range(2, 64, 8):
        im.rect(x, 8, x + 4, 14, shade(BUFF, 0.8))                           # dentils
    im.rect(0, 112, 64, 144, shade(BUFF, 0.86))
    im.rect(0, 112, 64, 114, shade(BUFF, 1.08))
    im.rect(0, 128, 64, 129, shade(BUFF, 0.6))
    if window:                                                               # a blind window: stone round a dark panel
        im.rect(14, 30, 50, 100, shade(BUFF, 0.95))
        im.rect(18, 34, 46, 96, (30, 30, 38))
        im.rect(31, 34, 33, 96, shade(BUFF, 0.8))
        im.rect(18, 62, 46, 64, shade(BUFF, 0.8))
        im.rect(12, 100, 52, 104, shade(BUFF, 1.05))
    grime(im, seed + 1, foot=30, streaks=6)
    return im


def crop(im, y0, y1):
    out = Img(im.w, y1 - y0)
    out.px = [list(p) for p in im.px[y0 * im.w:y1 * im.w]]
    return out


def sheet(seed, h=128, paint=STEEL):
    """Ribbed sheet steel, painted once."""
    im = Img(64, h, paint)
    rnd = random.Random(seed)
    for x in range(64):
        f = (1.1, 1.0, 0.88, 0.76)[x % 8 // 2]
        for y in range(h):
            im.set(x, y, shade(paint, f))
    for _ in range(30):                                                      # rust: through the paint, and running
        x, y, n = rnd.randrange(64), rnd.randrange(h), rnd.randrange(4, 30)
        for k in range(n):
            blend(im, x, y + k, RUST, 0.6 * (1 - k / n))
        blend(im, x + 1, y, RUST, 0.6)
        blend(im, x - 1, y + 1, RUST, 0.5)
    for y in range(h - 26, h):
        for x in range(64):
            if rnd.random() < ((y - (h - 26)) / 26) ** 1.5:
                blend(im, x, y, RUST, 0.7)
    im.rect(0, 0, 64, 4, shade(paint, 0.55))
    im.noise(5, seed)
    return im


def fascia(word, paint, ink, seed, sign=False):
    im = Img(64, 16, paint)
    im.rect(0, 0, 64, 1, shade(paint, 1.2))
    im.rect(0, 14, 64, 16, shade(paint, 0.5))
    n = len(word) * 6 - 1
    x = 32 - n // 2 + (7 if sign else 0)
    if sign:                                                                 # the stop's own sign: a black A on yellow
        im.rect(x - 14, 2, x - 3, 13, (226, 186, 40))
        im.frame(x - 14, 2, x - 3, 13, (30, 28, 24), 1)
        text(im, "A", x - 11, 5, (30, 28, 24), 1)
    text(im, word, x, 5, ink, 1)
    rnd = random.Random(seed)
    for _ in range(8):
        x, n = rnd.randrange(64), rnd.randrange(3, 12)
        for k in range(n):
            blend(im, x, 2 + k, RUST, 0.5 * (1 - k / n))
    im.noise(5, seed)
    return im


def flat(base, seed, amount=7):
    im = Img(64, 64, base)
    im.noise(amount, seed)
    return im


def make(out):
    def both(name, im):
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    out["textures/AJQF.png"] = fence(301).png()
    out["textures/AJQFA.png"] = fence(302, posters=True).png()
    out["textures/AJQFB.png"] = fence(303, broken=True).png()
    front = museum(311)
    out["textures/AJQM.png"] = front.png()
    out["textures/AJQMA.png"] = museum(312, window=True).png()
    out["textures/AJQMP.png"] = crop(front, 16, 144).png()

    lime = bricks(64, 64, LIME, 321, mortar=0.78)
    rnd = random.Random(322)
    for _ in range(5):
        x, n = rnd.randrange(64), rnd.randrange(10, 40)
        for k in range(n):
            blend(lime, x, k, (60, 56, 50), 0.25 * (1 - k / n))
    out["textures/AJQB.png"] = lime.png()

    kiosk = sheet(331, paint=(70, 96, 130))                                  # the kiosk: blue once
    kiosk.rect(0, 30, 64, 34, shade((70, 96, 130), 0.6))                     # the shelf its shutter came down to
    kiosk.rect(0, 92, 64, 96, shade((70, 96, 130), 0.6))
    out["textures/AJQK.png"] = kiosk.png()

    out["textures/AJQS.png"] = sheet(341).png()
    sign = sheet(342)
    sign.rect(8, 20, 30, 42, (226, 186, 40))                                 # the stop's sign
    sign.frame(8, 20, 30, 42, (30, 28, 24), 2)
    text(sign, "A", 12, 24, (30, 28, 24), 3)
    sign.rect(34, 18, 58, 70, (206, 200, 180))                               # a timetable, what is left of it
    sign.frame(34, 18, 58, 70, (60, 56, 50), 1)
    rnd = random.Random(343)
    for y in range(22, 66, 4):
        if rnd.random() < 0.7:
            sign.rect(37, y, 37 + rnd.randrange(6, 19), y + 1, (90, 86, 80))
    for _ in range(140):
        blend(sign, rnd.randrange(34, 58), rnd.randrange(40, 70), STEEL, 0.9)   # torn from below
    for k in range(18):
        blend(sign, 9, 42 + k, RUST, 0.6 - k * 0.03)
        blend(sign, 28, 42 + k, RUST, 0.5 - k * 0.03)
    out["textures/AJQSA.png"] = sign.png()

    out["textures/AJQSF.png"] = fascia("BUS STOP", shade(STEEL, 0.8), (226, 220, 196), 351, sign=True).png()
    out["textures/AJQKF.png"] = fascia("PRESS", (58, 80, 110), (226, 220, 196), 352).png()
    out["textures/AJQMF.png"] = fascia("MUSEUM", shade(BUFF, 0.9), (70, 34, 24), 353).png()
    out["textures/AJQDF.png"] = fascia("DEPOT", (60, 60, 64), (226, 186, 40), 354).png()

    # the museum's door from the square: the generic locked door's leaf under 32 rows of the front
    # (AJQMD0, MAP22: the plain door's leaf, no lock, and a card on it: nobody has a key to it there)
    for name, door in (("AJQMD1", "AJHK1"), ("AJQMD0", "AJHDOR")):
        leaf = unpng(out[f"textures/{door}.png"])
        face = Img(64, 128)
        for y in range(32):
            for x in range(64):
                face.px[y * 64 + x] = list(front.px[(16 + y) * 64 + (x + 48) % 64])
        for y in range(96):
            face.px[(32 + y) * 64:(33 + y) * 64] = [list(p) for p in leaf.px[(leaf.h - 96 + y) * 64:(leaf.h - 95 + y) * 64]]
        face.rect(0, 28, 64, 32, shade(BUFF, 0.7))                           # its lintel
        if name == "AJQMD0":
            face.rect(12, 60, 52, 73, (236, 228, 204))
            face.frame(12, 60, 52, 73, (120, 100, 70), 1)
            text(face, "CLOSED", 15, 64, (70, 34, 24), 1)
        out[f"textures/{name}.png"] = face.png()

    # --- flats ---------------------------------------------------------------
    rnd = random.Random(361)
    asphalt = flat((62, 62, 66), 361, 9)
    for _ in range(3):                                                       # patches, of other years
        x, y, w, h = rnd.randrange(64), rnd.randrange(64), rnd.randrange(10, 26), rnd.randrange(8, 20)
        tone = rnd.choice(((48, 48, 52), (78, 76, 76)))
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                blend(asphalt, xx % 64, yy % 64, tone, 0.5)
    for _ in range(4):
        x, y = rnd.randrange(64), rnd.randrange(64)
        for k in range(rnd.randrange(20, 60)):
            blend(asphalt, x % 64, y % 64, (22, 22, 24), 0.8)
            if rnd.random() < 0.12:
                blend(asphalt, (x + 1) % 64, y % 64, (70, 96, 48), 0.8)      # what grows in a crack
            x += rnd.choice((-1, 0, 1, 1))
            y += rnd.choice((-1, 0, 1))
    both("AJQAS", asphalt)

    slabs = flat((128, 126, 118), 362, 6)
    for i in range(0, 64, 32):
        slabs.rect(i, 0, i + 1, 64, (70, 70, 66))
        slabs.rect(0, i, 64, i + 1, (70, 70, 66))
    for _ in range(46):
        k = rnd.randrange(64)
        blend(slabs, k, rnd.choice((0, 32)) + rnd.choice((0, 1)), (70, 100, 48), 0.8)
        blend(slabs, rnd.choice((0, 32)) + rnd.choice((0, 1)), k, (70, 100, 48), 0.8)
    crack(slabs, 12, 34, 28, rnd, (60, 60, 58), 0.8, wrap=True)
    crack(slabs, 44, 2, 22, rnd, (60, 60, 58), 0.8, wrap=True)
    for cx, cy in ((48, 48), (10, 20)):                                      # a slab that has sunk; a stain
        for y in range(cy - 7, cy + 7):
            for x in range(cx - 9, cx + 9):
                blend(slabs, x % 64, y % 64, (90, 88, 84), 0.25)
    both("AJQPV", slabs)

    oiled = flat((112, 110, 104), 363, 6)
    oiled.rect(0, 0, 64, 1, (80, 78, 74))
    oiled.rect(0, 0, 1, 64, (80, 78, 74))
    for cx, cy, r in ((20, 22, 11), (46, 44, 8), (50, 12, 5)):                # oil, where buses stood
        for y in range(cy - r, cy + r):
            for x in range(cx - r, cx + r):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / r
                if d < 1:
                    blend(oiled, x % 64, y % 64, (36, 34, 36), 0.6 * (1 - d * d))
    both("AJQOC", oiled)

    roof = flat((186, 176, 150), 364, 6)                                     # a bus from above: seams, a hatch
    for x in (0, 32):
        roof.rect(x, 0, x + 1, 64, (120, 112, 96))
    roof.frame(18, 20, 46, 44, (110, 104, 90), 2)
    for _ in range(60):
        blend(roof, rnd.randrange(64), rnd.randrange(64), RUST, 0.5)
    both("AJQRF", roof)

    under = Img(64, 64, shade(STEEL, 0.7))                                   # under a canopy: the same sheet, darker
    for x in range(64):
        for y in range(64):
            under.set(x, y, shade(STEEL, 0.7 * (1.08, 1.0, 0.9, 0.8)[x % 8 // 2]))
    for _ in range(50):
        blend(under, rnd.randrange(64), rnd.randrange(64), RUST, 0.6)
    under.noise(4, 365)
    both("AJQSC", under)

    green = (74, 104, 70)
    bench = Img(64, 64, (40, 38, 36))                                        # slats, their green paint going
    for y in range(0, 64, 8):
        for yy in range(y, y + 6):
            for x in range(64):
                bench.set(x, yy, shade(green if rnd.random() < 0.8 else (130, 104, 70), 1.08 if yy == y else 1))
    for x in (6, 57):
        for y in range(0, 64, 8):
            bench.set(x, y + 3, (40, 36, 34))
    bench.noise(6, 366)
    both("AJQBE", bench)
