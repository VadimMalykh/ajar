"""Act 1, level 6: "After Hours" (MAP06).

A museum, shut for the night. Nothing new to learn: the doors, keys,
squeezes, bolts and Stray doors of the levels before, in a bigger building
with more ways round it. As in MAP05 the way out is built: BLUE's far side is
in one end of the night room, off the terrace, and an empty frame in the
other.

The catch: BLUE leans in the strongroom, behind a hole no door fits through.
The strongroom has a frame. Hang BLUE there and you are in the night room,
with BLUE behind you. To get it out, another door has to hang in the
strongroom in its place, and that door can only be brought in the way you
just came: through the night room, off the terrace. A door reaches the
terrace only from above, off the upper gallery (RED) or the roof (YELLOW).
So: one door hung to get up, a second carried round and swapped for BLUE,
and BLUE carried out through the second and round again.

Places. One floor to walk about in: the lobby (start), the great hall, the
cloakroom (RED), the gift shop, the cafe (GREEN) and, down steps, the sunken
court under the sky. Over the court's west side the upper gallery (RED's
far side; key 1), over its east side the roof (YELLOW's; key 3), north of it
the terrace (steps up from the court to a gap no door fits through; a drop
back) and the night room, bolted inside.
A mezzanine over the great hall (VIOLET's; key 4). The cellar (GREEN's; key
2, a frame), whose door up to the cafe is bolted on the cellar side. The
west wing (key 1): four rooms round, YELLOW, a frame, and the office (keys
3 and 4) with the hole into the strongroom. The east wing (key 2): four
rooms round, VIOLET, and the archive (keys 2 and 3): Stray doors.

Secrets: the stockroom behind the gift shop (a squeeze) and PINK's store;
the grotto off the court (the office's lever, or a Stray door); the
gardener's shed (shoot its bell through the bars); a nook off the roof.
"""
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


UP, ROOF, MEZZ, COURT, CELLAR = 160, 224, 192, -72, -128
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
LOW = dict(ceil=128, ctex="AJBOARD")                  # a porch: doors and frames in tall rooms stand under one
SEAT = dict(ftex="AJSOFA", side="AJSOFA", floor=16)
CASE = dict(ftex="AJSTEEL", side="AJWOOD", floor=40)  # a display case, a plinth, a counter
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
NIGHT_BOLT, CELLAR_BOLT, GROTTO, SHED = 401, 402, 403, 404
NX, NY = 160, 2256                                    # the night room's south-west corner


CRATE = dict(ftex="AJWOOD", side="AJWOOD")

# The museum's look (gfx_museum.py): 2, Cabinet (terracotta, glazed tile,
# mahogany), is the user's choice for the whole of it. AJAR_MUSEUM=1 and 3 are
# the candidates that lost (Athenaeum: ashlar and marble; Kunsthalle: white
# walls, concrete); AJAR_MUSEUM=0 is the level as first built. A look changes
# textures only: no floor, wall or railing moves. Rooms are not tinted in a look.
LOOK = (os.environ.get("AJAR_MUSEUM") or "2").replace("0", "")


def T(tag, pic=""):
    return f"AJ6{tag}{LOOK}{pic}"


if LOOK:
    import gfx_museum
    m.align = gfx_museum.aligned(LOOK)
    WARM = GOLD = SKY = LEAF = PLUM = ROSE = None
    FRONT, LOWW, HALLW = T("Y"), T("A"), T("H")
    OPEN = dict(ceil=512, ctex="F_SKY1", wall=FRONT)
    RAIL = dict(RAIL, mid=T("RL"), floorpeg=True)
    LOW = dict(ceil=128, ctex=T("CP"), wall=LOWW)
    SEAT = dict(ftex=T("BN"), side=T("BN"), floor=16)
    CASE = dict(ftex=T("VT"), side=T("V"), floor=40)
    WOOD = dict(ftex=T("WD"), side=T("WD"))
    TICKET = dict(WOOD, floor=40)
    TABLE = dict(ftex="AJ6XT", side="AJ6XT")
    SHELF = dict(ftex=T("WD"), side="AJ6XA")
    BENCH = dict(ftex="AJ6XP", side="AJ6XP")                # a garden seat
    PATH, PAVE, LAWN, STONE, STONEF, HOLE = T("P"), T("FT"), T("FG"), "AJ6XP", "AJ6XP", "AJTRIM"
    LOBBY = dict(wall=T("L"), ftex=T("F"), ctex=T("CG"))
    HALL = dict(wall=HALLW, ftex=T("F"), ctex=T("CH"))
    STAIR = dict(wall=T("S"), ftex="AJ6XP", side="AJ6XP", ctex=T("CP"))
    STEPS = dict(wall=T("S"), ftex=T("FT"), side="AJ6XP", ctex=T("CP"))
    LANDING = dict(wall="AJ6XC", ftex="AJ6XP")
    TERR = dict(OPEN, side=T("YE"))
    UPPER = dict(wall=T("U"), side=T("YG"), ftex=T("FW"), ctex=T("CG"))
    UPPER_S = [((-256, 1152, -64, 1168), dict(side=T("HG")))]   # its front onto the great hall
    ROOFO = dict(OPEN, wall=T("YU"), side=T("YS"))
    ROOFF, ROOFP = T("FR"), dict(ceil=ROOF + 128, ctex=T("CP"), wall=LOWW)
    NOOK = dict(wall=LOWW, ftex=T("FR"), ctex=T("CP"))
    MEZZW = dict(wall=T("HM"), side=T("HV"), ftex=T("FW"), ctex=T("CH"))
    CELLW, BOILER = "AJ6XC", "AJ6XB"
    GROT = dict(wall="AJ6XG", ftex="AJ6XP", ctex="AJ6XG")
    SHEDW = dict(wall="AJ6XS", ftex=T("FT"), ctex="AJBOARD")
    STOCK = dict(wall="AJ6XK", ftex=T("FI"), ctex=T("CL"))

    def room(tag, floor="FI"):
        return dict(wall=T(tag), ftex=T(floor), ctex=T("CG" if len(tag) == 2 else "CL"))
    CLOAK, SHOP, CAFE, OFFICE, ARCHIVE = room("K"), room("M"), room("C", "FC"), room("O"), room("R")
    WA, WB, EA, EB = room("WA", "FW"), room("WB", "FW"), room("EA", "FW"), room("EB", "FW")
else:
    FRONT = LOWW = HALLW = None
    TICKET, TABLE, SHELF, BENCH = CASE, WOOD, WOOD, dict(ftex="AJSOFA", side="AJSOFA")
    PATH, PAVE, LAWN, STONE, STONEF, HOLE = "AJARCHF", "AJARCHF", "AJGRASS", "AJTRIM", "AJTRIMF", "AJBRICK"
    LOBBY = HALL = dict(wall="AJBRICK", ftex="AJFLOOR")
    STAIR = LANDING = dict(wall="AJBRICK", ftex="AJBOARD")
    STEPS = dict(wall="AJBRICK", ftex="AJARCHF")
    TERR = ROOFO = OPEN
    UPPER = MEZZW = dict(wall="AJBRICK", ftex="AJBOARD")
    UPPER_S = []
    ROOFF, ROOFP = "AJSTEEL", dict(ceil=ROOF + 128, ctex="AJBOARD")
    NOOK = dict(wall="AJBRICK", ftex="AJSTEEL")
    CELLW, BOILER = "AJBRICK", "AJSAFE"
    GROT = SHEDW = STOCK = dict(wall="AJSAFE")
    CLOAK = SHOP = CAFE = OFFICE = ARCHIVE = WA = WB = EA = EB = {}


def low(floor):
    return dict(LOW, ceil=floor + 128)


def rail(*runs, **more):
    """Railings. In a look `more` is what else their lines carry (the wall
    over a gallery that has a ceiling)."""
    for a, b in runs:
        m.cut(a, b)
        m.line(a, b, **dict(RAIL, **(more if LOOK else {})))


def over(a, b, tex, **k):
    """In a look: the wall over the opening a-b (under a lower ceiling) carries
    on as `tex`, in line with the wall beside it."""
    if LOOK:
        m.line(a, b, upper=tex, dontpegtop=True, **k)


def porch(box, tex, sides):
    """The walls over the open sides ("SENW") of a low-ceilinged piece of a
    taller place. Not the others: a door in one would be painted over."""
    x1, y1, x2, y2 = box
    ends = dict(S=((x1, y1), (x2, y1)), E=((x2, y1), (x2, y2)), N=((x2, y2), (x1, y2)), W=((x1, y2), (x1, y1)))
    for side in sides:
        over(*ends[side], tex)


def pieces(tex, fixed, starts, axis="x", upper=False, names="AB", look=True):
    """In a look: 64-long pieces of a wall with their own texture, `tex` and
    one of `names` by turns (windows lit and dark, pictures). Each starts at a
    multiple of 64. `upper`: the wall is the one over an opening; such pieces
    are declared before the porch() or over() of the whole opening."""
    for i, s in enumerate(starts if LOOK else ()):
        a, b = ((s, fixed), (s + 64, fixed)) if axis == "x" else ((fixed, s), (fixed, s + 64))
        name = f"AJ6{tex}{names[i % len(names)]}{LOOK}" if look else f"AJ6{tex}{LOOK}{names[i % len(names)]}"
        m.cut(a, b)
        if upper:
            m.line(a, b, upper=name, dontpegtop=True)
        else:
            m.line(a, b, mid=name)


def pictures(tag, fixed, starts, axis="x", names="123"):
    """In a look: pictures and exhibits on 64-long pieces of a room's wall."""
    pieces(tag, fixed, starts, axis, names=names, look=False)


def door(a, b, out, floor, faces, **k):
    """A room door. In a look each side has its own face (gfx_museum.FACES):
    the wall of the room it is seen from carries on over it."""
    ajarmap.roomdoor(m, a, b, out, floor, **k)
    if LOOK:
        m.line(a, b, upper=f"AJ6D{LOOK}{faces[0]}")
        m.line((a[0] + out[0] * 16, a[1] + out[1] * 16), (b[0] + out[0] * 16, b[1] + out[1] * 16),
               upper=f"AJ6D{LOOK}{faces[1]}")


def bolted(a, b, out, floor, tag, faces, **k):
    """A bolted door; `faces` as door()'s (gfx_museum.BOLTS), "-" for a side
    that stays as it is (the night room's)."""
    ajarmap.bolted(m, a, b, out, floor, tag, **k)
    for face, p, q in ((faces[0], a, b), (faces[1], (a[0] + out[0] * 16, a[1] + out[1] * 16),
                                         (b[0] + out[0] * 16, b[1] + out[1] * 16))):
        if LOOK and face != "-":
            m.line(p, q, upper=f"AJ6Z{LOOK}{face}")


def opening(a, b, out, floor, near, far):
    """An open way between two rooms of a wing; in a look their walls carry on over it."""
    ajarmap.opening(m, a, b, out, floor)
    over(a, b, near and near.get("wall"))
    over((a[0] + out[0] * 16, a[1] + out[1] * 16), (b[0] + out[0] * 16, b[1] + out[1] * 16), far and far.get("wall"))


def squeeze(a, b, out, floor, near, far):
    ajarmap.squeeze(m, a, b, out, floor)
    over(a, b, near)
    over((a[0] + out[0] * 16, a[1] + out[1] * 16), (b[0] + out[0] * 16, b[1] + out[1] * 16), far)


def bars(a, b, out, floor, near=None, far=None):
    """A barred opening in a 16 thick wall: to look and shoot through. In a
    look, `near` and `far` are the walls it is cut through on either side."""
    c = (a[0] + out[0] * 16, a[1] + out[1] * 16)
    d = (b[0] + out[0] * 16, b[1] + out[1] * 16)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall=HOLE,
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)
    if LOOK:
        m.line(a, b, upper=near, lower=near, dontpegtop=True, dontpegbottom=True)
        m.line(c, d, upper=far, lower=far, dontpegtop=True, dontpegbottom=True)


def gallery(box, cases, **k):
    """A room of a wing: 160 high, with display cases."""
    ajarmap.fitted(m, box, [(c, CASE) for c in cases], **dict(dict(ceil=160, light=175), **k))


# === the ground floor ===========================================================
# the lobby: start here
ajarmap.fitted(m, (0, 0, 640, 384), [
    ((256, 0, 384, 384), dict(ftex=PATH)),                                   # the way in
    ((32, 256, 160, 320), TICKET),                                           # the ticket desk
    ((544, 32, 608, 96), SEAT),
], floor=0, ceil=192, light=185, **LOBBY)
pictures("L", 0, (64,), "y", "1")                                            # the plan of the museum
pictures("L", 640, (256,), "y", "1")
pictures("L", 0, (128,), "x", "1")
recess((416, 0), (480, 0), (0, -1), 0, 101, 201)                             # frame in the lobby

# the great hall
ajarmap.fitted(m, (-256, 384, 896, 1152), [
    ((-256, 896, -192, 1088), LOW),                                          # before the west wing's door
    ((832, 576, 896, 768), LOW),                                             # before the cafe's
    ((192, 1088, 672, 1152), LOW),                                           # the head of the steps; a frame
    ((256, 384, 384, 1152), dict(ftex=PATH)),                                # the way through
    ((-64, 640, 0, 896), SEAT), ((640, 640, 704, 896), SEAT),                # benches
    ((64, 512, 128, 576), CASE), ((512, 512, 576, 576), CASE),               # plinths
    ((64, 960, 128, 1024), CASE), ((512, 960, 576, 1024), CASE),
], floor=0, ceil=384, light=190, **HALL)
for box, sides in (((-256, 896, -192, 1088), "SEN"), ((832, 576, 896, 768), "SWN"), ((192, 1088, 672, 1152), "SWE")):
    porch(box, T("HK"), sides)
over((0, 384), (640, 384), T("HL"))                                          # the lobby's mouth
pictures("H", 384, (-192, 768), "x", "12")
pictures("H", 1152, (0, 768), "x", "21")
pictures("H", 896, (448, 896, 1024), "y", "12")
recess((544, 1152), (608, 1152), (0, 1), 0, 102, 201)                        # frame in the great hall

# the cloakroom: RED
ajarmap.fitted(m, (-288, 64, -16, 320), [((-288, 64, -256, 256), dict(WOOD, floor=48)),
                                         ((-160, 288, -64, 320), dict(WOOD, floor=48))],
               ceil=128, light=170, color=WARM, **CLOAK)
door((0, 160), (0, 224), (-1, 0), 0, "AB")
# the gift shop, and behind its counter a hole into the stockroom (secret): PINK hangs there
ajarmap.fitted(m, (656, 64, 944, 320), [((736, 128, 864, 192), CASE), ((672, 288, 800, 320), dict(WOOD, floor=64))],
               ceil=128, light=175, color=GOLD, **SHOP)
door((640, 160), (640, 224), (1, 0), 0, "AC")
m.sector(rect(960, 64, 1136, 320), ceil=112, light=140, color=ROSE, special=1024, **STOCK)
squeeze((944, 232), (944, 280), (1, 0), 0, T("M"), "AJ6XK")
recess((1016, 320), (1080, 320), (0, 1), 0, 107, 201, color=ROSE)

# the cafe: GREEN, the east wing's door (one lock), and steps down to the cellar
ajarmap.fitted(m, (912, 480, 1360, 960), [
    ((1008, 608, 1072, 672), dict(TABLE, floor=32)), ((1008, 800, 1072, 864), dict(TABLE, floor=32)),
    ((1168, 704, 1232, 768), dict(TABLE, floor=32)),
    ((912, 864, 944, 960), CASE),                                            # the counter
], ceil=128, light=175, color=LEAF, **CAFE)
pictures("C", 912, (512,), "y", "1")                                         # the menu
pictures("C", 960, (960,), "x", "1")
pictures("C", 1360, (640,), "y", "1")
door((896, 640), (896, 704), (1, 0), 0, "DE")
ajarmap.stairs(m, (1232, 480), (1296, 480), (0, -1), 0, CELLAR, light=150, **STAIR)
m.sector(rect(1232, 160, 1296, 224), floor=CELLAR, ceil=0, light=140, **LANDING)
over((1232, 224), (1296, 224), T("S"))

# --- the sunken court, under the sky -------------------------------------------
ajarmap.stairs(m, (256, 1152), (384, 1152), (0, 1), 0, COURT, steps=6, light=200, **STEPS)
ajarmap.fitted(m, (-64, 1344, 704, 1984), [
    ((0, 1344, 192, 1408), low(COURT)),                                      # before the grotto's door
    ((448, 1344, 688, 1408), low(COURT)),                                    # before the shed's
    ((256, 1344, 384, 1984), dict(ftex=PAVE)),                               # the path
    ((224, 1600, 416, 1728), dict(floor=COURT + 32, ftex="AJWATER", side=STONE)),      # the fountain
    ((32, 1536, 96, 1792), dict(BENCH, floor=COURT + 16)), ((544, 1536, 608, 1792), dict(BENCH, floor=COURT + 16)),
    # steps up to the terrace, and at their head a gap by a gatepost that no door fits through
] + [((640, 1776 + 32 * i, 704, 1808 + 32 * i), dict(floor=COURT + 12 * (i + 1), ftex=PAVE, side=STONE))
     for i in range(6)] + [
    ((640, 1968, 704, 1984), dict(floor=0, ftex=STONEF, side=STONE)),
    ((640, 1968, 656, 1984), dict(floor=56, ftex=STONEF, side=STONE)),
], floor=COURT, light=210, ftex=LAWN, **OPEN)
pieces("Y", 1344, (-64, 192, 384), names="BAB")                              # windows in the hall's back wall
pieces("YC", 1408, (0, 128, 448, 576), upper=True)                           # and over the two porches
pieces("YT", 1344, (256, 320), upper=True)                                   # and over the mouth of the steps
porch((0, 1344, 192, 1408), T("YC"), "ENW")
porch((448, 1344, 688, 1408), T("YC"), "ENW")
m.line((656, 1968), (704, 1968), id=ajarmap.SQUEEZE, blockmonsters=True)
# the grotto (secret): the lever in the office opens it, or you come by Stray door
m.sector(rect(-32, 1264, 176, 1328), floor=COURT, ceil=COURT + 112, light=150, special=1024, **GROT)
m.sector(rect(-32, 1168, 176, 1264), floor=COURT, ceil=COURT + 112, light=150, **GROT)
bolted((64, 1344), (128, 1344), (0, -1), COURT, GROTTO, "BE", line_id=307)
ajarmap.unbolt(m, (-32, 1264), (176, 1264), GROTTO)
ajarmap.stray_place(m, 0, (176, 1184), (176, 1248), (1, 0), COURT, color=ROSE)
# the gardener's shed (secret), seen through bars from the court: shoot its bell
m.sector(rect(416, 1232, 688, 1328), floor=COURT, ceil=COURT + 112, light=170, color=ROSE, special=1024,
         **SHEDW)
bars((592, 1344), (656, 1344), (0, -1), COURT, LOWW, "AJ6XS")
bolted((480, 1344), (544, 1344), (0, -1), COURT, SHED, "AF")
m.cut((592, 1232), (656, 1232))
m.line((592, 1232), (656, 1232), special=11, args=(SHED, 32), impact=True, mid="AJTARG6" if LOOK else "AJTARG", exact=True)

# --- the terrace, and the night room off it -------------------------------------
ajarmap.fitted(m, (-64, 1984, 704, 2240), [
    ((192, 2176, 448, 2240), LOW),                                           # before the night room's door
    ((0, 2176, 128, 2208), dict(BENCH, floor=16)), ((512, 2176, 640, 2208), dict(BENCH, floor=16)),
], floor=0, light=210, ftex=PAVE, **TERR)
pieces("Y", 2240, (0, 128, 512, 640), names="ABBA")
pieces("YT", 2176, (192, 384), upper=True)
porch((192, 2176, 448, 2240), T("YT"), "SEW")
# the night room: BLUE's far side at one end, the frame at the other. Its
# door onto the terrace is bolted inside
ajarmap.way_home(m, NX, NY, BLUE)
bolted((NX + 128, 2240), (NX + 192, 2240), (0, 1), 0, NIGHT_BOLT, "A-", line_id=304)
ajarmap.unbolt(m, (NX, NY + 96), (NX + 320, NY + 96), NIGHT_BOLT)

# === above ======================================================================
# --- the upper gallery (RED's far side): the great hall, the court, the terrace ---
ajarmap.fitted(m, (-256, 1152, -64, 2240), UPPER_S, floor=UP, ceil=UP + 176, light=190, color=WARM, **UPPER)
rail(((-256, 1152), (-208, 1152)), ((-112, 1152), (-64, 1152)),              # a gap over the great hall
     upper=HALLW, dontpegtop=True)
rail(((-64, 1344), (-64, 1792)), ((-64, 1920), (-64, 1984)),                 # one over the court
     ((-64, 1984), (-64, 2048)), ((-64, 2176), (-64, 2240)),                 # one over the terrace
     upper=FRONT, dontpegtop=True)
over((-256, 1152), (-64, 1152), HALLW)
over((-64, 1344), (-64, 2240), FRONT)
pictures("U", -256, (1280, 1408, 1792, 1920, 2048), "y", "12")
pictures("U", 2240, (-192,), "x", "2")
recess((-256, 1600), (-256, 1664), (-1, 0), UP, far_id(RED), 101, far_colour=RED, color=WARM)

# --- the roof (YELLOW's far side) along the court's east side ---------------------
ajarmap.fitted(m, (704, 1344, 896, 2240), [((832, 1664, 896, 1856), ROOFP)],
               floor=ROOF, light=220, color=GOLD, ftex=ROOFF, **ROOFO)
porch((832, 1664, 896, 1856), T("YR"), "SNW")
rail(((704, 1344), (704, 1568)), ((704, 1696), (704, 1984)),
     ((704, 1984), (704, 2048)), ((704, 2176), (704, 2240)))
recess((896, 1728), (896, 1792), (1, 0), ROOF, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)
m.sector(rect(752, 2240, 848, 2336), floor=ROOF, ceil=ROOF + 96, light=110, special=1024, **NOOK)  # a nook (secret)
over((752, 2240), (848, 2240), T("YU"))

# --- the mezzanine (VIOLET's far side), over the great hall's west side -----------
ajarmap.fitted(m, (-512, 448, -256, 832), [], floor=MEZZ, ceil=384, light=190, color=PLUM, **MEZZW)
rail(((-256, 448), (-256, 704)), ((-256, 800), (-256, 832)))
recess((-512, 608), (-512, 672), (-1, 0), MEZZ, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)

# === below: the cellar (GREEN's far side) =========================================
CELL = dict(floor=CELLAR, ceil=0, light=140, wall=CELLW, ftex="AJPIT")
ajarmap.fitted(m, (1216, -64, 1856, 144), [((1408, 16, 1536, 144), dict(CRATE, floor=CELLAR + 48)),
                                           ((1536, 80, 1600, 144), dict(CRATE, floor=CELLAR + 96))], **CELL)
ajarmap.fitted(m, (1216, -448, 1856, -64), [((1344, -320, 1408, -192), dict(CRATE, floor=CELLAR + 48)),
                                            ((1664, -256, 1792, -192), dict(CRATE, floor=CELLAR + 48))], **CELL)
bolted((1232, 160), (1296, 160), (0, -1), CELLAR, CELLAR_BOLT, "CD", line_id=305)
ajarmap.unbolt(m, (1216, -64), (1856, -64), CELLAR_BOLT)
recess((1216, -168), (1216, -104), (-1, 0), CELLAR, 104, 201)                # the cellar's frame
recess((1504, -448), (1568, -448), (0, -1), CELLAR, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)
# the boiler room: behind an ordinary door, and one of the places a Stray door opens onto
m.sector(rect(1872, -384, 2192, -128), **dict(CELL, wall=BOILER, light=120))
door((1856, -288), (1856, -224), (1, 0), CELLAR, "NO")
ajarmap.stray_place(m, 1, (2192, -288), (2192, -224), (1, 0), CELLAR)

# === the west wing: one lock ======================================================
gallery((-720, 848, -272, 1136), [((-528, 960, -464, 1024))], color=SKY, **WA)
gallery((-720, 1152, -352, 1600), [((-592, 1280, -480, 1344)), ((-592, 1440, -480, 1504))], **WB)
gallery((-1200, 1152, -736, 1600), [((-1040, 1344, -912, 1408))], **WA)
gallery((-1200, 848, -736, 1136), [((-1136, 912, -1072, 976)), ((-864, 912, -800, 976))], color=GOLD, **WB)
door((-256, 960), (-256, 1024), (-1, 0), 0, "FG", keys="1", line_id=301)
opening((-432, 1136), (-368, 1136), (0, 1), 0, WA, WB)
opening((-720, 1376), (-720, 1440), (-1, 0), 0, WB, WA)
opening((-1120, 1152), (-1056, 1152), (0, -1), 0, WA, WB)
opening((-720, 1040), (-720, 1104), (-1, 0), 0, WA, WB)
pictures("WA", 848, (-640, -512, -384))                                      # antiquities: the first room
pictures("WA", 1136, (-640, -576), names="23")
pictures("WA", -720, (896,), "y", "1")
pictures("WB", -720, (1216, 1472), "y")                                      # the second
pictures("WB", -352, (1216, 1344, 1472), "y", "312")
pictures("WB", 1152, (-640, -576), names="21")
pictures("WB", 1600, (-512, -448), names="13")
pictures("WA", -1200, (1344, 1472), "y", "23")                               # the third
pictures("WA", 1600, (-1152, -1024, -896), names="312")
pictures("WA", -736, (1216, 1472), "y", "13")
pictures("WA", 1152, (-960, -832), names="21")
pictures("WB", 848, (-1024, -960), names="12")                               # the fourth
pictures("WB", 1136, (-960, -832), names="31")
pictures("WB", -736, (896,), "y", "2")
recess((-1200, 1216), (-1200, 1280), (-1, 0), 0, 103, 201)                   # the west wing's frame
# the office: two locks. A desk, a lever, and a hole in the wall behind the desk
ajarmap.fitted(m, (-720, 1616, -352, 1904), [((-656, 1728, -464, 1792), dict(WOOD, floor=40)),
                                             ((-400, 1616, -352, 1728), SEAT)],
               ceil=128, light=175, color=PLUM, **OFFICE)
door((-656, 1600), (-592, 1600), (0, 1), 0, "JK", keys="34", line_id=303)
m.line((-720, 1728), (-720, 1792), special=11, args=(GROTTO, 32), playeruse=True, mid=f"AJ6LV{LOOK}" if LOOK else "AJLEVR", exact=True,
       id=308)
# the strongroom: BLUE, and a frame. No door comes in or out by the hole
m.sector(rect(-720, 1920, -352, 2176), ceil=128, light=150, color=SKY, wall="AJSAFE")
squeeze((-560, 1904), (-512, 1904), (0, 1), 0, T("O"), "AJSAFE")
recess((-568, 2176), (-504, 2176), (0, 1), 0, 105, 201, color=SKY)           # the strongroom's frame

# === the east wing: one lock ======================================================
gallery((976, 976, 1424, 1392), [((1168, 1152, 1232, 1216))], color=LEAF, **EA)
gallery((976, 1408, 1424, 1856), [((1072, 1536, 1136, 1728)), ((1264, 1536, 1328, 1728))], **EB)
gallery((1440, 1408, 1888, 1856), [((1632, 1600, 1696, 1664))], color=PLUM, **EA)
gallery((1440, 976, 1888, 1392), [((1568, 1088, 1760, 1152))], **EB)
door((1104, 960), (1168, 960), (0, 1), 0, "HI", keys="2", line_id=302)
opening((1008, 1392), (1072, 1392), (0, 1), 0, EA, EB)
opening((1424, 1760), (1424, 1824), (1, 0), 0, EB, EA)
opening((1792, 1408), (1856, 1408), (0, -1), 0, EA, EB)
opening((1440, 1008), (1440, 1072), (-1, 0), 0, EB, EA)
pictures("EA", 976, (1024, 1216, 1344))                                      # paintings: the first room
pictures("EA", 976, (1024, 1152, 1280), "y", "231")
pictures("EA", 1392, (1152, 1280), names="31")
pictures("EA", 1424, (1152, 1280), "y", "12")
pictures("EB", 976, (1472, 1600, 1728), "y")                                 # the second
pictures("EB", 1408, (1152, 1280), names="23")
pictures("EB", 1856, (1024, 1280), names="31")
pictures("EB", 1424, (1472, 1600), "y", "21")
pictures("EA", 1856, (1536, 1664, 1792), names="213")                        # the third
pictures("EA", 1888, (1472, 1728), "y", "31")
pictures("EA", 1408, (1536, 1664), names="12")
pictures("EA", 1440, (1472, 1600), "y", "23")
pictures("EB", 976, (1536, 1664, 1792), names="312")                         # the fourth
pictures("EB", 1888, (1024, 1152, 1280), "y", "123")
pictures("EB", 1392, (1536, 1664), names="23")
pictures("EB", 1440, (1152, 1280), "y", "31")
# the archive: two locks. Shelves, and what was never catalogued
ajarmap.fitted(m, (976, 1872, 1424, 2208), [((1040, 1968, 1104, 2144), dict(SHELF, floor=72)),
                                            ((1296, 1968, 1360, 2144), dict(SHELF, floor=72))],
               ceil=128, light=160, color=GOLD, **ARCHIVE)
door((1168, 1856), (1232, 1856), (0, 1), 0, "LM", keys="23", line_id=306)

# === far sides that are places of their own =====================================
# the store (PINK's far side): no other way in (secret)
m.sector(rect(4000, 0, 4448, 384), ceil=160, light=150, color=ROSE, wall="AJSAFE", special=1024)
recess((4000, 160), (4000, 224), (-1, 0), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)

# --- doors and keys ----------------------------------------------------------
m.thing(320, 64, 1, angle=90)                                             # player start, in the lobby
ajarmap.stray(m, 620, 360, angle=180)                                     # a Stray door in the lobby
ajarmap.stray(m, 680, 2010, angle=180)                                    # one on the terrace
ajarmap.stray(m, 1000, 2180, angle=0)                                     # two in the archive
ajarmap.stray(m, 1400, 2180, angle=180)
ajarmap.door(m, RED, -150, 84, angle=90)                                  # leaning in the cloakroom
ajarmap.door(m, GREEN, 1340, 900, angle=180)                              # leaning in the cafe
ajarmap.door(m, YELLOW, -1180, 1000, angle=0)                             # leaning in the west wing
ajarmap.door(m, VIOLET, 1860, 1600, angle=180)                            # leaning in the east wing
ajarmap.door(m, BLUE, -380, 2040, angle=180)                              # leaning in the strongroom
ajarmap.door(m, PINK, 1048, 300, frame=107)                               # hanging in the stockroom
ajarmap.key(m, 1, -160, 2200)                                             # north end of the upper gallery
ajarmap.key(m, 2, 1800, -400)                                             # the cellar
ajarmap.key(m, 3, 800, 2200)                                              # north end of the roof
ajarmap.key(m, 4, -384, 480)                                              # south end of the mezzanine

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


# the lobby: a shotgun for anyone who came without one
things(SHOTGUN, (200, 80))
things(SHELLS, (160, 80), (160, 120))
things(STIM, (600, 140))
things(LAMP, (24, 24), (616, 24))
things(ZOMBIE, (120, 200), (520, 240), angle=270)
things(IMP, (320, 340), angle=270)
# the great hall: the night staff. The lodger wakes when you are well into it
# Fireballs and teeth at the front, guns at the back: from the lobby the men at
# the far end shoot through everything that is coming for you
things(ZOMBIE, (-100, 500), (700, 500), (-150, 1050), (160, 1060), (480, 1060), angle=270)
things(IMP, (-180, 450), (820, 450), (96, 640), (544, 640), (200, 800), (440, 800), angle=270)
things(SERGEANT, (0, 980), (640, 980), (320, 1080), angle=270)
things(DEMON, (320, 620), (760, 900), angle=270)
things(CACO, (320, 880), angle=270, ambush=True)
things(LODGER, (320, 760), args=(300,))
things(LAMP, (-232, 408), (872, 408), (-232, 870), (872, 1128))
things(SHELLS, (-32, 600), (672, 600), (320, 1120))
things(SHELLBOX, (864, 600))
things(LAUNCHER, (420, 1120))                                              # at the head of the steps: the court is next
things(ROCKETS, (460, 1120), (460, 1090))
things(CLIP, (320, 460), (320, 540))
things(STIM, (-220, 760), (860, 800))
things(MEDIKIT, (860, 1100))
# the cloakroom: RED, and those who never collected their coats
things(ZOMBIE, (-80, 120), (-220, 280), angle=0)
things(IMP, (-200, 180), angle=0)
things(TORCH_R, (-232, 88), (-40, 88))
things(STIM, (-40, 300))
# the gift shop
things(SERGEANT, (700, 100), (900, 100), angle=180)
things(IMP, (800, 250), angle=180)
things(CLIP, (680, 240), (720, 240))
things(HELMET, (900, 300))
things(BACKPACK, (900, 160))                                               # the shop sells bags
# the stockroom
things(IMP, (1000, 100), (1100, 100), angle=90)
things(SHELLBOX, (1100, 280))
things(CANDLE, (976, 80), (1120, 80))
# the store: what the museum does not show
things(LAUNCHER, (4380, 192))
things(ROCKETBOX, (4380, 140), (4380, 244))
things(MEGA, (4400, 340))
things(AMMOBOX, (4400, 40))
things(REVENANT, (4250, 100), (4250, 290), angle=180)
things(KNIGHT, (4130, 192), angle=180)
things(CANDELABRA, (4424, 24), (4424, 360))
# the cafe: GREEN, and a late supper
things(ZOMBIE, (960, 540), (1300, 560), angle=180)
things(SERGEANT, (1120, 900), (1300, 800), angle=180)
things(IMP, (1120, 560), (1280, 640), angle=180)
things(DEMON, (1100, 740), angle=180)
things(TORCH_G, (1336, 840), (1208, 936))
things(CHAINGUN, (980, 920))
things(AMMOBOX, (1020, 920))
things(BERSERK, (1280, 900))                                               # by GREEN: for what is in the cellar
things(STIM, (940, 500), (1340, 500))
# the court: under the sky, and overlooked from three sides
# The sergeants are at the far end, under the terrace: from the steps they shoot
# through the whole court. The galleries on either side look at each other
things(IMP, (0, 1420), (640, 1440), (60, 1830), (580, 1830), (160, 1664), (480, 1664), angle=270)
things(DEMON, (120, 1500), (520, 1500), (320, 1820), angle=270)
things(SPECTRE, (140, 1890), (500, 1890), angle=270)
things(SERGEANT, (220, 1950), (440, 1940), angle=270)
things(KNIGHT, (320, 1500), angle=270)
things(CACO, (160, 1760), angle=270, ambush=True)
things(SOUL, (320, 1560), (420, 1900), angle=270)
things(BARREL, (-32, 1560), (672, 1560), (-32, 1960))
things(LAMP, (232, 1368), (408, 1368))
things(SHELLS, (64, 1520), (576, 1520))
things(MEDIKIT, (-32, 1700), (672, 1700))
things(ROCKETS, (320, 1960), (360, 1960))
# the grotto
things(SPHERE, (0, 1200))
things(SHELLBOX, (60, 1200))
things(CELLS, (120, 1200))
things(SPECTRE, (72, 1296), angle=90)
things(CANDLE, (-16, 1312), (160, 1312))
# the gardener's shed
things(PLASMA, (552, 1280))
things(CELLS, (500, 1260), (604, 1260))
things(MEGA, (440, 1280))
# the upper gallery: snipers over the great hall and the court
things(CHAINGUNNER, (-100, 1500), angle=0)
things(IMP, (-200, 1300), (-200, 1760), (-120, 2100), (-100, 1860), angle=0)
things(SERGEANT, (-160, 1200), angle=270)
things(REVENANT, (-200, 2000), angle=270)
things(TORCH_R, (-232, 1576), (-232, 1688))
things(MEDIKIT, (-230, 1250))
things(SUPER, (-220, 2200))
things(SHELLS, (-220, 2160), (-220, 2120))
things(STIM, (-100, 1180))
# the roof
things(CHAINGUNNER, (760, 1900), angle=180)
things(IMP, (860, 1400), (860, 1960), (760, 2120), (760, 1500), angle=180)
things(SERGEANT, (800, 1620), angle=180)
things(KNIGHT, (800, 2060), angle=270)
things(CACO, (800, 1440), angle=180, ambush=True)
things(MEDIKIT, (872, 1368))
things(ROCKETBOX, (872, 2216))
things(ARMOR, (800, 2300))                                                 # in the nook
# the terrace
things(REVENANT, (100, 2100), (540, 2100), angle=270)
things(IMP, (0, 2030), (640, 2030), (320, 2040), angle=270)
things(SERGEANT, (220, 2140), (420, 2140), angle=270)
things(LAMP, (208, 2216), (432, 2216))
things(ARMOR, (64, 2224))
things(STIM, (576, 2224))
# the night room: someone has been waiting
things(REVENANT, (NX + 160, NY + 200), angle=270)
things(KNIGHT, (NX + 224, NY + 40), angle=90)
# the mezzanine
things(CHAINGUNNER, (-300, 760), angle=0)
things(IMP, (-460, 780), (-300, 500), angle=0)
things(KNIGHT, (-440, 520), angle=0)
things(STIM, (-480, 800))
things(SHELLBOX, (-480, 480))
things(PLASMA, (-400, 810))                                                # the cells have been lying about since the strongroom
things(CELLS, (-360, 810))
# the cellar
things(SPECTRE, (1300, -380), (1700, -380), (1300, -100), (1760, -100), angle=90)
things(DEMON, (1500, -160), (1600, -300), (1300, 60), angle=90)
things(IMP, (1440, 90), (1504, 50), (1728, -224), angle=180)               # on the crates
things(SERGEANT, (1700, 80), (1800, 20), angle=180)
things(SOUL, (1500, -100), (1700, -20), angle=90)
things(LODGER, (1400, -120), args=(300,))
things(TORCH_G, (1480, -424), (1592, -424))
things(CANDLE, (1240, -424), (1832, -424), (1240, 120), (1832, 120))
things(MEDIKIT, (1820, 110), (1250, -330))
things(SHELLBOX, (1240, 60))
# the boiler room: do not open this door
things(MANCUBUS, (2100, -256), angle=180)
things(KNIGHT, (1980, -340), (1980, -170), angle=180)
things(SPHERE, (2160, -360))
things(ROCKETBOX, (2160, -160), (2120, -160))
# the west wing: antiquities
things(ZOMBIE, (-600, 900), (-320, 1100), angle=0)
things(IMP, (-680, 1100), (-400, 900), (-680, 1200), (-400, 1560), angle=0)
things(SERGEANT, (-640, 1400), (-420, 1240), angle=270)
things(DEMON, (-540, 1560), (-1000, 1280), (-820, 1520), angle=270)
things(CHAINGUNNER, (-1130, 1540), (-780, 1180), angle=270)
things(REVENANT, (-960, 1000), angle=0)
things(KNIGHT, (-1100, 1060), angle=0)
things(PAIN, (-960, 1500), angle=270)
things(TECHLAMP, (-696, 872), (-296, 872), (-1176, 1576), (-760, 1576))
things(SHELLS, (-560, 1180), (-1160, 1180))
things(MEDIKIT, (-1170, 880), (-1100, 1570))
things(STIM, (-380, 1180), (-760, 870))
things(AMMOBOX, (-760, 1100))
# the office: the director, working late, and deaf to the wing
things(BARON, (-560, 1840), angle=270, ambush=True)
things(KNIGHT, (-680, 1680), angle=270, ambush=True)
things(TECHLAMP, (-696, 1880), (-376, 1880))
things(MEDIKIT, (-380, 1860))
# the strongroom
things(SPECTRE, (-660, 2100), (-420, 2140), angle=270)
things(TORCH_B, (-592, 2152), (-480, 2152))
things(CELLS, (-690, 1950))
# the east wing: paintings
things(ZOMBIE, (1040, 1040), (1360, 1040), (1040, 1460), angle=270)
things(IMP, (1380, 1340), (1010, 1300), (1200, 1480), (1380, 1500), (1480, 1820), (1840, 1460), angle=270)
things(SERGEANT, (1200, 1800), (1500, 1340), (1840, 1040), angle=270)
things(DEMON, (1200, 1300), (1660, 1500), angle=270)
things(SPECTRE, (1500, 1180), (1820, 1180), angle=180)
things(CHAINGUNNER, (1820, 1340), (1000, 1820), angle=180)
things(REVENANT, (1660, 1740), angle=270)
things(ARACHNO, (1660, 1280), angle=180)
things(CACO, (1200, 1640), angle=270, ambush=True)
things(TECHLAMP, (1000, 1368), (1400, 1000), (1464, 1432), (1864, 1368))
things(TORCH_B, (1864, 1540), (1864, 1660))
things(SHELLBOX, (1400, 1832))
things(MEDIKIT, (1464, 1000), (1000, 1432))
things(STIM, (1864, 1832), (1400, 1368))
things(ROCKETS, (1660, 1184), (1700, 1184))
# the archive
things(REVENANT, (1200, 2160), angle=270)
things(IMP, (1050, 1930), (1350, 1930), angle=270)
things(CANDELABRA, (1000, 1896), (1400, 1896))
things(SUPER, (1200, 2060))
things(SHELLBOX, (1160, 2180))
things(MEDIKIT, (1240, 2180))

# --- ambushes: what taking a key brings (ajarmap.ambush) ----------------------
# key 1, at the north end of the upper gallery: the whole gallery, behind you
ajarmap.ambush(m, 1, REVENANT, (-160, 1250), angle=90)
ajarmap.ambush(m, 1, IMP, (-200, 1420), (-120, 1560), angle=90)
# key 2, in the cellar: out of the dark
ajarmap.ambush(m, 2, SPECTRE, (1650, -360), (1500, -340), (1760, -130), angle=0)
# key 4, on the mezzanine: up from the great hall
ajarmap.ambush(m, 4, CACO, (-150, 620), (200, 600), angle=180)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "hall" is the lobby, the great hall, the cloakroom, the gift shop, the cafe
# and the court, and also the grotto and the shed, which open from inside.
# a is the cellar door's bolt, b the night room's. The boiler room is part
# of the cellar. The stockroom, PINK and the store are left out: nothing
# there leaves, and nothing else needs it.
PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("upper", "hall"), ("upper", "terrace"), ("roof", "hall"), ("roof", "terrace"),
          ("mezzanine", "hall"), ("terrace", "hall"),
          ("hall", "terrace", "", "squeeze"),                                    # the gap by the gatepost
          ("hall", "west", "1"), ("west", "hall", "1"),
          ("hall", "east", "2"), ("east", "hall", "2"),
          ("east", "archive", "23"), ("archive", "east", "23"),
          ("west", "office", "34"), ("office", "west", "34"),
          ("office", "strongroom", "", "squeeze"), ("strongroom", "office", "", "squeeze"),
          ("cellar", "hall", "a"), ("hall", "cellar", "a"),
          ("night", "terrace", "b"), ("terrace", "night", "b")],
    keys={"1": "upper", "2": "cellar", "3": "roof", "4": "mezzanine", "a": "cellar", "b": "night"},
    auto="ab",
    frames={101: "hall", 102: "hall", 103: "west", 104: "cellar", 105: "strongroom", ajarmap.HOME: "night"},
    doors={
        RED: dict(home="upper", lean="hall"),
        GREEN: dict(home="cellar", lean="hall"),
        YELLOW: dict(home="roof", lean="west"),
        VIOLET: dict(home="mezzanine", lean="east"),
        BLUE: dict(home="night", lean="strongroom"),
    },
    pool=["hall", "cellar"],               # the grotto; the boiler room
)
