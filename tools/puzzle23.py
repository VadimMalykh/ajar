"""MAP23 "Sleeping Dogs": the door puzzle (PLAN.md, "MAP23 "Sleeping Dogs":
the first version, as decided"), checked in the build as MAP21's and MAP22's.

    python3 tools/puzzle23.py              PUZZLE23: solution, states, stuck, lost
    python3 tools/puzzle23.py all          that, and every variant

The animal house twice: NOW (night, the ruin; the runs open to the hall) and
THEN (day; every part locked for the night from the next, entered only by the
clocked door). Regions NOW end in N, THEN in T; `exit` is the goal.

  yardN     the start: line 6's stop, the clocked door leaning; frame 101 (the
            clocked door's alone); the house's front door to the hall; the
            gateway to the big run (open NOW)
  hallN     the hub: the kennels, the stalls and the guards' antechamber off it
  kenN      the kennels NOW (run, pens and passage, open to each other and to
            the hall): frame 102. closetN behind the shutter S1, which stands
            open while pen 1's scales hold 400: key 1
  stallN    the stalls NOW (run, funnel, stall 2, passage): frame 103.
            ledgeN, the stall's ledge at 48, reached only up the bones of a
            knight in the stall: key 2 (as first designed RED leant there).
            Down is a drop
  anteN     the guards' antechamber: frame 104. guardN, the guard room's far
            side, past two barons and an arch-vile: RED leans there (as first
            designed key 2 lay there)
  bigN      the big run NOW, off the yard: the big one's bones in its middle
            (a step that leads nowhere). cledgeN, the crush's ledge, reached
            only up its bones in the crush; the brass door on it (keys 1 and
            2) to the night room, `exit`. Down is a drop
  bpassN    the big run's keeper's passage NOW, sealed: frame 105 (the
            clocked door's alone), RED's far side
  yardT     the yard by day, sealed: frame 121
  kenT      the kennels THEN: frame 122 in the keeper's passage, the turnstile
            to the run (the player passes with a door or without): one region.
            Here a demon can be baited into pen 1 and shut in: key "d"
  stallT    the stalls THEN: frame 123; a knight into the stall: key "k"
  isoT      the isolation wing THEN: frame 124 in the run's west end, the
            turnstile to the keeper's passage; the guards led here and left
            (penned or not): key "g"
  bpassT    the big run's keeper's passage THEN: frame 125, RED's far side;
            the big one into the crush: key "c"

Bones are keys got THEN (the house is always stocked: a specimen can always be
had, so the key is never out of reach while its region is), and the ways they
make NOW need them; S1, the stall's ledge and the crush's ledge need too that
the clocked door hangs nowhere ("apart", tools/solve.py: bones stand in for one
alive THEN only while the times are apart). The guards' going is a key with no
such condition: once THEN they are out of the guard room whatever hangs.

As first designed (AS_DESIGNED, RED on the stall's ledge) there is no
solution: the bones stand in only while the clocked door hangs nowhere, and
then it is in the player's hands, and a door is never put down, so RED on the
ledge can never be taken (`all` prints why()). PUZZLE23 is fix 1 of three:
RED with the guards, key 2 on the ledge (10 door actions, 0 stuck, nothing
lost). Every stall and pen lies on the south side or at the south end of its
run; that is the map's business, not the solver's.
"""
import copy
import sys

import solve
from ajarmap import RED, NAMES
from ajarthen import THEN_ID

CLOCK = 10                                      # the clocked door's key
NOW_FRAMES = {101: "yardN", 102: "kenN", 103: "stallN", 104: "anteN", 105: "bpassN"}
THEN_REGION = {101: "yardT", 102: "kenT", 103: "stallT", 104: "isoT", 105: "bpassT"}
APART = {"apart": True}

AS_DESIGNED = dict(
    start="yardN", goal="exit", names={**NAMES, CLOCK: "the clocked door"}, complete=True,
    frames={**NOW_FRAMES, **{f + THEN_ID: r for f, r in THEN_REGION.items()}},
    twins={f: f + THEN_ID for f in NOW_FRAMES},
    only={101: CLOCK, 105: CLOCK},              # (their twins 121 and 125 the same)
    walk=[
        ("yardN", "hallN"), ("hallN", "yardN"),             # the house's front door (Doom's, USE)
        ("yardN", "bigN"), ("bigN", "yardN"),               # the big run's gateway, open NOW
        ("hallN", "kenN"), ("kenN", "hallN"),
        ("hallN", "stallN"), ("stallN", "hallN"),
        ("hallN", "anteN"), ("anteN", "hallN"),
        ("kenN", "closetN", "d", None, APART), ("closetN", "kenN"),          # S1, held open by the bones
        ("stallN", "ledgeN", "k", None, APART), ("ledgeN", "stallN"),        # up the knight's bones; a drop
        ("anteN", "guardN", "g"), ("guardN", "anteN"),                       # past the guards, once they are gone
        ("bigN", "cledgeN", "c", None, APART), ("cledgeN", "bigN"),          # up the big one's bones; a drop
        ("cledgeN", "exit", "12"),                                           # the brass door
    ],
    keys={"1": "closetN", "2": "guardN", "d": "kenT", "k": "stallT", "g": "isoT", "c": "bpassT"},
    doors={
        CLOCK: dict(clock=True, lean="yardN"),
        RED: dict(home="bpassN", home_then="bpassT", lean="ledgeN"),
    },
)


def red_with_the_guards(p=AS_DESIGNED):
    """Fix 1, taken (PLAN.md, "Corrected by the solver"): RED on the guard
    room's far side, key 2 on the stall's ledge. The guards once THEN are out
    of the guard room whatever hangs (unless left loose with the clocked door
    in 104), so RED is taken with empty hands, the clocked door hung in another
    wing; key 2 is taken with it in hand."""
    q = copy.deepcopy(p)
    q["keys"]["2"] = "ledgeN"
    q["doors"][RED]["lean"] = "guardN"
    return q


PUZZLE23 = red_with_the_guards()


def without_key(k, p=PUZZLE23):
    """p with bones `k` never to be had: is that wing needed?"""
    q = copy.deepcopy(p)
    q["keys"].pop(k)
    return q


def keys_only(p=AS_DESIGNED):
    """The bones as keys alone, with no "apart": what the condition costs."""
    q = copy.deepcopy(p)
    q["walk"] = [w[:3] if len(w) > 3 else w for w in q["walk"]]
    return q


def frame_on_ledge(p=PUZZLE23):
    """Against the rule "no frame beyond a way that bones make": a twinned
    frame 106/126 on the stall's ledge (THEN in the stall). The clocked door
    hung there and the player dropped back, the bones are gone."""
    q = copy.deepcopy(p)
    q["frames"].update({106: "ledgeN", 106 + THEN_ID: "stallT"})
    q["twins"][106] = 106 + THEN_ID
    return q


def knight_killed(p=AS_DESIGNED):
    """The knight killed THEN in the stall (through the hatch): its bones are
    there for good, whatever hangs (key "K", no "apart")."""
    q = copy.deepcopy(p)
    q["keys"]["K"] = "stallT"
    q["walk"].append(("stallN", "ledgeN", "K"))
    return q


def red_behind_shutter(p=AS_DESIGNED):
    """On the stall's ledge a switch (key "r", for good) opens a closet off
    the stall's run at floor level, where RED leans."""
    q = copy.deepcopy(p)
    q["keys"]["r"] = "ledgeN"
    q["walk"] += [("stallN", "redN", "r"), ("redN", "stallN", "r")]
    q["doors"][RED]["lean"] = "redN"
    return q


def why(p=AS_DESIGNED):
    """What the player can have, as designed: the keys and places reached."""
    solve.solve(p)
    dist, _ = solve.solve.plain
    keys = sorted({k for s in dist for k in s[3]})
    places = sorted({s[0] for s in dist})
    held = sorted({s[1] for s in dist if s[0] == "ledgeN"}, key=repr)
    print(f"    keys ever had: {' '.join(keys)}; places reached: {' '.join(places)}")
    print(f"    on the stall's ledge the player holds: {', '.join(str(p['names'].get(c, c)) for c in held)}"
          " (bones stand in only while the clocked door hangs nowhere, and then it is in hand;"
          " one door at a time: RED cannot be taken)")


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
    report(PUZZLE23, "PUZZLE23 (MAP23 as built: fix 1, RED with the guards, key 2 on the stall's ledge)")
    if "all" in args:
        report(AS_DESIGNED, "as first designed (RED on the stall's ledge, key 2 with the guards)", quiet=True)
        why()
        report(knight_killed(), "fix 3: as designed, the knight may be killed in the stall then", quiet=True)
        report(red_behind_shutter(), "fix 2: as designed, a switch on the ledge opens RED's closet for good", quiet=True)
        for k, wing in (("d", "the kennels"), ("k", "the stalls"), ("g", "the guards"), ("c", "the big run")):
            report(without_key(k), f"without {wing} (no key {k})", quiet=True)
        report(keys_only(PUZZLE23), "bones as keys alone (no 'apart')", quiet=True)
        report(frame_on_ledge(), "a twinned frame on the stall's ledge (against the rule)", quiet=True)


if __name__ == "__main__":
    main(sys.argv[1:])
