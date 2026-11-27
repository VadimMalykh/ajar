"""MAP22 "Day Return": the door puzzle as designed (PLAN.md, "MAP22 'Day
Return': the first version, as decided" and "MAP22: BLUE's ambush with an
arch-vile; the way out is gated"), checked before the map is built.

    python3 tools/puzzle22.py              PUZZLE22: solution, states, stuck, lost
    python3 tools/puzzle22.py all          that, and every variant

MAP10's square forty years earlier, by day, the bus new; and the same square
now, at night, the old bus. Regions THEN end in T, NOW in N. The goal is
hanging BLUE in the brass frame of the line's night room then (home_frame,
home_door: the gate parts the frame from BLUE's far side).

  sqT       the square then: the stop, the bus's two faces, the lane, the shelter
  hotelT    line 1 (a fixed doorway)        stationT  line 5 (a fixed doorway)
  theatreT  RED's far side then; its stage door drops into pitT, whose
            doorway is the bus's door 8
  depotT    YELLOW's far side then; the clocked door stands here; its wicket
            lets out into the lane, a step down, and never in
  lineT     the night room then, west of the gate, behind the shelter's brass
            door (keys 1 and 2): BLUE's far side then, the stair's landing
  lineE     the night room then, east of the gate: the brass frame HOME
            (BLUE's alone) and frame 125. The gate is a bolted door, the bolt
            on this side: the automatic key "g", got on first coming here
            (in the level: crossing the line north of frame 125, the only
            way in), opens it both ways for good
  stop2T    the other stop then: the 20. Its door 1 is door 8 of the 10, its
            door 2 the pit's doorway, its door 3 frame 126, its door 4 obsT
  obsT      the observatory's library then; domeT behind the door with the
            plate 2 (key 2), out by its stair (a door fits)
  museumT   the museum then, behind the door with the plate 1 (key 1), both
            ways: the great hall, the gallery, the cellar
  sqN       the square now: MAP10's, at night, the old bus
  stop2N, obsN, domeN, museumN   the same now. Key 3 lies in domeN
  theatreN  RED's far side now (as in MAP10): BLUE leans here. pitN as then
  depotN    YELLOW's far side now (as in MAP10); its wicket as then
  lineN     the night room now, whole (the gate's wall is down): BLUE's far
            side and frame 105. MAP10's hole down into the shelter is shut by
            Doom's stone: with it open (lineN to sqN) the level can be lost,
            the player through the clocked door in 125 and down the hole
            (672 stuck states)

Frames. The bus then: 121 (door 2: RED hangs there at the start), 122 (door
7, in its back), 123 (door 6, brass, no twin), 124 (door 4). The old bus now:
MAP10's own 101 (door 2) and 102 (door 7), and 104 (door 4). The 20: 106 now
and 126 then (its door 3). 101/121, 102/122, 104/124 and 106/126 are twins
and take any door at both times: no frame of a bus is the clocked door's
alone (Vadim, 2026-11-27: hanging it there is the accident). 105/125 in the
night room's south wall are twins and the clocked door's alone. A colour door joins places, never times: hung on the
bus then it runs to its far side then, on the old bus now to the same place
now.

The turn and the keys. The first time the clocked door hangs, the times are
joined and what is now comes through: that is the turn. Nothing is to be had
from the districts before it: key 1 is carried by what then comes to the
hotel, key 2 by what comes to the theatre. Here: an automatic key "t", got
on first standing in sqN, opens hotelK, theatreK and museumK, where keys 1, 2
and 4 lie (key 4 is carried by what the turn brings to the museum; key 3
lies in the dome now). Keys 1 and 2 open the museum and the dome; the
shelter's brass door wants 3 and 4. (In
the level the turn comes at the hanging, a free step earlier.)

As first designed (2026-11-27): 8 door actions, 12437 states, 0 stuck. Gated
(2026-11-27): 12 door actions, 28633 states, 0 stuck, nothing lost; with `all`
the same without door 6's frame, 15 without door 7's, 12 with no way out of
the theatre but RED, each with 0 stuck. The shelter's brass door stays locked
from both sides: free from inside there are 92 stuck states.

Bigger (2026-11-27; PLAN.md, "MAP22 bigger"): the other stop, the
observatory, the museum, keys 3 and 4, door 4 an ordinary frame. 12 door
actions, 761148 states, 0 stuck, nothing lost (about 3 minutes). The dome and
the museum's cellar have no frame, and no squeeze on the way out: with
MAP10's drop, squeeze and frame there RED can be shut in for good (29856
stuck states).
"""
import copy
import sys

import solve
from ajarmap import RED, BLUE, YELLOW, HOME, NAMES
from ajarthen import THEN_ID

CLOCK = 10                                      # the clocked door's key
F2, F7, F4 = 101, 102, 104                      # the old bus's frames now: doors 2, 7 and 4; then = + THEN_ID
F5 = 105                                        # the night room's south wall now; then (125) east of the gate
F6 = 123                                        # door 6 of the bus then: no twin
F3B = 106                                       # door 3 of the 20, at the other stop: now; then = + THEN_ID

PUZZLE22 = dict(
    start="sqT", goal="exit", names={**NAMES, CLOCK: "the clocked door"}, complete=True,
    frames={F2: "sqN", F7: "sqN", F4: "sqN", F5: "lineN", F3B: "stop2N",
            F2 + THEN_ID: "sqT", F7 + THEN_ID: "sqT", F4 + THEN_ID: "sqT", F5 + THEN_ID: "lineE",
            F3B + THEN_ID: "stop2T", F6: "sqT", HOME: "lineE"},
    twins={f: f + THEN_ID for f in (F2, F7, F4, F5, F3B)},
    then_frames=(F6, HOME),
    only={F5: CLOCK, F5 + THEN_ID: CLOCK, HOME: BLUE},     # (no frame of a bus is the clocked door's alone)
    home_frame=HOME,
    home_door=BLUE,
    walk=[
        ("sqT", "hotelT"), ("hotelT", "sqT"),                   # line 1
        ("sqT", "stationT"), ("stationT", "sqT"),               # line 5
        ("theatreT", "pitT"), ("pitT", "stop2T"), ("stop2T", "pitT"),   # the stage door: a drop; door 2 of the 20
        ("theatreN", "pitN"), ("pitN", "stop2N"), ("stop2N", "pitN"),
        ("sqT", "stop2T"), ("stop2T", "sqT"), ("sqN", "stop2N"), ("stop2N", "sqN"),     # door 8 of the 10: door 1 of the 20
        ("stop2T", "obsT"), ("obsT", "stop2T"), ("stop2N", "obsN"), ("obsN", "stop2N"), # door 4 of the 20
        ("obsT", "domeT", "2"), ("domeT", "obsT"),              # the dome's door; out by its stair, a door in hand or not
        ("obsN", "domeN", "2"), ("domeN", "obsN"),
        ("sqT", "museumT", "1"), ("museumT", "sqT", "1"),       # the museum's door on the square
        ("sqN", "museumN", "1"), ("museumN", "sqN", "1"),
        ("depotT", "sqT"), ("depotN", "sqN"),                   # the wicket: a step down, never in
        ("lineT", "lineE", "g"), ("lineE", "lineT", "g"),       # the gate: bolted on its east side
        ("sqT", "lineT", "34"), ("lineT", "sqT", "34"),         # the shelter's brass door
        ("hotelT", "hotelK", "t"), ("hotelK", "hotelT", "t"),   # what the turn brings to the hotel has key 1
        ("theatreT", "theatreK", "t"), ("theatreK", "theatreT", "t"),
        ("museumT", "museumK", "t"), ("museumK", "museumT", "t"),   # ... and to the museum key 4
    ],
    keys={"1": "hotelK", "2": "theatreK", "3": "domeN", "4": "museumK", "t": "sqN", "g": "lineE"},
    auto="tg",
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
        for f in (F7, F6, F3B, F4):             # (RED hangs in door 2's at the start)
            report(without_frame(f), f"without frame {f}", quiet=True)


if __name__ == "__main__":
    main(sys.argv[1:])
