"""The sound lab (map SOUND): a room to hear door sounds and music in. MAP=SOUND ./run.sh

One plain, bright room. On the north wall four frames side by side: 101 and
102 start with RED and BLUE hung in them, 103 and 104 are empty, and GREEN
leans in front of 103. So taking a door, hanging one and swapping one (use
a hung door's frame while carrying another) are each a step or two apart.
The three far sides are on the south wall, in the same room: whatever hangs
where, walking through comes back into this room, and no door can be lost.

On the east wall, well away from the frames, four switches (soundlab.zs):
TAKE and SET step their sound on (Doom's, 1, 2 ... the candidates of
ajsounds.txt, tools/sfx.py, Doom's ...) and play it; MUSIC - and MUSIC + step
through silence and the tracks of ajmusic.txt (tools/music_trial.py, from
trial/music/). A shotgun and shells by the start, to hear a door beside
a shot. The level begins with Doom's sounds and silence.
"""
import ajarmap
from ajarmap import RED, BLUE, GREEN
from udmf import Map, rect

m = Map()
HALL = 0xE8ECF4
BUTTON_T = 20134    # AjarSoundButton (soundlab.zs)

m.sector(rect(0, 0, 1024, 768), ceil=192, light=224, color=HALL)


def frame(a, b, out, n):
    ajarmap.recess(m, a, b, out, 0, n, 201, color=HALL)


for k, n in enumerate((101, 102, 103, 104)):                  # the frames, north wall
    x = 128 + 128 * k
    frame((x, 768), (x + 64, 768), (0, 1), n)
for c, x in ((RED, 128), (BLUE, 320), (GREEN, 512)):          # the far sides, south wall
    ajarmap.recess(m, (x, 0), (x + 64, 0), (0, -1), 0, ajarmap.far_id(c), 101, far_colour=c, color=HALL)

# The switches, east wall, seen from the room left to right: TAKE, SET, and
# further on MUSIC - and MUSIC +. Line id = thing id = 800 + what it does.
for kind, tex, y in ((1, "AJSNDT", 512), (2, "AJSNDS", 416), (4, "AJSNDM", 256), (3, "AJSNDP", 160)):
    a, b = (1024, y + 64), (1024, y)
    m.cut(a, b)
    m.line(a, b, special=130, args=(800 + kind,), playeruse=True, repeatspecial=True, mid=tex, exact=True,
           id=800 + kind)
    m.thing(1000, y + 32, BUTTON_T, id=800 + kind, args=(kind,))

m.thing(560, 160, 1, angle=80)                               # the player: the frames ahead, the switches right
ajarmap.door(m, RED, 160, 600, frame=101)
ajarmap.door(m, BLUE, 288, 600, frame=102)
ajarmap.door(m, GREEN, 416, 700, angle=270)
m.thing(480, 200, 2001)                                      # a shotgun and shells
m.thing(440, 200, 2049)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
