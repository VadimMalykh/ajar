"""Act 1, level 8: "Closing Time" (MAP08).

A department store after the doors are locked. One new thing (Vadim's idea,
2026-11-15): the way out is behind a rolling shutter that a lever sends up
for eight seconds. The lever is in the caretaker's office, the shutter is
across the loading dock, and nothing but a route of doors laid beforehand
gets a door from the one to the other in that time.

The night room has a grille across it (ajarmap.way_home, grille). BLUE's far
side is in its west half, the brass frame in its east half, and only empty
hands pass the grille. The shutter is the only way into the frame's half with
anything in hand: so BLUE has to be carried under it.

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


def low(floor=0):
    """A porch: doors and frames in tall rooms and under the sky stand under one."""
    return dict(ceil=floor + 128, ctex="AJBOARD")


def rail(*runs):
    for a, b in runs:
        m.cut(a, b)
        m.line(a, b, **RAIL)


def bars(a, b, out, floor, thick=16):
    """A barred opening in a wall: to look and shoot through."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall="AJBRICK",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)


def hall(box, cases, **k):
    """A department: 160 high, with counters."""
    ajarmap.fitted(m, box, [(c, CASE) for c in cases], **dict(dict(ceil=160, light=175), **k))


# === the arcade, the lobby =======================================================
# the arcade: start here. The shop window is behind glass, the kiosk behind bars
ajarmap.fitted(m, (-704, -704, 704, -448), [
    ((-64, -704, 64, -448), PATH),
    ((-64, -512, 64, -448), low()),                                          # before the front door
    ((-704, -688, -640, -496), low()),                                       # before the kiosk
    ((384, -512, 512, -448), low()),                                         # before the shop window
    ((-320, -672, -192, -640), SEAT), ((192, -672, 320, -640), SEAT),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
# the kiosk (secret), seen through bars: shoot its bell
m.sector(rect(-976, -688, -720, -496), ceil=112, light=170, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (-704, -672), (-704, -608), (-1, 0), 0, KIOSK)
bars((-704, -576), (-704, -512), (-1, 0), 0)
m.cut((-976, -576), (-976, -512))
m.line((-976, -576), (-976, -512), special=11, args=(KIOSK, 32), impact=True, mid="AJTARG", exact=True)

# the lobby: RED, a frame, the cash office's two locks, the way into the atrium
ajarmap.fitted(m, (-256, -432, 256, 0), [
    ((-64, -432, 64, 0), PATH),
    ((96, -320, 224, -256), CASE),                                           # the enquiry desk
    ((-224, -112, -96, -48), SEAT),
], floor=0, ceil=192, light=185, wall="AJBRICK", ftex="AJFLOOR")
ajarmap.roomdoor(m, (-32, -448), (32, -448), (0, 1), 0)
recess((256, -128), (256, -64), (1, 0), 0, 101, 201)                         # the lobby's frame
m.sector(rect(-96, 0, 96, 16), ceil=160, light=185, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
# the shop window (secret): bolted inside, opened by the cash office's lever, and
# one of the places a Stray door opens onto
m.sector(rect(272, -432, 336, -272), ceil=112, light=190, color=ROSE, wall="AJSAFE")
m.sector(rect(336, -432, 560, -272), ceil=112, light=190, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (256, -400), (256, -336), (1, 0), 0, WINDOW, line_id=305)
ajarmap.unbolt(m, (336, -432), (336, -272), WINDOW)
bars((416, -448), (480, -448), (0, 1), 0)
ajarmap.stray_place(m, 1, (432, -272), (496, -272), (0, 1), 0, color=ROSE)
# the cash office: two locks. BLUE, and the lever of the shop window
ajarmap.fitted(m, (-592, -432, -272, -112), [
    ((-464, -304, -400, -240), CASE),                                        # the safe
    ((-592, -176, -528, -112), SEAT),
], floor=0, ceil=128, light=170, color=PLUM)
ajarmap.roomdoor(m, (-256, -304), (-256, -240), (-1, 0), 0, keys="34", line_id=303)
m.cut((-592, -304), (-592, -240))
m.line((-592, -304), (-592, -240), special=11, args=(WINDOW, 32), playeruse=True, mid="AJLEVR", exact=True,
       id=308)

# === the atrium, under its gallery ===============================================
GAL = dict(floor=UP, ftex="AJSTEEL", side="AJSTEEL")
ajarmap.fitted(m, (-512, 16, 512, 1040), [
    ((-64, 16, 64, 1040), PATH),
    ((-192, 336, 192, 720), dict(ctex="F_SKY1")),                            # the lantern, open to the stars
    ((-512, 32, -448, 128), low()),                                          # before the west wing's door
    ((448, 32, 512, 128), low()),                                            # before the east wing's
    ((448, 896, 512, 992), low()),                                           # before the goods passage's
    ((-512, 144, -384, 1040), GAL),
    ((-512, 624, -448, 752), dict(GAL, **low(UP))),                          # before RED's far side
    ((-64, 464, 64, 592), dict(floor=32, ftex="AJWATER", side="AJTRIM")),    # the fountain
    ((-256, 208, -128, 272), CASE), ((128, 208, 256, 272), CASE),            # counters
    ((-256, 784, -128, 848), CASE), ((128, 784, 256, 848), CASE),
    ((288, 464, 352, 592), SEAT),
], floor=0, ceil=448, light=180, color=SKY, wall="AJBRICK", ftex="AJFLOOR")
recess((-512, 656), (-512, 720), (-1, 0), UP, far_id(RED), 101, far_colour=RED, color=SKY)
rail(((-512, 144), (-384, 144)), ((-384, 144), (-384, 400)), ((-384, 464), (-384, 1040)))   # a gap over the atrium

# === the door showroom, the caretaker's office over it ============================
# The stairs up to the office end at a gatepost no door fits past. Off the
# balcony there is a gap in the rail: down is the only way with a door
BAL = dict(floor=UP, ftex="AJBOARD", side="AJWOOD")
ajarmap.fitted(m, (-512, 1056, 384, 1440), [
    ((-160 + 32 * i, 1056, -128 + 32 * i, 1120), dict(floor=20 * (i + 1), ftex="AJARCHF", side="AJTRIM"))
    for i in range(8)] + [
    ((128, 1056, 384, 1440), BAL),
    ((96, 1056, 128, 1120), dict(floor=UP, ftex="AJTRIMF", side="AJTRIM")),
    ((96, 1104, 128, 1120), dict(floor=UP + 56, ftex="AJTRIMF", side="AJTRIM")),
] + [((-352 + 96 * k, 1184, -336 + 96 * k, 1248), dict(WOOD, floor=96)) for k in range(4)],   # doors, on show
    floor=0, ceil=320, light=180, color=WARM, wall="AJBRICK", ftex="AJFLOOR")
m.line((128, 1056), (128, 1104), id=ajarmap.SQUEEZE, blockmonsters=True)
rail(((128, 1120), (128, 1280)), ((128, 1344), (128, 1440)))                 # a gap to jump down by
recess((-64, 1440), (0, 1440), (0, 1), 0, 106, 201, color=WARM)              # the showroom's two frames
recess((-192, 1440), (-128, 1440), (0, 1), 0, 107, 201, color=WARM)
recess((224, 1440), (288, 1440), (0, 1), UP, far_id(YELLOW), 101, far_colour=YELLOW, color=WARM)
ajarmap.lever(m, (384, 1248), (384, 1312), SECONDS, line_id=309)
ajarmap.squeeze(m, (-312, 1040), (-264, 1040), (0, 1), 0)                    # the turnstile, from the atrium
ajarmap.opening(m, (-480, 1040), (-416, 1040), (0, 1), UP)                   # the hole from the gallery

# === the loading dock, the night room behind its shutter ==========================
ajarmap.fitted(m, (-512, 1520, 384, 1840), [
    ((-320, 1520, -192, 1584), low()),                                       # before VIOLET's far side
    ((-320, 1776, -192, 1840), low()),                                       # before the shutter
    ((-480, 1776, -352, 1840), low()),                                       # before the night room's door
    ((0, 1616, 128, 1744), dict(WOOD, floor=48)),                            # crates
    ((192, 1552, 256, 1616), dict(WOOD, floor=48)),
], floor=0, light=NIGHT, ftex="AJARCHF", **OPEN)
recess((-288, 1520), (-224, 1520), (0, -1), 0, far_id(VIOLET), 101, far_colour=VIOLET)
for a, b in (((-320, 1776), (-192, 1776)), ((-192, 1776), (-192, 1840)), ((-320, 1776), (-320, 1840))):    # nothing but you stands under the shutter
    m.line(a, b, blockmonsters=True)
ajarmap.squeeze(m, (-440, 1440), (-392, 1440), (0, 1), 0, thick=80)          # the hatch, from the showroom
bars((32, 1440), (96, 1440), (0, 1), 0, thick=80)                            # the showroom's window on the dock
bars((304, 1440), (368, 1440), (0, 1), UP, thick=80)                         # and the office's
ajarmap.way_home(m, NX, NY, BLUE, grille=True)
m.sector(rect(-288, 1856, -224, 1936), ceil=96, light=160, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
ajarmap.shutter(m, (-288, 1840), (-224, 1840), (0, 1), 0, line_id=310)
ajarmap.bolted(m, (-448, 1840), (-384, 1840), (0, 1), 0, NIGHT_BOLT, thick=96, line_id=304)
ajarmap.unbolt(m, (NX, NY + 96), (NX + 320, NY + 96), NIGHT_BOLT)
ajarmap.unbolt(m, (-288, 1936), (-224, 1936), NIGHT_BOLT)

# === the stockroom under the goods passage ========================================
# a chute down from the dock; stairs up to the passage, and two doors on the way
ajarmap.fitted(m, (400, 1520, 1184, 1968), [
    ((528, 1584, 656, 1712), dict(WOOD, floor=PIT + 48)),                    # crates, clear of the chute
    ((848, 1616, 912, 1744), dict(WOOD, floor=PIT + 48)),
    ((944, 1840, 1072, 1904), dict(WOOD, floor=PIT + 96)),
], floor=PIT, ceil=128, light=140, wall="AJBRICK", ftex="AJPIT")
ajarmap.opening(m, (384, 1744), (384, 1808), (1, 0), 0)                      # the chute
recess((736, 1968), (800, 1968), (0, 1), PIT, 103, 201)                      # the stockroom's frame
ajarmap.stairs(m, (1056, 1520), (1120, 1520), (0, -1), PIT, 128, ceil=128, light=150, wall="AJBRICK",
               ftex="AJBOARD")
m.sector(rect(1056, 1120, 1120, 1264), ceil=128, light=150, wall="AJBRICK", ftex="AJBOARD")
m.sector(rect(1200, 1680, 1344, 1808), floor=PIT, ceil=PIT + 96, light=120, wall="AJSAFE", ftex="AJPIT",
         special=1024)
ajarmap.squeeze(m, (1184, 1720), (1184, 1768), (1, 0), PIT)
ajarmap.fitted(m, (528, 896, 1184, 1104), [
    ((704, 896, 832, 944), dict(WOOD, floor=48)),
    ((960, 1040, 1024, 1104), dict(WOOD, floor=48)),
], floor=0, ceil=160, light=165, wall="AJBRICK", ftex="AJBOARD")
ajarmap.roomdoor(m, (512, 912), (512, 976), (1, 0), 0)
ajarmap.roomdoor(m, (1056, 1120), (1120, 1120), (0, -1), 0, line_id=307)
# the boiler room: bolted inside, and one of the places a Stray door opens onto
m.sector(rect(608, 1120, 928, 1184), ceil=128, light=120, wall="AJSAFE", ftex="AJPIT")
m.sector(rect(608, 1184, 928, 1408), ceil=128, light=120, wall="AJSAFE", ftex="AJPIT")
ajarmap.bolted(m, (736, 1104), (800, 1104), (0, 1), 0, BOILER, line_id=306)
ajarmap.unbolt(m, (608, 1184), (928, 1184), BOILER)
ajarmap.stray_place(m, 0, (608, 1264), (608, 1328), (-1, 0), 0)

# === the west wing: one lock. Toys, haberdashery, furniture =======================
hall((-976, 16, -528, 336), [((-848, 144, -720, 208)), ((-656, 240, -592, 304))], color=GOLD)            # toys
hall((-1440, 16, -992, 336), [((-1376, 208, -1248, 272)), ((-1120, 208, -1056, 272))], color=LEAF)      # haberdashery
ajarmap.fitted(m, (-1440, -432, -992, 0), [                                                              # furniture
    ((-1408, -368, -1344, -240), SEAT), ((-1088, -368, -1024, -240), SEAT),
    ((-1280, -176, -1152, -112), dict(WOOD, floor=32)),
], floor=0, ceil=160, light=175, color=PLUM)
ajarmap.roomdoor(m, (-512, 48), (-512, 112), (-1, 0), 0, keys="1", line_id=301)
ajarmap.roomdoor(m, (-976, 144), (-976, 208), (-1, 0), 0)
ajarmap.roomdoor(m, (-1248, 16), (-1184, 16), (0, -1), 0)
recess((-1248, -432), (-1184, -432), (0, -1), 0, 102, 201, color=PLUM)       # the furniture department's frame

# === the roof: a hole lets down onto the gallery ==================================
ajarmap.fitted(m, (-1408, 416, -592, 1040), [
    ((-1056, 976, -928, 1040), low(ROOF)),                                   # before GREEN's far side
    ((-1216, 544, -1088, 672), dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")),   # skylights
    ((-896, 608, -768, 736), dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")),
    ((-1216, 800, -1088, 928), dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")),
], floor=ROOF, light=NIGHT + 10, ftex="AJSTEEL", **OPEN)
m.sector(rect(-592, 896, -528, 992), floor=ROOF, light=NIGHT + 10, ftex="AJSTEEL", **OPEN)
recess((-1024, 1040), (-960, 1040), (0, 1), ROOF, far_id(GREEN), 101, far_colour=GREEN)
ajarmap.opening(m, (-528, 912), (-528, 976), (1, 0), ROOF)

# === the east wing: one lock. China, linen, carpets ===============================
hall((528, 16, 976, 336), [((656, 144, 848, 176)), ((656, 240, 848, 272))], color=GOLD)                  # china
hall((528, 352, 976, 848), [((592, 480, 656, 608)), ((848, 480, 912, 608)), ((720, 720, 784, 784))],
     color=LEAF)                                                                                         # linen
hall((992, 16, 1440, 336), [((1120, 208, 1184, 272)), ((1312, 144, 1376, 208))], color=PLUM)            # carpets
ajarmap.roomdoor(m, (512, 48), (512, 112), (1, 0), 0, keys="2", line_id=302)
ajarmap.opening(m, (720, 336), (784, 336), (0, 1), 0)
ajarmap.roomdoor(m, (976, 144), (976, 208), (1, 0), 0)
# the lamp store (secret): a hole no door fits through, PINK, and a frame. Beyond
# its bars the strongroom (secret): PINK's far side. The strongroom's own door
# into the carpets is bolted inside
m.sector(rect(992, -208, 1200, 0), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.squeeze(m, (1064, 16), (1112, 16), (0, -1), 0)
m.sector(rect(1216, -64, 1440, 0), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(1216, -208, 1440, -64), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
bars((1200, -152), (1200, -88), (1, 0), 0)
recess((1064, -208), (1128, -208), (0, -1), 0, 109, 201, color=ROSE)
recess((1296, -208), (1360, -208), (0, -1), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)
ajarmap.bolted(m, (1296, 16), (1360, 16), (0, -1), 0, STRONG)
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
things(KNIGHT, (-350, -360), (-540, -360), angle=0, ambush=True)
things(TECHLAMP, (-296, -136), (-296, -408))
things(MEDIKIT, (-560, -220))
things(CELLS, (-330, -150))
# the atrium: late shoppers, round the fountain
things(IMP, (-300, 120), (300, 120), (-200, 400), (200, 400), (-300, 640), (300, 700), (-150, 940), (150, 940), angle=270)
things(DEMON, (-120, 340), (120, 340), (-250, 560), (230, 620), (0, 760), angle=270)
things(SERGEANT, (-330, 320), (330, 300), (-100, 880), (380, 860), angle=270)
things(ZOMBIE, (0, 160), (-200, 700), (400, 420), angle=270)
things(KNIGHT, (0, 660), (-280, 900), angle=270)
things(CACO, (-120, 520), (140, 520), angle=270, ambush=True)
things(REVENANT, (280, 960), angle=270)
things(SPECTRE, (-300, 480), (300, 240), (60, 880), angle=270)
things(CHAINGUNNER, (440, 200), (440, 700), angle=180)
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
things(CHAINGUNNER, (-448, 560), (-448, 880), angle=0)
things(IMP, (-448, 340), (-448, 1000), angle=0)
things(SERGEANT, (-420, 780), angle=0)
things(CHAINGUN, (-448, 480))
things(AMMOBOX, (-480, 180))
things(STIM, (-420, 960))
# the showroom: somebody lives in the frames
things(LODGER, (-320, 1320), args=(300,))
things(IMP, (-440, 1120), (-200, 1300), (70, 1160), (-360, 1400), angle=270)
things(DEMON, (-300, 1140), (-60, 1340), (40, 1400), angle=270)
things(SERGEANT, (-100, 1160), (-480, 1300), angle=270)
things(KNIGHT, (-240, 1380), angle=270)
things(SPECTRE, (-420, 1220), (20, 1220), angle=270)
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
things(DEMON, (-100, 1600), (200, 1700), (-400, 1680), angle=270)
things(SPECTRE, (-60, 1780), (280, 1800), (-460, 1600), angle=270)
things(IMP, (60, 1680), (-160, 1700), (340, 1560), angle=270)
things(KNIGHT, (160, 1790), angle=270)
things(CHAINGUNNER, (224, 1584), angle=180)
things(REVENANT, (-20, 1560), angle=270)
things(SERGEANT, (300, 1720), (-460, 1760), angle=270)
things(SOUL, (-100, 1720), (100, 1580), angle=270)
things(LAMP, (-340, 1548), (-170, 1548), (-340, 1812), (-170, 1812))
things(SHELLS, (300, 1640), (-480, 1740))
things(SHELLBOX, (-480, 1560))
things(STIM, (360, 1560))
things(MEDIKIT, (-140, 1548), (350, 1700))
# the night room: someone has been waiting, on BLUE's side of the grille
things(REVENANT, (NX + 80, NY + 200), angle=270)
things(KNIGHT, (NX + 90, NY + 40), (NX + 120, NY + 128), angle=270)
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
things(KNIGHT, (-1300, -300), (-1120, -300), angle=90)
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
things(CACO, (-1000, 700), (-800, 520), (-1300, 480), angle=0, ambush=True)
things(REVENANT, (-700, 980), angle=0)
things(SOUL, (-1100, 460), (-760, 800), (-1340, 1000), angle=0)
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
things(KNIGHT, (1240, 100), (1390, 250), angle=180)
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

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "store" is the arcade, the lobby, the atrium, the goods passage and the
# stockroom, and also the kiosk, the shop window and the boiler room, which
# open from inside. "office" is the balcony; "night" is the night room west of
# its grille (BLUE's far side) and "home" east of it (the brass frame). b is
# the night room's bolt, drawn from either half (c). The lamp store, the
# strongroom and PINK are left out: PINK never leaves, and nothing else needs
# it.
#
# The dash: a leg is how far it is, in map units, between two ends that can be
# run with a door in hand; an ordinary door on the way counts as a second of
# running (583). The limit is what a runner covers in the shutter's time less
# two seconds for the lever and the turns. Only the showroom's frames are
# within it.
RUN = 583
PUZZLE = dict(
    start="store", goal="exit", names=ajarmap.NAMES, complete=True,
    home_frame=ajarmap.HOME, home_door=BLUE,
    walk=[("gallery", "store"), ("gallery", "showroom"), ("roof", "gallery"),
          ("store", "showroom", "", "squeeze"), ("showroom", "store", "", "squeeze"),     # the turnstile
          ("showroom", "office", "", "squeeze"), ("office", "showroom"),                  # the gatepost; the gap
          ("showroom", "dock", "", "squeeze"), ("dock", "showroom", "", "squeeze"),       # the hatch
          ("dock", "store"),                                                              # the chute
          ("dock", "night", "b"), ("night", "dock", "b"), ("dock", "night", "c"), ("night", "dock", "c"),
          ("night", "home", "", "squeeze"), ("home", "night", "", "squeeze"),             # the grille
          ("home", "dock"),                                                               # the shutter, pushed
          ("store", "west", "1"), ("west", "store", "1"),
          ("store", "east", "2"), ("east", "store", "2"),
          ("store", "cash", "34"), ("cash", "store", "34")],
    keys={"1": "gallery", "2": "roof", "3": "east", "4": "office", "b": "night", "c": "home"},
    auto="bc",
    frames={101: "store", 103: "store", 102: "west", 106: "showroom", 107: "showroom",
            ajarmap.HOME: "home"},
    doors={
        RED: dict(home="gallery", lean="store"),
        GREEN: dict(home="roof", lean="west"),
        YELLOW: dict(home="office", lean="east"),
        VIOLET: dict(home="dock", lean="dock"),
        BLUE: dict(home="night", lean="cash"),
    },
    pool=["store"],                        # the boiler room; the shop window
    dash=dict(at="office", to="home", limit=(SECONDS - 2) * RUN, legs={
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
