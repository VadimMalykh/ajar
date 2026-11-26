"""MAP33's looks, the map's side (tools/map_station.py calls apply() once the map is built and checked:
AJAR_POWER unset or "mix", the game's own look, MIX below; 1, 2, 3 one look whole; 0 the plain level). The three looks are three states of one power station (1 "Temple of Power", 2 "The
Grid", 3 "Cold Reserve"); the art is tools/gfx_power.py (the slots, shared) and tools/gfx_power<k>.py (each
look's painters). This file says which slot each surface of the map wears; it is the same for every look.

A look changes textures, their offsets, flats and tints, and hangs pictures on pieces cut out of walls (a
line split, never a new sector). Nothing else of the map changes: heights, light, things, tags, specials,
flags (tools/power33_compare.py checks it against the plain level).

Rules (the session's brief, 2026-11-26):
- the doors' frames, far sides, time doors, shutters, glass, railings, bars, cases, the last hall's lit
  patches and steam strip (their floors), water: as built. The wall over a doorway, a window or a bay is the
  room's own (as MAP20's look did it), so that plates can hang over the ways.
- ways (corridor and doorway sectors) keep their part's tint; rooms lose theirs (white light).
- every wall of a part's place carries the phase band: one course in the part's colour 72 to 80 over that
  place's main floor (gfx_power.BAND), drawn into its wall texture. A way's band is over its own floor
  (stepped on stairs).
- walls at absolute heights (each texture's row 0 at its z0, `hook`), patterns by world position.
- Doom's share: the bays and pedestals of R and L, the exit room (Doom's own textures).

The slots are named in gfx_power.SLOTS (walls) and gfx_power.FLATS (flats); pictures by gfx_power.PICTURES.
A wall texture is f"AJP{look}{slot}{nn}": a slot with its parameters (the floor its band is over, the part),
H and z0 from the heights it is shown at (found by laying the map once). A picture is f"AJP{look}Q{nn}".

The mix: each place belongs to a group (GROUPS) and wears its group's look; the names carry the look they
are painted in, so that AJP1..., AJP2... and AJP3... stand side by side in one build. A picture (the five, the
plates over and beside the ways, INSTRUMENT STORE, DANGER plates on walls: PICTURE_KINDS) is painted by the
"pictures" look over the wall of the place it hangs on, in that place's look; an object's own face (a
boiler's front, a casing's side, a transformer's end, a cabinet's, the chimney's plate, windows and
pilasters drawn on a wall) goes with its place.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import gfx_power

B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# R's six bays (map_station.py names them BAYS, and then gives the name to the last hall's eight)
R_BAYS = [(5376, 2048, 5472, 2144), (6016, 2048, 6112, 2144), (6624, 2048, 6720, 2144),
          (6944, 2304, 7040, 2400), (6944, 2560, 7040, 2656), (6944, 3072, 7040, 3168)]
DOOM_TEX = {"MARBGRAY", "SUPPORT3", "EXITSTON"}

# MAP33's look as chosen by Vadim from the look board (2026-11-26): group -> look (1 "Temple of Power",
# 2 "The Grid", 3 "Cold Reserve"). AJAR_POWER unset (or "mix") builds this; Doom's share is as it is.
MIX = dict(yards=2, boiler=1, machine=1, cable=1, hall=3, pictures=3)
GROUPS = ("yards", "boiler", "machine", "cable", "hall", "pictures")
# yards: everything out of doors (the coal yard, the stack court and the chimney, the yard in the middle on its
#        three levels and the pump shed, the switchyard and its hut, the pond, the outfall, the cooling tower)
#        and the sky; boiler, machine, cable: part 1's, 2's and 3's rooms and ways indoors (the gatehouse
#        with part 1; box 2 with part 2, box 3 with part 3); hall: the switchgear hall L and its three stands;
#        pictures: the kinds below.
PICTURE_KINDS = {"plan", "rules", "shadow", "single", "synchro", "plate", "plateside", "store", "danger"}
PART_GROUP = {1: "boiler", 2: "machine", 3: "cable"}


def _b36(n):
    return B36[n // 36] + B36[n % 36]


class Look:
    """The textures a look (or the mix) asks for: walls (a slot and its parameters, in a look), pictures,
    flats; and the faces of the map that wear a picture or an object's own art. `looks` maps each group to
    its look; use(group) says which group's places are being dressed."""

    def __init__(self, n):
        self.n = n                    # 1, 2, 3 or "mix"
        self.looks = dict(MIX) if n == "mix" else {g: n for g in GROUPS}
        self.cur = None
        self.tex = {}                 # name -> spec: kind "wall" or "pic", look, slot/kind, W, params, lo, hi
        self.keys = {}
        self.count = {}
        self.flats = set()            # (look, slot)
        self.faces = []               # dict(P0, P1, part, name, w, scale, offx): power33_faces
        self.problems = []
        self.collect = False
        self.sky = self.looks["yards"]

    def use(self, group):
        self.cur = self.looks[group]

    def wall(self, slot, look=None, **params):
        lk = look or self.cur
        key = ("wall", lk, slot, tuple(sorted(params.items())))
        if key not in self.keys:
            assert slot in gfx_power.SLOTS, slot
            i = self.count[(lk, slot)] = self.count.get((lk, slot), -1) + 1
            name = f"AJP{lk}{slot}{_b36(i)}"
            self.keys[key] = name
            self.tex[name] = dict(kind="wall", look=lk, slot=slot, W=gfx_power.SLOTS[slot]["w"], params=params,
                                  lo=1e9, hi=-1e9)
        return self.keys[key]

    def flat(self, slot, look=None):
        assert slot in gfx_power.FLATS, slot
        lk = look or self.cur
        self.flats.add((lk, slot))
        return f"AJP{lk}{slot}"

    def pic(self, kind, w, base=None, **params):
        assert kind in gfx_power.PICTURES, kind
        lk = self.looks["pictures"] if kind in PICTURE_KINDS else self.cur
        i = self.count[(lk, "Q")] = self.count.get((lk, "Q"), -1) + 1
        name = f"AJP{lk}Q{_b36(i)}"
        self.tex[name] = dict(kind="pic", look=lk, pic=kind, w=w, base=base, params=params, lo=1e9, hi=-1e9,
                              shift=0)
        return name


def oriented(a, b, out):
    """(P0, P1) of the wall a-b seen looking `out`: P0 at the viewer's left (the viewer is to the right of
    P0 -> P1, as Doom's front side is)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    return (a, b) if dy * -out[0] - dx * -out[1] > 0 else (b, a)


def _dot(p, d):
    return p[0] * d[0] + p[1] * d[1]


def apply(S, n):
    """Dress the map of tools/map_station.py (the module S) in look n (1, 2, 3, or "mix": MIX)."""
    m = S.m
    L = Look(n)
    S.LOOKSPEC = L
    secs = m.sectors
    polys = m.polys
    part_colours = {S.Y_WAY, S.G_WAY, S.R_WAY}

    def bbox(i):
        p = polys[i]
        return (min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p))

    def within(i, box):
        b = bbox(i)
        return box[0] <= b[0] and b[2] <= box[2] and box[1] <= b[1] and b[3] <= box[3]

    def part(i):
        return secs[i]["raw"].get("user_part") or 0

    # --- which sectors are left as built ------------------------------------------------------------
    OPEN = set(S.OPENINGS)
    GLASS = set()
    for key, pr in m.lineprops.items():
        if len(key) == 2 and pr.get("blockeverything"):
            a, b = tuple(key)
            for i, p in enumerate(polys):
                if secs[i]["wall"] == "AJTRIM" and a in p and b in p:
                    GLASS.add(i)
    CASES = set(S.CASES)
    KEEP = set()
    for i, s in enumerate(secs):
        w = s["wall"]
        if w in ("AJTRIM", "AJSHUT") or w.startswith("AJTR") or w.startswith("AJNO") or w.startswith("AJARCH") \
                or i in CASES or s["ftex"] == "FWATER1":
            KEEP.add(i)
    WAYS = set()             # corridors, stairs, lobbies: the room's own wall goes on over them
    BAYS = set()             # Doom's bays: the room's own wall over their mouths
    ROLE = {}
    LOOKOF = {}              # sector -> the look it is dressed in (the hook's own walls: pits, trays)

    def dress(i, wall=None, side=None, ftex=None, ctex=None, tint="room", way=False, role=None):
        s = secs[i]
        if wall:
            s["wall"] = wall
        if side:
            s["side"] = side
        if ftex:
            s["ftex"] = ftex
        if ctex:
            s["ctex"] = ctex
        if tint == "room":
            s["color"] = None
        elif tint == "floor" and s["color"] is not None:     # a way out of doors: its tint on its floor only (not
            s["raw"] = dict(s["raw"], color_floor=s["color"])  # up a yard's wall to the sky)
            s["color"] = None
        if way:
            WAYS.add(i)
        ROLE[i] = role or ROLE.get(i)
        LOOKOF[i] = L.cur

    W, F_ = L.wall, L.flat
    SKY = "F_SKY1"

    def riser(i, kind="stone"):
        """A stair's step sides: the riser's height is its step's."""
        return W("RI", kind=kind)

    # the last hall's patches and strip: their floors exactly as built (AJLITE, its tint and light in raw),
    # the ceiling the hall's, no tint over it
    L.use("hall")
    for i, s in enumerate(secs):
        if s["ftex"] == "AJLITE":
            s["color"] = None
            s["ctex"] = F_("KF")
            KEEP.add(i)

    def ksky(i):
        return SKY if secs[i]["ctex"] == SKY else None

    # --- part 1 -------------------------------------------------------------------------------------
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE:
            continue
        p = part(i)
        fl = s["floor"]
        col = s["color"]
        # S, the gatehouse
        L.use("yards" if within(i, S.YARD_BOX) or (within(i, S.STACK) and s["ctex"] == SKY) else "boiler")
        if within(i, S.S_BOX):
            if fl == 40:
                dress(i, wall=W("TD", F=0, part=1, top=192), side=W("CT"), ftex=F_("TK"), ctex=F_("PK"), role="S")
            else:
                dress(i, wall=W("TD", F=0, part=1, top=192), side=riser(i), ftex=F_("TZ"), ctex=F_("PK"), role="S")
        # the coal yard
        elif within(i, S.YARD_BOX):
            wall = W("YD", F=0, part=1)
            if s["side"] == "AJWALL" or (s["ftex"] == "AJPIT" and col == S.COAL):
                dress(i, wall=wall, side=W("CF"), ftex=F_("CL"), role="yard")
            elif fl == 176:
                dress(i, wall=wall, side=W("SL"), ftex=F_("TB"), role="yard")
            else:
                dress(i, wall=wall, side=W("CF"), ftex=F_("CN"), role="yard")
        # the boiler house
        elif within(i, S.BOIL_BOX) and s["id"] == S.BOIL:
            wall = W("BH", F=0, part=1)
            if fl == 288:
                dress(i, wall=wall, side=W("BS"), ftex=F_("BT"), role="boiler")
            elif fl == 16:
                dress(i, wall=wall, side=W("SE"), ftex=F_("CQ"), role="boil")
            elif fl == S.CAT:
                dress(i, wall=wall, side=wall, ftex=F_("GR"), role="boil")
            else:
                dress(i, wall=wall, side=wall, ftex=F_("BP"), ctex=F_("KB"), role="boil")
            secs[i]["ctex"] = F_("KB")
        # the ash tunnel and the cache
        elif within(i, (3600, 3840, 4352, 3968)):
            dress(i, wall=W("AT", F=0, part=1), side=W("AT", F=0, part=1), ftex=F_("AS"), ctex=F_("BV"), tint=None,
                  way=True, role="ash")
        elif within(i, S.CACHE):
            dress(i, wall=W("AT", F=0, part=1), ftex=F_("AS"), ctex=F_("BV"), role="ash")
        # the pump room
        elif within(i, S.PUMP1) and fl >= S.CAT:
            if fl == S.CAT:
                dress(i, wall=W("TD", F=S.CAT, part=1, top=S.CAT + 192), side=riser(i), ftex=F_("QT"), ctex=F_("PK"),
                      role="pumproom")
            else:
                dress(i, wall=W("TD", F=S.CAT, part=1, top=S.CAT + 192), side=W("PC", F=S.CAT), ftex=F_("PT"),
                      role="pump")
        # the stack court
        elif within(i, S.STACK) and s["ctex"] == SKY:
            wall = W("YD", F=0, part=1)
            if fl == 0:
                dress(i, wall=wall, side=W("SF"), ftex=F_("ST"), role="stack")
            else:
                dress(i, wall=wall, side=W("SF"), ftex=F_("ER"), role="stack")
        # the gantry over R
        elif s["id"] == S.GANTRY:
            dress(i, wall=W("TH", F=0, part=1), side=W("GG"), ftex=F_("CQ"), ctex=F_("RG"), role="gantry")

    # --- R, the turbine hall; the mezzanine ---------------------------------------------------------
    L.use("machine")
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE or s["id"] != S.RT or not within(i, S.R_BOX):
            continue
        fl = s["floor"]
        wall = W("TH", F=S.RF, part=2)
        b = bbox(i)
        if any(within(i, c) for c in S.CASINGS) and fl == S.RF + S.CASING_H:
            dress(i, wall=wall, side=W("TE"), ftex=F_("CS"), role="casing")
        elif within(i, S.SPIDER_PIT) and fl < S.RF:
            dress(i, wall=wall, side=wall, ftex=F_("SP"), role="spiderpit")
        elif any(within(i, c) for c in S.CONDENSERS) and fl < S.RF:
            dress(i, wall=wall, side=wall, ftex=F_("SP"), role="condpit")
        elif any(within(i, c) for c in R_BAYS) and fl == S.RF + S.BAY_H:
            dress(i, wall="MARBGRAY", side="MARBGRAY", ftex="FLOOR4_8", ctex="CEIL5_1", role="rbay")
        else:
            dress(i, wall=wall, side=W("SK"), ftex=F_("TT"), ctex=F_("RG"), role="R")
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE:
            continue
        if within(i, S.MEZZ):
            dress(i, wall=W("TH", F=0, part=2), side=W("TH", F=S.RF, part=2), ftex=F_("TT"), ctex=F_("RG"),
                  role="mezz")         # (its edge over R: R's own wall)

    # --- part 2 -------------------------------------------------------------------------------------
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE:
            continue
        fl = s["floor"]
        L.use("machine")
        if s["id"] == S.ajarthird.box_tag(2) or s["id"] == S.ajarthird.box_tag(3):
            k = 2 if s["id"] == S.ajarthird.box_tag(2) else 3
            L.use(PART_GROUP[k])
            dress(i, wall=W("TD", F=0, part=k, top=160), side=riser(i), ftex=F_("TZ"), ctex=F_("PK"), role="box")
        elif within(i, S.GALLERY):
            dress(i, wall=W("TD", F=0, part=2, top=160), side=riser(i), ftex=F_("TZ"), ctex=F_("PK"), role="gallery")
        elif within(i, S.ARMOURY):
            dress(i, wall=W("AR", F=0, part=2), ftex=F_("SP"), ctex=F_("DP"), role="armoury")
        elif within(i, S.WORK_BOX) and s["id"] == S.WORK:
            wall = W("WS", F=0, part=2)
            if fl == 40:
                dress(i, wall=wall, side=W("BN"), ftex=F_("BB"), role="bench")
            elif fl == 72:
                dress(i, wall=wall, side=W("LA"), ftex=F_("LT"), role="lathe")
            else:
                dress(i, wall=wall, side=W("SK"), ftex=F_("WB"), ctex=F_("KB"), role="workshop")

    # --- the yard in the middle ---------------------------------------------------------------------
    L1, L2, L3, YP = S.L1, S.L2, S.L3, S.YPLACE
    L.use("yards")
    for i in [S.LEDGE1_SEC] + S.TERR_SECS:
        dress(i, wall=W("YD", F=0, part=1), side=W("SF", F=S.FLOOR2, part=2), ftex=F_("SB"), role="ledge1")
    for i in [S.LEDGE3_SEC] + S.CORNER_SECS:
        dress(i, wall=W("YD", F=S.SOUTH3, part=3), side=W("SF", F=S.FLOOR2, part=2), ftex=F_("SB"), role="ledge3")
    for i in S.FLOOR_SECS:
        s = secs[i]
        fl = s["floor"]
        wall = W("YD", F=S.FLOOR2, part=2)
        if s["side"] == "AJBOLT" and fl == S.FLOOR2 + S.PUMP_H:
            dress(i, wall=wall, side=W("PC", F=S.FLOOR2), ftex=F_("PT"), role="ypump")
        elif s["side"] == "AJBOLT":
            dress(i, wall=wall, side=W("LP"), ftex=F_("LG"), role="pipe")
        elif fl > S.FLOOR2:
            dress(i, wall=wall, side=W("EF"), ftex=F_("ER"), role="bank")
        else:
            dress(i, wall=wall, side=W("SF", F=S.FLOOR2, part=2), ftex=F_("CD"), role="yfloor")
    dress(S.SHED_SECS[0], wall=W("SH"), ftex=F_("CF"), ctex=F_("KB"), role="shed")
    KEEP.add(S.SHED_SECS[1])
    for i, s in enumerate(secs):            # the yard's stairs: stone, out of doors
        if i in KEEP or i in ROLE:
            continue
        if s["id"] == YP and s["ctex"] == SKY and s["color"] == S.G_WAY:
            dress(i, wall=W("YD", F=S.FLOOR2, part=2), side=riser(i), ftex=F_("SB"), tint="floor", role="ystairs")

    # --- part 3 -------------------------------------------------------------------------------------
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE:
            continue
        fl = s["floor"]
        col = s["color"]
        L.use("cable" if any(within(i, t) for t in S.TUN) or within(i, S.RELAY) or within(i, S.DUCT) else "yards")
        if any(within(i, t) for t in S.TUN):
            low = s["ceil"] == 72
            dress(i, wall=W("TU", F=0, part=3), side=W("TU", F=0, part=3), ftex=F_("CF"),
                  ctex=F_(("CB" if within(i, S.TUN[0]) else "CA") if low else "KC"), tint=None, way=True, role="tunnel")
        elif within(i, S.SW) and s["ctex"] == SKY:
            wall = W("YD", F=0, part=3)
            if any(within(i, t) for t in S.TRANS) and fl == 112:
                dress(i, wall=wall, side=W("TF"), ftex=F_("TO"), role="trans")
            elif fl == 8:
                dress(i, wall=wall, side=W("PL"), ftex=F_("PN"), role="plinth")
            elif fl == 160:
                dress(i, wall=wall, side=W("GL"), ftex=F_("CQ"), role="swgantry")
            elif fl > 0:
                dress(i, wall=wall, side=W("GF"), ftex=F_("GV"), role="sbank")
            else:
                dress(i, wall=wall, side=W("GF"), ftex=F_("GV"), role="switchyard")
        elif within(i, (2832, 928, 2960, 1056)):
            dress(i, wall=W("SH"), ftex=F_("CF"), ctex=F_("KB"), role="hut")
        elif within(i, S.RELAY):
            if fl == 96:
                dress(i, wall=W("RR", F=0, part=3), side=W("RC"), ftex=F_("RT"), role="relaycab")
            else:
                dress(i, wall=W("RR", F=0, part=3), side=riser(i), ftex=F_("LI"), ctex=F_("PK"), role="relay")
        elif within(i, S.POND) and s["ctex"] == SKY:
            wall = W("YD", F=S.PG, part=3, damp=1)
            if fl == S.PG:
                dress(i, wall=wall, side=W("PF"), ftex=F_("CN"), role="pond")
            else:
                dress(i, wall=wall, side=W("PF"), ftex=F_("DG"), role="pbank")
        elif within(i, S.CHANNEL):
            dress(i, wall=W("OC", F=-8, part=3), side=W("OC", F=-8, part=3), ftex=F_("SB"),
                  tint="floor", role="outfall")
        elif s["id"] == S.TOWER:
            wall = W("TW", F=S.TF, part=3)
            if fl == S.TF + 96:
                dress(i, wall=wall, side=W("TL"), ftex=F_("KS"), role="tledge")
            else:
                dress(i, wall=wall, side=W("TP"), ftex=F_("WC"), role="tower")
        elif within(i, S.DUCT):
            dress(i, wall=W("DK", F=S.RF, part=3), side=W("DK", F=S.RF, part=3), ftex=F_("CF"), ctex=F_("KC"), role="duct")

    # --- the last hall L, its stands, the exit room ---------------------------------------------------
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE:
            continue
        fl = s["floor"]
        L.use("hall")
        if s["id"] == S.LASTT:
            if any(within(i, p) for p in S.PEDESTALS) and fl == S.FL + 72:
                dress(i, wall="MARBGRAY", side="MARBGRAY", ftex="FLOOR4_8", ctex=F_("KF"), role="pedestal")
            elif any(within(i, b) for b in S.BAYS) and fl == S.FL + 72:
                dress(i, wall="MARBGRAY", side="MARBGRAY", ftex="FLOOR4_8", ctex="TLITE6_1", role="lbay")
                BAYS.add(i)
            elif any(within(i, c) for c in S.SWITCHGEAR) and fl == S.FL + S.CAB_H:
                dress(i, wall=W("LH", F=S.FL, part=0), side=W("SN"), ftex=F_("SC"), ctex=F_("KF"), role="cabinet")
            elif within(i, S.STEPS):
                dress(i, wall=W("LH", F=S.FL, part=0), side=W("RI", kind="marble"), ftex=F_("MC"), ctex=F_("KF"),
                      role="lsteps")
            else:
                dress(i, wall=W("LH", F=S.FL, part=0), side=W("SK"), ftex=F_("MC"), ctex=F_("KF"), role="L")
        elif s["id"] in S.ST:
            k = S.ST.index(s["id"]) + 1
            dress(i, wall=W("LH", F=0, part=k), side=W("LH", F=0, part=k), ftex=F_("TS"), ctex=F_("PK"), role="stand")
        elif s["id"] == S.OUT or within(i, (9104, 2816, 9168, 2944)):
            last = within(i, (9104, 2816, 9168, 2944))
            dress(i, wall="EXITSTON", side="EXITSTON", ftex="FLOOR4_8", ctex="TLITE6_1" if last else "CEIL5_1",
                  role="exitroom")

    # --- the ways: every corridor, lobby, passage and stair not dressed above -----------------------
    for i, s in enumerate(secs):
        if i in KEEP or i in ROLE:
            continue
        col = s["color"]
        p = part(i)
        if col in part_colours and p:
            L.use("yards" if s["ctex"] == SKY else PART_GROUP[p])
            dress(i, wall=W("CO", F=s["floor"], part=p, top=s["ceil"]), side=riser(i),
                  ftex=F_("TZ"), ctex=SKY if s["ctex"] == SKY else F_("PK"), tint=None, way=True, role="way")
    LEFT = [i for i, s in enumerate(secs) if i not in KEEP and i not in ROLE]
    assert not LEFT, ("sectors the look does not dress", [(i, bbox(i), secs[i]["wall"], secs[i]["color"]) for i in LEFT[:12]])

    # --- the faces: pictures, plates, objects' own art, Doom's edges ---------------------------------
    import power33_faces
    power33_faces.hang(S, L, ROLE)

    # --- the hook: every side's last texture and offsets; laid once to find each texture's heights ----
    m.line_hook = make_hook(S, L, OPEN, GLASS, WAYS, BAYS, ROLE, LOOKOF)
    L.collect = True
    m.parts()
    L.collect = False
    for name, t in L.tex.items():
        if t["hi"] < t["lo"]:               # (named on sides where it is not drawn: a small one all the same)
            t["lo"], t["hi"] = 0, 16
        t["z0"], t["H"] = int(math.ceil(t["hi"])), int(math.ceil(t["hi"]) - math.floor(t["lo"]))
    for name, t in L.tex.items():           # a picture is painted on its wall's texture: that texture's heights
        if t["kind"] == "pic" and t["base"]:
            b = L.tex[t["base"]]
            t["basespec"] = dict(slot=b["slot"], W=b["W"], params=b["params"], look=b["look"])
    S.MAPINFO = {'sky1 = "SKY2", 0': f'sky1 = "AJP{L.sky}SKY", 0.2'}
    what = (f"the mix ({', '.join(f'{g} {k}' for g, k in L.looks.items())})" if n == "mix"
            else f"the look {n} ({gfx_power.NAMES.get(n, '?')})")
    S.MEASURE.append(f"    {what}: {sum(1 for t in L.tex.values() if t['kind'] == 'wall')} "
                     f"wall textures, {sum(1 for t in L.tex.values() if t['kind'] == 'pic')} pictures and plates, "
                     f"{len(L.flats)} flats; {len(L.faces)} faces")


def make_hook(S, L, OPEN, GLASS, WAYS, BAYS, ROLE, LOOKOF):
    """udmf's line hook: the room's own wall over its ways; the faces; every look texture laid by world
    position along the wall and pegged so that its row 0 stands at its z0 (Doom's pegging rules: a one-sided
    wall from its ceiling, or its floor if lower-unpegged; an upper from the lower ceiling, or its own if
    upper-unpegged; a lower from the higher floor, or its own ceiling if lower-unpegged)."""
    m = S.m
    secs = m.sectors
    SKY = "F_SKY1"
    # the faces by the line they lie on
    index = {}
    for fc in L.faces:
        index.setdefault(_line_key(fc["P0"], fc["P1"]), []).append(fc)
    over = OPEN | GLASS | BAYS

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

    def hook(ld, sides, a, b, si, other, given):
        both = [(sides[ld["sidefront"]], si, other, a, b)]
        if other is not None:
            both.append((sides[ld["sideback"]], other, si, b, a))
        for sd, f, o, p, q in both:
            F, B = secs[f], (secs[o] if o is not None else None)
            if B is not None and given["upper"] is None and F["ceil"] > B["ceil"] and f not in over:
                # the room's own wall over a doorway, a window, a bay, a way
                if o in over or (o in WAYS and f not in WAYS):
                    sd["texturetop"] = F["wall"]
            if B is not None and given["lower"] is None and o in OPEN and f not in OPEN:
                sd["texturebottom"] = F["side"]
            if B is not None and F["floor"] < B["floor"] and given["lower"] is None:
                r = ROLE.get(f)
                if r in ("spiderpit", "condpit"):         # a pit's own walls
                    sd["texturebottom"] = L.wall("SW" if r == "spiderpit" else "CW", look=LOOKOF[f])
            if B is not None and F["ceil"] > B["ceil"] and ROLE.get(f) == "tunnel" and ROLE.get(o) == "tunnel":
                sd["texturetop"] = L.wall("TR", look=LOOKOF[f])  # a cable tray's edge
            for part, key in (("top", "texturetop"), ("mid", "texturemiddle"), ("bottom", "texturebottom")):
                name = sd.get(key)
                if name is None or given[{"top": "upper", "mid": "mid", "bottom": "lower"}[part]] is not None:
                    continue
                fc, t1 = find(p, q, part)
                d = (q[0] - p[0], q[1] - p[1])
                ln = math.hypot(*d)
                if fc is not None:
                    name = sd[key] = fc["name"]
                    sc = fc.get("scale")
                    if sc:
                        sd["scalex_" + part] = round(sc, 5)
                    u = (t1 * (sc or 1) + fc.get("offx", 0)) % fc["w"]
                    if 0.01 < u < fc["w"] - 0.01:
                        sd["offsetx_" + part] = round(u, 3)
                    else:
                        sd.pop("offsetx_" + part, None)
                t = L.tex.get(name)
                if t is None:
                    continue
                if fc is None:
                    # the wall's run: by world position along it (round things: each face fitted with whole repeats)
                    Wd = t["W"]
                    if p[0] != q[0] and p[1] != q[1] and gfx_power.SLOTS[t["slot"]].get("fit"):
                        k = max(1, round(ln / Wd))
                        sd["scalex_" + part] = round(Wd * k / ln, 5)
                        sd.pop("offsetx_" + part, None)
                    else:
                        u = _dot(p, (d[0] / ln, d[1] / ln)) % Wd
                        if 0.01 < u < Wd - 0.01:
                            sd["offsetx_" + part] = round(u, 3)
                        else:
                            sd.pop("offsetx_" + part, None)
                # the heights it is shown at, and the row at its z0
                if part == "mid":
                    if B is not None:
                        continue
                    lo, hi = F["floor"], F["ceil"]
                elif part == "top":
                    if B is None or F["ceil"] <= B["ceil"] or F["ctex"] == B["ctex"] == SKY:
                        continue                # (no upper is drawn between two skies)
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


def _line_key(p, q):
    """The infinite line through p and q, as a hashable key (direction up to sign, and offset)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    g = math.hypot(dx, dy)
    ux, uy = dx / g, dy / g
    if ux < -1e-9 or (abs(ux) < 1e-9 and uy < 0):
        ux, uy = -ux, -uy
    c = -uy * p[0] + ux * p[1]
    return (round(ux, 4), round(uy, 4), round(c, 1))
