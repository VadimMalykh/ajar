"""MAP23's looks, the art's shared part (PLAN.md, "Look: MAP23, the animal house"; the map's side is
tools/dogs23.py). Three answers to what the institute took its animals for:

  1 "Vivarium"     specimens: a laboratory animal house of the 1960s (tools/gfx_dogs1.py)
  2 "Menagerie"    exhibits: an old zoological garden's house (tools/gfx_dogs2.py, to be painted)
  3 "The Kennels"  kept animals: a working kennel and stable yard (tools/gfx_dogs3.py, to be painted)

A look is one module, art only, that fills every slot named here:

  WALLS    {slot: painter(w, then, **params)}  w a Wall (gfx_power.Wall: row r at the absolute height z0 - r,
           column c at x = (shift + c) % W along the wall); paint by absolute height, so that a course stands at
           one height on every wall of a place.
  FLATS    {slot: painter(then) -> Img}         64 square, or FLATS[slot]["size"].
  PICTURES {kind: painter(w, spec, then)}       w is the wall it hangs on, already painted (in the look of the
           place it hangs in); the painter draws the picture over it. spec: the picture's parameters (below)
           and "w", its width; z0, H as walls'.
  SPRITES  {kind: painter(then) -> (Img, grab)} the decor things (transparent ground; grab: the foot's middle).

`then` is True for THEN (day, light 216, whole) and False for NOW (night, light 120, the ruin forty years on: paint
it so that it still reads at 120). Names: walls AJD<look><slot><T|N><v>, flats AJD<look><slot><T|N>, pictures
AJD<look>Q<nn><T|N>, sprites AJVB (bowl), AJVK (bucket), AJVS (store), frame A..F = look 1 THEN, look 1 NOW, look
2 THEN, ... A look missing (no gfx_dogs<n>.py yet) is drawn with look 1's art under its own names (said in the
build). To add a look: write tools/gfx_dogs<n>.py with the four tables (gfx_dogs1.py is the model), build it
with AJAR_QUICK=1 AJAR_DOGS=<n> AJAR_OUT=build/look<n>.pk3 ./build.sh and shoot it with
tools/board23_shots.sh <n> build/look<n>.pk3.

Rules for every look: nothing in the doors' colours where it could be taken for a door or a key (RED is the
level's door: (200, 60, 50); the clocked door is ivory; keys 1 and 2 are brass); the three looks must differ at a
glance (1 white, green and steel; 2 brick red, cream, dark green and sky blue; 3 black, white, blue-grey and
straw).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gfx import Img                                         # noqa: E402
from gfx_power import Wall, flat, h32, jit, mix, shade, text_width     # noqa: E402,F401  (the letters too)

NAMES = {1: "Vivarium", 2: "Menagerie", 3: "The Kennels"}
LOOKS = (1, 2, 3)

# --- the wall slots: what each one is (its period along the wall; `force`: the heights it must cover, for a
# surface that moves) ------------------------------------------------------------------------------------------
SLOTS = {
    # yard
    "YF": dict(w=64, group="yard", what="the house's front, the yard's north wall (0..256, under the sky); a door "
                                         "and frame 101 in it, the plan and ANIMAL HOUSE hang on it"),
    "YW": dict(w=64, group="yard", what="the yard's other walls (0..256, under the sky; NOW the same, a ruin)"),
    "SM": dict(w=64, group="yard", what="the shelter's mass: its roof's edge and the 144 over it (112..256), "
                                         "seen from the yard; LINE 6 hangs on its east face"),
    "SL": dict(w=64, group="yard", what="sills and frames: the glass wall's strip (sill 0..8, head 136..256), the "
                                         "gateway's head NOW (160..256), the front door's reveal THEN"),
    "GW": dict(w=64, group="yard", what="the big run's gateway THEN, shut (0..256 seen from the yard, 0..192 from "
                                         "the run): a gate, not a door"),
    "HD": dict(w=64, group="yard", what="the front door's face THEN, 64 x 128 from its foot (one face, laid from "
                                         "its left edge: 'Locked for the night.')"),
    # hall
    "HW": dict(w=64, group="hall", what="the hall (0..192) and the short ways off it, NOW only"),
    # runs
    "RW": dict(w=64, group="runs", what="the runs' walls (0..160, the big run 0..192), their funnels, the "
                                         "corridor from the hall, the antechamber and the guard room"),
    # pens
    "PW": dict(w=64, group="pens", what="the pens', the stall's, the crush's walls (0..128, the crush 0..160)"),
    "LF": dict(w=64, group="pens", what="NOW: a ledge's face (0..48): what is left of a wall that stood there "
                                         "THEN, the pen's wall's lowest 48 rows broken off at the top"),
    "GL": dict(w=64, group="pens", force=(0, 192), what="a gate's leaf (the shutter of a pen, the stall, the "
                                                         "isolation pen, the crush), 0..192 (it comes down)"),
    "GR": dict(w=64, group="pens", what="a gate's reveal: its jambs (16 deep) and NOW the gap where it was"),
    "HS": dict(w=64, group="pens", what="a hatch's surround (0..128: under it 0..24, the hole 24..56, over it): "
                                         "seen from the passage and from the pen"),
    # passages
    "KW": dict(w=64, group="passages", what="the keepers' passages and their legs, S1's closet and the "
                                             "secrets (0..128)"),
    "TS": dict(w=64, group="passages", what="a turnstile's jambs (0..96; NOW the jambs of a gap)"),
}

# --- the flats --------------------------------------------------------------------------------------------------
FLATS = {
    "YG": dict(group="yard", what="the yard's ground (and under the shelter)"),
    "SC": dict(group="yard", what="the shelter's ceiling"),
    "SF": dict(group="yard", what="a sill's and a frame's top and underside"),
    "HF": dict(group="hall", what="the hall's floor"),
    "HC": dict(group="hall", what="the hall's ceiling"),
    "RF": dict(group="runs", size=128, what="a run's floor (128: one tile laid by the world's grid)"),
    "RC": dict(group="runs", what="a run's ceiling"),
    "PF": dict(group="pens", what="a pen's floor"),
    "WP": dict(group="pens", size=256, what="pen 1's floor, the weigh plate: one platform 240 by 256 (columns "
                                            "0..240 its width, rows 0..256 its depth; the rest is never seen)"),
    "PC": dict(group="pens", what="a pen's ceiling"),
    "LT": dict(group="pens", what="NOW: a ledge's top, broken masonry"),
    "GT": dict(group="pens", what="a gate's and a hatch's head and sill (steel or stone)"),
    "KF": dict(group="passages", what="a passage's floor"),
    "KK": dict(group="passages", what="a passage's ceiling"),
    "TF": dict(group="passages", what="a turnstile's head and floor"),
}

# --- the pictures: what each kind is; their parameters (dogs23.py hangs them) ---------------------------------
PICTURES = {
    "shelter": "the shelter's plate, on its mass facing the yard: LINE 6 over THE INSTITUTE (lines)",
    "house": "ANIMAL HOUSE over the front door (lines; door: the door's columns (c1, c2) and its head z)",
    "plan": "the plan of the house (plan: boxes and lines in the picture's own units, see draw_plan)",
    "gate": "a gate's name over it, run's side (lines: PEN 1 / WEIGH PEN ...; z: the head of the opening)",
    "hatch": "a hatch's name over it, passage's side, small (lines; arrow: -1 / 1 the gate's lever to the "
             "left / right, 0 none; z: the hatch's head)",
    "lever": "GATE and its name beside a lever (lines; arrow)",
    "rules": "the keepers' rules (lines: KEEPERS, the four, BY ORDER)",
    "weigh": "the weigh record (lines)",
    "glass": "DO NOT TAP ON THE GLASS, over the glass (lines)",
    "keepers": "KEEPERS ONLY over a turnstile, passage's side (lines; z: the turnstile's head)",
    "board": "a run's name board on its wall (run: a key of RUNS; the look says what the animals are)",
    "card": "the small board by a run's hatch (run)",
}

# what each run holds: the name boards' matter (each look shows what it takes the animals for)
RUNS = {
    "kennels": dict(ids=("K 1", "K 2", "K 3"), species="PINK DEMON", latin="DAEMON ROSEUS",
                    names=("ROSIE", "BRUTUS", "PINKY"), mass=(400, 400, 400), kind="demon"),
    "stalls": dict(ids=("S 1", "S 2"), species="HELL KNIGHT", latin="EQUES INFERNI", names=("DUKE", "PRINCE"),
                   mass=(500, 500), kind="knight"),
    "isolation": dict(ids=("I 1", "I 2", "I 3"), species="BARON OF HELL", latin="BARO INFERNI",
                      names=("BARON", "COUNT", "DOC"), mass=(1000, 1000, 500), kind="baron"),
    "big": dict(ids=("B 1",), species="CYBERDEMON", latin="TYRANNUS MAXIMUS", names=("TINY",), mass=(1000,),
                kind="cyber"),
}
RULES = ("KEEPERS", "1 NEVER ENTER A RUN", "2 THEY COME TO THE HATCH", "3 SHUT THE GATE BEHIND THEM",
         "4 WHERE YOU LEAVE THEM", "  THEY STAY", "BY ORDER")
WEIGH = ("WEIGH PEN 1", "ONE HEAD 400", "TWO HEAD 800", "THREE HEAD 1200")

SPRITES = {
    "bowl": dict(letters="AJVB", what="a feed bowl on the pen's side of a hatch (THEN full or clean, NOW rusted "
                                      "or overturned), about 20 x 8"),
    "bucket": dict(letters="AJVK", what="a bucket with a brush, in a passage near its hatch, about 24 x 24"),
    "store": dict(letters="AJVS", what="a store in a passage's dead corner (look 1 steel bins, 2 a barrow of meat "
                                       "or a crate, 3 sacks and a bale), about 40 x 40"),
}


# === shared helpers ==========================================================================================
def frame_of(look, then):
    """The sprite frame of a look at a time (dogs.zs: AjarDogsDecor)."""
    return "ABCDEF"[(look - 1) * 2 + (0 if then else 1)]


def write(w, s, cx, ztop, col, scale=1):
    """A line of capitals centred on column cx, its top at the height ztop."""
    w.centre(s, cx, ztop, col, scale)


def board(w, c1, ztop, c2, zbot, ground, edge=None, t=1):
    """A plain board (a plate) from column c1 to c2, ztop down to zbot."""
    w.rect(c1, ztop, c2, zbot, ground)
    if edge:
        w.frame(c1, ztop, c2, zbot, edge, t)


def lines_block(lines, scales, gap=3):
    """The height of a block of lines of the given scales."""
    return sum(5 * s for s in scales) + gap * (len(lines) - 1)


def write_lines(w, lines, cx, ztop, col, scales=None, gap=3, left=None):
    """Lines of capitals from ztop down, each centred on cx (or from column `left`)."""
    scales = scales or [1] * len(lines)
    z = ztop
    for s, sc in zip(lines, scales):
        if left is None:
            w.centre(s, cx, z, col, sc)
        else:
            w.text(s, left, z, col, sc)
        z -= 5 * sc + gap
    return z


def arrow(w, cx, zmid, d, col, size=4):
    """A small arrow pointing left (d -1) or right (d 1)."""
    for i in range(size):
        w.rect(cx + d * i, zmid + size - 1 - i, cx + d * i + 1, zmid - size + 1 + i, col)
    w.rect(min(cx, cx - d * size * 2), zmid + 1, max(cx, cx - d * size * 2) + 1, zmid - 1, col)


def draw_plan(w, plan, c1, ztop, c2, zbot, ink, ground=None, faint=None, here=None, scale=1):
    """The house's plan in the box (c1, ztop)-(c2, zbot) of the wall: `plan` from dogs23.plan(): dict(box=(x1,
    y1, x2, y2) of the whole in the map's units, rooms=[(box, name)], thin=[box] (the passages: drawn as a thin
    line along their middle), here=(x, y) the YOU ARE HERE spot). The map's north is up."""
    if ground:
        w.rect(c1, ztop, c2, zbot, ground)
    X1, Y1, X2, Y2 = plan["box"]
    pad = 4
    sx = (c2 - c1 - 2 * pad) / (X2 - X1)
    sz = (ztop - zbot - 2 * pad - 8) / (Y2 - Y1)
    s = min(sx, sz)
    ox = c1 + pad + ((c2 - c1 - 2 * pad) - s * (X2 - X1)) / 2
    oz = zbot + pad + ((ztop - zbot - 2 * pad - 8) - s * (Y2 - Y1)) / 2

    def P(x, y):
        return ox + (x - X1) * s, oz + (y - Y1) * s
    for (x1, y1, x2, y2) in plan["thin"]:
        a, b = P(x1, y1), P(x2, y2)
        if (x2 - x1) >= (y2 - y1):
            zm = (a[1] + b[1]) / 2
            w.rect(a[0], zm + 1, b[0], zm, faint or ink)
        else:
            cm = (a[0] + b[0]) / 2
            w.rect(cm, b[1], cm + 1, a[1], faint or ink)
    for (x1, y1, x2, y2), name in plan["rooms"]:
        a, b = P(x1, y1), P(x2, y2)
        w.frame(int(a[0]), int(b[1]) + 1, int(b[0]) + 1, int(a[1]), ink, 1)
    back = ground or w.get(int((c1 + c2) / 2), int((ztop + zbot) / 2)) or (255, 255, 255)
    for (x1, y1, x2, y2), name in plan["rooms"]:
        if not name:
            continue
        a, b = P(x1, y1), P(x2, y2)
        cx, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        words = name.split("/")
        z = cz + (len(words) * 6 - 1) / 2
        for word in words:
            tw = text_width(word)
            w.rect(int(cx) - (tw + 1) // 2 - 1, int(z) + 1, int(cx) + tw // 2 + 2, int(z) - 6, back)
            w.centre(word, int(cx), int(z), ink, 1)
            z -= 6
    if here is not None and plan.get("here"):
        hx, hz = P(*plan["here"])
        side = plan.get("side", -1)
        X0 = P(plan["edge"], 0)[0] if "edge" in plan else hx
        tx = X0 + side * 3
        for k, word in enumerate(("YOU ARE", "HERE")):
            tw = text_width(word)
            left = tx - tw if side < 0 else tx
            w.rect(int(left) - 1, int(hz) + 6 - 6 * k, int(left) + tw + 1, int(hz) - 6 * k, back)
            w.text(word, int(left), int(hz) + 5 - 6 * k, here, 1)
        w.rect(min(hx, tx), int(hz) + 1, max(hx, tx) + 1, int(hz), here)
        w.disc(hx, hz, 2.5, here)


def chips(w, c1, ztop, c2, zbot, col, n, seed, rad=(1, 3)):
    """Chips knocked out of a board (NOW): small irregular spots of `col` inside the box."""
    r = random.Random(seed)
    for _ in range(n):
        cx = r.uniform(c1 + 1, c2 - 1)
        cz = r.uniform(zbot + 1, ztop - 1)
        w.disc(cx, cz, r.uniform(*rad), col)


def rust_run(w, c, ztop, length, col, a=0.55, width=2):
    """A rust run down from a fixing at column c, height ztop."""
    for i in range(int(length)):
        f = a * (1 - i / length)
        for dc in range(width):
            w.at(c + dc, ztop - i, col, f)


def sprite_img(wd, ht):
    return Img(wd, ht, (0, 0, 0, 0))


# === the dispatcher ===========================================================================================
def module(n):
    """The look's painters: gfx_dogs<n>; a look not yet painted falls back to look 1's (said in the build)."""
    import importlib
    try:
        return importlib.import_module(f"gfx_dogs{n}")
    except ImportError:
        print(f"MAP23's look {n} ({NAMES.get(n, '?')}) is not painted yet: look 1's art under its names")
        return importlib.import_module("gfx_dogs1")


def wall_image(look, spec, w=None, H=None, z0=None, shift=0):
    """The wall texture of `spec` (its slot, time and parameters), or a piece of it w wide for a picture."""
    W = spec["W"]
    out = Wall(w or W, H or spec["H"], spec["z0"] if z0 is None else z0, shift, W)
    look.WALLS[spec["slot"]](out, spec["then"], **spec["params"])
    return out


def picture(look, spec, base_look):
    """A picture painted by `look` over its wall (spec["basespec"]) painted by `base_look`."""
    b = spec.get("basespec")
    if b:
        w = wall_image(base_look, b, spec["w"], spec["H"], spec["z0"], spec["shift"])
    else:
        w = Wall(spec["w"], spec["H"], spec["z0"])
    look.PICTURES[spec["pic"]](w, spec, spec["then"])
    return w


def make(out, S):
    """The textures, pictures, flats and sprites MAP23's map (tools/map_sleepingdogs.py, `S`) asks for in its look
    or its mix (tools/dogs23.py, Look); nothing when the build has no look."""
    L = getattr(S, "LOOKSPEC", None)
    if L is None:
        return
    mods = {}

    def mod(k):
        if k not in mods:
            mods[k] = module(k)
        return mods[k]

    def put(kind, nm, data):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = data
    for nm, spec in L.tex.items():
        if spec["kind"] == "wall":
            put("textures", nm, wall_image(mod(spec["look"]), spec).im.png())
        else:
            b = spec.get("basespec")
            put("textures", nm, picture(mod(spec["look"]), dict(spec, **spec["params"]),
                                        mod(b["look"]) if b else None).im.png())
    for nm, (lk, slot, then) in sorted(L.flats.items()):
        im = mod(lk).FLATS[slot](then)
        size = FLATS[slot].get("size", 64)
        assert (im.w, im.h) == (size, size), (nm, im.w, im.h)
        put("flats", nm, im.png())
    for kind, lk in sorted(L.sprites):
        for then in (True, False):
            im, grab = mod(lk).SPRITES[kind](then)
            put("sprites", f"{SPRITES[kind]['letters']}{frame_of(lk, then)}0", im.png(grab=grab))
