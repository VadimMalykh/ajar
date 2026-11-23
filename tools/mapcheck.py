"""Checks a level's geometry and draws it: python3 tools/mapcheck.py map_hinges6 [out.png]

Reports sectors that overlap, things that stand in no sector or in a sector
too low for them, things closer than 16 to a wall or a step they cannot
climb, and pits: floors with everything around them more than a step higher
and nothing that could take the player out again. The picture (4 map units to a pixel, north up) shows floors by
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
# case, MAP16's weighbridge dial
ON_WALL = {20043, 20045, 20047, 20048, 20051, 20052, 20053, 20071}
RADIUS = {3002: 30, 58: 30, 69: 24, 3003: 24, 3005: 31, 67: 48, 68: 64, 71: 31, 66: 20, 16: 40}
for t in m.things:
    x, y = t["x"], t["y"]
    s = sector_at(x + 0.5, y + 0.5)
    if not s:
        print(f"VOID thing {t['type']} at {x},{y}")
        bad += 1
        continue
    sec = m.sectors[s[0]]
    r = RADIUS.get(t["type"], 20 if t["type"] in MONSTERS else 16)
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
            if abs(f - sec["floor"]) > 24 and t["type"] in MONSTERS:
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
