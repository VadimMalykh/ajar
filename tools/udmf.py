"""Tiny UDMF map builder.

Sectors are declared as clockwise polygons (y up). Edges shared by two
sectors become two-sided lines automatically; edges are split wherever
another sector's vertex lies on them, so rooms only need to touch.
"""
import struct


def rect(x1, y1, x2, y2):
    return [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]


def _clockwise(poly):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))
    return poly if area < 0 else poly[::-1]


class Map:
    def __init__(self):
        self.sectors = []      # dicts
        self.polys = []
        self.lineprops = {}    # frozenset({a, b}) -> dict
        self.things = []
        self.cuts = set()      # extra vertices that split the edges they lie on

    def sector(self, poly, floor=0, ceil=192, light=200, wall="AJWALL",
               ftex="AJFLOOR", ctex="AJCEIL", color=None, side=None, id=0, special=0, raw=None):
        """`wall` is what the sector's own walls show; `side` (default: the
        same) is what a step up to it shows, e.g. the side of a bed. `raw` is
        a dict of further UDMF sector properties (lightfloor and the like)."""
        self.polys.append(_clockwise([tuple(p) for p in poly]))
        self.sectors.append(dict(floor=floor, ceil=ceil, light=light, wall=wall,
                                 ftex=ftex, ctex=ctex, color=color, side=side or wall,
                                 id=id, special=special, raw=raw or {}))
        return len(self.sectors) - 1

    def line(self, a, b, **props):
        """Attach properties (id, special, args, mid, flags...) to the edge a-b."""
        self.lineprops.setdefault(frozenset((tuple(a), tuple(b))), {}).update(props)

    def cut(self, *points):
        """Split whatever edge each point lies on, so that part of a wall can
        be given its own texture with line()."""
        self.cuts.update(tuple(p) for p in points)

    def thing(self, x, y, type, angle=0, **props):
        self.things.append(dict(x=x, y=y, type=type, angle=angle, **props))

    # ------------------------------------------------------------------
    def _split(self):
        allv = {v for p in self.polys for v in p} | self.cuts
        out = []
        for poly in self.polys:
            new = []
            for a, b in zip(poly, poly[1:] + poly[:1]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                mids = []
                for v in allv:
                    if v in (a, b):
                        continue
                    px, py = v[0] - a[0], v[1] - a[1]
                    if dx * py - dy * px != 0:
                        continue
                    t = (px * dx + py * dy) / (dx * dx + dy * dy)
                    if 0 < t < 1:
                        mids.append((t, v))
                new.append(a)
                new.extend(v for _, v in sorted(mids))
            out.append(new)
        return out

    def textmap(self):
        polys = self._split()
        # line properties given for an unsplit edge apply to all its pieces
        def props_for(a, b):
            p = self.lineprops.get(frozenset((a, b)))
            if p is not None:
                return p
            for key, val in self.lineprops.items():
                p1, p2 = tuple(key)
                dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                ok = True
                for v in (a, b):
                    px, py = v[0] - p1[0], v[1] - p1[1]
                    t = (px * dx + py * dy) / (dx * dx + dy * dy)
                    if dx * py - dy * px != 0 or not 0 <= t <= 1:
                        ok = False
                if ok and not val.get("exact"):
                    return val
            return {}

        verts, vidx = [], {}
        def vi(v):
            if v not in vidx:
                vidx[v] = len(verts)
                verts.append(v)
            return vidx[v]

        edges = {}
        for si, poly in enumerate(polys):
            for a, b in zip(poly, poly[1:] + poly[:1]):
                if (a, b) in edges:
                    raise ValueError(f"overlapping sectors at edge {a}-{b}")
                edges[(a, b)] = si

        lines, sides = [], []
        def side(si, **tex):
            sides.append(dict(sector=si, **tex))
            return len(sides) - 1

        done = set()
        for (a, b), si in edges.items():
            if (a, b) in done:
                continue
            p = dict(props_for(a, b))
            p.pop("exact", None)
            mid = p.pop("mid", None)
            midboth = p.pop("midboth", False)
            lower = p.pop("lower", None)           # texture of the step, both sides
            upper = p.pop("upper", None)           # texture above the opening, both sides
            s = self.sectors[si]
            ld = dict(v1=vi(a), v2=vi(b))
            other = edges.get((b, a))
            if other is None:
                ld["sidefront"] = side(si, texturemiddle=mid or s["wall"])
                ld["blocking"] = True
            else:
                done.add((b, a))
                o = self.sectors[other]
                front = dict(texturetop=upper or o["wall"], texturebottom=lower or o["side"])
                if mid:
                    front["texturemiddle"] = mid
                ld["sidefront"] = side(si, **front)
                back = dict(texturetop=upper or s["wall"], texturebottom=lower or s["side"])
                if mid and midboth:
                    back["texturemiddle"] = mid
                ld["sideback"] = side(other, **back)
                ld["twosided"] = True
            args = p.pop("args", ())
            for i, v in enumerate(args):
                if v:
                    ld[f"arg{i}"] = v
            ld.update(p)
            lines.append(ld)

        def val(v):
            if isinstance(v, bool):
                return "true" if v else "false"
            if isinstance(v, str):
                return '"%s"' % v
            return str(v)

        def block(kind, d):
            return kind + "{" + "".join(f"{k}={val(v)};" for k, v in d.items()) + "}\n"

        out = ['namespace="zdoom";\n']
        for x, y in verts:
            out.append(block("vertex", dict(x=float(x), y=float(y))))
        for ld in lines:
            out.append(block("linedef", ld))
        for sd in sides:
            out.append(block("sidedef", sd))
        for s in self.sectors:
            d = dict(heightfloor=s["floor"], heightceiling=s["ceil"], texturefloor=s["ftex"],
                     textureceiling=s["ctex"], lightlevel=s["light"])
            for extra in ("id", "special"):
                if s[extra]:
                    d[extra] = s[extra]
            if s["color"] is not None:
                # Tint the room's surfaces only. "lightcolor" would tint sprites
                # too, and a door must keep its own colour wherever it stands.
                for part in ("floor", "ceiling", "walltop", "wallbottom"):
                    d["color_" + part] = s["color"]
            d.update(s["raw"])
            out.append(block("sector", d))
        for t in self.things:
            d = dict(t)
            d["x"], d["y"] = float(d["x"]), float(d["y"])
            args = d.pop("args", ())
            for i, v in enumerate(args):
                if v:
                    d[f"arg{i}"] = v
            for f in ("skill1", "skill2", "skill3", "skill4", "skill5", "single", "coop", "dm"):
                d[f] = True
            out.append(block("thing", d))
        return "".join(out)

    def wad(self, name="MAP01"):
        lumps = [(name, b""), ("TEXTMAP", self.textmap().encode()), ("ENDMAP", b"")]
        data, direc, pos = b"", b"", 12
        for n, d in lumps:
            direc += struct.pack("<ii8s", pos, len(d), n.encode())
            data += d
            pos += len(d)
        return b"PWAD" + struct.pack("<ii", len(lumps), pos) + data + direc
