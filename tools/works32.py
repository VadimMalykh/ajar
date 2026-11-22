"""MAP32's look (Vadim, 2026-11-21, "Deep Field"; PLAN.md, "Look: MAP32"):
the level of map_secret2.py dressed after it is built, with AJAR_WORKS unset
or 1. AJAR_WORKS=0 is the plain level, which this never touches.

Its lights, since 2026-11-22 (Vadim: "on walls only, something more still
like orange glow, not white on black"): one still orange wall lamp, the only
house light of the level, painted with its glow onto a wall plate
(gfx_works.py). Over every time door (centred on its mouth, with 32 of glow
cut beside it each side), and along the walls of each room's main spaces
(RECTS and the two corridors): on each straight run of plain wall
max(1, round(length / LAMP_EVERY)) lamps, spread evenly about the run's
middle on the walls' 128 grid, LAMP_APART apart at least; none on a run
shorter than LAMP_RUN, none whose middle is nearer than LAMP_NEAR to one of
the puzzle's lamps (2026-11-22, round two: more of them, the rooms of goes
lit 176 instead of 152). No light is
attached to a lamp: they are pictures only. The pens and the way out have a
dull orange light each (things that works.zs lights).

Nothing here moves a wall, a floor or a ceiling, or adds a sector: it gives
sectors and lines textures, flats, light and (in UDMF) a second tag, cuts a
few walls into pieces so that a piece can wear its own picture, and puts
things that are carriers of light or mark the rooms (src/zscript/works.zs,
which also answers the game: the press, a room done, the plate line).

  dress(g)  dresses the module g (map_secret2) and returns its SIGNS, the
            signs gfx_works.make draws. Prints how many lamps each room got.
"""
import math
import sys

from gfx_works import CODE, HEIGHTS, STRIP

ROOM_T = 20081          # AjarWorksRoom: a rectangle of a room (args: room, half width, half height); marks the look
SPOT_T = 20080          # AjarWorksSpot: a light (args: kind, room, radius, strength in hundredths)
ORANGE_LAMP = 2
TAG = 4100              # sectors of room k: moreids 4100 + 10k; those the press's light follows: + 1
QUIET = 192             # the pens' lights reach no frame, leaf, plate, lamp or lever
LAMP_EVERY = 384        # a wall lamp to so much of a straight run of wall
LAMP_RUN = 192          # a run shorter than this has none
LAMP_NEAR = 160         # no wall lamp's middle nearer than this to one of the puzzle's lamps
LAMP_APART = 256        # lamps on one run at least this far apart
WHY = []                # (a check's notes) the plates a wall lamp was not put on, and why
PUZZLE_T = {20001, 20002, 20044, 20047, 20048, 20053, 20054, 20056, 20057}
LAMP_T = {20048, 20053, 20054, 20057}


def dress(g):
    m = g.m
    S = m.sectors
    n_sec = len(S)
    caseglass = {c - 1 for c in g.CASES}

    def box(si):
        p = m.polys[si]
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        return min(xs), min(ys), max(xs), max(ys)

    def centre(si):
        x1, y1, x2, y2 = box(si)
        return (x1 + x2) / 2, (y1 + y2) / 2

    def room_of(x, y):
        if x < 1000:
            return 1
        if x < 3900:
            return 2
        if 6552 <= x <= 6872 and 96 <= y <= 224:
            return 0                                    # the corridor from room 3 to room 4
        if 7728 <= x <= 8048 and 388 <= y <= 516:
            return 0                                    # from room 4 to room 5
        if x < 6872:
            return 3
        if x < 8048:
            return 4
        return 5

    # --- which sectors are dressed, and as what -------------------------------------
    def skipped(si):
        s = S[si]
        w = s["wall"]
        if w.startswith("AJTR") or w.startswith("AJXA") or w.startswith("AJXW") or w in ("AJSHUT", "AJTRIM"):
            return True
        if w == "AJBOLT" and s["floor"] == s["ceil"] and s["id"] in (3390, 3490):
            return True                                 # the steel doors the wins open
        return False

    INFO = {}
    for si in range(n_sec):
        if skipped(si):
            continue
        s = S[si]
        x, y = centre(si)
        k = room_of(x, y)
        role = "room"
        if s["color"] == g.BOX:
            role = "box"
        elif si in g.CASES:
            role = "case"
        elif s["color"] == g.PEN:
            role = "pen"
        elif s["floor"] == s["ceil"]:
            role = "slab"
        elif k == 3 and (s["id"] == g.PRESS3 or y > g.PY):
            role = "chamber"
        elif k == 3 and s["id"] == g.WING3TAG and s["wall"] == "AJBOLT":
            role = "cage"
        INFO[si] = dict(room=k, role=role, pegfloor=role == "chamber")
    lobby3 = [si for si in INFO if box(si) == (4744, 64, 5000, 320)]
    lobby4 = [si for si in INFO if box(si) == (6872, 32, 7200, 320)]

    def height(si):
        s = S[si]
        if INFO[si]["room"] == 3 and s["id"] == g.WING3TAG and s["ceil"] == g.WC and 0 < s["floor"] < g.WF:
            return g.WC - g.HY                          # the stairs: the landing's wall
        return s["ceil"] - s["floor"]

    for si, info in INFO.items():
        s, k, role = S[si], info["room"], info["role"]
        h = height(si)
        if h not in CODE:
            assert role == "slab", (si, h, role)
        c = CODE.get(h, "D")
        if role == "chamber":
            s["wall"] = "AJZPD"
        elif role != "slab":
            s["wall"] = f"AJZW{c}"
        s["side"] = "AJZQ" if role == "slab" else "AJZSTP"
        x, y = centre(si)
        if role == "chamber":
            s["ftex"], s["ctex"] = "AJZBED", "AJZPLT"
            # the bed is one picture over the chamber and the mouth: its north-west corner at (HX, WY)
            s["raw"] = dict(s["raw"], xpanningfloor=float((-g.HX) % 2048), ypanningfloor=float(g.WY % 512))
        else:
            s["ftex"] = "AJZFT"
        sky = ((k == 2 and s["floor"] == g.PITF and role == "room")
               or (k == 3 and role in ("room", "slab") and s["ceil"] == g.HY + 320 and y < g.PY)
               or (k == 4 and role in ("room", "slab") and g.RX <= x <= g.RX + g.RW and 0 <= y <= g.RY + g.RL))
        if role != "chamber":
            s["ctex"] = "F_SKY1" if sky else "AJZKP"
        s["color"] = None
        if role == "box":
            s["light"] = 176
        elif role == "case":
            pass
        elif k in (1, 2, 5, 0) or si in lobby3 + lobby4:
            s["light"] = 176
        else:
            s["light"] = 184
        if role not in ("box", "case") and k:
            ids = [TAG + 10 * k]
            if k == 3 and (role == "chamber" or (g.HY <= y < g.PY and g.HX <= x <= g.HX + g.HW)):
                ids.append(TAG + 10 * k + 1)              # the hall and the chamber: the press's light
            s["raw"] = dict(s["raw"], moreids=" ".join(map(str, ids)))

    # --- the edges, for finding wall pieces --------------------------------------------
    EDGES = []                  # (si, a, b): a polygon's edges as drawn (clockwise: the sector on the right)
    for si, p in enumerate(m.polys):
        for a, b in zip(p, p[1:] + p[:1]):
            EDGES.append((si, a, b))

    def on(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx * (p[1] - a[1]) - dy * (p[0] - a[0]):
            return None
        return ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)

    def wall_of(p, q, si=None):
        """The edge (si, a, b) of a dressed sector that holds the segment p-q."""
        for s_i, a, b in EDGES:
            if (si is None and s_i not in INFO) or (si is not None and s_i != si):
                continue
            t1, t2 = on(p, a, b), on(q, a, b)
            if t1 is not None and t2 is not None and min(t1, t2) >= -1e-9 and max(t1, t2) <= 1 + 1e-9:
                return s_i, a, b
        return None

    CLAIMED = []                # pieces already given a picture: (a, b)

    def free(si, a, b, start, toward, most):
        """How far the one-sided wall of si (its edge a-b) runs from `start`
        toward the point `toward`, up to `most`: until the edge ends, another
        sector meets the line or a piece already claimed begins (0: something
        lies against `start` on that side already)."""
        d = (toward[0] - start[0], toward[1] - start[1])
        ln = math.hypot(*d)
        u = (d[0] / ln, d[1] / ln)

        def along(v):
            return (v[0] - start[0]) * u[0] + (v[1] - start[1]) * u[1]
        far = min(most, max(along(a), along(b)))
        for s_i, c, e in EDGES + [(None,) + cl for cl in CLAIMED]:
            if s_i == si or on(c, a, b) is None or on(e, a, b) is None:
                continue
            lo, hi = sorted((along(c), along(e)))
            if hi <= 1e-9 or lo >= far:
                continue
            if lo <= 1e-9:
                return 0
            far = lo
        return max(0, int(far))

    OFFS = {}                   # a piece's side offsets: {frozenset of its ends: {...}}

    def piece(si, a, b, start, toward, want, tex, **line):
        """Cut a piece up to `want` long out of the wall from `start` toward
        `toward` and give it `tex`; returns its ends (or None)."""
        n = free(si, a, b, start, toward, want)
        if n < 8:
            return None
        d = (toward[0] - start[0], toward[1] - start[1])
        ln = math.hypot(*d)
        end = (start[0] + round(d[0] / ln * n), start[1] + round(d[1] / ln * n))
        m.cut(start, end)
        m.line(start, end, mid=tex, **line)
        CLAIMED.append((start, end))
        return start, end, n

    # --- time doors: a lamp over each; frames: a pale surround -------------------------------
    def mouth_of(rs):
        """The mouth of the recess sector rs: (the room's sector, its edge a, b, the mouth's ends in the
        edge's direction)."""
        p = m.polys[rs]
        for q1, q2 in zip(p, p[1:] + p[:1]):
            w = wall_of(q1, q2)
            if w:
                si, a, b = w
                ta, tb = on(q1, a, b), on(q2, a, b)
                return si, a, b, (q1, q2) if ta < tb else (q2, q1)
        return None

    def towards(a, b, p, back):
        """A point on a-b beyond p, away from (back) or toward b."""
        if back:
            return a if a != p else (2 * p[0] - b[0], 2 * p[1] - b[1])
        return b if b != p else (2 * p[0] - a[0], 2 * p[1] - a[1])

    def cut_along(si, start, d, want, tex):
        """Pieces of `tex` on the one-sided wall from `start` in the direction d
        (a unit), `want` long in all, on across sectors as high as si; returns
        how much was cut (less where the wall turns or opens)."""
        done, pt = 0, start
        while done < want:
            w = wall_of(pt, (pt[0] + d[0], pt[1] + d[1]))
            if not w or S[w[0]]["floor"] != S[si]["floor"] or S[w[0]]["ceil"] != S[si]["ceil"] \
                    or INFO[w[0]]["role"] not in ("room", "chamber", "box"):
                break
            s_i, a, b = w
            far = (pt[0] + d[0] * (want - done), pt[1] + d[1] * (want - done))
            got = piece(s_i, a, b, pt, far, want - done, tex,
                        **({"dontpegbottom": True} if INFO[s_i]["pegfloor"] else {}))
            if not got:
                break
            pt, done = got[1], done + got[2]
        return done

    COUNT = {k: [0, 0] for k in range(6)}       # by room (0: the corridors): wall lamps, door lamps
    DOOR_AT = []                # the door lamps' middles (on the mouth's line): the hook centres them
    CUT_SHORT = []              # doors where the glow beside the mouth could not be cut whole
    steel = [set(m.polys[i]) for i in range(n_sec) if S[i]["id"] in (3390, 3490)]
    doors = frames = 0
    for rs in range(n_sec):
        s = S[rs]
        if rs in INFO or s["ceil"] - s["floor"] != 96 or s["light"] != 176 or rs in caseglass:
            continue
        if any(len(set(m.polys[rs]) & st) >= 2 for st in steel):
            continue                                    # the mouth of a steel door: no frame, no time door
        w = s["wall"]
        time = w == "AJTR10"
        frame = w == "AJTRIM" or (w.startswith("AJXA") and len(w) > 4) or (w.startswith("AJTR") and not time)
        if not (time or frame):
            continue
        mo = mouth_of(rs)
        if not mo:
            continue
        si, a, b, (p, q) = mo
        info = INFO[si]
        k = info["room"]
        h = height(si)
        c = CODE[h]
        if time:
            doors += 1
            if info["role"] == "chamber":
                assert h == 192, h
                m.line(p, q, upper="AJZXD")             # hung from the door: the press's ceiling moves
            else:
                m.line(p, q, upper=f"AJZU{c}", dontpegtop=True)
            DOOR_AT.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
            COUNT[k][1] += 1
            ln = math.hypot(q[0] - p[0], q[1] - p[1])
            u = ((q[0] - p[0]) / ln, (q[1] - p[1]) / ln)
            for start, d in ((p, (-u[0], -u[1])), (q, u)):     # the glow beside the mouth
                n = cut_along(si, start, d, STRIP, f"AJZU{c}")
                if n < STRIP:
                    CUT_SHORT.append((k, start, n))
        else:
            frames += 1
            m.line(p, q, upper=f"AJZN{c}", lower=f"AJZN{c}", dontpegtop=True, dontpegbottom=True)
            for start, back in ((p, True), (q, False)):
                piece(si, a, b, start, towards(a, b, start, back), 64, f"AJZN{c}")
    assert doors >= 20 and frames >= 12, (doors, frames)
    for k, st, n in CUT_SHORT:
        print(f"works32: room {k}: the door lamp's glow by {st} only {n} wide (the wall turns or opens)", file=sys.stderr)

    # --- room 3: the test bay -------------------------------------------------------------
    m.line((g.MOUTH3[0], g.PY), (g.MOUTH3[1], g.PY), upper="AJZTH", exact=True, dontpegtop=True)
    for x in g.MOUTH3:                                  # the stubs' ends: hazard stripes
        m.line((x, g.PY), (x, g.PY + 32), mid="AJZHAZ", dontpegbottom=True)

    # --- signs ----------------------------------------------------------------------------
    SIGNS = [dict(kind="upper", name="AJZI1", w=192, h=32, lines=["TEST BAY 1"], scale=2)]
    m.line((224, 0), (416, 0), upper="AJZI1", exact=True)
    for name, k, p, q, lines, y in (("AJZ5D", 2, (2560, 320), (2688, 320), ["TEST", "BAY 2"], 64),
                                    ("AJZ6H", 3, (5000, 0), (5128, 0), ["CABIN", "OPENS", "UNDER", "LOAD"], 150),
                                    ("AJZ7B", 3, (5480, -16), (5608, -16), ["CONTROL"], 30),
                                    ("AJZ8D", 4, (7056, 320), (7184, 320), ["TEST", "BAY 4"], 64),
                                    ("AJZ9D", 5, (8096, 672), (8224, 672), ["TEST", "BAY 5"], 64)):
        w = wall_of(p, q)
        assert w, ("no wall for the sign", name)
        si, a, b = w
        assert CODE[height(si)] == name[4], (name, height(si))
        st = p if on(p, a, b) < on(q, a, b) else q
        got = piece(si, a, b, st, q if st == p else p, 128, None)
        assert got and got[2] == 128, ("no room for the sign", name, got)
        m.line(p, q, mid=name)
        SIGNS.append(dict(kind="wall", name=name, h=height(si), lines=lines, y=y))

    # --- the way out: a hatch round the night room's mouth, lit all round ------------------
    hp, hq = (g.NX + 128, g.NY - 16), (g.NX + 192, g.NY - 16)
    m.line(hp, hq, lower="AJZHA", upper="AJZHB")
    w = wall_of(hp, hq)
    si, a, b = w
    for start, back, tex in ((hp if on(hp, a, b) < on(hq, a, b) else hq, True, "AJZHC"),
                             (hq if on(hp, a, b) < on(hq, a, b) else hp, False, "AJZHD")):
        got = piece(si, a, b, start, towards(a, b, start, back), STRIP, tex)
        if got and tex == "AJZHC" and got[2] < STRIP:
            OFFS[frozenset(got[:2])] = {"offsetx_mid": float(STRIP - got[2])}

    # --- the rooms: their rectangles (things that mark the look, for works.zs) -----------------
    NAMED = {1: [("room", (0, -192, 640, 512)), ("box", (-400, 32, -208, 224)), ("nook", (384, 528, 576, 624))],
             2: [("gallery", (2000, 0, 3280, 320)), ("pit", g.PIT2), ("box", (2384, 480, 2576, 672)),
                 ("case", (2048, 336, 2304, 432))],
             3: [("hall", (g.HX, g.HY, g.HX + g.HW, g.PY)), ("chamber", (g.HX, g.PY, g.HX + g.HW, g.WY)),
                 ("lobby", (4744, 64, 5000, 320)), ("wing", (g.LANDING3[0], g.PEN3[1], g.CAGE3BOX[2], g.HY)),
                 ("box 1", (4776, 464, 4984, 656)), ("box 2", (6552, 464, 6760, 656)),
                 ("box 3", (6100, -216, 6356, -16)), ("case", (4776, 336, 4968, 432))],
             4: [("range", (g.RX, g.RY, g.RX + g.RW, g.RY + g.RL)), ("lobby", (6872, 32, 7200, 320)),
                 ("west wing", g.WINGS4[0]), ("east wing", g.WINGS4[1]), ("pen", g.PEN4),
                 ("box 1", (7200, -208, 7376, -16)), ("box 2", (7536, -208, 7712, -16)),
                 ("box 3", (6992, 500, 7184, 680)), ("case", (7728, 96, 7824, 288))],
             5: [("S", (8048, 160, 8560, 672)), ("L", (8800, 160, 9248, 672)), ("E", (9600, 160, 10112, 608)),
                 ("box", (8200, -240, 8392, -48)), ("case", (8576, 512, 8672, 640))],
             0: [("corridor 3-4", (6552, 96, 6872, 224)), ("corridor 4-5", (7728, 388, 8048, 516))]}
    RECTS = {k: [r for _, r in v] for k, v in NAMED.items() if k}
    CORRIDORS = [r for _, r in NAMED[0]]
    for k, rects in RECTS.items():
        for x1, y1, x2, y2 in rects:
            m.thing((x1 + x2) / 2, (y1 + y2) / 2, ROOM_T, args=(k, (x2 - x1) // 2, (y2 - y1) // 2))
    PER_RECT = {}               # wall lamps by (room, its rectangle's name)

    def rect_of(k, pt):
        for name, (x1, y1, x2, y2) in NAMED[k]:
            if x1 <= pt[0] <= x2 and y1 <= pt[1] <= y2:
                return name
        return "elsewhere"

    # --- the wall lamps ---------------------------------------------------------------------
    PUZZLE_LAMPS = [(t["x"], t["y"]) for t in m.things if t["type"] in LAMP_T]
    MAIN = [r for rects in RECTS.values() for r in rects] + CORRIDORS

    def in_main(pt):
        return any(x1 <= pt[0] <= x2 and y1 <= pt[1] <= y2 for x1, y1, x2, y2 in MAIN)

    def subtract(lo, hi, cover):
        parts = [(lo, hi)]
        for c0, c1 in cover:
            nxt = []
            for p0, p1 in parts:
                if c1 <= p0 or c0 >= p1:
                    nxt.append((p0, p1))
                    continue
                if c0 > p0:
                    nxt.append((p0, c0))
                if c1 < p1:
                    nxt.append((c1, p1))
            parts = nxt
        return parts

    # the plain one-sided wall of the rooms' main spaces, by line: {(axis, where, direction): [(w0, w1, si, a, b)]}
    LINES = {}
    for si, info in INFO.items():
        if info["role"] not in ("room", "chamber"):
            continue
        s = S[si]
        h = height(si)
        if h != s["ceil"] - s["floor"] or h <= 96:
            continue
        p = m.polys[si]
        for a, b in zip(p, p[1:] + p[:1]):
            if a[0] != b[0] and a[1] != b[1]:
                continue
            ax = 0 if a[1] == b[1] else 1              # the axis the wall runs along
            cover = [sorted((c[ax], e[ax])) for s_j, c, e in EDGES
                     if s_j != si and on(c, a, b) is not None and on(e, a, b) is not None]
            cover += [sorted((c[ax], e[ax])) for c, e in CLAIMED if on(c, a, b) is not None and on(e, a, b) is not None]
            lo, hi = sorted((a[ax], b[ax]))
            for w0, w1 in subtract(lo, hi, cover):
                mid = ((w0 + w1) / 2, a[1]) if ax == 0 else (a[0], (w0 + w1) / 2)
                if in_main(mid):
                    LINES.setdefault((ax, a[1 - ax], 1 if b[ax] > a[ax] else -1), []).append((w0, w1, si, a, b))

    def at(ax, where, w):
        return (w, where) if ax == 0 else (where, w)

    for (ax, where, d), parts in sorted(LINES.items()):
        parts.sort()
        runs = [[parts[0]]]
        for pt in parts[1:]:
            if pt[0] == runs[-1][-1][1]:
                runs[-1].append(pt)
            else:
                runs.append([pt])
        for run in runs:
            w0, w1 = run[0][0], run[-1][1]
            ln = w1 - w0
            if ln < LAMP_RUN:
                WHY.append((run[0][2], at(ax, where, w0), at(ax, where, w1), None, f"run {ln} long"))
                continue
            n = max(1, int(ln / LAMP_EVERY + 0.5))
            mid = (w0 + w1) / 2
            chosen = []
            for i in range(n):
                want = mid + (i - (n - 1) / 2) * ln / n          # the lamp's middle, as the rule spreads them
                g0 = round((want - 64) / 128) * 128
                tries = sorted((g0 + o for o in (0, 128, -128, 256, -256)),
                               key=lambda x: (abs(x + 64 - want), abs(x + 64 - mid)))
                for x in tries:
                    centre_pt = at(ax, where, x + 64)
                    # the parts the plate lies on: one after another, sectors as high (a seam between them is unseen)
                    on_it = [pt for pt in run if pt[1] > x and pt[0] < x + 128]
                    whole = (on_it and on_it[0][0] <= x and on_it[-1][1] >= x + 128
                             and all(p1[1] == p2[0] for p1, p2 in zip(on_it, on_it[1:]))
                             and len({(S[pt[2]]["floor"], S[pt[2]]["ceil"], INFO[pt[2]]["role"]) for pt in on_it}) == 1)
                    if not whole:
                        WHY.append((run[0][2], at(ax, where, x), at(ax, where, x + 128), centre_pt,
                                    f"not whole on the run {at(ax, where, w0)}..{at(ax, where, w1)}"))
                        continue
                    if any(abs(x - o) < LAMP_APART for o in chosen):
                        WHY.append((run[0][2], at(ax, where, x), at(ax, where, x + 128), centre_pt, "by another lamp"))
                        continue
                    near = [(round(math.hypot(centre_pt[0] - lx, centre_pt[1] - ly)), (lx, ly)) for lx, ly in PUZZLE_LAMPS]
                    near = [nl for nl in near if nl[0] < LAMP_NEAR]
                    if near:
                        WHY.append((run[0][2], at(ax, where, x), at(ax, where, x + 128), centre_pt,
                                    f"puzzle lamp {min(near)[1]} {min(near)[0]} away"))
                        continue
                    si = on_it[0][2]
                    tex = "AJZPDL" if INFO[si]["role"] == "chamber" else f"AJZWL{CODE[height(si)]}"
                    for p0, p1, s_i, a, b in on_it:
                        lo, hi = max(p0, x), min(p1, x + 128)
                        start, end = at(ax, where, lo), at(ax, where, hi)
                        got = piece(s_i, a, b, start, end, hi - lo, tex)
                        assert got and got[2] == hi - lo, ("a wall lamp's plate not whole", start, end, got)
                    chosen.append(x)
                    k = INFO[si]["room"]
                    COUNT[k][0] += 1
                    PER_RECT[(k, rect_of(k, centre_pt))] = PER_RECT.get((k, rect_of(k, centre_pt)), 0) + 1
                    break
    for k in (1, 2, 3, 4, 5, 0):
        where = ", ".join(f"{name} {PER_RECT[(k, name)]}" for name, _ in NAMED[k] + [("elsewhere", None)]
                          if (k, name) in PER_RECT)
        print(f"works32: {f'room {k}' if k else 'the corridors'}: {COUNT[k][0]} wall lamps, {COUNT[k][1]} door lamps"
              f"{' (' + where + ')' if where else ''}", file=sys.stderr)

    # --- the puzzle's things: the pens' lights keep off them -------------------------------------
    PUZZLE = [(t["x"], t["y"]) for t in m.things if t["type"] in PUZZLE_T]
    for rs in range(n_sec):
        s = S[rs]
        if rs not in INFO and s["light"] == 176 and s["ceil"] - s["floor"] == 96 and s["wall"].startswith("AJTR") \
                and s["wall"] != "AJTR10":
            PUZZLE.append(centre(rs))                   # a far side: a leaf comes out there

    def quiet(p):
        return min(math.hypot(p[0] - x, p[1] - y) for x, y in PUZZLE)

    # the pens: a dull orange, steady (they are fight: rule 5 counts them)
    for k, pen in ((3, g.PEN3), (4, g.PEN4)):
        c = ((pen[0] + pen[2]) / 2, (pen[1] + pen[3]) / 2)
        r = min(300, int(quiet(c)) - 16)
        assert r >= QUIET, ("the pen's light by the puzzle", k, quiet(c))
        m.thing(c[0], c[1], SPOT_T, args=(ORANGE_LAMP, k, r, 45, 0), height=96.0)
    # the hatch: a light before the way out, orange as the pens'
    m.thing(g.NX + 160, g.NY - 48, SPOT_T, args=(ORANGE_LAMP, 5, 200, 60, 0), height=150.0)
    assert quiet((g.NX + 160, g.NY - 48)) >= 200 + 16

    # --- each side's last touches: world alignment, pegging, the door lamps centred ----------------
    ALIGNED = {f"AJZW{c}" for c in HEIGHTS} | {f"AJZWL{c}" for c in HEIGHTS} | {"AJZPD", "AJZPDL"}
    DOOR_TEX = {f"AJZU{c}" for c in HEIGHTS} | {"AJZXD"}

    def replace_upper(o_i):
        o = S[o_i]
        return o_i in INFO or o["wall"] == "AJTRIM" or o_i in caseglass

    def replace_lower(o_i):
        o = S[o_i]
        return o_i not in INFO and (o["wall"] in ("AJTRIM",) or o_i in caseglass)

    def align(sd, part, p, q):
        if p[1] == q[1]:
            u = p[0] if q[0] > p[0] else -p[0]
        elif p[0] == q[0]:
            u = p[1] if q[1] > p[1] else -p[1]
        else:
            return
        if u % 128:
            sd["offsetx_" + part] = float(u % 128)

    def door_off(sd, part, p, q):
        """A door lamp's picture on the side p-q: its column 64 at the door's middle."""
        ln = math.hypot(q[0] - p[0], q[1] - p[1])
        u = ((q[0] - p[0]) / ln, (q[1] - p[1]) / ln)
        best = None
        for c in DOOR_AT:
            if abs(u[0] * (c[1] - p[1]) - u[1] * (c[0] - p[0])) > 1e-6:
                continue
            s = (p[0] - c[0]) * u[0] + (p[1] - c[1]) * u[1]     # p from the door's middle, along the side
            if -64 - 1e-6 <= s and s + ln <= 64 + 1e-6 and (best is None or abs(s) < abs(best)):
                best = s
        assert best is not None, ("a door lamp's piece by no door", p, q)
        if (64 + best) % 128:
            sd["offsetx_" + part] = float((64 + best) % 128)

    def hook(ld, sides, a, b, si, other, given):
        front = sides[ld["sidefront"]]
        if other is None:
            if si not in INFO:
                return
            tex = front.get("texturemiddle", "")
            if tex in ALIGNED:
                align(front, "mid", a, b)
            elif tex in DOOR_TEX:
                door_off(front, "mid", a, b)
            if INFO[si]["pegfloor"]:
                ld["dontpegbottom"] = True
            key = frozenset((a, b))
            if key in OFFS:
                front.update(OFFS[key])
            return
        back = sides[ld["sideback"]]
        for sd, s_i, o_i, p, q in ((front, si, other, a, b), (back, other, si, b, a)):
            if s_i not in INFO or INFO[s_i]["role"] == "slab":
                continue
            s, o = S[s_i], S[o_i]
            if given["upper"] is None and s["ceil"] > o["ceil"] and replace_upper(o_i):
                sd["texturetop"] = s["wall"]
                align(sd, "top", p, q)
                ld["dontpegtop"] = True
            if given["lower"] is None and s["floor"] < o["floor"] and replace_lower(o_i):
                sd["texturebottom"] = s["wall"]
                align(sd, "bottom", p, q)
                ld["dontpegbottom"] = True
            if sd.get("texturetop") in DOOR_TEX and s["ceil"] > o["ceil"]:
                door_off(sd, "top", p, q)

    m.line_hook = hook
    return SIGNS
