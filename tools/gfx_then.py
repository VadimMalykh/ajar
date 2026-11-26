"""The then and now lab's own pictures (map THEN, tools/map_then.py).

  AJTHL2, AJTHL3   a lever on the lab wall of MAP11's look 2 (Thaw, THEN) and
                   look 3 (Post Box, NOW), 256 high, the lever at hand height
                   from the floor (lay it with dontpegbottom); both switches
  AJTHD3           the same place NOW where a fixture's lever was: its plate
                   rusted, the lever gone, two bolt holes (does nothing)
The clocked door is gfx.py's (door(CLOCKED)); the heap's crates are MAP17's
(AJDSTOR, AJDSTOF); a burnt hole's edges are Doom's ASHWALL2.
"""
import random

from gfx import levers, lever, unpng, shade


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
