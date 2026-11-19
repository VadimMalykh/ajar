"""Act 1, level 7: "Small Hours" (MAP07).

An observatory on a hill, at night. One new sight and no new rule: wherever a
door's far side is, an empty frame stands beside it, with something between
the two that cannot be walked: the bars of the gate, the height of a balcony,
a ravine. A door hung beside its own far side is a step across.

The way out is that step with nothing to cross (ajarmap.way_round). The night
room is off the dome's gallery. In its west wall a ready-made pair of
openings turns you round; in its east wall are BLUE's far side and an empty
frame. BLUE hung there turns you round at that end too, and the room repeats
with you in it.

The beginning is quiet: the road, the gate, the forecourt, the hall and the
yard are empty. The library and the dome are not, and both can be taken from
above: GREEN's far side is on the stacks over the library, and the dome's
gallery is reached over the roof (or through YELLOW). Hung in the hall's
frame, GREEN puts you over the library before anything in it has seen you.

The catch. BLUE leans in the transit house on the knoll, beyond the ravine,
behind two locks. VIOLET, whose far side is the knoll, leans on the hillside,
and the hillside is reached only by a stile no door fits through or by a
drop off the roof: so VIOLET hangs in the hillside's one frame, the one that
stands across the ravine from its own far side. BLUE comes down off the knoll
to that same frame and no further. What has to hang there instead is YELLOW,
which leads up to the gallery, and YELLOW gets to the hillside only over the
knoll: through VIOLET, hung somewhere else by then.

Places. The road (start), the gate, the forecourt, the hall, the library
under its stacks, the dome under its gallery, the west yard and the lane are
one place to walk about in. The dome is eight-sided, with the telescope on
its pier; so is the planetarium. It is night indoors too: each lamp and
glass case has its pool of light (AJAR_DIM). North of the building the hill
is open: the wood is below it, and the country beyond. Up: the stacks (GREEN's far side; key 1), the
gallery (YELLOW's; key 2), the roof between the lane and the dome, the night
room. North: the hillside (VIOLET, a frame), the ravine, the knoll (VIOLET's
far side) and the transit house (keys 3 and 4: BLUE). West wing (key 1): the
workshop, the instrument room (YELLOW), the clock room (key 4). East wing
(key 2): the lecture room, the planetarium, the orrery, and steps down to the
cellar (key 3).

Secrets: the lens store behind the instrument room (a squeeze; PINK and a
frame) and beyond its bars the armoury (PINK's far side); the cave in the
ravine (the transit house's lever, or a Stray door); the shed in the lane
(shoot its bell through the bars); an alcove past the cistern.
"""
import math
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


UP, PIT, CELLAR = 160, -128, -128
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True, floorpeg=True)
SEAT = dict(ftex="AJSOFA", side="AJSOFA", floor=16)
CASE = dict(ftex="AJSTEEL", side="AJWOOD", floor=40)  # a display case, a plinth, a bench of instruments
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
PATH = dict(ftex="AJARCHF")
GATE, NIGHT_BOLT, BOILER, CAVE, ARMOURY, SHED = 401, 402, 403, 404, 405, 406
NX, NY = -160, 1712                                   # the night room's south-west corner
NIGHT = 150                                           # light under the sky

# Small hours: indoors is dim, with a pool of light at every lamp, glass case
# and exhibit. AJAR_DIM=0 is evenly bright, as the level was first lit.
DIM = (os.environ.get("AJAR_DIM") or "1") != "0"
TECHLAMP, CANDELABRA, TORCH_R = 86, 35, 46
LAMPS = {                                             # what lights the rooms, and where
    TECHLAMP: [(-232, 552), (232, 888),                                              # the hall
               (-232, 1080), (232, 1080), (-176, 1456), (176, 1456),                 # the dome's floor
               (-424, 2984), (-88, 3080),                                            # the transit house
               (-1608, 664), (-1208, 1000), (-1608, 1064), (-1208, 1400), (-1608, 600), (-1208, 264),   # west wing
               (360, 552), (760, 824), (824, 1016), (1224, 1352)],                   # east wing
    CANDELABRA: [(872, 600), (1176, 600), (872, 904), (1176, 904),                   # the planetarium
                 (-256, 1536), (256, 1536),                                          # the gallery's corners
                 (-968, 872)],                                                       # the stacks
    TORCH_R: [(-776, 616), (-296, 552)],                                             # the library
}


def lux(bright, dim):
    return dim if DIM else bright


# The observatory's look (gfx_observatory.py): 3, Star Palace (fluted concrete,
# bronze, midnight blue and gold), is the user's choice for the whole of it.
# AJAR_OBSERVATORY=1 and 2 are the candidates that lost (Royal: brick and
# Portland stone, oak, brass; Mountain: granite, riveted iron, limewash, pine);
# AJAR_OBSERVATORY=0 is the level in the plain textures it was first built in.
# A look changes textures only: no floor, wall or railing moves. Rooms are not
# tinted in a look.
LOOK = (os.environ.get("AJAR_OBSERVATORY") or "3").replace("0", "")
FACES = {}                  # the door faces this build needs, and their textures: gfx_observatory.make draws them


def T(tag, pic=""):
    return f"AJ7{tag}{LOOK}{pic}"


if LOOK:
    import gfx_observatory
    m.align = gfx_observatory.aligned(LOOK)
    WARM = GOLD = SKY = LEAF = PLUM = ROSE = None
    FRONT, LOWW, PORCH, HOLE = T("Y"), T("A"), T("CP"), "AJTRIM"
    OPEN = dict(ceil=512, ctex="F_SKY1", wall=T("G"))                     # the grounds: a wall, and trees over it
    BUILT = dict(ceil=512, ctex="F_SKY1", wall=FRONT)                     # between the building's own walls
    WILD = dict(ceil=512, ctex="F_SKY1", wall="AJ7XN", side="AJ7XR")      # the hill
    ROOFO = dict(ceil=512, ctex="F_SKY1", wall=T("YU"), side=T("YS"))
    RAIL = dict(RAIL, mid=T("RL"))
    SEAT = dict(ftex=T("BN"), side=T("BN"), floor=16)
    GSEAT = dict(ftex="AJ6XP", side="AJ6XP", floor=16)                    # a stone seat out of doors
    CASE = dict(ftex=T("VT"), side=T("V"), floor=40)
    CRATE = WOOD
    WOOD = dict(ftex=T("WD"), side=T("WD"))
    PLINTH = dict(ftex=T("WD"), side=T("WD"), floor=32)                   # what an exhibit stands on
    PLANET = dict(wall=T("EP"), ftex=T("FE"), ctex=T("CS"))               # the planetarium
    STARS, SHELL = T("ES"), T("DS")                                       # between the steps of its dome; of the telescope's
    BOOKS = dict(ftex=T("WD"), side=T("LB"))
    PATH, RUN = dict(ftex=T("FO")), dict(ftex=T("P"))
    STONE, PAVE, ROCKF = "AJ6XP", T("FT"), "AJ7XR"
    HALL = dict(wall=T("H"), ftex=T("F"), ctex=T("CH"))
    LIB = dict(wall=T("L"), ftex=T("FL"), ctex=T("CL"))
    STACKS = dict(wall=T("LS"), ftex=T("FA"), side=T("LV"), ctex=T("CL"))
    DOME = dict(wall=T("D"), ftex=T("FD"), ctex=T("CD"))
    GAL = dict(floor=UP, ftex=T("FA"), side=T("DV"))
    PIER = dict(floor=256, ftex="AJSTEEL", side=T("DP"))
    ROOFF, SKYLIGHT = T("FR"), dict(floor=UP + 40, ftex=T("FS"), side=T("FS"), light=255)
    TRANSIT = dict(wall=T("T"), ftex=T("FI"), ctex=T("CW"))
    STEPS = dict(wall=T("S"), ftex="AJ6XP", side="AJ6XP", ctex=T("CP"))
    BOILERW, SHEDW, CAVEW, CELLW, LENSW, ARMW = "AJ6XB", "AJ6XS", "AJ6XG", "AJ6XC", "AJ7XL", "AJ7XA"

    def wing(tag):
        return dict(wall=T(tag), ftex=T("FW"), ctex=T("CW"))
else:
    FRONT = LOWW = None
    PORCH, HOLE = "AJBOARD", "AJBRICK"
    BUILT = WILD = ROOFO = OPEN
    GSEAT, CRATE, BOOKS, RUN = SEAT, WOOD, WOOD, PATH
    PLINTH = dict(WOOD, floor=32)
    PLANET = dict(wall="AJXW2", ftex="AJXG2", ctex="AJXC2")
    STARS, SHELL = "AJXW2", "AJBRICK"
    STONE, PAVE, ROCKF = "AJTRIM", "AJARCHF", "AJPIT"
    HALL = LIB = DOME = dict(wall="AJBRICK", ftex="AJFLOOR")
    STACKS = dict(wall="AJBRICK", ftex="AJBOARD", side="AJWOOD")
    GAL = dict(floor=UP, ftex="AJSTEEL", side="AJSTEEL")
    PIER = dict(floor=256, ftex="AJSTEEL", side="AJSTEEL")
    ROOFF, SKYLIGHT = "AJSTEEL", dict(floor=UP + 40, ftex="AJSTEEL", side="AJSTEEL")
    TRANSIT = {}
    STEPS = dict(wall="AJBRICK", ftex="AJBOARD")
    BOILERW = SHEDW = CAVEW = LENSW = ARMW = "AJSAFE"
    CELLW = "AJBRICK"

    def wing(tag):
        return {}


def low(floor=0):
    """A porch: doors and frames in tall rooms and under the sky stand under one."""
    return dict(dict(ceil=floor + 128, ctex=PORCH), **(dict(wall=LOWW) if LOOK else {}))


def over(a, b, tex, **k):
    """In a look: the wall over the opening a-b (under a lower ceiling) carries
    on as `tex`, in line with the wall beside it."""
    if LOOK and tex:
        m.line(a, b, upper=tex, dontpegtop=True, **k)


def pools(box, base):
    """Small hours: the light round each lamp in the room `box`, falling off in three steps."""
    spots = [p for kind in LAMPS.values() for p in kind if box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]]
    return [((x - d, y - d, x + d, y + d), dict(light=min(255, base + up)))
            for d, up in ((112, 25), (80, 50), (48, 80)) for x, y in spots] if DIM else []


def glowing(features, base):
    """Small hours: a glass case or an exhibit is lit, and lights the floor round it."""
    def lit(change):
        return DIM and (change is CASE or change is PLINTH or change is PIER)
    return ([((r[0] - 32, r[1] - 32, r[2] + 32, r[3] + 32), dict(light=min(255, base + 40)))
             for r, change in features if lit(change)]
            + [(r, dict(change, light=min(255, base + 85)) if lit(change) else change) for r, change in features])


def fit(box, features, above=None, outline=None, **base):
    """ajarmap.shaped: a room `box` (or the polygon `outline` inside it) with
    furniture, and at night its pools of light. In a look the walls over the
    open sides of its porches (low()) carry on as `above` (default: the
    room's own wall)."""
    ajarmap.shaped(m, box, pools(box, base["light"]) + glowing(features, base["light"]), outline, **base)
    for shape, change in features:
        if change.get("ctex") != PORCH or isinstance(shape[0], tuple):
            continue
        x1, y1, x2, y2 = shape
        for a, b, on_wall in (((x1, y1), (x2, y1), y1 == box[1]), ((x2, y1), (x2, y2), x2 == box[2]),
                              ((x2, y2), (x1, y2), y2 == box[3]), ((x1, y2), (x1, y1), x1 == box[0])):
            if not on_wall:
                over(a, b, above or base.get("wall"))


def rail(*runs, **k):
    for a, b in runs:
        m.cut(a, b)
        m.line(a, b, **dict(RAIL, **k))


def edges(poly):
    return list(zip(poly, poly[1:] + poly[:1]))


def slant(a, b, whole=None, **k):
    """Properties for the slanting wall a-b, part of the wall `whole` (default:
    all of it). In a look its textures are stretched to a whole number of 64s
    over `whole`, so that they meet the walls at its two ends as they meet
    each other."""
    w = whole or (a, b)
    length = math.dist(*w)
    m.line(a, b, **dict(k, **(dict(fit=(w[0], max(1, round(length / 64)) * 64 / length)) if LOOK else {})))


def windows(fixed, starts, axis="x"):
    """In a look: 64-long pieces of the building's front with windows, lit and
    dark by turns. Each starts at a multiple of 64. Declared before front()."""
    for i, s in enumerate(starts if LOOK else ()):
        a, b = ((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
        m.cut(a, b)
        m.line(a, b, mid=T("Y" + "AB"[i % 2]))


def front(*runs, tex=None):
    """In a look: these pieces of a place's wall are the building's (or `tex`)."""
    for a, b in runs if LOOK else ():
        m.line(a, b, mid=tex or FRONT)


def pictures(tag, fixed, starts, axis="x"):
    """In a look: 64-long pieces of a room's wall with something hung on them."""
    for i, s in enumerate(starts if LOOK else ()):
        a, b = ((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
        m.cut(a, b)
        m.line(a, b, mid=T(tag, "12"[i % 2]))


def _face(kind, tag, a, out, keys=""):
    """The face of a door whose mouth starts at `a` in the wall `tag`, seen by
    someone the door goes `out` from: the wall carries on over the leaf."""
    lo = a[0] if out[0] == 0 else a[1]
    s = lo % 64 if out in ((0, 1), (-1, 0)) else -lo % 64
    return FACES.setdefault((LOOK, kind, tag, s, keys), f"AJ7{kind}{LOOK}{len(FACES):02d}")


def _doors(kind, a, b, out, near, far, thick, keys=""):
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    lo = (min(a[0], b[0]), min(a[1], b[1]))
    if LOOK and near:
        m.line(a, b, upper=_face(kind, near, lo, out, keys))
    if LOOK and far:
        m.line(c, d, upper=_face(kind, far, lo, (-out[0], -out[1]), keys))


def door(a, b, out, floor, near, far, **k):
    """A room door. In a look each side has its own face: `near` and `far` are
    the walls it stands in (tags of gfx_observatory's, "XC" for AJ6XC)."""
    ajarmap.roomdoor(m, a, b, out, floor, **k)
    _doors("D", a, b, out, near, far, k.get("thick", 16), k.get("keys", ""))


def bolted(a, b, out, floor, tag, near, far, **k):
    """A bolted door; `near`, `far` as door()'s, None for a side that stays as it is."""
    ajarmap.bolted(m, a, b, out, floor, tag, **k)
    _doors("Z", a, b, out, near, far, k.get("thick", 16))


def _wall(tag):
    return tag and (tag if tag.startswith("AJ") else T(tag))


def opening(a, b, out, floor, near, far, thick=16):
    """An open way between two rooms; in a look their walls carry on over it."""
    ajarmap.opening(m, a, b, out, floor, thick=thick)
    over(a, b, _wall(near))
    over((a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick), _wall(far))


def squeeze(a, b, out, floor, near, far):
    ajarmap.squeeze(m, a, b, out, floor)
    over(a, b, _wall(near))
    over((a[0] + out[0] * 16, a[1] + out[1] * 16), (b[0] + out[0] * 16, b[1] + out[1] * 16), _wall(far))


def bars(a, b, out, floor, near=None, far=None, thick=16):
    """A barred opening in a wall: to look and shoot through. In a look, `near`
    and `far` are the walls it is cut through on either side."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall=HOLE,
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)
    if LOOK:
        m.line(a, b, upper=_wall(near), lower=_wall(near), dontpegtop=True, dontpegbottom=True)
        m.line(c, d, upper=_wall(far), lower=_wall(far), dontpegtop=True, dontpegbottom=True)


def hall(box, cases, tag, plinths=(), **k):
    """A room of a wing: 160 high, with benches of instruments."""
    fit(box, [(c, CASE) for c in cases] + [(c, PLINTH) for c in plinths],
        **dict(dict(ceil=160, light=lux(175, 125)), **dict(k, **wing(tag))))


# === the way in: nobody about ====================================================
# the road: start here. The gate is bolted on the inside; beside it, bars to
# look through and an empty frame
fit((-384, -832, 384, -320), [
    ((-64, -832, 64, -320), PATH),
    ((-64, -384, 64, -320), low()),                                          # before the gate
    ((128, -384, 256, -320), low()),                                         # before the frame
    ((-320, -640, -256, -448), GSEAT),                                       # a bench for those who wait
], above=FRONT, floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
recess((160, -320), (224, -320), (0, 1), 0, 101, 201)                        # the frame by the gate
# the gate passage: RED's far side, three steps from that frame
fit((-128, -256, 128, 0), [
    ((-64, -256, 64, 0), PATH),
    ((-64, -256, 64, -192), low()),
    ((-128, -192, -64, -64), low()),
], above=FRONT, floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
recess((-128, -160), (-128, -96), (-1, 0), 0, far_id(RED), 101, far_colour=RED)
m.line((-128, -160), (-128, -96), special=11, args=(GATE, 32), playercross=True)   # coming in draws the bolt
# the forecourt
fit((-448, 0, 448, 512), [
    ((-64, 0, 64, 512), PATH),
    ((-96, 448, 96, 512), low()),                                            # before the front door
    ((-448, 192, -384, 320), low()),                                         # before the arch to the yard
    ((-32, 224, 32, 288), dict(floor=40, ftex="AJSTEEL", side=STONE)),       # the sundial
    ((-288, 96, -160, 128), GSEAT), ((160, 96, 288, 128), GSEAT),
    ((-288, 384, -160, 416), GSEAT), ((160, 384, 288, 416), GSEAT),
], above=FRONT, floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
windows(512, (-384, -256, 192, 320))                                         # the building's front
front(((-448, 512), (-96, 512)), ((96, 512), (448, 512)))
bolted((-32, -320), (32, -320), (0, 1), 0, GATE, "A", "A", thick=64, line_id=311)
bars((64, -320), (128, -320), (0, 1), 0, T("G"), T("G"), thick=64)

# the hall: GREEN, a frame, and three doors
fit((-256, 528, 256, 912), [
    ((-64, 528, 64, 912), RUN),
    ((-224, 560, -160, 624), SEAT), ((-224, 816, -160, 880), SEAT),
    ((160, 816, 224, 880), PLINTH),                                          # a globe on its stand
], floor=0, ceil=256, light=lux(185, 140), **HALL)
pictures("H", 528, (-192, 128))
pictures("H", 912, (128, -192))
door((-32, 512), (32, 512), (0, 1), 0, "A", "H")
recess((256, 560), (256, 624), (1, 0), 0, 105, 201)                          # the hall's frame

# the west yard, and the lane north out of it
fit((-1168, 64, -464, 448), [
    ((-528, 192, -464, 320), low()),
    ((-1072, 64, -944, 128), low()),                                         # before the boiler house
    ((-848, 224, -784, 288), dict(floor=32, ftex="AJWATER", side=STONE)),    # the well
    ((-656, 96, -592, 224), GSEAT),
], above=FRONT, floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
windows(448, (-1008, -768, -592))                                            # the library's back
front(((-1008, 448), (-464, 448)))
opening((-448, 224), (-448, 288), (-1, 0), 0, "A", "A")
fit((-1168, 448, -1008, 2000), [
    ((-1168, 768, -1104, 896), low()),                                       # before the west wing's door
    ((-1168, 1728, -1104, 1952), low()),                                     # before the shed
    ((-1072, 1152, -1008, 1280), dict(CRATE, floor=48)),                     # crates
    ((-1168, 1408, -1104, 1472), dict(CRATE, floor=48)),
], floor=0, light=NIGHT, ftex=PAVE, **BUILT)
windows(-1168, (960, 1088, 1216, 1536), "y")                                 # the west wing
# the boiler house: bolted inside, and one of the places a Stray door opens onto.
# A Stray door is luck (Vadim, 2026-11-18: all of the kills and items have to be
# within reach): a lever in the cellar's alcove draws the bolt too
m.sector(rect(-1168, -16, -848, 48), ceil=128, light=120, wall=BOILERW, ftex="AJPIT")
m.sector(rect(-1168, -208, -848, -16), ceil=128, light=120, wall=BOILERW, ftex="AJPIT")
bolted((-1040, 64), (-976, 64), (0, -1), 0, BOILER, "A", "XB", line_id=305)
ajarmap.unbolt(m, (-1168, -16), (-848, -16), BOILER)
ajarmap.stray_place(m, 0, (-1040, -208), (-976, -208), (0, -1), 0)
# the shed in the lane (secret), seen through bars: shoot its bell
m.sector(rect(-1440, 1744, -1184, 1936), ceil=112, light=170, color=ROSE, wall=SHEDW, special=1024)
bolted((-1168, 1760), (-1168, 1824), (-1, 0), 0, SHED, "A", "XS")
bars((-1168, 1856), (-1168, 1920), (-1, 0), 0, LOWW, SHEDW)
m.cut((-1440, 1856), (-1440, 1920))
m.line((-1440, 1856), (-1440, 1920), special=11, args=(SHED, 32), impact=True, mid="AJTARG6" if LOOK else "AJTARG", exact=True)

# === the library, under its stacks ===============================================
fit((-800, 528, -272, 912), [
    ((-336, 656, -272, 784), low()),                                         # before the hall's door
    ((-784, 528, -656, 592), low()),                                         # before the frame
    ((-640, 656, -448, 720), dict(WOOD, floor=32)), ((-640, 784, -448, 848), dict(WOOD, floor=32)),   # tables
    ((-432, 528, -368, 592), dict(BOOKS, floor=112)), ((-432, 848, -368, 912), dict(BOOKS, floor=112)),
], floor=0, ceil=320, light=lux(170, 120), color=WARM, **LIB)
door((-256, 688), (-256, 752), (-1, 0), 0, "H", "A")
recess((-752, 528), (-688, 528), (0, -1), 0, 102, 201, color=WARM)           # the frame under the stacks
fit((-992, 528, -800, 912), [
    ((-992, 624, -960, 848), dict(BOOKS, floor=UP + 72)),                    # shelves
], floor=UP, ceil=320, light=lux(180, 120), color=WARM, **STACKS)
rail(((-800, 528), (-800, 688)), ((-800, 752), (-800, 912)))                 # a gap over the library
recess((-928, 528), (-864, 528), (0, -1), UP, far_id(GREEN), 101, far_colour=GREEN, color=WARM)

# === the dome, under its gallery =================================================
# Eight-sided: a square 768 with 192 cut off each corner. The gallery runs
# round the west, north and east of it, 160 up. Two low bays open out of the
# slanting walls, where the corners were: the frame's on the floor, and over
# on the gallery YELLOW's far side. The middle of the roof is stepped up, and
# the slit runs through it from wall to wall.
DOME_BOX = (-384, 928, 384, 1696)
ROUND = ajarmap.octagon(*DOME_BOX, 192)
LANTERN = ajarmap.octagon(-240, 1072, 240, 1552, 144)
DARK = lux(175, 120)
fit(DOME_BOX, [
    (LANTERN, dict(ceil=512)),
    ((-32, 928, 32, 1696), dict(ctex="F_SKY1")),                             # the slit, open to the stars
    ((-96, 928, 96, 992), low()),                                            # before the hall's door
    ((-384, 1056, -256, 1440), GAL), ((256, 1056, 384, 1440), GAL), ((-128, 1568, 128, 1696), GAL),
    ([(-384, 1440), (-256, 1440), (-128, 1568), (-128, 1696), (-384, 1696)], GAL),
    ([(384, 1440), (256, 1440), (128, 1568), (128, 1696), (384, 1696)], GAL),
    ((-384, 1216, -320, 1344), dict(GAL, **low(UP))),                        # before the roof's door
    ((-96, 1632, 96, 1696), dict(GAL, **low(UP))),                           # before the night room's
    ((-64, 1248, 64, 1376), PIER),                                           # the pier of the telescope
    ((-160, 1088, -96, 1152), CASE), ((96, 1088, 160, 1152), CASE),
], outline=ROUND, floor=0, ceil=448, light=DARK, color=SKY, **DOME)
for a, b in edges(LANTERN):                                                  # the step in the roof
    slant(a, b, upper=SHELL) if a[0] != b[0] and a[1] != b[1] else m.line(a, b, upper=SHELL)
SE, NE = ((192, 928), (384, 1120)), ((192, 1696), (384, 1504))               # the slanting walls with a bay in them
slant((-384, 1120), (-192, 928))
slant((-384, 1504), (-192, 1696))
m.sector([(192, 928), (288, 1024), (352, 1024), (352, 928)], floor=0, light=DARK, color=SKY,
         **dict(DOME, **low()))                                              # the frame's bay
slant((192, 928), (288, 1024), SE, **(dict(upper=T("D"), dontpegtop=True) if LOOK else {}))
slant((288, 1024), (384, 1120), SE)
m.sector([(192, 1696), (352, 1696), (352, 1600), (288, 1600)], light=DARK, color=SKY,
         **dict(DOME, **dict(GAL, **low(UP))))                               # the bay of YELLOW's far side
slant((192, 1696), (288, 1600), NE, **(dict(upper=T("D"), dontpegtop=True) if LOOK else {}))
slant((288, 1600), (384, 1504), NE)
door((-32, 912), (32, 912), (0, 1), 0, "H", "A")
recess((288, 928), (352, 928), (0, -1), 0, 103, 201, color=SKY)              # the frame under the gallery
recess((256, 1696), (320, 1696), (0, 1), UP, far_id(YELLOW), 101, far_colour=YELLOW, color=SKY)
rail(((-320, 1056), (-256, 1056)), ((256, 1056), (320, 1056)),
     ((-256, 1056), (-256, 1344)), ((-256, 1408), (-256, 1440)),             # a gap on the west side
     ((256, 1056), (256, 1344)), ((256, 1408), (256, 1440)),                 # and on the east
     ((-128, 1568), (64, 1568)))                                             # and on the north
for a, b in (((-256, 1440), (-128, 1568)), ((256, 1440), (128, 1568))):      # the gallery's slanting fronts
    rail((a, b), **(dict(fit=(a, 192 / math.dist(a, b))) if LOOK else {}))
# the night room off the gallery: bolted inside
ajarmap.way_round(m, NX, NY, BLUE, floor=UP)
bolted((-32, 1696), (32, 1696), (0, 1), UP, NIGHT_BOLT, "A", None, line_id=304)
ajarmap.unbolt(m, (NX, NY + 32), (NX + 320, NY + 32), NIGHT_BOLT)

# === the roof, between the lane and the dome ======================================
fit((-992, 928, -400, 1696), [
    ((-464, 1216, -400, 1344), low(UP)),                                     # before the gallery's door
    ((-832, 1088, -704, 1216), SKYLIGHT),                                    # skylights
    ((-832, 1408, -704, 1536), SKYLIGHT),
], above=LOOK and T("YD"), floor=UP, light=NIGHT + 10, ftex=ROOFF, **ROOFO)
for corner in ([(-400, 1120), (-208, 928), (-400, 928)], [(-400, 1504), (-208, 1696), (-400, 1696)]):
    m.sector(corner, floor=UP, light=NIGHT + 10, ftex=ROOFF, **ROOFO)        # the roof runs in where the dome's corners were
    slant(corner[0], corner[1], **(dict(mid=T("YD")) if LOOK else {}))
front(((-400, 1120), (-400, 1216)), ((-400, 1344), (-400, 1504)), tex=T("YD"))    # the dome
door((-384, 1248), (-384, 1312), (-1, 0), UP, "A", "A", line_id=306)

# === the hillside, the ravine, the knoll ==========================================
# under the roof's north edge: steps up to it, and at their head a gap by a
# gatepost that no door fits through. With a door the way is down: off the roof
ajarmap.fitted(m, (-992, 1696, -400, 2000), [
    ((-464, 1952 - 32 * i, -400, 1984 - 32 * i), dict(floor=20 * (i + 1), ftex=PAVE, side=STONE))
    for i in range(8)] + [
    ((-464, 1696, -400, 1728), dict(floor=UP, ftex="AJTRIMF", side=STONE)),
    ((-416, 1696, -400, 1728), dict(floor=UP + 56, ftex="AJTRIMF", side=STONE)),
], floor=0, light=NIGHT, ftex="AJGRASS", **BUILT)
m.line((-464, 1696), (-416, 1696), id=ajarmap.SQUEEZE, blockmonsters=True)
rail(((-992, 1696), (-704, 1696)), ((-640, 1696), (-464, 1696)))             # a gap to jump down by
squeeze((-1008, 1800), (-1008, 1848), (1, 0), 0, FRONT, FRONT)               # the stile, from the lane
# the slope down to the ravine; the stump of the bridge tower has the frame
HILL = dict(floor=0, light=NIGHT, ftex="AJGRASS", **WILD)
ajarmap.fitted(m, (-992, 2000, -96, 2400), [((-672, 2128, -608, 2192), dict(floor=48, side=STONE)),
                                           ((-352, 2256, -288, 2320), dict(floor=48, side=STONE))], **HILL)
ajarmap.fitted(m, (-96, 2000, 32, 2272), [], **HILL)
fit((32, 2000, 800, 2400), [((32, 2272, 96, 2400), low()),
                            ((416, 2128, 480, 2192), dict(floor=48, side=STONE))], above=FRONT, **HILL)
over((32, 2400), (96, 2400), FRONT)                                          # the tower stump, from the ravine
windows(2000, (-256, 128, 256, 576))                                         # the back of the building
front(((-400, 2000), (-96, 2000)), ((-96, 2000), (32, 2000)), ((32, 2000), (800, 2000)))
front(((-96, 2272), (-96, 2400)), ((-96, 2272), (32, 2272)), ((-96, 2400), (32, 2400)))   # the tower's stump
recess((32, 2304), (32, 2368), (-1, 0), 0, 104, 201)                         # the hillside's frame
# the ravine: steps out of it at the west end, a cave at the foot of the far bank
# Its far bank west of the knoll has the cave in it, so nothing can lie on
# top of it: the sky comes down to 48 along its foot instead (SHELF), and the
# bank ends there, with the wood's tops over it.
SHELF = dict(ceil=48, wall="AJ7XR")
fit((-992, 2400, 800, 2592), [
    ((-992, 2576, -480, 2592), SHELF), ((-864, 2512, -704, 2592), SHELF),
] + [
    ((-768 - 32 * i, 2400, -736 - 32 * i, 2464), dict(floor=PIT + 16 * (i + 1), ftex=PAVE, side=STONE))
    for i in range(8)] + [
    ((-848, 2528, -720, 2592), low(PIT)),
    ((200, 2464, 328, 2528), dict(ftex="AJWATER")),
], above=LOOK and "AJ7XR", floor=PIT, light=NIGHT - 20, ftex=ROCKF, **WILD)
for a, b in (((-992, 2576), (-864, 2576)), ((-864, 2576), (-864, 2512)), ((-864, 2512), (-704, 2512)),
             ((-704, 2512), (-704, 2576)), ((-704, 2576), (-480, 2576))):
    m.line(a, b, mid="AJ7XT", midboth=True, upper="-", midraise=128)
m.sector(rect(-896, 2608, -672, 2672), floor=PIT, ceil=PIT + 112, light=140, wall=CAVEW, ftex=ROCKF)
m.sector(rect(-896, 2672, -672, 2800), floor=PIT, ceil=PIT + 112, light=140, wall=CAVEW, ftex=ROCKF,
         special=1024)
bolted((-816, 2592), (-752, 2592), (0, 1), PIT, CAVE, "A", "XG", line_id=307)
ajarmap.unbolt(m, (-896, 2672), (-672, 2672), CAVE)
ajarmap.stray_place(m, 1, (-896, 2704), (-896, 2768), (-1, 0), PIT, color=ROSE)
# Where the hill ends the wood is below it: a bank of rock to stop at, the
# tops of the trees over it, and beyond them the country under the stars.
def horizon(path, first, last, **ends):
    """`path` as ajarmap.beyond's. `first` and `last` are the walls the bank and
    the wood end against."""
    sky = dict(ceil=512, ctex="F_SKY1", light=NIGHT, wall="AJ7XN")
    caps, lines = ajarmap.beyond(m, path, [
        (16, dict(sky, floor=32, ftex="AJ7XR", side="AJ7XR")),
        (112, dict(sky, floor=-96, ftex="AJ7XK")),
        (144, dict(sky, floor=-96, ceil=32, ftex="AJ7XK", wall="AJ7XH")),
    ], **ends)
    for a, b in zip(path, path[1:]):
        m.line(a, b, blocking=True)                                          # nothing walks or flies off the hill
    for a, b in lines[0]:
        m.line(a, b, mid="AJ7XT", midboth=True, dontpegbottom=True)
    for end, tex in zip(caps, (first, last)):
        for a, b in end[:2]:
            m.line(a, b, mid=tex)


BACK = FRONT or "AJBRICK"
horizon([(800, 2000), (800, 2592), (416, 2592), (416, 2944)], BACK, BACK)    # east of the hill and of the knoll
horizon([(-992, 2592), (-992, 2000)], "AJ7XN", BACK)                         # west of the hill
horizon([(-480, 2944), (-480, 2592)], BACK, "AJ7XN", end=(-1, 0))            # west of the knoll
# the knoll: VIOLET's far side looks back across the ravine at the frame
fit((-480, 2592, 416, 2944), [
    ((128, 2880, 256, 2944), low()),
    ((-320, 2880, -192, 2944), low()),
    ((-416, 2720, -352, 2784), dict(floor=48, side=STONE)),
], above=FRONT, floor=0, light=NIGHT, ftex="AJGRASS", **WILD)
windows(2944, (-128, 0, 320))                                                # the transit house
front(((-480, 2944), (-320, 2944)), ((-192, 2944), (128, 2944)), ((256, 2944), (416, 2944)))
recess((160, 2944), (224, 2944), (0, 1), 0, far_id(VIOLET), 101, far_colour=VIOLET)
# the transit house: two locks. BLUE, and the lever of the cave
fit((-448, 2960, -64, 3280), [
    ((-288, 3088, -224, 3152), CASE),                                        # the transit instrument
    ((-128, 3216, -64, 3280), SEAT),
], floor=0, ceil=160, light=lux(170, 125), color=PLUM, **TRANSIT)
pictures("T", 3280, (-384, -256))
door((-288, 2944), (-224, 2944), (0, 1), 0, "A", "T", keys="34", line_id=303)
m.cut((-448, 3088), (-448, 3152))
m.line((-448, 3088), (-448, 3152), special=11, args=(CAVE, 32), playeruse=True, mid=f"AJ7LV{LOOK}" if LOOK else "AJLEVR", exact=True,
       id=308)

# === the west wing: one lock, off the lane =========================================
hall((-1632, 640, -1184, 1024), [((-1504, 768, -1376, 832)), ((-1312, 928, -1248, 992))], "WK", color=GOLD)   # workshop
hall((-1632, 1040, -1184, 1424), [((-1568, 1168, -1504, 1296)), ((-1312, 1168, -1248, 1296))], "WI")          # instruments
hall((-1632, 240, -1184, 624), [((-1440, 368, -1376, 496))], "WC", color=LEAF)                                # clocks
pictures("WK", -1632, (704, 896), "y")
pictures("WK", 640, (-1600, -1280))
pictures("WI", -1184, (1088, 1216, 1344), "y")
pictures("WI", 1040, (-1600, -1280))
pictures("WC", -1632, (256, 384, 512), "y")
pictures("WC", 240, (-1600, -1472, -1344, -1280))
pictures("WC", -1184, (320, 448), "y")
door((-1168, 800), (-1168, 864), (-1, 0), 0, "A", "WK", keys="1", line_id=301)
opening((-1440, 1024), (-1376, 1024), (0, 1), 0, "WK", "WI")
opening((-1440, 640), (-1376, 640), (0, -1), 0, "WK", "WC")
# the lens store (secret): a hole no door fits through, PINK, and a frame. Beyond
# its bars the armoury (secret): PINK's far side. The armoury's own door into the
# instrument room is bolted inside
m.sector(rect(-1632, 1440, -1424, 1648), ceil=112, light=150, color=ROSE, wall=LENSW, special=1024)
squeeze((-1560, 1424), (-1512, 1424), (0, 1), 0, "WI", LENSW)
m.sector(rect(-1408, 1440, -1184, 1504), ceil=112, light=150, color=ROSE, wall=ARMW)
m.sector(rect(-1408, 1504, -1184, 1648), ceil=112, light=150, color=ROSE, wall=ARMW, special=1024)
bars((-1424, 1528), (-1424, 1592), (1, 0), 0, LENSW, ARMW)
recess((-1560, 1648), (-1496, 1648), (0, 1), 0, 107, 201, color=ROSE)
recess((-1328, 1648), (-1264, 1648), (0, 1), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)
bolted((-1320, 1424), (-1256, 1424), (0, 1), 0, ARMOURY, "WI", "XA")
ajarmap.unbolt(m, (-1408, 1504), (-1184, 1504), ARMOURY)

# === the east wing: one lock, off the hall =========================================
hall((336, 528, 784, 848), [((432, 624, 688, 656)), ((432, 720, 688, 752))], "EL", color=GOLD)          # lecture room
pictures("EL", 848, (448, 576))
pictures("EL", 528, (384, 512, 640))
# the planetarium: eight-sided, under a dome in three steps, the projector in the middle
SKYBOX = (800, 528, 1248, 976)
SKYROOM = ajarmap.octagon(*SKYBOX, 96)
STEPS3 = [(ajarmap.octagon(864, 592, 1184, 912, 72), 208), (ajarmap.octagon(912, 640, 1136, 864, 56), 232),
          (ajarmap.octagon(960, 688, 1088, 816, 32), 248)]
fit(SKYBOX, [(ring, dict(ceil=h)) for ring, h in STEPS3] + [((992, 720, 1056, 784), PLINTH)],
    outline=SKYROOM, floor=0, ceil=176, light=lux(120, 100), **PLANET)
for ring, _ in STEPS3:
    for a, b in edges(ring):
        slant(a, b, upper=STARS) if a[0] != b[0] and a[1] != b[1] else m.line(a, b, upper=STARS)
for a, b in edges(SKYROOM):
    if a[0] != b[0] and a[1] != b[1]:
        slant(a, b)
hall((800, 992, 1248, 1376), [((864, 1120, 928, 1184)), ((1120, 1120, 1184, 1184))], "EO",
     plinths=[(992, 1056, 1056, 1120)], color=PLUM)                                                    # orrery
pictures("EO", 800, (1024, 1216), "y")
pictures("EO", 1248, (1024, 1216), "y")
pictures("EO", 1376, (832, 1152))
door((256, 688), (256, 752), (1, 0), 0, "H", "EL", keys="2", thick=80, line_id=302)
opening((784, 656), (784, 720), (1, 0), 0, "EL", LOOK and "EP")
opening((992, 976), (1056, 976), (0, 1), 0, LOOK and "EP", "EO")
over((992, 1376), (1056, 1376), LOOK and T("EO"))                            # the head of the cellar steps
# steps down to the cellar: the cistern, and past it a hole into an alcove (secret)
ajarmap.stairs(m, (992, 1376), (1056, 1376), (0, 1), 0, CELLAR, light=150, **STEPS)
CELL = dict(floor=CELLAR, ceil=0, light=140, wall=CELLW, ftex="AJPIT")
ajarmap.fitted(m, (800, 1632, 1376, 1968), [
    ((1120, 1728, 1312, 1904), dict(floor=CELLAR - 16, ftex="AJWATER")),
    ((848, 1840, 960, 1920), dict(CRATE, floor=CELLAR + 48)),     # a crate, 48 clear of the walls: a Stray door leans behind it
], **CELL)
m.sector(rect(1392, 1760, 1536, 1888), floor=CELLAR, ceil=CELLAR + 96, light=120, wall=CAVEW, ftex="AJPIT",
         special=1024)
squeeze((1376, 1800), (1376, 1848), (1, 0), CELLAR, CELLW, CAVEW)
m.cut((1424, 1888), (1488, 1888))                                            # in the alcove, beside the hole: the boiler house's lever
m.line((1424, 1888), (1488, 1888), special=11, args=(BOILER, 32), playeruse=True, mid="AJ6LVG" if LOOK else "AJLEVR",
       exact=True)

# --- doors and keys ----------------------------------------------------------
m.thing(0, -768, 1, angle=90)                                             # player start, on the road
ajarmap.door(m, RED, 320, -340, angle=270)                                # leaning by the gate
ajarmap.door(m, GREEN, 236, 800, angle=180)                               # leaning in the hall
ajarmap.door(m, YELLOW, -1612, 1380, angle=0)                             # leaning in the instrument room
ajarmap.door(m, VIOLET, 300, 2020, angle=90)                              # leaning on the hillside
ajarmap.door(m, BLUE, -428, 3240, angle=0)                                # leaning in the transit house
ajarmap.door(m, PINK, -1612, 1620, angle=0)                               # leaning in the lens store
ajarmap.stray(m, -1028, 1600, angle=180)                                  # Stray doors: in the lane
ajarmap.stray(m, -960, 960, angle=0)                                      # on the roof
ajarmap.stray(m, -820, 880, angle=180)                                    # on the stacks
ajarmap.stray(m, 820, 1940, angle=0)                                      # in the cellar
ajarmap.stray(m, -84, 3000, angle=180)                                    # in the transit house
ajarmap.key(m, 1, -896, 880)                                              # north end of the stacks
ajarmap.key(m, 2, 320, 1100)                                              # south end of the east gallery
ajarmap.key(m, 3, 1340, 1660)                                             # the cellar
ajarmap.key(m, 4, -1600, 280)                                             # the clock room

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACHNO, PAIN = 65, 69, 3003, 66, 3006, 3005, 67, 68, 71
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, LAMP = 34, 2028
TORCH_G, TORCH_B = 45, 55
POOL, BARREL = 24, 2035
BACKPACK = 8


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the road, the passage, the forecourt, the hall, the yard: lamps and nobody
things(LAMP, (-96, -352), (280, -416), (-96, -32), (96, -32), (-96, 480), (96, 480), (-500, 416), (-1136, 416))
for kind, spots in LAMPS.items():                                         # indoors: every lamp, and its pool of light
    things(kind, *spots)
things(20024, (192, 848), angle=200)                                      # the hall's globe
things(20021, (0, 1312), angle=90)                                        # the telescope, pointing out of the slit
things(20022, (1024, 752), angle=225)                                     # the planetarium's projector
things(20023, (1024, 1088), angle=270)                                    # the orrery
things(SHOTGUN, (0, 720))                                                 # for anyone who came without one
things(SHELLS, (-40, 760), (40, 760))
things(BACKPACK, (0, 820))
things(BERSERK, (-200, 720))                                              # by the library's door: it is full of teeth
things(STIM, (200, 720), (-500, 100))
things(BONUS, (-200, -700), (-200, -560), (0, 96), (0, 160))
# the lane: the first of them, round the corner
things(ZOMBIE, (-1090, 1000), (-1130, 1100), (-1060, 1340), (-1090, 1560), angle=270)
things(IMP, (-1140, 1240), (-1060, 1500), (-1090, 1900), angle=270)
things(SERGEANT, (-1050, 1700), (-1130, 1660), angle=270)
things(LAMP, (-1030, 480), (-1030, 1000), (-1030, 1960))
things(CLIP, (-1040, 700), (-1040, 740))
things(STIM, (-1140, 1980))
things(MEDIKIT, (-1140, 1320))
# the boiler house: do not open this door
things(MANCUBUS, (-1000, -120), angle=90)
things(KNIGHT, (-1120, -150), (-890, -150), angle=90)
things(SPHERE, (-1140, 20))
things(ROCKETBOX, (-880, 20), (-920, 20))
# the shed
things(PLASMA, (-1300, 1840))
things(CELLS, (-1400, 1780), (-1400, 1820))
things(MEGA, (-1220, 1900))
# the library: readers. From the stacks they are all below you
# A demon waits just inside the hall's door
things(IMP, (-700, 640), (-400, 690), (-700, 880), (-560, 752), (-380, 810), (-330, 600), angle=0)
things(DEMON, (-600, 610), (-500, 880), (-740, 760), (-320, 740), angle=0)
things(SERGEANT, (-670, 760), (-420, 620), (-570, 880), angle=0)
things(SPECTRE, (-760, 700), (-320, 880), angle=0)
things(KNIGHT, (-720, 820), angle=0)
things(CACO, (-510, 620), angle=0, ambush=True)
things(SHELLS, (-544, 704), (-544, 800))                                    # at the tables' edges: within reach
things(MEDIKIT, (-300, 890))
# the stacks: key 1, a chaingun, a rocket launcher for the readers below, and
# a quiet reader or two
things(ZOMBIE, (-900, 700), (-850, 600), angle=0)
things(CHAINGUN, (-900, 800))
things(LAUNCHER, (-850, 760))
things(ROCKETBOX, (-850, 680))
things(AMMOBOX, (-940, 890))
things(SHELLBOX, (-830, 560))
things(STIM, (-960, 590))
# the dome: the night's observers, round the telescope
things(BARON, (-170, 1396), (170, 1396), angle=270)
things(KNIGHT, (0, 1160), angle=270)
things(REVENANT, (-120, 1520), (120, 1520), angle=270)
things(IMP, (-240, 1030), (240, 1030), (-200, 1020), (200, 1040), (-150, 1320), (150, 1320), angle=270)
things(DEMON, (-220, 1150), (220, 1150), angle=270)
things(MANCUBUS, (0, 1500), angle=270, ambush=True)
things(SHELLBOX, (-160, 1480))
things(MEDIKIT, (160, 1480), (-160, 950))
things(ROCKETS, (-40, 1410), (40, 1410))
# the gallery: key 2, cells, and those who watch from above
things(CHAINGUNNER, (-320, 1500), (320, 1500), angle=270)
things(IMP, (-320, 1120), (-100, 1630), (140, 1610), angle=270)
things(SERGEANT, (320, 1230), angle=270)
things(REVENANT, (60, 1600), angle=270)
things(PLASMA, (-200, 1640))
things(CELLS, (-220, 1620), (-280, 1560), (328, 1650))
things(ROCKETBOX, (64, 1664))
things(STIM, (-340, 1500), (350, 1400))
things(MEDIKIT, (-340, 1160))
# the night room: someone has been waiting
things(REVENANT, (NX + 160, NY + 128), angle=270)
things(KNIGHT, (NX + 224, NY + 224), angle=270)
# the roof
things(IMP, (-940, 1040), (-600, 980), (-940, 1300), (-560, 1620), angle=0)
things(SERGEANT, (-640, 1300), (-900, 1620), angle=0)
things(CHAINGUNNER, (-520, 1100), (-940, 1500), angle=0)
things(CACO, (-640, 1100), (-620, 1500), angle=0, ambush=True)
things(REVENANT, (-560, 1400), angle=0)
things(SUPER, (-768, 1310))
things(SHELLS, (-768, 1270), (-768, 1350))
things(MEDIKIT, (-960, 1660), (-960, 1180))
things(ARMOR, (-430, 960))
# the hillside
things(IMP, (-900, 1800), (-700, 1900), (-560, 2100), (-200, 2100), (500, 2060), angle=270)
things(DEMON, (-800, 2200), (-460, 2300), (200, 2200), (600, 2300), angle=270)
things(SPECTRE, (-900, 2320), (700, 2100), angle=270)
things(KNIGHT, (300, 2240), angle=270)
things(SOUL, (-600, 2000), (100, 2100), (560, 2200), angle=270)
things(SERGEANT, (-760, 2060), (520, 2330), angle=270)
things(CHAINGUNNER, (740, 2240), angle=180)
things(CACO, (0, 2140), angle=270, ambush=True)
things(LAMP, (60, 2250), (-560, 1730))
things(SHELLS, (-760, 1760), (-500, 2060))
things(SHELLBOX, (-940, 1740))
things(STIM, (700, 2360), (-960, 2040))
things(MEDIKIT, (-900, 2380), (300, 2380))
things(ROCKETS, (-640, 2224))
# the ravine and its cave
things(SPECTRE, (-400, 2500), (0, 2520), (700, 2500), angle=180)
things(DEMON, (-600, 2540), (400, 2460), angle=180)
things(IMP, (-900, 2520), (100, 2560), angle=0)
things(MEDIKIT, (760, 2560))
things(SHELLBOX, (-960, 2560))
things(SPHERE, (-720, 2760))
things(CELLS, (-700, 2640), (-740, 2640))
things(SPECTRE, (-800, 2740), angle=270)
things(CANDLE, (-872, 2632), (-696, 2632))
# the knoll: the house's garden
things(REVENANT, (-100, 2700), (300, 2760), angle=270)
things(IMP, (-300, 2660), (60, 2860), (360, 2640), angle=270)
things(KNIGHT, (-150, 2840), angle=270)
things(CHAINGUNNER, (380, 2800), angle=270)
things(LAMP, (-340, 2912), (-170, 2912), (110, 2912), (274, 2912))
things(MEDIKIT, (-440, 2900), (0, 2620))
things(SHELLBOX, (-440, 2860))
things(ROCKETBOX, (380, 2900))
# the transit house: the astronomer, working late, and deaf to the garden
things(BARON, (-160, 3120), angle=270, ambush=True)
things(KNIGHT, (-380, 3040), angle=270, ambush=True)
things(MEDIKIT, (-200, 3250))
things(CELLS, (-340, 3250))
# the west wing: the workshop, the instruments, the clocks
things(ZOMBIE, (-1300, 700), (-1560, 700), (-1300, 1100), angle=0)
things(IMP, (-1560, 960), (-1240, 860), (-1560, 1100), (-1260, 1350), (-1560, 560), (-1240, 300), angle=0)
things(SERGEANT, (-1440, 900), (-1400, 1340), (-1300, 560), angle=0)
things(DEMON, (-1440, 700), (-1400, 1100), (-1500, 420), angle=0)
things(CHAINGUNNER, (-1600, 1380), (-1240, 580), angle=0)
things(REVENANT, (-1500, 300), angle=0)
things(PAIN, (-1400, 1220), angle=0)
things(SHELLS, (-1220, 680), (-1600, 1000))
things(MEDIKIT, (-1210, 1064), (-1600, 600))
things(STIM, (-1600, 680), (-1220, 1300))
things(AMMOBOX, (-1220, 270))
# the lens store and the armoury
things(CANDLE, (-1608, 1464), (-1448, 1464))
things(HELMET, (-1460, 1620))
things(LAUNCHER, (-1296, 1560))
things(ROCKETBOX, (-1380, 1620), (-1210, 1620))
things(MEGA, (-1380, 1470))
things(AMMOBOX, (-1210, 1470))
# the east wing: the lecture room, the planetarium, the orrery
things(ZOMBIE, (400, 580), (720, 580), (400, 800), angle=180)
things(IMP, (560, 580), (720, 800), (910, 650), (1130, 650), (910, 860), (1180, 1040), (860, 1320), angle=180)
things(SERGEANT, (560, 690), (1130, 860), (1180, 1320), angle=180)
things(DEMON, (720, 690), (1020, 900), (1100, 1310), angle=180)
things(SPECTRE, (900, 760), (1150, 760), angle=180)
things(CHAINGUNNER, (1200, 690), (880, 1070), angle=180)
things(ARACHNO, (1024, 620), angle=270)
things(CACO, (1024, 1220), angle=270, ambush=True)
things(REVENANT, (1210, 1250), angle=180)
things(SHELLBOX, (760, 552))
things(AMMOBOX, (400, 552))
things(MEDIKIT, (1224, 1016), (360, 824), (1224, 1180))
things(STIM, (824, 1352), (1224, 760))
things(ROCKETS, (1024, 1340), (1064, 1340))
# the cellar and its alcove
things(SPECTRE, (890, 1730), (1000, 1900), (1340, 1880), angle=90)
things(DEMON, (1000, 1790), (1100, 1670), (1340, 1700), angle=90)
things(IMP, (880, 1890), (1216, 1800), (1200, 1680), angle=90)
things(SOUL, (1100, 1940), (1250, 1940), angle=90)
things(LODGER, (1024, 1700), args=(300,))
things(TORCH_G, (824, 1656), (1352, 1944))
things(MEDIKIT, (830, 1790))
things(ARMOR, (1500, 1824))
things(SHELLBOX, (1500, 1780))
things(CELLS, (1500, 1868))
things(CANDLE, (1416, 1784), (1416, 1864))

# --- ambushes: what taking a key brings (ajarmap.ambush) ----------------------
# key 3, in the cellar: out of the dark
ajarmap.ambush(m, 3, SPECTRE, (1000, 1700), (880, 1770), angle=0)
ajarmap.ambush(m, 3, DEMON, (1060, 1930), angle=0)
# key 4, in the clock room: the clocks strike, one after another, and each
# brings somebody worse (Vadim, 2026-11-17: no two ambushes alike)
ajarmap.ambush(m, 4, IMP, (-1300, 300), angle=180)
ajarmap.ambush(m, 4, SERGEANT, (-1340, 590), angle=180, after=2)
ajarmap.ambush(m, 4, CHAINGUNNER, (-1500, 560), angle=180, after=4)
ajarmap.ambush(m, 4, REVENANT, (-1250, 430), angle=180, after=6)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "grounds" is the gate passage, the forecourt, the hall, the library, the
# dome, the yard, the lane, and also the boiler house and the shed, which
# open from inside. "gallery" is the dome's gallery and the roof; "hillside"
# is the ravine and its cave too; "east" the east wing and the cellar; "west"
# the west wing. a is the gate's bolt, b the night room's. The lens store,
# the armoury and PINK are left out: PINK never leaves, and nothing else
# needs it.
PUZZLE = dict(
    start="road", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("road", "grounds", "a"), ("grounds", "road", "a"),
          ("stacks", "grounds"), ("gallery", "grounds"), ("gallery", "hillside"),
          ("hillside", "gallery", "", "squeeze"),                               # the steps and the gatepost
          ("gallery", "night", "b"), ("night", "gallery", "b"),
          ("grounds", "hillside", "", "squeeze"), ("hillside", "grounds", "", "squeeze"),   # the stile
          ("knoll", "hillside"),
          ("knoll", "house", "34"), ("house", "knoll", "34"),
          ("grounds", "west", "1"), ("west", "grounds", "1"),
          ("grounds", "east", "2"), ("east", "grounds", "2")],
    keys={"1": "stacks", "2": "gallery", "3": "east", "4": "west", "a": "grounds", "b": "night"},
    auto="ab",
    frames={101: "road", 102: "grounds", 103: "grounds", 105: "grounds", 104: "hillside",
            ajarmap.HOME: "night"},
    doors={
        RED: dict(home="grounds", lean="road"),
        GREEN: dict(home="stacks", lean="grounds"),
        YELLOW: dict(home="gallery", lean="west"),
        VIOLET: dict(home="knoll", lean="hillside"),
        BLUE: dict(home="night", lean="house"),
    },
    pool=["grounds", "hillside"],          # the boiler house; the cave
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
