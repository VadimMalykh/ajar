"""The kennel lab's own pictures (map KENNEL, tools/map_kennel.py).

  AJKD A..J   a readout digit 0..9, amber on a dark plate (the scales below their
              mark), 16 by 24, a wall sprite (src/zscript/kennel.zs)
  AJKD K      the plate with no digit (a leading place)
  AJKD L..U   the digits 0..9 in green (the scales at or over their mark)
"""
from gfx import Img, digit

PLATE, RIM = (22, 20, 18), (70, 64, 56)
AMBER, GREEN = (236, 168, 40), (90, 230, 90)
FRAMES = "ABCDEFGHIJKLMNOPQRSTU"


def plate(ch, c):
    im = Img(16, 24, PLATE)
    im.frame(0, 0, 16, 24, RIM, 1)
    if ch != " ":
        digit(im, ch, 2, 2, c, 4)
    return im


def make(out):
    for k in range(10):
        out[f"sprites/AJKD{FRAMES[k]}0.png"] = plate(str(k), AMBER).png(grab=(8, 24))
        out[f"sprites/AJKD{FRAMES[11 + k]}0.png"] = plate(str(k), GREEN).png(grab=(8, 24))
    out["sprites/AJKDK0.png"] = plate(" ", AMBER).png(grab=(8, 24))
