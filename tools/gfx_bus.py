"""MAP10's bus (ajarmap.bus): the flat red outline of a bus standing at its
stop, after the teleporter bus of "Гостья из будущего" (1984), and the route
board beside it (ajarmap.route_board). Provisional, like every level's look
before its board: a dark body, a red outline, a number over each door.

AJBUS    64x144  the body between two doors: a window, the red outline
AJBUSZ   48x144  an end of the body
AJBNn    64x48   what is over door n (1..9): the number on a destination board
                 (0: a board with nothing on it)
AJRnc    16x128  the route board's lamp for door n (0..9; 0 is the shelter):
                 c is 0 (nothing runs), a door's colour 1..6, or 7 (a line
                 that always runs, or a Stray door)
"""
from gfx import Img, shade, digit, DOOR_COLOURS

RED = (214, 44, 36)
BODY = (38, 40, 50)
GLASS = (92, 112, 132)
CREAM = (232, 224, 200)
H = 144


def _outline(im, w, left=False, right=False):
    """The red line round the bus: along its roof and its skirt, and down an end."""
    im.rect(0, 0, w, 4, RED)
    im.rect(0, H - 22, w, H - 19, RED)
    if left:
        im.rect(0, 0, 4, H - 19, RED)
    if right:
        im.rect(w - 4, 0, w, H - 19, RED)


def make(out):
    body = Img(64, H, BODY)
    body.rect(6, 54, 58, 96, GLASS)                               # a window
    body.frame(6, 54, 58, 96, RED, 2)
    body.rect(6, 62, 58, 63, shade(GLASS, 1.25))
    body.rect(0, H - 19, 64, H, (20, 20, 24))                     # under the skirt
    _outline(body, 64)
    body.noise(4, 101)
    out["textures/AJBUS.png"] = body.png()

    end = Img(48, H, BODY)
    end.rect(0, H - 19, 48, H, (20, 20, 24))
    end.disc(24, H - 18, 17, (16, 16, 18))                        # a wheel
    end.disc(24, H - 18, 8, (120, 120, 126))
    end.rect(10, 54, 38, 96, GLASS)
    end.frame(10, 54, 38, 96, RED, 2)
    _outline(end, 48, left=True, right=True)
    end.noise(4, 102)
    out["textures/AJBUSZ.png"] = end.png()

    for n in range(10):                                           # 0: a door with no number
        top = Img(64, 48, BODY)
        top.rect(0, 0, 64, 4, RED)
        top.rect(10, 12, 54, 40, (12, 12, 14))                    # the destination board
        top.frame(10, 12, 54, 40, RED, 2)
        if n:
            digit(top, str(n), 26, 16, CREAM, 4)
        top.noise(4, 110 + n)
        out[f"textures/AJBN{n}.png"] = top.png()

    for n in range(10):
        for c in range(8):
            lamp = Img(16, 128, (30, 30, 36))
            lamp.frame(0, 0, 16, 128, (70, 66, 60), 1)
            digit(lamp, str(n), 5, 30, CREAM, 2)
            col = CREAM if c == 7 else DOOR_COLOURS[c] if c else (52, 52, 58)
            lamp.disc(8, 54, 5, col)
            if c:
                lamp.disc(7, 53, 2, shade(col, 1.3))
            out[f"textures/AJR{n}{c}.png"] = lamp.png()
