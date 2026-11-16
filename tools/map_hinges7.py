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
one place to walk about in. Up: the stacks (GREEN's far side; key 1), the
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
    """A room of a wing: 160 high, with benches of instruments."""
    ajarmap.fitted(m, box, [(c, CASE) for c in cases], **dict(dict(ceil=160, light=175), **k))


# === the way in: nobody about ====================================================
# the road: start here. The gate is bolted on the inside; beside it, bars to
# look through and an empty frame
ajarmap.fitted(m, (-384, -832, 384, -320), [
    ((-64, -832, 64, -320), PATH),
    ((-64, -384, 64, -320), low()),                                          # before the gate
    ((128, -384, 256, -320), low()),                                         # before the frame
    ((-320, -640, -256, -448), SEAT),                                        # a bench for those who wait
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
recess((160, -320), (224, -320), (0, 1), 0, 101, 201)                        # the frame by the gate
# the gate passage: RED's far side, three steps from that frame
ajarmap.fitted(m, (-128, -256, 128, 0), [
    ((-64, -256, 64, 0), PATH),
    ((-64, -256, 64, -192), low()),
    ((-128, -192, -64, -64), low()),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
recess((-128, -160), (-128, -96), (-1, 0), 0, far_id(RED), 101, far_colour=RED)
m.line((-128, -160), (-128, -96), special=11, args=(GATE, 32), playercross=True)   # coming in draws the bolt
# the forecourt
ajarmap.fitted(m, (-448, 0, 448, 512), [
    ((-64, 0, 64, 512), PATH),
    ((-96, 448, 96, 512), low()),                                            # before the front door
    ((-448, 192, -384, 320), low()),                                         # before the arch to the yard
    ((-32, 224, 32, 288), dict(floor=40, ftex="AJSTEEL", side="AJTRIM")),    # the sundial
    ((-288, 96, -160, 128), SEAT), ((160, 96, 288, 128), SEAT),
    ((-288, 384, -160, 416), SEAT), ((160, 384, 288, 416), SEAT),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
ajarmap.bolted(m, (-32, -320), (32, -320), (0, 1), 0, GATE, thick=64, line_id=311)
bars((64, -320), (128, -320), (0, 1), 0, thick=64)

# the hall: GREEN, a frame, and three doors
ajarmap.fitted(m, (-256, 528, 256, 912), [
    ((-64, 528, 64, 912), PATH),
    ((-224, 560, -160, 624), SEAT), ((-224, 816, -160, 880), SEAT),
    ((160, 816, 224, 880), CASE),                                            # a globe on its stand
], floor=0, ceil=256, light=185, wall="AJBRICK", ftex="AJFLOOR")
ajarmap.roomdoor(m, (-32, 512), (32, 512), (0, 1), 0)
recess((256, 560), (256, 624), (1, 0), 0, 105, 201)                          # the hall's frame

# the west yard, and the lane north out of it
ajarmap.fitted(m, (-1168, 64, -464, 448), [
    ((-528, 192, -464, 320), low()),
    ((-1072, 64, -944, 128), low()),                                         # before the boiler house
    ((-848, 224, -784, 288), dict(floor=32, ftex="AJWATER", side="AJTRIM")),  # the well
    ((-656, 96, -592, 224), SEAT),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
ajarmap.opening(m, (-448, 224), (-448, 288), (-1, 0), 0)
ajarmap.fitted(m, (-1168, 448, -1008, 2000), [
    ((-1168, 768, -1104, 896), low()),                                       # before the west wing's door
    ((-1168, 1728, -1104, 1952), low()),                                     # before the shed
    ((-1072, 1152, -1008, 1280), dict(WOOD, floor=48)),                      # crates
    ((-1168, 1408, -1104, 1472), dict(WOOD, floor=48)),
], floor=0, light=NIGHT, ftex="AJARCHF", **OPEN)
# the boiler house: bolted inside, and one of the places a Stray door opens onto
m.sector(rect(-1168, -16, -848, 48), ceil=128, light=120, wall="AJSAFE", ftex="AJPIT")
m.sector(rect(-1168, -208, -848, -16), ceil=128, light=120, wall="AJSAFE", ftex="AJPIT")
ajarmap.bolted(m, (-1040, 64), (-976, 64), (0, -1), 0, BOILER, line_id=305)
ajarmap.unbolt(m, (-1168, -16), (-848, -16), BOILER)
ajarmap.stray_place(m, 0, (-1040, -208), (-976, -208), (0, -1), 0)
# the shed in the lane (secret), seen through bars: shoot its bell
m.sector(rect(-1440, 1744, -1184, 1936), ceil=112, light=170, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.bolted(m, (-1168, 1760), (-1168, 1824), (-1, 0), 0, SHED)
bars((-1168, 1856), (-1168, 1920), (-1, 0), 0)
m.cut((-1440, 1856), (-1440, 1920))
m.line((-1440, 1856), (-1440, 1920), special=11, args=(SHED, 32), impact=True, mid="AJTARG", exact=True)

# === the library, under its stacks ===============================================
ajarmap.fitted(m, (-800, 528, -272, 912), [
    ((-336, 656, -272, 784), low()),                                         # before the hall's door
    ((-784, 528, -656, 592), low()),                                         # before the frame
    ((-640, 656, -448, 720), dict(WOOD, floor=32)), ((-640, 784, -448, 848), dict(WOOD, floor=32)),   # tables
    ((-432, 528, -368, 592), dict(WOOD, floor=112)), ((-432, 848, -368, 912), dict(WOOD, floor=112)),
], floor=0, ceil=320, light=170, color=WARM, wall="AJBRICK", ftex="AJFLOOR")
ajarmap.roomdoor(m, (-256, 688), (-256, 752), (-1, 0), 0)
recess((-752, 528), (-688, 528), (0, -1), 0, 102, 201, color=WARM)           # the frame under the stacks
ajarmap.fitted(m, (-992, 528, -800, 912), [
    ((-992, 624, -960, 848), dict(WOOD, floor=UP + 72)),                     # shelves
], floor=UP, ceil=320, light=180, color=WARM, wall="AJBRICK", ftex="AJBOARD", side="AJWOOD")
rail(((-800, 528), (-800, 688)), ((-800, 752), (-800, 912)))                 # a gap over the library
recess((-928, 528), (-864, 528), (0, -1), UP, far_id(GREEN), 101, far_colour=GREEN, color=WARM)

# === the dome, under its gallery =================================================
GAL = dict(floor=UP, ftex="AJSTEEL", side="AJSTEEL")
ajarmap.fitted(m, (-384, 928, 384, 1696), [
    ((-32, 928, 32, 1696), dict(ctex="F_SKY1")),                             # the slit, open to the stars
    ((-96, 928, 96, 992), low()),                                            # before the hall's door
    ((224, 928, 352, 992), low()),                                           # before the frame
    ((-384, 1056, -256, 1696), GAL), ((256, 1056, 384, 1696), GAL), ((-384, 1568, 384, 1696), GAL),
    ((-384, 1216, -320, 1344), dict(GAL, **low(UP))),                        # before the roof's door
    ((-96, 1632, 96, 1696), dict(GAL, **low(UP))),                           # before the night room's
    ((224, 1632, 352, 1696), dict(GAL, **low(UP))),                          # before YELLOW's far side
    ((-64, 1248, 64, 1376), dict(floor=256, ftex="AJSTEEL", side="AJSTEEL")),   # the pier of the telescope
    ((-160, 1088, -96, 1152), CASE), ((96, 1088, 160, 1152), CASE),
], floor=0, ceil=448, light=175, color=SKY, wall="AJBRICK", ftex="AJFLOOR")
ajarmap.roomdoor(m, (-32, 912), (32, 912), (0, 1), 0)
recess((288, 928), (352, 928), (0, -1), 0, 103, 201, color=SKY)              # the frame under the gallery
recess((256, 1696), (320, 1696), (0, 1), UP, far_id(YELLOW), 101, far_colour=YELLOW, color=SKY)
rail(((-384, 1056), (-256, 1056)), ((256, 1056), (384, 1056)),
     ((-256, 1056), (-256, 1408)), ((-256, 1472), (-256, 1568)),             # a gap on the west side
     ((256, 1056), (256, 1408)), ((256, 1472), (256, 1568)),                 # and on the east
     ((-256, 1568), (96, 1568)), ((160, 1568), (256, 1568)))                 # and on the north
# the night room off the gallery: bolted inside
ajarmap.way_round(m, NX, NY, BLUE, floor=UP)
ajarmap.bolted(m, (-32, 1696), (32, 1696), (0, 1), UP, NIGHT_BOLT, line_id=304)
ajarmap.unbolt(m, (NX, NY + 32), (NX + 320, NY + 32), NIGHT_BOLT)

# === the roof, between the lane and the dome ======================================
ajarmap.fitted(m, (-992, 928, -400, 1696), [
    ((-464, 1216, -400, 1344), low(UP)),                                     # before the gallery's door
    ((-832, 1088, -704, 1216), dict(floor=UP + 40, ftex="AJSTEEL", side="AJSTEEL")),   # skylights
    ((-832, 1408, -704, 1536), dict(floor=UP + 40, ftex="AJSTEEL", side="AJSTEEL")),
], floor=UP, light=NIGHT + 10, ftex="AJSTEEL", **OPEN)
ajarmap.roomdoor(m, (-384, 1248), (-384, 1312), (-1, 0), UP, line_id=306)

# === the hillside, the ravine, the knoll ==========================================
# under the roof's north edge: steps up to it, and at their head a gap by a
# gatepost that no door fits through. With a door the way is down: off the roof
ajarmap.fitted(m, (-992, 1696, -400, 2000), [
    ((-464, 1952 - 32 * i, -400, 1984 - 32 * i), dict(floor=20 * (i + 1), ftex="AJARCHF", side="AJTRIM"))
    for i in range(8)] + [
    ((-464, 1696, -400, 1728), dict(floor=UP, ftex="AJTRIMF", side="AJTRIM")),
    ((-416, 1696, -400, 1728), dict(floor=UP + 56, ftex="AJTRIMF", side="AJTRIM")),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
m.line((-464, 1696), (-416, 1696), id=ajarmap.SQUEEZE, blockmonsters=True)
rail(((-992, 1696), (-704, 1696)), ((-640, 1696), (-464, 1696)))             # a gap to jump down by
ajarmap.squeeze(m, (-1008, 1800), (-1008, 1848), (1, 0), 0)                  # the stile, from the lane
# the slope down to the ravine; the stump of the bridge tower has the frame
HILL = dict(floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
ajarmap.fitted(m, (-992, 2000, -96, 2400), [((-672, 2128, -608, 2192), dict(floor=48, side="AJTRIM")),
                                           ((-352, 2256, -288, 2320), dict(floor=48, side="AJTRIM"))], **HILL)
ajarmap.fitted(m, (-96, 2000, 32, 2272), [], **HILL)
ajarmap.fitted(m, (32, 2000, 800, 2400), [((32, 2272, 96, 2400), low()),
                                         ((416, 2128, 480, 2192), dict(floor=48, side="AJTRIM"))], **HILL)
recess((32, 2304), (32, 2368), (-1, 0), 0, 104, 201)                         # the hillside's frame
# the ravine: steps out of it at the west end, a cave at the foot of the far bank
ajarmap.fitted(m, (-992, 2400, 800, 2592), [
    ((-768 - 32 * i, 2400, -736 - 32 * i, 2464), dict(floor=PIT + 16 * (i + 1), ftex="AJARCHF", side="AJTRIM"))
    for i in range(8)] + [
    ((-848, 2528, -720, 2592), low(PIT)),
    ((200, 2464, 328, 2528), dict(ftex="AJWATER")),
], floor=PIT, light=NIGHT - 20, ftex="AJPIT", **OPEN)
m.sector(rect(-896, 2608, -672, 2672), floor=PIT, ceil=PIT + 112, light=140, wall="AJSAFE", ftex="AJPIT")
m.sector(rect(-896, 2672, -672, 2800), floor=PIT, ceil=PIT + 112, light=140, wall="AJSAFE", ftex="AJPIT",
         special=1024)
ajarmap.bolted(m, (-816, 2592), (-752, 2592), (0, 1), PIT, CAVE, line_id=307)
ajarmap.unbolt(m, (-896, 2672), (-672, 2672), CAVE)
ajarmap.stray_place(m, 1, (-896, 2704), (-896, 2768), (-1, 0), PIT, color=ROSE)
# the knoll: VIOLET's far side looks back across the ravine at the frame
ajarmap.fitted(m, (-480, 2592, 416, 2944), [
    ((128, 2880, 256, 2944), low()),
    ((-320, 2880, -192, 2944), low()),
    ((-416, 2720, -352, 2784), dict(floor=48, side="AJTRIM")),
], floor=0, light=NIGHT, ftex="AJGRASS", **OPEN)
recess((160, 2944), (224, 2944), (0, 1), 0, far_id(VIOLET), 101, far_colour=VIOLET)
# the transit house: two locks. BLUE, and the lever of the cave
ajarmap.fitted(m, (-448, 2960, -64, 3280), [
    ((-288, 3088, -224, 3152), CASE),                                        # the transit instrument
    ((-128, 3216, -64, 3280), SEAT),
], floor=0, ceil=160, light=170, color=PLUM)
ajarmap.roomdoor(m, (-288, 2944), (-224, 2944), (0, 1), 0, keys="34", line_id=303)
m.cut((-448, 3088), (-448, 3152))
m.line((-448, 3088), (-448, 3152), special=11, args=(CAVE, 32), playeruse=True, mid="AJLEVR", exact=True,
       id=308)

# === the west wing: one lock, off the lane =========================================
hall((-1632, 640, -1184, 1024), [((-1504, 768, -1376, 832)), ((-1312, 928, -1248, 992))], color=GOLD)   # workshop
hall((-1632, 1040, -1184, 1424), [((-1568, 1168, -1504, 1296)), ((-1312, 1168, -1248, 1296))])          # instruments
hall((-1632, 240, -1184, 624), [((-1440, 368, -1376, 496))], color=LEAF)                                # clocks
ajarmap.roomdoor(m, (-1168, 800), (-1168, 864), (-1, 0), 0, keys="1", line_id=301)
ajarmap.opening(m, (-1440, 1024), (-1376, 1024), (0, 1), 0)
ajarmap.opening(m, (-1440, 640), (-1376, 640), (0, -1), 0)
# the lens store (secret): a hole no door fits through, PINK, and a frame. Beyond
# its bars the armoury (secret): PINK's far side. The armoury's own door into the
# instrument room is bolted inside
m.sector(rect(-1632, 1440, -1424, 1648), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.squeeze(m, (-1560, 1424), (-1512, 1424), (0, 1), 0)
m.sector(rect(-1408, 1440, -1184, 1504), ceil=112, light=150, color=ROSE, wall="AJSAFE")
m.sector(rect(-1408, 1504, -1184, 1648), ceil=112, light=150, color=ROSE, wall="AJSAFE", special=1024)
bars((-1424, 1528), (-1424, 1592), (1, 0), 0)
recess((-1560, 1648), (-1496, 1648), (0, 1), 0, 107, 201, color=ROSE)
recess((-1328, 1648), (-1264, 1648), (0, 1), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)
ajarmap.bolted(m, (-1320, 1424), (-1256, 1424), (0, 1), 0, ARMOURY)
ajarmap.unbolt(m, (-1408, 1504), (-1184, 1504), ARMOURY)

# === the east wing: one lock, off the hall =========================================
hall((336, 528, 784, 848), [((432, 624, 688, 656)), ((432, 720, 688, 752))], color=GOLD)                # lecture room
ajarmap.fitted(m, (800, 528, 1248, 976), [((992, 720, 1056, 784), CASE)],                              # planetarium
               ceil=224, light=120, wall="AJXW2", ftex="AJXG2", ctex="AJXC2")
hall((800, 992, 1248, 1376), [((864, 1120, 928, 1184)), ((1120, 1120, 1184, 1184)), ((992, 1056, 1056, 1120))],
     color=PLUM)                                                                                       # orrery
ajarmap.roomdoor(m, (256, 688), (256, 752), (1, 0), 0, keys="2", thick=80, line_id=302)
ajarmap.opening(m, (784, 656), (784, 720), (1, 0), 0)
ajarmap.opening(m, (992, 976), (1056, 976), (0, 1), 0)
# steps down to the cellar: the cistern, and past it a hole into an alcove (secret)
ajarmap.stairs(m, (992, 1376), (1056, 1376), (0, 1), 0, CELLAR, light=150, wall="AJBRICK", ftex="AJBOARD")
CELL = dict(floor=CELLAR, ceil=0, light=140, wall="AJBRICK", ftex="AJPIT")
ajarmap.fitted(m, (800, 1632, 1376, 1968), [
    ((1120, 1728, 1312, 1904), dict(floor=CELLAR - 16, ftex="AJWATER")),
    ((832, 1840, 960, 1936), dict(WOOD, floor=CELLAR + 48)),
], **CELL)
m.sector(rect(1392, 1760, 1536, 1888), floor=CELLAR, ceil=CELLAR + 96, light=120, wall="AJSAFE", ftex="AJPIT",
         special=1024)
ajarmap.squeeze(m, (1376, 1800), (1376, 1848), (1, 0), CELLAR)

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
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, BARREL = 24, 2035


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the road, the passage, the forecourt, the hall, the yard: lamps and nobody
things(LAMP, (-96, -352), (280, -352), (-96, -32), (96, -32), (-96, 480), (96, 480), (-500, 416), (-1136, 416))
things(TECHLAMP, (-232, 552), (232, 888))
things(SHOTGUN, (0, 720))                                                 # for anyone who came without one
things(SHELLS, (-40, 760), (40, 760))
things(STIM, (-200, 720), (-500, 100))
things(BONUS, (-200, -700), (-200, -560), (0, 96), (0, 160))
# the lane: the first of them, round the corner
things(ZOMBIE, (-1090, 1000), (-1130, 1100), (-1060, 1340), (-1090, 1560), angle=270)
things(IMP, (-1140, 1240), (-1060, 1500), (-1090, 1900), angle=270)
things(SERGEANT, (-1050, 1700), (-1130, 1660), angle=270)
things(LAMP, (-1030, 480), (-1030, 1000), (-1030, 1960))
things(CLIP, (-1040, 700), (-1040, 740))
things(STIM, (-1140, 1980))
# the boiler house: do not open this door
things(MANCUBUS, (-1000, -120), angle=90)
things(KNIGHT, (-1120, -150), (-890, -150), angle=90)
things(BERSERK, (-1140, 20))
things(ROCKETS, (-880, 20), (-920, 20))
# the shed
things(PLASMA, (-1300, 1840))
things(CELLS, (-1400, 1780), (-1400, 1820))
things(MEGA, (-1220, 1900))
# the library: readers. From the stacks they are all below you
things(IMP, (-700, 640), (-400, 680), (-700, 880), (-560, 760), (-380, 800), (-320, 580), angle=0)
things(DEMON, (-600, 600), (-500, 880), (-740, 760), (-360, 740), angle=0)
things(SERGEANT, (-680, 700), (-420, 620), (-560, 880), angle=0)
things(SPECTRE, (-760, 640), (-320, 880), angle=0)
things(KNIGHT, (-720, 820), angle=0)
things(CACO, (-540, 620), angle=0, ambush=True)
things(TORCH_R, (-776, 616), (-296, 552))
things(SHELLS, (-544, 688), (-544, 816))
things(MEDIKIT, (-300, 890))
# the stacks: key 1, a chaingun, and a quiet reader or two
things(ZOMBIE, (-900, 700), (-850, 600), angle=0)
things(CHAINGUN, (-900, 800))
things(AMMOBOX, (-940, 890))
things(SHELLBOX, (-830, 560))
things(STIM, (-960, 590))
# the dome: the night's observers, round the telescope
things(BARON, (-160, 1440), (160, 1440), angle=270)
things(KNIGHT, (0, 1160), (-200, 1240), (200, 1240), angle=270)
things(REVENANT, (-120, 1520), (120, 1520), angle=270)
things(IMP, (-320, 980), (320, 1010), (-200, 1020), (200, 1040), (-150, 1320), (150, 1320), angle=270)
things(DEMON, (-220, 1150), (220, 1150), (0, 1100), angle=270)
things(MANCUBUS, (0, 1500), angle=270, ambush=True)
things(TECHLAMP, (-232, 1080), (232, 1080), (-232, 1544), (232, 1544))
things(SHELLBOX, (-220, 1500))
things(MEDIKIT, (220, 1500), (-350, 950))
things(ROCKETS, (-40, 1410), (40, 1410))
# the gallery: key 2, cells, and those who watch from above
things(CHAINGUNNER, (-320, 1500), (320, 1500), angle=270)
things(IMP, (-320, 1120), (-100, 1630), (140, 1610), angle=270)
things(SERGEANT, (320, 1230), angle=270)
things(REVENANT, (60, 1600), angle=270)
things(PLASMA, (-200, 1640))
things(CELLS, (-250, 1640), (-300, 1640), (340, 1660))
things(STIM, (-350, 1670), (350, 1400))
# the night room: someone has been waiting
things(REVENANT, (NX + 160, NY + 128), angle=270)
things(KNIGHT, (NX + 96, NY + 224), (NX + 224, NY + 224), angle=270)
# the roof
things(IMP, (-940, 1040), (-600, 980), (-940, 1300), (-560, 1620), angle=0)
things(SERGEANT, (-640, 1300), (-900, 1620), angle=0)
things(CHAINGUNNER, (-520, 1100), (-940, 1500), angle=0)
things(CACO, (-640, 1100), (-620, 1500), angle=0, ambush=True)
things(REVENANT, (-560, 1400), angle=0)
things(SUPER, (-768, 1310))
things(SHELLS, (-768, 1270), (-768, 1350))
things(MEDIKIT, (-960, 1660))
things(ARMOR, (-430, 960))
# the hillside
things(IMP, (-900, 1800), (-700, 1900), (-560, 2100), (-200, 2100), (500, 2060), angle=270)
things(DEMON, (-800, 2200), (-460, 2300), (200, 2200), (600, 2300), angle=270)
things(SPECTRE, (-900, 2320), (-200, 2330), (700, 2100), angle=270)
things(KNIGHT, (300, 2240), angle=270)
things(SOUL, (-600, 2000), (100, 2100), (560, 2200), angle=270)
things(IMP, (680, 2040), (-300, 2040), angle=270)
things(SERGEANT, (-760, 2060), (520, 2330), angle=270)
things(CHAINGUNNER, (740, 2240), angle=180)
things(CACO, (0, 2140), angle=270, ambush=True)
things(LAMP, (60, 2250), (-560, 1730))
things(SHELLS, (-760, 1760), (-500, 2060))
things(STIM, (700, 2360), (-960, 2040))
things(ROCKETS, (-640, 2224))
# the ravine and its cave
things(SPECTRE, (-400, 2500), (0, 2520), (400, 2440), (700, 2500), angle=180)
things(DEMON, (-600, 2540), (-150, 2470), (560, 2540), angle=180)
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
things(KNIGHT, (-150, 2840), (20, 2680), angle=270)
things(CHAINGUNNER, (-440, 2640), (380, 2800), angle=270)
things(LAMP, (-340, 2912), (-170, 2912), (110, 2912), (274, 2912))
things(MEDIKIT, (-440, 2900))
things(ROCKETBOX, (380, 2900))
# the transit house: the astronomer, working late, and deaf to the garden
things(BARON, (-160, 3120), angle=270, ambush=True)
things(KNIGHT, (-380, 3040), (-160, 3020), angle=270, ambush=True)
things(TECHLAMP, (-424, 2984), (-88, 2984))
things(MEDIKIT, (-200, 3250))
things(CELLS, (-340, 3250))
# the west wing: the workshop, the instruments, the clocks
things(ZOMBIE, (-1300, 700), (-1560, 700), (-1300, 1100), angle=0)
things(IMP, (-1560, 960), (-1240, 860), (-1560, 1100), (-1240, 1380), (-1560, 560), (-1240, 300), angle=0)
things(SERGEANT, (-1440, 900), (-1400, 1340), (-1300, 560), angle=0)
things(DEMON, (-1440, 700), (-1400, 1100), (-1500, 420), angle=0)
things(CHAINGUNNER, (-1600, 1380), (-1240, 580), angle=0)
things(REVENANT, (-1500, 300), angle=0)
things(KNIGHT, (-1300, 420), angle=0)
things(PAIN, (-1400, 1220), angle=0)
things(TECHLAMP, (-1608, 664), (-1208, 1000), (-1608, 1064), (-1208, 1400), (-1608, 600), (-1208, 264))
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
things(IMP, (560, 580), (720, 800), (860, 600), (1180, 600), (860, 900), (1180, 1040), (860, 1320), angle=180)
things(SERGEANT, (560, 690), (1180, 900), (1180, 1320), angle=180)
things(DEMON, (720, 690), (1020, 900), (1020, 1260), angle=180)
things(SPECTRE, (900, 760), (1150, 760), angle=180)
things(CHAINGUNNER, (1200, 560), (840, 1040), angle=180)
things(ARACHNO, (1024, 620), angle=270)
things(CACO, (1024, 1220), angle=270, ambush=True)
things(REVENANT, (1210, 1250), angle=180)
things(KNIGHT, (930, 1300), angle=180)
things(SERGEANT, (640, 800), angle=180)
things(TECHLAMP, (360, 552), (760, 824), (824, 1016), (1224, 1352))
things(CANDELABRA, (824, 552), (1224, 552), (824, 952), (1224, 952))
things(SHELLBOX, (760, 552))
things(MEDIKIT, (1224, 1016), (360, 824))
things(STIM, (824, 1352), (1224, 760))
things(ROCKETS, (1024, 1340), (1064, 1340))
# the cellar and its alcove
things(SPECTRE, (860, 1700), (1000, 1900), (1340, 1920), angle=90)
things(DEMON, (1000, 1760), (1060, 1680), (1340, 1700), angle=90)
things(IMP, (880, 1890), (1216, 1800), (1200, 1680), angle=90)
things(SOUL, (1100, 1940), (1250, 1940), angle=90)
things(LODGER, (1024, 1700), args=(300,))
things(TORCH_G, (824, 1656), (1352, 1944))
things(MEDIKIT, (830, 1790))
things(ARMOR, (1500, 1824))
things(SHELLBOX, (1500, 1780))
things(CELLS, (1500, 1868))
things(CANDLE, (1416, 1784), (1416, 1864))

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
