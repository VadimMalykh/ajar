"""The old door's pictures (the old door lab, map BEFORE; PLAN.md, "The old door
lab"; src/zscript/then.zs, a door left hanging).

A colour door hung at an earlier time is an old door in the same frame at
every later time. Its leaf is the colour's own (gfx.door), aged:

  AJO1..AJO6  ten years (a door hung BEFORE, seen THEN), RED to PINK: the
              paint dulled and greyed, scuffed at the foot and round the
              knob, the first chips at the foot and the edges, the glyph
              yellowed; plainly not the new door beside it, still the colour
  AJQ1..AJQ6  forty and fifty years (seen NOW), RED to PINK: most of the
              colour gone out of the paint, and the paint off in ragged
              patches down to grey weathered wood (peel, bare), most at the
              foot and the edges; rust run from the two hinges (the left
              edge: the knob is on the right), the knob gone dark; the colour
              still reads in what is left and the glyph is still there

The leaf is a wall sprite, so the far side, which sees it through the
opening, sees the same face. The far side's own face, the colour's surround
of its recess (gfx.py's AJTRn / AJTFn), ages with the old door that opens
onto it (then.zs, AgeFar):

  AJTRnO, AJTFnO  ten years: dulled as the leaf
  AJTRnQ, AJTFnQ  forty and fifty years: faded, the paint off in patches,
                  rust run down from the top
"""
import random

from gfx import DOOR_COLOURS, Img, door, shade

COLOURS = range(1, 7)
HINGES = (14, 80)           # the hinges' rows on the leaf's left edge


def toward(c, to, f):
    return tuple(max(0, min(255, round(a + (b - a) * f))) for a, b in zip(c[:3], to))


def grey(c):
    v = sum(c[:3]) / 3
    return (v, v, v)


def peel(w, h, seed, bias):
    """Where the paint has come off: a smooth random field (a coarse grid, blended) plus `bias(x, y)`, cut at a
    level, so the bare places are a few ragged patches and not spots."""
    rnd = random.Random(seed)
    gw, gh = w // 8 + 2, h // 8 + 2
    g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    off = set()
    for y in range(h):
        for x in range(w):
            fx, fy = x / 8, y / 8
            ix, iy = int(fx), int(fy)
            tx, ty = fx - ix, fy - iy
            n = (g[iy][ix] * (1 - tx) * (1 - ty) + g[iy][ix + 1] * tx * (1 - ty)
                 + g[iy + 1][ix] * (1 - tx) * ty + g[iy + 1][ix + 1] * tx * ty)
            if n + bias(x, y) + rnd.uniform(-0.05, 0.05) > 0.66:
                off.add((x, y))
    return off


def bare(im, off, seed):
    """The wood under the paint, weathered grey, its grain running down; a dark line where the paint's edge
    stands over it (above and to the left)."""
    rnd = random.Random(seed)
    grain = [rnd.uniform(0.82, 1.08) for _ in range(im.w)]
    wood = (104, 92, 78)
    for x, y in off:
        c = shade(wood, grain[x] * rnd.uniform(0.94, 1.04))
        if (x, y - 1) not in off or (x - 1, y) not in off:
            c = shade(wood, 0.55)
        im.set(x, y, c)


def ten_years(c):
    im = door(c)
    rnd = random.Random(500 + c)
    for i, p in enumerate(im.px):
        x, y = i % im.w, i // im.w
        glyph = p[0] > 230 and p[1] > 230 and p[2] > 220
        q = toward(p, grey(p), 0.42)
        q = shade(q, 0.74 + 0.06 * rnd.random())
        if glyph:                                             # the glyph: yellowed
            q = toward(q, (196, 182, 136), 0.6)
        if y > 80 and rnd.random() < 0.2 + (y - 80) * 0.04:   # scuffed at the foot
            q = shade(q, 0.7)
        if (x - 53) ** 2 + (y - 49) ** 2 < 64 and rnd.random() < 0.5:     # and round the knob
            q = shade(q, 0.75)
        im.px[i] = list(q) + [255]
    # the first chips, at the foot and the edges
    off = peel(im.w, im.h, 520 + c, lambda x, y: -0.22 + 0.4 * (y / 95) ** 4 + (0.12 if min(x, 63 - x) < 3 else 0))
    bare(im, off, 540 + c)
    return im


def fifty_years(c):
    im = door(c)
    rnd = random.Random(700 + c)
    for i, p in enumerate(im.px):
        y = i // im.w
        glyph = p[0] > 230 and p[1] > 230 and p[2] > 220
        q = toward(p, grey(p), 0.62)                          # sun and damp: most of the colour is gone
        q = shade(q, 0.56 + 0.08 * rnd.random() - 0.08 * (y / 95))
        if glyph:
            q = toward(q, (150, 138, 104), 0.7)
        im.px[i] = list(q) + [255]
    # the paint off in ragged patches, most of all at the foot and along the edges; the glyph keeps most of its own
    def bias(x, y):
        b = 0.02 + 0.34 * (y / 95) ** 2 + (0.14 if min(x, 63 - x) < 5 else 0)
        if 21 <= x <= 43 and 13 <= y <= 39:
            b -= 0.3
        return b
    off = peel(im.w, im.h, 720 + c, bias)
    bare(im, off, 740 + c)
    # rust run down from each hinge
    rust = (112, 52, 26)
    for hy in HINGES:
        for x in range(0, 11):
            run = round(30 * (1 - x / 11) * rnd.uniform(0.6, 1.0))
            for y in range(hy - 3, hy + run):
                if 0 <= y < im.h:
                    k = (y - hy) / max(run, 1)
                    f = 0.85 if y < hy + 3 else max(0.15, 0.75 * (1 - k))
                    im.set(x, y, toward(im.px[y * im.w + x], rust, f))
        im.rect(0, hy - 3, 3, hy + 4, (60, 38, 26))           # the hinge itself
    im.disc(53, 49, 3, (70, 62, 46))                          # the knob, gone dark
    return im


def surround(c):
    """The colour's surround of a far side, as gfx.py draws AJTRn."""
    rgb = DOOR_COLOURS[c]
    t = Img(64, 64, shade(rgb, 0.7))
    t.noise(5, 20 + c)
    for y in range(0, 64, 16):
        t.rect(0, y, 64, y + 1, shade(rgb, 0.4))
    return t


def surround_ten(c):
    t = surround(c)
    rnd = random.Random(900 + c)
    for i, p in enumerate(t.px):
        t.px[i] = list(shade(toward(p, grey(p), 0.42), 0.74 + 0.06 * rnd.random())) + [255]
    return t


def surround_fifty(c):
    t = surround(c)
    rnd = random.Random(1100 + c)
    rust = (112, 52, 26)
    for i, p in enumerate(t.px):
        t.px[i] = list(shade(toward(p, grey(p), 0.62), 0.56 + 0.08 * rnd.random())) + [255]
    off = peel(64, 64, 1120 + c, lambda x, y: 0.06)           # the paint off in patches
    bare(t, off, 1140 + c)
    for x0 in (rnd.randint(4, 24), rnd.randint(36, 58)):     # rust run down from the top
        for x in range(x0, x0 + 3):
            run = rnd.randint(14, 30)
            for y in range(run):
                t.set(x, y, toward(t.px[y * t.w + x], rust, 0.7 * (1 - y / run)))
    return t


def make(out):
    for c in COLOURS:
        out[f"sprites/AJO{c}A0.png"] = ten_years(c).png(grab=(32, 96))
        out[f"sprites/AJQ{c}A0.png"] = fifty_years(c).png(grab=(32, 96))
        for age, im in (("O", surround_ten(c)), ("Q", surround_fifty(c))):
            out[f"textures/AJTR{c}{age}.png"] = im.png()
            out[f"flats/AJTF{c}{age}.png"] = im.png()
