"""The left-handed room lab's own textures (tools/map_lefthand.py, map LEFT).
Each has a clear left and right, so that a copy that is not flipped, or not
lined up, shows at a glance:
  AJLBWALL  the room's wall, 64 x 128: pale plaster, a dark stripe near the
            left edge of each panel and a red triangle pointing right
  AJLBPLAQ  the south wall's plaque, 128 x 192: the wall with a brass plate
            "ROOM 20" over an arrow pointing right
  AJLBFLOR  the floor, 64 x 64: tiles with an F in one corner
  AJLBSTEP  the step's top, 64 x 64: a green flat with a stripe at a slant
And flip_all (tools/lefthand.py) makes the flipped copies the map asks for."""
from gfx import Img, shade, text
import lefthand

PLASTER, STRIPE, MARK = (196, 188, 170), (70, 64, 58), (190, 40, 40)


def wall():
    im = Img(64, 128, PLASTER)
    im.noise(6, 71)
    im.rect(6, 0, 10, 128, STRIPE)             # the stripe, near the left
    im.rect(0, 0, 64, 2, shade(PLASTER, 0.7))  # a joint at the top of each panel
    for y in range(8):                          # a triangle pointing right, top left
        im.rect(16, 12 + y, 16 + y + 1, 13 + y, MARK)
        im.rect(16, 27 - y, 16 + y + 1, 28 - y, MARK)
    return im


def make(out):
    w = wall()
    out["textures/AJLBWALL.png"] = w.png()
    pl = Img(128, 192)
    pl.px = [list(w.px[(y % 128) * 64 + x % 64]) for y in range(192) for x in range(128)]
    brass, ink = (200, 170, 90), (40, 30, 20)
    pl.rect(10, 52, 118, 112, shade(brass, 0.6))
    pl.rect(12, 54, 116, 110, brass)
    text(pl, "ROOM 20", 22, 62, ink, 2)
    pl.rect(24, 86, 92, 92, ink)               # an arrow pointing right
    for i in range(10):
        pl.rect(92 + i, 80 + i, 93 + i, 98 - i, ink)
    out["textures/AJLBPLAQ.png"] = pl.png()
    fl = Img(64, 64, (120, 116, 110))
    fl.noise(5, 72)
    fl.frame(0, 0, 64, 64, (90, 86, 80))
    fl.rect(8, 8, 12, 28, (40, 40, 44))         # an F, top left
    fl.rect(8, 8, 22, 12, (40, 40, 44))
    fl.rect(8, 16, 18, 20, (40, 40, 44))
    out["flats/AJLBFLOR.png"] = fl.png()
    st = Img(64, 64, (70, 130, 80))
    st.noise(5, 73)
    for x in range(64):
        st.rect(x, (x // 2 + 4) % 64, x + 1, (x // 2 + 4) % 64 + 5, (220, 220, 200))
    out["flats/AJLBSTEP.png"] = st.png()


def flip(out):
    lefthand.flip_all(out)
