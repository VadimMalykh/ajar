"""MAP32's look: the pictures (Vadim, 2026-11-21, "Deep Field"; its lights
redone 2026-11-22, Vadim: "on walls only, something more still like orange
glow, not white on black"; AJAR_WORKS in map_secret2.py, the dressing in
works32.py, what answers the game in src/zscript/works.zs).

A plant hung in space where time doors are tested: dark plated steel, orange
for hazard and marking, and one kind of light: a still orange wall lamp, a
short bar in a dark housing with a soft glow painted round it on the plate.
Nothing here moves (no ANIMDEFS); the stars drift (MAPINFO).

Every name is AJZ... Heights of wall (the last letter of a wall's name):
A 96, B 128, C 160, D 192, E 224, F 256, G 288, H 320. A wall is hung from
the ceiling (the chamber's from its floor: the press's ceiling moves).
  AJZB<h>   patch: the plate, 128 wide, rows of 64 from the top, rivets, the
            skirting
  AJZW<h>   a wall (TEXTURES: AJZB<h>); also the pens' and the cage's
  AJZWL<h>  a wall with a lamp (a picture, B..H): the lamp centred 128 wide,
            its middle LAMP_Y(h) over the floor; a brightmap: the bar
            white, the glow grey in proportion
  AJZU<h>   the wall over a time door and the 32 beside it each side (a
            picture, B..H): the same lamp, its middle DOOR_Y(h) over the
            floor, centred on the door's mouth (64 wide; works32.py sets the
            offsets)
  AJZXD     the wall over a time door in the chamber (96 high, hung from the
            door): rows 0..95 of AJZUD
  AJZPD     the chamber's wall (TEXTURES: AJZBD and a load scale, AJZSC);
            AJZPDL the same with a lamp (a picture)
  AJZ1..9   a wall with a sign on it (SIGNS, from works32.py; TEXTURES)
  AJZTH     the steel lintel over the chamber's mouth, 1280 wide (TEST BAY 3,
            LOAD 4000 t between hazard stripes; TEXTURES)
Pictures: AJZN<h> a frame's surround (pale neutral steel, 64 each side and
over the frame), AJZQ a slab's or pillar's side (an orange line along its
top), AJZSTP a step, AJZHAZ hazard stripes, AJZSKY the stars,
AJZHA/AJZHB/AJZHC/AJZHD the hatch round the way out (an orange lit border),
AJZI1 a sign over an opening. Flats: AJZFT tread plate, AJZKP the ceiling's
steel plate, AJZPLT the press's face (ribbed), AJZBED the bed under it (a
composite: hazard border, the load cells). Sprite AJZT: a dash of white
light, laid flat (the plate line, works.zs).
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

ORANGE = (255, 138, 48)
CORE = (255, 214, 150)          # the middle of a lamp's bar: pale warm
HEIGHTS = {"A": 96, "B": 128, "C": 160, "D": 192, "E": 224, "F": 256, "G": 288, "H": 320}
CODE = {h: c for c, h in HEIGHTS.items()}
LAMPED = [c for c, h in HEIGHTS.items() if h > 96]     # the heights a lamp is drawn for
STRIP = 32              # a strip beside the hatch; and beside a time door, the door lamp's glow
LAMP_W, LAMP_H = 44, 7  # the lamp's bar
GLOW_SX = 30.0          # the glow: a gaussian, its sigma across,
GLOW_UP, GLOW_DOWN = 26.0, 32.0     # above the lamp and below it
GLOW_WHOLE, GLOW_GONE = 34, 62      # across: whole within GLOW_WHOLE of the middle, nothing from GLOW_GONE
GLOW_LIFT = 1.1         # the steel under the glow brightened by this share (warm) at its heart
GLOW_ADD = 0.7          # and ORANGE added by this share
WARM = (1.0, 0.55, 0.1)


def LAMP_Y(h):
    """A wall lamp's middle over the floor: 128 on walls 192 and higher, lower
    on shorter ones so that the lamp and most of its glow fit."""
    return min(128, h - 60)


def DOOR_Y(h):
    """A door lamp's middle over the floor (the door is 96 high): 128 where the
    wall allows, else half way between the door's top and the ceiling."""
    return min(128, (96 + h) // 2)


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

    def crop(self, y0, y1):
        im = Canvas(self.w, y1 - y0)
        im.b[:] = self.b[y0 * self.w * 4:y1 * self.w * 4]
        return im

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


def plate(h, *, top=TOP, bot=BOT, seam=SEAM, hi=SEAM_HI, rivet=RIVET, seed=1, w=128, skirting=True):
    """A wall of plates 128 wide, h high, hung from the ceiling: rows of 64
    from the top, rivets at the corners, the skirting at the foot."""
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
    if skirting:
        im.rect(0, h - 4, w, h, (12, 15, 20))
    return im


# --- the lamp -------------------------------------------------------------------
def glow_at(dx, dy):
    """The glow's strength (0..1) at (dx, dy) from the lamp's middle (dy down)."""
    ax = abs(dx)
    if ax >= GLOW_GONE:
        return 0.0
    sy = GLOW_DOWN if dy > 0 else GLOW_UP
    g = math.exp(-0.5 * ((dx / GLOW_SX) ** 2 + (dy / sy) ** 2))
    if ax > GLOW_WHOLE:
        t = (ax - GLOW_WHOLE) / (GLOW_GONE - GLOW_WHOLE)
        g *= 1 - t * t * (3 - 2 * t)
    return g


def lamp(im, cy, seed, cx=64):
    """Paints a lamp, its bar's middle at (cx, cy), and its glow onto im;
    returns the brightmap (the bar white, the glow grey in proportion)."""
    rnd = random.Random(seed)
    bm = Canvas(im.w, im.h, (0, 0, 0, 255))
    b, m = im.b, bm.b
    for y in range(im.h):
        for x in range(im.w):
            g = glow_at(x + 0.5 - cx, y + 0.5 - cy)
            if g <= 0.0:
                continue
            i = (y * im.w + x) * 4
            for k in range(3):
                v = b[i + k] * (1 + GLOW_LIFT * g * WARM[k]) + ORANGE[k] * GLOW_ADD * g
                b[i + k] = min(255, int(v + rnd.random()))         # dithered: no steps
            v = min(255, int(255 * g + rnd.random()))
            m[i:i + 3] = bytes((v, v, v))
    hw = LAMP_W // 2
    x0, y0 = cx - hw, cy - LAMP_H // 2
    im.rect(x0 - 2, y0 - 2, x0 + LAMP_W + 2, y0 + LAMP_H + 2, (10, 10, 12))      # the housing
    im.rect(x0 - 2, y0 - 2, x0 + LAMP_W + 2, y0 - 1, (70, 60, 52))
    bm.rect(x0 - 2, y0 - 2, x0 + LAMP_W + 2, y0 + LAMP_H + 2, (0, 0, 0))
    for y in range(y0, y0 + LAMP_H):
        for x in range(x0, x0 + LAMP_W):
            ex = abs(x + 0.5 - cx) / hw
            ey = abs(y + 0.5 - (y0 + LAMP_H / 2)) / (LAMP_H / 2)
            im.set(x, y, mix(CORE, ORANGE, min(1.0, max(ex ** 3, ey ** 2))))
            bm.set(x, y, (255, 255, 255))
    return bm


def lamp_wall(h, y_over_floor, seed, base=None):
    """A plate h high with a lamp, its middle y_over_floor over the floor: (picture, brightmap)."""
    im = base or plate(h, seed=40 + h)
    return im, lamp(im, h - y_over_floor, seed)


# --- composites ---------------------------------------------------------------
class Comp:
    """The TEXTURES lump and the GLDEFS brightmaps."""

    def __init__(self):
        self.tex, self.glow = [], []

    def define(self, kind, name, w, h, patches):
        lines = [f'{kind} "{name}", {w}, {h}', "{"]
        for nm, x, y in patches:
            lines.append(f'\tPatch "{nm}", {x}, {y}')
        lines.append("}")
        self.tex.append("\n".join(lines))

    def brightmap(self, kind, name, path):
        self.glow.append(f'brightmap {kind} "{name}"\n{{\n\tmap "{path}"\n}}')


def bright(w, h, mask=(), rows=()):
    """A brightmap: white where it is lit whatever the room's light."""
    im = Canvas(w, h, (0, 0, 0, 255))
    for y0, n in rows:
        im.rect(0, y0, w, y0 + n, (255, 255, 255))
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
    return plate(128, top=(26, 33, 44), bot=(22, 28, 38), skirting=False, seed=9)


def neutral(h, seed=4):
    """A frame's surround: pale neutral steel (a picture)."""
    return plate(h, top=(150, 154, 158), bot=(128, 132, 136), seam=(92, 96, 100), hi=(176, 180, 184),
                 rivet=(196, 198, 202), seed=seed, skirting=False)


def slab_side():
    im = plate(320, top=(30, 38, 50), bot=(20, 26, 35), skirting=False, seed=13)
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


def lit_border(im, x1, y1, x2, y2):
    """The hatch's border: ORANGE with a pale warm core."""
    im.rect(x1, y1, x2, y2, ORANGE)
    if x2 - x1 > y2 - y1:
        im.rect(x1, y1 + 2, x2, y2 - 2, CORE)
    else:
        im.rect(x1 + 2, y1, x2 - 2, y2, CORE)


# --- all of it ----------------------------------------------------------------
def make(out, signs=()):
    """Writes the pictures and returns the text of TEXTURES and GLDEFS, as a dict."""
    comp = Comp()
    for c, h in HEIGHTS.items():
        out[f"patches/AJZB{c}.png"] = plate(h, seed=40 + h).png()
        comp.define("WallTexture", f"AJZW{c}", 128, h, [(f"AJZB{c}", 0, 0)])
    # the lamps: on a wall (AJZWL), over a time door (AJZU)
    for c in LAMPED:
        h = HEIGHTS[c]
        for nm, y in ((f"AJZWL{c}", LAMP_Y(h)), (f"AJZU{c}", DOOR_Y(h))):
            im, bm = lamp_wall(h, y, seed=70 + h)
            out[f"textures/{nm}.png"] = im.png()
            out[f"brightmaps/{nm.lower()}.png"] = bm.png()
            comp.brightmap("texture", nm, f"brightmaps/{nm.lower()}.png")
            if nm == "AJZUD":
                # the chamber's door: the wall over it, 96 high, hung from the door (rows 0..95 of the 192)
                out["textures/AJZXD.png"] = im.crop(0, 96).png()
                out["brightmaps/ajzxd.png"] = bm.crop(0, 96).png()
                comp.brightmap("texture", "AJZXD", "brightmaps/ajzxd.png")
    # the chamber: a load scale on every plate; with a lamp
    sc = scale_strip(192)
    out["patches/AJZSC.png"] = sc.png()
    comp.define("WallTexture", "AJZPD", 128, 192, [("AJZBD", 0, 0), ("AJZSC", 6, 0)])
    pd = plate(192, seed=40 + 192)
    pd.paste(sc, 6, 0)
    im, bm = lamp_wall(192, LAMP_Y(192), seed=80, base=pd)
    out["textures/AJZPDL.png"] = im.png()
    out["brightmaps/ajzpdl.png"] = bm.png()
    comp.brightmap("texture", "AJZPDL", "brightmaps/ajzpdl.png")
    # the lintel over the chamber's mouth: 1280 wide, 320 high, the hall's wall over it: TEST BAY 3 and
    # LOAD 4000 t between hazard stripes; below the lintel's 128, the press's face
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
    base = [("AJZBH", x, 0) for x in range(0, 1280, 128)]
    base += [("AJZPF", x, 128) for x in range(0, 1280, 128)]
    base += [("AJZHZ", x, 96) for x in range(0, 1280, 64)]
    s1x, s2x = 640 - 40 - s1.w, 640 + 40
    base += [("AJZG3", s1x, 94), ("AJZG4", s2x, 94)]
    comp.define("WallTexture", "AJZTH", 1280, 320, base)
    out["brightmaps/ajzth.png"] = bright(1280, 320, mask=[((s1x, 94), s1), ((s2x, 94), s2)]).png()
    comp.brightmap("texture", "AJZTH", "brightmaps/ajzth.png")
    # the floor: tread plate; the ceiling: steel plate
    tr = tread()
    out["flats/AJZFT.png"] = tr.png()
    out["patches/AJZFT.png"] = tr.png()
    out["flats/AJZKP.png"] = ceiling_plate().png()
    # pictures
    for c, h in HEIGHTS.items():
        out[f"textures/AJZN{c}.png"] = neutral(h).png()
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
    # the hatch round the way out: an orange border lit all round (lower 96, upper 32, sides of 224)
    for nm, h, rows in (("AJZHA", 96, ((0, 6),)), ("AJZHB", 32, ((26, 6),))):
        im = plate(h, seed=50 + h, skirting=False)
        for y0, n in rows:
            lit_border(im, 0, y0, 128, y0 + n)
        out[f"textures/{nm}.png"] = im.png()
        out[f"brightmaps/{nm.lower()}.png"] = bright(128, h, rows=rows).png()
        comp.brightmap("texture", nm, f"brightmaps/{nm.lower()}.png")
    for nm, x0 in (("AJZHC", STRIP - 6), ("AJZHD", 0)):          # C: the hatch on its right; D: on its left
        h = 224
        im = plate(h, seed=55, w=STRIP)
        lit_border(im, x0, 32 - 6, x0 + 6, 128 + 6)
        out[f"textures/{nm}.png"] = im.png()
        bm = bright(STRIP, h)
        bm.rect(x0, 26, x0 + 6, 134, (255, 255, 255))
        out[f"brightmaps/{nm.lower()}.png"] = bm.png()
        comp.brightmap("texture", nm, f"brightmaps/{nm.lower()}.png")
    # signs: on an opening's upper (a picture) or on a wall piece (a composite)
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
            comp.define("WallTexture", sg["name"], 128, h, [(f"AJZB{c}", 0, 0), (pn, 8, y)])
            bm = f"brightmaps/{sg['name'].lower()}.png"
            out[bm] = bright(128, h, mask=[((8, y), p)]).png()
            comp.brightmap("texture", sg["name"], bm)
    return {"textures": "\n\n".join(comp.tex) + "\n",
            "gldefs": "\n\n".join(comp.glow) + "\n"}
