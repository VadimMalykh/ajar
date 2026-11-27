"""MAP23's look against the plain level: nothing moved (tools/dogs23.py; the model is tools/power33_compare.py).

    python3 tools/dogs_compare.py build/plain.pk3 build/look1.pk3 [build/main.pk3]

1. Every map but MAP23 is the same, byte for byte, in the two builds.
2. MAP23 with the look against the plain one, textures, offsets, scales and line splits set aside:
   - the things the same (every field, in order), but for the decor appended after them: each of those one of
     dogs.zs's three (20199, 20202, 20203), with no tid, no special, args (look 1..3, 0 or 1);
   - the sectors the same (count and every field but their flats, panning, scales and colours: heights, light,
     tags, specials, user fields), but for the sky tag (2380) on THEN's sky sectors, which had none;
   - the lines the same once the pieces the look cut out of a line are joined again (each plain line covered
     exactly by lines of the look on it, every one with the plain line's flags, special, arguments, id and its
     sides' sectors), the sky transfer's special (190, 2380, 255) set aside on the one line that has it;
   - the multiset of line specials the same, plus that one sky transfer.
With a third build (main's package): the first build's MAP23 TEXTMAP and every other map are main's, byte for
byte, and the other files of the package that differ are listed (AJAR_DOGS unset changes no map).
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
LINE_GEOM = {"v1", "v2", "sidefront", "sideback"}
DECOR = {"20199", "20202", "20203"}
SKY_TAG = "2380"
SKY_LINE = (("arg0", SKY_TAG), ("arg1", "255"), ("special", "190"))


def lines(m, drop_sky=False):
    V = [(float(v["x"]), float(v["y"])) for v in m["vertex"]]
    S = m["sidedef"]
    out = []
    for ld in m["linedef"]:
        a, b = V[int(ld["v1"])], V[int(ld["v2"])]
        fs = S[int(ld["sidefront"])]["sector"]
        bs = S[int(ld["sideback"])]["sector"] if "sideback" in ld else None
        props = {k: v for k, v in ld.items() if k not in LINE_GEOM}
        if drop_sky and props.get("special") == "190" and props.get("arg0") == SKY_TAG:
            for k in ("special", "arg0", "arg1"):
                props.pop(k)
        out.append((a, b, fs, bs, tuple(sorted(props.items()))))
    return out


def compare(plain, look):
    P, L = parse(plain), parse(look)
    res, ok = [], True
    n = len(P["thing"])
    extra = L["thing"][n:]
    bad_extra = [t for t in extra if t.get("type") not in DECOR or "id" in t or "special" in t
                 or t.get("arg0") not in ("1", "2", "3") or t.get("arg1", "0") not in ("0", "1")]
    if P["thing"] != L["thing"][:n] or bad_extra:
        ok = False
        res.append(f"THINGS DIFFER ({n} plain, {len(L['thing'])} look; {len(bad_extra)} added that are not decor)")
    else:
        kinds = collections.Counter(t["type"] for t in extra)
        res.append(f"things the same: {n}, and {len(extra)} decor after them ({dict(kinds)})")
    strip = lambda s: {k: v for k, v in s.items() if not SECTOR_LOOK.match(k)}
    if len(P["sector"]) != len(L["sector"]):
        ok = False
        res.append(f"SECTOR COUNT DIFFERS: {len(P['sector'])} plain, {len(L['sector'])} look")
    else:
        bad, tagged = [], 0
        for i, (a, b) in enumerate(zip(P["sector"], L["sector"])):
            a, b = strip(a), strip(b)
            if "id" not in a and b.get("id") == SKY_TAG:
                b = dict(b)
                b.pop("id")
                tagged += 1
            if a != b:
                bad.append(i)
        if bad:
            ok = False
            res.append(f"SECTORS DIFFER: {len(bad)}, e.g. {bad[0]}: {strip(P['sector'][bad[0]])} / "
                       f"{strip(L['sector'][bad[0]])}")
        else:
            res.append(f"sectors the same (heights, light, tags, specials, user fields): {len(P['sector'])}; "
                       f"{tagged} of THEN's sky sectors tagged {SKY_TAG}")
    spec = lambda m: collections.Counter(
        tuple((k, v) for k, v in sorted(ld.items()) if k == "special" or k.startswith("arg"))
        for ld in m["linedef"] if "special" in ld)
    sp, sl = spec(P), spec(L)
    sky = collections.Counter({SKY_LINE: 1})
    if sp + sky != sl:
        ok = False
        res.append(f"LINE SPECIALS DIFFER: {sum(sp.values())} plain, {sum(sl.values())} look")
    else:
        res.append(f"line specials the same: {sum(sp.values())} lines with a special, {len(sp)} kinds; and the "
                   f"one sky transfer")
    lp, ll = lines(P), lines(L, drop_sky=True)
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
    others = [n for n in a if n != "MAP23"]
    same = [n for n in others if a[n] == b.get(n)]
    if len(same) != len(others) or set(a) != set(b):
        ok = False
        print("OTHER MAPS DIFFER:", sorted(set(others) - set(same)), sorted(set(a) ^ set(b)))
    else:
        print(f"every other map the same, byte for byte: {len(others)}")
    pa, pb = lumps(a["MAP23"])["TEXTMAP"], lumps(b["MAP23"])["TEXTMAP"]
    if len(sys.argv) > 3:
        base = maps(sys.argv[3])
        if lumps(base["MAP23"])["TEXTMAP"] == pa:
            print(f"MAP23 plain: its TEXTMAP is main's, byte for byte ({len(pa)} bytes)")
        else:
            ok = False
            print("MAP23 PLAIN DIFFERS FROM MAIN'S")
        mo = [n for n in base if base[n] != a.get(n)]
        print(f"the plain build's maps against main's: {len(base) - len(mo)} of {len(base)} byte for byte"
              + (f"; DIFFER: {mo}" if mo else ""))
        ok = ok and not mo and set(base) == set(a)
        with zipfile.ZipFile(sys.argv[1]) as z1, zipfile.ZipFile(sys.argv[3]) as z3:
            n1, n3 = set(z1.namelist()), set(z3.namelist())
            diff = sorted(n for n in n1 & n3 if z1.read(n) != z3.read(n))
            print(f"the plain package against main's: {len(n1 & n3) - len(diff)} files the same; differ: {diff}; "
                  f"only in the plain build: {sorted(n1 - n3)}; only in main's: {sorted(n3 - n1)}")
    good, res = compare(pa, pb)
    print("MAP23, the look against the plain level:")
    print("\n".join("    " + r for r in res))
    ok = ok and good
    print("all the same" if ok else "DIFFERENCES")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
