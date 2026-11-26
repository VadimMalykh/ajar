"""MAP33's look against the plain level: nothing moved (tools/power33.py).

    python3 tools/power33_compare.py build/plain.pk3 build/look1.pk3 [build/base.pk3]

1. Every map but MAP33 is the same, byte for byte, in the two builds.
2. MAP33 with the look against the plain one, textures, offsets, scales, tints and line splits set aside:
   the things the same (every field, in order), the sectors the same (count and every field but their
   flats, panning, scales and colours: heights, light, tags, specials, user fields), the lines the same
   once the pieces the look cut out of a line are joined again (each plain line covered exactly by lines of
   the look on it, every one with the plain line's flags, special, arguments, id and its sides' sectors),
   and the multiset of line specials (special and arguments) the same.
With a third build (the plain level from before the look): MAP33's TEXTMAP of the first build is that one's,
byte for byte (AJAR_POWER unset changes nothing).
"""
import collections
import re
import struct
import sys
import zipfile


def lumps(wad):
    n, off = struct.unpack("<4xii", wad[:12])
    out = {}
    for i in range(n):
        p, s, nm = struct.unpack("<ii8s", wad[off + 16 * i: off + 16 * i + 16])
        out[nm.rstrip(b"\0").decode()] = wad[p:p + s]
    return out


def maps(pk3):
    with zipfile.ZipFile(pk3) as z:
        return {n[5:-4]: z.read(n) for n in z.namelist() if n.startswith("maps/") and n.endswith(".wad")}


BLOCK = re.compile(r"(\w+)\s*\{([^}]*)\}", re.S)
FIELD = re.compile(r"(\w+)\s*=\s*(\"[^\"]*\"|[^;]+);")


def parse(textmap):
    out = collections.defaultdict(list)
    for kind, body in BLOCK.findall(textmap.decode()):
        out[kind].append({k: v.strip() for k, v in FIELD.findall(body)})
    return out


SECTOR_LOOK = re.compile(r"^(texturefloor|textureceiling|color_\w+|lightcolor|[xy]panning\w+|[xy]scale\w+|rotation\w+)$")
SIDE_KEEP = {"sector"}
LINE_GEOM = {"v1", "v2", "sidefront", "sideback"}


def lines(m):
    V = [(float(v["x"]), float(v["y"])) for v in m["vertex"]]
    S = m["sidedef"]
    out = []
    for ld in m["linedef"]:
        a, b = V[int(ld["v1"])], V[int(ld["v2"])]
        fs = S[int(ld["sidefront"])]["sector"]
        bs = S[int(ld["sideback"])]["sector"] if "sideback" in ld else None
        props = tuple(sorted((k, v) for k, v in ld.items() if k not in LINE_GEOM))
        out.append((a, b, fs, bs, props))
    return out


def compare(plain, look):
    P, L = parse(plain), parse(look)
    res = []
    ok = True
    if P["thing"] != L["thing"]:
        ok = False
        res.append(f"THINGS DIFFER ({len(P['thing'])} plain, {len(L['thing'])} look)")
    else:
        res.append(f"things the same: {len(P['thing'])}")
    strip = lambda s: {k: v for k, v in s.items() if not SECTOR_LOOK.match(k)}
    if len(P["sector"]) != len(L["sector"]):
        ok = False
        res.append(f"SECTOR COUNT DIFFERS: {len(P['sector'])} plain, {len(L['sector'])} look")
    else:
        bad = [i for i, (a, b) in enumerate(zip(P["sector"], L["sector"])) if strip(a) != strip(b)]
        if bad:
            ok = False
            res.append(f"SECTORS DIFFER: {len(bad)}, e.g. {bad[0]}: {strip(P['sector'][bad[0]])} / {strip(L['sector'][bad[0]])}")
        else:
            res.append(f"sectors the same (heights, light, tags, specials, user fields): {len(P['sector'])}")
    spec = lambda m: collections.Counter(
        tuple((k, v) for k, v in sorted(ld.items()) if k == "special" or k.startswith("arg"))
        for ld in m["linedef"] if "special" in ld)
    sp, sl = spec(P), spec(L)
    if sp != sl:
        ok = False
        res.append(f"LINE SPECIALS DIFFER: {sum(sp.values())} plain, {sum(sl.values())} look")
    else:
        res.append(f"line specials the same: {sum(sp.values())} lines with a special, {len(sp)} kinds")
    lp, ll = lines(P), lines(L)
    index = collections.defaultdict(list)
    for ln in ll:
        index[(ln[2], ln[3])].append(ln)
    bad, split, used = [], 0, 0
    for a, b, fs, bs, props in lp:
        dx, dy = b[0] - a[0], b[1] - a[1]
        n2 = dx * dx + dy * dy
        cover = []
        for c, d, fs2, bs2, props2 in index[(fs, bs)]:
            if any(abs(dx * (v[1] - a[1]) - dy * (v[0] - a[0])) > 1e-6 * n2 ** 0.5 for v in (c, d)):
                continue
            t1 = ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / n2
            t2 = ((d[0] - a[0]) * dx + (d[1] - a[1]) * dy) / n2
            if t2 <= t1 or t2 <= 1e-9 or t1 >= 1 - 1e-9:
                continue
            cover.append((t1, t2, props2))
        cover.sort()
        pos, good = 0.0, True
        for t1, t2, props2 in cover:
            if abs(t1 - pos) > 1e-9 or props2 != props:
                good = False
            pos = t2
        if not good or abs(pos - 1) > 1e-9:
            bad.append((a, b))
        else:
            used += len(cover)
            split += len(cover) > 1
    if bad or used != len(ll):
        ok = False
        res.append(f"LINES DIFFER: {len(bad)} plain lines not matched (e.g. {bad[:3]}); {used} of the look's "
                   f"{len(ll)} lines on plain lines")
    else:
        res.append(f"lines the same once joined: {len(lp)} plain lines, {len(ll)} in the look ({split} cut into "
                   f"pieces, {len(ll) - len(lp)} pieces more), flags, specials, arguments, ids, sides' sectors")
    return ok, res


def main():
    a, b = maps(sys.argv[1]), maps(sys.argv[2])
    ok = True
    others = [n for n in a if n != "MAP33"]
    same = [n for n in others if a[n] == b.get(n)]
    if len(same) != len(others) or set(a) != set(b):
        ok = False
        print("OTHER MAPS DIFFER:", sorted(set(others) - set(same)), sorted(set(a) ^ set(b)))
    else:
        print(f"every other map the same, byte for byte: {len(others)}")
    pa, pb = lumps(a["MAP33"])["TEXTMAP"], lumps(b["MAP33"])["TEXTMAP"]
    if len(sys.argv) > 3:
        base = lumps(maps(sys.argv[3])["MAP33"])["TEXTMAP"]
        if base == pa:
            print(f"MAP33 plain: its TEXTMAP is the earlier build's, byte for byte ({len(pa)} bytes)")
        else:
            ok = False
            print("MAP33 PLAIN DIFFERS FROM THE EARLIER BUILD")
    good, res = compare(pa, pb)
    print("MAP33, the look against the plain level:")
    print("\n".join("    " + r for r in res))
    ok = ok and good
    print("all the same" if ok else "DIFFERENCES")
    sys.exit(0 if ok else 1)


main()
