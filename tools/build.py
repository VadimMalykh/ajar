"""Builds build/ajar.pk3 from src/ plus generated textures and maps."""
import hashlib
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
import gfx
import map_hinges1
import map_hinges2
import map_hinges3
import map_hinges4
import map_hinges5
import map_hinges6
import map_hinges7
import map_hinges8
import map_hinges9
import map_hinges10
import map_institute1
import map_institute2
import map_institute3
import map_institute4
import map_institute5
import map_institute6
import map_test
import map_lab
import map_eng
import map_lift
import map_belt
import map_optics
import map_mirror
import map_time
import map_timedoor
import map_plate
import map_press
import map_twokey
import map_shut
import map_secret1
import map_secret2
import map_shift
import solve

MAPS = {"MAP01": map_hinges1, "MAP02": map_hinges2, "MAP03": map_hinges3, "MAP04": map_hinges4, "MAP05": map_hinges5, "MAP06": map_hinges6, "MAP07": map_hinges7, "MAP08": map_hinges8, "MAP09": map_hinges9, "MAP10": map_hinges10, "MAP11": map_institute1, "MAP12": map_institute2, "MAP13": map_institute3, "MAP14": map_institute4, "MAP15": map_institute5, "MAP16": map_institute6, "TEST": map_test, "LAB": map_lab, "ENG": map_eng, "LIFT": map_lift, "BELT": map_belt, "OPT": map_optics, "MIR": map_mirror, "TIME": map_time, "TDOOR": map_timedoor, "PLATE": map_plate, "PRESS": map_press, "TWOKEY": map_twokey, "SHUT": map_shut, "SHIFT": map_shift, "MAP31": map_secret1, "MAP32": map_secret2}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(root, "build"), exist_ok=True)


def proof(name, puzzle):
    """What the solver has to say about a level, as lines to print; a level
    that fails stops the build."""
    out = []
    actions, steps, seen, stuck = solve.solve(puzzle)
    if actions is None:
        sys.exit(f"{name}: no solution")
    out.append(f"{name}: solvable in {actions} door actions, {seen} states, {len(stuck)} stuck")
    out += ["    " + s for s in steps]
    if puzzle.get("home_chain", {}).get("secret"):
        n, more = solve.secret(puzzle)
        if n is None:
            sys.exit(f"{name}: no way to the secret way out")
        out.append(f"    the secret way out: {n} door actions")
        out += ["        " + s for s in more]
    if stuck:
        print("\n".join(out))
        sys.exit(f"{name}: the player can get stuck, e.g. {stuck[0]}")
    gone = solve.lost(puzzle)
    out.append(f"    can be lost for good: {', '.join(w for w, _ in gone) or 'nothing'}")
    if gone and puzzle.get("complete"):
        print("\n".join(out))
        sys.exit(f"{name}: {gone[0][0]} can be lost, e.g. from {gone[0][1]}")
    return out


# A proof is kept (build/proofs.json) for as long as neither the level's
# puzzle nor the solver changes: the later levels take minutes each.
kept_at = os.path.join(root, "build", "proofs.json")
try:
    with open(kept_at) as f:
        kept = json.load(f)
except (OSError, ValueError):
    kept = {}
with open(solve.__file__, "rb") as f:
    solver = f.read()
for name, mod in MAPS.items():
    if not hasattr(mod, "PUZZLE") or os.environ.get("AJAR_QUICK"):     # AJAR_QUICK=1 ./build.sh: no solver
        continue
    key = hashlib.sha1(solver + repr(mod.PUZZLE).encode()).hexdigest()
    if kept.get(name, {}).get("key") != key:
        kept[name] = dict(key=key, lines=proof(name, mod.PUZZLE))
        with open(kept_at, "w") as f:
            json.dump(kept, f)
    print("\n".join(kept[name]["lines"]))

# AJAR_OUT=build/mine.pk3 ./build.sh: another file, so that two sessions building at once do not write over each other
out = os.path.join(root, os.environ.get("AJAR_OUT") or os.path.join("build", "ajar.pk3"))
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    src = os.path.join(root, "src")
    for d, _, files in os.walk(src):
        for f in files:
            p = os.path.join(d, f)
            z.write(p, os.path.relpath(p, src))
    for name, data in gfx.make_all().items():
        z.writestr(name, data)
    for name, mod in MAPS.items():
        z.writestr(f"maps/{name}.wad", mod.m.wad(name))
print("built", out)
