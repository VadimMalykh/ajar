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
import map_dispatch
import map_clockdept
import map_paper
import map_highwater
import map_test
import map_lab
import map_eng
import map_lift
import map_belt
import map_clock
import map_oneside
import map_pass
import map_water
import map_optics
import map_mirror
import map_time
import map_timedoor
import map_plate
import map_press
import map_twokey
import map_shut
import map_third
import map_secret1
import map_secret2
import map_shift
import map_soundlab
import map_lefthand
import gfx_title                                # the title, the menus and the help page (AJAR_TITLE; unset: look 1; 0: none, Doom II's)
import music
import music_trial
import sfx
import solve

MAPS = {"MAP01": map_hinges1, "MAP02": map_hinges2, "MAP03": map_hinges3, "MAP04": map_hinges4, "MAP05": map_hinges5, "MAP06": map_hinges6, "MAP07": map_hinges7, "MAP08": map_hinges8, "MAP09": map_hinges9, "MAP10": map_hinges10, "MAP11": map_institute1, "MAP12": map_institute2, "MAP13": map_institute3, "MAP14": map_institute4, "MAP15": map_institute5, "MAP16": map_institute6, "MAP17": map_dispatch, "MAP18": map_clockdept, "MAP19": map_paper, "MAP20": map_highwater, "TEST": map_test, "LAB": map_lab, "ENG": map_eng, "LIFT": map_lift, "BELT": map_belt, "CLOCK": map_clock, "ONESIDE": map_oneside, "PASS": map_pass, "WATER": map_water, "OPT": map_optics, "MIR": map_mirror, "TIME": map_time, "TDOOR": map_timedoor, "PLATE": map_plate, "PRESS": map_press, "TWOKEY": map_twokey, "SHUT": map_shut, "THIRD": map_third, "SHIFT": map_shift, "SOUND": map_soundlab, "LEFT": map_lefthand, "MAP31": map_secret1, "MAP32": map_secret2}

import map_station                              # MAP33 "Third Person" (third.zs)
MAPS["MAP33"] = map_station

import map_last                                 # the last fight lab (third.zs, last.zs)
MAPS["LAST"] = map_last

import map_yard                                 # the yard lab: a common place (third.zs, common.zs)
MAPS["YARD"] = map_yard

import map_then                                 # the then and now lab: a place built twice (then.zs)
MAPS["THEN"] = map_then

import map_longrun                              # MAP21 "In the Long Run" (then.zs, map21.zs); last: its signs and door faces
MAPS["MAP21"] = map_longrun                     # are numbered after MAP11's to 16's (map_institute1.SIGNS, FACES)

import map_dayreturn                            # MAP22 "Day Return" (then.zs, map22.zs): after MAP21, so that no earlier
MAPS["MAP22"] = map_dayreturn                   # map's numbering moves

import map_kennel                               # the kennel lab: bones as a tool (then.zs, kennel.zs); last, so that no
MAPS["KENNEL"] = map_kennel                     # other map's numbering moves
import map_sleepingdogs                         # MAP23 "Sleeping Dogs" (then.zs, kennel.zs, map23.zs): after the kennel
MAPS["MAP23"] = map_sleepingdogs                # lab, so that no other map's numbering moves
import map_before                               # the three times lab (then.zs): last, so that no other map's numbering
MAPS["BEFORE"] = map_before                     # moves
import map_lefthanging                          # MAP24 "Left Hanging" (then.zs, water.zs, map24.zs): after BEFORE, so
MAPS["MAP24"] = map_lefthanging                 # that no other map's numbering moves

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
for name, mod in MAPS.items():                  # a level checked another way prints its own figures (MAP18: the stopwatch; MAP19: the measure)
    if hasattr(mod, "MEASURE"):
        print("\n".join(mod.MEASURE))

# AJAR_OUT=build/mine.pk3 ./build.sh: another file, so that two sessions building at once do not write over each other
out = os.path.join(root, os.environ.get("AJAR_OUT") or os.path.join("build", "ajar.pk3"))
# AJAR_TITLE=n: Ajar's own title, menus and help page, look n (tools/gfx_title.py). Its files go in as they
# are; a name ending in "+" is text to add to the end of that file (mapinfo.txt, language.txt, textures.txt).
# With AJAR_TITLE=0 there is none of either, and every file goes in as it is.
title = gfx_title.make()
more = {name[:-1]: title.pop(name) for name in list(title) if name.endswith("+")}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    src = os.path.join(root, "src")
    # a map may ask for lines of its mapinfo.txt block to be changed (MAPINFO: {old line: new line}; MAP33's
    # look, AJAR_POWER, its sky); with none asked for, the file goes in as it is
    edits = {name: mod.MAPINFO for name, mod in MAPS.items() if getattr(mod, "MAPINFO", None)}
    for d, _, files in os.walk(src):
        for f in files:
            p = os.path.join(d, f)
            if os.path.relpath(p, src) == "mapinfo.txt" and (edits or "mapinfo.txt" in more):
                with open(p) as fh:
                    text = fh.read()
                for name, changes in edits.items():
                    at = text.index(f'\nmap {name} "')
                    end = text.index("\n}", at)
                    block = text[at:end]
                    for old, new in changes.items():
                        assert block.count(old) == 1, (name, old)
                        block = block.replace(old, new)
                    text = text[:at] + block + text[end:]
                z.writestr("mapinfo.txt", text + more.pop("mapinfo.txt", b"").decode())
                continue
            if os.path.relpath(p, src) in more:
                with open(p, "rb") as fh:
                    z.writestr(os.path.relpath(p, src), fh.read() + more.pop(os.path.relpath(p, src)))
                continue
            z.write(p, os.path.relpath(p, src))
    for name, data in gfx.make_all().items():
        if name in more:
            data = (data if isinstance(data, bytes) else data.encode()) + more.pop(name)
        z.writestr(name, data)
    assert not more, more                       # text to add to a file that is not there
    for name, data in title.items():
        z.writestr(name, data)
    for name, data in sfx.make_all().items():          # the door sounds, their sndinfo.txt and ajsounds.txt
        z.writestr(name, data)
    # the music on trial, one list (ajmusic.txt) for the lab: the pieces written by tools/music.py, then any
    # recorded file put into trial/music/ (local to a worktree, never committed)
    tunes, own = music.make_all(), music_trial.make_all(root)
    tunes["ajmusic.txt"] += own.pop("ajmusic.txt")
    for name, data in {**tunes, **own}.items():
        z.writestr(name, data, zipfile.ZIP_STORED if name.startswith("music/AJT") else zipfile.ZIP_DEFLATED)
    for name, mod in MAPS.items():
        z.writestr(f"maps/{name}.wad", mod.m.wad(name))
print("built", out)
