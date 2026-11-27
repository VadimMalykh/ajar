"""Look 2's title map, "Portals" (AJAR_TITLE=2; tools/gfx_title2.py, and the helpers: tools/map_title.py).

A dark hall whose north wall steps back in three bays, a frame in each, and a colour door hung in each by
the game's own machinery: the real frame (ajarmap.recess: its AjarFrame and the frame's portal line), the
real AjarDoor hung there at the start (ajarmap.door with frame=), whose leaf AjarHandler stands open at a
jamb as it does in every level (leaf.zs, PoseLeaf), and the far side's own portal line (id far_id(colour)),
which the handler links to the frame. Through each door is a room of one level, in that level's own
textures and with its own props, bright against the hall:

  RED     MAP03 "Stage Door": the theatre (its look 1, gfx_theatre.py) seen from the dress circle: the
          stage below, its boards and candelabra, the curtain, the proscenium over it
  BLUE    MAP07 "Small Hours": the planetarium (the observatory's look 3, gfx_observatory.py): its town
          and stars on the walls, the projector on its plinth in the middle
  YELLOW  MAP08 "Closing Time": the toy department (the store's look 3, gfx_store.py): its shelves, a
          counter with the till, the rocking horse

The camera stands near the wall, turned to the left of square on, so that the bays step away from it:
RED nearest, half the picture high, on the right; BLUE behind it; YELLOW furthest, by the menu, which
stands on the plain wall at the left. Stepped, each doorway is seen within some twenty degrees of square
on (a straight wall seen at this nearness would show the far doorways edge on, the 16-deep frame
hiding them). It glides nearer and back, a minute each way (camera(glide=)), so the rooms shift in
their doorways and RED's doorway runs out past the picture's edge.

A leaf hangs at the left jamb unless something is in its way (leaf.zs), and there it would stand between
the camera and its own doorway: so each frame has a low step (4 high) where that leaf would stand, and
the leaf hangs at the right jamb, swung out towards the camera, clear (by 5) of the next bay's wall.

Each far side is a portal line flush in its room's south wall (no coloured recess of its own), oriented so
that the portal only moves the view (no turn): a point (u, v) beyond a frame's line, u east along the wall
from the doorway's middle and v north into it, is the point (u, v) from the middle of the far line in its
room. The rooms are built in those coordinates (place()), their props where the doorways show them from
the glide's path, and big enough that every ray through every doorway from either end of the glide ends on
a wall away from the doorway (check(), run when the map is made).

No monsters, nothing that makes a sound; the player pawn stands in the closet, out of every view.
"""
import math

import ajarmap
from ajarmap import RED, BLUE, YELLOW, far_id
from udmf import Map
import map_title
import gfx_observatory
import gfx_store

# --- the hall ----------------------------------------------------------------------------------------
WEST, SOUTH, EAST = -768, -192, 448
HALL_CEIL, HALL_LIGHT = 176, 96
WALL, FLOOR, CEIL = "AJT2W", "AJT2F", "AJT2C"      # gfx_title2.files()
DOORS = ((YELLOW, -136, 328), (BLUE, -32, 256), (RED, 72, 184))   # far to near: colour, its mouth's middle
RETURN = 40                          # each bay's wall turns back this far left of the next frame's middle
PLACES = {BLUE: (4096, 0), RED: (6144, 0), YELLOW: (9216, 0)}   # where the middle of each far line is
EYE = 48
HOME = (32, -8, 118)                 # the camera: x, y, angle
GLIDE = (-8, 8, 114)                 # where it glides to and back
PERIOD = 120                         # seconds there and back


def place(colour):
    """A function (u, v) -> world point, for building the far side of `colour` in its doorway's terms."""
    ox, oy = PLACES[colour]
    return lambda u, v: (ox + u, oy + v)


def R(at, u1, v1, u2, v2):
    """A rectangle in a place's terms, as (x1, y1, x2, y2) in the world."""
    a, b = at(u1, v1), at(u2, v2)
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


def far_line(m, colour, frame_id):
    """The far side of `colour`: a portal line flush in its room's south wall, from u = -32 to 32, the room
    to its north (declare the room first: the line's front faces the sector declared first), and the small
    stub behind it that every portal line has (ajarmap.STUB)."""
    at = place(colour)
    a, b = at(-32, 0), at(32, 0)
    m.sector([a, b, at(32, -ajarmap.STUB), at(-32, -ajarmap.STUB)], floor=0, ceil=ajarmap.DOOR_H, light=96,
             wall=f"AJTR{colour}", ftex=f"AJTF{colour}", ctex=f"AJTF{colour}")
    m.line(a, b, id=far_id(colour), special=156, args=(frame_id, 0, 1, 1), mid=f"AJDR{colour}")


def theatre(m):
    """RED's far side: MAP03's theatre in its own look 1 (map_hinges3: HOUSE 448, STAGE 64), seen from
    the front of the dress circle. The doorway opens onto the circle's edge (a lip of tier front); the
    stalls lie far below, out of the doorway's sight; across them, 200 on, the stage, 128 above the
    stalls and 80 below the eye, deep (440), so that its boards show from the apron to the curtain's foot:
    its candelabra, the curtain at its back (whole: 384 high), under the proscenium's lintel and between
    its sides. The rays through the doorway run north and a little east."""
    at = place(RED)
    m.align |= ({f"AJ3{k}1{t}" for k, ts in (("H", "ABCD"), ("T", "ABC")) for t in ts} | {f"AJ3{k}1" for k in "FGBK"})
    STALLS, STAGE, HOUSE = -160, -32, 288
    FRONT, LEFT, RIGHT = 200, -8, 200                    # the stage's front, its opening's sides
    x1, y1, x2, y2 = R(at, -192, 0, 448, 640)
    wing = dict(floor=STAGE, ceil=STAGE, wall="AJ3H1A", side="AJ3H1A")
    leg = dict(floor=STAGE, ceil=STAGE, wall="AJ3K1", side="AJ3K1")
    ajarmap.fitted(m, (x1, y1, x2, y2), [
        (R(at, -192, 48, 448, 56), dict(floor=8, ftex="AJ3M1", side="AJ3T1A", light=176)),      # the circle's lip
        (R(at, -192, 56, 448, FRONT), dict(floor=STALLS, light=144)),                            # the stalls
        (R(at, LEFT, FRONT, RIGHT, 640), dict(floor=STAGE, ceil=STAGE + 384, light=240, wall="AJ3K1",
                                              ftex="AJBOARD", side="AJWOOD", ctex="AJ3XC")),   # the stage
        (R(at, LEFT, FRONT, RIGHT, FRONT + 24), dict(floor=STAGE, ceil=128, light=232, wall="AJ3H1A",
                                                     ftex="AJBOARD", side="AJWOOD", ctex="AJ3XC")),  # the lintel
        (R(at, -192, FRONT, LEFT, FRONT + 24), wing), (R(at, RIGHT, FRONT, 448, FRONT + 24), wing),   # its sides
        (R(at, -192, FRONT + 24, LEFT, 640), leg), (R(at, RIGHT, FRONT + 24, 448, 640), leg),         # the wings
    ], floor=0, ceil=HOUSE, light=176, wall="AJ3H1A", ftex="AJ3M1", ctex="AJ3C1")
    for u, v in ((24, 280), (88, 296), (152, 280)):                           # candelabra on the boards
        m.thing(*at(u, v), 35)
    return (x1, y1, x2, y2)


def planetarium(m):
    """BLUE's far side: MAP07's planetarium (map_hinges7: SKYBOX, STEPS3, PLANET, PLINTH), the same size,
    in the observatory's own look 3, the projector on its plinth in the middle. The doorway is in its south
    wall, east of the middle; the rays through it go north and a little west, over the projector to the
    north wall's town and stars."""
    at = place(BLUE)
    T = lambda tag: f"AJ7{tag}3"
    m.align |= gfx_observatory.aligned("3")
    x1, y1, x2, y2 = R(at, -272, 0, 176, 448)
    room = ajarmap.octagon(x1, y1, x2, y2, 96)
    steps = [(ajarmap.octagon(x1 + 64, y1 + 64, x2 - 64, y2 - 64, 72), 208),
             (ajarmap.octagon(x1 + 112, y1 + 112, x2 - 112, y2 - 112, 56), 232),
             (ajarmap.octagon(x1 + 160, y1 + 160, x2 - 160, y2 - 160, 32), 248)]
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    plinth = (cx - 32, cy - 32, cx + 32, cy + 32)
    ajarmap.shaped(m, (x1, y1, x2, y2),
                   [(ring, dict(ceil=h)) for ring, h in steps]
                   + [((cx - 80, cy - 80, cx + 80, cy + 80), dict(light=224)),
                      (plinth, dict(floor=32, ftex=T("WD"), side=T("WD"), light=248))],
                   outline=room, floor=0, ceil=176, light=208, wall=T("EP"), ftex=T("FE"), ctex=T("CS"))
    for ring, _ in steps:
        for a, b in zip(ring, ring[1:] + ring[:1]):
            fit = None
            if a[0] != b[0] and a[1] != b[1]:
                L = math.dist(a, b)
                fit = (a, max(1, round(L / 64)) * 64 / L)
            m.line(a, b, upper=T("ES"), **(dict(fit=fit) if fit else {}))
    for a, b in zip(room, room[1:] + room[:1]):
        if a[0] != b[0] and a[1] != b[1]:
            L = math.dist(a, b)
            m.line(a, b, fit=(a, max(1, round(L / 64)) * 64 / L))
    m.thing(cx, cy, 20022, angle=300)                                       # the projector
    return (x1, y1, x2, y2)


def toys(m):
    """YELLOW's far side: MAP08's toy department (map_hinges8: hall(), shelves("TY"), CASE), 160 high, in
    the store's own look 3: its yellow walls and fitted shelves of toys, a counter with the till, the
    rocking horse. The doorway is at the east end of its south wall; the rays through it go north-west,
    past the counter and the horse to the shelves on the north wall."""
    at = place(YELLOW)
    T = lambda tag, pic="": f"AJ8{tag}3{pic}"
    m.align |= gfx_store.aligned("3")
    x1, y1, x2, y2 = R(at, -448, 0, 64, 384)
    case = dict(ftex=T("VT"), side=T("V"), floor=40, light=232)
    ajarmap.fitted(m, (x1, y1, x2, y2), [(R(at, -128, 136, -72, 184), case)],
                   floor=0, ceil=160, light=224, wall=T("TY"), ftex=T("FD"), ctex=T("CD"))
    for i, u in enumerate(range(-448, 64, 64)):                               # the fitted shelves
        a, b = at(u, 384), at(u + 64, 384)
        m.cut(a, b)
        m.line(a, b, mid=T("TY", 1 + i % 2))
    for i, v in enumerate(range(64, 384, 64)):
        a, b = at(-448, v + 64), at(-448, v)
        m.cut(a, b)
        m.line(a, b, mid=T("TY", 1 + i % 2))
    m.thing(*at(-100, 160), 20028, angle=315)                                 # the till, on the counter
    m.thing(*at(-112, 296), 20027, angle=330)                                 # the rocking horse
    return (x1, y1, x2, y2)


def clip(feats, box):
    """The features' rectangles cut to box, the empty ones left out."""
    out = []
    for (a, b, c, d), change in feats:
        r = (max(a, box[0]), max(b, box[1]), min(c, box[2]), min(d, box[3]))
        if r[0] < r[2] and r[1] < r[3]:
            out.append((r, change))
    return out


def bays():
    """The hall's three boxes, west to east: each runs from the last one's turn to RETURN left of the next
    frame, and north to its own frame's mouth."""
    out, west = [], WEST
    for k, (colour, x, y) in enumerate(DOORS):
        east = DOORS[k + 1][1] - RETURN if k + 1 < len(DOORS) else EAST
        out.append((west, SOUTH, east, y))
        west = east
    return out


def hall(m):
    """The hall: dark and plain, its north wall in three bays, a frame in each, the low step at the left
    of each frame (so that the leaf hangs at the right jamb), and a little light on the floor before each
    open door."""
    feats = []
    for colour, x, y in DOORS:
        feats.append(((x - 64, y - 144, x + 96, y), dict(raw={"lightfloor": 24})))
        feats.append(((x - 40, y - 72, x + 64, y), dict(raw={"lightfloor": 48})))
        feats.append(((x - 52, y - 16, x - 35, y), dict(floor=4, side="AJWOOD")))          # the step
    for box in bays():
        ajarmap.fitted(m, box, clip(feats, box), floor=0, ceil=HALL_CEIL, light=HALL_LIGHT,
                       wall=WALL, ftex=FLOOR, ctex=CEIL)
    for i, (colour, x, y) in enumerate(DOORS):
        fid = 101 + i
        ajarmap.recess(m, (x - 32, y), (x + 32, y), (0, 1), 0, fid, far_id(colour))
        ajarmap.door(m, colour, x, y + 8, frame=fid)


def portals():
    """Look 2's title map: (wad bytes, extra lines of its mapinfo block)."""
    m = Map()
    hall(m)
    rooms = {RED: theatre(m), BLUE: planetarium(m), YELLOW: toys(m)}
    for i, (colour, x, y) in enumerate(DOORS):
        far_line(m, colour, 101 + i)
    check(rooms)
    map_title.closet(m, -2048, -2048)
    x, y, a = HOME
    gx, gy, ga = GLIDE
    map_title.spot(m, gx, gy, EYE, ga, 0, 1)
    map_title.camera(m, x, y, EYE, a, pitch=0, glide=1, period=PERIOD)
    return m.wad("TITLEMAP"), []


def check(rooms):
    """Where the rays from the glide's two ends through each doorway end in its far room's box: none on
    its south wall (beside the doorway: a view along the room's own front wall), every one at least 160
    in. The rays are those that pass the frame's 16-deep mouth; the rooms are closed, so nothing is seen
    past them, and this says that each doorway shows the room built for it. Returns {colour: [(u, v)]}."""
    ends = {}
    for colour, xc, yc in DOORS:
        ox, oy = PLACES[colour]
        bx1, by1, bx2, by2 = rooms[colour]
        u1, v1, u2, v2 = bx1 - ox, by1 - oy, bx2 - ox, by2 - oy
        for cx, cy, _ in (HOME, GLIDE):
            cu, cv = cx - xc, cy - (yc + 16)                 # the camera in the far side's terms
            for u in range(-32, 33, 8):
                du, dv = u - cu, -cv
                mouth = cu + du * (-16 - cv) / dv            # the ray at the frame's mouth, 16 before its line
                if not -32 <= mouth <= 32:
                    continue                                 # hidden by the jamb
                t = min((v2 - 0) / dv, (u2 - u) / du if du > 0 else (u1 - u) / du if du < 0 else 1e9)
                end = (u + du * t, dv * t)
                assert end[1] >= 160, (colour, (cx, cy), u, end)
                ends.setdefault(colour, []).append(end)
    return ends
