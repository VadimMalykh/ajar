"""MAP24 "Left Hanging": its one picture of its own (tools/map_lefthanging.py).
The notice THEN over the first frame 121, where the old GREEN hangs: ON TEST.
DO NOT REMOVE., on a card pinned to the test room's wall (look 2, LA), as
MAP21's notice (gfx_longrun.notice) is. It is the wall over the frame (an
upper, laid from the ceiling at 256: the frame's head is at 96, so rows 0 to
160 show), the card at rows 62 to 116, 140 to 194 over the floor."""
import gfx_institute as GI
from gfx import text

NOTICE = "AJLHN0"                                   # the texture's name (map_lefthanging hangs it)
LOOK, PART, SHIFT = 2, "LA", 16                     # THEN's look, the test room's wall, where 512, 688..752 starts
LINES = [("ON TEST.", "r"), ("-", "r"), ("DO NOT", "b"), ("REMOVE.", "b")]


def words(im, s, x, y, c):
    """text() at its smallest, with the full stops the font has not got."""
    text(im, s.replace(".", " "), x, y, c, 1)
    for n, ch in enumerate(s):
        if ch == ".":
            im.rect(x + n * 6, y + 4, x + n * 6 + 1, y + 5, c)


def notice():
    im = GI.on_wall(LOOK, PART, 64, SHIFT)
    red, blue, card = (196, 36, 30), (36, 64, 140), (248, 248, 244)
    x1, y1, x2, y2 = 5, 62, 59, 116
    im.rect(x1 + 1, y1 + 1, x2 + 1, y2 + 1, (40, 40, 40))       # its shadow on the wall
    im.rect(x1, y1, x2, y2, card)
    im.frame(x1, y1, x2, y2, red, 1)
    im.rect(x1 + 2, y1 + 2, x2 - 2, y1 + 4, blue)
    y = y1 + 9
    for s, c in LINES:
        if s == "-":
            im.rect(14, y + 1, 50, y + 2, red)
            y += 7
            continue
        w = len(s) * 6 - 1
        words(im, s, 32 - w // 2, y, red if c == "r" else blue)
        y += 10
    im.rect(x1 + 2, y2 - 4, x2 - 2, y2 - 2, blue)
    im.disc(32, y1 - 0.5, 1.5, (80, 80, 84))                     # the pin
    return im


def make(out):
    out[f"textures/{NOTICE}.png"] = notice().png()
