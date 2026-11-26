"""MAP21 "In the Long Run": the door puzzle as designed (PLAN.md, "Levels 21
to 30"), checked before any map is built. PUZZLE21 is the design as given;
the variant_* functions beside it are changes tried against its stuck
states, and frozen() is the test that each long cause is needed.

    python3 tools/puzzle21.py              PUZZLE21: solution, states, stuck, lost
    python3 tools/puzzle21.py all          that, then every variant and the tests
    python3 tools/puzzle21.py frozen variant_pocket_now_clock_only    some of them

Each takes a few minutes (PUZZLE21: two million states). The solution printed
has the solver's number of door actions; its steps are a tidy one of that
length (the fewest steps too), since setting a cause costs no action.

Found (2026-11-26): solvable in 9; 2656 stuck states, all one way: a plain
door hung in 103 now while the clocked door is carried down the drop into
the pocket c1T, where it can hang nowhere (1103's twin is full) and cannot
go back up the squeeze. variant_pocket_now_clock_only removes them and keeps
every stage needed.

Regions NOW end in N (and the closets A, B, C), THEN in T; `exit` is the goal.
"""
import copy
import sys

import solve
from ajarmap import RED, BLUE, NAMES

CLOCK = 10                                      # the clocked door's key
NOW = (101, 102, 103, 104, 105, 106, 107, 108, 110, 111)     # the frames' now ids; then = now + 1000

PUZZLE21 = dict(
    start="hallN", goal="exit", names={**NAMES, CLOCK: "the clocked door"},
    frames={101: "hallN", 102: "hallN", 103: "spineN", 104: "spineN", 105: "spineN", 106: "spineN",
            107: "spineN", 108: "spineN", 110: "lobbyN", 111: "lobbyN",
            1101: "hallT", 1102: "hallT", 1103: "c1T", 1104: "spineT", 1105: "spineT", 1106: "spineT",
            1107: "spineT", 1108: "spineT", 1110: "lobbyT", 1111: "lobbyT"},
    twins={f: f + 1000 for f in NOW},
    only={101: CLOCK},                          # the machine's frame
    walk=[
        ("hallT", "c1T"),                                       # a drop: anything carried goes
        ("c1T", "hallT", "", "squeeze"), ("hallT", "c1T", "", "squeeze"),
        ("vestN", "hallN", "u"), ("hallN", "vestN", "u"),       # bolted from inside
        ("vestN", "spineN", "u"), ("spineN", "vestN", "u"),
        ("spineN", "vstoreN", "", None, {"valve": "shut"}), ("vstoreN", "spineN", "", None, {"valve": "shut"}),
        ("spineN", "vledgeN", "", None, {"valve": "open"}), ("vledgeN", "spineN", "", None, {"valve": "open"}),
        ("spineN", "bgalN", "", None, {"belt": "run"}), ("bgalN", "spineN"),       # up the heap; down is a drop
        ("spineN", "bcelN", "", None, {"belt": "stop"}), ("bcelN", "spineN", "", None, {"belt": "stop"}),
        ("spineN", "closetA", "", None, {"beam": "A"}), ("closetA", "spineN", "", None, {"beam": "A"}),
        ("spineN", "closetB", "", None, {"beam": "B"}), ("closetB", "spineN", "", None, {"beam": "B"}),
        ("spineN", "closetC", "", None, {"beam": "C"}), ("closetC", "spineN", "", None, {"beam": "C"}),
        ("hallT", "exit", "12", None, {"hung": (CLOCK, 101)}),
    ],
    causes=dict(
        valve=dict(states=("open", "shut"), start="open", at=["spineT"], via={105: "spineN"}),
        belt=dict(states=("stop", "run"), start="stop", at=["spineT"], via={108: "spineN"}),
        beam=dict(states=("off", "A", "B", "C"), start="C", at=["spineT"], via={106: "spineN", 107: "spineN"}),
    ),
    keys={"1": "lobbyT", "2": "vstoreN", "u": "vestN"},
    auto="u",                                   # the bolts are drawn on first arriving in the vestibule
    doors={
        CLOCK: dict(clock=True, frame=101),
        RED: dict(home="lobbyT", lean="bgalN"),
        BLUE: dict(home="vestN", lean="closetA"),
    },
)


# -- variants: each the smallest change tried against a family of stuck states

def frozen(name, p=PUZZLE21):
    """The puzzle with one long cause fixed at its start state."""
    q = copy.deepcopy(p)
    cz = q["causes"][name]
    cz["states"] = (cz["start"],)
    return q


def without_vestibule(p=PUZZLE21):
    """No way into the vestibule's bolted doors at all (BLUE's far side
    still opens into it): is the vestibule stage skippable?"""
    q = copy.deepcopy(p)
    q["walk"] = [w for w in q["walk"] if "vestN" not in w[:2]]
    return q


VARIANTS = {}


def variant(f):
    VARIANTS[f.__name__] = f
    return f


@variant
def variant_pocket_clock_only(p=PUZZLE21):
    """The pocket's frame (103, and so 1103) takes only the clocked door.

    Against the one family of stuck states: a plain door hung in 103 now
    fills that frame, so the clocked door brought down the drop into c1T
    can be hung nowhere there and cannot go back up the squeeze."""
    q = copy.deepcopy(p)
    q["only"] = {**q["only"], 103: CLOCK}
    return q


@variant
def variant_pocket_now_clock_only(p=PUZZLE21):
    """Only the now side of the pocket's frame (103) is the clocked door's.

    103 takes only the clocked door, 1103 (then, in the pocket) any door.
    variant_pocket_clock_only shuts in the pocket a plain door carried down
    the drop (it can hang nowhere there); here it hangs in 1103 and leads
    to its home. A plain door in 1103 does not shut the clocked door in
    either: it is carried through it, or swapped for it."""
    q = copy.deepcopy(p)
    q["only"] = {**q["only"], 103: CLOCK, 1103: tuple(sorted(q["doors"]))}
    return q


@variant
def variant_pocket_stair(p=PUZZLE21):
    """The pocket c1T gets back up to the hall then on foot, door in hand.

    The other way to the same end: the squeeze c1T -> hallT made a plain
    way (a stair), so the clocked door is never shut in the pocket; the
    hall then always has 1101, which takes only the clocked door."""
    q = copy.deepcopy(p)
    q["walk"] = [w for w in q["walk"] if w[:2] not in (("c1T", "hallT"), ("hallT", "c1T"))]
    q["walk"] += [("hallT", "c1T"), ("c1T", "hallT")]
    return q


@variant
def variant_shots_only(p=PUZZLE21):
    """Not a fix: the fixtures can be set only by a shot through the door.

    The causes lose `at`: in spineT the player can no longer walk up to the
    valve, the belt and the beam, so each has to be shot from now through
    the clocked door hung in its own frame (105, 108, 106 or 107), as in
    the expected solution. With the pocket's fix (variant_pocket_now_clock_only)."""
    q = variant_pocket_now_clock_only(p)
    for cz in q["causes"].values():
        cz["at"] = []
    return q


# -- printing

def nm(p, c):
    return p.get("names", {}).get(c, c)


def describe(p, s):
    here, carried, locs, keys, _, _, _, _, cs = s
    parts = [f"in {here}"]
    parts.append(f"holding {nm(p, carried)}" if carried is not None else "empty hands")
    tw = solve._twins(p)
    for c, loc in zip(sorted(p["doors"]), locs):
        if c == carried:
            continue
        if loc[0] == "frame":
            f = loc[1]
            where = f"{f}/{tw[f]}" if p["doors"][c].get("clock") else f"{f}"
            far = (f"{p['frames'][f]}<->{p['frames'][tw[f]]}" if p["doors"][c].get("clock")
                   else f"{p['frames'][f]}<->{p['doors'][c]['home']}")
            parts.append(f"{nm(p, c)} hung in {where} ({far})")
        else:
            parts.append(f"{nm(p, c)} leans in {loc[1]}")
    parts.append("keys " + ("".join(k for k in keys) or "none"))
    parts.append(", ".join(f"{n} {v}" for n, v in zip(sorted(p.get("causes", {})), cs)))
    return "; ".join(parts)


def tidy(p, targets):
    """{target: (steps, states)}: for each target state, a way there with the
    fewest door actions and, among those, the fewest steps (the solver's own
    shortest solution has the fewest actions but may wander at no cost).
    The target "won" is the first win found: any won state will do."""
    import heapq
    start = next(iter(solve.solve.plain[0]))     # the search's first state
    best, prev, todo, left = {start: (0, 0)}, {}, [((0, 0), 0, start)], set(targets)
    found = None
    n = 0
    while todo and left:
        d, _, s = heapq.heappop(todo)
        if best[s] < d:
            continue
        left.discard(s)
        if solve._won(p, s):
            if "won" in left:
                left.discard("won")
                found = s
            if s not in targets:
                continue
        for cost, what, m in solve._moves(p, s):
            e = (d[0] + cost, d[1] + 1)
            if m not in best or e < best[m]:
                best[m] = e
                prev[m] = (s, what)
                n += 1
                heapq.heappush(todo, (e, n, m))
    out = {}
    for t in targets:
        if t == "won":
            t = found
        steps, s = [], t
        while s in prev:
            s, what = prev[s]
            steps.append(what)
        out["won" if t is found else t] = (steps[::-1], [t] + [x for x in _back(prev, t)])
    return out


def _back(prev, s):
    while s in prev:
        s = prev[s][0]
        yield s


def family(p, s):
    """What a stuck state is, roughly: what fills the pocket's frame now
    (103) and then (1103), and where the clocked door is."""
    where = dict(zip(sorted(p["doors"]), s[2]))
    hung = solve._hung(p, where)
    clock = next(c for c in p["doors"] if p["doors"][c].get("clock"))
    plain = lambda f: nm(p, hung[f]) if f in hung and hung[f] != clock else "-"
    loc = where[clock]
    at = (f"carried, player in {s[0]}" if loc == ("carried",) else
          f"hung in {loc[1]}/{loc[1] + 1000}" if loc[0] == "frame" else f"leans in {loc[1]}")
    return f"103: {plain(103)}, 1103: {plain(1103)}, the clocked door {at}"


def stages(p, steps_states):
    """Which of the five stages a run of states goes through."""
    seen = {s[0] for s in steps_states}
    keys = set().union(*(set(s[3]) for s in steps_states))
    out = []
    out.append("cellar" if "vstoreN" in seen else "NO cellar")
    out.append("belt" if "bgalN" in seen else "NO belt")
    out.append("beam" if {"closetA", "closetB", "closetC"} & seen else "NO beam")
    out.append("lobby" if "lobbyT" in seen else "NO lobby")
    out.append("vestibule" if "u" in keys else "NO vestibule")
    return out


def report(p, title, examples=10, quiet=False, lose=True):
    """Solves p and prints: the solution (the solver's length; the steps of
    a tidy one of the same length), states, stuck states by family with an
    example of each, nearest first, and what lost() says."""
    from collections import defaultdict
    actions, steps, seen, stuck = solve.solve(p)
    dist_plain, _ = solve.solve.plain
    print(f"== {title}: " + (f"solvable in {actions} door actions" if actions is not None else "NO SOLUTION")
          + f", {seen} states, {len(stuck)} stuck", flush=True)
    if actions is None:
        return actions, seen, stuck
    fams = defaultdict(list)
    for s in stuck:
        fams[family(p, s)].append(s)
    eg = {f: min(ss, key=lambda s: (dist_plain.get(s, 10 ** 6), repr(s))) for f, ss in fams.items()}
    order = sorted(fams, key=lambda f: (dist_plain.get(eg[f], 10 ** 6), f))[:examples]
    ways = tidy(p, ["won"] + [eg[f] for f in order if eg[f] in dist_plain])
    best = "won"
    if not quiet:
        for st in ways[best][0]:
            print("    " + st)
    print("    stages: " + ", ".join(stages(p, ways[best][1])))
    if lose:
        gone = solve.lost(p)
        print(f"    can be lost for good: {', '.join(w for w, _ in gone) or 'nothing'}"
              + (" (every stuck state loses them)" if stuck else ""))
    if stuck:
        print(f"    {len(fams)} families of stuck states; the {len(order)} nearest, each with its nearest state:")
        for f in order:
            s = eg[f]
            print(f"      {f}: {len(fams[f])} states")
            print(f"        e.g. [{dist_plain.get(s)} actions] {describe(p, s)}")
            if s in ways:
                print("        by: " + "; ".join(ways[s][0]))
    sys.stdout.flush()
    return actions, seen, stuck


def main(args):
    """No argument: PUZZLE21. `all`: that, the causes frozen, the vestibule
    test and every variant. Or name any of: puzzle, frozen, vestibule and
    the variants."""
    want = set(args) if args and "all" not in args else (
        {"puzzle", "frozen", "vestibule", *VARIANTS} if args else {"puzzle"})
    if "puzzle" in want:
        report(PUZZLE21, "PUZZLE21 (MAP21 as designed)")
    if "frozen" in want:
        for name in ("valve", "belt", "beam"):
            report(frozen(name), f"PUZZLE21, the {name} frozen at {PUZZLE21['causes'][name]['start']}",
                   examples=2, quiet=True, lose=False)
    if "vestibule" in want:
        report(without_vestibule(), "PUZZLE21 without a way in by the vestibule's bolted doors", examples=2, lose=False)
    for name, f in VARIANTS.items():
        if name not in want:
            continue
        print()
        q = f()
        report(q, f"{name}: {f.__doc__.strip().splitlines()[0]}", examples=5)
        for c in ("valve", "belt", "beam"):
            report(frozen(c, q), f"{name}, the {c} frozen", examples=1, quiet=True, lose=False)
        report(without_vestibule(q), f"{name}, without a way in by the vestibule's bolted doors",
               examples=1, quiet=True, lose=False)


if __name__ == "__main__":
    main(sys.argv[1:])
