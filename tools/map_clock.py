"""The clock lab (map CLOCK): a pulse that laps through hung doors. MAP=CLOCK ./run.sh

An engine test for MAP18's two clocks (PLAN.md, "MAP18: the clock
department" and "The clock lab"): the metronome (a pulse laps a corridor
through a hung Pair; each lap it strikes a contact; a gate stays up while
the beat is fast enough) and the relay run (a lever, a far shutter up for
some seconds).

The gallery is one hall 2048 long, x 0..2048, with two lanes along it.
Frames on one line along a corridor are walls to each other: a frame facing
east stands in the way of every longer loop on its line. So the nearer
frames stand on piers, and lane A's pier has a frame on both faces: a Pair
hung in those two makes the pier something a pulse flies through.
  lane A (y 32..96): frame 111 in the west end wall, the pier at x 880..1024
    (frame 112 on its west face, 113 on its east face), frame 114 in the
    east end wall. 113 and 114 are 1024 apart; 111 and 114 are 2048 apart,
    with the other Pair hung in 112 and 113.
  lane B (y 192..256): frame 115 on a pier's east face at x 1536, frame 116
    in the east end wall: 512 apart.
A line across the whole hall at x 1800 is the contact (it is in every loop):
a pulse crossing it sets off the AjarContact (Thing_Activate), which tells
the metronome. The gate in the north wall (x 600..664) is the metronome's;
behind it the lever room, with the relay lever (5 seconds) for the shutter in
the north wall at x 1600..1664, behind which is the night room. The lamp
beside the gate flashes on each beat. Two emitters, one a lane, at x 1700,
fire east; their buttons are on the south wall (A at x 1600, B at 1680).
RED's far side is at the west end of the range, south of the hall: a pulse
through RED comes out there flying east.
Both Pairs and RED lean at the west end. The checks are
src/zscript/clock.zs (MODE=1..7 tools/smoke.sh).
"""
import ajarmap
from ajarmap import RED, TEAL, ORANGE, far_id, recess
from udmf import Map, rect

m = Map()
EMITTER_T, CONTACT_T = 20110, 20111
EMIT_A, EMIT_B, CONTACT_TID = 1101, 1102, 1110
GATE_TAG, LAMP_TAG = 610, 611
RELAY_SECONDS = 5
HALL, BACK, RANGE = 0xE0E8F0, 0xFFE8C8, 0xE8FFE0
CEIL = 192

# --- the gallery, in bands so that the piers stand in it ---------------------
for x1, x2, gaps in ((0, 880, ()), (880, 1024, ((32, 96),)), (1024, 1472, ()),
                     (1472, 1536, ((192, 256),)), (1536, 1800, ()), (1800, 2048, ())):
    y = 0
    for g1, g2 in gaps + ((384, 384),):
        if g1 > y:
            m.sector(rect(x1, y, x2, g1), ceil=CEIL, color=HALL)
        y = g2


def frame(a, b, out, n):
    recess(m, a, b, out, 0, n, 201, color=HALL)


frame((0, 32), (0, 96), (-1, 0), 111)          # lane A, west end
frame((880, 32), (880, 96), (1, 0), 112)       # lane A, the pier's west face
frame((1024, 32), (1024, 96), (-1, 0), 113)    # lane A, the pier's east face
frame((2048, 32), (2048, 96), (1, 0), 114)     # lane A, east end
frame((1536, 192), (1536, 256), (-1, 0), 115)  # lane B, its pier's east face
frame((2048, 192), (2048, 256), (1, 0), 116)   # lane B, east end

# the contact: a pulse that crosses x 1800 (either way) sets off the AjarContact
m.line((1800, 0), (1800, 384), special=130, args=(CONTACT_TID,), missilecross=True, repeatspecial=True)
m.thing(1800, 352, CONTACT_T, id=CONTACT_TID, args=(GATE_TAG, 70, LAMP_TAG))

# the emitters, one a lane, and their buttons on the south wall
for tid, y, x in ((EMIT_A, 64, 1600), (EMIT_B, 224, 1680)):
    m.thing(1700, y, EMITTER_T, angle=0, id=tid, args=(20, 0))
    m.cut((x, 0), (x + 64, 0))
    m.line((x, 0), (x + 64, 0), special=130, args=(tid,), playeruse=True, repeatspecial=True,
           mid="AJEXIT", exact=True, id=tid)

# --- the gate, the lever room and the relay lever ---------------------------
m.sector(rect(568, 400, 696, 528), ceil=128, color=BACK)                 # the lever room
m.sector(rect(600, 384, 664, 400), ceil=0, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF",
         light=160, id=GATE_TAG)
for p, q in (((600, 384), (600, 400)), ((664, 384), (664, 400))):
    m.line(p, q, mid="AJTRIM", dontpegbottom=True)
ajarmap.lever(m, (600, 528), (664, 528), RELAY_SECONDS, line_id=320)
# the lamp: a lit niche beside the gate that flashes on each beat
m.sector(rect(720, 384, 752, 400), floor=64, ceil=96, light=96, ftex="AJTRIMF", ctex="AJTRIMF",
         wall="AJTRIM", id=LAMP_TAG)

# --- the relay shutter and the night room -----------------------------------
m.sector(rect(1568, 400, 1696, 528), ceil=128, color=BACK)               # the night room
ajarmap.shutter(m, (1600, 384), (1664, 384), (0, 1), 0, line_id=321)

# --- the range: RED's far side, and a straight run east from it -------------
m.sector(rect(0, -256, 1024, -128), ceil=CEIL, color=RANGE)
recess(m, (0, -224), (0, -160), (-1, 0), 0, far_id(RED), 111, far_colour=RED, color=RANGE)

# --- the player and the doors, at the west end ------------------------------
m.thing(400, 250, 1, angle=0)
ajarmap.pair(m, TEAL, (120, 330, 270), (180, 330, 270))
ajarmap.pair(m, ORANGE, (240, 330, 270), (300, 330, 270))
ajarmap.door(m, RED, 360, 330, angle=270)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
