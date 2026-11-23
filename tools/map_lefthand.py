"""The left-handed room lab (map LEFT): MAP=LEFT ./run.sh

Can MAP20's secret way out be built: a pane among real mirrors that is not
a mirror but an opening onto a room built as the mirror image of this one
(PLAN.md, "MAP20's secret way out: the left-handed copy" and "The
left-handed room lab"). The copy is made by tools/lefthand.py.

Bays off one corridor (y -144..-16), west to east, each a room 512 x 384
(x 0..512, y 0..384 from its corner) whose north wall holds five panes in a
row, each in the same surround: a niche 64 wide, 8 deep, a sill 24 high, a
head at 160, the glass at the back (y 392). The fourth pane (x 320..384) is
the one that may be an opening. Each room has things with a clear left and
right: a plaque "ROOM 20" with an arrow on the south wall, a lamp and a
brighter patch of floor in the north-east only, a step along the south wall's
west half, a sham door frame in the west wall, a marine's statue turned
aslant (8 rotations), a dead marine (one picture), and its way in is a door
in the east wall's south end.
  A  the opening: the fourth pane is a line portal (501) onto the matching
     pane (502) of A', A built again reflected in the glass's plane (y 392),
     far north (y 2440..2896). A' has one thing more: a door in its west
     wall near the panes, and behind it a room with an Exit_Secret line.
  B  the same room with the fourth pane a real mirror: the control for
     question 1 (1024 east of A, so that every flat and texture is laid the
     same).
  C  as A with a mirror on the south wall too (the depth question), its
     copy C' (511, 512). C' is kept off the automap until the player has
     stood in it (A' is not: the two ways, for question 5).
  D  as B with that mirror: C's control.
  V  the carried door: the panes are niches like a frame's (64 wide, 16
     deep, 96 high, no sill) and the fourth is frame 101; GREEN leans in the
     room, its far side is the matching pane of V' (V reflected in y 400).
     A second frame (102) in the east wall.
The tests are in src/zscript/lefthand.zs: MAP=LEFT MODE=n tools/smoke.sh, 1
walking in and back, shots, the way out (checks); 2 question 1's views (then
tools/lefthand_compare.py on them); 3 the tells, the depth, the automap
(views); 4 the carried door, sight and sound (checks); 5 the carried door
(views). PLAN.md, "The left-handed room lab".
"""
import ajarmap
from ajarmap import GREEN, far_id, DOOR_H
import lefthand
from udmf import Map, rect

m = Map()
STATUE_T = 20151            # AjarLeftHandStatue (lefthand.zs)
MIRROR = 182                # Line_Mirror
PORTAL = 156                # Line_SetPortal
EXIT_SECRET = 244
PANES = [(32, 96), (128, 192), (224, 288), (320, 384), (416, 480)]
OPEN = 3                    # the fourth pane
LIGHT, LAMP_LIGHT = 160, 224
LOOK = dict(wall="AJLBWALL", ftex="AJLBFLOR", ctex="AJCEIL")
TRIM = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
BAYS = {"A": 0, "B": 1024, "C": 2048, "D": 3072, "V": 4096}
COPY_DY = {"pane": 2096, "frame": 2080}     # the copies' shift north: the glass at 392 (pane) or 400 (frame) goes to 2488 / 2480


def bay(mm, ox, *, kind="pane", opening=None, south=False, copy=False, door_way=True):
    """One room with its pane wall, its corner at (ox, 0), into the Map mm.
    `opening`: (this line id, target id) makes the fourth pane a portal;
    without it the fourth pane is a mirror (or, for kind "frame", see
    frame_bay). `south`: a mirror pane on the south wall too. `copy`: the
    source of a reflected copy: one thing more (the door in the west wall and
    the way out behind it), and no way in from the corridor."""
    X = lambda x: ox + x
    for box in ((0, 64, 192, 96), (192, 0, 512, 96), (0, 96, 512, 256), (0, 256, 384, 384)):   # the room, in pieces
        mm.sector(rect(X(box[0]), box[1], X(box[2]), box[3]), light=LIGHT, **LOOK)
    mm.sector(rect(X(384), 256, X(512), 384), light=LAMP_LIGHT, **LOOK)          # the lamp's patch
    mm.sector(rect(X(0), 0, X(192), 64), floor=16, light=LIGHT, wall="AJLBWALL", ftex="AJLBSTEP", ctex="AJCEIL")   # the step
    depth, sill, head = (8, 24, 160) if kind == "pane" else (16, 0, DOOR_H)
    glass = 384 + depth
    for k, (x1, x2) in enumerate(PANES):
        if kind == "frame" and k == OPEN:
            continue                                                            # the frame, or its far side: frame_bay
        mm.sector(rect(X(x1), 384, X(x2), glass), floor=sill, ceil=head, light=LIGHT if kind == "pane" else 176, **TRIM)
        if k == OPEN and opening:
            mm.sector(rect(X(x1), glass, X(x2), glass + 48), floor=sill, ceil=head, light=96, **TRIM)   # the stub behind the portal
            mm.line((X(x1), glass), (X(x2), glass), id=opening[0], special=PORTAL, args=(opening[1], 0, 1, 1))
        else:
            mm.line((X(x1), glass), (X(x2), glass), special=MIRROR)
    if south:
        mm.sector(rect(X(336), -8, X(464), 0), floor=24, ceil=160, light=LIGHT, **TRIM)
        mm.line((X(336), -8), (X(464), -8), special=MIRROR)
    mm.cut((X(192), 0), (X(320), 0))
    mm.line((X(192), 0), (X(320), 0), mid="AJLBPLAQ")                        # the plaque
    mm.sector(rect(X(-16), 192, X(0), 256), ceil=DOOR_H, light=LIGHT, **TRIM)   # the sham frame
    mm.line((X(-16), 192), (X(-16), 256), mid="AJFRAME")
    # the way in: a door in the east wall's south end (shut in every test; on the corridor's side in the room only)
    d = mm.sector(rect(X(512), 32, X(528), 96), ceil=0, light=LIGHT, wall="AJHDOR", ftex="AJTRIMF", ctex="AJTRIMF")
    mm.line((X(512), 32), (X(512), 96), special=12, args=(0, 16, 150), playeruse=True, repeatspecial=True, back=d)
    if not copy and door_way:
        mm.sector(rect(X(528), 32, X(592), 96), ceil=128, light=LIGHT, **TRIM)
        mm.sector(rect(X(528), -16, X(592), 32), ceil=128, light=LIGHT, **TRIM)
        mm.line((X(528), 32), (X(528), 96), special=12, args=(0, 16, 150), playeruse=True, repeatspecial=True, back=d)
    if copy:
        # the one thing not as it was: a door in the west wall near the panes, the way out behind it
        d = mm.sector(rect(X(-16), 296, X(0), 360), ceil=0, light=LIGHT, wall="AJHDOR", ftex="AJTRIMF", ctex="AJTRIMF")
        mm.line((X(0), 296), (X(0), 360), special=12, args=(0, 16, 150), playeruse=True, repeatspecial=True, back=d)
        mm.sector(rect(X(-80), 280, X(-16), 376), ceil=128, light=200, **TRIM)
        mm.sector(rect(X(-144), 280, X(-80), 376), ceil=128, light=200, **TRIM)
        mm.line((X(-80), 280), (X(-80), 376), special=EXIT_SECRET, playercross=True)
    mm.thing(X(472), 344, 2028)                                                 # the lamp (one that does not flicker: the views compare frame by frame)
    mm.thing(X(128), 200, STATUE_T, angle=30)                                   # the statue, turned aslant (out of the cameras' way to the fourth pane)
    mm.thing(X(176), 232, 15)                                                   # a dead marine
    return glass


def frame_bay(mm, ox, *, copy=False):
    """Bay V: the fourth pane is frame 101 (or, in the copy, GREEN's far side)."""
    glass = bay(mm, ox, kind="frame", copy=copy)
    x1, x2 = PANES[OPEN]
    if copy:
        ajarmap.recess(mm, (ox + x1, 384), (ox + x2, 384), (0, 1), 0, far_id(GREEN), 101, far_colour=GREEN,
                       trim=("AJTRIM", "AJTRIMF"))                          # the frame's own trim, not GREEN's
    else:
        ajarmap.recess(mm, (ox + x1, 384), (ox + x2, 384), (0, 1), 0, 101, far_id(GREEN))
        ajarmap.recess(mm, (ox + 512, 224), (ox + 512, 160), (1, 0), 0, 102, far_id(GREEN))
        ajarmap.door(mm, GREEN, ox + 128, 160, angle=90)
    return glass


# --- the bays and their copies -------------------------------------------------
SOURCES = {}                # the source of each copy (as built before reflecting): for tools/mapcheck.py
for name, ox in BAYS.items():
    if name == "V":
        glass = frame_bay(m, ox)
        src = Map()
        frame_bay(src, ox, copy=True)
    else:
        mirror_only = name in "BD"
        ids = {"A": (501, 502), "C": (511, 512)}.get(name)
        glass = bay(m, ox, opening=ids, south=name in "CD")
        if mirror_only:
            continue
        src = Map()
        bay(src, ox, opening=ids[::-1], south=name == "C", copy=True)
    SOURCES[name] = src
    lefthand.left_handed(m, src, "y", glass, (0, COPY_DY["frame" if name == "V" else "pane"]), hide=name == "C")

# --- the corridor ----------------------------------------------------------------
m.sector(rect(-64, -144, 4800, -16), ceil=128, light=170, **TRIM)
m.thing(-32, -80, 1, angle=0)

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
