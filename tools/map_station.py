"""The third secret level: "Third Person" (MAP33), reached by MAP20's secret
way out once MAP20 is built. PLAN.md: "MAP33, the third secret level" (the
outline), "The three goes lab" (the engine: src/zscript/third.zs, its helpers
tools/ajarthird.py, the lab map tools/map_third.py), "MAP33 "Third Person": the
first version, as decided" (this map's design), "... the first playable
version" (what was built), "MAP33: the last fight in the level, and doors at
the fight halls" (the end and the lobbies), "MAP33: the yard in the middle, on
three levels, as decided" and "... built" (the common place). The tests:
src/zscript/map33.zs, MAP=MAP33 MODE=n tools/smoke.sh.

A power station, played whole three times: go k plays part k, and the time
door at the end of part k leads to before, into box k + 1, which looks onto
the gatehouse S where the earlier selves set off. No part is joined to
another on foot (ajarthird.apart): where they meet it is glass, a railing or
a height. North is up (+y), x east; about 9000 x 3000 of rooms in a frame of
9400 x 5400.

Part 1, yellow, along the north (S, the coal yard, the boiler house, the ash
tunnel and its cache, the pump room, the stack court, the yard's terrace and
north ledge, the gantry over the turbine hall, the corridor to stand 1). Part
2, green, through the middle (box 2, the gallery, the workshop and its
armoury, the yard's floor and its pump shed, the mezzanine, the turbine hall
R, the passage to stand 2). Part 3, red, along the south (box 3, the cable
tunnel, the switchyard, the relay room, the cooling pond, the cooling tower,
the yard's corner piece and south ledge, the duct along R's south wall, the
corridor to stand 3, the exit door across the hall).

The yard (common.zs, the engine's COMMON PLACE; PLAN.md "MAP33: the yard in
the middle, built"), where part 2's pump hall and stores were: open to the
sky, x 3968..4736. Its floor (-128, part 2's level) between the ledges (y
2240..3456), in down stairs from the workshop's corridor on the west and out
up stairs into the mezzanine's corridor on the east; four pumps, two pipe
runs, banks on the west and east walls; the pump shed (part 2's secret) in the
west wall. The terrace at its north-east corner (where the passage from the
stack court to the gantry was) and the ledge along its north rim (0, part 1's
level); the corner piece north of the tower's passage and the ledge along its
south rim (-64, part 3's level). Rims (players only) between the levels; each
part's group comes when its go first stands on its level, and its way on (the
gantry's west mouth, the shutter at the head of the east stairs, the one at
the duct stairs' mouth) opens when the group is dead; in later goes the group
comes again with its earlier self there firing. Part 2's walkers lie as
bodies on the floor in go 1.

The end (the last fight, the engine's last.zs as in the lab LAST,
tools/map_last.py): the switchgear hall, east of R, sunk to -96, with three
stands round it: 1 on the north, 2 on the west, 3 on the south. Plate 1 on
stand 1 rings the alarm: the guards (AjarThirdGuard, by skill) come to life
round the hall, on pedestals, in bays and on the floor among the switchgear
cabinets. Go 1 holds plate 1 30 seconds in all (its time door opens then), go 2
plate 2 15 seconds while plate 1 is held, and go 3 crosses the hall from
stand 3's gate (shut to monsters) to the exit door in the east wall, open while
both plates are held. The lab's four ways the selves help each other are in
it (PLAN.md, "MAP33: the last hall with the four rules"): the guards come in
waves (wave 1 at the alarm: every guard that stands; wave 2 at plate 2's first
press from the alarm on: the flyers and the knights, on green patches; wave 3
in go 3 when the third self steps onto the hall's floor: the demons and the
barons, on red patches before the exit door); one invulnerability sphere for
the three, a copy on each stand; an earlier self hit by 60 holds its fire for
three seconds; a steam valve on stand 1 (it blows over the blue strip before
the exit door) and a breaker on stand 2 (it stuns the hall), each worked once a
go and again by itself in the later goes.

Window halls (third.zs): 1 the coal yard (part 1; its gate opens when it is
clear), 2 the workshop (part 2; seen from the relay room), 3 the turbine hall
R (part 2; its gantry is the watched place, its posts the future seen; seen
from the duct), 4 the boiler house (part 1; seen from the gallery, so that
BLUE hung again is seen with the fight round it as it was), 5 the cooling
tower (part 3; its exit opens when it is clear: part 3 cannot be run through).
The coal yard, the boiler house and the workshop are come into through a
lobby between two shutters (AjarThirdLock, ajarthird.lock): the outer one
shuts behind the player, then the inner one opens, and both stay open once
the hall is won; their other ways on are win shutters. So no monster of
these halls leaves them and no invisible line stands in an open doorway.
The gallery's monsters (part 2) are fallen things (ajarthird.fallen): go 1 sees
them through its windows dead, as go 2, which passes there first, leaves them.

The yards out of doors (the coal yard, the stack court, the switchyard) and
the pond are natural(): banks heaped against their walls in terraces
(bank(), with no dents in a terrace's front: mapcheck's pockets), irregular
heaps and islands (heap(), blob()), round things (ngon()); what stands there
is put on free floor (put(), items_on()).

Generator checks: the parts apart (the rims closed); every window hall closed to monsters at its
mouths, and the lobbies' halls with no monster-only line in an open way;
every post where its monster cannot leave and in sight from the gantry; the
supplies of each part against its monsters (tools/budget.py), the last hall's
guards apart; every standing guard in sight of a plate and of the crossing,
the crossing with cover from each; wave 1 the standing guards, wave 3 east of
the crossing's middle and 256 or more from the foot of stand 3's steps, the
patches clear of the islands and the red ones by the door on the strip, the
strip's floor all within the steam's reach, the share's copies and the levers
clear of the plates, time doors, wind plates and cases; the yard's levels
tagged and each its part's, the place closed to monsters, every walking comer
on the floor's level with room and none within 256 of the west stairs' foot,
every flyer over the floor with room, every body seen from two of the terrace
and the ledges, the shed's doorway 64, nothing over 24 high before a stairs'
foot; each part's length on foot (python3 tools/map_station.py --walk).
"""
import heapq
import math
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
import ajarmap
import ajartime
import ajarthird
import budget
from ajarmap import BLUE, VIOLET, PINK, far_id
from udmf import Map, rect, MONSTERS

m = Map()

# --- heights, tags, colours -----------------------------------------------------------
G, RF, CAT = 0, -128, 128       # the ground; the turbine hall's floor; the boiler house's catwalk and the pump room
SKY = 448                       # an open yard's sky
YARD, WORK, RT, BOIL = 3341, 3342, 3343, 3344          # the window halls' sector tags
GANTRY = 3346                   # the gantry: R's second tag, the watched place
GATE, GSHUT, STEEL, EXIT, OUT, RELAYSHUT = 3351, 3352, 3353, 3354, 3355, 3356
TOWER, TSHUT = 3347, 3357       # the cooling tower (window hall 5) and its exit's shutter
LASTT, ALARM = 3358, 3359       # the last hall L (its floor, pedestals, bays, cabinets, steps); stand 3's gate
# the lobbies (ajarthird.lock): each window hall's outer shutter, inner shutter, lobby
YOUT, YIN, YLOB = 3371, 3372, 3373                      # the coal yard
BOUT, BIN, BLOB = 3374, 3375, 3376                      # the boiler house
WOUT, WIN_, WLOB = 3377, 3378, 3379                     # the workshop
CATSHUT, ASHSHUT, PUMPSHUT = 3380, 3381, 3382           # the ways on its win opens: the boiler house's two, the workshop's
H_YARD, H_WORK, H_R, H_BOIL, H_TOWER = 1, 2, 3, 4, 5    # the window halls' numbers
F_BLUE, F_VIOLET, F_PINK, F_CACHE = 101, 102, 103, 104  # frames

Y_ROOM, Y_WAY = 0xF2EAD0, 0xFFE070      # part 1: its rooms, and its corridors and doorways (yellow)
G_ROOM, G_WAY = 0xDCECDA, 0x98EC8C      # part 2 (green)
R_ROOM, R_WAY = 0xF2DCD8, 0xFF9C8C      # part 3 (red)
HALLC = 0xD8D6D0                         # the turbine hall
COAL = 0x58585C
STEELC = 0x9CA4AC
RAIL = dict(mid="AJRAIL", midboth=True, blocking=True, dontpegbottom=True)
BARS = dict(mid="AJGRIL", midboth=True, blocking=True, dontpegbottom=True)


class _Holes:
    """ajarmap.shaped() draws through this: a piece marked `hole` is left out (solid)."""
    def sector(self, poly, **props):
        if not props.pop("hole", False):
            m.sector(poly, **props)


def area(box, feats=(), holes=(), **base):
    """A room `box` with raised or sunk pieces (`feats`: (rect or convex polygon,
    changes)) and solid pieces (`holes`)."""
    ajarmap.shaped(_Holes(), box, list(feats) + [(h, dict(hole=True)) for h in holes], **base)


def inside(poly, x, y):
    n = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            n = not n
    return n


class _Cells:
    """Things with a bounding box, found again by the cells they touch."""
    def __init__(self, size=128):
        self.size, self.d = size, {}

    def keys(self, box):
        c = self.size
        for ix in range(int(box[0] // c), int(box[2] // c) + 1):
            for iy in range(int(box[1] // c), int(box[3] // c) + 1):
                yield ix, iy

    def add(self, box, item):
        for k in self.keys(box):
            self.d.setdefault(k, []).append(item)

    def near(self, box):
        out = set()
        for k in self.keys(box):
            out.update(self.d.get(k, ()))
        return out


class _SecIndex:
    """sec_at's look-up, made again whenever sectors have been added."""
    n = -1

    def __call__(self, x, y):
        if self.n != len(m.polys):
            self.n, self.cells = len(m.polys), _Cells(256)
            self.fl = [[(float(a), float(b)) for a, b in p] for p in m.polys]
            for i, p in enumerate(self.fl):
                self.cells.add((min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p)), i)
        for i in sorted(self.cells.near((x, y, x, y))):
            if inside(self.fl[i], x, y):
                return i
        return None


_SEC = _SecIndex()


def sec_at(x, y):
    """The sector at x, y (its index)."""
    return _SEC(x + .5, y + .5)


# --- natural rooms: banks, heaps, round things (2026-11-24, after Vadim's first play) ----------------
# area() cuts a room into a grid at every corner of every piece, which is right for furniture in rows
# and wrong for a yard full of irregular slanting shapes (thousands of slivers). natural() takes the
# pieces as they are: their edges make a plan, each piece of floor between edges is one sector (any
# form, not only convex), and a piece standing free (a heap) is tied to the rest by an upright cut
# above and below it, so that no sector has a hole in it.
def _isrect(s):
    return len(s) == 4 and not isinstance(s[0], (tuple, list))


def _num(v):
    return int(v) if isinstance(v, Fraction) and v.denominator == 1 else v


def _pt(p):
    return (_num(p[0]), _num(p[1]))


def _orient(p, q, r):
    v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (v > 0) - (v < 0)


def _sbox(s):
    (ax, ay), (bx, by) = s
    return (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))


def _split_segs(segs):
    """Every segment cut at every corner that lies on it (exactly: ints and Fractions)."""
    cells = _Cells(64)
    for v in {v for s in segs for v in s}:
        cells.add((v[0], v[1], v[0], v[1]), v)
    out = set()
    for a, b in segs:
        dx, dy = b[0] - a[0], b[1] - a[1]
        n2 = dx * dx + dy * dy
        mids = []
        for v in cells.near(_sbox((a, b))):
            if v == a or v == b:
                continue
            px, py = v[0] - a[0], v[1] - a[1]
            if dx * py - dy * px:
                continue
            t = Fraction(px * dx + py * dy) / n2
            if 0 < t < 1:
                mids.append((t, v))
        pts = [a] + [v for _, v in sorted(mids)] + [b]
        for p, q in zip(pts, pts[1:]):
            out.add((p, q) if p < q else (q, p))
    return out


def _no_crossings(segs):
    L = sorted(segs)
    cells = _Cells(128)
    for i, s in enumerate(L):
        cells.add(_sbox(s), i)
    for i, (a, b) in enumerate(L):
        for j in cells.near(_sbox((a, b))):
            if j <= i:
                continue
            c, d = L[j]
            if len({a, b, c, d}) < 4:
                continue
            if _orient(a, b, c) * _orient(a, b, d) < 0 and _orient(c, d, a) * _orient(c, d, b) < 0:
                raise AssertionError(("two edges of a natural room cross", (a, b), (c, d)))


def _tie(segs, anchor):
    """Each piece of the plan not joined to the outline (a heap, a pillar, a tier on a heap) gets an
    upright cut from its top corner up and from its bottom corner down, to the first edge met."""
    segs = set(segs)
    up = {}

    def root(v):
        while up.get(v, v) != v:
            up[v] = up.get(up[v], up[v])
            v = up[v]
        return v
    for a, b in segs:
        ra, rb = root(a), root(b)
        if ra != rb:
            up[ra] = rb
    groups = {}
    for v in {v for s in segs for v in s}:
        groups.setdefault(root(v), []).append(v)
    main = root(anchor)
    for r in sorted(groups, key=lambda r: min(groups[r])):
        if r == main:
            continue
        vs = groups[r]
        for v, sign in ((max(vs, key=lambda v: (v[1], -v[0])), 1), (min(vs, key=lambda v: (v[1], v[0])), -1)):
            x0, best = v[0], None
            for s in segs:
                (ax, ay), (bx, by) = s
                if not min(ax, bx) <= x0 <= max(ax, bx):
                    continue
                if ax == bx:
                    y = min(ay, by) if sign > 0 else max(ay, by)
                else:
                    y = ay + Fraction(x0 - ax) * (by - ay) / (bx - ax)
                if (y - v[1]) * sign > 0 and (best is None or (y - best[0]) * sign < 0):
                    best = (y, s)
            assert best, ("nothing above or below", v)
            h = _pt((x0, best[0]))
            s = best[1]
            if h not in s:
                segs.discard(s)
                for p, q in ((s[0], h), (h, s[1])):
                    segs.add((p, q) if p < q else (q, p))
            segs.add((v, h) if v < h else (h, v))
    return segs


def _faces(segs):
    """The faces of a joined plan, each a list of corners anticlockwise (and the outside, clockwise)."""
    adj = {}
    for a, b in segs:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    pos = {}
    for v, ns in adj.items():
        ns.sort(key=lambda w: math.atan2(float(w[1] - v[1]), float(w[0] - v[0])))
        for i, w in enumerate(ns):
            pos[v, w] = i
    seen, faces = set(), []
    for a, b in sorted(segs):
        for e in ((a, b), (b, a)):
            if e in seen:
                continue
            face = []
            while e not in seen:
                seen.add(e)
                face.append(e[0])
                u, v = e
                e = (v, adj[v][pos[v, u] - 1])
            faces.append(face)
    return faces


def _area2(poly):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))


def _probe(face):
    """A point just inside a face (anticlockwise): off the middle of its longest edge, to its left."""
    best = None
    for a, b in zip(face, face[1:] + face[:1]):
        ln = math.hypot(float(b[0] - a[0]), float(b[1] - a[1]))
        if best is None or ln > best[0]:
            best = (ln, a, b)
    ln, a, b = best
    return ((float(a[0]) + float(b[0])) / 2 - float(b[1] - a[1]) / ln * 0.05,
            (float(a[1]) + float(b[1])) / 2 + float(b[0] - a[0]) / ln * 0.05)


def _pin(poly, p):
    return inside([(float(x), float(y)) for x, y in poly], *p)


def natural(outline, feats=(), holes=(), **base):
    """A room of the polygon (or box) `outline` with raised or sunk pieces `feats` ((rect or polygon of
    any form, changes); later ones win where they lie in each other) and solid pieces `holes`. Pieces
    may lie in each other or touch, not cross. Returns the sectors."""
    outline = rect(*outline) if _isrect(outline) else list(outline)
    feats = [(rect(*s) if _isrect(s) else list(s), ch) for s, ch in feats]
    holes = [rect(*h) if _isrect(h) else list(h) for h in holes]
    segs = set()
    for poly in [outline] + [s for s, _ in feats] + holes:
        poly = [_pt(p) for p in poly]
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if a != b:
                segs.add((a, b) if a < b else (b, a))
    segs = _split_segs(segs)
    _no_crossings(segs)
    segs = _tie(segs, _pt(outline[0]))
    out = []
    for f in _faces(segs):
        if _area2(f) <= 0:
            continue
        p = _probe(f)
        assert _pin(outline, p), ("a piece outside its room", f[:4])
        if any(_pin(h, p) for h in holes):
            continue
        props = dict(base)
        for s, ch in feats:
            if _pin(s, p):
                props.update(ch)
        out.append(m.sector(f, **props))
    return out


def hull(pts):
    """The convex hull of integer points, anticlockwise."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def half(ps):
        h = []
        for p in ps:
            while len(h) >= 2 and _orient(h[-2], h[-1], p) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, hi = half(pts), half(pts[::-1])
    return lo[:-1] + hi[:-1]


def ngon(cx, cy, r, n, turn=0.5):
    """A round thing as a regular n-gon of corner radius r (corners rounded to whole units)."""
    return [(round(cx + r * math.cos(2 * math.pi * (i + turn) / n)), round(cy + r * math.sin(2 * math.pi * (i + turn) / n)))
            for i in range(n)]


def blob(rng, cx, cy, rx, ry, n, rot=None):
    """An irregular convex polygon of about n corners round cx, cy: no edge along x or y longer than 48."""
    for _ in range(200):
        r0 = rng.uniform(0, 2 * math.pi) if rot is None else rot
        pts = []
        for i in range(n):
            a = r0 + 2 * math.pi * (i + rng.uniform(-.3, .3)) / n
            k = rng.uniform(.84, 1.08)
            pts.append((round(cx + rx * k * math.cos(a)), round(cy + ry * k * math.sin(a))))
        h = hull(pts)
        if len(h) >= min(n, 8) - 1 and all(not ((a[0] == b[0] or a[1] == b[1]) and abs(a[0] - b[0]) + abs(a[1] - b[1]) > 48)
                                          for a, b in zip(h, h[1:] + h[:1])):
            return h
    raise AssertionError(("no blob", cx, cy))


def _dist_seg(p, a, b):
    ax, ay, bx, by = float(a[0]), float(a[1]), float(b[0]), float(b[1])
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def margin(inner, outer):
    """How far the polygon `inner` keeps inside `outer` (negative: it does not lie inside)."""
    d = min(_dist_seg(p, a, b) for p in inner for a, b in zip(outer, outer[1:] + outer[:1]))
    return d if all(_pin(outer, p) for p in inner) else -d


def heap(seed, cx, cy, rx, ry, tiers, *, n=7, inset=(44, 60)):
    """A heap: `tiers` nested irregular convex polygons, each `inset` (min, max) inside the one before."""
    rng = random.Random(seed)
    out = [blob(rng, cx, cy, rx, ry, n)]
    for k in range(1, tiers):
        for _ in range(400):
            d = rng.uniform(*inset)
            c = (sum(p[0] for p in out[-1]) / len(out[-1]), sum(p[1] for p in out[-1]) / len(out[-1]))
            rxk = rx - d * k * rx / max(rx, ry) * 1.05
            ryk = ry - d * k * ry / max(rx, ry) * 1.05
            t = blob(rng, c[0] + rng.uniform(-12, 12), c[1] + rng.uniform(-12, 12), rxk, ryk, rng.choice((6, 7, 8)))
            if margin(t, out[-1]) >= 30:
                out.append(t)
                break
        else:
            raise AssertionError(("no tier", seed, k))
    return out


def bank(seed, path, env, *, ground, heights=(40, 88, 136), gaps=((40, 64), (40, 64)), step=(44, 84), least=24, avoid=(), keep=24):
    """Ground heaped against the walls along `path` (corners on the room's walls, the room on the left
    hand going along it): terraces `heights` over `ground`, rising towards the wall, each the gap
    (gaps[k - 1]: min, max) nearer the wall than the one before. `env`: [(distance along the path,
    depth)], what the front terrace reaches into the room at most (each station 62 to 100 per cent of
    it); depth 0 at an end that is not a corner of the room. `avoid`: rectangles the bank keeps 24 off
    (it is made shallower where it would come nearer). Returns the terraces' polygons by height:
    [[polygon, ...], ...]."""
    rng = random.Random(seed)
    legs = list(zip(path, path[1:]))
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in legs]
    total = sum(lens)

    def envd(t):
        for (t0, d0), (t1, d1) in zip(env, env[1:]):
            if t0 <= t <= t1:
                return d0 + (d1 - d0) * (t - t0) / (t1 - t0) if t1 > t0 else d1
        return env[-1][1]

    def leg(t):
        acc = 0
        for k, ln in enumerate(lens):
            if t <= acc + ln or k == len(lens) - 1:
                return k, t - acc
            acc += ln

    def wall(t):
        """The point of the wall at t along the path, exactly on it."""
        k, s = leg(t)
        a, b = legs[k]
        f = Fraction(s).limit_denominator(64) / Fraction(lens[k]).limit_denominator(64) if s else Fraction(0)
        f = min(f, Fraction(1))
        return _pt((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))

    def at(t, d):
        k, s = leg(t)
        (ax, ay), (bx, by) = legs[k]
        ux, uy = (bx - ax) / lens[k], (by - ay) / lens[k]
        return (round(ax + ux * s - uy * d), round(ay + uy * s + ux * d))
    corners = []
    acc = 0
    for ln in lens[:-1]:
        acc += ln
        corners.append(acc)
    ts, t = [0.0], 0.0
    while True:
        t += rng.randint(*step)
        if t > total - step[0] * .6:
            break
        if any(abs(t - c) < envd(t) + 24 for c in corners):         # (by a corner the bank cuts across it)
            continue
        ts.append(t)
    ts.append(total)
    assert env[0][1] == 0 and env[-1][1] == 0, "a bank ends at the wall"
    v, k = [0], rng.uniform(.7, 1.0)
    for t in ts[1:-1]:
        k = min(1.0, max(.62, k + rng.uniform(-.16, .16)))         # (a wandering share of the envelope)
        d = round(envd(t) * k)
        while abs(d - v[-1]) < 10:
            d += rng.choice((-12, 12))
        v.append(max(d, 0))
    v.append(0)

    def hits(p, q):
        n = int(math.hypot(q[0] - p[0], q[1] - p[1]) // 8) + 1
        return any(a[0] - keep < p[0] + (q[0] - p[0]) * i / n < a[2] + keep and a[1] - keep < p[1] + (q[1] - p[1]) * i / n < a[3] + keep
                   for i in range(n + 1) for a in avoid)

    def smooth(row, cap=None):
        """No pockets (2026-11-24): mapcheck's SLOT finds a place where a body 32 wide stands and one 48 wide
        does not in every dent of a terrace's front (a station nearer the wall than the line between its
        neighbours: the floor before it is a V), and where two runs of a terrace come down to the wall less
        than 64 apart. So a dent is filled up to that line (never past `cap`, the terrace below less 40, nor
        near what the bank avoids: there the run is cut back to the wall instead), and of two runs too near
        the smaller end is cut back. Station values only rise to a line between their neighbours or drop
        to 0, so it ends."""
        if cap:
            row = [min(d, c) for d, c in zip(row, cap)]
        row = [d if d >= least else 0 for d in row]
        n = len(row)
        for _ in range(4 * n + 50):
            changed = False
            i = 1
            while i < n - 1:
                if row[i] == 0 and row[i - 1] > 0:
                    j = i
                    while j < n - 1 and row[j] == 0:
                        j += 1
                    if row[j] > 0 and ts[j - 1] - ts[i] < 64:
                        row[i - 1 if row[i - 1] <= row[j] else j] = 0
                        changed = True
                    i = j
                i += 1
            for i in range(1, n - 1):
                if row[i] <= 0:
                    continue
                chord = row[i - 1] + (row[i + 1] - row[i - 1]) * (ts[i] - ts[i - 1]) / (ts[i + 1] - ts[i - 1])
                if row[i] < chord - .5:
                    want = math.ceil(chord)
                    if (cap and want > cap[i]) or hits(at(ts[i - 1], row[i - 1]), at(ts[i], want)) or \
                            hits(at(ts[i], want), at(ts[i + 1], row[i + 1])):
                        row[i] = 0
                    else:
                        row[i] = want
                    changed = True
            if not changed:
                return row
        raise AssertionError(("a bank's terrace does not settle", seed))
    for _ in range(60):
        bad = [i for i in range(len(ts) - 1) if hits(at(ts[i], v[i]), at(ts[i + 1], v[i + 1]))]
        if not bad:
            break
        for i in bad:
            v[i], v[i + 1] = int(v[i] * .85), int(v[i + 1] * .85)
    else:
        raise AssertionError(("a bank cannot keep off", avoid))
    rows = [smooth(v)]
    for k in range(1, len(heights)):
        g = gaps[min(k - 1, len(gaps) - 1)]
        rows.append(smooth([d - rng.randint(*g) if d > 0 else d for d in rows[-1]], [d - 40 for d in rows[-1]]))
    cum = [sum(lens[:k + 1]) for k in range(len(legs) - 1)]
    out = []
    for row in rows:
        row = [d if d >= least else 0 for d in row]
        polys = []
        i = 1
        while i < len(ts):
            if row[i] <= 0:
                i += 1
                continue
            j = i
            while row[j] > 0:
                j += 1
            ta, tb = ts[i - 1], ts[j]
            polys.append([wall(ta)] + [at(ts[k], row[k]) for k in range(i, j)] + [wall(tb)]
                         + [_pt(path[k + 1]) for k in range(len(cum) - 1, -1, -1) if ta < cum[k] < tb])
            i = j
        out.append(polys)
    return out


PLACED = []          # (x, y, r): the monsters put by spot(), kept apart


def stands(x, y, r, floor):
    """mapcheck's test and more: the square of half-side r round x, y (corners, middles of the sides,
    halfway) lies on sectors whose floor is `floor`."""
    for dx in (-r, -r / 2, 0, r / 2, r):
        for dy in (-r, -r / 2, 0, r / 2, r):
            s = sec_at(x + dx, y + dy)
            if s is None or m.sectors[s]["floor"] != floor:
                return False
    return True


def spot(x, y, r, floor, *, solid=True, reach=384):
    """The free floor nearest x, y (8 apart): where a thing of radius r stands wholly on `floor`, 8 more
    to spare, and (`solid`) clear of the monsters put before. Natural rooms put their things so: what
    would stand on a bank or a heap goes to the floor beside it."""
    for d in range(0, reach + 1, 8):
        ring = [(x, y)] if d == 0 else sorted({(x + i, y + j) for i in range(-d, d + 1, 8) for j in (-d, d)}
                                              | {(x + i, y + j) for j in range(-d, d + 1, 8) for i in (-d, d)},
                                              key=lambda p: ((p[0] - x) ** 2 + (p[1] - y) ** 2, p))
        for px, py in ring:
            if stands(px, py, r + 8, floor) and (not solid or all(max(abs(px - qx), abs(py - qy)) >= r + qr + 8
                                                                  for qx, qy, qr in PLACED)):      # (Doom's boxes)
                if solid:
                    PLACED.append((px, py, r))
                return px, py
    raise AssertionError(("no free floor near", x, y, floor))


def put(kind, pts, floor, angle=0, skill=None, **kw):
    """Monsters of `kind` at the free floor nearest each of `pts` (spot)."""
    for x, y in pts:
        px, py = spot(x, y, ajartime.RADIUS[kind], floor)
        if skill:
            kw = dict(kw, skill=skill)
        m.thing(px, py, kind, angle=angle, **kw)


def items_on(floor, kind, *pts):
    """Items at the free floor nearest each of `pts`."""
    for x, y in pts:
        m.thing(*spot(x, y, 16, floor, solid=False), kind)


def free_grid(box, n, floor, *, step=96, r=32, avoid=()):
    """n places spread over a grid in `box` where a thing of radius r stands on `floor` (stands), not in
    the rectangles `avoid`; as grid() does it."""
    x1, y1, x2, y2 = box
    pts = []
    y = y1 + r + 8
    while y <= y2 - r - 8:
        x = x1 + r + 8
        while x <= x2 - r - 8:
            if not any(a[0] <= x <= a[2] and a[1] <= y <= a[3] for a in avoid) and stands(x, y, r + 8, floor):
                pts.append((x, y))
            x += step
        y += step
    assert len(pts) >= n, (box, n, len(pts))
    out = [pts[int(i * len(pts) / n)] for i in range(n)]
    PLACED.extend((x, y, r) for x, y in out)
    return out


def grid(box, n, *, step=96, r=24, avoid=()):
    """n places spread over a grid in `box`, `r` clear of its walls and of the
    rectangles `avoid` (grown by r + 8)."""
    x1, y1, x2, y2 = box
    pts = []
    y = y1 + r + 8
    while y <= y2 - r - 8:
        x = x1 + r + 8
        while x <= x2 - r - 8:
            if not any(a[0] - r - 8 < x < a[2] + r + 8 and a[1] - r - 8 < y < a[3] + r + 8 for a in avoid):
                pts.append((x, y))
            x += step
        y += step
    assert len(pts) >= n, (box, n, len(pts))
    return [pts[int(i * len(pts) / n)] for i in range(n)]


def mon(kind, pts, angle=0, skill=None):
    for x, y in pts:
        if skill:
            m.thing(x, y, kind, angle=angle, skill=skill)
        else:
            m.thing(x, y, kind, angle=angle)


def items(kind, *pts):
    for x, y in pts:
        m.thing(x, y, kind)


def opening(a, b, out, floor, color, thick=16, ceil=96):
    """A doorway in a wall, tinted with its part's colour."""
    c = (a[0] + out[0] * thick, a[1] + out[1] * thick)
    d = (b[0] + out[0] * thick, b[1] + out[1] * thick)
    return m.sector([a, b, d, c], floor=floor, ceil=floor + ceil, light=176, wall="AJTRIM", ftex="AJTRIMF",
                    ctex="AJTRIMF", color=color)


def no_monsters(a, b):
    """No monster walks or flies over the line a-b (a window hall's mouth)."""
    m.line(a, b, blockmonsters=True)
    MOUTHS.append((a, b))


def railing(a, b):
    m.line(a, b, **RAIL)


MOUTHS = []          # every window hall's mouths (checked below)
CASES = []


def case(a, b, out, floor, figures, **look):
    """A glass case (ajartime.case) with figures: (x, y, what, kind, angle),
    each inside it (8 clear of its walls; a frame against the back wall)."""
    si = ajartime.case(m, a, b, out, floor, **look)
    deep = 96
    xs = [a[0], b[0], a[0] + out[0] * (16 + deep), b[0] + out[0] * (16 + deep)]
    ys = [a[1], b[1], a[1] + out[1] * (16 + deep), b[1] + out[1] * (16 + deep)]
    for x, y, what, kind, ang in figures:
        r = 1 if what in ("frame", "hung") else 8
        assert min(xs) + r < x < max(xs) - r and min(ys) + r < y < max(ys) - r, (x, y, what)
        ajartime.figure(m, x, y, what, kind=kind, angle=ang)
    CASES.append(si)
    return si


def three(a, b, out, floor, **look):
    """The sign of the level, in a case: the first self (yellow) and the
    second (green) each on a plate, the third (red) walking into a door
    frame at the back."""
    ux, uy = (b[0] - a[0], b[1] - a[1])
    ln = math.hypot(ux, uy)
    ux, uy = ux / ln, uy / ln
    face = {(0, 1): 270, (0, -1): 90, (1, 0): 180, (-1, 0): 0}[tuple(out)]
    back = {(0, 1): 90, (0, -1): 270, (1, 0): 0, (-1, 0): 180}[tuple(out)]

    def at(along, deep):
        return (round(a[0] + ux * along + out[0] * (16 + deep)), round(a[1] + uy * along + out[1] * (16 + deep)))
    figs = []
    for k, along in ((1, 0.22), (2, 0.48)):
        x, y = at(ln * along, 40)
        figs += [(x, y, "plate", 0, 0), (x, y, "me", k, face), (x, y, "go", k, 0)]
    fx, fy = at(ln * 0.78, 94)
    wx, wy = at(ln * 0.78, 64)
    figs += [(fx, fy, "frame", 0, face), (wx, wy, "walking", 3, back), (wx, wy, "go", 3, 0)]
    return case(a, b, out, floor, figs, **look)


# =====================================================================================
# PART 1, yellow: the boiler side
# =====================================================================================
# --- S, the gatehouse: the start; box 2 and box 3 look into it from the south ---------
S_BOX = (0, 2560, 768, 3200)
area(S_BOX, [((96, 2976, 352, 3040), dict(floor=40, side="AJWOOD")),          # the gatekeeper's counter
             ((96, 3040, 128, 3136), dict(floor=40, side="AJWOOD"))],
     holes=[(224, 2752, 288, 2816), (480, 2752, 544, 2816)],                   # two pillars
     ceil=192, light=200, color=Y_ROOM)
m.thing(384, 2640, 1, angle=90)
m.thing(640, 3040, 2001, angle=180)                    # a shotgun
items(2008, (680, 3100), (600, 3100))
items(2011, (160, 2640))
three((0, 2816), (0, 3008), (-1, 0), G, color=Y_ROOM)
# the doorway north, a corridor, the coal yard
opening((448, 3200), (576, 3200), (0, 1), G, Y_WAY)
m.sector(rect(448, 3216, 576, 3552), ceil=128, light=170, color=Y_WAY)
# the yard's lobby, the corridor's last 128 (third.zs, AjarThirdLock): the outer shutter across the corridor
# (worked from the lobby's side), the inner one at the yard's mouth
ajartime.shutter(m, (448, 3568), (576, 3568), (0, -1), G, YOUT, color=Y_WAY)
m.sector(rect(448, 3568, 576, 3696), ceil=128, light=170, color=Y_WAY, id=YLOB)
ajartime.shutter(m, (448, 3696), (576, 3696), (0, 1), G, YIN, color=Y_WAY)
mon(3004, [(480, 3460), (544, 3400)], angle=270)

# --- the coal yard: window hall 1, open to the sky -----------------------------------
# (after Vadim's first play: irregular heaps, the bunker's wall bowed, coal banked against the walls;
# kept clear: the corridor's mouth, the gallery's windows (nothing over 24 within 256 of the glass),
# the gate, and a walk 256 wide from the mouth to the gate)
YARD_BOX = (256, 3712, 1920, 4992)
COALY = dict(color=COAL, ftex="AJPIT", side="AJWALL")
HEAPS = [heap(11, 610, 4200, 135, 130, 3), heap(12, 980, 4075, 105, 80, 2), heap(13, 1430, 4100, 135, 95, 2),
         heap(14, 820, 4466, 100, 72, 2), heap(15, 1180, 4370, 160, 112, 3), heap(16, 1545, 4420, 75, 92, 2)]
yfeat = [(t, dict(floor=f, **COALY)) for h in HEAPS for t, f in zip(h, (32, 72, 104))]
BUNKER_FACE = [(256, 4672), (700, 4600), (1100, 4576), (1520, 4608), (1920, 4672)]      # bowed 96 south in the middle
for (ax, ay), (bx, by) in zip(BUNKER_FACE, BUNKER_FACE[1:]):
    yfeat.append(([(ax, ay), (bx, by), (bx, by + 64), (ax, ay + 64)], dict(floor=176, side="AJBRICK", ftex="AJTRIMF")))
yfeat.append(((320, 4800, 1856, 4928), dict(floor=48, color=COAL, ftex="AJPIT")))    # coal in the bunker
YBANKS = [bank(21, [(256, 4600), (256, 3712), (340, 3712)],                         # the west wall and the south-west corner
               [(0, 0), (60, 150), (200, 250), (270, 150), (560, 140), (590, 185), (616, 90), (860, 85), (972, 0)], ground=G),
          bank(22, [(1920, 4590), (1920, 4672), (1520, 4608)],                      # the north-east corner, by the gate
               [(0, 0), (30, 50), (82, 60), (200, 60), (330, 58), (400, 95), (460, 50), (487, 0)], ground=G,
               heights=(40, 88), gaps=((30, 40),))]
yfeat += [(t, dict(floor=G + h, **COALY)) for b in YBANKS for h, ts in zip((40, 88, 136), b) for t in ts]
natural(YARD_BOX, yfeat, ceil=SKY, ctex="F_SKY1", light=210, wall="AJBRICK", color=Y_ROOM, id=YARD)
ajarthird.hall(m, 400, 3740, H_YARD, 1, YARD, YLOB)
ajarthird.lock(m, 512, 3640, H_YARD, YOUT, YIN, YLOB)
# the gate to the boiler house: shut until the yard is clear
ajartime.shutter(m, (1920, 4480), (1920, 4352), (1, 0), G, GATE, nomonsters=True, color=Y_WAY)
MOUTHS.append(((1920, 4480), (1920, 4352)))
# the boiler house's lobby: the passage behind the gate, between shutters of its own (the outer just east of
# the gate, the inner at the passage's east end, which runs 32 into the boiler house so that the lobby is 112)
ajartime.shutter(m, (1952, 4480), (1952, 4352), (-1, 0), G, BOUT, color=Y_WAY)
m.sector(rect(1952, 4352, 2064, 4480), ceil=128, light=170, color=Y_WAY, id=BLOB)
ajartime.shutter(m, (2064, 4480), (2064, 4352), (1, 0), G, BIN, color=Y_WAY)
ajarthird.win(m, 1900, 4416, H_YARD, GATE)
# the fight: zombiemen, sergeants, imps and demons in the yard; cacodemons behind the bunker's wall
YARD_FLOOR = (288, 3744, 1888, 4640)
yard_pts = free_grid(YARD_FLOOR, 40, G, step=96, r=32, avoid=[(256, 3712, 704, 3904)])
mon(3004, yard_pts[0:9], angle=270)
mon(9, yard_pts[9:18], angle=270)
mon(3001, yard_pts[18:30], angle=270)
mon(3002, yard_pts[30:37], angle=270)
mon(3002, yard_pts[37:40], angle=270, skill=4)
mon(3005, [(448, 4864), (768, 4864), (1088, 4864), (1408, 4864), (1728, 4864)], angle=270)
mon(3005, [(608, 4864), (1568, 4864)], angle=270, skill=4)
items_on(G, 2008, (360, 3800), (1800, 3800), (1800, 4300), (400, 4400))
items_on(G, 2049, (980, 4250), (1300, 4280))
items_on(G, 2012, (1320, 3800), (900, 3780))
items_on(G, 2011, (420, 4200), (1860, 4560))
items_on(G, 2018, (1000, 4520))

# --- the boiler house: window hall 4. BLUE leans on the floor; its frame is in the
# first boiler's face; its far side is on the catwalk, 128 up, where the way on is ----
BOIL_BOX = (2048, 3712, 3584, 4992)
CATWALK = (2048, 4800, 3584, 4992)
BOILERS = [(2176, 4224, 2400, 4544), (2528, 4224, 2752, 4544), (2880, 4224, 3104, 4544), (3232, 4224, 3456, 4544)]
FRAME_B = (2256, 2320)          # frame 101's mouth on the first boiler's south face
bfeat = [(CATWALK, dict(floor=CAT, color=Y_WAY))]
for b in BOILERS:
    bfeat.append((b, dict(floor=288, side="AJBOLT", ftex="AJTRIMF", color=STEELC)))
    bfeat.append(((b[0] + 32, b[1] - 32, b[2] - 32, b[1]), dict(floor=16, side="AJBRICK", color=0xB0A090)))  # its firing step
area(BOIL_BOX, bfeat, holes=[(FRAME_B[0], 4224, FRAME_B[1], 4288), (2048, 4352, 2080, 4480)],     # (the lobby's end)
     ceil=384, light=172, wall="AJBRICK", color=Y_ROOM, id=BOIL)
ajarmap.recess(m, (FRAME_B[0], 4224), (FRAME_B[1], 4224), (0, 1), G, F_BLUE, far_id(BLUE), color=Y_WAY, tag=BOIL)
ajarmap.recess(m, (2240, 4992), (2304, 4992), (0, 1), CAT, far_id(BLUE), F_BLUE, far_colour=BLUE, tag=BOIL)
ajarmap.door(m, BLUE, 3330, 3880, angle=180)
railing((2048, 4800), (3584, 4800))
ajarthird.hall(m, 2100, 3760, H_BOIL, 1, BOIL, BLOB)
ajarthird.lock(m, 2008, 4416, H_BOIL, BOUT, BIN, BLOB)
# the catwalk's way on (east, to the pump room) and the ash tunnel's mouth (east, on the floor): shutters the
# boiler house's win opens (it is won when nothing lives in it; the catwalk is shot at from the floor and through BLUE)
ajartime.shutter(m, (3584, 4960), (3584, 4832), (1, 0), CAT, CATSHUT, nomonsters=True, color=Y_WAY)
ajartime.shutter(m, (3584, 3968), (3584, 3840), (1, 0), G, ASHSHUT, nomonsters=True, color=Y_WAY)
MOUTHS.extend([((3584, 4960), (3584, 4832)), ((3584, 3968), (3584, 3840))])
ajarthird.win(m, 3560, 4896, H_BOIL, CATSHUT)
ajarthird.win(m, 3560, 3904, H_BOIL, ASHSHUT)
# the fight: imps and sergeants on the floor; hell knights, revenants, chaingunners on the catwalk
mon(3001, [(2160, 3900), (2600, 3800), (3000, 4000), (3420, 4100)], angle=180)
mon(9, [(2480, 4000), (2860, 3800), (3200, 3760)], angle=180)
mon(69, [(2400, 4900), (2900, 4880), (3400, 4900)], angle=270)
mon(66, [(2150, 4880), (2650, 4900), (3150, 4880)], angle=270)
mon(65, [(2280, 4860), (2520, 4860), (2780, 4860), (3030, 4860), (3280, 4860), (3500, 4860)], angle=270)
mon(69, [(2770, 4920)], angle=270, skill=4)
mon(3001, [(2300, 3760), (3100, 3880)], angle=180)
m.thing(2640, 3780, 2002, angle=90)                     # the chaingun
items(2048, (2700, 3780), (3480, 3780))
items(2012, (2100, 4100), (3500, 4600))
items(2049, (3480, 3840))
m.thing(3200, 4930, 82, angle=180)                      # the super shotgun, on the catwalk
items(2049, (3000, 4930))

# --- the ash tunnel (from the boiler house floor) and the cache at its end (the
# secret of part 1): frame 104 there takes BLUE back to the catwalk, a short cut ----
area((3600, 3840, 4352, 3968), [((3600, 3840, 4352, 3872), dict(ceil=80)), ((3600, 3936, 4352, 3968), dict(ceil=80))],
     ceil=104, light=112, color=Y_WAY, ftex="AJPIT")
mon(3002, [(3760, 3904), (4000, 3904)], angle=180)
mon(58, [(3880, 3904), (4120, 3904), (4260, 3904)], angle=180)
mon(3002, [(4200, 3904)], angle=180, skill=4)
items(2008, (3700, 3880), (3700, 3930))
CACHE = (4352, 3776, 4608, 4032)
m.sector(rect(*CACHE), ceil=128, light=160, color=Y_ROOM, special=1024)
ajarmap.recess(m, (4608, 3872), (4608, 3936), (1, 0), G, F_CACHE, far_id(BLUE), color=Y_WAY)
items(2013, (4480, 3904))
items(2049, (4420, 3820), (4420, 3990))
items(2048, (4550, 3820))

# --- the pump room, 128 up, from the catwalk -------------------------------------------
PUMP1 = (3600, 4352, 4608, 4992)
PUMPS1 = [(3776, 4480, 3904, 4608), (4160, 4480, 4288, 4608), (3776, 4736, 3904, 4864), (4160, 4736, 4288, 4864)]
area(PUMP1, [(ajarmap.octagon(*p, 40), dict(floor=CAT + 72, side="AJBOLT", color=STEELC)) for p in PUMPS1],
     floor=CAT, ceil=CAT + 192, light=176, color=Y_ROOM)
mon(3002, [(3700, 4420), (4040, 4680), (4480, 4900)], angle=180)
mon(58, [(3700, 4700), (4040, 4420), (4400, 4420), (4040, 4920)], angle=180)
mon(69, [(4480, 4560), (4480, 4440), (4380, 4700)], angle=180)
mon(3001, [(3700, 4920), (4560, 4800), (3980, 4560), (4100, 4380)], angle=180)
mon(69, [(4560, 4680)], angle=180, skill=4)
mon(3001, [(4300, 4920), (3700, 4560)], angle=180)
items(2049, (3680, 4900))
items(2048, (4580, 4380), (4580, 4440))
items(2012, (4000, 4920), (4000, 4400))
items(2018, (3660, 4380))
# the stairs down to the stack court
ajarmap.stairs(m, (4608, 4608), (4608, 4736), (1, 0), CAT, -CAT, steps=8, depth=32, ceil=CAT + 128, color=Y_WAY)

# --- the stack court, open, at the foot of the chimney ----------------------------------
# (after Vadim's first play: a rough ring round a round chimney; the imps' ledge one terrace curving
# round the north-east; banks on the west wall and across the south-east corner. The north-west and
# south-west corners stay square: the stairs' foot and the passage south are there)
STACK = (4864, 3584, 6144, 4864)
CHIMNEY = ngon(5504, 4224, 192, 16)
EARTH = dict(color=0x9C8468, ftex="AJPIT", side="AJBRICK")
SBANKS = [(bank(31, [(4864, 4480), (4864, 3872)], [(0, 0), (70, 170), (250, 300), (420, 250), (540, 150), (608, 0)],
                ground=G), (40, 88, 136)),
          (bank(32, [(5200, 3584), (6144, 3584), (6144, 3900)],
                [(0, 0), (80, 110), (450, 170), (750, 250), (944, 330), (1100, 250), (1210, 120), (1260, 0)], ground=G),
           (40, 88, 136)),
          (bank(33, [(6144, 3960), (6144, 4864), (5160, 4864)],                    # the imps' ledge, and banks behind it
                [(0, 0), (50, 120), (560, 124), (904, 330), (1250, 124), (1830, 120), (1888, 0)], ground=G,
                heights=(96, 144, 192), gaps=((100, 124), (48, 64))), (96, 144, 192))]
sfeat = [(t, dict(floor=G + h, **(dict(side="AJBRICK", ftex="AJTRIMF") if h == 96 else EARTH)))
         for b, hs in SBANKS for h, ts in zip(hs, b) for t in ts]
natural(STACK, sfeat, holes=[CHIMNEY], ceil=SKY, ctex="F_SKY1", light=204, wall="AJBRICK", color=Y_ROOM)
put(3003, [(5200, 4240), (5820, 4100)], G, angle=180)
put(64, [(5504, 3800)], G, angle=90, skill=3)               # the arch-vile, on the higher difficulties
LEDGE_IMPS = [(5250 + 110 * i, 4816) for i in range(7)] + [(6000, 4780), (6060, 4700)] + \
             [(6096, 4580 - 110 * i) for i in range(8)]                       # the ring of imps on the ledge
put(3001, LEDGE_IMPS[:9], G + 96, angle=270)
put(3001, LEDGE_IMPS[9:], G + 96, angle=180)
put(65, [(5000, 3700), (5800, 3860), (5100, 4600), (5880, 4560)], G, angle=90)
put(9, [(5150, 3800), (5750, 3780), (5250, 4500), (5750, 4500)], G, angle=90)
put(3003, [(5500, 4600)], G, angle=270, skill=4)
put(9, [(5450, 3700), (5300, 4700), (5700, 4700)], G, angle=90)
put(3004, [(5150, 4300), (5900, 4300)], G, angle=90)
m.thing(*spot(5504, 3940, 16, G, solid=False), 2003, angle=90)                     # the rocket launcher
items_on(G, 2046, (5380, 3940), (5620, 3940))
items_on(G, 2010, (5100, 4100), (5100, 4200), (5900, 4100), (5900, 4200))
items_on(G, 2049, (5850, 3760))
items_on(G, 2012, (4950, 3660), (5200, 3660))
items_on(G, 2048, (5900, 4600))
items_on(G, 2046, (5900, 3900))
items_on(G, 2008, (5150, 4000), (5150, 4060), (5850, 4000), (5850, 4060))
items_on(G, 2012, (5600, 4500), (5400, 4500))

# --- the gantry over R (128 over its floor, behind a railing), its shutter (R's win opens it), E1. The way to
# it from the stack court is the yard's terrace now (below, THE YARD): its west mouth is part 1's way on from
# the yard (WAY1), with a line no monster crosses behind it, as before --------------------------------------
put(3001, [(4960, 3700), (5080, 3660)], G, angle=270)          # (the two imps of the passage that was here)
GANTRY_BOX = (5056, 3264, 7040, 3392)
m.sector(rect(*GANTRY_BOX), floor=G, ceil=384, light=160, color=Y_WAY, id=GANTRY)
railing((5056, 3264), (7040, 3264))
no_monsters((5056, 3264), (5056, 3392))
ajartime.shutter(m, (7040, 3392), (7040, 3264), (1, 0), G, GSHUT, color=Y_WAY)
MOUTHS.append(((7040, 3392), (7040, 3264)))
m.line((7040, 3392), (7040, 3264), blockmonsters=True)
m.sector(rect(7056, 3264, 7424, 3392), ceil=128, light=176, color=Y_WAY)
# on to stand 1 over the last hall (below): north, then east along the hall's north side
m.sector(rect(7296, 3392, 7424, 3456), ceil=128, light=176, color=Y_WAY)
m.sector(rect(7296, 3456, 8192, 3584), ceil=128, light=176, color=Y_WAY)
# stand 1's supplies, before it (and before its save): a soulsphere, a blue armour, 2 boxes of rockets,
# 4 boxes of shells, a box of bullets
SUPPLY1 = [(2048, 7840, 3520), (2013, 7900, 3520), (2019, 7960, 3520), (2046, 8020, 3490), (2046, 8020, 3550),
           (2049, 8080, 3490), (2049, 8080, 3550), (2049, 8140, 3490), (2049, 8140, 3550)]

# =====================================================================================
# THE TURBINE HALL R: window hall 3 (part 2's fight), the future seen
# =====================================================================================
R_BOX = (5056, 2048, 7040, 3264)
CASINGS = [(5248, 2560, 5888, 2752), (6208, 2560, 6848, 2752)]       # the two turbines, 96 high
SPIDER_PIT = (5888, 2496, 6208, 2816)                                 # between them, 40 deep
CONDENSERS = [(5376, 2880, 5568, 3072), (6528, 2880, 6720, 3072)]    # 32 deep
BAYS = [(5376, 2048, 5472, 2144), (6016, 2048, 6112, 2144), (6624, 2048, 6720, 2144),     # south wall
        (6944, 2304, 7040, 2400), (6944, 2560, 7040, 2656), (6944, 3072, 7040, 3168)]     # east wall, 96 high
CASING_H, PIT_SPIDER, PIT_COND, BAY_H = 96, 40, 32, 96
rfeat = [(c, dict(floor=RF + CASING_H, side="AJBOLT", ftex="AJTRIMF", color=STEELC)) for c in CASINGS]
rfeat.append((SPIDER_PIT, dict(floor=RF - PIT_SPIDER, ftex="AJPIT", light=150)))
rfeat += [(c, dict(floor=RF - PIT_COND, ftex="AJPIT", light=150)) for c in CONDENSERS]
rfeat += [(b, dict(floor=RF + BAY_H, side="AJBRICK", ftex="AJTRIMF")) for b in BAYS]
area(R_BOX, rfeat, floor=RF, ceil=384, light=168, color=HALLC, id=RT)
for x1, y1, x2, y2 in [SPIDER_PIT] + CONDENSERS:              # the pits: railings nothing passes
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        railing(a, b)
for x1, y1, x2, y2 in CASINGS + BAYS:                         # the islands: no monster is thrown off them
    for a, b in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        if not (a[0] == b[0] == 7040 or a[1] == b[1] == 2048):     # (not along R's walls)
            m.line(a, b, blockmonsters=True)
ajarthird.hall(m, 5100, 2100, H_R, 2, RT, GANTRY)
ajarthird.watch(m, 5120, 3328, GANTRY, H_R, 1)
ajarthird.win(m, 7000, 3330, H_R, GSHUT)
ajarthird.win(m, 7000, 2880, H_R, STEEL)
# the posts: (kind, x, y, angle, the place it stands, skill)
MID = lambda b: ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)
POSTS = [(67, 5408, 2656, 90, CASINGS[0], 1), (67, 5728, 2656, 90, CASINGS[0], 2),
         (67, 6368, 2656, 90, CASINGS[1], 1), (67, 6688, 2656, 90, CASINGS[1], 3),
         (68, *MID(CONDENSERS[0]), 270, CONDENSERS[0], 1), (68, *MID(CONDENSERS[1]), 270, CONDENSERS[1], 2),
         (7, *MID(SPIDER_PIT), 90, SPIDER_PIT, 3),
         (66, *MID(BAYS[0]), 90, BAYS[0], 1), (65, *MID(BAYS[1]), 90, BAYS[1], 1), (66, *MID(BAYS[2]), 90, BAYS[2], 2),
         (65, *MID(BAYS[3]), 180, BAYS[3], 1), (66, *MID(BAYS[4]), 180, BAYS[4], 2), (65, *MID(BAYS[5]), 180, BAYS[5], 3),
         (71, 5300, 2300, 90, None, 1), (71, 6150, 3100, 270, None, 2), (71, 6560, 2300, 90, None, 3),
         (71, 5900, 2200, 90, None, 4)]
for kind, x, y, ang, place, sk in POSTS:
    m.thing(x, y, ajarthird.POST_T, angle=ang, args=(H_R, kind), skill=sk)
FLOOR_AT = {}


def neighbours():
    """Sector -> the sectors it shares a two-sided line with."""
    polys = m._split()
    edges = {}
    for i, p in enumerate(polys):
        for a, b in zip(p, p[1:] + p[:1]):
            edges[(a, b)] = i
    out = {}
    for (a, b), i in edges.items():
        j = edges.get((b, a))
        if j is not None:
            out.setdefault(i, set()).add(j)
    return out


NEAR = neighbours()
for kind, x, y, ang, place, sk in POSTS:
    if place is None:
        assert kind == 71                                                  # (it moves, and leaves no body)
        continue
    r = ajartime.RADIUS[kind]
    assert place[0] + r < x < place[2] - r and place[1] + r < y < place[3] - r, ("no room at the post", kind, x, y)
    s = sec_at(x, y)
    f = m.sectors[s]["floor"]
    FLOOR_AT[(x, y)] = f
    # the floor it can walk on from there (steps of 24 at most) is its island or its pit and nothing more:
    # every neighbour of it differs by more than 24
    island, todo = {s}, [s]
    while todo:
        for j in NEAR.get(todo.pop(), ()):
            if j not in island and abs(m.sectors[j]["floor"] - f) <= 24:
                island.add(j)
                todo.append(j)
    for i in island:
        xs = [p[0] for p in m.polys[i]]
        ys = [p[1] for p in m.polys[i]]
        assert place[0] <= min(xs) and max(xs) <= place[2] and place[1] <= min(ys) and max(ys) <= place[3], \
            ("a post's monster can walk off", kind, x, y)
        for j in NEAR.get(i, ()):
            assert j in island or abs(m.sectors[j]["floor"] - f) > 24
    if f > RF:
        assert f - RF >= 64                                             # a pedestal 64 high or more
    else:
        assert 32 <= RF - f <= 48                                       # a pit 32 deep or more,
        assert RF - f < ajartime.HEIGHT[kind] * 3 / 4                   # shallow enough that its eyes are over the rim
assert SPIDER_PIT[2] - SPIDER_PIT[0] >= 320 and SPIDER_PIT[3] - SPIDER_PIT[1] >= 320

# The sight from the gantry: R in pieces of (x1, y1, x2, y2, floor, ceil), the gantry over it
def tiles(box, feats, floor, ceil):
    xs = sorted({box[0], box[2]} | {v for r, _ in feats for v in (r[0], r[2])})
    ys = sorted({box[1], box[3]} | {v for r, _ in feats for v in (r[1], r[3])})
    out = []
    for x1, x2 in zip(xs, xs[1:]):
        for y1, y2 in zip(ys, ys[1:]):
            f = floor
            for r, ch in feats:
                if r[0] <= x1 and x2 <= r[2] and r[1] <= y1 and y2 <= r[3]:
                    f = ch["floor"]
            out.append((x1, y1, x2, y2, f, ceil))
    return out


R_SPACES = tiles(R_BOX, rfeat, RF, 384) + [GANTRY_BOX + (G, 384)]
SEEN_FROM = {}
for kind, x, y, ang, place, sk in POSTS:
    if place is None:
        continue
    body = (x, y, FLOOR_AT[(x, y)] + 8)
    eyes = [(gx, 3328, G + 41) for gx in range(5088, 7024, 32)]
    seen = [e for e in eyes if ajartime.seen(R_SPACES, e, body)]
    assert seen, ("a post not in sight from the gantry", kind, x, y)
    SEEN_FROM[(x, y)] = seen[len(seen) // 2]

# =====================================================================================
# PART 2, green: the machine side
# =====================================================================================
BOX2_BOX = (448, 2304, 704, 2544)
BOX2 = ajarthird.box(m, 2, rect(*BOX2_BOX), ceil=160, light=210, color=G_ROOM)
ajartime.glass(m, (480, 2560), (672, 2560), (0, -1), G)
ajarthird.box_door_at(m, 2, (544, 2304), (608, 2304), (0, -1), G, color=G_WAY)
opening((704, 2368), (704, 2496), (1, 0), G, G_WAY)
m.sector(rect(720, 2368, 1024, 2496), ceil=128, light=170, color=G_WAY)
m.sector(rect(896, 2496, 1024, 3504), ceil=128, light=170, color=G_WAY)
opening((896, 3504), (1024, 3504), (0, 1), G, G_WAY)
mon(3004, [(960, 2800), (960, 3200)], angle=270)
mon(3001, [(960, 3000), (960, 3400)], angle=270)
items(2008, (940, 2560), (980, 2560))
items(2011, (960, 2640))

# --- the gallery: windows onto the coal yard and the boiler house's floor --------------
GALLERY = (896, 3520, 3840, 3696)
area(GALLERY, [((896 + 192 * i, 3520, 896 + 192 * i + 64, 3552), dict(ceil=128)) for i in range(15)],
     ceil=160, light=176, color=G_ROOM)
for a, b in (((960, 3712), (1344, 3712)), ((1472, 3712), (1856, 3712)), ((2112, 3712), (2560, 3712))):
    ajartime.glass(m, a, b, (0, -1), G, top=128)
# its monsters are fallen things (ajarthird.fallen): go 1 sees the gallery through its windows as go 2 will
# have left it, a body at each (after Vadim's play of go 1: "this hallway I always pass as #2 earlier")


def gallery_mon(kind, pts, angle=0, skill=None):
    for x, y in pts:
        ajarthird.fallen(m, x, y, 2, kind, angle=angle, **({"skill": skill} if skill else {}))


gallery_mon(3001, [(3300, 3600), (3500, 3640), (3700, 3580)], angle=180)
gallery_mon(3004, [(3200, 3640), (3420, 3560), (3620, 3640)], angle=180)
gallery_mon(9, [(3560, 3600), (3760, 3640)], angle=180)
gallery_mon(9, [(3360, 3600)], angle=180, skill=4)
gallery_mon(3001, [(2400, 3600), (2600, 3640)], angle=180)
gallery_mon(9, [(2800, 3580)], angle=180)
gallery_mon(3004, [(3000, 3600), (1800, 3600)], angle=180)
items(2008, (1100, 3560), (1200, 3560), (2000, 3640), (2100, 3640))
items(2007, (1600, 3640), (2420, 3650))
items(2012, (2900, 3640))
items(2049, (1400, 3600))
items(2048, (2240, 3600))
# down, and back west along the workshop's north wall to its door
opening((3712, 3520), (3840, 3520), (0, -1), G, G_WAY)
m.sector(rect(3712, 3216, 3840, 3504), ceil=128, light=170, color=G_WAY)
m.sector(rect(2960, 3104, 3840, 3216), ceil=128, light=170, color=G_WAY)
mon(3001, [(3776, 3300), (3300, 3160)], angle=270)
mon(3004, [(3000, 3160)], angle=0)
# the workshop's lobby, the corridor's west end: the outer shutter across the corridor (worked from the lobby's
# side), the inner one in the workshop's door
ajartime.shutter(m, (2944, 3216), (2944, 3104), (1, 0), G, WOUT, color=G_WAY)
m.sector(rect(2752, 3104, 2944, 3216), ceil=128, light=170, color=G_WAY, id=WLOB)
ajartime.shutter(m, (2752, 3104), (2880, 3104), (0, -1), G, WIN_, thick=32, color=G_WAY)

# --- the workshop: window hall 2. VIOLET leans here; its far side is in the armoury
# behind bars (a plasma rifle, cells, armour for R) -------------------------------------
WORK_BOX = (2688, 2176, 3840, 3072)
BENCHES = [(2944, 2432, 3200, 2496), (3328, 2432, 3584, 2496), (2944, 2752, 3200, 2816), (3328, 2752, 3584, 2816)]
LATHES = [(3072, 2560, 3200, 2688), (3456, 2560, 3584, 2688)]
wfeat = [(b, dict(floor=40, side="AJWOOD", ftex="AJTRIMF")) for b in BENCHES]
wfeat += [(b, dict(floor=72, side="AJBOLT", color=STEELC)) for b in LATHES]
area(WORK_BOX, wfeat, ceil=256, light=184, color=G_ROOM, id=WORK)
ajarthird.hall(m, 2740, 3020, H_WORK, 2, WORK, WLOB)
ajarthird.lock(m, 2848, 3160, H_WORK, WOUT, WIN_, WLOB)
ARMOURY = (2368, 2240, 2688, 2496)
m.sector(rect(*ARMOURY), ceil=160, light=200, color=G_ROOM, id=WORK)
m.line((2688, 2240), (2688, 2496), **BARS)
ajarmap.recess(m, (2688, 2752), (2688, 2816), (-1, 0), G, F_VIOLET, far_id(VIOLET), color=G_WAY, tag=WORK)
ajarmap.recess(m, (2368, 2336), (2368, 2400), (-1, 0), G, far_id(VIOLET), F_VIOLET, far_colour=VIOLET, tag=WORK)
ajarmap.door(m, VIOLET, 3700, 2280, angle=180)
m.thing(2560, 2368, 2004, angle=0)                      # the plasma rifle
items(17, (2460, 2290), (2460, 2440))
items(2019, (2600, 2300))
# the fight
mon(65, [(2800, 2300), (2800, 2960), (3760, 2700), (3300, 2960), (3000, 2240), (3700, 2960)], angle=90)
mon(3002, [(3010, 2620), (3300, 2620), (3400, 2340), (2900, 2620), (3640, 2400), (3250, 2880)], angle=90)
mon(66, [(3000, 2950), (3500, 2940), (2780, 2620), (3740, 2560)], angle=270)
m.thing(3270, 2300, 67, angle=90)                        # a mancubus
mon(3001, [(2780, 2440), (2880, 2860), (3420, 2860), (3740, 2860), (3140, 2900), (3540, 2300)], angle=90)
mon(9, [(3000, 2340), (3200, 2340), (3400, 2620), (3640, 2640)], angle=90)
mon(66, [(2900, 2340)], angle=90, skill=4)
mon(3001, [(3150, 2380), (3400, 2200)], angle=90)
mon(3002, [(2940, 3020), (3160, 3020)], angle=270)
mon(9, [(3460, 3020), (3720, 2440)], angle=270)
items(2049, (2760, 3020), (3620, 3020))
items(2048, (2760, 2200), (3800, 2200))
items(2046, (3260, 2560))
items(2012, (3800, 3020), (2760, 2700))
items(2049, (3100, 2240))
items(2047, (3400, 2240), (3440, 2240))
items(2011, (3700, 2600), (3700, 2650))
# to the yard: a shutter the workshop's win opens, and a short corridor to the head of the yard's west stairs
ajartime.shutter(m, (3840, 2944), (3840, 2816), (1, 0), G, PUMPSHUT, nomonsters=True, color=G_WAY)
MOUTHS.append(((3840, 2944), (3840, 2816)))
ajarthird.win(m, 3820, 2880, H_WORK, PUMPSHUT)
m.sector(rect(3856, 2816, 3968, 2944), ceil=128, light=170, color=G_WAY)

# =====================================================================================
# THE YARD: the common place in the middle (common.zs; PLAN.md "MAP33: the yard in the middle, on three
# levels, as decided" and "... built"). Open to the sky, where part 2's pump hall and stores were. Part 2 crosses
# its floor (-128: in from the workshop's corridor down stairs on the west, out up stairs on the east into the
# mezzanine's corridor); part 1 comes from the stack court onto the terrace at its north-east corner and the
# ledge along its north rim (0), on to the gantry by its west mouth; part 3 comes from the tower's passage onto
# the corner piece at its south-east corner and the ledge along its south rim (-64), back to the stairs down
# into the duct. The three never meet on foot: rims (ajarthird.rim, players only) between the levels; shots,
# sight and flyers pass. Each part's group comes the first time its go stands on its level (the levels' sectors
# carry 3390 + k and nothing else: the place's own sectors, YPLACE, are the stairs, the entries, the pumps, the
# pipes, the banks and the shed); its way on (WAYk, a shutter closed to monsters) opens once the group is dead.
# Every other way out of the place blocks monsters (asserted, ajarthird.sealed).
# =====================================================================================
YPLACE = 3388                                           # the place's own sectors (no part's level)
L1, L2, L3 = (ajarthird.level_tag(k) for k in (1, 2, 3))     # the north ledge and the terrace; the floor; the south ledge and the corner
WAY1, WAY2, WAY3 = 3383, 3384, 3385                     # each part's way on from its level
YX1, YX2, YY1, YY2 = 3968, 4736, 2240, 3456             # the floor's box, between the ledges
FLOOR2 = RF                                             # the floor: part 2's level, the turbine hall's height
SOUTH3 = -64                                            # the south ledge: part 3's level, the tower's passage's height (TF)
YCOL = 0xD4D8CC                                         # the floor
EARTHY = dict(color=0x9C8C74, ftex="AJPIT", side="AJBRICK")
PIPE = dict(side="AJBOLT", ftex="AJTRIMF", color=STEELC)
YSKY = dict(ceil=SKY, ctex="F_SKY1")

# --- the north side, part 1's level (0, 128 over the floor): the terrace at the north-east corner, where the
# passage from the stack court to the gantry was, entered from the stack court by a doorway; its first 112 are
# the place's own (the entry), so that the group comes when the player is well onto it. The ledge along the
# north rim west from it, a dead end with a cache --------------------------------------------------------------
TERRACE = (4736, 3152, 5040, 3568)
T_ENTRY = (4736, 3456, 5040, 3568)
YLEDGE1 = (YX1, YY2, YX2, 3584)
T_DOOR = (4912, 5040)                                   # the doorway from the stack court (its south wall, y 3584)
opening((T_DOOR[0], 3584), (T_DOOR[1], 3584), (0, -1), G, Y_WAY)
m.line((T_DOOR[0], 3568), (T_DOOR[1], 3568), blockmonsters=True)     # (out of the place: no monster crosses)
TERR_SECS = [m.sector(rect(*T_ENTRY), light=206, color=Y_ROOM, wall="AJBRICK", id=YPLACE, **YSKY),
             m.sector(rect(TERRACE[0], TERRACE[1], TERRACE[2], T_ENTRY[1]), light=206, color=Y_ROOM, wall="AJBRICK", id=L1, **YSKY)]
LEDGE1_SEC = m.sector(rect(*YLEDGE1), light=206, color=Y_ROOM, wall="AJBRICK", id=L1, **YSKY)
# part 1's way on: a shutter at the gantry's west mouth (the line no monster of R crosses stays behind it)
ajartime.shutter(m, (5040, 3392), (5040, 3264), (1, 0), G, WAY1, nomonsters=True, color=Y_WAY)
ajarthird.way(m, 5010, 3330, 1, WAY1)
# the cache at the ledge's west end: 2 boxes of rockets, a box of shells, a medikit
items(2046, (4000, 3500), (4000, 3550))
items(2049, (4050, 3525))
items(2012, (4100, 3525))

# --- the south side, part 3's level (-64, 64 over the floor): the tower's passage goes on north to the corner
# piece (its first 64 the place's own: the group comes past the duct stairs' shutter), and from it the ledge
# along the south rim, west to a dead end with a cache --------------------------------------------------------
CORNER = (4736, 1984, 4864, 2240)
C_ENTRY = (4736, 1984, 4864, 2048)
YLEDGE3 = (YX1, 2112, YX2, YY1)
m.line((4736, 1984), (4864, 1984), blockmonsters=True)               # (out of the place: no monster crosses)
CORNER_SECS = [m.sector(rect(*C_ENTRY), floor=SOUTH3, light=200, color=R_ROOM, wall="AJBRICK", id=YPLACE, **YSKY),
               m.sector(rect(CORNER[0], C_ENTRY[3], CORNER[2], CORNER[3]), floor=SOUTH3, light=200, color=R_ROOM,
                        wall="AJBRICK", id=L3, **YSKY)]
LEDGE3_SEC = m.sector(rect(*YLEDGE3), floor=SOUTH3, light=200, color=R_ROOM, wall="AJBRICK", id=L3, **YSKY)
items(17, (4000, 2150), (4000, 2200))
items(2046, (4050, 2175))
items(2012, (4100, 2175))

# --- the floor, part 2's level: in by stairs from the workshop's corridor (west), out by stairs to the
# mezzanine's corridor (east, its way on there); four pumps (80 high) and two pipe runs as cover, banks along
# the west and the east walls, the pump shed in the west wall (the secret of part 2: the clerk's nook's) ----------
W_STAIRS = (3968, 2816, 4224, 2944)                     # down from the corridor (G) to the floor, eastwards
E_STAIRS = (4480, 2304, 4736, 2432)                     # up from the floor to the mezzanine's corridor (G), eastwards
ajarmap.stairs(m, (3968, 2816), (3968, 2944), (1, 0), G, FLOOR2 - G, steps=8, depth=32, light=200, color=G_WAY,
               wall="AJBRICK", id=YPLACE, **YSKY)
m.line((3968, 2816), (3968, 2944), blockmonsters=True)               # (out of the place: no monster crosses)
ajarmap.stairs(m, (4480, 2304), (4480, 2432), (1, 0), FLOOR2, G - FLOOR2, steps=8, depth=32, light=200, color=G_WAY,
               wall="AJBRICK", id=YPLACE, **YSKY)
# part 2's way on: a shutter at the head of the east stairs, where the stores' doorway was
ajartime.shutter(m, (4736, 2432), (4736, 2304), (1, 0), G, WAY2, nomonsters=True, color=G_WAY)
ajarthird.way(m, 4700, 2368, 2, WAY2)
# the pump shed: a room in the west wall, 128 x 176 and 96 high, entered from the floor by a doorway 64 wide
SHED_NOTCH = (3968, 2400, 4112, 2608)                   # what the shed and its walls take out of the floor
SHED = (3968, 2416, 4096, 2592)
SHED_DOOR = (4096, 2480, 4112, 2544)
SHED_SECS = [m.sector(rect(*SHED), floor=FLOOR2, ceil=FLOOR2 + 96, light=144, color=0xC8C0B0, wall="AJWOOD",
                      ftex="AJTRIMF", special=1024, id=YPLACE),
             m.sector(rect(*SHED_DOOR), floor=FLOOR2, ceil=FLOOR2 + 80, light=170, color=G_WAY, wall="AJTRIM",
                      ftex="AJTRIMF", id=YPLACE)]
items(2046, (4000, 2450), (4000, 2560))                 # what the clerk's nook had: 2 boxes of rockets, a blue armour
items(2019, (4050, 2505))
FLOOR_OUT = [(YX1, YY1), (YX2, YY1), (YX2, E_STAIRS[1]), (E_STAIRS[0], E_STAIRS[1]), (E_STAIRS[0], E_STAIRS[3]),
             (YX2, E_STAIRS[3]), (YX2, YY2), (YX1, YY2), (YX1, W_STAIRS[3]), (W_STAIRS[2], W_STAIRS[3]),
             (W_STAIRS[2], W_STAIRS[1]), (YX1, W_STAIRS[1]), (YX1, SHED_NOTCH[3]), (SHED_NOTCH[2], SHED_NOTCH[3]),
             (SHED_NOTCH[2], SHED_NOTCH[1]), (YX1, SHED_NOTCH[1])]
PUMPS3 = [(4224, 3136, 4352, 3264), (4416, 2976, 4544, 3104), (4224, 2400, 4352, 2528), (4352, 2688, 4480, 2816)]
PIPES = [(4416, 3264, 4608, 3296), (4544, 2592, 4576, 2848)]
PUMP_H, PIPE_H = 80, 48
yfeat2 = [(ajarmap.octagon(*p, 40), dict(floor=FLOOR2 + PUMP_H, id=YPLACE, **PIPE)) for p in PUMPS3]
yfeat2 += [(p, dict(floor=FLOOR2 + PIPE_H, id=YPLACE, **PIPE)) for p in PIPES]
YBANKS2 = [bank(71, [(YX1, YY2 - 64), (YX1, 3024)],                      # the west wall, north of the stairs (64 off the
                [(0, 0), (60, 110), (160, 150), (260, 120), (320, 90), (368, 0)], ground=FLOOR2, heights=(40, 88),   # ledge's face: a pocket)
                gaps=((40, 64),)),
           bank(72, [(YX2, 2512), (YX2, 3072)],                           # the east wall, between the stairs and the terrace
                [(0, 0), (60, 80), (200, 96), (360, 70), (480, 90), (560, 0)], ground=FLOOR2, heights=(40, 88),
                gaps=((30, 40),), avoid=PIPES)]
yfeat2 += [(t, dict(floor=FLOOR2 + h, id=YPLACE, **EARTHY)) for b in YBANKS2 for h, ts in zip((40, 88), b) for t in ts]
FLOOR_SECS = natural(FLOOR_OUT, yfeat2, floor=FLOOR2, light=206, wall="AJBRICK", color=YCOL, id=L2, **YSKY)
# the rims: the north ledge's and the terrace's fronts, the south ledge's (the corner piece is walled to the north)
ajarthird.rim(m, (YX1, YY2), (YX2, YY2))
ajarthird.rim(m, (YX2, TERRACE[1]), (YX2, YY2))
ajarthird.rim(m, (YX1, YY1), (YX2, YY1))
ajarthird.common(m, 4300, 2950, YPLACE)


def stands_on(x, y, r, floor, tag):
    """stands(), and every point looked at in a sector with `tag`."""
    for dx in (-r, -r / 2, 0, r / 2, r):
        for dy in (-r, -r / 2, 0, r / 2, r):
            s = sec_at(x + dx, y + dy)
            if s is None or m.sectors[s]["floor"] != floor or m.sectors[s]["id"] != tag:
                return False
    return True


def sees(p, q, step=8):
    """Is q (x, y, z) seen from p through the sectors (each piece of the line in a sector, between its floor and
    its ceiling)? Rims and lines that only stop players do not block sight."""
    n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) // step))
    for i in range(1, n):
        t = i / n
        x, y, z = (p[k] + (q[k] - p[k]) * t for k in range(3))
        s = sec_at(x, y)
        if s is None or not m.sectors[s]["floor"] < z < m.sectors[s]["ceil"]:
            return False
    return True


def foot_dist(p, stairs, west):
    """How far p is from the foot of a flight (its edge on the floor's side)."""
    fx = stairs[2] if west else stairs[0]
    return _dist_seg(p, (fx, stairs[1]), (fx, stairs[3]))


# Where the bodies are looked at from: the terrace, the north ledge and the south ledge (a player's eyes, 41 up)
YEYES = {"the terrace": [(x, y, G + 41) for x in (4760, 4840, 4920) for y in (3180, 3280, 3380)],
         "the north ledge": [(x, 3476, G + 41) for x in range(4000, 4736, 96)],
         "the south ledge": [(x, 2220, SOUTH3 + 41) for x in range(4000, 4736, 96)] + [(4720, 2160, SOUTH3 + 41)]}


def seen_from(x, y, z):
    return [k for k, es in YEYES.items() if any(sees(e, (x, y, z)) for e in es)]


def fly_spot(x, y, r):
    """A flyer's place nearest x, y (8 apart): over the floor's level with room round it (as a walker's), clear
    of every thing put before (Doom's boxes, as spot())."""
    for d in range(0, 257, 8):
        ring = [(x, y)] if d == 0 else sorted({(x + i, y + j) for i in range(-d, d + 1, 8) for j in (-d, d)}
                                              | {(x + i, y + j) for j in range(-d, d + 1, 8) for i in (-d, d)},
                                              key=lambda p: ((p[0] - x) ** 2 + (p[1] - y) ** 2, p))
        for px, py in ring:
            if stands_on(px, py, r + 8, FLOOR2, L2) and all(max(abs(px - qx), abs(py - qy)) >= r + qr + 8 for qx, qy, qr in PLACED):
                PLACED.append((px, py, r))
                return px, py
    raise AssertionError(("no room for a flyer near", x, y))


# --- the groups (ajarthird.comer: thinned on the easier skills as their monsters are) ----------------------------
# Part 2's, on the floor: what the pump hall and the stores had, in the same order (so that the rest of the map is
# thinned as before), and a fifth cacodemon (skill 3 up): every walker seen fallen in go 1, at places spread over
# the floor's free ground that are seen from at least two of the terrace and the ledges, none within 256 of the
# foot of the west stairs (where go 2 comes down) nor 96 of the east stairs' (its way out)
W_FOOT = ((W_STAIRS[2] + 0.0, W_STAIRS[1] + 0.0), (W_STAIRS[2] + 0.0, W_STAIRS[3] + 0.0))
cands = []
for cy in range(YY1 + 48, YY2 - 47, 32):
    for cx in range(YX1 + 48, YX2 - 47, 32):
        if foot_dist((cx, cy), W_STAIRS, True) < 256 + 32 or foot_dist((cx, cy), E_STAIRS, False) < 96 + 32:
            continue
        if stands_on(cx, cy, 40, FLOOR2, L2) and len(seen_from(cx, cy, FLOOR2 + 8)) >= 2:
            cands.append((cx, cy))
SEQ2 = [(3005, None)] * 4 + [(69, None)] * 3 + [(3001, None)] * 4 + [(3002, None)] * 2 + [(65, None)] * 2 + \
       [(3005, 4)] + [(58, None)] * 2 + [(3004, None)] * 2 + [(9, None)] * 2 + \
       [(58, None)] * 4 + [(3001, None)] * 3 + [(69, None)] * 3 + [(3002, None)] + [(58, 4)] + [(3004, None)] * 2 + \
       [(9, None)] * 2 + [(3001, None)] + [(3005, 3)]          # (the old order; the last, the fifth cacodemon, is new)
WALKERS2 = sum(1 for k, sk in SEQ2 if k != 3005)
# spread: each next place the candidate farthest from those taken
chosen = [min(cands, key=lambda p: (abs(p[0] - 4352) + abs(p[1] - 2848), p))]
while len(chosen) < WALKERS2:
    chosen.append(max(cands, key=lambda p: (min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in chosen), -p[0], -p[1])))
PLACED.extend((x, y, 32) for x, y in chosen)
CACO2 = [(4160, 3000, 160), (4560, 2860, 200), (4300, 2560, 180), (4620, 2520, 240), (4440, 2440, 200), (4180, 2720, 220)]
# (kind, x, y, angle, z over the floor, part, seen fallen, skill); the walkers face the middle of the floor
GROUPS = []
wk, ck = iter(chosen), iter(CACO2)
for kind, sk in SEQ2:
    if kind == 3005:
        x, y, z = next(ck)
        GROUPS.append((3005, *fly_spot(x, y, 31), 180, z, 2, False, sk))
    else:
        x, y = next(wk)
        GROUPS.append((kind, x, y, round(math.degrees(math.atan2(2848 - y, 4352 - x))) % 360, 0, 2, True, sk))
# part 1's: 5 cacodemons and a pain elemental over the middle of the floor, 96 to 200 over the terrace's level
# (skill 1: 3 cacodemons; skill 2: 4 and the pain elemental)
for x, y, z, sk in ((4400, 3000, 96, 1), (4250, 2900, 150, 1), (4520, 2800, 200, 1), (4180, 3150, 120, 2),
                    (4600, 3120, 180, 3)):
    GROUPS.append((3005, *fly_spot(x, y, 31), 0, z - FLOOR2, 1, False, sk))
GROUPS.append((71, *fly_spot(4380, 2860, 31), 0, 160 - FLOOR2, 1, False, 2))
# part 3's: 4 cacodemons and 2 pain elementals over the middle of the floor, 96 to 200 over the corner's level
# (skill 1: 2 cacodemons and one pain elemental; skill 4: a third pain elemental)
for x, y, z, sk in ((4300, 2650, 96, 1), (4500, 2700, 150, 1), (4220, 2640, 200, 2), (4420, 2500, 120, 3)):
    GROUPS.append((3005, *fly_spot(x, y, 31), 90, z + SOUTH3 - FLOOR2, 3, False, sk))
for x, y, z, sk in ((4250, 2750, 160, 1), (4500, 2560, 190, 3), (4350, 2420, 140, 4)):
    GROUPS.append((71, *fly_spot(x, y, 31), 90, z + SOUTH3 - FLOOR2, 3, False, sk))
for kind, x, y, a, z, part, f, sk in GROUPS:
    ajarthird.comer(m, x, y, part, kind, a, z, fallen=f, skill=sk)
# supplies: what the pump hall and the stores gave, on the floor and in the mezzanine's corridor (the soulsphere
# before the drop stays before it)
items_on(FLOOR2, 2046, (4040, 2300), (4100, 2300), (4660, 3360), (4500, 3400))
items_on(FLOOR2, 2047, (4680, 2280), (4620, 2280), (4060, 2880 + 200))
items_on(FLOOR2, 2012, (4300, 2340), (4400, 3400), (4680, 2470))
items_on(FLOOR2, 2049, (4050, 2240 + 40), (4600, 3200), (4300, 3400), (4060, 3000))
items_on(FLOOR2, 17, (4380, 2620), (4560, 2420))
items_on(FLOOR2, 2048, (4200, 3380))
items_on(FLOOR2, 2047, (4660, 2960))

# --- the mezzanine's corridor, the mezzanine: R's west side ---------------------------------------------------
m.sector(rect(4752, 2304, 4864, 2432), ceil=128, light=170, color=G_WAY)
items(2013, (4800, 2400))                                # a soulsphere before the drop
items(2012, (4800, 2330))
MEZZ = (4864, 2304, 5056, 3136)
m.sector(rect(*MEZZ), ceil=384, light=168, color=G_WAY)
no_monsters((5056, 2304), (5056, 3136))                  # the drop into R: no monster of R comes up it (lost souls)
mon(3001, [(4960, 3060), (4960, 2380), (4960, 2600), (4960, 2800), (4960, 2960)], angle=0)
items(2046, (4900, 2480))

# --- the steel door (R's win), the stairs up, E2 -----------------------------------------
ajartime.shutter(m, (7040, 2944), (7040, 2816), (1, 0), RF, STEEL, nomonsters=True, color=G_WAY)
MOUTHS.append(((7040, 2944), (7040, 2816)))
ajarmap.stairs(m, (7056, 2816), (7056, 2944), (1, 0), RF, -RF, steps=8, depth=32, ceil=G + 128, color=G_WAY)
# the passage on to stand 2 over the last hall (below), from the west
m.sector(rect(7312, 2816, 7616, 2944), ceil=128, light=176, color=G_WAY)
# stand 2's supplies, before it: a soulsphere, a blue armour, 2 cell packs, 2 boxes of rockets
SUPPLY2 = [(2013, 7400, 2850), (2019, 7400, 2910), (17, 7470, 2850), (17, 7470, 2910), (2046, 7540, 2850),
           (2046, 7540, 2910)]

# =====================================================================================
# PART 3, red: the cable side
# =====================================================================================
BOX3_BOX = (64, 2304, 320, 2544)
BOX3 = ajarthird.box(m, 3, rect(*BOX3_BOX), ceil=160, light=210, color=R_ROOM)
ajartime.glass(m, (96, 2560), (288, 2560), (0, -1), G)
ajarthird.box_door_at(m, 3, (64, 2432), (64, 2368), (-1, 0), G, color=R_WAY)
opening((256, 2304), (128, 2304), (0, -1), G, R_WAY)
# a berserk pack by the east wall, opposite the box's door: go 3 may begin with nothing left of go 2 (Vadim came
# with 1 of health and his fists, the tunnel's spectres at the opening). Off the tests' way (route 15, x 192).
items(2023, (272, 2400))
# --- the cable tunnel: low and dark, trays of cable along its walls ----------------------
TUN = [(128, 1984, 256, 2288), (256, 1984, 1280, 2112)]
area(TUN[0], [((128, 1984, 152, 2288), dict(ceil=72)), ((232, 1984, 256, 2288), dict(ceil=72))],
     ceil=96, light=112, color=R_WAY, ftex="AJPIT")
area(TUN[1], [((256, 1984, 1280, 2008), dict(ceil=72)), ((256, 2088, 1280, 2112), dict(ceil=72))],
     ceil=96, light=112, color=R_WAY, ftex="AJPIT")
mon(58, [(192, 2100), (500, 2048), (760, 2048), (1000, 2048), (1170, 2030), (640, 2060)], angle=180)
mon(3001, [(420, 2048), (880, 2048), (1100, 2048), (1240, 2040)], angle=180)
mon(3001, [(330, 2048), (560, 2048)], angle=180, skill=4)
mon(58, [(820, 2075), (930, 2075)], angle=180)                  # (part 3, longer: two more spectres,
mon(69, [(1225, 2085)], angle=180)                              # and a hell knight at the east end)
items(2008, (192, 2250), (192, 2220), (300, 2048), (340, 2048))
items(2011, (700, 2048))
items(2049, (380, 2030))

# --- the switchyard, open: transformers in rows, gantries along its south wall ----------
SW = (1280, 896, 2816, 2112)
TRANS = [(x, y, x + 128, y + 192) for x in (1536, 1920, 2304) for y in (1088, 1440)] + \
        [(1920, 1792, 2048, 1984), (2304, 1792, 2432, 1984)]
SWG = [(1344, 896, 2688, 992)]                         # a gantry for the imps, 160 up
sfeat = [(t, dict(floor=112, side="AJBOLT", ftex="AJTRIMF", color=0x8C94A0)) for t in TRANS]
sfeat += [((t[0] - 16, t[1] - 16, t[2] + 16, t[3] + 16), dict(floor=8, color=0xA0A0A0)) for t in TRANS]
sfeat = [f for pair in zip(sfeat[len(TRANS):], sfeat[:len(TRANS)]) for f in pair]     # (plinth, then transformer on it)
sfeat += [(g, dict(floor=160, side="AJBOLT", ftex="AJTRIMF")) for g in SWG]
# (after Vadim's first play: gravel banked unevenly along the north wall, the west wall and the east
# wall's north end, clear of the tunnel's mouth, PINK and its frame, the relay shutter and the hut)
GRAVEL = dict(color=0xA4A49C, ftex="AJPIT", side="AJWALL")
PLINTHS = [(t[0] - 16, t[1] - 16, t[2] + 16, t[3] + 16) for t in TRANS]
WBANKS = [bank(41, [(2560, 2112), (1560, 2112)], [(0, 0), (60, 150), (110, 80), (270, 80), (310, 210), (400, 250), (450, 210),
                                                    (500, 80), (650, 80), (700, 200), (800, 280), (930, 220), (1000, 0)],
               ground=G, avoid=PLINTHS),
          bank(42, [(1280, 1770), (1280, 1120)], [(0, 0), (80, 120), (250, 200), (400, 150), (560, 190), (650, 0)], ground=G,
               avoid=PLINTHS),
          bank(43, [(2816, 1590), (2816, 1860)], [(0, 0), (60, 140), (150, 170), (220, 110), (270, 0)], ground=G, avoid=PLINTHS)]
sfeat += [(t, dict(floor=G + h, **GRAVEL)) for b in WBANKS for h, ts in zip((40, 88, 136), b) for t in ts]
natural(SW, sfeat, ceil=SKY, ctex="F_SKY1", light=200, wall="AJBRICK", color=R_ROOM)
ajarmap.door(m, PINK, 1400, 1860, angle=0)
ajarmap.recess(m, (2816, 1408), (2816, 1472), (1, 0), G, F_PINK, far_id(PINK), color=R_WAY)
# the relay room's shutter, which does not open
m.sector(rect(2816, 1984, 2928, 2112), ceil=128, light=150, color=R_WAY)
ajartime.shutter(m, (2928, 2112), (2928, 1984), (1, 0), G, RELAYSHUT, color=R_WAY)
mon(3001, [(1400 + 96 * i, 944) for i in range(0, 13, 2)], angle=90)                   # imps on the gantry
mon(3001, [(1496 + 192 * i, 944) for i in range(3)], angle=90, skill=4)
PLACED.extend((1400 + 96 * i, 944, 20) for i in range(13))
put(68, [(2650, 1200), (2560, 1720), (2200, 1680)], G, angle=180)
put(3005, [(2500, 1300), (2600, 1900), (2100, 1300), (2200, 1560), (2560, 1560), (2400, 1050)], G, angle=180)
put(3004, [(1700, 1300), (1800, 1700), (1750, 1850), (1450, 1600)], G, angle=0)
put(9, [(1700, 1100), (1840, 1500), (2160, 1800), (1450, 1300), (2150, 1150), (1700, 1760)], G, angle=0)
put(67, [(1792, 1180), (2176, 1360)], G, angle=180)                                    # (part 3, longer: two mancubi
mon(66, [(2072, 944), (2456, 944)], angle=90)                                          # and two revenants on the gantry)
items_on(G, 2046, (1360, 2060), (1360, 2000))
items_on(G, 2049, (1760, 1400), (2160, 1700))
items_on(G, 2048, (1760, 1600))
items_on(G, 2012, (1440, 1100), (2700, 1340))
items_on(G, 2047, (2700, 1560), (2620, 1620))
# the hut by the switchyard's south-east corner: the secret of part 3
opening((2816, 1024), (2816, 960), (1, 0), G, R_ROOM, ceil=72)
m.sector(rect(2832, 928, 2960, 1056), ceil=96, light=140, color=R_ROOM, special=1024)
items(8, (2896, 990))
items(2046, (2930, 1030))
items(2012, (2860, 1030))

# --- the relay room: PINK's far side; a window onto the workshop; the doorway south to the pond ---
RELAY = (2944, 1792, 3584, 2160)
CABINETS = [(3072, 1792, 3328, 1840)]
area(RELAY, [(c, dict(floor=96, side="AJBOLT", ftex="AJTRIMF", color=STEELC)) for c in CABINETS],
     ceil=192, light=168, color=R_ROOM)
ajarmap.recess(m, (2944, 1856), (2944, 1920), (-1, 0), G, far_id(PINK), F_PINK, far_colour=PINK)
ajartime.glass(m, (3008, 2176), (3520, 2176), (0, -1), G)          # onto the workshop (from its side)
mon(3001, [(3300, 1950), (3500, 2080)], angle=180)
mon(9, [(3100, 2080), (3500, 1900)], angle=180)
mon(65, [(3200, 2000), (3400, 1960)], angle=270)
items(2049, (3540, 1880))
items(2012, (3000, 2100))
items(2046, (3380, 2110))

# =====================================================================================
# PART 3, longer (after Vadim's first play): the cooling pond, the cooling tower
# =====================================================================================
# --- the cooling pond, out of doors: shallow water in the middle, banks all round, three
# islands; a dry path round its west and south, the short way through the water ------------
POND = (3040, 320, 4416, 1728)
PG, PW = -24, -44                   # the dry ground (the banks' foot), the water (20 under it)
ISLE = PW + 40                      # the islands, 40 over the water
LEDGE3 = PG + 96                    # the ledge along the south bank
opening((3424, 1792), (3552, 1792), (0, -1), G, R_WAY)
ajarmap.stairs(m, (3424, 1776), (3552, 1776), (0, -1), G, PG - G, steps=3, depth=16, ceil=G + 128, color=R_WAY)
POND_WATER = [(round(3770 + r * math.cos(math.radians(a))), round(1010 + r * math.sin(math.radians(a))))
              for a, r in ((0, 500), (20, 470), (40, 430), (60, 400), (80, 415), (100, 450), (120, 540), (140, 470),
                           (160, 380), (180, 350), (200, 370), (220, 430), (240, 400), (260, 370), (280, 360), (300, 400),
                           (320, 440), (340, 480))]
ISLANDS = [blob(random.Random(51), 3620, 1000, 112, 102, 7), blob(random.Random(52), 3990, 860, 108, 100, 8),
           blob(random.Random(53), 3900, 1200, 104, 108, 6)]
for isl in ISLANDS:
    assert margin(isl, POND_WATER) >= 60, ("an island too near the water's edge", isl[0])
assert min(max(p[0] for p in i) - min(p[0] for p in i) for i in ISLANDS) >= 160
MUD = dict(color=0x8C8C70, ftex="AJPIT", side="AJBRICK")
PBANKS = [(bank(61, [(3300, 1728), (3040, 1728), (3040, 1560)], [(0, 0), (60, 100), (260, 240), (380, 120), (428, 0)],
                ground=PG), (40, 88, 136)),
          (bank(62, [(3040, 1490), (3040, 744)], [(0, 0), (90, 160), (315, 230), (539, 150), (683, 180), (746, 0)],     # (64 or more
                # from the banks beside it along the wall: 30 and 20 were pockets, 2026-11-24)
                ground=PG), (40, 88, 136)),
          (bank(63, [(3040, 680), (3040, 320), (4416, 320), (4416, 720)],          # the south bank: its foot a ledge
                [(0, 0), (80, 150), (360, 300), (560, 170), (900, 140), (1300, 160), (1600, 150), (1736, 330), (1950, 200),
                 (2080, 120), (2136, 0)], ground=PG, heights=(96, 144, 192), gaps=((100, 124), (48, 64))), (96, 144, 192)),
          (bank(64, [(4416, 1200), (4416, 1728), (3660, 1728)],
                [(0, 0), (80, 140), (400, 230), (528, 320), (700, 240), (1000, 180), (1200, 140), (1284, 0)],
                ground=PG), (40, 88, 136))]
pfeat = [(t, dict(floor=PG + h, **(dict(side="AJBRICK", ftex="AJTRIMF", color=0xB0A898) if h == 96 else MUD)))
         for b, hs in PBANKS for h, ts in zip(hs, b) for t in ts]
pfeat.append((POND_WATER, dict(floor=PW, ftex="FWATER1", side="AJBRICK", color=None, light=190)))
pfeat += [(isl, dict(floor=ISLE, **MUD)) for isl in ISLANDS]
natural(POND, pfeat, floor=PG, ceil=SKY, ctex="F_SKY1", light=204, wall="AJBRICK", color=R_ROOM)
# the outfall: a channel east, 16 over the dry ground, and a drop of 56 into the tower
CHANNEL = (4416, 960, 4544, 1088)
m.sector(rect(*CHANNEL), floor=-8, ceil=SKY, ctex="F_SKY1", light=200, wall="AJBRICK", ftex="AJTRIMF", color=R_WAY)
# the fight: a mancubus on each island, revenants on the south ledge, cacodemons and a pain elemental
# over the water, spectres in it, imps on the banks' foot, two hell knights at the outfall
put(67, [((min(p[0] for p in i) + max(p[0] for p in i)) // 2, (min(p[1] for p in i) + max(p[1] for p in i)) // 2)
         for i in ISLANDS], ISLE, angle=90)
put(66, [(3420, 420), (3700, 420), (3980, 420), (4200, 440)], LEDGE3, angle=90)
put(3005, [(3560, 1300), (3760, 760), (4150, 1000), (3700, 1420), (4150, 1250)], PW, angle=90)
put(71, [(3820, 980)], PW, angle=90)
put(58, [(3480, 1000), (3800, 1100), (4100, 760), (3660, 700), (4180, 1150)], PW, angle=90)
put(3001, [(3220, 1380), (3200, 1000), (3330, 640), (3640, 530), (4200, 560), (4200, 1420)], PG, angle=0)
put(69, [(4450, 992), (4450, 1056)], -8, angle=180)
m.thing(*spot(3220, 1150, 16, PG, solid=False), 2004, angle=0)          # a plasma rifle on the dry path
items_on(PG, 17, (3250, 820))
items_on(PG, 2047, (3420, 560), (3900, 520), (3160, 1260), (4300, 640))
items_on(PG, 2049, (4300, 1180))
items_on(PG, 2046, (3220, 1500), (4300, 820))
items_on(PG, 2049, (3600, 1640), (3260, 760))
items_on(PG, 2012, (3330, 1620), (4280, 1350), (4050, 520))
items_on(-8, 2013, (4520, 1000))                    # before the drop: a soulsphere and a blue armour
items_on(-8, 2019, (4520, 1050))

# --- the cooling tower, round, open to the sky: window hall 5 (part 3's own: its exit opens when
# nothing lives in it). A basin in the middle, eight pillars, a ring ledge broken at the way in and
# the way out ----------------------------------------------------------------------------------------
TC, TRW, TF = (5184, 1024), 646, -64          # its middle, the corners of its 24-sided wall, its floor


def tower_at(r, deg):
    return (round(TC[0] + r * math.cos(math.radians(deg))), round(TC[1] + r * math.sin(math.radians(deg))))


# (2026-11-24: the wall's corners at 0, 90 and 270 degrees pointed along an axis, and mapcheck's square
# bodies found a pocket in each on the ledge: the wall goes straight across them now. And the ledge's
# ends by the outfall end square to the line of its wall, not along a radius: the floor between was a
# wedge of 75 degrees, a pocket too)
FLAT = (0, 90, 270)
TOWER_OUT = []
for k in range(24):
    if k * 15 == 120:
        TOWER_OUT += [(4864, 1600), (4736, 1600)]           # the exit's alcove: its shutter faces north
    elif k * 15 == 180:
        TOWER_OUT += [(4544, 1088), (4544, 960)]            # the outfall's end
    elif k * 15 not in FLAT:
        TOWER_OUT.append(tower_at(TRW, k * 15))
RING = [a for a in range(0, 360, 15) if not 105 <= a < 135 and not 165 <= a < 195]     # the ledge's pieces start there


def ledge_piece(a):
    if (a + 15) % 360 in FLAT:                              # (two pieces in one: the wall straight across)
        return [tower_at(TRW, a), tower_at(TRW, a + 30), tower_at(552, a + 30), tower_at(552, a + 15), tower_at(552, a)]
    inner = [tower_at(552, a + 15), tower_at(552, a)]
    if a + 15 == 165:                                       # (by the outfall: its end along y)
        inner[0] = (inner[0][0], tower_at(TRW, 165)[1])
    if a == 195:
        inner[1] = (inner[1][0], tower_at(TRW, 195)[1])
    return [tower_at(TRW, a), tower_at(TRW, a + 15)] + inner


tfeat = [(ledge_piece(a), dict(floor=TF + 96, side="AJBRICK", ftex="AJTRIMF")) for a in RING if a not in FLAT]
BASIN = ngon(TC[0], TC[1], 176, 24)
tfeat.append((BASIN, dict(floor=TF - 16, ftex="FWATER1", color=None, light=190)))
PILLARS = [ajarmap.octagon(x - 32, y - 32, x + 32, y + 32, 19) for x, y in (tower_at(384, 22.5 + 45 * k) for k in range(8))]
natural(TOWER_OUT, tfeat, holes=PILLARS, floor=TF, ceil=SKY, ctex="F_SKY1", light=196, wall="AJBRICK", color=R_ROOM,
        id=TOWER)
no_monsters((4544, 960), (4544, 1088))
ajarthird.hall(m, 4620, 1024, H_TOWER, 3, TOWER)
ajartime.shutter(m, (4736, 1600), (4864, 1600), (0, 1), TF, TSHUT, nomonsters=True, color=R_WAY)
MOUTHS.append(((4736, 1600), (4864, 1600)))
no_monsters((4736, 1616), (4864, 1616))                  # (and none of the passage's stands in it)
ajarthird.win(m, 4800, 1560, H_TOWER, TSHUT)
# the fight: a cyberdemon on the basin (two barons in its place on the lowest skill), imps and
# revenants on the ring ledge, hell knights and barons on the floor, an arch-vile on the hardest
put(16, [TC], TF - 16, angle=180, skill=2)
put(3003, [(TC[0], TC[1] + 96), (TC[0], TC[1] - 96)], TF - 16, angle=180, skill=1, upto=1)
put(3001, [tower_at(600, a) for a in (200, 225, 250, 275, 300, 325, 350, 15)], TF + 96, angle=180)
put(66, [tower_at(600, a) for a in (40, 65, 90, 150)], TF + 96, angle=270)
put(69, [tower_at(280, a) for a in (0, 90, 270, 200)], TF, angle=180)
put(3003, [tower_at(480, a) for a in (45, 315)], TF, angle=180, skill=3)
put(64, [tower_at(280, 135)], TF, angle=270, skill=4)
for k in range(8):                                       # behind the pillars, as seen from the basin
    items_on(TF, 2046 if k % 2 else 17, tower_at(452, 22.5 + 45 * k))
items_on(TF, 2046, tower_at(452, 0), tower_at(452, 180 + 20))
items_on(TF, 2012, tower_at(300, 45), tower_at(300, 225), tower_at(300, 315), tower_at(470, 160))
items_on(TF, 2049, tower_at(470, 260), tower_at(470, 100))
items_on(TF, 17, tower_at(452, 250), tower_at(452, 70))

# --- behind the tower's exit: a passage north (on to the yard's corner piece, above), steps down into the
# duct's west end behind part 3's way on from the yard (WAY3, a shutter its group's death opens) -------------
m.sector(rect(4736, 1616, 4864, 1984), floor=TF, ceil=TF + 128, light=150, color=R_WAY)
put(65, [(4770, 1700), (4830, 1860)], TF, angle=270)
put(3001, [(4830, 1760), (4770, 1940)], TF, angle=270)
items_on(TF, 2049, (4800, 1660))
items_on(TF, 2046, (4770, 1820))
items_on(TF, 2012, (4800, 1950))
ajartime.shutter(m, (4864, 1984), (4864, 1856), (1, 0), TF, WAY3, nomonsters=True, color=R_WAY)
ajarthird.way(m, 4830, 1920, 3, WAY3)
ajarmap.stairs(m, (4880, 1856), (4880, 1984), (1, 0), TF, RF - TF, steps=8, depth=22, ceil=TF + 128, color=R_WAY)

# --- the duct along R's south wall, behind glass -------------------------------------------
DUCT = (5056, 1856, 7040, 2032)
area(DUCT, [((5056 + 256 * i, 1856, 5056 + 256 * i + 32, 1888), dict(ceil=RF + 96)) for i in range(8)],
     floor=RF, ceil=RF + 128, light=140, color=R_ROOM)
DUCT_WINDOWS = [(5120, 5344), (5504, 5984), (6144, 6592), (6752, 7008)]
for x1, x2 in DUCT_WINDOWS:
    ajartime.glass(m, (x1, 2048), (x2, 2048), (0, -1), RF, top=112)
mon(58, [(5600, 1950), (6300, 1950), (6900, 1950)], angle=180)
mon(3001, [(5900, 1950)], angle=180)
mon(69, [(6080, 1950), (6640, 1950)], angle=180)                  # (part 3, longer: two hell knights)
items(2046, (5300, 1950))
items(2011, (5200, 1950), (6600, 1950))
m.sector(rect(7040, 1856, 7616, 1984), floor=RF, ceil=RF + 128, light=150, color=R_WAY)
ajarmap.stairs(m, (7488, 1984), (7616, 1984), (0, 1), RF, -RF, steps=8, depth=32, ceil=G + 128, color=R_WAY)
# the landing at the stairs' head and the corridor east to stand 3, under the last hall's south wall
m.sector(rect(7488, 2240, 8192, 2336), ceil=128, light=170, color=R_WAY)
# stand 3's supplies, before it: a soulsphere, a blue armour, 2 cell packs, 2 boxes of rockets, a medikit
SUPPLY3 = [(2013, 7820, 2288), (2019, 7880, 2288), (17, 7940, 2270), (17, 7940, 2306), (2046, 8000, 2270),
           (2046, 8000, 2306), (2012, 8060, 2288)]

# =====================================================================================
# THE LAST HALL L: the switchgear hall, where the three goes fight one fight together
# (third.zs, last.zs; the lab is map LAST). Stand 1 (part 1) on its north side, stand 2
# (part 2) on its west, stand 3 (part 3) on its south; the exit door in its east wall.
# With the lab's four rules (last.zs): waves, the share, the stagger, the levers (below).
# =====================================================================================
L_BOX = (7808, 2368, 8960, 3392)
FL, LCEIL = -96, 384            # its floor (the stands are at the ground) and its ceiling
ST = [ajarthird.stand_tag(k) for k in (1, 2, 3)]
for kind, x, y in SUPPLY1 + SUPPLY2 + SUPPLY3:
    m.thing(x, y, kind)


def stand(k, box, pillar, **look):
    """Stand k: the rectangle `box` less a solid pillar 64 x 64."""
    return [m.sector(rect(*r), floor=G, ceil=192, light=200, id=ST[k - 1], **look) for r in ajarthird.tiles(*box, [pillar])]


STAND_BOX = {1: (8192, 3392, 8576, 3584), 2: (7616, 2688, 7808, 3072), 3: (8192, 2176, 8576, 2368)}
PILLAR = {1: (8288, 3456, 8352, 3520), 2: (7680, 2752, 7744, 2816), 3: (8448, 2240, 8512, 2304)}
PLATE1, PLATE2 = (8448, 3456), (7744, 2880)         # 64 behind their railings
STAND1 = stand(1, STAND_BOX[1], PILLAR[1], color=Y_ROOM)
ajarthird.plate(m, *PLATE1, 1)
ajarthird.time_door_at(m, 1, (8512, 3584), (8448, 3584), (0, 1), G, color=Y_WAY)
three((8224, 3584), (8400, 3584), (0, 1), G, color=Y_ROOM)
STAND2 = stand(2, STAND_BOX[2], PILLAR[2], color=G_ROOM)
ajarthird.plate(m, *PLATE2, 2)
ajarthird.time_door_at(m, 2, (7616, 3040), (7616, 2976), (-1, 0), G, color=G_WAY)
WIND2 = (7712, 3070)
ajarthird.wind(m, *WIND2, 270)
three((7792, 2688), (7632, 2688), (0, -1), G, color=G_ROOM)
STAND3 = stand(3, STAND_BOX[3], PILLAR[3], color=R_ROOM)
WIND3 = (8232, 2178)
ajarthird.wind(m, *WIND3, 90)
three((8448, 2176), (8288, 2176), (0, -1), G, color=R_ROOM)
# stand 3's gate in its railing's line (the alarm opens it; no monster comes up through it), steps down behind it
GATE3 = (8320, 8448)
ajartime.shutter(m, (GATE3[0], 2368), (GATE3[1], 2368), (0, 1), G, ALARM, nomonsters=True, color=R_WAY)
STEPS = (GATE3[0], 2368, GATE3[1], 2480)
ajarmap.stairs(m, (GATE3[0], 2384), (GATE3[1], 2384), (0, 1), G, FL, steps=6, depth=16, ceil=LCEIL, light=170,
               color=HALLC, id=LASTT)
# the railings: each stand's whole front (stand 3's either side of its gate)
for a, b in (((8192, 3392), (8576, 3392)), ((7808, 2688), (7808, 3072)), ((8192, 2368), (GATE3[0], 2368)),
             ((GATE3[1], 2368), (8576, 2368))):
    ajarthird.railing(m, a, b)

# the floor: pedestals 72 high (the arachnotrons' in the east half, the mancubi's in the west), bays 72 high
# (revenants: east wall, beside the exit door and by the corners; chaingunners: north and south walls, east
# parts), six switchgear cabinets 64 high
PEDESTALS = [(8672, 2464, 8864, 2656), (8672, 3104, 8864, 3296),      # arachnotrons (192: 2 x (64 + 24) and more)
             (7904, 2464, 8064, 2624), (7904, 3136, 8064, 3296)]      # mancubi (160: 2 x (48 + 24) and more)
BAYS = [(8960, 2624, 9024, 2752), (8960, 3008, 9024, 3136), (8960, 3232, 9024, 3360), (8960, 2400, 9024, 2528),
        (8640, 3392, 8768, 3456), (8800, 3392, 8928, 3456), (8640, 2304, 8768, 2368), (8800, 2304, 8928, 2368)]
BAY_MOUTH = [((8960, 2624), (8960, 2752)), ((8960, 3008), (8960, 3136)), ((8960, 3232), (8960, 3360)),
             ((8960, 2400), (8960, 2528)), ((8640, 3392), (8768, 3392)), ((8800, 3392), (8928, 3392)),
             ((8640, 2368), (8768, 2368)), ((8800, 2368), (8928, 2368))]
SWITCHGEAR = [(8448, 2592, 8576, 2656), (8672, 2752, 8800, 2816), (8672, 2944, 8800, 3008),
            (8160, 2752, 8288, 2816), (8384, 2944, 8512, 3008), (8224, 2592, 8352, 2656)]
CAB_H = 64

# The guards (ajarthird.guard): (kind, x, y, angle, z over the floor, skill, where it stands: None walks or
# flies, wave). Waves by plates (last.zs; PLAN.md "MAP33: the last hall with the four rules"): wave 1 at the
# alarm, every guard that stands (pedestals, bays); wave 2 when plate 2 is first pressed from the alarm on
# (go 2 and 3): the cacodemons, the pain elemental, the hell knights; wave 3 in go 3, when the third self
# first stands on the hall's floor (stand 3's steps are the hall's): the demons and the barons, on the east
# half between the middle of the crossing and the exit door.
MIDR = lambda r: ((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)
GUARDS = [(68, *MIDR(PEDESTALS[0]), 135, 0, 1, PEDESTALS[0], 1), (68, *MIDR(PEDESTALS[1]), 225, 0, 2, PEDESTALS[1], 1),
          (67, *MIDR(PEDESTALS[2]), 45, 0, 1, PEDESTALS[2], 1), (67, *MIDR(PEDESTALS[3]), 315, 0, 3, PEDESTALS[3], 1),
          # (in a bay: 24 in from its mouth, so that it is seen at a slant)
          (66, 8984, MIDR(BAYS[0])[1], 180, 0, 1, BAYS[0], 1), (66, 8984, MIDR(BAYS[1])[1], 180, 0, 1, BAYS[1], 1),
          (66, 8984, MIDR(BAYS[2])[1], 180, 0, 2, BAYS[2], 1), (66, 8984, MIDR(BAYS[3])[1], 180, 0, 3, BAYS[3], 1),
          (65, MIDR(BAYS[4])[0], 3416, 270, 0, 1, BAYS[4], 1), (65, MIDR(BAYS[5])[0], 3416, 270, 0, 2, BAYS[5], 1),
          (65, MIDR(BAYS[6])[0], 2344, 90, 0, 2, BAYS[6], 1), (65, MIDR(BAYS[7])[0], 2344, 90, 0, 3, BAYS[7], 1),
          # wave 2: over the middle, and the knights on the floor (green patches)
          (3005, 8400, 2880, 180, 200, 1, None, 2), (3005, 8600, 3200, 180, 220, 2, None, 2),
          (3005, 8150, 2700, 90, 200, 3, None, 2), (3005, 8540, 2780, 90, 240, 4, None, 2),
          (71, 8400, 3220, 270, 230, 4, None, 2),
          (69, 8100, 2960, 0, 0, 1, None, 2), (69, 8460, 2800, 180, 0, 2, None, 2), (69, 8360, 3100, 270, 0, 3, None, 2),
          # wave 3 (red patches): before the exit door, on the steam's strip and beside it
          (3002, 8880, 2720, 180, 0, 1, None, 3), (3002, 8740, 2880, 180, 0, 1, None, 3),
          (3002, 8740, 3056, 180, 0, 2, None, 3), (3002, 8620, 2720, 180, 0, 2, None, 3),
          (3002, 8620, 3010, 180, 0, 3, None, 3), (3002, 8912, 2560, 180, 0, 3, None, 3),
          (3003, 8880, 2848, 180, 0, 2, None, 3), (3003, 8880, 3040, 180, 0, 4, None, 3)]
WALKS = {69, 3002, 3003}
# the marks on the floor where a walking guard of wave 2 (green) or 3 (red) comes: a 64 x 64 sector of its own
# with the hall's tag, a lit plate (AJLITE, the game's own) at full light, strongly tinted
GREEN, RED = 0x30FF30, 0xFF2828
PATCHES = [((x - 32, y - 32, x + 32, y + 32), GREEN if w == 2 else RED) for k, x, y, a, z, sk, place, w in GUARDS
           if w > 1 and k in WALKS]
# the steam's strip before the exit door: the last 256 of the crossing, across the door's width and 128 to each
# side (x 8704..8960, y 2688..3072); its floor the lit plates (AJLITE) tinted pale blue at full light (a grating,
# AJZPLT, was tried: dark, it was not told from the hall's floor from stand 1); six vents (reach 96) cover it,
# on the floor round the two cabinets in it
STRIP = (8704, 2688, 8960, 3072)
STEAMY = 0x78B4FF
VENTS = [(8768, 2720), (8768, 2880), (8768, 3040), (8896, 2752), (8896, 2880), (8896, 3008)]


def overlap(p, q):
    return p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]


def marked(r, ftex, colour, pan=False):
    """A piece of the hall's floor told apart: its own floor picture, tinted, at full light (the rest as the hall)."""
    raw = dict(color_floor=colour, lightfloor=255, lightfloorabsolute=True)
    if pan:                     # (the picture's frame on the patch's edges)
        raw.update(xpanningfloor=float(-r[0] % 64), ypanningfloor=float(r[3] % 64))
    m.sector(rect(*r), floor=FL, ceil=LCEIL, light=170, color=HALLC, ftex=ftex, id=LASTT, raw=raw)


ISLANDS = PEDESTALS + SWITCHGEAR + [STEPS]
for r in ajarthird.tiles(*L_BOX, ISLANDS + [STRIP] + [p for p, c in PATCHES]):
    m.sector(rect(*r), floor=FL, ceil=LCEIL, light=170, color=HALLC, id=LASTT)
for r in ajarthird.tiles(*STRIP, [c for c in ISLANDS if overlap(c, STRIP)] + [p for p, c in PATCHES if overlap(p, STRIP)]):
    marked(r, "AJLITE", STEAMY)
for p, c in PATCHES:
    marked(p, "AJLITE", c, pan=True)
for p in PEDESTALS:
    m.sector(rect(*p), floor=FL + 72, ceil=LCEIL, light=180, color=HALLC, side="AJBOLT", ftex="AJTRIMF", id=LASTT)
    for a, b in (((p[0], p[1]), (p[2], p[1])), ((p[2], p[1]), (p[2], p[3])), ((p[2], p[3]), (p[0], p[3])),
                 ((p[0], p[3]), (p[0], p[1]))):
        m.line(a, b, blockmonsters=True)                 # (no monster is thrown off it)
for b, (p, q) in zip(BAYS, BAY_MOUTH):
    m.sector(rect(*b), floor=FL + 72, ceil=FL + 200, light=160, color=HALLC, side="AJBRICK", ftex="AJTRIMF", id=LASTT)
    m.line(p, q, blockmonsters=True)
for c in SWITCHGEAR:
    m.sector(rect(*c), floor=FL + CAB_H, ceil=LCEIL, light=180, color=STEELC, side="AJBOLT", ftex="AJTRIMF", id=LASTT)
# the exit door in the east wall, at the floor, and the way out
ajartime.shutter(m, (8960, 2944), (8960, 2816), (1, 0), FL, EXIT, color=R_WAY)
m.sector(rect(8976, 2816, 9104, 2944), floor=FL, ceil=FL + 128, light=220, color=R_WAY, id=OUT)
m.sector(rect(9104, 2816, 9168, 2944), floor=FL, ceil=FL + 128, light=230, color=R_WAY, ftex="AJTRIMF")
m.line((9104, 2816), (9104, 2944), special=243, playercross=True)
m.line((9168, 2816), (9168, 2944), mid="AJEXIT", exact=True)

for kind, x, y, a, z, sk, place, w in GUARDS:
    ajarthird.guard(m, x, y, kind, a, z, skill=sk, wave=w)
# The share (one invulnerability sphere for the three selves): a copy on each stand near its back wall, clear
# of the plate, the time door, the wind plate, the case of three and the pillar
SHARES = {1: (8544, 3544), 2: (7648, 2752), 3: (8544, 2208)}
for x, y in SHARES.values():
    ajarthird.share(m, x, y)
# The levers (the hall's machines): 1, the steam valve, on stand 1's east wall (its vents, number 1, on the
# strip); 2, the breaker, on stand 2's north wall, east of the wind plate. None on stand 3.
LEVER1, LEVER2 = (8574, 3440), (7780, 3070)
ajarthird.lever(m, *LEVER1, 180, 1, 1, tag=1)
ajarthird.lever(m, *LEVER2, 270, 2, 2)
for x, y in VENTS:
    ajarthird.vent(m, x, y, 1)
# (an earlier self hit by 60, summed from the alarm and falling by 1 a tic, holds its fire for three seconds)
ajarthird.last(m, 9040, 2860, LASTT, gate=ALARM, stagger=60)

ajarthird.third(m, 9040, 2900, EXIT, OUT, (-1264, 0, 9400, 5400))      # (its middle on the yard's floor)

# =====================================================================================
# CHECKS
# =====================================================================================
S = sec_at(384, 2640)
# each part from its start, and from beyond its doors' far sides (BLUE: the catwalk; VIOLET: the armoury;
# PINK: the relay room); a pit behind its railing is reached from nowhere and counted with R below.
# Part 3 reaches the last hall's floor and the exit by its gate; stands 1 and 2 are not reached from it.
PARTS = ajarthird.apart(m, {1: [S, sec_at(2272, 4900)], 2: [BOX2, sec_at(2500, 2400)], 3: [BOX3, sec_at(3200, 1950)]})
assert set(STAND1) <= PARTS[1] and set(STAND2) <= PARTS[2] and set(STAND3) <= PARTS[3]
L_SECS = {i for i, s in enumerate(m.sectors) if s["id"] == LASTT}
assert L_SECS <= PARTS[3] and sec_at(9040, 2880) in PARTS[3]
# every stand's railing is closed to players and monsters (stand 3's gate is a sector of its own)
RAILS = [ajarthird.closed(m, t, LASTT) for t in ST]
assert all(RAILS), RAILS
assert sec_at(6000, 2300) in PARTS[2]                                   # R is part 2's
assert sec_at(6000, 3330) in PARTS[1]                                   # the gantry part 1's
assert sec_at(6000, 1950) in PARTS[3]                                   # the duct part 3's


def part_of(x, y):
    s = sec_at(x, y)
    for p, got in PARTS.items():
        if s in got:
            return p
    if s is not None and m.sectors[s]["id"] == RT:                    # R's pits, behind their railings
        return 2
    return None


# each sector's part, for the tests (map33.zs reads it: user_part)
for i, sec in enumerate(m.sectors):
    p = next((q for q, got in PARTS.items() if i in got), 2 if sec["id"] == RT else 0)
    if p:
        sec["raw"]["user_part"] = p


# Every window hall is closed to monsters: each two-sided way out of its sectors is a mouth with a
# monster-blocking line, a line that blocks, glass, or a step no monster takes (more than 24 up from
# inside and the hall's own side the low one is not enough: a flyer goes up it).
def hall_ways(tags):
    """The two-sided lines between a sector with one of `tags` and one without (as edge keys)."""
    polys = m._split()
    edges = {}
    for i, p in enumerate(polys):
        for a, b in zip(p, p[1:] + p[:1]):
            edges[(a, b)] = i
    out = []
    for (a, b), i in edges.items():
        j = edges.get((b, a))
        if j is None or (m.sectors[i]["id"] in tags) == (m.sectors[j]["id"] in tags) or m.sectors[i]["id"] not in tags:
            continue
        out.append((a, b, j))
    return out


def blocked(a, b):
    """Does a line given in m.lineprops cover the edge a-b and keep monsters off it?"""
    for key, pr in m.lineprops.items():
        if len(key) != 2:
            continue
        p1, p2 = tuple(key)
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        ok = True
        for v in (a, b):
            px, py = v[0] - p1[0], v[1] - p1[1]
            t = (px * dx + py * dy) / (dx * dx + dy * dy)
            if dx * py - dy * px != 0 or not -1e-9 <= t <= 1 + 1e-9:
                ok = False
        if ok and (pr.get("blockmonsters") or pr.get("blocking") or pr.get("special") == 156):
            return True
    return False


# (a lobby is in its hall; a lock's shutters and a win's are closed: shut while anything of the hall lives)
LOCK_WIN = {YOUT, YIN, BOUT, BIN, WOUT, WIN_, CATSHUT, ASHSHUT, PUMPSHUT}
for tags in ((YARD, YLOB), (WORK, WLOB), (RT, GANTRY), (BOIL, BLOB), (TOWER,)):
    for a, b, j in hall_ways(tags):
        assert blocked(a, b) or m.sectors[j]["id"] in LOCK_WIN, ("a window hall open to monsters", tags, a, b, m.sectors[j]["id"])
# no line only monsters are kept off remains across an open doorway of the three halls with lobbies: each is
# on a shutter's face (the yard's gate, the ways on) or a window's (glass), never between two open floors
for key, pr in m.lineprops.items():
    if len(key) != 2 or not pr.get("blockmonsters") or pr.get("blocking"):
        continue
    a, b = tuple(key)
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    n = (b[1] - a[1], a[0] - b[0])
    ln = math.hypot(*n)
    sides = [sec_at(mid[0] + n[0] / ln * 4 * s, mid[1] + n[1] / ln * 4 * s) for s in (1, -1)]
    tags_ = [m.sectors[s]["id"] if s is not None else None for s in sides]
    if any(t in (YARD, YLOB, BOIL, BLOB, WORK, WLOB) for t in tags_):
        assert any(t in (GATE, CATSHUT, ASHSHUT, PUMPSHUT) for t in tags_) or None in tags_, ("an invisible line in a hall's doorway", a, b, tags_)

# Things in each part, and the supplies against the monsters (skill 3 "Resident", 1 "Just visiting")
SK = m._skills()
BY_PART = {1: [], 2: [], 3: []}
for t, s in zip(m.things, SK):
    p = t["args"][1] if t["type"] == ajarthird.COMER_T else part_of(t["x"], t["y"])     # (a group's monster: its part's)
    if p and t["type"] != ajarthird.GUARD_T:            # (the last hall's guards are fought anew by every go: below)
        BY_PART[p].append((t, s))
SUPPLY = {}
RATIO = {1: 1.6, 2: 1.6, 3: 1.6}          # ammunition's damage against the monsters' health, at least
for p, ts in BY_PART.items():
    for level in (3, 1):
        r = budget.reckon([t for t, s in ts], [s for t, s in ts], level)
        SUPPLY[p, level] = r
    r = SUPPLY[p, 3]
    assert r["dmg"] >= RATIO[p] * r["hp"], ("part", p, r["dmg"], r["hp"])
MONSTERS3 = {p: sum(SUPPLY[p, 3]["monsters"].values()) for p in BY_PART}
assert 110 <= MONSTERS3[1] <= 130 and 100 <= MONSTERS3[2] <= 120 and 95 <= MONSTERS3[3] <= 110, MONSTERS3
# every monster of the level is in one of the parts
for t in m.things:
    if t["type"] in MONSTERS or t["type"] in (ajarthird.POST_T, ajarthird.FALLEN_T):
        assert part_of(t["x"], t["y"]), ("a monster in no part", t)

# --- the yard (the common place): its levels, the place closed, its groups, the shed, the stairs' feet ----------
TAGS = {i: sec["id"] for i, sec in enumerate(m.sectors)}
LV = {k: {i for i, t in TAGS.items() if t == ajarthird.level_tag(k)} for k in (1, 2, 3)}
# each level's sectors tagged (and nothing else of the map): the north ledge and the terrace (behind its entry);
# the floor round its pumps, pipes and banks; the south ledge and the corner piece (behind its entry). Each is
# its own part's (part 1's and part 3's apart from part 2's floor, the rims closed: ajarthird.apart above)
assert LV[1] == {LEDGE1_SEC, TERR_SECS[1]} and LV[3] == {LEDGE3_SEC, CORNER_SECS[1]}, (LV[1], LV[3])
assert LV[2] == {i for i in FLOOR_SECS if TAGS[i] == L2} and len(LV[2]) >= 4, LV[2]
assert all(LV[k] <= PARTS[k] for k in (1, 2, 3)), "a level not its part's"
assert TAGS[TERR_SECS[0]] == TAGS[CORNER_SECS[0]] == YPLACE and all(TAGS[i] == YPLACE for i in SHED_SECS)
# the place is closed to monsters: every two-sided line out of it blocks them (the rims inside it do not)
YARD_SEALED = ajarthird.sealed(m, {YPLACE, L1, L2, L3})
assert YARD_SEALED >= 5, YARD_SEALED
# the groups: a walker stands on the floor's level with room (its box and 8 more, all on level 2's sectors at
# the floor's height), none within 256 of the west stairs' foot; a flyer over level 2 with room round it and
# under the sky; no comer in a wall
YWALKS = {69, 3001, 3002, 65, 58, 3004, 9}
for kind, x, y, a, z, part, f, sk in GROUPS:
    r = ajartime.RADIUS[kind]
    s0 = sec_at(x, y)
    assert s0 is not None and TAGS[s0] == L2, ("a comer not over the floor", kind, x, y)
    if kind in YWALKS:
        assert z == 0 and f and stands_on(x, y, r + 8, FLOOR2, L2), ("a walker of the yard with no room", kind, x, y)
        assert foot_dist((x, y), W_STAIRS, True) >= 256, ("a walker by the west stairs' foot", kind, x, y)
    else:
        assert not f and 96 <= z and FLOOR2 + z + ajartime.HEIGHT[kind] < SKY - 16, ("a flyer's height", kind, x, y, z)
        assert stands_on(x, y, r + 8, FLOOR2, L2), ("a flyer over something, or in a wall", kind, x, y)
# the bodies (the walkers, seen fallen in go 1) each seen from two of the terrace, the north ledge, the south ledge
BODIES_SEEN = {k: 0 for k in YEYES}
for kind, x, y, a, z, part, f, sk in GROUPS:
    if f:
        by = seen_from(x, y, FLOOR2 + 8)
        assert len(by) >= 2, ("a body seen from too few places", kind, x, y, by)
        for k in by:
            BODIES_SEEN[k] += 1
# the shed: its own sector, the secret, entered from the floor by a doorway 64 wide or more (walked into below)
assert SHED_DOOR[3] - SHED_DOOR[1] >= 64 and m.sectors[SHED_SECS[0]]["special"] == 1024
assert sec_at(SHED_DOOR[0] + 8, (SHED_DOOR[1] + SHED_DOOR[3]) // 2) == SHED_SECS[1]
# nothing over 24 high on the floor before a stairs' foot (96 deep, 32 more to each side)
for x1, y1, x2, y2 in ((W_STAIRS[2], W_STAIRS[1] - 32, W_STAIRS[2] + 96, W_STAIRS[3] + 32),
                       (E_STAIRS[0] - 96, E_STAIRS[1] - 32, E_STAIRS[0], E_STAIRS[3] + 32)):
    for px in range(x1 + 1, x2, 8):
        for py in range(y1 + 1, y2, 8):
            sp = sec_at(px, py)
            assert sp is not None and m.sectors[sp]["floor"] <= FLOOR2 + 24, ("something high at a stairs' foot", px, py)
# the counts by skill (the build's row)
YGROUP = {(k, lv): 0 for k in (1, 2, 3) for lv in (1, 2, 3, 4)}
for t, sk in zip(m.things, SK):
    if t["type"] == ajarthird.COMER_T:
        for lv in (1, 2, 3, 4):
            if sk <= lv and lv <= t.get("upto", 4):
                YGROUP[t["args"][1], lv] += 1

# The last hall: in no part's count; its guards by skill, their health against each stand's supplies
G_THINGS = [(t, s) for t, s in zip(m.things, SK) if t["type"] == ajarthird.GUARD_T]
LAST_ROW = {lv: budget.reckon([t for t, s in G_THINGS], [s for t, s in G_THINGS], lv) for lv in (1, 2, 3, 4)}
STAND_SUP = {k: budget.reckon([dict(x=x, y=y, type=kind) for kind, x, y in sup], [1] * len(sup), 3)
             for k, sup in ((1, SUPPLY1), (2, SUPPLY2), (3, SUPPLY3))}
MEASURE = [f"MAP33: {len(m.sectors)} sectors, {len(m.things)} things; monsters on skill 3 "
           f"{MONSTERS3[1]} + {MONSTERS3[2]} + {MONSTERS3[3]}"] + \
          ["    the yard: groups (skill 1 / 2 / 3 / 4) " + "; ".join(f"part {k} " + " / ".join(str(YGROUP[k, lv]) for lv in (1, 2, 3, 4))
                                                                 for k in (1, 2, 3))
           + f"; the bodies seen from " + ", ".join(f"{k} {n}" for k, n in BODIES_SEEN.items())
           + f" of {sum(1 for g in GROUPS if g[6])}; {YARD_SEALED} ways out closed to monsters"] + \
          ["    " + budget.line(f"part {p}", SUPPLY[p, lv], lv) for p in (1, 2, 3) for lv in (3, 1)] + \
          ["    the last hall: guards on skill " + ", ".join(f"{lv} {sum(LAST_ROW[lv]['monsters'].values())} (hp {LAST_ROW[lv]['hp']})"
                                                         for lv in (1, 2, 3, 4)) + "; "
           + ", ".join(f"stand {k}'s supplies dmg {r['dmg']} (x{r['dmg'] / LAST_ROW[3]['hp']:.2f} of skill 3), heal {r['heal']}, "
                       f"armour {r['armor']}" for k, r in STAND_SUP.items())]


# --- the last hall's guards: room, sight, cover -------------------------------------------------
# the space between them, in pieces (x1, y1, x2, y2, floor, ceil): the hall, its islands, the bays, the gate
# (open) and its steps, the stands (less their pillars)
L_SPACES = [r + (FL, LCEIL) for r in ajarthird.tiles(*L_BOX, PEDESTALS + SWITCHGEAR + [STEPS])]
L_SPACES += [p + (FL + 72, LCEIL) for p in PEDESTALS] + [c + (FL + CAB_H, LCEIL) for c in SWITCHGEAR]
L_SPACES += [b + (FL + 72, FL + 200) for b in BAYS]
L_SPACES += [(GATE3[0], 2368, GATE3[1], 2384, G, G + 96)]
L_SPACES += [(GATE3[0], 2384 + 16 * i, GATE3[1], 2400 + 16 * i, G + FL * (i + 1) // 6, LCEIL) for i in range(6)]
for k in (1, 2, 3):
    L_SPACES += [r + (G, 192) for r in ajarthird.tiles(*STAND_BOX[k], [PILLAR[k]])]
# the crossing: the third self's way from stand 3 through the gate and the steps, along the first cabinet,
# between the two by the exit door, out (map33.zs walks it)
CROSSING = [(8384, 2330), (8384, 2500), (8400, 2560), (8400, 2688), (8600, 2688), (8640, 2730), (8640, 2916),
            (8930, 2916), (8990, 2880), (9140, 2880)]


def along(path, step=16):
    out = []
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) // step))
        out += [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n)]
    return out + [path[-1]]


CROSS_PTS = [p for p in along(CROSSING) if L_BOX[0] < p[0] < L_BOX[2] and p[1] > 2480]     # (on the hall's floor)
EYES = [(*PLATE1, G + 41), (*PLATE2, G + 41)]
COVER = {}
for kind, x, y, a, z, sk, place, w in GUARDS:
    r, hgt = ajartime.RADIUS[kind], ajartime.HEIGHT[kind]
    if place is None:
        assert stands(x, y, r + 8, FL), ("a guard with no room on the floor", kind, x, y)
        continue
    zf = FL + 72
    assert place[0] + r + 24 <= x <= place[2] - r - 24 or place in BAYS and place[0] + 24 <= x <= place[2] - 24, ("no room", kind, x, y)
    assert place[1] + r + 24 <= y <= place[3] - r - 24 or place in BAYS and place[1] + 24 <= y <= place[3] - 24, ("no room", kind, x, y)
    assert sec_at(x, y) is not None and m.sectors[sec_at(x, y)]["floor"] == zf
    mid, eye = (x, y, zf + hgt / 2), (x, y, zf + hgt * 3 / 4)
    assert any(ajartime.seen(L_SPACES, e, mid) for e in EYES), ("a standing guard seen from neither plate", kind, x, y)
    assert any(ajartime.seen(L_SPACES, (px, py, FL + 41), mid) for px, py in CROSS_PTS), ("a guard not seen from the crossing", kind, x, y)
    hid = [(px, py) for px, py in CROSS_PTS if not ajartime.seen(L_SPACES, eye, (px, py, FL + 54))]
    COVER[(kind, x, y)] = hid
assert all(COVER.values()), ("the crossing has no cover from these standing guards", [g for g, h in COVER.items() if not h])
# the cabinets: 96 clear between any two, to the walls, the pedestals and the steps
for i, c in enumerate(SWITCHGEAR):
    assert L_BOX[0] + 96 <= c[0] and c[2] <= L_BOX[2] - 96 and L_BOX[1] + 96 <= c[1] and c[3] <= L_BOX[3] - 96, c
    for o in SWITCHGEAR[i + 1:] + PEDESTALS + [STEPS]:
        assert c[2] + 96 <= o[0] or o[2] + 96 <= c[0] or c[3] + 96 <= o[1] or o[3] + 96 <= c[1], ("cabinets too near", c, o)


# --- the four rules in the hall: waves, patches, the steam's strip, the share, the levers ----------
def seg_dist(p, a, b):
    """The distance from point p to the segment a-b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


# wave 1 is every guard that stands (on a pedestal or in a bay) and only those; wave 2 the flyers and the knights,
# wave 3 the demons and the barons
assert all((w == 1) == (place is not None) for kind, x, y, a, z, sk, place, w in GUARDS)
assert all(w == (2 if kind in (3005, 71, 69) else 3) for kind, x, y, a, z, sk, place, w in GUARDS if place is None)
# wave 3 on the east half, between the middle of the crossing and the exit door, none within 256 of the foot
# of stand 3's steps
_c = along(CROSSING, 4)
MIDCROSS = _c[len(_c) // 2]
FOOT = ((GATE3[0] + GATE3[1]) / 2, STEPS[3])
for kind, x, y, a, z, sk, place, w in GUARDS:
    if w == 3:
        assert x > (L_BOX[0] + L_BOX[2]) / 2 and x >= MIDCROSS[0] - 32 and math.hypot(x - FOOT[0], y - FOOT[1]) >= 256, ("wave 3's place", kind, x, y)
# a patch in the hall, clear of every island and of the other patches; a walking guard in its middle
for i, (p, c) in enumerate(PATCHES):
    assert L_BOX[0] <= p[0] and p[2] <= L_BOX[2] and L_BOX[1] <= p[1] and p[3] <= L_BOX[3], p
    assert not any(overlap(p, q) for q in ISLANDS) and not any(overlap(p, q) for q, d in PATCHES[i + 1:]), ("a patch on an island", p)
# the red patches near the exit door (their middles within 256 of the door's) lie on the steam's strip
DOOR_MID = (8960, 2880)
for p, c in PATCHES:
    mx, my = (p[0] + p[2]) / 2, (p[1] + p[3]) / 2
    if c == RED and math.hypot(mx - DOOR_MID[0], my - DOOR_MID[1]) <= 256:
        assert STRIP[0] <= mx <= STRIP[2] and STRIP[1] <= my <= STRIP[3], ("a red patch by the door off the strip", p)
# the vents: on the hall's floor (not on a cabinet), and every point of the strip's floor within the reach
# (96) of one, so that the steam is where the floor is blue
for x, y in VENTS:
    s = sec_at(x, y)
    assert s is not None and m.sectors[s]["floor"] == FL and m.sectors[s]["id"] == LASTT, ("a vent off the floor", x, y)
for px in range(STRIP[0] + 4, STRIP[2], 8):
    for py in range(STRIP[1] + 4, STRIP[3], 8):
        s = sec_at(px, py)
        if s is not None and m.sectors[s]["floor"] == FL:
            assert any(math.hypot(px - vx, py - vy) <= 96 for vx, vy in VENTS), ("the strip beyond the steam", px, py)
# the share: a copy on each stand's floor with 24 clear all round (a 48-wide square), near its back wall,
# clear of the plate, the time door, the wind plate and the case of three
TIME_MOUTH = {1: ((8448, 3584), (8512, 3584)), 2: ((7616, 2976), (7616, 3040))}
CASE_MOUTH = {1: ((8224, 3584), (8400, 3584)), 2: ((7632, 2688), (7792, 2688)), 3: ((8288, 2176), (8448, 2176))}
WINDS = {2: WIND2, 3: WIND3}
PLATES = {1: PLATE1, 2: PLATE2}
BACK = {1: ((8192, 3584), (8576, 3584)), 2: ((7616, 2688), (7616, 3072)), 3: ((8192, 2176), (8576, 2176))}
for k, (x, y) in SHARES.items():
    assert stands(x, y, 24, G) and m.sectors[sec_at(x, y)]["id"] == ST[k - 1], ("the share's copy has no room", k)
    assert seg_dist((x, y), *BACK[k]) <= 48, ("the share's copy not near the back wall", k)
    assert k not in PLATES or math.hypot(x - PLATES[k][0], y - PLATES[k][1]) >= 96
    assert k not in TIME_MOUTH or seg_dist((x, y), *TIME_MOUTH[k]) >= 48
    assert k not in WINDS or math.hypot(x - WINDS[k][0], y - WINDS[k][1]) >= 96
    assert seg_dist((x, y), *CASE_MOUTH[k]) >= 48, ("the share's copy at the case", k)
# the levers: 2 off a wall of their stand, clear of its time door, its wind plate and its case
for k, (x, y) in ((1, LEVER1), (2, LEVER2)):
    s = sec_at(x, y)
    assert s is not None and m.sectors[s]["id"] == ST[k - 1]
    assert seg_dist((x, y), *TIME_MOUTH[k]) >= 96 and seg_dist((x, y), *CASE_MOUTH[k]) >= 96
    assert k not in WINDS or math.hypot(x - WINDS[k][0], y - WINDS[k][1]) >= 64

# --- each part's length on foot (python3 tools/map_station.py --walk) ---------------------------
RUN = 583            # units a second, running (MAP08's measure)


def walk_lengths(step=16):
    """The shortest walk of each part from its start to its end (plate 1, plate 2, through the exit
    door), with the door it needs fetched and hung on the way: a grid of `step`, the player's box
    kept clear of walls, steps of 24 up at most, any drop down, 56 of headroom, no line that blocks
    crossed (railings, glass, bars); shutters taken as open."""
    x0, y0 = -256, -64
    xs = [p[0] for poly in m.polys for p in poly]
    ys = [p[1] for poly in m.polys for p in poly]
    W, H = int((max(xs) - x0) // step) + 2, int((max(ys) - y0) // step) + 2
    cell = [-1] * (W * H)
    for i, poly in enumerate(m.polys):
        bx = (min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly))
        for cy in range(int((bx[1] - y0) // step), int((bx[3] - y0) // step) + 1):
            for cx in range(int((bx[0] - x0) // step), int((bx[2] - x0) // step) + 1):
                px, py = x0 + cx * step + step / 2, y0 + cy * step + step / 2
                if 0 <= cx < W and 0 <= cy < H and inside(poly, px, py):
                    cell[cy * W + cx] = i
    fl = [s["floor"] for s in m.sectors]
    ce = [s["ceil"] if s["ceil"] > s["floor"] else s["floor"] + 96 for s in m.sectors]
    # cells by a line that blocks are not stood in
    for key, pr in m.lineprops.items():
        if len(key) != 2 or not (pr.get("blocking") or pr.get("blockeverything") or pr.get("blockplayers")):    # (a rim)
            continue
        (ax, ay), (bx_, by) = tuple(key)
        n = int(max(abs(bx_ - ax), abs(by - ay)) / 4) + 1
        for k in range(n + 1):
            px, py = ax + (bx_ - ax) * k / n, ay + (by - ay) * k / n
            for dx in (-12, 0, 12):
                for dy in (-12, 0, 12):
                    cx, cy = int((px + dx - x0) // step), int((py + dy - y0) // step)
                    if 0 <= cx < W and 0 <= cy < H:
                        cell[cy * W + cx] = -2
    ok = [False] * (W * H)
    for cy in range(1, H - 1):
        for cx in range(1, W - 1):
            k = cy * W + cx
            if cell[k] >= 0 and all(cell[k + d] >= 0 for d in (1, -1, W, -W, W + 1, W - 1, -W + 1, -W - 1)):
                ok[k] = True

    def at(x, y):
        return int((y - y0) // step) * W + int((x - x0) // step)

    def dist(a, b):
        src, dst = at(*a), at(*b)
        assert ok[src] and ok[dst], ("a walk's end is not stood in", a, b)
        best = {src: 0.0}
        todo = [(0.0, src)]
        moves = [(d, step * (1.4142 if dx and dy else 1)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                 if dx or dy for d in [dy * W + dx]]
        ROUND = (1, -1, W, -W, W + 1, W - 1, -W + 1, -W - 1)
        while todo:
            c, k = heapq.heappop(todo)
            if k == dst:
                return c
            if c > best.get(k, 1e18):
                continue
            s1 = cell[k]
            for d, w in moves:
                j = k + d
                if not ok[j]:
                    continue
                s2 = cell[j]
                if fl[s2] - fl[s1] > 24 or min(ce[s1], ce[s2]) - max(fl[s1], fl[s2]) < 56:
                    continue
                # the player's box (the cells round it) is not in a crate, a bench or a bank: nothing round
                # the cell stands more than a step over it (so a slot 32 wide between furniture is no way)
                # (what is no higher than where the step comes from does not count: a drop lands at the ledge's foot)
                if any(fl[cell[j + d2]] - fl[s2] > 24 and fl[cell[j + d2]] - fl[s1] > 24 for d2 in ROUND):
                    continue
                if c + w < best.get(j, 1e18):
                    best[j] = c + w
                    heapq.heappush(todo, (c + w, j))
        raise AssertionError(("no walk", a, b))

    legs = {1: [((384, 2640), (3330, 3880)), ((3330, 3880), (FRAME_B[0] + 32, 4200)), ((2272, 4960), (4880, 3300)), ((4880, 3300), PLATE1)],     # (over the yard's terrace)
            2: [((576, 2400), PLATE2)],
            3: [((192, 2400), (1400, 1860)), ((1400, 1860), (2790, 1440)), ((2976, 1888), (4800, 1580)),
                ((4800, 1580), (4700, 2176)), ((4700, 2176), (8384, 2300)), ((8384, 2300), (9140, 2880))]}
    # (part 3: onto the yard's corner piece and its ledge, back to the duct stairs; the last: through the gate, across L)
    # the three secrets are walked into (itemcheck's reckoning passed the old nook when its gap was 32)
    legs["the secrets (cache, shed, hut)"] = [((3650, 3904), (4480, 3904)), ((4300, 2512), (4030, 2512)),
                                              ((2700, 1000), (2896, 990))]
    return {p: [dist(a, b) for a, b in ls] for p, ls in legs.items()}


# every build walks each part and into each secret (about 4 s): a way a player's box does not pass stops it
WALK = walk_lengths()

if __name__ == "__main__":
    if "--walk" in sys.argv:
        for p, ls in WALK.items():
            print(f"{p if isinstance(p, str) else 'part ' + str(p)}: {round(sum(ls))} units ({' + '.join(str(round(x)) for x in ls)}), "
                  f"{sum(ls) / RUN:.1f} s at a run")
    else:
        sys.stdout.write(m.textmap())
