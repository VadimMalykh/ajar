"""Tiny UDMF map builder.

Sectors are declared as clockwise polygons (y up). Edges shared by two
sectors become two-sided lines automatically; edges are split wherever
another sector's vertex lies on them, so rooms only need to touch.
"""
import struct

# Doom's monsters by editor number: zombie, sergeant, imp, demon, spectre,
# chaingunner, knight, baron, revenant, lost soul, cacodemon, mancubus,
# arachnotron, pain elemental, arch-vile, cyberdemon, spider mastermind
MONSTERS = {3004, 9, 3001, 3002, 58, 65, 69, 3003, 66, 3006, 3005, 67, 68, 71, 64, 16, 7}


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
        self.align = set()     # textures laid by world position, not from each line's start

    def sector(self, poly, floor=0, ceil=192, light=200, wall="AJWALL",
               ftex="AJFLOOR", ctex="AJCEIL", color=None, side=None, id=0, special=0, raw=None, lift=0):
        """`wall` is what the sector's own walls show; `side` (default: the
        same) is what a step up to it shows, e.g. the side of a bed. `raw` is
        a dict of further UDMF sector properties (lightfloor and the like).
        `lift` says the ceiling is that much higher than the room's (a strip
        of lights): walls hung from the ceiling are then drawn that much
        lower, so that they stay in line with the rest of the room's."""
        self.polys.append(_clockwise([tuple(p) for p in poly]))
        self.sectors.append(dict(floor=floor, ceil=ceil, light=light, wall=wall,
                                 ftex=ftex, ctex=ctex, color=color, side=side or wall,
                                 id=id, special=special, raw=raw or {}, lift=lift))
        return len(self.sectors) - 1

    def line(self, a, b, **props):
        """Attach properties (id, special, args, mid, flags...) to the edge a-b."""
        self.lineprops.setdefault(frozenset((tuple(a), tuple(b))), {}).update(props)

    def cut(self, *points):
        """Split whatever edge each point lies on, so that part of a wall can
        be given its own texture with line()."""
        self.cuts.update(tuple(p) for p in points)

    def thing(self, x, y, type, angle=0, **props):
        """`skill=N` (1 to 4): the thing is only there from that difficulty up.
        Without it, Doom's monsters are thinned on the two easier ones (see
        _skills); everything else is there on all of them."""
        self.things.append(dict(x=x, y=y, type=type, angle=angle, **props))

    def _skills(self):
        """The lowest difficulty each thing is there on (mapinfo.txt: 1 "Just
        visiting", 2 "Short stay", 3 "Resident", the level as designed, 4
        "Night shift"). Of each kind of Doom monster, in the order they were
        placed, 1 keeps every second one and 2 three in four; the first of a
        kind is always kept. Ajar's own monsters are part of the puzzle and
        are never thinned."""
        seen, out = {}, []
        for t in self.things:
            if "skill" in t:
                out.append(t["skill"])
            elif t["type"] in MONSTERS:
                i = seen[t["type"]] = seen.get(t["type"], -1) + 1
                out.append(1 if i % 2 == 0 else 3 if i % 4 == 3 else 2)
            else:
                out.append(1)
        return out

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
                if ok:
                    # a line that is one picture (exact) and has been cut by
                    # something else all the same: each piece shows its part
                    return dict(val, whole=(p1, p2)) if val.get("exact") else val
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

        # A line given for part of a wall must end at corners of the map: a
        # piece of wall that runs past its end would get none of its
        # properties (a railing with a hole in it). cut() makes the corners.
        for key, val in self.lineprops.items():
            p1, p2 = tuple(key)
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            for a, b in edges:
                ts = [((v[0] - p1[0]) * dx + (v[1] - p1[1]) * dy) / (dx * dx + dy * dy) for v in (a, b)
                      if dx * (v[1] - p1[1]) - dy * (v[0] - p1[0]) == 0]
                if len(ts) == 2 and max(ts) > 0 and min(ts) < 1 and (min(ts) < 0 or max(ts) > 1):
                    raise ValueError(f"line {p1}-{p2} ({', '.join(sorted(val))}) ends inside the wall piece {a}-{b}: cut() it")

        lines, sides = [], []
        def side(si, a=None, b=None, hung=(), drop=0, fit=None, whole=None, **tex):
            # a wall texture in self.align starts at its place in the world,
            # so a wall cut into pieces (furniture, openings) shows no seams.
            # Such textures must be 64 wide and symmetric left to right.
            # On a slanting wall they are laid from `fit`: (a point of the
            # wall, usually its end; a stretch that makes the whole wall a
            # number of 64s long).
            d = dict(sector=si, **tex)
            if a and whole:                    # a piece of one picture: see props_for
                o = min(whole, key=lambda q: (q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1]))
                u = ((a[0] - o[0]) ** 2 + (a[1] - o[1]) ** 2) ** 0.5
                laid = tex.get("texturetop") in self.align       # the wall over a hung sign stays in its place
                if u:                          # (a door's face is the wall over its sunk leaf)
                    d["offsetx_mid"] = float(u)
                    if not laid:
                        d["offsetx_top"] = float(u)
                if laid and (a[0] == b[0] or a[1] == b[1]):
                    w = (a[0] if b[0] > a[0] else -a[0]) if a[1] == b[1] else (a[1] if b[1] > a[1] else -a[1])
                    if w % 64:
                        d["offsetx_top"] = float(w % 64)
            elif a and fit:
                (ox, oy), scale = fit
                u = (((a[0] - ox) ** 2 + (a[1] - oy) ** 2) ** 0.5 * scale) % 64
                for part in ("top", "mid", "bottom"):
                    if tex.get("texture" + ("middle" if part == "mid" else part)) in self.align:
                        d["scalex_" + part] = scale
                        if 0.01 < u < 63.99:
                            d["offsetx_" + part] = round(u, 3)
            elif a and (a[0] == b[0] or a[1] == b[1]):
                u = (a[0] if b[0] > a[0] else -a[0]) if a[1] == b[1] else (a[1] if b[1] > a[1] else -a[1])
                for part in ("top", "mid", "bottom"):
                    if tex.get("texture" + ("middle" if part == "mid" else part)) in self.align and u % 64:
                        d["offsetx_" + part] = float(u % 64)
            for part in hung:                  # see sector(lift=)
                if self.sectors[si]["lift"]:
                    d["offsety_" + part] = float(-self.sectors[si]["lift"])
            if drop:                           # see floorpeg
                d["offsety_bottom"] = d.get("offsety_bottom", 0.0) + drop
            sides.append(d)
            return len(sides) - 1

        done = set()
        for (a, b), si in edges.items():
            if (a, b) in done:
                continue
            p = dict(props_for(a, b))
            p.pop("exact", None)
            fit = p.pop("fit", None)               # see side()
            whole = p.pop("whole", None)
            midraise = p.pop("midraise", 0)        # the middle texture stands this much higher
            mid = p.pop("mid", None)
            midboth = p.pop("midboth", False)
            lit = p.pop("lit", None)               # the wall's own light, whatever the room's (a lit screen)
            lower = p.pop("lower", None)           # texture of the step, both sides
            upper = p.pop("upper", None)           # texture above the opening, both sides
            # floorpeg: on a line that is lower-unpegged for the sake of what
            # stands on it (a railing), the wall below still starts at the
            # raised floor, as it would on a line without that flag
            floorpeg = p.pop("floorpeg", False) and p.get("dontpegbottom") and not lower
            s = self.sectors[si]
            ld = dict(v1=vi(a), v2=vi(b))
            other = edges.get((b, a))
            if other is None:
                ld["sidefront"] = side(si, a, b, () if p.get("dontpegbottom") else ("mid",),
                                       fit=fit, whole=whole, texturemiddle=mid or s["wall"])
                ld["blocking"] = True
            else:
                done.add((b, a))
                o = self.sectors[other]
                front = dict(texturetop=upper or o["wall"], texturebottom=lower or o["side"])
                if mid:
                    front["texturemiddle"] = mid
                hung = [part for part, flag in (("top", "dontpegtop"), ("bottom", "dontpegbottom")) if p.get(flag)]
                def drop(view, far):
                    return float(far["floor"] - view["ceil"]) if floorpeg and far["floor"] > view["floor"] else 0
                ld["sidefront"] = side(si, a, b, hung, drop(s, o), fit=fit, whole=whole, **front)
                back = dict(texturetop=upper or s["wall"], texturebottom=lower or s["side"])
                if mid and midboth:
                    back["texturemiddle"] = mid
                ld["sideback"] = side(other, b, a, hung, drop(o, s), fit=fit, whole=whole, **back)
                if midraise:
                    for sd in (sides[ld["sidefront"]], sides[ld["sideback"]]):
                        sd["offsety_mid"] = float(midraise)
                ld["twosided"] = True
            if lit is not None:
                for k in ("sidefront", "sideback"):
                    if k in ld:
                        sides[ld[k]].update(light=lit, lightabsolute=True)
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
        for t, least in zip(self.things, self._skills()):
            d = dict(t)
            d.pop("skill", None)
            d["x"], d["y"] = float(d["x"]), float(d["y"])
            args = d.pop("args", ())
            for i, v in enumerate(args):
                if v:
                    d[f"arg{i}"] = v
            for n in range(least, 6):
                d[f"skill{n}"] = True
            for f in ("single", "coop", "dm"):
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
