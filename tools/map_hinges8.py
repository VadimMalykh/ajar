"""Act 1, level 8: "Closing Time" (MAP08).

A department store after the doors are locked. One new thing (Vadim's idea,
2026-11-15): the way out is behind a rolling shutter that a lever sends up
for eight seconds. The lever is in the caretaker's office, the shutter is
across the loading dock, and nothing but a route of doors laid beforehand
gets a door from the one to the other in that time.

The night room has no door of its own. You come into it through BLUE, hung
anywhere, and leave the same way; but then BLUE is not in your hands. Its
brass frame takes no door but BLUE (ajarmap.way_home, only), so no other
door hung there makes a way in. The shutter is the only way into the room
with anything in hand: so BLUE has to be carried under it.

The catch. The caretaker's office is a balcony over the door showroom. The
stairs up to it end at a gatepost no door passes, so a door comes into the
office only through YELLOW, whose far side is there. Off the balcony the way
is down, into the showroom, and the showroom is a place doors do not leave:
its way in from the store is a turnstile, its way to the dock a hatch. A door
comes into it from above: off the office, or through a hole from the gallery
over the atrium (RED's far side). VIOLET's far side is in the dock, facing
the shutter. So: VIOLET hangs in the showroom; BLUE goes up through YELLOW,
the lever, down off the balcony, through VIOLET, and under the shutter.

Places. The arcade (start), the lobby, the atrium, the goods passage and the
stockroom under it are one place to walk about in. The gallery over the
atrium's west side (RED's far side; key 1). The roof (GREEN's; key 2), from
which a hole lets down onto the gallery. The showroom (two frames), the
office over it (YELLOW's far side; key 4; the lever), the dock (VIOLET, and
its far side), the night room. West wing (key 1): toys, haberdashery,
furniture (GREEN, a frame). East wing (key 2): china (key 3), linen, carpets
(YELLOW). The cash office (keys 3 and 4): BLUE.

Secrets: the shop window (the cash office's lever, or a Stray door); the
kiosk in the arcade (shoot its bell through the bars); the lamp store behind
the carpets (a squeeze; PINK and a frame) and beyond its bars the strongroom
(PINK's far side); an alcove off the stockroom.
"""
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


UP, ROOF, PIT = 160, 320, -128
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True, floorpeg=True)
SEAT = dict(ftex="AJSOFA", side="AJSOFA", floor=16)
CASE = dict(ftex="AJSTEEL", side="AJWOOD", floor=40)  # a counter, a display case
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
PATH = dict(ftex="AJARCHF")
KIOSK, NIGHT_BOLT, BOILER, WINDOW, STRONG = 401, 402, 403, 404, 405
NX, NY = -480, 1936                                   # the night room's south-west corner
NIGHT = 150                                           # light under the sky
SECONDS = 8                                           # how long the shutter stays up

# The store's look (gfx_store.py). AJAR_STORE=1..3 dresses the whole of it in a
# candidate: 1 Emporium (red brick, green cast iron, oak, encaustic tile),
# 2 Grand Magasin (cream stone, sea-green iron and gilt, marble, mahogany),
# 3 Festival (buff brick, plate glass, teak, lino, a colour to a department).
# Without it the level is in the plain textures it was first built in: nothing
# is chosen yet. A look changes textures only: no floor, wall or railing moves.
# Rooms are not tinted in a look.
LOOK = (os.environ.get("AJAR_STORE") or "").replace("0", "")
FACES = {}                  # the door faces this build needs, and their textures: gfx_store.make draws them


def T(tag, pic=""):
    return f"AJ8{tag}{LOOK}{pic}"


if LOOK:
    import gfx_store
    m.align = gfx_store.aligned(LOOK)
    WARM = GOLD = SKY = LEAF = PLUM = ROSE = None
    FRONT, BACK, STREET = T("Y"), T("K"), "AJ8XS"
    LOWW, PORCH, HOLE = T("A"), T("CP"), "AJTRIM"
    ARCADE = dict(ceil=512, ctex="F_SKY1", wall=STREET)                   # the houses round it; the store's front is named
    OPEN = dict(ceil=512, ctex="F_SKY1", wall=BACK)                       # the dock, the roof
    RAIL = dict(RAIL, mid=T("RL"))
    SEAT = dict(ftex=T("BN"), side=T("BN"), floor=16)
    GSEAT = dict(ftex=T("PL"), side=T("PL"), floor=16)                    # a stone seat out of doors
    CASE = dict(ftex=T("VT"), side=T("V"), floor=40)
    CRATE = WOOD
    WOOD = dict(ftex=T("WD"), side=T("WD"))
    PATH, WALK = dict(ftex=T("P")), dict(ftex=T("FT"))
    STEP = dict(ftex=T("PL"), side=T("PL"))
    POST = dict(ftex=T("PL"), side=T("PL"))
    BASIN = T("PL")
    ARCF, DOCKF, ROOFF = T("FA"), T("FK"), T("FR")
    LOBBY = dict(wall=T("L"), ftex=T("F"), ctex=T("CL"))
    ATRIUM = dict(wall=T("H"), ftex=T("F"), ctex=T("CA"))
    GAL = dict(floor=UP, ftex=T("FG"), side=T("GV"))
    SHOW = dict(wall=T("SH"), ftex=T("FS"), ctex=T("CS"))
    BAL = dict(floor=UP, ftex=T("FG"), side=T("GV"))
    ONSHOW = dict(ftex=T("WD"), side="AJ8XD", floor=96)                   # a door nobody has painted yet
    CASH = dict(wall=T("CO"), ftex=T("FO"), ctex=T("CD"))
    SKYLIGHT = dict(floor=ROOF + 40, ftex=T("FL"), side=T("FL"), light=255)
    STOCK = dict(wall="AJ6XK", ftex="AJPIT")
    PASSAGE = dict(wall="AJ8XP", ftex="AJBOARD")
    FURN = dict(wall=T("FU"), ftex=T("FD"), ctex=T("CD"))
    BOILERW, KIOSKW, WINDOWW, LAMPW, ALCOVEW = "AJ6XB", "AJ8XN", "AJ8XW", "AJ8XL", "AJ6XC"
    BELL = "AJTARG8"

    def wing(tag, east):
        return dict(wall=T(tag), ftex=T("FE" if east else "FD"), ctex=T("CD"))
else:
    FRONT = BACK = STREET = LOWW = None
    PORCH, HOLE = "AJBOARD", "AJBRICK"
    ARCADE = OPEN
    GSEAT, CRATE, WALK = SEAT, WOOD, PATH
    STEP = dict(ftex="AJARCHF", side="AJTRIM")
    POST = dict(ftex="AJTRIMF", side="AJTRIM")
    BASIN = "AJTRIM"
    ARCF, DOCKF, ROOFF = "AJGRASS", "AJARCHF", "AJSTEEL"
    LOBBY = ATRIUM = SHOW = dict(wall="AJBRICK", ftex="AJFLOOR")
    GAL = dict(floor=UP, ftex="AJSTEEL", side="AJSTEEL")
    BAL = dict(floor=UP, ftex="AJBOARD", side="AJWOOD")
    ONSHOW = dict(WOOD, floor=96)
    CASH = FURN = {}
    SKYLIGHT = dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")
    STOCK = dict(wall="AJBRICK", ftex="AJPIT")
    PASSAGE = dict(wall="AJBRICK", ftex="AJBOARD")
    BOILERW = KIOSKW = WINDOWW = LAMPW = ALCOVEW = "AJSAFE"
    BELL = "AJTARG"

    def wing(tag, east):
        return {}


def low(floor=0, wall=None):
    """A porch: doors and frames in tall rooms and under the sky stand under one.
    In a look `wall` is the wall under it (default: the indoor porches')."""
    return dict(dict(ceil=floor + 128, ctex=PORCH), **(dict(wall=wall or LOWW) if LOOK else {}))


def over(a, b, tex):
    """In a look: the wall over the opening a-b (under a lower ceiling) carries
    on as `tex`, in line with the wall beside it; and so does the wall under
    it, where the opening's floor is higher than the room's."""
    if LOOK and tex:
        m.line(a, b, upper=tex, lower=tex, dontpegtop=True, dontpegbottom=True)


def fit(box, features, above=None, **base):
    """ajarmap.fitted. In a look the walls over the open sides of its porches
    (low()) carry on as `above` (default: the room's own wall)."""
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
    """In a look: these pieces of the arcade's wall are the store's front."""
    for a, b in runs if LOOK else ():
        m.line(a, b, mid=FRONT)


def shelves(tag, fixed, starts, axis="x"):
    """In a look: fitted shelves of what the department `tag` sells."""
    pieces((T(tag, 1), T(tag, 2)), fixed, starts, axis)


def _wall(tag):
    return tag and (tag if tag.startswith("AJ") else T(tag))


def _face(kind, tag, a, out, keys=""):
    """The face of a door whose mouth starts at `a` in the wall `tag`, seen by
    someone the door goes `out` from: the wall carries on over the leaf."""
    lo = a[0] if out[0] == 0 else a[1]
    s = lo % 64 if out in ((0, 1), (-1, 0)) else -lo % 64
    return FACES.setdefault((LOOK, kind, tag, s, keys), f"AJ8{kind}{LOOK}{len(FACES):02d}")


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
    the walls it stands in (tags of gfx_store's: "L", "XP"...)."""
    ajarmap.roomdoor(m, a, b, out, floor, **k)
    _doors("D", a, b, out, near, far, k.get("thick", 16), k.get("keys", ""))


def bolted(a, b, out, floor, tag, near, far, **k):
    """A bolted door; `near`, `far` as door()'s, None for a side that stays as it is."""
    ajarmap.bolted(m, a, b, out, floor, tag, **k)
    _doors("Z", a, b, out, near, far, k.get("thick", 16))


def opening(a, b, out, floor, near, far, thick=16):
    """An open way between two rooms; in a look their walls carry on round it."""
    ajarmap.opening(m, a, b, out, floor, thick=thick)
    over(a, b, _wall(near))
    over((a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick), _wall(far))


def squeeze(a, b, out, floor, near, far, thick=16):
    ajarmap.squeeze(m, a, b, out, floor, thick=thick)
    over(a, b, _wall(near))
    over((a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick), _wall(far))


def bars(a, b, out, floor, near=None, far=None, thick=16):
    """A barred opening in a wall: to look and shoot through. In a look, `near`
    and `far` are the walls it is cut through on either side."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall=HOLE,
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)
    over(a, b, _wall(near))
    over(c, d, _wall(far))


def hall(box, cases, tag, east=False, **k):
    """A department: 160 high, with counters."""
    fit(box, [(c, CASE) for c in cases], **dict(dict(ceil=160, light=175), **dict(k, **wing(tag, east))))


# === the arcade, the lobby =======================================================
# the arcade: start here. The shop window is behind glass, the kiosk behind bars
fit((-704, -704, 704, -448), [
    ((-64, -704, 64, -448), WALK),
    ((-64, -512, 64, -448), low(wall=T("YP"))),                              # before the front door
    ((-704, -688, -640, -496), low(wall="AJ8XT")),                           # before the kiosk
    ((384, -512, 512, -448), low(wall=T("YP"))),                             # before the shop window
    ((-320, -672, -192, -640), GSEAT), ((192, -672, 320, -640), GSEAT),
], above=FRONT, floor=0, light=NIGHT, ftex=ARCF, **ARCADE)
if LOOK:
    for a, b in (((-704, -688), (-640, -688)), ((-640, -688), (-640, -496)), ((-640, -496), (-704, -496))):
        m.line(a, b, upper=STREET, dontpegtop=True)                          # over the kiosk's porch
pieces((T("YA"), T("YB")), -448, (-640, -512, -384, -256, 128, 256, 576))    # the store's windows
front(((-704, -448), (-64, -448)), ((64, -448), (384, -448)), ((512, -448), (704, -448)))
pieces(("AJ8XSA",), -704, (-576, -128, 320))                                 # somebody is still up, across the way
pieces(("AJ8XSA",), 704, (-640,), "y")
# the kiosk (secret), seen through bars: shoot its bell
m.sector(rect(-976, -688, -720, -496), ceil=112, light=170, color=ROSE, wall=KIOSKW, special=1024)
bolted((-704, -672), (-704, -608), (-1, 0), 0, KIOSK, "XT", "XN")
bars((-704, -576), (-704, -512), (-1, 0), 0, "AJ8XT", KIOSKW)
m.cut((-976, -576), (-976, -512))
m.line((-976, -576), (-976, -512), special=11, args=(KIOSK, 32), impact=True, mid=BELL, exact=True)

# the lobby: RED, a frame, the cash office's two locks, the way into the atrium
fit((-256, -432, 256, 0), [
    ((-64, -432, 64, 0), PATH),
    ((96, -320, 224, -256), CASE),                                           # the enquiry desk
    ((-224, -112, -96, -48), SEAT),
], floor=0, ceil=192, light=185, **LOBBY)
door((-32, -448), (32, -448), (0, 1), 0, "YP", "L")
recess((256, -128), (256, -64), (1, 0), 0, 101, 201)                         # the lobby's frame
m.sector(rect(-96, 0, 96, 16), ceil=160, light=185, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
over((-96, 0), (96, 0), _wall("L"))
over((-96, 16), (96, 16), _wall("H"))
# the shop window (secret): bolted inside, opened by the cash office's lever, and
# one of the places a Stray door opens onto
m.sector(rect(272, -432, 336, -272), ceil=112, light=190, color=ROSE, wall=WINDOWW)
m.sector(rect(336, -432, 560, -272), ceil=112, light=190, color=ROSE, wall=WINDOWW, special=1024)
bolted((256, -400), (256, -336), (1, 0), 0, WINDOW, "L", "XW", line_id=305)
ajarmap.unbolt(m, (336, -432), (336, -272), WINDOW)
bars((416, -448), (480, -448), (0, 1), 0, "YP", WINDOWW)
ajarmap.stray_place(m, 1, (432, -272), (496, -272), (0, 1), 0, color=ROSE)
# the cash office: two locks. BLUE, and the lever of the shop window
fit((-592, -432, -272, -112), [
    ((-464, -304, -400, -240), CASE),                                        # the safe
    ((-592, -176, -528, -112), SEAT),
], floor=0, ceil=128, light=170, color=PLUM, **CASH)
door((-256, -304), (-256, -240), (-1, 0), 0, "L", "CO", keys="34", line_id=303)
m.cut((-592, -304), (-592, -240))
m.line((-592, -304), (-592, -240), special=11, args=(WINDOW, 32), playeruse=True, mid=T("LC") if LOOK else "AJLEVR", exact=True,
       id=308)

# === the atrium, under its gallery ===============================================
fit((-512, 16, 512, 1040), [
    ((-64, 16, 64, 1040), PATH),
    ((-192, 336, 192, 720), dict(ctex="F_SKY1")),                            # the lantern, open to the stars
    ((-512, 32, -448, 128), low()),                                          # before the west wing's door
    ((448, 32, 512, 128), low()),                                            # before the east wing's
    ((448, 896, 512, 992), low()),                                           # before the goods passage's
    ((-512, 144, -384, 1040), GAL),
    ((-512, 624, -448, 752), dict(GAL, **low(UP))),                          # before RED's far side
    ((-64, 464, 64, 592), dict(floor=32, ftex="AJWATER", side=BASIN)),       # the fountain
    ((-256, 208, -128, 272), CASE), ((128, 208, 256, 272), CASE),            # counters
    ((-256, 784, -128, 848), CASE), ((128, 784, 256, 848), CASE),
    ((288, 464, 352, 592), SEAT),
], floor=0, ceil=448, light=180, color=SKY, **ATRIUM)
recess((-512, 656), (-512, 720), (-1, 0), UP, far_id(RED), 101, far_colour=RED, color=SKY)
rail(((-512, 144), (-384, 144)), ((-384, 144), (-384, 400)), ((-384, 464), (-384, 1040)))   # a gap over the atrium

# === the door showroom, the caretaker's office over it ============================
# The stairs up to the office end at a gatepost no door fits past. Off the
# balcony there is a gap in the rail: down is the only way with a door
ajarmap.fitted(m, (-512, 1056, 384, 1440), [
    ((-160 + 32 * i, 1056, -128 + 32 * i, 1120), dict(STEP, floor=20 * (i + 1)))
    for i in range(8)] + [
    ((128, 1056, 384, 1440), BAL),
    ((96, 1056, 128, 1120), dict(POST, floor=UP)),
    ((96, 1104, 128, 1120), dict(POST, floor=UP + 56)),
] + [((-352 + 96 * k, 1184, -336 + 96 * k, 1248), ONSHOW) for k in range(4)],   # doors, on show
    floor=0, ceil=320, light=180, color=WARM, **SHOW)
m.line((128, 1056), (128, 1104), id=ajarmap.SQUEEZE, blockmonsters=True)
rail(((128, 1120), (128, 1280)), ((128, 1344), (128, 1440)))                 # a gap to jump down by
recess((-64, 1440), (0, 1440), (0, 1), 0, 106, 201, color=WARM)              # the showroom's two frames
recess((-192, 1440), (-128, 1440), (0, 1), 0, 107, 201, color=WARM)
recess((224, 1440), (288, 1440), (0, 1), UP, far_id(YELLOW), 101, far_colour=YELLOW, color=WARM)
ajarmap.lever(m, (384, 1248), (384, 1312), SECONDS, line_id=309, tex=T("LV") if LOOK else "AJLEVB")
squeeze((-312, 1040), (-264, 1040), (0, 1), 0, "H", "SH")                    # the turnstile, from the atrium
opening((-480, 1040), (-416, 1040), (0, 1), UP, "H", "SH")                   # the hole from the gallery

# === the loading dock, the night room behind its shutter ==========================
fit((-512, 1520, 384, 1840), [
    ((-320, 1520, -192, 1584), low(wall=T("KA"))),                           # before VIOLET's far side
    ((-320, 1776, -192, 1840), low(wall=T("KA"))),                           # before the shutter
    ((0, 1616, 128, 1744), dict(CRATE, floor=48)),     # crates
    ((192, 1552, 256, 1616), dict(CRATE, floor=48)),
], floor=0, light=NIGHT, ftex=DOCKF, **OPEN)
recess((-288, 1520), (-224, 1520), (0, -1), 0, far_id(VIOLET), 101, far_colour=VIOLET)
for a, b in (((-320, 1776), (-192, 1776)), ((-192, 1776), (-192, 1840)), ((-320, 1776), (-320, 1840))):    # nothing but you stands under the shutter
    m.line(a, b, blockmonsters=True)
squeeze((-440, 1440), (-392, 1440), (0, 1), 0, "SH", BACK, thick=80)         # the hatch, from the showroom
bars((32, 1440), (96, 1440), (0, 1), 0, "SH", BACK, thick=80)                # the showroom's window on the dock
bars((304, 1440), (368, 1440), (0, 1), UP, "SH", BACK, thick=80)             # and the office's
ajarmap.way_home(m, NX, NY, BLUE, only=True)
m.sector(rect(-288, 1856, -224, 1936), ceil=96, light=160, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
ajarmap.shutter(m, (-288, 1840), (-224, 1840), (0, 1), 0, line_id=310)
_doors("S", (-288, 1840), (-224, 1840), (0, 1), "KA", None, 16)
m.line((-288, 1936), (-224, 1936), blockmonsters=True)                       # nor does the room's company

# === the stockroom under the goods passage ========================================
# a chute down from the dock; stairs up to the passage, and two doors on the way
ajarmap.fitted(m, (400, 1520, 1184, 1968), [
    ((528, 1584, 656, 1712), dict(CRATE, floor=PIT + 48)),    # crates, clear of the chute
    ((848, 1616, 912, 1744), dict(CRATE, floor=PIT + 48)),
    ((944, 1840, 1072, 1904), dict(CRATE, floor=PIT + 96)),
], floor=PIT, ceil=128, light=140, **STOCK)
opening((384, 1744), (384, 1808), (1, 0), 0, BACK, STOCK["wall"])            # the chute
recess((736, 1968), (800, 1968), (0, 1), PIT, 103, 201)                      # the stockroom's frame
ajarmap.stairs(m, (1056, 1520), (1120, 1520), (0, -1), PIT, 128, ceil=128, light=150, **PASSAGE)
m.sector(rect(1056, 1120, 1120, 1264), ceil=128, light=150, **PASSAGE)
m.sector(rect(1200, 1680, 1344, 1808), floor=PIT, ceil=PIT + 96, light=120, wall=ALCOVEW, ftex="AJPIT",
         special=1024)
squeeze((1184, 1720), (1184, 1768), (1, 0), PIT, STOCK["wall"], ALCOVEW)
ajarmap.fitted(m, (528, 896, 1184, 1104), [
    ((704, 896, 832, 944), dict(CRATE, floor=48)),
    ((960, 1040, 1024, 1104), dict(CRATE, floor=48)),
], floor=0, ceil=160, light=165, **PASSAGE)
door((512, 912), (512, 976), (1, 0), 0, "A", "XP")
door((1056, 1120), (1120, 1120), (0, -1), 0, "XP", "XP", line_id=307)
# the boiler room: bolted inside, and one of the places a Stray door opens onto
m.sector(rect(608, 1120, 928, 1184), ceil=128, light=120, wall=BOILERW, ftex="AJPIT")
m.sector(rect(608, 1184, 928, 1408), ceil=128, light=120, wall=BOILERW, ftex="AJPIT")
bolted((736, 1104), (800, 1104), (0, 1), 0, BOILER, "XP", "XB", line_id=306)
ajarmap.unbolt(m, (608, 1184), (928, 1184), BOILER)
ajarmap.stray_place(m, 0, (608, 1264), (608, 1328), (-1, 0), 0)

# === the west wing: one lock. Toys, haberdashery, furniture =======================
hall((-976, 16, -528, 336), [((-848, 144, -720, 208)), ((-656, 240, -592, 304))], "TY", color=GOLD)      # toys
hall((-1440, 16, -992, 336), [((-1376, 208, -1248, 272)), ((-1120, 208, -1056, 272))], "HB", color=LEAF) # haberdashery
fit((-1440, -432, -992, 0), [                                                                            # furniture
    ((-1408, -368, -1344, -240), SEAT), ((-1088, -368, -1024, -240), SEAT),
    ((-1280, -176, -1152, -112), dict(WOOD, floor=32)),
], floor=0, ceil=160, light=175, color=PLUM, **FURN)
shelves("TY", 16, (-896, -768, -640))
shelves("TY", 336, (-896, -768, -640))
shelves("HB", 16, (-1408, -1088))
shelves("HB", 336, (-1344, -1216, -1088))
shelves("HB", -1440, (64, 192), "y")
shelves("FU", 0, (-1408, -1088))
shelves("FU", -432, (-1408, -1088))
shelves("FU", -1440, (-384, -256), "y")
shelves("FU", -992, (-384, -128), "y")
door((-512, 48), (-512, 112), (-1, 0), 0, "A", "TY", keys="1", line_id=301)
door((-976, 144), (-976, 208), (-1, 0), 0, "TY", "HB")
door((-1248, 16), (-1184, 16), (0, -1), 0, "HB", "FU")
recess((-1248, -432), (-1184, -432), (0, -1), 0, 102, 201, color=PLUM)       # the furniture department's frame

# === the roof: a hole lets down onto the gallery ==================================
fit((-1408, 416, -592, 1040), [
    ((-1056, 976, -928, 1040), low(ROOF, wall=T("KA"))),                     # before GREEN's far side
    ((-1216, 544, -1088, 672), SKYLIGHT),                                    # skylights
    ((-896, 608, -768, 736), SKYLIGHT),
    ((-1216, 800, -1088, 928), SKYLIGHT),
], floor=ROOF, light=NIGHT + 10, ftex=ROOFF, **OPEN)
m.sector(rect(-592, 896, -528, 992), floor=ROOF, light=NIGHT + 10, ftex=ROOFF, **OPEN)
recess((-1024, 1040), (-960, 1040), (0, 1), ROOF, far_id(GREEN), 101, far_colour=GREEN)
opening((-528, 912), (-528, 976), (1, 0), ROOF, BACK, "H")

# === the east wing: one lock. China, linen, carpets ===============================
hall((528, 16, 976, 336), [((656, 144, 848, 176)), ((656, 240, 848, 272))], "CH", True, color=GOLD)      # china
hall((528, 352, 976, 848), [((592, 480, 656, 608)), ((848, 480, 912, 608)), ((720, 720, 784, 784))],
     "LN", True, color=LEAF)                                                                             # linen
hall((992, 16, 1440, 336), [((1120, 208, 1184, 272)), ((1312, 144, 1376, 208))], "CP", True, color=PLUM) # carpets
shelves("CH", 16, (576, 704, 832))
shelves("CH", 336, (576, 832))
shelves("LN", 528, (448, 576, 704), "y")
shelves("LN", 976, (448, 576, 704), "y")
shelves("LN", 848, (576, 704, 832))
shelves("CP", 16, (1152, 1216))
shelves("CP", 336, (1024, 1152, 1280))
shelves("CP", 1440, (64, 192), "y")
door((512, 48), (512, 112), (1, 0), 0, "A", "CH", keys="2", line_id=302)
opening((720, 336), (784, 336), (0, 1), 0, "CH", "LN")
door((976, 144), (976, 208), (1, 0), 0, "CH", "CP")
# the lamp store (secret): a hole no door fits through, PINK, and a frame. Beyond
# its bars the strongroom (secret): PINK's far side. The strongroom's own door
# into the carpets is bolted inside
m.sector(rect(992, -208, 1200, 0), ceil=112, light=150, color=ROSE, wall=LAMPW, special=1024)
squeeze((1064, 16), (1112, 16), (0, -1), 0, "CP", LAMPW)
m.sector(rect(1216, -64, 1440, 0), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(1216, -208, 1440, -64), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
bars((1200, -152), (1200, -88), (1, 0), 0, LAMPW, "AJSAFE")
recess((1064, -208), (1128, -208), (0, -1), 0, 109, 201, color=ROSE)
recess((1296, -208), (1360, -208), (0, -1), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)
bolted((1296, 16), (1360, 16), (0, -1), 0, STRONG, "CP", None)
ajarmap.unbolt(m, (1216, -64), (1440, -64), STRONG)

# --- doors and keys ----------------------------------------------------------
m.thing(0, -640, 1, angle=90)                                             # player start, in the arcade
ajarmap.door(m, RED, -236, -400, angle=0)                                 # leaning in the lobby
ajarmap.door(m, GREEN, -1420, -40, angle=0)                               # leaning among the furniture
ajarmap.door(m, YELLOW, 1420, 40, angle=180)                              # leaning among the carpets
ajarmap.door(m, VIOLET, 364, 1820, angle=180)                             # leaning in the dock
ajarmap.door(m, BLUE, -572, -412, angle=0)                                # leaning in the cash office
ajarmap.door(m, PINK, 1012, -188, angle=0)                                # leaning in the lamp store
ajarmap.stray(m, 492, 36, angle=180)                                      # Stray doors: in the atrium
ajarmap.stray(m, -1388, 1020, angle=0)                                    # on the roof
ajarmap.stray(m, 548, 828, angle=0)                                       # in the linen department
ajarmap.stray(m, 1164, 1540, angle=180)                                   # in the stockroom
ajarmap.stray(m, -492, 1420, angle=0)                                     # in the showroom
ajarmap.key(m, 1, -448, 240)                                              # south end of the gallery
ajarmap.key(m, 2, -1340, 480)                                             # the far corner of the roof
ajarmap.key(m, 3, 944, 816)                                               # the linen department
ajarmap.key(m, 4, 336, 1104)                                              # the caretaker's office

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


# the arcade: lamps and nobody
things(LAMP, (-96, -480), (96, -480), (-600, -480), (600, -480), (-600, -672), (600, -672))
things(BONUS, (-256, -560), (-200, -560), (200, -560), (256, -560))
# the kiosk
things(PLASMA, (-850, -600))
things(CELLS, (-940, -660), (-940, -620))
things(MEGA, (-760, -530))
# the lobby: the night staff
things(ZOMBIE, (-160, -200), (160, -160), (0, -60), angle=270)
things(IMP, (-200, -330), (200, -380), angle=270)
things(SHOTGUN, (0, -260))
things(SHELLS, (-40, -220), (40, -220))
things(BACKPACK, (160, -220))                                              # handed in at the enquiry desk
things(STIM, (-230, -30), (230, -30))
things(TECHLAMP, (-232, -408), (232, -24))
# the shop window: what is on show
things(MEGA, (448, -352))
things(ROCKETBOX, (520, -400))
things(SPHERE, (380, -300))
things(CANDLE, (360, -408), (536, -296))
# the cash office: counting the takings, and deaf to the lobby
things(BARON, (-430, -180), angle=0, ambush=True)
things(KNIGHT, (-350, -360), angle=0, ambush=True)
things(TECHLAMP, (-296, -136), (-296, -408))
things(MEDIKIT, (-560, -220))
things(CELLS, (-330, -150))
# the atrium: late shoppers, round the fountain
things(IMP, (-300, 120), (300, 120), (-200, 400), (200, 400), (-300, 640), (300, 700), angle=270)
things(DEMON, (-120, 340), (120, 340), (0, 760), angle=270)
things(SERGEANT, (-330, 320), (330, 300), (-100, 880), (380, 860), angle=270)
things(ZOMBIE, (0, 160), (-200, 700), (400, 420), angle=270)
things(KNIGHT, (0, 660), angle=270)
things(CACO, (140, 520), angle=270, ambush=True)
things(REVENANT, (280, 960), angle=270)
things(SPECTRE, (-300, 480), (60, 880), angle=270)
things(CHAINGUNNER, (440, 700), angle=180)
things(TECHLAMP, (-360, 40), (360, 40), (-360, 1016), (488, 1016))
things(SHELLBOX, (-192, 320), (300, 1000))
things(MEDIKIT, (192, 320), (-340, 760), (0, 1000))
things(SHELLS, (-192, 740), (192, 740))
things(STIM, (-480, 40), (480, 780))
# the gallery: key 1, a chaingun, a rocket launcher for the crowd below, and
# those who watch from above
things(LAUNCHER, (-420, 300))
things(ROCKETBOX, (-480, 300), (-480, 1000))
things(MEDIKIT, (-480, 600))
things(CHAINGUNNER, (-448, 880), angle=0)
things(IMP, (-448, 340), (-448, 1000), (-448, 560), angle=0)
things(SERGEANT, (-420, 780), angle=0)
things(CHAINGUN, (-448, 480))
things(AMMOBOX, (-480, 180))
things(STIM, (-420, 960))
# the showroom: somebody lives in the frames
things(LODGER, (-320, 1320), args=(300,))
things(IMP, (-440, 1120), (-200, 1300), (70, 1160), (-360, 1400), angle=270)
things(DEMON, (-300, 1140), (-60, 1340), angle=270)
things(SERGEANT, (-100, 1160), (-480, 1300), angle=270)
things(KNIGHT, (-240, 1380), angle=270)
things(SPECTRE, (-420, 1220), angle=270)
things(ZOMBIE, (-220, 1150), (-300, 1260), angle=270)
things(TORCH_R, (-488, 1080), (104, 1416))
things(SHELLS, (-400, 1280), (-40, 1280))
things(MEDIKIT, (-490, 1200))
# the office: key 4, the lever, the caretaker
things(CHAINGUNNER, (200, 1380), angle=180)
things(IMP, (340, 1180), (180, 1200), angle=180)
things(TECHLAMP, (360, 1080), (360, 1416))
things(MEDIKIT, (160, 1090))
things(SHELLBOX, (350, 1360))
things(PLASMA, (300, 1160))                                                # for the dock, and the run
things(CELLS, (250, 1160), (250, 1120))
# the dock: between you and the shutter
things(DEMON, (-100, 1600), (200, 1700), angle=270)
things(SPECTRE, (-60, 1780), (-460, 1600), angle=270)
things(IMP, (60, 1680), (-160, 1700), (340, 1560), angle=270)
things(CHAINGUNNER, (224, 1584), angle=180)
things(REVENANT, (-20, 1560), angle=270)
things(SERGEANT, (300, 1720), (-460, 1760), angle=270)
things(SOUL, (100, 1580), angle=270)
things(LAMP, (-340, 1548), (-170, 1548), (-340, 1812), (-170, 1812))
things(SHELLS, (300, 1640), (-480, 1740))
things(SHELLBOX, (-480, 1560))
things(STIM, (360, 1560))
things(MEDIKIT, (-140, 1548), (350, 1700))
# the night room: someone has been waiting
things(REVENANT, (NX + 80, NY + 200), angle=270)
things(KNIGHT, (NX + 200, NY + 40), angle=270)
# the stockroom and its alcove
things(SPECTRE, (460, 1620), (760, 1820), (1000, 1600), (1120, 1850), angle=180)
things(DEMON, (700, 1600), (900, 1880), (460, 1900), angle=180)
things(IMP, (592, 1648), (880, 1680), (1008, 1872), angle=180)
things(SOUL, (640, 1900), (1100, 1700), angle=180)
things(SERGEANT, (980, 1760), (560, 1860), angle=180)
things(TORCH_G, (424, 1544), (1160, 1944))
things(MEDIKIT, (430, 1940))
things(SHELLBOX, (1150, 1560))
things(ARMOR, (1280, 1744))
things(CELLS, (1310, 1700), (1310, 1788))
things(CANDLE, (1224, 1704), (1224, 1784))
# the goods passage
things(ZOMBIE, (640, 1010), (900, 960), (1100, 1000), angle=180)
things(IMP, (768, 920), (1140, 1060), angle=180)
things(SERGEANT, (860, 1060), (600, 940), angle=180)
things(DEMON, (700, 1040), (1000, 940), angle=180)
things(TECHLAMP, (552, 1080), (1160, 920))
things(STIM, (1150, 1080))
things(CLIP, (560, 920), (600, 920))
things(BERSERK, (1088, 1200))                                              # at the head of the stairs: the stockroom is full of teeth
# the boiler room: do not open this door
things(MANCUBUS, (768, 1320), angle=270)
things(KNIGHT, (660, 1240), (880, 1240), angle=270)
things(SPHERE, (640, 1150))
things(ROCKETBOX, (880, 1150), (840, 1150))
# the west wing: toys, haberdashery, furniture
things(ZOMBIE, (-620, 80), (-900, 90), (-700, 300), angle=0)
things(IMP, (-940, 290), (-570, 190), (-800, 60), (-680, 120), angle=0)
things(SERGEANT, (-780, 280), (-900, 220), angle=0)
things(SPECTRE, (-870, 300), (-740, 90), angle=0)
things(CACO, (-640, 190), angle=0, ambush=True)
things(DEMON, (-710, 250), (-930, 150), angle=0)
things(IMP, (-1400, 60), (-1060, 70), (-1200, 300), angle=0)
things(CHAINGUNNER, (-1370, 300), (-1020, 300), angle=0)
things(DEMON, (-1300, 140), (-1100, 140), angle=0)
things(REVENANT, (-1200, 100), angle=0)
things(PAIN, (-1200, 180), angle=0)
things(KNIGHT, (-1120, -300), angle=90)
things(BARON, (-1216, -220), angle=90)
things(IMP, (-1400, -60), (-1060, -390), (-1400, -400), angle=90)
things(SERGEANT, (-1040, -60), (-1216, -60), angle=90)
things(TECHLAMP, (-952, 40), (-552, 312), (-1416, 312), (-1016, 40), (-1016, -408), (-1416, -200))
things(SHELLS, (-560, 310), (-1410, 200))
things(SHELLBOX, (-1410, 40))
things(MEDIKIT, (-950, 310), (-1020, -30), (-1010, 180))
things(STIM, (-1020, 200), (-1410, -410))
things(AMMOBOX, (-1100, -410))
things(ROCKETS, (-1216, -144), (-1250, -144))
# the roof
things(IMP, (-1360, 600), (-700, 480), (-1000, 480), (-660, 800), angle=0)
things(SERGEANT, (-1300, 900), (-800, 900), angle=0)
things(CHAINGUNNER, (-1360, 760), (-640, 620), angle=0)
things(CACO, (-1000, 700), (-1300, 480), angle=0, ambush=True)
things(REVENANT, (-700, 980), angle=0)
things(SOUL, (-1100, 460), (-760, 800), angle=0)
things(KNIGHT, (-840, 980), angle=0)
things(SUPER, (-1000, 800))
things(SHELLS, (-1000, 760), (-1000, 840))
things(SHELLBOX, (-1380, 440))
things(MEDIKIT, (-1380, 1000), (-630, 1010))
things(ARMOR, (-630, 450))
things(LAMP, (-1070, 950), (-914, 950))
# the east wing: china, linen, carpets
things(ZOMBIE, (600, 80), (900, 80), (600, 300), angle=180)
things(IMP, (760, 80), (900, 290), (560, 210), angle=180)
things(SERGEANT, (900, 210), (760, 300), angle=180)
things(DEMON, (620, 210), (880, 140), angle=180)
things(IMP, (610, 410), (920, 400), (580, 800), (640, 650), angle=270)
things(SPECTRE, (660, 400), (850, 400), angle=270)
things(CHAINGUNNER, (940, 680), (560, 680), angle=270)
things(ARACHNO, (752, 520), angle=270)
things(CACO, (752, 650), angle=270, ambush=True)
things(KNIGHT, (1390, 250), angle=180)
things(REVENANT, (1060, 270), (1260, 300), angle=180)
things(IMP, (1040, 60), (1410, 130), angle=180)
things(SERGEANT, (1170, 50), angle=180)
things(DEMON, (1100, 120), (1380, 60), angle=180)
things(ZOMBIE, (640, 760), (900, 760), angle=270)
things(TECHLAMP, (552, 40), (952, 312), (552, 376), (952, 824), (1016, 312), (1416, 312))
things(CANDELABRA, (952, 40), (552, 312))
things(SHELLBOX, (940, 376))
things(MEDIKIT, (560, 824), (1410, 200), (560, 40))
things(STIM, (940, 40), (1020, 40))
things(ROCKETS, (1250, 40), (1290, 40))
things(CELLS, (860, 824))
# the lamp store and the strongroom
things(CANDLE, (1016, -24), (1176, -24))
things(HELMET, (1170, -180))
things(LAUNCHER, (1328, -130))
things(ROCKETBOX, (1240, -180), (1410, -180))
things(MEGA, (1240, -30))
things(AMMOBOX, (1410, -30))

# --- ambushes: what taking a key brings (ajarmap.ambush) ----------------------
# key 1, on the gallery: up from the atrium, at a man with a rocket launcher
ajarmap.ambush(m, 1, CACO, (-250, 300), (-250, 640), angle=180)
# key 3, among the linen
ajarmap.ambush(m, 3, REVENANT, (560, 740), angle=0)
ajarmap.ambush(m, 3, IMP, (700, 400), (820, 400), angle=90)
# key 4, in the office: the showroom you are about to jump into
ajarmap.ambush(m, 4, DEMON, (-100, 1340), (-300, 1340), (-380, 1130), angle=0)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "store" is the arcade, the lobby, the atrium, the goods passage and the
# stockroom, and also the kiosk, the shop window and the boiler room, which
# open from inside. "office" is the balcony; "night" is the night room, whose
# brass frame takes BLUE only. The lamp store, the strongroom and PINK are left
# out: PINK never leaves, and nothing else needs it.
#
# The dash: a leg is how far it is, in map units, between two ends that can be
# run with a door in hand; an ordinary door on the way counts as a second of
# running (583). The limit is what a runner covers in the shutter's time less
# two seconds for the lever and the turns. Only the showroom's frames are
# within it.
RUN = 583
PUZZLE = dict(
    start="store", goal="exit", names=ajarmap.NAMES, complete=True,
    home_frame=ajarmap.HOME, only={ajarmap.HOME: BLUE},
    walk=[("gallery", "store"), ("gallery", "showroom"), ("roof", "gallery"),
          ("store", "showroom", "", "squeeze"), ("showroom", "store", "", "squeeze"),     # the turnstile
          ("showroom", "office", "", "squeeze"), ("office", "showroom"),                  # the gatepost; the gap
          ("showroom", "dock", "", "squeeze"), ("dock", "showroom", "", "squeeze"),       # the hatch
          ("dock", "store"),                                                              # the chute
          ("night", "dock"),                                                              # the shutter, pushed
          ("store", "west", "1"), ("west", "store", "1"),
          ("store", "east", "2"), ("east", "store", "2"),
          ("store", "cash", "34"), ("cash", "store", "34")],
    keys={"1": "gallery", "2": "roof", "3": "east", "4": "office"},
    frames={101: "store", 103: "store", 102: "west", 106: "showroom", 107: "showroom",
            ajarmap.HOME: "night"},
    doors={
        RED: dict(home="gallery", lean="store"),
        GREEN: dict(home="roof", lean="west"),
        YELLOW: dict(home="office", lean="east"),
        VIOLET: dict(home="dock", lean="dock"),
        BLUE: dict(home="night", lean="cash"),
    },
    pool=["store"],                        # the boiler room; the shop window
    dash=dict(at="office", to="night", limit=(SECONDS - 2) * RUN, legs={
        ("lever", 106): 460, ("lever", 107): 560,              # off the balcony
        ("lever", far_id(YELLOW)): 200,                        # back the way you came
        (106, 107): 190, (107, 106): 190,
        (far_id(VIOLET), "shutter"): 320,
        (101, 103): 2500 + 2 * RUN, (103, 101): 2500 + 2 * RUN,
        (101, 102): 2010 + 3 * RUN, (102, 101): 2010 + 3 * RUN,
    }),
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
