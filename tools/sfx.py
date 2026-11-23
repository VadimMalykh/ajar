"""Door sounds on trial in the sound lab (map SOUND: MAP=SOUND ./run.sh), third round.

A door taken is a piece of space coming loose; a door set, a piece of space
locking in. Two families, side by side in the lab:

A. Doom's own sounds, played by their logical names (the game always runs
   on the player's doom2.wad, so nothing is copied into the package), each
   at a pitch of its own (A_StartSound's pitch: 2 an octave up, 0.5 an
   octave down). DOOM below.

B. Recordings turned into shapes no door makes: reversed, re-pitched,
   layered, reverberated. The sources are Kenney Vleugels' "RPG sounds" and
   "Sci-fi sounds" (both CC0: assets/sounds/kenney-rpg/, kenney-scifi/, each
   with its license.txt), OGG files decoded with the system's libsndfile
   through ctypes (standard library only; the ajar-tools image has
   libsndfile1). OWN below: one line each, its recipe a small function of
   the helpers further down. A take's energy rises and stops dead; a set has
   a short lead-in, then a heavy hit with a short tail.
   Every B sound is then finished the same way: DC and rumble under 30 Hz
   off, a gentle low-pass at 6 kHz (Doom's own are 11025 Hz, nothing above
   5.5 kHz), its loudest 100 ms brought to LOUD (Doom's door sounds measure
   -12.5 dBFS so) with a soft limiter holding the peak under CEIL, 3 ms
   fades at both ends.

Written mono, 22050 Hz, 16-bit (44100 Hz sources are low-passed and halved).

The game's own door sounds, chosen by Vadim by ear in the lab on 2026-11-23
(GAME below): the take is B's "field drops", the set Doom's lift stopping at
pitch 0.7. Every level plays them (AjarHandler in src/zscript/ajar.zs, whose
TAKE_SOUND ... SET_PITCH must say the same). The rest stay candidates, to
compare again in the lab, Doom's old door first among them.

make_all() gives build.py:
    sounds/ajtake.wav                          the game's take (ajar/take)
    sounds/ajtake1.wav ... sounds/ajsetN.wav   family B's candidates, in table order
    sndinfo.txt     ajar/take -> ajtake, ajar/take1..n -> ajtake1..n, ajar/set1..n -> ajset1..n
    ajsounds.txt    one line a sound, kind|logical name|its name|pitch: first
                    the game's two (kind gametake, gameset), then the
                    candidates (take, set), family A then B, read by the lab
                    (src/zscript/soundlab.zs)

    python3 tools/sfx.py DIR [IWAD]     writes the WAVs, sndinfo.txt and
                                        ajsounds.txt to DIR and prints each
                                        one's length, peak, loudness, where
                                        its loudest 100 ms lies and its
                                        envelope; with IWAD the same for
                                        Doom's two door sounds.
"""
import ctypes
import ctypes.util
import io
import math
import os
import random
import struct
import sys
import wave
from fractions import Fraction

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds")
PACKS = {"rpg": "kenney-rpg", "scifi": "kenney-scifi"}
OUT = 22050                     # the rate written
LOUD = -13.0                    # dBFS, RMS of the loudest 100 ms
CEIL = -1.2                     # dBFS, the limiter's ceiling (the peak stays under it)
EDGE = 0.003                    # s, the fades at both ends

# --- the game's own: chosen by Vadim by ear in the lab, 2026-11-23 ------------------
# The same names and pitches as AjarHandler's TAKE_SOUND, TAKE_PITCH, SET_SOUND,
# SET_PITCH (src/zscript/ajar.zs); the lab checks that they agree. The take's
# recipe is take_field_drops below, written as sounds/ajtake.wav.
GAME = [
    # kind    its name in the lab                logical name      pitch
    ("take", "field drops",                     "ajar/take",       1.0),
    ("set",  "Doom's lift stops, pitch 0.7",    "plats/pt1_stop",  0.7),
]

# --- family A: Doom's own, by name and pitch ----------------------------------------
DOOM = [
    # kind    its name in the lab             logical name (GZDoom's Doom sndinfo)  pitch
    ("take", "Doom's door (the old one)",     "doors/dr1_clos",                      1.0),
    ("take", "Doom: weapon pick-up",          "misc/w_pkup",                         1.0),
    ("take", "Doom: fast door shuts",         "doors/dr2_clos",                      1.0),
    ("take", "Doom: lift starts, pitch 1.3",  "plats/pt1_strt",                      1.3),
    ("set",  "Doom's door (the old one)",     "doors/dr1_open",                      1.0),
    ("set",  "Doom: lift stops",              "plats/pt1_stop",                      1.0),
    ("set",  "Doom: fast door opens",         "doors/dr2_open",                      1.0),
]


# --- decoding: libsndfile through ctypes -------------------------------------------
class SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64), ("samplerate", ctypes.c_int), ("channels", ctypes.c_int),
                ("format", ctypes.c_int), ("sections", ctypes.c_int), ("seekable", ctypes.c_int)]


SFM_READ = 0x10
_lib = None


def libsndfile():
    global _lib
    if _lib is None:
        name = ctypes.util.find_library("sndfile") or "libsndfile.so.1"
        lib = ctypes.CDLL(name)
        lib.sf_open.restype = ctypes.c_void_p
        lib.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SF_INFO)]
        lib.sf_readf_float.restype = ctypes.c_int64
        lib.sf_readf_float.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int64]
        lib.sf_close.argtypes = [ctypes.c_void_p]
        lib.sf_strerror.restype = ctypes.c_char_p
        lib.sf_strerror.argtypes = [ctypes.c_void_p]
        _lib = lib
    return _lib


def decode(path):
    """(rate, mono samples as fractions of full scale): the channels averaged."""
    lib = libsndfile()
    info = SF_INFO()
    f = lib.sf_open(path.encode(), SFM_READ, ctypes.byref(info))
    if not f:
        raise SystemExit(f"sfx: cannot open {path}: {lib.sf_strerror(None).decode()}")
    try:
        ch = info.channels
        out = []
        buf = (ctypes.c_float * (4096 * ch))()
        while True:
            n = lib.sf_readf_float(f, buf, 4096)
            if n <= 0:
                break
            if ch == 1:
                out.extend(buf[:n])
            else:
                vals = buf[:n * ch]
                out.extend(sum(vals[i * ch:i * ch + ch]) / ch for i in range(n))
    finally:
        lib.sf_close(f)
    return info.samplerate, out


# --- to 22050 Hz --------------------------------------------------------------------
def resample(x, src, dst, half=64):
    """Windowed-sinc (Blackman) resampling, polyphase: the kernels for each
    phase of the rational ratio are made once. The cut-off is 0.9 of the lower
    Nyquist rate (about 10 kHz from 44100 to 22050)."""
    if src == dst:
        return list(x)
    r = Fraction(src, dst)
    p, q = r.numerator, r.denominator
    fc = 0.45 * min(src, dst) / src           # cycles per source sample
    kernels = []
    for ph in range(q):
        frac = ph / q
        h = []
        for k in range(-half + 1, half + 1):     # taps at i0 + k, i0 = floor(t)
            d = frac - k                         # t minus the tap's time
            u = (d + half) / (2 * half)          # 0..1 across the window
            w = 0.42 - 0.5 * math.cos(2 * math.pi * u) + 0.08 * math.cos(4 * math.pi * u) if 0 <= u <= 1 else 0.0
            s = 2 * fc if d == 0 else math.sin(2 * math.pi * fc * d) / (math.pi * d)
            h.append(s * w)
        g = sum(h)
        kernels.append([v / g for v in h])
    n = len(x)
    pad = [0.0] * half
    xp = pad + list(x) + pad
    out = []
    for i in range(int(n * dst / src)):
        i0, ph = divmod(i * p, q)
        h = kernels[ph]
        seg = xp[i0 + 1:i0 + 1 + 2 * half]         # the taps k = -half + 1 .. half (xp is padded by half)
        out.append(sum(a * b for a, b in zip(h, seg)))
    return out


# --- measures -----------------------------------------------------------------------
def db(v):
    return 20 * math.log10(v) if v > 0 else -999.0


def loudest(x, rate=OUT, window=0.1):
    """(RMS over the loudest `window` seconds, where it starts)."""
    w = max(1, min(len(x), int(rate * window)))
    sq = [v * v for v in x]
    acc = sum(sq[:w])
    best, at = acc, 0
    for i in range(w, len(sq)):
        acc += sq[i] - sq[i - w]
        if acc > best:
            best, at = acc, i - w + 1
    return math.sqrt(max(best, 0) / w), at


def peak(x):
    return max(abs(v) for v in x) or 1e-9


def trim(x, lead_db=-40, tail_db=-60):
    """Without the leading silence (below lead_db of the peak) and the trailing
    one (below tail_db)."""
    p = peak(x)
    a = next(i for i, v in enumerate(x) if abs(v) >= p * 10 ** (lead_db / 20))
    b = max(i for i, v in enumerate(x) if abs(v) >= p * 10 ** (tail_db / 20))
    return x[a:b + 1]


# --- the sources --------------------------------------------------------------------
_sources = {}


def src(pack, name):
    """A source at OUT Hz, trimmed of its silences, at its own level."""
    key = (pack, name)
    if key not in _sources:
        rate, x = decode(os.path.join(SOUNDS_DIR, PACKS[pack], name + ".ogg"))
        _sources[key] = trim(resample(x, rate, OUT))
    return list(_sources[key])


def rpg(name):
    return src("rpg", name)


def scifi(name):
    return src("scifi", name)


# --- the helpers: each takes a list of samples at OUT Hz and gives a new one ---------
def S(t):
    """Seconds to samples."""
    return int(round(t * OUT))


def semis(n):
    """The speed factor of n semitones (-12: half speed, an octave down)."""
    return 2 ** (n / 12)


def rev(x):
    return x[::-1]


def cut(x, a=0.0, b=None):
    """From a to b seconds (b None: to the end; negative: from the end)."""
    return x[S(a):None if b is None else S(b)]


def hit(x, pre=0.002, under=6.0):
    """From its first hit on: from `pre` seconds before the first sample within
    `under` dB of its peak (what comes before, the hand on the door, goes)."""
    p = peak(x) * 10 ** (-under / 20)
    i = next(i for i, v in enumerate(x) if abs(v) >= p)
    return x[max(0, i - S(pre)):]


def last(x, t):
    """The last t seconds."""
    return x[-S(t):]


def pad(x, before=0.0, after=0.0):
    return [0.0] * S(before) + x + [0.0] * S(after)


def gain(x, dbs):
    g = 10 ** (dbs / 20)
    return [v * g for v in x]


def norm(x, to=0.0):
    """Peak at `to` dBFS (layers are balanced by peak, then by gain)."""
    g = 10 ** (to / 20) / peak(x)
    return [v * g for v in x]


def speed(x, f):
    """Played f times as fast: pitch up and shorter for f > 1 (linear interpolation)."""
    n = int((len(x) - 1) / f)
    out = []
    for i in range(n):
        p = i * f
        k = int(p)
        t = p - k
        out.append(x[k] * (1 - t) + x[k + 1] * t)
    return out


def glide(x, f0, f1):
    """Played at a speed going from f0 to f1 across the source (a pitch that
    falls or rises), linear interpolation."""
    out, p, n = [], 0.0, len(x) - 1
    while p < n:
        k = int(p)
        t = p - k
        out.append(x[k] * (1 - t) + x[k + 1] * t)
        p += f0 + (f1 - f0) * p / n
    return out


def mix(*layers):
    """Layers (samples, at seconds[, dB]) summed into one."""
    parts = [(x, S(at), 10 ** ((rest[0] if rest else 0) / 20)) for x, at, *rest in layers]
    out = [0.0] * max(a + len(x) for x, a, _ in parts)
    for x, a, g in parts:
        for i, v in enumerate(x):
            out[a + i] += v * g
    return out


def then(a, b, overlap=0.0):
    """b starting `overlap` seconds before a ends."""
    return mix((a, 0), (b, max(0.0, len(a) / OUT - overlap)))


def fade_in(x, t, curve=1.0):
    """A fade from silence over t seconds (curve > 1: slower at first)."""
    n = min(len(x), max(1, S(t)))
    return [v * ((i / n) ** curve if i < n else 1.0) for i, v in enumerate(x)]


def fade_out(x, t, curve=1.0):
    return rev(fade_in(rev(x), t, curve))


def decay(x, t60, after=0.0):
    """An exponential fade from `after` seconds on, 60 dB down in t60 seconds."""
    a = S(after)
    k = math.log(1000) / (t60 * OUT)
    return [v if i < a else v * math.exp(-k * (i - a)) for i, v in enumerate(x)]


def steady(x, t=0.02):
    """Its own rise and fall taken out: divided by its RMS envelope (blocks of t
    seconds, joined linearly), so that a shape put on after is the only one."""
    b = max(1, S(t))
    env = []
    for i in range(0, len(x), b):
        part = x[i:i + b]
        env.append(math.sqrt(sum(v * v for v in part) / len(part)))
    floor = max(env) * 0.01
    out = []
    for i, v in enumerate(x):
        p = i / b - 0.5
        k = min(max(int(p), 0), len(env) - 1)
        k1 = min(k + 1, len(env) - 1)
        t = min(max(p - k, 0.0), 1.0)
        out.append(v / max(env[k] * (1 - t) + env[k1] * t, floor))
    return out


def swell(x, curve=2.0):
    """Shaped to rise across its whole length: from silence to full at its end."""
    return fade_in(x, len(x) / OUT, curve)


def lowpass(x, hz):
    """One pole, 6 dB an octave."""
    a = 1 - math.exp(-2 * math.pi * hz / OUT)
    y, out = 0.0, []
    for v in x:
        y += a * (v - y)
        out.append(y)
    return out


def highpass(x, hz):
    return [v - l for v, l in zip(x, lowpass(x, hz))]


def reverb(x, t60=0.4, wet=0.3, size=1.0):
    """A short Schroeder reverb: four combs in parallel, two all-passes in
    series; the tail (t60 seconds) is added to the length. `size` scales the
    delays (a smaller room for < 1)."""
    n = len(x) + S(t60)
    dry = x + [0.0] * (n - len(x))
    acc = [0.0] * n
    for ms in (29.7, 37.1, 41.1, 43.7):
        d = max(1, int(ms * size * OUT / 1000))
        g = 10 ** (-3 * d / OUT / t60)
        y = [0.0] * n
        for i in range(n):
            y[i] = dry[i] + (g * y[i - d] if i >= d else 0.0)
            acc[i] += y[i] / 4
    for ms, g in ((5.0, 0.7), (1.7, 0.7)):
        d = max(1, int(ms * size * OUT / 1000))
        y = [0.0] * n
        for i in range(n):
            y[i] = -g * acc[i] + (acc[i - d] + g * y[i - d] if i >= d else 0.0)
        acc = y
    return [a + wet * b for a, b in zip(dry, acc)]


def click(ms=3.0, at_db=0.0):
    """A tiny click: one cycle of a 1.5 kHz sine under a short decay."""
    n = max(2, S(ms / 1000))
    return [10 ** (at_db / 20) * math.sin(2 * math.pi * 1500 * i / OUT) * math.exp(-4 * i / n) for i in range(n)]


def limit(x, ceil_db=CEIL, knee_db=6.0):
    """A soft limiter: linear up to knee_db under the ceiling, a tanh curve
    above it that never reaches the ceiling."""
    c = 10 ** (ceil_db / 20)
    k = c * 10 ** (-knee_db / 20)
    r = c - k

    def one(v):
        a = abs(v)
        if a <= k:
            return v
        return math.copysign(k + r * math.tanh((a - k) / r), v)
    return [one(v) for v in x]


def finish(x):
    """The same for every B sound: DC and rumble under 30 Hz off, a gentle
    low-pass at 6 kHz, the loudest 100 ms at LOUD dBFS through the limiter
    (the gain before it found by a few steps), 3 ms fades at both ends."""
    m = sum(x) / len(x)
    x = lowpass(highpass([v - m for v in x], 30), 6000)
    target = 10 ** (LOUD / 20)
    g = target / (loudest(x)[0] or 1e-9)
    for _ in range(40):
        y = limit([v * g for v in x])
        e = LOUD - db(loudest(y)[0])
        if abs(e) < 0.05:
            break
        g *= 10 ** (e / 20)
    m = sum(y) / len(y)
    y = [v - m for v in y]
    return fade_out(fade_in(y, EDGE), EDGE)


# --- family B: the recipes ------------------------------------------------------------
# Takes: a piece of space comes loose; the energy rises and then stops dead, 0.35-0.7 s.
def take_unslam():
    """A door shut played backwards: its ring swells into the slam, and stops on it."""
    return rev(cut(hit(rpg("doorClose_4")), 0, 0.5))


def take_unslam_low():
    """The same an octave lower, the reverb put on before reversing, so that its
    tail comes first as a rising pre-swell; a tiny click at the very end."""
    x = rev(reverb(cut(speed(hit(rpg("doorClose_4")), 0.5), 0, 0.4), t60=0.5, wet=0.5))
    x = fade_in(last(x, 0.62), 0.05)
    return mix((x, 0), (click(3, -6), len(x) / OUT - 0.004))


def take_peel():
    """A knife drawn, five semitones down, swelling, ending in a short pop (a thud
    pitched up) that stops it."""
    w = swell(cut(speed(rpg("drawKnife2"), semis(-5)), 0, 0.42), 1.5)
    pop = fade_out(cut(speed(hit(rpg("bookPlace1")), semis(9)), 0, 0.05), 0.015)
    return then(norm(w, -6), norm(pop), 0.02)


def take_field_drops():
    """A force field falling in pitch while it grows, cut short."""
    x = glide(scifi("forceField_000"), 1.5, 0.55)
    return swell(steady(cut(x, 0, 0.5)), 1.6)


# Sets: a piece of space locks in; a short lead-in, then a heavy hit with a short tail, 0.4-0.9 s.
def set_seal():
    """A whoosh backwards (0.2 s) straight into a door shut a fifth down, with a
    copy an octave under that, in a short reverb."""
    lead = swell(last(rev(rpg("cloth1")), 0.2), 1.2)
    shut = hit(rpg("doorClose_4"))
    slam = mix((cut(speed(shut, 2 / 3), 0, 0.42), 0), (cut(speed(shut, 1 / 3), 0, 0.42), 0, -3))
    return reverb(then(norm(lead, -4), norm(decay(slam, 0.45, 0.05))), t60=0.2, wet=0.25, size=0.6)


def set_slam_sub():
    """A slam with an octave-down copy and a low-passed sub under it; no lead-in,
    the shortest reverb."""
    x = cut(hit(rpg("doorClose_2")), 0, 0.45)
    low = speed(x, 0.5)
    sub = lowpass(lowpass(low, 120), 120)
    y = mix((norm(x), 0), (norm(low), 0, -4), (norm(sub), 0, -2))
    return reverb(decay(cut(y, 0, 0.6), 0.6, 0.08), t60=0.15, wet=0.2, size=0.5)


def set_field_clunk():
    """A force field rising in pitch (0.2 s) into a metal impact."""
    lead = swell(steady(cut(glide(scifi("forceField_000"), 0.6, 1.8), 0, 0.2)), 1.5)
    clunk = decay(cut(hit(scifi("impactMetal_003")), 0, 0.55), 0.5, 0.03)
    return then(norm(lead, -14), norm(clunk))


def set_thud_ring():
    """A low thud with a short metallic ring after it, the ring a metal pot an
    octave and a fifth down, fading over 0.5 s."""
    thud = norm(cut(speed(hit(rpg("bookPlace2")), semis(-7)), 0, 0.3))
    ring = decay(norm(cut(speed(cut(hit(rpg("metalPot1")), 0, 0.3), semis(-19)), 0, 0.65)), 0.7, 0.02)
    return mix((thud, 0), (ring, 0.01, -3))


OWN = [
    # kind    its name in the lab   the recipe
    ("take", "un-slam",           take_unslam),
    ("take", "un-slam, low",      take_unslam_low),
    ("take", "peel",              take_peel),
    ("set",  "seal",              set_seal),
    ("set",  "slam with sub",     set_slam_sub),
    ("set",  "field up, clunk",   set_field_clunk),
    ("set",  "thud and ring",     set_thud_ring),
]



# --- MAP20's water (water.zs): made here, from noise and the recordings above -------------------
def _noise(t, seed):
    r = random.Random(seed)
    return [r.uniform(-1, 1) for _ in range(S(t))]


def _loud(x):
    """finish() without its fades: the gain to LOUD through the limiter (a loop's ends must meet)."""
    m = sum(x) / len(x)
    x = lowpass(highpass([v - m for v in x], 30), 6000)
    target = 10 ** (LOUD / 20)
    g = target / (loudest(x)[0] or 1e-9)
    for _ in range(40):
        y = limit([v * g for v in x])
        e = LOUD - db(loudest(y)[0])
        if abs(e) < 0.05:
            break
        g *= 10 ** (e / 20)
    return y


def _loop(x, t=0.25):
    """The last `t` s laid over the first, fading across, so that the sound loops without a seam."""
    n = S(t)
    body, tail = x[:-n], x[-n:]
    for i in range(n):
        f = i / n
        body[i] = body[i] * f + tail[i] * (1 - f)
    return body


def _bubbles(t, seed, rate=9.0, lo=500, hi=1400):
    """Little rising sine chirps at random, as air comes up through water."""
    r = random.Random(seed)
    out = [0.0] * S(t)
    k = 0.0
    while True:
        k += r.expovariate(rate)
        if k > t - 0.08:
            break
        f0, d = r.uniform(lo, hi), r.uniform(0.02, 0.06)
        a, ph = r.uniform(0.2, 0.6), 0.0
        for i in range(S(d)):
            f = f0 * (1 + 0.8 * i / S(d))
            ph += 2 * math.pi * f / OUT
            j = S(k) + i
            if j < len(out):
                out[j] += a * math.sin(ph) * math.sin(math.pi * i / S(d))
    return out


def water_running():
    """Water through a door: a rushing noise, low-passed, over a few bubbles; a 2 s loop."""
    rush = lowpass(lowpass(highpass(_noise(2.25, 20), 120), 1400), 2200)
    return mix((norm(rush), 0), (norm(_bubbles(2.25, 21)), 0, -10))


def water_splash():
    """Going in or out: a burst of noise falling away, a cloth whoosh under it, bubbles after."""
    burst = decay(lowpass(highpass(_noise(0.7, 22), 300), 3000), 0.35, 0.02)
    whoosh = cut(speed(rpg("cloth1"), semis(-3)), 0, 0.4)
    return mix((norm(fade_in(burst, 0.01)), 0), (norm(whoosh), 0, -6), (norm(_bubbles(0.5, 23, 20)), 0.15, -12))


def wheel_turning():
    """A paddle wheel: a slow knock (a book set down, an octave down) twice a turn, a pot's ring a
    long way down after each, water noise under it; a 1.6 s loop."""
    t = 1.85
    knock = cut(speed(hit(rpg("bookPlace2")), 0.5), 0, 0.3)
    ring = decay(cut(speed(cut(hit(rpg("metalPot1")), 0, 0.3), semis(-24)), 0, 0.5), 0.5, 0.02)
    water = lowpass(highpass(_noise(t, 24), 100), 900)
    return mix((norm(water), 0, -8), (norm(knock), 0.05), (norm(ring), 0.08, -9),
               (norm(knock), 0.85, -2), (norm(ring), 0.88, -10))


WATER = [
    # logical name   lump       the recipe          a loop?
    ("ajar/water",   "ajwater",  water_running,      True),
    ("ajar/splash",  "ajsplash", water_splash,       False),
    ("ajar/wheel",   "ajwheel",  wheel_turning,      True),
]


def wav(x):
    samples = [max(-32768, min(32767, int(round(v * 32767)))) for v in x]
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUT)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return b.getvalue()


def first_line(f):
    return " ".join(f.__doc__.split())


_made = None


def make_all():
    """{pk3 path: bytes or text} for build.py."""
    global _made
    if _made is None:
        out, snd, listing, count = {}, [], [], {"take": 0, "set": 0}
        snd.append("// Made by tools/sfx.py from recordings (assets/sounds/kenney-rpg, kenney-scifi; CC0): the game's\n"
                   "// take (ajar/take, every level plays it) and the sound lab's candidates (soundlab.zs).\n")
        out["sounds/ajtake.wav"] = wav(finish(take_field_drops()))
        snd.append(f"ajar/take\tajtake\t\t// the game's take, {GAME[0][1]}: {first_line(take_field_drops)}")
        game = [f"game{kind}|{logical}|{name}|{pitch:g}" for kind, name, logical, pitch in GAME]
        for kind, name, logical, pitch in DOOM:
            listing.append(f"{kind}|{logical}|{name}|{pitch:g}")
        own = {"take": [], "set": []}
        for kind, name, recipe in OWN:
            count[kind] += 1
            lump = f"aj{kind}{count[kind]}"
            out[f"sounds/{lump}.wav"] = wav(finish(recipe()))
            snd.append(f"ajar/{kind}{count[kind]}\t{lump}\t\t// {name}: {first_line(recipe)}")
            own[kind].append(f"{kind}|ajar/{kind}{count[kind]}|{name}|1")
        for logical, lump, recipe, loop in WATER:
            out[f"sounds/{lump}.wav"] = wav(_loop(_loud(recipe())) if loop else finish(recipe()))
            snd.append(f"{logical}\t{lump}\t\t// MAP20: {first_line(recipe)}")
        listing = game + [l for l in listing if l.startswith("take")] + own["take"] + [l for l in listing if l.startswith("set")] + own["set"]
        out["sndinfo.txt"] = "\n".join(snd) + "\n"
        out["ajsounds.txt"] = "\n".join(listing) + "\n"
        _made = out
    return _made


# --- figures --------------------------------------------------------------------
def figures(samples, rate):
    """Length (s), peak (dBFS), RMS over the loudest 100 ms (dBFS), where the
    middle of that 100 ms lies (% of the length), and the envelope: the RMS of
    each tenth of the sound, dB under the loudest tenth."""
    rms, at = loudest(samples, rate)
    n = len(samples)
    w = int(rate * 0.1)
    tenths = []
    for k in range(10):
        part = samples[k * n // 10:(k + 1) * n // 10] or [0.0]
        tenths.append(math.sqrt(sum(v * v for v in part) / len(part)))
    top = max(tenths) or 1e-9
    env = " ".join(f"{max(-99, round(db(t / top))):3d}" for t in tenths)
    return n / rate, db(peak(samples)), db(rms), 100 * (at + min(w, n) / 2) / n, env


def wav_figures(data):
    with wave.open(io.BytesIO(data)) as w:
        n = w.getnframes()
        s = struct.unpack(f"<{n}h", w.readframes(n))
        return figures([v / 32768 for v in s], w.getframerate())


def doom_sound(wad, name):
    """A Doom sound lump: (rate, samples as fractions), 8-bit unsigned after an 8-byte header."""
    with open(wad, "rb") as f:
        data = f.read()
    n, off = struct.unpack("<4xII", data[:12])
    for i in range(n):
        pos, size, nm = struct.unpack("<II8s", data[off + 16 * i:off + 16 * i + 16])
        if nm.rstrip(b"\0").decode() == name:
            lump = data[pos:pos + size]
            fmt, rate, count = struct.unpack("<HHI", lump[:8])
            body = lump[8:8 + count]
            body = body[16:-16] if len(body) > 32 else body       # (DMX pads 16 bytes at each end)
            return rate, [(b - 128) / 128 for b in body]
    raise KeyError(name)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    print(f"{'sound':10} {'length s':>9} {'peak dBFS':>10} {'RMS 100ms':>10} {'at %':>5}  envelope by tenths (dB)          name")
    made = make_all()
    names = iter([GAME[0][1] + " (the game's)"] + [name for kind, name, recipe in OWN])
    for path, data in made.items():
        with open(os.path.join(out, os.path.basename(path)), "wb" if isinstance(data, bytes) else "w") as f:
            f.write(data)
        if path.endswith(".wav"):
            name = next(names)
            ln, pk, rms, at, env = wav_figures(data)
            print(f"{os.path.basename(path)[:-4]:10} {ln:9.3f} {pk:10.2f} {rms:10.2f} {at:5.0f}  {env}  {name}")
    if len(sys.argv) > 2:
        for name in ("DSDORCLS", "DSDOROPN", "DSWPNUP", "DSBDCLS", "DSBDOPN", "DSPSTART", "DSPSTOP"):
            rate, s = doom_sound(sys.argv[2], name)
            ln, pk, rms, at, env = figures(s, rate)
            print(f"{name:10} {ln:9.3f} {pk:10.2f} {rms:10.2f} {at:5.0f}  {env}  ({rate} Hz, 8-bit)")
