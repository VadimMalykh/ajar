"""MAP18's own art in MAP11's institute (gfx_institute.py): the sign of a
one-sided doorway. AJIY<look><nn>, 64 wide, is the room's wall (laid as the
wall beside it lies: `shift`; `reps` times over, for a wall higher than its
texture) with a plate 32 x 32 on it, its top `top` rows under the top; on it, in the institute's sign colours, a doorway that
an arrow goes into straight and comes out of turned, to somewhere else: this
doorway does not lead back the way you came. No words. The map asks for
each one it hangs (map_clockdept.SIGNPLATES, map_clockdept.sign).
"""
from gfx import Img, shade
from gfx_institute import PLATE, on_wall

# the pictogram, 28 x 28 inside the plate's rim: # ink, + the doorway's dark inside
PICTO = [
    "....................##......",
    "...................####.....",
    "..................######....",
    ".................########...",
    "................##########..",
    "....................##......",
    "....................##......",
    "....................##......",
    "..........########..##......",
    "..........########..##......",
    "..........##++++##..##......",
    "..........##++++##..##......",
    "..........##++++##..##......",
    ".....#....##++++##..##......",
    ".....##...##++++##..##......",
    ".....###..##++++##..##......",
    ".....####.##++++##..##......",
    "############++++######......",
    "############++++######......",
    ".....####.##++++##..........",
    ".....###..##++++##..........",
    ".....##...##++++##..........",
    ".....#....##++++##..........",
    "..........##++++##..........",
    "..........##++++##..........",
    "..........##++++##..........",
    "..........##++++##..........",
    "............................",
]


def plate_sign(n, part, shift, top, reps=1):
    one = on_wall(n, part, 64, shift)
    im = Img(64, one.h * reps)
    im.px = [list(p) for _ in range(reps) for p in one.px]
    ground, ink = PLATE[n]
    rim = shade(ink, 0.8) if n != 3 else (90, 84, 70)
    dark = shade(ground, 0.55) if n != 1 else (14, 12, 14)
    x0, y0 = 16, top
    im.rect(x0 + 1, y0 + 1, x0 + 33, y0 + 33, shade((40, 38, 36), 1))             # its shadow on the wall
    im.rect(x0, y0, x0 + 32, y0 + 32, ground)
    im.frame(x0, y0, x0 + 32, y0 + 32, rim, 1)
    for y, row in enumerate(PICTO):
        for x, ch in enumerate(row):
            if ch == "#":
                im.set(x0 + 2 + x, y0 + 2 + y, ink)
            elif ch == "+":
                im.set(x0 + 2 + x, y0 + 2 + y, dark)
    for sx, sy in ((x0 + 2, y0 + 2), (x0 + 29, y0 + 2), (x0 + 2, y0 + 29), (x0 + 29, y0 + 29)):    # four screws
        im.set(sx, sy, rim)
    im.noise(2, 1977 + n)
    return im


def make(out, plates):
    """`plates`: {(look, wall, shift, top, reps): name} (map_clockdept.SIGNPLATES)."""
    for (n, part, shift, top, reps), nm in plates.items():
        key = f"textures/{nm}.png"
        assert key not in out, key
        out[key] = plate_sign(n, part, shift, top, reps).png()


if __name__ == "__main__":
    # swatches: python3 tools/gfx_clockdept.py <dir>  (every look, on the three walls MAP18 hangs it on)
    import os
    import sys
    os.makedirs(sys.argv[1], exist_ok=True)
    for n in (1, 2, 3):
        for part, shift, top, reps in (("CO", 0, 124, 1), ("PU", 32, 316, 2), ("CK", 0, 92, 1)):
            with open(os.path.join(sys.argv[1], f"sign{n}{part}.png"), "wb") as f:
                f.write(plate_sign(n, part, shift, top, reps).png())
