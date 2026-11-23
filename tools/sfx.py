"""Ajar's own door sounds, cut from recordings (the sound lab, map SOUND: MAP=SOUND ./run.sh).

The sources are Kenney Vleugels' "RPG sounds" (CC0, assets/sounds/kenney-rpg/,
license.txt there): OGG files, decoded with the system's libsndfile through
ctypes (standard library only; the ajar-tools image has libsndfile1).

SOUNDS below is the list of candidates, one line each: whether it is a take
(a door coming off its hinges) or a set (a door hung), its name, and its
layers. The first layer is a source as it is; each further layer is placed
by a rule and set some dB under the first, both measured by loudness (the
RMS of the loudest 100 ms). A candidate is then cut: leading silence (below
-40 dB of its peak) off, trailing silence (below -60 dB) off, at most
TAKE_MAX / SET_MAX seconds with a 60 ms fade-out when that cuts it, and its
peak brought to -3 dBFS. Nothing is saturated or compressed: a recording
whose loudness stays under Doom's door sounds at that peak stays quieter.

Written mono, 22050 Hz, 16-bit (44100 Hz sources are low-passed and halved).

make_all() gives build.py:
    sounds/ajtake1.wav ... sounds/ajsetN.wav   the candidates, in table order
    sndinfo.txt     ajar/take1..n -> ajtake1..n, ajar/set1..n -> ajset1..n
    ajsounds.txt    one line a candidate, kind|logical name|its name, read by
                    the lab (src/zscript/soundlab.zs)
Every level still plays Doom's door sounds; only the lab chooses these.

    python3 tools/sfx.py DIR [IWAD]     writes the WAVs, sndinfo.txt and
                                        ajsounds.txt to DIR and prints each
                                        one's length, peak and loudness, and
                                        with IWAD the same for Doom's two.
"""
import ctypes
import ctypes.util
import io
import math
import os
import struct
import sys
import wave
from fractions import Fraction

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds", "kenney-rpg")
OUT = 22050                     # the rate written
PEAK = 10 ** (-3 / 20)          # -3 dBFS
TAKE_MAX, SET_MAX = 0.8, 0.9    # seconds
FADE = 0.06                     # the fade-out when a sound is cut short
CREAKS = ("creak1", "creak2", "creak3")     # a layer naming several sources takes the shortest

# A layer: (source, when, dB[, "peak"]). `when`: 0 (with the first layer);
# "dies" (as the layer before it dies away, its 10 ms envelope 24 dB under its
# peak for good); "peak+S" (S seconds after the first layer's loudest point).
# dB: against the first layer's loudness, or with "peak" its peak (for a click
# laid on a door: by loudness a 20 ms click 3 dB under would peak 5 dB over the
# door, and the whole would come out 5 dB quieter).
SOUNDS = [
    # kind    its name               layers
    ("take", "door opens 1",       [("doorOpen_1",)]),
    ("take", "door opens 2",       [("doorOpen_2",)]),
    ("take", "latch",              [("metalLatch",)]),
    ("take", "latch, then creak",  [("metalLatch",), (CREAKS, "dies", -4)]),
    ("take", "click",              [("metalClick",)]),
    ("set",  "door shuts 1",       [("doorClose_1",)]),
    ("set",  "door shuts 2",       [("doorClose_2",)]),
    ("set",  "door shuts 3",       [("doorClose_3",)]),
    ("set",  "door shuts 4",       [("doorClose_4",)]),
    ("set",  "shut and latch",     [("doorClose_1",), ("metalLatch", "peak+0.08", -3, "peak")]),
]
LIMIT = {"take": TAKE_MAX, "set": SET_MAX}


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


# --- measures and cuts --------------------------------------------------------------
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


def peak_at(x):
    return max(range(len(x)), key=lambda i: abs(x[i]))


def trim(x, lead_db=-40, tail_db=-60):
    """Without the leading silence (below lead_db of the peak) and the trailing
    one (below tail_db)."""
    p = max(abs(v) for v in x) or 1.0
    a = next(i for i, v in enumerate(x) if abs(v) >= p * 10 ** (lead_db / 20))
    b = max(i for i, v in enumerate(x) if abs(v) >= p * 10 ** (tail_db / 20))
    return x[a:b + 1]


def dies(x, rate=OUT, under=24):
    """Where x dies away: from here on its 10 ms envelope stays `under` dB
    under its peak."""
    w = int(rate * 0.01)
    env = [max(abs(v) for v in x[i:i + w]) for i in range(0, len(x), w)]
    top = max(env)
    last = max(i for i, e in enumerate(env) if e >= top * 10 ** (-under / 20))
    return min(len(x), (last + 1) * w)


_sources = {}


def source(name):
    """A source at OUT Hz, trimmed of its silences."""
    if name not in _sources:
        rate, x = decode(os.path.join(SRC, name + ".ogg"))
        _sources[name] = trim(resample(x, rate, OUT))
    return _sources[name]


def build(layers):
    """The candidate's layers mixed, before the final cut."""
    first = source(layers[0][0])
    loud0, _ = loudest(first)
    peak0 = max(abs(v) for v in first)
    parts = [(first, 0)]
    for name, when, gain, *by in layers[1:]:
        names = name if isinstance(name, tuple) else (name,)
        x = min((source(n) for n in names), key=len)
        if when == "dies":
            prev, at = parts[-1]
            at += dies(prev)
        elif isinstance(when, str) and when.startswith("peak+"):
            at = peak_at(first) + int(round(float(when[5:]) * OUT))
        else:
            at = int(round(when * OUT))
        if by == ["peak"]:
            g = peak0 / max(abs(v) for v in x) * 10 ** (gain / 20)
        else:
            g = loud0 / (loudest(x)[0] or 1) * 10 ** (gain / 20)
        parts.append(([v * g for v in x], at))
    out = [0.0] * max(at + len(x) for x, at in parts)
    for x, at in parts:
        for i, v in enumerate(x):
            out[at + i] += v
    return out


def finish(x, limit):
    """Trimmed, cut to `limit` seconds with a fade-out if longer, peak at -3 dBFS:
    16-bit integers."""
    x = trim(x)
    n = int(limit * OUT)
    if len(x) > n:
        x = x[:n]
        f = int(FADE * OUT)
        for i in range(f):
            x[n - f + i] *= 0.5 + 0.5 * math.cos(math.pi * (i + 1) / f)
    p = max(abs(v) for v in x)
    return [int(round(v * PEAK * 32767 / p)) for v in x]


def wav(samples):
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUT)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return b.getvalue()


def recipe(layers):
    """A layer list in words, for the table and the sndinfo comments."""
    out = []
    for i, (name, *rest) in enumerate(layers):
        name = "shortest of " + "/".join(name) if isinstance(name, tuple) else name
        if rest:
            when, gain, *by = rest
            w = "as it dies away" if when == "dies" else (f"{when[5:]} s after the peak" if isinstance(when, str) else f"at {when} s")
            name += f" {w}, {gain:+g} dB" + (" by peak" if by else " by loudness")
        out.append(name)
    return " + ".join(out)


_made = None


def make_all():
    """{pk3 path: bytes or text} for build.py."""
    global _made
    if _made is None:
        out, snd, listing, count = {}, [], [], {"take": 0, "set": 0}
        snd.append("// Made by tools/sfx.py from recordings (assets/sounds/kenney-rpg, CC0): the sound lab's\n"
                   "// door sounds. Every level still plays Doom's; the lab (soundlab.zs) chooses these.\n")
        for kind, name, layers in SOUNDS:
            count[kind] += 1
            lump = f"aj{kind}{count[kind]}"
            out[f"sounds/{lump}.wav"] = wav(finish(build(layers), LIMIT[kind]))
            snd.append(f"ajar/{kind}{count[kind]}\t{lump}\t\t// {name}: {recipe(layers)}")
            listing.append(f"{kind}|ajar/{kind}{count[kind]}|{name}")
        out["sndinfo.txt"] = "\n".join(snd) + "\n"
        out["ajsounds.txt"] = "\n".join(listing) + "\n"
        _made = out
    return _made


# --- figures --------------------------------------------------------------------
def figures(samples, rate):
    """Length (s), peak (dBFS), RMS over the loudest 100 ms (dBFS); samples as
    fractions of full scale."""
    rms, _ = loudest(samples, rate)
    return len(samples) / rate, db(max(abs(v) for v in samples)), db(rms)


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
    print(f"{'sound':10} {'length s':>9} {'peak dBFS':>10} {'RMS 100ms dBFS':>15}  recipe")
    made = make_all()
    names = iter(SOUNDS)
    for path, data in made.items():
        with open(os.path.join(out, os.path.basename(path)), "wb" if isinstance(data, bytes) else "w") as f:
            f.write(data)
        if path.endswith(".wav"):
            kind, name, layers = next(names)
            ln, pk, rms = wav_figures(data)
            print(f"{os.path.basename(path)[:-4]:10} {ln:9.3f} {pk:10.2f} {rms:15.2f}  {name}: {recipe(layers)}")
    if len(sys.argv) > 2:
        for name in ("DSDORCLS", "DSDOROPN"):
            rate, s = doom_sound(sys.argv[2], name)
            ln, pk, rms = figures(s, rate)
            print(f"{name:10} {ln:9.3f} {pk:10.2f} {rms:15.2f}   ({rate} Hz, 8-bit)")
