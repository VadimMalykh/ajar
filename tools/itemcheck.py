"""Things to pick up that the player cannot get to:
python3 tools/itemcheck.py map_hinges3 ... (in the ajar-tools image, from the project root)

Walks the level from the player's start, from every line that has an id or a
special (a frame, a recess, a room door: a hung door or a switch may bring
the player there) and from every tagged sector, stepping up 24 at most and
down any drop; ceilings are not looked at. A pickup in a sector never walked
into is reported, unless it can be touched from a walked one beside it
(no more than the player's height above it, and less than 20 in from the
edge between them: the player's middle stays 16 short of a step he cannot
climb, and he touches what is within 36 of it).
"""
import importlib, sys
sys.path.insert(0, "tools")
import ajarmap
from udmf import MONSTERS

SKIP = set(MONSTERS) | set(ajarmap.SCENERY_T) | {1, 2, 3, 4, 11, 14, 9001, 9024, 9025, ajarmap.AMBUSH_T, ajarmap.LINE_T,
                                                 ajarmap.LIFT_T, 20003, 20004, 20005,
                                                 20132, 20133,   # the pass's desks and registers (pass.zs): plates, not pickups
                                                 20169,          # a fallen thing (ajarthird.fallen): a monster, not a pickup
                                                 20173, 20174, 20175,   # a common place, its comers (monsters) and ways (ajarthird.common)
                                                 20195, 20196, 20197, 20198,   # MAP21's apparatus (apparatus.zs): sprites, not pickups
                                                 20199, 20202, 20203}   # MAP23's decor (dogs.zs, dogs23.py): sprites, not pickups


def inside(poly, x, y):
    n = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            n = not n
    return n


def edge_dist(a, b, x, y):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
    return max(abs(a[0] + t * dx - x), abs(a[1] + t * dy - y))


total = 0
for name in sys.argv[1:]:
    m = importlib.import_module(name).m
    polys = m._split()
    F = [s["floor"] for s in m.sectors]
    edges = {}
    for i, p in enumerate(polys):
        for a, b in zip(p, p[1:] + p[:1]):
            edges.setdefault(frozenset((a, b)), []).append(i)
    near = {i: set() for i in range(len(polys))}
    for who in edges.values():
        for i in who:
            near[i] |= set(who) - {i}

    def on(key, e):                                  # the edge e is part of the line `key`
        (a, b), pts = tuple(key), tuple(e)
        return all((b[0] - a[0]) * (p[1] - a[1]) == (b[1] - a[1]) * (p[0] - a[0]) and
                   min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]) for p in pts)

    def at(x, y):
        for i, p in enumerate(m.polys):
            if inside(p, x + .5, y + .5):
                return i

    seeds = {at(t["x"], t["y"]) for t in m.things if t["type"] == 1}
    seeds |= {i for i, s in enumerate(m.sectors) if s["id"]}
    marked = [k for k, pr in m.lineprops.items() if len(k) == 2 and (pr.get("id") or pr.get("special"))]
    for e, who in edges.items():
        if any(on(k, e) for k in marked):
            seeds |= set(who)
    seeds.discard(None)
    seen, todo = set(seeds), list(seeds)
    while todo:
        i = todo.pop()
        for j in near[i]:
            if j not in seen and F[j] <= F[i] + 24:
                seen.add(j)
                todo.append(j)
    bad = 0
    for t in m.things:
        if t["type"] in SKIP or t["type"] == ajarmap.DOOR_T:
            continue
        i = at(t["x"], t["y"])
        if i is None or i in seen:
            continue
        ok = [e for e, who in edges.items() if i in who and edge_dist(*e, t["x"], t["y"]) < 20 and
              any(j in seen and 0 <= F[i] - F[j] < 56 for j in who)]
        if ok:
            continue
        low = [F[i] - F[j] for j in near[i] if j in seen]
        print(name, "OUT OF REACH", t["type"], (t["x"], t["y"]), "floor", F[i],
              f"({min(low)} above the floor beside it)" if low else "(nothing walked beside it)")
        bad += 1
    total += bad
    print(name, "items check:", bad, "problems")
sys.exit(1 if total else 0)
