"""Act 1, level 5: "Lost Property" (MAP05).

A railway terminus. There is no way out to find: you build it. Off platform
2 is the night room every level has ended in, but its two ends are not
joined. VIOLET's far side is in one of them and an empty frame in the
other. Hang VIOLET in that frame and the room opens onto itself.

The catch: VIOLET, hung anywhere, takes you to the night room, and then it
is behind you, not in your hands. It has to be carried there, and the only
way to platform 2 with a door is over the bridge (RED) and down. The
night room's own door is bolted on the inside, so the first visit is by
VIOLET, or by luck.

What is new:

- Building the way out (ajarmap.way_home).
- Stray doors (ajarmap.stray): one by the start, two in the lost property
  office, one in the loft. Each opens once, for five seconds, onto one of
  six places: the night room, the gallery, the lamp room, the parcels
  office, the engine shed, the kiosk.
- The nailer, in the engine shed. YELLOW hangs there, and is nailed there
  as soon as it sees you. The gate from the yard to the concourse is bolted
  on the yard side; once it is open the nailer comes out to work.
- A turnstile is a squeeze: platform 2 is two steps from the concourse, for
  anyone with empty hands. BLUE leans just beyond it.

Places. The concourse (start), platform 1 and the tracks are one place to
walk about in. Off platform 1: the waiting room (RED), the lost property
office (keys 1 and 2; key 3), behind it the lockers (a squeeze; PINK) and
the lamp room. A train stands at platform 2; you can run along its roof
from the bridge. The bridge (RED's far side) crosses the east end, with
gaps in its rail over platform 1, the train, platform 2 and the yard, and
the signal box (key 1, GREEN, a lever) off it. The gallery (GREEN's far
side; key 2) looks down into the concourse. Off platform 2: the parcels
office (BLUE's far side; key 4), bolted inside, and the night room. North
of everything the goods yard, the engine shed, the loft over it (YELLOW's
far side) and the station master's office (keys 3 and 4): VIOLET.

Secrets: the lockers and PINK's store; the lamp room (the lever in the
signal box, or a Stray door); the kiosk in the concourse (shoot its bell
through the bars, or a Stray door); a nook off the gallery.
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, PINK, far_id
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


PIT, GALLERY, BRIDGE, ROOF, LOFT = -64, 192, 160, 112, 160
WARM, GOLD, SKY, LEAF, PLUM, ROSE = 0xFFD8CC, 0xFFE890, 0xA8C0FF, 0xD4F4D0, 0xD0A0FF, 0xFFC0DC
OPEN = dict(ceil=512, ctex="F_SKY1", wall="AJBRICK")
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
LOW = dict(ceil=128, ctex="AJBOARD")                  # a canopy, a porch
SEAT = dict(ftex="AJSOFA", side="AJSOFA")
WOOD = dict(ftex="AJWOOD", side="AJWOOD")
GATE, NIGHT_BOLT, PARCELS_BOLT, LAMPS, KIOSK = 401, 402, 403, 404, 405
NX, NY = 1280, 1296                                   # the night room's south-west corner


def rail(*runs):
    for a, b in runs:
        m.cut(a, b)             # a railing ends where it says, not at the next corner of a room
        m.line(a, b, **RAIL)


def bars(a, b, out, floor):
    """A barred opening in a 16 thick wall: to look and shoot through."""
    c = (a[0] + out[0] * 16, a[1] + out[1] * 16)
    d = (b[0] + out[0] * 16, b[1] + out[1] * 16)
    m.sector([a, b, d, c], floor=floor + 32, ceil=floor + 96, light=170, wall="AJBRICK",
             ftex="AJTRIMF", ctex="AJTRIMF")
    m.line(a, b, mid="AJWIN", midboth=True, blocking=True)


# === the concourse, platform 1, the tracks ====================================
ajarmap.fitted(m, (0, 0, 512, 1600), [
    ((0, 0, 512, 128), LOW),                                                 # the vestibule: start here
    ((224, 128, 288, 1536), dict(ftex="AJARCHF")),                           # the way through
    ((160, 1536, 352, 1600), LOW),                                           # before the yard gate
    ((448, 1280, 512, 1600), LOW),                                           # the arcade by the kiosk
    ((96, 640, 160, 896), dict(SEAT, floor=16)),                             # benches
    ((352, 640, 416, 896), dict(SEAT, floor=16)),
], floor=0, ceil=384, light=190, wall="AJBRICK", ftex="AJFLOOR")
recess((352, 0), (416, 0), (0, -1), 0, 101, 201)                             # frame in the vestibule

ajarmap.fitted(m, (512, 256, 2048, 512), [
    ((512, 256, 2048, 320), LOW),                                            # the canopy
    ((1920, 488, 1984, 512), dict(floor=PIT + 16)),                          # steps up from the tracks
    ((1920, 464, 1984, 488), dict(floor=PIT + 32)),
    ((1920, 440, 1984, 464), dict(floor=PIT + 48)),
    ((1200, 336, 1328, 368), dict(SEAT, floor=16)),
], floor=0, light=200, ftex="AJARCHF", **OPEN)
recess((864, 256), (928, 256), (0, -1), 0, 102, 201)                         # frame on platform 1

# the tracks, and the train at platform 2: its roof is a way along
ajarmap.fitted(m, (512, 512, 2048, 1024), [
    ((832, 816, 2048, 1008), dict(floor=ROOF, ftex="AJSTEEL", side="AJTRN")),
], floor=PIT, light=200, ftex="AJRAILS", **OPEN)

# --- off platform 1 -----------------------------------------------------------
# the waiting room: RED
ajarmap.fitted(m, (544, 16, 832, 240), [((544, 16, 576, 176), dict(SEAT, floor=16)),
                                        ((800, 16, 832, 176), dict(SEAT, floor=16))],
               ceil=128, light=170, color=WARM)
ajarmap.roomdoor(m, (656, 256), (720, 256), (0, -1), 0)
# the lost property office: two locks. A counter, and what nobody came back for
ajarmap.fitted(m, (960, 16, 1408, 240), [((960, 128, 1280, 160), dict(WOOD, floor=40)),
                                         ((1216, 16, 1312, 48), dict(WOOD, floor=64)),
                                         ((976, 16, 1072, 48), dict(WOOD, floor=64))],
               ceil=128, light=170, color=GOLD)
ajarmap.roomdoor(m, (1056, 256), (1120, 256), (0, -1), 0, keys="12", line_id=301)
# the lockers, through a hole behind the counter (secret): PINK hangs here
m.sector(rect(1424, 16, 1600, 240), ceil=112, light=140, color=ROSE, wall="AJSAFE", special=1024)
ajarmap.squeeze(m, (1408, 56), (1408, 104), (1, 0), 0)
recess((1600, 96), (1600, 160), (1, 0), 0, 106, 201, color=ROSE)
# the lamp room (secret): the signal box's lever opens it, or you come by Stray door
m.sector(rect(1696, 128, 1920, 240), ceil=112, light=150, wall="AJSAFE", special=1024)
m.sector(rect(1696, 16, 1920, 128), ceil=112, light=150, wall="AJSAFE")
ajarmap.bolted(m, (1776, 256), (1840, 256), (0, -1), 0, LAMPS, line_id=307)
ajarmap.unbolt(m, (1696, 128), (1920, 128), LAMPS)
ajarmap.stray_place(m, 2, (1920, 40), (1920, 104), (1, 0), 0)

# === above ======================================================================
# --- the gallery (GREEN's far side), along the concourse's west wall -------------
m.sector(rect(-256, 256, 0, 1280), floor=GALLERY, ceil=384, light=190, color=LEAF, wall="AJBRICK",
         ftex="AJBOARD")
rail(((0, 256), (0, 400)), ((0, 528), (0, 1280)))
recess((-256, 960), (-256, 1024), (-1, 0), GALLERY, far_id(GREEN), 101, far_colour=GREEN, color=LEAF)
m.sector(rect(-176, 1280, -80, 1376), floor=GALLERY, ceil=GALLERY + 96, light=110, wall="AJBRICK",
         ftex="AJBOARD", special=1024)                                       # a nook (secret)

# --- the bridge (RED's far side) across the east end, and the signal box ---------
ajarmap.fitted(m, (2048, 256, 2240, 2192), [((2176, 960, 2240, 1088), dict(ceil=BRIDGE + 128, ctex="AJBOARD"))],
               floor=BRIDGE, light=210, color=WARM, ftex="AJBOARD", **OPEN)
rail(((2048, 256), (2048, 352)), ((2048, 448), (2048, 848)), ((2048, 976), (2048, 1088)),
     ((2048, 1184), (2048, 1280)), ((2048, 1680), (2048, 1856)), ((2048, 1984), (2048, 2192)))
recess((2240, 544), (2240, 608), (1, 0), BRIDGE, far_id(RED), 101, far_colour=RED, color=WARM)
m.sector(rect(2256, 896, 2512, 1152), floor=BRIDGE, ceil=BRIDGE + 128, light=180, color=WARM)
ajarmap.roomdoor(m, (2240, 992), (2240, 1056), (1, 0), BRIDGE)
m.cut((2512, 992), (2512, 1056))
m.line((2512, 992), (2512, 1056), special=11, args=(LAMPS, 32), playeruse=True, mid="AJLEVR", exact=True,
       id=306)

# === platform 2 and what is off it ================================================
ajarmap.fitted(m, (528, 1024, 2048, 1280), [
    ((528, 1216, 2048, 1280), LOW),
    ((1600, 1184, 1728, 1216), dict(SEAT, floor=16)),
], floor=0, light=200, ftex="AJARCHF", **OPEN)
ajarmap.squeeze(m, (512, 1128), (512, 1176), (1, 0), 0)                      # the turnstile
bars((512, 1048), (512, 1112), (1, 0), 0)
recess((1088, 1280), (1152, 1280), (0, 1), 0, 104, 201)                      # frame on platform 2

# the parcels office (BLUE's far side): its door is bolted inside
m.sector(rect(752, 1296, 1056, 1392), ceil=128, light=160, color=SKY)
ajarmap.fitted(m, (752, 1392, 1056, 1552), [((784, 1504, 944, 1552), dict(WOOD, floor=48))],
               ceil=128, light=160, color=SKY)
ajarmap.bolted(m, (880, 1280), (944, 1280), (0, 1), 0, PARCELS_BOLT, line_id=303)
ajarmap.unbolt(m, (752, 1392), (1056, 1392), PARCELS_BOLT)
recess((1056, 1440), (1056, 1504), (1, 0), 0, far_id(BLUE), 101, far_colour=BLUE, color=SKY)

# the night room: VIOLET's far side at one end, the frame at the other. Its
# door onto the platform is bolted inside
ajarmap.way_home(m, NX, NY, VIOLET)
ajarmap.bolted(m, (NX + 128, 1280), (NX + 192, 1280), (0, 1), 0, NIGHT_BOLT, line_id=304)
ajarmap.unbolt(m, (NX, NY + 96), (NX + 320, NY + 96), NIGHT_BOLT)

# the kiosk (secret), seen through bars from the concourse: shoot its bell
m.sector(rect(528, 1312, 656, 1568), ceil=112, light=170, color=ROSE, wall="AJSAFE", special=1024)
bars((512, 1400), (512, 1464), (1, 0), 0)
ajarmap.bolted(m, (512, 1496), (512, 1560), (1, 0), 0, KIOSK)
m.cut((656, 1400), (656, 1464))
m.line((656, 1400), (656, 1464), special=11, args=(KIOSK, 32), impact=True, mid="AJTARG", exact=True)
ajarmap.stray_place(m, 5, (560, 1568), (624, 1568), (0, 1), 0, color=ROSE)

# === the goods yard ================================================================
ajarmap.fitted(m, (0, 1680, 1024, 2192), [
    ((192, 1680, 320, 1744), LOW),                                           # inside the gate
    ((400, 2128, 496, 2192), LOW),                                           # the station master's porch
    ((640, 1840, 768, 1968), dict(WOOD, floor=48)),                          # crates
    ((768, 1840, 832, 1904), dict(WOOD, floor=96)),
    ((96, 1936, 192, 2032), dict(WOOD, floor=48)),
], floor=0, light=200, ftex="AJPIT", **OPEN)
ajarmap.bolted(m, (224, 1600), (288, 1600), (0, 1), 0, GATE, thick=80, line_id=305)
# the engine shed: an engine, the nailer, and a frame with YELLOW in it
ajarmap.fitted(m, (1024, 1680, 1728, 2192), [
    ((1216, 1872, 1536, 2000), dict(floor=96, ftex="AJSTEEL", side="AJSTEEL")),
    ((1536, 1904, 1600, 1968), dict(floor=56, ftex="AJSTEEL", side="AJSTEEL")),
], floor=0, ceil=192, light=140, wall="AJBRICK", ftex="AJRAILS")
ajarmap.unbolt(m, (1024, 1680), (1024, 2192), GATE)
recess((1344, 2192), (1408, 2192), (0, 1), 0, 105, 201)                      # the shed's frame
ajarmap.stray_place(m, 4, (1120, 1680), (1184, 1680), (0, -1), 0)
m.sector(rect(1728, 1680, 2048, 2192), floor=0, light=200, ftex="AJPIT", **OPEN)

# the loft over the yard (YELLOW's far side)
m.sector(rect(1760, 2192, 2048, 2448), floor=LOFT, light=200, color=GOLD, ftex="AJBOARD", **OPEN)
rail(((1760, 2192), (1856, 2192)), ((1952, 2192), (2048, 2192)))
recess((1760, 2288), (1760, 2352), (-1, 0), LOFT, far_id(YELLOW), 101, far_colour=YELLOW, color=GOLD)

# the station master's office: two locks. VIOLET
ajarmap.fitted(m, (256, 2208, 640, 2464), [((320, 2368, 480, 2416), dict(WOOD, floor=40)),
                                           ((576, 2240, 640, 2368), dict(SEAT, floor=16))],
               ceil=128, light=175, color=PLUM)
ajarmap.roomdoor(m, (416, 2192), (480, 2192), (0, 1), 0, keys="34", line_id=302)

# === far sides that are places of their own =====================================
# the store (PINK's far side): no other way in (secret)
m.sector(rect(4000, 0, 4448, 384), ceil=160, light=150, color=ROSE, wall="AJSAFE", special=1024)
recess((4000, 160), (4000, 224), (-1, 0), 0, far_id(PINK), 101, far_colour=PINK, color=ROSE)

# --- doors and keys ----------------------------------------------------------
m.thing(256, 64, 1, angle=90)                                             # player start, in the vestibule
ajarmap.stray(m, 20, 64, angle=0)                                         # a Stray door by the start
ajarmap.stray(m, 1300, 220, angle=270)                                    # two in the lost property office
ajarmap.stray(m, 1380, 220, angle=270)
ajarmap.stray(m, 2030, 2420, angle=180)                                   # one in the loft
ajarmap.door(m, RED, 690, 30, angle=90)                                   # leaning in the waiting room
ajarmap.door(m, GREEN, 2490, 920, angle=180)                              # leaning in the signal box
ajarmap.door(m, BLUE, 548, 1080, angle=0)                                 # leaning beyond the turnstile
ajarmap.door(m, YELLOW, 1376, 2100, frame=105)                            # hanging in the shed
ajarmap.door(m, VIOLET, 610, 2440, angle=180)                             # leaning in the master's office
ajarmap.door(m, PINK, 1580, 128, frame=106)                               # hanging in the lockers
ajarmap.key(m, 1, 2460, 1120)                                             # the signal box
ajarmap.key(m, 2, -128, 300)                                              # south end of the gallery
ajarmap.key(m, 3, 1000, 200)                                              # behind the counter
ajarmap.key(m, 4, 800, 1470)                                              # the parcels office

ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, LODGER, NAILER = 3004, 9, 3001, 3002, 58, 20005, 20004
CHAINGUNNER, KNIGHT, BARON, REVENANT, SOUL, CACO, MANCUBUS, ARACHNO = 65, 69, 3003, 66, 3006, 3005, 67, 68
SHOTGUN, SUPER, CHAINGUN, LAUNCHER, PLASMA, SHELLS, SHELLBOX, CLIP, AMMOBOX, ROCKETS, ROCKETBOX, CELLS = (
    2001, 82, 2002, 2003, 2004, 2008, 2049, 2007, 2048, 2010, 2046, 17)
STIM, MEDIKIT, BONUS, HELMET, ARMOR, MEGA, SPHERE, BERSERK = 2011, 2012, 2014, 2015, 2018, 2019, 2013, 2023
CANDLE, CANDELABRA, LAMP, TECHLAMP = 34, 35, 2028, 86
TORCH_R, TORCH_G, TORCH_B = 46, 45, 55
POOL, BARREL = 24, 2035


def things(kind, *spots, angle=0, **k):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle, **k)


# the vestibule: a shotgun for anyone who came without one
things(SHOTGUN, (420, 100))
things(SHELLS, (460, 100), (460, 60))
things(STIM, (60, 110))
# the concourse: travellers. The lodger wakes when you are well into it
things(ZOMBIE, (120, 420), (400, 480), (256, 700), (120, 1100), (400, 1150), angle=270)
things(IMP, (60, 300), (460, 320), (60, 1450), (256, 1300), (128, 768), (384, 768), angle=270)
things(SERGEANT, (256, 520), (180, 980), (330, 980), angle=270)
things(DEMON, (256, 1150), (120, 1300), angle=270)
things(CACO, (256, 900), angle=270, ambush=True)
things(LODGER, (300, 1000), args=(300,))
things(LAMP, (24, 152), (488, 152), (24, 1576), (424, 1576))
things(MEDIKIT, (40, 1560))
things(SHELLS, (128, 620), (384, 620), (480, 1240))
things(CLIP, (256, 300), (256, 380))
things(STIM, (480, 560), (40, 900))
# the gallery: watching the concourse
things(CHAINGUNNER, (-60, 800), angle=0)
things(IMP, (-180, 500), (-180, 1100), (-60, 1200), angle=0)
things(SERGEANT, (-120, 340), angle=90)
things(TORCH_G, (-232, 936), (-232, 1048))
things(STIM, (-40, 1250))
things(ARMOR, (-128, 1340))                                                # in the nook
# platform 1
things(ZOMBIE, (700, 400), (1000, 440), (1500, 400), angle=180)
things(IMP, (840, 360), (1400, 460), (1800, 360), (2000, 300), angle=180)
things(SERGEANT, (1150, 420), (1700, 440), angle=180)
things(DEMON, (1300, 440), angle=180)
things(BARREL, (980, 290), (1560, 290))
things(LAMP, (600, 290), (1900, 290))
things(SHELLS, (1264, 420))
things(STIM, (1750, 290))
# the tracks: what lives between the rails
things(DEMON, (700, 600), (1100, 700), (1500, 600), (1900, 700), angle=180)
things(SPECTRE, (900, 640), (1300, 700), (1700, 640), (640, 900), (760, 960), angle=180)
things(SOUL, (1000, 560), (1600, 760), angle=180)
things(POOL, (1200, 620), (700, 800))
things(MEDIKIT, (560, 990))
things(SHELLBOX, (2000, 560))
# the waiting room: RED, and those still waiting
things(ZOMBIE, (620, 100), (760, 100), angle=90)
things(IMP, (690, 180), angle=90)
things(TORCH_R, (600, 200), (780, 200))
things(STIM, (590, 40))
# the lost property office: the clerks
things(CHAINGUNNER, (1100, 60), angle=90)
things(SERGEANT, (1000, 80), (1340, 80), angle=90)
things(IMP, (1160, 200), (1340, 180), angle=180)
things(CHAINGUN, (1140, 40))
things(AMMOBOX, (1180, 40))
things(MEDIKIT, (1380, 40))
things(CANDELABRA, (984, 232), (1392, 150))
# the lockers
things(IMP, (1500, 60), (1500, 200), angle=180)
things(HELMET, (1450, 220))
things(CANDLE, (1440, 30), (1580, 30))
# the store: left luggage nobody dares claim
things(LAUNCHER, (4380, 192))
things(ROCKETBOX, (4380, 140), (4380, 244))
things(MEGA, (4400, 340))
things(AMMOBOX, (4400, 40))
things(REVENANT, (4250, 100), (4250, 290), angle=180)
things(KNIGHT, (4130, 192), angle=180)
things(CANDELABRA, (4424, 24), (4424, 360))
# the lamp room
things(SPHERE, (1730, 60))
things(SHELLBOX, (1800, 40))
things(CELLS, (1860, 40))
things(LAMP, (1720, 216), (1896, 216))
things(SPECTRE, (1800, 190), angle=90)
# the train's roof
things(IMP, (1000, 912), (1300, 912), (1600, 912), angle=0)
things(SOUL, (1150, 860), (1450, 960), angle=0)
things(CLIP, (1900, 912))
things(BONUS, (900, 912), (940, 912), (980, 880))
# the bridge: snipers over the whole station
things(CHAINGUNNER, (2100, 700), (2100, 1500), angle=180)
things(IMP, (2180, 320), (2180, 1250), (2180, 1750), (2100, 2100), angle=180)
things(SERGEANT, (2140, 900), (2140, 1620), angle=180)
things(REVENANT, (2150, 2000), angle=270)
things(TORCH_R, (2216, 520), (2216, 632))
things(SUPER, (2200, 280))
things(SHELLS, (2160, 280), (2120, 280))
things(MEDIKIT, (2200, 1400))
# the signal box
things(SERGEANT, (2400, 960), angle=180)
things(ZOMBIE, (2440, 1080), (2330, 1100), angle=180)
things(TECHLAMP, (2290, 920))
things(STIM, (2290, 1120))
# platform 2
things(ZOMBIE, (700, 1150), (1000, 1100), (1500, 1150), angle=180)
things(IMP, (900, 1200), (1250, 1080), (1800, 1200), (1950, 1080), angle=180)
things(SERGEANT, (1200, 1180), (1700, 1100), angle=180)
things(KNIGHT, (1440, 1150), angle=180)
things(CACO, (1000, 1160), angle=180, ambush=True)
things(LAMP, (560, 1250), (2016, 1250))
things(SHELLS, (1664, 1240))
things(STIM, (620, 1040), (1900, 1250))
# the parcels office
things(DEMON, (840, 1340), (980, 1340), angle=270)
things(SERGEANT, (1000, 1520), angle=180)
things(TORCH_B, (1032, 1416), (1032, 1528))
things(SHELLBOX, (780, 1340))
things(MEDIKIT, (1020, 1320))
# the night room: someone has been waiting
things(REVENANT, (NX + 160, NY + 200), angle=270)
things(SERGEANT, (NX + 96, NY + 40), (NX + 224, NY + 40), angle=90)
# the kiosk
things(PLASMA, (592, 1440))
things(CELLS, (560, 1360), (624, 1360))
things(MEGA, (592, 1520))
# the yard: goods, and those unloading them
things(ZOMBIE, (300, 1800), (700, 1760), (500, 2050), (900, 2100), angle=270)
things(IMP, (60, 1740), (960, 1740), (60, 2140), (704, 1904), (800, 1872), (144, 1984), angle=270)
things(SERGEANT, (500, 1880), (860, 2000), (250, 2100), angle=270)
things(DEMON, (400, 1960), (900, 1850), angle=270)
things(CACO, (512, 1936), angle=270, ambush=True)
things(BARREL, (600, 1800), (840, 1960), (220, 1960))
things(LAMP, (24, 1704), (24, 2168), (1000, 1704), (1000, 2168))
things(MEDIKIT, (60, 1900))
things(SHELLBOX, (980, 2160))
things(BERSERK, (40, 2160))
things(ROCKETS, (700, 2160), (740, 2160))
# under the bridge
things(SERGEANT, (1800, 1760), (1960, 2100), angle=180)
things(IMP, (1900, 1800), (1800, 2040), angle=180)
things(KNIGHT, (1900, 1940), angle=180)
things(STIM, (2020, 1700))
# the engine shed: the nailer and its mates
things(NAILER, (1376, 2080), angle=270)
things(SPECTRE, (1100, 1800), (1100, 2100), (1650, 1800), (1650, 2100), angle=180)
things(DEMON, (1160, 1940), (1650, 1940), angle=180)
things(IMP, (1376, 1936), (1300, 1936), (1450, 1936), angle=180)                  # on the engine
things(SERGEANT, (1250, 2120), (1500, 2120), (1300, 1760), angle=180)
things(MANCUBUS, (1560, 1780), angle=180)
things(CANDLE, (1048, 1704), (1704, 1704), (1048, 2168), (1704, 2168))
things(AMMOBOX, (1680, 2160))
things(MEDIKIT, (1060, 2150))
# the loft
things(CHAINGUNNER, (1900, 2260), angle=270)
things(IMP, (1820, 2400), (2000, 2300), angle=270)
things(TORCH_R, (1784, 2264), (1784, 2376))
things(ARMOR, (1800, 2230))
things(ROCKETBOX, (2010, 2230))
# the station master's office: the master, on VIOLET, and deaf to the yard
things(BARON, (448, 2320), angle=270, ambush=True)
things(KNIGHT, (320, 2260), (560, 2420), angle=270, ambush=True)
things(TECHLAMP, (280, 2440), (616, 2232))
things(MEDIKIT, (280, 2232))

# The same level as a graph, for tools/solve.py. Keep in step with the above.
# "hall" is the concourse, platform 1, the tracks and the waiting room, and
# also the lamp room and the kiosk, which open from inside. a is the yard
# gate's bolt, b the night room's, c the parcels office's. The lockers, PINK
# and the store are left out: nothing there leaves, and nothing else needs it.
PUZZLE = dict(
    start="hall", goal="exit", names=ajarmap.NAMES, complete=True, home_frame=ajarmap.HOME,
    walk=[("gallery", "hall"), ("bridge", "hall"), ("bridge", "p2"), ("bridge", "yard"), ("p2", "hall"),
          ("hall", "p2", "", "squeeze"), ("p2", "hall", "", "squeeze"),          # the turnstile
          ("yard", "hall", "a"), ("hall", "yard", "a"),
          ("loft", "yard"),
          ("yard", "master", "34"), ("master", "yard", "34"),
          ("hall", "lostprop", "12"), ("lostprop", "hall", "12"),
          ("parcels", "p2", "c"), ("p2", "parcels", "c"),
          ("night", "p2", "b"), ("p2", "night", "b")],
    keys={"1": "bridge", "2": "gallery", "3": "lostprop", "4": "parcels",
          "a": "yard", "b": "night", "c": "parcels"},
    auto="abc",
    frames={101: "hall", 102: "hall", 104: "p2", 105: "yard", ajarmap.HOME: "night"},
    doors={
        RED: dict(home="bridge", lean="hall"),
        GREEN: dict(home="gallery", lean="bridge"),
        BLUE: dict(home="parcels", lean="p2"),
        YELLOW: dict(home="loft", frame=105),
        VIOLET: dict(home="night", lean="master"),
    },
    pool=["hall", "yard"],                 # the lamp room and the kiosk; the shed
    nailer=dict(zone=["yard", ("hall", "a")]),
)
