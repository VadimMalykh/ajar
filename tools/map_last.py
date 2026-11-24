"""The last fight lab (map LAST): three selves of the player fight one fight
together. THIRD's structure without its middle: three short parts that meet
only at the last hall L, where each part ends on a stand over L's floor.
MAP=LAST ./run.sh; the tests are MAP=LAST MODE=1 to 4 tools/smoke.sh. See
src/zscript/last.zs (the engine's rules for a last hall, with third.zs) and
PLAN.md, "The last fight lab".

Part 1 (yellow): the start room S (every weapon, plenty of ammunition, a blue
armour), a corridor east to stand 1 on L's north side: plate 1, time door 1.
Part 2 (green): box 2 south of S (glass onto S), the supply room R2 behind
it, a corridor to stand 2 on L's west side: plate 2, time door 2, a plate
that winds on.
Part 3 (red): box 3 west of S (glass onto S), the supply room R3, a long
corridor round to stand 3 on L's south side: the gate in its railing (the
alarm opens it), steps down to L's floor, and a plate that winds on. The
exit door is in L's east wall: the third self crosses about 900 units of
floor to it.
L: 1024 x 1024, its floor 96 under the stands, which are open to it along
their whole fronts behind railings. Its guards come at the alarm: two
mancubi on pedestals, two revenants in bays of the east wall beside the exit
door, two cacodemons over the middle, four demons and two hell knights on
the floor, among four low blocks.
"""
import ajarmap
import ajartime
import ajarthird
from udmf import Map, rect

m = Map()
P1 = 0xF0E8C8       # part 1's rooms, yellowish
P2 = 0xD8ECD8       # part 2's, greenish
P3 = 0xF0D8D4       # part 3's, reddish
HALL = 0xD8D4CC     # the last hall

HALLT = 3350        # the last hall's sectors: floor, pedestals, bays, blocks, the steps
GATE = 3352         # stand 3's gate (the alarm opens it)
EXIT = 3353         # the exit door in L's east wall
OUT = 3354          # the room behind it
FL = -96            # L's floor (the stands are at 0)
LC = 320            # L's ceiling
ST = [ajarthird.stand_tag(k) for k in (1, 2, 3)]


def stand(k, box, pillar, **look):
    """Stand k: the rectangle `box` less a solid pillar."""
    return [m.sector(rect(*r), floor=0, ceil=192, light=200, id=ST[k - 1], **look) for r in ajarthird.tiles(*box, [pillar])]


# --- part 1 ----------------------------------------------------------------------
S = m.sector(rect(576, 1088, 960, 1472), ceil=192, light=200, color=P1)
m.thing(768, 1280, 1, angle=0)


def supplies(x, y):
    """Every weapon of the fight, plenty of ammunition, a blue armour: a row of
    things from x, y eastwards and one row north."""
    for i, kind in enumerate([2001, 2002, 2003, 2004, 2019]):
        m.thing(x + 28 * i, y, kind, angle=90)
    for i, kind in enumerate([2049, 2049, 2048, 2048, 2046, 2046, 17, 17]):
        m.thing(x + 16 * i, y + 40, kind, angle=90)


supplies(624, 1380)
m.sector(rect(960, 1120, 1344, 1184), ceil=128, light=190, color=P1)        # C1
STAND1 = stand(1, (1344, 1024, 1728, 1216), (1440, 1088, 1504, 1152), color=P1)
ajarthird.plate(m, 1600, 1088, 1)
ajarthird.time_door_at(m, 1, (1600, 1216), (1664, 1216), (0, 1), 0, color=P1)

# --- part 2 ----------------------------------------------------------------------
ajartime.glass(m, (656, 1088), (768, 1088), (0, -1), 0)
BOX2 = ajarthird.box(m, 2, rect(640, 912, 784, 1072), ceil=160, light=210, color=P2)
ajarthird.box_door_at(m, 2, (640, 960), (640, 1024), (-1, 0), 0, color=P2)
m.sector(rect(608, 704, 816, 912), ceil=160, light=200, color=P2)            # R2
supplies(624, 730)
m.sector(rect(752, 592, 816, 704), ceil=128, light=190, color=P2)            # C2
m.sector(rect(752, 528, 832, 592), ceil=128, light=190, color=P2)
STAND2 = stand(2, (832, 320, 1024, 704), (896, 576, 960, 640), color=P2)
ajarthird.plate(m, 960, 512, 2)
ajarthird.time_door_at(m, 2, (832, 448), (832, 384), (-1, 0), 0, color=P2)
ajarthird.wind(m, 900, 702, 270)

# --- part 3 ----------------------------------------------------------------------
ajartime.glass(m, (576, 1184), (576, 1296), (-1, 0), 0)
BOX3 = ajarthird.box(m, 3, rect(400, 1168, 560, 1312), ceil=160, light=210, color=P3)
ajarthird.box_door_at(m, 3, (448, 1312), (512, 1312), (0, 1), 0, color=P3)
m.sector(rect(400, 960, 560, 1168), ceil=160, light=200, color=P3)           # R3
supplies(424, 984)
m.sector(rect(448, -160, 512, 960), ceil=128, light=180, color=P3)           # C3, south
m.sector(rect(512, -160, 1152, -96), ceil=128, light=170, color=P3)          # ... and east
STAND3 = stand(3, (1152, -192, 1536, 0), (1408, -128, 1472, -64), color=P3)     # (its pillar 64 off the east wall: it was 32, a slot)
ajarthird.wind(m, 1534, -160, 180)
# the gate in stand 3's railing, and the steps down behind it to L's floor
ajartime.shutter(m, (1280, 0), (1408, 0), (0, 1), 0, GATE, nomonsters=True, color=P3)
ajarmap.stairs(m, (1280, 16), (1408, 16), (0, 1), 0, FL, steps=6, depth=16, ceil=LC, light=170, color=HALL, id=HALLT)

# --- the last hall L ---------------------------------------------------------------
PEDESTALS = [(1600, 736, 1792, 928), (1792, 64, 1984, 256)]                 # the mancubi's, 72 high
BAYS = [(2048, 448, 2112, 576), (2048, 832, 2112, 960)]                     # the revenants', 72 high
CG_BAYS = [(960, 832, 1024, 960), (1600, -64, 1728, 0)]                     # the chaingunners', 72 high: west wall, south wall
BLOCKS = [(1376, 256, 1504, 320), (1632, 224, 1696, 352), (1664, 496, 1792, 560), (1920, 464, 1984, 592)]   # cover, 64 high
STEPS = (1280, 0, 1408, 112)                                                # the gate and the steps
GREEN = 0x70F070    # the floor where a walking guard of wave 2 comes
RED = 0xFF6060      # ... of wave 3

# the guards (all skills: the lab's cast): (kind, x, y, angle, z over the floor, wave)
GUARDS = [(67, 1696, 832, 225, 0, 1), (67, 1888, 160, 135, 0, 1),           # wave 1, at the alarm: mancubi on the pedestals,
          (66, 2080, 512, 180, 0, 1), (66, 2080, 896, 180, 0, 1),           # revenants in the east bays,
          (65, 992, 896, 0, 0, 1), (65, 1664, -32, 90, 0, 1),               # chaingunners in the west and the south bay
          (3005, 1480, 520, 90, 200, 2), (3005, 1620, 700, 180, 200, 2),    # wave 2, plate 2: cacodemons over the middle,
          (69, 1480, 860, 270, 0, 2), (69, 1200, 600, 0, 0, 2),             # hell knights on the floor
          (3003, 1952, 704, 180, 0, 3),                                     # wave 3, the third self on the floor: a baron at the exit door,
          (3002, 1888, 416, 180, 0, 3), (3002, 2000, 896, 180, 0, 3),       # demons
          (3002, 1728, 640, 180, 0, 3), (3002, 1560, 440, 270, 0, 3)]
WALKS = {69, 3003, 3002}
PATCHES = [((x - 32, y - 32, x + 32, y + 32), GREEN if w == 2 else RED) for k, x, y, a, z, w in GUARDS if w > 1 and k in WALKS]

for r in ajarthird.tiles(1024, 0, 2048, 1024, PEDESTALS + BLOCKS + [STEPS] + [p for p, c in PATCHES]):
    m.sector(rect(*r), floor=FL, ceil=LC, light=170, color=HALL, id=HALLT)
for p, c in PATCHES:
    m.sector(rect(*p), floor=FL, ceil=LC, light=170, color=c, id=HALLT)
for p in PEDESTALS:
    m.sector(rect(*p), floor=FL + 72, ceil=LC, light=180, color=HALL, side="AJBOLT", id=HALLT)
for b in BAYS + CG_BAYS:
    m.sector(rect(*b), floor=FL + 72, ceil=FL + 200, light=160, color=HALL, side="AJBOLT", id=HALLT)
for b in BAYS:
    m.line((b[0], b[1]), (b[0], b[3]), blockmonsters=True)
m.line((CG_BAYS[0][2], CG_BAYS[0][1]), (CG_BAYS[0][2], CG_BAYS[0][3]), blockmonsters=True)
m.line((CG_BAYS[1][0], CG_BAYS[1][3]), (CG_BAYS[1][2], CG_BAYS[1][3]), blockmonsters=True)
for b in BLOCKS:
    m.sector(rect(*b), floor=FL + 64, ceil=LC, light=180, color=HALL, side="AJBOLT", id=HALLT)
# the railings: each stand's whole front (stand 3's either side of its gate)
ajarthird.railing(m, (1344, 1024), (1728, 1024))
ajarthird.railing(m, (1024, 320), (1024, 704))
ajarthird.railing(m, (1152, 0), (1280, 0))
ajarthird.railing(m, (1408, 0), (1536, 0))
# the exit door in the east wall, at floor level, and the way out
ajartime.shutter(m, (2048, 640), (2048, 768), (1, 0), FL, EXIT, color=P3)
m.sector(rect(2064, 640, 2192, 768), floor=FL, ceil=FL + 128, light=220, color=P3, id=OUT)
m.sector(rect(2192, 640, 2256, 768), floor=FL, ceil=FL + 128, light=230, color=P3, ftex="AJTRIMF")
m.line((2192, 640), (2192, 768), special=243, playercross=True)
m.line((2256, 640), (2256, 768), mid="AJEXIT", exact=True)

for kind, x, y, a, z, w in GUARDS:
    ajarthird.guard(m, x, y, kind, a, z, wave=w)
# wave 1 stands where it cannot leave: on a pedestal or in a bay, 64 or more over the floor
STANDING = PEDESTALS + BAYS + CG_BAYS
assert all(any(p[0] + 20 <= x <= p[2] - 20 and p[1] + 20 <= y <= p[3] - 20 for p in STANDING) for k, x, y, a, z, w in GUARDS if w == 1)
# a walking guard of a later wave stands in the middle of its patch, clear of every island
assert all(not (p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]) for p, c in PATCHES for q in PEDESTALS + BLOCKS + [STEPS])
ajarthird.last(m, 1536, 900, HALLT, gate=GATE)
ajarthird.third(m, 1536, 960, EXIT, OUT, (300, -300, 2400, 1600))

# no part is joined to another on foot (glass, the railings are not ways):
# from S, box 2 and box 3. Part 3 reaches the hall, by the gate and the steps,
# and the exit; stands 1 and 2 are not reached from it.
PARTS = ajarthird.apart(m, {1: S, 2: BOX2, 3: BOX3})
assert set(STAND1) <= PARTS[1] and set(STAND2) <= PARTS[2] and set(STAND3) <= PARTS[3]
HALL_SECS = {i for i, s in enumerate(m.sectors) if s["id"] == HALLT}
assert HALL_SECS <= PARTS[3]
# every stand's railing is closed to monsters (stand 3's gate is a sector of its own)
RAILS = [ajarthird.closed(m, t, HALLT) for t in ST]
assert all(RAILS), RAILS

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
