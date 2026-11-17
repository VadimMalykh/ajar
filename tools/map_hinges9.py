"""Act 1, level 9: "Putting You Through" (MAP09).

A telephone exchange at night. One new thing (Vadim's idea, 2026-11-16): the
way out is a chain. The night room ("the line", ajarmap.way_through) has
nothing in it but the far sides of BLUE and VIOLET, one at each end. The
trunk room has two brass frames, facing each other (ajarmap.brass_pair). Hang
BLUE and VIOLET there, either way round, and the two rooms open onto each
other without end. Walk through into the line and out of it again: that is
the way out.

Until then the line is a dead end with two door backs in it, high in the
wall over the forecourt (a hole lets you drop out of it, never in). But with
BLUE and VIOLET hung in any two frames it is a way between them, for you and
for whatever you carry: and that is what the level asks for first.

The catch. VIOLET leans in the test room, and the only way in or out of
there is a hatch no door fits through. The test room has a frame. Hang
VIOLET in it and you are on the line without it. To get VIOLET out another
door must hang in that frame instead, and a door comes into the test room
only along the line: through BLUE, hung somewhere, and VIOLET's far side.
Then VIOLET leaves through the door it was swapped for.

The trunk room is a place doors come into from above only: off the cable
loft, which opens off the supervisor's gallery (GREEN's far side; the roof,
RED's, lets down onto it). Its way in from the switchroom is a hatch; a chute
lets a door out again, into the battery room.

Rebuilt 2026-11-16 (Vadim: it was MAP08's plan with the rooms renamed). The
puzzle is the one above; the building and the way into it are its own:

- The switchroom is a long hall, east to west. The supervisor's gallery runs
  along its north wall, the monitor's balcony is its south-west corner.
- You start on the roof, under the sky, having come over the roofs: key 1
  is in its other corner, and a hole lets down onto the gallery, over a
  switchroom full of the night shift. There is no way back up but RED,
  which leans in the call office and whose far side is on the roof.
- West wing, open: canteen, rest room (GREEN, a frame), and the cloakroom
  (key 1), where key 2 is.
- East wing (keys 2 and 3): apparatus room, relay room, and off the
  apparatus room the test room. The thief is back (not seen since MAP04):
  it lives in the east wing with YELLOW on its back, and has no frame there
  to hang it in: it is to be caught.
- The repainter is new (enemies.zs): it goes about the switchroom, and any
  two doors left hanging or leaning where it can get at them change places.
- North-east, under the trunk room's chute: the battery room, down stairs
  from the cable passage, and key 3 in its far corner; off the passage the
  generator room.
- The forecourt is the last place you see, not the first: out by the front
  door from the call office. The line hangs over its east end, the kiosk is
  at its west end.

Shuffled 2026-11-17 (Vadim: still too like MAP08: the start outside the
front door, a wing on key 1 and a wing on key 2, the office on 3 and 4, the
same secrets in the same places, a cellar of demons). The puzzle and the
rooms stayed; the start, the keys, the locks, the secrets and who is in the
cellar moved.

Places. The roof (start; RED's far side; key 1). The supervisor's gallery
and the cable loft north of it (GREEN's). The call office, the forecourt,
the switchroom, the cable passage and the battery room under it (key 3) are
one place to walk about in, and the west wing with them. The cloakroom
(key 1): key 2. The monitor's balcony (YELLOW's; key 4). The manager's
office (key 4): BLUE.

Secrets: the kiosk in the forecourt (a lever at the trunk positions puts a
call through and draws its bolt, or a Stray door); the stationery store
behind the cloakroom's coats (a squeeze; PINK and a frame) and beyond its
bars the strongroom (PINK's far side); an alcove behind the cable drums in
the loft.
"""
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


UP, ROOF, PIT = 160, 320, -128
LINE = 96                                             # the floor of the night room, over the forecourt
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True, floorpeg=True)
SEAT = dict(ftex="AJSOFA", side="AJSOFA", floor=16)
CASE = dict(ftex="AJSTEEL", side="AJWOOD", floor=40)  # a counter, a desk
BOARD = dict(ftex="AJSTEEL", side="AJWOOD", floor=88)   # a switchboard
RACK = dict(ftex="AJSTEEL", side="AJSTEEL", floor=128)  # a rack of selectors
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
PATH = dict(ftex="AJARCHF")
KIOSK, GENERATOR, STRONG = 401, 403, 405
NX, NY = 760, -560                                    # the night room's south-west corner
NIGHT = 150                                           # light under the sky

# The exchange's look (gfx_exchange.py), chosen from a board of three
# (user, 2026-11-17, design/map09-board.html): 1 Central, a manual exchange
# of the 1900s: red brick and terracotta, mahogany, glazed tile, brass. The
# two that lost can still be built to compare: AJAR_EXCHANGE=2 Trunk (the
# 1930s), 3 Crossbar (the 1960s), 0 the plain textures the level was built
# in. A look changes textures only: no floor, wall or railing moves. Rooms
# are not tinted in a look.
LOOK = (os.environ.get("AJAR_EXCHANGE") or "1").replace("0", "")
FACES = {}                  # the door faces this build needs, and their textures: gfx_exchange.make draws them


def T(tag):
    return f"AJ9{tag}{LOOK}"


import gfx_exchange
if LOOK:
    m.align = gfx_exchange.aligned(LOOK)
    WARM = GOLD = SKY = LEAF = PLUM = ROSE = None
    FRONT, ROUND, STREET = T("Y"), T("K"), "AJ9XS"
    LOWW, HIGHW, PORCH, HOLE = T("HP"), T("HQ"), T("CP"), "AJTRIM"
    YARD = dict(ceil=512, ctex="F_SKY1", wall=STREET)                     # the houses across the road; the front is named
    OPEN = dict(ceil=512, ctex="F_SKY1", wall=ROUND)                      # the roof
    RAIL = dict(RAIL, mid=T("RL"))
    SEAT = dict(ftex=T("BN"), side=T("BN"), floor=16)
    GSEAT = dict(ftex=T("PL"), side=T("PL"), floor=16)                    # a stone seat out of doors
    CASE = dict(ftex=T("VT"), side=T("V"), floor=40)
    BOARD = dict(ftex=T("ST"), side=T("S"), floor=88)
    RACK = dict(ftex=T("RT"), side=T("R"), floor=128)
    BOOTH = dict(ftex=T("WD"), side=T("BS"), floor=128)                   # a call box: its front is named
    WOOD = dict(ftex=T("WD"), side=T("WD"))
    DRUM = dict(ftex="AJ9XD", side="AJ9XD")
    PEGS = dict(ftex=T("WD"), side="AJ9XK", floor=96)                     # coats
    CELL = dict(floor=PIT + 40, ftex="AJ9XJT", side="AJ9XJ")
    PATH, WALK = dict(ftex=T("P")), dict(ftex=T("FT"))
    YARDF, ROOFF = T("FA"), T("FR")
    CALL = dict(wall=T("L"), ftex=T("F"), ctex=T("CL"))
    MANAGER = dict(wall=T("MG"), ftex=T("FO"), ctex=T("CD"))
    SWITCH = dict(wall=T("H"), ftex=T("F"), ctex=T("CA"))
    GAL = BAL = dict(floor=UP, ftex=T("FG"), side=T("GV"))
    SKYLIGHT = dict(floor=ROOF + 40, ftex=T("FL"), side=T("FL"), light=255)
    LOFTW, SHAFT = "AJ9XC", dict(ceil=288, wall=T("TRH"))
    TRUNK = dict(wall=T("TR"), ftex=T("FS"), ctex=T("CD"))
    BATTERY, PASSAGE = dict(wall="AJ9XB", ftex="AJPIT"), dict(wall="AJ9XP", ftex="AJBOARD")
    APPARATUS = dict(wall=T("AP"), ftex=T("FE"), ctex=T("CL"))
    TEST = dict(wall=T("TS"), ftex=T("FE"), ctex=T("CD"))
    GENW, KIOSKW, STOREW, ALCOVEW = "AJ9XG", "AJ9XN", "AJ9XL", "AJ6XC"
    BELL = "AJTARG9"

    def wing(tag, east):
        return dict(wall=T(tag), ftex=T("FE" if east else "FD"), ctex=T("CD"))
else:
    FRONT = ROUND = STREET = LOWW = HIGHW = None
    PORCH, HOLE = "AJBOARD", "AJBRICK"
    YARD = OPEN
    GSEAT, WALK = SEAT, PATH
    BOOTH, DRUM, PEGS = dict(WOOD, floor=128), WOOD, dict(WOOD, floor=96)
    CELL = dict(floor=PIT + 40, ftex="AJWATER", side="AJSTEEL")
    YARDF, ROOFF = "AJGRASS", "AJSTEEL"
    CALL = SWITCH = TRUNK = APPARATUS = dict(wall="AJBRICK", ftex="AJFLOOR")
    MANAGER = TEST = {}
    GAL = dict(floor=UP, ftex="AJSTEEL", side="AJSTEEL")
    BAL = dict(floor=UP, ftex="AJBOARD", side="AJWOOD")
    SKYLIGHT = dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")
    LOFTW, SHAFT = "AJBRICK", dict(ceil=288)
    BATTERY, PASSAGE = dict(wall="AJBRICK", ftex="AJPIT"), dict(wall="AJBRICK", ftex="AJBOARD")
    GENW = KIOSKW = STOREW = ALCOVEW = "AJSAFE"
    BELL = "AJTARG"

    def wing(tag, east):
        return {}


def low(floor=0, wall=None):
    """A porch: doors and frames in tall rooms and under the sky stand under one.
    In a look `wall` is the wall under it (default: the switchroom's own, where
    all the indoor porches are: its ground floor's, or its gallery's)."""
    return dict(dict(ceil=floor + 128, ctex=PORCH), **(dict(wall=wall or (LOWW if floor == 0 else HIGHW)) if LOOK else {}))


def _wall(tag):
    return tag and (tag if tag.startswith("AJ") else "AJ9" + tag if tag.startswith("X") else T(tag))


def over(a, b, tex):
    """In a look: the wall over the opening a-b (under a lower ceiling) carries
    on as `tex`, in line with the wall beside it; and so does the wall under
    it, where the opening's floor is higher than the room's."""
    if LOOK and tex:
        m.line(a, b, upper=_wall(tex), lower=_wall(tex), dontpegtop=True, dontpegbottom=True)


def fit(box, features, above=None, **base):
    """ajarmap.fitted: a room with furniture. In a look the walls over the open
    sides of its porches (low()) carry on as `above` (default: the room's own wall)."""
    ajarmap.fitted(m, box, features, **base)
    for shape, change in features if LOOK else ():
        if change.get("ctex") != PORCH:
            continue
        x1, y1, x2, y2 = shape
        for a, b, on_wall in (((x1, y1), (x2, y1), y1 == box[1]), ((x2, y1), (x2, y2), x2 == box[2]),
                              ((x2, y2), (x1, y2), y2 == box[3]), ((x1, y2), (x1, y1), x1 == box[0])):
            if not on_wall:
                m.line(a, b, upper=above or base.get("wall"), dontpegtop=True)


def rail(*runs):
    for a, b in runs:
        m.cut(a, b)
        m.line(a, b, **RAIL)


def pieces(tex, fixed, starts, axis="x"):
    """In a look: 64-long pieces of a wall in the textures `tex`, by turns. Each
    starts at a multiple of 64. Declared before front()."""
    for i, s in enumerate(starts if LOOK else ()):
        a, b = ((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
        m.cut(a, b)
        m.line(a, b, mid=tex[i % len(tex)])


def front(*runs):
    """In a look: these pieces of the forecourt's wall are the exchange's front."""
    for a, b in runs if LOOK else ():
        m.line(a, b, mid=FRONT)


def _face(kind, tag, a, out, keys=""):
    """The face of a door whose mouth starts at `a` in the wall `tag`, seen by
    someone the door goes `out` from: the wall carries on over the leaf."""
    lo = a[0] if out[0] == 0 else a[1]
    s = lo % 64 if out in ((0, 1), (-1, 0)) else -lo % 64
    return FACES.setdefault((LOOK, kind, tag, s, keys), f"AJ9{kind}{LOOK}{len(FACES):02d}")


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
    the walls it stands in (tags of gfx_exchange's: "L", "XP"...)."""
    ajarmap.roomdoor(m, a, b, out, floor, **k)
    _doors("D", a, b, out, near, far, k.get("thick", 16), k.get("keys", ""))


def bolted(a, b, out, floor, tag, near, far, **k):
    """A bolted door; `near`, `far` as door()'s, None for a side that stays as it is."""
    ajarmap.bolted(m, a, b, out, floor, tag, **k)
    _doors("Z", a, b, out, near, far, k.get("thick", 16))


def _far(a, b, out, thick):
    return (a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick)


def opening(a, b, out, floor, near, far, thick=16):
    """An open way between two rooms; in a look their walls carry on round it."""
    ajarmap.opening(m, a, b, out, floor, thick=thick)
    over(a, b, near)
    over(*_far(a, b, out, thick), far)


def squeeze(a, b, out, floor, near, far, thick=16):
    ajarmap.squeeze(m, a, b, out, floor, thick=thick)
    over(a, b, near)
    over(*_far(a, b, out, thick), far)


def bars(a, b, out, floor, near=None, far=None, thick=16):
    """A barred opening in a wall: to look and shoot through. In a look, `near`
    and `far` are the walls it is cut through on either side."""
    c, d = _far(a, b, out, thick)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall=HOLE,
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)
    over(a, b, near)
    over(c, d, far)


def hall(box, cases, tag, east=False, **k):
    """A room of the wings: 160 high, with furniture."""
    fit(box, cases, **dict(dict(ceil=160, light=175), **dict(k, **wing(tag, east))))


# === the forecourt, the line over its east end ===================================
# out by the front door. The kiosk is behind bars at the west end; high in
# the north wall, to the east, a hole shows a starry ceiling
fit((-512, -832, 1100, -576), [
    ((-64, -832, 64, -576), WALK),
    ((-64, -640, 64, -576), low(wall=T("YP"))),                              # before the front door
    ((-512, -816, -448, -624), low(wall="AJ9XT")),                           # before the kiosk
    ((-320, -800, -192, -768), GSEAT), ((192, -800, 320, -768), GSEAT), ((640, -800, 768, -768), GSEAT),
], above=FRONT, floor=0, light=NIGHT, ftex=YARDF, **YARD)
if LOOK:
    for a, b in (((-512, -816), (-448, -816)), ((-448, -816), (-448, -624)), ((-448, -624), (-512, -624))):
        m.line(a, b, upper=STREET, dontpegtop=True)                          # over the kiosk's porch
pieces((T("YB"), T("YA"), T("YA"), T("YA"), T("YA"), T("YB"), T("YA"), T("YB"), T("YB")), -576,
       (-448, -320, -192, 128, 256, 448, 576, 704, 1024))                    # the exchange's windows
front(((-512, -576), (-64, -576)), ((64, -576), (888, -576)), ((952, -576), (1100, -576)))
pieces(("AJ9XSA",), -832, (-384, -128, 384, 832))                            # somebody is still up, across the road
# the line: BLUE's far side at its west end, VIOLET's at its east end, and a
# hole to drop out by
ajarmap.way_through(m, NX, NY, BLUE, VIOLET, floor=LINE)
m.sector(rect(NX + 128, NY - 16, NX + 192, NY), floor=LINE, ceil=LINE + 96, light=150, wall=HOLE,
         ftex="AJTRIMF", ctex="AJTRIMF")
over((NX + 128, NY - 16), (NX + 192, NY - 16), FRONT)
# the kiosk (secret), seen through bars: there is nothing to shoot. A lever at
# the trunk positions puts a call through to it, and its bolt is drawn. One of
# the places a Stray door opens onto
m.sector(rect(-592, -816, -528, -624), ceil=112, light=170, color=ROSE, wall=KIOSKW)
m.sector(rect(-784, -816, -592, -624), ceil=112, light=170, color=ROSE, wall=KIOSKW, special=1024)
bolted((-512, -800), (-512, -736), (-1, 0), 0, KIOSK, "XT", "XN", line_id=305)
ajarmap.unbolt(m, (-592, -816), (-592, -624), KIOSK)
bars((-512, -704), (-512, -640), (-1, 0), 0, "XT", KIOSKW)
ajarmap.stray_place(m, 1, (-720, -816), (-656, -816), (0, -1), 0, color=ROSE)

# === the call office ==============================================================
# wide and shallow: RED, a frame, call boxes, the manager's two locks, the way on
fit((-384, -560, 384, -304), [
    ((-64, -560, 64, -304), PATH),
    ((128, -544, 192, -480), BOOTH), ((224, -544, 288, -480), BOOTH),        # call boxes
    ((320, -544, 384, -480), BOOTH),
    ((-320, -416, -192, -352), CASE),                                        # the counter
    ((-320, -544, -192, -512), SEAT),
], floor=0, ceil=192, light=185, **CALL)
if LOOK:
    for x in (128, 224, 320):
        m.line((x, -480), (x + 64, -480), lower=T("B"))                      # their doors
door((-32, -576), (32, -576), (0, 1), 0, "YP", "L")
recess((384, -464), (384, -400), (1, 0), 0, 101, 201)                        # the call office's frame
m.sector(rect(-96, -304, 96, -288), ceil=160, light=185, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
over((-96, -304), (96, -304), "L")
over((-96, -288), (96, -288), "H")
# the manager's office: one lock, the last key. BLUE
fit((-720, -560, -400, -304), [
    ((-592, -464, -528, -400), CASE),                                        # the desk
    ((-720, -368, -656, -304), SEAT),
], floor=0, ceil=128, light=170, color=PLUM, **MANAGER)
door((-384, -464), (-384, -400), (-1, 0), 0, "L", "MG", keys="4", line_id=303)

# === the switchroom: a long hall, its gallery along the north wall, its balcony
# in the south-west corner ===========================================================
fit((-768, -288, 768, 224), [
    ((-64, -288, 64, 96), PATH),
    ((-768, -32, -704, 96), low()),                                          # before the west wing's door
    ((704, -232, 768, -104), low()),                                         # before the east wing's
    ((704, 80, 768, 208), low()),                                            # before the cable passage's
    ((416, -288, 544, -224), low()),                                         # before the switchroom's frame
    ((384, 160, 512, 224), low()),                                           # before the hatch to the trunk room
    ((-768, 96, 384, 224), GAL),
    ((-480, 160, -352, 224), dict(GAL, **low(UP))),                          # before GREEN's far side
    ((160, 160, 288, 224), dict(GAL, **low(UP))),                            # before the way into the loft
    ((-768, -288, -512, -32), BAL),
    ((-768, -224, -704, -96), dict(BAL, **low(UP))),                         # before YELLOW's far side
    ((-384, -192, -128, -160), BOARD), ((-384, -64, -128, -32), BOARD),      # switchboards, in ranks along the hall
    ((128, -192, 384, -160), BOARD), ((128, -64, 384, -32), BOARD),
    ((480, -96, 672, -64), BOARD), ((480, 32, 672, 64), BOARD),
    ((-288, -128, -224, -96), SEAT), ((224, -128, 288, -96), SEAT),
], floor=0, ceil=448, light=180, color=SKY, **SWITCH)
recess((-448, 224), (-384, 224), (0, 1), UP, far_id(GREEN), 101, far_colour=GREEN, color=SKY)
recess((-768, -192), (-768, -128), (-1, 0), UP, far_id(YELLOW), 101, far_colour=YELLOW, color=SKY)
recess((448, -288), (512, -288), (0, -1), 0, 102, 201, color=SKY)            # the switchroom's frame
rail(((-768, 96), (-256, 96)), ((-192, 96), (384, 96)), ((384, 96), (384, 224)))        # a gap over the switchroom
rail(((-768, -32), (-512, -32)), ((-512, -32), (-512, -128)), ((-512, -192), (-512, -288)))   # and one in the balcony's

# === the roof (RED's far side): a hole lets down onto the gallery ==================
fit((-1344, 304, -528, 928), [
    ((-992, 864, -864, 928), low(ROOF, wall=T("KA"))),                       # before RED's far side
    ((-1216, 432, -1088, 560), SKYLIGHT),                                    # skylights
    ((-896, 496, -768, 624), SKYLIGHT),
    ((-1216, 688, -1088, 816), SKYLIGHT),
], floor=ROOF, light=NIGHT + 10, ftex=ROOFF, **OPEN)
m.sector(rect(-640, 240, -576, 304), floor=ROOF, light=NIGHT + 10, ftex=ROOFF, **OPEN)
recess((-960, 928), (-896, 928), (0, 1), ROOF, far_id(RED), 101, far_colour=RED)
opening((-640, 224), (-576, 224), (0, 1), ROOF, "H", ROUND)

# === the cable loft, the trunk room under its edge =================================
# The loft opens off the gallery's east end. From it a hole lets down into the
# trunk room: the only way in there with a door
LOFT = dict(floor=UP, ceil=320, light=150, wall=LOFTW, ftex="AJBOARD")
opening((192, 224), (256, 224), (0, 1), UP, "HQ", LOFTW)
m.sector(rect(192, 240, 256, 576), **LOFT)
fit((192, 576, 848, 800), [
    ((320, 672, 448, 736), dict(DRUM, floor=UP + 48)),                       # cable drums
    ((704, 640, 768, 768), dict(DRUM, floor=UP + 48)),
], **LOFT)
m.sector(rect(560, 560, 624, 576), floor=UP, ceil=UP + 96, light=150, wall="AJTRIM", ftex="AJTRIMF",
         ctex="AJTRIMF")
over((560, 576), (624, 576), LOFTW)
over((560, 560), (624, 560), "TRH")
# an alcove behind the drums (secret)
m.sector(rect(616, 816, 744, 944), floor=UP, ceil=UP + 96, light=120, wall=ALCOVEW, ftex="AJBOARD", special=1024)
squeeze((656, 800), (704, 800), (0, 1), UP, LOFTW, ALCOVEW)
# the trunk room: two brass frames, and nothing else to hang a door in
fit((336, 304, 848, 560), [
    ((336, 400, 848, 464), ajarmap.RUNNER),
    ((528, 464, 656, 560), SHAFT),                                           # under the hole
    ((400, 336, 528, 368), BOARD), ((656, 336, 784, 368), BOARD),            # the trunk positions
], rug="AJXR2", floor=0, ceil=160, light=170, color=GOLD, **TRUNK)
if LOOK:
    for a, b in (((528, 464), (656, 464)), ((528, 464), (528, 560)), ((656, 464), (656, 560))):
        m.line(a, b, upper="AJ9XH")                                          # the shaft's own sides
ajarmap.brass_pair(m, (336, 400), (336, 464), (848, 400), (848, 464), 0, BLUE, VIOLET)
squeeze((424, 224), (472, 224), (0, 1), 0, "HP", "TR", thick=80)              # the hatch, from the switchroom
m.cut((560, 304), (624, 304))                                                # between the trunk positions: the kiosk's lever
m.line((560, 304), (624, 304), special=11, args=(KIOSK, 32), playeruse=True, mid="AJLEVR", exact=True, id=307)
m.sector(rect(848, 496, 864, 560), ceil=96, light=150, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")   # the chute
over((848, 496), (848, 560), "TR")
over((864, 496), (864, 560), BATTERY["wall"])

# === the battery room, the cable passage ==========================================
# a chute down from the trunk room; stairs up to the passage
fit((864, 480, 1504, 928), [
    ((960, 672, 1088, 864), CELL),                                           # cells
    ((1184, 672, 1312, 864), CELL),
    ((1056, 512, 1248, 576), CELL),
], floor=PIT, ceil=128, light=140, **BATTERY)
recess((1100, 928), (1164, 928), (0, 1), PIT, 105, 201)                      # the battery room's frame
ajarmap.stairs(m, (1408, 224), (1472, 224), (0, 1), 0, -128, ceil=128, light=150, wall=BATTERY["wall"],
               ftex="AJBOARD")
fit((784, 80, 1472, 224), [
    ((896, 80, 1024, 112), dict(WOOD, floor=48)),
    ((1216, 192, 1280, 224), dict(WOOD, floor=48)),
], floor=0, ceil=160, light=165, **PASSAGE)
door((768, 112), (768, 176), (1, 0), 0, "HP", "XP")
# the generator room: bolted inside, and one of the places a Stray door opens onto
m.sector(rect(944, 240, 1264, 304), ceil=128, light=120, wall=GENW, ftex="AJPIT")
m.sector(rect(944, 304, 1264, 464), ceil=128, light=120, wall=GENW, ftex="AJPIT")
bolted((1072, 224), (1136, 224), (0, 1), 0, GENERATOR, "XP", "XG", line_id=306)
ajarmap.unbolt(m, (944, 304), (1264, 304), GENERATOR)
ajarmap.stray_place(m, 0, (1264, 352), (1264, 416), (1, 0), 0)

# === the west wing: open. Canteen, rest room; the cloakroom has the lock ===========
hall((-1360, -288, -848, 96), [((-1232, -160, -1104, -96), CASE), ((-1040, -32, -976, 32), CASE),
                               ((-1264, 32, -1136, 64), SEAT)], "CN", color=GOLD)                               # canteen
hall((-1680, -288, -1376, 96), [((-1616, -224, -1552, -96), PEGS),
                                ((-1488, -32, -1424, 32), PEGS)], "CK", color=LEAF)                              # cloakroom
hall((-1360, 112, -912, 288), [((-1040, 224, -912, 288), SEAT),
                               ((-1232, 144, -1104, 176), dict(WOOD, floor=32))], "RR", color=PLUM)              # rest room
door((-768, 0), (-768, 64), (-1, 0), 0, "HP", "CN", thick=80)
door((-1360, -128), (-1360, -64), (-1, 0), 0, "CN", "CK", keys="1", line_id=301)
door((-1168, 96), (-1104, 96), (0, 1), 0, "CN", "RR")
recess((-1360, 168), (-1360, 232), (-1, 0), 0, 103, 201, color=PLUM)         # the rest room's frame
# the stationery store (secret): a hole behind the coats that no door fits
# through, PINK, and a frame. Beyond its bars the strongroom (secret): PINK's
# far side. The strongroom's own door into the cloakroom is bolted inside
m.sector(rect(-1904, -288, -1696, -112), ceil=112, light=150, color=ROSE, wall=STOREW, special=1024)
squeeze((-1680, -216), (-1680, -168), (-1, 0), 0, "CK", STOREW)
m.sector(rect(-1760, -96, -1696, 32), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(-1920, -96, -1760, 32), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
bars((-1856, -112), (-1792, -112), (0, 1), 0, STOREW, None)
recess((-1832, -288), (-1768, -288), (0, -1), 0, 109, 201, color=ROSE)
recess((-1920, -64), (-1920, 0), (-1, 0), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)
bolted((-1680, -64), (-1680, 0), (-1, 0), 0, STRONG, "CK", None)
ajarmap.unbolt(m, (-1760, -96), (-1760, 32), STRONG)

# === the east wing: two locks. Apparatus room, relay room; the test room ==========
fit((784, -288, 1360, 64), [
    ((848, -224, 1168, -192), RACK), ((848, -96, 1168, -64), RACK),
    ((1232, -160, 1296, 0), RACK),
], floor=0, ceil=192, light=165, color=LEAF, **APPARATUS)
hall((1376, -288, 1824, 32), [((1504, -96, 1568, -32), CASE), ((1696, -224, 1760, -160), CASE)], "RY", True,
     color=PLUM)                                                             # relay room
door((768, -200), (768, -136), (1, 0), 0, "HP", "AP", keys="23", line_id=302)
door((1360, -200), (1360, -136), (1, 0), 0, "AP", "RY")
# No frame in this wing: the thief has nowhere to hang what it carries, and a
# door hung in here would be a way in past the lock (the solver found the
# player shut out for good that way)
# the test room: a hatch no door fits through, VIOLET, and a frame
fit((1200, -560, 1520, -304), [
    ((1440, -528, 1504, -400), CASE),                                        # the test desk
], floor=0, ceil=128, light=160, color=GOLD, **TEST)
squeeze((1256, -288), (1304, -288), (0, -1), 0, "AP", "TS")
recess((1328, -560), (1392, -560), (0, -1), 0, 104, 201, color=GOLD)         # the test room's frame

# --- doors and keys ----------------------------------------------------------
THIEF, REPAINTER = 20003, 20007
m.thing(-1280, 860, 1, angle=315)                                         # player start: on the roof, in its far corner
ajarmap.door(m, RED, -364, -324, angle=0)                                 # leaning in the call office
ajarmap.door(m, GREEN, -932, 132, angle=180)                              # leaning in the rest room
m.thing(1640, -100, THIEF, angle=180, args=(YELLOW, 1))                   # the thief: has YELLOW, stays in the east wing
ajarmap.door(m, YELLOW, 1640, -100, angle=180)                            # (on the thief's back)
m.thing(600, 150, REPAINTER, angle=180)                                   # the repainter, new here: about the switchroom
ajarmap.door(m, VIOLET, 1220, -324, angle=0)                              # leaning in the test room
ajarmap.door(m, BLUE, -700, -540, angle=0)                                # leaning in the manager's office
ajarmap.door(m, PINK, -1716, -268, angle=180)                             # leaning in the stationery store
ajarmap.stray(m, 748, 204, angle=180)                                     # Stray doors: in the switchroom
ajarmap.stray(m, -1324, 908, angle=0)                                     # on the roof
ajarmap.stray(m, -1340, 270, angle=0)                                     # in the rest room
ajarmap.stray(m, 884, 908, angle=0)                                       # in the battery room
ajarmap.stray(m, 212, 780, angle=0)                                       # in the cable loft
ajarmap.key(m, 1, -1290, 350)                                             # the roof's other corner
ajarmap.key(m, 2, -1640, -250)                                            # the cloakroom
ajarmap.key(m, 3, 1420, 860)                                              # the far corner of the battery room
ajarmap.key(m, 4, -560, -250)                                             # the monitor's balcony

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACHNO, PAIN = 65, 69, 3003, 66, 3006, 3005, 67, 68, 71
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, BARREL = 24, 2035
BACKPACK = 8


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the forecourt: the way in was over the roofs, and here is who watches the door
things(KNIGHT, (600, -700), angle=180)
things(REVENANT, (-380, -690), angle=0)
things(CACO, (900, -700), (-300, -640), angle=180, ambush=True)
things(SOUL, (400, -650), (800, -720), angle=180)
things(CHAINGUNNER, (1000, -640), angle=180)
things(MEDIKIT, (480, -620))
things(LAMP, (-96, -608), (96, -608), (-440, -600), (560, -800), (1060, -800))
things(BONUS, (-256, -700), (-200, -700), (200, -700), (256, -700))
# the kiosk
things(PLASMA, (-690, -720))
things(CELLS, (-740, -780), (-740, -740))
things(MEGA, (-620, -660))
# the line: nobody
# the call office: the night staff. Guns at the far end, behind the counter
things(ZOMBIE, (-160, -470), (200, -400), (0, -340), angle=270)
things(IMP, (-300, -330), (330, -340), angle=270)
things(SUPER, (0, -440))
things(SHELLS, (-40, -400), (40, -400))
things(BACKPACK, (-256, -450))                                             # left at the counter
things(STIM, (-350, -500), (350, -340))
things(TECHLAMP, (-360, -536), (104, -536))                                 # not where RED leans (it stood in the door)
# the manager's office: working late, and deaf to the call office
things(BARON, (-500, -360), angle=0, ambush=True)
things(KNIGHT, (-620, -520), angle=0, ambush=True)
things(TECHLAMP, (-424, -328), (-424, -536))
things(MEDIKIT, (-690, -420))
things(CELLS, (-440, -500))
# the switchroom: the night shift, between the boards. From the way in the
# guns are at the two ends of the hall and shoot along it, through the rest
things(IMP, (-256, -240), (256, -240), (-448, -112), (432, -160), (-256, 32), (256, 30), angle=270)
things(DEMON, (-90, -110), (90, -110), (0, 50), angle=270)
things(SERGEANT, (-440, 30), (-470, -220), (700, -10), (610, -180), angle=270)
things(ZOMBIE, (0, -200), (-600, 30), (420, 60), angle=270)
things(KNIGHT, (0, -20), angle=270)
things(CACO, (-180, -110), angle=270, ambush=True)
things(REVENANT, (560, -10), angle=180)
things(SPECTRE, (310, -110), angle=270)
things(CHAINGUNNER, (730, -260), angle=180)
things(TECHLAMP, (-488, 72), (360, 72))
things(SHELLBOX, (-430, -250), (690, 200))
things(MEDIKIT, (560, -250), (-560, 60))
things(SHELLS, (-200, 60), (200, 60))
things(STIM, (40, -270), (740, -60))
# the gallery, where the roof lets you down: a chaingun, a rocket launcher for
# the crowd below, and those who watch from above
things(LAUNCHER, (-680, 190))
things(ROCKETBOX, (-740, 120), (340, 200))
things(CHAINGUN, (-300, 180))
things(AMMOBOX, (-260, 200))
things(MEDIKIT, (100, 200))
things(CHAINGUNNER, (0, 130), angle=270)
things(IMP, (-520, 130), (300, 130), angle=270)
things(SERGEANT, (-150, 190), angle=270)
# the balcony: key 4, the monitor
things(PLASMA, (-720, -260))                                               # for the trunk room, and what is left
things(CELLS, (-680, -260), (-640, -260))
things(MEDIKIT, (-740, -60))
things(CHAINGUNNER, (-560, -80), angle=0)
things(IMP, (-640, -160), angle=0)
# the roof: start here, with a shotgun to hand. Key 1 is in the other corner
things(SHOTGUN, (-1220, 800))
things(SHELLS, (-1180, 860), (-1000, 600), (-1000, 680))
things(IMP, (-1220, 380), (-640, 400), (-980, 400), (-620, 760), angle=90)
things(ZOMBIE, (-1300, 600), (-760, 700), angle=90)
things(SERGEANT, (-720, 860), angle=180)
things(SHELLBOX, (-560, 330))
things(MEDIKIT, (-1320, 330), (-560, 620))
things(ARMOR, (-560, 900))
things(LAMP, (-1006, 880), (-850, 880))
# the cable loft
things(IMP, (224, 400), (224, 520), (500, 620), (620, 760), angle=270)
things(SERGEANT, (400, 620), (660, 620), angle=270)
things(REVENANT, (800, 600), angle=180)
things(SOUL, (300, 770), (560, 700), angle=270)
things(SHELLS, (224, 300), (820, 780))
things(SHELLBOX, (810, 720))
things(MEDIKIT, (480, 780))
things(STIM, (224, 560))
things(TECHLAMP, (520, 776))
things(ARMOR, (680, 900))                                                  # its alcove
things(CELLS, (640, 920), (720, 920))
things(CANDLE, (632, 832), (728, 832))
# the trunk room: somebody lives in the frames
things(LODGER, (592, 330), args=(300,))
things(DEMON, (420, 520), (750, 520), angle=270)
things(KNIGHT, (700, 432), angle=180)
things(IMP, (370, 330), (816, 336), angle=270)
things(TORCH_B, (360, 536), (824, 480))
things(MEDIKIT, (360, 372))
things(SHELLS, (820, 372))
# the battery room: key 3 in its far corner, and what guards the cells
things(KNIGHT, (920, 620), (1400, 620), angle=180)
things(REVENANT, (1380, 800), angle=180)
things(CACO, (1140, 620), angle=180)
things(IMP, (1024, 768), (1248, 768), (1150, 544), angle=180)                 # on the cells
things(SOUL, (900, 800), (1340, 540), angle=180)
things(SERGEANT, (1440, 560), (900, 900), angle=180)
things(TORCH_G, (1480, 904), (1480, 504))
things(MEDIKIT, (1150, 640), (890, 700))
things(SHELLBOX, (1340, 900))
# the cable passage
things(ZOMBIE, (860, 150), (1100, 120), (1300, 140), angle=180)
things(IMP, (980, 180), (1400, 110), angle=180)
things(SERGEANT, (1180, 150), (1360, 190), angle=180)
things(DEMON, (1040, 190), (1250, 120), angle=180)
things(TECHLAMP, (808, 104), (1448, 104))
things(STIM, (800, 200))
things(CLIP, (850, 100), (850, 130))
things(ROCKETS, (1440, 200), (1440, 170))                                  # at the head of the stairs
# the generator room: do not open this door
things(MANCUBUS, (1104, 400), angle=270)
things(KNIGHT, (990, 350), (1210, 350), angle=270)
things(SPHERE, (970, 270))
things(ROCKETBOX, (1230, 270), (1190, 270))
# the west wing. The canteen: things that eat
things(BERSERK, (-730, 80))                                                # before its door
things(ZOMBIE, (-900, -100), (-1040, -180), (-1300, -40), angle=0)
things(IMP, (-1300, 40), (-930, -240), (-1200, -250), angle=0)
things(SERGEANT, (-1090, 60), (-1330, -260), angle=0)
things(DEMON, (-1000, -90), (-1180, -40), (-1270, -170), angle=0)
things(SPECTRE, (-940, 20), angle=0)
things(TECHLAMP, (-872, -264), (-1336, 0))                                 # not in the cloakroom's door (it stood there)
things(SHELLS, (-880, 70), (-1340, -130))
things(MEDIKIT, (-1340, -270))
things(STIM, (-870, -60))
# the cloakroom: key 2, and the attendants
things(SPECTRE, (-1600, -40), angle=0)
things(CHAINGUNNER, (-1640, 60), (-1440, -230), angle=0)
things(REVENANT, (-1520, -160), angle=0)
things(PAIN, (-1560, 40), angle=0)
things(IMP, (-1440, 60), angle=0)
things(SHELLBOX, (-1400, 70))
things(MEDIKIT, (-1660, -60))
things(TECHLAMP, (-1400, -264))
# the rest room: GREEN, a frame, and who is resting
things(BARON, (-1280, 200), angle=0)
things(KNIGHT, (-1000, 160), angle=180)
things(IMP, (-1180, 250), (-1320, 256), angle=270)
things(SERGEANT, (-1060, 140), angle=270)
things(AMMOBOX, (-940, 200))
things(ROCKETS, (-1340, 130), (-1300, 130))
things(STIM, (-930, 250))
# the east wing. The apparatus room: the thief's hunting ground
things(ZOMBIE, (830, -40), (900, 20), angle=180)
things(IMP, (1000, -150), (1100, -10), (1200, -250), (1330, 30), (1330, -80), angle=180)
things(SERGEANT, (1000, -256), (1200, 30), angle=180)
things(DEMON, (880, -140), (1150, 20), angle=180)
things(CHAINGUNNER, (1330, -250), angle=180)
things(CACO, (1100, -140), angle=180, ambush=True)
things(TECHLAMP, (808, -264), (808, 40))
things(SHELLBOX, (860, 40))
things(MEDIKIT, (1340, -20))
things(CELLS, (1200, -270))
things(STIM, (850, -270))
# the relay room
things(ARACHNO, (1620, -200), angle=180)
things(KNIGHT, (1440, -40), angle=180)
things(REVENANT, (1780, -60), (1440, -240), angle=180)
things(IMP, (1780, 0), (1420, 10), angle=180)
things(SERGEANT, (1700, -110), angle=180)
things(ROCKETS, (1400, -270), (1480, -270))
things(MEDIKIT, (1800, -270))
things(SHELLBOX, (1800, 10))
# the test room: whoever was testing the line
things(KNIGHT, (1380, -440), angle=90)
things(IMP, (1260, -500), (1480, -340), angle=90)
things(TECHLAMP, (1224, -536))
things(STIM, (1500, -544))
# the stationery store and the strongroom
things(CANDLE, (-1720, -136), (-1880, -264))
things(HELMET, (-1876, -140))
things(LAUNCHER, (-1840, -32))
things(ROCKETBOX, (-1786, 10), (-1896, 10))
things(MEGA, (-1786, -80))
things(AMMOBOX, (-1896, -80))

# --- ambushes: what taking a key brings (ajarmap.ambush) ----------------------
# key 1, in a corner of the roof: between you and the hole
ajarmap.ambush(m, 1, IMP, (-960, 720), (-700, 480), (-700, 330), angle=180)
# key 2, in the cloakroom: the canteen you have to go back through
ajarmap.ambush(m, 2, REVENANT, (-1100, -250), angle=180)
ajarmap.ambush(m, 2, IMP, (-950, -200), (-1250, 70), angle=180)
# key 3, in the battery room: the passage you have to go back by
ajarmap.ambush(m, 3, REVENANT, (1300, 150), angle=180)
ajarmap.ambush(m, 3, IMP, (1000, 150), (1150, 120), angle=180)
# key 4, on the balcony: the floor below
ajarmap.ambush(m, 4, KNIGHT, (0, -150), angle=180)
ajarmap.ambush(m, 4, IMP, (-300, 60), (300, 60), angle=180)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "main" is the call office, the forecourt, the switchroom, the cable passage
# and the battery room, and also the kiosk and the generator room, which open
# from inside. "roof" is where the level starts. "gallery" is the supervisor's
# gallery and the cable loft; "balcony" the monitor's; "west" the canteen and
# the rest room, open from the start; "cloak" the cloakroom; "east" the
# apparatus and relay rooms, where the thief lives; "night" is the line. The
# stationery store, the strongroom and PINK are left out: PINK never leaves,
# and nothing else needs it.
PUZZLE = dict(
    start="roof", goal="exit", names=ajarmap.NAMES, complete=True,
    home_chain=dict(frames=[ajarmap.HOME, ajarmap.HOME2], doors=[BLUE, VIOLET]),
    walk=[("gallery", "main"), ("gallery", "trunk"), ("roof", "gallery"),
          ("main", "trunk", "", "squeeze"), ("trunk", "main", "", "squeeze"),             # the hatch
          ("trunk", "main"),                                                              # the chute
          ("balcony", "main"),
          ("east", "test", "", "squeeze"), ("test", "east", "", "squeeze"),               # the test room's hatch
          ("night", "main"),                                                              # the hole over the forecourt
          ("main", "west"), ("west", "main"),
          ("west", "cloak", "1"), ("cloak", "west", "1"),
          ("main", "east", "23"), ("east", "main", "23"),
          ("main", "office", "4"), ("office", "main", "4")],
    keys={"1": "roof", "2": "cloak", "3": "main", "4": "balcony"},
    frames={101: "main", 102: "main", 105: "main", 103: "west", 104: "test",
            ajarmap.HOME: "trunk", ajarmap.HOME2: "trunk"},
    doors={
        RED: dict(home="roof", lean="main"),
        GREEN: dict(home="gallery", lean="west"),
        YELLOW: dict(home="balcony", thief=True),
        BLUE: dict(home="night", lean="office"),
        VIOLET: dict(home="night", lean="test"),
    },
    thief=dict(zone="east", sees=()),
    repainter=dict(zone=["main", "west"]),      # it wanders: the west wing too
    pool=["main"],                         # the generator room; the kiosk
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
