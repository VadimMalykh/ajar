"""Act 2, level 7: "Made to Order" (MAP17), the goods dispatch. It wears
MAP11's look (AJAR_INSTITUTE), as MAP16 does. PLAN.md, "MAP17: the goods
dispatch" and its first version as decided (2026-11-22).

One reader: a crate on a belt. The hopper issues a crate; the belts carry it
east, and where a belt ends at a frame the crate goes through whatever door
hangs there and rides on from that door's far side. Each station stamps the
crate with its colour as it passes its machine. A checker reads the stamps
of a crate that comes onto it, in order, first lowest; what it opens stays
open. No keys, no thief, no nailer, no Stray door: nobody but the player
moves a door.

Stations: the press RED (the hatch at the end of its cell), the kiln GREEN
(the low glowing tunnel), labelling BLUE (the gantry). A TEAL Pair for the
bay. Frames: 101 the hopper's outlet (the hall), 102 the press's (the press
hall), 103 the kiln's, 104 labelling's, 105 the bay's (a TEAL leaf only).

Rooms, all on floor 0:
  the hall (the start): the hopper and its belt to 101. RED leans here.
  the press hall: RED's far side in its west wall opens into the cell, glass
    on three sides, round the head of the press's belt; the press is a hatch
    40 high in the cell's east end (a crate passes, nobody else). Beyond it
    the belt runs over order 1's checker to 102. GREEN leans here.
  the kiln, south, sealed: GREEN's far side, the belt through the kiln's
    tunnel (the player walks round it), order 2's scale, 103.
  labelling, north, sealed: BLUE's far side, the belt under the gantry, 104.
  the dispatch wing, east: BLUE and both TEAL leaves lean here. The bay: 105,
    a short belt out of it, the scale, and beyond it the shutter to the night
    room. Panels in the wall south and north of it: two secrets.
  the night room: VIOLET leans here; its far side in the west end, a brass
    frame that takes any door but VIOLET in the east end. The way out is a
    ring round the line (AjarRing, map17.zs; PLAN.md, "MAP17: the way out
    round the line, and three secrets").
  the store behind the hopper, west of the hall: a secret, reached up the
    belt against it, under the chute.
Glass (shots stop, sight does not): the hall sees the press's checker, the
press hall sees the kiln's scale, the wing sees into the kiln and labelling.
Steel doors with no handle: A, the hall to the press hall; B, the press hall
to the wing.

The orders (a note at each checker is a picture of the crate as wanted):
  1. the press's checker wants RED: steel door A opens.
  2. the kiln's scale wants RED, GREEN: steel door B opens.
  3. the bay's scale wants GREEN, BLUE, RED: the shutter goes up.
  The secrets: the bay's scale also takes BLUE, RED, GREEN (its note is in
  the press's cell, beside RED's far side, its stub on the panel): the panel
  south of the shutter opens; and a crate with no stamps (a leaf in 101, its
  twin in 105; the note by the hopper, its stub on the panel): the panel
  north of it opens.
  The way out: the brass frame holds GREEN or BLUE, and that station's
  outlet VIOLET (or the other station's door, and its outlet VIOLET); then
  coming into the night room by either of its doors ends the level.
A crate that has not moved on along the line for ten seconds is taken back,
as is one with more than six stamps or one off the belts (AjarHopper,
map17.zs); the next comes two seconds after.

In the PUZZLE graph an order is a `sights` key set off by the arrangement of
doors that fills it, as the beams of MAP13 and MAP15 are.
"""
import ajarmap
import map_institute1 as I1
from ajarmap import RED, GREEN, BLUE, VIOLET, TEAL, far_id, LEAVES
from map_institute1 import T, dress, tint, named, things, LOOK, FACES
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, REVENANT, CACO
from udmf import Map, rect

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12 and MAP16.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED

CRATE_T, STATION_T, HOPPER_T, CHECKER_T, LAMP_T, RING_T = 20094, 20095, 20096, 20097, 20098, 20099
LINE, SCALE = 901, 902                      # sector tags: every belt (all run east, at SPEED), the bay's scale
SPEED = 4                                   # units a tic: the player walks at 8.3 and gets out against it
DOOR_A, DOOR_B, SHUTTER, PANEL, PANEL2 = 1, 2, 3, 4, 5  # sector tags of what the checkers open
RING = 9                                    # ambush cause 40 + RING: the way out's ring first closed (map17.zs)
HALL_F, PRESS_F, KILN_F, LABEL_F, BAY_F = 101, 102, 103, 104, 105
CELL_N = 171                                # thing ids of the checkers (their lamps name them)
H = 256                                     # the rooms' height, but the kiln's
KILN_H = 192
BW = 32                                     # half a belt's width
CW = 16                                     # a curb's width (and its height)
BELT_F, SCALE_F, CURB_F, CURB_S = "AJDBELT", "AJDSCAL", "AJDCRBF", "AJDCRBS"
GLASS = dict(mid="AJGLAS", midboth=True, blocking=True, blockhitscan=True, blockprojectiles=True)
TALL_GLASS = dict(GLASS, wrapmidtex=True)
PALE, RUST, COLD, STEEL, DIM = 0xDCE8DC, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0, 0xB0B8C8
GLOW = 0xFFA060                             # the kiln's tunnel: tinted in every look

HALL = dict(ceil=H, light=190, color=tint(PALE), **dress(wall="EX", ftex="FE", ctex="KE"))
PRESS = dict(ceil=H, light=180, color=tint(RUST), **dress(wall="LA", ftex="FA", ctex="KA"))
KILN = dict(ceil=KILN_H, light=150, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
LABEL = dict(ceil=H, light=170, color=tint(DIM), **dress(wall="AR", ftex="FR", ctex="KA"))
WING = dict(ceil=H, light=185, color=tint(STEEL), **dress(wall="CO", ftex="FC", ctex="KC"))
WALL = {id(HALL): "EX", id(PRESS): "LA", id(KILN): "PU", id(LABEL): "AR", id(WING): "CO"}

# What gfx_dispatch.make draws for this map, besides its fixed pictures:
# {texture name: (wall part, shift, what)} for the notes on a wall and the
# shutter's face (see gfx_dispatch.note_on_wall).
NOTES = {}


def tile(box, holes, **props):
    """The floor of a room `box` (x1, y1, x2, y2) round the rectangles
    `holes`: as few rectangular sectors as a grid along their edges gives."""
    xs = sorted({box[0], box[2]} | {v for h in holes for v in (h[0], h[2]) if box[0] < v < box[2]})
    ys = sorted({box[1], box[3]} | {v for h in holes for v in (h[1], h[3]) if box[1] < v < box[3]})

    def free(x1, y1, x2, y2):
        return not any(h[0] <= x1 and x2 <= h[2] and h[1] <= y1 and y2 <= h[3] for h in holes)
    runs = {}
    for j, (y1, y2) in enumerate(zip(ys, ys[1:])):
        i = 0
        while i < len(xs) - 1:
            if not free(xs[i], y1, xs[i + 1], y2):
                i += 1
                continue
            k = i
            while k + 1 < len(xs) - 1 and free(xs[k + 1], y1, xs[k + 2], y2):
                k += 1
            key = (i, k + 1)
            if key in runs and runs[key][-1][1] == j:
                runs[key][-1][1] = j + 1
            else:
                runs.setdefault(key, []).append([j, j + 1])
            i = k + 1
    for (i1, i2), spans in sorted(runs.items()):
        for j1, j2 in spans:
            m.sector(rect(xs[i1], ys[j1], xs[i2], ys[j2]), floor=0, **props)


def run(x1, x2, y, look, *, curbs=(True, True), ceil=None, ftex=BELT_F, tag=LINE, light=None, **more):
    """A stretch of belt along y from x1 to x2 (all belts carry east), with
    its curbs (south, north), in the room's look. Returns the curbs' boxes."""
    base = dict(look, **({"ceil": ceil} if ceil else {}))
    lit = light or min(255, look["light"] + 20)
    m.sector(rect(x1, y - BW, x2, y + BW), floor=0, **dict(base, ftex=ftex, light=lit, id=tag, **more))
    boxes = []
    for on, y1 in zip(curbs, (y - BW - CW, y + BW)):
        if on:
            m.sector(rect(x1, y1, x2, y1 + CW), floor=CW, **dict(base, ftex=CURB_F, side=CURB_S, light=lit))
            boxes.append((x1, y1, x2, y1 + CW))
    return boxes


def scroll(x, y):
    """The one Scroll_Floor line of every belt: on the edge between a belt at
    y (its middle) and its north curb, at x."""
    p, q = (x, y + BW), (x + 8, y + BW)
    m.cut(p, q)
    m.line(p, q, special=223, args=(LINE, 0, 2, 128 + 32 * SPEED, 128), exact=True)


def frame(a, b, out, n, **more):
    ajarmap.recess(m, a, b, out, 0, n, far_id(RED), tag=LINE, **more)


def far(a, b, out, colour, color=None):
    ajarmap.recess(m, a, b, out, 0, far_id(colour), HALL_F, far_colour=colour, tag=LINE, color=color)


def window(box, ends, sill=40, top=160):
    """A window through a wall: the sector `box`, glass on the two lines `ends`."""
    m.sector(rect(*box), floor=sill, ceil=top, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    for p, q in ends:
        m.line(p, q, **GLASS)


def steel_door(a, b, out, tag, near, far_part, words, back_words=""):
    """A steel door with no handle (ajarmap.steel), its face in the look of
    the room it is seen from, with `words` over it."""
    ajarmap.steel(m, a, b, out, 0, tag)
    if LOOK:
        c, d = I1._far(a, b, out)
        for (p, q), o, part, s in (((a, b), out, near, words), ((c, d), (-out[0], -out[1]), far_part, back_words)):
            key = (LOOK, part, I1._shift(p, q, o), "", s)
            m.line(p, q, upper=FACES.setdefault(key, f"AJID{LOOK}{len(FACES):02d}"))


def sign(a, b, out, part, words="", oh=96):
    """In a look: the wall over the way a-b (seen looking `out`) in line with
    the room's wall beside it, with a plate `words` on it (named())."""
    if LOOK:
        m.line(a, b, upper=T(part), dontpegtop=True)
        named(a, b, out, part, words, oh)


def passage(a, b, out, thick, far_part, words):
    """An open way `thick` long through a wall behind a steel door, a-b its
    near mouth (the door's back); a plate over its far mouth."""
    ajarmap.opening(m, a, b, out, 0, thick=thick)
    c, d = I1._far(a, b, out, thick)
    sign(c, d, (-out[0], -out[1]), far_part, words)


def board(box, face, note, look, top=112):
    """A notice board standing beside a checker: `box`, its top at `top`; the
    note (a texture) on its side `face` ("n" or "s"), plain steel elsewhere."""
    x1, y1, x2, y2 = box
    m.sector(rect(*box), floor=top, **dict(look, ftex="AJTRIMF", side="AJDBRDS"))
    p, q = ((x1, y2), (x2, y2)) if face == "n" else ((x1, y1), (x2, y1))
    m.line(p, q, lower=note)


def route_board(x, y, step, look, depth=8):
    """The dispatcher's board: a niche 128 high in the wall at x, y, and in its
    back wall a panel for each outlet and the night room's brass frame, the colour that hangs there now lit
    (ajarmap.route_board; AjarHandler.BoardTick). `step` is (64, 0) along a
    north wall, (0, -64) along an east one."""
    n = 6
    if step[0]:
        box = (x, y, x + 64 * n, y + depth)
        a = (x, y + depth)
    else:
        box = (x, y - 64 * n, x + depth, y)
        a = (x + depth, y)
    m.sector(rect(*box), floor=64, ceil=192, light=230, **{k: v for k, v in look.items() if k not in ("ceil", "light")})
    mouth = ((x, y), (x + 64 * n, y)) if step[0] else ((x, y), (x, y - 64 * n))
    I1.over(*mouth, WALL[id(look)])
    ajarmap.route_board(m, a, [("H", HALL_F), ("P", PRESS_F), ("K", KILN_F), ("L", LABEL_F), ("D", BAY_F),
                               ("X", ajarmap.HOME)], step=step)


def note_on_wall(a, b, out, part, what, name=None):
    """A note pinned to the room's wall piece a-b (64 long), seen looking `out`."""
    name = name or f"AJDN{len(NOTES):02d}"
    NOTES[name] = (part, I1._shift(a, b, out), what)
    m.cut(a, b)
    m.line(a, b, mid=name, exact=True)
    return name


# === the hall: the hopper and its belt to 101 =====================================
HY = 256                                    # the middle of the hall's belt, the cell's and the press hall's
tile((0, 0, 640, 512), [(0, HY - 48, 640, HY + 48)], **HALL)
# the hopper: a chute over the belt's first 96; crates drop out of it onto the belt
HOPPER = dict(HALL, ceil=96)
run(0, 96, HY, HOPPER)
run(96, 640, HY, HALL)
scroll(160, HY)
for p, q in (((96, HY - 48), (96, HY + 48)), ((0, HY - 48), (96, HY - 48)), ((0, HY + 48), (96, HY + 48))):
    m.line(p, q, upper="AJDHOPR", dontpegtop=True)
# the store behind the hopper, where the crates come from (a secret): its mouth is the west wall under the
# chute, the belt's width and 64 high, reached by walking up the belt against it. Crates stacked against
# its walls. Not on the line: a crate is never issued into it, and one that got there would be taken back.
STORE = (-208, HY - 96, -16, HY + 96)
STORE_LOOK = dict(light=104, color=tint(DIM), **dress(wall="CK", ftex="FC", ctex="KC"))
m.sector(rect(-16, HY - BW, 0, HY + BW), floor=0, ceil=64, **STORE_LOOK)
m.line((0, HY - BW), (0, HY + BW), upper="AJDHOPR")                         # (its dark foot over the mouth)
m.sector(rect(*STORE), floor=0, ceil=128, special=1024, **STORE_LOOK)
for box, top in (((-208, HY + 96, -144, HY + 128), 96), ((-144, HY + 96, -80, HY + 128), 64),
                 ((-80, HY + 96, -16, HY + 128), 32), ((-240, HY - 96, -208, HY + 96), 96),
                 ((-208, HY - 128, -144, HY - 96), 64), ((-144, HY - 128, -80, HY - 96), 96),
                 ((-80, HY - 128, -16, HY - 96), 64)):
    m.sector(rect(*box), floor=top, ceil=128, **dict(STORE_LOOK, ftex="AJDSTOF", side="AJDSTOR"))
frame((640, HY - BW), (640, HY + BW), (1, 0), HALL_F, color=tint(PALE))
m.thing(48, HY, HOPPER_T, args=(LINE, SCALE))
# the window onto the press hall: the press's checker is seen from here
window((640, 48, 768, 144), [((640, 48), (640, 144)), ((768, 48), (768, 144))])
sign((640, 48), (640, 144), (1, 0), "EX", "PRESS", oh=160)
sign((768, 144), (768, 48), (-1, 0), "LA", oh=160)
# steel door A, and the passage beyond it into the press hall
steel_door((640, 400), (640, 464), (1, 0), DOOR_A, "EX", "EX", "PRESS")
passage((656, 400), (656, 464), (1, 0), 112, "LA", "HOPPER")
route_board(160, 512, (64, 0), HALL)
I1.hang((0, 384), (0, 512), "WS")                                           # a warning by the hopper
# the blank crate's note, torn from its top, by the hopper in plain sight (its stub: the second panel)
note_on_wall((0, 128), (0, 192), (-1, 0), "EX", "blank", name="AJDNH0")

# === the press hall, the cell and the press ===========================================
CELL = (768, 160, 992, 352)
PRESS_BOX = (992, HY - 48, 1056, HY + 48)   # the press: solid but for its hatch
CHECK1 = (1184, 1248)                        # the press's checker: a stretch of the belt
BOARD1 = (1184, HY + 48, 1248, HY + 64)      # its notice board, north of the belt
tile((768, 0, 1600, 512), [CELL, PRESS_BOX, (1056, HY - 48, 1600, HY + 48), BOARD1], **PRESS)
# the cell: the belt from RED's far side, floor beside it, glass round it
run(768, 992, HY, PRESS)
m.sector(rect(768, CELL[1], 992, HY - 48), floor=0, **PRESS)
m.sector(rect(768, HY + 48, 992, CELL[3]), floor=0, **PRESS)
far((768, HY + BW), (768, HY - BW), (-1, 0), RED, color=tint(RUST))
for p, q in (((768, CELL[1]), (992, CELL[1])), ((768, CELL[3]), (992, CELL[3])),
             ((992, CELL[1]), (992, HY - 48)), ((992, HY + 48), (992, CELL[3]))):
    m.line(p, q, **TALL_GLASS)
# the secret's note, on the cell's west wall beside RED's far side: behind whoever comes in. Torn from
# its top: the stub is on the panel in the bay
note_on_wall((768, HY + BW), (768, HY + BW + 64), (-1, 0), "LA", "secret", name="AJDN00")
# the press: a hatch 40 high through it over the belt; it stamps RED
m.sector(rect(992, HY - BW, 1056, HY + BW), floor=0, ceil=40, light=150, wall="AJDPRSS", ftex=BELT_F,
         ctex="AJTRIMF", id=LINE)
for x in (992, 1056):
    m.line((x, HY - BW), (x, HY + BW), upper="AJDPRSS", dontpegtop=True)
for p, q in (((992, HY - 48), (992, HY - BW)), ((992, HY + BW), (992, HY + 48)),
             ((1056, HY - 48), (1056, HY - BW)), ((1056, HY + BW), (1056, HY + 48)),
             ((992, HY - 48), (1056, HY - 48)), ((992, HY + 48), (1056, HY + 48))):
    m.cut(p, q)
    m.line(p, q, mid="AJDPRSS")
m.thing(1024, HY, STATION_T, args=(RED,))
# beyond it the belt over order 1's checker to 102
run(1056, CHECK1[0], HY, PRESS)
run(CHECK1[0], CHECK1[1], HY, PRESS, ftex=SCALE_F)
run(CHECK1[1], 1600, HY, PRESS)
board(BOARD1, "s", "AJDNP1", PRESS)
m.thing(1216, HY, CHECKER_T, id=CELL_N, args=(1, DOOR_A, 0, 0, 1))
m.thing(1216, HY + 56, LAMP_T, args=(CELL_N,))
frame((1600, HY - BW), (1600, HY + BW), (1, 0), PRESS_F, color=tint(RUST))
# steel door B to the wing, and the passage beyond it
steel_door((1600, 400), (1600, 464), (1, 0), DOOR_B, "LA", "LA", "DISPATCH")
passage((1616, 400), (1616, 464), (1, 0), 112, "CO", "PRESS")
# the window onto the kiln's scale
window((1376, -64, 1504, 0), [((1376, 0), (1504, 0)), ((1376, -64), (1504, -64))])
sign((1504, 0), (1376, 0), (0, -1), "LA", "KILN", oh=160)
sign((1376, -64), (1504, -64), (0, 1), "PU", oh=160)
route_board(1088, 512, (64, 0), PRESS)

# === the kiln, sealed: GREEN's far side, the tunnel, order 2's scale, 103 ===================
KY = -256
TUNNEL = (1024, KY - 64, 1216, KY + 64)      # the kiln proper: solid, but for the tunnel through it
CHECK2 = (1408, 1472)
BOARD2 = (1408, KY - 64, 1472, KY - 48)      # the scale's notice board, south of the belt: seen from the press hall
tile((768, -448, 1600, -64), [TUNNEL, (768, KY - 48, 1600, KY + 48), BOARD2], **KILN)
run(768, TUNNEL[0], KY, KILN)
m.sector(rect(TUNNEL[0], KY - BW, TUNNEL[2], KY + BW), floor=0, ceil=40, light=255, wall="AJDKILN", ftex=BELT_F,
         ctex="AJDKILF", id=LINE, color=GLOW)
for x in (TUNNEL[0], TUNNEL[2]):
    m.line((x, KY - BW), (x, KY + BW), upper="AJDKILN", dontpegtop=True)
for x in (TUNNEL[0], TUNNEL[2]):
    for y1, y2 in ((KY - 64, KY - BW), (KY + BW, KY + 64)):
        m.cut((x, y1), (x, y2))
        m.line((x, y1), (x, y2), mid="AJDKILN")
for y in (KY - 64, KY + 64):
    m.cut((TUNNEL[0], y), (TUNNEL[2], y))
    m.line((TUNNEL[0], y), (TUNNEL[2], y), mid="AJDKILN")
m.thing(1120, KY, STATION_T, args=(GREEN,))
for x in (TUNNEL[0] - 24, TUNNEL[2] + 24):
    m.thing(x, KY, 9800, height=24, args=(255, 140, 60, 96))                 # the glow out of its mouths
run(TUNNEL[2], CHECK2[0], KY, KILN)
run(CHECK2[0], CHECK2[1], KY, KILN, ftex=SCALE_F)
run(CHECK2[1], 1600, KY, KILN)
board(BOARD2, "n", "AJDNK2", KILN)
m.thing(1440, KY, CHECKER_T, id=CELL_N + 1, args=(13, DOOR_B, 0, 0, 2))
m.thing(1440, KY - 56, LAMP_T, args=(CELL_N + 1,))
far((768, KY + BW), (768, KY - BW), (-1, 0), GREEN, color=tint(COLD))
frame((1600, KY - BW), (1600, KY + BW), (1, 0), KILN_F, color=tint(COLD))
I1.hang((768, -448), (768, -320), "GA")                                    # gauges, beside the far side

# === labelling, sealed: BLUE's far side, the gantry, 104 ===========================================
LY = 768
GANTRY = (1088, LY - 64, 1152, LY + 64)
tile((768, 576, 1600, 960), [(768, LY - 48, 1600, LY + 48), (GANTRY[0], LY - 80, GANTRY[2], LY + 80)], **LABEL)
run(768, GANTRY[0], LY, LABEL)
run(GANTRY[0], GANTRY[2], LY, LABEL, ceil=72, wall="AJDGANT")
run(GANTRY[2], 1600, LY, LABEL)
for y1, y2 in ((LY - 64, LY - 48), (LY + 48, LY + 64)):
    m.sector(rect(GANTRY[0], y1, GANTRY[2], y2), floor=0, **dict(LABEL, ceil=72, wall="AJDGANT"))
for x in GANTRY[0::2]:
    m.line((x, LY - 64), (x, LY + 64), upper="AJDGANT", dontpegtop=True)
for y1, y2, face in ((LY - 80, LY - 64, LY - 80), (LY + 64, LY + 80, LY + 80)):   # its legs: solid
    for p, q in (((GANTRY[0], y1), (GANTRY[0], y2)), ((GANTRY[2], y1), (GANTRY[2], y2)),
                 ((GANTRY[0], face), (GANTRY[2], face)), ((GANTRY[0], y1 + y2 - face), (GANTRY[2], y1 + y2 - face))):
        m.cut(p, q)
        m.line(p, q, mid="AJDGANT")
m.thing(1120, LY, STATION_T, args=(BLUE,))
far((768, LY + BW), (768, LY - BW), (-1, 0), BLUE, color=tint(DIM))
frame((1600, LY - BW), (1600, LY + BW), (1, 0), LABEL_F, color=tint(DIM))

# === the dispatch wing; the bay, its scale and the shutter; the panel =================================
BY = 64                                     # the middle of the bay's belt and scale
SCALE_X = (1856, 2016)
STAND = (1904, BY - 64, 1968, BY - 48)       # the bay's lamp stands on it
RACKS = [(2080, -320, 2144, -256), (2080, 320, 2144, 384)]       # racks of goods, for cover
tile((1728, -448, 2176, 960), [(1728, BY - 48, SCALE_X[1], BY + 48), STAND] + RACKS, **WING)
run(1728, SCALE_X[0], BY, WING)
run(SCALE_X[0], SCALE_X[1], BY, WING, ftex=SCALE_F, tag=SCALE)
frame((1728, BY + BW), (1728, BY - BW), (-1, 0), BAY_F, home=TEAL, only=3, color=tint(STEEL))
m.sector(rect(*STAND), floor=80, **dict(WING, ftex="AJTRIMF", side="AJDBRDS"))
m.thing(1936, BY, CHECKER_T, id=CELL_N + 2, args=(321, SHUTTER, 213, PANEL, 3 + 10 * PANEL2))     # (+ the blank one)
m.thing(1936, BY - 56, LAMP_T, args=(CELL_N + 2,))
# the shutter to the night room, the bay's note on it
m.sector(rect(2176, BY - BW, 2192, BY + BW), floor=0, ceil=0, light=160, wall="AJSHUT", ftex="AJTRIMF",
         ctex="AJTRIMF", id=SHUTTER)
NOTES["AJDNB3"] = ("CO", I1._shift((2176, BY - BW), (2176, BY + BW), (1, 0)), "shutter")
m.line((2176, BY - BW), (2176, BY + BW), upper="AJDNB3", dontpegtop=True)
for p, q in (((2176, BY - BW), (2192, BY - BW)), ((2176, BY + BW), (2192, BY + BW))):
    m.line(p, q, mid="AJTRIM", dontpegbottom=True)
# the way to the night room
m.sector(rect(2192, BY - BW, 2560, BY + BW), floor=0, ceil=160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
m.sector(rect(2496, BY + BW, 2560, 128), floor=0, ceil=160, light=150, color=tint(STEEL),
         **dress(wall="EV", ftex="FE", ctex="KE"))
# The night room: VIOLET's far side in its west end, an empty brass frame in its east end, facing each other,
# but the frame takes any door but VIOLET, and nothing hung in it is the way out by itself. The way out is a
# ring round the line (AjarRing, map17.zs): the brass frame holds GREEN or BLUE, that station's outlet
# VIOLET, or the other station's door and its outlet VIOLET; then coming into the night room by either of
# its doors ends the level.
NIGHT = (2368, 128)
ajarmap.way_home(m, *NIGHT, VIOLET, barred=True)
m.thing(NIGHT[0] + 160, NIGHT[1] + 128, RING_T, args=(192, 128, ajarmap.HOME, VIOLET))
# the panels in the wall south and north of the shutter, and the closets behind them: secrets. Each has the
# stub of a note pinned to it, the top of the sheet whose rest is elsewhere
for (y1, y2), tag, stub in (((-128, -64), PANEL, "AJDNS1"), ((192, 256), PANEL2, "AJDNS2")):
    m.sector(rect(2176, y1, 2192, y2), floor=0, ceil=0, light=160, wall=T("CO") if LOOK else "AJWALL",
             ftex="AJTRIMF", ctex="AJTRIMF", id=tag)
    NOTES[stub] = ("CO", I1._shift((2176, y1), (2176, y2), (1, 0)), "stub:" + ("secret" if tag == PANEL else "blank"))
    m.line((2176, y1), (2176, y2), upper=stub, dontpegtop=True)
m.sector(rect(2192, -192, 2320, 0), floor=0, ceil=128, light=120, color=tint(DIM), special=1024,
         **dress(wall="CK", ftex="FC", ctex="KC"))
# (the second closet stops short of VIOLET's far side, whose stub reaches west to 2304)
m.sector(rect(2192, 128, 2288, 320), floor=0, ceil=128, light=120, color=tint(DIM), special=1024,
         **dress(wall="CK", ftex="FC", ctex="KC"))
# the windows into the kiln and labelling
window((1600, -416, 1728, -320), [((1600, -416), (1600, -320)), ((1728, -416), (1728, -320))])
sign((1728, -320), (1728, -416), (-1, 0), "CO", "KILN", oh=160)
sign((1600, -416), (1600, -320), (1, 0), "PU", oh=160)
window((1600, 848, 1728, 944), [((1600, 848), (1600, 944)), ((1728, 848), (1728, 944))])
sign((1728, 944), (1728, 848), (-1, 0), "CO", "LABELS", oh=160)
sign((1600, 848), (1600, 944), (1, 0), "AR", oh=160)
route_board(2176, 896, (0, -64), WING)
for box in RACKS:
    m.sector(rect(*box), **dict(WING, **I1.box(64)))

# === doors ===========================================================================================
ajarmap.door(m, RED, 560, 120, angle=90)
ajarmap.door(m, GREEN, 1450, 450, angle=270)
ajarmap.door(m, BLUE, 1800, 650, angle=0)
ajarmap.pair(m, TEAL, (1800, 760, 0), (1800, 870, 0))
ajarmap.door(m, VIOLET, NIGHT[0] + 160, NIGHT[1] + 232, angle=270)           # against the north wall, seen from the way in

# === the hall: the start ===========================================================================
m.thing(320, 80, 1, angle=90)
m.thing(400, 120, 2001)                                                     # shotgun
things(2008, (440, 120), (480, 120))
m.thing(200, 440, 2002)                                                     # chaingun
things(2048, (260, 440))
things(2011, (40, 40), (600, 40))
things(ZOMBIE, (120, 400), (500, 380), (600, 470), (300, 470), angle=270)
things(SERGEANT, (420, 460), (120, 140), angle=270)
things(IMP, (560, 380), (60, 470), angle=180)

# === the press hall ===================================================================================
m.thing(1300, 450, 82)                                                      # super shotgun
things(2049, (1350, 420), (840, 40))
things(2011, (1560, 40), (1560, 470))
m.thing(900, 460, 2018)                                                     # green armour
things(IMP, (1100, 420), (1250, 100), (1500, 140), (1500, 400), (850, 470), angle=180)
things(SERGEANT, (1150, 80), (1400, 60), (1400, 380), angle=180)
things(DEMON, (1250, 390), (1100, 120), angle=180)
m.thing(1550, 330, CHAINGUNNER, angle=180)
m.thing(1520, 60, REVENANT, angle=180)
m.thing(1350, 140, CACO, angle=180)

# === the kiln ===========================================================================================
m.thing(1300, -400, 2003)                                                   # rocket launcher
things(2010, (1350, -400), (1250, -400))
m.thing(1560, -100, 2012)
things(IMP, (900, -120), (1300, -130), (1540, -400), angle=180)
m.thing(1100, -400, SPECTRE, angle=90)
m.thing(1500, -140, REVENANT, angle=180)
m.thing(950, -400, CHAINGUNNER, angle=0)

# === labelling ==========================================================================================
m.thing(1400, 900, 2004)                                                    # plasma rifle
things(2047, (1450, 900), (1350, 900))
m.thing(820, 620, 2012)
things(IMP, (900, 900), (1250, 620), (1540, 900), angle=180)
things(SERGEANT, (1000, 640), (1300, 900), angle=180)
m.thing(1500, 640, KNIGHT, angle=180)
m.thing(1200, 900, SPECTRE, angle=180)

# === the wing ===========================================================================================
things(2046, (2140, 200), (1760, -400))
things(17, (2140, -420))
things(2012, (1760, 920), (2140, 600))
things(2049, (2140, 920))
m.thing(1800, -200, 2019)                                                   # blue armour
things(IMP, (1850, 300), (2000, 300), (1850, -300), (2000, -300), (1900, 800), (2050, 800), angle=180)
things(SERGEANT, (2000, 520), (2000, -170), (2100, 150), angle=180)
things(CHAINGUNNER, (2100, 700), (2100, -200), angle=180)
things(REVENANT, (2000, 900), (2000, -420), angle=180)
m.thing(1950, 650, KNIGHT, angle=180)
things(CACO, (1900, 450), (1900, -100), angle=180)
things(DEMON, (2000, 200), (1850, 150), angle=180)
# the secret: the closet behind the panel
m.thing(2256, -96, 83)                                                      # a megasphere
things(2046, (2256, -160))
# the second: the closet behind the panel north of the shutter
m.thing(2240, 224, 2013)                                                    # a soul sphere
things(2046, (2240, 160))
things(17, (2240, 288))
# the third: the store behind the hopper
m.thing(-112, HY, 8)                                                        # a backpack
things(2049, (-176, HY - 40))
things(2015, (-176, HY + 40), (-144, HY + 64), (-80, HY - 64), (-48, HY + 64))

# === the night room ==========================================================================================
things(2012, (NIGHT[0] + 80, NIGHT[1] + 40), (NIGHT[0] + 240, NIGHT[1] + 40))
things(2049, (NIGHT[0] + 80, NIGHT[1] + 216))
things(2046, (NIGHT[0] + 240, NIGHT[1] + 216))

# === ambushes =============================================================================================
# RED, taken: the hall
ajarmap.ambush(m, 10 + RED, IMP, (100, 60), (480, 40), angle=90)
ajarmap.ambush(m, 10 + RED, SERGEANT, (240, 420), (450, 470), angle=270, after=2)
# order 1 filled (steel door A opens): company waits in the press hall by its mouth
ajarmap.ambush(m, 40 + DOOR_A, IMP, (900, 400), (1000, 470), (1050, 400), angle=180, near=640)
ajarmap.ambush(m, 40 + DOOR_A, DEMON, (1150, 470), angle=180, near=640)
# GREEN, taken: the press hall
ajarmap.ambush(m, 10 + GREEN, SPECTRE, (1250, 450), (1400, 470), angle=270)
ajarmap.ambush(m, 10 + GREEN, IMP, (850, 60), (1000, 60), angle=90, after=2)
# order 2 filled (steel door B opens): the wing, by its mouth
ajarmap.ambush(m, 40 + DOOR_B, CHAINGUNNER, (1800, 400), (1800, 520), angle=180, near=700)
ajarmap.ambush(m, 40 + DOOR_B, IMP, (1950, 380), (1950, 560), angle=180, near=700)
# BLUE, taken: the wing
ajarmap.ambush(m, 10 + BLUE, REVENANT, (2050, 450), angle=180)
ajarmap.ambush(m, 10 + BLUE, CACO, (1900, -350), angle=90, after=3)
# a TEAL leaf, taken: the wing again, and labelling
ajarmap.ambush(m, 10 + TEAL, KNIGHT, (2100, -50), angle=180)
ajarmap.ambush(m, 10 + TEAL, IMP, (900, 620), (1000, 900), angle=0, after=2)
# VIOLET, taken: the wing, by the shutter
ajarmap.ambush(m, 10 + VIOLET, KNIGHT, (2090, 210), angle=180)
ajarmap.ambush(m, 10 + VIOLET, IMP, (2130, -120), (2050, 260), angle=180)
# the ring first closed: the kiln and labelling, off the belts
ajarmap.ambush(m, 40 + RING, REVENANT, (1150, -130), angle=0)
ajarmap.ambush(m, 40 + RING, IMP, (850, -380), (1450, -380), angle=90)
ajarmap.ambush(m, 40 + RING, KNIGHT, (1350, 640), angle=90)
ajarmap.ambush(m, 40 + RING, IMP, (850, 860), (1450, 860), angle=270)

LA, LB = LEAVES[TEAL]


def _both(d):
    """An arrangement with a leaf in each of two frames, either leaf in either."""
    base, x, y = d
    return [{**base, LA: (x,), LB: (y,)}, {**base, LB: (x,), LA: (y,)}]


PUZZLE = dict(
    start="hall", goal="exit", complete=True,
    names={RED: "RED", BLUE: "BLUE", GREEN: "GREEN", VIOLET: "VIOLET", LA: "a TEAL leaf", LB: "the other TEAL leaf"},
    walk=[("hall", "floor", "a"), ("floor", "hall", "a"),                    # steel door A: order 1
          ("floor", "wing", "b"), ("wing", "floor", "b"),                    # steel door B: order 2
          ("wing", "night", "x"), ("night", "wing", "x"),                    # the shutter: order 3
          ("night", "exit", "y"),                                            # the ring walked round
          ("wing", "secret", "s"), ("secret", "wing", "s"),                  # the panel: the hidden order
          ("wing", "blank", "t"), ("blank", "wing", "t"),                    # the second panel: the blank crate
          ("hall", "store"), ("store", "hall")],                             # the store behind the hopper
    frames={HALL_F: "hall", PRESS_F: "floor", KILN_F: "kiln", LABEL_F: "label", BAY_F: "wing", ajarmap.HOME: "night"},
    only={BAY_F: (LA, LB), ajarmap.HOME: (RED, GREEN, BLUE, LA, LB)},
    doors={RED: dict(home="pressIn", lean="hall"), GREEN: dict(home="kiln", lean="floor"),
           BLUE: dict(home="label", lean="wing"), VIOLET: dict(home="night", lean="night"),
           LA: dict(pair=LB, lean="wing"), LB: dict(pair=LA, lean="wing")},
    sights={
        "a": dict(at="hall", say="a crate comes to the press stamped RED", lines=[{RED: (HALL_F,)}]),
        "b": dict(at="floor", say="a crate comes onto the kiln's scale stamped RED, GREEN",
                  lines=[{RED: (HALL_F,), GREEN: (PRESS_F,)}]),
        "x": dict(at="wing", say="the bay's order is filled",
                  lines=_both(({GREEN: (HALL_F,), BLUE: (KILN_F,), RED: (LABEL_F,)}, PRESS_F, BAY_F))),
        "y": dict(at="night", say="the line runs round through the way out",
                  lines=[{GREEN: (ajarmap.HOME,), VIOLET: (KILN_F,)}, {BLUE: (ajarmap.HOME,), VIOLET: (LABEL_F,)},
                         {GREEN: (ajarmap.HOME,), BLUE: (KILN_F,), VIOLET: (LABEL_F,)},
                         {BLUE: (ajarmap.HOME,), GREEN: (LABEL_F,), VIOLET: (KILN_F,)}]),
        "s": dict(at="wing", say="the hidden order is filled",
                  lines=_both(({BLUE: (HALL_F,), RED: (LABEL_F,), GREEN: (PRESS_F,)}, KILN_F, BAY_F))),
        "t": dict(at="wing", say="a blank crate comes onto the bay's scale", lines=_both(({}, HALL_F, BAY_F))),
    })
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
