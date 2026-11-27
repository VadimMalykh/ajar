"""The old door's pictures (the old door lab, map BEFORE; PLAN.md, "The old door
lab"; src/zscript/then.zs, a door left hanging).

A colour door hung at an earlier time is an old door in the same frame at
every later time. Its leaf is the colour's own (gfx.door), aged:

  AJO1..AJO6  ten years (a door hung BEFORE, seen THEN), RED to PINK: the
              paint dulled and greyed a little, scuffed at the foot and round
              the knob, the glyph yellowed; still the colour at a glance
  AJQ1..AJQ6  forty and fifty years (seen NOW), RED to PINK: the paint faded
              and flaking off in patches down to the grey primer and the wood,
              rust run from the two hinges (the left edge: the knob is on the
              right), the knob gone dark; the colour still reads in what is left
              and the glyph is still there

The leaf is a wall sprite, so the far side, which sees it through the
opening, sees the same face. The far side's own face, the colour's surround
of its recess (gfx.py's AJTRn / AJTFn), ages with the old door that opens
onto it (then.zs, AgeFar):

  AJTRnO, AJTFnO  ten years: dulled as the leaf
  AJTRnQ, AJTFnQ  forty and fifty years: faded, flaking to the primer, rust
                  run down from the top
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


def ten_years(c):
    im = door(c)
    rnd = random.Random(500 + c)
    for i, p in enumerate(im.px):
        x, y = i % im.w, i // im.w
        q = toward(p, grey(p), 0.3)
        q = shade(q, 0.86 + 0.06 * rnd.random())
        if p[0] > 230 and p[1] > 230 and p[2] > 220:         # the glyph: yellowed
            q = toward(q, (214, 200, 150), 0.5)
        if y > 86 and rnd.random() < 0.35:                    # scuffed at the foot
            q = shade(q, 0.75)
        if (x - 53) ** 2 + (y - 49) ** 2 < 49 and rnd.random() < 0.5:     # and round the knob
            q = shade(q, 0.8)
        im.px[i] = list(q) + [255]
    return im


def fifty_years(c):
    im = door(c)
    rnd = random.Random(700 + c)
    primer, wood = (150, 146, 136), (122, 96, 70)
    for i, p in enumerate(im.px):
        q = toward(p, grey(p), 0.45)
        q = shade(q, 0.72 + 0.1 * rnd.random())
        if p[0] > 230 and p[1] > 230 and p[2] > 220:
            q = toward(q, (190, 176, 132), 0.6)
        im.px[i] = list(q) + [255]
    # flakes: patches where the paint has come off, the primer round them and the wood in the middle
    for _ in range(26):
        cx, cy, r = rnd.randint(2, 61), rnd.randint(2, 93), rnd.uniform(2, 5.5)
        if 23 <= cx <= 41 and 15 <= cy <= 37:
            continue                                          # the glyph stays readable
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                d = ((x - cx) ** 2 + ((y - cy) * 0.8) ** 2) ** 0.5 + rnd.uniform(-0.8, 0.8)
                if d < r * 0.55:
                    im.set(x, y, shade(wood, rnd.uniform(0.85, 1.05)))
                elif d < r:
                    im.set(x, y, shade(primer, rnd.uniform(0.85, 1.0)))
    # rust run down from each hinge
    rust = (128, 62, 30)
    for hy in HINGES:
        for x in range(0, 9):
            run = round(22 * (1 - x / 9) * rnd.uniform(0.6, 1.0))
            for y in range(hy - 3, hy + run):
                if 0 <= y < im.h:
                    k = (y - hy) / max(run, 1)
                    f = 0.85 if y < hy + 3 else max(0.15, 0.7 * (1 - k))
                    im.set(x, y, toward(im.px[y * im.w + x], rust, f))
        im.rect(0, hy - 3, 3, hy + 4, (72, 44, 30))           # the hinge itself
    im.disc(53, 49, 3, (96, 84, 60))                          # the knob, gone dark
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
        t.px[i] = list(shade(toward(p, grey(p), 0.3), 0.86 + 0.06 * rnd.random())) + [255]
    return t


def surround_fifty(c):
    t = surround(c)
    rnd = random.Random(1100 + c)
    primer, rust = (150, 146, 136), (128, 62, 30)
    for i, p in enumerate(t.px):
        t.px[i] = list(shade(toward(p, grey(p), 0.45), 0.72 + 0.1 * rnd.random())) + [255]
    for _ in range(9):                                        # flakes down to the primer
        cx, cy, r = rnd.randint(0, 63), rnd.randint(0, 63), rnd.uniform(2, 4.5)
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 + rnd.uniform(-0.8, 0.8) < r:
                    t.set(x % 64, y % 64, shade(primer, rnd.uniform(0.8, 1.0)))
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
