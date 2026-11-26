"""The then and now lab's own pictures (map THEN, tools/map_then.py).

  AJTHL2, AJTHL3   a lever on the lab wall of MAP11's look 2 (Thaw, THEN) and
                   look 3 (Post Box, NOW), 256 high, the lever at hand height
                   from the floor (lay it with dontpegbottom); both switches
  AJTHD3           the same place NOW where a fixture's lever was: its plate
                   rusted, the lever gone, two bolt holes (does nothing)
MAP21 (tools/map_longrun.py):
  AJCKTR, AJCKTF   the trim of a frame that takes only the clocked door: ivory
                   bands with a clock face in each 64 (wall and flat)
  AJTHK2, AJTHK3   the machine desk's panel, 64 by 40 (the desk's lower face):
                   then two key switches marked 1 and 2 and a lamp; now
                   smashed, the switches torn out
The clocked door is gfx.py's (door(CLOCKED)); the heap's crates are MAP17's
(AJDSTOR, AJDSTOF); a burnt hole's edges are Doom's ASHWALL2.
"""
import math
import random

from gfx import Img, levers, lever, unpng, shade, text

IVORY, BRASS, INK = (226, 218, 196), (190, 150, 70), (40, 34, 30)


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


def clock_trim():
    """MAP21: the trim of a frame that takes only the clocked door."""
    im = Img(64, 64, IVORY)
    im.noise(4, 2110)
    for y in range(0, 64, 32):
        im.rect(0, y, 64, y + 2, shade(BRASS, 0.6))
        im.rect(0, y + 2, 64, y + 3, shade(BRASS, 1.2))
        im.disc(31.5, y + 16, 11, shade(BRASS, 0.7))
        im.disc(31.5, y + 16, 9, (244, 238, 222))
        for k in range(12):                                     # the hours
            a = k * math.pi / 6
            im.set(round(31.5 + 7 * math.cos(a)), round(y + 16 + 7 * math.sin(a)), INK)
        im.rect(31, y + 9, 33, y + 17, INK)                     # ten to two
        im.rect(32, y + 15, 38, y + 17, INK)
    return im


def desk_panel(live):
    """MAP21: the machine desk's lower face, 64 by 40. Then: two key switches
    (1 and 2) and a lamp between them; now: smashed."""
    im = Img(64, 40, (150, 156, 160) if live else (78, 74, 66))
    im.noise(5 if live else 12, 2120 + live)
    im.frame(0, 0, 64, 40, (84, 86, 90), 2)
    rnd = random.Random(2130)
    if live:
        for cx, n in ((16, 1), (48, 2)):
            im.disc(cx, 22, 7, (60, 62, 66))
            im.disc(cx, 22, 5, (200, 196, 170))
            im.rect(cx - 1, 16, cx + 1, 28, (40, 40, 44))      # the key's slot
            for k in range(n):                                  # its number as dots
                im.disc(cx - 3 * (n - 1) + 6 * k, 7, 1, INK)
        im.disc(32, 22, 3, (200, 60, 40))                       # the lamp
    else:
        for cx in (16, 48):
            im.disc(cx, 22, 7, (24, 20, 18))                    # holes where the switches were
            for _ in range(14):
                im.set(cx + rnd.randint(-9, 9), 22 + rnd.randint(-9, 9), (40, 34, 28))
        for x in range(4, 60):                                  # a crack across it
            im.set(x, 12 + (x * 7 // 13) % 9, (30, 26, 22))
    return im


def make_longrun(out):
    import gfx
    if gfx.CLOCKDOOR:                                            # a look of the board's (tools/gfx_clockdoor.py)
        import gfx_clockdoor
        tr, fl = gfx_clockdoor.trim(gfx.CLOCKDOOR)
    else:
        tr = fl = clock_trim()
    out["textures/AJCKTR.png"] = tr.png()
    out["flats/AJCKTF.png"] = fl.png()
    out["textures/AJTHK2.png"] = desk_panel(True).png()
    out["textures/AJTHK3.png"] = desk_panel(False).png()
    causes(out)


# === MAP21: the causes made readable (PLAN.md, "MAP21: the causes made readable") ===================
# Plain first versions, in the rooms' looks (the apparatus is restyled later).
#   AJ21Lnn(N)       a cause's lever THEN with its name plate over it (VALVE, BELT, BEAM), both states;
#   AJ21Dnn          the same NOW: the plate faded, the lever gone (AJTHD3's rust);
#   AJ21Fnn          NOW: the goods-in flap in the bay's west wall, shut, rusted (laid from the floor)
#   AJ21Pnn          the pipe on the pit's west wall, 512 high (its mouth 232 under the ceiling): THEN
#                    painted, NOW rusted
#   AJ21Bnn          the plan board on optics' north wall, 192 wide: the room as one faces it, the
#                    emitter (OFF) in the middle, A left, B top, C right (THEN's targets sit on it)
#   AJ21Snn          optics: a wall's letter (A, B, C) on a plate over where the beam strikes it
#   (nn: map_longrun.PICTURES, each laid as the wall around it)
#   AJ21FLP          THEN: the flap's strips (a middle texture, see through), 64 by 40
#   AJ21RAL, AJ21RAW THEN: the hatch's rail, posts and a bar / the bar only over the belt's end
#                    (middle textures, 256 high, laid from the ceiling at 216: the bar 34 to 40 over the
#                    bay's floor, over a crate's lid)
#   AJ21BT3, AJ21CT3, AJ21CS3   NOW: the belt rusted: its bed, its curbs' tops, their sides
#   sprites AJXS (the stream, 8 by 64, four frames), AJXP (the wet patch, flat), AJXW (the emitter's wreck)
RUST, RUST_D = (124, 70, 38), (70, 40, 24)


def _plated(look, part, shift, words):
    """The wall with a name plate where a lever's plate goes over it (rows 160 to 171)."""
    from gfx_institute import on_wall, plate
    im = on_wall(look, part, 64, shift)
    plate(im, words, 32, 160, look)
    if look == 3:                                                # faded NOW
        rnd = random.Random(2140 + len(words))
        for _ in range(60):
            x, y = rnd.randint(26 - 3 * len(words), 38 + 3 * len(words)), rnd.randint(160, 171)
            p = im.px[y * 64 + x]
            im.set(x, y, shade(p[:3], rnd.uniform(0.8, 0.95)))
    return im


def _dead(wall):
    """AJTHD3's dead lever, on `wall`."""
    dead = lever(wall, False, 256)
    cy = 256 - 52
    rnd = random.Random(77)
    for y in range(cy - 26, cy + 24):
        for x in range(18, 46):
            dead.set(x, y, shade(RUST, rnd.uniform(0.75, 1.15)))
    for y in (cy - 20, cy + 18):
        dead.disc(32, y, 2, (34, 26, 20))
    dead.rect(30, cy - 8, 34, cy + 10, shade(RUST, 0.6))
    return dead


def _flap(look, part, shift):
    """NOW: the goods-in flap, shut: a steel shutter 40 high at the wall's foot, rusted."""
    from gfx_institute import on_wall
    im = on_wall(look, part, 64, shift)
    rnd = random.Random(2150)
    top = 256 - 40
    for y in range(top, 256):
        for x in range(64):
            im.set(x, y, shade((96, 88, 80) if (y - top) % 8 else (60, 54, 48), rnd.uniform(0.85, 1.1)))
    im.rect(0, top - 3, 64, top, (60, 56, 52))                   # its lintel
    for _ in range(26):                                          # rust
        x, y = rnd.randint(0, 63), rnd.randint(top, 255)
        im.disc(x, y, rnd.uniform(1, 2.5), shade(RUST, rnd.uniform(0.8, 1.2)))
    return im


def _pipe(look, part, shift):
    """The pipe on the pit's west wall: down from the ceiling, its mouth 232 under it (z -16)."""
    from gfx_institute import on_wall
    w = on_wall(look, part, 64, shift)
    im = Img(64, 512)
    im.px = [list(w.px[(y % w.h) * 64 + x]) for y in range(512) for x in range(64)]
    now = look == 3
    c = RUST if now else (96, 122, 112)
    rnd = random.Random(2160 + look)
    for y in range(0, 226):
        for x in range(26, 38):
            f = 0.7 + 0.6 * math.sin((x - 25) / 13 * math.pi)        # round
            im.set(x, y, shade(c, f * (rnd.uniform(0.8, 1.15) if now else 1)))
        im.set(25, y, shade(c, 0.4))
        im.set(38, y, shade(c, 0.4))
    for y in range(24, 226, 64):                                 # flanges and their brackets
        im.rect(23, y, 41, y + 4, shade(c, 0.85))
        im.rect(18, y + 1, 23, y + 3, (60, 60, 60))
        im.rect(41, y + 1, 46, y + 3, (60, 60, 60))
    im.rect(22, 222, 42, 230, shade(c, 0.9))                     # the collar
    im.rect(22, 222, 42, 223, shade(c, 1.3))
    for y in range(229, 236):                                    # the mouth, open downwards
        half = 8 - abs(y - 232)
        im.rect(32 - half, y, 32 + half, y + 1, (16, 14, 12))
    if now:                                                      # rust run down the wall under it
        for k in range(5):
            x = 28 + k * 2 + rnd.randint(-1, 1)
            for y in range(236, 236 + rnd.randint(20, 70)):
                im.set(x, y, shade(RUST, rnd.uniform(0.6, 1.0)))
    return im


def _board(look, part, shift):
    """The plan board, 192 wide: the room as one faces it from the south wall's frame. Texture x is world
    x - 1472, row 216 - z: A (x 32, row 144), C (160, 144), B (108, 80), OFF (84, 144) are where the
    targets sit (map_longrun.BOARD_TARGETS)."""
    from gfx_institute import on_wall
    im = on_wall(look, part, 192, shift)
    now = look == 3
    ground, ink = ((196, 188, 158), (112, 100, 88)) if now else ((236, 236, 228), (40, 70, 130))
    im.rect(4, 32, 188, 230, shade(ground, 0.55))                # its frame
    im.rect(6, 34, 186, 228, ground)
    im.frame(31, 79, 162, 210, ink, 2)                           # the room
    im.disc(96, 144, 5, ink)                                     # the emitter
    for (x1, y1), (x2, y2) in (((90, 144), (34, 144)), ((102, 144), (159, 144)), ((96, 138), (96, 82))):
        n = max(abs(x2 - x1), abs(y2 - y1))
        for k in range(0, n, 4):                                 # its beams, dotted
            im.set(x1 + (x2 - x1) * k // n, y1 + (y2 - y1) * k // n, ink)
    text(im, "A", 10, 139, ink, 2)
    text(im, "C", 172, 139, ink, 2)
    text(im, "B", 83, 75, ink, 2)
    text(im, "OFF", 79, 160, ink, 2)
    text(im, "BEAM", 73, 40, ink, 2)
    if now:
        rnd = random.Random(2170)
        for _ in range(40):
            im.disc(rnd.randint(8, 184), rnd.randint(36, 226), rnd.uniform(2, 6), shade(ground, rnd.uniform(0.75, 0.9)))
        im.noise(10, 2171)
    return im


def _letter(look, part, shift, words):
    """Optics: a wall's letter on MAP11's plate, large, just over where the beam strikes it (laid from the
    ceiling at 216: its foot at row 158, z 58, over a burnt hole's head at 56)."""
    from gfx_institute import on_wall, plate
    im = on_wall(look, part, 64, shift)
    plate(im, words, 32, 137, look, 3)
    return im


def _rail(posts):
    """A middle texture 64 by 256, laid from the ceiling (216): a bar at rows 216 to 222 (z 0 to -6, 34 to
    40 over the bay's floor) and, with `posts`, a post at each end down to the floor."""
    im = Img(64, 256, (0, 0, 0, 0))
    steel, dark = (200, 170, 40), (120, 96, 20)
    im.rect(0, 216, 64, 222, steel)
    im.rect(0, 221, 64, 222, dark)
    for x in range(0, 64, 16):                                   # hazard stripes on the bar
        im.rect(x, 216, x + 6, 221, (40, 36, 30))
    if posts:
        for x in (0, 60):
            im.rect(x, 216, x + 4, 256, (150, 150, 150))
            im.rect(x + 3, 216, x + 4, 256, (90, 90, 90))
    return im


def causes(out):
    import map_longrun
    from gfx import levers
    from gfx_institute import on_wall
    for (kind, look, part, shift, words), nm in map_longrun.PICTURES.items():
        if kind == "L":
            levers(out, nm, _plated(look, part, shift, words), 256)
        elif kind == "D":
            out[f"textures/{nm}.png"] = _dead(_plated(look, part, shift, words)).png()
        elif kind == "F":
            out[f"textures/{nm}.png"] = _flap(look, part, shift).png()
        elif kind == "P":
            out[f"textures/{nm}.png"] = _pipe(look, part, shift).png()
        elif kind == "B":
            out[f"textures/{nm}.png"] = _board(look, part, shift).png()
        elif kind == "S":
            out[f"textures/{nm}.png"] = _letter(look, part, shift, words).png()
    strips = Img(64, 40, (0, 0, 0, 0))                           # the flap THEN: strips of dark rubber
    for x in range(1, 64, 8):
        strips.rect(x, 0, x + 6, 40, (34, 36, 40, 220))
        strips.rect(x, 0, x + 1, 40, (70, 72, 78, 220))
    strips.rect(0, 0, 64, 3, (90, 90, 96))
    out["textures/AJ21FLP.png"] = strips.png()
    out["textures/AJ21RAL.png"] = _rail(True).png()
    out["textures/AJ21RAW.png"] = _rail(False).png()
    rnd = random.Random(2180)
    bed = Img(64, 64, RUST_D)                                    # the belt NOW: its slats, rusted
    for y in range(0, 64, 8):
        bed.rect(0, y, 64, y + 6, RUST)
    bed.noise(14, 2181)
    for _ in range(30):
        bed.disc(rnd.randint(0, 63), rnd.randint(0, 63), rnd.uniform(1, 3), shade(RUST_D, rnd.uniform(0.7, 1.1)))
    out["flats/AJ21BT3.png"] = bed.png()
    top = Img(64, 64, (92, 80, 70))
    top.noise(16, 2182)
    out["flats/AJ21CT3.png"] = top.png()
    side = Img(64, 16, (86, 74, 64))
    side.rect(0, 0, 64, 2, (110, 96, 84))
    side.noise(14, 2183)
    out["textures/AJ21CS3.png"] = side.png()
    for k in range(4):                                           # the stream: a thin fall of water, four frames
        s = Img(8, 64, (0, 0, 0, 0))
        r = random.Random(2190 + k)
        for y in range(64):
            for x in range(1, 7):
                v = 0.5 + 0.5 * math.sin((y + 16 * k) * 0.45 + x * 1.7) * r.uniform(0.6, 1)
                s.set(x, y, (int(150 + 90 * v), int(180 + 70 * v), 255, int(110 + 100 * v) if 2 <= x <= 5 else 70))
        out[f"sprites/AJXS{'ABCD'[k]}0.png"] = s.png(grab=(4, 64))
    patch = Img(48, 48, (0, 0, 0, 0))                            # where it lands THEN: wet
    r = random.Random(2195)
    for _ in range(26):
        patch.disc(24 + r.randint(-12, 12), 24 + r.randint(-12, 12), r.uniform(4, 9), (30, 40, 48, 120))
    patch.disc(24, 24, 7, (24, 34, 44, 170))
    out["sprites/AJXPA0.png"] = patch.png(grab=(24, 24))
    import gfx_institute2
    wreck = gfx_institute2.emitter_lamp()                        # NOW: the emitter's wreck, rusted, its lens broken
    r = random.Random(2196)
    for i, p in enumerate(wreck.px):
        if p[3]:
            g = (p[0] + p[1] + p[2]) / 3 / 140
            wreck.px[i] = list(shade(RUST if r.random() < 0.55 else (88, 84, 78), g * r.uniform(0.7, 1.05))) + [255]
    wreck.disc(15, 18, 5, (22, 20, 18))
    for _ in range(6):
        wreck.set(15 + r.randint(-4, 4), 18 + r.randint(-4, 4), (120, 116, 110))
    wreck.rect(11, 2, 19, 6, (0, 0, 0, 0))                       # the handle gone
    out["sprites/AJXWA0.png"] = wreck.png(grab=(15, 58))
