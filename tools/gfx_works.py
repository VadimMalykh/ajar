"""MAP32's look, "Deep Field" (Vadim, 2026-11-21; AJAR_WORKS in map_secret2.py,
the dressing in works32.py, the lights in src/zscript/works.zs).

A plant hung in space where time doors are tested: dark plated steel, thin
lines of ice-white light (ICE), a little orange for hazard and marking.

Every name is AJZ... Most textures are composites (the TEXTURES lump written
here): a plate drawn once per wall height and thin strips of light laid over
it, so that the moving variants cost no pictures. A FAMILY is five letters,
AJZ<part><height>, and its variants are the last three:
  M00..M15  the lights move: the high line breathes, the dashes of the
            conduit at the foot run to the right (as the wall is seen)
  L00..L15  the same, the dashes running to the left
  S00       steady (a fight that is on, a box)
  W00       plain white and steady (a room that is done)
  D00       the high line failed (a stutter: works.zs swaps it in)
works.zs picks the variant by the room's state; a name of any other shape is
never touched by it.
Parts: W a wall; U the wall over a time door (a lit line across its top);
V, Y a strip beside a time door, the door on its left (V) or right (Y), the
conduit climbing it; P the press's chamber (a load scale on every plate);
T the steel lintel over the chamber's mouth (TEST BAY 3, LOAD 4000 t); X
the wall over a time door in the chamber (96 high, hung from the door);
1..9 a wall with a sign on it (SIGNS, from works32.py); CF the floor with a
conduit every 256 (dashes run east); KC a ceiling with a light line.
Heights (the fifth letter): A 96, B 128, C 160, D 192, E 224, F 256, G 288,
H 320. A wall is hung from the ceiling, so its high line is a quarter of the
height down and its conduit 24 over the floor.
Pictures, not composites: AJZN<h> a frame's surround (pale neutral steel, a
white line), AJZO<h> the wall over a frame (a white lit strip), AJZQ a slab's
or pillar's side (an orange line along its top), AJZSTP a step, AJZFT the
tread plate floor, AJZPLT the press's face (ribbed), AJZBED the bed under it
(a composite: hazard border, the load cells), AJZHA/AJZHB/AJZHC/AJZHD the
hatch round the way out, AJZSKY the stars, AJZN0..AJZN9 signs over openings.
Sprite AJZT: a dash of white light, laid flat (the plate line, works.zs).
"""
import math
import random
import struct
import zlib

from gfx import DIGITS, text

DIGITS.update({"t": ("00000", "01000", "11100", "01000", "00110"),
               "K": ("10010", "10100", "11000", "10100", "10010"),
               "W": ("10001", "10001", "10101", "11011", "10001"),
               "X": ("10001", "01010", "00100", "01010", "10001")})

ICE = (159, 216, 255)
ORANGE = (255, 138, 48)
WHITE = (236, 240, 244)
HEIGHTS = {"A": 96, "B": 128, "C": 160, "D": 192, "E": 224, "F": 256, "G": 288, "H": 320}
CODE = {h: c for c, h in HEIGHTS.items()}
FRAMES = 16             # a breath: FRAMES x TICS tics (3.2 seconds)
TICS = 7
PERIOD, STEP = 48, 12   # the dashes: one every PERIOD, STEP further each frame (60 a second)
DOOR_TOP = 102          # the lit line over a time door, over the floor (the door is 96 high)
STRIP = 32              # a strip beside a time door


def high_row(h):
    """The high line's top row: a quarter of the wall down from the ceiling."""
    return round(h / 4) - 1


def foot_row(h):
    """The conduit's top row: its middle 24 over the floor."""
    return h - 26


class Canvas:
    """RGBA, fast enough for big pictures; draws text with gfx.text."""

    def __init__(self, w, h, c=(0, 0, 0, 0)):
        self.w, self.h = w, h
        c = tuple(c) + (255,) * (4 - len(c))
        self.b = bytearray(bytes(c) * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 4
            self.b[i:i + 4] = bytes(tuple(c) + (255,) * (4 - len(c)))

    def get(self, x, y):
        i = (y * self.w + x) * 4
        return tuple(self.b[i:i + 4])

    def rect(self, x1, y1, x2, y2, c):
        x1, x2, y1, y2 = max(0, x1), min(self.w, x2), max(0, y1), min(self.h, y2)
        if x1 >= x2:
            return
        row = bytes(tuple(c) + (255,) * (4 - len(c))) * (x2 - x1)
        for y in range(y1, y2):
            i = (y * self.w + x1) * 4
            self.b[i:i + len(row)] = row

    def frame(self, x1, y1, x2, y2, c, t=1):
        self.rect(x1, y1, x2, y1 + t, c)
        self.rect(x1, y2 - t, x2, y2, c)
        self.rect(x1, y1, x1 + t, y2, c)
        self.rect(x2 - t, y1, x2, y2, c)

    def shade(self, x1, y1, x2, y2, f):
        for y in range(max(0, y1), min(self.h, y2)):
            for x in range(max(0, x1), min(self.w, x2)):
                i = (y * self.w + x) * 4
                for k in range(3):
                    self.b[i + k] = max(0, min(255, int(self.b[i + k] * f)))

    def noise(self, amount, seed):
        rnd = random.Random(seed)
        b = self.b
        for i in range(0, len(b), 4):
            d = rnd.randint(-amount, amount)
            for k in range(3):
                v = b[i + k] + d
                b[i + k] = 0 if v < 0 else 255 if v > 255 else v

    def paste(self, src, x0, y0):
        for y in range(src.h):
            for x in range(src.w):
                c = src.get(x, y)
                if c[3]:
                    self.set(x0 + x, y0 + y, c)

    def png(self, grab=None):
        raw = b"".join(b"\0" + bytes(self.b[y * self.w * 4:(y + 1) * self.w * 4]) for y in range(self.h))

        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
        out = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
        if grab:
            out += chunk(b"grAb", struct.pack(">ii", *grab))
        return out + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")


def scale(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --- the plates ---------------------------------------------------------------
TOP, BOT = (31, 41, 56), (18, 24, 33)
SEAM, SEAM_HI, RIVET = (9, 12, 17), (46, 58, 76), (74, 88, 108)
GROOVE = (5, 7, 10)


def plate(h, *, top=TOP, bot=BOT, seam=SEAM, hi=SEAM_HI, rivet=RIVET, seed=1, w=128, grooves=True):
    """A wall of plates 128 wide, h high, hung from the ceiling: rows of 64
    from the top, rivets at the corners, a groove for the high line and one
    for the conduit at the foot."""
    im = Canvas(w, h)
    for y in range(h):
        im.rect(0, y, w, y + 1, mix(top, bot, y / max(1, h - 1)))
    im.noise(3, seed)
    for x in range(0, w, 128):
        im.rect(x, 0, x + 1, h, seam)
        im.rect(x + 1, 0, x + 2, h, hi)
    for y in range(0, h, 64):
        im.rect(0, y, w, y + 1, seam)
        im.rect(0, y + 1, w, y + 2, hi)
        for x in range(0, w, 128):
            for rx in (x + 7, x + 120):
                for ry in (y + 7, y + 56):
                    if ry < h:
                        im.rect(rx, ry, rx + 2, ry + 2, rivet)
                        im.set(rx + 1, ry + 2, seam)
                        im.set(rx + 2, ry + 1, seam)
    if grooves:
        r = high_row(h)
        im.rect(0, r - 2, w, r + 5, GROOVE)
        im.rect(0, r - 3, w, r - 2, hi)
        im.rect(0, r + 5, w, r + 6, seam)
        f = foot_row(h)
        im.rect(0, f - 3, w, f + 7, GROOVE)
        im.rect(0, f - 4, w, f - 3, hi)
        im.rect(0, f + 7, w, f + 8, (40, 48, 60))
        im.rect(0, h - 4, w, h, (12, 15, 20))                # the skirting
    return im


def hiline(c, w=128):
    im = Canvas(w, 3)
    im.rect(0, 0, w, 1, scale(c, 0.55))
    im.rect(0, 1, w, 2, c)
    im.rect(0, 2, w, 3, scale(c, 0.55))
    return im


def conduit(c, w=128 + PERIOD, moving=True):
    """The conduit at the foot: a dim line with bright dashes."""
    im = Canvas(w, 4)
    dim = scale(c, 0.30)
    im.rect(0, 0, w, 4, (16, 24, 34))
    im.rect(0, 1, w, 3, dim)
    if moving:
        for x in range(0, w, PERIOD):
            im.rect(x, 0, x + 14, 4, c)
            im.rect(x + 2, 1, x + 12, 3, mix(c, (255, 255, 255), 0.6))
    return im


def vconduit(c, length, phase):
    """The conduit climbing beside a time door, its dashes `phase` up."""
    im = Canvas(4, length)
    im.rect(0, 0, 4, length, (16, 24, 34))
    im.rect(1, 0, 3, length, scale(c, 0.30))
    for y in range(-PERIOD, length + PERIOD, PERIOD):
        y0 = y - phase
        im.rect(0, y0, 4, y0 + 14, c)
        im.rect(1, y0 + 2, 3, y0 + 12, mix(c, (255, 255, 255), 0.6))
    return im


def breath(f):
    """The high line's strength at frame f: it swells and sinks once a cycle."""
    return 0.42 + 0.58 * (0.5 - 0.5 * math.cos(2 * math.pi * f / FRAMES))


# --- composites ---------------------------------------------------------------
class Comp:
    """The TEXTURES lump, the ANIMDEFS lines and the GLDEFS brightmaps."""

    def __init__(self):
        self.tex, self.anim, self.glow = [], [], []

    def define(self, kind, name, w, h, patches):
        lines = [f'{kind} "{name}", {w}, {h}', "{"]
        for p in patches:
            nm, x, y = p[:3]
            extra = p[3] if len(p) > 3 else None
            if extra:
                lines.append(f'\tPatch "{nm}", {x}, {y} {{ Alpha {extra:.3f} Style Translucent }}')
            else:
                lines.append(f'\tPatch "{nm}", {x}, {y}')
        lines.append("}")
        self.tex.append("\n".join(lines))

    def brightmap(self, kind, name, path):
        self.glow.append(f'brightmap {kind} "{name}"\n{{\n\tmap "{path}"\n}}')

    def animate(self, kind, names):
        self.anim.append(f"{kind} {names[0]}\n" + "".join(f"\tpic {n} tics {TICS}\n" for n in names))


def family(out, comp, fam, w, h, base, lit, *, conduit_at=None, flat=False, brightmap=None, extra=()):
    """Every variant of the family `fam` (5 letters): `base` the patches
    under the lights, `lit` a list of (x, y, width) where the high line (and
    lines like it) lie, `conduit_at` (x0, y, width) of the conduit (or None),
    `extra` patches over all. Brightmap: the picture at `brightmap`."""
    kind = "Flat" if flat else "WallTexture"
    akind = "flat" if flat else "texture"

    def lines(strip, alpha):
        return [(strip, x, y, alpha) if alpha < 0.999 else (strip, x, y) for x, y, _ in lit for _ in [0]]

    def cond(strip, off):
        if not conduit_at:
            return []
        x0, y, width = conduit_at
        return [(strip, x0 + xx + off, y) for xx in range(0, width, 128)]

    names = {}
    for v in ("M", "L"):
        names[v] = []
        for f in range(FRAMES):
            a = breath(f)
            off = -PERIOD + (f * STEP) % PERIOD if v == "M" else -((f * STEP) % PERIOD)
            nm = f"{fam}{v}{f:02d}"
            comp.define(kind, nm, w, h, base + lines("AJZHL", a) + cond("AJZCD", off) + list(extra))
            names[v].append(nm)
        comp.animate(akind, names[v])
    comp.define(kind, f"{fam}S00", w, h, base + lines("AJZHL", 0.8) + cond("AJZCD", 0) + list(extra))
    comp.define(kind, f"{fam}W00", w, h, base + lines("AJZHW", 0.9) + cond("AJZCW", 0) + list(extra))
    comp.define(kind, f"{fam}D00", w, h, base + cond("AJZCD", 0) + list(extra))
    if brightmap:
        for v in ("M", "L"):
            for nm in names[v]:
                comp.brightmap(akind, nm, brightmap)
        for v in "SWD":
            comp.brightmap(akind, f"{fam}{v}00", brightmap)


def bright(w, h, rows=(), rects=(), mask=None):
    """A brightmap: white where it is lit whatever the room's light."""
    im = Canvas(w, h, (0, 0, 0, 255))
    for y0, n in rows:
        im.rect(0, y0, w, y0 + n, (255, 255, 255))
    for r in rects:
        im.rect(*r, (255, 255, 255))
    if mask:
        for (x0, y0), src in mask:
            for y in range(src.h):
                for x in range(src.w):
                    if src.get(x, y)[3] and sum(src.get(x, y)[:3]) > 200:
                        im.set(x0 + x, y0 + y, (255, 255, 255))
    return im


# --- pictures ---------------------------------------------------------------------
def hazard(w, h, phase=0):
    im = Canvas(w, h)
    for y in range(h):
        for x in range(w):
            im.set(x, y, ORANGE if ((x + y + phase) // 12) % 2 == 0 else (18, 18, 20))
    return im


def sign_plate(lines, w, s=3, ink=ORANGE):
    """A sign: orange capitals on a black plate with an orange edge."""
    lh = 5 * s + 4
    h = lh * len(lines) + 8
    im = Canvas(w, h, (12, 14, 18, 255))
    im.frame(0, 0, w, h, ORANGE, 2)
    im.rect(3, 3, w - 3, 4, (40, 30, 20))
    for i, ln in enumerate(lines):
        tw = len(ln) * 6 * s - s
        text(im, ln, (w - tw) // 2, 6 + i * lh, ink, s)
    return im


def tread(seed=5):
    im = Canvas(128, 128, (26, 31, 38, 255))
    im.noise(3, seed)
    for y in range(0, 128, 16):
        for x in range(0, 128, 16):
            ox = 8 if (y // 16) % 2 else 0
            for i in range(9):
                im.set(x + ox + 3 + i, y + 3 + i // 2 + (i % 2), (44, 51, 60))
                im.set(x + ox + 3 + i, y + 4 + i // 2 + (i % 2), (14, 17, 22))
    im.rect(0, 0, 128, 1, (10, 12, 16))
    im.rect(0, 0, 1, 128, (10, 12, 16))
    im.rect(0, 1, 128, 2, (40, 48, 58))
    im.rect(1, 0, 2, 128, (40, 48, 58))
    return im


def ceiling_plate():
    im = plate(128, top=(26, 33, 44), bot=(22, 28, 38), grooves=False, seed=9)
    im.rect(0, 56, 128, 72, (36, 44, 56))
    im.rect(0, 58, 128, 70, GROOVE)
    return im


def neutral(h, seed=4):
    """A frame's surround: pale neutral steel, a white line (a picture)."""
    im = plate(h, top=(150, 154, 158), bot=(128, 132, 136), seam=(92, 96, 100), hi=(176, 180, 184),
               rivet=(196, 198, 202), seed=seed, grooves=False)
    r = high_row(h)
    im.rect(0, r - 2, 128, r + 5, (60, 62, 66))
    im.rect(0, r, 128, r + 3, WHITE)
    return im


def slab_side():
    im = plate(320, top=(30, 38, 50), bot=(20, 26, 35), grooves=False, seed=13)
    im.rect(0, 0, 128, 2, (60, 40, 24))
    im.rect(0, 2, 128, 6, ORANGE)
    im.rect(0, 6, 128, 7, (60, 40, 24))
    return im


def step_side():
    im = Canvas(128, 64, (24, 30, 39, 255))
    im.noise(3, 21)
    im.rect(0, 0, 128, 3, ORANGE)
    im.rect(0, 3, 128, 4, (50, 30, 16))
    for x in range(0, 128, 32):
        im.rect(x, 4, x + 1, 64, (12, 15, 20))
    return im


def platen():
    im = Canvas(128, 128, (40, 46, 54, 255))
    im.noise(3, 23)
    for y in range(0, 128, 16):
        im.rect(0, y, 128, y + 3, (64, 72, 82))
        im.rect(0, y + 3, 128, y + 5, (52, 58, 68))
        im.rect(0, y + 12, 128, y + 16, (20, 24, 30))
    for x in (0, 64):
        im.rect(x, 0, x + 2, 128, (16, 18, 22))
    return im


def bed_tile():
    """The bed under the press: scored steel with a grid."""
    im = Canvas(128, 128, (54, 58, 64, 255))
    im.noise(4, 27)
    rnd = random.Random(27)
    for _ in range(40):                       # scores
        x, y, n = rnd.randrange(128), rnd.randrange(128), rnd.randrange(6, 22)
        for i in range(n):
            im.set((x + i) % 128, (y + i // 3) % 128, (78, 82, 88))
    for v in range(0, 128, 32):
        im.rect(v, 0, v + 1, 128, (34, 37, 42))
        im.rect(0, v, 128, v + 1, (34, 37, 42))
    return im


def starfield():
    w, h = 1024, 256
    im = Canvas(w, h, (2, 3, 7, 255))
    rnd = random.Random(32)
    # a faint blue nebula with a touch of orange, along a slanting band
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            u = (x / w) * 2 * math.pi
            band = math.exp(-((y - 110 - 40 * math.sin(u)) / 46.0) ** 2)
            cloud = 0.5 + 0.25 * math.sin(3 * u + y / 23.0) + 0.25 * math.sin(7 * u - y / 31.0)
            k = band * cloud
            warm = max(0.0, math.sin(u + 1.2)) ** 6 * k
            c = (int(2 + 22 * k + 40 * warm), int(3 + 30 * k + 14 * warm), int(7 + 52 * k))
            im.rect(x, y, x + 2, y + 2, c)
    for _ in range(1300):
        x, y = rnd.randrange(w), rnd.randrange(h)
        b = rnd.random() ** 3
        c = mix((90, 100, 130), (250, 252, 255), b)
        im.set(x, y, c)
        if b > 0.6:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                im.set(x + dx, y + dy, scale(c, 0.45))
    return im


def dash_sprite():
    im = Canvas(64, 10)
    for y in range(10):
        a = 1 - abs(y - 4.5) / 5.0
        for x in range(64):
            e = min(1.0, min(x, 63 - x) / 8.0)
            v = int(255 * max(0.0, a) * e)
            im.set(x, y, (255, 255, 255, v))
    return im


def scale_strip(h):
    """A load scale: ticks every 16 from the floor, numbers every 64."""
    im = Canvas(28, h)
    paint = (190, 196, 202)
    for k in range(0, h, 16):
        y = h - 1 - k
        if k == 0:
            continue
        long = k % 64 == 0
        im.rect(0, y, 12 if long else 6, y + 1, paint if not long else ORANGE)
        if long:
            s = str(k)
            text(im, s, 14 - (len(s) - 2) * 6 if len(s) > 2 else 14, y - 2, ORANGE, 1)
    im.rect(0, 0, 1, h, paint)
    return im


# --- the families ----------------------------------------------------------------
def wall_base(h, part, comp, out):
    """The patches of a plain wall of height h, 128 wide."""
    return [(f"AJZB{CODE[h]}", 0, 0)]


def make(out, signs=()):
    """Writes the pictures and returns the text of TEXTURES, ANIMDEFS lines
    and GLDEFS, as a dict."""
    comp = Comp()
    out["patches/AJZHL.png"] = hiline(ICE).png()
    out["patches/AJZHW.png"] = hiline(WHITE).png()
    out["patches/AJZCD.png"] = conduit(ICE).png()
    out["patches/AJZCW.png"] = conduit(WHITE, moving=False).png()
    for c, h in HEIGHTS.items():
        out[f"patches/AJZB{c}.png"] = plate(h, seed=40 + h).png()
    # walls: W, and the chamber's P (a scale on every plate)
    for c, h in HEIGHTS.items():
        hr, fr = high_row(h), foot_row(h)
        bm = f"brightmaps/ajzw{c.lower()}.png"
        out[bm] = bright(128, h, rows=((hr, 3), (fr, 4))).png()
        family(out, comp, f"AJZW{c}", 128, h, [(f"AJZB{c}", 0, 0)], [(0, hr, 128)], conduit_at=(0, fr, 128),
               brightmap=bm)
    out["patches/AJZSC.png"] = scale_strip(192).png()
    h, c = 192, "D"
    family(out, comp, "AJZPD", 128, h, [(f"AJZB{c}", 0, 0), ("AJZSC", 6, 0)], [(0, high_row(h), 128)],
           conduit_at=(0, foot_row(h), 128), brightmap="brightmaps/ajzwd.png")
    # the wall over a time door (the line over the door: DOOR_TOP over the floor),
    # and the strips beside it
    for c, h in HEIGHTS.items():
        if h < 128:
            continue
        hr, fr, dr = high_row(h), foot_row(h), h - DOOR_TOP - 1
        bm = f"brightmaps/ajzu{c.lower()}.png"
        out[bm] = bright(128, h, rows=((hr, 3), (dr, 3))).png()
        family(out, comp, f"AJZU{c}", 128, h, [(f"AJZB{c}", 0, 0)], [(0, hr, 128), (0, dr, 128)],
               brightmap=bm)
        # the strips: the vertical conduit from the foot's conduit to the door's line
        length = fr + 4 - dr
        for ph in range(PERIOD // STEP):
            out[f"patches/AJZV{c}{ph}.png"] = vconduit(ICE, length, ph * STEP).png()
        out[f"patches/AJZV{c}S.png"] = vconduit(ICE, length, 0).png()
        out[f"patches/AJZV{c}W.png"] = vconduit(WHITE, length, 0).png()
        for part, lx in (("V", 4), ("Y", STRIP - 8)):
            fam = f"AJZ{part}{c}"
            bm = f"brightmaps/ajz{part.lower()}{c.lower()}.png"
            hx = (lx - 128 + 4, lx + 4) if part == "V" else (lx, lx + 128)     # the door's line, to the door side
            dl = (0, dr, lx + 4, dr + 3) if part == "V" else (lx, dr, STRIP, dr + 3)
            out[bm] = bright(STRIP, h, rows=((hr, 3), (fr, 4)), rects=((lx, dr, lx + 4, fr + 4), dl)).png()
            under = [(f"AJZB{c}", 0, 0)]
            door_line = (hx[0], dr, 128)
            names = {}
            for v in ("M", "L"):
                names[v] = []
                for f in range(FRAMES):
                    a = breath(f)
                    off = -PERIOD + (f * STEP) % PERIOD
                    nm = f"{fam}{v}{f:02d}"
                    comp.define("WallTexture", nm, STRIP, h, under + [
                        ("AJZHL", 0, hr, a), ("AJZCD", off, fr), ("AJZHL", door_line[0], dr, a),
                        (f"AJZV{c}{f % (PERIOD // STEP)}", lx, dr)])
                    names[v].append(nm)
                comp.animate("texture", names[v])
            comp.define("WallTexture", f"{fam}S00", STRIP, h, under + [
                ("AJZHL", 0, hr, 0.8), ("AJZCD", 0, fr), ("AJZHL", door_line[0], dr, 0.8), (f"AJZV{c}S", lx, dr)])
            comp.define("WallTexture", f"{fam}W00", STRIP, h, under + [
                ("AJZHW", 0, hr, 0.9), ("AJZCW", 0, fr), ("AJZHW", door_line[0], dr, 0.9), (f"AJZV{c}W", lx, dr)])
            comp.define("WallTexture", f"{fam}D00", STRIP, h, under + [
                ("AJZCD", 0, fr), ("AJZHL", door_line[0], dr, 0.8), (f"AJZV{c}S", lx, dr)])
            for v in ("M", "L"):
                for nm in names[v]:
                    comp.brightmap("texture", nm, bm)
            for v in "SWD":
                comp.brightmap("texture", f"{fam}{v}00", bm)
    # the chamber's door: the wall over it, 96 high, hung from the door (rows 0..95 of a wall of 192)
    out["brightmaps/ajzxd.png"] = bright(128, 96, rows=((high_row(192), 3), (192 - DOOR_TOP - 1, 3))).png()
    family(out, comp, "AJZXD", 128, 96, [("AJZBD", 0, 0)], [(0, high_row(192), 128), (0, 192 - DOOR_TOP - 1, 128)],
           brightmap="brightmaps/ajzxd.png")
    # the lintel over the chamber's mouth: 1280 wide, 320 high, the hall's wall over it; under the hall's
    # high line TEST BAY 3 and LOAD 4000 t between hazard stripes; below the lintel's 128, the press's face
    hz = hazard(64, 24)
    out["patches/AJZHZ.png"] = hz.png()
    s1 = sign_plate(["TEST BAY 3"], 220, 3)
    s2 = sign_plate(["LOAD 4000 t"], 240, 3)
    out["patches/AJZG3.png"] = s1.png()
    out["patches/AJZG4.png"] = s2.png()
    face = Canvas(128, 192, (40, 46, 54, 255))
    face.noise(3, 25)
    for y in range(0, 192, 24):
        face.rect(0, y, 128, y + 4, (66, 74, 84))
        face.rect(0, y + 18, 128, y + 24, (20, 24, 30))
    out["patches/AJZPF.png"] = face.png()
    hr = high_row(320)
    base = [("AJZBH", x, 0) for x in range(0, 1280, 128)]
    base += [("AJZPF", x, 128) for x in range(0, 1280, 128)]
    base += [("AJZHZ", x, 96) for x in range(0, 1280, 64)]
    s1x, s2x = 640 - 40 - s1.w, 640 + 40
    base += [("AJZG3", s1x, 94), ("AJZG4", s2x, 94)]
    out["brightmaps/ajzth.png"] = bright(1280, 320, rows=((hr, 3),), mask=[((s1x, 94), s1), ((s2x, 94), s2)]).png()
    family(out, comp, "AJZTH", 1280, 320, base, [(x, hr, 128) for x in range(0, 1280, 128)],
           brightmap="brightmaps/ajzth.png")
    # the floor: tread plate; with a conduit every 256 (in the middle of the flat), its dashes running east
    tr = tread()
    out["flats/AJZFT.png"] = tr.png()
    out["patches/AJZFT.png"] = tr.png()
    gr = Canvas(256, 12, (6, 8, 11, 255))
    gr.rect(0, 0, 256, 1, (52, 60, 72))
    gr.rect(0, 11, 256, 12, (52, 60, 72))
    out["patches/AJZFG.png"] = gr.png()
    out["brightmaps/ajzcf.png"] = bright(256, 256, rows=((126, 4),)).png()
    fbase = [("AJZFT", x, y) for x in (0, 128) for y in (0, 128)] + [("AJZFG", 0, 122)]
    names = []
    for f in range(PERIOD // STEP):
        nm = f"AJZCFM{f:02d}"
        comp.define("Flat", nm, 256, 256, fbase + [("AJZCD", -PERIOD + f * STEP + xx, 126) for xx in (0, 128, 256)])
        names.append(nm)
        comp.brightmap("flat", nm, "brightmaps/ajzcf.png")
    comp.animate("flat", names)
    for v, strip in (("S", "AJZCD"), ("W", "AJZCW"), ("D", "AJZCD")):
        comp.define("Flat", f"AJZCF{v}00", 256, 256, fbase + [(strip, xx, 126) for xx in (0, 128)])
        comp.brightmap("flat", f"AJZCF{v}00", "brightmaps/ajzcf.png")
    # the ceiling: steel with a line of light across every 128
    out["patches/AJZKP.png"] = ceiling_plate().png()
    out["patches/AJZKL.png"] = hiline(ICE, 128).png()
    out["brightmaps/ajzkc.png"] = bright(128, 128, rows=((59, 10),)).png()
    for v, c in (("S", ICE), ("W", WHITE)):
        lamp = Canvas(128, 10)
        lamp.rect(0, 0, 128, 10, scale(c, 0.55))
        lamp.rect(0, 2, 128, 8, c)
        for x in range(0, 128, 32):
            lamp.rect(x, 0, x + 2, 10, (30, 36, 46))
        out[f"patches/AJZK{v}.png"] = lamp.png()
        comp.define("Flat", f"AJZKC{v}00", 128, 128, [("AJZKP", 0, 0), (f"AJZK{v}", 0, 59)])
        comp.brightmap("flat", f"AJZKC{v}00", "brightmaps/ajzkc.png")
    # pictures
    for c, h in HEIGHTS.items():
        out[f"textures/AJZN{c}.png"] = neutral(h).png()
        out[f"brightmaps/ajzn{c.lower()}.png"] = bright(128, h, rows=((high_row(h), 3),)).png()
        comp.brightmap("texture", f"AJZN{c}", f"brightmaps/ajzn{c.lower()}.png")
        if h >= 128:
            o = neutral(h, seed=6)
            dr = h - DOOR_TOP - 1
            o.rect(0, dr - 2, 128, dr + 5, (60, 62, 66))
            o.rect(0, dr, 128, dr + 3, WHITE)
            out[f"textures/AJZO{c}.png"] = o.png()
            out[f"brightmaps/ajzo{c.lower()}.png"] = bright(128, h, rows=((high_row(h), 3), (dr, 3))).png()
            comp.brightmap("texture", f"AJZO{c}", f"brightmaps/ajzo{c.lower()}.png")
    for c, h in HEIGHTS.items():                                 # plain plate: the pens, the cage
        comp.define("WallTexture", f"AJZR{c}", 128, h, [(f"AJZB{c}", 0, 0)])
    out["textures/AJZHAZ.png"] = hazard(64, 64).png()
    out["textures/AJZQ.png"] = slab_side().png()
    out["brightmaps/ajzq.png"] = bright(128, 320, rows=((2, 4),)).png()
    comp.brightmap("texture", "AJZQ", "brightmaps/ajzq.png")
    out["textures/AJZSTP.png"] = step_side().png()
    out["flats/AJZPLT.png"] = platen().png()
    out["textures/AJZSKY.png"] = starfield().png()
    out["sprites/AJZTA0.png"] = dash_sprite().png(grab=(32, 5))
    # the bed: 2048 by 512 (the chamber and the mouth, 1536 by 512, from its north-west corner), panned
    # into place by works32.py: a hazard border 32 wide, the load cells round the two plates
    out["patches/AJZBT.png"] = bed_tile().png()
    out["patches/AJZHV.png"] = hazard(32, 64).png()
    out["patches/AJZHH.png"] = hazard(64, 32).png()
    sq = Canvas(100, 100)
    sq.frame(0, 0, 100, 100, ORANGE, 4)
    for k in range(4):
        sq.rect(10 + 22 * k, 0, 14 + 22 * k, 10, ORANGE)
    out["patches/AJZLQ.png"] = sq.png()
    bed = [("AJZBT", x, y) for x in range(0, 2048, 128) for y in range(0, 512, 128)]
    bed += [("AJZHV", 0, y) for y in range(0, 512, 64)] + [("AJZHV", 1504, y) for y in range(0, 512, 64)]
    bed += [("AJZHH", x, 0) for x in range(0, 1536, 64)] + [("AJZHH", x, 480) for x in range(0, 1536, 64)]
    for letter, (px, py) in (("A", (768, 64)), ("B", (96, 96))):
        lab = Canvas(6 * 2 * 11, 12)
        text(lab, f"LOAD CELL {letter}", 0, 1, ORANGE, 2)
        out[f"patches/AJZL{letter}.png"] = lab.png()
        bed += [("AJZLQ", px - 50, py - 50), (f"AJZL{letter}", px - lab.w // 2, py + 56)]
    comp.define("Flat", "AJZBED", 2048, 512, bed)
    # the hatch round the way out: a full ICE border (lower 96, upper 32, sides of 224)
    for nm, h, rows in (("AJZHA", 96, ((0, 6),)), ("AJZHB", 32, ((26, 6),))):
        im = plate(h, seed=50 + h, grooves=False)
        for y0, n in rows:
            im.rect(0, y0, 128, y0 + n, ICE)
            im.rect(0, y0 + 2, 128, y0 + n - 2, mix(ICE, (255, 255, 255), 0.7))
        out[f"textures/{nm}.png"] = im.png()
        out[f"brightmaps/{nm.lower()}.png"] = bright(128, h, rows=rows).png()
        comp.brightmap("texture", nm, f"brightmaps/{nm.lower()}.png")
    for nm, x0 in (("AJZHC", STRIP - 6), ("AJZHD", 0)):          # C: the hatch on its right; D: on its left
        h = 224
        im = plate(h, seed=55, w=STRIP)
        im.rect(x0, 32 - 6, x0 + 6, 128 + 6, ICE)
        im.rect(x0 + 2, 32 - 4, x0 + 4, 128 + 4, mix(ICE, (255, 255, 255), 0.7))
        hr, fr = high_row(h), foot_row(h)
        im.rect(0, hr, STRIP, hr + 3, ICE)
        out[f"textures/{nm}.png"] = im.png()
        out[f"brightmaps/{nm.lower()}.png"] = bright(STRIP, h, rows=((hr, 3),), rects=((x0, 26, x0 + 6, 134),)).png()
        comp.brightmap("texture", nm, f"brightmaps/{nm.lower()}.png")
    # signs: on an opening's upper (a picture) or on a wall piece (a family)
    for sg in signs:
        if sg["kind"] == "upper":
            w, h = sg["w"], sg["h"]
            im = Canvas(w, h, (16, 20, 26, 255))
            im.noise(3, 60)
            p = sign_plate(sg["lines"], w - 24, sg.get("scale", 2))
            im.paste(p, 12, (h - p.h) // 2)
            out[f"textures/{sg['name']}.png"] = im.png()
            out[f"brightmaps/{sg['name'].lower()}.png"] = bright(w, h, mask=[((12, (h - p.h) // 2), p)]).png()
            comp.brightmap("texture", sg["name"], f"brightmaps/{sg['name'].lower()}.png")
        else:
            h, c = sg["h"], CODE[sg["h"]]
            p = sign_plate(sg["lines"], 112, sg.get("scale", 2))
            pn = f"AJZS{sg['name'][3]}"
            out[f"patches/{pn}.png"] = p.png()
            y = sg["y"]
            hr, fr = high_row(h), foot_row(h)
            bm = f"brightmaps/{sg['name'].lower()}.png"
            out[bm] = bright(128, h, rows=((hr, 3), (fr, 4)), mask=[((8, y), p)]).png()
            family(out, comp, sg["name"], 128, h, [(f"AJZB{c}", 0, 0)], [(0, hr, 128)], conduit_at=(0, fr, 128),
                   extra=[(pn, 8, y)], brightmap=bm)
    return {"textures": "\n\n".join(comp.tex) + "\n",
            "animdefs": "\n".join(comp.anim) + "\n",
            "gldefs": "\n\n".join(comp.glow) + "\n"}
