"""Look 2's title map, "Portals" (AJAR_TITLE=2; tools/gfx_title2.py, and the helpers: tools/map_title.py).

A dark hall with three frames in its north wall, and a colour door hung in each by the game's own
machinery: the real frame (ajarmap.recess: its AjarFrame and the frame's portal line), the real AjarDoor
hung there at the start (ajarmap.door with frame=), whose leaf AjarHandler stands open at a jamb as it does
in every level (leaf.zs, PoseLeaf), and the far side's own portal line (id far_id(colour)), which the
handler links to the frame. Through each door is a small room of one level, in that level's own
textures and with its own props, bright against the hall:

  BLUE    MAP07 "Small Hours": the planetarium (the observatory's look 3, gfx_observatory.py): its town
          and stars on the walls, its dome in steps, the projector on its plinth
  RED     MAP03 "Stage Door": the stalls and the stage (the theatre's look 1, gfx_theatre.py): rows of
          seats, the curtain, candelabra on the stage
  YELLOW  MAP08 "Closing Time": the toy department (the store's look 3, gfx_store.py): its shelves, a
          counter with the till, the rocking horse

The camera stands back in the hall, west of the doors, looking along the wall at an angle, so that the
doors recede across the right of the picture and the menu stands on the plain wall at the left. It glides
along the hall and back, a minute each way (camera(glide=)), so the rooms shift in their doorways.

Each far side is a portal line flush in its room's south wall (no coloured recess of its own: at this
angle a recess's depth would hide half of each doorway), oriented so that the portal only moves the view
(no turn): a point (u, v) beyond a frame's line, u east along the wall from the doorway's middle and v
north into it, is the point (u, v) from the middle of the far line in its room. The rooms are built in those
coordinates (place()), and big enough that every ray through every doorway from every point of the
glide ends on one of their walls (tools/map_title2.py: check(), run when the map is made).

A leaf hangs at the left jamb unless something is in its way (leaf.zs), and there it would stand
between the camera and its own doorway: so each frame has a pilaster at its left, and the leaf hangs
at the right jamb, swung out towards the camera.

No monsters, nothing that makes a sound; the player pawn stands in the closet, out of every view.
"""
import math

import ajarmap
from ajarmap import RED, BLUE, YELLOW, far_id
from udmf import Map, rect
import map_title
import gfx_observatory
import gfx_store

# --- the hall ----------------------------------------------------------------------------------------
HALL = (-512, -576, 1408, 0)         # x1, y1, x2, y2: the north wall is y = 0
HALL_CEIL, HALL_LIGHT = 176, 128
WALL, FLOOR, CEIL = "AJT2W", "AJT2F", "AJT2C"      # gfx_title2.files()
DOORS = ((BLUE, 128), (RED, 272), (YELLOW, 416))   # colour, the middle of its frame's mouth (x)
PLACES = {BLUE: (4096, 0), RED: (6144, 0), YELLOW: (9216, 0)}   # where the middle of each far line is
EYE = 48
HOME = (56, -288, 72)                # the camera: x, y, angle
GLIDE = (104, -288, 80)              # where it glides to and back
PERIOD = 120                         # seconds there and back


def place(m, colour):
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
    at = place(m, colour)
    a, b = at(-32, 0), at(32, 0)
    m.sector([a, b, at(32, -ajarmap.STUB), at(-32, -ajarmap.STUB)], floor=0, ceil=ajarmap.DOOR_H, light=96,
             wall=f"AJTR{colour}", ftex=f"AJTF{colour}", ctex=f"AJTF{colour}")
    m.line(a, b, id=far_id(colour), special=156, args=(frame_id, 0, 1, 1), mid=f"AJDR{colour}")


def planetarium(m):
    """BLUE's far side: MAP07's planetarium (map_hinges7: SKYBOX, STEPS3, PLANET, PLINTH), the same size,
    in the observatory's own look 3, the projector on its plinth in the middle. The doorway is in its south
    wall; the rays through it go north, past the projector to the north wall."""
    at = place(m, BLUE)
    T = lambda tag: f"AJ7{tag}3"
    m.align |= gfx_observatory.aligned("3")
    x1, y1, x2, y2 = R(at, -192, 0, 256, 448)
    room = ajarmap.octagon(x1, y1, x2, y2, 96)
    steps = [(ajarmap.octagon(x1 + 64, y1 + 64, x2 - 64, y2 - 64, 72), 208),
             (ajarmap.octagon(x1 + 112, y1 + 112, x2 - 112, y2 - 112, 56), 232),
             (ajarmap.octagon(x1 + 160, y1 + 160, x2 - 160, y2 - 160, 32), 248)]
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    plinth = (cx - 32, cy - 32, cx + 32, cy + 32)
    ajarmap.shaped(m, (x1, y1, x2, y2),
                   [(ring, dict(ceil=h)) for ring, h in steps]
                   + [((cx - 80, cy - 80, cx + 80, cy + 80), dict(light=216)),
                      (plinth, dict(floor=32, ftex=T("WD"), side=T("WD"), light=240))],
                   outline=room, floor=0, ceil=176, light=196, wall=T("EP"), ftex=T("FE"), ctex=T("CS"))
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
    m.thing(cx, cy, 20022, angle=225)                                       # the projector
    return (x1, y1, x2, y2)


def stalls(m):
    """RED's far side: MAP03's stalls and stage (map_hinges3: HOUSE 448, STAGE 64, STALLS, BOARDS, SEAT),
    in the theatre's own look 1. The doorway is at the west end of the stalls' south wall; the rays through
    it go north-east, across the rows of seats and the aisle to the stage, its curtain and candelabra."""
    at = place(m, RED)
    m.align |= ({f"AJ3{k}1{t}" for k, ts in (("H", "ABCD"), ("T", "ABC")) for t in ts} | {f"AJ3{k}1" for k in "FGBK"})
    HOUSE, STAGE = 448, 64
    x1, y1, x2, y2 = R(at, -96, 0, 864, 768)
    stage = (x1, y2 - 192, x2, y2)
    seats = [(x1 + 64, y1 + v, x2 - 64, y1 + v + 32) for v in range(96, 480, 64)]
    aisles = [(x, y1, x + 64, y2 - 192) for x in (at(192, 0)[0],)]
    ajarmap.fitted(m, (x1, y1, x2, y2),
                   [(s, dict(floor=16, ftex="AJ3S1", side="AJ3S1")) for s in seats]
                   + [(a, dict(floor=0, ftex="AJ3R1")) for a in aisles]
                   + [((x1, y2 - 256, x2, y2 - 192), dict(light=216)),
                      (stage, dict(floor=STAGE, light=232, wall="AJ3K1", ftex="AJBOARD", side="AJWOOD",
                                   ctex="AJ3XC"))],
                   floor=0, ceil=HOUSE, light=208, wall="AJ3H1A", ftex="AJ3M1", ctex="AJ3C1")
    for u in (256, 576):                                                       # candelabra along the stage's front
        m.thing(*at(u, 768 - 192 + 24), 35)
    return (x1, y1, x2, y2)


def toys(m):
    """YELLOW's far side: MAP08's toy department (map_hinges8: hall(), shelves("TY"), CASE), 160 high, in
    the store's own look 3: its yellow walls and fitted shelves of toys, a counter with the till, the
    rocking horse. The doorway is at the west end of its south wall; the rays through it go north-east, past
    the counter to the shelves on the north wall."""
    at = place(m, YELLOW)
    T = lambda tag, pic="": f"AJ8{tag}3{pic}"
    m.align |= gfx_store.aligned("3")
    x1, y1, x2, y2 = R(at, -64, 0, 832, 448)
    case = dict(ftex=T("VT"), side=T("V"), floor=40, light=224)
    counters = [R(at, 192, 192, 320, 256)]
    ajarmap.fitted(m, (x1, y1, x2, y2), [(c, case) for c in counters],
                   floor=0, ceil=160, light=212, wall=T("TY"), ftex=T("FD"), ctex=T("CD"))
    for i, u in enumerate(range(256, 832, 64)):                                # the fitted shelves
        a, b = at(u, 448), at(u + 64, 448)
        m.cut(a, b)
        m.line(a, b, mid=T("TY", 1 + i % 2))
    for i, v in enumerate(range(64, 448, 64)):
        a, b = at(832, v), at(832, v + 64)
        m.cut(a, b)
        m.line(a, b, mid=T("TY", 1 + i % 2))
    m.thing(*at(256, 224), 20028, angle=270)                                   # the till, on the counter
    m.thing(*at(380, 340), 20027, angle=200)                                   # the rocking horse
    return (x1, y1, x2, y2)


def hall(m):
    """The hall: dark and plain, the three frames in its north wall, a pilaster at the left of each (so
    that the leaf hangs at the right jamb), and a little light on the floor before each open door."""
    x1, y1, x2, y2 = HALL
    feats = []
    for colour, xc in DOORS:
        feats.append(((xc - 48, -16, xc - 32, 0), dict(ceil=0)))                       # the pilaster
        feats.append(((xc - 64, -160, xc + 96, 0), dict(raw={"lightfloor": 14})))
        feats.append(((xc - 32, -96, xc + 64, 0), dict(raw={"lightfloor": 30})))
    ajarmap.fitted(m, HALL, feats, floor=0, ceil=HALL_CEIL, light=HALL_LIGHT, wall=WALL, ftex=FLOOR, ctex=CEIL)
    for i, (colour, xc) in enumerate(DOORS):
        fid = 101 + i
        ajarmap.recess(m, (xc - 32, 0), (xc + 32, 0), (0, 1), 0, fid, far_id(colour))
        ajarmap.door(m, colour, xc, 8, frame=fid)


def portals():
    """Look 2's title map: (wad bytes, extra lines of its mapinfo block)."""
    m = Map()
    hall(m)
    rooms = {BLUE: planetarium(m), RED: stalls(m), YELLOW: toys(m)}
    for i, (colour, xc) in enumerate(DOORS):
        far_line(m, colour, 101 + i)
    check(rooms)
    map_title.closet(m, -2048, -2048)
    x, y, a = HOME
    gx, gy, ga = GLIDE
    map_title.spot(m, gx, gy, EYE, ga, 0, 1)
    map_title.camera(m, x, y, EYE, a, pitch=0, glide=1, period=PERIOD)
    return m.wad("TITLEMAP"), []


def check(rooms):
    """Where the rays from the glide's two ends through each doorway end, in its far room: every one on
    the north or the east wall of the room's box, none on the west or the south one (beside the doorway:
    a view along the room's own front wall). The rooms are closed, so nothing is seen past them; this
    says that each doorway shows the room built for it. Returns {colour: [(u, v) where a ray ends]}."""
    ends = {}
    for colour, xc in DOORS:
        ox, oy = PLACES[colour]
        bx1, by1, bx2, by2 = rooms[colour]
        u1, v1, u2, v2 = bx1 - ox, by1 - oy, bx2 - ox, by2 - oy
        for cx, cy, _ in (HOME, GLIDE):
            cu, cv = cx - xc, cy - 16                        # the camera in the far side's terms
            for u in range(-32, 33, 8):
                du, dv = u - cu, -cv
                mouth = cu + du * (-16 - cv) / dv            # the ray at the frame's mouth, 16 before its line
                if not -32 <= mouth <= 32:
                    continue                                 # hidden by the jamb
                t = min((v2 - 0) / dv, (u2 - u) / du if du > 0 else (u1 - u) / du if du < 0 else 1e9)
                end = (u + du * t, dv * t)
                assert end[1] >= v2 - 1 or end[0] >= u2 - 1, (colour, (cx, cy), u, end)
                ends.setdefault(colour, []).append(end)
    return ends
