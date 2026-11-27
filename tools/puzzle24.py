"""MAP24 "Left Hanging": the door puzzle (PLAN.md, "MAP24 "Left Hanging": the
first version, as decided"), checked in the build as MAP21's to MAP23's.

    python3 tools/puzzle24.py              PUZZLE24: solution, states, stuck, lost
    python3 tools/puzzle24.py all          that, and the design's "To prove" lines, each by a variant

The endurance wing three times: NOW (the ruin), THEN (the 1960s, the doors on
test) and BEFORE (ten years before THEN: the wing's site, two yards under the
sky). Three doors: the clocked door (NOW and THEN; leans in the lobby NOW),
the ten-year door (THEN and BEFORE; hangs on test in 122 / 142 at the start)
and GREEN (hangs BEFORE in the first frame 141 at the start, so old GREEN
hangs THEN in 121 and NOW in 101 from the first tic). A door left hanging is
an old door at every later time (`old`). Regions NOW end in N, THEN in T,
BEFORE are the yards and the cellar; `exit` is the goal.

  hallN     the start: the lobby (frame 105, the clocked door leaning), the
            hall off it with bay C (frame 102), the wet bay E five steps down
            (the cistern, frame 103: filled by the valve), the hoist's shaft
            and the stair up to its top, the landing over the sump; the sump
            itself (a broken stair down to its bottom 128 under the hall),
            GREEN's far side NOW in the bottom's wall
  testN     the test room NOW (frame 101), open to the lobby only while a
            colour door hangs BEFORE in 141 (a cause that follows that frame);
            the brass door (keys 1 and 2) in its back wall to `exit`
  strongN   the strongroom NOW: frame 104 and no other way in; key 1
  galleryN  the gallery NOW, across the hoist's landing (there while the
            hoist was left up BEFORE); down is a drop into the shaft. A secret
  ledgeN    the sump's ledge, 112 over its bottom: key 2. Reached only by
            swimming, while the sump stands full (96 deep: the valve open THEN
            and GREEN hung at the wet bay's spot, 103 NOW, 123 THEN or 143
            BEFORE, its old self in the cistern NOW); down is a drop
  hallT     the lobby THEN (frame 125), the hall (bay C with the test rig,
            frame 122), the dry pump bay (frame 123), the hoist's stair
  testT     the test room THEN (frame 121), under ON TEST. DO NOT REMOVE.;
            open as testN
  strongT   the strongroom THEN: frame 124 only; the megasphere (a secret)
  galleryT  the gallery THEN across the landing: the valve
  storeT    GREEN's far side THEN: the store, locked for the night
  yardA     the site BEFORE: the first frame 141, pier 142
  yardB     the far yard BEFORE: piers 143 and 144 (the strongroom's ground),
            the hoist and its lever. No way between the yards
  cellarB   GREEN's far side BEFORE: the old building's cellar

The sump keeps its water when GREEN comes off (water.zs keeps no history) and
drains only through an old GREEN NOW in an outfall room: the solver asks for
the stricter condition, the link as it stands (what the player can be sure of).
"""
import copy
import sys

import solve
from ajarmap import GREEN, NAMES
from ajarthen import THEN_ID, CLOCKED, TENYEAR

NOW_FRAMES = {101: "testN", 102: "hallN", 103: "hallN", 104: "strongN", 105: "hallN"}
THEN_FRAMES = {121: "testT", 122: "hallT", 123: "hallT", 124: "strongT", 125: "hallT"}
BEFORE_FRAMES = {141: "yardA", 142: "yardA", 143: "yardB", 144: "yardB"}
A_FRAME = 141                                   # the first frame BEFORE: the test room follows it
SUMP_FULL = {"valve": "open", "hung": (GREEN, 103)}     # GREEN in 103, or old in 103 (hung in 123 or 143)
OPEN = {"hung": (GREEN, A_FRAME)}               # a colour door BEFORE in 141: GREEN is the only one

PUZZLE24 = dict(
    start="hallN", goal="exit", old=True, complete=True,
    names={**NAMES, CLOCKED: "the clocked door", TENYEAR: "the ten-year door"},
    frames={**NOW_FRAMES, **THEN_FRAMES, **BEFORE_FRAMES},
    twins={f: f + THEN_ID for f in NOW_FRAMES},
    befores={f: f + THEN_ID for f in THEN_FRAMES if f + THEN_ID in BEFORE_FRAMES},
    doors={CLOCKED: dict(clock=True, lean="hallN"),
           TENYEAR: dict(clock=True, span=1, frame=122),
           GREEN: dict(home="hallN", home_then="storeT", home_before="cellarB", frame=A_FRAME)},
    causes={"hoist": dict(states=("down", "up"), start="down", at=["yardB"]),
            "valve": dict(states=("shut", "open"), start="shut", at=["galleryT"])},
    walk=[
        ("hallN", "testN", "", None, OPEN), ("testN", "hallN", "", None, OPEN),     # the test room's mouth
        ("hallT", "testT", "", None, OPEN), ("testT", "hallT", "", None, OPEN),
        ("testN", "exit", "12"),                                                   # the brass door
        ("hallN", "galleryN", "", None, {"hoist": "up"}), ("galleryN", "hallN"),   # across the landing; a drop
        ("hallT", "galleryT", "", None, {"hoist": "up"}), ("galleryT", "hallT"),
        ("hallN", "ledgeN", "", None, SUMP_FULL), ("ledgeN", "hallN"),             # a swim; a drop
    ],
    keys={"1": "strongN", "2": "ledgeN"},
)


def variant(change):
    q = copy.deepcopy(PUZZLE24)
    change(q)
    q.pop("complete")
    return q


def no_hoist(q):
    q["causes"]["hoist"]["states"] = ("down",)


def no_valve(q):
    q["causes"]["valve"]["states"] = ("shut",)


def not_in(frame, door, also=None):
    """`door` never hangs in `frame` (every other door does); `also`: the twin's own list, where the frame's
    would hold for its twin too."""
    def change(q):
        every = tuple(sorted(q["doors"]))
        q.setdefault("only", {})[frame] = tuple(c for c in every if c != door)
        if also:
            q["only"][also] = every
    return change


def no_green_at_e(q):
    """GREEN at the wet bay's spot at no time (103, 123, 143)."""
    for f in (103, 123, 143):
        not_in(f, GREEN, None)(q)


VARIANTS = [
    ("without the hoist (it never goes up)", no_hoist),
    ("without the valve (it never opens)", no_valve),
    ("without GREEN left in 144", not_in(144, GREEN)),
    ("without GREEN left THEN in 123 (it may hang NOW in 103 or BEFORE in 143)", not_in(123, GREEN, also=103)),
    ("without GREEN at the wet bay's spot at any time (103, 123, 143)", no_green_at_e),
    ("without the ten-year door in 123 (143)", not_in(123, TENYEAR, also=103)),
    ("without the ten-year door in 144 (124)", not_in(144, TENYEAR)),
]


def reached(p, region):
    """After solve(p): the states the player's own moves reach in which he stands in `region`."""
    return [s for s in solve.solve.plain[0] if s[0] == region]


def where(p, s):
    return dict(zip(sorted(p["doors"]), s[2]))


def describe(p, s):
    here, carried, locs, keys, _, _, _, _, cs = s
    nm = p["names"]
    parts = [f"in {here}", f"holding {nm.get(carried, carried)}" if carried is not None else "empty hands"]
    for c, loc in zip(sorted(p["doors"]), locs):
        if c != carried:
            parts.append(f"{nm.get(c, c)} {'hung in' if loc[0] == 'frame' else 'leans in'} {loc[1]}")
    parts.append("keys " + ("".join(keys) or "none"))
    parts.append(" ".join(f"{n} {v}" for n, v in zip(sorted(p["causes"]), cs)))
    return "; ".join(parts)


def report(p, title, quiet=False):
    actions, steps, seen, stuck = solve.solve(p)
    print(f"== {title}: " + (f"solvable in {actions} door actions" if actions is not None else "NO SOLUTION")
          + f", {seen} states, {len(stuck)} stuck", flush=True)
    if actions is not None and not quiet:
        for st in steps:
            print("    " + st)
    if actions is not None:
        print("    can be lost for good: " + (", ".join(w for w, _ in solve.lost(p)) or "nothing"))
    for s in sorted(stuck, key=repr)[:5]:
        print("    stuck e.g.: " + describe(p, s))
    sys.stdout.flush()
    return actions


def to_prove():
    """The design's "To prove" lines: each a variant with no solution, or a fact of every state the player can
    bring about. Returns the lines that do not hold."""
    bad = []
    for title, change in VARIANTS:
        q = variant(change)
        n = report(q, title, quiet=True)
        if "ten-year door in 123" in title:
            gone = not reached(q, "yardB")
            print(f"    yard B reached: {'never' if gone else 'yes'}")
            if not gone:
                bad.append(title)
        elif "ten-year door in 144" in title:
            gone = not reached(q, "strongT")
            print(f"    the strongroom THEN (the megasphere) reached: {'never' if gone else 'yes'}")
            if not gone:
                bad.append(title)
        elif n is not None:
            bad.append(title)
    return bad


def clocked_only_now(q):
    """An option, not built: frame 103 takes only the clocked door NOW (ajarthen.clock_frame(when=(NOW,))), 123
    any door; old GREEN still hangs there (the old door rule asks no frame)."""
    q.setdefault("only", {}).update({103: (CLOCKED,), 123: tuple(sorted(q["doors"]))})


def main(args):
    report(PUZZLE24, "PUZZLE24 (MAP24 as decided)")
    if "all" in args:
        bad = to_prove()
        print("To prove: " + ("all hold" if not bad else "DO NOT HOLD: " + "; ".join(bad)))
        print("An option for the line that does not hold (not built): 103 the clocked door's alone NOW")
        report(variant(clocked_only_now), "  with it", quiet=True)
        report(variant(lambda q: (clocked_only_now(q), q["only"].update({123: (CLOCKED, TENYEAR)}))),
               "  with it, without GREEN left THEN in 123", quiet=True)


if __name__ == "__main__":
    main(sys.argv[1:])
