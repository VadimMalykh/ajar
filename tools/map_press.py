"""The press lab (map PRESS): a fight that becomes a room of goes when it is
won, and a press in it. MAP=PRESS ./run.sh; the tests are MAP=PRESS MODE=3
and 4 tools/smoke.sh. See src/zscript/goes.zs.

One hall, 1024 by 768, entered from the way in to the south. It is an open
fight (time.zs) that becomes a room of goes when it is won (zone mix=True):
ten demons and imps, all of them AjarCues of wave 1, nothing that flies. The
north third of the hall is the press (its walls and ceiling are steel): its
ceiling comes down to the floor when the switch on the south wall is used.
Two time doors (west and south) and two boxes behind glass (west and
south). In the east wall a sprung frame (101), RED leaning by it and the
frame's plate 324 from its mouth; RED's far side is in a small room to the
east, outside the fight, whose east end is the exit. The steel door the win
opens is in the west wall, into a lobby that is part of the hall.
"""
import ajarmap
import ajartime
from ajarmap import RED, far_id
from udmf import Map, rect

m = Map()
HALL = 0xE8E0D0
BOX = 0xFFE8C0
OUT = 0xE0F0D8
PRESS = 3500        # the press's sector tag (goes.zs: AjarTimeHandler.PRESS_TAG, for the tests)
F1 = 101

# the hall, its press, and the way in
m.sector(rect(0, 0, 1024, 512), ceil=192, light=200, color=HALL)
m.sector(rect(0, 512, 1024, 768), ceil=192, light=190, color=HALL, wall="AJBOLT", ctex="AJTRIMF", id=PRESS)
ajartime.press(m, 512, 640, PRESS)
ajartime.press_switch(m, 320, 2, 90, PRESS)
m.sector(rect(448, -192, 576, 0), ceil=128, light=180, color=HALL)
m.thing(512, -150, 1, angle=90)
ajartime.zone(m, 1, 0, 0, 0, 1024, 768, grow=72, mix=True)

# the time doors: west and south
ajartime.hall_door(m, 1, 1, (0, 96), (0, 160), (-1, 0), 0, color=HALL)
ajartime.hall_door(m, 1, 2, (864, 0), (928, 0), (0, -1), 0, color=HALL)

# box 1, west, its door in its west wall; box 2, south, its door in its south wall
m.sector(rect(-240, 192, -16, 384), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (0, 224), (0, 352), (-1, 0), 64)
ajartime.box_door(m, 1, 1, (-240, 256), (-240, 320), (-1, 0), 64, color=BOX)
ajartime.zone(m, 1, 1, -304, 192, -16, 384)
m.sector(rect(640, -208, 832, -16), floor=64, ceil=192, light=210, color=BOX)
ajartime.glass(m, (672, 0), (800, 0), (0, -1), 64)
ajartime.box_door(m, 1, 2, (704, -208), (768, -208), (0, -1), 64, color=BOX)
ajartime.zone(m, 1, 2, 640, -272, 832, -16)

# the steel door the win opens, west, into a lobby that is part of the hall
a, b, c, d = (0, 416), (0, 480), (-16, 416), (-16, 480)
m.sector([a, b, d, c], floor=0, ceil=0, light=160, wall="AJBOLT", ftex="AJTRIMF", ctex="AJTRIMF", id=3090 + 100 * 1)
m.line(a, b, exact=True)
m.line(c, d, exact=True)
for p, q in ((a, c), (b, d)):
    m.line(p, q, mid="AJTRIM", dontpegbottom=True)
m.sector(rect(-208, 400, -16, 496), ceil=128, light=180, color=HALL)
ajartime.zone(m, 1, 0, -208, 400, -16, 496)

# the sprung frame, east; RED by it, its plate out in the hall
ajarmap.recess(m, (1024, 224), (1024, 288), (1, 0), 0, F1, far_id(RED), color=HALL)
ajarmap.door(m, RED, 960, 150, angle=180)
ajartime.plate(m, 700, 256, F1)
assert ((1024 - 700) ** 2 + (256 - 256) ** 2) ** 0.5 >= 300

# the room beyond RED, outside the fight, and the exit at its east end
m.sector(rect(1216, 128, 1408, 384), ceil=160, light=200, color=OUT)
m.sector(rect(1408, 128, 1472, 384), ceil=160, light=230, color=OUT, ftex="AJTRIMF")
ajarmap.recess(m, (1216, 224), (1216, 288), (-1, 0), 0, far_id(RED), F1, far_colour=RED, color=OUT)
m.line((1408, 128), (1408, 384), special=243, playercross=True)
m.line((1472, 128), (1472, 384), mid="AJEXIT", exact=True)

# the fight: all of it wave 1, out of the press, nothing that flies
DEMONS = [(150, 300), (350, 300), (560, 380), (850, 380), (250, 440), (760, 440)]
IMPS = [(150, 150), (450, 200), (600, 150), (880, 300)]
ajartime.cue(m, 1, 1, 0, 3002, *DEMONS, angle=90, always=True)
ajartime.cue(m, 1, 1, 0, 3001, *IMPS, angle=90, always=True)
assert all(y < 512 for _, y in DEMONS + IMPS)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
