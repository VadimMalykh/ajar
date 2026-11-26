"""Doors beside walls and switches, from the built maps: python3 tools/leafcheck.py [build/ajar.pk3] [MAP21 ...]

Reads every map of the package (or those named) and reports two things
(PLAN.md, "Doors: the open leaf keeps clear of walls; USE at a lever works the
lever"):

  LEAF  each frame whose door's leaf, posed as the engine posed every leaf until
        2026-11-26 (hinged at the jamb of the frame line's first end, 16 out from
        the frame line, swung open 115 degrees, 64 long), comes within 2 of a
        wall or cuts into one, and what the rule now makes of it (the same
        reckoning as AjarLeafRoom in src/zscript/leaf.zs): hinged on the
        other jamb if that is clear, else opened less, to the widest angle clear
        at either jamb, and as before if none is. A wall: a one-sided line, or
        a two-sided one whose opening is lower than the leaf (96) or whose floor
        is higher than the frame's; and the leaf stands on open floor all along.
        Things (furniture) are not walls. -v lists the clear frames too.
  NEAR  each switch (a line with a special that the player USEs, not a frame's
        own mouth) within 96 of a frame's mouth or of a far side's.

No map is changed: this only reads. The maps are parsed from their TEXTMAP lumps.
In docker: docker run --rm -u "$(id -u):$(id -g)" -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD":/work -w /work
ajar-tools python3 tools/leafcheck.py
"""
import math
import re
import struct
import sys
import zipfile

FRAME_T = 20001
LEAF, OPEN, CLEAR, DEPTH, NEAR = 64.0, 115.0, 2.0, 16.0, 96.0


def parse(text):
    out = {"vertex": [], "linedef": [], "sidedef": [], "sector": [], "thing": []}
    for kind, body in re.findall(r"(\w+)\s*\{([^}]*)\}", text):
        d = {}
        for k, v in re.findall(r"(\w+)\s*=\s*([^;]*);", body):
            v = v.strip()
            d[k] = v.strip('"') if v.startswith('"') else True if v == "true" else False if v == "false" else float(v)
        out.setdefault(kind, []).append(d)
    return out


def textmap(wad):
    n, off = struct.unpack("<4xii", wad[:12])
    for i in range(n):
        o, size, name = struct.unpack("<ii8s", wad[off + 16 * i: off + 16 * i + 16])
        if name.rstrip(b"\0") == b"TEXTMAP":
            return wad[o:o + size].decode("latin-1")
    return None


def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def mul(a, s): return (a[0] * s, a[1] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def cross(a, b): return a[0] * b[1] - a[1] * b[0]
def length(a): return math.hypot(a[0], a[1])


def pdist(p, a, b):
    """The distance from p to the segment a-b."""
    d = sub(b, a)
    n = dot(d, d)
    t = 0 if n == 0 else max(0, min(1, dot(sub(p, a), d) / n))
    return length(sub(p, add(a, mul(d, t))))


def crosses(p, q, a, b):
    """The segments p-q and a-b cross (touching counts); returns the parameter along p-q, or None."""
    r, s = sub(q, p), sub(b, a)
    den = cross(r, s)
    if abs(den) < 1e-12:
        return None
    t = cross(sub(a, p), s) / den
    u = cross(sub(a, p), r) / den
    return t if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9 else None


class Level:
    def __init__(self, name, t):
        self.name = name
        self.t = t
        self.v = [(p["x"], p["y"]) for p in t["vertex"]]
        self.lines = []
        for i, ld in enumerate(t["linedef"]):
            a, b = self.v[int(ld["v1"])], self.v[int(ld["v2"])]
            fs = t["sidedef"][int(ld["sidefront"])] if "sidefront" in ld else None
            bs = t["sidedef"][int(ld["sideback"])] if "sideback" in ld else None
            front = t["sector"][int(fs["sector"])] if fs else None
            back = t["sector"][int(bs["sector"])] if bs else None
            ids = {int(ld.get("id", 0))} | {int(x) for x in str(ld.get("moreids", "")).split() if x}
            self.lines.append(dict(i=i, a=a, b=b, front=front, back=back, ids=ids, ld=ld,
                                   special=int(ld.get("special", 0)),
                                   args=[int(ld.get(f"arg{k}", 0)) for k in range(5)]))
        self.frames = [th for th in t["thing"] if int(th["type"]) == FRAME_T]
        self.frame_ids = {int(th.get("arg0", 0)) for th in self.frames}

    def line_by_id(self, i):
        for l in self.lines:
            if i in l["ids"]:
                return l
        return None

    def solid(self, l, z):
        """A wall for a leaf standing from z to z + 96 (flat sectors: these maps have no slopes at frames)."""
        if l["back"] is None or l["front"] is None:
            return True
        f, b = l["front"], l["back"]
        top = min(f.get("heightceiling", 0), b.get("heightceiling", 0))
        bottom = max(f.get("heightfloor", 0), b.get("heightfloor", 0))
        return top < z + 96 - 1 or bottom > z + 1

    def sector_at(self, p):
        """The sector p is in (the nearest line east of it, and its side), or None: outside the map."""
        best, sec = None, None
        for l in self.lines:
            a, b = l["a"], l["b"]
            if (a[1] > p[1]) == (b[1] > p[1]):
                continue
            x = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x >= p[0] and (best is None or x < best):
                best = x
                sec = l["front"] if cross(sub(b, a), sub(p, a)) < 0 else l["back"]
        return sec


class Room:
    """The walls round the frame on line l that a leaf (z to z + 96) hung at either jamb might reach, and the
    reckoning of AjarLeafRoom in src/zscript/leaf.zs."""

    def __init__(self, lv, l, z):
        self.lv, self.l, self.z = lv, l, z
        at = mul(add(l["a"], l["b"]), 0.5)
        r = length(sub(l["b"], l["a"])) / 2 + DEPTH + LEAF + 2 * CLEAR
        self.walls = [w for w in lv.lines if lv.solid(w, z) and pdist(at, w["a"], w["b"]) < r]

    def pose(self, mirrored, open_):
        """The leaf: (hinge, far end), as AjarLeafRoom.Hinge and Way."""
        a, b = self.l["a"], self.l["b"]
        d = sub(b, a)
        dl = length(d)
        dr = (d[0] / dl, d[1] / dl)
        n = (dr[1], -dr[0])
        hinge = add(b if mirrored else a, mul(n, DEPTH))
        shut = mul(dr, -1) if mirrored else dr
        if not mirrored and open_ == OPEN:
            u = sub(mul(n, math.cos(math.radians(25))), mul(dr, math.sin(math.radians(25))))
        else:
            u = add(mul(shut, math.cos(math.radians(open_))), mul(n, math.sin(math.radians(open_))))
        return hinge, add(hinge, mul(u, LEAF))

    def blocked(self, mirrored, open_):
        """What the leaf comes within CLEAR of or stands in, or None: it is clear (AjarLeafRoom.Clear)."""
        h, e = self.pose(mirrored, open_)
        for w in self.walls:
            a, b = w["a"], w["b"]
            why = f"line {w['i']} ({a[0]:.0f},{a[1]:.0f})-({b[0]:.0f},{b[1]:.0f})"
            if pdist(h, a, b) < 1:
                # a wall at the hinge (the room's wall beside the frame, the recess's side): its other end and the
                # leaf's end count (and the points below: which side of it the leaf is on)
                if pdist(e, a, b) < CLEAR:
                    return why
                for p in (a, b):
                    if length(sub(p, h)) >= 1 and pdist(p, h, e) < CLEAR:
                        return why
                continue
            if crosses(h, e, a, b) is not None or min(pdist(e, a, b), pdist(a, h, e), pdist(b, h, e)) < CLEAR:
                return why
        # every 4 along the leaf from 2 out: in the map, on a floor no higher than the leaf's foot, under a ceiling
        # no lower than its top
        for k in range(17):
            s = min(2 + 4 * k, LEAF)
            p = add(h, mul(sub(e, h), s / LEAF))
            sec = self.lv.sector_at(p)
            if sec is None:
                return f"outside the map at ({p[0]:.0f},{p[1]:.0f})"
            if sec.get("heightfloor", 0) > self.z + 1 or sec.get("heightceiling", 0) < self.z + 96 - 1:
                return f"floor {sec.get('heightfloor', 0):.0f} ceiling {sec.get('heightceiling', 0):.0f} at ({p[0]:.0f},{p[1]:.0f})"
        return None

    def widest(self):
        """The widest opening (degrees, to about 0.0002) at which the leaf is clear at a jamb: (mirrored, angle), the
        frame line's first end winning a tie; None: clear at neither, at any whole degree from 114 down to 1."""
        best = None
        for mirrored in (False, True):
            a = OPEN - 1
            while a >= 1 and self.blocked(mirrored, a):
                a -= 1
            if a < 1:
                continue
            lo, hi = a, a + 1
            for _ in range(12):
                mid = (lo + hi) / 2
                if self.blocked(mirrored, mid):
                    hi = mid
                else:
                    lo = mid
            if best is None or lo > best[1] + 0.001:     # (a tie, to rounding: the first jamb)
                best = (mirrored, lo)
        return best


def frame_z(lv, l):
    return (l["front"] or {}).get("heightfloor", 0)


def report(lv, verbose):
    out = []
    for th in sorted(lv.frames, key=lambda th: int(th.get("arg0", 0))):
        fid = int(th.get("arg0", 0))
        l = lv.line_by_id(fid)
        if not l:
            continue
        r = Room(lv, l, frame_z(lv, l))
        why = r.blocked(False, OPEN)
        if not why:
            if verbose:
                h, e = r.pose(False, OPEN)
                out.append(f"LEAF {lv.name} frame {fid}: clear as posed (hinge {h[0]:.1f},{h[1]:.1f})")
            continue
        other = r.blocked(True, OPEN)
        if not other:
            out.append(f"LEAF {lv.name} frame {fid}: cuts {why}; hinged on the other jamb instead")
            continue
        best = r.widest()
        now = "nothing is clear: posed as before" if not best else \
            f"opened {best[1]:.2f} degrees{', hinged on the other jamb' if best[0] else ''}"
        out.append(f"LEAF {lv.name} frame {fid}: cuts {why}; the other jamb too ({other}); {now}")
    return out


def switches(lv):
    out = []
    mouths = []
    for l in lv.lines:
        if l["special"] != 156:
            continue
        fid = min(l["ids"] - {0}, default=0)
        a, b = l["a"], l["b"]
        d = sub(b, a)
        n = (d[1] / length(d), -d[0] / length(d))
        kind = "frame" if fid in lv.frame_ids else "far side"
        mouths.append((kind, fid, add(a, mul(n, DEPTH)), add(b, mul(n, DEPTH))))
    for s in lv.lines:
        if not s["special"] or not s["ld"].get("playeruse"):
            continue
        if s["special"] == 130 and s["args"][0] in lv.frame_ids:
            continue                # a frame's own mouth
        for kind, fid, a, b in mouths:
            dist = min(pdist(s["a"], a, b), pdist(s["b"], a, b), pdist(a, s["a"], s["b"]), pdist(b, s["a"], s["b"]))
            if crosses(s["a"], s["b"], a, b) is not None:
                dist = 0
            if dist <= NEAR:
                mid = mul(add(s["a"], s["b"]), 0.5)
                out.append(f"NEAR {lv.name} line {s['i']} special {s['special']}({','.join(map(str, s['args']))}) "
                           f"at ({mid[0]:.0f},{mid[1]:.0f}) {length(sub(s['b'], s['a'])):.0f} long: "
                           f"{dist:.0f} from {kind} {fid}")
    return out


def main():
    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv
    pk3 = args.pop(0) if args and args[0].endswith(".pk3") else "build/ajar.pk3"
    z = zipfile.ZipFile(pk3)
    names = sorted(n for n in z.namelist() if n.startswith("maps/") and n.endswith(".wad"))
    if args:
        names = [n for n in names if n[5:-4] in args]
    for n in names:
        tm = textmap(z.read(n))
        if not tm:
            continue
        lv = Level(n[5:-4], parse(tm))
        for line in report(lv, verbose) + switches(lv):
            print(line)


if __name__ == "__main__":
    main()
