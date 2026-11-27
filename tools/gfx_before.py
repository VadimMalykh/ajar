"""The three times lab's own pictures (map BEFORE, tools/map_before.py).

  AJTHL1   a lever on the wall of MAP11's look 1 (BEFORE's piers), 256 high,
           the lever at hand height from the floor (lay it with
           dontpegbottom); a switch, as AJTHL2 and AJTHL3
  AJTHD2   the same place THEN, ten years on, where a fixture's lever BEFORE
           was: its plate painted over in the wall's colour, the lever gone, two
           bolts left (does nothing). NOW the place is gfx_then's AJTHD3
The ten-year door is gfx.py's (door(TENYEAR)).
"""
import random

from gfx import levers, lever, unpng, shade


def make(out):
    levers(out, "AJTHL1", unpng(out["textures/AJILA1.png"]), 256)
    wall = unpng(out["textures/AJILA2.png"])
    dead = lever(wall, False, 256)
    cy = 256 - 52
    paint = wall.px[(cy % wall.h) * wall.w + 32][:3]
    rnd = random.Random(78)
    for y in range(cy - 26, cy + 24):                            # the plate, painted over with the wall
        for x in range(18, 46):
            dead.set(x, y, shade(paint, rnd.uniform(0.9, 1.0)))
    for x in range(18, 46):                                      # its edge, under the paint
        dead.set(x, cy - 26, shade(paint, 0.8))
        dead.set(x, cy + 23, shade(paint, 0.8))
    for y in range(cy - 26, cy + 24):
        dead.set(18, y, shade(paint, 0.8))
        dead.set(45, y, shade(paint, 0.8))
    for y in (cy - 20, cy + 18):
        dead.disc(32, y, 2, shade(paint, 0.6))                   # the bolts
    out["textures/AJTHD2.png"] = dead.png()
