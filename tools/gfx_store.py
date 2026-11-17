"""Candidate looks for MAP08, the department store (see AJAR_STORE in map_hinges8.py).

Three looks for the whole store, numbered 1 to 3. For look n (name = AJ8 + tag + n):
  Y    the front on the arcade, 640: rows count down from the sky's edge at 512.
       0..352 two upper floors under a cornice, 352..384 the fascia, 384..512
       the ground floor, 512..640 below ground. YA, YB with windows: a lit
       shop window under dark upper floors; a dark one under a lit office.
       YP its ground floor alone (128), for porches
  K    the back of the store, 640: the dock, the roof. KA its foot (128)
  L    lobby, 192          A  porches indoors, 128
  H    atrium, 448: clerestory (128), the gallery's wall (160), the ground
       floor's (160). GV what carries the gallery and the balcony (160)
  SH   door showroom, 320: two storeys of 160
  CO   cash office, 128
  TY toys, HB haberdashery, FU furniture, CH china, LN linen, CP carpets (all
     160; each with <n>1, <n>2: fitted shelves of what the department sells)
  LV the shutter's lever on the office wall, LC the shop window's in the cash
     office (each with its pulled state, <name>N)
  RL railing   V the side of a glass counter, VT its top
  WD tables (wall and flat), BN seats (wall and flat), PL stone: steps, the
     fountain's rim (wall and flat)
  flats: F lobby and atrium, P the way through them, FD the west wing's floor,
         FE the east wing's, FS showroom, FO cash office, FG gallery and
         balcony, FR roof, FL a lit skylight, FK the dock, FA the arcade, FT the
         way across it; CL lobby ceiling, CA atrium, CD departments, CS
         showroom, CP porches
The same in all three: AJ8XS the houses round the arcade (640; AJ8XSA with a lit
window), AJ8XT their foot (128), AJ8XP the goods passage (160), AJ8XN the kiosk
(112), AJ8XW the shop window from inside (112), AJ8XL the lamp store (112),
AJ8XD a door on show (96). AJTARG8 is the kiosk's wall with its bell. The
stockroom wears the museum's (AJ6XK), the boiler room AJ6XB.

A door's face is made for its own place in its wall: AJ8D<n><number> for a room
door, AJ8Z<n><number> for a bolted one, AJ8S<n><number> for the shutter. The
map says which it needs and names them (FACES in map_hinges8.py).

Every wall is 64 wide and the same mirrored, and the map lines them up by world
position (Map.align). What stands free in a room repeats every 16.
"""
import random

from gfx import Img, shade, BRASS, bell, levers, text
import gfx_theatre as th
import gfx_yard as gy
import gfx_museum as mu
from gfx_museum import st, mix, bare
from gfx_station import arch, copy

NAMES = {"1": "Emporium", "2": "Grand Magasin", "3": "Festival"}

IVORY, GILT, INK = (236, 230, 212), (204, 168, 84), (38, 36, 40)
GLASS, LAMP = (26, 32, 50), (240, 206, 130)
# 1: an emporium of the 1880s
BRICK, IRONG, OAK, CREAM = (132, 62, 48), (34, 64, 52), (96, 64, 38), (226, 214, 184)
# 2: a grand magasin of the 1900s
STONE, SEA, MAHOG, MARB = (226, 216, 192), (64, 128, 116), (98, 48, 32), (198, 198, 204)
# 3: a store of the 1950s
BUFFB, TURQ, TEAK, WHITE, CHAR, MUST, CORAL = ((206, 186, 150), (60, 164, 164), (150, 96, 52), (236, 234, 226),
                                               (50, 52, 58), (214, 170, 50), (226, 112, 92))


def _oak(field, fstyle, mark, **more):
    return st(field, fstyle, mark, OAK, "panel", (60, 40, 24), (40, 28, 18), CREAM, **more)


def _gilt(field, fstyle, mark, **more):
    return st(field, fstyle, mark, (236, 228, 208), "panel", GILT, (90, 60, 50), IVORY, **more)


LOOKS = {
    # an emporium of the 1880s: red brick and green cast iron, oak, encaustic tile, pressed tin
    "1": dict(
        hall=st((200, 186, 148), "plain", (200, 186, 148), OAK, "panel", (60, 40, 24), (40, 28, 18), CREAM,
                stile=IRONG, bead=GILT, frieze=IRONG, fz="stencil"),
        upper=_oak((150, 160, 128), "stripe", (136, 146, 114), stile=IRONG, bead=GILT),
        low=st((200, 186, 148), "plaster", (184, 170, 132), OAK, "boards", (60, 40, 24), (40, 28, 18), CREAM),
        lobby=_oak((40, 76, 60), "damask", (56, 94, 76), frieze=CREAM, fz="swag"),
        show=_oak((204, 190, 152), "panel", (176, 160, 122)),
        cash=st(OAK, "panel", (62, 40, 22), OAK, "boards", (60, 40, 24), (40, 28, 18), (70, 46, 28)),
        ty=_oak((214, 176, 84), "stripe", (198, 158, 68)),
        hb=_oak((166, 90, 96), "damask", (184, 108, 112)),
        fu=_oak((44, 80, 64), "damask", (58, 96, 78)),
        ch=_oak((46, 62, 104), "plain", (46, 62, 104), frieze=CREAM, fz="stencil"),
        ln=st((226, 222, 206), "tile", (198, 194, 178), (60, 100, 104), "concrete", (40, 70, 74), (30, 50, 54), CREAM),
        cp=_oak((112, 36, 40), "damask", (134, 54, 56)),
        wood=OAK, frame=BRASS, felt=(36, 64, 50), plinth=OAK, bench=(104, 34, 36), stonec=(176, 168, 150)),
    # a grand magasin of the 1900s: cream stone, sea-green iron and gilt, marble, mahogany, mosaic
    "2": dict(
        hall=st(IVORY, "panel", GILT, MARB, "marble", GILT, (70, 66, 70), IVORY, stile=SEA, bead=GILT,
                frieze=SEA, fz="swag"),
        upper=st(IVORY, "panel", (204, 194, 164), (226, 218, 198), "panel", GILT, (70, 66, 70), IVORY,
                 stile=SEA, bead=GILT),
        low=st((230, 222, 200), "panel", (200, 190, 160), MARB, "marble", GILT, (70, 66, 70), IVORY),
        lobby=st((226, 214, 186), "stripe", (208, 194, 160), MARB, "marble", GILT, (70, 66, 70), IVORY,
                 frieze=SEA, fz="swag"),
        show=_gilt((226, 218, 196), "panel", GILT),
        cash=st(MAHOG, "panel", (66, 30, 20), MAHOG, "boards", GILT, (40, 22, 16), IVORY),
        ty=_gilt((150, 186, 214), "stripe", (134, 170, 200)),
        hb=_gilt((176, 156, 200), "damask", (192, 174, 214)),
        fu=_gilt((170, 198, 176), "panel", (140, 170, 148)),
        ch=_gilt(IVORY, "panel", GILT, frieze=(150, 186, 214), fz="swag"),
        ln=_gilt((232, 196, 196), "stripe", (220, 180, 180)),
        cp=_gilt((150, 50, 70), "damask", (170, 70, 88)),
        wood=MAHOG, frame=GILT, felt=(60, 34, 44), plinth=MAHOG, bench=(64, 128, 116), stonec=MARB),
    # a store of the 1950s: buff brick, plate glass, turquoise mosaic, teak, lino, one colour to a department
    "3": dict(
        hall=st(WHITE, "plain", WHITE, TEAK, "boards", (190, 150, 100), CHAR, WHITE, stile=TURQ, bead=WHITE),
        upper=bare((244, 226, 150), stile=TURQ, bead=WHITE),
        low=bare((210, 204, 190)),
        lobby=st(TEAK, "slats", (108, 66, 34), TEAK, "boards", (190, 150, 100), CHAR, WHITE),
        show=bare(WHITE),
        cash=bare((130, 156, 140)),
        ty=bare(MUST), hb=bare(CORAL),
        fu=st(TEAK, "slats", (108, 66, 34), TEAK, "boards", (190, 150, 100), CHAR, WHITE),
        ch=bare(TURQ), ln=bare((220, 226, 232)), cp=bare((70, 72, 80), skirt=(20, 20, 24)),
        wood=TEAK, frame=(170, 174, 180), felt=(232, 230, 222), plinth=(236, 234, 226), bench=CORAL,
        stonec=(190, 186, 178)),
}

ROOMS = {"TY": "ty", "HB": "hb", "FU": "fu", "CH": "ch", "LN": "ln", "CP": "cp"}
ALIGNED = ("Y", "YA", "YB", "YP", "K", "KA", "L", "A", "H", "GV", "SH", "CO") + tuple(ROOMS)
SAME = ("AJ8XS", "AJ8XSA", "AJ8XT", "AJ8XP", "AJ8XN", "AJ8XW", "AJ8XL", "AJ6XK", "AJ6XB", "AJ6XC")
ALWAYS = {"AJ8XJ"}                      # laid by their place in the world in the plain level too


def aligned(n):
    return ({f"AJ8{t}{n}" for t in ALIGNED} | {f"AJ8{t}{n}{i}" for t in ROOMS for i in (1, 2)} | set(SAME))


def darken(im, y0, y1, f0, f1):
    for y in range(y0, y1):
        f = f0 + (f1 - f0) * (y - y0) / max(1, y1 - y0 - 1)
        for x in range(im.w):
            p = im.px[y * im.w + x]
            p[:3] = shade(p[:3], f)


def rows(dst, src, y, y0=0, y1=None):
    """Copies rows y0..y1 of `src` into `dst` from row y down."""
    y1 = src.h if y1 is None else y1
    for k in range(y1 - y0):
        dst.px[(y + k) * 64:(y + k + 1) * 64] = [list(p) for p in src.px[(y0 + k) * 64:(y0 + k + 1) * 64]]


# --- outdoors ------------------------------------------------------------------
_fronts = {}


def _base(n):
    """The front without windows: one bay, a pier on every 64."""
    if n in _fronts:
        return _fronts[n]
    if n == "1":                                                     # red brick, stone bands, green cast iron below
        im = th.brick(64, 640, BRICK, shade(BRICK, 0.6), 1301)
        im.rect(0, 0, 64, 8, shade(CREAM, 0.9))                      # coping
        for x in range(0, 64, 8):                                    # brick dentils under it
            im.rect(x, 8, x + 4, 16, shade(BRICK, 0.7))
        im.rect(0, 40, 64, 52, shade(CREAM, 0.92))                   # cornice
        im.rect(0, 50, 64, 52, shade(CREAM, 0.55))
        for y in (204, 344):                                         # a stone band under each floor
            im.rect(0, y, 64, y + 8, shade(CREAM, 0.9))
            im.rect(0, y + 7, 64, y + 8, shade(CREAM, 0.55))
        im.rect(0, 52, 5, 344, shade(BRICK, 1.14))                   # a brick pier
        im.rect(5, 52, 6, 344, shade(BRICK, 0.6))
        im.rect(0, 352, 64, 384, IRONG)                              # the fascia
        im.rect(0, 352, 64, 354, GILT)
        im.rect(0, 380, 64, 384, shade(IRONG, 0.5))
        im.rect(8, 362, 32, 374, shade(IRONG, 1.3))
        im.frame(8, 362, 32, 374, GILT, 1)
        im.rect(0, 384, 64, 512, shade(IRONG, 0.8))                  # the ground floor: iron
        im.rect(0, 384, 6, 512, IRONG)                               # a cast column
        im.rect(2, 384, 3, 512, shade(IRONG, 1.5))
        im.rect(0, 384, 8, 392, GILT)
        im.rect(0, 498, 8, 512, shade(IRONG, 0.6))
        gy.paste(im, th.brick(64, 128, shade(BRICK, 0.5), shade(BRICK, 0.3), 1302), 512)
        im.noise(5, 1303)
        gy.grime(im, 300, 344, 0.9)
    elif n == "2":                                                   # cream stone, a slate roof, iron and gilt
        im = Img(64, 640, STONE)
        mu.ashlar(im, 48, 352, STONE, step=24)
        for y in range(0, 40):                                       # the mansard: slates
            im.rect(0, y, 64, y + 1, shade((84, 92, 108), 0.7 + 0.3 * y / 40))
        for j, y in enumerate(range(0, 40, 8)):
            for x in range(4 if j % 2 else 0, 64, 8):
                im.rect(x, y, x + 1, y + 8, (56, 62, 76))
            im.rect(0, y + 7, 64, y + 8, (56, 62, 76))
        im.rect(0, 40, 64, 56, shade(STONE, 1.05))                   # cornice, with modillions
        im.rect(0, 53, 64, 56, shade(STONE, 0.6))
        for x in range(2, 64, 8):
            im.rect(x, 46, x + 4, 52, shade(STONE, 0.78))
        im.rect(0, 56, 7, 352, shade(STONE, 1.04))                   # a pilaster
        im.rect(7, 56, 8, 352, shade(STONE, 0.66))
        im.disc(3, 66, 3, GILT)
        im.rect(0, 204, 64, 212, shade(STONE, 0.9))
        im.rect(0, 211, 64, 212, shade(STONE, 0.6))
        im.rect(0, 352, 64, 384, SEA)                                # the fascia: iron, a gilt line of letters
        im.rect(0, 352, 64, 355, GILT)
        im.rect(0, 381, 64, 384, shade(SEA, 0.5))
        for x in range(10, 32, 5):
            im.rect(x, 363, x + 3, 373, GILT)
        im.rect(0, 384, 64, 512, shade(SEA, 0.75))
        im.rect(0, 384, 6, 512, SEA)
        im.rect(2, 384, 3, 512, shade(SEA, 1.4))
        im.rect(0, 496, 64, 512, (60, 58, 64))                       # a plinth of dark marble
        im.rect(0, 496, 64, 497, (130, 126, 134))
        darken(im, 512, 640, 0.7, 0.5)
        im.noise(4, 1304)
        gy.grime(im, 300, 352, 0.92)
    else:                                                            # buff brick over a band of mosaic and plate glass
        im = th.brick(64, 640, BUFFB, shade(BUFFB, 0.78), 1305, course=6)
        im.rect(0, 0, 64, 10, WHITE)                                 # a flat coping
        im.rect(0, 10, 64, 12, shade(WHITE, 0.5))
        for y in (64, 216):                                          # white concrete bands round the strips of window
            im.rect(0, y, 64, y + 6, WHITE)
            im.rect(0, y + 120, 64, y + 126, WHITE)
            im.rect(0, y + 125, 64, y + 126, shade(WHITE, 0.6))
        im.rect(0, 352, 64, 384, WHITE)                              # the fascia, a line of neon along it
        im.rect(0, 352, 64, 353, shade(WHITE, 0.6))
        im.rect(0, 366, 64, 369, CORAL)
        im.rect(0, 367, 64, 368, (255, 214, 200))
        im.rect(0, 382, 64, 384, CHAR)
        for y in range(384, 496, 4):                                 # mosaic
            for x in range(0, 64, 4):
                im.rect(x, y, x + 4, y + 4, shade(TURQ, random.Random(x * 7 + y).choice((0.82, 0.94, 1.0, 1.1))))
        im.rect(0, 496, 64, 512, (24, 24, 28))                       # black glass at the foot
        im.rect(0, 496, 64, 497, (90, 90, 96))
        darken(im, 512, 640, 0.7, 0.5)
        im.noise(4, 1306)
    _fronts[n] = gy.mirror(im)
    return _fronts[n]


def window(im, n, top, bottom, lit):
    """An upper window in the middle of a 64-wide bay."""
    glass = LAMP if lit else GLASS
    if n == "1":                                                     # a round-headed sash under a stone arch
        arch(im, 32, top - 6, 16, bottom, shade(CREAM, 0.9))
        arch(im, 32, top, 12, bottom, glass)
        im.rect(31, top, 33, bottom, IVORY)
        for y in range(top + 14, bottom, 26):
            im.rect(20, y, 44, y + 1, IVORY)
        im.rect(16, bottom, 48, bottom + 5, shade(CREAM, 0.9))
        im.rect(16, bottom + 4, 48, bottom + 5, shade(CREAM, 0.55))
    elif n == "2":                                                   # a wide bay of iron and glass, gilt at its head
        arch(im, 32, top, 22, bottom, SEA)
        arch(im, 32, top + 3, 19, bottom - 3, glass)
        for x in (20, 32, 44):
            im.rect(x - 1, top + 3, x + 1, bottom - 3, SEA)
        im.rect(13, top + 30, 51, top + 32, SEA)
        im.rect(13, (top + bottom) // 2 + 14, 51, (top + bottom) // 2 + 16, SEA)
        im.disc(32, top + 3, 3, GILT)
        im.rect(10, bottom, 54, bottom + 4, shade(STONE, 0.85))
    else:                                                            # a strip of steel windows from pier to pier
        top, bottom = top + 2, bottom - 4
        im.rect(0, top, 64, bottom, glass if lit else GLASS)
        for x in range(0, 64, 16):
            im.rect(x, top, x + 1, bottom, (200, 204, 208))
        im.rect(0, (top + bottom) // 2, 64, (top + bottom) // 2 + 1, (200, 204, 208))
        if lit:                                                      # a blind half down
            im.rect(1, top, 63, top + 30, (226, 214, 180))
    return im


def mannequin(im, cx, foot, dress, h=64):
    skin = (226, 190, 160)
    im.rect(cx - 1, foot - 14, cx + 1, foot, (60, 50, 40))           # its stand
    im.rect(cx - 5, foot - 2, cx + 5, foot, (60, 50, 40))
    for y in range(foot - h + 22, foot - 12):                        # a skirt
        half = 3 + (y - (foot - h + 22)) * 6 // (h - 34)
        im.rect(cx - half, y, cx + half + 1, y + 1, dress)
    im.rect(cx - 4, foot - h + 8, cx + 5, foot - h + 22, shade(dress, 1.15))
    im.rect(cx - 1, foot - h + 5, cx + 2, foot - h + 8, skin)
    im.disc(cx, foot - h + 2, 3, skin)


def display(im, n, lit):
    """The shop window of a bay, rows 392..488."""
    edge = {"1": GILT, "2": GILT, "3": (190, 194, 200)}[n]
    x0, y0, y1 = (8, 394, 488) if n != "3" else (2, 388, 494)
    im.rect(x0, y0, 64 - x0, y1, edge)
    if lit:
        for y in range(y0 + 2, y1 - 2):
            f = (y - y0) / (y1 - y0)
            im.rect(x0 + 2, y, 62 - x0, y + 1, mix((250, 226, 160), (180, 140, 90), f))
        im.rect(x0 + 2, y1 - 12, 62 - x0, y1 - 2, {"1": (110, 40, 44), "2": (60, 110, 100), "3": (236, 234, 226)}[n])
        mannequin(im, 32, y1 - 12, {"1": (60, 50, 90), "2": (190, 60, 80), "3": MUST}[n])
        for cx, c in ((17, (90, 60, 40)), (47, (90, 60, 40))):       # a hat on a stand each side
            im.rect(cx, y1 - 34, cx + 1, y1 - 12, (60, 50, 40))
            im.rect(cx - 5, y1 - 37, cx + 6, y1 - 34, c)
            im.rect(cx - 3, y1 - 42, cx + 4, y1 - 37, shade(c, 1.2))
    else:
        im.rect(x0 + 2, y0 + 2, 62 - x0, y1 - 2, GLASS)
        for i in range(30):                                          # the street's lamps in the glass
            im.set(x0 + 6 + i // 2, y1 - 20 - i, shade(GLASS, 1.8))
        mannequin(im, 32, y1 - 12, (44, 50, 70))
    if n == "1":                                                     # an awning rolled up under the fascia
        im.rect(6, 384, 58, 392, (150, 50, 44))
        im.rect(6, 390, 58, 392, shade((150, 50, 44), 0.6))
    return im


def front(n, win=0):
    im = copy(_base(n))
    if win:
        window(im, n, 72, 188, False)
        window(im, n, 228, 332, win == 2)
        display(im, n, win == 1)
        gy.mirror(im)
    return im


def back(n):
    """The back of the store, 640: what the dock and the roof see."""
    c = {"1": shade(BRICK, 0.82), "2": (176, 160, 130), "3": (190, 176, 150)}[n]
    im = th.brick(64, 640, c, shade(c, 0.62), 1310 + int(n), course=8 if n != "3" else 6)
    cop = {"1": (90, 84, 80), "2": shade(STONE, 0.9), "3": WHITE}[n]
    im.rect(0, 0, 64, 8, cop)
    im.rect(0, 8, 64, 10, shade(cop, 0.5))
    pipe = {"1": IRONG, "2": SEA, "3": (120, 124, 130)}[n]
    im.rect(0, 10, 3, 512, pipe)                                     # a downpipe on every 64
    im.rect(3, 10, 4, 512, shade(c, 0.5))
    for y in range(60, 512, 90):
        im.rect(0, y, 5, y + 3, shade(pipe, 0.6))
    if n == "1":                                                     # a blind arch of brick
        arch(im, 32, 380, 14, 470, shade(c, 0.8))
        im.rect(18, 470, 46, 474, (90, 84, 80))
    elif n == "2":                                                   # white glazed brick to head height
        for y in range(384, 512, 8):
            for x in range(0, 32, 16):
                im.rect(x + (8 if (y // 8) % 2 else 0), y, x + 15 + (8 if (y // 8) % 2 else 0), y + 7, (220, 222, 216))
        im.rect(0, 380, 64, 384, SEA)
        im.rect(0, 10, 3, 512, pipe)
    else:                                                            # a concrete band, a painted number
        im.rect(0, 376, 64, 384, (170, 168, 160))
        im.rect(22, 420, 42, 452, WHITE)
        im.rect(26, 424, 38, 448, CHAR)
        im.rect(29, 428, 35, 444, WHITE)
    im.rect(0, 500, 64, 512, shade(c, 0.55))
    darken(im, 512, 640, 0.7, 0.5)
    im.noise(5, 1314 + int(n))
    gy.grime(im, 420, 512, 0.82)
    return gy.mirror(im)


def street(lit):
    """The houses round the arcade, 640: shut shops under dark rooms."""
    c = (74, 62, 62)
    im = th.brick(64, 640, c, shade(c, 0.6), 1320)
    im.rect(0, 0, 64, 6, (40, 38, 42))
    darken(im, 6, 60, 0.6, 1.0)
    for k, top in enumerate((90, 230)):
        im.rect(20, top - 6, 44, top, (120, 112, 104))
        im.rect(22, top, 42, top + 76, LAMP if lit and k == 1 else GLASS)
        im.rect(31, top, 33, top + 76, (150, 146, 140))
        im.rect(22, top + 36, 42, top + 38, (150, 146, 140))
        if lit and k == 1:
            im.rect(23, top, 31, top + 76, (150, 70, 60))            # a curtain
        im.rect(18, top + 76, 46, top + 80, (120, 112, 104))
    im.rect(0, 352, 64, 380, (36, 44, 60))                           # a fascia nobody can read at this hour
    im.rect(0, 352, 64, 354, (100, 100, 110))
    for x in range(10, 32, 6):
        im.rect(x, 362, x + 4, 371, (90, 96, 116))
    im.rect(0, 380, 64, 500, (70, 74, 82))                           # a shutter down over the shop
    for y in range(384, 500, 6):
        im.rect(4, y, 60, y + 1, (40, 42, 48))
        im.rect(4, y + 1, 60, y + 2, (104, 108, 118))
    im.rect(0, 380, 4, 512, (46, 40, 40))
    im.rect(0, 500, 64, 512, (46, 40, 40))
    darken(im, 512, 640, 0.7, 0.5)
    im.noise(5, 1321)
    return gy.mirror(im)


# --- the atrium, the showroom ---------------------------------------------------------
def clerestory(n):
    """128: what is between the gallery's wall and the atrium's roof."""
    c = LOOKS[n]
    im = Img(64, 128, c["upper"]["field"])
    if n == "1":                                                     # arched lights between iron trusses
        im.rect(0, 0, 64, 128, (198, 186, 150))
        arch(im, 32, 22, 22, 118, IRONG)
        arch(im, 32, 26, 18, 114, GLASS)
        for x in (22, 32, 42):
            im.rect(x, 26, x + 1, 114, IRONG)
        im.rect(14, 70, 50, 72, IRONG)
        for i in range(18):                                          # the truss springs from every pier
            im.rect(0, i, 18 - i, i + 1, IRONG)
        im.rect(0, 0, 4, 128, IRONG)
        im.rect(0, 0, 64, 5, shade(IRONG, 0.6))
    elif n == "2":                                                   # coloured glass in iron, gilt above
        im.rect(0, 0, 64, 128, IVORY)
        im.rect(0, 0, 64, 12, GILT)
        im.rect(0, 12, 64, 14, shade(GILT, 0.5))
        arch(im, 32, 22, 24, 120, SEA)
        arch(im, 32, 26, 20, 116, (30, 44, 60))
        r = random.Random(1330)
        for y in range(30, 116, 12):
            for x in range(12, 32, 7):
                if (x - 32) ** 2 + (y - 46) ** 2 < 420 or y > 46:
                    im.rect(x, y, x + 6, y + 11, shade(r.choice(((60, 110, 120), (150, 110, 50), (110, 50, 70), (50, 80, 120))), 0.8))
        im.rect(31, 26, 33, 116, SEA)
        im.rect(0, 0, 5, 128, SEA)
        im.rect(5, 0, 6, 128, GILT)
    else:                                                            # a ribbon of window under a white beam
        im.rect(0, 0, 64, 128, WHITE)
        im.rect(0, 30, 64, 104, GLASS)
        for x in range(0, 64, 16):
            im.rect(x, 30, x + 1, 104, (200, 204, 208))
        im.rect(0, 66, 64, 67, (200, 204, 208))
        im.rect(0, 28, 64, 30, shade(WHITE, 0.6))
        im.rect(0, 104, 64, 108, TURQ)
        im.rect(0, 0, 4, 128, TURQ)
    darken(im, 0, 40, 0.6, 1.0)
    return im


def atrium(n):
    """448: the clerestory, the gallery's wall, the ground floor's."""
    c = LOOKS[n]
    im = Img(64, 448)
    rows(im, clerestory(n), 0)
    rows(im, mu.wall(c["upper"], 160, seed=40 + int(n)), 128)
    low = mu.wall(c["hall"], 160, seed=44 + int(n))
    rows(im, low, 288)
    im.field = (288 + low.field[0], 288 + low.field[1])
    edge = c["hall"]["rail"]                                         # where the gallery's floor meets the wall
    im.rect(0, 284, 64, 290, c["hall"]["skirt"])
    im.rect(0, 284, 64, 285, edge)
    return gy.mirror(im)


def showroom(n):
    """320: two storeys of the same wall, the balcony's floor between them."""
    c = LOOKS[n]
    w = mu.wall(c["show"], 160, seed=50 + int(n))
    im = Img(64, 320)
    rows(im, w, 0)
    rows(im, w, 160)
    im.rect(0, 156, 64, 162, c["show"]["skirt"])
    im.field = (160 + w.field[0], 160 + w.field[1])
    return gy.mirror(im)


def gallery_front(n):
    """What carries the gallery and the balcony, 160: fitted drawers, a deck edge."""
    c = LOOKS[n]
    wood = c["wood"]
    im = Img(64, 160, wood)
    deck = {"1": IRONG, "2": SEA, "3": WHITE}[n]
    im.rect(0, 0, 64, 12, deck)
    im.rect(0, 0, 64, 1, shade(deck, 1.3))
    im.rect(0, 9, 64, 10, GILT if n != "3" else TURQ)
    im.rect(0, 12, 64, 15, (20, 20, 20))
    if n == "3":                                                     # pigeonholes of folded things
        for y in range(20, 150, 26):
            for x in (3, 18):
                im.rect(x, y, x + 13, y + 22, shade(wood, 0.4))
                im.rect(x + 1, y + 10, x + 12, y + 22, (WHITE, TURQ, MUST, CORAL)[(x + y) % 4])
                im.rect(x + 1, y + 15, x + 12, y + 16, CHAR)
    else:                                                            # drawers, a brass pull and a label each
        for y in range(20, 150, 22):
            for x in (3, 18):
                im.frame(x, y, x + 14, y + 20, shade(wood, 0.6), 1)
                im.rect(x + 1, y + 1, x + 13, y + 2, shade(wood, 1.3))
                im.rect(x + 4, y + 5, x + 10, y + 9, IVORY)
                im.rect(x + 5, y + 12, x + 9, y + 14, BRASS)
    im.rect(0, 152, 64, 160, shade(wood, 0.5))
    im.noise(4, 1340 + int(n))
    darken(im, 15, 34, 0.6, 1.0)
    return gy.mirror(im)


# --- what the departments sell ---------------------------------------------------------
BRIGHT = ((200, 60, 50), (60, 110, 190), (230, 190, 60), (70, 150, 90), (230, 230, 220), (220, 130, 60))


def _toys(im, r, x0, y, h, k):
    x = x0
    while x < 30:
        kind = r.choice("bBdt")
        c = r.choice(BRIGHT)
        if kind == "b":                                              # a ball
            im.disc(x + 4, y - 5, 4, c)
            im.rect(x + 1, y - 6, x + 8, y - 5, shade(c, 0.6))
            x += 10
        elif kind == "B":                                            # blocks
            im.rect(x, y - 6, x + 6, y, c)
            im.rect(x + 3, y - 12, x + 9, y - 6, r.choice(BRIGHT))
            im.rect(x + 6, y - 6, x + 12, y, r.choice(BRIGHT))
            x += 14
        elif kind == "d":                                            # a drum
            im.rect(x, y - 9, x + 9, y, c)
            im.rect(x, y - 9, x + 9, y - 7, GILT)
            im.rect(x, y - 2, x + 9, y, GILT)
            x += 11
        else:                                                        # a bear
            b = (150, 104, 60)
            im.disc(x + 5, y - 5, 5, b)
            im.disc(x + 5, y - 13, 3, b)
            im.set(x + 2, y - 16, b)
            im.set(x + 8, y - 16, b)
            im.set(x + 4, y - 13, INK)
            im.set(x + 6, y - 13, INK)
            x += 12


def _cloth(im, r, x0, y, h, k):
    x = x0
    if k % 2:                                                        # reels and cards of buttons
        while x < 30:
            c = r.choice(BRIGHT)
            for yy in range(y - 5, y - h + 4, -9):
                im.disc(x + 3, yy, 3, c)
                im.disc(x + 3, yy, 1, (200, 180, 140))
            x += 8
    else:                                                            # bolts of cloth, on end
        while x < 30:
            w, c = r.choice((4, 5, 6)), shade(r.choice(BRIGHT + ((120, 60, 110), (60, 70, 90))), r.choice((0.7, 0.9, 1.0)))
            im.rect(x, y - h + 4, min(31, x + w), y, c)
            im.rect(x, y - h + 4, x + 1, y, shade(c, 0.6))
            im.rect(x, y - h + 4, min(31, x + w), y - h + 6, (226, 220, 200))
            x += w + 1


def _mirrors(im, r, x0, y, h, k):
    if k % 2:                                                        # lengths of curtain
        for x in range(x0, 30, 7):
            c = shade(r.choice(((150, 60, 60), (70, 100, 80), (190, 160, 90), (70, 80, 120))), 0.9)
            for xx in range(x, min(31, x + 6)):
                im.rect(xx, y - h + 4, xx + 1, y, shade(c, 0.8 + 0.2 * abs(((xx - x) % 3) - 1)))
    else:                                                            # a chair on the shelf, a lamp
        c = r.choice(((120, 50, 50), (60, 100, 90), (190, 160, 90)))
        im.rect(x0 + 2, y - 10, x0 + 13, y - 6, c)
        im.rect(x0 + 2, y - 20, x0 + 5, y - 6, shade(c, 0.8))
        im.rect(x0 + 2, y - 6, x0 + 3, y, INK)
        im.rect(x0 + 12, y - 6, x0 + 13, y, INK)
        im.rect(x0 + 21, y - 14, x0 + 22, y, BRASS)
        for i in range(7):
            im.rect(x0 + 21 - i // 2 - 2, y - 21 + i, x0 + 22 + i // 2 + 2, y - 20 + i, LAMP)


def _china(im, r, x0, y, h, k):
    rim = r.choice(((60, 90, 170), (170, 60, 70), (70, 130, 100), GILT))
    x = x0
    while x < 29:
        if (x + k) % 3:                                              # a plate on edge
            im.disc(x + 5, y - 6, 5, (240, 238, 230))
            im.disc(x + 5, y - 6, 3, rim)
            im.disc(x + 5, y - 6, 2, (240, 238, 230))
            x += 12
        else:                                                        # a jug
            im.rect(x + 1, y - 11, x + 7, y, (240, 238, 230))
            im.rect(x + 1, y - 8, x + 7, y - 6, rim)
            im.rect(x + 7, y - 9, x + 9, y - 4, (240, 238, 230))
            x += 11


def _linen(im, r, x0, y, h, k):
    for x in range(x0, 28, 10):
        yy = y
        while yy - 4 > y - h + 3 + r.randrange(6):
            c = r.choice(((244, 242, 236), (226, 232, 240), (240, 226, 226), (230, 238, 220), (244, 236, 200)))
            im.rect(x, yy - 4, min(31, x + 9), yy, c)
            im.rect(x, yy - 1, min(31, x + 9), yy, shade(c, 0.78))
            yy -= 4


def _rugs(im, r, x0, y, h, k):
    for x in range(x0, 24, 14):                                      # rolled, on end; one hung open behind
        a, b = r.choice((((140, 40, 40), GILT), ((40, 60, 110), IVORY), ((60, 100, 70), GILT), ((150, 96, 50), INK)))
        im.rect(x, y - h + 3, x + 12, y, a)
        im.frame(x, y - h + 3, x + 12, y, b, 1)
        im.diamond(x + 6, y - h // 2, 4, b)
        im.diamond(x + 6, y - h // 2, 2, a)


GOODS = {"TY": _toys, "HB": _cloth, "FU": _mirrors, "CH": _china, "LN": _linen, "CP": _rugs}


def shelves(im, n, tag, k, seed):
    """A fitted case of shelves on the wall `im`, from under the frieze to the dado rail."""
    c, r = LOOKS[n], random.Random(seed)
    wood = c["wood"]
    f0, f1 = im.field
    y0, y1 = f0 + 6, f1 - 4
    im.rect(6, y0 + 3, 62, y1 + 3, shade(im.px[(y0 + 20) * 64 + 2][:3], 0.6))     # its shadow
    im.rect(4, y0, 60, y1, wood)
    im.rect(6, y0 + 4, 58, y1, shade(wood, 0.34) if n != "3" else (226, 224, 216))
    im.rect(4, y0, 60, y0 + 4, shade(wood, 1.2))
    step = (y1 - y0 - 4) // 3
    for i in range(3):
        y = y0 + 4 + step * (i + 1)
        GOODS[tag](im, r, 7, y - 3, step - 3, k + i)
        im.rect(4, y - 3, 60, y, wood)
        im.rect(4, y - 1, 60, y, shade(wood, 0.5))
    im.rect(4, y0, 6, y1, wood)
    return gy.mirror(im)


# --- floors, ceilings, furniture ----------------------------------------------------
def checker(a, b, step, seed):
    f = Img(64, 64, a)
    for i in range(0, 64, step):
        for j in range(0, 64, step):
            if (i + j) // step % 2:
                f.rect(i, j, i + step, j + step, b)
    f.noise(4, seed)
    return f


def flat(n, tag, seed):
    if tag == "F":                                                   # lobby and atrium
        if n == "1":                                                 # encaustic tile
            f = checker((196, 150, 96), (226, 210, 170), 16, seed)
            for cx in range(0, 65, 16):
                for cy in range(0, 65, 16):
                    f.diamond(cx, cy, 3, (40, 36, 40) if (cx + cy) // 16 % 2 else (120, 50, 40))
            return f
        if n == "2":                                                 # mosaic, a green border to every square
            f = th.flat("terrazzo", (226, 218, 196), (190, 180, 150), seed)
            f.frame(0, 0, 64, 64, SEA, 2)
            f.frame(4, 4, 60, 60, GILT, 1)
            f.diamond(32, 32, 7, SEA)
            f.diamond(32, 32, 4, (226, 218, 196))
            return f
        return checker((214, 212, 204), (150, 152, 156), 32, seed)   # big lino squares
    if tag == "P":                                                   # the way through
        if n == "1":
            return th.flat("carpet", (120, 36, 40), GILT, seed)
        if n == "2":
            return th.flat("carpet", (44, 100, 90), GILT, seed)
        return th.flat("carpet", CHAR, MUST, seed)
    if tag in ("FD", "FE", "FS", "FG"):
        if n == "1":
            a = {"FD": (110, 74, 44), "FE": (128, 90, 54), "FS": (140, 100, 60), "FG": (96, 64, 38)}[tag]
            return th.flat("boards", a, shade(a, 0.6), seed)
        if n == "2":
            if tag == "FE":
                return th.flat("carpet", (150, 70, 84), IVORY, seed)
            if tag == "FS":
                return checker((226, 220, 204), (60, 58, 64), 16, seed)
            a = (150, 96, 54) if tag == "FD" else (120, 70, 44)      # parquet, in squares
            f = Img(64, 64, a)
            for i in range(0, 64, 16):
                for j in range(0, 64, 16):
                    for k in range(0, 16, 4):
                        if (i + j) // 16 % 2:
                            f.rect(i + k, j, i + k + 1, j + 16, shade(a, 0.7))
                        else:
                            f.rect(i, j + k, i + 16, j + k + 1, shade(a, 0.7))
            f.noise(5, seed)
            return f
        if tag == "FD":
            return checker(TURQ, WHITE, 16, seed)
        if tag == "FE":                                              # cork
            f = Img(64, 64, (170, 126, 80))
            f.noise(14, seed)
            f.frame(0, 0, 64, 64, (140, 100, 62), 1)
            return f
        if tag == "FS":
            return th.flat("terrazzo", (200, 196, 186), (120, 116, 110), seed)
        return th.flat("boards", TEAK, shade(TEAK, 0.6), seed)
    if tag == "FO":
        return th.flat("carpet", {"1": (40, 74, 58), "2": (110, 40, 56), "3": (90, 110, 100)}[n], GILT if n != "3" else WHITE, seed)
    if tag == "FR":
        if n == "3":
            f = Img(64, 64, (120, 112, 100))
            f.noise(18, seed)
            return f
        return gy.flat("lead", seed)
    if tag == "FL":                                                  # a skylight, lit from below
        f = Img(64, 64, (236, 214, 150))
        f.noise(6, seed)
        bar = {"1": IRONG, "2": SEA, "3": (226, 226, 220)}[n]
        for i in range(0, 64, 16):
            f.rect(i, 0, i + 2, 64, bar)
            f.rect(0, i, 64, i + 2, bar)
        return f
    if tag == "FK":
        if n == "3":
            f = Img(64, 64, (140, 138, 130))
            f.noise(7, seed)
            f.rect(0, 0, 64, 1, (100, 98, 92))
            f.rect(0, 0, 1, 64, (100, 98, 92))
            return f
        return gy.flat({"1": "setts", "2": "cobbles"}[n], seed)
    if tag == "FA":
        return gy.flat({"1": "flags", "2": "slabs", "3": "flags"}[n], seed)
    if n == "1":                                                     # FT: the way across the arcade
        return gy.flat("tiles", seed)
    if n == "2":
        return th.flat("octagon", (226, 220, 204), (60, 110, 100), seed)
    return th.flat("terrazzo", (196, 190, 176), TURQ, seed)


def ceiling(n, tag, seed):
    if tag == "CP":
        if n == "1":
            return gy.ceiling((150, 116, 72), (90, 66, 40), 16, seed)
        if n == "2":
            return th.ceiling("coffer", (232, 226, 206), GILT, False, seed)
        f = Img(64, 64, shade(TEAK, 1.1))
        for x in range(0, 64, 8):
            f.rect(x, 0, x + 1, 64, shade(TEAK, 0.6))
        f.noise(4, seed)
        return f
    lamp = tag in ("CL", "CD", "CS")
    if n == "1":                                                     # pressed tin, painted cream
        f = Img(64, 64, CREAM)
        for i in (0, 32):
            for j in (0, 32):
                f.frame(i, j, i + 32, j + 32, shade(CREAM, 0.82), 1)
                f.frame(i + 5, j + 5, i + 27, j + 27, shade(CREAM, 0.9), 1)
                f.diamond(i + 16, j + 16, 6, shade(CREAM, 0.88))
                f.diamond(i + 16, j + 16, 3, CREAM)
        if tag == "CA":
            f.rect(0, 0, 64, 4, IRONG)
        if lamp:
            f.disc(32, 32, 5, BRASS)
            f.disc(32, 32, 3, (255, 244, 204))
        f.noise(3, seed)
        return f
    if n == "2":
        return th.ceiling("coffer", (236, 230, 212), GILT, lamp, seed)
    f = Img(64, 64, (232, 230, 222))                                 # acoustic tile
    for i in range(0, 64, 16):
        f.rect(i, 0, i + 1, 64, (204, 202, 194))
        f.rect(0, i, 64, i + 1, (204, 202, 194))
    for i in range(4, 64, 4):
        for j in range(4, 64, 4):
            if i % 16 and j % 16:
                f.set(i, j, (190, 188, 180))
    if lamp:
        f.rect(16, 28, 48, 36, (255, 252, 236))
        f.frame(16, 28, 48, 36, (170, 170, 164), 1)
    if tag == "CA":
        f.rect(0, 0, 64, 3, TURQ)
    f.noise(3, seed)
    return f


def railing(n):
    r = Img(64, 32, (0, 0, 0, 0))
    if n == "1":                                                     # cast iron, green, a gilt knob on every post
        r.rect(0, 0, 64, 3, OAK)
        r.rect(0, 0, 64, 1, shade(OAK, 1.4))
        r.rect(0, 29, 64, 32, IRONG)
        for x in range(0, 64, 8):
            r.rect(x + 3, 3, x + 5, 29, IRONG)
            r.disc(x + 4, 15, 2, IRONG)
        for x in range(0, 64, 32):
            r.rect(x, 3, x + 3, 29, shade(IRONG, 1.3))
            r.disc(x + 1, 5, 2, GILT)
    elif n == "2":                                                   # whiplash curves in green iron, a brass rail
        r.rect(0, 0, 64, 3, BRASS)
        r.rect(0, 0, 64, 1, shade(BRASS, 1.3))
        r.rect(0, 29, 64, 32, SEA)
        for x in range(0, 64, 16):
            r.rect(x, 3, x + 2, 29, SEA)
            for i in range(26):
                dx = int(5 * (1 - abs(i - 13) / 13) ** 0.5 * (1 if i < 13 else -1))
                r.set(x + 9 + dx, 3 + i, SEA)
                r.set(x + 8 - dx + 1, 3 + i, shade(SEA, 0.8))
            r.disc(x + 9, 16, 2, GILT)
    else:                                                            # a teak rail on thin steel, a panel of glass
        r.rect(0, 0, 64, 4, TEAK)
        r.rect(0, 0, 64, 1, shade(TEAK, 1.4))
        for x in range(0, 64, 32):
            r.rect(x, 4, x + 2, 32, (170, 174, 180))
        r.rect(0, 10, 64, 11, (170, 174, 180))
        r.rect(0, 30, 64, 32, (120, 124, 130))
        for x in range(2, 64, 4):
            for y in range(12, 30, 4):
                r.set(x, y, (150, 190, 200, 120))
    return r


def case(n, top):
    """A glass counter 40 high. Repeats every 16."""
    c = LOOKS[n]
    if top:
        f = Img(64, 64, c["felt"])
        f.noise(4, 1350 + int(n))
        dark = sum(c["felt"]) < 300
        for i in range(4):
            for j in range(4):
                x, y = i * 16 + 8, j * 16 + 8
                k = (i + 2 * j) % 4
                if k == 0:                                           # gloves
                    f.rect(x - 5, y - 2, x + 4, y + 3, (190, 150, 110))
                    f.rect(x - 5, y, x - 2, y + 1, c["felt"])
                elif k == 1:                                         # a watch
                    f.disc(x, y, 3, GILT)
                    f.disc(x, y, 2, IVORY)
                elif k == 2:                                         # a scarf, folded
                    f.rect(x - 5, y - 3, x + 5, y + 4, BRIGHT[(i + j) % 6])
                    f.rect(x - 5, y, x + 5, y + 1, shade(BRIGHT[(i + j) % 6], 0.7))
                else:                                                # a bottle of scent
                    f.rect(x - 2, y - 2, x + 3, y + 4, (200, 170, 90))
                    f.rect(x - 1, y - 4, x + 2, y - 2, INK)
        for k in range(-64, 64, 32):                                 # light on the glass
            for i in range(64):
                for d in (0, 1, 6):
                    x = k + i + d
                    if 0 <= x < 64:
                        p = f.px[i * 64 + x]
                        p[:3] = mix(p[:3], (255, 255, 255), 0.22 if dark else 0.5)
        return f
    wood = c["plinth"]
    im = Img(64, 64, wood)
    im.noise(4, 1354 + int(n))
    g = (40, 52, 60)
    im.rect(0, 0, 64, 15, g)
    for x in range(0, 64, 16):
        im.rect(x, 0, x + 1, 15, c["frame"])
        im.rect(x + 5, 8, x + 11, 13, BRIGHT[(x // 16) % 6])        # what lies on the shelf inside
        for i in range(10):
            im.set(x + 4 + i // 2, 12 - i, shade(g, 1.9))
    im.rect(0, 0, 64, 2, c["frame"])
    im.rect(0, 13, 64, 16, c["frame"])
    im.rect(0, 16, 64, 17, shade(wood, 0.5))
    for x in range(0, 64, 16):
        im.rect(x, 17, x + 1, 64, shade(wood, 0.78))
        if n != "3":
            im.frame(x + 3, 20, x + 14, 38, shade(wood, 0.7), 1)
    im.rect(0, 38, 64, 64, shade(wood, 0.7))
    return im


# --- the same in every look -------------------------------------------------------
def passage():
    """The goods passage, 160: two coats of paint on brick, a line between them."""
    im = th.brick(64, 160, (196, 190, 170), (170, 164, 146), 1360)
    for y in range(88, 160):
        for x in range(64):
            p = im.px[y * 64 + x]
            p[:3] = mix(p[:3], (60, 90, 80), 0.75)
    im.rect(0, 86, 64, 89, (30, 40, 36))
    im.rect(0, 150, 64, 160, (40, 40, 40))
    im.rect(0, 8, 64, 11, (120, 122, 126))                           # a pipe along under the ceiling
    im.rect(0, 8, 64, 9, (170, 172, 176))
    im.noise(5, 1361)
    gy.grime(im, 110, 160, 0.8)
    return gy.mirror(im)


def kiosk():
    """112: papers and magazines on their rails."""
    r = random.Random(1362)
    im = Img(64, 112, (60, 80, 70))
    for x in range(0, 64, 8):
        im.rect(x, 0, x + 1, 112, (44, 60, 52))
    for y in range(6, 100, 23):
        x = 2
        while x < 30:
            w = r.choice((7, 8, 9))
            c = r.choice(((226, 220, 200), (200, 60, 50), (60, 110, 190), (230, 190, 60), (226, 220, 200)))
            im.rect(x, y, min(31, x + w), y + 17, c)
            im.rect(x + 1, y + 2, min(30, x + w - 1), y + 5, INK if sum(c) > 500 else IVORY)
            im.rect(x + 1, y + 8, min(30, x + w - 1), y + 14, shade(c, 0.8))
            x += w + 1
        im.rect(0, y + 17, 64, y + 20, (150, 116, 72))
        im.rect(0, y + 19, 64, y + 20, (30, 26, 22))
    im.rect(0, 100, 64, 112, (40, 52, 46))
    im.noise(4, 1363)
    return gy.mirror(im)


def backdrop():
    """112: the shop window from inside: a curtain, and the back of a showcard."""
    c = (120, 44, 60)
    im = Img(64, 112, c)
    for x in range(64):
        im.rect(x, 0, x + 1, 112, shade(c, 0.62 + 0.38 * abs(((x % 16) - 8) / 8)))
    im.rect(0, 0, 64, 8, BRASS)
    im.rect(0, 8, 64, 10, shade(c, 0.4))
    for x in range(4, 64, 8):
        im.disc(x, 9, 2, shade(BRASS, 0.7))
    im.rect(0, 102, 64, 112, (60, 44, 34))
    im.noise(4, 1364)
    return gy.mirror(im)


def lamps():
    """112: the lamp store: shades on shelves, some of them lit."""
    r = random.Random(1365)
    im = Img(64, 112, (56, 46, 40))
    for y in range(4, 100, 34):
        for x in (9, 23):
            lit = r.random() < 0.6
            c = r.choice(((226, 196, 120), (200, 110, 90), (130, 170, 150), (226, 214, 190)))
            c = c if lit else shade(c, 0.45)
            for i in range(12):
                im.rect(x - 3 - i // 3, y + i, x + 4 + i // 3, y + i + 1, c)
            if lit:
                im.rect(x - 2, y + 4, x + 3, y + 9, (255, 246, 210))
            im.rect(x, y + 12, x + 1, y + 26, BRASS)
            im.rect(x - 3, y + 26, x + 4, y + 28, BRASS)
        im.rect(0, y + 28, 64, y + 32, (130, 100, 70))
        im.rect(0, y + 31, 64, y + 32, (26, 22, 18))
    im.rect(0, 104, 64, 112, (40, 32, 28))
    im.noise(4, 1366)
    return gy.mirror(im)


def show_door():
    """96: a door nobody has painted yet. No colour: it is not one of yours."""
    pine = (206, 178, 130)
    im = Img(64, 96, pine)
    for x in range(3, 64, 7):
        im.rect(x, 0, x + 1, 96, shade(pine, 0.92))
    im.frame(0, 0, 64, 96, shade(pine, 0.6), 3)
    for y1, y2 in ((10, 42), (50, 88)):
        for x1, x2 in ((9, 29), (35, 55)):
            im.frame(x1, y1, x2, y2, shade(pine, 0.7), 2)
            im.rect(x1 + 2, y1 + 2, x2 - 2, y1 + 3, shade(pine, 1.15))
    im.rect(4, 4, 14, 9, (236, 232, 220))                            # its ticket
    im.noise(5, 1367)
    return im


IRON = (58, 62, 70)


def glazing_bar():
    """What a glass roof's bars are made of: painted iron."""
    im = Img(64, 64, IRON)
    im.noise(4, 1500)
    for x in range(0, 64, 16):
        im.rect(x, 0, x + 1, 64, shade(IRON, 1.5))
        im.rect(x + 15, 0, x + 16, 64, shade(IRON, 0.6))
    return im


def lantern_side():
    """48: the upright of the atrium's lantern: small panes with the night
    behind them. It repeats every 16, so it meets itself at any corner."""
    im = Img(64, 48, GLASS)
    for y in range(6, 44):
        for x in range(64):
            im.set(x, y, shade((34, 42, 70), 0.75 + 0.5 * (44 - y) / 38))
    r = random.Random(1501)
    for _ in range(9):
        im.set(r.randrange(64), r.randrange(8, 40), (190, 196, 220))
    for x in range(0, 64, 16):
        im.rect(x, 0, x + 2, 48, shade(IRON, 1.3))
        im.rect(x + 14, 0, x + 16, 48, shade(IRON, 1.3))
        im.rect(x + 2, 6, x + 3, 44, shade(IRON, 0.5))
    im.rect(0, 0, 64, 6, IRON)
    im.rect(0, 5, 64, 6, shade(IRON, 0.5))
    im.rect(0, 24, 64, 26, shade(IRON, 1.2))
    im.rect(0, 44, 64, 48, shade(IRON, 1.5))
    im.rect(0, 47, 64, 48, shade(IRON, 0.5))
    return im


def gate():
    """160: the arcade's gate, shut for the night: iron bars with spear heads."""
    im = Img(64, 160, (0, 0, 0, 0))
    c = (40, 42, 48)
    for x in range(3, 64, 8):
        im.rect(x, 12, x + 2, 160, c)
        im.rect(x, 12, x + 1, 160, shade(c, 1.7))
        for i in range(8):                                           # a spear head
            im.rect(x - (i // 3), 4 + i, x + 2 + (i // 3), 5 + i, GILT if i < 6 else c)
    for y in (22, 96, 150):
        im.rect(0, y, 64, y + 4, c)
        im.rect(0, y, 64, y + 1, shade(c, 1.7))
    for x in range(7, 64, 16):                                       # scrolls between the rails
        for dy in range(0, 14):
            dx = int(3 * (1 - abs(dy - 7) / 7) ** 0.5)
            im.set(x + dx, 100 + dy, c)
            im.set(x + 7 - dx, 100 + dy, c)
    im.rect(0, 0, 2, 160, c)
    im.rect(62, 0, 64, 160, c)
    im.rect(26, 84, 38, 96, (70, 72, 80))                            # the lock
    im.disc(32, 90, 2, BRASS)
    return im


def road():
    """The street outside the arcade: setts, wet."""
    r = random.Random(1502)
    c = (62, 62, 68)
    im = Img(64, 64, shade(c, 0.6))
    for j in range(8):
        for i in range(-1, 6):
            x = i * 12 + (6 if j % 2 else 0)
            im.rect(x + 1, j * 8 + 1, x + 12, j * 8 + 8, shade(c, r.uniform(0.85, 1.15)))
    im.noise(5, 1503)
    return im


def roofs():
    """The roofs below the store's: slates, in courses."""
    c = (60, 66, 80)
    im = Img(64, 64, c)
    for j in range(8):
        im.rect(0, j * 8, 64, j * 8 + 1, shade(c, 0.6))
        for x in range(4 if j % 2 else 0, 64, 8):
            im.rect(x, j * 8, x + 1, j * 8 + 8, shade(c, 0.75))
    im.noise(5, 1504)
    return im


def skyline():
    """256 by 224: the town from the roof: roofs, gables and chimneys against
    the sky (clear above them), a window lit here and there. Solid in its
    lower 150 rows."""
    r = random.Random(1505)
    im = Img(256, 224, (0, 0, 0, 0))
    dark = (30, 30, 40)
    x = 0
    while x < 256:
        w = r.choice((24, 32, 40, 48))
        w = min(w, 256 - x)
        top = r.randrange(16, 70)
        c = shade(dark, r.uniform(0.8, 1.25))
        kind = r.choice(("flat", "gable", "gable", "hip"))
        for i in range(w):
            if kind == "gable":
                lift = int((w / 2 - abs(i - w / 2)) * 0.8)
            elif kind == "hip":
                lift = min(i, w - i, 10)
            else:
                lift = 0
            im.rect(x + i, top + 20 - lift, x + i + 1, 224, c)
        if kind != "flat":
            im.rect(x, top + 20, x + w, top + 22, shade(c, 1.5))     # the eaves
        for _ in range(r.randrange(1, 3)):                           # chimneys, with pots
            cx = x + r.randrange(3, max(4, w - 8))
            im.rect(cx, top, cx + 6, top + 24, shade(c, 0.8))
            im.rect(cx - 1, top, cx + 7, top + 2, shade(c, 1.4))
            im.rect(cx + 1, top - 5, cx + 3, top, (70, 44, 36))
            im.rect(cx + 4, top - 4, cx + 6, top, (70, 44, 36))
        for wy in range(top + 34, 200, 26):                          # windows
            for wx in range(x + 5, x + w - 8, 12):
                lit = r.random() < 0.13
                im.rect(wx, wy, wx + 6, wy + 10, LAMP if lit else (16, 18, 28))
                if lit:
                    im.rect(wx + 3, wy, wx + 4, wy + 10, shade(LAMP, 0.6))
        x += w
    return im


SIGN = {"1": (IRONG, GILT, GILT), "2": (SEA, GILT, IVORY), "3": (CHAR, WHITE, CORAL)}     # board, letters, a line


def sign(n, lines, w):
    """A sign hung from a canopy, `w` wide: the first line large, the rest small."""
    board, ink, rule = SIGN[n]
    h = 13 + 7 * (len(lines) - 1) + (5 if len(lines) > 1 else 3)
    im = Img(w, h, board)
    im.frame(0, 0, w, h, shade(board, 1.6), 1)
    text(im, lines[0], (w - (12 * len(lines[0]) - 2)) // 2, 3, ink, 2)
    if len(lines) > 1:
        im.rect(6, 15, w - 6, 16, rule)
    for i, line in enumerate(lines[1:]):
        text(im, line, (w - (6 * len(line) - 1)) // 2, 18 + 7 * i, ink, 1)
    return im


def plate(im, n, lines, bottom):
    """A small plate on the wall `im`, its foot at row `bottom`: what the room beyond sells."""
    board, ink, rule = SIGN[n]
    w = max(6 * len(line) - 1 for line in lines) + 6
    h = 7 * len(lines) + 4
    x0, y0 = (64 - w) // 2, bottom - h
    im.rect(x0, y0, x0 + w, y0 + h, board)
    im.frame(x0, y0, x0 + w, y0 + h, rule, 1)
    for i, line in enumerate(lines):
        text(im, line, (64 - (6 * len(line) - 1)) // 2, y0 + 3 + 7 * i, ink, 1)


def make(out, rd, faces={}, signs={}):
    """`rd` is the plain room door (leaf in its bottom 96 rows). `faces` is the
    door faces the map needs: {(look, kind "D", "Z" or "S", wall tag, shift,
    keys, plate): texture}; kind "O" is the wall over an open way, with its
    plate. `signs` is its hanging signs: {(look, lines, width): texture}."""
    def both(name, im):
        out[f"textures/{name}.png"] = out[f"flats/{name}.png"] = im.png()

    def tex(name, im):
        out[f"textures/{name}.png"] = im.png()
        return im

    T = 128
    sc = (132, 138, 148)
    steel = copy(rd)                                                 # a bolted door's leaf (as AJBOLT)
    steel.rect(0, T + 32, 64, T + 128, sc)
    steel.frame(0, T + 32, 64, T + 128, shade(sc, 0.5), 3)
    for y in (T + 44, T + 78, T + 112):
        steel.rect(3, y, 61, y + 3, shade(sc, 0.7))
        for x in (8, 32, 56):
            steel.disc(x, y + 1, 2, (200, 204, 210))
    steel.noise(5, 78)
    shut = copy(rd)                                                  # the rolling shutter (as AJSHUT)
    shut.rect(0, T + 32, 64, T + 128, sc)
    for y in range(T + 32, T + 128, 8):
        shut.rect(0, y, 64, y + 1, shade(sc, 0.5))
        shut.rect(0, y + 1, 64, y + 2, (176, 182, 192))
    shut.rect(0, T + 120, 64, T + 128, shade(sc, 0.6))
    shut.rect(24, T + 122, 40, T + 126, (200, 204, 210))
    shut.noise(4, 79)
    leaves = {"D": rd, "Z": steel, "S": shut}

    # --- the same in every look ------------------------------------------------
    same = {}
    xs = street(False)
    tex("AJ8XS", xs)
    tex("AJ8XSA", street(True))
    same["XT"] = tex("AJ8XT", gy.crop(xs, 384, 512))
    same["XP"] = tex("AJ8XP", passage())
    same["XN"] = tex("AJ8XN", kiosk())
    same["XW"] = tex("AJ8XW", backdrop())
    same["XL"] = tex("AJ8XL", lamps())
    tex("AJ8XD", show_door())
    both("AJ8XI", glazing_bar())
    tex("AJ8XJ", lantern_side())
    tex("AJ8XG", gate())
    both("AJ8XR", road())
    both("AJ8XF", roofs())
    tex("AJ8XH", skyline())
    tex("AJ8XE", Img(64, 64, (24, 24, 32)))                          # what the town's roofs stand on, in the dark
    tex("AJTARG8", bell(same["XN"], 32, 60))
    for tag in ("XC", "XB", "XK"):                                   # the museum's, made before these
        same[tag] = mu.WALLS[tag]

    # --- the three looks ---------------------------------------------------------
    for n, c in LOOKS.items():
        k = int(n)

        def name(tag, pic=""):
            return f"AJ8{tag}{n}{pic}"

        walls = dict(same)
        # outdoors
        for tag, win in (("", 0), ("A", 1), ("B", 2)):
            tex(name("Y" + tag), front(n, win))
        walls["YP"] = tex(name("YP"), gy.crop(_base(n), 384, 512))
        bk = tex(name("K"), back(n))
        walls["KA"] = tex(name("KA"), gy.crop(bk, 384, 512))

        # indoors
        walls["L"] = tex(name("L"), mu.wall(c["lobby"], 192, seed=k))
        walls["A"] = tex(name("A"), mu.wall(c["low"], 128, seed=k))
        walls["H"] = tex(name("H"), atrium(n))
        walls["SH"] = tex(name("SH"), showroom(n))
        walls["CO"] = tex(name("CO"), mu.wall(c["cash"], 128, seed=k + 3))
        tex(name("GV"), gallery_front(n))
        levers(out, name("LV"), shifted(gy.crop(walls["SH"], 0, 160), 32))    # the shutter's lever, in the office
        levers(out, name("LC"), shifted(walls["CO"], 16))                     # the shop window's, in the cash office
        for tag, part in ROOMS.items():
            walls[tag] = tex(name(tag), mu.wall(c[part], 160, seed=k + sum(map(ord, tag))))
            for i in (1, 2):
                tex(name(tag, i), shelves(copy_field(walls[tag]), n, tag, i, 1370 + 10 * k + i + sum(map(ord, tag))))

        # doors
        for (look, kind, tag, s, keys, lines), texture in faces.items():
            if look != n:
                continue
            if kind == "O":                                          # over an open way: the wall, and a plate
                d = shifted(walls[tag], s)
                plate(d, n, lines, d.h - 100)
                tex(texture, d)
                continue
            d = mu.face(walls[tag], s, leaves[kind], c["wood"] if kind == "D" else (70, 74, 82))
            if lines:
                plate(d, n, lines, 140)
            tex(texture, th.locked(d, keys) if keys else d)
        for (look, lines, w), texture in signs.items():
            if look == n:
                tex(texture, sign(n, lines, w))

        # what stands in the rooms
        tex(name("RL"), railing(n))
        tex(name("V"), case(n, False))
        out[f"flats/{name('VT')}.png"] = case(n, True).png()
        wd = Img(64, 64, c["wood"])
        wd.noise(5, 1380 + k)
        for x in range(0, 64, 8):
            wd.rect(x, 0, x + 1, 64, shade(c["wood"], 0.7))
        wd.rect(0, 0, 64, 3, shade(c["wood"], 1.25))
        wd.rect(0, 3, 64, 4, shade(c["wood"], 0.5))
        both(name("WD"), wd)
        bn = Img(64, 64, c["bench"])
        bn.noise(5, 1384 + k)
        for x in range(0, 64, 16):
            for y in range(0, 64, 16):
                bn.disc(x + 8, y + 8, 1, shade(c["bench"], 0.5))
        bn.rect(0, 0, 64, 2, shade(c["bench"], 1.4))
        both(name("BN"), bn)
        pl = Img(64, 64, c["stonec"])
        pl.noise(6, 1388 + k)
        pl.rect(0, 0, 64, 3, shade(c["stonec"], 1.15))
        pl.rect(0, 3, 64, 4, shade(c["stonec"], 0.6))
        for x in range(0, 64, 32):
            pl.rect(x, 4, x + 1, 64, shade(c["stonec"], 0.8))
        both(name("PL"), pl)

        # floors and ceilings
        for i, tag in enumerate(("F", "P", "FD", "FE", "FS", "FO", "FG", "FR", "FL", "FK", "FA", "FT")):
            out[f"flats/{name(tag)}.png"] = flat(n, tag, 1400 + 20 * k + i).png()
        out[f"textures/{name('FL')}.png"] = out[f"flats/{name('FL')}.png"]       # a skylight's sides are glass too
        for i, tag in enumerate(("CL", "CA", "CD", "CS", "CP")):
            out[f"flats/{name(tag)}.png"] = ceiling(n, tag, 1460 + 10 * k + i).png()


def shifted(im, s):
    """The wall `im` as it runs past a piece that starts `s` along its 64."""
    out = Img(im.w, im.h)
    out.px = [list(im.px[y * im.w + (x + s) % im.w]) for y in range(im.h) for x in range(im.w)]
    return out


def copy_field(im):
    out = copy(im)
    out.field = im.field
    return out
