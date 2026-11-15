"""Builds build/ajar.pk3 from src/ plus generated textures and maps."""
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
import map_test
import solve

MAPS = {"MAP01": map_hinges1, "MAP02": map_hinges2, "MAP03": map_hinges3, "MAP04": map_hinges4, "MAP05": map_hinges5, "MAP06": map_hinges6, "TEST": map_test}

for name, mod in MAPS.items():
    if not hasattr(mod, "PUZZLE"):
        continue
    actions, steps, seen, stuck = solve.solve(mod.PUZZLE)
    if actions is None:
        sys.exit(f"{name}: no solution")
    print(f"{name}: solvable in {actions} door actions, {seen} states, {len(stuck)} stuck")
    for s in steps:
        print("   ", s)
    if stuck:
        sys.exit(f"{name}: the player can get stuck, e.g. {stuck[0]}")
    gone = solve.lost(mod.PUZZLE)
    print(f"    can be lost for good: {', '.join(w for w, _ in gone) or 'nothing'}")
    if gone and mod.PUZZLE.get("complete"):
        sys.exit(f"{name}: {gone[0][0]} can be lost, e.g. from {gone[0][1]}")

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(root, "build"), exist_ok=True)
out = os.path.join(root, "build", "ajar.pk3")
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
