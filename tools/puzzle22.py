"""MAP22 "Day Return": the door puzzle as designed (PLAN.md, "MAP22 'Day
Return': the first version, as decided"), checked before the map is built.

    python3 tools/puzzle22.py              PUZZLE22: solution, states, stuck, lost
    python3 tools/puzzle22.py all          that, and every variant

MAP10's square forty years earlier, by day, the bus new; and the same square
now, at night, the old bus. Regions THEN end in T, NOW in N. The goal is
hanging BLUE in the brass frame of the line's night room then (home_frame).

  sqT       the square then: the stop, the bus's two faces, the lane, the shelter
  hotelT    line 1 (a fixed doorway)        stationT  line 5 (a fixed doorway)
  theatreT  RED's far side then; its stage door drops into pitT, whose
            doorway is the bus's door 8
  depotT    YELLOW's far side then; the clocked door stands here; its wicket
            lets out into the lane, a step down, and never in
  lineT     the night room behind the shelter's brass door (keys 1 and 2):
            BLUE's far side then, and the brass frame HOME (BLUE's alone)
  sqN       the square now: MAP10's, at night, the old bus
  theatreN  RED's far side now (as in MAP10): BLUE leans here. pitN as then
  depotN    YELLOW's far side now (as in MAP10); its wicket as then
  lineN     the night room now: BLUE's far side, a hole down into the shelter

Frames. The bus then: 121 (door 2: RED hangs there at the start), 122 (door
7, in its back), 123 (door 6, brass, no twin), 124 (door 4). The old bus now:
MAP10's own 101 (door 2) and 102 (door 7), and 104 (door 4). 101/121 and
102/122 are twins and take any door at both times; 104/124 are twins and the
clocked door's alone. A colour door joins places, never times: hung on the
bus then it runs to its far side then, on the old bus now to the same place
now.

The turn and the keys. The first time the clocked door hangs, the times are
joined and what is now comes through: that is the turn. Nothing is to be had
from the districts before it: key 1 is carried by what then comes to the
hotel, key 2 by what comes to the theatre. Here: an automatic key "t", got
on first standing in sqN, opens hotelK and theatreK, where the keys lie. (In
the level the turn comes at the hanging, a free step earlier.)

As designed (2026-11-27): 8 door actions, 12437 states, 0 stuck, nothing lost;
the same without door 7's frames or without door 6's (`all`).
"""
import copy
import sys

import solve
from ajarmap import RED, BLUE, YELLOW, HOME, NAMES
from ajarthen import THEN_ID

CLOCK = 10                                      # the clocked door's key
F2, F7, F4 = 101, 102, 104                      # the old bus's frames now: doors 2, 7 and 4; then = + THEN_ID
F6 = 123                                        # door 6 of the bus then: no twin

PUZZLE22 = dict(
    start="sqT", goal="exit", names={**NAMES, CLOCK: "the clocked door"}, complete=True,
    frames={F2: "sqN", F7: "sqN", F4: "sqN",
            F2 + THEN_ID: "sqT", F7 + THEN_ID: "sqT", F4 + THEN_ID: "sqT", F6: "sqT", HOME: "lineT"},
    twins={f: f + THEN_ID for f in (F2, F7, F4)},
    then_frames=(F6, HOME),
    only={F4: CLOCK, F4 + THEN_ID: CLOCK, HOME: BLUE},
    home_frame=HOME,
    walk=[
        ("sqT", "hotelT"), ("hotelT", "sqT"),                   # line 1
        ("sqT", "stationT"), ("stationT", "sqT"),               # line 5
        ("theatreT", "pitT"), ("pitT", "sqT"), ("sqT", "pitT"),     # the stage door: a drop; door 8
        ("theatreN", "pitN"), ("pitN", "sqN"), ("sqN", "pitN"),
        ("depotT", "sqT"), ("depotN", "sqN"),                   # the wicket: a step down, never in
        ("lineN", "sqN"),                                       # the hole over the shelter
        ("sqT", "lineT", "12"), ("lineT", "sqT", "12"),         # the shelter's brass door
        ("hotelT", "hotelK", "t"), ("hotelK", "hotelT", "t"),   # what the turn brings to the hotel has key 1
        ("theatreT", "theatreK", "t"), ("theatreK", "theatreT", "t"),
    ],
    keys={"1": "hotelK", "2": "theatreK", "t": "sqN"},
    auto="t",
    doors={
        CLOCK: dict(clock=True, lean="depotT"),
        RED: dict(home="theatreN", home_then="theatreT", frame=F2 + THEN_ID),
        YELLOW: dict(home="depotN", home_then="depotT", lean="stationT"),
        BLUE: dict(home="lineN", home_then="lineT", lean="theatreN"),
    },
)


def without_frame(f, p=PUZZLE22):
    """p without a frame (a now id: its twin too): is it needed?"""
    q = copy.deepcopy(p)
    for x in (f, q["twins"].pop(f, None)):
        if x is not None:
            q["frames"].pop(x)
    q["then_frames"] = tuple(x for x in q["then_frames"] if x != f)
    return q


def no_pit(p=PUZZLE22):
    """The theatre with no way out but RED, at both times."""
    q = copy.deepcopy(p)
    q["walk"] = [w for w in q["walk"] if not {"pitT", "pitN"} & set(w[:2])]
    return q


def describe(p, s):
    here, carried, locs, keys, _, _, _, _, cs = s
    parts = [f"in {here}", f"holding {p['names'].get(carried, carried)}" if carried is not None else "empty hands"]
    for c, loc in zip(sorted(p["doors"]), locs):
        if c != carried:
            parts.append(f"{p['names'].get(c, c)} {'hung in' if loc[0] == 'frame' else 'leans in'} {loc[1]}")
    parts.append("keys " + ("".join(keys) or "none"))
    return "; ".join(parts)


def report(p, title, quiet=False):
    actions, steps, seen, stuck = solve.solve(p)
    print(f"== {title}: " + (f"solvable in {actions} door actions" if actions is not None else "NO SOLUTION")
          + f", {seen} states, {len(stuck)} stuck", flush=True)
    if actions is None:
        return
    if not quiet:
        for st in steps:
            print("    " + st)
    print("    can be lost for good: " + (", ".join(w for w, _ in solve.lost(p)) or "nothing"))
    for s in sorted(stuck, key=repr)[:5]:
        print("    stuck e.g.: " + describe(p, s))
    sys.stdout.flush()


def main(args):
    report(PUZZLE22, "PUZZLE22 (MAP22 as designed)")
    if "all" in args:
        report(no_pit(), "the theatre with no way out but RED", quiet=True)
        for f in (F7, F6):                      # (RED hangs in door 2's at the start)
            report(without_frame(f), f"without frame {f}", quiet=True)


if __name__ == "__main__":
    main(sys.argv[1:])
