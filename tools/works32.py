"""MAP32's look, "Deep Field" (Vadim, 2026-11-21; PLAN.md, "Look: MAP32"):
the level of map_secret2.py dressed after it is built, with AJAR_WORKS unset
or 1. AJAR_WORKS=0 is the plain level, which this never touches.

Nothing here moves a wall, a floor or a ceiling, or adds a sector: it gives
sectors and lines textures, flats, light and (in UDMF) a second tag, cuts a
few walls into pieces so that a piece can wear its own picture, and puts
things that are nothing but carriers of light (src/zscript/works.zs). The
pictures are drawn by gfx_works.py; the lights and the textures that change
with the game are worked by works.zs.

  dress(g)  dresses the module g (map_secret2) and returns its SIGNS, the
            signs gfx_works.make draws.
"""
import math

from gfx_works import CODE, STRIP, high_row

ROOM_T = 20081          # AjarWorksRoom: a rectangle of a room (args: room, half width, half height, axis, sweep)
SPOT_T = 20080          # AjarWorksSpot: a light (args: kind, room, radius, dx or line id, dy)
STEADY, ORANGE_LAMP, TRAVEL, STUTTER = 1, 2, 3, 4
TAG = 4100              # sectors of room k: moreids 4100 + 10k; those the press's light follows: + 1
STUTTER_ID = 4300       # the line of room k's stutter: 4300 + k
QUIET = 192             # no coloured or moving light nearer than this to a frame, leaf, plate, lamp or lever
LAMP_QUIET = 256        # nothing that stutters nearer than this to a lamp
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
        steady = role in ("box", "case")
        if role in ("pen", "cage"):
            s["wall"] = f"AJZR{c}"
        elif role == "chamber":
            s["wall"] = "AJZPDM00"
        elif role != "slab":
            s["wall"] = f"AJZW{c}{'S' if steady else 'M'}00"
        s["side"] = "AJZQ" if role == "slab" else "AJZSTP"
        x, y = centre(si)
        if role == "chamber":
            s["ftex"], s["ctex"] = "AJZBED", "AJZPLT"
            # the bed is one picture over the chamber and the mouth: its north-west corner at (HX, WY)
            s["raw"] = dict(s["raw"], xpanningfloor=float((-g.HX) % 2048), ypanningfloor=float(g.WY % 512))
        elif role in ("room",) and k in (1, 2, 5, 0):
            s["ftex"] = "AJZCFM00"
        else:
            s["ftex"] = "AJZFT"
        if k == 0 and 388 <= y <= 516:
            s["raw"] = dict(s["raw"], ypanningfloor=float((128 + 452) % 256))     # a conduit down its middle
        sky = ((k == 2 and s["floor"] == g.PITF and role == "room")
               or (k == 3 and role in ("room", "slab") and s["ceil"] == g.HY + 320 and y < g.PY)
               or (k == 4 and role in ("room", "slab") and g.RX <= x <= g.RX + g.RW and 0 <= y <= g.RY + g.RL))
        if role != "chamber":
            s["ctex"] = "F_SKY1" if sky else "AJZKCS00"
        s["color"] = None
        if role == "box":
            s["light"] = 170
        elif role == "case":
            pass
        elif k in (1, 2, 5, 0) or si in lobby3 + lobby4:
            s["light"] = 152
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

    # --- time doors: the conduit climbs round them --------------------------------------
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

    TARGET = {1: (192, 512), 2: (2632, 0), 3: (6536, 160), 4: (7456, 1400), 5: (9856, 608), 0: (1e6, 0)}

    def var(name, k, a, b):
        """A moving family's name with its dashes running toward room k's way on."""
        if len(name) != 8 or name[5] != "M":
            return name
        t = TARGET[k]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if (t[0] - mid[0]) * (b[0] - a[0]) + (t[1] - mid[1]) * (b[1] - a[1]) < 0:
            return name[:5] + "L" + name[6:]
        return name

    steel = [set(m.polys[i]) for i in range(n_sec) if S[i]["id"] in (3390, 3490)]
    doors = frames = 0
    for rs in range(n_sec):
        s = S[rs]
        if s["ceil"] - s["floor"] != 96 or s["light"] != 176 or rs in caseglass:
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
        info, room = INFO[si], S[si]
        k = info["room"]
        h = height(si)
        c = CODE[h]
        if time:
            doors += 1
            steady = info["role"] == "box"
            v = "S" if steady else "M"
            if info["role"] == "chamber":
                m.line(p, q, upper=f"AJZXD{v}00")       # hung from the door: the press's ceiling moves
            else:
                m.line(p, q, upper=f"AJZU{c}{v}00", dontpegtop=True)
            for start, back, part in ((p, True, "Y"), (q, False, "V")):
                got = piece(si, a, b, start, towards(a, b, start, back), STRIP, None,
                            **({"dontpegbottom": True} if info["pegfloor"] else {}))
                if got:
                    st, en, n = got
                    m.line(st, en, mid=f"AJZ{part}{c}{v}00")
                    if part == "Y" and n < STRIP:
                        OFFS[frozenset((st, en))] = {"offsetx_mid": float(STRIP - n)}
        else:
            frames += 1
            m.line(p, q, upper=f"AJZO{c}", lower=f"AJZN{c}", dontpegtop=True, dontpegbottom=True)
            for start, back in ((p, True), (q, False)):
                piece(si, a, b, start, towards(a, b, start, back), 64, f"AJZN{c}")
    assert doors >= 20 and frames >= 12, (doors, frames)

    # --- room 3: the test bay -------------------------------------------------------------
    m.line((g.MOUTH3[0], g.PY), (g.MOUTH3[1], g.PY), upper="AJZTHM00", exact=True, dontpegtop=True)
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
        m.line(p, q, mid=var(f"{name}M00", k, a, b))
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

    # --- the puzzle's things: no coloured or moving light near them ---------------------------
    PUZZLE = [(t["x"], t["y"]) for t in m.things if t["type"] in PUZZLE_T]
    LAMPS = [(t["x"], t["y"]) for t in m.things if t["type"] in LAMP_T]
    for rs in range(n_sec):
        s = S[rs]
        if s["light"] == 176 and s["ceil"] - s["floor"] == 96 and s["wall"].startswith("AJTR") and s["wall"] != "AJTR10":
            PUZZLE.append(centre(rs))                   # a far side: a leaf comes out there

    def quiet(p):
        return min(math.hypot(p[0] - x, p[1] - y) for x, y in PUZZLE)

    # --- stutters: one stretch of the high line in each room -----------------------------------
    STUTTERS = {1: ((640, 64), (640, 192)), 2: ((2880, 0), (3008, 0)), 3: ((6400, 0), (6528, 0)),
                4: ((7200, 1000), (7200, 1128)), 5: ((9120, 672), (9248, 672))}
    for k, (p, q) in STUTTERS.items():
        w = wall_of(p, q)
        assert w, ("no wall for the stutter", k)
        si, a, b = w
        st = p if on(p, a, b) < on(q, a, b) else q
        got = piece(si, a, b, st, q if st == p else p, 128, None, id=STUTTER_ID + k)
        assert got and got[2] == 128, ("no room for the stutter", k)
        mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        nrm = (b[1] - a[1], -(b[0] - a[0]))          # into the sector (it is on the right of a-b)
        ln = math.hypot(*nrm)
        at = (mid[0] + nrm[0] / ln * 24, mid[1] + nrm[1] / ln * 24)
        assert quiet(at) >= 160 + 16 and quiet(at) >= QUIET and min(math.hypot(at[0] - x, at[1] - y) for x, y in LAMPS) >= LAMP_QUIET, (k, at)
        h = height(si)
        m.thing(at[0], at[1], SPOT_T, args=(STUTTER, k, 160, STUTTER_ID + k, 0), height=float(h - high_row(h) - 4))

    # --- the rooms, for works.zs: their rectangles; sweeps along the big ones --------------------
    RECTS = {1: [((0, -192, 640, 512), 0, 1), ((-400, 32, -208, 224), 0, 0), ((384, 528, 576, 624), 0, 0)],
             2: [((2000, 0, 3280, 320), 0, 1), (g.PIT2, 1, 1), ((2384, 480, 2576, 672), 0, 0),
                 ((2048, 336, 2304, 432), 0, 0)],
             3: [((g.HX, g.HY, g.HX + g.HW, g.PY), 0, 1), ((g.HX, g.PY, g.HX + g.HW, g.WY), 0, 1),
                 ((4744, 64, 5000, 320), 0, 0), ((g.LANDING3[0], g.PEN3[1], g.CAGE3BOX[2], g.HY), 0, 0),
                 ((4776, 464, 4984, 656), 0, 0), ((6552, 464, 6760, 656), 0, 0), ((6100, -216, 6356, -16), 0, 0),
                 ((4776, 336, 4968, 432), 0, 0)],
             4: [((g.RX, g.RY, g.RX + g.RW, g.RY + g.RL), 1, 1), ((6872, 32, 7200, 320), 0, 0),
                 (g.WINGS4[0], 1, 0), (g.WINGS4[1], 1, 0), (g.PEN4, 0, 0), ((7200, -208, 7376, -16), 0, 0),
                 ((7536, -208, 7712, -16), 0, 0), ((6992, 500, 7184, 680), 0, 0), ((7728, 96, 7824, 288), 0, 0)],
             5: [((8048, 160, 8560, 672), 1, 1), ((8800, 160, 9248, 672), 1, 1), ((9600, 160, 10112, 608), 1, 1),
                 ((8200, -240, 8392, -48), 0, 0), ((8576, 512, 8672, 640), 0, 0)]}
    for k, rects in RECTS.items():
        for (x1, y1, x2, y2), axis, sweep in rects:
            m.thing((x1 + x2) / 2, (y1 + y2) / 2, ROOM_T, args=(k, (x2 - x1) // 2, (y2 - y1) // 2, axis, sweep))

    # --- steady lights: high on the walls, ICE, away from the puzzle -----------------------------
    def floor_at(p):
        for si in INFO:
            x1, y1, x2, y2 = box(si)
            if x1 < p[0] < x2 and y1 < p[1] < y2 and INFO[si]["role"] not in ("slab",):
                return si
        return None

    def steady(k, rect, n, radius, inset=40):
        x1, y1, x2, y2 = rect
        cands = []
        for x in range(x1 + inset, x2 - inset + 1, 32):
            cands += [(x, y1 + inset), (x, y2 - inset)]
        for y in range(y1 + inset, y2 - inset + 1, 32):
            cands += [(x1 + inset, y), (x2 - inset, y)]
        cands = [c for c in cands if quiet(c) >= max(QUIET, radius) + 16 and floor_at(c) is not None]
        chosen = []
        while len(chosen) < n and cands:
            best = max(cands, key=lambda c: (min([math.hypot(c[0] - o[0], c[1] - o[1]) for o in chosen] or [1e9]),
                                             quiet(c)))
            if chosen and min(math.hypot(best[0] - o[0], best[1] - o[1]) for o in chosen) < 300:
                break
            chosen.append(best)
        for c in chosen:
            si = floor_at(c)
            h = height(si)
            m.thing(c[0], c[1], SPOT_T, args=(STEADY, k, radius, 0, 0), height=float(h - high_row(h) - 12))
        return len(chosen)

    LIGHTS = {}
    LIGHTS[1] = steady(1, (0, 0, 640, 512), 3, 224)
    LIGHTS[2] = steady(2, (2000, 0, 3280, 320), 3, 224) + steady(2, g.PIT2, 2, 256)
    LIGHTS[3] = steady(3, (g.HX, g.HY, g.HX + g.HW, g.PY), 4, 288) + steady(3, (4744, 64, 5000, 320), 1, 224)
    LIGHTS[4] = steady(4, (g.RX, g.RY, g.RX + g.RW, g.RY + g.RL), 4, 256) + steady(4, g.WINGS4[0], 1, 200) \
        + steady(4, g.WINGS4[1], 1, 200)
    LIGHTS[5] = steady(5, (8048, 160, 8560, 672), 1, 224) + steady(5, (8800, 160, 9248, 672), 1, 224) \
        + steady(5, (9600, 160, 10112, 608), 1, 224)
    steady(0, (6552, 96, 6872, 224), 1, 200, inset=64)
    steady(0, (7728, 388, 8048, 516), 1, 200, inset=64)
    # the pens: a dull orange, steady (they are fight: rule 5 counts them)
    for k, pen in ((3, g.PEN3), (4, g.PEN4)):
        c = ((pen[0] + pen[2]) / 2, (pen[1] + pen[3]) / 2)
        r = min(300, int(quiet(c)) - 16)
        assert r >= QUIET, ("the pen's light by the puzzle", k, quiet(c))
        m.thing(c[0], c[1], SPOT_T, args=(ORANGE_LAMP, k, r, 0, 0), height=96.0)
        LIGHTS[k] += 1
    # the hatch: the brightest light of the level, before the way out
    m.thing(g.NX + 160, g.NY - 48, SPOT_T, args=(STEADY, 5, 200, 0, 0), height=150.0)
    assert quiet((g.NX + 160, g.NY - 48)) >= 200 + 16
    LIGHTS[5] += 1
    # steady lights a room has (with its stutter's): 12 at most with what moves; in rooms 3 and 4 at most 8
    assert LIGHTS[3] <= 7 and LIGHTS[4] <= 7 and all(n <= 7 for n in LIGHTS.values()), LIGHTS

    # --- lights that travel along a floor conduit toward the room's time door --------------------
    for k, a, b in ((1, (600, 128), (40, 128)), (2, (3240, 128), (2520, 128)), (2, (3310, -128), (3760, -128)),
                    (0, (6560, 128), (6864, 128)), (0, (7736, 452), (8040, 452))):
        clear = sum(quiet((a[0] + (b[0] - a[0]) * i / 20, a[1] + (b[1] - a[1]) * i / 20)) >= QUIET for i in range(21))
        assert clear >= 7, ("a travelling light mostly by the puzzle", a, b, clear)
        m.thing(a[0], a[1], SPOT_T, args=(TRAVEL, k, 160, b[0] - a[0], b[1] - a[1]), height=20.0)

    # --- each side's last touches: direction, world alignment, pegging --------------------------------
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

    def hook(ld, sides, a, b, si, other, given):
        front = sides[ld["sidefront"]]
        if other is None:
            if si not in INFO:
                return
            k = INFO[si]["room"]
            key = frozenset((a, b))
            tex = front.get("texturemiddle", "")
            if tex.startswith("AJZ") and len(tex) == 8 and tex[5] in "MLS":
                front["texturemiddle"] = var(tex, k, a, b)
                if key not in OFFS and tex[3] not in "VY" and not tex[3].isdigit():      # (a sign is its own piece)
                    align(front, "mid", a, b)
            if INFO[si]["pegfloor"]:
                ld["dontpegbottom"] = True
            if key in OFFS:
                front.update(OFFS[key])
            return
        back = sides[ld["sideback"]]
        for sd, s_i, o_i, p, q in ((front, si, other, a, b), (back, other, si, b, a)):
            if s_i not in INFO or INFO[s_i]["role"] == "slab":
                continue
            s, o, k = S[s_i], S[o_i], INFO[s_i]["room"]
            if given["upper"] is None and s["ceil"] > o["ceil"] and replace_upper(o_i):
                sd["texturetop"] = var(s["wall"], k, p, q)
                align(sd, "top", p, q)
                ld["dontpegtop"] = True
            if given["lower"] is None and s["floor"] < o["floor"] and replace_lower(o_i):
                sd["texturebottom"] = var(s["wall"], k, p, q)
                align(sd, "bottom", p, q)
                ld["dontpegbottom"] = True
            for part, key in (("top", "texturetop"), ("bottom", "texturebottom")):
                if given["upper" if part == "top" else "lower"] is not None:
                    tex = sd.get(key, "")
                    if tex.startswith("AJZ") and len(tex) == 8 and tex[5] == "M" and tex[3] in "UX5678":
                        sd[key] = var(tex, k, p, q)

    m.line_hook = hook
    return SIGNS
