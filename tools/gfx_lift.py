"""The lift's buttons (ajarmap.lift_button, MAP12): AJLB<n>, 32 wide and 256
high, laid from the floor up: a strip of khaki steel trunking with a plate at
hand height that says which floor it sends the car to (0, 1, 2), and AJLBX,
the same with the plate torn off and bare wires: the car's own panel. AJLBF
is the emitter's (ajarmap.emitter, MAP13): the plate shows a lamp and its beam."""
from gfx import Img, digit, shade

KHAKI, CREAM, RED, DARK = (112, 116, 94), (222, 216, 190), (170, 44, 36), (30, 30, 32)


def button(n):
    im = Img(32, 256, KHAKI)
    im.noise(5, 31 + (n if isinstance(n, int) else 0))
    im.rect(0, 0, 1, 256, shade(KHAKI, 0.7))
    im.rect(31, 0, 32, 256, shade(KHAKI, 0.7))
    im.rect(1, 0, 2, 256, shade(KHAKI, 1.2))
    for y in range(24, 256, 64):                                   # the trunking's joints
        im.rect(2, y, 30, y + 1, shade(KHAKI, 0.7))
    cy = 256 - 52
    im.rect(3, cy - 22, 29, cy + 22, DARK)
    if n is None:                                                  # torn out
        for x, c in ((9, RED), (14, (200, 180, 60)), (20, (60, 90, 170))):
            im.rect(x, cy - 16, x + 1, cy + 6, c)
            im.rect(x, cy + 6, x + 3, cy + 7, c)
        return im
    im.rect(4, cy - 21, 28, cy + 21, CREAM)
    im.rect(4, cy - 21, 28, cy - 20, shade(CREAM, 1.1))
    if n == "F":                                                   # a lamp, and the beam out of it
        im.rect(7, cy - 15, 12, cy - 7, DARK)
        im.rect(12, cy - 12, 25, cy - 10, RED)
        for x in (15, 19, 23):
            im.rect(x, cy - 16, x + 1, cy - 14, RED)
            im.rect(x, cy - 8, x + 1, cy - 6, RED)
    else:
        digit(im, str(n), 11, cy - 17, RED, 3)
    im.disc(16, cy + 10, 6, DARK)                                  # the button
    im.disc(16, cy + 10, 4, RED)
    im.disc(15, cy + 9, 1, (240, 150, 130))
    return im


def make(out):
    for n in (0, 1, 2):
        out[f"textures/AJLB{n}.png"] = button(n).png()
    out["textures/AJLBF.png"] = button("F").png()
    out["textures/AJLBX.png"] = button(None).png()
