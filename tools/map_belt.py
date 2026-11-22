"""The belt lab (map BELT): conveyor belts through hung doors. MAP=BELT ./run.sh

An engine test for MAP17's goods dispatch: a belt (a scrolling floor,
ajarmap.belt) carries a crate (AjarCrate) into a frame, through whatever
door hangs there, and out of that door's far side onto the next belt. Four
rooms in a row, each with a door onto the hall along their south side, so
everything can be walked to:
  H, the hopper (the start; a crate on its belt): from BLUE's far side in
    its west wall to frame 101 in its east wall. All the doors lean here:
    RED, GREEN, BLUE and both TEAL leaves.
  P, the press: from RED's far side to frame 102. Half-way the belt goes
    through a wall by a hatch 40 high: a crate passes, the player does not.
  K, the kiln: from GREEN's far side, in its north wall (a frame's traveller
    comes out turned), south to a corner and east to frame 103.
  S, the scale: frame 104 (for a Pair leaf: no colour leads here), a short
    belt, and the scale, a plain floor where what rides stops.
An AjarStation on each room's belt stamps a crate that comes in with the
room's number: H 2, P 1, K 3, S 8 (the colours of the far sides that lead
in, TEAL for S). The checks are src/zscript/belt.zs (MODE=1..6 tools/smoke.sh).
"""
import ajarmap
from ajarmap import RED, GREEN, BLUE, TEAL, BELT_TAG, CURB_W, belt, recess, far_id
from udmf import Map, rect

m = Map()
CRATE_T, STATION_T = 20094, 20095
HCOL, PCOL, KCOL, SCOL, HALLC = 0xD8E8FF, 0xFFD8C8, 0xD8FFD0, 0xF0E0FF, 0xE8E8E8
TH, TP, TKV, TKH, TS = (BELT_TAG + i for i in range(1, 6))   # one tag a belt direction
Y0, Y1 = 160, 224          # the belts of H, P and K's last run lie between these


def strips(x1, x2, top, color):
    """A room's floor south and north of a belt along x from x1 to x2."""
    m.sector(rect(x1, 0, x2, Y0 - CURB_W), color=color)
    m.sector(rect(x1, Y1 + CURB_W, x2, top), color=color)


# H: x 0..640
strips(0, 640, 384, HCOL)
belt(m, (0, 192), (640, 192), TH, color=HCOL)
recess(m, (0, Y0), (0, Y1), (-1, 0), 0, far_id(BLUE), 101, far_colour=BLUE, color=HCOL, tag=TH)
recess(m, (640, Y0), (640, Y1), (1, 0), 0, 101, 201, color=HCOL, tag=TH)

# P: x 800..1440, a wall 16 thick at x 1104..1120 with the hatch in it
strips(800, 1104, 384, PCOL)
strips(1120, 1440, 384, PCOL)
belt(m, (800, 192), (1104, 192), TP, color=PCOL)
m.sector(rect(1104, Y0, 1120, Y1), ceil=40, ftex="FLAT20", light=160, color=PCOL, id=TP)      # the hatch
belt(m, (1120, 192), (1440, 192), TP, scroll=False, color=PCOL)
recess(m, (800, Y0), (800, Y1), (-1, 0), 0, far_id(RED), 101, far_colour=RED, color=PCOL, tag=TP)
recess(m, (1440, Y0), (1440, Y1), (1, 0), 0, 102, 201, color=PCOL, tag=TP)

# K: x 1600..2240, y 0..448; GREEN's far side in the north wall at x 1760..1824
m.sector(rect(1600, 0, 2240, Y0 - CURB_W), color=KCOL)
m.sector(rect(1600, Y0 - CURB_W, 1744, 448), color=KCOL)
m.sector(rect(1840, Y1 + CURB_W, 2240, 448), color=KCOL)
belt(m, (1792, 448), (1792, Y1), TKV, color=KCOL)                       # south from the far side...
belt(m, (1760, 192), (2240, 192), TKH, curbs=(False, False), color=KCOL)  # ...the corner and east
for box in ((1840, Y1, 2240, Y1 + CURB_W), (1840, Y0 - CURB_W, 2240, Y0), (1744, Y0, 1760, Y1)):
    m.sector(rect(*box), floor=ajarmap.CURB_H, ftex="STEP1", side="METAL", color=KCOL)
# what comes down the first run keeps going south a little at the corner: a
# curb there would be climbed by anything that can step 16 (the player, a
# monster), so beyond the corner stands a buffer nothing climbs
m.sector(rect(1744, Y0 - CURB_W, 1840, Y0), floor=48, ftex="STEP1", side="METAL", color=KCOL)
recess(m, (1760, 448), (1824, 448), (0, 1), 0, far_id(GREEN), 101, far_colour=GREEN, color=KCOL, tag=TKV)
recess(m, (2240, Y0), (2240, Y1), (1, 0), 0, 103, 201, color=KCOL, tag=TKH)

# S: x 2400..2848; frame 104, a belt 128 long, the scale 160 long, the rest floor
strips(2400, 2848, 384, SCOL)
belt(m, (2400, 192), (2528, 192), TS, color=SCOL)
m.sector(rect(2528, Y0, 2688, Y1), ftex="FLAT5_4", light=230, color=SCOL)                     # the scale
for y in (Y0 - CURB_W, Y1):
    m.sector(rect(2528, y, 2688, y + CURB_W), floor=ajarmap.CURB_H, ftex="STEP1", side="METAL", color=SCOL)
m.sector(rect(2688, Y0 - CURB_W, 2848, Y1 + CURB_W), color=SCOL)
recess(m, (2400, Y0), (2400, Y1), (-1, 0), 0, 104, 201, color=SCOL, tag=TS)

# the hall along the south, and a door into each room (P has two: its halves)
m.sector(rect(-96, -176, 2944, -16), color=HALLC)
for x in (448, 896, 1248, 1904, 2720):
    ajarmap.opening(m, (x, 0), (x + 64, 0), (0, -1), 0)

for x, y, colour in ((320, 192, BLUE), (960, 192, RED), (1792, 336, GREEN), (2608, 192, TEAL)):
    m.thing(x, y, STATION_T, args=(colour,))
m.thing(96, 192, CRATE_T)
m.thing(560, 72, 1, angle=90)
ajarmap.door(m, RED, 80, 72, angle=90)
ajarmap.door(m, GREEN, 160, 72, angle=90)
ajarmap.door(m, BLUE, 240, 72, angle=90)
ajarmap.pair(m, TEAL, (320, 72, 90), (400, 72, 90))

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
