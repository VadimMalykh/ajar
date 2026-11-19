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
                A leaf of a Pair (ajarmap.pair) has no home: dict(pair=the
                other leaf's key, lean=region or frame=id). The two leaves
                have keys of their own (ajarmap.LEAVES), not their colour.
                Hung both, each frame leads to the other; one alone is shut
  thief         optional dict(zone=region, sees=[regions]): one thief, which
                stays in `zone` and can see the player there and in `sees`
  nailer        optional dict(zone=region or [regions]): one nailer, which can
                walk to the frames in those regions. (region, key) in the
                list: only once the player has that key (a gate that opens)
  home_frame    optional frame id (ajarmap.way_home): the level is also won by
                hanging in it the door whose home is that frame's region
                (or the door `home_door`, where a grille parts the two;
                the search then goes on past that, with the door fixed)
  home_chain    optional dict(frames=[two frame ids], doors=[two colours])
                (ajarmap.way_through): the level is won when those two doors
                hang in those two frames, either way round. With
                level=n, only while the lift stands at floor n as well: one
                of the frames is in the car, the other on that landing, and
                they face each other only there (MAP14). With
                secret=dict(frame=id, door=colour) (ajarmap.way_longer) there
                is a longer loop as well, and a secret way out: that door
                and one of the two in the two frames, the other of the two
                in the frame `secret` names. It is won too, and lost() says
                if it can ever be put out of reach
  pool          optional [regions] of the level's stray places, which only a
                Stray door opens onto (it may also open onto the far side
                of a coloured door). The Stray doors themselves are not
                listed: see below
  only          optional {frame id: colour, or a tuple of colours}: no other
                door hangs in that frame
  dash          optional dict(at=region, to=region, limit=units, legs={(a, b):
                units}): a way that a lever in `at` opens for a few seconds
                (ajarmap.shutter). Whatever is carried gets from `at` to `to`
                if a route from "lever" to "shutter" is no longer than
                `limit`. A leg is a stretch that can be run with a door in
                hand, one way; its ends are "lever", "shutter", a frame's
                line id or a far side's (200 + colour). A hung door joins
                its frame and its far side
  lift          optional dict(car=region, floors=[the region of each landing,
                from the bottom], buttons={region: (the floors a button
                there sends the car to)}, at=the floor it starts on, 0 if
                not given) (ajarmap.lift_button): one lift. The car is a
                region like any other, with frames and far sides of its
                own, and is joined on foot to the landing it stands at.
                Sending it costs nothing, and a door rides in it
  sights        optional {key (a letter): what sets it off} (ajarmap.target):
                something that is shot, and opens steel doors (walk links
                that need that key) for good. dict(through=door): a target
                in that door's home, shot from wherever the door hangs, so
                the player has to be in that frame's region.
                dict(at=region, lines=[{door: (frames it may hang in)}]): an
                emitter's button in `at`, and the arrangements of doors,
                any one of which puts its beam on the sensor
A door with barred=True (a rail before its far side) is never walked through.

Regions are places you can walk around freely. Walking, picking up a key and
stepping through a hung door are free; pick up / hang / unhinge / swap cost
one action each. Keys are never lost.

The thief is not an opponent to be outplayed but a source of disorder: it may
at any time pick up a door leaning in its zone, hang the one it carries in an
empty frame there, and, while it can see the player, take a hung door down or
swap it. The player can kill it when in its zone; its door then leans there.
Every arrangement the two of them can produce is explored, and from each one
the player must be able to win by their own moves alone.

The nailer is the same kind of thing. While it lives, a door hanging in a
frame in its zone may or may not be nailed, so taking it down or swapping it
there is luck: it can happen, but no win may depend on it. The player, in
its zone, can kill it. (Which doors are nailed is not kept: that would
multiply the states by every subset of doors.)

So is a dash that is not sure: a quicker runner may get through with any
arrangement of doors, so from `at` the player may find themselves in `to`
with whatever they carry, but no win may depend on it.

So is a Stray door's draw. With empty hands (that is, perhaps holding a Stray
door: they are not counted, and a level may have any number) in a place with
a frame, the player may at any time find themselves in any place of the
pool, or at the far side of any door that hangs nowhere just then: with empty hands, or with a door that leant nearby, if the frame was
empty; with the door that hung there, and the frame empty, if it was not.
The printed solution uses no Stray door, and no win may depend on a draw.
"""
from collections import deque


def _moves(p, state, nailed=False):
    """Yields (cost, description, next state): what the player can be sure
    of doing. With `nailed`, instead, only what they can do if the nailer
    has not got there first."""
    here, carried, locs, keys, thief, nails, car = state
    colours = sorted(p["doors"])
    where = dict(zip(colours, locs))
    nm = lambda c: p.get("names", {}).get(c, c)

    def out(region=here, carry=carried, at=car, **change):
        w = dict(where)
        w.update({int(k[1:]): v for k, v in change.items()})
        return (region, carry, tuple(w[c] for c in colours), keys, thief, nails, at)

    for k, region in p.get("keys", {}).items():
        if region == here and k not in keys:
            yield 0, f"take key {k}", (here, carried, locs, tuple(sorted(keys + (k,))), thief, nails, car)
            if k in p.get("auto", ()):
                return                               # it happens by itself, before anything else
    for a, b, *more in p["walk"]:
        need = tuple(more[0]) if more else ()            # "23": keys 2 and 3
        if len(more) > 1 and carried is not None:        # a squeeze: no door fits
            continue
        if a == here and all(k in keys for k in need):
            yield 0, f"walk to {b}" + (f" (key {', '.join(need)})" if need else "") + (
                " (squeeze)" if len(more) > 1 else ""), out(region=b)
    if thief & 1 and here == p["thief"]["zone"]:
        loot = [c for c, loc in where.items() if loc == ("thief",)]
        w = dict(where)
        for c in loot:
            w[c] = ("lean", here)
        yield 0, "kill the thief" + (f" (it drops {nm(loot[0])})" if loot else ""), (
            here, carried, tuple(w[c] for c in colours), keys, 0, nails, car)
    if nails and here in _zone(p["nailer"], keys):
        yield 0, "kill the nailer", (here, carried, locs, keys, thief, 0, car)
    for k, sg in p.get("sights", {}).items():
        if k in keys:
            continue
        if "through" in sg:
            loc = where[sg["through"]]
            ok = loc[0] == "frame" and p["frames"][loc[1]] == here
        else:
            ok = here == sg["at"] and any(all(where[c][0] == "frame" and where[c][1] in fs for c, fs in alt.items())
                                          for alt in sg["lines"])
        if ok:
            yield 0, sg.get("say", f"set off {k}"), (here, carried, locs, tuple(sorted(keys + (k,))), thief, nails, car)
    lift = p.get("lift")
    if lift:
        stops = lift["floors"]
        if here == lift["car"]:
            yield 0, f"out of the lift to {stops[car]}", out(region=stops[car])
        elif here == stops[car]:
            yield 0, "into the lift", out(region=lift["car"])
        for n in lift["buttons"].get(here, ()):
            if n != car:
                yield 0, f"send the lift to {stops[n]}", out(at=n)
    hung = {loc[1]: c for c, loc in where.items() if loc[0] == "frame"}
    dash = p.get("dash")
    if dash and here == dash["at"] and _run(dash, hung) <= dash["limit"]:
        yield 0, f"pull the lever and run to {dash['to']}", out(region=dash["to"])
    for f, c in hung.items():
        twin = p["doors"][c].get("pair")
        if twin is not None:                         # a Pair: to the frame its twin hangs in, if it hangs
            if where[twin][0] != "frame" or twin < c:
                continue
            ends = (p["frames"][f], p["frames"][where[twin][1]])
        elif p["doors"][c].get("barred"):
            continue                                 # a rail before its far side: shots and sight, no walking
        else:
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
        if c is not None and f == p.get("home_frame") and c == p.get("home_door"):
            continue                                 # the way out, built: it stays
        takes = p.get("only", {}).get(f, carried)
        sec = p.get("home_chain", {}).get("secret", {})
        if carried is not None and f == sec.get("frame") and carried == sec.get("door"):
            continue                                 # a longer chain's third door, in its own room: it would open onto itself
        if carried is not None and carried not in (takes if isinstance(takes, tuple) else (takes,)):
            continue                                 # a frame that takes one door only, or two
        if c is None and carried is not None:
            yield 1, f"hang {nm(carried)} in {f}", out(carry=None, **{f"d{carried}": ("frame", f)})
        elif c is not None and bool(nails and region in _zone(p["nailer"], keys)) != nailed:
            continue                                 # it may be nailed: see _luck
        elif c is not None and carried is None:
            yield 1, f"unhinge {nm(c)} from {f}", out(carry=c, **{f"d{c}": ("carried",)})
        elif c is not None:
            yield 1, f"swap {nm(c)} for {nm(carried)} in {f}", out(
                carry=c, **{f"d{c}": ("carried",), f"d{carried}": ("frame", f)})


DOOR_STEP = 64      # what stepping through a hung door adds to a run


def _run(dash, hung):
    """The shortest run from the lever to the shutter, in map units, by the
    legs of `dash` and the doors that hang (`hung`: {frame id: colour})."""
    best, todo = {"lever": 0}, ["lever"]
    while todo:
        a = todo.pop()
        steps = [(y, d) for (x, y), d in dash["legs"].items() if x == a]
        steps += [(200 + c, DOOR_STEP) for f, c in hung.items() if f == a and c not in dash.get("pairs", {})]
        steps += [(f, DOOR_STEP) for f, c in hung.items() if 200 + c == a and c not in dash.get("pairs", {})]
        twins = {c: f for f, c in hung.items()}      # a Pair, both leaves hung: frame to frame
        steps += [(twins[dash["pairs"][c]], DOOR_STEP) for f, c in hung.items()
                  if f == a and dash.get("pairs", {}).get(c) in twins]
        for b, d in steps:
            if best[a] + d < best.get(b, 1e9):
                best[b] = best[a] + d
                todo.append(b)
    return best.get("shutter", 1e9)


def _zone(who, keys):
    z = who["zone"]
    z = (z,) if isinstance(z, str) else tuple(z)
    return tuple(r if isinstance(r, str) else r[0] for r in z if isinstance(r, str) or r[1] in keys)


def _chain(p, s):
    """0, or the length of the loop of doors that runs through the night
    room: 2 (the way out) or 3 (the secret one). See home_chain."""
    chain = p.get("home_chain")
    if not chain:
        return 0
    if chain.get("level", s[6]) != s[6]:
        return 0                                     # the car is not level with the other brass frame
    where = dict(zip(sorted(p["doors"]), s[2]))
    brass = {("frame", f) for f in chain["frames"]}
    a, b = chain["doors"]
    if {where[a], where[b]} == brass:
        return 2
    more = chain.get("secret")
    if more and where[more["door"]] in brass:
        for x, y in ((a, b), (b, a)):
            if where[x] in brass and where[y] == ("frame", more["frame"]):
                return 3
    return 0


def _won(p, s):
    if s[0] == p["goal"]:
        return True
    if p.get("home_chain"):
        return _chain(p, s) > 0
    f = p.get("home_frame")
    if f is None:
        return False
    return any(loc == ("frame", f) and (c == p["home_door"] if "home_door" in p
                                        else p["doors"][c].get("home") == p["frames"][f])
               for c, loc in zip(sorted(p["doors"]), s[2]))


def _luck(p, state):
    """Yields the states that the nailer being slow, or the draw of a Stray
    door, can turn `state` into."""
    here, carried, locs, keys, thief, nails, car = state
    if nails:
        for _, _, n in _moves(p, state, True):
            yield n
    if p.get("dash") and here == p["dash"]["at"]:
        yield (p["dash"]["to"],) + state[1:]
    if carried is not None or not p.get("pool"):
        return
    colours = sorted(p["doors"])
    where = dict(zip(colours, locs))
    hung = {loc[1]: c for c, loc in where.items() if loc[0] == "frame"}
    for f, region in p["frames"].items():
        if region != here:
            continue
        hands = [hung.get(f)]                       # what was swapped out, or nothing...
        if hands[0] is None:                         # ...or a door snatched up on the way
            hands += [c for c, loc in where.items() if loc == ("lean", here)]
        for c in hands:
            w = dict(where)
            if c is not None:
                w[c] = ("carried",)
            # the pool: the level's stray places, and the far side of every
            # door that hangs nowhere
            # (but not the room of a longer chain's third door: ajarmap.way_longer)
            shut = p.get("home_chain", {}).get("secret", {}).get("door")
            for place in sorted(set(p["pool"]) | {p["doors"][k]["home"] for k in colours if w[k][0] != "frame" and k != shut and "home" in p["doors"][k]}):
                yield (place, c, tuple(w[k] for k in colours), keys, thief, nails, car)


def _thief(p, state):
    """Yields the states the thief can turn `state` into."""
    here, carried, locs, keys, thief, nails, car = state
    if not thief & 1:
        return
    t = p["thief"]
    colours = sorted(p["doors"])
    where = dict(zip(colours, locs))
    seen = here == t["zone"] or here in t.get("sees", ())

    def out(**change):
        w = dict(where)
        w.update({int(k[1:]): v for k, v in change.items()})
        return (here, carried, tuple(w[c] for c in colours), keys, thief, nails, car)

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


def _search(p, start, with_luck):
    dist, prev, back = {start: 0}, {}, {}
    queue = deque([start])
    while queue:                                   # 0-1 BFS
        s = queue.popleft()
        if _won(p, s) and (s[0] == p["goal"] or "home_door" not in p):
            continue                               # (with home_door the player may go on: see lost())
        for cost, what, n in _moves(p, s):
            back.setdefault(n, []).append(s)
            if n not in dist or dist[s] + cost < dist[n]:
                dist[n] = dist[s] + cost
                prev[n] = (s, what)
                (queue.append if cost else queue.appendleft)(n)
        if with_luck:
            for n in list(_thief(p, s)) + list(_luck(p, s)):
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
        for d in (p["doors"][c] for c in colours)), (), 1 if p.get("thief") else 0,
        0, p.get("lift", {}).get("at", 0))
    # the solution: the thief and the nailer do nothing in it, and no Stray door is used
    dist, prev, back = _search(p, start, False)
    wins = [s for s in dist if _won(p, s)]
    solve.plain = dist, prev                       # for secret()
    if not wins:
        return None, [], len(dist), []
    best = min(wins, key=dist.get)
    actions = dist[best]
    steps, s = [], best
    while s in prev:
        s, what = prev[s]
        steps.append(what)
    steps.reverse()
    if p.get("thief") or p.get("nailer") or p.get("pool") or p.get("dash"):
        dist, prev, back = _search(p, start[:5] + (1 if p.get("nailer") else 0,) + start[6:], True)
        wins = [s for s in dist if _won(p, s)]
    alive, todo = set(wins), list(wins)
    while todo:
        for s in back.get(todo.pop(), ()):
            if s not in alive:
                alive.add(s)
                todo.append(s)
    stuck = [s for s in dist if s not in alive]
    solve.back, solve.dist = back, dist            # for lost()
    return actions, steps, len(dist), stuck


def secret(p):
    """After solve(p): (actions, steps) of the shortest way to the secret way
    out of a `home_chain` that has one, by the player's moves alone; or
    (None, [])."""
    dist, prev = solve.plain
    ends = [s for s in dist if _chain(p, s) == 3]
    if not ends:
        return None, []
    s = min(ends, key=dist.get)
    actions, steps = dist[s], []
    while s in prev:
        s, what = prev[s]
        steps.append(what)
    return actions, steps[::-1]


def lost(p):
    """After solve(p): the places and keys that can be lost for good, as
    [(what, a state it cannot be reached from)]. A level where this is empty
    stays fully reachable whatever the player (and the thief) does, for
    those who want every kill, item and secret. With `home_door` a way out
    that has been built is not the end: the player may still go anywhere
    they can with that door fixed in its frame, so having had to build it
    to get out of somewhere loses nothing."""
    back, dist = solve.back, solve.dist
    live = [s for s in dist if not _won(p, s)]
    regions = {p["start"]} | {r for link in p["walk"] for r in link[:2]} | set(p["frames"].values())
    regions |= set(p.get("pool", ()))
    for d in p["doors"].values():
        regions |= ({d["home"]} if "home" in d else set()) | ({d["lean"]} if "lean" in d else set())
    if p.get("thief"):
        regions.add(p["thief"]["zone"])
    tests = [(r, lambda s, r=r: s[0] == r) for r in sorted(regions - {p["goal"]})]
    tests += [(f"key {k}", lambda s, k=k: k in s[3]) for k in sorted(set(p.get("keys", {})) | set(p.get("sights", {})))]
    if p.get("home_chain", {}).get("secret"):
        tests.append(("the secret way out", lambda s: _chain(p, s) == 3))
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
