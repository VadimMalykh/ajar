"""Checks a level's door puzzle: solvable, how long, and no way to get stuck.

A puzzle is a dict:
  start, goal   region names
  walk          [(from, to)] one-way walking links (drops); add both ways if needed
                (a fixed doorway is one link each way). (from, to, keys) is a
                locked door: it needs every key in `keys` ("23" is keys 2 and 3).
                (from, to, keys, "squeeze") is a way too small for a door:
                it needs empty hands as well (see "Squeezes" in PLAN.md)
  keys          optional {key name: region where it lies}
  auto          optional: the keys that are not keys but something that happens
                by itself on first coming to that region (a bolted door that
                opens as you arrive: see ajarmap.bolted). Use letters for them
  frames        {frame line id: region}
  names         optional {colour: name} for the printed solution
  doors         {colour: dict(home=region, frame=id) or dict(home=region, lean=region)
                or dict(home=region, thief=True): the thief starts with it}
  thief         optional dict(zone=region, sees=[regions]): one thief, which
                stays in `zone` and can see the player there and in `sees`

Regions are places you can walk around freely. Walking, picking up a key and
stepping through a hung door are free; pick up / hang / unhinge / swap cost
one action each. Keys are never lost.

The thief is not an opponent to be outplayed but a source of disorder: it may
at any time pick up a door leaning in its zone, hang the one it carries in an
empty frame there, and, while it can see the player, take a hung door down or
swap it. The player can kill it when in its zone; its door then leans there.
Every arrangement the two of them can produce is explored, and from each one
the player must be able to win by their own moves alone.
"""
from collections import deque


def _moves(p, state):
    """Yields (cost, description, next state)."""
    here, carried, locs, keys, thief = state
    colours = sorted(p["doors"])
    where = dict(zip(colours, locs))
    nm = lambda c: p.get("names", {}).get(c, c)

    def out(region=here, carry=carried, **change):
        w = dict(where)
        w.update({int(k[1:]): v for k, v in change.items()})
        return (region, carry, tuple(w[c] for c in colours), keys, thief)

    for k, region in p.get("keys", {}).items():
        if region == here and k not in keys:
            yield 0, f"take key {k}", (here, carried, locs, tuple(sorted(keys + (k,))), thief)
            if k in p.get("auto", ()):
                return                               # it happens by itself, before anything else
    for a, b, *more in p["walk"]:
        need = tuple(more[0]) if more else ()            # "23": keys 2 and 3
        if len(more) > 1 and carried is not None:        # a squeeze: no door fits
            continue
        if a == here and all(k in keys for k in need):
            yield 0, f"walk to {b}" + (f" (key {', '.join(need)})" if need else "") + (
                " (squeeze)" if len(more) > 1 else ""), out(region=b)
    if thief and here == p["thief"]["zone"]:
        loot = [c for c, loc in where.items() if loc == ("thief",)]
        w = dict(where)
        for c in loot:
            w[c] = ("lean", here)
        yield 0, "kill the thief" + (f" (it drops {nm(loot[0])})" if loot else ""), (
            here, carried, tuple(w[c] for c in colours), keys, 0)
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


def _thief(p, state):
    """Yields the states the thief can turn `state` into."""
    here, carried, locs, keys, thief = state
    if not thief:
        return
    t = p["thief"]
    colours = sorted(p["doors"])
    where = dict(zip(colours, locs))
    seen = here == t["zone"] or here in t.get("sees", ())

    def out(**change):
        w = dict(where)
        w.update({int(k[1:]): v for k, v in change.items()})
        return (here, carried, tuple(w[c] for c in colours), keys, thief)

    loot = next((c for c, loc in where.items() if loc == ("thief",)), None)
    if loot is None:
        for c, loc in where.items():
            if loc == ("lean", t["zone"]):
                yield out(**{f"d{c}": ("thief",)})
    hung = {loc[1]: c for c, loc in where.items() if loc[0] == "frame"}
    for f, region in p["frames"].items():
        if region != t["zone"]:
            continue
        c = hung.get(f)
        if c is None and loot is not None:
            yield out(**{f"d{loot}": ("frame", f)})
        elif c is not None and seen and loot is None:
            yield out(**{f"d{c}": ("thief",)})
        elif c is not None and seen:
            yield out(**{f"d{c}": ("thief",), f"d{loot}": ("frame", f)})


def _search(p, start, with_thief):
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
        if with_thief:
            for n in _thief(p, s):
                if n not in dist:                  # not in `back`: not the player's doing
                    dist[n] = dist[s]
                    queue.appendleft(n)
    return dist, prev, back


def solve(p):
    """Returns (actions in the shortest solution, its steps, states seen, stuck states).
    The solution is the player's alone (the thief does nothing in it); the
    states are everything player and thief can bring about between them."""
    colours = sorted(p["doors"])
    start = (p["start"], None, tuple(
        ("frame", d["frame"]) if "frame" in d else ("thief",) if d.get("thief") else ("lean", d["lean"])
        for d in (p["doors"][c] for c in colours)), (), 1 if p.get("thief") else 0)
    dist, prev, back = _search(p, start, False)
    wins = [s for s in dist if s[0] == p["goal"]]
    if not wins:
        return None, [], len(dist), []
    best = min(wins, key=dist.get)
    actions = dist[best]
    steps, s = [], best
    while s in prev:
        s, what = prev[s]
        steps.append(what)
    steps.reverse()
    if p.get("thief"):
        dist, prev, back = _search(p, start, True)
        wins = [s for s in dist if s[0] == p["goal"]]
    alive, todo = set(wins), list(wins)
    while todo:
        for s in back.get(todo.pop(), ()):
            if s not in alive:
                alive.add(s)
                todo.append(s)
    stuck = [s for s in dist if s not in alive]
    solve.back, solve.dist = back, dist            # for lost()
    return actions, steps, len(dist), stuck


def lost(p):
    """After solve(p): the places and keys that can be lost for good, as
    [(what, a state it cannot be reached from)]. A level where this is empty
    stays fully reachable whatever the player (and the thief) does, for
    those who want every kill, item and secret."""
    back, dist = solve.back, solve.dist
    live = [s for s in dist if s[0] != p["goal"]]
    regions = {p["start"]} | {r for link in p["walk"] for r in link[:2]} | set(p["frames"].values())
    for d in p["doors"].values():
        regions |= {d["home"]} | ({d["lean"]} if "lean" in d else set())
    if p.get("thief"):
        regions.add(p["thief"]["zone"])
    tests = [(r, lambda s, r=r: s[0] == r) for r in sorted(regions - {p["goal"]})]
    tests += [(f"key {k}", lambda s, k=k: k in s[3]) for k in sorted(p.get("keys", {}))]
    out = []
    for what, there in tests:
        ok = {s for s in dist if there(s)}
        todo = list(ok)
        while todo:
            for s in back.get(todo.pop(), ()):
                if s not in ok:
                    ok.add(s)
                    todo.append(s)
        bad = [s for s in live if s not in ok]
        if bad:
            out.append((what, bad[0]))
    return out
