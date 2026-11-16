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
loft, which is the north end of the supervisor's gallery (RED's far side;
the roof, GREEN's, lets down onto it). Its way in from the switchroom is a
hatch; a chute lets a door out again, into the battery room.

Places. The forecourt (start), the call office, the switchroom, the cable
passage and the battery room under it are one place to walk about in. The
supervisor's gallery over the switchroom's west side and the cable loft
north of it (RED's far side; key 1). The roof (GREEN's; key 2). The
monitor's balcony over the switchroom's north-east corner (YELLOW's; key 4).
West wing (key 1): canteen, cloakroom, rest room (GREEN, a frame). East wing
(key 2): apparatus room (key 3), relay room (YELLOW, a frame), and off the
apparatus room the test room. The manager's office (keys 3 and 4): BLUE.

Secrets: the kiosk in the forecourt (shoot its bell through the bars, or a
Stray door); the stationery store behind the relay room (a squeeze; PINK and
a frame) and beyond its bars the strongroom (PINK's far side); an alcove off
the battery room.
"""
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
NX, NY = -1008, -560                                  # the night room's south-west corner
NIGHT = 150                                           # light under the sky


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
    """A room of the wings: 160 high, with furniture."""
    ajarmap.fitted(m, box, cases, **dict(dict(ceil=160, light=175), **k))


# === the forecourt, the line over it ==============================================
# start here: nobody about. The kiosk is behind bars; high in the north wall a
# hole shows a starry ceiling
ajarmap.fitted(m, (-1056, -832, 512, -576), [
    ((-64, -832, 64, -576), PATH),
    ((-64, -640, 64, -576), low()),                                          # before the front door
    ((448, -816, 512, -624), low()),                                         # before the kiosk
    ((-320, -800, -192, -768), SEAT), ((192, -800, 320, -768), SEAT),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
# the line: BLUE's far side at its west end, VIOLET's at its east end, and a
# hole to drop out by
ajarmap.way_through(m, NX, NY, BLUE, VIOLET, floor=LINE)
m.sector(rect(NX + 128, NY - 16, NX + 192, NY), floor=LINE, ceil=LINE + 96, light=150, wall="AJBRICK",
         ftex="AJTRIMF", ctex="AJTRIMF")
# the kiosk (secret), seen through bars: shoot its bell. One of the places a
# Stray door opens onto
m.sector(rect(528, -816, 592, -624), ceil=112, light=170, color=ROSE, wall="AJSAFE")
m.sector(rect(592, -816, 784, -624), ceil=112, light=170, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (512, -800), (512, -736), (1, 0), 0, KIOSK, line_id=305)
ajarmap.unbolt(m, (592, -816), (592, -624), KIOSK)
bars((512, -704), (512, -640), (1, 0), 0)
m.cut((784, -704), (784, -640))
m.line((784, -704), (784, -640), special=11, args=(KIOSK, 32), impact=True, mid="AJTARG", exact=True)
ajarmap.stray_place(m, 1, (656, -624), (720, -624), (0, 1), 0, color=ROSE)

# === the call office ==============================================================
# RED, a frame, booths, the manager's two locks, the way into the switchroom
ajarmap.fitted(m, (-256, -560, 256, -128), [
    ((-64, -560, 64, -128), PATH),
    ((192, -544, 256, -480), dict(WOOD, floor=128)), ((192, -448, 256, -384), dict(WOOD, floor=128)),   # booths
    ((96, -544, 160, -480), dict(WOOD, floor=128)),
    ((-224, -240, -96, -176), CASE),                                         # the counter
    ((-240, -544, -112, -512), SEAT),
], floor=0, ceil=192, light=185, wall="AJBRICK", ftex="AJFLOOR")
ajarmap.roomdoor(m, (-32, -576), (32, -576), (0, 1), 0)
recess((256, -256), (256, -192), (1, 0), 0, 101, 201)                        # the call office's frame
m.sector(rect(-96, -128, 96, -112), ceil=160, light=185, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
# the manager's office: two locks. BLUE
ajarmap.fitted(m, (-592, -560, -272, -240), [
    ((-464, -432, -400, -368), CASE),                                        # the desk
    ((-592, -304, -528, -240), SEAT),
], floor=0, ceil=128, light=170, color=PLUM)
ajarmap.roomdoor(m, (-256, -432), (-256, -368), (-1, 0), 0, keys="34", line_id=303)

# === the switchroom, under its gallery and its balcony =============================
GAL = dict(floor=UP, ftex="AJSTEEL", side="AJSTEEL")
BAL = dict(floor=UP, ftex="AJBOARD", side="AJWOOD")
ajarmap.fitted(m, (-512, -112, 512, 912), [
    ((-64, -112, 64, 912), PATH),
    ((-512, -96, -448, 0), low()),                                           # before the west wing's door
    ((448, -96, 512, 0), low()),                                             # before the east wing's
    ((448, 592, 512, 688), low()),                                           # before the cable passage's
    ((320, -112, 448, -48), low()),                                          # before the switchroom's frame
    ((-64, 848, 64, 912), low()),                                            # before the hatch to the trunk room
    ((-512, 16, -384, 912), GAL),
    ((-512, 496, -448, 624), dict(GAL, **low(UP))),                          # before RED's far side
    ((-512, 848, -384, 912), dict(GAL, **low(UP))),                          # before the way into the loft
    ((128, 784, 512, 912), BAL),
    ((256, 848, 384, 912), dict(BAL, **low(UP))),                            # before YELLOW's far side
    ((-320, 96, -288, 352), BOARD), ((-176, 96, -144, 352), BOARD),          # switchboards, in four ranks
    ((144, 96, 176, 352), BOARD), ((288, 96, 320, 352), BOARD),
    ((-320, 464, -288, 720), BOARD), ((-176, 464, -144, 720), BOARD),
    ((144, 464, 176, 656), BOARD), ((288, 464, 320, 656), BOARD),
    ((-256, 384, -192, 432), SEAT), ((192, 384, 256, 432), SEAT),
], floor=0, ceil=448, light=180, color=SKY, wall="AJBRICK", ftex="AJFLOOR")
recess((-512, 528), (-512, 592), (-1, 0), UP, far_id(RED), 101, far_colour=RED, color=SKY)
recess((288, 912), (352, 912), (0, 1), UP, far_id(YELLOW), 101, far_colour=YELLOW, color=SKY)
recess((352, -112), (416, -112), (0, -1), 0, 102, 201, color=SKY)            # the switchroom's frame
rail(((-512, 16), (-384, 16)), ((-384, 16), (-384, 272)), ((-384, 336), (-384, 912)))    # a gap over the switchroom
rail(((128, 784), (128, 912)), ((128, 784), (224, 784)), ((288, 784), (512, 784)))       # and one in the balcony's

# === the cable loft, the trunk room under its edge =================================
# The loft is the gallery's north end. From it a hole lets down into the trunk
# room: the only way in there with a door
LOFT = dict(floor=UP, ceil=320, light=150, wall="AJBRICK", ftex="AJBOARD")
ajarmap.opening(m, (-480, 912), (-416, 912), (0, 1), UP)
m.sector(rect(-512, 928, -384, 1216), **LOFT)
ajarmap.fitted(m, (-512, 1216, 256, 1440), [
    ((-256, 1312, -128, 1376), dict(WOOD, floor=UP + 48)),                   # cable drums
    ((64, 1280, 128, 1408), dict(WOOD, floor=UP + 48)),
], **LOFT)
m.sector(rect(-32, 1200, 32, 1216), floor=UP, ceil=UP + 96, light=150, wall="AJTRIM", ftex="AJTRIMF",
         ctex="AJTRIMF")
# the trunk room: two brass frames, and nothing else to hang a door in
ajarmap.fitted(m, (-256, 944, 256, 1200), [
    ((-256, 1040, 256, 1104), ajarmap.RUNNER),
    ((-64, 1104, 64, 1200), dict(ceil=288)),                                 # under the hole
    ((-192, 976, -64, 1008), BOARD), ((64, 976, 192, 1008), BOARD),          # the trunk positions
], rug="AJXR2", floor=0, ceil=160, light=170, color=GOLD, wall="AJBRICK", ftex="AJFLOOR")
ajarmap.brass_pair(m, (-256, 1040), (-256, 1104), (256, 1040), (256, 1104), 0, BLUE, VIOLET)
ajarmap.squeeze(m, (-24, 912), (24, 912), (0, 1), 0, thick=32)               # the hatch, from the switchroom
m.sector(rect(256, 1136, 272, 1200), ceil=96, light=150, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")   # the chute

# === the battery room, the cable passage ==========================================
# a chute down from the trunk room; stairs up to the passage, and two doors on the way
ajarmap.fitted(m, (272, 1120, 1184, 1568), [
    ((400, 1312, 528, 1504), dict(floor=PIT + 40, ftex="AJWATER", side="AJSTEEL")),      # cells
    ((624, 1312, 752, 1504), dict(floor=PIT + 40, ftex="AJWATER", side="AJSTEEL")),
    ((848, 1184, 976, 1312), dict(floor=PIT + 40, ftex="AJWATER", side="AJSTEEL")),
], floor=PIT, ceil=128, light=140, wall="AJBRICK", ftex="AJPIT")
recess((880, 1568), (944, 1568), (0, 1), PIT, 105, 201)                      # the battery room's frame
ajarmap.stairs(m, (1056, 1120), (1120, 1120), (0, -1), PIT, 128, ceil=128, light=150, wall="AJBRICK",
               ftex="AJBOARD")
m.sector(rect(1056, 720, 1120, 864), ceil=128, light=150, wall="AJBRICK", ftex="AJBOARD")
m.sector(rect(1200, 1280, 1344, 1408), floor=PIT, ceil=PIT + 96, light=120, wall="AJSAFE", ftex="AJPIT",
         special=1024)
ajarmap.squeeze(m, (1184, 1320), (1184, 1368), (1, 0), PIT)
ajarmap.fitted(m, (528, 576, 1184, 704), [
    ((704, 576, 832, 608), dict(WOOD, floor=48)),
    ((928, 672, 992, 704), dict(WOOD, floor=48)),
], floor=0, ceil=160, light=165, wall="AJBRICK", ftex="AJBOARD")
ajarmap.roomdoor(m, (512, 608), (512, 672), (1, 0), 0)
ajarmap.roomdoor(m, (1056, 720), (1120, 720), (0, -1), 0, line_id=307)
# the generator room: bolted inside, and one of the places a Stray door opens onto
m.sector(rect(608, 720, 928, 784), ceil=128, light=120, wall="AJSAFE", ftex="AJPIT")
m.sector(rect(608, 784, 928, 1088), ceil=128, light=120, wall="AJSAFE", ftex="AJPIT")
ajarmap.bolted(m, (736, 704), (800, 704), (0, 1), 0, GENERATOR, line_id=306)
ajarmap.unbolt(m, (608, 784), (928, 784), GENERATOR)
ajarmap.stray_place(m, 0, (608, 880), (608, 944), (-1, 0), 0)

# === the west wing: one lock. Canteen, cloakroom, rest room =======================
hall((-976, -112, -528, 208), [((-848, 16, -720, 80), CASE), ((-656, 112, -592, 176), CASE)], color=GOLD)      # canteen
hall((-1440, -112, -992, 208), [((-1376, 80, -1248, 144), WOOD | dict(floor=96)),
                                ((-1120, 80, -1056, 144), WOOD | dict(floor=96))], color=LEAF)                   # cloakroom
hall((-1440, 224, -992, 656), [                                                                                  # rest room
    ((-1408, 544, -1344, 624), SEAT), ((-1088, 288, -1024, 416), SEAT),
    ((-1280, 480, -1152, 544), dict(WOOD, floor=32)),
], color=PLUM)
ajarmap.roomdoor(m, (-512, -80), (-512, -16), (-1, 0), 0, keys="1", line_id=301)
ajarmap.roomdoor(m, (-976, 16), (-976, 80), (-1, 0), 0)
ajarmap.roomdoor(m, (-1248, 208), (-1184, 208), (0, 1), 0)
recess((-1440, 400), (-1440, 464), (-1, 0), 0, 103, 201, color=PLUM)         # the rest room's frame

# === the roof: a hole lets down onto the gallery ==================================
ajarmap.fitted(m, (-1408, 672, -592, 1296), [
    ((-1056, 1232, -928, 1296), low(ROOF)),                                  # before GREEN's far side
    ((-1216, 800, -1088, 928), dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")),   # skylights
    ((-896, 864, -768, 992), dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")),
    ((-1216, 1056, -1088, 1184), dict(floor=ROOF + 40, ftex="AJSTEEL", side="AJSTEEL")),
], floor=ROOF, light=NIGHT + 10, ftex="AJSTEEL", **OPEN)
m.sector(rect(-592, 768, -528, 864), floor=ROOF, light=NIGHT + 10, ftex="AJSTEEL", **OPEN)
recess((-1024, 1296), (-960, 1296), (0, 1), ROOF, far_id(GREEN), 101, far_colour=GREEN)
ajarmap.opening(m, (-528, 784), (-528, 848), (1, 0), ROOF)

# === the east wing: one lock. Apparatus room, relay room; the test room ===========
ajarmap.fitted(m, (528, -112, 1104, 560), [
    ((592, 16, 912, 48), RACK), ((592, 144, 912, 176), RACK),
    ((592, 272, 912, 304), RACK), ((592, 400, 912, 432), RACK),
    ((976, 208, 1040, 464), RACK),
], floor=0, ceil=192, light=165, color=LEAF, wall="AJBRICK", ftex="AJFLOOR")
hall((1120, -112, 1568, 208), [((1248, 80, 1312, 144), CASE), ((1440, 16, 1504, 80), CASE)], color=PLUM)        # relay room
ajarmap.roomdoor(m, (512, -80), (512, -16), (1, 0), 0, keys="2", line_id=302)
ajarmap.roomdoor(m, (1104, 16), (1104, 80), (1, 0), 0)
recess((1312, -112), (1376, -112), (0, -1), 0, 106, 201, color=PLUM)         # the relay room's frame
# the test room: a hatch no door fits through, VIOLET, and a frame
ajarmap.fitted(m, (640, -384, 960, -128), [
    ((672, -352, 736, -224), CASE),                                          # the test desk
], floor=0, ceil=128, light=160, color=GOLD)
ajarmap.squeeze(m, (792, -112), (840, -112), (0, -1), 0)
recess((768, -384), (832, -384), (0, -1), 0, 104, 201, color=GOLD)           # the test room's frame
# the stationery store (secret): a hole no door fits through, PINK, and a frame.
# Beyond its bars the strongroom (secret): PINK's far side. The strongroom's own
# door into the relay room is bolted inside
m.sector(rect(1184, 224, 1392, 432), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.squeeze(m, (1256, 208), (1304, 208), (0, 1), 0)
m.sector(rect(1408, 224, 1632, 288), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(1408, 288, 1632, 432), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
bars((1392, 304), (1392, 368), (1, 0), 0)
recess((1256, 432), (1320, 432), (0, 1), 0, 109, 201, color=ROSE)
recess((1488, 432), (1552, 432), (0, 1), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)
ajarmap.bolted(m, (1456, 208), (1520, 208), (0, 1), 0, STRONG)
ajarmap.unbolt(m, (1408, 288), (1632, 288), STRONG)

# --- doors and keys ----------------------------------------------------------
m.thing(0, -768, 1, angle=90)                                             # player start, in the forecourt
ajarmap.door(m, RED, -236, -150, angle=0)                                 # leaning in the call office
ajarmap.door(m, GREEN, -1420, 244, angle=0)                               # leaning in the rest room
ajarmap.door(m, YELLOW, 1548, 188, angle=180)                             # leaning in the relay room
ajarmap.door(m, VIOLET, 940, -148, angle=180)                             # leaning in the test room
ajarmap.door(m, BLUE, -572, -540, angle=0)                                # leaning in the manager's office
ajarmap.door(m, PINK, 1204, 244, angle=0)                                 # leaning in the stationery store
ajarmap.stray(m, 492, 20, angle=180)                                      # Stray doors: in the switchroom
ajarmap.stray(m, -1388, 1276, angle=0)                                    # on the roof
ajarmap.stray(m, 1084, 540, angle=180)                                    # in the apparatus room
ajarmap.stray(m, 292, 1548, angle=0)                                      # in the battery room
ajarmap.stray(m, -492, 1420, angle=0)                                     # in the cable loft
ajarmap.key(m, 1, -448, 112)                                              # south end of the gallery
ajarmap.key(m, 2, -1340, 740)                                             # the far corner of the roof
ajarmap.key(m, 3, 1072, -80)                                              # behind the racks of the apparatus room
ajarmap.key(m, 4, 480, 880)                                               # the monitor's balcony

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACHNO, PAIN = 65, 69, 3003, 66, 3006, 3005, 67, 68, 71
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, BARREL = 24, 2035


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the forecourt: lamps and nobody
things(LAMP, (-96, -608), (96, -608), (-600, -608), (-1000, -800), (420, -800))
things(BONUS, (-256, -700), (-200, -700), (200, -700), (256, -700))
# the kiosk
things(PLASMA, (690, -720))
things(CELLS, (740, -780), (740, -740))
things(MEGA, (620, -660))
# the line: nobody. It can be seen into from the forecourt, and the start is quiet
# the call office: the night staff
things(ZOMBIE, (-160, -330), (160, -290), (0, -190), angle=270)
things(IMP, (-200, -460), (130, -400), angle=270)
things(SHOTGUN, (0, -390))
things(SHELLS, (-40, -350), (40, -350))
things(STIM, (-230, -150), (230, -150))
things(TECHLAMP, (-232, -480), (232, -152))
# the manager's office: working late, and deaf to the call office
things(BARON, (-430, -300), angle=0, ambush=True)
things(KNIGHT, (-330, -520), (-540, -480), angle=0, ambush=True)
things(TECHLAMP, (-296, -264), (-296, -536))
things(MEDIKIT, (-560, -340))
things(CELLS, (-330, -280))
# the switchroom: the night shift, between the boards
things(IMP, (-240, -8), (240, -8), (-232, 272), (232, 272), (-240, 512), (240, 572), (-100, 780), (100, 720), angle=270)
things(DEMON, (-100, 212), (100, 212), (-232, 600), (232, 492), (0, 632), angle=270)
things(SERGEANT, (-350, 40), (360, 40), (-100, 560), (380, 540), angle=270)
things(ZOMBIE, (0, 32), (-232, 160), (400, 292), angle=270)
things(KNIGHT, (0, 432), (-240, 780), angle=270)
things(CACO, (-100, 400), (100, 400), angle=270, ambush=True)
things(REVENANT, (60, 760), angle=270)
things(SPECTRE, (-232, 400), (232, 160), (-60, 700), angle=270)
things(CHAINGUNNER, (440, 200), (420, 720), angle=180)
things(TECHLAMP, (-360, -88), (488, 24), (-360, 888), (104, 888))
things(SHELLBOX, (-232, 64))
things(MEDIKIT, (232, 64), (-340, 760))
things(SHELLS, (-232, 740), (232, 700))
things(STIM, (-480, -88), (480, 560))
# the gallery: key 1, a chaingun, and those who watch from above
things(CHAINGUNNER, (-448, 432), (-448, 720), angle=0)
things(IMP, (-448, 212), (-448, 816), angle=0)
things(SERGEANT, (-420, 652), angle=0)
things(CHAINGUN, (-448, 352))
things(AMMOBOX, (-480, 52))
things(STIM, (-420, 760))
# the balcony: key 4, the monitor
things(CHAINGUNNER, (200, 860), angle=270)
things(IMP, (430, 820), angle=180)
things(MEDIKIT, (160, 880))
# the cable loft
things(IMP, (-448, 1000), (-448, 1150), (-300, 1260), (160, 1260), angle=270)
things(SERGEANT, (-200, 1400), (0, 1400), angle=270)
things(REVENANT, (200, 1400), angle=180)
things(SOUL, (-400, 1380), (-60, 1280), angle=270)
things(SHELLS, (-480, 1250), (220, 1250))
things(STIM, (-100, 1420))
things(TECHLAMP, (-490, 1236), (236, 1420))
# the trunk room: somebody lives in the frames
things(LODGER, (0, 1000), args=(300,))
things(DEMON, (-200, 1150), (200, 1150), angle=270)
things(KNIGHT, (-128, 1072), (128, 1072), angle=270)
things(IMP, (-220, 970), (220, 970), angle=270)
things(TORCH_B, (-232, 1176), (232, 968))
things(MEDIKIT, (-230, 1010))
things(SHELLS, (230, 1010))
# the battery room and its alcove
things(SPECTRE, (340, 1260), (580, 1400), (800, 1420), (1100, 1500), angle=180)
things(DEMON, (580, 1200), (820, 1520), (340, 1520), angle=180)
things(IMP, (464, 1408), (688, 1408), (912, 1248), angle=180)
things(SOUL, (560, 1530), (1040, 1300), angle=180)
things(SERGEANT, (1000, 1400), (700, 1240), angle=180)
things(TORCH_G, (296, 1144), (1160, 1544))
things(MEDIKIT, (300, 1540))
things(SHELLBOX, (1150, 1160))
things(ARMOR, (1280, 1344))
things(CELLS, (1310, 1300), (1310, 1388))
things(CANDLE, (1224, 1304), (1224, 1384))
# the cable passage
things(ZOMBIE, (640, 660), (900, 620), (1000, 640), angle=180)
things(IMP, (768, 660), (1140, 610), angle=180)
things(SERGEANT, (860, 640), (600, 610), angle=180)
things(DEMON, (700, 640), (1140, 650), angle=180)
things(TECHLAMP, (552, 680), (1160, 600))
things(STIM, (1160, 676))
things(CLIP, (560, 600), (600, 600))
# the generator room: do not open this door
things(MANCUBUS, (768, 960), angle=270)
things(KNIGHT, (660, 860), (880, 860), angle=270)
things(BERSERK, (640, 750))
things(ROCKETS, (880, 750), (840, 750))
# the west wing: canteen, cloakroom, rest room
things(ZOMBIE, (-600, -48), (-900, -48), (-700, 172), angle=0)
things(IMP, (-940, 172), (-560, 52), (-800, -68), (-640, -8), angle=0)
things(SERGEANT, (-780, 152), (-900, 120), angle=0)
things(SPECTRE, (-560, -68), (-940, -68), angle=0)
things(CACO, (-760, -28), angle=0, ambush=True)
things(DEMON, (-720, 130), (-860, -28), angle=0)
things(IMP, (-1400, -68), (-1040, -68), (-1200, 172), angle=0)
things(CHAINGUNNER, (-1400, 172), (-1020, 172), angle=0)
things(DEMON, (-1300, 12), (-1180, 40), angle=0)
things(REVENANT, (-1200, -28), angle=0)
things(PAIN, (-1200, 60), angle=0)
things(KNIGHT, (-1300, 340), (-1120, 520), angle=270)
things(BARON, (-1216, 400), angle=270)
things(IMP, (-1400, 280), (-1040, 620), (-1300, 620), angle=270)
things(SERGEANT, (-1040, 260), (-1216, 600), angle=270)
things(TECHLAMP, (-952, -88), (-552, 184), (-1416, 184), (-1016, -88), (-1016, 632), (-1416, 500))
things(SHELLS, (-560, 182), (-1410, 72))
things(MEDIKIT, (-950, 182), (-1020, 250))
things(STIM, (-1020, 72), (-1410, 630))
things(AMMOBOX, (-1100, 630))
things(ROCKETS, (-1216, 300), (-1250, 300))
# the roof
things(IMP, (-1360, 860), (-700, 740), (-1000, 740), (-660, 1060), angle=0)
things(SERGEANT, (-1300, 1160), (-800, 1160), angle=0)
things(CHAINGUNNER, (-1360, 1020), (-640, 940), angle=0)
things(CACO, (-1000, 960), (-800, 780), (-1300, 740), angle=0, ambush=True)
things(REVENANT, (-700, 1240), angle=0)
things(SOUL, (-1040, 720), (-720, 1040), (-1340, 1260), angle=0)
things(KNIGHT, (-840, 1240), angle=0)
things(SUPER, (-1000, 1040))
things(SHELLS, (-1000, 1010), (-1000, 1080))
things(MEDIKIT, (-1380, 1200))
things(ARMOR, (-630, 710))
things(LAMP, (-1070, 1206), (-914, 1206))
# the east wing: apparatus room, relay room
things(ZOMBIE, (560, 100), (620, -60), (560, 350), angle=180)
things(IMP, (760, 100), (940, 350), (560, 220), (760, 480), (1072, 520), angle=180)
things(SERGEANT, (940, 220), (760, 350), (600, 500), angle=180)
things(DEMON, (620, 230), (880, 100), (700, -60), angle=180)
things(SPECTRE, (940, 500), (800, 228), angle=180)
things(CHAINGUNNER, (1072, -30), (560, 520), angle=180)
things(ARACHNO, (990, 100), angle=180)
things(CACO, (752, 520), angle=180, ambush=True)
things(KNIGHT, (1240, -28), (1400, 152), angle=180)
things(REVENANT, (1160, 172), (1380, 172), angle=180)
things(IMP, (1160, -68), (1530, -28), angle=180)
things(SERGEANT, (1200, 40), angle=180)
things(DEMON, (1400, -40), (1530, 150), angle=180)
things(TECHLAMP, (552, -88), (1080, -88), (552, 536), (1144, 184), (1544, -88))
things(CANDELABRA, (1080, 536))
things(SHELLBOX, (560, -80))
things(MEDIKIT, (1072, 480), (1540, 150))
things(STIM, (940, -88), (1144, -88))
things(ROCKETS, (1250, -80), (1290, -80))
things(CELLS, (1000, 540))
# the test room: whoever was testing the line
things(KNIGHT, (880, -300), angle=90)
things(IMP, (700, -180), (920, -200), angle=90)
things(TECHLAMP, (664, -152), (936, -360))
things(STIM, (700, -356))
# the stationery store and the strongroom
things(CANDLE, (1208, 408), (1368, 248))
things(HELMET, (1360, 400))
things(LAUNCHER, (1520, 350))
things(ROCKETBOX, (1432, 400), (1608, 400))
things(MEGA, (1432, 250))
things(AMMOBOX, (1608, 250))

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "main" is the forecourt, the call office, the switchroom, the cable passage
# and the battery room, and also the kiosk and the generator room, which open
# from inside. "gallery" is the supervisor's gallery and the cable loft;
# "balcony" the monitor's; "east" the apparatus and relay rooms; "night" is the
# line. The stationery store, the strongroom and PINK are left out: PINK never
# leaves, and nothing else needs it.
PUZZLE = dict(
    start="main", goal="exit", names=ajarmap.NAMES, complete=True,
    home_chain=dict(frames=[ajarmap.HOME, ajarmap.HOME2], doors=[BLUE, VIOLET]),
    walk=[("gallery", "main"), ("gallery", "trunk"), ("roof", "gallery"),
          ("main", "trunk", "", "squeeze"), ("trunk", "main", "", "squeeze"),             # the hatch
          ("trunk", "main"),                                                              # the chute
          ("balcony", "main"),
          ("east", "test", "", "squeeze"), ("test", "east", "", "squeeze"),               # the test room's hatch
          ("night", "main"),                                                              # the hole over the forecourt
          ("main", "west", "1"), ("west", "main", "1"),
          ("main", "east", "2"), ("east", "main", "2"),
          ("main", "office", "34"), ("office", "main", "34")],
    keys={"1": "gallery", "2": "roof", "3": "east", "4": "balcony"},
    frames={101: "main", 102: "main", 105: "main", 103: "west", 106: "east", 104: "test",
            ajarmap.HOME: "trunk", ajarmap.HOME2: "trunk"},
    doors={
        RED: dict(home="gallery", lean="main"),
        GREEN: dict(home="roof", lean="west"),
        YELLOW: dict(home="balcony", lean="east"),
        BLUE: dict(home="night", lean="office"),
        VIOLET: dict(home="night", lean="test"),
    },
    pool=["main"],                         # the generator room; the kiosk
)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
