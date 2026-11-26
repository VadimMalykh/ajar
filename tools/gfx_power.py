"""MAP33's looks, the art's shared part (PLAN.md: the look board of MAP33 "Third Person"; the map's side is
tools/power33.py and tools/power33_faces.py). Three looks are three states of one power station:

  1 "Temple of Power" (the 1930s; tools/gfx_power1.py)
  2 "The Grid" (the 1960s; tools/gfx_power2.py, to come)
  3 "Cold Reserve" (long after its last coal; tools/gfx_power3.py, to come)

A look is one module that fills the slots named here: WALLS {slot: painter(w, **params)}, FLATS {slot:
painter() -> Img}, PICTURES {kind: painter(w, spec)}, sky() -> Img. Every texture of the map's is made from a
slot by this file's make(), which builds only the look the build asks for (AJAR_POWER).

Walls. A wall texture is W wide (SLOTS[slot]["w"], its period along the wall: the map lays it by world
position) and H high; its row r stands at the absolute height z0 - r (`Wall`). The map finds H and z0 from
where the texture is shown (power33.apply), so a painter draws by absolute height: a course, the phase band,
a stain stands at one height on every wall of a place, seen from any floor. Parameters:
  F     the floor of the place the wall belongs to (its main floor): what the phase band and the skirting
        are drawn over;
  part  1, 2 or 3: the part whose colour the phase band is in (0: no band: the last hall below its stands);
  top   (rooms of the tile family) the ceiling, for a cornice under it.
The phase band (every look): one course in the part's colour from F + 72 to F + 80 (BAND), drawn in the look's
manner; nothing else of a look is yellow, green or red (but red DANGER plates in part 3's places).
A slot with "fit" is laid on round things (the chimney, the tower, octagons) face by face, each face a whole
number of repeats: its pattern should have a clean edge at x = 0.

Pictures are drawn over the wall they hang on (spec["basespec"]: that wall's slot and parameters, spec["shift"]
its column at the picture's left edge), H and z0 as walls'.
Flats are 64 square unless FLATS says otherwise (128: one tile of 128 laid by the world's grid).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gfx import DIGITS, Img, text


def shade(c, f):
    """gfx.shade, quicker (the looks' painters call it some millions of times)."""
    r, g, b = int(c[0] * f), int(c[1] * f), int(c[2] * f)
    return (255 if r > 255 else 0 if r < 0 else r, 255 if g > 255 else 0 if g < 0 else g,
            255 if b > 255 else 0 if b < 0 else b)

NAMES = {1: "Temple of Power", 2: "The Grid", 3: "Cold Reserve"}
BAND = (72, 80)                             # the phase band: from F + 72 up to F + 80
PART_COLOURS = {1: (255, 208, 64), 2: (88, 200, 80), 3: (232, 72, 56)}
SKY_TOP = 448                               # the yards' sky

# --- the wall slots: what each one is in every look, and its period along the wall -----------------------
SLOTS = {
    "TD": dict(w=64, what="the tile family's rooms: the gatehouse S, the boxes, the gallery, the pump room "
                          "(F, part, top: a cornice under the ceiling)"),
    "CO": dict(w=64, what="corridors, lobbies, passages and stairs of every part (F the sector's own floor: "
                          "the band steps with a stair; part; top)"),
    "GP": dict(w=64, what="the gatehouse's two pillars (F, part)"),
    "CT": dict(w=64, what="the gatekeeper's counter, its front (40 high)"),
    "SK": dict(w=64, what="a floor's own edge, where it is seen from lower (a kerb)"),
    "RI": dict(w=64, what="a stair's step sides, risers of 8 or 16 (kind: stone, marble)"),
    "YD": dict(w=256, what="out of doors: the yards' walls up to the sky at 448 (F, part; damp: the pond's)"),
    "SL": dict(w=64, what="the coal bunker's wall, 176 high: sleepers between posts"),
    "CF": dict(w=64, what="coal heaped: the heaps' and banks' faces in the coal yard"),
    "EF": dict(w=64, what="earth and rubble banks' faces (the middle yard)"),
    "GF": dict(w=64, what="gravel banks' faces (the switchyard)"),
    "SF": dict(w=64, what="stone retaining faces (the stack court's terraces; the middle yard's ledges, with "
                          "the floor's band: F, part)"),
    "PF": dict(w=64, what="stone pitching: the pond's banks and islands"),
    "CH": dict(w=64, fit=True, what="the chimney's shaft, 16 faces from 0 to the sky (absolute: its base to 48)"),
    "BH": dict(w=128, what="the boiler house's walls, 0 to 384 (F, part)"),
    "BS": dict(w=64, what="a boiler's sides (288 high) but its front"),
    "SE": dict(w=64, what="a firing step's edge (16 high)"),
    "AT": dict(w=64, what="the ash tunnel and its cache (F, part)"),
    "PC": dict(w=64, fit=True, what="a pump's casing, octagonal, 72 or 80 high (F: the floor it stands on)"),
    "LP": dict(w=64, what="a lagged pipe run's side, 48 high (the middle yard)"),
    "TH": dict(w=64, what="the turbine hall's walls, -128 to 384, and the gantry's and the mezzanine's (F, part)"),
    "GG": dict(w=64, what="the gantry's edge over R: a crane girder's face, -128 to 0"),
    "TE": dict(w=64, what="a turbine casing's ends (96 high, and down into the spider's pit)"),
    "SW": dict(w=64, what="the spider's pit's walls (40 deep)"),
    "CW": dict(w=64, what="a condenser pit's walls (32 deep)"),
    "WS": dict(w=64, what="the workshop's walls (F, part)"),
    "BN": dict(w=64, what="a bench's front, 40 high"),
    "LA": dict(w=128, what="a lathe's sides, 72 high, 128 long (laid by world position: one machine a face)"),
    "AR": dict(w=64, what="the armoury's walls (F, part)"),
    "TU": dict(w=64, what="the cable tunnel's walls, 0 to 96 (F, part)"),
    "TR": dict(w=64, what="a cable tray's edge, 72 to 96 (the tunnel's upper)"),
    "TF": dict(w=64, what="a transformer's long sides, 8 to 112: its cooling fins"),
    "PL": dict(w=64, what="a transformer's plinth, 8 high"),
    "GL": dict(w=64, what="the switchyard's gantry, 160 high: a lattice girder's face"),
    "RR": dict(w=64, what="the relay room's walls (F, part)"),
    "RC": dict(w=64, what="the relay cabinets' faces, 96 high"),
    "OC": dict(w=64, what="the outfall channel's walls (F, part)"),
    "TW": dict(w=64, fit=True, what="the cooling tower's shell, -64 to the sky (F, part)"),
    "TP": dict(w=64, fit=True, what="the tower's pillars, and its basin's kerb"),
    "TL": dict(w=64, fit=True, what="the tower's ring ledge's face, 96 high"),
    "DK": dict(w=64, what="the duct's walls along R (F, part)"),
    "LH": dict(w=128, what="the switchgear hall's walls (F -96: a dado to 0, no band) and its stands' (F 0, part)"),
    "SN": dict(w=64, what="a switchgear cabinet's ends and its long faces' ground, 64 high"),
    "SH": dict(w=64, what="the secrets' sheds (the pump shed, the hut): plain, nothing to mark them"),
}

# --- the flats ---------------------------------------------------------------------------------------------
FLATS = {
    "TZ": "terrazzo (rooms and corridors)", "PK": "a plaster ceiling", "TK": "the counter's top",
    "CN": "cinder ground (the coal yard; the pond's dry path)", "CL": "coal", "ER": "earth", "ST": "granite setts",
    "SB": "stone slabs (the middle yard's levels, the outfall)", "CD": "concrete with drain channels (the middle yard)",
    "GV": "pale gravel", "BP": "brick paving (the boiler house)", "CQ": "steel chequer plate", "GR": "open grating",
    "BT": "a boiler's top: riveted plate, a manhole (128)", "AS": "ash", "BV": "a brick vault",
    "QT": "quarry tiles", "PT": "a pump's bolted lid (128)", "LG": "a lagged pipe's top", "TT": "terrazzo in large "
    "squares (128: R, the mezzanine)", "RG": "trusses and glazing (R's roof)", "CS": "a turbine casing's top",
    "SP": "steel plate (pits, the armoury)", "WB": "wood blocks (the workshop)", "BB": "a bench's top",
    "LT": "a lathe's top: the bed's ways", "KB": "boards on beams (a roof: the workshop, the boiler house, sheds)",
    "DP": "dark plate (the armoury's ceiling)", "CA": "cables along x (a tray seen from under it)",
    "CB": "cables along y", "CF": "a concrete floor", "KC": "a concrete ceiling", "TO": "a transformer's lid",
    "PN": "a plinth's top", "DG": "dry grass and earth (the pond's banks)", "WC": "wet concrete with drains (the "
    "tower)", "LI": "brown lino", "RT": "a relay cabinet's top", "MC": "marble chequer, 64 squares (128: L's floor)",
    "KF": "coffered plaster (128: L's ceiling)", "TS": "teak boards (the stands)", "SC": "a switchgear cabinet's "
    "top", "KS": "a concrete slab (the tower's ledge)", "TB": "the bunker wall's top: tarred timber",
}
BIG_FLATS = {"BT", "PT", "TT", "MC", "KF", "RG"}       # 128 square

# --- the pictures: what each kind is (power33_faces hangs them) ---------------------------------------------
PICTURES = {
    "plan": "the station plan in S: GENERATING STATION, the rooms, the three ways 1 2 3 (256 x 128 or so)",
    "rules": "the safety rules in S (an enamel board)",
    "shadow": "the shadow board in the workshop: tools' outlines, three gone",
    "single": "the single-line diagram in the relay room: G1, G2, three busbars, TOWN WORKS INSTITUTE",
    "synchro": "the synchroscope in L: SLOW / FAST, three small meters 1 2 3 with lamps",
    "plate": "a plate over a way: words, a bar of the part's colour at its left (words, head, part)",
    "plateside": "a plate beside a way that has no wall over it (a shutter): words, an arrow (words, at, arrow, part)",
    "danger": "DANGER 33000 VOLTS, red and white (at)",
    "window": "a tall window in a yard's wall (lit: 0/1)",
    "bhwindow": "a tall window high in the boiler house's wall",
    "pilaster": "a giant pilaster on the turbine hall's wall",
    "cplate": "the chimney's plate: 1933",
    "boiler": "a boiler's front: two fire doors, gauge glasses, a dial, a valve wheel, its number (n; gap: the "
              "frame's columns, kept clear)",
    "casing": "a turbine casing's long side: the maker's plate No n, 30 MW 3000 RPM (n)",
    "tend": "a transformer's end: the tank, its rating plate T<n>, a DANGER plate if `danger` (n, danger)",
    "cabinet": "a switchgear cabinet's long side: two cubicle doors with a meter, a handle, a number (n)",
    "store": "the armoury's plate over its bars: INSTRUMENT STORE",
}


# === shared helpers =======================================================================================
def h32(x, z, s=0):
    """A number in [0, 1) for a place (x, z) and a seed: the same wherever the place is drawn."""
    v = (x * 73856093) ^ (z * 19349663) ^ (s * 83492791) ^ 0x5bd1e995
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    return ((v ^ (v >> 16)) & 0xffff) / 65536


def jit(c, x, z, s, amt):
    return shade(c, 1 + (h32(x, z, s) - 0.5) * 2 * amt)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Wall:
    """An image whose row r stands at the absolute height z0 - r (its top edge); column c at x = shift + c
    of a pattern `period` wide (x is given to painters as (shift + c) % period)."""

    def __init__(self, w, H, z0, shift=0, period=64):
        self.w, self.H, self.z0, self.shift, self.period = w, H, z0, shift, period
        self.im = Img(w, H)

    @property
    def bot(self):
        return self.z0 - self.H

    def rows(self, ztop, zbot):
        return range(max(0, int(self.z0 - ztop)), min(self.H, int(self.z0 - zbot)))

    def fill(self, ztop, zbot, fn):
        """fn(x, z) -> colour for the rows from ztop down to zbot (z the top edge of the row)."""
        px, w, P, sh = self.im.px, self.w, self.period, self.shift
        xs = [(sh + c) % P for c in range(w)]
        for r in self.rows(ztop, zbot):
            z = self.z0 - r
            base = r * w
            for c in range(w):
                col = fn(xs[c], z)
                px[base + c] = [col[0], col[1], col[2], 255]

    def tint(self, ztop, zbot, fn):
        """fn(x, z, colour) -> colour, over what is drawn."""
        px, w, P, sh = self.im.px, self.w, self.period, self.shift
        for r in self.rows(ztop, zbot):
            z = self.z0 - r
            for c in range(w):
                p = px[r * w + c]
                col = fn((sh + c) % P, z, (p[0], p[1], p[2]))
                px[r * w + c] = [col[0], col[1], col[2], 255]

    def get(self, c, z):
        r = self.z0 - z
        if 0 <= r < self.H and 0 <= c < self.w:
            return tuple(self.im.px[r * self.w + c][:3])
        return None

    def at(self, c, z, col, a=1.0):
        r, c = int(self.z0 - z), int(c)
        if 0 <= r < self.H and 0 <= c < self.w:
            if a >= 1:
                self.im.px[r * self.w + c] = [col[0], col[1], col[2], 255]
            else:
                p = self.im.px[r * self.w + c]
                self.im.px[r * self.w + c] = [int(p[i] + (col[i] - p[i]) * a) for i in range(3)] + [255]

    def rect(self, c1, ztop, c2, zbot, col, a=1.0):
        """Columns c1..c2 (exclusive), heights ztop down to zbot (exclusive)."""
        for r in self.rows(ztop, zbot):
            for c in range(max(0, int(c1)), min(self.w, int(c2))):
                self.at(c, self.z0 - r, col, a)

    def frame(self, c1, ztop, c2, zbot, col, t=1):
        self.rect(c1, ztop, c2, ztop - t, col)
        self.rect(c1, zbot + t, c2, zbot, col)
        self.rect(c1, ztop, c1 + t, zbot, col)
        self.rect(c2 - t, ztop, c2, zbot, col)

    def disc(self, cx, cz, rad, col, a=1.0):
        for z in range(int(cz - rad) - 1, int(cz + rad) + 2):
            for c in range(int(cx - rad) - 1, int(cx + rad) + 2):
                if (c + 0.5 - cx) ** 2 + (z - 0.5 - cz) ** 2 <= rad * rad:
                    self.at(c, z, col, a)

    def ring(self, cx, cz, r1, r2, col):
        for z in range(int(cz - r2) - 1, int(cz + r2) + 2):
            for c in range(int(cx - r2) - 1, int(cx + r2) + 2):
                if r1 <= math.hypot(c + 0.5 - cx, z - 0.5 - cz) <= r2:
                    self.at(c, z, col)

    def line(self, c1, z1, c2, z2, col, t=1):
        n = int(max(abs(c2 - c1), abs(z2 - z1)) * 2) + 1
        for i in range(n + 1):
            c = c1 + (c2 - c1) * i / n
            z = z1 + (z2 - z1) * i / n
            for dc in range(t):
                for dz in range(t):
                    self.at(int(round(c)) + dc, int(round(z)) - dz, col)

    def text(self, s, c, ztop, col, scale=1):
        """Capitals with their top at the height ztop (the game's 5x5 face, 6 to a letter)."""
        im = Img(len(s) * 6 * scale, 5 * scale, (0, 0, 0, 0))
        text(im, s, 0, 0, col, scale)
        self.paste(im, c, ztop)

    def paste(self, im, c, ztop):
        for y in range(im.h):
            for x in range(im.w):
                p = im.px[y * im.w + x]
                if p[3]:
                    self.at(c + x, ztop - y, p[:3])

    def centre(self, s, cx, ztop, col, scale=1):
        self.text(s, cx - (len(s) * 6 * scale - scale) // 2, ztop, col, scale)


def text_width(s, scale=1):
    return len(s) * 6 * scale - scale


def flat(fn, size=64):
    im = Img(size, size)
    for y in range(size):
        for x in range(size):
            c = fn(x, y)
            im.px[y * size + x] = [c[0], c[1], c[2], 255]
    return im


# letters the plates need beyond gfx's: J, Z and the full stop (gfx_institute), K, W, X (gfx_cinema), and these
import gfx_institute                                    # noqa: E402  (its letters)
import gfx_cinema                                       # noqa: E402
DIGITS.update({":": ("00000", "00100", "00000", "00100", "00000"),
               "'": ("00100", "00100", "00000", "00000", "00000"),
               ",": ("00000", "00000", "00000", "00100", "01000"),
               "Q": ("01110", "10001", "10101", "10010", "01101"),
               "/": ("00001", "00010", "00100", "01000", "10000")})


# === the dispatcher =========================================================================================
def module(n):
    """The look's painters: gfx_power<n>; a look not yet drawn falls back to look 1's (said in the build)."""
    import importlib
    try:
        return importlib.import_module(f"gfx_power{n}")
    except ImportError:
        print(f"MAP33's look {n} ({NAMES.get(n, '?')}) is not drawn yet: look 1's art under its names")
        return importlib.import_module("gfx_power1")


def wall_image(look, spec, w=None, H=None, z0=None, shift=0):
    """The wall texture of `spec` (its slot and parameters), or a piece of it w wide for a picture."""
    W = spec["W"]
    out = Wall(w or W, H or spec["H"], spec["z0"] if z0 is None else z0, shift, W)
    look.WALLS[spec["slot"]](out, **spec["params"])
    return out


def picture(look, spec, base_look=None):
    """A picture painted by `look` over its wall (spec["basespec"]) painted by `base_look` (the look of the
    place it hangs on; by default `look`)."""
    if spec.get("basespec"):
        b = dict(spec["basespec"])
        w = wall_image(base_look or look, b, spec["w"], spec["H"], spec["z0"], spec["shift"])
    else:
        w = Wall(spec["w"], spec["H"], spec["z0"])
    look.PICTURES[spec["pic"]](w, spec)
    return w


def make(out, S):
    """The textures, pictures, flats and sky MAP33's map (tools/map_station.py, `S`) asks for in its look or
    its mix (each texture in the look named in it: tools/power33.py, Look)."""
    n = getattr(S, "POWER", 0)
    if not n:
        return
    L = S.LOOKSPEC
    mods = {}

    def mod(k):
        if k not in mods:
            mods[k] = module(k)
        return mods[k]

    def put(kind, nm, im):
        key = f"{kind}/{nm}.png"
        assert key not in out, key
        out[key] = im.png()
    for nm, spec in L.tex.items():
        if spec["kind"] == "wall":
            put("textures", nm, wall_image(mod(spec["look"]), spec).im)
        else:
            b = spec.get("basespec")
            put("textures", nm, picture(mod(spec["look"]), dict(spec, **spec["params"]),
                                        mod(b["look"]) if b else None).im)
    for lk, slot in sorted(L.flats):
        put("flats", f"AJP{lk}{slot}", mod(lk).FLATS[slot]())
    put("textures", f"AJP{L.sky}SKY", mod(L.sky).sky())
