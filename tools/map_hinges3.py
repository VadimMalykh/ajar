"""Act 1, level 3: "Stage Door" (MAP03).

A theatre, and the first level that is not a chain. The way out is the RED
door, locked in the star's dressing room behind two locks.

Front of house is one place to walk about in: foyer, cloakroom, bar,
stalls, orchestra pit. Everything else is above or below it and is reached
by door: the dress circle (BLUE), the room under the stage (VIOLET), the
flies (GREEN). Most of those places are left by dropping.

What is new, and why it is not a chain:

- Two doors from the start, BLUE in the bar and VIOLET in the cloakroom,
  and two things to fetch with them in either order: key 2 on the circle,
  GREEN under the stage.
- Shortcuts. The circle's stairs and the grate between the pit and the room
  under the stage are bolted on their far side and open for good the first
  time you get there (ajarmap.bolted).
- A door with two jobs. Nothing leads to the stage: you drop onto it from
  the flies. But the flies are also the way to the gods, along the lighting
  bridge, and both are one-way, so each trip through GREEN is a choice.
- A door first met from its far side. YELLOW hangs in the lighting booth,
  a shut room behind the gods. In the gods its far side stands open, and
  through it is the booth and key 3.
- A spare door. PINK hangs in the manager's office (key 1, from a dressing
  room). It opens onto the property store: guns, and what guards them. You
  do not need it, and a door once taken wants a frame for good.
- Frames: foyer, stalls, under the stage, booth, office. RED must be picked
  up with empty hands, so every other door you took has to hang somewhere.

Keys 2 and 3 open the star's dressing room, backstage: RED, which opens
onto the way out. The stage is too high to climb, so it goes out by the drop
into the pit, or into the room under the stage, which has a frame.
"""
import os

import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


HOUSE = 448                                       # auditorium ceiling
STAGE, UNDER, PIT, CIRCLE, GODS, FLIES = 64, -64, -48, 128, 224, 288
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
WOOD = dict(ftex="AJWOOD", side="AJWOOD")

# The theatre's look (gfx_theatre.py): 1, an opera house, is the user's choice
# for the whole building. AJAR_THEATRE=2 and 3 are the candidates that lost
# (an old playhouse, a civic theatre of the 1960s); AJAR_THEATRE=0 is the
# theatre as first built.
# With a look, rooms are not tinted, runners' lights sit flush in the ceiling,
# and the back of the house is the same in all three.
LOOK = (os.environ.get("AJAR_THEATRE") or "1").replace("0", "")
if LOOK:
    WARM = GOLD = SKY = LEAF = PLUM = ROSE = None
    RAIL = dict(RAIL, floorpeg=True)          # the tier fronts under the railings start at the tier's floor
    LOWC, TOPC, DARKC = f"AJ3E{LOOK}", f"AJ3C{LOOK}", "AJ3XC"
    RUN = dict(rug=f"AJ3R{LOOK}", lite=f"AJ3L{LOOK}", lift=0)
    FOYER = dict(wall=f"AJ3F{LOOK}", ftex=f"AJ3O{LOOK}", ctex=LOWC)
    SIDE = dict(wall=f"AJ3G{LOOK}", ftex=f"AJ3O{LOOK}", ctex=LOWC)      # passage, cloakroom, office
    BAR = dict(wall=f"AJ3B{LOOK}", ftex=f"AJ3M{LOOK}", ctex=LOWC)
    STALLS = dict(wall=f"AJ3H{LOOK}A", ftex=f"AJ3M{LOOK}", ctex=TOPC)
    TIER1 = dict(wall=f"AJ3H{LOOK}B", side=f"AJ3T{LOOK}A", ftex=f"AJ3M{LOOK}", ctex=TOPC)
    TIER2 = dict(wall=f"AJ3H{LOOK}C", side=f"AJ3T{LOOK}B", ftex=f"AJ3M{LOOK}", ctex=TOPC)
    BRIDGE = dict(wall=f"AJ3H{LOOK}D", side=f"AJ3T{LOOK}C", ctex=TOPC)
    FLY = dict(wall="AJ3XL", ctex=DARKC)
    CURTAIN, UNDERW, BOOTHW = f"AJ3K{LOOK}", "AJ3XU", "AJ3XB"
    SEAT = dict(ftex=f"AJ3S{LOOK}", side=f"AJ3S{LOOK}")
    BACKL = dict(wall="AJ3XW", ftex="AJ3XF", lift=0)
    DRESS, STARS, GREENS = (dict(wall=w, ftex="AJ3XF") for w in ("AJ3XD", "AJ3XS", "AJ3XG"))
    STAIR = dict(wall="AJ3XP", ftex="AJ3XF")
    FDOOR, BDOOR = f"AJ3D{LOOK}F", "AJ3DXB"
    m.align = ({f"AJ3{k}{LOOK}{t}" for k, ts in (("H", "ABCD"), ("T", "ABC")) for t in ts} |
               {f"AJ3{k}{LOOK}" for k in "FGBK"} |
               {"AJ3XW", "AJ3XD", "AJ3XS", "AJ3XG", "AJ3XM", "AJ3XN", "AJ3XB", "AJ3XU", "AJ3XL", "AJ3XP"})
else:
    LOWC = TOPC = DARKC = "AJCEIL"
    RUN = FOYER = SIDE = BAR = STALLS = TIER1 = TIER2 = BRIDGE = FLY = {}
    BACKL = DRESS = STARS = GREENS = STAIR = {}
    CURTAIN, UNDERW, BOOTHW = "AJCURT", "AJBRICK", "AJSAFE"
    SEAT = dict(ftex="AJSOFA", side="AJSOFA")
    FDOOR = BDOOR = ""
GATE_PIT, GATE_BOOTH, GATE_STAIRS = 401, 402, 403           # the three bolted ways


def rail(*runs):
    for a, b in runs:
        m.cut(a, b)             # a railing ends where it says, not at the next corner of a room
        m.line(a, b, **RAIL)


# === front of house ==========================================================
# --- the foyer: start here. Box office, a sofa, pictures of the first two doors
ajarmap.fitted(m, (-640, 1024, 240, 1680), [
    ((-640, 1320, 240, 1384), ajarmap.RUNNER), ((96, 1024, 160, 1680), ajarmap.RUNNER),
    ((-640, 1440, -576, 1616), dict(WOOD, floor=40)),                        # box office counter
    ((-480, 1648, -352, 1680), dict(SEAT, floor=40)), ((-480, 1616, -352, 1648), dict(SEAT, floor=16)),
], ceil=176, light=190, **FOYER, **RUN)
m.sector(rect(64, 896, 192, 1024), ceil=128, light=170, **SIDE)             # the way into the stalls
if LOOK:                                  # the taller rooms' walls carry on over its two mouths
    m.line((64, 1024), (192, 1024), upper=FOYER["wall"], dontpegtop=True)
    m.line((64, 896), (192, 896), upper=STALLS["wall"], dontpegtop=True)
recess((-256, 1024), (-192, 1024), (0, -1), 0, 101, 201)                    # foyer frame
ajarmap.picture(m, (-448, 1024), (-384, 1024), VIOLET, 176, tex=f"AJ3P{LOOK}{VIOLET}" if LOOK else None)
ajarmap.picture(m, (-64, 1024), (0, 1024), BLUE, 176, tex=f"AJ3P{LOOK}{BLUE}" if LOOK else None)
# the cloakroom (VIOLET leans here)
ajarmap.fitted(m, (-912, 1100, -656, 1356), [((-912, 1100, -880, 1356), dict(WOOD, floor=48))],
               ceil=128, light=150, **SIDE)
ajarmap.roomdoor(m, (-640, 1196), (-640, 1260), (-1, 0), 0, skin=FDOOR)
# the manager's office, locked (key 1): its frame starts with PINK in it
ajarmap.fitted(m, (-384, 1696, -128, 1952), [((-384, 1760, -320, 1888), dict(WOOD, floor=32))],
               ceil=128, light=160, color=ROSE, **SIDE)
ajarmap.roomdoor(m, (-288, 1680), (-224, 1680), (0, 1), 0, keys="1", line_id=301, skin=FDOOR)
recess((-288, 1952), (-224, 1952), (0, 1), 0, 106, 201, color=ROSE)
# the bar (BLUE leans here); the circle's stairs come down into it
ajarmap.fitted(m, (256, 1360, 1024, 1680), [
    ((480, 1616, 864, 1648), dict(WOOD, floor=40)),                          # the bar itself
    ((640, 1424, 704, 1488), dict(floor=28, ftex="AJCLOTH", side="AJCLOTH")),
    ((832, 1424, 896, 1488), dict(floor=28, ftex="AJCLOTH", side="AJCLOTH")),
], ceil=144, light=180, color=SKY, **BAR)
ajarmap.opening(m, (240, 1488), (240, 1552), (1, 0), 0)

# --- the stalls: rows of seats, an aisle down to the pit --------------------
ajarmap.fitted(m, (0, 0, 1024, 896),
               [((0, 416, 1024, 480), ajarmap.RUNNER)] +
               [((x, y, x + 48, y + 320), dict(SEAT, floor=16))
                for x in range(320, 896, 128) for y in (64, 512)],
               ceil=HOUSE, light=170, **STALLS, **RUN)
recess((224, 896), (288, 896), (0, 1), 0, 104, 201)                         # stalls frame
# the orchestra pit, a step down and another
m.sector(rect(1024, 0, 1056, 896), floor=PIT // 2, ceil=HOUSE, light=160, **STALLS)
m.sector(rect(1056, 0, 1152, 896), floor=PIT, ceil=HOUSE, light=150, **dict(STALLS, ftex="AJBOARD"))

# === the stage, too high to climb; the room under it is open from above =====
BOARDS = dict(floor=STAGE, ceil=HOUSE, light=200, wall=CURTAIN, ftex="AJBOARD", side="AJWOOD", ctex=DARKC)
m.sector(rect(1152, 0, 1792, 640), **BOARDS)
m.sector(rect(1424, 640, 1792, 896), **BOARDS)
for y1, y2 in ((640, 736), (800, 896)):                                     # the stage's lip
    m.sector(rect(1152, y1, 1168, y2), **BOARDS)
m.sector(rect(1168, 640, 1424, 896), floor=UNDER, ceil=HOUSE, light=140, wall=UNDERW,
         ftex="AJPIT", color=PLUM, ctex=DARKC)
recess((1200, 896), (1264, 896), (0, 1), UNDER, 102, 201, color=PLUM)       # frame under the stage
recess((1328, 896), (1392, 896), (0, 1), UNDER, far_id(VIOLET), 101, far_colour=VIOLET, color=PLUM)
# the grate between it and the pit: a block of the stage front that sinks
# for good when anything comes down here
m.sector(rect(1152, 736, 1168, 800), floor=STAGE, ceil=HOUSE, light=160, wall=CURTAIN,
         ftex="AJTRIMF", side="AJGRATE", id=GATE_PIT, ctex=DARKC)
for a, b in (((1168, 640), (1424, 640)), ((1424, 640), (1424, 896)), ((1168, 640), (1168, 736)),
             ((1168, 800), (1168, 896)), ((1328, 896), (1392, 896))):
    ajarmap.unbolt(m, a, b, GATE_PIT, special=21)
    if LOOK and b != (1392, 896):                             # the room's walls are the stage's sides
        m.line(a, b, lower=UNDERW)
m.line((1168, 736), (1168, 800), id=304)

# --- backstage: a corridor, dressing rooms, the green room ------------------
BACK = dict(floor=STAGE, ceil=STAGE + 128)
m.sector(rect(1536, 896, 1728, 960), light=170, **BACK, **{k: v for k, v in BACKL.items() if k != "lift"})
ajarmap.room(m, [1152, 2112], [960, 992, 1056, 1088], lambda i, j: j == 1, light=165, **BACK, **BACKL)
ROOM = dict(floor=STAGE, ceil=STAGE + 112)
TABLE = dict(WOOD, floor=STAGE + 32)                                        # dressing tables
if LOOK:                                  # a mirror with bulbs over every table; the room's wall at its ends
    m.line((1536, 896), (1728, 896), upper=CURTAIN, dontpegtop=True)
    TABLE["wall"] = "AJ3XM"
    for x, w in ((1152, "AJ3XD"), (1408, "AJ3XD"), (1472, "AJ3XD"), (1728, "AJ3XD"), (1792, "AJ3XS"), (2048, "AJ3XS")):
        m.line((x, 1328), (x, 1360), mid=w)
ajarmap.fitted(m, (1152, 1104, 1408, 1360), [((1152, 1328, 1408, 1360), TABLE)], light=175, **ROOM, **DRESS)
ajarmap.roomdoor(m, (1248, 1088), (1312, 1088), (0, 1), STAGE, skin=BDOOR)
ajarmap.fitted(m, (1472, 1104, 1728, 1360), [((1472, 1328, 1728, 1360), TABLE)], light=140, **ROOM, **DRESS)
ajarmap.roomdoor(m, (1568, 1088), (1632, 1088), (0, 1), STAGE, skin=BDOOR)
ajarmap.fitted(m, (1792, 1104, 2048, 1360),                                  # the star's: two locks
               [((1792, 1328, 2048, 1360), dict(TABLE, wall="AJ3XN") if LOOK else TABLE),
                ((1792, 1136, 1808, 1264), dict(SEAT, floor=STAGE + 40)),
                ((1808, 1136, 1840, 1264), dict(SEAT, floor=STAGE + 16))],
               light=185, color=WARM, **ROOM, **STARS)
ajarmap.roomdoor(m, (1888, 1088), (1952, 1088), (0, 1), STAGE, keys="23", line_id=302, skin=BDOOR)
ajarmap.fitted(m, (2128, 896, 2448, 1152),                                   # the green room
               [((2416, 928, 2448, 1120), dict(SEAT, floor=STAGE + 40)),
                ((2384, 928, 2416, 1120), dict(SEAT, floor=STAGE + 16))],
               light=170, color=LEAF, **ROOM, **GREENS)
ajarmap.opening(m, (2112, 992), (2112, 1056), (1, 0), STAGE)

# === above the house =========================================================
# --- the dress circle (BLUE's far side): a ledge along the north wall --------
ajarmap.fitted(m, (320, 896, 1024, 1088), [((480, 976, 992, 1024), dict(SEAT, floor=CIRCLE + 16))],
               floor=CIRCLE, ceil=HOUSE, light=185, color=SKY, **TIER1)
rail(((320, 896), (640, 896)), ((768, 896), (1024, 896)))
recess((640, 1088), (704, 1088), (0, 1), CIRCLE, far_id(BLUE), 101, far_colour=BLUE, color=SKY)
ajarmap.unbolt(m, (640, 1088), (704, 1088), GATE_STAIRS)
# its stairs, down to a door into the bar that is bolted on this side
ajarmap.stairs(m, (352, 1088), (416, 1088), (0, 1), CIRCLE, -CIRCLE, ceil=CIRCLE + 128, light=170, **STAIR)
if LOOK:
    m.line((352, 1088), (416, 1088), upper=TIER1["wall"], dontpegtop=True)
ajarmap.bolted(m, (352, 1360), (416, 1360), (0, -1), 0, GATE_STAIRS, line_id=303)

# --- the gods (YELLOW's far side): the top tier, at the back -----------------
ajarmap.fitted(m, (-448, 128, 0, 768), [((-352, 176, -304, 368), dict(SEAT, floor=GODS + 16)),
                                        ((-352, 528, -304, 720), dict(SEAT, floor=GODS + 16))],
               floor=GODS, ceil=HOUSE, light=175, color=GOLD, **TIER2)
rail(((0, 128), (0, 384)), ((0, 512), (0, 768)))
recess((-256, 768), (-192, 768), (0, 1), GODS, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)
# the lighting booth behind them: shut, with YELLOW hanging in its frame. Its
# door to the gods is bolted inside; a window shows what is in there
BOOTH = dict(floor=GODS, ceil=GODS + 112, light=200, wall=BOOTHW, color=GOLD, ctex=LOWC)
m.sector(rect(-720, 320, -672, 576), **BOOTH)
m.sector(rect(-672, 320, -464, 576), **BOOTH)
ajarmap.unbolt(m, (-672, 320), (-672, 576), GATE_BOOTH)
recess((-720, 416), (-720, 480), (-1, 0), GODS, 105, 201, color=GOLD)        # booth frame
ajarmap.bolted(m, (-448, 416), (-448, 480), (-1, 0), GODS, GATE_BOOTH, line_id=305)
m.sector(rect(-464, 496, -448, 560), floor=GODS + 40, ceil=GODS + 96, light=220, wall=BOOTHW,
         ftex="AJTRIMF", ctex="AJTRIMF")
m.line((-448, 496), (-448, 560), mid="AJWIN", midboth=True, blocking=True)
if LOOK:
    m.line((-448, 496), (-448, 560), upper=TIER2["wall"], dontpegtop=True, lower="AJ3XP")

# --- the flies (GREEN's far side) over the stage, and the lighting bridge
# from them along the south wall to a landing above the gods ------------------
HIGH = dict(floor=FLIES, ceil=HOUSE, light=170, wall="AJTRIM", ftex="AJBOARD", color=LEAF)
m.sector(rect(1152, -192, 1792, 0), **dict(HIGH, **FLY))
HIGH = dict(HIGH, **BRIDGE)
recess((1440, -192), (1504, -192), (0, -1), FLIES, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)
m.sector(rect(0, -96, 1152, 0), **HIGH)
m.sector(rect(-448, -96, 0, 128), **HIGH)
rail(((1152, 0), (1408, 0)), ((1536, 0), (1792, 0)), ((0, 0), (1152, 0)), ((0, 0), (0, 128)))
# a nook off the bridge that nobody looks into (secret)
m.sector(rect(512, -224, 640, -96), floor=FLIES, ceil=FLIES + 96, light=110, wall="AJTRIM",
         ftex="AJBOARD", special=1024)

# === far sides that are places of their own ==================================
# --- the property store (PINK's far side): no other way in (secret) ----------
m.sector(rect(4000, 0, 4448, 384), ceil=160, light=150, color=ROSE, wall="AJSAFE", special=1024)
recess((4000, 160), (4000, 224), (-1, 0), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)

# --- the way out (RED's far side): the same room in every level -------------
ajarmap.way_out(m, 5000, 0, RED)

# --- doors and keys ----------------------------------------------------------
m.thing(-200, 1352, 1, angle=0)                                           # player start, in the foyer
ajarmap.door(m, VIOLET, -866, 1228, angle=0)                              # leaning in the cloakroom
ajarmap.door(m, BLUE, 1010, 1520, angle=180)                              # leaning in the bar
ajarmap.door(m, GREEN, 1296, 654, angle=90)                               # leaning under the stage
ajarmap.door(m, YELLOW, -700, 448, frame=105)                             # hanging in the booth
ajarmap.door(m, PINK, -256, 1930, frame=106)                              # hanging in the office
ajarmap.door(m, RED, 2034, 1232, angle=180)                               # leaning in the star's room
ajarmap.key(m, 1, 1280, 1300)                                             # first dressing room
ajarmap.key(m, 2, 990, 1050)                                              # far end of the circle
ajarmap.key(m, 3, -560, 540)                                              # the booth, by the window

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER = 3004, 9, 3001, 3002, 58, 20005
CHAINGUNNER, KNIGHT, REVENANT, SOUL, CACO = 65, 69, 66, 3006, 3005
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS = (
    2001, 82, 2002, 2003, 2008, 2049, 2007, 2048, 2046)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE = 2011, 2012, 2014, 2015, 2018, 2019, 2013
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, DEAD_ZOMBIE = 24, 18


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the foyer: quiet. A shotgun for anyone who came without one.
things(SHOTGUN, (-520, 1528))
things(SHELLS, (-520, 1480), (-520, 1576))
things(CANDELABRA, (-616, 1048), (216, 1048), (-616, 1656), (216, 1656))
things(LAMP, (40, 1048), (216, 1440), (216, 1600))
things(STIM, (-300, 1640))
# the cloakroom: the attendant
things(ZOMBIE, (-760, 1140), angle=0)
things(CLIP, (-700, 1330))
# the bar: last orders
things(SERGEANT, (540, 1560), (800, 1560), angle=180)
things(IMP, (672, 1400), (940, 1400), angle=180)
things(ZOMBIE, (330, 1640), angle=90)
things(TORCH_B, (1000, 1456), (1000, 1584))
things(STIM, (500, 1632), (700, 1632))
things(ARMOR, (300, 1400))
# the stalls: an audience; the lodger wakes when you are well into the house
things(IMP, (500, 120), (760, 200), (500, 760), (760, 680), (900, 448), angle=180)
things(ZOMBIE, (250, 200), (250, 700), (620, 448), angle=180)
things(SERGEANT, (960, 100), (960, 800), angle=180)
things(LAMP, (24, 24), (24, 872))
things(CLIP, (120, 448), (150, 448))
things(MEDIKIT, (990, 30))
things(LODGER, (512, 448), args=(260,))
# the pit: the orchestra
things(DEMON, (1104, 200), (1104, 620), angle=180)
things(SPECTRE, (1104, 410), angle=180)
things(SHELLS, (1100, 30), (1100, 860))
# the stage: tonight's act
things(KNIGHT, (1500, 300), angle=180)
things(IMP, (1300, 120), (1700, 120), (1700, 760), angle=180)
things(CHAINGUNNER, (1740, 448), angle=180)
things(CANDELABRA, (1176, 24), (1176, 616))
things(SHELLBOX, (1760, 40))
things(STIM, (1500, 860), (1540, 860))
# under the stage: something you cannot quite see
things(SPECTRE, (1240, 700), (1370, 820), angle=90)
things(POOL, (1300, 780))
things(MEDIKIT, (1400, 870))
# backstage: stagehands
things(ZOMBIE, (1300, 1024), (1700, 1024), angle=180)
things(SERGEANT, (1900, 1024), (2060, 1024), angle=180)
things(CANDLE, (1168, 976), (1168, 1072))
# first dressing room: key 1 and an imp at the mirror
things(IMP, (1200, 1260), angle=270)
things(LAMP, (1388, 1124))
things(SHELLS, (1380, 1300))
# second dressing room: dark; a chaingun and the chorus
things(CHAINGUN, (1600, 1280))
things(AMMOBOX, (1640, 1280))
things(IMP, (1500, 1200), (1700, 1200), angle=270)
things(DEMON, (1600, 1180), angle=270)
# the star's: RED, and the star
things(KNIGHT, (1920, 1220), angle=270)
things(TORCH_R, (2030, 1160), (2030, 1304))
things(MEDIKIT, (1880, 1300))
# the green room: the understudies
things(SERGEANT, (2200, 940), (2200, 1110), angle=180)
things(CACO, (2330, 1024), angle=180)
things(SHELLBOX, (2420, 910))
things(STIM, (2420, 1136))
# the dress circle: the best seats, and the best gun
things(SUPER, (900, 940))
things(SHELLS, (860, 940), (940, 940))
things(CHAINGUNNER, (520, 930), angle=0)
things(IMP, (960, 1056), angle=180)
things(TORCH_B, (616, 1072), (728, 1072))
# the gods: snipers at the rail
things(CHAINGUNNER, (-40, 200), (-40, 700), angle=0)
things(IMP, (-400, 448), angle=0)
things(CANDELABRA, (-280, 744), (-168, 744))
things(AMMOBOX, (-420, 160))
things(MEDIKIT, (-420, 740))
# the booth: key 3, and the man who works the lights
things(SERGEANT, (-520, 360), angle=180)
things(TECHLAMP, (-488, 344), (-488, 552))
# the flies and the bridge: lost souls among the ropes
things(SOUL, (1250, -96), (1700, -96), (700, -48), (200, -48), angle=180)
things(TORCH_G, (1408, -168), (1536, -168))
things(BONUS, (1200, -160), (1760, -160))
things(SPHERE, (576, -180))                                               # in the nook
# the property store: a rocket launcher, armour, and the props that walk
things(LAUNCHER, (4380, 192))
things(ROCKETS, (4380, 140), (4380, 244), (4420, 192))
things(MEGA, (4400, 340))
things(SHELLBOX, (4400, 40))
things(REVENANT, (4250, 100), (4250, 290), angle=180)
things(IMP, (4130, 60), (4130, 330), angle=180)
things(CANDELABRA, (4424, 24), (4424, 360))
# the way out: the last things between you and it
things(REVENANT, (5264, 128), angle=180)
things(SERGEANT, (5230, 48), (5230, 208), angle=180)

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "front" is foyer, cloakroom, bar, stalls and pit; "stage" includes backstage;
# "flies" includes the bridge. a, b, c are the three bolts.
PUZZLE = dict(
    start="front", goal="exit", names=ajarmap.NAMES, complete=True,
    walk=[("circle", "front"), ("gods", "front"), ("flies", "stage"), ("flies", "gods"),
          ("stage", "front"), ("stage", "under"),
          ("under", "front", "a"), ("front", "under", "a"),               # the grate
          ("booth", "gods", "b"), ("gods", "booth", "b"),                 # the booth's door
          ("circle", "front", "c"), ("front", "circle", "c"),             # the circle's stairs
          ("front", "office", "1"), ("office", "front", "1"),
          ("stage", "star", "23"), ("star", "stage", "23")],
    keys={"1": "stage", "2": "circle", "3": "booth", "a": "under", "b": "booth", "c": "circle"},
    auto="abc",
    frames={101: "front", 104: "front", 102: "under", 105: "booth", 106: "office"},
    doors={
        VIOLET: dict(home="under", lean="front"),
        BLUE: dict(home="circle", lean="front"),
        GREEN: dict(home="flies", lean="under"),
        YELLOW: dict(home="gods", frame=105),
        PINK: dict(home="store", frame=106),
        RED: dict(home="exit", lean="star"),
    },
)
