"""The then and now lab's own pictures (map THEN, tools/map_then.py).

  AJTHL2, AJTHL3   a lever on the lab wall of MAP11's look 2 (Thaw, THEN) and
                   look 3 (Post Box, NOW), 256 high, the lever at hand height
                   from the floor (lay it with dontpegbottom); both switches
  AJTHD3           the same place NOW where a fixture's lever was: its plate
                   rusted, the lever gone, two bolt holes (does nothing)
MAP21 (tools/map_longrun.py):
  AJCKTR, AJCKTF   the trim of a frame that takes only the clocked door: ivory
                   bands with a clock face in each 64 (wall and flat)
  AJTHK2, AJTHK3   the machine desk's panel, 64 by 40 (the desk's lower face):
                   then two key switches marked 1 and 2 and a lamp; now
                   smashed, the switches torn out
The clocked door is gfx.py's (door(CLOCKED)); the heap's crates are MAP17's
(AJDSTOR, AJDSTOF); a burnt hole's edges are Doom's ASHWALL2.
"""
import math
import random

from gfx import Img, levers, lever, unpng, shade

IVORY, BRASS, INK = (226, 218, 196), (190, 150, 70), (40, 34, 30)


def make(out):
    walls = {n: unpng(out[f"textures/AJILA{n}.png"]) for n in (2, 3)}
    levers(out, "AJTHL2", walls[2], 256)
    levers(out, "AJTHL3", walls[3], 256)
    dead = lever(walls[3], False, 256)
    cy = 256 - 52
    rust, dark = (112, 70, 40), (34, 26, 20)
    rnd = random.Random(77)
    for y in range(cy - 26, cy + 24):                            # the plate, rusted over, lamp and lever gone
        for x in range(18, 46):
            dead.set(x, y, shade(rust, rnd.uniform(0.75, 1.15)))
    for y in (cy - 20, cy + 18):
        dead.disc(32, y, 2, dark)                                # where the bolts were
    dead.rect(30, cy - 8, 34, cy + 10, shade(rust, 0.6))         # a scar where the slot was
    out["textures/AJTHD3.png"] = dead.png()


def clock_trim():
    """MAP21: the trim of a frame that takes only the clocked door."""
    im = Img(64, 64, IVORY)
    im.noise(4, 2110)
    for y in range(0, 64, 32):
        im.rect(0, y, 64, y + 2, shade(BRASS, 0.6))
        im.rect(0, y + 2, 64, y + 3, shade(BRASS, 1.2))
        im.disc(31.5, y + 16, 11, shade(BRASS, 0.7))
        im.disc(31.5, y + 16, 9, (244, 238, 222))
        for k in range(12):                                     # the hours
            a = k * math.pi / 6
            im.set(round(31.5 + 7 * math.cos(a)), round(y + 16 + 7 * math.sin(a)), INK)
        im.rect(31, y + 9, 33, y + 17, INK)                     # ten to two
        im.rect(32, y + 15, 38, y + 17, INK)
    return im


def desk_panel(live):
    """MAP21: the machine desk's lower face, 64 by 40. Then: two key switches
    (1 and 2) and a lamp between them; now: smashed."""
    im = Img(64, 40, (150, 156, 160) if live else (78, 74, 66))
    im.noise(5 if live else 12, 2120 + live)
    im.frame(0, 0, 64, 40, (84, 86, 90), 2)
    rnd = random.Random(2130)
    if live:
        for cx, n in ((16, 1), (48, 2)):
            im.disc(cx, 22, 7, (60, 62, 66))
            im.disc(cx, 22, 5, (200, 196, 170))
            im.rect(cx - 1, 16, cx + 1, 28, (40, 40, 44))      # the key's slot
            for k in range(n):                                  # its number as dots
                im.disc(cx - 3 * (n - 1) + 6 * k, 7, 1, INK)
        im.disc(32, 22, 3, (200, 60, 40))                       # the lamp
    else:
        for cx in (16, 48):
            im.disc(cx, 22, 7, (24, 20, 18))                    # holes where the switches were
            for _ in range(14):
                im.set(cx + rnd.randint(-9, 9), 22 + rnd.randint(-9, 9), (40, 34, 28))
        for x in range(4, 60):                                  # a crack across it
            im.set(x, 12 + (x * 7 // 13) % 9, (30, 26, 22))
    return im


def make_longrun(out):
    tr = clock_trim()
    out["textures/AJCKTR.png"] = tr.png()
    out["flats/AJCKTF.png"] = tr.png()
    out["textures/AJTHK2.png"] = desk_panel(True).png()
    out["textures/AJTHK3.png"] = desk_panel(False).png()
