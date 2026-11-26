"""Runs the solver on every level that has a PUZZLE and prints one line per
level: states, actions and steps of the shortest solution, stuck states and
what lost() says. For checking that a change to solve.py leaves every old
level's verdict as it was: run it before and after, and diff the two.

    python3 tools/solvecheck.py                  every tools/map_*.py with a PUZZLE
    python3 tools/solvecheck.py map_hinges1 ...  only those
    python3 tools/solvecheck.py --skip map_x     all but those

A module that fails to import is reported as such and skipped.
"""
import glob
import hashlib
import io
import contextlib
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import solve                                     # noqa: E402


def check(name):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            mod = __import__(name)
    except BaseException as e:                   # a map that does not build: not the solver's business
        return f"{name}: IMPORT FAILED ({type(e).__name__}: {e})"
    p = getattr(mod, "PUZZLE", None)
    if p is None:
        return None
    t = time.time()
    actions, steps, seen, stuck = solve.solve(p)
    line = f"{name}: {seen} states, {actions} actions, steps {hashlib.sha1(repr(steps).encode()).hexdigest()[:12]}, {len(stuck)} stuck"
    if stuck:
        line += f" (first {min(stuck, key=repr)})"
    if actions is not None and p.get("home_chain", {}).get("secret"):
        n, more = solve.secret(p)
        line += f", secret {n} {hashlib.sha1(repr(more).encode()).hexdigest()[:12]}"
    if actions is not None:
        gone = solve.lost(p)
        line += f", lost: {', '.join(w for w, _ in gone) or 'nothing'}"
    print(f"    ({name}: {time.time() - t:.0f} s)", file=sys.stderr)
    return line


def main(argv):
    skip = set()
    if argv[:1] == ["--skip"]:
        skip, argv = set(argv[1:]), []
    names = argv or sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(here, "map_*.py")))
    for name in names:
        if name in skip:
            print(f"{name}: SKIPPED")
            continue
        src = open(os.path.join(here, name + ".py")).read()
        if "PUZZLE" not in src:
            continue
        line = check(name)
        if line:
            print(line, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
