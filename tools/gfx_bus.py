"""MAP10's bus (ajarmap.bus): the flat red outline of a bus standing at its
stop, after the teleporter bus of "Гостья из будущего" (1984), and the route
board beside it (ajarmap.route_board). Provisional, like every level's look
before its board: a dark body, a red outline, a number over each door.

AJBUS    64x144  the body between two doors: a window, the red outline
AJBUSZ   48x144  an end of the body
AJBUSF  144x144  its front: the windscreen, the lamps, the number
AJBUSR  144x144  its back
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
# a livery: the letter in its textures' names (AJ?US...), its line, its number
LIVERIES = (("B", RED, "10"), ("C", (236, 180, 48), "20"))


def _outline(im, w, RED, left=False, right=False):
    """The red line round the bus: along its roof and its skirt, and down an end."""
    im.rect(0, 0, w, 4, RED)
    im.rect(0, H - 22, w, H - 19, RED)
    if left:
        im.rect(0, 0, 4, H - 19, RED)
    if right:
        im.rect(w - 4, 0, w, H - 19, RED)


def make(out):
    for L, line, num in LIVERIES:
        body = Img(64, H, BODY)
        body.rect(6, 54, 58, 96, GLASS)                               # a window
        body.frame(6, 54, 58, 96, line, 2)
        body.rect(6, 62, 58, 63, shade(GLASS, 1.25))
        body.rect(0, H - 19, 64, H, (20, 20, 24))                     # under the skirt
        _outline(body, 64, line)
        body.noise(4, 101)
        out[f"textures/AJ{L}US.png"] = body.png()

        end = Img(48, H, BODY)
        end.rect(0, H - 19, 48, H, (20, 20, 24))
        end.disc(24, H - 18, 17, (16, 16, 18))                        # a wheel
        end.disc(24, H - 18, 8, (120, 120, 126))
        end.rect(10, 54, 38, 96, GLASS)
        end.frame(10, 54, 38, 96, line, 2)
        _outline(end, 48, line, left=True, right=True)
        end.noise(4, 102)
        out[f"textures/AJ{L}USZ.png"] = end.png()

        front = Img(144, H, BODY)
        front.rect(0, H - 19, 144, H, (20, 20, 24))
        front.rect(12, 34, 132, 88, GLASS)                            # the windscreen
        front.frame(12, 34, 132, 88, line, 2)
        front.rect(71, 34, 73, 88, line)
        front.rect(12, 44, 132, 45, shade(GLASS, 1.25))
        front.rect(48, 10, 96, 28, (12, 12, 14))                      # the number
        front.frame(48, 10, 96, 28, line, 2)
        digit(front, num[0], 60, 13, CREAM, 2)
        digit(front, num[1], 74, 13, CREAM, 2)
        for cx in (24, 120):                                          # lamps
            front.disc(cx, 106, 9, CREAM)
            front.disc(cx - 2, 104, 4, (255, 250, 230))
        front.rect(44, 98, 100, 116, (24, 24, 28))                    # the grille
        for gy in range(101, 116, 4):
            front.rect(46, gy, 98, gy + 1, (70, 70, 76))
        _outline(front, 144, line, left=True, right=True)
        front.noise(4, 103)
        out[f"textures/AJ{L}USF.png"] = front.png()

        back = Img(144, H, BODY)
        back.rect(0, H - 19, 144, H, (20, 20, 24))
        back.rect(28, 40, 116, 78, GLASS)                             # the back window
        back.frame(28, 40, 116, 78, line, 2)
        for cx in (16, 128):                                          # tail lamps
            back.rect(cx - 5, 96, cx + 5, 116, (200, 30, 26))
            back.rect(cx - 5, 96, cx + 5, 101, (240, 150, 40))
        back.rect(40, 92, 104, 118, (24, 24, 28))                     # the engine's cover
        back.frame(40, 92, 104, 118, (70, 70, 76), 1)
        for gx in range(46, 100, 6):
            back.rect(gx, 96, gx + 2, 114, (60, 60, 66))
        _outline(back, 144, line, left=True, right=True)
        back.noise(4, 104)
        out[f"textures/AJ{L}USR.png"] = back.png()

        for n in range(10):                                           # 0: a door with no number
            top = Img(64, 48, BODY)
            top.rect(0, 0, 64, 4, line)
            top.rect(10, 12, 54, 40, (12, 12, 14))                    # the destination board
            top.frame(10, 12, 54, 40, line, 2)
            if n:
                digit(top, str(n), 26, 16, CREAM, 4)
            top.noise(4, 110 + n)
            out[f"textures/AJ{L}N{n}.png"] = top.png()

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
