"""MAP23's looks, the map's side (PLAN.md, "Look: MAP23, the animal house"). tools/map_sleepingdogs.py calls
apply() once the map is built and checked, when AJAR_DOGS is set: 1, 2, 3 one look for every group; "mix" the
table MIX below (Vadim's picks, group by group). Unset or 0: the plain level, and this file is not imported.

The art is tools/gfx_dogs.py (the slots, shared) and tools/gfx_dogs<n>.py (each look's painters). This file says
which slot each surface of the map wears, where the pictures hang and where the decor things stand: the same for
every look. A look goes by place: each sector belongs to a group and wears that group's look.

The rule: nothing moves. A look changes wall textures and offsets, flats (and their panning: pen 1's weigh plate),
hangs pictures on pieces cut out of walls (a line split, never a new sector), and adds decor things after every
other thing of the map. One bend: THEN's sky sectors get a tag and one line the sky transfer (MAP22's AJ22SKY by
day; the map's own sky is AJ7SKY, a clear night, in every build). tools/dogs_compare.py checks it.

Untouched in every look: frames and their trim, far sides, the door leaves, the clocked door, RED, the levers, the
glass (and the crush's glass strip), the scales' readouts, S1 and S2, the brass door, the night room and the way
out, and Doom's share: the stone where the hatches were NOW, the Doom gates' pads THEN, Doom's front door NOW (its
leaf and its tracks; the wall over it is the house's).

Groups: yard (the yard at both times), hall (NOW), runs, pens, passages, plates (every picture), things (the decor
sprites). Walls are laid by world position along the wall, each texture's row 0 at its z0 (found from where it
is shown: power33's way).
"""
import math
import os

import gfx_dogs
from power33 import _dot, _line_key, oriented

GROUPS = ("yard", "hall", "runs", "pens", "passages", "plates", "things")
# MAP23's look as Vadim picks it from the look board, group -> look (1 Vivarium, 2 Menagerie, 3 The Kennels):
MIX = dict(yard=1, hall=1, runs=1, pens=1, passages=1, plates=1, things=1)

SKY_TAG = 2380                               # THEN's sky sectors (the day sky, a sky transfer)
DECOR_T = dict(bowl=20199, bucket=20202, store=20203)       # dogs.zs: AjarDogsBowl, AjarDogsBucket, AjarDogsStore
B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NOTES = []                                   # where each picture and thing is (the build prints them)


def setting():
    """AJAR_DOGS: 0 (unset or 0: the plain level), 1, 2, 3, or "mix"."""
    v = (os.environ.get("AJAR_DOGS") or "").strip()
    if v in ("", "0"):
        return 0
    if v == "mix":
        return "mix"
    assert v in ("1", "2", "3"), f"AJAR_DOGS={v}: 0, 1, 2, 3 or mix"
    return int(v)


class Look:
    """The textures a look (or the mix) asks for, by group: walls (a slot at a time, with parameters), pictures,
    flats, sprites; and the faces of the map that wear a picture."""

    def __init__(self, n):
        self.n = n
        self.looks = dict(MIX) if n == "mix" else {g: n for g in GROUPS}
        self.tex = {}                 # name -> spec
        self.keys = {}
        self.count = {}
        self.flats = {}               # name -> (look, slot, then)
        self.sprites = set()          # (kind, look)
        self.faces = []
        self.problems = []
        self.collect = False

    def wall(self, group, slot, then, **params):
        lk = self.looks[group]
        key = ("wall", lk, slot, then, tuple(sorted(params.items())))
        if key not in self.keys:
            assert slot in gfx_dogs.SLOTS, slot
            i = self.count[(lk, slot, then)] = self.count.get((lk, slot, then), -1) + 1
            name = f"AJD{lk}{slot}{'T' if then else 'N'}{B36[i]}"
            self.keys[key] = name
            self.tex[name] = dict(kind="wall", look=lk, slot=slot, then=then, W=gfx_dogs.SLOTS[slot]["w"],
                                  params=params, lo=1e9, hi=-1e9, force=gfx_dogs.SLOTS[slot].get("force"))
        return self.keys[key]

    def flat(self, group, slot, then):
        assert slot in gfx_dogs.FLATS, slot
        lk = self.looks[group]
        name = f"AJD{lk}{slot}{'T' if then else 'N'}"
        self.flats[name] = (lk, slot, then)
        return name

    def pic(self, kind, then, w, base, look=None, **params):
        assert kind in gfx_dogs.PICTURES or kind in gfx_dogs.SLOTS, kind
        lk = look or self.looks["plates"]
        i = self.count[(lk, "Q", then)] = self.count.get((lk, "Q", then), -1) + 1
        name = f"AJD{lk}Q{B36[i // 36]}{B36[i % 36]}{'T' if then else 'N'}"
        b = self.tex[base]
        self.tex[name] = dict(kind="pic", look=lk, pic=kind, then=then, w=w, base=base, params=params, lo=1e9,
                              hi=-1e9, shift=0, force=b.get("force"))
        return name


def apply(S, n):
    """Dress the map of tools/map_sleepingdogs.py (the module S) in look n (1, 2, 3, or "mix": MIX)."""
    m = S.m
    L = Look(n)
    S.LOOKSPEC = L
    secs, polys = m.sectors, m.polys
    OFF = S.OFF[1]                                     # -8192: THEN is NOW + (0, OFF)
    HALF = OFF / 2

    def is_then(i):
        return max(p[1] for p in polys[i]) < HALF

    def nbox(i):
        """The sector's bounding box in NOW's coordinates."""
        d = -OFF if is_then(i) else 0
        p = polys[i]
        return (min(q[0] for q in p), min(q[1] for q in p) + d, max(q[0] for q in p), max(q[1] for q in p) + d)

    def within(b, box):
        return box[0] <= b[0] and b[2] <= box[2] and box[1] <= b[1] and b[3] <= box[3]

    D = dict(dressed={}, ways=set(), gates=set(), yard=set())

    def dress(i, group, wall=None, side=None, ftex=None, ctex=None, way=False):
        then = is_then(i)
        s = secs[i]
        if wall:
            s["wall"] = L.wall(group, wall, then)
            s["side"] = L.wall(group, side or wall, then)
        if ftex:
            s["ftex"] = L.flat(group, ftex, then)
        if ctex:
            s["ctex"] = L.flat(group, ctex, then)
        if way:
            D["ways"].add(i)
        D["dressed"][i] = (group, then)

    STUBS = [(-16, 600, 0, 664), (-16, 1056, 0, 1184), (96, 1216, 160, 1280)]
    CORRIDOR = (768, 1024, 1152, 1152)
    SFUN = (1152, 512, 1408, 640)
    BFUN = (656, -1024, 912, -896)
    PEN_BOXES = [(x1, S.PEN_Y[0], x2, S.PEN_Y[1]) for x1, x2 in S.PENS]
    GATE_BOXES = [(c - 64, S.PEN_Y[1], c + 64, S.PEN_Y[1] + 16) for c in S.PMID] + [S.SGATE, S.IGATE, S.BGATE]
    HATCHES = [(c - 32, 672, c + 32, 688) for c in S.PMID] + [S.SHATCH, S.IHATCH]
    TURNS = [S.KTURN, S.STURN, S.ITURN]
    ANTE, GUARD, DOORWAY = (0, 1280, 256, 1472), (272, 1280, 1024, 1472), (256, 1344, 272, 1408)
    YARD_SECRET = [(-16, 192, 0, 256), (-112, 176, -16, 272)]
    KEEP = []
    for i, s in enumerate(secs):
        b, T = nbox(i), is_then(i)
        sky = s["ctex"] == "F_SKY1"
        pad = s["ftex"] == S.PAD
        if within(b, S.YARD):
            if sky:
                dress(i, "yard", "YW", ftex="YG")
                D["yard"].add(i)
            else:                                                       # the shelter: its roof and the mass over it
                dress(i, "yard", "SM", ftex="YG", ctex="SC")
        elif b in ((640, S.GLASS_Y[0], 656, S.GLASS_Y[1]), (640, S.GATEWAY_Y[0], 656, S.GATEWAY_Y[1])) or \
                (T and b == (288, 512, 352, 528)):
            dress(i, "yard", "SL", ftex="SF", ctex="SF")
        elif T and b in YARD_SECRET:                                    # (its gap a way: the yard's wall over it)
            dress(i, "passages", "KW", ftex="KF", ctex="KK", way=b == YARD_SECRET[0])
        elif not T and (within(b, S.HALL) or b in STUBS):
            dress(i, "hall", "HW", ftex="HF", ctex="HC", way=b in STUBS)
        elif not T and b == CORRIDOR:
            dress(i, "runs", "RW", ftex="RF", ctex="RC", way=True)
        elif not T and s["wall"] == "DOORTRAK" and b in ((288, 512, 352, 528), (288, 576, 352, 592)):
            D["ways"].add(i)                                            # Doom's front door: the wall over it is the room's
            KEEP.append(i)
        elif within(b, S.KRUN) or within(b, S.SRUN) or b == SFUN or within(b, S.BRUN) or b == BFUN or \
                (T and b == S.IRUN) or (not T and b in (ANTE, GUARD)):
            dress(i, "runs", "RW", ftex=None if pad else "RF", ctex=None if sky else "RC")
        elif not T and b == DOORWAY:
            dress(i, "runs", "RW", ftex="RF", ctex="RC", way=True)
        elif b in PEN_BOXES:
            if b == PEN_BOXES[0]:                                       # the weigh plate: one platform, laid from its corner
                dress(i, "pens", "PW", ftex="WP", ctex="PC")
                x1, y2 = min(p[0] for p in polys[i]), max(p[1] for p in polys[i])
                s["raw"] = dict(s["raw"], xpanningfloor=float(-x1 % 256), ypanningfloor=float(y2 % 256))
            else:
                dress(i, "pens", "PW", ftex="PF", ctex="PC")
        elif b in GATE_BOXES:
            if T and s["ceil"] == 0:                                    # a shut gate (pens 2 and 3 THEN): the leaf itself
                dress(i, "pens", "GL", ftex="GT", ctex="GT")
            elif T:                                                     # a gate on its lever: its leaf is the line's upper
                dress(i, "pens", "GR", ftex="GT", ctex="GT")
                D["gates"].add(i)
            else:                                                       # NOW: the gap where the gate was
                dress(i, "pens", "GR", ftex="GT", ctex="GT", way=True)
        elif b in HATCHES:
            dress(i, "pens", "HS", ftex="GT", ctex="GT")
        elif s["floor"] == S.LEDGE and not T and any(within(b, x) for x in S.SLEDGES + S.CLEDGES):
            dress(i, "pens", "PW", side="LF", ftex="LT", ctex="PC")
        elif b in (S.STALL, S.CRUSH_BOX) or (T and b == S.IPEN):
            dress(i, "pens", "PW", ftex="PF", ctex="PC")
        elif b in (S.KPASS, S.KLEG, S.SPASS[int(T)], S.SLEG[int(T)], S.BPASS[int(T)]) or (T and b == S.IPASS) or \
                (not T and b in (S.CLOSET, S.SECRET2)):
            dress(i, "passages", "KW", ftex="KF", ctex="KK")
        elif b in TURNS:
            dress(i, "passages", "TS", ftex="TF", ctex="TF", way=True)
        else:
            KEEP.append(i)
    left = [(i, nbox(i), secs[i]["wall"]) for i in KEEP
            if any(str(secs[i][k]).startswith("AJI") for k in ("wall", "side", "ftex", "ctex"))]
    assert not left, ("sectors in MAP11's look that the look does not dress", left)

    # --- the sky: THEN's sky sectors by day (MAP22's sky; a sky transfer) -------------------------------------
    for i, s in enumerate(secs):
        if s["ctex"] == "F_SKY1" and is_then(i):
            assert not s["id"], i
            s["id"] = SKY_TAG
    (ax, ay), (bx, by) = (192, 128), (640, 128)
    m.line((ax, ay + OFF), (bx, by + OFF), special=190, args=(SKY_TAG, 255), upper="AJ22SKY")

    # --- the pictures and plates; the decor things -----------------------------------------------------------
    hang(S, L, D)
    decor(S, L)

    # --- the hook: every side's last texture and offsets; laid once to find each texture's heights ------------
    m.line_hook = make_hook(S, L, D)
    L.collect = True
    m.parts()
    L.collect = False
    for name, t in L.tex.items():
        if t["hi"] < t["lo"]:
            t["lo"], t["hi"] = 0, 16
        if t.get("force"):
            t["lo"], t["hi"] = min(t["lo"], t["force"][0]), max(t["hi"], t["force"][1])
        t["z0"], t["H"] = int(math.ceil(t["hi"])), int(math.ceil(t["hi"]) - math.floor(t["lo"]))
    for name, t in L.tex.items():           # a picture is painted on its wall's texture: that texture's heights
        if t["kind"] == "pic":
            b = L.tex[t["base"]]
            t["basespec"] = dict(slot=b["slot"], W=b["W"], params=b["params"], look=b["look"], then=b["then"])
    assert not L.problems, L.problems[:8]
    what = (f"the mix ({', '.join(f'{g} {k}' for g, k in L.looks.items())})" if n == "mix"
            else f"the look {n} ({gfx_dogs.NAMES.get(n, '?')})")
    S.MEASURE = getattr(S, "MEASURE", []) + [
        f"MAP23: {what}: {sum(1 for t in L.tex.values() if t['kind'] == 'wall')} wall textures, "
        f"{sum(1 for t in L.tex.values() if t['kind'] == 'pic')} pictures and plates, {len(L.flats)} flats, "
        f"{len(L.sprites)} kinds of decor; {len(L.faces)} faces"] + ["    " + x for x in NOTES]


# =============================================================================================================
# THE PICTURES (group plates; each painted over the wall of its own place's look). Places in NOW's coordinates;
# `out` the way the viewer looks at it. Kept 16 clear of frames, levers, hatches, readouts, shutters and the gap.
# =============================================================================================================
def plan(S, here, side, edge):
    """The house's plan, from the generator's own boxes (gfx_dogs.draw_plan)."""
    rooms = [(S.YARD, "YARD"), (S.HALL, "HALL"), (S.KRUN, "KENNELS"), (S.SRUN, "STALLS"), (S.STALL, ""),
             (S.IRUN, "ISOLATION"), (S.IPEN, ""), (S.BRUN, "BIG/RUN"), (S.CRUSH_BOX, "")]
    rooms += [((x1, S.PEN_Y[0], x2, S.PEN_Y[1]), "") for x1, x2 in S.PENS]
    thin = [S.KPASS, S.KLEG, S.SPASS[1], S.SLEG[1], S.IPASS, S.BPASS[1]]
    xs = [b[0] for b, _ in rooms] + [b[0] for b in thin]
    ys = [b[1] for b, _ in rooms] + [b[1] for b in thin]
    xe = [b[2] for b, _ in rooms] + [b[2] for b in thin]
    ye = [b[3] for b, _ in rooms] + [b[3] for b in thin]
    return dict(box=(min(xs), min(ys), max(xe), max(ye)), rooms=rooms, thin=thin, here=here, side=side, edge=edge)


def hang(S, L, D):
    m = S.m
    OFF = S.OFF[1]
    secs = m.sectors

    def shift_of(P0, P1, base):
        d = (P1[0] - P0[0], P1[1] - P0[1])
        ln = math.hypot(*d)
        return int(round((P0[0] * d[0] + P0[1] * d[1]) / ln)) % L.tex[base]["W"]

    def W(group, slot, then):
        return L.wall(group, slot, then)

    def pic(a, b, out, then, kind, base, parts=("mid",), cut=True, note=None, look=None, **params):
        dy = OFF if then else 0
        P0, P1 = oriented((a[0], a[1] + dy), (b[0], b[1] + dy), out)
        w = int(round(math.hypot(P1[0] - P0[0], P1[1] - P0[1])))
        name = L.pic(kind, then, w, base, look=look, **params)
        L.tex[name]["shift"] = shift_of(P0, P1, base)
        if cut:
            m.cut(P0, P1)
        for part in parts:
            L.faces.append(dict(P0=P0, P1=P1, part=part, name=name, w=w))
        NOTES.append(f"{note or kind} {'THEN' if then else 'NOW'}: {name} on {(a, b)} (NOW's), looking {out}")
        return name

    def wallface(a, b, out, then, name, w):
        dy = OFF if then else 0
        P0, P1 = oriented((a[0], a[1] + dy), (b[0], b[1] + dy), out)
        L.faces.append(dict(P0=P0, P1=P1, part="mid", name=name, w=w))

    BOTH = (True, False)
    for then in BOTH:
        # 1. the shelter's plate, on its mass's east face (the yard's side)
        pic((192, 128), (192, 320), (-1, 0), then, "shelter", W("yard", "SM", then), parts=("top",), cut=False,
            note="1, LINE 6 / THE INSTITUTE", lines=("LINE 6", "THE INSTITUTE"))
        # 2. ANIMAL HOUSE over the front door (on the wall beside it and over it); the plan west of it
        pic((240, 512), (400, 512), (0, 1), then, "house", W("yard", "YF", then), parts=("mid", "top"),
            note="2, ANIMAL HOUSE", lines=("ANIMAL HOUSE",), door=(48, 112), head=128 if then else 96)
        pic((64, 512), (224, 512), (0, 1), then, "plan", W("yard", "YF", then), note="2, the plan (yard)",
            plan=plan(S, (144, 470), -1, 0))
        # 6. DO NOT TAP ON THE GLASS, on the wall over the glass, the yard's side
        pic((640, -64), (640, 128), (1, 0), then, "glass", W("yard", "SL", then), parts=("top",), cut=True,
            note="6, DO NOT TAP ON THE GLASS", lines=("DO NOT TAP", "ON THE GLASS"))
    # the plan once in the hall NOW (its south wall, east of the door)
    pic((416, 592), (576, 592), (0, -1), False, "plan", W("hall", "HW", False), note="2, the plan (hall)",
        plan=plan(S, (496, 640), 1, 768))

    # 3. over each gate, the run's side (the leaf THEN, the run's own wall NOW where the gate is gone); the
    # hatches' names in the passages; GATE by the levers
    GATES = [((c - 64, 960), (c + 64, 960), (0, -1), (f"PEN {k + 1}",) + (("WEIGH PEN",) if k == 0 else ()), BOTH,
              "runs") for k, c in enumerate(S.PMID)]
    GATES += [((1240, 512), (1320, 512), (0, -1), ("STALL",), BOTH, "runs"),
              ((768, 1312), (768, 1440), (1, 0), ("ISOLATION",), (True,), "runs"),
              ((720, -1024), (848, -1024), (0, -1), ("CRUSH",), BOTH, "runs")]
    for a, b, out, words, whens, grp in GATES:
        for then in whens:
            base = W("pens", "GL", then) if then else W("runs", "RW", then)
            pic(a, b, out, then, "gate", base, parts=("top",), cut=False, note=f"3, {' / '.join(words)} (gate)",
                lines=words, head=160 if words == ("CRUSH",) else 128)
    HATCH_NAMES = [((c - 32, 672), (c + 32, 672), (0, 1), (f"PEN {k + 1}",), 0, BOTH) for k, c in enumerate(S.PMID)]
    HATCH_NAMES += [((1248, 288), (1312, 288), (0, 1), ("STALL", "GATE"), 1, (True,)),
                    ((872, 1488), (936, 1488), (0, -1), ("ISOLATION", "GATE"), -1, (True,))]
    for a, b, out, words, arr, whens in HATCH_NAMES:
        for then in whens:
            pic(a, b, out, then, "hatch", W("pens", "HS", then), parts=("top",), cut=False,
                note=f"3, {' / '.join(words)} (hatch)", lines=words, arrow=arr)
    for then in BOTH:                       # pen 1's lever (both times): beside it, east
        pic((-632, 672), (-568, 672), (0, 1), then, "lever", W("passages", "KW", then), note="3, GATE PEN 1 (lever)",
            lines=("GATE", "PEN 1"), arrow=-1)
    pic((928, -1312), (992, -1312), (0, 1), True, "lever", W("passages", "KW", True), note="3, GATE CRUSH (lever)",
        lines=("GATE", "CRUSH"), arrow=-1)

    # 4. the keepers' rules, once in each passage; 5. the weigh record near pen 1's readout
    for a, b, out, whens in (((-704, 544), (-512, 544), (0, -1), BOTH), ((1280, 160), (1472, 160), (0, -1), BOTH),
                             ((384, 1616), (576, 1616), (0, 1), (True,)), ((640, -1456), (832, -1456), (0, -1), BOTH)):
        for then in whens:
            pic(a, b, out, then, "rules", W("passages", "KW", then), note="4, the keepers' rules", lines=gfx_dogs.RULES)
    for then in BOTH:
        pic((-1024, 544), (-832, 544), (0, -1), then, "weigh", W("passages", "KW", then), note="5, the weigh record",
            lines=gfx_dogs.WEIGH)

    # 6. KEEPERS ONLY over each turnstile, the passage's side
    for a, b, out, whens in (((-928, 1040), (-928, 1136), (1, 0), BOTH), ((1424, 1328), (1424, 1424), (-1, 0), BOTH),
                             ((160, 1488), (256, 1488), (0, -1), (True,))):
        for then in whens:
            pic(a, b, out, then, "keepers", W("passages", "KW", then), parts=("mid", "top"),
                note="6, KEEPERS ONLY", lines=("KEEPERS ONLY",), head=96)

    # 7. the name boards: one on each run's wall, a small one by its hatch in the passage
    for a, b, out, run, whens in (((-576, 1216), (-384, 1216), (0, 1), "kennels", BOTH),
                                  ((1408, 960), (1408, 1088), (1, 0), "stalls", BOTH),
                                  ((384, 1280), (576, 1280), (0, -1), "isolation", BOTH),
                                  ((912, 224), (912, 352), (1, 0), "big", BOTH)):
        for then in whens:
            pic(a, b, out, then, "board", W("runs", "RW", then), note=f"7, the name board ({run})", run=run)
    for a, b, out, run, whens in (((-440, 672), (-376, 672), (0, 1), "kennels", BOTH),
                                  ((1168, 288), (1232, 288), (0, 1), "stalls", (True,)),
                                  ((1168, 224), (1232, 224), (0, 1), "stalls", (False,)),
                                  ((792, 1488), (856, 1488), (0, -1), "isolation", (True,)),
                                  ((640, -1312), (704, -1312), (0, 1), "big", (True,)),
                                  ((640, -1360), (704, -1360), (0, 1), "big", (False,))):
        for then in whens:
            pic(a, b, out, then, "card", W("passages", "KW", then), note=f"7, the card ({run})", run=run)

    # the yard's own faces (group yard): the front door's face THEN, the gateway's gate is a slot (the hook)
    wallface((288, 528), (352, 528), (0, 1), True, W("yard", "HD", True), 64)


# =============================================================================================================
# THE DECOR THINGS (group things): small, low, not solid, against walls; args (look, then); appended last
# =============================================================================================================
def decor(S, L):
    m = S.m
    OFF = S.OFF[1]
    lk = L.looks["things"]
    BOTH = (True, False)
    spots = []
    for c in S.PMID:                                                # a bowl on the pen's side of every hatch
        spots.append(("bowl", c, 708, BOTH))
    spots += [("bowl", 1280, 324, BOTH), ("bowl", 904, 1452, BOTH)]
    spots += [("bucket", -890, 658, BOTH), ("bucket", 1220, 276, (True,)), ("bucket", 1220, 210, (False,)),
              ("bucket", 850, 1502, (True,)), ("bucket", 700, -1326, (True,)), ("bucket", 700, -1374, (False,))]
    spots += [("store", -1016, 566, BOTH), ("store", 1514, 1514, BOTH), ("store", 22, 1594, (True,)),
              ("store", 1050, -1436, BOTH)]
    for kind, x, y, whens in spots:
        L.sprites.add((kind, lk))
        for then in whens:
            m.thing(x, y + (OFF if then else 0), DECOR_T[kind], angle=0, args=(lk, 1 if then else 0))
            NOTES.append(f"thing {kind} {'THEN' if then else 'NOW'} at {(x, y)} (NOW's)")


# =============================================================================================================
# THE HOOK
# =============================================================================================================
def make_hook(S, L, D):
    """udmf's line hook: the room's own wall over its ways and in its frames' heads; the house's front; the
    gates' leaves THEN; the faces; every look texture laid by world position along the wall and pegged so that
    its row 0 stands at its z0 (Doom's pegging rules, as power33's hook)."""
    m = S.m
    secs = m.sectors
    OFF = S.OFF[1]
    SKY = "F_SKY1"
    index = {}
    for fc in L.faces:
        index.setdefault(_line_key(fc["P0"], fc["P1"]), []).append(fc)
    dressed, ways, gates, yard = D["dressed"], D["ways"], D["gates"], D["yard"]

    def find(p, q, part):
        for fc in index.get(_line_key(p, q), ()):
            if fc["part"] != part:
                continue
            P0, P1 = fc["P0"], fc["P1"]
            d = (P1[0] - P0[0], P1[1] - P0[1])
            ln = math.hypot(*d)
            u = (d[0] / ln, d[1] / ln)
            if _dot((q[0] - p[0], q[1] - p[1]), u) <= 0:
                continue
            t1 = _dot((p[0] - P0[0], p[1] - P0[1]), u)
            t2 = _dot((q[0] - P0[0], q[1] - P0[1]), u)
            if -0.01 <= t1 and t2 <= ln + 0.01:
                return fc, t1
        return None, 0

    def north(p, q, then):
        return p[1] == q[1] == 512 + (OFF if then else 0) and q[0] > p[0]

    def gateway(p, q, then):
        y0, y1 = (v + (OFF if then else 0) for v in S.GATEWAY_Y)
        return p[0] == q[0] and p[0] in (640, 656) and min(p[1], q[1]) >= y0 and max(p[1], q[1]) <= y1

    def hook(ld, sides, a, b, si, other, given):
        both = [(sides[ld["sidefront"]], si, other, a, b)]
        if other is not None:
            both.append((sides[ld["sideback"]], other, si, b, a))
        for sd, f, o, p, q in both:
            F, B = secs[f], (secs[o] if o is not None else None)
            if f in dressed:
                group, then = dressed[f]
                if B is None:
                    if given["mid"] == "AJSHUT" and gateway(p, q, then):
                        sd["texturemiddle"] = L.wall("yard", "GW", then)
                    elif given["mid"] is None and f in yard and north(p, q, then):
                        sd["texturemiddle"] = L.wall("yard", "YF", then)
                else:
                    gu = given["upper"]
                    own = L.wall("yard", "YF", then) if f in yard and north(p, q, then) else F["wall"]
                    if gu == "AJSHUT" and (f in gates or o in gates):
                        sd["texturetop"] = L.wall("pens", "GL", then)
                    elif gu is not None and gu.startswith("AJI"):
                        sd["texturetop"] = own
                    elif gu is None and F["ceil"] > B["ceil"] and o in ways and f not in ways:
                        sd["texturetop"] = own
            for part, key in (("top", "texturetop"), ("mid", "texturemiddle"), ("bottom", "texturebottom")):
                name = sd.get(key)
                fc, t1 = find(p, q, part)
                if fc is not None and (B is None) == (part == "mid"):
                    name = sd[key] = fc["name"]
                    u = (t1 + fc.get("offx", 0)) % fc["w"]
                    if 0.01 < u < fc["w"] - 0.01:
                        sd["offsetx_" + part] = round(u, 3)
                    else:
                        sd.pop("offsetx_" + part, None)
                t = L.tex.get(name) if name else None
                if t is None:
                    continue
                d = (q[0] - p[0], q[1] - p[1])
                ln = math.hypot(*d)
                if fc is None:
                    Wd = t["W"] if t["kind"] == "wall" else t["w"]
                    u = _dot(p, (d[0] / ln, d[1] / ln)) % Wd
                    if 0.01 < u < Wd - 0.01:
                        sd["offsetx_" + part] = round(u, 3)
                    else:
                        sd.pop("offsetx_" + part, None)
                if part == "mid":
                    if B is not None:
                        continue
                    lo, hi = F["floor"], F["ceil"]
                elif part == "top":
                    if B is None or F["ceil"] <= B["ceil"] or F["ctex"] == B["ctex"] == SKY:
                        continue
                    lo, hi = B["ceil"], F["ceil"]
                else:
                    if B is None or F["floor"] >= B["floor"]:
                        continue
                    lo, hi = F["floor"], B["floor"]
                if L.collect:
                    t["lo"] = min(t["lo"], lo)
                    t["hi"] = max(t["hi"], hi)
                    continue
                H, z0 = t["H"], t["z0"]
                if part == "mid":
                    anchor = F["floor"] + H if ld.get("dontpegbottom") else F["ceil"]
                elif part == "top":
                    anchor = F["ceil"] if ld.get("dontpegtop") else B["ceil"] + H
                else:
                    anchor = F["ceil"] if ld.get("dontpegbottom") else B["floor"]
                off = (z0 - anchor) % H
                if off:
                    sd["offsety_" + part] = float(off)
                else:
                    sd.pop("offsety_" + part, None)
                if lo < z0 - H or hi > z0:
                    L.problems.append(f"{name} (rows {z0 - H}..{z0}) shown {lo}..{hi} at {p}-{q}")
    return hook
