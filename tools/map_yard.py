"""The yard lab (map YARD): a COMMON PLACE that the three parts go through,
each on its own level, open to the sky (PLAN.md, "MAP33: the yard in the
middle, on three levels, as decided" and "The yard lab"; the engine is
src/zscript/common.zs with third.zs). MAP=YARD ./run.sh; the tests are
MAP=YARD MODE=1 to 3 tools/smoke.sh (src/zscript/yardtest.zs).

THIRD's and LAST's skeleton: the start room S with boxes 2 and 3 looking into
it, three short parts, each with its supplies at its start (a shotgun, a
chaingun, a rocket launcher, plenty of ammunition, a blue armour), the yard in
the middle of every part's way, and its own end room beyond: plate 1 and
time door 1 (E1), plate 2, time door 2 and a plate that winds on (E2), the
exit door and a plate that winds on (E3).

The yard: 768 wide (x 1536..2304) and 1216 long (y 0..1216) of floor at
-128, under the sky.
- Part 2 (green) crosses the floor: in from the west down stairs (y
  640..768), out on the east side through its way (a shutter) up stairs (y
  192..320). Four octagonal pumps on the floor, 96 high: cover.
- Part 1 (yellow): the north ledge, 128 deep at 0, along the north rim; in
  from the north at its east end, its way on (a shutter) in the east wall
  beside it. The ledge is a dead end to the west, with ammunition there.
- Part 3 (red): the south ledge, 128 deep at -64, along the south rim;
  likewise in from the south at its east end, its way on in the east wall.
- Railings (ajarthird.rim) along both ledges: players stop, shots, sight
  and flyers pass. Every way out of the yard is closed to monsters.
The groups (all skills): part 2's on the floor, four demons, two hell
knights and two imps (all seen fallen in go 1) and two cacodemons over it;
part 1's three cacodemons and a pain elemental, part 3's three cacodemons,
each over the middle of the floor.
"""
import ajarmap
import ajartime
import ajarthird
from udmf import Map, rect

m = Map()
P1 = 0xF0E8C8       # part 1's rooms, yellowish
P2 = 0xD8ECD8       # part 2's, greenish
P3 = 0xF0D8D4       # part 3's, reddish
YARDC = 0xE0DCD4    # the yard

PLACE = 3388        # the yard's own sectors (part 2's stairs in, the pumps' tops): ajarthird.common
L1, L2, L3 = (ajarthird.level_tag(k) for k in (1, 2, 3))     # the north ledge, the floor, the south ledge
WAY1, WAY2, WAY3 = 3381, 3382, 3383                           # each part's way on from its level (shutters)
EXIT = 3384         # the exit door in E3
OUT = 3385          # the room behind it
SKY = 384           # the yard's sky
FL = -128           # its floor
YX1, YX2, YY1, YY2 = 1536, 2304, 0, 1216                      # the floor's box


def supplies(x, y):
    """A shotgun, a chaingun, a rocket launcher, plenty of ammunition, a
    blue armour: a row of things from x, y eastwards and one row north."""
    for i, kind in enumerate([2001, 2002, 2003, 2019]):
        m.thing(x + 28 * i, y, kind, angle=90)
    for i, kind in enumerate([2049, 2049, 2048, 2048, 2048, 2046, 2046, 2046]):
        m.thing(x + 16 * i, y + 40, kind, angle=90)


# --- part 1 ----------------------------------------------------------------------
S = m.sector(rect(576, 1088, 960, 1472), ceil=192, light=200, color=P1)
m.thing(768, 1280, 1, angle=0)
supplies(624, 1380)
m.sector(rect(960, 1408, 2176, 1472), ceil=128, light=190, color=P1)         # C1, east
m.sector(rect(2176, 1344, 2272, 1472), ceil=128, light=190, color=P1)        # ... and south, onto the ledge's east end
m.line((2176, 1344), (2272, 1344), blockmonsters=True)
LEDGE1 = m.sector(rect(YX1, YY2, YX2, YY2 + 128), floor=0, ceil=SKY, ctex="F_SKY1", light=210, color=P1, wall="AJBRICK", id=L1)
for i, kind in enumerate([2048, 2048, 2046, 2046]):                          # at the dead end
    m.thing(1568 + 24 * i, 1312, kind, angle=0)
ajartime.shutter(m, (YX2, 1232), (YX2, 1328), (1, 0), 0, WAY1, nomonsters=True, color=P1)
ajarthird.way(m, 2280, 1300, 1, WAY1)
m.sector(rect(2320, 1232, 2560, 1328), ceil=128, light=190, color=P1)        # to E1
E1 = m.sector(rect(2560, 1152, 2816, 1408), ceil=192, light=210, color=P1)
ajarthird.plate(m, 2688, 1280, 1)
ajarthird.time_door_at(m, 1, (2816, 1248), (2816, 1312), (1, 0), 0, color=P1)

# --- part 2 ----------------------------------------------------------------------
ajartime.glass(m, (656, 1088), (768, 1088), (0, -1), 0)
BOX2 = ajarthird.box(m, 2, rect(640, 912, 784, 1072), ceil=160, light=210, color=P2)
ajarthird.box_door_at(m, 2, (640, 960), (640, 1024), (-1, 0), 0, color=P2)
m.sector(rect(608, 704, 816, 912), ceil=160, light=200, color=P2)            # R2
supplies(624, 730)
m.sector(rect(816, 640, 1280, 768), ceil=128, light=190, color=P2)           # C2
m.line((1280, 640), (1280, 768), blockmonsters=True)
ajarmap.stairs(m, (1280, 640), (1280, 768), (1, 0), 0, FL, steps=8, depth=32, ceil=160, light=200, color=YARDC, id=PLACE)
# the floor, round the pumps
PUMPS = [(1664, 256, 1792, 384), (2048, 448, 2176, 576), (1664, 896, 1792, 1024), (2048, 896, 2176, 1024)]
ajarmap.shaped(m, (YX1, YY1, YX2, YY2), [(ajarmap.octagon(*p, 40), dict(floor=FL + 96, side="AJBOLT", id=PLACE)) for p in PUMPS],
               floor=FL, ceil=SKY, ctex="F_SKY1", light=210, color=YARDC, wall="AJBRICK", id=L2)
ajartime.shutter(m, (YX2, 192), (YX2, 320), (1, 0), FL, WAY2, nomonsters=True, color=P2)
ajarthird.way(m, 2280, 300, 2, WAY2)
ajarmap.stairs(m, (2320, 192), (2320, 320), (1, 0), FL, -FL, steps=8, depth=32, ceil=160, light=190, color=P2)
m.sector(rect(2576, 192, 2640, 320), ceil=128, light=190, color=P2)
E2 = m.sector(rect(2640, 128, 2896, 384), ceil=192, light=210, color=P2)
ajarthird.plate(m, 2768, 256, 2)
ajarthird.wind(m, 2894, 160, 180)
ajarthird.time_door_at(m, 2, (2896, 224), (2896, 288), (1, 0), 0, color=P2)

# --- part 3 ----------------------------------------------------------------------
ajartime.glass(m, (576, 1184), (576, 1296), (-1, 0), 0)
BOX3 = ajarthird.box(m, 3, rect(400, 1168, 560, 1312), ceil=160, light=210, color=P3)
ajarthird.box_door_at(m, 3, (448, 1312), (512, 1312), (0, 1), 0, color=P3)
m.sector(rect(400, 960, 560, 1168), ceil=160, light=200, color=P3)           # R3
supplies(424, 984)
m.sector(rect(448, -352, 512, 960), ceil=128, light=180, color=P3)           # C3, south
m.sector(rect(512, -352, 2272, -288), ceil=128, light=170, color=P3)         # ... and east
ajarmap.stairs(m, (2176, -288), (2272, -288), (0, 1), 0, -64, steps=4, depth=40, ceil=128, light=180, color=P3)   # ... and north, down
m.line((2176, -128), (2272, -128), blockmonsters=True)
LEDGE3 = m.sector(rect(YX1, YY1 - 128, YX2, YY1), floor=-64, ceil=SKY, ctex="F_SKY1", light=210, color=P3, wall="AJBRICK", id=L3)
for i, kind in enumerate([2048, 2048, 2046, 2046]):                          # at the dead end
    m.thing(1568 + 24 * i, -64, kind, angle=0)
ajartime.shutter(m, (YX2, -112), (YX2, -16), (1, 0), -64, WAY3, nomonsters=True, color=P3)
ajarthird.way(m, 2280, -40, 3, WAY3)
m.sector(rect(2320, -112, 2560, -16), floor=-64, ceil=64, light=190, color=P3)                 # to E3
E3 = m.sector(rect(2560, -400, 2816, -16), floor=-64, ceil=128, light=210, color=P3)
ajarthird.wind(m, 2814, -60, 180)
ajartime.shutter(m, (2816, -272), (2816, -208), (1, 0), -64, EXIT)
m.sector(rect(2832, -304, 2960, -176), floor=-64, ceil=64, light=220, color=P3, id=OUT)
m.sector(rect(2960, -304, 3024, -176), floor=-64, ceil=64, light=230, color=P3, ftex="AJTRIMF")
m.line((2960, -304), (2960, -176), special=243, playercross=True)
m.line((3024, -304), (3024, -176), mid="AJEXIT", exact=True)

# --- the yard: its rims, the place, the groups ---------------------------------------
ajarthird.rim(m, (YX1, YY2), (YX2, YY2))
ajarthird.rim(m, (YX1, YY1), (YX2, YY1))
ajarthird.common(m, 1920, 1100, PLACE)
WALKS = {3002, 69, 3001}
# (part, kind, x, y, angle, z over the floor, seen fallen)
GROUPS = [(2, 3002, 1600, 520, 0, 0, True), (2, 3002, 1880, 300, 90, 0, True), (2, 3002, 1960, 760, 180, 0, True),
          (2, 3002, 2240, 1100, 180, 0, True), (2, 69, 1940, 520, 180, 0, True), (2, 69, 1600, 1120, 270, 0, True),
          (2, 3001, 2240, 700, 180, 0, True), (2, 3001, 1880, 1120, 270, 0, True),
          (2, 3005, 1856, 896, 180, 200, False), (2, 3005, 1984, 960, 180, 200, False),
          (1, 3005, 1792, 640, 90, 192, False), (1, 3005, 1920, 704, 90, 192, False), (1, 3005, 2048, 640, 90, 192, False),
          (1, 71, 1920, 576, 90, 192, False),
          (3, 3005, 1760, 448, 270, 128, False), (3, 3005, 1904, 384, 270, 128, False), (3, 3005, 2000, 416, 270, 128, False)]
for part, kind, x, y, a, z, f in GROUPS:
    ajarthird.comer(m, x, y, part, kind, a, z, fallen=f, skill=1)
ajarthird.third(m, 768, 1200, EXIT, OUT, (300, -500, 3100, 1600))

# no part is joined to another on foot (glass and the rims are not ways): from S, box 2 and box 3
PARTS = ajarthird.apart(m, {1: S, 2: BOX2, 3: BOX3})
assert LEDGE1 in PARTS[1] and LEDGE3 in PARTS[3] and E1 in PARTS[1] and E2 in PARTS[2] and E3 in PARTS[3]
TAGS = {i: s["id"] for i, s in enumerate(m.sectors)}
assert {i for i, t in TAGS.items() if t == L2} <= PARTS[2]
# each level's sectors tagged: the ledges, and the floor all round the pumps
assert TAGS[LEDGE1] == L1 and TAGS[LEDGE3] == L3 and sum(1 for t in TAGS.values() if t == L2) >= 4


def sector_at(x, y):
    for i, poly in enumerate(m.polys):
        if ajarmap._inside((x + 0.5, y + 0.5), poly):
            return i
    return None


# a comer that walks stands on the floor's level, clear of the pumps (by its radius and more); a flyer over the floor
for part, kind, x, y, a, z, f in GROUPS:
    s = sector_at(x, y)
    assert s is not None and TAGS[s] == L2, (kind, x, y)
    if kind in WALKS:
        assert all(TAGS.get(sector_at(x + dx, y + dy)) == L2 for dx in (-40, 0, 40) for dy in (-40, 0, 40)), (kind, x, y)
# the yard is closed to monsters: every way out blocks them (the rims do not: flyers cross between the levels)
assert ajarthird.sealed(m, {PLACE, L1, L2, L3}) >= 5

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
