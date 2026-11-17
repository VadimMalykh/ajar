"""The lab (map LAB): a room to try the Pair door in. MAP=LAB ./run.sh

A Pair is two leaves of one colour that open onto each other. The hall has
both TEAL leaves, a plain RED door and seven frames:
  111 (west) and 112 (east) face each other: the endless corridor;
  113 (south) is round the corner from 112: the room repeats turned;
  114 and 115 (south) are side by side: each turns you round;
  117 (west) is a spare, for RED.
The gallery is too high to climb. RED's far side is up there, with frame 116,
both ORANGE leaves and the way out. Go up by RED with a leaf, hang it in 116,
drop back down and hang its twin: the hall and the gallery are joined, and
RED is free again. The lever on the west wall changes what a leaf hung alone
shows (AjarHandler.PairTick). No solver: nothing here can be lost.
"""
import ajarmap
from ajarmap import RED, TEAL, ORANGE
from udmf import Map, rect

m = Map()
HALL = 0xD8E8FF
UP = 0xFFE8C0
H = 128             # the gallery's floor

m.sector(rect(0, 0, 768, 512), ceil=256, light=200, color=HALL)
m.sector([(0, 512), (0, 704), (768, 704), (768, 640), (768, 576), (768, 512)],
         floor=H, ceil=256, light=220, color=UP)


def frame(a, b, out, n, floor=0, color=HALL):
    ajarmap.recess(m, a, b, out, floor, n, 201, color=color)


frame((0, 96), (0, 160), (-1, 0), 111)
frame((768, 96), (768, 160), (1, 0), 112)
frame((608, 0), (672, 0), (0, -1), 113)
frame((160, 0), (224, 0), (0, -1), 114)
frame((288, 0), (352, 0), (0, -1), 115)
frame((0, 320), (0, 384), (-1, 0), 117)
frame((96, 704), (160, 704), (0, 1), 116, H, UP)
ajarmap.recess(m, (480, 704), (544, 704), (0, 1), H, 201, 111, far_colour=RED, color=UP)
m.line((768, 576), (768, 640), special=243, playeruse=True, mid="AJEXIT", exact=True)
ajarmap.pair_switch(m, (0, 416), (0, 480))

m.thing(384, 300, 1, angle=270)
ajarmap.pair(m, TEAL, (300, 440, 270), (440, 440, 270))
ajarmap.pair(m, ORANGE, (300, 660, 270), (400, 660, 270))
ajarmap.door(m, RED, 620, 440, angle=270)
m.thing(384, 200, 2001)             # a shotgun and shells: a corridor without end is a range
m.thing(384, 160, 2049)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
