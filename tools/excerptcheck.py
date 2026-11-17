"""Whether the pieces of earlier levels in MAP10 (ajarmap.excerpt) look as
they do in those levels: python3 tools/excerptcheck.py [-v]

For each excerpt, every line of MAP10 that lies where a line of the source
level lies (moved) is compared with it: both sides' textures and offsets, the
flags that change how a wall is drawn, and the sectors behind (heights, flats,
light, tint). Then the things: what stands in the source inside the excerpt's
rooms and is not in MAP10. Differences are grouped by kind; -v lists each.
"""
import collections
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])


def parse(text):
    out = collections.defaultdict(list)
    for kind, body in re.findall(r"(\w+)\{([^}]*)\}", text):
        d = {}
        for k, v in re.findall(r"(\w+)=([^;]*);", body):
            d[k] = v.strip('"') if v.startswith('"') else True if v == "true" else False if v == "false" else float(v)
        out[kind].append(d)
    return out


LOOKS = ("texturetop", "texturemiddle", "texturebottom", "offsetx_top", "offsetx_mid", "offsetx_bottom",
         "offsety_top", "offsety_mid", "offsety_bottom", "scalex_top", "scalex_mid", "scalex_bottom")
FLAGS = ("dontpegtop", "dontpegbottom", "twosided", "blocking")
SECTOR = ("heightfloor", "heightceiling", "texturefloor", "textureceiling", "lightlevel", "color_floor",
          "color_ceiling", "color_walltop", "color_wallbottom", "lightfloor", "lightceiling",
          "lightfloorabsolute", "lightceilingabsolute", "xpanningfloor", "ypanningfloor")


def lines_of(t, dx=0, dy=0):
    """{frozenset of its two ends: {(end a, end b): what that side shows}}"""
    out = {}
    for ld in t["linedef"]:
        a, b = (t["vertex"][int(ld[k])] for k in ("v1", "v2"))
        a, b = (a["x"] + dx, a["y"] + dy), (b["x"] + dx, b["y"] + dy)
        sides = {}
        for which, way in (("sidefront", (a, b)), ("sideback", (b, a))):
            if which in ld:
                sd = t["sidedef"][int(ld[which])]
                sec = t["sector"][int(sd["sector"])]
                sides[way] = dict({k: sd[k] for k in LOOKS if k in sd}, **{"sector." + k: sec[k] for k in SECTOR if k in sec})
        out[frozenset((a, b))] = dict(sides=sides, flags={k: ld[k] for k in FLAGS if ld.get(k)},
                                      special=ld.get("special", 0))
    return out


def visible(side, flags, other):
    """Drop what cannot be seen: a top or bottom texture where nothing shows
    is still written by udmf.py, and is the neighbour's wall."""
    d = dict(side)
    if not flags.get("twosided"):
        for k in list(d):
            if k.endswith(("top", "bottom")) and not k.startswith("sector."):
                del d[k]
    elif other is not None:
        if other.get("sector.heightceiling", 0) >= d.get("sector.heightceiling", 0):
            d = {k: v for k, v in d.items() if not k.endswith("_top") and k != "texturetop"}
        if other.get("sector.heightfloor", 0) <= d.get("sector.heightfloor", 0):
            d = {k: v for k, v in d.items() if not k.endswith("_bottom") and k != "texturebottom"}
    return d


def main(verbose):
    import ajarmap
    import map_hinges2, map_hinges3, map_hinges5, map_hinges10 as ten
    new = parse(ten.m.textmap())
    mine = lines_of(new)
    bad = 0
    for name, src, (dx, dy) in (("MAP02 the hotel", map_hinges2.m, (ten.HX, 0)),
                                ("MAP05 the station", map_hinges5.m, (ten.SX, 0)),
                                ("MAP03 the theatre", map_hinges3.m, (0, ten.TY))):
        old = parse(src.textmap())
        theirs = lines_of(old, dx, dy)
        same = n = 0
        kinds = collections.Counter()
        notes = []
        for key, was in theirs.items():
            now = mine.get(key)
            if now is None:
                continue
            n += 1
            ok = True
            for way, side in now["sides"].items():
                ws = was["sides"].get(way)
                if ws is None:              # a wall here, a way through there: where the excerpt ends
                    continue
                back = [s for w, s in now["sides"].items() if w != way]
                wback = [s for w, s in was["sides"].items() if w != way]
                a = visible(side, now["flags"], back[0] if back else None)
                b = visible(ws, was["flags"], wback[0] if wback else None)
                if len(now["sides"]) != len(was["sides"]):
                    # the excerpt's edge: only the room's own side can be compared, and its wall
                    # is what the room shows where the original had a hole
                    kinds["edge of the excerpt (a wall where the level went on)"] += 1
                    if verbose:
                        notes.append(f"  edge {sorted(key)}: now {a.get('texturemiddle')}, was two-sided {b.get('texturetop')}/{b.get('texturebottom')}"
                                     f" special {was['special']}")
                    continue
                for k in sorted(set(a) | set(b)):
                    if a.get(k) != b.get(k):
                        ok = False
                        kinds[k] += 1
                        notes.append(f"  {sorted(key)} {k}: now {a.get(k)}, was {b.get(k)}")
                for k in FLAGS:
                    if now["flags"].get(k) != was["flags"].get(k):
                        ok = False
                        kinds["flag " + k] += 1
                        notes.append(f"  {sorted(key)} flag {k}: now {now['flags'].get(k)}, was {was['flags'].get(k)} (special {was['special']})")
            same += ok
        # things
        def spot(t):
            return (t["x"], t["y"], int(t["type"]), t.get("angle", 0))
        have = collections.Counter(spot(t) for t in new["thing"])
        polys = src.polys
        kept = {frozenset((round(v[0], 3), round(v[1], 3)) for v in p) for p in ten.m.polys}
        gone = collections.Counter()
        for t in old["thing"]:
            s = (t["x"] + dx, t["y"] + dy, int(t["type"]), t.get("angle", 0))
            if have[s]:
                continue
            where = next((p for p in polys if _inside(t["x"], t["y"], p)), None)
            inside = where is not None and frozenset((round(v[0] + dx, 3), round(v[1] + dy, 3)) for v in where) in kept
            if inside:
                gone[int(t["type"])] += 1
                if verbose:
                    notes.append(f"  thing {int(t['type'])} at {t['x'], t['y']} (now {s[0], s[1]}) is not in MAP10")
        print(f"{name}: {n} lines in common, {same} the same; differences: {dict(kinds) or 'none'}")
        print(f"    things left behind in rooms that were kept, by type: {dict(gone) or 'none'}")
        if notes:
            print("\n".join(notes[:400 if verbose else 12]))
        bad += n - same
    return bad


def _inside(x, y, p):
    hit = False
    for a, b in zip(p, p[1:] + p[:1]):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            hit = not hit
    return hit


if __name__ == "__main__":
    sys.exit(1 if main("-v" in sys.argv) else 0)
