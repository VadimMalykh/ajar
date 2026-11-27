"""Checks a level's geometry and draws it: python3 tools/mapcheck.py map_hinges6 [out.png]

Reports sectors that overlap, things that stand in no sector or in a sector
too low for them, things closer than 16 to a wall or a step they cannot
climb, pits: floors with everything around them more than a step higher
and nothing that could take the player out again, lintels: steps down
that are shut by a ceiling too low over the upper floor, and slots: places a
body 32 wide (the player) gets into and one 48 wide does not, and parts only
the narrower one gets to (nothing the player might walk into is to be under
48). The picture (4 map units to a pixel, north up) shows floors by
height, things as dots (red: monsters, green: the rest) and doors, frames
and keys in white.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import gfx

mod = importlib.import_module(sys.argv[1])
m = mod.m
S = 4
polys = m.polys
xs = [p[0] for poly in polys for p in poly if p[0] < 3000]
ys = [p[1] for poly in polys for p in poly]
x0, x1, y0, y1 = min(xs) - 32, max(xs) + 32, min(ys) - 32, max(ys) + 32
W, H = (x1 - x0) // S, (y1 - y0) // S


def inside(poly, x, y):
    n = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            n = not n
    return n


def sector_at(x, y):
    return [i for i, poly in enumerate(polys) if inside(poly, x, y)]


bad = 0
boxes = [(min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly))
         for poly in polys]
for i in range(len(polys)):
    for j in range(i + 1, len(polys)):
        a, b = boxes[i], boxes[j]
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            cx, cy = (max(a[0], b[0]) + min(a[2], b[2])) / 2, (max(a[1], b[1]) + min(a[3], b[3])) / 2
            if inside(polys[i], cx + 0.5, cy + 0.5) and inside(polys[j], cx + 0.5, cy + 0.5):
                print(f"OVERLAP sectors {i} {boxes[i]} and {j} {boxes[j]}")
                bad += 1

MONSTERS = {3004, 9, 3001, 3002, 58, 65, 69, 3003, 66, 3006, 3005, 67, 68, 71, 64, 16, 20003, 20004, 20005}
# things that are not solid and stand against a wall on purpose: the wind and
# begin-anew plates, the press's switch, the lamps, the figures in a glass
# case, MAP16's weighbridge dial, MAP33's plates that wind (third.zs), MAP21's stream from a pipe (map21.zs),
# the kennel lab's scales (kennel.zs: their readout on the wall), MAP23's decor (dogs.zs: bowls, buckets, stores),
# a long cause's target (then.zs: 12 off its wall, radius 10, shot, never walked into)
ON_WALL = {20043, 20045, 20047, 20048, 20051, 20052, 20053, 20071, 20165, 20171, 20191, 20193, 20199, 20202, 20203,
           20182}
RADIUS = {3002: 30, 58: 30, 69: 24, 3003: 24, 3005: 31, 67: 48, 68: 64, 71: 31, 66: 20, 16: 40}
for t in m.things:
    x, y = t["x"], t["y"]
    s = sector_at(x + 0.5, y + 0.5)
    if not s:
        print(f"VOID thing {t['type']} at {x},{y}")
        bad += 1
        continue
    sec = m.sectors[s[0]]
    ty = t["args"][1] if t["type"] == 20169 else t["args"][0] if t["type"] == 20174 else t["type"]     # (a fallen thing, ajarthird.fallen, or a comer, ajarthird.comer: where its monster will stand)
    r = RADIUS.get(ty, 20 if ty in MONSTERS else 16)
    if t["type"] in (20001, 20002) or t["type"] in ON_WALL:
        continue
    for dx in (-r, 0, r):
        for dy in (-r, 0, r):
            o = sector_at(x + dx + 0.5, y + dy + 0.5)
            if not o:
                print(f"WALL thing {t['type']} at {x},{y} (radius {r}) reaches a wall")
                bad += 1
                break
            f = m.sectors[o[0]]["floor"]
            if abs(f - sec["floor"]) > 24 and ty in MONSTERS:
                print(f"EDGE thing {t['type']} at {x},{y} (radius {r}) hangs over a step of {f - sec['floor']}")
                break
        else:
            continue
        break


# --- pits ---------------------------------------------------------------------------
# A pit is a floor, or several joined by steps of no more than 24, with every
# floor around it more than 24 higher: what walks or falls in stays in. It is
# a problem when the player can get to it and nothing could take them out.
# - Got to: on foot (steps of 24 at most up, any drop down, 56 of headroom, not
#   through a line that blocks or carries a middle texture: a railing, bars, a
#   grille) from where the player starts or lands (things 1 to 4, 11, 14), from
#   a line with an id or a special (a frame, a portal, a door) or from a sector
#   with an id (a lift). Scenery that nobody gets to (a stage in an excerpt, a
#   horizon beyond a parapet) is so left alone.
# - Taken out: a sector of the pit has an id (a lift, a floor that moves), one
#   of its lines has a special or an id, or a thing in it has a special or is
#   where the player starts or lands.
# (2026-11-23: MAP18's desks on the upper floor were such pits, 216 deep.)
STEP, TALL, ARRIVE = 24, 56, (1, 2, 3, 4, 11, 14)


def shared(p, q):
    """The polygons p and q (or a line, as its two ends) have a piece of an
    edge in common."""
    for a, b in zip(p, p[1:] + p[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = dx * dx + dy * dy
        for c, d in zip(q, q[1:] + q[:1]):
            if dx * (c[1] - a[1]) - dy * (c[0] - a[0]) or dx * (d[1] - a[1]) - dy * (d[0] - a[0]):
                continue
            t = sorted((((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / n, ((d[0] - a[0]) * dx + (d[1] - a[1]) * dy) / n))
            if min(t[1], 1) - max(t[0], 0) > 1e-9:
                return True
    return False


def touch(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


near = {i: [] for i in range(len(polys))}
for i in range(len(polys)):
    for j in range(i + 1, len(polys)):
        if touch(boxes[i], boxes[j]) and shared(polys[i], polys[j]):
            near[i].append(j)
            near[j].append(i)


def along(lines):
    """For each sector, those of `lines` (ends, box) that run along its edge."""
    out = {i: set() for i in range(len(polys))}
    for n, (k, box) in enumerate(lines):
        for i in range(len(polys)):
            if touch(box, boxes[i]) and shared(k, polys[i]):
                out[i].add(n)
    return out


def boxed(keys):
    return [(list(k), (min(v[0] for v in k), min(v[1] for v in k), max(v[0] for v in k), max(v[1] for v in k))) for k in keys]


live = along(boxed(k for k, p in m.lineprops.items() if len(k) == 2 and (p.get("special") or p.get("id"))))
shut = along(boxed(k for k, p in m.lineprops.items() if len(k) == 2 and (p.get("blocking") or p.get("mid"))))
stood = {}                                   # sector: the things that count, standing in it
for t in m.things:
    if t.get("special") or t["type"] in ARRIVE:
        for i in sector_at(t["x"] + 0.5, t["y"] + 0.5):
            stood[i] = True
got = {i for i in range(len(polys)) if m.sectors[i]["id"] or live[i] or i in stood}
todo = list(got)
while todo:
    i = todo.pop()
    a = m.sectors[i]
    for j in near[i]:
        b = m.sectors[j]
        if (j not in got and b["floor"] - a["floor"] <= STEP and not shut[i] & shut[j]
                and min(a["ceil"], b["ceil"]) - max(a["floor"], b["floor"]) >= TALL):
            got.add(j)
            todo.append(j)

# --- lintels ------------------------------------------------------------------------
# A step down that cannot be taken. The engine lets a body down from a floor only
# when the whole of its box (32 by 32 for the player) is off that floor, and until
# then it must fit, at the upper floor's height, under every ceiling the box is
# under. So a step down is shut when, wherever along its edge the player comes
# off it, something within 40 beyond the edge has its ceiling less than 56 over
# the upper floor (40: the box and 8 to stop in; a landing of just 32 is a place
# nobody can stand still on): a lintel that comes down with the steps, a low doorway at the
# foot of a ledge. The same way up is open (from below the player fits), so it is
# a trap: in and never out. Looked at: every straight piece of edge (along x or y)
# between a floor the player gets to and a lower one, the player's box put just
# beyond it at every place along it. A place is shut by a lintel, shut by a wall
# (no floor there, a floor more than a step up, glass or scenery) or free; the
# edge is reported when no place is free and a lintel shuts at least one. Sectors
# with an id and sectors with no height (doors, lifts, floors that move) are left
# out.
# (2026-11-23: MAP19's link hall, floor 64, had a side door of two steps of 32
# under lintels at 136 and 112: Vadim walked in and could not walk out.)
BOX, LAND = 32, 40


def edge_pieces(p, q):
    """The straight pieces (along x or y) that the polygons p and q share:
    (axis, at, lo, hi), axis 0 for a piece along x at y = `at`."""
    out = []
    for a, b in zip(p, p[1:] + p[:1]):
        for axis in (0, 1):
            if a[1 - axis] != b[1 - axis] or a[axis] == b[axis]:
                continue
            for c, d in zip(q, q[1:] + q[:1]):
                if c[1 - axis] != a[1 - axis] or d[1 - axis] != a[1 - axis]:
                    continue
                lo, hi = max(min(a[axis], b[axis]), min(c[axis], d[axis])), min(max(a[axis], b[axis]), max(c[axis], d[axis]))
                if hi - lo >= BOX:
                    out.append((axis, a[1 - axis], lo, hi))
    return out


def lintels():
    n = 0
    moves = [bool(s["id"]) or s["floor"] == s["ceil"] for s in m.sectors]
    for i in sorted(got):
        hi_s = m.sectors[i]
        if moves[i]:
            continue
        for j in near[i]:
            lo_s = m.sectors[j]
            fh = hi_s["floor"]
            if (moves[j] or lo_s["floor"] >= fh or shut[i] & shut[j]
                    or min(hi_s["ceil"], lo_s["ceil"]) - fh < TALL):
                continue
            for axis, at, lo, hi in edge_pieces(polys[i], polys[j]):
                mid = (lo + hi) / 2
                pt = lambda along_, across: (along_, across) if axis == 0 else (across, along_)
                side = 1 if inside(polys[j], *pt(mid + 0.25, at + 0.5)) else -1
                reach = (lo, min(at, at + side * LAND), hi, max(at, at + side * LAND))
                reach = reach if axis == 0 else (reach[1], reach[0], reach[3], reach[2])
                cand = [k for k in range(len(polys)) if touch(reach, boxes[k])]
                free, low = 0, None
                c = lo + BOX / 2
                while c <= hi - BOX / 2:
                    wall, under, top = False, fh, []
                    for da in (-15.5, -8, 0.25, 8, 15.5):
                        for dd in (0.5, 8, 16, 24, 32, LAND - 0.5):
                            x, y = pt(c + da, at + side * dd)
                            k = next((k for k in cand if inside(polys[k], x, y)), None)
                            if k is None or k == i or m.sectors[k]["floor"] - fh > STEP or (k not in got and not moves[k]):
                                wall = True
                            elif not moves[k]:
                                under = max(under, m.sectors[k]["floor"])
                                top.append((m.sectors[k]["ceil"], k))
                    if not wall and top and min(top)[0] - under < TALL:
                        low = min(top)
                    elif not wall:
                        free += 1
                    c += 8
                if low and not free:
                    a, b = pt(lo, at), pt(hi, at)
                    print(f"LINTEL the step down from sector {i} (floor {fh}) to {j} (floor {lo_s['floor']}) at {a}-{b}: within "
                          f"{LAND} beyond it sector {low[1]} {boxes[low[1]]} has its ceiling at {low[0]}, less than {TALL} over "
                          f"the upper floor: the way down is shut")
                    n += 1
    return n


bad += lintels()

group = list(range(len(polys)))


def root(i):
    while group[i] != i:
        group[i] = group[group[i]]
        i = group[i]
    return i


for i, others in near.items():
    for j in others:
        if abs(m.sectors[i]["floor"] - m.sectors[j]["floor"]) <= STEP:
            group[root(i)] = root(j)
members = {}
for i in range(len(polys)):
    members.setdefault(root(i), []).append(i)
for g in members.values():
    rims = [m.sectors[j]["floor"] - m.sectors[i]["floor"] for i in g for j in near[i] if root(j) != root(i)]
    if not rims or min(rims) <= STEP or not got & set(g):
        continue
    if any(m.sectors[i]["id"] or live[i] or i in stood for i in g):
        continue
    print(f"PIT sectors {g} {[boxes[i] for i in g][:3]}: floor {sorted({m.sectors[i]['floor'] for i in g})}, "
          f"everything around {min(rims)} or more higher, and no way out")
    bad += 1


# --- slots ---------------------------------------------------------------------------
# A place a body 32 wide (the player) can stand in and one 48 wide cannot: a gap
# between furniture and a wall, a nook. The engine lets the player through 32
# exactly, but nobody steers through it, so nothing he might walk into is to be
# under 48. Looked at on a grid of 8: each cell takes its sector's floor and
# ceiling (a sector with floor == ceiling and an id is a door, taken as open,
# 128 high; no sector is void). A body of half-width r stands at a grid vertex
# when the cells under it have no void, 56 or more between the lowest ceiling
# and the highest floor (F(r), where it stands) and no blocking line runs
# through its inside. A SLOT is a vertex where r = 16 stands and no vertex
# within 8 has r = 24 standing within a step (24) of it; neighbouring ones are
# reported as one. Also a SLOT: a part cut off for the wider body, i.e. within
# one piece the narrow body walks (4-neighbours, steps of 24, no drops), the
# wider body's pieces, counted only where it stands as high as the narrow one
# (else the tops of furniture would count): every one but the largest.
# Things in the way are not looked at. On maps with slanting lines or corners
# off the grid of 8 the cells are taken by their middles and it is approximate.
# (2026-11-24: MAP19's drawing office could not be entered, its counter 32 from
# the wall across the way in; the second such place on that map.)
SG, NARROW, WIDE = 8, 16, 24
VOID = (-6000, -6000)                                               # ajarwater.VOID


def slots():
    n = 0
    pts = [p for poly in polys for p in poly]
    blocking = [tuple(k) for k, p in m.lineprops.items() if len(k) == 2 and p.get("blocking")]
    odd = any(p[0] % SG or p[1] % SG for p in pts) or any(
        a[0] != b[0] and a[1] != b[1] for poly in polys for a, b in zip(poly, poly[1:] + poly[:1])) or any(
        a[0] != b[0] and a[1] != b[1] for a, b in blocking)
    if odd:
        print("SLOT note: slanting lines or corners off the grid of 8 here: the slots are approximate")
    gx0 = int(min(p[0] for p in pts)) // SG * SG - 64
    gy0 = int(min(p[1] for p in pts)) // SG * SG - 64
    nx = (int(max(p[0] for p in pts)) - gx0) // SG + 16            # cells; the margin's are void
    ny = (int(max(p[1] for p in pts)) - gy0) // SG + 16
    VF, VC = 10 ** 9, -10 ** 9
    floor = [[VF] * nx for _ in range(ny)]
    ceil = [[VC] * nx for _ in range(ny)]
    h = SG / 2
    for poly, s in zip(polys, m.sectors):
        if all(VOID[1] <= p[1] <= VOID[1] + 32 and p[0] < VOID[0] + 4096 for p in poly):
            continue                                                # a basin's control sectors (ajarwater.basin), in the void
        f, c = s["floor"], s["ceil"]
        if f == c and s["id"]:
            c = f + 128
        edges = list(zip(poly, poly[1:] + poly[:1]))
        ylo, yhi = min(p[1] for p in poly), max(p[1] for p in poly)
        for j in range(max(0, int((ylo - gy0 - h) // SG)), min(ny, int((yhi - gy0) // SG) + 1)):
            yc = gy0 + j * SG + h
            xs = sorted(a[0] + (yc - a[1]) * (b[0] - a[0]) / (b[1] - a[1]) for a, b in edges if (a[1] > yc) != (b[1] > yc))
            fr, cr = floor[j], ceil[j]
            for xa, xb in zip(xs[::2], xs[1::2]):
                for i in range(max(0, -int(-(xa - gx0 - h) // SG)), min(nx, -int(-(xb - gx0 - h) // SG))):
                    fr[i], cr[i] = f, c
    wv, hv = nx + 1, ny + 1                                         # vertices; vertex i has cells i-1 and i on its sides

    def stand(r):
        """Flat lists over the vertices: F (the floor the body stands on) and ok."""
        k = r // SG
        pad = lambda row, v: [v] * k + row + [v] * k
        fx = [list(map(max, *[pad(row, VF)[t:t + wv] for t in range(2 * k)])) for row in floor]
        cx = [list(map(min, *[pad(row, VC)[t:t + wv] for t in range(2 * k)])) for row in ceil]
        fx = [[VF] * wv] * k + fx + [[VF] * wv] * k
        cx = [[VC] * wv] * k + cx + [[VC] * wv] * k
        F, ok = [], []
        for j in range(hv):
            fr = list(map(max, *fx[j:j + 2 * k]))
            cr = list(map(min, *cx[j:j + 2 * k]))
            F += fr
            ok += [cc - ff >= TALL for ff, cc in zip(fr, cr)]
        for a, b in blocking:                                       # no blocking line through the body's inside
            if a[0] == b[0] or a[1] == b[1]:
                segs = [(a, b)]
            else:                                                   # slanting: pieces of at most 4 along it
                steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) // 4) + 1
                q = [(a[0] + (b[0] - a[0]) * t / steps, a[1] + (b[1] - a[1]) * t / steps) for t in range(steps + 1)]
                segs = [(p, p) for p in q]
            for p, q in segs:
                x1, x2 = sorted((p[0], q[0]))
                y1, y2 = sorted((p[1], q[1]))
                # vertices whose open square of half-width r meets the segment
                i1, i2 = int((x1 - r - gx0) // SG) + 1, -int(-(x2 + r - gx0) // SG) - 1
                j1, j2 = int((y1 - r - gy0) // SG) + 1, -int(-(y2 + r - gy0) // SG) - 1
                for j in range(max(0, j1), min(hv, j2 + 1)):
                    for i in range(max(0, i1), min(wv, i2 + 1)):
                        ok[j * wv + i] = False
        return F, ok

    def pieces(F, ok):
        comp = [-1] * len(ok)
        sizes = []
        for s0 in [i for i, v in enumerate(ok) if v]:
            if comp[s0] >= 0:
                continue
            c = len(sizes)
            comp[s0] = c
            todo = [s0]
            size = 0
            while todo:
                s = todo.pop()
                size += 1
                f = F[s]
                for t in (s + 1, s - 1, s + wv, s - wv):            # the margin's vertices never stand: no wrap
                    if ok[t] and comp[t] < 0 and -STEP <= F[t] - f <= STEP:
                        comp[t] = c
                        todo.append(t)
            sizes.append(size)
        return comp

    F1, ok1 = stand(NARROW)
    F2, ok2 = stand(WIDE)
    d = (WIDE - NARROW) // SG
    near_ = [dj * wv + di for dj in range(-d, d + 1) for di in range(-d, d + 1)]
    slot = set()
    for s in [i for i, v in enumerate(ok1) if v]:
        f = F1[s]
        if not any(ok2[s + o] and -STEP <= F2[s + o] - f <= STEP for o in near_):
            slot.add(s)

    def box(group, grow):
        xs_, ys_ = [gx0 + s % wv * SG for s in group], [gy0 + s // wv * SG for s in group]
        return (min(xs_) - grow, min(ys_) - grow, max(xs_) + grow, max(ys_) + grow)

    seen = set()
    for s0 in sorted(slot):
        if s0 in seen:
            continue
        seen.add(s0)
        todo, group = [s0], []
        while todo:
            s = todo.pop()
            group.append(s)
            for t in (s + 1, s - 1, s + wv, s - wv):
                if t in slot and t not in seen:
                    seen.add(t)
                    todo.append(t)
        print(f"SLOT a body 32 wide stands in {box(group, NARROW)} (floor {F1[s0]}), one {2 * WIDE} wide nowhere there")
        n += 1
    c1, c2 = pieces(F1, ok1), pieces(F2, ok2)
    parts = {}
    for s in range(len(ok1)):
        if ok1[s] and ok2[s] and F1[s] == F2[s]:
            parts.setdefault(c1[s], {}).setdefault(c2[s], []).append(s)
    for p in parts.values():
        for part in sorted(p.values(), key=len, reverse=True)[1:]:
            print(f"SLOT cut off for a body {2 * WIDE} wide: its middle stands in {box(part, 0)} (floor {F2[part[0]]}), "
                  f"no way to it from the rest of where it walks but for one 32 wide")
            n += 1
    return n


bad += slots()

if len(sys.argv) > 2:
    im = gfx.Img(W, H, (16, 16, 24))
    floors = sorted({s["floor"] for s in m.sectors})
    for i, b in enumerate(boxes):
        if b[0] > 3000:
            continue
        sec = m.sectors[i]
        k = floors.index(sec["floor"]) / max(1, len(floors) - 1)
        c = (int(60 + 150 * k), int(70 + 100 * k), int(150 - 90 * k))
        if sec["floor"] == sec["ceil"]:
            c = (200, 120, 40)                      # a shut door
        if sec["special"] == 1024:
            c = (c[0], min(255, c[1] + 60), c[2])
        im.rect((b[0] - x0) // S + 1, H - (b[3] - y0) // S + 1, (b[2] - x0) // S, H - (b[1] - y0) // S, c)
    for t in m.things:
        if t["x"] > 3000:
            continue
        c = (255, 60, 60) if t["type"] in MONSTERS else (255, 255, 255) if t["type"] in (
            20001, 20002, 20011, 20012, 20013, 20014, 1) else (80, 255, 80)
        px, py = int(t["x"] - x0) // S, H - int(t["y"] - y0) // S
        im.rect(px - 1, py - 1, px + 2, py + 2, c)
    with open(sys.argv[2], "wb") as f:
        f.write(im.png())
print(f"{len(polys)} sectors, {len(m.things)} things, {sum(t['type'] in MONSTERS for t in m.things)} monsters, "
      f"{sum(s['special'] == 1024 for s in m.sectors)} secret sectors, {bad} problems")
