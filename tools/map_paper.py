"""Act 2, level 9: "On Paper" (MAP19), the pass office. It wears MAP11's look
(AJAR_INSTITUTE), as MAP16 to MAP18 do. PLAN.md, "MAP19 'On Paper': the first
version, as decided"; the pass, its double, the registers and the pass desks
are the pass lab's (map PASS, tools/map_pass.py, src/zscript/pass.zs).

The rule (the lab's): through any portal of the game's the player lands at the
far side and a white double walks on through the wall behind the frame; from
then on it is at T(player), a turn, a shift and a change of height that change
only at a crossing. A register is signed when the double has stood on its
plate, at its height, for a second. Each register opens a steel door.

Phase 1 of the build (this file as it stands): the building, its doors, frames,
sealed rooms and glass, the fixed paradoxes, the way out, the fights, the
measure and the checks. Every register and every pass desk goes through
register() and pass_desk() below, which for now only record them (the measure
uses them) and put a MapSpot; each register's steel door is a plain tagged
door the test script opens. The lap constants are named at the top.

Floors (each area at its own height, side by side in plan: no room over room):
the basement -256, the ground 0, the upper floor 256; the water tower's stair
-128, its sealed stair to -512.

Places, south to north (x east, y north; about 8000 x 5600):
  the gatehouse: the pass hall (the start; the brass frames; RED), the
    forecourt (open; RED's far side; the duty room behind glass, frame 101)
  the covered way (one-sided: longer going than coming) to the block
  the block, ground floor: the lobby (the porter's lodge, secret), the
    gallery (121), the archive (the stack behind glass, 102; the reading
    corridor, GREEN's far side), the canteen and kitchen, the link hall (105,
    106; the sealed gallery behind 106; the east strongroom, VIOLET), offices,
    the east lane (open) to the east yard (112, GREEN hung)
  the stair hall (BLUE's far side, 104; the hall with no stair behind glass)
    and the upper floor (the side room, 103; the drawing office, TEAL; the
    hall with no size; 122; the balcony over the pond court)
  the pond court (open; the pond, the island, the kiosk with YELLOW, the
    boathouse behind 113, the boat store bigger inside; ORANGE)
  the basement (BLUE; 123; the plasma rifle)
  the garden (open; the avenue, 109 and 110; the gazebo; 124)
  the tower yard (open; YELLOW's far side; the water tower, 107 and 108, its
    sealed stair; the tower's strongroom, PINK; 111)
  the night room (way_through: VIOLET and PINK's far sides)

No PUZZLE: ten doors and nineteen frames are too many states. Instead this
module checks, when it is built, the facts the design rests on (MEASURE): the
stages open in order, each in one piece on foot; every court has a way in
with empty hands and a way out for a door; and the registers, by the rule's
geometry (rectangle arithmetic under quarter turns); the build fails if not.
"""
import heapq
import math

import ajarmap
import map_institute1 as I1
import map_clockdept as CD                    # MAP18's one-sided doorway sign (its SIGNPLATES are drawn by gfx.py)
from ajarmap import RED, GREEN, BLUE, YELLOW, VIOLET, PINK, TEAL, ORANGE, far_id, HOME
from map_institute1 import T, dress, tint, over, hang, LOOK
from map_institute1 import ZOMBIE, SERGEANT, IMP, DEMON, SPECTRE, CHAINGUNNER, KNIGHT, REVENANT, CACO
from map_institute1 import BARON, SOUL, MANCUBUS
from udmf import MONSTERS, Map, rect

# --- the laps: set from the pass lab's measured figures in phase 2 ---------------------------------
# LINK_LAP: how far one lap of the link hall (a Pair in 105 and 106, walked east into 106 and out of
# 105) moves the double, east; for now the distance between the two frames' portal lines.
# STAIR_LAP: the same for the water tower's flight (a Pair in 107 and 108, walked down into 107 and
# out of 108): (along, down).
LINK_LAP = 544
STAIR_LAP = (544, 128)
LINK_LAPS, STAIR_LAPS = 5, 3                 # the laps that sign registers 5 and 6
PLATE = 128                                  # a register's plate: a square this wide (the lab's)
TOL_Z = 16                                   # the double is on the plate if its feet are this near it
RUN = 16.7                                   # the player running, units a tic (the test runs)

m = Map()
# MAP11's helpers draw on the map `m` of their own module: for as long as
# this file runs that is this map (put back at the end), as in MAP12 to MAP18.
_theirs, I1.m = I1.m, m
_cd, CD.m = CD.m, m                           # ... and MAP18's fit() draws on its module's `m`
if LOOK:
    import gfx_institute
    m.align |= gfx_institute.ALIGNED

G, U, B = 0, 256, -256                       # the ground, the upper floor, the basement
TOWER_FOOT = -128                            # the water tower's stair: its head is on the ground
MAPSPOT = 9001
REG_TAG = {n: 1900 + n for n in range(1, 8)}  # each register's steel door (sector tag)
LODGE_TAG, BRIDGE_TAG = 1908, 1909           # the porter's lodge's door; the island's footbridge (phase 2)
BRIDGE_RAIL = 1910                           # line id: the pond's railing where the footbridge lands
REGISTER_T = 9001                            # phase 1: a register is a MapSpot (the lab's thing in phase 2)
REG_SPOT, DESK_SPOT = 1950, 1970             # their tids: + the register's number; + the desk's
PROG, VIEW = 3000, 2900                      # MapSpots: the test run's program (map19.zs), the views
FENCE = 48                                   # no monster nearer than this to an odd face or a gate

PALE, MINT, PAPER, DIM, RUST, COLD, STEEL = 0xDCE8DC, 0xC8E0C8, 0xF0E4C8, 0xB0B8C8, 0xE8C8B0, 0xA8C0D8, 0xC8D0E0
GLASS = dict(mid="AJGLAS", midboth=True, blocking=True, blockhitscan=True, blockprojectiles=True)
TALL_GLASS = dict(GLASS, wrapmidtex=True)
RAIL = dict(mid="AJGRIL", midboth=True, blocking=True, dontpegbottom=True)


def P(x, y):
    return (round(x, 3), round(y, 3))


# === the walk: a graph of waypoints over convex areas (MAP18's, with heights that may slope) ========
class Walk:
    """Convex walkable pieces ("areas"), each at one height or sloping
    (stairs: `ramp` = (axis, c0, z0, c1, z1)), and points in them ("nodes"):
    the middle of every opening between two areas (it is in both), a point
    32 in front of every frame and far side. Two nodes of one area are
    joined by a straight line unless it passes through an obstacle grown by
    the player's radius. `link` is a way both ways (a steel door: `tag`, open
    or not); `arc` one way only: a drop, a turnstile, a one-sided doorway's
    face (`portal`: the angle it is walked through, for the tests)."""
    R = 16

    def __init__(self):
        self.areas = {}
        self.nodes = []
        self.links = []
        self.arcs = []
        self.portals = {}            # (node, node): the angle that walks through a portal from the first to the second
        self.sealed = set()          # areas nobody walks in: the rooms behind glass (for the checks)

    def area(self, name, shape, z, obst=(), ramp=None):
        assert name not in self.areas, name
        self.areas[name] = dict(box=tuple(shape), z=z, obst=[tuple(o) for o in obst], ramp=ramp)

    def z_at(self, name, x, y):
        a = self.areas[name]
        if not a["ramp"]:
            return a["z"]
        axis, c0, z0, c1, z1 = a["ramp"]
        c = x if axis == "x" else y
        t = min(1, max(0, (c - c0) / (c1 - c0)))
        return z0 + (z1 - z0) * t

    def node(self, x, y, label, *areas):
        self.nodes.append(dict(x=x, y=y, label=label, areas=set(areas)))
        return len(self.nodes) - 1

    def link(self, i, j, cost, tag=0):
        self.links.append((i, j, cost, tag))

    def arc(self, i, j, cost, portal=None, kind="walk"):
        """One way only, from node i to node j. `kind`: walk, drop,
        turnstile, squeeze, portal (a one-sided doorway's face or a gate)."""
        self.arcs.append((i, j, cost, "portal" if portal is not None else kind))
        if portal is not None:
            self.portals[i, j] = portal

    @staticmethod
    def crosses(p, q, r):
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
        """Adjacency: node -> [(node, cost, kind, tag)], kind 'walk', 'door'
        (a steel door: tag), 'drop', 'turnstile', 'squeeze', 'portal'."""
        if hasattr(self, "_adj"):
            return self._adj
        for n in self.nodes:                                  # a node may name an area declared after it
            for a in n["areas"]:
                assert a in self.areas, (n["label"], a)
        for name, a in self.areas.items():                  # the corners round each obstacle
            if name in self.sealed:
                continue
            box = a["box"]
            for r in a["obst"]:
                g = self.R + 8
                for x, y in ((r[0] - g, r[1] - g), (r[0] - g, r[3] + g), (r[2] + g, r[1] - g), (r[2] + g, r[3] + g)):
                    free = all(not (o[0] - self.R < x < o[2] + self.R and o[1] - self.R < y < o[3] + self.R) for o in a["obst"])
                    if box[0] + self.R < x < box[2] - self.R and box[1] + self.R < y < box[3] - self.R and free:
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
                    adj[i].append((j, d, "walk", 0))
                    adj[j].append((i, d, "walk", 0))
        for i, j, c, tag in self.links:
            kind = "door" if tag else "walk"
            adj[i].append((j, c, kind, tag))
            adj[j].append((i, c, kind, tag))
        for i, j, c, kind in self.arcs:
            adj[i].append((j, c, kind, 0))
        radj = {i: [] for i in adj}
        for i, out in adj.items():
            for j, c, kind, tag in out:
                radj[j].append((i, c, kind, tag))
        self._adj, self._radj = adj, radj
        return adj

    def dijkstra(self, src, opened=None, reverse=False, portals=True):
        """Shortest ways from src (to src: `reverse`). `opened`: the steel
        doors' tags that are open (None: all of them); `portals`: whether the
        building's own portals may be walked through."""
        adj = self._radj if reverse else self.graph()
        dist, prev = {src: 0.0}, {src: None}
        todo = [(0.0, src)]
        while todo:
            d, i = heapq.heappop(todo)
            if d > dist[i]:
                continue
            for j, c, kind, tag in adj[i]:
                if kind == "door" and opened is not None and tag not in opened:
                    continue
                if kind == "portal" and not portals:
                    continue
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
FRAMES = {}         # line id -> the frame's portal end (see port())
FARS = {}           # colour -> the far side's portal end
PORTS = {}          # name -> a portal end: dict(c, inn, z, node, name)
CROSS = []          # the building's own crossings: (name, from end, to end)
REGISTERS = {}      # n -> dict(name, box, z, opens, centre)
DESKS = []          # (x, y): the pass desks
ODD_LINES = []      # (a, b): every odd face and gate
SIGNPLATES = CD.SIGNPLATES                    # MAP18's dict: the pictograms are drawn under MAP18's names (AJIY3nn)
SIGNS = I1.SIGNS                              # MAP11's: the words over ways and on plates (AJIS3nn)


def angle_of(v):
    return round(math.degrees(math.atan2(v[1], v[0]))) % 360


def front(a, b, out, d=32):
    return ((a[0] + b[0]) / 2 - out[0] * d, (a[1] + b[1]) / 2 - out[1] * d)


def port(name, a, b, out, z, node, depth=ajarmap.DEPTH, inn=None):
    """A portal end: its line is a-b moved `depth` along `out`; what crosses
    it going in moves along `inn` (default `out`) and comes out of another
    end going against that end's `inn`."""
    c = ((a[0] + b[0]) / 2 + out[0] * depth, (a[1] + b[1]) / 2 + out[1] * depth)
    PORTS[name] = dict(c=c, inn=tuple(inn or out), z=z, node=node, name=name)
    return PORTS[name]


# === the look: each area its own walls, floor, ceiling and light =====================================
def look(wall, ftex, ctex, light, ceil, color=None):
    return dict(ceil=ceil, light=light, color=tint(color), **dress(wall=wall, ftex=ftex, ctex=ctex))


SKY = "F_SKY1"


def sky(wall, ftex, light, ceil):
    d = look(wall, ftex, "KC", light, ceil)
    d["ctex"] = SKY
    return d


fit = CD.fit                                  # MAP18's rooms with furniture and holes (they draw on `m`: see below)
grid = CD.grid
RUNNER = CD.RUNNER


def block(height, top="BT", side=None):
    """A bench, a desk, a table, `height` over the floor of the room it is
    put in (MAP18's block(): fit() adds the room's floor)."""
    d = I1.box(height, top, side)
    d["up"] = d.pop("floor")
    return d


def solid(part, top):                        # to the ceiling: a pillar, a stack, a tank
    return dict(floor=top, **dress(side=part))


def room(box, z, look_, features=(), holes=(), obst=(), name=None, sealed=False):
    """A rectangular room: its sectors (fit) and, with `name`, its walk area
    (obstacles: every feature whose floor is more than a step over the
    room's, and the given `obst`)."""
    fit(box, list(features), holes=list(holes), floor=z, **look_)
    if name:
        ob = [r for r, d in features if d.get("up", 0) > 24 or d.get("floor", z) > z + 24] + list(obst)
        W.area(name, box, z, obst=ob)
        if sealed:
            W.sealed.add(name)


def gap(a, b, out, z, near, far_part, A, B_, thick=64, color=None):
    """An open way `thick` through a wall from the area A to the area B_; a-b
    its mouth on A's side. The walk's node is its middle."""
    ajarmap.opening(m, a, b, out, z, thick=thick, color=tint(color))
    over(a, b, near)
    over(*I1._far(a, b, out, thick), far_part)
    c = ((a[0] + b[0]) / 2 + out[0] * thick / 2, (a[1] + b[1]) / 2 + out[1] * thick / 2)
    i = W.node(c[0], c[1], f"{A}/{B_}", A, B_)
    return i


def joint(a, b, A, B_):
    """Two areas side by side along the wall piece a-b, open between them."""
    return W.node((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, f"{A}/{B_}", A, B_)


def frame(a, b, out, n, z, area, color=None):
    ajarmap.recess(m, a, b, out, z, n, far_id(RED), color=tint(color))
    f = front(a, b, out)
    node = W.node(f[0], f[1], f"frame {n}", area)
    FRAMES[n] = port(f"frame {n}", a, b, out, z, node)
    FRAMES[n]["mouth"] = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return FRAMES[n]


def far(a, b, out, colour, z, area, color=None):
    ajarmap.recess(m, a, b, out, z, far_id(colour), 101, far_colour=colour, color=tint(color))
    f = front(a, b, out)
    node = W.node(f[0], f[1], f"far side {ajarmap.NAMES[colour]}", area) if area else None
    FARS[colour] = port(f"far {ajarmap.NAMES[colour]}", a, b, out, z, node)
    FARS[colour]["mouth"] = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return FARS[colour]


def fixed(n, a1, a2, a_out, a_z, A, b1, b2, b_out, b_z, B_, trim=None):
    """Fixed doorway n (ajarmap.doorway): a crossing each way."""
    ajarmap.doorway(m, n, a1, a2, a_out, a_z, b1, b2, b_out, b_z, trim=trim)
    fa, fb = front(a1, a2, a_out), front(b1, b2, b_out)
    i, j = W.node(fa[0], fa[1], f"doorway {n}a", A), W.node(fb[0], fb[1], f"doorway {n}b", B_)
    pa = port(f"doorway {n}a", a1, a2, a_out, a_z, i)
    pb = port(f"doorway {n}b", b1, b2, b_out, b_z, j)
    W.arc(i, j, 32, portal=angle_of(a_out))
    W.arc(j, i, 32, portal=angle_of(b_out))
    CROSS.append((f"fixed doorway {n} ({A} to {B_})", pa, pb))
    CROSS.append((f"fixed doorway {n} ({B_} to {A})", pb, pa))
    return i, j


def glass(box, lines, sill=16, top=144, z=0):
    """A pane through a wall: the sector `box` (sill to top over `z`), glass
    on each of `lines`."""
    m.sector(rect(*box), floor=z + sill, ceil=z + top, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    for p, q in lines:
        m.line(p, q, **GLASS)


def pane_x(x1, x2, y1, y2, z=0, sill=16, top=144):
    """A pane in a wall running east-west (x1..x2), y1..y2 its thickness."""
    glass((x1, y1, x2, y2), [((x1, y1), (x2, y1)), ((x1, y2), (x2, y2))], sill, top, z)


def pane_y(y1, y2, x1, x2, z=0, sill=16, top=144):
    """A pane in a wall running north-south (y1..y2), x1..x2 its thickness."""
    glass((x1, y1, x2, y2), [((x1, y1), (x1, y2)), ((x2, y1), (x2, y2))], sill, top, z)


STEEL_DOORS = []    # (node a, node b, tag)


def steel_door(a, b, out, z, tag, A, B_, thick=64, near=None, far_part=None):
    """A register's steel door (ajarmap.steel), opened by its register (phase
    2) or by the test script (Door_Open on `tag`): a walk link that needs it."""
    ajarmap.steel(m, a, b, out, z, tag, thick=thick)
    if near:
        over(a, b, near)
    if far_part:
        over(*I1._far(a, b, out, thick), far_part)
    pa = (((a[0] + b[0]) / 2 - out[0] * 24), ((a[1] + b[1]) / 2 - out[1] * 24))
    pb = (((a[0] + b[0]) / 2 + out[0] * (thick + 24)), ((a[1] + b[1]) / 2 + out[1] * (thick + 24)))
    i, j = W.node(*pa, f"steel {tag} ({A})", A), W.node(*pb, f"steel {tag} ({B_})", B_)
    W.link(i, j, thick + 48, tag=tag)
    STEEL_DOORS.append((i, j, tag))
    return i, j


def squeeze(a, b, out, z, A, B_, near=None, far_part=None, thick=64):
    """A hole too small for a door (ajarmap.squeeze, 48 wide): empty hands
    only, both ways."""
    ajarmap.squeeze(m, a, b, out, z, thick=thick)
    if near:
        over(a, b, near)
    if far_part:
        over(*I1._far(a, b, out, thick), far_part)
    pa = ((a[0] + b[0]) / 2 - out[0] * 24, (a[1] + b[1]) / 2 - out[1] * 24)
    pb = ((a[0] + b[0]) / 2 + out[0] * (thick + 24), (a[1] + b[1]) / 2 + out[1] * (thick + 24))
    i, j = W.node(*pa, f"squeeze ({A})", A), W.node(*pb, f"squeeze ({B_})", B_)
    W.arc(i, j, thick + 48, kind="squeeze")
    W.arc(j, i, thick + 48, kind="squeeze")
    return i, j


def turnstile(a, b, out, z, A, B_, near=None, far_part=None, thick=64):
    """A way out only, wide enough for a door: a-b (64 wide) its mouth on
    A's side, `out` towards B_. Two steps up (16, then 40) and a drop of 40
    on B_'s side: nobody climbs back (nojump; a step is 24 at most)."""
    h = thick // 2
    c, d = (a[0] + out[0] * h, a[1] + out[1] * h), (b[0] + out[0] * h, b[1] + out[1] * h)
    e, f = (a[0] + out[0] * thick, a[1] + out[1] * thick), (b[0] + out[0] * thick, b[1] + out[1] * thick)
    trim = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.sector([a, b, d, c], floor=z + 16, ceil=z + 128, light=170, **trim)
    m.sector([c, d, f, e], floor=z + 40, ceil=z + 128, light=170, **trim)
    if near:
        over(a, b, near)
    if far_part:
        over(e, f, far_part)
    pa = ((a[0] + b[0]) / 2 - out[0] * 24, (a[1] + b[1]) / 2 - out[1] * 24)
    pb = ((a[0] + b[0]) / 2 + out[0] * (thick + 32), (a[1] + b[1]) / 2 + out[1] * (thick + 32))
    i, j = W.node(*pa, f"turnstile ({A})", A), W.node(*pb, f"turnstile ({B_})", B_)
    W.arc(i, j, thick + 56, kind="turnstile")
    return i, j


def fence(*points):
    """A blockmonsters line along `points` (a polyline on sector edges)."""
    for p, q in zip(points, points[1:]):
        m.line(p, q, blockmonsters=True)


def gate(m1, m2, out, z, line_id, target, part, area, name):
    """The far end of a one-sided doorway's odd face (MAP18's gate()): a
    16-deep recess with a portal at its back, fixed from the start; what
    walks in here comes out of `target`."""
    D, S = ajarmap.DEPTH, ajarmap.STUB
    b1, b2 = (m1[0] + out[0] * D, m1[1] + out[1] * D), (m2[0] + out[0] * D, m2[1] + out[1] * D)
    c1, c2 = (b1[0] + out[0] * S, b1[1] + out[1] * S), (b2[0] + out[0] * S, b2[1] + out[1] * S)
    trim = dict(wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
    m.sector([m1, m2, b2, b1], floor=z, ceil=z + ajarmap.DOOR_H, light=176, **trim)
    m.sector([b1, b2, c2, c1], floor=z, ceil=z + ajarmap.DOOR_H, light=96, **trim)
    m.line(b1, b2, id=line_id, special=156, args=(target, 0, 1, 1))
    over(m1, m2, part)
    ODD_LINES.append((b1, b2))
    f = front(m1, m2, out, 8)
    node = W.node(f[0], f[1], name, area)
    return port(name, m1, m2, out, z, node)


def oneway(a, b, out, z, line_id, target, near, far_part, area_face, area_mouth, name, *, thick=16, mouth_id=0):
    """A one-sided doorway (ajarmap.oneside, blind): a-b its plain mouth in
    the wall `near`; its odd face `thick` further `out`, in the wall
    `far_part` of the room it faces. Returns its two portal ends (the odd
    face, walked into against `out`; the mouth, as a target)."""
    ajarmap.oneside(m, a, b, out, z, line_id, target, thick=thick, mouth_id=mouth_id, blind=True)
    c, d = I1._far(a, b, out, thick)
    over(a, b, near)
    over(c, d, far_part)
    ODD_LINES.append((c, d))
    fo = ((c[0] + d[0]) / 2 + out[0] * 8, (c[1] + d[1]) / 2 + out[1] * 8)
    fm = ((a[0] + b[0]) / 2 - out[0] * 8, (a[1] + b[1]) / 2 - out[1] * 8)
    face = port(f"{name}'s odd face", a, b, out, z, W.node(*fo, f"{name}'s odd face", area_face), depth=thick,
                inn=(-out[0], -out[1]))
    mouth = port(f"{name}'s mouth", a, b, out, z, W.node(*fm, f"{name}'s mouth", area_mouth), depth=0)
    W.arc(mouth["node"], face["node"], thick + 16)            # from the plain side: a plain walk
    return face, mouth


def os_sign(a, b, look_out, part, ceil):
    """MAP18's sign of an odd face (map_clockdept.sign): the pictogram of a
    way that does not lead back, on the wall piece a-b (64 long) beside it."""
    if not LOOK:
        return
    h = gfx_institute.HEIGHT.get(part, 256)
    reps = -(-ceil // h)
    key = (LOOK, part, I1._shift(a, b, look_out), ceil - CD.SIGN_TOP, reps)
    m.cut(a, b)
    m.line(a, b, mid=SIGNPLATES.setdefault(key, f"AJIY{LOOK}{len(SIGNPLATES):02d}"), exact=True)


PLAQUES = []        # (a, b, words): for the views and the write-up


def plaque(a, b, look_out, part, words, z=0, niche=8, high=128, top=84):
    """A sign with `words` on the wall piece a-b (64, 128 or 192 long) of a
    room whose wall is `part`, seen looking `look_out`: a niche `niche` deep
    and `high` high in the wall, its back wall the room's wall with a plate
    on it (gfx_institute.sign, MAP11's names over ways), the plate's top
    `top` over the floor. The wall goes on over the niche."""
    PLAQUES.append((a, b, words))
    if not LOOK:
        return
    w = abs(a[0] - b[0]) + abs(a[1] - b[1])
    assert len(words) * 6 + 5 <= w, (words, w)
    c, d = (a[0] + look_out[0] * niche, a[1] + look_out[1] * niche), (b[0] + look_out[0] * niche, b[1] + look_out[1] * niche)
    m.sector([a, b, d, c], floor=z, ceil=z + high, light=200, **dress(wall=part, ftex="FC", ctex="KC"))
    over(a, b, part)
    h = gfx_institute.HEIGHT.get(part, 256)
    y = high - top                                            # the plate's top row (the wall hung from the niche's top)
    oh = h - 15 - y
    assert 0 <= y <= h - 11 and top + h > high, (words, y)
    key = (LOOK, part, words, I1._shift(c, d, look_out), w, oh)
    m.line(c, d, mid=SIGNS.setdefault(key, f"AJIS{LOOK}{len(SIGNS):02d}"), exact=True)


def register(n, name, box, z, opens):
    """A register (phase 1: recorded, a MapSpot at its plate's middle; the
    pass lab's thing in phase 2): the plate `box` at height z; signed, it
    opens the steel doors tagged `opens`."""
    c = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
    assert box[2] - box[0] == PLATE and box[3] - box[1] == PLATE, (n, box)
    REGISTERS[n] = dict(name=name, box=box, z=z, opens=opens, centre=c)
    m.thing(c[0], c[1], REGISTER_T, id=REG_SPOT + n, args=(n, opens))


def plate_box(c):
    return (c[0] - PLATE // 2, c[1] - PLATE // 2, c[0] + PLATE // 2, c[1] + PLATE // 2)


def pass_desk(x, y):
    """A pass desk (phase 1: recorded, a MapSpot; the lab's in phase 2)."""
    DESKS.append((x, y))
    m.thing(x, y, MAPSPOT, id=DESK_SPOT + len(DESKS))


def things(kind, *spots, angle=0):
    for x, y in spots:
        m.thing(x, y, kind, angle=angle)


# =================================================================================================
# THE GATEHOUSE (stage 1): the pass hall, the forecourt, the duty room; the night room apart
# =================================================================================================
ENTR = look("LB", "FL", "KL", 210, 256, PALE)
PH = (512, 256, 1280, 768)
ph_pillars = [(640, 352, 704, 416), (1088, 352, 1152, 416), (640, 608, 704, 672), (1088, 608, 1152, 672)]
room(PH, G, ENTR, grid(PH, 2, 2, 236, 96) + [(r, solid("PI", 256)) for r in ph_pillars], name="passhall")
hang((832, 256), (960, 256), "ST")                                          # the street doors, behind the start
hang((640, 768), (768, 768), "NB")                                          # notices
START = W.node(896, 352, "the start", "passhall")
# the way out: two brass frames across the hall, VIOLET and PINK's far sides in the night room
ajarmap.brass_pair(m, (512, 480), (512, 544), (1280, 480), (1280, 544), G, VIOLET, PINK)
for name_, a, b, out in (("brass west", (512, 480), (512, 544), (-1, 0)), ("brass east", (1280, 480), (1280, 544), (1, 0))):
    f = front(a, b, out)
    FRAMES[190 if out[0] < 0 else 191] = port(name_, a, b, out, G, W.node(f[0], f[1], name_, "passhall"))
NR = (64, 288)                                                              # the night room: (x, y) of its south-west corner
ajarmap.way_through(m, NR[0], NR[1], VIOLET, PINK, floor=64)
W.area("nightroom", (NR[0], NR[1], NR[0] + 320, NR[1] + 256), 64)
for colour, x, out in ((VIOLET, NR[0], (-1, 0)), (PINK, NR[0] + 320, (1, 0))):
    a, b = (x, NR[1] + 96), (x, NR[1] + 160)
    f = front(a, b, out)
    FARS[colour] = port(f"far {ajarmap.NAMES[colour]}", a, b, out, 64, W.node(f[0], f[1], f"far side {ajarmap.NAMES[colour]}", "nightroom"))
# its way out on foot: a hole in its north wall, a drop into a passage to the pass hall
m.sector(rect(192, 544, 256, 560), floor=64, ceil=160, light=150, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
room((192, 560, 448, 704), G, look("PU", "FP", "KP", 150, 128, COLD), name="nightway")
W.arc(W.node(224, 528, "the night room's hole", "nightroom"), W.node(224, 584, "the drop", "nightway"), 56, kind="drop")
gap((512, 640), (512, 704), (-1, 0), G, "LB", "PU", "passhall", "nightway")
pass_desk(1000, 720)

# --- the forecourt: open; RED's far side straight across from the duty room's frame 101 -------------
FC = (704, 832, 1280, 2048)
OPEN = sky("LB", "FL", 224, 320)
room(FC, G, OPEN, [((768, 896, 1216, 1984), dict(ftex=T("FC") if LOOK else "AJFLOOR"))], name="forecourt")
PH_N = gap((832, 768), (960, 768), (0, 1), G, "LB", "LB", "passhall", "forecourt")
frame((704, 1376), (704, 1440), (-1, 0), 101, G, "forecourt")
far((1280, 1376), (1280, 1440), (1, 0), RED, G, "forecourt")
# the duty room, sealed: glass either side of 101, its own steel door (register 1's), the chaingun
DR = (256, 1152, 624, 1664)
room(DR, G, look("CK", "FC", "KC", 176, 160, PAPER), [((256, 1152, 320, 1664), block(48, "UT", "US"))], name="dutyroom",
     sealed=True)
pane_y(1216, 1344, 624, 704)
pane_y(1472, 1568, 624, 704)
steel_door((704, 1600), (704, 1664), (-1, 0), G, REG_TAG[1], "forecourt", "dutyroom", thick=80)
REG1_C = (DR[2] - 128, 1408)                                                # 128 in from the duty room's glass wall, on 101's axis
register(1, "the duty room", plate_box(REG1_C), G, REG_TAG[1])
plaque((704, 1728), (704, 1856), (-1, 0), "LB", "REGISTER 1 DUTY ROOM")
# the barrier: register 1's steel door in the forecourt's north wall, to the covered way

# =================================================================================================
# THE COVERED WAY (stage 2's way in): longer going than coming
# =================================================================================================
# A real corridor from the barrier north to the lobby. Going north its
# one-sided doorway's odd face (facing south) sends the player into X, a plain
# straight corridor 768 long elsewhere with the same heading, whose far end
# puts them out of the doorway's plain mouth heading north. Coming south is a
# plain walk. The double goes straight up the real corridor (the porter's lodge).
ODD_CW, X_IN, X_OUT, MOUTH_CW = 1871, 1873, 1874, 1872
CWL = look("CO", "FC", "KC", 170, 192, MINT)
CW_X = (896, 1088)
CW_ODD_Y, CW_MOUTH_Y = 2224, 2240
for box in ((896, 2112, 1088, 2176), (896, 2176, 1088, CW_ODD_Y), (896, CW_MOUTH_Y, 1088, 2272), (896, 2272, 1088, 2560)):
    m.sector(rect(*box), **dict(CWL, floor=G))
W.area("cwsouth", (896, 2112, 1088, CW_ODD_Y), G)
W.area("cwnorth", (896, CW_MOUTH_Y, 1088, 2560), G)
steel_door((960, 2048), (1024, 2048), (0, 1), G, REG_TAG[1], "forecourt", "cwsouth", thick=64)
CW_FACE, CW_MOUTH = oneway((960, CW_MOUTH_Y), (1024, CW_MOUTH_Y), (0, -1), G, ODD_CW, X_IN, "CO", "CO", "cwsouth",
                           "cwnorth", "the covered way", mouth_id=MOUTH_CW)
fence((896, 2176), (1088, 2176))             # 48 from the odd face
fence((896, 2272), (1088, 2272))             # 48 from it on the mouth's side
for a, b in (((896, CW_ODD_Y), (960, CW_ODD_Y)), ((1024, CW_ODD_Y), (1088, CW_ODD_Y))):
    os_sign(a, b, (0, 1), "CO", 192)
# X: the stretch, in free ground between the forecourt and the garden, heading north
XL = look("CO", "FC", "KC", 150, 192, MINT)
XB = (1408, 1216, 1504, 1984)
for box in ((1408, 1216, 1504, 1264), (1408, 1264, 1504, 1936), (1408, 1936, 1504, 1984)):
    fit(box, [((box[0], 1568, box[2], 1632), dict(light=196))] if box[1] == 1264 else [], **dict(XL, floor=G))
W.area("stretch", XB, G)
X_IN_P = gate((1424, 1216), (1488, 1216), (0, -1), G, X_IN, ODD_CW, "CO", "stretch", "the stretch's way in")
X_OUT_P = gate((1424, 1984), (1488, 1984), (0, 1), G, X_OUT, MOUTH_CW, "CO", "stretch", "the stretch's way out")
fence((1408, 1264), (1504, 1264))
fence((1408, 1936), (1504, 1936))
W.arc(CW_FACE["node"], X_IN_P["node"], 32, portal=90)        # north into the odd face: into the stretch
W.arc(X_IN_P["node"], CW_FACE["node"], 32, portal=270)       # back out of its way in: out of the odd face, south
W.arc(X_OUT_P["node"], CW_MOUTH["node"], 32, portal=90)      # out of its way out: out of the mouth, north
CROSS.append(("the covered way's odd face (into the stretch)", CW_FACE, X_IN_P))
CROSS.append(("the stretch's way in (out of the odd face)", X_IN_P, CW_FACE))
CROSS.append(("the stretch's way out (out of the mouth)", X_OUT_P, CW_MOUTH))
CW_SOUTH = W.node(992, 2140, "the covered way, south (tests)", "cwsouth")
CW_NORTH = W.node(992, 2300, "the covered way, north (tests)", "cwnorth")

# =================================================================================================
# THE BLOCK, GROUND FLOOR (stage 2)
# =================================================================================================
# --- the lobby, the porter's lodge (secret) -------------------------------------------------------
LO = (640, 2560, 1408, 3200)
LODGE = (896, 2976, 1088, 3168)
lo_pillars = [(768, 2816, 832, 2880), (1216, 2816, 1280, 2880)]
room(LO, G, look("LB", "FL", "KL", 205, 256, PALE), grid(LO, 2, 2, 230, 96) + [(r, solid("PI", 256)) for r in lo_pillars],
     holes=[LODGE], name="lobby", obst=[LODGE])
joint((896, 2560), (1088, 2560), "cwnorth", "lobby")
LODGE_IN = (912, 2992, 1072, 3152)
room(LODGE_IN, G, dict(look("CK", "FC", "KC", 190, 128, PAPER), special=1024), name="lodge", sealed=True)
for box in ((896, 2976, 1088, 2992), (896, 2992, 912, 3152), (1072, 2992, 1088, 3152), (896, 3152, 960, 3168), (1024, 3152, 1088, 3168)):
    m.sector(rect(*box), floor=G, ceil=128, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
for p, q in (((896, 2976), (1088, 2976)), ((896, 2976), (896, 3168)), ((1088, 2976), (1088, 3168)), ((896, 3168), (960, 3168)),
             ((1024, 3168), (1088, 3168)), ((912, 2992), (1072, 2992)), ((912, 2992), (912, 3152)), ((1072, 2992), (1072, 3152)),
             ((912, 3152), (960, 3152)), ((1024, 3152), (1072, 3152))):
    m.line(p, q, **GLASS)
ajarmap.steel(m, (960, 3168), (1024, 3168), (0, -1), G, LODGE_TAG, thick=16)
# the lodge's plate: where the double stands when the player has just come out of the covered way
# (48 north of its mouth): the stretch and the doorway shift it north by the stretch's length
CW_OUT_AT = (992, CW_MOUTH_Y + 48)
pass_desk(1180, 2620)

# --- the gallery (the spine) ------------------------------------------------------------------------
GA = (640, 3200, 2944, 3392)
room(GA, G, look("CO", "FC", "KC", 190, 256, MINT), [((x, 3200, x + 64, 3392), dict(light=225)) for x in range(768, 2944, 384)],
     name="gallery")
joint((640, 3200), (1408, 3200), "lobby", "gallery")
frame((640, 3264), (640, 3328), (-1, 0), 121, G, "gallery")

# --- the archive: the vestibule, the stack (sealed), the reading corridor ---------------------------
VE = (1472, 2560, 1728, 2816)
room(VE, G, look("AR", "FR", "KA", 170, 256, DIM), name="vestibule")
gap((1408, 2624), (1408, 2752), (1, 0), G, "LB", "AR", "lobby", "vestibule")
frame((1728, 2656), (1728, 2720), (1, 0), 102, G, "vestibule")
for a, b in (((1536, 2560), (1664, 2560)),):
    hang(a, b, "CI")
ST = (1808, 2560, 2816, 2816)
st_shelves = [((x, 2560, x + 192, 2608), solid("SK", 192)) for x in range(1856, 2752, 256)]
room(ST, G, look("AR", "FR", "KA", 200, 192, DIM), grid(ST, 4, 1, 224, 96) + st_shelves, name="stack", sealed=True)
pane_x(1808, 2816, 2816, 2832)
RC = (1760, 2832, 3008, 2992)
room(RC, G, look("AR", "FR", "KA", 180, 192, DIM), grid(RC, 5, 1, 210, 64), name="reading")
far((1760, 2880), (1760, 2944), (-1, 0), GREEN, G, "reading")
REG2_C = (1728 + 864, 2688)                                                 # 864 in from the stack's west wall, on 102's axis
register(2, "the stack", plate_box(REG2_C), G, REG_TAG[2])
RP = (2816, 2992, 2944, 3200)
room(RP, G, look("CO", "FC", "KC", 180, 192, MINT), name="readingway")
joint((2816, 2992), (2944, 2992), "reading", "readingway")
joint((2816, 3200), (2944, 3200), "readingway", "gallery")
plaque((1472, 2816), (1600, 2816), (0, 1), "AR", "REGISTER 2 THE STACK")

# --- the canteen, the kitchen; the garden door (register 4's) ----------------------------------------
CA = (3072, 2560, 3840, 3136)
tables = [((x, y, x + 128, y + 64), block(32, "TT", "TS")) for x in (3200, 3456) for y in (2688, 2880)]
room(CA, G, look("CA", "FN", "KC", 200, 256, PAPER), grid(CA, 3, 2, 236, 96) + tables, name="canteen")
gap((3008, 2880), (3008, 2944), (1, 0), G, "AR", "CA", "reading", "canteen")
hang((3584, 3136), (3712, 3136), "MN")
KI = (3904, 2560, 4416, 3136)
ovens = [((4224, 2688, 4352, 2816), solid("TK", 64)), ((4224, 2944, 4352, 3072), solid("TK", 64))]
room(KI, G, look("LA", "FA", "KA", 190, 256, RUST), grid(KI, 2, 2, 224) + ovens, name="kitchen")
gap((3840, 2752), (3840, 2880), (1, 0), G, "CA", "LA", "canteen", "kitchen")
GS = (3392, 2176, 3520, 2496)
room(GS, G, sky("PU", "FP", 200, 320), name="gardensteps")
steel_door((3424, 2560), (3488, 2560), (0, -1), G, REG_TAG[4], "canteen", "gardensteps", thick=64)

# --- the link hall; the sealed gallery behind 106; the east strongroom (VIOLET) ----------------------
LH = (3072, 3200, 3584, 3392)
room(LH, G, look("LB", "FL", "KL", 210, 192, PALE), name="link")
frame((3072, 3264), (3072, 3328), (-1, 0), 105, G, "link")
frame((3584, 3264), (3584, 3328), (1, 0), 106, G, "link")
pane_y(3208, 3256, 3584, 3712)
pane_y(3336, 3384, 3584, 3712)
LINK_MID = ((LH[0] + LH[2]) / 2, (LH[1] + LH[3]) / 2)
LV = (2880, 3456, 3712, 3712)
room(LV, G, look("LB", "FL", "KL", 190, 256, PALE), name="linkvest")
gap((2880, 3392), (2944, 3392), (0, 1), G, "CO", "LB", "gallery", "linkvest")
gap((3296, 3392), (3360, 3392), (0, 1), G, "LB", "LB", "link", "linkvest")
pass_desk(3440, 3500)
plaque((3392, 3392), (3520, 3392), (0, 1), "LB", "REGISTER 5 GALLERY")
SG = (3712, 3200, 6400, 3392)
room(SG, G, look("CO", "FC", "KC", 220, 192, MINT), [((x, 3200, x + 64, 3392), dict(light=250)) for x in range(3840, 6400, 320)],
     name="sealedgallery", sealed=True)
REG5_C = (LINK_MID[0] + LINK_LAPS * LINK_LAP, LINK_MID[1])
register(5, "down the bricked-up gallery", plate_box(REG5_C), G, REG_TAG[5])
SR5 = (6464, 3136, 6848, 3392)
room(SR5, G, look("LA", "FA", "KA", 160, 192, RUST), name="strongroom5", sealed=True)

# --- the east lane (open) and the east yard (GREEN hung in 112) -------------------------------------
EL = (3776, 3456, 6848, 3648)
room(EL, G, sky("PU", "FP", 200, 320), name="lane")
gap((3712, 3520), (3712, 3584), (1, 0), G, "LB", "PU", "linkvest", "lane")
for x in (4224, 4864, 5504, 5984):                                          # windows into the sealed gallery
    pane_x(x, x + 128, 3392, 3456)
EY = (6912, 2752, 7872, 3712)
room(EY, G, sky("LB", "FC", 224, 320), [((7104, 2944, 7680, 3520), dict(ftex=T("FL") if LOOK else "AJFLOOR"))], name="eastyard")
steel_door((6912, 3200), (6912, 3264), (-1, 0), G, REG_TAG[5], "eastyard", "strongroom5", thick=64)
pane_y(3296, 3360, 6848, 6912, sill=32, top=128)
frame((7872, 3200), (7872, 3264), (1, 0), 112, G, "eastyard")
squeeze((6848, 3472), (6848, 3520), (1, 0), G, "lane", "eastyard")
turnstile((6912, 3632), (6912, 3568), (-1, 0), G, "eastyard", "lane")

# --- offices off the gallery; the basement's stair room (register 3's door); the stair hall ----------
W1 = (1216, 3456, 1664, 4032)
desks_w1 = [((1280, 3584, 1408, 3648), block(40, "DT", "DS")), ((1472, 3840, 1600, 3904), block(40, "DT", "DS"))]
room(W1, G, look("AR", "FR", "KA", 162, 256, DIM), grid(W1, 1, 2, 200, 96) + desks_w1, name="officew1")
gap((1408, 3392), (1472, 3392), (0, 1), G, "CO", "AR", "gallery", "officew1")
W2 = (2368, 3456, 2816, 3968)
desks_w2 = [((2432, 3584, 2560, 3648), block(40, "DT", "DS")), ((2624, 3776, 2752, 3840), block(40, "DT", "DS"))]
room(W2, G, look("AR", "FR", "KA", 170, 256, DIM), grid(W2, 1, 2, 200, 96) + desks_w2, name="officew2")
gap((2560, 3392), (2624, 3392), (0, 1), G, "CO", "AR", "gallery", "officew2")
BSR = (640, 3456, 1152, 3840)
room(BSR, G, look("PU", "FP", "KP", 160, 192, COLD), name="basementstair")
steel_door((864, 3392), (928, 3392), (0, 1), G, REG_TAG[3], "gallery", "basementstair", thick=64)

# --- the stair hall: BLUE's far side in a pier at the grand stair's foot; 104 beside it ----------------
STAIRS = look("LB", "FE", "KE", 190, 448, STEEL)
SH = (1728, 3456, 2304, 3904)
PIER = (1824, 3856, 1952, 3936)
room(SH, G, STAIRS, grid(SH, 2, 1, 220, 96), holes=[PIER], name="stairhall", obst=[PIER])
for box in ((1792, 3904, 1824, 3936), (1952, 3904, 1984, 3936)):
    m.sector(rect(*box), floor=G, **{k: v for k, v in STAIRS.items()})
steel_door((2112, 3392), (2176, 3392), (0, 1), G, REG_TAG[2], "gallery", "stairhall", thick=64)
far((1856, 3936), (1920, 3936), (0, -1), BLUE, G, None)                     # its front is the flight's first step
frame((2112, 3904), (2176, 3904), (0, 1), 104, G, "stairhall")
ajarmap.stairs(m, (1792, 3936), (1984, 3936), (0, 1), G, U, steps=16, depth=32, ceil=448, light=190,
               color=tint(STEEL), **dress(wall="LB", ftex="FE", ctex="KE"))
W.area("flight", (1792, 3904, 1984, 4448), G, ramp=("y", 3936, G, 4448, U))
W.node(1808, 3920, "the stair's foot, west", "stairhall", "flight")
W.node(1968, 3920, "the stair's foot, east", "stairhall", "flight")
FARS[BLUE]["node"] = W.node(1888, 3968, "far side BLUE", "flight")
TL = (1792, 4448, 1984, 4640)
room(TL, U, STAIRS, name="toplanding")
joint((1792, 4448), (1984, 4448), "flight", "toplanding")
# beside it, behind glass for its whole length: the hall with no stair, sealed; a gallery at 256 at
# its far end, where the stair's head would be
NSH = (2048, 3984, 2240, 4576)
room(NSH, G, STAIRS, [((2048, 4448, 2240, 4576), dict(floor=U, **dress(side="GF", ftex="GT")))], name="nostair", sealed=True)
glass((1984, 3968, 2048, 4576), [((1984, 3968), (1984, 4576)), ((2048, 3984), (2048, 4576))], sill=0, top=448)
for p, q in (((1984, 3968), (1984, 4576)), ((2048, 3984), (2048, 4576))):
    m.line(p, q, **TALL_GLASS)
REG4_C = ((TL[0] + TL[2]) / 2 + 256, (4448 + 4576) / 2)                    # on the gallery: the top landing, as the double sees it
register(4, "the hall with no stair", plate_box(REG4_C), U, REG_TAG[4])
plaque((1728, 3584), (1728, 3712), (-1, 0), "LB", "REGISTER 4 NO STAIR")

# =================================================================================================
# THE UPPER FLOOR (stage 3)
# =================================================================================================
UC = (1600, 4640, 4864, 4832)
room(UC, U, look("CO", "FC", "KC", 176, U + 192, MINT), [((x, 4640, x + 64, 4832), dict(light=210)) for x in range(1728, 4864, 512)],
     name="upper")
joint((1792, 4640), (1984, 4640), "toplanding", "upper")
# the side room, sealed: 103 in the corridor's north wall; the room runs off to the right (east)
frame((3968, 4832), (4032, 4832), (0, 1), 103, U, "upper")
SR3 = (4064, 4848, 4736, 5120)
room(SR3, U, look("CK", "FC", "KC", 184, U + 160, PAPER), [((4096, 5056, 4672, 5120), block(48, "UT", "US"))], name="sideroom",
     sealed=True)
pane_x(4352, 4480, 4832, 4848, z=U)
REG3_C = (FRAMES[103]["mouth"][0] + 560, FRAMES[103]["mouth"][1] + 96)      # 96 ahead and 560 to the right of the frame
register(3, "the side room", plate_box(REG3_C), U, REG_TAG[3])
plaque((3776, 4832), (3904, 4832), (0, 1), "CO", "REGISTER 3 SIDE ROOM", z=U)
# the hall with no size: its four walls are the gazebo's four faces in the garden
NS = (2432, 4160, 2816, 4544)
room(NS, U, look("EX", "FE", "KE", 196, U + 192, STEEL), [((2560, 4288, 2688, 4416), dict(light=230))], name="nosize")
# its door is register 4's, as the garden's: through its walls it is the garden (the gazebo), and the
# garden is the stage register 4 opens (a departure: the design's door here is a plain one)
steel_door((2464, 4640), (2528, 4640), (0, -1), U, REG_TAG[4], "upper", "nosize", thick=96, near="CO", far_part="EX")
# the drawing office: both TEAL leaves; 122
DO = (2944, 4096, 3712, 4512)
do_benches = [((3008, 4224, 3136, 4352), block(48)), ((3520, 4224, 3648, 4352), block(48)), ((3200, 4416, 3456, 4480), block(48, "UT", "US"))]
room(DO, U, look("LA", "FA", "KA", 188, U + 192, RUST), grid(DO, 2, 1, 224, 96) + do_benches, name="drawing")
gap((3264, 4640), (3392, 4640), (0, -1), U, "CO", "LA", "upper", "drawing", thick=128)
frame((3264, 4096), (3328, 4096), (0, -1), 122, U, "drawing")
# offices north of the corridor; the upper store (the rocket launcher)
N_OFF = [(1664, 2304), (2368, 3072), (3136, 3904)]
for k, (x1, x2) in enumerate(N_OFF):
    desks = [((x1 + 64, 5056, x1 + 192, 5120), block(40, "DT", "DS")), ((x2 - 192, 5312, x2 - 64, 5376), block(40, "DT", "DS"))]
    room((x1, 4896, x2, 5568), U, look("AR", "FR", "KA", 150 + 12 * k, U + 192, DIM), grid((x1, 4896, x2, 5568), 1, 2, 200, 96) + desks,
         name=f"office{k}")
    cx = (x1 + x2) // 2 // 64 * 64
    gap((cx, 4832), (cx + 64, 4832), (0, 1), U, "CO", "AR", "upper", f"office{k}")
USTORE = (3968, 5184, 4800, 5568)
us_shelves = [((x, 5248, x + 64, 5504), solid("SK", U + 192)) for x in (4160, 4416, 4672)]
room(USTORE, U, look("AR", "FR", "KA", 156, U + 192, DIM), us_shelves, name="upperstore")
gap((3904, 5312), (3904, 5376), (1, 0), U, "AR", "AR", "office2", "upperstore")
# the balcony at the corridor's east end, over the pond court: a drop of 256, one way
gap((4864, 4672), (4864, 4800), (1, 0), U, "CO", "LB", "upper", "balcony")

# =================================================================================================
# THE POND COURT (open; in by the balcony only, out by a turnstile into the east lane)
# =================================================================================================
PC = (4928, 3712, 6848, 5568)
BAL = (4928, 4640, 5056, 4832)
POND = (5568, 4224, 6400, 5248)
ISLAND = (5824, 4736, 6144, 5056)
LSTORE = (5888, 3904, 6080, 4096)            # the little boat store, on the pond's bank
LS_FENCE = (5904, 3856, 6064, 3904)
KIOSK = (5120, 5120, 5376, 5376)
PCL = sky("LB", "FC", 220, 512)
room(PC, G, PCL, [((4992, 3776, 6784, 5504), dict(ftex=T("FL") if LOOK else "AJFLOOR")),
                  (BAL, dict(floor=U, **dress(side="GF", ftex="GT"))), (LS_FENCE, dict(id=0))],
     holes=[POND, LSTORE, KIOSK], name="pond", obst=[POND, LSTORE, KIOSK, BAL])
W.area("balcony", BAL, U)
BAL_EDGE = W.node(5040, 4736, "the balcony's edge", "balcony")
W.arc(BAL_EDGE, W.node(5088, 4736, "under the balcony", "pond"), 48, kind="drop")
# the pond: 24 under the court, water, a railing round it; the island and its pavilion (secret)
WATER = dict(ceil=512, light=200, wall=T("LB") if LOOK else "AJWALL", ftex="FWATER1", ctex=SKY)
fit(POND, [((5952, POND[1], 6016, ISLAND[1]), dict(id=BRIDGE_TAG))], holes=[ISLAND], floor=-24, **WATER)
# (the strip 5952..6016 from the bank to the island is the footbridge, down in the water: phase 2 raises it)
posts = [(ISLAND[0] + 32, ISLAND[1] + 32), (ISLAND[2] - 48, ISLAND[1] + 32), (ISLAND[0] + 32, ISLAND[3] - 48), (ISLAND[2] - 48, ISLAND[3] - 48)]
fit(ISLAND, [((x, y, x + 16, y + 16), solid("PI", 160)) for x, y in posts] + [((5920, 4832, 6048, 4960), dict(light=240, special=1024))],
    floor=G, **PCL)
W.area("island", ISLAND, G)
for p, q in (((POND[0], POND[1]), (POND[0], POND[3])), ((POND[0], POND[3]), (POND[2], POND[3])), ((POND[2], POND[3]), (POND[2], POND[1])),
             ((POND[2], POND[1]), (6016, POND[1])), ((5952, POND[1]), (POND[0], POND[1])),
             ((ISLAND[0], ISLAND[1]), (ISLAND[0], ISLAND[3])), ((ISLAND[0], ISLAND[3]), (ISLAND[2], ISLAND[3])),
             ((ISLAND[2], ISLAND[3]), (ISLAND[2], ISLAND[1])), ((ISLAND[2], ISLAND[1]), (6016, ISLAND[1])),
             ((5952, ISLAND[1]), (ISLAND[0], ISLAND[1]))):
    m.line(p, q, **RAIL)
m.line((5952, POND[1]), (6016, POND[1]), id=BRIDGE_RAIL, **RAIL)            # where the footbridge will land: unrailed in phase 2
REG9_C = None                                                               # the island's plate: by the boat store (below)
# the boat store, bigger inside (MAP18's hut): its door from the court shows and leads into the big
# store in free ground (between the garden and the block), heading east; the big store's door leads
# back out of the little one's. The inside of the little store is reached by a plain door in its side.
ODD_B, BIG_GATE, MOUTH_B = 1875, 1876, 1877
fit((5904, 3920, 6064, 4080), [((5904, 3920, 6064, 3952), dict(id=0))], floor=G, **look("CK", "FC", "KC", 150, 128, PAPER))
W.area("littlestore", (5904, 3920, 6064, 4080), G)
BOAT_FACE, BOAT_MOUTH = oneway((5952, 3920), (6016, 3920), (0, -1), G, ODD_B, BIG_GATE, "CK", "LB", "pond", "littlestore",
                               "the boat store", mouth_id=MOUTH_B)
fence((5904, 3904), (5904, 3856), (6064, 3856), (6064, 3904))
fence((5904, 3952), (6064, 3952))
for a, b in (((5888, 3904), (5952, 3904)), ((6016, 3904), (6080, 3904))):
    os_sign(a, b, (0, 1), "LB", 512)
ajarmap.opening(m, (6064, 4000), (6064, 4064), (1, 0), G)                   # its side: a plain way in
over((6064, 4000), (6064, 4064), "CK")
over((6080, 4000), (6080, 4064), "LB")
W.link(W.node(6048, 4032, "the boat store's side door", "littlestore"), W.node(6112, 4032, "the boat store's side door", "pond"), 64)
BIG = (4032, 2240, 5056, 2496)
for box in ((4032, 2240, 4080, 2496), (4080, 2240, 5056, 2496)):
    fit(box, grid(box, 3, 1, 190, 96) if box[0] == 4080 else [], floor=G, **look("AR", "FR", "KA", 156, 192, DIM))
W.area("bigstore", BIG, G)
BIG_P = gate((4032, 2400), (4032, 2336), (-1, 0), G, BIG_GATE, ODD_B, "AR", "bigstore", "the big store's door")
fence((4080, 2240), (4080, 2496))
W.arc(BOAT_FACE["node"], BIG_P["node"], 32, portal=90)       # into the little store's door: into the big store
W.arc(BIG_P["node"], BOAT_FACE["node"], 32, portal=180)      # the big store's door: out of the little store's, south
CROSS.append(("the boat store's door (into the big store)", BOAT_FACE, BIG_P))
CROSS.append(("the big store's door (out of the boat store's)", BIG_P, BOAT_FACE))
BIG_END = (BIG[2] - 48, (BIG[1] + BIG[3]) / 2)
# the kiosk, sealed behind steel (register 7's), YELLOW in it, glass to see it
fit((5136, 5136, 5360, 5360), floor=G, **look("CK", "FC", "KC", 190, 128, PAPER))
W.area("kiosk", (5136, 5136, 5360, 5360), G)
W.sealed.add("kiosk")
for box in ((5120, 5120, 5216, 5136), (5280, 5120, 5376, 5136), (5120, 5136, 5136, 5376), (5360, 5136, 5376, 5376), (5136, 5360, 5360, 5376)):
    m.sector(rect(*box), floor=G + 16, ceil=G + 112, light=200, wall="AJTRIM", ftex="AJTRIMF", ctex="AJTRIMF")
for p, q in (((5120, 5120), (5216, 5120)), ((5280, 5120), (5376, 5120)), ((5120, 5120), (5120, 5376)), ((5376, 5120), (5376, 5376)),
             ((5120, 5376), (5376, 5376)), ((5136, 5136), (5216, 5136)), ((5280, 5136), (5360, 5136)), ((5136, 5136), (5136, 5360)),
             ((5360, 5136), (5360, 5360)), ((5136, 5360), (5360, 5360))):
    m.line(p, q, **GLASS)
steel_door((5216, 5120), (5280, 5120), (0, 1), G, REG_TAG[7], "pond", "kiosk", thick=16)
# 113 in the court's east wall; the boathouse behind it, sealed, glass either side
frame((6848, 4512), (6848, 4576), (1, 0), 113, G, "pond")
BH = (6928, 4416, 7952, 4672)
room(BH, G, look("PU", "FP", "KP", 170, 192, COLD), [((x, 4416, x + 64, 4672), dict(light=220)) for x in range(7040, 7952, 256)],
     name="boathouse", sealed=True)
pane_y(4432, 4496, 6848, 6928)
pane_y(4592, 4656, 6848, 6928)
REG7_C = (6848 + 864, 4544)                                                 # 864 in from the court's wall, on 113's axis
register(7, "the boathouse", plate_box(REG7_C), G, REG_TAG[7])
PC_OUT = turnstile((6016, 3712), (6080, 3712), (0, -1), G, "pond", "lane")

# =================================================================================================
# THE BASEMENT (stage 4): by register 3's door and a stair down
# =================================================================================================
BASE = look("PU", "FP", "KP", 152, B + 192, COLD)
ajarmap.stairs(m, (832, 3840), (1024, 3840), (0, 1), G, B, steps=16, depth=32, ceil=160, light=152, color=tint(COLD),
               **dress(wall="PU", ftex="FP", ctex="KP"))
W.area("basestairs", (832, 3840, 1024, 4352), G, ramp=("y", 3840, G, 4352, B))
joint((832, 3840), (1024, 3840), "basementstair", "basestairs")
BL = (768, 4352, 1088, 4608)
room(BL, B, BASE, name="blanding")
joint((832, 4352), (1024, 4352), "basestairs", "blanding")
BST = (0, 4352, 704, 5056)
b_shelves = [((x, 4480, x + 48, 4928), solid("SK", B + 192)) for x in (128, 320, 512)]
room(BST, B, look("AR", "FR", "KA", 144, B + 192, DIM), grid(BST, 2, 3, 180) + b_shelves, name="stores")
gap((768, 4416), (768, 4544), (-1, 0), B, "PU", "AR", "blanding", "stores")
BB = (1152, 4352, 1536, 5056)
boilers = [((1216, 4544, 1344, 4672), solid("TK", B + 224)), ((1344, 4800, 1472, 4928), solid("TK", B + 224))]
room(BB, B, look("PU", "FP", "KQ", 144, B + 224, COLD), grid(BB, 2, 2, 176) + boilers, name="boiler")
gap((1088, 4416), (1088, 4544), (1, 0), B, "PU", "PU", "blanding", "boiler")
BNP = (832, 4608, 1024, 5120)
room(BNP, B, BASE, name="bpassage")
joint((832, 4608), (1024, 4608), "blanding", "bpassage")
LC = (0, 5120, 1536, 5376)
lc_tanks = [((384, 5184, 448, 5248), solid("TK", B + 160)), ((1088, 5248, 1152, 5312), solid("TK", B + 160))]
room(LC, B, look("PU", "FP", "KP", 140, B + 160, COLD), grid(LC, 4, 1, 176) + lc_tanks, name="cellar")
joint((832, 5120), (1024, 5120), "bpassage", "cellar")
frame((640, 5376), (704, 5376), (0, 1), 123, B, "cellar")

# =================================================================================================
# THE GARDEN (stage 4's door; open): lawns, paths, hedges; the avenue; the gazebo
# =================================================================================================
GD = (1536, 64, 5696, 2176)
GRASS = dict(sky("LB", "FL", 232, 320), ftex="GRASS1")
ARCH_S, ARCH_N = (2624, 384, 2880, 512), (2624, 1792, 2880, 1920)
GAZEBO = (4224, 960, 4416, 1152)
HEDGE = dict(floor=64, ftex="GRASS2", **dress(side="PS"))
hedges = [(1664, 320, 2368, 384), (3008, 320, 3904, 384), (1664, 1856, 2368, 1920), (3008, 1856, 3904, 1920),
          (4672, 448, 5504, 512), (4672, 1664, 5504, 1728), (1664, 704, 1728, 1536), (5568, 704, 5632, 1280),
          (3328, 896, 3392, 1344), (4864, 896, 5248, 960), (4864, 1216, 5248, 1280)]
paths = [(2688, 64, 2816, 2176), (1536, 1024, 5696, 1088), (3392, 1088, 3520, 2176)]
room(GD, G, GRASS, [(p, dict(ftex=T("FC") if LOOK else "AJFLOOR")) for p in paths] + [(h, HEDGE) for h in hedges],
     holes=[ARCH_S, ARCH_N, GAZEBO], name="garden", obst=[ARCH_S, ARCH_N, GAZEBO])
joint((3392, 2176), (3520, 2176), "gardensteps", "garden")
frame((2720, 512), (2784, 512), (0, -1), 109, G, "garden")                  # the avenue: its south arch, facing north
frame((2784, 1792), (2720, 1792), (0, 1), 110, G, "garden")                 # ... its north arch, facing south: 1280 apart
frame((2240, 2176), (2304, 2176), (0, 1), 124, G, "garden")                 # in the block's garden wall
pass_desk(3600, 2120)
# the gazebo: MAP18's clock tower: each face the far end of a fixed doorway whose near end is a wall
# of the hall with no size, upstairs
cx, cy = (NS[0] + NS[2]) // 2, (NS[1] + NS[3]) // 2
bx, by = (GAZEBO[0] + GAZEBO[2]) // 2, (GAZEBO[1] + GAZEBO[3]) // 2
for n, (dx, dy) in zip((1, 2, 3, 4), ((0, 1), (1, 0), (0, -1), (-1, 0))):
    hx, hy = cx + dx * 192, cy + dy * 192
    tx, ty = bx + dx * 96, by + dy * 96
    a1, a2 = (P(hx - dy * 32, hy - dx * 32), P(hx + dy * 32, hy + dx * 32))
    b1, b2 = (P(tx - dy * 32, ty - dx * 32), P(tx + dy * 32, ty + dx * 32))
    fixed(n, a1, a2, (dx, dy), U, "nosize", b1, b2, (-dx, -dy), G, "garden")
# the tower yard's two ways from the garden: a squeeze in, a turnstile out
squeeze((5696, 1408), (5696, 1456), (1, 0), G, "garden", "toweryard")

# =================================================================================================
# THE TOWER YARD (open; in with a door by YELLOW only, with empty hands by the squeeze)
# =================================================================================================
TY = (5760, 64, 7168, 1728)
TW = (6208, 368, 6528, 1728)                 # the water tower; its sealed stair goes on north beyond the yard
TS = (6656, 1152, 7040, 1536)                # the tower's strongroom (PINK)
room(TY, G, sky("PU", "FP", 210, 320), [((5824, 128, 7104, 320), dict(ftex=T("FL") if LOOK else "AJFLOOR"))],
     holes=[TW, TS], name="toweryard", obst=[TW, TS])
TY_OUT = turnstile((5760, 704), (5760, 640), (-1, 0), G, "toweryard", "garden")
far((6784, 64), (6848, 64), (0, -1), YELLOW, G, "toweryard")
frame((7168, 1216), (7168, 1280), (1, 0), 111, G, "toweryard")
# the tower: the head landing (ground), one flight of 8 steps down 128, the foot landing; 108 at the
# head facing down the flight, 107 at the foot facing up it (MAP18's stair hall)
TOWER = look("PU", "FP", "KP", 170, 192, COLD)
HL = (6272, 448, 6464, 576)
room(HL, G, TOWER, name="towerhead")
ajarmap.opening(m, (6208, 480), (6208, 544), (1, 0), G, thick=64)
over((6208, 480), (6208, 544), "PU")
over((6272, 480), (6272, 544), "PU")
W.node(6240, 512, "the tower's door", "toweryard", "towerhead")
ajarmap.stairs(m, (6272, 576), (6464, 576), (0, 1), G, TOWER_FOOT, steps=8, depth=32, ceil=192, light=170, color=tint(COLD),
               **dress(wall="PU", ftex="FP", ctex="KP"))
W.area("towerflight", (6272, 576, 6464, 832), G, ramp=("y", 576, G, 832, TOWER_FOOT))
joint((6272, 576), (6464, 576), "towerhead", "towerflight")
FOOT = (6272, 832, 6464, 960)
room(FOOT, TOWER_FOOT, dict(TOWER, ceil=TOWER_FOOT + 256), name="towerfoot")
joint((6272, 832), (6464, 832), "towerflight", "towerfoot")
frame((6336, 448), (6400, 448), (0, -1), 108, G, "towerhead")
frame((6336, 960), (6400, 960), (0, 1), 107, TOWER_FOOT, "towerfoot")
FOOT_MID = ((FOOT[0] + FOOT[2]) / 2, (FOOT[1] + FOOT[3]) / 2)
# behind the foot's wall the stair goes on down, sealed: three more flights of the same pitch, lit;
# glass beside 107 to see down it
for x1, x2 in ((6272, 6320), (6416, 6464)):
    glass((x1, 960, x2, 1040), [((x1, 960), (x2, 960)), ((x1, 1040), (x2, 1040))], sill=16, top=144, z=TOWER_FOOT)
SEAL = look("PU", "FP", "KP", 200, 0, COLD)
ALONG, DOWN = STAIR_LAP
m.sector(rect(6272, 1040, 6464, 1120), floor=TOWER_FOOT, ceil=TOWER_FOOT + 192, **{k: v for k, v in SEAL.items() if k != "ceil"})
W.area("sealedstair0", (6272, 1040, 6464, 1120), TOWER_FOOT)
for k in (1, 2, 3):
    top = -DOWN * k                                                         # the flight's top: k laps down
    ajarmap.stairs(m, (6272, 576 + ALONG * k), (6464, 576 + ALONG * k), (0, 1), top, TOWER_FOOT, steps=8, depth=32,
                   ceil=top + 192, light=200, color=tint(COLD), **dress(wall="PU", ftex="FP", ctex="KP"))
    y1 = 832 + ALONG * k
    y2 = 1120 + ALONG * k if k < 3 else 832 + ALONG * k + 288
    m.sector(rect(6272, y1, 6464, y2), floor=top + TOWER_FOOT, ceil=top + TOWER_FOOT + 192, light=200,
             **{kk: v for kk, v in SEAL.items() if kk not in ("ceil", "light")})
    W.area(f"sealedflight{k}", (6272, 576 + ALONG * k, 6464, 832 + ALONG * k), top, ramp=("y", 576 + ALONG * k, top, 832 + ALONG * k, top + TOWER_FOOT))
    W.area(f"sealedstair{k}", (6272, y1, 6464, y2), top + TOWER_FOOT)
for name_ in [a for a in W.areas if a.startswith("sealed")]:
    W.sealed.add(name_)
REG6_C = (FOOT_MID[0], FOOT_MID[1] + STAIR_LAPS * ALONG)
register(6, "down the bricked-up stair", plate_box(REG6_C), TOWER_FOOT - STAIR_LAPS * DOWN, REG_TAG[6])
# the tower's strongroom (PINK), its steel door on register 6's tag, a window
TS_IN = (6672, 1168, 7024, 1520)
room(TS_IN, G, look("LA", "FA", "KA", 160, 192, RUST), name="strongroom6", sealed=True)
for box in ((6656, 1152, 7040, 1168), (6656, 1520, 7040, 1536), (7024, 1168, 7040, 1520), (6656, 1168, 6672, 1280),
            (6656, 1344, 6672, 1392), (6656, 1456, 6672, 1520)):
    m.sector(rect(*box), floor=G, ceil=G, light=160, wall=T("LA") if LOOK else "AJWALL", ftex="AJTRIMF", ctex="AJTRIMF")
steel_door((6656, 1280), (6656, 1344), (1, 0), G, REG_TAG[6], "toweryard", "strongroom6", thick=16)
pane_y(1392, 1456, 6656, 6672, sill=32, top=128)

# =================================================================================================
# DOORS, THINGS, COMPANY
# =================================================================================================
m.thing(896, 352, 1, angle=90)                                              # the start: the pass hall, facing north
ajarmap.door(m, RED, 1150, 320, angle=90)                                   # RED leans in the pass hall
ajarmap.door(m, GREEN, 7840, 3232, frame=112)                               # GREEN hangs in the east yard's 112
ajarmap.door(m, BLUE, 128, 5248, angle=0)                                   # BLUE: the long cellar's far end
ajarmap.door(m, YELLOW, 5248, 5280, angle=270)                              # YELLOW: in the kiosk
ajarmap.door(m, VIOLET, 6656, 3264, angle=0)                                # VIOLET: the east strongroom
ajarmap.door(m, PINK, 6848, 1344, angle=180)                                # PINK: the tower's strongroom
ajarmap.pair(m, TEAL, (3072, 4448, 270), (3584, 4448, 270))                 # both TEAL leaves: the drawing office
ajarmap.pair(m, ORANGE, (5184, 3840, 90), (6656, 5440, 180))                # both ORANGE leaves: the pond court



# =================================================================================================
# THE MEASURE: THE REGISTERS BY THE RULE'S GEOMETRY, THE STAGES, THE COURTS (checked when built)
# =================================================================================================
def rot(k, v):
    x, y = v
    return ((x, y), (-y, x), (-x, -y), (y, -x))[k % 4]


class Tf:
    """p -> rot(k, p) + t and z -> z + dz: what a crossing does to where
    things are (quarter turns only: every portal here is square to x or y)."""
    def __init__(self, k=0, t=(0, 0), dz=0):
        self.k, self.t, self.dz = k % 4, t, dz

    def __call__(self, p):
        q = rot(self.k, p)
        return (q[0] + self.t[0], q[1] + self.t[1])

    def __matmul__(self, o):                                  # self after o
        q = rot(self.k, o.t)
        return Tf(self.k + o.k, (q[0] + self.t[0], q[1] + self.t[1]), self.dz + o.dz)

    def inv(self):
        q = rot(-self.k, self.t)
        return Tf(-self.k, (-q[0], -q[1]), -self.dz)

    def box(self, r):
        a, b = self((r[0], r[1])), self((r[2], r[3]))
        return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


def ends(e):
    """A portal end's line as udmf writes it (v1, v2): the front side is the
    sector declared first (the recess; the room beyond an odd face; the
    plain room at a mouth) and polygons are clockwise, so the front is on
    the right of v1 -> v2; `inn` points from the front to the back."""
    d = (e["inn"][1] * 32, -e["inn"][0] * 32)
    c = e["c"]
    return (c[0] - d[0], c[1] - d[1]), (c[0] + d[0], c[1] + d[1])


def quarter(v):
    return round(math.degrees(math.atan2(v[1], v[0])) / 90) % 4


def crossing(S, D):
    """In through the portal end S, out of D: the engine's rule for a line
    portal (Line_SetPortal type 1): a point p at S's line comes out at
    D.v2 + R(p - S.v1), R the turn that lays S's line on D's reversed; the
    height by the two floors (the portals are aligned to the floor)."""
    s1, s2 = ends(S)
    d1, d2 = ends(D)
    k = quarter((d1[0] - d2[0], d1[1] - d2[1])) - quarter((s2[0] - s1[0], s2[1] - s1[1]))
    q = rot(k, s1)
    return Tf(k, (d2[0] - q[0], d2[1] - q[1]), D["z"] - S["z"])


def standable(area, r, z, tol=TOL_Z):
    """Whether the player can stand somewhere in the rectangle r of `area`
    with his feet within `tol` of z: the area less his radius, less its
    obstacles grown by it; a flight of steps taken as a slope."""
    a = W.areas[area]
    b, g = a["box"], Walk.R
    x1, y1, x2, y2 = max(r[0], b[0] + g), max(r[1], b[1] + g), min(r[2], b[2] - g), min(r[3], b[3] - g)
    if x1 > x2 or y1 > y2:
        return False
    if a["ramp"]:
        axis, c0, z0, c1, z1 = a["ramp"]
        lo, hi = sorted((c0 + (z - tol - z0) / (z1 - z0) * (c1 - c0), c0 + (z + tol - z0) / (z1 - z0) * (c1 - c0)))
        if axis == "x":
            x1, x2 = max(x1, lo), min(x2, hi)
        else:
            y1, y2 = max(y1, lo), min(y2, hi)
        if x1 > x2 or y1 > y2:
            return False
    elif abs(a["z"] - z) > tol:
        return False
    obs = [(o[0] - g, o[1] - g, o[2] + g, o[3] + g) for o in a["obst"]]
    xs = sorted({x1, x2} | {v for o in obs for v in (o[0], o[2]) if x1 < v < x2})
    ys = sorted({y1, y2} | {v for o in obs for v in (o[1], o[3]) if y1 < v < y2})
    for xa, xb in list(zip(xs, xs[1:])) or [(x1, x2)]:
        for ya, yb in list(zip(ys, ys[1:])) or [(y1, y2)]:
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            if not any(o[0] < cx < o[2] and o[1] < cy < o[3] for o in obs):
                return True
    return False


_REACH = {}


def reach(node, opened):
    """The areas and nodes the player gets to on foot from `node`, through no
    portal (drops, turnstiles and squeezes taken), with the steel doors
    `opened` open."""
    key = (node, frozenset(opened))
    if key not in _REACH:
        dist, _ = W.dijkstra(node, opened=opened, portals=False)
        _REACH[key] = ({a for i in dist for a in W.nodes[i]["areas"]}, set(dist))
    return _REACH[key]


PLAIN = (RED, GREEN, BLUE, YELLOW, VIOLET, PINK)
NAME = {**ajarmap.NAMES, TEAL: "TEAL", ORANGE: "ORANGE"}


def crossings():
    """Every crossing one move can make: each plain door in each frame, in
    through the frame or in through its far side; a Pair in each ordered
    pair of frames; the building's own portals."""
    out = []
    for c in PLAIN:
        for f in sorted(FRAMES):
            out.append((f"{NAME[c]} in {f}, into {f}", FRAMES[f], FARS[c], ("door", c, f, "in")))
            out.append((f"{NAME[c]} in {f}, into its far side", FARS[c], FRAMES[f], ("door", c, f, "back")))
    for f in sorted(FRAMES):
        for g in sorted(FRAMES):
            if f != g:
                out.append((f"a Pair in {f} and {g}, into {f}", FRAMES[f], FRAMES[g], ("pair", f, g)))
    for name, S, D in CROSS:
        out.append((name, S, D, ("own", name)))
    return [(n, S, D, crossing(S, D), key) for n, S, D, key in out]


def stage_sets():
    """The stages, as the steel doors open in order, and what each adds."""
    return [("the gatehouse", set()), ("the block's ground floor", {REG_TAG[1]}),
            ("the stair hall and the upper floor", {REG_TAG[1], REG_TAG[2]}),
            ("the basement", {REG_TAG[1], REG_TAG[2], REG_TAG[3]}),
            ("the garden and the grounds", {REG_TAG[1], REG_TAG[2], REG_TAG[3], REG_TAG[4]})]


STAGE_AREAS = [
    {"passhall", "forecourt", "nightway"},
    {"dutyroom", "cwsouth", "cwnorth", "stretch", "lobby", "gallery", "vestibule", "reading", "readingway", "canteen",
     "kitchen", "link", "linkvest", "lane", "eastyard", "officew1", "officew2"},
    {"stairhall", "flight", "toplanding", "upper", "drawing", "office0", "office1", "office2", "upperstore", "balcony",
     "pond", "littlestore", "bigstore"},
    {"basementstair", "basestairs", "blanding", "stores", "boiler", "bpassage", "cellar"},
    {"gardensteps", "garden", "nosize", "toweryard", "towerhead", "towerflight", "towerfoot"},
]
COURTS = {"eastyard": "the east yard", "pond": "the pond court", "toweryard": "the tower yard"}
APART = {"nightroom": "the night room (the way out: by the chain only)", "island": "the island (phase 2: its footbridge)",
         "strongroom5": "the east strongroom (register 5)", "strongroom6": "the tower's strongroom (register 6)",
         "kiosk": "the kiosk (register 7)"}


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(a[0] + t * dx - p[0], a[1] + t * dy - p[1])


def stubs_alone():
    """Every portal's stub (the dark space behind its line) touches no sector
    but its own recess: one that did would be a hole in a wall."""
    bad = []
    edges = {}
    for i, poly in enumerate(m.polys):
        for a, b in zip(poly, poly[1:] + poly[:1]):
            edges.setdefault((a[0] == b[0], a[0] if a[0] == b[0] else a[1]), []).append(
                (min(a[1], b[1]) if a[0] == b[0] else min(a[0], b[0]), max(a[1], b[1]) if a[0] == b[0] else max(a[0], b[0]), i))
    ports = [e for e in PORTS.values() if e["name"].startswith(("frame", "far", "brass", "doorway", "the stretch", "the big"))]
    for e in ports:
        (x1, y1), (x2, y2) = ends(e)
        s = ajarmap.STUB
        q = [(x1, y1), (x2, y2), (x2 + e["inn"][0] * s, y2 + e["inn"][1] * s), (x1 + e["inn"][0] * s, y1 + e["inn"][1] * s)]
        own = [i for i, poly in enumerate(m.polys) if sorted(poly) == sorted(q)]
        if len(own) != 1:
            bad.append(f"{e['name']}: no stub found")
            continue
        for a, b in list(zip(q, q[1:] + q[:1]))[1:]:                    # its three walls (the first edge is its line)
            vert = a[0] == b[0]
            key = (vert, a[0] if vert else a[1])
            lo, hi = sorted((a[1], b[1]) if vert else (a[0], b[0]))
            for l2, h2, i in edges.get(key, ()):
                if i != own[0] and min(hi, h2) - max(lo, l2) > 0:
                    bad.append(f"{e['name']}'s stub touches sector {i} at {a}-{b}")
    return bad


def measure():
    lines, bad = [], []
    adj = W.graph()
    X = crossings()
    lines.append(f"MAP19: {len(m.polys)} sectors, {len(W.areas)} walk areas, {len(W.nodes)} nodes, {len(FRAMES)} frames, "
                 f"{len(FARS)} far sides, {len(CROSS)} crossings of the building's own; {len(X)} crossings measured")
    # --- the stages: each one piece on foot (the building's own portals walked), opened in order -------
    seen_before = set()
    for (name, opened), want in zip(stage_sets(), STAGE_AREAS):
        dist, _ = W.dijkstra(START, opened=opened)
        got = {a for i in dist for a in W.nodes[i]["areas"]} - set(APART)
        new = got - seen_before
        want_all = seen_before | want
        if got != want_all:
            bad.append(f"stage '{name}': on foot it reaches {sorted(got - want_all)} too and not {sorted(want_all - got)}")
        back, _ = W.dijkstra(START, opened=opened, reverse=True)
        stuck = sorted({W.nodes[i]["label"] for i in dist if i not in back})
        if stuck:
            bad.append(f"stage '{name}': no way back on foot from {stuck[:6]}")
        lines.append(f"    stage '{name}' (steel open: {sorted(t - 1900 for t in opened) or 'none'}): {len(new)} areas more, "
                     f"one piece on foot")
        seen_before = got
    all_open = set(REG_TAG.values()) | {LODGE_TAG}
    dist, _ = W.dijkstra(START, opened=all_open)
    got = {a for i in dist for a in W.nodes[i]["areas"]}
    lost = sorted(set(W.areas) - got - W.sealed - set(APART))
    if lost:
        bad.append(f"areas nobody reaches on foot: {lost}")
    # --- the courts: in with empty hands, out with a door in hand ----------------------------------------
    for area, name in COURTS.items():
        ins = [kind for i, j, c, kind in W.arcs if area in W.nodes[j]["areas"] and area not in W.nodes[i]["areas"]]
        outs = [kind for i, j, c, kind in W.arcs if area in W.nodes[i]["areas"] and area not in W.nodes[j]["areas"]]
        if not set(ins) & {"squeeze", "drop"} or "turnstile" not in outs:
            bad.append(f"{name}: in {ins}, out {outs}")
        lines.append(f"    {name}: in by {', '.join(sorted(set(ins)))}; out by {', '.join(sorted(set(outs) - {'squeeze'}))}")
    # --- odd faces: no frame or far side within 112 ---------------------------------------------------
    near = min((seg_dist(e["mouth"], a, b), e["name"]) for e in list(FRAMES.values()) + list(FARS.values()) if "mouth" in e
               for a, b in ODD_LINES)
    if near[0] < 112:
        bad.append(f"{near[1]} is {near[0]:.0f} from a one-sided doorway's face or gate")
    bad += stubs_alone()
    # --- the registers -----------------------------------------------------------------------------------
    ANSWERS.clear()
    for n, r in sorted(REGISTERS.items()):
        P, z = r["box"], r["z"]
        opened = all_open - {r["opens"]}
        one = []
        for name, S, D, M, key in X:
            areas, _ = reach(D["node"], opened)
            Q, zt = M.box(P), z + M.dz
            where = [a for a in sorted(areas) if standable(a, Q, zt)]
            if where:
                one.append((name, key, where, M))
        r["one"] = one
        lines.append(f"    register {n} ({r['name']}): {len(one)} answers of one crossing"
                     + "".join(f"\n        {name} (standing in {', '.join(w)})" for name, key, w, M in one))
    # what each register was meant for (PLAN.md), and what it must not be
    def has(n, name, area=None):
        for nm, key, where, M in REGISTERS[n]["one"]:
            if nm == name and (area is None or area in where):
                return M
        return None

    meant = [(1, "RED in 101, into 101", "forecourt"), (2, "GREEN in 102, into 102", "reading"),
             (3, "RED in 103, into 103", "forecourt"), (4, "BLUE in 104, into 104", "toplanding"),
             (7, "GREEN in 113, into 113", "reading"), (9, "the boat store's door (into the big store)", "bigstore")]
    for n, name, area in meant:
        M = has(n, name, area)
        if not M:
            bad.append(f"register {n}: the answer meant ({name}, standing in {area}) does not put the double on its plate")
        else:
            ANSWERS[n] = (name, M(REGISTERS[n]["centre"]))
    for n, colour in ((2, RED), (3, GREEN)):
        no = [nm for nm, key, w, M in REGISTERS[n]["one"] if key[:3] == ("door", colour, 100 + n)]
        if no:
            bad.append(f"register {n} is answered by {NAME[colour]} in {100 + n}: {no}")
    for n in (5, 6):
        if REGISTERS[n]["one"]:
            bad.append(f"register {n} has answers of one crossing: {[nm for nm, *_ in REGISTERS[n]['one']]}")
    # the porter's lodge: just out of the covered way (its odd face, then the stretch's way out)
    M = crossing(X_OUT_P, CW_MOUTH) @ crossing(CW_FACE, X_IN_P)
    at = M(REGISTERS[8]["centre"])
    if not (abs(at[0] - CW_OUT_AT[0]) < 1 and abs(at[1] - CW_OUT_AT[1]) < 1 and standable("cwnorth", (*at, *at), G)):
        bad.append(f"the porter's lodge's plate is not where the covered way puts the double: {at}")
    ANSWERS[8] = ("the covered way, going north", at)
    # --- the laps -------------------------------------------------------------------------------------
    for n, (S, D), ks, mid, k0 in ((5, (FRAMES[106], FRAMES[105]), (4, 5, 6), LINK_MID, LINK_LAPS),
                                   (6, (FRAMES[107], FRAMES[108]), (2, 3, 4), FOOT_MID, STAIR_LAPS)):
        L, Mk, r = crossing(S, D), Tf(), REGISTERS[n]
        opened = all_open - {r["opens"]}
        areas, _ = reach(D["node"], opened)
        out = []
        for k in range(1, max(ks) + 1):
            Mk = L @ Mk
            if k in ks:
                where = [a for a in sorted(areas) if standable(a, Mk.box(r["box"]), r["z"] + Mk.dz)]
                out.append(f"{k} laps: {', '.join(where) or 'nowhere'}")
                if k == k0:
                    at = Mk(r["centre"])
                    ANSWERS[n] = (f"a Pair in {S['name'][6:]} and {D['name'][6:]}, {k} laps", at)
                    if abs(at[0] - mid[0]) > 1 or abs(at[1] - mid[1]) > 1 or abs(r["z"] + Mk.dz - W.z_at(
                            "link" if n == 5 else "towerfoot", *mid)) > TOL_Z:
                        bad.append(f"register {n}: {k} laps put the double on its plate with the player at {at}, not {mid}")
        lines.append(f"    register {n}, the laps (the player standing anywhere he can walk to from the frame he comes "
                     f"out of): {'; '.join(out)}")
    # --- two crossings in a row (the plate's middle only) --------------------------------------------------
    grid_ = {}
    for a, d in W.areas.items():
        b = d["box"]
        for gx in range(int(b[0]) // 512, int(b[2]) // 512 + 1):
            for gy in range(int(b[1]) // 512, int(b[3]) // 512 + 1):
                grid_.setdefault((gx, gy), []).append(a)
    by_s = {}
    for c in X:
        by_s.setdefault(c[1]["node"], []).append(c)
    for n, r in sorted(REGISTERS.items()):
        opened = all_open - {r["opens"]}
        count = 0
        for name1, S1, D1, M1, k1 in X:
            q1, z1 = M1(r["centre"]), r["z"] + M1.dz
            _, nodes1 = reach(D1["node"], opened)
            for s_node in nodes1 & by_s.keys():
                for name2, S2, D2, M2, k2 in by_s[s_node]:
                    q2 = M2(q1)
                    areas2 = None
                    for a in grid_.get((int(q2[0] // 512), int(q2[1] // 512)), ()):
                        if areas2 is None:
                            areas2 = reach(D2["node"], opened)[0]
                        if a in areas2 and standable(a, (*q2, *q2), z1 + M2.dz):
                            count += 1
                            break
        r["two"] = count
    lines.append("    two crossings in a row that put the double on the plate's middle: "
                 + ", ".join(f"register {n} {r['two']}" for n, r in sorted(REGISTERS.items())))
    lines.append("    (not modelled: doors carried while walking (every steel door but the register's own is taken as "
                 "open), whether the door asked for can be at hand, things in the way, the double's own size, the "
                 "time it must stand; a stair is taken as a slope)")
    return lines, bad


ANSWERS = {}
REG8_C = crossing(CW_FACE, X_IN_P).inv()(crossing(X_OUT_P, CW_MOUTH).inv()(CW_OUT_AT))
register(8, "the porter's lodge", plate_box(REG8_C), G, LODGE_TAG)
REG9_C = crossing(BOAT_FACE, BIG_P).inv()(BIG_END)
register(9, "the island", plate_box(REG9_C), G, BRIDGE_TAG)
assert LODGE_IN[0] <= REG8_C[0] - 64 and REG8_C[0] + 64 <= LODGE_IN[2] and LODGE_IN[1] <= REG8_C[1] - 64 <= REG8_C[1] + 64 <= LODGE_IN[3], REG8_C
assert ISLAND[0] <= REG9_C[0] - 64 and REG9_C[0] + 64 <= ISLAND[2] and ISLAND[1] <= REG9_C[1] - 64 <= REG9_C[1] + 64 <= ISLAND[3], REG9_C

import os as _os
import time as _time
_t0 = _time.time()
MEASURE, PROBLEMS = measure()
MEASURE[0] += f" ({_time.time() - _t0:.1f} s)"
if PROBLEMS:
    raise SystemExit("MAP19: " + "; ".join(PROBLEMS) + "\n" + "\n".join(MEASURE))

I1.m, CD.m = _theirs, _cd

if __name__ == "__main__":
    import sys
    sys.stdout.write(m.textmap())
