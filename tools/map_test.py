"""The Ajar test level (map TEST): every mechanic in one box."""
import ajarmap
from ajarmap import RED, BLUE, GREEN, YELLOW, VIOLET, DOOR_T
from udmf import Map, rect

m = Map()


def recess(*a, **k):
    return ajarmap.recess(m, *a, **k)


# --- the hall, the pit and the ledge -------------------------------------
m.sector(rect(0, 0, 640, 512))                                            # hall
for k in range(7):                                                        # stairs into the pit
    m.sector(rect(640 + 24 * k, 0, 664 + 24 * k, 96), floor=-16 * (k + 1), wall="AJTRIM")
m.sector([(640, 96), (640, 512), (896, 512), (896, 0), (808, 0), (808, 96)],
         floor=-128, ftex="AJPIT", light=150)                             # pit
LEDGE = 0x90B0FF
m.sector(rect(896, 0, 1216, 512), light=210, color=LEDGE)                 # ledge

recess((128, 512), (192, 512), (0, 1), 0, 101, 201)                       # hall N, starts with RED
recess((416, 512), (480, 512), (0, 1), 0, 102, 201)                       # hall N, empty
recess((416, 0), (480, 0), (0, -1), 0, 103, 201)                          # hall S, empty (faces 102)
recess((720, 512), (784, 512), (0, 1), -128, 104, 201)                    # pit N, starts with GREEN
recess((1216, 224), (1216, 288), (1, 0), 0, 105, 201, color=LEDGE)        # ledge E, empty
recess((1024, 512), (1088, 512), (0, 1), 0, 202, 101, far_colour=BLUE, color=LEDGE)  # BLUE far side

# --- red room: far side of RED, holds the BLUE door ------------------------
REDC = 0xFF8070
m.sector(rect(0, 2000, 384, 2384), ceil=160, light=220, color=REDC)
recess((160, 2000), (224, 2000), (0, -1), 0, 201, 101, far_colour=RED, color=REDC)
recess((384, 2160), (384, 2224), (1, 0), 0, 106, 201, color=REDC)        # frame in the red room

# --- green room: far side of GREEN, holds the exit -------------------------
GRNC = 0x80FF90
m.sector([(2000, 2000), (2000, 2256), (2320, 2256), (2320, 2160), (2320, 2096), (2320, 2000)],
         ceil=160, light=220, color=GRNC)
recess((2000, 2096), (2000, 2160), (-1, 0), 0, 203, 101, far_colour=GREEN, color=GRNC)
m.line((2320, 2096), (2320, 2160), special=243, playeruse=True, mid="AJEXIT", exact=True)

# --- a way out to build: YELLOW's far side at one end of a night room, an
# empty frame at the other (ajarmap.way_home); YELLOW leans in the green room.
# And a Stray door in the red room, with two places it may open onto ------------
ajarmap.way_home(m, 3000, 2000, YELLOW)
ajarmap.stray_place(m, 0, (2128, 2256), (2192, 2256), (0, 1), 0, color=GRNC)
ajarmap.stray_place(m, 1, (3128, 2000), (3192, 2000), (0, -1), 0)
ajarmap.door(m, YELLOW, 2300, 2030, angle=180)
ajarmap.stray(m, 200, 2370, angle=270)

# --- the same, the other way round (ajarmap.way_round): VIOLET leans in it ---
ajarmap.way_round(m, 4000, 2000, VIOLET, frame=191, n=8)
ajarmap.door(m, VIOLET, 4160, 2240, angle=270)

# --- things ----------------------------------------------------------------
m.thing(96, 256, 1, angle=0)                                              # player start
m.thing(0, 0, DOOR_T, args=(201, RED, 101))                               # hung by script at load
m.thing(1, 0, DOOR_T, args=(203, GREEN, 104))
m.thing(14, 2192, DOOR_T, angle=0, args=(202, BLUE, 0))                   # leaning on the west wall
# Ordinary Doom company: an imp at the far end of the hall, a zombie on the
# ledge, and a shotgun with shells by the start. (Doom thing numbers.)
m.thing(560, 400, 3001, angle=180)
m.thing(1100, 400, 3004, angle=180)
m.thing(96, 160, 2001)
m.thing(96, 110, 2049)
# A thief in the hall. It goes for the RED door as soon as it sees you,
# then keeps moving doors between the hall frames until it is killed.
m.thing(560, 150, 20003, angle=180)
# A nailer in the hall and a lodger (it starts inside the frames, so where it
# is placed does not matter). "+set ajar_only N" keeps just one of Ajar's
# own monsters: 1 thief, 2 nailer, 3 lodger.
m.thing(300, 100, 20004, angle=90)
m.thing(600, 60, 20005)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
