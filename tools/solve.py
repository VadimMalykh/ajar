"""Checks a level's door puzzle: solvable, how long, and no way to get stuck.

A puzzle is a dict:
  start, goal   region names
  walk          [(from, to)] one-way walking links (drops); add both ways if needed
                (a fixed doorway is one link each way). (from, to, keys) is a
                locked door: it needs every key in `keys` ("23" is keys 2 and 3)
  keys          optional {key name: region where it lies}
  frames        {frame line id: region}
  names         optional {colour: name} for the printed solution
  doors         {colour: dict(home=region, frame=id) or dict(home=region, lean=region)}

Regions are places you can walk around freely. Walking, picking up a key and
stepping through a hung door are free; pick up / hang / unhinge / swap cost
one action each. Keys are never lost.
"""
from collections import deque


def _moves(p, state):
    """Yields (cost, description, next state)."""
    here, carried, locs, keys = state
    colours = sorted(p["doors"])
    where = dict(zip(colours, locs))
    nm = lambda c: p.get("names", {}).get(c, c)

    def out(region=here, carry=carried, **change):
        w = dict(where)
        w.update({int(k[1:]): v for k, v in change.items()})
        return (region, carry, tuple(w[c] for c in colours), keys)

    for k, region in p.get("keys", {}).items():
        if region == here and k not in keys:
            yield 0, f"take key {k}", (here, carried, locs, tuple(sorted(keys + (k,))))
    for a, b, *need in p["walk"]:
        need = tuple(need[0]) if need else ()            # "23": keys 2 and 3
        if a == here and all(k in keys for k in need):
            yield 0, f"walk to {b}" + (f" (key {', '.join(need)})" if need else ""), out(region=b)
    hung = {loc[1]: c for c, loc in where.items() if loc[0] == "frame"}
    for f, c in hung.items():
        ends = (p["frames"][f], p["doors"][c]["home"])
        for a, b in (ends, ends[::-1]):
            if a == here and b != here:
                yield 0, f"through {nm(c)} to {b}", out(region=b)
    for c, loc in where.items():
        if loc == ("lean", here) and carried is None:
            yield 1, f"pick up {nm(c)}", out(carry=c, **{f"d{c}": ("carried",)})
    for f, region in p["frames"].items():
        if region != here:
            continue
        c = hung.get(f)
        if c is None and carried is not None:
            yield 1, f"hang {nm(carried)} in {f}", out(carry=None, **{f"d{carried}": ("frame", f)})
        elif c is not None and carried is None:
            yield 1, f"unhinge {nm(c)} from {f}", out(carry=c, **{f"d{c}": ("carried",)})
        elif c is not None:
            yield 1, f"swap {nm(c)} for {nm(carried)} in {f}", out(
                carry=c, **{f"d{c}": ("carried",), f"d{carried}": ("frame", f)})


def solve(p):
    """Returns (actions in the shortest solution, its steps, states seen, stuck states)."""
    colours = sorted(p["doors"])
    start = (p["start"], None, tuple(
        ("frame", d["frame"]) if "frame" in d else ("lean", d["lean"])
        for d in (p["doors"][c] for c in colours)), ())
    dist, prev, back = {start: 0}, {}, {}
    queue = deque([start])
    while queue:                                   # 0-1 BFS
        s = queue.popleft()
        if s[0] == p["goal"]:
            continue
        for cost, what, n in _moves(p, s):
            back.setdefault(n, []).append(s)
            if n not in dist or dist[s] + cost < dist[n]:
                dist[n] = dist[s] + cost
                prev[n] = (s, what)
                (queue.append if cost else queue.appendleft)(n)
    wins = [s for s in dist if s[0] == p["goal"]]
    if not wins:
        return None, [], len(dist), []
    alive, todo = set(wins), list(wins)
    while todo:
        for s in back.get(todo.pop(), ()):
            if s not in alive:
                alive.add(s)
                todo.append(s)
    stuck = [s for s in dist if s not in alive]
    best = min(wins, key=dist.get)
    steps, s = [], best
    while s in prev:
        s, what = prev[s]
        steps.append(what)
    steps.reverse()
    return dist[best], steps, len(dist), stuck
