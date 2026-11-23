"""Ajar's own door sounds, synthesised (the sound lab, map SOUND: MAP=SOUND ./run.sh).

Six sounds, three of each action: taking a door off its hinges (ajtake1..3)
and hanging one (ajset1..3). src/sndinfo.txt names them ajar/take1..3 and
ajar/set1..3. Standard library only, every random number from a fixed seed:
the same bytes on every build.

Synthesised at 44100 Hz, low-passed and taken down to 11025 Hz, 16-bit mono
(Doom's own rate, so they sit beside its shotgun). Each is brought to a peak
of -3 dBFS; its loudness (RMS over its loudest 100 ms) is meant to be within
about 3 dB of Doom's door sounds DSDORCLS and DSDOROPN.

    python3 tools/sfx.py DIR [IWAD]     writes the WAVs to DIR and prints each
                                        one's length, peak and loudness, and
                                        with IWAD the same for Doom's two.

The building blocks (after Farnell, "Designing Sound"):
  knock   a few ms of noise that rings 4-7 damped, inharmonic modes of a door
          panel; "hollow" leans on the upper modes, "thud" adds a low body
          whose pitch sinks a little, and longer decays
  clack   the same with small metal modes, 1.8-4.5 kHz: a hinge pin, a latch
  squeak  stick-slip: a sawtooth whose pitch glides and wobbles, through two
          resonances of the hinge plate (about 1.2 and 2.6 kHz)
  creak   an irregular train of impulses that speeds up from about 20 to 80 a
          second, each one ringing the wood (125, 250, 395, 560, 790 Hz)
  scrape  band-passed noise (1-3 kHz) under a rising envelope
"""
import io
import math
import random
import struct
import sys
import wave

SR = 44100          # synthesis rate
OUT = 11025         # the rate written
PEAK = 10 ** (-3 / 20)      # -3 dBFS


def n_of(t):
    return int(round(t * SR))


# --- filters -------------------------------------------------------------------
def biquad(x, b0, b1, b2, a1, a2):
    y = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, o
        y[i] = o
    return y


def bandpass(x, f, q):
    """RBJ band-pass, 0 dB at the centre."""
    w = 2 * math.pi * f / SR
    al = math.sin(w) / (2 * q)
    a0 = 1 + al
    return biquad(x, al / a0, 0.0, -al / a0, -2 * math.cos(w) / a0, (1 - al) / a0)


def lowpass(x, f, q=0.7071):
    w = 2 * math.pi * f / SR
    al = math.sin(w) / (2 * q)
    c = math.cos(w)
    a0 = 1 + al
    return biquad(x, (1 - c) / 2 / a0, (1 - c) / a0, (1 - c) / 2 / a0, -2 * c / a0, (1 - al) / a0)


def highpass(x, f, q=0.7071):
    w = 2 * math.pi * f / SR
    al = math.sin(w) / (2 * q)
    c = math.cos(w)
    a0 = 1 + al
    return biquad(x, (1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0, -2 * c / a0, (1 - al) / a0)


def resonator(x, f, tau):
    """One damped mode at f Hz whose ringing falls by 1/e in tau seconds;
    a unit impulse rings it at amplitude 1."""
    w = 2 * math.pi * f / SR
    r = math.exp(-1 / (tau * SR))
    return biquad(x, math.sin(w), 0.0, 0.0, -2 * r * math.cos(w), r * r)


def norm(x, to=1.0):
    p = max(abs(v) for v in x) or 1.0
    return [v * to / p for v in x]


def mix(total, *parts):
    """parts: (signal, start in seconds, gain)."""
    out = [0.0] * n_of(total)
    for sig, at, g in parts:
        i0 = n_of(at)
        for i, v in enumerate(sig):
            j = i0 + i
            if j >= len(out):
                break
            out[j] += g * v
    return out


# --- building blocks -----------------------------------------------------------
def burst(rnd, ms, length):
    """A noise burst of `ms` under a half-sine, in a signal `length` seconds long."""
    n = max(2, n_of(ms / 1000))
    x = [0.0] * n_of(length)
    for i in range(n):
        x[i] = rnd.uniform(-1, 1) * math.sin(math.pi * (i + 0.5) / n)
    return x


def modes(exc, freqs, amps, taus):
    out = [0.0] * len(exc)
    for f, a, tau in zip(freqs, amps, taus):
        for i, v in enumerate(norm(resonator(exc, f, tau), a)):
            out[i] += v
    return out


PANEL = (1, 1.58, 2.24, 2.92, 3.6, 4.31, 5.07)       # a door panel's inharmonic modes


def knock(seed, f0, amps, taus, *, ms=3, length=0.25, mallet=2500):
    """Wood: a burst through the panel's modes (len(amps) of them, 4-7)."""
    rnd = random.Random(seed)
    exc = lowpass(burst(rnd, ms, length), mallet)
    freqs = [f0 * r * rnd.uniform(0.98, 1.02) for r in PANEL[:len(amps)]]
    body = modes(exc, freqs, amps, taus)
    click = norm(highpass(burst(rnd, 0.6, length), 1500), 0.25)
    return norm([b + c for b, c in zip(body, click)])


def thud(seed, *, f0=95, glide=(82, 62), length=0.4, tau=0.11, weight=1.0):
    """A heavy knock: the panel's lower modes, slower, and a sinking body."""
    k = knock(seed, f0, (1.0, 0.85, 0.6, 0.45, 0.3, 0.2), (0.12, 0.10, 0.08, 0.06, 0.05, 0.04),
              ms=5, length=length, mallet=1400)
    n = n_of(length)
    body = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = glide[1] + (glide[0] - glide[1]) * math.exp(-t / 0.06)
        ph += 2 * math.pi * f / SR
        att = min(1.0, t / 0.004)
        body[i] = math.sin(ph) * math.exp(-t / tau) * att
    return norm([a + weight * b for a, b in zip(k, body)])


def hollow(seed, f0=150, *, length=0.2, taus=(0.03, 0.045, 0.06, 0.07, 0.06, 0.05)):
    """A light knock that leans on the upper modes."""
    return knock(seed, f0, (0.35, 0.55, 1.0, 0.9, 0.75, 0.55), taus, ms=2.5, length=length, mallet=3500)


METAL = (1850, 2430, 3170, 3890, 4420)


def clack(seed, *, scale=1.0, taus=(0.035, 0.03, 0.025, 0.02, 0.015), bounce=None, length=0.15):
    """A hinge pin or a latch; `bounce` (seconds) adds a quieter second click."""
    rnd = random.Random(seed)
    exc = burst(rnd, 0.5, length)
    if bounce:
        j = n_of(bounce)
        for i in range(n_of(0.0004)):
            exc[j + i] += 0.35 * rnd.uniform(-1, 1)
    freqs = [f * scale * rnd.uniform(0.97, 1.03) for f in METAL]
    m = modes(exc, freqs, (1.0, 0.8, 0.9, 0.6, 0.45), taus)
    return norm([a + 0.3 * b for a, b in zip(m, highpass(exc, 2000))])


def squeak(seed, *, length=0.18, f=(420, 760), attack=0.6):
    """Stick-slip of a dry hinge: pitch from f[0] to f[1], slow attack."""
    rnd = random.Random(seed)
    n = n_of(length)
    saw = [0.0] * n
    ph, wob, wv = 0.0, 0.0, 0.0
    for i in range(n):
        u = i / n
        wv += rnd.gauss(0, 0.0009)              # a small random walk in the pitch
        wv *= 0.995
        wob = max(-0.04, min(0.04, wob + wv))
        fr = (f[0] + (f[1] - f[0]) * u ** 0.8) * (1 + wob)
        ph += fr / SR
        if ph >= 1:
            ph -= 1
        saw[i] = 2 * ph - 1                     # sticks (slow rise), slips (drop)
    a = bandpass(saw, 1200, 5)
    b = bandpass(saw, 2600, 7)
    s = [0.9 * x + 0.7 * y + 0.12 * z for x, y, z in zip(a, b, lowpass(saw, 900))]
    out = [0.0] * n
    rel = n_of(0.02)
    for i in range(n):
        t = i / n
        env = math.sin(min(1.0, t / attack) * math.pi / 2) ** 2
        if i > n - rel:
            env *= (n - i) / rel
        out[i] = s[i] * env * (0.85 + 0.15 * math.sin(2 * math.pi * 31 * i / SR + rnd.random()))
    return norm(out)


WOOD = ((125, 1.0, 0.03), (250, 0.8, 0.025), (395, 0.7, 0.02), (560, 0.55, 0.016), (790, 0.4, 0.012))


def creak(seed, *, length=0.25, rate=(20, 80)):
    """Farnell's creaking door: impulses that come faster and faster, each
    ringing the wood."""
    rnd = random.Random(seed)
    n = n_of(length + 0.05)
    exc = [0.0] * n
    t = 0.004
    while t < length:
        u = t / length
        i = n_of(t)
        a = rnd.uniform(0.6, 1.0) * (0.5 + 0.5 * u)
        for k in range(n_of(0.0003)):
            exc[i + k] += a * (1 if k < 7 else -0.5)
        r = rate[0] + (rate[1] - rate[0]) * u ** 1.2
        t += rnd.uniform(0.75, 1.25) / r
    body = modes(exc, [f * rnd.uniform(0.97, 1.03) for f, _, _ in WOOD], [a for _, a, _ in WOOD],
                 [tau for _, _, tau in WOOD])
    grit = highpass(exc, 2000)
    return norm([b + 0.15 * g for b, g in zip(body, grit)])


def scrape(seed, *, length=0.08):
    """Pins sliding into their hinges."""
    rnd = random.Random(seed)
    n = n_of(length)
    x = [rnd.uniform(-1, 1) for _ in range(n)]
    y = bandpass(bandpass(x, 1800, 1.1), 2000, 1.4)
    g = lowpass([rnd.uniform(0, 1) for _ in range(n)], 120)     # grain
    rel = n_of(0.006)
    out = []
    for i in range(n):
        env = (i / n) ** 1.6
        if i > n - rel:
            env *= (n - i) / rel
        out.append(y[i] * env * (0.4 + 3 * g[i]))
    return norm(out)


# --- the six -------------------------------------------------------------------
def take_a():
    """Squeak and knock: a squeak rising in pitch, then a light hollow knock."""
    return mix(0.40, (squeak(11, length=0.18, f=(420, 780)), 0.0, 0.55), (hollow(12, 160), 0.175, 1.0))


def take_b():
    """Creak and pins: a low creak, accelerating, two light pin clicks and a soft tap."""
    return mix(0.44, (creak(21, length=0.25), 0.0, 0.75),
               (clack(22, scale=1.15), 0.255, 0.55), (clack(23, scale=1.2), 0.29, 0.45),
               (hollow(24, 175, taus=(0.025, 0.035, 0.045, 0.05, 0.04, 0.03)), 0.31, 0.55))


def take_c():
    """Pins only: two metal clicks close together and a hollow wood knock."""
    return mix(0.21, (clack(31, scale=1.1), 0.0, 0.9), (clack(32, scale=1.18), 0.035, 0.85),
               (hollow(33, 150, taus=(0.05, 0.065, 0.075, 0.075, 0.065, 0.055)), 0.06, 1.0))


def set_a():
    """Thud and clack: a heavy wood thud, a latch clack 40 ms after it."""
    return mix(0.45, (thud(41), 0.0, 1.0), (clack(42, scale=0.9, bounce=0.03), 0.04, 0.6))


def set_b():
    """Slide and thud: a short scrape, then thud and clack."""
    return mix(0.52, (scrape(51, length=0.085), 0.0, 0.5), (thud(52, f0=90, glide=(80, 60)), 0.08, 1.0),
               (clack(53, scale=0.92), 0.12, 0.55))


def set_c():
    """Two pins: clack, clack 70 ms apart, then a deep settling thud."""
    return mix(0.53, (clack(61, scale=0.85, bounce=0.025), 0.0, 0.7), (clack(62, scale=0.88), 0.07, 0.7),
               (thud(63, f0=80, glide=(72, 52), tau=0.14, length=0.38, weight=1.3), 0.13, 1.0))


SOUNDS = {"ajtake1": take_a, "ajtake2": take_b, "ajtake3": take_c,
          "ajset1": set_a, "ajset2": set_b, "ajset3": set_c}
# A gentle saturation (tanh) on the sharpest ones, so that with the peak at
# -3 dBFS their loudness still comes near Doom's door sounds.
DRIVE = {"ajtake1": 1.5, "ajtake3": 1.5}


# --- to 11025 Hz and 16 bits -----------------------------------------------------
def decimate(x, factor=SR // OUT, cutoff=4700, taps=127):
    """Windowed-sinc low-pass, evaluated at every factor-th sample."""
    h = []
    m = taps // 2
    for k in range(taps):
        j = k - m
        s = 2 * cutoff / SR * (1 if j == 0 else math.sin(2 * math.pi * cutoff / SR * j) / (2 * math.pi * cutoff / SR * j))
        h.append(s * (0.42 - 0.5 * math.cos(2 * math.pi * k / (taps - 1)) + 0.08 * math.cos(4 * math.pi * k / (taps - 1))))
    g = sum(h)
    h = [v / g for v in h]
    out = []
    for i in range(0, len(x), factor):
        acc = 0.0
        for k, c in enumerate(h):
            j = i + k - m
            if 0 <= j < len(x):
                acc += c * x[j]
        out.append(acc)
    return out


def finish(x, drive=0):
    """At 11025 Hz: no DC, a short fade at the end, the peak at -3 dBFS."""
    if drive:
        x = [math.tanh(drive * v) / math.tanh(drive) for v in norm(x)]
    y = decimate(highpass(x, 40))
    fade = OUT // 100
    for i in range(fade):
        y[-1 - i] *= i / fade
    return [int(round(v)) for v in norm(y, PEAK * 32767)]


def wav(samples):
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUT)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return b.getvalue()


_made = None


def make_all():
    """{pk3 path: WAV bytes} for build.py."""
    global _made
    if _made is None:
        _made = {f"sounds/{name}.wav": wav(finish(f(), DRIVE.get(name, 0))) for name, f in SOUNDS.items()}
    return _made


# --- figures -------------------------------------------------------------------
def figures(samples, rate, full=1.0):
    """Length (s), peak (dBFS), RMS over the loudest 100 ms (dBFS); samples as
    fractions of full scale."""
    w = max(1, int(rate * 0.1))
    best = 0.0
    sq = [v * v for v in samples]
    acc = sum(sq[:w])
    best = acc
    for i in range(w, len(sq)):
        acc += sq[i] - sq[i - w]
        best = max(best, acc)
    rms = math.sqrt(best / min(w, len(sq)))
    peak = max(abs(v) for v in samples)
    db = lambda v: 20 * math.log10(v / full) if v > 0 else -999
    return len(samples) / rate, db(peak), db(rms)


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
    import os
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    print(f"{'sound':10} {'length s':>9} {'peak dBFS':>10} {'RMS 100ms dBFS':>15}")
    for path, data in make_all().items():
        with open(os.path.join(out, os.path.basename(path)), "wb") as f:
            f.write(data)
        ln, pk, rms = wav_figures(data)
        print(f"{os.path.basename(path)[:-4]:10} {ln:9.3f} {pk:10.2f} {rms:15.2f}")
    if len(sys.argv) > 2:
        for name in ("DSDORCLS", "DSDOROPN"):
            rate, s = doom_sound(sys.argv[2], name)
            ln, pk, rms = figures(s, rate)
            print(f"{name:10} {ln:9.3f} {pk:10.2f} {rms:15.2f}   ({rate} Hz, 8-bit)")
