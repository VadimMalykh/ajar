"""The plate lab (map PLATE): the sprung frame and the room of goes.
MAP=PLATE ./run.sh; the tests are MAP=PLATE MODE=3 and 4 tools/smoke.sh.

The start room (the hall, 512 by 512) is a room of goes: a time door in its
west wall and the one box behind it (with the plate that forgets every go
on its west wall). In its north wall a sprung frame (101), RED leaning in
the room, and the frame's plate 312 from its mouth. RED's far side is in
the far room to the north, which is part of the room of goes (one zone over
both rooms). In the far room's east wall a second sprung frame (102), BLUE
leaning there and its plate 352 from the mouth. BLUE's far side is in the
third room to the east, outside the room of goes: walking into it ends the
room; its east end is the exit (a line to walk over).
See src/zscript/plate.zs.
"""
import ajarmap
import ajartime
from ajarmap import RED, BLUE, far_id
from udmf import Map, rect

m = Map()
HALL = 0xE8E0D0
FAR = 0xD8E4F0
BOX = 0xFFE8C0
THIRD = 0xE0F0D8

F1, F2 = 101, 102

# the hall
m.sector(rect(0, 0, 512, 512), ceil=192, light=200, color=HALL)
ajartime.hall_door(m, 1, 1, (0, 224), (0, 288), (-1, 0), 0, color=HALL)
ajarmap.recess(m, (224, 512), (288, 512), (0, 1), 0, F1, far_id(RED), color=HALL)
ajarmap.door(m, RED, 400, 400, angle=270)
ajartime.plate(m, 256, 200, F1)
m.thing(256, 64, 1, angle=90)

# the far room (stubs of frame 1 and of RED's far side are 64 apart)
m.sector(rect(0, 704, 512, 1216), ceil=192, light=190, color=FAR)
ajarmap.recess(m, (224, 704), (288, 704), (0, -1), 0, far_id(RED), F1, far_colour=RED, color=FAR)
ajarmap.recess(m, (512, 928), (512, 992), (1, 0), 0, F2, far_id(BLUE), color=FAR)
ajarmap.door(m, BLUE, 256, 1100, angle=270)
ajartime.plate(m, 160, 960, F2)
assert ((256 - 256) ** 2 + (512 - 200) ** 2) ** 0.5 >= 256 and ((512 - 160) ** 2 + (960 - 960) ** 2) ** 0.5 >= 256

# one zone over the hall and the far room (it takes in the time door's stub,
# x down to -64; not the box, not the third room)
ajartime.zone(m, 1, 0, 0, 0, 512, 1216, grow=72, goes=True)

# the box, west: its door in its east wall
m.sector(rect(-400, 160, -208, 352), ceil=160, light=210, color=BOX)
ajartime.box_door(m, 1, 1, (-208, 224), (-208, 288), (1, 0), 0, color=BOX)
ajartime.zone(m, 1, 1, -400, 160, -208, 352, grow=64)
ajartime.anew(m, -398, 256, 0)

# the third room, east of the far room, and the exit at its east end
m.sector(rect(704, 832, 896, 1088), ceil=160, light=200, color=THIRD)
m.sector(rect(896, 832, 1024, 1088), ceil=160, light=230, color=THIRD, ftex="AJTRIMF")
ajarmap.recess(m, (704, 928), (704, 992), (-1, 0), 0, far_id(BLUE), F2, far_colour=BLUE, color=THIRD)
m.line((896, 832), (896, 1088), special=243, playercross=True)
m.line((1024, 832), (1024, 1088), mid="AJEXIT", exact=True)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
