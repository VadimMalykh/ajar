"""Where a wall's bands step: python3 tools/bandcheck.py build/ajar.pk3 MAP10 [-v]

Reads the level from the package (maps/<MAP>.wad) and the height of each
wall texture from its picture there. Every piece of wall that can be seen (a
one-sided wall; the upper or lower part of a two-sided line where there is
a step) is laid against the height of the world: the height at which the
texture's top row stands, modulo the texture's height (its phase). Then,
going round each room from one wall piece to the next that starts where it
ends (a corner, a jog, a doorway):

  STEP    two pieces of the same texture side by side, overlapping in
          height, whose phases differ: the bands and courses step there
          (Vadim, MAP10, 2026-11-26).
  LINTEL  the wall over (or under) an opening shows another texture than
          the walls either side of it, which are one texture: the wall does
          not carry on over the opening. Door faces, signs and the like are
          such lintels on purpose; -v lists them all, otherwise only those
          whose texture is plain wall elsewhere in the level (not a face).

Coordinates are the vertex where the two pieces meet. Nothing is changed.
"""
import collections
import re
import struct
import sys
import zipfile


def parse(text):
    out = collections.defaultdict(list)
    for kind, body in re.findall(r"(\w+)\{([^}]*)\}", text):
        d = {}
        for k, v in re.findall(r"(\w+)=([^;]*);", body):
            d[k] = v.strip('"') if v.startswith('"') else True if v == "true" else False if v == "false" else float(v)
        out[kind].append(d)
    return out


def textmap(wad):
    n, at = struct.unpack("<ii", wad[4:12])
    for i in range(n):
        pos, size, name = struct.unpack("<ii8s", wad[at + 16 * i:at + 16 * i + 16])
        if name.rstrip(b"\0") == b"TEXTMAP":
            return wad[pos:pos + size].decode()
    raise ValueError("no TEXTMAP")


def heights(z):
    """{texture name: height} from the package's pictures (PNG)."""
    out = {}
    for name in z.namelist():
        if name.startswith("textures/") and name.lower().endswith(".png"):
            head = z.open(name).read(24)
            out[name[9:-4].upper()] = struct.unpack(">I", head[20:24])[0]
    return out


def pieces(t, H):
    """Every piece of wall that shows: dict(tex, lo, hi, phase, a, b, line, part).
    a-b is the piece as its own room sees it, left to right."""
    V = [(v["x"], v["y"]) for v in t["vertex"]]
    S, SD = t["sector"], t["sidedef"]
    out = []
    for li, ld in enumerate(t["linedef"]):
        v1, v2 = V[int(ld["v1"])], V[int(ld["v2"])]
        sides = [("sidefront", "sideback", v1, v2), ("sideback", "sidefront", v2, v1)]
        for mine, other, a, b in sides:
            if mine not in ld:
                continue
            sd = SD[int(ld[mine])]
            s = S[int(sd["sector"])]
            f, c = s.get("heightfloor", 0.0), s.get("heightceiling", 0.0)
            if other not in ld:
                tex = sd.get("texturemiddle", "-")
                h = H.get(tex)
                if h and c > f:
                    ref = f + h if ld.get("dontpegbottom") else c
                    oy = sd.get("offsety_mid", 0.0) + sd.get("offsety", 0.0)
                    out.append(dict(tex=tex, lo=f, hi=c, phase=(ref + oy) % h, a=a, b=b, line=li, part="mid"))
                continue
            o = S[int(SD[int(ld[other])]["sector"])]
            of, oc = o.get("heightfloor", 0.0), o.get("heightceiling", 0.0)
            sky = s.get("textureceiling") == "F_SKY1" and o.get("textureceiling") == "F_SKY1"
            tex = sd.get("texturetop", "-")
            h = H.get(tex)
            if h and c > oc and not sky:
                ref = c if ld.get("dontpegtop") else oc + h
                oy = sd.get("offsety_top", 0.0) + sd.get("offsety", 0.0)
                out.append(dict(tex=tex, lo=max(oc, f), hi=c, phase=(ref + oy) % h, a=a, b=b, line=li, part="top"))
            tex = sd.get("texturebottom", "-")
            h = H.get(tex)
            if h and of > f:
                ref = c if ld.get("dontpegbottom") else of
                oy = sd.get("offsety_bottom", 0.0) + sd.get("offsety", 0.0)
                out.append(dict(tex=tex, lo=f, hi=min(of, c), phase=(ref + oy) % h, a=a, b=b, line=li, part="bottom"))
    return out


def check(t, H, verbose=False):
    P = pieces(t, H)
    starts = collections.defaultdict(list)
    for p in P:
        starts[p["a"]].append(p)
    plain = {p["tex"] for p in P if p["part"] == "mid"}       # what is wall somewhere, not only over openings
    steps, lintels = [], []
    for p in P:
        for q in starts[p["b"]]:
            if q is p or min(p["hi"], q["hi"]) <= max(p["lo"], q["lo"]):
                continue
            if p["tex"] == q["tex"] and abs(p["phase"] - q["phase"]) > 0.01:
                h = H[p["tex"]]
                d = (q["phase"] - p["phase"]) % h
                steps.append((p["b"], p["tex"], min(d, h - d) * (1 if d <= h / 2 else -1), p, q))
    # a lintel: a piece over or under an opening (top or bottom) with the same
    # wall texture before and after it, its own another
    for p in P:
        if p["part"] == "mid":
            continue
        before = [q for q in P if q["b"] == p["a"] and q["tex"] != p["tex"] and q["part"] == "mid"
                  and q["lo"] < p["hi"] and q["hi"] > p["lo"]]
        after = [q for q in starts[p["b"]] if q["tex"] != p["tex"] and q["part"] == "mid"
                 and q["lo"] < p["hi"] and q["hi"] > p["lo"]]
        both = {q["tex"] for q in before} & {q["tex"] for q in after}
        if both and (verbose or p["tex"] in plain):
            lintels.append((p, sorted(both)))
    return steps, lintels


def main():
    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv
    pk3, name = args[0], args[1]
    with zipfile.ZipFile(pk3) as z:
        H = heights(z)
        t = parse(textmap(z.read(f"maps/{name}.wad")))
    steps, lintels = check(t, H, verbose)
    seen = set()
    for at, tex, d, p, q in sorted(steps, key=lambda s: (s[1], s[0])):
        key = (at, tex, round(d, 2))
        if key in seen:
            continue
        seen.add(key)
        print(f"STEP   {tex:8} at ({at[0]:g}, {at[1]:g}): {d:+g} (lines {p['line']} {p['part']} {p['lo']:g}..{p['hi']:g}"
              f" -> {q['line']} {q['part']} {q['lo']:g}..{q['hi']:g})")
    for p, both in lintels:
        print(f"LINTEL {p['tex']:8} over ({p['a'][0]:g}, {p['a'][1]:g})-({p['b'][0]:g}, {p['b'][1]:g}) "
              f"{p['lo']:g}..{p['hi']:g}, line {p['line']} {p['part']}, between {', '.join(both)}")
    print(f"{name}: {len(seen)} steps, {len(lintels)} lintels")


if __name__ == "__main__":
    main()
