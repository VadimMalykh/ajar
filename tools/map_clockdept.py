"""Act 2, level 8: "Time and Motion" (MAP18), the clock department. It wears
MAP11's look (AJAR_INSTITUTE), as MAP16 and MAP17 do. PLAN.md, "MAP18: the
clock department" and its subsection "The first version, as decided"; the
pulse, its lanes and its contacts are the clock lab's (src/zscript/clock.zs).

A big building to make geometries in, and one measure: the stopwatch. No
keys, no thief, no nailer, no lodger, no Stray door: every area and every
frame is reached on foot from every other with no door hung (the lift is on
foot). The doors are shortcuts and the makings of the paradoxes.

The run. The delay hall (west) has three lanes, 2048, 1024 and 512 long,
each with a frame in its west end (the long one in the hall's west wall, the
other two on piers) and one in the hall's east wall facing it, an emitter
near its east end firing east and, just behind the emitter, the lane's
contact. The levers are in the regulator room at the hall's west end, behind
glass, whose only door is to the yard. A lever calls back any pulse alive in
the hall, fires its lane's pulse and so raises the night room's shutter at
the other end of the building (the basement's north-east): the shutter is
up while the pulse lives. A pulse lives for LAPS passes of its own lane's
contact and then burns out; with no loop it bursts on the lane's end. So the
time for the run is LAPS times the loop: a Pair in a lane is the clock, and
two lanes joined by both Pairs (the east end of one to the west end of the
other and back) make one loop of both lengths.

Floors (each area at its own height, side by side in plan): the basement
-256, the ground 0, the upper floor 256; joined by the stair (north-west),
the lift (east of the rotunda: basement, ground, upper east) and the
kitchen's steps (south-east, down to the basement).

Areas, west to east (x 0..8000, y 0..4000; the court in the middle):
  the yard (south-west, open; the porter's hut)     ground
  the regulator room and the delay hall (west)      ground
  the north corridor, the stair hall and the stair  ground .. upper
  upper west: the spine, the drawing office, the workshop, four offices,
    the hall with no size                            upper
  the porch, the entrance hall (the start), the cloakroom   ground
  the court (open; the clock tower: the inside-out booth)   ground
  the north wing (the archive, the timekeepers)     upper
  the rotunda (the pillar and its stub): the arena  ground
  the lift and its gallery                          basement .. upper
  upper east: the six-sided hall, the room that is its own neighbour, the
    regulator store (ORANGE)                         upper
  the canteen and the kitchen (south-east)          ground
  the basement: the cellar, the stores, the boiler room, the night room

The paradoxes, each an ordinary part of the building:
  the endless corridor: any lane, a Pair in its two frames (walked too);
  the endless stair: the foot frame (107) faces up the flight, the head
    frame (108) down it;
  the moving room: RED's far side is in the lift's car;
  round the pillar: frames in the rotunda's north, east and west walls, and
    one in each face of the stub from the pillar to the south wall;
  the six-sided hall: its north-east and south-west walls are joined for
    good (fixed doorway 5), frames in its two straight walls, its other two
    walls its doorways;
  the room that is its own neighbour: north joined to south for good
    (fixed doorway 6), frames east and west;
  the inside-out booth: the clock tower's four faces (fixed doorways 1 to 4)
    are the four walls of the hall with no size, upper west.

Three sites are kept free for one-sided doorways (another task builds
them); each is marked `# ONESIDE site n` below.

No PUZZLE: five doors and some thirty frames with nothing locked are too many
arrangements to search and none can be stuck. Instead this module checks,
when it is built, that everything is one piece on foot and that the run's
clock and ways keep the rules (MEASURE below); the build fails if not.
"""
import heapq
import math

import ajarmap
import map_institute1 as I1
from ajarmap import RED, GREEN, BLUE, TEAL, ORANGE, far_id, LIFT
from map_institute1 import T, dress, tint, over, hang, LOOK
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, REVENANT, CACO
from map_institute1 import BARON, SOUL, MANCUBUS
from udmf import Map, rect

# --- the run's clock: the two named constants ---------------------------------------------------
LAPS = 4            # passes of its own lane's contact that a pulse lives for
SPEED = 20          # the pulse's speed, units a tic
RUN = 16.7          # the player running, units a tic: what the ways are timed at
LANES = {1: 2048, 2: 1024, 3: 512}          # lane: the distance between its two frames' mouths
NAMES = {1: "the long lane", 2: "the middle lane", 3: "the short lane"}
NEAR = 1000         # no frame or far side nearer than this on foot to a lever or the shutter

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12 to MAP17.
_theirs, I1.m = I1.m, m
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED

G, U, B = 0, 256, -256                       # the ground, the upper floor, the basement
ARACHNO, PAIN, VILE = 68, 71, 64
EMITTER_T, LANE_CONTACT_T, DELAY_T = 20110, 20130, 20131
EMIT_TID, CONTACT_TID = 1810, 1820           # + the lane
LEVER_ID = 1840                              # + the lane: the levers' lines
LAMP_TAG = 1830                              # + 0..LAPS-1: the lamps that count the beats left
SHUTTER_TAG = 1850                           # the night room's shutter
SHUTTER_ID = 1851                            # its line on the boiler room's side
ROUTE_A, ROUTE_B = 1860, 1900                # MapSpots: the measured ways (tid of the first; + 0 the doors)
MAPSPOT = 9001
CAR_TIDS = 1701                              # the lift's buttons: 1701..1706

PALE, MINT, PAPER, DIM, RUST, COLD, STEEL = 0xDCE8DC, 0xC8E0C8, 0xF0E4C8, 0xB0B8C8, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0


def P(x, y):
    return (round(x, 3), round(y, 3))


# === the measure: a graph of waypoints with real distances =========================================
class Walk:
    """Convex walkable pieces ("areas"), each at one height, and points in
    them ("nodes"): the middle of every opening between two areas (it is in
    both), a point 32 in front of every frame and far side, the levers, the
    shutter. Two nodes of one area are joined by a straight line unless it
    passes through an obstacle of the area (a pillar, a pier, the hut, kept
    16 off: the player's radius); round an obstacle the way goes by its
    corners, which are nodes too. Stairs are areas like any other (measured
    flat); the lift's ride is a link that costs its time (4 units a tic),
    the car assumed to be waiting. A hung door is a link of 32 (through two
    recesses 16 deep)."""
    R = 16

    def __init__(self):
        self.areas = {}
        self.nodes = []
        self.links = []

    def area(self, name, shape, z, obst=()):
        poly = rect(*shape) if not isinstance(shape[0], (tuple, list)) else list(shape)
        assert name not in self.areas, name
        self.areas[name] = dict(poly=poly, z=z, obst=list(obst))

    def node(self, x, y, label, *areas):
        for a in areas:
            assert a in self.areas, (label, a)
        self.nodes.append(dict(x=x, y=y, label=label, areas=set(areas)))
        return len(self.nodes) - 1

    def link(self, i, j, cost):
        self.links.append((i, j, cost))

    @staticmethod
    def crosses(p, q, r):
        """The segment p-q passes through the inside of the box r."""
        t0, t1 = 0.0, 1.0
        dx, dy = q[0] - p[0], q[1] - p[1]
        for pp, qq in ((-dx, p[0] - r[0]), (dx, r[2] - p[0]), (-dy, p[1] - r[1]), (dy, r[3] - p[1])):
            if pp == 0:
                if qq <= 0:
                    return False
            else:
                t = qq / pp
                if pp < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
        return t1 - t0 > 1e-9

    def graph(self):
        """Adjacency: node -> [(node, cost)]."""
        if hasattr(self, "_adj"):
            return self._adj
        for name, a in self.areas.items():                  # the corners round each obstacle
            for r in a["obst"]:
                g = self.R + 8
                for x, y in ((r[0] - g, r[1] - g), (r[0] - g, r[3] + g), (r[2] + g, r[1] - g), (r[2] + g, r[3] + g)):
                    free = all(not (o[0] - self.R < x < o[2] + self.R and o[1] - self.R < y < o[3] + self.R) for o in a["obst"])
                    if ajarmap._inside((x, y), a["poly"]) and free:
                        self.node(x, y, f"{name} corner", name)
        adj = {i: [] for i in range(len(self.nodes))}
        members = {}
        for i, n in enumerate(self.nodes):
            for a in n["areas"]:
                members.setdefault(a, []).append(i)
        for name, idx in members.items():
            boxes = [(r[0] - self.R, r[1] - self.R, r[2] + self.R, r[3] + self.R) for r in self.areas[name]["obst"]]
            for k, i in enumerate(idx):
                for j in idx[k + 1:]:
                    p, q = self.nodes[i], self.nodes[j]
                    p, q = (p["x"], p["y"]), (q["x"], q["y"])
                    if any(self.crosses(p, q, b) for b in boxes):
                        continue
                    d = math.hypot(q[0] - p[0], q[1] - p[1])
                    adj[i].append((j, d))
                    adj[j].append((i, d))
        for i, j, c in self.links:
            adj[i].append((j, c))
            adj[j].append((i, c))
        self._adj = adj
        return adj

    def dijkstra(self, src, extra=()):
        adj = self.graph()
        more = {}
        for i, j, c in extra:
            more.setdefault(i, []).append((j, c))
            more.setdefault(j, []).append((i, c))
        dist, prev = {src: 0.0}, {src: None}
        todo = [(0.0, src)]
        while todo:
            d, i = heapq.heappop(todo)
            if d > dist[i]:
                continue
            for j, c in adj[i] + more.get(i, []):
                if d + c < dist.get(j, 1e18):
                    dist[j] = d + c
                    prev[j] = i
                    heapq.heappush(todo, (d + c, j))
        return dist, prev

    @staticmethod
    def path(prev, j):
        out = []
        while j is not None:
            out.append(j)
            j = prev[j]
        return out[::-1]


W = Walk()
FRAMES = {}         # line id -> (node, the angle that walks into it)
FARS = {}           # colour (RED: (RED, floor)) -> (node, angle)
LEVERS = {}         # lane -> node
SHUTTER_NODE = None


def angle_of(out):
    return round(math.degrees(math.atan2(out[1], out[0]))) % 360


def front(a, b, out, d=32):
    return ((a[0] + b[0]) / 2 - out[0] * d, (a[1] + b[1]) / 2 - out[1] * d)


# === the look: each area its own walls, floor, ceiling and light ===================================
def look(wall, ftex, ctex, light, ceil, color=None):
    return dict(ceil=ceil, light=light, color=tint(color), **dress(wall=wall, ftex=ftex, ctex=ctex))


SKY = "F_SKY1"


def sky(wall, ftex, light, ceil):
    d = look(wall, ftex, "KC", light, ceil)
    d["ctex"] = SKY
    return d


def fit(box, features=(), holes=(), floor=0, **base):
    """A rectangular room (x1, y1, x2, y2) with furniture and holes: the room
    is cut along every feature's and hole's edges; cells in a hole are left
    out (void: a pillar, a pier, a wall), each other cell gets the room's
    properties changed by every feature it is in (later ones win; RUNNER is
    MAP11's strip of carpet under lights). Cells alike are joined."""
    x1, y1, x2, y2 = box
    xs = sorted({x1, x2} | {v for r, _ in features for v in (r[0], r[2]) if x1 < v < x2}
                | {v for h in holes for v in (h[0], h[2]) if x1 < v < x2})
    ys = sorted({y1, y2} | {v for r, _ in features for v in (r[1], r[3]) if y1 < v < y2}
                | {v for h in holes for v in (h[1], h[3]) if y1 < v < y2})
    cells = {}
    for i, (a, c) in enumerate(zip(xs, xs[1:])):
        for j, (b, d) in enumerate(zip(ys, ys[1:])):
            if any(h[0] <= a and c <= h[2] and h[1] <= b and d <= h[3] for h in holes):
                continue
            props = dict(base, floor=floor)
            for (fa, fb, fc, fd), change in features:
                if fa <= a and c <= fc and fb <= b and d <= fd:
                    if change.get("runner"):
                        props.update(ceil=base["ceil"] + 16, light=min(255, base["light"] + 30),
                                     ftex="AJRUG", ctex="AJLITE", lift=16)
                    else:
                        props.update(change)
            cells[i, j] = props
    runs = {}
    for j in range(len(ys) - 1):
        i = 0
        while i < len(xs) - 1:
            if (i, j) not in cells:
                i += 1
                continue
            k = i
            while (k + 1, j) in cells and cells[k + 1, j] == cells[i, j]:
                k += 1
            key = (i, k + 1, repr(sorted(cells[i, j].items(), key=repr)))
            if key in runs and runs[key][-1][1] == j:
                runs[key][-1][1] = j + 1
            else:
                runs.setdefault(key, []).append([j, j + 1, cells[i, j]])
            i = k + 1
    for (i1, i2, _), spans in sorted(runs.items(), key=lambda kv: (kv[1][0][0], kv[0][0])):
        for j1, j2, props in spans:
            m.sector(rect(xs[i1], ys[j1], xs[i2], ys[j2]), **props)


RUNNER = dict(runner=True)


def block(height, top="BT", side=None):      # a bench, a desk, a table: MAP11's (box())
    return I1.box(height, top, side)


def solid(part, top):                        # to the ceiling: a pillar, a stack, a tank (MAP11's pillar())
    return dict(floor=top, **dress(side=part))


def gap(a, b, out, z, near, far_part, A, B_, thick=64, color=None):
    """An open way `thick` through a wall from the area A (whose wall is
    `near`) to the area B_ (wall `far_part`); a-b its 64- or 128-wide mouth on
    A's side. The walk's node is its middle."""
    ajarmap.opening(m, a, b, out, z, thick=thick, color=tint(color))
    over(a, b, near)
    over(*I1._far(a, b, out, thick), far_part)
    c = ((a[0] + b[0]) / 2 + out[0] * thick / 2, (a[1] + b[1]) / 2 + out[1] * thick / 2)
    return W.node(c[0], c[1], f"{A}/{B_}", A, B_)


def joint(a, b, A, B_):
    """Two areas side by side along the wall piece a-b, open between them."""
    return W.node((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, f"{A}/{B_}", A, B_)


def frame(a, b, out, n, z, area, color=None, tag=0):
    ajarmap.recess(m, a, b, out, z, n, far_id(RED), color=tint(color), tag=tag)
    f = front(a, b, out)
    FRAMES[n] = (W.node(f[0], f[1], f"frame {n}", area), angle_of(out))


def far(a, b, out, colour, z, area, color=None, tag=0, key=None):
    ajarmap.recess(m, a, b, out, z, far_id(colour), 101, far_colour=colour, color=tint(color), tag=tag)
    if area:
        f = front(a, b, out)
        FARS[key or colour] = (W.node(f[0], f[1], f"far side {key or colour}", area), angle_of(out))


def fixed(n, a1, a2, a_out, a_z, A, b1, b2, b_out, b_z, B_, trim=None):
    """Fixed doorway n (ajarmap.doorway): a walk link both ways."""
    ajarmap.doorway(m, n, a1, a2, a_out, a_z, b1, b2, b_out, b_z, trim=trim)
    fa, fb = front(a1, a2, a_out), front(b1, b2, b_out)
    i, j = W.node(fa[0], fa[1], f"doorway {n}a", A), W.node(fb[0], fb[1], f"doorway {n}b", B_)
    W.link(i, j, 32)
    return i, j


def lamp(a, b, out, z, k, part):
    """A lamp of the count of beats left: a lit niche in the wall a-b (24
    wide), with tag LAMP_TAG + k (src/zscript/clock.zs lights it)."""
    c, d = (a[0] + out[0] * 8, a[1] + out[1] * 8), (b[0] + out[0] * 8, b[1] + out[1] * 8)
    m.sector([a, b, d, c], floor=z + 56, ceil=z + 88, light=120, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF",
             id=LAMP_TAG + k)
    over(a, b, part)


def things(kind, *spots, angle=0):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle)


# =================================================================================================
# THE GROUND FLOOR, WEST
# =================================================================================================
# --- the yard: open, south-west; the porter's hut ---------------------------------------------------
YARD = sky("PU", "FP", 224, 384)
HUT = (1344, 448, 1600, 704)                 # ONESIDE site 2: the porter's hut, 256 square (plain for now)
# ONESIDE site 2: the hut's "inside", a room about 1024 x 768, is to go in the free ground
# at x 256..1280, y -1088..-320 (south of the yard, nothing built there).
fit((0, 0, 2880, 1216), [((640, 832, 896, 896), dict(floor=32, **dress(side="PS"), ftex=T("PT") if LOOK else "AJBOARD")),
                         ((2304, 128, 2496, 192), dict(floor=32, **dress(side="PS"), ftex=T("PT") if LOOK else "AJBOARD"))],
    holes=[HUT], **YARD)
W.area("yard", (0, 0, 2880, 1216), G, obst=[HUT, (640, 832, 896, 896), (2304, 128, 2496, 192)])
fit((1360, 464, 1584, 688), **look("CK", "FC", "KC", 150, 128))         # the hut
W.area("hut", (1360, 464, 1584, 688), G)
ajarmap.roomdoor(m, (1440, 688), (1504, 688), (0, 1), 0)                # its door, from the yard
W.link(W.node(1472, 660, "hut door", "hut"), W.node(1472, 732, "hut door", "yard"), 72)
frame((0, 320), (0, 384), (-1, 0), 119, G, "yard")                     # Y1: the start of a track
frame((2048, 0), (2112, 0), (0, -1), 120, G, "yard")

# --- the regulator room: the levers, behind glass at the delay hall's west end -----------------------
REG = look("CA", "FN", "KC", 176, 128)
fit((64, 1280, 368, 2048), [((64, 1280, 112, 1344), block(48, "DT", "DS"))], **REG)
W.area("regulator", (64, 1280, 368, 2048), G, obst=[(64, 1280, 112, 1344)])
LANE_Y = {1: 1440, 2: 1664, 3: 1888}         # the lanes' middles
for lane, y in LANE_Y.items():               # a lever for each lane on the west wall, in the lanes' order
    a, b = (64, y - 32), (64, y + 32)
    m.cut(a, b)
    m.line(a, b, special=130, args=(EMIT_TID + lane,), playeruse=True, repeatspecial=True,
           mid=T("CL") if LOOK else "AJLEVR", exact=True, id=LEVER_ID + lane)
    LEVERS[lane] = W.node(96, y, f"lever {lane}", "regulator")
for k in range(LAPS):                        # the beats left, between the long lane's lever and the middle's
    lamp((64, 1496 + 32 * k), (64, 1520 + 32 * k), (-1, 0), G, k, "CA")
for y1, y2 in ((1600, 1728), (1824, 1952)):  # glass onto the hall, down the middle and short lanes
    m.sector(rect(368, y1, 448, y2), floor=40, ceil=104, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    for x in (368, 448):
        m.line((x, y1), (x, y2), mid="AJGLAS", midboth=True, blocking=True, blockhitscan=True, blockprojectiles=True)
REG_DOOR = gap((160, 1216), (224, 1216), (0, 1), G, "PU", "CA", "yard", "regulator")

# --- the delay hall: three lanes ---------------------------------------------------------------------
XW, XE = 448, 2496                           # the long lane's west and east frames' mouths
HALL = look("LA", "FA", "KA", 200, 256, RUST)
PIER = {2: (XE - 1024 - 96, LANE_Y[2] - 64, XE - 1024, LANE_Y[2] + 64),
        3: (XE - 512 - 96, LANE_Y[3] - 64, XE - 512, LANE_Y[3] + 64)}
CONTACT_X = XE - 192                         # each lane's contact: just behind its emitter
EMIT_X = XE - 160
strips = []
for lane, y in LANE_Y.items():
    west = XW if lane == 1 else XE - LANES[lane]
    strips += [((west, y - 32, XE, y + 32), RUNNER)]
for lane, y in LANE_Y.items():               # the contact: a bright band across the lane, its west edge the line
    strips += [((CONTACT_X, y - 32, CONTACT_X + 16, y + 32), dict(light=255))]
fit((XW, 1280, XE, 2048), strips + [((832, 1920, 960, 2048), block(64)), ((640, 1856, 768, 1984), block(48)),
                                    ((640, 1600, 704, 1728), block(96))],
    holes=list(PIER.values()), **HALL)
W.area("hall", (XW, 1280, XE, 2048), G, obst=list(PIER.values()) + [(832, 1920, 960, 2048), (640, 1856, 768, 1984),
                                                                    (640, 1600, 704, 1728)])
for lane, y in LANE_Y.items():
    m.line((CONTACT_X, y - 32), (CONTACT_X, y + 32), special=130, args=(CONTACT_TID + lane,), missilecross=True,
           repeatspecial=True)
    m.thing(CONTACT_X, y + 48, LANE_CONTACT_T, id=CONTACT_TID + lane, args=(lane,))
    m.thing(EMIT_X, y, EMITTER_T, angle=0, id=EMIT_TID + lane, args=(SPEED, 0, lane))
frame((XW, 1408), (XW, 1472), (-1, 0), 101, G, "hall")          # the long lane, west
frame((XE, 1408), (XE, 1472), (1, 0), 102, G, "hall")           # ... east
frame((XE - 1024, 1632), (XE - 1024, 1696), (-1, 0), 103, G, "hall")    # the middle lane, west (its pier's east face)
frame((XE, 1632), (XE, 1696), (1, 0), 104, G, "hall")
frame((XE - 512, 1856), (XE - 512, 1920), (-1, 0), 105, G, "hall")      # the short lane, west (its pier)
frame((XE, 1856), (XE, 1920), (1, 0), 106, G, "hall")
HALL_SE = gap((2240, 1216), (2368, 1216), (0, 1), G, "PU", "LA", "yard", "hall")

# --- the north corridor, the stair hall and the stair -----------------------------------------------
CORR = look("CO", "FC", "KC", 168, 192, MINT)
fit((448, 2112, 2944, 2288), [((1600, 2112, 1664, 2288), dict(light=200)), ((2368, 2112, 2432, 2288), dict(light=200))],
    **CORR)
W.area("ncorr", (448, 2112, 2944, 2288), G)
gap((1152, 2048), (1280, 2048), (0, 1), G, "LA", "CO", "hall", "ncorr")
frame((2240, 2288), (2304, 2288), (0, 1), 128, G, "ncorr")
STAIRS = look("LB", "FE", "KE", 184, 448, STEEL)
fit((640, 2288, 832, 2560), **dict(STAIRS, ceil=192))
W.area("stairhall", (640, 2288, 832, 2560), G)
joint((640, 2288), (832, 2288), "ncorr", "stairhall")
fit((448, 2368, 640, 2496), **STAIRS)       # the foot
W.area("foot", (448, 2368, 640, 2496), G)
joint((640, 2368), (640, 2496), "foot", "stairhall")
frame((512, 2368), (576, 2368), (0, -1), 107, G, "foot")        # the foot: facing up the flight
ajarmap.stairs(m, (448, 2496), (640, 2496), (0, 1), G, U, steps=16, depth=32, ceil=448, light=184,
               color=tint(STEEL), **dress(wall="LB", ftex="FE", ctex="KE"))
W.area("flight", (448, 2496, 640, 3008), G)
joint((448, 2496), (640, 2496), "foot", "flight")
fit((448, 3008, 640, 3136), floor=U, **STAIRS)                   # the head
W.area("head", (448, 3008, 640, 3136), U)
joint((448, 3008), (640, 3008), "flight", "head")
frame((512, 3136), (576, 3136), (0, 1), 108, U, "head")         # the head: facing down the flight

# =================================================================================================
# THE UPPER FLOOR, WEST AND NORTH
# =================================================================================================
SPINE = look("CO", "FC", "KC", 176, U + 192, MINT)
pools = [((x, 3072, x + 64, 3200), dict(light=210)) for x in range(1024, 7936, 512)]
fit((704, 3072, 7936, 3200), pools, floor=U, **SPINE)
W.area("spine", (704, 3072, 7936, 3200), U)
gap((640, 3072), (640, 3136), (1, 0), U, "LB", "CO", "head", "spine")

# --- the hall with no size: its four walls are the clock tower's four faces -----------------------
NOSIZE = (1536, 2608, 1920, 2992)
fit(NOSIZE, [((1664, 2736, 1792, 2864), dict(light=230))], floor=U, **look("EX", "FE", "KE", 196, U + 192, STEEL))
W.area("nosize", NOSIZE, U)
gap((1568, 2992), (1632, 2992), (0, 1), U, "EX", "CO", "nosize", "spine", thick=80)

# --- the drawing office and the workshop, south of the spine --------------------------------------
fit((768, 2688, 1408, 3008), [((832, 2752, 960, 2880), block(48)), ((1088, 2752, 1216, 2880), block(48)),
                              ((832, 2944, 1216, 3008), block(48, "UT", "US"))],
    floor=U, **look("LA", "FA", "KA", 188, U + 192, RUST))
W.area("drawing", (768, 2688, 1408, 3008), U, obst=[(832, 2752, 960, 2880), (1088, 2752, 1216, 2880), (832, 2944, 1216, 3008)])
gap((1280, 3008), (1344, 3008), (0, 1), U, "LA", "CO", "drawing", "spine")
fit((2048, 2688, 2880, 3008), [((2176, 2752, 2304, 2880), solid("TK", U + 64)), ((2560, 2752, 2688, 2880), solid("TK", U + 64))],
    floor=U, **look("EX", "FE", "KE", 180, U + 192, STEEL))
W.area("workshop", (2048, 2688, 2880, 3008), U, obst=[(2176, 2752, 2304, 2880), (2560, 2752, 2688, 2880)])
gap((2400, 3008), (2464, 3008), (0, 1), U, "EX", "CO", "workshop", "spine")

# --- four offices north of the spine -----------------------------------------------------------------
OFFICES = [(704, 1216), (1280, 1792), (1856, 2368), (2432, 2880)]
for k, (x1, x2) in enumerate(OFFICES):
    desks = [((x1 + 64, 3392, x1 + 192, 3456), block(40, "DT", "DS")), ((x2 - 192, 3648, x2 - 64, 3712), block(40, "DT", "DS"))]
    fit((x1, 3264, x2, 3968), desks, floor=U, **look("AR", "FR", "KA", 150 + 12 * k, U + 192, DIM))
    W.area(f"office{k}", (x1, 3264, x2, 3968), U, obst=[r for r, _ in desks])
    cx = (x1 + x2) // 2 // 64 * 64
    gap((cx, 3200), (cx + 64, 3200), (0, 1), U, "CO", "AR", "spine", f"office{k}")
frame((1504, 3968), (1568, 3968), (0, 1), 124, U, "office1")

# --- the north wing: the archive of clocks and the timekeepers' office ------------------------------
stacks = [((x, 3392, x + 64, 3840), solid("SK", U + 192)) for x in (3200, 3456, 3712)]
fit((3008, 3264, 3968, 3968), stacks, floor=U, **look("AR", "FR", "KA", 140, U + 192, DIM))
W.area("archive", (3008, 3264, 3968, 3968), U, obst=[r for r, _ in stacks])
gap((3072, 3200), (3200, 3200), (0, 1), U, "CO", "AR", "spine", "archive")
fit((4096, 3264, 5120, 3968), [((4352, 3520, 4864, 3584), block(40, "DT", "DS"))], floor=U,
    **look("LB", "FL", "KL", 190, U + 192, PALE))
W.area("timekeepers", (4096, 3264, 5120, 3968), U, obst=[(4352, 3520, 4864, 3584)])
gap((4544, 3200), (4672, 3200), (0, 1), U, "CO", "LB", "spine", "timekeepers")
frame((4576, 3968), (4640, 3968), (0, 1), 125, U, "timekeepers")

# =================================================================================================
# THE GROUND FLOOR, MIDDLE
# =================================================================================================
# --- the porch, the entrance hall (the start) and the cloakroom ---------------------------------
fit((2880, 320, 3456, 448), **look("CO", "FC", "KC", 180, 160, MINT))
W.area("porch", (2880, 320, 3456, 448), G)
joint((2880, 320), (2880, 448), "yard", "porch")
ENTR = look("LB", "FL", "KL", 210, 256, PALE)
desk = (3776, 832, 4224, 896)
fit((3456, 256, 4544, 1280), [(desk, block(40, "DT", "DS")),
                              ((3648, 448, 3712, 512), solid("PI", 256)), ((4288, 448, 4352, 512), solid("PI", 256)),
                              ((3648, 1024, 3712, 1088), solid("PI", 256)), ((4288, 1024, 4352, 1088), solid("PI", 256))],
    **ENTR)
W.area("entrance", (3456, 256, 4544, 1280), G, obst=[desk, (3648, 448, 3712, 512), (4288, 448, 4352, 512),
                                                    (3648, 1024, 3712, 1088), (4288, 1024, 4352, 1088)])
joint((3456, 320), (3456, 448), "porch", "entrance")
hang((3904, 256), (4096, 256), "ST")                                        # the street doors, behind the start
hang((3456, 1088), (3456, 1216), "NB")                                      # the clock
frame((4544, 896), (4544, 960), (1, 0), 118, G, "entrance")
fit((3008, 512, 3392, 1024), [((3008, 512, 3040, 1024), block(48, "UT", "US"))], **look("CK", "FC", "KC", 160, 160, PAPER))
W.area("cloak", (3008, 512, 3392, 1024), G, obst=[(3008, 512, 3040, 1024)])
for y in (576, 704, 832):
    hang((3008, y), (3008, y + 64), "CT")
# ONESIDE site 3: the cloakroom's doorway off the entrance hall (plain for now)
gap((3456, 704), (3456, 768), (-1, 0), G, "LB", "CK", "entrance", "cloak")
fit((4544, 512, 5056, 640), **look("CO", "FC", "KC", 176, 160, MINT))     # the way east to the canteen
W.area("eastway", (4544, 512, 5056, 640), G)
joint((4544, 512), (4544, 640), "entrance", "eastway")

# --- the court: open; the clock tower in its middle is the inside-out booth -----------------------
COURT = sky("LB", "FC", 232, 512)
BOOTH = (3904, 2048, 4096, 2240)
beds = [((3264, 1600, 3520, 1664), dict(floor=32, **dress(side="TS"), ftex=T("TT") if LOOK else "AJBOARD")),
        ((4480, 1600, 4736, 1664), dict(floor=32, **dress(side="TS"), ftex=T("TT") if LOOK else "AJBOARD")),
        ((3264, 2624, 3520, 2688), dict(floor=32, **dress(side="TS"), ftex=T("TT") if LOOK else "AJBOARD")),
        ((4480, 2624, 4736, 2688), dict(floor=32, **dress(side="TS"), ftex=T("TT") if LOOK else "AJBOARD"))]
fit((3008, 1344, 4992, 2944), beds, holes=[BOOTH], **COURT)
W.area("court", (3008, 1344, 4992, 2944), G, obst=[BOOTH] + [r for r, _ in beds])
gap((3936, 1280), (4064, 1280), (0, 1), G, "LB", "LB", "entrance", "court")
gap((2944, 2176), (2944, 2240), (1, 0), G, "CO", "LB", "ncorr", "court")
far((3968, 2944), (4032, 2944), (0, 1), BLUE, G, "court")
frame((3264, 1344), (3328, 1344), (0, -1), 127, G, "court")
# the four faces of the tower, each the far end of a fixed doorway whose
# near end is a wall of the hall with no size: from the hall the court is
# seen looking north, east, south and west from the tower
cx, cy = (NOSIZE[0] + NOSIZE[2]) // 2, (NOSIZE[1] + NOSIZE[3]) // 2
bx, by = (BOOTH[0] + BOOTH[2]) // 2, (BOOTH[1] + BOOTH[3]) // 2
for n, (dx, dy) in zip((1, 2, 3, 4), ((0, 1), (1, 0), (0, -1), (-1, 0))):
    hx, hy = cx + dx * 192, cy + dy * 192                                   # the hall's wall, its middle
    tx, ty = bx + dx * 96, by + dy * 96                                     # the tower's face, its middle
    a1, a2 = (P(hx - dy * 32, hy - dx * 32), P(hx + dy * 32, hy + dx * 32))
    b1, b2 = (P(tx - dy * 32, ty - dx * 32), P(tx + dy * 32, ty + dx * 32))
    fixed(n, a1, a2, (dx, dy), U, "nosize", b1, b2, (-dx, -dy), G, "court")

# ONESIDE site 1: the corridor between the court and the rotunda (plain for
# now). The way east is to be longer than the way back west: free ground
# for an extra stretch of about 1024 is kept north of it, x 4992..5440,
# y 2368..2944 (nothing built there).
fit((4992, 2176, 5440, 2304), **look("CO", "FC", "KC", 170, 192, MINT))
W.area("oneside", (4992, 2176, 5440, 2304), G)
joint((4992, 2176), (4992, 2304), "court", "oneside")

# --- the rotunda: eight-sided, a pillar, a stub from it to the south wall: the arena --------------
ROT = (5440, 1600, 6592, 2752)
OCT = ajarmap.octagon(*ROT, 320)
PILLAR = (5888, 2048, 6144, 2304)
STUB = (5936, 1600, 6096, 2048)
ROTL = look("EX", "FE", "KE", 172, 384, STEEL)


def clip(poly, cell):
    """The convex polygon `poly` cut to the box `cell`."""
    pts = rect(*cell)
    cx, cy = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    for a, b in zip(poly, poly[1:] + poly[:1]):
        def side(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        s0 = 1 if side((cx, cy)) > 0 else -1
        keep = []
        for p, q in zip(pts, pts[1:] + pts[:1]):
            sp, sq = side(p) * s0, side(q) * s0
            if sp >= 0:
                keep.append(p)
            if sp * sq < 0:
                t = sp / (sp - sq)
                keep.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        pts = keep
        if len(pts) < 3:
            return []
    out = []
    for p in pts:
        p = tuple(int(v) if v == int(v) else v for v in p)
        if p not in out:
            out.append(p)
    return out if len(out) > 2 else []


rot_pools = [((5632, 2432, 5760, 2560), dict(light=210)), ((6272, 2432, 6400, 2560), dict(light=210)),
             ((5632, 1792, 5760, 1920), dict(light=210)), ((6272, 1792, 6400, 1920), dict(light=210))]
xs = sorted({5440, 5760, 5888, 5936, 6096, 6144, 6272, 6592} | {v for r, _ in rot_pools for v in (r[0], r[2])})
ys = sorted({1600, 1920, 2048, 2304, 2432, 2752} | {v for r, _ in rot_pools for v in (r[1], r[3])})
for xa, xb in zip(xs, xs[1:]):
    for ya, yb in zip(ys, ys[1:]):
        if any(h[0] <= xa and xb <= h[2] and h[1] <= ya and yb <= h[3] for h in (PILLAR, STUB)):
            continue
        piece = clip(OCT, (xa, ya, xb, yb))
        if not piece:
            continue
        props = dict(ROTL)
        for r, change in rot_pools:
            if r[0] <= xa and xb <= r[2] and r[1] <= ya and yb <= r[3]:
                props.update(change)
        m.sector(piece, **props)
W.area("rotunda", OCT, G, obst=[PILLAR, STUB])
joint((5440, 2176), (5440, 2304), "oneside", "rotunda")
frame((5984, 2752), (6048, 2752), (0, 1), 109, G, "rotunda")             # north
frame((6592, 2240), (6592, 2304), (1, 0), 110, G, "rotunda")             # east
frame((5440, 1984), (5440, 2048), (-1, 0), 111, G, "rotunda")            # west
frame((5936, 1760), (5936, 1824), (1, 0), 112, G, "rotunda")             # the stub's west face
frame((6096, 1760), (6096, 1824), (-1, 0), 113, G, "rotunda")            # ... and its east face

# --- the lift: basement, ground, upper east; RED's far side is in the car --------------------------
CAR = (6720, 1920, 6912, 2112)
m.sector(rect(*CAR), floor=G, ceil=G + 128, light=200, color=tint(PAPER), id=LIFT, **dress(wall="EV", ftex="FE", ctex="KE"))
far((6784, 1920), (6848, 1920), (0, -1), RED, G, None, color=PAPER, tag=LIFT)


def landing(x1, y1, x2, y2, z):
    m.sector(rect(x1, y1, x2, y2), floor=z, ceil=z + 112, light=176, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")


landing(6688, 1968, 6720, 2064, G)
landing(6912, 1968, 6944, 2064, B)
landing(6768, 2112, 6864, 2144, U)
fit((6592, 1968, 6688, 2064), **look("CO", "FC", "KC", 176, 128, MINT))
W.area("liftway", (6592, 1968, 6688, 2064), G)
joint((6592, 1968), (6592, 2064), "rotunda", "liftway")
for z in (B, G, U):
    W.area(f"car{z}", CAR, z)
# the car's own buttons (AJLB0 the basement, 1 the ground, 2 the upper floor) and a call button at each landing
ajarmap.lift_button(m, (6720, 1928), (6720, 1960), G, CAR_TIDS, (6752, 1952), tex="AJLB1", foot=True)
ajarmap.lift_button(m, (6912, 1928), (6912, 1960), B, CAR_TIDS + 1, (6880, 1952), tex="AJLB0", foot=True)
ajarmap.lift_button(m, (6728, 2112), (6760, 2112), U, CAR_TIDS + 2, (6752, 2080), tex="AJLB2", foot=True)
ajarmap.lift_button(m, (6600, 1968), (6632, 1968), G, CAR_TIDS + 3, (6616, 2000), tex="AJLB1", foot=True)
LAND = {}
LAND[G] = (W.node(6704, 2016, "landing G", "liftway", f"car{G}"))
CARN = {z: W.node(6816, 1968, f"car {z}", f"car{z}") for z in (B, G, U)}   # RED's far side, in the car at z
for z in (B, G, U):
    FARS[(RED, z)] = (CARN[z], 270)
RIDE = 4                                    # the car, units a tic
for z1, z2 in ((B, G), (G, U), (B, U)):
    W.link(CARN[z1], CARN[z2], abs(z2 - z1) / RIDE * RUN)
W.link(CARN[G], LAND[G], 0)

# --- the canteen and the kitchen (south-east); the kitchen's steps down to the basement -------------
tables = [((x, y, x + 128, y + 64), block(32, "TT", "TS")) for x in (5248, 5504, 5760, 6016) for y in (576, 832, 1088)]
counter = (6336, 576, 6400, 1216)
fit((5056, 320, 6400, 1472), tables + [(counter, block(40, "DT", "DS"))], **look("CA", "FN", "KC", 200, 256, PAPER))
W.area("canteen", (5056, 320, 6400, 1472), G, obst=[r for r, _ in tables] + [counter])
joint((5056, 512), (5056, 640), "eastway", "canteen")
hang((5568, 1472), (5696, 1472), "MN")
frame((5600, 320), (5664, 320), (0, -1), 121, G, "canteen")
ovens = [((6528, 896, 6784, 1024), solid("TK", 64)), ((6528, 384, 6784, 512), solid("TK", 64))]
fit((6400, 320, 6912, 1472), ovens, **look("LA", "FA", "KA", 190, 256, RUST))
W.area("kitchen", (6400, 320, 6912, 1472), G, obst=[r for r, _ in ovens])
joint((6400, 320), (6400, 576), "canteen", "kitchen")
joint((6400, 1216), (6400, 1472), "canteen", "kitchen")
for x1 in (5792, 6144):                                                     # two ways up to the rotunda, either side of the stub
    fit((x1, 1472, x1 + 96, 1600), **look("CO", "FC", "KC", 176, 192, MINT))
    W.area(f"rotway{x1}", (x1, 1472, x1 + 96, 1600), G)
    joint((x1, 1472), (x1 + 96, 1472), "canteen", f"rotway{x1}")
    joint((x1, 1600), (x1 + 96, 1600), f"rotway{x1}", "rotunda")
STEP = dict(light=150, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
ajarmap.stairs(m, (6912, 1344), (6912, 1472), (1, 0), G, -128, steps=8, depth=32, ceil=96, **STEP)
ajarmap.stairs(m, (7168, 1344), (7168, 1472), (1, 0), -128, -128, steps=8, depth=32, ceil=-32, **STEP)
W.area("steps", (6912, 1344, 7424, 1472), G)
joint((6912, 1344), (6912, 1472), "kitchen", "steps")

# =================================================================================================
# THE BASEMENT (EAST)
# =================================================================================================
BASE = dict(floor=B)
# the cellar, at the foot of the kitchen's steps; the stores south of it
fit((7424, 1152, 7936, 1872), [((7616, 1344, 7744, 1472), solid("TK", B + 192)), ((7808, 1600, 7936, 1728), solid("TK", B + 192))],
    **BASE, **look("PU", "FP", "KP", 152, B + 192, COLD))
W.area("cellar", (7424, 1152, 7936, 1872), B, obst=[(7616, 1344, 7744, 1472), (7808, 1600, 7936, 1728)])
joint((7424, 1344), (7424, 1472), "steps", "cellar")
shelves = [((7232, y, 7744, y + 48), solid("SK", B + 192)) for y in (448, 704)]
fit((7040, 256, 7936, 1088), shelves, **BASE, **look("AR", "FR", "KA", 144, B + 192, DIM))
W.area("stores", (7040, 256, 7936, 1088), B, obst=[r for r, _ in shelves])
gap((7616, 1088), (7744, 1088), (0, 1), B, "AR", "PU", "stores", "cellar")
far((7040, 512), (7040, 576), (-1, 0), GREEN, B, "stores")
frame((7040, 896), (7040, 960), (-1, 0), 122, B, "stores")
frame((7936, 576), (7936, 640), (1, 0), 123, B, "stores")
fit((6944, 1936, 7936, 2096), **BASE, **look("PU", "FP", "KP", 140, B + 160, COLD))
W.area("mid", (6944, 1936, 7936, 2096), B)
gap((7616, 1872), (7744, 1872), (0, 1), B, "PU", "PU", "cellar", "mid")
LAND[B] = W.node(6928, 2016, "landing B", "mid", f"car{B}")
ajarmap.lift_button(m, (6944, 2064), (6944, 2096), B, CAR_TIDS + 4, (6976, 2064), tex="AJLB0", foot=True)
boilers = [((7168, 2304, 7296, 2432), solid("TK", B + 224)), ((7424, 2304, 7552, 2432), solid("TK", B + 224))]
fit((7040, 2160, 7936, 2592), boilers + [((7680, 2432, 7872, 2592), dict(light=200))],
    **BASE, **look("PU", "FP", "KQ", 144, B + 224, COLD))
W.area("boiler", (7040, 2160, 7936, 2592), B, obst=[r for r, _ in boilers])
gap((7616, 2096), (7744, 2096), (0, 1), B, "PU", "PU", "mid", "boiler")
# the shutter: up while a pulse lives (AjarDelayShutter, clock.zs), from the boiler room into the night room
ajarmap.way_out(m, 7616, 2608, None, floor=B)
m.sector(rect(7744, 2592, 7808, 2608), floor=B, ceil=B, light=160, wall="AJSHUT", ftex="AJTRIMF", ctex="AJTRIMF",
         id=SHUTTER_TAG)
for p, q in (((7744, 2592), (7744, 2608)), ((7808, 2592), (7808, 2608))):
    m.line(p, q, mid="AJTRIM", dontpegbottom=True)
m.line((7744, 2592), (7808, 2592), id=SHUTTER_ID)
SHUTTER_NODE = W.node(7776, 2568, "the shutter", "boiler")
for k in range(LAPS):
    lamp((7712 - 32 * k, 2592), (7736 - 32 * k, 2592), (0, 1), B, k, "PU")
m.thing(7600, 2500, DELAY_T, args=(SHUTTER_TAG, LAMP_TAG, LAPS))

# =================================================================================================
# THE UPPER FLOOR, EAST
# =================================================================================================
fit((6736, 2144, 6896, 3072), [((6736, 2560, 6896, 2624), dict(light=210))], floor=U, **look("CO", "FC", "KC", 176, U + 192, MINT))
W.area("gallery", (6736, 2144, 6896, 3072), U)
LAND[U] = W.node(6816, 2128, "landing U", "gallery", f"car{U}")
joint((6736, 3072), (6896, 3072), "gallery", "spine")
ajarmap.lift_button(m, (6736, 2160), (6736, 2192), U, CAR_TIDS + 5, (6768, 2176), tex="AJLB2", foot=True)
for z in (B, U):
    W.link(CARN[z], LAND[z], 0)

# --- the six-sided hall: north-east joined to south-west for good, frames north and south ----------
HX, HY, HS = 5952, 3616, 320
HH = HS * math.sqrt(3) / 2
HEXV = [P(HX + HS, HY), P(HX + HS / 2, HY + HH), P(HX - HS / 2, HY + HH), P(HX - HS, HY),
        P(HX - HS / 2, HY - HH), P(HX + HS / 2, HY - HH)]                    # E, NE, NW, W, SW, SE


def along(a, b, u):
    """The point u along the wall a-b from its middle."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    return P((a[0] + b[0]) / 2 + (b[0] - a[0]) / L * u, (a[1] + b[1]) / 2 + (b[1] - a[1]) / L * u)


E_, NE, NW, W_, SW, SE = HEXV
ne1, ne2 = along(E_, NE, -32), along(E_, NE, 32)                             # the joined walls' mouths
sw1, sw2 = along(W_, SW, -32), along(W_, SW, 32)
nw1, nw2 = along(NW, W_, -48), along(NW, W_, 48)                             # the doorways: 96 wide
se1, se2 = along(SE, E_, -48), along(SE, E_, 48)
n1, n2 = P(HX + 32, HY + HH), P(HX - 32, HY + HH)                             # the frames, north and south
s1, s2 = P(HX - 32, HY - HH), P(HX + 32, HY - HH)
outline = [E_, ne1, ne2, NE, n1, n2, NW, nw1, nw2, W_, sw1, sw2, SW, s1, s2, SE, se1, se2]
HEXL = look("LB", "FL", "KL", 212, U + 192, PALE)
m.sector(outline, floor=U, **HEXL)
W.area("hex", HEXV, U)


def unit(a, b):
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[1] - a[1]) / L, -(b[0] - a[0]) / L)                           # the outward normal of a wall a-b (clockwise)


out_ne, out_sw = unit(E_, NE), unit(W_, SW)
out_ne = (-out_ne[0], -out_ne[1]) if out_ne[0] < 0 else out_ne
out_sw = (-out_sw[0], -out_sw[1]) if out_sw[0] > 0 else out_sw
fixed(5, ne1, ne2, out_ne, U, "hex", sw1, sw2, out_sw, U, "hex")
frame(n1, n2, (0, 1), 114, U, "hex")
frame(s1, s2, (0, -1), 115, U, "hex")
# the doorways in the two other slanted walls: a neck out to a straight corridor
NWX, SEX = 5504, 6400
m.sector([nw1, nw2, (NWX, nw2[1]), (NWX, nw1[1])], floor=U, **HEXL)
m.sector([se1, se2, (SEX, se2[1]), (SEX, se1[1])], floor=U, **HEXL)
fit((5376, 3200, NWX, 3840), floor=U, **look("CO", "FC", "KC", 176, U + 192, MINT))
fit((SEX, 3200, 6528, 3584), floor=U, **look("CO", "FC", "KC", 176, U + 192, MINT))
W.area("hexwest", (5376, 3200, NWX, 3840), U)
W.area("hexeast", (SEX, 3200, 6528, 3584), U)
joint((5376, 3200), (NWX, 3200), "spine", "hexwest")
joint((SEX, 3200), (6528, 3200), "spine", "hexeast")
W.node((nw1[0] + nw2[0]) / 2, (nw1[1] + nw2[1]) / 2, "hex door w", "hex", "hexwest")
W.node((se1[0] + se2[0]) / 2, (se1[1] + se2[1]) / 2, "hex door e", "hex", "hexeast")

# --- the room that is its own neighbour: north joined to south for good, frames east and west ------
SQ = (6656, 3392, 7040, 3776)
fit(SQ, [((6784, 3520, 6912, 3648), dict(light=220))], floor=U, **look("CK", "FC", "KC", 184, U + 160, PAPER))
W.area("square", SQ, U)
fixed(6, (6816, 3776), (6880, 3776), (0, 1), U, "square", (6816, 3392), (6880, 3392), (0, -1), U, "square")
frame((7040, 3552), (7040, 3616), (1, 0), 116, U, "square")
frame((6656, 3552), (6656, 3616), (-1, 0), 117, U, "square")
gap((6688, 3200), (6752, 3200), (0, 1), U, "CO", "CK", "spine", "square", thick=192)

# --- the regulator store, far east: both ORANGE leaves ---------------------------------------------
store_benches = [((7424, 3456, 7552, 3520), block(48)), ((7680, 3456, 7808, 3520), block(48))]
fit((7296, 3328, 7936, 3968), store_benches, floor=U, **look("LA", "FA", "KA", 192, U + 192, RUST))
W.area("orange", (7296, 3328, 7936, 3968), U, obst=[r for r, _ in store_benches])
gap((7552, 3200), (7680, 3200), (0, 1), U, "CO", "LA", "spine", "orange", thick=128)
frame((7936, 3584), (7936, 3648), (1, 0), 126, U, "orange")


# =================================================================================================
# DOORS, THINGS, COMPANY
# =================================================================================================
m.thing(4000, 416, 1, angle=90)                                             # the start: the entrance hall
ajarmap.pair(m, TEAL, (3584, 640, 0), (4416, 640, 180))                     # both TEAL leaves, at the start
ajarmap.pair(m, ORANGE, (7488, 3800, 270), (7744, 3800, 270))               # both ORANGE leaves, far east upstairs
ajarmap.door(m, RED, 5700, 2480, angle=315)                                 # in the rotunda, by the lift
ajarmap.door(m, GREEN, 900, 3800, angle=270)                                # the furthest find: the far north-west office
ajarmap.door(m, BLUE, 2752, 2944, angle=270)                                # the workshop, upstairs

# --- weapons, in the order of MAP15 to MAP17, and ammunition for the size --------------------------
m.thing(4000, 560, 2001)                                                    # shotgun: the entrance hall
things(2008, (3900, 560), (4100, 560))
things(2011, (3520, 320), (4480, 320))
m.thing(3200, 896, 2002)                                                    # chaingun: the cloakroom
things(2048, (3300, 896))
m.thing(3300, 640, 8)                                                       # backpack
m.thing(4000, 1500, 82)                                                     # super shotgun: the court, seen from the hall with no size
things(2049, (3150, 1450), (4850, 1450), (3150, 2850))
things(2012, (4850, 2850))
m.thing(6016, 2624, 2003)                                                   # rocket launcher: the rotunda, north of the pillar
things(2046, (5600, 2240), (6432, 2240))
things(2010, (5952, 2624), (6080, 2624))
m.thing(7616, 3900, 2004)                                                   # plasma rifle: the regulator store
things(17, (7360, 3900), (7872, 3900))
things(2047, (7616, 3400))
# the yard and the regulator room
things(2049, (2700, 1100), (300, 900))
things(2018, (1472, 560))                                                   # green armour, in the porter's hut
things(2012, (300, 1990))
things(2007, (2600, 150), (1100, 150))
things(2011, (2780, 600), (100, 100))
# the delay hall: the endless corridor's cache, at the long lane's west end (by 101)
things(2046, (512, 1340), (512, 1540))
things(2012, (560, 1340))
things(2049, (2400, 2000))
things(2048, (900, 2160), (2700, 2160))                                     # the north corridor
# the endless stair: the foot's cache, seen from the head through the head frame
things(2012, (480, 2448), (608, 2448))
things(2049, (544, 2448))
things(2008, (544, 3060))
# the moving room: blue armour rides in the car
m.thing(6880, 2064, 2019)
# upstairs west
things(2049, (1000, 2780), (2120, 2720))
things(2048, (1100, 3900), (2300, 3900))
things(2012, (1728, 2800))                                                  # the hall with no size
things(2046, (2800, 3350), (3900, 3900))
things(17, (4200, 3300))
things(2012, (4900, 3900), (1300, 3300))
things(2047, (5000, 3300))
# round the pillar: the megasphere in the pocket east of the stub
m.thing(6200, 1680, 83)
things(2046, (5520, 1980), (6500, 1980))
things(2012, (5700, 2600), (6350, 2600))
# the canteen and the kitchen
things(2049, (5150, 1400), (6300, 400))
things(2048, (5700, 1400))
things(2012, (6850, 400), (6850, 1250))
things(2046, (6450, 1300))
# the six-sided hall's cache, and the room that is its own neighbour
things(17, (5900, 3616), (6004, 3616))
m.thing(6848, 3640, 2013)                                                   # a soul sphere
things(2012, (7300, 3150), (5440, 3700))
# the basement
things(2049, (7500, 1200), (7300, 1000))
things(2046, (7880, 1180), (7100, 300))
things(17, (7880, 300), (7600, 1000))
things(2012, (7100, 1000), (7880, 1000), (7100, 2200), (7880, 2200))
things(2047, (7500, 2016), (7100, 2016))
m.thing(7600, 600, 2013)                                                    # a soul sphere among the stores

# --- monsters, area by area --------------------------------------------------------------------------
things(ZOMBIE, (400, 800), (1000, 300), (1800, 900), (2200, 600), (2600, 300), (900, 1100), angle=90)       # the yard
things(SERGEANT, (1200, 1000), (2000, 300), (2500, 900), (700, 500), angle=90)
things(IMP, (1700, 200), (2100, 1100), (1100, 600), (2700, 1000), (500, 200), (1500, 1050), angle=90)
things(DEMON, (1900, 600), (2400, 400), angle=90)
m.thing(1472, 600, ZOMBIE, angle=270)                                       # the porter
things(IMP, (250, 1700), (250, 1950), angle=180)                            # the regulator room
things(IMP, (1000, 1350), (1600, 1350), (2200, 1550), (1200, 1980), (2000, 2000), angle=180)  # the delay hall
things(SERGEANT, (800, 1550), (1700, 1800), (2300, 1750), angle=180)
things(CHAINGUNNER, (2400, 1320), (1150, 1750), angle=180)
m.thing(1800, 1980, KNIGHT, angle=180)
things(DEMON, (600, 1450), (1300, 1550), angle=0)
things(SPECTRE, (2100, 1850), (1550, 2000), angle=180)
things(ZOMBIE, (900, 2200), (1500, 2200), (2100, 2200), angle=0)            # the north corridor
things(IMP, (2600, 2200), (1200, 2250), angle=0)
m.thing(544, 2900, IMP, angle=270)                                          # the stair
m.thing(560, 3080, SERGEANT, angle=270)
things(ZOMBIE, (1100, 3136), (2800, 3136), (4400, 3136), (6000, 3136), angle=0)     # the spine
things(IMP, (2000, 3136), (3600, 3136), (5200, 3136), (7200, 3136), angle=180)
things(IMP, (1620, 2700), (1840, 2700), (1620, 2900), angle=90)             # the hall with no size
m.thing(1840, 2900, KNIGHT, angle=180)
things(IMP, (1300, 2950), (1000, 2720), angle=180)                          # the drawing office
m.thing(850, 2720, SERGEANT, angle=0)
m.thing(2450, 2800, CHAINGUNNER, angle=270)                                 # the workshop
things(IMP, (2100, 2950), (2800, 2720), angle=270)
m.thing(2450, 2950, REVENANT, angle=270)
for k, (x1, x2) in enumerate(OFFICES):                                      # the offices
    things(IMP, (x1 + 96, 3600), (x2 - 116, 3850), angle=270)
    m.thing((x1 + x2) // 2, 3350, (SERGEANT, KNIGHT, CHAINGUNNER, SPECTRE)[k], angle=270)
things(IMP, (3350, 3600), (3600, 3600), (3850, 3600), angle=270)            # the archive
things(SPECTRE, (3100, 3900), (3600, 3320), angle=270)
things(SERGEANT, (4200, 3400), (5000, 3400), angle=270)                     # the timekeepers
m.thing(4600, 3800, CHAINGUNNER, angle=270)
m.thing(4200, 3850, KNIGHT, angle=270)
m.thing(3100, 384, ZOMBIE, angle=0)                                         # the porch
things(ZOMBIE, (3600, 1150), (4400, 1150), (3550, 350), (4450, 350), angle=90)      # the entrance hall
things(SERGEANT, (3900, 960), (4100, 960), angle=270)
things(IMP, (3600, 800), (4400, 800), angle=270)
things(SERGEANT, (3200, 600), (3300, 960), angle=0)                         # the cloakroom
things(IMP, (3300, 1450), (4700, 1450), (3200, 2000), (4800, 2000), (3300, 2850), (4700, 2850), angle=270)  # the court
things(SERGEANT, (3600, 1800), (4400, 1800), (3600, 2500), (4400, 2500), angle=270)
things(CHAINGUNNER, (3800, 2800), (4200, 2800), angle=270)
things(CACO, (3500, 2200), (4500, 2200), (4000, 1720), angle=270)
things(KNIGHT, (3700, 1500), (4300, 1500), angle=90)
things(REVENANT, (3100, 2400), (4900, 2400), angle=270)
things(DEMON, (3800, 2350), (4200, 1950), angle=270)
m.thing(5200, 2240, IMP, angle=180)                                         # the corridor to the rotunda
things(IMP, (5600, 2400), (6400, 2400), (5800, 2650), (6250, 2650), (5650, 1750), (6350, 1800), angle=180)   # the rotunda
things(DEMON, (5700, 2150), (6300, 2150), (6016, 2450), angle=180)
things(SPECTRE, (5800, 1700), (6250, 1950), angle=90)
things(CACO, (5750, 2560), (6300, 2560), angle=270)
things(REVENANT, (5560, 2100), (6480, 2100), angle=180)
m.thing(6016, 2560, MANCUBUS, angle=270)
things(KNIGHT, (5650, 1950), (6350, 1850), angle=90)
m.thing(6150, 2400, BARON, angle=270)
things(CHAINGUNNER, (5520, 2300), (6500, 2300), angle=180)
things(IMP, (6816, 2500), (6816, 2900), angle=270)                         # the lift's gallery
things(IMP, (5150, 450), (5440, 450), (5700, 450), (5950, 450), angle=180)  # the canteen
things(SERGEANT, (6250, 450), (5150, 1000), (5440, 1000), angle=180)
things(ZOMBIE, (5700, 760), (5950, 1000), (6250, 1000), angle=180)
things(DEMON, (5440, 1300), (5950, 1300), angle=270)
m.thing(6250, 760, CHAINGUNNER, angle=180)
things(IMP, (6600, 700), (6800, 1200), angle=180)                           # the kitchen
m.thing(6600, 1250, DEMON, angle=180)
m.thing(6850, 600, SPECTRE, angle=180)
things(IMP, (7550, 1250), (7850, 1250), angle=180)                          # the cellar
things(SPECTRE, (7550, 1700), (7700, 1800), angle=90)
m.thing(7500, 1550, CHAINGUNNER, angle=90)
m.thing(7880, 1450, REVENANT, angle=180)
things(IMP, (7150, 350), (7850, 350), (7500, 600), angle=90)                # the stores
things(SERGEANT, (7150, 900), (7850, 900), angle=90)
things(KNIGHT, (7500, 1000), (7500, 350), angle=90)
m.thing(7850, 600, CACO, angle=180)
things(ZOMBIE, (7200, 2016), (7450, 2016), (7850, 2016), angle=0)           # the corridor under the lift
things(IMP, (7100, 2250), (7350, 2500), (7650, 2250), angle=180)            # the boiler room
things(REVENANT, (7100, 2520), (7880, 2300), angle=180)
m.thing(7900, 2500, KNIGHT, angle=180)
m.thing(7350, 2220, MANCUBUS, angle=90)
m.thing(7700, 2400, CHAINGUNNER, angle=270)
things(IMP, (5852, 3616), (6052, 3616), (5952, 3480), angle=270)            # the six-sided hall
things(CACO, (5952, 3760), (5800, 3700), angle=270)
things(IMP, (5440, 3400), (6464, 3400), angle=90)                           # its two ways in
things(SERGEANT, (6750, 3480), (6950, 3700), (6720, 3700), angle=270)       # the room that is its own neighbour
things(CHAINGUNNER, (7400, 3900), (7850, 3900), angle=270)                  # the regulator store
things(REVENANT, (7600, 3650), (7350, 3650), angle=270)
m.thing(7850, 3650, KNIGHT, angle=270)
things(IMP, (7600, 3400), (7900, 3400), angle=90)

# --- ambushes: when each door is first taken, and the first time a pulse makes a lap --------------
# a TEAL leaf: sergeants round you in the entrance hall, then imps in from the court
ajarmap.ambush(m, 10 + TEAL, SERGEANT, (3700, 400), (4300, 400), (4000, 720), angle=90)
ajarmap.ambush(m, 10 + TEAL, IMP, (3700, 1200), (4300, 1200), angle=270, after=3)
# an ORANGE leaf: lost souls round you in the regulator store, revenants on the spine 4 s later
ajarmap.ambush(m, 10 + ORANGE, SOUL, (7400, 3500), (7800, 3500), (7600, 3750), angle=270)
ajarmap.ambush(m, 10 + ORANGE, REVENANT, (7616, 3136), (7300, 3120), angle=90, after=4)
# RED: the arena wakes: spectres round the pillar, a mancubus at the lift's way 3 s later
ajarmap.ambush(m, 10 + RED, SPECTRE, (5650, 2500), (6350, 2500), (6200, 2650), angle=270)
ajarmap.ambush(m, 10 + RED, MANCUBUS, (6480, 1900), angle=180, after=3)
# GREEN: chaingunners at the offices' doors when you are back on the spine, a cacodemon 5 s later
ajarmap.ambush(m, 10 + GREEN, CHAINGUNNER, (1536, 3136), (2112, 3136), angle=180, near=700)
ajarmap.ambush(m, 10 + GREEN, CACO, (1000, 3500), angle=270, after=5)
# BLUE: knights in the hall with no size, imps in the workshop 2 s later
ajarmap.ambush(m, 10 + BLUE, KNIGHT, (1680, 2800), (1780, 2800), angle=90)
ajarmap.ambush(m, 10 + BLUE, IMP, (2200, 2720), (2650, 2950), (2900 - 64, 2720), angle=180, after=2)
# the first lap a pulse makes: the run is on, and the yard and the canteen fill
ajarmap.ambush(m, 50, IMP, (600, 1000), (1400, 300), (2300, 900), angle=90)
ajarmap.ambush(m, 50, DEMON, (2700, 500), (3000, 384), angle=180, after=2)
ajarmap.ambush(m, 50, REVENANT, (5300, 900), (6150, 1250), angle=180, after=4)
ajarmap.ambush(m, 50, SPECTRE, (7650, 2520), (7880, 2016), angle=180, after=6)


# =================================================================================================
# THE MEASURE: ONE PIECE ON FOOT, THE WAYS AND THE CLOCK (checked when the level is built)
# =================================================================================================
def tics(units):
    return units / RUN


def lap(*lanes):
    """A lap of the loop through `lanes`, in tics: the pulse flies 32 more
    than the mouths are apart in each (portal line to portal line)."""
    return sum(LANES[k] + 32 for k in lanes) / SPEED


def life(*lanes):
    """How long a pulse fired in lanes[0] lives, the loop through `lanes`:
    from the emitter east to the east frame's portal, through the other
    lanes, from the first lane's west frame to its contact (the first lap),
    then LAPS - 1 laps more (MAP=MAP18 MODE=4 measures it to the tic)."""
    first = (XE + 16 - (EMIT_X + 20)) + sum(LANES[k] + 32 for k in lanes[1:]) + CONTACT_X - (XE - LANES[lanes[0]] - 16)
    return (first + (LAPS - 1) * SPEED * lap(*lanes)) / SPEED


def measure():
    adj = W.graph()
    lines, bad = [], []
    # one piece on foot, with no door hung
    seen, todo = {0}, [0]
    while todo:
        for j, _ in adj[todo.pop()]:
            if j not in seen:
                seen.add(j)
                todo.append(j)
    if len(seen) != len(W.nodes):
        lost = sorted({W.nodes[i]["label"] for i in range(len(W.nodes)) if i not in seen})
        bad.append(f"not one piece on foot: {', '.join(lost[:8])}")
    areas = {a for n in W.nodes for a in n["areas"]}
    if areas != set(W.areas):
        bad.append(f"areas with no way in: {sorted(set(W.areas) - areas)}")
    lever = LEVERS[1]
    dL, pL = W.dijkstra(lever)
    dS, pS = W.dijkstra(SHUTTER_NODE)
    dlev = [W.dijkstra(LEVERS[k])[0] for k in LEVERS]
    near_l = min(min(d[n] for d in dlev) for n, _ in list(FRAMES.values()) + list(FARS.values()))
    near_s = min(dS[n] for n, _ in list(FRAMES.values()) + list(FARS.values()))
    lines.append(f"MAP18: one piece on foot: {len(W.areas)} areas, {len(W.nodes)} nodes, {len(FRAMES)} frames, "
                 f"{len(FARS)} far sides (RED's at three floors); the nearest frame or far side "
                 f"{near_l:.0f} on foot from a lever, {near_s:.0f} from the shutter")
    if near_l < NEAR or near_s < NEAR:
        bad.append(f"a frame or far side nearer than {NEAR} to a lever ({near_l:.0f}) or the shutter ({near_s:.0f})")
    w0 = dL[SHUTTER_NODE]
    track = [n for n in FRAMES if n not in (101, 102)]                     # TEAL hangs in the long lane
    fars = {RED: [FARS[(RED, z)][0] for z in (B, G, U)], GREEN: [FARS[GREEN][0]], BLUE: [FARS[BLUE][0]]}

    def one(colour):
        best = w0
        for f in track:
            fn = FRAMES[f][0]
            if colour == ORANGE:
                for g in track:
                    if g != f:
                        best = min(best, dL[fn] + 32 + dS[FRAMES[g][0]])
            else:
                for x in fars[colour]:
                    best = min(best, dL[fn] + 32 + dS[x], dL[x] + 32 + dS[fn])
        return best

    # every door on the track at once: a search over (key node, doors used)
    keys = [lever, SHUTTER_NODE] + [FRAMES[f][0] for f in track] + [x for v in fars.values() for x in v]
    keys = list(dict.fromkeys(keys))
    D = {k: W.dijkstra(k) for k in keys}
    frame_of = {FRAMES[f][0]: f for f in track}
    far_of = {x: c for c, v in fars.items() for x in v}
    bit = {ORANGE: 1, RED: 2, GREEN: 4, BLUE: 8}
    start = (lever, 0, None)
    best = {start: 0.0}
    back = {start: None}
    todo = [(0.0, start)]
    goal = None
    while todo:
        d, st = heapq.heappop(todo)
        if d > best[st]:
            continue
        k, used, came = st
        if k == SHUTTER_NODE:
            goal = st
            break
        moves = []
        for k2 in keys:                                                     # walk to another key node
            if k2 != k and k2 in D[k][0]:
                moves.append(((k2, used, None), D[k][0][k2], ("walk",)))
        if k in frame_of and k != came:                                     # hang a door here and go through
            f = frame_of[k]
            if not used & bit[ORANGE]:
                for g in track:
                    if g != f:
                        moves.append(((FRAMES[g][0], used | bit[ORANGE], FRAMES[g][0]), 32, ("pair", f, g)))
            for c in (RED, GREEN, BLUE):
                if not used & bit[c]:
                    for x in fars[c]:
                        moves.append(((x, used | bit[c], None), 32, ("door", c, f, x)))
        if k in far_of and k != came:                                       # through a far side to where its door hangs
            c = far_of[k]
            if not used & bit[c]:
                for g in track:
                    moves.append(((FRAMES[g][0], used | bit[c], FRAMES[g][0]), 32, ("back", c, g, k)))
        for st2, cost, how in moves:
            if d + cost < best.get(st2, 1e18):
                best[st2] = d + cost
                back[st2] = (st, how)
                heapq.heappush(todo, (d + cost, st2))
    w_all = best[goal]
    steps, st = [], goal
    while back[st]:
        st, how = back[st][0], back[st][1]
        steps.append((st, how))
    steps.reverse()
    hung, used_frames = {}, []
    for (k, _, _), how in steps:
        if how[0] == "pair":
            hung[ORANGE] = (how[1], how[2])
            used_frames += [how[1], how[2]]
        elif how[0] == "door":
            hung[how[1]] = (how[2], how[3])
            used_frames.append(how[2])
        elif how[0] == "back":
            hung[how[1]] = (how[2], how[3])
            used_frames.append(how[2])
    if len(set(used_frames)) != len(used_frames):
        bad.append(f"the best track hangs two doors in one frame: {hung}")
    ws = {c: one(c) for c in (ORANGE, RED, GREEN, BLUE)}
    w1 = min(ws.values())
    t = {k: life(k) for k in LANES}
    t_lm = life(1, 2)
    pairs = {(a, b): life(a, b) for a, b in ((1, 2), (1, 3), (2, 3))}
    name = {ORANGE: "ORANGE", RED: "RED", GREEN: "GREEN", BLUE: "BLUE"}
    lines.append(f"    the run, at {RUN} a tic (LAPS {LAPS}, the pulse {SPEED} a tic): lever to shutter on foot "
                 f"{w0:.0f} ({tics(w0):.0f} tics)" + "".join(f"; {name[c]} only {ws[c]:.0f} ({tics(ws[c]):.0f})" for c in ws)
                 + f"; all of them {w_all:.0f} ({tics(w_all):.0f})")
    lines.append("    the clock (fired to burnt out): " + ", ".join(f"{NAMES[k]} {t[k]:.0f} tics ({lap(k):.1f} a lap)" for k in LANES)
                 + "; " + ", ".join(f"lanes {a}+{b} {v:.0f} tics ({lap(a, b):.1f} a lap)" for (a, b), v in pairs.items()))
    ratio = tics(w0) / t[1]
    spare_lm = t_lm - tics(w0)
    spare_1 = t[1] - tics(w1)
    lines.append(f"    the long lane alone, nothing on the track: the way takes {ratio:.2f} of its time; both Pairs "
                 f"in lanes 1 and 2, on foot: {spare_lm:.0f} tics spare; the long lane and the best single link: "
                 f"{spare_1:.0f} tics spare")
    lines.append("    the best track with everything (TEAL in the long lane): "
                 + ", ".join(f"{name[c]} {v[0]}" + (f" and {v[1]}" if c == ORANGE else "") for c, v in hung.items()))
    if not 1.25 <= ratio <= 1.45:
        bad.append(f"the long lane alone with nothing on the track: the way is {ratio:.2f} of its time, not about 4/3")
    if spare_lm < 0:
        bad.append(f"both Pairs in lanes 1 and 2 are not enough on foot ({spare_lm:.0f} tics)")
    if spare_1 < 105:
        bad.append(f"the long lane and the best single link leave {spare_1:.0f} tics, under 3 seconds")
    return lines, bad, dict(dL=dL, pL=pL, w0=w0, steps=steps, hung=hung, D=D, goal=goal)


MEASURE, PROBLEMS, _R = measure()
if PROBLEMS:
    raise SystemExit("MAP18: " + "; ".join(PROBLEMS) + "\n" + "\n".join(MEASURE))


# --- the measured ways as MapSpots, for the smoke tests (map18.zs) ---------------------------------
def spots(first, nodes, dy=0):
    """MapSpots `first` + 1, 2, ... at the nodes of a way; args[0] 1 where the
    way goes through a door here (args[1] the angle to walk it in). Way B's
    stand 1 north of where way A's would (no two things on one spot)."""
    for i, (x, y, through, ang) in enumerate(nodes):
        m.thing(round(x), round(y) + dy, MAPSPOT, id=first + 1 + i, angle=ang if through == 1 else 0, args=(through, ang))


angle_at = {n: a for n, a in list(FRAMES.values()) + list(FARS.values())}
D, steps = _R["D"], _R["steps"]
legs = []                                    # (node, through a door here)
for idx, ((k, used, came), how) in enumerate(steps):
    nxt = steps[idx + 1][0][0] if idx + 1 < len(steps) else _R["goal"][0]
    if how[0] == "walk":
        legs += [(i, False) for i in Walk.path(D[k][1], nxt)[:-1]]
    else:
        legs.append((k, True))
CARZ = {n: z for z, n in CARN.items()}


def as_spots(legs):
    """(x, y, what, angle): what 1 through a door at `angle`, 2 a ride in
    the car to the floor `angle` - 512 (the car's buttons), 0 a plain walk."""
    out, prev = [], None
    for n, through in legs:
        x, y = W.nodes[n]["x"], W.nodes[n]["y"]
        if prev in CARZ and n in CARZ and CARZ[prev] != CARZ[n]:
            out.append((x, y, 2, CARZ[n] + 512))
        elif through:
            out.append((x, y, 1, angle_at[n]))
        else:
            out.append((x, y, 0, 0))
        prev = n
    return out


route_a = as_spots(legs)
route_b = as_spots([(i, False) for i in Walk.path(_R["pL"], SHUTTER_NODE)[:-1]])
for r in (route_a, route_b):                 # the shutter, and beyond it into the night room and out by its east end
    r += [(7776, 2568, 0, 0), (7776, 2648, 0, 0), (7776, 2736, 0, 0), (7904, 2736, 0, 0)]
hung = _R["hung"]
red_floor = next((z for z in (B, G, U) if RED in hung and hung[RED][1] == CARN[z]), G)
# the doors hung for way A: ORANGE's two frames, RED's, GREEN's, BLUE's; RED's car's floor + 512
m.thing(200, 200, MAPSPOT, id=ROUTE_A, args=(*(hung[ORANGE] if ORANGE in hung else (0, 0)),
                                           hung[RED][0] if RED in hung else 0, hung[GREEN][0] if GREEN in hung else 0,
                                           hung[BLUE][0] if BLUE in hung else 0))
m.thing(264, 200, MAPSPOT, id=ROUTE_A - 1, args=(red_floor + 512,))
spots(ROUTE_A, route_a)
spots(ROUTE_B, route_b, dy=1)
MEASURE.append(f"    the ways as MapSpots: A {len(route_a)} spots (tid {ROUTE_A + 1} on), B {len(route_b)} ({ROUTE_B + 1} on); "
               f"RED's car at {red_floor}")
I1.m = _theirs

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
