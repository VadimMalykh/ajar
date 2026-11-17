"""Candidate looks for MAP09, the telephone exchange (see AJAR_EXCHANGE in map_hinges9.py).

Three looks for the whole exchange, numbered 1 to 3. For look n (name = AJ9 + tag + n):
  Y    the front on the forecourt, 640: rows count down from the sky's edge at
       512. 0..352 the upper floors, 352..384 a band, 384..512 the ground
       floor, 512..640 below ground. YA, YB with windows: a lit ground floor
       under dark rooms; a dark one under a lit room. YP its ground floor
       alone (128), for porches
  K    what stands round the roof, 640 (the top 192 are seen): the switchroom's
       upper storey, its windows lit. KA plain wall of it (128), for the porch
  L    call office, 192          A  porches indoors, 128
  H    switchroom, 448: clerestory (128), the gallery's wall (160), the
       ground floor's (160). HP, HQ the lowest 128 of the ground floor's and
       of the gallery's, for its porches. GV what carries the gallery and the
       balcony (160): the distribution frame
  MG manager's office (128), TR trunk room (160; TRH the same under the hole
     from the loft, 288), CN canteen, CK cloakroom, RR rest room (160),
     AP apparatus room (192), RY relay room (160), TS test room (128)
  S  a switchboard (88 seen), ST its top       R  a rack of selectors (128)
  B  a call box's front (128), BS its sides    V  a counter or desk, VT its top
  RL railing
  WD tables (wall and flat), BN seats (wall and flat), PL stone (wall and flat)
  flats: F call office and switchroom, P the way through them, FO manager's
         office, FD the west wing, FE the east wing, FS trunk room, FG gallery
         and balcony, FR roof, FL a lit skylight, FA the forecourt, FT the way
         across it; CL call office and apparatus room ceiling, CA switchroom,
         CD rooms, CP porches
The same in all three: AJ9XS the houses across the road (640; AJ9XSA with a lit
window), AJ9XT their foot (128), AJ9XN the kiosk (112), AJ9XL the stationery
store (112), AJ9XC the cable loft (160), AJ9XD a cable drum (wall and flat),
AJ9XH the shaft down from the loft (128), AJ9XB the battery room (256), AJ9XJ a
row of cells and AJ9XJT their tops, AJ9XP the cable passage (160), AJ9XG the
generator room (128), AJ9XK coats on their pegs (96). AJTARG9 is the kiosk's
wall with its bell. The alcove off the battery room wears the museum's cellar
(AJ6XC); the strongroom keeps its safes, and the line is not touched.

A door's face is made for its own place in its wall: AJ9D<n><number> for a room
door, AJ9Z<n><number> for a bolted one. The map says which it needs and names
them (FACES in map_hinges9.py).

Every wall is 64 wide and the same mirrored, and the map lines them up by world
position (Map.align). Switchboards and drums repeat every 32, racks, counters
and coats every 16. A call box's front is one picture and is not laid by
position.
"""
import random

from gfx import Img, shade, BRASS, bell, text
import gfx_theatre as th
import gfx_yard as gy
import gfx_museum as mu
from gfx_museum import st, mix, bare
from gfx_station import arch, copy
from gfx_hotel import tiled
from gfx_store import darken, rows, checker, shifted

NAMES = {"1": "Central", "2": "Trunk", "3": "Crossbar"}

IVORY, GILT, INK = (236, 230, 212), (204, 168, 84), (38, 36, 40)
GLASS, LAMP = (26, 32, 50), (240, 206, 130)
# 1: a manual exchange of the 1900s
BRICK, TERRA, MAHOG, CREAM, BOTTLE = (140, 58, 44), (190, 120, 84), (98, 48, 32), (226, 214, 184), (36, 70, 56)
# 2: a trunk exchange of the 1930s
BROWN, PORT, GPO, PAINT, OAK, BLACK = (124, 96, 76), (220, 212, 192), (52, 88, 70), (226, 216, 180), (140, 100, 62), (30, 30, 34)
# 3: a crossbar exchange of the 1960s
CONC, SPAN, WHITE, GREY, ORANGE, TEAL, TEAK, STEELG = ((196, 194, 186), (70, 110, 150), (236, 234, 226), (212, 214, 212),
                                                       (226, 120, 60), (40, 120, 130), (150, 96, 52), (150, 160, 152))
ALU = (190, 194, 200)


def _mah(field, fstyle, mark, **more):
    return st(field, fstyle, mark, MAHOG, "panel", BRASS, (40, 24, 18), CREAM, **more)


def _two(top, dado, **more):
    """Two coats of gloss paint and a black line between them."""
    return st(top, "plain", top, dado, "paint", BLACK, BLACK, shade(top, 1.04), **more)


LOOKS = {
    # a manual exchange of the 1900s: red brick and terracotta, mahogany, glazed tile, brass
    "1": dict(
        call=_mah((216, 204, 170), "plaster", (200, 188, 152), frieze=BOTTLE, fz="stencil"),
        hall=st(CREAM, "plain", CREAM, (112, 64, 44), "concrete", (60, 36, 26), (40, 28, 22), CREAM,
                stile=BOTTLE, bead=GILT),
        upper=st((206, 196, 164), "tile", (186, 176, 144), (206, 196, 164), "none", (60, 36, 26), (60, 36, 26), CREAM,
                 stile=BOTTLE, bead=GILT),
        low=st(CREAM, "plaster", (206, 194, 160), (112, 64, 44), "concrete", (60, 36, 26), (40, 28, 22), CREAM),
        manager=_mah((112, 40, 44), "damask", (134, 58, 58)),
        trunk=_mah((52, 84, 70), "stripe", (64, 100, 84)),
        cn=st((232, 230, 220), "tile", (200, 198, 188), (120, 72, 50), "concrete", (60, 36, 26), (40, 28, 22), CREAM),
        ck=st((204, 186, 146), "plain", (204, 186, 146), (110, 74, 44), "boards", (60, 40, 24), (40, 28, 18), CREAM),
        rr=st((170, 150, 120), "damask", (188, 168, 136), (110, 74, 44), "boards", (60, 40, 24), (40, 28, 18), CREAM),
        ap=st((224, 220, 206), "block", (196, 192, 178), BOTTLE, "paint", (24, 44, 36), (24, 30, 28), (224, 220, 206)),
        ry=st((214, 216, 200), "block", (188, 190, 174), (70, 52, 44), "paint", (40, 30, 26), (30, 24, 22), (214, 216, 200)),
        ts=st(MAHOG, "panel", (66, 30, 20), MAHOG, "boards", BRASS, (40, 22, 16), (70, 40, 28)),
        wood=MAHOG, bench=(52, 84, 70), stonec=(190, 170, 146), metal=BOTTLE, top=(36, 64, 50)),
    # a trunk exchange of the 1930s: brown brick over Portland stone, two-tone gloss paint, oak, lino
    "2": dict(
        call=st((222, 214, 190), "panel", (196, 186, 158), OAK, "panel", (170, 174, 180), BLACK, PORT,
                frieze=GPO, fz="void"),
        hall=_two(PAINT, GPO),
        upper=st(PAINT, "tile", (206, 196, 160), PAINT, "none", BLACK, GPO, PAINT),
        low=_two((214, 204, 170), GPO),
        manager=st(OAK, "panel", (104, 72, 42), OAK, "boards", (170, 174, 180), BLACK, (150, 110, 70)),
        trunk=st((196, 190, 166), "tile", (172, 166, 142), GPO, "paint", BLACK, BLACK, PAINT),
        cn=_two((232, 216, 150), (126, 84, 54)),
        ck=_two((190, 198, 184), (92, 104, 96)),
        rr=_two((186, 204, 214), (60, 76, 104)),
        ap=_two((206, 208, 204), (96, 100, 104)),
        ry=_two((212, 212, 198), (104, 96, 84)),
        ts=st((214, 208, 186), "tile", (188, 182, 160), GPO, "paint", BLACK, BLACK, PAINT),
        wood=OAK, bench=(92, 50, 44), stonec=PORT, metal=BLACK, top=(60, 44, 36)),
    # a crossbar exchange of the 1960s: a concrete frame, blue panels, white walls, one wall of colour
    "3": dict(
        call=st(TEAK, "slats", (108, 66, 34), WHITE, "none", ALU, (50, 52, 58), WHITE),
        hall=bare(GREY, stile=ALU, bead=WHITE),
        upper=st(WHITE, "tile", (214, 212, 204), WHITE, "none", ALU, GREY, WHITE, stile=ALU, bead=WHITE),
        low=bare((200, 202, 200)),
        manager=bare((214, 170, 50)),
        trunk=bare(ORANGE),
        cn=bare((236, 214, 120)), ck=bare((176, 182, 186)), rr=bare((196, 170, 150)),
        ap=bare((196, 208, 200)), ry=bare((186, 200, 210)),
        ts=st(WHITE, "tile", (214, 212, 204), WHITE, "none", ALU, (50, 52, 58), WHITE),
        wood=TEAK, bench=TEAL, stonec=CONC, metal=STEELG, top=(232, 230, 222)),
}

ROOMS = {"CN": "cn", "CK": "ck", "RR": "rr", "RY": "ry"}                      # the rooms 160 high
ALIGNED = ("Y", "YA", "YB", "YP", "K", "KA", "L", "A", "H", "HP", "HQ", "GV", "MG", "TR", "TRH", "AP", "TS", "BS") + tuple(ROOMS)
SAME = ("AJ9XS", "AJ9XSA", "AJ9XT", "AJ9XN", "AJ9XL", "AJ9XC", "AJ9XH", "AJ9XB", "AJ9XP", "AJ9XG", "AJ6XC")


def aligned(n):
    return {f"AJ9{t}{n}" for t in ALIGNED} | set(SAME)


def half(w, h, c, draw):
    """A picture that repeats every `w` (16 or 32) and reads the same from
    either end, 64 wide: `draw` paints one piece."""
    im = Img(w, h, c)
    draw(im)
    return tiled(gy.mirror(im), 64, h)


# --- outdoors ------------------------------------------------------------------
_fronts = {}


def _base(n):
    """The front without windows: one bay, a pier on every 64."""
    if n in _fronts:
        return _fronts[n]
    if n == "1":                                                     # red brick, terracotta bands, a stone foot
        im = th.brick(64, 640, BRICK, shade(BRICK, 0.6), 1601)
        im.rect(0, 0, 64, 8, shade(TERRA, 1.1))                      # coping
        for x in range(0, 64, 8):                                    # dentils
            im.rect(x, 8, x + 4, 14, shade(TERRA, 0.7))
        im.rect(0, 40, 64, 52, TERRA)                                # cornice
        im.rect(0, 50, 64, 52, shade(TERRA, 0.55))
        for y in (204, 344):
            im.rect(0, y, 64, y + 8, TERRA)
            im.rect(0, y + 7, 64, y + 8, shade(TERRA, 0.55))
        im.rect(0, 52, 6, 344, shade(BRICK, 1.14))                   # a brick pier
        im.rect(6, 52, 7, 344, shade(BRICK, 0.6))
        im.rect(0, 352, 64, 384, TERRA)                              # the band: roundels, a wire to each
        im.rect(0, 352, 64, 354, shade(TERRA, 1.25))
        im.rect(0, 381, 64, 384, shade(TERRA, 0.5))
        im.disc(16, 368, 7, shade(TERRA, 0.7))
        im.disc(16, 368, 5, shade(TERRA, 1.15))
        im.rect(22, 367, 32, 369, shade(TERRA, 0.7))
        for y in range(384, 496, 16):                                # the ground floor: brick banded with stone
            im.rect(0, y + 12, 64, y + 16, shade(CREAM, 0.86))
        im.rect(0, 384, 7, 496, shade(CREAM, 0.9))
        im.rect(7, 384, 8, 496, shade(CREAM, 0.55))
        im.rect(0, 496, 64, 512, (84, 80, 78))
        im.rect(0, 496, 64, 497, (140, 134, 128))
        gy.paste(im, th.brick(64, 128, shade(BRICK, 0.5), shade(BRICK, 0.3), 1602), 512)
        im.noise(5, 1603)
        gy.grime(im, 300, 344, 0.9)
    elif n == "2":                                                   # brown brick over a ground floor of Portland stone
        im = th.brick(64, 640, BROWN, shade(BROWN, 0.66), 1604, course=6)
        im.rect(0, 0, 64, 14, PORT)                                  # a stone parapet
        im.rect(0, 12, 64, 14, shade(PORT, 0.6))
        im.rect(0, 14, 64, 20, shade(BROWN, 0.8))
        for y in (204,):
            im.rect(0, y, 64, y + 6, PORT)
            im.rect(0, y + 5, 64, y + 6, shade(PORT, 0.6))
        im.rect(0, 340, 64, 352, PORT)                               # a cornice over the stone
        im.rect(0, 350, 64, 352, shade(PORT, 0.55))
        mu.ashlar(im, 352, 496, PORT, step=24)
        im.rect(0, 352, 64, 384, shade(PORT, 1.03))                  # the band: a fret cut in it
        im.rect(0, 382, 64, 384, shade(PORT, 0.6))
        for x in range(8, 32, 8):
            im.frame(x, 362, x + 6, 374, shade(PORT, 0.72), 1)
        im.rect(0, 384, 8, 496, shade(PORT, 1.05))                   # a flat pilaster
        im.rect(8, 384, 9, 496, shade(PORT, 0.66))
        im.rect(0, 496, 64, 512, (70, 70, 76))                       # a foot of grey granite
        im.rect(0, 496, 64, 497, (130, 130, 138))
        darken(im, 512, 640, 0.7, 0.5)
        im.noise(4, 1605)
        gy.grime(im, 300, 340, 0.92)
    else:                                                            # a concrete frame, blue panels, dark brick below
        im = Img(64, 640, SPAN)
        for y0 in (12, 184):                                         # two floors of panel and window
            im.rect(0, y0, 64, y0 + 60, SPAN)
            im.rect(0, y0 + 60, 64, y0 + 160, shade(SPAN, 0.9))
            for x in range(0, 64, 16):
                im.rect(x, y0, x + 1, y0 + 172, ALU)
            im.rect(0, y0 + 58, 64, y0 + 60, ALU)
        for y in (0, 172, 344):                                      # the floors' edges
            im.rect(0, y, 64, y + 12, CONC)
            im.rect(0, y + 11, 64, y + 12, shade(CONC, 0.6))
        im.rect(0, 0, 6, 384, CONC)                                  # a column
        im.rect(6, 12, 7, 384, shade(CONC, 0.6))
        im.rect(0, 352, 64, 384, WHITE)                              # the band, a blue line along it
        im.rect(0, 352, 64, 353, shade(WHITE, 0.6))
        im.rect(0, 372, 64, 376, SPAN)
        im.rect(0, 382, 64, 384, (50, 52, 58))
        gy.paste(im, th.brick(64, 128, (72, 62, 66), (44, 40, 44), 1606, course=6), 384)
        gy.paste(im, th.brick(64, 128, (72, 62, 66), (44, 40, 44), 1606, course=6), 512)
        im.rect(0, 384, 6, 512, CONC)
        im.rect(6, 384, 7, 512, shade(CONC, 0.6))
        im.rect(0, 500, 64, 512, (40, 40, 44))
        darken(im, 512, 640, 0.7, 0.5)
        im.noise(4, 1607)
    _fronts[n] = gy.mirror(im)
    return _fronts[n]


def window(im, n, top, bottom, lit):
    """An upper window in the middle of a 64-wide bay."""
    glass = LAMP if lit else GLASS
    if n == "1":                                                     # a round-headed sash under a terracotta arch
        arch(im, 32, top - 6, 17, bottom, TERRA)
        arch(im, 32, top, 13, bottom, glass)
        im.rect(31, top, 33, bottom, IVORY)
        for y in range(top + 14, bottom, 24):
            im.rect(19, y, 45, y + 1, IVORY)
        im.rect(15, bottom, 49, bottom + 5, TERRA)
        im.rect(15, bottom + 4, 49, bottom + 5, shade(TERRA, 0.55))
    elif n == "2":                                                   # steel casements in small panes, a stone surround
        im.rect(13, top - 4, 51, bottom + 4, PORT)
        im.rect(13, bottom + 3, 51, bottom + 4, shade(PORT, 0.6))
        im.rect(16, top, 48, bottom, glass)
        for x in range(16, 49, 8):
            im.rect(x, top, x + 1, bottom, (60, 64, 60))
        for y in range(top, bottom, 14):
            im.rect(16, y, 48, y + 1, (60, 64, 60))
    else:                                                            # the glass between the panels
        im.rect(0, top - 2, 64, bottom + 2, glass if lit else GLASS)
        for x in range(0, 64, 16):
            im.rect(x, top - 2, x + 1, bottom + 2, ALU)
        im.rect(0, top - 2, 64, top - 1, ALU)
        if lit:                                                      # strip lights, seen from below
            for x in range(4, 64, 16):
                im.rect(x, top + 6, x + 9, top + 8, (255, 255, 240))
    return im


def ground(im, n, lit):
    """The ground floor's window of a bay, rows 392..488."""
    glass = LAMP if lit else GLASS
    if n == "1":                                                     # tall and round-headed, a blind half down
        arch(im, 32, 394, 20, 486, shade(CREAM, 0.9))
        arch(im, 32, 398, 16, 482, glass)
        im.rect(31, 398, 33, 482, IVORY)
        im.rect(16, 440, 48, 442, IVORY)
        if lit:
            arch(im, 32, 398, 16, 426, (226, 206, 160))
        im.rect(12, 486, 52, 490, shade(CREAM, 0.9))
    elif n == "2":                                                   # wide, in steel, a bronze grille over its foot
        im.rect(12, 396, 52, 484, shade(PORT, 0.8))
        im.rect(14, 398, 50, 482, glass)
        for x in range(14, 51, 9):
            im.rect(x, 398, x + 1, 482, (60, 64, 60))
        for y in range(398, 482, 14):
            im.rect(14, y, 50, y + 1, (60, 64, 60))
        im.rect(14, 462, 50, 482, (96, 74, 44))
        for x in range(16, 50, 4):
            im.rect(x, 464, x + 1, 480, (40, 30, 20))
    else:                                                            # a slot of glass high in the brick
        im.rect(7, 394, 57, 430, ALU)
        im.rect(9, 396, 55, 428, glass)
        for x in (24, 40):
            im.rect(x, 396, x + 1, 428, ALU)
    return im


def front(n, win=0):
    im = copy(_base(n))
    if win:
        t1, b1, t2, b2 = (72, 188, 228, 332) if n != "3" else (72, 172, 244, 344)
        window(im, n, t1, b1, False)
        window(im, n, t2, b2, win == 2)
        ground(im, n, win == 1)
        gy.mirror(im)
    return im


def round_roof(n):
    """What stands round the roof, 640: the switchroom's upper storey, its
    clerestory lit from inside. The roof's floor is at row 192."""
    c = {"1": BRICK, "2": BROWN, "3": (72, 62, 66)}[n]
    im = th.brick(64, 640, c, shade(c, 0.62), 1610 + int(n), course=8 if n == "1" else 6)
    cop = {"1": TERRA, "2": PORT, "3": CONC}[n]
    im.rect(0, 0, 64, 10, cop)
    im.rect(0, 10, 64, 12, shade(cop, 0.5))
    if n == "1":                                                     # a lunette to each bay
        arch(im, 32, 62, 20, 86, TERRA)
        arch(im, 32, 66, 16, 84, LAMP)
        im.rect(31, 66, 33, 84, shade(BOTTLE, 0.8))
        im.rect(10, 86, 54, 90, TERRA)
    elif n == "2":                                                   # a long steel window
        im.rect(6, 56, 58, 100, PORT)
        im.rect(8, 60, 56, 96, LAMP)
        for x in range(8, 57, 8):
            im.rect(x, 60, x + 1, 96, (60, 64, 60))
        im.rect(8, 78, 56, 79, (60, 64, 60))
    else:                                                            # a ribbon of glass under the concrete
        im.rect(0, 12, 64, 40, CONC)
        im.rect(0, 40, 64, 96, LAMP)
        for x in range(0, 64, 16):
            im.rect(x, 40, x + 1, 96, ALU)
        im.rect(0, 96, 64, 100, ALU)
    pipe = {"1": BOTTLE, "2": BLACK, "3": ALU}[n]
    im.rect(0, 12, 3, 192, pipe)                                     # a downpipe on every 64
    im.rect(3, 12, 4, 192, shade(c, 0.5))
    im.rect(0, 180, 64, 192, (84, 88, 96))                           # lead flashing
    im.rect(0, 180, 64, 181, (140, 144, 152))
    darken(im, 192, 640, 0.75, 0.5)
    im.noise(5, 1614 + int(n))
    gy.grime(im, 130, 180, 0.85)
    return gy.mirror(im)


def street(lit):
    """The houses across the road, 640: a terrace behind its railings, a
    telegraph pole to every house and the wires along the lot."""
    c = (66, 60, 68)
    im = th.brick(64, 640, c, shade(c, 0.6), 1620)
    for y in range(0, 70):                                           # a slate roof against the sky
        im.rect(0, y, 64, y + 1, shade((50, 54, 68), 0.6 + 0.4 * y / 70))
    im.rect(0, 70, 64, 76, (96, 90, 90))                             # the gutter
    im.rect(8, 22, 20, 70, shade(c, 0.8))                            # a chimney
    im.rect(7, 22, 21, 25, shade(c, 1.3))
    for k, top in enumerate((110, 250)):
        im.rect(18, top - 6, 46, top, (112, 106, 100))
        im.rect(21, top, 43, top + 80, LAMP if lit and k == 0 else GLASS)
        im.rect(31, top, 33, top + 80, (150, 146, 140))
        im.rect(21, top + 38, 43, top + 40, (150, 146, 140))
        if lit and k == 0:
            im.rect(34, top, 43, top + 80, (110, 60, 70))            # a curtain
        im.rect(17, top + 80, 47, top + 84, (112, 106, 100))
    im.rect(0, 392, 64, 512, shade(c, 0.9))
    im.rect(20, 404, 44, 500, (40, 44, 56))                          # a front door, its fanlight dark
    arch(im, 32, 392, 12, 406, (112, 106, 100))
    arch(im, 32, 395, 9, 406, GLASS)
    im.frame(23, 410, 41, 450, (58, 62, 76), 1)
    im.frame(23, 456, 41, 496, (58, 62, 76), 1)
    im.rect(0, 500, 64, 512, (50, 46, 48))
    for x in range(2, 64, 6):                                        # area railings
        im.rect(x, 470, x + 1, 512, (24, 24, 28))
    im.rect(0, 474, 20, 475, (24, 24, 28))
    im.rect(44, 474, 64, 475, (24, 24, 28))
    im.rect(0, 30, 3, 512, (44, 36, 30))                             # the pole, on every 64
    im.rect(3, 30, 4, 512, (20, 18, 16))
    for y in (40, 52, 64):                                           # its arms and the wires
        im.rect(0, y, 12, y + 2, (44, 36, 30))
        for x in (5, 10):
            im.rect(x, y - 3, x + 1, y, (190, 190, 180))
        im.rect(0, y - 4, 64, y - 3, (24, 24, 30))
    darken(im, 512, 640, 0.7, 0.5)
    im.noise(5, 1621)
    return gy.mirror(im)


# --- the switchroom ----------------------------------------------------------------
def clerestory(n):
    """128: what is between the gallery's wall and the switchroom's roof."""
    c = LOOKS[n]
    im = Img(64, 128, c["upper"]["field"])
    if n == "1":                                                     # a lunette in every bay, an iron truss from every pier
        arch(im, 32, 30, 22, 100, BOTTLE)
        arch(im, 32, 34, 18, 96, GLASS)
        for x in (22, 32, 42):
            im.rect(x, 34, x + 1, 96, BOTTLE)
        im.rect(8, 100, 56, 104, (60, 36, 26))
        for i in range(22):
            im.rect(0, i, 22 - i, i + 1, BOTTLE)
        im.rect(0, 0, 4, 128, BOTTLE)
        im.rect(4, 22, 5, 128, GILT)
        im.rect(0, 0, 64, 5, shade(BOTTLE, 0.6))
    elif n == "2":                                                   # steel windows in small panes, a painted beam
        im.rect(0, 0, 64, 14, GPO)
        im.rect(0, 14, 64, 16, BLACK)
        im.rect(8, 30, 56, 104, (60, 64, 60))
        im.rect(10, 32, 54, 102, GLASS)
        for x in range(10, 55, 11):
            im.rect(x, 32, x + 1, 102, (60, 64, 60))
        for y in range(32, 102, 14):
            im.rect(10, y, 54, y + 1, (60, 64, 60))
        im.rect(0, 0, 5, 128, shade(PAINT, 0.9))
        im.rect(5, 16, 6, 128, shade(PAINT, 0.6))
    else:                                                            # a ribbon of window, a cable tray under it
        im.rect(0, 0, 64, 128, WHITE)
        im.rect(0, 24, 64, 92, GLASS)
        for x in range(0, 64, 16):
            im.rect(x, 24, x + 1, 92, ALU)
        im.rect(0, 22, 64, 24, shade(WHITE, 0.6))
        im.rect(0, 108, 64, 116, STEELG)
        for x in range(0, 64, 4):
            im.rect(x, 110, x + 1, 114, shade(STEELG, 0.6))
        im.rect(0, 0, 4, 128, ALU)
    darken(im, 0, 40, 0.6, 1.0)
    return im


def switchroom(n):
    """448: the clerestory, the gallery's wall, the ground floor's."""
    c = LOOKS[n]
    im = Img(64, 448)
    rows(im, clerestory(n), 0)
    rows(im, mu.wall(c["upper"], 160, seed=60 + int(n)), 128)
    low = mu.wall(c["hall"], 160, seed=64 + int(n))
    rows(im, low, 288)
    im.field = (288 + low.field[0], 288 + low.field[1])
    im.rect(0, 284, 64, 290, c["hall"]["skirt"])                     # where the gallery's floor meets the wall
    im.rect(0, 284, 64, 285, c["hall"]["rail"])
    return gy.mirror(im)


WIRES = ((200, 60, 50), (60, 110, 190), (230, 190, 60), (70, 150, 90), (230, 230, 220), (220, 130, 60), (150, 90, 160))


def frame_front(n):
    """What carries the gallery and the balcony, 160: the distribution frame,
    a jumper wire to every line in the town."""
    c = LOOKS[n]
    post = {"1": (86, 60, 40), "2": BLACK, "3": STEELG}[n]
    back = {"1": (40, 30, 24), "2": (24, 26, 28), "3": (60, 66, 66)}[n]
    im = Img(64, 160, back)
    r = random.Random(1630 + int(n))
    wires = WIRES if n == "3" else ((176, 150, 110), (150, 60, 50), (70, 96, 70), (196, 186, 160), (90, 70, 110))
    for y in range(18, 148, 13):                                     # terminal blocks, and the wires off them
        im.rect(6, y, 32, y + 6, {"1": (196, 186, 160), "2": (60, 40, 30), "3": (226, 226, 220)}[n])
        for x in range(8, 32, 3):
            im.set(x, y + 2, BRASS)
            im.set(x, y + 4, BRASS)
        for x in range(8, 32, 3):
            if r.random() < 0.75:
                w = r.choice(wires)
                for k in range(1, 7):
                    im.set(x + (k % 2), y + 5 + k, w)
    im.rect(0, 15, 5, 160, post)                                     # an upright on every 64
    im.rect(5, 15, 6, 160, shade(post, 0.5))
    im.rect(1, 15, 2, 160, shade(post, 1.4))
    deck = {"1": BOTTLE, "2": GPO, "3": WHITE}[n]
    im.rect(0, 0, 64, 12, deck)
    im.rect(0, 0, 64, 1, shade(deck, 1.3))
    im.rect(0, 9, 64, 10, GILT if n == "1" else BLACK if n == "2" else ORANGE)
    im.rect(0, 12, 64, 15, (20, 20, 20))
    im.rect(0, 152, 64, 160, shade(post, 0.6))
    im.noise(4, 1634 + int(n))
    darken(im, 15, 34, 0.6, 1.0)
    return gy.mirror(im)


def board(n, top):
    """A switchboard, 88 high: a face of jacks and lamps over a shelf of keys
    and plugs, one operator's place to every 32. Both its long sides are faces."""
    c = LOOKS[n]
    wood = {"1": MAHOG, "2": (58, 44, 36), "3": (176, 182, 176)}[n]
    r = random.Random(1640 + int(n))
    if top:
        f = Img(64, 64, shade(wood, 0.9))
        f.noise(4, 1644 + int(n))
        for x in range(0, 64, 32):
            f.rect(x, 0, x + 1, 64, shade(wood, 0.6))
        for y in (2, 34):                                            # a board is 32 deep
            f.rect(0, y + 10, 64, y + 20, {"1": (30, 26, 24), "2": (20, 20, 22), "3": (120, 126, 122)}[n])
            f.rect(0, y, 64, y + 1, shade(wood, 1.4))
        return f

    def draw(im):
        im.rect(0, 0, 32, 3, shade(wood, 1.3))                       # the cornice
        im.rect(0, 3, 32, 4, shade(wood, 0.5))
        panel = {"1": (28, 24, 24), "2": (22, 22, 24), "3": (206, 210, 204)}[n]
        im.rect(2, 6, 16, 50, panel)
        if n == "3":                                                 # no cords: rows of keys that light
            for y in range(9, 48, 5):
                for x in range(4, 16, 4):
                    k = r.random()
                    im.rect(x, y, x + 3, y + 3, ORANGE if k < 0.12 else (120, 200, 130) if k < 0.2 else (236, 236, 228))
                    im.rect(x, y + 3, x + 3, y + 4, shade(panel, 0.7))
            im.rect(2, 6, 16, 7, ALU)
        else:
            lampc = (250, 214, 120) if n == "1" else (236, 240, 220)
            for y in range(8, 30, 3):                                # the subscribers' jacks, a lamp over each
                for x in range(4, 16, 3):
                    im.set(x, y, lampc if r.random() < 0.1 else BRASS if n == "1" else (120, 124, 128))
            im.rect(2, 31, 16, 33, IVORY if n == "2" else shade(wood, 1.2))   # the strip that names them
            for y in range(35, 49, 3):
                for x in range(4, 16, 3):
                    im.set(x, y, (16, 14, 14) if n == "1" else (70, 72, 76))
            for x0, y0, cc in ((6, 22, (150, 50, 44)), (11, 37, (60, 110, 80)), (14, 14, (150, 50, 44))):
                for k in range(52 - y0):                             # cords, up from the shelf
                    im.set(min(15, x0 + (k * (15 - x0)) // (2 * (52 - y0))), y0 + k, cc)
        im.rect(0, 50, 32, 52, shade(wood, 1.35))                    # the keyshelf
        im.rect(0, 52, 32, 58, shade(wood, 1.1))
        im.rect(0, 58, 32, 60, shade(wood, 0.45))
        for x in range(3, 16, 4):                                    # plugs standing in it, or keys
            im.rect(x, 47 if n != "3" else 53, x + 1, 52 if n != "3" else 56, BRASS if n == "1" else (200, 204, 208) if n == "2" else (60, 64, 66))
        im.rect(0, 60, 32, 96, shade(wood, 0.8))                     # the kneehole
        if n != "3":
            im.frame(3, 64, 16, 86, shade(wood, 0.55), 1)
        im.rect(0, 6, 2, 60, wood)                                   # the stile between two places
        im.rect(0, 6, 1, 60, shade(wood, 1.3))
        im.rect(0, 88, 32, 96, shade(wood, 0.4))
    return half(32, 96, wood, draw)


def rack(n):
    """A rack of apparatus, 128: one upright to every 16."""
    r = random.Random(1650 + int(n))
    iron = {"1": (30, 32, 34), "2": (104, 110, 112), "3": STEELG}[n]

    def draw(im):
        im.rect(0, 0, 16, 128, shade(iron, 0.45))
        for y in range(6, 120, {"1": 10, "2": 19, "3": 8}[n]):
            if n == "1":                                             # relays: a coil in cotton, a brass tongue
                im.rect(4, y, 8, y + 4, (140, 120, 84))
                im.rect(4, y + 1, 8, y + 2, (100, 84, 56))
                im.rect(3, y + 5, 8, y + 6, BRASS)
                im.set(3, y + 2, (190, 60, 50) if r.random() < 0.3 else (60, 60, 64))
            elif n == "2":                                           # a selector under its can, the bank below it
                im.rect(2, y, 8, y + 9, (60, 62, 66))
                im.rect(2, y, 3, y + 9, (120, 124, 128))
                for k in range(4):
                    im.rect(2 + k, y + 10 + k, 8, y + 11 + k, BRASS if k % 2 else (150, 126, 70))
                if r.random() < 0.15:
                    im.set(6, y + 2, (255, 200, 90))
            else:                                                    # a crossbar switch: bars, and rows of contacts
                im.rect(2, y, 8, y + 6, (212, 216, 210))
                im.rect(2, y + 2, 8, y + 3, (120, 126, 122))
                im.set(3 + r.randrange(4), y + 4, r.choice(WIRES))
        im.rect(0, 0, 2, 128, iron)                                  # the upright
        im.rect(0, 0, 1, 128, shade(iron, 1.4))
        im.rect(0, 0, 16, 4, iron)
        im.rect(0, 120, 16, 128, shade(iron, 0.7))
    return half(16, 128, iron, draw)


def callbox(n, side):
    """A call box, 128 high: its front is one picture, its sides repeat."""
    c = LOOKS[n]
    wood = {"1": MAHOG, "2": PAINT, "3": WHITE}[n]
    trim = {"1": BRASS, "2": GPO, "3": TEAL}[n]
    if side:
        def draw(im):
            im.frame(2, 6, 32, 60, shade(wood, 0.7), 1)
            im.frame(2, 66, 32, 120, shade(wood, 0.7), 1)
            im.rect(0, 0, 32, 4, trim)
            im.rect(0, 122, 32, 128, shade(wood, 0.5))
        return half(32, 128, wood, draw)
    im = Img(64, 128, wood)
    im.noise(4, 1660 + int(n))
    im.rect(0, 0, 64, 16, trim if n != "1" else shade(wood, 0.7))    # the head, and what it says
    ink = {"1": GILT, "2": IVORY, "3": WHITE}[n]
    text(im, "TELEPHONE", 5, 5, ink, 1)
    im.rect(0, 16, 64, 17, shade(wood, 0.5))
    im.frame(6, 20, 58, 124, shade(wood, 0.6), 2)                    # the door
    im.rect(12, 26, 52, 78, (30, 38, 46))                            # its glass, the lamp inside
    for y in range(26, 78):
        f = 1 - abs(y - 40) / 40
        im.rect(12, y, 52, y + 1, mix((30, 38, 46), (226, 196, 120), max(0, f) * 0.55))
    if n != "3":                                                     # glazing bars
        im.rect(31, 26, 33, 78, shade(wood, 0.7))
        im.rect(12, 43, 52, 45, shade(wood, 0.7))
    im.rect(25, 52, 39, 70, (20, 20, 22))                            # the instrument on the wall
    im.rect(19, 47, 45, 50, (20, 20, 22))                            # and its handset across it
    im.rect(19, 50, 23, 54, (20, 20, 22))
    im.rect(41, 50, 45, 54, (20, 20, 22))
    im.disc(32, 61, 4, (96, 96, 102))
    im.disc(32, 61, 1, (20, 20, 22))
    im.frame(12, 84, 52, 118, shade(wood, 0.72), 1)
    im.rect(50, 70, 54, 84, trim)                                    # the handle
    im.rect(0, 122, 64, 128, shade(wood, 0.5))
    return im


def railing(n):
    r = Img(64, 32, (0, 0, 0, 0))
    if n == "1":                                                     # cast iron under a brass rail
        r.rect(0, 0, 64, 3, BRASS)
        r.rect(0, 0, 64, 1, shade(BRASS, 1.3))
        r.rect(0, 29, 64, 32, BOTTLE)
        for x in range(0, 64, 8):
            r.rect(x + 3, 3, x + 5, 29, BOTTLE)
            r.diamond(x + 4, 16, 2, BOTTLE)
        for x in range(0, 64, 32):
            r.rect(x, 3, x + 3, 29, shade(BOTTLE, 1.3))
    elif n == "2":                                                   # three steel tubes, painted
        for y in (0, 12, 24):
            r.rect(0, y, 64, y + 3, BLACK)
            r.rect(0, y, 64, y + 1, (110, 112, 118))
        for x in range(0, 64, 32):
            r.rect(x, 0, x + 3, 32, BLACK)
        r.rect(0, 30, 64, 32, GPO)
    else:                                                            # a teak rail, thin steel, a panel of wired glass
        r.rect(0, 0, 64, 4, TEAK)
        r.rect(0, 0, 64, 1, shade(TEAK, 1.4))
        for x in range(0, 64, 32):
            r.rect(x, 4, x + 2, 32, ALU)
        r.rect(0, 30, 64, 32, (120, 124, 130))
        for x in range(2, 64, 4):
            for y in range(8, 30, 4):
                r.set(x, y, (150, 190, 200, 120))
    return r


def desk(n, top):
    """A counter or a desk, 40 high. Repeats every 16."""
    c = LOOKS[n]
    wood = c["wood"]
    if top:
        f = Img(64, 64, c["top"])
        f.noise(4, 1670 + int(n))
        f.frame(0, 0, 64, 64, shade(wood, 1.1), 2)
        for i, (x, y) in enumerate(((8, 8), (40, 36))):              # a pad, a pencil, and the telephone
            f.rect(x, y, x + 12, y + 16, (232, 228, 214))
            for k in range(3, 14, 3):
                f.rect(x + 2, y + k, x + 10, y + k + 1, (150, 150, 160))
            f.rect(x + 14, y + 2, x + 15, y + 12, (200, 160, 60))
        for x, y in ((40, 8), (8, 40)):
            body = (20, 20, 22) if n != "3" else (220, 216, 200)
            f.rect(x, y + 3, x + 12, y + 13, body)
            f.disc(x + 6, y + 8, 3, shade(body, 1.6) if n != "3" else (150, 150, 150))
            f.rect(x - 1, y, x + 13, y + 3, shade(body, 1.3) if n != "3" else shade(body, 0.85))
        return f
    im = Img(64, 64, wood)
    im.noise(4, 1674 + int(n))
    im.rect(0, 0, 64, 3, shade(wood, 1.3))
    im.rect(0, 3, 64, 5, shade(wood, 0.5))
    for x in range(0, 64, 16):
        im.rect(x, 5, x + 1, 64, shade(wood, 0.72))
        if n == "1":
            im.frame(x + 3, 8, x + 14, 34, shade(wood, 0.7), 1)
        elif n == "2":
            im.rect(x + 3, 10, x + 14, 11, (170, 174, 180))
    if n == "3":
        im.rect(0, 5, 64, 30, WHITE)
        im.rect(0, 30, 64, 31, ALU)
    im.rect(0, 36, 64, 64, shade(wood, 0.6))
    return im


# --- floors, ceilings ---------------------------------------------------------------
def flat(n, tag, seed):
    if tag == "F":                                                   # call office and switchroom
        if n == "1":                                                 # wood block, herringbone
            a = (128, 86, 50)
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
        if n == "2":                                                 # brown lino, a line round every square
            f = Img(64, 64, (112, 74, 52))
            f.noise(6, seed)
            f.frame(0, 0, 64, 64, (84, 54, 38), 1)
            return f
        return checker((206, 208, 204), (168, 174, 172), 16, seed)   # vinyl tile
    if tag == "P":                                                   # the way through
        if n == "1":
            return th.flat("carpet", (38, 70, 56), GILT, seed)
        if n == "2":
            f = Img(64, 64, GPO)
            f.noise(5, seed)
            f.rect(0, 0, 2, 64, (20, 30, 26))
            f.rect(62, 0, 64, 64, (20, 30, 26))
            return f
        f = Img(64, 64, (60, 64, 70))
        f.noise(7, seed)
        return f
    if tag == "FO":
        return th.flat("carpet", {"1": (110, 36, 40), "2": (60, 50, 44), "3": (80, 96, 110)}[n], GILT if n != "3" else WHITE, seed)
    if tag in ("FD", "FE", "FS", "FG"):
        if n == "1":
            if tag == "FD":
                return gy.flat("quarry", seed)
            a = {"FE": (120, 84, 52), "FS": (104, 70, 42), "FG": (90, 62, 40)}[tag]
            return th.flat("boards", a, shade(a, 0.6), seed)
        if n == "2":
            if tag == "FD":
                return checker((176, 150, 110), (120, 84, 60), 16, seed)
            if tag == "FE":
                f = Img(64, 64, (120, 124, 126))
                f.noise(6, seed)
                f.frame(0, 0, 64, 64, (96, 100, 102), 1)
                return f
            if tag == "FS":
                return th.flat("carpet", (70, 60, 50), (150, 126, 70), seed)
            return th.flat("boards", OAK, shade(OAK, 0.6), seed)
        if tag == "FD":
            return checker((226, 196, 110), WHITE, 16, seed)
        if tag == "FE":
            return th.flat("terrazzo", (176, 186, 182), (110, 120, 118), seed)
        if tag == "FS":
            return th.flat("carpet", (60, 64, 70), ORANGE, seed)
        f = Img(64, 64, (150, 156, 152))                             # FG: steel plate, studded
        f.noise(5, seed)
        for i in range(4, 64, 8):
            for j in range(4, 64, 8):
                f.set(i, j, (196, 200, 196))
        return f
    if tag == "FR":
        if n == "3":
            f = Img(64, 64, (112, 106, 98))
            f.noise(18, seed)
            return f
        return gy.flat("lead", seed)
    if tag == "FL":                                                  # a skylight, lit from below
        f = Img(64, 64, (236, 214, 150))
        f.noise(6, seed)
        bar = {"1": BOTTLE, "2": (60, 64, 60), "3": ALU}[n]
        for i in range(0, 64, 16):
            f.rect(i, 0, i + 2, 64, bar)
            f.rect(0, i, 64, i + 2, bar)
        return f
    if tag == "FA":
        return gy.flat({"1": "setts", "2": "flags", "3": "slabs"}[n], seed)
    if n == "1":                                                     # FT: the way across the forecourt
        return gy.flat("tiles", seed)
    if n == "2":
        return gy.flat("slabs", seed)
    f = Img(64, 64, (150, 150, 146))
    f.noise(7, seed)
    f.rect(0, 0, 64, 1, (110, 110, 106))
    f.rect(0, 0, 1, 64, (110, 110, 106))
    return f


def ceiling(n, tag, seed):
    if tag == "CP":
        if n == "1":
            return gy.ceiling((150, 116, 72), (90, 66, 40), 16, seed)
        if n == "2":
            return gy.ceiling(PAINT, None, 16, seed)
        f = Img(64, 64, shade(TEAK, 1.1))
        for x in range(0, 64, 8):
            f.rect(x, 0, x + 1, 64, shade(TEAK, 0.6))
        f.noise(4, seed)
        return f
    lamp = tag in ("CL", "CD")
    if n == "1":                                                     # boarded, cream; a lamp under a green shade
        f = Img(64, 64, CREAM)
        for x in range(0, 64, 8):
            f.rect(x, 0, x + 1, 64, shade(CREAM, 0.84))
        if tag == "CA":
            f.rect(0, 0, 64, 5, BOTTLE)
            f.rect(0, 5, 64, 6, shade(BOTTLE, 0.5))
        if lamp:
            f.disc(32, 32, 7, BOTTLE)
            f.disc(32, 32, 4, (255, 244, 204))
        f.noise(3, seed)
        return f
    if n == "2":                                                     # painted plaster, a beam, an opal bowl
        f = Img(64, 64, shade(PAINT, 1.04))
        f.rect(0, 0, 64, 6, shade(PAINT, 0.86) if tag != "CA" else GPO)
        f.rect(0, 6, 64, 7, shade(PAINT, 0.6))
        if lamp:
            f.disc(32, 34, 8, (150, 152, 150))
            f.disc(32, 34, 6, (255, 250, 230))
        f.noise(3, seed)
        return f
    f = Img(64, 64, (232, 230, 222))                                 # acoustic tile, strip lights
    for i in range(0, 64, 16):
        f.rect(i, 0, i + 1, 64, (204, 202, 194))
        f.rect(0, i, 64, i + 1, (204, 202, 194))
    for i in range(4, 64, 4):
        for j in range(4, 64, 4):
            if i % 16 and j % 16:
                f.set(i, j, (190, 188, 180))
    if lamp or tag == "CA":
        f.rect(8, 28, 56, 36, (255, 252, 236))
        f.frame(8, 28, 56, 36, (170, 170, 164), 1)
    f.noise(3, seed)
    return f


# --- the same in every look -------------------------------------------------------
def kiosk():
    """112: the kiosk at the gate: directories on their shelves, a notice."""
    r = random.Random(1680)
    im = Img(64, 112, (70, 52, 40))
    for y in range(8, 96, 22):
        x = 2
        while x < 30:
            w = r.choice((4, 5, 6))
            c = r.choice(((150, 40, 40), (40, 60, 110), (60, 90, 60), (190, 170, 120), (40, 40, 44)))
            im.rect(x, y + r.randrange(3), min(31, x + w), y + 17, c)
            im.rect(x, y + 8, min(31, x + w), y + 10, GILT if sum(c) < 400 else INK)
            x += w + 1
        im.rect(0, y + 17, 64, y + 20, (130, 100, 70))
        im.rect(0, y + 19, 64, y + 20, (30, 26, 22))
    im.rect(0, 100, 64, 112, (44, 34, 28))
    im.noise(4, 1681)
    return gy.mirror(im)


def stationery():
    """112: the stationery store: reams, pads and boxes of forms."""
    r = random.Random(1682)
    im = Img(64, 112, (60, 62, 58))
    for y in range(4, 100, 24):
        x = 2
        while x < 30:
            w = r.choice((8, 10, 13))
            hh = r.choice((10, 14, 18))
            c = r.choice(((226, 220, 204), (200, 190, 160), (150, 170, 190), (226, 200, 150), (190, 110, 90)))
            im.rect(x, y + 20 - hh, min(31, x + w), y + 20, c)
            for k in range(y + 23 - hh, y + 20, 3):
                im.rect(x, k, min(31, x + w), k + 1, shade(c, 0.8))
            x += w + 1
        im.rect(0, y + 20, 64, y + 23, (120, 124, 118))
        im.rect(0, y + 22, 64, y + 23, (30, 30, 28))
    im.rect(0, 102, 64, 112, (40, 42, 40))
    im.noise(4, 1683)
    return gy.mirror(im)


def loft():
    """The cable loft, 160: bare brick, and the cables on their hangers."""
    c = (120, 78, 62)
    im = th.brick(64, 160, c, shade(c, 0.6), 1684)
    for k, y in enumerate((20, 30, 40, 54, 64)):                     # lead-covered cables, some fat
        t = 7 if k in (1, 3) else 4
        im.rect(0, y, 64, y + t, (112, 116, 124))
        im.rect(0, y, 64, y + 1, (170, 174, 182))
        im.rect(0, y + t - 1, 64, y + t, (60, 62, 70))
    im.rect(0, 14, 4, 76, (40, 40, 44))                              # a hanger on every 64
    im.rect(0, 76, 10, 79, (40, 40, 44))
    im.rect(0, 150, 64, 160, shade(c, 0.5))
    im.noise(5, 1685)
    gy.grime(im, 110, 160, 0.8)
    return gy.mirror(im)


def drum(top):
    """A cable drum on its side."""
    wood = (150, 116, 76)
    if top:
        f = Img(64, 64, wood)
        f.noise(6, 1686)
        for cx in (16, 48):
            for cy in (16, 48):
                f.disc(cx, cy, 15, shade(wood, 0.8))
                f.disc(cx, cy, 13, wood)
                f.disc(cx, cy, 4, (40, 40, 44))
        return f

    def draw(im):
        im.rect(0, 0, 32, 3, shade(wood, 1.2))
        im.rect(3, 6, 32, 44, (40, 42, 48))                          # the cable wound on it
        for y in range(8, 44, 4):
            im.rect(3, y, 32, y + 1, (84, 88, 98))
        im.rect(0, 3, 3, 48, shade(wood, 0.8))
        im.rect(0, 44, 32, 48, shade(wood, 0.6))
    return half(32, 64, wood, draw)


def shaft():
    """128: the hole down from the loft into the trunk room: brick, cables."""
    c = (84, 58, 50)
    im = th.brick(64, 128, c, shade(c, 0.6), 1687)
    for x in (10, 18, 24):
        im.rect(x, 0, x + 4, 128, (96, 100, 108))
        im.rect(x, 0, x + 1, 128, (150, 154, 162))
    for y in (30, 94):
        im.rect(6, y, 32, y + 3, (36, 36, 40))
    darken(im, 0, 128, 0.6, 1.0)
    return gy.mirror(im)


def battery():
    """The battery room, 256: white glazed brick, a black foot, acid on it."""
    c = (214, 218, 212)
    im = th.brick(64, 256, c, (150, 156, 150), 1688)
    im.rect(0, 0, 64, 8, (60, 66, 62))
    im.rect(0, 28, 64, 32, (96, 70, 44))                             # the busbar, copper
    im.rect(0, 28, 64, 29, (190, 130, 80))
    for y in (26, 32):
        im.rect(2, y, 6, y + 2, (40, 40, 44))
    for y in range(176, 256):
        for x in range(64):
            p = im.px[y * 64 + x]
            p[:3] = mix(p[:3], (44, 60, 54), 0.8)
    im.rect(0, 174, 64, 177, (20, 22, 22))
    r = random.Random(1689)
    for _ in range(14):                                              # where the acid has run
        x, y = r.randrange(32), r.randrange(90, 170)
        im.rect(x, y, x + 1, min(176, y + r.randrange(6, 30)), (176, 180, 150))
    im.noise(4, 1690)
    gy.grime(im, 120, 256, 0.85)
    return gy.mirror(im)


def cells(top):
    """A row of cells, 40 high: glass jars, the plates in the acid."""
    if top:
        f = Img(64, 64, (40, 44, 46))
        for i in range(0, 64, 16):
            for j in range(0, 64, 16):
                f.rect(i + 1, j + 1, i + 15, j + 15, (120, 140, 130))
                for k in range(3, 14, 3):
                    f.rect(i + 2, j + k, i + 14, j + k + 1, (70, 74, 80))
                f.disc(i + 8, j + 3, 1, (176, 120, 70))
        f.noise(4, 1691)
        return f

    def draw(im):
        im.rect(0, 0, 16, 3, (60, 62, 66))
        im.rect(1, 3, 16, 34, (96, 124, 112))                        # the jar
        im.rect(1, 3, 16, 9, (150, 170, 160))
        for x in range(3, 16, 3):
            im.rect(x, 9, x + 1, 32, (60, 64, 70))
        im.rect(0, 3, 1, 34, (170, 190, 180))
        im.rect(0, 34, 16, 40, (84, 60, 40))                         # the stand
        im.rect(0, 40, 16, 64, (40, 30, 24))
    return half(16, 64, (60, 62, 66), draw)


def passage():
    """The cable passage, 160: whitewash over black, the cables along it."""
    im = th.brick(64, 160, (206, 204, 190), (176, 174, 160), 1692)
    for y in range(96, 160):
        for x in range(64):
            p = im.px[y * 64 + x]
            p[:3] = mix(p[:3], (36, 38, 42), 0.8)
    im.rect(0, 94, 64, 97, (24, 24, 26))
    for y, t in ((12, 6), (22, 4), (30, 4)):
        im.rect(0, y, 64, y + t, (112, 116, 124))
        im.rect(0, y, 64, y + 1, (170, 174, 182))
    im.rect(0, 8, 3, 40, (40, 40, 44))
    im.noise(5, 1693)
    gy.grime(im, 110, 160, 0.8)
    return gy.mirror(im)


def generator():
    """The generator room, 128: engine-room green, a panel of dials."""
    c = (84, 112, 96)
    im = Img(64, 128, c)
    im.rect(0, 70, 64, 128, shade(c, 0.6))
    im.rect(0, 68, 64, 71, (200, 60, 40))
    im.rect(8, 14, 32, 60, (30, 32, 34))                             # a slate panel
    im.frame(8, 14, 32, 60, BRASS, 1)
    for cx, cy in ((16, 26), (26, 26)):
        im.disc(cx, cy, 4, IVORY)
        im.set(cx, cy, INK)
        im.set(cx + 1, cy - 1, INK)
        im.set(cx + 2, cy - 2, INK)
    for x in range(13, 30, 5):
        im.rect(x, 40, x + 2, 52, BRASS)
        im.disc(x + 1, 40, 1, (200, 60, 40))
    im.rect(0, 120, 64, 128, (30, 34, 32))
    im.noise(5, 1694)
    gy.grime(im, 90, 128, 0.8)
    return gy.mirror(im)


def coats():
    """96: a row of pegs, a coat on each, hats over them."""
    r = random.Random(1695)

    def draw(im):
        c = r.choice(((60, 56, 70), (90, 70, 50), (50, 66, 60), (110, 96, 80)))
        im.rect(0, 0, 16, 4, (120, 90, 60))
        im.rect(1, 6, 8, 11, shade(c, 0.8))                          # a hat
        im.rect(0, 10, 8, 12, shade(c, 0.6))
        for y in range(16, 84):                                      # a coat, wider at the hem
            half_w = 3 + (y - 16) // 14
            im.rect(max(0, 8 - half_w), y, 8, y + 1, shade(c, 0.9 + 0.2 * ((y // 3) % 2)))
        im.rect(7, 16, 8, 84, shade(c, 0.5))
        im.rect(0, 88, 16, 96, (60, 44, 30))
    return half(16, 96, (36, 30, 28), draw)


def make(out, rd, faces={}):
    """`rd` is the plain room door (leaf in its bottom 96 rows). `faces` is the
    door faces the map needs: {(look, kind "D" or "Z", wall tag, shift, keys):
    texture}."""
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
    leaves = {"D": rd, "Z": steel}

    # --- the same in every look ------------------------------------------------
    same = {}
    xs = street(False)
    tex("AJ9XS", xs)
    tex("AJ9XSA", street(True))
    same["XT"] = tex("AJ9XT", gy.crop(xs, 384, 512))
    same["XN"] = tex("AJ9XN", kiosk())
    same["XL"] = tex("AJ9XL", stationery())
    same["XC"] = tex("AJ9XC", loft())
    same["XH"] = tex("AJ9XH", shaft())
    same["XB"] = tex("AJ9XB", battery())
    same["XP"] = tex("AJ9XP", passage())
    same["XG"] = tex("AJ9XG", generator())
    tex("AJ9XD", drum(False))
    out["flats/AJ9XD.png"] = drum(True).png()
    tex("AJ9XJ", cells(False))
    out["flats/AJ9XJT.png"] = cells(True).png()
    tex("AJ9XK", coats())
    tex("AJTARG9", bell(same["XN"], 32, 60))

    # --- the three looks ---------------------------------------------------------
    for n, c in LOOKS.items():
        k = int(n)

        def name(tag):
            return f"AJ9{tag}{n}"

        walls = dict(same)
        for tag, win in (("", 0), ("A", 1), ("B", 2)):
            tex(name("Y" + tag), front(n, win))
        walls["YP"] = tex(name("YP"), gy.crop(_base(n), 384, 512))
        rr = tex(name("K"), round_roof(n))
        ka = gy.crop(rr, 112, 240)                                   # its plain brick, for the porch on the roof
        rows(ka, gy.crop(rr, 112, 176), 64)
        walls["KA"] = tex(name("KA"), gy.mirror(ka))

        walls["L"] = tex(name("L"), mu.wall(c["call"], 192, seed=k))
        walls["A"] = tex(name("A"), mu.wall(c["low"], 128, seed=k))
        walls["H"] = tex(name("H"), switchroom(n))
        # under the switchroom's porches its own wall goes on (Vadim, 2026-11-17: the porches' wall,
        # A, has its dado lower, and the panelling broke at every door): the lowest 128 of its
        # ground floor's wall, and of its gallery's
        walls["HP"] = tex(name("HP"), gy.crop(walls["H"], 320, 448))
        walls["HQ"] = tex(name("HQ"), gy.crop(walls["H"], 160, 288))
        walls["MG"] = tex(name("MG"), mu.wall(c["manager"], 128, seed=k + 3))
        walls["TR"] = tex(name("TR"), mu.wall(c["trunk"], 160, seed=k + 5))
        high = Img(64, 288)                                          # the trunk room's wall under the hole from the loft
        rows(high, same["XH"], 0)
        rows(high, walls["TR"], 128)
        tex(name("TRH"), high)
        walls["AP"] = tex(name("AP"), mu.wall(c["ap"], 192, seed=k + 7))
        walls["TS"] = tex(name("TS"), mu.wall(c["ts"], 128, seed=k + 9))
        for tag, part in ROOMS.items():
            walls[tag] = tex(name(tag), mu.wall(c[part], 160, seed=k + sum(map(ord, tag))))
        tex(name("GV"), frame_front(n))

        for (look, kind, tag, s, keys), texture in faces.items():
            if look != n:
                continue
            d = mu.face(walls[tag], s, leaves[kind], c["wood"] if kind == "D" else (70, 74, 82))
            tex(texture, th.locked(d, keys) if keys else d)

        # what stands in the rooms
        tex(name("RL"), railing(n))
        tex(name("S"), board(n, False))
        out[f"flats/{name('ST')}.png"] = board(n, True).png()
        tex(name("R"), rack(n))
        tex(name("B"), callbox(n, False))
        tex(name("BS"), callbox(n, True))
        tex(name("V"), desk(n, False))
        out[f"flats/{name('VT')}.png"] = desk(n, True).png()
        wd = Img(64, 64, c["wood"])
        wd.noise(5, 1700 + k)
        for x in range(0, 64, 8):
            wd.rect(x, 0, x + 1, 64, shade(c["wood"], 0.7))
        wd.rect(0, 0, 64, 3, shade(c["wood"], 1.25))
        wd.rect(0, 3, 64, 4, shade(c["wood"], 0.5))
        both(name("WD"), wd)
        bn = Img(64, 64, c["bench"])
        bn.noise(5, 1704 + k)
        for x in range(0, 64, 16):
            for y in range(0, 64, 16):
                bn.disc(x + 8, y + 8, 1, shade(c["bench"], 0.5))
        bn.rect(0, 0, 64, 2, shade(c["bench"], 1.4))
        both(name("BN"), bn)
        pl = Img(64, 64, c["stonec"])
        pl.noise(6, 1708 + k)
        pl.rect(0, 0, 64, 3, shade(c["stonec"], 1.15))
        pl.rect(0, 3, 64, 4, shade(c["stonec"], 0.6))
        for x in range(0, 64, 32):
            pl.rect(x, 4, x + 1, 64, shade(c["stonec"], 0.8))
        both(name("PL"), pl)
        mt = Img(64, 64, c["metal"])                                 # the top of a rack
        mt.noise(4, 1712 + k)
        for x in range(0, 64, 16):
            mt.rect(x, 0, x + 1, 64, shade(c["metal"], 0.6))
        out[f"flats/{name('RT')}.png"] = mt.png()

        for i, tag in enumerate(("F", "P", "FO", "FD", "FE", "FS", "FG", "FR", "FL", "FA", "FT")):
            out[f"flats/{name(tag)}.png"] = flat(n, tag, 1720 + 20 * k + i).png()
        out[f"textures/{name('FL')}.png"] = out[f"flats/{name('FL')}.png"]       # a skylight's sides are glass too
        for i, tag in enumerate(("CL", "CA", "CD", "CP")):
            out[f"flats/{name(tag)}.png"] = ceiling(n, tag, 1790 + 10 * k + i).png()


if __name__ == "__main__":
    # The look board's swatches (tools/board9_shots.sh): for each look the
    # front, the call office, the switchroom, a switchboard, a rack, a call
    # box and the floor, 64 wide, into the directory named.
    import os
    import sys
    os.makedirs(sys.argv[1], exist_ok=True)
    for n, c in LOOKS.items():
        pics = dict(Y=gy.crop(front(n, 1), 392, 512), L=mu.wall(c["call"], 192, seed=int(n)), H=gy.crop(switchroom(n), 288, 448),
                    S=gy.crop(board(n, False), 0, 88), R=rack(n), B=callbox(n, False), F=flat(n, "F", 1720 + 20 * int(n)))
        for tag, im in pics.items():
            open(os.path.join(sys.argv[1], f"{tag}{n}.png"), "wb").write(im.png())
