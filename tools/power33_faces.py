"""MAP33's looks: the faces (tools/power33.py). What hangs on the walls (the pictures, the plates over and
beside the ways, the windows and pilasters drawn into the walls, DANGER plates), the objects' own faces (the
boilers' fronts, the turbine casings', the transformers' ends, the switchgear cabinets'), the round things'
faces (the chimney, the gatehouse's pillars, the tower's pillars) and Doom's edges in the bays. The same in
every look: the look draws each in its manner (gfx_power.PICTURES).

A face is a stretch P0-P1 of a wall seen from one side (P0 at the viewer's left) and the part of its sides it
covers (mid: a wall; top: the wall over a way; bottom: an object's side over the floor before it). A picture
on a wall that runs past it is a piece cut out of it (m.cut: the line split, nothing else).
"""
import math

from power33 import oriented

NOTES = []          # where each picture hangs (the build prints them)


def hang(S, L, ROLE):
    m = S.m
    secs = m.sectors

    def sec_wall(x, y):
        s = S.sec_at(x, y)
        assert s is not None, ("no sector at", x, y)
        return secs[s]["wall"]

    def add(P0, P1, part, name, w, scale=None, offx=0, cut=False):
        if cut:
            _one_sided(S, P0, P1)
            m.cut(P0, P1)
        L.faces.append(dict(P0=P0, P1=P1, part=part, name=name, w=w, scale=scale, offx=offx))

    def shift_of(P0, P1, base):
        """The base wall's column at P0 (walls are laid by world position along the line: power33's hook)."""
        if base not in L.tex:
            return 0
        d = (P1[0] - P0[0], P1[1] - P0[1])
        ln = math.hypot(*d)
        return int(round((P0[0] * d[0] + P0[1] * d[1]) / ln)) % L.tex[base]["W"]

    def pic(a, b, out, kind, base, part="mid", cut=True, note=None, **params):
        P0, P1 = oriented(a, b, out)
        w = int(round(math.hypot(P1[0] - P0[0], P1[1] - P0[1])))
        name = L.pic(kind, w, base=base, **params)
        L.tex[name]["shift"] = shift_of(P0, P1, base)
        add(P0, P1, part, name, w, cut=cut)
        if note:
            NOTES.append(f"{note}: {name} on {P0}-{P1}")
        return name

    def plate(a, b, out, words, head, part_no, x=None, y=None):
        """Over a way a-b (its head `head`), seen looking `out` from the room at (x, y)."""
        mx, my = (a[0] + b[0]) / 2 - out[0] * 8, (a[1] + b[1]) / 2 - out[1] * 8
        return pic(a, b, out, "plate", sec_wall(mx, my), part="top", cut=False, note=f"plate {' '.join(words)}",
                   words=words, head=head, part_no=part_no)

    def beside(a, b, out, words, at, arrow, part_no):
        """On the wall piece a-b beside a way with no wall over it (a shutter), seen looking `out`: the plate's
        foot at `at`, an arrow to the way (-1 left, 1 right as seen)."""
        mx, my = (a[0] + b[0]) / 2 - out[0] * 8, (a[1] + b[1]) / 2 - out[1] * 8
        return pic(a, b, out, "plateside", sec_wall(mx, my), note=f"plate {' '.join(words)} (beside)", words=words,
                   at=at, arrow=arrow, part_no=part_no)

    def wallpic(a, b, out, kind, note, **params):
        mx, my = (a[0] + b[0]) / 2 - out[0] * 8, (a[1] + b[1]) / 2 - out[1] * 8
        return pic(a, b, out, kind, sec_wall(mx, my), note=note, **params)

    def wallface(a, b, out, name, fit=False):
        """A wall texture of its own on the face a-b (the pillars, the chimney)."""
        P0, P1 = oriented(a, b, out)
        ln = math.hypot(P1[0] - P0[0], P1[1] - P0[1])
        W = L.tex[name]["W"]
        k = max(1, round(ln / W))
        add(P0, P1, "mid", name, W, scale=W * k / ln if fit else None)

    def doom_edges(a, b, out, edge):
        """A Doom bay's back wall a-b: SUPPORT3 `edge` wide at its two ends (the room's MARBGRAY between)."""
        P0, P1 = oriented(a, b, out)
        ln = math.hypot(P1[0] - P0[0], P1[1] - P0[1])
        u = ((P1[0] - P0[0]) / ln, (P1[1] - P0[1]) / ln)
        Q0 = (P0[0] + round(u[0] * edge), P0[1] + round(u[1] * edge))
        Q1 = (P1[0] - round(u[0] * edge), P1[1] - round(u[1] * edge))
        add(P0, Q0, "mid", "SUPPORT3", 64, offx=8 if edge < 32 else 0, cut=True)       # (a whole support of its two,
        add(Q1, P1, "mid", "SUPPORT3", 64, offx=40 if edge < 32 else 32, cut=True)     # or the middle of one)

    # === part 1 ==============================================================================================
    # S: the station plan on the north wall (what the player faces at the start), the rules on the east wall
    wallpic((160, 3200), (416, 3200), (0, 1), "plan", "picture 1, the station plan (S, north wall)", plan=station_plan(S))
    wallpic((768, 2880), (768, 3072), (1, 0), "rules", "picture 2, the safety rules (S, east wall)")
    gp = L.wall("GP", F=0, part=1)
    for x1, y1, x2, y2 in ((224, 2752, 288, 2816), (480, 2752, 544, 2816)):      # the two pillars, faience
        for a, b, out in (((x1, y1), (x2, y1), (0, 1)), ((x2, y1), (x2, y2), (-1, 0)), ((x2, y2), (x1, y2), (0, -1)),
                          ((x1, y2), (x1, y1), (1, 0))):
            wallface(a, b, out, gp)
    plate((448, 3200), (576, 3200), (0, 1), ("COAL YARD",), 96, 1)
    # the coal yard: tall windows high in the walls it shares with buildings (the gallery's, the boiler house's)
    for k, x in enumerate((640, 768, 1376)):
        wallpic((x, 3712), (x + 64, 3712), (0, -1), "window", f"coal yard window", lit=k % 2)
    for k, y in enumerate((3840, 4032, 4224)):
        wallpic((1920, y), (1920, y + 64), (1, 0), "window", f"coal yard window", lit=(k + 1) % 2)
    beside((1920, 4288), (1920, 4352), (1, 0), ("BOILER", "HOUSE"), 96, -1, 1)
    # the boiler house: the boilers' fronts (BLUE's frame in the first one's, its columns kept clear), windows
    for k, b in enumerate(S.BOILERS):
        gap = (S.FRAME_B[0] - b[0], S.FRAME_B[1] - b[0]) if k == 0 else None
        name = L.pic("boiler", b[2] - b[0], n=k + 1, gap=gap)
        add((b[0], b[1]), (b[2], b[1]), "bottom", name, b[2] - b[0])
        NOTES.append(f"boiler {k + 1}'s front: {name}")
    for x in (2432, 2496, 2816, 2880, 3200, 3264):
        wallpic((x, 4992), (x + 64, 4992), (0, 1), "bhwindow", "boiler house window")
    for x in (2752, 2816, 3136, 3200):
        wallpic((x, 3712), (x + 64, 3712), (0, -1), "bhwindow", "boiler house window")
    beside((3584, 3968), (3584, 4032), (1, 0), ("ASH", "TUNNEL"), 96, 1, 1)
    beside((3520, 4992), (3584, 4992), (0, 1), ("PUMPS",), S.CAT + 96, 1, 1)
    # the pump room: over the stairs down to the stack court
    plate((4608, 4608), (4608, 4736), (1, 0), ("STACK",), S.CAT + 128, 1)
    # the stack court: the chimney's sixteen faces and its plate, the plate over the way to the yard's terrace
    ch = L.wall("CH")
    C = S.CHIMNEY
    mids = [((C[i][0] + C[(i + 1) % len(C)][0]) / 2, (C[i][1] + C[(i + 1) % len(C)][1]) / 2) for i in range(len(C))]
    plate_face = min(range(len(C)), key=lambda i: abs(math.degrees(math.atan2(mids[i][1] - 4224, mids[i][0] - 5504)) - 135))
    for i in range(len(C)):                     # (the plate on the face towards the way in, from the north-west)
        a, b = C[i], C[(i + 1) % len(C)]
        out = (5504 - mids[i][0], 4224 - mids[i][1])
        if i == plate_face:
            P0, P1 = oriented(a, b, out)
            ln = math.hypot(P1[0] - P0[0], P1[1] - P0[1])
            name = L.pic("cplate", 64, base=ch)
            add(P0, P1, "mid", name, 64, scale=64 / ln)
            NOTES.append(f"the chimney's plate 1933: {name} on {P0}-{P1}")
        else:
            wallface(a, b, out, ch, fit=True)
    plate((4912, 3584), (5040, 3584), (0, -1), ("YARD",), 96, 1)
    # the terrace: beside the gantry's west mouth (part 1's way on)
    beside((5040, 3392), (5040, 3456), (1, 0), ("GANTRY",), 96, 1, 1)

    # === part 2 ==============================================================================================
    plate((896, 3504), (1024, 3504), (0, 1), ("GALLERY",), 96, 2)
    plate((3712, 3520), (3840, 3520), (0, -1), ("WORKSHOP",), 96, 2)
    wallpic((3840, 2464), (3840, 2656), (1, 0), "shadow", "picture 3, the shadow board (the workshop, east wall)")
    pic((2688, 2240), (2688, 2496), (-1, 0), "store", L.wall("WS", F=0, part=2), part="top", cut=False,
        note="the armoury's plate INSTRUMENT STORE (over its bars)")
    beside((4736, 2432), (4736, 2496), (1, 0), ("TURBINE", "HALL"), 96, 1, 2)
    # R: the casings' long sides, the pilasters, the plate by the steel door, Doom's bays
    for k, c in enumerate(S.CASINGS):
        for a, b, out, face in (((c[0], c[1]), (c[2], c[1]), (0, 1), "south"), ((c[0], c[3]), (c[2], c[3]), (0, -1), "north")):
            P0, P1 = oriented(a, b, out)
            name = L.pic("casing", c[2] - c[0], n=k + 1, face=face)
            add(P0, P1, "bottom", name, c[2] - c[0])
    th = L.wall("TH", F=S.RF, part=2)
    for x in (5344, 5472, 5984, 6112, 6592, 6720):                     # (32 wide, beside the south bays)
        pic((x, 2048), (x + 32, 2048), (0, -1), "pilaster", th, note="R pilaster")
    for y in (2128, 2448, 2720, 3184):
        pic((7040, y), (7040, y + 64), (1, 0), "pilaster", th, note="R pilaster")
    for y in (2144, 3168):
        pic((5056, y), (5056, y + 64), (-1, 0), "pilaster", th, note="R pilaster")
    beside((7040, 2944), (7040, 3008), (1, 0), ("SWITCHGEAR",), S.RF + 96, 1, 2)
    import power33
    for x1, y1, x2, y2 in power33.R_BAYS:
        if y1 == 2048:
            doom_edges((x1, 2048), (x2, 2048), (0, -1), 16)
        else:
            doom_edges((7040, y1), (7040, y2), (1, 0), 16)

    # === part 3 ==============================================================================================
    plate((128, 2304), (256, 2304), (0, -1), ("CABLE", "TUNNEL"), 96, 3)
    plate((1280, 1984), (1280, 2112), (-1, 0), ("CABLE", "TUNNEL"), 96, 3)
    plate((2816, 1984), (2816, 2112), (1, 0), ("RELAY", "ROOM"), 128, 3)
    plate((3424, 1792), (3552, 1792), (0, -1), ("COOLING", "POND"), 96, 3)
    beside((4864, 1792), (4864, 1856), (1, 0), ("CABLE", "DUCT"), S.TF + 96, -1, 3)
    wallpic((3584, 1856), (3584, 2112), (1, 0), "single", "picture 4, the single-line diagram (the relay room, east wall)")
    # the switchyard: the transformers' ends, numbered T1 to T8 in the generator's order; DANGER plates
    for k, t in enumerate(S.TRANS):
        for a, b, out, danger in (((t[0], t[1]), (t[2], t[1]), (0, 1), k % 2 == 0), ((t[0], t[3]), (t[2], t[3]), (0, -1), k % 2 == 1)):
            P0, P1 = oriented(a, b, out)
            name = L.pic("tend", t[2] - t[0], n=k + 1, danger=int(danger))
            add(P0, P1, "bottom", name, t[2] - t[0])
    wallpic((2816, 1216), (2816, 1280), (1, 0), "danger", "DANGER plate (switchyard, east wall)", at=120)
    wallpic((2688, 2112), (2752, 2112), (0, 1), "danger", "DANGER plate (switchyard, north wall)", at=120)
    wallpic((1280, 1856), (1280, 1920), (-1, 0), "danger", "DANGER plate (switchyard, west wall)", at=120)
    # the tower: its pillars
    tp = L.wall("TP")
    for P in S.PILLARS:
        cx, cy = sum(p[0] for p in P) / len(P), sum(p[1] for p in P) / len(P)
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            wallface(a, b, (cx - (a[0] + b[0]) / 2, cy - (a[1] + b[1]) / 2), tp, fit=True)

    # === the last hall ======================================================================================
    wallpic((7904, 3392), (8096, 3392), (0, 1), "synchro", "picture 5, the synchroscope (L, north wall)")
    for k, c in enumerate(S.SWITCHGEAR):
        for j, (a, b, out) in enumerate((((c[0], c[1]), (c[2], c[1]), (0, 1)), ((c[0], c[3]), (c[2], c[3]), (0, -1)))):
            P0, P1 = oriented(a, b, out)
            name = L.pic("cabinet", c[2] - c[0], n=2 * k + j + 1)
            add(P0, P1, "bottom", name, c[2] - c[0])
    for x1, y1, x2, y2 in S.BAYS:
        if x1 == 8960:
            doom_edges((9024, y1), (9024, y2), (1, 0), 32)
        elif y1 == 3392:
            doom_edges((x1, 3456), (x2, 3456), (0, 1), 32)
        else:
            doom_edges((x1, 2304), (x2, 2304), (0, -1), 32)


def _one_sided(S, P0, P1):
    """A piece cut out of a wall: the wall must be one-sided there, with no line of the map's own on it."""
    m = S.m
    mx, my = (P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2
    ln = math.hypot(P1[0] - P0[0], P1[1] - P0[1])
    nx, ny = (P1[1] - P0[1]) / ln, -(P1[0] - P0[0]) / ln          # to the viewer's side
    assert S.sec_at(mx + nx * 4, my + ny * 4) is not None, ("no room before the piece", P0, P1)
    assert S.sec_at(mx - nx * 4, my - ny * 4) is None, ("a piece of a two-sided wall", P0, P1)
    for key in m.lineprops:
        if len(key) != 2:
            continue
        a, b = tuple(key)
        if _overlaps(a, b, P0, P1):
            raise AssertionError(("a piece on a line of the map's own", P0, P1, m.lineprops[key]))


def _overlaps(a, b, p, q):
    dx, dy = b[0] - a[0], b[1] - a[1]
    for v in (p, q):
        if dx * (v[1] - a[1]) - dy * (v[0] - a[0]) != 0:
            return False
    n2 = dx * dx + dy * dy
    ts = sorted(((v[0] - a[0]) * dx + (v[1] - a[1]) * dy) / n2 for v in (p, q))
    return ts[1] > 0 and ts[0] < 1


def station_plan(S):
    """The station plan's figures, from the generator: the rooms as boxes (x1, y1, x2, y2), round things
    (x, y, r), and the three ways as lines of points from the gatehouse to the switchgear hall."""
    boxes = [S.S_BOX, S.YARD_BOX, S.BOIL_BOX, S.PUMP1, S.STACK, S.GANTRY_BOX, S.R_BOX, S.GALLERY, S.WORK_BOX,
             S.ARMOURY, S.MEZZ, (S.YX1, 2112, S.YX2, 3584), S.TERRACE, S.SW, S.RELAY, S.POND, S.DUCT, S.L_BOX,
             S.BOX2_BOX, S.BOX3_BOX, S.CACHE, (3600, 3840, 4352, 3968)] + list(S.TUN) + list(S.STAND_BOX.values())
    rounds = [(5504, 4224, 192), (S.TC[0], S.TC[1], S.TRW)]
    ways = {1: [(384, 2700), (512, 3400), (900, 4200), (1900, 4416), (2800, 4000), (2800, 4900), (4100, 4672),
                (5300, 4300), (4880, 3300), (6000, 3330), (7360, 3520), (8400, 3500)],
            2: [(576, 2430), (960, 2430), (960, 3600), (3776, 3600), (3776, 3160), (3300, 2900), (3900, 2880),
                (4300, 2700), (4600, 2368), (4960, 2368), (6000, 2848), (7100, 2880), (7700, 2880)],
            3: [(192, 2400), (192, 2050), (1270, 2050), (2000, 1700), (3200, 1950), (3488, 1700), (3800, 1200),
                (5184, 1024), (4800, 1700), (4800, 2150), (5700, 1950), (7550, 1920), (7550, 2288), (8384, 2280)]}
    return dict(boxes=boxes, rounds=rounds, ways=ways, exit=(9168, 2880))
