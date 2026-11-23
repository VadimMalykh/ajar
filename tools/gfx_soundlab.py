"""The sound lab's switches (tools/map_soundlab.py, map SOUND): 64 wide and as
tall as its room (192), on the plain wall: a sign with what the switch does
and under it a round push-button in a steel plate, one colour for each pair.
AJSNDT takes (TAKE), AJSNDS sets (SET), AJSNDP and AJSNDM step the music on
and back (MUSIC + and MUSIC -)."""
from gfx import Img, DIGITS, shade

GLYPHS = dict(DIGITS)
GLYPHS.update({"K": ("10001", "10010", "11100", "10010", "10001"),
               "+": ("00000", "00100", "01110", "00100", "00000")})
H = 192             # the room's height: the texture is laid from the ceiling down
TAKE, SET, MUSIC = (196, 70, 56), (64, 110, 210), (60, 160, 90)


def write(im, s, y, c, scale=2):
    """Capitals centred across the texture, top at y."""
    w = len(s) * 6 * scale - scale
    x0 = (im.w - w) // 2
    for n, ch in enumerate(s):
        for j, row in enumerate(GLYPHS[ch]):
            for i, on in enumerate(row):
                if on == "1":
                    x, yy = x0 + n * 6 * scale + i * scale, y + j * scale
                    im.rect(x, yy, x + scale, yy + scale, c)


def switch(wall, words, colour):
    im = Img(64, H)                                              # (the wall is 128 wide: its left half)
    im.px = [list(wall.px[(y % wall.h) * wall.w + x]) for y in range(H) for x in range(64)]
    ink, card = (24, 24, 28), (236, 230, 212)
    top = 74 if len(words) == 2 else 82                          # the sign, at eye height
    bottom = 112
    im.rect(3, top - 1, 61, bottom + 1, shade(colour, 0.5))
    im.rect(4, top, 60, bottom, card)
    im.rect(4, top, 60, top + 3, colour)
    im.rect(4, bottom - 3, 60, bottom, colour)
    y = top + 7
    for k, w in enumerate(words):
        write(im, w, y, ink, 2 if k == 0 else 3)
        y += 14
    cy = 140                                                     # the button, at hand height (52 above the floor)
    iron, rim = (70, 72, 78), (150, 152, 160)
    im.rect(15, cy - 17, 49, cy + 17, (30, 28, 26))
    im.rect(16, cy - 16, 48, cy + 16, rim)
    im.rect(18, cy - 14, 46, cy + 14, iron)
    im.disc(32, cy, 10, shade(colour, 0.45))
    im.disc(32, cy, 8, colour)
    im.disc(29, cy - 3, 2, shade(colour, 1.5))
    for x, yy in ((19, cy - 13), (44, cy - 13), (19, cy + 12), (44, cy + 12)):
        im.rect(x, yy, x + 2, yy + 2, (40, 40, 44))              # its screws
    return im


def make(out, wall):
    for name, words, c in (("AJSNDT", ("TAKE",), TAKE), ("AJSNDS", ("SET",), SET),
                           ("AJSNDP", ("MUSIC", "+"), MUSIC), ("AJSNDM", ("MUSIC", "-"), MUSIC)):
        out[f"textures/{name}.png"] = switch(wall, words, c).png()
