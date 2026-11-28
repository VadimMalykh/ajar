"""MAP23 "Sleeping Dogs": the door puzzle (PLAN.md, "MAP23 "Sleeping Dogs":
the first version, as decided", and "MAP23: the way out built, BLUE, the
press: as decided"), checked in the build as MAP21's and MAP22's.

    python3 tools/puzzle23.py              PUZZLE23: solution, states, stuck, lost
    python3 tools/puzzle23.py all          that, and every variant

The animal house twice: NOW (night, the ruin; the runs open to the hall) and
THEN (day; every part locked for the night from the next, entered only by the
clocked door). Regions NOW end in N, THEN in T. The goal is BLUE hung in the
brass frame of the night room (`home_frame`, HOME23); `exit` is the goal of
the first version only (its night room was a ready way out).

  yardN     the start: line 6's stop, the clocked door leaning; frame 101 (the
            clocked door's alone); the house's front door to the hall; the
            gateway to the big run (open NOW)
  hallN     the hub: the kennels, the stalls and the guards' antechamber off it
  kenN      the kennels NOW (run, pens and passage, open to each other and to
            the hall): frame 102. closetN behind the shutter S1, which stands
            open while pen 1's scales hold 400: key 1. blueN behind the second
            shutter, in the closet, open while they hold 1000: BLUE leans there
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
            2) to the night room. Down is a drop
  nightN    the night room, behind the brass door (keys 1 and 2, from either
            side): BLUE's far side in one end, the brass frame HOME23 (BLUE's
            alone) in the other
  bpassN    the big run's keeper's passage NOW, sealed: frame 105 (the
            clocked door's alone), RED's far side
  yardT     the yard by day, sealed: frame 121
  kenT      the kennels THEN: frame 122 in the keeper's passage, the turnstile
            to the run (the player passes with a door or without): one region.
            Here a demon can be baited into pen 1 and shut in: key "d"; all
            three: key "D"; the three shot dead in the pen through its hatch,
            for good: key "X"
  stallT    the stalls THEN: frame 123; a knight into the stall: key "k"
  isoT      the isolation wing THEN: frame 124 in the run's west end, the
            turnstile to the keeper's passage; the guards led here and left
            (penned or not): key "g"
  bpassT    the big run's keeper's passage THEN: frame 125, RED's far side;
            the big one into the crush: key "c"; pressed dead there by the
            crush's roof, for good: key "P"
  nightT    the night room's place THEN, sealed: BLUE's far side THEN (a
            colour door joins places, never times), nothing else

Bones are keys got THEN (the house is always stocked: a specimen can always be
had, so the key is never out of reach while its region is), and the ways they
make NOW need them; S1, the second shutter, the stall's ledge and the crush's
ledge need too that the clocked door hangs nowhere ("apart", tools/solve.py:
bones stand in for one alive THEN only while the times are apart). Bones of
one killed THEN are keys with no such condition ("X", "P"): they are there for
good, whatever hangs. So is the guards' going: once THEN they are out of the
guard room whatever hangs.

The old door rule is on (`old`, PLAN.md "The old door lab"): RED or BLUE hung
THEN in 122, 123 or 124 is an old door NOW in 102, 103 or 104, open onto its
far side NOW. No part of the way needs it.

As first designed (AS_DESIGNED, RED on the stall's ledge) there is no
solution: the bones stand in only while the clocked door hangs nowhere, and
then it is in the player's hands, and a door is never put down, so RED on the
ledge can never be taken (`all` prints why()). FIRST is fix 1 of three, the
first playable version (built 2026-11-27): RED with the guards, key 2 on the
ledge, the night room a ready way out. PUZZLE23 is the way out built, BLUE,
the press (2026-11-28). Every stall and pen lies on the south side or at the
south end of its run; that is the map's business, not the solver's.
"""
import copy
import sys

import solve
from ajarmap import RED, BLUE, NAMES
from ajarthen import THEN_ID

CLOCK = 10                                      # the clocked door's key
HOME23 = 109                                    # the night room's brass frame (map_sleepingdogs.py; BLUE's alone)
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


FIRST = red_with_the_guards()                   # the first playable version (built 2026-11-27)


def way_out_built(p=FIRST):
    """The way out built, BLUE, the press (PLAN.md, "MAP23: the way out built,
    BLUE, the press: as decided"). The night room behind the brass door is
    ajarmap.way_home with BLUE: the goal is BLUE in the brass frame. BLUE
    leans behind the second shutter (1000: the three demons in pen 1), which
    stands open while they are penned alive and the times apart ("D"), or for
    good once they are shot dead in the pen ("X"); S1 the same (400). The
    crush's ledge is reached up the big one's bones while it is penned and the
    times apart ("c"), or for good once it is pressed dead in the crush ("P").
    The old door rule on."""
    q = copy.deepcopy(p)
    q["goal"] = "exit"                          # (no way leads there: the goal is the brass frame)
    q["home_frame"] = HOME23
    q["old"] = True
    q["frames"][HOME23] = "nightN"
    q["only"][HOME23] = BLUE
    q["walk"].remove(("cledgeN", "exit", "12"))
    q["walk"] += [
        ("kenN", "closetN", "X"),                                            # S1, for good
        ("closetN", "blueN", "D", None, APART), ("closetN", "blueN", "X"),   # the second shutter (1000)
        ("blueN", "closetN"),
        ("bigN", "cledgeN", "P"),                                            # up the pressed one's bones
        ("cledgeN", "nightN", "12"), ("nightN", "cledgeN", "12"),            # the brass door, both ways locked
    ]
    q["keys"].update({"D": "kenT", "X": "kenT", "P": "bpassT"})
    q["doors"][BLUE] = dict(home="nightN", home_then="nightT", lean="blueN")
    return q


PUZZLE23 = way_out_built()


def without_key(*ks, p=PUZZLE23):
    """p with bones `ks` never to be had: is that wing, or that kill, needed?"""
    q = copy.deepcopy(p)
    for k in ks:
        q["keys"].pop(k)
    return q


def keys_only(p=AS_DESIGNED):
    """The bones as keys alone, with no "apart": what the condition costs."""
    q = copy.deepcopy(p)
    q["walk"] = [w[:3] if len(w) > 3 else w for w in q["walk"]]
    return q


def old_off(p=PUZZLE23):
    """The old door rule off: does any of the way need it?"""
    q = copy.deepcopy(p)
    q.pop("old")
    return q


def frame_on_ledge(p=PUZZLE23):
    """Against the rule "no frame beyond a way that bones make": a twinned
    frame 106/126 on the stall's ledge (THEN in the stall). The clocked door
    hung there and the player dropped back, the bones are gone."""
    q = copy.deepcopy(p)
    q["frames"].update({106: "ledgeN", 106 + THEN_ID: "stallT"})
    q["twins"][106] = 106 + THEN_ID
    return q


def frame_takes_any(p=PUZZLE23):
    """The brass frame taking any door (no `only`): BLUE is still the one
    that makes the way out, but could another door hung there carry it in?"""
    q = copy.deepcopy(p)
    q["only"].pop(HOME23)
    return q


def blue_not_then(p=PUZZLE23):
    """A way out of the trap below (not decided): the wings' frames THEN (122, 123, 124) take any door but BLUE
    (recess only=4, their trim says so), their twins NOW any door."""
    q = copy.deepcopy(p)
    for f in (102, 103, 104):
        q["only"][f + THEN_ID] = (CLOCK, RED)
        q["only"][f] = (CLOCK, RED, BLUE)
    return q


# THE TRAP (2026-11-28, the worker on Opus, measured): with `old` on, PUZZLE23 has 2592 stuck states, every one
# BLUE hung THEN in 122, 123 or 124 with the clocked door in hand. The player carries BLUE THEN into a wing through
# the clocked door and swaps BLUE in for it: BLUE's old self now fills the NOW twin, and the clocked door's own
# refusal ("At the other time a door hangs in this frame", the old door lab's check clockedRefusedOldDoorInTwin)
# keeps it out of the wing's frame for good; the wing THEN has no other way out, and BLUE's far side THEN (nightT)
# none at all. BLUE can never leave the wing: the level is lost. RED in the same place is not (its far side THEN
# is in bpassT, with frame 125 for the clocked door, and old RED NOW opens on bpassN). No geometry mends it: the
# only exit of a wing THEN is its frame, and BLUE can leave by it only with the clocked door in it. The options
# measured: blue_not_then() (0 stuck; nightT then never reached), old_off() (0 stuck), and, outside this file,
# the clocked door allowed to swap in for a colour door whose old self fills its twin (solve.py and then.zs; 0
# stuck, nothing lost; BEFORE and MAP24 the same states and actions).
# DECIDED (2026-11-28, the session on Fable): the last, the law mended, not the map (PLAN.md, "The old door rule,
# mended"). With it PUZZLE23 as it stands: 11 door actions, 186668 states, 0 stuck, nothing lost.


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


def reached(p, what=""):
    """After solve(p) (no solution): what the player can still have: keys, places, and what he holds where it
    matters (BLUE's room, the crush's ledge, the night room)."""
    dist, _ = solve.solve.plain
    keys = sorted({k for s in dist for k in s[3]})
    places = sorted({s[0] for s in dist})
    print(f"    keys ever had: {' '.join(keys)}; places reached: {' '.join(places)}")
    for r in ("blueN", "cledgeN", "nightN"):
        held = sorted({s[1] for s in dist if s[0] == r}, key=repr)
        if held:
            print(f"    in {r} the player holds: {', '.join(str(p['names'].get(c, c) if c is not None else 'nothing') for c in held)}")
    blue = sorted({loc for s in dist for c, loc in zip(sorted(p["doors"]), s[2]) if c == BLUE}, key=repr)
    if blue:
        print(f"    BLUE is ever: {', '.join(' '.join(map(str, loc)) for loc in blue)}")
    if what:
        print(f"    {what}")


def shortest_to(p, test, what):
    """After solve(p): the fewest door actions to a state where `test` holds, by the player's moves alone."""
    dist, _ = solve.solve.plain
    got = [d for s, d in dist.items() if test(s)]
    print(f"    {what}: " + (f"in {min(got)} door actions" if got else "NEVER"))


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
        return False
    if not quiet:
        for st in steps:
            print("    " + st)
    print("    can be lost for good: " + (", ".join(w for w, _ in solve.lost(p)) or "nothing"))
    for s in sorted(stuck, key=repr)[:5]:
        print("    stuck e.g.: " + describe(p, s))
    sys.stdout.flush()
    return True


def main(args):
    report(PUZZLE23, "PUZZLE23 (MAP23 as built: the way out built with BLUE, the press, the old door rule on)")
    if "all" not in args:
        return
    # --- what the design's "To prove" asks, each by a variant
    report(without_key("X"), "the demons only penned alive, never killed (no key X)", quiet=True)
    reached(without_key("X"), "(penned alive, the second shutter is open only while the clocked door is in hand)")
    report(without_key("P"), "the big one only penned alive, never pressed (no key P)", quiet=True)
    reached(without_key("P"), "(penned alive, its bones stand in only while the clocked door is in hand)")
    report(without_key("X", "P"), "penning alone (no key X, no key P)", quiet=True)
    for k in ("1", "2"):
        shortest_to(without_key("X", "P"), lambda s, k=k: k in s[3], f"key {k} by penning alone")
    q = without_key("X", "P")
    solve.solve(q)
    print("    keys ever had by penning alone: " + " ".join(sorted({k for s in solve.solve.plain[0] for k in s[3]})))
    # --- the wings: each still needed
    for k, wing in (("d", "the kennels' one demon (key d)"), ("k", "the stalls (key k)"), ("g", "the guards (key g)"),
                    ("c", "the big one penned (key c)")):
        report(without_key(k), f"without {wing}", quiet=True)
    report(without_key("D"), "without the three demons penned alive (no key D)", quiet=True)
    # --- the rules
    report(old_off(), "the old door rule off (does the way need it?)", quiet=True)
    report(keys_only(PUZZLE23), "bones as keys alone (no 'apart')", quiet=True)
    report(keys_only(without_key("X", "P")), "bones as keys alone, no kill (no 'apart', no X, no P)", quiet=True)
    report(frame_takes_any(), "the brass frame takes any door (no 'only')", quiet=True)
    report(frame_on_ledge(), "a twinned frame on the stall's ledge (against the rule)", quiet=True)
    # --- the trap's ways out (not decided)
    report(blue_not_then(), "the wings' frames THEN take any door but BLUE", quiet=True)
    # --- the first version (built 2026-11-27): its history
    report(FIRST, "the first playable version (fix 1: RED with the guards, key 2 on the ledge; the way out ready)",
           quiet=True)
    report(AS_DESIGNED, "as first designed (RED on the stall's ledge, key 2 with the guards)", quiet=True)
    why()
    report(knight_killed(), "fix 3: as first designed, the knight may be killed in the stall then", quiet=True)
    report(red_behind_shutter(), "fix 2: as first designed, a switch on the ledge opens RED's closet for good",
           quiet=True)


if __name__ == "__main__":
    main(sys.argv[1:])
